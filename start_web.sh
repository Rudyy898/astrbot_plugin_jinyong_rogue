#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"
python3 web/server.py --host 127.0.0.1 --port 8790
