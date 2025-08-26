import json, os, subprocess, time

WARM = False

def lambda_handler(event, ctx):
    commit = os.environ.get("COMMIT_SHA", "dev")
    memory = int(os.environ.get("AWS_LAMBDA_FUNCTION_MEMORY_SIZE", "0"))

    out = subprocess.check_output(
        ["python", "python-bench/run.py", "--json"], text=True
    ).strip()
    now = int(time.time() * 1000)

    results = []
    for line in filter(None, out.splitlines()):
        r = json.loads(line)
        base = {
            "ts": now,
            "lang": "Python",
            "memory_mb": memory,
            "cold": not WARM,
            "commit": commit,
            **r
        }
        emf = {
            "_aws": {
                "Timestamp": now,
                "CloudWatchMetrics": [{
                    "Namespace": "GPXvsFIT/Benchmarks",
                    "Dimensions": [["Language","Format","Parser","MemoryMB","Cold"]],
                    "Metrics": [
                        {"Name":"mean_ms","Unit":"Milliseconds"},
                        {"Name":"p50_ms","Unit":"Milliseconds"},
                        {"Name":"p95_ms","Unit":"Milliseconds"}
                    ]
                }]
            },
            "Language": "Python",
            "Format": base["format"],
            "Parser": base["parser"],
            "MemoryMB": memory,
            "Cold": (not WARM),
            "mean_ms": base["mean_ms"],
            "p50_ms": base["p50_ms"],
            "p95_ms": base["p95_ms"]
        }
        print(json.dumps(emf))
        print(json.dumps(base))
        results.append(base)

    global WARM
    WARM = True
    return {"ok": True, "count": len(results)}