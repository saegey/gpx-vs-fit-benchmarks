# GPX vs FIT Benchmarks

This project benchmarks the performance of different libraries and parsers for reading FIT and GPX files across multiple programming languages (Go, Python, Node.js).

This benchmark was created to go along with a blog post [From GPX to FIT: Lessons in Scaling Fitness Data](https://saegey.com/project/gpx-falls-short/)

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
