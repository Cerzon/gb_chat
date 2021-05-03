from json import JSONDecodeError, loads
from typing import Any, Callable

from ..log import get_logger
from .exceptions import DeserializationError
from .json import JSON
from .parsed_msg_handler import ParsedMessageHandler
from .settings import MSG_ENCODING

_logger: Any = get_logger()

Decode = Callable[[bytes], str]
Loads = Callable[[str], JSON]


class Deserializer:
    def __init__(
        self,
        handler: ParsedMessageHandler,
        decode: Decode = lambda x: x.decode(MSG_ENCODING),
        loads: Loads = loads,
    ) -> None:
        self._handler = handler
        self._decode = decode
        self._loads = loads

    def deserialize(self, msg: bytes) -> None:
        try:
            msg_str = self._decode(msg)
            msg_dict = self._loads(msg_str)
            _logger.debug("Deserialize message", msg=msg_dict)
        except (UnicodeError, JSONDecodeError) as e:
            raise DeserializationError() from e

        self._handler.process(msg_dict)
