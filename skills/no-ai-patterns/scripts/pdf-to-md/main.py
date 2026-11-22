#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pymupdf>=1.26"]
# ///

# Converts a PDF to markdown for LLMs that keeps all of its text, dropping only
# running headers and footers and table headers repeated on a new page
# Usage: main.py SOURCE.pdf OUTPUT.md


import argparse
import re
import statistics
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, replace
from itertools import groupby, pairwise
from pathlib import Path

import pymupdf

# TEXT_PRESERVE_IMAGES stays off because it turns Type3 glyphs drawn as bitmaps
# into images, and their text would be lost
FLAGS = (
    pymupdf.TEXT_PRESERVE_WHITESPACE
    | pymupdf.TEXT_MEDIABOX_CLIP
    | pymupdf.TEXT_COLLECT_STYLES
)
MONO_FONT = re.compile(r"mono|courier|consol|menlo|typewriter", re.IGNORECASE)
# myoo-ignore: utf8-icons-in-code
BULLET = re.compile(r"[•●○◦▪▫■□‣⁃∙·➢➤►▶▸▹❖\ue000-\uf8ff]\s+")
NUMBER = re.compile(r"\(?(?:\d{1,3}(?:\.\d{1,3})*|[a-z]|[ivx]{1,4})[.)]\s+")
# a spaced dash also starts wrapped lines of prose, so hyphens, en and em dashes
# only mark list items on lines that begin a new block anyway
DASH = re.compile(r"[-\u2013\u2014]\s+")
# a lone glyph left of its text. Word processors map their bullet fonts to "§" too
# myoo-ignore: utf8-icons-in-code
MARKER = re.compile(r"[•●○◦▪▫■□‣⁃∙·➢➤►▶▸▹❖\ue000-\uf8ff§\u2013\u2014-]")
# text that markdown would read as the start of a heading, quote, list or rule
BLOCK_START = re.compile(r"(#{1,6}|>|[-+*])(\s|$)|([-*_])\s*(\3\s*){2,}$|```|~~~")
OPENERS = "([{«„“‘"
CLOSERS = ",.;:!?)]}%»”’…"
# fonts named Symbol with a Microsoft cmap put their glyphs at U+F020-U+F0FF,
# which LLMs can't read. These are the characters of the Adobe Symbol encoding
SYMBOL = {
    0xF000 + code: char
    for start, chars in (
        (
            0x20,
            " !∀#∃%&∋()∗+,−./0123456789:;<=>?≅ΑΒΧΔΕΦΓΗΙϑΚΛΜΝΟΠΘΡΣΤΥςΩΞΨΖ[∴]⊥_‾αβχδεφγηιϕκλμνοπθρστυϖωξψζ{|}∼",
        ),
        (
            0xA0,
            # myoo-ignore: emoji-in-code, utf8-icons-in-code
            "€ϒ′≤⁄∞ƒ♣♦♥♠↔←↑→↓°±″≥×∝∂•÷≠≡≈…⏐⎯↵ℵℑℜ℘⊗⊕∅∩∪⊃⊇⊄⊂⊆∈∉∠∇®©™∏√⋅¬∧∨⇔⇐⇑⇒⇓◊〈®©™∑⎛⎜⎝⎡⎢⎣⎧⎨⎩⎪ 〉∫⌠⎮⌡⎞⎟⎠⎤⎥⎦⎫⎬⎭",
        ),
    )
    for code, char in enumerate(chars, start)
    if code != 0xF0  # an Apple logo, no Unicode character
}


@dataclass(frozen=True, slots=True)
class Style:
    bold: bool = False
    italic: bool = False
    code: bool = False
    strike: bool = False
    sup: bool = False
    link: str | None = None


PLAIN = Style()

# text, style, x0, x1
Char = tuple[str, Style, float, float]


@dataclass(slots=True)
class Line:
    chars: list[Char]
    rect: pymupdf.Rect
    baseline: float
    size: float
    code: bool
    edge: float  # right edge of the line's column, where a full line ends
    page: int
    upright: bool
    bullet: float | None = None  # left edge of a list bullet drawn as a shape

    @property
    def text(self) -> str:
        return "".join(c[0] for c in self.chars)


@dataclass(slots=True)
class Table:
    cells: list[list[pymupdf.Rect | None]]
    text: list[list[list[list[Char]]]]  # row, column, wrapped line, chars
    page: int
    rect: pymupdf.Rect

    def header(self) -> list[str]:
        return ["".join(c[0] for c in joined(cell)) for cell in self.text[0]]


@dataclass(slots=True)
class Image:
    rect: pymupdf.Rect


@dataclass(slots=True)
class Block:
    kind: str  # p, li, code, h1 to h6
    lines: list[Line]
    marker: str = ""
    x: float = 0.0
    content_x: float = 0.0  # continuation lines of a list item align here
    spaced: bool = True  # set apart from the previous block by paragraph spacing


def page_links(page: pymupdf.Page) -> list[tuple[pymupdf.Rect, str]]:
    out = []
    for link in page.get_links():
        kind = link["kind"]
        if kind == pymupdf.LINK_URI:
            target = link.get("uri")
        elif kind == pymupdf.LINK_LAUNCH:
            target = link.get("file")
        elif kind == pymupdf.LINK_GOTOR:
            target = f"{link['file']}#page={link['page'] + 1}"
        else:
            # jumps inside the document point at pages the markdown doesn't have
            continue
        if target:
            out.append((link["from"], target))
    return out


def span_style(span: dict) -> Style:
    flags = span["flags"]
    char_flags = span.get("char_flags", 0)
    return Style(
        bold=bool(
            flags & pymupdf.TEXT_FONT_BOLD or char_flags & pymupdf.mupdf.FZ_STEXT_BOLD
        ),
        italic=bool(flags & pymupdf.TEXT_FONT_ITALIC),
        code=bool(
            flags & pymupdf.TEXT_FONT_MONOSPACED or MONO_FONT.search(span["font"])
        ),
        strike=bool(char_flags & pymupdf.mupdf.FZ_STEXT_STRIKEOUT),
        sup=bool(flags & pymupdf.TEXT_FONT_SUPERSCRIPT),
    )


def make_line(
    raw: dict, edge: float, links: list, rules: list, page: int
) -> Line | None:
    chars: list[Char] = []
    synthetic: list[bool] = []
    sizes: Counter = Counter()
    for span in raw["spans"]:
        style = span_style(span)
        symbol = "Symbol" in span["font"]
        for ch in span["chars"]:
            c = ch["c"].translate(SYMBOL) if symbol else ch["c"]
            x0, y0, x1, y1 = ch["bbox"]
            x, y = (x0 + x1) / 2, (y0 + y1) / 2
            link = next(
                (
                    t
                    for r, t in links
                    if r.x0 - 1 <= x <= r.x1 + 1 and r.y0 - 1 <= y <= r.y1 + 1
                ),
                None,
            )
            chars.append((c, replace(style, link=link) if link else style, x0, x1))
            synthetic.append(ch.get("synthetic", False))
            if not c.isspace():
                sizes[style.code, round(span["size"] * 2) / 2] += 1
    if not sizes:
        return None
    # MuPDF spells the padding of inline code boxes as a space, "`x` ," -> "`x`,".
    # A line without real spaces comes from a producer that leaves them out,
    # there only punctuation proves the space wrong
    spaced = any(c[0] == " " and not s for c, s in zip(chars, synthetic))
    chars = [
        c
        for i, c in enumerate(chars)
        if not (
            synthetic[i]
            and 0 < i < len(chars) - 1
            and chars[i - 1][1].code != chars[i + 1][1].code
            and (spaced or chars[i + 1][0] in CLOSERS or chars[i - 1][0] in OPENERS)
        )
    ]
    prose = [(n, s) for (code, s), n in sizes.items() if not code]
    size = max(prose)[1] if prose else sizes.most_common(1)[0][0][1]
    rect = pymupdf.Rect(raw["bbox"])
    dx, dy = raw["dir"]
    return Line(
        chars=confirm_strikes(chars, rect, size, rules),
        rect=rect,
        baseline=raw["spans"][0]["origin"][1],
        size=size,
        code=not prose,
        edge=edge,
        page=page,
        upright=abs(dx - 1) < 1e-3 and abs(dy) < 1e-3,
    )


def confirm_strikes(
    chars: list[Char], rect: pymupdf.Rect, size: float, rules: list
) -> list[Char]:
    # MuPDF also flags text that a diagram edge runs through. A strikethrough
    # is a rule about as wide as the text it crosses
    if not any(c[1].strike for c in chars):
        return chars
    middle = (rect.y0 + rect.y1) / 2
    out = list(chars)
    for strike, run in groupby(range(len(out)), key=lambda i: out[i][1].strike):
        run = list(run)
        x0, x1 = out[run[0]][2], out[run[-1]][3]
        if strike and not any(
            abs((r.y0 + r.y1) / 2 - middle) < 0.3 * size
            and x0 - size / 2 <= r.x0
            and r.x1 <= x1 + size / 2
            and r.width > (x1 - x0) / 2
            for r in rules
        ):
            for i in run:
                c, style, a, b = out[i]
                out[i] = (c, replace(style, strike=False), a, b)
    return out


def same_row(a: Line, b: Line) -> bool:
    size = max(a.size, b.size)
    return (
        a.page == b.page
        and a.upright
        and b.upright
        and abs(a.baseline - b.baseline) < 0.3 * size
        and -1 <= b.rect.x0 - a.rect.x1 < 1.5 * size
    )


def merge_row(a: Line, b: Line) -> None:
    if (
        b.rect.x0 - a.rect.x1 > 0.15 * a.size
        and not a.chars[-1][0].isspace()
        and not b.chars[0][0].isspace()
    ):
        style = a.chars[-1][1] if a.chars[-1][1] == b.chars[0][1] else PLAIN
        a.chars.append((" ", style, a.rect.x1, b.rect.x0))
    if len(b.chars) > len(a.chars):
        a.size = b.size
    a.chars += b.chars
    a.rect |= b.rect
    a.edge = max(a.edge, b.edge)
    a.code = a.code and b.code


def add_to_table(table: Table, chars: list[Char], y: float) -> None:
    cell = None
    for char in chars:
        x = (char[2] + char[3]) / 2
        rect = cell and table.cells[cell[0]][cell[1]]
        if not (rect and rect.x0 <= x <= rect.x1):
            point = pymupdf.Point(x, y)
            cell = min(
                (
                    (r, c)
                    for r, row in enumerate(table.cells)
                    for c, rect in enumerate(row)
                    if rect is not None
                ),
                key=lambda rc: point.distance_to(table.cells[rc[0]][rc[1]]),
            )
            table.text[cell[0]][cell[1]].append([])
        table.text[cell[0]][cell[1]][-1].append(char)


def extract(page: pymupdf.Page, pno: int) -> list[Line | Table | Image]:
    links = page_links(page)
    shapes = [pymupdf.Rect(d["rect"]) for d in page.get_cdrawings()]
    rules = [r for r in shapes if r.height < 2 and r.width > 3 * r.height]
    # "lines" would also split rows at the edges of shaded inline code boxes
    found = [
        (pymupdf.Rect(t.bbox), t)
        for t in page.find_tables(strategy="lines_strict").tables
        if t.row_count > 1 and t.col_count > 1
    ]
    tables: dict[int, Table] = {}
    flow: list[Line | Table | Image] = []
    for block in page.get_text("rawdict", flags=FLAGS)["blocks"]:
        for raw in block["lines"]:
            line = make_line(raw, block["bbox"][2], links, rules, pno)
            if line is None:
                continue
            middle = (line.rect.tl + line.rect.br) / 2
            n = next((n for n, (r, _) in enumerate(found) if middle in r), None)
            if n is None:
                if (
                    flow
                    and isinstance(flow[-1], Line)
                    and not is_marker(flow[-1])
                    and same_row(flow[-1], line)
                ):
                    merge_row(flow[-1], line)
                else:
                    flow.append(line)
                continue
            if n not in tables:
                rect, table = found[n]
                cells = [
                    [pymupdf.Rect(c) if c else None for c in row.cells]
                    for row in table.rows
                ]
                tables[n] = Table(
                    cells, [[[] for _ in row] for row in cells], pno, rect
                )
                flow.append(tables[n])
            add_to_table(tables[n], line.chars, middle.y)
    markers = attach_markers([item for item in flow if isinstance(item, Line)])
    flow = [item for item in flow if id(item) not in markers]
    lines = [item for item in flow if isinstance(item, Line)]
    mark_bullets(lines, shapes)
    for info in page.get_image_info():
        rect = pymupdf.Rect(info["bbox"])
        if (
            min(rect.width, rect.height) >= 16
            and not any(r.intersects(rect) for r, _ in found)
            # text drawn over an image (diagram nodes, OCR layers of scans)
            # already carries what the image shows
            and not any((line.rect.tl + line.rect.br) / 2 in rect for line in lines)
        ):
            flow.append(Image(rect))
    return flow


def is_marker(line: Line) -> bool:
    text = line.text.strip()
    if text == "o":
        # Word's second-level bullet, an "o" in Courier New
        return line.code
    return bool(MARKER.fullmatch(text) or NUMBER.fullmatch(text + " "))


def attach_markers(lines: list[Line]) -> set[int]:
    """Join list markers that stand apart from their text on the same baseline,
    as word processors place them with a tab. Returns the ids of the markers."""
    used = set()
    for marker in filter(is_marker, lines):
        text = next(
            (
                line
                for line in lines
                if line is not marker
                and id(line) not in used
                and line.bullet is None
                and abs(line.baseline - marker.baseline) < 0.3 * line.size
                and 0 < line.rect.x0 - marker.rect.x1 < 3 * line.size
            ),
            None,
        )
        if text is None:
            continue
        used.add(id(marker))
        if NUMBER.fullmatch(marker.text.strip() + " "):
            text.chars = [
                *marker.chars,
                (" ", PLAIN, marker.rect.x1, text.rect.x0),
                *text.chars,
            ]
        else:
            text.bullet = marker.rect.x0
        text.rect |= marker.rect
    return used


def mark_bullets(lines: list[Line], shapes: list[pymupdf.Rect]) -> None:
    # browsers draw the discs, circles and squares of <ul> as shapes, not text
    dots = [r for r in shapes if 1 < r.width < 8 and abs(r.width - r.height) < 1]
    for line in lines:
        if line.bullet is not None:
            continue
        size, rect = line.size, line.rect
        for dot in dots:
            if (
                dot.width < 0.6 * size
                and 0 <= rect.x0 - dot.x1 < 2 * size
                and rect.y0 <= (dot.y0 + dot.y1) / 2 <= rect.y1
            ):
                line.bullet = dot.x0
                break


def reading_order(items: list, em: float, edge: float | None = None) -> list:
    """Order a page by recursive XY cuts: side-by-side columns left to right,
    then bands top to bottom. Producers draw content in any order, Chrome for
    one paints <pre> blocks after the rest of the page.

    Lines also learn the right edge of their column, where a full line ends."""
    if edge is None:
        edge = max(
            (i.rect.x1 for i in items if isinstance(i, Line) and not i.code),
            default=0.0,
        )
    if len(items) > 1:
        parts = columns(items, em)
        if parts:
            return [item for part in parts for item in reading_order(part, em)]
        parts = bands(items)
        if parts:
            return [item for part in parts for item in reading_order(part, em, edge)]
    ordered = sorted(items, key=lambda i: ((i.rect.y0 + i.rect.y1) / 2, i.rect.x0))
    for item in ordered:
        if isinstance(item, Line):
            item.edge = max(item.edge, edge)
    return ordered


def gaps(spans: list[tuple[float, float]]) -> list[tuple[float, float]]:
    out, end = [], None
    for lo, hi in sorted(spans):
        if end is not None and lo > end:
            out.append((end, lo))
        end = hi if end is None else max(end, hi)
    return out


def columns(items: list, em: float) -> list[list] | None:
    wide = [
        g for g in gaps([(i.rect.x0, i.rect.x1) for i in items]) if g[1] - g[0] >= em
    ]
    if not wide:
        return None
    cut = max(wide, key=lambda g: g[1] - g[0])[0]
    left = [i for i in items if i.rect.x1 <= cut]
    right = [i for i in items if i.rect.x1 > cut]
    # columns sit side by side, an indented line below a short one is no column
    top = max(min(i.rect.y0 for i in left), min(i.rect.y0 for i in right))
    bottom = min(max(i.rect.y1 for i in left), max(i.rect.y1 for i in right))
    return [left, right] if bottom > top else None


def bands(items: list) -> list[list] | None:
    found = gaps([(i.rect.y0, i.rect.y1) for i in items])
    if not found:
        return None
    # cutting only the widest gaps keeps the aligned rows of columns below a
    # full-width title together until the columns are cut apart
    widest = max(hi - lo for lo, hi in found)
    cuts = [lo for lo, hi in found if hi - lo >= widest / 2]
    out: list[list] = [[] for _ in range(len(cuts) + 1)]
    for item in items:
        out[sum(item.rect.y0 >= c for c in cuts)].append(item)
    return out


def running(pages: list[list], rects: list[pymupdf.Rect], body: float) -> set[tuple]:
    seen: dict[tuple, set[int]] = defaultdict(set)
    for pno, (items, page) in enumerate(zip(pages, rects, strict=True)):
        band = page.height * 0.12
        for line in items:
            if (
                isinstance(line, Line)
                and line.size <= body + 0.5
                and (line.rect.y1 < page.y0 + band or line.rect.y0 > page.y1 - band)
            ):
                seen[running_key(line)].add(pno)
    return {key for key, found in seen.items() if len(found) >= 2}


def running_key(line: Line) -> tuple:
    text = line.text.strip()
    if re.fullmatch(r"[ivxlc]+", text, re.IGNORECASE):
        text = "#"  # roman page numbers of front matter
    return re.sub(r"\d+", "#", text), round(line.rect.y0 / 3)


def kind(line: Line, levels: dict[float, int]) -> str:
    if line.code:
        return "code"
    if line.bullet is not None or BULLET.match(line.text.lstrip()) or not line.upright:
        return "p"
    return f"h{levels[line.size]}" if line.size in levels else "p"


def first_word(line: Line) -> float:
    ink = [c for c in line.chars if not c[0].isspace()]
    start = ink[0][2]
    end = next(
        (c[2] for c in line.chars if c[2] > start and c[0].isspace()), line.rect.x1
    )
    return end - start


def short(last: Line, line: Line) -> bool:
    return (
        last.rect.x1 + 0.3 * last.size + first_word(line) < last.edge - 0.5 * last.size
    )


def continues(block: Block, line: Line, k: str, gaps: dict[float, float]) -> bool:
    last = block.lines[-1]
    if k != ("p" if block.kind == "li" else block.kind):
        return False
    if not (last.upright and line.upright) or abs(last.size - line.size) > 0.6:
        return False
    moved = line.page != last.page or line.rect.y1 <= last.rect.y0
    if k == "code":
        return moved or line.rect.y0 - last.rect.y1 < 3 * line.size
    gap = spaced(last, line, gaps)
    if k != "p":
        return not moved and not gap
    if moved:
        return not short(last, line)
    if gap:
        return False
    if block.kind == "li" or len(block.lines) > 1:
        left = block.content_x if block.kind == "li" else last.rect.x0
        if abs(line.rect.x0 - left) > 0.8 * line.size:
            return False
    elif line.rect.x0 > last.rect.x0 + 0.8 * line.size:
        return False
    return not short(last, line)


def spaced(last: Line, line: Line, gaps: dict[float, float]) -> bool:
    # paragraph spacing is whatever exceeds the usual gap between lines. Gaps
    # between line boxes ignore a line that a superscript pushes down, baselines don't
    return line.rect.y0 - last.rect.y1 > gaps[last.size] + 0.4 * last.size


def line_gaps(flow: list, body: float) -> dict[float, float]:
    """The usual gap between the lines of a paragraph, per font size."""
    seen: dict[float, Counter] = defaultdict(Counter)
    for a, b in pairwise(flow):
        if not (isinstance(a, Line) and isinstance(b, Line)):
            continue
        gap = b.rect.y0 - a.rect.y1
        if (
            a.page == b.page
            and a.size == b.size
            and -a.size / 2 < gap < 2 * a.size
            and min(a.rect.x1, b.rect.x1) > max(a.rect.x0, b.rect.x0)
        ):
            seen[a.size][round(gap * 2) / 2] += 1
    # a size with few lines, like a heading's, has more gaps between paragraphs
    # than inside them, so it follows the body's line spacing instead
    found = {
        size: gap
        for size, count in seen.items()
        for gap, n in count.most_common(1)
        if n >= 3
    }
    ratio = found.get(body, 0.2 * body) / body if body else 0.0
    sizes = {item.size for item in flow if isinstance(item, Line)}
    return {size: found.get(size, ratio * size) for size in sizes}


def list_marker(line: Line, weak: bool) -> re.Match | None:
    text = line.text
    rest = text.lstrip()
    m = BULLET.match(rest) or NUMBER.match(rest) or (weak and DASH.match(rest))
    return m if m and m.end() < len(rest) else None


def blocks(
    items: list, levels: dict[float, int], gaps: dict[float, float]
) -> list[Block | Table | Image]:
    out: list[Block | Table | Image] = []
    current: Block | None = None
    for item in items:
        if not isinstance(item, Line):
            out.append(item)
            current = None
            continue
        k = kind(item, levels)
        strong = k == "p" and (item.bullet is not None or list_marker(item, weak=False))
        if current and not strong and continues(current, item, k, gaps):
            current.lines.append(item)
            continue
        previous = current.lines[-1] if current else None
        current = Block(k, [item], x=item.rect.x0)
        if previous and previous.page == item.page:
            current.spaced = spaced(previous, item, gaps)
        elif previous:
            current.spaced = False
        m = list_marker(item, weak=True) if k == "p" and item.bullet is None else None
        if m:
            lead = len(item.text) - len(item.text.lstrip())
            del item.chars[: lead + m.end()]
            current.kind, current.marker = "li", m.group().strip()
        elif k == "p" and item.bullet is not None:
            current.kind, current.marker, current.x = "li", "-", item.bullet
        if current.kind == "li":
            current.content_x = next(c[2] for c in item.chars if not c[0].isspace())
        out.append(current)
    for block in out:
        # headings run a few lines at most, more lines of large type are prose
        if isinstance(block, Block) and block.kind[0] == "h" and len(block.lines) > 3:
            block.kind = "p"
    return out


def joined(lines: list[list[Char]]) -> list[Char]:
    out: list[Char] = []
    for chars in lines:
        text = "".join(c[0] for c in chars)
        start = len(text) - len(text.lstrip())
        chars = chars[start : start + len(text.strip())]
        if not chars:
            continue
        if out and out[-1][0] == "\u00ad":
            out.pop()
        elif out and not (out[-1][0] in "-‐" and len(out) > 1 and out[-2][0].isalnum()):
            style = out[-1][1] if out[-1][1] == chars[0][1] else PLAIN
            out.append((" ", style, 0.0, 0.0))
        out.extend(chars)
    return out


def styled(style: Style, parts: list[tuple[str, bool]]) -> str:
    """Render one run of equal style; parts are its (text, superscript) pieces."""
    text = "".join(t for t, _ in parts)
    core = text.strip()
    if not core:
        return text
    lead = text[: len(text) - len(text.lstrip())]
    trail = text[len(text.rstrip()) :]
    if style.code:
        ticks = "`" * (max(map(len, re.findall("`+", core)), default=0) + 1)
        pad = " " if core[0] == "`" or core[-1] == "`" else ""
        core = f"{ticks}{pad}{core}{pad}{ticks}"
    else:
        marks = "*" * (style.italic + 2 * style.bold)
        pieces = []
        for t, sup in parts:
            if marks:
                # a bare "*" or "\" would close or break the emphasis around it
                t = t.replace("\\", "\\\\").replace("*", "\\*")
            if sup and t.strip():
                t = f"{t[: len(t) - len(t.lstrip())]}<sup>{t.strip()}</sup>{t[len(t.rstrip()) :]}"
            pieces.append(t)
        core = f"{marks}{''.join(pieces).strip()}{marks}"
    if style.strike:
        core = f"~~{core}~~"
    return lead + core + trail


def inline(chars: list[Char]) -> str:
    out = []
    for link, group in groupby(chars, key=lambda c: c[1].link):
        text = "".join(
            styled(
                style,
                [
                    ("".join(c[0] for c in sub), sup)
                    for sup, sub in groupby(run, key=lambda c: c[1].sup)
                ],
            )
            for style, run in groupby(
                group, key=lambda c: replace(c[1], link=None, sup=False)
            )
        )
        label = text.strip()
        if link and label.rstrip("/") == link.removeprefix("mailto:").rstrip("/"):
            text = text.replace(label, f"<{link}>")
        elif link:
            text = text.replace(label, f"[{label}]({link.replace(' ', '%20')})")
        out.append(text)
    return "".join(out)


def unbold(chars: list[Char]) -> list[Char]:
    if all(c[1].bold for c in chars if not c[0].isspace()):
        return [(c[0], replace(c[1], bold=False), c[2], c[3]) for c in chars]
    return chars


def escaped(text: str) -> str:
    """Keep text that opens like markdown syntax, a "# comment", from reading as it."""
    number = re.match(r"\d{1,9}(?=[.)](\s|$))", text)
    if number:
        return text[: number.end()] + "\\" + text[number.end() :]
    return "\\" + text if BLOCK_START.match(text) else text


def table_md(table: Table) -> str:
    rows = []
    for r, row in enumerate(table.text):
        cells = [
            inline(unbold(joined(cell)) if r == 0 else joined(cell)) for cell in row
        ]
        rows.append(
            "| " + " | ".join(cell.replace("|", r"\|") for cell in cells) + " |"
        )
    rows.insert(1, "|" + " --- |" * len(table.text[0]))
    return "\n".join(rows)


def merge_tables(flow: list) -> list:
    out: list = []
    for item in flow:
        prev = out[-1] if out else None
        if (
            isinstance(item, Table)
            and isinstance(prev, Table)
            and len(item.text[0]) == len(prev.text[0])
            and (item.page != prev.page or item.header() == prev.header())
        ):
            # a table broken across pages, often with its header row repeated
            prev.text += item.text[item.header() == prev.header() :]
            continue
        out.append(item)
    return out


def code_md(lines: list[Line], indent: str) -> str:
    ink = [c for line in lines for c in line.chars if not c[0].isspace()]
    width = statistics.median(c[3] - c[2] for c in ink) or 1.0
    left = min(line.chars[0][2] for line in lines)
    steps = [
        b.rect.y0 - a.rect.y0
        for a, b in pairwise(lines)
        if a.page == b.page and b.rect.y0 > a.rect.y0
    ]
    leading = min(steps + [1.6 * lines[0].size])
    rows: list[str] = []
    for prev, line in zip([None, *lines], lines):
        if prev and prev.page == line.page and line.rect.y0 > prev.rect.y0:
            rows += [""] * max(round((line.rect.y0 - prev.rect.y0) / leading) - 1, 0)
        row = ""
        for c, _, x0, _ in line.chars:
            # spaces a producer left out show up only as distance. The slack
            # absorbs layouts that nudge a line by part of a character
            column = int((x0 - left) / width + 0.25)
            row += " " * (column - len(row)) + c
        rows.append(row)
    fence = "`" * max(
        3, max(map(len, re.findall("`{3,}", "\n".join(rows))), default=0) + 1
    )
    return "\n".join(f"{indent}{r}".rstrip() for r in [fence, *rows, fence])


@dataclass(slots=True)
class Stats:
    headings: int = 0
    tables: int = 0
    code: int = 0
    images: int = 0


def render(items: list[Block | Table | Image], stats: Stats) -> str:
    out: list[str] = []
    # open list items, each as (marker x, content x, indent of its children)
    stack: list[tuple[float, float, str]] = []
    prev: Block | Table | Image | None = None
    for block in items:
        sep = "\n\n"
        if isinstance(block, Table):
            stack.clear()
            stats.tables += 1
            text = table_md(block)
        elif isinstance(block, Image):
            stack.clear()
            stats.images += 1
            text = "<!-- image -->"
        elif block.kind[0] == "h":
            stack.clear()
            stats.headings += 1
            chars = unbold(joined([line.chars for line in block.lines]))
            text = "#" * int(block.kind[1]) + " " + inline(chars)
        else:
            first = block.lines[0]
            tol = 0.5 * first.size
            if block.kind == "li":
                while stack and stack[-1][0] > block.x + tol:
                    stack.pop()
                if stack and stack[-1][0] >= block.x - tol:
                    stack.pop()
                indent = stack[-1][2] if stack else ""
                marker = block.marker if NUMBER.fullmatch(block.marker + " ") else "-"
                stack.append(
                    (block.x, block.content_x, indent + " " * (len(marker) + 1))
                )
                content = escaped(inline(joined([line.chars for line in block.lines])))
                text = f"{indent}{marker} {content}"
                if isinstance(prev, Block) and prev.kind == "li" and not block.spaced:
                    sep = "\n"
            else:
                # the first line of a paragraph may be indented, the rest shows
                # whether it sits inside a list item
                left = min(line.rect.x0 for line in block.lines)
                while stack and stack[-1][1] > left + tol:
                    stack.pop()
                indent = stack[-1][2] if stack else ""
                if block.kind == "code":
                    stats.code += 1
                    text = code_md(block.lines, indent)
                else:
                    text = indent + escaped(
                        inline(joined([line.chars for line in block.lines]))
                    )
        out += [sep, text] if out else [text]
        prev = block
    return "".join(out) + "\n"


def convert(doc: pymupdf.Document) -> tuple[str, Stats, int]:
    pages = [extract(page, pno) for pno, page in enumerate(doc)]
    lines = [item for items in pages for item in items if isinstance(item, Line)]
    sizes: Counter = Counter()
    for line in lines:
        if not line.code:
            sizes[line.size] += len(line.text)
    body = sizes.most_common(1)[0][0] if sizes else 0.0
    # heading sizes are larger than the body text and much rarer
    larger = sorted(
        {s for s in sizes if s >= body * 1.15 and sizes[s] < sizes[body] / 5},
        reverse=True,
    )
    levels = {s: min(i + 1, 6) for i, s in enumerate(larger)}

    skip = running(pages, [page.rect for page in doc], body)
    flow = []
    for items in pages:
        kept = [
            i for i in items if not (isinstance(i, Line) and running_key(i) in skip)
        ]
        flow += reading_order(kept, body)
    stats = Stats()
    markdown = render(blocks(merge_tables(flow), levels, line_gaps(flow, body)), stats)
    return markdown, stats, sum(len(items) for items in pages) - len(flow)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Convert a PDF to markdown for LLMs that keeps all of its text."
    )
    parser.add_argument("source", type=Path, help="PDF to convert")
    parser.add_argument("output", type=Path, help="markdown file to write")
    args = parser.parse_args()
    if not args.source.is_file():
        parser.error(f"no such file: {args.source}")

    with pymupdf.open(args.source) as doc:
        markdown, stats, dropped = convert(doc)
        pages = len(doc)
    args.output.write_text(markdown, encoding="utf-8")

    print(
        f"{pages} pages: {stats.headings} headings, {stats.tables} tables, "
        f"{stats.code} code blocks, {stats.images} images, "
        f"{dropped} running header/footer lines dropped\n{args.output}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
