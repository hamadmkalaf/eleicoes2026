"""Reparte as 28 mesas entre as tres paredes, uma entrada por parede.

Regra do Posto (15/09/2026): quem entra pela porta A vota na parede oeste,
pela B na norte, pela C na leste. Cada entrada passa a ter uma parede inteira
e so ela, entao **equilibrar as entradas e equilibrar as paredes viraram o
mesmo problema**, e a fila de cada entrada e a fila daquela parede.

Este modulo refaz a reparticao do zero:

  1. mede quantas mesas cabem em cada parede, trecho a trecho, com as duplas
     e os corredores que a planta oficial usa;
  2. varre todas as reparticoes (n_oeste, n_norte, n_leste) que cabem;
  3. para cada uma, procura a atribuicao de mesa -> parede que deixa o
     comparecimento esperado mais parecido entre as tres;
  4. desempata pela densidade -- esperados por metro util de parede --, que e
     o que decide a profundidade da fila agora que cada parede tem a sua;
  5. monta as posicoes: as tres mesas de maior carga isoladas, uma por parede,
     e as demais em duplas.

Nao mexe na agregacao de secoes. O par principal -> agregada de cada urna e do
Cartorio Eleitoral (data/oficiais/secoes_agregadas_dublin_2026.pdf, conferido
em 15/09) e os mesarios ja estao nomeados por MRV; o que se reparte aqui e a
mesa inteira, com as suas duas secoes juntas.

Geometria e convencoes vindas de simulador/equitativo.js, que por sua vez as
leu da planta oficial A:
  dupla   = dois modulos a 3,90 m, o primeiro com lado +1 e o segundo com -1,
            para os mesarios ficarem de frente um para o outro;
  unidade = dupla ou mesa isolada; 2,40 m de eixo a eixo entre unidades, que
            sao 1,50 m livres de corpo a corpo.

    python3 scripts/arranjo_paredes.py            # relatorio, sem gravar
    python3 scripts/arranjo_paredes.py --grava    # grava o cenario e decisoes
"""
import itertools
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PASSO_DUPLA = 3.90      # entre as duas mesas de uma dupla
PASSO_UNID = 2.40       # entre unidades (1,50 m livres de corpo a corpo)

# Trechos livres do eixo de cada parede, no ponto de encosto do modulo. Ja
# descontam meia largura do corpo, os vaos de porta, a faixa protegida da
# fachada leste e os dois cantos onde a fila de uma parede cortaria o corpo da
# outra. Transcritos de simulador/equitativo.js.
PAREDES = {
    "oeste": {"rot": 0,   "eixo": "y", "fixo": 0.0,  "sentido": +1,
              "trechos": [(7.45, 18.81), (22.98, 36.25), (39.05, 43.95)]},
    "norte": {"rot": 270, "eixo": "x", "fixo": 44.4, "sentido": +1,
              "trechos": [(10.20, 20.21), (24.67, 42.30)]},
    "leste": {"rot": 180, "eixo": "y", "fixo": 47.3, "sentido": -1,
              "trechos": [(3.20, 39.50)]},
}
ORDEM = ("oeste", "norte", "leste")
ENTRADA = {"oeste": "A", "norte": "B", "leste": "C"}   # a decisao de 15/09
PORTA = {"A": "S4", "B": "S5", "C": "S6"}

comprimento = lambda p: sum(b - a for a, b in PAREDES[p]["trechos"])


def cabe(span, duplas, isoladas):
    """Uma composicao de unidades cabe num trecho?"""
    n = duplas + isoladas
    if n == 0:
        return True
    return duplas * PASSO_DUPLA + (n - 1) * PASSO_UNID <= span + 1e-9


def capacidade(parede, isoladas_totais):
    """Quantas mesas cabem na parede, com `isoladas_totais` mesas isoladas.

    As isoladas sao as de maior carga (uma por parede, sempre) mais, na parede
    que receber a sobra, a mesa avulsa do total impar. O resto anda em duplas.
    """
    melhor = 0
    for trechos in _reparte_isoladas(PAREDES[parede]["trechos"], isoladas_totais):
        total = 0
        for span, iso in trechos:
            d = 0
            while cabe(span, d + 1, iso):
                d += 1
            total += 2 * d + iso
        melhor = max(melhor, total)
    return melhor


def _reparte_isoladas(trechos, n):
    """Todas as maneiras de espalhar n isoladas pelos trechos."""
    if len(trechos) == 1:
        yield [(trechos[0][1] - trechos[0][0], n)]
        return
    span = trechos[0][1] - trechos[0][0]
    for k in range(n + 1):
        for resto in _reparte_isoladas(trechos[1:], n - k):
            yield [(span, k)] + resto


def isoladas_de(n_mesas):
    """Quantas mesas isoladas uma parede com `n_mesas` tem.

    Sempre a de maior carga; mais uma avulsa quando as demais forem impares,
    porque nao ha como fechar todas em duplas.
    """
    return 1 + ((n_mesas - 1) % 2)


def reparticoes(mesas):
    """(n_oeste, n_norte, n_leste) que cabem fisicamente, com uma alta em cada."""
    total = len(mesas)
    saida = []
    for n_o, n_n in itertools.product(range(1, total - 1), repeat=2):
        n_l = total - n_o - n_n
        if n_l < 1:
            continue
        contas = dict(zip(ORDEM, (n_o, n_n, n_l)))
        if all(contas[p] <= capacidade(p, isoladas_de(contas[p])) for p in ORDEM):
            saida.append(contas)
    return saida


def equilibra(mesas, contas, altas, iteracoes=90):
    """A atribuicao mesa -> parede que mais aproxima o esperado das tres.

    Uma das tres mesas de maior carga em cada parede (elas nunca dividem fila),
    e busca local sobre as demais: troca pares entre paredes enquanto o maior
    intervalo entre paredes diminuir.
    """
    esperado = {m["mrv"]: m["esperado"] for m in mesas}
    outras = sorted((m["mrv"] for m in mesas if m["mrv"] not in altas),
                    key=lambda n: -esperado[n])
    melhor = None
    # cada permutacao das altas pelas paredes e um ponto de partida distinto
    for perm in itertools.permutations(altas):
        base = {p: [perm[i]] for i, p in enumerate(ORDEM)}
        # semeadura guloso: a proxima mesa vai para a parede mais longe da cota
        grupos = {p: list(v) for p, v in base.items()}
        alvo = {p: sum(esperado.values()) * contas[p] / len(mesas) for p in ORDEM}
        for n in outras:
            cabem = [p for p in ORDEM if len(grupos[p]) < contas[p]]
            p = max(cabem, key=lambda p: alvo[p] - sum(esperado[x] for x in grupos[p]))
            grupos[p].append(n)
        custo = lambda g: (max(sum(esperado[x] for x in g[p]) for p in ORDEM)
                           - min(sum(esperado[x] for x in g[p]) for p in ORDEM))
        c = custo(grupos)
        for _ in range(iteracoes):
            achou = False
            for a, b in itertools.combinations(ORDEM, 2):
                for i, x in enumerate(grupos[a]):
                    if x in altas:
                        continue
                    for j, y in enumerate(grupos[b]):
                        if y in altas:
                            continue
                        grupos[a][i], grupos[b][j] = y, x
                        novo = custo(grupos)
                        if novo < c - 1e-9:
                            c, achou = novo, True
                        else:
                            grupos[a][i], grupos[b][j] = x, y
                        if achou:
                            break
                    if achou:
                        break
                if achou:
                    break
            if not achou:
                break
        if melhor is None or c < melhor[0]:
            melhor = (c, {p: sorted(grupos[p]) for p in ORDEM})
    return melhor


def unidades_da_parede(mrvs, altas, esperado):
    """As unidades da parede: as isoladas primeiro, depois as duplas."""
    isoladas = [n for n in mrvs if n in altas]
    resto = [n for n in mrvs if n not in altas]
    if len(resto) % 2:
        # a avulsa e a de menor carga: e a que menos precisa de vizinha
        avulsa = min(resto, key=lambda n: esperado[n])
        resto.remove(avulsa)
        isoladas.append(avulsa)
    resto.sort()
    return ([{"tipo": "isolada", "mrvs": [n]} for n in isoladas]
            + [{"tipo": "dupla", "mrvs": [resto[i], resto[i + 1]]}
               for i in range(0, len(resto), 2)])


def distribui(parede, unidades):
    """Empacota as unidades nos trechos da parede. None se não couber."""
    trechos = [{"ini": a, "fim": b, "span": b - a, "u": []}
               for a, b in PAREDES[parede]["trechos"]]
    # duplas primeiro, que são as maiores
    for u in sorted(unidades, key=lambda u: u["tipo"] != "dupla"):
        candidatos = []
        for t in trechos:
            d = sum(1 for x in t["u"] if x["tipo"] == "dupla") + (u["tipo"] == "dupla")
            iso = sum(1 for x in t["u"] if x["tipo"] == "isolada") + (u["tipo"] == "isolada")
            if not cabe(t["span"], d, iso):
                continue
            usado = d * PASSO_DUPLA + (d + iso - 1) * PASSO_UNID
            # uma isolada prefere um trecho que já tem gente: sozinha num
            # trecho de ponta, a mesa de maior carga fica no canto do salão
            abre_vazio = 1 if (u["tipo"] == "isolada" and not t["u"]) else 0
            candidatos.append(((abre_vazio, -(t["span"] - usado)), t))
        if not candidatos:
            return None
        min(candidatos, key=lambda c: c[0])[1]["u"].append(u)
    return trechos


def posicoes(parede, trechos):
    """As unidades empacotadas viram posições de mesa, em x/y/rot/lado."""
    P = PAREDES[parede]
    saida = []
    for t in trechos:
        if not t["u"]:
            continue
        nd = sum(1 for u in t["u"] if u["tipo"] == "dupla")
        n = len(t["u"])
        usado = nd * PASSO_DUPLA + (n - 1) * PASSO_UNID
        # a folga vira respiro entre unidades, com teto de 0,60 m: sem teto o
        # bloco encosta no vão de porta da borda; com teto, fica centrado e o
        # vão entre unidades nunca chega aos 3,90 m que separam uma dupla
        extra = min((t["span"] - usado) / (n - 1), 0.60) if n > 1 else 0
        cur = t["ini"] + (t["span"] - (usado + (n - 1) * extra)) / 2
        for u in _intercala(t["u"]):
            if u["tipo"] == "dupla":
                saida.append({"n": u["mrvs"][0], "u": cur, "lado": 1})
                saida.append({"n": u["mrvs"][1], "u": cur + PASSO_DUPLA, "lado": -1})
                cur += PASSO_DUPLA
            else:
                saida.append({"n": u["mrvs"][0], "u": cur, "lado": 1})
            cur += PASSO_UNID + extra
    todos = [v for t in P["trechos"] for v in t]
    espelho = min(todos) + max(todos)
    fora = []
    for o in saida:
        c = round(o["u"] if P["sentido"] > 0 else espelho - o["u"], 2)
        fora.append({"n": o["n"], "rot": P["rot"], "lado": o["lado"],
                     **({"x": c, "y": P["fixo"]} if P["eixo"] == "x"
                        else {"x": P["fixo"], "y": c})})
    return fora


def _intercala(unidades):
    """Isoladas entre as duplas, nunca uma isolada ao lado da outra.

    Duas isoladas vizinhas se leem como uma dupla com as cadeiras trocadas,
    que e o oposto do que a regra das duplas quer mostrar.
    """
    iso = [u for u in unidades if u["tipo"] == "isolada"]
    dup = [u for u in unidades if u["tipo"] == "dupla"]
    if not iso:
        return dup
    cortes = [round((k + 1) * len(dup) / (len(iso) + 1)) for k in range(len(iso))]
    seq, d = [], 0
    for k in range(len(iso)):
        while d < cortes[k]:
            seq.append(dup[d]); d += 1
        seq.append(iso[k])
    seq.extend(dup[d:])
    return seq


def monta(mesas, grupos, altas):
    """Do agrupamento por parede às 28 posições. None se algo não couber."""
    esperado = {m["mrv"]: m["esperado"] for m in mesas}
    alteracoes, relatorio = [], {}
    for parede in ORDEM:
        unidades = unidades_da_parede(grupos[parede], altas, esperado)
        trechos = distribui(parede, unidades)
        if trechos is None:
            return None
        alteracoes.extend(posicoes(parede, trechos))
        relatorio[parede] = {
            "entrada": ENTRADA[parede], "porta": PORTA[ENTRADA[parede]],
            "mesas": grupos[parede],
            "esperado": sum(esperado[n] for n in grupos[parede]),
            "metros": round(comprimento(parede), 2),
            "duplas": [u["mrvs"] for u in unidades if u["tipo"] == "dupla"],
            "isoladas": [u["mrvs"][0] for u in unidades if u["tipo"] == "isolada"],
        }
    alteracoes.sort(key=lambda a: a["n"])
    return {"alteracoes": alteracoes, "relatorio": relatorio}


def folgas(alteracoes, grupos):
    """A menor folga livre entre corpos vizinhos, parede a parede.

    Dentro de uma dupla os modulos ficam a 3,90 m de eixo a eixo, o que da
    3,00 m livres; entre unidades, 2,40 m de eixo, 1,50 m livres.
    """
    LARG = 0.90
    pos = {a["n"]: a for a in alteracoes}
    saida = {}
    for parede, mrvs in grupos.items():
        eixo = PAREDES[parede]["eixo"]
        cs = sorted(pos[n][eixo] for n in mrvs)
        saida[parede] = round(min(b - a for a, b in zip(cs, cs[1:])) - LARG, 2)
    return saida


def melhor_arranjo(mesas, atual=None):
    """Varre as repartições viáveis e devolve a melhor, com as candidatas.

    Ordena por: carga mais parecida entre as paredes; depois menos mesa
    trocando de parede em relação a `atual`; depois espaço por mesa mais
    parecido entre as paredes.
    """
    esperado = {m["mrv"]: m["esperado"] for m in mesas}
    altas = tuple(sorted((m["mrv"] for m in mesas if m["classe"] == "alta")))
    total = sum(esperado.values())
    candidatas = []
    for contas in reparticoes(mesas):
        r = equilibra(mesas, contas, altas)
        if r is None:
            continue
        custo, grupos = r
        arranjo = monta(mesas, grupos, altas)
        if arranjo is None:
            continue
        cargas = {p: arranjo["relatorio"][p]["esperado"] for p in ORDEM}
        dens = {p: cargas[p] / comprimento(p) for p in ORDEM}
        espaco = {p: comprimento(p) / contas[p] for p in ORDEM}
        mudam = (sum(1 for p in ORDEM for n in grupos[p] if atual.get(n) != p)
                 if atual else 0)
        candidatas.append({
            "contas": dict(contas), "grupos": grupos,
            "amplitude": max(cargas.values()) - min(cargas.values()),
            "mudam": mudam,
            "espaco": round(max(espaco.values()) - min(espaco.values()), 2),
            "cargas": cargas, "dens": dens, "espaco_por_mesa": espaco,
            "folgas": folgas(arranjo["alteracoes"], grupos), "arranjo": arranjo,
        })
    if not candidatas:
        raise SystemExit("nenhuma repartição das mesas coube nas três paredes")
    candidatas.sort(key=lambda c: (c["amplitude"], c["mudam"], c["espaco"]))
    return candidatas[0], candidatas, total


def main(argv):
    with open(os.path.join(RAIZ, "data", "decisoes.json"), encoding="utf-8") as f:
        decisoes = json.load(f)
    mesas = decisoes["mesas"]
    atual = {m["mrv"]: m["parede"] for m in mesas}
    melhor, candidatas, total = melhor_arranjo(mesas, atual)

    print(f"{len(mesas)} mesas · {total} esperados · terço perfeito {total / 3:.0f}")
    print(f"\nCapacidade física de cada parede (duplas de {PASSO_DUPLA} m, "
          f"{PASSO_UNID} m entre unidades):")
    for p in ORDEM:
        print(f"  {p:<6} {comprimento(p):>5.2f} m em {len(PAREDES[p]['trechos'])} trecho(s)"
              f" · cabem até {capacidade(p, 1)} mesas com uma isolada, "
              f"{capacidade(p, 2)} com duas")

    print(f"\n{len(candidatas)} repartições couberam. As melhores:")
    print(f"  {'mesas o/n/l':<12} {'ampl.':>6} {'trocam':>7}  {'esperado por parede':<24}"
          f" {'metros por mesa':<22} {'menor folga livre':<22}")
    for c in candidatas[:8]:
        cargas = " · ".join(f"{c['cargas'][p]:>4}" for p in ORDEM)
        esp = " · ".join(f"{c['espaco_por_mesa'][p]:>5.2f}" for p in ORDEM)
        fol = " · ".join(f"{c['folgas'][p]:>5.2f}" for p in ORDEM)
        print(f"  {'/'.join(str(c['contas'][p]) for p in ORDEM):<12} {c['amplitude']:>6}"
              f" {c['mudam']:>7}  {cargas:<24} {esp:<22} {fol:<22}")

    r = melhor["arranjo"]["relatorio"]
    print(f"\nEscolhida — {melhor['mudam']} das {len(mesas)} mesas trocam de parede:")
    for p in ORDEM:
        d = r[p]
        print(f"  {p:<6} entrada {d['entrada']} (porta {d['porta']}) · "
              f"{len(d['mesas'])} mesas · {d['esperado']} esperados · "
              f"{d['esperado'] / d['metros']:.1f} por metro")
        print(f"         duplas: {' '.join('(' + '+'.join(map(str, x)) + ')' for x in d['duplas'])}")
        print(f"         isoladas: {', '.join(map(str, d['isoladas']))}"
              f" · menor folga livre {melhor['folgas'][p]:.2f} m")

    # A alternativa que o Posto leva por padrao: a composicao de hoje ja da
    # 3.833/3.835/3.831, e chegar ao zero exige mover 16 das 28 mesas de
    # parede. Refazer so o pareamento mantem a composicao e melhora a pior
    # folga do salao.
    altas = tuple(sorted(m["mrv"] for m in mesas if m["classe"] == "alta"))
    grupos_atual = {p: sorted(n for n, q in atual.items() if q == p) for p in ORDEM}
    mantido = monta(mesas, grupos_atual, altas)
    if mantido is None:
        raise SystemExit("a composição atual não coube no empacotador")
    f = folgas(mantido["alteracoes"], grupos_atual)
    cargas = [mantido["relatorio"][p]["esperado"] for p in ORDEM]
    print(f"\nAlternativa — composição de hoje, só o pareamento refeito "
          f"(0 mesas trocam de parede):")
    for p in ORDEM:
        d = mantido["relatorio"][p]
        print(f"  {p:<6} entrada {d['entrada']} (porta {d['porta']}) · "
              f"{len(d['mesas'])} mesas · {d['esperado']} esperados · "
              f"{d['esperado'] / d['metros']:.1f} por metro · "
              f"menor folga {f[p]:.2f} m")
        print(f"         duplas: {' '.join('(' + '+'.join(map(str, x)) + ')' for x in d['duplas'])}")
        print(f"         isoladas: {', '.join(map(str, d['isoladas']))}")
    print(f"  amplitude {max(cargas) - min(cargas)} eleitores "
          f"({100 * (max(cargas) - min(cargas)) / (total / 3):.2f}% do terço)")

    if "--grava" not in argv:
        print("\n(nada gravado; use --grava para aplicar, e --otimo para a "
              "repartição de amplitude zero em vez da composição de hoje)")
        return mantido

    usa_otimo = "--otimo" in argv
    grupos = melhor["grupos"] if usa_otimo else grupos_atual
    arranjo = melhor["arranjo"] if usa_otimo else mantido
    decisoes, cenario = grava(decisoes, grupos, arranjo)

    caminho_cenario = os.path.join(RAIZ, "cenarios", ID_CENARIO + ".json")
    with open(caminho_cenario, "w", encoding="utf-8") as fh:
        json.dump(cenario, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    with open(os.path.join(RAIZ, "data", "decisoes.json"), "w", encoding="utf-8") as fh:
        json.dump(decisoes, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    print(f"\ngravado cenarios/{ID_CENARIO}.json e data/decisoes.json "
          f"({'repartição ótima' if usa_otimo else 'composição mantida'})")
    return arranjo



# --------------------------------------------------------------------------
# Gravacao: o cenario novo e o data/decisoes.json com as entradas por parede
# --------------------------------------------------------------------------
ID_CENARIO = "paredes-abc-20260915"
NOME_CENARIO = "Paredes_ABC"
CORES = {"A": ("azul", "#2a78d6"), "B": ("âmbar", "#e08a00"), "C": ("magenta", "#c2185b")}


def numeracao_eleitor(alteracoes, grupos):
    """1 na mesa mais ao sul da parede oeste, sentido horario ate 28.

    Oeste de sul para norte, norte de oeste para leste, leste de norte para
    sul -- a ordem em que o eleitor encontra as mesas ao dar a volta no salao.
    """
    pos = {a["n"]: a for a in alteracoes}
    ordem = []
    ordem += sorted(grupos["oeste"], key=lambda n: pos[n]["y"])
    ordem += sorted(grupos["norte"], key=lambda n: pos[n]["x"])
    ordem += sorted(grupos["leste"], key=lambda n: -pos[n]["y"])
    return {n: i + 1 for i, n in enumerate(ordem)}


def grava(decisoes, grupos, arranjo, quando="2026-09-15"):
    """Aplica o arranjo ao bloco de decisoes e devolve (decisoes, cenario)."""
    eleitor = numeracao_eleitor(arranjo["alteracoes"], grupos)
    parede_de = {n: p for p, ns in grupos.items() for n in ns}
    total = sum(m["esperado"] for m in decisoes["mesas"])

    for m in decisoes["mesas"]:
        p = parede_de[m["mrv"]]
        m["parede"] = p
        m["entrada"] = ENTRADA[p]
        m["porta"] = PORTA[ENTRADA[p]]
        m["eleitor"] = eleitor[m["mrv"]]

    entradas = []
    for p in ORDEM:
        e = ENTRADA[p]
        cor, hexa = CORES[e]
        esperado = arranjo["relatorio"][p]["esperado"]
        entradas.append({
            "id": e, "porta": PORTA[e], "cor": cor, "hex": hexa, "parede": p,
            "mrvs": sorted(grupos[p]), "esperado": esperado,
            "quota": round(esperado / total, 4),
            "metros_de_parede": round(comprimento(p), 2),
            "por_metro": round(esperado / comprimento(p), 1),
        })
    decisoes["entradas"] = entradas
    decisoes["portas"] = {
        **{PORTA[ENTRADA[p]]: {"papel": "entrada", "entrada": ENTRADA[p],
                               "cor": CORES[ENTRADA[p]][1], "parede": p} for p in ORDEM},
        **{s: {"papel": "saida"} for s in decisoes["saidas"]},
    }
    decisoes["atualizadoEm"] = quando
    decisoes["cenario_trabalho"] = {"id": ID_CENARIO, "nome": NOME_CENARIO,
                                    "criadoEm": quando + "T00:00:00.000Z",
                                    "provisorio": False}
    decisoes["entradas_por_parede"] = (
        "Decisão do Posto de 15/09/2026: cada entrada serve uma parede inteira e só ela — "
        "A (S4) a oeste, B (S5) ao norte, C (S6) a leste. Equilibrar as entradas e "
        "equilibrar as paredes passaram a ser o mesmo problema. Substitui a atribuição "
        "por cota do Ring 3, que não existe mais.")
    # o Ring 3 foi abandonado; as cotas que ele definia não valem mais
    if "ring3" in decisoes:
        decisoes["ring3"] = {
            "situacao": "abandonado em 15/09/2026 — o RDS proibiu fila no terreno e não "
                        "houve autorização de Brasília; a fila passa a ser dimensionada "
                        "dentro do Hall 2, uma por parede.",
        }

    cenario = {"nome": NOME_CENARIO, "base": "A", "id": ID_CENARIO,
               "alteracoes": arranjo["alteracoes"], "medidas": [],
               "criadoEm": quando + "T00:00:00.000Z"}
    return decisoes, cenario

if __name__ == "__main__":
    main(sys.argv)
