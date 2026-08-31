"""Monta saidas/ideia1_plano.html a partir de saidas/ideia1_dados.json e da planta."""
import json, os, re, sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "scripts"))
import salao as FL

CLASSE = {"leve": "leve", "media": "média", "alta": "alta", "critica": "crítica"}
FILEIRA = {"F1c": "1 · reforçado", "F1A": "1", "F1B": "1",
           "F2A": "2", "F2B": "2", "F3A": "3", "F3B": "3"}


def sensibilidade(urnas):
    linhas = []
    for t in (45, 50, 55, 60, 70, 90):
        picos = [FL.simula_fila(u["esperado"], t) for u in urnas]
        fim = max(p[2] for p in picos)
        linhas.append(dict(t=t, soma=sum(p[0] for p in picos),
                           maior=max(p[0] for p in picos),
                           n10=sum(1 for p in picos if p[0] > 10),
                           fim=f"{int(fim)}h{int(round((fim % 1) * 60)):02d}"))
    return linhas


def barras(mrvs):
    top = sorted(mrvs, key=lambda m: -m["esperado"])
    tope = top[0]["esperado"]
    out = []
    for m in top:
        w = m["esperado"] / tope * 100
        crit = m["classe"] == "critica"
        rot = (f'{m["urna"]} · {m["aptos"]} aptos · {m["esperado"]} esperados · '
               f'fila de pico {m["fila_pico"]}')
        out.append(
            f'<div class="linha{" destaque" if crit else ""}" tabindex="0" '
            f'aria-label="{rot}"><span class="cod">{m["urna"]}</span>'
            f'<span class="trilho"><span class="barra" style="width:{w:.1f}%">'
            f'</span></span><span class="val">{m["esperado"]}</span>'
            f'<span class="dica" role="tooltip">{rot}</span></div>')
    return "\n".join(out)


def tabela(mrvs):
    ls = []
    for m in sorted(mrvs, key=lambda m: (m["zona"], m["dist_entrada"])):
        sec = " + ".join(str(s) for s in m["secoes"])
        orig = m["origem_interior"] or "—"
        ls.append(f'''<tr>
<td class="z z{m["zona"]}">{m["zona"]}</td><td class="mono peq">{FILEIRA[m["fileira"]]}</td>
<td class="mono b">{m["urna"]}</td><td class="mono peq">{sec}</td>
<td class="mono">{m["aptos"]}</td><td class="mono">{orig}</td>
<td class="mono b">{m["esperado"]}</td><td class="mono">{m["fila_pico"] or "—"}</td>
<td class="mono peq">{m["baia_largura"]:.1f} × {m["baia_profundidade"]:.1f}</td>
<td class="mono">{m["mesarios"]}</td>
<td><span class="tag t{m["classe"]}">{CLASSE[m["classe"]]}</span></td></tr>''')
    return "\n".join(ls)


def main():
    d = json.load(open(os.path.join(RAIZ, "saidas", "ideia1_dados.json"), encoding="utf-8"))
    svg = open(os.path.join(RAIZ, "saidas", "ideia1_planta.svg"), encoding="utf-8").read()
    svg = re.sub(r'\swidth="\d+"\sheight="\d+"', ' style="width:100%;height:auto"', svg, count=1)
    urnas = FL.carrega_urnas()
    for u in urnas:
        u["fila_pico"] = FL.simula_fila(u["esperado"])[0]
    sens = sensibilidade(urnas)
    t = d["totais"]
    m = d["mrvs"]
    n = {c: sum(1 for x in m if x["classe"] == c) for c in CLASSE}
    interior = sum(x["aptos_interior"] for x in m)

    sens_html = "\n".join(
        f'<tr{" class=proj" if s["t"] == 55 else ""}><td class="mono b">{s["t"]} s</td>'
        f'<td class="mono">{s["soma"]:,}</td><td class="mono">{s["maior"]}</td>'
        f'<td class="mono">{s["n10"]}</td><td class="mono">{s["fim"]}</td></tr>'
        .replace(",", ".") for s in sens)

    campos = dict(
        svg=svg, barras=barras(m), tabela=tabela(m), sens=sens_html,
        esperado=f'{t["esperado"]:,}'.replace(",", "."),
        aptos=f'{t["aptos"]:,}'.replace(",", "."),
        interior=f'{interior:,}'.replace(",", "."),
        zA=f'{t["esperado_A"]:,}'.replace(",", "."),
        zB=f'{t["esperado_B"]:,}'.replace(",", "."),
        pctA=round(t["esperado_A"] / t["esperado"] * 100),
        pctB=round(t["esperado_B"] / t["esperado"] * 100),
        f55=t["fila_pico_somada"], f60=t["fila_pico_somada_60s"],
        f45=t["fila_pico_somada_45s"],
        f90=f'{t["fila_pico_somada_90s"]:,}'.replace(",", "."),
        reserva=t["fila_pico_somada_60s"] - t["fila_pico_somada"],
        baliza=t["balizador_estimado_m"], mesarios=t["mesarios"],
        nleve=n["leve"], nmedia=n["media"], nalta=n["alta"], ncrit=n["critica"],
        pico_min=round(t["esperado"] * 0.15 / 60),
        pico_zona=str(round(t["esperado"] * 0.15 / 60 / 2, 1)).replace(".", ","),
    )
    html = PAGINA
    for k, v in campos.items():
        html = html.replace("@@" + k + "@@", str(v))
    assert "@@" not in html, "placeholder nao substituido: " + \
        html[html.index("@@"):html.index("@@") + 40]
    cam = os.path.join(RAIZ, "saidas", "ideia1_plano.html")
    open(cam, "w", encoding="utf-8").write(html)
    print("gravado", cam, os.path.getsize(cam), "bytes")


PAGINA = open(os.path.join(RAIZ, "scripts", "ideia1_template.html"),
              encoding="utf-8").read() if os.path.exists(
    os.path.join(RAIZ, "scripts", "ideia1_template.html")) else ""

if __name__ == "__main__":
    main()
