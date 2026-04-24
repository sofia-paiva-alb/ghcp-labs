"""
Part 1 — Mocking HTTP & DB (10 min)
====================================
Goal: Test all 5 code paths in process_order() by mocking the payment
API (requests.post) and using an in-memory SQLite database.

Code paths to cover:
  1. Invalid order         → {"status": "invalid", "errors": [...]}
  2. DB save failure       → {"status": "error", ...}
  3. Payment succeeds      → {"status": "ok", ...}
  4. Payment HTTP error    → {"status": "payment_failed", ...}
  5. Payment timeout       → {"status": "payment_timeout"}

Hints (try on your own first!):
  - Patch at the import location: @patch("order_processor.requests.post")
  - For raise_for_status on 402: mock_resp.raise_for_status.side_effect = requests.HTTPError("402")
  - For timeout: mock_post.side_effect = requests.Timeout()
"""

import pytest
import sqlite3
from unittest.mock import patch, MagicMock
import requests
from order_processor import Order, OrderItem, process_order


# ── Helpers ──────────────────────────────────────────────────────────

def make_test_order(**overrides):
    """Create a valid Order. Pass keyword args to override defaults."""
    defaults = dict(
        order_id="ORD-001",
        customer_email="test@example.com",
        items=[OrderItem("PROD-1", "Widget", 2, 10.00)],
    )
    defaults.update(overrides)
    return Order(**defaults)


def setup_db():
    """Return an in-memory SQLite connection with the orders table."""
    conn = sqlite3.connect(":memory:")
    conn.execute(
        "CREATE TABLE orders "
        "(order_id TEXT PRIMARY KEY, customer_email TEXT, total REAL, created_at TEXT)"
    )
    return conn


# ── Tests — fill in each method ──────────────────────────────────────

class TestProcessOrder:

    # Path 1: invalid order
    def test_invalid_order_returns_errors(self):
        order = make_test_order(items=[])

        result = process_order(order, card_token="tok_test")

        assert result["status"] == "invalid"
        assert "errors" in result
        assert "order must contain at least one item" in result["errors"]

    # Path 2: DB save failure
    @patch("order_processor.requests.post")
    def test_db_save_failure(self, mock_post):
        order = make_test_order()
        conn = sqlite3.connect(":memory:")  # Intentionally no orders table.

        result = process_order(order, card_token="tok_test", conn=conn)

        assert result["status"] == "error"
        assert result["message"] == "Failed to save order"
        mock_post.assert_not_called()

    # Path 3: successful payment
    @patch("order_processor.requests.post")
    def test_successful_payment(self, mock_post):
        order = make_test_order()
        conn = setup_db()
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"id": "PAY-123"}
        mock_post.return_value = mock_resp

        result = process_order(order, card_token="tok_test", conn=conn)

        assert result["status"] == "ok"
        assert result["payment_id"] == "PAY-123"
        assert result["total"] == pytest.approx(20.0)

    # Path 4: payment HTTP error (e.g. 402 Payment Required)
    @patch("order_processor.requests.post")
    def test_payment_http_error(self, mock_post):
        order = make_test_order()
        conn = setup_db()
        mock_resp = MagicMock()
        mock_resp.raise_for_status.side_effect = requests.HTTPError("402")
        mock_post.return_value = mock_resp

        result = process_order(order, card_token="tok_test", conn=conn)

        assert result["status"] == "payment_failed"
        assert "402" in result["message"]

    # Path 5: payment timeout
    @patch("order_processor.requests.post")
    def test_payment_timeout(self, mock_post):
        order = make_test_order()
        conn = setup_db()
        mock_post.side_effect = requests.Timeout()

        result = process_order(order, card_token="tok_test", conn=conn)

        assert result["status"] == "payment_timeout"
