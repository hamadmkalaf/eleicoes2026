"""Deriva o plano de sinalizacao interna a partir da prancheta Hamad_Final.

Le a prancheta (28 mesas com coordenadas, rotacao e lado), identifica a parede
de cada mesa, reconstroi os pares de mesas, cruza com saidas/dados.json e
escreve saidas/sinalizacao.json e saidas/plano_sinalizacao.md.

Regra de portas dada pelo Posto: porta A -> parede oeste, porta B -> parede
norte, porta C -> parede leste. Orientacao do salao L-O (eixo x = leste-oeste).

O vinculo mesa -> urna e uma PREMISSA (ver MAPA_MESA_URNA): a prancheta numera
posicoes de 1 a 28 e dados.json numera urnas de 1 a 28 por volume decrescente.
Trocar o dicionario abaixo e suficiente para regerar todo o plano.
"""

import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
SAIDAS = BASE / "saidas"

# Prancheta "Hamad_Final" (id hamad-final-20260913150300), Cenario 3 / Ring 3.
PRANCHETA = [
    {"n": 1, "x": 0.8, "y": 15.8, "rot": 0, "lado": 1},
    {"n": 2, "x": 8.55, "y": 43.6, "rot": 270, "lado": 1},
    {"n": 3, "x": 47.3, "y": 36.65, "rot": 180, "lado": 1},
    {"n": 4, "x": 0.8, "y": 29.6, "rot": 0, "lado": -1},
    {"n": 5, "x": 0.8, "y": 25.7, "rot": 0, "lado": 1},
    {"n": 6, "x": 0.8, "y": 19.7, "rot": 0, "lado": -1},
    {"n": 7, "x": 47.3, "y": 32.75, "rot": 180, "lado": -1},
    {"n": 8, "x": 36.2, "y": 43.6, "rot": 270, "lado": -1},
    {"n": 9, "x": 0.8, "y": 32.35, "rot": 0, "lado": 1},
    {"n": 10, "x": 32.3, "y": 43.6, "rot": 270, "lado": 1},
    {"n": 11, "x": 0.8, "y": 36.25, "rot": 0, "lado": -1},
    {"n": 12, "x": 0.8, "y": 8.9, "rot": 0, "lado": 1},
    {"n": 13, "x": 42.95, "y": 43.6, "rot": 270, "lado": -1},
    {"n": 14, "x": 47.3, "y": 26.75, "rot": 180, "lado": 1},
    {"n": 15, "x": 19.35, "y": 43.6, "rot": 270, "lado": 1},
    {"n": 16, "x": 23.25, "y": 43.6, "rot": 270, "lado": -1},
    {"n": 17, "x": 0.8, "y": 12.8, "rot": 0, "lado": -1},
    {"n": 18, "x": 47.3, "y": 22.85, "rot": 180, "lado": -1},
    {"n": 19, "x": 47.3, "y": 12.95, "rot": 180, "lado": 1},
    {"n": 20, "x": 39.05, "y": 43.6, "rot": 270, "lado": 1},
    {"n": 21, "x": 47.3, "y": 19.85, "rot": 180, "lado": 1},
    {"n": 22, "x": 28.25, "y": 43.6, "rot": 270, "lado": 1},
    {"n": 23, "x": 47.3, "y": 29.75, "rot": 180, "lado": 1},
    {"n": 24, "x": 0.8, "y": 23.0, "rot": 0, "lado": 1},
    {"n": 25, "x": 12.45, "y": 43.6, "rot": 270, "lado": -1},
    {"n": 26, "x": 47.3, "y": 15.95, "rot": 180, "lado": -1},
    {"n": 27, "x": 47.3, "y": 9.95, "rot": 180, "lado": 1},
    {"n": 28, "x": 47.3, "y": 6.05, "rot": 180, "lado": -1},
]

# PREMISSA a validar: posicao na prancheta == Posicao em dados.json.
MAPA_MESA_URNA = {n: n for n in range(1, 29)}

PAREDE_POR_ROT = {0: "OESTE", 180: "LESTE", 270: "NORTE"}
PORTA_POR_PAREDE = {"OESTE": "A", "NORTE": "B", "LESTE": "C"}
VAO_DO_PAR = 3.9  # m entre as duas mesas de um par: e o corredor de atendimento

# Taxas de comparecimento de 2022 usadas no contexto do Posto.
TAXA_DUBLIN = 0.74
TAXA_INTERIOR = 0.50


def eixo(mesa: dict) -> float:
    """Coordenada da mesa ao longo da sua propria parede."""
    return mesa["x"] if mesa["rot"] == 270 else mesa["y"]


def agrupa(mesas: list, invertido: bool) -> list:
    """Reconstroi os pares: duas mesas a 3,90 m com os lados voltados uma para
    a outra compartilham o corredor entre elas. O resto e mesa isolada.

    Nas paredes oeste e norte o par le (+1, -1) no sentido crescente; na parede
    leste, que esta rotacionada 180 graus, a convencao de lado se inverte.
    """
    mesas = sorted(mesas, key=eixo)
    primeiro, segundo = (-1, 1) if invertido else (1, -1)
    grupos, i = [], 0
    while i < len(mesas):
        a = mesas[i]
        b = mesas[i + 1] if i + 1 < len(mesas) else None
        emparelha = (
            b is not None
            and abs(eixo(b) - eixo(a) - VAO_DO_PAR) < 0.01
            and a["lado"] == primeiro
            and b["lado"] == segundo
        )
        if emparelha:
            grupos.append([a, b])
            i += 2
        else:
            grupos.append([a])
            i += 1
    return grupos


def carrega_urnas() -> tuple:
    dados = json.loads((SAIDAS / "dados.json").read_text(encoding="utf-8"))
    urnas = {u["Posicao"]: u for u in dados["urnas"]}
    residencia = {r["Urna"]: r for r in dados["residencia_urna"]}
    return urnas, residencia


def descreve_mesa(n: int, urnas: dict, residencia: dict) -> dict:
    u = urnas[MAPA_MESA_URNA[n]]
    secoes = [int(u["Secao_principal"])]
    if u["Qtd_secoes"] == 2:
        secoes.append(int(u["Secao_agregada"]))
    r = residencia[u["Urna"]]
    origens = {k: v for k, v in r.items() if k not in ("Urna", "TOTAL") and v > 0}
    dublin = r["DUBLIN"]
    fora = r["TOTAL"] - dublin
    return {
        "mesa": n,
        "urna": u["Urna"],
        "secoes": secoes,
        "aptos": u["Total_combinado"],
        "origens": sorted(origens),
        "comparecimento": dublin * TAXA_DUBLIN + fora * TAXA_INTERIOR,
    }


def monta() -> dict:
    urnas, residencia = carrega_urnas()
    paredes = {}
    for mesa in PRANCHETA:
        paredes.setdefault(PAREDE_POR_ROT[mesa["rot"]], []).append(mesa)

    plano = {"paredes": [], "total_aptos": 0, "total_comparecimento": 0.0}
    for parede in ("OESTE", "NORTE", "LESTE"):
        grupos = agrupa(paredes[parede], invertido=(parede == "LESTE"))
        blocos, aptos, comp, secoes_porta = [], 0, 0.0, []
        for ordem, grupo in enumerate(grupos, start=1):
            mesas = [descreve_mesa(m["n"], urnas, residencia) for m in grupo]
            secoes = sorted(s for m in mesas for s in m["secoes"])
            origens = sorted({o for m in mesas for o in m["origens"]})
            blocos.append({
                "ordem": ordem,
                "tipo": "PAR" if len(mesas) == 2 else "ISOLADA",
                "mesas": [m["mesa"] for m in mesas],
                "coord_inicial": eixo(grupo[0]),
                "coord_final": eixo(grupo[-1]),
                "secoes": secoes,
                "origens": origens,
                "aptos": sum(m["aptos"] for m in mesas),
                "comparecimento": round(sum(m["comparecimento"] for m in mesas)),
            })
            secoes_porta += secoes
            aptos += blocos[-1]["aptos"]
            comp += sum(m["comparecimento"] for m in mesas)
        plano["paredes"].append({
            "parede": parede,
            "porta": PORTA_POR_PAREDE[parede],
            "n_mesas": len(paredes[parede]),
            "n_pares": sum(1 for b in blocos if b["tipo"] == "PAR"),
            "n_isoladas": sum(1 for b in blocos if b["tipo"] == "ISOLADA"),
            "blocos": blocos,
            "secoes": sorted(secoes_porta),
            "aptos": aptos,
            "comparecimento": round(comp),
        })
        plano["total_aptos"] += aptos
        plano["total_comparecimento"] += comp
    plano["total_comparecimento"] = round(plano["total_comparecimento"])
    return plano


def valida(plano: dict) -> None:
    """Falha em vez de gravar um plano que nao fecha com a base do TSE."""
    dados = json.loads((SAIDAS / "dados.json").read_text(encoding="utf-8"))
    secoes = [s for p in plano["paredes"] for s in p["secoes"]]
    assert len(secoes) == len(set(secoes)) == dados["total_secoes"], (
        f"secoes duplicadas ou faltantes: {len(secoes)} unicas={len(set(secoes))}"
    )
    assert plano["total_aptos"] == dados["total_eleitores"], (
        f"aptos {plano['total_aptos']} != {dados['total_eleitores']}"
    )
    mesas = [m for p in plano["paredes"] for b in p["blocos"] for m in b["mesas"]]
    assert sorted(mesas) == list(range(1, 29)), "as 28 mesas nao fecham"


def main() -> None:
    plano = monta()
    valida(plano)
    destino = SAIDAS / "sinalizacao.json"
    destino.write_text(
        json.dumps(plano, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    for p in plano["paredes"]:
        print(
            f"Porta {p['porta']} / parede {p['parede']}: {p['n_mesas']} mesas "
            f"({p['n_pares']} pares + {p['n_isoladas']} isoladas), "
            f"{len(p['secoes'])} secoes, {p['aptos']} aptos, "
            f"{p['comparecimento']} comparecimento esperado"
        )
    print(f"Gravado {destino.relative_to(BASE)}")


if __name__ == "__main__":
    main()
