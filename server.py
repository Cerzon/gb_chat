import errno
import selectors
import socket
from typing import Any, Dict, List

import click
import structlog

from gb_chat.io.deserializer import Deserializer
from gb_chat.io.message_framer import MessageFramer
from gb_chat.io.message_sender import MessageSender
from gb_chat.io.message_splitter import MessageSplitter
from gb_chat.io.parsed_msg_handler import ParsedMessageHandler
from gb_chat.io.send_buffer import SendBuffer
from gb_chat.io.serializer import Serializer
from gb_chat.log import (bind_client_name_to_logger,
                         bind_remote_address_to_logger, configure_logging,
                         get_logger)
from gb_chat.server.client import Client
from gb_chat.server.disconnector import Disconnector
from gb_chat.server.message_router import MessageRouter
from gb_chat.server.server import Server

_logger: Any = get_logger()


class NothingToRead(Exception):
    pass


class UnableToWrite(Exception):
    pass


class StopProcessing(Exception):
    pass


class ClientConnection:
    def __init__(
        self,
        sock: socket.socket,
        send_buffer: SendBuffer,
        msg_splitter: MessageSplitter,
        client: Client,
    ) -> None:
        self._sock = sock
        self._send_buffer = send_buffer
        self._msg_splitter = msg_splitter
        self._client = client

    def read(self) -> None:
        try:
            while True:
                data = self._sock.recv(1024)
                if not data:
                    raise NothingToRead()
                if not self._client.disconnector.should_disconnect:
                    self._msg_splitter.feed(data)
        except socket.error as e:
            err = e.args[0]
            if err in (errno.EAGAIN, errno.EWOULDBLOCK):
                return

            raise NothingToRead() from e

    def write(self) -> None:
        if not self._send_buffer.data:
            return

        size = self._sock.send(self._send_buffer.data)
        if size == 0:
            raise UnableToWrite()

        self._send_buffer.bytes_sent(size)

    @property
    def client(self) -> Client:
        return self._client

    @property
    def have_outgoing_data(self) -> bool:
        return bool(self._send_buffer.data)

    @property
    def socket(self) -> socket.socket:
        return self._sock


class SocketHandler:
    def __init__(self, sel: selectors.BaseSelector, server: Server) -> None:
        self._sel = sel
        self._server = server
        self._clients: Dict[socket.socket, ClientConnection] = {}

    def accept_new_connection(self, server_sock: socket.socket) -> None:
        sock, _ = server_sock.accept()
        with bind_remote_address_to_logger(sock):
            sock.setblocking(False)

            disconnector = Disconnector()
            send_buffer = SendBuffer()
            msg_framer = MessageFramer(send_buffer)
            serializer = Serializer(msg_framer)
            msg_sender = MessageSender(serializer)
            client = Client(msg_sender, disconnector)
            msg_router = MessageRouter(self._server, client)
            parsed_msg_handler = ParsedMessageHandler(msg_router)
            deserializer = Deserializer(parsed_msg_handler)
            msg_splitter = MessageSplitter(deserializer)

            self._clients[sock] = ClientConnection(
                sock, send_buffer, msg_splitter, client
            )
            self._server.on_client_connected(client)

            self._sel.register(
                sock, selectors.EVENT_READ | selectors.EVENT_WRITE, self._process_sock_event  # type: ignore
            )
            _logger.debug("New client connected")

    def run(self) -> None:
        while True:
            self._process_io_events()
            self._disconnect_requested_clients()

    def _process_io_events(self) -> None:
        events: List[Any] = []
        try:
            events = self._sel.select()

            for key, mask in events:
                callback = key.data
                callback(key.fileobj, mask)
        except KeyboardInterrupt:
            self._disconnect_all_clients()
            raise StopProcessing()
        except:
            self._disconnect_all_clients()
            raise

    def _disconnect_all_clients(self) -> None:
        clients_to_disconnect: List[ClientConnection] = []
        for _, client_connection in self._clients.items():
            clients_to_disconnect.append(client_connection)
        self._disconnect_clients(*clients_to_disconnect)

    def _disconnect_requested_clients(self) -> None:
        clients_to_disconnect: List[ClientConnection] = []
        for _, client_connection in self._clients.items():
            if (
                client_connection.client.disconnector.should_disconnect
                and not client_connection.have_outgoing_data
            ):
                clients_to_disconnect.append(client_connection)
        self._disconnect_clients(*clients_to_disconnect)

    def _disconnect_clients(self, *client_connections: ClientConnection) -> None:
        for client_connection in client_connections:
            sock = client_connection.socket
            with bind_remote_address_to_logger(sock):
                with bind_client_name_to_logger(client_connection.client.name):
                    _logger.debug("Client disconnected")
                    self._sel.unregister(sock)
                    sock.close()
                    self._server.on_client_disconnected(self._clients[sock].client)
                    del self._clients[sock]

    def _process_sock_event(self, sock: socket.socket, mask: int) -> None:
        with bind_remote_address_to_logger(sock):
            connection = self._clients[sock]
            with bind_client_name_to_logger(connection.client.name):
                try:
                    if mask & selectors.EVENT_READ:
                        connection.read()
                    if mask & selectors.EVENT_WRITE:
                        connection.write()
                except (UnableToWrite, NothingToRead):
                    self._disconnect_clients(connection)


@click.command()
@click.option("-a", "--address", type=str, default="localhost")
@click.option("-p", "--port", type=click.IntRange(1, 65535), default=7777)
def main(address: str, port: int) -> None:
    configure_logging(structlog.dev.ConsoleRenderer(colors=False))
    logger = _logger.bind(address=address, port=port)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.setblocking(False)
        server_sock.bind((address, port))
        server_sock.listen()

        with selectors.DefaultSelector() as sel:
            server = Server()
            handler = SocketHandler(sel, server)

            sel.register(
                server_sock,
                selectors.EVENT_READ,
                lambda sock, _: handler.accept_new_connection(sock),  # type: ignore
            )

            try:
                logger.info("Start server")
                handler.run()
            except StopProcessing:
                logger.info("Stop server")
            except:
                logger.exception("Stop server due to error")


if __name__ == "__main__":
    main()
