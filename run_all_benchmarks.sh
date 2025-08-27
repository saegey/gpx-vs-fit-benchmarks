#!/usr/bin/env bash
# Run all FIT/GPX benchmarks for Go, Python, and Node.js
set -e


# Default values
FIT_FILE="testdata/BWR_San_Diego_Waffle_Ride_.fit"
GPX_FILE="testdata/BWR_San_Diego_Waffle_Ride_.gpx"
ITERS=25
BENCH_LIST="python,go,nodejs,ruby"

# Parse flags
while [[ $# -gt 0 ]]; do
    case $1 in
        --fit)
            FIT_FILE="$2"
            shift 2
        ;;
        --gpx)
            GPX_FILE="$2"
            shift 2
        ;;
        --iters)
            ITERS="$2"
            shift 2
        ;;
        --bench)
            BENCH_LIST="$2"
            shift 2
        ;;
        *)
            echo "Unknown option: $1" >&2
            exit 1
        ;;
    esac
done

# Convert comma-separated list to array
IFS=',' read -ra BENCH_ARR <<< "$BENCH_LIST"

should_run() {
  local name="$1"
  for b in "${BENCH_ARR[@]}"; do
    if [[ "$b" == "$name" ]]; then
      return 0
    fi
  done
  return 1
}

# Python benchmark
if should_run python; then
  if [ -f python_bench/fit_bench.py ] && [ -f python_bench/gpx_bench.py ]; then
    echo "\n--- Python Benchmark (FIT) ---"
    (cd python_bench && python3 fit_bench.py --fit $FIT_FILE -n $ITERS)
    echo "\n--- Python Benchmark (GPX) ---"
    (cd python_bench && python3 gpx_bench.py --gpx $GPX_FILE -n $ITERS)
  else
    echo "Python benchmark script(s) not found."
  fi
fi

# Go benchmark
if should_run go; then
  if [ -f cmd/fit/main.go ] && [ -f cmd/gpx/main.go ]; then
    echo "\n--- Go Benchmark (FIT) ---"
    (go run gobench/cmd/fit/main.go -n $ITERS -json)
    echo "\n--- Go Benchmark (GPX) ---"
    (go run gobench/cmd/gpx/main.go -n $ITERS -json)
  else
    echo "Go benchmark script(s) not found."
  fi
fi

# Node.js benchmark
if should_run nodejs; then
  if [ -f node-bench/fit-bench.js ]; then
    echo "\n--- Node.js Benchmark ---"
    (cd node-bench && node fit-bench.js $FIT_FILE $ITERS && node gpx-bench.js $GPX_FILE $ITERS)
  else
    echo "Node.js benchmark script not found."
  fi
fi

# Ruby benchmark
if should_run ruby; then
  if [ -f ruby_bench/bench.rb ]; then
    echo "\n--- Ruby Benchmark (rubyfit) ---"
    (cd ruby_bench && bundle install >/dev/null && ruby bench.rb -f $FIT_FILE -n $ITERS)
  else
    echo "Ruby benchmark script not found."
  fi
fi
