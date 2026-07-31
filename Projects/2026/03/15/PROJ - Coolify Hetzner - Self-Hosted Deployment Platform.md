---
title: Coolify Hetzner
aliases:
  - Coolify Hetzner
  - Project Coolify Hetzner
  - HQ Server
tags:
  - project
  - devops
  - infrastructure
  - coolify
  - hetzner
  - self-hosted
status: historical
type: project
created: 2026-03-15
repo: /home/manuel/code/wesen/2026-03-15--install-coolify
server: 89.167.52.236
domain: hq.scapegoat.dev
---

> [!warning] Historical — the Coolify platform is retired
> This note describes deployment on Coolify. The platform moved to Hetzner k3s with Argo CD
> and Vault; see [[Projects/2026/03/27/PROJ - K3s Migration Program - From Coolify to GitOps Platform]].
> Nothing after 2026-05 runs on Coolify. Every service named here that still exists now has an
> Argo CD package under `gitops/kustomize/` in `wesen/2026-03-27--hetzner-k3s`.
>
> The analysis and the reasons for the migration remain worth reading. The **procedures** do not
> apply — for current deployment see
> [[Research/KB/Projects/infrastructure-and-release]] and the k3s repo's
> `docs/app-deployment-pipeline.md`.

# Coolify Hetzner

This project configures and operates a self-hosted Coolify v4 instance on a Hetzner cloud server. The server acts as a general-purpose deployment platform for web applications and services, accessible at `hq.scapegoat.dev`. The first deployed service is Keycloak for identity management at `auth.scapegoat.dev`.

> [!summary]
> The project has two purposes:
> 1. a production deployment platform for web apps and services via Coolify
> 2. a central identity and authentication layer via Keycloak

## Why this project exists

Running a personal deployment platform removes the friction of spinning up new services. Instead of configuring a fresh VPS for each project, Coolify provides a single dashboard where new applications, databases, and services can be deployed from Git repos or Docker images with automatic SSL, domain routing, and health monitoring.

The Hetzner server was chosen for its cost-to-performance ratio and European data residency. The `scapegoat.dev` domain provides a stable namespace for all hosted services.

## Current project status

The server is fully operational with core infrastructure in place.

What already exists:

- Coolify v4.0.0-beta.468 dashboard at `https://hq.scapegoat.dev`
- Keycloak 26.1 at `https://auth.scapegoat.dev`
- Traefik v3.6.10 reverse proxy with automatic Let's Encrypt SSL
- Firewall hardened via DOCKER-USER iptables (only ports 22, 80, 443 open)
- Daily platform backups (config, DB dumps, 7-day retention)
- Scheduled database backups every 6 hours via Coolify built-in scheduler

What is still incomplete:

- S3 offsite backups (Hetzner Storage Box available but not yet configured)
- Email notifications for alerts and backup failures
- No application deployments beyond Keycloak yet
- No monitoring dashboard or alerting

## Project shape

The project has three layers:

1. **Infrastructure**
   - Hetzner cloud server (ubuntu-16gb-hel1-1, Helsinki)
   - Ubuntu 24.04, Docker, Coolify v4
   - Traefik reverse proxy with Let's Encrypt
   - DigitalOcean DNS for `scapegoat.dev`

2. **Platform services**
   - Coolify dashboard — deploy and manage apps
   - Keycloak — identity provider and SSO
   - PostgreSQL — shared database (deployed via Coolify)

3. **Operations**
   - Automated backups (platform + database)
   - Firewall rules persisted via iptables-persistent
   - Implementation diary tracking all configuration changes

## Architecture

```text
Internet
  -> DNS (scapegoat.dev via DigitalOcean)
  -> Hetzner server (89.167.52.236)
  -> Traefik v3.6 (ports 80/443)
     -> hq.scapegoat.dev    -> Coolify dashboard (coolify:8080)
     -> auth.scapegoat.dev  -> Keycloak 26.1 (keycloak:8080)
     -> *.scapegoat.dev     -> future services
```

Key server paths:

- `/data/coolify/source/.env` — Coolify environment config
- `/data/coolify/proxy/docker-compose.yml` — Traefik proxy config
- `/data/coolify/proxy/dynamic/` — Traefik routing rules (watched, auto-reload)
- `/data/coolify/services/` — deployed service configs
- `/data/coolify/backups/` — local backup storage
- `/data/coolify/backups/platform-backup.sh` — daily platform backup script
- `/etc/iptables/rules.v4` — persisted firewall rules

## Running services

| Service | Domain | Container | Version |
|---------|--------|-----------|---------|
| Coolify dashboard | `hq.scapegoat.dev` | coolify | v4.0.0-beta.468 |
| Keycloak | `auth.scapegoat.dev` | keycloak-k12lm4blpo13louovn3pfsgs | 26.1 |
| Traefik proxy | — | coolify-proxy | v3.6.10 |
| Coolify DB | — | coolify-db | PostgreSQL 15 |
| App PostgreSQL | — | go1o5tbegalwy3kesshq3hcp | PostgreSQL |
| Redis | — | coolify-redis | 7 |
| WebSocket | — | coolify-realtime | soketi |
| Health monitor | — | coolify-sentinel | 1.0.12 |

## Security posture

The server uses a layered firewall approach because Docker bypasses UFW by managing its own iptables chains:

- **UFW** was initially configured but was removed during iptables-persistent installation; not reinstalled because DOCKER-USER rules are more reliable with Docker.
- **DOCKER-USER iptables chain** blocks ports 8000 (Coolify direct), 8080 (Traefik API), 6001 (WebSocket), and 6002 (terminal) on eth0. These ports are only needed when accessing Coolify by IP; with a custom domain through Traefik, they can safely be closed per Coolify documentation.
- **Persisted** via iptables-persistent to `/etc/iptables/rules.v4`.
- All HTTPS traffic uses TLS 1.3 with Let's Encrypt certificates.

## Important project docs

- `/home/manuel/code/wesen/2026-03-15--install-coolify/ttmp/2026/03/15/COOLIFY-001--configure-coolify-on-hetzner-server/reference/01-diary.md` — full implementation diary (6 steps covering assessment, SSL, firewall, Keycloak, and backups)
- `/home/manuel/code/wesen/2026-03-15--install-coolify/ttmp/2026/03/15/COOLIFY-001--configure-coolify-on-hetzner-server/index.md` — ticket index

## Open questions

- What applications should be deployed next?
- Should S3 offsite backups use Hetzner Storage Box or another provider?
- Should Keycloak be integrated as SSO for Coolify itself and future services?
- What monitoring and alerting should be set up (Grafana, Uptime Kuma, etc.)?
- Should a wildcard SSL certificate (`*.scapegoat.dev`) be used instead of per-domain Let's Encrypt?

## Near-term next steps

- Configure S3 offsite backups to Hetzner Storage Box
- Set up email notifications (SMTP or Resend) for Coolify alerts
- Deploy first application workload
- Consider adding Uptime Kuma or similar for service health monitoring
- Configure Keycloak realms and clients for SSO

## Project working rule

> [!important]
> All server changes are documented in the implementation diary under docmgr ticket COOLIFY-001.
> Prefer configuring services through their compose files and Traefik dynamic config over manual UI changes, so the configuration is reproducible and tracked.
