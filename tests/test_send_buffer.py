import pytest
from gb_chat.io.send_buffer import SendBuffer


@pytest.fixture
def sut():
    return SendBuffer()


def test_empty_contains_no_data(sut):
    assert sut.data == b""


def test_send_appends_data(sut):
    sut.send(b"abc")
    assert sut.data == b"abc"
    sut.send(b"def")
    assert sut.data == b"abcdef"


def test_bytes_sent_removes_bytes_from_beginning(sut):
    sut.send(b"abc")
    sut.bytes_sent(1)
    assert sut.data == b"bc"
    sut.bytes_sent(2)
    assert sut.data == b""


def test_raises_when_bytes_sent_more_than_contain(sut):
    sut.send(b"abc")
    with pytest.raises(ValueError):
        sut.bytes_sent(4)
