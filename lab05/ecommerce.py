"""
Lab 5 — Agents
================
A multi-service e-commerce backend. Participants use Copilot agents
(including HVE Core agents) to research, plan, and implement features.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


# ── Enums ────────────────────────────────────────────────────────────

class OrderStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class PaymentMethod(Enum):
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    PAYPAL = "paypal"
    BANK_TRANSFER = "bank_transfer"


# ── Models ───────────────────────────────────────────────────────────

@dataclass
class Address:
    street: str
    city: str
    state: str
    zip_code: str
    country: str = "US"


@dataclass
class Customer:
    customer_id: str
    name: str
    email: str
    address: Optional[Address] = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class CartItem:
    product_id: str
    name: str
    quantity: int
    unit_price: float

    @property
    def total(self) -> float:
        return self.quantity * self.unit_price


@dataclass
class ShoppingCart:
    customer_id: str
    items: list[CartItem] = field(default_factory=list)

    def add_item(self, item: CartItem) -> None:
        for existing in self.items:
            if existing.product_id == item.product_id:
                existing.quantity += item.quantity
                return
        self.items.append(item)

    def remove_item(self, product_id: str) -> bool:
        for i, item in enumerate(self.items):
            if item.product_id == product_id:
                self.items.pop(i)
                return True
        return False

    @property
    def subtotal(self) -> float:
        return sum(item.total for item in self.items)

    @property
    def item_count(self) -> int:
        return sum(item.quantity for item in self.items)


@dataclass
class EcomOrder:
    order_id: str
    customer: Customer
    items: list[CartItem]
    status: OrderStatus = OrderStatus.PENDING
    payment_method: Optional[PaymentMethod] = None
    shipping_address: Optional[Address] = None
    created_at: datetime = field(default_factory=datetime.now)
    notes: str = ""

    @property
    def subtotal(self) -> float:
        return sum(item.total for item in self.items)

    def calculate_shipping(self) -> float:
        """Flat rate + per-item fee."""
        if self.subtotal > 100:
            return 0.0  # free shipping over $100
        return 5.99 + (1.50 * sum(item.quantity for item in self.items))

    def calculate_tax(self, rate: float = 0.08) -> float:
        return round(self.subtotal * rate, 2)

    @property
    def total(self) -> float:
        return self.subtotal + self.calculate_shipping() + self.calculate_tax()

    def cancel(self) -> bool:
        if self.status in (OrderStatus.PENDING, OrderStatus.CONFIRMED):
            self.status = OrderStatus.CANCELLED
            return True
        return False

    def advance_status(self) -> bool:
        transitions = {
            OrderStatus.PENDING: OrderStatus.CONFIRMED,
            OrderStatus.CONFIRMED: OrderStatus.SHIPPED,
            OrderStatus.SHIPPED: OrderStatus.DELIVERED,
        }
        next_status = transitions.get(self.status)
        if next_status:
            self.status = next_status
            return True
        return False


# ── Services ─────────────────────────────────────────────────────────

class OrderService:
    """Manages order lifecycle."""

    def __init__(self):
        self._orders: dict[str, EcomOrder] = {}
        self._next_id = 1

    def create_order(self, customer: Customer, cart: ShoppingCart,
                     payment_method: PaymentMethod,
                     shipping_address: Optional[Address] = None) -> EcomOrder:
        if not cart.items:
            raise ValueError("Cannot create order with empty cart")

        order_id = f"ORD-{self._next_id:06d}"
        self._next_id += 1

        order = EcomOrder(
            order_id=order_id,
            customer=customer,
            items=list(cart.items),
            payment_method=payment_method,
            shipping_address=shipping_address or customer.address,
        )
        self._orders[order_id] = order
        return order

    def get_order(self, order_id: str) -> Optional[EcomOrder]:
        return self._orders.get(order_id)

    def get_customer_orders(self, customer_id: str) -> list[EcomOrder]:
        return [o for o in self._orders.values() if o.customer.customer_id == customer_id]

    def cancel_order(self, order_id: str) -> bool:
        order = self.get_order(order_id)
        if order is None:
            return False
        return order.cancel()

    def get_order_summary(self) -> dict:
        total_orders = len(self._orders)
        by_status = {}
        total_revenue = 0.0
        for order in self._orders.values():
            status = order.status.value
            by_status[status] = by_status.get(status, 0) + 1
            if order.status != OrderStatus.CANCELLED:
                total_revenue += order.total
        return {
            "total_orders": total_orders,
            "by_status": by_status,
            "total_revenue": round(total_revenue, 2),
        }
