from unittest.mock import MagicMock

import pytest
from gb_chat.msg.client_to_server import (Authenticate, Chat, Join, Leave,
                                          Presence, Quit)
from gb_chat.server.message_router import MessageRouter, UnsupportedMessageType
from gb_chat.server.server import Server


@pytest.fixture
def server():
    return MagicMock(spec_set=Server)


@pytest.fixture
def sut(server):
    return MessageRouter(server)


def test_raises_when_unsupported_message_type(sut):
    with pytest.raises(UnsupportedMessageType):
        sut.route(MagicMock())


def test_route_auth(sut, server):
    msg = MagicMock(spec=Authenticate)
    sut.route(msg)
    server.on_auth.assert_called_once_with(msg)


def test_route_quit(sut, server):
    msg = MagicMock(spec=Quit)
    sut.route(msg)
    server.on_quit.assert_called_once_with(msg)


def test_route_presense(sut, server):
    msg = MagicMock(spec=Presence)
    sut.route(msg)
    server.on_presense.assert_called_once_with(msg)


def test_route_chat(sut, server):
    msg = MagicMock(spec=Chat)
    sut.route(msg)
    server.on_chat.assert_called_once_with(msg)


def test_route_join(sut, server):
    msg = MagicMock(spec=Join)
    sut.route(msg)
    server.on_join.assert_called_once_with(msg)


def test_route_leave(sut, server):
    msg = MagicMock(spec=Leave)
    sut.route(msg)
    server.on_leave.assert_called_once_with(msg)
