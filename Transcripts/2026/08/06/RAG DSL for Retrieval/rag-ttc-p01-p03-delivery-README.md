# rag-ttc P01-P03 delivery

This delivery implements the first three semantic-foundations projects as one coherent kernel and documents the work as a doctoral-style implementation thesis.

## Contents

- `rag-ttc-p01-p03-doctoral-thesis.pdf` - rendered thesis.
- `rag-ttc-p01-p03-doctoral-thesis.md` - editable thesis source.
- `rag-ttc-p01-p03-thesis-assets/` - diagrams and the scaling chart used by the thesis.
- `rag-ttc-p01-p03-implementation.zip` - complete patched `rag-ttc` source snapshot.
- `rag-ttc-p01-p03.patch` - unified patch against the supplied source snapshot; verified with `patch -p1`.
- `rag-ttc-p01-p03-reproducibility.zip` - standalone handoff package with fixtures, reports, checksums, and a network-free demonstration script.
- `validation/` - PDF preflight, test logs, static parse result, evaluation, and scaling measurements.

## Implemented foundations

### P01 - Semantic identity and cache fingerprints

- Typed canonical values with explicit scalar, list, set, object, optional, byte, and portable-path semantics.
- Domain- and version-separated SHA-256 fingerprints.
- Explicit semantic, lineage, observation, presentation, operational, and secret field roles.
- Mutation-contract tests that require behavior-affecting fields to change identity while excluded fields do not.
- Cache-key patches for resolved provider configuration and connected-retrieval RRF configuration.

### P02 - Canonical facts and provenance

- Separate `Fact`, `Derivation`, and `Observation` records.
- Canonical JSON and stable record identities.
- Multiple independent derivations for one fact.
- Verification of IDs, conflicts, dependencies, observations, and least finite proof ranks.
- Extractable, independently verifiable proof bundles.
- Adapters for existing RAG chunks, evidence, representations, and knowledge facts.

### P03 - Lawful merge and deterministic evidence ledger

- State join defined as union over complete record variants.
- Associative, commutative, and idempotent merge.
- Explicit retention and reporting of same-ID/different-content conflicts.
- Mutex-protected mutable ledger preserving the same extensional semantics.
- Deterministic post-merge selection, budgets, one-per-fact policy, and citation labels.
- Exhaustive delivery-order and candidate-order experiments plus concurrent retry tests.

## Validation status

The standalone semantic kernel was compiled, race-tested, and vetted with the available Go 1.23.2 toolchain in GOPATH mode. The conformance command evaluated all 720 permutations of six merge deltas, all six candidate completion orders, conflict retention, proof verification, tamper detection, and 100 concurrent retry runs. Every Go source file in the patched tree was parsed and found `gofmt` clean.

The complete repository suite was not executed. The supplied module declares Go 1.26.5 and contains a `tool` block that the available Go 1.23.2 parser does not understand; network access was unavailable for acquiring the declared toolchain. Production-package changes outside the standalone kernel are therefore statically reviewed and patched, but remain integration candidates until the repository is tested under its declared toolchain.

## Reproduction

From the patched repository:

```bash
./research/p01-p03-foundations/demo.sh
```

The script requires no external model, database, network access, or third-party Go module for the core experiment.
