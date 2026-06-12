# hello-agent

A deliberately simple **"Hello Agent's World"** web app. The app itself is
trivial — the goal of this project is to practice a complete, realistic
development workflow:

```
git push → CI (lint + test + build) → CD (build & push image, deploy) → dev/stage on a home server
```

...and ultimately to use that server, via an agentic coding tool, to extend
the app itself. See [`docs/`](docs/) for the full picture.

## Stack

- **App**: Python 3.12, [FastAPI](https://fastapi.tiangolo.com/) + Jinja2, served by `uvicorn`
- **Quality**: `ruff` (lint), `pytest` (tests)
- **Packaging**: Docker (single small image, non-root user)
- **CI/CD**: GitHub Actions → GitHub Container Registry (GHCR) → Tailscale + SSH deploy
- **Runtime**: Docker Compose, two environments (`dev`, `stage`) on an Ubuntu 22.04 home server

## Quickstart

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt

# Lint & test
ruff check .
pytest

# Run the dev server
APP_ENV=local APP_VERSION=local-dev uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000 and http://127.0.0.1:8000/health.

## Run with Docker

```bash
docker build -t hello-agent:local --build-arg APP_VERSION=$(git rev-parse --short HEAD) .
docker run --rm -p 8000:8000 -e APP_ENV=local hello-agent:local
```

## Deploy host setup (one-time)

CI/CD does **not** create the compose stack on the deploy host — before the
first CD run for an environment, create it manually:

```bash
# on the deploy host (e.g. rusty), as the deploy user
mkdir -p ~/deploy/hello-agent/{dev,stage}

# copy each environment's files from this repo, e.g.:
#   docker/compose/dev/docker-compose.yml   -> ~/deploy/hello-agent/dev/docker-compose.yml
#   docker/compose/dev/.env.example         -> ~/deploy/hello-agent/dev/.env
# (and the same for stage)
```

The GHCR package (`hello-agent`) must also be **public** so
`docker compose pull` on the host needs no authentication. Without this
setup, `docker compose pull`/`up` fail with "no configuration file provided"
and the deploy step's health check fails. See
[`docs/rusty-setup.md`](docs/rusty-setup.md) for the full runbook.

## Documentation

- [`docs/architecture.md`](docs/architecture.md) — app structure, configuration, dev/stage rationale
- [`docs/deployment.md`](docs/deployment.md) — CI/CD pipeline, image tagging, rollback
- [`docs/rusty-setup.md`](docs/rusty-setup.md) — one-time setup of the deploy server ("rusty")
- [`docs/lessons-learned.md`](docs/lessons-learned.md) — gotchas from getting CI/CD running end-to-end
- [`docs/agent-workflow.md`](docs/agent-workflow.md) — using Claude Code as `dev-agent` to extend this app

Agent-specific operating rules (Docker permissions, do/don't) live in
[`CLAUDE.md`](CLAUDE.md).
