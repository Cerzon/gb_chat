import threading


class Disconnector:
    def __init__(self) -> None:
        self._flag = threading.Event()

    def disconnect(self) -> None:
        self._flag.set()

    @property
    def should_disconnect(self) -> bool:
        return self._flag.is_set()
