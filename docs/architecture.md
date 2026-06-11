# Architecture

## App structure

```
app/
├── main.py        # FastAPI app, routes
├── config.py      # reads APP_ENV / APP_VERSION from environment variables
├── templates/     # Jinja2 templates (index.html)
└── static/        # CSS
```

Two endpoints:

- `GET /` — HTML page: greeting, current environment, running version
- `GET /health` — JSON health check: `{"status": "ok", "env": ..., "version": ...}`,
  used by the Docker healthcheck and the CD smoke test

## Configuration

Two environment variables control the app's identity:

- `APP_VERSION` — baked into the Docker image at build time
  (`--build-arg APP_VERSION=<git sha>`). The same image, once built, always
  reports the same version regardless of where it runs.
- `APP_ENV` — **not** baked into the image. It's set per-environment in each
  environment's `docker-compose.yml` (`dev` or `stage`), so a single
  immutable image can be promoted from dev to stage unchanged.

The index page uses `APP_ENV` to pick an accent color (dev = blue,
stage = orange) as a quick visual indicator of which environment you're
looking at.

## Why two environments (dev + stage)?

For a FastAPI + uvicorn container this big, each instance idles at roughly
50-80MB of RAM. Running both `dev` and `stage` simultaneously on rusty
(1.7GB total RAM) costs well under 200MB combined — negligible headroom cost.

In exchange, it gives:

- A realistic **branch → environment promotion** flow
  (`develop` → dev, `main` → stage), which is the actual point of this
  project (practicing the workflow, not the app).
- A safe place (`dev`) for an agent (or yourself) to break things while
  iterating, with `stage` remaining a stable, "promoted" reference.

## Image tagging

Every CD run pushes two tags to GHCR:

- `ghcr.io/sgiermek/hello-agent:<git-sha>` — immutable, used for rollback
- `ghcr.io/sgiermek/hello-agent:dev-latest` or `:stage-latest` — floating tag
  that each environment's `docker-compose.yml` tracks via `IMAGE_TAG`
