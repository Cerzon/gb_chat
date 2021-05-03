from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from gb_chat.client.client import Client
from gb_chat.common.disconnector import Disconnector
from gb_chat.common.exceptions import InvalidRoomName
from gb_chat.common.room_name_validator import RoomNameValidator
from gb_chat.io.message_sender import MessageSender
from gb_chat.msg.client_to_server import (Authenticate, ChatFromClient, Join,
                                          Leave, Presence, Quit)
from gb_chat.msg.server_to_client import Response
from gb_chat.msg.status import Status


@pytest.fixture
def msg_sender():
    return MagicMock(spec_set=MessageSender)


@pytest.fixture
def room_name_validator():
    res = MagicMock(spec_set=RoomNameValidator)
    res.is_valid.return_value = True
    return res


@pytest.fixture
def disconnector():
    return MagicMock(spec_set=Disconnector)


@pytest.fixture
def sut_start(msg_sender, room_name_validator, disconnector):
    return Client(msg_sender, room_name_validator, disconnector)


def test_send_login(sut_start, msg_sender):
    sut_start.login("username", "password")
    msg_sender.send.assert_called_once_with(Authenticate("username", "password"))


@pytest.fixture
def sut_login_sent(sut_start, msg_sender):
    sut_start.login("username", "password")
    msg_sender.send.reset_mock()
    return sut_start


def test_send_presence_when_success_login(sut_login_sent, msg_sender):
    sut_login_sent.on_response(Response(HTTPStatus.OK, "OK"))
    msg_sender.send.assert_called_once_with(Presence(Status.ONLINE))


@pytest.mark.parametrize("code", [HTTPStatus.BAD_REQUEST, HTTPStatus.UNAUTHORIZED])
def test_disconnect_when_login_failed(code, sut_login_sent, msg_sender, disconnector):
    sut_login_sent.on_response(Response(code, "error"))
    disconnector.disconnect.assert_called_once()
    msg_sender.send.assert_not_called()


@pytest.fixture
def sut_logged_in(sut_login_sent, msg_sender):
    sut_login_sent.on_response(Response(HTTPStatus.OK, "OK"))
    msg_sender.send.reset_mock()
    return sut_login_sent


def test_send_msg_when_logged_in(sut_logged_in, msg_sender):
    sut_logged_in.send_msg("to_user", "message text")
    msg_sender.send.assert_called_once_with(ChatFromClient("to_user", "message text"))


def test_join_room_when_logged_in(sut_logged_in, msg_sender, room_name_validator):
    sut_logged_in.join_room("#room")
    room_name_validator.is_valid.assert_called_once_with("#room")
    msg_sender.send.assert_called_once_with(Join("#room"))


def test_join_room_raises_when_logged_in_and_invalid_name(
    sut_logged_in, msg_sender, room_name_validator
):
    room_name_validator.is_valid.return_value = False
    with pytest.raises(InvalidRoomName):
        sut_logged_in.join_room("#room")

    room_name_validator.is_valid.assert_called_once_with("#room")
    msg_sender.send.assert_not_called()


def test_leave_room_when_logged_in(sut_logged_in, msg_sender, room_name_validator):
    sut_logged_in.leave_room("#room")
    room_name_validator.is_valid.assert_called_once_with("#room")
    msg_sender.send.assert_called_once_with(Leave("#room"))


def test_leave_room_raises_when_logged_in_and_invalid_name(
    sut_logged_in, msg_sender, room_name_validator
):
    room_name_validator.is_valid.return_value = False
    with pytest.raises(InvalidRoomName):
        sut_logged_in.leave_room("#room")

    room_name_validator.is_valid.assert_called_once_with("#room")
    msg_sender.send.assert_not_called()


def test_send_quit_when_logged_in(sut_logged_in, msg_sender):
    sut_logged_in.quit()
    msg_sender.send.assert_called_once_with(Quit())


@pytest.fixture
def sut_finish(sut_logged_in, msg_sender):
    sut_logged_in.quit()
    msg_sender.send.reset_mock()
    return sut_logged_in


@pytest.fixture(params=["sut_start", "sut_login_sent", "sut_finish"])
def sut_not_logged_in(request):
    return request.getfixturevalue(request.param)


def test_not_send_msg_when_not_logged_in(sut_not_logged_in, msg_sender):
    sut_not_logged_in.send_msg("to_user", "message text")
    msg_sender.send.assert_not_called()


def test_not_join_when_not_logged_in(
    sut_not_logged_in, msg_sender, room_name_validator
):
    sut_not_logged_in.join_room("#room")
    room_name_validator.is_valid.assert_not_called()
    msg_sender.send.assert_not_called()


def test_not_leave_when_not_logged_in(
    sut_not_logged_in, msg_sender, room_name_validator
):
    sut_not_logged_in.leave_room("#room")
    room_name_validator.is_valid.assert_not_called()
    msg_sender.send.assert_not_called()


def test_not_quit_msg_when_not_logged_in(sut_not_logged_in, msg_sender):
    sut_not_logged_in.quit()
    msg_sender.send.assert_not_called()
