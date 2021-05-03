from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from gb_chat.client.message_router import MessageRouter as ClientMessageRouter
from gb_chat.common.exceptions import UnsupportedMessageType
from gb_chat.io.message_sender import MessageSender
from gb_chat.io.parsed_msg_handler import ParsedMessageHandler
from gb_chat.io.serializer import Serializer
from gb_chat.msg.client_to_server import (AddContact, Authenticate,
                                          ChatFromClient, GetContacts, Join,
                                          Leave, Presence, Quit, RemoveContact)
from gb_chat.msg.server_to_client import ChatToClient, Probe, Response
from gb_chat.msg.status import Status
from gb_chat.server.message_router import MessageRouter as ServerMessageRouter

from conftest import TIME_FACTORY_TIMESTAMP

test_data_client_to_server = [
    (
        Authenticate("user_name", "pass"),
        {
            "action": "authenticate",
            "time": TIME_FACTORY_TIMESTAMP,
            "user": {"account_name": "user_name", "password": "pass"},
        },
    ),
    (Quit(), {"action": "quit"}),
    (Presence(), {"action": "presence", "time": TIME_FACTORY_TIMESTAMP}),
    (
        Presence(Status.ONLINE),
        {"action": "presence", "time": TIME_FACTORY_TIMESTAMP, "status": "online"},
    ),
    (
        ChatFromClient("recipient", "message text"),
        {
            "action": "msg",
            "time": TIME_FACTORY_TIMESTAMP,
            "to": "recipient",
            "message": "message text",
        },
    ),
    (
        Join("#room_name"),
        {"action": "join", "room": "#room_name", "time": TIME_FACTORY_TIMESTAMP},
    ),
    (
        Leave("#room_name"),
        {"action": "leave", "room": "#room_name", "time": TIME_FACTORY_TIMESTAMP},
    ),
    (
        AddContact("user_name"),
        {"action": "add_contact", "user": "user_name", "time": TIME_FACTORY_TIMESTAMP},
    ),
    (
        RemoveContact("user_name"),
        {"action": "del_contact", "user": "user_name", "time": TIME_FACTORY_TIMESTAMP},
    ),
    (GetContacts(), {"action": "get_contacts", "time": TIME_FACTORY_TIMESTAMP}),
]

test_data_server_to_client = [
    (
        Response(HTTPStatus.OK, "message text"),
        {"response": 200, "message": "message text", "time": TIME_FACTORY_TIMESTAMP},
    ),
    (Probe(), {"action": "probe", "time": TIME_FACTORY_TIMESTAMP}),
    (
        ChatToClient("sender", "message text"),
        {
            "action": "msg",
            "time": TIME_FACTORY_TIMESTAMP,
            "from": "sender",
            "message": "message text",
        },
    ),
    (
        ChatToClient("sender", "message text", "#room"),
        {
            "action": "msg",
            "time": TIME_FACTORY_TIMESTAMP,
            "from": "sender",
            "message": "message text",
            "room": "#room",
        },
    ),
]


@pytest.mark.parametrize(
    "msg,expected", test_data_client_to_server + test_data_server_to_client
)
def test_convert_msg_to_dict(msg, expected, time_factory):
    serializer = MagicMock(spec_set=Serializer)
    sut = MessageSender(serializer, time_factory)
    sut.send(msg)
    serializer.serialize.assert_called_once_with(expected)


def test_send_raises_when_unsupported_message(time_factory):
    serializer = MagicMock(spec_set=Serializer)
    sut = MessageSender(serializer, time_factory)
    with pytest.raises(UnsupportedMessageType):
        sut.send(MagicMock())


@pytest.mark.parametrize("expected,msg_dict", test_data_client_to_server)
def test_convert_incomming_server_dict_to_msg(expected, msg_dict):
    router = MagicMock(spec_set=ServerMessageRouter)
    sut = ParsedMessageHandler(router)
    sut.process(msg_dict)
    router.route.assert_called_once_with(expected)


@pytest.mark.parametrize("expected,msg_dict", test_data_server_to_client)
def test_convert_incomming_client_dict_to_msg(expected, msg_dict):
    router = MagicMock(spec_set=ClientMessageRouter)
    sut = ParsedMessageHandler(router)
    sut.process(msg_dict)
    router.route.assert_called_once_with(expected)


@pytest.mark.parametrize(
    "msg,router",
    [
        ({"action": "foo"}, MagicMock(spec_set=ServerMessageRouter)),
        ({"a": "b"}, MagicMock(spec_set=ServerMessageRouter)),
        ({"a": "b"}, MagicMock(spec_set=ClientMessageRouter)),
        ({"action": "foo"}, MagicMock(spec_set=ClientMessageRouter)),
    ],
)
def test_process_raises_when_unsupported_msg(msg, router):
    sut = ParsedMessageHandler(router)
    with pytest.raises(UnsupportedMessageType):
        sut.process(msg)
