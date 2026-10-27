import io
p = 'apresentacao/build.js'
s = open(p, encoding='utf-8').read()
needle = 'const path = require("path");'
assert needle in s
s = s.replace(needle, needle + '\nconst NOTES = require("./notes");', 1)

for n in list(range(2, 11)) + [12, 13, 14, 15, 16, 18, 19, 20]:
    old = f"  footer(s); page(s, {n});\n}}"
    new = f"  footer(s); page(s, {n});\n  s.addNotes(NOTES[\"{n:02d}\"]);\n}}"
    assert old in s, f"missing footer page {n}"
    s = s.replace(old, new, 1)

for n in (11, 17):
    old = f"  page(s, {n}, true);\n}}"
    new = f"  page(s, {n}, true);\n  s.addNotes(NOTES[\"{n:02d}\"]);\n}}"
    assert old in s, f"missing dark page {n}"
    s = s.replace(old, new, 1)

old = '  tx(s, "2026", 12.0, 6.72, 0.5, 0.25, {\n    face: F.mono, size: 8, color: C.muted, align: "right",\n  });\n}'
new = '  tx(s, "2026", 12.0, 6.72, 0.5, 0.25, {\n    face: F.mono, size: 8, color: C.muted, align: "right",\n  });\n  s.addNotes(NOTES["01"]);\n}'
assert old in s, "missing slide 1 end"
s = s.replace(old, new, 1)

open(p, 'w', encoding='utf-8').write(s)
print('patched notes')
