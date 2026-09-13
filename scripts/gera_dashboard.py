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
import decisoes_abertas as DA                                 # noqa: E402

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
    "fitas": ("Fitas no piso em vez do checkpoint", "https://claude.ai/code/artifact/d36838b6-fb73-47b5-b7d1-d78b5eda8629"),
    "instrucoes": ("Instruções de fluxo (treinamento)", None),
    "decisoes": ("Decisões em aberto (registro)", None),
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
    "pecas/fitas_piso.html": SAIDAS / "fitas_piso.html",
    "pecas/instrucoes.html": SAIDAS / "instrucoes_fluxo.html",
    "pecas/decisoes.html": SAIDAS / "decisoes_em_aberto.html",
}
# historico/: copias dos artefatos superados, baixadas do claude.ai em 11/09/2026;
# ficam so em saidas/dashboard/historico/ e nao sao regeradas.
LOCAL = {
    "urnas": "pecas/urnas.html", "planta": "pecas/planta_base.html", "mesas": "pecas/mesas.html",
    "prancheta": "ferramentas/prancheta.html", "simulador": "ferramentas/simulador.html",
    "rota": "pecas/rota.html", "barreiras": "pecas/barreiras.html", "ring3": "pecas/ring3_quatro.html",
    "fluxo": "historico/fluxo_ilhas_2026-08-28.html", "paredes": "historico/mesas_nas_paredes_2026-08-31.html",
    "ring3vivo": "ferramentas/ring3.html",
    "fitas": "pecas/fitas_piso.html", "instrucoes": "pecas/instrucoes.html",
    "decisoes": "pecas/decisoes.html",
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
        ext = f'<a class="ext" href="{url}" target="_blank" rel="noopener">no claude.ai</a>' if url else ""
        itens.append(f'<span class="peca"><a href="{LOCAL[k]}">{esc(nome)}</a>{ext}</span>')
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


def tabela_ring3(r3, vig):
    """Plano vigente contra os quatro desenhos sem garganta (saidas/ring3.json)."""
    cols = [("plano_vigente_reconstruido", "Plano vigente · garganta, 3 serpenteados e 2 baias", "1.402 no plano original (300 separadores); reconstrução a 44 × 35 m dá 191 + baias"),
            ("vertical_sem_baias", "Norte-sul · corredor em L · barreira inteira", "raias de 32 m"),
            ("girado", "Leste-oeste · corredor em L · barreira inteira", "descarga da zona B no eixo de S5"),
            ("vertical_ccb_na_ponta", "Norte-sul · CCB só na ponta + fita grossa", "115 apoios de fita a cada 5 m; 154 CCB se os apoios forem CCB"),
            ("girado_ccb_na_ponta", "Leste-oeste · CCB só na ponta + fita grossa", "66 divisórias curtas")]
    linhas = []
    for k, nome, nota in cols:
        d = r3[k]
        cls = ' class="marcada"' if k == vig else ""
        fita = f'{vg(d["fita_grossa_m"], 0)} m' if d.get("fita_grossa_m") else "—"
        apoios = str(d["apoios_da_fita"]["apoios"]) if d.get("apoios_da_fita") else "—"
        linhas.append(f'<tr{cls}><td>{esc(nome)}{("<span class=sub>" + esc(nota) + "</span>") if nota else ""}</td>'
                      f'<td class="num mono">{fmt(d["capacidade"])}</td><td class="num mono">{fmt(d["capacidade_baias"])}</td>'
                      f'<td class="num mono">{d["meias_voltas"]}</td>'
                      f'<td class="num mono">{d["separadores"]}</td><td class="num mono">{d["compra"]}</td>'
                      f'<td class="num mono">EUR {fmt(d["custo_compra_eur"])}</td>'
                      f'<td class="num mono">{fita}</td><td class="num mono">{apoios}</td></tr>')
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


def tabela_barreiras(tb, sem_guia):
    """Os sete tracados: o adotado, os descartados e as hipoteses de corte."""
    linhas = []
    for c in tb["cenarios"]:
        cls = ' class="marcada"' if c.get("adotado") else ""
        sg = sem_guia.get(c["nome"], "—")
        linhas.append(f'<tr{cls}><td><strong>{esc(c["nome"])}</strong> <span class="tag t-livre">{esc(c["familia"])}</span>'
                      f'<span class="sub">{esc(c["desc"])}</span></td>'
                      f'<td class="num mono">{c["corridas"]}</td><td class="num mono">{c["fitas"]}</td>'
                      f'<td class="num mono">{c["postes"]}</td><td class="num mono">{c["postes_reserva"]}</td>'
                      f'<td class="num mono">{vg(c["metros"], 0)} m</td><td class="num mono">EUR {fmt(c["custo"]["lista_ex"])}</td>'
                      f'<td class="num mono">{sg}</td></tr>')
    return "\n".join(linhas)


def tabela_fitas(fp):
    """Resumo da varredura sem checkpoint (saidas/fitas_piso.json)."""
    ids = ["ref", "fitas-livre", "fitas-buffer", "fitas-mesa", "fitas-buffer-filas", "ref-id60", "fitas-livre-id60"]
    por = {r["id"]: r for r in fp["resultados"]}
    linhas = []
    for k in ids:
        r = por[k]
        cls = ' class="marcada"' if k == "ref" else ""
        linhas.append(f'<tr{cls}><td>{esc(r["nome"])}</td><td class="mono">{esc(r["fechaP50"])}</td>'
                      f'<td class="num mono">{r["p90TotalMin"]}</td><td class="num mono">{r["p90ForaMin"]} / {r["p90DentroMin"]}</td>'
                      f'<td class="num mono">{fmt(r["dentroMax"])}</td><td class="num mono">{fmt(r["ring3Max"])}</td>'
                      f'<td class="num mono">{fmt(r["estouroFilas"])}</td></tr>')
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


# ------------------------------------------------------ decisoes em aberto --
COR_ESTADO = {"em aberto": "var(--alerta)", "parcial": "var(--aviso)", "decidida": "var(--ok)"}


def grafo_decisoes(reg):
    """SVG do grafo de dependencia: uma coluna por camada, seta = 'condiciona'."""
    W_NO, H_NO, DX, DY, X0, Y0 = 172, 58, 236, 82, 16, 18
    camadas = reg["camadas"]
    por_id = {d["id"]: d for d in reg["decisoes"]}
    pos = {}
    alt = max(len(c) for c in camadas)
    for i, c in enumerate(camadas):
        off = (alt - len(c)) * DY / 2
        for j, k in enumerate(c):
            pos[k] = (X0 + i * DX, Y0 + off + j * DY)
    W = X0 + (len(camadas) - 1) * DX + W_NO + 16
    H = Y0 + alt * DY + 8
    o = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Grafo das decisões em aberto: cada seta liga uma decisão às que ela condiciona; as colunas são a ordem recomendada de decisão." style="max-width:100%;height:auto;display:block">',
         '<defs><marker id="dec-seta" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
         '<path d="M0,1 L9,5 L0,9 z" fill="currentColor"/></marker></defs>']
    for i, c in enumerate(camadas):
        o.append(f'<text x="{X0 + i * DX + W_NO / 2:.0f}" y="11" text-anchor="middle" font-size="10" fill="var(--meio)" font-family="IBM Plex Mono,monospace" letter-spacing=".1em">{i + 1}ª CAMADA</text>')
    for d in reg["decisoes"]:
        x0, y0 = pos[d["id"]]
        for alvo in d["condiciona"]:
            x1, y1 = pos[alvo]
            xa, ya = x0 + W_NO, y0 + H_NO / 2
            xb, yb = x1, y1 + H_NO / 2
            cx = (xa + xb) / 2
            o.append(f'<path d="M{xa:.0f},{ya:.0f} C{cx:.0f},{ya:.0f} {cx:.0f},{yb:.0f} {xb - 2:.0f},{yb:.0f}" fill="none" stroke="currentColor" stroke-opacity=".38" stroke-width="1.3" marker-end="url(#dec-seta)"/>')
    for d in reg["decisoes"]:
        x, y = pos[d["id"]]
        vig = next((op for op in d["opcoes"] if op["vigente"]), None)
        hoje = esc((vig["id"] if vig else "sem opção vigente"))
        o.append(f'<a href="#dec-{d["id"]}"><g>'
                 f'<rect x="{x}" y="{y:.0f}" width="{W_NO}" height="{H_NO}" rx="6" fill="var(--folha)" stroke="{COR_ESTADO[d["estado"]]}" stroke-width="1.6"/>'
                 f'<text x="{x + 12}" y="{y + 20:.0f}" font-size="12" font-weight="600" fill="var(--tinta)" font-family="IBM Plex Sans,sans-serif">{esc(d["id"])} · {esc(d["curto"])}</text>'
                 f'<text x="{x + 12}" y="{y + 36:.0f}" font-size="10.5" fill="var(--meio)" font-family="IBM Plex Sans,sans-serif">{esc(d["estado"])} · {len(d["opcoes"])} opções</text>'
                 f'<text x="{x + 12}" y="{y + 50:.0f}" font-size="10" fill="var(--meio)" font-family="IBM Plex Mono,monospace">hoje: {hoje}</text>'
                 f'</g></a>')
    o.append("</svg>")
    return "".join(o)


def fatos_html(reg):
    return "".join(f'<div class="resposta"><span class="num">{esc(f["id"])}</span><span class="curta">{esc(f["titulo"])}</span>'
                   f'<p>{esc(f["texto"])}</p><p class="fonte">{esc(f["fonte"])}</p></div>' for f in reg["fatos"])


def cartoes_decisoes(reg):
    por_id = {d["id"]: d for d in reg["decisoes"]}

    def chips(ids):
        return " ".join(f'<a class="chip" href="#dec-{k}">{k}</a>' for k in ids) or '<span class="chip vazio">nada</span>'

    out = []
    for d in reg["decisoes"]:
        ops = []
        for op in d["opcoes"]:
            cls = ' class="vigente"' if op["vigente"] else ""
            marca = '<span class="tag t-entrada">o que as saídas de hoje assumem</span> ' if op["vigente"] else ""
            ef = "".join(f'<li><a href="#dec-{k}">{k}</a> → {esc(v)}</li>' for k, v in op["efeitos"].items())
            ops.append(f'<li{cls}><b>{esc(op["rotulo"])}</b> {marca}<span class="res">{esc(op["resumo"])}</span>'
                       + (f'<ul class="ef">{ef}</ul>' if ef else "") + "</li>")
        adic = ""
        if d.get("adicionais"):
            adic = '<p class="mini-rot">Sinalizações adicionais a prever</p><ul class="adic">' + "".join(f"<li>{esc(a)}</li>" for a in d["adicionais"]) + "</ul>"
        out.append(
            f'<article class="cartao" id="dec-{d["id"]}">'
            f'<header><span class="id">{esc(d["id"])}</span><h3>{esc(d["titulo"])}</h3>'
            f'<span class="estado" style="color:{COR_ESTADO[d["estado"]]}">{esc(d["estado"])}</span></header>'
            f'<p class="perg">{esc(d["pergunta"])}</p>'
            f'<div class="liga"><span><i>depende de</i> {chips(d["depende_de"])}</span><span><i>condiciona</i> {chips(d["condiciona"])}</span>'
            f'<span><i>restrições</i> {" ".join(f"<span class=chip>{k}</span>" for k in d["restricoes"]) or "—"}</span></div>'
            f'<ol class="opcoes">{"".join(ops)}</ol>{adic}'
            f'<p class="fontes-dec">Fontes: {esc(" · ".join(d["fontes"]))}</p>'
            f'</article>')
    return "".join(out)


def matriz_decisoes(reg):
    alvos = [k for k in reg["ordem"] if any(k in op["efeitos"] for d in reg["decisoes"] for op in d["opcoes"])]
    cab = "".join(f'<th><a href="#dec-{k}">{k}</a></th>' for k in alvos)
    linhas = []
    for d in reg["decisoes"]:
        for op in d["opcoes"]:
            if not op["efeitos"]:
                continue
            cls = ' class="marcada"' if op["vigente"] else ""
            cel = "".join(f'<td class="ef">{esc(op["efeitos"].get(k, ""))}</td>' for k in alvos)
            linhas.append(f'<tr{cls}><td class="se"><b>{esc(d["id"])}</b> = {esc(op["rotulo"])}</td>{cel}</tr>')
    return f'<thead><tr><th>Se …</th>{cab}</tr></thead><tbody>{"".join(linhas)}</tbody>'


def main():
    dec = DC.montar()
    dados = json.loads((SAIDAS / "dados.json").read_text(encoding="utf-8"))
    r3 = json.loads((SAIDAS / "ring3.json").read_text(encoding="utf-8"))
    tb = json.loads((SAIDAS / "tensa_barreiras.json").read_text(encoding="utf-8"))
    mesas = json.loads((SAIDAS / "mesas.json").read_text(encoding="utf-8"))
    varr = json.loads((SAIDAS / "varredura_top.json").read_text(encoding="utf-8"))
    fp = json.loads((SAIDAS / "fitas_piso.json").read_text(encoding="utf-8"))
    reg = DA.montar()
    PAR = DA.parametros(reg)
    VIG = DA.vigentes(reg)
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
    vsp = r3["vertical_ccb_na_ponta"]
    r3_vig = r3[PAR["D3"]["ring3_json"]]
    sem_guia = {op["parametros"]["tensa"]: op["parametros"]["mesas_sem_guia"] for op in next(d for d in reg["decisoes"] if d["id"] == "D4")["opcoes"]}
    n_abertas = sum(1 for d in reg["decisoes"] if d["estado"] != "decidida")
    fb = next(r for r in fp["resultados"] if r["id"] == "fitas-buffer")
    fl = next(r for r in fp["resultados"] if r["id"] == "fitas-livre")
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
        "TABELA_RING3": tabela_ring3(r3, PAR["D3"]["ring3_json"]),
        "R3_VIG_NOME": esc(r3_vig["nome"]), "R3_VIG_CAP": fmt(r3_vig["capacidade"]), "R3_VIG_SEP": str(r3_vig["separadores"]),
        "VSP_SEP": str(vsp["separadores"]), "VSP_FITA": vg(vsp["fita_grossa_m"], 0), "VSP_APOIOS": str(vsp["apoios_da_fita"]["apoios"]),
        "VSP_APOIOS_CCB": str(vsp["apoios_da_fita"]["separadores_se_forem_ccb"]),
        "PV_CAP": fmt(pv["capacidade"]), "VS_CAP": fmt(vs["capacidade"]),
        "PV_SEP": str(dec["ring3"]["separadores"]), "VS_SEP": str(vs["separadores"]),
        "PV_COMPRA": str(dec["ring3"]["a_adquirir"]), "VS_COMPRA": str(vs["compra"]),
        "PV_EUR": fmt(dec["ring3"]["custo_eur"]), "VS_EUR": fmt(vs["custo_compra_eur"]),
        "INDICE_CONDADOS": indice_condados(dec),
        "TABELA_BARREIRAS": tabela_barreiras(tb, sem_guia),
        "TABELA_FITAS": tabela_fitas(fp),
        "FIT_FECHA": esc(fb["fechaP50"]), "FIT_LIVRE_DENTRO": fmt(fl["dentroMax"]), "FIT_LIVRE_CHEIA": fmt(fl["estouroFilas"]),
        "FIT_BUFFER_RING3": fmt(fb["ring3Max"]), "FIT_REF_RING3": fmt(next(r for r in fp["resultados"] if r["id"] == "ref")["ring3Max"]),
        "DEC_N": str(n_abertas), "DEC_DATA": reg["registradoEm"][8:10] + "/" + reg["registradoEm"][5:7],
        "DEC_GRAFO": grafo_decisoes(reg), "DEC_FATOS": fatos_html(reg), "DEC_CARTOES": cartoes_decisoes(reg),
        "DEC_MATRIZ": matriz_decisoes(reg),
        "DEC_ORDEM": " → ".join(" · ".join(c) for c in reg["camadas"]),
        "B_POSTES": str(adotado["postes"]), "B_RESERVA": str(adotado["postes_reserva"]),
        "B_FITAS": str(adotado["fitas"]), "B_METROS": vg(adotado["metros"], 0), "B_CORRIDAS": str(adotado["corridas"]),
        "FOLEGO": fol_html, "FOLEGO_NUNCA": fol_nunca,
        "SIM_FECHA": melhor["fecha90"], "SIM_P90": str(melhor["P90min"]), "SIM_RING3": fmt(melhor["ring3p90"]),
        "SIM_ARRANJO": "Três polos (as três mesas vermelhas em áreas distintas)",
        "MODULO_FRENTE": vg(mesas["modulo"]["largura"], 2), "MODULO_PROF": vg(mesas["modulo"]["profundidade"], 2),
        "PECAS_URNAS": pecas("urnas"), "PECAS_PLANTA": pecas("planta"), "PECAS_MESAS": pecas("mesas", "prancheta"),
        "PECAS_RING3": pecas("ring3"), "PECAS_ROTA": pecas("rota"), "PECAS_BARREIRAS": pecas("barreiras"),
        "PECAS_SIM": pecas("simulador", "fitas"), "PECAS_HISTORICO": pecas("fluxo", "paredes", "mesas"),
        "PECAS_DECISOES": pecas("instrucoes", "decisoes"),
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
