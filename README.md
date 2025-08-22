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
