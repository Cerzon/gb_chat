from contextlib import closing
from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest
from gb_chat.db.engine import make_engine
from PyQt5.QtWidgets import QApplication
from sqlalchemy.orm import sessionmaker

TIME_FACTORY_TIMESTAMP = 1619857471.0
TIME_FACTORY_DATETIME = datetime.fromtimestamp(TIME_FACTORY_TIMESTAMP, timezone.utc)
VALID_USERNAME = "user"
VALID_PASSWORD = "P@ssw0rd"


@pytest.fixture
def time_factory():
    return MagicMock(return_value=TIME_FACTORY_DATETIME)


@pytest.fixture
def session():
    engine = make_engine("sqlite:///:memory:")
    with closing(sessionmaker(engine)()) as s:
        yield s


@pytest.fixture
def qapp():
    return QApplication([])
