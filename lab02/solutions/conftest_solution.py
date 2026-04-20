"""
SOLUTION — conftest.py with shared factory fixture
====================================================
"""

import sqlite3
import pytest
from order_processor import Order, OrderItem


@pytest.fixture
def make_order():
    """Factory fixture — returns a function that creates an Order with sensible defaults."""
    def _factory(**overrides):
        defaults = dict(
            order_id="ORD-001",
            customer_email="test@example.com",
            items=[OrderItem("PROD-1", "Widget", 2, 10.00)],
            discount_pct=0.0,
        )
        defaults.update(overrides)
        return Order(**defaults)
    return _factory


@pytest.fixture
def db_conn():
    """Yields an in-memory SQLite connection with the orders table, auto-closes."""
    conn = sqlite3.connect(":memory:")
    conn.execute(
        "CREATE TABLE orders "
        "(order_id TEXT PRIMARY KEY, customer_email TEXT, total REAL, created_at TEXT)"
    )
    yield conn
    conn.close()
