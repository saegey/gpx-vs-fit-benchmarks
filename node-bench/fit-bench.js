#!/usr/bin/env node
const { parseFitCountRecords, bench, fs, path } = require('./common-bench');

async function main() {
  const fitPath = process.argv[2] || path.join(__dirname, "testdata", "BWR_San_Diego_Waffle_Ride_.fit");
  const N = Number(process.argv[3] || 25);
  const fitBuf = fs.readFileSync(fitPath);

  const fitStats = await bench(N, async () => {
    await parseFitCountRecords(fitBuf, { force: true });
  });

  const result = {
    format: "FIT",
    parser: "fit-file-parser",
    iterations: N,
    mean_ms: fitStats.mean,
    p50_ms: fitStats.p50,
    p95_ms: fitStats.p95,
    min_ms: fitStats.min,
    max_ms: fitStats.max
  };
  console.log(JSON.stringify([result], null, 2));
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
