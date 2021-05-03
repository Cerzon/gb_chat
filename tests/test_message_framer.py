from unittest.mock import MagicMock

import pytest
from gb_chat.io.exceptions import MessageTooBig
from gb_chat.io.message_framer import MessageFramer
from gb_chat.io.send_buffer import SendBuffer


@pytest.fixture
def send_buffer():
    return MagicMock(spec_set=SendBuffer)


@pytest.fixture
def sut(send_buffer):
    return MessageFramer(send_buffer)


def test_make_frame(sut, send_buffer):
    sut.frame(b'{"a": "b"}')
    send_buffer.send.assert_called_once_with(b'\x00\x00\x00\x0A{"a": "b"}')


def test_raises_when_msg_is_too_big(sut):
    class FakeData:
        def __len__(self) -> int:
            return 0x1_00_00_00_00

    data = FakeData()
    with pytest.raises(MessageTooBig):
        sut.frame(data)
