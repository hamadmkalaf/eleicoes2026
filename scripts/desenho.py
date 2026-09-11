"""Primitivas de desenho das plantas do Hall 2.

Tudo em escala: as coordenadas vem em metros do modelo do salao e viram px
aqui. O SVG usa atributos de apresentacao (nao classes CSS) para renderizar
igual em navegador, visualizador de imagem e impressao.

Origem do desenho igual a de `salao.py`: canto sudoeste util do salao, x para
leste, y para norte. `px` inverte y, porque o SVG cresce para baixo.
"""
import math
import os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = 15.0                              # px por metro
ML, MR, MT, MB = 64, 64, 76, 200      # margens em px
W, H = 50.3, 44.4                     # dimensoes uteis do salao, em metros

# Paleta verificada com o validador de paletas (separacao para daltonismo e
# visao normal).
AZUL, AMBAR, VERDE, VERM = "#1f6fb2", "#b26a12", "#16867f", "#b23b2e"
MODULO, MESA, URNA = "#0f1620", "#5d6773", "#c3ccd6"
FONTE = ('font-family="ui-sans-serif,system-ui,\'Segoe UI\',Helvetica,Arial,'
         'sans-serif"')
EST = {
    "lbl":  f'{FONTE} font-size="9.5" fill="#243244"',
    "sub":  f'{FONTE} font-size="8" fill="#5c6c80"',
    "cod":  f'{FONTE} font-size="12" font-weight="700" fill="#1f2c3c"',
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


def txt(x, y, t, est="lbl", anchor="middle", rot=0, dy=0, dx=0):
    a, b = px(x, y)
    a += dx
    b += dy
    tr = f' transform="rotate({rot} {a:.1f} {b:.1f})"' if rot else ""
    return (f'<text x="{a:.1f}" y="{b:.1f}" {EST[est]} '
            f'text-anchor="{anchor}"{tr}>{esc(t)}</text>')


def ponta(x, y, ang, cor, tam=4.4):
    """Ponta de seta, em graus no sentido anti-horario a partir do leste."""
    a, b = px(x, y)
    p = []
    for da, r in ((0, tam * 1.7), (140, tam), (220, tam)):
        t = math.radians(ang + da)
        p.append(f"{a + r * math.cos(t):.1f},{b - r * math.sin(t):.1f}")
    return f'<polygon points="{" ".join(p)}" fill="{cor}"/>'


def cota(x0, y0, x1, y1, rotulo, dy=0, dx=0):
    """Linha de cota com marcas nas pontas e o rotulo no meio."""
    a, b = px(x0, y0)
    c, d = px(x1, y1)
    vertical = abs(b - d) > abs(a - c)
    o = [f'<path d="M{a:.1f} {b:.1f}L{c:.1f} {d:.1f}" stroke="{MESA}" '
         f'stroke-width="0.8" opacity=".8"/>']
    for mx, my in ((a, b), (c, d)):
        ex, ey = (0, 3) if not vertical else (3, 0)
        o.append(f'<line x1="{mx - ex:.1f}" y1="{my - ey:.1f}" '
                 f'x2="{mx + ex:.1f}" y2="{my + ey:.1f}" stroke="{MESA}" '
                 f'stroke-width="0.8"/>')
    o.append(txt((x0 + x1) / 2, (y0 + y1) / 2, rotulo, "sub", dy=dy, dx=dx,
                 rot=-90 if vertical else 0))
    return "".join(o)


def estilo():
    """A folha de estilo comum as pecas de leitura."""
    with open(os.path.join(RAIZ, "scripts", "estilo_plano.css"),
              encoding="utf-8") as f:
        return f.read().rstrip("\n")
