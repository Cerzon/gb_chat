from enum import Enum, auto
from http import HTTPStatus, client
from typing import Any

from ..common.disconnector import Disconnector
from ..common.exceptions import InvalidRoomName
from ..common.room_name_validator import RoomNameValidator
from ..io.message_sender import MessageSender
from ..log import get_logger
from ..msg.client_to_server import (Authenticate, ChatFromClient, Join, Leave,
                                    Presence, Quit)
from ..msg.server_to_client import ChatToClient, Probe, Response
from ..msg.status import Status

_logger: Any = get_logger()


class _State(Enum):
    START = auto()
    LOGIN_SENT = auto()
    LOGGED_IN = auto()
    FINISH = auto()


class Client:
    def __init__(
        self,
        msg_sender: MessageSender,
        room_name_validator: RoomNameValidator,
        disconnector: Disconnector,
    ) -> None:
        self._msg_sender = msg_sender
        self._room_name_validator = room_name_validator
        self._disconnector = disconnector
        self._state: _State = _State.START

    def login(self, username: str, password: str) -> None:
        if self._state != _State.START:
            return

        _logger.info("Send auth", username=username)
        self._msg_sender.send(Authenticate(username, password))
        self._state = _State.LOGIN_SENT

    def send_msg(self, to_user: str, msg: str) -> None:
        if self._state != _State.LOGGED_IN:
            return

        _logger.info("Send chat message", to=to_user, msg=msg)
        self._msg_sender.send(ChatFromClient(to_user, msg))

    def join_room(self, room: str) -> None:
        if self._state != _State.LOGGED_IN:
            return

        if not self._room_name_validator.is_valid(room):
            raise InvalidRoomName(f"{room} is invalid")

        _logger.info("Join room", room=room)
        self._msg_sender.send(Join(room))

    def leave_room(self, room: str) -> None:
        if self._state != _State.LOGGED_IN:
            return

        if not self._room_name_validator.is_valid(room):
            raise InvalidRoomName(f"{room} is invalid")

        _logger.info("Leave room", room=room)
        self._msg_sender.send(Leave(room))

    def quit(self) -> None:
        if self._state != _State.LOGGED_IN:
            return

        self._msg_sender.send(Quit())
        self._state = _State.FINISH

    def on_response(self, msg: Response) -> None:
        if self._state == _State.LOGIN_SENT:
            self._handle_auth_response(msg)
        else:
            print(f"Error {msg.code} ({client.responses[msg.code]}): {msg.msg}")

    def on_probe(self, msg: Probe) -> None:
        _logger.debug("Probe received")

    def on_chat(self, msg: ChatToClient) -> None:
        _logger.info("Chat received", from_user=msg.sender, msg=msg.message)
        if msg.room is None:
            print(f"Message from {msg.sender}: {msg.message}")
        else:
            print(f"Message from {msg.room} ({msg.sender}): {msg.message}")

    def _handle_auth_response(self, msg: Response) -> None:
        if msg.code == HTTPStatus.OK:
            _logger.info("Login success")
            self._state = _State.LOGGED_IN
            self._msg_sender.send(Presence(Status.ONLINE))
        else:
            _logger.error("Login failure", error_code=msg.code, error_msg=msg.msg)
            self._state = _State.FINISH
            self._disconnector.disconnect()
