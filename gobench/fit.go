// gobench/fit.go
package gobench

import (
	"bytes"
	_ "embed"
	"time"

	"github.com/tormoder/fit"
)

//go:embed testdata/BWR_San_Diego_Waffle_Ride_.fit
var fitBytes []byte

func RunFit(iter int) (Result, error) {
	fitDur := make([]time.Duration, iter)
	for i := 0; i < iter; i++ {
		start := time.Now()
		if _, err := fit.Decode(bytes.NewReader(fitBytes)); err != nil {
			return Result{}, err
		}
		fitDur[i] = time.Since(start)
	}
	return summarize("FIT", "tormoder/fit", iter, fitDur), nil
}
