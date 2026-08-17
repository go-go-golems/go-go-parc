---
title: "PROJECT REPORT - CoinVault Chat Image Attachments - Live Verification Across Provider Protocols"
aliases:
  - CoinVault image attachments live test
  - multimodal chat end-to-end verification
  - COINVAULT-046 verification
status: active
type: article
created: 2026-08-17
repo: /home/manuel/workspaces/2026-08-12/deploy-dev-indexer/coinvault
design_ticket: /home/manuel/workspaces/2026-08-12/deploy-dev-indexer/coinvault/ttmp/2026/08/17/COINVAULT-046--add-image-upload-support-to-the-chat
companion_report: "[[PROJECT REPORT - CoinVault Chat Image Attachments - A Cross-Repository Deep Dive]]"
pull_requests:
  - https://github.com/go-go-golems/geppetto/pull/414
  - https://github.com/go-go-golems/pinocchio/pull/199
  - https://github.com/goldeneagle/coinvault/pull/7
tags:
  - article
  - project-report
  - coinvault
  - testing
  - verification
  - multimodal
  - openai-responses
  - chat-completions
  - playwright
  - geppetto
  - pinocchio
---

# CoinVault Chat Image Attachments: Live Verification Across Provider Protocols

Unit tests can prove that a request builder places an `input_image` part into a JSON body. They cannot prove that a vision model on the other end of the network decodes that part and reasons about the pixels, that the image is still present on the second turn of a conversation, or that a browser that reloads the page sees the same picture the user attached. Those three properties — provider consumption, history fidelity, and hydration — are the ones a chat application actually depends on, and they can only be established by running the real binary against real models through the real interface. This report describes how that was done for the CoinVault image-attachment feature on the afternoon of 2026-08-17, what evidence each step produced, and which parts of the harness are reusable for the next multimodal feature. The design and implementation of the feature itself are documented in the companion report, [[PROJECT REPORT - CoinVault Chat Image Attachments - A Cross-Repository Deep Dive]]; this note assumes that architecture and concentrates on verifying it.

> [!summary]
> - A real test needed four things the unit suite does not: provider credentials, a profile registry in which vision-capable profiles *declare* the capability, an application database so the production `analyst` profile could load its tools, and the built frontend served by the Go binary. All four were available locally without new secrets; the only new artefact was a scratch copy of the profile registry with `coinvault.capabilities@v1: {vision: true}` added.
> - Two provider protocols were exercised through the same UI: OpenAI chat completions (`glm-5.2-vision` via LunaRoute) and OpenAI Responses (`gpt-5-nano`). Both read a rendered coin image correctly (`LIBERTY / 1 OZ FINE GOLD / 50 DOLLARS / 2026`), which is verifiable text rather than a subjective description.
> - History fidelity was proven by a second turn that asked about the image without re-attaching it: the answer was correct, and the server log showed the image-resolver middleware running once per turn. Hydration was proven by reloading the page and observing the thumbnail served from the authenticated attachment endpoint. The persisted turn store held two user blocks and zero image bytes.
> - The harness surfaced two environment traps worth remembering: a stale backend already bound to the default devctl port made the new profiles API look broken, and Playwright's file chooser only accepts paths under the workspace root.

## 1. What "for real" has to mean here

The feature moves an image through five representations: an HTTP upload, a sessionstream command, an echoed user-message event and its timeline entity, a geppetto user block that holds only a reference, and a provider request into which a middleware substitutes the bytes immediately before the call. The unit and HTTP-level tests written during implementation cover each boundary in isolation with fakes on the far side: a recording engine stands in for the model, an in-memory hub stands in for the websocket, and a `httptest` mux stands in for the browser. Earlier the same day a `curl`-driven smoke test on the real binary had taken the path as far as the provider's authentication and stopped at a 401 from a dummy key.

What remained unproven were properties that require the far side to be real:

1. **Provider consumption.** The adapters produce a data URL (chat completions) or an `input_image` part (Responses). Only a vision model can confirm that the encoding is one it accepts and that the image content, not merely its presence, reaches the model.
2. **History fidelity across turns.** The engine reloads conversation history from YAML on every message. The accessor fix in geppetto (`turns.BlockImages`) exists precisely because the previous code lost images at this boundary. The test must therefore include a second turn that depends on the first turn's image.
3. **Hydration.** The browser renders live user messages from a websocket event and reloaded conversations from a snapshot. Both go through one mapping function, but a reload is the only way to observe the snapshot path with real data.
4. **The storage invariant.** No image bytes may appear in the persisted turn store; only the internal reference `coinvault-attachment://<sid>/<id>`.
5. **The vision gate and the UI coupling to it.** The attach button must be enabled only when the selected profile declares vision, and the server must reject image submissions for profiles that do not.

Each of these was checked explicitly and is reported below.

## 2. The harness

### 2.1 Credentials and the capability declaration

The local devctl configuration points the backend at `~/.config/pinocchio/profiles.yaml`, a registry that already contains working credentials for LunaRoute (`glm-5.2-vision*`), OpenAI Responses (`gpt-5-nano`, `gpt-5-mini`, `gpt-5.6-luna*`), Anthropic (`sonnet`, `haiku`) and Gemini (`gemini-2.5-flash` and others). No new secrets were required.

That registry does not declare vision capability on any profile, and the server's vision gate treats an undeclared profile as text-only. Rather than edit the user's global file, a scratch copy was written with the extension added to eight vision-capable profiles:

```python
d = yaml.safe_load(open('~/.config/pinocchio/profiles.yaml'))
for slug in ['glm-5.2-vision', 'glm-5.2-vision-fast', 'gpt-5.6-luna', 'gpt-5.6-luna-low',
             'gpt-5-nano', 'gpt-5-mini', 'sonnet', 'gemini-2.5-flash']:
    d['profiles'][slug].setdefault('extensions', {})['coinvault.capabilities@v1'] = {'vision': True}
yaml.safe_dump(d, open('<scratch>/profiles-vision.yaml', 'w'), sort_keys=False)
```

The extension key follows geppetto's `namespace.feature@vN` convention; a bare `capabilities:` key is rejected by the registry loader at startup, which is how the convention was discovered during implementation.

### 2.2 The database

The production `analyst` application profile requires the `sql_doc` and `sql_query` tools, and the tool catalog is built from a live database handle; without one the server refuses to start with `application profile "analyst" requires unavailable tools`. The repository's `docker-compose.yml` provides a MySQL 8.4 service with the development credentials, so `docker compose up -d mysql` was sufficient. The volume was empty, which is fine for an image test — the model was told not to query — and produces one unrelated symptom: `/api/stats/metals` returns 500 because the tables do not exist. That is the only console error the browser reported.

### 2.3 The server and the UI

The binary was built from the working tree and started directly rather than through devctl, so that the registry, profile, and storage locations could be controlled:

```bash
coinvault --log-level debug serve \
  --serve-host 127.0.0.1 --serve-port 18944 \
  --host 127.0.0.1 --port 3306 --database gec_dev --user gec --password gec_dev_password \
  --timeline-db <scratch>/real/timeline.db --turns-db <scratch>/real/turns.db \
  --attachments-dir <scratch>/real/attachments \
  --profile-registries <scratch>/profiles-vision.yaml \
  --profile glm-5.2-vision --application-profile analyst
```

Without the `embed` build tag the Go server serves the frontend from `web/dist` on disk, which had been produced by `pnpm build` during implementation. The browser therefore exercised the same bundle that would ship in the container image, not the Vite dev server.

Port 18944 was chosen after the first attempt on the devctl default, 18933, failed with `bind: address already in use`: a backend from an earlier devctl session was still running there. Because `curl` was pointed at the port rather than at a process, the profiles API it returned came from that old binary, and `supports_images` was absent from the response — an alarming but false signal. The lesson generalises: when a test asserts on a new field, first confirm which process owns the port (`ss -ltnp | grep 18933`). The stale process was terminated with the user's permission.

### 2.4 The browser driver

Playwright, through its MCP server, drove the actual React UI: navigate, click the attach button, satisfy the file chooser, type into the textarea, submit with Enter, wait, take an accessibility snapshot, switch the model `<select>`, reload. The accessibility snapshot rather than a screenshot was the primary observation channel because it exposes the rendered text verbatim (the assistant's answer, the tray's `640×640 · 20 KB` label, the `Open image gold-coin.png` button that wraps the thumbnail). One constraint: the file chooser accepts only paths under the workspace root, so the test image was copied into `.playwright-mcp/`.

### 2.5 The test image

A description of an arbitrary photograph cannot be checked mechanically. The test image was instead rendered with Pillow: a 640×640 PNG (20,535 bytes) showing a gold disc with a double ring and four lines of dark text — `LIBERTY`, `1 OZ FINE GOLD`, `50 DOLLARS`, `2026`. The correct answer to "read out the text" is then a fixed string, and the correct answer to "what year and denomination" on a later turn is `2026` and `50 dollars`. Any answer that omits or misreads a line is a failure; any answer that reproduces them could only have come from the pixels.

## 3. Evidence, protocol by protocol

### 3.1 OpenAI chat completions via LunaRoute (`glm-5.2-vision`)

With the GLM profile selected the attach button was enabled and the hint line read "Paste or drop images". Choosing the file created the session lazily (the URL gained `?conv_id=…` before any message was sent), uploaded, and the tray showed `gold-coin.png · 640×640 · 20 KB` — dimensions and size that come from the server's response, so this line alone proves the upload, sniff, and decode succeeded. The prompt was:

> Describe exactly what you see in the attached image. Read out any text on it. Do not run any database queries for this.

The server log for the run, in order:

```
built tool registry … registered_tools=["sql_doc","sql_query"]
attachments: resolved image references for provider request block_id=46c8ffba… images=1
Making request to openai from turn blocks … model=glm-5.2-vision
OpenAI request message … idx=0 role=system  content_preview="You are CoinVault Analyst…"
OpenAI request message … idx=1 role=user    content_preview="Describe exactly what you see…"
Adding tools to OpenAI request … tool_count=2
OpenAI metadata finalized … input_tokens=8417 output_tokens=174 stop_reason=stop
OpenAI streaming complete … final_text_length=460 tool_call_count=0
```

The middleware line confirms the reference was resolved into bytes for this call; the adapter then emitted the user message as `MultiContent` (text part plus an `image_url` data URL — the log's `content_preview` shows only the text part, which is expected). The model's answer, as rendered in the transcript:

> This image shows a round, gold-colored medallion or coin design on a light cream background. The medallion has a double-ring border in a darker brownish-gold tone. Inside the central area, the text reads as follows: At the top: **LIBERTY**. Below that: **1 OZ FINE GOLD** and **50 DOLLARS**. At the bottom: **2026**. The text is in a dark brown color…

The reasoning row (GLM streams reasoning, rendered collapsed as "Thought for 2.3s") said "I can see a circular gold medal or coin design". All four text lines were read correctly, and the model made no tool calls despite having two available.

### 3.2 History fidelity: the second turn

The second message deliberately attached nothing:

> Without me re-attaching anything: what year is printed on the coin I showed you, and what denomination? Answer in one line.

Answer: "The coin bears the year 2026 and a denomination of 50 dollars." The log shows the same block id being resolved again — `attachments: resolved image references … block_id=46c8ffba… images=1` — followed by a four-message request (system, user with image, assistant, user), and `input_tokens=8565` against 8417 for the first turn: the image is present in the reloaded history and re-sent, as designed. Before the geppetto accessor fix this second request would have carried the first user message without its image, and the model would have had to answer from its own earlier text; the reasoning trace ("Based on the detailed description of the image I just provided…") shows that a model can sometimes get away with that, which is exactly why the log line and the token count, not the answer alone, are the evidence that the image was there.

### 3.3 OpenAI Responses (`gpt-5-nano`)

Selecting a different model starts a new conversation by design (`handleInferenceProfileChange` calls `handleNewConversation`), so the image was attached again and the prompt was:

> Read out all the text printed on the attached image, top to bottom, and name the metal colour. No database queries.

The Responses adapter logs a structured summary of the input it built, which is the most direct evidence available that the wire shape is correct:

```
attachments: resolved image references for provider request block_id=8b58f409… images=1
Responses: request input summary … input_items=2 input_preview=[
  {"role":"system","parts":[{"type":"input_text","len":17953,…}]},
  {"role":"user","parts":[{"type":"input_text","len":115,…},{"type":"input_image","len":0,"text":""}]}]
Responses: built request … include_len=1 input_items=2 model=gpt-5-nano
Responses: sending request … body_len=61988 url=https://api.openai.com/v1/responses
Responses: HTTP response received … content_type="text/event-stream; charset=utf-8" status=200
```

The user item has two parts, `input_text` and `input_image`; the body is 61,988 bytes for a 20,535-byte PNG, consistent with base64 expansion (≈1.37×) plus the 18 KB system prompt. The answer:

> Text (top to bottom): LIBERTY · 1 OZ FINE GOLD · 50 DOLLARS · 2026. Metal colour: Gold

Both protocols therefore consumed the same stored bytes through the same middleware; the difference is entirely inside the adapters, which is where it belongs.

### 3.4 Hydration

Navigating to the conversation URL again — a full page load, so the local Redux state was empty and everything came from the sessionstream snapshot — produced a user bubble containing an `<img>` whose `src` was `/api/chat/sessions/b78c7115…/attachments/att_yyzqt4zcajkfqkuy3gxnmqzqme`, with `naturalWidth` 640, `naturalHeight` 640, and `complete === true`, followed by the assistant's answer text. The image was fetched from the authenticated attachment endpoint, not from any inline data, which is what the reference-only design promises.

### 3.5 The storage invariant

```
$ sqlite3 <scratch>/real/turns.db "select count(*), sum(instr(payload_json,'content')>0) from blocks where kind='user'"
2|0
```

Two user blocks from the first conversation (both turns), neither containing a `content` key. Their `images` payload holds `{"attachment_id","media_type","url":"coinvault-attachment://…"}`. The middleware's restore step — replacing the resolved byte maps with the original reference maps on both the input and returned turn after the provider call — held under real toolloop snapshot hooks and the real persister, not just under the unit test's fake `next`.

### 3.6 The vision gate

Two observations covered it. On the UI side, the attach button's enabled state followed the selected profile's `supports_images`, which the scratch registry made true for GLM and gpt-5-nano. On the server side, the earlier `curl` smoke run had already shown `POST …/messages` with attachments against the `default` profile returning `400 selected model profile does not accept images: coinvault/default`; the same code path is exercised by the profiles API response the UI reads.

## 4. What the harness is worth keeping

The pieces that will be reused the next time a multimodal or provider-specific behaviour needs a real check:

- **A registry overlay, not a registry edit.** Copying `~/.config/pinocchio/profiles.yaml` to scratch and adding extensions keeps credentials in one place and lets the test declare capabilities without touching the user's configuration.
- **A binary started by hand on a non-default port** with explicit `--timeline-db`, `--turns-db`, and `--attachments-dir` in scratch, so state can be inspected with `sqlite3` and discarded afterwards.
- **A rendered test image with printed text**, so model answers are checkable strings.
- **The debug log as the oracle for protocol shape.** Both adapters already log enough (`resolved image references`, `Responses: request input summary`, token counts) to distinguish "the model saw the image" from "the model remembered its own description".
- **Playwright accessibility snapshots** for asserting on rendered text and image elements; `page.evaluate` for `naturalWidth`/`complete` on hydrated images.

Two things not to forget: check who owns the port before trusting an HTTP response, and put files Playwright must upload under the workspace root.

## 5. What remains

- Claude (`sonnet`) and Gemini (`gemini-2.5-flash`) adapters through the same UI. Both consume inline bytes, which the middleware supplies, so the expectation is that they work; the run is one model-selector change away in the same harness.
- A photograph rather than a rendered image, to observe the client-side downscale (`downscaleImageFile`, ≤ 2048 px) and the resulting request sizes.
- Paste and drag/drop through the browser (only the file chooser was driven).
- Merging the three pull requests in dependency order and replacing the pseudo-version pins with tagged releases.

## 6. Where the details live

- Diary Step 8 of `COINVAULT-046` records the commands, the log excerpts, and the environment traps: `/home/manuel/workspaces/2026-08-12/deploy-dev-indexer/coinvault/ttmp/2026/08/17/COINVAULT-046--add-image-upload-support-to-the-chat/reference/01-investigation-diary.md`
- The feature itself: [[PROJECT REPORT - CoinVault Chat Image Attachments - A Cross-Repository Deep Dive]]
- Pull requests: geppetto #414, pinocchio #199, coinvault #7.
