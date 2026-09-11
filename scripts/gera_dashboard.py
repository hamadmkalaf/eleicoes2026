"""Gera saidas/dashboard/: o plano do posto de Dublin numa pagina so.

index.html conta o plano na ordem do percurso do eleitor (quem vota, o salao,
as mesas, a fila externa, a rota e as placas, as barreiras, o dia simulado, o
caminho ate aqui, fontes) com os numeros lidos das saidas dos scripts; embute
a Prancheta, o Simulador e o Ring 3 vivo em iframes da mesma origem, para as
portas clicadas no Simulador propagarem. As pecas completas sao copiadas para
ferramentas/, pecas/ e historico/, de modo que a pasta inteira e publicavel
como um artefato multi-arquivo ou servida por qualquer servidor estatico.

Uso: python3 scripts/gera_dashboard.py   (depois dos demais geradores)
"""
import html
import json
import shutil
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
SAIDAS = BASE / "saidas"
DEST = SAIDAS / "dashboard"
sys.path.insert(0, str(BASE / "scripts"))

import decisoes as DC                                         # noqa: E402

ARTEFATOS = {
    "urnas": ("Urnas de Dublin", "https://claude.ai/code/artifact/3d1b9ff8-458d-42c9-b1b6-8aacf15dfd9f"),
    "planta": ("Planta-base do Hall 2", "https://claude.ai/code/artifact/48817634-cbe1-426e-829f-5b5c674a688c"),
    "mesas": ("Quantas mesas cabem no Hall 2", "https://claude.ai/code/artifact/8ea7b55b-ec3f-4dd4-baaf-7702c4d3fcce"),
    "prancheta": ("Prancheta do Hall 2", "https://claude.ai/code/artifact/f6a9b812-2b5e-4972-bb81-104b018e16b0"),
    "simulador": ("Simulador do Hall 2", "https://claude.ai/code/artifact/f2fea148-f618-4d3d-aa63-b0653f4139bc"),
    "rota": ("Rota do Eleitor", "https://claude.ai/code/artifact/0320fda4-365e-406e-8aa4-1d0a1b535de8"),
    "barreiras": ("Barreiras do Hall 2", "https://claude.ai/code/artifact/e2db2813-7842-4425-a028-ba64cd790981"),
    "ring3": ("Ring 3, quatro desenhos", "https://claude.ai/code/artifact/c1257b13-e450-4bc1-b801-439a32bddb87"),
    "fluxo": ("Fluxo do Posto de Dublin", "https://claude.ai/code/artifact/bdf8a5b8-2fdd-4b00-a409-9fe4af2bf3f2"),
    "paredes": ("As 28 Mesas nas Paredes", "https://claude.ai/code/artifact/1193fccf-effa-49ca-8ac5-5f4946fe4788"),
}

# origem no repositorio -> caminho dentro de saidas/dashboard/
COPIAS = {
    "ferramentas/prancheta.html": SAIDAS / "editor.html",
    "ferramentas/simulador.html": SAIDAS / "simulador_fluxo.html",
    "ferramentas/ring3.html": SAIDAS / "ring3_vivo.html",
    "pecas/urnas.html": SAIDAS / "dublin_agregacoes.html",
    "pecas/planta_base.html": SAIDAS / "planta_base.html",
    "pecas/mesas.html": SAIDAS / "mesas.html",
    "pecas/rota.html": SAIDAS / "plano_sinalizacao.html",
    "pecas/barreiras.html": SAIDAS / "barreiras_hall2.html",
    "pecas/ring3_quatro.html": SAIDAS / "ring3_horizontal.html",
}
# historico/: copias dos artefatos superados, baixadas do claude.ai em 11/09/2026;
# ficam so em saidas/dashboard/historico/ e nao sao regeradas.
LOCAL = {
    "urnas": "pecas/urnas.html", "planta": "pecas/planta_base.html", "mesas": "pecas/mesas.html",
    "prancheta": "ferramentas/prancheta.html", "simulador": "ferramentas/simulador.html",
    "rota": "pecas/rota.html", "barreiras": "pecas/barreiras.html", "ring3": "pecas/ring3_quatro.html",
    "fluxo": "historico/fluxo_ilhas_2026-08-28.html", "paredes": "historico/mesas_nas_paredes_2026-08-31.html",
    "ring3vivo": "ferramentas/ring3.html",
}

esc = html.escape


def fmt(n):
    return f"{int(round(n)):,}".replace(",", ".")


def vg(v, c=1):
    return f"{v:.{c}f}".replace(".", ",")


def pecas(*chaves):
    """Linha de links: copia embutida e URL original de cada peca."""
    itens = []
    for k in chaves:
        nome, url = ARTEFATOS[k]
        itens.append(f'<span class="peca"><a href="{LOCAL[k]}">{esc(nome)}</a>'
                     f'<a class="ext" href="{url}" target="_blank" rel="noopener">no claude.ai</a></span>')
    return '<div class="pecas"><span class="rot">Peças completas</span>' + "".join(itens) + "</div>"


def barras_mesas(dec):
    """As 28 mesas por comparecimento esperado, com a cor da classe."""
    mesas = sorted(dec["mesas"], key=lambda m: (-m["esperado"], m["mrv"]))
    maximo = mesas[0]["esperado"]
    linhas = []
    for m in mesas:
        sec = f'{m["principal"]}' + (f' + {m["agregada"]}' if m["agregada"] else "")
        origem = (m["origem_agregada"] or "").title()
        linhas.append(
            f'<div class="linha" tabindex="0" aria-label="MRV {m["mrv"]}: {m["esperado"]} esperados de {m["aptos"]} aptos">'
            f'<span class="cod">{m["mrv"]}</span>'
            f'<span class="trilho"><span class="barra c-{m["classe"]}" style="width:{m["esperado"] / maximo * 100:.1f}%"></span></span>'
            f'<span class="val">{m["esperado"]}</span>'
            f'<span class="dica">MRV {m["mrv"]} · seções {sec}{(" · " + origem) if origem else ""} · {m["aptos"]} aptos · entrada {m["entrada"]}</span>'
            f'</div>')
    return "\n".join(linhas)


def tabela_residencia(dados):
    tot = dados["total_eleitores"]
    r = dados["residencia_total"]
    linhas = []
    for local, qt in r.items():
        linhas.append(f'<tr><td>{esc(local.title())}</td><td class="num mono">{fmt(qt)}</td>'
                      f'<td class="num mono">{vg(qt / tot * 100, 1)}%</td></tr>')
    return "\n".join(linhas)


def tabela_portas(dec):
    """As 18 portas resumidas por fachada; papeis das decididas."""
    import planta_base as PB
    linhas = []
    for p in PB.numera():
        estado = p.get("estado", "livre")
        rot = {"entrada": f'entrada {dec["portas"].get(p["num"], {}).get("entrada", "")}',
               "saida": "saída de eleitores", "fechada": "fechada", "catering": "catering",
               "emergencia": "emergência", "livre": "a definir"}.get(estado, estado)
        cls = {"entrada": "t-entrada", "saida": "t-saida", "emergencia": "t-emerg", "fechada": "t-fechada"}.get(estado, "t-livre")
        linhas.append(f'<tr><td class="mono b">{p["num"]}</td><td>{esc(p["parede"])}</td>'
                      f'<td class="mono">{esc(p["codigo"])}</td><td class="num mono">{vg(p["larg"], 2)} m</td>'
                      f'<td><span class="tag {cls}">{esc(rot)}</span></td></tr>')
    return "\n".join(linhas)


def tabela_entradas(dec):
    linhas = []
    for e in dec["entradas"]:
        mrvs = ", ".join(str(n) for n in e["mrvs"])
        linhas.append(f'<tr><td><span class="sw" style="background:{e["hex"]}"></span><strong>{e["id"]}</strong> {esc(e["cor"])}</td>'
                      f'<td class="mono">{e["porta"]}</td><td class="num mono">{len(e["mrvs"])}</td>'
                      f'<td class="num mono">{fmt(e["esperado"])}</td><td class="num mono">{fmt(e["capacidade"])}</td>'
                      f'<td class="mono mesas">{mrvs}</td></tr>')
    return "\n".join(linhas)


def tabela_ring3(r3):
    """Plano vigente contra os quatro desenhos sem garganta (saidas/ring3.json)."""
    cols = [("plano_vigente_reconstruido", "Plano vigente · com garganta e baias", "1.402 no plano original (300 separadores); reconstrução dá 314"),
            ("vertical_sem_baias", "Norte-sul, sem baias", "o desenho pedido em 08/09"),
            ("vertical_com_baias", "Norte-sul, com baias", ""),
            ("girado", "Leste-oeste, sem baias", ""),
            ("girado_com_baias", "Leste-oeste, com baias", "")]
    linhas = []
    for k, nome, nota in cols:
        d = r3[k]
        linhas.append(f'<tr><td>{esc(nome)}{("<span class=sub>" + esc(nota) + "</span>") if nota else ""}</td>'
                      f'<td class="num mono">{fmt(d["capacidade"])}</td><td class="num mono">{fmt(d["capacidade_raias"])}</td>'
                      f'<td class="num mono">{fmt(d["capacidade_baias"])}</td>'
                      f'<td class="num mono">{d["separadores"]}</td><td class="num mono">{d["compra"]}</td>'
                      f'<td class="num mono">EUR {fmt(d["custo_compra_eur"])}</td></tr>')
    return "\n".join(linhas)


def indice_condados(dec):
    """Localidade de origem -> mesas e entradas (para o painel de consulta)."""
    por = {}
    for m in dec["mesas"]:
        o = m["origem_agregada"]
        if not o or o == "DUBLIN":
            continue
        por.setdefault(o, []).append(m)
    linhas = []
    for o, ms in sorted(por.items(), key=lambda kv: -sum(x["aptos_agregada"] for x in kv[1])):
        aptos = sum(x["aptos_agregada"] for x in ms)
        celas = " ".join(f'<span class="chip" style="color:{dec["portas"][x["porta"]]["cor"]}">MRV {x["mrv"]} · {x["entrada"]}</span>' for x in ms)
        linhas.append(f'<tr><td>{esc(o.title())}</td><td class="num mono">{fmt(aptos)}</td>'
                      f'<td class="mono">{", ".join(str(x["agregada"]) for x in ms)}</td><td>{celas}</td></tr>')
    return "\n".join(linhas)


def tabela_barreiras(tb):
    linhas = []
    for c in tb["cenarios"]:
        cls = ' class="marcada"' if c.get("adotado") else ""
        linhas.append(f'<tr{cls}><td><strong>{esc(c["nome"])}</strong><span class="sub">{esc(c["desc"])}</span></td>'
                      f'<td class="num mono">{c["corridas"]}</td><td class="num mono">{c["fitas"]}</td>'
                      f'<td class="num mono">{c["postes"]}</td><td class="num mono">{c["postes_reserva"]}</td>'
                      f'<td class="num mono">{vg(c["metros"], 0)} m</td></tr>')
    return "\n".join(linhas)


def folego(tb):
    """Minutos ate a fila de cada mesa transbordar, no desenho adotado."""
    fol = sorted(tb["folego"], key=lambda f: (f["minutos"] is None, f["minutos"] or 0))
    linhas = []
    for f in fol:
        if f["minutos"] is None:
            continue
        risco = f["minutos"] < 20
        w = min(f["minutos"], 40) / 40 * 100
        linhas.append(f'<div class="linha" tabindex="0" aria-label="MRV {f["n"]}: lota em {f["minutos"]} minutos">'
                      f'<span class="cod">{f["n"]}</span><span class="trilho"><span class="barra {"c-alta" if risco else "c-neutra"}" style="width:{w:.1f}%"></span></span>'
                      f'<span class="val">{f["minutos"]}</span>'
                      f'<span class="dica">MRV {f["n"]} · seção {f["mrv"]} · fila de {vg(f["fila"], 0)} m (cabem {f["cap"]}) · chegam {vg(f["chega_min"], 2)}/min · lota em {f["minutos"]} min de pico</span></div>')
    nunca = ", ".join(str(f["n"]) for f in tb["folego"] if f["minutos"] is None)
    return "\n".join(linhas), nunca


def main():
    dec = DC.montar()
    dados = json.loads((SAIDAS / "dados.json").read_text(encoding="utf-8"))
    r3 = json.loads((SAIDAS / "ring3.json").read_text(encoding="utf-8"))
    tb = json.loads((SAIDAS / "tensa_barreiras.json").read_text(encoding="utf-8"))
    mesas = json.loads((SAIDAS / "mesas.json").read_text(encoding="utf-8"))
    varr = json.loads((SAIDAS / "varredura_top.json").read_text(encoding="utf-8"))
    planta_svg = (SAIDAS / "planta_base.svg").read_text(encoding="utf-8").replace(' width="1058" height="972"', ' style="width:100%;height:auto"', 1)
    modulo_svg = (SAIDAS / "mesas_modulo.svg").read_text(encoding="utf-8")
    base = json.loads((BASE / "data" / "prancheta_hall2.json").read_text(encoding="utf-8"))
    portas_js = (BASE / "simulador" / "portas.js").read_text(encoding="utf-8")
    template = (BASE / "scripts" / "dashboard_template.html").read_text(encoding="utf-8")

    mesas_dec = dec["mesas"]
    altas = [m for m in mesas_dec if m["classe"] == "alta"]
    fora_dublin = sum(v for k, v in dados["residencia_total"].items() if k != "DUBLIN")
    contagem = dec["classes"]["contagem"]
    adotado = next(c for c in tb["cenarios"] if c.get("adotado"))
    fol_html, fol_nunca = folego(tb)
    melhor = varr[0]
    pv = r3["plano_vigente_reconstruido"]
    vs = r3["vertical_sem_baias"]
    urna_max = max(u["Total_combinado"] for u in dados["urnas"])
    urna_min = min(u["Total_combinado"] for u in dados["urnas"])

    def js(obj):
        return json.dumps(obj, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")

    subst = {
        "APTOS": fmt(dec["comparecimento"]["aptos"]),
        "ESPERADOS": fmt(dec["comparecimento"]["total"]),
        "TAXA": vg(100 * dec["comparecimento"]["total"] / dec["comparecimento"]["aptos"], 1),
        "SECOES": str(dados["total_secoes"]),
        "URNAS": str(dados["total_urnas"]),
        "URNA_MAX": fmt(urna_max), "URNA_MIN": fmt(urna_min),
        "FORA_DUBLIN": fmt(fora_dublin), "FORA_PCT": str(round(fora_dublin / dados["total_eleitores"] * 100)),
        "ALTAS": " · ".join(f'MRV {m["mrv"]} ({m["principal"]} + {m["agregada"]}, {m["esperado"]})' for m in sorted(altas, key=lambda m: -m["esperado"])),
        "N_ALTA": str(contagem["alta"]), "N_MEDIA": str(contagem["media"]), "N_BAIXA": str(contagem["baixa"]),
        "BARRAS_MESAS": barras_mesas(dec),
        "TABELA_RESIDENCIA": tabela_residencia(dados),
        "PLANTA_SVG": planta_svg,
        "MODULO_SVG": modulo_svg,
        "TABELA_PORTAS": tabela_portas(dec),
        "TABELA_ENTRADAS": tabela_entradas(dec),
        "TABELA_RING3": tabela_ring3(r3),
        "PV_CAP": fmt(pv["capacidade"]), "VS_CAP": fmt(vs["capacidade"]),
        "PV_SEP": str(dec["ring3"]["separadores"]), "VS_SEP": str(vs["separadores"]),
        "PV_COMPRA": str(dec["ring3"]["a_adquirir"]), "VS_COMPRA": str(vs["compra"]),
        "PV_EUR": fmt(dec["ring3"]["custo_eur"]), "VS_EUR": fmt(vs["custo_compra_eur"]),
        "INDICE_CONDADOS": indice_condados(dec),
        "TABELA_BARREIRAS": tabela_barreiras(tb),
        "B_POSTES": str(adotado["postes"]), "B_RESERVA": str(adotado["postes_reserva"]),
        "B_FITAS": str(adotado["fitas"]), "B_METROS": vg(adotado["metros"], 0), "B_CORRIDAS": str(adotado["corridas"]),
        "FOLEGO": fol_html, "FOLEGO_NUNCA": fol_nunca,
        "SIM_FECHA": melhor["fecha90"], "SIM_P90": str(melhor["P90min"]), "SIM_RING3": fmt(melhor["ring3p90"]),
        "SIM_ARRANJO": "Três polos (as três mesas vermelhas em áreas distintas)",
        "MODULO_FRENTE": vg(mesas["modulo"]["largura"], 2), "MODULO_PROF": vg(mesas["modulo"]["profundidade"], 2),
        "PECAS_URNAS": pecas("urnas"), "PECAS_PLANTA": pecas("planta"), "PECAS_MESAS": pecas("mesas", "prancheta"),
        "PECAS_RING3": pecas("ring3"), "PECAS_ROTA": pecas("rota"), "PECAS_BARREIRAS": pecas("barreiras"),
        "PECAS_SIM": pecas("simulador"), "PECAS_HISTORICO": pecas("fluxo", "paredes", "mesas"),
        "LINK_PRANCHETA": LOCAL["prancheta"], "LINK_SIMULADOR": LOCAL["simulador"], "LINK_RING3VIVO": LOCAL["ring3vivo"],
        "URL_PRANCHETA": ARTEFATOS["prancheta"][1], "URL_SIMULADOR": ARTEFATOS["simulador"][1],
        "BASE_JS": "const BASE = " + js({"portas": base["portas"], "salao": base["salao"]}) + ";",
        "DECISOES_JS": "const DECISOES = " + js(dec) + ";",
        "PORTAS_JS": portas_js,
    }
    pagina = template
    for k, v in subst.items():
        pagina = pagina.replace("{{" + k + "}}", v)
    import re
    faltam = sorted(set(re.findall(r"\{\{([A-Z0-9_]+)\}\}", pagina)))
    if faltam:
        raise SystemExit(f"placeholders sem valor no template: {faltam}")

    DEST.mkdir(parents=True, exist_ok=True)
    (DEST / "index.html").write_text(pagina, encoding="utf-8")
    for alvo, origem in COPIAS.items():
        if not origem.exists():
            raise SystemExit(f"falta {origem}")
        (DEST / alvo).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(origem, DEST / alvo)
    print(f"gravado {DEST.relative_to(BASE)}/index.html ({len(pagina) // 1024} KB) e {len(COPIAS)} cópias")


if __name__ == "__main__":
    main()
