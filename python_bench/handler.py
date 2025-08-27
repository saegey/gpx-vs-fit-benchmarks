import json, os, sys, time
from pathlib import Path

# add vendored deps to path FIRST
HERE = Path(__file__).parent
VENDOR = HERE / "vendor"
if VENDOR.exists():
    sys.path.insert(0, str(VENDOR))

# now safe to import your bench module
import python_bench.gpx_fit_bench as bench  # relative import via package path

WARM = False

def lambda_handler(event, ctx):
    global WARM
    t_start = time.perf_counter()
    print(f"[py] start ts={int(time.time()*1000)} cold={not WARM}")
    commit = os.environ.get("COMMIT_SHA", "dev")
    memory = int(os.environ.get("AWS_LAMBDA_FUNCTION_MEMORY_SIZE", "0"))
    now = int(time.time() * 1000)

    # your bench module should return a list of result dicts
    # each dict should have: format, parser, iterations, mean_ms, p50_ms, p95_ms, min_ms, max_ms
    t0 = time.perf_counter()
    results = bench.run_bench(iterations=1)  # implement this in gpx_fit_bench.py
    print(f"[py] run_bench done in {(time.perf_counter()-t0)*1000:.2f}ms")

    # log EMF + JSON lines
    for r in results:
        emf = {
            "_aws": {"Timestamp": now, "CloudWatchMetrics": [{
                "Namespace": "GPXvsFIT/Benchmarks",
                "Dimensions": [["Language","Format","Parser","MemoryMB","Cold"]],
                "Metrics": [
                    {"Name":"mean_ms","Unit":"Milliseconds"},
                    {"Name":"p50_ms","Unit":"Milliseconds"},
                    {"Name":"p95_ms","Unit":"Milliseconds"},
                ],
            }]},
            "Language": "Python", "Format": r["format"], "Parser": r["parser"],
            "MemoryMB": memory, "Cold": (not WARM),
            "mean_ms": r["mean_ms"], "p50_ms": r["p50_ms"], "p95_ms": r["p95_ms"],
        }
        print(json.dumps(emf))
        print(json.dumps({"ts": now, "lang":"Python", "memory_mb": memory, "cold": (not WARM), "commit": commit, **r}))

    WARM = True
    print(f"[py] total handler time {(time.perf_counter()-t_start)*1000:.2f}ms")
    return {"ok": True, "count": len(results)}