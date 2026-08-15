# Sources — Sentinel-Delimited Command Completion

Reference material saved locally so the theory behind the `01 - Sentinel-
Delimited Command Completion over an Ordered Line Queue` design entry can be
studied without re-searching. Each entry maps to the concept it grounds.

The design entry lives at `../designs/01 - Sentinel-Delimited Command
Completion over an Ordered Line Queue.md`.

## Foundational papers (PDF, freely available)

| # | File | What it grounds in the design entry |
|---|---|---|
| 01 | `01-lamport-1978-time-clocks-ordering-events.pdf` | **Happens-before / FIFO channels.** The line queue is a FIFO channel = a total order under Lamport's `→`; the correlation-by-position axiom. CACM 21(7):558–565, 1978. DOI 10.1145/359545.359563. |
| 02 | `02-alpern-schneider-1985-defining-liveness.pdf` | **Safety vs. liveness.** A constant-sentinel desync is a *safety* violation (point at the moment it broke), not a liveness/timeout problem — which is why the fix is quarantine, not a longer timeout. Information Processing Letters 21(4), 1985. |
| 03 | `03-fischer-lynch-paterson-1985-flp-impossibility.pdf` | **FLP / timeout-as-signal.** You cannot detect a crashed peer purely by message passing; a timeout is a wall-clock bound, not a proof — so quarantine-on-timeout is the safe choice. JACM 32(2), 1985. DOI 10.1145/3149.214121. |
| 04 | `04-akkoyunlu-ekanadham-huber-1975-two-generals.pdf` | **Two-generals / delivery semantics.** Exactly-once is impossible over an unreliable channel without idempotency; motion (non-idempotent) gets at-most-once. The original statement of the problem. ACM SOSP 1975. DOI 10.1145/800213.806523. |
| 05 | `05-castagnoli-1993-crc-optimization-24-32-bits.pdf` | **CRC undetected-error theory.** The CRC is a linear code over GF(2); its `2^{-16}` random-error figure is a *detection* rate, not an *authentication* rate — the quantitative form of "CRC ≠ desync bound." IEEE Trans. Communications 41(6), 1993. |

## Reference web pages (markdown / rst, extracted)

| # | File | What it grounds |
|---|---|---|
| 06 | `06-koopman-cmu-crc-best-polynomials.md` | **CRC polynomial selection & the "Polynomial Zoo."** Koopman's CMU CRC pages — the practical reference for CRC undetected-error bounds and polynomial choice. Extracted from `users.ece.cmu.edu/~koopman/crc/`. |
| 07 | `07-wikipedia-mathematics-of-crc.md` | **CRC as polynomial arithmetic over GF(2).** The remainder-after-division framing, why odd-bit errors are detected (`x+1` divides the generator), and burst-error detection bounds. The math behind §6.1 of the MZ1-005 study. |
| 08 | `08-wikipedia-safety-and-liveness-properties.md` | **Safety/liveness definitions.** The topological characterization (every property is the intersection of a safety and a liveness property) and the Alpern–Schneider formal definition. |
| 09 | `09-wikipedia-two-generals-problem.md` | **Two-generals overview & history.** The impossibility of common knowledge over an unreliable channel; why acks cannot terminate. Links back to paper 04. |
| 10 | `10-peterson-davie-systems-approach-framing.rst` | **Framing & sentinel/flag-byte self-synchronization.** Chapter 2.3 of *Computer Networks: A Systems Approach* (Peterson & Davie) — sentinel characters, character stuffing, HDLC `0x7E`, bit stuffing, COBS. The textbook treatment of the framing family this pattern belongs to. Free online: book.systemsapproach.org. |
| 11 | `11-peterson-davie-systems-approach-error-detection.rst` | **Error detection & CRC.** Chapter 2.4 of the same book — CRC derivation, undetected errors, why CRC-32 catches the "overwhelming majority." Pairs with papers 05 and sources 06/07. |

## Textbooks (commercial — cited, not downloaded)

These are the standard textbook references for the broader theory; they are
not free, so they are listed here as citations rather than saved files.

- **Tanenbaum & Wetherall**, *Computer Networks*, 5th ed. (Pearson, 2010,
  ISBN 978-0132126953). Chapters on the data link layer (framing, error
  detection, HDLC). The canonical networking textbook.
- **Coulouris, Dollimore, Kindberg & Blair**, *Distributed Systems: Concepts
  and Design*, 5th ed. (Pearson, 2011, ISBN 978-0132143011). Chapters on
  time, coordination, and consistency — happens-before, physical/logical
  clocks, two-generals, failure models.
- **Kurose & Ross**, *Computer Networking: A Top-Down Approach*, 7th ed.
  (Pearson, 2017, ISBN 978-0133587937). Chapter on reliable data transfer —
  the FSM-driven sender/receiver with sequence numbers and ACKs, the
  textbook form of "correlation by value."
- **Peterson, Davie & Bavier**, *Computer Networks: A Systems Approach*, 6th
  ed. (Morgan Kaufmann, 2021). The free online edition at
  https://book.systemsapproach.org/ — sources 10 and 11 are its framing and
  error-detection chapters.

## How these map to the design entry's sections

| Design entry section | Primary sources |
|---|---|
| Mathematical/CS foundations — FIFO / happens-before | 01, 08 |
| — safety vs. liveness (quarantine, not longer timeout) | 02, 08 |
| — two-generals / at-most-once delivery | 04, 09 |
| — FLP / timeout-as-signal | 03 |
| — CRC / error detection vs. authentication | 05, 06, 07, 11 |
| — sentinel / flag-byte framing self-synchronization | 10 |
| Design-pattern vocabulary — in-band sentinel signaling | 10, 11 |
| Textbook depth (cited only) | Tanenbaum, Coulouris, Kurose & Ross, Peterson & Davie |
