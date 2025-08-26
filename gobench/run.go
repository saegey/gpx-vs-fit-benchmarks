package gobench

import (
	"bytes"
	"os"
	"testing"

	"github.com/tkrajina/gpxgo/gpx"
	"github.com/tormoder/fit"
)

var fitBytes, gpxBytes []byte

func TestMain(m *testing.M) {
	var err error
	fitBytes, err = os.ReadFile("../testdata/BWR_San_Diego_Waffle_Ride_.fit")
	if err != nil {
		panic(err)
	}
	gpxBytes, err = os.ReadFile("testdata/BWR_San_Diego_Waffle_Ride_.gpx")
	if err != nil {
		panic(err)
	}
	os.Exit(m.Run())
}

func BenchmarkParseFIT(b *testing.B) {
	b.ReportAllocs()
	b.SetBytes(int64(len(fitBytes)))
	for i := 0; i < b.N; i++ {
		_, err := fit.Decode(bytes.NewReader(fitBytes))
		if err != nil {
			b.Fatal(err)
		}
	}
}

func BenchmarkParseGPX(b *testing.B) {
	b.ReportAllocs()
	b.SetBytes(int64(len(gpxBytes)))
	for i := 0; i < b.N; i++ {
		_, err := gpx.Parse(bytes.NewReader(gpxBytes))
		if err != nil {
			b.Fatal(err)
		}
	}
}
