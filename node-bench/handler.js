const { execFileSync } = require("node:child_process");

let WARM = false;

exports.run = async (event = {}) => {
  const commit = process.env.COMMIT_SHA || "dev";
  const memory = parseInt(process.env.AWS_LAMBDA_FUNCTION_MEMORY_SIZE || "0", 10);

  // Run your Node benchmark binary/script that prints JSON lines per parser
  // e.g., node node-bench/run.js --json
  const out = execFileSync("node", ["node-bench/run.js", "--json"], { encoding: "utf8" });

  const lines = out.trim().split(/\r?\n/).filter(Boolean);
  const now = Date.now();

  const results = lines.map((l) => {
    const r = JSON.parse(l); // must include format/parser/iterations/mean_ms/p50_ms/p95_ms...
    const base = {
      ts: now,
      lang: "Node",
      memory_mb: memory,
      cold: !WARM,
      commit,
      ...r,
    };

    // Emit EMF
    const emf = {
      _aws: {
        Timestamp: now,
        CloudWatchMetrics: [{
          Namespace: "GPXvsFIT/Benchmarks",
          Dimensions: [["Language","Format","Parser","MemoryMB","Cold"]],
          Metrics: [
            { Name: "mean_ms", Unit: "Milliseconds" },
            { Name: "p50_ms",  Unit: "Milliseconds" },
            { Name: "p95_ms",  Unit: "Milliseconds" }
          ]
        }]
      },
      Language: "Node",
      Format: base.format,
      Parser: base.parser,
      MemoryMB: memory,
      Cold: !WARM,
      mean_ms: base.mean_ms,
      p50_ms: base.p50_ms,
      p95_ms: base.p95_ms
    };
    console.log(JSON.stringify(emf));
    console.log(JSON.stringify(base));
    return base;
  });

  WARM = true;
  return { ok: true, count: results.length };
};