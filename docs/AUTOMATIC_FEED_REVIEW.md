# Automatic filing feed

## How updates flow

1. GitHub Actions runs the existing Python NSE collector at minutes 15 and 45 each hour, or on manual dispatch. GitHub schedules are best effort and may be delayed.
2. The collector verifies original attachment PDFs, hashes, timestamps and source metadata; classifies new events using category rules; ranks materiality; deduplicates; and retains routine records. New titles/summaries use original exchange metadata, not hardcoded company-event answers. Existing editorial enhancements are not required for new events.
3. A public JSON feed is committed on the separate `data` branch. Main/application code is not rebuilt or redeployed per filing update. The workflow uses the built-in GitHub token; no Gemini key or personal token is needed. Only verified metadata/story text is published, not PDF contents or credentials.
4. The Worker reads that feed at most once per minute, validates references/domains and retains its last good copy on failure. Cold starts fall back to the bundled snapshot. Data older than two hours is marked stale.
5. The frontend fetches the API every minute while visible, on tab focus and on returning to the tab. Current-window filtering and the existing reel component render the new list; replay and research remain separate.

Unchanged limitation: new filings are surfaced with factual exchange metadata and category-based significance, not automatically generated deep financial analysis. Existing research remains grounded in its explicitly dated indexed documents.

## Review locally

Run `.\.venv\Scripts\python.exe -m backend.scripts.auto_feed --once` for a single verified update, or omit `--once` for the 30-minute loop. Run FastAPI and Vite as described in the README. Local API reads `backend/data/live_feed.json`; the frontend polls it automatically. Generated feed/cache files are ignored by Git.

For initial hosted setup: push the workflow/code, deploy the feed-enabled Worker once, and manually run **Refresh verified filing feed** once to create the initial data-branch feed. Thereafter the schedule updates filing data independently. The workflow and public API expose timestamps so that an operator can distinguish a recent successful update from a retained snapshot.

## Verification

Tests cover adding a new event without changing replay/research, deduplication, missing/unsafe citations, future timestamps, cached failure state across subsequent requests, and cold-start fallback. Live NSE ingestion is checked separately; passing mocks does not prove the future GitHub scheduler or hosting region can reach NSE. Failures remain visible through freshness metadata.

The 16 November 2026 local live review retrieved 25 announcements and verified 24 unique attachment-backed updates for the tracked companies. The built Worker integration check uses an HTTP feed containing a previously unknown filing/source ID and verifies that it reaches the snapshot, current briefing and source endpoint without changing replay or research.
