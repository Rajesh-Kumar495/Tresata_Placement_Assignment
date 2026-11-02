# Project Tracking — Index

The working record for the Tresata take-home. Everything we decide, reject or learn goes here first, so the 4-page brief and its AI-usage appendix can be written from it without reconstructing history.

| File | What it holds | Feeds which part of the brief |
|---|---|---|
| [progress.md](progress.md) | Stage status, timeline, what's done / next / blocked | — (internal) |
| [phase-logs/phase1_problem_research.md](phase-logs/phase1_problem_research.md) | Stage 1: 5 ranked problems + sources | "Area explored & what surprised you" |
| [phase-logs/phase2_design.md](phase-logs/phase2_design.md) | Stage 2: design session log, what changed and why | Solution design |
| [phase-logs/phase3_build.md](phase-logs/phase3_build.md) | Stage 3: sign-off changes, full 18-letter triage record, what was built, lessons from real documents | Surprises, prototype, honest failures |
| [decisions.md](decisions.md) | Architecture Decision Records (ADR-001…) | Solution design, risks |
| [rejected-alternatives.md](rejected-alternatives.md) | Every option we considered and dropped, with reason | "Alternatives you rejected and why" |
| [open-questions.md](open-questions.md) | Unresolved items needing a human call or verification | "Things to consider before spending more time" |
| [ai-collaboration-log.md](ai-collaboration-log.md) | Key prompts, AI suggestions corrected/rejected, human-originated decisions | **Appendix: what you added beyond the AI** |
| [secondary-target_withholding.md](secondary-target_withholding.md) | Parked problem #1 (India treaty withholding) | — (only if time remains) |

Design deliverables live in [`../docs/design/`](../docs/design/):
- [architecture.md](../docs/design/architecture.md) — system architecture for the primary target
- [test_plan.md](../docs/design/test_plan.md) — eval-first test plan and case catalogue

## Conventions
- **ADR status:** `Proposed` → `Accepted` (only after the human reviewer signs off) → `Superseded by ADR-x`.
- **Verification tags** on any factual claim: `[VERIFIED: source]`, `[SECONDARY]`, `[UNVERIFIED]`.
- **Dates** are absolute (YYYY-MM-DD). Project start: 2026-11-01.
