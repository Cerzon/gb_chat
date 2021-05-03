from unittest.mock import MagicMock

from gb_chat.io.deserializer import Deserializer
from gb_chat.io.message_framer import MessageFramer
from gb_chat.io.message_splitter import MessageSplitter
from gb_chat.io.parsed_msg_handler import ParsedMessageHandler
from gb_chat.io.send_buffer import SendBuffer
from gb_chat.io.serializer import Serializer


def test_serialize_deserialize():
    send_buffer = SendBuffer()
    msg_framer = MessageFramer(send_buffer)
    serializer = Serializer(msg_framer)

    parsed_msg_handler = MagicMock(spec_set=ParsedMessageHandler)
    deserializer = Deserializer(parsed_msg_handler)
    msg_splitter = MessageSplitter(deserializer)

    serializer.serialize({"a": "b"})
    msg_splitter.feed(send_buffer.data)
    parsed_msg_handler.process.assert_called_once_with({"a": "b"})
