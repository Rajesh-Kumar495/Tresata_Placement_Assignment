# Rejected Alternatives

Every option considered and dropped, and why. Feeds the "alternatives you rejected" section of the brief.

## Problem selection (Stage 1)
| Alternative | Why rejected / deferred |
|---|---|
| Regulator-circular tracking; FTA rules of origin | Excluded by the assignment PDF |
| Treaty withholding (India), originally ranked #1 | **Deferred, not rejected**: secondary target. See ADR-001. |
| ASC 842 lease classification | No external answer key; many existing commercial tools; key inputs (fair value, "reasonably certain") are often absent from the contract |
| OFAC 50% rule | Evaluation almost entirely synthetic; the hard part (entity resolution) is a different project |
| Debt covenant compliance | 100–250-page credit agreements with nested definitions; highest parsing risk for 48h |

## Architecture (Stage 2)
| Alternative | Why rejected |
|---|---|
| **Single LLM call: "here is the release, list non-GAAP issues"** | No exactness (it would do arithmetic itself), no per-rule metrics, unverifiable citations, unbounded output. A good *baseline* to compare against in the eval, though. Worth considering as a reported baseline row. |
| **Autonomous multi-agent system** (planner + specialist agents + critic) | Non-reproducible call graphs; hard to audit; cost and latency unbounded; larger prompt-injection surface. The workflow is known in advance, so planning adds nothing (ADR-002). |
| **Vector-DB RAG over C&DIs** | The corpus is small enough to inject exact rule text. Retrieval adds a silent failure mode (wrong chunk retrieved → wrong rule judged). ADR-003. |
| **Fine-tuning a model** on comment letters | Too little labelled data, 48h budget, opaque knowledge that can't be updated when C&DIs change, and it puts knowledge back in the model, the opposite of P3. |
| **LLM computes the reconciliation tie-out** | LLMs are unreliable at multi-row arithmetic, and the result isn't auditable. ADR-005. |
| **Pure rules / regex, no LLM** | Can't identify novel measure names (D05), can't judge 100.01 "normal recurring operating expense" or 102.10 "record performance" language. This is the honest "why AI" answer: the LLM is needed for identification and judgment, and *only* there. |
| **Fuzzy matching in the grounding gate** | Lets paraphrased or hallucinated evidence through, defeating the gate's purpose. ADR-004. |
| **LLM self-reported confidence for routing** | Poorly calibrated. Replaced by composed confidence (ADR-007). |
| **Human review only at the end** | Inventory errors would silently suppress whole rule families before the human sees anything. ADR-006. |
| **PDF / OCR ingestion in the prototype** | Adds an error source unrelated to the thesis. EDGAR provides HTML. ADR-011. |
| **Streamlit / web UI as a must-have** | Nice for demos but not core to the thesis. Static HTML memo + CLI dispositions first (Q3). |
| **Workflow engine / queue / microservices in the prototype** | Volume is low and peaky. Documented as the production direction only (architecture §12). |
| **Treating every C&DI as applicable to every document** | Legally wrong for furnished 8-K releases (10(e)(1)(ii) refers to filings). ADR-009. |
