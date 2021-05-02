import errno
import logging
import select
import socket
import threading
from typing import Any

import click
import structlog

from gb_chat.client.client import Client
from gb_chat.client.message_router import MessageRouter
from gb_chat.common.disconnector import Disconnector
from gb_chat.common.exceptions import NothingToRead, UnableToWrite
from gb_chat.common.room_name_validator import RoomNameValidator
from gb_chat.common.thread_executor import IoThreadExecutor
from gb_chat.io.deserializer import Deserializer
from gb_chat.io.message_framer import MessageFramer
from gb_chat.io.message_sender import MessageSender
from gb_chat.io.message_splitter import MessageSplitter
from gb_chat.io.parsed_msg_handler import ParsedMessageHandler
from gb_chat.io.send_buffer import SendBuffer
from gb_chat.io.serializer import Serializer
from gb_chat.io.settings import EVENTS_WAIT_TIMEOUT
from gb_chat.log import configure_logging, get_logger

_logger: Any = get_logger()


def read_data(sock: socket.socket, msg_splitter: MessageSplitter) -> None:
    try:
        while True:
            data = sock.recv(1024)
            if not data:
                raise NothingToRead()
            msg_splitter.feed(data)
    except socket.error as e:
        err = e.args[0]
        if err in (errno.EAGAIN, errno.EWOULDBLOCK):
            return

        raise NothingToRead() from e


def write_data(sock: socket.socket, send_buffer: SendBuffer) -> None:
    if not send_buffer.data:
        return

    size = sock.send(send_buffer.data)
    if size == 0:
        raise UnableToWrite()

    send_buffer.bytes_sent(size)


def mainloop(
    sock: socket.socket,
    send_buffer: SendBuffer,
    msg_splitter: MessageSplitter,
    disconnector: Disconnector,
    io_thread_executor: IoThreadExecutor,
    event: threading.Event,
) -> None:
    while not event.is_set() and not disconnector.should_disconnect:
        r, w, _ = select.select([sock], [sock], [], EVENTS_WAIT_TIMEOUT)
        if r:
            read_data(sock, msg_splitter)
        if w:
            write_data(sock, send_buffer)

        io_thread_executor.execute_all()

    while send_buffer.data:
        _, w, _ = select.select([], [sock], [], 0)
        if w:
            write_data(sock, send_buffer)


def io_thread(
    sock: socket.socket,
    send_buffer: SendBuffer,
    msg_splitter: MessageSplitter,
    disconnector: Disconnector,
    logger: Any,
    io_thread_executor: IoThreadExecutor,
    event: threading.Event,
) -> None:
    try:
        mainloop(
            sock, send_buffer, msg_splitter, disconnector, io_thread_executor, event
        )
    except (KeyboardInterrupt, NothingToRead, UnableToWrite):
        pass
    except Exception:
        logger.exception("Disconnected")
        return

    logger.info("Disconnected")


@click.command()
@click.option("-a", "--address", type=str, default="localhost", show_default=True)
@click.option(
    "-p", "--port", type=click.IntRange(1, 65535), default=7777, show_default=True
)
@click.argument("username", type=str, required=True)
@click.argument("password", type=str, required=True)
@click.option("-v", "--verbose", is_flag=True, default=False, show_default=True)
def main(address: str, port: int, username: str, password: str, verbose: bool) -> None:
    log_level = logging.DEBUG if verbose else logging.ERROR
    configure_logging(structlog.dev.ConsoleRenderer(colors=False), log_level)
    logger = _logger.bind(address=address, port=port)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.connect((address, port))
        except ConnectionRefusedError:
            logger.error("Server unavailable")
            return

        logger.info("Connected to server")
        sock.setblocking(False)

        send_buffer = SendBuffer()
        msg_framer = MessageFramer(send_buffer)
        serializer = Serializer(msg_framer)
        msg_sender = MessageSender(serializer)
        disconnector = Disconnector()
        client = Client(msg_sender, RoomNameValidator(), disconnector)
        msg_router = MessageRouter(client)
        parsed_msg_handler = ParsedMessageHandler(msg_router)
        deserializer = Deserializer(parsed_msg_handler)
        msg_splitter = MessageSplitter(deserializer)

        io_thread_executor = IoThreadExecutor()
        event = threading.Event()
        thread = threading.Thread(
            name="io",
            target=lambda: io_thread(
                sock,
                send_buffer,
                msg_splitter,
                disconnector,
                logger,
                io_thread_executor,
                event,
            ),
        )
        try:
            thread.start()
            io_thread_executor.schedule(lambda: client.login(username, password))

            while not disconnector.should_disconnect:
                print(
                    "Enter command:\n"
                    "m - send message\n"
                    "j - join room\n"
                    "l - leave room\n"
                    "q - exit\n"
                )
                cmd = input("CMD: ")
                if not cmd:
                    continue
                elif cmd.startswith("m"):
                    to = input("To: ")
                    msg = input("Message: ")
                    io_thread_executor.schedule(lambda: client.send_msg(to, msg))
                elif cmd.startswith("j"):
                    room = input("Room: ")
                    io_thread_executor.schedule(lambda: client.join_room(room))
                elif cmd.startswith("l"):
                    room = input("Room: ")
                    io_thread_executor.schedule(lambda: client.leave_room(room))
                else:
                    io_thread_executor.schedule(lambda: client.quit())
                    break
        except KeyboardInterrupt:
            pass
        finally:
            event.set()
            thread.join()


if __name__ == "__main__":
    main()
