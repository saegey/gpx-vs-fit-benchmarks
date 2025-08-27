package main

import (
	"context"
	"encoding/json"
	"fmt"
	"time"

	"github.com/aws/aws-lambda-go/lambda"
	"github.com/saegey/gpx-vs-fit-benchmarks/gobench"
)

func handler(ctx context.Context) (any, error) {
	start := time.Now()
	fmt.Printf("[go] start ts=%d\n", time.Now().UnixMilli())

	t0 := time.Now()
	results, err := gobench.RunAll(25)
	if err != nil {
		fmt.Println("[go] RunAll error:", err)
		return nil, err
	}
	fmt.Printf("[go] RunAll done in %.2fms\n", float64(time.Since(t0).Microseconds())/1000.0)
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
	fmt.Printf("[go] total handler time %.2fms\n", float64(time.Since(start).Microseconds())/1000.0)
	return map[string]any{"ok": true, "count": len(results)}, nil
}

func main() { lambda.Start(handler) }
