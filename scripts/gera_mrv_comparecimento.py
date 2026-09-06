"""Junta a designacao oficial de MRVs (DJE/TRE-DF) ao eleitorado por secao,
com estimativa de comparecimento por localidade de origem (domicilio).

Fonte da designacao MRV -> secao principal: Diario da Justica Eletronico do
TRE-DF, Ano 2026 n. 139, disponibilizado em 04/08/2026 ("Convocacao de
mesarios - Justica Eleitoral, Irlanda, Apoio e Mesarios Dublin"), paginas
915-921. E o unico documento que atribui numero de MRV as 28 urnas de
Dublin; o pipeline desta pasta (parse_dados.py / mapa_agregacoes.py) so
conhece a secao principal, nao o numero de MRV.

QT_ELEITOR_SECAO (aqui "Eleitores aptos") e dado oficial do TSE. Nao ha, em
nenhum arquivo de data/raw/, uma estimativa de comparecimento por secao
publicada pelo TSE ou pelo Cartorio Eleitoral -- so o numero de aptos.

A taxa de comparecimento por domicilio abaixo (TAXA_POR_DOMICILIO) vem de
handoff_agregacao_dublin_2026.md (secao 2), fornecido pelo usuario em
03/09/2026: taxas de 2022 por condado/localidade de origem, algumas
"diretas" (dado do proprio domicilio), outras "proxy" (domicilio parecido
usado como substituto) ou "genericas" (taxa media nacional de abstencao).
Cada secao (principal ou agregada) tem 100% do seu eleitorado numa unica
localidade de origem (achado ja registrado em
contexto_eleicoes_dublin_2026.md), entao a taxa e aplicada secao a secao,
nao mais por um binario Dublin/interior -- essa e uma estimativa mais fina
que a usada na primeira versao deste script (74%/50%), mas ainda nao e
comparecimento oficial por secao.
"""

import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
SAIDAS = BASE / "saidas"

# MRV -> secao principal, transcrito do DJE/TRE-DF (ver docstring do modulo).
MRV_SECAO_PRINCIPAL = {
    1: 511, 2: 512, 3: 513, 4: 517, 5: 1160, 6: 1352, 7: 3054, 8: 3078,
    9: 3108, 10: 3142, 11: 3161, 12: 3179, 13: 3216, 14: 3229, 15: 3245,
    16: 3302, 17: 3305, 18: 3306, 19: 3308, 20: 3309, 21: 3311, 22: 3313,
    23: 3315, 24: 3322, 25: 3442, 26: 3688, 27: 3832, 28: 3862,
}

# Taxa de comparecimento 2022 por domicilio e qualidade do dado, transcritas
# de handoff_agregacao_dublin_2026.md secao 2. Chave = valor de
# Residencia_predominante em saidas/dados.json (mesma grafia, maiusculas).
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


def _secao_agregada(urna: dict):
    agr = urna["Secao_agregada"]
    if agr is None or (isinstance(agr, float) and agr != agr):  # NaN
        return None
    return int(agr)


def main():
    dados = json.loads((SAIDAS / "dados.json").read_text(encoding="utf-8"))
    urnas = {u["Secao_principal"]: u for u in dados["urnas"]}
    secoes = {s["Secao"]: s for s in dados["secoes"]}

    if set(MRV_SECAO_PRINCIPAL.values()) != set(urnas):
        faltando = set(MRV_SECAO_PRINCIPAL.values()) ^ set(urnas)
        raise SystemExit(f"Descasamento MRV x urnas do pipeline: {faltando}")

    faltando_taxa = {s["Residencia_predominante"] for s in secoes.values()} - set(TAXA_POR_DOMICILIO)
    if faltando_taxa:
        raise SystemExit(f"Sem taxa de comparecimento para: {faltando_taxa}")

    def comparecimento_secao(secao_num: int) -> float:
        s = secoes[secao_num]
        taxa, _ = TAXA_POR_DOMICILIO[s["Residencia_predominante"]]
        return s["Eleitores"] * taxa

    linhas = []
    total_aptos = 0
    total_comparecimento_exato = 0.0
    for mrv in sorted(MRV_SECAO_PRINCIPAL):
        secao_p = MRV_SECAO_PRINCIPAL[mrv]
        urna = urnas[secao_p]
        secao_a = _secao_agregada(urna)

        taxa_p, qual_p = TAXA_POR_DOMICILIO[secoes[secao_p]["Residencia_predominante"]]
        comp_p = comparecimento_secao(secao_p)

        if secao_a:
            origem_a = secoes[secao_a]["Residencia_predominante"]
            taxa_a, qual_a = TAXA_POR_DOMICILIO[origem_a]
            comp_a = comparecimento_secao(secao_a)
        else:
            origem_a = taxa_a = qual_a = comp_a = None

        comp_total = comp_p + (comp_a or 0)
        total_aptos += urna["Total_combinado"]
        total_comparecimento_exato += comp_total

        linhas.append({
            "mrv": mrv,
            "secao_principal": secao_p,
            "eleitores_principal": urna["Eleitores_principal"],
            "taxa_principal": taxa_p,
            "qualidade_principal": qual_p,
            "secao_agregada": secao_a,
            "eleitores_agregada": urna["Eleitores_agregada"],
            "origem_agregada": origem_a,
            "taxa_agregada": taxa_a,
            "qualidade_agregada": qual_a,
            "total_aptos": urna["Total_combinado"],
            "comparecimento_estimado": round(comp_total),
        })

    assert total_aptos == dados["total_eleitores"], (
        f"Soma dos 28 MRVs ({total_aptos}) != total do repositorio "
        f"({dados['total_eleitores']})"
    )

    total_comparecimento = round(total_comparecimento_exato)
    gera_markdown(linhas, total_aptos, total_comparecimento)
    print(f"{len(linhas)} MRVs | {total_aptos:,} eleitores aptos | "
          f"~{total_comparecimento:,} comparecimento estimado (taxa por domicílio, 2022, não oficial)"
          .replace(",", "."))


def gera_markdown(linhas, total_aptos, total_comparecimento):
    out = []
    out.append("# MRV x seção x comparecimento estimado — Dublin, 1º turno 2026\n")
    out.append(
        "Junta a designação oficial de MRVs do DJE/TRE-DF (Ano 2026 n. 139, "
        "04/08/2026 — convocação de mesários, Irlanda/Dublin) ao eleitorado "
        "apurado em `saidas/dados.json` (fonte: TSE, `data/raw/`), com "
        "estimativa de comparecimento por seção usando a taxa de 2022 do "
        "domicílio de origem de cada seção "
        "(`handoff_agregacao_dublin_2026.md`).\n"
    )
    out.append(
        "## Aviso sobre a coluna de comparecimento\n\n"
        "**Não há, em nenhum arquivo deste repositório, uma estimativa de "
        "comparecimento por seção publicada pelo TSE ou pelo Cartório "
        "Eleitoral.** O que existe é o número de **eleitores aptos** "
        "(`QT_ELEITOR_SECAO`) por seção — dado oficial — e, em "
        "`handoff_agregacao_dublin_2026.md`, uma taxa de comparecimento de "
        "**2022** por domicílio/condado (não por seção), com qualidade "
        "desigual: `direto` (dado do próprio domicílio), `proxy` (domicílio "
        "parecido usado como substituto) ou `genérico` (taxa média nacional "
        "de abstenção). A coluna **Comparecimento estimado** abaixo aplica "
        "essa taxa a cada seção conforme seu domicílio predominante — já "
        "verificado seção a seção contra os totais do handoff (bate em "
        "todas as 15 localidades). Ainda assim, é uma **taxa de 2022 "
        "aplicada a 2026**, não uma projeção validada pelo TSE/Cartório "
        "Eleitoral para este pleito — trate como estimativa de trabalho, "
        "de qualidade heterogênea entre localidades (ver coluna "
        "**Qualidade**).\n"
    )
    out.append(
        "## Tabela\n\n"
        "| MRV | Seção principal (Dublin) | Comparecimento estimado | "
        "Seção agregada | Origem (taxa · qualidade) | "
        "Eleitores aptos (agregada) | Comparecimento estimado (agregada) | "
        "**Total aptos** | **Total comparecimento estimado** |\n"
        "|---|---|---|---|---|---|---|---|---|"
    )
    for l in linhas:
        if l["secao_agregada"]:
            sec_a = f"{l['secao_agregada']:04d}"
            origem = f"{l['origem_agregada']} ({l['taxa_agregada']:.1%} · {l['qualidade_agregada']})"
            elei_a = l["eleitores_agregada"]
            comp_a = round(elei_a * l["taxa_agregada"])
        else:
            sec_a = "—"
            origem = "—"
            elei_a = 0
            comp_a = 0
        comp_p = round(l["eleitores_principal"] * l["taxa_principal"])
        out.append(
            f"| MRV {l['mrv']} | {l['secao_principal']:04d} "
            f"({l['eleitores_principal']} aptos · {l['taxa_principal']:.0%} · "
            f"{l['qualidade_principal']}) | {comp_p} | {sec_a} | {origem} | "
            f"{elei_a} | {comp_a} | **{l['total_aptos']}** | "
            f"**{l['comparecimento_estimado']}** |"
        )
    fmt = lambda n: f"{int(n):,}".replace(",", ".")
    out.append(
        f"| **Total (28 MRVs)** | | | | | | | **{fmt(total_aptos)}** | "
        f"**{fmt(total_comparecimento)}** |\n"
    )
    out.append(
        "## Fontes\n\n"
        "- **Designação MRV → seção:** Diário da Justiça Eletrônico do "
        "TRE-DF, Ano 2026 n. 139 (04/08/2026), \"Convocação Mesários — "
        "Justiça Eleitoral, Irlanda, Apoio e Mesários Dublin\", p. 915–921.\n"
        "- **Eleitores aptos por seção:** `saidas/dados.json`, gerado por "
        "`scripts/mapa_agregacoes.py` a partir de "
        "`data/raw/eleitorado_local_votacao_2026_ZZ.csv` (TSE, 13/08/2026) "
        "e `data/raw/Filtrado_Dublin.csv` (TSE, 14/07/2026); reconciliado "
        "contra `QT_ELEITOR_ELEICAO_FEDERAL`.\n"
        "- **Taxa de comparecimento por domicílio (2022):** "
        "`handoff_agregacao_dublin_2026.md`, seção 2 — não oficial, "
        "qualidade do dado varia por localidade (ver coluna Qualidade na "
        "tabela); pendente de validação por fonte primária (ex.: "
        "resultado seção a seção de 2022 do TSE).\n"
    )
    (SAIDAS / "mrv_secoes_comparecimento.md").write_text(
        "\n".join(out) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
