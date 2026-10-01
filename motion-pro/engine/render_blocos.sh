#!/bin/bash
# resumable chunked render: worker.sh <parity> ; chunks of 80 frames
cd /home/claude/ig/r1
N=$(cat out/N.txt); CH=80; i=0
for ((s=0; s<N; s+=CH)); do
  e=$((s+CH)); [ $e -gt $N ] && e=$N
  if [ $((i%2)) -eq $1 ]; then
    f=$(printf "out/c/c_%03d.mp4" $i)
    if [ ! -f "$f" ]; then node engine/render2.js http://localhost:8126/r1/build.html 30 3 $s $e out/c/tmp_$1.mp4 >> out/w$1.log 2>&1 && mv out/c/tmp_$1.mp4 "$f"; fi
  fi
  i=$((i+1))
done
echo DONE >> out/w$1.log
