# -*- coding: utf-8 -*-
"""Gera o desenho em escala do plano de filas do Hall 2 sem o Ring 3."""
import os, json
from plano_filas import (carrega, clusters, anel, HALL_L, HALL_P, RECORTE,
                         FAIXA_SECOES, ANEL_PROF)

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ESC = 14.0                      # px por metro
MX, MY = 60, 70                 # margens
LEG = 330                       # painel de legenda

W = int(HALL_L * ESC) + 2 * MX + LEG
H = int(HALL_P * ESC) + 2 * MY

C = {"fundo": "#fbfaf8", "parede": "#1f2933", "secao": "#2f4858",
     "anelA": "#2a6f97", "anelB": "#7b3f9d", "porta_a": "#0e8a8a",
     "porta_b": "#8b2f8b", "nucleo": "#e9edf1", "texto": "#1f2933",
     "suave": "#6b7785", "saida": "#c0392b", "faixa": "#f2f0ea"}

def X(m): return MX + m * ESC
def Y(m): return MY + (HALL_P - m) * ESC        # y para cima

def rect(x, y, w, h, **kw):
    a = " ".join(f'{k.replace("_","-")}="{v}"' for k, v in kw.items())
    return f'<rect x="{X(x):.1f}" y="{Y(y+h):.1f}" width="{w*ESC:.1f}" height="{h*ESC:.1f}" {a}/>'

def txt(x, y, s, size=11, anchor="middle", fill=C["texto"], weight="400", rot=0):
    t = f' transform="rotate({rot} {X(x):.1f} {Y(y):.1f})"' if rot else ""
    return (f'<text x="{X(x):.1f}" y="{Y(y):.1f}" font-size="{size}" '
            f'text-anchor="{anchor}" fill="{fill}" font-weight="{weight}"'
            f' font-family="Inter, Helvetica, Arial, sans-serif"{t}>{s}</text>')

def linha(x1, y1, x2, y2, **kw):
    a = " ".join(f'{k.replace("_","-")}="{v}"' for k, v in kw.items())
    return f'<line x1="{X(x1):.1f}" y1="{Y(y1):.1f}" x2="{X(x2):.1f}" y2="{Y(y2):.1f}" {a}/>'

def serpentina(x, y, w, h, cor, vertical, canais=7):
    """Desenha as linhas de canal dentro de um bloco de espera."""
    out = [rect(x, y, w, h, fill=cor, fill_opacity="0.12", stroke=cor,
                stroke_width="1.6")]
    n = canais
    if vertical:      # canais paralelos ao eixo y, empilhados em x
        for i in range(1, n):
            xi = x + w * i / n
            y0, y1 = (y + 1.0, y + h) if i % 2 else (y, y + h - 1.0)
            out.append(linha(xi, y0, xi, y1, stroke=cor, stroke_width="0.9",
                             stroke_opacity="0.55"))
    else:
        for i in range(1, n):
            yi = y + h * i / n
            x0, x1 = (x + 1.0, x + w) if i % 2 else (x, x + w - 1.0)
            out.append(linha(x0, yi, x1, yi, stroke=cor, stroke_width="0.9",
                             stroke_opacity="0.55"))
    return "\n".join(out)

def mesa(cx, cy, parede):
    """Mesa receptora (1,8 x 0,8) + urna, encostada na parede."""
    if parede in ("O", "L"):
        w, h = 0.8, 1.8
    else:
        w, h = 1.8, 0.8
    return rect(cx - w / 2, cy - h / 2, w, h, fill=C["secao"], stroke="none")

def main():
    d, urnas = carrega()
    cl = clusters(urnas)
    nomes = ["A1", "A2", "A3", "B1", "B2", "B3"]
    carga = {nomes[i]: round(sum(u["esperado"] for u in c)) for i, c in enumerate(cl)}
    urn = {nomes[i]: [u["urna"] for u in c] for i, c in enumerate(cl)}
    a = anel()

    f = FAIXA_SECOES                 # 7,0 m
    p = ANEL_PROF                    # 7,7 m
    xw0, xw1 = f, f + p                       # coluna oeste do anel
    xe0, xe1 = HALL_L - f - p, HALL_L - f     # coluna leste
    yn0, yn1 = HALL_P - f - p, HALL_P - f     # tira norte
    ybase, ytopo = 8.0, HALL_P - f            # extensao vertical do anel
    ymeio = (ybase + ytopo) / 2
    xmeio = (xw1 + xe0) / 2

    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
         f'<rect width="{W}" height="{H}" fill="{C["fundo"]}"/>']

    # ---- casca do salao (com recorte a sudoeste)
    pts = [(RECORTE[0], 0), (HALL_L, 0), (HALL_L, HALL_P), (0, HALL_P),
           (0, RECORTE[1]), (RECORTE[0], RECORTE[1])]
    dpath = "M " + " L ".join(f"{X(x):.1f},{Y(y):.1f}" for x, y in pts) + " Z"
    s.append(f'<path d="{dpath}" fill="#ffffff" stroke="{C["parede"]}" stroke-width="3"/>')

    # ---- faixa das secoes (sombreada)
    s.append(rect(0, f, f, HALL_P - 2 * f, fill=C["faixa"], stroke="none"))
    s.append(rect(0, HALL_P - f, HALL_L, f, fill=C["faixa"], stroke="none"))
    s.append(rect(HALL_L - f, f, f, HALL_P - 2 * f, fill=C["faixa"], stroke="none"))

    # ---- zona de triagem interna (sul)
    s.append(rect(RECORTE[0], 0, HALL_L - RECORTE[0], ybase, fill="#fdf6e8",
                  stroke="#c9a227", stroke_width="1", stroke_dasharray="5 4"))
    s.append(txt(27.0, 4.8, "ZONA DE TRIAGEM E ACOLHIMENTO", 11, weight="700",
                 fill="#9a7b0a"))
    s.append(txt(27.0, 3.1, "postos de consulta \u00b7 faixa priorit\u00e1ria \u00b7 cadeiras", 9.5,
                 fill="#9a7b0a"))

    # ---- nucleo livre
    s.append(rect(xw1, ybase, xe0 - xw1, yn0 - ybase, fill=C["nucleo"],
                  stroke=C["suave"], stroke_width="1", stroke_dasharray="4 4"))
    s.append(txt(xmeio, ymeio + 1.6, "NÚCLEO LIVRE", 14, weight="700", fill=C["suave"]))
    s.append(txt(xmeio, ymeio - 0.2, f"{a['nucleo_livre_m2']} m² — circulação, faixa", 11, fill=C["suave"]))
    s.append(txt(xmeio, ymeio - 1.5, "prioritária, apoio médico e", 11, fill=C["suave"]))
    s.append(txt(xmeio, ymeio - 2.8, f"reserva p/ +{a['nucleo_reserva_p']} pessoas", 11, fill=C["suave"]))

    # ---- anel de espera: 6 segmentos
    seg = [
        ("A1", xw0, ybase, p, (ytopo - ybase) / 2, C["anelA"], True),
        ("A2", xw0, ymeio, p, (ytopo - ybase) / 2, C["anelA"], True),
        ("A3", xw1, yn0, (xe0 - xw1) / 2, p, C["anelA"], False),
        ("B1", xw1 + (xe0 - xw1) / 2, yn0, (xe0 - xw1) / 2, p, C["anelB"], False),
        ("B2", xe0, ymeio, p, (ytopo - ybase) / 2, C["anelB"], True),
        ("B3", xe0, ybase, p, (ytopo - ybase) / 2, C["anelB"], True),
    ]
    for nome, x, y, w, h, cor, vert in seg:
        s.append(serpentina(x, y, w, h, cor, vert))
        cx, cy = x + w / 2, y + h / 2
        rot = -90 if vert else 0
        s.append(txt(cx, cy + (0.9 if not vert else 0), nome, 17, weight="700",
                     fill=cor, rot=rot))
        s.append(txt(cx + (1.3 if vert else 0), cy - (1.3 if not vert else 0),
                     f"{carga[nome]} eleitores", 9.5, fill=cor, rot=rot))

    # ---- mesas receptoras (28): 8 oeste, 10 norte, 10 leste
    def dispoe(n, a0, a1):
        passo = (a1 - a0) / n
        return [a0 + passo * (i + 0.5) for i in range(n)]
    oeste = dispoe(8, RECORTE[1] + 0.5, HALL_P - 0.5)
    norte = dispoe(10, 0.5, HALL_L - 0.5)
    leste = dispoe(10, 0.5, HALL_P - 0.5)
    for cy in oeste:
        s.append(mesa(1.3, cy, "O"))
    for cx in norte:
        s.append(mesa(cx, HALL_P - 1.3, "N"))
    for cy in leste:
        s.append(mesa(HALL_L - 1.3, cy, "L"))
    s.append(txt(4.3, HALL_P / 2 - 3, "8 MRV", 11, weight="700", fill=C["secao"], rot=-90))
    s.append(txt(HALL_L / 2, HALL_P - 4.6, "10 MRV", 11, weight="700", fill=C["secao"]))
    s.append(txt(HALL_L - 3.4, HALL_P / 2 - 3, "10 MRV", 11, weight="700", fill=C["secao"], rot=-90))

    # ---- portas de entrada A e B e saidas
    for nome, px, cor in (("A", 17.0, C["porta_a"]), ("B", 37.0, C["porta_b"])):
        s.append(rect(px - 1.6, -0.45, 3.2, 0.9, fill=cor, stroke="none"))
        s.append(txt(px, -2.6, f"ENTRADA {nome}", 12, weight="700", fill=cor))
        s.append(txt(px, -4.2, "triagem + consulta", 9.5, fill=cor))
    # corredores de distribuicao
    for px, cor, lados in ((17.0, C["porta_a"], -1), (37.0, C["porta_b"], 1)):
        s.append(f'<path d="M {X(px):.1f},{Y(0.5):.1f} L {X(px):.1f},{Y(yn0-1.5):.1f}" '
                 f'stroke="{cor}" stroke-width="7" stroke-opacity="0.30" fill="none"/>')
        for yy in (ybase + 3, ymeio + 2, yn0 - 1.5):
            x2 = (xw1 + 0.5) if lados < 0 else (xe0 - 0.5)
            s.append(f'<path d="M {X(px):.1f},{Y(yy):.1f} L {X(x2):.1f},{Y(yy):.1f}" '
                     f'stroke="{cor}" stroke-width="4" stroke-opacity="0.28" fill="none"/>')
            s.append(f'<circle cx="{X(x2):.1f}" cy="{Y(yy):.1f}" r="4" fill="{cor}" fill-opacity="0.7"/>')
    # saidas laterais (portas reais do Hall 2)
    for yy in (12.0, 22.0, 32.0, 39.0):
        s.append(rect(HALL_L - 0.45, yy - 1.1, 0.9, 2.2, fill=C["saida"], stroke="none"))
        s.append(f'<path d="M {X(HALL_L-4.5):.1f},{Y(yy):.1f} L {X(HALL_L+1.8):.1f},{Y(yy):.1f}" '
                 f'stroke="{C["saida"]}" stroke-width="2" fill="none" marker-end="url(#seta)"/>')
    for yy in (12.0, 21.0):
        s.append(rect(-0.45, yy - 1.1, 0.9, 2.2, fill=C["saida"], stroke="none"))
        s.append(f'<path d="M {X(4.5):.1f},{Y(yy):.1f} L {X(-1.8):.1f},{Y(yy):.1f}" '
                 f'stroke="{C["saida"]}" stroke-width="2" fill="none" marker-end="url(#seta)"/>')
    s.append(txt(HALL_L - 5.6, 26, "SA\u00cdDAS", 10.5, weight="700", fill=C["saida"], rot=-90))
    s.append(txt(6.3, 16.5, "SA\u00cdDAS", 10.5, weight="700", fill=C["saida"], rot=-90))

    # ---- cotas
    s.append(linha(0, HALL_P + 1.6, HALL_L, HALL_P + 1.6, stroke=C["suave"], stroke_width="1"))
    s.append(txt(HALL_L / 2, HALL_P + 2.2, "50,20 m", 11, fill=C["suave"]))
    s.append(linha(-2.6, 0, -2.6, HALL_P, stroke=C["suave"], stroke_width="1"))
    s.append(txt(-3.2, HALL_P / 2, "44,50 m", 11, fill=C["suave"], rot=-90))
    s.append(linha(36.0, -3.4, 46.0, -3.4,
                   stroke=C["texto"], stroke_width="2"))
    for k in range(3):
        s.append(linha(36.0 + 5 * k, -3.9, 36.0 + 5 * k, -2.9,
                       stroke=C["texto"], stroke_width="1.4"))
    s.append(txt(41.0, -5.6, "0          5         10 m", 9.5, fill=C["texto"]))
    s.append(txt(xw0 + p / 2, ybase + 0.9, f"anel {p:.1f} m".replace(".", ","), 9, fill=C["anelA"]))
    s.append(txt(f / 2, ybase + 0.9, f"faixa MRV {f:.1f} m".replace(".", ","), 9, fill=C["secao"]))

    # ---- marcador de seta
    s.insert(1, f'<defs><marker id="seta" viewBox="0 0 10 10" refX="9" refY="5" '
                f'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
                f'<path d="M 0 0 L 10 5 L 0 10 z" fill="{C["saida"]}"/></marker></defs>')

    # ---- legenda
    lx = MX + HALL_L * ESC + 34
    ly = MY + 6
    L = []
    L.append(f'<text x="{lx}" y="{ly}" font-size="19" font-weight="700" fill="{C["texto"]}" font-family="Inter, Helvetica, Arial, sans-serif">Filas sem o Ring 3</text>')
    L.append(f'<text x="{lx}" y="{ly+20}" font-size="12" fill="{C["suave"]}" font-family="Inter, Helvetica, Arial, sans-serif">RDS Hall 2 · 50,2 × 44,5 m · 2.238 m²</text>')
    L.append(f'<text x="{lx}" y="{ly+36}" font-size="12" fill="{C["suave"]}" font-family="Inter, Helvetica, Arial, sans-serif">28 urnas · 16.794 aptos · 11.416 esperados</text>')
    y = ly + 66
    blocos = [
        ("ANEL DE ESPERA", C["texto"], [
            (f"{a['area_m2']} m² · {a['canais']} canais de 1,10 m", C["suave"]),
            (f"capacidade de projeto: {a['capacidade_p']} pessoas", C["suave"]),
            (f"{a['unifila_un']} unifilas ({a['barreira_m']} m de barreira)", C["suave"])]),
    ]
    for titulo, cor, itens in blocos:
        L.append(f'<text x="{lx}" y="{y}" font-size="13" font-weight="700" fill="{cor}" font-family="Inter, Helvetica, Arial, sans-serif">{titulo}</text>')
        y += 17
        for t, c in itens:
            L.append(f'<text x="{lx}" y="{y}" font-size="11.5" fill="{c}" font-family="Inter, Helvetica, Arial, sans-serif">{t}</text>')
            y += 15
        y += 8
    L.append(f'<text x="{lx}" y="{y}" font-size="13" font-weight="700" fill="{C["texto"]}" font-family="Inter, Helvetica, Arial, sans-serif">AS 6 FILAS (3 por porta)</text>')
    y += 18
    for i, nome in enumerate(nomes):
        cor = C["anelA"] if nome[0] == "A" else C["anelB"]
        L.append(f'<rect x="{lx}" y="{y-9}" width="11" height="11" rx="2" fill="{cor}" fill-opacity="0.25" stroke="{cor}"/>')
        L.append(f'<text x="{lx+18}" y="{y}" font-size="11.5" font-weight="700" fill="{cor}" font-family="Inter, Helvetica, Arial, sans-serif">{nome}</text>')
        L.append(f'<text x="{lx+42}" y="{y}" font-size="11" fill="{C["suave"]}" font-family="Inter, Helvetica, Arial, sans-serif">{carga[nome]} eleitores</text>')
        y += 14
        L.append(f'<text x="{lx+18}" y="{y}" font-size="10" fill="{C["suave"]}" font-family="Inter, Helvetica, Arial, sans-serif">urnas {", ".join(str(v) for v in sorted(urn[nome]))}</text>')
        y += 18
    y += 6
    for t, w_, c in [("FLUXO", "700", C["texto"]),
                     ("1. triagem na porta (A ou B)", "400", C["suave"]),
                     ("2. corredor até a fila indicada", "400", C["suave"]),
                     ("3. anel de espera (serpentina)", "400", C["suave"]),
                     ("4. liberação para a micro-fila da urna", "400", C["suave"]),
                     ("5. voto e saída pela parede lateral", "400", C["suave"]),
                     ("— sem cruzamento entre entrada e saída —", "400", C["saida"])]:
        L.append(f'<text x="{lx}" y="{y}" font-size="{13 if w_=="700" else 11.5}" font-weight="{w_}" fill="{c}" font-family="Inter, Helvetica, Arial, sans-serif">{t}</text>')
        y += 16 if w_ == "400" else 19
    s.append("\n".join(L))
    s.append("</svg>")

    out = os.path.join(BASE, "saidas", "plano_filas_sem_ring3.svg")
    open(out, "w", encoding="utf-8").write("\n".join(s))
    print("->", out, f"({W}x{H})")

if __name__ == "__main__":
    main()
