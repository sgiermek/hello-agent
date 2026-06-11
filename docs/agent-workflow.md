# Agent Workflow (future work)

> **Status: not implemented yet.** This document is a placeholder for the
> final phase of this project.

## Goal

Once the dev/stage CI/CD pipeline is working end-to-end, the next step is to
use **Claude Code**, running as the `dev-agent` user on rusty and controlled
from the **Claude mobile app**, to extend `hello-agent` itself — making
changes, committing, and letting the existing CI/CD pipeline deploy them.

## Prerequisites (expected to already be satisfied by this point)

- [x] `dev-agent` has rootless Docker (build/run/compose for this project)
- [x] `dev-agent` has SSH access set up for CD
- [ ] `hello-agent` repo cloned on rusty under `dev-agent`'s home directory
- [ ] CI/CD pipeline verified green for both `develop` and `main`

## Remaining setup (future session)

1. Install Claude Code CLI for `dev-agent` on rusty.
2. Authenticate Claude Code (Anthropic account / API access).
3. Pair the Claude mobile app with the Claude Code session on rusty
   (remote/SSH-backed session).
4. Give the agent a small, well-scoped first task (e.g., add an endpoint or
   tweak the index page), working on a feature branch off `develop`.

## Operating rules

The agent must follow the rules in [`CLAUDE.md`](../CLAUDE.md) — particularly
the Docker allow/forbid list, which exists specifically to keep an
autonomous agent's Docker usage scoped to this project and away from the
host system or other users' data.
