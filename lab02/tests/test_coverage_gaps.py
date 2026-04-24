"""
Part 4 — Coverage gap fill tests.

Focused tests for standalone helpers in order_processor.py that are not
fully exercised by earlier parts.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from order_processor import (
    NOTIFICATION_URL,
    PAYMENT_API_URL,
    charge_customer,
    get_db_connection,
    load_order,
    notify_customer,
    save_order,
)


def test_get_db_connection_uses_sqlite_connect():
    with patch("order_processor.sqlite3.connect") as mock_connect:
        fake_conn = MagicMock()
        mock_connect.return_value = fake_conn

        conn = get_db_connection("custom.db")

        assert conn is fake_conn
        mock_connect.assert_called_once_with("custom.db")


def test_save_order_internal_connection_is_closed(make_order):
    order = make_order()
    mock_conn = MagicMock()

    with patch("order_processor.get_db_connection", return_value=mock_conn):
        assert save_order(order) is True

    mock_conn.close.assert_called_once()


def test_load_order_returns_none_and_closes_internal_connection():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None
    mock_conn.cursor.return_value = mock_cursor

    with patch("order_processor.get_db_connection", return_value=mock_conn):
        result = load_order("MISSING")

    assert result is None
    mock_conn.close.assert_called_once()


def test_load_order_returns_row_dict_and_closes_internal_connection():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = ("ORD-9", "x@example.com", 42.0, "2026-01-01T00:00:00")
    mock_conn.cursor.return_value = mock_cursor

    with patch("order_processor.get_db_connection", return_value=mock_conn):
        result = load_order("ORD-9")

    assert result == {
        "order_id": "ORD-9",
        "customer_email": "x@example.com",
        "total": 42.0,
        "created_at": "2026-01-01T00:00:00",
    }
    mock_conn.close.assert_called_once()


@patch("order_processor.requests.post")
def test_charge_customer_posts_expected_payload(mock_post, make_order):
    order = make_order(discount_pct=10)
    mock_response = MagicMock()
    mock_response.json.return_value = {"id": "PAY-999"}
    mock_post.return_value = mock_response

    result = charge_customer(order, "tok_abc")

    assert result == {"id": "PAY-999"}
    mock_post.assert_called_once_with(
        f"{PAYMENT_API_URL}/v1/charge",
        json={
            "amount": 1800,
            "currency": "GBP",
            "card_token": "tok_abc",
            "reference": "ORD-001",
            "customer": "test@example.com",
        },
        timeout=10,
    )


@pytest.mark.asyncio
async def test_notify_customer_creates_and_closes_own_session(make_order):
    order = make_order()
    mock_session = MagicMock()
    mock_session.close = AsyncMock()
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_context_manager = AsyncMock()
    mock_context_manager.__aenter__.return_value = mock_response
    mock_session.post.return_value = mock_context_manager

    with patch("order_processor.aiohttp.ClientSession", return_value=mock_session):
        result = await notify_customer(order, "Hi")

    assert result is True
    mock_session.post.assert_called_once_with(
        f"{NOTIFICATION_URL}/send",
        json={"to": "test@example.com", "body": "Hi", "ref": "ORD-001"},
    )
    mock_session.close.assert_awaited_once()
