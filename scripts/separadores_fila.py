"""As 100 unifilas: onde a barreira vale mais do que a fita.

O Posto aprovou a fita no chao como desenho base -- linhas coladas no piso e
papel de sinalizacao colado junto. As 100 unifilas do orcamento (item d,
EUR 1.303,00) deixam de ser "a fila" e passam a ser um recurso escasso a
alocar. Este modulo calcula a alocacao DEFINITIVA (decisao de 17/09) e as duas
alternativas que ficaram no caminho, e desenha as tres.

Decisoes de 17/09
-----------------
1. As cores sao as das fitas ja em estoque: A azul, B amarelo, C laranja -- as
   mesmas do artefato de sinalizacao. Amarelo virou cor de zona, entao a linha
   de espera deixou de ser amarela e passou a zebrado preto-e-branco.
2. Os rotulos sao por GRUPO de mesas e por SECAO -- nunca por numero de mesa.
   Os 16 grupos (A1..A5, B1..B5, C1..C6) vem de ``data/grupos_mesas.json``.
3. **As avenidas nunca se cruzam.** ``confere()`` prova isso pela faixa de x de
   cada uma e sai com codigo 1 se alguma invadir zona protegida.

Convencoes de calculo
---------------------
Uma unifila de 2,00 m de cinta so fica esticada com os postes a cerca de 90%
do comprimento da cinta -- 1,80 m. Um trecho continuo de L metros custa
portanto ``ceil(L / 1.80) + 1`` postes, e **cada trecho independente custa um
poste a mais**, o terminal. Os "200 metros" do orcamento sao comprimento
nominal de cinta; esticados e repartidos em trechos, as 100 unidades rendem
perto de 170 m de linha util.

Geometria
---------
Le a planta medida (``data/prancheta_hall2.json``), o cenario fechado
(``cenarios/paredes-abc-20260915.json``) e as decisoes
(``data/decisoes.json``). Nao altera nenhum dos tres.

    python3 scripts/separadores_fila.py           # relatorio
    python3 scripts/separadores_fila.py --grava   # relatorio + SVG + JSON
"""
import json
import math
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAIDAS = os.path.join(RAIZ, "saidas")

# --------------------------------------------------------------------------
# Premissas do material
# --------------------------------------------------------------------------
CINTA = 2.00          # comprimento nominal da cinta, do orcamento
VAO_POSTE = 1.80      # 90% da cinta: o vao que deixa a cinta esticada
UNIFILAS = 100        # o que o orcamento aprovou
PRECO_UNIFILA = 13.03 # EUR, item (d) do orcamento / 100

LARG_AVENIDA = 3.00   # largura livre de cada avenida de entrada
LARG_CANAL = 1.10     # canal de micro-fila na frente da mesa
PASSO_FILA = 0.65     # metro de canal por pessoa, projeto (plano de filas)
RECUO_MESA = 1.50     # linha de espera: sigilo do voto


def postes(L):
    """Postes de um trecho continuo de L metros, cinta esticada."""
    if L <= 0:
        return 0
    return math.ceil(round(L / VAO_POSTE, 6)) + 1


def comp(pts):
    return sum(math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1))


# --------------------------------------------------------------------------
# Carga
# --------------------------------------------------------------------------
def carrega():
    with open(os.path.join(RAIZ, "data", "prancheta_hall2.json"), encoding="utf-8") as f:
        planta = json.load(f)
    with open(os.path.join(RAIZ, "data", "decisoes.json"), encoding="utf-8") as f:
        dec = json.load(f)
    with open(os.path.join(RAIZ, "cenarios", "paredes-abc-20260915.json"), encoding="utf-8") as f:
        cen = json.load(f)
    return planta, dec, cen


def monta_mesas(planta, dec, cen):
    """As 28 mesas com posicao, parede, entrada, classe e numero do eleitor."""
    base = {m["n"]: dict(m) for m in planta["cenarios"][cen["base"]]["mrvs"]}
    for alt in cen["alteracoes"]:
        base[alt["n"]].update(alt)
    with open(os.path.join(RAIZ, "data", "grupos_mesas.json"), encoding="utf-8") as f:
        grupos = json.load(f)["grupos"]
    grupo_de = {mrv: g for g in grupos for mrv in g["mrvs"]}

    mesas = []
    for d in dec["mesas"]:
        n = d["mrv"]
        m = base[n]
        rot = m["rot"]
        dx, dy = round(math.cos(math.radians(rot))), round(math.sin(math.radians(rot)))
        secoes = [d["principal"]] + ([d["agregada"]] if d["agregada"] else [])
        mesas.append({
            "mrv": n, "x": m["x"], "y": m["y"], "rot": rot, "dx": dx, "dy": dy,
            "parede": d["parede"], "entrada": d["entrada"],
            "hex_entrada": CORES_ZONA[d["entrada"]],
            "grupo": grupo_de[n]["id"], "grupo_secoes": grupo_de[n]["secoes"],
            "classe": d["classe"], "cor": d["cor"], "esperado": d["esperado"],
            "eleitor": d["eleitor"], "secoes": secoes,
        })
    return sorted(mesas, key=lambda m: m["eleitor"])


def frente(m, planta):
    """Ponto no eixo do modulo, na boca da mesa (fim do modulo, inicio da fila)."""
    P = planta["modulo"]["prof"]
    return (m["x"] + m["dx"] * P, m["y"] + m["dy"] * P)


def boca_avenida(m, planta):
    """Ponto onde o ramal daquela mesa encosta na avenida da sua parede."""
    fx, fy = frente(m, planta)
    sobra = BANDA_PAREDE[m["parede"]] - planta["modulo"]["prof"]
    return (fx + m["dx"] * sobra, fy + m["dy"] * sobra)


# --------------------------------------------------------------------------
# O traçado: avenidas, ramais, serpenteados
# --------------------------------------------------------------------------
# Cada avenida e um par de trilhos. A geometria evita as zonas protegidas de
# 16/09 (recuos de S3, S7, R1, N2, O2 e a faixa de emergencia da fachada leste).
# Cores das fitas que o Posto ja tem em estoque (a foto de 17/09) e que o
# artefato de sinalizacao Ek3FfeYnwvQLZEs4ZJ5Zzr ja usa nos paineis de porta:
# A azul, B amarelo, C laranja. Amarelo passa a ser da zona B, entao a linha de
# espera **nao pode mais ser amarela** -- vira zebrado preto-e-branco.
CORES_ZONA = {"A": "#33507E", "B": "#E8C63A", "C": "#DE7343"}
ESTOQUE_FITA = 165.0   # metros por cor ja em estoque (a confirmar: cada ou total)

# Regra de 17/09: **as avenidas nunca se cruzam.** Cada uma sai da sua porta e
# chega a sua parede sem tocar no envelope das outras -- A fica toda a oeste de
# x = 25,03, B entre 26,80 e 29,80, C entre 32,00 e 36,50.
#
# E o retorno? Nao usa o campo central: **as avenidas levam para dentro, as
# bandas trazem para fora.** Quem votou sai andando pela propria banda da sua
# parede ate S2 (banda oeste) ou S8 (banda leste). Assim nenhum fluxo de saida
# atravessa avenida nenhuma, e o campo central fica so como reserva de fila.
AVENIDAS = {
    # A sai pelos 3,20 m LESTE de S4 -- a metade oeste da porta esta sobre o
    # recuo de emergencia S3, que vai ate x = 21,47 -- sobe 3,40 m, vira a oeste
    # por baixo das mesas da parede oeste e sobe rente a banda. O trilho externo
    # em x = 25,03 encosta na alvenaria de 0,29 m que separa S4 de S5; a curva em
    # x = 11,00 fica a leste do recuo R1 (ate 10,80) e deixa a rota de saida para
    # S2 passar por fora da avenida.
    "A": {"parede": "oeste", "porta": "S4", "hex": CORES_ZONA["A"],
          "trilho_interno": [(21.83, 0.00), (21.83, 3.40), (11.00, 3.40),
                             (11.00, 36.30)],
          "trilho_externo": [(25.03, 0.00), (25.03, 6.40), (14.00, 6.40),
                             (14.00, 36.30)]},
    # B sobe reta de S5 ate a banda norte. Nao distribui em pente: termina em T.
    "B": {"parede": "norte", "porta": "S5", "hex": CORES_ZONA["B"],
          "trilho_interno": [(26.80, 0.00), (26.80, 35.40)],
          "trilho_externo": [(29.80, 0.00), (29.80, 35.40)]},
    # C sai pelos 3 m oeste de S6 -- a leste de x = 35,09 esta o recuo da
    # preferencial S7 -- e abre para a banda leste.
    "C": {"parede": "leste", "porta": "S6", "hex": CORES_ZONA["C"],
          "trilho_interno": [(32.00, 0.00), (32.00, 3.20), (33.50, 5.20),
                             (33.50, 39.50)],
          "trilho_externo": [(35.00, 0.00), (35.00, 3.20), (36.50, 5.20),
                             (36.50, 39.50)]},
}
# Distancia da parede ate o trilho mais proximo da avenida daquela parede: e o
# que sobra para o modulo (4,10), o serpenteado (4,20) e a circulacao de saida.
BANDA_PAREDE = {"oeste": 11.00, "norte": 9.00, "leste": 10.80}
# O T da parede norte: a avenida B chega perpendicular e tem de distribuir para
# os dois lados. E o unico ponto do salao onde todo o fluxo de uma entrada passa
# por um so metro quadrado.
DISTRIBUIDOR_NORTE = [(10.20, 35.40), (42.30, 35.40)]
BOCA_PROF = 6.00      # trecho de cada trilho de avenida barreirado junto a porta
BOCA_SAIDA = 8.00     # trilho que protege a boca de cada saida (S2, S8)
CANAL_PREF = 10.00    # canal da entrada preferencial S7


def serpenteado_trilhos(s):
    """Os 3 trilhos de um serpenteado de 2 raias na frente de uma vermelha."""
    x1, y1, x2, y2 = s["rect"]
    prof = s["profundidade"]
    if s["parede"] == "oeste":      # cresce em +x, raias ao longo de y
        return [[(x1, y1 + i * s["passo_raia"]), (x1 + prof, y1 + i * s["passo_raia"])]
                for i in range(3)]
    if s["parede"] == "leste":      # cresce em -x
        return [[(x2, y1 + i * s["passo_raia"]), (x2 - prof, y1 + i * s["passo_raia"])]
                for i in range(3)]
    return [[(x1 + i * s["passo_raia"], y2), (x1 + i * s["passo_raia"], y2 - prof)]
            for i in range(3)]


def _recorta(pts, L):
    """Os primeiros L metros de uma polilinha, a partir do primeiro ponto."""
    saida, resta = [pts[0]], L
    for a, b in zip(pts, pts[1:]):
        seg = math.dist(a, b)
        if resta <= seg:
            u = resta / seg
            saida.append((a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u))
            return saida
        saida.append(b)
        resta -= seg
    return saida


def catalogo(planta, dec, mesas):
    """Todo trecho de barreira que o desenho gostaria de ter, com o seu preco."""
    itens = {}

    # A boca de cada avenida: os primeiros BOCA_PROF metros dos dois trilhos,
    # a partir da porta. As tres portas sao contiguas -- 0,29 m de alvenaria
    # entre S4|S5 e entre S5|S6 -- e quem entra pela porta errada nao se perde:
    # e conduzido ate a parede errada. A boca e o que impede isso.
    for aid, av in AVENIDAS.items():
        for lado in ("interno", "externo"):
            itens[f"boca_{aid}_{lado[:3]}"] = {
                "grupo": "boca", "entrada": aid, "hex": av["hex"],
                "rotulo": f"boca da avenida {aid} ({av['porta']}) · trilho {lado}",
                "trilhos": [_recorta(av[f"trilho_{lado}"], BOCA_PROF)],
            }

    for aid, av in AVENIDAS.items():
        itens[f"avenida_{aid}_int"] = {
            "grupo": "avenida", "entrada": aid, "hex": av["hex"],
            "rotulo": f"avenida {aid} · trilho do lado da parede",
            "trilhos": [av["trilho_interno"]],
        }
        itens[f"avenida_{aid}_ext"] = {
            "grupo": "avenida", "entrada": aid, "hex": av["hex"],
            "rotulo": f"avenida {aid} · trilho do lado do campo de retorno",
            "trilhos": [av["trilho_externo"]],
        }
    itens["distribuidor_norte"] = {
        "grupo": "cruzamento", "entrada": "B", "hex": "#e08a00",
        "rotulo": "distribuidor da parede norte — o T em que a avenida B desemboca",
        "trilhos": [DISTRIBUIDOR_NORTE],
    }

    itens["trilho_sul_A"] = {
        "grupo": "cruzamento", "entrada": "A", "hex": "#2a78d6",
        "rotulo": "trilho sul da perna A — separa a entrada da saída S2 e do recuo S3",
        "trilhos": [[(11.00, 3.40), (25.03, 3.40)]],
    }
    for pid, x1, x2 in (("S2", 13.25, 14.45), ("S8", 42.12, 43.32)):
        itens[f"boca_saida_{pid}"] = {
            "grupo": "cruzamento", "entrada": None, "hex": "#5b6470",
            "rotulo": f"boca da saída {pid} — protege quem sai de quem entra",
            "trilhos": [[(x1 - 0.6, 0.0), (x1 - 0.6, BOCA_SAIDA)],
                        [(x2 + 0.6, 0.0), (x2 + 0.6, BOCA_SAIDA)]],
        }
    itens["canal_S7"] = {
        "grupo": "cruzamento", "entrada": None, "hex": "#1e8449",
        "rotulo": "canal da entrada preferencial S7",
        "trilhos": [[(38.09 - 0.6, 0.0), (38.09 - 0.6, CANAL_PREF)],
                    [(39.36 + 0.6, 0.0), (39.36 + 0.6, CANAL_PREF)]],
    }

    for s in dec["serpenteados"]:
        m = next(x for x in mesas if x["mrv"] == s["mrv"])
        itens[f"serp_{s['mrv']}"] = {
            "grupo": "vermelha", "entrada": m["entrada"], "hex": "#c0392b",
            "rotulo": f"serpenteado do grupo {m['grupo']} · seções "
                      f"{' · '.join(str(x) for x in m['grupo_secoes'])} "
                      f"({s['pessoas']:.0f} pessoas)",
            "trilhos": serpenteado_trilhos(s),
        }

    for m in mesas:
        if m["classe"] == "alta":
            continue                      # ja tem serpenteado
        fx, fy = frente(m, planta)
        bx, by = boca_avenida(m, planta)
        itens[f"cabeca_{m['eleitor']}"] = {
            "grupo": "cabeca_" + m["classe"], "entrada": m["entrada"], "hex": m["cor"],
            "rotulo": f"cabeça de fila · grupo {m['grupo']} · seções "
                      f"{' · '.join(str(x) for x in m['secoes'])} "
                      f"({m['esperado']} esperados)",
            "trilhos": [[(fx, fy), (bx, by)]],
        }

    for k, it in itens.items():
        it["metros"] = round(sum(comp(t) for t in it["trilhos"]), 2)
        it["postes"] = sum(postes(comp(t)) for t in it["trilhos"])
    return itens


# --------------------------------------------------------------------------
# As tres opcoes
# --------------------------------------------------------------------------
def opcoes(itens, mesas):
    amarelas = [m["eleitor"] for m in mesas if m["classe"] == "media"]
    verdes = [m["eleitor"] for m in mesas if m["classe"] == "baixa"]
    # As verdes entram por carga esperada decrescente ate o orcamento acabar.
    ordem_verde = [m["eleitor"] for m in
                   sorted((m for m in mesas if m["classe"] == "baixa"),
                          key=lambda m: -m["esperado"])]

    bocas = [f"boca_{a}_{l}" for a in "ABC" for l in ("int", "ext")]
    op1 = ["boca_A_int", "boca_C_ext", "avenida_A_ext",
           "avenida_B_int", "avenida_B_ext", "avenida_C_int"]
    op2 = (["serp_22", "serp_23", "serp_24"]
           + [f"cabeca_{e}" for e in amarelas]
           + [f"cabeca_{e}" for e in ordem_verde[:8]])
    # A avenida B entra inteira, entao a sua boca ja esta dentro dela: contar as
    # duas seria contar os primeiros 6 m duas vezes.
    op3 = [b for b in bocas if "_B_" not in b] + [
        "avenida_B_int", "avenida_B_ext", "serp_22", "serp_23", "serp_24"]

    def monta(nome, subtitulo, doutrina, chaves, aposta, risco):
        usados = sum(itens[k]["postes"] for k in chaves)
        return {"nome": nome, "subtitulo": subtitulo, "doutrina": doutrina,
                "itens": chaves, "postes": usados, "reserva": UNIFILAS - usados,
                "metros": round(sum(itens[k]["metros"] for k in chaves), 1),
                "aposta": aposta, "risco": risco}

    return [
        monta("Opção 1", "As três avenidas",
              "A barreira paga o trajeto: canaliza o caminho inteiro da porta até a "
              "banda da parede e deixa as cabeças de fila na fita.",
              op1,
              "Um eleitor mal encaminhado custa mais do que um eleitor mal enfileirado: "
              "quem chega à parede errada volta atravessando o salão, contra o fluxo.",
              "Nada segura as três vermelhas. Os 20 em pé à frente de cada uma ficam "
              "contidos só por fita, que é justamente onde a fita não segura."),
        monta("Opção 2", "As cabeças de fila",
              "A barreira paga a contenção: vai onde as pessoas param de andar — as três "
              "vermelhas e as mesas de maior carga — e o trajeto inteiro fica na fita.",
              op2,
              "Pressão de multidão só existe onde a fila é estática. Corredor é fluxo "
              "andando, e fluxo andando obedece a linha pintada.",
              "A boca é o gargalo não paralelizável já identificado: 11,5 mil pessoas por "
              "18,4 m de porta, com as três correntes separadas apenas por fita."),
        monta("Definitiva", "Bocas, avenida B e as três vermelhas",
              "A barreira paga só o que a fita comprovadamente não faz: separar correntes "
              "que se cruzam e conter multidão parada.",
              op3,
              "Fita é uma fronteira que se vê; barreira é uma fronteira que custa "
              "atravessar. Gasta-se barreira onde atravessar compensa — na boca, no "
              "cruzamento e na cabeça da fila cheia.",
              "Depois dos 6 m de boca, as avenidas A e C ficam na fita, e sobram 2 "
              "unifilas de reserva. Se o corte de caminho aparecer, 2 postes não "
              "respondem: é por isso que as 15 adicionais deixam de ser folga."),
    ]



# --------------------------------------------------------------------------
# A fita: tudo o que o tracado pede e a barreira nao cobre
# --------------------------------------------------------------------------
# A fita e comprada em rolo, e rolo tem cor. Por isso a conta util nao e
# "metros de fita", e "metros de cada cor" -- e quem compra precisa do segundo.
CORES_FITA = {
    "A": {"rotulo": "azul · zona A / parede oeste (em estoque)", "hex": CORES_ZONA["A"]},
    "B": {"rotulo": "amarelo · zona B / parede norte (em estoque)", "hex": CORES_ZONA["B"]},
    "C": {"rotulo": "laranja · zona C / parede leste (em estoque)", "hex": CORES_ZONA["C"]},
    # Amarelo virou cor de zona: a linha de espera NAO pode mais ser amarela.
    "espera": {"rotulo": "zebrado preto-e-branco · linha de espera", "hex": "#16202b"},
    "pref": {"rotulo": "verde · preferencial S7", "hex": "#1e8449"},
    "neutro": {"rotulo": "branco · rota de saída", "hex": "#8a94a6"},
}
ROLO = 50.0           # metros por rolo de fita de marcacao de piso
RETOQUE = 0.10        # margem para o retoque do meio-dia e perdas de corte
GALAO = 0.90          # fita por galao (chevron) pintado no eixo da avenida
PASSO_GALAO = 5.00    # um galao a cada 5 m
SETAS_SAIDA = 40      # galoes de saida espalhados pelo campo livre


def cor_do_item(chave, itens, mesas):
    """A cor de rolo em que cada trecho do tracado e pintado, se for fita."""
    it = itens[chave]
    if chave.startswith(("divisor_", "trilho_sul", "boca_saida")):
        return "neutro"
    if chave == "canal_S7":
        return "pref"
    return it["entrada"] or "neutro"


def fita(op, itens, mesas, planta):
    """Metros de fita por cor, para uma opcao. Fita e o complemento da barreira.

    Todo trecho do tracado existe no chao de um jeito ou de outro: o que a
    barreira nao cobre, a fita cobre. Somam-se depois os elementos que sao
    sempre fita -- o lado livre de cada ramal, a linha de espera, as marcas de
    0,65 m, os galoes e a sinalizacao de saida.
    """
    por_cor = {c: 0.0 for c in CORES_FITA}
    ativos = set(op["itens"])

    # 1. o que a barreira nao levou
    for chave, it in itens.items():
        if chave in ativos:
            continue
        if chave.startswith("cabeca_"):
            continue            # tratado no bloco dos ramais, abaixo
        por_cor[cor_do_item(chave, itens, mesas)] += it["metros"]

    # 2. os ramais das 28 mesas: canal de 1,10 m, dois lados. O comprimento do
    # ramal e a banda DAQUELA parede menos o modulo -- 6,90 na oeste, 4,90 na
    # norte, 6,70 na leste --, nao um valor unico.
    ramal = {p_: BANDA_PAREDE[p_] - planta["modulo"]["prof"] for p_ in BANDA_PAREDE}
    for m in mesas:
        chave = f"cabeca_{m['eleitor']}"
        # um lado vira barreira so quando aquela cabeca esta na opcao
        lados = 1 if chave in ativos else 2
        por_cor[m["entrada"]] += lados * ramal[m["parede"]]

    # 3. sempre fita: linha de espera, marcas de fila, galoes, setas de saida
    for m in mesas:
        n_marcas = int(round((ramal[m["parede"]] - RECUO_MESA) / PASSO_FILA))
        por_cor["espera"] += LARG_CANAL
        por_cor[m["entrada"]] += n_marcas * 0.25
    for aid, av in AVENIDAS.items():
        eixo = (comp(av["trilho_interno"]) + comp(av["trilho_externo"])) / 2
        por_cor[aid] += int(eixo / PASSO_GALAO) * GALAO
    por_cor["neutro"] += SETAS_SAIDA * GALAO

    por_cor = {c: round(v, 1) for c, v in por_cor.items()}
    total = round(sum(por_cor.values()), 1)
    com_retoque = {c: round(v * (1 + RETOQUE), 1) for c, v in por_cor.items()}
    rolos = {c: math.ceil(v / ROLO) for c, v in com_retoque.items()}
    return {"por_cor": por_cor, "com_retoque": com_retoque, "rolos": rolos,
            "total": total, "total_com_retoque": round(total * (1 + RETOQUE), 1),
            "rolos_total": sum(rolos.values())}

# --------------------------------------------------------------------------
# Conferencia: a regra de 17/09
# --------------------------------------------------------------------------
def confere(dec):
    """As avenidas nao se cruzam, e nenhuma invade zona protegida.

    A separacao e provada pela faixa de x: cada avenida vive na sua, e as tres
    faixas sao disjuntas. Se algum dia a geometria mudar, isto quebra aqui e nao
    no dia da eleicao.
    """
    faltas = []
    faixas = {}
    for aid, av in AVENIDAS.items():
        xs = [p[0] for p in av["trilho_interno"] + av["trilho_externo"]]
        faixas[aid] = (min(xs), max(xs))
    for a, b in (("A", "B"), ("B", "C"), ("A", "C")):
        if not (faixas[a][1] < faixas[b][0] or faixas[b][1] < faixas[a][0]):
            faltas.append(f"avenidas {a} e {b} se cruzam: faixas {faixas[a]} e {faixas[b]}")

    protegidas = [(z["rect"], z["rotulo"]) for z in dec["zonas_protegidas"]]
    for aid, av in AVENIDAS.items():
        for lado in ("trilho_interno", "trilho_externo"):
            pts = av[lado]
            for a, b in zip(pts, pts[1:]):       # amostra o segmento
                n = max(2, int(math.dist(a, b) / 0.25))
                for i in range(n + 1):
                    t = i / n
                    x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
                    for (x1, y1, x2, y2), rot in protegidas:
                        if x1 - 1e-9 < x < x2 + 1e-9 and y1 - 1e-9 < y < y2 + 1e-9:
                            faltas.append(f"avenida {aid} ({lado}) entra em: {rot}")
    return faixas, sorted(set(faltas))


# --------------------------------------------------------------------------
# Desenho
# --------------------------------------------------------------------------
S = 15.0          # px por metro
MARG_E, MARG_T = 52, 92
LEGENDA = 278


def svg_plano(planta, dec, mesas, itens, op, grupos, titulo_extra=""):
    LARG, ALT = planta["salao"]["largura"], planta["salao"]["altura"]
    W = MARG_E * 2 + LARG * S + LEGENDA
    H = MARG_T + 46 + ALT * S
    px = lambda x, y: (MARG_E + x * S, MARG_T + (ALT - y) * S)
    o = []
    add = o.append

    add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.0f}" height="{H:.0f}" '
        f'viewBox="0 0 {W:.0f} {H:.0f}" font-family="Inter, Helvetica, Arial, sans-serif">')
    add(f'<rect width="{W:.0f}" height="{H:.0f}" fill="#fbfaf8"/>')
    add('<defs>'
        '<pattern id="prot" width="7" height="7" patternTransform="rotate(45)" '
        'patternUnits="userSpaceOnUse">'
        '<line x1="0" y1="0" x2="0" y2="7" stroke="#c0392b" stroke-width="1.1" '
        'stroke-opacity=".28"/></pattern>'
        '<marker id="seta" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" '
        'markerHeight="6" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/>'
        '</marker></defs>')

    add(f'<text x="{MARG_E}" y="34" font-size="21" font-weight="700" fill="#16202b">'
        f'{op["nome"]} · {op["subtitulo"]}</text>')
    saldo = (f'{op["reserva"]} em reserva móvel' if op["reserva"] >= 0
             else f'<tspan fill="#c0392b">não cabe: faltam {-op["reserva"]} unidades</tspan>')
    add(f'<text x="{MARG_E}" y="56" font-size="12.5" fill="#5b6470">'
        f'{op["postes"]} unifilas em barreira ({op["metros"]:.0f} m de cinta esticada) '
        f'de {UNIFILAS} orçadas · {saldo}{titulo_extra}</text>')
    fi = op.get("fita")
    if fi:
        add(f'<text x="{MARG_E}" y="78" font-size="12.5" fill="#5b6470">'
            f'Todo o resto em fita no chão: <tspan font-weight="700">{fi["total"]:.0f} m</tspan>'
            f' — {fi["total_com_retoque"]:.0f} m com o retoque do meio-dia, '
            f'{fi["rolos_total"]} rolos de 50 m repartidos em 6 cores</text>')

    # salao
    cont = " ".join(f"{px(x, y)[0]:.1f},{px(x, y)[1]:.1f}" for x, y in planta["salao"]["contorno"])
    add(f'<polygon points="{cont}" fill="#ffffff" stroke="#16202b" stroke-width="2"/>')

    # zonas protegidas e sala de apoio
    for z in dec["zonas_protegidas"]:
        x1, y1, x2, y2 = z["rect"]
        a, b = px(x1, y2)
        cor = "#8a94a6" if z["tipo"] == "sala_apoio" else "url(#prot)"
        add(f'<rect x="{a:.1f}" y="{b:.1f}" width="{(x2-x1)*S:.1f}" height="{(y2-y1)*S:.1f}" '
            f'fill="{cor}" fill-opacity="{0.22 if z["tipo"]=="sala_apoio" else 1}" '
            f'stroke="#c0392b" stroke-opacity=".35" stroke-dasharray="3 3"/>')

    # bandas de secao (a faixa de 9 m de cada parede usada)
    bandas = [(0, 0, BANDA_PAREDE["oeste"], ALT),
              (0, ALT - BANDA_PAREDE["norte"], LARG, ALT),
              (47.3 - BANDA_PAREDE["leste"], 0, 47.3, ALT)]
    for x1, y1, x2, y2 in bandas:
        a, b = px(x1, y2)
        add(f'<rect x="{a:.1f}" y="{b:.1f}" width="{(x2-x1)*S:.1f}" height="{(y2-y1)*S:.1f}" '
            f'fill="#16202b" fill-opacity=".035"/>')

    # ---- fita no chao: avenidas e ramais ----
    ativos = set(op["itens"])
    for aid, av in AVENIDAS.items():
        for lado in ("trilho_interno", "trilho_externo"):
            chave = f"avenida_{aid}_{'int' if lado=='trilho_interno' else 'ext'}"
            if chave in ativos:
                continue
            pts = " ".join(f"{px(*p)[0]:.1f},{px(*p)[1]:.1f}" for p in av[lado])
            add(f'<polyline points="{pts}" fill="none" stroke="{av["hex"]}" stroke-width="2.4" '
                f'stroke-dasharray="9 6" stroke-opacity=".85" stroke-linejoin="round"/>')
        # seta de sentido no eixo da avenida
        p0 = av["trilho_interno"][-2] if len(av["trilho_interno"]) > 2 else av["trilho_interno"][0]
        p1 = av["trilho_interno"][-1]
        mx = ((p0[0] + p1[0]) / 2 + (av["trilho_externo"][-1][0] + av["trilho_externo"][-2][0]
                                     if len(av["trilho_externo"]) > 2 else 0)) if False else None
        cxm = (av["trilho_interno"][-1][0] + av["trilho_externo"][-1][0]) / 2
        ya, yb = (p0[1] + p1[1]) / 2, p1[1]
        a1, b1 = px(cxm, ya)
        a2, b2 = px(cxm, min(yb, ya + 5))
        add(f'<line x1="{a1:.1f}" y1="{b1:.1f}" x2="{a2:.1f}" y2="{b2:.1f}" '
            f'stroke="{av["hex"]}" stroke-width="3" marker-end="url(#seta)" opacity=".9"/>')

    # distribuidor da parede norte (fita, quando nao esta na barreira)
    if "distribuidor_norte" not in ativos:
        pts = " ".join(f"{px(*p)[0]:.1f},{px(*p)[1]:.1f}" for p in DISTRIBUIDOR_NORTE)
        add(f'<polyline points="{pts}" fill="none" stroke="#e08a00" stroke-width="2.4" '
            f'stroke-dasharray="9 6" stroke-opacity=".85"/>')

    # saidas: campo livre, so sinalizado. Setas cinza convergindo em S2 e S8.
    for (x0, y0), (x1, y1) in (((6.0, 9.0), (13.85, 2.0)), ((20.0, 30.0), (13.85, 2.0)),
                               ((36.0, 30.0), (42.7, 2.0)), ((44.0, 9.0), (42.7, 2.0))):
        a1, b1 = px(x0, y0)
        a2, b2 = px(x1, y1)
        add(f'<line x1="{a1:.1f}" y1="{b1:.1f}" x2="{a2:.1f}" y2="{b2:.1f}" '
            f'stroke="#8a94a6" stroke-width="1.6" stroke-dasharray="2 5" '
            f'marker-end="url(#seta)" opacity=".75"/>')

    # ramais e linha de espera de cada mesa (fita, sempre)
    for m in mesas:
        fx, fy = frente(m, planta)
        bx, by = boca_avenida(m, planta)
        perp = (-m["dy"], m["dx"])
        meia = LARG_CANAL / 2
        for sgn in (1, -1):
            p1 = px(bx + perp[0] * meia * sgn, by + perp[1] * meia * sgn)
            p2 = px(fx + perp[0] * meia * sgn, fy + perp[1] * meia * sgn)
            add(f'<line x1="{p1[0]:.1f}" y1="{p1[1]:.1f}" x2="{p2[0]:.1f}" y2="{p2[1]:.1f}" '
                f'stroke="{m["hex_entrada"]}" stroke-width="1.5" stroke-dasharray="5 4" '
                f'stroke-opacity=".7"/>')
        ex, ey = fx + m["dx"] * RECUO_MESA * -1, fy + m["dy"] * RECUO_MESA * -1
        e1 = px(ex + perp[0] * meia, ey + perp[1] * meia)
        e2 = px(ex - perp[0] * meia, ey - perp[1] * meia)
        add(f'<line x1="{e1[0]:.1f}" y1="{e1[1]:.1f}" x2="{e2[0]:.1f}" y2="{e2[1]:.1f}" '
            f'stroke="#16202b" stroke-width="3.4" stroke-dasharray="3 3"/>')

    # ---- modulos ----
    P, L = planta["modulo"]["prof"], planta["modulo"]["larg"] / 2
    for m in mesas:
        dxp, dyp = m["dx"], m["dy"]
        pxp, pyp = -dyp, dxp
        cantos = [(m["x"] + pxp * L, m["y"] + pyp * L),
                  (m["x"] - pxp * L, m["y"] - pyp * L),
                  (m["x"] - pxp * L + dxp * P, m["y"] - pyp * L + dyp * P),
                  (m["x"] + pxp * L + dxp * P, m["y"] + pyp * L + dyp * P)]
        pts = " ".join(f"{px(*c)[0]:.1f},{px(*c)[1]:.1f}" for c in cantos)
        add(f'<polygon points="{pts}" fill="{m["cor"]}" fill-opacity=".92" '
            f'stroke="#16202b" stroke-width=".7"/>')
        # Rotulo por GRUPO e por SECAO -- nunca por numero de mesa. E a convencao
        # do artefato de sinalizacao: "Nenhum traz numero de mesa: so as secoes".
        gx, gy = px(m["x"] + dxp * P / 2, m["y"] + dyp * P / 2)
        giro = -90 if m["rot"] == 270 else 0
        trg = f' transform="rotate({giro} {gx:.1f} {gy+4:.1f})"' if giro else ""
        add(f'<text x="{gx:.1f}" y="{gy+4:.1f}" font-size="11.5" font-weight="800" '
            f'fill="#fff" text-anchor="middle"{trg}>{m["grupo"]}</text>')

    # ---- marcador de grupo: onde vai o x-banner, com as secoes do grupo ----
    # 4,60 m da LINHA DAS MESAS (parede oeste x=0, norte y=44,4, leste x=47,3).
    # O sinalizacao_v2.json traz 45,7 para a leste, medido dos 50,3 da fachada:
    # isso joga o x-banner dentro da faixa de emergencia. Aqui fica 42,70.
    for g in grupos:
        eixo = sum(g["coord"]) / len(g["coord"])
        # Achado: nos tres grupos vermelhos os 4,60 m caem DENTRO do serpenteado
        # (4,10 a 8,30 da parede). Nesses, o x-banner recua para 8,60 m.
        rec = 8.60 if g["classe"] == "alta" else 4.60
        if g["parede"] == "oeste":
            bx, by, anc = rec, eixo, "start"
        elif g["parede"] == "norte":
            bx, by, anc = eixo, 44.4 - rec, "middle"
        else:
            bx, by, anc = 47.3 - rec, eixo, "end"
        a, b = px(bx, by)
        cor = CORES_ZONA[g["entrada"]]
        escuro = g["entrada"] != "B"
        larg, alt = 68, 26
        rx = a if anc == "start" else (a - larg if anc == "end" else a - larg / 2)
        add(f'<rect x="{rx:.1f}" y="{b-alt/2:.1f}" width="{larg}" height="{alt}" rx="4" '
            f'fill="{cor}" stroke="#16202b" stroke-width=".8"/>')
        tc = "#ffffff" if escuro else "#16202b"
        add(f'<text x="{rx+6:.1f}" y="{b-1:.1f}" font-size="12" font-weight="800" '
            f'fill="{tc}">{g["id"]}</text>')
        add(f'<text x="{rx+6:.1f}" y="{b+9:.1f}" font-size="6.6" font-weight="600" '
            f'fill="{tc}" fill-opacity=".9">'
            f'{" ".join(str(x) for x in g["secoes"])}</text>')

    # ---- portas ----
    for p in planta["portas"]:
        sin = dec["sinalizacao_portas"].get(p["id"], {})
        papel = sin.get("papel", "livre")
        cor = {"entrada": CORES_ZONA.get(sin.get("entrada"), "#8a94a6"),
               "saida": "#5b6470", "emergencia": "#c0392b", "preferencial": "#1e8449",
               "fechada": "#b9bfc9", "livre": "#b9bfc9"}[papel]
        a1, b1 = px(p["x1"], p["y1"])
        a2, b2 = px(p["x2"], p["y2"])
        add(f'<line x1="{a1:.1f}" y1="{b1:.1f}" x2="{a2:.1f}" y2="{b2:.1f}" '
            f'stroke="{cor}" stroke-width="6" stroke-linecap="butt"/>')
        if papel in ("entrada", "saida", "preferencial"):
            mx, my = (a1 + a2) / 2, (b1 + b2) / 2
            rot_t = -90 if p["face"] in ("leste", "oeste") else 0
            tr = f' transform="rotate({rot_t} {mx:.1f} {my:.1f})"' if rot_t else ""
            add(f'<text x="{mx:.1f}" y="{my+16:.1f}" font-size="10.5" font-weight="700" '
                f'fill="{cor}" text-anchor="middle"{tr}>{p["id"]}</text>')

    # ---- barreira ----
    for k in op["itens"]:
        it = itens[k]
        for t in it["trilhos"]:
            pts = " ".join(f"{px(*p)[0]:.1f},{px(*p)[1]:.1f}" for p in t)
            add(f'<polyline points="{pts}" fill="none" stroke="#16202b" stroke-width="5.4" '
                f'stroke-linejoin="round" stroke-linecap="round"/>')
            pts2 = " ".join(f"{px(*p)[0]:.1f},{px(*p)[1]:.1f}" for p in t)
            add(f'<polyline points="{pts2}" fill="none" stroke="{it["hex"]}" '
                f'stroke-width="2.6" stroke-linejoin="round" stroke-linecap="round"/>')
            # os postes
            Lt = comp(t)
            n = postes(Lt)
            for i in range(n):
                f_ = 0 if n == 1 else i / (n - 1)
                d = f_ * Lt
                # caminha pela polilinha
                rest, ponto = d, t[0]
                for j in range(len(t) - 1):
                    seg = math.dist(t[j], t[j + 1])
                    if rest <= seg or j == len(t) - 2:
                        u = 0 if seg == 0 else rest / seg
                        ponto = (t[j][0] + (t[j + 1][0] - t[j][0]) * u,
                                 t[j][1] + (t[j + 1][1] - t[j][1]) * u)
                        break
                    rest -= seg
                a, b = px(*ponto)
                add(f'<circle cx="{a:.1f}" cy="{b:.1f}" r="3.1" fill="#16202b"/>')

    # ---- legenda ----
    lx = MARG_E + LARG * S + 26
    ly = MARG_T + 6
    add(f'<text x="{lx}" y="{ly}" font-size="12" font-weight="700" fill="#16202b" '
        f'letter-spacing=".08em">O QUE VAI NA BARREIRA</text>')
    ly += 20
    # Grupos com muitos trechos iguais entram numa linha so, para a legenda caber.
    entradas_leg, vistos = [], set()
    for k in op["itens"]:
        it = itens[k]
        g = it["grupo"]
        irmaos = [j for j in op["itens"] if itens[j]["grupo"] == g]
        # So as cabecas de fila colapsam: sao dezenas de trechos iguais. Os
        # trilhos de avenida nao, porque e justamente *quais* deles entram que
        # distingue uma opcao da outra.
        if not g.startswith("cabeca_") or len(irmaos) <= 3:
            entradas_leg.append((it["hex"], it["rotulo"], it["metros"], it["postes"]))
            continue
        if g in vistos:
            continue
        vistos.add(g)
        rot = {"cabeca_media": "cabeça de fila das 8 mesas amarelas",
               "cabeca_baixa": f"cabeça de fila de {len(irmaos)} mesas verdes",
               }.get(g, f"{g} ({len(irmaos)} trechos)")
        entradas_leg.append((itens[irmaos[0]]["hex"], rot,
                             sum(itens[j]["metros"] for j in irmaos),
                             sum(itens[j]["postes"] for j in irmaos)))
    for hexe, rot, metros, pst in entradas_leg:
        add(f'<line x1="{lx}" y1="{ly-4:.0f}" x2="{lx+20}" y2="{ly-4:.0f}" stroke="#16202b" '
            f'stroke-width="5"/>')
        add(f'<line x1="{lx}" y1="{ly-4:.0f}" x2="{lx+20}" y2="{ly-4:.0f}" '
            f'stroke="{hexe}" stroke-width="2.4"/>')
        add(f'<text x="{lx+28}" y="{ly}" font-size="10.6" fill="#31404f">{rot[:58]}</text>')
        add(f'<text x="{lx+28}" y="{ly+12}" font-size="10" fill="#8a94a6">'
            f'{metros:.1f} m · {pst} unifilas</text>')
        ly += 30
    ly += 8
    add(f'<line x1="{lx}" y1="{ly-14:.0f}" x2="{lx+210}" y2="{ly-14:.0f}" stroke="#dcdde1"/>')
    add(f'<text x="{lx}" y="{ly}" font-size="12" font-weight="700" fill="#16202b" '
        f'letter-spacing=".08em">O QUE VAI NA FITA</text>')
    ly += 18
    for cor, txt in ((None, "avenidas não barreiradas — 2 linhas a 3,00 m"),
                     (None, "28 ramais de mesa — canal de 1,10 m"),
                     ("#16202b", "linha de espera a 1,50 m — zebrado, nunca amarelo"),
                     (None, "papel da seção, colado fora da linha de pisada"),
                     ("#8a94a6", "saída: campo livre, só sinalizado")):
        traco = "" if cor else ' stroke-dasharray="6 4"'
        add(f'<line x1="{lx}" y1="{ly-4:.0f}" x2="{lx+20}" y2="{ly-4:.0f}" '
            f'stroke="{cor or "#8a94a6"}" stroke-width="{3 if cor else 2}"{traco}/>')
        add(f'<text x="{lx+28}" y="{ly}" font-size="10.6" fill="#31404f">{txt}</text>')
        ly += 19
    ly += 14
    add(f'<line x1="{lx}" y1="{ly-14:.0f}" x2="{lx+210}" y2="{ly-14:.0f}" stroke="#dcdde1"/>')
    for i, cl in enumerate(("alta", "media", "baixa")):
        c = dec["classes"]["cores"][cl]
        add(f'<rect x="{lx}" y="{ly-9:.0f}" width="13" height="11" fill="{c["hex"]}"/>')
        add(f'<text x="{lx+20}" y="{ly}" font-size="10.6" fill="#31404f">'
            f'{c["rotulo"]} ({dec["classes"]["contagem"][cl]})</text>')
        ly += 18
    ly += 10
    add(f'<text x="{lx}" y="{ly}" font-size="10.2" fill="#8a94a6">A aposta</text>')
    ly += 14
    for linha in quebra(op["aposta"], 42):
        add(f'<text x="{lx}" y="{ly}" font-size="10.4" fill="#31404f">{linha}</text>')
        ly += 13
    ly += 8
    add(f'<text x="{lx}" y="{ly}" font-size="10.2" fill="#8a94a6">O risco</text>')
    ly += 14
    for linha in quebra(op["risco"], 42):
        add(f'<text x="{lx}" y="{ly}" font-size="10.4" fill="#c0392b">{linha}</text>')
        ly += 13

    add(f'<text x="{MARG_E}" y="{H-14:.0f}" font-size="10" fill="#8a94a6">'
        f'Hall 2 · RDS Ballsbridge · cenário Paredes_ABC · escala 1 m = {S:.0f} px · '
        f'poste a {VAO_POSTE:.2f} m (cinta de {CINTA:.2f} m esticada a 90%)</text>')
    add('</svg>')
    return "\n".join(o)


def quebra(txt, n):
    linhas, atual = [], ""
    for w in txt.split():
        if len(atual) + len(w) + 1 > n:
            linhas.append(atual)
            atual = w
        else:
            atual = (atual + " " + w).strip()
    if atual:
        linhas.append(atual)
    return linhas


# --------------------------------------------------------------------------
# Desenho de detalhe: da barreira à mesa
# --------------------------------------------------------------------------
def virg(v):
    return f"{v:.2f}".replace(".", ",")


def svg_detalhe(mesas, dec):
    AZUL = CORES_ZONA["A"]
    """Corte ampliado do ramal: onde a barreira acaba e a fita leva ate a mesa."""
    E = 56.0                     # px por metro
    ox, oy = 104, 176            # origem do desenho (parede, y = 0)
    W, H = 1180, 590
    px = lambda x, y: (ox + x * E, oy + y * E)
    o = []
    add = o.append

    banda = BANDA_PAREDE["oeste"]
    mod, espera, avenida = 4.10, 4.10 + RECUO_MESA, banda + LARG_AVENIDA
    lat = 4.20                                   # extensao lateral desenhada
    meio = lat / 2
    y1, y2 = meio - LARG_CANAL / 2, meio + LARG_CANAL / 2

    add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" font-family="Inter, Helvetica, Arial, sans-serif">')
    add(f'<rect width="{W}" height="{H}" fill="#fbfaf8"/>')
    add('<defs><marker id="s2" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" '
        'markerHeight="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#33507E"/>'
        '</marker></defs>')
    add(f'<text x="{ox}" y="46" font-size="22" font-weight="700" fill="#16202b">'
        f'Do fim da barreira até a mesa — o ramal, em escala</text>')
    add(f'<text x="{ox}" y="72" font-size="13" fill="#5b6470">'
        f'Vale igual nas três paredes. Aqui a parede oeste: a mesa à esquerda, a avenida '
        f'à direita, {virg(banda)} m entre uma e outra.</text>')
    add(f'<text x="{ox}" y="94" font-size="13" fill="#5b6470">'
        f'A barreira pára na boca do ramal. Da boca até a mesa, quem manda é a fita — e é '
        f'por isso que a linha de espera tem de ser inconfundível.</text>')

    # parede e vizinhas
    a, b = px(0, 0)
    add(f'<rect x="{a-18:.0f}" y="{b:.0f}" width="18" height="{lat*E:.0f}" fill="#16202b"/>')
    add(f'<text x="{a-30:.0f}" y="{px(0,meio)[1]:.0f}" font-size="11.5" fill="#16202b" '
        f'text-anchor="middle" letter-spacing=".1em" '
        f'transform="rotate(-90 {a-30:.0f} {px(0,meio)[1]:.0f})">PAREDE</text>')
    for yy, txt in ((0.05, "mesa vizinha"), (lat - 0.50, "mesa vizinha")):
        a, b = px(0, yy)
        add(f'<rect x="{a:.0f}" y="{b:.0f}" width="{mod*E:.0f}" height="{0.45*E:.0f}" '
            f'fill="#8a94a6" fill-opacity=".28" stroke="#8a94a6" stroke-dasharray="4 3"/>')
        add(f'<text x="{a+10:.0f}" y="{b+21:.0f}" font-size="10.5" fill="#6b7686">{txt}</text>')

    # o modulo desta secao
    a, b = px(0, meio - 0.45)
    add(f'<rect x="{a:.0f}" y="{b:.0f}" width="{mod*E:.0f}" height="{0.9*E:.0f}" '
        f'fill="#1e8449" fill-opacity=".92" stroke="#16202b"/>')
    add(f'<text x="{px(mod/2, meio)[0]:.0f}" y="{px(mod/2, meio)[1]+5:.0f}" font-size="13" '
        f'font-weight="700" fill="#fff" text-anchor="middle">MESA + URNA · 4,10 m</text>')

    # avenida
    a, b = px(banda, 0)
    add(f'<rect x="{a:.0f}" y="{b:.0f}" width="{LARG_AVENIDA*E:.0f}" height="{lat*E:.0f}" '
        f'fill="{AZUL}" fill-opacity=".07"/>')
    p1, p2 = px(banda + LARG_AVENIDA / 2, lat - 0.15), px(banda + LARG_AVENIDA / 2, 0.15)
    add(f'<line x1="{p1[0]:.0f}" y1="{p1[1]:.0f}" x2="{p2[0]:.0f}" y2="{p2[1]:.0f}" '
        f'stroke="{AZUL}" stroke-width="3.2" marker-end="url(#s2)" opacity=".75"/>')
    add(f'<text x="{px(avenida+0.18, 0.55)[0]:.0f}" y="{px(avenida+0.18, 0.55)[1]:.0f}" '
        f'font-size="12.5" font-weight="700" fill="{AZUL}">AVENIDA · 3,00 m</text>')
    add(f'<text x="{px(avenida+0.18, 0.55)[0]:.0f}" y="{px(avenida+0.18, 0.55)[1]+17:.0f}" '
        f'font-size="11" fill="#5b6470">sentido único, na cor da entrada</text>')

    # barreira: dois trechos, com o vao do ramal entre eles
    for ya, yb in ((0.0, y1), (y2, lat)):
        p1, p2 = px(banda, ya), px(banda, yb)
        add(f'<line x1="{p1[0]:.0f}" y1="{p1[1]:.0f}" x2="{p2[0]:.0f}" y2="{p2[1]:.0f}" '
            f'stroke="#16202b" stroke-width="8" stroke-linecap="round"/>')
        for yy in (ya, yb):
            a, b = px(banda, yy)
            add(f'<circle cx="{a:.0f}" cy="{b:.0f}" r="6.5" fill="#16202b"/>')
            add(f'<circle cx="{a:.0f}" cy="{b:.0f}" r="2.4" fill="#fbfaf8"/>')
    add(f'<text x="{px(banda, 0)[0]:.0f}" y="{px(banda,0)[1]-34:.0f}" font-size="12.5" '
        f'font-weight="700" fill="#16202b" text-anchor="middle">BARREIRA</text>')
    add(f'<text x="{px(banda, 0)[0]:.0f}" y="{px(banda,0)[1]-18:.0f}" font-size="11" '
        f'fill="#5b6470" text-anchor="middle">postes a 1,80 m · o vão do ramal é o único</text>')

    # canal de fita: da boca ate a linha de espera
    for yy in (y1, y2):
        p1, p2 = px(espera, yy), px(banda, yy)
        add(f'<line x1="{p1[0]:.0f}" y1="{p1[1]:.0f}" x2="{p2[0]:.0f}" y2="{p2[1]:.0f}" '
            f'stroke="{AZUL}" stroke-width="5" stroke-dasharray="15 10"/>')
    n = int(round((banda - espera) / PASSO_FILA))
    for i in range(1, n + 1):
        xx = espera + i * PASSO_FILA
        p1, p2 = px(xx, y1 + 0.02), px(xx, y1 + 0.24)
        add(f'<line x1="{p1[0]:.0f}" y1="{p1[1]:.0f}" x2="{p2[0]:.0f}" y2="{p2[1]:.0f}" '
            f'stroke="{AZUL}" stroke-width="3" stroke-opacity=".5"/>')
    p = px((banda + espera) / 2 + 0.25, y1 - 0.14)
    add(f'<text x="{p[0]:.0f}" y="{p[1]:.0f}" font-size="11.5" fill="{AZUL}" '
        f'text-anchor="middle">canal de 1,10 m · marcas de 0,65 m: {n} marcas = {n} pessoas</text>')

    # linha de espera
    p1, p2 = px(espera, y1 - 0.30), px(espera, y2 + 0.30)
    add(f'<line x1="{p1[0]:.0f}" y1="{p1[1]:.0f}" x2="{p2[0]:.0f}" y2="{p2[1]:.0f}" '
        f'stroke="#16202b" stroke-width="10" stroke-dasharray="7 7"/>')
    p = px(espera, y2 + 0.52)
    add(f'<text x="{p[0]:.0f}" y="{p[1]:.0f}" font-size="12.5" font-weight="700" '
        f'fill="#16202b" text-anchor="middle">LINHA DE ESPERA</text>')
    add(f'<text x="{p[0]:.0f}" y="{p[1]+16:.0f}" font-size="11" fill="#5b6470" '
        f'text-anchor="middle">1,50 m da mesa — zebrado preto-e-branco, sigilo do voto</text>')
    add(f'<text x="{p[0]:.0f}" y="{p[1]+31:.0f}" font-size="11" fill="#5b6470" '
        f'text-anchor="middle">só passa quem o mesário chamar</text>')

    # o papel da secao, fora da linha de pisada
    a, b = px(banda - 2.05, y2 + 0.16)
    add(f'<rect x="{a:.0f}" y="{b:.0f}" width="{1.45*E:.0f}" height="{0.72*E:.0f}" '
        f'fill="#fff" stroke="#16202b" stroke-width="1.6"/>')
    add(f'<text x="{a+48:.0f}" y="{b+22:.0f}" font-size="15" font-weight="700" '
        f'fill="#16202b" text-anchor="middle">GRUPO A4</text>')
    add(f'<text x="{a+48:.0f}" y="{b+40:.0f}" font-size="11" fill="#5b6470" '
        f'text-anchor="middle">seções 513 · 1105</text>')
    nota = ("Papel plastificado, colado FORA da linha de pisada. No meio do canal ele "
            "some sob os pés e sob o corpo de quem está na frente: serve para confirmar, "
            "nunca para decidir.")
    nota2 = ("O número que decide vai no banner, à altura dos olhos — os banners já estão "
             "orçados (item c, EUR 1.961,00).")
    add(f'<text x="{ox}" y="{H-46}" font-size="11.5" fill="#6b7686">{nota}</text>')
    add(f'<text x="{ox}" y="{H-28}" font-size="11.5" fill="#6b7686">{nota2}</text>')

    # cotas
    def cota(x1_, x2_, yy, txt):
        p1, p2 = px(x1_, yy), px(x2_, yy)
        add(f'<line x1="{p1[0]:.0f}" y1="{p1[1]:.0f}" x2="{p2[0]:.0f}" y2="{p2[1]:.0f}" '
            f'stroke="#8a94a6" stroke-width="1"/>')
        for q in (p1, p2):
            add(f'<line x1="{q[0]:.0f}" y1="{q[1]-5:.0f}" x2="{q[0]:.0f}" y2="{q[1]+5:.0f}" '
                f'stroke="#8a94a6" stroke-width="1"/>')
        add(f'<text x="{(p1[0]+p2[0])/2:.0f}" y="{p1[1]-8:.0f}" font-size="11" '
            f'fill="#5b6470" text-anchor="middle">{txt}</text>')

    cota(0, mod, lat + 0.24, "4,10 — módulo")
    cota(mod, espera, lat + 0.24, "1,50")
    cota(espera, banda, lat + 0.24, f"{virg(banda-espera)} — fila de ~{n} pessoas")
    cota(0, banda, lat + 0.72, f"{virg(banda)} — banda da seção oeste")
    add('</svg>')
    return "\n".join(o)


# --------------------------------------------------------------------------
def main():
    grava = "--grava" in sys.argv
    planta, dec, cen = carrega()
    mesas = monta_mesas(planta, dec, cen)
    with open(os.path.join(RAIZ, "data", "grupos_mesas.json"), encoding="utf-8") as f:
        grupos = json.load(f)["grupos"]
    itens = catalogo(planta, dec, mesas)
    ops = opcoes(itens, mesas)
    for op in ops:
        op["fita"] = fita(op, itens, mesas, planta)

    faixas, faltas = confere(dec)
    print("\nAs avenidas não se cruzam — faixas de x, disjuntas:")
    for aid, (a, b) in faixas.items():
        print(f"    {aid}: {a:6.2f} .. {b:6.2f} m")
    if faltas:
        print("\nFALHAS:")
        for f in faltas:
            print("   ", f)
        sys.exit(1)
    print("    nenhuma avenida invade zona protegida\n")

    total_desejado = sum(i["postes"] for i in itens.values())
    print(f"\nCatálogo completo do desenho: {total_desejado} unifilas "
          f"({sum(i['metros'] for i in itens.values()):.0f} m de trilho)")
    print(f"Orçamento aprovado: {UNIFILAS} unifilas "
          f"({UNIFILAS/total_desejado*100:.0f}% do desejado, "
          f"EUR {UNIFILAS*PRECO_UNIFILA:,.2f})\n")
    for op in ops:
        print(f"  {op['nome']} — {op['subtitulo']}")
        fi = op["fita"]
        print(f"    barreira: {op['postes']} unifilas em {op['metros']:.0f} m · "
              f"reserva móvel {op['reserva']}")
        print(f"    fita:     {fi['total']:.0f} m ({fi['total_com_retoque']:.0f} m com "
              f"retoque) · {fi['rolos_total']} rolos de {ROLO:.0f} m")
        for c, v in fi["por_cor"].items():
            print(f"      {v:6.1f} m  {fi['rolos'][c]} rolo(s)  {CORES_FITA[c]['rotulo']}")
        for k in op["itens"]:
            print(f"      {itens[k]['postes']:>3}  {itens[k]['rotulo']}")
        print()

    if not grava:
        print("(sem --grava: nada foi escrito)")
        return

    os.makedirs(SAIDAS, exist_ok=True)
    for i, op in enumerate(ops, start=1):
        nome = "separadores_definitivo.svg" if op["nome"] == "Definitiva" \
            else f"separadores_opcao{i}.svg"
        caminho = os.path.join(SAIDAS, nome)
        with open(caminho, "w", encoding="utf-8") as f:
            f.write(svg_plano(planta, dec, mesas, itens, op, grupos))
        print("escrito", os.path.relpath(caminho, RAIZ))
    caminho = os.path.join(SAIDAS, "separadores_detalhe.svg")
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(svg_detalhe(mesas, dec))
    print("escrito", os.path.relpath(caminho, RAIZ))

    resumo = {
        "premissas": {"cinta_m": CINTA, "vao_poste_m": VAO_POSTE,
                      "unifilas_orcadas": UNIFILAS, "preco_unitario_eur": PRECO_UNIFILA,
                      "banda_por_parede_m": BANDA_PAREDE, "largura_avenida_m": LARG_AVENIDA,
                      "largura_canal_m": LARG_CANAL, "passo_fila_m": PASSO_FILA,
                      "linha_espera_m": RECUO_MESA, "rolo_fita_m": ROLO,
                      "retoque_fita": RETOQUE, "passo_galao_m": PASSO_GALAO},
        "catalogo": {k: {"rotulo": v["rotulo"], "grupo": v["grupo"],
                         "metros": v["metros"], "postes": v["postes"]}
                     for k, v in itens.items()},
        "catalogo_total_postes": total_desejado,
        "opcoes": ops,
    }
    caminho = os.path.join(SAIDAS, "separadores_fila.json")
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(resumo, f, ensure_ascii=False, indent=1)
    print("escrito", os.path.relpath(caminho, RAIZ))


if __name__ == "__main__":
    main()
