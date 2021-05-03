from datetime import datetime
from time import time
from typing import Any, Callable, Union

from ..common.exceptions import UnsupportedMessageType
from ..common.types import TimeFactory
from ..log import get_logger
from ..msg.client_to_server import (AddContact, Authenticate, ChatFromClient,
                                    ClientToServerMessage, GetContacts, Join,
                                    Leave, Presence, Quit, RemoveContact)
from ..msg.server_to_client import (ChatToClient, Probe, Response,
                                    ServerToClientMessage)
from .json import JSON
from .serializer import Serializer

_logger: Any = get_logger()


Message = Union[ClientToServerMessage, ServerToClientMessage]


class MessageSender:
    def __init__(
        self, serializer: Serializer, time_factory: TimeFactory = datetime.utcnow
    ) -> None:
        self._serializer = serializer
        self._time_factory = time_factory

    def send(self, msg: Message) -> None:
        _logger.debug("Convert", msg=msg)
        msg_dict = self._convert(msg)
        if not isinstance(msg, Quit):
            msg_dict["time"] = self._time_factory().timestamp()
        self._serializer.serialize(msg_dict)

    @staticmethod
    def _convert(msg: Message) -> JSON:
        if isinstance(msg, Response):
            return {"response": msg.code, "message": msg.msg}
        elif isinstance(msg, Probe):
            return {"action": "probe"}
        elif isinstance(msg, ChatToClient):
            msg_json = {
                "action": "msg",
                "from": msg.sender,
                "message": msg.message,
            }
            if msg.room is not None:
                msg_json["room"] = msg.room

            return msg_json
        elif isinstance(msg, Authenticate):
            return {
                "action": "authenticate",
                "user": {
                    "account_name": msg.login,
                    "password": msg.password,
                },
            }
        elif isinstance(msg, Quit):
            return {"action": "quit"}
        elif isinstance(msg, Presence):
            res = {"action": "presence"}
            if msg.status:
                res["status"] = msg.status.value
            return res
        elif isinstance(msg, ChatFromClient):
            return {"action": "msg", "to": msg.to, "message": msg.message}
        elif isinstance(msg, Join):
            return {"action": "join", "room": msg.room}
        elif isinstance(msg, Leave):
            return {"action": "leave", "room": msg.room}
        elif isinstance(msg, AddContact):
            return {"action": "add_contact", "user": msg.user}
        elif isinstance(msg, RemoveContact):
            return {"action": "del_contact", "user": msg.user}
        elif isinstance(msg, GetContacts):
            return {"action": "get_contacts"}
        else:
            raise UnsupportedMessageType("Can't convert message {type(msg)}")
