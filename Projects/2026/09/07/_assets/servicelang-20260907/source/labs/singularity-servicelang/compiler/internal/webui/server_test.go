package webui

import (
	"bytes"
	"encoding/json"
	"net/http/httptest"
	"strings"
	"testing"

	"servicelang/internal/compiler"
)

func TestHTTPExplorer(t *testing.T) {
	handler, err := NewHandler()
	if err != nil {
		t.Fatal(err)
	}
	presets, err := Presets()
	if err != nil {
		t.Fatal(err)
	}
	for _, p := range presets {
		t.Run(p.ID, func(t *testing.T) {
			body, _ := json.Marshal(map[string]string{"Source": p.Source, "Filename": p.Filename, "Plan": p.Plan})
			request := httptest.NewRequest("POST", "/api/analyze", bytes.NewReader(body))
			request.Header.Set("Content-Type", "application/json")
			response := httptest.NewRecorder()
			handler.ServeHTTP(response, request)
			if response.Code != 200 {
				t.Fatal(response.Code, response.Body.String())
			}
			var r compiler.Inspection
			if err := json.Unmarshal(response.Body.Bytes(), &r); err != nil {
				t.Fatal(err)
			}
			if r.Accepted != p.Expected {
				t.Fatalf("unexpected preset result: %+v", r.Diagnostics)
			}
			if !r.Accepted && r.Output != nil {
				t.Fatal("rejected API source emitted output")
			}
		})
	}
	for _, tc := range []struct {
		path   string
		status int
	}{{"/", 200}, {"/explore", 200}, {"/api/missing", 404}, {"/missing.js", 404}} {
		response := httptest.NewRecorder()
		handler.ServeHTTP(response, httptest.NewRequest("GET", tc.path, nil))
		if response.Code != tc.status {
			t.Fatalf("%s: %d", tc.path, response.Code)
		}
		if tc.status == 200 && !strings.Contains(response.Body.String(), "ServiceLang") {
			t.Fatal("SPA missing")
		}
	}
	response := httptest.NewRecorder()
	handler.ServeHTTP(response, httptest.NewRequest("POST", "/api/analyze", strings.NewReader(`{}`)))
	if response.Code != 415 {
		t.Fatal("missing JSON content type accepted")
	}
}
