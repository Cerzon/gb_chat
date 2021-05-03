from typing import Any

from ..log import get_logger
from .deserializer import Deserializer
from .exceptions import MessageSizeError
from .settings import HEADER_BYTEORDER, HEADER_SIZE

_logger: Any = get_logger()


class MessageSplitter:
    def __init__(self, deserializer: Deserializer) -> None:
        self._deserializer = deserializer
        self._data = b""

    def feed(self, data: bytes) -> None:
        self._data += data
        _logger.debug("Data received", received=len(data), total=len(self._data))
        self._process_data()

    def _process_data(self) -> None:
        if len(self._data) < HEADER_SIZE:
            return

        header = self._data[:HEADER_SIZE]
        msg_size = int.from_bytes(header, HEADER_BYTEORDER)
        if msg_size == 0:
            raise MessageSizeError("Message size is 0")

        rest_data = self._data[HEADER_SIZE:]
        if len(rest_data) < msg_size:
            return

        msg_data = rest_data[:msg_size]
        _logger.debug("Send data to deserializer", msg_size=msg_size)
        self._deserializer.deserialize(msg_data)
        self._data = rest_data[msg_size:]
        self._process_data()
