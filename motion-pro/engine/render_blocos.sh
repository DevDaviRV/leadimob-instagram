#!/bin/bash
# Render retomável em blocos (o ambiente de nuvem pode reiniciar no meio de um render longo).
# Uso: render_blocos.sh <url> <total_quadros> <pasta_saida> [fps=30] [sub=4] [bloco=80]  (obturador: SHUTTER=0.5 por padrão)
# Roda 2 processos em paralelo; blocos já prontos são pulados. Ao final: <pasta_saida>/raw.mp4
URL=$1; N=$2; OUT=$3; FPS=${4:-30}; SUB=${5:-4}; CH=${6:-80}
ENG="$(cd "$(dirname "$0")" && pwd)"; mkdir -p "$OUT/c"
worker(){ local i=0
  for ((s=0; s<N; s+=CH)); do e=$((s+CH)); [ $e -gt $N ] && e=$N
    if [ $((i%2)) -eq $1 ]; then f=$(printf "$OUT/c/c_%03d.mp4" $i)
      [ -f "$f" ] || { node "$ENG/render2.js" "$URL" $FPS $SUB $s $e "$OUT/c/tmp_$1.mp4" >> "$OUT/w$1.log" 2>&1 && mv "$OUT/c/tmp_$1.mp4" "$f"; }
    fi; i=$((i+1)); done; }
worker 0 & worker 1 & wait
ls "$OUT"/c/c_*.mp4 | sed "s#^.*/c/#file c/#" > "$OUT/l.txt"
ffmpeg -v error -y -f concat -i "$OUT/l.txt" -c copy "$OUT/raw.mp4" && echo "DONE $OUT/raw.mp4"
