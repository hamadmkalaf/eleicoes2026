# -*- coding: utf-8 -*-
"""Desenha a serpentina dentro do desenho atual, sem alterá-lo."""
import os
from prancheta_capacidade import (layout, resume, zona, FAIXA, APRON, SAIDA_L,
                                  PORTA_A, PORTA_B, PORTA_SAIDA)
from serpentina_hall2 import HALL_L, HALL_P, NOTCH_X, NOTCH_Y, Y_CENTRO

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ESC = 15.0
MX, MY = 60, 132
LEG = 322
W = int(HALL_L * ESC) + 2 * MX + LEG
H = int(HALL_P * ESC) + MY + 96

C = {"fundo": "#fbfaf8", "parede": "#1f2933", "secao": "#2f4858",
     "A": "#0e7490", "B": "#7b3f9d", "faixa": "#f0eee8", "texto": "#1f2933",
     "suave": "#6b7785", "saida": "#c0392b", "apron": "#fdf6e8",
     "apronL": "#9a7b0a", "linha": "#b03a2e"}

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

def main():
    lay = layout("N-S", saida_central=True)
    r = resume(lay)
    z = zona()
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
         f'<rect width="{W}" height="{H}" fill="{C["fundo"]}"/>']
    s.append(f'<text x="{MX}" y="44" font-size="26" font-weight="700" fill="{C["texto"]}" '
             f'font-family="Inter, Helvetica, Arial, sans-serif">Serpentina dentro do desenho atual</text>')
    s.append(f'<text x="{MX}" y="67" font-size="12.5" fill="{C["suave"]}" '
             f'font-family="Inter, Helvetica, Arial, sans-serif">As mesas ficam onde estão, nas três paredes. '
             f'Entradas A e B e saída central mantidas. A fila ocupa só o que sobra.</text>')

    # casca
    pts = [(NOTCH_X, 0), (HALL_L, 0), (HALL_L, HALL_P), (0, HALL_P),
           (0, NOTCH_Y), (NOTCH_X, NOTCH_Y)]
    d = "M " + " L ".join(f"{X(x):.1f},{Y(y):.1f}" for x, y in pts) + " Z"
    s.append(f'<path d="{d}" fill="#ffffff" stroke="{C["parede"]}" stroke-width="2.6"/>')

    # faixa perimetral das mesas (preservada)
    s.append(rect(0, NOTCH_Y, FAIXA, HALL_P - NOTCH_Y, fill=C["faixa"], stroke="none"))
    s.append(rect(0, HALL_P - FAIXA, HALL_L, FAIXA, fill=C["faixa"], stroke="none"))
    s.append(rect(HALL_L - FAIXA, 0, FAIXA, HALL_P, fill=C["faixa"], stroke="none"))
    s.append(txt(FAIXA / 2, 16, f"faixa das mesas {FAIXA:.1f} m".replace(".", ","),
                 9.5, fill=C["suave"], rot=-90))
    s.append(txt(HALL_L - FAIXA / 2, 30, f"faixa das mesas {FAIXA:.1f} m".replace(".", ","),
                 9.5, fill=C["suave"], rot=-90))

    # mesas como na prancheta: 10 oeste, 6 norte, 16 leste
    def col(n, a0, a1):
        p = (a1 - a0) / n
        return [a0 + p * (i + 0.5) for i in range(n)]
    for cy in col(10, NOTCH_Y + 0.6, HALL_P - 0.6):
        s.append(rect(1.0, cy - 0.9, 0.9, 1.8, fill=C["secao"], stroke="none"))
    for cx in col(6, 14.0, 34.0):
        s.append(rect(cx - 0.9, HALL_P - 1.9, 1.8, 0.9, fill=C["secao"], stroke="none"))
    for cy in col(16, 0.6, HALL_P - 0.6):
        s.append(rect(HALL_L - 1.9, cy - 0.9, 0.9, 1.8, fill=C["secao"], stroke="none"))
    s.append(txt(HALL_L - 4.0, HALL_P / 2, "MRV · leste", 10, weight="600",
                 fill=C["secao"], rot=-90))
    s.append(txt(3.6, HALL_P * 0.62, "MRV · oeste", 10, weight="600",
                 fill=C["secao"], rot=-90))
    s.append(txt(24.0, HALL_P - 4.2, "MRV · norte", 10, weight="600", fill=C["secao"]))

    # piso livre ao norte da zona de fila
    s.append(txt(HALL_L / 2 - 3, Y_CENTRO + 7.0, "CIRCULAÇÃO DO PISO DE VOTAÇÃO",
                 11.5, weight="700", fill=C["suave"]))
    s.append(txt(HALL_L / 2 - 3, Y_CENTRO + 5.2,
                 "da cabeça de cada fila até a mesa, e da mesa até a saída",
                 9.5, fill=C["suave"]))

    # linha do centro
    s.append(line(FAIXA, Y_CENTRO, HALL_L - FAIXA, Y_CENTRO, stroke=C["linha"],
                  stroke_width="2", stroke_dasharray="7 5"))
    s.append(txt(HALL_L - FAIXA - 0.8, Y_CENTRO + 1.0,
                 f"centro do salão — y = {Y_CENTRO:.2f} m".replace(".", ","),
                 9.5, anchor="end", fill=C["linha"], weight="600"))

    # apron de triagem
    s.append(rect(NOTCH_X, 0, HALL_L - NOTCH_X, APRON, fill=C["apron"],
                  stroke=C["apronL"], stroke_width="0.9", stroke_dasharray="4 3"))
    s.append(txt(17.5, APRON / 2 - 0.3,
                 f"triagem e distribuição — {APRON:.1f} m".replace(".", ","), 9.5,
                 weight="600", fill=C["apronL"]))

    # corredor da saída central
    s.append(rect(PORTA_SAIDA - SAIDA_L / 2, 0, SAIDA_L, Y_CENTRO,
                  fill="#fdecea", stroke=C["saida"], stroke_width="1",
                  stroke_dasharray="5 4"))
    s.append(txt(PORTA_SAIDA, Y_CENTRO - 4.0, "corredor", 9, fill=C["saida"], rot=-90))
    s.append(txt(PORTA_SAIDA + 1.0, Y_CENTRO - 4.0, "de saída", 9, fill=C["saida"], rot=-90))

    # blocos de fila
    for b in lay["blocos"]:
        cor = C[b["nome"][0]]
        x, y, w, h = b["x0"], b["y0"], b["larg_m"], b["prof_m"]
        s.append(rect(x, y, w, h, fill=cor, fill_opacity="0.13", stroke=cor,
                      stroke_width="1.4"))
        n = b["canais"]
        for i in range(1, n):
            xi = x + w * i / n
            y0, y1 = (y + 0.9, y + h) if i % 2 else (y, y + h - 0.9)
            s.append(line(xi, y0, xi, y1, stroke=cor, stroke_width="0.8",
                          stroke_opacity="0.5"))
        cap = next(q["cap"] for q in r["por_bloco"] if q["nome"] == b["nome"])
        s.append(txt(x + w / 2, y + h / 2 + 0.7, b["nome"], 15, weight="700", fill=cor))
        s.append(txt(x + w / 2, y + h / 2 - 1.5, f"{cap}", 11, fill=cor))
        s.append(txt(x + w / 2, y + h / 2 - 3.0, "pessoas", 8, fill=cor))

    # corredor de acesso a A1
    s.append(rect(FAIXA, NOTCH_Y, NOTCH_X + 3.0 - FAIXA, 1.2, fill="#ffffff",
                  stroke=C["A"], stroke_width="0.8", stroke_dasharray="3 3"))

    # portas
    for nome, px, cor in (("A", PORTA_A, C["A"]), ("B", PORTA_B, C["B"])):
        s.append(rect(px - 1.6, -0.45, 3.2, 0.9, fill=cor, stroke="none"))
        s.append(txt(px, -2.6, f"ENTRADA {nome}", 11, weight="700", fill=cor))
    s.append(rect(PORTA_SAIDA - 1.3, -0.45, 2.6, 0.9, fill=C["saida"], stroke="none"))
    s.append(txt(PORTA_SAIDA, -4.4, "SAÍDA", 10.5, weight="700", fill=C["saida"]))

    # cotas
    s.append(line(FAIXA, -6.6, HALL_L - FAIXA, -6.6, stroke=C["suave"], stroke_width="1"))
    s.append(txt((HALL_L) / 2, -6.1, f"{z['larg']:.1f} m de zona útil".replace(".", ","),
                 10, fill=C["suave"]))

    # legenda
    lx = MX + HALL_L * ESC + 34
    y = MY + 8
    L = []
    def t(s_, size=11.5, w_="400", c=C["suave"], dy=15):
        nonlocal y
        L.append(f'<text x="{lx}" y="{y}" font-size="{size}" font-weight="{w_}" '
                 f'fill="{c}" font-family="Inter, Helvetica, Arial, sans-serif">{s_}</text>')
        y += dy
    cap = r["capacidade"]
    L.append(f'<text x="{lx}" y="{y+16}" font-size="46" font-weight="700" fill="{C["texto"]}" '
             f'font-family="Inter, Helvetica, Arial, sans-serif">{cap["projeto"]}</text>')
    y += 44
    t("pessoas — cenário de projeto", 12.5, "600", C["texto"])
    t(f"{cap['maximo']} no máximo admissível (2,0 p/m²)", 11.5)
    t(f"{cap['confortavel']} com folga confortável", 11.5, dy=26)
    t("A ZONA", 13, "700", C["texto"], 18)
    t(f"{z['larg']:.1f} × {z['prof']:.2f} m entre as faixas".replace(".", ","))
    t(f"{r['canais']} canais de 1,10 m · {r['metros_canal']} m de canal")
    t(f"{r['unifila_un']} unifilas ({r['barreira_m']} m)", dy=26)
    t("OS 6 BLOCOS", 13, "700", C["texto"], 18)
    for b in r["por_bloco"]:
        cor = C[b["nome"][0]]
        L.append(f'<rect x="{lx}" y="{y-9}" width="11" height="11" rx="2" fill="{cor}" '
                 f'fill-opacity="0.25" stroke="{cor}"/>')
        L.append(f'<text x="{lx+18}" y="{y}" font-size="11.5" font-weight="700" fill="{cor}" '
                 f'font-family="Inter, Helvetica, Arial, sans-serif">{b["nome"]}</text>')
        L.append(f'<text x="{lx+42}" y="{y}" font-size="11" fill="{C["suave"]}" '
                 f'font-family="Inter, Helvetica, Arial, sans-serif">'
                 f'{b["canais"]} canais · {b["cap"]} pessoas</text>')
        y += 16
    y += 12
    t("O DESEQUILÍBRIO", 13, "700", C["texto"], 18)
    t("A saída central não fica no meio do salão,")
    t("então a porta A fica com 60% da zona e a")
    t("porta B com 40%. A divisão de urnas por")
    t("porta tem de seguir essa proporção —", 11.5, "400", C["suave"])
    t("60/40, não 50/50.", 11.5, "600", C["texto"])
    s.append("\n".join(L))
    s.append("</svg>")
    out = os.path.join(BASE, "saidas", "prancheta_serpentina.svg")
    open(out, "w", encoding="utf-8").write("\n".join(s))
    print("->", out, f"({W}x{H})")

if __name__ == "__main__":
    main()
