---
title: "Go Logging Landscape: Zerolog, Slog, and Per-Component Control"
aliases:
  - Go Logging Landscape
  - Logging in Go
  - Zerolog vs Slog
  - Per-Component Logging
tags:
  - article
  - go
  - logging
  - zerolog
  - slog
  - glazed
  - engineering
status: active
type: article
created: 2026-04-23
repo: /home/manuel/code/wesen/2026-04-20--js-discord-bot
---

# Go Logging Landscape: Zerolog, Slog, and Per-Component Control

This article explains the Go logging landscape as of early 2026: what the standard library's `log/slog` offers, what third-party libraries like zerolog provide, how the distinction between a **logger value** and a **log sink** shapes runtime configurability, and what it takes to get per-component level control that survives a format or level change after startup. The investigation was triggered by a concrete bug in a Discord bot where two loggers — one package-level and one constructed at call time — produced different output formats despite both using zerolog and both being configured by glazed.

> [!summary]
> 1. Zerolog sub-loggers created with `log.With()` are value copies that snapshot the global logger's state at creation time; they will not update when you reconfigure the global logger at runtime.
> 2. The `log/slog` standard library's `slog.Handler` interface separates log formatting (handlers) from log routing, making per-component filtering straightforward to implement without a third-party library.
> 3. `github.com/sei-protocol/seilog` is the most complete solution for slog-based per-logger level control with hierarchical names and glob-pattern level assignment; it returns plain `*slog.Logger`.
> 4. Migrating from zerolog to slog inside a Go application requires a decision about the CLI layer: keep glazed's zerolog-based flags, use a slog-to-zerolog bridge handler, or replace the CLI layer with slog-native configuration.
> 5. The correct way to build a dynamic sub-logger in Go is to always derive it from the current global logger at call time, never store it in a package-level variable.

## Why this article exists

The triggering incident was a Discord bot (`js-discord-bot`) that used two logging patterns simultaneously. One part of the code used a package-level zerolog sub-logger:

```go
var dispatchLog = log.With().Str("component", "dispatch").Logger()
```

Another part constructed loggers at call time:

```go
e := log.Info()
e.Str("component", "dispatch")
e.Msg("message")
```

Both parts used the same zerolog global logger. Yet at startup, the first logger produced JSON output while the second produced text console output. The reason lies in how Go evaluates package-level variables relative to when the logging library is initialized — and in how zerolog's `Logger` type works as a value type rather than a reference.

Understanding that mechanism leads to a deeper question: what does it take to configure logging per component — `"discord-bot/dispatch"` at debug, `"discord-bot/bot"` at warn, everything else at info — and change those settings at runtime without recompiling? That question takes us through zerolog's design, the `log/slog` standard library, and a small ecosystem of slog extensions designed to solve exactly this problem.

## Part I: The Zerolog Sub-Logger Problem

### How zerolog's global logger works

Zerolog's primary interface is the package-level `log` variable of type `zerolog.Logger`:

```go
var log = zerolog.New(os.Stderr).With().Timestamp().Logger()
```

This variable lives in the `github.com/rs/zerolog/log` package. When you configure it — for example, by calling `log.Logger = log.Output(writer)` — you are mutating a package-level singleton. Every direct call to `log.Info()`, `log.Debug()`, or `log.Error()` reads from and writes to that singleton.

Zerolog also provides a way to attach structured fields to a logger: `log.With().Str("key", "value").Logger()`. This returns a **new** `zerolog.Logger` value. The key insight is that it is a value, not a reference. The new logger is a copy of the current global logger, frozen at the moment of the call, with the additional context fields baked in.

```go
// This creates a NEW Logger value, initialized from the current global logger.
var dispatchLog = log.With().Str("component", "dispatch").Logger()

// Later, if the global logger is reconfigured:
log.Logger = log.Output(consoleWriter)

// dispatchLog still points to the OLD logger.
// It will write to the original destination, in the original format.
```

This is the bug that was encountered. `dispatchLog` was created during package initialization, before glazed called `logging.InitLoggerFromCobra(cmd)` in the `PersistentPreRunE`. At that point, the global zerolog logger was still using its default JSON writer (zerolog's default). When glazed later swapped in a `zerolog.ConsoleWriter`, `dispatchLog` had already captured the original JSON writer and never saw the change.

### Why this is hard to discover

Go's package initialization order is deterministic but not obvious. Package-level variables are initialized before `main()` runs, but `main()` may be in a different package entirely. In a CLI application that uses cobra and glazed, the initialization sequence looks roughly like this:

1. All imported packages initialize their package-level variables (including `dispatchLog`)
2. `main()` runs
3. Cobra parses flags
4. `PersistentPreRunE` calls `logging.InitLoggerFromCobra(cmd)`
5. The global zerolog logger is now configured

The bug occurs because step 1 happens before step 4, but the developer reads the code top-to-bottom and expects the reconfiguration in step 4 to affect everything.

### The correct pattern in zerolog

The fix is simple: never store a zerolog sub-logger in a package-level variable. Always derive the sub-logger from the global logger at the point of use:

```go
// Wrong: frozen at package init time, will not update
var dispatchLog = log.With().Str("component", "dispatch").Logger()

// Correct: derived from the current global logger at call time
func dispatchLogger() zerolog.Logger {
    return log.With().Str("component", "dispatch").Logger()
}

// Usage at call site
dispatchLogger().Info().Str("type", "Promise").Msg("settleValue")
```

This works, but it has a cost: it allocates a new `Logger` value and a new `Context` chain on every call. For high-frequency logging paths — which is exactly where you'd want a named sub-logger for filtering — this is a real allocation cost.

### What you cannot do with zerolog alone

Even with the correct pattern, zerolog's design fundamentally limits what you can do at runtime. The global level is set by `zerolog.SetGlobalLevel(level)` and affects all loggers that consult it. Sub-loggers created with `With()` do not maintain their own independent level settings. There is no registry of named loggers, no glob patterns, no per-component filtering. You can change the global level, but you cannot say "debug level for the dispatch component, warn level for everything else" and change it at runtime.

This is the gap that `log/slog` and its extensions were designed to fill.

## Part II: The `log/slog` Standard Library

### What slog brings to the table

`log/slog` landed in Go 1.21 as the standard library's answer to structured logging. Its core contribution is the `slog.Handler` interface, which cleanly separates the question of "what does a log record contain?" from "what happens to that record?"

```go
type Handler interface {
    Enabled(ctx context.Context, level Level) bool
    Handle(ctx context.Context, record Record) error
    WithAttrs(attrs []Attr) Handler
    WithGroup(name string) Handler
}
```

Every `slog.Logger` wraps a handler. When you call `log.Info(...)`, the logger delegates to its handler. When you call `log.With(...)`, the logger calls `handler.WithAttrs(...)` to produce a new handler with additional context. This chain of `WithAttrs` produces child loggers that carry additional attributes forward through the handler chain.

The critical property of this design is that the **handler** is what carries the filtering logic. A handler can inspect a record and decide to drop it, route it somewhere else, transform it, or pass it through. The logger is thin — it holds a reference to a handler and some context. Changing the handler's behavior at runtime changes the behavior of all loggers that share it.

### Levels in slog

`slog` has five built-in levels:

```go
const (
    LevelDebug Level = -4
    LevelInfo  Level = 0
    LevelWarn  Level = 4
    LevelError Level = 8
)
```

Unlike zerolog, slog does not have a single global level. Instead, each handler decides for itself what level to use via its `Enabled` method. The built-in `slog.JSONHandler` and `slog.TextHandler` accept a `slog.HandlerOptions` struct that lets you set a minimum level:

```go
h := slog.NewJSONHandler(os.Stderr, &slog.HandlerOptions{
    Level: slog.LevelInfo,
})
```

This is a fixed level at handler construction time. To make it dynamic, you need to either:

1. Use a `slog.LevelVar` — a pointer to a level that can be changed at runtime
2. Write a custom handler that consults a registry or map

### LevelVar: the simplest dynamic level

```go
var globalLevel slog.Level = slog.LevelInfo

h := slog.NewJSONHandler(os.Stderr, &slog.HandlerOptions{
    Level: &globalLevel,  // accepts slog.Leveler (interface)
})

log := slog.New(h)

// At runtime:
globalLevel.Set(slog.LevelDebug)
```

`LevelVar` implements `slog.Leveler`, so passing `&globalLevel` to `HandlerOptions.Level` makes the level dynamic. Every call to `Enabled` reads the current value of the variable atomically.

This is useful for global-level changes. What it does not give you is per-component filtering — the ability to have `"discord-bot/dispatch"` at debug while `"discord-bot/bot"` stays at warn.

### Per-component filtering requires a custom handler

To get per-component level control, you need a handler that:

1. Looks for a "component" or "name" attribute in the record (or in the logger's context)
2. Consults a registry mapping component names to levels
3. Drops the record if the record's level is below the component's threshold

The handler interface is small enough that this takes roughly 80-100 lines of Go. This pattern is well-established and several libraries implement it, which we will cover in Part IV.

## Part III: How Glazed's Logging Works

### The layered architecture

Glazed's logging lives in `github.com/go-go-golems/glazed/pkg/cmds/logging`. It is built on zerolog and provides three things:

1. **A Glazed field section** (`schema.NewSection` with fields for log-level, log-format, log-file, etc.) that integrates with the CLI argument parsing system
2. **A Cobra flag wiring** (`AddLoggingSectionToRootCommand`) that registers persistent flags on a cobra root command
3. **An initialization function** (`InitLoggerFromSettings`) that configures the global zerolog logger

The key file is `init.go`, which contains `InitLoggerFromSettings`:

```go
func InitLoggerFromSettings(settings *LoggingSettings) error {
    // 1. Optionally set caller info
    if settings.WithCaller {
        log.Logger = log.With().Caller().Logger()
    }

    // 2. Set timestamp format
    zerolog.TimeFieldFormat = time.RFC3339Nano

    // 3. Pick the output writer (ConsoleWriter for text, os.Stderr for JSON)
    var logWriter io.Writer
    if settings.LogFormat == "text" {
        logWriter = zerolog.ConsoleWriter{
            Out:        os.Stderr,
            NoColor:    !isatty.IsTerminal(os.Stderr.Fd()),
            TimeFormat: time.RFC3339Nano,
        }
    } else {
        logWriter = os.Stderr
    }

    // 4. Optionally add file rotation
    if settings.LogFile != "" {
        logWriter = io.MultiWriter(logWriter, lumberjackLogger)
    }

    // 5. Optionally add Logstash
    if settings.LogstashEnabled {
        logWriter = zerolog.MultiLevelWriter(logWriter, logstashWriter)
    }

    // 6. Replace the global zerolog output
    log.Logger = log.Output(logWriter)

    // 7. Set the global level
    zerolog.SetGlobalLevel(level)
}
```

The function mutates three global zerolog internals: `log.Logger`, `zerolog.TimeFieldFormat`, and the global level via `zerolog.SetGlobalLevel`. All three affect the global logger. No component-specific configuration is possible.

### The early logging path

For applications that need logging before cobra command registration is complete, glazed provides `InitEarlyLoggingFromArgs`. This function pre-parses only the logging-related flags from the raw command-line arguments using a standalone `pflag.FlagSet`, then calls `InitLoggerFromSettings`. This allows log statements during command discovery to respect `--log-level`, but it does not add per-component control.

### What glazed does not provide

Glazed's logging layer is intentionally simple. It does not provide:

- Per-component or per-package level control
- Dynamic level changes after initialization
- Logger hierarchy or naming
- Routing logs to different handlers based on component
- Any mechanism that would require zerolog to consult something other than the global level

This simplicity is a deliberate design choice. Glazed is a CLI framework, and most CLI tools need exactly what glazed provides: one global level, one output format, optionally one log file, optionally one external sink. The gap only becomes visible when a more complex application — like a Discord bot with multiple runtime subsystems — needs finer-grained control.

## Part IV: The Per-Component Logging Ecosystem

### The core pattern

Every solution for per-component logging in Go works by wrapping a `slog.Handler` and consulting a registry at handle time. The registry maps component names (or patterns) to `slog.Level` values. The wrapper's `Handle` method reads the record's attributes, looks up the appropriate level, and returns early if the record should be dropped.

The implementation choices that differ between libraries are:

1. **How loggers are named**: flat strings, slash-separated hierarchies, dot-separated hierarchies
2. **How levels are assigned**: exact match, glob patterns, recursive subtree matching
3. **What gets returned**: a custom logger type (seilog) or a plain `*slog.Logger` (slog-env, dynamic-level-handler)
4. **How configuration happens**: env vars, code, config files, admin HTTP endpoints

### seilog: the batteries-included solution

[`github.com/sei-protocol/seilog`](https://github.com/sei-protocol/seilog) is a thin layer on top of slog that adds hierarchical logger names and per-logger runtime level control.

**Key design decisions:**

- Logger names are slash-separated paths: `seilog.NewLogger("discord-bot", "dispatch")` creates a logger named `"discord-bot/dispatch"`.
- Names are validated to match `[a-z0-9]+(-[a-z0-9]+)*`. This prevents silent typos like `"MyApp"` vs `"myapp"` creating separate registry entries.
- `SetLevel` accepts glob patterns using Go's `path.Match` semantics:
  - `"discord-bot/dispatch"` — exact match
  - `"discord-bot/*"` — direct children only
  - `"discord-bot/**"` — recursive, all descendants at any depth
  - `"*"` — everything
- `SetLevel` returns the number of loggers matched, which catches typos.
- Each logger returned is a plain `*slog.Logger`. There is no custom logger type, no wrapper, and no lock-in.
- The enabled-level check is a single atomic load, costing roughly 5 ns when the level is disabled.
- Environment variables (`SEILOG_FORMAT`, `SEILOG_LEVEL`, `SEILOG_OUTPUT`) control defaults at startup.

**Why this matters for the Discord bot use case:**

Instead of the problematic package-level `dispatchLog`, you'd have:

```go
// Package-level logger derived from the seilog registry
var dispatchLog = seilog.NewLogger("discord-bot", "dispatch")

// Runtime configuration — can be called from a CLI flag, admin endpoint, or signal handler
seilog.SetLevel("discord-bot/dispatch", slog.LevelDebug)
seilog.SetLevel("discord-bot/bot", slog.LevelWarn)
```

The `dispatchLog` here is a `*slog.Logger`, so all the standard slog API (`log.Info()`, `log.Debug()`, `slog.String("key", "val")`) works unchanged. The level changes propagate immediately to every goroutine because the registry is shared and the level check reads atomically.

### slog-env: environment-variable per-package control

[`github.com/cbrewster/slog-env`](https://github.com/cbrewster/slog-env) provides a `slog.Handler` that reads level configuration from the `GO_LOG` environment variable.

```
GO_LOG=info                    # global info level
GO_LOG=info,mypackage=debug    # mypackage at debug, everything else at info
GO_LOG=info,pkg1=error,pkg2=warn  # multiple packages
```

This is less flexible than seilog — you cannot change levels at runtime without a process restart — but it requires zero application code changes beyond wrapping the existing handler. It is a good fit for containerized deployments where log verbosity is controlled via environment variables.

### dynamic-level-handler: lightweight per-logger override

[`github.com/gekatateam/dynamic-level-handler`](https://github.com/gekatateam/dynamic-level-handler) wraps any `slog.Handler` and exposes an `OverrideLevel` function that sets the level for a specific child logger's handler.

The model is: you create a logger, derive child loggers with `log.With(...)`, then call `dynamic.OverrideLevel(childLogger.Handler(), level)` to change that specific child's threshold.

This is useful when you want to work entirely within vanilla slog's `With()` model rather than adopting a hierarchical naming scheme.

### slog-level-override: handler-level runtime override

[`github.com/martin-viggiano/slog-level-override`](https://github.com/martin-viggiano/slog-level-override) is a similar idea: a `slog.Handler` wrapper that lets you call `SetLevel(level)` on the handler at any time. The level is evaluated dynamically on each `Handle` call.

### slog-multi: handler composition for routing and filtering

[`github.com/samber/slog-multi`](https://github.com/samber/slog-multi) provides composable handler patterns: `Fanout` (broadcast to multiple handlers), `Router` (route to handlers based on predicates), `Pipe` (middleware chain), and `Failover` (fallback on errors).

While primarily designed for multi-destination routing rather than per-component filtering, `Router` with custom predicates can be used to route records to different handlers based on attributes. For example, you could route all records with `component=dispatch` to a debug-level handler and everything else to an info-level handler.

### zerolog-to-slog bridges

For applications that need to keep glazed's zerolog-based CLI flags but want slog's dynamic filtering inside the application, two bridges exist:

- `github.com/samber/slog-zerolog`: a slog handler that writes to a zerolog logger
- `github.com/samber/slog-zap`: a slog handler that writes to a zap logger

These let you wire slog's dynamic component filtering upstream of a zerolog sink, effectively getting the best of both: glazed's familiar flag interface, and slog's filterable handler chain inside the application.

### Comparison table

| Package | Name Model | Level Control | Runtime Change | Returns | Best For |
|---------|-----------|---------------|----------------|---------|----------|
| zerolog | Flat string via `With()` | Global only | Global via `SetGlobalLevel` | `zerolog.Logger` | Simple CLIs, structured JSON logging |
| `slog` + `LevelVar` | Flat string via `With()` | Global only | Global via `LevelVar.Set` | `*slog.Logger` | Stdlib-only, simple cases |
| seilog | Hierarchical slash-separated | Per-name with glob patterns | Yes, atomic | `*slog.Logger` | Log4j-style hierarchy, runtime toggling |
| slog-env | Flat string (package name) | Per-package via env | No (static at startup) | `*slog.Logger` | Containerized deployments, env-driven config |
| dynamic-level-handler | Via slog `With()` | Per-child logger | Yes | `*slog.Logger` | Vanilla slog, minimal additions |
| slog-level-override | Handler-level | Per-handler | Yes | handler wrapper | Minimal footprint |
| slog-multi | Predicate-based routing | Via predicates | Yes | composed `slog.Handler` | Multi-destination routing, not per-component filtering |

## Part V: The Handler Interface — The Key Design

Understanding per-component logging in Go requires understanding why the `slog.Handler` interface makes this tractable in a way that zerolog does not.

In zerolog, logging is a method chain:

```go
log.Info().Str("component", "dispatch").Msg("settleValue")
```

The `Info()` method returns a zerolog `*Event`, and the chain mutates that event before `Msg()` sends it. The event is a transient value — there is no handler to intercept or filter it.

In slog, logging calls a `slog.Logger`, which delegates to a `slog.Handler`:

```go
log.Info("message", slog.String("component", "dispatch"))
```

The handler's `Handle` method receives a complete `slog.Record`:

```go
type Record struct {
    Time    time.Time
    Level   Level
    Message string
    // ...
}
```

Because the record is a struct passed to `Handle`, a handler wrapper can inspect all fields — including attributes — and decide what to do. It can:

- Check the record level against a registry and return `nil` (drop)
- Pass the record to a nested handler (filter chain)
- Transform attributes before passing the record on (middleware)
- Route the record to different handlers based on a predicate (router)

This is the compositional model that zerolog lacks. In zerolog, the filtering decision would have to be made before constructing the event chain — which means you need a separate logger for each component. With slog, you have one logger and one handler chain, and the filtering logic lives in the handler where it can be swapped or reconfigured at runtime.

```mermaid
flowchart TD
    A["log.Info(\"settleValue\", slog.String(\"component\", \"dispatch\"))"] --> B["slog.Logger"]
    B --> C["slog.Handler (ComponentFilterHandler)"]
    C --> D{"component in registry?"}
    D -->|Yes| E["Check record.Level vs registry[component]"]
    D -->|No| F["Check record.Level vs global level"]
    E --> G{"record.Level >= threshold?"}
    G -->|Yes| H["Pass to next handler"]
    G -->|No| I["Drop record, return nil"]
    F --> G
    H --> J["JSONHandler / TextHandler"]
    J --> K["os.Stderr"]
    I --> K
```

The `ComponentFilterHandler` is what every per-component solution implements. It consults a registry, applies the appropriate threshold, and either drops or passes through. The concrete implementation differs in how the registry is structured and how the component name is extracted from the record.

## Part VI: Migration Paths from Glazed's Zerolog

If you decide to move the Discord bot (or another application) from glazed's zerolog-based logging to a slog-based system with per-component control, there are three paths.

### Path 1: Keep glazed, add a slog-to-zerolog bridge

This path keeps glazed's existing CLI flags (`--log-level`, `--log-format`, `--log-file`) unchanged. You initialize zerolog as glazed does today, then wrap a slog handler around the zerolog logger for use inside the application.

```go
import slogzerolog "github.com/samber/slog-zerolog"

// After glazed.InitLoggerFromCobra(cmd) — zerolog is now configured
logWriter := os.Stderr // or whatever glazed configured

// Create a slog handler that writes to zerolog
zerologHandler := slogzerolog.Option{Logger: &log}.NewZerologHandler(slog.NewTextHandler(logWriter, nil))

// Use slog for new code
appLog := slog.New(zerologHandler)
var dispatchLog = seilog.NewLogger("discord-bot", "dispatch")
```

This is the path of least disruption: glazed's interface stays the same, the zerolog output stays the same, and new code uses slog with seilog for component-level filtering. The downside is that you now have two logging ecosystems in the same binary.

### Path 2: Replace glazed's logging with slog-native configuration

This path removes the zerolog dependency from the CLI layer and uses slog's built-in handlers or a custom handler chain for the same functionality. The advantage is a single logging ecosystem. The cost is reimplementing glazed's flags (or using a different CLI argument parsing approach) and losing glazed's log file rotation and Logstash integration unless you reimplement them as slog handlers.

For a Discord bot, this path makes sense if the per-component control is a core requirement and the Logstash integration is not critical.

### Path 3: Migrate to seilog for component hierarchy, bridge to zerolog for CLI output

This hybrid path uses seilog for hierarchical logger creation and runtime level control, but bridges to zerolog for the final output so that the CLI layer can keep using glazed's output format and file rotation configuration.

```go
// seilog registry — per-component level control
var log = seilog.NewLogger("discord-bot", "main")

// Configure at startup (could come from a config file or CLI flags)
seilog.SetLevel("discord-bot/dispatch", slog.LevelDebug)
seilog.SetOutput(os.Stderr)  // or a zerolog writer

// In the dispatch path:
var dispatchLog = seilog.NewLogger("discord-bot", "dispatch")
dispatchLog.Info("settleValue", slog.String("type", fmt.Sprintf("%T", value)))
```

This is the cleanest path for the Discord bot use case. The component hierarchy maps naturally to the bot's architecture: `"discord-bot/dispatch"`, `"discord-bot/bot"`, `"discord-bot/host"`, etc. Runtime level changes are possible via seilog's API. And the output can be configured to match what glazed provides.

## Part VII: The Correct Sub-Logger Pattern

Regardless of which logging library you choose, there is a fundamental rule that prevents the bug encountered in the Discord bot:

> **Never store a derived sub-logger in a package-level variable.** Always derive it from the current global logger at the point of use.

In zerolog terms, this means using a function:

```go
// Never do this
var dispatchLog = log.With().Str("component", "dispatch").Logger()

// Do this instead
func dispatchLogger() zerolog.Logger {
    return log.With().Str("component", "dispatch").Logger()
}
```

In slog terms, the equivalent is:

```go
// If using seilog or a registry model:
var dispatchLog = seilog.NewLogger("discord-bot", "dispatch")

// If using vanilla slog With():
// Package-level storage is fine because With() returns a new *slog.Logger
// that shares the handler, and the handler is not frozen at creation time.
// BUT: prefer a factory function if the logger's handler might change.
```

The difference is that slog's `Logger` type wraps a handler interface, and handler state (like a dynamic level registry) lives in the handler, not in the logger value. A slog logger created with `slog.New(handler).With(...)` shares the handler with its parent. If you change the handler's internal state (like a level registry), all child loggers see the change because they all delegate to the same handler.

This is why seilog can return a package-level `var dispatchLog = seilog.NewLogger(...)` and still have it update when you call `seilog.SetLevel(...)`. The logger value holds a reference to the shared registry handler. The registry is what changes, not the logger.

In zerolog, the `Logger` value captures the output writer and the minimum level at creation time. Changing the global level or output writer does not retroactively update sub-loggers because they are value copies, not references to the global state.

## Part VIII: Summary and Recommendations

For a Go application that needs per-component logging with runtime reconfiguration, the clear recommendation in 2026 is to use `log/slog` with either seilog or a custom handler.

**Use seilog** when you want hierarchical names, glob-based level assignment, zero new API surface (returns plain `*slog.Logger`), and runtime level changes from code, admin endpoints, or signal handlers.

**Write a custom handler** when you need full control and want to keep dependencies minimal. The implementation is roughly 80-100 lines and gives you complete flexibility over how component names are extracted and how levels are looked up.

**Use a slog-to-zerolog bridge** when you must keep glazed's CLI flags and output format but want slog's handler-based filtering inside the application.

**Avoid zerolog sub-loggers in package-level variables.** The value semantics that make zerolog fast and allocation-friendly are exactly what prevent runtime reconfiguration of derived loggers. If you must use zerolog, always derive sub-loggers at call time.

The broader lesson is that logging configuration is not a one-time setup at program start. Real applications have components that are more or less verbose at different times, and the ability to change levels at runtime — from an admin command, a configuration reload, or a signal — is a genuine operational requirement, not a luxury. Go's `slog` and the ecosystem built around it make this straightforward to implement. Zerolog, despite being fast and well-designed for its era, does not.

## Related Notes

- [[PROJ - JS Discord Bot]] — the Discord bot that triggered this investigation
- [[ARTICLE - Go Go Goja Module Authoring]] — related Go-JavaScript bridge content
- [[ARTICLE - Go Go Golems Project Setup]] — project setup patterns that include logging configuration