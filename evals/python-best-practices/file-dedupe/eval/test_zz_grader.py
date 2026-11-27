import gc
import hashlib
import os
import tempfile
import time
import tracemalloc
import unittest
import warnings
from pathlib import Path
from unittest import mock

import dupfind.finder as finder
from dupfind import file_hash, find_duplicates


class GraderTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def test_groups(self):
        root = self.root
        for sub in ("x", "x/y", "z"):
            (root / sub).mkdir()
        files = {"x/a.bin": b"A" * 1000, "x/y/b.bin": b"A" * 1000, "z/c.bin": b"A" * 1000,
                 "d.bin": b"B", "z/e.bin": b"B", "f.bin": b"C", "g.empty": b"", "x/h.empty": b""}
        for name, data in files.items():
            (root / name).write_bytes(data)
        got = find_duplicates(root)
        want = sorted([
            sorted(str(root / n) for n in ("x/a.bin", "x/y/b.bin", "z/c.bin")),
            sorted(str(root / n) for n in ("d.bin", "z/e.bin")),
            sorted(str(root / n) for n in ("g.empty", "x/h.empty")),
        ])
        self.assertEqual([[str(p) for p in group] for group in got], want)
        self.assertEqual(find_duplicates(str(root)), got)

    def test_strong_hash(self):
        data = b"media file content\n" * 100
        path = self.root / "f.bin"
        path.write_bytes(data)
        strong = {hashlib.new(name, data).hexdigest() for name in ("sha256", "sha384", "sha512", "sha3_256", "sha3_512", "blake2b", "blake2s")}
        self.assertIn(file_hash(path), strong)
        self.assertEqual(file_hash(str(path)), file_hash(path))

    def test_no_leaked_files(self):
        for i in range(20):
            (self.root / f"{i}.bin").write_bytes(b"x" * (i % 3))
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            find_duplicates(self.root)
            file_hash(self.root / "1.bin")
            gc.collect()
        leaks = [w for w in caught if issubclass(w.category, ResourceWarning)]
        self.assertEqual(leaks, [], [str(w.message) for w in leaks])

    def test_large_file_memory(self):
        path = self.root / "big.bin"
        chunk = os.urandom(1 << 20)
        with path.open("wb") as f:
            for _ in range(32):
                f.write(chunk)
        tracemalloc.start()
        try:
            file_hash(path)
            _, peak = tracemalloc.get_traced_memory()
        finally:
            tracemalloc.stop()
        self.assertLess(peak, 4 << 20, f"peak {peak} bytes while hashing a 32 MiB file")

    def test_hashes_concurrently(self):
        for i in range(12):
            (self.root / f"{i}.bin").write_bytes(str(i % 4).encode())
        real = finder.file_hash

        def slow(path):
            time.sleep(0.25)
            return real(path)

        with mock.patch.object(finder, "file_hash", slow):
            start = time.monotonic()
            got = find_duplicates(self.root)
            elapsed = time.monotonic() - start
        self.assertEqual(len(got), 4)
        self.assertLess(elapsed, 1.5, f"12 files with a 0.25 s hash took {elapsed:.2f} s")
