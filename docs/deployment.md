# Deployment

## Overview

```
push to develop ──▶ CI (lint, test, build) ──▶ CD-Dev ──▶ build & push image ──▶ deploy to rusty:dev (8001)
push to main    ──▶ CI (lint, test, build) ──▶ CD-Stage ──▶ build & push image ──▶ deploy to rusty:stage (8002)
```

- Images are built and pushed to **GHCR**: `ghcr.io/sgiermek/hello-agent`
- Each push gets two tags: `:<git-sha>` (immutable, for rollback) and
  `:dev-latest` / `:stage-latest` (floating, tracked by the running compose stack)
- The deploy server "rusty" is reached over **Tailscale** (the GitHub Actions
  runner joins the tailnet ephemerally), then the deploy step connects over
  **SSH** as `dev-agent`

## CD connectivity: why Tailscale?

GitHub-hosted runners cannot reach rusty's LAN address (`192.168.10.100`)
directly. Three approaches were considered:

1. **Self-hosted GitHub Actions runner on rusty** — avoids the network
   problem, but a permanently-running runner process adds maintenance
   overhead on a 1.7GB box that's already running two app containers, and
   somewhat undermines the "CI reaches out to deploy" model.
2. **Tailscale (chosen)** — the GitHub-hosted runner joins the tailnet for
   the duration of the job (`tailscale/github-action`), then SSHes to
   rusty's Tailscale IP. `tailscaled` itself is a lightweight daemon
   (~20MB) and may be useful for LAN-independent access later anyway.
3. **Manual/hybrid** — CD only builds & pushes the image; deployment is done
   by hand on rusty. Lowest setup cost, but skips the part of the workflow
   this project exists to practice.

Browser access to the running app stays on the LAN
(`http://192.168.10.100:8001` / `:8002`) — Tailscale is only used as the
CI → server tunnel for deploys.

## What each CD run does

1. Build the Docker image, tag with `<git-sha>` and the env's floating tag, push to GHCR.
2. Connect to the tailnet (`tag:ci`).
3. SSH to `dev-agent@<rusty-tailscale-ip>`, in `~/deploy/hello-agent/<env>/`:
   ```bash
   docker compose pull
   docker compose up -d
   sleep 5
   curl -f http://localhost:<port>/health
   ```

The `docker-compose.yml` and `.env` files on rusty are **static
infrastructure**, created once during the [rusty setup](rusty-setup.md) and
not touched by routine deploys — only the image referenced by the floating
tag changes.

## Rollback

1. SSH to rusty as `dev-agent`.
2. In the affected environment's directory, edit `.env`:
   ```
   IMAGE_TAG=<previous-git-sha>
   ```
3. `docker compose up -d`

## Required GitHub repository configuration

Settings → Secrets and variables → Actions → **Repository secrets**:

| Secret | Purpose | How to obtain |
|---|---|---|
| `TAILSCALE_OAUTH_CLIENT_ID` / `TAILSCALE_OAUTH_CLIENT_SECRET` | Lets the CI runner join the tailnet ephemerally | Tailscale admin console → Settings → OAuth clients → generate, tag `tag:ci` |
| `DEPLOY_HOST` | rusty's Tailscale IP | `tailscale ip -4` on rusty (after `tailscale up`) |
| `DEPLOY_USER` | SSH user for deploy | `dev-agent` |
| `DEPLOY_SSH_KEY` | Private key for `dev-agent` on rusty | Generate on your machine: `ssh-keygen -t ed25519 -C "github-actions-hello-agent" -f ~/.ssh/hello_agent_deploy -N ""`. Paste the **private** key here; the **public** key goes into `dev-agent`'s `~/.ssh/authorized_keys` on rusty. |

Also required:

- Settings → Actions → General → Workflow permissions = **"Read and write
  permissions"** (needed to push to GHCR with the default `GITHUB_TOKEN`).
- After the first successful CD run, check the `hello-agent` package's
  visibility under your GitHub profile's **Packages** tab. If it's private,
  switch it to **Public** so `docker compose pull` on rusty needs no
  authentication.
- If your tailnet uses custom ACLs, ensure `tag:ci` exists under
  `tagOwners` in the Tailscale admin console's Access Controls, and that
  `tag:ci` can reach rusty on port 22.
