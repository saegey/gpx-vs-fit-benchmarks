#!/usr/bin/env bash
# Run all FIT/GPX benchmarks for Go, Python, and Node.js
set -e

# Paths to test files
FIT_FILE="testdata/BWR_San_Diego_Waffle_Ride_.fit"
GPX_FILE="testdata/BWR_San_Diego_Waffle_Ride_.gpx"
ITERS=25

# Python benchmark
if [ -f python-bench/gpx_fit_bench_revised.py ]; then
  echo "\n--- Python Benchmark ---"
  (cd python-bench && python3 gpx_fit_bench_revised.py --fit ../$FIT_FILE --gpx ../$GPX_FILE -n $ITERS)
else
  echo "Python benchmark script not found."
fi

# Go benchmark
if [ -f gpx-fit-test/main.go ]; then
  echo "\n--- Go Benchmark ---"
  (cd gpx-fit-test && go run main.go --fit ../$FIT_FILE --gpx ../$GPX_FILE -n $ITERS)
else
  echo "Go benchmark script not found."
fi

# Node.js benchmark
if [ -f node-bench/bench.js ]; then
  echo "\n--- Node.js Benchmark ---"
  (cd node-bench && node bench.js ../$FIT_FILE ../$GPX_FILE $ITERS)
else
  echo "Node.js benchmark script not found."
fi
