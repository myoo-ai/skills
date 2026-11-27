import json
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from ledger import Invoice, LineItem, describe, load_invoices, paginate, totals_by_customer


class LedgerTest(unittest.TestCase):
    def test_invoice_total(self):
        invoice = Invoice(
            "INV-1",
            "acme.example.com",
            [LineItem("BOLT", 3, Decimal("0.25")), LineItem("NUT", 2, Decimal("0.10"))],
        )
        self.assertEqual(invoice.total(), Decimal("0.95"))

    def test_paginate(self):
        pages = paginate(list(range(5)), 2)
        self.assertEqual([p.items for p in pages], [[0, 1], [2, 3], [4]])
        self.assertEqual(pages[-1].number, 3)

    def test_describe(self):
        self.assertEqual(describe({"type": "payment", "amount": 10}), "payment of 10")
        self.assertEqual(describe({"type": "other"}), "unknown event")

    def test_load_and_total(self):
        with tempfile.TemporaryDirectory() as tmp:
            invoice = {
                "number": "INV-7",
                "customer": "shop.example.com",
                "issued": "2026-01-05T10:00:00+00:00",
                "items": [{"sku": "BOLT", "quantity": 4, "unit_price": "1.50"}],
            }
            Path(tmp, "inv-7.json").write_text(json.dumps(invoice), encoding="utf-8")
            invoices = load_invoices(tmp)
        self.assertEqual(totals_by_customer(invoices), {"shop.example.com": Decimal("6.00")})


if __name__ == "__main__":
    unittest.main()
