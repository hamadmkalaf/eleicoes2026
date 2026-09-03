# MRV x seção x comparecimento estimado — Dublin, 1º turno 2026

Junta a designação oficial de MRVs do DJE/TRE-DF (Ano 2026 n. 139, 04/08/2026 — convocação de mesários, Irlanda/Dublin) ao eleitorado apurado em `saidas/dados.json` (fonte: TSE, `data/raw/`).

## Aviso sobre a coluna de comparecimento

**Não há, em nenhum arquivo deste repositório, uma estimativa de comparecimento por seção publicada pelo TSE ou pelo Cartório Eleitoral.** Os dois CSVs em `data/raw/` trazem apenas o número de **eleitores aptos** (`QT_ELEITOR_SECAO`), não comparecimento esperado.

A coluna **Comparecimento estimado** abaixo é um cálculo derivado, não um dado oficial: aplica, seção a seção, a única taxa de comparecimento registrada no repositório — `contexto_eleicoes_dublin_2026.md` cita **74%** para seções domiciliadas em Dublin e **50%** para seções do interior, taxas de 2022 que o próprio documento marca como *"ainda sujeitas a validação final com o Cartório Eleitoral/TSE"* — não é uma taxa por seção, e sim uma taxa única por origem (Dublin vs. interior) aplicada a cada seção conforme a residência predominante do seu eleitorado. Trate como estimativa de trabalho, não como projeção validada.

Se você localizar o comparecimento real por seção (ex.: resultado seção a seção das eleições de 2022, publicado pelo TSE), essa é a fonte que deveria substituir a taxa fixa usada aqui — `scripts/gera_mrv_comparecimento.py` foi escrito para isso, bastando trocar `TAXA_DUBLIN`/`TAXA_INTERIOR` por um valor por seção.

## Tabela

| MRV | Seção principal | Seção agregada | Origem da agregada | Eleitores aptos (principal) | Eleitores aptos (agregada) | **Total aptos** | **Comparecimento estimado*** |
|---|---|---|---|---|---|---|---|
| MRV 1 | 0511 | 1100 | ROSCOMMON | 400 | 182 | **582** | **387** |
| MRV 2 | 0512 | 2855 | LONGFORD | 400 | 76 | **476** | **334** |
| MRV 3 | 0513 | 1105 | MAYO | 400 | 102 | **502** | **347** |
| MRV 4 | 0517 | 1292 | CAVAN | 400 | 113 | **513** | **352** |
| MRV 5 | 1160 | 3845 | LIMERICK | 400 | 73 | **473** | **332** |
| MRV 6 | 1352 | 0522 | DONEGAL | 400 | 62 | **462** | **327** |
| MRV 7 | 3054 | 1099 | KERRY | 400 | 54 | **454** | **323** |
| MRV 8 | 3078 | 2847 | LEITRIM | 400 | 29 | **429** | **310** |
| MRV 9 | 3108 | 3422 | GALWAY | 398 | 358 | **756** | **474** |
| MRV 10 | 3142 | 1278 | LIMERICK | 398 | 395 | **793** | **492** |
| MRV 11 | 3161 | 3307 | CORK | 397 | 394 | **791** | **491** |
| MRV 12 | 3179 | 0530 | WESTMEATH | 398 | 278 | **676** | **434** |
| MRV 13 | 3216 | 0527 | CLARE | 398 | 173 | **571** | **381** |
| MRV 14 | 3229 | 3821 | CORK | 398 | 208 | **606** | **399** |
| MRV 15 | 3245 | 0519 | CORK | 397 | 384 | **781** | **486** |
| MRV 16 | 3302 | 3181 | OUTROS LOCAIS DA IRLANDA | 396 | 375 | **771** | **481** |
| MRV 17 | 3305 | 0521 | GALWAY | 397 | 370 | **767** | **479** |
| MRV 18 | 3306 | 0518 | OUTROS LOCAIS DA IRLANDA | 396 | 370 | **766** | **478** |
| MRV 19 | 3308 | — | — | 399 | 0 | **399** | **295** |
| MRV 20 | 3309 | 1314 | WATERFORD | 398 | 217 | **615** | **403** |
| MRV 21 | 3311 | 3913 | DUBLIN | 397 | 233 | **630** | **466** |
| MRV 22 | 3313 | 3889 | DUBLIN | 397 | 400 | **797** | **590** |
| MRV 23 | 3315 | 3778 | DUBLIN | 395 | 397 | **792** | **586** |
| MRV 24 | 3322 | 3752 | DUBLIN | 398 | 396 | **794** | **588** |
| MRV 25 | 3442 | — | — | 398 | 0 | **398** | **295** |
| MRV 26 | 3688 | — | — | 400 | 0 | **400** | **296** |
| MRV 27 | 3832 | — | — | 400 | 0 | **400** | **296** |
| MRV 28 | 3862 | — | — | 400 | 0 | **400** | **296** |
| **Total (28 MRVs)** | | | | | | **16.794** | **11.418*** |

\* Estimado a 74% (origem Dublin) / 50% (origem interior) sobre os eleitores aptos — ver aviso acima. Não confundir com eleitores aptos, que é dado oficial (TSE).

## Fontes

- **Designação MRV → seção:** Diário da Justiça Eletrônico do TRE-DF, Ano 2026 n. 139 (04/08/2026), "Convocação Mesários — Justiça Eleitoral, Irlanda, Apoio e Mesários Dublin", p. 915–921.
- **Eleitores aptos por seção:** `saidas/dados.json`, gerado por `scripts/mapa_agregacoes.py` a partir de `data/raw/eleitorado_local_votacao_2026_ZZ.csv` (TSE, 13/08/2026) e `data/raw/Filtrado_Dublin.csv` (TSE, 14/07/2026); reconciliado contra `QT_ELEITOR_ELEICAO_FEDERAL`.
- **Taxa de comparecimento (74%/50%):** `contexto_eleicoes_dublin_2026.md`, seção 1 — não oficial, pendente de validação.

