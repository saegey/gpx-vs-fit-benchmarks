#!/usr/bin/env node
const { parseGpxCountPoints, bench, fs, path } = require('./common-bench');

async function main() {
  const gpxPath = process.argv[2] || path.join(__dirname, "testdata", "BWR_San_Diego_Waffle_Ride_.gpx");
  const N = Number(process.argv[3] || 25);
  const gpxBuf = fs.readFileSync(gpxPath);

  const gpxStats = await bench(N, async () => {
    parseGpxCountPoints(gpxBuf);
  });

  const result = {
    format: "GPX",
    parser: "fast-xml-parser",
    iterations: N,
    mean_ms: gpxStats.mean,
    p50_ms: gpxStats.p50,
    p95_ms: gpxStats.p95,
    min_ms: gpxStats.min,
    max_ms: gpxStats.max
  };
  console.log(JSON.stringify([result], null, 2));
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
