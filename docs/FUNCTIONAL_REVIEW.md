# Functional review / 15 November 2026

## Checked

- Real Gemini model discovery verified the provided key without logging it. Local and hosted keys are server-side secrets.
- Real answers for Reliance, TCS, HDFC Bank, Airtel and Sun Pharma returned supported Gemini claims; unsupported portions were discarded as partial where necessary.
- HCLTECH, outside the curated collection, retrieved an original 26-page NSE transcript and produced a cited research answer through the generic discovery path. The live result file records source IDs/pages and elapsed times.
- Eleven Python tests exercise completed-session filtering, exclusion of the latest volume from its baseline, five-company coverage, guidance calculations, real page references, invalid symbols/requests, citation rejection (including invented title numbers), allowed PDF domains and provider-timeout fallback.
- Four Node tests cover the 15 market snapshots, factual source locations, hosted claim rejection and null-volume/intraday handling.
- Hosted Worker smoke checks cover HTML/assets, health, watchlist, snapshot, current briefing, ledger, original source lookup, invalid inputs and keyless research.
- TypeScript and Vite production builds passed. A GitHub Actions workflow repeats offline checks from a clean clone with fixture-based FTS data and no API key.
- Reviewed source-level reel controls, inactive-story inertness, keyboard navigation, immersive Escape/focus containment, localStorage persistence, async stale-answer prevention, selected-company market filtering and reduced-motion rules.
- The chat export is explicitly redacted and excludes internal reasoning/tool payloads. The credential is not part of tracked source or the frontend build.

## Corrections made during this review

1. Configured and tested the Gemini key, instead of leaving only deterministic retrieval active.
2. Kept the fast evidence-extraction model from exhausting its response budget before JSON output.
3. Tightened excerpt/title validation while accepting equivalent decimal formatting, typographic ligatures and fiscal labels.
4. Added bounded generic NSE PDF discovery, dynamic source metadata and source-drawer integration.
5. Added a hosted validated-answer cache and rejected null market volumes.
6. Included linked original promise/outcome pages in retrieval when the curated evidence map is relevant.
7. Made tests independent of ignored local SQLite/PDF files so a clean clone can verify offline.
8. Formatted the frontend/hosted source, documented deployment/setup and prepared evaluator deliverables.

## Limits

Rendered desktop/390px, touch gestures and actual browser focus remain unverified because a saved browser permission blocks preview access. Source review and API tests do not substitute for those checks. The owner approved the redesigned appearance in chat.

Dynamic discovery is best effort and exchange access can differ between local and hosted networks. It is capped and returns a partial state. Snapshots show their actual dates. Citation validation checks provenance and matching text, not a formal semantic proof of every paraphrase.

Public deployment checks are recorded separately in `PUBLIC_ENDPOINT_REVIEW.json` after final publication.
