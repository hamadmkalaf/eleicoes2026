"""Desenha a planta-base do Hall 2 e monta a peca de leitura do espaco.

Vem antes das ideias 1 e 2: nao propoe layout nenhum, so mostra o salao como
ele e e o papel que cada porta recebeu — o que as duas ideias tem em comum e o
que precisa estar acordado antes de escolher entre elas. Serve para conferir
que o espaco esta sendo lido do mesmo jeito pelos dois lados da conversa.

Geometria e papeis das portas vem de `salao.py`; a linguagem grafica (escala,
paleta, primitivas) vem de `ideia1_planta.py`, para que as tres plantas se leiam
como um conjunto. Grava `saidas/planta_base.svg` e `saidas/planta_base.html`.
"""
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "scripts"))

import salao as FL                                          # noqa: E402
from ideia1_planta import (AMBAR, AZUL, EST, H, ML, MR, MT, MESA, MODULO,  # noqa: E402
                           S, VERDE, VERM, W, esc, ponta, px, rect, txt)
from ideia1_pagina import estilo                            # noqa: E402

MB = 250          # margem inferior: fachada sul, cotas e legenda

# As saidas 2.8/2.9 ficam na parede do recorte sudoeste, medidas no PDF. Nao
# entram em `salao.PORTAS` porque nenhuma parede do recorte recebe MRV em
# qualquer das duas ideias — aqui aparecem so para a planta ficar completa.
RECORTE_X, RECORTE_Y = FL.RECORTE[2], FL.RECORTE[3]
PORTA_RECORTE = ("2.8/2.9", 3.0, 6.5)

# Papel de cada porta. E o mesmo nas ideias 1 e 2, de proposito: as duas foram
# desenhadas sobre a mesma decisao de fachada para poderem ser comparadas.
PAPEL = {
    "carga oeste": ("entrada", "ENTRADA A"),
    "carga leste": ("entrada", "ENTRADA B"),
    "2.4": ("saida", "SAÍDA"),
    "2.5/2.6": ("reforco", "reforço"),
    "2.2/2.3": ("reforco", "reforço"),
    "2.7": ("emergencia", "emergência"),
    "2.1": ("emergencia", "emergência"),
    "2.13": ("emergencia", "emergência"),
    "2.14/2.15": ("emergencia", "emergência"),
    "2.22/2.23": ("emergencia", "emergência"),
    "2.20/2.21": ("emergencia", "emergência"),
    "2.18/2.19": ("emergencia", "emergência"),
    "2.16/2.17": ("emergencia", "emergência"),
    "2.10/2.11 (WC)": ("passagem", "acesso aos WC"),
    "acesso Hall 1": ("passagem", "passagem"),
    "2.8/2.9": ("emergencia", "emergência"),
}
COR_PAPEL = {"entrada": AZUL, "saida": AMBAR, "reforco": AMBAR,
             "emergencia": VERDE, "passagem": MESA}

# Vetor unitario que aponta da parede para dentro do salao.
DENTRO = {"norte": (0, -1), "sul": (0, 1), "oeste": (1, 0), "leste": (-1, 0)}


def vg(v, casas=1) -> str:
    return f"{v:.{casas}f}".replace(".", ",")


def ponto_na_parede(parede, t, fora=0.0):
    """Ponto sobre a parede na coordenada `t`, deslocado `fora` metros."""
    dx, dy = DENTRO[parede]
    if parede == "norte":
        return t, H + fora
    if parede == "sul":
        return t, -fora
    if parede == "oeste":
        return -fora, t
    return W + fora, t


def segmento_de_porta(parede, a, b, cor, larg=5.0):
    p1, p2 = ponto_na_parede(parede, a), ponto_na_parede(parede, b)
    x1, y1 = px(*p1)
    x2, y2 = px(*p2)
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{cor}" stroke-width="{larg}" stroke-linecap="butt"/>')


def envelope(parede, a, b, r, duvida):
    """Zona de recuo de uma saida de emergencia, medida para dentro do salao."""
    if parede == "norte":
        z = (a - r, H - r, b + r, H)
    elif parede == "sul":
        z = (a - r, 0, b + r, r)
    elif parede == "oeste":
        z = (0, a - r, r, b + r)
    else:
        z = (W - r, a - r, W, b + r)
    return rect(*z, fill=VERDE, opacity=".05" if duvida else ".09",
                stroke=VERDE, stroke_width="0.9",
                stroke_dasharray="2 4" if duvida else "4 3")


def cota(x0, y0, x1, y1, rotulo, dy=0):
    """Linha de cota simples com marcas nas pontas."""
    a, b = px(x0, y0)
    c, d = px(x1, y1)
    o = [f'<path d="M{a:.1f} {b:.1f}L{c:.1f} {d:.1f}" stroke="{MESA}" '
         f'stroke-width="0.8" opacity=".8"/>']
    for mx, my in ((a, b), (c, d)):
        ang = 90 if abs(a - c) > abs(b - d) else 0
        o.append(f'<line x1="{mx - 3 * (ang == 90 and 0 or 1):.1f}" '
                 f'y1="{my - 3 * (ang == 90 and 1 or 0):.1f}" '
                 f'x2="{mx + 3 * (ang == 90 and 0 or 1):.1f}" '
                 f'y2="{my + 3 * (ang == 90 and 1 or 0):.1f}" '
                 f'stroke="{MESA}" stroke-width="0.8"/>')
    vertical = abs(b - d) > abs(a - c)
    o.append(txt((x0 + x1) / 2 + (0.9 if vertical else 0), (y0 + y1) / 2,
                 rotulo, "sub", dy=dy, rot=-90 if vertical else 0))
    return "".join(o)


def main():
    LG, AL = ML + W * S + MR, MT + H * S + MB
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {LG:.0f} '
         f'{AL:.0f}" width="{LG:.0f}" height="{AL:.0f}" role="img" '
         f'aria-label="Planta-base do Hall 2: contorno, as dezesseis portas e '
         f'o papel de cada uma no dia da votação">',
         f'<rect x="0" y="0" width="{LG}" height="{AL}" fill="#fbfaf7"/>']

    # ---------- piso e contorno
    poly = [(RECORTE_X, 0), (W, 0), (W, H), (0, H), (0, RECORTE_Y),
            (RECORTE_X, RECORTE_Y)]
    pts = " ".join(f"{px(x, y)[0]:.1f},{px(x, y)[1]:.1f}" for x, y in poly)
    o.append(f'<polygon points="{pts}" fill="#eef1f4"/>')

    # ---------- envelopes de recuo das saidas de emergencia
    for parede, lista in FL.PORTAS.items():
        for nome, a, b in lista:
            if PAPEL[nome][0] in ("entrada", "passagem"):
                continue
            o.append(envelope(parede, a, b, FL.RECUO_EMERGENCIA,
                              duvida=parede != "leste"))

    o.append(f'<polygon points="{pts}" fill="none" stroke="#1c2733" '
             f'stroke-width="3.4"/>')

    # ---------- portas
    for parede, lista in FL.PORTAS.items():
        for nome, a, b in lista:
            papel, _ = PAPEL[nome]
            o.append(segmento_de_porta(parede, a, b, COR_PAPEL[papel],
                                       6.5 if papel in ("entrada", "saida") else 5.0))
    ra, rb = PORTA_RECORTE[1], PORTA_RECORTE[2]
    x1, y1 = px(RECORTE_X, ra)
    x2, y2 = px(RECORTE_X, rb)
    o.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
             f'stroke="{VERDE}" stroke-width="5" stroke-linecap="butt"/>')

    # ---------- rotulos das portas, fora do salao
    for nome, a, b in FL.PORTAS["norte"]:
        o.append(txt((a + b) / 2, H, nome, "lbl", dy=-14))
        o.append(txt((a + b) / 2, H, f"{vg(b - a, 2)} m", "sub", dy=-4))
    for nome, a, b in FL.PORTAS["leste"]:
        o.append(txt(W, (a + b) / 2, nome, "lbl", anchor="start", dy=-3))
        x, y = px(W, (a + b) / 2)
        o[-1] = o[-1].replace(f'x="{x:.1f}"', f'x="{x + 10:.1f}"')
        o.append(txt(W, (a + b) / 2, f"{vg(b - a, 2)} m", "sub",
                     anchor="start", dy=8))
        o[-1] = o[-1].replace(f'x="{x:.1f}"', f'x="{x + 10:.1f}"')
    for nome, a, b in FL.PORTAS["oeste"]:
        curto = "Hall 1" if "Hall 1" in nome else nome.split(" (")[0]
        x, y = px(0, (a + b) / 2)
        for i, (t, est, dy) in enumerate(((curto, "lbl", -3),
                                          (f"{vg(b - a, 2)} m", "sub", 8))):
            o.append(txt(0, (a + b) / 2, t, est, anchor="end", dy=dy)
                     .replace(f'x="{x:.1f}"', f'x="{x - 10:.1f}"'))
    xr, _ = px(RECORTE_X, (ra + rb) / 2)
    for t, est, dy in ((PORTA_RECORTE[0], "lbl", -3), ("emergência", "sub", 8)):
        o.append(txt(RECORTE_X, (ra + rb) / 2, t, est, anchor="start", dy=dy)
                 .replace(f'x="{xr:.1f}"', f'x="{xr + 10:.1f}"'))

    # ---------- fachada sul: rotulo, papel e faixas
    for nome, a, b in FL.PORTAS["sul"]:
        papel, rotulo = PAPEL[nome]
        forte = papel in ("entrada", "saida")
        o.append(txt((a + b) / 2, 0, rotulo if forte else nome,
                     "prt" if forte else "lbl", dy=18))
        o.append(txt((a + b) / 2, 0, f"{vg(b - a, 2)} m", "sub", dy=29))
        if papel == "reforco":
            o.append(txt((a + b) / 2, 0, rotulo, "sub", dy=40))

    faixas = [(FL.PORTA_CARGA_O, "entra", AZUL),
              ((19.10, 37.47), "sai", AMBAR),
              (FL.PORTA_CARGA_L, "entra", AZUL)]
    for (a, b), papel, cor in faixas:
        xa, ya = px(a, 0)
        xb, _ = px(b, 0)
        o.append(f'<path d="M{xa:.1f} {ya + 44:.1f}v6h{xb - xa:.1f}v-6" '
                 f'fill="none" stroke="{cor}" stroke-width="1.6"/>')
    ea, eb = sum(FL.PORTA_CARGA_O) / 2, sum(FL.PORTA_CARGA_L) / 2
    o.append(txt(ea, 0, "entra", "via", dy=68))
    o.append(txt((19.10 + 37.47) / 2, 0, "sai", "via", dy=68))
    o.append(txt(eb, 0, "entra", "via", dy=68))
    o.append(cota(ea, -6.6, eb, -6.6, f"{vg(eb - ea)} m entre as entradas",
                  dy=-6))

    # ---------- setas de fluxo
    for x in (9.64, 46.94):
        a, b = px(x, 0)
        o.append(f'<path d="M{a:.1f} {b + 34:.1f}V{b - 42:.1f}" stroke="{AZUL}" '
                 f'stroke-width="3" opacity=".55"/>')
        o.append(ponta(x, 2.9, 90, AZUL, 5.2))
    a, b = px(28.29, 0)
    o.append(f'<path d="M{a:.1f} {b - 42:.1f}V{b + 34:.1f}" stroke="{AMBAR}" '
             f'stroke-width="3" opacity=".55"/>')
    o.append(ponta(28.29, -2.3, 270, AMBAR, 5.2))

    # ---------- setas de servico: WC e Hall 1 saem pela parede oeste
    for nome, a, b in FL.PORTAS["oeste"]:
        m = (a + b) / 2
        x, y = px(0, m)
        o.append(f'<path d="M{x - 4:.1f} {y:.1f}h-16" stroke="{MESA}" '
                 f'stroke-width="2" opacity=".6"/>')
        o.append(ponta(-1.5, m, 180, MESA, 4.0))

    # ---------- nomes das paredes e do recorte
    o.append(txt(W / 2, H - 4.2, "PAREDE NORTE", "zona"))
    o.append(txt(W / 2, 4.2, "FACHADA SUL", "zona"))
    o.append(txt(4.4, (H + RECORTE_Y) / 2, "PAREDE OESTE", "zona", rot=-90))
    o.append(txt(W - 4.4, H / 2, "PAREDE LESTE", "zona", rot=90))
    o.append(txt(RECORTE_X / 2, RECORTE_Y / 2, "fora do salão", "sub"))
    o.append(txt(RECORTE_X / 2, RECORTE_Y / 2, f"{vg(RECORTE_X)} × {vg(RECORTE_Y)} m",
                 "sub", dy=11))

    # ---------- cotas gerais
    o.append(cota(0, H + 2.2, W, H + 2.2, f"{vg(W)} m", dy=-5))
    o.append(cota(W + 2.9, 0, W + 2.9, H, f"{vg(H)} m", dy=-6))

    o.append(txt(0.0, H + 3.7, "PLANTA-BASE — o salão e o papel de cada porta",
                 "tit", anchor="start"))

    # ---------- legenda
    _, m_todas, _ = FL.capacidade_de_parede()
    _, m_leste, _ = FL.capacidade_de_parede(
        recuo={"leste": 3.0, "norte": 0.6, "oeste": 0.6, "sul": 0.6})
    ly, cx = MT + H * S + 132, ML
    itens = [(AZUL, "entrada do eleitor"), (AMBAR, "saída e reforços de saída"),
             (VERDE, "saída de emergência e seu recuo de 3 m"),
             (MESA, "passagem de serviço: WC e Hall 1")]
    for c, lab in itens:
        o.append(f'<rect x="{cx}" y="{ly - 8}" width="11" height="11" '
                 f'fill="{c}" opacity=".55" stroke="{c}"/>')
        o.append(f'<text x="{cx + 16}" y="{ly + 1}" {EST["lbl"]}>{esc(lab)}</text>')
        cx += 26 + len(lab) * 5.3
    for i, linha in enumerate((
            "Contorno e vãos medidos da planta oficial do RDS e da versão "
            "revisada que assinala as duas portas de carga. Nenhuma mesa "
            "receptora está desenhada: o miolo do salão é o",
            "que as ideias 1 e 2 disputam. O recuo de 3 m aparece hachurado em "
            "todas as saídas de emergência — cheio na parede leste, onde a "
            "exigência foi confirmada, e pontilhado nas",
            "demais, onde ainda é pergunta em aberto. É essa dúvida que separa "
            "55,7 m de parede livre de 74,9 m.")):
        o.append(f'<text x="{ML}" y="{ly + 26 + i * 14}" {EST["sub"]}>'
                 f'{esc(linha)}</text>')
    o.append("</svg>")

    cam = os.path.join(RAIZ, "saidas", "planta_base.svg")
    open(cam, "w", encoding="utf-8").write("\n".join(o))
    print("gravado", cam, os.path.getsize(cam), "bytes")
    return "\n".join(o)


# --------------------------------------------------------------- peca de leitura
NOTA = {
    "carga oeste": "Porta de carga. Entrada A, na ponta oeste da fachada.",
    "carga leste": "Porta de carga. Entrada B, na ponta leste da fachada.",
    "2.4": "Baia central da fachada sul. Por onde o eleitor sai depois de votar.",
    "2.5/2.6": "Abre junto com a 2.4 no pico da manhã.",
    "2.2/2.3": "Abre junto com a 2.4 no pico da manhã.",
    "2.7": "Fica fechada ao público; vão estreito, entre a entrada A e a saída.",
    "2.1": "Fica fechada ao público; vão estreito, entre a saída e a entrada B.",
    "2.13": "Recuo de 3 m em dúvida: pode ou não liberar parede para mesas.",
    "2.14/2.15": "Recuo de 3 m em dúvida: pode ou não liberar parede para mesas.",
    "2.22/2.23": "Recuo de 3 m confirmado. Sobra um nicho de 2,79 m entre pares.",
    "2.20/2.21": "Recuo de 3 m confirmado. Sobra um nicho de 2,79 m entre pares.",
    "2.18/2.19": "Recuo de 3 m confirmado. Sobra um nicho de 2,79 m entre pares.",
    "2.16/2.17": "Recuo de 3 m confirmado. Come 3 m da ponta da parede norte.",
    "2.10/2.11 (WC)": "Único acesso aos sanitários, que ficam fora do salão.",
    "acesso Hall 1": "Passagem de serviço para o Hall 1. Não recebe público.",
    "2.8/2.9": "Parede do recorte sudoeste. Fora do modelo de geometria.",
}
NOME_PAREDE = {"sul": "sul", "norte": "norte", "leste": "leste",
               "oeste": "oeste", "recorte": "recorte"}
NOME_PAPEL = {"entrada": "entrada", "saida": "saída", "reforco": "reforço",
              "emergencia": "emergência", "passagem": "passagem"}
CLASSE_PAPEL = {"entrada": "talta", "saida": "talta", "reforco": "tmedia",
                "emergencia": "tleve", "passagem": "tleve"}


def todas_as_portas():
    """As portas de `salao.py` mais as do recorte, na ordem de leitura."""
    for parede in ("sul", "leste", "norte", "oeste"):
        for nome, a, b in FL.PORTAS[parede]:
            yield parede, nome, a, b
    yield "recorte", PORTA_RECORTE[0], PORTA_RECORTE[1], PORTA_RECORTE[2]


def tabela_portas():
    ls = []
    for parede, nome, a, b in todas_as_portas():
        papel, _ = PAPEL[nome]
        ls.append(f'<tr><td>{NOME_PAREDE[parede]}</td>'
                  f'<td class="mono b">{esc(nome.split(" (")[0])}</td>'
                  f'<td class="mono">{vg(b - a, 2)} m</td>'
                  f'<td><span class="tag {CLASSE_PAPEL[papel]}">'
                  f'{NOME_PAPEL[papel]}</span></td>'
                  f'<td>{esc(NOTA[nome])}</td></tr>')
    return "\n".join(ls)


def tabela_espacos(piso, m_leste, m_todas, p_leste, p_todas):
    linhas = [
        ("Piso do salão", f"{piso} m²",
         f"{vg(W)} × {vg(H)} m menos o recorte de {vg(FL.RECORTE[2])} × "
         f"{vg(FL.RECORTE[3])} m"),
        ("Perímetro construído", f"{vg(2 * (W + H))} m",
         "soma das quatro paredes, sem descontar vãos nem recuos"),
        ("Parede livre · recuo só na leste", f"{vg(m_leste)} m",
         f"{p_leste} posições de mesa com o módulo de "
         f"{vg(FL.LARG_MIN_BAIA, 2)} m de frente"),
        ("Parede livre · recuo em todas", f"{vg(m_todas)} m",
         f"{p_todas} posições de mesa com o mesmo módulo"),
        ("Recorte do canto sudoeste", f"{vg(FL.RECORTE[2] * FL.RECORTE[3])} m²",
         "não pertence ao Hall 2; sobra a parede com as saídas 2.8/2.9"),
    ]
    return "\n".join(f'<tr><td>{a}</td><td class="mono b">{b}</td>'
                      f'<td>{c}</td></tr>' for a, b, c in linhas)


def pagina(svg):
    """Monta saidas/planta_base.html a partir do template e da planta."""
    svg = re.sub(r'\swidth="\d+"\sheight="\d+"',
                 ' style="width:100%;height:auto"', svg, count=1)
    _, m_todas, p_todas = FL.capacidade_de_parede()
    _, m_leste, p_leste = FL.capacidade_de_parede(
        recuo={"leste": 3.0, "norte": 0.6, "oeste": 0.6, "sul": 0.6})
    recorte = FL.RECORTE[2] * FL.RECORTE[3]
    piso = W * H - recorte
    vaos = [(PAPEL[n][0], b - a) for _, n, a, b in todas_as_portas()]
    soma = lambda *papeis: sum(v for p, v in vaos if p in papeis)
    ea, eb = sum(FL.PORTA_CARGA_O) / 2, sum(FL.PORTA_CARGA_L) / 2

    campos = dict(
        estilo=estilo(), svg=svg,
        piso=f"{piso:,.0f}".replace(",", "."),
        recorte=vg(recorte),
        recorte_dim=f"{vg(FL.RECORTE[2])} × {vg(FL.RECORTE[3])}",
        larg=vg(W), prof=vg(H),
        nportas=len(vaos),
        vao_total=vg(sum(v for _, v in vaos)),
        vao_entrada=vg(soma("entrada")),
        vao_saida=vg(soma("saida", "reforco")),
        dist_entradas=vg(eb - ea),
        m_leste=vg(m_leste), m_todas=vg(m_todas),
        p_leste=p_leste, p_todas=p_todas,
        portas=tabela_portas(),
        espacos=tabela_espacos(f"{piso:,.0f}".replace(",", "."),
                               m_leste, m_todas, p_leste, p_todas),
    )
    with open(os.path.join(RAIZ, "scripts", "planta_base_template.html"),
              encoding="utf-8") as f:
        html = f.read()
    for k, v in campos.items():
        html = html.replace("@@" + k + "@@", str(v))
    if "@@" in html:
        raise SystemExit("placeholder nao substituido: "
                         + html[html.index("@@"):html.index("@@") + 40])
    cam = os.path.join(RAIZ, "saidas", "planta_base.html")
    open(cam, "w", encoding="utf-8").write(html)
    print("gravado", cam, os.path.getsize(cam), "bytes")


if __name__ == "__main__":
    pagina(main())
