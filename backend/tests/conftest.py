"""
CyberGuard SME - Test configuration using an isolated in-memory database.
Prevents test data from polluting the production cyberguard.db.
"""
import sys
import os
import sqlite3
import pytest

# Ensure backend module is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# --------------------------------------------------------------------------
# Override DATABASE_PATH to use in-memory DB for tests
# --------------------------------------------------------------------------
import database as db_module

# Patch the path to a temp file so tests don't touch production data
TEST_DB_PATH = os.path.join(os.path.dirname(__file__), "test_cyberguard.db")
db_module.DATABASE_PATH = TEST_DB_PATH


def pytest_sessionstart(session):
    """Initialize a clean test database at the beginning of the test session."""
    # Remove leftover test db from a previous failed run
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
    db_module.init_db()


def pytest_sessionfinish(session, exitstatus):
    """Remove test database after all tests have completed."""
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except Exception:
            pass
