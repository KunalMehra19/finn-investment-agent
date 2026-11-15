# FINN — From Signal to Evidence

A mobile-first Indian-equity research desk: **notice a signal → investigate the business → verify the original evidence**.

**[Read the one-page project report (PDF)](FINN_Project_Report.pdf)** - what we built, key decisions and trade-offs, deliberate omissions, and next steps.

**[Open the public demo](https://finn-research-desk.delicateloon4.chatgpt.site)** · **[Demo guide](docs/DEMO_GUIDE.md)** · **[Source manifest](docs/SOURCE_MANIFEST.md)** · **[Redacted AI conversation](docs/CHAT_LOG_REDACTED.md)**

Built for the ENAM AI Engineer Build Challenge. This is a focused evaluator prototype, with interaction, evidence quality and reliable fallbacks prioritized over scaling infrastructure. It provides information, not investment advice or trading execution.

## Try the complete journey

1. Enter **Signal Room** from the briefing. Swipe vertically, scroll, select an issue or use the arrow keys. There is no autoplay. Save a signal or open its evidence.
2. Investigate L&T’s Noida Metro order. The disclosed ₹1,000–2,500 crore classification is a **value band**, not an exact contract price. Check PDF page 2 of the original NSE attachment.
3. Open TCS in Research and ask **“What changed in operating margins from FY25 to FY26?”** Gemini answers from retrieved original pages, with clickable citations and explicit unknowns.
4. Open the **Promise ledger**. Compare exact prior guidance with subsequent results. Each finding has two evidence actions. TCS’s FY26 margin excludes one-off costs; that accounting basis is stated.
5. Change the daily-move and relative-volume thresholds in Watchlist. Following, thresholds and saved stories persist on your browser.
6. Search **HCLTECH**, then ask about management’s outlook. An unfamiliar NSE ticker triggers verified identity/EOD lookup and a bounded attempt to retrieve and parse an original NSE document. Failed acquisition produces an honest partial state.

## Working features

| Area | Behavior |
| --- | --- |
| Push briefing | 15-stock watchlist, real 24h/7d filtering, materiality before recency, routine filings retained in a collapsible section |
| Reels | Vertical touch snapping, bounded wheel steps, issue selection, keyboard navigation, immersive mode, saving and source controls |
| Market signals | Completed-session EOD close/move/volume, 20-session relative volume and configurable thresholds |
| Pull research | Gemini over primary passages, structured claims, source/page/excerpt and numeric checks, caching and deterministic fallback |
| Evidence library | Original issuer/exchange URLs, PDF pages, SHA-256 hashes, financial periods, publication and retrieval dates |
| Guidance vs. Outcome | Three historical comparisons across TCS and Sun Pharma, with Met / Missed / Unclear and dual citations |
| Generalization | Bounded original-document discovery for unfamiliar tickers, rather than hardcoded unseen-company answers |

Three additional original-document caches (HCLTECH, ASIANPAINT and AXISBANK) are prewarmed through the generic discovery script for demo resilience. They contain primary passages, not pre-written research answers.

The baseline includes **15 real market snapshots**, **35 verified original documents**, **five historical replay stories**, a recent NSE filing snapshot, and **three guidance comparisons**. Reliance, TCS, HDFC Bank, Bharti Airtel and Sun Pharma have curated financial research; L&T also has a current-order analysis. Current stories age out of real-time windows. Historical events retain their actual dates and never appear as fresh filings.

## Product and engineering choices

FINN starts with a short, prioritized reading sequence rather than a blank chatbot. Original evidence stays close to the signal. The **Midnight Signal** interface uses graphite, acid yellow, strong typography and a manually controlled reel format. Dense research, exact periods and accounting bases remain easy to inspect.

The ledger is an accountability tool, not a management score. Spending below a stated budget is a variance, not automatically a business failure. A qualitative promise remains Unclear rather than receiving an invented numeric threshold.

| Layer | Implementation |
| --- | --- |
| Frontend | React 19, TypeScript, Vite, Tailwind, custom CSS variables, Lucide |
| Local API | FastAPI, Pydantic, httpx |
| Market data | yfinance / Yahoo Finance EOD |
| Original documents | NSE and issuer PDFs, signature/hash checks, PyMuPDF |
| Retrieval | SQLite FTS5 locally; bounded keyword retrieval in hosted adapter |
| AI | Gemini 2.5 Flash with one Flash-Lite quota fallback, structured JSON, validation and cached answers |
| Hosted runtime | Cloudflare Worker serving frontend + API; `unpdf` for dynamic PDF text extraction |
| Persistence | Local SQLite/files; browser localStorage; bundled durable seed and bounded hosted memory caches |

The Worker adapter makes the hosted prototype self-contained without a separate persistent Python host. No accounts, queues, Redis or scaling infrastructure were added.

## Evidence-bound research

1. Retrieve pages from original issuer/exchange documents.
2. For a ticker without indexed pages, try the official NSE announcement route for the preceding 90 days and at most one suitable transcript/report/results PDF.
3. Ask Gemini for short claims with a real source ID, PDF page and supporting excerpt. Questions and document contents are untrusted data, not instructions.
4. Validate the source, page, normalized exact excerpt, excerpt length and numeric inputs. Equivalent decimal formats and fiscal labels are normalized; numerical unit conversion is not delegated to the model.
5. On a provider 429 quota response, try the configured Flash-Lite model once; do not retry indefinitely. Remove unsupported claims. Cache validated answers for about 12 hours. Provider/key/quota/parse failures return available deterministic evidence and a clear limitation.

Seed comparison arithmetic is performed in Python. Banks use NII/NIM rather than an industrial EBITDA template. Citation validation is conservative but cannot formally prove semantic entailment; material conclusions should still be checked against the original.

## Freshness and resource limits

- Initial EOD seed: **13 November 2026**, retrieved on 15 November 2026. Prices are unadjusted completed-session closes, not live quotes.
- Daily move: `(latest completed close / preceding close − 1) × 100`.
- Relative volume: `latest volume / mean(previous 20 completed-session volumes)`, excluding the latest session from the baseline.
- A session is withheld before 16:00 IST. Failed refreshes retain the last verified snapshot. Corporate actions may affect unadjusted changes.
- In-app refresh updates market data. Filing updates use a scheduled NSE collector every 30 minutes; the open app polls the verified feed every minute. GitHub schedules may be delayed, and exchange failures retain the previous feed with a freshness warning.
- Dynamic acquisition: roughly 16 seconds, one PDF, 5 MB, at most 80 pages, allowlisted HTTPS archive domains and bounded parsing. Scanned/blocked/oversized sources can remain unavailable.
- AI calls use small per-visitor and per-process limits. These caches and limits are sized for a demo, not distributed production abuse prevention.

Yahoo access through yfinance is unofficial. Review provider terms before wider distribution. Original PDFs and the complete extracted corpus are not committed; the manifest records original URLs, dates, page counts and hashes.

## Run locally

Tested with **Node.js 24** and **Python 3.12**. Dependency snapshots are `package-lock.json` and `backend/requirements.lock.txt`.

```powershell
git clone https://github.com/KunalMehra19/finn-investment-agent.git
cd finn-investment-agent
npm ci
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend/requirements.lock.txt
Copy-Item .env.example .env
```

Set `GEMINI_API_KEY` in `.env`; the tested model is `gemini-2.5-flash`. Keys stay server-side. Never use a `VITE_` key variable or commit credentials.

Build the full local document index:

```powershell
.\.venv\Scripts\python.exe backend/scripts/ingest.py
```

Start the API:

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

In a second terminal:

```powershell
npm run dev
```

Open **http://127.0.0.1:5173**. The tracked snapshot also supports keyless browsing and curated research. Without ingestion, a key alone does not create a PDF index; available deterministic evidence remains usable.

For a single-process production preview, run `npm run build`, restart FastAPI and open **http://127.0.0.1:8000**. `npm run preview` alone does not proxy the API.

## Refresh the baseline

The automatic filing feed uses GitHub Actions at minutes 15 and 45 each hour, a separate `data` branch for verified JSON, runtime feed loading and one-minute frontend polling. See [Automatic feed](docs/AUTOMATIC_FEED_REVIEW.md) for verification, setup and limitations. Filing updates require no application redeployment after the initial feed-enabled Worker deployment.

For an automatic local collector, run this alongside FastAPI and Vite:

```powershell
.\.venv\Scripts\python.exe -m backend.scripts.auto_feed --interval 1800
```

The following commands rebuild the bundled baseline manually:

```powershell
.\.venv\Scripts\python.exe backend/scripts/refresh_market.py
.\.venv\Scripts\python.exe backend/scripts/refresh_filings.py
.\.venv\Scripts\python.exe backend/scripts/curate.py
.\.venv\Scripts\python.exe backend/scripts/write_docs.py
```

Ingestion checks signatures/redirects, hashes and page text. `curate.py` asserts that seeded promises match the actual original page. Exchange failures preserve prior filing data; byte-identical notifications are deduplicated before ranking.

## Verify and package

```powershell
.\.venv\Scripts\python.exe -m pytest -q
npm test
npm run build
node scripts/build-worker.mjs
node tests/worker-smoke.mjs
node tests/worker-feed-smoke.mjs
```

Explicit live checks, with a local key:

```powershell
.\.venv\Scripts\python.exe backend/scripts/verify_gemini.py
.\.venv\Scripts\python.exe -m backend.scripts.live_review
```

Optional cached-document preparation: `.\.venv\Scripts\python.exe -m backend.scripts.prewarm HCLTECH ASIANPAINT AXISBANK`.

The Worker embeds built assets and original indexed passages server-side. Run ingestion before packaging for full coverage; without the local corpus, the build uses short verified excerpts with narrower AI coverage. Runtime secrets are configured independently and are never embedded in the bundle. `.openai/hosting.json` identifies the deployment. GitHub Actions verifies builds, data, validation and routes without secrets or live PDF downloads.

## API

| Endpoint | Purpose |
| --- | --- |
| `GET /api/health` | Readiness, document/EOD counts and whether Gemini is configured; no secret values |
| `GET /api/snapshot` | Dated evaluator snapshot |
| `GET /api/watchlist` | Companies, prices and coverage |
| `GET /api/briefing?mode=current&window=7d` | Current ranked filings; separate `mode=replay` |
| `GET /api/company/{ticker}` | Verified identity and EOD/source availability |
| `POST /api/research` | JSON `{ "ticker": "TCS", "question": "What changed in margins?" }` |
| `GET /api/ledger/{ticker}` | Dual-citation guidance comparisons |
| `GET /api/sources/{id}` | Original metadata and PDF location |
| `POST /api/refresh` | Bounded market refresh |

## Repository map

```text
frontend/src/        App, Signal Room, research, watchlist, evidence sheets
backend/app/         API, EOD calculations, retrieval, discovery, Gemini
backend/scripts/     Ingestion, curation, refresh and live checks
backend/data/        Tracked snapshot/provenance; ignored PDFs/index/cache
worker/              Hosted API and dynamic PDF discovery
scripts/             Worker build and authorized repository handoff utility
tests/, backend/tests/  Market, source, citation and fallback tests
docs/                Walkthrough, provenance, design and AI build history
submission/          Email-ready summary, covering email and checklist
```

## Deliberate limits

No trading, P&L, broker execution, login, billing, OS notifications, voice or secondary-news investment research. The ledger is a verified historical sample, not an exhaustive four-quarter scorecard. Annual-report coverage is selective. Dynamic research requires an accessible, parseable original attachment and can fail honestly.

Next steps: broader annual reports, a fixed retrieval evaluation set, deeper analysis of new filings, stronger claim-entailment checks and durable public quotas/caching. These were left out to protect the focused evaluator journey.

## Handoff and verification

[Functional review](docs/FUNCTIONAL_REVIEW.md) · [Live checks](docs/LIVE_FUNCTIONAL_REVIEW.json) · [Deliverables](submission/DELIVERABLES.md) · [Approach summary](submission/APPROACH_SUMMARY.txt) · [Covering email](submission/COVERING_EMAIL.txt)

Rendered 390px/desktop browser QA remains unverified because a saved permission blocked preview access. The owner reviewed and approved the redesigned appearance in the project chat. Build/API/data/live-provider checks are reported separately from visual and gesture testing.

The [redacted chat export](docs/CHAT_LOG_REDACTED.md) includes visible user/assistant messages, excluding credentials, internal reasoning and tool payloads. [AI build history](docs/AI_BUILD_HISTORY.md) records decisions and trade-offs. Nothing has been emailed automatically.
