// Package suitegov enforces ground-truth governance and split hygiene as
// structural properties rather than conventions.
//
// The package unifies three mechanisms observed separately in CoinVault,
// rag-ttc, and Ragopt:
//
//   - suite identity as an explicit projection (semantic digest distinct from
//     byte digest, case order participating because it controls execution);
//   - an append-only, hash-chained proposal ledger whose Commit requires a
//     reviewer identity distinct from every proposal author and mints a new
//     digest-named immutable evaluation set;
//   - structurally closed splits, where held-out data is replaced by a typed
//     sentinel and no loadable suite can be constructed without an explicit
//     Open transition carrying promotion evidence;
//   - a run-side lock verifier suitable for embedding in an experiment
//     preflight, binding the suite a run measures to a reviewed identity.
//
// Everything is standard library only. Product adapters own YAML parsing,
// principal authentication, and storage beyond the local filesystem.
package suitegov

import (
	"bytes"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"regexp"
	"sort"
)

// SuiteSchemaVersion identifies the suite document contract.
const SuiteSchemaVersion = "suitegov-suite/v1"

// SemanticDigest identifies the normalized meaning of a suite: schema version,
// name, ordered cases with canonical inputs and sorted groups. Two files with
// different bytes but equal normalized content share a SemanticDigest.
type SemanticDigest string

// ByteDigest identifies exact file bytes. It binds execution artifacts;
// SemanticDigest binds meaning. The distinction follows Ragopt's policy
// digests (exact bytes versus parsed semantics).
type ByteDigest string

// Identity names a principal (author, reviewer, approver). The package treats
// identities as opaque non-empty strings; authentication is the caller's job.
type Identity string

var identifierPattern = regexp.MustCompile(`^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$`)

// Case is one evaluation case. Input is opaque JSON: the package never
// interprets product semantics, mirroring Ragopt's suite contract.
type Case struct {
	ID     string          `json:"id"`
	Groups []string        `json:"groups,omitempty"`
	Input  json.RawMessage `json:"input"`
}

// Suite is an ordered list of cases. Order is semantic: it participates in
// the digest because it controls execution schedules downstream.
type Suite struct {
	SchemaVersion string `json:"schema_version"`
	Name          string `json:"name"`
	Cases         []Case `json:"cases"`
}

// SuiteDocument pairs a normalized suite with its two identities and origin.
type SuiteDocument struct {
	Suite          Suite
	SemanticDigest SemanticDigest
	ByteDigest     ByteDigest
	SourcePath     string
}

// LoadSuite strictly loads, normalizes, and identifies one suite file.
func LoadSuite(path string) (*SuiteDocument, error) {
	absolute, err := filepath.Abs(path)
	if err != nil {
		return nil, fmt.Errorf("resolve suite path: %w", err)
	}
	data, err := os.ReadFile(absolute)
	if err != nil {
		return nil, fmt.Errorf("read suite: %w", err)
	}
	document, err := LoadSuiteBytes(data)
	if err != nil {
		return nil, err
	}
	document.SourcePath = absolute
	return document, nil
}

// LoadSuiteBytes strictly decodes and identifies suite bytes.
func LoadSuiteBytes(data []byte) (*SuiteDocument, error) {
	var suite Suite
	if err := decodeStrictJSON(data, &suite); err != nil {
		return nil, fmt.Errorf("decode suite: %w", err)
	}
	if err := normalizeSuite(&suite); err != nil {
		return nil, err
	}
	semantic, err := IdentifySuite(suite)
	if err != nil {
		return nil, err
	}
	return &SuiteDocument{
		Suite:          suite,
		SemanticDigest: semantic,
		ByteDigest:     digestBytes(data),
	}, nil
}

// IdentifySuite computes the semantic digest of an already-normalized suite.
// The projection is exactly: schema version, name, and the ordered case list
// with canonical inputs and sorted groups, JSON-marshaled.
func IdentifySuite(suite Suite) (SemanticDigest, error) {
	data, err := json.Marshal(suite)
	if err != nil {
		return "", fmt.Errorf("marshal suite identity: %w", err)
	}
	return SemanticDigest(digestBytes(data)), nil
}

func normalizeSuite(suite *Suite) error {
	if suite == nil {
		return errors.New("suite is nil")
	}
	if suite.SchemaVersion != SuiteSchemaVersion {
		return fmt.Errorf("unsupported suite schema version %q", suite.SchemaVersion)
	}
	if !identifierPattern.MatchString(suite.Name) {
		return fmt.Errorf("invalid suite name %q", suite.Name)
	}
	if len(suite.Cases) == 0 {
		return errors.New("suite requires at least one case")
	}
	seen := make(map[string]struct{}, len(suite.Cases))
	for index := range suite.Cases {
		value := &suite.Cases[index]
		if err := normalizeCase(value); err != nil {
			return fmt.Errorf("case %d: %w", index, err)
		}
		if _, duplicate := seen[value.ID]; duplicate {
			return fmt.Errorf("duplicate case ID %q", value.ID)
		}
		seen[value.ID] = struct{}{}
	}
	return nil
}

func normalizeCase(value *Case) error {
	if value == nil {
		return errors.New("case is nil")
	}
	if !identifierPattern.MatchString(value.ID) {
		return fmt.Errorf("invalid case ID %q", value.ID)
	}
	if len(value.Input) == 0 || !json.Valid(value.Input) {
		return fmt.Errorf("case %q input is not valid JSON", value.ID)
	}
	canonical, err := canonicalRawJSON(value.Input)
	if err != nil {
		return fmt.Errorf("canonicalize case %q input: %w", value.ID, err)
	}
	value.Input = canonical
	groups := make(map[string]struct{}, len(value.Groups))
	for _, group := range value.Groups {
		if !identifierPattern.MatchString(group) {
			return fmt.Errorf("case %q has invalid group %q", value.ID, group)
		}
		if _, duplicate := groups[group]; duplicate {
			return fmt.Errorf("case %q has duplicate group %q", value.ID, group)
		}
		groups[group] = struct{}{}
	}
	sort.Strings(value.Groups)
	return nil
}

func canonicalRawJSON(raw []byte) (json.RawMessage, error) {
	decoder := json.NewDecoder(bytes.NewReader(raw))
	decoder.UseNumber()
	var value any
	if err := decoder.Decode(&value); err != nil {
		return nil, fmt.Errorf("decode JSON value: %w", err)
	}
	var extra any
	if err := decoder.Decode(&extra); !errors.Is(err, io.EOF) {
		if err == nil {
			return nil, errors.New("JSON contains multiple values")
		}
		return nil, fmt.Errorf("check JSON trailing data: %w", err)
	}
	data, err := json.Marshal(value)
	if err != nil {
		return nil, fmt.Errorf("marshal canonical JSON value: %w", err)
	}
	return data, nil
}

func decodeStrictJSON(data []byte, destination any) error {
	decoder := json.NewDecoder(bytes.NewReader(data))
	decoder.DisallowUnknownFields()
	if err := decoder.Decode(destination); err != nil {
		return err
	}
	var extra any
	if err := decoder.Decode(&extra); !errors.Is(err, io.EOF) {
		if err == nil {
			return errors.New("JSON contains multiple values")
		}
		return err
	}
	return nil
}

func digestBytes(data []byte) ByteDigest {
	sum := sha256.Sum256(data)
	return ByteDigest("sha256:" + hex.EncodeToString(sum[:]))
}
