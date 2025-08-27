package gobench

import (
	"sort"
	"time"
)

type Result struct {
	Format     string  `json:"format"`
	Parser     string  `json:"parser"`
	Iterations int     `json:"iterations"`
	MeanMS     float64 `json:"mean_ms"`
	P50MS      float64 `json:"p50_ms"`
	P95MS      float64 `json:"p95_ms"`
	MinMS      float64 `json:"min_ms"`
	MaxMS      float64 `json:"max_ms"`
}

func summarize(format, parser string, iter int, durs []time.Duration) Result {
	sort.Slice(durs, func(i, j int) bool { return durs[i] < durs[j] })
	var total time.Duration
	for _, d := range durs {
		total += d
	}
	toMS := func(d time.Duration) float64 { return float64(d.Nanoseconds()) / 1e6 }
	mean := toMS(total) / float64(iter)
	p := func(q float64) float64 {
		idx := int(float64(len(durs)-1) * q)
		return toMS(durs[idx])
	}
	return Result{
		Format:     format,
		Parser:     parser,
		Iterations: iter,
		MeanMS:     mean,
		P50MS:      p(0.50),
		P95MS:      p(0.95),
		MinMS:      toMS(durs[0]),
		MaxMS:      toMS(durs[len(durs)-1]),
	}
}
