# python_bench/gpx_fit_bench.py
import argparse
import io
import json
import os
import statistics
import sys
import time
from pathlib import Path

# Optional: use vendored deps if present (python_bench/vendor)
HERE = Path(__file__).parent
VENDOR = HERE / "vendor"
if VENDOR.exists():
    sys.path.insert(0, str(VENDOR))

import fitdecode  # type: ignore
import gpxpy      # type: ignore


# ---------- data loading ------------------------------------------------------

def _find_testdata_file(name: str) -> Path:
    """
    Resolve testdata path in common layouts.
    Prefer ./testdata next to this file; fall back to parent dirs if needed.
    """
    candidates = [
        HERE / "testdata" / name,
        HERE.parent / "testdata" / name,
        HERE.parent.parent / "testdata" / name,
    ]
    for p in candidates:
        if p.exists():
            return p
    raise FileNotFoundError(
        f"Could not find testdata file {name}. Ensure it's packaged under "
        f"{HERE}/testdata or add your own --fit/--gpx paths."
    )


def _read_bytes(path: Path) -> bytes:
    with path.open("rb") as f:
        return f.read()


# ---------- parsing funcs -----------------------------------------------------

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


# ---------- stats helpers -----------------------------------------------------

def _percentile(sorted_vals, q: float) -> float:
    """
    q in [0,1]; simple nearest-rank on zero-indexed array.
    Assumes sorted_vals is non-empty and sorted ascending.
    """
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


# ---------- public API --------------------------------------------------------

def run_bench(iterations: int = 25,
              fit_path: str | None = None,
              gpx_path: str | None = None) -> list[dict]:
    """
    Execute FIT and GPX parses for `iterations`, returning summary dicts.
    """
    fit_file = Path(fit_path) if fit_path else _find_testdata_file("BWR_San_Diego_Waffle_Ride_.fit")
    gpx_file = Path(gpx_path) if gpx_path else _find_testdata_file("BWR_San_Diego_Waffle_Ride_.gpx")

    fit_bytes = _read_bytes(fit_file)
    # gpx_bytes = _read_bytes(gpx_file)

    # time in ms
    def bench(func, data: bytes, n: int) -> list[float]:
        out = []
        for _ in range(n):
            t0 = time.perf_counter()
            func(data)
            out.append((time.perf_counter() - t0) * 1000.0)
        return out

    fit_times = bench(parse_fit, fit_bytes, iterations)
    # gpx_times = bench(parse_gpx, gpx_bytes, iterations)

    return [
        _summarize("FIT", "fitdecode", iterations, fit_times),
        # _summarize("GPX", "gpxpy", iterations, gpx_times),
    ]


# ---------- CLI entrypoint ----------------------------------------------------

def _main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description="GPX/FIT benchmarks")
    p.add_argument("--json", action="store_true", help="emit one JSON object per line")
    p.add_argument("-n", "--iterations", type=int, default=25, help="iterations per parser")
    p.add_argument("--fit", type=str, help="path to FIT file (optional)")
    p.add_argument("--gpx", type=str, help="path to GPX file (optional)")
    args = p.parse_args(argv)

    results = run_bench(iterations=args.iterations, fit_path=args.fit, gpx_path=args.gpx)

    if args.json:
        for r in results:
            print(json.dumps(r))
    else:
        # human-friendly
        for r in results:
            print(
                f"{r['format']} ({r['parser']}): "
                f"mean={r['mean_ms']:.2f}ms p50={r['p50_ms']:.2f}ms "
                f"p95={r['p95_ms']:.2f}ms min={r['min_ms']:.2f}ms max={r['max_ms']:.2f}ms "
                f"(n={r['iterations']})"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))