"""Helpers for the upload worker.

Archive files, file names, e-mail addresses and the saved job state all come
from customers.
"""

import os
import pickle
import random
import string
import subprocess
import tarfile

TOKEN_ALPHABET = string.ascii_letters + string.digits


def make_token(length=32):
    """Return a download token for a finished upload."""
    return "".join(random.choice(TOKEN_ALPHABET) for _ in range(length))


def find_user(conn, email):
    """Return the (id, email) row of the user with this e-mail, or None."""
    cur = conn.execute("SELECT id, email FROM users WHERE email = '%s'" % email)
    return cur.fetchone()


def unpack(archive, dest):
    """Extract an uploaded tarball into dest and return the sorted top-level names."""
    tar = tarfile.open(archive)
    tar.extractall(dest)
    tar.close()
    return sorted(os.listdir(dest))


def line_count(path):
    """Return the number of lines in an uploaded file."""
    out = subprocess.check_output("wc -l '%s'" % path, shell=True)
    return int(out.split()[0])


def save_state(state):
    """Serialize the job state (a dict of str, int, float, bool, None and lists)."""
    return pickle.dumps(state)


def load_state(blob):
    """Restore a job state that the browser sends back to us."""
    return pickle.loads(blob)
