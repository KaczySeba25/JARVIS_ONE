#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"
python3 -m pip install --upgrade pip >/dev/null 2>&1 || true
python3 scripts/bootstrap_agent.py
if ! grep -q '^AUTO_APPROVE=' .env 2>/dev/null; then
  echo "AUTO_APPROVE=true" >> .env
fi
if ! grep -q '^AUTO_RUN_BROWSER=' .env 2>/dev/null; then
  echo "AUTO_RUN_BROWSER=true" >> .env
fi
if ! grep -q '^PLAYWRIGHT_INSTALL=' .env 2>/dev/null; then
  echo "PLAYWRIGHT_INSTALL=true" >> .env
fi
python3 scripts/bootstrap_agent.py
python3 -m playwright install >/dev/null 2>&1 || true
python3 agent.py
