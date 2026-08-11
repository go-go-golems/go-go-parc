# Sources for Sessionstream event and observation foundations

This directory preserves the primary papers and specification snapshots used by
`02 - Typed Transition Systems and Trace Algebra.md`. The files were retrieved on
2026-08-11. `SHA256SUMS` records the exact archived bytes.

The archive distinguishes mathematical models from production recommendations. A
paper can clarify ordering, traces, queues, or composition without implying that
Sessionstream should implement the paper's complete model.

## Source inventory

| File | Original source | Why it is retained |
|---|---|---|
| `01-lamport-time-clocks-ordering.pdf` | Leslie Lamport, “Time, Clocks, and the Ordering of Events in a Distributed System,” CACM 21(7), 1978. <https://lamport.azurewebsites.net/pubs/time-clocks.pdf> | Defines happened-before as a partial order and distinguishes causal order from arbitrary total order. This is the basis for treating Sessionstream session ordinals, connection order, and dispatcher admission order as different relations. |
| `02-herlihy-wing-linearizability.pdf` | Maurice Herlihy and Jeannette Wing, “Linearizability: A Correctness Condition for Concurrent Objects,” TOPLAS 12(3), 1990. <https://cs.brown.edu/people/mph/HerlihyW90/p463-herlihy.pdf> | Supplies the correctness criterion for concurrent `TrySubmit` and `Close`: each operation must appear to take effect at one point between invocation and response. |
| `03-kahn-semantics-parallel-programming.pdf` | Gilles Kahn, “The Semantics of a Simple Language for Parallel Programming,” IFIP Congress, 1974. <https://perso.ensta-paris.fr/~chapoutot/various/kahn_networks.pdf> | Provides the stream-history view of communicating processes and clarifies why deterministic blocking process networks differ from Sessionstream's finite, lossy diagnostic dispatcher. |
| `04-hutton-universality-expressiveness-fold.pdf` | Graham Hutton, “A Tutorial on the Universality and Expressiveness of Fold,” JFP 9(4), 1999. <https://people.cs.nott.ac.uk/pszgmh/fold.pdf> | Grounds projections, replay, checks, and trace summaries as folds over finite event sequences. |
| `05-eugster-many-faces-publish-subscribe.pdf` | Patrick Eugster, Pascal Felber, Rachid Guerraoui, and Anne-Marie Kermarrec, “The Many Faces of Publish/Subscribe,” ACM Computing Surveys 35(2), 2003. <https://systems.cs.columbia.edu/ds2-class/papers/eugster-pubsub.pdf> | Separates time, space, and synchronization decoupling and prevents conflating observer callbacks with durable publish/subscribe infrastructure. |
| `06-chandra-toueg-unreliable-failure-detectors.pdf` | Tushar Chandra and Sam Toueg, “Unreliable Failure Detectors for Reliable Distributed Systems,” JACM 43(2), 1996. <https://courses.csail.mit.edu/6.852/08/papers/CT96-JACM.pdf> | Supports the heartbeat interpretation as suspicion under assumptions, not proof of failure, and keeps timeout observations separate from authoritative state transitions. |
| `07-lynch-tuttle-io-automata.pdf` | Nancy Lynch and Mark Tuttle, “Hierarchical Correctness Proofs for Distributed Algorithms,” PODC, 1987. <https://groups.csail.mit.edu/tds/papers/Lynch/podc87-tuttle.pdf> | Provides the input/output automaton and refinement perspective used to separate domain, pipeline, transport, and diagnostic planes. |
| `08-reactive-streams-jvm-specification.md` | Reactive Streams JVM specification README, archived at repository commit `a625d3aba756e9842ad1291a5b73f5db280b6168`. <https://github.com/reactive-streams/reactive-streams-jvm> | Defines demand-driven nonblocking backpressure and serial signal rules. It is retained mainly as a contrast: dropping on overflow is not Reactive Streams backpressure. |
| `09-opentelemetry-specification-overview.md` | OpenTelemetry specification overview. <https://opentelemetry.io/docs/specs/otel/overview/> | Shows an established separation between instrumentation API, SDK policy, semantic conventions, exporters, context propagation, traces, metrics, and logs. |
| `10-opentelemetry-signals.md` | OpenTelemetry signals overview. <https://opentelemetry.io/docs/concepts/signals/> | Provides the signal taxonomy used when evaluating whether custom Sessionstream observers should instead become spans, span events, logs, or metrics. |
| `11-cloudevents-specification.md` | CloudEvents specification, archived at repository commit `c2845a49bc9831be02f305a4a792401b932d77d4`. <https://github.com/cloudevents/spec> | Distinguishes an occurrence from its event representation and separates event context from event data. It informs envelope design but does not justify one universal in-process record. |
| `12-fowler-event-sourcing.md` | Martin Fowler, “Event Sourcing.” <https://martinfowler.com/eaaDev/EventSourcing.html> | Describes state reconstruction from an ordered event log and the distinction between current application state and authoritative event history. |
| `13-mit-queueing-models.pdf` | Cathy Wu, “Queuing Models: Stochastic Throughput,” MIT 1.041/1.200, Spring 2023. <https://web.mit.edu/1.041/spring2023/lectures/L8-queuing-models-2023sp.pdf> | Supplies queue-capacity, throughput, stationary-analysis, and Little's-law foundations for sizing and measuring a bounded diagnostic dispatcher. |

## Retrieval methods

- Primary PDFs and raw GitHub specifications were downloaded directly with `curl -fL`.
- OpenTelemetry and Fowler pages were converted to Markdown with `defuddle parse <url> --md`.
- Archived Markdown was normalized to LF line endings and trailing whitespace was removed for stable vault rendering and Git validation.
- The Reactive Streams and CloudEvents source revisions were recorded with `git ls-remote`.
- `pdftotext -layout` was used during research, but generated text copies are not retained because the original PDFs and this index are sufficient.

## Integrity check

From this directory:

```bash
sha256sum --check SHA256SUMS
```

## Scope and rights

These local copies are research references. Copyright and redistribution rights remain with their respective authors and publishers. Follow the original source's terms before redistributing this directory outside the private vault.
