"""Planta e registro dos separadores de fila do Hall 2, gerados.

Le saidas/tensa_barreiras.json (scripts/tensa_barreiras.py), a geometria da
prancheta (data/prancheta_hall2.json) e as decisoes do Posto, e grava:
  - saidas/barreiras_hall2.html  a planta em escala com um desenho por
                                 tracado (1e, 1f, 1g, 1h), as 28 mesas com o
                                 numero eleitor em destaque e o MRV ao lado,
                                 as tabelas de contagem e o grafico de folego;
  - saidas/tensa_barreiras.md    o registro da decisao em markdown.

Substitui a pagina escrita a mao de 11/09 (que so conhecia os sete tracados
antigos). Nada aqui e digitado: mudar o cenario de trabalho, a regra de mesa
ou um tracado e regenerar.

Uso: python3 scripts/gera_barreiras_hall2.py   (depois de tensa_barreiras.py)
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
import desenho as D                                            # noqa: E402
from desenho import EST, S, esc, px                            # noqa: E402

ARQ_HTML = os.path.join(SAIDAS, "barreiras_hall2.html")
ARQ_MD = os.path.join(SAIDAS, "tensa_barreiras.md")

CLASSE_COR = {"alta": D.VERM, "media": "#c9a227", "baixa": "#3a9d5d"}
COR_CANAL = "#14181e"
COR_PAR = "#1f6fb2"
COR_POLO = "#b23b2e"
VERDE_SAIDA = "#16867f"


def vg(v, c=0):
    return f"{v:,.{c}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def dir_(rot):
    r = math.radians(rot)
    return round(math.cos(r)), round(math.sin(r))


def corpo(modulo, m):
    d = dir_(m["rot"])
    p = (-d[1], d[0])
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


def planta(J, P, dec, c):
    """Um SVG por tracado: salao, portas, canal, linhas de mesa e as 28 mesas."""
    sal, mod = P["salao"], P["modulo"]
    cor_entrada = {e["id"]: e["hex"] for e in dec["entradas"]}
    porta_entrada = {e["porta"]: e for e in dec["entradas"]}
    canal = c["canal"]
    o = [poly(sal["contorno"], fill="#fbfaf7", stroke="#1f2c3c", stroke_width="2")]
    # faixa de entrada: da porta ao checkpoint (1e) ou ao topo do T
    x0, x1 = J["divisas"]["bordas"]
    o.append(D.rect(x0, 0, x1, canal["canal_m"], fill="#dfe5ec", opacity=".45"))
    o.append(D.txt((x0 + x1) / 2, canal["canal_m"] + 0.9,
                   ("checkpoint a " if canal["canal"] == "meio" else "topo do T a ") + f"{canal['canal_m']:.0f} m", "sub"))
    # portas
    for p in P["portas"]:
        if p["id"] in porta_entrada:
            cor, larg = porta_entrada[p["id"]]["hex"], 5
        elif p["id"] in dec["saidas"]:
            cor, larg = VERDE_SAIDA, 5
        else:
            cor, larg = "#9aa6b4", 3
        o.append(linha((p["x1"], p["y1"]), (p["x2"], p["y2"]), stroke=cor, stroke_width=larg, stroke_linecap="round"))
        cx, cy = (p["x1"] + p["x2"]) / 2, (p["y1"] + p["y2"]) / 2
        if p["face"] == "sul":
            rot = ("ENTRADA " + porta_entrada[p["id"]]["id"] + " · " if p["id"] in porta_entrada
                   else ("SAÍDA · " if p["id"] in dec["saidas"] else "")) + p["id"]
            o.append(D.txt(cx, cy, rot, "prt", dy=14))
        elif p["face"] == "norte":
            o.append(D.txt(cx, cy, p["id"], "sub", dy=-6))
        elif p["face"] == "leste":
            o.append(D.txt(cx, cy, p["id"], "sub", dx=14, dy=3))
        else:
            o.append(D.txt(cx, cy, p["id"], "sub", dx=-14, dy=3))
    # mesas
    ind = {m["mrv"]: m for m in J["mesas"]}
    for m in J["mesas"]:
        cor = CLASSE_COR[m["classe"]]
        o.append(poly(corpo(mod, m), fill=cor, opacity=".9", stroke="#1f2c3c", stroke_width=".6"))
        d = dir_(m["rot"])
        cx, cy = m["x"] + d[0] * mod["prof"] / 2, m["y"] + d[1] * mod["prof"] / 2
        rot = {0: 90, 180: -90, 270: 0, 90: 0}[m["rot"]]
        o.append(D.txt(cx, cy, str(m["eleitor"]), "cod", dy=4, rot=rot))
        # MRV pequeno, junto a parede
        bx, by = m["x"] + d[0] * 0.55, m["y"] + d[1] * 0.55
        o.append(D.txt(bx, by, f"MRV {m['mrv']}", "sub", dy=3, rot=rot).replace('font-size="8"', 'font-size="6.5"'))
        if not m["guia"]:
            # sem unifila: contorno tracejado a frente do modulo
            fx, fy = m["x"] + d[0] * mod["prof"], m["y"] + d[1] * mod["prof"]
            q = (-d[1], d[0])
            o.append(polyline([(fx + q[0] * 0.6, fy + q[1] * 0.6), (fx + d[0] * 3 + q[0] * 0.6, fy + d[1] * 3 + q[1] * 0.6)],
                              stroke="#5c6c80", stroke_width="1.2", stroke_dasharray="3 3"))
        # marca da entrada
        ex, ey = m["x"] + d[0] * (mod["prof"] + 0.6), m["y"] + d[1] * (mod["prof"] + 0.6)
        o.append(circulo((ex, ey), 0.42, fill=cor_entrada[m["entrada"]], stroke="#fff", stroke_width=".8"))
        o.append(D.txt(ex, ey, m["entrada"], "sub", dy=3).replace('fill="#5c6c80"', 'fill="#fff" font-weight="700"'))
    # linhas de barreira
    for l in c["linhas"]:
        if not l["pontos"]:
            continue
        if l["tipo"] in ("divisoria", "T"):
            o.append(polyline(l["pontos"], stroke=COR_CANAL, stroke_width="4", stroke_linejoin="round", stroke_linecap="round"))
            for x, y in l["pontos"]:
                o.append(circulo((x, y), 0.28, fill=COR_CANAL))
        else:
            cor = COR_POLO if l["tipo"] == "polo" else COR_PAR
            o.append(polyline(l["pontos"], stroke=cor, stroke_width="3", stroke_linecap="round"))
            for x, y in l["pontos"]:
                o.append(circulo((x, y), 0.24, fill=cor))
    # bochechas: marcas no topo do canal
    n_boch = next((i["postes"] for i in c["itens"] if i["rotulo"].startswith("bochechas")), 0)
    if n_boch:
        xs = J["divisas"]["meio"]
        if canal["canal"] == "meio":
            pontos = [x0 + 0.3, xs[0] - 0.3, xs[0] + 0.3, xs[1] - 0.3, xs[1] + 0.3, x1 - 0.3]
        else:
            pontos = [xs[0] + 0.3, xs[1] - 0.3]
        for x in pontos[:n_boch]:
            o.append(circulo((x, canal["canal_m"]), 0.28, fill=COR_CANAL, stroke="#fff", stroke_width=".8"))
    # titulo e legenda
    tit = f"Traçado {c['nome']}" + (" — adotado" if c["adotado"] else "")
    sub = f"{c['postes']} postes ({c['postes_reserva']} com reserva) · {c['fitas']} fitas · {c['corridas']} corridas · {vg(c['metros'])} m"
    o.append(D.txt(0, D.H + 2.6, tit, "tit", anchor="start"))
    o.append(D.txt(0, D.H + 1.3, sub, "sub", anchor="start"))
    y = -1.6
    itens = [(COR_CANAL, "canal de entrada (postes Tensa)"), (COR_PAR, "linha do meio do par · 4 m"),
             (COR_POLO, "polo (vermelha) · 10 m"), (CLASSE_COR["alta"], "mesa vermelha"),
             (CLASSE_COR["media"], "amarela"), (CLASSE_COR["baixa"], "verde"), (VERDE_SAIDA, "saída")]
    x = 0
    for cor, rot in itens:
        o.append(D.rect(x, y - 0.5, x + 0.9, y + 0.5, fill=cor))
        o.append(D.txt(x + 1.3, y, rot, "sub", anchor="start", dy=3))
        x += 1.3 + len(rot) * 0.36 + 1.2
    o.append(D.txt(0, y - 1.7, "Número grande: numeração eleitor. MRV: numeração oficial. Tracejado cinza à frente da mesa: sem unifila (não vermelha sem par). Círculo: entrada que serve a mesa.", "sub", anchor="start"))
    W = D.ML + D.W * S + D.MR
    Hh = D.MT + D.H * S + 70
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.0f} {Hh:.0f}" width="100%" '
            f'role="img" aria-label="{esc(tit)}">' + "".join(o) + "</svg>")


def grafico_folego(J):
    """Barras horizontais: minutos de pico que a fila de cada mesa aguenta."""
    fol = [f for f in J["folego"] if f["guia"] and f["minutos"] is not None]
    fol.sort(key=lambda f: f["minutos"])
    if not fol:
        return "", "", ""
    LW, RH, X0, TOP = 560, 16, 150, 26
    maxm = max(40, max(f["minutos"] for f in fol))
    Hh = TOP + RH * len(fol) + 24
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {X0 + LW + 60} {Hh}" width="100%" role="img" '
         'aria-label="Minutos até a fila transbordar, por mesa, com referência em 20 minutos">']
    o.append(f'<text x="{X0}" y="14" {EST["sub"]}>minutos de pico até a fila da mesa transbordar (60 s por voto, pico 1,8× a média)</text>')
    x20 = X0 + 20 / maxm * LW
    o.append(f'<line x1="{x20:.1f}" y1="{TOP - 6}" x2="{x20:.1f}" y2="{Hh - 20}" stroke="{D.VERM}" stroke-width="1" stroke-dasharray="4 3"/>')
    o.append(f'<text x="{x20 + 4:.1f}" y="{Hh - 8}" {EST["sub"]} fill="{D.VERM}">20 min</text>')
    for i, f in enumerate(fol):
        y = TOP + i * RH
        w = f["minutos"] / maxm * LW
        cor = D.VERM if f["minutos"] < 20 else "#75808e"
        o.append(f'<text x="{X0 - 8}" y="{y + 12}" {EST["lbl"]} text-anchor="end">mesa {f["eleitor"]} · MRV {f["mrv"]} · {f["tipo"]}</text>')
        o.append(f'<rect x="{X0}" y="{y + 3}" width="{w:.1f}" height="{RH - 6}" fill="{cor}"/>')
        o.append(f'<text x="{X0 + w + 5:.1f}" y="{y + 12}" {EST["sub"]}>{f["minutos"]} min · fila {vg(f["fila"])} m, cabem {f["cap"]}</text>')
    o.append("</svg>")
    nunca = ", ".join(f"{f['eleitor']} (MRV {f['mrv']})" for f in J["folego"] if f["guia"] and f["minutos"] is None)
    sem = ", ".join(f"{f['eleitor']} (MRV {f['mrv']}, {f['classe']})" for f in J["folego"] if not f["guia"])
    return "".join(o), nunca, sem


# ------------------------------------------------------------------ md ---
def tabela_conta(c):
    out = ["| Item | Corridas | Comp. | Fitas | Postes |", "|---|--:|--:|--:|--:|"]
    for i in c["itens"]:
        comp = vg(i["L"], 1) + " m" if i["L"] else "—"
        cor = str(i["corridas"]) if i["corridas"] else "—"
        out.append(f"| {i['rotulo'].replace('|', chr(92) + '|')} | {cor} | {comp} | {i['fitas']} | {i['postes']} |")
    out.append(f"| **Total** | **{c['corridas']}** | | **{c['fitas']}** | **{c['postes']}** |")
    return "\n".join(out)


def markdown(J, dec):
    ad = next(c for c in J["cenarios"] if c["adotado"])
    ind = {m["mrv"]: m for m in J["mesas"]}
    F = J["fonte"]
    filas = J["premissas"]["filas_mesa_m"]
    k = ad["custo"]
    L = []
    L.append("# Separadores Tensa para o Hall 2 — os quatro traçados de 13/09\n")
    L.append(f"> Gerado por `scripts/gera_barreiras_hall2.py` de `saidas/tensa_barreiras.json` "
             f"(`scripts/tensa_barreiras.py`, {J['geradoEm']}). Não editar à mão.\n")
    L.append(f"> **Traçado adotado: {ad['nome']}.** {ad['postes']} postes, {ad['postes_reserva']} com reserva de 10 %, "
             f"{ad['fitas']} fitas de 2 m ({vg(ad['metros'])} m de barreira), EUR {vg(k['lista_ex'], 2)} ex-VAT com entrega. "
             f"Contra os {J['premissas']['precos']['orcado_unidades']} postes já contratados: {ad['postes_reserva'] - J['premissas']['precos']['orcado_unidades']:+d}.\n")
    prov = (f" **Provisório:** o cenário `{F['pendente']}` (o \"Hamad_Final\" da prancheta) ainda não foi colado em `cenarios/`; "
            "a conta e a numeração eleitor mudam quando ele entrar." if F["provisorio"] else "")
    L.append(f"Base: cenário **`{F['cenario']}`** da Prancheta do Hall 2 (salvo em {F['criadoEm'][:10]}, sobre a planta {F['base']}), "
             f"com as 28 mesas onde ficaram, as portas S4/S5/S6 como entradas A, B e C e as saídas S2 e S8.{prov}\n")
    L.append("## A regra de mesa (Posto, 13/09/2026)\n")
    L.append(f"- **Par de mesas que se encaram:** uma única linha de **{vg(filas['par'])} m** no meio do corredor, separando as duas filas.")
    L.append(f"- **Mesa vermelha** (as três de maior comparecimento, os polos): **{vg(filas['polo'])} m** de unifila do seu lado.")
    L.append("- **Mesa não vermelha sem par: sem unifila.** Fica com a placa alta e o orientador de piso.\n")
    L.append("## Os quatro traçados do canal de entrada\n")
    L.append("| Traçado | Canal | Corridas | Fitas | Postes | Com reserva | Barreira | EUR ex-VAT | Mesas sem guia |")
    L.append("|---|---|--:|--:|--:|--:|--:|--:|--:|")
    for c in J["cenarios"]:
        cn = c["canal"]
        canal = (f"duas divisórias de {vg(cn['canal_m'])} m + 6 bochechas" if cn["canal"] == "meio"
                 else f"T: canal B de {vg(cn['canal_m'])} m, braços de {vg(cn['braco_m'])} m + 2 bochechas")
        marca = " **(adotado)**" if c["adotado"] else ""
        L.append(f"| **{c['nome']}**{marca} | {canal} | {c['corridas']} | {c['fitas']} | {c['postes']} | {c['postes_reserva']} | "
                 f"{vg(c['metros'])} m | {vg(c['custo']['lista_ex'], 2)} | {c['mesas_sem_guia']} |")
    L.append("")
    L.append("- **1e**: as duas divisórias que separam as três correntes, da porta ao checkpoint (20 m), com duas bochechas de portão por canal.")
    L.append("- **1f, 1g, 1h (\"desenho em T\")**: só o canal B fica isolado, por 15, 10 ou 5 m; no topo, um braço perpendicular para oeste guia a fila A e um para leste guia a fila C (6 m nos dois primeiros, premissa; 3 m no 1h). Cada lado do T é uma corrida contínua: o canto é um poste com duas fitas.\n")
    for c in J["cenarios"]:
        L.append(f"### Traçado {c['nome']}" + (" — **adotado**" if c["adotado"] else "") + "\n")
        L.append(c["desc"] + "\n")
        L.append(tabela_conta(c) + "\n")
    L.append("## O pareamento no cenário de trabalho\n")
    pa = J["pareamento"]
    L.append(f"{len(pa['pares'])} pares ({2 * len(pa['pares'])} mesas), {len(pa['sem_par'])} mesas sem par, {len(pa['polos'])} polos. "
             "Regra da própria prancheta: mesmo giro, mesmo recuo da parede, mesários de lados opostos; os polos saem do sorteio antes.\n")
    L.append("| Par (nº eleitor) | MRV | Corredor | Classes |\n|---|---|--:|---|")
    for p in pa["pares"]:
        a, b = ind[p["a"]], ind[p["b"]]
        L.append(f"| {a['eleitor']}–{b['eleitor']} | {p['a']}–{p['b']} | {vg(p['corredor'], 2)} m | {a['classe']}/{b['classe']} |")
    L.append("")
    L.append("- Sem par, **sem unifila**: " + ", ".join(f"mesa {ind[n]['eleitor']} (MRV {n}, {ind[n]['classe']})" for n in pa["sem_par"]) + ".")
    L.append("- Polos, 10 m: " + ", ".join(f"mesa {ind[n]['eleitor']} (MRV {n})" for n in pa["polos"]) + ".")
    for a in J["avisos"]:
        L.append(f"- **Atenção:** {a}.")
    L.append("")
    L.append("## Fôlego das filas com guia\n")
    L.append("Minutos de pico (1,8× a média, 60 s por voto) que a fila aguenta antes de transbordar; a fila de 4 m cabe 8 pessoas, a de 10 m, 20.\n")
    L.append("| Mesa (nº eleitor) | MRV | Seção | Classe | Esperados | Fila | Cabem | Chegam/min | Lota em |\n|---|---|---|---|--:|--:|--:|--:|--:|")
    for f in sorted(J["folego"], key=lambda f: (not f["guia"], f["minutos"] is None, f["minutos"] or 0)):
        lota = "sem guia" if not f["guia"] else ("não lota" if f["minutos"] is None else f"{f['minutos']} min")
        L.append(f"| {f['eleitor']} | {f['mrv']} | {f['principal']} | {f['classe']} | {f['esperado']} | "
                 f"{vg(f['fila']) + ' m' if f['guia'] else '—'} | {f['cap'] if f['guia'] else '—'} | {vg(f['chega_min'], 2)} | {lota} |")
    L.append("")
    L.append("## Como se conta um poste\n")
    L.append("O produto é o **Tensa Barrier (2 m Black Ribbon)**: um poste com fita retrátil de 2,00 m que engata no poste seguinte. "
             "Uma corrida de *L* metros gasta `⌈L/2⌉` fitas e **`⌈L/2⌉ + 1` postes** — o poste a mais é o de ponta. "
             "Corridas independentes não compartilham poste; por isso o número de corridas, e não só a metragem, manda no orçamento.\n")
    L.append("## Premissas que mexem no número\n")
    L.append(f"1. Fita de **{vg(J['premissas']['fita_m'], 2)} m** por poste. Com fita de 3,0 m a contagem cai cerca de 30 %.")
    L.append(f"2. **{vg(J['premissas']['densidade_p_por_m'], 1)} pessoas por metro** de fila (0,50 m cada); com bagagem ou carrinho cai para 1,5–1,7.")
    L.append("3. 60 s por voto e pico de 1,8× a média (8h–17h). Com caderno físico a 90 s, nenhuma fila de 4 m se sustenta na hora de pico.")
    L.append("4. Vãos de 5,93 m em S4, S5 e S6, com 0,29 m entre eles; as divisórias ficam em x "
             + " e ".join(vg(x, 2) for x in J["divisas"]["meio"]) + " m. Conferir em campo.")
    L.append(f"5. Comparecimento esperado da base B: **{vg(J['comparecimento_total'])}**. Preços: EUR {vg(J['premissas']['precos']['lista_ex'], 2)} ex-VAT por unidade, entrega EUR {vg(J['premissas']['precos']['entrega'], 2)} (M. O'Byrne Hire).")
    L.append("6. Numeração eleitor: 1 na mesa mais ao sul da parede oeste, sentido horário, 28 na mais ao sul da parede leste; MRV é a numeração oficial.\n")
    L.append("## O que mudou em 13/09\n")
    L.append("Os traçados 1, 1i (escada 10/5/3 m por fôlego) e as hipóteses A, B, B2 e C de 11/09 foram retirados: "
             "a regra passou a ser par = 4 m, vermelha = 10 m, solta não vermelha = sem unifila, e o canal de entrada ganhou as três variantes em T. "
             "As hipóteses antigas seguem em `saidas/propostas_alternativas.md`, marcadas como superadas.\n")
    return "\n".join(L) + "\n"


# ---------------------------------------------------------------- html ---
def md_para_html(md):
    out, tab = [], []

    def inline(s):
        s = H.escape(s, quote=False)
        while "**" in s:
            s = s.replace("**", "<b>", 1).replace("**", "</b>", 1)
        while "`" in s:
            s = s.replace("`", "<code>", 1).replace("`", "</code>", 1)
        s = s.replace("*L*", "<i>L</i>")
        return s

    def flush():
        nonlocal tab
        if tab:
            out.append("<div class='tw'><table>")
            for i, r in enumerate(tab):
                if set(r.replace("|", "").strip()) <= set("-: "):
                    continue
                cels = [c.strip().replace("\x00", "|") for c in r.replace("\\|", "\x00").strip().strip("|").split("|")]
                tag = "th" if i == 0 else "td"
                out.append("<tr>" + "".join(f"<{tag}>{inline(c)}</{tag}>" for c in cels) + "</tr>")
            out.append("</table></div>")
            tab = []
    lista = []
    for l in md.splitlines():
        if l.startswith("|"):
            tab.append(l); continue
        flush()
        if l.startswith("- ") or (l[:2].strip().isdigit() and ". " in l[:4]):
            lista.append(l.split(" ", 1)[1]); continue
        if lista:
            out.append("<ul>" + "".join(f"<li>{inline(i)}</li>" for i in lista) + "</ul>"); lista = []
        if l.startswith("# "):
            continue
        if l.startswith("## "):
            out.append(f"<h2>{inline(l[3:])}</h2>")
        elif l.startswith("### "):
            out.append(f"<h3>{inline(l[4:])}</h3>")
        elif l.startswith("> "):
            out.append(f"<p class='lead'>{inline(l[2:])}</p>")
        elif l.strip():
            out.append(f"<p>{inline(l)}</p>")
    flush()
    if lista:
        out.append("<ul>" + "".join(f"<li>{inline(i)}</li>" for i in lista) + "</ul>")
    return "\n".join(out)


def pagina(J, svgs, md, grafico, nunca, sem):
    ad = next(c for c in J["cenarios"] if c["adotado"])
    F = J["fonte"]
    figs = "".join(f"<figure>{svg}<figcaption>{esc(cap)}</figcaption></figure>" for svg, cap in svgs)
    prov = (f'<span class="selo">provisório · {esc(F["pendente"])} pendente</span>' if F["provisorio"] else "")
    return f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Barreiras do Hall 2</title>
<style>
:root{{--bg:#fbfaf7;--fg:#1f2c3c;--mut:#5c6c80;--line:#dfe5ec;--card:#fff;--acc:#1f6fb2;--warn:#b26a12}}
@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{--bg:#151a21;--fg:#e8ecf1;--mut:#a3aebb;--line:#2c3542;--card:#1c232c;--acc:#7fb3e6;--warn:#dda257}}}}
:root[data-theme="dark"]{{--bg:#151a21;--fg:#e8ecf1;--mut:#a3aebb;--line:#2c3542;--card:#1c232c;--acc:#7fb3e6;--warn:#dda257}}
body{{background:var(--bg);color:var(--fg);font:15px/1.5 ui-sans-serif,system-ui,'Segoe UI',Helvetica,Arial,sans-serif;margin:0;padding:24px 16px 56px}}
main{{max-width:1180px;margin:0 auto}}h1{{font-size:1.6rem;line-height:1.2;margin:.2em 0 .3em;text-wrap:balance}}
h2{{font-size:1.15rem;margin:1.8em 0 .5em;color:var(--acc)}}h3{{font-size:1rem;margin:1.2em 0 .3em}}p{{margin:.5em 0;max-width:80ch}}
.lead{{color:var(--mut);max-width:80ch;border-left:3px solid var(--warn);padding-left:12px}}
.selo{{display:inline-block;background:var(--warn);color:#fff;font-size:.72rem;font-weight:600;padding:2px 8px;border-radius:3px;margin-left:8px;vertical-align:middle}}
.faixa{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin:14px 0}}
.faixa div{{background:var(--card);border:1px solid var(--line);padding:10px 12px}}.faixa dt{{font-size:.7rem;letter-spacing:.08em;text-transform:uppercase;color:var(--mut)}}
.faixa dd{{margin:0;font-size:1.3rem;font-weight:600;font-variant-numeric:tabular-nums}}.faixa dd small{{display:block;font-size:.75rem;font-weight:400;color:var(--mut)}}
.figs{{display:grid;grid-template-columns:repeat(auto-fit,minmax(360px,1fr));gap:18px;margin:18px 0}}
figure{{margin:0;background:var(--card);border:1px solid var(--line);border-radius:6px;padding:8px}}figure svg{{width:100%;height:auto;display:block}}
figcaption{{color:var(--mut);font-size:13px;padding:8px 4px 2px;line-height:1.4}}
.grafico{{background:var(--card);border:1px solid var(--line);border-radius:6px;padding:8px;margin:12px 0}}.grafico svg{{width:100%;height:auto;display:block}}
.tw{{overflow-x:auto;margin:.6em 0}}table{{border-collapse:collapse;font-size:13px;min-width:720px;font-variant-numeric:tabular-nums}}
th,td{{border-bottom:1px solid var(--line);padding:5px 9px;text-align:left;vertical-align:top}}th{{color:var(--mut);font-weight:600;white-space:nowrap}}
ul{{padding-left:1.2em;max-width:80ch}}li{{margin:.25em 0}}
code{{font-size:.92em;background:var(--line);padding:0 4px;border-radius:3px}}
</style></head><body><main>
<h1>Barreiras do Hall 2: os quatro traçados de 13/09 {prov}</h1>
<p class="lead">Quantos separadores Tensa cada traçado consome, contados sobre o cenário <b>{esc(F["cenario"])}</b> da Prancheta, com a regra de mesa de 13/09 (par = 4 m no meio, vermelha = 10 m, não vermelha sem par = sem unifila). <b>Traçado adotado: {esc(ad["nome"])}.</b> Gerado em {J["geradoEm"]}.</p>
<dl class="faixa">
<div><dt>Postes ({esc(ad["nome"])})</dt><dd>{ad["postes"]}<small>{ad["postes_reserva"]} com reserva de 10 %</small></dd></div>
<div><dt>Fitas de 2 m</dt><dd>{ad["fitas"]}<small>{vg(ad["metros"])} m de barreira</small></dd></div>
<div><dt>Corridas</dt><dd>{ad["corridas"]}<small>{len(J["pareamento"]["pares"])} pares · {len(J["pareamento"]["polos"])} polos · canal</small></dd></div>
<div><dt>Mesas sem guia</dt><dd>{ad["mesas_sem_guia"]}<small>não vermelhas sem par</small></dd></div>
<div><dt>Já contratados</dt><dd>{J["premissas"]["precos"]["orcado_unidades"]}<small>{ad["postes_reserva"] - J["premissas"]["precos"]["orcado_unidades"]:+d} contra o adotado com reserva</small></dd></div>
</dl>
<div class="figs">{figs}</div>
<h2>Fôlego das filas com guia</h2>
<div class="grafico">{grafico}</div>
<p>Não lotam em hipótese nenhuma: {esc(nunca) or "nenhuma"}. Sem guia (fora do gráfico): {esc(sem) or "nenhuma"}.</p>
{md_para_html(md)}
</main></body></html>
"""


def main():
    with open(os.path.join(SAIDAS, "tensa_barreiras.json"), encoding="utf-8") as f:
        J = json.load(f)
    with open(DC.PRANCHETA, encoding="utf-8") as f:
        P = json.load(f)
    dec = DC.montar()
    if [c["nome"] for c in J["cenarios"]] != ["1e", "1f", "1g", "1h"]:
        raise SystemExit("tensa_barreiras.json nao tem os quatro tracados 1e/1f/1g/1h: rode tensa_barreiras.py")
    svgs = []
    for c in J["cenarios"]:
        cn = c["canal"]
        cap = (f"{c['nome']}: duas divisórias de {vg(cn['canal_m'])} m entre A|B e B|C, 6 bochechas."
               if cn["canal"] == "meio" else
               f"{c['nome']}: canal B isolado por {vg(cn['canal_m'])} m, braços de {vg(cn['braco_m'])} m para oeste (fila A) e leste (fila C), 2 bochechas.")
        cap += f" {c['postes']} postes, {c['fitas']} fitas, {vg(c['metros'])} m; {c['mesas_sem_guia']} mesas sem guia."
        svgs.append((planta(J, P, dec, c), cap))
    md = markdown(J, dec)
    grafico, nunca, sem = grafico_folego(J)
    with open(ARQ_MD, "w", encoding="utf-8") as f:
        f.write(md)
    with open(ARQ_HTML, "w", encoding="utf-8") as f:
        f.write(pagina(J, svgs, md, grafico, nunca, sem))
    print("gravado", os.path.relpath(ARQ_MD, RAIZ), "e", os.path.relpath(ARQ_HTML, RAIZ),
          f"({os.path.getsize(ARQ_HTML) // 1024} KB)")


if __name__ == "__main__":
    main()
