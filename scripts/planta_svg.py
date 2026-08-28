"""Desenha a planta de fluxo do Hall 2 a partir de saidas/fluxo_dados.json.

Tudo em escala: as coordenadas vem em metros do modelo e sao convertidas em px.
O SVG usa atributos de apresentacao (nao classes CSS) para renderizar igual em
navegador, visualizador de imagem e impressao.
"""
import json, math, os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = 15.0                              # px por metro
ML, MR, MT, MB = 64, 64, 76, 190      # margens em px
W, H = 50.3, 44.4                     # dimensoes uteis do salao, em metros

AZUL, AMBAR, VERDE = "#2d6fb0", "#b8761c", "#2f8a5b"
COR = {"leve": "#a9c9e2", "media": "#6a9bc6", "alta": "#e2a33c", "critica": "#c8493c"}
FONTE = ('font-family="ui-sans-serif,system-ui,\'Segoe UI\',Helvetica,Arial,'
         'sans-serif"')
EST = {
    "lbl":  f'{FONTE} font-size="9.5" fill="#243244"',
    "sub":  f'{FONTE} font-size="8" fill="#5c6c80"',
    "urna": f'{FONTE} font-size="10" font-weight="700" fill="#1f2c3c"',
    "tit":  f'{FONTE} font-size="16" font-weight="700" fill="#1f2c3c"',
    "prt":  f'{FONTE} font-size="9.5" font-weight="700" fill="#243244"',
    "zona": f'{FONTE} font-size="12" font-weight="700" fill="#243244" opacity=".42"',
    "via":  f'{FONTE} font-size="8.5" font-weight="700" fill="#243244" opacity=".75"',
}


def px(x, y):
    return ML + x * S, MT + (H - y) * S


def esc(t):
    return str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def rect(x0, y0, x1, y1, **kw):
    ax, ay = px(x0, y1)
    bx, by = px(x1, y0)
    at = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in kw.items())
    return (f'<rect x="{ax:.1f}" y="{ay:.1f}" width="{bx - ax:.1f}" '
            f'height="{by - ay:.1f}" {at}/>')


def txt(x, y, t, est="lbl", anchor="middle", rot=0, dy=0):
    a, b = px(x, y)
    b += dy
    tr = f' transform="rotate({rot} {a:.1f} {b:.1f})"' if rot else ""
    return (f'<text x="{a:.1f}" y="{b:.1f}" {EST[est]} '
            f'text-anchor="{anchor}"{tr}>{esc(t)}</text>')


def par(x, y, cima, baixo, rot=0):
    """Codigo da urna e comparecimento esperado, empilhados; girados quando a
    baia e estreita e profunda."""
    a, b = px(x, y)
    tr = f' transform="rotate({rot} {a:.1f} {b:.1f})"' if rot else ""
    return (f'<g{tr}><text x="{a:.1f}" y="{b - 2:.1f}" {EST["urna"]} '
            f'text-anchor="middle">{esc(cima)}</text>'
            f'<text x="{a:.1f}" y="{b + 8:.1f}" {EST["sub"]} '
            f'text-anchor="middle">{esc(baixo)}</text></g>')


def ponta(x, y, ang, cor, tam=4.2):
    """Cabeca de seta desenhada como poligono, para nao depender de <marker>."""
    a, b = px(x, y)
    p = []
    for da, r in ((0, tam * 1.7), (140, tam), (220, tam)):
        t = math.radians(ang + da)
        p.append(f"{a + r * math.cos(t):.1f},{b - r * math.sin(t):.1f}")
    return f'<polygon points="{" ".join(p)}" fill="{cor}"/>'


def rota(pts, cor, larg_m, rotulo=None, op=".16"):
    """Corredor de circulacao: faixa larga translucida + setas de sentido."""
    d = " ".join(f"{px(x, y)[0]:.1f},{px(x, y)[1]:.1f}" for x, y in pts)
    o = [f'<polyline points="{d}" fill="none" stroke="{cor}" '
         f'stroke-width="{larg_m * S:.1f}" stroke-linejoin="round" '
         f'stroke-linecap="round" opacity="{op}"/>']
    for i in range(len(pts) - 1):
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        ang = math.degrees(math.atan2(y1 - y0, x1 - x0))
        o.append(ponta((x0 + x1) / 2, (y0 + y1) / 2, ang, cor))
    if rotulo:
        mx, my = pts[len(pts) // 2]
        o.append(txt(mx, my, rotulo, "via", dy=-larg_m * S / 2 - 4))
    return "".join(o)


def main():
    with open(os.path.join(RAIZ, "saidas", "fluxo_dados.json"), encoding="utf-8") as f:
        d = json.load(f)
    LG, AL = ML + W * S + MR, MT + H * S + MB
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {LG:.0f} {AL:.0f}" '
         f'width="{LG:.0f}" height="{AL:.0f}" role="img" aria-label="Planta de '
         f'fluxo do Hall 2 do RDS com as 28 mesas receptoras de votos">',
         f'<rect x="0" y="0" width="{LG}" height="{AL}" fill="#fbfaf7"/>']

    # ---------- zonas e piso
    o.append(rect(0, 0, 25.32, H, fill=AZUL, opacity=".05"))
    o.append(rect(31.25, 0, W, H, fill=AMBAR, opacity=".045"))
    o.append(rect(0, 0, 7.8, 7.0, fill="#fbfaf7"))
    poly = [(7.8, 0), (W, 0), (W, H), (0, H), (0, 7.0), (7.8, 7.0)]
    pts = " ".join(f"{px(x, y)[0]:.1f},{px(x, y)[1]:.1f}" for x, y in poly)
    o.append(f'<polygon points="{pts}" fill="none" stroke="#1c2733" stroke-width="3.4"/>')

    # ---------- reserva de fila (piso mantido livre p/ expandir as filas)
    for x0, x1, rot in ((16.0, 24.6, "RESERVA A"), (31.9, 34.8, "RESERVA B")):
        o.append(rect(x0, 12.0, x1, 27.0, fill="none", stroke="#8a97a6",
                      stroke_width="1.2", stroke_dasharray="7 5"))
        o.append(txt((x0 + x1) / 2, 25.4, rot, "via"))
        o.append(txt((x0 + x1) / 2, 24.2, "piso livre p/ 60 s", "sub"))

    # ---------- corredores
    # Avenida (entrada) e retorno (saida) correm em faixas paralelas e
    # adjacentes, nunca se cruzando: as avenidas ficam encostadas nas bocas das
    # baias, os retornos por dentro delas, e ambos so se encontram na espinha.
    e = d["espinha_saida"]
    o.append(rota([(28.3, 32.0), (28.3, 1.5)], AMBAR, 5.9, None, ".17"))
    o.append(rect(e["x0"], e["y0"], e["x1"], e["y1"], fill="none", stroke=AMBAR,
                  stroke_width="1.5", stroke_dasharray="6 4"))
    o.append(txt(28.3, 20.0, "ESPINHA DE SAÍDA", "via", rot=-90))
    o.append(rota([(22.07, 1.5), (22.07, 3.5), (17.0, 3.2), (10.6, 7.5),
                   (10.6, 34.0), (11.5, 41.0)], AZUL, 3.0))
    o.append(rota([(13.6, 41.0), (13.4, 31.0), (13.4, 12.0), (18.0, 9.0),
                   (25.6, 9.0)], AMBAR, 2.6, None, ".14"))
    o.append(rota([(34.51, 1.5), (34.51, 3.5), (39.0, 3.2), (40.2, 7.5),
                   (40.2, 26.0), (38.5, 29.8), (29.0, 29.8)], AZUL, 3.0))
    o.append(rota([(29.0, 32.2), (37.5, 32.2), (36.6, 28.0), (36.6, 12.0),
                   (33.0, 9.0), (31.3, 9.0)], AMBAR, 2.6, None, ".14"))
    o.append(txt(10.6, 22.0, "AVENIDA A", "via", rot=-90))
    o.append(txt(13.4, 22.0, "RETORNO A", "via", rot=-90))
    o.append(txt(40.2, 18.0, "AVENIDA B", "via", rot=-90))
    o.append(txt(36.6, 18.0, "RETORNO B", "via", rot=-90))

    # ---------- baias de fila e modulos mesa+urna
    for m in d["mrvs"]:
        nx, ny = m["normal"]
        lw, dp, x, y = m["baia_largura"], m["baia_profundidade"], m["x"], m["y"]
        c = COR[m["classe"]]
        if ny:
            ym = y + ny * 1.2
            o.append(rect(x - lw / 2, min(ym, ym + ny * dp), x + lw / 2,
                          max(ym, ym + ny * dp), fill=c, opacity=".2", stroke=c,
                          stroke_width="1.2", stroke_dasharray="4 3"))
            o.append(rect(x - 1.0, min(y, ym), x + 1.0, max(y, ym), fill="#33465c"))
            o.append(par(x, ym + ny * dp / 2, m["urna"], m["esperado"], -90))
        else:
            xm = x + nx * 1.2
            o.append(rect(min(xm, xm + nx * dp), y - lw / 2,
                          max(xm, xm + nx * dp), y + lw / 2, fill=c, opacity=".2",
                          stroke=c, stroke_width="1.2", stroke_dasharray="4 3"))
            o.append(rect(min(x, xm), y - 1.0, max(x, xm), y + 1.0, fill="#33465c"))
            o.append(par(xm + nx * dp / 2, y, m["urna"], m["esperado"]))

    # ---------- setor reforcado
    o.append(rect(24.4, 31.6, 42.2, 44.4, fill="none", stroke=COR["critica"],
                  stroke_width="1.6", stroke_dasharray="8 4"))
    o.append(txt(33.3, 45.6, "SETOR REFORÇADO — 3 urnas Dublin+Dublin, "
                 "fila de pico ~57 cada, 4 mesários", "via"))

    # ---------- saidas de emergencia, por cima de tudo
    for lado, lista in d["portas"].items():
        for nome, a, b in lista:
            if lado == "sul":
                continue
            if lado == "norte":
                (x1, y1), (x2, y2) = px(a, H), px(b, H)
            elif lado == "oeste":
                (x1, y1), (x2, y2) = px(0, a), px(0, b)
            else:
                (x1, y1), (x2, y2) = px(W, a), px(W, b)
            o.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                     f'stroke="{VERDE}" stroke-width="6"/>')

    # ---------- portas operacionais da parede sul
    for nome, a, b, cor, rot in [
            ("2.7", 17.22, 18.47, "#5b93c9", "prior. A"),
            ("2.5/2.6", 19.10, 25.03, AZUL, "ENTRADA A"),
            ("2.4", 25.32, 31.25, AMBAR, "SAÍDA"),
            ("2.2/2.3", 31.54, 37.47, AZUL, "ENTRADA B"),
            ("2.1", 38.09, 39.36, "#5b93c9", "prior. B")]:
        (x1, y1), (x2, _) = px(a, 0), px(b, 0)
        o.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y1:.1f}" '
                 f'stroke="{cor}" stroke-width="7.5"/>')
        o.append(f'<text x="{(x1 + x2) / 2:.1f}" y="{y1 + 22:.1f}" {EST["prt"]} '
                 f'text-anchor="middle">{esc(rot)}</text>')
        o.append(f'<text x="{(x1 + x2) / 2:.1f}" y="{y1 + 33:.1f}" {EST["sub"]} '
                 f'text-anchor="middle">porta {esc(nome)}</text>')

    o.append(txt(6.0, 20.5, "ZONA A", "zona"))
    o.append(txt(36.5, 6.0, "ZONA B", "zona"))

    # ---------- titulo, escala, legenda
    t = d["totais"]
    o.append(f'<text x="{ML}" y="26" {EST["tit"]}>RDS Ballsbridge, Hall 2 — planta '
             f'de fluxo do 1º turno (04/10/2026)</text>')
    o.append(f'<text x="{ML}" y="44" {EST["sub"]}>50,2 × 44,5 m · 2.238 m² · 28 MRVs '
             f'· {t["esperado"]:,} eleitores esperados · 2 entradas + 1 saída · '
             f'baias dimensionadas para 55 s por eleitor</text>'.replace(",", "."))
    ax, ay = px(0, -1.3)
    bx, _ = px(10, -1.3)
    o.append(f'<line x1="{ax:.1f}" y1="{ay:.1f}" x2="{bx:.1f}" y2="{ay:.1f}" '
             f'stroke="#243244" stroke-width="2"/>')
    o.append(f'<text x="{(ax + bx) / 2:.1f}" y="{ay - 5:.1f}" {EST["sub"]} '
             f'text-anchor="middle">10 m</text>')

    ly, cx = MT + H * S + 88, ML
    for i, (c, lab, cheio) in enumerate([
            ("#33465c", "mesa receptora + urna (MRV)", True),
            (COR["leve"], "baia de fila — carga leve", False),
            (COR["media"], "carga média", False),
            (COR["alta"], "carga alta", False),
            (COR["critica"], "carga crítica", False),
            (AZUL, "avenida de entrada", False),
            (AMBAR, "fluxo de saída", False),
            (VERDE, "saída de emergência — manter livre", True)]):
        if i == 4:
            cx, ly = ML, ly + 20
        o.append(f'<rect x="{cx}" y="{ly - 8}" width="11" height="11" fill="{c}" '
                 f'opacity="{1 if cheio else .4}" stroke="{c}"/>')
        o.append(f'<text x="{cx + 16}" y="{ly + 1}" {EST["lbl"]}>{esc(lab)}</text>')
        cx += 24 + len(lab) * 5.3
    o.append(f'<text x="{ML}" y="{ly + 26}" {EST["sub"]}>Em cada baia: código da urna '
             f'(acima) e eleitores esperados (abaixo). A carga cresce com a distância '
             f'até a porta, de modo que nenhum eleitor de urna leve caminhe por trás '
             f'da fila de uma urna pesada.</text>')
    o.append("</svg>")

    cam = os.path.join(RAIZ, "saidas", "planta_fluxo.svg")
    with open(cam, "w", encoding="utf-8") as f:
        f.write("\n".join(o))
    print("gravado", cam, os.path.getsize(cam), "bytes")


if __name__ == "__main__":
    main()
