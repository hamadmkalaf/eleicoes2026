"""Monta saidas/ideia2_plano.html a partir de saidas/ideia2_dados.json e da planta.

Reaproveita a folha de estilo comum (scripts/estilo_plano.css) e a mesma
estrutura de peca de leitura da ideia 1: as duas precisam ser comparadas lado a
lado, e trocar de linguagem no meio da comparacao atrapalha.
"""
import json
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "scripts"))
import salao as FL                                       # noqa: E402
from ideia1_pagina import estilo                         # noqa: E402

CLASSE = {"leve": "leve", "media": "média", "alta": "alta", "critica": "crítica"}
PAREDE = {"norte": "norte", "oeste": "oeste", "leste": "leste"}


def mil(n) -> str:
    return f"{int(n):,}".replace(",", ".")


def vg(v, casas=1) -> str:
    return f"{v:.{casas}f}".replace(".", ",")


def tabela_viabilidade(linhas):
    ls = []
    for x in linhas:
        if x["parede_livre_m"] is None:
            marca = ' class="proj"' if "com setor" in x["cenario"] else ""
            ls.append(f'<tr{marca}><td>{x["cenario"]}</td>'
                      f'<td class="mono b">{vg(x["exigida_m"])} m exigidos</td>'
                      f'<td class="mono">—</td></tr>')
        else:
            cabe = x["posicoes"] >= 28
            marca = ' class="proj"' if cabe else ""
            ls.append(f'<tr{marca}><td>{x["cenario"]}</td>'
                      f'<td class="mono">{vg(x["parede_livre_m"])} m</td>'
                      f'<td class="mono b">{x["posicoes"]}</td></tr>')
    return "\n".join(ls)


def tabela_trechos(trechos, mrvs):
    ls = []
    for t in trechos:
        n = sum(1 for m in mrvs if m["parede"] == t["parede"]
                and t["de"] - 0.05 <= m["centro"] <= t["ate"] + 0.05)
        ls.append(f'<tr><td>{PAREDE[t["parede"]]}</td>'
                  f'<td class="mono">{vg(t["de"], 2)}</td>'
                  f'<td class="mono">{vg(t["ate"], 2)}</td>'
                  f'<td class="mono">{vg(t["comprimento"], 2)} m</td>'
                  f'<td class="mono b">{n}</td></tr>')
    return "\n".join(ls)


def barras(mrvs):
    top = sorted(mrvs, key=lambda m: -m["esperado"])
    tope = top[0]["esperado"]
    out = []
    for m in top:
        w = m["esperado"] / tope * 100
        rot = (f'{m["urna"]} · zona {m["zona"]} · parede {m["parede"]} · '
               f'{m["esperado"]} esperados · fila de pico {m["fila_pico"]}')
        out.append(
            f'<div class="linha{" destaque" if m["reforcada"] else ""}" '
            f'tabindex="0" aria-label="{rot}">'
            f'<span class="cod">{m["urna"]}</span>'
            f'<span class="trilho"><span class="barra" style="width:{w:.1f}%">'
            f'</span></span><span class="val">{m["esperado"]}</span>'
            f'<span class="dica" role="tooltip">{rot}</span></div>')
    return "\n".join(out)


def tabela(mrvs):
    ordem = {"A": 0, "setor": 1, "B": 2}
    ls = []
    for m in sorted(mrvs, key=lambda m: (ordem[m["zona"]], m["dist_entrada"])):
        sec = " + ".join(str(s) for s in m["secoes"])
        zona = "setor" if m["zona"] == "setor" else m["zona"]
        ls.append(f'''<tr>
<td class="z z{m["zona"] if m["zona"] != "setor" else "A"}">{zona}</td>
<td class="peq">{PAREDE[m["parede"]]}</td>
<td class="mono b">{m["urna"]}</td><td class="mono peq">{sec}</td>
<td class="mono">{m["aptos"]}</td>
<td class="mono peq">{m["origem_interior"] or "—"}</td>
<td class="mono b">{m["esperado"]}</td>
<td class="mono">{m["fila_pico"] or "—"}</td>
<td class="mono peq" style="white-space:nowrap">{vg(m["baia_largura"])}&#215;{vg(m["baia_profundidade"])}</td>
<td class="mono">{vg(m["dist_entrada"], 0)} m</td>
<td><span class="tag t{m["classe"]}">{CLASSE[m["classe"]]}</span></td></tr>''')
    return "\n".join(ls)


def comparacao(d2, d1):
    i2, t1 = d2["indicadores"], d1["totais"]
    mrvs1 = d1["mrvs"]
    dist1 = round(sum(m["dist_entrada"] for m in mrvs1) / len(mrvs1), 1)
    linhas = [
        ("MRVs fora das paredes", 28, 0),
        ("Balizador estimado", f'{t1["balizador_estimado_m"]} m',
         f'{i2["balizador_estimado_m"]} m'),
        ("Mesários", t1["mesarios"], i2["mesarios"]),
        ("Fila de pico somada a 55 s", t1["fila_pico_somada"],
         i2["fila_pico_somada"]),
        ("Fila de pico somada a 60 s", t1["fila_pico_somada_60s"], "—"),
        ("Caminhada média da porta ao módulo", f"{vg(dist1)} m",
         f'{vg(i2["dist_media_m"])} m'),
        ("Eleitorado da zona A", mil(t1["esperado_A"]),
         mil(i2["zonas"]["A"]["esperado"] + i2["zonas"]["setor"]["esperado"] // 2)),
        ("Eleitorado da zona B", mil(t1["esperado_B"]),
         mil(i2["zonas"]["B"]["esperado"]
             + i2["zonas"]["setor"]["esperado"] - i2["zonas"]["setor"]["esperado"] // 2)),
        ("Condições externas de que depende", 2, 3),
    ]
    return "\n".join(f'<tr><td>{r}</td><td class="mono">{a}</td>'
                     f'<td class="mono b">{b}</td></tr>' for r, a, b in linhas)


def main():
    d = json.load(open(os.path.join(RAIZ, "saidas", "ideia2_dados.json"),
                       encoding="utf-8"))
    d1 = json.load(open(os.path.join(RAIZ, "saidas", "ideia1_dados.json"),
                        encoding="utf-8"))
    svg = open(os.path.join(RAIZ, "saidas", "ideia2_planta.svg"),
               encoding="utf-8").read()
    svg = re.sub(r'\swidth="\d+"\sheight="\d+"',
                 ' style="width:100%;height:auto"', svg, count=1)

    ind = d["indicadores"]
    zonas = ind["zonas"]
    setor = zonas["setor"]["esperado"]
    total_a = zonas["A"]["esperado"] + setor // 2
    total_b = zonas["B"]["esperado"] + setor - setor // 2
    fila60 = sum(FL.simula_fila(m["esperado"], 60)[0] for m in d["mrvs"])

    viab = {x["cenario"]: x for x in d["viabilidade"]}
    def linha(chave):
        return next(v for k, v in viab.items() if chave in k)

    campos = dict(
        estilo=estilo(), svg=svg,
        m_todas=vg(linha("todas as saidas · módulo lado a lado")["parede_livre_m"]),
        p_todas_lado=linha("todas as saidas · módulo lado a lado")["posicoes"],
        p_leste_lado=linha("2.16–2.23 · módulo lado a lado")["posicoes"],
        p_leste_linha=linha("2.16–2.23 · módulo em linha")["posicoes"],
        exig_sem=vg(linha("sem setor reforçado")["exigida_m"]),
        folga=vg(ind["frente_disponivel_m"] - ind["frente_ocupada_m"]),
        frente=vg(ind["frente_ocupada_m"]),
        disponivel=vg(ind["frente_disponivel_m"]),
        fila=ind["fila_pico_somada"], fila_sem=ind["fila_pico_sem_reforco"],
        fila60=fila60,
        dist=vg(ind["dist_media_m"]),
        baliza=ind["balizador_estimado_m"],
        baliza1=d1["totais"]["balizador_estimado_m"],
        ntrechos=len(d["trechos"]),
        viab=tabela_viabilidade(d["viabilidade"]),
        trechos=tabela_trechos(d["trechos"], d["mrvs"]),
        barras=barras(d["mrvs"]), tabela=tabela(d["mrvs"]),
        comparacao=comparacao(d, d1),
        nA=zonas["A"]["mrvs"], nB=zonas["B"]["mrvs"],
        zA=mil(zonas["A"]["esperado"]), zB=mil(zonas["B"]["esperado"]),
        zSetor=mil(setor),
        pctA=round(total_a / ind["esperado"] * 100),
        pctB=round(total_b / ind["esperado"] * 100),
    )

    with open(os.path.join(RAIZ, "scripts", "ideia2_template.html"),
              encoding="utf-8") as f:
        html = f.read()
    for k, v in campos.items():
        html = html.replace("@@" + k + "@@", str(v))
    if "@@" in html:
        raise SystemExit("placeholder nao substituido: "
                         + html[html.index("@@"):html.index("@@") + 40])
    cam = os.path.join(RAIZ, "saidas", "ideia2_plano.html")
    open(cam, "w", encoding="utf-8").write(html)
    print("gravado", cam, os.path.getsize(cam), "bytes")


if __name__ == "__main__":
    main()
