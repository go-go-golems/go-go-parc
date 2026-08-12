package main

import (
	"bufio"
	"encoding/json"
	"flag"
	"fmt"
	"os"

	"dispatchlab"
)

func main() {
	output := flag.String("output", "-", "model-event JSONL output path, or - for stdout")
	intervalOutput := flag.String("interval-output", "", "operation-interval JSONL output path")
	runID := flag.String("run-id", "tracegen-run", "stable trace run partition")
	dispatcherID := flag.String("dispatcher-id", "observer-1", "stable dispatcher partition")
	flag.Parse()

	callbackEntered := make(chan struct{})
	releaseCallback := make(chan struct{})
	delivered := make([]int, 0, 3)
	d, err := dispatchlab.NewCheckedWithIdentity[int](2, func(v int) {
		delivered = append(delivered, v)
		if v == 10 {
			close(callbackEntered)
			<-releaseCallback
		}
		if v == 20 {
			panic("intentional tracegen callback panic")
		}
	}, dispatchlab.TraceIdentity{RunID: *runID, DispatcherID: *dispatcherID})
	if err != nil {
		fatal(err)
	}

	// Move one item in flight, fill the two-slot queue, and force one drop.
	if !d.TrySubmit(10) {
		fatal(fmt.Errorf("first sample submission was not admitted"))
	}
	<-callbackEntered
	if !d.TrySubmit(20) || !d.TrySubmit(30) {
		fatal(fmt.Errorf("queued sample submissions were not admitted"))
	}
	if d.TrySubmit(40) {
		fatal(fmt.Errorf("full-queue sample submission was unexpectedly admitted"))
	}

	// Exercise effective close, idempotent close, and post-close rejection.
	d.Close()
	d.Close()
	if d.TrySubmit(50) {
		fatal(fmt.Errorf("post-close sample submission was unexpectedly admitted"))
	}
	close(releaseCallback)
	d.Wait()

	if len(delivered) != 3 || delivered[0] != 10 || delivered[1] != 20 || delivered[2] != 30 {
		fatal(fmt.Errorf("delivery order mismatch: %v", delivered))
	}
	if d.Dropped() != 1 {
		fatal(fmt.Errorf("drop count mismatch: %d", d.Dropped()))
	}

	if err := writeJSONL(*output, d.ModelTrace()); err != nil {
		fatal(err)
	}
	if *intervalOutput != "" {
		if err := writeJSONL(*intervalOutput, d.OperationIntervals()); err != nil {
			fatal(err)
		}
	}
}

func writeJSONL[T any](path string, events []T) error {
	var file *os.File
	var err error
	if path == "-" {
		file = os.Stdout
	} else {
		file, err = os.Create(path)
		if err != nil {
			return err
		}
		defer file.Close()
	}
	writer := bufio.NewWriter(file)
	encoder := json.NewEncoder(writer)
	for _, event := range events {
		if err := encoder.Encode(event); err != nil {
			return err
		}
	}
	return writer.Flush()
}

func fatal(err error) {
	fmt.Fprintln(os.Stderr, "tracegen:", err)
	os.Exit(1)
}
