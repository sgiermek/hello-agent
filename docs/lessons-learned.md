# Lessons Learned

Notes from getting the CI/CD pipeline running end-to-end for the first time.

## 1. Secrets can be correct while the deploy still fails

The first `develop` → CD-Dev run had `build-push` and the Tailscale/SSH
connection all succeed, but `deploy` failed:

```
no configuration file provided: not found
curl: (7) Failed to connect to localhost port 8001
```

Root cause: `~/deploy/hello-agent/dev/` on rusty was empty — step 1 of
[`rusty-setup.md`](rusty-setup.md) (create `docker-compose.yml` + `.env`)
hadn't been done yet. `docker compose pull`/`up` silently no-op without a
compose file, so the container never started.

**Takeaway:** if CD fails at the `deploy` step with "no configuration file
provided", check the deploy-host directory exists and has the compose files
*before* re-checking secrets — rusty-setup.md step 1 is a hard prerequisite
for the first CD run of each environment (`dev`/`stage`).

## 2. Match the version format between local and CI builds

CD-built images reported the full 40-character commit SHA as `APP_VERSION`
(e.g. `b27615d0d15507f520a8b378e4e7fe06b8382737`), while local builds used
`git rev-parse --short HEAD` per the Quickstart in the README/CLAUDE.md.

**Fix:** each workflow (`ci.yml`, `cd-dev.yml`, `cd-stage.yml`) now has a
"Resolve short SHA" step that runs `git rev-parse --short HEAD` and uses the
result for both `APP_VERSION` and the immutable GHCR image tag — consistent
with local builds and shorter to read on the index page.
