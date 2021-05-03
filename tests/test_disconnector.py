import pytest
from gb_chat.common.disconnector import Disconnector


@pytest.fixture
def sut():
    return Disconnector()


def test_should_not_disconnect_after_init(sut):
    assert sut.should_disconnect == False


def test_should_disconnect_after_disconnect_called(sut):
    sut.disconnect()
    assert sut.should_disconnect == True
