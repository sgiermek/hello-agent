#!/usr/bin/env bash
# Usage: ./scripts/smoke_test.sh <port>
set -euo pipefail

PORT="${1:?Usage: $0 <port>}"

curl -f "http://localhost:${PORT}/health"
echo
