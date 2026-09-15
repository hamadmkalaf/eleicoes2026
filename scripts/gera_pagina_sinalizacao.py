"""Gera a pagina visual do plano de sinalizacao a partir de saidas/sinalizacao.json.

A peca central e a planta em escala do Hall 2 desenhada com as coordenadas
reais da prancheta Hamad_Final: cada bloco aparece onde vai ficar, na cor da
sua porta, rotulado com as secoes que o banner daquele bloco vai exibir.
"""

import json
import math
from pathlib import Path

from plano_sinalizacao import (
    PAREDE_POR_ROT,
    PRANCHETA,
    carrega_urnas,
    descreve_mesa,
    eixo,
)

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



# --- piso: um slot de fila por mesa ------------------------------------------
LANE, PESSOA, FOLGA, MINCAP = 1.0, 0.5, 1.3, 6.0
CANTO = 8.0                                  # quadrado de canto sem fila
PROF_MAX = {"OESTE": 22.0, "LESTE": 22.0, "NORTE": 19.0}
# perfil horario assumido de chegada, 8h-17h, com pico matinal
PERFIL = [.12, .15, .16, .14, .11, .09, .08, .08, .07]
SEG_POR_VOTO = 60


def fila_maxima(comparecimento: float) -> float:
    """Pessoas na fila da mesa no pior momento do dia, modelo horario simples."""
    servico = 3600 / SEG_POR_VOTO
    q = pico = 0.0
    for fatia in PERFIL:
        q = max(0.0, q + comparecimento * fatia - servico)
        pico = max(pico, q)
    return pico


def slots(plano: dict) -> list:
    """Dimensiona o slot de piso de cada mesa: largura pelo vao ate a vizinha,
    profundidade pelo tamanho projetado da fila daquela mesa."""
    urnas, residencia = carrega_urnas()
    porta = {p["parede"]: p["porta"] for p in plano["paredes"]}
    bloco = {m: f'B{p["porta"]}{b["ordem"]}'
             for p in plano["paredes"] for b in p["blocos"] for m in b["mesas"]}
    paredes = {}
    for mesa in PRANCHETA:
        paredes.setdefault(PAREDE_POR_ROT[mesa["rot"]], []).append(mesa)

    out = []
    for parede, mesas in paredes.items():
        mesas = sorted(mesas, key=eixo)
        for i, m in enumerate(mesas):
            c = eixo(m)
            ant = c - eixo(mesas[i - 1]) if i else 6.0
            pos = eixo(mesas[i + 1]) - c if i < len(mesas) - 1 else 6.0
            larg = min(3.9, max(2.0, min(ant, pos)))
            vias = max(1, int(larg // LANE))
            d = descreve_mesa(m["n"], urnas, residencia)
            metros = fila_maxima(d["comparecimento"]) * PESSOA
            cap = max(MINCAP, FOLGA * metros)
            prof = cap / vias
            no_canto = ((parede in ("OESTE", "LESTE") and c > 43.6 - CANTO)
                        or (parede == "NORTE" and not 12.5 < c < 39.0))
            limite = CANTO if no_canto else PROF_MAX[parede]
            out.append({
                "mesa": m["n"], "bloco": bloco[m["n"]], "porta": porta[parede],
                "parede": parede, "coord": c, "secoes": d["secoes"],
                "comparecimento": round(d["comparecimento"]),
                "fila": round(metros, 1), "cap": round(cap, 1),
                "larg": round(larg, 2), "vias": vias, "prof": round(prof, 1),
                "limite": limite, "estoura": prof > limite + .05,
                "tipo": 1 if cap <= 6.5 else (2 if vias == 1 or cap <= 30 else 3),
            })
    return sorted(out, key=lambda s: -s["cap"])


def caixa_slot(s: dict) -> tuple:
    """Retangulo do slot em coordenadas de planta (x, y, largura, altura)."""
    prof = min(s["prof"], s["limite"])
    if s["parede"] == "OESTE":
        return 1.6, sy(s["coord"]) - s["larg"] / 2, prof, s["larg"]
    if s["parede"] == "LESTE":
        return 46.5 - prof, sy(s["coord"]) - s["larg"] / 2, prof, s["larg"]
    return s["coord"] - s["larg"] / 2, sy(43.6) + 0.8, s["larg"], prof


def planta_piso(plano: dict, ss: list) -> str:
    """SVG do plano de colagem: cada mesa com a sua via de fila."""
    M, TOPO = 10.0, 12.0
    p = [f'<svg class="planta piso" viewBox="{-M} {-TOPO} {HALL_X + 2 * M} '
         f'{HALL_Y + TOPO + M}" role="img" aria-label="Plano de colagem das '
         f'filas no piso: uma via por mesa, perpendicular a sua parede">']
    p.append(f'<rect x="0" y="0" width="{HALL_X}" height="{HALL_Y}" class="salao"/>')
    p.append(f'<g class="rosa"><text x="{HALL_X/2:.1f}" y="-8.4" '
             f'text-anchor="middle">N</text></g>')

    for s in sorted(ss, key=lambda k: k["mesa"]):
        c = COR[s["porta"]]
        x, y, w, h = caixa_slot(s)
        alerta = " alerta" if s["estoura"] else ""
        p.append(f'<rect class="slot t-{c}{alerta}" x="{x:.2f}" y="{y:.2f}" '
                 f'width="{w:.2f}" height="{h:.2f}"/>')
        # divisorias internas da serpentina
        if s["tipo"] == 3:
            for k in range(1, s["vias"]):
                if s["parede"] == "NORTE":
                    dx = x + w * k / s["vias"]
                    p.append(f'<line class="via t-{c}" x1="{dx:.2f}" y1="{y:.2f}" '
                             f'x2="{dx:.2f}" y2="{y+h:.2f}"/>')
                else:
                    dy = y + h * k / s["vias"]
                    p.append(f'<line class="via t-{c}" x1="{x:.2f}" y1="{dy:.2f}" '
                             f'x2="{x+w:.2f}" y2="{dy:.2f}"/>')
        # rotulo na cauda da fila, que e por onde o eleitor entra
        if s["parede"] == "OESTE":
            tx, ty, anc = x + w + 0.8, y + h / 2 + 0.45, "start"
            linhas = [" ".join(str(v) for v in s["secoes"])]
        elif s["parede"] == "LESTE":
            # fora do salao: dentro, colidiria com os rotulos da parede norte
            tx, ty, anc = 47.8, y + h / 2 + 0.45, "start"
            linhas = [" ".join(str(v) for v in s["secoes"])]
        else:   # norte: coluna, senao os rotulos vizinhos se sobrepoem
            tx, ty, anc = x + w / 2, y + h + 1.8, "middle"
            linhas = [str(v) for v in s["secoes"]]
        p.append(f'<text class="rot t-{c}" x="{tx:.2f}" y="{ty:.2f}" '
                 f'text-anchor="{anc}">')
        for i, ln in enumerate(linhas):
            p.append(f'<tspan x="{tx:.2f}" dy="{0 if i == 0 else 1.5:.2f}">{ln}</tspan>')
        p.append('</text>')

    for parede in ("OESTE", "NORTE", "LESTE"):
        pt = {"OESTE": "A", "NORTE": "B", "LESTE": "C"}[parede]
        px = PORTAS_X[pt]
        p.append(f'<rect class="porta t-{COR[pt]}" x="{px-2.2:.2f}" '
                 f'y="{HALL_Y-0.45:.2f}" width="4.4" height="0.9"/>')
        p.append(f'<text class="letra t-{COR[pt]}" x="{px:.2f}" '
                 f'y="{HALL_Y+4.2:.2f}" text-anchor="middle">{pt}</text>')
    p.append(f'<text class="centro" x="27.0" y="{sy(10.5):.2f}" text-anchor="middle">'
             f'ZONA LIVRE DE CIRCULAÇÃO</text>')
    p.append(f'<text class="centro sub" x="27.0" y="{sy(8.1):.2f}" '
             f'text-anchor="middle">o eleitor entra na via pela cauda</text>')
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
    ss = slots(plano)
    plano["piso"] = ss
    (SAIDAS / "sinalizacao.json").write_text(
        json.dumps(plano, ensure_ascii=False, indent=2), encoding="utf-8")
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

    fita = 0.0
    decais = 0
    linhas_piso = []
    for s in sorted(ss, key=lambda k: (-k["cap"], k["mesa"])):
        prof = min(s["prof"], s["limite"])
        fita += prof if s["tipo"] == 1 else (s["vias"] + 1) * prof
        decais += 1 + math.ceil(s["cap"] / 5)
        nome = {1: "marca de início", 2: "via simples", 3: "serpentina"}[s["tipo"]]
        aviso = ' class="alerta"' if s["estoura"] else ""
        secs = "".join(f'<span class="sec">{v}</span>' for v in s["secoes"])
        linhas_piso.append(
            f'<tr{aviso}><th scope="row" class="t-{COR[s["porta"]]}">{s["bloco"]}</th>'
            f'<td class="secs">{secs}</td>'
            f'<td class="num">{fmt(s["comparecimento"])}</td>'
            f'<td class="num">{round(s["fila"] / PESSOA)}</td>'
            f'<td class="num">{str(s["cap"]).replace(".", ",")} m</td>'
            f'<td class="num">{str(s["larg"]).replace(".", ",")} m · {s["vias"]}</td>'
            f'<td class="num">{str(round(prof, 1)).replace(".", ",")} m</td>'
            f'<td>{nome}{" ⚠" if s["estoura"] else ""}</td></tr>')
    estouram = [s for s in ss if s["estoura"]]

    html = (html
            .replace("<!--PISO-->", planta_piso(plano, ss))
            .replace("<!--TABPISO-->", "\n".join(linhas_piso))
            .replace("{{FITA}}", f"{fita:.0f}")
            .replace("{{DECAIS}}", str(decais))
            .replace("{{VIA}}", f'{sum(s["cap"] for s in ss):.0f}')
            .replace("{{NESTOURA}}", str(len(estouram)))
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
