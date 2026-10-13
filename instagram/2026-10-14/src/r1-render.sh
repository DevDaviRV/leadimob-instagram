#!/bin/bash
# blocos retomáveis com subquadros por trecho (12 nas viradas rápidas, 4 no resto)
URL=http://localhost:8126/work/r1-1410/build.html; OUT=out; mkdir -p $OUT/c
ENG=../../motion-pro/engine
SEGS="0:80:4 80:160:4 160:258:4 258:293:12 293:373:4 373:453:4 453:538:4 538:570:12 570:650:4 650:730:4 730:810:4 810:890:4 890:990:4 990:1022:12 1022:1110:4 1110:1198:4"
worker(){ local i=0; for sg in $SEGS; do IFS=: read a b s <<< "$sg"
  if [ $((i%2)) -eq $1 ]; then f=$(printf "$OUT/c/c_%03d.mp4" $i); [ -f "$f" ] || { node $ENG/render2.js $URL 30 $s $a $b $OUT/c/tmp_$1.mp4 >> $OUT/w$1.log 2>&1 && mv $OUT/c/tmp_$1.mp4 "$f"; }; fi; i=$((i+1)); done; }
worker 0 & worker 1 & wait
ls $OUT/c/c_*.mp4 | sed "s#^$OUT/#file #" > $OUT/l.txt
ffmpeg -v error -y -f concat -i $OUT/l.txt -c copy $OUT/raw.mp4 && echo "DONE $OUT/raw.mp4"
