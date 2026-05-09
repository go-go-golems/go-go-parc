---
title: Go-Side JavaScript DSLs for Discord Bots
aliases:
  - Go-side JS DSL for Discord bots
  - Discord UI DSL in Go
  - Error-first JS DSL builders
  - Go proxy DSL pattern for Goja
tags:
  - article
  - playbook
  - go
  - javascript
  - goja
  - discord
  - dsl
  - proxies
  - types
  - error-handling
status: active
type: article
created: 2026-04-22
repo: /home/manuel/code/wesen/2026-04-20--js-discord-bot
---

# Go-Side JavaScript DSLs for Discord Bots

This note captures a pattern that emerged while implementing a JavaScript UI DSL for Discord bots running inside a Goja runtime: keep the JavaScript surface pleasant, but move the builder logic into Go. That lets the host enforce types, catch bad method calls early, and control how payloads are normalized before they ever reach Discord.

The immediate trigger was the `ui-showcase` bot in `/home/manuel/code/wesen/2026-04-20--js-discord-bot`. The first version of the DSL lived in JavaScript. It was easy to write, but it leaked wrong shapes and let bad payloads escape until Discord rejected them. The final version moved the builders to Go and exposed them through `require("ui")` as Goja proxy objects.

> [!summary]
> - Put the builder state in Go, not in JavaScript, when you need strict validation and predictable shapes.
> - Use Goja Proxy traps to preserve fluent chaining while still rejecting wrong-parent calls and raw objects.
> - Return typed Go values from `.build()` so the host can normalize them directly and keep error handling centralized.

## Why this note exists

A JS DSL looks attractive because the surface reads naturally:

```js
ui.message()
  .content("Search results")
  .row(ui.pager("prev", "next", { hasPrevious, hasNext }))
  .build()
```

But once the DSL starts constructing real Discord payloads, the host becomes responsible for a few things that JavaScript is not very good at enforcing:

- whether a method belongs to the current builder
- whether a value is a real builder or a random object
- whether a component tree is structurally valid
- whether a message should create a new interaction response or update an existing one
- whether modal fields are keyed the way the submission handler expects

If the DSL stays in JavaScript, those mistakes often survive until the Discord API rejects them. That is too late. The better move is to shift the builder engine into Go, where the host can keep the shape of the data under control and let JavaScript focus on orchestration.

## When to use this pattern

Use a Go-side DSL when:

- the runtime is JavaScript, but the host is Go and already owns the normalization layer
- wrong payloads are expensive, noisy, or hard to debug after the fact
- the DSL needs fluent chaining, but also strict type and parent checking
- the host must choose between multiple transport behaviors, such as new-message vs in-place update
- the same builder output must work both in tests and in live interaction dispatch

Do not use it when:

- the JavaScript side is just a thin helper layer and validation is not important
- the payload shape is unstable and you expect to rewrite it often
- the host cannot conveniently expose native constructors or proxy traps

## Core mental model

The right mental model is not “JavaScript implements the DSL.” The right model is:

1. **JavaScript names the intent.**
   It decides what the bot wants to do: show a message, build a form, render a row, update a screen.

2. **Go owns the builder state.**
   The builder accumulates fields, components, and flags in a typed Go struct.

3. **The Proxy preserves the fluent shape.**
   JavaScript still sees `.content().embed().row().build()`.

4. **`.build()` returns a typed Go value.**
   The host can route that value into the Discord response path without reinterpreting loose JavaScript objects.

5. **Discord response behavior is chosen centrally.**
   The host decides whether a component click should update in place or create a follow-up message.

That last step matters more than it first appears. A UI DSL for bots is not only about constructing payloads. It is also about controlling the interaction lifecycle.

## Pattern shape

At a high level, the system looks like this:

```mermaid
flowchart TD
    JS[Bot script in Goja JS] --> UI[require("ui") Go module]
    UI --> P[Goja Proxy builders]
    P --> B[Typed Go builder structs]
    B --> R[normalizedResponse or Discord component]
    R --> N[normalizeResponsePayload / host responder]
    N --> D[Discord interaction response]

    style UI fill:#dbeafe,stroke:#2563eb
    style B fill:#dcfce7,stroke:#16a34a
    style N fill:#fef3c7,stroke:#d97706
    style D fill:#fee2e2,stroke:#dc2626
```

The important design choice is that the DSL objects are not plain JS objects. They are Go-backed proxy objects. That gives you fluent ergonomics without giving up the host’s control over validation and payload shape.

## Architecture

The implementation in `/home/manuel/code/wesen/2026-04-20--js-discord-bot` split into a few layers:

- `internal/jsdiscord/ui_module.go`
  - registers `require("ui")`
  - exports `message`, `embed`, `button`, `select`, `userSelect`, `roleSelect`, `channelSelect`, `mentionableSelect`, `form`, `row`, `pager`, `actions`, `confirm`, `card`, `ok`, `error`, `emptyResults`, and `truncate`
- `internal/jsdiscord/ui_message.go`
  - `MessageBuilder`
  - row flattening and component extraction
  - builder proxy traps for message methods
- `internal/jsdiscord/ui_components.go`
  - `ButtonBuilder`, `SelectBuilder`, typed selects
  - `optionEntries()` support for the showcase screens
- `internal/jsdiscord/ui_form.go`
  - modal builder with `text()` / `textarea()` field chaining
- `internal/jsdiscord/host_responses.go`
  - response-type selection
  - in-place component updates vs follow-up messages
- `internal/jsdiscord/payload_model.go`
  - `normalizedResponse` and payload normalization

The showcase bot in `examples/discord-bots/ui-showcase/` then consumes the module as a regular JS dependency:

```js
const ui = require("./lib/ui")
```

That `lib/ui/index.js` file now re-exports the Go module and the JS state helpers.

## Implementation details

### 1. Make the builder live in Go

The reason for moving the builder into Go is simple: Go can reject invalid states earlier and more consistently.

A button builder in JS can happily accept any object. A Go builder can reject wrong parents, type mismatches, and invalid construction paths using Proxy traps and explicit errors.

The builder pattern in Go looks like this:

```go
func newButtonBuilder(vm *goja.Runtime, customID, label, style string) goja.Value {
    b := &ButtonBuilder{customID: customID, label: label, style: resolveButtonStyle(style)}

    proxy := vm.NewProxy(target, &goja.ProxyTrapConfig{
        Get: func(target *goja.Object, property string, receiver goja.Value) goja.Value {
            switch property {
            case "disabled":
                return vm.ToValue(func(call goja.FunctionCall) goja.Value {
                    b.disabled = true
                    return receiver
                })
            case "build":
                return vm.ToValue(func(call goja.FunctionCall) goja.Value {
                    return vm.ToValue(b.build())
                })
            default:
                checkMethod(vm, "ui.button", property, buttonAvailable)
                return goja.Undefined()
            }
        },
    })

    return vm.ToValue(proxy)
}
```

This is the key move: JavaScript gets a normal fluent chain, but the host retains the struct and the trap logic.

### 2. Use Proxy traps for three kinds of method lookup

Every builder needs the same three-way decision tree:

- **own method** — return a chain function
- **known method from a different builder** — raise a guided error
- **unknown method** — raise a listable unknown-method error

That distinction matters. It produces errors like:

- `ui.message: .field() is not available here. You probably meant to call this on ui.embed().`
- `ui.select: unknown method .something(). Available: placeholder, option, options, optionEntries, minValues, maxValues, disabled, build.`

Those messages are much better than a generic “cannot read property of undefined” or “unexpected token.”

### 3. Return typed Go values from `.build()`

The `.build()` method should be the boundary where the builder becomes a real output object.

For example:

- `ui.embed(...).build()` → `*discordgo.MessageEmbed`
- `ui.button(...).build()` → `discordgo.Button`
- `ui.select(...).build()` → `discordgo.SelectMenu`
- `ui.message().build()` → `*normalizedResponse`

This is what gives the host control. It can route typed outputs to the right Discord response behavior and keep all normalization in one place.

### 4. Normalize once, not twice

One of the easiest mistakes in this kind of system is to create a typed value, export it to a generic map, and then reconstruct the typed value again later.

That path looks flexible, but it is where shape bugs sneak in.

The better rule is:

- JS objects can still flow through the old map-based normalization path
- Go builders should flow through a typed fast path
- the host should not round-trip a typed response through a generic map unless it absolutely has to

This was especially important for Discord buttons and select menus, where the library already knows how to serialize the proper component types.

### 5. Treat component interactions differently from slash commands

This is where the DSL stopped being “just a payload builder” and became an interaction-lifecycle tool.

Discord has different response types for different situations:

- slash commands normally create a new message
- component clicks often should update the message in place
- deferred component acknowledgements use a different callback type than deferred slash commands

The host now chooses response types centrally:

- **type 4** — new message
- **type 7** — update the component’s original message in place
- **type 6** — defer component update
- **type 5** — defer slash command response

That means a pager button click can update the existing UI instead of spraying new messages into the channel.

### 6. Flatten rows, don’t nest them

A helper like `ui.pager()` naturally returns a whole row. A message builder’s `.row(...)` method should accept that row and flatten it into its children instead of nesting rows inside rows.

That sounds like a small detail, but it is one of the most practical UI rules in the entire implementation.

If you do not flatten, Discord rejects the component tree.

The logic looks like this:

```go
func buildRowFromArgs(vm *goja.Runtime, args []goja.Value) discordgo.ActionsRow {
    var components []discordgo.MessageComponent
    for _, arg := range args {
        components = append(components, extractRowComponents(vm, arg)...)
    }
    return discordgo.ActionsRow{Components: components}
}
```

So a row helper can return a row, and `.row(...)` can still consume it.

### 7. Modal field keys must match the submission values

For modals, the `customId` of the text input becomes the key in `ctx.values` when the modal is submitted.

That means the builder has to preserve the mapping carefully:

```js
ui.form("showcase:form:submit", "Feedback Form")
  .text("title", "Title")
  .textarea("feedback", "Your feedback")
```

Here the first argument is the field key, not the label.

That detail is easy to get wrong, and when it goes wrong the modal opens successfully but the submit handler only sees defaults.

## Common failure modes

### Wrong-parent methods

If you call `ui.message().field(...)` or `ui.embed().ephemeral()`, the builder should not silently accept it. It should tell you which builder you probably meant.

That is why the method-owner map exists.

### Raw JS objects passed into typed methods

`ui.message().embed({ ... })` should not be normalized quietly. That would erase the whole point of the typed DSL.

The Go builder should reject raw objects and tell the caller to pass a real `ui.embed()` builder.

### Nested rows

`ui.message().row(ui.pager(...))` should flatten, not nest. Nested rows are invalid Discord payloads.

### Empty or nil values becoming “real” data

A nil value can become `"<nil>"` if you stringify too early. That is how duplicate select values and other confusing payload bugs appear.

### Relying on Discord to catch shape bugs

If Discord is the first validator, the error is already too late. The DSL should catch shape bugs before the HTTP request is made.

## Recommended implementation sequence

If you are building a similar system, this sequence is the safest:

1. **Start with a small Go-backed builder**
   - one or two methods only
   - prove that Proxy chaining works

2. **Add method-owner errors**
   - wrong parent
   - unknown method
   - type mismatch

3. **Return typed Go values from `.build()`**
   - do not normalize through a JS map if you can avoid it

4. **Add one response path at a time**
   - message
   - embed
   - buttons
   - selects
   - forms

5. **Add interaction lifecycle behavior**
   - new message vs update message
   - deferred update vs deferred new message
   - follow-up opt-out if you need it

6. **Write integration tests against the full dispatch pipeline**
   - not just unit tests for the builders
   - make sure the real response path stays healthy

## Pseudocode

Here is the overall shape of the system:

```text
function ui.message():
    builder = new MessageBuilder()
    return Proxy(builder)

Proxy Get trap:
    if property is an own method:
        return chain function
    else if property belongs to another builder:
        throw guided wrong-parent error
    else:
        throw unknown-method error

function build():
    validate builder state
    return typed Go output

function host reply(payload):
    if payload is normalizedResponse:
        choose response type based on interaction kind
        send data to Discord
    else:
        normalize legacy map/object payload
        send data to Discord
```

That is the whole pattern in one page: fluent JavaScript, typed Go, centralized host behavior.

## How to think about the tradeoff

The tradeoff is not “Go versus JavaScript.” It is:

- **JavaScript is the best place to write the bot’s intent.**
- **Go is the best place to enforce the shape of the response.**

The more the DSL acts like a real compiler front-end, the better the bot behaves under pressure. The host gets to decide how to serialize, how to update messages, how to defer, and how to surface errors. The JavaScript side gets a clean, fluent, ergonomic API.

That division of labor is the reason the final `ui-showcase` bot feels simpler than the original JavaScript-only prototype, even though the host has become more capable.

## Related implementation notes

Concrete repo paths worth reading alongside this article:

- `/home/manuel/code/wesen/2026-04-20--js-discord-bot/internal/jsdiscord/ui_module.go`
- `/home/manuel/code/wesen/2026-04-20--js-discord-bot/internal/jsdiscord/ui_message.go`
- `/home/manuel/code/wesen/2026-04-20--js-discord-bot/internal/jsdiscord/ui_components.go`
- `/home/manuel/code/wesen/2026-04-20--js-discord-bot/internal/jsdiscord/ui_form.go`
- `/home/manuel/code/wesen/2026-04-20--js-discord-bot/internal/jsdiscord/host_responses.go`
- `/home/manuel/code/wesen/2026-04-20--js-discord-bot/examples/discord-bots/ui-showcase/index.js`
- `/home/manuel/code/wesen/2026-04-20--js-discord-bot/examples/discord-bots/README.md`

Related ticket docs and source notes live under:

- `/home/manuel/code/wesen/2026-04-20--js-discord-bot/ttmp/2026/04/21/DISCORD-BOT-019--knowledge-base-bot-ui-dsl/`

## Closing rule

If you can move validation and response-shape control into the host without making the JavaScript API awkward, do it. The DSL stays pleasant. The errors get better. The bot becomes easier to debug.
