<div class="cover-page">

<div class="eyebrow">ARCHITECTURE STUDY</div>

# OpenAI Realtime Audio Support for Geppetto

## Browser audio transport, backend control, session design, tools, persistence, and rollout

<div class="cover-rule"></div>

**Research date:** 2026-08-11  
**Codebase reviewed:** `geppetto-sessionstream.zip`  
**Archive SHA-256:** `26628f8b3458050d493adebe157f7fdfda10c4ad8d15545412c5593314faafd1`

<div class="cover-decision">
<strong>Primary recommendation</strong><br>
Use direct browser-to-OpenAI WebRTC for the audio media path, an authenticated Geppetto endpoint for session bootstrap, and an OpenAI sideband WebSocket from Geppetto for tools, policy, observability, and durable state. Add a provider-neutral long-lived <code>live</code> subsystem instead of treating Realtime as another finite <code>engine.Engine</code>.
</div>

<div class="cover-note">Current as of 2026-08-11. OpenAI model names and protocol details must remain configuration-driven because this API surface continues to evolve.</div>

</div>

<div class="page-break"></div>

# Executive summary {#executive-summary}

Geppetto can support OpenAI Realtime audio cleanly, but the implementation should not be forced into its existing finite inference abstraction. The current `engine.Engine` contract accepts one `Turn` and returns one updated `Turn`; `session.ExecutionHandle` represents one cancelable, waitable inference; and `toolloop.Loop` repeatedly invokes that finite engine. A Realtime call is structurally different: it is a long-lived, bidirectional session containing many user speech turns, model responses, interruptions, function calls, configuration updates, and transport events.

The correct design is a parallel provider-neutral `pkg/inference/live` subsystem. It should reuse Geppetto's strongest existing concepts - stable `SessionID` values, canonical event correlation, `EventSink`, tool registry/executor, Turn persistence, settings, and JavaScript-facing session vocabulary - while introducing a separate lifecycle and reliable command path for duplex sessions.

<div class="decision-box">

### Direct answers

1. **Can the browser stream microphone audio directly to OpenAI?** Yes. For browser and mobile clients, OpenAI recommends WebRTC. The browser supplies a microphone media track to `RTCPeerConnection`, receives model audio as a remote media track, and uses a data channel for JSON control events. It does not manually Base64-encode microphone chunks in this topology. [OAI-WEBRTC] [OAI-CONVERSATIONS]

2. **Does all audio need to pass through the application's backend?** No. In the recommended topology, audio flows between the browser and OpenAI. Geppetto remains involved for authentication/bootstrap and attaches to the same Realtime call through a server-side sideband WebSocket for tools and control. [OAI-SIDEBAND]

3. **Is any backend required?** For a secure production browser application, yes, but it can be very small. A trusted endpoint either mints a short-lived Realtime client secret or forwards the browser's SDP offer through the unified `/v1/realtime/calls` interface. The permanent OpenAI API key must remain on the server. [OAI-WEBRTC] [OAI-CLIENT-SECRETS]

4. **Can the browser connect over WebSocket instead?** Technically yes with an ephemeral token, but OpenAI recommends WebRTC for browser/mobile clients. Browser WebSocket audio requires manual capture, resampling, PCM framing, Base64 encoding, playback buffering, and interruption truncation. [OAI-WEBSOCKET] [OAI-CONVERSATIONS]

5. **Should Geppetto support a backend media proxy?** Yes as a second transport, not the default. It is justified for telephony, recording/compliance, transcoding, media inspection, centralized routing, or non-WebRTC environments. It adds latency, bandwidth, CPU, failure modes, and a difficult playback/truncation implementation.

6. **Can the proposed feature benefit from both existing Geppetto designs?** Yes. The session-centered API should own identity, lifecycle, snapshots, and persistence. The streaming EventEmitter/EventSink design should expose semantic deltas and lifecycle events. Raw audio must remain on a dedicated media path rather than being emitted through the general event bus.

7. **Should Geppetto support both voice architectures?** Yes. Expose both a native speech-to-speech Realtime mode and a chained mode that uses live transcription -> existing Geppetto text agent/tool loop -> streaming speech generation. OpenAI documents both as valid architectures with different control/latency tradeoffs. [OAI-VOICE-AGENTS]

</div>

## Recommended production shape

<img class="diagram-img" alt="Recommended WebRTC and sideband architecture" src="data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiIHN0YW5kYWxvbmU9Im5vIj8+CjwhRE9DVFlQRSBzdmcgUFVCTElDICItLy9XM0MvL0RURCBTVkcgMS4xLy9FTiIKICJodHRwOi8vd3d3LnczLm9yZy9HcmFwaGljcy9TVkcvMS4xL0RURC9zdmcxMS5kdGQiPgo8IS0tIEdlbmVyYXRlZCBieSBncmFwaHZpeiB2ZXJzaW9uIDIuNDIuNCAoMCkKIC0tPgo8IS0tIFRpdGxlOiBHIFBhZ2VzOiAxIC0tPgo8c3ZnIHdpZHRoPSI5NjVwdCIgaGVpZ2h0PSIzOThwdCIKIHZpZXdCb3g9IjAuMDAgMC4wMCA5NjUuMDAgMzk4LjAwIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIj4KPGcgaWQ9ImdyYXBoMCIgY2xhc3M9ImdyYXBoIiB0cmFuc2Zvcm09InNjYWxlKDEgMSkgcm90YXRlKDApIHRyYW5zbGF0ZSgxOCAzODApIj4KPHRpdGxlPkc8L3RpdGxlPgo8ZyBpZD0iY2x1c3QxIiBjbGFzcz0iY2x1c3RlciI+Cjx0aXRsZT5jbHVzdGVyX2Jyb3dzZXI8L3RpdGxlPgo8cGF0aCBmaWxsPSJ0cmFuc3BhcmVudCIgc3Ryb2tlPSIjOWJiNGM1IiBkPSJNMjAsLTI2OEMyMCwtMjY4IDU2MCwtMjY4IDU2MCwtMjY4IDU2NiwtMjY4IDU3MiwtMjc0IDU3MiwtMjgwIDU3MiwtMjgwIDU3MiwtMzQyIDU3MiwtMzQyIDU3MiwtMzQ4IDU2NiwtMzU0IDU2MCwtMzU0IDU2MCwtMzU0IDIwLC0zNTQgMjAsLTM1NCAxNCwtMzU0IDgsLTM0OCA4LC0zNDIgOCwtMzQyIDgsLTI4MCA4LC0yODAgOCwtMjc0IDE0LC0yNjggMjAsLTI2OCIvPgo8dGV4dCB0ZXh0LWFuY2hvcj0ibWlkZGxlIiB4PSIyOTAiIHk9Ii0zNDEuMiIgZm9udC1mYW1pbHk9IkRlamFWdSBTYW5zIiBmb250LXNpemU9IjExLjAwIj5Ccm93c2VyPC90ZXh0Pgo8L2c+CjxnIGlkPSJjbHVzdDIiIGNsYXNzPSJjbHVzdGVyIj4KPHRpdGxlPmNsdXN0ZXJfYmFja2VuZDwvdGl0bGU+CjxwYXRoIGZpbGw9InRyYW5zcGFyZW50IiBzdHJva2U9IiM5YmI0YzUiIGQ9Ik0zNzksLThDMzc5LC04IDkwOSwtOCA5MDksLTggOTE1LC04IDkyMSwtMTQgOTIxLC0yMCA5MjEsLTIwIDkyMSwtMjIwIDkyMSwtMjIwIDkyMSwtMjI2IDkxNSwtMjMyIDkwOSwtMjMyIDkwOSwtMjMyIDM3OSwtMjMyIDM3OSwtMjMyIDM3MywtMjMyIDM2NywtMjI2IDM2NywtMjIwIDM2NywtMjIwIDM2NywtMjAgMzY3LC0yMCAzNjcsLTE0IDM3MywtOCAzNzksLTgiLz4KPHRleHQgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iNDI1LjUiIHk9Ii0xNS4yIiBmb250LWZhbWlseT0iRGVqYVZ1IFNhbnMiIGZvbnQtc2l6ZT0iMTEuMDAiPkdlcHBldHRvIGJhY2tlbmQ8L3RleHQ+CjwvZz4KPGcgaWQ9ImNsdXN0MyIgY2xhc3M9ImNsdXN0ZXIiPgo8dGl0bGU+Y2x1c3Rlcl9vcGVuYWk8L3RpdGxlPgo8cGF0aCBmaWxsPSJ0cmFuc3BhcmVudCIgc3Ryb2tlPSIjOWJiNGM1IiBkPSJNNzQ0LC0yNTZDNzQ0LC0yNTYgODg3LC0yNTYgODg3LC0yNTYgODkzLC0yNTYgODk5LC0yNjIgODk5LC0yNjggODk5LC0yNjggODk5LC0zMTYgODk5LC0zMTYgODk5LC0zMjIgODkzLC0zMjggODg3LC0zMjggODg3LC0zMjggNzQ0LC0zMjggNzQ0LC0zMjggNzM4LC0zMjggNzMyLC0zMjIgNzMyLC0zMTYgNzMyLC0zMTYgNzMyLC0yNjggNzMyLC0yNjggNzMyLC0yNjIgNzM4LC0yNTYgNzQ0LC0yNTYiLz4KPHRleHQgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iODE1LjUiIHk9Ii0zMTUuMiIgZm9udC1mYW1pbHk9IkRlamFWdSBTYW5zIiBmb250LXNpemU9IjExLjAwIj5PcGVuQUkgUmVhbHRpbWU8L3RleHQ+CjwvZz4KPCEtLSB1aSAtLT4KPGcgaWQ9Im5vZGUxIiBjbGFzcz0ibm9kZSI+Cjx0aXRsZT51aTwvdGl0bGU+CjxwYXRoIGZpbGw9IiNlYWYzZjgiIHN0cm9rZT0iIzI0NDQ1ZiIgc3Ryb2tlLXdpZHRoPSIxLjIiIGQ9Ik0yMDYsLTMxOUMyMDYsLTMxOSAyOCwtMzE5IDI4LC0zMTkgMjIsLTMxOSAxNiwtMzEzIDE2LC0zMDcgMTYsLTMwNyAxNiwtMjk1IDE2LC0yOTUgMTYsLTI4OSAyMiwtMjgzIDI4LC0yODMgMjgsLTI4MyAyMDYsLTI4MyAyMDYsLTI4MyAyMTIsLTI4MyAyMTgsLTI4OSAyMTgsLTI5NSAyMTgsLTI5NSAyMTgsLTMwNyAyMTgsLTMwNyAyMTgsLTMxMyAyMTIsLTMxOSAyMDYsLTMxOSIvPgo8dGV4dCB0ZXh0LWFuY2hvcj0ibWlkZGxlIiB4PSIxMTciIHk9Ii0zMDQiIGZvbnQtZmFtaWx5PSJEZWphVnUgU2FucyIgZm9udC1zaXplPSIxMC4wMCI+Vm9pY2UgVUk8L3RleHQ+Cjx0ZXh0IHRleHQtYW5jaG9yPSJtaWRkbGUiIHg9IjExNyIgeT0iLTI5MyIgZm9udC1mYW1pbHk9IkRlamFWdSBTYW5zIiBmb250LXNpemU9IjEwLjAwIj51c2VyIGdlc3R1cmUsIG11dGUsIGRldmljZSBzZWxlY3Rpb248L3RleHQ+CjwvZz4KPCEtLSBwYyAtLT4KPGcgaWQ9Im5vZGUyIiBjbGFzcz0ibm9kZSI+Cjx0aXRsZT5wYzwvdGl0bGU+CjxwYXRoIGZpbGw9IiNkY2VjZjUiIHN0cm9rZT0iIzI0NDQ1ZiIgc3Ryb2tlLXdpZHRoPSIxLjIiIGQ9Ik01NTIsLTMyNkM1NTIsLTMyNiA0MTAsLTMyNiA0MTAsLTMyNiA0MDQsLTMyNiAzOTgsLTMyMCAzOTgsLTMxNCAzOTgsLTMxNCAzOTgsLTMwMiAzOTgsLTMwMiAzOTgsLTI5NiA0MDQsLTI5MCA0MTAsLTI5MCA0MTAsLTI5MCA1NTIsLTI5MCA1NTIsLTI5MCA1NTgsLTI5MCA1NjQsLTI5NiA1NjQsLTMwMiA1NjQsLTMwMiA1NjQsLTMxNCA1NjQsLTMxNCA1NjQsLTMyMCA1NTgsLTMyNiA1NTIsLTMyNiIvPgo8dGV4dCB0ZXh0LWFuY2hvcj0ibWlkZGxlIiB4PSI0ODEiIHk9Ii0zMTEiIGZvbnQtZmFtaWx5PSJEZWphVnUgU2FucyIgZm9udC1zaXplPSIxMC4wMCI+UlRDUGVlckNvbm5lY3Rpb248L3RleHQ+Cjx0ZXh0IHRleHQtYW5jaG9yPSJtaWRkbGUiIHg9IjQ4MSIgeT0iLTMwMCIgZm9udC1mYW1pbHk9IkRlamFWdSBTYW5zIiBmb250LXNpemU9IjEwLjAwIj5tZWRpYSB0cmFja3MgKyBkYXRhIGNoYW5uZWw8L3RleHQ+CjwvZz4KPCEtLSB1aSYjNDU7Jmd0O3BjIC0tPgo8ZyBpZD0iZWRnZTEiIGNsYXNzPSJlZGdlIj4KPHRpdGxlPnVpJiM0NTsmZ3Q7cGM8L3RpdGxlPgo8cGF0aCBmaWxsPSJub25lIiBzdHJva2U9IiM1MzZiN2EiIHN0cm9rZS13aWR0aD0iMS40IiBkPSJNMjE4LjM2LC0zMDIuOTRDMjcyLjIsLTMwMy45OCAzMzguMDIsLTMwNS4yNSAzOTAuMTcsLTMwNi4yNiIvPgo8cG9seWdvbiBmaWxsPSIjNTM2YjdhIiBzdHJva2U9IiM1MzZiN2EiIHN0cm9rZS13aWR0aD0iMS40IiBwb2ludHM9IjM5MC4yMSwtMzA4Ljg5IDM5Ny43NiwtMzA2LjQxIDM5MC4zMiwtMzAzLjY0IDM5MC4yMSwtMzA4Ljg5Ii8+Cjx0ZXh0IHRleHQtYW5jaG9yPSJtaWRkbGUiIHg9IjI5Ni41IiB5PSItMzA3LjgiIGZvbnQtZmFtaWx5PSJEZWphVnUgU2FucyIgZm9udC1zaXplPSI5LjAwIj5taWNyb3Bob25lIC8gc3BlYWtlcjwvdGV4dD4KPC9nPgo8IS0tIGJvb3RzdHJhcCAtLT4KPGcgaWQ9Im5vZGUzIiBjbGFzcz0ibm9kZSI+Cjx0aXRsZT5ib290c3RyYXA8L3RpdGxlPgo8cGF0aCBmaWxsPSIjZWVmNGZmIiBzdHJva2U9IiMyNDQ0NWYiIHN0cm9rZS13aWR0aD0iMS4yIiBkPSJNNTQ4LC0yMjRDNTQ4LC0yMjQgNDE0LC0yMjQgNDE0LC0yMjQgNDA4LC0yMjQgNDAyLC0yMTggNDAyLC0yMTIgNDAyLC0yMTIgNDAyLC0yMDAgNDAyLC0yMDAgNDAyLC0xOTQgNDA4LC0xODggNDE0LC0xODggNDE0LC0xODggNTQ4LC0xODggNTQ4LC0xODggNTU0LC0xODggNTYwLC0xOTQgNTYwLC0yMDAgNTYwLC0yMDAgNTYwLC0yMTIgNTYwLC0yMTIgNTYwLC0yMTggNTU0LC0yMjQgNTQ4LC0yMjQiLz4KPHRleHQgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iNDgxIiB5PSItMjA5IiBmb250LWZhbWlseT0iRGVqYVZ1IFNhbnMiIGZvbnQtc2l6ZT0iMTAuMDAiPkF1dGhlbnRpY2F0ZWQgYm9vdHN0cmFwPC90ZXh0Pgo8dGV4dCB0ZXh0LWFuY2hvcj0ibWlkZGxlIiB4PSI0ODEiIHk9Ii0xOTgiIGZvbnQtZmFtaWx5PSJEZWphVnUgU2FucyIgZm9udC1zaXplPSIxMC4wMCI+U0RQIGFuc3dlciBvciBjbGllbnQgc2VjcmV0PC90ZXh0Pgo8L2c+CjwhLS0gdWkmIzQ1OyZndDtib290c3RyYXAgLS0+CjxnIGlkPSJlZGdlNiIgY2xhc3M9ImVkZ2UiPgo8dGl0bGU+dWkmIzQ1OyZndDtib290c3RyYXA8L3RpdGxlPgo8cGF0aCBmaWxsPSJub25lIiBzdHJva2U9IiM1MzZiN2EiIHN0cm9rZS13aWR0aD0iMS40IiBzdHJva2UtZGFzaGFycmF5PSI1LDIiIGQ9Ik0xODYuOTQsLTI4Mi45MUMyNDguOTYsLTI2Ni42MyAzMzkuOTMsLTI0Mi43NiA0MDQuMDMsLTIyNS45NCIvPgo8cG9seWdvbiBmaWxsPSIjNTM2YjdhIiBzdHJva2U9IiM1MzZiN2EiIHN0cm9rZS13aWR0aD0iMS40IiBwb2ludHM9IjQwNC43MywtMjI4LjQ3IDQxMS4zMiwtMjI0LjAzIDQwMy4zOSwtMjIzLjM5IDQwNC43MywtMjI4LjQ3Ii8+CjwvZz4KPCEtLSBjYWxsIC0tPgo8ZyBpZD0ibm9kZTgiIGNsYXNzPSJub2RlIj4KPHRpdGxlPmNhbGw8L3RpdGxlPgo8cGF0aCBmaWxsPSIjZTRmNWVkIiBzdHJva2U9IiMyNDQ0NWYiIHN0cm9rZS13aWR0aD0iMS4yIiBkPSJNODc5LC0zMDBDODc5LC0zMDAgNzUyLC0zMDAgNzUyLC0zMDAgNzQ2LC0zMDAgNzQwLC0yOTQgNzQwLC0yODggNzQwLC0yODggNzQwLC0yNzYgNzQwLC0yNzYgNzQwLC0yNzAgNzQ2LC0yNjQgNzUyLC0yNjQgNzUyLC0yNjQgODc5LC0yNjQgODc5LC0yNjQgODg1LC0yNjQgODkxLC0yNzAgODkxLC0yNzYgODkxLC0yNzYgODkxLC0yODggODkxLC0yODggODkxLC0yOTQgODg1LC0zMDAgODc5LC0zMDAiLz4KPHRleHQgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iODE1LjUiIHk9Ii0yODUiIGZvbnQtZmFtaWx5PSJEZWphVnUgU2FucyIgZm9udC1zaXplPSIxMC4wMCI+T25lIFJlYWx0aW1lIGNhbGwvc2Vzc2lvbjwvdGV4dD4KPHRleHQgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iODE1LjUiIHk9Ii0yNzQiIGZvbnQtZmFtaWx5PSJEZWphVnUgU2FucyIgZm9udC1zaXplPSIxMC4wMCI+Y29udmVyc2F0aW9uICsgcmVzcG9uc2VzPC90ZXh0Pgo8L2c+CjwhLS0gcGMmIzQ1OyZndDtjYWxsIC0tPgo8ZyBpZD0iZWRnZTUiIGNsYXNzPSJlZGdlIj4KPHRpdGxlPnBjJiM0NTsmZ3Q7Y2FsbDwvdGl0bGU+CjxwYXRoIGZpbGw9Im5vbmUiIHN0cm9rZT0iIzFlNmY5ZiIgc3Ryb2tlLXdpZHRoPSIyLjIiIGQ9Ik01NjQuMTksLTMwMS41N0M2MTUuMzIsLTI5Ny41OCA2ODAuODQsLTI5Mi40NSA3MzIuMDIsLTI4OC40NSIvPgo8cG9seWdvbiBmaWxsPSIjMWU2ZjlmIiBzdHJva2U9IiMxZTZmOWYiIHN0cm9rZS13aWR0aD0iMi4yIiBwb2ludHM9IjczMi41MSwtMjkxLjA0IDczOS43OCwtMjg3Ljg0IDczMi4xLC0yODUuODEgNzMyLjUxLC0yOTEuMDQiLz4KPHRleHQgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iNjUyLjUiIHk9Ii0yOTkuOCIgZm9udC1mYW1pbHk9IkRlamFWdSBTYW5zIiBmb250LXNpemU9IjkuMDAiPmRpcmVjdCBXZWJSVEM8L3RleHQ+CjwvZz4KPCEtLSBib290c3RyYXAmIzQ1OyZndDtjYWxsIC0tPgo8ZyBpZD0iZWRnZTciIGNsYXNzPSJlZGdlIj4KPHRpdGxlPmJvb3RzdHJhcDplJiM0NTsmZ3Q7Y2FsbDp3PC90aXRsZT4KPHBhdGggZmlsbD0ibm9uZSIgc3Ryb2tlPSIjNTM2YjdhIiBzdHJva2Utd2lkdGg9IjEuNCIgc3Ryb2tlLWRhc2hhcnJheT0iNSwyIiBkPSJNNTYxLC0yMDZDNTkwLjcxLC0yMDYgNTg5LjI4LC0yMzEgNjE2LC0yNDQgNjY0Ljg2LC0yNjcuNzYgNjgwLjA4LC0yODAuNzUgNzMwLjc2LC0yODEuOTEiLz4KPHBvbHlnb24gZmlsbD0iIzUzNmI3YSIgc3Ryb2tlPSIjNTM2YjdhIiBzdHJva2Utd2lkdGg9IjEuNCIgcG9pbnRzPSI3MzAuOTcsLTI4NC41NCA3MzguNSwtMjgyIDczMS4wMywtMjc5LjI5IDczMC45NywtMjg0LjU0Ii8+CjwvZz4KPCEtLSBzaWRlYmFuZCAtLT4KPGcgaWQ9Im5vZGU0IiBjbGFzcz0ibm9kZSI+Cjx0aXRsZT5zaWRlYmFuZDwvdGl0bGU+CjxwYXRoIGZpbGw9IiNkZmU5ZmYiIHN0cm9rZT0iIzI0NDQ1ZiIgc3Ryb2tlLXdpZHRoPSIxLjIiIGQ9Ik01NzUsLTE0OEM1NzUsLTE0OCAzODcsLTE0OCAzODcsLTE0OCAzODEsLTE0OCAzNzUsLTE0MiAzNzUsLTEzNiAzNzUsLTEzNiAzNzUsLTEyNCAzNzUsLTEyNCAzNzUsLTExOCAzODEsLTExMiAzODcsLTExMiAzODcsLTExMiA1NzUsLTExMiA1NzUsLTExMiA1ODEsLTExMiA1ODcsLTExOCA1ODcsLTEyNCA1ODcsLTEyNCA1ODcsLTEzNiA1ODcsLTEzNiA1ODcsLTE0MiA1ODEsLTE0OCA1NzUsLTE0OCIvPgo8dGV4dCB0ZXh0LWFuY2hvcj0ibWlkZGxlIiB4PSI0ODEiIHk9Ii0xMzMiIGZvbnQtZmFtaWx5PSJEZWphVnUgU2FucyIgZm9udC1zaXplPSIxMC4wMCI+TGl2ZSBjb250cm9sbGVyIC8gc2lkZWJhbmQ8L3RleHQ+Cjx0ZXh0IHRleHQtYW5jaG9yPSJtaWRkbGUiIHg9IjQ4MSIgeT0iLTEyMiIgZm9udC1mYW1pbHk9IkRlamFWdSBTYW5zIiBmb250LXNpemU9IjEwLjAwIj5wcm90b2NvbCByZWR1Y2VyICsgcmVsaWFibGUgY29tbWFuZHM8L3RleHQ+CjwvZz4KPCEtLSB0b29scyAtLT4KPGcgaWQ9Im5vZGU1IiBjbGFzcz0ibm9kZSI+Cjx0aXRsZT50b29sczwvdGl0bGU+CjxwYXRoIGZpbGw9IiNlZWY0ZmYiIHN0cm9rZT0iIzI0NDQ1ZiIgc3Ryb2tlLXdpZHRoPSIxLjIiIGQ9Ik04ODcsLTcyQzg4NywtNzIgNzQ0LC03MiA3NDQsLTcyIDczOCwtNzIgNzMyLC02NiA3MzIsLTYwIDczMiwtNjAgNzMyLC00OCA3MzIsLTQ4IDczMiwtNDIgNzM4LC0zNiA3NDQsLTM2IDc0NCwtMzYgODg3LC0zNiA4ODcsLTM2IDg5MywtMzYgODk5LC00MiA4OTksLTQ4IDg5OSwtNDggODk5LC02MCA4OTksLTYwIDg5OSwtNjYgODkzLC03MiA4ODcsLTcyIi8+Cjx0ZXh0IHRleHQtYW5jaG9yPSJtaWRkbGUiIHg9IjgxNS41IiB5PSItNTciIGZvbnQtZmFtaWx5PSJEZWphVnUgU2FucyIgZm9udC1zaXplPSIxMC4wMCI+VG9vbCByZWdpc3RyeSArIGV4ZWN1dG9yPC90ZXh0Pgo8dGV4dCB0ZXh0LWFuY2hvcj0ibWlkZGxlIiB4PSI4MTUuNSIgeT0iLTQ2IiBmb250LWZhbWlseT0iRGVqYVZ1IFNhbnMiIGZvbnQtc2l6ZT0iMTAuMDAiPmF1dGhvcml6YXRpb24gKyBpZGVtcG90ZW5jeTwvdGV4dD4KPC9nPgo8IS0tIHNpZGViYW5kJiM0NTsmZ3Q7dG9vbHMgLS0+CjxnIGlkPSJlZGdlMiIgY2xhc3M9ImVkZ2UiPgo8dGl0bGU+c2lkZWJhbmQmIzQ1OyZndDt0b29sczwvdGl0bGU+CjxwYXRoIGZpbGw9Im5vbmUiIHN0cm9rZT0iIzUzNmI3YSIgc3Ryb2tlLXdpZHRoPSIxLjQiIGQ9Ik01NjguMzMsLTExMC4yN0M2MTcuNTQsLTk5LjAyIDY3OS4wMSwtODQuOTcgNzI4LjIxLC03My43MiIvPgo8cG9seWdvbiBmaWxsPSIjNTM2YjdhIiBzdHJva2U9IiM1MzZiN2EiIHN0cm9rZS13aWR0aD0iMS40IiBwb2ludHM9IjU2Ny41MiwtMTA3Ljc2IDU2MC44LC0xMTEuOTkgNTY4LjY5LC0xMTIuODggNTY3LjUyLC0xMDcuNzYiLz4KPHBvbHlnb24gZmlsbD0iIzUzNmI3YSIgc3Ryb2tlPSIjNTM2YjdhIiBzdHJva2Utd2lkdGg9IjEuNCIgcG9pbnRzPSI3MjguOTcsLTc2LjI0IDczNS42OSwtNzIuMDEgNzI3LjgsLTcxLjEzIDcyOC45NywtNzYuMjQiLz4KPHRleHQgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iNjUyLjUiIHk9Ii0xMDEuOCIgZm9udC1mYW1pbHk9IkRlamFWdSBTYW5zIiBmb250LXNpemU9IjkuMDAiPnRvb2wgY2FsbHMvcmVzdWx0czwvdGV4dD4KPC9nPgo8IS0tIHBlcnNpc3QgLS0+CjxnIGlkPSJub2RlNiIgY2xhc3M9Im5vZGUiPgo8dGl0bGU+cGVyc2lzdDwvdGl0bGU+CjxwYXRoIGZpbGw9IiNlZWY0ZmYiIHN0cm9rZT0iIzI0NDQ1ZiIgc3Ryb2tlLXdpZHRoPSIxLjIiIGQ9Ik05MDEsLTE0OEM5MDEsLTE0OCA3MzAsLTE0OCA3MzAsLTE0OCA3MjQsLTE0OCA3MTgsLTE0MiA3MTgsLTEzNiA3MTgsLTEzNiA3MTgsLTEyNCA3MTgsLTEyNCA3MTgsLTExOCA3MjQsLTExMiA3MzAsLTExMiA3MzAsLTExMiA5MDEsLTExMiA5MDEsLTExMiA5MDcsLTExMiA5MTMsLTExOCA5MTMsLTEyNCA5MTMsLTEyNCA5MTMsLTEzNiA5MTMsLTEzNiA5MTMsLTE0MiA5MDcsLTE0OCA5MDEsLTE0OCIvPgo8dGV4dCB0ZXh0LWFuY2hvcj0ibWlkZGxlIiB4PSI4MTUuNSIgeT0iLTEzMyIgZm9udC1mYW1pbHk9IkRlamFWdSBTYW5zIiBmb250LXNpemU9IjEwLjAwIj5TZXNzaW9uIG1pcnJvciArIHBlcnNpc3RlbmNlPC90ZXh0Pgo8dGV4dCB0ZXh0LWFuY2hvcj0ibWlkZGxlIiB4PSI4MTUuNSIgeT0iLTEyMiIgZm9udC1mYW1pbHk9IkRlamFWdSBTYW5zIiBmb250LXNpemU9IjEwLjAwIj5maW5hbCB0cmFuc2NyaXB0cyBhbmQgc3RhYmxlIGJhcnJpZXJzPC90ZXh0Pgo8L2c+CjwhLS0gc2lkZWJhbmQmIzQ1OyZndDtwZXJzaXN0IC0tPgo8ZyBpZD0iZWRnZTMiIGNsYXNzPSJlZGdlIj4KPHRpdGxlPnNpZGViYW5kJiM0NTsmZ3Q7cGVyc2lzdDwvdGl0bGU+CjxwYXRoIGZpbGw9Im5vbmUiIHN0cm9rZT0iIzUzNmI3YSIgc3Ryb2tlLXdpZHRoPSIxLjQiIGQ9Ik01ODcuMjEsLTEzMEM2MjYuNDUsLTEzMCA2NzAuOTYsLTEzMCA3MTAuMTIsLTEzMCIvPgo8cG9seWdvbiBmaWxsPSIjNTM2YjdhIiBzdHJva2U9IiM1MzZiN2EiIHN0cm9rZS13aWR0aD0iMS40IiBwb2ludHM9IjcxMC4zOCwtMTMyLjYzIDcxNy44OCwtMTMwIDcxMC4zOCwtMTI3LjM4IDcxMC4zOCwtMTMyLjYzIi8+Cjx0ZXh0IHRleHQtYW5jaG9yPSJtaWRkbGUiIHg9IjY1Mi41IiB5PSItMTMyLjgiIGZvbnQtZmFtaWx5PSJEZWphVnUgU2FucyIgZm9udC1zaXplPSI5LjAwIj5zdGFibGUgaXRlbXM8L3RleHQ+CjwvZz4KPCEtLSBldmVudHMgLS0+CjxnIGlkPSJub2RlNyIgY2xhc3M9Im5vZGUiPgo8dGl0bGU+ZXZlbnRzPC90aXRsZT4KPHBhdGggZmlsbD0iI2VlZjRmZiIgc3Ryb2tlPSIjMjQ0NDVmIiBzdHJva2Utd2lkdGg9IjEuMiIgZD0iTTg4OSwtMjI0Qzg4OSwtMjI0IDc0MiwtMjI0IDc0MiwtMjI0IDczNiwtMjI0IDczMCwtMjE4IDczMCwtMjEyIDczMCwtMjEyIDczMCwtMjAwIDczMCwtMjAwIDczMCwtMTk0IDczNiwtMTg4IDc0MiwtMTg4IDc0MiwtMTg4IDg4OSwtMTg4IDg4OSwtMTg4IDg5NSwtMTg4IDkwMSwtMTk0IDkwMSwtMjAwIDkwMSwtMjAwIDkwMSwtMjEyIDkwMSwtMjEyIDkwMSwtMjE4IDg5NSwtMjI0IDg4OSwtMjI0Ii8+Cjx0ZXh0IHRleHQtYW5jaG9yPSJtaWRkbGUiIHg9IjgxNS41IiB5PSItMjA5IiBmb250LWZhbWlseT0iRGVqYVZ1IFNhbnMiIGZvbnQtc2l6ZT0iMTAuMDAiPkNhbm9uaWNhbCBFdmVudFNpbms8L3RleHQ+Cjx0ZXh0IHRleHQtYW5jaG9yPSJtaWRkbGUiIHg9IjgxNS41IiB5PSItMTk4IiBmb250LWZhbWlseT0iRGVqYVZ1IFNhbnMiIGZvbnQtc2l6ZT0iMTAuMDAiPnNlbWFudGljIGFuZCBsaWZlY3ljbGUgZXZlbnRzPC90ZXh0Pgo8L2c+CjwhLS0gc2lkZWJhbmQmIzQ1OyZndDtldmVudHMgLS0+CjxnIGlkPSJlZGdlNCIgY2xhc3M9ImVkZ2UiPgo8dGl0bGU+c2lkZWJhbmQmIzQ1OyZndDtldmVudHM8L3RpdGxlPgo8cGF0aCBmaWxsPSJub25lIiBzdHJva2U9IiM1MzZiN2EiIHN0cm9rZS13aWR0aD0iMS40IiBkPSJNNTYwLjgsLTE0OC4wMUM2MTEuMTMsLTE1OS41MiA2NzYuNDIsLTE3NC40NCA3MjguMTYsLTE4Ni4yNyIvPgo8cG9seWdvbiBmaWxsPSIjNTM2YjdhIiBzdHJva2U9IiM1MzZiN2EiIHN0cm9rZS13aWR0aD0iMS40IiBwb2ludHM9IjcyNy44LC0xODguODcgNzM1LjY5LC0xODcuOTkgNzI4Ljk3LC0xODMuNzYgNzI3LjgsLTE4OC44NyIvPgo8dGV4dCB0ZXh0LWFuY2hvcj0ibWlkZGxlIiB4PSI2NTIuNSIgeT0iLTE3OS44IiBmb250LWZhbWlseT0iRGVqYVZ1IFNhbnMiIGZvbnQtc2l6ZT0iOS4wMCI+bWFwcGVkIGV2ZW50czwvdGV4dD4KPC9nPgo8IS0tIHNpZGViYW5kJiM0NTsmZ3Q7Y2FsbCAtLT4KPGcgaWQ9ImVkZ2U4IiBjbGFzcz0iZWRnZSI+Cjx0aXRsZT5zaWRlYmFuZDplJiM0NTsmZ3Q7Y2FsbDp3PC90aXRsZT4KPHBhdGggZmlsbD0ibm9uZSIgc3Ryb2tlPSIjMmE3ZjYyIiBzdHJva2Utd2lkdGg9IjIiIGQ9Ik01OTQuNDUsLTEzMC45N0M2MTUuNDgsLTEzNy40IDU5Ny4yMiwtMTc0LjIxIDYxNiwtMTk3IDY0MS4wMSwtMjI3LjM1IDY1Ni43MiwtMjI0LjU0IDY4OSwtMjQ3IDcwOC43OCwtMjYwLjc3IDcxMS4yMiwtMjc3LjkxIDczMC44LC0yODEuMzciLz4KPHBvbHlnb24gZmlsbD0iIzJhN2Y2MiIgc3Ryb2tlPSIjMmE3ZjYyIiBzdHJva2Utd2lkdGg9IjIiIHBvaW50cz0iNTk0Ljc4LC0xMjguMzcgNTg3LC0xMzAgNTk0LjEsLTEzMy41NyA1OTQuNzgsLTEyOC4zNyIvPgo8cG9seWdvbiBmaWxsPSIjMmE3ZjYyIiBzdHJva2U9IiMyYTdmNjIiIHN0cm9rZS13aWR0aD0iMiIgcG9pbnRzPSI3MzAuODEsLTI4NC4wMSA3MzguNSwtMjgyIDczMS4yNCwtMjc4Ljc4IDczMC44MSwtMjg0LjAxIi8+CjwvZz4KPC9nPgo8L3N2Zz4K">

The media plane and control plane are intentionally separate:

- **Media plane:** browser microphone and speaker audio over WebRTC directly to the OpenAI Realtime call.
- **Bootstrap plane:** a short authenticated HTTP exchange with Geppetto, using either the unified SDP interface or a short-lived client secret.
- **Control plane:** a Geppetto sideband WebSocket attached by OpenAI `call_id`, used for session updates, tool execution, canonical event mapping, metrics, and persistence.
- **Durable plane:** only stable semantic state is written to Geppetto Turns. Raw audio deltas and partial provider events are not treated as durable conversation state.

## Main design decisions

| Decision | Recommendation | Reason |
|---|---|---|
| Public abstraction | Add `live.Session` / `live.Controller` | A Realtime call is not one finite inference. |
| Browser transport | Direct WebRTC | Lowest implementation burden and best browser media behavior. |
| Backend role | Bootstrap + sideband | Keeps keys/tools private without proxying audio. |
| Strict client isolation | Backend-owned WebSocket proxy when required | Direct browser sessions give the client protocol access; instructions are not an authorization boundary. |
| Tool execution | Existing registry/executor through a new reliable `ToolDispatcher` | Reuse schemas and execution, but not the finite `toolloop.Loop` orchestrator. |
| Events | Reuse canonical events; add live/audio lifecycle events | Preserves observability and JS integration. |
| Raw audio | Never through default `EventSink` | Prevents high-volume copies, memory pressure, and accidental logging. |
| Persistence | Final transcripts, completed items, tool barriers, close snapshots | Partial deltas are reorderable and interruption-sensitive. |
| Voice product modes | `native_realtime` and `chained` | Natural low latency versus explicit text control and existing-agent reuse. |
| Model selection | Configuration profile, not a hard-coded string | Current docs use both model families and point releases; the surface will change. |

# Contents {#contents}

1. [Scope, method, and limitations](#scope-method-and-limitations)
2. [What the existing Geppetto architecture provides](#existing-geppetto-architecture)
3. [How the OpenAI Realtime API behaves](#openai-realtime-behavior)
4. [Browser-to-API transport study](#transport-study)
5. [Recommended target architecture](#recommended-target-architecture)
6. [Supporting both native and chained voice](#native-and-chained)
7. [Detailed Go package and interface design](#go-design)
8. [Browser client design](#browser-client-design)
9. [Backend endpoint and sideband design](#backend-design)
10. [Events, correlation, tools, and persistence](#events-tools-persistence)
11. [Security and privacy model](#security-and-privacy)
12. [Reliability, interruption, and long-session behavior](#reliability)
13. [Observability, capacity, and cost](#observability-cost)
14. [Testing strategy](#testing)
15. [Incremental rollout plan](#rollout)
16. [Decision record and implementation checklist](#decision-record)
17. [Appendices and references](#appendices)



# 1. Scope, method, and limitations {#scope-method-and-limitations}

## 1.1 Questions studied

This report addresses four linked questions:

- How should OpenAI Realtime audio fit into the uploaded Geppetto codebase?
- Which existing session and streaming-event concepts can be reused, and where are new abstractions required?
- How can a browser stream microphone audio to the API, and when must audio pass through an application backend?
- How should the design handle tools, security, persistence, interruption, observability, testing, and migration?

## 1.2 Review method

The analysis combined:

1. Static inspection of the uploaded repository, including engine, session, event, Turn, tool-loop, OpenAI adapter, settings, transcription, and JavaScript module code.
2. Review of the repository's design notes for the session-centered JavaScript API and streaming EventEmitter work.
3. Review of current official OpenAI documentation for WebRTC, WebSocket, client secrets, sideband control, conversation events, VAD, transcription, voice architectures, models, and costs.
4. Architectural comparison of direct WebRTC, unified SDP bootstrap, direct browser WebSocket, backend WebSocket media proxy, and chained voice.

The archive contains 2,286 files, including 503 Go files and 1,444 Markdown files. It does not contain `.git` metadata, so no commit hash could be identified.

## 1.3 Validation limitation

A full `go test ./...` run could not be completed in the isolated environment because `go.mod` requests Go toolchain `go1.26.5`, which the local Go command attempted to download, and network access was unavailable. Static review also found imports/references to `pkg/inference/toolloop/enginebuilder`, while that package directory is absent from the supplied archive. These facts are baseline caveats, not evidence that the proposed design or the rest of the codebase fails to compile in its normal development environment.

## 1.4 Source notation

- Repository citations use `path:line-line`, based on the supplied archive.
- OpenAI citations such as [OAI-WEBRTC] refer to official documentation listed in the References section.
- Statements labeled **recommendation** or **inference** are architectural judgments derived from the reviewed sources rather than claims made by those sources.



# 2. What the existing Geppetto architecture provides {#existing-geppetto-architecture}

## 2.1 The current engine is deliberately finite

`pkg/inference/engine/engine.go:9-15` defines:

```go
type Engine interface {
    RunInference(ctx context.Context, t *turns.Turn) (*turns.Turn, error)
}
```

The comments are explicit: an engine processes a Turn, returns an updated Turn, and does not own tool orchestration. The Chat Completions and Responses adapters may consume provider streaming internally, but their public behavior is still finite: start one provider call, reduce deltas, and return a final Turn.

This is a good abstraction for text and batch-like inference. It is a poor lifecycle match for Realtime because a Realtime connection:

- remains open across many speech turns;
- accepts commands at arbitrary times;
- emits server events independently of a single method invocation;
- can have overlapping response, transcript, and tool streams;
- supports interruptions and mutable session configuration;
- terminates due to explicit close, connection failure, policy, or maximum session age rather than completion of one response.

**Conclusion:** do not add an `OpenAIRealtimeEngine` that blocks inside `RunInference` for the lifetime of a call, and do not redefine `RunInference` to sometimes mean one response and sometimes mean one hour-long duplex session.

## 2.2 The current Session is valuable, but its active unit is one inference

`pkg/inference/session/session.go:21-35` gives Geppetto a stable `SessionID`, append-only Turn snapshots, and an invariant of one active inference. `AppendNewTurnFromUserPrompts` clones the latest Turn and assigns a new Turn ID (`session.go:53-103`). `StartInference` builds one blocking runner, launches it in a goroutine, and returns an `ExecutionHandle` (`session.go:189-281`).

`pkg/inference/session/execution.go:13-84` confirms that the handle represents one in-flight inference with `Cancel`, `Wait`, and `IsRunning`.

These semantics should remain intact for text agents and chained voice. Native Realtime needs a sibling abstraction with a different active-unit invariant:

- one active provider connection per live session;
- zero or one active default-conversation response at a time in the common case;
- potentially multiple out-of-band responses;
- independent transcript and tool operations;
- explicit connection state and terminal error.

The existing `SessionID` should still be the canonical Geppetto identifier. A live session can produce stable Turn snapshots at semantic barriers, but should not append a new Turn for every protocol delta.

## 2.3 The event system is a strong reuse point

`pkg/events/sink.go:3-18` describes `EventSink` as the integration point for streaming deltas, WebSocket broadcasts, logs, traces, and metrics. It also warns against constructing durable state from partial events. `pkg/events/context.go:15-48` fans events out on a best-effort basis and ignores sink errors. `pkg/events/correlation.go:3-20` provides canonical IDs:

- `SessionID`
- `RunID`
- `TurnID`
- `ProviderCallID`
- `SegmentID`
- `ToolCallID`

The correlation comments correctly state that provider-native response/item IDs belong in adapter state or debug payloads, not as canonical routing keys.

This is almost exactly what Realtime needs for semantic observability. It is not sufficient for control. Since sinks are best-effort, a tool result or `conversation.item.truncate` command must never depend on an event consumer successfully receiving an `EventSink` event. The live subsystem therefore needs two paths:

- **reliable internal command/effect path** for protocol correctness;
- **best-effort canonical event path** for UI, telemetry, logs, and subscribers.

## 2.4 The Turn model is text/tool oriented

`pkg/turns/block_kind_gen.go:13-21` defines user text, LLM text, tool call/use, system, reasoning, and other blocks. `pkg/turns/helpers_blocks.go:14-40` supports text and images, but not audio. `Turn.Clone` copies block metadata and payload maps only shallowly for nested values (`pkg/turns/types.go:28-62`).

The initial implementation should not introduce raw audio blocks. Raw PCM/Base64 would make Turns huge, leak sensitive media into ordinary persistence/logging, and interact badly with shallow nested values. If recording is later required, store an immutable external media reference:

```go
type MediaRef struct {
    URI            string
    MIMEType       string
    SHA256         string
    DurationMS     int64
    SampleRate     int
    Channels       int
    ProviderItemID string // provenance/debug only
}
```

A transcript block may carry a `MediaRef` as metadata, but the Turn itself should store semantic content, not the byte stream.

## 2.5 Tool infrastructure is reusable; the current loop is not

`pkg/inference/toolloop/loop.go:92-174` repeatedly invokes a finite engine, extracts tool calls, executes them, appends tool results, and invokes the model again. That orchestration cannot own a Realtime call because the provider session itself already owns the conversation and response lifecycle.

The following parts remain valuable:

- thread-safe tool registry (`pkg/inference/tools/registry.go`);
- tool executor interface (`pkg/inference/tools/executor.go`);
- JSON schema generation and definitions;
- canonical tool events;
- authorization/deadline middleware that exists around tool execution.

A new `live.ToolDispatcher` should consume provider function-call events, execute through the existing registry/executor, and send the result back over the live transport.

## 2.6 Settings and factory boundaries should stay explicit

`pkg/inference/engine/factory/factory.go:105-197` returns finite engines for Chat, Responses, Claude, and Gemini. `pkg/steps/ai/settings/settings-chat.go:22-61` has a `Stream` flag, but this means streaming one HTTP response, not opening a duplex media session.

Adding a branch to `EngineFactory` based on `ApiTypeOpenAIRealtime` would create a return-type mismatch. The better separation is:

```text
EngineFactory       -> finite engine.Engine
LiveSessionFactory  -> long-lived live.Controller / live.Session
```

A Realtime API type may still be useful for profile selection and CLI/config parsing, but it should not imply that Realtime implements `engine.Engine`.

## 2.7 Existing transcription code is not live microphone streaming

`pkg/steps/ai/openai/transcribe.go:300-459` uses the legacy file-transcription client. Its so-called streaming mode reads chunks from a file and submits separate transcription requests. That is not equivalent to a persistent Realtime transcription session, does not provide browser microphone transport, and may split encoded container data at unsafe byte boundaries.

For chained voice, add a real Realtime transcription transport based on the current transcription session API. OpenAI's current guide uses a transcription session, streams `input_audio_buffer.append`, and emits incremental and completed transcript events. [OAI-TRANSCRIPTION]



# 3. How the OpenAI Realtime API behaves {#openai-realtime-behavior}

## 3.1 Session, Conversation, Items, and Responses

The provider model is not “one request.” A Realtime Session contains:

- a mutable Session configuration;
- a Conversation containing user/model Items;
- Responses that generate audio or text Items;
- an input audio buffer when using WebSocket or explicit buffer control;
- function-call Items and function-call-output Items;
- lifecycle, transcript, rate-limit, and error events.

The server sends `session.created`, accepts `session.update`, and sends `session.updated`. Most settings can change while connected, but the output voice cannot change after the model has emitted audio. Current documentation caps a Realtime session at 60 minutes. [OAI-CONVERSATIONS]

This provider lifecycle implies a long-lived reducer, not a method that reduces one SSE response.

## 3.2 WebRTC separates media tracks from JSON events

In a browser WebRTC topology:

- the microphone is obtained with `navigator.mediaDevices.getUserMedia`;
- its audio track is added to `RTCPeerConnection`;
- model speech arrives as a remote audio track;
- a WebRTC data channel carries JSON client/server events;
- WebRTC and the service handle media packetization, timing, congestion behavior, and output buffering.

OpenAI recommends WebRTC rather than WebSocket for browser/mobile clients. [OAI-WEBRTC]

## 3.3 WebSocket exposes the low-level audio protocol

Over WebSocket, the application must:

- convert input to a configured audio format;
- Base64-encode chunks into `input_audio_buffer.append` JSON events;
- commit the buffer manually when VAD is disabled;
- receive Base64 audio bytes from `response.output_audio.delta`;
- buffer and schedule playback;
- stop playback on interruption;
- track how much audio actually played;
- send `conversation.item.truncate` with `audio_end_ms` so unplayed speech is removed from conversation state.

OpenAI explicitly notes that `response.output_audio.done` and `response.done` do not contain the audio bytes. [OAI-CONVERSATIONS]

## 3.4 VAD and response control

VAD is enabled by default for supported speech-to-speech sessions. Current modes are:

- `server_vad`: detects speech boundaries from audio activity;
- `semantic_vad`: estimates whether the user has semantically completed the utterance, often improving natural turn-taking at some latency cost;
- `null`: disables turn detection, requiring manual commit and response creation.

The API emits `input_audio_buffer.speech_started` and `input_audio_buffer.speech_stopped`. It can also retain VAD events while disabling automatic response creation, which is useful when Geppetto must run moderation, retrieval, or policy checks before allowing a response. [OAI-VAD] [OAI-CLIENT-SECRETS]

## 3.5 Transcripts have different authority levels

There are two important transcript classes:

- **output audio transcript:** transcript associated with model speech;
- **input audio transcription:** a separate asynchronous transcription of user audio.

The input transcription is not the native model's internal audio understanding and should be treated as guidance rather than a byte-for-byte or semantic guarantee of what the model heard. [OAI-CLIENT-SECRETS]

This matters for persistence and audits. Geppetto should store transcript source metadata and avoid claiming that a user transcript is the exact model input interpretation.

## 3.6 Function calls form an event-driven loop

When the model emits a function call, the application executes it and sends:

1. `conversation.item.create` with `item.type = "function_call_output"`, the same `call_id`, and a JSON string output;
2. `response.create` to ask the model to continue.

This is analogous to the existing tool loop, but the orchestration lives inside the ongoing Realtime session. [OAI-CONVERSATIONS]

## 3.7 Events can be concurrent and out of order

Delta streams for audio, text, transcript, and function arguments can overlap. Completion events for different transcription turns are not guaranteed to arrive in order; the official transcription guide requires matching by `item_id`. [OAI-TRANSCRIPTION]

Therefore the adapter must index provider-native state by session/call/response/item/content IDs internally, while mapping only stable semantic events to Geppetto's canonical IDs.



# 4. Browser-to-API transport study {#transport-study}

<img class="diagram-img" alt="Comparison of Realtime transport topologies" src="data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiIHN0YW5kYWxvbmU9Im5vIj8+CjwhRE9DVFlQRSBzdmcgUFVCTElDICItLy9XM0MvL0RURCBTVkcgMS4xLy9FTiIKICJodHRwOi8vd3d3LnczLm9yZy9HcmFwaGljcy9TVkcvMS4xL0RURC9zdmcxMS5kdGQiPgo8IS0tIEdlbmVyYXRlZCBieSBncmFwaHZpeiB2ZXJzaW9uIDIuNDIuNCAoMCkKIC0tPgo8IS0tIFRpdGxlOiBHIFBhZ2VzOiAxIC0tPgo8c3ZnIHdpZHRoPSI0MzVwdCIgaGVpZ2h0PSI5ODJwdCIKIHZpZXdCb3g9IjAuMDAgMC4wMCA0MzUuMDAgOTgyLjAwIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIj4KPGcgaWQ9ImdyYXBoMCIgY2xhc3M9ImdyYXBoIiB0cmFuc2Zvcm09InNjYWxlKDEgMSkgcm90YXRlKDApIHRyYW5zbGF0ZSgxOCA5NjQpIj4KPHRpdGxlPkc8L3RpdGxlPgo8ZyBpZD0iY2x1c3QxIiBjbGFzcz0iY2x1c3RlciI+Cjx0aXRsZT5jbHVzdGVyX2E8L3RpdGxlPgo8cGF0aCBmaWxsPSJ0cmFuc3BhcmVudCIgc3Ryb2tlPSIjNjVhNmM1IiBkPSJNNTQuNSwtNzIxQzU0LjUsLTcyMSAzMTQuNSwtNzIxIDMxNC41LC03MjEgMzIwLjUsLTcyMSAzMjYuNSwtNzI3IDMyNi41LC03MzMgMzI2LjUsLTczMyAzMjYuNSwtODY5IDMyNi41LC04NjkgMzI2LjUsLTg3NSAzMjAuNSwtODgxIDMxNC41LC04ODEgMzE0LjUsLTg4MSA1NC41LC04ODEgNTQuNSwtODgxIDQ4LjUsLTg4MSA0Mi41LC04NzUgNDIuNSwtODY5IDQyLjUsLTg2OSA0Mi41LC03MzMgNDIuNSwtNzMzIDQyLjUsLTcyNyA0OC41LC03MjEgNTQuNSwtNzIxIi8+Cjx0ZXh0IHRleHQtYW5jaG9yPSJtaWRkbGUiIHg9IjE4NC41IiB5PSItODY1LjgiIGZvbnQtZmFtaWx5PSJEZWphVnUgU2FucyIgZm9udC1zaXplPSIxNC4wMCI+QS4gRGlyZWN0IFdlYlJUQyArIHNpZGViYW5kIChkZWZhdWx0KTwvdGV4dD4KPC9nPgo8ZyBpZD0iY2x1c3QyIiBjbGFzcz0iY2x1c3RlciI+Cjx0aXRsZT5jbHVzdGVyX2I8L3RpdGxlPgo8cGF0aCBmaWxsPSJ0cmFuc3BhcmVudCIgc3Ryb2tlPSIjNjVhNmM1IiBkPSJNMzQuNSwtNDU1QzM0LjUsLTQ1NSAzMTguNSwtNDU1IDMxOC41LC00NTUgMzI0LjUsLTQ1NSAzMzAuNSwtNDYxIDMzMC41LC00NjcgMzMwLjUsLTQ2NyAzMzAuNSwtNjg4IDMzMC41LC02ODggMzMwLjUsLTY5NCAzMjQuNSwtNzAwIDMxOC41LC03MDAgMzE4LjUsLTcwMCAzNC41LC03MDAgMzQuNSwtNzAwIDI4LjUsLTcwMCAyMi41LC02OTQgMjIuNSwtNjg4IDIyLjUsLTY4OCAyMi41LC00NjcgMjIuNSwtNDY3IDIyLjUsLTQ2MSAyOC41LC00NTUgMzQuNSwtNDU1Ii8+Cjx0ZXh0IHRleHQtYW5jaG9yPSJtaWRkbGUiIHg9IjE3Ni41IiB5PSItNjg0LjgiIGZvbnQtZmFtaWx5PSJEZWphVnUgU2FucyIgZm9udC1zaXplPSIxNC4wMCI+Qi4gVW5pZmllZCBTRFAgYm9vdHN0cmFwPC90ZXh0Pgo8L2c+CjxnIGlkPSJjbHVzdDMiIGNsYXNzPSJjbHVzdGVyIj4KPHRpdGxlPmNsdXN0ZXJfYzwvdGl0bGU+CjxwYXRoIGZpbGw9InRyYW5zcGFyZW50IiBzdHJva2U9IiNiMDhiNTIiIGQ9Ik02Mi41LC0xODlDNjIuNSwtMTg5IDMxMS41LC0xODkgMzExLjUsLTE4OSAzMTcuNSwtMTg5IDMyMy41LC0xOTUgMzIzLjUsLTIwMSAzMjMuNSwtMjAxIDMyMy41LC00MjIgMzIzLjUsLTQyMiAzMjMuNSwtNDI4IDMxNy41LC00MzQgMzExLjUsLTQzNCAzMTEuNSwtNDM0IDYyLjUsLTQzNCA2Mi41LC00MzQgNTYuNSwtNDM0IDUwLjUsLTQyOCA1MC41LC00MjIgNTAuNSwtNDIyIDUwLjUsLTIwMSA1MC41LC0yMDEgNTAuNSwtMTk1IDU2LjUsLTE4OSA2Mi41LC0xODkiLz4KPHRleHQgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iMTg3IiB5PSItNDE4LjgiIGZvbnQtZmFtaWx5PSJEZWphVnUgU2FucyIgZm9udC1zaXplPSIxNC4wMCI+Qy4gQmFja2VuZCYjNDU7b3duZWQgV2ViU29ja2V0IG1lZGlhPC90ZXh0Pgo8L2c+CjxnIGlkPSJjbHVzdDQiIGNsYXNzPSJjbHVzdGVyIj4KPHRpdGxlPmNsdXN0ZXJfZDwvdGl0bGU+CjxwYXRoIGZpbGw9InRyYW5zcGFyZW50IiBzdHJva2U9IiNjMDZiNmIiIGQ9Ik02OC41LC04QzY4LjUsLTggMjYxLjUsLTggMjYxLjUsLTggMjY3LjUsLTggMjczLjUsLTE0IDI3My41LC0yMCAyNzMuNSwtMjAgMjczLjUsLTE1NiAyNzMuNSwtMTU2IDI3My41LC0xNjIgMjY3LjUsLTE2OCAyNjEuNSwtMTY4IDI2MS41LC0xNjggNjguNSwtMTY4IDY4LjUsLTE2OCA2Mi41LC0xNjggNTYuNSwtMTYyIDU2LjUsLTE1NiA1Ni41LC0xNTYgNTYuNSwtMjAgNTYuNSwtMjAgNTYuNSwtMTQgNjIuNSwtOCA2OC41LC04Ii8+Cjx0ZXh0IHRleHQtYW5jaG9yPSJtaWRkbGUiIHg9IjE2NSIgeT0iLTE1Mi44IiBmb250LWZhbWlseT0iRGVqYVZ1IFNhbnMiIGZvbnQtc2l6ZT0iMTQuMDAiPkQuIERpcmVjdCBicm93c2VyIFdlYlNvY2tldDwvdGV4dD4KPC9nPgo8IS0tIHRpdGxlIC0tPgo8ZyBpZD0ibm9kZTEiIGNsYXNzPSJub2RlIj4KPHRpdGxlPnRpdGxlPC90aXRsZT4KPHRleHQgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iMTk5LjUiIHk9Ii05MjQuNiIgZm9udC1mYW1pbHk9IkRlamFWdSBTYW5zIiBmb250LXNpemU9IjEzLjAwIiBmaWxsPSIjMGYyNDM4Ij5UcmFuc3BvcnQgdG9wb2xvZ2llcyBhbmQgdGhlaXIgb3BlcmF0aW9uYWwgY29uc2VxdWVuY2VzPC90ZXh0Pgo8L2c+CjwhLS0gYTEgLS0+CjxnIGlkPSJub2RlMiIgY2xhc3M9Im5vZGUiPgo8dGl0bGU+YTE8L3RpdGxlPgo8cGF0aCBmaWxsPSIjZWFmM2Y4IiBzdHJva2U9IiMyNDQ0NWYiIGQ9Ik0yMTcuNSwtODUwQzIxNy41LC04NTAgMTgxLjUsLTg1MCAxODEuNSwtODUwIDE3NS41LC04NTAgMTY5LjUsLTg0NCAxNjkuNSwtODM4IDE2OS41LC04MzggMTY5LjUsLTgyNiAxNjkuNSwtODI2IDE2OS41LC04MjAgMTc1LjUsLTgxNCAxODEuNSwtODE0IDE4MS41LC04MTQgMjE3LjUsLTgxNCAyMTcuNSwtODE0IDIyMy41LC04MTQgMjI5LjUsLTgyMCAyMjkuNSwtODI2IDIyOS41LC04MjYgMjI5LjUsLTgzOCAyMjkuNSwtODM4IDIyOS41LC04NDQgMjIzLjUsLTg1MCAyMTcuNSwtODUwIi8+Cjx0ZXh0IHRleHQtYW5jaG9yPSJtaWRkbGUiIHg9IjE5OS41IiB5PSItODI5LjQiIGZvbnQtZmFtaWx5PSJEZWphVnUgU2FucyIgZm9udC1zaXplPSI5LjUwIj5Ccm93c2VyPC90ZXh0Pgo8L2c+CjwhLS0gdGl0bGUmIzQ1OyZndDthMSAtLT4KPCEtLSBhMiAtLT4KPGcgaWQ9Im5vZGUzIiBjbGFzcz0ibm9kZSI+Cjx0aXRsZT5hMjwvdGl0bGU+CjxwYXRoIGZpbGw9IiNlNGY1ZWQiIHN0cm9rZT0iIzI0NDQ1ZiIgZD0iTTE0Mi41LC03NjVDMTQyLjUsLTc2NSA3MC41LC03NjUgNzAuNSwtNzY1IDY0LjUsLTc2NSA1OC41LC03NTkgNTguNSwtNzUzIDU4LjUsLTc1MyA1OC41LC03NDEgNTguNSwtNzQxIDU4LjUsLTczNSA2NC41LC03MjkgNzAuNSwtNzI5IDcwLjUsLTcyOSAxNDIuNSwtNzI5IDE0Mi41LC03MjkgMTQ4LjUsLTcyOSAxNTQuNSwtNzM1IDE1NC41LC03NDEgMTU0LjUsLTc0MSAxNTQuNSwtNzUzIDE1NC41LC03NTMgMTU0LjUsLTc1OSAxNDguNSwtNzY1IDE0Mi41LC03NjUiLz4KPHRleHQgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iMTA2LjUiIHk9Ii03NDkuNCIgZm9udC1mYW1pbHk9IkRlamFWdSBTYW5zIiBmb250LXNpemU9IjkuNTAiPk9wZW5BSTwvdGV4dD4KPHRleHQgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iMTA2LjUiIHk9Ii03MzkuNCIgZm9udC1mYW1pbHk9IkRlamFWdSBTYW5zIiBmb250LXNpemU9IjkuNTAiPm1lZGlhIGVuZHBvaW50PC90ZXh0Pgo8L2c+CjwhLS0gYTEmIzQ1OyZndDthMiAtLT4KPGcgaWQ9ImVkZ2UxIiBjbGFzcz0iZWRnZSI+Cjx0aXRsZT5hMSYjNDU7Jmd0O2EyPC90aXRsZT4KPHBhdGggZmlsbD0ibm9uZSIgc3Ryb2tlPSIjMWU2ZjlmIiBzdHJva2Utd2lkdGg9IjIiIGQ9Ik0xODAuMjMsLTgxMy44QzE2Ni4wMSwtODAxLjEyIDE0Ni41NiwtNzgzLjc1IDEzMS4yLC03NzAuMDQiLz4KPHBvbHlnb24gZmlsbD0iIzFlNmY5ZiIgc3Ryb2tlPSIjMWU2ZjlmIiBzdHJva2Utd2lkdGg9IjIiIHBvaW50cz0iMTMyLjYsLTc2OC4wMSAxMjUuNzQsLTc2NS4xOCAxMjkuMzQsLTc3MS42NiAxMzIuNiwtNzY4LjAxIi8+Cjx0ZXh0IHRleHQtYW5jaG9yPSJtaWRkbGUiIHg9IjIwMi41IiB5PSItNzg3LjIiIGZvbnQtZmFtaWx5PSJEZWphVnUgU2FucyIgZm9udC1zaXplPSI4LjUwIj5tZWRpYSArIGNsaWVudCBldmVudHM8L3RleHQ+CjwvZz4KPCEtLSBiMSAtLT4KPGcgaWQ9Im5vZGU1IiBjbGFzcz0ibm9kZSI+Cjx0aXRsZT5iMTwvdGl0bGU+CjxwYXRoIGZpbGw9IiNlYWYzZjgiIHN0cm9rZT0iIzI0NDQ1ZiIgZD0iTTEyNC41LC02NjlDMTI0LjUsLTY2OSA4OC41LC02NjkgODguNSwtNjY5IDgyLjUsLTY2OSA3Ni41LC02NjMgNzYuNSwtNjU3IDc2LjUsLTY1NyA3Ni41LC02NDUgNzYuNSwtNjQ1IDc2LjUsLTYzOSA4Mi41LC02MzMgODguNSwtNjMzIDg4LjUsLTYzMyAxMjQuNSwtNjMzIDEyNC41LC02MzMgMTMwLjUsLTYzMyAxMzYuNSwtNjM5IDEzNi41LC02NDUgMTM2LjUsLTY0NSAxMzYuNSwtNjU3IDEzNi41LC02NTcgMTM2LjUsLTY2MyAxMzAuNSwtNjY5IDEyNC41LC02NjkiLz4KPHRleHQgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iMTA2LjUiIHk9Ii02NDguNCIgZm9udC1mYW1pbHk9IkRlamFWdSBTYW5zIiBmb250LXNpemU9IjkuNTAiPkJyb3dzZXI8L3RleHQ+CjwvZz4KPCEtLSBhMiYjNDU7Jmd0O2IxIC0tPgo8IS0tIGEzIC0tPgo8ZyBpZD0ibm9kZTQiIGNsYXNzPSJub2RlIj4KPHRpdGxlPmEzPC90aXRsZT4KPHBhdGggZmlsbD0iI2VlZjRmZiIgc3Ryb2tlPSIjMjQ0NDVmIiBkPSJNMTI1LjUsLTg1MEMxMjUuNSwtODUwIDY1LjUsLTg1MCA2NS41LC04NTAgNTkuNSwtODUwIDUzLjUsLTg0NCA1My41LC04MzggNTMuNSwtODM4IDUzLjUsLTgyNiA1My41LC04MjYgNTMuNSwtODIwIDU5LjUsLTgxNCA2NS41LC04MTQgNjUuNSwtODE0IDEyNS41LC04MTQgMTI1LjUsLTgxNCAxMzEuNSwtODE0IDEzNy41LC04MjAgMTM3LjUsLTgyNiAxMzcuNSwtODI2IDEzNy41LC04MzggMTM3LjUsLTgzOCAxMzcuNSwtODQ0IDEzMS41LC04NTAgMTI1LjUsLTg1MCIvPgo8dGV4dCB0ZXh0LWFuY2hvcj0ibWlkZGxlIiB4PSI5NS41IiB5PSItODM0LjQiIGZvbnQtZmFtaWx5PSJEZWphVnUgU2FucyIgZm9udC1zaXplPSI5LjUwIj5HZXBwZXR0bzwvdGV4dD4KPHRleHQgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iOTUuNSIgeT0iLTgyNC40IiBmb250LWZhbWlseT0iRGVqYVZ1IFNhbnMiIGZvbnQtc2l6ZT0iOS41MCI+Y29udHJvbCBwbGFuZTwvdGV4dD4KPC9nPgo8IS0tIGEzJiM0NTsmZ3Q7YTIgLS0+CjxnIGlkPSJlZGdlMiIgY2xhc3M9ImVkZ2UiPgo8dGl0bGU+YTMmIzQ1OyZndDthMjwvdGl0bGU+CjxwYXRoIGZpbGw9Im5vbmUiIHN0cm9rZT0iIzJhN2Y2MiIgc3Ryb2tlLXdpZHRoPSIxLjciIGQ9Ik05OC43MiwtODA2Ljc0QzEwMC4xNSwtNzk1LjkxIDEwMS44NCwtNzgzLjE3IDEwMy4yOCwtNzcyLjMzIi8+Cjxwb2x5Z29uIGZpbGw9IiMyYTdmNjIiIHN0cm9rZT0iIzJhN2Y2MiIgc3Ryb2tlLXdpZHRoPSIxLjciIHBvaW50cz0iOTYuMjcsLTgwNi41NCA5Ny43OCwtODEzLjggMTAxLjEzLC04MDcuMTggOTYuMjcsLTgwNi41NCIvPgo8cG9seWdvbiBmaWxsPSIjMmE3ZjYyIiBzdHJva2U9IiMyYTdmNjIiIHN0cm9rZS13aWR0aD0iMS43IiBwb2ludHM9IjEwNS43MywtNzcyLjQ0IDEwNC4yMiwtNzY1LjE4IDEwMC44OCwtNzcxLjc5IDEwNS43MywtNzcyLjQ0Ii8+Cjx0ZXh0IHRleHQtYW5jaG9yPSJtaWRkbGUiIHg9IjEyMCIgeT0iLTc4Ny4yIiBmb250LWZhbWlseT0iRGVqYVZ1IFNhbnMiIGZvbnQtc2l6ZT0iOC41MCI+c2lkZWJhbmQ8L3RleHQ+CjwvZz4KPCEtLSBiMiAtLT4KPGcgaWQ9Im5vZGU2IiBjbGFzcz0ibm9kZSI+Cjx0aXRsZT5iMjwvdGl0bGU+CjxwYXRoIGZpbGw9IiNlZWY0ZmYiIHN0cm9rZT0iIzI0NDQ1ZiIgZD0iTTE0NiwtNTg0QzE0NiwtNTg0IDQzLC01ODQgNDMsLTU4NCAzNywtNTg0IDMxLC01NzggMzEsLTU3MiAzMSwtNTcyIDMxLC01NjAgMzEsLTU2MCAzMSwtNTU0IDM3LC01NDggNDMsLTU0OCA0MywtNTQ4IDE0NiwtNTQ4IDE0NiwtNTQ4IDE1MiwtNTQ4IDE1OCwtNTU0IDE1OCwtNTYwIDE1OCwtNTYwIDE1OCwtNTcyIDE1OCwtNTcyIDE1OCwtNTc4IDE1MiwtNTg0IDE0NiwtNTg0Ii8+Cjx0ZXh0IHRleHQtYW5jaG9yPSJtaWRkbGUiIHg9Ijk0LjUiIHk9Ii01NjguNCIgZm9udC1mYW1pbHk9IkRlamFWdSBTYW5zIiBmb250LXNpemU9IjkuNTAiPkdlcHBldHRvPC90ZXh0Pgo8dGV4dCB0ZXh0LWFuY2hvcj0ibWlkZGxlIiB4PSI5NC41IiB5PSItNTU4LjQiIGZvbnQtZmFtaWx5PSJEZWphVnUgU2FucyIgZm9udC1zaXplPSI5LjUwIj5pbml0aWFsaXphdGlvbiBlbmRwb2ludDwvdGV4dD4KPC9nPgo8IS0tIGIxJiM0NTsmZ3Q7YjIgLS0+CjxnIGlkPSJlZGdlMyIgY2xhc3M9ImVkZ2UiPgo8dGl0bGU+YjEmIzQ1OyZndDtiMjwvdGl0bGU+CjxwYXRoIGZpbGw9Im5vbmUiIHN0cm9rZT0iIzUzNmI3YSIgZD0iTTEwNC4wMSwtNjMyLjhDMTAyLjI4LC02MjAuNzggOTkuOTMsLTYwNC41NyA5OCwtNTkxLjI0Ii8+Cjxwb2x5Z29uIGZpbGw9IiM1MzZiN2EiIHN0cm9rZT0iIzUzNmI3YSIgcG9pbnRzPSIxMDAuNDEsLTU5MC43NSA5Ni45OCwtNTg0LjE4IDk1LjU2LC01OTEuNDUgMTAwLjQxLC01OTAuNzUiLz4KPHRleHQgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iMTIxIiB5PSItNjA2LjIiIGZvbnQtZmFtaWx5PSJEZWphVnUgU2FucyIgZm9udC1zaXplPSI4LjUwIj5vZmZlciBTRFA8L3RleHQ+CjwvZz4KPCEtLSBiMyAtLT4KPGcgaWQ9Im5vZGU3IiBjbGFzcz0ibm9kZSI+Cjx0aXRsZT5iMzwvdGl0bGU+CjxwYXRoIGZpbGw9IiNlNGY1ZWQiIHN0cm9rZT0iIzI0NDQ1ZiIgZD0iTTE0OS41LC00OTlDMTQ5LjUsLTQ5OSA3Ny41LC00OTkgNzcuNSwtNDk5IDcxLjUsLTQ5OSA2NS41LC00OTMgNjUuNSwtNDg3IDY1LjUsLTQ4NyA2NS41LC00NzUgNjUuNSwtNDc1IDY1LjUsLTQ2OSA3MS41LC00NjMgNzcuNSwtNDYzIDc3LjUsLTQ2MyAxNDkuNSwtNDYzIDE0OS41LC00NjMgMTU1LjUsLTQ2MyAxNjEuNSwtNDY5IDE2MS41LC00NzUgMTYxLjUsLTQ3NSAxNjEuNSwtNDg3IDE2MS41LC00ODcgMTYxLjUsLTQ5MyAxNTUuNSwtNDk5IDE0OS41LC00OTkiLz4KPHRleHQgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iMTEzLjUiIHk9Ii00ODMuNCIgZm9udC1mYW1pbHk9IkRlamFWdSBTYW5zIiBmb250LXNpemU9IjkuNTAiPk9wZW5BSTwvdGV4dD4KPHRleHQgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iMTEzLjUiIHk9Ii00NzMuNCIgZm9udC1mYW1pbHk9IkRlamFWdSBTYW5zIiBmb250LXNpemU9IjkuNTAiPm1lZGlhIGVuZHBvaW50PC90ZXh0Pgo8L2c+CjwhLS0gYjImIzQ1OyZndDtiMyAtLT4KPGcgaWQ9ImVkZ2U0IiBjbGFzcz0iZWRnZSI+Cjx0aXRsZT5iMiYjNDU7Jmd0O2IzPC90aXRsZT4KPHBhdGggZmlsbD0ibm9uZSIgc3Ryb2tlPSIjNTM2YjdhIiBkPSJNOTguNDQsLTU0Ny44QzEwMS4xOSwtNTM1Ljc4IDEwNC45LC01MTkuNTcgMTA3Ljk1LC01MDYuMjQiLz4KPHBvbHlnb24gZmlsbD0iIzUzNmI3YSIgc3Ryb2tlPSIjNTM2YjdhIiBwb2ludHM9IjExMC4zOSwtNTA2LjU1IDEwOS41NywtNDk5LjE4IDEwNS42MiwtNTA1LjQ1IDExMC4zOSwtNTA2LjU1Ii8+Cjx0ZXh0IHRleHQtYW5jaG9yPSJtaWRkbGUiIHg9IjE1MyIgeT0iLTUyMS4yIiBmb250LWZhbWlseT0iRGVqYVZ1IFNhbnMiIGZvbnQtc2l6ZT0iOC41MCI+bXVsdGlwYXJ0IFNEUCArIHBvbGljeTwvdGV4dD4KPC9nPgo8IS0tIGIzJiM0NTsmZ3Q7YjEgLS0+CjxnIGlkPSJlZGdlNSIgY2xhc3M9ImVkZ2UiPgo8dGl0bGU+YjMmIzQ1OyZndDtiMTwvdGl0bGU+CjxwYXRoIGZpbGw9Im5vbmUiIHN0cm9rZT0iIzFlNmY5ZiIgc3Ryb2tlLXdpZHRoPSIyIiBkPSJNMTYxLjU3LC00ODYuOTJDMTg4LjksLTQ5Mi4zNyAyMTYuNDMsLTUwMy44NCAyMDkuNSwtNTI4IDE5Ny40OSwtNTY5Ljg2IDE2MS40MywtNjA2LjMgMTM1LjM2LC02MjguMTkiLz4KPHBvbHlnb24gZmlsbD0iIzFlNmY5ZiIgc3Ryb2tlPSIjMWU2ZjlmIiBzdHJva2Utd2lkdGg9IjIiIHBvaW50cz0iMTMzLjQ4LC02MjYuNTcgMTI5LjYzLC02MzIuOTEgMTM2LjU5LC02MzAuMzUgMTMzLjQ4LC02MjYuNTciLz4KPHRleHQgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iMjUwLjUiIHk9Ii01NjMuNyIgZm9udC1mYW1pbHk9IkRlamFWdSBTYW5zIiBmb250LXNpemU9IjguNTAiPmFuc3dlcjsgbWVkaWEgaXMgZGlyZWN0PC90ZXh0Pgo8L2c+CjwhLS0gYzEgLS0+CjxnIGlkPSJub2RlOCIgY2xhc3M9Im5vZGUiPgo8dGl0bGU+YzE8L3RpdGxlPgo8cGF0aCBmaWxsPSIjZmZmNWU1IiBzdHJva2U9IiMyNDQ0NWYiIGQ9Ik0xNDQsLTQwM0MxNDQsLTQwMyA4MywtNDAzIDgzLC00MDMgNzcsLTQwMyA3MSwtMzk3IDcxLC0zOTEgNzEsLTM5MSA3MSwtMzc5IDcxLC0zNzkgNzEsLTM3MyA3NywtMzY3IDgzLC0zNjcgODMsLTM2NyAxNDQsLTM2NyAxNDQsLTM2NyAxNTAsLTM2NyAxNTYsLTM3MyAxNTYsLTM3OSAxNTYsLTM3OSAxNTYsLTM5MSAxNTYsLTM5MSAxNTYsLTM5NyAxNTAsLTQwMyAxNDQsLTQwMyIvPgo8dGV4dCB0ZXh0LWFuY2hvcj0ibWlkZGxlIiB4PSIxMTMuNSIgeT0iLTM4Ny40IiBmb250LWZhbWlseT0iRGVqYVZ1IFNhbnMiIGZvbnQtc2l6ZT0iOS41MCI+QnJvd3NlcjwvdGV4dD4KPHRleHQgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iMTEzLjUiIHk9Ii0zNzcuNCIgZm9udC1mYW1pbHk9IkRlamFWdSBTYW5zIiBmb250LXNpemU9IjkuNTAiPkF1ZGlvV29ya2xldDwvdGV4dD4KPC9nPgo8IS0tIGIzJiM0NTsmZ3Q7YzEgLS0+CjwhLS0gYzIgLS0+CjxnIGlkPSJub2RlOSIgY2xhc3M9Im5vZGUiPgo8dGl0bGU+YzI8L3RpdGxlPgo8cGF0aCBmaWxsPSIjZmZmMGQ1IiBzdHJva2U9IiMyNDQ0NWYiIGQ9Ik0xNDcsLTMxOEMxNDcsLTMxOCA4MCwtMzE4IDgwLC0zMTggNzQsLTMxOCA2OCwtMzEyIDY4LC0zMDYgNjgsLTMwNiA2OCwtMjk0IDY4LC0yOTQgNjgsLTI4OCA3NCwtMjgyIDgwLC0yODIgODAsLTI4MiAxNDcsLTI4MiAxNDcsLTI4MiAxNTMsLTI4MiAxNTksLTI4OCAxNTksLTI5NCAxNTksLTI5NCAxNTksLTMwNiAxNTksLTMwNiAxNTksLTMxMiAxNTMsLTMxOCAxNDcsLTMxOCIvPgo8dGV4dCB0ZXh0LWFuY2hvcj0ibWlkZGxlIiB4PSIxMTMuNSIgeT0iLTMwMi40IiBmb250LWZhbWlseT0iRGVqYVZ1IFNhbnMiIGZvbnQtc2l6ZT0iOS41MCI+R2VwcGV0dG88L3RleHQ+Cjx0ZXh0IHRleHQtYW5jaG9yPSJtaWRkbGUiIHg9IjExMy41IiB5PSItMjkyLjQiIGZvbnQtZmFtaWx5PSJEZWphVnUgU2FucyIgZm9udC1zaXplPSI5LjUwIj5hdWRpbyBnYXRld2F5PC90ZXh0Pgo8L2c+CjwhLS0gYzEmIzQ1OyZndDtjMiAtLT4KPGcgaWQ9ImVkZ2U2IiBjbGFzcz0iZWRnZSI+Cjx0aXRsZT5jMSYjNDU7Jmd0O2MyPC90aXRsZT4KPHBhdGggZmlsbD0ibm9uZSIgc3Ryb2tlPSIjNTM2YjdhIiBkPSJNMTEzLjUsLTM1OS43NEMxMTMuNSwtMzQ4LjkxIDExMy41LC0zMzYuMTcgMTEzLjUsLTMyNS4zMyIvPgo8cG9seWdvbiBmaWxsPSIjNTM2YjdhIiBzdHJva2U9IiM1MzZiN2EiIHBvaW50cz0iMTExLjA1LC0zNTkuOCAxMTMuNSwtMzY2LjggMTE1Ljk1LC0zNTkuOCAxMTEuMDUsLTM1OS44Ii8+Cjxwb2x5Z29uIGZpbGw9IiM1MzZiN2EiIHN0cm9rZT0iIzUzNmI3YSIgcG9pbnRzPSIxMTUuOTUsLTMyNS4xOCAxMTMuNSwtMzE4LjE4IDExMS4wNSwtMzI1LjE4IDExNS45NSwtMzI1LjE4Ii8+Cjx0ZXh0IHRleHQtYW5jaG9yPSJtaWRkbGUiIHg9IjE1NC41IiB5PSItMzQwLjIiIGZvbnQtZmFtaWx5PSJEZWphVnUgU2FucyIgZm9udC1zaXplPSI4LjUwIj5iaW5hcnkgUENNIGZyYW1lczwvdGV4dD4KPC9nPgo8IS0tIGMzIC0tPgo8ZyBpZD0ibm9kZTEwIiBjbGFzcz0ibm9kZSI+Cjx0aXRsZT5jMzwvdGl0bGU+CjxwYXRoIGZpbGw9IiNlNGY1ZWQiIHN0cm9rZT0iIzI0NDQ1ZiIgZD0iTTEzOC41LC0yMzNDMTM4LjUsLTIzMyA4OC41LC0yMzMgODguNSwtMjMzIDgyLjUsLTIzMyA3Ni41LC0yMjcgNzYuNSwtMjIxIDc2LjUsLTIyMSA3Ni41LC0yMDkgNzYuNSwtMjA5IDc2LjUsLTIwMyA4Mi41LC0xOTcgODguNSwtMTk3IDg4LjUsLTE5NyAxMzguNSwtMTk3IDEzOC41LC0xOTcgMTQ0LjUsLTE5NyAxNTAuNSwtMjAzIDE1MC41LC0yMDkgMTUwLjUsLTIwOSAxNTAuNSwtMjIxIDE1MC41LC0yMjEgMTUwLjUsLTIyNyAxNDQuNSwtMjMzIDEzOC41LC0yMzMiLz4KPHRleHQgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iMTEzLjUiIHk9Ii0yMTcuNCIgZm9udC1mYW1pbHk9IkRlamFWdSBTYW5zIiBmb250LXNpemU9IjkuNTAiPk9wZW5BSTwvdGV4dD4KPHRleHQgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iMTEzLjUiIHk9Ii0yMDcuNCIgZm9udC1mYW1pbHk9IkRlamFWdSBTYW5zIiBmb250LXNpemU9IjkuNTAiPldlYlNvY2tldDwvdGV4dD4KPC9nPgo8IS0tIGMyJiM0NTsmZ3Q7YzMgLS0+CjxnIGlkPSJlZGdlNyIgY2xhc3M9ImVkZ2UiPgo8dGl0bGU+YzImIzQ1OyZndDtjMzwvdGl0bGU+CjxwYXRoIGZpbGw9Im5vbmUiIHN0cm9rZT0iIzUzNmI3YSIgZD0iTTExMy41LC0yNzQuNzRDMTEzLjUsLTI2My45MSAxMTMuNSwtMjUxLjE3IDExMy41LC0yNDAuMzMiLz4KPHBvbHlnb24gZmlsbD0iIzUzNmI3YSIgc3Ryb2tlPSIjNTM2YjdhIiBwb2ludHM9IjExMS4wNSwtMjc0LjggMTEzLjUsLTI4MS44IDExNS45NSwtMjc0LjggMTExLjA1LC0yNzQuOCIvPgo8cG9seWdvbiBmaWxsPSIjNTM2YjdhIiBzdHJva2U9IiM1MzZiN2EiIHBvaW50cz0iMTE1Ljk1LC0yNDAuMTggMTEzLjUsLTIzMy4xOCAxMTEuMDUsLTI0MC4xOCAxMTUuOTUsLTI0MC4xOCIvPgo8dGV4dCB0ZXh0LWFuY2hvcj0ibWlkZGxlIiB4PSIxNTkiIHk9Ii0yNTUuMiIgZm9udC1mYW1pbHk9IkRlamFWdSBTYW5zIiBmb250LXNpemU9IjguNTAiPkpTT04gKyBCYXNlNjQgYXVkaW88L3RleHQ+CjwvZz4KPCEtLSBkMSAtLT4KPGcgaWQ9Im5vZGUxMSIgY2xhc3M9Im5vZGUiPgo8dGl0bGU+ZDE8L3RpdGxlPgo8cGF0aCBmaWxsPSIjZmRlY2VjIiBzdHJva2U9IiMyNDQ0NWYiIGQ9Ik0xMzEuNSwtMTM3QzEzMS41LC0xMzcgOTUuNSwtMTM3IDk1LjUsLTEzNyA4OS41LC0xMzcgODMuNSwtMTMxIDgzLjUsLTEyNSA4My41LC0xMjUgODMuNSwtMTEzIDgzLjUsLTExMyA4My41LC0xMDcgODkuNSwtMTAxIDk1LjUsLTEwMSA5NS41LC0xMDEgMTMxLjUsLTEwMSAxMzEuNSwtMTAxIDEzNy41LC0xMDEgMTQzLjUsLTEwNyAxNDMuNSwtMTEzIDE0My41LC0xMTMgMTQzLjUsLTEyNSAxNDMuNSwtMTI1IDE0My41LC0xMzEgMTM3LjUsLTEzNyAxMzEuNSwtMTM3Ii8+Cjx0ZXh0IHRleHQtYW5jaG9yPSJtaWRkbGUiIHg9IjExMy41IiB5PSItMTE2LjQiIGZvbnQtZmFtaWx5PSJEZWphVnUgU2FucyIgZm9udC1zaXplPSI5LjUwIj5Ccm93c2VyPC90ZXh0Pgo8L2c+CjwhLS0gYzMmIzQ1OyZndDtkMSAtLT4KPCEtLSBkMiAtLT4KPGcgaWQ9Im5vZGUxMiIgY2xhc3M9Im5vZGUiPgo8dGl0bGU+ZDI8L3RpdGxlPgo8cGF0aCBmaWxsPSIjZTRmNWVkIiBzdHJva2U9IiMyNDQ0NWYiIGQ9Ik0xMzguNSwtNTJDMTM4LjUsLTUyIDg4LjUsLTUyIDg4LjUsLTUyIDgyLjUsLTUyIDc2LjUsLTQ2IDc2LjUsLTQwIDc2LjUsLTQwIDc2LjUsLTI4IDc2LjUsLTI4IDc2LjUsLTIyIDgyLjUsLTE2IDg4LjUsLTE2IDg4LjUsLTE2IDEzOC41LC0xNiAxMzguNSwtMTYgMTQ0LjUsLTE2IDE1MC41LC0yMiAxNTAuNSwtMjggMTUwLjUsLTI4IDE1MC41LC00MCAxNTAuNSwtNDAgMTUwLjUsLTQ2IDE0NC41LC01MiAxMzguNSwtNTIiLz4KPHRleHQgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iMTEzLjUiIHk9Ii0zNi40IiBmb250LWZhbWlseT0iRGVqYVZ1IFNhbnMiIGZvbnQtc2l6ZT0iOS41MCI+T3BlbkFJPC90ZXh0Pgo8dGV4dCB0ZXh0LWFuY2hvcj0ibWlkZGxlIiB4PSIxMTMuNSIgeT0iLTI2LjQiIGZvbnQtZmFtaWx5PSJEZWphVnUgU2FucyIgZm9udC1zaXplPSI5LjUwIj5XZWJTb2NrZXQ8L3RleHQ+CjwvZz4KPCEtLSBkMSYjNDU7Jmd0O2QyIC0tPgo8ZyBpZD0iZWRnZTgiIGNsYXNzPSJlZGdlIj4KPHRpdGxlPmQxJiM0NTsmZ3Q7ZDI8L3RpdGxlPgo8cGF0aCBmaWxsPSJub25lIiBzdHJva2U9IiM1MzZiN2EiIGQ9Ik0xMTMuNSwtOTMuNzRDMTEzLjUsLTgyLjkxIDExMy41LC03MC4xNyAxMTMuNSwtNTkuMzMiLz4KPHBvbHlnb24gZmlsbD0iIzUzNmI3YSIgc3Ryb2tlPSIjNTM2YjdhIiBwb2ludHM9IjExMS4wNSwtOTMuOCAxMTMuNSwtMTAwLjggMTE1Ljk1LC05My44IDExMS4wNSwtOTMuOCIvPgo8cG9seWdvbiBmaWxsPSIjNTM2YjdhIiBzdHJva2U9IiM1MzZiN2EiIHBvaW50cz0iMTE1Ljk1LC01OS4xOCAxMTMuNSwtNTIuMTggMTExLjA1LC01OS4xOCAxMTUuOTUsLTU5LjE4Ii8+Cjx0ZXh0IHRleHQtYW5jaG9yPSJtaWRkbGUiIHg9IjE4MyIgeT0iLTc0LjIiIGZvbnQtZmFtaWx5PSJEZWphVnUgU2FucyIgZm9udC1zaXplPSI4LjUwIj5lcGhlbWVyYWwgdG9rZW47IG1hbnVhbCBtZWRpYTwvdGV4dD4KPC9nPgo8L2c+Cjwvc3ZnPgo=">

## 4.1 Option A: direct browser WebRTC with ephemeral client secret

### Flow

1. Browser authenticates to Geppetto.
2. Geppetto calls `POST /v1/realtime/client_secrets` using the permanent server key.
3. Geppetto returns the short-lived client secret and a Geppetto live-session identifier.
4. Browser creates `RTCPeerConnection`, adds microphone track and event data channel, creates an SDP offer, and POSTs the offer directly to OpenAI using the short-lived secret.
5. Browser installs the SDP answer and begins media exchange.
6. Browser extracts the OpenAI `call_id` from the `Location` response header and sends it to Geppetto.
7. Geppetto opens a sideband WebSocket to the same call.

### Advantages

- Geppetto is not in the SDP forwarding path after minting the token.
- Audio never transits Geppetto.
- Browser media behavior is handled by WebRTC.
- Infrastructure cost and bandwidth at Geppetto remain low.

### Risks and mitigations

- Client secrets are short-lived but can create multiple sessions until they expire. The API allows 10 to 7,200 seconds and defaults to 600 seconds. Use the smallest practical TTL, normally 30-60 seconds, bind issuance to an authenticated application session, rate-limit it, and record one logical issuance. [OAI-CLIENT-SECRETS]
- Attached client-secret configuration can be overridden by the client. Treat it as a default, not a security boundary. Keep privileged tools server-side and reauthorize every tool action.
- There is a sideband attach race. Mute/disable the microphone track until the backend acknowledges attachment, or do not advertise privileged tools until sideband control is active.
- A hostile client can use its protocol access to send session events. If the requirement is that the client must be technically unable to modify session configuration, use a backend-owned control/media connection rather than relying on UI restrictions.

### Fit

Best when the application favors minimal bootstrap latency and can tolerate a two-step token/call attachment flow.

## 4.2 Option B: unified SDP interface through Geppetto

### Flow

1. Browser creates a WebRTC SDP offer.
2. Browser POSTs the raw offer to an authenticated Geppetto endpoint.
3. Geppetto creates a multipart request containing fields `sdp` and `session`, then calls `/v1/realtime/calls` with the permanent key.
4. Geppetto captures the answer SDP and `Location`/`call_id`.
5. Geppetto can attach sideband before returning success.
6. Browser installs the answer; media then flows directly between browser and OpenAI.

OpenAI describes the unified interface as simpler, with the tradeoff that the application server is in the critical path for session initialization. [OAI-WEBRTC]

### Advantages

- One browser bootstrap call.
- Server chooses the authoritative initial session configuration.
- `call_id` is available to the backend immediately.
- Sideband can attach before the browser enables microphone input.
- Easier correlation and audit of session creation.

### Disadvantages

- Geppetto must proxy the SDP setup request and handle multipart requests correctly.
- The backend is a dependency for initial call setup.
- Client protocol access still exists after the WebRTC data channel opens; the server-provided initial config alone is not an authorization boundary.

### Fit

**Recommended default for tool-enabled production sessions** because it closes the sideband attach race and simplifies policy/correlation, while still keeping media off the backend.

## 4.3 Option C: direct browser WebSocket to OpenAI

The official WebSocket guide shows that an ephemeral token can be used from browser-like environments, but explicitly recommends WebRTC for browser/mobile clients. [OAI-WEBSOCKET]

### Why it is usually inferior

- Browser audio must be captured as samples, downmixed, resampled, converted to PCM16, Base64-encoded, and wrapped in JSON.
- Output audio must be decoded and scheduled without gaps.
- The browser must implement interruption truncation accurately.
- WebSocket does not supply the media-specific behavior provided by WebRTC.
- The client still requires a backend to mint an ephemeral secret.

### When it can be justified

- A constrained runtime has WebSocket but not functional WebRTC.
- The application already owns a mature low-latency PCM engine.
- The product intentionally wants exact application-level media framing and accepts the complexity.

This should not be the first browser implementation.

## 4.4 Option D: browser -> Geppetto WebSocket -> OpenAI WebSocket

This topology places Geppetto in the media path.

### Browser input pipeline

Use an `AudioWorklet`, not `MediaRecorder`, for the primary live PCM path:

1. Capture Float32 samples from the browser audio graph.
2. Downmix to one channel.
3. Resample from the device/AudioContext rate (commonly 44.1 or 48 kHz) to the configured 24 kHz PCM rate.
4. Convert to signed little-endian PCM16.
5. Batch into small binary frames with sequence number and capture timestamp.
6. Send binary frames to Geppetto.
7. Geppetto Base64-encodes the bytes and emits `input_audio_buffer.append` JSON to OpenAI.

`MediaRecorder` is useful for archival recordings, but it commonly emits compressed container chunks such as WebM/Opus rather than raw PCM. Using it for a low-latency Realtime WebSocket path requires decode/transcode and introduces additional buffering.

### Output pipeline

1. Geppetto receives `response.output_audio.delta` Base64 data.
2. Decode once on the server or forward compact binary PCM to the browser.
3. Browser writes samples into an `AudioWorklet` ring buffer.
4. Track exact samples played, not merely received.
5. On `input_audio_buffer.speech_started`, stop queued playback and report the played duration.
6. Geppetto sends `conversation.item.truncate` with the corresponding `audio_end_ms`.

### Bandwidth estimate

At 24,000 samples/s, mono PCM16 is:

```text
24,000 samples/s * 2 bytes/sample = 48,000 bytes/s
Base64 expansion                       ~= 64,000 bytes/s
Raw bit rate                           ~= 384 kbit/s
Base64 payload bit rate                ~= 512 kbit/s before JSON/TLS framing
```

This is manageable for one session, but expensive at scale compared with letting WebRTC manage compressed media. A 20 ms PCM frame contains 480 samples or 960 raw bytes; a 100 ms frame contains 2,400 samples or 4,800 raw bytes. A starting range of 40-80 ms balances overhead and latency, but must be benchmarked under realistic devices and networks.

### Operational costs

- all input and output audio bandwidth crosses Geppetto;
- Base64 conversion and JSON allocation occur on the OpenAI leg;
- two independent real-time sockets must be backpressured;
- every backend deployment/incident can disrupt media;
- autoscaling must account for connection count, audio byte rate, and CPU;
- recording/privacy obligations attach directly to the backend.

### Fit

Use when server media custody is a requirement, not merely because it seems architecturally familiar.

## 4.5 Option E: chained voice

Chained voice uses live speech-to-text, an existing text agent, and text-to-speech. It may use WebRTC for browser transcription, WebSocket for server audio, or a browser/backend hybrid.

It provides:

- explicit intermediate text;
- straightforward policy checks before generation or speech;
- reuse of existing `Session`, `Engine`, and `toolloop.Loop`;
- deterministic choice of when to speak;
- easier durable transcripts and approvals.

It usually has more latency and less natural barge-in than native speech-to-speech. OpenAI recommends the chained pattern for predictable workflows and extending an existing text agent. [OAI-VOICE-AGENTS]

## 4.6 Decision matrix

Scores are relative for Geppetto's likely use cases: 5 is favorable, 1 is unfavorable.

| Topology | Browser latency/media behavior | Backend load | Server policy/tool control | Implementation complexity | Recommended use |
|---|---:|---:|---:|---:|---|
| Direct WebRTC + unified bootstrap + sideband | 5 | 5 | 4 | 3 | Default browser voice agent |
| Direct WebRTC + ephemeral secret + sideband | 5 | 5 | 4 | 3 | Lower bootstrap coupling; manage attach race |
| Direct browser WebSocket | 2 | 5 | 2 | 1 | Exceptional runtime constraints |
| Backend media proxy | 3 | 1 | 5 | 1 | Compliance, telephony, recording, transcoding |
| Chained voice | 3 | 3 | 5 | 3 | Approval-heavy, auditable, existing text workflows |
| Pure browser with permanent key | 1 | 5 | 1 | 4 | Reject: credential exposure |



# 5. Recommended target architecture {#recommended-target-architecture}

## 5.1 Separate four responsibilities

### Live domain layer

Provider-neutral session state, commands, snapshots, terminal errors, and lifecycle. It must not know about WebRTC browser APIs.

### OpenAI Realtime adapter

Exact provider protocol types, client-secret/unified bootstrap calls, server WebSocket transport, sideband attachment, event reducer, tool mapping, and provider diagnostics.

### Browser media client

`RTCPeerConnection`, device permissions, microphone controls, autoplay/user gesture, remote audio, data-channel events, call bootstrap, and browser metrics.

### Existing Geppetto services

Session IDs, canonical events, tool registry/executor, settings loading, persistence, logs/traces/metrics, and Goja integration.

## 5.2 Media plane versus semantic plane

A central rule is to keep media bytes separate from semantic state.

| Plane | Examples | Handling |
|---|---|---|
| Media | microphone samples, remote audio packets, output PCM deltas | WebRTC track or dedicated bounded audio transport |
| Provider protocol | `session.updated`, item IDs, audio deltas, argument deltas | typed adapter + reducer |
| Reliable control | tool output, truncate, cancel, session update | bounded command queue; transport write pump |
| Canonical semantic events | transcript delta, response started, tool call, error | `events.EventSink` |
| Durable state | final transcripts, completed tool result, completed/truncated assistant item | Turn/session persistence at stable barriers |

The default EventSink should never carry raw PCM or Base64 audio. Doing so would multiply copies, encourage accidental logging, and let slow telemetry subscribers interfere with media.

## 5.3 Why a new live subsystem is preferable to extending Engine

A parallel subsystem preserves backward compatibility and makes invariants explicit:

```text
Finite inference                               Live session
----------------                               ------------
one input Turn                                 mutable session configuration
one output Turn                                many conversation Items/Responses
method completion is success boundary          close/failure is session boundary
SSE can be reduced internally                  independent duplex event stream
finite tool loop invokes engine repeatedly     tools occur inside the live connection
ExecutionHandle.Wait() returns result           Session.Done() signals terminal state
```

Adapters can share lower-level utilities, but their public contracts should not be merged.

## 5.4 Provider call identity

Use two identifiers:

- **Geppetto live SessionID:** stable across the user-facing live interaction and used for application correlation.
- **OpenAI call/session IDs:** provider-native capabilities and provenance kept inside adapter state/debug metadata.

A reconnect or 60-minute rollover may create a new provider call while retaining the same higher-level Geppetto session or creating a linked successor, depending on persistence policy.



# 6. Supporting both native and chained voice {#native-and-chained}

<img class="diagram-img" alt="Native and chained voice architectures" src="data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiIHN0YW5kYWxvbmU9Im5vIj8+CjwhRE9DVFlQRSBzdmcgUFVCTElDICItLy9XM0MvL0RURCBTVkcgMS4xLy9FTiIKICJodHRwOi8vd3d3LnczLm9yZy9HcmFwaGljcy9TVkcvMS4xL0RURC9zdmcxMS5kdGQiPgo8IS0tIEdlbmVyYXRlZCBieSBncmFwaHZpeiB2ZXJzaW9uIDIuNDIuNCAoMCkKIC0tPgo8IS0tIFRpdGxlOiBHIFBhZ2VzOiAxIC0tPgo8c3ZnIHdpZHRoPSIxMTYzcHQiIGhlaWdodD0iMjE4cHQiCiB2aWV3Qm94PSIwLjAwIDAuMDAgMTE2My4wMCAyMTguMDAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgeG1sbnM6eGxpbms9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkveGxpbmsiPgo8ZyBpZD0iZ3JhcGgwIiBjbGFzcz0iZ3JhcGgiIHRyYW5zZm9ybT0ic2NhbGUoMSAxKSByb3RhdGUoMCkgdHJhbnNsYXRlKDE4IDIwMCkiPgo8dGl0bGU+RzwvdGl0bGU+CjwhLS0gbWljMSAtLT4KPGcgaWQ9Im5vZGUxIiBjbGFzcz0ibm9kZSI+Cjx0aXRsZT5taWMxPC90aXRsZT4KPHBhdGggZmlsbD0iI2VhZjNmOCIgc3Ryb2tlPSIjMjQ0NDVmIiBkPSJNNjUsLTczQzY1LC03MyAxMiwtNzMgMTIsLTczIDYsLTczIDAsLTY3IDAsLTYxIDAsLTYxIDAsLTQ5IDAsLTQ5IDAsLTQzIDYsLTM3IDEyLC0zNyAxMiwtMzcgNjUsLTM3IDY1LC0zNyA3MSwtMzcgNzcsLTQzIDc3LC00OSA3NywtNDkgNzcsLTYxIDc3LC02MSA3NywtNjcgNzEsLTczIDY1LC03MyIvPgo8dGV4dCB0ZXh0LWFuY2hvcj0ibWlkZGxlIiB4PSIzOC41IiB5PSItNTIuNCIgZm9udC1mYW1pbHk9IkRlamFWdSBTYW5zIiBmb250LXNpemU9IjkuNTAiPk1pY3JvcGhvbmU8L3RleHQ+CjwvZz4KPCEtLSBydCAtLT4KPGcgaWQ9Im5vZGUyIiBjbGFzcz0ibm9kZSI+Cjx0aXRsZT5ydDwvdGl0bGU+CjxwYXRoIGZpbGw9IiNkY2VjZjUiIHN0cm9rZT0iIzI0NDQ1ZiIgZD0iTTM5MiwtNzNDMzkyLC03MyAyMDAsLTczIDIwMCwtNzMgMTk0LC03MyAxODgsLTY3IDE4OCwtNjEgMTg4LC02MSAxODgsLTQ5IDE4OCwtNDkgMTg4LC00MyAxOTQsLTM3IDIwMCwtMzcgMjAwLC0zNyAzOTIsLTM3IDM5MiwtMzcgMzk4LC0zNyA0MDQsLTQzIDQwNCwtNDkgNDA0LC00OSA0MDQsLTYxIDQwNCwtNjEgNDA0LC02NyAzOTgsLTczIDM5MiwtNzMiLz4KPHRleHQgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iMjk2IiB5PSItNTcuNCIgZm9udC1mYW1pbHk9IkRlamFWdSBTYW5zIiBmb250LXNpemU9IjkuNTAiPk5hdGl2ZSBSZWFsdGltZSBtb2RlbDwvdGV4dD4KPHRleHQgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iMjk2IiB5PSItNDcuNCIgZm9udC1mYW1pbHk9IkRlamFWdSBTYW5zIiBmb250LXNpemU9IjkuNTAiPmF1ZGlvIGluICYjNDU7Jmd0OyByZWFzb25pbmcvdG9vbHMgJiM0NTsmZ3Q7IGF1ZGlvIG91dDwvdGV4dD4KPC9nPgo8IS0tIG1pYzEmIzQ1OyZndDtydCAtLT4KPGcgaWQ9ImVkZ2UxIiBjbGFzcz0iZWRnZSI+Cjx0aXRsZT5taWMxJiM0NTsmZ3Q7cnQ8L3RpdGxlPgo8cGF0aCBmaWxsPSJub25lIiBzdHJva2U9IiM1MzZiN2EiIGQ9Ik03Ny4yLC01NUMxMDQuNTksLTU1IDE0My4yMywtNTUgMTgwLjM3LC01NSIvPgo8cG9seWdvbiBmaWxsPSIjNTM2YjdhIiBzdHJva2U9IiM1MzZiN2EiIHBvaW50cz0iMTgwLjc3LC01Ny40NSAxODcuNzcsLTU1IDE4MC43NywtNTIuNTUgMTgwLjc3LC01Ny40NSIvPgo8dGV4dCB0ZXh0LWFuY2hvcj0ibWlkZGxlIiB4PSIxMzIuNSIgeT0iLTU3LjIiIGZvbnQtZmFtaWx5PSJEZWphVnUgU2FucyIgZm9udC1zaXplPSI4LjUwIj5XZWJSVEMgYXVkaW88L3RleHQ+CjwvZz4KPCEtLSBzcGsxIC0tPgo8ZyBpZD0ibm9kZTMiIGNsYXNzPSJub2RlIj4KPHRpdGxlPnNwazE8L3RpdGxlPgo8cGF0aCBmaWxsPSIjZWFmM2Y4IiBzdHJva2U9IiMyNDQ0NWYiIGQ9Ik0xMTE1LC0xMDlDMTExNSwtMTA5IDEwNzksLTEwOSAxMDc5LC0xMDkgMTA3MywtMTA5IDEwNjcsLTEwMyAxMDY3LC05NyAxMDY3LC05NyAxMDY3LC04NSAxMDY3LC04NSAxMDY3LC03OSAxMDczLC03MyAxMDc5LC03MyAxMDc5LC03MyAxMTE1LC03MyAxMTE1LC03MyAxMTIxLC03MyAxMTI3LC03OSAxMTI3LC04NSAxMTI3LC04NSAxMTI3LC05NyAxMTI3LC05NyAxMTI3LC0xMDMgMTEyMSwtMTA5IDExMTUsLTEwOSIvPgo8dGV4dCB0ZXh0LWFuY2hvcj0ibWlkZGxlIiB4PSIxMDk3IiB5PSItODguNCIgZm9udC1mYW1pbHk9IkRlamFWdSBTYW5zIiBmb250LXNpemU9IjkuNTAiPlNwZWFrZXI8L3RleHQ+CjwvZz4KPCEtLSBydCYjNDU7Jmd0O3NwazEgLS0+CjxnIGlkPSJlZGdlMiIgY2xhc3M9ImVkZ2UiPgo8dGl0bGU+cnQmIzQ1OyZndDtzcGsxPC90aXRsZT4KPHBhdGggZmlsbD0ibm9uZSIgc3Ryb2tlPSIjNTM2YjdhIiBkPSJNNDA0LjM0LC01OS44NEM1ODUuNzEsLTY4LjAxIDk0NC4zMSwtODQuMTcgMTA1OS40OCwtODkuMzUiLz4KPHBvbHlnb24gZmlsbD0iIzUzNmI3YSIgc3Ryb2tlPSIjNTM2YjdhIiBwb2ludHM9IjEwNTkuNiwtOTEuODEgMTA2Ni43LC04OS42OCAxMDU5LjgyLC04Ni45MiAxMDU5LjYsLTkxLjgxIi8+Cjx0ZXh0IHRleHQtYW5jaG9yPSJtaWRkbGUiIHg9Ijc0Mi41IiB5PSItNzguMiIgZm9udC1mYW1pbHk9IkRlamFWdSBTYW5zIiBmb250LXNpemU9IjguNTAiPldlYlJUQyBhdWRpbzwvdGV4dD4KPC9nPgo8IS0tIHRvb2xzMSAtLT4KPGcgaWQ9Im5vZGU0IiBjbGFzcz0ibm9kZSI+Cjx0aXRsZT50b29sczE8L3RpdGxlPgo8cGF0aCBmaWxsPSIjZWVmNGZmIiBzdHJva2U9IiMyNDQ0NWYiIGQ9Ik02NDAuNSwtMzZDNjQwLjUsLTM2IDU3MS41LC0zNiA1NzEuNSwtMzYgNTY1LjUsLTM2IDU1OS41LC0zMCA1NTkuNSwtMjQgNTU5LjUsLTI0IDU1OS41LC0xMiA1NTkuNSwtMTIgNTU5LjUsLTYgNTY1LjUsMCA1NzEuNSwwIDU3MS41LDAgNjQwLjUsMCA2NDAuNSwwIDY0Ni41LDAgNjUyLjUsLTYgNjUyLjUsLTEyIDY1Mi41LC0xMiA2NTIuNSwtMjQgNjUyLjUsLTI0IDY1Mi41LC0zMCA2NDYuNSwtMzYgNjQwLjUsLTM2Ii8+Cjx0ZXh0IHRleHQtYW5jaG9yPSJtaWRkbGUiIHg9IjYwNiIgeT0iLTIwLjQiIGZvbnQtZmFtaWx5PSJEZWphVnUgU2FucyIgZm9udC1zaXplPSI5LjUwIj5HZXBwZXR0byB0b29sczwvdGV4dD4KPHRleHQgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iNjA2IiB5PSItMTAuNCIgZm9udC1mYW1pbHk9IkRlamFWdSBTYW5zIiBmb250LXNpemU9IjkuNTAiPnZpYSBzaWRlYmFuZDwvdGV4dD4KPC9nPgo8IS0tIHJ0JiM0NTsmZ3Q7dG9vbHMxIC0tPgo8ZyBpZD0iZWRnZTMiIGNsYXNzPSJlZGdlIj4KPHRpdGxlPnJ0JiM0NTsmZ3Q7dG9vbHMxPC90aXRsZT4KPHBhdGggZmlsbD0ibm9uZSIgc3Ryb2tlPSIjNTM2YjdhIiBkPSJNNDExLjUsLTQxLjI1QzQ1OS44NywtMzUuNDMgNTEzLjgyLC0yOC45NSA1NTIuNDQsLTI0LjMxIi8+Cjxwb2x5Z29uIGZpbGw9IiM1MzZiN2EiIHN0cm9rZT0iIzUzNmI3YSIgcG9pbnRzPSI0MTAuOTUsLTM4Ljg0IDQwNC4yOSwtNDIuMTEgNDExLjUzLC00My43MSA0MTAuOTUsLTM4Ljg0Ii8+Cjxwb2x5Z29uIGZpbGw9IiM1MzZiN2EiIHN0cm9rZT0iIzUzNmI3YSIgcG9pbnRzPSI1NTIuODEsLTI2Ljc0IDU1OS40NywtMjMuNDcgNTUyLjIzLC0yMS44NyA1NTIuODEsLTI2Ljc0Ii8+Cjx0ZXh0IHRleHQtYW5jaG9yPSJtaWRkbGUiIHg9IjQ2NC41IiB5PSItNDAuMiIgZm9udC1mYW1pbHk9IkRlamFWdSBTYW5zIiBmb250LXNpemU9IjguNTAiPnRvb2wgZXZlbnRzPC90ZXh0Pgo8L2c+CjwhLS0gbWljMiAtLT4KPGcgaWQ9Im5vZGU1IiBjbGFzcz0ibm9kZSI+Cjx0aXRsZT5taWMyPC90aXRsZT4KPHBhdGggZmlsbD0iI2ZmZjVlNSIgc3Ryb2tlPSIjMjQ0NDVmIiBkPSJNNjUsLTE4MkM2NSwtMTgyIDEyLC0xODIgMTIsLTE4MiA2LC0xODIgMCwtMTc2IDAsLTE3MCAwLC0xNzAgMCwtMTU4IDAsLTE1OCAwLC0xNTIgNiwtMTQ2IDEyLC0xNDYgMTIsLTE0NiA2NSwtMTQ2IDY1LC0xNDYgNzEsLTE0NiA3NywtMTUyIDc3LC0xNTggNzcsLTE1OCA3NywtMTcwIDc3LC0xNzAgNzcsLTE3NiA3MSwtMTgyIDY1LC0xODIiLz4KPHRleHQgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iMzguNSIgeT0iLTE2MS40IiBmb250LWZhbWlseT0iRGVqYVZ1IFNhbnMiIGZvbnQtc2l6ZT0iOS41MCI+TWljcm9waG9uZTwvdGV4dD4KPC9nPgo8IS0tIHN0dCAtLT4KPGcgaWQ9Im5vZGU2IiBjbGFzcz0ibm9kZSI+Cjx0aXRsZT5zdHQ8L3RpdGxlPgo8cGF0aCBmaWxsPSIjZmZmMGQ1IiBzdHJva2U9IiMyNDQ0NWYiIGQ9Ik0zNDgsLTE4MkMzNDgsLTE4MiAyNDQsLTE4MiAyNDQsLTE4MiAyMzgsLTE4MiAyMzIsLTE3NiAyMzIsLTE3MCAyMzIsLTE3MCAyMzIsLTE1OCAyMzIsLTE1OCAyMzIsLTE1MiAyMzgsLTE0NiAyNDQsLTE0NiAyNDQsLTE0NiAzNDgsLTE0NiAzNDgsLTE0NiAzNTQsLTE0NiAzNjAsLTE1MiAzNjAsLTE1OCAzNjAsLTE1OCAzNjAsLTE3MCAzNjAsLTE3MCAzNjAsLTE3NiAzNTQsLTE4MiAzNDgsLTE4MiIvPgo8dGV4dCB0ZXh0LWFuY2hvcj0ibWlkZGxlIiB4PSIyOTYiIHk9Ii0xNjEuNCIgZm9udC1mYW1pbHk9IkRlamFWdSBTYW5zIiBmb250LXNpemU9IjkuNTAiPlJlYWx0aW1lIHRyYW5zY3JpcHRpb248L3RleHQ+CjwvZz4KPCEtLSBtaWMyJiM0NTsmZ3Q7c3R0IC0tPgo8ZyBpZD0iZWRnZTQiIGNsYXNzPSJlZGdlIj4KPHRpdGxlPm1pYzImIzQ1OyZndDtzdHQ8L3RpdGxlPgo8cGF0aCBmaWxsPSJub25lIiBzdHJva2U9IiM1MzZiN2EiIGQ9Ik03Ny4yLC0xNjRDMTE1Ljg5LC0xNjQgMTc2Ljk5LC0xNjQgMjI0LjY0LC0xNjQiLz4KPHBvbHlnb24gZmlsbD0iIzUzNmI3YSIgc3Ryb2tlPSIjNTM2YjdhIiBwb2ludHM9IjIyNC44NywtMTY2LjQ1IDIzMS44NywtMTY0IDIyNC44NywtMTYxLjU1IDIyNC44NywtMTY2LjQ1Ii8+Cjx0ZXh0IHRleHQtYW5jaG9yPSJtaWRkbGUiIHg9IjEzMi41IiB5PSItMTY2LjIiIGZvbnQtZmFtaWx5PSJEZWphVnUgU2FucyIgZm9udC1zaXplPSI4LjUwIj5saXZlIGF1ZGlvPC90ZXh0Pgo8L2c+CjwhLS0gdGV4dCAtLT4KPGcgaWQ9Im5vZGU3IiBjbGFzcz0ibm9kZSI+Cjx0aXRsZT50ZXh0PC90aXRsZT4KPHBhdGggZmlsbD0iI2VlZjRmZiIgc3Ryb2tlPSIjMjQ0NDVmIiBkPSJNNjc1LC0xODJDNjc1LC0xODIgNTM3LC0xODIgNTM3LC0xODIgNTMxLC0xODIgNTI1LC0xNzYgNTI1LC0xNzAgNTI1LC0xNzAgNTI1LC0xNTggNTI1LC0xNTggNTI1LC0xNTIgNTMxLC0xNDYgNTM3LC0xNDYgNTM3LC0xNDYgNjc1LC0xNDYgNjc1LC0xNDYgNjgxLC0xNDYgNjg3LC0xNTIgNjg3LC0xNTggNjg3LC0xNTggNjg3LC0xNzAgNjg3LC0xNzAgNjg3LC0xNzYgNjgxLC0xODIgNjc1LC0xODIiLz4KPHRleHQgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iNjA2IiB5PSItMTY2LjQiIGZvbnQtZmFtaWx5PSJEZWphVnUgU2FucyIgZm9udC1zaXplPSI5LjUwIj5FeGlzdGluZyBHZXBwZXR0bzwvdGV4dD4KPHRleHQgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iNjA2IiB5PSItMTU2LjQiIGZvbnQtZmFtaWx5PSJEZWphVnUgU2FucyIgZm9udC1zaXplPSI5LjUwIj5TZXNzaW9uICsgRW5naW5lICsgdG9vbCBsb29wPC90ZXh0Pgo8L2c+CjwhLS0gc3R0JiM0NTsmZ3Q7dGV4dCAtLT4KPGcgaWQ9ImVkZ2U1IiBjbGFzcz0iZWRnZSI+Cjx0aXRsZT5zdHQmIzQ1OyZndDt0ZXh0PC90aXRsZT4KPHBhdGggZmlsbD0ibm9uZSIgc3Ryb2tlPSIjNTM2YjdhIiBkPSJNMzYwLjA3LC0xNjRDNDA1LjYyLC0xNjQgNDY3LjcxLC0xNjQgNTE3Ljk4LC0xNjQiLz4KPHBvbHlnb24gZmlsbD0iIzUzNmI3YSIgc3Ryb2tlPSIjNTM2YjdhIiBwb2ludHM9IjUxNy45OSwtMTY2LjQ1IDUyNC45OSwtMTY0IDUxNy45OSwtMTYxLjU1IDUxNy45OSwtMTY2LjQ1Ii8+Cjx0ZXh0IHRleHQtYW5jaG9yPSJtaWRkbGUiIHg9IjQ2NC41IiB5PSItMTY2LjIiIGZvbnQtZmFtaWx5PSJEZWphVnUgU2FucyIgZm9udC1zaXplPSI4LjUwIj5maW5hbC9pbnRlcmltIHRleHQ8L3RleHQ+CjwvZz4KPCEtLSB0dHMgLS0+CjxnIGlkPSJub2RlOCIgY2xhc3M9Im5vZGUiPgo8dGl0bGU+dHRzPC90aXRsZT4KPHBhdGggZmlsbD0iI2ZmZjBkNSIgc3Ryb2tlPSIjMjQ0NDVmIiBkPSJNOTQ5LC0xODJDOTQ5LC0xODIgODEwLC0xODIgODEwLC0xODIgODA0LC0xODIgNzk4LC0xNzYgNzk4LC0xNzAgNzk4LC0xNzAgNzk4LC0xNTggNzk4LC0xNTggNzk4LC0xNTIgODA0LC0xNDYgODEwLC0xNDYgODEwLC0xNDYgOTQ5LC0xNDYgOTQ5LC0xNDYgOTU1LC0xNDYgOTYxLC0xNTIgOTYxLC0xNTggOTYxLC0xNTggOTYxLC0xNzAgOTYxLC0xNzAgOTYxLC0xNzYgOTU1LC0xODIgOTQ5LC0xODIiLz4KPHRleHQgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iODc5LjUiIHk9Ii0xNjEuNCIgZm9udC1mYW1pbHk9IkRlamFWdSBTYW5zIiBmb250LXNpemU9IjkuNTAiPlN0cmVhbWluZyBzcGVlY2ggZ2VuZXJhdGlvbjwvdGV4dD4KPC9nPgo8IS0tIHRleHQmIzQ1OyZndDt0dHMgLS0+CjxnIGlkPSJlZGdlNiIgY2xhc3M9ImVkZ2UiPgo8dGl0bGU+dGV4dCYjNDU7Jmd0O3R0czwvdGl0bGU+CjxwYXRoIGZpbGw9Im5vbmUiIHN0cm9rZT0iIzUzNmI3YSIgZD0iTTY4Ny4zNiwtMTY0QzcxOS45MSwtMTY0IDc1Ny41OSwtMTY0IDc5MC44NSwtMTY0Ii8+Cjxwb2x5Z29uIGZpbGw9IiM1MzZiN2EiIHN0cm9rZT0iIzUzNmI3YSIgcG9pbnRzPSI3OTAuODgsLTE2Ni40NSA3OTcuODgsLTE2NCA3OTAuODgsLTE2MS41NSA3OTAuODgsLTE2Ni40NSIvPgo8dGV4dCB0ZXh0LWFuY2hvcj0ibWlkZGxlIiB4PSI3NDIuNSIgeT0iLTE2Ni4yIiBmb250LWZhbWlseT0iRGVqYVZ1IFNhbnMiIGZvbnQtc2l6ZT0iOC41MCI+YXBwcm92ZWQgdGV4dDwvdGV4dD4KPC9nPgo8IS0tIHNwazIgLS0+CjxnIGlkPSJub2RlOSIgY2xhc3M9Im5vZGUiPgo8dGl0bGU+c3BrMjwvdGl0bGU+CjxwYXRoIGZpbGw9IiNmZmY1ZTUiIHN0cm9rZT0iIzI0NDQ1ZiIgZD0iTTExMTUsLTE4MkMxMTE1LC0xODIgMTA3OSwtMTgyIDEwNzksLTE4MiAxMDczLC0xODIgMTA2NywtMTc2IDEwNjcsLTE3MCAxMDY3LC0xNzAgMTA2NywtMTU4IDEwNjcsLTE1OCAxMDY3LC0xNTIgMTA3MywtMTQ2IDEwNzksLTE0NiAxMDc5LC0xNDYgMTExNSwtMTQ2IDExMTUsLTE0NiAxMTIxLC0xNDYgMTEyNywtMTUyIDExMjcsLTE1OCAxMTI3LC0xNTggMTEyNywtMTcwIDExMjcsLTE3MCAxMTI3LC0xNzYgMTEyMSwtMTgyIDExMTUsLTE4MiIvPgo8dGV4dCB0ZXh0LWFuY2hvcj0ibWlkZGxlIiB4PSIxMDk3IiB5PSItMTYxLjQiIGZvbnQtZmFtaWx5PSJEZWphVnUgU2FucyIgZm9udC1zaXplPSI5LjUwIj5TcGVha2VyPC90ZXh0Pgo8L2c+CjwhLS0gdHRzJiM0NTsmZ3Q7c3BrMiAtLT4KPGcgaWQ9ImVkZ2U3IiBjbGFzcz0iZWRnZSI+Cjx0aXRsZT50dHMmIzQ1OyZndDtzcGsyPC90aXRsZT4KPHBhdGggZmlsbD0ibm9uZSIgc3Ryb2tlPSIjNTM2YjdhIiBkPSJNOTYxLjA1LC0xNjRDOTk0LjkzLC0xNjQgMTAzMi42NCwtMTY0IDEwNTkuNTcsLTE2NCIvPgo8cG9seWdvbiBmaWxsPSIjNTM2YjdhIiBzdHJva2U9IiM1MzZiN2EiIHBvaW50cz0iMTA1OS44NiwtMTY2LjQ1IDEwNjYuODYsLTE2NCAxMDU5Ljg2LC0xNjEuNTUgMTA1OS44NiwtMTY2LjQ1Ii8+Cjx0ZXh0IHRleHQtYW5jaG9yPSJtaWRkbGUiIHg9IjEwMTQiIHk9Ii0xNjYuMiIgZm9udC1mYW1pbHk9IkRlamFWdSBTYW5zIiBmb250LXNpemU9IjguNTAiPmF1ZGlvIHN0cmVhbTwvdGV4dD4KPC9nPgo8L2c+Cjwvc3ZnPgo=">

The phrase “both designs” has two useful interpretations in this codebase, and both should be adopted.

## 6.1 Both existing Geppetto interaction designs

### Session-centered design

Use the session concept for:

- stable identity;
- lifecycle and close/cancel semantics;
- append-only stable snapshots;
- fork/resume at transcript barriers;
- persistence and UI ownership.

### Streaming event design

Use EventSink/EventEmitter for:

- incremental text/transcript updates;
- live state changes;
- tool progress;
- response lifecycle;
- rate limits and errors.

The live session owns correctness; the event layer observes it. This preserves the current event system's best-effort contract.

## 6.2 Both voice architectures

### Mode A: `native_realtime`

Use direct audio input/output in one Realtime model session.

Best for:

- conversational assistants;
- low first-audio latency;
- natural turn-taking;
- barge-in;
- voice style/prosody;
- real-time tool interactions.

Tradeoffs:

- less explicit control over intermediate text;
- input transcript is an asynchronous auxiliary signal;
- client and server must reason about ongoing provider conversation state;
- strict approval before every spoken phrase is harder.

### Mode B: `chained`

Use live transcription -> current Geppetto text workflow -> streaming TTS.

Best for:

- support and transaction flows;
- approvals or human review;
- deterministic policy checkpoints;
- durable, authoritative text records;
- reuse of existing prompts, engines, tools, and middleware;
- providers that do not offer native speech-to-speech.

Tradeoffs:

- greater end-to-end latency;
- more orchestration components;
- barge-in and prosody require explicit implementation;
- the spoken result may feel less fluid.

## 6.3 Common product facade, separate internals

A product-facing browser API can use a shared vocabulary:

```ts
const voice = await client.voiceSession({
  mode: "native_realtime", // or "chained"
  transport: "webrtc_direct",
  profile: "support-default",
});

voice.on("input-transcript-delta", renderUserCaption);
voice.on("output-transcript-delta", renderAssistantCaption);
voice.on("tool-call-started", renderToolStatus);
await voice.connect();
```

Internally, the modes should remain distinct:

- native mode opens `live.Session` and the OpenAI Realtime adapter;
- chained mode opens a transcription session, commits a text Turn into the existing `Session`, runs the normal engine/tool loop, and streams TTS output.

Do not make native Realtime pretend that every VAD boundary is `session.next()`. Provider Conversation Items and Responses are finer-grained and interruption-sensitive.



# 7. Detailed Go package and interface design {#go-design}

<img class="diagram-img" alt="Proposed live subsystem internals" src="data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiIHN0YW5kYWxvbmU9Im5vIj8+CjwhRE9DVFlQRSBzdmcgUFVCTElDICItLy9XM0MvL0RURCBTVkcgMS4xLy9FTiIKICJodHRwOi8vd3d3LnczLm9yZy9HcmFwaGljcy9TVkcvMS4xL0RURC9zdmcxMS5kdGQiPgo8IS0tIEdlbmVyYXRlZCBieSBncmFwaHZpeiB2ZXJzaW9uIDIuNDIuNCAoMCkKIC0tPgo8IS0tIFRpdGxlOiBHIFBhZ2VzOiAxIC0tPgo8c3ZnIHdpZHRoPSIxNTA1cHQiIGhlaWdodD0iMjI4cHQiCiB2aWV3Qm94PSIwLjAwIDAuMDAgMTUwNS4wMCAyMjguMDAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgeG1sbnM6eGxpbms9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkveGxpbmsiPgo8ZyBpZD0iZ3JhcGgwIiBjbGFzcz0iZ3JhcGgiIHRyYW5zZm9ybT0ic2NhbGUoMSAxKSByb3RhdGUoMCkgdHJhbnNsYXRlKDE4IDIxMCkiPgo8dGl0bGU+RzwvdGl0bGU+CjwhLS0gYXBpIC0tPgo8ZyBpZD0ibm9kZTEiIGNsYXNzPSJub2RlIj4KPHRpdGxlPmFwaTwvdGl0bGU+CjxwYXRoIGZpbGw9IiNlYWYzZjgiIHN0cm9rZT0iIzI0NDQ1ZiIgZD0iTTEyNCwtMTIwQzEyNCwtMTIwIDEyLC0xMjAgMTIsLTEyMCA2LC0xMjAgMCwtMTE0IDAsLTEwOCAwLC0xMDggMCwtOTYgMCwtOTYgMCwtOTAgNiwtODQgMTIsLTg0IDEyLC04NCAxMjQsLTg0IDEyNCwtODQgMTMwLC04NCAxMzYsLTkwIDEzNiwtOTYgMTM2LC05NiAxMzYsLTEwOCAxMzYsLTEwOCAxMzYsLTExNCAxMzAsLTEyMCAxMjQsLTEyMCIvPgo8dGV4dCB0ZXh0LWFuY2hvcj0ibWlkZGxlIiB4PSI2OCIgeT0iLTEwNC40IiBmb250LWZhbWlseT0iRGVqYVZ1IFNhbnMiIGZvbnQtc2l6ZT0iOS41MCI+QnJvd3NlciBIVFRQIC8gV2ViUlRDPC90ZXh0Pgo8dGV4dCB0ZXh0LWFuY2hvcj0ibWlkZGxlIiB4PSI2OCIgeT0iLTk0LjQiIGZvbnQtZmFtaWx5PSJEZWphVnUgU2FucyIgZm9udC1zaXplPSI5LjUwIj5vciBzZXJ2ZXIgY2FsbGVyPC90ZXh0Pgo8L2c+CjwhLS0gZmFjYWRlIC0tPgo8ZyBpZD0ibm9kZTIiIGNsYXNzPSJub2RlIj4KPHRpdGxlPmZhY2FkZTwvdGl0bGU+CjxwYXRoIGZpbGw9IiNkZmU5ZmYiIHN0cm9rZT0iIzI0NDQ1ZiIgZD0iTTI4NSwtMTIwQzI4NSwtMTIwIDE5NywtMTIwIDE5NywtMTIwIDE5MSwtMTIwIDE4NSwtMTE0IDE4NSwtMTA4IDE4NSwtMTA4IDE4NSwtOTYgMTg1LC05NiAxODUsLTkwIDE5MSwtODQgMTk3LC04NCAxOTcsLTg0IDI4NSwtODQgMjg1LC04NCAyOTEsLTg0IDI5NywtOTAgMjk3LC05NiAyOTcsLTk2IDI5NywtMTA4IDI5NywtMTA4IDI5NywtMTE0IDI5MSwtMTIwIDI4NSwtMTIwIi8+Cjx0ZXh0IHRleHQtYW5jaG9yPSJtaWRkbGUiIHg9IjI0MSIgeT0iLTEwNC40IiBmb250LWZhbWlseT0iRGVqYVZ1IFNhbnMiIGZvbnQtc2l6ZT0iOS41MCI+bGl2ZS5Db250cm9sbGVyPC90ZXh0Pgo8dGV4dCB0ZXh0LWFuY2hvcj0ibWlkZGxlIiB4PSIyNDEiIHk9Ii05NC40IiBmb250LWZhbWlseT0iRGVqYVZ1IFNhbnMiIGZvbnQtc2l6ZT0iOS41MCI+TGl2ZVNlc3Npb25GYWN0b3J5PC90ZXh0Pgo8L2c+CjwhLS0gYXBpJiM0NTsmZ3Q7ZmFjYWRlIC0tPgo8ZyBpZD0iZWRnZTEiIGNsYXNzPSJlZGdlIj4KPHRpdGxlPmFwaSYjNDU7Jmd0O2ZhY2FkZTwvdGl0bGU+CjxwYXRoIGZpbGw9Im5vbmUiIHN0cm9rZT0iIzUzNmI3YSIgZD0iTTEzNi4wOSwtMTAyQzE0OS44OCwtMTAyIDE2NC4zMywtMTAyIDE3Ny45MywtMTAyIi8+Cjxwb2x5Z29uIGZpbGw9IiM1MzZiN2EiIHN0cm9rZT0iIzUzNmI3YSIgcG9pbnRzPSIxNzcuOTUsLTEwNC40NSAxODQuOTUsLTEwMiAxNzcuOTUsLTk5LjU1IDE3Ny45NSwtMTA0LjQ1Ii8+CjwvZz4KPCEtLSBzZXNzaW9uIC0tPgo8ZyBpZD0ibm9kZTMiIGNsYXNzPSJub2RlIj4KPHRpdGxlPnNlc3Npb248L3RpdGxlPgo8cGF0aCBmaWxsPSIjZGZlOWZmIiBzdHJva2U9IiMyNDQ0NWYiIGQ9Ik00NzQsLTEyMEM0NzQsLTEyMCAzNTgsLTEyMCAzNTgsLTEyMCAzNTIsLTEyMCAzNDYsLTExNCAzNDYsLTEwOCAzNDYsLTEwOCAzNDYsLTk2IDM0NiwtOTYgMzQ2LC05MCAzNTIsLTg0IDM1OCwtODQgMzU4LC04NCA0NzQsLTg0IDQ3NCwtODQgNDgwLC04NCA0ODYsLTkwIDQ4NiwtOTYgNDg2LC05NiA0ODYsLTEwOCA0ODYsLTEwOCA0ODYsLTExNCA0ODAsLTEyMCA0NzQsLTEyMCIvPgo8dGV4dCB0ZXh0LWFuY2hvcj0ibWlkZGxlIiB4PSI0MTYiIHk9Ii0xMDQuNCIgZm9udC1mYW1pbHk9IkRlamFWdSBTYW5zIiBmb250LXNpemU9IjkuNTAiPmxpdmUuU2Vzc2lvbjwvdGV4dD4KPHRleHQgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iNDE2IiB5PSItOTQuNCIgZm9udC1mYW1pbHk9IkRlamFWdSBTYW5zIiBmb250LXNpemU9IjkuNTAiPnN0YXRlICsgY29tbWFuZCBxdWV1ZTwvdGV4dD4KPC9nPgo8IS0tIGZhY2FkZSYjNDU7Jmd0O3Nlc3Npb24gLS0+CjxnIGlkPSJlZGdlMiIgY2xhc3M9ImVkZ2UiPgo8dGl0bGU+ZmFjYWRlJiM0NTsmZ3Q7c2Vzc2lvbjwvdGl0bGU+CjxwYXRoIGZpbGw9Im5vbmUiIHN0cm9rZT0iIzUzNmI3YSIgZD0iTTI5Ny4yMSwtMTAyQzMxMC4zNSwtMTAyIDMyNC42LC0xMDIgMzM4LjUsLTEwMiIvPgo8cG9seWdvbiBmaWxsPSIjNTM2YjdhIiBzdHJva2U9IiM1MzZiN2EiIHBvaW50cz0iMzM4LjczLC0xMDQuNDUgMzQ1LjczLC0xMDIgMzM4LjczLC05OS41NSAzMzguNzMsLTEwNC40NSIvPgo8L2c+CjwhLS0gdHJhbnNwb3J0IC0tPgo8ZyBpZD0ibm9kZTQiIGNsYXNzPSJub2RlIj4KPHRpdGxlPnRyYW5zcG9ydDwvdGl0bGU+CjxwYXRoIGZpbGw9IiNlNGY1ZWQiIHN0cm9rZT0iIzI0NDQ1ZiIgZD0iTTc2NC41LC0xOTJDNzY0LjUsLTE5MiA2NjUuNSwtMTkyIDY2NS41LC0xOTIgNjU5LjUsLTE5MiA2NTMuNSwtMTg2IDY1My41LC0xODAgNjUzLjUsLTE4MCA2NTMuNSwtMTY4IDY1My41LC0xNjggNjUzLjUsLTE2MiA2NTkuNSwtMTU2IDY2NS41LC0xNTYgNjY1LjUsLTE1NiA3NjQuNSwtMTU2IDc2NC41LC0xNTYgNzcwLjUsLTE1NiA3NzYuNSwtMTYyIDc3Ni41LC0xNjggNzc2LjUsLTE2OCA3NzYuNSwtMTgwIDc3Ni41LC0xODAgNzc2LjUsLTE4NiA3NzAuNSwtMTkyIDc2NC41LC0xOTIiLz4KPHRleHQgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iNzE1IiB5PSItMTc2LjQiIGZvbnQtZmFtaWx5PSJEZWphVnUgU2FucyIgZm9udC1zaXplPSI5LjUwIj5UcmFuc3BvcnQ8L3RleHQ+Cjx0ZXh0IHRleHQtYW5jaG9yPSJtaWRkbGUiIHg9IjcxNSIgeT0iLTE2Ni40IiBmb250LWZhbWlseT0iRGVqYVZ1IFNhbnMiIGZvbnQtc2l6ZT0iOS41MCI+c2lkZWJhbmQgLyBzZXJ2ZXIgV1M8L3RleHQ+CjwvZz4KPCEtLSBzZXNzaW9uJiM0NTsmZ3Q7dHJhbnNwb3J0IC0tPgo8ZyBpZD0iZWRnZTMiIGNsYXNzPSJlZGdlIj4KPHRpdGxlPnNlc3Npb24mIzQ1OyZndDt0cmFuc3BvcnQ8L3RpdGxlPgo8cGF0aCBmaWxsPSJub25lIiBzdHJva2U9IiM1MzZiN2EiIGQ9Ik00OTMuMTcsLTEyMC40N0M1NDAuNDYsLTEzMS45MyA2MDAuNjgsLTE0Ni41MyA2NDYuMjksLTE1Ny41OSIvPgo8cG9seWdvbiBmaWxsPSIjNTM2YjdhIiBzdHJva2U9IiM1MzZiN2EiIHBvaW50cz0iNDkzLjY0LC0xMTguMDYgNDg2LjI2LC0xMTguNzkgNDkyLjQ4LC0xMjIuODIgNDkzLjY0LC0xMTguMDYiLz4KPHBvbHlnb24gZmlsbD0iIzUzNmI3YSIgc3Ryb2tlPSIjNTM2YjdhIiBwb2ludHM9IjY0NS44MiwtMTU5Ljk5IDY1My4yLC0xNTkuMjYgNjQ2Ljk3LC0xNTUuMjMgNjQ1LjgyLC0xNTkuOTkiLz4KPHRleHQgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iNTYzIiB5PSItMTUwLjIiIGZvbnQtZmFtaWx5PSJEZWphVnUgU2FucyIgZm9udC1zaXplPSI4LjUwIj50eXBlZCBjb21tYW5kcy9ldmVudHM8L3RleHQ+CjwvZz4KPCEtLSBqcyAtLT4KPGcgaWQ9Im5vZGUxMCIgY2xhc3M9Im5vZGUiPgo8dGl0bGU+anM8L3RpdGxlPgo8cGF0aCBmaWxsPSIjZWVmNGZmIiBzdHJva2U9IiMyNDQ0NWYiIGQ9Ik03NzgsLTEyMEM3NzgsLTEyMCA2NTIsLTEyMCA2NTIsLTEyMCA2NDYsLTEyMCA2NDAsLTExNCA2NDAsLTEwOCA2NDAsLTEwOCA2NDAsLTk2IDY0MCwtOTYgNjQwLC05MCA2NDYsLTg0IDY1MiwtODQgNjUyLC04NCA3NzgsLTg0IDc3OCwtODQgNzg0LC04NCA3OTAsLTkwIDc5MCwtOTYgNzkwLC05NiA3OTAsLTEwOCA3OTAsLTEwOCA3OTAsLTExNCA3ODQsLTEyMCA3NzgsLTEyMCIvPgo8dGV4dCB0ZXh0LWFuY2hvcj0ibWlkZGxlIiB4PSI3MTUiIHk9Ii0xMDQuNCIgZm9udC1mYW1pbHk9IkRlamFWdSBTYW5zIiBmb250LXNpemU9IjkuNTAiPkdvamEgbGl2ZSYjNDU7c2Vzc2lvbiBBUEk8L3RleHQ+Cjx0ZXh0IHRleHQtYW5jaG9yPSJtaWRkbGUiIHg9IjcxNSIgeT0iLTk0LjQiIGZvbnQtZmFtaWx5PSJEZWphVnUgU2FucyIgZm9udC1zaXplPSI5LjUwIj5zZXJ2ZXImIzQ1O21hbmFnZWQgdXNlIGNhc2VzPC90ZXh0Pgo8L2c+CjwhLS0gc2Vzc2lvbiYjNDU7Jmd0O2pzIC0tPgo8ZyBpZD0iZWRnZTExIiBjbGFzcz0iZWRnZSI+Cjx0aXRsZT5zZXNzaW9uJiM0NTsmZ3Q7anM8L3RpdGxlPgo8cGF0aCBmaWxsPSJub25lIiBzdHJva2U9IiM1MzZiN2EiIGQ9Ik00OTMuMzksLTEwMkM1MzYuMSwtMTAyIDU4OS4zMiwtMTAyIDYzMi43OSwtMTAyIi8+Cjxwb2x5Z29uIGZpbGw9IiM1MzZiN2EiIHN0cm9rZT0iIzUzNmI3YSIgcG9pbnRzPSI0OTMuMjYsLTk5LjU1IDQ4Ni4yNiwtMTAyIDQ5My4yNiwtMTA0LjQ1IDQ5My4yNiwtOTkuNTUiLz4KPHBvbHlnb24gZmlsbD0iIzUzNmI3YSIgc3Ryb2tlPSIjNTM2YjdhIiBwb2ludHM9IjYzMi45NSwtMTA0LjQ1IDYzOS45NSwtMTAyIDYzMi45NSwtOTkuNTUgNjMyLjk1LC0xMDQuNDUiLz4KPHRleHQgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iNTYzIiB5PSItMTA0LjIiIGZvbnQtZmFtaWx5PSJEZWphVnUgU2FucyIgZm9udC1zaXplPSI4LjUwIj5jb250cm9sIC8gb2JzZXJ2YXRpb248L3RleHQ+CjwvZz4KPCEtLSByZWR1Y2VyIC0tPgo8ZyBpZD0ibm9kZTUiIGNsYXNzPSJub2RlIj4KPHRpdGxlPnJlZHVjZXI8L3RpdGxlPgo8cGF0aCBmaWxsPSIjZTRmNWVkIiBzdHJva2U9IiMyNDQ0NWYiIGQ9Ik0xMDU1LC0xMDJDMTA1NSwtMTAyIDkxMCwtMTAyIDkxMCwtMTAyIDkwNCwtMTAyIDg5OCwtOTYgODk4LC05MCA4OTgsLTkwIDg5OCwtNzggODk4LC03OCA4OTgsLTcyIDkwNCwtNjYgOTEwLC02NiA5MTAsLTY2IDEwNTUsLTY2IDEwNTUsLTY2IDEwNjEsLTY2IDEwNjcsLTcyIDEwNjcsLTc4IDEwNjcsLTc4IDEwNjcsLTkwIDEwNjcsLTkwIDEwNjcsLTk2IDEwNjEsLTEwMiAxMDU1LC0xMDIiLz4KPHRleHQgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iOTgyLjUiIHk9Ii04Ni40IiBmb250LWZhbWlseT0iRGVqYVZ1IFNhbnMiIGZvbnQtc2l6ZT0iOS41MCI+UHJvdG9jb2wgcmVkdWNlcjwvdGV4dD4KPHRleHQgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iOTgyLjUiIHk9Ii03Ni40IiBmb250LWZhbWlseT0iRGVqYVZ1IFNhbnMiIGZvbnQtc2l6ZT0iOS41MCI+cHJvdmlkZXIgZXZlbnQgJiM0NTsmZ3Q7IHN0YXRlL2VmZmVjdHM8L3RleHQ+CjwvZz4KPCEtLSB0cmFuc3BvcnQmIzQ1OyZndDtyZWR1Y2VyIC0tPgo8ZyBpZD0iZWRnZTQiIGNsYXNzPSJlZGdlIj4KPHRpdGxlPnRyYW5zcG9ydCYjNDU7Jmd0O3JlZHVjZXI8L3RpdGxlPgo8cGF0aCBmaWxsPSJub25lIiBzdHJva2U9IiM1MzZiN2EiIGQ9Ik03NjIuMTcsLTE1NS45N0M3NzguNDgsLTE0OS43NyA3OTYuOTksLTE0Mi45IDgxNCwtMTM3IDg0Ni45NSwtMTI1LjU4IDg4My44OSwtMTEzLjc4IDkxNC42NywtMTA0LjIzIi8+Cjxwb2x5Z29uIGZpbGw9IiM1MzZiN2EiIHN0cm9rZT0iIzUzNmI3YSIgcG9pbnRzPSI5MTUuNTgsLTEwNi41MSA5MjEuNTUsLTEwMi4xIDkxNC4xNCwtMTAxLjgzIDkxNS41OCwtMTA2LjUxIi8+Cjx0ZXh0IHRleHQtYW5jaG9yPSJtaWRkbGUiIHg9Ijg0NCIgeT0iLTEzOS4yIiBmb250LWZhbWlseT0iRGVqYVZ1IFNhbnMiIGZvbnQtc2l6ZT0iOC41MCI+c2VydmVyIGV2ZW50czwvdGV4dD4KPC9nPgo8IS0tIHJlZHVjZXImIzQ1OyZndDtzZXNzaW9uIC0tPgo8ZyBpZD0iZWRnZTUiIGNsYXNzPSJlZGdlIj4KPHRpdGxlPnJlZHVjZXImIzQ1OyZndDtzZXNzaW9uPC90aXRsZT4KPHBhdGggZmlsbD0ibm9uZSIgc3Ryb2tlPSIjNTM2YjdhIiBkPSJNODk3Ljg3LC02OS42MkM4NjQuNDQsLTY0LjU1IDgyNS41LC01OS40OSA3OTAsLTU3IDcyMy41LC01Mi4zMyA3MDYuMzQsLTUwLjM3IDY0MCwtNTcgNTkwLjY3LC02MS45MyA1MzYuMTEsLTcyLjg0IDQ5My4zLC04Mi42OCIvPgo8cG9seWdvbiBmaWxsPSIjNTM2YjdhIiBzdHJva2U9IiM1MzZiN2EiIHBvaW50cz0iNDkyLjUzLC04MC4zNSA0ODYuMjcsLTg0LjMyIDQ5My42NCwtODUuMTIgNDkyLjUzLC04MC4zNSIvPgo8dGV4dCB0ZXh0LWFuY2hvcj0ibWlkZGxlIiB4PSI3MTUiIHk9Ii01OS4yIiBmb250LWZhbWlseT0iRGVqYVZ1IFNhbnMiIGZvbnQtc2l6ZT0iOC41MCI+c3RhdGUgdHJhbnNpdGlvbnM8L3RleHQ+CjwvZz4KPCEtLSBtaXJyb3IgLS0+CjxnIGlkPSJub2RlNiIgY2xhc3M9Im5vZGUiPgo8dGl0bGU+bWlycm9yPC90aXRsZT4KPHBhdGggZmlsbD0iI2VlZjRmZiIgc3Ryb2tlPSIjMjQ0NDVmIiBkPSJNMTI2OCwtMTA4QzEyNjgsLTEwOCAxMTI4LC0xMDggMTEyOCwtMTA4IDExMjIsLTEwOCAxMTE2LC0xMDIgMTExNiwtOTYgMTExNiwtOTYgMTExNiwtODQgMTExNiwtODQgMTExNiwtNzggMTEyMiwtNzIgMTEyOCwtNzIgMTEyOCwtNzIgMTI2OCwtNzIgMTI2OCwtNzIgMTI3NCwtNzIgMTI4MCwtNzggMTI4MCwtODQgMTI4MCwtODQgMTI4MCwtOTYgMTI4MCwtOTYgMTI4MCwtMTAyIDEyNzQsLTEwOCAxMjY4LC0xMDgiLz4KPHRleHQgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iMTE5OCIgeT0iLTkyLjQiIGZvbnQtZmFtaWx5PSJEZWphVnUgU2FucyIgZm9udC1zaXplPSI5LjUwIj5Db252ZXJzYXRpb25NaXJyb3I8L3RleHQ+Cjx0ZXh0IHRleHQtYW5jaG9yPSJtaWRkbGUiIHg9IjExOTgiIHk9Ii04Mi40IiBmb250LWZhbWlseT0iRGVqYVZ1IFNhbnMiIGZvbnQtc2l6ZT0iOS41MCI+cHJvdmlkZXIgSURzICsgc3RhYmxlIGJhcnJpZXJzPC90ZXh0Pgo8L2c+CjwhLS0gcmVkdWNlciYjNDU7Jmd0O21pcnJvciAtLT4KPGcgaWQ9ImVkZ2U2IiBjbGFzcz0iZWRnZSI+Cjx0aXRsZT5yZWR1Y2VyJiM0NTsmZ3Q7bWlycm9yPC90aXRsZT4KPHBhdGggZmlsbD0ibm9uZSIgc3Ryb2tlPSIjNTM2YjdhIiBkPSJNMTA2Ny4yNywtODYuMzVDMTA4MC45LC04Ni43NCAxMDk1LjA1LC04Ny4xMyAxMTA4Ljc4LC04Ny41MiIvPgo8cG9seWdvbiBmaWxsPSIjNTM2YjdhIiBzdHJva2U9IiM1MzZiN2EiIHBvaW50cz0iMTEwOC44NSwtODkuOTcgMTExNS45MiwtODcuNzIgMTEwOC45OSwtODUuMDggMTEwOC44NSwtODkuOTciLz4KPC9nPgo8IS0tIHRvb2wgLS0+CjxnIGlkPSJub2RlNyIgY2xhc3M9Im5vZGUiPgo8dGl0bGU+dG9vbDwvdGl0bGU+CjxwYXRoIGZpbGw9IiNlZWY0ZmYiIHN0cm9rZT0iIzI0NDQ1ZiIgZD0iTTEyNDMsLTE4N0MxMjQzLC0xODcgMTE1MywtMTg3IDExNTMsLTE4NyAxMTQ3LC0xODcgMTE0MSwtMTgxIDExNDEsLTE3NSAxMTQxLC0xNzUgMTE0MSwtMTYzIDExNDEsLTE2MyAxMTQxLC0xNTcgMTE0NywtMTUxIDExNTMsLTE1MSAxMTUzLC0xNTEgMTI0MywtMTUxIDEyNDMsLTE1MSAxMjQ5LC0xNTEgMTI1NSwtMTU3IDEyNTUsLTE2MyAxMjU1LC0xNjMgMTI1NSwtMTc1IDEyNTUsLTE3NSAxMjU1LC0xODEgMTI0OSwtMTg3IDEyNDMsLTE4NyIvPgo8dGV4dCB0ZXh0LWFuY2hvcj0ibWlkZGxlIiB4PSIxMTk4IiB5PSItMTcxLjQiIGZvbnQtZmFtaWx5PSJEZWphVnUgU2FucyIgZm9udC1zaXplPSI5LjUwIj5Ub29sRGlzcGF0Y2hlcjwvdGV4dD4KPHRleHQgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iMTE5OCIgeT0iLTE2MS40IiBmb250LWZhbWlseT0iRGVqYVZ1IFNhbnMiIGZvbnQtc2l6ZT0iOS41MCI+cmVnaXN0cnkgKyBleGVjdXRvcjwvdGV4dD4KPC9nPgo8IS0tIHJlZHVjZXImIzQ1OyZndDt0b29sIC0tPgo8ZyBpZD0iZWRnZTciIGNsYXNzPSJlZGdlIj4KPHRpdGxlPnJlZHVjZXImIzQ1OyZndDt0b29sPC90aXRsZT4KPHBhdGggZmlsbD0ibm9uZSIgc3Ryb2tlPSIjNTM2YjdhIiBkPSJNMTAyOC43OCwtMTAyLjAzQzEwNjIuODksLTExNS42MSAxMTA5LjcsLTEzNC4yNCAxMTQ1LjI4LC0xNDguNDEiLz4KPHBvbHlnb24gZmlsbD0iIzUzNmI3YSIgc3Ryb2tlPSIjNTM2YjdhIiBwb2ludHM9IjExNDQuMzgsLTE1MC42OSAxMTUxLjc5LC0xNTEgMTE0Ni4xOSwtMTQ2LjEzIDExNDQuMzgsLTE1MC42OSIvPgo8L2c+CjwhLS0gc2luayAtLT4KPGcgaWQ9Im5vZGU4IiBjbGFzcz0ibm9kZSI+Cjx0aXRsZT5zaW5rPC90aXRsZT4KPHBhdGggZmlsbD0iI2VlZjRmZiIgc3Ryb2tlPSIjMjQ0NDVmIiBkPSJNMTI2MSwtMzZDMTI2MSwtMzYgMTEzNSwtMzYgMTEzNSwtMzYgMTEyOSwtMzYgMTEyMywtMzAgMTEyMywtMjQgMTEyMywtMjQgMTEyMywtMTIgMTEyMywtMTIgMTEyMywtNiAxMTI5LDAgMTEzNSwwIDExMzUsMCAxMjYxLDAgMTI2MSwwIDEyNjcsMCAxMjczLC02IDEyNzMsLTEyIDEyNzMsLTEyIDEyNzMsLTI0IDEyNzMsLTI0IDEyNzMsLTMwIDEyNjcsLTM2IDEyNjEsLTM2Ii8+Cjx0ZXh0IHRleHQtYW5jaG9yPSJtaWRkbGUiIHg9IjExOTgiIHk9Ii0yMC40IiBmb250LWZhbWlseT0iRGVqYVZ1IFNhbnMiIGZvbnQtc2l6ZT0iOS41MCI+ZXZlbnRzLkV2ZW50U2luazwvdGV4dD4KPHRleHQgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iMTE5OCIgeT0iLTEwLjQiIGZvbnQtZmFtaWx5PSJEZWphVnUgU2FucyIgZm9udC1zaXplPSI5LjUwIj5jYW5vbmljYWwgc2VtYW50aWMgZXZlbnRzPC90ZXh0Pgo8L2c+CjwhLS0gcmVkdWNlciYjNDU7Jmd0O3NpbmsgLS0+CjxnIGlkPSJlZGdlOCIgY2xhc3M9ImVkZ2UiPgo8dGl0bGU+cmVkdWNlciYjNDU7Jmd0O3Npbms8L3RpdGxlPgo8cGF0aCBmaWxsPSJub25lIiBzdHJva2U9IiM1MzZiN2EiIGQ9Ik0xMDQxLjg0LC02NS45N0MxMDY5LjczLC01Ny4zNCAxMTAzLjIxLC00Ni45OSAxMTMxLjkyLC0zOC4xMiIvPgo8cG9seWdvbiBmaWxsPSIjNTM2YjdhIiBzdHJva2U9IiM1MzZiN2EiIHBvaW50cz0iMTEzMi43NywtNDAuNDIgMTEzOC43MywtMzYuMDEgMTEzMS4zMiwtMzUuNzQgMTEzMi43NywtNDAuNDIiLz4KPC9nPgo8IS0tIHN0b3JlIC0tPgo8ZyBpZD0ibm9kZTkiIGNsYXNzPSJub2RlIj4KPHRpdGxlPnN0b3JlPC90aXRsZT4KPHBhdGggZmlsbD0iI2VlZjRmZiIgc3Ryb2tlPSIjMjQ0NDVmIiBkPSJNMTQ1NywtMTA4QzE0NTcsLTEwOCAxMzQxLC0xMDggMTM0MSwtMTA4IDEzMzUsLTEwOCAxMzI5LC0xMDIgMTMyOSwtOTYgMTMyOSwtOTYgMTMyOSwtODQgMTMyOSwtODQgMTMyOSwtNzggMTMzNSwtNzIgMTM0MSwtNzIgMTM0MSwtNzIgMTQ1NywtNzIgMTQ1NywtNzIgMTQ2MywtNzIgMTQ2OSwtNzggMTQ2OSwtODQgMTQ2OSwtODQgMTQ2OSwtOTYgMTQ2OSwtOTYgMTQ2OSwtMTAyIDE0NjMsLTEwOCAxNDU3LC0xMDgiLz4KPHRleHQgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iMTM5OSIgeT0iLTg3LjQiIGZvbnQtZmFtaWx5PSJEZWphVnUgU2FucyIgZm9udC1zaXplPSI5LjUwIj5UdXJuL3Nlc3Npb24gcGVyc2lzdGVuY2U8L3RleHQ+CjwvZz4KPCEtLSBtaXJyb3ImIzQ1OyZndDtzdG9yZSAtLT4KPGcgaWQ9ImVkZ2U5IiBjbGFzcz0iZWRnZSI+Cjx0aXRsZT5taXJyb3ImIzQ1OyZndDtzdG9yZTwvdGl0bGU+CjxwYXRoIGZpbGw9Im5vbmUiIHN0cm9rZT0iIzUzNmI3YSIgZD0iTTEyODAuMjMsLTkwQzEyOTMuOTYsLTkwIDEzMDguMTYsLTkwIDEzMjEuNzYsLTkwIi8+Cjxwb2x5Z29uIGZpbGw9IiM1MzZiN2EiIHN0cm9rZT0iIzUzNmI3YSIgcG9pbnRzPSIxMzIxLjgxLC05Mi40NSAxMzI4LjgxLC05MCAxMzIxLjgxLC04Ny41NSAxMzIxLjgxLC05Mi40NSIvPgo8L2c+CjwhLS0gdG9vbCYjNDU7Jmd0O3RyYW5zcG9ydCAtLT4KPGcgaWQ9ImVkZ2UxMCIgY2xhc3M9ImVkZ2UiPgo8dGl0bGU+dG9vbCYjNDU7Jmd0O3RyYW5zcG9ydDwvdGl0bGU+CjxwYXRoIGZpbGw9Im5vbmUiIHN0cm9rZT0iIzUzNmI3YSIgZD0iTTExNDAuNjgsLTE2OS41OUMxMDUxLjg1LC0xNzAuNTEgODc5LjUxLC0xNzIuMyA3ODMuOTUsLTE3My4yOSIvPgo8cG9seWdvbiBmaWxsPSIjNTM2YjdhIiBzdHJva2U9IiM1MzZiN2EiIHBvaW50cz0iNzgzLjg5LC0xNzAuODQgNzc2LjkyLC0xNzMuMzcgNzgzLjk0LC0xNzUuNzQgNzgzLjg5LC0xNzAuODQiLz4KPHRleHQgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iOTgyLjUiIHk9Ii0xNzQuMiIgZm9udC1mYW1pbHk9IkRlamFWdSBTYW5zIiBmb250LXNpemU9IjguNTAiPmZ1bmN0aW9uIG91dHB1dCArIHJlc3BvbnNlLmNyZWF0ZTwvdGV4dD4KPC9nPgo8L2c+Cjwvc3ZnPgo=">

## 7.1 Proposed package layout

```text
pkg/inference/live/
  types.go                 # IDs, states, snapshots
  config.go                # provider-neutral live config
  command.go               # reliable commands
  session.go               # lifecycle, queues, Done/Err/Close
  controller.go            # open and attach operations
  transport.go             # provider-neutral duplex transport
  reducer.go               # generic reducer contracts/effects
  mirror.go                # stable semantic conversation state
  tool_dispatcher.go       # reliable tool loop integration
  persistence.go           # stable barrier interface
  errors.go

pkg/steps/ai/openai_realtime/
  settings.go
  client_secret.go
  unified_sdp.go
  websocket_transport.go
  sideband.go
  protocol_client_events.go
  protocol_server_events.go
  reducer.go
  event_mapper.go
  tool_mapper.go
  observability.go
  testdata/*.jsonl

pkg/events/live_events.go
pkg/js/modules/geppetto/api_live_session.go
pkg/js/modules/geppetto/api_live_event_payloads.go
```

The uploaded repository does not contain a browser UI/media package. Browser TypeScript should therefore be a distinct deliverable or downstream package, for example:

```text
web/realtime/
  voice_session.ts
  openai_webrtc_transport.ts
  audio_devices.ts
  event_types.ts
  browser_metrics.ts
```

## 7.2 Core lifecycle interfaces

```go
package live

type State string

const (
    StateNew        State = "new"
    StateConnecting State = "connecting"
    StateActive     State = "active"
    StateClosing    State = "closing"
    StateClosed     State = "closed"
    StateFailed     State = "failed"
)

type Session interface {
    ID() string
    State() State
    Send(ctx context.Context, cmd Command) error
    Snapshot() Snapshot
    Done() <-chan struct{}
    Err() error
    Close(ctx context.Context) error
}

type Controller interface {
    OpenServerSession(ctx context.Context, cfg SessionConfig) (Session, error)
    AttachSideband(ctx context.Context, callID string, cfg AttachConfig) (Session, error)
}

type BrowserBootstrapService interface {
    CreateClientSecret(
        ctx context.Context,
        req BootstrapRequest,
    ) (*ClientSecretBootstrap, error)

    AnswerWebRTC(
        ctx context.Context,
        req WebRTCOfferRequest,
    ) (*WebRTCAnswer, error)
}
```

`Session.Send` is for low-rate reliable commands. It is not for raw WebRTC media.

## 7.3 Transport interface

```go
type Transport interface {
    Send(ctx context.Context, event ClientEvent) error
    Receive(ctx context.Context) (ServerEvent, error)
    Close(ctx context.Context) error
}
```

Implementation rules:

- exactly one read pump owns `Receive`;
- exactly one write pump serializes protocol writes;
- callers submit to a bounded command queue;
- terminal error is recorded once;
- context cancellation stops pumps and tool work;
- callbacks/events are never invoked while internal locks are held;
- oversized provider events and audio payloads are bounded before logging.

For direct browser WebRTC, Geppetto's `Transport` is the sideband WebSocket, not the browser media connection. Browser control events can be mirrored or observed through the same OpenAI call.

## 7.4 Commands

Start with explicit typed commands:

```go
type Command interface { isLiveCommand() }

type UpdateSession struct { Patch SessionPatch }
type CreateConversationItem struct { Item ItemInput }
type CreateResponse struct { Response ResponseRequest }
type CancelResponse struct { ResponseID string }
type CommitInputAudio struct{}
type ClearInputAudio struct{}
type AppendInputAudio struct { PCM []byte } // server WebSocket only
type TruncateItem struct {
    ProviderItemID string
    ContentIndex   int
    AudioEndMS     int64
}
type SendToolOutput struct {
    CallID string
    JSON   string
}
type Close struct { Reason string }
```

Avoid a generic `SendJSON(any)` in the public live package. The adapter can expose an escape hatch under an explicitly unstable/debug namespace, but normal code should be compile-time checked.

## 7.5 Provider protocol reducer

The OpenAI adapter should decode into exact event structs and reduce them through a deterministic state machine:

```go
type Reduction struct {
    NewState ProviderState
    Events   []events.Event
    Effects  []Effect
    Barriers []PersistenceBarrier
}

func Reduce(state ProviderState, event ServerEvent) (Reduction, error)
```

Effects can include:

- enqueue tool execution;
- send tool output;
- send `response.create`;
- persist final transcript;
- mark response cancelled;
- record usage/rate limit;
- close or fail session.

Pure reducer tests can replay JSONL fixtures without network access.

## 7.6 Session state machine

```text
New -> Connecting -> Active -> Closing -> Closed
                  \-> Failed
Active -----------> Failed
Closing ----------> Failed
```

State transitions must be monotonic. `Close` is idempotent. `Err()` returns nil for an orderly close and a terminal cause for failure. A failed sideband does not necessarily stop browser audio immediately; policy should decide whether to fail closed, attempt reattach, or allow a tool-free degraded mode.

Recommended default:

- if privileged tools are advertised, sideband loss fails closed and the browser is instructed to end the call;
- if the session is explicitly tool-free, sideband loss may degrade to local browser operation while emitting a high-severity event.

## 7.7 Live settings

Add a separate settings block rather than overloading `Chat.Stream`:

```go
type RealtimeSettings struct {
    Model              string
    Voice              string
    OutputModalities   []string
    Transport          string // webrtc_direct, server_websocket
    BootstrapMode      string // unified_sdp, client_secret
    SidebandRequired   bool

    InputFormat        AudioFormat
    OutputFormat       AudioFormat
    InputTranscription *TranscriptionSettings
    NoiseReduction     *NoiseReductionSettings
    TurnDetection      TurnDetectionSettings

    ReasoningEffort    string
    MaxOutputTokens    int
    Truncation         TruncationSettings
    Include            []string

    ClientSecretTTL    time.Duration
    MaxSessionAge      time.Duration
    RolloverLead       time.Duration
    Profile            string
}
```

Configuration rules:

- model and voice are selected by profile;
- validate transport-specific fields;
- validate PCM rates against provider support;
- reject client-secret TTL outside provider limits;
- require sideband when privileged tools are present;
- lock voice selection before first audio output;
- do not hard-code `gpt-realtime-2.1`; current docs identify `gpt-realtime-2` as the strongest reasoning voice family while examples use point releases. [OAI-REALTIME-MODELS] [OAI-WEBRTC]

## 7.8 Factory integration

```go
type LiveSessionFactory interface {
    BuildController(
        ctx context.Context,
        settings *settings.InferenceSettings,
        deps Dependencies,
    ) (live.Controller, error)
}
```

`engine/factory` remains unchanged except for shared dependency helpers. A higher-level `AgentFactory` may expose both finite and live construction, but their return types remain distinct.

## 7.9 Official SDK versus protocol types

The current official Go SDK exposes Realtime REST/session/client-secret/call types. Geppetto can use it for authenticated REST operations if it fits dependency policy. The live WebSocket pump should still remain behind Geppetto's `Transport` interface so protocol handling, reconnect behavior, tests, and logging are under project control. Avoid leaking SDK structs across the provider-neutral `live` package.



# 8. Browser client design {#browser-client-design}

## 8.1 Browser WebRTC responsibilities

The browser package should own:

- user-gesture-gated microphone permission;
- input/output device selection;
- `RTCPeerConnection` lifecycle;
- microphone track enable/disable;
- remote audio element/stream;
- data-channel serialization and event dispatch;
- browser connection state and metrics;
- sideband-ready gating;
- accessibility captions from transcript events;
- explicit close and cleanup.

It should not own privileged tool implementations or permanent credentials.

## 8.2 Recommended unified-bootstrap sketch

```ts
type BootstrapAnswer = {
  sdp: string;
  geppettoSessionId: string;
  callId?: string; // backend may keep this opaque
};

export async function connectRealtimeVoice(): Promise<RTCPeerConnection> {
  // Call from a user click so microphone and audio playback are allowed.
  const pc = new RTCPeerConnection();
  const dc = pc.createDataChannel("oai-events");

  const output = document.createElement("audio");
  output.autoplay = true;
  output.playsInline = true;
  pc.ontrack = (event) => {
    output.srcObject = event.streams[0];
  };

  const media = await navigator.mediaDevices.getUserMedia({
    audio: {
      echoCancellation: true,
      noiseSuppression: true,
      autoGainControl: true,
      channelCount: 1,
    },
  });

  const track = media.getAudioTracks()[0];
  track.enabled = false; // enable only after sideband-ready response
  pc.addTrack(track, media);

  dc.addEventListener("message", (event) => {
    const message = JSON.parse(String(event.data));
    dispatchRealtimeEvent(message);
  });

  const offer = await pc.createOffer();
  await pc.setLocalDescription(offer);

  const response = await fetch("/api/live/openai/webrtc", {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/sdp",
      "X-CSRF-Token": readCsrfToken(),
    },
    body: offer.sdp,
  });
  if (!response.ok) throw new Error(`bootstrap failed: ${response.status}`);

  const answer = await response.json() as BootstrapAnswer;
  await pc.setRemoteDescription({ type: "answer", sdp: answer.sdp });

  await waitForDataChannelOpen(dc);
  await waitForSidebandReady(answer.geppettoSessionId);
  track.enabled = true;
  return pc;
}
```

The actual response can return raw `application/sdp` plus metadata headers instead of JSON. JSON is shown to make correlation explicit; either contract is acceptable if carefully specified.

## 8.3 Ephemeral-secret sketch

```ts
const tokenResponse = await fetch("/api/live/openai/client-secret", {
  method: "POST",
  credentials: "include",
  headers: { "X-CSRF-Token": readCsrfToken() },
});
const bootstrap = await tokenResponse.json();

const sdpResponse = await fetch("https://api.openai.com/v1/realtime/calls", {
  method: "POST",
  body: offer.sdp,
  headers: {
    Authorization: `Bearer ${bootstrap.clientSecret}`,
    "Content-Type": "application/sdp",
  },
});

const location = sdpResponse.headers.get("Location");
const callId = location?.split("/").pop();
if (!callId) throw new Error("missing realtime call id");

await fetch(`/api/live/${bootstrap.geppettoSessionId}/attach`, {
  method: "POST",
  credentials: "include",
  headers: {
    "Content-Type": "application/json",
    "X-CSRF-Token": readCsrfToken(),
  },
  body: JSON.stringify({ callId }),
});
```

Keep the microphone disabled until attach acknowledgement. Never log the client secret or put it in a URL/query string.

## 8.4 Browser event surface

Expose provider-neutral events, while allowing an optional raw debug stream:

```ts
type VoiceEvents = {
  "state-changed": { from: VoiceState; to: VoiceState };
  "input-speech-started": { at: number };
  "input-speech-stopped": { at: number };
  "input-transcript-delta": { itemId: string; delta: string };
  "input-transcript-finished": { itemId: string; text: string };
  "output-transcript-delta": { responseId: string; delta: string };
  "output-transcript-finished": { responseId: string; text: string };
  "tool-call-started": ToolCallView;
  "tool-call-finished": ToolResultView;
  "interrupted": { responseId?: string };
  "error": { code: string; message: string; recoverable: boolean };
};
```

Raw OpenAI events may be exposed only under `debug.onProviderEvent` with redaction and size limits.

## 8.5 Device and browser edge cases

- Begin connection from a user gesture to satisfy microphone and autoplay restrictions.
- Handle permission denial distinctly from network failure.
- Listen for `devicechange`; do not silently switch microphones during a sensitive call.
- Stop all media tracks and close the data channel/peer connection on teardown.
- Surface `connectionState`, `iceConnectionState`, and data-channel state.
- Treat page suspension/background throttling as a possible call-quality event.
- Avoid rendering every transcript delta through a large framework tree; batch UI updates at animation-frame cadence.
- Test browser echo cancellation together with provider noise reduction. More processing is not always better.

## 8.6 Browser audio proxy implementation details

For the optional backend proxy:

- capture and playback in `AudioWorkletProcessor` instances;
- use bounded ring buffers;
- use `WebSocket.bufferedAmount` thresholds;
- send sequence number, sample count, and capture timestamp in a compact binary header;
- resample using a stateful filter, not independent per-frame naive interpolation;
- do not spawn an `AudioBufferSourceNode` for every small output chunk;
- track **played samples** for interruption, not queued samples;
- if `SharedArrayBuffer` is used, configure cross-origin isolation deliberately; otherwise use transferable buffers and account for copying.



# 9. Backend endpoint and sideband design {#backend-design}

## 9.1 Endpoint set

A minimal production API can expose:

```text
POST /api/live/openai/webrtc
  Request:  application/sdp
  Response: answer SDP + Geppetto live session metadata
  Role:     unified SDP bootstrap; server captures call_id and attaches sideband

POST /api/live/openai/client-secret
  Request:  authenticated application request
  Response: short-lived client secret + Geppetto live session ID
  Role:     alternative ephemeral bootstrap

POST /api/live/{sessionID}/attach
  Request:  call_id obtained by browser
  Role:     attach sideband for ephemeral flow

GET /api/live/{sessionID}/status
  Role:     sideband-ready and state checks

POST /api/live/{sessionID}/close
  Role:     explicit user/application termination
```

The first production slice can implement only unified bootstrap, status, and close.

## 9.2 Unified endpoint sequence

```text
Browser              Geppetto                     OpenAI
   | create offer        |                            |
   | POST SDP ---------->|                            |
   |                     | POST multipart sdp+session>|
   |                     |<-- answer + Location -------|
   |                     | connect sideband(call_id) --> WebSocket
   |                     |<-- session.created/updated --|
   |<-- answer + ready --|                            |
   | set remote SDP      |                            |
   | enable microphone   |                            |
   |======= WebRTC media and events ==================>|
```

The endpoint should not return “ready” until:

- OpenAI returned a successful SDP answer;
- a valid `call_id` was captured;
- sideband connected if required;
- initial server-controlled `session.update` was acknowledged or timed out according to policy;
- tool definitions were installed if tools are enabled.

## 9.3 Sideband session ownership

The backend stores a short-lived live-session record:

```go
type LiveRecord struct {
    SessionID       string
    UserID          string
    Provider        string
    ProviderCallID  string // secret/capability-like; encrypt or protect
    State           live.State
    Profile         string
    CreatedAt       time.Time
    SidebandReadyAt *time.Time
    ExpiresAt       time.Time
}
```

Do not expose the provider `call_id` unless the browser flow requires it. Treat it as a capability for attaching to the live call.

## 9.4 Sideband read loop

The sideband loop should:

1. decode a bounded JSON event;
2. attach receive timestamp and provider sequence/debug IDs;
3. reduce into provider state;
4. synchronously enqueue required protocol effects;
5. enqueue tool work on a bounded worker path;
6. emit canonical best-effort events;
7. write persistence barriers asynchronously with ordering per live session;
8. update metrics.

Tool output must be serialized through the single write pump. Event subscribers must never write directly to the WebSocket.

## 9.5 Sideband loss policy

Classify failures:

- **transient network failure before tools are advertised:** retry attach with jitter within a short deadline;
- **loss during a tool-free session:** optional degraded continuation, with clear UI warning;
- **loss while privileged tools are available or running:** fail closed, cancel/close the call, and prevent further tool output;
- **provider reports terminal error:** persist final stable state and close;
- **browser disconnects while sideband remains:** close after a short grace period unless a handoff flow exists.

OpenAI does not turn sideband into an application authorization boundary. Tool handlers remain responsible for user/account authorization.

## 9.6 Go HTTP implementation notes

- Limit SDP request size.
- Enforce `Content-Type` and reject unexpected multipart/browser payloads.
- Set upstream timeouts for OpenAI REST bootstrap.
- Do not retry a successful call creation blindly; retries can create duplicate live calls.
- Generate an idempotency key for application bootstrap and cache the result briefly.
- Propagate a stable, privacy-preserving safety identifier from the trusted backend as documented by OpenAI. [OAI-WEBRTC]
- Redact Authorization, client secrets, SDP, and call IDs from logs.
- Apply the repository's existing outbound URL/local-network safety policies if base URLs are configurable.



# 10. Events, correlation, tools, and persistence {#events-tools-persistence}

## 10.1 Canonical event additions

Add event types in `pkg/events/live_events.go`:

```text
live-session-started
live-session-updated
live-session-ended
live-session-failed

response-started
response-finished
response-cancelled
conversation-item-added
conversation-item-finished

audio-input-started
audio-input-stopped
audio-input-committed
input-transcript-delta
input-transcript-finished
audio-output-started
audio-output-stopped
output-transcript-delta
output-transcript-finished

rate-limits-updated
```

Reuse existing `text-delta`, `text-segment`, error, interrupt, and tool events when their semantics match. Do not duplicate all provider event names one-for-one in the canonical layer.

## 10.2 Correlation mapping

| OpenAI concept | Geppetto mapping |
|---|---|
| one live call/session | canonical `SessionID`; provider call ID in adapter state |
| one model Response | `ProviderCallID` or a response-scoped canonical ID |
| output content/transcript stream | `SegmentID` |
| function `call_id` | `ToolCallID` |
| provider event ID | debug metadata used to correlate errors |
| provider item ID | adapter mirror key and provenance metadata |
| stable user/model exchange | a persisted Turn snapshot |

Provider item IDs are essential internally because deltas and completions can arrive out of order. They should not replace canonical IDs in public routing.

## 10.3 Reliable tool dispatcher

```go
type ToolDispatcher struct {
    Registry tools.ToolRegistry
    Executor tools.ToolExecutor
    Send     func(context.Context, live.Command) error
    Seen     IdempotencyStore // keyed by provider call_id
}
```

Processing steps:

1. Assemble function arguments by provider item/call ID.
2. Validate final JSON against the registered tool schema.
3. Deduplicate the provider `call_id`.
4. Reauthorize the tool against the current application user/session.
5. Apply deadline, cancellation, and confirmation policy.
6. Execute through the existing executor.
7. Emit existing canonical tool lifecycle events.
8. Send `function_call_output` with the same `call_id`.
9. Send `response.create` if the provider does not automatically continue.
10. Persist a stable tool-call/tool-result barrier.

The dispatcher must not subscribe to `EventSink` to discover calls; it receives a reliable reducer effect.

## 10.4 Client-side versus server-side tools

Default rule:

- privileged, data-bearing, or state-changing tools execute on Geppetto;
- harmless UI-only actions may be represented as client events, but should not be advertised as trusted tools unless the backend can verify their result;
- write tools require explicit authorization and, where appropriate, user confirmation;
- tool output is untrusted data until validated and escaped before prompt insertion.

Direct WebRTC should not move tool credentials or internal APIs into the browser.

## 10.5 Conversation mirror

During a live call, maintain a mutable provider mirror:

```go
type ConversationMirror struct {
    Session     SessionSummary
    Items       map[string]*ItemState
    ItemOrder   []string
    Responses   map[string]*ResponseState
    ActiveAudio *PlaybackState
    Usage       UsageState
}
```

The mirror tracks partial deltas, but persistence only occurs at barriers.

## 10.6 Persistence barriers

Recommended stable barriers:

1. user audio is committed and final input transcript arrives;
2. assistant content item is done, or has been correctly truncated after interruption;
3. function call and function output are complete;
4. response is done/cancelled and semantic state is stable;
5. session closes or rolls over.

Do not persist:

- every audio delta;
- every transcript character delta;
- unplayed assistant transcript after interruption;
- provider event objects wholesale;
- secrets, SDP, or raw call IDs in ordinary Turn metadata.

## 10.7 Mapping to Turns

Two reasonable policies exist.

### Exchange-based snapshots

Append one new Turn after a completed user speech turn and the corresponding assistant response/tool cycle. This is closest to current text sessions and easiest for replay.

### Item-based snapshots

Append after each completed meaningful Conversation Item. This captures multi-part and tool-heavy flows more precisely but creates more Turn snapshots.

**Recommendation:** start with exchange-based snapshots and include item provenance metadata. Use item-based persistence only where audits require it.

## 10.8 Interrupted assistant output

WebRTC/SIP automatically truncate unplayed output on user interruption. WebSocket clients must stop playback, track played duration, and send `conversation.item.truncate`. [OAI-CONVERSATIONS]

Persistence must use the post-truncation semantic state. Otherwise Geppetto will store words the user never heard and may replay them as conversation context later.

## 10.9 Transcript source metadata

```go
type TranscriptMeta struct {
    Source          string // input_async, output_audio, output_text, chained_stt
    ProviderModel   string
    ProviderItemID  string
    Final           bool
    Interrupted     bool
    StartMS         int64
    EndMS           int64
    ConfidenceClass string // optional provider-neutral bucket, not invented score
}
```

Do not manufacture confidence values when the provider does not supply them.



# 11. Security and privacy model {#security-and-privacy}

## 11.1 Security boundaries

| Asset or action | Trusted boundary |
|---|---|
| permanent OpenAI API key | Geppetto backend only |
| short-lived client secret | authenticated browser memory, never persistent storage |
| provider call ID | backend capability record; browser only when required |
| tool credentials | backend tool executor only |
| authorization to change external state | backend application policy, not model instructions |
| raw microphone audio | browser/OpenAI by default; backend only in explicit proxy/record mode |
| transcripts | classified application data with explicit retention policy |

## 11.2 Client-secret handling

Official client secrets:

- are short-lived;
- can have a 10-7,200 second TTL;
- default to 600 seconds;
- can create multiple sessions until expiry;
- can carry session configuration that the client may override. [OAI-CLIENT-SECRETS]

Application policy should therefore:

- use 30-60 seconds unless measurements require longer;
- issue only after user/session authorization;
- enforce per-user and per-IP rate/concurrency quotas;
- bind the issuance record to a Geppetto SessionID and expected profile;
- never store the token in localStorage, cookies, URLs, analytics, or logs;
- reject reuse at the application layer where observable, while acknowledging the provider token itself is not guaranteed single-use;
- assume a malicious browser can alter provider session events.

## 11.3 Session configuration is not authorization

Prompts, tool descriptions, `session.update`, and client-secret defaults influence model behavior; they do not authorize access to databases, purchases, email, files, or other state changes.

Every tool invocation must independently establish:

- authenticated user identity;
- tenant/account scope;
- permission for the requested operation;
- validation of arguments;
- confirmation requirements;
- idempotency and replay protection;
- output filtering.

If policy requires preventing the browser from issuing any provider control event, direct WebRTC is not a hard isolation mechanism because the connected client owns a data channel and credential. Use a backend-owned WebSocket/media gateway for that threat model.

## 11.4 Bootstrap endpoint defenses

- authenticated session required;
- CSRF protection for cookie-authenticated requests;
- exact Origin/Host checks;
- restrictive CORS;
- request-body and SDP size limits;
- content-type validation;
- rate limit by user, tenant, IP, and device fingerprint where lawful;
- maximum concurrent live sessions;
- spend/quota checks before call creation;
- no open redirect or user-controlled OpenAI base URL;
- upstream timeout and circuit breaker;
- idempotency record to avoid duplicate calls;
- audit event without storing secrets or SDP.

## 11.5 Audio and transcript privacy

Default privacy posture:

- direct WebRTC, so Geppetto does not receive raw audio;
- no recording;
- final transcript persistence only where product behavior requires it;
- transcript redaction/classification before logs or analytics;
- no raw provider event logging in production by default;
- explicit user notice and consent if recording is added;
- separate retention policy for media, transcript, tool data, and metrics;
- deletion workflow that covers external media objects and derived transcripts.

A request to “record calls” materially changes the architecture. Direct WebRTC does not automatically give the backend an audio copy. Recording would require explicit browser capture/upload, a parallel media path, or the backend proxy topology.

## 11.6 Logging rules

Never log:

- Authorization headers;
- client secrets;
- complete SDP offers/answers;
- raw `call_id` values at normal log levels;
- Base64 audio;
- full tool arguments/results unless a data classification policy allows it;
- full transcripts by default.

Log bounded metadata:

- hashed/stable application user identifier;
- canonical SessionID;
- provider/model/profile;
- event type and byte size;
- latency and status;
- redacted error code;
- usage totals;
- tool name and outcome class.

## 11.7 Safety identifier

OpenAI recommends sending a stable, privacy-preserving safety identifier from the trusted backend. For client-secret flows, bind it when minting the secret; for unified calls and server WebSockets, set it in the backend request. [OAI-WEBRTC] [OAI-WEBSOCKET]



# 12. Reliability, interruption, and long-session behavior {#reliability}

## 12.1 Bounded queues and backpressure

Every live queue must have a bound and an overflow policy:

| Queue | Overflow policy |
|---|---|
| reliable commands | block with context/deadline, then fail session if correctness cannot be preserved |
| provider read events | process continuously; fail on sustained inability to reduce |
| canonical EventSink | best-effort/drop according to existing sink policy, with drop metric |
| persistence writes | bounded per-session ordered queue; fail/degrade based on durability contract |
| browser proxy input audio | stop/pause capture or terminate; do not grow unbounded |
| browser proxy output audio | cap latency buffer; cancel/truncate rather than play stale speech |

Do not solve backpressure by allowing unbounded channels.

## 12.2 Interruption behavior

### WebRTC

The service manages output buffering and automatically truncates unplayed audio when VAD detects an interruption. Geppetto still records a canonical interrupt/cancel event and persists the resulting truncated content. [OAI-CONVERSATIONS]

### WebSocket proxy

The application owns playback. On speech start:

1. stop output immediately;
2. cancel queued samples;
3. calculate played milliseconds from sample count;
4. identify the current provider item/content index;
5. send `conversation.item.truncate`;
6. wait for item/response state to stabilize;
7. persist only the heard portion.

This behavior requires deterministic integration tests because a small bookkeeping error corrupts future conversation state.

## 12.3 Session rollover

Current Realtime sessions have a 60-minute maximum. [OAI-CONVERSATIONS]

Set an application maximum below that limit, for example 55 minutes, and start graceful rollover with a lead time. A rollover procedure can:

1. prevent new long-running tool work;
2. wait for or cancel the active response;
3. persist final stable items;
4. create a structured summary/current-state block;
5. open a successor provider call;
6. seed authoritative context and tool state;
7. atomically switch the browser or instruct reconnect;
8. link predecessor/successor provider IDs under the Geppetto session.

Do not replay partial audio. Replay only stable transcript/tool context or a structured summary.

## 12.4 Reconnect semantics

A dropped WebRTC connection normally results in a new provider session rather than transparent restoration of the exact media stream. Define reconnect as:

- a new provider call;
- same or successor Geppetto SessionID according to product policy;
- restored stable conversation summary/items;
- no restoration of partial response/audio buffers;
- idempotency protection for tools that may have completed near disconnection.

## 12.5 Sideband attach race

For ephemeral bootstrap, the browser can establish the call before Geppetto attaches. Mitigations in order of preference:

1. use unified bootstrap and attach before returning answer;
2. keep the microphone track disabled until backend ready;
3. start with no privileged tools and add them only after sideband ready;
4. treat early client events as untrusted and close if policy was not installed.

## 12.6 Event ordering

- index by provider item/response IDs;
- accept transcript completion out of order across different items;
- require monotonically applied content indices per item where the protocol guarantees them;
- deduplicate event IDs when present;
- preserve receive order in debug traces without assuming it equals semantic order;
- make reducer operations idempotent where possible.

## 12.7 Tool idempotency

Provider retries, reconnect races, or local retries can repeat a function-call signal. Use the provider `call_id` plus Geppetto SessionID as an idempotency key. Store terminal tool outcome long enough to safely return the same output rather than executing a state-changing tool twice.

## 12.8 VAD tuning

Start with `server_vad` for predictable behavior. Evaluate `semantic_vad` for conversational use cases. Provide push-to-talk/manual mode as a fallback for noisy environments, domain-specific pauses, and accessibility needs.

Measure:

- false starts;
- clipped initial phonemes;
- premature turn endings;
- user-to-first-audio latency;
- interruption success;
- performance with headsets, laptop microphones, conference rooms, accents, and background audio.



# 13. Observability, capacity, and cost {#observability-cost}

## 13.1 Metrics

### Bootstrap and connection

- `live_bootstrap_requests_total{mode,status}`
- `live_bootstrap_duration_seconds{mode}`
- `live_webrtc_connected_total`
- `live_sideband_attach_duration_seconds`
- `live_sideband_failures_total{reason}`
- `live_active_sessions{provider,profile,transport}`

### Conversation quality

- end-of-user-turn to first output audio;
- speech-start and speech-stop detection latency;
- response duration;
- interruption count and truncation latency;
- reconnect and rollover counts;
- transcript finalization latency;
- browser playback buffer depth for proxy mode.

### Tools

- tool call count by name/outcome;
- queue delay;
- execution latency;
- timeout/cancellation;
- duplicate call detection;
- confirmation denial.

### Capacity

- sideband WebSocket count;
- read/write event rates;
- event and command queue depth;
- dropped best-effort events;
- proxy audio bytes/s and Base64 CPU if enabled;
- goroutine count and memory per session.

## 13.2 Tracing

Create one trace per live session with spans for:

- bootstrap;
- OpenAI call creation;
- sideband attach;
- each provider Response;
- each tool call;
- persistence barrier;
- rollover/reconnect;
- close/failure.

Do not create a span for every 20 ms audio frame. Aggregate media statistics.

## 13.3 Browser telemetry

Collect bounded WebRTC statistics at a low cadence, such as every 5-10 seconds, and summarize:

- connection/ICE state;
- round-trip time where available;
- inbound/outbound packet loss and jitter;
- audio level availability;
- concealed samples or jitter-buffer delay where available;
- device type category without storing raw device labels unless necessary.

Respect privacy and avoid high-cardinality labels.

## 13.4 Cost model

OpenAI documents two billing patterns:

- conversational Realtime responses accrue text/audio/image tokens, with later responses including growing conversation context;
- streaming transcription/translation sessions are billed by audio duration. [OAI-COSTS]

Practical controls:

- maximum session age;
- per-user concurrent-session quota;
- profile-specific model and reasoning effort;
- silence filtering/VAD;
- response length constraints;
- periodic context compaction or structured summary;
- early close when the page is hidden/disconnected;
- usage accounting from response usage/rate-limit events;
- budget alerts and kill switches.

Do not embed current prices in code. Fetch or configure them outside the protocol implementation because prices and model names change.

## 13.5 Context growth

Each conversational response sees the conversation state, so later turns can cost more. [OAI-COSTS] Current model guidance also emphasizes structured state for long sessions. [OAI-REALTIME-MODELS]

Geppetto should maintain:

- current task;
- authoritative current state;
- compact tool results;
- verified user/account facts;
- a summary of older dialogue;
- explicit stale/ superseded markers.

Avoid repeatedly injecting entire raw transcripts or verbose tool payloads.



# 14. Testing strategy {#testing}

## 14.1 Protocol fixture tests

Store redacted JSONL event streams in `openai_realtime/testdata`:

- simple audio turn;
- text-only response;
- function call and result;
- argument deltas;
- user interruption;
- response cancellation;
- out-of-order transcript completions;
- rate-limit update;
- provider error linked to client `event_id`;
- sideband attach and session update;
- session close/timeout.

Replay each stream through the pure reducer and assert:

- final state;
- canonical event sequence;
- reliable effects;
- persistence barriers;
- no duplicate tools.

## 14.2 Fake transport tests

Implement a scripted transport:

```go
type FakeTransport struct {
    Incoming chan ServerEvent
    Sent     []ClientEvent
    FailRead error
    FailSend error
}
```

Use it for lifecycle, cancellation, bounded queue, close idempotency, and tool dispatch tests without network access.

## 14.3 Property/state tests

Generate event permutations that preserve required per-item constraints and verify:

- no panic;
- terminal states remain terminal;
- duplicate final events are idempotent;
- output transcript never resurrects truncated text;
- one tool `call_id` executes at most once;
- canonical IDs remain stable.

## 14.4 Persistence tests

- no persistence on raw deltas;
- final user transcript persists once;
- interrupted assistant output stores only the heard/truncated portion;
- tool call and output persist atomically or with recoverable status;
- reconnect rehydrates only stable state;
- media references are immutable and deep-copy safe.

## 14.5 HTTP/bootstrap tests

- unauthenticated and CSRF failures;
- Origin/CORS checks;
- SDP body limits;
- upstream non-2xx mapping;
- missing `Location`/call ID;
- duplicate bootstrap idempotency;
- client-secret TTL validation;
- per-user quota;
- sideband-required readiness timeout;
- no secrets in response/log snapshots.

Use an HTTP recorder or fake upstream, not live OpenAI, for the majority of tests.

## 14.6 Browser tests

Use Playwright with fake media devices where possible:

- permission accepted/denied;
- user-gesture connection;
- microphone mute/unmute;
- remote track attachment;
- data-channel event parsing;
- close cleanup;
- sideband-ready gating;
- network disconnect UI;
- device change;
- captions under high delta rate.

A gated live integration suite should use a spend cap and explicit environment flag.

## 14.7 Audio proxy tests

For optional backend media proxy:

- deterministic resampling vectors;
- PCM16 saturation/endian tests;
- sequence loss/reordering behavior;
- playback ring-buffer underflow/overflow;
- exact sample-to-millisecond truncation;
- `WebSocket.bufferedAmount` thresholds;
- Base64 round trip;
- long-run memory/CPU soak;
- interruption under jitter.

## 14.8 Compatibility tests

The new packages should not change:

- existing `engine.Engine` behavior;
- existing Session append/next behavior;
- current tool-loop tests;
- current EventSink contracts;
- Chat/Responses provider selection.



# 15. Incremental rollout plan {#rollout}

## Phase 0: establish a clean baseline

- restore or identify the missing `pkg/inference/toolloop/enginebuilder` package in the full development checkout;
- run existing unit/integration tests with the requested Go toolchain;
- record public API compatibility expectations;
- add feature flags for live functionality.

## Phase 1: provider-neutral live core

Deliver:

- `pkg/inference/live` lifecycle interfaces;
- typed command queue and state machine;
- fake transport;
- canonical live event definitions;
- reducer/effect test harness;
- no browser or live OpenAI dependency.

Exit criteria:

- lifecycle and concurrency tests pass under race detection;
- bounded queues and close semantics are documented;
- existing code is unaffected.

## Phase 2: server WebSocket adapter and protocol validation

Implement the OpenAI server WebSocket transport first as an engineering test harness, even though it is not the default browser topology. It gives Geppetto complete access to protocol events and simplifies fixture capture, tool integration, and reducer validation.

Deliver:

- exact event types;
- server WebSocket connection;
- audio append/output handling for test files or a CLI harness;
- tool dispatcher;
- interruption/truncate tests;
- usage/rate-limit metrics.

This phase validates protocol semantics before adding browser signaling.

## Phase 3: unified WebRTC bootstrap and browser demo

Deliver:

- authenticated `/api/live/openai/webrtc` endpoint;
- browser `RTCPeerConnection` client;
- remote audio playback and microphone controls;
- sideband attachment before ready;
- final transcript captions;
- close/status endpoints;
- no recording;
- one configuration profile.

## Phase 4: production sideband control

Deliver:

- privileged tool execution;
- per-tool authorization/confirmation;
- canonical event mapping;
- stable persistence barriers;
- sideband loss policy;
- observability dashboards;
- quotas and audit events.

## Phase 5: chained voice

Deliver:

- true Realtime transcription adapter using `gpt-live-transcribe` or configured equivalent;
- integration with existing Geppetto Session/Engine/tool loop;
- streaming speech generation;
- barge-in/cancel policy;
- explicit transcript/policy checkpoints.

This replaces the current file-chunk “streaming” transcription path for live microphone use rather than modifying it in place.

## Phase 6: hardening and optional media gateway

- 55-minute rollover;
- reconnect/summary rehydration;
- load/soak testing;
- browser network/device matrix;
- cost controls;
- recording/compliance design if required;
- backend media proxy only after a concrete requirement and capacity model.

## Recommended first production scope

Keep the first release deliberately narrow:

```text
transport:          direct browser WebRTC
bootstrap:          unified SDP
sideband:           required when tools are enabled
turn detection:     server_vad
recording:          disabled
persistence:        final transcripts + tool barriers only
models/voice:       one versioned configuration profile
session length:     capped below provider maximum
fallback:           text UI and explicit reconnect
```



# 16. Decision record and implementation checklist {#decision-record}

## 16.1 Architecture decision record

### ADR-1: Realtime is not an Engine

**Status:** recommended  
**Decision:** introduce `pkg/inference/live` and `LiveSessionFactory`.  
**Reason:** lifecycle and concurrency differ fundamentally from one finite inference.  
**Consequence:** some shared utilities move below engine/live boundaries; callers choose finite or live explicitly.

### ADR-2: WebRTC is the default browser media transport

**Status:** recommended  
**Decision:** browser audio flows directly to OpenAI.  
**Reason:** official recommendation, lower media implementation burden, better interruption/output buffering, lower backend load.  
**Consequence:** raw audio is not available to Geppetto unless a separate recording path is added.

### ADR-3: Unified SDP bootstrap is the default tool-enabled bootstrap

**Status:** recommended  
**Decision:** browser posts offer SDP to Geppetto; Geppetto creates the call and attaches sideband before returning ready.  
**Reason:** simpler correlation and no sideband attach race.  
**Consequence:** backend is in the setup critical path, though not the media path.

### ADR-4: Sideband owns privileged business logic

**Status:** recommended  
**Decision:** tools, policy, and durable state stay on Geppetto.  
**Reason:** client code and credentials are untrusted; OpenAI explicitly provides sideband for server control.  
**Consequence:** sideband availability becomes a production dependency for tool-enabled sessions.

### ADR-5: EventSink is observational, not a control bus

**Status:** recommended  
**Decision:** reliable effects use internal queues; canonical events remain best-effort.  
**Reason:** existing sink behavior ignores sink failures and warns against durable state from partial events.  
**Consequence:** live code has explicit command/effect plumbing.

### ADR-6: Persist semantic barriers, not audio deltas

**Status:** recommended  
**Decision:** store final transcripts, completed/truncated items, and tool barriers.  
**Reason:** deltas are high-volume, reorderable, interruption-sensitive, and potentially sensitive.  
**Consequence:** exact audio replay requires a separate opt-in recording subsystem.

### ADR-7: Support native and chained modes

**Status:** recommended  
**Decision:** share product vocabulary but keep internal pipelines separate.  
**Reason:** natural conversation and deterministic workflows are both valid requirements.  
**Consequence:** capability profiles must state which mode, transport, and persistence semantics apply.

## 16.2 Implementation checklist

### Domain and concurrency

- [ ] Define live states and terminal semantics.
- [ ] Implement one read pump and one write pump.
- [ ] Bound every queue and document overflow behavior.
- [ ] Make `Close` idempotent.
- [ ] Add race-enabled tests.

### OpenAI adapter

- [ ] Define exact client/server event structs.
- [ ] Implement client-secret REST call.
- [ ] Implement unified multipart SDP call.
- [ ] Capture and protect `call_id`.
- [ ] Implement sideband WebSocket attachment.
- [ ] Add pure reducer and JSONL fixtures.
- [ ] Map errors through client `event_id` where available.

### Tools

- [ ] Reuse registry/executor and schema definitions.
- [ ] Deduplicate by `call_id`.
- [ ] Reauthorize every tool invocation.
- [ ] Send `function_call_output` then `response.create`.
- [ ] Persist tool barriers.

### Browser

- [ ] User-gesture-gated connection.
- [ ] Microphone/device controls.
- [ ] Remote track playback.
- [ ] Data-channel event parsing.
- [ ] Sideband-ready microphone gate.
- [ ] Clean close and track stop.
- [ ] Accessibility captions and connection status.

### Security

- [ ] Permanent key only on backend.
- [ ] Client-secret TTL 30-60 seconds by default.
- [ ] Auth/CSRF/Origin/CORS checks.
- [ ] Concurrency/spend quotas.
- [ ] Redaction of secrets, SDP, audio, and transcripts.
- [ ] Explicit recording consent and retention if added.

### Persistence and events

- [ ] Add live canonical event types.
- [ ] Keep raw audio off EventSink.
- [ ] Implement provider ConversationMirror.
- [ ] Persist final/transformed state after interruption.
- [ ] Mark transcript source and authority.

### Operations

- [ ] Bootstrap/sideband/response/tool metrics.
- [ ] Browser WebRTC aggregate stats.
- [ ] Session rollover below 60 minutes.
- [ ] Reconnect/rehydration policy.
- [ ] Cost and active-session limits.
- [ ] Kill switch and feature flags.



# 17. Appendices and references {#appendices}

## Appendix A: OpenAI event mapping starter table

| Provider event | Canonical handling | Durable? |
|---|---|---:|
| `session.created` | `live-session-started` after local readiness rules | session record |
| `session.updated` | `live-session-updated` | selected config snapshot |
| `input_audio_buffer.speech_started` | `audio-input-started`; interrupt UI | no |
| `input_audio_buffer.speech_stopped` | `audio-input-stopped` | no |
| `input_audio_buffer.committed` | `audio-input-committed` | pending barrier |
| `conversation.item.input_audio_transcription.delta` | `input-transcript-delta` | no |
| `conversation.item.input_audio_transcription.completed` | `input-transcript-finished` | yes |
| `response.created` | `response-started` | no |
| `response.output_audio.delta` | media plane only for WebSocket | no |
| `response.output_audio_transcript.delta` | `output-transcript-delta` | no |
| `response.output_audio_transcript.done` | `output-transcript-finished` | candidate barrier |
| `response.function_call_arguments.delta` | internal assembler; optional debug event | no |
| `response.function_call_arguments.done` | reliable tool-dispatch effect | tool barrier |
| `conversation.item.done` | item-finished; update mirror | yes when stable |
| `response.cancelled` | response-cancelled/interrupted | persist truncation result |
| `response.done` | response-finished + usage | yes |
| `rate_limits.updated` | rate-limits-updated metric/event | aggregate only |
| `error` | canonical error; correlate by `event_id` | terminal or audit depending severity |

The adapter must tolerate additional provider events and preserve unknown event type/ID in a bounded debug record without failing the entire session unless protocol correctness requires it.

## Appendix B: Example configuration profile

```yaml
api:
  type: openai-realtime

realtime:
  profile: support-default-v1
  model: ${OPENAI_REALTIME_MODEL}
  voice: marin
  transport: webrtc_direct
  bootstrap_mode: unified_sdp
  sideband_required: true
  output_modalities: [audio]

  turn_detection:
    type: server_vad
    create_response: true
    interrupt_response: true
    prefix_padding_ms: 300
    silence_duration_ms: 500

  input_transcription:
    enabled: true
    model: gpt-live-transcribe
    language: en

  noise_reduction:
    type: near_field

  client_secret_ttl: 45s
  max_session_age: 55m
  rollover_lead: 2m
  persist:
    final_input_transcripts: true
    final_output_transcripts: true
    tool_barriers: true
    raw_audio: false
```

Exact model/voice values must be validated against the active account and current API documentation.

## Appendix C: Repository evidence map

| Finding | Repository evidence |
|---|---|
| finite engine contract | `pkg/inference/engine/engine.go:9-15` |
| optional finite result wrapper | `pkg/inference/engine/run_with_result.go:26-103` |
| blocking session runner builder | `pkg/inference/session/builder.go:9-20` |
| one-inference execution handle | `pkg/inference/session/execution.go:13-84` |
| stable session ID and append-only snapshots | `pkg/inference/session/session.go:21-35` |
| clone latest Turn for next prompt | `pkg/inference/session/session.go:53-103` |
| asynchronous finite StartInference | `pkg/inference/session/session.go:189-281` |
| EventSink use and durability warning | `pkg/events/sink.go:3-18` |
| best-effort context fanout | `pkg/events/context.go:15-48` |
| canonical correlation IDs | `pkg/events/correlation.go:3-20` |
| current event vocabulary | `pkg/events/chat-events.go:13-96` |
| current Turn/block kinds omit audio | `pkg/turns/block_kind_gen.go:13-21` |
| shallow nested clone concern | `pkg/turns/types.go:28-62` |
| finite tool-loop orchestration | `pkg/inference/toolloop/loop.go:92-174` |
| reusable registry/executor | `pkg/inference/tools/registry.go:8-18`; `executor.go:7-11` |
| factory supports finite APIs only | `pkg/inference/engine/factory/factory.go:105-197` |
| Chat Stream is response streaming | `pkg/steps/ai/settings/settings-chat.go:22-61` |
| file-chunk transcription implementation | `pkg/steps/ai/openai/transcribe.go:300-459` |
| session-centered JS design note | `ttmp/2026/06/02/.../01-session-centered-javascript-api-design-and-implementation-guide.md` |
| JS streaming event design note | `ttmp/2026/06/01/.../01-geppetto-js-streaming-events-design-and-implementation-guide.md` |

## Appendix D: Key failure modes and controls

| Failure mode | Control |
|---|---|
| permanent key exposed in browser | server-only standard key; ephemeral/unified bootstrap |
| token reused to create extra calls | very short TTL, issuance quotas, application binding, monitoring |
| client overrides session config | tools authorize independently; sideband monitors; proxy for strict isolation |
| tool executes twice | `call_id` idempotency store |
| sideband attaches too late | unified bootstrap or microphone gate |
| output stored beyond interruption | post-truncation persistence barrier |
| WebSocket playback drifts | sample-count ring buffer and deterministic truncate tests |
| event subscriber blocks media | media plane separate; best-effort EventSink |
| unbounded memory | bounded command/event/audio queues |
| 60-minute provider termination | graceful rollover before maximum |
| full transcript/audio leaks to logs | redaction, payload caps, data-classification defaults |
| reconnect replays partial state | restore stable summaries/items only |
| model instructions treated as permissions | backend authorization for every action |

## References

All OpenAI references were reviewed on 2026-08-11.

- **OAI-WEBRTC** - OpenAI, [*Realtime API with WebRTC*][OAI-WEBRTC].
- **OAI-WEBSOCKET** - OpenAI, [*Realtime API with WebSocket*][OAI-WEBSOCKET].
- **OAI-CONVERSATIONS** - OpenAI, [*Realtime conversations*][OAI-CONVERSATIONS].
- **OAI-SIDEBAND** - OpenAI, [*Webhooks and server-side controls*][OAI-SIDEBAND].
- **OAI-CLIENT-SECRETS** - OpenAI API Reference, [*Create Realtime client secret*][OAI-CLIENT-SECRETS].
- **OAI-VAD** - OpenAI, [*Voice activity detection (VAD)*][OAI-VAD].
- **OAI-TRANSCRIPTION** - OpenAI, [*Realtime transcription*][OAI-TRANSCRIPTION].
- **OAI-VOICE-AGENTS** - OpenAI, [*Voice agents*][OAI-VOICE-AGENTS].
- **OAI-COSTS** - OpenAI, [*Managing costs*][OAI-COSTS].
- **OAI-REALTIME-MODELS** - OpenAI, [*Using realtime models*][OAI-REALTIME-MODELS].
- **OAI-GO-SDK** - OpenAI, [*Official Go SDK*][OAI-GO-SDK].

[OAI-WEBRTC]: https://developers.openai.com/api/docs/guides/realtime-webrtc
[OAI-WEBSOCKET]: https://developers.openai.com/api/docs/guides/realtime-websocket
[OAI-CONVERSATIONS]: https://developers.openai.com/api/docs/guides/realtime-conversations
[OAI-SIDEBAND]: https://developers.openai.com/api/docs/guides/realtime-server-controls
[OAI-CLIENT-SECRETS]: https://developers.openai.com/api/reference/resources/realtime/subresources/client_secrets/methods/create
[OAI-VAD]: https://developers.openai.com/api/docs/guides/realtime-vad
[OAI-TRANSCRIPTION]: https://developers.openai.com/api/docs/guides/realtime-transcription
[OAI-VOICE-AGENTS]: https://developers.openai.com/api/docs/guides/voice-agents
[OAI-COSTS]: https://developers.openai.com/api/docs/guides/realtime-costs
[OAI-REALTIME-MODELS]: https://developers.openai.com/api/docs/guides/realtime-models-prompting
[OAI-GO-SDK]: https://github.com/openai/openai-go
