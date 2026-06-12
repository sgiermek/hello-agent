---
name: hello-agent-review
description: Review changes to hello-agent for correctness and project-specific conventions - ruff/pytest, CI/CD short-SHA versioning across all three workflows, the develop->dev / main->stage branch-environment mapping, APP_ENV/APP_VERSION split, Docker Agent Operating Rules (CLAUDE.md) for rusty, secrets handling, and deploy-host (docker/compose vs ~/deploy/hello-agent) consistency. Use when asked to review, check, or audit a diff/PR in this repo, or as reference alongside /code-review and /security-review.
---

# hello-agent code review

## Current changes

```!
git status --short
git diff HEAD
```

## Review checklist

### Code quality
- `ruff check .` must pass (rules E, F, I, UP; line-length 100; target py312 - see `pyproject.toml`).
- `pytest` must pass; new behavior needs tests under `tests/`.
- `app/config.py`: `APP_VERSION` is baked into the image at build time (immutable per image); `APP_ENV` is set per-environment at runtime via compose. Don't conflate the two.

### CI/CD workflows (`.github/workflows/`)
- `ci.yml`, `cd-dev.yml`, and `cd-stage.yml` each resolve `sha_short` via `git rev-parse --short HEAD` and use it for both the `APP_VERSION` build-arg and the immutable GHCR image tag. If one workflow's tagging/version logic changes, the other two should match.
- Branch -> environment mapping is fixed: `develop` -> dev (port 8001), `main` -> stage (port 8002). Changing this requires updating `docs/architecture.md` and `docs/deployment.md`.
- Secrets must only be referenced via `${{ secrets.NAME }}` - never inlined or hardcoded.

### Docker / deploy
- `Dockerfile` must keep the non-root `appuser` and stay a single small image.
- `docker/compose/{dev,stage}/docker-compose.yml` mirror what must exist on the deploy host at `~/deploy/hello-agent/{dev,stage}/` (see `docs/lessons-learned.md` #1). If these change, the host-side copies need a matching manual update - they are not synced by CI/CD.
- `.env` files for the compose stacks are gitignored; only `.env.example` is committed.

### Agent Operating Rules (rusty / dev-agent)
- For anything touching Docker commands, compose files, or CI deploy steps, cross-check against `CLAUDE.md`'s allow/forbid list:
  - Forbidden: mounting `/` or `/home/szymon`, `--privileged`, `--network host` (without explicit approval), `docker system prune -a`.

### Secrets & sensitive data
- No `.env` files, private keys, tokens, or credentials in the diff.
- Any new local/secret config files are covered by `.gitignore`.

### Docs consistency
- If versioning, image tagging, ports, env vars, or branch->environment mapping change, update the relevant doc: `README.md`, `docs/architecture.md`, `docs/deployment.md`, `docs/rusty-setup.md`.

## Instructions

1. Read the diff above (and any files it references) to understand the change.
2. If Python files changed, run `ruff check .` and `pytest`.
3. Walk through the checklist above, skipping items that don't apply to this diff.
4. Report findings grouped by checklist area, citing `file:line` for each one. If nothing applies, say so briefly.
