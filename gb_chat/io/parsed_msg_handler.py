from http import HTTPStatus
from typing import Any, Optional, Union, cast

from ..client.message_router import MessageRouter as ClientMessageRouter
from ..common.exceptions import UnsupportedMessageType
from ..log import get_logger
from ..msg.client_to_server import (AddContact, Authenticate, ChatFromClient,
                                    GetContacts, Join, Leave, Presence, Quit,
                                    RemoveContact)
from ..msg.server_to_client import ChatToClient, Probe, Response
from ..msg.status import Status
from ..server.message_router import MessageRouter as ServerMessageRouter
from .json import JSON

_logger: Any = get_logger()


class ParsedMessageHandler:
    def __init__(
        self, msg_router: Union[ServerMessageRouter, ClientMessageRouter]
    ) -> None:
        self._msg_router = msg_router

    def process(self, msg: JSON) -> None:
        _logger.debug("Process message", msg=msg)
        if isinstance(self._msg_router, ServerMessageRouter):
            self._process_incomming_server_msg(msg)
        else:
            self._process_incomming_client_msg(msg)

    def _process_incomming_server_msg(self, msg: JSON) -> None:
        router = cast(ServerMessageRouter, self._msg_router)
        try:
            action = msg["action"]
        except KeyError:
            raise UnsupportedMessageType("No action field in message")

        if action == "authenticate":
            user = msg["user"]
            router.route(Authenticate(user["account_name"], user["password"]))
        elif action == "quit":
            router.route(Quit())
        elif action == "presence":
            status: Optional[Status] = None
            if "status" in msg:
                status = Status(msg["status"])
            router.route(Presence(status))
        elif action == "msg":
            router.route(ChatFromClient(msg["to"], msg["message"]))
        elif action == "join":
            router.route(Join(msg["room"]))
        elif action == "leave":
            router.route(Leave(msg["room"]))
        elif action == "add_contact":
            router.route(AddContact(msg["user"]))
        elif action == "del_contact":
            router.route(RemoveContact(msg["user"]))
        elif action == "get_contacts":
            router.route(GetContacts())
        else:
            raise UnsupportedMessageType(f"Unsupported action {action}")

    def _process_incomming_client_msg(self, msg: JSON) -> None:
        router = cast(ClientMessageRouter, self._msg_router)
        if "action" in msg:
            action = msg["action"]
            if action == "probe":
                router.route(Probe())
            elif action == "msg":
                router.route(
                    ChatToClient(
                        msg["from"], msg["message"], msg.setdefault("room", None)
                    )
                )
            else:
                raise UnsupportedMessageType(f"Unsupported msg action {action}")
        elif "response" in msg:
            router.route(Response(HTTPStatus(msg["response"]), msg["message"]))
        else:
            raise UnsupportedMessageType(f"Unsupported msg {msg}")
