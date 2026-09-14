"""Gera a pagina visual do plano de sinalizacao a partir de saidas/sinalizacao.json.

A peca central e a planta em escala do Hall 2 desenhada com as coordenadas
reais da prancheta Hamad_Final: cada bloco aparece onde vai ficar, na cor da
sua porta, rotulado com as secoes que o banner daquele bloco vai exibir.
"""

import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
SAIDAS = BASE / "saidas"

HALL_X, HALL_Y = 50.2, 44.5          # m, planta do RDS Hall 2
MESA_LARG, MESA_PROF = 1.8, 1.6      # m, modulo assumido da mesa
PORTAS_X = {"A": 9.0, "B": 25.75, "C": 41.0}   # premissa P3
COR = {"A": "a", "B": "b", "C": "c"}


def fmt(n) -> str:
    return f"{int(n):,}".replace(",", ".")


def sx(x: float) -> float:
    return x


def sy(y: float) -> float:
    """SVG cresce para baixo; a planta e desenhada com o norte em cima."""
    return HALL_Y - y


def retangulo_mesa(parede: str, coord: float) -> tuple:
    """Canto superior esquerdo e dimensoes da mesa, em metros de planta."""
    if parede == "OESTE":
        return 0.8 - MESA_PROF / 2, sy(coord) - MESA_LARG / 2, MESA_PROF, MESA_LARG
    if parede == "LESTE":
        return 47.3 - MESA_PROF / 2, sy(coord) - MESA_LARG / 2, MESA_PROF, MESA_LARG
    return coord - MESA_LARG / 2, sy(43.6) - MESA_PROF / 2, MESA_LARG, MESA_PROF


def planta(plano: dict) -> str:
    """SVG da planta, 1 unidade = 1 m, com margem para os rotulos."""
    M, TOPO = 10.0, 14.0
    vb = f"{-M} {-TOPO} {HALL_X + 2 * M} {HALL_Y + TOPO + M}"
    p = [f'<svg class="planta" viewBox="{vb}" role="img" '
         f'aria-label="Planta do Hall 2 com as 28 mesas agrupadas em 16 blocos, '
         f'coloridos pela porta que os atende">']

    p.append(f'<rect x="0" y="0" width="{HALL_X}" height="{HALL_Y}" class="salao"/>')

    # rosa dos ventos: o salao esta em orientacao L-O
    p.append(f'<g class="rosa"><text x="{HALL_X/2:.1f}" y="-10.4" '
             f'text-anchor="middle">N</text>'
             f'<text x="-4.4" y="{HALL_Y/2:.1f}" text-anchor="middle">O</text>'
             f'<text x="{HALL_X+4.4:.1f}" y="{HALL_Y/2:.1f}" '
             f'text-anchor="middle">L</text></g>')

    for parede in plano["paredes"]:
        c = COR[parede["porta"]]
        nome = parede["parede"]
        for b in parede["blocos"]:
            coords = [b["coord_inicial"], b["coord_final"]]
            caixas = [retangulo_mesa(nome, k) for k in dict.fromkeys(coords)]
            x0 = min(k[0] for k in caixas)
            y0 = min(k[1] for k in caixas)
            x1 = max(k[0] + k[2] for k in caixas)
            y1 = max(k[1] + k[3] for k in caixas)
            pad = 0.55
            p.append(f'<rect class="bloco t-{c}" x="{x0-pad:.2f}" y="{y0-pad:.2f}" '
                     f'width="{x1-x0+2*pad:.2f}" height="{y1-y0+2*pad:.2f}" rx="0.5"/>')
            for (mx, my, mw, mh) in caixas:
                p.append(f'<rect class="mesa t-{c}" x="{mx:.2f}" y="{my:.2f}" '
                         f'width="{mw}" height="{mh}"/>')

            # rotulo do banner, voltado para dentro do salao e fora do tronco
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            if nome == "OESTE":
                tx, ty, anc = x1 + 3.4, cy, "start"
                linhas = [" ".join(str(s) for s in b["secoes"][i:i + 2])
                          for i in range(0, len(b["secoes"]), 2)]
            elif nome == "LESTE":
                tx, ty, anc = x0 - 3.4, cy, "end"
                linhas = [" ".join(str(s) for s in b["secoes"][i:i + 2])
                          for i in range(0, len(b["secoes"]), 2)]
            else:
                linhas = [str(s) for s in b["secoes"]]   # coluna acima do salao
                tx, anc = cx, "middle"
                ty = y0 - 1.0 - (len(linhas) - 1) * 1.5
            dy0 = -(len(linhas) - 1) * 0.75 if nome != "NORTE" else 0.0
            p.append(f'<text class="rot t-{c}" x="{tx:.2f}" y="{ty:.2f}" '
                     f'text-anchor="{anc}">')
            for i, ln in enumerate(linhas):
                p.append(f'<tspan x="{tx:.2f}" dy="{dy0 if i == 0 else 1.5:.2f}">'
                         f'{ln}</tspan>')
            p.append('</text>')

        # porta + seta de encaminhamento
        px = PORTAS_X[parede["porta"]]
        p.append(f'<rect class="porta t-{c}" x="{px-2.2:.2f}" y="{HALL_Y-0.45:.2f}" '
                 f'width="4.4" height="0.9"/>')
        p.append(f'<text class="letra t-{c}" x="{px:.2f}" y="{HALL_Y+4.2:.2f}" '
                 f'text-anchor="middle">{parede["porta"]}</text>')
        tronco = {
            "OESTE": f'M {px:.2f} {HALL_Y} L {px:.2f} {sy(5):.2f} '
                     f'L 3.8 {sy(5):.2f} L 3.8 {sy(38):.2f}',
            "LESTE": f'M {px:.2f} {HALL_Y} L {px:.2f} {sy(3):.2f} '
                     f'L 44.3 {sy(3):.2f} L 44.3 {sy(38):.2f}',
            "NORTE": f'M {px:.2f} {HALL_Y} L {px:.2f} {sy(40):.2f}',
        }[nome]
        p.append(f'<path class="fluxo t-{c}" d="{tronco}"/>')
        ponta = (3.8, sy(38)) if nome == "OESTE" else (
            (44.3, sy(38)) if nome == "LESTE" else (px, sy(40)))
        p.append(f'<path class="ponta t-{c}" d="M {ponta[0]-0.75:.2f} '
                 f'{ponta[1]+1.5:.2f} L {ponta[0]:.2f} {ponta[1]-0.3:.2f} '
                 f'L {ponta[0]+0.75:.2f} {ponta[1]+1.5:.2f} Z"/>')

    p.append('</svg>')
    return "\n".join(p)


def tabela_blocos(parede: dict) -> str:
    linhas = []
    for b in parede["blocos"]:
        pos = (f'{b["coord_inicial"]:.2f}'.replace(".", ",") + " m"
               if b["tipo"] == "ISOLADA" else
               f'{b["coord_inicial"]:.2f}'.replace(".", ",") + "–"
               + f'{b["coord_final"]:.2f}'.replace(".", ",") + " m")
        secoes = "".join(f'<span class="sec">{s}</span>' for s in b["secoes"])
        tipo = "par" if b["tipo"] == "PAR" else "isolada"
        linhas.append(
            f'<tr><th scope="row">B{parede["porta"]}{b["ordem"]}</th>'
            f'<td><span class="tag tag-{tipo}">{tipo}</span></td>'
            f'<td class="num">{pos}</td>'
            f'<td class="secs">{secoes}</td>'
            f'<td class="num">{fmt(b["aptos"])}</td>'
            f'<td class="num">{fmt(b["comparecimento"])}</td></tr>')
    return "\n".join(linhas)


def main() -> None:
    plano = json.loads((SAIDAS / "sinalizacao.json").read_text(encoding="utf-8"))
    html = (BASE / "scripts" / "sinalizacao_template.html").read_text(encoding="utf-8")

    tiles, tabelas, listas = [], [], []
    lookup = []
    for p in plano["paredes"]:
        c = COR[p["porta"]]
        por_mesa = round(p["comparecimento"] / p["n_mesas"])
        tiles.append(
            f'<article class="tile t-{c}"><p class="tile-k">Porta {p["porta"]}</p>'
            f'<p class="tile-w">parede {p["parede"].lower()}</p>'
            f'<dl><div><dt>mesas</dt><dd>{p["n_mesas"]}</dd></div>'
            f'<div><dt>blocos</dt><dd>{len(p["blocos"])}</dd></div>'
            f'<div><dt>seções</dt><dd>{len(p["secoes"])}</dd></div>'
            f'<div><dt>aptos</dt><dd>{fmt(p["aptos"])}</dd></div>'
            f'<div class="hi"><dt>compar./mesa</dt><dd>{por_mesa}</dd></div></dl>'
            f'</article>')
        tabelas.append(
            f'<section class="wall t-{c}"><h3>Porta {p["porta"]} '
            f'<span>parede {p["parede"].lower()} · {p["n_pares"]} pares + '
            f'{p["n_isoladas"]} isolada(s)</span></h3>'
            f'<div class="scroll"><table><thead><tr>'
            f'<th scope="col">Peça</th><th scope="col">Tipo</th>'
            f'<th scope="col">Posição na parede</th>'
            f'<th scope="col">Seções impressas no banner</th>'
            f'<th scope="col">Aptos</th><th scope="col">Compar.</th>'
            f'</tr></thead><tbody>{tabela_blocos(p)}</tbody></table></div></section>')
        listas.append(
            f'<article class="lista t-{c}"><h4>Porta {p["porta"]}</h4>'
            f'<p class="sub">{len(p["secoes"])} seções · {fmt(p["aptos"])} aptos</p>'
            f'<div class="grid-sec">'
            + "".join(f'<span class="sec">{s}</span>' for s in p["secoes"])
            + '</div></article>')
        for b in p["blocos"]:
            for s in b["secoes"]:
                lookup.append((s, p["porta"], p["parede"].title()))

    lookup.sort()
    linhas_lookup = "".join(
        f'<li><span class="sec">{s}</span>'
        f'<span class="porta-pin t-{COR[pt]}">{pt}</span>'
        f'<span class="pd">{pr.lower()}</span></li>' for s, pt, pr in lookup)

    html = (html
            .replace("<!--TILES-->", "\n".join(tiles))
            .replace("<!--PLANTA-->", planta(plano))
            .replace("<!--TABELAS-->", "\n".join(tabelas))
            .replace("<!--LISTAS-->", "\n".join(listas))
            .replace("<!--LOOKUP-->", linhas_lookup)
            .replace("{{APTOS}}", fmt(plano["total_aptos"]))
            .replace("{{COMP}}", fmt(plano["total_comparecimento"])))

    destino = SAIDAS / "plano_sinalizacao.html"
    destino.write_text(html, encoding="utf-8")
    print(f"Gravado {destino.relative_to(BASE)} ({len(html):,} bytes)")


if __name__ == "__main__":
    main()
