from unittest.mock import MagicMock, call

import pytest
from gb_chat.io.deserializer import Deserializer
from gb_chat.io.message_splitter import MessageSizeError, MessageSplitter
from gb_chat.io.settings import HEADER_BYTEORDER, HEADER_SIZE


@pytest.fixture
def deserializer():
    return MagicMock(spec_set=Deserializer)


@pytest.fixture
def sut(deserializer):
    return MessageSplitter(deserializer)


def test_zero_msg_size_raises(sut):
    with pytest.raises(MessageSizeError):
        sut.feed(b"\0" * HEADER_SIZE)


@pytest.mark.parametrize(
    "data", [int(10).to_bytes(HEADER_SIZE, HEADER_BYTEORDER) + b"abc", b"\0\1"]
)
def test_no_call_deserializer_when_not_enought_data(data, sut, deserializer):
    sut.feed(data)
    assert not deserializer.deserialize.called


def prepare_msgs(*args):
    return b"".join(
        [len(msg).to_bytes(HEADER_SIZE, HEADER_BYTEORDER) + msg for msg in args]
    )


def test_call_deserializer_when_one_msg_feed(sut, deserializer):
    data = prepare_msgs(b"abc")
    sut.feed(data)
    deserializer.deserialize.assert_called_once_with(b"abc")


msg_data = prepare_msgs(b"abc")


@pytest.mark.parametrize(
    "chunk1,chunk2",
    [
        (msg_data[:1], msg_data[1:]),
        (msg_data[:HEADER_SIZE], msg_data[HEADER_SIZE:]),
        (msg_data[: HEADER_SIZE + 1], msg_data[HEADER_SIZE + 1 :]),
    ],
)
def test_call_deserializer_when_one_msg_feed_in_parts(
    chunk1, chunk2, sut, deserializer
):
    sut.feed(chunk1)
    assert not deserializer.deserialize.called
    sut.feed(chunk2)
    deserializer.deserialize.assert_called_once_with(b"abc")


def test_call_deserializer_when_two_msg_feed(sut, deserializer):
    data = prepare_msgs(b"abc", b"cdef")
    sut.feed(data)
    assert deserializer.deserialize.mock_calls == [call(b"abc"), call(b"cdef")]
