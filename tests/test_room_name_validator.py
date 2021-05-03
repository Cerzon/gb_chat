import pytest
from gb_chat.common.room_name_validator import RoomNameValidator


@pytest.fixture
def sut():
    return RoomNameValidator()


@pytest.mark.parametrize("name", ["#room", "#room_name", "#room-name", "#R@0m"])
def test_valid_room_name(name, sut):
    assert sut.is_valid(name)


@pytest.mark.parametrize("name", ["room", "#room name", "#room#name"])
def test_invalid_room_name(name, sut):
    assert not sut.is_valid(name)
