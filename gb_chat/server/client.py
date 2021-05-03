from dataclasses import dataclass
from typing import Optional

from ..common.disconnector import Disconnector
from ..io.message_sender import MessageSender


@dataclass
class Client:
    msg_sender: MessageSender
    disconnector: Disconnector

    name: Optional[str] = None

    def __hash__(self) -> int:
        return hash(self.msg_sender)
