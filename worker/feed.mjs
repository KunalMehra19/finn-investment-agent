const DEFAULT_URL =
  "https://raw.githubusercontent.com/KunalMehra19/finn-investment-agent/data/feed.json";
export function validateFeed(feed) {
  if (
    feed?.schema_version !== 1 ||
    !Array.isArray(feed.current_stories) ||
    !Array.isArray(feed.sources) ||
    !feed.filing_coverage ||
    !feed.feed_status
  )
    return false;
  if (feed.current_stories.length > 500 || feed.sources.length > 500)
    return false;
  const hosts = new Set([
    "nsearchives.nseindia.com",
    "nsearchives.nseindia.in",
    "archives.nseindia.com",
  ]);
  const sources = new Map();
  for (const s of feed.sources) {
    if (
      ![
        "id",
        "ticker",
        "title",
        "kind",
        "period",
        "url",
        "sha256",
        "retrieved_at",
      ].every((k) => typeof s[k] === "string")
    )
      return false;
    let u;
    try {
      u = new URL(s.url);
    } catch {
      return false;
    }
    if (
      u.protocol !== "https:" ||
      !hosts.has(u.hostname) ||
      u.username ||
      (u.port && u.port !== "443") ||
      u.password ||
      s.status !== "verified" ||
      !Number.isInteger(s.pages) ||
      s.pages < 1 ||
      !s.sha256?.match(/^[a-f0-9]{64}$/)
    )
      return false;
    sources.set(s.id, s);
  }
  for (const s of feed.current_stories) {
    if (
      ![
        "id",
        "ticker",
        "title",
        "display_title",
        "summary",
        "why",
        "source_id",
        "category",
        "origin",
        "published",
      ].every((k) => typeof s[k] === "string") ||
      !Number.isInteger(s.page)
    )
      return false;
    const source = sources.get(s.source_id);
    if (
      !source ||
      source.ticker !== s.ticker ||
      !Number.isFinite(Date.parse(s.published)) ||
      Date.parse(s.published) > Date.now() + 300000 ||
      s.page < 1 ||
      s.page > source.pages ||
      typeof s.title !== "string" ||
      typeof s.summary !== "string" ||
      typeof s.why !== "string" ||
      !Number.isFinite(s.priority) ||
      typeof s.routine !== "boolean"
    )
      return false;
  }
  return Number.isFinite(Date.parse(feed.feed_status.last_success_at));
}
export function mergeFeed(base, feed, failed = false, now = Date.now()) {
  if (!feed)
    return {
      ...base,
      feed_status: {
        state: "baseline",
        message:
          "Automatic feed unavailable; showing bundled verified snapshot.",
        last_success_at: base.filing_coverage?.checked_at,
      },
    };
  const stale =
    failed ||
    feed.feed_status.state === "stale" ||
    now - Date.parse(feed.feed_status.last_success_at) > 7200000;
  return {
    ...base,
    current_stories: feed.current_stories,
    sources: [
      ...new Map(
        [...base.sources, ...feed.sources].map((s) => [s.id, s]),
      ).values(),
    ],
    filing_coverage: feed.filing_coverage,
    feed_status: {
      ...feed.feed_status,
      state: stale ? "stale" : "fresh",
      message: stale
        ? "Refresh delayed; retaining the last verified filing feed."
        : feed.feed_status.message,
    },
  };
}
export function createFeedReader(fetcher = fetch, clock = Date.now) {
  let good = null,
    checked = -Infinity,
    inFlight = null,
    lastFailed = false;
  return async (base, url = DEFAULT_URL) => {
    if (clock() - checked < 60000)
      return mergeFeed(base, good, lastFailed, clock());
    if (inFlight)
      return inFlight.then((result) =>
        mergeFeed(base, result.feed, result.failed, clock()),
      );
    inFlight = (async () => {
      let failed = false;
      try {
        const r = await fetcher(url, {
          signal: AbortSignal.timeout(5000),
          headers: { Accept: "application/json" },
        });
        if (!r.ok || Number(r.headers.get("Content-Length")) > 1500000)
          throw Error();
        const text = await r.text();
        if (text.length > 1500000) throw Error();
        const body = JSON.parse(text);
        if (!validateFeed(body)) throw Error();
        good = body;
      } catch {
        failed = true;
      }
      checked = clock();
      lastFailed = failed;
      return { feed: good, failed };
    })();
    try {
      const r = await inFlight;
      return mergeFeed(base, r.feed, r.failed, clock());
    } finally {
      inFlight = null;
    }
  };
}
export const readFeed = createFeedReader();
