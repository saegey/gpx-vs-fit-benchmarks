package main

import (
	"encoding/json"
	"fmt"
	"os"
	"strconv"

	"github.com/saegey/gpx-vs-fit-benchmarks/gobench"
)

func main() {
	iters := 25
	if len(os.Args) > 1 {
		if n, err := strconv.Atoi(os.Args[1]); err == nil {
			iters = n
		}
	}
	result, err := gobench.RunFit(iters)
	if err != nil {
		fmt.Fprintln(os.Stderr, "Error:", err)
		os.Exit(1)
	}
	b, _ := json.MarshalIndent([]gobench.Result{result}, "", "  ")
	fmt.Println(string(b))
}
