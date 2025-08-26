package main

import (
	"context"
	"encoding/json"
	"fmt"

	"github.com/aws/aws-lambda-go/lambda"
	"github.com/saegey/gpx-vs-fit-benchmarks/gobench"
)

func handler(ctx context.Context) (any, error) {
	results, err := gobench.RunAll()
	if err != nil {
		return nil, err
	}
	// Print a JSON line per result (for Logs Insights)
	for _, r := range results {
		b, _ := json.Marshal(map[string]any{
			"lang":       "Go",
			"format":     r.Format,
			"parser":     r.Parser,
			"iterations": r.Iterations,
			"mean_ms":    r.MeanMS,
			"p50_ms":     r.P50MS,
			"p95_ms":     r.P95MS,
			"min_ms":     r.MinMS,
			"max_ms":     r.MaxMS,
		})
		fmt.Println(string(b))
	}
	return map[string]any{"ok": true, "count": len(results)}, nil
}

func main() { lambda.Start(handler) }
