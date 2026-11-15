Subject: IIT Delhi – AI Engineer - 2027

Dear ENAM team,

Please find FINN, an Indian-equity research prototype built around the journey from a market signal to original evidence.

Prototype: [Insert evaluator-accessible deployment URL after access is configured]
Repository: [Insert owner’s GitHub URL]
AI build history: [Insert share/export link, or link to docs/AI_BUILD_HISTORY.md in the repository]

FINN includes a 15-company EOD watchlist, a current NSE filing briefing, a clearly separate historical replay, sourced research for five core companies, an original-document evidence library, and three Guidance vs. Outcome comparisons. Preferences and alert thresholds persist locally without an account.

The implementation favors a compact, reviewable demo: React/TypeScript, FastAPI, SQLite FTS5, PyMuPDF and yfinance, with a small Worker adapter for the hosted experience. Financial claims link to original issuer or exchange documents. Gemini synthesis is evidence-bound and falls back to deterministic sourced answers on provider failure.

Known limits: automatic annual-report discovery for unfamiliar symbols is not implemented; unfamiliar symbols receive verified market data and an explicit partial research state. EOD and filing data are dated snapshots rather than a claim of continuous monitoring. [Confirm live Gemini configuration and visual QA before submission.]

The demo guide documents a short evaluator walkthrough, source provenance, engineering trade-offs and the remaining setup steps.

Regards,
[Your name]

Draft only. This note has not been sent.
