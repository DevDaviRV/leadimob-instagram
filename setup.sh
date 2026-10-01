#!/usr/bin/env bash
# Prepara um ambiente novo (efêmero) para produzir: deps de render e áudio.
set -e
cd "$(dirname "$0")"
PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 npm i --silent
pip install --break-system-packages -q numpy scipy pillow 2>/dev/null || true
echo "ok — Chromium em /opt/pw-browsers/chromium; sirva a pasta por HTTP: python3 -m http.server 8126"
