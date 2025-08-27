# python_bench/gpx_bench.py
import argparse
import json
from pathlib import Path
from bench_common import parse_gpx, _summarize, bench

def main():
    p = argparse.ArgumentParser(description="GPX benchmark")
    p.add_argument("--gpx", type=str, required=False, help="path to GPX file")
    p.add_argument("-n", "--iterations", type=int, default=25, help="iterations")
    args = p.parse_args()

    gpx_file = Path(args.gpx) if args.gpx else Path(__file__).parent / "testdata" / "BWR_San_Diego_Waffle_Ride_.gpx"
    gpx_bytes = gpx_file.read_bytes()
    gpx_times = bench(parse_gpx, gpx_bytes, args.iterations)
    result = _summarize("GPX", "gpxpy", args.iterations, gpx_times)
    print(json.dumps([result], indent=2))

if __name__ == "__main__":
    main()
