from typing import Any, List

from sqlalchemy.orm.session import Session

from ..common.types import TimeFactory
from ..log import get_logger
from .tables import User, UserHistory, UserHistoryEventEnum

_logger: Any = get_logger()


class UserHistoryStorage:
    def __init__(self, session: Session, time_factory: TimeFactory) -> None:
        self._session = session
        self._time_factory = time_factory

    def all(self) -> List[UserHistory]:
        _logger.debug("Fetch all user history")
        return self._session.query(UserHistory).all()

    def add_register_record(self, user: User) -> None:
        self._add_record(user, UserHistoryEventEnum.REGISTER)

    def add_login_record(self, user: User) -> None:
        self._add_record(user, UserHistoryEventEnum.LOGIN)

    def add_logout_record(self, user: User) -> None:
        self._add_record(user, UserHistoryEventEnum.LOGOUT)

    def _add_record(self, user: User, event: UserHistoryEventEnum) -> None:
        user.history.append(UserHistory(event=event, time=self._time_factory()))
        self._session.commit()
        _logger.debug(f"Add {event.name.lower()} record", user=user.username)
