from typing import Any

from ..log import get_logger

_logger: Any = get_logger()


class SendBuffer:
    def __init__(self) -> None:
        self._data = b""

    @property
    def data(self) -> bytes:
        return self._data

    def send(self, data: bytes) -> None:
        self._data += data
        _logger.debug(
            "Store data to buffer", data_size=len(data), total=len(self._data)
        )

    def bytes_sent(self, size: int) -> None:
        if size > len(self._data):
            raise ValueError(
                f"Sent more than have size={size} len(self.data)={len(self._data)}"
            )

        _logger.debug("Data sent", sent=size)
        self._data = self._data[size:]
