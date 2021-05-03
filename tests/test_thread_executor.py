from unittest.mock import MagicMock

import pytest
from gb_chat.common.thread_executor import IoThreadExecutor, UiThreadExecutor
from PyQt5.QtWidgets import QApplication


@pytest.mark.parametrize("tasks", [[MagicMock()], [MagicMock(), MagicMock()]])
def test_io_thread_execute(tasks):
    sut = IoThreadExecutor()
    for task in tasks:
        sut.schedule(task)

    sut.execute_all()
    for task in tasks:
        task.assert_called_once()


@pytest.mark.parametrize("tasks", [[MagicMock()], [MagicMock(), MagicMock()]])
def test_ui_thread_execute(tasks, qapp):
    sut = UiThreadExecutor(qapp)
    for task in tasks:
        sut.schedule(task)

    qapp.sendPostedEvents(sut)

    for task in tasks:
        task.assert_called_once()
