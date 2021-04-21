from json import dumps
from typing import Callable

from .exceptions import SerializationError
from .json import JSON
from .message_framer import MessageFramer
from .settings import MSG_ENCODING

Encode = Callable[[str], bytes]
Dumps = Callable[[JSON], str]


class Serializer:
    def __init__(
        self,
        msg_framer: MessageFramer,
        dumps: Dumps = dumps,
        encode: Encode = lambda x: x.encode(MSG_ENCODING),
    ) -> None:
        self._msg_framer = msg_framer
        self._dumps = dumps
        self._encode = encode

    def serialize(self, msg: JSON) -> None:
        try:
            msg_str = self._dumps(msg)
            msg_bytes = self._encode(msg_str)
        except (UnicodeError, TypeError, OverflowError, ValueError) as e:
            raise SerializationError() from e

        self._msg_framer.frame(msg_bytes)
