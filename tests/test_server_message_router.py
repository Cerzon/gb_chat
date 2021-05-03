from unittest.mock import MagicMock

import pytest
from gb_chat.common.exceptions import UnsupportedMessageType
from gb_chat.msg.client_to_server import (AddContact, Authenticate,
                                          ChatFromClient, GetContacts, Join,
                                          Leave, Presence, Quit, RemoveContact)
from gb_chat.server.client import Client
from gb_chat.server.message_router import MessageRouter
from gb_chat.server.server import Server


@pytest.fixture
def server():
    return MagicMock(spec_set=Server)


@pytest.fixture
def client():
    return MagicMock(spec_set=Client)


@pytest.fixture
def sut(server, client):
    return MessageRouter(server, client)


def test_raises_when_unsupported_message_type(sut):
    with pytest.raises(UnsupportedMessageType):
        sut.route(MagicMock())


def test_route_auth(sut, server, client):
    msg = MagicMock(spec=Authenticate)
    sut.route(msg)
    server.on_auth.assert_called_once_with(msg, client)


def test_route_quit(sut, server, client):
    msg = MagicMock(spec=Quit)
    sut.route(msg)
    server.on_quit.assert_called_once_with(msg, client)


def test_route_presence(sut, server, client):
    msg = MagicMock(spec=Presence)
    sut.route(msg)
    server.on_presence.assert_called_once_with(msg, client)


def test_route_chat(sut, server, client):
    msg = MagicMock(spec=ChatFromClient)
    sut.route(msg)
    server.on_chat.assert_called_once_with(msg, client)


def test_route_join(sut, server, client):
    msg = MagicMock(spec=Join)
    sut.route(msg)
    server.on_join.assert_called_once_with(msg, client)


def test_route_leave(sut, server, client):
    msg = MagicMock(spec=Leave)
    sut.route(msg)
    server.on_leave.assert_called_once_with(msg, client)


def test_route_add_contact(sut, server, client):
    msg = MagicMock(spec=AddContact)
    sut.route(msg)
    server.on_add_contact.assert_called_once_with(msg, client)


def test_route_remove_contact(sut, server, client):
    msg = MagicMock(spec=RemoveContact)
    sut.route(msg)
    server.on_remove_contact.assert_called_once_with(msg, client)


def test_route_get_contacts(sut, server, client):
    msg = MagicMock(spec=GetContacts)
    sut.route(msg)
    server.on_get_contacts.assert_called_once_with(msg, client)
