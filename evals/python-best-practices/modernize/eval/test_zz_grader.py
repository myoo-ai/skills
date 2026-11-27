import json
import tempfile
import unittest
from datetime import timedelta
from decimal import Decimal
from pathlib import Path

from ledger import Invoice, LineItem, Page, describe, first, load_invoices, paginate, parse_amount


class GraderTest(unittest.TestCase):
    def test_behavior(self):
        inv = Invoice("INV-2", "acme.example.com")
        self.assertEqual(inv.items, [])
        self.assertEqual(inv.issued.utcoffset(), timedelta(0))
        self.assertIsNot(Invoice("A", "b").items, Invoice("C", "d").items)
        self.assertEqual(LineItem("A", 1, Decimal("2")), LineItem("A", 1, Decimal("2")))
        self.assertEqual(LineItem("A", 3, Decimal("2")).total(), Decimal("6"))
        pages = paginate(["a", "b", "c"], 2)
        self.assertEqual([(p.items, p.number, p.size) for p in pages], [(["a", "b"], 1, 2), (["c"], 2, 2)])
        self.assertEqual(Page([1], 1, 5).items, [1])
        with self.assertRaises(ValueError):
            paginate([1], 0)
        self.assertIsNone(first([]))
        self.assertEqual(first([], 5), 5)
        self.assertEqual(first(iter([7, 8])), 7)
        self.assertEqual(parse_amount("12.00"), 12)
        self.assertIsInstance(parse_amount("12.00"), int)
        self.assertEqual(parse_amount(" 1.5 "), Decimal("1.5"))
        self.assertEqual(parse_amount(2.5), Decimal("2.5"))
        self.assertEqual(parse_amount(3), 3)
        self.assertEqual(describe({"type": "payment", "amount": 5}), "payment of 5")
        self.assertEqual(describe({"type": "refund", "amount": 2, "reason": "damaged"}), "refund of 2 (damaged)")
        self.assertEqual(describe({"type": "refund", "amount": 2}), "unknown event")
        self.assertEqual(describe({"type": "note", "text": "hi"}), "note: hi")
        self.assertEqual(describe({"type": "note", "text": 3}), "unknown event")
        self.assertEqual(describe({}), "unknown event")
        with tempfile.TemporaryDirectory() as tmp:
            for n in (2, 1):
                doc = {"number": f"INV-{n}", "customer": "c.example.com", "items": [{"sku": "X", "quantity": n, "unit_price": "1.10"}]}
                Path(tmp, f"inv-{n}.json").write_text(json.dumps(doc), encoding="utf-8")
            Path(tmp, "notes.txt").write_text("skip me", encoding="utf-8")
            for arg in (tmp, Path(tmp)):
                invoices = load_invoices(arg)
                self.assertEqual([i.number for i in invoices], ["INV-1", "INV-2"])
                self.assertEqual(invoices[1].total(), Decimal("2.20"))
                self.assertEqual(invoices[0].issued.utcoffset(), timedelta(0))
