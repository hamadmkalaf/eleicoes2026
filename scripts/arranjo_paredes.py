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
# A vermelha de cada parede precisa de uma unidade verde de cada lado. Uma
# unidade verde e uma dupla de dois verdes ou uma isolada verde, entao quatro
# verdes por parede bastam para as duas: duas duplas inteiramente verdes.
MIN_VERDES = 4
# Quanta amplitude a mais a composicao de hoje pode ter e ainda vencer a otima.
# Zerar a amplitude custa mover 16 das 28 mesas de parede; 20 eleitores sao
# 0,5% do terco, abaixo do que qualquer mesario notaria num dia de nove horas.
TOLERANCIA_AMPLITUDE = 20
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
    pelo menos MIN_VERDES mesas verdes em cada uma (para ladear a vermelha), e
    busca local sobre as demais: troca pares entre paredes enquanto o maior
    intervalo entre paredes diminuir, sem quebrar o minimo de verdes.
    """
    esperado = {m["mrv"]: m["esperado"] for m in mesas}
    verde = {m["mrv"]: m["classe"] == "baixa" for m in mesas}
    outras = sorted((m["mrv"] for m in mesas if m["mrv"] not in altas),
                    key=lambda n: -esperado[n])
    melhor = None
    # cada permutacao das altas pelas paredes e um ponto de partida distinto
    for perm in itertools.permutations(altas):
        base = {p: [perm[i]] for i, p in enumerate(ORDEM)}
        # semeadura guloso: a proxima mesa vai para a parede mais longe da cota
        grupos = {p: list(v) for p, v in base.items()}
        alvo = {p: sum(esperado.values()) * contas[p] / len(mesas) for p in ORDEM}
        # primeiro o piso de verdes de cada parede, depois o equilibrio de carga
        verdes_livres = sorted((n for n in outras if verde[n]), key=lambda n: -esperado[n])
        for p in ORDEM:
            while (sum(1 for x in grupos[p] if verde[x]) < min(MIN_VERDES, contas[p] - 1)
                   and len(grupos[p]) < contas[p] and verdes_livres):
                grupos[p].append(verdes_livres.pop())
        postas = {x for g in grupos.values() for x in g}
        for n in outras:
            if n in postas:
                continue
            cabem = [p for p in ORDEM if len(grupos[p]) < contas[p]]
            p = max(cabem, key=lambda p: alvo[p] - sum(esperado[x] for x in grupos[p]))
            grupos[p].append(n)
        custo = lambda g: (max(sum(esperado[x] for x in g[p]) for p in ORDEM)
                           - min(sum(esperado[x] for x in g[p]) for p in ORDEM))
        def valido(g):
            return all(sum(1 for x in g[p] if verde[x]) >= min(MIN_VERDES, contas[p] - 1)
                       for p in ORDEM)
        if not valido(grupos):
            continue
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
                        novo = custo(grupos) if valido(grupos) else float("inf")
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


def unidades_da_parede(mrvs, altas, esperado, classe):
    """As unidades da parede: a vermelha isolada, a avulsa da paridade, e as duplas.

    As duplas emparelham **verde com verde primeiro**, para sobrar unidade
    inteiramente verde para ladear a vermelha (regra do Posto de 16/09: a mesa
    de maior carga fica no meio da parede, com verdes em volta).
    """
    vermelhas = [n for n in mrvs if n in altas]
    resto = [n for n in mrvs if n not in altas]
    isoladas = []
    if len(resto) % 2:
        # a avulsa e a de menor carga: e a que menos precisa de vizinha
        avulsa = min(resto, key=lambda n: esperado[n])
        resto.remove(avulsa)
        isoladas.append(avulsa)
    verdes = sorted(n for n in resto if classe[n] == "baixa")
    demais = sorted(n for n in resto if classe[n] != "baixa")
    duplas = []
    while len(verdes) >= 2:
        duplas.append([verdes.pop(0), verdes.pop(0)])
    sobra = verdes + demais                      # o verde solto, se houver, e os amarelos
    while len(sobra) >= 2:
        duplas.append([sobra.pop(0), sobra.pop(0)])
    if sobra:
        raise SystemExit(f"sobrou mesa sem par na parede com {mrvs}")

    def unidade(tipo, ns, **extra):
        return {"tipo": tipo, "mrvs": list(ns),
                "verde": all(classe[n] == "baixa" for n in ns), **extra}

    return ([unidade("isolada", [n], vermelha=True) for n in vermelhas]
            + [unidade("isolada", [n]) for n in isoladas]
            + [unidade("dupla", d) for d in duplas])


def largura(unidades):
    """Quanto um bloco de unidades ocupa, de encosto a encosto."""
    n = len(unidades)
    if not n:
        return 0.0
    return sum(PASSO_DUPLA for u in unidades if u["tipo"] == "dupla") + (n - 1) * PASSO_UNID


def _reparticoes_de_trecho(n_trechos, duplas, isoladas):
    """Todas as formas de repartir D duplas e I isoladas por N trechos."""
    def parte(total, n):
        if n == 1:
            yield (total,)
            return
        for k in range(total + 1):
            for resto in parte(total - k, n - 1):
                yield (k,) + resto
    for d in parte(duplas, n_trechos):
        for i in parte(isoladas, n_trechos):
            yield list(zip(d, i))


def _coloca(trechos, seqs):
    """Do bloco de cada trecho para o eixo de cada mesa.

    O bloco fica centrado no trecho, e o encosto do primeiro modulo e
    arredondado ao centimetro **antes** de somar os passos: assim os vaos
    saem exatos (3,90 e 2,40 m de encosto a encosto) e nao acumulam um
    centimetro de arredondamento.
    """
    saida = []
    for (ini, fim), seq in zip(trechos, seqs):
        if not seq:
            continue
        cur = round(ini + ((fim - ini) - largura(seq)) / 2, 2)
        for u in seq:
            if u["tipo"] == "dupla":
                saida.append((u["mrvs"][0], round(cur, 2), 1))
                saida.append((u["mrvs"][1], round(cur + PASSO_DUPLA, 2), -1))
                cur += PASSO_DUPLA
            else:
                saida.append((u["mrvs"][0], round(cur, 2), 1))
            cur += PASSO_UNID
    return saida


def _centralidade(postas, mrv_vermelha, verde_de):
    """Distância da vermelha ao meio da fileira, ou None se a regra falhar.

    A regra de 16/09 é dupla: a vermelha fica **no terço central** da fileira
    e as duas mesas imediatamente ao lado dela são **verdes**. O "ao lado" é
    global, não por trecho: um vão de porta separa, mas continua sendo o que o
    eleitor vê em volta da mesa cheia.
    """
    ordenadas = sorted(postas, key=lambda t: t[1])
    eixos = [c for _, c, _ in ordenadas]
    i = next(k for k, (m, _, _) in enumerate(ordenadas) if m == mrv_vermelha)
    vizinhas = [ordenadas[j][0] for j in (i - 1, i + 1) if 0 <= j < len(ordenadas)]
    if len(vizinhas) < 2 or any(not verde_de(v) for v in vizinhas):
        return None
    meio = (min(eixos) + max(eixos)) / 2
    desvio = abs(eixos[i] - meio)
    if desvio > (max(eixos) - min(eixos)) / 4:          # fora do terço central
        return None
    return desvio


def arranja_parede(parede, unidades, verde_de=lambda n: True):
    """As posições da parede, com a vermelha no meio e verdes ao lado.

    Varre todas as repartições das unidades pelos trechos e, em cada uma, todas
    as posições possíveis da vermelha, e fica com a que põe a vermelha mais
    perto do meio da fileira de mesas — sempre com uma unidade verde de cada
    lado dela. `None` se nada couber.
    """
    P = PAREDES[parede]
    trechos = P["trechos"]
    vermelha = next((u for u in unidades if u.get("vermelha")), None)
    demais = [u for u in unidades if u is not vermelha]
    n_duplas = sum(1 for u in unidades if u["tipo"] == "dupla")
    n_isoladas = sum(1 for u in unidades if u["tipo"] == "isolada")

    melhor = None
    for corte in _reparticoes_de_trecho(len(trechos), n_duplas, n_isoladas):
        if any(not cabe(b - a, d, i) for (a, b), (d, i) in zip(trechos, corte)):
            continue
        if vermelha is None:
            seqs = _preenche(corte, demais, None, None)
            if seqs is None:
                continue
            postas = _coloca(trechos, seqs)
            chave = (0, 0.0)
        else:
            melhor_local = None
            for t_red, (d, i) in enumerate(corte):
                if i == 0:
                    continue
                n = d + i
                for k in range(n):
                    seqs = _preenche(corte, demais, t_red, k, vermelha)
                    if seqs is None:
                        continue
                    postas = _coloca(trechos, seqs)
                    desvio = _centralidade(postas, vermelha["mrvs"][0], verde_de)
                    if desvio is None:
                        continue
                    if melhor_local is None or desvio < melhor_local[0]:
                        melhor_local = (desvio, postas)
            if melhor_local is None:
                continue
            chave, postas = melhor_local
            chave = (0, chave)
        if melhor is None or chave < melhor[0]:
            melhor = (chave, postas)

    if melhor is None:
        return None
    todos = [v for t in trechos for v in t]
    espelho = round(min(todos) + max(todos), 2)
    fora = []
    for mrv, c, lado in melhor[1]:
        v = round(c if P["sentido"] > 0 else espelho - c, 2)
        fora.append({"n": mrv, "rot": P["rot"], "lado": lado,
                     **({"x": v, "y": P["fixo"]} if P["eixo"] == "x"
                        else {"x": P["fixo"], "y": v})})
    return fora


def _preenche(corte, demais, t_red, k_red, vermelha=None):
    """Distribui as unidades pelos trechos, verdes ao lado da vermelha.

    `corte` diz quantas duplas e isoladas cada trecho leva; `t_red`/`k_red`
    dizem onde a vermelha entra. Devolve uma lista de sequências, uma por
    trecho, ou None se faltar unidade do tipo certo.
    """
    duplas = [u for u in demais if u["tipo"] == "dupla"]
    isoladas = [u for u in demais if u["tipo"] == "isolada"]
    # verdes primeiro na fila de saque, para sobrarem para ladear a vermelha
    verdes = [u for u in duplas + isoladas if u["verde"]]
    outras = [u for u in duplas + isoladas if not u["verde"]]

    seqs = []
    for t, (d, i) in enumerate(corte):
        n = d + i
        if t == t_red:
            if i < 1:
                return None
            seq = [None] * n
            seq[k_red] = vermelha
            faltam_d, faltam_i = d, i - 1
        else:
            seq = [None] * n
            faltam_d, faltam_i = d, i
        seqs.append({"seq": seq, "d": faltam_d, "i": faltam_i})

    def saca(tipo, preferir_verde):
        fontes = (verdes, outras) if preferir_verde else (outras, verdes)
        for fonte in fontes:
            for u in fonte:
                if u["tipo"] == tipo:
                    fonte.remove(u)
                    return u
        return None

    # 1. as duas vizinhas da vermelha, verdes
    if vermelha is not None:
        alvo = seqs[t_red]
        for v in (k_red - 1, k_red + 1):
            if not (0 <= v < len(alvo["seq"])) or alvo["seq"][v] is not None:
                continue
            tipo = "dupla" if alvo["d"] else "isolada"
            u = saca(tipo, True)
            if u is None or not u["verde"]:
                return None
            alvo["seq"][v] = u
            alvo["d" if tipo == "dupla" else "i"] -= 1
    # 2. o resto, duplas antes das isoladas
    for bloco in seqs:
        for idx, val in enumerate(bloco["seq"]):
            if val is not None:
                continue
            tipo = "dupla" if bloco["d"] else "isolada"
            u = saca(tipo, False)
            if u is None:
                return None
            bloco["seq"][idx] = u
            bloco["d" if tipo == "dupla" else "i"] -= 1
    return [b["seq"] for b in seqs]


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
    classe = {m["mrv"]: m["classe"] for m in mesas}
    alteracoes, relatorio = [], {}
    for parede in ORDEM:
        unidades = unidades_da_parede(grupos[parede], altas, esperado, classe)
        postas = arranja_parede(parede, unidades,
                                lambda n: classe.get(n) == "baixa")
        if postas is None:
            return None
        alteracoes.extend(postas)
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
    verde = {m["mrv"]: m["classe"] == "baixa" for m in mesas}
    sem_verde = [p for p in ORDEM
                 if sum(1 for n in grupos_atual[p] if verde[n])
                 < min(MIN_VERDES, len(grupos_atual[p]) - 1)]
    mantido = None if sem_verde else monta(mesas, grupos_atual, altas)
    if sem_verde:
        print(f"\nAlternativa — composição de hoje: NÃO SERVE MAIS.\n  A parede "
              f"{', '.join(sem_verde)} não tem as {MIN_VERDES} mesas verdes que a "
              f"regra de 16/09 exige para ladear a vermelha.")
    elif mantido is None:
        print("\nAlternativa — composição de hoje, só o pareamento refeito: "
              "NÃO CABE MAIS.\n  A regra de 16/09 (vermelha no meio da parede, com "
              "duas unidades verdes ao lado) reserva 12,60 m no trecho central, e a\n"
              "  parede norte com 9 mesas não fecha: o trecho oeste dela tem 10,01 m "
              "e duas duplas pedem 10,20 m.\n  A repartição escolhida acima passa a "
              "ser a única saída.")
        mantido = None
    else:
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

    if mantido is not None:
        cargas = [mantido["relatorio"][p]["esperado"] for p in ORDEM]
        excesso = (max(cargas) - min(cargas)) - melhor["amplitude"]
        if excesso > TOLERANCIA_AMPLITUDE:
            print(f"  → descartada: {excesso} eleitores de amplitude a mais que a "
                  f"repartição ótima, acima da tolerância de {TOLERANCIA_AMPLITUDE}.")
            mantido = None
        else:
            print(f"  → escolhida: {excesso} eleitores de amplitude a mais que a ótima, "
                  f"e nenhuma mesa troca de parede.")
    usa_otimo = "--otimo" in argv or mantido is None
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

RECUO_PORTA = 3.00        # desobstrucao na frente de N2 e O2 (decisao de 16/09)
FAIXA_LESTE = 3.00        # faixa protegida da fachada leste, das saidas L1 a L4

# Papel de cada porta que nao e entrada nem saida de eleitor. As entradas e
# saidas saem de ENTRADA/PORTA e de decisoes["saidas"].
PAPEIS_PORTA = {
    "N1": ("fechada", "porta de serviço, fechada no dia"),
    "N2": ("livre", "acesso de serviço — mantida desobstruída"),
    "L1": ("emergencia", "saída de emergência"),
    "L2": ("emergencia", "saída de emergência"),
    "L3": ("emergencia", "saída de emergência"),
    "L4": ("emergencia", "saída de emergência"),
    "O1": ("fechada", "acesso ao Hall 1, fechado no dia"),
    "O2": ("livre", "acesso de serviço — mantida desobstruída"),
    "R1": ("livre", "recorte sudoeste — recuo de emergência"),
    "S1": ("livre", "porta de carga, sem papel de eleitor"),
    "S3": ("livre", "recuo de emergência"),
    "S7": ("preferencial", "entrada preferencial — idoso, gestante, PcD, "
                           "com acompanhante, sem fila"),
    "S9": ("livre", "porta de carga, sem papel de eleitor"),
}


def sinalizacao_e_zonas(planta, decisoes):
    """O rotulo de cada porta e as areas que ficam livres de mesa e de fila."""
    portas = {p["id"]: p for p in planta["portas"]}
    sinal = {}
    for pid, p in portas.items():
        if pid in PORTA.values():
            e = next(k for k, v in PORTA.items() if v == pid)
            parede = next(w for w, x in ENTRADA.items() if x == e)
            sinal[pid] = {"papel": "entrada", "entrada": e, "parede": parede,
                          "rotulo": f"entrada {e} — parede {parede}"}
        elif pid in decisoes["saidas"]:
            sinal[pid] = {"papel": "saida", "rotulo": "saída de eleitor"}
        else:
            papel, rotulo = PAPEIS_PORTA[pid]
            sinal[pid] = {"papel": papel, "rotulo": rotulo}
        sinal[pid]["face"] = p["face"]
        sinal[pid]["rds"] = p["rds"]
        sinal[pid]["larg"] = p["larg"]

    zonas = [{"tipo": "faixa_emergencia", "porta": "L1 a L4",
              "rect": [50.3 - FAIXA_LESTE, 0.0, 50.3, 44.4],
              "rotulo": f"fachada leste · faixa protegida de {FAIXA_LESTE:.0f} m "
                        f"para as saídas de emergência"}]
    for pid in ("N2", "O2"):
        p = portas[pid]
        if p["face"] == "norte":
            rect = [p["x1"], p["y1"] - RECUO_PORTA, p["x2"], p["y2"]]
        else:                                    # fachada oeste
            rect = [p["x1"], p["y1"], p["x2"] + RECUO_PORTA, p["y2"]]
        zonas.append({"tipo": "recuo_porta", "porta": pid, "rect": rect,
                      "rotulo": f"{pid} · recuo de {RECUO_PORTA:.0f} m, "
                                f"sem mesa e sem fila"})
    zonas.append({"tipo": "recuo_porta", "porta": "S7",
                  "rect": [35.09, 0.0, 42.36, 3.0],
                  "rotulo": "S7 · recuo da entrada preferencial"})
    zonas.append({"tipo": "recuo_porta", "porta": "R1",
                  "rect": [7.8, 0.0, 10.8, 7.0],
                  "rotulo": "R1 · recuo de emergência"})
    zonas.append({"tipo": "recuo_porta", "porta": "S3",
                  "rect": [14.22, 0.0, 21.47, 3.0],
                  "rotulo": "S3 · recuo de emergência"})
    return sinal, zonas


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


def _planta():
    with open(os.path.join(RAIZ, "data", "prancheta_hall2.json"), encoding="utf-8") as f:
        return json.load(f)


def grava(decisoes, grupos, arranjo, quando="2026-09-16"):
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
    sinal, zonas = sinalizacao_e_zonas(_planta(), decisoes)
    decisoes["sinalizacao_portas"] = sinal
    decisoes["zonas_protegidas"] = zonas
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
