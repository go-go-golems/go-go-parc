---
title: Screencast Studio - Prometheus Metrics Architecture and Field Guide
aliases:
  - Screencast Studio Metrics Field Guide
  - Screencast Studio Prometheus Metrics Guide
  - Prometheus Metrics Architecture and Field Guide
tags:
  - article
  - screencast-studio
  - gstreamer
  - metrics
  - prometheus
  - observability
  - backend
status: active
type: article
created: 2026-04-15
repo: /home/manuel/code/wesen/2026-04-09--screencast-studio
---

# Screencast Studio - Prometheus Metrics Architecture and Field Guide

This note explains the project’s Prometheus-style metrics system: how it is implemented, what metric families exist, what each family is meant to answer, and how the investigation has been using those metrics during the preview/recording performance work.

The important thing to understand is that this metrics layer was not built as a generic observability platform first. It was built as an investigation tool: quick to extend, easy to scrape from ticket-local scripts, and precise enough to rule hypotheses in or out.

> [!summary]
> 1. The project uses a small in-process metrics registry rather than a heavier external client library.
> 2. `/metrics` exposes counters and gauges in Prometheus text format, and the experiments usually interpret counters through first/last snapshot deltas.
> 3. The most important metric families cover preview HTTP serving, PreviewManager internals, EventHub/websocket fanout, shared bridge recorder behavior, and GStreamer audio parse failures.
> 4. The metrics were good enough to rule out several upper-layer suspects before lower-level profiling became necessary.

## Why this note exists

The metrics surface has grown organically during the investigation. That is good for the project, but it also means a future investigator could easily ask:

- what does each metric family actually mean?
- which ones are gauges and which ones are cumulative counters?
- why did the project choose this lightweight implementation?
- how should short experiment runs interpret cumulative values?

This note answers those questions in one place.

## Architecture overview

### In-process registry

The core implementation lives in:

- `/home/manuel/code/wesen/2026-04-09--screencast-studio/pkg/metrics/metrics.go`

It provides:

- `CounterVec`
- `GaugeVec`
- a default process-local registry
- Prometheus text exposition through `WritePrometheus`

The key characteristics are:

- metrics are registered in-process
- label sets are normalized into stable keys
- values are stored with atomics
- exposition is deterministic and sorted
- the system currently supports counters and gauges, but not histograms or summaries

### Export endpoint

The metrics endpoint lives in:

- `/home/manuel/code/wesen/2026-04-09--screencast-studio/internal/web/handlers_metrics.go`

and is mounted at:

- `/metrics`

That endpoint simply renders the current contents of the default registry in Prometheus text format.

## How to think about the metrics

### Counters are cumulative

Most of the investigation metrics are counters.

That means short-lived experiments should almost never interpret the raw number in isolation. Instead, the useful interpretation is usually:

```text
last snapshot - first snapshot = delta for this run
```

That is exactly why the ticket-local browser samplers save repeated `.prom` snapshots and emit `metric-deltas.txt` files.

### Gauges describe current state

Examples:

- active MJPEG clients
- active websocket connections
- EventHub subscriber count

These are usually interpreted as the **last observed state** during a run.

### Timing metrics are cumulative nanosecond counters

The current system does not use histograms.

Instead, timing families are usually cumulative nanosecond totals, which means the normal interpretation is:

- total nanoseconds over the run
- divided by a relevant frame/event count if you want an approximate per-event cost

This turned out to be enough to answer the question the investigation actually cared about most often:

> is this path even remotely expensive enough to explain the observed CPU spike?

## Metric families by subsystem

## 1. Preview HTTP serving metrics

Defined in:
- `internal/web/preview_metrics.go`

Produced mainly by:
- `internal/web/handlers_preview.go`

Families:

- `screencast_studio_preview_http_clients`
  - gauge
  - labels: `source_type`
  - meaning: currently connected MJPEG preview clients

- `screencast_studio_preview_http_streams_started_total`
  - counter
  - labels: `source_type`
  - meaning: how many MJPEG streams started

- `screencast_studio_preview_http_streams_finished_total`
  - counter
  - labels: `source_type`, `reason`
  - meaning: why MJPEG streams ended

- `screencast_studio_preview_http_frames_served_total`
  - counter
  - labels: `source_type`
  - meaning: JPEG frames served to HTTP clients

- `screencast_studio_preview_http_bytes_served_total`
  - counter
  - labels: `source_type`
  - meaning: total multipart/JPEG bytes written

- `screencast_studio_preview_http_flushes_total`
  - counter
  - labels: `source_type`
  - meaning: total flush calls during MJPEG serving

- `screencast_studio_preview_http_loop_iterations_total`
  - counter
  - labels: `source_type`
  - meaning: total handler-loop iterations

- `screencast_studio_preview_http_idle_iterations_total`
  - counter
  - labels: `source_type`
  - meaning: loop iterations that did not serve a new frame

- `screencast_studio_preview_http_write_nanoseconds_total`
  - counter
  - labels: `source_type`
  - meaning: cumulative time spent writing multipart headers and JPEG bytes

- `screencast_studio_preview_http_flush_nanoseconds_total`
  - counter
  - labels: `source_type`
  - meaning: cumulative time spent in `Flush()`

### Why they matter

These metrics answered two increasingly narrow questions:

1. is the browser path serving dramatically more preview bytes than synthetic baselines?
2. is the final MJPEG write/flush loop itself expensive enough to explain the hot path?

The later result was especially important: final write/flush time turned out to be too small to explain the observed CPU spikes.

## 2. PreviewManager lifecycle and timing metrics

Defined in:
- `internal/web/preview_metrics.go`

Produced mainly by:
- `internal/web/preview_manager.go`

Families:

- `screencast_studio_preview_frame_updates_total`
- `screencast_studio_preview_frame_store_nanoseconds_total`
- `screencast_studio_preview_latest_frame_copy_nanoseconds_total`
- `screencast_studio_preview_state_publish_nanoseconds_total`
- `screencast_studio_preview_ensures_total`
- `screencast_studio_preview_releases_total`

These cover:

- how often frames are stored
- how expensive frame storage is
- how expensive copying the cached frame back out is
- how expensive `preview.state` publication is
- how preview ensure/release flows behave

### Why they matter

These metrics were added after MJPEG timing suggested the final HTTP write path was too cheap. They let the project test the next immediate Go-side layer and showed that PreviewManager overhead was also too small to explain the hot phase.

## 3. EventHub and websocket metrics

Defined in:
- `internal/web/event_metrics.go`

Produced mainly by:
- `internal/web/event_hub.go`
- `internal/web/handlers_ws.go`

Families:

- `screencast_studio_eventhub_subscribers`
- `screencast_studio_eventhub_events_published_total`
- `screencast_studio_eventhub_events_delivered_total`
- `screencast_studio_eventhub_events_dropped_total`
- `screencast_studio_eventhub_publish_nanoseconds_total`
- `screencast_studio_websocket_connections`
- `screencast_studio_websocket_events_written_total`
- `screencast_studio_websocket_event_write_errors_total`

### Why they matter

These metrics were added because the real browser path includes `/ws`, while the plain MJPEG baselines do not. They made it possible to test the websocket hypothesis directly and later to show that EventHub publish time was also too small to explain the full browser-path CPU spike.

## 4. GStreamer recording parse-failure metrics

Defined in:
- `pkg/media/gst/recording.go`

Family:

- `screencast_studio_gst_audio_level_parse_failures_total`

Labels:
- `reason`
- `rms_type`

### Why it matters

This family replaced a noisy repeated log line with a countable signal. It is more of an observability hygiene metric than a browser-path hotspot metric, but it is still part of the project’s metrics story.

## 5. Shared bridge recorder metrics

Defined in:
- `pkg/media/gst/shared_video_recording_bridge.go`

Families:

- `screencast_studio_gst_shared_bridge_recorder_samples_received_total`
- `screencast_studio_gst_shared_bridge_recorder_buffers_copied_total`
- `screencast_studio_gst_shared_bridge_recorder_enqueued_total`
- `screencast_studio_gst_shared_bridge_recorder_dropped_total`
- `screencast_studio_gst_shared_bridge_recorder_worker_handled_total`
- `screencast_studio_gst_shared_bridge_recorder_appsrc_pushed_total`

These help answer questions like:

- how many samples are reaching the bridge?
- how many buffers are copied?
- is the queue dropping?
- is the downstream appsrc path keeping up?

## Label strategy and why it matters

One of the project’s best metrics decisions was to keep labels low-cardinality.

Common labels include:

- `source_type`
- `reason`
- `result`
- `event_type`
- `rms_type`

The project intentionally avoided labels like:

- session ID
- preview ID
- source ID
- browser tab identity

That made the metrics easier to aggregate, easier to compare across many short runs, and much safer for future Prometheus/Grafana use.

## How the investigation actually used the metrics

### 1. To compare fresh-server and real-browser runs

By computing first/last deltas, the project turned cumulative counters into per-run evidence.

### 2. To reject the “it must just be more JPEG bytes” theory

Frame/byte deltas showed that browser recording runs were hot even without proportionally huge served-byte deltas.

### 3. To test the websocket hypothesis directly

EventHub and websocket counters made the synthetic websocket ablation measurable and showed that websocket fanout alone was too small.

### 4. To test whether final MJPEG write/flush time explains the spike

Timing counters showed it did not.

### 5. To test whether PreviewManager/EventHub internals explain the spike

More timing counters showed they also did not, which is exactly what justified starting lower-level profiling work.

## Current limitations

### No histograms or summaries

Timing metrics are cumulative totals, so distribution shape is not visible.

### No automatic per-run reset

The registry is process-global, so per-run meaning depends on first/last snapshot deltas.

### No built-in Prometheus retention or dashboards

The current setup is ideal for ticket-local scripts and manual analysis, but a full Prometheus+Grafana deployment would still need extra wiring.

### Not a substitute for lower-level profilers

The metrics are excellent for ruling out many application-level suspects, but they cannot explain lower-layer CPU in GStreamer, CGO, or libc. That is why the project eventually escalated to pprof and now toward perf.

## Working rules for future metrics work

- add metrics only when they answer a concrete question
- keep labels low-cardinality unless there is a strong reason not to
- prefer ticket-local delta interpretation for short experiments
- if cumulative timing is already tiny, move down the stack instead of adding more app-level counters blindly

## Important source docs

The source documents for this note are:

- `/home/manuel/code/wesen/2026-04-09--screencast-studio/ttmp/2026/04/14/SCS-0016--investigate-low-level-performance-hot-path-with-pprof-perf-and-ebpf/reference/03-prometheus-metrics-architecture-and-field-guide.md`
- `/home/manuel/code/wesen/2026-04-09--screencast-studio/pkg/metrics/metrics.go`
- `/home/manuel/code/wesen/2026-04-09--screencast-studio/internal/web/preview_metrics.go`
- `/home/manuel/code/wesen/2026-04-09--screencast-studio/internal/web/event_metrics.go`

## Related notes

- [[ARTICLE - Screencast Studio - Performance Investigation Approaches and Tricks]]
- [[Research Brief - Preview and Recording Performance Investigation Handoff]]
