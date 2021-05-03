from typing import Any

from ..common.exceptions import UnsupportedMessageType
from ..log import get_logger
from ..msg.server_to_client import (ChatToClient, Probe, Response,
                                    ServerToClientMessage)
from .client import Client

_logger: Any = get_logger()


class MessageRouter:
    def __init__(self, client: Client) -> None:
        self._client = client

    def route(self, msg: ServerToClientMessage) -> None:
        _logger.debug("Route message", msg=msg)
        if isinstance(msg, Response):
            self._client.on_response(msg)
        elif isinstance(msg, Probe):
            self._client.on_probe(msg)
        elif isinstance(msg, ChatToClient):
            self._client.on_chat(msg)
        else:
            raise UnsupportedMessageType(f"Unsupported message {type(msg)}")
