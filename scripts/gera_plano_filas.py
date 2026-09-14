"""Plano de distribuicao de filas: fitas no piso, sem checkpoint (Posto, 14/09/2026).

Como a fila de cada eleitor se distribui do Ring 3 a mesa no regime decidido:
a zona do Ring 3 da sua entrada, a porta que libera enquanto cabe, a fita no
piso da sua entrada que o leva da soleira a mesa, a fila da mesa guiada por
poste (4 m no par, 10 m na vermelha) e o orientador volante como unica resposta
a uma fila cheia. Nada e digitado a mao: le
  - scripts/decisoes.py            mesas, entradas, Ring 3 decidido, numeracoes
  - scripts/decisoes_abertas.py    D2 (fitas), D4 (so_mesas), D7, D6, D1b
  - saidas/fitas_piso.json         troncos de fita e a simulacao sem checkpoint
                                   sobre o cenario de trabalho (simulador/fitas.js)
  - saidas/tensa_barreiras.json    filas de mesa e folego do tracado vigente
  - saidas/ring3.json              zonas do desenho decidido
e grava docs/plano_filas.md e saidas/plano_filas.html (com a planta dos
troncos, desenhada por scripts/fitas_piso.planta). Falha se D2 nao for fitas,
se D4 nao for o tracado sem canal ou se fitas_piso.json tiver sido gerado
sobre outro arranjo que nao o cenario de trabalho.

Uso: python3 scripts/gera_plano_filas.py   (depois de fitas.js, fitas_piso.py,
tensa_barreiras.py e decisoes_abertas.py; antes de gera_dashboard.py)
"""
import json
import math
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "scripts"))
SAIDAS = os.path.join(RAIZ, "saidas")
ARQ_MD = os.path.join(RAIZ, "docs", "plano_filas.md")
ARQ_HTML = os.path.join(SAIDAS, "plano_filas.html")
ARQ_SVG = os.path.join(SAIDAS, "plano_filas_troncos.svg")

import decisoes as DC                                          # noqa: E402
import decisoes_abertas as DA                                  # noqa: E402
import fitas_piso as FP                                        # noqa: E402
import gera_instrucoes_fluxo as GI                             # noqa: E402

JANELA_MIN = 9 * 60
FATOR_PICO = 1.8


def fmt(n):
    return f"{int(round(n)):,}".replace(",", ".")


def vg(v, c=1):
    return f"{v:.{c}f}".replace(".", ",")


def carrega(nome):
    with open(os.path.join(SAIDAS, nome), encoding="utf-8") as f:
        return json.load(f)


def pico_min(esperado):
    return esperado * FATOR_PICO / JANELA_MIN


def dados():
    dec = DC.montar()
    reg = DA.montar()
    P = DA.parametros(reg)
    fp = carrega("fitas_piso.json")
    tb = carrega("tensa_barreiras.json")
    r3 = carrega("ring3.json")
    ct = dec["cenario_trabalho"]
    if P["D2"].get("existe") is not False:
        raise SystemExit("D2 vigente nao e 'fitas no piso, sem checkpoint': este plano so vale nesse regime")
    if P["D4"].get("canal") != "nenhum":
        raise SystemExit(f"D4 vigente ({P['D4'].get('tensa')}) tem poste no canal de entrada; o plano de fitas supoe o tracado sem canal")
    if fp.get("arranjoId") != ct["id"]:
        raise SystemExit(f"fitas_piso.json foi gerado sobre {fp.get('arranjoId')!r}, nao sobre o cenario de trabalho {ct['id']!r}: rode node simulador/fitas.js 8")
    if tb["adotado"] != P["D4"]["tensa"] or tb["fonte"]["id"] != ct["id"]:
        raise SystemExit("tensa_barreiras.json nao corresponde a D4 vigente ou ao cenario de trabalho: rode tensa_barreiras.py")
    r3d = r3[dec["ring3"]["decidido"]["ring3_json"]]
    return dec, reg, P, fp, tb, r3d


def documento():
    dec, reg, P, fp, tb, r3d = dados()
    ct = dec["cenario_trabalho"]
    ent = dec["entradas"]
    n_ent = len(ent)
    mesas = {m["mrv"]: m for m in dec["mesas"]}
    el = {m["mrv"]: m["eleitor"] for m in dec["mesas"]}
    G = fp["geometria"]["decisao"]
    R = {r["id"]: r for r in fp["resultados"]}
    zonas = {z["entrada"]: z for z in r3d["zonas"]}
    tb_mesa = {m["mrv"]: m for m in tb["mesas"]}
    fol = {f["mrv"]: f for f in tb["folego"]}
    cen = next(c for c in tb["cenarios"] if c["adotado"])
    eq, total_vol = GI.equipe(dec, P, r3d, tb, n_ent)
    dec_r3 = dec["ring3"]["decidido"]
    fb = R["fitas-buffer"]
    fbf = R.get("fitas-buffer-filas")
    ref = R["ref"]
    fl = R["fitas-livre"]
    fm = R.get("fitas-mesa")

    def mesa(mrv):
        return f"{el[mrv]} (MRV {mrv})"

    def secoes(mrv):
        m = mesas[mrv]
        return str(m["principal"]) + (f" + {m['agregada']}" if m["agregada"] else "")

    L = []
    L.append("# Plano de distribuição de filas — fitas no piso, sem checkpoint\n")
    L.append(f"> Gerado por `scripts/gera_plano_filas.py` (registro de decisões de {reg['registradoEm']}; cenário de trabalho **{ct['nome']}**). "
             "Não editar à mão: quando uma decisão ou uma saída muda, o plano muda. Regime decidido pelo Posto em 14/09: "
             "**sinalização por fitas no piso, sem checkpoint** (D2 = fitas), **nenhum poste na entrada** (D4 = só as filas de mesa), "
             "Ring 3 no desenho de 13/09 (D3).\n")
    L.append(f"Vale para o 1º turno, 04/10/2026, 8h–17h, RDS Hall 2 e Ring 3; {fmt(dec['comparecimento']['total'])} eleitores esperados em "
             f"{len(dec['mesas'])} mesas; entradas {', '.join(e['porta'] + ' (' + e['id'] + ')' for e in ent)}; saídas {' e '.join(dec['saidas'])}.\n")

    L.append("## 1. O regime em uma frase\n")
    L.append("**O eleitor espera na zona do Ring 3 da sua entrada; a porta o libera enquanto houver lugar nas filas de mesa; na soleira ele lê o painel seção → mesa e segue a fita da sua entrada até a sua mesa; a fila da mesa é a única contenção, guiada por poste, e o orientador volante é a única resposta a uma fila cheia.**\n")
    L.append("- Não há ponto de controle entre a porta e a mesa: ninguém confere documento nem retém no caminho. A fita leva direto (Posto, 14/09).")
    L.append("- A porta não é livre: libera pelo ritmo da zona, com o marshal olhando as filas de mesa. É o regime que o simulador chama de \"buffer\" (seção 5); a porta livre lota o salão.")
    L.append("- Cada mesa é conhecida do eleitor pelo **número eleitor** (placa alta) e da equipe pelo **MRV**; as seções ficam no painel da soleira e na placa da mesa.\n")

    L.append("## 2. Fila externa: uma zona do Ring 3 por entrada\n")
    L.append(f"Desenho decidido: **{r3d['nome']}**, {fmt(r3d['capacidade'])} pessoas, {r3d['separadores']} separadores contados ({dec_r3['registrados']} registrados), "
             f"{vg(r3d['fita_grossa_m'], 0)} m de fita grossa. O eleitor entra no Ring 3 pelo canto nordeste, desce o corredor em L e entra na zona da sua letra.\n")
    L.append("| Zona | Porta | Cabe (decidido) | Raias | Esperados no dia | Pico (pessoas/min) | Pico simulado sem checkpoint (p50 / p90 do total) | Mesas da zona (nº eleitor · MRV · seções) |\n|---|---|---|---|---|---|---|---|")
    pz = {z["nome"].replace("Entrada ", ""): z for z in fb["porZona"]}
    for e in ent:
        z = zonas[e["id"]]
        ms = sorted(e["mrvs"], key=lambda n: el[n])
        L.append(f"| **{e['id']}** | {e['porta']} | {fmt(z['capacidade'])} | {z['raias']} × {vg(z['comprimento_raia_m'], 1)} m | {fmt(e['esperado'])} | {vg(pico_min(e['esperado']))} | "
                 f"{fmt(pz[e['id']]['ring3Max']) if e['id'] in pz else '—'} | {'; '.join(f'{el[n]} · MRV {n} · {secoes(n)}' for n in ms)} |")
    L.append("")
    L.append(f"- No pico do dia simulado sem checkpoint (porta regulando), o Ring 3 inteiro chega a **{fmt(fb['ring3Max'])}** pessoas (p50) e {fmt(fb['ring3MaxP90'])} no dia ruim (p90), "
             f"contra {fmt(r3d['capacidade'])} de lotação decidida: cabe, com folga de {fmt(r3d['capacidade'] - fb['ring3MaxP90'])} no dia ruim. Com checkpoint eram {fmt(ref['ring3Max'])}.")
    L.append("- A fita delimita, não contém: o marshal da cabeça de cada zona segura a passagem entre zonas e corrige quem errou de letra enquanto ainda cabe voltar.\n")

    L.append("## 3. Da porta à mesa: os troncos de fita\n")
    L.append(f"Uma fita por entrada, na cor da entrada e com a letra a cada poucos metros, saindo da soleira e ramificando por parede: **{G['fitaTroncos_m']:.0f} m de fita** em "
             f"{len(G['troncos'])} troncos (uma fita por mesa custaria {G['fitaPorMesa_m']:.0f} m). Os troncos de entradas diferentes se cruzam {G['cruzTroncos']} vezes e "
             f"cruzam o caminho de saída {G['cruzSaida']} vezes: a fita no piso admite cruzamento, o poste não. Caminho médio da porta à fila: "
             f"{' · '.join(e['entrada'] + ' ' + vg(e['distMedia_m'], 0) + ' m' for e in G['porEntrada'])}.\n")
    L.append("| Entrada | Parede | Mesas na ordem em que a fita as alcança (nº eleitor · MRV) | Fita do tronco |\n|---|---|---|---|")
    for e in ent:
        for t in sorted((t for t in G["troncos"] if t["entrada"] == e["id"]), key=lambda t: -len(t["mesas"])):
            L.append(f"| **{e['id']}** ({e['porta']}) | {t['parede']} | {' → '.join(f'{el[n]} · MRV {n}' for n in t['mesas'])} | {vg(t['comp'], 0)} m |")
    L.append("")
    L.append("- A fita termina na **cauda** da fila de cada mesa, não na mesa: quem chega entra no fim da fila guiada.")
    L.append("- Placa alta com o número eleitor em toda mesa: é o que confirma o destino a 20 m; a fita no piso some sob os pés quando o salão enche.")
    L.append("- A atribuição mesa → entrada é a das quotas do Ring 3 (`decisoes.py`), uma vermelha por entrada; por isso cada entrada serve as três paredes e os troncos se cruzam. A alternativa por parede (oeste A, norte B, leste C) zera os cruzamentos mas desequilibra as portas e mudaria a decisão de 06/09: fica registrada em `saidas/fitas_piso.md`.\n")

    L.append("## 4. Filas de mesa\n")
    filas = tb["premissas"]["filas_mesa_m"]
    L.append(f"Regra de 13/09, traçado **{cen['nome']}** (14/09): par de mesas = uma linha de {filas['par']:.0f} m no meio (cabem {int(filas['par'] * tb['premissas']['densidade_p_por_m'])} por fila); "
             f"mesa vermelha = {filas['polo']:.0f} m ({int(filas['polo'] * tb['premissas']['densidade_p_por_m'])}); não vermelha sem par = sem fita. "
             f"**{cen['postes']} postes** ({cen['postes_reserva']} com reserva), {cen['fitas']} fitas de 2 m, nenhum na entrada. "
             f"{len(tb['pareamento']['pares'])} pares, {len(tb['pareamento']['polos'])} polos, {len(tb['sem_guia'])} mesa(s) sem guia"
             + (": " + ", ".join(mesa(n) for n in tb["sem_guia"]) if tb["sem_guia"] else "") + ".\n")
    L.append("| Mesa (nº eleitor) | MRV | Seções | Entrada | Parede | Fila | Cabem | Lota em | Esperados |\n|---|---|---|---|---|---|---|---|---|")
    for m in sorted(dec["mesas"], key=lambda m: m["eleitor"]):
        t, f = tb_mesa[m["mrv"]], fol[m["mrv"]]
        tipo = {"par": "par", "polo": "vermelha", "solta": "sem guia"}[t["tipo"]]
        fila = f"{vg(t['fila_m'], 0)} m ({tipo})" if t["guia"] else "sem fita"
        lota = "—" if not f["guia"] else ("não lota" if f["minutos"] is None else f"{f['minutos']} min")
        L.append(f"| **{m['eleitor']}** | {m['mrv']} | {secoes(m['mrv'])} | {m['entrada']} | {m['parede']} | {fila} | {f['cap'] if f['guia'] else '—'} | {lota} | {m['esperado']} |")
    L.append("")
    curtos = sorted((f for f in tb["folego"] if f["guia"] and f["minutos"] is not None and f["minutos"] < 20), key=lambda f: f["minutos"])
    if curtos:
        L.append(f"- Lotam em menos de 20 minutos de pico: {', '.join(mesa(f['mrv']) + ' em ' + str(f['minutos']) + ' min' for f in curtos)}. São as mesas que o orientador volante vigia.")
    L.append("- Fila além do poste: o orientador volante abre uma segunda fila paralela rente à parede e avisa a coordenação; a coordenação segura a porta daquela entrada, não a mesa.\n")

    L.append("## 5. Liberação na porta: o que o simulador diz\n")
    L.append(f"Motor oficial (`simulador/modelo.js`), {fp['runs']} dias por cenário, sobre o {ct['nome']}. \"Chegadas a fila cheia\" conta eleitores que chegam à mesa com a fila no limite e ficam além do poste; \"perdidos\" os que erram o caminho.\n")
    L.append("| Cenário | Fecha (p50 / p90) | Espera P90 (fora / dentro) | Pico dentro | Pico Ring 3 (p50 / p90) | Chegadas a fila cheia | Veredito |\n|---|---|---|---|---|---|---|")
    for rid, rot in (("ref", "Referência: com checkpoint (descartado)"), ("fitas-buffer", "**Fitas, porta libera enquanto cabe (regime deste plano)**"),
                     ("fitas-buffer-filas", "Fitas, porta regulando, filas de mesa maiores (5/8/12)"), ("fitas-livre", "Fitas, porta livre"),
                     ("fitas-mesa", "Fitas, porta só libera quem tem vaga na sua mesa"), ("fitas-buffer-erro25", "Fitas, porta regulando, 25 % se perdem"),
                     ("fitas-buffer-grande", "Fitas, porta regulando, comparecimento +15 %")):
        r = R.get(rid)
        if not r:
            continue
        ver = "todos os critérios ok" if not r["ruins"] else f"**{r['nota']}**: " + "; ".join(x["titulo"] for x in r["ruins"][:3])
        L.append(f"| {rot} | {r['fechaP50']} / {r['fechaP90']} | {r['p90TotalMin']} min ({r['p90ForaMin']} / {r['p90DentroMin']}) | {fmt(r['dentroMax'])} | {fmt(r['ring3Max'])} / {fmt(r['ring3MaxP90'])} | {fmt(r['estouroFilas'])} | {ver} |")
    L.append("")
    L.append(f"- **Fechamento não muda:** a última mesa fecha às {fb['fechaP50']} com ou sem checkpoint. O checkpoint nunca custou vazão; o que ele fazia era reter por mesa.")
    L.append(f"- **O preço das fitas é a espera lá fora:** P90 de {fb['p90TotalMin']} min ({fb['p90ForaMin']} no Ring 3) contra {ref['p90TotalMin']} min com checkpoint, porque a porta só abre quando cabe. Com a porta livre a espera cai para {fl['p90TotalMin']} min, mas {fmt(fl['dentroMax'])} pessoas ficam dentro do salão e {fmt(fl['estouroFilas'])} chegam a uma fila cheia: não é opção.")
    if fbf:
        L.append(f"- Filas de mesa maiores (5/8/12 pessoas no simulador; as de 4 m e 10 m deste plano cabem 8 e 20) reduzem as chegadas a fila cheia de {fmt(fb['estouroFilas'])} para {fmt(fbf['estouroFilas'])} e a espera para {fbf['p90TotalMin']} min.")
    if fm:
        L.append(f"- Liberar só quem tem vaga na própria mesa (a porta \"conferindo\") atrasa o fechamento para {fm['fechaP50']} e empurra {fmt(fm['ring3Max'])} pessoas para o Ring 3: é o checkpoint de volta, na porta.")
    L.append("")

    L.append("## 6. Gatilhos e equipe\n")
    L.append("Quem vê, avisa a coordenação; ninguém retém por conta própria.\n")
    for e in ent:
        z = zonas[e["id"]]
        L.append(f"- Zona {e['id']} com mais de {fmt(z['capacidade'])} pessoas, ou porta {e['porta']} recebendo mais de {vg(pico_min(e['esperado']))} por minuto por mais de 10 min → abrir ritmo na porta; nunca fechar a entrada da zona.")
    L.append(f"- Fila de mesa além do poste ({filas['par']:.0f} m no par, {filas['polo']:.0f} m na vermelha) → segunda fila paralela pelo orientador volante e porta daquela entrada segurada pela coordenação.")
    L.append(f"- Mais de {fmt(fb['dentroMax'] * 1.5)} pessoas dentro do salão (1,5× o pico simulado) → porta segurada nas três entradas até as filas baixarem.")
    L.append("- Eleitor na mesa errada → o orientador o leva à certa pelo corredor mais curto; nunca de volta à porta.\n")
    L.append("| Posto | Pessoas | Tarefa | Reporta a |\n|---|---|---|---|")
    for l in eq:
        L.append(f"| {l['posto']} | {l['n'] if l['n'] else '—'} | {l['tarefa']} | {l['reporta']} |")
    L.append(f"| **Total de voluntários** | **{total_vol}** | mais {GI.SEGURANCAS} seguranças | |")
    L.append("")

    L.append("## 7. Sinalização mínima do regime (D6, plano derivado)\n")
    L.append(f"- **Painel seção → mesa na soleira** de cada entrada ({n_ent}), lido em pé em 10 s: seção, número eleitor da mesa, cor e letra da fita.")
    L.append(f"- **Fita no piso por entrada**, {G['fitaTroncos_m']:.0f} m no total, na cor da entrada e com a letra impressa a cada poucos metros ({' · '.join(e['entrada'] + ' ' + vg(e['fitaTroncos_m'], 0) + ' m' for e in G['porEntrada'])}).")
    L.append(f"- **Placa alta com o número eleitor em toda mesa** ({len(dec['mesas'])}), com as seções em corpo menor; o MRV só no verso, para a equipe.")
    L.append("- Placas P0–P2 fora e as placas de porta nas CCBs do Ring 3 (D5) seguem o plano de sinalização; o antigo painel do checkpoint (P6) sai.\n")

    L.append("## 8. O que muda neste plano se a decisão (a) mudar\n")
    d9 = next(d for d in reg["decisoes"] if d["id"] == "D9")
    L.append("A única decisão de fluxo em aberto é a identificação no caderno físico (D9). Efeitos de cada opção sobre este plano:\n")
    for o in d9["opcoes"]:
        ef = [o["efeitos"].get(k) for k in ("D2", "D7") if o["efeitos"].get(k)]
        L.append(f"- *{o['rotulo']}*: " + (" ".join(ef) if ef else "sem efeito direto."))
    return "\n".join(L) + "\n"


def main():
    dec, reg, P, fp, tb, r3d = dados()
    md = documento()
    Pp, G = fp["planta"], fp["geometria"]["decisao"]
    svg = FP.planta(Pp, f"Fitas no piso por entrada, cenário {dec['cenario_trabalho']['nome']}",
                    f"{G['fitaTroncos_m']:.0f} m de fita em {len(G['troncos'])} troncos; {G['cruzTroncos']} cruzamentos entre entradas.",
                    "fitas", G)
    os.makedirs(os.path.dirname(ARQ_MD), exist_ok=True)
    with open(ARQ_MD, "w", encoding="utf-8") as f:
        f.write(md)
    with open(ARQ_SVG, "w", encoding="utf-8") as f:
        f.write(svg)
    pagina = GI.html_pagina(md, "Plano de distribuição de filas · Posto de Dublin 2026")
    fig = f'<figure style="margin:16px 0;background:var(--card);border:1px solid var(--line);border-radius:6px;padding:8px;overflow-x:auto"><div style="min-width:720px">{svg}</div></figure>'
    pagina = pagina.replace("</h1>", "</h1>\n" + fig, 1)
    with open(ARQ_HTML, "w", encoding="utf-8") as f:
        f.write(pagina)
    print("gravado", os.path.relpath(ARQ_MD, RAIZ), os.path.relpath(ARQ_HTML, RAIZ), os.path.relpath(ARQ_SVG, RAIZ),
          f"({len(md) // 1024} KB)")


if __name__ == "__main__":
    main()
