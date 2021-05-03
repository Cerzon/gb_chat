from typing import Any

from ..common.exceptions import UnsupportedMessageType
from ..log import get_logger
from ..msg.client_to_server import (AddContact, Authenticate, ChatFromClient,
                                    ClientToServerMessage, GetContacts, Join,
                                    Leave, Presence, Quit, RemoveContact)
from .client import Client
from .server import Server

_logger: Any = get_logger()


class MessageRouter:
    def __init__(self, server: Server, client: Client) -> None:
        self._server = server
        self._client = client

    def route(self, msg: ClientToServerMessage) -> None:
        _logger.debug("Route message", msg=msg)
        if isinstance(msg, Authenticate):
            self._server.on_auth(msg, self._client)
        elif isinstance(msg, Quit):
            self._server.on_quit(msg, self._client)
        elif isinstance(msg, Presence):
            self._server.on_presence(msg, self._client)
        elif isinstance(msg, ChatFromClient):
            self._server.on_chat(msg, self._client)
        elif isinstance(msg, Join):
            self._server.on_join(msg, self._client)
        elif isinstance(msg, Leave):
            self._server.on_leave(msg, self._client)
        elif isinstance(msg, AddContact):
            self._server.on_add_contact(msg, self._client)
        elif isinstance(msg, RemoveContact):
            self._server.on_remove_contact(msg, self._client)
        elif isinstance(msg, GetContacts):
            self._server.on_get_contacts(msg, self._client)
        else:
            raise UnsupportedMessageType(f"Unsupported message {type(msg)}")
