import argparse
import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Optional

# When executed as a script (__package__ is empty), add this folder to sys.path
if __package__ in (None, ""):
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "vendor"))

try:
    # Module mode: python -m python_bench.fit_bench
    from .bench_common import parse_gpx, _summarize, bench  # type: ignore
except ImportError:
    # Script mode: python python_bench/fit_bench.py
    from bench_common import parse_gpx, _summarize, bench

DEFAULT_TESTDATA = Path(__file__).parent / "testdata" / "BWR_San_Diego_Waffle_Ride_.gpx"


def run_benchmark(gpx_path: Optional[Path] = None, iterations: int = 5) -> List[Dict]:
    """
    Pure function used by Lambda: returns a list of result dicts.
    """
    src = Path(gpx_path) if gpx_path else DEFAULT_TESTDATA
    gpx_bytes = src.read_bytes()
    gpx_times = bench(parse_gpx, gpx_bytes, iterations)
    result = _summarize("GPX", "gpxpy", iterations, gpx_times)
    return [result]


def main(argv: Optional[list] = None) -> List[Dict]:
    """
    CLI entrypoint: prints JSON for humans AND returns the results.
    """
    p = argparse.ArgumentParser(description="GPX benchmark")
    p.add_argument("--gpx", type=str, help="path to GPX file")
    p.add_argument("-n", "--iterations", type=int, default=5, help="iterations")
    args = p.parse_args(argv)

    results = run_benchmark(Path(args.gpx) if args.gpx else None, args.iterations)
    # print pretty JSON for CLI usage
    print(json.dumps(results, indent=2))
    return results


if __name__ == "__main__":
    main()