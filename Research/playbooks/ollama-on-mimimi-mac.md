---
title: Accessing Ollama on the mimimi Mac
aliases:
  - mimimi Ollama tunnel
  - Mac Ollama access
tags:
  - playbook
  - ollama
  - ssh
  - llm
  - embeddings
status: active
type: article
created: 2026-07-15
repo: /home/manuel/workspaces/2026-07-13/rag-eval-ttc/rag-evaluation-system
---

# Accessing Ollama on the mimimi Mac

This playbook describes how to use the Ollama server running on Manuel's Mac
from another development machine without exposing the model API on the LAN. It
uses SSH local-port forwarding: callers use a normal local URL, while Ollama
continues to bind only to the Mac's loopback interface.

> [!summary]
> - Use `mimimi-2.local`, not `mimimi.local`: the short alias was unresolved when this playbook was verified.
> - Start a local-only tunnel to `http://127.0.0.1:11435`; the remote Ollama listener remains `127.0.0.1:11434`.
> - `nomic-embed-text:latest` is installed and returns 768-dimensional embeddings. It is not a chat LLM; install a chat-capable model before using `/api/chat`.

## When to use this

Use this pattern when a local project needs embeddings or inference from the
Mac's Ollama instance. Typical uses are RAG indexing, query embedding,
retrieval experiments, interactive LLM tools, and small scripts that speak
Ollama's native HTTP API.

Do not put this host, port, or a tunnel command into a repository's immutable
experiment specification. They are runtime infrastructure. Record the model
name, dimensions, and experiment configuration separately when reproducibility
matters.

## Topology and safety boundary

```mermaid
flowchart LR
    A[Local script or application] -->|HTTP 127.0.0.1:11435| B[SSH tunnel in tmux]
    B -->|encrypted SSH forwarding| C[mimimi-2.local]
    C -->|HTTP 127.0.0.1:11434| D[Ollama]
    D --> E[Embedding or chat model]

    style B fill:#e7f3ff,stroke:#1f6feb
    style D fill:#e9f7ef,stroke:#22863a
```

Both HTTP listeners are loopback-only. Keep it that way:

- Local callers use `127.0.0.1:11435`.
- Ollama stays on `127.0.0.1:11434` on the Mac.
- Do not add `-g`, `0.0.0.0`, reverse forwarding, or a firewall exception.
- The tunnel carries no API key. SSH authentication is the access boundary.

## Verify the remote server

First check SSH reachability and the model inventory. This does not start a
tunnel.

```bash
ssh -o BatchMode=yes -o ConnectTimeout=10 mimimi-2.local \
  'curl -fsS --max-time 5 http://127.0.0.1:11434/api/tags | jq -r "[.models[].name] | join(\",\")"'
```

Expected current output includes:

```text
nomic-embed-text:latest
```

If the Mac shell needs the Ollama CLI, it may not be on `PATH`. Use the app
bundle executable instead:

```bash
ssh mimimi-2.local '/Applications/Ollama.app/Contents/Resources/ollama list'
```

## Start the local tunnel

Use tmux so the tunnel survives the terminal that started it and can be
inspected independently from a long-running experiment.

```bash
tmux new-session -d -s ollama-mimimi \
  'exec ssh -N -o ExitOnForwardFailure=yes -o ServerAliveInterval=30 -o ServerAliveCountMax=3 -L 127.0.0.1:11435:127.0.0.1:11434 mimimi-2.local'
```

Inspect the session and validate the locally reachable endpoint:

```bash
tmux capture-pane -pt ollama-mimimi:0.0 -S -80
curl -fsS --max-time 5 http://127.0.0.1:11435/api/tags \
  | jq -r '[.models[].name] | join(",")'
```

The exact forwarding relation is:

```text
127.0.0.1:11435 on this machine
    -> SSH
    -> 127.0.0.1:11434 on mimimi-2.local
```

## Generate embeddings now

`nomic-embed-text:latest` is installed and produces 768-dimensional vectors.
Use the current native Ollama embedding endpoint for a bounded health check:

```bash
curl -fsS --max-time 30 http://127.0.0.1:11435/api/embed \
  -H 'Content-Type: application/json' \
  -d '{"model":"nomic-embed-text","input":"embedding health check"}' \
  | jq '[.embeddings[0] | length]'
```

Expected output:

```json
[768]
```

Some existing Go integrations, including Geppetto, use the compatibility
endpoint `/api/embeddings` with a `prompt` field:

```bash
curl -fsS --max-time 30 http://127.0.0.1:11435/api/embeddings \
  -H 'Content-Type: application/json' \
  -d '{"model":"nomic-embed-text","prompt":"embedding health check"}' \
  | jq '.embedding | length'
```

For Geppetto/RAG work, configure the provider explicitly as:

```text
type       = ollama
engine     = nomic-embed-text
dimensions = 768
base URL   = http://127.0.0.1:11435
```

## Run an LLM query

The currently verified model, `nomic-embed-text`, is for embeddings only. It
cannot provide meaningful chat responses. First inspect whether the desired
chat model is already installed:

```bash
curl -fsS http://127.0.0.1:11435/api/tags | jq -r '.models[].name'
```

If no chat-capable model is available, ask the Mac owner before downloading
one; model pulls consume disk space and network bandwidth. Two useful current
starting points are:

- `qwen3.5:9b`: the current default Qwen 3.5 tag is about 6.6 GB, supports
  text and image input, tools and thinking, and has a 256K context window.
  This is the recommended first general-purpose local model for chat, coding,
  and agent experiments on this Mac.
- `gemma4:12b`: about 7.6 GB, with text and image input and a 256K context
  window. Use this when testing the current Gemma family or when its
  multimodal and reasoning behaviour is the point of comparison.

Both are current-generation models, not aliases for the older Qwen 3 or Gemma
3 recommendations. Do not pull both by default: choose one, measure the Mac's
responsiveness and memory pressure, then add the other only when comparison is
useful.

The Ollama library names are authoritative at pull time. Confirm free disk
space and available memory first, then pull exactly one model as an explicit
operator action. The Mac's CLI may be absent from `PATH`, so use its verified
app-bundle path:

```bash
ssh mimimi-2.local \
  '/Applications/Ollama.app/Contents/Resources/ollama pull qwen3.5:9b'
```

Or install the smaller multimodal option:

```bash
ssh mimimi-2.local \
  '/Applications/Ollama.app/Contents/Resources/ollama pull gemma4:12b'
```

The command runs the download on the Mac, so it continues to use the Mac's
network and model store. Keep the SSH session open until the pull reports
success. If a colleague needs the pull to survive a disconnected terminal,
start the command in a remote tmux session only after verifying that tmux is
available on the Mac.

After the pull, verify the model and perform one short local request through
the tunnel before handing it to an application:

```bash
curl -fsS http://127.0.0.1:11435/api/tags | jq -r '.models[].name'

curl -fsS --max-time 180 http://127.0.0.1:11435/api/chat \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "qwen3.5:9b",
    "stream": false,
    "messages": [{"role": "user", "content": "Reply with exactly: ready"}]
  }' \
  | jq -r '.message.content'
```

Once a chat model is installed, make a non-streaming query through the tunnel:

```bash
curl -fsS --max-time 180 http://127.0.0.1:11435/api/chat \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "<installed-chat-model>",
    "stream": false,
    "messages": [
      {"role": "user", "content": "Explain reciprocal rank fusion in three sentences."}
    ]
  }' \
  | jq -r '.message.content'
```

Replace `<installed-chat-model>` with a name reported by `/api/tags`. Set a
timeout appropriate to the model and request. `stream: false` is convenient
for scripts; omit it or set `true` when consuming Ollama's streamed JSON
responses.

The model recommendations and reported sizes above are based on the current
[Qwen 3.5 Ollama listing](https://ollama.com/library/qwen3.5) and
[Gemma 4 Ollama listing](https://ollama.com/library/gemma4). Consult the
library immediately before a large pull because available tags and sizes can
change.

## Use from applications

Point a native-Ollama client at the local tunnel URL:

```text
baseURL = http://127.0.0.1:11435
```

For OpenAI-compatible clients, first verify the Ollama version and its exposed
`/v1` endpoints. The commands above use the stable native Ollama endpoints and
are the preferred starting point for diagnostics.

## Troubleshooting

| Symptom | Meaning and next action |
| --- | --- |
| `mimimi.local` does not resolve | Use `mimimi-2.local`. The shorter alias was not resolvable when verified. Repair DNS/mDNS separately if that alias is required. |
| SSH cannot connect | Confirm the Mac is awake and reachable; run the remote `/api/tags` check before changing tunnel options. |
| Local port 11435 refuses connections | Inspect `tmux capture-pane -pt ollama-mimimi:0.0 -S -80`; restart the tunnel only after remote health succeeds. |
| `nomic-embed-text` returns no chat answer | This is expected: it is an embedding model. Select an installed chat model. |
| Long RAG job appears to stop | Inspect tmux and durable run records. Do not start duplicate corpus jobs merely because a foreground shell stopped showing output. |

Stop the local tunnel when finished:

```bash
tmux kill-session -t ollama-mimimi
```

This stops only the SSH forwarding session. It does not stop Ollama on the
Mac.

## Related material

- RAG experiment operator reference: `/home/manuel/workspaces/2026-07-13/rag-eval-ttc/rag-evaluation-system/ttmp/2026/07/14/RAGEVAL-RAG-DSL-001--typed-fluent-javascript-rag-laboratory-module/reference/03-mimimi-ollama-tunnel-operator-playbook.md`
- Geppetto's Ollama provider: `/home/manuel/workspaces/2026-07-13/rag-eval-ttc/geppetto/pkg/embeddings/ollama.go`
