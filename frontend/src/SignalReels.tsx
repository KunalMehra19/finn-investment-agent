import { useEffect, useRef, useState } from "react";
import {
  ArrowDown,
  ArrowUp,
  ArrowUpRight,
  Bookmark,
  Check,
  FileText,
  Maximize2,
  Minimize2,
  ShieldCheck,
  X,
} from "lucide-react";
import type { Company, Dataset, Story } from "./types";

type Props = {
  stories: Story[];
  data: Dataset;
  index: number;
  onIndex: (n: number) => void;
  saved: string[];
  onSave: (id: string) => void;
  onInvestigate: (s: Story) => void;
  onEvidence: (id: string, page: number) => void;
  mode: string;
};
const pad = (n: number) => String(n).padStart(2, "0");
const date = (s: string) =>
  new Date(s.length === 10 ? s + "T12:00:00+05:30" : s).toLocaleDateString(
    "en-IN",
    {
      day: "2-digit",
      month: "short",
      year: "numeric",
      timeZone: "Asia/Kolkata",
    },
  );

export default function SignalReels({
  stories,
  data,
  index,
  onIndex,
  saved,
  onSave,
  onInvestigate,
  onEvidence,
  mode,
}: Props) {
  const [immersive, setImmersive] = useState(false),
    [expanded, setExpanded] = useState<string | null>(null);
  const viewport = useRef<HTMLDivElement>(null),
    returnFocus = useRef<HTMLElement | null>(null),
    wheelLock = useRef(0);
  const current = stories.length ? index % stories.length : 0;
  const reduced = () =>
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const jump = (n: number) => {
    if (!viewport.current) return;
    const next = Math.max(0, Math.min(stories.length - 1, n));
    viewport.current.scrollTo({
      top: next * viewport.current.clientHeight,
      behavior: reduced() ? "instant" : "smooth",
    });
    onIndex(next);
  };
  useEffect(() => {
    const el = viewport.current;
    if (el) el.scrollTop = current * el.clientHeight;
  }, [immersive, stories.map((s) => s.id).join("|")]);
  useEffect(() => {
    const el = viewport.current;
    if (!el) return;
    const handler = (e: WheelEvent) => {
      if (Math.abs(e.deltaY) < 8) return;
      const next =
        Math.round(el.scrollTop / el.clientHeight) + (e.deltaY > 0 ? 1 : -1);
      if (!immersive && (next < 0 || next >= stories.length)) return;
      e.preventDefault();
      if (Date.now() < wheelLock.current) return;
      wheelLock.current = Date.now() + 650;
      jump(next);
    };
    el.addEventListener("wheel", handler, { passive: false });
    return () => el.removeEventListener("wheel", handler);
  }, [stories.length, immersive]);
  useEffect(() => {
    if (!immersive) return;
    returnFocus.current = document.activeElement as HTMLElement;
    const old = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    viewport.current?.focus();
    const key = (e: KeyboardEvent) => {
      if (e.key === "Escape") setImmersive(false);
      if (e.key === "Tab") {
        const host = viewport.current?.closest(".signal-reels");
        const nodes = Array.from(
          host?.querySelectorAll<HTMLElement>(
            'button,a[href],[tabindex="0"]',
          ) || [],
        ).filter(
          (el) =>
            el.getClientRects().length &&
            !el.matches(":disabled") &&
            !el.closest("[inert]"),
        );
        const first = nodes[0],
          last = nodes.at(-1);
        if (e.shiftKey && document.activeElement === first) {
          e.preventDefault();
          last?.focus();
        } else if (!e.shiftKey && document.activeElement === last) {
          e.preventDefault();
          first?.focus();
        }
      }
    };
    window.addEventListener("keydown", key);
    return () => {
      document.body.style.overflow = old;
      window.removeEventListener("keydown", key);
      returnFocus.current?.focus();
    };
  }, [immersive]);
  const inspect = (id: string, page: number) => {
    setImmersive(false);
    onEvidence(id, page);
  };
  const investigate = (story: Story) => {
    setImmersive(false);
    onInvestigate(story);
  };
  return (
    <section
      className={`signal-reels ${immersive ? "immersive" : ""}`}
      aria-label="Signal reels"
      {...(immersive ? { role: "dialog", "aria-modal": true } : {})}
    >
      <header className="reel-masthead">
        <span>
          <i />
          THE SIGNAL ROOM
        </span>
        <span>
          {mode === "replay" ? "HISTORICAL REPLAY" : "NSE / CURRENT FILINGS"}
        </span>
        <button
          onClick={() => setImmersive((v) => !v)}
          aria-label={
            immersive ? "Exit immersive reels" : "Open immersive reels"
          }
        >
          {immersive ? <Minimize2 size={15} /> : <Maximize2 size={15} />}
          <span>{immersive ? "Exit" : "Enter reels"}</span>
        </button>
        {immersive && (
          <button
            className="reel-close"
            onClick={() => setImmersive(false)}
            aria-label="Close reels"
          >
            <X size={20} />
          </button>
        )}
      </header>
      <p className="visually-hidden" role="status" aria-live="polite">
        Story {current + 1} of {stories.length}: {stories[current]?.title}
      </p>
      <div className="reel-layout">
        <div
          className="reel-viewport"
          ref={viewport}
          tabIndex={0}
          role="region"
          aria-label="Swipe up or down to browse financial stories"
          onScroll={(e) => {
            const el = e.currentTarget,
              n = Math.round(el.scrollTop / el.clientHeight);
            if (n !== current && n < stories.length) onIndex(n);
          }}
          onKeyDown={(e) => {
            if (
              (e.target as HTMLElement).tagName === "BUTTON" ||
              (e.target as HTMLElement).tagName === "A"
            )
              return;
            const moves: Record<string, number> = {
              ArrowDown: current + 1,
              ArrowUp: current - 1,
              ArrowRight: current + 1,
              ArrowLeft: current - 1,
              PageDown: current + 1,
              PageUp: current - 1,
              Home: 0,
              End: stories.length - 1,
            };
            if (e.key in moves) {
              e.preventDefault();
              jump(moves[e.key]);
            }
          }}
        >
          {stories.map((story, n) => {
            const c = data.companies.find(
                (c) => c.ticker === story.ticker,
              ) as Company,
              original = data.sources.find((s) => s.id === story.source_id),
              facts = (data.facts[story.ticker] || [])
                .filter((f) => f.source_id === story.source_id)
                .slice(0, 2);
            return (
              <article
                key={story.id}
                className={`signal-frame ${n === current ? "is-current" : ""}`}
                aria-label={`Story ${n + 1} of ${stories.length}: ${story.title}`}
                aria-hidden={n !== current}
                inert={n !== current ? true : undefined}
              >
                <div className="reel-graticule" aria-hidden="true" />
                <div className="reel-topline">
                  <div className="reel-company">
                    <span className="reel-monogram">{c.initials}</span>
                    <div>
                      <strong>{c.short}</strong>
                      <span>NSE:{c.ticker}</span>
                    </div>
                  </div>
                  <span className="reel-category">{story.category}</span>
                </div>
                <div className="reel-editorial">
                  <div className="reel-kicker">
                    <span>{pad(n + 1)}</span>
                    <span>
                      {story.category === "Orders"
                        ? "THE NEXT CHAPTER"
                        : story.category === "Management"
                          ? "PEOPLE & POWER"
                          : story.category === "Transcript"
                            ? "ON THE RECORD"
                            : "INSIDE THE NUMBERS"}
                    </span>
                    <span className="reel-datestamp">
                      {date(story.published)}
                    </span>
                  </div>
                  <h2>{story.display_title}</h2>
                  <p className="reel-summary">{story.summary}</p>
                  {facts.length > 0 && (
                    <div className="reel-facts">
                      {facts.map((f) => (
                        <button
                          key={f.label}
                          onClick={() => inspect(f.source_id, f.page)}
                        >
                          <span>
                            {f.label}
                            <ArrowUpRight size={12} />
                          </span>
                          <strong>{f.value}</strong>
                          <small>{f.period}</small>
                        </button>
                      ))}
                    </div>
                  )}
                </div>
                <aside className="reel-actions">
                  <button
                    aria-label={
                      saved.includes(story.id) ? "Unsave reel" : "Save reel"
                    }
                    aria-pressed={saved.includes(story.id)}
                    onClick={() => onSave(story.id)}
                  >
                    <Bookmark
                      size={19}
                      fill={saved.includes(story.id) ? "currentColor" : "none"}
                    />
                    <span>Save</span>
                  </button>
                  <button
                    aria-label="Inspect reel evidence"
                    onClick={() => inspect(story.source_id, story.page)}
                  >
                    <FileText size={19} />
                    <span>Source</span>
                  </button>
                </aside>
                <div className="reel-bottom">
                  <button
                    className="reel-context"
                    aria-expanded={expanded === story.id}
                    onClick={() =>
                      setExpanded((v) => (v === story.id ? null : story.id))
                    }
                  >
                    <span>THE IMPLICATION</span>
                    <span>{expanded === story.id ? "−" : "+"}</span>
                  </button>
                  {expanded === story.id && (
                    <p className="reel-context-text">{story.why}</p>
                  )}
                  <div className="reel-source-line">
                    <ShieldCheck size={13} />
                    <span>
                      {story.origin === "NSE filing"
                        ? "NSE ORIGINAL"
                        : "ISSUER ORIGINAL"}{" "}
                      / PDF P.{story.page}
                    </span>
                    <span>{original?.pages} PAGES</span>
                  </div>
                  <button
                    className="reel-investigate"
                    onClick={() => investigate(story)}
                  >
                    <span>Investigate the story</span>
                    <ArrowUpRight size={21} />
                  </button>
                </div>
                <span className="reel-watermark" aria-hidden="true">
                  {pad(n + 1)}
                </span>
              </article>
            );
          })}
        </div>
        <aside className="reel-index">
          <div className="reel-index-heading">
            <span>IN THIS EDITION</span>
            <strong>
              {pad(stories.length)}
              <small> SIGNALS</small>
            </strong>
          </div>
          {stories.map((s, n) => (
            <button
              key={s.id}
              className={n === current ? "active" : ""}
              onClick={() => jump(n)}
              aria-label={`Go to reel ${n + 1}: ${s.title}`}
              aria-current={n === current ? "true" : undefined}
            >
              <span>{pad(n + 1)}</span>
              <div>
                <strong>
                  {data.companies.find((c) => c.ticker === s.ticker)?.short}
                </strong>
                <p>{s.title}</p>
              </div>
              {n === current && <i />}
            </button>
          ))}
          <div className="reel-manual">
            <span>
              <Check size={12} />
              YOU SET THE PACE
            </span>
            <p>
              Swipe. Read. Verify.
              <br />
              No autoplay.
            </p>
          </div>
        </aside>
      </div>
      <footer className="reel-navigation">
        <span className="reel-position">
          {pad(current + 1)}
          <span> / {pad(stories.length)}</span>
        </span>
        <div className="reel-dots">
          {stories.map((s, n) => (
            <button
              key={s.id}
              onClick={() => jump(n)}
              className={n === current ? "active" : ""}
              aria-label={`Show reel ${n + 1}`}
            />
          ))}
        </div>
        <span className="reel-hint">SCROLL OR SWIPE TO CONTINUE</span>
        <div className="reel-controls">
          <button
            aria-label="Previous reel"
            disabled={current === 0}
            onClick={() => jump(current - 1)}
          >
            <ArrowUp size={17} />
          </button>
          <button
            aria-label="Next reel"
            disabled={current === stories.length - 1}
            onClick={() => jump(current + 1)}
          >
            <ArrowDown size={17} />
          </button>
        </div>
      </footer>
    </section>
  );
}
