# -*- coding: utf-8 -*-
"""Gera o roteiro da apresentacao em Markdown e DOCX."""
import os
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)

PAPER = RGBColor(0xF4, 0xF1, 0xEA)
INK = RGBColor(0x17, 0x15, 0x12)
MUTED = RGBColor(0x6E, 0x69, 0x60)
TERRA = RGBColor(0xC2, 0x4E, 0x2E)
RULE = RGBColor(0xD9, 0xD2, 0xC5)

TITLE = "Roteiro — Como um robô aprende?"
SUB = "Feira de Ciências 2026 · versão principal de 7 minutos"
INTRO = (
    "Este roteiro acompanha o deck “Como um robô aprende?”. A fala foi escrita para ser dita, "
    "não lida: frases curtas, uma ideia por slide e pausas para olhar o robô. Os tempos são uma "
    "referência; se o público estiver envolvido, deixe a conversa correr e corte o que for menos "
    "importante. Os slides 14–16 e o apêndice ficam para perguntas."
)

TIMING = [
    ("01", "0:00–0:25", "Capa e gancho: “ele aprendeu sozinho”"),
    ("02", "0:25–1:00", "O desafio: 3 sensores, 3 ações, 10 decisões/s"),
    ("03", "1:00–1:35", "Duas abordagens: regras prontas × aprender fazendo"),
    ("04", "1:35–2:10", "A recompensa: +1, −0,5, −3"),
    ("05", "2:10–2:40", "Os 8 estados: 2³"),
    ("06", "2:40–3:30", "A Q-table: 8 × 3 = 24 notas"),
    ("07", "3:30–3:55", "A evolução: a tabela ganhando preferência"),
    ("08", "3:55–4:20", "O ciclo: sensar, escolher, agir, medir"),
    ("09", "4:20–4:50", "Explorar × confiar: ε de 1,00 a 0,13"),
    ("10", "4:50–5:20", "O treinamento: 200 episódios"),
    ("11", "5:20–5:50", "O resultado: −49 → +559"),
    ("12", "5:50–6:15", "O comportamento: 5 → 120 passos"),
    ("13", "6:15–6:35", "A curva não é lisa"),
    ("17", "6:35–7:00", "Fechamento e demo ao vivo"),
]

MAIN = [
    dict(
        n="01", title="Capa", time="0:00–0:25", key="A pergunta",
        speech=[
            "Olá! Este é um robô seguidor de linha. A diferença é que ele não foi programado com todas as regras: ele aprendeu sozinho a seguir a linha.",
            "A pergunta que guia o projeto é simples: como uma máquina aprende? Em sete minutos, eu vou mostrar o caminho. E o robô está aqui do lado, então no final vocês podem vê-lo rodando.",
        ],
        action="Aponte para o robô na mesa. Deixe a pista visível, mas ainda sem ligar o robô.",
    ),
    dict(
        n="02", title="O desafio", time="0:25–1:00", key="Decidir sem parar",
        speech=[
            "Para a gente, seguir uma linha é quase automático. Olhamos, corrigimos o corpo e seguimos. Para uma máquina, cada instante é uma decisão.",
            "Ele tem três sensores embaixo, dois motores e um Arduino. Dez vezes por segundo, ele precisa responder: para onde eu vou agora? Esquerda, reto ou direita? E ele não vê a linha: só sabe se cada sensor está no branco ou no preto.",
        ],
        action="Aponte para os três sensores e para as rodas. Mostre o robô parado sobre a linha.",
    ),
    dict(
        n="03", title="Duas abordagens", time="1:00–1:35", key="Repetir × adaptar",
        speech=[
            "Existem dois jeitos de resolver isso. No primeiro, o programador escreve todas as regras: se o sensor da esquerda vê preto e o da direita não, vire à esquerda. Funciona muito bem... até a pista mudar.",
            "No segundo, o robô testa, recebe uma nota e ajusta o próprio comportamento. É aprendizado por reforço. O primeiro repete; o segundo se adapta. É esse segundo que a gente vai destrinchar.",
        ],
        action="Gesto para a coluna da esquerda e depois para a da direita.",
    ),
    dict(
        n="04", title="A recompensa", time="1:35–2:10", key="O professor é um número",
        speech=[
            "O professor do robô não é uma pessoa: é a recompensa. Depois de cada ação, ele recebe uma nota. Se o sensor central está na linha, ganha +1. Se um sensor lateral está ativo, perde 0,5. Se perdeu a linha completamente, perde 3.",
            "As notas se somam. É como treinar um cachorro com petiscos — só que o petisco aqui é um número. Ele não sabe o que é “certo”; ele aprende o que dá nota melhor.",
        ],
        action="Aponte para os três números. Se houver visitantes, pergunte: “qual dessas notas vocês querem ganhar?”",
    ),
    dict(
        n="05", title="Os 8 estados", time="2:10–2:40", key="O mundo em 3 bits",
        speech=[
            "Para decidir, ele precisa resumir o mundo. Cada sensor só responde 0 ou 1: branco ou preto. Três sensores binários dão 2³, ou seja, 8 combinações.",
            "Por exemplo: 010 quer dizer esquerda branco, centro preto, direita branco. Isso é o estado “centralizado”. Toda a percepção do robô cabe em oito códigos. É uma simplificação — e é isso que torna o problema tratável.",
        ],
        action="Aponte para a linha 010 destacada e para os três pontos.",
    ),
    dict(
        n="06", title="A Q-table", time="2:40–3:30", key="O coração do projeto",
        speech=[
            "Agora o coração do projeto: a Q-table. Ela tem oito linhas, uma para cada situação, e três colunas, uma para cada ação. Cada célula guarda uma nota: quanto vale aquela ação naquela situação.",
            "Olha a linha 010, a situação centralizada: +7,7 para esquerda, +9,0 para reto, +8,3 para direita. A maior nota é 9,0, então ele escolhe reto. A célula terracota mostra a melhor ação de cada linha.",
            "São 24 números. É só isso que ele precisa guardar. E repare na linha 000: todas as notas são negativas porque ele perdeu a linha. Ele ainda escolhe a menos ruim, mas aprende a evitar chegar ali.",
        ],
        action="Passe o dedo na linha 010; depois aponte para a coluna RETO e para a célula terracota. Faça uma pausa de 2 segundos antes de dizer “24 números”.",
    ),
    dict(
        n="07", title="A evolução da tabela", time="3:30–3:55", key="Acumulação, não salto",
        speech=[
            "E de onde vêm esses números? Do treinamento. No começo, a tabela está toda zerada. A cada episódio, ele erra, recebe a nota e atualiza uma célula.",
            "Aqui estão quatro momentos: episódio 10, 50, 100 e 200. No começo, quase tudo neutro; no fim, cada linha já tem uma preferência clara. Não é um salto: é acumulação. Cada erro muda um pouquinho.",
        ],
        action="Aponte para os quatro quadros, da esquerda para a direita.",
    ),
    dict(
        n="08", title="O ciclo", time="3:55–4:20", key="O loop que cabe no Arduino",
        speech=[
            "O ciclo é sempre o mesmo: sensar, escolher, agir, medir. Ele lê os três sensores, consulta a linha da tabela, aciona os motores e recebe a recompensa. Dez vezes por segundo.",
            "A cada volta, uma única célula da tabela é atualizada. É um loop muito simples — e é isso que cabe dentro de um Arduino.",
        ],
        action="Faça um círculo no ar acompanhando as setas.",
    ),
    dict(
        n="09", title="Explorar × confiar", time="4:20–4:50", key="Curiosidade que cai",
        speech=[
            "Existe um dilema: ele pode repetir o que já sabe ou arriscar algo novo. No começo, ele chuta quase tudo: a exploração é 1,00, 100%. A cada episódio, essa curiosidade cai.",
            "Depois de 200 episódios, está em 0,13: 13% de exploração, 87% de confiança no que aprendeu. O mínimo no código é 2%. Se só chutar, nunca aprende; se só repetir, nunca descobre algo melhor.",
        ],
        action="Aponte para a curva e depois para os dois números.",
    ),
    dict(
        n="10", title="O treinamento", time="4:50–5:20", key="Errar é barato",
        speech=[
            "O treinamento acontece no simulador: 200 episódios, até 1.000 passos cada. Cada episódio começa em um ponto diferente da pista. Se ele fica 15 passos fora da linha, o episódio acaba.",
            "No simulador, errar é barato: ele pode cair, sair da pista, recomeçar. Depois, a mesma tabela vai para o robô de verdade. Aqui, cada ponto é um episódio; os terracota são os snapshots que a gente usou para acompanhar a evolução.",
        ],
        action="Aponte para o número 200, depois para a grade de pontos.",
    ),
    dict(
        n="11", title="O resultado", time="5:20–5:50", key="−49 → +559",
        speech=[
            "E o resultado aparece na recompensa. Nos primeiros 20 episódios, a média era −49. Nos últimos 20, +559. Isso não é um prêmio: é o sinal de que ele passa muito mais tempo na linha.",
            "A curva completa está no próximo slide. Mas o número grande resume: ele saiu de um comportamento ruim para um comportamento bom.",
        ],
        action="Pause depois de “+559”. Deixe o número aparecer para o público.",
    ),
    dict(
        n="12", title="O comportamento", time="5:50–6:15", key="5 → 120 passos",
        speech=[
            "Para comparar, a mesma pista e o mesmo ponto de partida. Em cima, a política aleatória: ela fica na linha só 5 passos e sai. Embaixo, a política aprendida: 120 passos, 120 na linha.",
            "Cada quadradinho é um passo; terracota quer dizer “está sobre a linha”. A diferença não é sorte: é a tabela.",
        ],
        action="Aponte para a faixa de cima e depois para a de baixo. Se o robô estiver rodando, aponte para ele também.",
    ),
    dict(
        n="13", title="A curva não é lisa", time="6:15–6:35", key="Aprender é irregular",
        speech=[
            "Só que a curva não é lisa. Cada linha clara é um episódio; a linha escura é a média móvel. Tem queda, tem episódio ruim, tem variação.",
            "O melhor episódio chegou a +822, mas os últimos 20 ficaram em +559. Aprender é irregular. Ele ainda erra — só erra menos.",
        ],
        action="Não tente justificar cada queda. A mensagem é a tendência, não cada ponto.",
    ),
    dict(
        n="17", title="Fechamento", time="6:35–7:00", key="Demo ao vivo",
        speech=[
            "Então, voltando à pergunta do começo: como um robô aprende? Ele não nasceu sabendo. Ele tentou, errou, recebeu notas e ajustou uma tabela de 24 números. Isso é aprendizado por reforço.",
            "E o robô está aqui do lado: eu posso colocá-lo na pista agora. Enquanto ele anda, reparem nos sensores e nas rodas. E me perguntem: e se a linha acabar? Obrigado!",
        ],
        action="Coloque o robô na pista e deixe-o rodar por 10–15 segundos antes de abrir para perguntas.",
    ),
]

EXT = [
    dict(
        n="14", title="Arquitetura", time="+0:00–0:40", key="Quatro formas de montar",
        speech=[
            "Se vocês quiserem entender como isso vira um projeto de engenharia, existem quatro formas de montar. A mais simples é o if/else, que é a linha de base. Depois, o simulador em Python, que treina rápido.",
            "Depois, o agente embarcado no Arduino, que aprende sozinho. E o modo serial, em que o Python manda leituras e o Arduino devolve ações. A mesma tabela de 24 números pode viver no PC ou na RAM do microcontrolador. O robô aqui usa a versão embarcada.",
        ],
        action="Aponte para as três colunas do slide: simulador, ponte e robô.",
    ),
    dict(
        n="15", title="Por que importa", time="+0:40–1:10", key="IA local e barata",
        speech=[
            "Por que isso importa? Porque é inteligência artificial rodando local, sem nuvem, com 24 números e um microcontrolador barato. É a ideia de edge AI: decidir perto de onde a ação acontece.",
            "E é uma forma muito concreta de ensinar reforço: dá para ver a tabela mudando.",
        ],
        action="Sem pressa. Deixe a frase “sem nuvem” cair.",
    ),
    dict(
        n="16", title="Limites", time="+1:10–1:40", key="O que ainda falta",
        speech=[
            "E o que ele ainda não sabe? Oito estados é pouco para curvas fechadas e cruzamentos. A linha ainda pode ser perdida. E o simulador não é o chão de verdade: atrito, ruído e bateria mudam o jogo.",
            "Os próximos passos são mais sensores, câmera e estados contínuos. O próximo passo é sair do discreto — e continuar aprendendo.",
        ],
        action="Aponte para o “8 → ∞” e depois para a lista de próximos passos.",
    ),
]

QA = [
    ("O que é Q-learning, em uma frase?",
     "É aprender por tentativa e erro: o robô age, recebe uma nota e guarda quanto vale cada ação em cada situação. Aqui, a “memória” é uma tabela de 8 por 3."),
    ("Ele realmente aprende ou é só um monte de if/else?",
     "As regras de aprendizado são programadas; o comportamento, não. A tabela começa zerada e é preenchida pela experiência. O if/else decide sempre igual; o Q-learning muda com o que vive."),
    ("Por que 8 estados?",
     "São 3 sensores binários: 2³ = 8. É uma simplificação deliberada. Com mais sensores ou câmera, o número de estados cresce — e o próximo passo é justamente esse."),
    ("Por que a recompensa é negativa?",
     "Negativo é um sinal de “essa ação me afastou do objetivo”. O −3 é o pior caso: perdeu a linha. Ele aprende a evitar. O +1 é o centro na linha."),
    ("Ele ainda erra?",
     "Sim. A curva não é lisa e a política final pode perder a linha em curvas fechadas ou pisos diferentes. O aprendizado reduz o erro; não elimina."),
    ("Quanto tempo leva para treinar?",
     "No simulador, são 200 episódios, até 1.000 passos cada. No Arduino, o treinamento é online e mais lento, porque cada ação tem um delay de 100 ms. O tempo real depende da pista e do hardware."),
    ("Por que não usar if/else?",
     "If/else é ótimo quando você conhece todas as situações. O aprendizado serve para adaptar quando a pista ou as condições mudam. O if/else é a linha de base."),
    ("Isso é inteligência artificial de verdade?",
     "É uma forma clássica de aprendizado por reforço, não um modelo generativo. Mas é IA que aprende com experiência e toma decisão — e cabe em um microcontrolador."),
    ("O que acontece se ele perder a linha?",
     "No simulador, 15 passos perdidos encerram o episódio. No robô real, ele pode parar ou continuar a última ação, dependendo do firmware. A recompensa −3 pune esse comportamento."),
    ("Quanto custa e o que tem dentro?",
     "Arduino, três sensores IR, ponte H L298N, dois motores DC com caixa de redução, chassi e bateria. A Q-table ocupa 24 números na RAM; não precisa de nuvem nem de câmera."),
    ("Dá para usar em carro autônomo?",
     "A ideia é a mesma, mas o espaço de estados é muito maior. Aqui é uma versão didática, embarcada e de baixo custo. É um ponto de partida, não um produto."),
    ("O que é epsilon?",
     "É a chance de explorar: começa em 1,00 (100%) e cai para 0,13 em 200 episódios, com mínimo de 0,02. É o equilíbrio entre arriscar e confiar."),
]

CHECK = [
    "Ensaie com o robô ligado: fale enquanto ele anda.",
    "Teste a pista e a carga da bateria; leve bateria/pilhas reserva.",
    "Leve o PDF em um pendrive e também no e-mail/cloud.",
    "Teste HDMI, som e brilho; desative notificações.",
    "Imprima este roteiro ou deixe no celular; o deck tem notas, mas o papel é o backup.",
    "Deixe o robô em uma mesa segura e fixe a pista com fita.",
    "Leve um pano ou escova macia para limpar os sensores.",
    "Não deixe visitantes pegarem no robô; convide a apontar.",
    "Plano B: se o robô falhar, use os slides 11–12 e explique a tabela; se o projetor falhar, use o robô e este roteiro.",
]

NUMBERS = [
    ("3", "sensores · 3 ações · 8 estados · 24 notas"),
    ("200", "episódios · até 1.000 passos · 15 passos perdidos"),
    ("−49 → +559", "recompensa média: primeiros 20 × últimos 20 episódios"),
    ("5 → 120", "passos na linha: política aleatória × política aprendida"),
    ("1,00 → 0,13", "exploração: início × após 200 episódios (mínimo 0,02)"),
]

PHRASES = [
    "Ele não vê a linha; ele sente o contraste.",
    "A tabela é o cérebro dele.",
    "No começo ele chuta; depois confia.",
    "Aprender é irregular.",
    "Ele não nasceu sabendo. Aprendeu.",
]


def md_escape(t):
    return t.replace("|", "\\|")


def build_md():
    out = []
    out.append(f"# {TITLE}\n")
    out.append(f"**{SUB}**\n")
    out.append(INTRO + "\n")
    out.append("## Roteiro principal — 7 minutos\n")
    out.append("| Slide | Tempo | Ideia-chave |")
    out.append("|---|---|---|")
    for n, t, k in TIMING:
        out.append(f"| {n} | {t} | {md_escape(k)} |")
    out.append("")
    for sec in MAIN:
        out.append(f"## Slide {sec['n']} · {sec['title']} — {sec['time']}\n")
        out.append("**Fala**\n")
        for p in sec["speech"]:
            out.append(p + "\n")
        out.append(f"> **Ação:** {sec['action']}\n")
    out.append("## Versão estendida — acrescente os slides 14–16\n")
    out.append("Se sobrar tempo ou se a conversa pedir mais profundidade, insira estes três slides **depois do 13 e antes do 17**. O total fica em cerca de 9 minutos.\n")
    for sec in EXT:
        out.append(f"## Slide {sec['n']} · {sec['title']} — {sec['time']}\n")
        out.append("**Fala**\n")
        for p in sec["speech"]:
            out.append(p + "\n")
        out.append(f"> **Ação:** {sec['action']}\n")
    out.append("## Perguntas prováveis\n")
    for q, a in QA:
        out.append(f"**{q}**\n")
        out.append(a + "\n")
    out.append("## Checklist antes da feira\n")
    for item in CHECK:
        out.append(f"- {item}")
    out.append("")
    out.append("## Números para decorar\n")
    for num, desc in NUMBERS:
        out.append(f"- **{num}** — {desc}")
    out.append("")
    out.append("## Frases de bolso\n")
    for p in PHRASES:
        out.append(f"- “{p}”")
    out.append("")
    path = os.path.join(BASE, "Roteiro_Apresentacao.md")
    open(path, "w", encoding="utf-8").write("\n".join(out))
    print("ok", path)


def set_cell_shading(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_color)
    tcPr.append(shd)


def set_cell_margins(cell, top=60, bottom=60, left=100, right=100):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement("w:tcMar")
    for tag, val in (("top", top), ("bottom", bottom), ("left", left), ("right", right)):
        el = OxmlElement(f"w:{tag}")
        el.set(qn("w:w"), str(val))
        el.set(qn("w:type"), "dxa")
        tcMar.append(el)
    tcPr.append(tcMar)


def add_bottom_border(paragraph, color="C24E2E", size=6):
    pPr = paragraph._p.get_or_add_pPr()
    pbdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), str(size))
    bottom.set(qn("w:space"), "4")
    bottom.set(qn("w:color"), color)
    pbdr.append(bottom)
    pPr.append(pbdr)


def shade_paragraph(paragraph, color="F7F3EC"):
    pPr = paragraph._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), color)
    pPr.append(shd)


def add_run(p, text, size=10.5, color=INK, font="Segoe UI", bold=False, italic=False):
    r = p.add_run(text)
    r.font.name = font
    r.font.size = Pt(size)
    r.font.color.rgb = color
    r.bold = bold
    r.italic = italic
    return r


def para(doc, text="", size=10.5, color=INK, font="Segoe UI", bold=False, italic=False,
         space_after=4, space_before=0, line=1.28, align=WD_ALIGN_PARAGRAPH.LEFT, indent=0):
    p = doc.add_paragraph()
    p.alignment = align
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.line_spacing = line
    if indent:
        p.paragraph_format.left_indent = Cm(indent)
    if text:
        add_run(p, text, size=size, color=color, font=font, bold=bold, italic=italic)
    return p


def section_heading(doc, n, title, time):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(2)
    add_run(p, f"SLIDE {n}  ", size=9, color=TERRA, font="Consolas", bold=True)
    add_run(p, title, size=15, color=INK, font="Bahnschrift")
    add_run(p, f"   {time}", size=8.5, color=MUTED, font="Consolas")
    add_bottom_border(p, "D9D2C5", 4)


def action_line(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(0.35)
    p.paragraph_format.space_before = Pt(3)
    p.paragraph_format.space_after = Pt(8)
    p.paragraph_format.line_spacing = 1.2
    shade_paragraph(p, "F7F3EC")
    add_run(p, "▸  ", size=10, color=TERRA, font="Georgia", bold=True)
    add_run(p, text, size=10, color=MUTED, font="Georgia", italic=True)


def build_docx():
    doc = Document()
    sec = doc.sections[0]
    sec.page_height = Cm(29.7)
    sec.page_width = Cm(21.0)
    sec.top_margin = Cm(1.9)
    sec.bottom_margin = Cm(1.8)
    sec.left_margin = Cm(2.0)
    sec.right_margin = Cm(2.0)

    style = doc.styles["Normal"]
    style.font.name = "Segoe UI"
    style.font.size = Pt(10.5)
    style.font.color.rgb = INK
    style.paragraph_format.space_after = Pt(4)

    # rodapé
    footer = sec.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_run(footer, "Roteiro · Como um robô aprende? · Feira de Ciências 2026", size=8, color=MUTED, font="Consolas")

    p = para(doc, "ROTEIRO DE APRESENTAÇÃO", size=8.5, color=TERRA, font="Consolas", bold=True, space_after=4)
    p = para(doc, TITLE, size=24, color=INK, font="Bahnschrift", space_after=2, line=1.0)
    para(doc, SUB, size=11, color=MUTED, font="Segoe UI", space_after=10)

    # caixa de introdução
    t = doc.add_table(rows=1, cols=1)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = t.cell(0, 0)
    set_cell_shading(cell, "F7F3EC")
    set_cell_margins(cell, 120, 120, 160, 160)
    cell.paragraphs[0].paragraph_format.space_after = Pt(0)
    cell.paragraphs[0].paragraph_format.line_spacing = 1.3
    add_run(cell.paragraphs[0], INTRO, size=10, color=MUTED, font="Georgia", italic=True)

    para(doc, "Roteiro principal — 7 minutos", size=16, color=INK, font="Bahnschrift", space_before=16, space_after=6)

    # tabela de tempos
    table = doc.add_table(rows=1, cols=3)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    widths = [Cm(2.0), Cm(3.2), Cm(11.6)]
    hdr = table.rows[0].cells
    for i, (txt, w) in enumerate(zip(["SLIDE", "TEMPO", "IDEIA-CHAVE"], widths)):
        hdr[i].width = w
        set_cell_shading(hdr[i], "171512")
        set_cell_margins(hdr[i], 70, 70, 100, 100)
        p = hdr[i].paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        add_run(p, txt, size=8, color=RGBColor(0xF4, 0xF1, 0xEA), font="Consolas", bold=True)
    for idx, (n, t_, k) in enumerate(TIMING):
        row = table.add_row().cells
        for i, (txt, w) in enumerate(zip([n, t_, k], widths)):
            row[i].width = w
            set_cell_margins(row[i], 60, 60, 100, 100)
            p = row[i].paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            add_run(p, txt, size=9.5, color=TERRA if i == 0 else INK, font="Consolas" if i < 2 else "Segoe UI",
                    bold=(i == 0))

    # roteiro principal
    doc.add_page_break()
    para(doc, "Roteiro principal", size=18, color=INK, font="Bahnschrift", space_after=2)
    para(doc, "Fale como se estivesse explicando para um amigo. As pausas são parte do roteiro.", size=10, color=MUTED, font="Georgia", italic=True, space_after=8)

    for sec_ in MAIN:
        section_heading(doc, sec_["n"], sec_["title"], sec_["time"])
        for speech in sec_["speech"]:
            para(doc, speech, size=10.5, color=INK, space_after=5, line=1.32)
        action_line(doc, sec_["action"])

    # estendido
    doc.add_page_break()
    para(doc, "Versão estendida — slides 14–16", size=18, color=INK, font="Bahnschrift", space_after=2)
    para(doc, "Insira estes três slides depois do 13 e antes do 17. O total fica em cerca de 9 minutos.", size=10, color=MUTED, font="Georgia", italic=True, space_after=8)
    for sec_ in EXT:
        section_heading(doc, sec_["n"], sec_["title"], sec_["time"])
        for speech in sec_["speech"]:
            para(doc, speech, size=10.5, color=INK, space_after=5, line=1.32)
        action_line(doc, sec_["action"])

    # Q&A
    doc.add_page_break()
    para(doc, "Perguntas prováveis", size=18, color=INK, font="Bahnschrift", space_after=2)
    para(doc, "Respostas curtas. Se a pergunta pedir mais, volte ao slide correspondente.", size=10, color=MUTED, font="Georgia", italic=True, space_after=8)
    for q, a in QA:
        p = para(doc, q, size=10.5, color=INK, bold=True, space_before=6, space_after=2, line=1.2)
        para(doc, a, size=10, color=MUTED, space_after=4, line=1.28)

    # checklist
    doc.add_page_break()
    para(doc, "Checklist e números", size=18, color=INK, font="Bahnschrift", space_after=2)
    para(doc, "Antes de sair de casa e antes de começar a falar.", size=10, color=MUTED, font="Georgia", italic=True, space_after=6)

    para(doc, "CHECKLIST", size=9, color=TERRA, font="Consolas", bold=True, space_before=6, space_after=4)
    for item in CHECK:
        p = doc.add_paragraph(style="List Bullet")
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.2
        add_run(p, item, size=10, color=INK)

    para(doc, "NÚMEROS PARA DECORAR", size=9, color=TERRA, font="Consolas", bold=True, space_before=12, space_after=4)
    for num, desc in NUMBERS:
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(3)
        add_run(p, f"{num}  ", size=12, color=TERRA, font="Consolas", bold=True)
        add_run(p, desc, size=10, color=INK, font="Segoe UI")

    para(doc, "FRASES DE BOLSO", size=9, color=TERRA, font="Consolas", bold=True, space_before=12, space_after=4)
    for phrase in PHRASES:
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(3)
        add_run(p, f"“{phrase}”", size=11, color=MUTED, font="Georgia", italic=True)

    path = os.path.join(BASE, "Roteiro_Apresentacao.docx")
    doc.save(path)
    print("ok", path)


if __name__ == "__main__":
    build_md()
    build_docx()
