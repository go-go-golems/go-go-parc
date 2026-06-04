---
title: GOTOOLCHAIN and Stale Docker Images on GHA Runners
created: 2026-06-03
tags:
  - til
  - go
  - docker
  - github-actions
---

# TIL - GOTOOLCHAIN and Stale Docker Images on GHA Runners

Official `golang` Docker images set `GOTOOLCHAIN=local` by default. This prevents Go from auto-downloading a newer toolchain even when `go.mod` requires a newer patch version.

GitHub Actions runners pre-cache Docker images (like `golang:1.26-bookworm`). That cached image can lag behind Docker Hub, so the runner may still have `1.26.3` even though `1.26.4` is available.

When `docker/build-push-action` runs without `pull: true`, it uses the stale local image, causing:

```
go: go.mod requires go >= 1.26.4 (running go 1.26.3; GOTOOLCHAIN=local)
```

**Fix:** Set `ENV GOTOOLCHAIN=auto` in the Dockerfile. Go then downloads the exact toolchain version required by `go.mod`, regardless of the base image patch version.

```dockerfile
FROM golang:1.26-bookworm AS go-build
WORKDIR /src
ENV GOTOOLCHAIN=auto
COPY go.mod go.sum ./
RUN go mod download
```

This is more robust than chasing exact patch tags every time `go.mod` bumps.
