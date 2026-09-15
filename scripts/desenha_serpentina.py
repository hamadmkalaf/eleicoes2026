# -*- coding: utf-8 -*-
"""Desenha as duas orientações de serpentina na zona sul do Hall 2."""
import os, math
from serpentina_hall2 import (layout_ns, layout_lo, resume, HALL_L, HALL_P,
                              NOTCH_X, NOTCH_Y, APRON, MARGEM, Y_CENTRO,
                              LARG_CANAL, parede_para_secoes)

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ESC = 9.6
PW = HALL_L * ESC                 # largura de um painel
MX, MY, GAPP = 46, 152, 66
W = int(2 * PW + GAPP + 2 * MX)
H = int(HALL_P * ESC + MY + 176)

C = {"fundo": "#fbfaf8", "parede": "#1f2933", "secao": "#2f4858",
     "A": "#0e7490", "B": "#7b3f9d", "voto": "#eef2f4", "texto": "#1f2933",
     "suave": "#6b7785", "saida": "#c0392b", "apron": "#fdf6e8",
     "apronL": "#c9a227", "linha": "#b03a2e"}


def mk(ox):
    def X(m): return ox + m * ESC
    def Y(m): return MY + (HALL_P - m) * ESC
    return X, Y


def painel(ox, lay, titulo, subtitulo, y_div=Y_CENTRO, acesso=True):
    X, Y = mk(ox)
    r = resume(lay)
    o = []

    def rect(x, y, w, h, **kw):
        a = " ".join(f'{k.replace("_","-")}="{v}"' for k, v in kw.items())
        return (f'<rect x="{X(x):.1f}" y="{Y(y+h):.1f}" width="{w*ESC:.1f}" '
                f'height="{h*ESC:.1f}" {a}/>')

    def txt(x, y, s, size=10, anchor="middle", fill=C["texto"], weight="400", rot=0):
        t = f' transform="rotate({rot} {X(x):.1f} {Y(y):.1f})"' if rot else ""
        return (f'<text x="{X(x):.1f}" y="{Y(y):.1f}" font-size="{size}" '
                f'text-anchor="{anchor}" fill="{fill}" font-weight="{weight}" '
                f'font-family="Inter, Helvetica, Arial, sans-serif"{t}>{s}</text>')

    def line(x1, y1, x2, y2, **kw):
        a = " ".join(f'{k.replace("_","-")}="{v}"' for k, v in kw.items())
        return (f'<line x1="{X(x1):.1f}" y1="{Y(y1):.1f}" x2="{X(x2):.1f}" '
                f'y2="{Y(y2):.1f}" {a}/>')

    # título do painel
    o.append(f'<text x="{ox}" y="{MY - 62}" font-size="19" font-weight="700" '
             f'fill="{C["texto"]}" font-family="Inter, Helvetica, Arial, sans-serif">{titulo}</text>')
    o.append(f'<text x="{ox}" y="{MY - 43}" font-size="11.5" fill="{C["suave"]}" '
             f'font-family="Inter, Helvetica, Arial, sans-serif">{subtitulo}</text>')
    cap = r["capacidade"]
    o.append(f'<text x="{ox}" y="{MY - 20}" font-size="13" fill="{C["suave"]}" '
             f'font-family="Inter, Helvetica, Arial, sans-serif">'
             f'<tspan font-size="25" font-weight="700" fill="{C["texto"]}">{cap["projeto"]}</tspan>'
             f'<tspan dx="6">pessoas no projeto</tspan>'
             f'<tspan dx="12" fill="{C["suave"]}">· {cap["maximo"]} no máximo admissível</tspan></text>')

    # casca
    pts = [(NOTCH_X, 0), (HALL_L, 0), (HALL_L, HALL_P), (0, HALL_P),
           (0, NOTCH_Y), (NOTCH_X, NOTCH_Y)]
    d = "M " + " L ".join(f"{X(x):.1f},{Y(y):.1f}" for x, y in pts) + " Z"
    o.append(f'<path d="{d}" fill="#ffffff" stroke="{C["parede"]}" stroke-width="2.4"/>')

    # piso de votação ao norte
    o.append(rect(0, y_div, HALL_L, HALL_P - y_div, fill=C["voto"], stroke="none"))
    o.append(txt(HALL_L / 2, y_div + (HALL_P - y_div) / 2 + 0.6,
                 "PISO DE VOTAÇÃO — 28 MRV", 11.5, weight="700", fill=C["secao"]))
    p = parede_para_secoes(y_div)
    o.append(txt(HALL_L / 2, y_div + (HALL_P - y_div) / 2 - 1.8,
                 f"passo de {p['passo_por_urna_m']:.2f} m por seção".replace(".", ","),
                 9.5, fill=C["suave"]))
    for i in range(14):   # parede norte
        cx = 1.6 + i * (HALL_L - 3.2) / 13
        o.append(rect(cx - 0.9, HALL_P - 1.6, 1.8, 0.8, fill=C["secao"], stroke="none"))
    for i in range(7):    # paredes leste e oeste do setor norte
        cy = y_div + 1.8 + i * (HALL_P - y_div - 4.2) / 6
        o.append(rect(0.8, cy - 0.9, 0.8, 1.8, fill=C["secao"], stroke="none"))
        o.append(rect(HALL_L - 1.6, cy - 0.9, 0.8, 1.8, fill=C["secao"], stroke="none"))

    # linha divisória
    o.append(line(0, y_div, HALL_L, y_div, stroke=C["linha"], stroke_width="2",
                  stroke_dasharray="7 5"))
    o.append(txt(HALL_L - 2.6, y_div + 1.1, f"linha divisória y = {y_div:.2f} m".replace(".", ","),
                 9.5, anchor="end", fill=C["linha"], weight="600"))

    # apron das portas
    o.append(rect(NOTCH_X, 0, HALL_L - NOTCH_X, APRON, fill=C["apron"],
                  stroke=C["apronL"], stroke_width="0.9", stroke_dasharray="4 3"))
    o.append(txt((HALL_L + NOTCH_X) / 2, APRON / 2 - 0.3,
                 f"triagem e acolhimento — {APRON:.1f} m".replace(".", ","),
                 9.5, weight="600", fill="#9a7b0a"))

    # blocos de fila
    for b in lay["blocos"]:
        cor = C[b["nome"][0]]
        x, y = b["x0"], b["y0"]
        w, h = b["x1"] - b["x0"], b["y1"] - b["y0"]
        o.append(rect(x, y, w, h, fill=cor, fill_opacity="0.13", stroke=cor,
                      stroke_width="1.3"))
        n = b["canais"]
        if lay["orientacao"] == "N-S":
            for i in range(1, n):
                xi = x + w * i / n
                y0, y1 = (y + 0.9, y + h) if i % 2 else (y, y + h - 0.9)
                o.append(line(xi, y0, xi, y1, stroke=cor, stroke_width="0.7",
                              stroke_opacity="0.5"))
            o.append(txt(x + w / 2, y + h / 2 + 0.8, b["nome"], 14, weight="700", fill=cor))
            o.append(txt(x + w / 2, y + h / 2 - 1.4,
                         f"{round(b['metros_canal'])} m", 9, fill=cor))
        else:
            for i in range(1, n):
                yi = y + h * i / n
                x0, x1 = (x + 0.9, x + w) if i % 2 else (x, x + w - 0.9)
                o.append(line(x0, yi, x1, yi, stroke=cor, stroke_width="0.7",
                              stroke_opacity="0.5"))
            o.append(txt(x + w / 2, y + h / 2 + 0.5, b["nome"], 13, weight="700", fill=cor))
            o.append(txt(x + w / 2 + 4.2, y + h / 2 + 0.5,
                         f"{round(b['metros_canal'])} m", 9, fill=cor))

    # corredor de acesso lateral às faixas sobre o recorte
    if acesso:
        o.append(rect(MARGEM, NOTCH_Y, NOTCH_X + 5.2 - MARGEM, 1.2, fill="#ffffff",
                      stroke=C["A"], stroke_width="0.8", stroke_dasharray="3 3"))
        o.append(txt((MARGEM + NOTCH_X + 5.2) / 2, NOTCH_Y + 0.25, "acesso a A1 e A2",
                     8, fill=C["A"]))

    # portas
    for nome, px in (("A", 17.0), ("B", 37.0)):
        cor = C[nome]
        o.append(rect(px - 1.6, -0.4, 3.2, 0.8, fill=cor, stroke="none"))
        o.append(txt(px, -2.4, f"ENTRADA {nome}", 10.5, weight="700", fill=cor))
    # saídas do piso de votação
    for yy in (y_div + 3.0, HALL_P - 6.0):
        o.append(rect(HALL_L - 0.4, yy - 1.0, 0.8, 2.0, fill=C["saida"], stroke="none"))
        o.append(rect(-0.4, yy - 1.0, 0.8, 2.0, fill=C["saida"], stroke="none"))
    o.append(txt(HALL_L / 2, HALL_P - 3.2, "saídas do piso de votação — norte, leste e oeste",
                 9, fill=C["saida"]))

    # cotas
    o.append(line(HALL_L + 1.4, 0, HALL_L + 1.4, y_div, stroke=C["suave"], stroke_width="0.8"))
    o.append(txt(HALL_L + 2.4, y_div / 2, f"zona de fila {y_div:.1f} m".replace(".", ","),
                 9, fill=C["suave"], rot=-90))
    return "\n".join(o), r


def main():
    y = Y_CENTRO
    ns, lo = layout_ns(y_div=y), layout_lo(y_div=y)
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
         f'<rect width="{W}" height="{H}" fill="{C["fundo"]}"/>']
    s.append(f'<text x="{MX}" y="40" font-size="25" font-weight="700" fill="{C["texto"]}" '
             f'font-family="Inter, Helvetica, Arial, sans-serif">Serpentina dentro do Hall 2</text>')
    s.append(f'<text x="{MX}" y="61" font-size="12.5" fill="{C["suave"]}" '
             f'font-family="Inter, Helvetica, Arial, sans-serif">Zona da parede sul (portas A e B) '
             f'até o centro do salão · canal de 1,10 m · passo de 0,65 m por pessoa · 3 filas por porta</text>')

    p1, r1 = painel(MX, ns, "A · Canais norte-sul", "6 faixas lado a lado; entrada ao sul, cabeça ao norte", y)
    p2, r2 = painel(MX + PW + GAPP, lo, "B · Canais leste-oeste",
                    "2 metades (uma por porta) × 3 bandas empilhadas", y, acesso=False)
    s += [p1, p2]

    gy = H - 92
    ganho = 100 * r1["capacidade"]["projeto"] / r2["capacidade"]["projeto"] - 100
    s.append(f'<line x1="{MX}" y1="{gy-26}" x2="{W-MX}" y2="{gy-26}" stroke="#c6c1b4" stroke-width="1"/>')
    s.append(f'<text x="{MX}" y="{gy}" font-size="13.5" font-weight="700" fill="{C["texto"]}" '
             f'font-family="Inter, Helvetica, Arial, sans-serif">'
             f'Norte-sul acomoda {ganho:.0f}% mais gente na mesma zona</text>')
    for i, t in enumerate([
        f"N-S: {r1['metros_canal']} m de canal em {r1['area_m2']} m² · {r1['unifila_un']} unifilas · "
        f"os 6 blocos dividem a largura, e o pedágio dos corredores é pago uma só vez.",
        f"L-O: {r2['metros_canal']} m de canal em {r2['area_m2']} m² · {r2['unifila_un']} unifilas · "
        f"cada metade empilha canais na mesma profundidade, então o pedágio é pago duas vezes, mais a espinha central.",
        "Em N-S a cabeça de cada fila já aponta para o piso de votação. Em L-O, quem sai da banda sul "
        "precisa atravessar as bandas do norte."]):
        s.append(f'<text x="{MX}" y="{gy + 19 + i * 16}" font-size="11.5" fill="{C["suave"]}" '
                 f'font-family="Inter, Helvetica, Arial, sans-serif">{t}</text>')
    s.append("</svg>")
    out = os.path.join(BASE, "saidas", "serpentina_hall2.svg")
    open(out, "w", encoding="utf-8").write("\n".join(s))
    print("->", out, f"({W}x{H})")


if __name__ == "__main__":
    main()
