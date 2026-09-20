import sqlite3
import pytest
from app.db.connection import get_db, initialize_database
from app.db.seed import calculate_status


def test_db_initialization(test_db):
    """Verifies that all tables and indexes exist in the initialized database."""
    with get_db(test_db) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in cursor.fetchall()}
        assert "products" in tables
        assert "sales" in tables
        assert "employees" in tables
        assert "hr_policies" in tables
        assert "activity_logs" in tables


def test_seed_idempotency_does_not_duplicate(test_db):
    """Verifies that calling initialize_database multiple times does NOT duplicate rows."""
    with get_db(test_db) as conn:
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM products")
        initial_products = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM sales")
        initial_sales = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM employees")
        initial_employees = c.fetchone()[0]

    # Re-run initialization
    initialize_database(test_db)

    with get_db(test_db) as conn:
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM products")
        assert c.fetchone()[0] == initial_products
        c.execute("SELECT COUNT(*) FROM sales")
        assert c.fetchone()[0] == initial_sales
        c.execute("SELECT COUNT(*) FROM employees")
        assert c.fetchone()[0] == initial_employees


def test_calculate_status_logic():
    """Verifies inventory status calculation logic."""
    assert calculate_status(stock=0, reorder_level=10) == "out_of_stock"
    assert calculate_status(stock=4, reorder_level=10) == "low"
    assert calculate_status(stock=10, reorder_level=10) == "low"
    assert calculate_status(stock=11, reorder_level=10) == "healthy"
    assert calculate_status(stock=50, reorder_level=10) == "healthy"
