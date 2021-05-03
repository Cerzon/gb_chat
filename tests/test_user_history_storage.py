from contextlib import closing
from datetime import tzinfo

import pytest
from gb_chat.db.user_history_storage import (UserHistoryEventEnum,
                                             UserHistoryStorage)
from gb_chat.db.user_storage import User, UserStorage

from conftest import TIME_FACTORY_DATETIME, VALID_PASSWORD, VALID_USERNAME


@pytest.fixture
def sut(session, time_factory):
    return UserHistoryStorage(session, time_factory)


def test_all_returns_nothing(sut):
    assert sut.all() == []


@pytest.fixture
def user(session, sut):
    user_storage = UserStorage(session, sut)
    user_storage.register_user(VALID_USERNAME, VALID_PASSWORD)

    return user_storage.get_user_by_name(VALID_USERNAME)


def compare_history(history, event, time, user):
    assert history.event == event
    assert history.time == time.replace(tzinfo=None)
    assert history.user == user


def test_add_register_record(sut, user):
    all = sut.all()
    assert len(all) == 1
    compare_history(all[0], UserHistoryEventEnum.REGISTER, TIME_FACTORY_DATETIME, user)


def test_add_login_record(sut, user):
    sut.add_login_record(user)

    all = sut.all()
    assert len(all) == 2
    compare_history(all[1], UserHistoryEventEnum.LOGIN, TIME_FACTORY_DATETIME, user)


def test_add_logout_record(sut, user):
    sut.add_logout_record(user)

    all = sut.all()
    assert len(all) == 2
    compare_history(all[1], UserHistoryEventEnum.LOGOUT, TIME_FACTORY_DATETIME, user)
