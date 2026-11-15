import assert from "node:assert/strict";
import { createServer } from "node:http";
import fs from "node:fs";
import worker from "../dist/server/index.js";

const base = JSON.parse(fs.readFileSync("backend/data/demo.json"));
const published = new Date().toISOString();
const source = {
  ...base.sources.find((s) => s.id === base.current_stories[0].source_id),
  id: "smoke-new-filing-source",
};
const story = {
  ...base.current_stories[0],
  id: "smoke-new-filing",
  source_id: source.id,
  published,
};
const feed = {
  schema_version: 1,
  current_stories: [story],
  sources: [source],
  filing_coverage: { status: "checked", checked_at: published },
  feed_status: { state: "fresh", last_success_at: published },
};
const server = createServer((_req, res) => {
  res.writeHead(200, { "Content-Type": "application/json" });
  res.end(JSON.stringify(feed));
});
await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
try {
  const env = { FINN_FEED_URL: `http://127.0.0.1:${server.address().port}/feed.json` };
  const request = (path) => worker.fetch(new Request("https://finn.test" + path), env, {});
  const snapshot = await (await request("/api/snapshot")).json();
  assert.equal(snapshot.feed_status.state, "fresh");
  assert.equal(snapshot.current_stories[0].id, story.id);
  assert.deepEqual(snapshot.stories, base.stories);
  assert.deepEqual(snapshot.insights, base.insights);
  const briefing = await (await request("/api/briefing?mode=current&window=24h")).json();
  assert.equal(briefing.stories[0].id, story.id);
  const citation = await request("/api/sources/" + source.id);
  assert.equal(citation.status, 200);
  assert.equal((await citation.json()).id, source.id);
  console.log("Built Worker loads a new filing over HTTP into snapshot and briefing, resolves its new citation, and preserves replay/research.");
} finally {
  server.closeAllConnections();
  await new Promise((resolve) => server.close(resolve));
}
