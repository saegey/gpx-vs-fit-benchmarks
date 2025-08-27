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
    from .bench_common import parse_fit, _summarize, bench  # type: ignore
except ImportError:
    # Script mode: python python_bench/fit_bench.py
    from bench_common import parse_fit, _summarize, bench

DEFAULT_TESTDATA = Path(__file__).parent / "testdata" / "BWR_San_Diego_Waffle_Ride_.fit"


def run_benchmark(fit_path: Optional[Path] = None, iterations: int = 5) -> List[Dict]:
    """
    Pure function for Lambda: returns list of result dicts.
    """
    src = Path(fit_path) if fit_path else DEFAULT_TESTDATA
    fit_bytes = src.read_bytes()
    fit_times = bench(parse_fit, fit_bytes, iterations)
    result = _summarize("FIT", "fitdecode", iterations, fit_times)
    return [result]


def main(argv: Optional[list] = None) -> List[Dict]:
    """
    CLI entrypoint: prints pretty JSON and also returns results.
    Safe to call from tests too (pass argv to avoid argparse reading sys.argv).
    """
    p = argparse.ArgumentParser(description="FIT benchmark")
    p.add_argument("--fit", type=str, help="path to FIT file")
    p.add_argument("-n", "--iterations", type=int, default=5, help="iterations")
    args = p.parse_args(argv)

    results = run_benchmark(Path(args.fit) if args.fit else None, args.iterations)
    print(json.dumps(results, indent=2))
    return results


if __name__ == "__main__":
    main()