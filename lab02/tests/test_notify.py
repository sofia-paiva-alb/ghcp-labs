"""
Part 3 — Async Testing with AsyncMock (15 min)
================================================
Goal: Test the async notify_customer() function using AsyncMock
and pytest-asyncio.

Key concepts:
  - AsyncMock (from unittest.mock, Python 3.8+)
  - Mocking async context managers (the `async with session.post(...)` pattern)
  - assert_awaited_once_with() instead of assert_called_once_with()

Hints (try on your own first!):
  - Mock the context manager response:
      mock_session.post.return_value.__aenter__.return_value.status = 200
  - Use @pytest.mark.asyncio on each test
  - Use assert_awaited_once_with() for async verification
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from order_processor import Order, OrderItem, notify_customer


def make_test_order():
    return Order(
        order_id="ORD-001",
        customer_email="test@example.com",
        items=[OrderItem("PROD-1", "Widget", 1, 10.00)],
    )


class TestNotifyCustomer:

    @pytest.mark.asyncio
    async def test_successful_notification(self):
        # TODO:
        # 1. Create a mock session (AsyncMock)
        # 2. Set mock_session.post.return_value.__aenter__.return_value.status = 200
        # 3. Call await notify_customer(order, "Your order is confirmed!", session=mock_session)
        # 4. Assert result is True
        # 5. Assert mock_session.post was awaited once with correct URL and JSON
        pass

    @pytest.mark.asyncio
    async def test_failed_notification_non_200(self):
        # TODO:
        # 1. Same setup but set status = 500
        # 2. Assert result is False
        pass

    @pytest.mark.asyncio
    async def test_network_error_returns_false(self):
        # TODO:
        # 1. Make mock_session.post.side_effect = aiohttp.ClientError()
        # 2. Assert result is False
        pass
