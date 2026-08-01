"""Test fixtures.

FLIGHTS_DB_PATH is set before `app` is imported anywhere, so the suite builds
and seeds its own throwaway database and never touches the working flights.db.
"""

import os
import tempfile
from pathlib import Path

import pytest

TMP_DB = Path(tempfile.gettempdir()) / "flights-test.db"
TMP_DB.unlink(missing_ok=True)
os.environ["FLIGHTS_DB_PATH"] = str(TMP_DB)

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


@pytest.fixture(scope="session")
def client():
    """A client over a freshly seeded database.

    Entering the context manager runs the app's lifespan, which is what creates
    the tables and seeds them — the same code path production uses on a cold
    start, rather than a test-only substitute.
    """
    with TestClient(app) as c:
        yield c
    TMP_DB.unlink(missing_ok=True)


@pytest.fixture(scope="session")
def today():
    from datetime import date

    return date.today().isoformat()
