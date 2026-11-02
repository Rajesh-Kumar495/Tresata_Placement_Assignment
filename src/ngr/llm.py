"""Bounded LLM client (architecture §7, ADR-008, ADR-015, ADR-019).

* OpenAI-compatible endpoint (GOEDEL_URL / GOEDEL_API_KEY / LLM_MODEL_ID from .env).
* Every call is content-addressed: key = sha256(model, messages, params, schema).
  Responses are recorded to eval/cassettes/ so runs replay byte-identically with
  no network and no API key (mode="replay").
* Output must be JSON matching a Pydantic schema; one repair retry carrying the
  validation error, then the caller gets a SchemaFailure (-> NEEDS_REVIEW).
* temperature=0, k=1. Escalation sampling is the caller's decision (ADR-015).
"""

from __future__ import annotations

import hashlib
import json
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, TypeVar

import httpx
from pydantic import BaseModel, ValidationError

from .config import PROJECT_ROOT, llm_settings

CASSETTES = PROJECT_ROOT / "eval" / "cassettes"
T = TypeVar("T", bound=BaseModel)
Mode = Literal["live", "replay", "record"]  # record = use cache if present, else call and store


class SchemaFailure(RuntimeError):
    def __init__(self, step: str, error: str, raw: str):
        super().__init__(f"{step}: schema failure after repair: {error}")
        self.step, self.error, self.raw = step, error, raw


@dataclass
class CallRecord:
    call_id: str
    step: str
    model: str
    cache_hit: bool
    schema_valid: bool
    repaired: bool
    latency_ms: int
    prompt_tokens: int
    completion_tokens: int


@dataclass
class LLMClient:
    mode: Mode = "record"
    cassette_dir: Path = CASSETTES
    min_interval_s: float = 0.2
    calls: list[CallRecord] = field(default_factory=list)
    _last: float = 0.0
    _settings: tuple[str, str, str] | None = None

    @property
    def model(self) -> str:
        if self._settings is None:
            if self.mode == "replay":
                from .config import load_env
                import os

                load_env()
                return os.environ.get("LLM_MODEL_ID", "replay")
            self._settings = llm_settings()
        return self._settings[2]

    # ------------------------------------------------------------ public
    def complete_json(self, step: str, system: str, user: str, schema: type[T], *, temperature: float = 0.0, max_tokens: int = 4000) -> T:
        messages = [{"role": "system", "content": system}, {"role": "user", "content": user}]
        raw, rec = self._call(step, messages, temperature, max_tokens, schema.__name__)
        try:
            out = schema.model_validate(_extract_json(raw))
            self.calls.append(rec)
            return out
        except (ValidationError, ValueError) as e:
            err = _short_error(e)
        repair = messages + [
            {"role": "assistant", "content": raw},
            {"role": "user", "content": f"Your previous reply did not match the required JSON schema: {err}\nReturn the corrected JSON object only."},
        ]
        raw2, rec2 = self._call(step + ":repair", repair, temperature, max_tokens, schema.__name__)
        rec2.repaired = True
        try:
            out = schema.model_validate(_extract_json(raw2))
            self.calls.extend([rec, rec2])
            return out
        except (ValidationError, ValueError) as e2:
            rec2.schema_valid = False
            self.calls.extend([rec, rec2])
            raise SchemaFailure(step, _short_error(e2), raw2) from e2

    # ------------------------------------------------------------ internals
    def _call(self, step, messages, temperature, max_tokens, schema_name) -> tuple[str, CallRecord]:
        model = self.model
        payload = {"model": model, "messages": messages, "temperature": temperature, "max_tokens": max_tokens, "schema": schema_name}
        key = hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
        path = self.cassette_dir / f"{key[:2]}" / f"{key}.json"
        if self.mode in ("replay", "record") and path.exists():
            c = json.loads(path.read_text(encoding="utf-8"))
            return c["response_text"], CallRecord(key[:16], step, c["model"], True, True, False, 0, c["usage"].get("prompt_tokens", 0), c["usage"].get("completion_tokens", 0))
        if self.mode == "replay":
            raise RuntimeError(f"replay mode: no cassette for {step} ({key[:12]})")

        api_key, url, _ = self._settings or llm_settings()
        body = {"model": model, "messages": messages, "temperature": temperature, "max_tokens": max_tokens, "response_format": {"type": "json_object"}}
        t0 = time.monotonic()
        data = self._post(url + "/chat/completions", body, api_key)
        latency = int((time.monotonic() - t0) * 1000)
        text = data["choices"][0]["message"]["content"] or ""
        usage = data.get("usage") or {}
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(
                {"key": key, "step": step, "model": data.get("model", model), "request": {"messages": messages, "temperature": temperature, "max_tokens": max_tokens, "schema": schema_name},
                 "response_text": text, "usage": usage, "latency_ms": latency},
                indent=1, ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        return text, CallRecord(key[:16], step, data.get("model", model), False, True, False, latency, usage.get("prompt_tokens", 0), usage.get("completion_tokens", 0))

    def _post(self, url: str, body: dict, api_key: str) -> dict:
        for attempt in range(5):
            wait = self.min_interval_s - (time.monotonic() - self._last)
            if wait > 0:
                time.sleep(wait)
            self._last = time.monotonic()
            try:
                r = httpx.post(url, json=body, headers={"Authorization": f"Bearer {api_key}"}, timeout=180)
            except httpx.TransportError:
                time.sleep(2**attempt)
                continue
            if r.status_code == 429 or r.status_code >= 500:
                retry_after = r.headers.get("retry-after")
                time.sleep(float(retry_after) if retry_after and retry_after.replace(".", "").isdigit() else 2**attempt)
                continue
            r.raise_for_status()
            return r.json()
        raise RuntimeError(f"LLM endpoint failed after retries: {url}")


def _extract_json(text: str):
    t = text.strip()
    m = re.search(r"```(?:json)?\s*(.*?)```", t, re.S)
    if m:
        t = m.group(1).strip()
    if not t.startswith(("{", "[")):
        i = t.find("{")
        t = t[i:] if i >= 0 else t
    return json.loads(t)


def _short_error(e: Exception) -> str:
    return str(e).replace("\n", " ")[:600]
