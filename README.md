# Non-GAAP Earnings-Release Review Assistant (prototype)

This tool reviews non-GAAP measures in SEC earnings releases (Form 8-K Item 2.02, Ex 99.1) against:
- Regulation G;
- Item 10(e) of Regulation S-K;
- the SEC staff's Non-GAAP C&DIs.

It splits the work between deterministic code (parsing, arithmetic, rules) and bounded LLM steps (identifying measures, judgment calls). Every finding is traceable to a source span and a cited rule. A human reviewer confirms the inputs and owns the conclusions.

**Status:** Stage 3 in progress. The deterministic core is built (document model, tie-out engine, gold labels). The LLM steps, rules and report are not built yet. See [tracking/progress.md](tracking/progress.md).

- Design: [docs/design/architecture.md](docs/design/architecture.md)
- Evaluation plan: [docs/design/test_plan.md](docs/design/test_plan.md)
- Decisions: [tracking/decisions.md](tracking/decisions.md)

## Setup

Create the environment:

```bash
python -m venv .venv
```

Install the package with development dependencies:

```bash
.venv/Scripts/python -m pip install -e ".[dev]"
```

Copy the configuration template, then fill in `.env`:

```bash
cp .env.example .env
```

`.env` is git-ignored. `SEC_EDGAR_USER_AGENT` is required for any EDGAR download, under the SEC fair-access policy. The OpenRouter variables are needed from the LLM steps onward.

## Run the tests

```bash
.venv/Scripts/python -m pytest
```

## Data

Only public EDGAR filings and synthetic variants of them are used:
- Tier A/B cases are real releases;
- Tier C/D cases are synthetic, derived from a real release, and labelled as such.

No confidential or personal data is used.
