import tempfile
import unittest
from pathlib import Path

from dupfind import find_duplicates


class FinderTest(unittest.TestCase):
    def test_groups(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a").mkdir()
            (root / "a" / "one.txt").write_bytes(b"same")
            (root / "two.txt").write_bytes(b"same")
            (root / "other.txt").write_bytes(b"different")
            self.assertEqual(
                find_duplicates(root),
                [sorted([str(root / "a" / "one.txt"), str(root / "two.txt")])],
            )
