import pytest

from ngr import config, edgar


def test_edgar_fetch_refuses_without_user_agent(monkeypatch, tmp_path):
    monkeypatch.delenv("SEC_EDGAR_USER_AGENT", raising=False)
    monkeypatch.setattr(config, "PROJECT_ROOT", tmp_path)  # no .env to load
    with pytest.raises(config.ConfigError, match="SEC_EDGAR_USER_AGENT"):
        edgar.fetch("https://www.sec.gov/", "x.htm")


def test_user_agent_read_from_environment(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "PROJECT_ROOT", tmp_path)
    monkeypatch.setenv("SEC_EDGAR_USER_AGENT", "Test Runner test@example.com")
    assert config.edgar_user_agent() == "Test Runner test@example.com"


def test_env_example_has_placeholders_only():
    text = (config.PROJECT_ROOT / ".env.example").read_text(encoding="utf-8")
    for line in text.splitlines():
        if line and not line.startswith("#"):
            key, _, value = line.partition("=")
            assert value == "", f"{key} must be an empty placeholder in .env.example"
