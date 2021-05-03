from queue import Empty, SimpleQueue
from typing import Any, Callable, Optional, cast

from PyQt5.QtCore import QEvent, QObject
from PyQt5.QtWidgets import QApplication

from ..log import get_logger

Function = Callable[[], None]


class IoThreadExecutor:
    def __init__(self) -> None:
        self._queue: SimpleQueue[Function] = SimpleQueue()
        self._logger: Any = get_logger("IoThreadExecutor")

    def schedule(self, fun: Function) -> None:
        self._queue.put(fun)
        self._logger.debug("Schedule task", qsize=self._queue.qsize())

    def execute_all(self) -> None:
        try:
            while True:
                fun = self._queue.get_nowait()
                self._logger.debug(
                    "Execute task",
                    qsize=self._queue.qsize(),
                )
                fun()
        except Empty:
            return


class _FunctionEvent(QEvent):
    EVENT_TYPE: QEvent.Type = QEvent.Type.User

    def __init__(self, fun: Function) -> None:
        super().__init__(self.EVENT_TYPE)
        self.fun = fun


class UiThreadExecutor(QObject):
    def __init__(self, app: QApplication) -> None:
        super().__init__(parent=None)
        self._app = app
        self._logger: Any = get_logger("UiThreadExecutor")

    def schedule(self, fun: Function) -> None:
        self._logger.debug("Schedule task")
        self._app.postEvent(self, _FunctionEvent(fun))

    def event(self, e: QEvent) -> bool:
        if e.type() != _FunctionEvent.EVENT_TYPE:
            return super().event(e)

        fun_event = cast(_FunctionEvent, e)
        self._logger.debug("Execute task")
        fun_event.fun()
        return True
