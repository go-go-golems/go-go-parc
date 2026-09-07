package webui

import (
	"bytes"
	"embed"
	"encoding/json"
	"fmt"
	"io"
	"io/fs"
	"mime"
	"net/http"
	"strings"
	"time"

	"servicelang/internal/compiler"
)

//go:embed assets presets runtime
var bundled embed.FS

type Preset struct {
	ID, Title, Description, Filename, Source, Plan string
	Expected                                       bool
}

func Presets() ([]Preset, error) {
	read := func(name string) (string, error) { b, e := bundled.ReadFile("presets/" + name); return string(b), e }
	sensor, e := read("sensor.svc")
	if e != nil {
		return nil, e
	}
	memory, e := read("ownership.svc")
	if e != nil {
		return nil, e
	}
	branch, e := read("branch.svc")
	if e != nil {
		return nil, e
	}
	bad, e := read("double-move.invalid.svc")
	if e != nil {
		return nil, e
	}
	plan, e := read("sensor.plan.json")
	if e != nil {
		return nil, e
	}
	marker := "close(move ready);"
	at := strings.LastIndex(branch, marker)
	if at < 0 {
		return nil, fmt.Errorf("branch preset lost its mutation anchor")
	}
	leak := branch[:at] + branch[at+len(marker):]
	return []Preset{
		{"sensor", "Sensor · explicit polling", "Start, Waiting and Complete over the actual SensorRPC inventory.", "sensor.svc", sensor, "", true},
		{"memory", "Buffer · checked arithmetic", "Allocate, read, release; overflow remains an explicit alternative.", "ownership.svc", memory, "", true},
		{"branch", "Branch · both paths consume", "Pin this baseline, then compare the one-arm leak.", "branch.svc", branch, "", true},
		{"branch-leak", "Branch · one path leaks", "One close removed from the same source. The join is {L,D}.", "branch-leak.svc", leak, "", false},
		{"double-move", "Move · consumed twice", "The second move points back to the first ownership transfer.", "double-move.invalid.svc", bad, "", false},
		{"startup", "Startup · checked wiring", "Two fixed endpoints with reversed component order and declared authorities.", "sensor.svc", sensor, plan, true},
		{"startup-denied", "Startup · undeclared endpoint", "The same compiler accepts source but rejects this wiring plan.", "sensor.svc", sensor, strings.ReplaceAll(plan, `"endpoint": "radio-b"`, `"endpoint": "undeclared"`), false},
	}, nil
}
func writeJSON(w http.ResponseWriter, status int, value any) {
	w.Header().Set("Content-Type", "application/json")
	w.Header().Set("Cache-Control", "no-store")
	w.WriteHeader(status)
	_ = json.NewEncoder(w).Encode(value)
}
func NewHandler() (http.Handler, error) {
	presets, err := Presets()
	if err != nil {
		return nil, err
	}
	public, err := fs.Sub(bundled, "assets")
	if err != nil {
		return nil, err
	}
	implementation, err := compiler.ImplementationFiles()
	if err != nil {
		return nil, err
	}
	native, err := bundled.ReadDir("runtime")
	if err != nil {
		return nil, err
	}
	for _, f := range native {
		b, e := bundled.ReadFile("runtime/" + f.Name())
		if e != nil {
			return nil, e
		}
		implementation["runtime/"+f.Name()] = string(b)
	}
	mux := http.NewServeMux()
	busy := make(chan struct{}, 1)
	mux.HandleFunc("GET /api/presets", func(w http.ResponseWriter, r *http.Request) { writeJSON(w, 200, presets) })
	mux.HandleFunc("GET /api/implementation", func(w http.ResponseWriter, r *http.Request) { writeJSON(w, 200, implementation) })
	mux.HandleFunc("POST /api/analyze", func(w http.ResponseWriter, r *http.Request) {
		media, _, err := mime.ParseMediaType(r.Header.Get("Content-Type"))
		if err != nil || media != "application/json" {
			writeJSON(w, 415, map[string]string{"error": "application/json required"})
			return
		}
		select {
		case busy <- struct{}{}:
			defer func() { <-busy }()
		default:
			writeJSON(w, 429, map[string]string{"error": "compiler busy; retry when the current request finishes"})
			return
		}
		r.Body = http.MaxBytesReader(w, r.Body, 1<<20)
		defer r.Body.Close()
		var request struct{ Source, Filename, Plan string }
		d := json.NewDecoder(r.Body)
		d.DisallowUnknownFields()
		if err = d.Decode(&request); err != nil {
			writeJSON(w, 400, map[string]string{"error": err.Error()})
			return
		}
		if err = d.Decode(new(any)); err != io.EOF {
			writeJSON(w, 400, map[string]string{"error": "one JSON object required"})
			return
		}
		if len(request.Source) > 65536 || len(request.Plan) > 65536 || len(request.Filename) > 256 {
			writeJSON(w, 413, map[string]string{"error": "source/plan limit 64 KiB; filename limit 256 bytes"})
			return
		}
		if request.Filename == "" {
			request.Filename = "editor.svc"
		}
		report, err := compiler.Inspect(request.Filename, request.Source, []byte(request.Plan))
		if err != nil {
			writeJSON(w, 500, map[string]string{"error": err.Error()})
			return
		}
		writeJSON(w, 200, report)
	})
	mux.HandleFunc("GET /api", http.NotFound)
	mux.HandleFunc("GET /api/", http.NotFound)
	mux.HandleFunc("GET /", func(w http.ResponseWriter, r *http.Request) {
		name := strings.TrimPrefix(r.URL.Path, "/")
		if name == "" {
			name = "index.html"
		}
		if !fs.ValidPath(name) {
			http.NotFound(w, r)
			return
		}
		data, err := fs.ReadFile(public, name)
		if err != nil {
			if strings.Contains(name, ".") {
				http.NotFound(w, r)
				return
			}
			name = "index.html"
			data, err = fs.ReadFile(public, name)
		}
		if err != nil {
			http.NotFound(w, r)
			return
		}
		if name == "index.html" {
			w.Header().Set("Cache-Control", "no-store")
		}
		http.ServeContent(w, r, name, time.Time{}, bytes.NewReader(data))
	})
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("X-Content-Type-Options", "nosniff")
		mux.ServeHTTP(w, r)
	}), nil
}
