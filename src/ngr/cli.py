"""Reviewer CLI: the human-in-the-loop checkpoints as files + commands (ADR-018).

    python -I -m ngr.cli review  <doc_id | path.htm> [--out DIR] [--mode record|replay|live]
        -> DIR/report.html, review.json, hc1_proposal.json, hc2_dispositions.json

    python -I -m ngr.cli hc1     <doc_id | path.htm> <hc1_confirmed.json> [--out DIR] [--reviewer NAME]
        HC1: re-run the rules on the reviewer-confirmed measure list (edit hc1_proposal.json:
        set "confirmed": true/false, fix kind/per_share/comparable_gaap, add missing measures).

    python -I -m ngr.cli hc2     <DIR> --reviewer NAME
        HC2: validate hc2_dispositions.json (every FLAG/NEEDS_REVIEW needs accept|reject|edit,
        and reject needs a note) and append a signed record to DIR/audit.jsonl.
"""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from .corpus import load_document, raw_path
from .docmodel import parse_html
from .llm import LLMClient
from .report import write as write_report
from .review import review


def _load(target: str):
    p = Path(target)
    if p.exists():
        return p.stem, parse_html(p.read_bytes())
    if raw_path(target).exists():
        return target, load_document(target)
    raise SystemExit(f"not a file or known doc_id: {target}")


def _arg(argv, flag, default=None):
    return argv[argv.index(flag) + 1] if flag in argv else default


def _audit(out: Path, event: dict) -> None:
    event["at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with open(out / "audit.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")


def cmd_review(argv) -> int:
    doc_id, doc = _load(argv[0])
    out = Path(_arg(argv, "--out", f"runs/review_{doc_id}"))
    llm = LLMClient(mode=_arg(argv, "--mode", "record"))
    rv = review(doc_id, doc, llm)
    write_report(rv, doc, out, doc_id, llm.model)
    proposal = [{"name": m.name, "kind": m.kind, "per_share": m.per_share, "forward_looking": m.forward_looking,
                 "comparable_gaap": m.comparable_gaap, "evidence": [s.ref for s in m.mentions], "confirmed": None} for m in rv.inventory.measures]
    (out / "hc1_proposal.json").write_text(json.dumps({"doc_id": doc_id, "doc_sha256": doc.sha256, "measures": proposal,
                                                       "also_review": rv.inventory.unexplained_candidates}, indent=1), encoding="utf-8")
    _audit(out, {"event": "review", "doc_sha256": doc.sha256, "model": llm.model, "llm_calls": len(llm.calls)})
    print(f"memo: {out / 'report.html'}  ({sum(f.verdict == 'FLAG' for f in rv.findings)} FLAG, {sum(f.verdict == 'NEEDS_REVIEW' for f in rv.findings)} NEEDS_REVIEW)")
    return 0


def cmd_hc1(argv) -> int:
    doc_id, doc = _load(argv[0])
    data = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    measures = data["measures"] if isinstance(data, dict) else data
    undecided = [m["name"] for m in measures if m.get("confirmed") is None]
    if undecided:
        raise SystemExit(f"HC1 incomplete: set confirmed true/false for {undecided}")
    out = Path(_arg(argv, "--out", f"runs/review_{doc_id}"))
    llm = LLMClient(mode=_arg(argv, "--mode", "record"))
    rv = review(doc_id, doc, llm, hc1=measures)
    write_report(rv, doc, out, f"{doc_id} (HC1 confirmed)", llm.model)
    _audit(out, {"event": "hc1_confirmed", "reviewer": _arg(argv, "--reviewer", "unknown"), "doc_sha256": doc.sha256,
                 "hc1_sha256": hashlib.sha256(Path(argv[1]).read_bytes()).hexdigest(), "measures": [m["name"] for m in measures if m.get("confirmed")]})
    print(f"memo (HC1 confirmed): {out / 'report.html'}")
    return 0


def cmd_hc2(argv) -> int:
    out = Path(argv[0])
    reviewer = _arg(argv, "--reviewer")
    if not reviewer:
        raise SystemExit("--reviewer is required: dispositions are signed")
    p = out / "hc2_dispositions.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    problems = []
    for i, f in enumerate(data["findings"]):
        if f.get("disposition") not in ("accept", "reject", "edit"):
            problems.append(f"#{i} {f['rule_id']}: disposition must be accept|reject|edit")
        elif f["disposition"] == "reject" and not (f.get("reviewer_note") or "").strip():
            problems.append(f"#{i} {f['rule_id']}: a rejection needs a reviewer_note")
    if problems:
        print("\n".join(problems))
        return 1
    _audit(out, {"event": "hc2_signed", "reviewer": reviewer, "dispositions_sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
                 "counts": {d: sum(f["disposition"] == d for f in data["findings"]) for d in ("accept", "reject", "edit")}})
    print(f"HC2 recorded in {out / 'audit.jsonl'}")
    return 0


def main(argv: list[str]) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if len(argv) < 3 or argv[1] not in ("review", "hc1", "hc2"):
        print(__doc__)
        return 2
    return {"review": cmd_review, "hc1": cmd_hc1, "hc2": cmd_hc2}[argv[1]](argv[2:])


if __name__ == "__main__":
    sys.exit(main(sys.argv))
