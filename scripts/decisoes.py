"""Fonte unica das decisoes de operacao do posto de Dublin (RDS Hall 2).

Ate 06/09/2026 cada peca carregava a sua copia das decisoes: papeis das
portas no simulador e no Ring 3, base de comparecimento em quatro scripts,
capacidade do Ring 3 digitada no simulador, atribuicao de urnas a entradas
num script solto, numeracao das mesas em tres sistemas. Mudar uma decisao
exigia editar quatro lugares. Agora a decisao mora aqui, e os geradores da
planta-base, da prancheta, do simulador, do Ring 3 e da sinalizacao leem
`montar()` (ou `data/decisoes.json`, que `gera_decisoes.py` grava dela).

Decisoes registradas (Posto, 06/09/2026):

  1. Comparecimento esperado: base B, taxa de 2022 por domicilio de origem
     (scripts/comparecimento.py).
  2. Numeracao das mesas: a do DJE/TRE-DF (MRV 1 a 28) e a unica identidade
     da mesa, na prancheta, no simulador e na sinalizacao. O numero nao
     depende da posicao: a mesa 22 e a 22 esteja ela na parede norte, leste
     ou oeste. A numeracao voltada ao eleitor (por distribuicao na parede)
     so entra depois que o cenario da prancheta for fechado.
  3. Cores por carga esperada: vermelho para as 3 mesas de maior
     comparecimento, amarelo para as de comparecimento medio, verde para as
     de baixo.
  4. Portas da fachada sul: entradas S4 (A), S5 (B) e S6 (C); saidas S2 e S8.
     Tomada durante o desenho do Ring 3 e em conversa com um colega.
  5. Nomenclatura das entradas para o eleitor (cor ou letra): SEM decisao.
"""
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "scripts"))

import comparecimento as CP                                   # noqa: E402

DECIDIDO_EM = "2026-09-06"
ARQUIVO = os.path.join(RAIZ, "data", "decisoes.json")

# ------------------------------------------------------------ portas ------
# Numeracao de fachada da planta-base (N1.., L1.., S1..S9, O1.., R1).
ENTRADAS = [("A", "S4"), ("B", "S5"), ("C", "S6")]
SAIDAS = ["S2", "S8"]
PAPEL_PORTA = {**{p: "entrada" for _, p in ENTRADAS}, **{p: "saida" for p in SAIDAS}}
ENTRADA_DA_PORTA = {p: e for e, p in ENTRADAS}
PORTA_DA_ENTRADA = dict(ENTRADAS)

# Cores das tres raias, do plano de sinalizacao (azul, ambar, magenta:
# distinguiveis em deuteranopia e protanopia). Sao cores de RAIA; se a
# placa da porta vai dizer a cor ou uma letra continua em aberto.
CORES_ENTRADA = {"A": ("azul", "#2a78d6"), "B": ("âmbar", "#e08a00"),
                 "C": ("magenta", "#c2185b")}

# ----------------------------------------------------- classes de carga ----
N_ALTA = 3               # as 3 mesas de maior comparecimento esperado
LIMIAR_MEDIA = 450       # esperado >= 450: media (amarelo); abaixo: baixa (verde)
CLASSES = {
    "alta":  {"cor": "vermelho", "hex": "#c0392b", "rotulo": "alto comparecimento"},
    "media": {"cor": "amarelo",  "hex": "#d4a017", "rotulo": "médio comparecimento"},
    "baixa": {"cor": "verde",    "hex": "#1e8449", "rotulo": "baixo comparecimento"},
}
ORDEM_CLASSES = ["alta", "media", "baixa"]

# ------------------------------------------------- MRV do DJE/TRE-DF -------
# MRV -> secao principal, transcrito do Diario da Justica Eletronico do
# TRE-DF, Ano 2026 n. 139 (04/08/2026), p. 915-921 (convocacao de mesarios,
# Irlanda/Dublin). Regra observada: MRV k e a k-esima secao principal em
# ordem crescente de numero.
MRV_SECAO_PRINCIPAL = {
    1: 511, 2: 512, 3: 513, 4: 517, 5: 1160, 6: 1352, 7: 3054, 8: 3078,
    9: 3108, 10: 3142, 11: 3161, 12: 3179, 13: 3216, 14: 3229, 15: 3245,
    16: 3302, 17: 3305, 18: 3306, 19: 3308, 20: 3309, 21: 3311, 22: 3313,
    23: 3315, 24: 3322, 25: 3442, 26: 3688, 27: 3832, 28: 3862,
}


def classifica(esperados):
    """{mrv: classe} -- as N_ALTA maiores sao 'alta'; >= LIMIAR_MEDIA 'media'."""
    ordem = sorted(esperados, key=lambda k: (-esperados[k], k))
    out = {}
    for i, k in enumerate(ordem):
        if i < N_ALTA:
            out[k] = "alta"
        elif esperados[k] >= LIMIAR_MEDIA:
            out[k] = "media"
        else:
            out[k] = "baixa"
    return out


def mesas(dados=None):
    """As 28 mesas pela numeracao do DJE, com secoes, aptos, esperado e classe."""
    dados = dados or CP.carrega_dados()
    por_principal = {u["principal"]: u for u in CP.por_urna(dados)}
    if set(MRV_SECAO_PRINCIPAL.values()) != set(por_principal):
        raise SystemExit("descasamento MRV x urnas do pipeline: "
                         f"{set(MRV_SECAO_PRINCIPAL.values()) ^ set(por_principal)}")
    secoes = {s["Secao"]: s for s in dados["secoes"]}
    saida = []
    for mrv in sorted(MRV_SECAO_PRINCIPAL):
        u = por_principal[MRV_SECAO_PRINCIPAL[mrv]]
        agr = u["agregada"]
        saida.append({
            "mrv": mrv,
            "principal": u["principal"],
            "agregada": agr,
            "origem_agregada": secoes[agr]["Residencia_predominante"] if agr else None,
            "aptos": u["aptos"],
            "aptos_principal": secoes[u["principal"]]["Eleitores"],
            "aptos_agregada": secoes[agr]["Eleitores"] if agr else 0,
            "aptos_dublin": u["aptos_dublin"],
            "aptos_interior": u["aptos_interior"],
            "esperado": u["esperado"],
            "esperado_exato": round(u["esperado_exato"], 2),
        })
    classes = classifica({m["mrv"]: m["esperado"] for m in saida})
    for m in saida:
        m["classe"] = classes[m["mrv"]]
        m["cor"] = CLASSES[m["classe"]]["hex"]
    return saida


def atribui_entradas(lista, quotas):
    """Reparte as mesas entre as entradas na proporcao das quotas.

    Uma mesa de classe alta em cada entrada (as tres criticas nunca na mesma
    fila), depois as demais, sempre para a entrada mais distante da sua quota.
    Devolve {entrada: [mrv, ...]}.
    """
    total = sum(m["esperado"] for m in lista)
    alvo = {k: v * total for k, v in quotas.items()}
    grupos = {k: [] for k in quotas}
    carga = {k: 0.0 for k in quotas}
    ordenadas = sorted(lista, key=lambda m: (-m["esperado"], m["mrv"]))
    altas = [m for m in ordenadas if m["classe"] == "alta"]
    for entrada, m in zip(sorted(quotas, key=lambda k: -quotas[k]), altas):
        grupos[entrada].append(m["mrv"])
        carga[entrada] += m["esperado"]
    for m in ordenadas:
        if m["classe"] == "alta" and any(m["mrv"] in g for g in grupos.values()):
            continue
        entrada = max(carga, key=lambda k: alvo[k] - carga[k])
        grupos[entrada].append(m["mrv"])
        carga[entrada] += m["esperado"]
    return {k: sorted(v) for k, v in grupos.items()}, carga, alvo


def montar(dados=None):
    """Tudo que os geradores precisam, num dicionario serializavel."""
    import layout_ring3 as R3                                 # noqa: E402  (lazy: R3 importa este modulo)
    import salao as FL                                        # noqa: E402

    dados = dados or CP.carrega_dados()
    lista = mesas(dados)
    caps = R3.capacidades()
    quotas = {c["entrada"]: c["quota"] for c in caps}
    grupos, carga, alvo = atribui_entradas(lista, quotas)
    entrada_da_mesa = {mrv: e for e, ms in grupos.items() for mrv in ms}
    for m in lista:
        m["entrada"] = entrada_da_mesa[m["mrv"]]
        m["porta"] = PORTA_DA_ENTRADA[m["entrada"]]

    entradas = []
    for c in caps:
        e = c["entrada"]
        entradas.append({
            "id": e, "porta": c["porta"],
            "cor": CORES_ENTRADA[e][0], "hex": CORES_ENTRADA[e][1],
            "balizas": c["balizas"], "serpenteado": int(round(c["serpenteado"])),
            "baia": int(round(c["baia"])), "capacidade": int(round(c["total"])),
            "quota": round(c["quota"], 4),
            "mrvs": grupos[e], "esperado": int(round(carga[e])),
            "alvo": int(round(alvo[e])),
        })
    r = R3.resumo()
    ev = R3.egresso()
    rect = FL.ring3_rect()
    portas = {}
    for num, papel in PAPEL_PORTA.items():
        portas[num] = {"papel": papel}
        if papel == "entrada":
            portas[num]["entrada"] = ENTRADA_DA_PORTA[num]
            portas[num]["cor"] = CORES_ENTRADA[ENTRADA_DA_PORTA[num]][1]
    contagem = {k: sum(1 for m in lista if m["classe"] == k) for k in ORDEM_CLASSES}
    return {
        "decididoEm": DECIDIDO_EM,
        "numeracao": "MRV do DJE/TRE-DF, identidade unica da mesa; nao depende da posicao",
        "comparecimento": {
            "base": CP.BASE, "rotulo": CP.ROTULO,
            "total": sum(m["esperado"] for m in lista),
            "total_exato": round(sum(m["esperado_exato"] for m in lista), 1),
            "aptos": sum(m["aptos"] for m in lista),
            "taxas": {k: {"taxa": v[0], "qualidade": v[1]}
                      for k, v in CP.TAXA_POR_DOMICILIO.items()},
        },
        "classes": {
            "regra": f"as {N_ALTA} maiores = alta; esperado >= {LIMIAR_MEDIA} = media; "
                     "abaixo = baixa",
            "n_alta": N_ALTA, "limiar_media": LIMIAR_MEDIA,
            "cores": {k: dict(CLASSES[k]) for k in ORDEM_CLASSES},
            "contagem": contagem,
        },
        "portas": portas,
        "entradas": entradas,
        "saidas": list(SAIDAS),
        "nomenclatura_portas": "em aberto: cor ou letra",
        "mesas": lista,
        "ring3": {
            "largura": R3.LARGURA, "profundidade": R3.PROFUNDIDADE,
            "apron": FL.RING3["apron"], "rect": [round(v, 2) for v in rect],
            "eixo": "centrado em S5 (estimativa; aferir o bordo oeste em campo)",
            "serpenteado": R3.PROF_SERPENTE, "balizas": list(R3.BALIZAS),
            "capacidade": int(round(r["total_pessoas"])),
            "separadores": r["unidades"], "metros": round(r["metros"], 1),
            "em_maos": R3.SEPARADORES_EM_MAOS, "a_adquirir": r["faltam"],
            "custo_eur": round(r["custo"]),
            "evacuacao_min": round(ev["tempo_atual"], 1),
            "largura_saida_exigida": round(ev["larg_exigida"], 2),
        },
    }


def carrega():
    """Alias de montar(): as decisoes sao sempre recalculadas, nunca lidas
    de um arquivo que possa ter ficado para tras."""
    return montar()


if __name__ == "__main__":
    d = montar()
    print(json.dumps({k: v for k, v in d.items() if k != "mesas"},
                     ensure_ascii=False, indent=1))
