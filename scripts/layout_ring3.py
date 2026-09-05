"""Layout do Ring 3: tres corredores serpenteados e calculo de barreiras.

Desenho definido pelo Posto:
  - acesso pelo canto SUDESTE;
  - corredor estreito de distribuicao no "fundo" (bordo sul), de leste a oeste;
  - tres serpenteados ("Disney queue") dele derivados, de oeste para leste:
    ENTRADA A -> porta S4, ENTRADA B -> S5, ENTRADA C -> S6;
  - S2 e S8 reservadas como SAIDA, nos flancos, fora do vao das entradas.

Piso pavimentado. Espaco locado desde a vespera, sem carros a remover.

TODO O CALCULO DE BARREIRA AQUI E SO DO RING 3. O interior do Hall 2 (filas
junto as 28 urnas, canalizacao das portas para dentro) tem necessidade propria,
ainda nao dimensionada.

Gera saidas/layout_ring3.svg em escala e imprime o quantitativo por componente.
Uso:  python3 scripts/layout_ring3.py
"""

import math
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "saidas" / "layout_ring3.svg"

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
CORREDOR_FUNDO = 2.5    # corredor estreito de distribuicao
ZONA_DESCARGA = 5.0     # leque convergente ate as portas

LARG_BALIZA = 1.40
PASSO_PESSOA = 0.50
CORREDOR_EGRESSO = 2.0  # vao livre entre blocos vizinhos
METROS_POR_UNIDADE = 2.0
EUR_POR_METRO = 6.51
SEPARADORES_EM_MAOS = 100

BALIZAS = 5             # tem de ser impar: entra-se pelo sul e a ultima
                        # baliza precisa correr para o norte
PROF_SERPENTE = PROFUNDIDADE - FOLGA_SUL - CORREDOR_FUNDO - ZONA_DESCARGA
LARG_BLOCO = BALIZAS * LARG_BALIZA
PASSO_BLOCOS = LARG_BLOCO + CORREDOR_EGRESSO            # 9,0 m
# O bloco A e ESPELHADO: entra-se pela baliza oeste e sai-se pela leste. Isso
# poe a saida de A exatamente sobre S4 e a de C exatamente sobre S6, deixando
# so o corredor B com desvio. Sem o espelhamento, A sairia 5,6 m fora da sua
# porta — uma diagonal de 48 graus na faixa de descarga.
ESPELHADO = (True, False, False)      # blocos A, B, C


def _saida_rel(espelhado):
    """Posicao da baliza de saida, relativa ao eixo do bloco."""
    d = LARG_BLOCO / 2 - LARG_BALIZA / 2
    return d if espelhado else -d


def eixos():
    """Eixos dos blocos e das portas, em metros do bordo oeste do Ring 3."""
    centro = LARGURA / 2
    return ([centro - PASSO_BLOCOS, centro, centro + PASSO_BLOCOS],
            [centro - PASSO_PORTAS, centro, centro + PASSO_PORTAS])


def desvios():
    """Deslocamento leste-oeste da baliza de saida de cada bloco ate sua porta."""
    eb, ep = eixos()
    return [abs(p - (b + _saida_rel(m)))
            for b, p, m in zip(eb, ep, ESPELHADO)]


def componentes():
    """Quantitativo de barreira do Ring 3, item a item."""
    ext = 3 * 2 * PROF_SERPENTE
    inte = 3 * (BALIZAS - 1) * (PROF_SERPENTE - LARG_BALIZA)
    # corredor de fundo: dois lados, menos os 3 vaos de acesso aos blocos
    comp_fundo = LARGURA - 3.0
    fundo = 2 * comp_fundo - 3 * 1.5
    garganta = 10.0
    # canais de descarga: um por bloco, da baliza de saida ate a porta
    diags = [math.hypot(ZONA_DESCARGA, d) for d in desvios()]
    descarga = 2 * sum(diags)
    itens = [
        ("1", "Balizas externas dos 3 blocos",
         f"3 × 2 × {PROF_SERPENTE:.1f} m", ext),
        ("2", "Balizas internas dos 3 blocos",
         f"3 × {BALIZAS-1} × {PROF_SERPENTE-LARG_BALIZA:.1f} m", inte),
        ("3", "Corredor de distribuição (fundo)",
         f"2 × {comp_fundo:.1f} − 3 vãos de 1,5 m", fundo),
        ("4", "Garganta de entrada (canto sudeste)",
         "funil de pré-triagem", garganta),
        ("5", "Canais de descarga até S4/S5/S6",
         "2 lados × (" + " + ".join(f"{d:.1f}" for d in diags) + ") m", descarga),
    ]
    return [(t, n, c, m, math.ceil(m / METROS_POR_UNIDADE)) for t, n, c, m in itens]


def resumo():
    itens = componentes()
    metros = sum(i[3] for i in itens)
    unid = sum(i[4] for i in itens)
    fila = BALIZAS * PROF_SERPENTE
    return {
        "itens": itens,
        "metros": metros,
        "unidades": unid,
        "faltam": max(0, unid - SEPARADORES_EM_MAOS),
        "custo": max(0, unid - SEPARADORES_EM_MAOS) * METROS_POR_UNIDADE * EUR_POR_METRO,
        "fila_bloco": fila,
        "pessoas_bloco": fila / PASSO_PESSOA,
        "pessoas_total": 3 * fila / PASSO_PESSOA,
    }


# ---------------------------------------------------------------- desenho --

ESC = 19
M_ESQ, M_DIR, M_TOPO, M_BASE = 84, 200, 132, 356

SEP = 'stroke="#c0392b" stroke-width="2.4" stroke-linecap="round"'
FLOW = ('stroke="#2471a3" stroke-width="2.2" fill="none" '
        'stroke-dasharray="7 5" marker-end="url(#a)"')
EXIT = ('stroke="#1e8449" stroke-width="2.2" fill="none" '
        'marker-end="url(#e)"')
SM = 'font-size="11" fill="#555"'
LBL = 'font-size="13" fill="#1a1a1a"'
BIG = 'font-size="16" font-weight="bold" fill="#1a1a1a"'
DIM = 'font-size="11" fill="#0a7d55"'


def _x(m):
    return M_ESQ + m * ESC


def _y(m):
    return M_TOPO + (PROFUNDIDADE - m) * ESC


def _tag(out, n, x, y):
    """Marcador numerado de componente de barreira."""
    out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="10" fill="#c0392b"/>')
    out.append(f'<text x="{x:.1f}" y="{y+4:.1f}" font-size="12" '
               f'font-weight="bold" fill="#fff" text-anchor="middle">{n}</text>')


def desenha():
    r = resumo()
    y0 = FOLGA_SUL + CORREDOR_FUNDO
    y1 = y0 + PROF_SERPENTE
    centro = LARGURA / 2

    eixos_bloco, eixos_porta = eixos()
    blocos = [(nome, porta, eb, ep, esp) for (nome, porta), eb, ep, esp
              in zip(ENTRADAS, eixos_bloco, eixos_porta, ESPELHADO)]

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
        '<marker id="e" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" '
        'markerHeight="6" orient="auto"><path d="M0,0 L10,5 L0,10 z" '
        'fill="#1e8449"/></marker></defs>')
    add(f'<rect width="{W}" height="{H}" fill="#fbfbf9"/>')
    add(f'<text x="{_x(0)}" y="36" font-size="21" font-weight="bold" '
        f'fill="#1a1a1a">Ring 3 — layout base de filas</text>')
    add(f'<text x="{_x(0)}" y="57" {SM}>Entrada pelo canto sudeste · corredor '
        f'de distribuição no fundo · serpenteados A/B/C descarregando em '
        f'S4, S5 e S6 · saídas por S2 e S8</text>')

    # ---- fachada sul do Hall 2, com as nove portas -----------------------
    hy = M_TOPO - 62
    add(f'<rect x="{_x(-2.5)}" y="{hy}" width="{(LARGURA+5)*ESC}" height="26" '
        f'fill="#e8eef4" stroke="#8fa6bb"/>')
    add(f'<text x="{_x(-1.8)}" y="{hy+18}" {BIG}>HALL 2</text>')
    # posiciona as nove portas relativas a S5, que fica no centro do Ring 3
    for nome, dist in PORTAS_SUL.items():
        xm = centro + (dist - PORTAS_SUL["S5"])
        if not -1 <= xm <= LARGURA + 1:
            continue
        cx = _x(xm)
        ent = next((n for n, p in ENTRADAS if p == nome), None)
        if ent:
            add(f'<rect x="{cx-17}" y="{hy+20}" width="34" height="9" '
                f'fill="#2471a3"/>')
            add(f'<text x="{cx}" y="{hy+45}" {LBL} text-anchor="middle" '
                f'font-weight="bold">{nome}</text>')
            add(f'<text x="{cx}" y="{hy+58}" font-size="10" fill="#2471a3" '
                f'text-anchor="middle">entrada {ent}</text>')
        elif nome in SAIDAS_PORTAS:
            add(f'<rect x="{cx-17}" y="{hy+20}" width="34" height="9" '
                f'fill="#1e8449"/>')
            add(f'<text x="{cx}" y="{hy+45}" {LBL} text-anchor="middle" '
                f'font-weight="bold" fill="#1e8449">{nome}</text>')
            add(f'<text x="{cx}" y="{hy+58}" font-size="10" fill="#1e8449" '
                f'text-anchor="middle">saída</text>')
        else:
            add(f'<rect x="{cx-13}" y="{hy+20}" width="26" height="7" '
                f'fill="#bdc3c7"/>')
            add(f'<text x="{cx}" y="{hy+45}" font-size="10" fill="#95a5a6" '
                f'text-anchor="middle">{nome}</text>')

    # ---- contorno do Ring 3 ----------------------------------------------
    add(f'<rect x="{_x(0)}" y="{_y(PROFUNDIDADE)}" width="{LARGURA*ESC}" '
        f'height="{PROFUNDIDADE*ESC}" fill="#fff" stroke="#333" stroke-width="2"/>')

    # ---- faixa de descarga -------------------------------------------------
    add(f'<rect x="{_x(0)}" y="{_y(PROFUNDIDADE)}" width="{LARGURA*ESC}" '
        f'height="{ZONA_DESCARGA*ESC}" fill="#eef4f9" stroke="#c7d8e6" '
        f'stroke-dasharray="5 3"/>')
    add(f'<text x="{_x(0.6)}" y="{_y(PROFUNDIDADE)+15}" {SM}>'
        f'faixa de descarga — {ZONA_DESCARGA:.1f} m</text>')

    # ---- reserva de flanco ------------------------------------------------
    fl = eixos_bloco[0] - LARG_BLOCO / 2
    fr = eixos_bloco[2] + LARG_BLOCO / 2
    for xa, xb in ((0.0, fl), (fr, LARGURA)):
        add(f'<rect x="{_x(xa)}" y="{_y(y1)}" width="{(xb-xa)*ESC}" '
            f'height="{PROF_SERPENTE*ESC}" fill="#f6f3ec" stroke="#d8cdb4" '
            f'stroke-dasharray="4 4"/>')
        cxm = _x((xa + xb) / 2)
        add(f'<text x="{cxm}" y="{_y(y0+PROF_SERPENTE/2)}" font-size="11" '
            f'fill="#9c8b63" text-anchor="middle" '
            f'transform="rotate(-90 {cxm} {_y(y0+PROF_SERPENTE/2)})">'
            f'reserva de flanco (sem balizas)</text>')

    # ---- corredor de distribuicao ----------------------------------------
    add(f'<rect x="{_x(0)}" y="{_y(y0)}" width="{LARGURA*ESC}" '
        f'height="{CORREDOR_FUNDO*ESC}" fill="#fdf3e3" stroke="#dfa94a" '
        f'stroke-dasharray="5 3"/>')
    add(f'<text x="{_x(0.6)}" y="{_y(y0)+13}" {SM}>corredor de distribuição '
        f'— {CORREDOR_FUNDO:.1f} m</text>')
    yf = _y(FOLGA_SUL + 0.6)
    add(f'<line x1="{_x(LARGURA-1.2):.1f}" y1="{yf:.1f}" x2="{_x(1.2):.1f}" '
        f'y2="{yf:.1f}" {FLOW}/>')
    _tag(out, "3", _x(LARGURA / 2 - 6), _y(FOLGA_SUL + 0.6) + 1)

    # ---- blocos serpenteados ---------------------------------------------
    for idx, (nome, porta, eb, ep, esp) in enumerate(blocos):
        xa, xb = eb - LARG_BLOCO / 2, eb + LARG_BLOCO / 2
        add(f'<rect x="{_x(xa)}" y="{_y(y1)}" width="{LARG_BLOCO*ESC}" '
            f'height="{PROF_SERPENTE*ESC}" fill="#f3f7fa" stroke="#d5e2ec"/>')
        base, passo = (xa, +1) if esp else (xb, -1)
        for j in range(BALIZAS + 1):
            xs = _x(base + passo * j * LARG_BALIZA)
            if j in (0, BALIZAS):
                ya, yb = _y(y1), _y(y0)
            elif j % 2 == 1:
                ya, yb = _y(y1 - LARG_BALIZA), _y(y0)
            else:
                ya, yb = _y(y1), _y(y0 + LARG_BALIZA)
            add(f'<line x1="{xs:.1f}" y1="{ya:.1f}" x2="{xs:.1f}" '
                f'y2="{yb:.1f}" {SEP}/>')
        # rota efetiva
        pts = []
        for j in range(BALIZAS):
            xc = _x(base + passo * (j + 0.5) * LARG_BALIZA)
            sobe = (j % 2 == 0)
            pts += [(xc, _y(y0 + 0.4) if sobe else _y(y1 - 0.4)),
                    (xc, _y(y1 - 0.4) if sobe else _y(y0 + 0.4))]
        add(f'<polyline points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in pts)}" '
            f'fill="none" stroke="#2471a3" stroke-width="1.7" '
            f'stroke-linejoin="round" opacity="0.85"/>')
        cx = _x(eb)
        add(f'<rect x="{_x(xa)}" y="{_y(y1)+4}" width="{LARG_BLOCO*ESC}" '
            f'height="36" fill="#fff" opacity="0.82"/>')
        add(f'<text x="{cx}" y="{_y(y1)+21}" {BIG} text-anchor="middle">'
            f'ENTRADA {nome}</text>')
        add(f'<text x="{cx}" y="{_y(y1)+35}" {SM} text-anchor="middle">'
            f'{BALIZAS} balizas · {r["pessoas_bloco"]:.0f} pessoas</text>')
        # entrada no bloco
        xent = _x(base + passo * 0.5 * LARG_BALIZA)
        add(f'<line x1="{xent:.1f}" y1="{_y(y0-0.2):.1f}" '
            f'x2="{xent:.1f}" y2="{_y(y0+0.9):.1f}" {FLOW}/>')
        # canal de descarga: da baliza oeste do bloco ate a porta
        xsai = eb + _saida_rel(esp)
        add(f'<line x1="{_x(xsai):.1f}" y1="{_y(y1):.1f}" x2="{_x(ep):.1f}" '
            f'y2="{_y(PROFUNDIDADE):.1f}" {FLOW}/>')
        add(f'<line x1="{_x(ep):.1f}" y1="{_y(PROFUNDIDADE):.1f}" '
            f'x2="{_x(ep):.1f}" y2="{hy+31}" {FLOW}/>')
        if idx == 0:
            _tag(out, "1", _x(xa) - 13, _y(y0 + PROF_SERPENTE * 0.72))
            _tag(out, "2", _x(eb), _y(y0 + PROF_SERPENTE * 0.5))
            _tag(out, "5", (_x(xsai) + _x(ep)) / 2, _y(y1 + ZONA_DESCARGA / 2))

    # ---- entrada no canto sudeste ----------------------------------------
    ey = _y(FOLGA_SUL + CORREDOR_FUNDO / 2)
    add(f'<line x1="{_x(LARGURA)+96:.1f}" y1="{ey:.1f}" '
        f'x2="{_x(LARGURA)+8:.1f}" y2="{ey:.1f}" {FLOW}/>')
    add(f'<line x1="{_x(LARGURA)+8:.1f}" y1="{ey:.1f}" '
        f'x2="{_x(LARGURA-0.6):.1f}" y2="{_y(FOLGA_SUL+0.6):.1f}" {FLOW}/>')
    add(f'<text x="{_x(LARGURA)+16}" y="{ey-12}" font-size="15" '
        f'font-weight="bold" fill="#c0392b">ENTRADA</text>')
    add(f'<text x="{_x(LARGURA)+16}" y="{ey+30}" font-size="11" '
        f'fill="#c0392b">canto sudeste</text>')
    _tag(out, "4", _x(LARGURA) + 8, ey - 30)

    # ---- saidas por S2 e S8 ----------------------------------------------
    for porta in SAIDAS_PORTAS:
        xm = centro + (PORTAS_SUL[porta] - PORTAS_SUL["S5"])
        cx = _x(xm)
        dx = -46 if xm < centro else 46
        yq = hy + 34
        add(f'<line x1="{cx:.1f}" y1="{hy+30}" x2="{cx:.1f}" y2="{yq:.1f}" '
            f'stroke="#1e8449" stroke-width="2.2"/>')
        add(f'<line x1="{cx:.1f}" y1="{yq:.1f}" x2="{cx+dx:.1f}" '
            f'y2="{yq:.1f}" {EXIT}/>')

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

    # ---- quantitativo de barreira ----------------------------------------
    ty = _y(0) + 52
    add(f'<text x="{_x(0)}" y="{ty}" font-size="15" font-weight="bold" '
        f'fill="#1a1a1a">Separadores de barreira — Ring 3 apenas</text>')
    ty += 24
    cols = [0, 26, 300, 500, 590]
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
    add(f'<text x="{_x(0)+cols[1]}" y="{ty}" {SM}>Em mãos hoje (item d do '
        f'orçamento)</text>')
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
    for t in [
        f'Capacidade: {r["pessoas_total"]:.0f} pessoas nos serpenteados '
        f'({r["pessoas_bloco"]:.0f} por corredor, a {PASSO_PESSOA:.2f} m por '
        f'pessoa) + ~490 na reserva de flanco.',
        f'Blocos a {PASSO_BLOCOS:.1f} m de eixo a eixo; portas S4/S5/S6 a '
        f'{PASSO_PORTAS:.1f} m. A baliza de saída de cada corredor caminha '
        + ", ".join(f"{d:.1f} m até {pt}" for (_, pt), d in zip(ENTRADAS, desvios()))
        + f' na faixa de descarga de {ZONA_DESCARGA:.0f} m.',
        'Este quantitativo cobre SOMENTE o Ring 3. O interior do Hall 2 tem '
        'necessidade própria, ainda não dimensionada.',
        'Posições das portas lidas na prancheta do Posto. Aferir em campo a '
        'distância do bordo oeste do Ring 3 ao canto sudoeste do Hall 2, que '
        'translada todo o conjunto.',
    ]:
        add(f'<text x="{_x(0)}" y="{ty}" {SM}>{t}</text>')
        ty += 17
    add('</svg>')

    SAIDA.write_text("\n".join(out), encoding="utf-8")
    return r


def main():
    r = resumo()
    print(f"Ring 3 {LARGURA:.0f} × {PROFUNDIDADE:.0f} m | serpenteado "
          f"{PROF_SERPENTE:.1f} m | {BALIZAS} balizas de {LARG_BALIZA:.2f} m")
    dv = desvios()
    print(f"Blocos a {PASSO_BLOCOS:.1f} m de eixo; portas S4/S5/S6 a "
          f"{PASSO_PORTAS:.1f} m.")
    print("Desvio da baliza de saída até a porta, por corredor: "
          + ", ".join(
              f"{n}→{pt} {d:.1f} m "
              f"({math.degrees(math.atan(d/ZONA_DESCARGA)):.0f}°)"
              for (n, pt), d in zip(ENTRADAS, dv)) + "\n")
    cab = f"{'':>3} {'Componente':<40} {'Cálculo':<34} {'metros':>8} {'sep.':>6}"
    print(cab); print("-" * len(cab))
    for tag, nome, calc, m, u in r["itens"]:
        print(f"{tag:>2}. {nome:<40} {calc:<34} {m:>8.1f} {u:>6}")
    print("-" * len(cab))
    print(f"{'':>3} {'TOTAL DO RING 3':<40} {'':<34} {r['metros']:>8.1f} "
          f"{r['unidades']:>6}")
    print(f"{'':>3} {'Em mãos (item d)':<40} {'':<34} {200.0:>8.1f} "
          f"{SEPARADORES_EM_MAOS:>6}")
    print(f"{'':>3} {'A ADQUIRIR':<40} {'':<34} "
          f"{r['faltam']*METROS_POR_UNIDADE:>8.1f} {r['faltam']:>6}"
          f"   ≈ EUR {r['custo']:,.0f}")
    print(f"\nCapacidade: {r['pessoas_total']:.0f} nos serpenteados "
          f"({r['pessoas_bloco']:.0f} por corredor) + ~490 de flanco.")
    desenha()
    print(f"Desenho: {SAIDA.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
