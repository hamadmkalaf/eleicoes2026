"""A prancheta pelas secoes: o cenario de trabalho com cada mesa rotulada pelas
secoes eleitorais que votam nela, em vez de numeros (Posto, 14/09/2026).

Le o cenario de trabalho por scripts/decisoes.py (posicoes, secoes, classe,
entrada, numeracao eleitor) e a geometria de data/prancheta_hall2.json, e grava:
  saidas/prancheta_secoes.svg    a planta em escala (22 px/m, para os numeros
                                 de secao caberem no modulo)
  saidas/prancheta_secoes.html   a peca: planta + tabela secao -> mesa
  (o PNG e tirado do SVG pelo Chromium no fechamento da sessao)

Uso: python3 scripts/gera_prancheta_secoes.py   (depois de gera_decisoes.py)
"""
import html as H
import json
import math
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "scripts"))
SAIDAS = os.path.join(RAIZ, "saidas")

import decisoes as DC                                          # noqa: E402

S = 22.0                     # px por metro
ML, MR, MT, MB = 70, 70, 84, 150
CLASSE_COR = {"alta": "#b23b2e", "media": "#c9a227", "baixa": "#3a9d5d"}
VERDE_SAIDA = "#16867f"
FONTE = ("font-family=\"ui-sans-serif,system-ui,'Segoe UI',Helvetica,Arial,sans-serif\"")


def px(x, y, alt):
    return ML + x * S, MT + (alt - y) * S


def esc(t):
    return str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def dir_(rot):
    r = math.radians(rot)
    return round(math.cos(r)), round(math.sin(r))


def corpo(mod, m):
    d = dir_(m["rot"])
    p = (-d[1], d[0])
    return [(m["x"] + d[0] * u + p[0] * v, m["y"] + d[1] * u + p[1] * v)
            for u, v in ((0, -mod["larg"] / 2), (mod["prof"], -mod["larg"] / 2),
                         (mod["prof"], mod["larg"] / 2), (0, mod["larg"] / 2))]


def planta(dec, P, pos):
    sal, mod = P["salao"], P["modulo"]
    alt = sal["altura"]
    cor_entrada = {e["id"]: e["hex"] for e in dec["entradas"]}
    porta_entrada = {e["porta"]: e for e in dec["entradas"]}
    ct = dec["cenario_trabalho"]

    def pt(x, y):
        a, b = px(x, y, alt)
        return f"{a:.1f},{b:.1f}"

    def txt(x, y, t, size=10, peso=400, cor="#243244", anchor="middle", rot=0, dy=0, dx=0, extra=""):
        a, b = px(x, y, alt)
        a += dx; b += dy
        tr = f' transform="rotate({rot} {a:.1f} {b:.1f})"' if rot else ""
        return (f'<text x="{a:.1f}" y="{b:.1f}" {FONTE} font-size="{size}" font-weight="{peso}" '
                f'fill="{cor}" text-anchor="{anchor}"{tr}{extra}>{esc(t)}</text>')

    o = ['<polygon points="' + " ".join(pt(x, y) for x, y in sal["contorno"]) + '" fill="#fbfaf7" stroke="#1f2c3c" stroke-width="2.4"/>']
    # portas
    for p in P["portas"]:
        if p["id"] in porta_entrada:
            cor, larg = porta_entrada[p["id"]]["hex"], 7
        elif p["id"] in dec["saidas"]:
            cor, larg = VERDE_SAIDA, 7
        else:
            cor, larg = "#9aa6b4", 4
        (x1, y1), (x2, y2) = px(p["x1"], p["y1"], alt), px(p["x2"], p["y2"], alt)
        o.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{cor}" stroke-width="{larg}" stroke-linecap="round"/>')
        cx, cy = (p["x1"] + p["x2"]) / 2, (p["y1"] + p["y2"]) / 2
        if p["face"] == "sul":
            rot = ("ENTRADA " + porta_entrada[p["id"]]["id"] + " · " if p["id"] in porta_entrada
                   else ("SAÍDA · " if p["id"] in dec["saidas"] else "")) + p["id"]
            o.append(txt(cx, cy, rot, 11, 700, dy=18))
        elif p["face"] == "norte":
            o.append(txt(cx, cy, p["id"], 9, 400, "#5c6c80", dy=-8))
        elif p["face"] == "leste":
            o.append(txt(cx, cy, p["id"], 9, 400, "#5c6c80", anchor="start", dx=12, dy=3))
        else:
            o.append(txt(cx, cy, p["id"], 9, 400, "#5c6c80", anchor="end", dx=-12, dy=3))
    # mesas
    for m in sorted(dec["mesas"], key=lambda m: m["mrv"]):
        q = pos[m["mrv"]]
        mm = dict(x=q["x"], y=q["y"], rot=int(q["rot"]) % 360)
        cor = CLASSE_COR[m["classe"]]
        o.append('<polygon points="' + " ".join(pt(x, y) for x, y in corpo(mod, mm)) + f'" fill="{cor}" opacity=".92" stroke="#1f2c3c" stroke-width=".7"/>')
        d = dir_(mm["rot"])
        cx, cy = mm["x"] + d[0] * mod["prof"] / 2, mm["y"] + d[1] * mod["prof"] / 2
        rot = {270: -90, 90: 90}.get(mm["rot"], 0)    # texto ao longo do modulo: vertical nas paredes norte e sul
        secoes = str(m["principal"]) + (f" · {m['agregada']}" if m["agregada"] else "")
        o.append(txt(cx, cy, secoes, 10.5, 700, "#fff", dy=4, rot=rot,
                     extra=' paint-order="stroke" stroke="#1f2c3c" stroke-width="2.2" stroke-linejoin="round"'))
        # letra da entrada na ponta da fila
        ex, ey = mm["x"] + d[0] * (mod["prof"] + 0.7), mm["y"] + d[1] * (mod["prof"] + 0.7)
        a, b = px(ex, ey, alt)
        o.append(f'<circle cx="{a:.1f}" cy="{b:.1f}" r="{0.45 * S:.1f}" fill="{cor_entrada[m["entrada"]]}" stroke="#fff" stroke-width="1.2"/>')
        o.append(txt(ex, ey, m["entrada"], 9.5, 700, "#fff", dy=3.5))
    # rotulos das paredes
    o.append(txt(sal["largura"] / 2, alt - 7.4, "PAREDE NORTE", 12, 700, "#243244", extra=' opacity=".35"'))
    o.append(txt(sal["largura"] / 2, 3.6, "FACHADA SUL", 12, 700, "#243244", extra=' opacity=".35"'))
    o.append(txt(7.6, alt / 2 + 4, "PAREDE OESTE", 12, 700, "#243244", rot=-90, extra=' opacity=".35"'))
    o.append(txt(sal["largura"] - 10.2, alt / 2, "PAREDE LESTE", 12, 700, "#243244", rot=90, extra=' opacity=".35"'))
    # titulo e legenda
    prov = " (provisório: Hamad_Final pendente)" if ct.get("provisorio") else ""
    o.append(txt(0, alt + 2.6, f"PRANCHETA PELAS SEÇÕES — cenário {ct['nome']}{prov}", 17, 700, "#1f2c3c", anchor="start"))
    o.append(txt(0, alt + 1.3, "Cada mesa mostra a seção principal e a agregada que votam nela; a cor é a carga esperada; a letra na ponta da fila é a entrada.", 9.5, 400, "#5c6c80", anchor="start"))
    y = -1.4
    itens = [(CLASSE_COR["alta"], "vermelha: as 3 de maior comparecimento"), (CLASSE_COR["media"], "amarela: 450 ou mais esperados"),
             (CLASSE_COR["baixa"], "verde: as demais"), (cor_entrada["A"], "entrada A (S4)"), (cor_entrada["B"], "entrada B (S5)"),
             (cor_entrada["C"], "entrada C (S6)"), (VERDE_SAIDA, "saída S2 / S8")]
    x = 0
    for cor, rot in itens:
        a, b = px(x, y + 0.45, alt)
        o.append(f'<rect x="{a:.1f}" y="{b:.1f}" width="{0.9 * S:.1f}" height="{0.9 * S:.1f}" fill="{cor}"/>')
        o.append(txt(x + 1.25, y, rot, 9.5, 400, "#5c6c80", anchor="start", dy=3))
        x += 1.25 + len(rot) * 0.27 + 1.0
    W = ML + sal["largura"] * S + MR
    Hh = MT + alt * S + MB
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.0f} {Hh:.0f}" width="{W:.0f}" height="{Hh:.0f}" role="img" '
            f'aria-label="Prancheta do Hall 2 no cenário {esc(ct["nome"])}, mesas rotuladas pelas seções eleitorais">'
            f'<rect width="{W:.0f}" height="{Hh:.0f}" fill="#fbfaf7"/>' + "".join(o) + "</svg>")


def tabela(dec):
    linhas = []
    for m in dec["mesas"]:
        linhas.append((m["principal"], m["mrv"], m["eleitor"], m["entrada"], m["parede"], m["esperado"], m["classe"]))
        if m["agregada"]:
            linhas.append((m["agregada"], m["mrv"], m["eleitor"], m["entrada"], m["parede"], m["esperado"], m["classe"]))
    linhas.sort()
    out = ["<table><thead><tr><th>Seção</th><th>Mesa (nº eleitor)</th><th>MRV oficial</th><th>Entrada</th><th>Parede</th><th>Esperados na mesa</th></tr></thead><tbody>"]
    for sec, mrv, el, ent, par, esp, cl in linhas:
        out.append(f'<tr><td class="mono">{sec}</td><td class="mono b">{el}</td><td class="mono">MRV {mrv}</td><td>{ent}</td><td>{par}</td><td class="num">{esp}</td></tr>')
    out.append("</tbody></table>")
    return "\n".join(out)


def pagina(dec, svg):
    ct = dec["cenario_trabalho"]
    return f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Prancheta pelas seções</title>
<style>
:root{{--bg:#fbfaf7;--fg:#1f2c3c;--mut:#5c6c80;--line:#dfe5ec;--card:#fff;--acc:#1f6fb2}}
@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{--bg:#151a21;--fg:#e8ecf1;--mut:#a3aebb;--line:#2c3542;--card:#1c232c;--acc:#7fb3e6}}}}
:root[data-theme="dark"]{{--bg:#151a21;--fg:#e8ecf1;--mut:#a3aebb;--line:#2c3542;--card:#1c232c;--acc:#7fb3e6}}
body{{background:var(--bg);color:var(--fg);font:15px/1.5 ui-sans-serif,system-ui,'Segoe UI',Helvetica,Arial,sans-serif;margin:0;padding:24px 16px 56px}}
main{{max-width:1240px;margin:0 auto}}h1{{font-size:1.6rem;line-height:1.2;margin:.2em 0 .3em;text-wrap:balance}}h2{{font-size:1.15rem;margin:1.6em 0 .5em;color:var(--acc)}}
p{{margin:.5em 0;max-width:80ch}}.lead{{color:var(--mut)}}
figure{{margin:16px 0;background:var(--card);border:1px solid var(--line);border-radius:6px;padding:8px;overflow-x:auto}}figure svg{{display:block;width:100%;height:auto;min-width:720px}}
.tw{{overflow-x:auto}}table{{border-collapse:collapse;font-size:13.5px;min-width:640px;font-variant-numeric:tabular-nums}}
th,td{{border-bottom:1px solid var(--line);padding:5px 10px;text-align:left}}th{{color:var(--mut);font-weight:600;white-space:nowrap}}
td.num{{text-align:right}}.mono{{font-family:ui-monospace,SFMono-Regular,Menlo,monospace}}.b{{font-weight:700}}
</style></head><body><main>
<h1>Prancheta pelas seções: quem vota onde no {H.escape(ct["nome"])}</h1>
<p class="lead">As 28 mesas receptoras nas posições do cenário de trabalho da prancheta, rotuladas pela seção eleitoral principal e pela agregada que votam em cada uma. A cor é a carga esperada (base B); a letra na ponta da fila é a entrada da fachada sul por onde os eleitores daquela mesa chegam. Gerado por <code>scripts/gera_prancheta_secoes.py</code>; a numeração eleitor e o MRV de cada mesa estão na tabela abaixo.</p>
<figure>{svg}</figure>
<h2>Seção → mesa</h2>
<div class="tw">{tabela(dec)}</div>
</main></body></html>
"""


def main():
    dec = DC.montar()
    with open(DC.PRANCHETA, encoding="utf-8") as f:
        P = json.load(f)
    pos = DC.posicoes()
    svg = planta(dec, P, pos)
    with open(os.path.join(SAIDAS, "prancheta_secoes.svg"), "w", encoding="utf-8") as f:
        f.write(svg)
    with open(os.path.join(SAIDAS, "prancheta_secoes.html"), "w", encoding="utf-8") as f:
        f.write(pagina(dec, svg))
    print("gravado saidas/prancheta_secoes.svg e saidas/prancheta_secoes.html "
          f"(cenário {dec['cenario_trabalho']['nome']})")


if __name__ == "__main__":
    main()
