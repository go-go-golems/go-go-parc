package instrumentlock

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"testing"
)

func writeFile(t *testing.T, root, relative, content string) {
	t.Helper()
	path := filepath.Join(root, filepath.FromSlash(relative))
	if err := os.MkdirAll(filepath.Dir(path), 0o755); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(path, []byte(content), 0o644); err != nil {
		t.Fatal(err)
	}
}

func fixtureManifest() Manifest {
	return Manifest{
		Instrument: "test-judge",
		Version:    "v1",
		Entries: []Entry{
			{Role: RoleHarnessSource, Path: "harness/judge.go"},
			{Role: RolePromptAsset, Path: "assets/prompt.txt"},
			{Role: RoleDataset, Path: "data/golden.json"},
		},
		SealedRoots: []string{"assets"},
		Dimensions:  map[string]string{"answer_model": "m-low", "judge_model": "m"},
	}
}

func buildFixture(t *testing.T) (string, Manifest) {
	t.Helper()
	root := t.TempDir()
	writeFile(t, root, "harness/judge.go", "package judge // v1")
	writeFile(t, root, "assets/prompt.txt", "You judge statements.")
	writeFile(t, root, "data/golden.json", `{"questions":[]}`)
	frozen, err := Freeze(root, fixtureManifest(), nil)
	if err != nil {
		t.Fatal(err)
	}
	return root, frozen
}

func observed() map[string]string {
	return map[string]string{"answer_model": "m-low", "judge_model": "m"}
}

func kinds(findings []Finding) map[FindingKind]int {
	counts := map[FindingKind]int{}
	for _, finding := range findings {
		counts[finding.Kind]++
	}
	return counts
}

func TestFreezeVerifyRoundTrip(t *testing.T) {
	root, frozen := buildFixture(t)
	findings := Verify(root, frozen, VerifyOptions{Observed: observed()})
	if err := FirstError(findings); err != nil {
		t.Fatalf("clean fixture must verify: %v", err)
	}
	for _, entry := range frozen.Entries {
		if entry.Digest == "" || entry.SizeBytes <= 0 {
			t.Fatalf("freeze left entry %q incomplete", entry.Path)
		}
	}
}

func TestDriftedFileIsRejected(t *testing.T) {
	root, frozen := buildFixture(t)
	writeFile(t, root, "assets/prompt.txt", "You judge statements. Be nice.")
	findings := Verify(root, frozen, VerifyOptions{Observed: observed()})
	if kinds(findings)[FindingDrift] != 1 {
		t.Fatalf("expected one drift finding, got %v", findings)
	}
	if err := FirstError(findings); err == nil {
		t.Fatal("drift must fail verification")
	}
	for _, finding := range findings {
		if finding.Kind == FindingDrift {
			if finding.Path != "assets/prompt.txt" || finding.Role != RolePromptAsset {
				t.Fatalf("drift finding misattributed: %+v", finding)
			}
			if finding.Expected == finding.Observed || finding.Expected == "" {
				t.Fatalf("drift finding must carry both digests: %+v", finding)
			}
		}
	}
}

func TestMissingFileIsRejected(t *testing.T) {
	root, frozen := buildFixture(t)
	if err := os.Remove(filepath.Join(root, "data", "golden.json")); err != nil {
		t.Fatal(err)
	}
	findings := Verify(root, frozen, VerifyOptions{Observed: observed()})
	if kinds(findings)[FindingMissing] != 1 {
		t.Fatalf("expected one missing finding, got %v", findings)
	}
}

func TestExtraFileInSealedRootIsRejected(t *testing.T) {
	root, frozen := buildFixture(t)
	writeFile(t, root, "assets/injected.txt", "surprise prompt")
	findings := Verify(root, frozen, VerifyOptions{Observed: observed()})
	if kinds(findings)[FindingUntracked] != 1 {
		t.Fatalf("expected one untracked finding, got %v", findings)
	}
	var untracked Finding
	for _, finding := range findings {
		if finding.Kind == FindingUntracked {
			untracked = finding
		}
	}
	if untracked.Path != "assets/injected.txt" {
		t.Fatalf("untracked finding misattributed: %+v", untracked)
	}
}

func TestStaleVersionKeyCannotSeeOldPopulation(t *testing.T) {
	cache := map[string]string{}
	payload := struct {
		Model  string `json:"model"`
		Prompt string `json:"prompt"`
	}{Model: "m", Prompt: "judge this"}

	v1, err := NewPopulationKey("statements", "v1", "m", payload)
	if err != nil {
		t.Fatal(err)
	}
	cache[v1.Key()] = "cached v1 verdict"

	v2, err := NewPopulationKey("statements", "v2", "m", payload)
	if err != nil {
		t.Fatal(err)
	}
	if v1.Key() == v2.Key() {
		t.Fatal("distinct instrument versions must produce disjoint key spaces")
	}
	if _, hit := cache[v2.Key()]; hit {
		t.Fatal("stale population leaked across an instrument version bump")
	}

	again, err := NewPopulationKey("statements", "v1", "m", payload)
	if err != nil {
		t.Fatal(err)
	}
	if again.Key() != v1.Key() {
		t.Fatal("identical coordinates must reproduce the identical key")
	}
}

func TestPopulationKeyCanonicalizesMapPayloads(t *testing.T) {
	a, err := NewPopulationKey("verdicts", "v1", "m", map[string]string{"x": "1", "y": "2"})
	if err != nil {
		t.Fatal(err)
	}
	b, err := NewPopulationKey("verdicts", "v1", "m", map[string]string{"y": "2", "x": "1"})
	if err != nil {
		t.Fatal(err)
	}
	if a.Key() != b.Key() {
		t.Fatal("map payload insertion order must not change the key")
	}
}

func TestProvisionalManifestIsRejected(t *testing.T) {
	root, frozen := buildFixture(t)
	frozen.Provisional = "freeze pending review"
	findings := Verify(root, frozen, VerifyOptions{Observed: observed()})
	if kinds(findings)[FindingProvisional] != 1 {
		t.Fatalf("expected provisional finding, got %v", findings)
	}
	if err := FirstError(findings); err == nil {
		t.Fatal("provisional manifest must not verify")
	}
}

func TestPathEscapeIsRejected(t *testing.T) {
	root := t.TempDir()
	manifest := Manifest{
		Instrument: "escape", Version: "v1",
		Entries: []Entry{{Role: RoleDataset, Path: "../outside.txt"}},
	}
	if _, err := Freeze(root, manifest, nil); err == nil {
		t.Fatal("freeze must reject escaping paths")
	}
	manifest.Entries[0].Digest = "sha256:deadbeef"
	manifest.Entries[0].SizeBytes = 1
	manifest.APIVersion = APIVersion
	findings := Verify(root, manifest, VerifyOptions{})
	if kinds(findings)[FindingPathEscape] != 1 {
		t.Fatalf("expected path escape finding, got %v", findings)
	}
}

func TestDimensionDriftAndUndeclared(t *testing.T) {
	root, frozen := buildFixture(t)
	runtimeObserved := map[string]string{
		"answer_model": "m-low",
		"judge_model":  "different",
		"tool_loop":    "max20",
	}
	findings := Verify(root, frozen, VerifyOptions{Observed: runtimeObserved})
	counts := kinds(findings)
	if counts[FindingDimensionDrift] != 1 {
		t.Fatalf("expected one dimension drift, got %v", findings)
	}
	if counts[FindingUndeclaredDimension] != 1 {
		t.Fatalf("expected one undeclared advisory, got %v", findings)
	}
	var advisoryOnly []Finding
	for _, finding := range findings {
		if finding.Kind == FindingUndeclaredDimension {
			if !finding.Advisory {
				t.Fatal("undeclared dimension must be advisory")
			}
			advisoryOnly = append(advisoryOnly, finding)
		}
	}
	if err := FirstError(advisoryOnly); err != nil {
		t.Fatal("advisory findings alone must not fail verification")
	}
}

func TestExtractorSelectsSubtree(t *testing.T) {
	root := t.TempDir()
	writeFile(t, root, "profiles.json", `{"selected":{"model":"m"},"other":{"model":"x"}}`)
	extractors := map[string]Extractor{
		"selected-profile": func(data []byte) ([]byte, error) {
			var document map[string]json.RawMessage
			if err := json.Unmarshal(data, &document); err != nil {
				return nil, err
			}
			selected, ok := document["selected"]
			if !ok {
				return nil, fmt.Errorf("no selected profile")
			}
			return selected, nil
		},
	}
	manifest := Manifest{
		Instrument: "profile-lock", Version: "v1",
		Entries: []Entry{{Role: RoleConfiguration, Path: "profiles.json", Extractor: "selected-profile"}},
	}
	frozen, err := Freeze(root, manifest, extractors)
	if err != nil {
		t.Fatal(err)
	}

	writeFile(t, root, "profiles.json", `{"selected":{"model":"m"},"other":{"model":"CHANGED"}}`)
	if err := FirstError(Verify(root, frozen, VerifyOptions{Extractors: extractors})); err != nil {
		t.Fatalf("unrelated profile change must not drift the selected lock: %v", err)
	}

	writeFile(t, root, "profiles.json", `{"selected":{"model":"CHANGED"},"other":{"model":"x"}}`)
	findings := Verify(root, frozen, VerifyOptions{Extractors: extractors})
	if kinds(findings)[FindingDrift] != 1 {
		t.Fatalf("selected profile change must drift, got %v", findings)
	}

	missing := Verify(root, frozen, VerifyOptions{})
	if kinds(missing)[FindingExtractorMissing] != 1 {
		t.Fatalf("verification without the extractor must fail explicitly, got %v", missing)
	}
}

func TestSelfInclusionFreezesOwnSource(t *testing.T) {
	manifest := Manifest{
		Instrument: "instrumentlock-self", Version: "v1",
		Entries: []Entry{
			{Role: RoleHarnessSource, Path: "instrumentlock.go"},
			{Role: RoleHarnessSource, Path: "populationkey.go"},
			{Role: RoleDependencyPin, Path: "go.mod"},
		},
	}
	frozen, err := Freeze(".", manifest, nil)
	if err != nil {
		t.Fatal(err)
	}
	if err := FirstError(Verify(".", frozen, VerifyOptions{})); err != nil {
		t.Fatalf("self-digest of the package's own source must verify: %v", err)
	}
	digest, err := ManifestDigest(frozen)
	if err != nil {
		t.Fatal(err)
	}
	if digest == "" || digest[:7] != "sha256:" {
		t.Fatalf("manifest digest malformed: %q", digest)
	}
}

func TestSaveLoadRoundTripAndUnknownFieldRejection(t *testing.T) {
	root, frozen := buildFixture(t)
	path := filepath.Join(root, "lock.json")
	if err := Save(path, frozen); err != nil {
		t.Fatal(err)
	}
	loaded, err := Load(path)
	if err != nil {
		t.Fatal(err)
	}
	if err := FirstError(Verify(root, loaded, VerifyOptions{Observed: observed()})); err != nil {
		t.Fatalf("loaded manifest must verify: %v", err)
	}
	writeFile(t, root, "bad.json", `{"api_version":"instrument-lock/v1","instrument":"x","version":"v1","entries":[],"surprise":true}`)
	if _, err := Load(filepath.Join(root, "bad.json")); err == nil {
		t.Fatal("unknown manifest fields must be rejected")
	}
}

func TestVerifyBuildRevisionIsAdvisoryWhenUnstamped(t *testing.T) {
	findings := VerifyBuildRevision("abc123")
	if len(findings) != 1 || !findings[0].Advisory {
		t.Fatalf("test binaries are unstamped; expected one advisory finding, got %v", findings)
	}
}
