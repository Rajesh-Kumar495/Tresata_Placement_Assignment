"""Minimal EDGAR fetcher.

Refuses to run without SEC_EDGAR_USER_AGENT (ADR-019). Stores raw bytes
immutably with their sha256 so every later step can cite exact input bytes.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass
from pathlib import Path

import httpx

from .config import PROJECT_ROOT, edgar_user_agent

RAW_DIR = PROJECT_ROOT / "data" / "raw"
_MIN_INTERVAL_S = 0.15  # stay well under the SEC's 10 requests/second limit
_last_request = 0.0


@dataclass(frozen=True)
class Fetched:
    url: str
    path: Path
    sha256: str
    content_type: str


def _throttle() -> None:
    global _last_request
    wait = _MIN_INTERVAL_S - (time.monotonic() - _last_request)
    if wait > 0:
        time.sleep(wait)
    _last_request = time.monotonic()


def fetch(url: str, dest_name: str, *, client: httpx.Client | None = None) -> Fetched:
    """Download `url` to data/raw/<dest_name> and write a sidecar .meta.json."""
    headers = {"User-Agent": edgar_user_agent(), "Accept-Encoding": "gzip, deflate"}
    own = client is None
    client = client or httpx.Client(timeout=30.0, follow_redirects=True)
    try:
        for attempt in range(4):
            _throttle()
            resp = client.get(url, headers=headers)
            if resp.status_code in (429, 503):
                time.sleep(2**attempt)
                continue
            resp.raise_for_status()
            break
        else:
            resp.raise_for_status()
    finally:
        if own:
            client.close()

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    path = RAW_DIR / dest_name
    path.write_bytes(resp.content)
    digest = hashlib.sha256(resp.content).hexdigest()
    ctype = resp.headers.get("content-type", "")
    meta = {"url": url, "sha256": digest, "content_type": ctype, "bytes": len(resp.content)}
    path.with_suffix(path.suffix + ".meta.json").write_text(json.dumps(meta, indent=2))
    return Fetched(url=url, path=path, sha256=digest, content_type=ctype)
