"""Ideia 2 — as 28 MRVs encostadas nas paredes do salao.

Cada modulo fica com o fundo na parede e a tela da urna voltada para ela: o
eleitor digita de costas para o salao e nenhum ponto do piso ve a tela. E a
premissa que o usuario pediu, e ela custa caro em metro linear, porque o
perimetro do Hall 2 esta recortado por catorze vaos.

O CONTEXTO §7 mostrou que a viabilidade depende de duas alavancas de fato: o
recuo de 3 m valer so para as saidas 2.16-2.23, e a urna poder ficar atras da
mesa (modulo em linha). Este modulo mostra que elas nao bastam. Contando cada
MRV pela frente minima, a parede oferece 29 posicoes; mas a baia de fila cresce
com a fila, e as tres urnas criticas pedem quase 10 m de frente cada no ponto de
projeto de 55 s. A conta real fecha em 110 m de frente exigida contra 75 m
disponiveis.

A terceira alavanca e o setor reforcado que a ideia 1 ja usa: quatro mesarios e
conferencia de documento dentro da fila levam as tres criticas ao ponto de 45 s,
e a fila de pico delas cai de 57 para 12. Com as tres, e so com as tres, as 28
MRVs cabem — e cabem exatamente, sem posicao de sobra.

Gera saidas/ideia2_dados.json.
"""
import json
import os

import salao as S

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ------------------------------------------------------------- as alavancas
# 1. Recuo de 3 m so nas saidas da parede leste; 0,6 m de balizador nas demais.
RECUO = {"leste": S.RECUO_EMERGENCIA, "norte": 0.6, "oeste": 0.6, "sul": 0.6}
# 2. Modulo em linha: urna atras da mesa dos mesarios, tela voltada a parede.
MOD_LARGURA, MOD_PROFUND = 1.80, 2.60
# 0,40 m de balizador entre modulos vizinhos, o mesmo criterio de
# salao.LARG_MIN_BAIA. A baia de fila, mais larga, leva os 0,60 m de
# salao.FOLGA_BAIA -- fila precisa de mais separacao que mobiliario.
FRENTE_MIN = MOD_LARGURA + 0.40
# 3. Setor reforcado: 4 mesarios e conferencia na fila levam a urna a 45 s.
SEG_REFORCADO = 45

# ------------------------------------------------------------ faixas do anel
PROF_BAIA_MAX = 7.0    # profundidade maxima da baia de fila
PROF_BAIA_MIN = 2.5    # avental minimo na frente do modulo, mesmo sem fila
RETORNO = 2.4          # corredor de retorno, colado na boca das baias
AVENIDA = 3.0          # avenida de entrada, entre o retorno e o miolo
ANEL = MOD_PROFUND + PROF_BAIA_MAX + RETORNO + AVENIDA   # 15,0 m

CANTOS = 1.5           # folga de canto usada no calculo de capacidade

# A parede sul e a fachada de entrada e saida, herdada da ideia 1: entra pelas
# duas portas de carga, sai pela baia central 2.4. Nao recebe MRV.
ESPINHA = dict(x0=25.4, x1=31.2, y0=0.0, y1=S.HALL_H - ANEL)

# Trechos que precisam ser encurtados ou abandonados porque a baia de uma
# parede invadiria a baia da perpendicular. Ver validacao no fim do arquivo.
LIMITE_OESTE = S.HALL_H - MOD_PROFUND - PROF_BAIA_MAX   # 34,8 m
TRECHOS_VETADOS = [("oeste", 39.10)]   # colide com a ponta oeste da parede norte


EIXO = {"norte": ("x", S.HALL_W), "sul": ("x", S.HALL_W),
        "oeste": ("y", S.HALL_H), "leste": ("y", S.HALL_H)}
PERPENDICULAR = {"norte": ("oeste", "leste"), "sul": ("oeste", "leste"),
                 "oeste": ("sul", "norte"), "leste": ("sul", "norte")}


def envelopes_de_canto(parede):
    """Pedacos da parede tomados pelo recuo de uma saida da parede vizinha.

    O recuo de 3 m das saidas 2.16-2.23 e um envelope, nao so uma faixa ao
    longo da propria parede: o da saida 2.16/2.17, que fica a 2,8 m do canto
    nordeste, alcanca a parede norte e come 3 m da ponta dela.
    """
    fim = EIXO[parede][1]
    cortes = []
    for i, vizinha in enumerate(PERPENDICULAR[parede]):
        limite = EIXO[vizinha][1]
        r = RECUO.get(vizinha, 0.6)
        for nome, a, b in S.PORTAS[vizinha]:
            if "carga" in nome or "Hall 1" in nome:
                continue
            # A parede em questao esta no inicio (i == 0) ou no fim do eixo da
            # vizinha; o envelope so a alcanca se transbordar aquela ponta.
            alcanca = (a - r < 0) if i == 0 else (b + r > limite)
            if alcanca:
                cortes.append((0.0, r) if i == 0 else (fim - r, fim))
    return cortes


def subtrai(intervalos, cortes):
    """Remove de cada intervalo os pedacos cobertos pelos cortes."""
    for c0, c1 in cortes:
        novos = []
        for x0, x1 in intervalos:
            if c1 <= x0 or c0 >= x1:
                novos.append((x0, x1))
                continue
            if x0 < c0:
                novos.append((x0, c0))
            if c1 < x1:
                novos.append((c1, x1))
        intervalos = novos
    return intervalos


def trechos_uteis():
    """Trechos de parede aproveitaveis, ja resolvidos os conflitos de canto."""
    brutos, _, _ = S.capacidade_de_parede(recuo=RECUO, frente=FRENTE_MIN,
                                          cantos=CANTOS)
    expandidos = []
    for parede, x0, x1, _, _ in brutos:
        if parede == "sul":
            continue
        for a, b in subtrai([(x0, x1)], envelopes_de_canto(parede)):
            expandidos.append((parede, a, b, 0, 0))
    saida = []
    for parede, x0, x1, _, _ in expandidos:
        if any(p == parede and abs(x0 - v) < 0.01 for p, v in TRECHOS_VETADOS):
            continue
        if parede == "oeste":
            x1 = min(x1, LIMITE_OESTE)
        if x1 - x0 < FRENTE_MIN:
            continue
        saida.append({"parede": parede, "de": round(x0, 2), "ate": round(x1, 2),
                      "comprimento": round(x1 - x0, 2)})
    return saida


def dimensiona(fila: int) -> tuple[float, float]:
    """Largura e profundidade da baia de uma urna com dada fila de pico.

    A largura sai da fila espalhada na profundidade maxima; a profundidade
    depois encolhe para o que a fila realmente ocupa naquela largura. Baia rasa
    onde a fila e curta e o que impede que as baias de duas paredes
    perpendiculares se encontrem nos cantos.
    """
    largura = max(FRENTE_MIN, fila * S.AREA_PESSOA / PROF_BAIA_MAX + S.FOLGA_BAIA)
    if fila <= 0:
        return round(largura, 2), PROF_BAIA_MIN
    profundidade = fila * S.AREA_PESSOA / (largura - S.FOLGA_BAIA)
    return round(largura, 2), round(min(PROF_BAIA_MAX,
                                        max(PROF_BAIA_MIN, profundidade)), 2)


def prepara_urnas():
    """As 28 urnas com fila de pico, ja aplicado o setor reforcado."""
    urnas = S.carrega_urnas()
    for u in urnas:
        u["classe"] = S.classe(u)
        u["reforcada"] = u["classe"] == "critica"
        seg = SEG_REFORCADO if u["reforcada"] else S.SEG_POR_VOTO
        u["seg_por_voto"] = seg
        u["fila_pico"] = S.simula_fila(u["esperado"], seg)[0]
        u["fila_sem_reforco"] = S.simula_fila(u["esperado"])[0]
        u["largura"], u["profundidade"] = dimensiona(u["fila_pico"])
    return urnas


# --------------------------------------------------------------- circuitos
# A ordem em que o eleitor de cada zona encontra as MRVs, subindo da porta de
# carga para o fundo do salao. A carga cresce ao longo dela: quem vota numa
# urna leve nunca atravessa o campo de fila de uma urna pesada.
# Cada vaga traz o sentido de preenchimento: "+" ocupa o trecho a partir do
# inicio, "-" a partir do fim. E o sentido em que o eleitor caminha.
CIRCUITO_A = [("oeste", 8.50, 4, "+"), ("oeste", 23.03, 5, "+"),
              ("norte", 1.50, 2, "+"), ("norte", 10.04, 4, "+")]
# A zona B sobe pela parede leste e depois volta para oeste pela parede norte,
# entao o trecho longo do norte se preenche de tras para a frente e encontra o
# setor reforcado no meio.
CIRCUITO_B = [("leste", 9.01, 1, "+"), ("leste", 20.87, 1, "+"),
              ("leste", 32.72, 1, "+"), ("norte", 24.82, 7, "-")]
# O setor reforcado ocupa a ponta oeste do trecho longo da parede norte, logo
# acima da cabeca da espinha de saida: e o ponto mais fundo do circuito das
# duas zonas e o que descarrega mais perto da porta de saida.
SETOR = ("norte", 24.82, 3, "+")


def aloca(urnas):
    """Reparte as 28 urnas entre setor reforcado, zona A e zona B.

    As tres criticas vao para o setor. Das 25 restantes, as 15 mais leves
    formam a zona A e as 10 mais pesadas a zona B -- e o que aproxima as duas
    zonas em eleitorado, ja que A tem mais posicoes que B.
    """
    criticas = sorted((u for u in urnas if u["reforcada"]),
                      key=lambda u: -u["esperado"])
    resto = sorted((u for u in urnas if not u["reforcada"]),
                   key=lambda u: u["esperado"])
    n_a = sum(n for _, _, n, _ in CIRCUITO_A)
    n_b = sum(n for _, _, n, _ in CIRCUITO_B)
    if len(criticas) != SETOR[2] or len(resto) != n_a + n_b:
        raise SystemExit(f"alocacao nao fecha: {len(criticas)} criticas e "
                         f"{len(resto)} demais para {SETOR[2]}+{n_a}+{n_b} vagas")
    return criticas, resto[:n_a], resto[n_a:]


def posiciona(urnas, circuito, zona, trechos, cursores):
    """Encaixa as urnas nas vagas do circuito, na ordem, e devolve as MRVs.

    `cursores` guarda as duas frentes de ocupacao de cada trecho, para que o
    setor reforcado e a zona B possam dividir o trecho longo da parede norte
    sem se atropelarem: um entra pelo inicio, o outro pelo fim.
    """
    mrvs, fila_urnas = [], list(urnas)
    for parede, inicio, quantas, sentido in circuito:
        chave = (parede, inicio)
        trecho = next(t for t in trechos
                      if t["parede"] == parede and abs(t["de"] - inicio) < 0.01)
        borda = cursores.setdefault(chave, {"ini": trecho["de"], "fim": trecho["ate"]})
        for _ in range(quantas):
            u = fila_urnas.pop(0)
            if sentido == "+":
                centro = borda["ini"] + u["largura"] / 2
                borda["ini"] += u["largura"]
            else:
                centro = borda["fim"] - u["largura"] / 2
                borda["fim"] -= u["largura"]
            mrvs.append(monta(u, parede, centro, zona))
        if borda["ini"] > borda["fim"] + 0.005:
            raise SystemExit(
                f"trecho {parede} {trecho['de']}-{trecho['ate']} estourou em "
                f"{borda['ini'] - borda['fim']:.2f} m")
    return mrvs


def monta(u, parede, centro, zona):
    """Uma MRV posicionada: modulo colado na parede, baia de fila a frente."""
    larg, prof = u["largura"], u["profundidade"]
    if parede == "norte":
        mod = (centro - larg / 2, S.HALL_H - MOD_PROFUND, centro + larg / 2, S.HALL_H)
        baia = (mod[0], mod[1] - prof, mod[2], mod[1])
        olhar = "norte"
    elif parede == "oeste":
        mod = (0.0, centro - larg / 2, MOD_PROFUND, centro + larg / 2)
        baia = (mod[2], mod[1], mod[2] + prof, mod[3])
        olhar = "oeste"
    else:
        mod = (S.HALL_W - MOD_PROFUND, centro - larg / 2, S.HALL_W, centro + larg / 2)
        baia = (mod[0] - prof, mod[1], mod[0], mod[3])
        olhar = "leste"
    return {
        "urna": u["urna"], "secoes": u["secoes"], "zona": zona,
        "classe": u["classe"], "reforcada": u["reforcada"],
        "aptos": u["aptos"], "esperado": u["esperado"],
        "origem_interior": u["origem_interior"],
        "seg_por_voto": u["seg_por_voto"], "fila_pico": u["fila_pico"],
        "fila_sem_reforco": u["fila_sem_reforco"],
        "parede": parede, "centro": round(centro, 2), "olhar": olhar,
        "baia_largura": larg, "baia_profundidade": prof,
        "modulo": [round(v, 2) for v in mod],
        "baia": [round(v, 2) for v in baia],
    }


# --------------------------------------------------------------- validacao
def sobrepoe(a, b, folga=0.0):
    return not (a[2] + folga <= b[0] or b[2] + folga <= a[0]
                or a[3] + folga <= b[1] or b[3] + folga <= a[1])


def dentro_do_salao(x, y):
    """O salao e o retangulo menos o recorte do canto sudoeste."""
    rx0, ry0, rx1, ry1 = S.RECORTE
    if not (-0.01 <= x <= S.HALL_W + 0.01 and -0.01 <= y <= S.HALL_H + 0.01):
        return False
    return not (rx0 - 0.01 < x < rx1 - 0.01 and ry0 - 0.01 < y < ry1 - 0.01)


def envelope_da_porta(parede, a, b, recuo):
    """Faixa que a saida projeta para dentro do salao e tem de ficar vazia."""
    if parede == "norte":
        return (a - recuo, S.HALL_H - recuo, b + recuo, S.HALL_H)
    if parede == "sul":
        return (a - recuo, 0.0, b + recuo, recuo)
    if parede == "oeste":
        return (0.0, a - recuo, recuo, b + recuo)
    return (S.HALL_W - recuo, a - recuo, S.HALL_W, b + recuo)


def confere(mrvs, urnas):
    """Recusa o layout em vez de desenhar planta impossivel.

    Foi esta checagem que apontou os dois conflitos de canto que o modelo hoje
    trata -- a baia da ponta norte da parede oeste contra a baia da ponta oeste
    da parede norte, e a baia mais ao norte da parede leste contra a ponta
    leste da parede norte.
    """
    if len(mrvs) != 28:
        raise SystemExit(f"{len(mrvs)} MRVs, esperadas 28")
    if sorted(m["urna"] for m in mrvs) != sorted(u["urna"] for u in urnas):
        raise SystemExit("as MRVs colocadas nao sao as 28 urnas do TSE")
    if sum(m["esperado"] for m in mrvs) != sum(u["esperado"] for u in urnas):
        raise SystemExit("o eleitorado esperado nao fecha")

    for m in mrvs:
        for retangulo, nome in ((m["modulo"], "modulo"), (m["baia"], "baia")):
            for x in (retangulo[0] + 0.01, retangulo[2] - 0.01):
                for y in (retangulo[1] + 0.01, retangulo[3] - 0.01):
                    if not dentro_do_salao(x, y):
                        raise SystemExit(f"{nome} da urna {m['urna']} sai do "
                                         f"salao em ({x:.2f}, {y:.2f})")

    ocupados = [(m, [m["modulo"][0], min(m["modulo"][1], m["baia"][1]),
                     m["modulo"][2], max(m["modulo"][3], m["baia"][3])]
                 if m["parede"] == "norte" else
                 [min(m["modulo"][0], m["baia"][0]), m["modulo"][1],
                  max(m["modulo"][2], m["baia"][2]), m["modulo"][3]])
                for m in mrvs]
    for i, (m1, r1) in enumerate(ocupados):
        for m2, r2 in ocupados[i + 1:]:
            if sobrepoe(r1, r2, folga=-0.02):
                raise SystemExit(f"as urnas {m1['urna']} ({m1['parede']}) e "
                                 f"{m2['urna']} ({m2['parede']}) se sobrepoem")

    for parede, portas in S.PORTAS.items():
        for nome, a, b in portas:
            if "carga" in nome or "Hall 1" in nome:
                continue
            recuo = RECUO.get(parede, 0.6)
            faixa = envelope_da_porta(parede, a, b, recuo)
            for m, r in ocupados:
                if sobrepoe(r, faixa):
                    raise SystemExit(f"a urna {m['urna']} invade o recuo de "
                                     f"{recuo} m da saida {nome} ({parede})")

    espinha = (ESPINHA["x0"], ESPINHA["y0"], ESPINHA["x1"], ESPINHA["y1"])
    for m, r in ocupados:
        if sobrepoe(r, espinha):
            raise SystemExit(f"a urna {m['urna']} invade a espinha de saida")


def faixas(mrvs):
    """As faixas do anel em cada parede, medidas da parede para dentro.

    A profundidade do retorno e da avenida acompanha a baia mais funda daquela
    parede: onde as filas sao curtas o anel encolhe e devolve piso ao miolo.
    """
    saida = {}
    for parede in ("norte", "oeste", "leste"):
        fundas = [m["baia_profundidade"] for m in mrvs if m["parede"] == parede]
        if not fundas:
            continue
        baia = max(fundas)
        saida[parede] = {
            "modulo": [0.0, MOD_PROFUND],
            "baia": [MOD_PROFUND, MOD_PROFUND + baia],
            "retorno": [MOD_PROFUND + baia, MOD_PROFUND + baia + RETORNO],
            "avenida": [MOD_PROFUND + baia + RETORNO,
                        MOD_PROFUND + baia + RETORNO + AVENIDA],
            "total": round(MOD_PROFUND + baia + RETORNO + AVENIDA, 2),
        }
    return saida


def distancia_da_entrada(m):
    """Caminhada em quarteirao da porta da zona ate o modulo, em metros."""
    if m["parede"] == "norte":
        alvo = (m["centro"], S.HALL_H - MOD_PROFUND / 2)
    elif m["parede"] == "oeste":
        alvo = (MOD_PROFUND / 2, m["centro"])
    else:
        alvo = (S.HALL_W - MOD_PROFUND / 2, m["centro"])
    portas = ([S.ENTRADA_A, S.ENTRADA_B] if m["zona"] == "setor"
              else [S.ENTRADA_ZONA[m["zona"]]])
    return round(min(abs(alvo[0] - p[0]) + abs(alvo[1] - p[1]) for p in portas), 1)


def indicadores(mrvs):
    zonas = {}
    for m in mrvs:
        z = zonas.setdefault(m["zona"], {"mrvs": 0, "esperado": 0, "aptos": 0})
        z["mrvs"] += 1
        z["esperado"] += m["esperado"]
        z["aptos"] += m["aptos"]
    frente = sum(m["baia_largura"] for m in mrvs)
    distancias = [m["dist_entrada"] for m in mrvs]
    # Mesmo criterio da ideia 1: tres mesarios por MRV, quatro nas reforcadas.
    mesarios = sum(4 if m["reforcada"] else 3 for m in mrvs)
    # Balizador: os dois lados da baia mais a boca.
    balizador = sum(2 * m["baia_profundidade"] + m["baia_largura"] for m in mrvs)
    return {
        "mesarios": mesarios,
        "balizador_estimado_m": round(balizador),
        "dist_media_m": round(sum(distancias) / len(distancias), 1),
        "dist_maxima_m": max(distancias),
        "mrvs": len(mrvs),
        "esperado": sum(m["esperado"] for m in mrvs),
        "frente_ocupada_m": round(frente, 1),
        "frente_disponivel_m": round(
            sum(t["comprimento"] for t in trechos_uteis()), 1),
        "baia_mais_larga_m": max(m["baia_largura"] for m in mrvs),
        "baia_mais_funda_m": max(m["baia_profundidade"] for m in mrvs),
        "fila_pico_somada": sum(m["fila_pico"] for m in mrvs),
        "fila_pico_sem_reforco": sum(m["fila_sem_reforco"] for m in mrvs),
        "zonas": zonas,
    }


def cenarios_de_viabilidade(urnas):
    """A conta que decide, nas quatro combinacoes das duas alavancas do §7.

    A coluna que importa nao e o numero de posicoes de frente minima, e sim a
    frente que as 28 baias realmente pedem depois de dimensionadas pela fila.
    """
    linhas = []
    for rot, recuo, frente in (
        ("recuo de 3 m em todas as saidas · módulo lado a lado",
         S.RECUO_EMERGENCIA, S.LARG_MIN_BAIA),
        ("recuo de 3 m em todas as saidas · módulo em linha",
         S.RECUO_EMERGENCIA, FRENTE_MIN),
        ("recuo de 3 m só nas saídas 2.16–2.23 · módulo lado a lado",
         RECUO, S.LARG_MIN_BAIA),
        ("recuo de 3 m só nas saídas 2.16–2.23 · módulo em linha",
         RECUO, FRENTE_MIN),
    ):
        trechos, metros, posicoes = S.capacidade_de_parede(
            recuo=recuo, frente=frente, cantos=CANTOS)
        metros = round(sum(b - a for p, a, b, _, _ in trechos if p != "sul"), 1)
        posicoes = sum(n for p, _, _, _, n in trechos if p != "sul")
        linhas.append({"cenario": rot, "parede_livre_m": metros,
                       "posicoes": posicoes})

    # Frente exigida pelas baias, com e sem o setor reforcado.
    for rot, reforco in (("sem setor reforçado", False), ("com setor reforçado", True)):
        exigida = 0.0
        for u in urnas:
            seg = SEG_REFORCADO if (reforco and u["classe"] == "critica") else S.SEG_POR_VOTO
            exigida += dimensiona(S.simula_fila(u["esperado"], seg)[0])[0]
        linhas.append({"cenario": f"frente exigida pelas 28 baias, {rot}",
                       "parede_livre_m": None, "exigida_m": round(exigida, 1)})
    return linhas


def main():
    urnas = prepara_urnas()
    trechos = trechos_uteis()
    criticas, zona_a, zona_b = aloca(urnas)

    cursores = {}
    mrvs = posiciona(criticas, [SETOR], "setor", trechos, cursores)
    mrvs += posiciona(zona_b, CIRCUITO_B, "B", trechos, cursores)
    mrvs += posiciona(zona_a, CIRCUITO_A, "A", trechos, cursores)
    for m in mrvs:
        m["dist_entrada"] = distancia_da_entrada(m)
    confere(mrvs, urnas)

    ind = indicadores(mrvs)
    dados = {
        "ideia": 2,
        "titulo": "As 28 MRVs encostadas nas paredes",
        "hall": {"largura": S.HALL_W, "altura": S.HALL_H, "recorte": S.RECORTE},
        "portas": S.PORTAS,
        "recuo": RECUO,
        "modulo": {"largura": MOD_LARGURA, "profundidade": MOD_PROFUND,
                   "frente_minima": round(FRENTE_MIN, 2), "disposicao": "em linha"},
        "anel": {"modulo": MOD_PROFUND, "baia_max": PROF_BAIA_MAX,
                 "retorno": RETORNO, "avenida": AVENIDA, "total": ANEL},
        "faixas": faixas(mrvs),
        "espinha_saida": ESPINHA,
        "entradas": {"A": S.ENTRADA_A, "B": S.ENTRADA_B},
        "saida": S.SAIDA,
        "seg_por_voto": S.SEG_POR_VOTO,
        "seg_reforcado": SEG_REFORCADO,
        "trechos": trechos,
        "viabilidade": cenarios_de_viabilidade(urnas),
        "indicadores": ind,
        "mrvs": sorted(mrvs, key=lambda m: (m["zona"], -m["esperado"])),
    }
    destino = os.path.join(RAIZ, "saidas", "ideia2_dados.json")
    with open(destino, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=1)

    print(f"{ind['mrvs']} MRVs · {ind['esperado']} esperados · "
          f"{ind['frente_ocupada_m']} m de frente ocupada de "
          f"{ind['frente_disponivel_m']} m disponiveis")
    print(f"fila de pico somada: {ind['fila_pico_somada']} "
          f"(sem setor reforcado seria {ind['fila_pico_sem_reforco']})")
    for zona, z in sorted(ind["zonas"].items()):
        print(f"  zona {zona}: {z['mrvs']:2d} MRVs · {z['esperado']:5d} esperados")
    print()
    for linha in dados["viabilidade"]:
        if linha["parede_livre_m"] is not None:
            print(f"  {linha['cenario']:<58} {linha['parede_livre_m']:6.1f} m "
                  f"-> {linha['posicoes']:2d} posicoes")
        else:
            print(f"  {linha['cenario']:<58} {linha['exigida_m']:6.1f} m exigidos")
    print(f"\ngravado em {destino}")


if __name__ == "__main__":
    main()
