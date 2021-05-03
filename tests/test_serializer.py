from unittest.mock import MagicMock

import pytest
from gb_chat.io.exceptions import SerializationError
from gb_chat.io.message_framer import MessageFramer
from gb_chat.io.serializer import Serializer


@pytest.fixture
def msg_framer():
    return MagicMock(spec_set=MessageFramer)


@pytest.fixture
def sut(msg_framer):
    return Serializer(msg_framer)


def test_raises_when_encode_error(msg_framer):
    encode = MagicMock(side_effect=UnicodeError())
    sut = Serializer(msg_framer, encode=encode)
    with pytest.raises(SerializationError):
        sut.serialize({"a": "b"})


@pytest.mark.parametrize("exc", [TypeError(), OverflowError(), ValueError()])
def test_raises_when_json_error(msg_framer, exc):
    dumps = MagicMock(side_effect=exc)
    sut = Serializer(msg_framer, dumps=dumps)
    with pytest.raises(SerializationError):
        sut.serialize({"a": "b"})


def test_call_send_when_msg_serialized(sut, msg_framer):
    sut.serialize({"a": "b"})
    msg_framer.frame.assert_called_once_with(b'{"a": "b"}')
