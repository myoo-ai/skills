"""Builds invoice totals from line items."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class Line:
    description: str
    quantity: int
    unit_price: Decimal


def total(lines: list[Line], vat_rate: Decimal = Decimal("0.21")) -> Decimal:
    """Return the invoice total including VAT, rounded to cents."""
    net = sum((line.unit_price * line.quantity for line in lines), Decimal(0))
    return (net * (1 + vat_rate)).quantize(Decimal("0.01"))
