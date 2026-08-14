package instrumentlock

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io/fs"
	"os"
	"path/filepath"
	"sort"
	"strings"
)

// APIVersion identifies the manifest schema. A future incompatible manifest
// must change this string; Verify rejects any other value.
const APIVersion = "instrument-lock/v1"

// Role records why an entry is frozen. Roles do not change verification
// mechanics; they exist so findings and trust ledgers can name what kind of
// apparatus drifted.
type Role string

const (
	// RoleHarnessSource marks the measuring code itself, including the file
	// that performs verification. Self-inclusion is the point: the instrument
	// freezes its own implementation, closing the "who watches the harness"
	// regress at exactly one level (the level the manifest digest occupies).
	RoleHarnessSource Role = "harness-source"
	// RolePromptAsset marks prompt text whose bytes reach a model.
	RolePromptAsset Role = "prompt-asset"
	// RoleDataset marks golden sets, suites, and other ground-truth inputs.
	RoleDataset Role = "dataset"
	// RoleDependencyPin marks files that pin dependency identity (go.mod,
	// go.sum, lockfiles).
	RoleDependencyPin Role = "dependency-pin"
	// RoleConfiguration marks profiles, registries, and runtime configuration.
	RoleConfiguration Role = "configuration"
)

// Entry freezes one file. Path is slash-separated and relative to the
// verification root. Digest covers the extracted content; SizeBytes is the
// length of the hashed (post-extraction) content so the size invariant has one
// meaning for raw and extracted entries alike.
type Entry struct {
	Role      Role   `json:"role"`
	Path      string `json:"path"`
	Digest    string `json:"digest"`
	SizeBytes int64  `json:"size_bytes"`
	// Extractor optionally names a normalization applied before hashing, such
	// as selecting one profile out of a registry file (rag-ttc's
	// profileDefinitionDigest). The extractor implementation is harness source
	// and must itself be covered by a RoleHarnessSource entry; the manifest
	// records only the name.
	Extractor string `json:"extractor,omitempty"`
}

// Manifest is the frozen apparatus identity. Dimensions carries declared
// expectations about the runtime environment (model identities, tool-loop
// configuration) that Verify compares against observed values.
type Manifest struct {
	APIVersion string `json:"api_version"`
	Instrument string `json:"instrument"`
	// Version is the instrument version (CoinVault's judgePromptVersion
	// discipline). It participates in PopulationKey derivation: bumping it
	// makes every previously cached measurement invisible, by construction.
	Version string `json:"version"`
	// Provisional, when non-empty, records that the freeze is not final.
	// Verification refuses provisional manifests, mirroring CoinVault's
	// implementation_note blocker.
	Provisional string            `json:"provisional,omitempty"`
	Entries     []Entry           `json:"entries"`
	SealedRoots []string          `json:"sealed_roots,omitempty"`
	Dimensions  map[string]string `json:"dimensions,omitempty"`
}

// Extractor normalizes file bytes before hashing. It must be deterministic;
// a nondeterministic extractor makes freeze and verify disagree spuriously.
type Extractor func(data []byte) ([]byte, error)

// FindingKind classifies one verification failure.
type FindingKind string

const (
	FindingSchemaInvalid       FindingKind = "schema-invalid"
	FindingProvisional         FindingKind = "provisional"
	FindingPathEscape          FindingKind = "path-escape"
	FindingMissing             FindingKind = "missing"
	FindingDrift               FindingKind = "drift"
	FindingUntracked           FindingKind = "untracked"
	FindingDimensionDrift      FindingKind = "dimension-drift"
	FindingUndeclaredDimension FindingKind = "undeclared-dimension"
	FindingExtractorMissing    FindingKind = "extractor-missing"
)

// Finding is one typed verification result. Verify returns every finding
// rather than the first, so an operator sees complete drift in one pass;
// FirstError restores fail-fast semantics for callers that want them.
type Finding struct {
	Kind      FindingKind `json:"kind"`
	Path      string      `json:"path,omitempty"`
	Role      Role        `json:"role,omitempty"`
	Dimension string      `json:"dimension,omitempty"`
	Expected  string      `json:"expected,omitempty"`
	Observed  string      `json:"observed,omitempty"`
	// Advisory findings report conditions worth surfacing that do not fail
	// verification (undeclared observed dimensions).
	Advisory bool   `json:"advisory,omitempty"`
	Detail   string `json:"detail,omitempty"`
}

func (f Finding) String() string {
	parts := []string{string(f.Kind)}
	if f.Path != "" {
		parts = append(parts, "path="+f.Path)
	}
	if f.Dimension != "" {
		parts = append(parts, "dimension="+f.Dimension)
	}
	if f.Expected != "" || f.Observed != "" {
		parts = append(parts, fmt.Sprintf("expected=%s observed=%s", f.Expected, f.Observed))
	}
	if f.Detail != "" {
		parts = append(parts, f.Detail)
	}
	return strings.Join(parts, " ")
}

// FirstError returns an error describing the first non-advisory finding, or
// nil when verification passed (possibly with advisory findings).
func FirstError(findings []Finding) error {
	for _, finding := range findings {
		if !finding.Advisory {
			return fmt.Errorf("instrument lock violated: %s", finding.String())
		}
	}
	return nil
}

func digestBytes(data []byte) string {
	sum := sha256.Sum256(data)
	return "sha256:" + hex.EncodeToString(sum[:])
}

// confine resolves a slash-relative entry path under root and rejects
// absolute paths and escapes, following CoinVault's source-lock confinement.
func confine(root, slashPath string) (string, error) {
	if slashPath == "" {
		return "", fmt.Errorf("entry path is empty")
	}
	if filepath.IsAbs(filepath.FromSlash(slashPath)) {
		return "", fmt.Errorf("entry path %q is absolute", slashPath)
	}
	joined := filepath.Join(root, filepath.FromSlash(slashPath))
	relative, err := filepath.Rel(root, joined)
	if err != nil || relative == ".." || strings.HasPrefix(relative, ".."+string(filepath.Separator)) {
		return "", fmt.Errorf("entry path %q escapes the root", slashPath)
	}
	return joined, nil
}

func hashedContent(path string, extractorName string, extractors map[string]Extractor) ([]byte, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, err
	}
	if extractorName == "" {
		return data, nil
	}
	extractor, ok := extractors[extractorName]
	if !ok {
		return nil, fmt.Errorf("extractor %q is not registered", extractorName)
	}
	extracted, err := extractor(data)
	if err != nil {
		return nil, fmt.Errorf("extractor %q: %w", extractorName, err)
	}
	return extracted, nil
}

// Freeze completes a manifest: it validates the schema, confines and sorts
// entry paths, rejects duplicates, and fills each entry's Digest and
// SizeBytes from the current worktree. The returned manifest is the frozen
// apparatus identity; callers should persist it and record ManifestDigest of
// it in their experiment snapshot so the lock itself is bound by the
// experiment's identity chain.
func Freeze(root string, manifest Manifest, extractors map[string]Extractor) (Manifest, error) {
	if manifest.APIVersion == "" {
		manifest.APIVersion = APIVersion
	}
	if manifest.APIVersion != APIVersion {
		return Manifest{}, fmt.Errorf("unsupported manifest api version %q", manifest.APIVersion)
	}
	if strings.TrimSpace(manifest.Instrument) == "" || strings.TrimSpace(manifest.Version) == "" {
		return Manifest{}, fmt.Errorf("manifest instrument and version are required")
	}
	seen := map[string]bool{}
	entries := append([]Entry(nil), manifest.Entries...)
	sort.Slice(entries, func(i, j int) bool { return entries[i].Path < entries[j].Path })
	for index := range entries {
		entry := &entries[index]
		if seen[entry.Path] {
			return Manifest{}, fmt.Errorf("duplicate entry path %q", entry.Path)
		}
		seen[entry.Path] = true
		resolved, err := confine(root, entry.Path)
		if err != nil {
			return Manifest{}, err
		}
		content, err := hashedContent(resolved, entry.Extractor, extractors)
		if err != nil {
			return Manifest{}, fmt.Errorf("freeze %s: %w", entry.Path, err)
		}
		entry.Digest = digestBytes(content)
		entry.SizeBytes = int64(len(content))
	}
	manifest.Entries = entries
	sort.Strings(manifest.SealedRoots)
	return manifest, nil
}

// ManifestDigest is the lock's own identity: the digest of its canonical JSON
// encoding. Recording this value as a snapshot dimension closes the regress —
// the lock binds the apparatus, and the experiment identity binds the lock.
func ManifestDigest(manifest Manifest) (string, error) {
	data, err := json.Marshal(manifest)
	if err != nil {
		return "", err
	}
	return digestBytes(data), nil
}

// VerifyOptions carries the extractor registry and the runtime-observed
// dimension values to compare against the manifest's declared dimensions.
type VerifyOptions struct {
	Extractors map[string]Extractor
	Observed   map[string]string
}

// Verify checks a frozen manifest against the worktree under root and the
// observed runtime dimensions. It returns every finding; an empty (or
// advisory-only) slice is a pass. Verify never mutates anything and performs
// no network or provider calls: it is safe to run as a zero-spend preflight.
func Verify(root string, manifest Manifest, opts VerifyOptions) []Finding {
	var findings []Finding
	if manifest.APIVersion != APIVersion {
		return append(findings, Finding{Kind: FindingSchemaInvalid, Detail: fmt.Sprintf("api version %q", manifest.APIVersion)})
	}
	if strings.TrimSpace(manifest.Instrument) == "" || strings.TrimSpace(manifest.Version) == "" || len(manifest.Entries) == 0 {
		return append(findings, Finding{Kind: FindingSchemaInvalid, Detail: "instrument, version, and at least one entry are required"})
	}
	if strings.TrimSpace(manifest.Provisional) != "" {
		findings = append(findings, Finding{Kind: FindingProvisional, Detail: manifest.Provisional})
	}
	locked := map[string]bool{}
	for _, entry := range manifest.Entries {
		locked[entry.Path] = true
		resolved, err := confine(root, entry.Path)
		if err != nil {
			findings = append(findings, Finding{Kind: FindingPathEscape, Path: entry.Path, Role: entry.Role, Detail: err.Error()})
			continue
		}
		content, err := hashedContent(resolved, entry.Extractor, opts.Extractors)
		if err != nil {
			kind := FindingMissing
			if entry.Extractor != "" && strings.Contains(err.Error(), "not registered") {
				kind = FindingExtractorMissing
			}
			findings = append(findings, Finding{Kind: kind, Path: entry.Path, Role: entry.Role, Detail: err.Error()})
			continue
		}
		observed := digestBytes(content)
		if observed != entry.Digest || int64(len(content)) != entry.SizeBytes {
			findings = append(findings, Finding{
				Kind: FindingDrift, Path: entry.Path, Role: entry.Role,
				Expected: entry.Digest, Observed: observed,
			})
		}
	}
	for _, sealedRoot := range manifest.SealedRoots {
		resolved, err := confine(root, sealedRoot)
		if err != nil {
			findings = append(findings, Finding{Kind: FindingPathEscape, Path: sealedRoot, Detail: err.Error()})
			continue
		}
		walkErr := filepath.WalkDir(resolved, func(path string, d fs.DirEntry, err error) error {
			if err != nil {
				return err
			}
			if d.IsDir() {
				return nil
			}
			relative, err := filepath.Rel(root, path)
			if err != nil {
				return err
			}
			slashRelative := filepath.ToSlash(relative)
			if !locked[slashRelative] {
				findings = append(findings, Finding{Kind: FindingUntracked, Path: slashRelative, Detail: "file inside sealed root is not locked"})
			}
			return nil
		})
		if walkErr != nil {
			findings = append(findings, Finding{Kind: FindingMissing, Path: sealedRoot, Detail: walkErr.Error()})
		}
	}
	findings = append(findings, VerifyDimensions(manifest.Dimensions, opts.Observed)...)
	return findings
}

// VerifyDimensions compares declared expectations against observed runtime
// values. Every declared dimension must match; observed dimensions that were
// never declared are reported as advisory, because an expectation the freeze
// did not think to declare is a coverage gap worth seeing, not a failure.
func VerifyDimensions(declared, observed map[string]string) []Finding {
	var findings []Finding
	names := make([]string, 0, len(declared))
	for name := range declared {
		names = append(names, name)
	}
	sort.Strings(names)
	for _, name := range names {
		value, present := observed[name]
		if !present || value != declared[name] {
			findings = append(findings, Finding{
				Kind: FindingDimensionDrift, Dimension: name,
				Expected: declared[name], Observed: value,
			})
		}
	}
	extras := make([]string, 0)
	for name := range observed {
		if _, present := declared[name]; !present {
			extras = append(extras, name)
		}
	}
	sort.Strings(extras)
	for _, name := range extras {
		findings = append(findings, Finding{
			Kind: FindingUndeclaredDimension, Dimension: name,
			Observed: observed[name], Advisory: true,
			Detail: "observed dimension was never declared by the freeze",
		})
	}
	return findings
}

// Save writes the manifest as canonical indented JSON.
func Save(path string, manifest Manifest) error {
	data, err := json.MarshalIndent(manifest, "", "  ")
	if err != nil {
		return err
	}
	return os.WriteFile(path, append(data, '\n'), 0o644)
}

// Load reads a manifest, rejecting unknown fields so schema drift surfaces at
// the boundary rather than as silently ignored keys.
func Load(path string) (Manifest, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return Manifest{}, err
	}
	decoder := json.NewDecoder(strings.NewReader(string(data)))
	decoder.DisallowUnknownFields()
	var manifest Manifest
	if err := decoder.Decode(&manifest); err != nil {
		return Manifest{}, fmt.Errorf("decode instrument lock: %w", err)
	}
	return manifest, nil
}
