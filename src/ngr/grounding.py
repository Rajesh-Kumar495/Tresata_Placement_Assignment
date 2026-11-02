"""Grounding gate (architecture §7.3, ADR-004).

A quote is accepted only if it occurs *exactly* in the document after
normalising whitespace and typographic quotes/dashes. No fuzzy matching: fuzzy
matching would re-admit paraphrased or invented evidence, which is what this
gate exists to stop. Normalisation is a 1:1 character mapping on the document
side, so offsets into Document.text stay valid.
"""

from __future__ import annotations

import re

from pydantic import BaseModel

from .docmodel import Document

_TYPO = str.maketrans({"‘": "'", "’": "'", "“": '"', "”": '"', "–": "-", "—": "-", " ": " "})


class Span(BaseModel):
    ref: str  # block id (b0001) or table row id (t07.r004)
    quote: str
    char_start: int
    char_end: int


def _norm_quote(q: str) -> str:
    return re.sub(r"\s+", " ", q.translate(_TYPO)).strip()


class Grounder:
    def __init__(self, doc: Document):
        self.doc = doc
        self.hay = doc.text.translate(_TYPO)  # same length as doc.text
        self.refs: list[tuple[int, int, str]] = [(b.char_start, b.char_end, b.id) for b in doc.blocks]
        for t in doc.tables:
            self.refs += [(r.char_start, r.char_end, r.id) for r in t.rows]
        self.refs.sort()
        self._by_id = {rid: (s, e) for s, e, rid in self.refs}

    def ground(self, quote: str, ref_hint: str | None = None) -> Span | None:
        q = _norm_quote(quote)
        if len(q) < 3:
            return None
        if ref_hint in self._by_id:  # prefer the location the model pointed at
            s, e = self._by_id[ref_hint]
            i = self.hay.find(q, s, e)
            if i >= 0:
                return Span(ref=ref_hint, quote=self.doc.text[i : i + len(q)], char_start=i, char_end=i + len(q))
        i = self.hay.find(q)
        if i < 0:
            return None
        return Span(ref=self.ref_at(i) or "doc", quote=self.doc.text[i : i + len(q)], char_start=i, char_end=i + len(q))

    def ref_at(self, offset: int) -> str | None:
        for s, e, rid in self.refs:
            if s <= offset < e:
                return rid
        return None
