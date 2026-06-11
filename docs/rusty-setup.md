# rusty Setup Runbook

One-time setup of the deploy server ("rusty", Ubuntu Server 22.04, 1.7GB RAM)
for the `hello-agent` dev/stage environments. Run the commands below and
report back the output where noted.

## 0. Prerequisites (already done)

- [x] Docker installed
- [x] Tailscale installed
- [x] User `dev-agent` exists with **rootless Docker** configured

Verify rootless Docker still works as `dev-agent`:

```bash
docker run --rm hello-world
docker compose version
```

Both should succeed without `sudo`.

## 1. Deploy directories

As `dev-agent`:

```bash
mkdir -p ~/deploy/hello-agent/dev ~/deploy/hello-agent/stage
```

### dev

Create `~/deploy/hello-agent/dev/docker-compose.yml`:

```yaml
services:
  hello-agent:
    image: ghcr.io/sgiermek/hello-agent:${IMAGE_TAG:-dev-latest}
    restart: unless-stopped
    ports:
      - "8001:8000"
    environment:
      APP_ENV: dev
    mem_limit: 128m
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')"]
      interval: 30s
      timeout: 3s
      retries: 3
      start_period: 5s
```

Create `~/deploy/hello-agent/dev/.env`:

```
IMAGE_TAG=dev-latest
```

### stage

Create `~/deploy/hello-agent/stage/docker-compose.yml` — identical, but:
- `ports: ["8002:8000"]`
- `APP_ENV: stage`
- `image: ghcr.io/sgiermek/hello-agent:${IMAGE_TAG:-stage-latest}`

Create `~/deploy/hello-agent/stage/.env`:

```
IMAGE_TAG=stage-latest
```

(These files are also kept in the repo under `docker/compose/{dev,stage}/`
for reference — copy them over, e.g. via `scp` from your Mac, instead of
retyping.)

## 2. SSH key-based auth for CD

On your Mac, generate a dedicated deploy keypair:

```bash
ssh-keygen -t ed25519 -C "github-actions-hello-agent" -f ~/.ssh/hello_agent_deploy -N ""
```

On rusty, confirm `dev-agent` has a real login shell (required for
`appleboy/ssh-action` to run commands):

```bash
getent passwd dev-agent
```

If the shell is `/usr/sbin/nologin`, fix it (as a sudo-capable user):

```bash
sudo chsh -s /bin/bash dev-agent
```

As `dev-agent`, add the **public** key (`~/.ssh/hello_agent_deploy.pub` from
your Mac) to `authorized_keys`:

```bash
mkdir -p ~/.ssh && chmod 700 ~/.ssh
echo "<contents of hello_agent_deploy.pub>" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

The **private** key (`cat ~/.ssh/hello_agent_deploy` on your Mac) goes into
the GitHub repository secret `DEPLOY_SSH_KEY` (see
[`deployment.md`](deployment.md)).

## 3. Tailscale

Check current status:

```bash
tailscale status
```

If rusty isn't joined yet (as a sudo-capable user):

```bash
sudo tailscale up --ssh --hostname=rusty
```

Follow the printed URL to authenticate. Then get the Tailscale IP — this is
the value for the `DEPLOY_HOST` secret:

```bash
tailscale ip -4
```

If your tailnet uses custom ACLs (Tailscale admin console → Access
Controls), make sure:
- a `tag:ci` entry exists under `tagOwners`
- `tag:ci` is allowed to reach rusty on port 22

Default (allow-all) ACLs need no changes.

## 4. GHCR pull check

After the first CI/CD run has pushed an image, verify rusty can pull it
without authentication (the GHCR package should be public for a public
repo — see [`deployment.md`](deployment.md)):

```bash
docker pull ghcr.io/sgiermek/hello-agent:dev-latest
```

If this fails with an authentication error, flip the package's visibility to
Public on GitHub (your profile → Packages → hello-agent → Package settings).

## Done

Once steps 1-3 are complete, report back:
- The Tailscale IP from step 3 (→ `DEPLOY_HOST` secret)
- Confirmation that the SSH key was added and `dev-agent` has a login shell
