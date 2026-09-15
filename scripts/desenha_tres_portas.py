# -*- coding: utf-8 -*-
"""Desenha a serpentina de 6 blocos para a prancheta com 3 entradas."""
import os, sys
from tres_portas import (melhor, resume, regioes, PORTAS, ENTRADAS, FAIXA, APRON,
                         SAIDA_L, GAP)
from serpentina_hall2 import HALL_L, HALL_P, NOTCH_X, NOTCH_Y, Y_CENTRO

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ESC = 15.0
MX, MY, LEG = 60, 132, 330
W = int(HALL_L * ESC) + 2 * MX + LEG
H = int(HALL_P * ESC) + MY + 110

C = {"fundo": "#fbfaf8", "parede": "#1f2933", "secao": "#2f4858",
     "A": "#0e7490", "B": "#b8741a", "C": "#a23b72", "faixa": "#f0eee8",
     "texto": "#1f2933", "suave": "#6b7785", "saida": "#2e7d5b",
     "apron": "#fdf6e8", "apronL": "#9a7b0a", "linha": "#b03a2e", "cruz": "#c0392b"}

def X(m): return MX + m * ESC
def Y(m): return MY + (HALL_P - m) * ESC

def rect(x, y, w, h, **kw):
    a = " ".join(f'{k.replace("_","-")}="{v}"' for k, v in kw.items())
    return (f'<rect x="{X(x):.1f}" y="{Y(y+h):.1f}" width="{w*ESC:.1f}" '
            f'height="{h*ESC:.1f}" {a}/>')

def txt(x, y, s, size=11, anchor="middle", fill=C["texto"], weight="400", rot=0):
    t = f' transform="rotate({rot} {X(x):.1f} {Y(y):.1f})"' if rot else ""
    return (f'<text x="{X(x):.1f}" y="{Y(y):.1f}" font-size="{size}" '
            f'text-anchor="{anchor}" fill="{fill}" font-weight="{weight}" '
            f'font-family="Inter, Helvetica, Arial, sans-serif"{t}>{s}</text>')

def line(x1, y1, x2, y2, **kw):
    a = " ".join(f'{k.replace("_","-")}="{v}"' for k, v in kw.items())
    return (f'<line x1="{X(x1):.1f}" y1="{Y(y1):.1f}" x2="{X(x2):.1f}" '
            f'y2="{Y(y2):.1f}" {a}/>')

def main(k=2, s2=True, nome="tres_portas_serpentina"):
    bl = melhor(k, s2_aberta=s2)
    r = resume(bl)
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
         f'<rect width="{W}" height="{H}" fill="{C["fundo"]}"/>',
         f'<defs><marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" '
         f'markerHeight="6" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" '
         f'fill="{C["saida"]}"/></marker></defs>']
    s.append(f'<text x="{MX}" y="44" font-size="26" font-weight="700" fill="{C["texto"]}" '
             f'font-family="Inter, Helvetica, Arial, sans-serif">Serpentina para três entradas</text>')
    s.append(f'<text x="{MX}" y="67" font-size="12.5" fill="{C["suave"]}" '
             f'font-family="Inter, Helvetica, Arial, sans-serif">Prancheta Hamad_Final · entradas S4, S5 e S6 · '
             f'saídas S2 e S8 · mesas onde estão · {3*k} blocos, {k} por porta, mesma capacidade por porta</text>')

    # casca
    pts = [(NOTCH_X, 0), (HALL_L, 0), (HALL_L, HALL_P), (0, HALL_P), (0, NOTCH_Y), (NOTCH_X, NOTCH_Y)]
    d = "M " + " L ".join(f"{X(x):.1f},{Y(y):.1f}" for x, y in pts) + " Z"
    s.append(f'<path d="{d}" fill="#ffffff" stroke="{C["parede"]}" stroke-width="2.6"/>')

    # faixas das mesas
    s.append(rect(0, NOTCH_Y, FAIXA, HALL_P - NOTCH_Y, fill=C["faixa"], stroke="none"))
    s.append(rect(0, HALL_P - FAIXA, HALL_L, FAIXA, fill=C["faixa"], stroke="none"))
    s.append(rect(HALL_L - FAIXA, 0, FAIXA, HALL_P, fill=C["faixa"], stroke="none"))
    def col(n, a0, a1):
        p = (a1 - a0) / n
        return [a0 + p * (i + 0.5) for i in range(n)]
    for cy in col(9, NOTCH_Y + 1.0, HALL_P - FAIXA - 0.5):
        s.append(rect(1.0, cy - 0.9, 0.9, 1.8, fill=C["secao"], stroke="none"))
    for cx in col(9, FAIXA + 1.0, HALL_L - FAIXA - 1.0):
        s.append(rect(cx - 0.9, HALL_P - 1.9, 1.8, 0.9, fill=C["secao"], stroke="none"))
    for cy in col(10, 1.0, HALL_P - FAIXA - 0.5):
        s.append(rect(HALL_L - 1.9, cy - 0.9, 0.9, 1.8, fill=C["secao"], stroke="none"))
    s.append(txt(3.8, 30.0, "PAREDE OESTE · 9 mesas", 9.5, weight="600", fill=C["secao"], rot=-90))
    s.append(txt(HALL_L - 3.8, 22.0, "PAREDE LESTE · 10 mesas", 9.5, weight="600", fill=C["secao"], rot=-90))
    s.append(txt(HALL_L / 2, HALL_P - 4.3, "PAREDE NORTE · 9 mesas", 9.5, weight="600", fill=C["secao"]))

    # piso de circulação
    s.append(txt(HALL_L / 2, Y_CENTRO + 7.4, "CIRCULAÇÃO DO PISO DE VOTAÇÃO", 11.5, weight="700", fill=C["suave"]))
    s.append(txt(HALL_L / 2, Y_CENTRO + 5.6, "da cabeça de cada fila à mesa; da mesa às saídas", 9.5, fill=C["suave"]))
    s.append(line(FAIXA, Y_CENTRO, HALL_L - FAIXA, Y_CENTRO, stroke=C["linha"], stroke_width="2", stroke_dasharray="7 5"))
    s.append(txt(HALL_L - FAIXA - 0.8, Y_CENTRO + 1.0, f"centro — y = {Y_CENTRO:.2f} m".replace(".", ","),
                 9.5, anchor="end", fill=C["linha"], weight="600"))

    # apron
    s.append(rect(NOTCH_X, 0, HALL_L - NOTCH_X, APRON, fill=C["apron"], stroke=C["apronL"],
                  stroke_width="0.9", stroke_dasharray="4 3"))
    s.append(txt(29.5, APRON / 2 - 0.3, f"triagem e distribuição — {APRON:.1f} m".replace(".", ","),
                 9.5, weight="600", fill=C["apronL"]))

    # corredor de saída S2
    if s2:
        xs = PORTAS["S2"]
        s.append(rect(FAIXA, NOTCH_Y, xs + SAIDA_L / 2 - FAIXA, SAIDA_L, fill="#e7f2ec",
                      stroke=C["saida"], stroke_width="1", stroke_dasharray="5 4"))
        s.append(rect(xs - SAIDA_L / 2, 0, SAIDA_L, NOTCH_Y + SAIDA_L, fill="#e7f2ec",
                      stroke=C["saida"], stroke_width="1", stroke_dasharray="5 4"))
        s.append(f'<path d="M {X(3.5):.1f},{Y(Y_CENTRO+1):.1f} L {X(3.5):.1f},{Y(NOTCH_Y+1.5):.1f} '
                 f'L {X(xs):.1f},{Y(NOTCH_Y+1.5):.1f} L {X(xs):.1f},{Y(0.6):.1f}" fill="none" '
                 f'stroke="{C["saida"]}" stroke-width="2" marker-end="url(#ar)"/>')
        s.append(txt(xs - 0.2, APRON + 1.0, "saída", 8.5, fill=C["saida"], rot=-90))
        # cruzamento
        s.append(rect(xs - SAIDA_L / 2, 0.6, SAIDA_L, 2.8, fill="none", stroke=C["cruz"],
                      stroke_width="1.6"))
        s.append(txt(xs, -1.6 - 3.6, "cruzamento", 8.5, weight="700", fill=C["cruz"]))
        s.append(txt(xs, -1.6 - 4.9, "com fiscal", 8.5, fill=C["cruz"]))
    # saída leste S8
    xe = PORTAS["S8"]
    s.append(f'<path d="M {X(HALL_L-3.5):.1f},{Y(Y_CENTRO+1):.1f} L {X(HALL_L-3.5):.1f},{Y(2.5):.1f} '
             f'L {X(xe):.1f},{Y(2.5):.1f} L {X(xe):.1f},{Y(0.6):.1f}" fill="none" '
             f'stroke="{C["saida"]}" stroke-width="2" marker-end="url(#ar)"/>')

    # blocos
    for b in bl:
        cor = C[b["porta"]]
        x, y, w, h = b["x0"], b["y0"], b["canais"] * 1.1, b["prof"]
        s.append(rect(x, y, w, h, fill=cor, fill_opacity="0.13", stroke=cor, stroke_width="1.4"))
        for i in range(1, b["canais"]):
            xi = x + 1.1 * i
            y0, y1 = (y + 0.9, y + h) if i % 2 else (y, y + h - 0.9)
            s.append(line(xi, y0, xi, y1, stroke=cor, stroke_width="0.8", stroke_opacity="0.5"))
        cap = round(b["metros"] / 0.65 - max(0, b["canais"] - 1) * 0.5)
        s.append(txt(x + w / 2, y + h / 2 + 0.8, b["nome"], 14, weight="700", fill=cor))
        s.append(txt(x + w / 2, y + h / 2 - 1.3, f"{cap}", 10.5, fill=cor))
        s.append(txt(x + w / 2, y + h / 2 - 2.7, "pessoas", 7.5, fill=cor))

    # portas S1..S9
    for porta_n, px in PORTAS.items():
        if porta_n in ("S4", "S5", "S6"):
            letra = {"S4": "A", "S5": "B", "S6": "C"}[porta_n]
            cor = C[letra]
            s.append(rect(px - 1.6, -0.45, 3.2, 0.9, fill=cor, stroke="none"))
            s.append(txt(px, -2.4, f"ENTRADA {letra}", 10, weight="700", fill=cor))
            s.append(txt(px, -3.7, porta_n, 8.5, fill=cor))
        elif porta_n in ("S2", "S8"):
            s.append(rect(px - 1.3, -0.45, 2.6, 0.9, fill=C["saida"], stroke="none"))
            s.append(txt(px, -2.4, "SAÍDA", 10, weight="700", fill=C["saida"]))
            s.append(txt(px, -3.7, porta_n, 8.5, fill=C["saida"]))
        else:
            s.append(rect(px - 0.9, -0.3, 1.8, 0.6, fill="#c9c4b8", stroke="none"))
            s.append(txt(px, -2.0, porta_n, 8, fill=C["suave"]))

    # legenda
    lx = MX + HALL_L * ESC + 34
    y = MY + 8
    L = []
    def t(s_, size=11.5, w_="400", c=C["suave"], dy=15):
        nonlocal y
        L.append(f'<text x="{lx}" y="{y}" font-size="{size}" font-weight="{w_}" fill="{c}" '
                 f'font-family="Inter, Helvetica, Arial, sans-serif">{s_}</text>')
        y += dy
    cap = r["capacidade"]
    L.append(f'<text x="{lx}" y="{y+16}" font-size="46" font-weight="700" fill="{C["texto"]}" '
             f'font-family="Inter, Helvetica, Arial, sans-serif">{cap["projeto"]}</text>')
    y += 44
    t("pessoas — cenário de projeto", 12.5, "600", C["texto"])
    t(f"{cap['maximo']} no máximo admissível (2,0 p/m²)")
    t(f"{cap['confortavel']} com folga confortável", dy=26)
    t("POR PORTA", 13, "700", C["texto"], 18)
    for p, v in r["por_porta"].items():
        L.append(f'<rect x="{lx}" y="{y-9}" width="11" height="11" rx="2" fill="{C[p]}" fill-opacity="0.25" stroke="{C[p]}"/>')
        L.append(f'<text x="{lx+18}" y="{y}" font-size="11.5" font-weight="700" fill="{C[p]}" '
                 f'font-family="Inter, Helvetica, Arial, sans-serif">{p}</text>')
        L.append(f'<text x="{lx+34}" y="{y}" font-size="11" fill="{C["suave"]}" '
                 f'font-family="Inter, Helvetica, Arial, sans-serif">{v["projeto"]} pessoas · {v["blocos"]} blocos · {v["canais"]} canais · {v["metros"]} m</text>')
        y += 16
    y += 10
    t("OS BLOCOS", 13, "700", C["texto"], 18)
    for b in bl:
        extra = " · a oeste de S2" if b["oeste"] else (" · recuado p/ igualar" if b.get("recuado") else "")
        t(f"{b['nome']}  {b['canais']} canais × {b['prof']:.1f} m = {b['metros']:.0f} m{extra}".replace(".", ","), 11)
    y += 10
    t("A ZONA", 13, "700", C["texto"], 18)
    t(f"{r['canais']} canais de 1,10 m · {r['metros_canal']} m de canal")
    t(f"{r['unifila_un']} unifilas ({r['barreira_m']} m)")
    t(f"corredores de {GAP:.1f} m entre blocos".replace(".", ","))
    t(f"saída S2: corredor de {SAIDA_L:.1f} m por cima do recorte".replace(".", ","))
    s.append("\n".join(L))
    s.append("</svg>")
    out = os.path.join(BASE, "saidas", f"{nome}.svg")
    open(out, "w", encoding="utf-8").write("\n".join(s))
    print("->", out)

if __name__ == "__main__":
    main(2, True, "tres_portas_serpentina")
    main(2, False, "tres_portas_s2_fechada")
