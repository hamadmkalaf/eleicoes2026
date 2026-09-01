"""Desenha a planta-base do Hall 2 e monta a peca de leitura do espaco.

Nao propoe layout nenhum. Mostra o salao como ele e, com as portas numeradas
por fachada e o que ja se sabe sobre cada uma: quais estao fechadas, qual serve
ao catering e quais sao saidas de emergencia com recuo obrigatorio. Quem entra e
quem sai por onde e decisao posterior, e de proposito nao aparece aqui.

Geometria vem de `salao.py`; a linguagem grafica, de `desenho.py`. Grava
`saidas/planta_base.svg` e `saidas/planta_base.html`.
"""
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "scripts"))

import salao as FL                                            # noqa: E402
import desenho as D                                           # noqa: E402

# Esta planta rotula as portas dos quatro lados, fora do salao: as margens
# laterais precisam caber "O2 / 2.10/2.11 · 3,07 m". As primitivas leem estas
# constantes na hora da chamada, entao mudar aqui basta.
D.ML, D.MR = 152, 152
MB = 230          # margem inferior: rotulos da fachada sul, cota e legenda

from desenho import (AZUL, EST, H, MESA, S, VERDE, VERM,      # noqa: E402
                     W, cota, esc, estilo, px, rect, txt)

# As saidas 2.8/2.9 ficam na parede do recorte sudoeste, medidas no PDF a 3,0 e
# 6,5 m do canto sul. Nao entram em `salao.PORTAS` nem na numeracao das
# fachadas: a parede do recorte nao e fachada do salao.
RECORTE_X, RECORTE_Y = FL.RECORTE[2], FL.RECORTE[3]
PORTA_RECORTE = ("2.8/2.9", 3.0, 6.5)

# Ordem de leitura de cada fachada, para a numeracao: as paredes horizontais
# sao lidas de oeste para leste; as verticais, de norte para sul. E o mesmo
# sentido em que se le o desenho, da esquerda para a direita e de cima para
# baixo.
SENTIDO = {"norte": 1, "sul": 1, "leste": -1, "oeste": -1}
INICIAL = {"norte": "N", "sul": "S", "leste": "L", "oeste": "O"}

# Estado conhecido de cada porta. `livre` quer dizer que ainda nao ha decisao —
# nao que a porta esteja disponivel.
ESTADO = {
    "N1": ("fechada", "Permanece fechada."),
    "N2": ("catering", "Desbloqueada: é a saída do catering."),
    "L1": ("emergencia", "Saída de emergência. Recuo de 3 m."),
    "L2": ("emergencia", "Saída de emergência. Recuo de 3 m."),
    "L3": ("emergencia", "Saída de emergência. Recuo de 3 m."),
    "L4": ("emergencia", "Saída de emergência. Recuo de 3 m."),
    "O1": ("livre", "Passagem para o Hall 1."),
    "O2": ("livre", "Único acesso aos sanitários, que ficam fora do salão."),
    "S1": ("livre", "Porta de carga."),
    "S7": ("livre", "Porta de carga."),
    "R1": ("livre", "Parede do recorte sudoeste, fora das fachadas."),
}
PADRAO = ("livre", "Sem papel definido.")
COR_ESTADO = {"livre": MESA, "fechada": VERM, "catering": AZUL,
              "emergencia": VERDE}
NOME_ESTADO = {"livre": "a definir", "fechada": "fechada",
               "catering": "catering", "emergencia": "emergência"}


def vg(v, casas=1) -> str:
    return f"{v:.{casas}f}".replace(".", ",")


def numera():
    """Numera as portas de cada fachada na ordem de leitura do desenho.

    Devolve uma lista de dicionarios com o numero atribuido, o codigo do RDS, a
    parede, o intervalo em metros e o estado conhecido.
    """
    portas = []
    for parede in ("norte", "leste", "sul", "oeste"):
        lista = sorted(FL.PORTAS[parede],
                       key=lambda p: SENTIDO[parede] * p[1])
        for i, (codigo, a, b) in enumerate(lista, 1):
            num = f"{INICIAL[parede]}{i}"
            estado, nota = ESTADO.get(num, PADRAO)
            portas.append({"num": num, "codigo": codigo.split(" (")[0],
                           "parede": parede, "a": a, "b": b, "meio": (a + b) / 2,
                           "larg": b - a, "estado": estado, "nota": nota})
    estado, nota = ESTADO["R1"]
    portas.append({"num": "R1", "codigo": PORTA_RECORTE[0], "parede": "recorte",
                   "a": PORTA_RECORTE[1], "b": PORTA_RECORTE[2],
                   "meio": sum(PORTA_RECORTE[1:]) / 2,
                   "larg": PORTA_RECORTE[2] - PORTA_RECORTE[1],
                   "estado": estado, "nota": nota})
    return portas


def ponto(parede, t):
    """Ponto sobre a parede, na coordenada corrente daquela parede."""
    if parede == "norte":
        return t, H
    if parede == "sul":
        return t, 0.0
    if parede == "oeste":
        return 0.0, t
    if parede == "recorte":
        return RECORTE_X, t
    return W, t


def segmento(p, cor, larg=6.0):
    x1, y1 = px(*ponto(p["parede"], p["a"]))
    x2, y2 = px(*ponto(p["parede"], p["b"]))
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{cor}" stroke-width="{larg}" stroke-linecap="butt"/>')


def envelope(p, r=FL.RECUO_EMERGENCIA):
    """Os 3 m a respeitar em torno de uma saida de emergencia."""
    return rect(W - r, max(0.0, p["a"] - r), W, min(H, p["b"] + r),
                fill=VERDE, opacity=".10", stroke=VERDE, stroke_width="1",
                stroke_dasharray="4 3")


def nichos_da_parede_leste(portas, r=FL.RECUO_EMERGENCIA):
    """Trechos da parede leste que sobram fora dos recuos."""
    livre = [(0.0, H)]
    for p in portas:
        if p["parede"] != "leste":
            continue
        novo = []
        for x0, x1 in livre:
            if p["b"] + r <= x0 or p["a"] - r >= x1:
                novo.append((x0, x1))
                continue
            if x0 < p["a"] - r:
                novo.append((x0, p["a"] - r))
            if p["b"] + r < x1:
                novo.append((p["b"] + r, x1))
        livre = novo
    return [(a, b) for a, b in livre if b - a > 0.05]


def planta(portas):
    LG, AL = D.ML + W * S + D.MR, D.MT + H * S + MB
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {LG:.0f} '
         f'{AL:.0f}" width="{LG:.0f}" height="{AL:.0f}" role="img" '
         f'aria-label="Planta-base do Hall 2: o salão vazio, as portas '
         f'numeradas por fachada e o recuo de 3 m da parede leste">',
         f'<rect x="0" y="0" width="{LG}" height="{AL}" fill="#fbfaf7"/>']

    poly = [(RECORTE_X, 0), (W, 0), (W, H), (0, H), (0, RECORTE_Y),
            (RECORTE_X, RECORTE_Y)]
    pts = " ".join(f"{px(x, y)[0]:.1f},{px(x, y)[1]:.1f}" for x, y in poly)
    o.append(f'<polygon points="{pts}" fill="#eef1f4"/>')

    # ---------- recuo de 3 m: so a parede leste, como foi determinado
    for p in portas:
        if p["estado"] == "emergencia":
            o.append(envelope(p))
    o.append(cota(W - FL.RECUO_EMERGENCIA, 4.48, W, 4.48, "3 m", dy=-5))

    o.append(f'<polygon points="{pts}" fill="none" stroke="#1c2733" '
             f'stroke-width="3.4"/>')

    # ---------- portas e rotulos
    for p in portas:
        cor = COR_ESTADO[p["estado"]]
        o.append(segmento(p, cor))
        detalhe = f'{p["codigo"]} · {vg(p["larg"], 2)} m'
        if p["parede"] == "norte":
            o.append(txt(p["meio"], H, p["num"], "cod", dy=-17))
            o.append(txt(p["meio"], H, detalhe, "sub", dy=-7))
        elif p["parede"] == "sul":
            o.append(txt(p["meio"], 0, p["num"], "cod", dy=20))
            o.append(txt(p["meio"], 0, detalhe, "sub", dy=31))
        elif p["parede"] == "leste":
            o.append(txt(W, p["meio"], p["num"], "cod", anchor="start",
                         dx=11, dy=-2))
            o.append(txt(W, p["meio"], detalhe, "sub", anchor="start",
                         dx=11, dy=9))
        elif p["parede"] == "oeste":
            o.append(txt(0, p["meio"], p["num"], "cod", anchor="end",
                         dx=-11, dy=-2))
            o.append(txt(0, p["meio"], detalhe, "sub", anchor="end",
                         dx=-11, dy=9))
        else:
            o.append(txt(RECORTE_X, p["meio"], p["num"], "cod", anchor="start",
                         dx=11, dy=-2))
            o.append(txt(RECORTE_X, p["meio"], detalhe, "sub", anchor="start",
                         dx=11, dy=9))

    # ---------- o que ja esta decidido, dito no desenho
    n1 = next(p for p in portas if p["num"] == "N1")
    n2 = next(p for p in portas if p["num"] == "N2")
    o.append(txt(n1["meio"], H, "FECHADA", "prt", dy=16)
             .replace('fill="#243244"', f'fill="{VERM}"'))
    o.append(txt(n2["meio"], H, "DESBLOQUEADA", "prt", dy=16)
             .replace('fill="#243244"', f'fill="{AZUL}"'))
    o.append(txt(n2["meio"], H, "saída do catering", "sub", dy=27)
             .replace('fill="#5c6c80"', f'fill="{AZUL}"'))
    o.append(txt(W - 5.6, H / 2, "SAÍDAS DE EMERGÊNCIA · RECUO DE 3 m", "via",
                 rot=90).replace('fill="#243244"', f'fill="{VERDE}"'))

    # ---------- para onde levam as portas da parede oeste
    o.append(txt(0, 37.65, "para o Hall 1", "sub", anchor="end", dx=-11, dy=23))
    o.append(txt(0, 20.90, "para os sanitários", "sub", anchor="end",
                 dx=-11, dy=23))

    # ---------- nomes das paredes, recorte e cotas
    o.append(txt(W / 2, H - 3.6, "PAREDE NORTE", "zona"))
    o.append(txt(W / 2, 3.6, "FACHADA SUL", "zona"))
    o.append(txt(4.6, (H + RECORTE_Y) / 2, "PAREDE OESTE", "zona", rot=-90))
    o.append(txt(W - 8.4, H / 2, "PAREDE LESTE", "zona", rot=90))
    o.append(txt(RECORTE_X / 2, RECORTE_Y / 2 + 0.6, "fora do salão", "sub"))
    o.append(txt(RECORTE_X / 2, RECORTE_Y / 2 - 0.6,
                 f"{vg(RECORTE_X)} × {vg(RECORTE_Y)} m", "sub"))
    o.append(cota(0, H + 2.4, W, H + 2.4, f"{vg(W)} m", dy=-5))
    o.append(cota(35.0, 0, 35.0, H, f"{vg(H)} m", dy=-5))

    o.append(txt(0.0, H + 3.9, "PLANTA-BASE — o salão e as portas numeradas",
                 "tit", anchor="start"))

    # ---------- legenda
    ly, cx = D.MT + H * S + 118, D.ML
    for c, lab in ((MESA, "porta sem papel definido"),
                   (VERM, "porta fechada"),
                   (AZUL, "porta desbloqueada · saída do catering"),
                   (VERDE, "saída de emergência e seu recuo de 3 m")):
        o.append(f'<rect x="{cx}" y="{ly - 8}" width="11" height="11" '
                 f'fill="{c}" opacity=".55" stroke="{c}"/>')
        o.append(f'<text x="{cx + 16}" y="{ly + 1}" {EST["lbl"]}>{esc(lab)}</text>')
        cx += 26 + len(lab) * 5.3
    nichos = nichos_da_parede_leste(portas)
    linhas = (
        "As portas são numeradas por fachada, na ordem de leitura do desenho: "
        "de oeste para leste nas paredes norte e sul, de norte para sul nas "
        "paredes leste e oeste. Abaixo de cada",
        "número vem o código do RDS e a largura do vão. Nada aqui atribui "
        "entrada ou saída de eleitor — essa decisão vem depois. O recuo de 3 m "
        "está marcado só na parede leste, onde",
        f"todas as portas são saídas de emergência; sobram dela {len(nichos)} "
        f"trechos de {vg(nichos[0][1] - nichos[0][0], 2)} m entre os recuos. "
        "As portas 2.8/2.9 ficam na parede do recorte, que não é fachada.")
    for i, linha in enumerate(linhas):
        o.append(f'<text x="{D.ML}" y="{ly + 26 + i * 14}" {EST["sub"]}>'
                 f'{esc(linha)}</text>')
    o.append("</svg>")

    svg = "\n".join(o)
    cam = os.path.join(RAIZ, "saidas", "planta_base.svg")
    open(cam, "w", encoding="utf-8").write(svg)
    print("gravado", cam, os.path.getsize(cam), "bytes")
    return svg


# --------------------------------------------------------------- peca de leitura
NOME_PAREDE = {"norte": "norte", "leste": "leste", "sul": "sul",
               "oeste": "oeste", "recorte": "recorte"}
CLASSE_ESTADO = {"livre": "tleve", "fechada": "tcritica",
                 "catering": "talta", "emergencia": "tmedia"}


def tabela_portas(portas):
    ls = []
    for p in portas:
        ls.append(f'<tr><td class="mono b">{p["num"]}</td>'
                  f'<td>{NOME_PAREDE[p["parede"]]}</td>'
                  f'<td class="mono">{esc(p["codigo"])}</td>'
                  f'<td class="mono">{vg(p["larg"], 2)} m</td>'
                  f'<td><span class="tag {CLASSE_ESTADO[p["estado"]]}">'
                  f'{NOME_ESTADO[p["estado"]]}</span></td>'
                  f'<td>{esc(p["nota"])}</td></tr>')
    return "\n".join(ls)


def tabela_fachadas(portas):
    """Comprimento de cada fachada, quanto dela e vao e quanto sobra."""
    comp = {"norte": W, "sul": W - RECORTE_X, "leste": H, "oeste": H - RECORTE_Y}
    ls = []
    for parede in ("norte", "leste", "sul", "oeste"):
        deste = [p for p in portas if p["parede"] == parede]
        vao = sum(p["larg"] for p in deste)
        if parede == "leste":
            sobra = sum(b - a for a, b in nichos_da_parede_leste(portas))
            obs = (f"{len(nichos_da_parede_leste(portas))} trechos entre os "
                   f"recuos de 3 m")
        else:
            sobra = comp[parede] - vao
            obs = "parede cheia, sem recuo marcado"
        ls.append(f'<tr><td>{NOME_PAREDE[parede]}</td>'
                  f'<td class="mono">{vg(comp[parede])} m</td>'
                  f'<td class="mono">{len(deste)}</td>'
                  f'<td class="mono">{vg(vao)} m</td>'
                  f'<td class="mono b">{vg(sobra)} m</td>'
                  f'<td>{obs}</td></tr>')
    return "\n".join(ls)


def pagina(portas, svg):
    """Monta saidas/planta_base.html a partir do template e da planta."""
    svg = re.sub(r'\swidth="\d+"\sheight="\d+"',
                 ' style="width:100%;height:auto"', svg, count=1)
    recorte = RECORTE_X * RECORTE_Y
    piso = W * H - recorte
    nichos = nichos_da_parede_leste(portas)
    campos = dict(
        estilo=estilo(), svg=svg,
        piso=f"{piso:,.0f}".replace(",", "."),
        recorte=vg(recorte),
        recorte_dim=f"{vg(RECORTE_X)} × {vg(RECORTE_Y)}",
        larg=vg(W), prof=vg(H),
        nportas=len(portas),
        vao_total=vg(sum(p["larg"] for p in portas)),
        nleste=len(nichos), nicho=vg(nichos[0][1] - nichos[0][0], 2),
        leste_livre=vg(sum(b - a for a, b in nichos)),
        recuo=vg(FL.RECUO_EMERGENCIA, 0).replace(",0", ""),
        portas=tabela_portas(portas),
        fachadas=tabela_fachadas(portas),
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


def main():
    portas = numera()
    pagina(portas, planta(portas))


if __name__ == "__main__":
    main()
