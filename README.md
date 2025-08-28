# GPX vs FIT Benchmarks

This project benchmarks the performance of different libraries and parsers for reading FIT and GPX files across multiple programming languages (Go, Python, Node.js).

This benchmark was created to go along with a blog post [From GPX to FIT: Lessons in Scaling Fitness Data](https://saegey.com/project/from-gpx-to-fit/)

## Purpose
The goal is to compare the speed and efficiency of popular FIT and GPX parsing libraries, using real-world activity files, to help developers choose the best tool for their needs.

## How to Use
1. Install the required language versions (see `.python-version` and `.node-version`).
2. Install dependencies for each language (see respective folders).
3. Run the benchmark scripts in each language folder or via the shell script

## Deploying/Running on AWS Lambda

This repo includes Serverless functions for Node, Python, Ruby, and Go. Below are the steps to vendor dependencies and build artifacts so they run on Lambda.


### Node.js (node-bench)

To install and vendor the required libraries for deployment to AWS Lambda:

```bash
cd node-bench
npm install
# This will create a node_modules directory with all dependencies.
# If you want to vendor only production dependencies (recommended for Lambda):
npm install --only=production
```

- Ensure `node_modules` is included in your deployment package (Serverless does this by default).
- Your handler and benchmark scripts will require the libraries from `node_modules`.

---

### Python (python_bench)

- Create a clean virtualenv and vendor dependencies locally for packaging:

```bash
cd python_bench
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt -t vendor
# optional: verify handler loads
python -c 'import sys; import python_bench.gpx_fit_bench as b; print("ok")'
```

Notes:
- The handler adds `python_bench/vendor` to `sys.path` before imports.
- Keep vendor lightweight; avoid platform-specific wheels unless you built them for manylinux.

### Ruby (ruby_bench)

`rubyfit` is a native C extension; build it for Amazon Linux 2023 using Docker and vendor it with the function.

1) Ensure `ruby_bench/Gemfile` exists (example):

```ruby
source "https://rubygems.org"
gem "rubyfit", git: "https://github.com/ridewithgps/rubyfit"
```

2) Build vendor/bundle in an AL2023 container (x86_64 by default; use `--platform linux/arm64` for arm):

```bash
cd ruby_bench
docker run --rm --platform linux/amd64 -v "$PWD":/work -w /work amazonlinux:2023 \
	bash -lc 'dnf -y install ruby rubygems ruby-devel gcc make git && \
						gem install bundler -v "~> 2" && \
						bundle config set path vendor/bundle && \
						bundle install --deployment --without development test'
```

Notes:
- Both `ruby_bench/handler.rb` and `ruby_bench/bench.rb` call `require 'bundler/setup'` so `vendor/bundle` is on the load path.


### Go (cmd/fit and cmd/gpx)

The Go Lambda handlers are split for FIT and GPX:

```
cmd/
	fit/
		main.go      # FIT Lambda handler
	gpx/
		main.go      # GPX Lambda handler
```

Build each binary for AWS Lambda:

```sh
GOOS=linux GOARCH=amd64 CGO_ENABLED=0 go build -o dist/go-fit/bootstrap ./cmd/fit
GOOS=linux GOARCH=amd64 CGO_ENABLED=0 go build -o dist/go-gpx/bootstrap ./cmd/gpx
```

Zip each for deployment:

```sh
cd dist/go-fit && zip -9 go-fit.zip bootstrap
cd dist/go-gpx && zip -9 go-gpx.zip bootstrap
```

Deploy using Serverless or your preferred method. See `serverless.yml` for function/zip mapping.

### Serverless deploy/invoke

```bash
# Package and deploy
npx serverless deploy --stage dev

# Invoke each function and stream logs
npx serverless invoke -f nodeFit --stage dev -l
npx serverless invoke -f nodeGpx --stage dev -l
npx serverless invoke -f pyFit --stage dev -l
npx serverless invoke -f pyGpx --stage dev -l
npx serverless invoke -f goFit --stage dev -l
npx serverless invoke -f goGpx --stage dev -l
npx serverless invoke -f rubyFit --stage dev -l
# npx serverless invoke -f rubyGpx --stage dev -l  # Uncomment if/when implemented
```

### Run all Lambda functions and display output

You can use this shell script to invoke all Lambda functions and print their output:

```bash
#!/usr/bin/env bash
set -e
STAGE=${1:-dev}
FUNCS=(nodeFit nodeGpx pyFit pyGpx goFit goGpx rubyFit)
for fn in "${FUNCS[@]}"; do
	echo -e "\n--- $fn ---"
	npx serverless invoke -f "$fn" --stage "$STAGE" -l || echo "$fn failed"
done
# Uncomment below if/when rubyGpx is implemented
# npx serverless invoke -f rubyGpx --stage "$STAGE" -l
```

## Version Management
- Python version: see `.python-version`
- Node.js version: see `.node-version`

## Notes
- This project is intended for comparative benchmarking only.
- Contributions and new parser benchmarks are welcome!


## M4 Pro Benchmark results
```bash
➜ ./run_all_benchmarks.sh
\n--- Python Benchmark (FIT) ---
[
  {
    "format": "FIT",
    "parser": "fitdecode",
    "iterations": 25,
    "mean_ms": 1708.618130106479,
    "p50_ms": 1707.5792918913066,
    "p95_ms": 1726.4431254006922,
    "min_ms": 1680.467292200774,
    "max_ms": 1731.3364166766405
  }
]
\n--- Python Benchmark (GPX) ---
[
  {
    "format": "GPX",
    "parser": "gpxpy",
    "iterations": 25,
    "mean_ms": 965.5417267978191,
    "p50_ms": 973.305375315249,
    "p95_ms": 1053.5742081701756,
    "min_ms": 870.0456251390278,
    "max_ms": 1119.412041734904
  }
]
\n--- Go Benchmark (FIT) ---
[
  {
    "format": "FIT",
    "parser": "tormoder/fit",
    "iterations": 25,
    "mean_ms": 21.130188360000002,
    "p50_ms": 20.72875,
    "p95_ms": 21.7165,
    "min_ms": 19.977917,
    "max_ms": 25.439583
  }
]
\n--- Go Benchmark (GPX) ---
[
  {
    "format": "GPX",
    "parser": "tkrajina/gpxgo",
    "iterations": 25,
    "mean_ms": 285.55204163999997,
    "p50_ms": 275.373916,
    "p95_ms": 308.075416,
    "min_ms": 268.349917,
    "max_ms": 353.530333
  }
]
\n--- Node.js Benchmark ---
[
  {
    "format": "FIT",
    "parser": "fit-file-parser",
    "iterations": 25,
    "mean_ms": 159.77257500000005,
    "p50_ms": 153.3343749999999,
    "p95_ms": 178.71695799999998,
    "min_ms": 144.89116699999977,
    "max_ms": 210.96279199999992
  }
]
[
  {
    "format": "GPX",
    "parser": "fast-xml-parser",
    "iterations": 25,
    "mean_ms": 370.25350840000004,
    "p50_ms": 368.85483299999987,
    "p95_ms": 397.3850000000002,
    "min_ms": 348.5311670000001,
    "max_ms": 423.097625
  }
]
\n--- Ruby Benchmark (rubyfit) ---
[
  {
    "format": "FIT",
    "parser": "rubyfit",
    "iterations": 25,
    "bytes": 1558095,
    "mean_ms": 46.92019999027252,
    "p50_ms": 46.02400027215481,
    "p95_ms": 46.875,
    "min_ms": 44.93400081992149,
    "max_ms": 58.787000365555286
  }
]
```

## Lambda 1024 mb memory Benchmark
```bash
❯ ./run_all_lambda_funcs.sh dev5 
-e 
--- nodeFit ---
{
    "ok": true
}
--------------------------------------------------------------------
START
2025-08-27 14:06:40.479 INFO    [js] start ts=1756328800479
2025-08-27 14:07:17.997 INFO    [js] fit-bench.js out:
[
  {
    "format": "FIT",
    "parser": "fit-file-parser",
    "iterations": 25,
    "mean_ms": 1492.6367101599994,
    "p50_ms": 1486.650665000001,
    "p95_ms": 1555.7191669999993,
    "min_ms": 1400.0084720000013,
    "max_ms": 1642.333054
  }
]

2025-08-27 14:07:17.997 INFO    [js] total handler time 37517.82ms
END Duration: 37522.08 ms (init: 146.52 ms) Memory Used: 143 MB

-e 
--- nodeGpx ---
{
    "ok": true
}
--------------------------------------------------------------------
START
2025-08-27 14:07:20.449 INFO    [js] start ts=1756328840449
2025-08-27 14:08:30.538 INFO    [js] gpx-bench.js out:
[
  {
    "format": "GPX",
    "parser": "fast-xml-parser",
    "iterations": 25,
    "mean_ms": 2792.8647244,
    "p50_ms": 2744.605236000003,
    "p95_ms": 2800.402799000003,
    "min_ms": 2714.5204230000018,
    "max_ms": 3620.4947970000003
  }
]

2025-08-27 14:08:30.538 INFO    [js] total handler time 70089.26ms
END Duration: 70093.43 ms (init: 152.08 ms) Memory Used: 293 MB

-e 
--- pyFit ---
{
    "ok": true,
    "count": 1
}
--------------------------------------------------------------------
START
[py] start ts=1756328913496 cold=True
[py] run_bench (fit) done in 110274.82ms
{"_aws": {"Timestamp": 1756328913503, "CloudWatchMetrics": [{"Namespace": "GPXvsFIT/Benchmarks", "Dimensions": [["Language", "Format", "Parser", "MemoryMB", "Cold"]], "Metrics": [{"Name": "mean_ms", "Unit": "Milliseconds"}, {"Name": "p50_ms", "Unit": "Milliseconds"}, {"Name": "p95_ms", "Unit": "Milliseconds"}]}]}, "Language": "Python", "Format": "FIT", "Parser": "fitdecode", "MemoryMB": 1024, "Cold": true, "mean_ms": 11025.127620700005, "p50_ms": 11003.737436000023, "p95_ms": 11107.643130000042}
{"ts": 1756328913503, "lang": "Python", "memory_mb": 1024, "cold": true, "commit": "dev", "format": "FIT", "parser": "fitdecode", "iterations": 10, "mean_ms": 11025.127620700005, "p50_ms": 11003.737436000023, "p95_ms": 11107.643130000042, "min_ms": 10925.412312000048, "max_ms": 11244.333019000009}
[py] total handler time 110281.24ms
END Duration: 110283.04 ms (init: 352.54 ms) Memory Used: 71 MB

-e 
--- pyGpx ---
{
    "ok": true,
    "count": 1
}
--------------------------------------------------------------------
START
[py] start ts=1756329026731 cold=True
[py] run_bench (gpx) done in 47837.55ms
{"_aws": {"Timestamp": 1756329026731, "CloudWatchMetrics": [{"Namespace": "GPXvsFIT/Benchmarks", "Dimensions": [["Language", "Format", "Parser", "MemoryMB", "Cold"]], "Metrics": [{"Name": "mean_ms", "Unit": "Milliseconds"}, {"Name": "p50_ms", "Unit": "Milliseconds"}, {"Name": "p95_ms", "Unit": "Milliseconds"}]}]}, "Language": "Python", "Format": "GPX", "Parser": "gpxpy", "MemoryMB": 1024, "Cold": true, "mean_ms": 4778.058608900001, "p50_ms": 4763.092366000001, "p95_ms": 4835.350298999998}
{"ts": 1756329026731, "lang": "Python", "memory_mb": 1024, "cold": true, "commit": "dev", "format": "GPX", "parser": "gpxpy", "iterations": 10, "mean_ms": 4778.058608900001, "p50_ms": 4763.092366000001, "p95_ms": 4835.350298999998, "min_ms": 4620.306272000001, "max_ms": 5197.912104}
[py] total handler time 47837.79ms
END Duration: 47839.75 ms (init: 303.28 ms) Memory Used: 341 MB

-e 
--- goFit ---
{
    "count": 1,
    "ok": true
}
--------------------------------------------------------------------
START
[go] start ts=1756329076344
[go] RunFit done in 3234.03ms
{"format":"FIT","iterations":25,"lang":"Go","max_ms":172.542613,"mean_ms":129.36038932,"min_ms":119.514382,"p50_ms":123.205216,"p95_ms":138.705589,"parser":"tormoder/fit"}
[go] total handler time 3234.14ms
END Duration: 3236.98 ms (init: 80.02 ms) Memory Used: 42 MB

-e 
--- goGpx ---
{
    "count": 1,
    "ok": true
}
--------------------------------------------------------------------
START
[go] start ts=1756329081155
[go] RunGpx done in 47459.68ms
{"format":"GPX","iterations":25,"lang":"Go","max_ms":2061.580418,"mean_ms":1898.3855437599998,"min_ms":1842.203819,"p50_ms":1895.050641,"p95_ms":1940.144303,"parser":"tkrajina/gpxgo"}
[go] total handler time 47459.83ms
END Duration: 47462.21 ms (init: 77.43 ms) Memory Used: 128 MB

-e 
--- rubyFit ---
{
    "ok": true,
    "count": 1
}
--------------------------------------------------------------------
START
[rb] start ts=1756329131857 cold=true
[rb] bench done in 7140.26ms
{"ts":1756329138997,"lang":"Ruby","format":"FIT","parser":"rubyfit","iterations":25,"mean_ms":273.51524956000105,"p50_ms":274.5697060000012,"p95_ms":278.2072790000001,"min_ms":264.88435600000315,"max_ms":297.7202630000022,"memory_mb":1024,"cold":true,"commit":"dev"}
[rb] total handler time 7140.68ms
END Duration: 7145.22 ms (init: 641.93 ms) Memory Used: 49 MB
```
