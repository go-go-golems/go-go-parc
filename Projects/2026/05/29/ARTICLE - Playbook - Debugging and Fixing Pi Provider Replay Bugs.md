---
title: "Playbook: Debugging and Fixing Pi Provider Replay Bugs"
aliases:
  - Pi Provider Replay Bugs
  - Pi Duplicate Message ID Debugging
  - Codex Responses Replay Fix
  - Pi Agent Source Fix Playbook
tags:
  - article
  - playbook
  - pi
  - debugging
  - llm-providers
  - openai-responses
  - go-minitrace
status: active
type: article
created: 2026-05-29
repo: /home/manuel/code/others/llms/pi/mariozechner/pi-mono
---

# Playbook: Debugging and Fixing Pi Provider Replay Bugs

This note records the investigation of a Pi provider failure where OpenAI Codex rejected a conversation with `Error: Duplicate item found with id msg_3. Remove duplicate items from your input and try again.` The immediate incident happened while working in `/home/manuel/workspaces/2026-05-29/chatbot-react`, but the useful knowledge belongs to Pi itself: how session transcripts are structured, how provider replay transforms historical messages into model-specific request items, and how to test a local Pi source checkout without losing the trail of evidence.

The goal is not only to remember that one bug was fixed upstream. The goal is to preserve a repeatable method for future Pi debugging work: isolate the failing transcript, inspect the provider conversion boundary, write a targeted regression test, and verify the fixed checkout before updating the global installation.

> [!summary]
> - The failure was caused by duplicate OpenAI Responses item IDs generated during replay of cross-provider assistant history.
> - `go-minitrace` is the right first tool for turning a Pi JSONL session into queryable evidence, but raw JSONL line inspection is still necessary near provider errors.
> - The correct fix lives in `@mariozechner/pi-ai`, not in the application repository that happened to trigger the failure.
> - Upstream Pi already contains the fix in `3f1ce9b6` and `d1fb34bc`; local work should rebase or reset to latest upstream before carrying a patch.

## Why this note exists

Provider replay bugs are easy to misattribute. The visible error appears during normal project work, and the project often has enough active changes to make the failure look application-specific. In this case, the user had asked the agent to continue a backend implementation and write a detailed report. The next model invocation failed before producing content. The backend work was not the cause; it merely produced a long mixed-provider Pi session that exposed a replay conversion bug.

Pi sessions preserve a complete JSONL event log under `~/.pi/agent/sessions`. That log is the source of truth. The investigation started with this transcript:

```text
/home/manuel/.pi/agent/sessions/--home-manuel-workspaces-2026-05-29-chatbot-react--/2026-05-29T12-52-32-763Z_019e73cb-217a-72b8-8267-137c6376439d.jsonl
```

The failing lines were near the end of the file. Line `867` recorded an assistant message from `openai-codex-responses` with `stopReason: "error"` and the duplicate item message. Line `870` repeated the same error and included diagnostics showing a provider transport failure before the message stream started. This placement matters: the provider rejected the input before generating new output, so the bug was in request construction rather than in downstream rendering, tool handling, or the target application.

## The replay path that failed

Pi does not send the raw JSONL transcript directly to the provider. It reconstructs a model context from prior messages, then each provider adapter converts that context into the provider's wire format. The relevant implementation lives in:

```text
/home/manuel/code/others/llms/pi/mariozechner/pi-mono/packages/ai/src/providers/openai-responses-shared.ts
/home/manuel/code/others/llms/pi/mariozechner/pi-mono/packages/ai/src/providers/transform-messages.ts
/home/manuel/code/others/llms/pi/mariozechner/pi-mono/packages/ai/src/providers/openai-codex-responses.ts
```

The failing session had switched providers. It started with `openai-codex/gpt-5.5`, switched to `zai/glm-5.1`, compacted, continued with many GLM assistant turns, and then switched back to `openai-codex/gpt-5.5`. That sequence is legal, but it stresses the replay boundary because a historical GLM assistant message is not native OpenAI Responses output. Pi must decide how to represent it when sending context to Codex.

The important transformation is this: cross-provider assistant `thinking` can become plain assistant text. A single GLM assistant turn may contain both a `thinking` block and a normal `text` block. After transformation, that one Pi assistant message can produce more than one OpenAI Responses `message` item.

The old fallback ID logic assigned IDs using the source message index:

```ts
let msgIndex = 0;
for (const msg of transformedMessages) {
  if (msg.role === "assistant") {
    for (const block of msg.content) {
      if (block.type === "text") {
        let msgId = parsedSignature?.id;
        if (!msgId) {
          msgId = `msg_${msgIndex}`;
        }
        output.push({ type: "message", id: msgId, ... });
      }
    }
  }
  msgIndex++;
}
```

This is valid only if each transformed assistant message emits at most one provider `message` item without an existing signature. The failing transcript violated that assumption. One source message could emit two text-like provider messages, both with the same fallback ID such as `msg_3`. OpenAI Responses rejects duplicate item IDs, so the request failed before streaming began.

## Evidence from the transcript

The useful transcript facts were found with a combination of `go-minitrace`, ripgrep, and small Python snippets. The first pass established size and location:

```bash
ls -lh ~/.pi/agent/sessions/--home-manuel-workspaces-2026-05-29-chatbot-react--/2026-05-29T12-52-32-763Z_019e73cb-217a-72b8-8267-137c6376439d.jsonl
wc -l ~/.pi/agent/sessions/--home-manuel-workspaces-2026-05-29-chatbot-react--/2026-05-29T12-52-32-763Z_019e73cb-217a-72b8-8267-137c6376439d.jsonl
rg -n "Duplicate item|msg_3|duplicate" ~/.pi/agent/sessions/--home-manuel-workspaces-2026-05-29-chatbot-react--/2026-05-29T12-52-32-763Z_019e73cb-217a-72b8-8267-137c6376439d.jsonl -S
```

Then the session was converted for structured inspection:

```bash
rm -rf /tmp/pi-dupe-analysis
mkdir -p /tmp/pi-dupe-analysis

go-minitrace convert pi \
  --source-session /home/manuel/.pi/agent/sessions/--home-manuel-workspaces-2026-05-29-chatbot-react--/2026-05-29T12-52-32-763Z_019e73cb-217a-72b8-8267-137c6376439d.jsonl \
  --output-dir /tmp/pi-dupe-analysis

go-minitrace query duckdb \
  --archive-glob '/tmp/pi-dupe-analysis/active/*/*.minitrace.json' \
  --preset session-list \
  --output json
```

The converted session reported `417` turns and `426` tool calls. That confirmed this was a long replay context, not a small fresh conversation.

Raw JSONL inspection around the failure showed the model switch and the error:

```text
line 864: model_change -> provider openai-codex, model gpt-5.5
line 866: user message asks for backend assessment/report
line 867: assistant openai-codex-responses error: Duplicate item found with id msg_3
line 870: same error, diagnostics requestBytes: 2385147, phase: before_message_stream_start
```

A targeted scan found assistant messages with both thinking and text blocks. The most important one after compaction was line `355`:

```text
line 355 id e112f421
provider: zai
api: openai-completions
model: glm-5.1
content types: ['thinking', 'text', 'toolCall']
```

That line had the shape needed to reproduce the bug: a foreign assistant message with multiple text-like blocks after transformation.

## The correct fix shape

The fix is to make fallback IDs unique per emitted OpenAI Responses message item, not merely per source Pi message. Upstream solved this by adding a per-assistant-message `textBlockIndex` and by changing fallback IDs from `msg_${msgIndex}` to `msg_pi_${msgIndex}` / `msg_pi_${msgIndex}_${textBlockIndex}`.

The relevant upstream commits are:

```text
3f1ce9b6 fix(ai): avoid duplicate Codex replay message ids closes #5148
d1fb34bc fix(ai): use valid synthetic Responses message ids closes #5148
```

The fixed logic in latest upstream has this essential shape:

```ts
let msgIndex = 0;
for (const msg of transformedMessages) {
  if (msg.role === "assistant") {
    let textBlockIndex = 0;

    for (const block of msg.content) {
      if (block.type === "text") {
        const fallbackMessageId =
          textBlockIndex === 0
            ? `msg_pi_${msgIndex}`
            : `msg_pi_${msgIndex}_${textBlockIndex}`;
        textBlockIndex++;

        let msgId = parsedSignature?.id;
        if (!msgId) {
          msgId = fallbackMessageId;
        }

        output.push({ type: "message", id: msgId, ... });
      }
    }
  }
  msgIndex++;
}
```

There are two design decisions here. First, the ID includes the source message index, so it remains stable across repeated replay of the same context. Second, the ID includes a per-message text block index only when needed, so a single source assistant message can safely produce multiple provider message items.

## Local source workflow

The installed global package was still `0.73.1`:

```bash
npm list -g @mariozechner/pi-coding-agent --depth=0
# /home/manuel/.nvm/versions/node/v22.22.1/lib
# └── @mariozechner/pi-coding-agent@0.73.1
```

There were two local Pi checkouts. The one used for source work was:

```text
/home/manuel/code/others/llms/pi/mariozechner/pi-mono
```

The important operational lesson is to fetch before patching. The local checkout initially pointed at an older `main` commit. After fetching upstream, `origin/main` contained the fix already. The correct move was to reset to upstream rather than keep a redundant local patch:

```bash
cd /home/manuel/code/others/llms/pi/mariozechner/pi-mono

git fetch origin
git reset --hard origin/main
```

After the reset, the checkout reported package versions `0.77.0` for both `packages/coding-agent` and `packages/ai`, while the installed global Pi remained `0.73.1`. That distinction matters. A source checkout being fixed does not change the executable used by the shell until it is built, linked, installed, or globally updated.

## Regression test

The regression test should not call the provider. It should test the conversion function directly. The bug was deterministic before the network request, so a unit test is better than an end-to-end provider test.

The upstream test lives at:

```text
/home/manuel/code/others/llms/pi/mariozechner/pi-mono/packages/ai/test/openai-responses-message-id.test.ts
```

The test constructs a foreign assistant message with both a thinking block and a text block, then verifies that `convertResponsesMessages()` emits unique OpenAI Responses message IDs.

```ts
const assistant: AssistantMessage = {
  role: "assistant",
  content: [
    { type: "thinking", thinking: "I should explain the plan first." },
    { type: "text", text: "Here is the plan." },
  ],
  api: "openai-completions",
  provider: "zai",
  model: "glm-5.1",
  usage,
  stopReason: "stop",
  timestamp: Date.now() - 1000,
};

const input = convertResponsesMessages(
  model,
  context,
  new Set(["openai", "openai-codex", "opencode"]),
);

const ids = input
  .filter((item) => item.type === "message")
  .map((item) => item.id);

expect(new Set(ids).size).toBe(ids.length);
```

The targeted local verification command was:

```bash
cd /home/manuel/code/others/llms/pi/mariozechner/pi-mono

npx vitest --run \
  packages/ai/test/openai-responses-message-id.test.ts \
  packages/ai/test/openai-responses-foreign-toolcall-id.test.ts
```

Both tests passed on the upstream checkout.

## Common failure modes when debugging Pi itself

The first failure mode is patching the wrong layer. The user-facing error appears in a project session, but the failing boundary may be Pi's provider adapter. Before changing application code, inspect whether the error happens before or after provider streaming begins. If the transcript says `phase: before_message_stream_start`, focus on request construction.

The second failure mode is testing with the wrong installed version. The source checkout can be correct while `/home/manuel/.nvm/versions/node/v22.22.1/bin/pi` still points at an older global npm package. Always check both:

```bash
which pi
npm list -g @mariozechner/pi-coding-agent --depth=0
node -e "console.log(require('/path/to/pi-mono/packages/coding-agent/package.json').version)"
```

The third failure mode is running the entire test suite and treating environmental failures as regression failures. The full `packages/ai` test suite includes provider and OAuth tests. In this investigation, unrelated failures came from unsupported Codex model names, expired Anthropic OAuth refresh, and local Ollama model availability. The conversion regression is covered by a small deterministic test and should be validated separately first.

The fourth failure mode is forgetting compaction. After a compaction event, the request context is not the full raw JSONL prefix. It is a compacted state plus the kept messages after `firstKeptEntryId`. When an error mentions `msg_3`, that index is usually relative to the transformed replay context, not line 3 of the original transcript.

## Recommended implementation sequence for future Pi replay bugs

Use this sequence when a future Pi session fails with a provider validation error:

1. Locate the session JSONL under `~/.pi/agent/sessions/<cwd-slug>/` and grep for the provider error string.
2. Convert only the failing session with `go-minitrace convert pi --source-session ...`.
3. Use `go-minitrace query duckdb --preset session-list` to establish turn count, tool count, model, and duration.
4. Inspect raw JSONL around the failing lines. Record model switches, compaction events, and provider diagnostics.
5. Find the provider conversion path in `packages/ai/src/providers/`.
6. Write a unit test at the conversion boundary before trying an end-to-end provider request.
7. Fetch upstream before carrying a local patch. The bug may already be fixed on `origin/main`.
8. Verify the focused test. Run broader tests only after the deterministic test passes.
9. Update the global Pi installation or link the local checkout before retrying the original workflow.
10. Record the transcript path, source commit, test command, and installed version in a durable note.

## Working rules

- Treat the JSONL transcript as evidence. Do not infer the failure path from memory when the transcript can show it.
- Separate application bugs from agent runtime bugs. Provider errors before stream start usually belong to Pi or the provider adapter.
- Prefer conversion-unit tests for replay bugs. They are faster, deterministic, and do not depend on provider credentials.
- Rebase or reset to latest upstream before writing a local fix. Pi moves quickly, and provider bugs may already be fixed.
- Verify the executable actually used by the shell. Updating a source checkout does not update global `pi` by itself.

## Related notes

- [[ARTICLE - Chat Overlay API - Two Proposals for a Typed Widget Streaming Architecture]] — the project session that exposed the bug.
- Pi source checkout: `/home/manuel/code/others/llms/pi/mariozechner/pi-mono`
- Failing session transcript: `/home/manuel/.pi/agent/sessions/--home-manuel-workspaces-2026-05-29-chatbot-react--/2026-05-29T12-52-32-763Z_019e73cb-217a-72b8-8267-137c6376439d.jsonl`
- Fixed provider file: `/home/manuel/code/others/llms/pi/mariozechner/pi-mono/packages/ai/src/providers/openai-responses-shared.ts`
- Regression test: `/home/manuel/code/others/llms/pi/mariozechner/pi-mono/packages/ai/test/openai-responses-message-id.test.ts`
