"""Confere o equilíbrio das três zonas do salão de votação.

A planta de 16/09/2026 distribui as 28 urnas nas paredes do Hall 2: parede
oeste = zona A (porta S4), parede norte = zona B (porta S5), parede leste =
zona C (porta S6). Cada zona é alimentada pela zona correspondente do pátio de
fila do Ring 3.

O critério de equilíbrio é o comparecimento esperado, não o número de urnas: as
urnas vão de 398 a 797 aptos. Taxas de 2022 (contexto_eleicoes_dublin_2026.md):
74% para eleitores domiciliados em Dublin, 50% para os do interior.

Uso: python3 scripts/zonas_balanceadas.py
"""

import json
from pathlib import Path

TAXA_DUBLIN = 0.74
TAXA_INTERIOR = 0.50

# Urnas por zona, lidas da planta do Hall 2 de 16/09/2026.
ZONAS = {
    "A · parede oeste · porta S4": [3179, 3078, 1352, 513, 3313, 3311, 3161, 3142, 3309],
    "B · parede norte · porta S5": [512, 1160, 3315, 3108, 3302, 3306, 3305, 3308, 3832],
    "C · parede leste · porta S6": [511, 517, 3322, 3054, 3216, 3862, 3245, 3229, 3688, 3442],
}

# Urnas com serpentina interna de 20 pessoas previstas na planta.
GRANDES = {3313, 3315, 3322}

DADOS = Path(__file__).resolve().parent.parent / "saidas" / "dados.json"


def carrega():
    """Retorna {urna: (aptos_dublin, aptos_interior)}."""
    with open(DADOS, encoding="utf-8") as f:
        dados = json.load(f)
    return {
        linha["Urna"]: (linha["DUBLIN"], linha["TOTAL"] - linha["DUBLIN"])
        for linha in dados["residencia_urna"]
    }


def comparecimento(dublin, interior):
    return round(dublin * TAXA_DUBLIN + interior * TAXA_INTERIOR)


def main():
    urnas = carrega()

    lidas = [u for lista in ZONAS.values() for u in lista]
    faltando = sorted(set(urnas) - set(lidas))
    sobrando = sorted(set(lidas) - set(urnas))
    if faltando or sobrando:
        raise SystemExit(
            f"planta não fecha com os dados: faltam {faltando}, sobram {sobrando}"
        )

    cargas = []
    for zona, lista in ZONAS.items():
        dublin = sum(urnas[u][0] for u in lista)
        interior = sum(urnas[u][1] for u in lista)
        carga = comparecimento(dublin, interior)
        cargas.append(carga)
        grandes = sorted(GRANDES.intersection(lista))
        print(
            f"Zona {zona}: {len(lista)} urnas | aptos {dublin + interior} "
            f"(Dublin {dublin}, interior {interior}) | comparecimento {carga} "
            f"| urnas grandes {grandes}"
        )

    print(f"\nComparecimento esperado total: {sum(cargas)}")
    print(f"Spread entre a zona mais cheia e a mais vazia: "
          f"{(max(cargas) - min(cargas)) / min(cargas):.1%}")

    orfas = [z for z, lista in ZONAS.items() if not GRANDES.intersection(lista)]
    if orfas:
        print(f"ATENÇÃO: zonas sem urna grande: {orfas}")
    else:
        print("Cada zona tem exatamente uma das três urnas grandes.")


if __name__ == "__main__":
    main()
