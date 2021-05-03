from typing import Any, Callable, Dict

from ..common.exceptions import InvalidRoomName
from ..common.room_name_validator import RoomNameValidator
from ..log import get_logger
from ..msg.client_to_server import ChatFromClient
from ..msg.server_to_client import ChatToClient
from .chat_room import ChatRoom, ChatToClientFactory
from .client import Client

_logger: Any = get_logger()

ChatRoomFactory = Callable[[ChatToClientFactory], ChatRoom]


class ChatRoomManager:
    def __init__(
        self,
        room_name_validator: RoomNameValidator,
        chat_room_factory: ChatRoomFactory = ChatRoom,
    ) -> None:
        self._room_name_validator = room_name_validator
        self._chat_room_factory = chat_room_factory
        self._rooms: Dict[str, ChatRoom] = {}

    def is_valid_name(self, room_name: str) -> bool:
        return self._room_name_validator.is_valid(room_name)

    def join(self, room_name: str, client: Client) -> None:
        if not self.is_valid_name(room_name):
            raise InvalidRoomName(f"{room_name} is not valid")

        if room_name in self._rooms:
            room = self._rooms[room_name]
        else:
            _logger.debug("Room created", room=room_name)
            room = self._chat_room_factory(
                lambda sender, message: ChatToClient(sender, message, room_name)
            )
            self._rooms[room_name] = room

        _logger.info("User joins group", room=room_name, client=client.name)
        room.join(client)

    def leave(
        self, room_name: str, client: Client, log_user_leave: bool = True
    ) -> None:
        if room_name not in self._rooms:
            return

        room = self._rooms[room_name]
        if log_user_leave:
            _logger.info("User leaves group", room=room_name, client=client.name)
        room.leave(client)

        if room.empty:
            _logger.info("Remove empty group", room=room_name)
            del self._rooms[room_name]

    def leave_all(self, client: Client) -> None:
        for room_name in [*self._rooms.keys()]:
            self.leave(room_name, client, False)

    def send_message(self, msg: ChatFromClient, from_client: Client) -> None:
        if msg.to not in self._rooms:
            return

        _logger.info(
            "User sends group message", room=msg.to, from_client=from_client.name
        )
        self._rooms[msg.to].send_message(msg, from_client)
