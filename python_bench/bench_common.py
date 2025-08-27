# python_bench/bench_common.py
import io
import statistics
import time
from pathlib import Path

import fitdecode  # type: ignore
import gpxpy      # type: ignore

def parse_fit(data: bytes) -> None:
    with fitdecode.FitReader(io.BytesIO(data)) as fr:
        for _ in fr:
            pass

def parse_gpx(data: bytes) -> None:
    gpx = gpxpy.parse(io.BytesIO(data))
    for t in gpx.tracks:
        for s in t.segments:
            for _ in s.points:
                pass

def _percentile(sorted_vals, q: float) -> float:
    if not sorted_vals:
        return 0.0
    idx = int((len(sorted_vals) - 1) * q)
    return sorted_vals[idx]

def _summarize(fmt: str, parser: str, n: int, times_ms: list[float]) -> dict:
    times_ms.sort()
    mean = statistics.fmean(times_ms) if times_ms else 0.0
    p50 = statistics.median(times_ms) if times_ms else 0.0
    p95 = _percentile(times_ms, 0.95)
    return {
        "format": fmt,
        "parser": parser,
        "iterations": n,
        "mean_ms": mean,
        "p50_ms": p50,
        "p95_ms": p95,
        "min_ms": times_ms[0] if times_ms else 0.0,
        "max_ms": times_ms[-1] if times_ms else 0.0,
    }

def bench(func, data: bytes, n: int) -> list[float]:
    out = []
    for _ in range(n):
        t0 = time.perf_counter()
        func(data)
        out.append((time.perf_counter() - t0) * 1000.0)
    return out
