from http import HTTPStatus
from typing import Any, Dict, List

from ..log import get_logger
from ..msg.client_to_server import (Authenticate, Chat, Join, Leave, Presence,
                                    Quit)
from ..msg.server_to_client import Response
from .client import Client

_logger: Any = get_logger()


class Server:
    def __init__(self) -> None:
        self._clients: List[Client] = []
        self._auth_clients: Dict[str, Client] = {}

    def on_client_connected(self, client: Client) -> None:
        _logger.info("Client connected")
        self._clients.append(client)

    def on_client_disconnected(self, client: Client) -> None:
        _logger.info("Client disconnected")
        self._clients.remove(client)
        for name, auth_client in self._auth_clients.items():
            if auth_client is not client:
                continue

            del self._auth_clients[name]
            return

    def on_auth(self, msg: Authenticate, from_client: Client) -> None:
        from_client.name = msg.login
        self._auth_clients[msg.login] = from_client
        from_client.msg_sender.send(Response(HTTPStatus.OK, "Login successful"))

    def on_quit(self, msg: Quit, from_client: Client) -> None:
        pass

    def on_presense(self, msg: Presence, from_client: Client) -> None:
        pass

    def on_chat(self, msg: Chat, from_client: Client) -> None:
        pass

    def on_join(self, msg: Join, from_client: Client) -> None:
        pass

    def on_leave(self, msg: Leave, from_client: Client) -> None:
        pass
