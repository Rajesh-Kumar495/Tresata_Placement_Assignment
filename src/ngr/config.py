"""Environment-based configuration (ADR-019).

Nothing personal or secret lives in code or git. Values come from the process
environment, optionally loaded from a git-ignored `.env` at the project root.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class ConfigError(RuntimeError):
    """A required setting is missing. The message says which and where to set it."""


def load_env() -> None:
    # override=False: an explicitly exported variable wins over the .env file.
    load_dotenv(PROJECT_ROOT / ".env", override=False)


def require(name: str, purpose: str) -> str:
    load_env()
    value = os.environ.get(name, "").strip()
    if not value:
        raise ConfigError(
            f"{name} is not set. It is required for {purpose}. "
            f"Add it to {PROJECT_ROOT / '.env'} (see .env.example) or export it."
        )
    return value


def edgar_user_agent() -> str:
    return require("SEC_EDGAR_USER_AGENT", "EDGAR downloads (SEC fair-access policy)")


def llm_settings() -> tuple[str, str, str]:
    """(api_key, base_url, model_id) for the OpenAI-compatible Goedel endpoint."""
    key = require("GOEDEL_API_KEY", "LLM calls")
    url = require("GOEDEL_URL", "LLM calls (OpenAI-compatible base URL, e.g. https://host/v1)")
    model = require("LLM_MODEL_ID", "LLM calls (pinned model id)")
    return key, url.rstrip("/"), model
