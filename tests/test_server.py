from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from gb_chat.common.disconnector import Disconnector
from gb_chat.io.message_sender import MessageSender
from gb_chat.msg.client_to_server import (AddContact, Authenticate,
                                          ChatFromClient, GetContacts, Join,
                                          Presence, Quit, RemoveContact)
from gb_chat.msg.server_to_client import ChatToClient, Probe, Response
from gb_chat.msg.status import Status
from gb_chat.server.chat_room_manager import ChatRoomManager
from gb_chat.server.client import Client
from gb_chat.server.server import Server


@pytest.fixture
def chat_room_manager():
    res = MagicMock(spec_set=ChatRoomManager)
    res.is_valid_name.return_value = False
    return res


@pytest.fixture
def sut(chat_room_manager):
    return Server(chat_room_manager)


@pytest.fixture
def client():
    return Client(MagicMock(spec_set=MessageSender), MagicMock(spec_set=Disconnector))


def test_client_connected(sut, client):
    sut.on_client_connected(client)


@pytest.fixture
def sut_with_client(sut, client):
    sut.on_client_connected(client)
    return sut


def test_disconnected_not_authed_client(sut_with_client, client):
    sut_with_client.on_client_disconnected(client)


def test_send_400_when_receive_auth_request_with_invalid_name(
    sut_with_client, chat_room_manager, client
):
    chat_room_manager.is_valid_name.return_value = True
    sut_with_client.on_auth(Authenticate("#username", "password"), client)

    chat_room_manager.is_valid_name.assert_called_once_with("#username")
    client.msg_sender.send.assert_called_once_with(
        Response(HTTPStatus.BAD_REQUEST, "Invalid name")
    )


def test_send_200_when_receive_auth_request(sut_with_client, client):
    sut_with_client.on_auth(Authenticate("username", "password"), client)

    assert client.name == "username"
    client.msg_sender.send.assert_called_once_with(
        Response(HTTPStatus.OK, "Login successful")
    )


@pytest.fixture
def sut_with_authed_client(sut_with_client, chat_room_manager, client):
    sut_with_client.on_auth(Authenticate("username", "password"), client)
    client.msg_sender.send.reset_mock()
    chat_room_manager.is_valid_name.reset_mock()
    return sut_with_client


def test_disconnected_authed_client(sut_with_authed_client, chat_room_manager, client):
    sut_with_authed_client.on_client_disconnected(client)
    chat_room_manager.leave_all.assert_called_once_with(client)


def test_not_send_probes_when_not_authed(sut_with_client, client):
    sut_with_client.send_probes()
    client.msg_sender.send.assert_not_called()


def test_not_send_probes_when_not_authed(sut_with_authed_client, client):
    sut_with_authed_client.send_probes()
    client.msg_sender.send.assert_called_once_with(Probe())


def test_disconnect_client_on_quit_msg(sut_with_client, client):
    sut_with_client.on_quit(Quit(), client)
    client.disconnector.disconnect.assert_called_once_with()


def test_on_chat_401_when_not_authed(sut_with_client, client):
    sut_with_client.on_chat(ChatFromClient("username", "msg"), client)
    client.msg_sender.send.assert_called_once_with(
        Response(HTTPStatus.UNAUTHORIZED, "Allowed only for authed users")
    )
    client.disconnector.disconnect.assert_not_called()


def test_on_chat_ignores_msg_to_self(sut_with_authed_client, client):
    sut_with_authed_client.on_chat(ChatFromClient(client.name, "msg"), client)
    client.msg_sender.send.assert_not_called()


def test_on_presence_401_when_not_auth(sut_with_client, client):
    sut_with_client.on_presence(Presence(Status.ONLINE), client)
    client.msg_sender.send.assert_called_once_with(
        Response(HTTPStatus.UNAUTHORIZED, "Allowed only for authed users")
    )
    client.disconnector.disconnect.assert_not_called()


def test_on_presence_without_status(sut_with_authed_client, client):
    sut_with_authed_client.on_presence(Presence(), client)
    client.disconnector.disconnect.assert_not_called()


def test_on_presence(sut_with_authed_client, client):
    sut_with_authed_client.on_presence(Presence(Status.ONLINE), client)
    client.disconnector.disconnect.assert_not_called()


def test_on_join_401_when_not_auth(sut_with_client, client):
    sut_with_client.on_join(Join("#room"), client)
    client.msg_sender.send.assert_called_once_with(
        Response(HTTPStatus.UNAUTHORIZED, "Allowed only for authed users")
    )
    client.disconnector.disconnect.assert_not_called()


def test_on_join(sut_with_authed_client, chat_room_manager, client):
    sut_with_authed_client.on_join(Join("#room"), client)
    chat_room_manager.join.assert_called_once_with("#room", client)


def test_on_leave_401_when_not_auth(sut_with_client, client):
    sut_with_client.on_leave(Join("#room"), client)
    client.msg_sender.send.assert_called_once_with(
        Response(HTTPStatus.UNAUTHORIZED, "Allowed only for authed users")
    )
    client.disconnector.disconnect.assert_not_called()


def test_on_leave(sut_with_authed_client, chat_room_manager, client):
    sut_with_authed_client.on_leave(Join("#room"), client)
    chat_room_manager.leave.assert_called_once_with("#room", client)


@pytest.fixture
def client2():
    return Client(MagicMock(spec_set=MessageSender), MagicMock(spec_set=Disconnector))


@pytest.fixture
def sut_with_client2(sut_with_authed_client, client2):
    sut_with_authed_client.on_client_connected(client2)
    return sut_with_authed_client


def test_on_chat_ignores_msg_to_not_authed(sut_with_client2, client, client2):
    sut_with_client2.on_chat(ChatFromClient("to name", "msg"), client)
    client2.msg_sender.send.assert_not_called()


@pytest.fixture
def sut_with_two_authed_clients(sut_with_client2, chat_room_manager, client2):
    sut_with_client2.on_auth(Authenticate("username2", "password"), client2)
    assert client2.name == "username2"
    client2.msg_sender.send.reset_mock()
    chat_room_manager.is_valid_name.reset_mock()
    return sut_with_client2


def test_on_chat_send_message_to_client(sut_with_two_authed_clients, client, client2):
    sut_with_two_authed_clients.on_chat(
        ChatFromClient(client2.name, "message text"), client
    )
    client2.msg_sender.send.assert_called_once_with(
        ChatToClient(client.name, "message text")
    )


def test_on_chat_to_room(sut_with_authed_client, chat_room_manager, client):
    chat_room_manager.is_valid_name.return_value = True
    msg = ChatFromClient("#room", "message text")
    sut_with_authed_client.on_chat(msg, client)

    chat_room_manager.is_valid_name.assert_called_once_with("#room")
    chat_room_manager.send_message.assert_called_once_with(msg, client)


def test_on_add_contact_401_when_not_authed(sut_with_client, client):
    msg = AddContact("other_user")
    sut_with_client.on_add_contact(msg, client)

    client.msg_sender.send.assert_called_once_with(
        Response(HTTPStatus.UNAUTHORIZED, "Allowed only for authed users")
    )
    client.disconnector.disconnect.assert_not_called()


def test_on_remove_contact_401_when_not_authed(sut_with_client, client):
    msg = RemoveContact("other_user")
    sut_with_client.on_remove_contact(msg, client)

    client.msg_sender.send.assert_called_once_with(
        Response(HTTPStatus.UNAUTHORIZED, "Allowed only for authed users")
    )
    client.disconnector.disconnect.assert_not_called()


def test_on_get_contacts_401_when_not_authed(sut_with_client, client):
    msg = GetContacts()
    sut_with_client.on_get_contacts(msg, client)

    client.msg_sender.send.assert_called_once_with(
        Response(HTTPStatus.UNAUTHORIZED, "Allowed only for authed users")
    )
    client.disconnector.disconnect.assert_not_called()
