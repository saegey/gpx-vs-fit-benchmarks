// gobench/run.go
package gobench

import (
	"bytes"
	_ "embed"
	"sort"
	"time"

	"github.com/tkrajina/gpxgo/gpx"
	"github.com/tormoder/fit"
)

//go:embed testdata/BWR_San_Diego_Waffle_Ride_.fit
var fitBytes []byte

//go:embed testdata/BWR_San_Diego_Waffle_Ride_.gpx
var gpxBytes []byte

// Files are embedded at build time via go:embed; no runtime loading required.

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

// RunAll executes both parsers for 'iter' iterations and returns summary stats.
func RunAll(iter int) ([]Result, error) {
	fitDur := make([]time.Duration, iter)
	for i := 0; i < iter; i++ {
		start := time.Now()
		if _, err := fit.Decode(bytes.NewReader(fitBytes)); err != nil {
			return nil, err
		}
		fitDur[i] = time.Since(start)
	}

	gpxDur := make([]time.Duration, iter)
	for i := 0; i < iter; i++ {
		start := time.Now()
		if _, err := gpx.Parse(bytes.NewReader(gpxBytes)); err != nil {
			return nil, err
		}
		gpxDur[i] = time.Since(start)
	}

	return []Result{
		summarize("FIT", "tormoder/fit", iter, fitDur),
		summarize("GPX", "tkrajina/gpxgo", iter, gpxDur),
	}, nil
}

func summarize(format, parser string, iter int, durs []time.Duration) Result {
	sort.Slice(durs, func(i, j int) bool { return durs[i] < durs[j] })
	var total time.Duration
	for _, d := range durs {
		total += d
	}
	// use ns precision -> ms
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
