import time
import io
import statistics
import fitdecode
import gpxpy


def parse_fit(data):
    with fitdecode.FitReader(io.BytesIO(data)) as fr:
        for _ in fr:
            pass


def parse_gpx(data):
    gpx = gpxpy.parse(io.BytesIO(data))
    for t in gpx.tracks:
        for s in t.segments:
            for _ in s.points:
                pass


def bench(label, func, data, n=25):
    times = []
    for _ in range(n):
        t0 = time.perf_counter()
        func(data)
        times.append((time.perf_counter() - t0) * 1000)
    print(f"{label}: mean={statistics.mean(times):.2f}ms p50={statistics.median(times):.2f}ms")


fit_bytes = open("../testdata/BWR_San_Diego_Waffle_Ride_.fit", "rb").read()
gpx_bytes = open("../testdata/BWR_San_Diego_Waffle_Ride_.gpx", "rb").read()

bench("FIT", parse_fit, fit_bytes)
bench("GPX", parse_gpx, gpx_bytes)
