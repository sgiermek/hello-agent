# hello-agent

A deliberately minimal "Hello Agent's World" FastAPI app. Its purpose is to
exercise a complete git → CI → CD → deploy workflow on modest home-lab
hardware (Ubuntu 22.04 server "rusty", 1.7GB RAM), and to serve as the
sandbox for agent-driven development (Claude Code running as the `dev-agent`
user on rusty).

## Stack

- Python 3.12, FastAPI + Jinja2, served by `uvicorn`
- Plain `requirements.txt` / `requirements-dev.txt` (no Poetry/uv)
- `ruff` for linting, `pytest` for tests
- Docker, Docker Compose for deployment

## Common Commands

```bash
# Setup
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt

# Lint & test
ruff check .
pytest

# Run locally
APP_ENV=local APP_VERSION=local-dev uvicorn app.main:app --reload

# Docker
docker build -t hello-agent:local --build-arg APP_VERSION=$(git rev-parse --short HEAD) .
docker run --rm -p 8000:8000 -e APP_ENV=local hello-agent:local

# Deploy environments (on rusty, run from the relevant directory)
cd ~/deploy/hello-agent/dev   # or stage
docker compose pull
docker compose up -d
```

## Branches & Environments

- `develop` → CD deploys to **dev** (`http://192.168.10.100:8001`)
- `main` → CD deploys to **stage** (`http://192.168.10.100:8002`)
- The same image is promoted unchanged between environments; only `APP_ENV`
  differs (set in each environment's `docker-compose.yml`).

## Agent Operating Rules (dev-agent / Claude Code on rusty)

These rules apply when working as `dev-agent` on rusty, where Docker runs in
**rootless mode** for this user.

**Allowed:**
- `docker ps`, `docker logs <container>`
- `docker compose up` / `down` within this project's compose directories
  (`~/deploy/hello-agent/dev`, `~/deploy/hello-agent/stage`, or a working copy of this repo)
- `docker build` for this project's images
- `docker exec` into this project's containers for debugging

**Forbidden:**
- Mounting `/` (host root) as a volume
- Mounting `/home/szymon` (other users' home directories) as a volume
- Using `--privileged`
- Using `--network host` unless explicitly required and approved by the user
- Destructive cleanup commands such as `docker system prune -a` (may affect
  other projects' images/containers/volumes)
