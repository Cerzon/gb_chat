from json import JSONDecodeError
from unittest.mock import MagicMock

import pytest
from gb_chat.io.deserializer import Deserializer
from gb_chat.io.exceptions import DeserializationError
from gb_chat.io.parsed_msg_handler import ParsedMessageHandler


@pytest.fixture
def handler():
    return MagicMock(spec_set=ParsedMessageHandler)


@pytest.fixture
def sut(handler):
    return Deserializer(handler)


def test_raises_when_decode_error(handler):
    decode = MagicMock(side_effect=UnicodeError())
    sut = Deserializer(handler, decode=decode)
    with pytest.raises(DeserializationError):
        sut.deserialize(b"abc")


def test_raises_when_json_error():
    loads = MagicMock(side_effect=JSONDecodeError("msg", "doc", 1))
    sut = Deserializer(handler, loads=loads)
    with pytest.raises(DeserializationError):
        sut.deserialize(b"abc")


def test_call_process_when_msg_deserialized(sut, handler):
    sut.deserialize(b'{"a": "b"}')
    handler.process.assert_called_once_with({"a": "b"})
