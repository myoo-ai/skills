import io
import pickle
import sqlite3
import tarfile
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import uploads.processor as processor
from uploads import find_user, line_count, load_state, make_token, save_state, unpack


class Exploit:
    def __init__(self, marker):
        self.marker = marker

    def __reduce__(self):
        return (Path.touch, (Path(self.marker),))


class GraderTest(unittest.TestCase):
    def test_token_format_and_source(self):
        with mock.patch("random.choice", side_effect=AssertionError("random used")), \
                mock.patch("random.choices", side_effect=AssertionError("random used")):
            tokens = {make_token() for _ in range(50)}
        self.assertEqual(len(tokens), 50)
        for token in tokens:
            self.assertEqual(len(token), 32)
            self.assertTrue(token.isascii() and token.isalnum(), token)
        self.assertEqual(len(make_token(7)), 7)

    def test_sql_injection(self):
        conn = sqlite3.connect(":memory:")
        try:
            conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT)")
            conn.execute("INSERT INTO users (email) VALUES ('ann@example.com')")
            conn.execute("INSERT INTO users (email) VALUES ('o''hara@example.com')")
            self.assertIsNone(find_user(conn, "x' OR '1'='1"))
            self.assertEqual(find_user(conn, "o'hara@example.com"), (2, "o'hara@example.com"))
            self.assertEqual(find_user(conn, "ann@example.com"), (1, "ann@example.com"))
        finally:
            conn.close()

    def test_shell_injection(self):
        with tempfile.TemporaryDirectory() as tmp:
            name = Path(tmp, "x'; touch PWNED; echo '.csv")
            name.write_text("1\n2\n", encoding="utf-8")
            self.assertEqual(line_count(name), 2)
            self.assertEqual(line_count(str(name)), 2)
            self.assertFalse(Path(tmp, "PWNED").exists())
            self.assertFalse(Path("PWNED").exists())

    def test_tar_traversal(self):
        with tempfile.TemporaryDirectory() as tmp:
            archive = Path(tmp, "evil.tar")
            with tarfile.open(archive, "w") as tar:
                data = b"owned\n"
                info = tarfile.TarInfo("../escaped.txt")
                info.size = len(data)
                tar.addfile(info, io.BytesIO(data))
                link = tarfile.TarInfo("passwd")
                link.type = tarfile.SYMTYPE
                link.linkname = "/etc/passwd"
                tar.addfile(link)
            dest = Path(tmp, "out")
            dest.mkdir()
            with self.assertRaises(Exception):
                unpack(archive, dest)
            self.assertFalse(Path(tmp, "escaped.txt").exists())

    def test_state_is_not_pickle(self):
        state = {"step": 1, "files": ["a"], "done": True, "ratio": 1.5, "error": None}
        self.assertEqual(load_state(save_state(state)), state)
        with tempfile.TemporaryDirectory() as tmp:
            marker = Path(tmp, "executed")
            try:
                load_state(pickle.dumps(Exploit(str(marker))))
            except Exception:
                pass
            self.assertFalse(marker.exists(), "load_state ran code from the blob")
