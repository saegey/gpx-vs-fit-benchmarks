#!/usr/bin/env node
/* eslint-disable no-console */
const fs = require('fs');
const { performance } = require('perf_hooks');
const FitParser = require('fit-file-parser').default || require('fit-file-parser');
const { XMLParser } = require('fast-xml-parser');
const path = require("node:path");

function stats(times) {
  const arr = times.slice().sort((a, b) => a - b);
  const mean = arr.reduce((s, x) => s + x, 0) / arr.length;
  const p50 = arr[Math.floor(arr.length * 0.5)];
  const p95 = arr[Math.max(0, Math.floor(arr.length * 0.95) - 1)];
  return { mean, p50, p95, min: arr[0], max: arr[arr.length - 1], n: arr.length };
}

function fmt(ms) {
  return `${ms.toFixed(2)}ms`;
}

function flatFindTrkpts(node, hits) {
  if (!node || typeof node !== 'object') return;
  // fast-xml-parser creates arrays for repeated nodes
  if (node.trkpt) {
    const pts = Array.isArray(node.trkpt) ? node.trkpt : [node.trkpt];
    for (const p of pts) hits.push(p);
  }
  // Recurse into common containers
  for (const k of Object.keys(node)) {
    const v = node[k];
    if (Array.isArray(v)) v.forEach((x) => flatFindTrkpts(x, hits));
    else if (typeof v === 'object') flatFindTrkpts(v, hits);
  }
}

function parseGpxCountPoints(xmlBuf) {
  const parser = new XMLParser({
    ignoreAttributes: false,
    attributeNamePrefix: '@_',
    trimValues: true,
  });
  const doc = parser.parse(xmlBuf.toString('utf8'));
  const hits = [];
  flatFindTrkpts(doc, hits);
  // Touch common fields to keep work symmetric
  let c = 0;
  for (const pt of hits) {
    // lat/lon may be on attributes; ele/time are child nodes
    const lat = pt['@_lat'];
    const lon = pt['@_lon'];
    const ele = pt.ele;
    const time = pt.time;
    void lat; void lon; void ele; void time;
    c++;
  }
  return c;
}

function parseFitCountRecords(fitBuf, { force = false } = {}) {
  return new Promise((resolve, reject) => {
    const parser = new FitParser({
      force,           // try to continue on minor errors
      speed: 'normal', // 'normal'|'fast' (fast skips some validations)
    });
    parser.parse(fitBuf, (err, data) => {
      if (err) return reject(err);
      // data.records is an array of per-second-ish messages
      const recs = Array.isArray(data.records) ? data.records : [];
      let c = 0;
      for (const r of recs) {
        // touch common fields like we did for GPX
        const lat = r.position_lat;
        const lon = r.position_long;
        const ele = r.altitude;
        const ts = r.timestamp;
        void lat; void lon; void ele; void ts;
        c++;
      }
      resolve(c);
    });
  });
}

async function bench(label, n, fn) {
  const times = [];
  for (let i = 0; i < n; i++) {
    const t0 = performance.now();
    await fn();
    times.push(performance.now() - t0);
  }
  const s = stats(times);
  console.log(
    `${label}: n=${s.n} mean=${fmt(s.mean)} p50=${fmt(s.p50)} p95=${fmt(s.p95)} min=${fmt(s.min)} max=${fmt(s.max)}`
  );
  return s;
}

async function main() {
  // args

  const fitPath = process.argv[2] || path.join(__dirname, "testdata", "BWR_San_Diego_Waffle_Ride_.fit");
  const gpxPath = process.argv[3] || path.join(__dirname, "testdata", "BWR_San_Diego_Waffle_Ride_.gpx");
  const N = Number(process.argv[4] || 25);

  const fitBuf = fs.readFileSync(fitPath);
  const gpxBuf = fs.readFileSync(gpxPath);

  console.log(`Sizes: FIT=${fitBuf.length.toLocaleString()} B  GPX=${gpxBuf.length.toLocaleString()} B`);

  // One untimed pass to get counts and verify parity
  const gpxCount = parseGpxCountPoints(gpxBuf);
  const fitCount = await parseFitCountRecords(fitBuf, { force: true });
  console.log(`Record/point counts: fit_records=${fitCount}  gpx_points=${gpxCount}`);

  // Timed runs
  const fitStats = await bench('FIT (fit-file-parser)', N, async () => {
    await parseFitCountRecords(fitBuf, { force: true });
  });

  const gpxStats = await bench('GPX (fast-xml-parser)', N, async () => {
    parseGpxCountPoints(gpxBuf);
  });

  console.log(`\nSpeedup (GPX/FIT mean): ${(gpxStats.mean / fitStats.mean).toFixed(2)}x`);
  console.log(`File size ratio (GPX/FIT): ${(gpxBuf.length / fitBuf.length).toFixed(2)}x`);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});