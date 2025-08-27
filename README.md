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

## Deploying/Running on AWS Lambda

This repo includes Serverless functions for Node, Python, Ruby, and Go. Below are the steps to vendor dependencies and build artifacts so they run on Lambda.

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

3) Package test data where the handler expects it:

```bash
mkdir -p ruby_bench/testdata
cp ../testdata/BWR_San_Diego_Waffle_Ride_.fit ruby_bench/testdata/
```

Notes:
- Both `ruby_bench/handler.rb` and `ruby_bench/bench.rb` call `require 'bundler/setup'` so `vendor/bundle` is on the load path.
- Ensure Serverless `package.patterns` includes `ruby_bench/**` and does not exclude `vendor/**`.

### Go (cmd/lambda)

The Go Lambda uses embedded test data (via `go:embed`) in `gobench/run.go`.

Build the bootstrap binary for Lambda (x86_64; set `GOARCH=arm64` for Graviton):

```bash
GOOS=linux GOARCH=amd64 CGO_ENABLED=0 go build -o bootstrap ./cmd/lambda
zip -9 dist/go-bench.zip bootstrap
```

If you package additional assets manually, include them in the ZIP before deploying.

### Serverless deploy/invoke

```bash
# Package and deploy
npx serverless deploy --stage dev

# Invoke each function and stream logs
npx serverless invoke -f nodeBench --stage dev -l
npx serverless invoke -f pythonBench --stage dev -l
npx serverless invoke -f rubyBench --stage dev -l
npx serverless invoke -f goBench --stage dev -l
```

Troubleshooting:
- CloudFormation in rollback: wait until it reaches a stable state (e.g., `UPDATE_ROLLBACK_COMPLETE`), then redeploy.
- Ruby: `cannot load such file -- rubyfit` means `vendor/bundle` wasn’t packaged for the correct platform. Rebuild in Amazon Linux 2023 and ensure it’s included in the ZIP.
- Python: if imports fail on Lambda, ensure `python_bench/vendor` is present in the package and added to `sys.path` (the handler does this automatically).
- Go: if test data is needed at runtime without embedding, either embed via `go:embed` or package files within the ZIP and adjust paths.

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