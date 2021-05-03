from enum import Enum, auto


class AutoName(Enum):
    def _generate_next_value_(name: str, start, count, last_values):  # type: ignore
        return name.lower()


class Status(AutoName):
    ONLINE = auto()
    AWAY = auto()
