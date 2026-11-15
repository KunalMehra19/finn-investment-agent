import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import { buildSync } from "esbuild";
// Bundle the actual hosted validation implementation for a Node test environment.
buildSync({
  entryPoints: ["worker/api.mjs"],
  outfile: "outputs/worker-test.mjs",
  bundle: true,
  format: "esm",
  platform: "node",
  target: "node22",
});
const { validateClaim, summarizeChart } =
  await import("../outputs/worker-test.mjs");
test("hosted claims reject invented title values and quotes", () => {
  const pages = [{ source_id: "a", page: 1, text: "Revenue was 100 crore." }];
  const claim = {
    title: "Revenue",
    text: "Revenue was 100 crore.",
    source_id: "a",
    page: 1,
    supporting_excerpt: "Revenue was 100 crore.",
  };
  assert.ok(validateClaim(claim, pages));
  assert.ok(!validateClaim({ ...claim, title: "Revenue 900" }, pages));
  assert.ok(!validateClaim({ ...claim, page: 2 }, pages));
  assert.ok(
    !validateClaim(
      { ...claim, supporting_excerpt: "Revenue was 900 crore." },
      pages,
    ),
  );
});
test("hosted market calculations reject null volume and exclude intraday", () => {
  const timestamps = Array.from(
    { length: 23 },
    (_, i) =>
      Date.parse(`2026-10-${String(i + 1).padStart(2, "0")}T10:00:00Z`) / 1000,
  );
  const q = { close: Array(23).fill(100), volume: Array(23).fill(100) };
  q.close[20] = 110;
  q.volume[20] = 500;
  q.volume[21] = null;
  q.close[22] = 900;
  const r = summarizeChart(
    { meta: {}, timestamp: timestamps, indicators: { quote: [q] } },
    new Date("2026-10-23T06:00:00Z"),
  );
  assert.equal(r.as_of, "2026-10-21");
  assert.equal(r.move, 10);
  assert.equal(r.relative_volume, 5);
});
