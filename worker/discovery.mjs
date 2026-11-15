import { getDocumentProxy, extractText } from "unpdf";

const discovered = new Map();
const hosts = new Set([
  "nsearchives.nseindia.com",
  "nsearchives.nseindia.in",
  "archives.nseindia.com",
]);
export const discoveredSources = () =>
  [...discovered.values()].flatMap((r) => r.sources || []);
export function safeDocumentURL(value) {
  try {
    const u = new URL(value);
    return (
      u.protocol === "https:" &&
      hosts.has(u.hostname) &&
      !u.username &&
      !u.password &&
      (!u.port || u.port === "443")
    );
  } catch {
    return false;
  }
}
async function pdfBytes(url, signal) {
  for (let n = 0; n < 3; n++) {
    if (!safeDocumentURL(url)) throw Error("Unapproved source domain");
    const r = await fetch(url, { redirect: "manual", signal });
    if (r.status >= 300 && r.status < 400) {
      url = new URL(r.headers.get("Location"), url).href;
      continue;
    }
    if (!r.ok || Number(r.headers.get("Content-Length")) > 5_000_000)
      throw Error("PDF unavailable or oversized");
    const reader = r.body.getReader(),
      chunks = [];
    let length = 0;
    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        length += value.length;
        if (length > 5_000_000) throw Error("PDF size limit");
        chunks.push(value);
      }
    } finally {
      await reader.cancel();
    }
    const bytes = new Uint8Array(length);
    let offset = 0;
    for (const chunk of chunks) {
      bytes.set(chunk, offset);
      offset += chunk.length;
    }
    if (new TextDecoder().decode(bytes.slice(0, 5)) !== "%PDF-")
      throw Error("Response is not a PDF");
    return bytes;
  }
  throw Error("Redirect limit");
}
export async function discover(ticker) {
  const prior = discovered.get(ticker);
  if (prior && prior.expires > Date.now()) return prior;
  const unavailable = {
    sources: [],
    passages: [],
    discovery:
      "No suitable original document was retrieved within the bounded discovery budget.",
    expires: Date.now() + 60000,
  };
  if (!/^[A-Z][A-Z0-9&-]{0,19}$/.test(ticker)) return unavailable;
  const signal = AbortSignal.timeout(16000),
    fmt = (d) =>
      `${String(d.getUTCDate()).padStart(2, "0")}-${String(d.getUTCMonth() + 1).padStart(2, "0")}-${d.getUTCFullYear()}`;
  try {
    const now = new Date(),
      from = new Date(now.getTime() - 90 * 86400000);
    const url = new URL("https://www.nseindia.com/api/corporate-announcements");
    url.search = new URLSearchParams({
      index: "equities",
      symbol: ticker,
      from_date: fmt(from),
      to_date: fmt(now),
    }).toString();
    const r = await fetch(url, {
      headers: { "User-Agent": "Mozilla/5.0", Accept: "application/json" },
      signal,
    });
    if (!r.ok) throw Error("Exchange unavailable");
    const rows = await r.json();
    if (!Array.isArray(rows)) throw Error("Invalid exchange response");
    const row = rows
      .filter(
        (x) =>
          x.symbol === ticker &&
          safeDocumentURL(x.attchmntFile) &&
          /transcript|annual.report|financial.results/i.test(
            x.desc + " " + x.attchmntText,
          ) &&
          !/intimation|schedule|audio|newspaper/i.test(x.desc),
      )
      .sort(
        (a, b) =>
          Number(/transcript/i.test(b.attchmntText)) -
          Number(/transcript/i.test(a.attchmntText)),
      )[0];
    if (!row) throw Error("No suitable attachment");
    const bytes = await pdfBytes(row.attchmntFile, signal);
    const hash = [
      ...new Uint8Array(await crypto.subtle.digest("SHA-256", bytes)),
    ]
      .map((b) => b.toString(16).padStart(2, "0"))
      .join("");
    let timer;
    const parsed = await Promise.race([
      (async () => {
        const pdf = await getDocumentProxy(bytes, {
          maxImageSize: 1000000,
          isEvalSupported: false,
        });
        try {
          if (pdf.numPages > 80) throw Error("Page limit");
          return await extractText(pdf);
        } finally {
          await pdf.destroy();
        }
      })(),
      new Promise((_, reject) => {
        timer = setTimeout(() => reject(Error("Parse timeout")), 2500);
      }),
    ]).finally(() => clearTimeout(timer));
    const text = parsed.text;
    if (!Array.isArray(text) || text.join("").length < 100)
      throw Error("No usable PDF text");
    const parts = String(row.an_dt).match(
        /^(\d{2})-([A-Za-z]{3})-(\d{4}) (\d{2}:\d{2}:\d{2})$/,
      ),
      months = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
      ];
    const published = parts
      ? `${parts[3]}-${String(months.indexOf(parts[2]) + 1).padStart(2, "0")}-${parts[1]}T${parts[4]}+05:30`
      : null;
    const id = "dynamic-" + ticker + "-" + hash.slice(0, 12),
      source = {
        id,
        ticker,
        title: row.attchmntText || row.desc,
        kind: /transcript/i.test(row.attchmntText)
          ? "Transcript"
          : "Exchange filing",
        period: "Period in original document",
        published,
        url: row.attchmntFile,
        pages: parsed.totalPages,
        page: 1,
        excerpt: "",
        status: "verified",
        sha256: hash,
        retrieved_at: new Date().toISOString(),
      };
    const result = {
      sources: [source],
      passages: text.map((s, i) => ({
        ticker,
        source_id: id,
        page: i + 1,
        text: s.replace(/\s+/g, " ").slice(0, 7500),
      })),
      discovery:
        "Original NSE attachment retrieved and indexed for this request.",
      expires: Date.now() + 43200000,
    };
    if (discovered.size >= 24)
      discovered.delete(discovered.keys().next().value);
    discovered.set(ticker, result);
    return result;
  } catch {
    discovered.set(ticker, unavailable);
    return unavailable;
  }
}
