import re
from typing import Any

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.session import Session
from sqlalchemy.sql import and_, exists

from ..log import get_logger
from .tables import User
from .user_history_storage import UserHistoryStorage

_logger: Any = get_logger()


class InvalidName(ValueError):
    pass


class InvalidPassword(ValueError):
    pass


class UserExists(ValueError):
    pass


class UserNotFound(ValueError):
    pass


class UserStorage:
    def __init__(
        self, session: Session, user_history_storage: UserHistoryStorage
    ) -> None:
        self._session = session
        self._user_history_storage = user_history_storage

    def register_user(self, username: str, password: str) -> None:
        self._check_username(username)
        self._check_password_complexity(password)

        try:
            user = User(username=username, password=password)
            self._session.add(user)
            self._user_history_storage.add_register_record(user)
            self._session.commit()
            _logger.debug("User registered", username=username)
        except IntegrityError:
            raise UserExists()

    def credentials_valid(self, username: str, password: str) -> bool:
        stmt = exists().where(
            and_(User.username == username, User.password == password)
        )
        valid: bool = self._session.query(stmt).scalar()  # type: ignore
        if valid:
            _logger.debug("creds for user are valid", username=username)
        else:
            _logger.debug("creds for user are invalid", username=username)
        return valid

    def get_user_by_name(self, username: str) -> User:
        try:
            _logger.debug("Get user by name", username=username)
            return self._session.query(User).filter(User.username == username).one()
        except NoResultFound:
            raise UserNotFound(f"user with username={username}")

    @staticmethod
    def _check_username(username: str) -> None:
        if not username.isalnum():
            raise InvalidName("username must be alphanumeric")
        if len(username) < 4:
            raise InvalidName("username must be at least 4 chars length")

    @staticmethod
    def _check_password_complexity(password: str) -> None:
        if len(password) < 8:
            raise InvalidPassword("password must be at least 8 chars length")
        if re.search(r"\d", password) is None:
            raise InvalidPassword("password must contain at least one digit")
        if re.search(r"[A-Z]", password) is None:
            raise InvalidPassword("password must contain at least one uppercase letter")
        if re.search(r"[a-z]", password) is None:
            raise InvalidPassword("password must contain at least one lowercase letter")
        if re.search(r"[ !@#$%&'()*+,-./[\\\]^_`{|}~" + r'"]', password) is None:
            raise InvalidPassword("password must contain at least one special char")
