#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pymupdf>=1.24"]
# ///

# Writes a git-style word diff of two PDFs side by side
# Usage: pdf_diff.py OLD.pdf NEW.pdf [-o OUT.pdf]


import argparse
import difflib
import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

import pymupdf

HEADER = 22
GUTTER = 18
RED = (0.86, 0.15, 0.15)
GREEN = (0.10, 0.62, 0.25)
GREY = (0.55, 0.55, 0.55)


@dataclass(slots=True)
class Token:
    text: str
    page: int
    rects: list[pymupdf.Rect]


def running_lines(pages: list[list[tuple]]) -> set[str]:
    seen = Counter()
    for words in pages:
        seen.update({_normalise(line) for line in _lines(words)})
    return {text for text, n in seen.items() if n >= 3 and n > len(pages) / 2}


def _lines(words: list[tuple]) -> list[list[tuple]]:
    lines: dict[tuple[int, int], list[tuple]] = {}
    for w in words:
        lines.setdefault((w[5], w[6]), []).append(w)
    return list(lines.values())


def _normalise(line: list[tuple]) -> str:
    return re.sub(r"\d+", "#", " ".join(w[4] for w in line))


def tokens(doc: pymupdf.Document) -> list[Token]:
    pages = [page.get_text("words") for page in doc]
    skip = running_lines(pages)
    out: list[Token] = []
    for pno, words in enumerate(pages):
        matrix = doc[pno].rotation_matrix
        flat = [
            (w[4], pymupdf.Rect(w[:4]) * matrix, i == len(line) - 1)
            for line in _lines(words)
            if _normalise(line) not in skip
            for i, w in enumerate(line)
        ]
        k = 0
        while k < len(flat):
            text, rect, line_end = flat[k]
            rects = [rect]
            if line_end and re.search(r"\w-$", text) and k + 1 < len(flat):
                k += 1
                text += flat[k][0]
                rects.append(flat[k][1])
            out.append(Token(text, pno, rects))
            k += 1
    return out


def merged(rects: list[pymupdf.Rect]) -> list[pymupdf.Rect]:
    out: list[pymupdf.Rect] = []
    for r in rects:
        if out and abs(r.y0 - out[-1].y0) < 1 and 0 <= r.x0 - out[-1].x1 < 8:
            out[-1] = out[-1] | r
        else:
            out.append(pymupdf.Rect(r))
    return out


@dataclass(slots=True)
class Diff:
    deleted: dict[int, list[pymupdf.Rect]] = field(default_factory=dict)
    inserted: dict[int, list[pymupdf.Rect]] = field(default_factory=dict)
    shared: Counter = field(default_factory=Counter)
    words_deleted: int = 0
    words_inserted: int = 0
    hunks: int = 0


def diff(old: list[Token], new: list[Token]) -> Diff:
    result = Diff()
    matcher = difflib.SequenceMatcher(
        None, [t.text for t in old], [t.text for t in new], autojunk=False
    )
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        a, b = old[i1:i2], new[j1:j2]
        if tag == "equal":
            result.shared.update((x.page, y.page) for x, y in zip(a, b, strict=True))
            continue
        if "".join(t.text for t in a) == "".join(t.text for t in b):
            continue
        result.hunks += 1
        result.words_deleted += len(a)
        result.words_inserted += len(b)
        for side, toks in ((result.deleted, a), (result.inserted, b)):
            for page in {t.page for t in toks}:
                boxes = [r for t in toks if t.page == page for r in t.rects]
                side.setdefault(page, []).extend(merged(boxes))
    return result


def pair_pages(
    shared: Counter, old_pages: int, new_pages: int
) -> list[tuple[int | None, int | None]]:
    best_old: dict[int, int] = {}
    best_new: dict[int, int] = {}
    for (i, j), _ in shared.most_common():
        best_old.setdefault(j, i)
        best_new.setdefault(i, j)
    pairs: list[tuple[int | None, int | None]] = sorted(
        {(i, j) for j, i in best_old.items()} | set(best_new.items()),
        key=lambda p: (p[1], p[0]),
    )
    for side, count, best in ((1, new_pages, best_old), (0, old_pages, best_new)):
        for k in range(count):
            if k in best:
                continue
            at = max(
                (
                    n + 1
                    for n, p in enumerate(pairs)
                    if p[side] is not None and p[side] < k
                ),
                default=0,
            )
            pairs.insert(at, (None, k) if side else (k, None))
    return pairs


def mark(
    page: pymupdf.Page,
    boxes: list[pymupdf.Rect],
    dx: float,
    bar_x: float,
    color,
    strike: bool,
) -> None:
    shape = page.new_shape()
    for r in boxes:
        shape.draw_rect(r + (dx, HEADER, dx, HEADER))
    shape.finish(color=None, fill=color, fill_opacity=0.28)
    for r in boxes:
        y = r.y0 + r.height * (0.55 if strike else 0.98) + HEADER
        shape.draw_line((r.x0 + dx, y), (r.x1 + dx, y))
    shape.finish(color=color, width=0.8)
    for r in boxes:
        shape.draw_rect(pymupdf.Rect(bar_x, r.y0 + HEADER, bar_x + 3, r.y1 + HEADER))
    shape.finish(color=None, fill=color)
    shape.commit()


def render(
    old_doc, new_doc, old_name: str, new_name: str, d: Diff, out_path: Path
) -> int:
    out = pymupdf.open()
    pairs = pair_pages(d.shared, len(old_doc), len(new_doc))
    for i, j in pairs:
        left = old_doc[i].rect if i is not None else new_doc[j].rect
        right = new_doc[j].rect if j is not None else old_doc[i].rect
        lw = left.width
        page = out.new_page(
            width=lw + GUTTER + right.width,
            height=HEADER + max(left.height, right.height),
        )
        page.draw_rect(
            pymupdf.Rect(0, 0, page.rect.width, HEADER),
            color=None,
            fill=(0.94, 0.94, 0.94),
        )
        label_y = HEADER - 7
        if i is not None:
            area = pymupdf.Rect(0, HEADER, lw, HEADER + left.height)
            page.show_pdf_page(area, old_doc, i)
            mark(page, d.deleted.get(i, []), 0, lw + 2, RED, strike=True)
            label = f"--- a/{old_name}  page {i + 1}/{len(old_doc)}"
            page.insert_text(
                (6, label_y), label, fontname="cour", fontsize=9, color=RED
            )
        if j is not None:
            x = lw + GUTTER
            area = pymupdf.Rect(x, HEADER, x + right.width, HEADER + right.height)
            page.show_pdf_page(area, new_doc, j)
            mark(page, d.inserted.get(j, []), x, x - 5, GREEN, strike=False)
            label = f"+++ b/{new_name}  page {j + 1}/{len(new_doc)}"
            page.insert_text(
                (x + 6, label_y), label, fontname="cour", fontsize=9, color=GREEN
            )
        for side, present in (
            (pymupdf.Rect(0, HEADER, lw, page.rect.height), i),
            (pymupdf.Rect(lw + GUTTER, HEADER, page.rect.width, page.rect.height), j),
        ):
            page.draw_rect(
                side,
                color=GREY,
                width=0.5,
                dashes=None if present is not None else "[3] 0",
            )
    out.save(out_path, garbage=3, deflate=True)
    return len(pairs)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Write a git-style word diff of two PDFs as a side-by-side PDF."
    )
    parser.add_argument("old", type=Path, help="original PDF (left, a/)")
    parser.add_argument("new", type=Path, help="changed PDF (right, b/)")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="output PDF (default: NEW.diff.pdf next to NEW)",
    )
    args = parser.parse_args()
    for path in (args.old, args.new):
        if not path.is_file():
            parser.error(f"no such file: {path}")
    out_path = args.output or args.new.with_name(f"{args.new.stem}.diff.pdf")

    with pymupdf.open(args.old) as old_doc, pymupdf.open(args.new) as new_doc:
        d = diff(tokens(old_doc), tokens(new_doc))
        pages = render(old_doc, new_doc, args.old.name, args.new.name, d, out_path)

    print(
        f"{d.hunks} changes, {d.words_inserted} words inserted(+), "
        f"{d.words_deleted} words deleted(-)\n{out_path}  ({pages} pages)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
