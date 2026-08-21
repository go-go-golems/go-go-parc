# OpenAI Realtime Audio Design

- URL: https://chatgpt.com/c/6a7b873e-b018-83ea-bc56-805cb3e96554
- Created: 2026-08-11T20:34:07.245Z

---

> Design how to add support for openai realtime audio, which can benefit from maybe both designs? Also study how one might stream audio from the browser to the api, and if it needs to be done through my own backend server or can be done in the browser?
>
> Make an indepth study and output a detailed report in markdown + pdf

```unknown
bash -lc cat /home/oai/skills/pdfs/SKILL.md && printf '\n---MARKDOWN/FILES---\n' && ls -la /home/oai/skills
```

I’ll inspect the codebase and its streaming designs, then verify OpenAI Realtime browser/server patterns from primary sources. I’ll deliver Markdown and PDF recommendations covering security, flows, and migration.

<details><summary>💭 Thinking</summary>

**Inspected design files, skills, archives, and SessionStream codebase dependencies**

</details>

```unknown
bash -lc cd /mnt/data/geppetto-sessionstream/geppetto && \
for f in \
  README.md \
  pkg/inference/engine/engine.go \
  pkg/inference/session/session.go \
  pkg/inference/session/execution.go \
  pkg/inference/session/builder.go \
  pkg/events/events.go \
  pkg/events/event-router.go \
  pkg/turns/turns.go \
  pkg/turns/blocks.go \
  pkg/inference/engine/factory/factory.go \
  pkg/steps/ai/types/types.go \
  pkg/steps/ai/settings/settings.go; do \
  if [ -f "$f" ]; then echo "===== $f ====="; sed -n '1,280p' "$f"; fi; \
done
```

<details><summary>💭 Thinking</summary>

**Inspected sessionstream event architecture and streaming integration files**

</details>

```json
{"search_query":[{"q":"site:platform.openai.com/docs/guides/realtime OpenAI Realtime API WebRTC browser ephemeral client secret"},{"q":"site:platform.openai.com/docs/guides/realtime OpenAI Realtime API WebSocket audio input buffer events"},{"q":"site:developers.openai.com realtime API WebRTC browser audio"},{"q":"site:openai.github.io/openai-agents-js realtime browser WebRTC OpenAI"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Researching current audio APIs**

I’m verifying the latest official documentation and browser standards, focusing on authentication, session architecture, voice activity detection, audio formats, interruptions, pricing, and whether a backend is required for browser audio streaming.

**Researched current audio APIs**

</details>

A key mismatch is that `RunInference` is finite, while Realtime is bidirectional and long-lived, favoring a first-class live-session API. Browser WebRTC with ephemeral credentials and backend WebSockets can share it.

```json
{"open":[{"ref_id":"turn624398search0"},{"ref_id":"turn624398search2"},{"ref_id":"turn624398search4"},{"ref_id":"turn624398search8"},{"ref_id":"turn624398search10"},{"ref_id":"turn624398search6"},{"ref_id":"turn624398search3"},{"ref_id":"turn624398search9"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Planning the integration report**

I’m mapping the uploaded codebase against two possible designs: a provider-native realtime engine and an application bridge for browser sessions, UI events, hydration, and audio delivery.

**Mapping the architecture**

I’m assessing how the existing blocking session model, event sinks, correlation IDs, and provider boundaries can support a persistent duplex audio session without disrupting current inference workflows.

**Defining the data model**

I’m separating transient audio chunks from durable turns: events can carry live audio and transcripts, while finalized transcripts, tool calls, and artifact references become persistent blocks without forcing every chunk into history.

**Comparing transport choices**

I’m distinguishing browser WebRTC, server WebSocket, and sideband control. The likely fit is browser-owned media with backend-owned session logic, tools, authorization, normalization, and application projections.

**Structuring the implementation**

I’m planning separate deployment modes and a provider-neutral realtime package, while keeping audio transport transient, transcripts durable, and existing blocking inference APIs compatible rather than forcing duplex sessions into them.

**Planned integration architecture, data model, transport, and implementation**

**Searched 2 websites**

**Searched Go-Go-Golems repositories**

</details>

```unknown
bash -lc cd /mnt/data && rm -rf sessionstream-src && git clone --depth 1 https://github.com/go-go-golems/sessionstream.git sessionstream-src && cd sessionstream-src && git rev-parse HEAD && find . -maxdepth 2 -type f | sed 's#^./##' | head -120
```

<details><summary>💭 Thinking</summary>

**Cloned public repository via Git**

**Synthesizing the design**

I’m combining the provider-neutral Geppetto layer with application-owned browser transport and sessionstream projections, keeping model IDs configurable and preserving secure server-side control of tools and credentials.

**Finalizing implementation paths**

I’m preparing the report around a recommended WebRTC-plus-sideband design, contrasting proxy and direct WebSocket alternatives, then documenting APIs, events, persistence, security, testing, rollout, and browser audio handling.

**Synthesized the design and finalized implementation paths**

**Fetched recursive GitHub repository tree**

</details>

```unknown
bash -lc ls -lah /mnt/data && find /mnt/data/geppetto-sessionstream -maxdepth 2 -type d | sed -n '1,120p' && echo '--- zip list top ---' && unzip -l /mnt/data/geppetto-sessionstream.zip | sed -n '1,80p'
```

<details><summary>💭 Thinking</summary>

**Inspected SessionStream repository structure and documentation**

</details>

```unknown
bash -lc cd /mnt/data/geppetto-sessionstream/sessionstream && \
for f in pkg/sessionstream/types.go pkg/sessionstream/schema.go pkg/sessionstream/hub.go pkg/sessionstream/handler.go pkg/sessionstream/projection.go pkg/sessionstream/hydration.go pkg/sessionstream/fanout.go pkg/sessionstream/consumer.go pkg/sessionstream/bus.go pkg/sessionstream/session_registry.go proto/sessionstream/v1/transport.proto examples/chatdemo/chat.go; do
  echo "===== $f ====="; sed -n '1,280p' "$f"; echo;
done
```

<details><summary>💭 Thinking</summary>

**Inspected Sessionstream architecture, handlers, transport, and WebSocket flow**

</details>

```json
{"open":[{"ref_id":"turn694877view0"},{"ref_id":"turn241872view0"},{"ref_id":"turn377263view0"},{"ref_id":"turn694877view3"},{"ref_id":"turn694877view2"},{"ref_id":"turn694877view5"},{"ref_id":"turn206795search0"},{"ref_id":"turn694877view6"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 2 websites**

</details>

```unknown
bash -lc for repo in /mnt/data/geppetto-sessionstream/geppetto /mnt/data/geppetto-sessionstream/sessionstream; do echo "==== $(basename $repo)/AGENT.md ===="; sed -n '1,260p' "$repo/AGENT.md"; echo; done
```

<details><summary>💭 Thinking</summary>

**Inspected repository guidance, architecture, dependencies, and SessionStream security semantics**

</details>

```json
{"search_query":[{"q":"site:developers.openai.com/api/docs/guides/realtime-tools OpenAI Realtime function calling tools"},{"q":"site:developers.openai.com/api/docs/api-reference/realtime-client-events conversation.item.create function_call_output"},{"q":"site:developers.openai.com/api/docs/api-reference/realtime-server-events response.function_call_arguments.done"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 1 website**

</details>

```unknown
bash -lc cd /mnt/data/geppetto-sessionstream/sessionstream && cat examples/chatdemo/proto/sessionstream/examples/chatdemo/v1/chat.proto && echo '--- app js transport use ---' && sed -n '1,320p' examples/goja-chatdemo-server/assets/public/app.js && echo '--- websocket module API ---' && sed -n '1,260p' pkg/js/modules/sessionstream/api_websocket.go
```

<details><summary>💭 Thinking</summary>

**Inspected Sessionstream schemas, APIs, and event model definitions**

</details>

```json
{"open":[{"ref_id":"turn281723view0","lineno":760},{"ref_id":"turn281723view0","lineno":810},{"ref_id":"turn281723view0","lineno":885},{"ref_id":"turn281723view0","lineno":921},{"ref_id":"turn281723view0","lineno":1016},{"ref_id":"turn281723view3","lineno":750},{"ref_id":"turn281723view2","lineno":747},{"ref_id":"turn281723view2","lineno":850},{"ref_id":"turn281723view4","lineno":1065},{"ref_id":"turn281723view4","lineno":1995}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Creating the report**

I’m documenting the combined architecture now: Geppetto owns provider-neutral realtime semantics, while sessionstream owns durable projections, hydration, commands, and browser-facing session state.

**Created the report**

**Searched 1 website**

</details>

```unknown
bash -lc sed -n '1,240p' /home/oai/skills/pdfs/SKILL.md && printf '\n---DOCX---\n' && sed -n '1,260p' /home/oai/skills/docx/SKILL.md
```

<details><summary>💭 Thinking</summary>

**Inspected repository files and extracted relevant code lines**

</details>

```json
{"search_query":[{"q":"site:developers.openai.com/api/docs/guides/realtime-webrtc OpenAI Realtime WebRTC browser unified interface ephemeral token sideband"},{"q":"site:developers.openai.com/api/docs/guides/realtime-websocket OpenAI Realtime WebSocket browser mobile WebRTC recommended base64 audio"},{"q":"site:developers.openai.com/api/docs/guides/realtime-server-controls OpenAI Realtime sideband call_id rtc websocket"},{"q":"site:developers.openai.com/api/docs/guides/realtime-transcription OpenAI Realtime transcription gpt-live-transcribe"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 1 website**

</details>

```unknown
bash -lc set -e
G=/mnt/data/geppetto-sessionstream/geppetto
S=/mnt/data/geppetto-sessionstream/sessionstream
show(){ local f=$1; local a=$2; local b=$3; echo "===== ${f#$G/} ====="; nl -ba "$f" | sed -n "${a},${b}p"; }
show "$G/pkg/inference/session/builder.go" 1 80
show "$G/pkg/inference/session/session.go" 1 260
show "$G/pkg/events/sink.go" 1 170
show "$G/pkg/events/context.go" 1 160
show "$G/pkg/events/chat-events.go" 1 330
show "$G/pkg/events/correlation.go" 1 260
show "$G/pkg/turns/types.go" 1 240
show "$G/pkg/turns/block_kind_gen.go" 1 180
show "$G/pkg/turns/keys_gen.go" 1 220
show "$G/pkg/inference/engine/factory/factory.go" 1 300
show "$G/pkg/steps/ai/types/types.go" 1 180
show "$G/pkg/steps/ai/openai/chat_stream_reducer.go" 1 320
show "$G/pkg/steps/ai/openai/observability.go" 1 240
show "$G/pkg/steps/ai/openai/transcribe.go" 1 260
printf '\n--- SESSIONSTREAM ---\n'
show "$S/pkg/sessionstream/types.go" 1 120
show "$S/pkg/sessionstream/schema.go" 1 320
show "$S/pkg/sessionstream/handler.go" 1 150
show "$S/pkg/sessionstream/projection.go" 1 200
show "$S/pkg/sessionstream/hydration.go" 1 260
show "$S/pkg/sessionstream/hub.go" 1 400
show "$S/pkg/sessionstream/transport/ws/server.go" 1 420
show "$S/proto/sessionstream/v1/transport.proto" 1 320
```

<details><summary>💭 Thinking</summary>

**Inspected sessionstream implementation, security, documentation, tooling, and repository status**

</details>

```json
{"open":[{"ref_id":"https://developers.openai.com/api/docs/guides/realtime-tools"}],"response_length":"long"}
```

I’ll separate high-rate audio from durable semantic events, preserving sessionstream hydration and UI projection boundaries. A WebRTC sideband backend can enforce instructions and tools without proxying microphone audio.

<details><summary>💭 Thinking</summary>

**Planning the report**

I’m grounding the design in both repositories: Geppetto’s finite inference boundary and sessionstream’s command/event projections. I’ll keep Realtime audio transient, persist finalized transcripts, and compare browser WebRTC with backend-mediated WebSocket approaches.

**Searching developers.openai.com**

</details>

```unknown
bash -lc cat /home/oai/skills/pdfs/SKILL.md && printf '\n---DOCX---\n' && cat /home/oai/skills/docx/SKILL.md
```

<details><summary>💭 Thinking</summary>

**Inspected PDF and document skills and Go repository structure**

</details>

```json
{"search_query":[{"q":"site:developers.openai.com/api/docs/guides realtime WebRTC browser unified interface sideband OpenAI"},{"q":"site:developers.openai.com/api/docs/guides realtime WebSocket browser WebRTC recommended OpenAI"},{"q":"site:developers.openai.com/api/docs/guides realtime conversations function calling tool output OpenAI"},{"q":"site:developers.openai.com/api/docs/models gpt-realtime 2.1 OpenAI"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 1 website**

</details>

```unknown
bash -lc set -euo pipefail
base=/mnt/data/geppetto-sessionstream
for spec in \
'geppetto/pkg/inference/engine/engine.go:1:80' \
'geppetto/pkg/inference/engine/types.go:145:190' \
'geppetto/pkg/inference/session/builder.go:1:80' \
'geppetto/pkg/inference/session/session.go:1:70' \
'geppetto/pkg/inference/session/session.go:175:275' \
'geppetto/pkg/events/sink.go:1:80' \
'geppetto/pkg/events/chat-events.go:1:120' \
'geppetto/pkg/events/chat-events.go:145:180' \
'geppetto/pkg/events/correlation.go:1:180' \
'geppetto/pkg/turns/types.go:1:180' \
'geppetto/pkg/steps/ai/types/types.go:1:150' \
'geppetto/pkg/inference/engine/factory/factory.go:1:240' \
'sessionstream/pkg/sessionstream/types.go:1:100' \
'sessionstream/pkg/sessionstream/schema.go:1:140' \
'sessionstream/pkg/sessionstream/handler.go:1:90' \
'sessionstream/pkg/sessionstream/projection.go:1:120' \
'sessionstream/pkg/sessionstream/hydration.go:1:220' \
'sessionstream/pkg/sessionstream/hub.go:1:240' \
'sessionstream/pkg/sessionstream/transport/ws/server.go:1:180' \
'sessionstream/proto/sessionstream/v1/transport.proto:1:220'; do
  file=${spec%%:*}; rest=${spec#*:}; start=${rest%%:*}; end=${rest##*:};
  echo "===== $file [$start-$end] ====="
  nl -ba "$base/$file" | sed -n "${start},${end}p"
done
```

<details><summary>💭 Thinking</summary>

**Inspected Sessionstream code, hydration details, block kinds, and guidelines**

</details>

```json
{"open":[{"ref_id":"turn217937view0","lineno":813},{"ref_id":"turn217937view0","lineno":921},{"ref_id":"turn217937view3","lineno":1938}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 1 website**

</details>

```unknown
bash -lc ls -la /mnt/data && find /mnt/data/geppetto-sessionstream -maxdepth 2 -type d | sed -n '1,40p' && printf '\n--- PDF SKILL ---\n' && sed -n '1,220p' /home/oai/skills/pdfs/SKILL.md && printf '\n--- DOCX SKILL ---\n' && sed -n '1,240p' /home/oai/skills/docx/SKILL.md
```

<details><summary>💭 Thinking</summary>

**Inspected report files and Geppetto Sessionstream source files**

</details>

```json
{"search_query":[{"q":"site:platform.openai.com/docs/guides/realtime-webrtc OpenAI Realtime WebRTC unified interface ephemeral token sideband"},{"q":"site:platform.openai.com/docs/guides/realtime-websocket OpenAI Realtime WebSocket audio append output_audio delta"},{"q":"site:platform.openai.com/docs/guides/realtime-conversations OpenAI Realtime conversations interruption function calling VAD"},{"q":"site:platform.openai.com/docs/models gpt-realtime gpt-realtime-mini realtime transcription"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 1 website**

</details>

```unknown
bash -lc command -v pandoc || true; command -v dot || true; command -v libreoffice || true; python - <<'PY'
import importlib.util
for m in ['docx','markdown','weasyprint','reportlab','PIL']:
    print(m, bool(importlib.util.find_spec(m)))
PY
```

<details><summary>💭 Thinking</summary>

**Created Geppetto Sessionstream architecture documentation and diagrams**

</details>

```json
{"find":[{"ref_id":"turn964695view2","pattern":"browser"},{"ref_id":"turn964695view2","pattern":"ephemeral"},{"ref_id":"turn964695view0","pattern":"WebSocket"},{"ref_id":"turn964695view3","pattern":"15 MB"},{"ref_id":"turn964695view3","pattern":"input_audio_buffer.append"},{"ref_id":"turn964695view3","pattern":"output_audio.delta"},{"ref_id":"turn964695view3","pattern":"automatic truncation"},{"ref_id":"turn964695view3","pattern":"conversation.item.truncate"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searching the web**

</details>

```unknown
bash -lc set -e
cd /mnt/data/realtime_report_work
for url in \
  https://developers.openai.com/api/docs/guides/realtime-webrtc.md \
  https://developers.openai.com/api/docs/guides/realtime-websocket.md \
  https://developers.openai.com/api/docs/guides/realtime-conversations.md \
  https://developers.openai.com/api/docs/guides/realtime-server-controls.md \
  https://developers.openai.com/api/docs/guides/realtime-transcription.md \
  https://developers.openai.com/api/docs/guides/realtime-vad.md \
  https://developers.openai.com/api/docs/guides/realtime-costs.md; do
  echo "Downloading $url"
  curl -fsSL --max-time 30 "$url" -o "$(basename "$url")"
done
wc -l *.md | sort -n

```

<details><summary>💭 Thinking</summary>

**Designing realtime support**

I’m framing the solution around an additive, long-lived Realtime API for Geppetto, while keeping browser media and sessionstream projection responsibilities separate. The report will compare WebRTC, WebSocket, sideband control, event normalization, persistence, security, testing, and rollout.

**Designed realtime support**

**Inspected Realtime sources and generated a comprehensive audio architecture report**

</details>

```unknown
bash -lc ls -l /mnt/data/realtime_report_work && wc -w /mnt/data/realtime_report_work/report_template.md && grep -n '@@DIAGRAM\|\\pagebreak' /mnt/data/realtime_report_work/report_template.md | head -20 && sed -n '1,180p' /home/oai/skills/pdfs/SKILL.md && printf '\n---DOCX---\n' && sed -n '1,220p' /home/oai/skills/docx/SKILL.md
```

<details><summary>💭 Thinking</summary>

**Created and polished a cited Markdown and DOCX report with diagrams**

</details>

```unknown
bash -lc rm -rf /mnt/data/realtime_report_work/rendered_docx/* && python /home/oai/skills/docx/render_docx.py /mnt/data/realtime_report_work/openai_realtime_audio_geppetto_sessionstream_report.docx --output_dir /mnt/data/realtime_report_work/rendered_docx --emit_pdf --verbose
```

<details><summary>💭 Thinking</summary>

**Rendered and inspected DOCX report layout and content across pages**

</details>

```unknown
bash -lc set -euo pipefail
cp /mnt/data/realtime_report_work/openai_realtime_audio_geppetto_sessionstream_report.md /mnt/data/openai_realtime_audio_geppetto_sessionstream_report.md
cp /mnt/data/realtime_report_work/rendered_docx/openai_realtime_audio_geppetto_sessionstream_report.pdf /mnt/data/openai_realtime_audio_geppetto_sessionstream_report.pdf
rm -rf /mnt/data/realtime_report_work/rendered_pdf/*
python /home/oai/skills/pdfs/scripts/render_pdf.py /mnt/data/openai_realtime_audio_geppetto_sessionstream_report.pdf --out_dir /mnt/data/realtime_report_work/rendered_pdf --dpi 200
ls /mnt/data/realtime_report_work/rendered_pdf/page-*.png | wc -l
ls -lh /mnt/data/openai_realtime_audio_geppetto_sessionstream_report.md /mnt/data/openai_realtime_audio_geppetto_sessionstream_report.pdf
pdfinfo /mnt/data/openai_realtime_audio_geppetto_sessionstream_report.pdf | sed -n '1,22p'
python /home/oai/skills/pdfs/scripts/pdf_preflight.py /mnt/data/openai_realtime_audio_geppetto_sessionstream_report.pdf
```

<details><summary>💭 Thinking</summary>

**Rendered and inspected the final report PDF images**

</details>

The 52-page report is complete and visually clean, with final diagram readability fixes. It also details WebSocket framing/playback duties and when recording, redaction, DSP, or governance requires backend audio relay.

## Completed

The report’s central recommendation is to add a provider-neutral, long-lived `pkg/inference/live` subsystem rather than stretching Geppetto’s finite `Engine.RunInference` contract into a duplex-session API.

The proposed production topology is:

1. **Browser-to-OpenAI WebRTC for media** — microphone audio and model audio travel directly between the browser and OpenAI.
2. **Authenticated Geppetto bootstrap endpoint** — the permanent OpenAI API key remains server-side; the backend either forwards the browser’s SDP offer through the unified interface or issues a short-lived client secret.
3. **Geppetto sideband WebSocket** — the backend attaches to the same Realtime call using its `call_id` and retains control over tools, authorization, instructions, observability, and persistence.
4. **Optional backend media proxy** — reserved for telephony, recording, compliance, transcoding, media inspection, or environments where direct WebRTC is unsuitable.

OpenAI recommends WebRTC for browser and mobile clients, supports both unified SDP and short-lived client-secret bootstrap flows, and documents a sideband connection that lets the application server control the same session without proxying its media. citeturn509053view0turn509053view1turn803448view3 Client secrets are temporary credentials rather than substitutes for application authorization. citeturn509053view4

The design also supports both native speech-to-speech Realtime sessions and a chained transcription → existing Geppetto agent/tool loop → speech-generation architecture. citeturn411926search1

The 52-page report includes:

- Repository-specific architectural findings
- Four architecture and transport diagrams
- Browser WebRTC and WebSocket implementation sketches
- Proposed Go packages and interfaces
- Unified SDP and ephemeral-secret endpoint designs
- Sideband lifecycle and failure handling
- Reliable tool-dispatch and idempotency design
- Event correlation and conversation mirroring
- VAD, interruption, truncation, and playback semantics
- Security, privacy, logging, and credential boundaries
- Session rollover, reconnect, queues, and backpressure
- Observability, capacity, and cost considerations
- Testing strategy, phased rollout, ADRs, and implementation checklists

## Deliverables

[Download the detailed Markdown report](sandbox:/mnt/data/openai_realtime_audio_geppetto_design_report.md)

[Download the formatted PDF report](sandbox:/mnt/data/openai_realtime_audio_geppetto_design_report.pdf)

