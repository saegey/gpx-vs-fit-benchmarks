const { execFileSync } = require("node:child_process");
const path = require("node:path");

exports.run = async () => {
  const script = path.join(__dirname, "bench.js");
  const t0 = process.hrtime.bigint();
  try {
    console.log(`[js] start ts=${Date.now()}`);
    const out = execFileSync(process.execPath, [script], { encoding: "utf8" });
    console.log(`[js] bench.js out:\n${out}`);
    const dt = Number(process.hrtime.bigint() - t0) / 1e6;
    console.log(`[js] total handler time ${dt.toFixed(2)}ms`);
    return { ok: true };
  } catch (err) {
    const dt = Number(process.hrtime.bigint() - t0) / 1e6;
    console.log(`[js] error after ${dt.toFixed(2)}ms: ${err && err.message}`);
    if (err && err.stdout) console.log(`[js] stdout:\n${err.stdout}`);
    if (err && err.stderr) console.log(`[js] stderr:\n${err.stderr}`);
    throw err;
  }
};