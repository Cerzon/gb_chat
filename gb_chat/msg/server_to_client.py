from dataclasses import dataclass
from http import HTTPStatus
from typing import Optional, Union


@dataclass(frozen=True)
class Response:
    code: HTTPStatus
    msg: str


@dataclass
class Probe:
    pass


@dataclass(frozen=True)
class ChatToClient:
    sender: str
    message: str
    room: Optional[str] = None


ServerToClientMessage = Union[Response, Probe, ChatToClient]
