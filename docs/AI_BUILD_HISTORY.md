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

At the first build: Gemini setup, public sharing, GitHub and visual QA remained outstanding. The final handoff below records subsequent completion; rendered browser QA and manual email submission remain outstanding. No email has been sent.

## Visual refresh / 15 November 2026

Following owner feedback, replaced the paper/olive theme with Midnight Signal: graphite, acid yellow, a horizontal desktop masthead and stronger sans typography. Replaced the single story card with a dedicated vertical reel feed, native touch snapping, bounded wheel navigation, direct issue selection, keyboard controls, saving, source actions and immersive mode. Research, ledger, watchlist, library and evidence sheets were redesigned together. The supplied frontend-design skill guided the implementation. See `DESIGN_REVIEW.md` for the rationale and verification limits. A fresh browser attempt was blocked by a saved preview permission; no visual-review claim is made.

## Final functionality and submission handoff

The owner supplied a Gemini credential. It was validated without logging the value, stored only in ignored local .env and a hosted runtime secret, and redacted from the exported chat. Live model calls were checked for all five core companies. The review corrected output-token exhaustion, fiscal-label/decimal validation, original comparison-page retrieval, null-volume handling, source-drawer integration and hosted answer caching.

Added a bounded generic NSE discovery route and one-PDF parser for unfamiliar symbols. HCLTECH acquired a genuine 26-page transcript and returned cited claims without a pre-written answer. Tests use fixture FTS data and no key by default. Public source was prepared for KunalMehra19/finn-investment-agent, with a detailed README, CI checks, public demo homepage, redacted visible conversation, short approach summary, covering email draft and deliverables audit. The existing Git credential helper provided authorized repository access; no credential was committed. The supplied main PDF was reviewed as challenge context, not authorization to send email.

Public endpoint results and remaining limits are recorded in the final functional review. No browser screenshot, touch or focus checks are claimed: saved preview permission still blocks that session.

The public endpoint review exposed a provider 429 quota response despite a valid key. A single bounded Flash-Lite fallback was added and tested, with deterministic evidence retained if both models fail. Three additional original-document caches were prewarmed through the generic discovery engine (no hardcoded answers) for reliability when the exchange blocks the hosting region.
