# MRV x seção x comparecimento estimado — Dublin, 1º turno 2026

Junta a designação oficial de MRVs do DJE/TRE-DF (Ano 2026 n. 139, 04/08/2026 — convocação de mesários, Irlanda/Dublin) ao eleitorado apurado em `saidas/dados.json` (fonte: TSE, `data/raw/`), com estimativa de comparecimento por seção usando a taxa de 2022 do domicílio de origem de cada seção (`handoff_agregacao_dublin_2026.md`).

## Aviso sobre a coluna de comparecimento

**Não há, em nenhum arquivo deste repositório, uma estimativa de comparecimento por seção publicada pelo TSE ou pelo Cartório Eleitoral.** O que existe é o número de **eleitores aptos** (`QT_ELEITOR_SECAO`) por seção — dado oficial — e, em `handoff_agregacao_dublin_2026.md`, uma taxa de comparecimento de **2022** por domicílio/condado (não por seção), com qualidade desigual: `direto` (dado do próprio domicílio), `proxy` (domicílio parecido usado como substituto) ou `genérico` (taxa média nacional de abstenção). A coluna **Comparecimento estimado** abaixo aplica essa taxa a cada seção conforme seu domicílio predominante — já verificado seção a seção contra os totais do handoff (bate em todas as 15 localidades). Ainda assim, é uma **taxa de 2022 aplicada a 2026**, não uma projeção validada pelo TSE/Cartório Eleitoral para este pleito — trate como estimativa de trabalho, de qualidade heterogênea entre localidades (ver coluna **Qualidade**).

## Tabela

| MRV | Seção principal (Dublin) | Comparecimento estimado | Seção agregada | Origem (taxa · qualidade) | Eleitores aptos (agregada) | Comparecimento estimado (agregada) | **Total aptos** | **Total comparecimento estimado** |
|---|---|---|---|---|---|---|---|---|
| MRV 1 | 0511 (400 aptos · 74% · direto) | 296 | 1100 | ROSCOMMON (43.4% · proxy) | 182 | 79 | **582** | **375** |
| MRV 2 | 0512 (400 aptos · 74% · direto) | 296 | 2855 | LONGFORD (77.8% · direto) | 76 | 59 | **476** | **355** |
| MRV 3 | 0513 (400 aptos · 74% · direto) | 296 | 1105 | MAYO (54.4% · proxy) | 102 | 55 | **502** | **351** |
| MRV 4 | 0517 (400 aptos · 74% · direto) | 296 | 1292 | CAVAN (46.1% · proxy) | 113 | 52 | **513** | **348** |
| MRV 5 | 1160 (400 aptos · 74% · direto) | 296 | 3845 | LIMERICK (43.4% · proxy) | 73 | 32 | **473** | **328** |
| MRV 6 | 1352 (400 aptos · 74% · direto) | 296 | 0522 | DONEGAL (51.0% · genérico (0,49 abst.)) | 62 | 32 | **462** | **328** |
| MRV 7 | 3054 (400 aptos · 74% · direto) | 296 | 1099 | KERRY (54.4% · proxy) | 54 | 29 | **454** | **325** |
| MRV 8 | 3078 (400 aptos · 74% · direto) | 296 | 2847 | LEITRIM (51.0% · genérico (0,49 abst.)) | 29 | 15 | **429** | **311** |
| MRV 9 | 3108 (398 aptos · 74% · direto) | 295 | 3422 | GALWAY (48.1% · direto) | 358 | 172 | **756** | **467** |
| MRV 10 | 3142 (398 aptos · 74% · direto) | 295 | 1278 | LIMERICK (43.4% · proxy) | 395 | 171 | **793** | **466** |
| MRV 11 | 3161 (397 aptos · 74% · direto) | 294 | 3307 | CORK (53.3% · direto) | 394 | 210 | **791** | **504** |
| MRV 12 | 3179 (398 aptos · 74% · direto) | 295 | 0530 | WESTMEATH (46.1% · proxy) | 278 | 128 | **676** | **423** |
| MRV 13 | 3216 (398 aptos · 74% · direto) | 295 | 0527 | CLARE (64.9% · direto) | 173 | 112 | **571** | **407** |
| MRV 14 | 3229 (398 aptos · 74% · direto) | 295 | 3821 | CORK (53.3% · direto) | 208 | 111 | **606** | **405** |
| MRV 15 | 3245 (397 aptos · 74% · direto) | 294 | 0519 | CORK (53.3% · direto) | 384 | 205 | **781** | **498** |
| MRV 16 | 3302 (396 aptos · 74% · direto) | 293 | 3181 | OUTROS LOCAIS DA IRLANDA (60.0% · direto) | 375 | 225 | **771** | **518** |
| MRV 17 | 3305 (397 aptos · 74% · direto) | 294 | 0521 | GALWAY (48.1% · direto) | 370 | 178 | **767** | **472** |
| MRV 18 | 3306 (396 aptos · 74% · direto) | 293 | 0518 | OUTROS LOCAIS DA IRLANDA (60.0% · direto) | 370 | 222 | **766** | **515** |
| MRV 19 | 3308 (399 aptos · 74% · direto) | 295 | — | — | 0 | 0 | **399** | **295** |
| MRV 20 | 3309 (398 aptos · 74% · direto) | 295 | 1314 | WATERFORD (46.1% · proxy) | 217 | 100 | **615** | **395** |
| MRV 21 | 3311 (397 aptos · 74% · direto) | 294 | 3913 | DUBLIN (74.0% · direto) | 233 | 172 | **630** | **466** |
| MRV 22 | 3313 (397 aptos · 74% · direto) | 294 | 3889 | DUBLIN (74.0% · direto) | 400 | 296 | **797** | **590** |
| MRV 23 | 3315 (395 aptos · 74% · direto) | 292 | 3778 | DUBLIN (74.0% · direto) | 397 | 294 | **792** | **586** |
| MRV 24 | 3322 (398 aptos · 74% · direto) | 295 | 3752 | DUBLIN (74.0% · direto) | 396 | 293 | **794** | **588** |
| MRV 25 | 3442 (398 aptos · 74% · direto) | 295 | — | — | 0 | 0 | **398** | **295** |
| MRV 26 | 3688 (400 aptos · 74% · direto) | 296 | — | — | 0 | 0 | **400** | **296** |
| MRV 27 | 3832 (400 aptos · 74% · direto) | 296 | — | — | 0 | 0 | **400** | **296** |
| MRV 28 | 3862 (400 aptos · 74% · direto) | 296 | — | — | 0 | 0 | **400** | **296** |
| **Total (28 MRVs)** | | | | | | | **16.794** | **11.498** |

## Fontes

- **Designação MRV → seção:** Diário da Justiça Eletrônico do TRE-DF, Ano 2026 n. 139 (04/08/2026), "Convocação Mesários — Justiça Eleitoral, Irlanda, Apoio e Mesários Dublin", p. 915–921.
- **Eleitores aptos por seção:** `saidas/dados.json`, gerado por `scripts/mapa_agregacoes.py` a partir de `data/raw/eleitorado_local_votacao_2026_ZZ.csv` (TSE, 13/08/2026) e `data/raw/Filtrado_Dublin.csv` (TSE, 14/07/2026); reconciliado contra `QT_ELEITOR_ELEICAO_FEDERAL`.
- **Taxa de comparecimento por domicílio (2022):** `handoff_agregacao_dublin_2026.md`, seção 2 — não oficial, qualidade do dado varia por localidade (ver coluna Qualidade na tabela); pendente de validação por fonte primária (ex.: resultado seção a seção de 2022 do TSE).

