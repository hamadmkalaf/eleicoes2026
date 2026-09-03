"""Junta a designacao oficial de MRVs (DJE/TRE-DF) ao eleitorado por secao.

Fonte da designacao MRV -> secao principal: Diario da Justica Eletronico do
TRE-DF, Ano 2026 n. 139, disponibilizado em 04/08/2026 ("Convocacao de
mesarios - Justica Eleitoral, Irlanda, Apoio e Mesarios Dublin"), paginas
915-921. E o unico documento que atribui numero de MRV as 28 urnas de
Dublin; o pipeline desta pasta (parse_dados.py / mapa_agregacoes.py) so
conhece a secao principal, nao o numero de MRV.

QT_ELEITOR_SECAO (aqui "Eleitores aptos") e dado oficial do TSE. Nao ha, em
nenhum arquivo de data/raw/, uma estimativa de comparecimento por secao
publicada pelo TSE ou pelo Cartorio Eleitoral. A unica referencia a taxa de
comparecimento no repositorio esta em contexto_eleicoes_dublin_2026.md
(secao 1): 74% para secoes domiciliadas em Dublin e ~50% para secoes do
interior, taxas de 2022 citadas de memoria de conversa anterior e marcadas
la mesmo como "ainda sujeitas a validacao final com o Cartorio
Eleitoral/TSE" -- nao e um numero oficial nem por secao, e sim uma taxa
unica de 2022 aplicada por origem (Dublin x interior). Esse calculo esta
isolado abaixo para poder ser substituido assim que houver dado oficial de
comparecimento por secao (ex.: resultado por secao das eleicoes de 2022).
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

TAXA_DUBLIN = 0.74
TAXA_INTERIOR = 0.50


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

    linhas = []
    total_aptos = 0
    total_comparecimento = 0
    for mrv in sorted(MRV_SECAO_PRINCIPAL):
        secao_p = MRV_SECAO_PRINCIPAL[mrv]
        urna = urnas[secao_p]
        secao_a = _secao_agregada(urna)

        eleitores_p = urna["Eleitores_principal"]
        eleitores_a = urna["Eleitores_agregada"]
        origem_a = secoes[secao_a]["Residencia_predominante"] if secao_a else None

        eleitores_dublin = eleitores_p + (eleitores_a if origem_a == "DUBLIN" else 0)
        eleitores_interior = eleitores_a if (secao_a and origem_a != "DUBLIN") else 0
        comparecimento = round(
            eleitores_dublin * TAXA_DUBLIN + eleitores_interior * TAXA_INTERIOR
        )

        total_aptos += urna["Total_combinado"]
        total_comparecimento += comparecimento

        linhas.append({
            "mrv": mrv,
            "secao_principal": secao_p,
            "secao_agregada": secao_a,
            "origem_agregada": origem_a,
            "eleitores_principal": eleitores_p,
            "eleitores_agregada": eleitores_a,
            "total_aptos": urna["Total_combinado"],
            "comparecimento_estimado": comparecimento,
        })

    assert total_aptos == dados["total_eleitores"], (
        f"Soma dos 28 MRVs ({total_aptos}) != total do repositorio "
        f"({dados['total_eleitores']})"
    )

    gera_markdown(linhas, total_aptos, total_comparecimento)
    print(f"{len(linhas)} MRVs | {total_aptos:,} eleitores aptos | "
          f"~{total_comparecimento:,} comparecimento estimado (taxa 2022, nao oficial)"
          .replace(",", "."))


def gera_markdown(linhas, total_aptos, total_comparecimento):
    out = []
    out.append("# MRV x seção x comparecimento estimado — Dublin, 1º turno 2026\n")
    out.append(
        "Junta a designação oficial de MRVs do DJE/TRE-DF (Ano 2026 n. 139, "
        "04/08/2026 — convocação de mesários, Irlanda/Dublin) ao eleitorado "
        "apurado em `saidas/dados.json` (fonte: TSE, `data/raw/`).\n"
    )
    out.append(
        "## Aviso sobre a coluna de comparecimento\n\n"
        "**Não há, em nenhum arquivo deste repositório, uma estimativa de "
        "comparecimento por seção publicada pelo TSE ou pelo Cartório "
        "Eleitoral.** Os dois CSVs em `data/raw/` trazem apenas o número de "
        "**eleitores aptos** (`QT_ELEITOR_SECAO`), não comparecimento "
        "esperado.\n\n"
        "A coluna **Comparecimento estimado** abaixo é um cálculo derivado, "
        "não um dado oficial: aplica, seção a seção, a única taxa de "
        "comparecimento registrada no repositório — "
        f"`contexto_eleicoes_dublin_2026.md` cita **{TAXA_DUBLIN:.0%}** "
        "para seções domiciliadas em Dublin e "
        f"**{TAXA_INTERIOR:.0%}** para seções do interior, taxas de 2022 "
        "que o próprio documento marca como *\"ainda sujeitas a validação "
        "final com o Cartório Eleitoral/TSE\"* — não é uma taxa por seção, "
        "e sim uma taxa única por origem (Dublin vs. interior) aplicada a "
        "cada seção conforme a residência predominante do seu eleitorado. "
        "Trate como estimativa de trabalho, não como projeção validada.\n\n"
        "Se você localizar o comparecimento real por seção (ex.: resultado "
        "seção a seção das eleições de 2022, publicado pelo TSE), essa é a "
        "fonte que deveria substituir a taxa fixa usada aqui — "
        "`scripts/gera_mrv_comparecimento.py` foi escrito para isso, "
        "bastando trocar `TAXA_DUBLIN`/`TAXA_INTERIOR` por um valor por "
        "seção.\n"
    )
    out.append(
        "## Tabela\n\n"
        "| MRV | Seção principal | Seção agregada | Origem da agregada | "
        "Eleitores aptos (principal) | Eleitores aptos (agregada) | "
        "**Total aptos** | **Comparecimento estimado*** |\n"
        "|---|---|---|---|---|---|---|---|"
    )
    for l in linhas:
        sec_a = f"{l['secao_agregada']:04d}" if l["secao_agregada"] else "—"
        origem = l["origem_agregada"] or "—"
        out.append(
            f"| MRV {l['mrv']} | {l['secao_principal']:04d} | {sec_a} | "
            f"{origem} | {l['eleitores_principal']} | "
            f"{l['eleitores_agregada'] or 0} | **{l['total_aptos']}** | "
            f"**{l['comparecimento_estimado']}** |"
        )
    out.append(
        f"| **Total (28 MRVs)** | | | | | | **{total_aptos:,}**".replace(",", ".")
        + f" | **{total_comparecimento:,}*** |".replace(",", ".")
    )
    out.append(
        "\n\\* Estimado a 74% (origem Dublin) / 50% (origem interior) sobre "
        "os eleitores aptos — ver aviso acima. Não confundir com "
        "eleitores aptos, que é dado oficial (TSE).\n"
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
        "- **Taxa de comparecimento (74%/50%):** "
        "`contexto_eleicoes_dublin_2026.md`, seção 1 — não oficial, "
        "pendente de validação.\n"
    )
    (SAIDAS / "mrv_secoes_comparecimento.md").write_text(
        "\n".join(out) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
