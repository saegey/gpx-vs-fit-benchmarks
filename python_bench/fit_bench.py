# python_bench/fit_bench.py
import argparse
import json
from pathlib import Path
from bench_common import parse_fit, _summarize, bench

def main():
    p = argparse.ArgumentParser(description="FIT benchmark")
    p.add_argument("--fit", type=str, required=False, help="path to FIT file")
    p.add_argument("-n", "--iterations", type=int, default=25, help="iterations")
    args = p.parse_args()

    fit_file = Path(args.fit) if args.fit else Path(__file__).parent / "testdata" / "BWR_San_Diego_Waffle_Ride_.fit"
    fit_bytes = fit_file.read_bytes()
    fit_times = bench(parse_fit, fit_bytes, args.iterations)
    result = _summarize("FIT", "fitdecode", args.iterations, fit_times)
    print(json.dumps([result], indent=2))

if __name__ == "__main__":
    main()
