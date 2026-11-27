"""Core ledger types and helpers."""

from __future__ import annotations

import json
import os
from datetime import datetime
from decimal import Decimal
from typing import Dict, Generic, Iterable, List, Optional, TypeVar, Union

from typing import TypeAlias

Amount: TypeAlias = Union[int, Decimal]

T = TypeVar("T")


class LineItem:
    """One line of an invoice."""

    def __init__(self, sku: str, quantity: int, unit_price: Decimal) -> None:
        self.sku = sku
        self.quantity = quantity
        self.unit_price = unit_price

    def __repr__(self) -> str:
        return "LineItem(sku=%r, quantity=%r, unit_price=%r)" % (
            self.sku,
            self.quantity,
            self.unit_price,
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, LineItem):
            return NotImplemented
        return (self.sku, self.quantity, self.unit_price) == (
            other.sku,
            other.quantity,
            other.unit_price,
        )

    def total(self) -> Decimal:
        return self.unit_price * self.quantity


class Invoice:
    """An invoice for one customer."""

    def __init__(
        self,
        number: str,
        customer: str,
        items: Optional[List[LineItem]] = None,
        issued: Optional[datetime] = None,
    ) -> None:
        self.number = number
        self.customer = customer
        self.items = items if items is not None else []
        self.issued = issued or datetime.utcnow()

    def __repr__(self) -> str:
        return "Invoice(number=%r, customer=%r, items=%r, issued=%r)" % (
            self.number,
            self.customer,
            self.items,
            self.issued,
        )

    def total(self) -> Decimal:
        return sum((item.total() for item in self.items), Decimal(0))


class Page(Generic[T]):
    """One page of a paginated result."""

    def __init__(self, items: List[T], number: int, size: int) -> None:
        self.items = items
        self.number = number
        self.size = size

    def __repr__(self) -> str:
        return "Page(items=%r, number=%r, size=%r)" % (self.items, self.number, self.size)


def paginate(items: List[T], size: int) -> List["Page[T]"]:
    """Split items into pages of at most size items, numbered from 1."""
    if size < 1:
        raise ValueError("size must be positive")
    pages = []
    for start in range(0, len(items), size):
        pages.append(Page(items[start : start + size], start // size + 1, size))
    return pages


def first(items: Iterable[T], default: Optional[T] = None) -> Optional[T]:
    """Return the first item, or default when items is empty."""
    for item in items:
        return item
    return default


def parse_amount(value: Union[str, int, float]) -> Amount:
    """Parse a money amount, keeping whole numbers as int."""
    if isinstance(value, float):
        value = repr(value)
    if isinstance(value, str):
        amount = Decimal(value.strip())
        if amount == amount.to_integral_value():
            return int(amount)
        return amount
    return value


def describe(event: Dict[str, object]) -> str:
    """Describe a ledger event for the audit log."""
    if event.get("type") == "payment" and "amount" in event:
        return "payment of %s" % event["amount"]
    elif event.get("type") == "refund" and "amount" in event and "reason" in event:
        return "refund of %s (%s)" % (event["amount"], event["reason"])
    elif event.get("type") == "note" and isinstance(event.get("text"), str):
        return "note: %s" % event["text"]
    else:
        return "unknown event"


def load_invoices(directory: Union[str, "os.PathLike[str]"]) -> List[Invoice]:
    """Load every *.json invoice in directory, ordered by file name."""
    result = []
    for name in sorted(os.listdir(directory)):
        if not name.endswith(".json"):
            continue
        f = open(os.path.join(directory, name))
        data = json.load(f)
        f.close()
        items = [
            LineItem(i["sku"], int(i["quantity"]), Decimal(i["unit_price"]))
            for i in data.get("items", [])
        ]
        issued = datetime.fromisoformat(data["issued"]) if "issued" in data else None
        result.append(Invoice(data["number"], data["customer"], items, issued))
    return result


def totals_by_customer(invoices: Iterable[Invoice]) -> Dict[str, Decimal]:
    """Sum invoice totals per customer."""
    totals: Dict[str, Decimal] = {}
    for invoice in invoices:
        totals[invoice.customer] = totals.get(invoice.customer, Decimal(0)) + invoice.total()
    return totals
