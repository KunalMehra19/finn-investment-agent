import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
test("fifteen snapshots contain no fabricated or missing values", () => {
  const d = JSON.parse(fs.readFileSync("backend/data/demo.json"));
  assert.equal(d.companies.length, 15);
  for (const c of d.companies) {
    const p = d.market.prices[c.ticker];
    assert.ok(p.close > 0);
    assert.ok(p.history.length >= 21);
    assert.equal(p.volume, p.history.at(-1).volume);
    assert.ok(p.as_of <= d.market.fetched_at.slice(0, 10));
    const baseline =
      p.history.slice(-21, -1).reduce((s, r) => s + r.volume, 0) / 20;
    assert.equal(
      p.relative_volume,
      Math.round((p.volume / baseline) * 100) / 100,
    );
  }
});
test("all factual records resolve to real PDF locations", () => {
  const d = JSON.parse(fs.readFileSync("backend/data/demo.json"));
  for (const rows of Object.values(d.facts)) {
    for (const f of rows) {
      const source = d.sources.find((s) => s.id === f.source_id);
      assert.ok(source);
      assert.ok(f.page > 0 && f.page <= source.pages);
      assert.equal(source.status, "verified");
    }
  }
  for (const rows of Object.values(d.insights))
    for (const i of rows)
      assert.ok(
        d.sources.some((s) => s.id === i.source_id && i.page <= s.pages),
      );
});
