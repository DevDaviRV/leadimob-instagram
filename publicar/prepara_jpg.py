#!/usr/bin/env python3
"""Gera os JPEG dos carrosséis de um ou mais dias: instagram/AAAA-MM-DD/carrossel/jpg/slide-NN.jpg.

Uso: python3 publicar/prepara_jpg.py AAAA-MM-DD [AAAA-MM-DD ...]

O Instagram só aceita JPEG em carrossel. Este script roda na PRODUÇÃO (ou na aprovação), onde o Pillow está
instalado pelo setup.sh. A rotina de publicação não instala pacotes: ela só copia os JPEG que já estão aqui.
"""
import json, os, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def jpg_de(day, f):
    return os.path.join(day, os.path.dirname(f), "jpg", os.path.splitext(os.path.basename(f))[0] + ".jpg")

if len(sys.argv) < 2: sys.exit(__doc__)
for data in sys.argv[1:]:
    day = os.path.join(ROOT, "instagram", data)
    man = json.load(open(os.path.join(day, "posts.json"), encoding="utf-8"))
    n = 0
    for post in man["posts"]:
        if post["tipo"] != "carrossel": continue
        for f in post["arquivos"]:
            out = jpg_de(day, f); os.makedirs(os.path.dirname(out), exist_ok=True)
            im = Image.open(os.path.join(day, f)).convert("RGB")
            if im.size != (1080, 1350): print(f"AVISO {data}: {f} tem {im.size[0]}x{im.size[1]} (esperado 1080x1350)")
            im.save(out, "JPEG", quality=92, optimize=True); n += 1
    print(f"OK {data}: {n} JPEG em carrossel/jpg/")
