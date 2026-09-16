"""Confere a prancheta do Hall 2 contra as tres fontes oficiais do Cartorio.

Duas perguntas, nesta ordem:

  1. Os numeros que alimentam a prancheta estao certos? Refaz, do zero e a
     partir dos PDFs de `data/oficiais/`, o aptos de cada seccao, os 28 pares
     principal -> agregada, o aptos de cada mesa e o comparecimento esperado
     de cada mesa, e compara com `data/decisoes.json` e `saidas/dados.json`.

  2. O cenario de trabalho reparte o comparecimento esperado por igual entre
     as tres paredes? Soma o esperado por parede, mede a amplitude e testa a
     robustez do equilibrio trocando a base de comparecimento.

Sai com codigo 1 se qualquer numero divergir. Observacoes (lacunas de mesario,
por exemplo) nao derrubam a conferencia -- so as divergencias derrubam.

    python3 scripts/confere_prancheta.py [cenario]

`cenario` e o id de um arquivo de `cenarios/` (sem o `.json`); o padrao e o
cenario de trabalho declarado em `data/decisoes.json`.
"""
import json
import os
import statistics as st
import sys

import fontes_oficiais as fontes

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Giro do modulo -> parede em que ele encosta (prancheta: x para leste, y para
# norte, ancoragem no ponto de encosto). Nenhum cenario usa rot 90 (fachada
# sul), que e onde ficam as portas.
PAREDE_POR_ROT = {0: "oeste", 270: "norte", 180: "leste"}

# Comprimento util de cada parede, em metros, do contorno do salao: o recorte
# a sudoeste come 7,0 m da parede oeste. Serve a densidade linear, nao ao
# equilibrio em si.
COMPRIMENTO = {"oeste": 44.4 - 7.0, "norte": 50.3, "leste": 44.4}


def carrega(*caminho):
    with open(os.path.join(RAIZ, *caminho), encoding="utf-8") as f:
        return json.load(f)


class Conferencia:
    """Acumula divergencias (derrubam) e observacoes (so informam)."""

    def __init__(self):
        self.divergencias = []
        self.observacoes = []

    def diverge(self, onde, msg):
        self.divergencias.append(f"{onde}: {msg}")

    def observa(self, onde, msg):
        self.observacoes.append(f"{onde}: {msg}")


def titulo(texto, n=None):
    rotulo = f"{n}. {texto}" if n else texto
    print(f"\n{'=' * 78}\n{rotulo}\n{'=' * 78}")


def confere_aptos(c, oficial, dados):
    """PDF de 13/07 x as 51 seccoes de saidas/dados.json (CSV de 13/08)."""
    repo = {s["Secao"]: s for s in dados["secoes"]}
    print(f"  seções: {len(oficial)} no PDF · {len(repo)} no repositório")
    print(f"  aptos:  {sum(v[0] for v in oficial.values())} no PDF · "
          f"{sum(s['Eleitores'] for s in repo.values())} no repositório")
    for secao, (n, localidade) in sorted(oficial.items()):
        s = repo.get(secao)
        if s is None:
            c.diverge("aptos", f"seção {secao:04d} ({n} aptos) não existe no repositório")
            continue
        if s["Eleitores"] != n:
            c.diverge("aptos", f"seção {secao:04d}: PDF {n} × repositório {s['Eleitores']}")
        if s["Residencia_predominante"] != localidade:
            c.diverge("localidade", f"seção {secao:04d}: PDF '{localidade}' × "
                                    f"repositório '{s['Residencia_predominante']}'")
    for secao in repo:
        if secao not in oficial:
            c.diverge("aptos", f"seção {secao:04d} do repositório não consta do PDF")
    if not c.divergencias:
        print("  as 51 seções batem, uma a uma, em aptos e em localidade de origem")


def confere_agregacoes(c, pares, mesas, oficial):
    """PDF de agregacoes x as 28 mesas, e cobertura das 51 seccoes."""
    do_pdf, da_prancheta = dict(pares), {m["principal"]: m.get("agregada") for m in mesas}
    print(f"  pares: {len(pares)} no PDF · {len(mesas)} mesas na prancheta")
    for principal, agregada in sorted(do_pdf.items()):
        if principal not in da_prancheta:
            c.diverge("agregação", f"principal {principal:04d} do PDF não é mesa na prancheta")
        elif da_prancheta[principal] != agregada:
            c.diverge("agregação", f"principal {principal:04d}: PDF agrega "
                                   f"{agregada} × prancheta agrega {da_prancheta[principal]}")
    for principal in da_prancheta:
        if principal not in do_pdf:
            c.diverge("agregação", f"mesa {principal:04d} da prancheta não consta do PDF")
    cobertas = [s for par in pares for s in par if s]
    print(f"  seções cobertas: {len(cobertas)} · distintas: {len(set(cobertas))}")
    faltando = sorted(set(oficial) - set(cobertas))
    if faltando:
        c.diverge("agregação", f"seções sem mesa: {faltando}")
    if len(cobertas) != len(set(cobertas)):
        c.diverge("agregação", "há seção repetida em mais de uma mesa")
    if not faltando and len(set(cobertas)) == len(oficial):
        print("  toda seção aparece em exatamente uma mesa; nenhuma sobra, nenhuma falta")


def confere_mesas(c, mesas, oficial, taxas):
    """Refaz aptos e esperado de cada mesa a partir do PDF e compara."""
    print(f"  {'MRV':>3} {'principal':>9} {'agregada':>8} {'origem da agregada':<26}"
          f" {'aptos':>6} {'esperado':>8} {'exato':>8}")
    soma_aptos = soma_esperado = 0
    soma_exata = 0.0
    for m in mesas:
        partes = [m["principal"]] + ([m["agregada"]] if m.get("agregada") else [])
        aptos = sum(oficial[s][0] for s in partes)
        exato = sum(oficial[s][0] * taxas[oficial[s][1]] for s in partes)
        esperado = round(exato)
        origem = oficial[m["agregada"]][1] if m.get("agregada") else None
        soma_aptos += aptos
        soma_esperado += esperado
        soma_exata += exato
        marca = ""
        if aptos != m["aptos"]:
            c.diverge("mesa", f"MRV {m['mrv']}: aptos recalculados {aptos} × "
                              f"prancheta {m['aptos']}")
            marca += "  << APTOS"
        if esperado != m["esperado"]:
            c.diverge("mesa", f"MRV {m['mrv']}: esperado recalculado {esperado} × "
                              f"prancheta {m['esperado']}")
            marca += "  << ESPERADO"
        if origem != m.get("origem_agregada"):
            c.diverge("mesa", f"MRV {m['mrv']}: origem da agregada PDF '{origem}' × "
                              f"prancheta '{m.get('origem_agregada')}'")
            marca += "  << ORIGEM"
        print(f"  {m['mrv']:>3} {m['principal']:>9} "
              f"{m['agregada'] if m.get('agregada') else '—':>8} {str(origem or '—'):<26}"
              f" {aptos:>6} {esperado:>8} {exato:>8.1f}{marca}")
    print(f"  {'TOTAL':>3} {'':>9} {'':>8} {'':<26} {soma_aptos:>6} {soma_esperado:>8}"
          f" {soma_exata:>8.1f}")
    if soma_aptos != sum(m["aptos"] for m in mesas):
        c.diverge("mesa", "a soma de aptos das 28 mesas não fecha")
    if soma_esperado != sum(m["esperado"] for m in mesas):
        c.diverge("mesa", "a soma do esperado das 28 mesas não fecha")


def confere_mesarios(c, por_secao, resumo, mesas):
    """Cobertura das 28 mesas pelo relatorio Convoca+ e lacunas de composicao."""
    print(f"  relatório: {resumo.get('nomeados')} nomeados · "
          f"{resumo.get('confirmados')} confirmados · "
          f"{resumo.get('sem_resposta')} sem resposta · "
          f"{resumo.get('dispensa')} pedido de dispensa")
    principais = {m["principal"] for m in mesas}
    if set(por_secao) != principais:
        c.diverge("mesários", f"só nas mesas: {sorted(principais - set(por_secao))}; "
                              f"só no relatório: {sorted(set(por_secao) - principais)}")
    else:
        print(f"  o relatório cobre exatamente as {len(principais)} seções principais "
              f"(uma mesa por MRV, não uma por seção)")
    nomeados = sum(len(v) for v in por_secao.values())
    if resumo.get("nomeados") not in (None, nomeados):
        c.diverge("mesários", f"{nomeados} linhas lidas × {resumo['nomeados']} declarados")
    for secao in sorted(por_secao):
        faltam = fontes.FUNCOES_MINIMAS - {f for f, _, _ in por_secao[secao]}
        if faltam:
            c.observa("mesários", f"seção {secao:04d} tem {len(por_secao[secao])} de 4 "
                                  f"nomeados: falta {', '.join(sorted(faltam))}")
    for secao in sorted(por_secao):
        pendentes = [f for f, _, s in por_secao[secao] if s and s != "Confirmado"]
        if len(pendentes) >= 3:
            c.observa("mesários", f"seção {secao:04d}: {len(pendentes)} de "
                                  f"{len(por_secao[secao])} sem confirmar "
                                  f"({', '.join(pendentes)})")


def paredes_do_cenario(cenario):
    """{mrv: parede} a partir do giro de cada modulo no cenario."""
    return {a["n"]: PAREDE_POR_ROT[a["rot"]] for a in cenario["alteracoes"]}


def confere_equidade(c, mesas, parede_de, nome):
    """Soma o esperado por parede e mede a amplitude contra o terco perfeito."""
    por_parede, mesas_por_parede = {}, {}
    for m in mesas:
        p = parede_de[m["mrv"]]
        por_parede[p] = por_parede.get(p, 0) + m["esperado"]
        mesas_por_parede.setdefault(p, []).append(m["esperado"])
    total = sum(por_parede.values())
    alvo = total / len(por_parede)
    print(f"  cenário {nome} · {total} esperados · terço perfeito = {alvo:.0f}")
    print(f"  {'parede':<8} {'mesas':>5} {'esperado':>9} {'desvio':>7} {'%':>8}"
          f" {'metros':>7} {'por m':>7} {'maior mesa':>11}")
    for p in sorted(por_parede, key=lambda k: -por_parede[k]):
        v, ms = por_parede[p], mesas_por_parede[p]
        print(f"  {p:<8} {len(ms):>5} {v:>9} {v - alvo:>+7.0f} {100 * (v / alvo - 1):>+7.2f}%"
              f" {COMPRIMENTO[p]:>7.1f} {v / COMPRIMENTO[p]:>7.1f} {max(ms):>11}")
    valores = list(por_parede.values())
    amplitude = max(valores) - min(valores)
    cv = st.pstdev(valores) / st.mean(valores) * 100
    print(f"  amplitude {amplitude} eleitores ({100 * amplitude / alvo:.2f}% do alvo) · CV {cv:.2f}%")
    if amplitude > 0.01 * alvo:
        c.observa("equidade", f"amplitude entre paredes de {amplitude} eleitores "
                              f"({100 * amplitude / alvo:.1f}% do alvo) — acima de 1%")
    # Decisão de 15/09: cada entrada serve uma parede inteira e só ela.
    por_entrada = {}
    for m in mesas:
        por_entrada.setdefault(m["entrada"], set()).add(parede_de[m["mrv"]])
    bagunca = {e: sorted(ps) for e, ps in por_entrada.items() if len(ps) != 1}
    if bagunca:
        c.diverge("entradas", "entrada servindo mais de uma parede: "
                              + "; ".join(f"{e} → {', '.join(ps)}" for e, ps in bagunca.items()))
    elif len({next(iter(ps)) for ps in por_entrada.values()}) != len(por_entrada):
        c.diverge("entradas", "duas entradas caem na mesma parede")
    else:
        print("  uma entrada por parede: "
              + " · ".join(f"{e} → {next(iter(por_entrada[e]))}" for e in sorted(por_entrada)))

    altas = sorted(mesas, key=lambda m: -m["esperado"])[:3]
    onde = {parede_de[m["mrv"]] for m in altas}
    print("  as três mesas de maior carga: "
          + " · ".join(f"MRV {m['mrv']} ({m['esperado']}) na {parede_de[m['mrv']]}" for m in altas))
    if len(onde) != len(por_parede):
        c.observa("equidade", f"as três mesas de maior carga ocupam {len(onde)} paredes, "
                              f"não {len(por_parede)}")
    return por_parede


def confere_sensibilidade(mesas, oficial, parede_de, taxas):
    """O equilibrio por parede sob outras bases de comparecimento.

    A base B foi escolhida em 06/09 e a composicao das paredes foi otimizada
    contra ela. Este bloco mede quanto do equilibrio e propriedade do arranjo
    e quanto e ajuste fino a essa base.
    """
    total_aptos = sum(v[0] for v in oficial.values())
    bases = [
        ("B — taxa de 2022 por condado (a que a prancheta usa)",
         lambda loc: taxas[loc]),
        ("A — binária: 74% Dublin, 50% interior",
         lambda loc: 0.74 if loc == "DUBLIN" else 0.50),
        ("uniforme de 68,5% (mesmo total da base B, sem contraste entre condados)",
         lambda loc: 11499 / total_aptos),
        ("nota verbal: uniforme de 71,5% (≈12.000)",
         lambda loc: 12000 / total_aptos),
        ("Dublin 80%, interior 45%",
         lambda loc: 0.80 if loc == "DUBLIN" else 0.45),
        ("Dublin 70%, interior 60%",
         lambda loc: 0.70 if loc == "DUBLIN" else 0.60),
    ]
    print(f"  {'base de comparecimento':<62} {'total':>6} {'ampl.':>6} {'% do alvo':>10}")
    for nome, taxa in bases:
        por_parede = {}
        for m in mesas:
            partes = [m["principal"]] + ([m["agregada"]] if m.get("agregada") else [])
            v = sum(oficial[s][0] * taxa(oficial[s][1]) for s in partes)
            por_parede[parede_de[m["mrv"]]] = por_parede.get(parede_de[m["mrv"]], 0) + v
        total = sum(por_parede.values())
        amplitude = max(por_parede.values()) - min(por_parede.values())
        print(f"  {nome:<62} {total:>6.0f} {amplitude:>6.0f} {300 * amplitude / total:>9.2f}%")

    print("\n  exposição de cada parede a taxa de qualidade fraca (proxy ou genérica):")
    exposicao = {}
    for m in mesas:
        for s in [m["principal"]] + ([m["agregada"]] if m.get("agregada") else []):
            aptos, loc = oficial[s]
            forte = QUALIDADE[loc] == "direto"
            d, f = exposicao.get(parede_de[m["mrv"]], (0.0, 0.0))
            exposicao[parede_de[m["mrv"]]] = (d + aptos * taxas[loc] * forte,
                                              f + aptos * taxas[loc] * (not forte))
    print(f"  {'parede':<8} {'esperado':>9} {'de taxa fraca':>14} {'%':>7} {'se errar 20%':>14}")
    for p in sorted(exposicao, key=lambda k: -exposicao[k][1]):
        d, f = exposicao[p]
        print(f"  {p:<8} {d + f:>9.0f} {f:>14.0f} {100 * f / (d + f):>6.1f}% {0.2 * f:>+13.0f}")


QUALIDADE = {}


def main(argv):
    c = Conferencia()
    decisoes = carrega("data", "decisoes.json")
    dados = carrega("saidas", "dados.json")
    mesas = decisoes["mesas"]
    taxas = {k: v["taxa"] for k, v in decisoes["comparecimento"]["taxas"].items()}
    QUALIDADE.update({k: v["qualidade"] for k, v in decisoes["comparecimento"]["taxas"].items()})

    id_cenario = argv[1] if len(argv) > 1 else decisoes["cenario_trabalho"]["id"]
    cenario = carrega("cenarios", id_cenario + ".json")

    oficial, totais_local, total_declarado = fontes.aptos_por_secao()
    pares, _ = fontes.agregacoes()
    por_secao, resumo = fontes.mesarios()

    print(f"Conferência da prancheta do Hall 2 · cenário {cenario['nome']} "
          f"({id_cenario})\nFontes: os três PDFs oficiais em data/oficiais/")

    titulo("APTOS POR SEÇÃO — PDF de 13/07/2026 × repositório", 1)
    confere_aptos(c, oficial, dados)
    if sum(v[0] for v in oficial.values()) != total_declarado:
        c.diverge("aptos", "a soma das seções não bate com o total declarado no PDF")
    if sum(totais_local.values()) != total_declarado:
        c.diverge("aptos", "a soma dos totais por localidade não bate com o total do PDF")

    titulo("AGREGAÇÕES — PDF do Cartório × as 28 mesas da prancheta", 2)
    confere_agregacoes(c, pares, mesas, oficial)

    titulo("APTOS E COMPARECIMENTO ESPERADO POR MESA — recálculo do zero", 3)
    confere_mesas(c, mesas, oficial, taxas)

    titulo("MESÁRIOS — relatório Convoca+ de 13/09/2026", 4)
    confere_mesarios(c, por_secao, resumo, mesas)

    titulo("EQUIDADE POR PAREDE — o que o cenário reparte", 5)
    parede_de = paredes_do_cenario(cenario)
    faltam = {m["mrv"] for m in mesas} - set(parede_de)
    if faltam:
        c.diverge("cenário", f"o cenário não posiciona as mesas {sorted(faltam)}; "
                             f"a conferência por parede precisa das 28")
    else:
        confere_equidade(c, mesas, parede_de, cenario["nome"])

        titulo("ROBUSTEZ — o equilíbrio sob outras bases de comparecimento", 6)
        confere_sensibilidade(mesas, oficial, parede_de, taxas)

    titulo("RESULTADO")
    if c.divergencias:
        print(f"  {len(c.divergencias)} divergência(s):")
        for d in c.divergencias:
            print("   ·", d)
    else:
        print("  Nenhuma divergência: a prancheta reproduz as três fontes oficiais.")
    if c.observacoes:
        print(f"  {len(c.observacoes)} observação(ões) — não derrubam a conferência:")
        for o in c.observacoes:
            print("   ·", o)
    return 1 if c.divergencias else 0


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    sys.exit(main(sys.argv))
