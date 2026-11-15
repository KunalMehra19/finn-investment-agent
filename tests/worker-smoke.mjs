import assert from "node:assert/strict";
import worker from "../dist/server/index.js";
const request = (path, init) =>
  worker.fetch(new Request("https://finn.test" + path, init), {}, {});
for (const path of [
  "/",
  "/api/health",
  "/api/watchlist",
  "/api/snapshot",
  "/api/briefing?mode=current&window=7d",
  "/api/ledger/TCS",
  "/api/sources/ril-fy25",
]) {
  const r = await request(path);
  assert.equal(r.status, 200, path);
  console.log("OK", path);
}
const home = await (await request("/")).text();
const assets = [...home.matchAll(/(?:src|href)="(\/assets\/[^\"]+)"/g)].map(
  (m) => m[1],
);
for (const asset of assets) assert.equal((await request(asset)).status, 200);
const answer = await (
  await request("/api/research", {
    method: "POST",
    body: JSON.stringify({
      ticker: "TCS",
      question: "What changed in margins?",
    }),
  })
).json();
assert.ok(answer.insights.length);
assert.equal(answer.status, "verified");
assert.equal((await request("/api/sources/no-such-id")).status, 404);
assert.equal((await request("/api/company/BAD!SYMBOL")).status, 400);
console.log(
  "Worker routes, assets, source lookup, validation and keyless research passed.",
);
