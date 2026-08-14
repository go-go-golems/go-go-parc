// Package instrumentlock freezes a measurement apparatus — data files, prompt
// assets, configuration, and the harness's own source — into a digest manifest,
// verifies the frozen identity before any spend, and derives version-keyed
// population keys so that cached measurement populations from different
// instrument versions can never mix.
//
// The package generalizes three independently evolved implementations:
// CoinVault's validateGECRagoptEnvironment/validateGECRagoptSourceLock,
// rag-ttc's validateI5Environment (which digests five of its own source files
// as locked snapshot dimensions), and Ragopt's byte-versus-semantic policy
// digest split.
//
// # Trust ledger
//
// A passing Verify at time t establishes, assuming SHA-256 collision
// resistance:
//
//   - every locked entry's content (raw bytes, or the named extractor's
//     normalization of them) hashed to the recorded digest when read at t;
//   - every sealed root contained no file outside the locked entry set at t;
//   - every declared dimension equaled the runtime-observed value computed
//     at t;
//   - the manifest itself was schema-valid and not marked provisional.
//
// A passing Verify does NOT establish:
//
//   - that any file remains unchanged after t (the TOCTOU window between
//     preflight and each later read is open unless the run re-reads content
//     from run-owned copies, as Ragopt's input binding does for data — but
//     deliberately not for harness source);
//   - that the running binary was built from the locked source (the
//     worktree/binary skew: digesting knowledge_ragopt.go on disk proves
//     nothing about the compiled code executing the digest check; see
//     BuildBinding for a partial, advisory mitigation);
//   - anything against an adversarial same-principal process (the lock
//     constrains accident and drift, not an attacker who can rewrite both
//     the files and the manifest);
//   - semantic equivalence: two byte-distinct files may behave identically,
//     and the lock will still report drift — the lock is deliberately
//     stricter than behavior.
//
// Verification therefore excludes exactly one class of worlds: those in which
// the apparatus present in the worktree at preflight time differs from the
// apparatus that was frozen. Everything after t is the run's obligation.
package instrumentlock
