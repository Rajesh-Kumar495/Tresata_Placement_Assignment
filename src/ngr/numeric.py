"""Deterministic parsing of numbers as printed in earnings-release tables.

Handles the conventions seen in EDGAR Ex 99.1 tables:
  (1,234)  -> -1234        accounting negative
  $(1,234) -> -1234        currency prefix
  —, –, -  -> 0            dash means nil
  1,234(a) -> 1234         trailing footnote marker, recorded separately
  12.5%    -> 12.5, percent
  −1,234   -> -1234        unicode minus

The printed precision (`decimals`) is kept because tie-out tolerance is based
on the unit of the last printed digit, not on the caption scale (ADR-014).
"""

from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation

from pydantic import BaseModel

DASHES = {"—", "–", "-", "‒", "―"}
_WS = re.compile(r"[\s ​  ]+")
# trailing footnote marker such as (a), (1), (12), *, ** or a superscript digit
_FOOTNOTE = re.compile(r"^(?P<num>.*?[\d)%])\s*(?P<fn>\((?:[a-zA-Z]|\d{1,2})\)|\*{1,3}|[¹²³⁴⁵⁶⁷⁸⁹⁰]+)$")
_NUMBER = re.compile(r"^\d{1,3}(?:,\d{3})*(?:\.\d+)?$|^\d+(?:\.\d+)?$|^\.\d+$")


class ParsedNumber(BaseModel):
    raw: str
    value: Decimal | None
    decimals: int = 0
    is_percent: bool = False
    is_currency: bool = False
    is_dash: bool = False
    footnotes: list[str] = []

    @property
    def unit(self) -> Decimal:
        """Value of one unit in the last printed digit, e.g. 0.1 for '12.3'."""
        return Decimal(1).scaleb(-self.decimals)


def normalize_ws(text: str) -> str:
    return _WS.sub(" ", text).strip()


def parse_number(raw: str) -> ParsedNumber:
    """Parse one printed table value. Returns value=None for non-numeric text."""
    text = normalize_ws(raw)
    out = ParsedNumber(raw=raw, value=None)
    if not text:
        return out
    if text in DASHES or text in {"$—", "$ —", "$-", "$ -"}:
        return ParsedNumber(raw=raw, value=Decimal(0), is_dash=True, is_currency=text.startswith("$"))

    footnotes: list[str] = []
    m = _FOOTNOTE.match(text)
    # "(12)" alone is a negative number, not a footnote: only strip when digits precede it
    if m and m.group("num").strip() not in {"", "$", "("} and not _is_paren_negative(text):
        footnotes.append(m.group("fn").strip("()"))
        text = m.group("num").strip()

    negative = False
    if text.startswith("−"):
        text = "-" + text[1:]
    is_currency = "$" in text
    text = text.replace("$", "").replace(" ", "")
    is_percent = text.endswith("%") or text.endswith("%)")
    text = text.replace("%", "")
    if text.startswith("(") and text.endswith(")"):
        negative, text = True, text[1:-1]
    elif text.startswith("(") and not text.endswith(")"):
        # EDGAR splits ")" into the next cell; the caller merges fragments,
        # but tolerate a lone opening parenthesis as a negative marker.
        negative, text = True, text[1:]
    if text.startswith("-"):
        negative, text = (not negative), text[1:]
    if not _NUMBER.match(text):
        return out

    try:
        value = Decimal(text.replace(",", ""))
    except InvalidOperation:  # pragma: no cover - regex already guards
        return out
    decimals = len(text.split(".")[1]) if "." in text else 0
    return ParsedNumber(
        raw=raw,
        value=-value if negative else value,
        decimals=decimals,
        is_percent=is_percent,
        is_currency=is_currency,
        footnotes=footnotes,
    )


def _is_paren_negative(text: str) -> bool:
    t = text.replace("$", "").replace(" ", "").rstrip("%")
    return bool(re.fullmatch(r"\(\d[\d,]*(?:\.\d+)?\)", t))


def looks_like_year(p: ParsedNumber) -> bool:
    return (
        p.value is not None
        and p.decimals == 0
        and not p.is_currency
        and not p.is_percent
        and "," not in p.raw
        and 1990 <= p.value <= 2100
    )
