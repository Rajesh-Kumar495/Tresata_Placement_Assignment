"""Verbatim rule text for the rule pack (ADR-003): extracted from fetched primary sources, hashed.

    python -I -m ngr.rule_sources     # rebuilds rules/excerpts.yaml from data/rules_src/

Knowledge lives here, not in the model: judges receive these exact excerpts, and
every finding cites the excerpt key + the source sha256 it was taken from.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from datetime import date

import yaml
from bs4 import BeautifulSoup

from .config import PROJECT_ROOT

SRC = PROJECT_ROOT / "data" / "rules_src"
OUT = PROJECT_ROOT / "rules" / "excerpts.yaml"
# Real question headings look like "Question 100.01 Question:" or "Question 102.10(a):".
# Cross-references ("See Question 102.10(c).") must not split the text.
_Q = re.compile(r"(?=Question (1\d\d\.\d\d(?:\([abc]\))?)(?::| Question ?:))")


def _text(name: str) -> tuple[str, str]:
    raw = (SRC / name).read_bytes()
    t = re.sub(r"\s+", " ", BeautifulSoup(raw, "lxml", from_encoding="utf-8").get_text(" "))
    t = t.replace(" 's ", "'s ")
    return t, hashlib.sha256(raw).hexdigest()


def cdi_questions() -> tuple[dict[str, str], str]:
    t, sha = _text("cdi_nongaap.html")
    parts = _Q.split(t)
    out: dict[str, str] = {}
    # split with a capture group yields [pre, key, body, key, body, ...]
    for k, body in zip(parts[1::2], parts[2::2]):
        seg = body.strip()
        seg = re.sub(r"\s*(Back to top|Section 10\d\..*)$", "", seg)[:3000]
        if len(seg) > len(out.get(k, "")):
            out[k] = seg
    return out, sha


def regsk_10e1() -> tuple[dict[str, str], str]:
    t, sha = _text("regsk_229_10.html")
    i = t.find("Use of non-GAAP financial measures in Commission filings")
    seg = t[i : i + 6000] if i >= 0 else ""
    pieces = {}
    for key, start, end in [
        ("10(e)(1)(i)", "(1) Whenever one or more non-GAAP", "(ii) A registrant must not"),
        ("10(e)(1)(ii)", "(ii) A registrant must not", "(iii)"),
    ]:
        a = seg.find(start)
        b = seg.find(end, a + len(start)) if a >= 0 else -1
        if a >= 0:
            pieces[key] = seg[a : b if b > a else a + 2500].strip()
    return pieces, sha


def build() -> dict:
    q, cdi_sha = cdi_questions()
    s, sk_sha = regsk_10e1()
    wanted = ["100.01", "100.02", "100.03", "100.04", "100.05", "100.06", "102.03", "102.05", "102.07", "102.10(a)", "102.10(b)", "102.10(c)", "102.11", "103.01", "103.02", "104.01", "104.06"]
    excerpts = {f"cdi:{k}": q[k] for k in wanted if k in q}
    excerpts.update({f"regsk:{k}": v for k, v in s.items()})
    meta = {
        "extracted": str(date.today()),
        "sources": {
            "cdi": {"file": "data/rules_src/cdi_nongaap.html", "sha256": cdi_sha, "page_last_updated": "2022-12-13"},
            "regsk": {"file": "data/rules_src/regsk_229_10.html", "sha256": sk_sha},
        },
        "missing": [k for k in wanted if k not in q],
    }
    doc = {"meta": meta, "excerpts": excerpts}
    OUT.write_text(yaml.safe_dump(doc, sort_keys=False, allow_unicode=True, width=120), encoding="utf-8")
    return doc


def load() -> dict[str, str]:
    return yaml.safe_load(OUT.read_text(encoding="utf-8"))["excerpts"]


if __name__ == "__main__":
    d = build()
    print(json.dumps({"n": len(d["excerpts"]), "missing": d["meta"]["missing"], "keys": list(d["excerpts"])}, indent=1))
    sys.exit(0)
