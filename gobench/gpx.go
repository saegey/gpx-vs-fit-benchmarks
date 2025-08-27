// gobench/gpx.go
package gobench

import (
	"bytes"
	_ "embed"
	"time"

	"github.com/tkrajina/gpxgo/gpx"
)

//go:embed testdata/BWR_San_Diego_Waffle_Ride_.gpx
var gpxBytes []byte

func RunGpx(iter int) (Result, error) {
	gpxDur := make([]time.Duration, iter)
	for i := 0; i < iter; i++ {
		start := time.Now()
		if _, err := gpx.Parse(bytes.NewReader(gpxBytes)); err != nil {
			return Result{}, err
		}
		gpxDur[i] = time.Since(start)
	}
	return summarize("GPX", "tkrajina/gpxgo", iter, gpxDur), nil
}
