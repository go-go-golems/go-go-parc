---
title: "Gemma 4 12B: Job-Sheet Inference Throughput"
aliases:
  - Gemma Job Sheet Benchmark
  - Mimimi Ollama Throughput Study
tags:
  - article
  - llm
  - ollama
  - inference
  - benchmarking
  - upwork
status: active
type: article
created: 2026-07-15
repo: /home/manuel/code/wesen/claw-stuff
---

# Gemma 4 12B: Job-Sheet Inference Throughput

This report measures how `gemma4:12b` on the Mimimi Mac turns real Upwork job descriptions into factual, structured job sheets. The objective is not to estimate an abstract model benchmark. It is to decide how a production job-sheet pipeline should package independent descriptions, what metrics actually explain latency, and how to preserve a parseable output contract.

> [!summary]
> - Gemma’s output evaluation rate was stable at **26.1–27.0 tokens/s** across descriptions from 55 to 7,547 characters.
> - Input evaluation was much faster—**223–289 tokens/s**—but output generation and time-to-first-token dominate end-to-end latency.
> - A single structured batch produced a valid JSON array for both 4-job and 8-job tests. Four concurrent independent single-job requests were slower than serial execution on this model host.
> - Follow-up turns retained unrelated prior job context and increased prompt tokens from 120 to 3,118 over four turns. The context window permits that accumulation; it does not make it efficient.

## Why this report exists

A job decision sheet has a strict factual contract. It needs a one-line project description, quoted requirements, a longer summary, quoted deliverables/scope language, and captured market metadata. The narrative portion is appropriate for an LLM because it requires reading a description and selecting evidence. The outer pipeline is not appropriate for an LLM: it must select records, preserve source facts, validate job IDs, parse structured output, render Markdown, and upload the finished packet.

The first implementation used one local LLM request per job. That approach is easy to understand, but it does not answer the operational question: should independent descriptions be processed serially, in parallel, in a batch, or as successive turns in one conversation? The experiments below answer that question with a real model, real descriptions, and the native Ollama timing counters.

## Experimental system

```mermaid
flowchart LR
  DB[(upwork.db)] -->|recent job descriptions| Selector[cohort selector]
  Selector --> Prompt[structured factual prompt]
  Prompt -->|HTTP /api/chat| Tunnel[SSH tunnel\n127.0.0.1:11435]
  Tunnel --> Mimimi[Ollama on Mimimi\ngemma4:12b]
  Mimimi --> Stream[NDJSON stream + final counters]
  Stream --> Validate[JSON contract validation]
  Validate --> Render[Markdown / PDF job packet]

  style DB fill:#f4f0e6,stroke:#26231f
  style Mimimi fill:#dce7ed,stroke:#26231f
  style Validate fill:#e1eadf,stroke:#26231f
```

The model is hosted on Mimimi and accessed only through an SSH local-port-forwarding tunnel. The local client uses `http://127.0.0.1:11435`; the remote Ollama server remains bound to loopback. The benchmark scripts are in the tracker repository:

```text
/home/manuel/code/wesen/claw-stuff/scripts/benchmark_ollama_job_sheets.py
/home/manuel/code/wesen/claw-stuff/scripts/benchmark_ollama_job_sheet_strategies.py
```

The source data is the current 24-hour Upwork cohort in:

```text
/home/manuel/code/wesen/claw-stuff/upwork/upwork.db
```

## The measurements: input tokens, output tokens, and first output

The phrase “tokens per second” is incomplete unless it names the token class and denominator. Ollama returns separate counters and durations for prompt evaluation and output evaluation. This report uses the following definitions.

| Metric | Formula | What it measures |
|---|---|---|
| Input tokens | `prompt_eval_count` | Tokens evaluated from the request prompt, including instructions and job description. |
| Output tokens | `eval_count` | Tokens generated for the model response. |
| Input TPS | `prompt_eval_count / prompt_eval_duration` | Model prompt-processing rate. |
| Output TPS | `eval_count / eval_duration` | Model generation rate after generation begins. |
| Model-total TPS | `(input + output tokens) / total_duration` | Ollama-reported aggregate model throughput. |
| Wall-total TPS | `(input + output tokens) / client wall time` | End-to-end client throughput, including load/scheduling/transport effects. |
| TTFT | client start → first non-empty streamed content | Time to first output visible to the client. |

TTFT must not be confused with prompt-evaluation duration. Prompt evaluation is one component of TTFT. Model loading, request scheduling, server work, and transport also occur before the client sees the first non-empty content chunk.

The earlier dashboard treated chunk arrival intervals as “streaming TPS.” That was misleading. Ollama can buffer output before emitting NDJSON chunks, so chunk arrival timing is not a direct token-generation counter. `eval_count / eval_duration` is the correct output-TPS measurement for this experiment.

## Streaming single-job experiment

Five job descriptions were processed sequentially with `stream: true`. The prompt asked for a factual job-sheet extraction and prohibited fit analysis or application recommendations.

![[assets/gemma4-12b-token-benchmark-2026-07-15.png]]

Browser-rendered capture of the same scientific plot:

![[assets/gemma4-12b-token-benchmark-browser-screenshot-2026-07-15.png]]

| Description size | Input tokens | Output tokens | Input TPS | Output TPS | Wall-total TPS | TTFT | Wall time |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 55 chars | 95 | 529 | 223.5 | 27.0 | 24.1 | 22.0 s | 25.8 s |
| 690 chars | 236 | 877 | 256.4 | 26.7 | 32.6 | 26.3 s | 34.2 s |
| 1,468 chars | 379 | 781 | 278.3 | 26.6 | 37.3 | 22.2 s | 31.1 s |
| 2,350 chars | 619 | 1,002 | 277.0 | 26.3 | 39.7 | 28.4 s | 40.8 s |
| 7,547 chars | 1,597 | 1,031 | 288.8 | 26.1 | 57.8 | 30.1 s | 45.5 s |

The output rate varies by less than one token/s across the sample. This is the stable part of the system. The user-visible wait is dominated by the time before output begins and by the number of generated tokens, not by a sudden collapse in output TPS as the description becomes longer.

The 55-character description is a useful edge case. Its text was exactly: “we are looking for someone to help us with our project.” It still induced 529 output tokens because the prompt required multiple structured sections. A small input is not necessarily a small request when the required response format is substantial.

## Request packaging experiment

The next experiment used four representative jobs: a 55-character sparse description, a 986-character hardware description, a 1,872-character PCB description, and a 7,547-character backend description. Every response was required to be parseable JSON with `job_id`, `one_line`, `summary`, and `deliverables` fields.

![[assets/gemma4-12b-strategy-throughput-2026-07-15.png]]

| Strategy | Jobs | Wall time | Parse result | Interpretation |
|---|---:|---:|---|---|
| Fresh requests, serial | 4 | 176.3 s | 4/4 objects | Baseline: no resource contention, but repeated request setup. |
| Fresh requests, four concurrent | 4 | 234.5 s | 4/4 objects | Correct output, worse wall time. Independent workers contended for the same model host. |
| One structured batch | 4 | 107.2 s | 4/4 array entries | Better: one prompt setup, one generation sequence, one parse operation. |
| One structured batch | 8 | 90.3 s | 8/8 array entries | Confirms that a larger bounded batch can remain parseable. This sample had shorter total input, so it is not a direct speed comparison with the four-job sample. |

The important result is not “eight is always optimal.” The result is that a bounded multi-job prompt is a valid output protocol. The model can return a JSON array with one attributable object per job. That makes batching available as an engineering tool.

## Fresh requests, parallelism, and context growth

Four concurrent independent requests did not improve wall-clock throughput in this environment. The individual calls became slower because they competed for the same loaded model. Parallelism at the HTTP client does not guarantee parallel model evaluation.

The follow-up-turn experiment shows a different failure mode. It sent one job, retained the assistant’s prior response, then added the next job as a new user turn.

![[assets/gemma4-12b-followup-context-2026-07-15.png]]

| Turn | Prompt tokens | Output tokens | Output TPS | Wall time |
|---:|---:|---:|---:|---:|
| 1 | 120 | 794 | 26.5 | 31.0 s |
| 2 | 514 | 1,566 | 25.9 | 62.3 s |
| 3 | 1,253 | 1,516 | 25.7 | 63.9 s |
| 4 | 3,118 | 1,641 | 25.3 | 77.1 s |

The output rate remains approximately constant. The request gets slower because every later call includes earlier job descriptions and earlier model answers. The model’s context window is large enough to hold this conversation, but the retained material has no semantic value for independent job sheets. It only adds input tokens and prompt-processing time.

## The correct pipeline boundary

The system should separate deterministic work from generative work.

```text
1. SQLite selects the cohort and emits canonical job IDs + descriptions.
2. The client groups independent jobs into bounded batches.
3. The LLM receives only the batch instructions and those source descriptions.
4. The client parses JSON, verifies every returned job ID, and rejects malformed batches.
5. Deterministic code adds posted age, market metrics, URLs, and local state.
6. Deterministic rendering creates the Markdown/PDF packet.
```

Pseudocode:

```python
for batch in partition(recent_jobs, size=8):
    response = ollama.chat(
        model="gemma4:12b",
        messages=[prompt_for_json_array(batch)],
        stream=False,
    )
    sheets = parse_json_array(response.content)
    assert {s.job_id for s in sheets} == {job.id for job in batch}
    render_sheets(join_source_facts(batch, sheets))
```

The LLM does not decide whether a job is a good fit. It extracts and compresses source text. The caller owns cohort selection, source facts, validation, rendering, and the human decision.

## Recommended production protocol

Use independent batches of **six to eight jobs**. Start with **one in-flight batch**. A one-batch protocol does not make assumptions about hidden model parallelism and keeps failures isolated. The batch response must be a strict JSON array; each object must contain the input `job_id` exactly once.

After a production-sized run has established output quality and error rates, test two simultaneous batches. Do not begin with twenty independent requests, and do not accumulate unrelated jobs as follow-up turns. Both strategies increase contention or context cost without improving the job-sheet contract.

The context window is a capacity limit, not a throughput target. Use it for information that must influence the next answer: a shared project specification, an evolving code review, a conversation requiring continuity. Do not use it as a container for independent records merely because it has unused space.

## Failure modes and controls

| Failure mode | Why it matters | Control |
|---|---|---|
| Sparse listing produces polished generic text | The source lacks details; prose can appear more specific than it is. | Require source quotes and allow `Not stated` deliverables. |
| JSON is syntactically valid but omits an input job | The packet silently loses a record. | Validate returned IDs as a set against batch IDs. |
| Parallel single-job calls contend | Wall time grows even though each call is valid. | Bound concurrency; measure actual host behavior. |
| Follow-up context grows | Prompt evaluation repeats irrelevant prior content. | Use fresh bounded batches for independent records. |
| Chunk timing is treated as TPS | Network/server buffering distorts the rate. | Use Ollama `eval_count` and `eval_duration` for output TPS. |
| Cold load is mixed with steady state | One request appears anomalously slow. | Record `load_duration`; report warm and cold behavior separately. |

## Reproduction commands

```bash
# Start the local-only tunnel if it is not already running.
tmux new-session -d -s ollama-mimimi \
  'exec ssh -N -o ExitOnForwardFailure=yes -L 127.0.0.1:11435:127.0.0.1:11434 mimimi-2.local'

# Run the streamed token benchmark.
cd /home/manuel/code/wesen/claw-stuff
python3 scripts/benchmark_ollama_job_sheets.py \
  --db upwork/upwork.db \
  --base-url http://127.0.0.1:11435 \
  --model gemma4:12b \
  --hours 24 --limit 5 \
  --out-prefix upwork/gemma4-12b-token-benchmark-2026-07-15

# Compare packaging strategies.
python3 scripts/benchmark_ollama_job_sheet_strategies.py
```

## Closing perspective

The inference result is simple once the counters are separated. Gemma 4 12B has a stable output-generation rate on this host. Input evaluation is much faster. The pipeline’s practical latency comes from TTFT, output length, scheduling, and packaging choices. Bounded structured batches reduce repeated setup and preserve a strong validation boundary. Context retention and indiscriminate parallel requests do not.

The next benchmark should hold total input tokens and requested output length constant while varying batch size and in-flight batch count. That experiment can distinguish the benefit of batching from differences in description length and response verbosity.
