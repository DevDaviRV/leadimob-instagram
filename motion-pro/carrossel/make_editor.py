#!/usr/bin/env python3
"""Gera o carrossel-editor.html (Carousel Studio) sem depender da skill instalada.
Usa como molde o editor de um carrossel já entregue neste repositório e troca só os dados (bloco deck-data).
uso: python3 motion-pro/carrossel/make_editor.py slides.json saida/carrossel-editor.html [molde.html]
O slides.json segue o formato do editor (ver instagram/2026-10-03/src/c1-slides.json)."""
import json, re, sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
slides, out = sys.argv[1], sys.argv[2]
molde = sys.argv[3] if len(sys.argv) > 3 else os.path.join(ROOT, "instagram/2026-10-03/carrossel/carrossel-editor.html")
data = json.load(open(slides, encoding="utf-8"))
assert data.get("slides"), "slides.json sem 'slides'"
tpl = open(molde, encoding="utf-8").read()
pat = re.compile(r'(<script id="deck-data" type="application/json">)(.*?)(</script>)', re.S)
assert pat.search(tpl), "molde sem bloco deck-data"
payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
html = pat.sub(lambda m: m.group(1) + payload + m.group(3), tpl, count=1)
os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
open(out, "w", encoding="utf-8").write(html)
print(f"ok: {out} ({len(data['slides'])} slides)")
