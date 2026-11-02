# Non-GAAP Earnings-Release Review Assistant (prototype)

This tool reviews non-GAAP measures in SEC earnings releases (Form 8-K Item 2.02, Ex 99.1) against:
- Regulation G;
- Item 10(e) of Regulation S-K;
- the SEC staff's Non-GAAP C&DIs.

It splits the work between deterministic code (parsing, arithmetic, rules) and bounded LLM steps (identifying measures, judgment calls). Every finding is traceable to a source span and a cited rule. A human reviewer confirms the inputs and owns the conclusions.

**Status:** Stage 3 in progress. The full pipeline is built: parser, tie-out, measure inventory, row-role labeller, 9 deterministic rules, 4 judge/hybrid rules, HTML/JSON review memo and the evaluation harness. See [tracking/progress.md](tracking/progress.md).

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

`.env` is git-ignored. `SEC_EDGAR_USER_AGENT` is required for any EDGAR download, under the SEC fair-access policy. `GOEDEL_API_KEY`, `GOEDEL_URL` and `LLM_MODEL_ID` are needed only for *live* LLM calls.

## Reproduce the pipeline without network or API key

The real corpus (`data/raw/`) and the recorded LLM responses (`eval/cassettes/`) are committed, so a replay runs fully offline:

```bash
.venv/Scripts/python -I -m ngr.pipeline --mode replay
```

Run the full evaluation (10 real releases + 20 synthetic cases), producing an HTML review memo per document plus scores:

```bash
.venv/Scripts/python -I -m ngr.evaluate --mode replay
```

Results go to `eval/results/full_eval.md`, with sample memos in `eval/results/sample_reports/`.

Validate the gold-label anchors against the corpus:

```bash
.venv/Scripts/python -I -m ngr.corpus validate
```

Results: [eval/results/step5_real_corpus.md](eval/results/step5_real_corpus.md). Model: `deepseek/deepseek-v4.1-flash` via an OpenAI-compatible endpoint.

## Run the tests

```bash
.venv/Scripts/python -m pytest
```

## Data

Only public EDGAR filings and synthetic variants of them are used:
- Tier A/B cases are real releases;
- Tier C/D cases are synthetic, derived from a real release, and labelled as such.

No confidential or personal data is used.
