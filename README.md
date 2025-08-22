# GPX vs FIT Benchmarks

This project benchmarks the performance of different libraries and parsers for reading FIT and GPX files across multiple programming languages (Go, Python, Node.js).

## Purpose
The goal is to compare the speed and efficiency of popular FIT and GPX parsing libraries, using real-world activity files, to help developers choose the best tool for their needs.

## Structure
- **python-bench/**: Python scripts and requirements for benchmarking `fitdecode`, `fitparse`, and `gpxpy`.
- **gpx-fit-test/**: Go code for benchmarking FIT and GPX parsers.
- **node-bench/**: Node.js scripts for benchmarking FIT and GPX parsers.
- **testdata/**: Sample FIT and GPX files used for benchmarking.

## How to Use
1. Install the required language versions (see `.python-version` and `.node-version`).
2. Install dependencies for each language (see respective folders).
3. Run the benchmark scripts in each language folder.

## Version Management
- Python version: see `.python-version`
- Node.js version: see `.node-version`

## Notes
- This project is intended for comparative benchmarking only.
- Contributions and new parser benchmarks are welcome!

## Results
```bash
➜ ./run_all_benchmarks.sh 
\n--- Python Benchmark ---
Sizes: FIT=1,558,095 B  GPX=11,353,470 B
Record/point counts: fitdecode=32412  fitparse=32412  gpx_points=32412
FIT (fitdecode): mean=1319.68ms p50=1316.86ms p95=1344.45ms min=1285.01ms max=1355.36ms n=25
FIT (fitparse): mean=3326.84ms p50=3318.44ms p95=3378.80ms min=3267.17ms max=3396.52ms n=25
GPX (gpxpy points): mean=1003.07ms p50=983.47ms p95=1100.89ms min=920.59ms max=1132.85ms n=25
\n--- Go Benchmark ---
FIT  : size=1558095B  n=25  mean=17.91ms  p50=17.79ms  p95=18.25ms  min=17.26ms  max=22.02ms
GPX  : size=11353470B  n=25  mean=267.07ms  p50=267.33ms  p95=270.69ms  min=259.12ms  max=271.80ms

Speedup (GPX/FIT mean): 14.91x
File size ratio (GPX/FIT): 7.29x
\n--- Node.js Benchmark ---
Sizes: FIT=1,558,095 B  GPX=11,353,470 B
Record/point counts: fit_records=32412  gpx_points=32412
FIT (fit-file-parser): n=25 mean=156.53ms p50=155.61ms p95=167.18ms min=145.28ms max=170.70ms
GPX (fast-xml-parser): n=25 mean=351.21ms p50=350.75ms p95=356.24ms min=343.65ms max=360.36ms

Speedup (GPX/FIT mean): 2.24x
File size ratio (GPX/FIT): 7.29x
```