# Step 4–5 results: real corpus, measure inventory, row-role labelling, tie-out

**Run:** `runs/20261102T181452Z` (live), replayed as `runs/20261102T181643Z` (replay mode, offline). Run outputs are git-ignored; the cassettes in `eval/cassettes/` reproduce them.
**Model:** `deepseek/deepseek-v4.1-flash` via the Goedel OpenAI-compatible endpoint. temperature 0, k=1, `response_format=json_object`.
**Corpus:** 10 real Ex 99.1 releases (6 Tier A, 4 Tier B), sha256-pinned in `eval/corpus_manifest.json`.

## Corpus verification
| Check | Result |
|---|---|
| Downloads (EDGAR, declared User-Agent) | 10/10, all HTML |
| Gold-label anchors found verbatim in parsed text (ADR-020) | **27/27** → all labels `validated` |
| Real reconciliations re-checked on parsed bytes with hand-assigned roles (`tests/test_real_corpus.py`) | Turtle Beach Table 5 (columnar), Capri Sch. 6 (columnar, to EPS), Adient (two column groups + memo build-up + "Less:" row), Citi Trends: all tie |

## Measure inventory (lexicon ∪ LLM, grounding gate)
| Doc | Measures | Gold recall, LLM only | Gold recall, surfaced to HC1 (LLM ∪ lexicon ∪ table cross-check) |
|---|---|---|---|
| A01 Aviat | 8 | 7/10 | 10/10 |
| A02 Turtle Beach | 5 | 4/4 | 4/4 |
| A03 Capri | 7 | 7/7 | 7/7 |
| A04 Citi Trends | 7 | 6/6 | 6/6 |
| A05 Lumen | 11 | 9/9 | 9/9 |
| A06 Adient | 13 | 10/10 | 10/10 |
| **Total** | | **43/46 (93%)**, pre-registered target ≥ 90% | **46/46** |

- **Grounding:** 181/181 quotes verbatim (0 rejected, 0 measures dropped).
- **Aviat misses:** the LLM missed three expense-line measures (non-GAAP R&D, S&A, tax provision). The lexicon *and* the table cross-check both surfaced them, so the reviewer sees them at HC1. This is the union/diff design working as intended on the weakest-point failure mode (FMEA F1).
- **Not measured:** inventory *precision*. Tier B has no gold measure lists, and some extra measures, e.g. Adient "Adjusted Results (income statement)", are arguably correct. HC1 is where a human trims them.

## Row-role labelling + deterministic tie-out
- **72 reconciliations** identified across 10 releases (vertical and horizontal), **193 line/column checks.**
- **191 PASS, 2 FLAG.** Both FLAGs are the same false positive: Turtle Beach's Adjusted EBITDA step (one per period). See below.
- **0 gate errors** (no unknown row or column IDs returned by the LLM).
- **Cost/latency:** 57 calls, about 57 s wall-clock for 10 documents (4 tables labelled in parallel per document).
- **Replay:** 57/57 cassette hits, byte-identical outputs (20/20 files), no network.

### What the first run broke, and what fixed it
| Observed on real data | Fix (deterministic unless noted) |
|---|---|
| 3/6 Tier A reconciliations are **columnar** ("As Reported \| adj… \| As Adjusted") | Horizontal orientation via transposition, so the same engine applies (ADR-021) |
| Repeated header block inside one table ("Six Months Ended") parsed as data | Header state machine in the parser |
| GAAP EPS → non-GAAP EPS labelled as a reconciliation with **no adjustment rows**. Lumen's prior year **passed by coincidence** (0.50 vs 0.51 within 1 cent). | `no_adjustment_values` guard: only an exact identity can pass (ADR-023) |
| Effective tax **rates** summed (30.8% + 45.0% ≠ 34.1%) | `ratio_not_additive` → NOT_EVALUATED (ADR-023) |
| Two period column groups returned as one reconciliation → `multiple_gaap_start` | Deterministic split at each gaap_start, logged on the result (ADR-023) |
| Labeller included a row of a different measure in horizontal lines; missed the vertical EBITDA step | Prompt: explicit guidance for repeated column groups, vertical continuation, line-row eligibility, per-share derivations (LLM change) |
| "EPS" vs "earnings per share", "R&D" vs "research and development" not matched | Matcher synonyms (eval tooling) |

### Open: the Turtle Beach uncued subtraction (needs a human decision)
- **The table:** Adjusted operating loss (5,397) → "Other non-operating expense, net" printed **198** with no "Less:" label → Adjusted EBITDA (5,595). Arithmetic: −5,397 − 198 = −5,595.
- **What the labeller did:** it found the vertical step correctly but returned `sign_hint=as_printed` (its note says "plus Other non-operating expense").
- **What the engine did:** it computes −5,199 and gets diff −396 = 2 × 198. The flip diagnosis is restricted to cue-bearing rows (human rule, ADR-014), so this row isn't eligible. **Verdict: FLAG**, a false positive, but not a silent pass.
- **Had the LLM said `subtract`:** the result would be PASS with the INFERRED_SIGN provenance warning (tested in `test_turtle_beach_adjusted_ebitda_step_needs_inferred_sign_and_says_so`).
- **Not done on purpose:**
  - tuning the prompt until this one document ties, which overfits the evaluation;
  - re-asking the LLM with the diff, which fits labels to numbers.
