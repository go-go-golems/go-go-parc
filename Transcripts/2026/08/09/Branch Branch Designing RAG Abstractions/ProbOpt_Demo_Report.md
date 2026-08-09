# ProbOpt sandbox demonstration

Root seed: `20260809`; paired repeats: `5`; cases: `10`.

## Exact finite-category law certificate

| Law | Result |
|---|---|
| left_identity | true |
| right_identity | true |
| associativity | true |
| discard_naturality | true |
| deterministic_copy_naturality | true |
| copy_commutativity | true |

## Candidate evidence

| Candidate | Decision | Recall | MRR | Precision | Latency ms | Index units | Pareto |
|---|---:|---:|---:|---:|---:|---:|---:|
| bounded-rerank (`cand_bfa606671c584`) | eligible | 0.900 | 0.850 | 0.333 | 1.013 | 688 | true |
| expensive-wide (`cand_796d601e2e8b4`) | rejected | 0.900 | 0.850 | 0.333 | 1.551 | 1768 | false |
| lexical-heavy (`cand_806a534ec0c30`) | eligible | 0.900 | 0.783 | 0.333 | 0.579 | 631 | true |
| smaller-overlap (`cand_5183e8a85e77c`) | eligible | 0.900 | 0.800 | 0.333 | 0.739 | 922 | true |
| title-hybrid (`cand_f268cec6dedbe`) | undecided | 0.900 | 0.750 | 0.333 | 0.586 | 688 | false |

## Selected incumbent

`cand_bfa606671c5841a54dc2bcee37fd576c62f87fc92fcf94dddd0cbea3e6010657` - **bounded-rerank**

## Gate details

### bounded-rerank

- `constraint:authorized`: passed=true, hard=true - seen=50 passed=50 failed=0
- `constraint:finite_scores`: passed=true, hard=true - seen=50 passed=50 failed=0
- `noninferior:recall`: passed=true, hard=true - beneficial_mean_delta=0.000000 margin=0.000000 n=50
- `noninferior:mrr`: passed=true, hard=true - beneficial_mean_delta=0.100000 margin=0.030000 n=50
- `budget:latency_ms`: passed=true, hard=true - mean=1.013062 maximum=1.300000
- `budget:index_units`: passed=true, hard=true - mean=688.000000 maximum=1200.000000
- `improve:mrr`: passed=true, hard=false - beneficial_mean_delta=0.100000 minimum=0.005000 n=50

### expensive-wide

- `constraint:authorized`: passed=true, hard=true - seen=50 passed=50 failed=0
- `constraint:finite_scores`: passed=true, hard=true - seen=50 passed=50 failed=0
- `noninferior:recall`: passed=true, hard=true - beneficial_mean_delta=0.000000 margin=0.000000 n=50
- `noninferior:mrr`: passed=true, hard=true - beneficial_mean_delta=0.100000 margin=0.030000 n=50
- `budget:latency_ms`: passed=false, hard=true - mean=1.551226 maximum=1.300000

### lexical-heavy

- `constraint:authorized`: passed=true, hard=true - seen=50 passed=50 failed=0
- `constraint:finite_scores`: passed=true, hard=true - seen=50 passed=50 failed=0
- `noninferior:recall`: passed=true, hard=true - beneficial_mean_delta=0.000000 margin=0.000000 n=50
- `noninferior:mrr`: passed=true, hard=true - beneficial_mean_delta=0.033333 margin=0.030000 n=50
- `budget:latency_ms`: passed=true, hard=true - mean=0.578568 maximum=1.300000
- `budget:index_units`: passed=true, hard=true - mean=631.000000 maximum=1200.000000
- `improve:mrr`: passed=true, hard=false - beneficial_mean_delta=0.033333 minimum=0.005000 n=50

### smaller-overlap

- `constraint:authorized`: passed=true, hard=true - seen=50 passed=50 failed=0
- `constraint:finite_scores`: passed=true, hard=true - seen=50 passed=50 failed=0
- `noninferior:recall`: passed=true, hard=true - beneficial_mean_delta=0.000000 margin=0.000000 n=50
- `noninferior:mrr`: passed=true, hard=true - beneficial_mean_delta=0.050000 margin=0.030000 n=50
- `budget:latency_ms`: passed=true, hard=true - mean=0.738595 maximum=1.300000
- `budget:index_units`: passed=true, hard=true - mean=922.000000 maximum=1200.000000
- `improve:mrr`: passed=true, hard=false - beneficial_mean_delta=0.050000 minimum=0.005000 n=50

### title-hybrid

- `constraint:authorized`: passed=true, hard=true - seen=50 passed=50 failed=0
- `constraint:finite_scores`: passed=true, hard=true - seen=50 passed=50 failed=0
- `noninferior:recall`: passed=true, hard=true - beneficial_mean_delta=0.000000 margin=0.000000 n=50
- `noninferior:mrr`: passed=true, hard=true - beneficial_mean_delta=0.000000 margin=0.030000 n=50
- `budget:latency_ms`: passed=true, hard=true - mean=0.585839 maximum=1.300000
- `budget:index_units`: passed=true, hard=true - mean=688.000000 maximum=1200.000000
- `improve:mrr`: passed=false, hard=false - beneficial_mean_delta=0.000000 minimum=0.005000 n=50

