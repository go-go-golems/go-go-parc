# Local camera execution evidence

**Acceptance: INCONCLUSIVE.** Exporting this report does not qualify the generator or backend.

- Run: `run\_3770618611ef8c2403925976`
- Execution state: completed
- Scenario: source-faults
- Scenario hash: `sha256:059ac7126af96c0e93dbce12fa04724e52a4024fd929e43908d2274558f6a92a`
- Target: local-test
- Started UTC us: 1788926875438283
- Ended UTC us: 1788926887447474
- Durable elapsed seconds: 12.009264
- Generator health: unknown

## Process-epoch observations

These are local observations, not receiver-delivered counts. `Published` means written into a stream with readers. Dropped AU counts also include units whose packets were all suppressed. Non-final samples are prefixes, not full-epoch totals.

| Camera | PID | Final | Profile | First frame | Scheduled end | Published | No reader | Skipped | Paused AU | Dropped AU | Dropped RTP | Dropped RTCP |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| cam\_01 | 1611449 | true | main | 0 | 181 | 124 | 57 | 0 | 0 | 0 | 0 | 0 |
| cam\_01 | 1611449 | true | sub | 0 | 121 | 0 | 91 | 0 | 10 | 20 | 12 | 2 |

Frame indexes are run-global. `Skipped` includes pre-epoch slots; the epoch start is provided to distinguish them. Do not sum overlapping epochs blindly.

## Missing evidence and limitations

- Local source observations only; no receiver or backend delivery measurement.
- No complete CPU/RSS/queue/network saturation or generator-health qualification.
- Backend, real-model and browser environment are unverified.
- Epoch counters can overlap; they are not blindly summed into whole-run totals.
- This local evidence document is not a canonical RunReport or acceptance verdict.

## Bundle

- [Machine-readable evidence](evidence.json)
- [Normalized scenario](scenario.json)
- [SHA-256 artifact manifest](artifact-manifest.json)
