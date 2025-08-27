#!/usr/bin/env python3
# pip install fitdecode fitparse gpxpy
import io, time, statistics, argparse
import gpxpy
import fitdecode
from fitparse import FitFile

def bench(func, data: bytes, iters: int):
    times = []
    for _ in range(iters):
        t0 = time.perf_counter()
        func(data)
        times.append((time.perf_counter() - t0) * 1000.0)
    times.sort()
    return {
        "mean_ms": statistics.mean(times),
        "p50_ms": statistics.median(times),
        "p95_ms": times[int(len(times)*0.95)-1],
        "min_ms": times[0],
        "max_ms": times[-1],
        "n": iters,
    }

def parse_gpx_points(data: bytes):
    # Parse and iterate all track points to equalize "work done"
    gpx = gpxpy.parse(io.BytesIO(data))
    cnt = 0
    for trk in gpx.tracks:
        for seg in trk.segments:
            for pt in seg.points:
                # touch fields
                _ = (pt.latitude, pt.longitude, pt.elevation, pt.time)
                cnt += 1
    return cnt

def parse_fit_fitdecode(data: bytes, check_crc=False, keep_unknown=False):
    # Iterate all messages; only touch "Record" fields to mimic GPX point iteration
    cnt = 0
    with fitdecode.FitReader(
        io.BytesIO(data),
        check_crc=check_crc,
    ) as fr:
        for frame in fr:
            if frame.frame_type == fitdecode.FIT_FRAME_DATA and getattr(frame, 'name', None) == "record":
                d = {f.name: f.value for f in frame.fields}
                # touch common fields
                _ = (d.get("position_lat"), d.get("position_long"),
                     d.get("altitude"), d.get("timestamp"))
                cnt += 1
    return cnt

def parse_fit_fitparse(data: bytes):
    cnt = 0
    ff = FitFile(io.BytesIO(data))
    # preload() pulls everything; alternatively iterate_messages('record') to match GPX points
    for m in ff.get_messages("record"):
        d = {f.name: f.value for f in m}
        _ = (d.get("position_lat"), d.get("position_long"),
             d.get("altitude"), d.get("timestamp"))
        cnt += 1
    return cnt

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fit", required=True)
    ap.add_argument("--gpx", required=True)
    ap.add_argument("-n", type=int, default=25)
    ap.add_argument("--crc", action="store_true", help="enable CRC check for fitdecode")
    args = ap.parse_args()

    fit_bytes = open(args.fit, "rb").read()
    gpx_bytes = open(args.gpx, "rb").read()

    print(f"Sizes: FIT={len(fit_bytes):,} B  GPX={len(gpx_bytes):,} B")

    # Sanity: show counts once (not timed)
    fit_cnt_fd = parse_fit_fitdecode(fit_bytes, check_crc=args.crc)
    fit_cnt_fp = parse_fit_fitparse(fit_bytes)
    gpx_cnt = parse_gpx_points(gpx_bytes)
    print(f"Record/point counts: fitdecode={fit_cnt_fd}  fitparse={fit_cnt_fp}  gpx_points={gpx_cnt}")

    r_fd = bench(lambda b: parse_fit_fitdecode(b, check_crc=args.crc), fit_bytes, args.n)
    r_fp = bench(parse_fit_fitparse, fit_bytes, args.n)
    r_gx = bench(parse_gpx_points, gpx_bytes, args.n)

    def show(label, r):
        print(f"{label}: mean={r['mean_ms']:.2f}ms p50={r['p50_ms']:.2f}ms p95={r['p95_ms']:.2f}ms "
              f"min={r['min_ms']:.2f}ms max={r['max_ms']:.2f}ms n={r['n']}")

    show("FIT (fitdecode)", r_fd)
    show("FIT (fitparse)", r_fp)
    show("GPX (gpxpy points)", r_gx)

if __name__ == "__main__":
    main()