import re
p = 'apresentacao/make_conceptual.py'
s = open(p, encoding='utf-8').read()
s = s.replace('    ax.plot([21, 21], [0.02, 1.88], color=INK, lw=1.0, ls=(0, (3, 3)), alpha=0.7)\n', '')
open(p, 'w', encoding='utf-8').write(s)
print('patched')
