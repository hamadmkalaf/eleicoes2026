"""Layout do Ring 3: tres corredores serpenteados e calculo de barreiras.

Desenho pedido pelo Posto:
  - acesso pelo canto SUDESTE;
  - corredor estreito de distribuicao no "fundo" (bordo sul), de leste a oeste;
  - tres corredores serpenteados ("Disney queue") que dele derivam, de oeste
    para leste: ENTRADA A, ENTRADA B e ENTRADA C;
  - descarga ao norte, cada corredor alinhado a uma porta do Hall 2.

Piso pavimentado. Espaco alugado desde a vespera, sem carros estacionados.

PORTAS. A planta RDS_Hall_2_Floorplan_(1).pdf nao usa rotulos S4/S5/S6: ela
numera as aberturas de 2.1 a 2.23. As posicoes abaixo foram medidas na pagina
2 dessa planta e convertidas pela escala aferida (~9,0 pt/m, conferida contra
os 50,2 m de largura e os 44,5 m de comprimento declarados).

Gera saidas/layout_ring3.svg em escala e imprime a tabela de barreiras.
Uso:  python3 scripts/layout_ring3.py
"""

from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "saidas" / "layout_ring3.svg"

# --- fachada sul do Hall 2, a que encara o Ring 3 --------------------------
# metros a partir do canto SUDOESTE do Hall 2 (fachada de 50,2 m)
PORTAS_SUL = {
    "2.7": 18.5, "2.6": 22.3, "2.5": 24.4, "2.4": 28.5,
    "2.3": 32.4, "2.2": 34.5, "2.1": 38.5,
}
# As tres aberturas isoladas ficam a 10,0 m uma da outra e servem de entrada;
# os pares intermediarios ficam livres para saida, sem cruzar fluxos.
ENTRADAS = [("A", "2.7"), ("B", "2.4"), ("C", "2.1")]
SAIDAS_PORTAS = ["2.6", "2.5", "2.3", "2.2"]

# --- dimensoes do Ring 3 (fotogrametria, +-10-15% linear) ------------------
LARGURA = 39.0          # leste-oeste, m
PROFUNDIDADE = 35.0     # sul-norte, m; o norte encara o Hall 2

# --- faixas no eixo sul-norte ---------------------------------------------
FOLGA_SUL = 1.5
CORREDOR_FUNDO = 2.5    # corredor estreito de distribuicao
ZONA_DESCARGA = 4.0     # leque de saida ate as portas

# --- parametros de fila ----------------------------------------------------
LARG_BALIZA = 1.40      # largura util de cada baliza, m
PASSO_PESSOA = 0.50     # avanco por pessoa na fila, m
CORREDOR_EGRESSO = 2.0  # entre blocos, para evacuacao
METROS_POR_UNIDADE = 2.0   # 100 separadores = 200 m (item d do orcamento)
EUR_POR_METRO = 6.51       # EUR 1.303,00 / 200 m

PROF_SERPENTE = PROFUNDIDADE - FOLGA_SUL - CORREDOR_FUNDO - ZONA_DESCARGA
PASSO_ENTRADAS = 10.0   # espacamento entre 2.7, 2.4 e 2.1

# Balizas por bloco. 5 e o maximo compativel com o espacamento de 10,0 m das
# portas: 5 x 1,40 = 7,0 m de bloco deixa 3,0 m de corredor de egresso entre
# blocos vizinhos. 7 balizas dariam 9,8 m e so 0,2 m de vao — inviavel.
BALIZAS_PROJETO = 5


def dimensiona(n_balizas, passo_entradas=PASSO_ENTRADAS):
    """Capacidade e barreira para n balizas por bloco, nos tres blocos.

    O serpenteado exige numero IMPAR de balizas: entra-se pelo sul e a ultima
    baliza tem de correr para o norte, onde ficam as portas.
    """
    if n_balizas % 2 == 0:
        raise ValueError("numero de balizas deve ser impar")
    larg_bloco = n_balizas * LARG_BALIZA
    vao = passo_entradas - larg_bloco          # egresso entre blocos vizinhos

    fila_m = n_balizas * PROF_SERPENTE
    # n balizas exigem n+1 corridas de separador; as internas abrem o retorno
    barreira_bloco = 2 * PROF_SERPENTE + (n_balizas - 1) * (PROF_SERPENTE - LARG_BALIZA)

    span = 2 * passo_entradas + larg_bloco     # largura ocupada pelos 3 blocos
    fundo = 2 * (span + 4.0) - 3 * 1.5         # dois lados, menos os 3 vaos
    garganta, descarga = 10.0, 3 * 2 * 6.0
    fixa = fundo + garganta + descarga
    total = 3 * barreira_bloco + fixa

    return {
        "balizas": n_balizas,
        "larg_bloco": larg_bloco,
        "vao_egresso": vao,
        "cabe": vao >= CORREDOR_EGRESSO and span + 8.0 <= LARGURA,
        "span": span,
        "fila_m_bloco": fila_m,
        "pessoas_bloco": fila_m / PASSO_PESSOA,
        "pessoas_total": 3 * fila_m / PASSO_PESSOA,
        "barreira_blocos": 3 * barreira_bloco,
        "barreira_fixa": fixa,
        "barreira_m": total,
        "unidades": total / METROS_POR_UNIDADE,
        "custo_extra_eur": max(0.0, total - 200.0) * EUR_POR_METRO,
    }


# ---------------------------------------------------------------- desenho --

ESC = 19
MARGEM_ESQ, MARGEM_DIR, MARGEM_TOPO, MARGEM_BASE = 80, 210, 130, 180

# Estilos aplicados inline: varios renderizadores de SVG ignoram <style>.
SEP = 'stroke="#c0392b" stroke-width="2.4" stroke-linecap="round"'
FLOW = ('stroke="#2471a3" stroke-width="2.2" fill="none" '
        'stroke-dasharray="7 5" marker-end="url(#a)"')
LBL = 'font-size="13" fill="#1a1a1a"'
SM = 'font-size="11" fill="#555"'
BIG = 'font-size="16" font-weight="bold" fill="#1a1a1a"'
DIM = 'font-size="11" fill="#0a7d55"'


def _x(m):
    return MARGEM_ESQ + m * ESC


def _y(m):
    """y do SVG a partir de metros medidos do bordo SUL do Ring 3."""
    return MARGEM_TOPO + (PROFUNDIDADE - m) * ESC


def desenha(n_balizas):
    p = dimensiona(n_balizas)
    lb = p["larg_bloco"]
    y0 = FOLGA_SUL + CORREDOR_FUNDO
    y1 = y0 + PROF_SERPENTE

    centro = LARGURA / 2
    eixos = [centro - PASSO_ENTRADAS, centro, centro + PASSO_ENTRADAS]
    blocos = [(nome, porta, e - lb / 2, e + lb / 2)
              for (nome, porta), e in zip(ENTRADAS, eixos)]

    W = int(LARGURA * ESC + MARGEM_ESQ + MARGEM_DIR)
    H = int(PROFUNDIDADE * ESC + MARGEM_TOPO + MARGEM_BASE)
    s, add = [], None
    out = []
    add = out.append

    add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" font-family="Helvetica,Arial,sans-serif">')
    add('<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" '
        'markerWidth="6" markerHeight="6" orient="auto">'
        '<path d="M0,0 L10,5 L0,10 z" fill="#2471a3"/></marker></defs>')
    add(f'<rect width="{W}" height="{H}" fill="#fbfbf9"/>')
    add(f'<text x="{_x(0)}" y="36" font-size="21" font-weight="bold" '
        f'fill="#1a1a1a">Ring 3 — layout base de filas</text>')
    add(f'<text x="{_x(0)}" y="57" {SM}>Acesso pelo canto sudeste · corredor '
        f'de distribuição no fundo · três serpenteados alinhados às portas da '
        f'fachada sul do Hall 2</text>')

    # fachada sul do Hall 2
    hy = MARGEM_TOPO - 58
    add(f'<rect x="{_x(-2)}" y="{hy}" width="{(LARGURA+4)*ESC}" height="28" '
        f'fill="#e8eef4" stroke="#8fa6bb"/>')
    add(f'<text x="{_x(-1)}" y="{hy+19}" {BIG}>HALL 2</text>')
    for nome, porta, xa, xb in blocos:
        cx = _x((xa + xb) / 2)
        add(f'<rect x="{cx-22}" y="{hy+22}" width="44" height="9" fill="#2471a3"/>')
        add(f'<text x="{cx}" y="{hy+48}" {LBL} text-anchor="middle" '
            f'font-weight="bold">porta {porta}</text>')
    for i, e in enumerate(eixos[:-1]):
        cx = _x(e + PASSO_ENTRADAS / 2)
        add(f'<rect x="{cx-16}" y="{hy+22}" width="32" height="9" fill="#7f8c8d"/>')
        add(f'<text x="{cx}" y="{hy+48}" {SM} text-anchor="middle">'
            f'{"/".join(SAIDAS_PORTAS[i*2:i*2+2])} · saída</text>')

    # contorno do Ring 3
    add(f'<rect x="{_x(0)}" y="{_y(PROFUNDIDADE)}" width="{LARGURA*ESC}" '
        f'height="{PROFUNDIDADE*ESC}" fill="#fff" stroke="#333" stroke-width="2"/>')

    # corredor de distribuicao no fundo
    add(f'<rect x="{_x(0)}" y="{_y(y0)}" width="{LARGURA*ESC}" '
        f'height="{CORREDOR_FUNDO*ESC}" fill="#fdf3e3" stroke="#dfa94a" '
        f'stroke-dasharray="5 3"/>')
    add(f'<text x="{_x(0.6)}" y="{_y(y0)+13}" {SM}>'
        f'corredor de distribuição — {CORREDOR_FUNDO:.1f} m</text>')

    # blocos serpenteados
    for nome, porta, xa, xb in blocos:
        add(f'<rect x="{_x(xa)}" y="{_y(y1)}" width="{lb*ESC}" '
            f'height="{PROF_SERPENTE*ESC}" fill="#f3f7fa" stroke="#d5e2ec"/>')
        for j in range(n_balizas + 1):
            xs = _x(xb - j * LARG_BALIZA)
            if j in (0, n_balizas):
                ya, yb = _y(y1), _y(y0)
            elif j % 2 == 1:
                ya, yb = _y(y1 - LARG_BALIZA), _y(y0)      # retorno pelo topo
            else:
                ya, yb = _y(y1), _y(y0 + LARG_BALIZA)      # retorno pela base
            add(f'<line x1="{xs:.1f}" y1="{ya:.1f}" x2="{xs:.1f}" '
                f'y2="{yb:.1f}" {SEP}/>')
        # rota efetiva de caminhamento, entrando pela baliza mais a leste
        pts = []
        for j in range(n_balizas):
            xc = _x(xb - (j + 0.5) * LARG_BALIZA)
            sobe = (j % 2 == 0)
            pts += [(xc, _y(y0 + 0.4) if sobe else _y(y1 - 0.4)),
                    (xc, _y(y1 - 0.4) if sobe else _y(y0 + 0.4))]
        d = " ".join(f"{a:.1f},{b:.1f}" for a, b in pts)
        add(f'<polyline points="{d}" fill="none" stroke="#2471a3" '
            f'stroke-width="1.7" stroke-linejoin="round" opacity="0.85"/>')

        cx = _x((xa + xb) / 2)
        add(f'<text x="{cx}" y="{_y(y1)-26}" {BIG} text-anchor="middle">'
            f'ENTRADA {nome}</text>')
        add(f'<text x="{cx}" y="{_y(y1)-11}" {SM} text-anchor="middle">'
            f'{n_balizas} balizas · {p["pessoas_bloco"]:.0f} pessoas</text>')
        # entra pelo sul-leste do bloco, sai pelo norte-oeste rumo a porta
        add(f'<line x1="{_x(xb-LARG_BALIZA/2):.1f}" y1="{_y(y0-0.2):.1f}" '
            f'x2="{_x(xb-LARG_BALIZA/2):.1f}" y2="{_y(y0+0.9):.1f}" {FLOW}/>')
        add(f'<line x1="{_x(xa+LARG_BALIZA/2):.1f}" y1="{_y(y1):.1f}" '
            f'x2="{_x(xa+LARG_BALIZA/2):.1f}" y2="{hy+34}" {FLOW}/>')

    # entrada no canto sudeste
    ey = _y(FOLGA_SUL + CORREDOR_FUNDO / 2)
    add(f'<line x1="{_x(LARGURA)+92:.1f}" y1="{ey:.1f}" '
        f'x2="{_x(LARGURA)+6:.1f}" y2="{ey:.1f}" {FLOW}/>')
    add(f'<line x1="{_x(LARGURA)+6:.1f}" y1="{ey:.1f}" '
        f'x2="{_x(LARGURA-0.6):.1f}" y2="{_y(FOLGA_SUL+0.6):.1f}" {FLOW}/>')
    add(f'<text x="{_x(LARGURA)+14}" y="{ey-14}" font-size="15" '
        f'font-weight="bold" fill="#c0392b">ENTRADA</text>')
    add(f'<text x="{_x(LARGURA)+14}" y="{ey+30}" font-size="11" fill="#c0392b">'
        f'canto sudeste</text>')
    # sentido do corredor de fundo, leste para oeste
    yf = _y(FOLGA_SUL + 0.6)
    add(f'<line x1="{_x(LARGURA-1.2):.1f}" y1="{yf:.1f}" x2="{_x(1.2):.1f}" '
        f'y2="{yf:.1f}" {FLOW}/>')

    # cotas
    add(f'<text x="{_x(LARGURA/2)}" y="{_y(0)+26}" {DIM} text-anchor="middle">'
        f'{LARGURA:.0f} m (leste–oeste)</text>')
    ymid = _y(PROFUNDIDADE/2)
    add(f'<text x="{_x(0)-16}" y="{ymid}" {DIM} text-anchor="middle" '
        f'transform="rotate(-90 {_x(0)-16} {ymid})">'
        f'{PROFUNDIDADE:.0f} m (sul–norte)</text>')
    ys = _y(y0+PROF_SERPENTE/2)
    add(f'<text x="{_x(LARGURA)+8}" y="{ys}" {DIM} text-anchor="middle" '
        f'transform="rotate(-90 {_x(LARGURA)+8} {ys})">'
        f'serpenteado {PROF_SERPENTE:.0f} m</text>')

    # legenda
    ly = _y(0) + 52
    linhas = [
        f'Serpenteado: {n_balizas} balizas de {LARG_BALIZA:.2f} m de largura × '
        f'{PROF_SERPENTE:.1f} m de profundidade, por corredor.',
        f'Eixos dos corredores a {PASSO_ENTRADAS:.1f} m entre si, coincidindo '
        f'com as portas {", ".join(pt for _, pt in ENTRADAS)}. Vão de egresso '
        f'entre blocos: {p["vao_egresso"]:.1f} m.',
        f'Capacidade de projeto: {p["pessoas_total"]:.0f} pessoas '
        f'({PASSO_PESSOA:.2f} m por pessoa) — {p["pessoas_bloco"]:.0f} por corredor.',
        f'Barreira: {p["barreira_m"]:.0f} m ≈ {p["unidades"]:.0f} separadores de '
        f'{METROS_POR_UNIDADE:.0f} m ({p["barreira_blocos"]:.0f} m nos blocos + '
        f'{p["barreira_fixa"]:.0f} m em fundo, garganta e descarga).',
        'Portas medidas na página 2 de RDS_Hall_2_Floorplan_(1).pdf. A planta '
        'não usa rótulos S4/S5/S6 — confirmar a correspondência.',
        'Transladar o conjunto no eixo leste–oeste até os eixos coincidirem com '
        'as portas: medir em campo a distância do bordo oeste do Ring 3 ao '
        'canto sudoeste do Hall 2.',
    ]
    add(f'<text x="{_x(0)}" y="{ly}" {LBL} font-weight="bold">Notas</text>')
    for i, t in enumerate(linhas):
        add(f'<text x="{_x(0)}" y="{ly+19+i*17}" {SM}>{t}</text>')
    add('</svg>')

    SAIDA.write_text("\n".join(out), encoding="utf-8")
    return p


def main():
    print(f"Ring 3: {LARGURA:.0f} × {PROFUNDIDADE:.0f} m | "
          f"profundidade util do serpenteado: {PROF_SERPENTE:.1f} m")
    print("Fachada sul do Hall 2, metros do canto sudoeste:")
    for k, v in sorted(PORTAS_SUL.items(), key=lambda kv: kv[1]):
        papel = next((f"ENTRADA {n}" for n, pt in ENTRADAS if pt == k), "saída")
        print(f"   porta {k:>4}  {v:5.1f} m   {papel}")
    print(f"   espaçamento entre as três entradas: "
          f"{PORTAS_SUL['2.4']-PORTAS_SUL['2.7']:.1f} m e "
          f"{PORTAS_SUL['2.1']-PORTAS_SUL['2.4']:.1f} m\n")

    cab = (f"{'balizas':>8} {'bloco':>8} {'vão':>6} {'fila/bloco':>11} "
           f"{'CAPACIDADE':>11} {'barreira':>10} {'separadores':>12} "
           f"{'custo extra':>12}")
    print(cab); print("-" * len(cab))
    for n in (3, 5, 7):
        p = dimensiona(n)
        marca = "" if p["cabe"] else "   VÃO INSUFICIENTE"
        print(f"{p['balizas']:>8} {p['larg_bloco']:>7.1f}m {p['vao_egresso']:>5.1f}m "
              f"{p['fila_m_bloco']:>10.0f}m {p['pessoas_total']:>11.0f} "
              f"{p['barreira_m']:>9.0f}m {p['unidades']:>12.0f} "
              f"{p['custo_extra_eur']:>11,.0f}€{marca}")

    p = desenha(BALIZAS_PROJETO)
    print(f"\nDesenho: {SAIDA.relative_to(RAIZ)} ({BALIZAS_PROJETO} balizas).")
    print(f"Disponível: 100 separadores (200 m). "
          f"Faltam {p['unidades']-100:.0f} unidades "
          f"(EUR {p['custo_extra_eur']:,.0f}).")


if __name__ == "__main__":
    main()
