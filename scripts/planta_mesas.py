"""Plantas de ocupacao do Hall 2: o modulo, as reguas de parede e os cenarios.

Usa as primitivas de `desenho.py`, na mesma escala e paleta da planta-base.
"""
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "scripts"))

import salao as FL                                            # noqa: E402
import mesas as MM                                            # noqa: E402
import desenho as D                                           # noqa: E402
import planta_base as PB                                      # noqa: E402

from desenho import AZUL, EST, H, S, VERDE, VERM, W, esc, px  # noqa: E402

ML, MR, MT = 46, 58, 54
MESA_COR, PESSOA, DIVISORIA, VIZINHA = "#3b4552", "#59616d", "#7a4c8f", "#9a8b72"
SERVICO = "#5d6773"

NOME_FACE = {"norte": "norte", "leste": "leste", "sul": "sul", "oeste": "oeste",
             "recorte_h": "recorte (face norte)", "recorte_v": "recorte (face leste)"}


def _margens(mb):
    D.ML, D.MR, D.MT, D.MB = ML, MR, MT, mb


def _svg(largura, altura, rotulo, corpo):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {largura:.0f} '
            f'{altura:.0f}" style="width:100%;height:auto" role="img" '
            f'aria-label="{esc(rotulo)}">'
            f'<rect x="0" y="0" width="{largura:.0f}" height="{altura:.0f}" '
            f'fill="#fbfaf7"/>' + "".join(corpo) + "</svg>")


def txt(x, y, t, est="sub", anchor="middle", **kw):
    return D.txt(x, y, t, est, anchor, **kw)


def livre(x, y, t, size=9.5, cor="#243244", peso=None, anchor="start"):
    """Texto posicionado em px, fora da malha do salao."""
    p = f' font-weight="{peso}"' if peso else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" {D.FONTE} font-size="{size}" '
            f'fill="{cor}" text-anchor="{anchor}"{p}>{esc(t)}</text>')


# ------------------------------------------------------------------ o modulo
def ponto(m, u, v=0.0):
    """(x, y) a u metros da parede e v metros do eixo do modulo."""
    f = FL.FACES[m["face"]]
    if f["eixo"] == "h":
        return (m["s"] + v, f["fixo"] + f["dentro"] * u)
    return (f["fixo"] + f["dentro"] * u, m["s"] + v)


def caixa(m, u0, u1, meia):
    a, b = ponto(m, u0, -meia), ponto(m, u1, +meia)
    return (min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1]))


def modulo(m):
    """Mesa de identificacao + tres mesarios + mesa de votacao + eleitor."""
    o = [D.rect(*caixa(m, 2.40, MM.PROF, MM.MESA_IDENT[1] / 2),
                fill=MESA_COR, opacity=".82")]
    cx, cy = px(*ponto(m, MM.FOLGA_ELEITOR + MM.URNA_D / 2))
    o.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{MM.URNA_D/2*S:.1f}" '
             f'fill="none" stroke="{AZUL}" stroke-width="1.5"/>')
    o.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{0.20*S:.1f}" '
             f'fill="{AZUL}" opacity=".55"/>')
    ex, ey = px(*ponto(m, MM.FOLGA_ELEITOR / 2))
    o.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{0.22*S:.1f}" fill="none" '
             f'stroke="{PESSOA}" stroke-width="1"/>')
    lado = +1 if m["lado"] == "a" else -1
    for k in range(3):
        mx, my = px(*ponto(m, 2.40 + 0.283 + k * 0.567,
                           lado * (MM.MESA_IDENT[1] / 2 + 0.26)))
        o.append(f'<circle cx="{mx:.1f}" cy="{my:.1f}" r="{0.22*S:.1f}" '
                 f'fill="{PESSOA}" opacity=".55"/>')
    return "".join(o)


def agrupa(modulos):
    """Agrupa os modulos por par; a MRV avulsa vem sozinha no seu grupo."""
    grupos, indice = [], {}
    for m in modulos:
        if m["par"] is None:
            grupos.append([m])
            continue
        if m["par"] not in indice:
            indice[m["par"]] = len(grupos)
            grupos.append([])
        grupos[indice[m["par"]]].append(m)
    return grupos


def pares(modulos):
    o = []
    for grupo in agrupa(modulos):
        a = grupo[0]
        b = grupo[1] if len(grupo) > 1 else None
        f = FL.FACES[a["face"]]
        if b is None:
            # avulsa: do outro lado do modulo ficam os mesarios e, depois
            # deles, a passagem livre que sobra do trecho
            s0 = a["s"] + MM.LARG / 2
            s1 = s0 + MM.MESARIO_ASSENTO + MM.FOLGA_ASSENTO + a["corredor"]
        else:
            s0 = min(a["s"], b["s"]) + MM.LARG / 2
            s1 = max(a["s"], b["s"]) - MM.LARG / 2
        o.append(D.rect(*FL.retangulo_na_parede(a["face"], s0, s1, MM.PROF),
                        fill=AZUL, opacity=".07"))
        meio = (s1 - a["corredor"] / 2) if b is None else (s0 + s1) / 2
        if f["eixo"] == "h":
            p0 = px(meio, f["fixo"] + f["dentro"] * (MM.PROF - 0.25))
            p1 = px(meio, f["fixo"] + f["dentro"] * 1.6)
        else:
            p0 = px(f["fixo"] + f["dentro"] * (MM.PROF - 0.25), meio)
            p1 = px(f["fixo"] + f["dentro"] * 1.6, meio)
        o.append(f'<path d="M{p0[0]:.1f} {p0[1]:.1f}L{p1[0]:.1f} {p1[1]:.1f}" '
                 f'stroke="{AZUL}" stroke-width="1.1" opacity=".5" '
                 f'marker-end="url(#seta)"/>')
        o.append(modulo(a) + (modulo(b) if b else ""))
    return "".join(o)


def legenda(y, itens, x0=ML):
    o, x = [], x0
    for cor, rotulo, tipo in itens:
        if tipo == "circ":
            o.append(f'<circle cx="{x+5.5:.1f}" cy="{y+5.5:.1f}" r="5" fill="none" '
                     f'stroke="{cor}" stroke-width="1.5"/>')
        elif tipo == "linha":
            o.append(f'<line x1="{x:.1f}" y1="{y+5.5:.1f}" x2="{x+11:.1f}" '
                     f'y2="{y+5.5:.1f}" stroke="{cor}" stroke-width="4"/>')
        else:
            o.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="11" height="11" '
                     f'fill="{cor}" opacity=".55" stroke="{cor}"/>')
        o.append(livre(x + 16, y + 9, rotulo))
        x += 16 + len(rotulo) * 5.0 + 20
    return o


DEFS = ('<defs><marker id="seta" viewBox="0 0 10 10" refX="9" refY="5" '
        'markerWidth="5" markerHeight="5" orient="auto-start-reverse">'
        f'<path d="M0 0L10 5L0 10z" fill="{AZUL}" opacity=".6"/></marker>'
        '<pattern id="hach" width="6" height="6" patternUnits="userSpaceOnUse" '
        f'patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="6" '
        f'stroke="{VERDE}" stroke-width="1" opacity=".35"/></pattern></defs>')


def planta(titulo, subtitulo, r, divisorias=(), notas=()):
    """Planta de ocupacao em escala."""
    mb = 46 + 46 + len(notas) * 13 + 10
    _margens(mb)
    LG, AL = ML + W * S + MR, MT + H * S + mb
    o = [DEFS]

    pts = " ".join(f"{px(x, y)[0]:.1f},{px(x, y)[1]:.1f}" for x, y in FL.CONTORNO)
    o.append(f'<polygon points="{pts}" fill="#eef1f4"/>')

    for rect, motivo in r["reservas"]:
        if "recuo" in motivo:
            o.append(D.rect(*rect, fill="url(#hach)", stroke=VERDE,
                            stroke_width="0.9", stroke_dasharray="4 3"))
        elif "vestíbulo" in motivo:
            o.append(D.rect(*rect, fill=VERM, opacity=".10", stroke=VERM,
                            stroke_width="0.9", stroke_dasharray="3 3"))
            a, b = px(rect[0], rect[3]), px(rect[2], rect[3])
            o.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" '
                     f'y2="{b[1]:.1f}" stroke="{DIVISORIA}" stroke-width="4"/>')

    for d in divisorias:
        o.append(D.rect(*MM.ilha_rect(d["eixo"], d["fixo"], d["s0"], d["s1"]),
                        fill="none", stroke=DIVISORIA, stroke_width="0.8",
                        stroke_dasharray="2 4", opacity=".55"))
        if d["eixo"] == "h":
            a, b = px(d["s0"], d["fixo"]), px(d["s1"], d["fixo"])
        else:
            a, b = px(d["fixo"], d["s0"]), px(d["fixo"], d["s1"])
        o.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" '
                 f'y2="{b[1]:.1f}" stroke="{DIVISORIA}" stroke-width="4"/>')

    o.append(f'<polygon points="{pts}" fill="none" stroke="#1c2733" stroke-width="3.2"/>')

    for p in PB.numera():
        face = "recorte_v" if p["parede"] == "recorte" else p["parede"]
        cor = {"fechada": VERM, "catering": AZUL,
               "emergencia": VERDE}.get(p["estado"], SERVICO)
        a, b = px(*PB.ponto(p["parede"], p["a"])), px(*PB.ponto(p["parede"], p["b"]))
        o.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" '
                 f'y2="{b[1]:.1f}" stroke="{cor}" stroke-width="5.4"/>')
        mx, my = px(*PB.ponto(p["parede"], p["meio"]))
        f = FL.FACES[face]
        if f["eixo"] == "h":
            o.append(livre(mx, my + (16 if f["dentro"] > 0 else -8), p["num"],
                           9.5, "#1f2c3c", "700", "middle"))
        else:
            fora = 11 if f["dentro"] < 0 else -11
            o.append(livre(mx + fora, my + 3, p["num"], 9.5, "#1f2c3c", "700",
                           "start" if f["dentro"] < 0 else "end"))

    o.append(pares(r["modulos"]))
    o.append(txt(FL.RECORTE[2] / 2, FL.RECORTE[3] / 2, "fora do salão", "sub"))

    o.append(livre(ML, 20, titulo, 15, "#1f2c3c", "700"))
    o.append(livre(ML, 36, subtitulo, 9.5, "#5c6c80"))

    ex, ey = ML + W * S - 10 * S, MT - 20
    o.append(f'<line x1="{ex:.1f}" y1="{ey:.1f}" x2="{ex+10*S:.1f}" y2="{ey:.1f}" '
             f'stroke="#5c6c80" stroke-width="1"/>')
    for k in (0, 5, 10):
        o.append(f'<line x1="{ex+k*S:.1f}" y1="{ey-3:.1f}" x2="{ex+k*S:.1f}" '
                 f'y2="{ey+3:.1f}" stroke="#5c6c80" stroke-width="1"/>')
    o.append(livre(ex + 10 * S + 14, ey + 3, "10 m", 8, "#5c6c80"))

    ly = MT + H * S + 26
    o += legenda(ly, [(MESA_COR, "mesa de identificação (1,70 × 0,80 m) e 3 mesários",
                       "rect"), (AZUL, "mesa de votação, Ø 0,90 m", "circ")])
    o += legenda(ly + 20, [(AZUL, "corredor do par", "rect"),
                           (VERDE, "recuo de 3 m da saída de emergência", "rect"),
                           (DIVISORIA, "divisória exenta", "linha")])
    for i, n in enumerate(notas):
        o.append(livre(ML, ly + 46 + i * 13, n, 8, "#5c6c80"))
    return _svg(LG, AL, f"{titulo}: {subtitulo}", o)


# ------------------------------------------------------------------- reguas
def reguas(cenario, hipotese="prudente", a_min=MM.CORREDOR_MAX, esc_px=13.4):
    """Por que 78 m de parede livre so rendem 48 m de parede usada."""
    r = MM.roda(cenario, hipotese, a_min, ordem=MM.ORDEM)
    cortes, _ = MM.bloqueios(cenario, hipotese)
    fora = MM.sombras(cenario, hipotese, a_min)

    esq, topo, alt, salto = 132.0, 74.0, 17.0, 34.0
    LG = esq + W * esc_px + 92
    AL = topo + len(MM.ORDEM) * salto + 116
    o = [livre(esq - 108, 26, "AS RÉGUAS DE PAREDE", 14, "#1f2c3c", "700"),
         livre(esq - 108, 44, "Cada parede na mesma escala. Um par exige 6,30 m "
               "contínuos; abaixo disso só entra MRV avulsa, e só a partir de "
               "2,70 m. Por isso a soma dos pedaços não vira mesa.", 9.5,
               "#5c6c80")]

    cor_motivo = [("recuo", VERDE), ("vestíbulo", VERM), ("vão", SERVICO)]
    y = topo
    for face in MM.ORDEM:
        f = FL.FACES[face]
        L = f["s1"] - f["s0"]
        o.append(livre(esq - 10, y + 12, NOME_FACE[face], 9.5, "#1f2c3c", "600",
                       "end"))
        o.append(f'<rect x="{esq:.1f}" y="{y:.1f}" width="{L*esc_px:.1f}" '
                 f'height="{alt}" fill="#fff" stroke="#5c6c80" stroke-width="0.7" '
                 'opacity=".85"/>')
        faixas = [(a, b, next((c for k, c in cor_motivo if k in mo), SERVICO))
                  for a, b, mo in cortes.get(face, [])]
        faixas += [(a, b, VIZINHA) for a, b in fora.get(face, [])]
        for a, b, cor in faixas:
            a, b = max(f["s0"], a), min(f["s1"], b)
            if b > a:
                o.append(f'<rect x="{esq+(a-f["s0"])*esc_px:.1f}" y="{y:.1f}" '
                         f'width="{(b-a)*esc_px:.1f}" height="{alt}" fill="{cor}" '
                         'opacity=".32"/>')
        mods = [m for m in r["modulos"] if m["face"] == face]
        for grupo in agrupa(mods):
            avulsa = len(grupo) == 1
            s0 = min(m["s"] for m in grupo) - MM.LARG / 2
            s1 = max(m["s"] for m in grupo) + MM.LARG / 2
            if avulsa:                       # o modulo mais o corredor que sobra
                s1 = s0 + MM.LARG + MM.MESARIO_ASSENTO + MM.FOLGA_ASSENTO \
                    + grupo[0]["corredor"]
            o.append(f'<rect x="{esq+(s0-f["s0"])*esc_px:.1f}" y="{y+2:.1f}" '
                     f'width="{(s1-s0)*esc_px:.1f}" height="{alt-4}" '
                     f'fill="{AZUL}" opacity="{".38" if avulsa else ".78"}"/>')
        n = len(mods)
        o.append(livre(esq + L * esc_px + 10, y + 12,
                       "—" if not n else f"{n} mesa" + ("s" if n > 1 else ""),
                       9.5, "#1f2c3c" if n else "#5c6c80", "600" if n else None))
        y += salto

    o.append(f'<line x1="{esq:.1f}" y1="{y+4:.1f}" x2="{esq+10*esc_px:.1f}" '
             f'y2="{y+4:.1f}" stroke="#5c6c80" stroke-width="1"/>')
    for k in (0, 5, 10):
        o.append(f'<line x1="{esq+k*esc_px:.1f}" y1="{y+1:.1f}" '
                 f'x2="{esq+k*esc_px:.1f}" y2="{y+7:.1f}" stroke="#5c6c80" '
                 'stroke-width="1"/>')
    o.append(livre(esq + 10 * esc_px + 12, y + 7, "10 m", 8, "#5c6c80"))

    itens = [(AZUL, "par de mesas (6,30 m)", "rect"),
             (VERDE, "recuo de saída de emergência", "rect"),
             (SERVICO, "vão de porta e sua folga", "rect"),
             (VIZINHA, "canto ou recuo da parede vizinha", "rect")]
    if cenario == "B":
        itens.append((VERM, "vestíbulo da divisória", "rect"))
    o += legenda(y + 26, itens, x0=esq - 108)
    o.append(f'<rect x="{esq-108:.1f}" y="{y+46:.1f}" width="11" height="11" '
             f'fill="{AZUL}" opacity=".26" stroke="{AZUL}" stroke-opacity=".5"/>')
    o.append(livre(esq - 92, y + 55, "MRV avulsa (2,79 m, corredor de 1,09 m)"))
    return _svg(LG, AL, f"As réguas de parede do cenário {cenario}", o)


# ---------------------------------------------------- figura do modulo isolado
def figura_modulo(e=52.0):
    """Um par de mesas receptoras visto de cima, com as cotas."""
    esq, topo = 96.0, 84.0
    util = 2 * MM.LARG + MM.CORREDOR_MAX + MM.ENTRE_PARES + MM.LARG   # 7,20 m
    LG, AL = esq + util * e + 306, topo + MM.PROF * e + 126

    def x(vl): return esq + vl * e
    def y(vl): return topo + vl * e

    o = ['<defs><marker id="s2" viewBox="0 0 10 10" refX="9" refY="5" '
         'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
         f'<path d="M0 0L10 5L0 10z" fill="{AZUL}"/></marker>'
         '<marker id="cota" viewBox="0 0 10 10" refX="5" refY="5" '
         'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
         '<path d="M2 2L8 5L2 8z" fill="#5c6c80"/></marker></defs>',
         f'<rect x="{x(0):.1f}" y="{y(0):.1f}" width="{util*e:.1f}" '
         f'height="{MM.PROF*e:.1f}" fill="#eef1f4"/>',
         f'<line x1="{x(-0.25):.1f}" y1="{y(0):.1f}" x2="{x(util+0.25):.1f}" '
         f'y2="{y(0):.1f}" stroke="#1c2733" stroke-width="6"/>',
         livre(x(util / 2), y(0) - 16,
               "PAREDE · as urnas ficam sempre voltadas para ela", 10.5,
               "#1f2c3c", "700", "middle"),
         f'<rect x="{x(MM.LARG):.1f}" y="{y(0):.1f}" '
         f'width="{MM.CORREDOR_MAX*e:.1f}" height="{MM.PROF*e:.1f}" '
         f'fill="{AZUL}" opacity=".07"/>']

    centros = [MM.LARG / 2, MM.LARG + MM.CORREDOR_MAX + MM.LARG / 2,
               2 * MM.LARG + MM.CORREDOR_MAX + MM.ENTRE_PARES + MM.LARG / 2]
    for c, lado, op in zip(centros, (+1, -1, +1), ("1", "1", ".34")):
        g = [f'<rect x="{x(c-MM.MESA_IDENT[1]/2):.1f}" y="{y(2.40):.1f}" '
             f'width="{MM.MESA_IDENT[1]*e:.1f}" height="{MM.MESA_IDENT[0]*e:.1f}" '
             f'fill="{MESA_COR}" opacity=".85"/>']
        cy = MM.FOLGA_ELEITOR + MM.URNA_D / 2
        g.append(f'<circle cx="{x(c):.1f}" cy="{y(cy):.1f}" '
                 f'r="{MM.URNA_D/2*e:.1f}" fill="#fff" stroke="{AZUL}" '
                 'stroke-width="2"/>')
        g.append(f'<rect x="{x(c-0.18):.1f}" y="{y(cy-0.20):.1f}" '
                 f'width="{0.36*e:.1f}" height="{0.30*e:.1f}" fill="{AZUL}" '
                 'opacity=".7"/>')
        g.append(f'<circle cx="{x(c):.1f}" cy="{y(MM.FOLGA_ELEITOR/2):.1f}" '
                 f'r="{0.24*e:.1f}" fill="none" stroke="{PESSOA}" stroke-width="1.6"/>')
        for k in range(3):
            g.append(f'<circle cx="{x(c + lado*(MM.MESA_IDENT[1]/2+0.26)):.1f}" '
                     f'cy="{y(2.40+0.283+k*0.567):.1f}" r="{0.24*e:.1f}" '
                     f'fill="{PESSOA}" opacity=".6"/>')
        o.append(f'<g opacity="{op}">' + "".join(g) + "</g>")

    xc = x(MM.LARG + MM.CORREDOR_MAX / 2)
    o.append(f'<path d="M{xc-9:.1f} {y(MM.PROF)+22:.1f}L{xc-9:.1f} {y(1.55):.1f}" '
             f'stroke="{AZUL}" stroke-width="2" marker-end="url(#s2)"/>')
    o.append(f'<path d="M{xc+9:.1f} {y(1.55):.1f}L{xc+9:.1f} {y(MM.PROF)+22:.1f}" '
             f'stroke="{AZUL}" stroke-width="2" opacity=".45" marker-end="url(#s2)"/>')
    o.append(livre(xc, y(MM.PROF) + 38, "entra · sai", 9.5, AZUL, "600", "middle"))

    cx = x(util) + 30
    for a, b, rot in ((0, MM.FOLGA_ELEITOR, "0,90 · eleitor votando"),
                      (MM.FOLGA_ELEITOR, MM.FOLGA_ELEITOR + MM.URNA_D,
                       "0,90 · mesa de votação"),
                      (MM.FOLGA_ELEITOR + MM.URNA_D, 2.40, "0,60 · passagem"),
                      (2.40, MM.PROF, "1,70 · mesa de identificação")):
        o.append(f'<path d="M{cx:.1f} {y(a):.1f}L{cx:.1f} {y(b):.1f}" '
                 'stroke="#5c6c80" stroke-width="0.9" marker-start="url(#cota)" '
                 'marker-end="url(#cota)"/>')
        o.append(livre(cx + 8, y((a + b) / 2) + 3, rot, 9, "#5c6c80"))
    o.append(f'<path d="M{cx+168:.1f} {y(0):.1f}L{cx+168:.1f} {y(MM.PROF):.1f}" '
             'stroke="#1f2c3c" stroke-width="1" marker-start="url(#cota)" '
             'marker-end="url(#cota)"/>')
    o.append(f'<text x="{cx+182:.1f}" y="{y(MM.PROF/2):.1f}" {D.FONTE} '
             f'font-size="9.5" fill="#1f2c3c" font-weight="600" '
             f'text-anchor="middle" transform="rotate(-90 {cx+182:.1f} '
             f'{y(MM.PROF/2):.1f})">4,10 m de profundidade</text>')

    cy2 = y(MM.PROF) + 58
    for a, b, rot in ((0, MM.LARG, "0,90"),
                      (MM.LARG, MM.LARG + MM.CORREDOR_MAX,
                       "corredor do par · 2,50 a 3,00"),
                      (MM.LARG + MM.CORREDOR_MAX, 2 * MM.LARG + MM.CORREDOR_MAX, "0,90"),
                      (2 * MM.LARG + MM.CORREDOR_MAX,
                       2 * MM.LARG + MM.CORREDOR_MAX + MM.ENTRE_PARES,
                       "entre pares · 1,50")):
        o.append(f'<path d="M{x(a):.1f} {cy2:.1f}L{x(b):.1f} {cy2:.1f}" '
                 'stroke="#5c6c80" stroke-width="0.9" marker-start="url(#cota)" '
                 'marker-end="url(#cota)"/>')
        o.append(livre(x((a + b) / 2), cy2 + 14, rot, 9, "#5c6c80", None, "middle"))
    tot = 2 * MM.LARG + MM.CORREDOR_MAX + MM.ENTRE_PARES
    o.append(f'<path d="M{x(0):.1f} {cy2+30:.1f}L{x(tot):.1f} {cy2+30:.1f}" '
             'stroke="#1f2c3c" stroke-width="1" marker-start="url(#cota)" '
             'marker-end="url(#cota)"/>')
    o.append(livre(x(tot / 2), cy2 + 44, "passo do par: 5,80 a 6,30 m de parede "
                   "para duas mesas receptoras", 9.5, "#1f2c3c", "600", "middle"))

    o.insert(0, livre(esq, 26, "O MÓDULO — uma mesa receptora de votos, e o par",
                      15, "#1f2c3c", "700"))
    o.insert(1, livre(esq, 44, "Vista de cima. Os mesários do par ficam de frente "
                      "uns para os outros; o par seguinte fica de costas.", 9.5,
                      "#5c6c80"))
    return _svg(LG, AL, "O módulo da mesa receptora de votos, com as cotas", o)


# --------------------------------------------------- a parede leste de perto
def _mod_leste(x, topo, e, n=1, corredor=None, cor=AZUL, op=".85"):
    """Um modulo visto de lado: profundidade para baixo, a partir da parede."""
    o = []
    for k in range(n):
        xk = x + k * ((MM.LARG + corredor) * e if corredor else 0)
        o.append(f'<rect x="{xk:.1f}" y="{topo+(MM.FOLGA_ELEITOR+MM.URNA_D+MM.PASSAGEM)*e:.1f}" '
                 f'width="{MM.LARG*e:.1f}" height="{MM.MESA_IDENT[0]*e:.1f}" '
                 f'fill="{MESA_COR}" opacity="{op}"/>')
        o.append(f'<circle cx="{xk+MM.LARG*e/2:.1f}" '
                 f'cy="{topo+(MM.FOLGA_ELEITOR+MM.URNA_D/2)*e:.1f}" '
                 f'r="{MM.URNA_D/2*e:.1f}" fill="none" stroke="{cor}" '
                 f'stroke-width="1.4" opacity="{op}"/>')
    return "".join(o)


def compara_leste(e=25.0):
    """As tres leituras possiveis da parede leste, na mesma escala."""
    esq, topo, banda = 210.0, 96.0, 152.0
    L = FL.HALL_H
    portas = FL.portas_da_face("leste")
    LG, AL = esq + L * e + 108, topo + 3 * banda + 74

    def x(v): return esq + v * e

    o = [livre(28, 28, "A PAREDE LESTE, DE PERTO", 14, "#1f2c3c", "700"),
         livre(28, 46, "Os 44,40 m da fachada, nas três leituras do recuo de 3 m. "
               "As quatro saídas de emergência L1 a L4 estão em verde.", 9.5,
               "#5c6c80"),
         livre(28, 60, "Um par de mesas ocupa 6,30 m de parede; uma MRV avulsa, "
               "2,70 m.", 9.5, "#5c6c80")]

    linhas = [
        ("recuo de 3 m dos dois lados", "o que o modelo aplica hoje", 3.0),
        ("recuo de 3 m só à frente do vão", "sem afastamento lateral", 0.0),
    ]

    for i, (titulo, sub, lat) in enumerate(linhas):
        y = topo + i * banda
        o.append(livre(28, y + 14, titulo, 10.5, "#1f2c3c", "600"))
        o.append(livre(28, y + 28, sub, 9, "#5c6c80"))

        livres = [(0.0, L)]
        for _c, a, b in portas:
            livres = FL.subtrai(livres, (a - lat, b + lat))
        if lat:
            for _c, a, b in portas:
                o.append(f'<rect x="{x(max(0, a-lat)):.1f}" y="{y+34:.1f}" '
                         f'width="{(min(L, b+lat)-max(0, a-lat))*e:.1f}" '
                         f'height="{MM.RECUO_FRONTAL*e:.1f}" fill="url(#hach)" '
                         f'stroke="{VERDE}" stroke-width="0.8" '
                         'stroke-dasharray="4 3"/>')

        total = 0
        for a, b in livres:
            n, corr, sobra, av, corr_av = MM.ocupa_trecho(
                b - a, MM.CORREDOR_MIN, MM.CORREDOR_MAX, avulsa=True)
            s = a + sobra / 2
            for _k in range(n):
                o.append(_mod_leste(x(s), y + 34, e, 2, corr))
                s += MM.passo_do_par(corr)
            if av:
                o.append(_mod_leste(x(a), y + 34, e, 1, None, AZUL, ".45"))
            total += 2 * n + av
        o.append(f'<line x1="{x(0):.1f}" y1="{y+34:.1f}" x2="{x(L):.1f}" '
                 f'y2="{y+34:.1f}" stroke="#1c2733" stroke-width="3.4"/>')
        for _c, a, b in portas:
            o.append(f'<line x1="{x(a):.1f}" y1="{y+34:.1f}" x2="{x(b):.1f}" '
                     f'y2="{y+34:.1f}" stroke="{VERDE}" stroke-width="5.4"/>')
        o.append(livre(x(L) + 12, y + 40, f"{total} mesas", 11, "#1f2c3c", "700"))

    # terceira faixa: a fita continua do modelo do colega
    y = topo + 2 * banda
    o.append(livre(28, y + 14, "a fita contínua do modelo", 10.5, "#1f2c3c", "600"))
    o.append(livre(28, y + 28, "14 mesas, como no desenho", 9, "#5c6c80"))
    passo = MM.passo_do_par(MM.CORREDOR_MAX)
    usado = 7 * passo - MM.ENTRE_PARES
    s = (L - usado) / 2
    for _k in range(7):
        o.append(_mod_leste(x(s), y + 34, e, 2, MM.CORREDOR_MAX, VERM))
        s += passo
    o.append(f'<line x1="{x(0):.1f}" y1="{y+34:.1f}" x2="{x(L):.1f}" '
             f'y2="{y+34:.1f}" stroke="#1c2733" stroke-width="3.4"/>')
    for _c, a, b in portas:
        o.append(f'<line x1="{x(a):.1f}" y1="{y+34:.1f}" x2="{x(b):.1f}" '
                 f'y2="{y+34:.1f}" stroke="{VERDE}" stroke-width="5.4"/>')
        o.append(f'<rect x="{x(a):.1f}" y="{y+34:.1f}" width="{(b-a)*e:.1f}" '
                 f'height="{MM.RECUO_FRONTAL*e:.1f}" fill="{VERM}" opacity=".16"/>')
    o.append(livre(x(L) + 12, y + 40, "14 mesas", 11, VERM, "700"))
    o.append(livre(x(0), y + 34 + MM.PROF * e + 16,
                   f"7 pares × 6,30 m = {usado:.2f} m".replace(".", ",")
                   + f" de parede, e a fachada tem {L:.2f} m".replace(".", ",")
                   + ". Sobram 1,80 m — menos que um vão de porta. As quatro "
                     "saídas ficam por baixo das mesas.", 9, VERM))

    o.append(f'<line x1="{x(0):.1f}" y1="{AL-40:.1f}" x2="{x(10):.1f}" '
             f'y2="{AL-40:.1f}" stroke="#5c6c80" stroke-width="1"/>')
    for k in (0, 5, 10):
        o.append(f'<line x1="{x(k):.1f}" y1="{AL-43:.1f}" x2="{x(k):.1f}" '
                 f'y2="{AL-37:.1f}" stroke="#5c6c80" stroke-width="1"/>')
    o.append(livre(x(10) + 12, AL - 37, "10 m", 8, "#5c6c80"))
    o.insert(0, DEFS)
    return _svg(LG, AL, "A parede leste nas tres leituras do recuo de 3 m", o)
