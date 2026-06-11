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

## Documentation

- [`docs/architecture.md`](docs/architecture.md) — app structure, configuration, dev/stage rationale
- [`docs/deployment.md`](docs/deployment.md) — CI/CD pipeline, image tagging, rollback
- [`docs/rusty-setup.md`](docs/rusty-setup.md) — one-time setup of the deploy server ("rusty")
- [`docs/agent-workflow.md`](docs/agent-workflow.md) — using Claude Code as `dev-agent` to extend this app

Agent-specific operating rules (Docker permissions, do/don't) live in
[`CLAUDE.md`](CLAUDE.md).
