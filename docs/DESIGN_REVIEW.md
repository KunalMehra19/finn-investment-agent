# FINN / Midnight Signal

Design refresh: 15 November 2026.

## Direction

Industrial / utilitarian, informed by a broadcast control room. The primary action is to notice a financial signal, browse deliberately, then open its original evidence. The anchor is a full-bleed vertical Signal Room: large issue typography, numbered source metadata, an acid-yellow action line and a manually controlled feed. This is a subjective aesthetic decision, not a claim of measured memorability.

Optional subjective DFII: Impact 4 + Fit 4 + Feasibility 5 + Performance 4 − Consistency risk 2 = **15**. This is a discussion aid, not a usability certification.

## System

- Graphite `--bg`, deeper `--deep`, acid `--accent`, off-white `--ink`; all stylesheet colors come from CSS variables. Financial positive/negative/unknown states retain explicit text and semantic colors.
- Existing DM Sans becomes the structural display and body type. Instrument Serif is reserved for exact management quotations. No new fonts or external visual assets were downloaded.
- Eight-pixel spacing rhythm with thin dividers, square controls and asymmetrical layouts. Navigation becomes a horizontal masthead on desktop and a compact mobile bar.
- Motion is limited to manual smooth reel snapping and short sheet transitions. Reduced-motion preferences disable animation and smooth navigation. No autoplay.
- Research, ledger, watchlist, library, command search and evidence sheets share the new palette and typography. The previous theme and its override stylesheet were removed.

## Reels

- Native vertical touch scrolling and scroll snapping, with bounded wheel gestures on desktop.
- Next/previous controls, direct issue selection, progress markers, arrows, Page Up/Down, Home/End and an immersive view.
- Persistent save, original-evidence and investigation controls; expandable analytical context.
- Inactive stories are inert and hidden from the accessibility tree. The active title is announced. Immersive mode traps focus, supports Escape and restores focus; opening an investigation/source exits immersive mode.
- No invented chart, footage or financial statistic is used as background decoration.

## Verification and limits

- TypeScript and production compilation checked. Existing market/source and Worker route smoke checks rerun after implementation.
- Source-level review covered 390px/760px/980px/1200px responsive rules, short-screen immersive rules, long values, keyboard handlers, focus containment, reduced motion, manual navigation, unchanged empty/error states and palette contrast calculations.
- **Rendered visual and interaction QA is not verified.** A new browser review attempt was rejected because a saved permission blocks the local preview origin. No alternate browser or screenshot workaround was used. Actual 390px/desktop rendering, touch gestures and keyboard focus still need a permitted browser session.
