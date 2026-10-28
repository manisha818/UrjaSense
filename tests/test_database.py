
from backend.app.db.session import Base, engine
from backend.app.db import models


def test_database_tables_exist():
    assert "devices" in Base.metadata.tables
    assert "readings" in Base.metadata.tables


def test_database_connection():
    with engine.connect() as connection:
        assert connection is not None
