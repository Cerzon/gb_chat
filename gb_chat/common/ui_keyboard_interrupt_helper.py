"""
This solution is taken from https://coldfix.de/2016/11/08/pyqt-boilerplate/#keyboardinterrupt-ctrl-c
"""
import signal
from typing import Callable

from PyQt5.QtCore import QCoreApplication, QTimer


def _interrupt_handler(app: QCoreApplication) -> None:
    app.quit()


def _safe_timer(timeout: int, fun: Callable[[], None]) -> None:
    def timer_event() -> None:
        try:
            fun()
        finally:
            QTimer.singleShot(timeout, timer_event)

    QTimer.singleShot(timeout, timer_event)


def setup_interrupt_handling(app: QCoreApplication) -> None:
    signal.signal(signal.SIGINT, lambda *args: _interrupt_handler(app))
    _safe_timer(50, lambda: None)
