#!/usr/bin/env python3
"""Publica um post do dia no Instagram (@leadimob.ai) pela API oficial (Instagram Login).

Uso: python3 publicar/publish.py --data AAAA-MM-DD --slot 09:00 --midia /caminho/do/repo-publico [--dry]

- Lê instagram/AAAA-MM-DD/posts.json (manifesto do dia) e publica o post do horário pedido.
- Copia a mídia para o repositório público de criativos (JPEG para carrossel, MP4 para reel), faz push e usa o link aberto.
  Só usa a biblioteca padrão do Python: os JPEG do carrossel vêm prontos de carrossel/jpg/ (publicar/prepara_jpg.py, na produção).
  Rode este comando sozinho, sem encadear instalação de pacotes.
- Autenticação: sem cabeçalho (a credencial do ambiente de nuvem é anexada pelo proxy em graph.instagram.com) ou variável IG_TOKEN.
  Nunca imprime o token.
- Idempotente: grava instagram/AAAA-MM-DD/PUBLICADO.json e não publica duas vezes o mesmo horário.
- Aprovação: se rotinas/config.json tiver "aprovacao": "manual", só publica se existir instagram/AAAA-MM-DD/APROVADO.
"""
import argparse, json, os, subprocess, sys, time, urllib.parse, urllib.request, urllib.error, shutil

API = "https://graph.instagram.com/v24.0"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = json.load(open(os.path.join(ROOT, "rotinas", "config.json")))
TOKEN = os.environ.get("IG_TOKEN", "").strip()

def api(method, path, params=None, soft=False):
    params = dict(params or {})
    url = f"{API}/{path}"
    data = None
    if method == "GET":
        if params: url += "?" + urllib.parse.urlencode(params)
    else:
        data = urllib.parse.urlencode(params).encode()
    req = urllib.request.Request(url, data=data, method=method)
    if TOKEN: req.add_header("Authorization", "Bearer " + TOKEN)
    try:
        with urllib.request.urlopen(req, timeout=120) as r: return json.load(r)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "ignore")[:600]
        if soft: return {"_erro": f"HTTP {e.code} {body}"}
        sys.exit(f"ERRO API {method} {path}: HTTP {e.code} {body}")

def sh(cmd, cwd):
    return subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()

def reachable(url, tries=40):
    """True quando o link aberto responde 200. 404 = ainda propagando (tenta de novo).
    Se a rede do ambiente bloquear o host, segue em frente: quem baixa a mídia é o Instagram."""
    bloqueios = 0
    for _ in range(tries):
        try:
            req = urllib.request.Request(url, method="HEAD")
            with urllib.request.urlopen(req, timeout=30) as r:
                if r.status == 200: return True
        except urllib.error.HTTPError as e:
            if e.code not in (404, 429, 500, 502, 503): bloqueios += 1
        except Exception:
            bloqueios += 1
        if bloqueios >= 3:
            print(f"AVISO: não consegui conferir {url} daqui (rede do ambiente); seguindo."); time.sleep(20); return True
        time.sleep(6)
    return False

def wait_container(cid, what):
    for _ in range(90):
        st = api("GET", cid, {"fields": "status_code,status"})
        code = st.get("status_code")
        if code == "FINISHED": return
        if code in ("ERROR", "EXPIRED"): sys.exit(f"ERRO: contêiner de {what} falhou: {st}")
        time.sleep(8)
    sys.exit(f"ERRO: contêiner de {what} não ficou pronto a tempo")

def copia_midia(day, post, dest, base, data):
    """Copia a mídia do post para a pasta do repositório público e devolve os links.
    Reel: o MP4. Carrossel: os JPEG já gerados na produção em carrossel/jpg/ (publicar/prepara_jpg.py).
    Esta rotina não instala nada: sem o JPEG pronto, só converte se o Pillow já estiver instalado."""
    if post["tipo"] == "reel":
        name = os.path.basename(post["arquivo"]); shutil.copyfile(os.path.join(day, post["arquivo"]), os.path.join(dest, name))
        return [f"{base}/{name}"]
    prontos = [os.path.join(day, os.path.dirname(f), "jpg", os.path.splitext(os.path.basename(f))[0] + ".jpg") for f in post["arquivos"]]
    faltam = [p for p in prontos if not os.path.exists(p)]
    Image = None
    if faltam:
        try:
            from PIL import Image
        except ImportError:
            sys.exit(f"ERRO: falta o JPEG pré-gerado ({os.path.relpath(faltam[0], ROOT)} e mais {len(faltam) - 1}) e o Pillow não está instalado. "
                     f"Gere na produção com: python3 publicar/prepara_jpg.py {data}")
    urls = []
    for i, (f, pronto) in enumerate(zip(post["arquivos"], prontos), 1):
        name = f"slide-{i:02d}.jpg"
        if os.path.exists(pronto): shutil.copyfile(pronto, os.path.join(dest, name))
        else: Image.open(os.path.join(day, f)).convert("RGB").save(os.path.join(dest, name), "JPEG", quality=92, optimize=True)
        urls.append(f"{base}/{name}")
    return urls

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True); ap.add_argument("--slot", required=True)
    ap.add_argument("--midia", required=True, help="pasta do clone do repositório público de criativos")
    ap.add_argument("--dry", action="store_true", help="prepara e sobe a mídia, cria os contêineres, mas NÃO publica")
    ap.add_argument("--teste", action="store_true", help="publica agora ignorando aprovação e registro (post de teste; não grava PUBLICADO.json)")
    a = ap.parse_args()
    day = os.path.join(ROOT, "instagram", a.data)
    man = json.load(open(os.path.join(day, "posts.json")))
    post = next((p for p in man["posts"] if p["horario"] == a.slot), None)
    if not post: sys.exit(f"Sem post para {a.slot} em {a.data}")
    pub_path = os.path.join(day, "PUBLICADO.json")
    pub = json.load(open(pub_path)) if os.path.exists(pub_path) else {}
    if a.slot in pub and not a.dry and not a.teste:
        print(f"JA_PUBLICADO {a.data} {a.slot}: {pub[a.slot].get('permalink')}"); return
    if CFG.get("aprovacao") == "manual" and not os.path.exists(os.path.join(day, "APROVADO")) and not a.dry and not a.teste:
        print(f"AGUARDANDO_APROVACAO {a.data}: crie instagram/{a.data}/APROVADO para liberar"); return

    # 1) mídia no repositório público
    dest = os.path.join(a.midia, a.data); os.makedirs(dest, exist_ok=True)
    base = CFG["midia_base_url"].rstrip("/") + "/" + a.data
    urls = copia_midia(day, post, dest, base, a.data)
    sh(["git", "add", "-A"], a.midia)
    if sh(["git", "status", "--porcelain"], a.midia):
        sh(["git", "commit", "-q", "-m", f"Midia {a.data} {a.slot}"], a.midia); sh(["git", "push", "-q", "origin", "HEAD:main"], a.midia)
    for u in urls:
        if not reachable(u): sys.exit(f"ERRO: link público não respondeu: {u}")

    # 2) contêineres
    cap = post["legenda"]
    if post["tipo"] == "reel":
        params = {"media_type": "REELS", "video_url": urls[0], "caption": cap, "share_to_feed": "true"}
        if post.get("capa_s") is not None: params["thumb_offset"] = int(float(post["capa_s"]) * 1000)
        res = api("POST", "me/media", params, soft=True)
        if "_erro" in res and "thumb_offset" in params:
            print("AVISO: capa por tempo recusada, publicando com a capa padrão:", res["_erro"][:160]); params.pop("thumb_offset"); res = api("POST", "me/media", params)
        elif "_erro" in res: sys.exit("ERRO API POST me/media: " + res["_erro"])
        cid = res["id"]; wait_container(cid, "reel")
    else:
        kids = []
        for u in urls:
            k = api("POST", "me/media", {"image_url": u, "is_carousel_item": "true"})["id"]; wait_container(k, "slide"); kids.append(k)
        cid = api("POST", "me/media", {"media_type": "CAROUSEL", "children": ",".join(kids), "caption": cap})["id"]; wait_container(cid, "carrossel")
    if a.dry:
        print(f"DRY_OK {a.data} {a.slot}: contêiner {cid} pronto, nada publicado"); return

    # 3) publicar
    mid = api("POST", "me/media_publish", {"creation_id": cid})["id"]
    info = api("GET", mid, {"fields": "permalink,media_type,timestamp"})
    if a.teste:
        print(f"TESTE_PUBLICADO {a.data} {a.slot}: {info.get('permalink')} (media_id {mid}; não registrado)"); return
    pub[a.slot] = {"media_id": mid, "permalink": info.get("permalink"), "publicado_em": info.get("timestamp"), "tipo": post["tipo"]}
    json.dump(pub, open(pub_path, "w"), ensure_ascii=False, indent=1)
    print(f"PUBLICADO {a.data} {a.slot}: {info.get('permalink')}")

if __name__ == "__main__":
    main()
