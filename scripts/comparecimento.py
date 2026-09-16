"""Base unica de comparecimento esperado: taxa de 2022 por domicilio de origem.

Decisao do Posto (06/09/2026). Tres bases conviviam no repositorio -- a
binaria 74% Dublin / 50% interior, o "~12.000" da nota verbal e a taxa de 2022
por condado do handoff (base B). Vale a base B, e toda estimativa de
comparecimento por secao, por urna ou total sai deste modulo.

Nao e comparecimento oficial. E a taxa observada em 2022 no domicilio de origem
de cada secao (handoff_agregacao_dublin_2026.md, secao 2), de qualidade
desigual ("direto", "proxy" ou "generico"), aplicada aos aptos de 2026. Cada
secao tem 100% do eleitorado numa unica localidade (achado da etapa 1), entao
a taxa e aplicada secao a secao e somada por urna.

Arredondamento: o esperado de uma urna e o arredondamento da soma exata das
suas secoes; o total e a soma dos esperados arredondados por urna, para que as
tabelas fechem.
"""
import json
import os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DADOS = os.path.join(RAIZ, "saidas", "dados.json")

BASE = "B"
ROTULO = "taxa de 2022 por domicílio de origem (base B, não oficial)"

# Chave = valor de Residencia_predominante em saidas/dados.json (mesma grafia,
# maiusculas). Transcrito de handoff_agregacao_dublin_2026.md, secao 2.
TAXA_POR_DOMICILIO = {
    "DUBLIN":                   (0.740, "direto"),
    "CORK":                     (0.533, "direto"),
    "OUTROS LOCAIS DA IRLANDA": (0.600, "direto"),
    "GALWAY":                   (0.481, "direto"),
    "LIMERICK":                 (0.434, "proxy"),
    "WESTMEATH":                (0.461, "proxy"),
    "WATERFORD":                (0.461, "proxy"),
    "ROSCOMMON":                (0.434, "proxy"),
    "CLARE":                    (0.649, "direto"),
    "CAVAN":                    (0.461, "proxy"),
    "MAYO":                     (0.544, "proxy"),
    "LONGFORD":                 (0.778, "direto"),
    "DONEGAL":                  (0.510, "genérico (0,49 abst.)"),
    "KERRY":                    (0.544, "proxy"),
    "LEITRIM":                  (0.510, "genérico (0,49 abst.)"),
}


def taxa(localidade):
    """(taxa, qualidade) do domicilio; falha alto se a localidade for nova."""
    return TAXA_POR_DOMICILIO[localidade]


def carrega_dados():
    with open(DADOS, encoding="utf-8") as f:
        return json.load(f)


def esperado_exato(contagens):
    """Soma de aptos x taxa para um dicionario {localidade: aptos}."""
    return sum(n * TAXA_POR_DOMICILIO[loc][0] for loc, n in contagens.items() if n)


def por_urna(dados=None):
    """Uma entrada por urna (secao principal), na ordem de saidas/dados.json.

    Cada entrada traz aptos, aptos_dublin, aptos_interior, as contagens por
    localidade, o esperado exato e o esperado arredondado.
    """
    dados = dados or carrega_dados()
    residencia = {r["Urna"]: r for r in dados["residencia_urna"]}
    saida = []
    for u in dados["urnas"]:
        r = residencia[u["Urna"]]
        contagens = {k: v for k, v in r.items() if k not in ("Urna", "TOTAL") and v}
        exato = esperado_exato(contagens)
        saida.append({
            "urna": u["Urna"],
            "principal": u["Secao_principal"],
            "agregada": _int_ou_none(u["Secao_agregada"]),
            "aptos": r["TOTAL"],
            "aptos_dublin": r.get("DUBLIN", 0),
            "aptos_interior": r["TOTAL"] - r.get("DUBLIN", 0),
            "localidades": contagens,
            "esperado_exato": exato,
            "esperado": int(round(exato)),
        })
    return saida


def por_secao(dados=None):
    """{secao: (esperado_exato, taxa, qualidade)} para as 51 secoes."""
    dados = dados or carrega_dados()
    out = {}
    for s in dados["secoes"]:
        t, q = TAXA_POR_DOMICILIO[s["Residencia_predominante"]]
        out[s["Secao"]] = (s["Eleitores"] * t, t, q)
    return out


def total(dados=None):
    """Soma dos esperados arredondados por urna."""
    return sum(u["esperado"] for u in por_urna(dados))


def _int_ou_none(v):
    if v is None or (isinstance(v, float) and v != v):
        return None
    return int(v)


if __name__ == "__main__":
    urnas = por_urna()
    print(f"{len(urnas)} urnas · {sum(u['aptos'] for u in urnas)} aptos · "
          f"{total()} esperados ({ROTULO})")
    for u in sorted(urnas, key=lambda u: -u["esperado"]):
        print(f"  {u['urna']:>5}  aptos {u['aptos']:>4}  esperado {u['esperado']:>4}"
              f"  ({u['esperado_exato']:.1f})")
