from unittest.mock import MagicMock

import pytest
from gb_chat.db.contact_storage import ContactError, ContactStorage
from gb_chat.db.tables import User
from gb_chat.db.user_history_storage import UserHistoryStorage
from gb_chat.db.user_storage import UserStorage

from conftest import VALID_PASSWORD, VALID_USERNAME


@pytest.fixture
def sut(session):
    return ContactStorage(session)


@pytest.fixture
def user_storage(session):
    user_history_storage = MagicMock(spec_set=UserHistoryStorage)
    return UserStorage(session, user_history_storage)


@pytest.fixture
def owner(session, user_storage):
    name = VALID_USERNAME + "owner"
    user_storage.register_user(name, VALID_PASSWORD)

    return user_storage.get_user_by_name(name)


@pytest.fixture
def contact(session, user_storage):
    name = VALID_USERNAME + "contact"
    user_storage.register_user(name, VALID_PASSWORD)

    return user_storage.get_user_by_name(name)


def test_add_contacts_raises_when_add_self(sut, owner):
    with pytest.raises(ContactError):
        sut.add_contact(owner, owner)


def test_add_contacts(sut, owner, contact):
    sut.add_contact(owner, contact)
    assert sut.get_user_contacts(owner) == [contact]


def test_add_contacts_idempotent(sut, owner, contact):
    sut.add_contact(owner, contact)
    sut.add_contact(owner, contact)
    assert sut.get_user_contacts(owner) == [contact]


def test_remove_contact_not_raise_when_not_in_contacts(sut, owner, contact):
    sut.remove_contact(owner, contact)
    assert sut.get_user_contacts(owner) == []


def test_remove_contact(sut, owner, contact):
    sut.add_contact(owner, contact)
    sut.remove_contact(owner, contact)
    assert sut.get_user_contacts(owner) == []
