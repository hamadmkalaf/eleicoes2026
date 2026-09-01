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

NOME_FACE = {"norte": "norte", "leste": "fachada leste", "sul": "sul",
             "oeste": "oeste", "recorte_h": "recorte (face norte)",
             "recorte_v": "recorte (face leste)",
             MM.FACE_LESTE_RECUADA: "leste, fileira recuada"}

# A regua mostra tambem a fachada leste em si, que nao recebe modulo nenhum:
# e ela que carrega a faixa protegida de 3 m.
ORDEM_REGUA = ["norte", "recorte_h", "oeste", "sul", "leste",
               MM.FACE_LESTE_RECUADA, "recorte_v"]


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


def vg(x, casas=2):
    """Numero no padrao brasileiro. Nunca aplicar .replace num f-string
    concatenado: literais adjacentes viram um so, e o ponto final da frase
    tambem vira virgula."""
    return f"{x:.{casas}f}".replace(".", ",")


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
        if "recuo" in motivo or "faixa protegida" in motivo:
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
                           (VERDE, "zona protegida de 3 m: faixa da fachada leste "
                                   "e recuo das saídas de emergência", "rect"),
                           (DIVISORIA, "divisória", "linha")])
    for i, n in enumerate(notas):
        o.append(livre(ML, ly + 46 + i * 13, n, 8, "#5c6c80"))
    return _svg(LG, AL, f"{titulo}: {subtitulo}", o)


# ------------------------------------------------------------------- reguas
def reguas(cenario, hipotese="prudente", a_min=MM.CORREDOR_MAX, esc_px=13.4,
           ajustes=None):
    """Onde a frente vem em pedacos, e onde vem inteira."""
    r = MM.roda(cenario, hipotese, a_min, ordem=MM.ORDEM, ajustes=ajustes)
    cortes, _ = MM.bloqueios(cenario, hipotese)
    fora = MM.sombras(cenario, hipotese, a_min)
    _ = ajustes

    esq, topo, alt, salto = 132.0, 88.0, 17.0, 34.0
    LG = esq + W * esc_px + 92
    AL = topo + len(ORDEM_REGUA) * salto + 116
    o = [livre(esq - 108, 26, "AS RÉGUAS DE PAREDE", 14, "#1f2c3c", "700"),
         livre(esq - 108, 44, "Cada face na mesma escala. Um par exige de 5,30 a "
               "6,30 m contínuos — por isso a soma dos pedaços não vira mesa.",
               9.5, "#5c6c80"),
         livre(esq - 108, 58, "A fachada leste não recebe módulo: é ela que carrega "
               "a faixa protegida. A fileira que vem depois dela é a linha seguinte.",
               9.5, "#5c6c80")]

    cor_motivo = [("recuo", VERDE), ("protegida", VERDE),
                  ("vestíbulo", VERM), ("vão", SERVICO)]
    y = topo
    for face in ORDEM_REGUA:
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

    itens = [(AZUL, "par de mesas", "rect"),
             (VERDE, "zona protegida de 3 m", "rect"),
             (SERVICO, "vão de porta e sua folga", "rect"),
             (VIZINHA, "canto ou recuo da parede vizinha", "rect")]
    if cenario == "B":
        itens.append((VERM, "vestíbulo da divisória", "rect"))
    o += legenda(y + 26, itens, x0=esq - 108)
    if any(m["par"] is None for m in r["modulos"]):
        o.append(f'<rect x="{esq-108:.1f}" y="{y+46:.1f}" width="11" height="11" '
                 f'fill="{AZUL}" opacity=".26" stroke="{AZUL}" stroke-opacity=".5"/>')
        o.append(livre(esq - 92, y + 55, "MRV avulsa"))
    return _svg(LG, AL, f"As réguas de parede do cenário {cenario}", o)


# ---------------------------------------------------- figura do modulo isolado
def figura_modulo(e=52.0):
    """Um par de mesas receptoras visto de cima, com as cotas."""
    esq, topo = 96.0, 84.0
    util = 2 * MM.LARG + MM.CORREDOR_MAX + MM.ENTRE_PARES_MAX + MM.LARG   # 7,20 m
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
               2 * MM.LARG + MM.CORREDOR_MAX + MM.ENTRE_PARES_MAX + MM.LARG / 2]
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
                       2 * MM.LARG + MM.CORREDOR_MAX + MM.ENTRE_PARES_MAX,
                       "entre pares · 1,00 a 1,50")):
        o.append(f'<path d="M{x(a):.1f} {cy2:.1f}L{x(b):.1f} {cy2:.1f}" '
                 'stroke="#5c6c80" stroke-width="0.9" marker-start="url(#cota)" '
                 'marker-end="url(#cota)"/>')
        o.append(livre(x((a + b) / 2), cy2 + 14, rot, 9, "#5c6c80", None, "middle"))
    tot = 2 * MM.LARG + MM.CORREDOR_MAX + MM.ENTRE_PARES_MAX
    o.append(f'<path d="M{x(0):.1f} {cy2+30:.1f}L{x(tot):.1f} {cy2+30:.1f}" '
             'stroke="#1f2c3c" stroke-width="1" marker-start="url(#cota)" '
             'marker-end="url(#cota)"/>')
    o.append(livre(x(tot / 2), cy2 + 44, "passo do par: 5,30 a 6,30 m de frente "
                   "para duas mesas receptoras", 9.5, "#1f2c3c", "600", "middle"))

    o.insert(0, livre(esq, 26, "O MÓDULO — uma mesa receptora de votos, e o par",
                      15, "#1f2c3c", "700"))
    o.insert(1, livre(esq, 44, "Vista de cima. Os mesários do par ficam de frente "
                      "uns para os outros; o par seguinte fica de costas.", 9.5,
                      "#5c6c80"))
    return _svg(LG, AL, "O módulo da mesa receptora de votos, com as cotas", o)


# --------------------------------------------------- a fachada leste de perto
def _mod_leste(x, topo, e, n=1, corredor=None, cor=AZUL, op=".85", recuo=0.0):
    """Modulos vistos de lado: a profundidade cresce para baixo, a partir de
    `recuo` metros da parede."""
    o = []
    u0 = recuo
    for k in range(n):
        xk = x + k * ((MM.LARG + corredor) * e if corredor else 0)
        o.append(f'<rect x="{xk:.1f}" '
                 f'y="{topo+(u0+MM.FOLGA_ELEITOR+MM.URNA_D+MM.PASSAGEM)*e:.1f}" '
                 f'width="{MM.LARG*e:.1f}" height="{MM.MESA_IDENT[0]*e:.1f}" '
                 f'fill="{MESA_COR}" opacity="{op}"/>')
        o.append(f'<circle cx="{xk+MM.LARG*e/2:.1f}" '
                 f'cy="{topo+(u0+MM.FOLGA_ELEITOR+MM.URNA_D/2)*e:.1f}" '
                 f'r="{MM.URNA_D/2*e:.1f}" fill="none" stroke="{cor}" '
                 f'stroke-width="1.4" opacity="{op}"/>')
        o.append(f'<circle cx="{xk+MM.LARG*e/2:.1f}" '
                 f'cy="{topo+(u0+MM.FOLGA_ELEITOR/2)*e:.1f}" '
                 f'r="{0.22*e:.1f}" fill="none" stroke="{PESSOA}" '
                 f'stroke-width="1" opacity="{op}"/>')
    return "".join(o)


def compara_leste(e=21.0):
    """A fachada leste encostada e recuada, na mesma escala."""
    esq, topo, banda = 208.0, 116.0, 226.0
    L = FL.HALL_H
    portas = FL.portas_da_face("leste")
    LG, AL = esq + L * e + 116, topo + 2 * banda + 118

    def x(v): return esq + v * e

    o = [DEFS,
         livre(28, 30, "A FACHADA LESTE — ENCOSTADA OU RECUADA", 14, "#1f2c3c", "700"),
         livre(28, 48, "Os 44,40 m da fachada vistos de lado: a parede em cima, a "
               "profundidade do salão para baixo. As quatro saídas de emergência "
               "L1 a L4 estão em verde.", 11, "#5c6c80"),
         livre(28, 64, "O módulo tem 4,10 m de profundidade e 0,90 m de frente; um "
               "par ocupa 5,30 a 6,30 m de frente.", 11, "#5c6c80")]

    # ---- faixa 1: encostada, com recuo de 3 m dos dois lados de cada vao
    y = topo
    o.append(livre(28, y + 14, "encostada na parede", 12, "#1f2c3c", "600"))
    o.append(livre(28, y + 28, "com recuo de 3 m dos", 10.5, "#5c6c80"))
    o.append(livre(28, y + 40, "dois lados de cada vão", 10.5, "#5c6c80"))
    livres = [(0.0, L)]
    for _c, a, b in portas:
        livres = FL.subtrai(livres, (a - 3.0, b + 3.0))
    for _c, a, b in portas:
        o.append(f'<rect x="{x(max(0, a-3)):.1f}" y="{y+34:.1f}" '
                 f'width="{(min(L, b+3)-max(0, a-3))*e:.1f}" '
                 f'height="{MM.FAIXA_LESTE*e:.1f}" fill="url(#hach)" '
                 f'stroke="{VERDE}" stroke-width="0.8" stroke-dasharray="4 3"/>')
    total = 0
    for a, b in livres:
        n, corr, _entre, sobra, av, _ca = MM.ocupa_trecho(
            b - a, MM.CORREDOR_MIN, MM.CORREDOR_MAX, avulsa=True)
        if av:
            o.append(_mod_leste(x(a), y + 34, e, 1, None, AZUL, ".45"))
        total += 2 * n + av
    o.append(f'<line x1="{x(0):.1f}" y1="{y+34:.1f}" x2="{x(L):.1f}" '
             f'y2="{y+34:.1f}" stroke="#1c2733" stroke-width="3.4"/>')
    for _c, a, b in portas:
        o.append(f'<line x1="{x(a):.1f}" y1="{y+34:.1f}" x2="{x(b):.1f}" '
                 f'y2="{y+34:.1f}" stroke="{VERDE}" stroke-width="5.4"/>')
    o.append(livre(x(L) + 12, y + 40, f"{total} mesas", 11, "#5c6c80", "700"))
    o.append(livre(x(0), y + 34 + 3.0 * e + 44,
                   "Os envelopes de 3 m em volta dos quatro vãos deixam três "
                   "trechos de 2,79 m. Não cabe par; cabe uma MRV sozinha em cada.",
                   9, "#5c6c80"))

    # ---- faixa 2: recuada 3 m, fileira continua
    y = topo + banda
    r = MM.roda("A", "prudente", MM.CORREDOR_MAX, ordem=MM.ORDEM,
                ajustes=MM.AJUSTE_28)
    tr = [t for t in r["por_face"][MM.FACE_LESTE_RECUADA]["trechos"] if t["pares"]]
    o.append(livre(28, y + 14, "recuada 3 m da parede", 12, "#1f2c3c", "600"))
    o.append(livre(28, y + 28, "faixa protegida contínua", 10.5, "#5c6c80"))
    o.append(livre(28, y + 40, "ao longo de toda a fachada", 10.5, "#5c6c80"))
    o.append(f'<rect x="{x(0):.1f}" y="{y+34:.1f}" width="{L*e:.1f}" '
             f'height="{MM.FAIXA_LESTE*e:.1f}" fill="url(#hach)" '
             f'stroke="{VERDE}" stroke-width="0.8" stroke-dasharray="4 3"/>')
    total = 0
    for t in tr:
        s0 = t["s0"] + t["sobra"] / 2
        for _k in range(t["pares"]):
            o.append(_mod_leste(x(s0), y + 34, e, 2, t["corredor"],
                                recuo=MM.FAIXA_LESTE))
            s0 += MM.passo_do_par(t["corredor"], t["entre_pares"] or 0)
        total += 2 * t["pares"]
    o.append(f'<line x1="{x(0):.1f}" y1="{y+34:.1f}" x2="{x(L):.1f}" '
             f'y2="{y+34:.1f}" stroke="#1c2733" stroke-width="3.4"/>')
    for _c, a, b in portas:
        o.append(f'<line x1="{x(a):.1f}" y1="{y+34:.1f}" x2="{x(b):.1f}" '
                 f'y2="{y+34:.1f}" stroke="{VERDE}" stroke-width="5.4"/>')
    o.append(livre(x(L) + 12, y + 40, f"{total} mesas", 11, "#1f2c3c", "700"))
    t0 = tr[0]
    # cotas no primeiro par, para o olho nao ler o espacamento ao contrario
    s0 = t0["s0"] + t0["sobra"] / 2
    yc = y + 34 + (MM.FAIXA_LESTE + MM.PROF) * e + 12
    for a0, b0, rot, dy in ((s0 + MM.LARG, s0 + MM.LARG + t0["corredor"],
                             f"{vg(t0['corredor'])} no par", 13),
                            (s0 + 2 * MM.LARG + t0["corredor"],
                             s0 + 2 * MM.LARG + t0["corredor"] + t0["entre_pares"],
                             f"{vg(t0['entre_pares'])} entre pares", 26)):
        o.append(f'<path d="M{x(a0):.1f} {yc:.1f}L{x(b0):.1f} {yc:.1f}" '
                 f'stroke="{AZUL}" stroke-width="0.9" opacity=".8"/>')
        for xx in (x(a0), x(b0)):
            o.append(f'<line x1="{xx:.1f}" y1="{yc-3:.1f}" x2="{xx:.1f}" '
                     f'y2="{yc+3:.1f}" stroke="{AZUL}" stroke-width="0.9" opacity=".8"/>')
        o.append(livre(x((a0 + b0) / 2), yc + dy, rot, 9.5, AZUL, None, "middle"))
    base = y + 34 + (MM.FAIXA_LESTE + MM.PROF) * e
    o.append(livre(x(0), base + 60,
                   "A faixa de 3 m corre a fachada inteira e liga as quatro saídas: "
                   "nada é montado nela e nenhuma fila se forma.", 10.5, "#1f2c3c"))
    o.append(livre(x(0), base + 74,
                   "Como a fileira não encosta na parede, os vãos deixam de "
                   f"recortá-la — {t0['pares']} pares alinhados em "
                   f"{vg(t0['livre'])} m.", 10.5, "#1f2c3c"))
    o.append(livre(x(0), base + 88,
                   "A urna fica voltada para a fachada e o eleitor se põe entre ela "
                   "e a faixa protegida: a tela aponta para a parede e não é vista "
                   "do salão.", 10.5, "#5c6c80"))

    ey = topo - 22
    ex0 = x(L) - 10 * e
    o.append(f'<line x1="{ex0:.1f}" y1="{ey:.1f}" x2="{x(L):.1f}" y2="{ey:.1f}" '
             'stroke="#5c6c80" stroke-width="1"/>')
    for k in (0, 5, 10):
        o.append(f'<line x1="{ex0+k*e:.1f}" y1="{ey-3:.1f}" x2="{ex0+k*e:.1f}" '
                 f'y2="{ey+3:.1f}" stroke="#5c6c80" stroke-width="1"/>')
    o.append(livre(x(L) + 12, ey + 3, "10 m", 8, "#5c6c80"))
    return _svg(LG, AL, "A fachada leste encostada e recuada", o)
