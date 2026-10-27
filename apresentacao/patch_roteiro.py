p = 'apresentacao/make_roteiro.py'
s = open(p, encoding='utf-8').read()
s = s.replace('for tag, val in (("top", top), ("bottom", bottom), ("start", left), ("end", right)):', 'for tag, val in (("top", top), ("bottom", bottom), ("left", left), ("right", right)):')
s = s.replace('    para(doc, "Página 1 de 4", size=8, color=MUTED, font="Consolas", align=WD_ALIGN_PARAGRAPH.RIGHT, space_before=6)\n\n', '')
s = s.replace('"No Arduino, o treinamento é online e mais lento, porque cada ação tem um delay de 100 ms. O tempo de parede depende da pista e do hardware."', '"No Arduino, o treinamento é online e mais lento, porque cada ação tem um delay de 100 ms. O tempo real depende da pista e do hardware."')
s = s.replace('    table = doc.add_table(rows=1, cols=3)\n    table.alignment = WD_TABLE_ALIGNMENT.CENTER\n', '    table = doc.add_table(rows=1, cols=3)\n    table.alignment = WD_TABLE_ALIGNMENT.CENTER\n    table.autofit = False\n')
open(p, 'w', encoding='utf-8').write(s)
print('patched')
