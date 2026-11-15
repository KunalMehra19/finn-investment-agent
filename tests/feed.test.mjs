import { test } from "node:test";
import assert from "node:assert/strict";
import { createFeedReader, validateFeed } from "../worker/feed.mjs";
import fs from "node:fs";
const base = JSON.parse(fs.readFileSync("backend/data/demo.json"));
const now = Date.now();
const makeFeed = () => ({
  schema_version: 1,
  current_stories: [
    {
      ...base.current_stories[0],
      id: "new-event",
      published: new Date(now).toISOString(),
    },
  ],
  sources: base.sources.filter(
    (s) => s.id === base.current_stories[0].source_id,
  ),
  filing_coverage: {
    status: "checked",
    checked_at: new Date(now).toISOString(),
  },
  feed_status: {
    state: "fresh",
    last_success_at: new Date(now).toISOString(),
    last_attempt_at: new Date(now).toISOString(),
  },
});
test("new verified event enters live snapshot, preserving research and replay", async () => {
  const f = makeFeed();
  assert.ok(validateFeed(f));
  const read = createFeedReader(async () => Response.json(f));
  const next = await read(base);
  assert.equal(next.current_stories[0].id, "new-event");
  assert.deepEqual(next.stories, base.stories);
  assert.deepEqual(next.insights, base.insights);
  assert.ok(next.sources.some((s) => s.id === f.current_stories[0].source_id));
  assert.equal(next.feed_status.state, "fresh");
});
test("outage and invalid source retain last good feed with stale status", async () => {
  let time = now,
    count = 0;
  const f = makeFeed();
  const read = createFeedReader(
    async () => {
      count++;
      if (count === 1) return Response.json(f);
      if (count === 2) throw Error("offline");
      const broken = makeFeed();
      broken.sources[0] = {
        ...broken.sources[0],
        url: "https://evil.example/fake.pdf",
      };
      return Response.json(broken);
    },
    () => time,
  );
  await read(base);
  time += 61000;
  let next = await read(base);
  assert.equal(next.feed_status.state, "stale");
  assert.equal(next.current_stories[0].id, "new-event");
  next = await read(base);
  assert.equal(next.feed_status.state, "stale");
  assert.equal(count, 2);
  time += 61000;
  next = await read(base);
  assert.equal(next.current_stories[0].id, "new-event");
  assert.equal(next.feed_status.state, "stale");
});
test("cold start outage uses bundled snapshot, never a blank feed", async () => {
  const read = createFeedReader(async () => new Response("", { status: 503 }));
  const next = await read(base);
  assert.deepEqual(next.current_stories, base.current_stories);
  assert.equal(next.feed_status.state, "baseline");
});
test("missing citations and future timestamps rejected", () => {
  let f = makeFeed();
  f.sources = [];
  assert.equal(validateFeed(f), false);
  f = makeFeed();
  f.current_stories[0].published = new Date(now + 86400000).toISOString();
  assert.equal(validateFeed(f), false);
});
