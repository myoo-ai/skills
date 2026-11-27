import io
import sqlite3
import tarfile
import tempfile
import unittest
from pathlib import Path

from uploads import find_user, line_count, load_state, make_token, save_state, unpack


class ProcessorTest(unittest.TestCase):
    def test_token(self):
        token = make_token()
        self.assertEqual(len(token), 32)
        self.assertTrue(token.isalnum())
        self.assertEqual(len(make_token(12)), 12)

    def test_find_user(self):
        conn = sqlite3.connect(":memory:")
        try:
            conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT)")
            conn.execute("INSERT INTO users (email) VALUES ('ann@example.com')")
            self.assertEqual(find_user(conn, "ann@example.com"), (1, "ann@example.com"))
            self.assertIsNone(find_user(conn, "bob@example.com"))
        finally:
            conn.close()

    def test_unpack(self):
        with tempfile.TemporaryDirectory() as tmp:
            archive = Path(tmp, "upload.tar")
            with tarfile.open(archive, "w") as tar:
                data = b"hello\n"
                info = tarfile.TarInfo("docs/readme.txt")
                info.size = len(data)
                tar.addfile(info, io.BytesIO(data))
            dest = Path(tmp, "out")
            dest.mkdir()
            self.assertEqual(unpack(archive, dest), ["docs"])
            self.assertEqual(Path(dest, "docs", "readme.txt").read_text(encoding="utf-8"), "hello\n")

    def test_line_count(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp, "orders.csv")
            path.write_text("a\nb\nc\n", encoding="utf-8")
            self.assertEqual(line_count(path), 3)

    def test_state_round_trip(self):
        state = {"step": 3, "files": ["a.csv", "b.csv"], "done": False, "ratio": 0.5, "error": None}
        self.assertEqual(load_state(save_state(state)), state)
