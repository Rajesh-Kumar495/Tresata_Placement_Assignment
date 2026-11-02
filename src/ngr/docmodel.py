"""HTML earnings release -> deterministic Document model (architecture §4.2).

Why a custom model instead of plain text: prominence rules depend on position
and style, and tie-out needs cell-level numbers. Everything here is pure and
deterministic: same bytes in, same model out, with stable IDs.

Known limits (documented, tested where possible):
  * rowspan is ignored (rare in EDGAR Ex 99.1 tables);
  * styles from external/class CSS are not resolved -> style signal may be
    "unavailable" (FMEA F10);
  * text inside images is invisible; images are recorded so callers can mark
    affected rules NOT_EVALUATED (ADR-011).
"""

from __future__ import annotations

import hashlib
import re
from typing import Literal

from bs4 import BeautifulSoup, NavigableString, Tag
from pydantic import BaseModel

from .numeric import ParsedNumber, looks_like_year, normalize_ws, parse_number

BLOCK_TAGS = {"p", "div", "li", "h1", "h2", "h3", "h4", "h5", "h6", "center", "blockquote", "td", "th"}
_TEXT_BLOCK_TAGS = BLOCK_TAGS - {"td", "th"}
BULLET_GLYPHS = "•·▪◦●■‣∙"
_BULLET_RE = re.compile(rf"^[{BULLET_GLYPHS}]\s*")
_SCALE_RE = re.compile(r"\bin\s+(thousands|millions|billions)\b", re.I)
_PERIOD_RE = re.compile(
    r"\b(three|six|nine|twelve)\s+months\s+ended\b|\b(quarter|year|fiscal year)\s+ended\b|"
    r"^(january|february|march|april|may|june|july|august|september|october|november|december)\b.*\d{4}",
    re.I,
)
_FONT_SIZE_RE = re.compile(r"font-size\s*:\s*([\d.]+)\s*(pt|px)", re.I)
_BOLD_RE = re.compile(r"font-weight\s*:\s*(bold|bolder|[6-9]00)", re.I)
_ITALIC_RE = re.compile(r"font-style\s*:\s*italic", re.I)
_PREFIX_FRAGMENTS = {"$", "US$", "€", "£"}
_SUFFIX_FRAGMENTS = {")", "%", ")%", "%)"}

BlockKind = Literal["headline", "heading", "bullet", "paragraph", "footnote"]


class Run(BaseModel):
    text: str
    bold: bool = False
    italic: bool = False
    font_size_pt: float | None = None


class Block(BaseModel):
    id: str
    order: int
    kind: BlockKind = "paragraph"
    text: str
    runs: list[Run]
    source_tag: str
    char_start: int = 0
    char_end: int = 0

    @property
    def bold_fraction(self) -> float:
        total = sum(len(r.text) for r in self.runs) or 1
        return sum(len(r.text) for r in self.runs if r.bold) / total

    @property
    def max_font_pt(self) -> float | None:
        sizes = [r.font_size_pt for r in self.runs if r.font_size_pt]
        return max(sizes) if sizes else None


class Cell(BaseModel):
    id: str
    text: str
    col_start: int  # grid range of the digit-bearing fragment (alignment key)
    col_end: int
    number: ParsedNumber | None = None
    header_path: list[str] = []

    @property
    def col_key(self) -> int:
        return self.col_end


class Row(BaseModel):
    id: str
    index: int
    label: str
    cells: list[Cell]
    is_header: bool = False
    char_start: int = 0
    char_end: int = 0

    def value_at(self, col_key: int) -> Cell | None:
        for c in self.cells:
            if c.col_key == col_key:
                return c
        return None


class Table(BaseModel):
    id: str
    order: int
    rows: list[Row]
    scale: str | None = None  # thousands | millions | billions
    except_per_share: bool = False
    context_before: str = ""
    char_start: int = 0
    char_end: int = 0

    @property
    def data_rows(self) -> list[Row]:
        return [r for r in self.rows if not r.is_header]

    def row(self, row_id: str) -> Row:
        for r in self.rows:
            if r.id == row_id:
                return r
        raise KeyError(row_id)

    def value_columns(self) -> list[int]:
        keys = {c.col_key for r in self.data_rows for c in r.cells if c.number and c.number.value is not None}
        return sorted(keys)


class Image(BaseModel):
    order: int
    src: str
    alt: str = ""


class Document(BaseModel):
    sha256: str
    blocks: list[Block]
    tables: list[Table]
    images: list[Image]
    text: str

    def table(self, table_id: str) -> Table:
        for t in self.tables:
            if t.id == table_id:
                return t
        raise KeyError(table_id)


# ---------------------------------------------------------------- parsing


def parse_html(html: str | bytes) -> Document:
    raw = html if isinstance(html, bytes) else html.encode("utf-8")
    soup = BeautifulSoup(raw, "lxml")
    root = soup.body or soup
    b = _Builder()
    b.walk(root)
    b.finish()
    return Document(
        sha256=hashlib.sha256(raw).hexdigest(),
        blocks=b.blocks,
        tables=b.tables,
        images=b.images,
        text=b.text,
    )


class _Builder:
    def __init__(self) -> None:
        self.blocks: list[Block] = []
        self.tables: list[Table] = []
        self.images: list[Image] = []
        self.order = 0
        self.parts: list[str] = []
        self.pos = 0
        self.text = ""

    # ---- traversal
    def walk(self, node: Tag) -> None:
        pending_inline: list[NavigableString | Tag] = []
        for child in node.children:
            if isinstance(child, NavigableString):
                if child.__class__.__name__ in ("Comment", "Doctype", "ProcessingInstruction"):
                    continue
                pending_inline.append(child)
                continue
            if not isinstance(child, Tag) or child.name in ("script", "style", "head", "title"):
                continue
            if child.name == "img":
                self._flush_inline(pending_inline, node)
                pending_inline = []
                self.images.append(Image(order=self._next(), src=child.get("src", ""), alt=child.get("alt", "")))
                continue
            if child.name == "table":
                self._flush_inline(pending_inline, node)
                pending_inline = []
                self._table(child)
                continue
            if child.name in _TEXT_BLOCK_TAGS:
                self._flush_inline(pending_inline, node)
                pending_inline = []
                if _has_block_descendant(child):
                    self.walk(child)
                else:
                    self._emit_block(child.name, _collect_runs(child), child)
                    for img in child.find_all("img"):
                        self.images.append(Image(order=self._next(), src=img.get("src", ""), alt=img.get("alt", "")))
                continue
            if child.name == "br":
                self._flush_inline(pending_inline, node)
                pending_inline = []
                continue
            # inline element (span, font, b, a, ...) — may itself contain blocks
            if _has_block_descendant(child):
                self._flush_inline(pending_inline, node)
                pending_inline = []
                self.walk(child)
            else:
                pending_inline.append(child)
        self._flush_inline(pending_inline, node)

    def _flush_inline(self, nodes: list, parent: Tag) -> None:
        runs: list[Run] = []
        for n in nodes:
            if isinstance(n, NavigableString):
                runs.extend(_runs_from_string(n))
            else:
                runs.extend(_collect_runs(n))
        if any(r.text.strip() for r in runs):
            self._emit_block(parent.name or "div", runs, parent)

    def _emit_block(self, tag: str, runs: list[Run], el: Tag) -> None:
        text = normalize_ws("".join(r.text for r in runs))
        if not text:
            return
        kind: BlockKind = "heading" if tag in {"h1", "h2", "h3", "h4"} else "paragraph"
        if tag == "li" or _BULLET_RE.match(text):
            kind = "bullet"
        self.blocks.append(
            Block(id=f"b{len(self.blocks) + 1:04d}", order=self._next(), kind=kind, text=text, runs=runs, source_tag=tag)
        )

    def _table(self, el: Tag) -> None:
        trs = [tr for tr in el.find_all("tr") if tr.find_parent("table") is el]
        grid_rows = [_grid_row(tr) for tr in trs]
        if not _is_data_table(grid_rows):
            # layout table: each row becomes a block (bullets are often laid out this way)
            for tr in trs:
                runs: list[Run] = []
                for td in tr.find_all(["td", "th"]):
                    if td.find_parent("table") is not el:
                        continue
                    if runs:
                        runs.append(Run(text=" "))
                    runs.extend(_collect_runs(td))
                    for img in td.find_all("img"):
                        self.images.append(Image(order=self._next(), src=img.get("src", ""), alt=img.get("alt", "")))
                self._emit_block("tr", runs, tr)
            return
        self._data_table(grid_rows)

    def _data_table(self, grid_rows: list[list[tuple[str, int, int]]]) -> None:
        tid = f"t{len(self.tables) + 1:02d}"
        rows: list[Row] = []
        header_tokens: list[list[tuple[str, int, int]]] = []
        in_header = True  # header state machine: tables may repeat a header block (e.g. "Six Months Ended")
        for i, cells in enumerate(grid_rows):
            tokens = _merge_fragments(cells)
            if not tokens:
                continue
            label = ""
            value_tokens = tokens
            first = parse_number(tokens[0][0])
            if first.value is None and not first.is_dash:
                label, value_tokens = tokens[0][0], tokens[1:]
            parsed = [(t, parse_number(t[0])) for t in value_tokens]
            numeric = [p for _, p in parsed if p.value is not None and not looks_like_year(p)]
            rid = f"{tid}.r{i + 1:03d}"
            if numeric:
                in_header = False
            elif not in_header and (_PERIOD_RE.search(label) or any(p.value is None for _, p in parsed)):
                # a new header block after data: reset the header context for the rows below it
                in_header = True
                header_tokens = []
            if in_header and not numeric:
                header_tokens.append(tokens)
                rows.append(Row(id=rid, index=i, label=label, cells=[], is_header=True))
                continue
            out_cells = []
            for j, ((text, s, e), p) in enumerate(parsed):
                out_cells.append(
                    Cell(
                        id=f"{rid}.c{j + 1:02d}",
                        text=text,
                        col_start=s,
                        col_end=e,
                        number=p if p.value is not None else None,
                        header_path=_header_path(header_tokens, s, e),
                    )
                )
            rows.append(Row(id=rid, index=i, label=label, cells=out_cells, is_header=False))

        table_text = " ".join(r.label for r in rows) + " " + " ".join(t for h in header_tokens for t, _, _ in h)
        context = " ".join(b.text for b in self.blocks[-3:])
        scale_m = _SCALE_RE.search(table_text) or _SCALE_RE.search(context)
        self.tables.append(
            Table(
                id=tid,
                order=self._next(),
                rows=rows,
                scale=scale_m.group(1).lower() if scale_m else None,
                except_per_share=bool(re.search(r"except\s+(?:share\s+and\s+)?per[\s-]share", table_text + " " + context, re.I)),
                context_before=context[-400:],
            )
        )

    def _next(self) -> int:
        self.order += 1
        return self.order

    # ---- post-processing
    def finish(self) -> None:
        _classify_headlines(self.blocks)
        items: list[tuple[int, object]] = [(b.order, b) for b in self.blocks] + [(t.order, t) for t in self.tables]
        pieces: list[str] = []
        pos = 0
        for _, item in sorted(items, key=lambda x: x[0]):
            if isinstance(item, Block):
                item.char_start = pos
                pieces.append(item.text)
                pos += len(item.text)
                item.char_end = pos
                pieces.append("\n")
                pos += 1
            else:
                item.char_start = pos
                for r in item.rows:
                    line = " | ".join([r.label] + [c.text for c in r.cells])
                    r.char_start = pos
                    pieces.append(line)
                    pos += len(line)
                    r.char_end = pos
                    pieces.append("\n")
                    pos += 1
                item.char_end = pos
        self.text = "".join(pieces)


# ---------------------------------------------------------------- helpers


def _has_block_descendant(el: Tag) -> bool:
    return el.find(list(_TEXT_BLOCK_TAGS | {"table"})) is not None


def _style_of(el: Tag) -> tuple[bool, bool, float | None]:
    bold = italic = False
    size: float | None = None
    for anc in [el, *el.parents]:
        if not isinstance(anc, Tag):
            continue
        if anc.name in ("b", "strong"):
            bold = True
        if anc.name in ("i", "em"):
            italic = True
        style = anc.get("style", "") or ""
        if not bold and _BOLD_RE.search(style):
            bold = True
        if not italic and _ITALIC_RE.search(style):
            italic = True
        if size is None:
            m = _FONT_SIZE_RE.search(style)
            if m:
                v = float(m.group(1))
                size = v * 0.75 if m.group(2).lower() == "px" else v
    return bold, italic, size


def _runs_from_string(s: NavigableString) -> list[Run]:
    if not str(s):
        return []
    parent = s.parent if isinstance(s.parent, Tag) else None
    bold, italic, size = _style_of(parent) if parent else (False, False, None)
    return [Run(text=str(s), bold=bold, italic=italic, font_size_pt=size)]


def _collect_runs(el: Tag) -> list[Run]:
    runs: list[Run] = []
    for s in el.find_all(string=True):
        if s.__class__.__name__ in ("Comment", "Doctype"):
            continue
        if isinstance(s.parent, Tag) and s.parent.name in ("script", "style"):
            continue
        runs.extend(_runs_from_string(s))
    return runs


def _grid_row(tr: Tag) -> list[tuple[str, int, int]]:
    col = 0
    out = []
    for td in tr.find_all(["td", "th"]):
        if td.find_parent("tr") is not tr:
            continue
        try:
            span = max(1, int(td.get("colspan", 1)))
        except ValueError:
            span = 1
        out.append((normalize_ws(td.get_text(" ")), col, col + span - 1))
        col += span
    return out


def _merge_fragments(cells: list[tuple[str, int, int]]) -> list[tuple[str, int, int]]:
    """Merge EDGAR's split cells: '$' | '(1,234' | ')' -> '$(1,234)'.

    The returned grid range is that of the digit-bearing fragment, so values
    align by column across rows whether or not they carry '$' or ')'.
    """
    tokens: list[list] = []  # [text, start, end, has_digit]
    prefix = ""
    for text, s, e in cells:
        if not text:
            continue
        if text in _PREFIX_FRAGMENTS:
            prefix += text
            continue
        if text in _SUFFIX_FRAGMENTS and tokens:
            tokens[-1][0] += text
            continue
        tokens.append([prefix + text, s, e, any(ch.isdigit() for ch in text)])
        prefix = ""
    return [(t, s, e) for t, s, e, _ in tokens]


def _is_data_table(grid_rows: list[list[tuple[str, int, int]]]) -> bool:
    numeric_rows = 0
    for cells in grid_rows:
        tokens = _merge_fragments(cells)
        vals = [parse_number(t) for t, _, _ in tokens[1:]]
        if any(v.value is not None and not looks_like_year(v) for v in vals):
            numeric_rows += 1
    return numeric_rows >= 2


def _header_path(header_tokens: list[list[tuple[str, int, int]]], s: int, e: int) -> list[str]:
    path = []
    for row in header_tokens:
        for text, hs, he in row:
            if hs <= e and s <= he and text:
                path.append(text)
                break
    return path


def _classify_headlines(blocks: list[Block]) -> None:
    """Blocks before the first body paragraph that are emphasised count as headline.

    Heuristic, documented: body paragraph = >= 200 chars and not mostly bold.
    Emphasised = mostly bold, or larger than the median font, or ALL CAPS.
    """
    # ADR-027: plain-styled sub-headline lines (Aviat) are still headline: everything non-bullet above
    # the first body paragraph counts. Emphasis no longer gates it.
    for b in blocks:
        if len(b.text) >= 200 and b.bold_fraction < 0.5:
            break
        if b.kind in ("paragraph", "heading"):
            b.kind = "headline"
