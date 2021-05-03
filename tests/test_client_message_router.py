from unittest.mock import MagicMock

import pytest
from gb_chat.client.client import Client
from gb_chat.client.message_router import MessageRouter
from gb_chat.common.exceptions import UnsupportedMessageType
from gb_chat.msg.server_to_client import ChatToClient, Probe, Response


@pytest.fixture
def client():
    return MagicMock(spec_set=Client)


@pytest.fixture
def sut(client):
    return MessageRouter(client)


def test_raises_when_unsupported_message_type(sut):
    with pytest.raises(UnsupportedMessageType):
        sut.route(MagicMock())


def test_route_response(sut, client):
    msg = MagicMock(spec=Response)
    sut.route(msg)
    client.on_response.assert_called_once_with(msg)


def test_route_probe(sut, client):
    msg = MagicMock(spec=Probe)
    sut.route(msg)
    client.on_probe.assert_called_once_with(msg)


def test_route_probe(sut, client):
    msg = MagicMock(spec=ChatToClient)
    sut.route(msg)
    client.on_chat.assert_called_once_with(msg)
