"""Desenha a planta da ideia 1 a partir de saidas/ideia1_dados.json.

Tudo em escala: as coordenadas vem em metros do modelo e viram px aqui. O SVG
usa atributos de apresentacao (nao classes CSS) para renderizar igual em
navegador, visualizador de imagem e impressao.
"""
import json, math, os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = 15.0                              # px por metro
ML, MR, MT, MB = 64, 64, 76, 200      # margens em px
W, H = 50.3, 44.4                     # dimensoes uteis do salao, em metros

# Paleta verificada com o validador de paletas (separacao para daltonismo e
# visao normal). Fluxos: tres matizes categoricos. Baias: rampa sequencial
# neutra, do claro ao escuro conforme a carga da urna.
AZUL, AMBAR, VERDE, VERM = "#1f6fb2", "#b26a12", "#16867f", "#b23b2e"
COR = {"leve": "#e9ecef", "media": "#b2bcc8", "alta": "#75808e", "critica": "#3b4552"}
MODULO, MESA, URNA = "#0f1620", "#5d6773", "#c3ccd6"
FONTE = ('font-family="ui-sans-serif,system-ui,\'Segoe UI\',Helvetica,Arial,'
         'sans-serif"')
EST = {
    "lbl":  f'{FONTE} font-size="9.5" fill="#243244"',
    "sub":  f'{FONTE} font-size="8" fill="#5c6c80"',
    "urna": f'{FONTE} font-size="10" font-weight="700" fill="#1f2c3c"',
    "urnac": f'{FONTE} font-size="10" font-weight="700" fill="#f2f5f8"',
    "subc": f'{FONTE} font-size="8" fill="#c6cfd8"',
    "tit":  f'{FONTE} font-size="16" font-weight="700" fill="#1f2c3c"',
    "prt":  f'{FONTE} font-size="9.5" font-weight="700" fill="#243244"',
    "zona": f'{FONTE} font-size="12" font-weight="700" fill="#243244" opacity=".4"',
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


def par(x, y, cima, baixo, claro=False):
    a, b = px(x, y)
    e1, e2 = (EST["urnac"], EST["subc"]) if claro else (EST["urna"], EST["sub"])
    return (f'<text x="{a:.1f}" y="{b - 2:.1f}" {e1} text-anchor="middle">'
            f'{esc(cima)}</text><text x="{a:.1f}" y="{b + 8:.1f}" {e2} '
            f'text-anchor="middle">{esc(baixo)}</text>')


def ponta(x, y, ang, cor, tam=4.4):
    a, b = px(x, y)
    p = []
    for da, r in ((0, tam * 1.7), (140, tam), (220, tam)):
        t = math.radians(ang + da)
        p.append(f"{a + r * math.cos(t):.1f},{b - r * math.sin(t):.1f}")
    return f'<polygon points="{" ".join(p)}" fill="{cor}"/>'


def rota(pts, cor, larg_m, op=".16"):
    """Corredor de circulacao: faixa larga translucida com setas de sentido."""
    d = " ".join(f"{px(x, y)[0]:.1f},{px(x, y)[1]:.1f}" for x, y in pts)
    o = [f'<polyline points="{d}" fill="none" stroke="{cor}" '
         f'stroke-width="{larg_m * S:.1f}" stroke-linejoin="round" '
         f'stroke-linecap="butt" opacity="{op}"/>']
    for i in range(len(pts) - 1):
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        ang = math.degrees(math.atan2(y1 - y0, x1 - x0))
        o.append(ponta((x0 + x1) / 2, (y0 + y1) / 2, ang, cor))
    return "".join(o)


def modulo(m):
    """Modulo mesa+urna, em escala: mesa dos mesarios de 1,60 x 0,70 m voltada
    para a fila, mesa redonda da urna de 0,90 m atras dela, e a tela da urna
    voltada para o painel lateral leste — perpendicular a fila e ao retorno."""
    x, y = m["x"], m["y"]
    lw, dp = 2.80, 1.90
    o = [rect(x - lw / 2, y, x + lw / 2, y + dp, fill=MODULO)]
    o.append(rect(x - lw / 2 + 0.15, y + 0.2, x - lw / 2 + 1.75, y + 0.9,
                  fill=MESA))                                   # mesa mesarios
    cx, cy = px(x + 0.55, y + 1.25)
    o.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{0.45 * S:.1f}" '
             f'fill="{URNA}"/>')                                 # mesa da urna
    px0, py0 = px(x + lw / 2 - 0.12, y + 1.85)
    px1, py1 = px(x + lw / 2 - 0.12, y + 0.6)
    o.append(f'<line x1="{px0:.1f}" y1="{py0:.1f}" x2="{px1:.1f}" y2="{py1:.1f}" '
             f'stroke="{VERM}" stroke-width="2.4"/>')            # painel da tela
    return "".join(o)


def main():
    d = json.load(open(os.path.join(RAIZ, "saidas", "ideia1_dados.json"),
                       encoding="utf-8"))
    LG, AL = ML + W * S + MR, MT + H * S + MB
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {LG:.0f} {AL:.0f}" '
         f'width="{LG:.0f}" height="{AL:.0f}" role="img" aria-label="Planta de '
         f'fluxo do Hall 2 do RDS com as 28 mesas receptoras de votos">',
         f'<rect x="0" y="0" width="{LG}" height="{AL}" fill="#fbfaf7"/>']

    # ---------- zonas
    esp = d["espinha_saida"]
    o.append(rect(0, 0, esp["x0"], H, fill=AZUL, opacity=".045"))
    o.append(rect(esp["x1"], 0, W, H, fill=AMBAR, opacity=".04"))
    o.append(rect(0, 0, 7.8, 7.0, fill="#fbfaf7"))
    poly = [(7.8, 0), (W, 0), (W, H), (0, H), (0, 7.0), (7.8, 7.0)]
    pts = " ".join(f"{px(x, y)[0]:.1f},{px(x, y)[1]:.1f}" for x, y in poly)
    o.append(f'<polygon points="{pts}" fill="none" stroke="#1c2733" stroke-width="3.4"/>')

    # ---------- envelope de 3 m das saidas de emergencia
    r = d["recuo_emergencia_m"]
    for lado, lista in d["portas"].items():
        for nome, a, b in lista:
            if lado == "sul" and "carga" in nome:
                continue
            if lado == "norte":
                z = (a - r, H - r, b + r, H)
            elif lado == "sul":
                z = (a - r, 0, b + r, r)
            elif lado == "oeste":
                z = (0, a - r, r, b + r)
            else:
                z = (W - r, a - r, W, b + r)
            o.append(rect(*z, fill=VERDE, opacity=".07", stroke=VERDE,
                          stroke_width="0.9", stroke_dasharray="3 3"))

    # ---------- corredores
    o.append(rota([(28.5, 43.0), (28.5, 1.6)], AMBAR, 5.0, ".17"))
    o.append(txt(28.5, 33.0, "ESPINHA DE SAÍDA", "via", rot=-90))
    # zona A: o conector da porta de carga sobe pelo avental e so entao vira
    # para oeste, porque abaixo de y = 7 o canto sudoeste do salao e recortado
    o.append(rota([(9.6, 2.4), (9.6, 8.4), (4.5, 8.4), (4.5, 26.0)], AZUL, 3.0))
    o.append(rota([(46.2, 2.4), (46.2, 26.0)], AZUL, 3.0))
    for xa, sinal in ((4.5, 1), (46.2, -1)):
        xi = 3.0 if sinal > 0 else 45.0
        xf = 26.0 if sinal > 0 else 31.0
        for y in (14.3, 25.7):                                    # distribuicao
            o.append(rota([(xa, y), (xf, y)], AZUL, 3.4))
        for y in (11.3, 22.7, 42.9):                              # retornos
            o.append(rota([(xi if y > 40 else (7.9 if sinal > 0 else xi), y),
                           (esp["x0"] if sinal > 0 else esp["x1"], y)],
                          AMBAR, 2.4, ".14"))
    o.append(txt(4.5, 19.0, "AVENIDA A", "via", rot=-90))
    o.append(txt(46.2, 20.0, "AVENIDA B", "via", rot=-90))
    o.append(txt(16.0, 43.4, "retorno da fileira 1", "via"))
    o.append(txt(16.0, 2.6, "AVENTAL SUL — triagem e distribuição da fileira 3", "via"))

    # ---------- baias de fila e modulos
    for m in d["mrvs"]:
        lw, dp, x, y = m["baia_largura"], m["baia_profundidade"], m["x"], m["y"]
        c = COR[m["classe"]]
        o.append(rect(x - lw / 2, y - dp, x + lw / 2, y, fill=c, opacity=".85",
                      stroke="#6b7480", stroke_width="1", stroke_dasharray="4 3"))
        o.append(modulo(m))
        o.append(par(x, y - dp / 2 + 1.0 if dp > 5 else y - dp / 2,
                     m["urna"], m["esperado"],
                     m["classe"] in ("alta", "critica")))

    # ---------- setor reforcado
    o.append(rect(2.7, 27.2, 19.8, 41.7, fill="none", stroke=VERM,
                  stroke_width="1.6", stroke_dasharray="8 4"))
    o.append(txt(11.2, 26.3, "SETOR REFORÇADO — 3 urnas Dublin+Dublin, "
                 "4 mesários cada", "via"))
    # ---------- reserva de fila para o cenario de 60 s
    for x0, x1, y0, y1 in ((20.0, 25.8, 27.6, 34.0), (31.2, 44.8, 27.6, 34.0)):
        o.append(rect(x0, y0, x1, y1, fill="none", stroke="#8a97a6",
                      stroke_width="1.2", stroke_dasharray="7 5"))
    o.append(txt(38.0, 30.6, "RESERVA DE FILA", "via"))
    o.append(txt(38.0, 29.4, "piso livre para o cenário de 60 s", "sub"))
    o.append(txt(22.9, 30.6, "RESERVA", "via"))

    # ---------- portas da parede sul
    papel = {"carga oeste": (AZUL, "ENTRADA A", "porta de carga · 3,62 m"),
             "carga leste": (AZUL, "ENTRADA B", "porta de carga · 3,63 m"),
             "2.4": (AMBAR, "SAÍDA", "2.4 · 5,93 m"),
             "2.5/2.6": ("#d9a25c", "reforço", "2.5/2.6"),
             "2.2/2.3": ("#d9a25c", "reforço", "2.2/2.3"),
             "2.7": (VERDE, "", "2.7"), "2.1": (VERDE, "", "2.1")}
    for nome, a, b in d["portas"]["sul"]:
        cor, rot, sub = papel[nome]
        (x1, y1), (x2, _) = px(a, 0), px(b, 0)
        o.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y1:.1f}" '
                 f'stroke="{cor}" stroke-width="7.5"/>')
        yy = y1 + (22 if rot else 33)
        if rot:
            o.append(f'<text x="{(x1 + x2) / 2:.1f}" y="{yy:.1f}" {EST["prt"]} '
                     f'text-anchor="middle">{esc(rot)}</text>')
        o.append(f'<text x="{(x1 + x2) / 2:.1f}" y="{y1 + 33:.1f}" {EST["sub"]} '
                 f'text-anchor="middle">{esc(sub)}</text>')

    o.append(txt(15.0, 12.6, "ZONA A", "zona"))
    o.append(txt(38.0, 32.5, "ZONA B", "zona"))

    # ---------- titulo, escala, legenda
    t = d["totais"]
    o.append(f'<text x="{ML}" y="26" {EST["tit"]}>RDS Ballsbridge, Hall 2 — planta '
             f'de fluxo do 1º turno (04/10/2026)</text>')
    o.append(f'<text x="{ML}" y="44" {EST["sub"]}>50,2 × 44,5 m · 2.238 m² · 28 MRVs '
             f'em três fileiras · módulo de 2,80 × 1,90 m · recuo de 3 m das saídas '
             f'de emergência · baias dimensionadas para 55 s por eleitor</text>')
    ax, ay = px(0, -1.3)
    bx, _ = px(10, -1.3)
    o.append(f'<line x1="{ax:.1f}" y1="{ay:.1f}" x2="{bx:.1f}" y2="{ay:.1f}" '
             f'stroke="#243244" stroke-width="2"/>')
    o.append(f'<text x="{(ax + bx) / 2:.1f}" y="{ay - 5:.1f}" {EST["sub"]} '
             f'text-anchor="middle">10 m</text>')

    ly, cx = MT + H * S + 96, ML
    itens = [(MODULO, "módulo mesa + urna", True),
             (COR["leve"], "baia de fila — carga leve", False),
             (COR["media"], "carga média", False),
             (COR["alta"], "carga alta", True),
             (COR["critica"], "carga crítica", True),
             (AZUL, "avenida e corredor de entrada", False),
             (AMBAR, "corredor de retorno e saída", False),
             (VERDE, "recuo de 3 m das saídas de emergência", False),
             (VERM, "painel para onde aponta a tela da urna", True)]
    for i, (c, lab, cheio) in enumerate(itens):
        if i in (5, 8):
            cx, ly = ML, ly + 20
        o.append(f'<rect x="{cx}" y="{ly - 8}" width="11" height="11" fill="{c}" '
                 f'opacity="{1 if cheio else .45}" stroke="{c}"/>')
        o.append(f'<text x="{cx + 16}" y="{ly + 1}" {EST["lbl"]}>{esc(lab)}</text>')
        cx += 24 + len(lab) * 5.3
    o.append(f'<text x="{ML}" y="{ly + 26}" {EST["sub"]}>Em cada baia: código da urna '
             f'(acima) e eleitores esperados (abaixo). Os módulos das três fileiras '
             f'olham todos para o sul: o eleitor entra na baia pelo corredor de '
             f'distribuição, vota, e sai pelo fundo do módulo no corredor de retorno, '
             f'que corre para a espinha central.</text>')
    o.append("</svg>")

    cam = os.path.join(RAIZ, "saidas", "ideia1_planta.svg")
    open(cam, "w", encoding="utf-8").write("\n".join(o))
    print("gravado", cam, os.path.getsize(cam), "bytes")


if __name__ == "__main__":
    main()
