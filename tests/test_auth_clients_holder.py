from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from gb_chat.common.disconnector import Disconnector
from gb_chat.io.message_sender import MessageSender
from gb_chat.msg.server_to_client import Response
from gb_chat.server.auth_clients_holder import AuthClientsHolder
from gb_chat.server.client import Client


@pytest.fixture
def client():
    return Client(MagicMock(spec_set=MessageSender), MagicMock(spec_set=Disconnector))


@pytest.fixture
def sut():
    return AuthClientsHolder()


def test_add_client_raises_when_no_name(sut, client):
    with pytest.raises(ValueError):
        sut.add_client(client)


@pytest.fixture
def client_with_name():
    return Client(
        MagicMock(spec_set=MessageSender), MagicMock(spec_set=Disconnector), "username"
    )


def test_add_client_with_name(sut, client_with_name):
    sut.add_client(client_with_name)
    assert sut.is_authed(client_with_name)
    assert sut.find_client(client_with_name.name) is client_with_name
    assert [x for x in sut.all] == [client_with_name]


def test_remove_client_raises_when_no_name(sut, client):
    with pytest.raises(ValueError):
        sut.remove_client(client)


def test_remove_client_raises_when_client_not_in_list(sut, client_with_name):
    with pytest.raises(ValueError):
        sut.remove_client(client_with_name)


def test_remove_client(sut, client_with_name):
    sut.add_client(client_with_name)
    sut.remove_client(client_with_name)
    assert not sut.is_authed(client_with_name)
    assert sut.find_client(client_with_name.name) is None


class Sut:
    auth = AuthClientsHolder()

    def __init__(self, mock) -> None:
        self.mock = mock

    @auth.required
    def method(self, msg, from_client):
        self.mock(msg, from_client)


def test_required_disconnect_client_when_not_authed(client_with_name):
    mock = MagicMock()
    sut = Sut(mock)
    sut.method(MagicMock(), client_with_name)
    mock.assert_not_called()
    client_with_name.msg_sender.send.assert_called_once_with(
        Response(HTTPStatus.UNAUTHORIZED, "Allowed only for authed users")
    )
    client_with_name.disconnector.disconnect.assert_not_called()


def test_required_called_when_authed(client_with_name):
    mock = MagicMock()
    msg = MagicMock()
    sut = Sut(mock)
    sut.auth.add_client(client_with_name)
    sut.method(msg, client_with_name)
    mock.assert_called_once_with(msg, client_with_name)
    client_with_name.msg_sender.send.assert_not_called()
    client_with_name.disconnector.disconnect.assert_not_called()
