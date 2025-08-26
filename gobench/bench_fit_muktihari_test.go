package gobench

import (
	"bytes"
	"os"
	"testing"

	"github.com/muktihari/fit/decoder"
	"github.com/muktihari/fit/profile/filedef"
)

var fitBytes []byte

func TestMain(m *testing.M) {
	var err error
	fitBytes, err = os.ReadFile("../testdata/BWR_San_Diego_Waffle_Ride_.fit")
	if err != nil {
		panic(err)
	}
	os.Exit(m.Run())
}

func BenchmarkParseFITMuktihari(b *testing.B) {
	b.ReportAllocs()
	b.SetBytes(int64(len(fitBytes)))
	for i := 0; i < b.N; i++ {
		lis := filedef.NewListener()
		dec := decoder.New(bytes.NewReader(fitBytes),
			decoder.WithMesgListener(lis),
			decoder.WithBroadcastOnly(),
		)
		_, err := dec.Decode()
		if err != nil {
			b.Fatal(err)
		}
		_ = lis.File() // ensure the file is processed
		lis.Close()
	}
}
