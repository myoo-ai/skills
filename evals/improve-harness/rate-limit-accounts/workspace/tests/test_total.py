from decimal import Decimal

from invoicer import Line, total


def test_total_includes_vat() -> None:
    lines = [Line("hosting", 2, Decimal("10.00")), Line("domain", 1, Decimal("5.00"))]
    assert total(lines) == Decimal("30.25")
