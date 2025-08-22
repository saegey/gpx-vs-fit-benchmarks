package main

import (
	"bytes"
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"sort"
	"time"

	"github.com/tkrajina/gpxgo/gpx"
	"github.com/tormoder/fit"
)

type stats struct {
	N         int           `json:"n"`
	MeanMs    float64       `json:"mean_ms"`
	P50Ms     float64       `json:"p50_ms"`
	P95Ms     float64       `json:"p95_ms"`
	MinMs     float64       `json:"min_ms"`
	MaxMs     float64       `json:"max_ms"`
	Bytes     int           `json:"bytes"`
	Label     string        `json:"label"`
	TotalTime time.Duration `json:"-"`
}

func run(label string, data []byte, n int, parse func([]byte) error) stats {
	times := make([]float64, 0, n)
	var min, max float64
	var sum float64
	min = 1e18

	startAll := time.Now()
	for i := 0; i < n; i++ {
		t0 := time.Now()
		if err := parse(data); err != nil {
			fmt.Fprintf(os.Stderr, "%s parse error: %v\n", label, err)
			os.Exit(1)
		}
		d := time.Since(t0).Seconds() * 1000
		times = append(times, d)
		if d < min {
			min = d
		}
		if d > max {
			max = d
		}
		sum += d
	}
	total := time.Since(startAll)

	sort.Float64s(times)
	p50 := times[len(times)/2]
	p95 := times[int(float64(len(times))*0.95)-1]

	return stats{
		N:         n,
		MeanMs:    sum / float64(n),
		P50Ms:     p50,
		P95Ms:     p95,
		MinMs:     min,
		MaxMs:     max,
		Bytes:     len(data),
		Label:     label,
		TotalTime: total,
	}
}

func parseFIT(b []byte) error {
	_, err := fit.Decode(bytes.NewReader(b))
	return err
}

func parseGPX(b []byte) error {
	_, err := gpx.Parse(bytes.NewReader(b))
	return err
}

func main() {
	fitPath := flag.String("fit", "testdata/activity.fit", "FIT file path")
	gpxPath := flag.String("gpx", "testdata/activity.gpx", "GPX file path")
	n := flag.Int("n", 25, "iterations per format")
	jsonOut := flag.Bool("json", false, "print JSON summary")
	flag.Parse()

	fitBytes, err := os.ReadFile(*fitPath)
	if err != nil {
		panic(err)
	}
	gpxBytes, err := os.ReadFile(*gpxPath)
	if err != nil {
		panic(err)
	}

	fitStats := run("FIT", fitBytes, *n, parseFIT)
	gpxStats := run("GPX", gpxBytes, *n, parseGPX)

	if *jsonOut {
		out := map[string]stats{"fit": fitStats, "gpx": gpxStats}
		enc := json.NewEncoder(os.Stdout)
		enc.SetIndent("", "  ")
		enc.Encode(out)
		return
	}

	fmt.Printf("FIT  : size=%dB  n=%d  mean=%.2fms  p50=%.2fms  p95=%.2fms  min=%.2fms  max=%.2fms\n",
		fitStats.Bytes, fitStats.N, fitStats.MeanMs, fitStats.P50Ms, fitStats.P95Ms, fitStats.MinMs, fitStats.MaxMs)
	fmt.Printf("GPX  : size=%dB  n=%d  mean=%.2fms  p50=%.2fms  p95=%.2fms  min=%.2fms  max=%.2fms\n",
		gpxStats.Bytes, gpxStats.N, gpxStats.MeanMs, gpxStats.P50Ms, gpxStats.P95Ms, gpxStats.MinMs, gpxStats.MaxMs)
	fmt.Printf("\nSpeedup (GPX/FIT mean): %.2fx\n", gpxStats.MeanMs/fitStats.MeanMs)
	fmt.Printf("File size ratio (GPX/FIT): %.2fx\n", float64(gpxStats.Bytes)/float64(fitStats.Bytes))
}
