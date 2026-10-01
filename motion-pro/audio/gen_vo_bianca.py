"""Narração Bianca (ElevenLabs) com as configs aprovadas pelo Davi.
Uso: python3 gen_vo_bianca.py texto.txt saida.mp3
Autenticação, em ordem: (1) variável ELEVEN_LABS_API_KEY, se existir; (2) sem variável, a requisição sai sem chave e a
"API credential" do ambiente de nuvem (cabeçalho xi-api-key para api.elevenlabs.io) é anexada pelo proxy. Nunca imprime a chave.
Se responder 401, nenhuma das duas está configurada. Requer conta paga (conta free não usa vozes da biblioteca pela API)."""
import os, sys, json, urllib.request
KEY = os.environ.get('ELEVEN_LABS_API_KEY', '').strip()
H = {"xi-api-key": KEY} if KEY else {}
text = open(sys.argv[1], encoding='utf-8').read().strip()
payload = {"text": text, "model_id": "eleven_multilingual_v2",
           "voice_settings": {"stability": 0.5, "similarity_boost": 0.75, "style": 0.0, "use_speaker_boost": True, "speed": 1.0}}
req = urllib.request.Request("https://api.elevenlabs.io/v1/text-to-speech/9LwXyqQB0mUwtLRsS227?output_format=mp3_44100_128",
    data=json.dumps(payload).encode(), headers={**H, "Content-Type": "application/json", "Accept": "audio/mpeg"}, method="POST")
try:
    with urllib.request.urlopen(req) as r: data = r.read()
except urllib.error.HTTPError as e:
    sys.exit("ERRO HTTP %s: %s" % (e.code, e.read().decode('utf-8','ignore')[:300]))
open(sys.argv[2], 'wb').write(data)
d = json.load(urllib.request.urlopen(urllib.request.Request("https://api.elevenlabs.io/v1/user/subscription", headers=H)))
print("OK", sys.argv[2], len(data), "bytes | creditos:", d.get('character_count'), "/", d.get('character_limit'))
