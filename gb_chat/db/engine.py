import sqlite3
from typing import Any

from sqlalchemy import event
from sqlalchemy.engine import Engine, create_engine

from .tables import Base, User, UserHistory, contacts_association


def _fk_pragma_on_connect(dbapi_con: sqlite3.Connection, _: Any) -> None:
    dbapi_con.execute("pragma foreign_keys=ON")


def make_engine(url: str, **kwargs: Any) -> Engine:
    engine = create_engine(url, **kwargs)
    event.listen(engine, "connect", _fk_pragma_on_connect)  # type: ignore
    Base.metadata.create_all(
        engine, tables=(User.__table__, UserHistory.__table__, contacts_association)
    )
    return engine
