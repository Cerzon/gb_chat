import re


class RoomNameValidator:
    def __init__(self) -> None:
        self._re = re.compile(r"^#[\w\-@]+$", re.ASCII)

    def is_valid(self, name: str) -> bool:
        return self._re.match(name) is not None
