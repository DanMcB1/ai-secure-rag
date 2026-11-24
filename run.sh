#!/usr/bin/env bash
# Start the Row-Level Secure RAG Engine locally. No API key required.
set -euo pipefail
cd "$(dirname "$0")"
if [[ ! -d .venv ]]; then
  python3 -m venv .venv
  .venv/bin/pip install -r requirements.txt
fi
exec .venv/bin/streamlit run app.py --server.headless true
