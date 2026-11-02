"""Corpus download + gold-label anchor validation (build step 4, ADR-020).

    python -I -m ngr.corpus fetch      # download every gold label's Ex 99.1 into data/raw/
    python -I -m ngr.corpus validate   # check anchors against the parsed downloaded text

The manifest (eval/corpus_manifest.json) is committed: it pins the sha256 of
each input so every later result can cite exact bytes.
"""

from __future__ import annotations

import json
import sys

from .config import PROJECT_ROOT
from .docmodel import Document, parse_html
from .labels import load_labels, missing_anchors

MANIFEST = PROJECT_ROOT / "eval" / "corpus_manifest.json"
RAW = PROJECT_ROOT / "data" / "raw"


def raw_path(doc_id: str):
    return RAW / f"{doc_id}.htm"


def load_document(doc_id: str) -> Document:
    return parse_html(raw_path(doc_id).read_bytes())


def fetch_all() -> dict:
    from .edgar import fetch

    manifest = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}
    for label in load_labels():
        if label.synthetic:
            continue
        got = fetch(label.source.exhibit_url, raw_path(label.doc_id).name)
        prev = manifest.get(label.doc_id, {}).get("sha256")
        if prev and prev != got.sha256:
            print(f"WARNING {label.doc_id}: sha256 changed since last fetch ({prev[:12]} -> {got.sha256[:12]})")
        manifest[label.doc_id] = {"url": got.url, "sha256": got.sha256, "content_type": got.content_type, "bytes": got.path.stat().st_size}
        print(f"fetched {label.doc_id}: {got.path.stat().st_size:,} bytes sha256={got.sha256[:12]}")
    MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True))
    return manifest


def validate_all() -> int:
    bad = 0
    for label in load_labels():
        if label.synthetic:
            continue
        p = raw_path(label.doc_id)
        if not p.exists():
            print(f"MISSING  {label.doc_id}: not downloaded")
            bad += 1
            continue
        doc = parse_html(p.read_bytes())
        missing = missing_anchors(label, doc.text)
        n = len(label.anchors())
        status = "OK      " if not missing else "FAIL    "
        print(f"{status}{label.doc_id}: {n - len(missing)}/{n} anchors found; {len(doc.blocks)} blocks, {len(doc.tables)} tables, {len(doc.images)} images")
        for m in missing:
            print(f"           missing: {m!r}")
        bad += bool(missing)
    return bad


def main(argv: list[str]) -> int:
    cmd = argv[1] if len(argv) > 1 else "validate"
    if cmd == "fetch":
        fetch_all()
        return 0
    if cmd == "validate":
        return 1 if validate_all() else 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
