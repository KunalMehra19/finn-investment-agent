# FINN · From Signal to Evidence

A compact Indian-equity research desk built for an evaluator. React + TypeScript + Vite + Tailwind on the front; FastAPI, SQLite FTS5, PyMuPDF and yfinance locally. A small Cloudflare Worker adapter serves the hosted version, including its API, without requiring a separate Python host.

## Run on Windows

```powershell
npm install
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend/requirements.txt
```

In one terminal:

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

In another:

```powershell
npm run dev
```

Open http://127.0.0.1:5173. The checked-in, dated snapshot supports a useful demo immediately. No login or Gemini key is needed to browse briefings, inspect evidence, use the editorial research collection, or open the promise ledger. Seed EOD prices survive a clean clone and provider failures.

## Refresh and index genuine sources

```powershell
.\.venv\Scripts\python.exe backend/scripts/ingest.py
.\.venv\Scripts\python.exe backend/scripts/refresh_market.py
.\.venv\Scripts\python.exe backend/scripts/refresh_filings.py
.\.venv\Scripts\python.exe backend/scripts/curate.py
```

The PDF downloader accepts only listed HTTPS issuer/exchange domains, validates redirects and PDF signatures, and caps file size. PDFs, the full extracted library and SQLite index are local ignored files. The tracked source manifest contains original URLs, hashes, dates and page counts. `curate.py` checks verbatim management promises against actual downloaded pages before producing a snapshot. Current and replay records remain separate.

`refresh_filings.py` makes a bounded best-effort NSE request. A failed refresh retains the last successful snapshot. Identical PDF notifications are deduplicated before materiality ranking. Routine notices remain accessible. Filings in the app are a retrieved window, not a claim of continuous market surveillance.

## Enable Gemini

Copy `.env.example` to `.env` and set `GEMINI_API_KEY`. `GEMINI_MODEL` is configurable; the supplied default is `gemini-3.8-flash`. Restart the API after configuration. Use a model available to your Google account. Never put the key in a `VITE_` variable or commit `.env`.

Research retrieves actual PDF pages through SQLite FTS5, asks Gemini for structured claims, validates source IDs, real page numbers, exact supporting excerpts and numerical inputs, and removes unsupported claims. A timeout, bad key, quota error or invalid response falls back to dated editorial evidence. Syntactic citation validation cannot formally prove semantic entailment; review material AI conclusions against the original documents.

The hosted Worker uses the same verified source snapshot and server-side primary passages. Set `GEMINI_API_KEY` and `GEMINI_MODEL` as hosting runtime secrets to enable hosted AI. The full local library is used when packaging locally; a clean clone without ingestion can still build using the short verified excerpts, with narrower AI coverage.

## Verify

```powershell
npm test
.\.venv\Scripts\python.exe -m pytest -q
npm run build
node scripts/build-worker.mjs
node tests/worker-smoke.mjs
```

For a single-process local production preview, build the frontend first, then restart FastAPI and open http://127.0.0.1:8000. FastAPI serves `dist/` as well as the API. `npm run preview` alone has no API proxy; use the Vite development server or FastAPI for the complete local app.

## Structure

- `frontend/src/`: responsive app, sheets, research, ledger, watchlist and source library.
- `backend/app/`: API, market calculations, full-text retrieval and Gemini validation.
- `backend/scripts/`: allowlisted ingestion, source curation and market/filing refresh.
- `backend/data/`: durable evaluator snapshot and verified source metadata.
- `worker/api.mjs`: hosted API adapter; generated Worker embeds built assets and selected original pages server-side.
- `docs/`: demo guide, source manifest, decisions, validation, AI build history and draft submission note.

## Deliberate limits

- No accounts, trading, portfolio P&L, billing, queues or scaling infrastructure.
- Price and volume are EOD; the exact session date is always shown. Yahoo access is unofficial, and provider access can fail. Review the provider’s usage terms before broader distribution.
- The default view is Current / 7 days. Current / 24 hours can be empty. Filing refresh is performed by the ingestion script; the in-app refresh updates market data only.
- Five core firms have curated financial research, and L&T has a sourced current-order analysis. Not every available PDF has an editorial answer for every question.
- Unfamiliar symbols receive a bounded verified market lookup. Automatic new-ticker annual-report discovery is not implemented; those cases show an explicit partial state.
- Three guidance comparisons are historical. TCS’s FY26 25% operating margin excludes specified one-off costs; that accounting basis is disclosed. Sun Pharma’s qualitative growth target remains `Unclear` instead of imposing an invented threshold.
- The hosted rate limit and fresh-price cache are in memory, appropriate for this small demo. Durable baseline evidence lives in the bundled snapshot.
- The first deployment preserves owner-private Sites access. An evaluator-facing public URL requires an explicit access change. A GitHub repository has not been provisioned.
- Automated browser inspection was declined by the browser access gate. Builds, API checks and data tests passed; visual desktop/390px browser QA remains unverified.

See [the demo guide](docs/DEMO_GUIDE.md), [source manifest](docs/SOURCE_MANIFEST.md) and [build history](docs/AI_BUILD_HISTORY.md).
