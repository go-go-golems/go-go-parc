package instrumentlock

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"runtime/debug"
	"strings"
)

// PopulationKey identifies one cached measurement inside one measurement
// population. It generalizes CoinVault's judge cache key, where
// execution.NewKey(step, judgePromptVersion, {model, prompt}) makes a prompt
// version bump invalidate the entire judged population.
//
// The invariant: two keys with different InstrumentVersion values render to
// different key strings for every payload, so populations produced by
// different instrument versions are disjoint by construction — no cache
// flush, no epoch bookkeeping, no possibility of forgetting.
type PopulationKey struct {
	Step              string `json:"step"`
	InstrumentVersion string `json:"instrument_version"`
	Model             string `json:"model"`
	PayloadDigest     string `json:"payload_digest"`
}

// NewPopulationKey canonicalizes the payload with encoding/json (map keys are
// sorted; struct fields keep declaration order, so payload types must be
// stable) and binds it to the step, instrument version, and model identity.
func NewPopulationKey(step, instrumentVersion, model string, payload any) (PopulationKey, error) {
	if strings.TrimSpace(step) == "" || strings.TrimSpace(instrumentVersion) == "" {
		return PopulationKey{}, fmt.Errorf("population key step and instrument version are required")
	}
	encoded, err := json.Marshal(payload)
	if err != nil {
		return PopulationKey{}, fmt.Errorf("canonicalize population payload: %w", err)
	}
	sum := sha256.Sum256(encoded)
	return PopulationKey{
		Step:              step,
		InstrumentVersion: instrumentVersion,
		Model:             model,
		PayloadDigest:     "sha256:" + hex.EncodeToString(sum[:]),
	}, nil
}

// Key renders the canonical cache key. All four coordinates participate, so
// equality of keys implies equality of (step, version, model, payload digest)
// up to hash collision.
func (k PopulationKey) Key() string {
	encoded, _ := json.Marshal(k)
	sum := sha256.Sum256(encoded)
	return "sha256:" + hex.EncodeToString(sum[:])
}

// BuildBinding reports the VCS revision and dirty flag compiled into the
// running binary, when the toolchain stamped them. It exists because a
// source lock digests the worktree, not the binary: a binary built before an
// edit, run in a worktree reverted after that edit, passes every file digest
// while executing code the lock never saw. Comparing the stamped revision
// against the lock's recorded base commit narrows (but does not close) that
// gap: it detects checkout drift, not uncommitted-at-build-time skew, because
// vcs.modified only records whether the build worktree was dirty.
type BuildBinding struct {
	Revision string
	Modified bool
	Stamped  bool
}

// ReadBuildBinding inspects the running binary's build info.
func ReadBuildBinding() BuildBinding {
	info, ok := debug.ReadBuildInfo()
	if !ok {
		return BuildBinding{}
	}
	binding := BuildBinding{}
	for _, setting := range info.Settings {
		switch setting.Key {
		case "vcs.revision":
			binding.Revision = setting.Value
			binding.Stamped = true
		case "vcs.modified":
			binding.Modified = setting.Value == "true"
		}
	}
	return binding
}

// VerifyBuildRevision compares the stamped binary revision against an
// expected base commit. An unstamped binary (tests, go run) yields an
// advisory finding: absence of evidence is reported as absence, never as a
// pass that claims more than it checked.
func VerifyBuildRevision(expected string) []Finding {
	binding := ReadBuildBinding()
	if !binding.Stamped {
		return []Finding{{
			Kind: FindingDimensionDrift, Dimension: "build.vcs.revision",
			Expected: expected, Observed: "", Advisory: true,
			Detail: "binary carries no VCS stamp; build binding cannot be checked",
		}}
	}
	var findings []Finding
	if !strings.HasPrefix(binding.Revision, expected) && !strings.HasPrefix(expected, binding.Revision) {
		findings = append(findings, Finding{
			Kind: FindingDimensionDrift, Dimension: "build.vcs.revision",
			Expected: expected, Observed: binding.Revision,
		})
	}
	if binding.Modified {
		findings = append(findings, Finding{
			Kind: FindingDimensionDrift, Dimension: "build.vcs.modified",
			Expected: "false", Observed: "true", Advisory: true,
			Detail: "binary was built from a dirty worktree; file digests cannot bind it",
		})
	}
	return findings
}
