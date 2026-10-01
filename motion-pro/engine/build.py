s=open('index.html').read().replace('__TIMELINE__',open('timeline.json').read())
open('build.html','w').write(s)
