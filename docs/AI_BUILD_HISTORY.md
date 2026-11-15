# AI build history

Built in one Codex session on 15 November 2026 from the supplied FINN execution plan and the project owner’s direction to prioritize UI and functionality for one evaluator.

## Product and implementation decisions

- Started from an empty `D:\finn` workspace. The supplied document was treated as project reference material, not as authorization to email an evaluator or change public sharing.
- Chose an editorial research-desk design: warm paper, forest green, muted olive, Instrument Serif headlines, DM Sans body type, restrained separators, company monograms and a manual story deck. No decorative stock charts or invented market numbers.
- Implemented React/TypeScript/Vite/Tailwind and a Python FastAPI/SQLite/PyMuPDF/yfinance backend. Added a small Worker adapter for a self-contained hosted prototype because Sites does not run a persistent Python process.
- Retrieved real Yahoo EOD data for all 15 watchlist symbols. Initial data is for the completed 13 November 2026 session. Daily move uses preceding close; relative volume excludes the latest session from its 20-session baseline.
- Downloaded original issuer PDFs, checked actual page content, retained hashes and page indices, and built SQLite FTS5. Retrieved official NSE announcement metadata for the watchlist and verified attachments individually.
- Kept current filing windows separate from historical FY25/FY26 replay events. Ranked materiality before recency and retained routine filings in a collapsible section.
- Manually checked three promise/outcome records. Corrected Reliance citations for the extra exchange-cover page and disclosed that TCS’s FY26 operating margin excludes one-off costs.
- Wired server-only Gemini synthesis with structured outputs, bounded prompts, citation/excerpt/page validation, numeric input checks, caching locally and rate limits. No API key was supplied, so live Gemini success remains unverified; deterministic evidence retrieval is functional.
- Verified HCLTECH, ASIANPAINT and AXISBANK market lookup and a clean failure for an invented symbol. Automatic unseen-company PDF discovery was omitted in favor of the explicit partial state.

## Verification

- TypeScript checking and Vite production build passed.
- Python tests cover market-session calculations, 20-session volume exclusion, citation rejection, current/replay separation, five-company coverage, guidance references and differences, invalid inputs, unknown questions and keyless research.
- Node checks verify all 15 snapshots and factual page references.
- Generated Worker smoke checks verify HTML/assets, health, snapshot, watchlist, briefing, ledger, sources, invalid inputs and keyless research.
- Real provider checks returned verified identities/EOD snapshots for the three unseen-symbol examples and HTTP 404 for a nonexistent symbol.
- The browser security gate declined local preview access. No workaround was used. Rendered desktop and 390px visual/interaction QA remains outstanding.

## Outstanding external setup

Gemini key configuration; explicit evaluator sharing/public access; owner-selected GitHub repository; visual browser QA; owner review and submission of the covering note. No message has been sent to anyone.
