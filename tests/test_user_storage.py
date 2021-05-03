from unittest.mock import MagicMock

import pytest
from gb_chat.db.user_history_storage import UserHistoryStorage
from gb_chat.db.user_storage import (InvalidName, InvalidPassword, UserExists,
                                     UserNotFound, UserStorage)

from conftest import VALID_PASSWORD, VALID_USERNAME


@pytest.fixture
def user_history_storage():
    return MagicMock(spec_set=UserHistoryStorage)


@pytest.fixture
def sut(session, user_history_storage):
    return UserStorage(session, user_history_storage)


@pytest.mark.parametrize("username", ["", " ", "user 1", "usr"])
def test_registers_user_raises_when_username_invalid(username, sut):
    with pytest.raises(InvalidName):
        sut.register_user(username, VALID_PASSWORD)


@pytest.mark.parametrize("password", ["", "qwerty", "password", "passw0rd", "Passw0rd"])
def test_registers_user_raises_when_password_invalid(password, sut):
    with pytest.raises(InvalidPassword):
        sut.register_user(VALID_USERNAME, password)


def test_registers_user_adds_register_record(sut, user_history_storage):
    sut.register_user(VALID_USERNAME, VALID_PASSWORD)
    user_history_storage.add_register_record.assert_called_once()
    call = user_history_storage.add_register_record.mock_calls[0]
    user = call.args[0]
    assert user.username == VALID_USERNAME
    assert user.password == VALID_PASSWORD


@pytest.fixture
def sut_with_user(sut):
    sut.register_user(VALID_USERNAME, VALID_PASSWORD)
    return sut


def test_registers_user_raises_when_same_name(sut_with_user):
    with pytest.raises(UserExists):
        sut_with_user.register_user(VALID_USERNAME, "P@ssw0rd111")


@pytest.mark.parametrize(
    "username,password", [(VALID_USERNAME, "pass"), ("user1", VALID_PASSWORD)]
)
def test_credentials_invalid(username, password, sut_with_user):
    assert not sut_with_user.credentials_valid(username, password)


def test_get_user_raises_when_no_user_found(sut):
    with pytest.raises(UserNotFound):
        sut.get_user_by_name("aaaa")


def test_get_user_raises_when_no_user_found(sut_with_user):
    user = sut_with_user.get_user_by_name(VALID_USERNAME)
    assert user.username == VALID_USERNAME
    assert user.password == VALID_PASSWORD
