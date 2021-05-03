from typing import Any, List

from sqlalchemy.orm.session import Session

from ..log import get_logger
from .tables import User

_logger: Any = get_logger()


class ContactError(ValueError):
    pass


class ContactStorage:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add_contact(self, owner: User, contact: User) -> None:
        if owner is contact:
            raise ContactError("Can't add self to contacts")

        if contact in owner.contacts:
            _logger.debug(
                "User already in contacts",
                owner=owner.username,
                contact=contact.username,
            )
            return

        owner.contacts.append(contact)
        self._session.commit()
        _logger.debug(
            "User added to contacts",
            owner=owner.username,
            contact=contact.username,
        )

    def remove_contact(self, owner: User, contact: User) -> None:
        try:
            owner.contacts.remove(contact)
        except ValueError:
            return

        self._session.commit()
        _logger.debug(
            "User removed from contacts",
            owner=owner.username,
            contact=contact.username,
        )

    def get_user_contacts(self, owner: User) -> List[User]:
        _logger.debug(
            "Get user contacts",
            owner=owner.username,
        )
        return owner.contacts
