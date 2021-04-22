from functools import partial, wraps
from typing import Any, Callable, Dict, Optional, Union, ValuesView

from ..log import get_logger
from ..msg.client_to_server import ClientToServerMessage
from .client import Client

_logger: Any = get_logger()


def _auth_deco(holder: "AuthClientsHolder", func: Callable) -> Callable:
    @wraps(func)
    def decorated(
        class_self: object, msg: ClientToServerMessage, from_client: Client
    ) -> None:
        if not holder.is_authed(from_client):
            _logger.warning("This msg is not allowed for unauthed user")
            from_client.disconnector.disconnect()
            return

        func(class_self, msg, from_client)

    return decorated


class AuthClientsHolder:
    def __init__(self) -> None:
        self._auth_clients: Dict[str, Client] = {}

    def add_client(self, client: Client) -> None:
        if client.name is None:
            raise ValueError("Client with empty name")

        self._auth_clients[client.name] = client

    def remove_client(self, client: Client) -> None:
        if client.name is None:
            raise ValueError("Client with empty name")

        if client.name not in self._auth_clients:
            raise ValueError("Client is not in list")

        del self._auth_clients[client.name]

    def is_authed(self, client: Client) -> bool:
        return client.name is not None and client.name in self._auth_clients

    def find_client(self, name: str) -> Optional[Client]:
        try:
            return self._auth_clients[name]
        except KeyError:
            return None

    @property
    def all(self) -> ValuesView[Client]:
        return self._auth_clients.values()

    @property
    def required(self) -> Callable[[Callable], Callable]:
        return partial(_auth_deco, self)
