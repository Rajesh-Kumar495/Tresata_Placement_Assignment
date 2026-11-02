# Submission checklist (for the morning)

Everything below the line "Done" is finished and committed. **Only you can do the items in "To do".**

## To do (you)
1. **Read the appendix of the brief** (`docs/brief/brief.pdf`, page 5), especially **"What came from me"** and **"One thing I'd stand behind without AI"**.
   - The AI assistant drafted them from the decisions you made in the chat (choosing problem #2, the unlabelled-subtraction policy, provenance disclosure, escalation-only sampling, the requirement vs staff-comment split…).
   - The assignment asks for *your* thinking, so edit them into your own words. Edit `docs/brief/brief.html`, then re-render the PDF:

     ```bash
     "/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe" --headless=new --no-pdf-header-footer --print-to-pdf="D:\Placements\Tresata_Assignment\docs\brief\brief.pdf" "file:///D:/Placements/Tresata_Assignment/docs/brief/brief.html"
     ```

   - Also add your own items to the "_human to add_" rows in `tracking/ai-collaboration-log.md`.
2. **Spot-check the adjudication** in `eval/results/adjudication.md`. The 83 unlabelled findings were labelled TP / debatable / FP by the AI, not by a qualified reviewer. The brief says so; change any labels you disagree with in `src/ngr/adjudicate.py`, then re-run:

   ```bash
   .venv/Scripts/python -I -m ngr.adjudicate
   ```

3. **Push to GitHub.** Nothing has been pushed; the remote is `origin` → `Rajesh-Kumar495/Tresata_Placement_Assignment`. The assignment says the repo link must be publicly accessible, so check the repo's visibility on GitHub after pushing.

   ```bash
   git push origin main
   ```

4. **Export the LLM chat logs** (this conversation) as the zip the form asks for.
5. **Fill in the form:** the brief PDF, the repo link, the chat-log zip.

## Done
- [x] Stage 1 research (5 problems ranked) → `tracking/phase-logs/phase1_problem_research.md`
- [x] Architecture + test plan, approved with your amendments → `docs/design/`, `tracking/decisions.md`
- [x] Prototype: parser, tie-out, inventory, labeller, 9 rules + 4 judges, HTML memo, HC1/HC2 CLI
- [x] Evaluation: 10 real releases + 20 synthetic cases, HC1-confirmed mode, single-call baseline, adjudication → `eval/results/`
- [x] Brief: 4 pages + 1-page appendix → `docs/brief/brief.pdf` (source: `brief.html`)
- [x] Offline reproducibility: corpus, rule sources and LLM cassettes committed and byte-pinned; a fresh clone runs the tests and replays the full evaluation without network or API key (verified)
- [x] `.env` never committed (verified in history)

## Known caveats to be ready for in a live discussion
- 2 of 19 SEC issues missed (Lumen "Modified" footnote location; Adient equity income). See `eval/results/README.md`.
- Precision on real documents: 53% strict / 90% lenient (AI-adjudicated). The noisiest rule is 100.01 "normal recurring expense".
- 13 bugs were fixed after the first full run; both runs are reported.
- The 20 generated synthetic HTML files are in git history (about 7 MB, commit 4d31c7f) although they are now ignored; harmless.
