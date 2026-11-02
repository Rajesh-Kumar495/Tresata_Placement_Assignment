# Non-GAAP Earnings-Release Review Assistant

A prototype that reviews **non-GAAP financial measures in US earnings releases** (Form 8-K Item 2.02, Exhibit 99.1) against:
- SEC Regulation G;
- Item 10(e) of Regulation S-K;
- the SEC staff's Non-GAAP C&DIs.

It produces a review memo for the SEC reporting team. Every finding is tied to an exact quote in the release and to the verbatim rule text, with a human checkpoint before the rules run (HC1) and a human sign-off on every finding (HC2).

> **The LLM identifies, code decides, a human confirms.** The LLM names the measures, labels table rows and columns, and judges four qualitative rules. It never produces a number used in arithmetic and never sets a finding's legal category. Parsing, tie-out arithmetic (exact decimals) and 9 rules are deterministic.

**Brief:** [docs/brief/brief.pdf](docs/brief/brief.pdf) (4 pages + 1-page appendix) · **Design:** [docs/design/architecture.md](docs/design/architecture.md) · **Evaluation plan:** [docs/design/test_plan.md](docs/design/test_plan.md) · **Decisions:** [tracking/decisions.md](tracking/decisions.md)

## Results (10 real SEC-reviewed releases + 20 synthetic cases)

| Metric | Pre-registered target | This system | Single-LLM-call baseline |
|---|---|---|---|
| SEC-raised issues detected (6 releases, 19 issues) | ≥ 70% | **17/19** | 9/19 |
| Known-clean items not flagged | 0 violations | **18/18** | 8/18 |
| Synthetic violations and traps | ≥ 90% | **20/20** | 8/19 |
| Evidence quotes verbatim in the source | 0 failures | **1183/1183** | 330/333 |
| Measure inventory recall / precision | ≥ 90% recall | 73/73 · 79/85 | — |
| Reconciliation checks on real releases | exact | 351 PASS · 2 NEEDS_REVIEW · 11 NOT_EVALUATED | invents tie-out errors |
| Precision on all 100 real-release findings | — | 53% strict · 90% lenient (AI-adjudicated) | — |

Where it fails is reported in [eval/results/README.md](eval/results/README.md):
- 2 misses;
- alert volume on the 100.01 and ordering rules;
- first-run vs final numbers and the 13 bugs fixed in between.

Model: `deepseek/deepseek-v4.1-flash` (OpenAI-compatible endpoint), temperature 0.

## Data
- **Real (public):** 10 EDGAR Ex 99.1 releases in `data/raw/`, sha256-pinned in `eval/corpus_manifest.json`.
  - 6 drew SEC staff comments on non-GAAP measures (Tier A), chosen by triaging all 18 letters an EDGAR full-text search returned.
  - 4 are the same companies' releases after they fixed the issues (Tier B).
  - Gold labels are in `eval/gold/`, with every anchor validated against the bytes.
- **Synthetic:** 20 cases, each a single documented edit to a real release (`src/ngr/synthetic.py`, specs in `eval/synthetic_cases.yaml`). They are labelled synthetic throughout.
- **Rule text:** verbatim excerpts in `rules/excerpts.yaml`, extracted from the fetched SEC and eCFR pages in `data/rules_src/`.
- No confidential or personal data is used.

## Run it

Create a Python 3.11+ environment:

```bash
python -m venv .venv
```

Install the package with development dependencies:

```bash
.venv/Scripts/python -m pip install -e ".[dev]"
```

Run the tests (no network needed):

```bash
.venv/Scripts/python -m pytest
```

Reproduce the full evaluation **offline**, without an API key, from recorded LLM responses (`eval/cassettes/`):

```bash
.venv/Scripts/python -I -m ngr.evaluate --mode replay
```

The same, with the human-confirmed (gold) measure list at HC1:

```bash
.venv/Scripts/python -I -m ngr.evaluate --mode replay --hc1 gold
```

The single-call baseline:

```bash
.venv/Scripts/python -I -m ngr.baseline --mode replay
```

Recompute the adjudication of unlabelled findings:

```bash
.venv/Scripts/python -I -m ngr.adjudicate
```

On macOS/Linux use `.venv/bin/python`. Outputs go to `eval/results/`; per-document HTML memos go to `runs/<run_id>/` (sample memos in `eval/results/sample_reports/`).

### Reviewer workflow (HC1 → HC2)

Review a release (a doc id or a path to an `.htm` file):

```bash
.venv/Scripts/python -I -m ngr.cli review A02-turtlebeach-2023-08-07
```

Edit `runs/review_<id>/hc1_proposal.json`, setting `"confirmed": true` or `false` on each measure, then re-run with the confirmed list:

```bash
.venv/Scripts/python -I -m ngr.cli hc1 A02-turtlebeach-2023-08-07 runs/review_A02-turtlebeach-2023-08-07/hc1_proposal.json --reviewer "Your Name"
```

Fill in `hc2_dispositions.json` (accept, reject or edit; a reject needs a note), then sign it into `audit.jsonl`:

```bash
.venv/Scripts/python -I -m ngr.cli hc2 runs/review_A02-turtlebeach-2023-08-07 --reviewer "Your Name"
```

### Live LLM calls and EDGAR downloads (optional)

Copy `.env.example` to `.env`, which is git-ignored, and set:
- `GOEDEL_API_KEY`, `GOEDEL_URL` and `LLM_MODEL_ID` for any OpenAI-compatible endpoint;
- `SEC_EDGAR_USER_AGENT` (a contact string, required by the SEC fair-access policy).

Then run without `--mode replay`, or re-download the corpus:

```bash
.venv/Scripts/python -I -m ngr.corpus fetch
```

## Layout
| Path | What |
|---|---|
| `src/ngr/docmodel.py`, `numeric.py` | HTML → blocks (with styles) and tables (cells, header paths, scale); accounting number parser |
| `src/ngr/tieout.py` | Deterministic tie-out: segmented chain, subtotal checkpoints, sign polarity, three-band tolerance, horizontal (columnar) reconciliations |
| `src/ngr/inventory.py`, `reconcile.py`, `grounding.py`, `llm.py` | Bounded LLM steps (measure inventory, row/column roles), exact-quote grounding gate, client with record/replay |
| `src/ngr/rules.py`, `judges.py`, `findings.py`, `rules/` | 9 deterministic rules, 4 judge/hybrid rules, finding model, rule pack with verbatim excerpts |
| `src/ngr/review.py`, `report.py`, `cli.py` | End-to-end review, HTML/JSON memo, HC1/HC2 reviewer commands |
| `src/ngr/evaluate.py`, `baseline.py`, `synthetic.py`, `adjudicate.py` | Evaluation harness, single-call baseline, synthetic cases, adjudication |
| `tracking/` | Decision records (ADR-001…028), phase logs, rejected alternatives, AI-collaboration log |
