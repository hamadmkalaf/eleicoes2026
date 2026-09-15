"""Distribui as 28 urnas nas três zonas do Ring 3 equilibrando comparecimento.

As zonas A, B e C do Ring 3 correspondem às portas A, B e C do Hall 2 (ver
CLAUDE.md). O critério de equilíbrio é o comparecimento esperado, não o número
de urnas: as urnas vão de 398 a 797 aptos.

Taxas de comparecimento de 2022 (contexto_eleicoes_dublin_2026.md): 74% para
eleitores domiciliados em Dublin, 50% para os do interior.

Uso: python3 scripts/zonas_balanceadas.py
"""

import json
from pathlib import Path

TAXA_DUBLIN = 0.74
TAXA_INTERIOR = 0.50
CAPACIDADE = {"A": 9, "B": 9, "C": 10}

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


def distribui(urnas):
    """Guloso: a urna mais pesada vai para a zona mais leve que ainda tem vaga."""
    esperado = {u: comparecimento(*v) for u, v in urnas.items()}
    zonas = {z: [] for z in CAPACIDADE}
    for urna, _ in sorted(esperado.items(), key=lambda par: -par[1]):
        com_vaga = [z for z in zonas if len(zonas[z]) < CAPACIDADE[z]]
        destino = min(com_vaga, key=lambda z: sum(esperado[u] for u in zonas[z]))
        zonas[destino].append(urna)
    return zonas, esperado


def main():
    urnas = carrega()
    zonas, esperado = distribui(urnas)

    total = sum(esperado.values())
    print(f"{len(urnas)} urnas, comparecimento esperado {total}\n")
    cargas = []
    for zona in sorted(zonas):
        lista = sorted(zonas[zona])
        dublin = sum(urnas[u][0] for u in lista)
        interior = sum(urnas[u][1] for u in lista)
        carga = sum(esperado[u] for u in lista)
        cargas.append(carga)
        print(
            f"Zona {zona}: {len(lista)} urnas | aptos {dublin + interior} "
            f"(Dublin {dublin}, interior {interior}) | comparecimento {carga}"
        )
        print(f"          {lista}")

    spread = (max(cargas) - min(cargas)) / min(cargas)
    print(f"\nSpread entre a zona mais cheia e a mais vazia: {spread:.1%}")


if __name__ == "__main__":
    main()
