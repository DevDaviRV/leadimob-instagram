#!/usr/bin/env bash
# Abre uma pasta de trabalho a partir de um MODELO APROVADO (ver motion-pro/MODELOS.md), já com fontes,
# three, motion, logo e demais ativos no lugar, para a página abrir igual à peça aprovada.
# uso: motion-pro/novo_trabalho.sh <modelo> <nome>
#   modelos: reel-tipografico | reel-narrado | carrossel | carrossel-b
# cria work/<nome>/ (fora do git). Sirva a raiz do repositório por HTTP e abra http://localhost:8126/work/<nome>/index.html
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; M="$1"; N="$2"
[ -n "$M" ] && [ -n "$N" ] || { sed -n 2,6p "$0"; exit 1; }
W="$ROOT/work/$N"; mkdir -p "$W"
case "$M" in
  reel-tipografico) S="$ROOT/instagram/2026-10-03/src"; cp "$S/r2-index.html" "$W/index.html"; cp "$S/r2-trilha.py" "$W/trilha.py";;
  reel-narrado)     S="$ROOT/motion-pro/v1-plataforma"; cp "$S/index.html" "$S/script.py" "$S/gaps.json" "$S/timeline.json" "$S/trilha.py" "$W/";;
  carrossel)        S="$ROOT/instagram/2026-10-02/src"; cp "$S/c1-index.html" "$W/index.html"; cp "$ROOT/instagram/2026-10-03/src/c1-shoot.js" "$W/shoot.js";;
  carrossel-b)      S="$ROOT/instagram/2026-10-03/src"; cp "$S/c1-index.html" "$W/index.html"; cp "$S/c1-shoot.js" "$W/shoot.js"; cp "$S/c1-slides.json" "$W/slides.json";;
  *) echo "modelo desconhecido: $M"; exit 1;;
esac
[ -d "$ROOT/node_modules" ] || { echo "rode ./setup.sh antes"; exit 1; }
ln -sfn "$ROOT/node_modules" "$W/node_modules"
for a in logo.png lid.png property.jpg; do ln -sfn "$ROOT/motion-pro/assets/$a" "$W/$a"; done
echo "ok: $W (modelo $M)"
