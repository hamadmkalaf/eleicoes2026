"""Layout do Ring 3: tres corredores serpenteados, baias de reserva e barreiras.

Desenho definido pelo Posto:
  - acesso pelo canto SUDESTE;
  - corredor estreito de distribuicao no "fundo" (bordo sul), de leste a oeste;
  - tres serpenteados ("Disney queue") dele derivados, de oeste para leste:
    ENTRADA A -> porta S4, ENTRADA B -> S5, ENTRADA C -> S6;
  - S2 e S8 reservadas como SAIDA, nos flancos, fora do vao das entradas.

RESERVA POR ENTRADA. A reserva nao e um deposito comum: cada entrada tem a sua,
porque o eleitor so vota na urna da sua secao e misturar as filas destroi o
roteamento feito na pre-triagem. As baias de flanco sao DEDICADAS — a oeste
serve so a entrada A, a leste so a C — e cada uma encosta na baliza de ENTRADA
do seu bloco, drenando direto para dentro dele, sem passar pelo corredor de
fundo. Por isso o bloco A e espelhado: sua baliza de entrada fica a oeste,
encostada na baia.

A entrada B fica no meio, com corredor de egresso dos dois lados, e nao tem
flanco. Em vez de uma baia, recebe DUAS BALIZAS A MAIS de profundidade de fila.

Piso pavimentado. Espaco locado desde a vespera, sem carros a remover.

TODO O CALCULO DE BARREIRA AQUI E SO DO RING 3. O interior do Hall 2 tem
necessidade propria, ainda nao dimensionada.

Gera saidas/layout_ring3.svg (fonte) e saidas/layout_ring3.png (visualizacao).
Uso:  python3 scripts/layout_ring3.py
"""

import math
import xml.etree.ElementTree as ET
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "saidas" / "layout_ring3.svg"
SAIDA_PNG = RAIZ / "saidas" / "layout_ring3.png"

# --- fachada sul do Hall 2 -------------------------------------------------
# metros do canto sudoeste, lidos na prancheta do Posto e convertidos pela
# largura declarada de 50,2 m (escala aferida ~22,5 px/m).
PORTAS_SUL = {
    "S1": 9.5, "S2": 13.7, "S3": 17.7, "S4": 21.9, "S5": 28.1,
    "S6": 34.3, "S7": 38.6, "S8": 42.6, "S9": 46.8,
}
ENTRADAS = [("A", "S4"), ("B", "S5"), ("C", "S6")]
SAIDAS_PORTAS = ["S2", "S8"]
PASSO_PORTAS = PORTAS_SUL["S5"] - PORTAS_SUL["S4"]      # 6,2 m

# --- Ring 3 (fotogrametria, +-10-15% linear) -------------------------------
LARGURA = 39.0          # leste-oeste, m
PROFUNDIDADE = 35.0     # sul-norte, m; o norte encara o Hall 2

FOLGA_SUL = 1.5
CORREDOR_FUNDO = 2.5    # corredor de distribuicao
ZONA_DESCARGA = 5.0     # leque convergente ate as portas

LARG_BALIZA = 1.40
PASSO_PESSOA = 0.50
CORREDOR_EGRESSO = 2.6  # vao livre entre blocos vizinhos
LARG_FLANCO = 5.0       # baia de reserva dedicada, em cada flanco
DENS_BAIA = 1.5         # pessoas/m2 na baia, sob marshal, sem balizas
VAO_ACESSO = 1.5        # largura de cada vao controlado

METROS_POR_UNIDADE = 2.0
ALTURA_SEPARADOR = 1.0
EUR_POR_METRO = 6.51
SEPARADORES_EM_MAOS = 200      # fornecidos pela organizadora do evento

# Balizas por bloco (A, B, C), todas impares: entra-se pelo sul e a ultima
# baliza precisa correr para o norte, onde ficam as portas.
# B recebe 7 por ser o unico corredor sem baia de flanco.
BALIZAS = (5, 7, 5)
# Bloco A espelhado: entra pela baliza OESTE, encostada na sua baia de flanco,
# e sai pela leste, que cai sobre S4.
ESPELHADO = (True, False, False)
# Baia de flanco de cada entrada: oeste serve A, leste serve C, B nao tem.
BAIA_DE = ("A", None, "C")

PROF_SERPENTE = PROFUNDIDADE - FOLGA_SUL - CORREDOR_FUNDO - ZONA_DESCARGA
LARG_BLOCOS = tuple(n * LARG_BALIZA for n in BALIZAS)


def eixos():
    """Eixos dos blocos e das portas, em metros do bordo oeste do Ring 3."""
    centro = LARGURA / 2
    eb, x = [], LARG_FLANCO
    for larg in LARG_BLOCOS:
        eb.append(x + larg / 2)
        x += larg + CORREDOR_EGRESSO
    return eb, [centro - PASSO_PORTAS, centro, centro + PASSO_PORTAS]


def _saida_rel(i):
    """Posicao da baliza de saida do bloco i, relativa ao seu eixo."""
    d = LARG_BLOCOS[i] / 2 - LARG_BALIZA / 2
    return d if ESPELHADO[i] else -d


def _entrada_rel(i):
    return -_saida_rel(i)


def desvios():
    """Deslocamento da baliza de saida de cada bloco ate a sua porta."""
    eb, ep = eixos()
    return [abs(p - (b + _saida_rel(i))) for i, (b, p) in enumerate(zip(eb, ep))]


def confere_geometria():
    """Falha alto se as larguras nao fecharem nos 39 m do Ring 3."""
    ocupado = sum(LARG_BLOCOS) + 2 * CORREDOR_EGRESSO + 2 * LARG_FLANCO
    if abs(ocupado - LARGURA) > 0.05:
        raise SystemExit(
            f"geometria nao fecha: blocos + egressos + flancos = {ocupado:.2f} m, "
            f"Ring 3 tem {LARGURA:.2f} m")
    if any(n % 2 == 0 for n in BALIZAS):
        raise SystemExit("todo bloco precisa de numero impar de balizas")


def capacidades():
    """Capacidade por entrada: serpenteado + baia de flanco, quando houver."""
    area_baia = LARG_FLANCO * PROF_SERPENTE
    out = []
    for i, (nome, porta) in enumerate(ENTRADAS):
        serp = BALIZAS[i] * PROF_SERPENTE / PASSO_PESSOA
        baia = area_baia * DENS_BAIA if BAIA_DE[i] else 0.0
        out.append({
            "entrada": nome, "porta": porta, "balizas": BALIZAS[i],
            "larg_bloco": LARG_BLOCOS[i], "serpenteado": serp,
            "baia": baia, "total": serp + baia,
            "area_baia": area_baia if BAIA_DE[i] else 0.0,
        })
    tot = sum(c["total"] for c in out)
    for c in out:
        c["quota"] = c["total"] / tot
    return out


def componentes():
    """Quantitativo de barreira do Ring 3, item a item."""
    ext = 3 * 2 * PROF_SERPENTE
    inte = sum((n - 1) for n in BALIZAS) * (PROF_SERPENTE - LARG_BALIZA)
    comp_fundo = LARGURA - 3.0
    fundo = 2 * comp_fundo - 3 * VAO_ACESSO
    garganta = 10.0
    descarga = 2 * sum(math.hypot(ZONA_DESCARGA, d) for d in desvios())
    # Baias de flanco: fecham no bordo sul (contra o corredor de fundo, com um
    # vao controlado) e no bordo norte. O lado do bloco ja e a baliza externa
    # dele, e o lado externo e o proprio limite do Ring 3.
    n_baias = sum(1 for b in BAIA_DE if b)
    baias = n_baias * ((LARG_FLANCO - VAO_ACESSO) + LARG_FLANCO)
    itens = [
        ("1", "Balizas externas dos 3 blocos",
         f"3 × 2 × {PROF_SERPENTE:.1f} m", ext),
        ("2", "Balizas internas dos 3 blocos",
         f"({'+'.join(str(n-1) for n in BALIZAS)}) × {PROF_SERPENTE-LARG_BALIZA:.1f} m",
         inte),
        ("3", "Corredor de distribuição (fundo)",
         f"2 × {comp_fundo:.1f} − 3 vãos de {VAO_ACESSO:.1f} m", fundo),
        ("4", "Garganta de entrada (canto sudeste)",
         "funil de pré-triagem", garganta),
        ("5", "Canais de descarga até S4/S5/S6",
         "2 lados × (" + " + ".join(f"{math.hypot(ZONA_DESCARGA, d):.1f}"
                                    for d in desvios()) + ") m", descarga),
        ("6", "Fechamento das baias de flanco (A e C)",
         f"{n_baias} × ({LARG_FLANCO-VAO_ACESSO:.1f} + {LARG_FLANCO:.1f}) m", baias),
    ]
    return [(t, n, c, m, math.ceil(m / METROS_POR_UNIDADE)) for t, n, c, m in itens]


def resumo():
    itens = componentes()
    metros = sum(i[3] for i in itens)
    unid = sum(i[4] for i in itens)
    caps = capacidades()
    return {
        "itens": itens, "metros": metros, "unidades": unid,
        "faltam": max(0, unid - SEPARADORES_EM_MAOS),
        "custo": max(0, unid - SEPARADORES_EM_MAOS) * METROS_POR_UNIDADE * EUR_POR_METRO,
        "caps": caps,
        "total_pessoas": sum(c["total"] for c in caps),
    }


# ---------------------------------------------------------------- desenho --

ESC = 19
M_ESQ, M_DIR, M_TOPO, M_BASE = 84, 200, 132, 392

SEP = 'stroke="#c0392b" stroke-width="2.4" stroke-linecap="round"'
FLOW = ('stroke="#2471a3" stroke-width="2.2" fill="none" '
        'stroke-dasharray="7 5" marker-end="url(#a)"')
SM = 'font-size="11" fill="#555"'
LBL = 'font-size="13" fill="#1a1a1a"'
BIG = 'font-size="16" font-weight="bold" fill="#1a1a1a"'
DIM = 'font-size="11" fill="#0a7d55"'
OCRE = "#8a7742"


def _x(m):
    return M_ESQ + m * ESC


def _y(m):
    return M_TOPO + (PROFUNDIDADE - m) * ESC


def _tag(out, n, x, y):
    out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="10" fill="#c0392b"/>')
    out.append(f'<text x="{x:.1f}" y="{y+4:.1f}" font-size="12" '
               f'font-weight="bold" fill="#fff" text-anchor="middle">{n}</text>')


def _giro(out, x, y, txt, tam, cor, negrito=False):
    peso = "bold" if negrito else "normal"
    out.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{tam}" fill="{cor}" '
               f'text-anchor="middle" font-weight="{peso}" '
               f'transform="rotate(-90 {x:.1f} {y:.1f})">{txt}</text>')


def desenha():
    r = resumo()
    caps = r["caps"]
    y0 = FOLGA_SUL + CORREDOR_FUNDO
    y1 = y0 + PROF_SERPENTE
    eixos_bloco, eixos_porta = eixos()
    centro = LARGURA / 2

    W = int(LARGURA * ESC + M_ESQ + M_DIR)
    H = int(PROFUNDIDADE * ESC + M_TOPO + M_BASE)
    out = []
    add = out.append

    add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" font-family="Helvetica,Arial,sans-serif">')
    add('<defs>'
        '<marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" '
        'markerHeight="6" orient="auto"><path d="M0,0 L10,5 L0,10 z" '
        'fill="#2471a3"/></marker>'
        '<marker id="b" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
        'markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" '
        f'fill="{OCRE}"/></marker>'
        '<marker id="e" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" '
        'markerHeight="6" orient="auto"><path d="M0,0 L10,5 L0,10 z" '
        'fill="#1e8449"/></marker></defs>')
    add(f'<rect width="{W}" height="{H}" fill="#fbfbf9"/>')
    add(f'<text x="{_x(0)}" y="36" font-size="21" font-weight="bold" '
        f'fill="#1a1a1a">Ring 3 — layout base de filas</text>')
    add(f'<text x="{_x(0)}" y="57" {SM}>Entrada pelo canto sudeste · corredor de '
        f'distribuição no fundo · serpenteados A/B/C descarregando em S4, S5 e '
        f'S6 · saídas por S2 e S8 · baias de reserva dedicadas a A e a C</text>')

    # ---- fachada sul do Hall 2 -------------------------------------------
    hy = M_TOPO - 62
    add(f'<rect x="{_x(-2.5)}" y="{hy}" width="{(LARGURA+5)*ESC}" height="26" '
        f'fill="#e8eef4" stroke="#8fa6bb"/>')
    add(f'<text x="{_x(-1.8)}" y="{hy+18}" {BIG}>HALL 2</text>')
    for nome, dist in PORTAS_SUL.items():
        xm = centro + (dist - PORTAS_SUL["S5"])
        if not -1 <= xm <= LARGURA + 1:
            continue
        cx = _x(xm)
        ent = next((n for n, p in ENTRADAS if p == nome), None)
        if ent:
            add(f'<rect x="{cx-17}" y="{hy+20}" width="34" height="9" fill="#2471a3"/>')
            add(f'<text x="{cx}" y="{hy+45}" {LBL} text-anchor="middle" '
                f'font-weight="bold">{nome}</text>')
            add(f'<text x="{cx}" y="{hy+58}" font-size="10" fill="#2471a3" '
                f'text-anchor="middle">entrada {ent}</text>')
        elif nome in SAIDAS_PORTAS:
            add(f'<rect x="{cx-17}" y="{hy+20}" width="34" height="9" fill="#1e8449"/>')
            add(f'<text x="{cx}" y="{hy+45}" font-size="13" fill="#1e8449" '
                f'text-anchor="middle" font-weight="bold">{nome}</text>')
            add(f'<text x="{cx}" y="{hy+58}" font-size="10" fill="#1e8449" '
                f'text-anchor="middle">saída</text>')
        else:
            add(f'<rect x="{cx-13}" y="{hy+20}" width="26" height="7" fill="#bdc3c7"/>')
            add(f'<text x="{cx}" y="{hy+45}" font-size="10" fill="#95a5a6" '
                f'text-anchor="middle">{nome}</text>')

    # ---- contorno do Ring 3 ----------------------------------------------
    add(f'<rect x="{_x(0)}" y="{_y(PROFUNDIDADE)}" width="{LARGURA*ESC}" '
        f'height="{PROFUNDIDADE*ESC}" fill="#fff" stroke="#333" stroke-width="2"/>')

    # ---- faixa de descarga ------------------------------------------------
    add(f'<rect x="{_x(0)}" y="{_y(PROFUNDIDADE)}" width="{LARGURA*ESC}" '
        f'height="{ZONA_DESCARGA*ESC}" fill="#eef4f9" stroke="#c7d8e6" '
        f'stroke-dasharray="5 3"/>')
    add(f'<text x="{_x(0.6)}" y="{_y(PROFUNDIDADE)+15}" {SM}>'
        f'faixa de descarga — {ZONA_DESCARGA:.1f} m</text>')

    # ---- baias de flanco, dedicadas -------------------------------------
    drenos = []
    for i, dono in enumerate(BAIA_DE):
        if not dono:
            continue
        oeste = eixos_bloco[i] < centro
        xa, xb = (0.0, LARG_FLANCO) if oeste else (LARGURA - LARG_FLANCO, LARGURA)
        add(f'<rect x="{_x(xa)}" y="{_y(y1)}" width="{LARG_FLANCO*ESC}" '
            f'height="{PROF_SERPENTE*ESC}" fill="#f6f0e2" stroke="{OCRE}" '
            f'stroke-width="1.6" stroke-dasharray="7 4"/>')
        cxm, ymid = _x((xa + xb) / 2), _y(y0 + PROF_SERPENTE / 2)
        c = caps[i]
        _giro(out, cxm - 16, ymid, f"BAIA DE RESERVA · {dono}", 13, OCRE, True)
        _giro(out, cxm, ymid, f"exclusiva da entrada {dono} — sem balizas",
              11, "#9c8b63")
        _giro(out, cxm + 15, ymid,
              f"{LARG_FLANCO:.1f} × {PROF_SERPENTE:.1f} m · "
              f"{c['area_baia']:.0f} m² · ~{c['baia']:.0f} pessoas", 11, "#9c8b63")
        # cota da largura
        add(f'<line x1="{_x(xa)+2}" y1="{_y(y1)-9}" x2="{_x(xb)-2}" '
            f'y2="{_y(y1)-9}" stroke="{OCRE}" stroke-width="1.2"/>')
        add(f'<text x="{cxm}" y="{_y(y1)-13}" font-size="11" fill="{OCRE}" '
            f'text-anchor="middle">{LARG_FLANCO:.1f} m</text>')
        # dreno direto para a baliza de ENTRADA do bloco vizinho: a baia
        # encosta nela, entao a seta parte de dentro da baia para ser legivel
        xent = eixos_bloco[i] + _entrada_rel(i)
        x_ini = (xb - 2.8) if oeste else (xa + 2.8)
        for fr in (0.22, 0.50, 0.78):
            yy = _y(y0 + PROF_SERPENTE * fr)
            drenos.append(f'<line x1="{_x(x_ini):.1f}" y1="{yy:.1f}" '
                          f'x2="{_x(xent):.1f}" y2="{yy:.1f}" stroke="{OCRE}" '
                          f'stroke-width="2.2" marker-end="url(#b)"/>')
        _giro(out, _x(xb - 1.2 if oeste else xa + 1.2),
              _y(y0 + PROF_SERPENTE * 0.5), "drena direto para a fila " + dono,
              10, OCRE)
        _tag(out, "6", _x((xa + xb) / 2), _y(y1) - 30)

    # ---- corredor de distribuicao ----------------------------------------
    add(f'<rect x="{_x(0)}" y="{_y(y0)}" width="{LARGURA*ESC}" '
        f'height="{CORREDOR_FUNDO*ESC}" fill="#fdf3e3" stroke="#dfa94a" '
        f'stroke-dasharray="5 3"/>')
    add(f'<text x="{_x(0.6)}" y="{_y(y0)+13}" {SM}>corredor de distribuição '
        f'— {CORREDOR_FUNDO:.1f} m</text>')
    yf = _y(FOLGA_SUL + 0.6)
    add(f'<line x1="{_x(LARGURA-1.2):.1f}" y1="{yf:.1f}" x2="{_x(1.2):.1f}" '
        f'y2="{yf:.1f}" {FLOW}/>')
    _tag(out, "3", _x(LARGURA / 2 - 7), yf)

    # ---- blocos serpenteados ---------------------------------------------
    for i, ((nome, porta), eb) in enumerate(zip(ENTRADAS, eixos_bloco)):
        larg = LARG_BLOCOS[i]
        n = BALIZAS[i]
        ep = eixos_porta[i]
        xa, xb = eb - larg / 2, eb + larg / 2
        add(f'<rect x="{_x(xa)}" y="{_y(y1)}" width="{larg*ESC}" '
            f'height="{PROF_SERPENTE*ESC}" fill="#f3f7fa" stroke="#d5e2ec"/>')
        base, passo = (xa, +1) if ESPELHADO[i] else (xb, -1)
        for j in range(n + 1):
            xs = _x(base + passo * j * LARG_BALIZA)
            if j in (0, n):
                ya, yb = _y(y1), _y(y0)
            elif j % 2 == 1:
                ya, yb = _y(y1 - LARG_BALIZA), _y(y0)
            else:
                ya, yb = _y(y1), _y(y0 + LARG_BALIZA)
            add(f'<line x1="{xs:.1f}" y1="{ya:.1f}" x2="{xs:.1f}" '
                f'y2="{yb:.1f}" {SEP}/>')
        pts = []
        for j in range(n):
            xc = _x(base + passo * (j + 0.5) * LARG_BALIZA)
            sobe = (j % 2 == 0)
            pts += [(xc, _y(y0 + 0.4) if sobe else _y(y1 - 0.4)),
                    (xc, _y(y1 - 0.4) if sobe else _y(y0 + 0.4))]
        add(f'<polyline points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in pts)}" '
            f'fill="none" stroke="#2471a3" stroke-width="1.8" '
            f'stroke-linejoin="round" opacity="0.9" marker-end="url(#a)"/>')
        c = caps[i]
        add(f'<text x="{_x(eb)}" y="{_y(y1)-40}" {BIG} text-anchor="middle">'
            f'ENTRADA {nome}</text>')
        add(f'<text x="{_x(eb)}" y="{_y(y1)-26}" {SM} text-anchor="middle">'
            f'{n} balizas · {c["serpenteado"]:.0f} pessoas</text>')
        rot = (f'+ baia {c["baia"]:.0f} = {c["total"]:.0f}' if c["baia"]
               else "sem baia — 2 balizas a mais")
        add(f'<text x="{_x(eb)}" y="{_y(y1)-13}" font-size="11" '
            f'fill="{OCRE if c["baia"] else "#7f8c8d"}" text-anchor="middle">'
            f'{rot}</text>')
        xent = _x(base + passo * 0.5 * LARG_BALIZA)
        add(f'<line x1="{xent:.1f}" y1="{_y(y0-0.2):.1f}" x2="{xent:.1f}" '
            f'y2="{_y(y0+0.9):.1f}" {FLOW}/>')
        xsai = eb + _saida_rel(i)
        add(f'<line x1="{_x(xsai):.1f}" y1="{_y(y1):.1f}" x2="{_x(ep):.1f}" '
            f'y2="{_y(PROFUNDIDADE):.1f}" {FLOW}/>')
        add(f'<line x1="{_x(ep):.1f}" y1="{_y(PROFUNDIDADE):.1f}" '
            f'x2="{_x(ep):.1f}" y2="{hy+31}" {FLOW}/>')
        if i == 0:
            _tag(out, "1", _x(xa) - 13, _y(y0 + PROF_SERPENTE * 0.90))
            _tag(out, "2", _x(eb), _y(y0 + PROF_SERPENTE * 0.5))
            _tag(out, "5", _x(xsai) - 16, _y(y1 + ZONA_DESCARGA * 0.72))

    out.extend(drenos)

    # ---- corredores de egresso -------------------------------------------
    for i in range(len(eixos_bloco) - 1):
        xm = (eixos_bloco[i] + LARG_BLOCOS[i] / 2
              + eixos_bloco[i+1] - LARG_BLOCOS[i+1] / 2) / 2
        _giro(out, _x(xm), _y(y0 + PROF_SERPENTE / 2),
              f"egresso {CORREDOR_EGRESSO:.1f} m", 11, "#7f8c8d")

    # ---- entrada no canto sudeste ----------------------------------------
    ey = _y(FOLGA_SUL + CORREDOR_FUNDO / 2)
    add(f'<line x1="{_x(LARGURA)+96:.1f}" y1="{ey:.1f}" '
        f'x2="{_x(LARGURA)+8:.1f}" y2="{ey:.1f}" {FLOW}/>')
    add(f'<line x1="{_x(LARGURA)+8:.1f}" y1="{ey:.1f}" '
        f'x2="{_x(LARGURA-0.6):.1f}" y2="{yf:.1f}" {FLOW}/>')
    add(f'<text x="{_x(LARGURA)+16}" y="{ey-12}" font-size="15" '
        f'font-weight="bold" fill="#c0392b">ENTRADA</text>')
    add(f'<text x="{_x(LARGURA)+16}" y="{ey+30}" font-size="11" '
        f'fill="#c0392b">canto sudeste</text>')
    _tag(out, "4", _x(LARGURA) + 8, ey - 30)

    # ---- saidas por S2 e S8 ----------------------------------------------
    for porta in SAIDAS_PORTAS:
        xm = centro + (PORTAS_SUL[porta] - PORTAS_SUL["S5"])
        cx, dx = _x(xm), (-46 if xm < centro else 46)
        add(f'<line x1="{cx:.1f}" y1="{hy+30}" x2="{cx:.1f}" y2="{hy+34}" '
            f'stroke="#1e8449" stroke-width="2.2"/>')
        add(f'<line x1="{cx:.1f}" y1="{hy+34}" x2="{cx+dx:.1f}" y2="{hy+34}" '
            f'stroke="#1e8449" stroke-width="2.2" fill="none" '
            f'marker-end="url(#e)"/>')

    # ---- cotas ------------------------------------------------------------
    add(f'<text x="{_x(LARGURA/2)}" y="{_y(0)+24}" {DIM} text-anchor="middle">'
        f'{LARGURA:.0f} m (leste–oeste)</text>')
    ym = _y(PROFUNDIDADE / 2)
    add(f'<text x="{_x(0)-16}" y="{ym}" {DIM} text-anchor="middle" '
        f'transform="rotate(-90 {_x(0)-16} {ym})">'
        f'{PROFUNDIDADE:.0f} m (sul–norte)</text>')
    ys = _y(y0 + PROF_SERPENTE / 2)
    add(f'<text x="{_x(LARGURA)+8}" y="{ys}" {DIM} text-anchor="middle" '
        f'transform="rotate(-90 {_x(LARGURA)+8} {ys})">'
        f'serpenteado {PROF_SERPENTE:.0f} m</text>')

    # ---- capacidade por entrada ------------------------------------------
    ty = _y(0) + 52
    add(f'<text x="{_x(0)}" y="{ty}" font-size="15" font-weight="bold" '
        f'fill="#1a1a1a">Capacidade por entrada — cada fila tem a sua reserva'
        f'</text>')
    ty += 22
    for k, t in enumerate(("Entrada", "Serpenteado", "Baia de reserva",
                           "Total", "Quota do eleitorado")):
        anc = "start" if k == 0 else "end"
        px = _x(0) + (0 if k == 0 else 130 + k * 118)
        add(f'<text x="{px}" y="{ty}" font-size="12" font-weight="bold" '
            f'fill="#555" text-anchor="{anc}">{t}</text>')
    add(f'<line x1="{_x(0)}" y1="{ty+6}" x2="{_x(0)+620}" y2="{ty+6}" '
        f'stroke="#ccc"/>')
    for c in caps:
        ty += 21
        add(f'<text x="{_x(0)}" y="{ty}" {LBL}>{c["entrada"]} → {c["porta"]} '
            f'({c["balizas"]} balizas)</text>')
        vals = [f'{c["serpenteado"]:.0f}',
                f'{c["baia"]:.0f}' if c["baia"] else "—",
                f'{c["total"]:.0f}', f'{c["quota"]:.0%}']
        for k, v in enumerate(vals, start=1):
            add(f'<text x="{_x(0)+130+k*118}" y="{ty}" {LBL} '
                f'text-anchor="end">{v}</text>')
    ty += 8
    add(f'<line x1="{_x(0)}" y1="{ty}" x2="{_x(0)+620}" y2="{ty}" stroke="#333"/>')
    ty += 19
    add(f'<text x="{_x(0)}" y="{ty}" {LBL} font-weight="bold">TOTAL</text>')
    add(f'<text x="{_x(0)+130+3*118}" y="{ty}" {LBL} font-weight="bold" '
        f'text-anchor="end">{r["total_pessoas"]:.0f}</text>')

    # ---- quantitativo de barreira ----------------------------------------
    ty += 34
    add(f'<text x="{_x(0)}" y="{ty}" font-size="15" font-weight="bold" '
        f'fill="#1a1a1a">Separadores de barreira — Ring 3 apenas</text>')
    ty += 22
    cols = [0, 26, 320, 500, 590]
    for c, t in zip(cols, ("", "Componente", "Cálculo", "Metros", "Separadores")):
        anc = "end" if t in ("Metros", "Separadores") else "start"
        px = _x(0) + c + (70 if anc == "end" else 0)
        add(f'<text x="{px}" y="{ty}" font-size="12" font-weight="bold" '
            f'fill="#555" text-anchor="{anc}">{t}</text>')
    add(f'<line x1="{_x(0)}" y1="{ty+6}" x2="{_x(0)+660}" y2="{ty+6}" '
        f'stroke="#ccc"/>')
    ty += 8
    for tag, nome, calc, m, u in r["itens"]:
        ty += 21
        _tag(out, tag, _x(0) + 9, ty - 4)
        add(f'<text x="{_x(0)+cols[1]}" y="{ty}" {LBL}>{nome}</text>')
        add(f'<text x="{_x(0)+cols[2]}" y="{ty}" {SM}>{calc}</text>')
        add(f'<text x="{_x(0)+cols[3]+70}" y="{ty}" {LBL} text-anchor="end">'
            f'{m:,.1f}</text>'.replace(",", "."))
        add(f'<text x="{_x(0)+cols[4]+70}" y="{ty}" {LBL} text-anchor="end">'
            f'{u}</text>')
    ty += 12
    add(f'<line x1="{_x(0)}" y1="{ty}" x2="{_x(0)+660}" y2="{ty}" stroke="#333"/>')
    ty += 20
    add(f'<text x="{_x(0)+cols[1]}" y="{ty}" {LBL} font-weight="bold">'
        f'TOTAL do Ring 3</text>')
    add(f'<text x="{_x(0)+cols[3]+70}" y="{ty}" {LBL} font-weight="bold" '
        f'text-anchor="end">{r["metros"]:,.1f}</text>'.replace(",", "."))
    add(f'<text x="{_x(0)+cols[4]+70}" y="{ty}" {LBL} font-weight="bold" '
        f'text-anchor="end">{r["unidades"]}</text>')
    ty += 20
    add(f'<text x="{_x(0)+cols[1]}" y="{ty}" {SM}>Fornecidos pela organizadora '
        f'({SEPARADORES_EM_MAOS} un. de {METROS_POR_UNIDADE:.0f} m × '
        f'{ALTURA_SEPARADOR:.0f} m de altura)</text>')
    add(f'<text x="{_x(0)+cols[4]+70}" y="{ty}" {SM} text-anchor="end">'
        f'−{SEPARADORES_EM_MAOS}</text>')
    ty += 20
    add(f'<text x="{_x(0)+cols[1]}" y="{ty}" font-size="13" font-weight="bold" '
        f'fill="#c0392b">A ADQUIRIR</text>')
    add(f'<text x="{_x(0)+cols[4]+70}" y="{ty}" font-size="13" '
        f'font-weight="bold" fill="#c0392b" text-anchor="end">'
        f'{r["faltam"]}</text>')
    add(f'<text x="{_x(0)+cols[4]+90}" y="{ty}" {SM}>'
        f'≈ EUR {r["custo"]:,.0f}'.replace(",", ".") + '</text>')

    ty += 28
    dv = desvios()
    for t in [
        'Cada entrada tem reserva própria: misturar as filas destruiria o '
        'roteamento da pré-triagem, já que o eleitor só vota na urna da sua seção.',
        f'As baias drenam direto para a baliza de entrada do seu bloco, sem '
        f'passar pelo corredor de fundo. B não tem flanco e recebe '
        f'{BALIZAS[1]-BALIZAS[0]} balizas a mais em compensação.',
        'Desvio da baliza de saída até a porta: '
        + ", ".join(f"{n} {d:.1f} m ({math.degrees(math.atan(d/ZONA_DESCARGA)):.0f}°)"
                    for (n, _), d in zip(ENTRADAS, dv))
        + f' na faixa de descarga de {ZONA_DESCARGA:.0f} m.',
        'Este quantitativo cobre SOMENTE o Ring 3. O interior do Hall 2 tem '
        'necessidade própria, ainda não dimensionada.',
        'Posições das portas lidas na prancheta do Posto. Aferir em campo a '
        'distância do bordo oeste do Ring 3 ao canto sudoeste do Hall 2.',
    ]:
        add(f'<text x="{_x(0)}" y="{ty}" {SM}>{t}</text>')
        ty += 17
    add('</svg>')

    svg = "\n".join(out)
    try:
        ET.fromstring(svg)
    except ET.ParseError as erro:
        raise SystemExit(f"SVG invalido, nao gravado: {erro}") from erro
    SAIDA.write_text(svg, encoding="utf-8")
    _exporta_png()
    return r


def _exporta_png(dpi=130):
    """Exporta um PNG do desenho. Opcional: sem pymupdf, so o SVG e gerado."""
    try:
        import pymupdf
    except ImportError:
        print("pymupdf ausente: PNG nao gerado (o SVG e a fonte da verdade).")
        return
    pymupdf.open(SAIDA)[0].get_pixmap(dpi=dpi).save(SAIDA_PNG)


def main():
    confere_geometria()
    r = resumo()
    print(f"Ring 3 {LARGURA:.0f} × {PROFUNDIDADE:.0f} m | serpenteado "
          f"{PROF_SERPENTE:.1f} m | egresso {CORREDOR_EGRESSO:.1f} m | "
          f"flanco {LARG_FLANCO:.1f} m\n")

    cab = (f"{'entrada':<9} {'balizas':>7} {'bloco':>7} {'serpent.':>9} "
           f"{'baia':>7} {'TOTAL':>7} {'quota':>7}")
    print(cab); print("-" * len(cab))
    for c in r["caps"]:
        print(f"{c['entrada']} → {c['porta']:<4} {c['balizas']:>7} "
              f"{c['larg_bloco']:>6.1f}m {c['serpenteado']:>9.0f} "
              f"{c['baia']:>7.0f} {c['total']:>7.0f} {c['quota']:>6.1%}")
    print("-" * len(cab))
    print(f"{'TOTAL':<9} {'':>7} {'':>7} "
          f"{sum(c['serpenteado'] for c in r['caps']):>9.0f} "
          f"{sum(c['baia'] for c in r['caps']):>7.0f} "
          f"{r['total_pessoas']:>7.0f}\n")

    cab2 = f"{'':>3} {'Componente':<40} {'Cálculo':<32} {'metros':>8} {'sep.':>6}"
    print(cab2); print("-" * len(cab2))
    for tag, nome, calc, m, u in r["itens"]:
        print(f"{tag:>2}. {nome:<40} {calc:<32} {m:>8.1f} {u:>6}")
    print("-" * len(cab2))
    print(f"{'':>3} {'TOTAL DO RING 3':<40} {'':<32} {r['metros']:>8.1f} "
          f"{r['unidades']:>6}")
    print(f"{'':>3} {'Fornecidos pela organizadora':<40} {'':<32} "
          f"{SEPARADORES_EM_MAOS*METROS_POR_UNIDADE:>8.1f} "
          f"{SEPARADORES_EM_MAOS:>6}")
    print(f"{'':>3} {'A ADQUIRIR':<40} {'':<32} "
          f"{r['faltam']*METROS_POR_UNIDADE:>8.1f} {r['faltam']:>6}"
          f"   ≈ EUR {r['custo']:,.0f}")

    desenha()
    print(f"\nDesenho: {SAIDA.relative_to(RAIZ)}")
    if SAIDA_PNG.exists():
        print(f"         {SAIDA_PNG.relative_to(RAIZ)} "
              f"({SAIDA_PNG.stat().st_size//1024} KB)")


if __name__ == "__main__":
    main()
