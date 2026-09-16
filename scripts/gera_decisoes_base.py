"""Reconstroi o bloco `mesas` de data/decisoes.json a partir das fontes.

`scripts/arranjo_paredes.py` le esse bloco e escreve por cima dele a camada de
layout (parede, entrada, porta, numero eleitor, zonas, serpenteados). O bloco
em si -- quais secoes formam cada urna, quantos aptos e quantos esperados --
vinha de um gerador que ficou noutro branch, o que deixava data/decisoes.json
sem origem reproduzivel dentro deste repositorio.

Este modulo fecha essa lacuna. Tudo aqui sai de tres coisas que o repositorio
tem:

  data/oficiais/secoes_agregadas_dublin_2026.pdf   os 28 pares principal -> agregada
  data/oficiais/aptos_por_secao_dublin_2026-07-13.pdf   aptos e condado de cada secao
  scripts/comparecimento.py                        a taxa de 2022 por condado

**Numeracao MRV.** A identidade oficial da mesa e o MRV do DJE/TRE-DF. Neste
repositorio ele sempre coincidiu com a **ordem crescente da secao principal**
(511 -> MRV 1, 512 -> MRV 2, ..., 3862 -> MRV 28), e e assim que ele e
reconstruido aqui. E uma inferencia verificada contra o bloco que veio do
DJE, nao uma leitura do DJE: se o Cartorio emitir uma numeracao diferente,
corrigir aqui e nao nas pecas geradas.

    python3 scripts/gera_decisoes_base.py            # confere contra o que existe
    python3 scripts/gera_decisoes_base.py --grava    # grava o bloco reconstruido
"""
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "scripts"))

import comparecimento as C                                      # noqa: E402
import fontes_oficiais as fontes                                # noqa: E402

N_ALTA = 3           # as tres de maior comparecimento sao "alta"
LIMIAR_MEDIA = 450   # daqui para cima e "media"; abaixo, "baixa"
CORES = {"alta": {"cor": "vermelho", "hex": "#c0392b", "rotulo": "alto comparecimento"},
         "media": {"cor": "amarelo", "hex": "#d4a017", "rotulo": "médio comparecimento"},
         "baixa": {"cor": "verde", "hex": "#1e8449", "rotulo": "baixo comparecimento"}}
DUBLIN = "DUBLIN"


def mesas():
    """As 28 mesas, do par oficial ate a classe de carga."""
    aptos, _, _ = fontes.aptos_por_secao()
    pares, _ = fontes.agregacoes()
    ordem = {p: i + 1 for i, p in enumerate(sorted(p for p, _ in pares))}

    saida = []
    for principal, agregada in sorted(pares):
        partes = [principal] + ([agregada] if agregada else [])
        n_p, loc_p = aptos[principal]
        n_a, loc_a = aptos[agregada] if agregada else (0, None)
        exato = sum(aptos[s][0] * C.TAXA_POR_DOMICILIO[aptos[s][1]][0] for s in partes)
        saida.append({
            "mrv": ordem[principal], "principal": principal, "agregada": agregada,
            "origem_agregada": loc_a,
            "aptos": n_p + n_a, "aptos_principal": n_p, "aptos_agregada": n_a,
            "aptos_dublin": sum(aptos[s][0] for s in partes if aptos[s][1] == DUBLIN),
            "aptos_interior": sum(aptos[s][0] for s in partes if aptos[s][1] != DUBLIN),
            "esperado": int(round(exato)), "esperado_exato": round(exato, 2),
        })

    # a classe sai do ranking, entao so da para atribuir com as 28 na mao
    corte = sorted((m["esperado"] for m in saida), reverse=True)[N_ALTA - 1]
    for m in saida:
        if m["esperado"] >= corte:
            m["classe"] = "alta"
        elif m["esperado"] >= LIMIAR_MEDIA:
            m["classe"] = "media"
        else:
            m["classe"] = "baixa"
        m["cor"] = CORES[m["classe"]]["hex"]
    n_alta = sum(1 for m in saida if m["classe"] == "alta")
    if n_alta != N_ALTA:
        raise SystemExit(f"{n_alta} mesas empataram no topo; a regra espera {N_ALTA}")
    return sorted(saida, key=lambda m: m["mrv"])


def comparecimento_bloco(ms):
    total = sum(m["esperado"] for m in ms)
    return {
        "base": C.BASE, "rotulo": C.ROTULO, "total": total,
        "total_exato": round(sum(m["esperado_exato"] for m in ms), 1),
        "aptos": sum(m["aptos"] for m in ms),
        "taxas": {loc: {"taxa": t, "qualidade": q}
                  for loc, (t, q) in C.TAXA_POR_DOMICILIO.items()},
    }


def classes_bloco(ms):
    contagem = {c: sum(1 for m in ms if m["classe"] == c) for c in CORES}
    return {
        "regra": f"as {N_ALTA} maiores = alta; esperado >= {LIMIAR_MEDIA} = media; "
                 f"abaixo = baixa",
        "n_alta": N_ALTA, "limiar_media": LIMIAR_MEDIA,
        "cores": {c: dict(CORES[c]) for c in CORES},
        "contagem": contagem,
    }


# Campos que a camada de layout escreve por cima; nao saem daqui.
DO_LAYOUT = ("eleitor", "parede", "entrada", "porta")


def main(argv):
    ms = mesas()
    caminho = os.path.join(RAIZ, "data", "decisoes.json")
    with open(caminho, encoding="utf-8") as f:
        atual = json.load(f)
    por_mrv = {m["mrv"]: m for m in atual["mesas"]}

    print(f"{len(ms)} mesas reconstruídas · {sum(m['aptos'] for m in ms)} aptos · "
          f"{sum(m['esperado'] for m in ms)} esperados")
    divergencias = []
    for m in ms:
        velha = por_mrv.get(m["mrv"])
        if velha is None:
            divergencias.append(f"MRV {m['mrv']} não existe em data/decisoes.json")
            continue
        for k, v in m.items():
            if k in DO_LAYOUT:
                continue
            if velha.get(k) != v:
                divergencias.append(f"MRV {m['mrv']}, campo {k}: "
                                    f"reconstruído {v!r} × atual {velha.get(k)!r}")
    if divergencias:
        print(f"\n{len(divergencias)} divergência(s):")
        for d in divergencias:
            print("  ·", d)
    else:
        print("bate campo a campo com o bloco que está em data/decisoes.json")

    if "--grava" not in argv:
        print("\n(nada gravado; use --grava para reescrever o bloco)")
        return 1 if divergencias else 0

    for m in ms:                       # preserva o que a camada de layout pôs
        velha = por_mrv.get(m["mrv"], {})
        for k in DO_LAYOUT:
            if k in velha:
                m[k] = velha[k]
    atual["mesas"] = ms
    atual["comparecimento"] = comparecimento_bloco(ms)
    atual["classes"] = classes_bloco(ms)
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(atual, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print("\ngravado o bloco mesas/comparecimento/classes em data/decisoes.json")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
