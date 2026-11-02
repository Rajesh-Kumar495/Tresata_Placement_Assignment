"""Adjudication of findings on the 10 real releases that no gold label covers.

    python -I -m ngr.adjudicate  -> eval/results/adjudication.md (+ .json)

Labels were assigned by the AI assistant after reading the source text and the SEC
correspondence, NOT by a qualified reviewer. They are recorded per finding with a
reason so a human can spot-check them. Categories:
  TP         supportable under the rule text and consistent with the SEC's comments on that issuer
  DEBATABLE  a defensible reading that a reviewer could reasonably dismiss
  FP         wrong (bug, wrong measure, or not a non-GAAP issue)
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter

from .config import PROJECT_ROOT

RESULTS = PROJECT_ROOT / "eval" / "results"

# (doc prefix, rule, subject regex) -> (label, reason). First match wins.
RULES: list[tuple[str, str, str, str, str]] = [
    ("A02", "R-RECON-TIEOUT", ".", "TP", "Q11 diagnostic: the subtraction really is unlabelled; NEEDS_REVIEW naming the row is the designed outcome"),
    ("A01", "R-PROM-HEADLINE", "Adjusted EBITDA", "TP", "SEC c2 named adjusted EBITDA in the headline as well (gold anchor covered only the EPS line)"),
    ("A02", "R-PROM-HEADLINE", ".", "TP", "Same header block the SEC raised in c4; guidance/target lines repeat the pattern"),
    ("A02", "R-NORMAL-OPEX", ".", "TP", "SEC c9 asked about exactly these adjustments (CEO separation, acquisition, non-recurring)"),
    ("A05", "R-PROM-ORDER", ".*", "FP_IF_TABLE", ""),  # resolved below by message
    (".", "R-PROM-ORDER", "record|^Adjusted EBITDA$", "TP", "Highlight bullet presents (record) Adjusted EBITDA with no net income in the list (102.10(a))"),
    ("A04", "R-PROM-LANGUAGE", ".", "TP", "CEO quote characterises adjusted EBITDA as stronger than expected; SEC c2b raised non-GAAP discussion prominence"),
    ("A05", "R-RECON-PRESENT", "Margin|Modified", "TP", "SEC c9/c10: modified metrics reconciled only on website; margin without GAAP margin"),
    ("A05", "R-NORMAL-OPEX", "Special Items", "TP", "SEC (10-K comment 2) asked Lumen to consider 100.01 for special items"),
    ("A05", "R-FWD-EXCEPTION", "Adjusted EBITDA|Free Cash Flow", "TP", "Outlook table gives non-GAAP guidance; no unreasonable-efforts disclosure found in the release text"),
    ("A06", "R-RECON-PRESENT", "margin", "TP", "Adjusted EBIT/EBITDA margins without GAAP margins; SEC c3 raised the same class of measures"),
    ("A06", "R-RECON-START-GAAP", ".", "TP", "Reconciliations start from adjusted EBITDA; SEC c2/c3"),
    ("A06", "R-PROM-ORDER", "Free cash flow|^Net debt$", "DEBATABLE", "Cash-flow/debt measure in a list without its GAAP comparable; commonly accepted presentation"),
    ("A06", "R-PROM-ORDER", ".", "TP", "Adjusted measures listed without/before GAAP comparables; SEC c3 asked for equal prominence across these measures"),
    ("B03", "R-FWD-EXCEPTION", ".", "TP", "Adjusted guidance with no reconciliation and no unreasonable-efforts disclosure (102.10(b) bullet 3)"),
    ("A03", "R-RECON-PRESENT", "Net debt", "FP", "Components given inline (cash $182m, borrowings $1.71bn -> net debt $1.53bn): a clearly understandable reconciliation"),
    ("A06", "R-RECON-PRESENT", "tax rate", "FP", "Table shows as-reported and adjusted effective tax rates side by side"),
    ("A06", "R-NORMAL-OPEX", "^Adjustments$", "FP", "Tax adjustment, not an operating expense"),
    ("A01", "R-NORMAL-OPEX", "Other expense", "FP", "Non-operating item; 100.01 concerns operating expenses"),
    ("A05", "R-NORMAL-OPEX", "Real estate", "FP", "Real-estate transaction gains/losses are not operating expenses"),
    ("B01", "R-RECON-PRESENT", "adjusted earnings", "FP", "Lexicon fragment of 'Adjusted earnings before interest, tax...' (= Adjusted EBITDA, which is reconciled)"),
    ("B02", "R-RECON-PRESENT", "run-rate", "FP", "Forward-looking run-rate; the release discloses why no reconciliation is provided"),
    ("B02", "R-PROM-LANGUAGE", ".", "FP", "'significantly' states a magnitude; not the 'record/exceptional' characterisation in 102.10(a)"),
    ("A05", "R-FWD-EXCEPTION", "Net Cash Interest", "DEBATABLE", "Unclear whether 'net cash interest' is a non-GAAP measure"),
    (".", "R-RECON-START-GAAP", ".", "DEBATABLE", "Chained from a measure reconciled to GAAP elsewhere; routed to NEEDS_REVIEW by design"),
    (".", "R-NORMAL-OPEX", ".", "DEBATABLE", "Restructuring / M&A / ERP / transformation exclusions: 100.01's 'occasionally, at irregular intervals' supports a flag, but these are widely accepted adjustments"),
    (".", "R-RECON-PRESENT", ".", "DEBATABLE", "Net debt / net cash / prior-year adjusted margin without an explicit reconciliation schedule"),
    (".", "R-PROM-ORDER", ".", "DEBATABLE", "Forward guidance or net debt in a bullet without the GAAP comparable"),
]


def classify(doc: str, f: dict) -> tuple[str, str]:
    for dp, rule, subj, label, reason in RULES:
        if (dp == "." or doc.startswith(dp)) and f["rule"] == rule and re.search(subj, f["subject"], re.I):
            if label == "FP_IF_TABLE":
                if f["message"].startswith("Table"):
                    return "FP", "Special-items detail table, not a presentation of a non-GAAP measure"
                return "DEBATABLE", "Net debt bullet without total debt"
            return label, reason
    return "DEBATABLE", "unclassified"


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    r = json.loads((RESULTS / "full_eval.json").read_text(encoding="utf-8"))
    rows = []
    for d, g in r["docs"].items():
        for x in g["extras"]:
            label, reason = classify(d, x)
            rows.append({"doc": d, **x, "label": label, "reason": reason})
    gold_hits = sum(e["result"] in ("hit", "weak") for g in r["docs"].values() for e in g["expected"] if e["expected"] != "NOT_EVALUATED")
    c = Counter(x["label"] for x in rows)
    total = len(rows) + gold_hits
    summary = {
        "findings_on_real_docs": total,
        "matched_to_SEC_gold": gold_hits,
        "unlabelled": len(rows),
        "unlabelled_TP": c["TP"], "unlabelled_DEBATABLE": c["DEBATABLE"], "unlabelled_FP": c["FP"],
        "precision_strict": round((gold_hits + c["TP"]) / total, 3),
        "precision_lenient": round((gold_hits + c["TP"] + c["DEBATABLE"]) / total, 3),
    }
    by_rule = {}
    for x in rows:
        by_rule.setdefault(x["rule"], Counter())[x["label"]] += 1
    (RESULTS / "adjudication.json").write_text(json.dumps({"summary": summary, "findings": rows}, indent=1), encoding="utf-8")
    L = ["# Adjudication of unlabelled findings on the 10 real releases", "",
         "**Adjudicated by the AI assistant**, not a qualified reviewer, after reading the source text and SEC correspondence. Spot-check before relying on it.", "",
         f"- Findings (FLAG/NEEDS_REVIEW) on real releases: **{total}**, of which {gold_hits} match an SEC-raised gold label",
         f"- Unlabelled: {len(rows)}: **TP {c['TP']} · DEBATABLE {c['DEBATABLE']} · FP {c['FP']}**",
         f"- Precision strict (gold + TP): **{summary['precision_strict']:.0%}** · lenient (+ debatable): **{summary['precision_lenient']:.0%}**", "",
         "| Rule | TP | DEBATABLE | FP |", "|---|---|---|---|"]
    for k, v in sorted(by_rule.items()):
        L.append(f"| {k} | {v['TP']} | {v['DEBATABLE']} | {v['FP']} |")
    L += ["", "| Doc | Rule | Verdict | Subject | Label | Reason |", "|---|---|---|---|---|---|"]
    for x in rows:
        L.append(f"| {x['doc'][:3]} | {x['rule']} | {x['verdict']} | {x['subject'][:40]} | **{x['label']}** | {x['reason']} |")
    (RESULTS / "adjudication.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=1))
    for k, v in sorted(by_rule.items()):
        print(k, dict(v))
    return 0


if __name__ == "__main__":
    sys.exit(main())
