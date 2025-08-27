package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"os"

	gobench "github.com/saegey/gpx-vs-fit-benchmarks/gobench"
)

func main() {
	iter := flag.Int("n", 25, "iterations per format")
	jsonOut := flag.Bool("json", false, "print JSON summary")
	flag.Parse()

	results, err := gobench.RunAll(*iter)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error: %v\n", err)
		os.Exit(1)
	}

	if *jsonOut {
		enc := json.NewEncoder(os.Stdout)
		enc.SetIndent("", "  ")
		if err := enc.Encode(results); err != nil {
			fmt.Fprintf(os.Stderr, "JSON encode error: %v\n", err)
			os.Exit(1)
		}
		return
	}

	for _, r := range results {
		fmt.Printf("%s/%s: mean=%.2fms p50=%.2fms p95=%.2fms min=%.2fms max=%.2fms\n",
			r.Format, r.Parser, r.MeanMS, r.P50MS, r.P95MS, r.MinMS, r.MaxMS)
	}
}
