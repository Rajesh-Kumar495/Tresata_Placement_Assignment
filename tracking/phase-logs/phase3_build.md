# Phase 3 Log — Build (Primary: SEC Non-GAAP)

## 2026-11-02 — Session 1: sign-off, triage, labels, deterministic core

### Human sign-off, with changes (all human-originated)
| # | Change | Recorded as |
|---|---|---|
| 1 | Tie-out must exclude intermediate subtotals from the sum (or check them as checkpoints) and handle sign polarity for "Less:"/"Deduct:" rows printed positive | ADR-014 |
| 2 | Judges: temperature 0, k=1. Extra samples only on UNCERTAIN or schema/grounding failure (free-tier rate limits) | ADR-015 |
| 3 | Cross-period recurrence diff is optional enrichment, built last on 1–2 Tier A cases | ADR-016 |
| Q1 | Distinguish statutory requirements (Reg G / 10(e)(1)(i)) from staff comment risk (10(e)(1)(ii) / C&DIs) in a category field, not a vague "advisory" | ADR-017 |
| Q2 | Verify C&DI 104.x / 105.x; 106.x out of scope | open-questions Q2 (closed) |
| Q3 | Static self-contained HTML + CLI/JSON, no Streamlit | ADR-018 |
| Q4 | Model bake-off on 2 tables; model ID in .env | ADR-019 |
| Q5 | Triage the 18 letters; lock ≥4 Tier A + ≥2 Tier B | test_plan §4 |
| Q6 | HTML only; image/PDF → NOT_EVALUATED | ADR-011 |
| Q7 | `SEC_EDGAR_USER_AGENT` from .env, placeholder in .env.example, no personal email in git | ADR-019 |

### Verification done
- **Form 8-K PDF (sec.gov/files/form8-k.pdf)**, read directly:
  - Item 2.02 Instruction 2 applies only Item 10(e)(1)(i) (p.15);
  - General Instruction B.2: Item 2.02 information is furnished, not filed (p.3).
  - This confirms the human's Q1 framing.
- **Verbatim C&DIs 104.02–105.07.** Notable: 104.04 (total segment profit outside the footnote is non-GAAP), 104.06 (constant currency: side-by-side presentation plus process description satisfies reconciliation), 105.06.
- **Reg G 244.100 (Cornell LII).** Note: "materially" does not appear in 100(b); "materially misleading" is staff language (C&DI 100.06). Q9 is open on a cross-reference oddity.

### Tier A/B triage: full record (18 letters)
Method: each letter read from EDGAR `filename2.txt` by fetch agents. For locked cases, the original Ex 99.1, the company CORRESP response and the first post-response Item 2.02 release were also read.

| # | Company | Verdict | Reason |
|---|---|---|---|
| 1 | Insperity | Reserve | 8-K reached via headline comment on 10-K "also applies to" |
| 2 | Cimpress | Reserve (first in line) | Ex 99.1 comments: PROM-ORDER, normal opex, unlabelled segment total |
| 3 | Worthington | Reserve | Ex 99.1: EBITDA from NI, PROM-RATIO |
| 4 | Citi Trends | **Locked A04 + B04** | Headline, flowthrough, other non-recurring |
| 5 | Everbridge | Dropped | 8-K only via "also applies to" |
| 6 | Capri | **Locked A03 + B03** | Bullets, op-margin recon, FCF unlabelled |
| 7 | Distribution Solutions Group | Reserve | PROM-DISCUSSION only (Ext) |
| 8 | Aviat | **Locked A01 + B01** | Headline, opex recon |
| 9 | MasterBrand | Reserve | PROM-RATIO, cost-savings adjustment |
| 10 | Vista Outdoor | Reserve | Headline, FCF label |
| 11 | BrightView | Dropped | Clean 8-K comment maps to Ext only |
| 12 | Sonoco | Dropped | 8-K not identified |
| 13 | ARKO | Reserve | PROM-DISCUSSION (Ext) |
| 14 | Lee Enterprises | Dropped | Strong comment is on Ex 99.2 |
| 15 | Adient | **Locked A06** (B reserve) | Recon start, recon present, normal opex; headline is a JPG |
| 16 | Turtle Beach | **Locked A02 + B02** | Headline %, net of tax, EBITDA from operating income, 100.01 |
| 17 | Harmonic | Reserve | Segment adj. EBITDA recon |
| 18 | Lumen | **Locked A05** | PROM-ORDER, Modified metrics recon on website only; response HTTP 503 (Q8) |

### Things learned from real documents (candidates for the brief's "what surprised you")
1. **The human's polarity/subtotal concern is real in our own corpus:**
   - Turtle Beach Table 5 has an intermediate subtotal *and* an uncued positive-printed subtraction.
   - Adient prints "Less: Adjusted Equity Income 25".
   - Citi Trends prints negatives.
   - Aviat mixes conventions within one release.
2. **A real image-only headline (Adient).** Prominence rules must abstain, and HTML-only (ADR-011) is not just a convenience limit.
3. **The SEC letter is not a complete label.** Aviat's release says "Achieved record quarterly adjusted EBITDA", a textbook 102.10(a) bullet 5 pattern, and the SEC did not raise it. Labelled `unscored`, to adjudicate manually.
4. **Companies don't always fully comply even after agreeing.** Capri's FCF is defined but reconciled only by in-text arithmetic; Adient still adjusts "restructuring related"; Lumen moved to an operating-income margin, not a net-income margin.
5. **Real-letter selection bias.** The search phrase selects for prominence issues; no letter in 18 was about an arithmetic tie-out error. Tier C carries the tie-out evaluation.

### Built
| Item | Notes |
|---|---|
| `pyproject.toml`, `.venv`, `.gitignore`, `.env.example` | `.env` git-ignored; placeholders only |
| `src/ngr/config.py`, `edgar.py` | Fetcher refuses without `SEC_EDGAR_USER_AGENT`; stores raw bytes + sha256 sidecar |
| `src/ngr/numeric.py` | Accounting number parser (parens, dashes, footnotes, unicode minus, printed precision) |
| `src/ngr/docmodel.py` | HTML → blocks (style runs, headline/bullet classification), data vs layout tables, EDGAR fragment merging (`$` / `(1,234` / `)`), colspan header paths, scale detection, images, stable IDs, char spans |
| `src/ngr/tieout.py` | Segmented chain, subtotal checkpoints, deterministic sign resolution (LLM hint ∪ lexicon, conflicts recorded), three-band tolerance, restricted diagnoses |
| `src/ngr/labels.py` | Gold-label schema + rule-ref validator + anchor validator (ADR-020) |
| `rules/rulepack.yaml` | Skeleton: 24 rule IDs, citations, category per document type, MVP flag. Verbatim excerpts in step 6. |
| `eval/gold/*.yaml` | 6 Tier A + 4 Tier B labels (anchors provisional until download) |
| `eval/synthetic_cases.yaml` | 15 mutation + 14 trap specs, pre-registered expectations |

### Tests: 68 passing
- `test_numeric` (31), `test_docmodel` (7), `test_tieout` (20, incl. 2 Hypothesis properties × 60 examples and 4 real-world reconciliations), `test_labels` (7), `test_config` (3).
- **Mutation check of the test suite.** Four deliberately broken engine copies were each caught:
  - loose tolerance → caught by a property test;
  - sign handling disabled → caught by the Adient real case;
  - subtotals not checked → caught by the wrong-subtotal test;
  - unrestricted flip diagnosis → caught by the Turtle Beach real case.

### Not done / blocked (at end of session 1)
- Corpus download blocked on `SEC_EDGAR_USER_AGENT` (resolved in session 2).
- No LLM code yet.

## 2026-11-02 — Session 2: real corpus, inventory, row-role labelling

### Human decisions this session
- LLM via the Goedel endpoint (`GOEDEL_API_KEY`, `GOEDEL_URL`) with `deepseek/deepseek-v4.1-flash` → ADR-024.
- Three-band tolerance **approved**: "passing up to a 3-unit discrepancy automatically on a 6-line table is way too loose for financial tie-outs" → ADR-014 addendum accepted.
- **New requirement:** an LLM-inferred sign on an unlabelled row must be surfaced in provenance even when the math ties → ADR-022.

### Done
- **Corpus:** 10/10 downloaded; **27/27 gold anchors verbatim** → labels `validated`. Corpus committed (ADR-025).
- **Real-bytes tests:** `tests/test_real_corpus.py` (7). Replaced the mis-transcribed Turtle Beach fixture: the real Table 5 is columnar.
- **New code:**
  - `llm.py`: OpenAI-compatible client, cassettes, schema repair;
  - `grounding.py`: exact-match gate with offset-preserving normalisation;
  - `inventory.py`: lexicon ∪ LLM, union/diff;
  - `reconcile.py`: orientation-aware labeller, ID gate, column-group split;
  - `pipeline.py`: runner, HC1 proposal files, manifest;
  - `tieout.py`: horizontal transposition, provenance warnings, guards.
- **Results:** see [eval/results/step5_real_corpus.md](../../eval/results/step5_real_corpus.md).
  - Inventory gold recall: 43/46 LLM-only, 46/46 surfaced to HC1.
  - Grounding: 181/181.
  - Tie-out: 191/193 PASS; the 2 FLAGs are the Turtle Beach uncued-sign false positive (Q11).
  - Replay: byte-identical.
- **Tests:** 81 passing.

### Surprises worth putting in the brief
1. **Half the real reconciliations are columnar.** A design built only from reading the rules (and from an AI agent's description of a table) would have assumed vertical bridges.
2. **Tolerance can produce false passes, not just false flags:** non-GAAP EPS 0.51 vs GAAP EPS 0.50 "tied" within a cent, with nothing reconciled.
3. **The LLM got table structure right far more often than signs.** Its one systematic error is semantic sign on uncued rows, exactly the case the human anticipated before any data was seen.

## 2026-11-02/03 — Session 3: rules, judges, evaluation, brief

### Human decisions this session
- **Q11 → ADR-026:** unlabelled single-row 2× discrepancies go to NEEDS_REVIEW with the row named, never PASS.
- **Q12:** gold measure lists for Tier B.
- Commit to git before the next phase.
- Later: "finish all the work"; then package the brief at the repository root and drop working files.

### Built
- 9 deterministic rules and 4 judge/hybrid rules, with verbatim rule excerpts (`rules/excerpts.yaml`) extracted from sha256-pinned SEC/eCFR pages.
- Finding model with category, lineage and provenance.
- Self-contained HTML memo; reviewer CLI (`review`, `hc1`, `hc2`, with a signed audit log).
- 20 synthetic cases; evaluation harness with HC1-gold mode; single-LLM-call baseline; adjudication of unlabelled findings.
- Brief (`Tresata_Brief.pdf`, 4 pages + appendix).

### Results (final)
- **System:** Tier A 17/19 (first run 14/19); must-not-flag 18/18; synthetic 20/20; evidence 1183/1183 verbatim; inventory 73/73 recall, 79/85 precision.
- **Baseline (one LLM call):** 9/19, 8/18, 8/19. It also reported arithmetic errors in reconciliations that tie.
- **Adjudication** of 83 unlabelled findings (by the AI, approved for use by the human): 36 TP, 37 debatable, 10 FP; precision 53% strict / 90% lenient.
- **13 general bugs** fixed after the first run; both runs are reported in `eval/results/README.md`.

### Verified at the end
- A fresh clone with no `.env` and no network passes the tests and replays the system evaluation, the HC1 run and the baseline byte-identically.
- `.env` was never committed.
- The confidential assignment PDF is untracked going forward.
