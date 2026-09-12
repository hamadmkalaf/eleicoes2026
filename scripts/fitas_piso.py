"""Fitas no piso em vez do checkpoint: desenho sobre a planta e pagina.

Le saidas/fitas_piso.json (gravado por `node simulador/fitas.js`) e produz:
  saidas/fitas_piso_referencia.svg   planta do Cenario Claude (checkpoint)
  saidas/fitas_piso_decisao.svg      fitas por tronco, atribuicao da decisao
  saidas/fitas_piso_parede.svg       fitas por tronco, atribuicao por parede
  saidas/fitas_piso.md               tabelas
  saidas/fitas_piso.html             pagina com tudo

A geometria e a da prancheta (data/prancheta_hall2.json) resolvida pelo
motor do simulador sobre o arranjo "Tres polos"; este script nao recalcula
nada, so desenha e tabula.
"""
import json
import math
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "scripts"))
import desenho as D                                            # noqa: E402
from desenho import EST, S, esc, px                            # noqa: E402

SAIDAS = os.path.join(RAIZ, "saidas")
VERDE_SAIDA = "#16867f"
CLASSE_COR = {"alta": "#b23b2e", "media": "#b26a12", "baixa": "#16867f"}


def vg(v, c=0):
    s = f"{v:,.{c}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return s


def dir_(rot):
    r = math.radians(rot)
    return round(math.cos(r)), round(math.sin(r))


def corpo(modulo, m):
    d = dir_(m["rot"]); p = (-d[1], d[0])
    pts = []
    for u, v in ((0, -modulo["larg"] / 2), (modulo["prof"], -modulo["larg"] / 2),
                 (modulo["prof"], modulo["larg"] / 2), (0, modulo["larg"] / 2)):
        pts.append((m["x"] + d[0] * u + p[0] * v, m["y"] + d[1] * u + p[1] * v))
    return pts


def poly(pts, **kw):
    at = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in kw.items())
    return '<polygon points="' + " ".join(f"{px(x, y)[0]:.1f},{px(x, y)[1]:.1f}" for x, y in pts) + f'" {at}/>'


def polyline(pts, **kw):
    at = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in kw.items())
    return '<polyline points="' + " ".join(f"{px(x, y)[0]:.1f},{px(x, y)[1]:.1f}" for x, y in pts) + f'" fill="none" {at}/>'


def linha(a, b, **kw):
    at = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in kw.items())
    (x1, y1), (x2, y2) = px(*a), px(*b)
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" {at}/>'


def circulo(c, r_m, **kw):
    at = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in kw.items())
    x, y = px(*c)
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r_m * S:.1f}" {at}/>'


def planta(P, titulo, subtitulo, modo, G=None, chave_entrada="entradaDecisao"):
    sal, mod = P["salao"], P["modulo"]
    cor_entrada = {e["letra"]: e["cor"] for e in P["entradas"]}
    porta_entrada = {e["porta"]: e for e in P["entradas"]}
    o = []
    # salao e recorte
    o.append(poly(sal["contorno"], fill="#fbfaf7", stroke="#1f2c3c", stroke_width="2"))
    for z in P["zonasProtegidas"]:
        r = z["rect"]
        o.append(D.rect(r[0], r[1], r[2], r[3], fill="#dfe5ec", opacity=".55"))
    # portas
    for p in P["portas"]:
        if p["id"] in porta_entrada:
            cor, larg = porta_entrada[p["id"]]["cor"], 5
        elif p["id"] in ("S2", "S8"):
            cor, larg = VERDE_SAIDA, 5
        else:
            cor, larg = "#9aa6b4", 3
        o.append(linha((p["x1"], p["y1"]), (p["x2"], p["y2"]), stroke=cor, stroke_width=larg, stroke_linecap="round"))
        cx, cy = (p["x1"] + p["x2"]) / 2, (p["y1"] + p["y2"]) / 2
        if p["face"] == "sul":
            rot = ("ENTRADA " + porta_entrada[p["id"]]["letra"] + " · " if p["id"] in porta_entrada
                   else ("SAÍDA · " if p["id"] in ("S2", "S8") else "")) + p["id"]
            o.append(D.txt(cx, cy, rot, "prt", dy=14))
        elif p["face"] == "norte":
            o.append(D.txt(cx, cy, p["id"], "sub", dy=-6))
        elif p["face"] == "leste":
            o.append(D.txt(cx, cy, p["id"], "sub", dx=14, dy=3))
        else:
            o.append(D.txt(cx, cy, p["id"], "sub", dx=-14, dy=3))
    # fitas ou checkpoint (por baixo das mesas)
    if modo == "checkpoint":
        cp = P["checkpointClaude"]
        for e, ponto in zip(P["entradas"], cp["pontos"]):
            c = e["centro"]
            o.append(D.rect(c[0] - 1.5, 0, c[0] + 1.5, cp["dist"], fill=e["cor"], opacity=".18"))
            o.append(linha(c, ponto, stroke=e["cor"], stroke_width="2", stroke_dasharray="6 4"))
            o.append(circulo(ponto, 0.9, fill=e["cor"]))
            o.append(D.txt(ponto[0], ponto[1], "CP " + e["letra"], "prt", dy=3.5))
        for m in P["mesas"]:
            e = next(x for x in P["entradas"] if x["letra"] == m["entradaDecisao"])
            ponto = cp["pontos"][P["entradas"].index(e)]
            o.append(linha(ponto, m["cauda"], stroke=e["cor"], stroke_width="0.9", opacity=".55", stroke_dasharray="3 3"))
    else:
        for t in G["troncos"]:
            o.append(polyline(t["pontos"], stroke=t["cor"], stroke_width="4", opacity=".85", stroke_linejoin="round"))
    # mesas
    for m in P["mesas"]:
        cor = CLASSE_COR[m["classe"]]
        o.append(poly(corpo(mod, m), fill=cor, opacity=".9", stroke="#1f2c3c", stroke_width=".6"))
        o.append(linha(m["frente"], m["cauda"], stroke="#1f2c3c", stroke_width="1.2", stroke_dasharray="2 2", opacity=".7"))
        d = dir_(m["rot"])
        cx, cy = m["x"] + d[0] * mod["prof"] / 2, m["y"] + d[1] * mod["prof"] / 2
        letra = m[chave_entrada]
        o.append(D.txt(cx, cy, str(m["mrv"]), "cod", dy=4, rot=0 if m["rot"] in (0, 180) else 0))
        # marca da entrada junto a cauda
        cx2, cy2 = m["cauda"]
        o.append(circulo((cx2, cy2), 0.45, fill=cor_entrada[letra], stroke="#fff", stroke_width=".8"))
        o.append(D.txt(cx2, cy2, letra, "sub", dy=3) .replace('fill="#5c6c80"', 'fill="#fff" font-weight="700"'))
    # titulo e legenda
    o.append(D.txt(0, D.H + 2.6, titulo, "tit", anchor="start"))
    o.append(D.txt(0, D.H + 1.3, subtitulo, "sub", anchor="start"))
    y = -1.6
    for letra, cor in cor_entrada.items():
        pass
    itens = [(cor_entrada["A"], "fita da entrada A (S4)"), (cor_entrada["B"], "fita da entrada B (S5)"),
             (cor_entrada["C"], "fita da entrada C (S6)"), (VERDE_SAIDA, "saída S2 / S8"),
             (CLASSE_COR["alta"], "mesa vermelha"), (CLASSE_COR["media"], "mesa amarela"), (CLASSE_COR["baixa"], "mesa verde")]
    x = 0
    for cor, rot in itens:
        o.append(D.rect(x, y - 0.5, x + 0.9, y + 0.5, fill=cor))
        o.append(D.txt(x + 1.3, y, rot, "sub", anchor="start", dy=3))
        x += 1.3 + len(rot) * 0.36 + 1.2
    o.append(D.txt(0, y - 1.7, "Tracejado curto à frente de cada mesa: a fila prevista (3/4/6 pessoas). Círculo na ponta da fila: entrada que serve a mesa.", "sub", anchor="start"))
    W = D.ML + D.W * S + D.MR
    H = D.MT + D.H * S + 70
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.0f} {H:.0f}" width="100%" '
            f'role="img" aria-label="{esc(titulo)}">' + "".join(o) + "</svg>")


def tabela(linhas, cab):
    out = ["| " + " | ".join(cab) + " |", "|" + "---|" * len(cab)]
    for l in linhas:
        out.append("| " + " | ".join(str(c) for c in l) + " |")
    return "\n".join(out)


def markdown(J):
    R, G = J["resultados"], J["geometria"]
    ref = next(r for r in R if r["id"] == "ref")
    md = ["# Fitas no piso em vez do checkpoint: o que o simulador diz\n",
          f"Arranjo **{J['arranjo']}**, entradas S4/S5/S6 e saídas S2/S8 da decisão de 06/09, base B (11.499 esperados), "
          f"identificação de 45 s e voto de 30 s salvo onde indicado, {J['runs']} dias simulados por cenário. "
          "Motor: `simulador/modelo.js`, o mesmo do simulador publicado; varredura em `simulador/fitas.js`.\n"]
    md.append("## Resultados por cenário\n")
    md.append("Espera P90 = tempo da chegada ao Ring 3 até o voto para nove em dez eleitores (fora + dentro). "
              "\"Chegadas a fila cheia\" = eleitores que chegaram à mesa com a fila já além do comprimento previsto "
              "(sem checkpoint ninguém os retém). \"Fome\" = minutos em que uma mesa vermelha ficou ociosa com gente esperando fora.\n")
    cab = ["Cenário", "Fecha (p50 / p90)", "Espera P90", "fora / dentro", "Pico dentro", "Pico Ring 3", "Fome vermelhas", "Chegadas a fila cheia", "Perdidos", "Fita", "Veredito"]
    grupos = []
    for r in R:
        if r["grupo"] not in grupos:
            grupos.append(r["grupo"])
    for g in grupos:
        md.append(f"### {g}\n")
        ls = []
        for r in [x for x in R if x["grupo"] == g]:
            ruins = "; ".join(f"{x['titulo'].lower()} ({x['status']})" for x in r["ruins"]) or "todos os critérios ok"
            ls.append([r["nome"], f"{r['fechaP50']} / {r['fechaP90']}", f"{r['p90TotalMin']} min", f"{r['p90ForaMin']} / {r['p90DentroMin']}",
                       vg(r["dentroMax"]), vg(r["ring3Max"]), f"{r['fomeVermelhasMin']} min", vg(r["estouroFilas"]), vg(r["perdidos"]),
                       f"{r['fita_m']} m", f"**{r['nota']}**: {ruins}"])
        md.append(tabela(ls, cab)); md.append("")
    md.append("## Geometria das fitas sobre o arranjo\n")
    md.append("Fita por mesa = uma reta da soleira da porta à ponta da fila de cada mesa (a sugestão literal). "
              "Troncos = uma fita por parede servida por cada entrada, correndo rente à parede e passando pela ponta da fila de cada mesa. "
              "Cruzamentos contam pares de fitas de entradas diferentes que se cortam no piso; fita × saída conta fitas cortadas pelo trajeto de quem sai.\n")
    cab = ["Atribuição mesa → entrada", "Fita por mesa", "Troncos", "Cruzamentos entre entradas (por mesa / troncos)", "Fita × saída", "Porta mais carregada ÷ menos"]
    ls = []
    for k in ("decisao", "geografica"):
        g = G[k]
        ls.append([g["rotulo"], f"{vg(g['fitaPorMesa_m'])} m", f"{vg(g['fitaTroncos_m'])} m", f"{g['cruzEntre']} / {g['cruzTroncos']}", g["cruzSaida"], f"{g['desequilibrio']:.2f}×"])
    md.append(tabela(ls, cab)); md.append("")
    for k in ("decisao", "geografica"):
        g = G[k]
        md.append(f"**{g['rotulo']}**\n")
        cab = ["Entrada", "Porta", "Mesas (MRV)", "Esperados", "Cabe no Ring 3", "Paredes servidas", "Troncos", "Caminho médio porta → fila"]
        md.append(tabela([[e["entrada"], e["porta"], ", ".join(map(str, e["mesas"])), vg(e["esperados"]), vg(e["capRing3"]), " / ".join(e["paredes"]),
                          f"{e['nTroncos']} ({vg(e['fitaTroncos_m'])} m)", f"{e['distMedia_m']:.1f} m"] for e in g["porEntrada"]], cab))
        md.append("")
    return "\n".join(md) + "\n"


def html(J, svgs, md):
    import html as H
    linhas, out, tab = md.splitlines(), [], []

    def inline(s):
        s = H.escape(s)
        while "**" in s:
            s = s.replace("**", "<b>", 1).replace("**", "</b>", 1)
        while "`" in s:
            s = s.replace("`", "<code>", 1).replace("`", "</code>", 1)
        return s

    def flush():
        nonlocal tab
        if tab:
            out.append("<div class='tw'><table>")
            for i, r in enumerate(tab):
                if set(r.replace("|", "").strip()) <= set("-: "):
                    continue
                cels = [c.strip() for c in r.strip().strip("|").split("|")]
                tag = "th" if i == 0 else "td"
                out.append("<tr>" + "".join(f"<{tag}>{inline(c)}</{tag}>" for c in cels) + "</tr>")
            out.append("</table></div>")
            tab = []
    for l in linhas:
        if l.startswith("|"):
            tab.append(l); continue
        flush()
        if l.startswith("# "):
            continue
        if l.startswith("## "):
            out.append(f"<h2>{inline(l[3:])}</h2>")
        elif l.startswith("### "):
            out.append(f"<h3>{inline(l[4:])}</h3>")
        elif l.strip():
            out.append(f"<p>{inline(l)}</p>")
    flush()
    corpo_html = "\n".join(out)
    figs = "".join(f"<figure>{svg}<figcaption>{esc(cap)}</figcaption></figure>" for svg, cap in svgs)
    return f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Fitas no piso do Hall 2</title>
<style>
:root{{--bg:#fbfaf7;--fg:#1f2c3c;--mut:#5c6c80;--line:#dfe5ec;--card:#fff;--acc:#1f6fb2}}
@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{--bg:#151a21;--fg:#e8ecf1;--mut:#a3aebb;--line:#2c3542;--card:#1c232c;--acc:#7fb3e6}}}}
:root[data-theme="dark"]{{--bg:#151a21;--fg:#e8ecf1;--mut:#a3aebb;--line:#2c3542;--card:#1c232c;--acc:#7fb3e6}}
body{{background:var(--bg);color:var(--fg);font:15px/1.5 ui-sans-serif,system-ui,'Segoe UI',Helvetica,Arial,sans-serif;margin:0;padding:24px 16px 56px}}
main{{max-width:1180px;margin:0 auto}}h1{{font-size:1.6rem;line-height:1.2;margin:.2em 0 .3em;text-wrap:balance}}
h2{{font-size:1.15rem;margin:1.8em 0 .5em;color:var(--acc)}}h3{{font-size:1rem;margin:1.2em 0 .3em}}p{{margin:.5em 0;max-width:80ch}}
.lead{{color:var(--mut);max-width:80ch}}
.figs{{display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:18px;margin:18px 0}}
figure{{margin:0;background:var(--card);border:1px solid var(--line);border-radius:6px;padding:8px}}figure svg{{width:100%;height:auto;display:block}}
figcaption{{color:var(--mut);font-size:13px;padding:8px 4px 2px;line-height:1.4}}
.tw{{overflow-x:auto;margin:.6em 0}}table{{border-collapse:collapse;font-size:13px;min-width:1100px;font-variant-numeric:tabular-nums}}
th,td{{border-bottom:1px solid var(--line);padding:5px 9px;text-align:left;vertical-align:top}}td:first-child{{min-width:240px}}td:last-child{{min-width:280px}}th{{color:var(--mut);font-weight:600;white-space:nowrap}}
code{{font-size:.92em;background:var(--line);padding:0 4px;border-radius:3px}}
</style></head><body><main>
<h1>Fitas no piso em vez do checkpoint</h1>
<p class="lead">O que muda no Hall 2 se o ponto de triagem a 16 m da porta sair e o eleitor for guiado da porta à mesa por fitas coloridas no piso. Simulado no motor oficial do projeto sobre o arranjo <b>{esc(J['arranjo'])}</b>, com as entradas, saídas e o comparecimento da decisão de 06/09/2026. Gerado em {J['geradoEm'][:10]}.</p>
<div class="figs">{figs}</div>
{corpo_html}
</main></body></html>
"""


def main():
    J = json.load(open(os.path.join(SAIDAS, "fitas_piso.json"), encoding="utf-8"))
    P, G = J["planta"], J["geometria"]
    ref = next(r for r in J["resultados"] if r["id"] == "ref")
    fb = next(r for r in J["resultados"] if r["id"] == "fitas-buffer")
    svg_ref = planta(P, "Referência: Cenário Claude, checkpoint a 16 m",
                     "Corredor de unifila da porta ao checkpoint; de lá a equipe despacha à mesa e retém quem chega a fila cheia.", "checkpoint")
    svg_dec = planta(P, "Fitas por tronco, atribuição da decisão",
                     f"Cada entrada serve mesas em três paredes: {G['decisao']['cruzTroncos']} cruzamentos entre troncos de entradas diferentes.", "fitas", G["decisao"])
    svg_geo = planta(P, "Fitas por tronco, atribuição por parede",
                     f"Oeste → A, norte → B, leste → C: sem cruzamentos, mas a porta C recebe {G['geografica']['desequilibrio']:.2f}× a carga da menos carregada.", "fitas", G["geografica"], "entradaGeo")
    for nome, svg in (("fitas_piso_referencia.svg", svg_ref), ("fitas_piso_decisao.svg", svg_dec), ("fitas_piso_parede.svg", svg_geo)):
        open(os.path.join(SAIDAS, nome), "w", encoding="utf-8").write(svg)
    md = markdown(J)
    open(os.path.join(SAIDAS, "fitas_piso.md"), "w", encoding="utf-8").write(md)
    caps = [(svg_ref, f"Com checkpoint (referência): última mesa fecha {ref['fechaP50']}, espera P90 {ref['p90TotalMin']} min, {ref['dentroMax']} pessoas dentro no pico."),
            (svg_dec, f"Sem checkpoint, porta liberando enquanto cabe na zona: fecha {fb['fechaP50']}, espera P90 {fb['p90TotalMin']} min, {vg(fb['estouroFilas'])} chegadas a fila cheia. Fitas de {vg(G['decisao']['fitaTroncos_m'])} m em {sum(e['nTroncos'] for e in G['decisao']['porEntrada'])} troncos."),
            (svg_geo, f"Mesmo desenho com as mesas atribuídas por parede: {vg(G['geografica']['fitaTroncos_m'])} m de fita, zero cruzamentos, portas em {G['geografica']['desequilibrio']:.2f}× de desequilíbrio.")]
    open(os.path.join(SAIDAS, "fitas_piso.html"), "w", encoding="utf-8").write(html(J, caps, md))
    print(md)


if __name__ == "__main__":
    main()
