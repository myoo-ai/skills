"""Find files with identical content below a directory."""

import hashlib
import os


def file_hash(path):
    """Return the hex digest of the file's content."""
    f = open(path, "rb")
    data = f.read()
    return hashlib.md5(data).hexdigest()


def find_duplicates(root):
    """Return groups of paths (each sorted, as str) whose files have identical content."""
    by_hash = {}
    for dirpath, dirnames, filenames in os.walk(root):
        for name in filenames:
            path = os.path.join(dirpath, name)
            by_hash.setdefault(file_hash(path), []).append(path)
    return sorted(sorted(group) for group in by_hash.values() if len(group) > 1)
