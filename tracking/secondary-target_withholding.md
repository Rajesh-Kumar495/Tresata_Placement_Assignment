# Secondary Target (Parked): Treaty Withholding-Rate Determination — India

**Status:** Parked 2026-11-01 by human decision; not built. The remaining time went into evaluation quality for the primary target (baseline, adjudication).
**Full research:** [phase-logs/phase1_problem_research.md §2 #1](phase-logs/phase1_problem_research.md)

## One-line problem
A CA must certify (Form 146, formerly 15CB, from 1 April 2026) the withholding rate on each outbound payment to a non-resident. That means characterising the payment (royalty / FTS / business profits) under the specific DTAA, applying "lower of Act vs treaty", and checking conditions (TRC, Form 10F, MFN notification).

## Why it's a separate system (not a mode of #2)
- Different knowledge base (DTAA texts + Income-tax Act 2025 vs SEC C&DIs).
- Different core artefact: an *amount* (rate × base + surcharge + cess) rather than a *compliance finding*.
- Different accountable human: the CA certifies by statute.

## What would carry over from #2's architecture
- Rules-as-data rule pack with citations and effective dates (ADR-003) — even more valuable here because of the 1961→2025 Act renumbering.
- Grounding gate: every LLM characterisation must quote the agreement/invoice clause (ADR-004).
- Decimal-only deterministic calculator (ADR-005).
- Record/replay harness and eval-first methodology (ADR-008, ADR-013).

## Open items before starting it
- [UNVERIFIED] Which section of the Income-tax Act 2025 replaces old s.195, and which rule governs Form 145/146. Secondary sources conflict (s.393 / s.395 / s.397; Rule 220). Must read the primary bare Act + Rules.
- Scope: 3–4 treaties (USA, UK, Netherlands, Singapore) × 4 payment types.
