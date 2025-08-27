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
	result, err := gobench.RunFit(25)
	if err != nil {
		fmt.Println("[go] RunFit error:", err)
		return nil, err
	}
	fmt.Printf("[go] RunFit done in %.2fms\n", float64(time.Since(t0).Microseconds())/1000.0)
	b, _ := json.Marshal(map[string]any{
		"lang":       "Go",
		"format":     result.Format,
		"parser":     result.Parser,
		"iterations": result.Iterations,
		"mean_ms":    result.MeanMS,
		"p50_ms":     result.P50MS,
		"p95_ms":     result.P95MS,
		"min_ms":     result.MinMS,
		"max_ms":     result.MaxMS,
	})
	fmt.Println(string(b))
	fmt.Printf("[go] total handler time %.2fms\n", float64(time.Since(start).Microseconds())/1000.0)
	return map[string]any{"ok": true, "count": 1}, nil
}

func main() { lambda.Start(handler) }
