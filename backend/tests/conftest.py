import os
import tempfile
import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.db.connection import initialize_database
from app.main import app


@pytest.fixture(scope="session")
def test_db():
    """
    Creates an isolated temporary SQLite database for test execution.
    Guarantees production database is never modified during tests.
    """
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        test_db_path = tmp.name

    # Point settings to test DB
    original_db_path = settings.DATABASE_PATH
    settings.DATABASE_PATH = test_db_path

    # Initialize schema and seed data
    initialize_database(test_db_path)

    yield test_db_path

    # Teardown
    settings.DATABASE_PATH = original_db_path
    if os.path.exists(test_db_path):
        try:
            os.remove(test_db_path)
        except OSError:
            pass


@pytest.fixture
def client(test_db):
    """TestClient configured with the isolated test database."""
    with TestClient(app) as test_client:
        yield test_client
