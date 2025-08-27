// node-bench/common-bench.js
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

function flatFindTrkpts(node, hits) {
  if (!node || typeof node !== 'object') return;
  if (node.trkpt) {
    const pts = Array.isArray(node.trkpt) ? node.trkpt : [node.trkpt];
    for (const p of pts) hits.push(p);
  }
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
  let c = 0;
  for (const pt of hits) {
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
      force,
      speed: 'normal',
    });
    parser.parse(fitBuf, (err, data) => {
      if (err) return reject(err);
      const recs = Array.isArray(data.records) ? data.records : [];
      let c = 0;
      for (const r of recs) {
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

async function bench(n, fn) {
  const times = [];
  for (let i = 0; i < n; i++) {
    const t0 = performance.now();
    await fn();
    times.push(performance.now() - t0);
  }
  return stats(times);
}

module.exports = {
  stats,
  flatFindTrkpts,
  parseGpxCountPoints,
  parseFitCountRecords,
  bench,
  fs,
  path
};
