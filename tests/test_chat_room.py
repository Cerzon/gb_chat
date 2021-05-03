from unittest.mock import MagicMock

import pytest
from gb_chat.common.disconnector import Disconnector
from gb_chat.io.message_sender import MessageSender
from gb_chat.msg.client_to_server import ChatFromClient
from gb_chat.msg.server_to_client import ChatToClient
from gb_chat.server.chat_room import ChatRoom
from gb_chat.server.client import Client


@pytest.fixture
def chat_to_client_factory():
    return lambda s, m: ChatToClient(s, m, "#room")


@pytest.fixture
def sut(chat_to_client_factory):
    return ChatRoom(chat_to_client_factory)


def test_empty_when_no_clients(sut):
    assert sut.empty


@pytest.fixture
def client():
    return Client(
        MagicMock(spec_set=MessageSender), MagicMock(spec_set=Disconnector), "username"
    )


def test_join(sut, client):
    sut.join(client)
    assert not sut.empty


@pytest.fixture
def sut_with_client(sut, client):
    sut.join(client)
    return sut


def test_leave(sut_with_client, client):
    sut_with_client.leave(client)
    assert sut_with_client.empty


def test_send_message(sut_with_client, client):
    client2 = Client(
        MagicMock(spec_set=MessageSender), MagicMock(spec_set=Disconnector), "username2"
    )
    sut_with_client.join(client2)

    sut_with_client.send_message(
        ChatFromClient("#doesnt-matter", "message text"), client
    )
    client.msg_sender.send.assert_not_called()
    client2.msg_sender.send.assert_called_with(
        ChatToClient("username", "message text", "#room")
    )
