package gobench

import (
	"bytes"
	"os"
	"time"

	"github.com/tkrajina/gpxgo/gpx"
	"github.com/tormoder/fit"
)

var fitBytes, gpxBytes []byte

func init() {
	var err error
	fitBytes, err = os.ReadFile("../testdata/BWR_San_Diego_Waffle_Ride_.fit")
	if err != nil {
		panic(err)
	}
	gpxBytes, err = os.ReadFile("../testdata/BWR_San_Diego_Waffle_Ride_.gpx")
	if err != nil {
		panic(err)
	}
}

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

func runFIT(iter int) Result {
	durations := make([]time.Duration, iter)
	for i := 0; i < iter; i++ {
		start := time.Now()
		_, err := fit.Decode(bytes.NewReader(fitBytes))
		if err != nil {
			panic(err)
		}
		durations[i] = time.Since(start)
	}
	return summarize("FIT", "tormoder/fit", iter, durations)
}

func runGPX(iter int) Result {
	durations := make([]time.Duration, iter)
	for i := 0; i < iter; i++ {
		start := time.Now()
		_, err := gpx.Parse(bytes.NewReader(gpxBytes))
		if err != nil {
			panic(err)
		}
		durations[i] = time.Since(start)
	}
	return summarize("GPX", "tkrajina/gpxgo", iter, durations)
}

// RunAll executes both parsers a fixed number of iterations
func RunAll(iter int) []Result {
	return []Result{
		runFIT(iter),
		runGPX(iter),
	}
}
