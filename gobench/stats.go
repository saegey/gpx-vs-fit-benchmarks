package gobench

import (
	"sort"
	"time"
)

func summarize(format, parser string, iter int, durations []time.Duration) Result {
	sort.Slice(durations, func(i, j int) bool { return durations[i] < durations[j] })

	total := time.Duration(0)
	for _, d := range durations {
		total += d
	}
	mean := float64(total.Milliseconds()) / float64(iter)

	get := func(p float64) float64 {
		idx := int(float64(len(durations)-1) * p)
		return float64(durations[idx].Milliseconds())
	}

	return Result{
		Format:     format,
		Parser:     parser,
		Iterations: iter,
		MeanMS:     mean,
		P50MS:      get(0.50),
		P95MS:      get(0.95),
		MinMS:      float64(durations[0].Milliseconds()),
		MaxMS:      float64(durations[len(durations)-1].Milliseconds()),
	}
}
