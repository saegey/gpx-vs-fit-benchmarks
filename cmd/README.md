# Go Lambda Build Instructions

To build the Go Lambda binaries for FIT and GPX benchmarks:

1. Each handler is in its own directory:

```
cmd/
  fit/
    main.go      # FIT Lambda handler
  gpx/
    main.go      # GPX Lambda handler
```

2. Build each binary for AWS Lambda:

```sh
GOOS=linux GOARCH=amd64 CGO_ENABLED=0 go build -o dist/go-fit/bootstrap ./cmd/fit
GOOS=linux GOARCH=amd64 CGO_ENABLED=0 go build -o dist/go-gpx/bootstrap ./cmd/gpx
```

3. Zip each for deployment:

```sh
cd dist/go-fit && zip -9 go-fit.zip bootstrap
cd dist/go-gpx && zip -9 go-gpx.zip bootstrap
```

4. Deploy using Serverless or your preferred method. See `serverless.yml` for function/zip mapping.

---

- Only one `main.go` per handler directory.
- Each handler imports and calls the appropriate benchmark logic from the `gobench` package.
