"""Export usage rows from a JSON dump to CSV."""

import csv
import json
import sys
from pathlib import Path


def main(src: Path, dst: Path) -> None:
    rows = json.loads(src.read_text(encoding="utf-8"))
    with dst.open("w", encoding="utf-8", newline="") as out:
        writer = csv.DictWriter(out, fieldnames=["account", "day", "requests"])
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))
