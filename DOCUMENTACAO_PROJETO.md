# Documentação consolidada do projeto — Eleições 2026, posto de Dublin (RDS Ballsbridge, Hall 2)

> Consolidação feita em **06/09/2026** na branch
> `claude/project-analysis-documentation-w49q34`, que reúne a **última versão de
> cada etapa** do projeto (antes espalhadas por 12 branches e 10 pull requests
> abertos). Uma cópia congelada do mesmo estado está na branch
> **`backup/consolidado-2026-09-06`**, de onde qualquer arquivo ou commit de
> qualquer etapa pode ser resgatado (ver §10). As branches originais não foram
> apagadas nem alteradas.

---

## Sumário

0. [Visão geral do projeto](#0-visão-geral-do-projeto)
1. [Agregação final: seções → MRVs e comparecimento esperado](#1-agregação-final-seções--mrvs-e-comparecimento-esperado)
2. [Planta-base do Hall 2](#2-planta-base-do-hall-2)
3. [Prancheta e seus cenários](#3-prancheta-e-seus-cenários)
4. [Simulados de fluxo](#4-simulados-de-fluxo)
5. [Dimensões e plano do Ring 3](#5-dimensões-e-plano-do-ring-3)
6. [Plano de sinalização externo](#6-plano-de-sinalização-externo)
7. [Expectativa de horários de pico](#7-expectativa-de-horários-de-pico)
8. [Revisão dos pull requests](#8-revisão-dos-pull-requests)
9. [Inconsistências entre etapas e pendências consolidadas](#9-inconsistências-entre-etapas-e-pendências-consolidadas)
10. [Como reproduzir, e como resgatar algo do backup](#10-como-reproduzir-e-como-resgatar-algo-do-backup)

---

## 0. Visão geral do projeto

### O problema

Organizar a votação do **1º turno de 04/10/2026 (8h–17h)** da zona eleitoral de
Dublin, Irlanda, concentrada num único local: o **Royal Dublin Society, Hall 2**
(RDS, Merrion Road, Ballsbridge, Dublin 4). Configuração fixada pelo TRE depois
de negociação encerrada: **28 urnas, 28 mesas receptoras (1:1)**, identificação
por **caderno físico**, espaço contratado **Hall 2 + Ring 3 (descoberto)**,
locado desde a véspera.

| Número-chave | Valor | Fonte |
|---|---|---|
| Eleitores aptos | **16.794** | CSV do TSE de 13/08/2026 |
| Seções | **51** (32 domiciliadas em Dublin, 19 no interior da Irlanda) | idem |
| Urnas / MRVs | **28** (23 com duas seções, 5 com uma) | mapa de agregações do TSE + DJE/TRE-DF |
| Eleitores do interior que votam em Dublin | 4.213 (25%) | perfil do eleitorado |
| Faixa de aptos por urna | 398 a 797 | pipeline da etapa 1 |
| Comparecimento esperado (taxas de 2022) | **~11.416–11.498** (ver §1.4 e §9.1) | estimativa, não oficial |
| Urnas críticas (duas seções de Dublin) | **3313 (590), 3322 (588), 3315 (586)** | etapa 1 e 5 |
| Hall 2 | 50,3 × 44,4 m, 2.179 m² úteis, pé-direito 7 m, 18 portas | planta do RDS medida em `scripts/salao.py` |
| Ring 3 | ~39 × 35 m (±10–15%), capacidade planejada 1.402 pessoas | fotogrametria, etapa 5 |
| Orçamento revisado do 1º turno | EUR 15.703,32 | `contexto_eleicoes_dublin_2026.md` §6 |

### As sete etapas e onde vivem

| # | Etapa | Branch(es) de origem | PR(s) | Último commit | Entregáveis principais |
|---|---|---|---|---|---|
| 1 | Agregação final e comparecimento por seção | `claude/dublin-electoral-sections-3odh1w` (base), `claude/mrv-secoes-eleitorais-rjvkxf` | #3 | 03/09 | `saidas/Dublin_2026_agregacoes.xlsx`, `saidas/dados.json`, `saidas/dublin_agregacoes.html`, `saidas/mrv_secoes_comparecimento.md`, `data/mrv_secoes.json` |
| 2 | Planta-base do Hall 2 | `deisgn-fluxo` | #1 | 03/09 | `saidas/planta_base.html/.svg`, `scripts/salao.py`, `scripts/planta_base.py`, `docs/CONTEXTO.md` |
| 3 | Prancheta e cenários | `deisgn-fluxo`, `claude/prancheta-delete-align-fv9e5o`, `claude/prancheta-busy-tables-scenario-h2iwgq`, `cenarios-hall2` (dados) | #1, #10, #7 | 06/09 | `saidas/editor.html`, `saidas/mesas.html`, `cenarios/*.json`, `scripts/mesas.py`, `scripts/gera_editor.py`, `scripts/cenarios.py`, `scripts/folgas_prancheta.py` |
| 4 | Simulados de fluxo | `claude/electoral-flow-simulator-5ihr5v`, `claude/simulador-fluxo-carregar-sinais-k4qxfw`, `claude/prancheta-delete-align-fv9e5o` (versão final dos arquivos), `claude/ring-3-dimensions-estimate-ge0jop` (`simula_fluxo.py`); rascunho superado em `claude/electoral-flow-simulation-c48buh` | #5, #9, #10, #6; #4 | 06/09 | `saidas/simulador_fluxo.html`, `simulador/*.js`, `scripts/gera_simulador.py`, `scripts/simula_fluxo.py`, `saidas/varredura_top.json` |
| 5 | Dimensões e plano do Ring 3 | `claude/ring-3-dimensions-estimate-ge0jop` | #6 | 06/09 | `saidas/plano_ring3.md`, `saidas/analise_gargalos.md`, `saidas/layout_ring3.svg/.png`, `scripts/layout_ring3.py` |
| 6 | Plano de sinalização externo | `claude/rds-ballsbridge-signage-points-kml93e` | #8 | 06/09 | `saidas/plano_sinalizacao.html`, `saidas/plano_sinalizacao.tmpl.html`, `scripts/gera_plano_sinalizacao.py`, `data/fotos/` (21 fotos) |
| 7 | Expectativa de horários de pico | `claude/eleicoes-brasileiras-horarios-pico-210a6l` | #2 | 03/09 | `pesquisa_horarios_pico_votacao.md` |

Documentos de contexto que atravessam as etapas: `contexto_eleicoes_dublin_2026.md`
(histórico da negociação, orçamento, contraproposta de agregação),
`handoff_agregacao_dublin_2026.md` (taxas de comparecimento de 2022 por
domicílio) e `docs/CONTEXTO.md` (documento de passagem do desenho de fluxo).

### Artefatos publicados (claude.ai)

| Peça | URL |
|---|---|
| Planta-base do Hall 2 | https://claude.ai/code/artifact/48817634-cbe1-426e-829f-5b5c674a688c |
| "Quantas mesas cabem no Hall 2" (planta das 28 mesas) | https://claude.ai/code/artifact/8ea7b55b-ec3f-4dd4-baaf-7702c4d3fcce |
| Prancheta do Hall 2 | https://claude.ai/code/artifact/f6a9b812-2b5e-4972-bb81-104b018e16b0 |
| Simulador de fluxo do Hall 2 | https://claude.ai/code/artifact/f2fea148-f618-4d3d-aa63-b0653f4139bc |
| Rota do Eleitor (plano de sinalização) | https://claude.ai/code/artifact/0320fda4-365e-406e-8aa4-1d0a1b535de8 |

Para atualizar qualquer uma, publique passando a URL em `url`; sem isso cria-se
um artefato separado.

### Linha do tempo

| Data | O que aconteceu |
|---|---|
| 13/08 | Análise das agregações de seções (base do repositório) |
| 28/08 | Upload da planta do RDS, do contexto consolidado e da prancheta manual (`PLANO COM FLUXOS MELHORADO.png`); primeira ideia de fluxo (ilhas) |
| 31/08 | Ideia 2 (28 MRVs nas paredes) |
| 01/09 | Planta-base fixada como referência; as duas ideias anteriores são apagadas a pedido; nova ideia das mesas pareadas com fileira recuada na fachada leste; planta fecha em 28 MRVs |
| 02/09 | MRVs numeradas 1–28; prancheta em escala; S2/S8 confirmadas no local como emergência sem recuo |
| 03/09 | MRV × seção (DJE/TRE-DF); pesquisa de horários de pico; simulador de fluxo; branch de dados `cenarios-hall2` |
| 05/09 | Plano do Ring 3 e análise de gargalos; cenário "Três polos"; plano de sinalização; simulador passa a carregar arranjos da prancheta |
| 06/09 | Ring 3 recalibrado (estoque de 200 separadores, reserva por entrada, evacuação, 3·9·3 balizas); levantamento fotográfico entra na sinalização; prancheta ganha alinhar/pares/apagar e biblioteca única de cenários; **consolidação desta branch** |

### Como a consolidação foi feita

Merges reais (não *squash*), em ordem, sobre a base `claude/dublin-electoral-sections-3odh1w`:

1. PR #3 (MRV × seção) e PR #2 (horários de pico): limpos.
2. PR #10 (que já contém todo o `deisgn-fluxo`, PR #1): limpo.
3. PR #9 (que contém o PR #5): conflitos *add/add* em quatro arquivos do
   simulador que o PR #10 havia copiado e evoluído (`scripts/gera_simulador.py`,
   `simulador/app.js`, `simulador/template.html`, `saidas/simulador_fluxo.html`).
   **Prevaleceu a versão do PR #10**, mais recente (06/09) e superconjunto da do
   PR #9. `saidas/varredura_top.json` entrou do PR #5.
4. PR #7 (Três polos): conflito em `cenarios/README.md`, resolvido juntando as
   duas versões. Os JSONs de cenário eram idênticos nos dois lados.
5. PR #6 (Ring 3) e PR #8 (sinalização): limpos.
6. `cenarios-hall2` (branch de dados, só `cenarios/*.json`) e PR #4 (rascunho
   superado do simulador): mesclados com `-s ours`, isto é, **o histórico ficou
   alcançável sem alterar a árvore**.
7. Ajuste de integração: `cenarios/planta_hall2.json` (PR #7) era cópia
   idêntica de `data/prancheta_hall2.json` e, na pasta de cenários, disparava
   aviso da biblioteca; `scripts/folgas_prancheta.py` passou a ler a cópia
   canônica e a duplicata saiu.

Todos os geradores foram reexecutados na árvore consolidada e reproduziram as
saídas versionadas **byte a byte**; os testes em Node passaram
(`teste_prancheta.js` 447/447, `teste_arranjos.js` 24/24, `teste_modelo.js`
com conservação de eleitores). As 12 branches originais são ancestrais do
HEAD desta branch (conferido com `git merge-base --is-ancestor`).

---

## 1. Agregação final: seções → MRVs e comparecimento esperado

### 1.1 Objetivo e fontes

Responder **quantos eleitores há em cada seção e em cada urna** e **onde eles
residem**, e depois ligar cada urna ao seu **número de MRV** oficial.

| Fonte | Data | O que dá |
|---|---|---|
| `data/raw/eleitorado_local_votacao_2026_ZZ.csv` (TSE) | 13/08/2026 | seção a seção no exterior: papel (Principal/Agregada), `NR_SECAO_PRINCIPAL`, `QT_ELEITOR_SECAO`, `QT_ELEITOR_ELEICAO_FEDERAL` |
| `data/raw/Filtrado_Dublin.csv` (TSE) | 14/07/2026 | perfil do eleitorado (seção × local de votação original × quantidade, faixa etária, biometria, deficiência) |
| `data/raw/mapa_agregacoes_TSE.png` | 13/08/2026 | mapa oficial de pares principal → agregada |
| DJE/TRE-DF, Ano 2026 n. 139, 04/08/2026, p. 915–921 | 04/08/2026 | convocação de mesários: **qual MRV (1 a 28) corresponde a qual seção principal** (transcrito em `scripts/gera_mrv_comparecimento.py` e `data/mrv_secoes.json`) |
| `handoff_agregacao_dublin_2026.md` | 03/09/2026 | taxas de comparecimento de **2022** por domicílio (Dublin 74%, Cork 53,3%, Galway 48,1%… com qualidade "direto", "proxy" ou "genérico") |

Os dois CSVs estão em latin-1, separados por `;`; o `Filtrado_Dublin.csv` vem
com a linha inteira entre aspas e precisa de desempacotamento
(`scripts/parse_dados.py`).

### 1.2 Método e validações

`scripts/mapa_agregacoes.py` monta as 28 urnas a partir dos pares do CSV e
**falha em vez de gravar saída errada** se: a soma por seção, por urna e do
perfil não fecharem em 16.794; as 51 seções não sobreviverem ou as urnas não
fecharem em 28; ou o total de cada urna não coincidir com
`QT_ELEITOR_ELEICAO_FEDERAL`, que o TSE já publica agregado na seção principal
(conferência independente, dois caminhos, mesmo número).

`scripts/gera_mrv_comparecimento.py` cruza a designação do DJE com
`saidas/dados.json` e aplica a taxa de 2022 do domicílio de origem de cada
seção; `assert` garante que os 28 MRVs somam 16.794.

### 1.3 Achados

- **Erro de digitação no PNG do TSE.** O mapa lista a agregada 3752 sob a
  principal 3222, que não existe em Dublin (é do Porto). A correta é a **3322**.
  O CSV prevalece; o caso está na aba `Inconsistencias`. Risco: a **3322 é ao
  mesmo tempo urna T1 crítica** e a que carrega o erro; se o erro se propagou
  para cadernos ou configuração da urna, a estação mais crítica chega mal
  configurada (ver `saidas/analise_gargalos.md` §6).
- **Cada seção é de uma única localidade.** As 28 principais são todas de
  Dublin (11.155 eleitores); as 23 agregadas trazem os condados do interior e
  mais 4 seções de Dublin.
- **Duas naturezas de urna cheia:** pares Dublin+Dublin (3313, 3322, 3315) e
  Dublin + condado inteiro (3142 com Limerick, 3161 e 3245 com Cork, 3305 e
  3108 com Galway). Os 4.213 eleitores do interior "chegam em rajada".
- **Perfil do eleitorado:** 80% entre 25 e 49 anos; só 211 eleitores com 60+ e
  85 com deficiência declarada (~296 prioritários em toda a zona); biometria
  coletada em 54,6% da zona, mas 65–71% nas três urnas críticas (coleta no
  cadastro, não garantia de leitor em Dublin).
- **Contexto da negociação** (`contexto_eleicoes_dublin_2026.md`): a proposta
  original do TSE era de 20 mesas/25 urnas sobre 14.626 aptos; a contraproposta
  mostrou que, por "casa dos pombos", com menos de 32 mesas há pares
  Dublin-Dublin forçados de ~583–590 comparecentes, e que só K ≥ 32 baixa esse
  pico. A negociação terminou em **28 urnas**, número com o qual todas as etapas
  seguintes trabalham.

### 1.4 Tabela mestra: MRV × seções × aptos × comparecimento esperado × numerações

Duas estimativas de comparecimento convivem no repositório. **Elas não são
intercambiáveis** (ver §9.1):

- **"74/50"**: 74% para eleitores domiciliados em Dublin e 50% para o interior,
  aplicado urna a urna. É a premissa de `scripts/salao.py`,
  `scripts/simula_fluxo.py`, do simulador (`medio (2022)`) e do plano de
  sinalização. Total: **11.416** (arredondando por urna em `simula_fluxo.py` e
  no simulador) ou **11.418** (arredondando por seção em `salao.py` e
  `gera_plano_sinalizacao.py`).
- **"por domicílio"**: a taxa de 2022 do condado de origem de cada seção
  agregada, de `handoff_agregacao_dublin_2026.md`. É a de
  `saidas/mrv_secoes_comparecimento.md`. Total: **11.498**.

| MRV (DJE) | Seção principal | Seção agregada | Origem da agregada | Aptos | Esperado 74/50 | Esperado por domicílio | Tier (§5) | Mesa/porta na sinalização (§6) |
|---|---|---|---|---|---|---|---|---|
| 1 | 511 | 1100 | Roscommon | 582 | 387 | 375 | T3 | M19 / C |
| 2 | 512 | 2855 | Longford | 476 | 334 | 355 | T3 | M1 / A |
| 3 | 513 | 1105 | Mayo | 502 | 347 | 351 | T3 | M2 / A |
| 4 | 517 | 1292 | Cavan | 513 | 352 | 348 | T3 | M10 / B |
| 5 | 1160 | 3845 | Limerick | 473 | 332 | 328 | T3 | M11 / B |
| 6 | 1352 | 522 | Donegal | 462 | 327 | 328 | T3 | M20 / C |
| 7 | 3054 | 1099 | Kerry | 454 | 323 | 325 | T3 | M21 / C |
| 8 | 3078 | 2847 | Leitrim | 429 | 310 | 311 | T3 | M12 / B |
| 9 | 3108 | 3422 | Galway | 756 | 474 | 467 | T2 | M22 / C |
| 10 | 3142 | 1278 | Limerick | 793 | 492 | 466 | T2 | M23 / C |
| 11 | 3161 | 3307 | Cork | 791 | 491 | 504 | T2 | M13 / B |
| 12 | 3179 | 530 | Westmeath | 676 | 434 | 423 | T3 | M3 / A |
| 13 | 3216 | 527 | Clare | 571 | 381 | 407 | T3 | M24 / C |
| 14 | 3229 | 3821 | Cork | 606 | 399 | 405 | T3 | M14 / B |
| 15 | 3245 | 519 | Cork | 781 | 486 | 498 | T2 | M4 / A |
| 16 | 3302 | 3181 | Outros locais da Irlanda | 771 | 481 | 518 | T2 | M5 / A |
| 17 | 3305 | 521 | Galway | 767 | 479 | 472 | T2 | M15 / B |
| 18 | 3306 | 518 | Outros locais da Irlanda | 766 | 478 | 515 | T2 | M25 / C |
| 19 | 3308 | — | — | 399 | 295 | 295 | T4 | M26 / C |
| 20 | 3309 | 1314 | Waterford | 615 | 403 | 395 | T3 | M6 / A |
| 21 | 3311 | 3913 | Dublin | 630 | 466 | 466 | T3 | M16 / B |
| **22** | **3313** | 3889 | Dublin | 797 | **590** | 590 | **T1** | M7 / A |
| **23** | **3315** | 3778 | Dublin | 792 | **586** | 586 | **T1** | M27 / C |
| **24** | **3322** | 3752 | Dublin | 794 | **588** | 588 | **T1** | M17 / B |
| 25 | 3442 | — | — | 398 | 295 | 295 | T4 | M28 / C |
| 26 | 3688 | — | — | 400 | 296 | 296 | T4 | M8 / A |
| 27 | 3832 | — | — | 400 | 296 | 296 | T4 | M18 / B |
| 28 | 3862 | — | — | 400 | 296 | 296 | T4 | M9 / A |
| **Total** | | | | **16.794** | **11.418** | **11.498** | | |

Regra do DJE: MRV *k* é a *k*-ésima seção principal em ordem crescente de
número. **Não há comparecimento oficial por seção em nenhuma fonte do
repositório**; as duas colunas são taxas de 2022 aplicadas a 2026, estimativa
de trabalho a substituir quando houver dado do Cartório.

### 1.5 Arquivos e como rodar

```bash
pip install pandas openpyxl
cd scripts
python3 mapa_agregacoes.py          # saidas/Dublin_2026_agregacoes.xlsx e saidas/dados.json
python3 gera_pagina.py              # saidas/dublin_agregacoes.html
python3 gera_mrv_comparecimento.py  # saidas/mrv_secoes_comparecimento.md
```

- `saidas/Dublin_2026_agregacoes.xlsx`: abas `Urnas`, `Secoes`,
  `Residencia x Secao`, `Residencia x Urna`, `Inconsistencias`.
- `saidas/dados.json`: os dados estruturados que alimentam a página e **todas
  as etapas seguintes** (simulações, Ring 3, sinalização leem daqui).
- `data/mrv_secoes.json`: a mesma designação MRV → seção, no formato que o
  simulador consome.

---

## 2. Planta-base do Hall 2

### 2.1 O que é

A leitura acordada do salão, e só isso: o contorno medido do Hall 2, as 18
portas com um número por fachada e o pouco que já está decidido sobre cada
uma. **Nenhuma porta recebe papel de entrada ou de saída** na planta-base; essa
decisão é de etapas posteriores (e, como o §9.3 registra, as etapas posteriores
tomaram decisões divergentes entre si).

Geometria medida direto dos PDFs do RDS (`RDS_Hall_2_Floorplan_(1).pdf`, pág.
2, e a versão revisada com as duas portas de carga assinaladas), com escala de
**8,69 pt/m** aferida contra a ficha técnica impressa no documento (50,2 × 44,5
m, 2.238 m²). Está codificada em **`scripts/salao.py`, fonte única**: não se
remede o PDF nem se duplicam constantes.

| Grandeza | Valor |
|---|---|
| Salão | 50,3 m (leste-oeste) × 44,4 m (norte-sul), canto sudoeste recortado (7,8 × 7,0 m) |
| Piso útil | 2.179 m² (2.238 m² brutos na ficha) |
| Pé-direito | 7 m, sem colunas; treliças a 7 m são a única fixação com alcance visual sobre o salão inteiro |
| Portas | 18, somando 56,1 m de vão |
| Parede leste fora dos recuos de 3 m | 8,4 m (três trechos de 2,79 m) |
| Origem (0,0) | canto sudoeste útil; x cresce para leste, y para norte |

### 2.2 Numeração das portas (usar esta, não a do RDS)

Por fachada, na ordem de leitura do desenho: oeste → leste nas paredes norte e
sul, norte → sul nas paredes leste e oeste. O código do RDS (que numera folhas
de porta e não localiza nada) fica entre parênteses quando o interlocutor é o
RDS. A numeração é gerada por `scripts/planta_base.py`, não escrita à mão.

| Nº | Parede | Código RDS | De–até (m) | Vão | Estado |
|---|---|---|---|---|---|
| N1 | norte | 2.13 | 7,41–9,44 | 2,03 m | **fechada** |
| N2 | norte | 2.14/2.15 | 20,66–24,22 | 3,56 m | **desbloqueada: saída do catering** |
| L1 | leste | 2.16/2.17 | 38,51–41,57 | 3,06 m | emergência, recuo de 3 m |
| L2 | leste | 2.18/2.19 | 26,66–29,72 | 3,06 m | emergência, recuo de 3 m |
| L3 | leste | 2.20/2.21 | 14,80–17,87 | 3,07 m | emergência, recuo de 3 m |
| L4 | leste | 2.22/2.23 | 2,95–6,01 | 3,06 m | emergência, recuo de 3 m |
| S1 | sul | carga oeste | 7,83–11,45 | 3,62 m | a definir (porta de carga) |
| S2 | sul | *sem código* | 13,25–14,45 | 1,20 m | **emergência confirmada no local (02/09), permanentemente aberta, sem recuo** |
| S3 | sul | 2.7 | 17,22–18,47 | 1,25 m | a definir |
| S4 | sul | 2.5/2.6 | 19,10–25,03 | 5,93 m | a definir |
| S5 | sul | 2.4 | 25,32–31,25 | 5,93 m | a definir |
| S6 | sul | 2.2/2.3 | 31,54–37,47 | 5,93 m | a definir |
| S7 | sul | 2.1 | 38,09–39,36 | 1,27 m | a definir |
| S8 | sul | *sem código* | 42,12–43,32 | 1,20 m | **emergência confirmada no local (02/09), permanentemente aberta, sem recuo** |
| S9 | sul | carga leste | 45,12–48,75 | 3,63 m | a definir (porta de carga) |
| O1 | oeste | acesso Hall 1 | 36,80–38,50 | 1,70 m | a definir |
| O2 | oeste | 2.10/2.11 | 19,36–22,43 | 3,07 m | a definir; único acesso aos sanitários |
| R1 | recorte | 2.8/2.9 | 3,00–6,50 | 3,50 m | a definir; parede do recorte, fora das fachadas |

"A definir" não é "disponível": significa que nada foi decidido. A posição e o
vão de S2 e S8 são **estimados sobre foto** (1,20 m, a ~1,8 m de cada porta de
carga), ainda sem medição no local.

### 2.3 O que já está decidido sobre o espaço

- A parede leste inteira é de emergência, com recuo de 3 m em torno de cada
  vão (o que a eliminava como parede de mesa até a fileira recuada do §3).
- N1 fechada; N2 desbloqueada para o catering, com caminho livre a definir.
- S2 e S8 são saídas de emergência permanentemente abertas, sem recuo
  (confirmação do chefe de segurança do RDS em 02/09/2026, a partir de fotos).
- Recuo das demais saídas de emergência (S3, S7, R1) **não determinado**.

### 2.4 Perguntas em aberto da planta-base (ainda sem resposta)

1. S1 e S9 (portas de carga) podem ficar abertas e travadas as nove horas, e a
   soleira serve a pedestre?
2. Quanto caminho livre o catering exige até N2, e por onde chega?
3. O recuo de 3 m vale para S3, S7 e R1?
4. Onde ficam as caixas de piso elétricas (decide canaletas atravessando a
   faixa protegida da fachada leste)?
5. O RDS aceita a **faixa protegida contínua** de 3 m na fachada leste no lugar
   dos envelopes por porta? (É a premissa de que 12 das 28 mesas dependem.)

### 2.5 Arquivos

| Arquivo | Papel |
|---|---|
| `scripts/salao.py` | fonte única da geometria (contorno, faces, portas, recuos), premissas, carga das urnas e simulação simples de fila; `python3 salao.py` imprime a capacidade de parede |
| `scripts/planta_base.py` + `planta_base_template.html` | gera `saidas/planta_base.svg` e `saidas/planta_base.html`; define a numeração N/L/S/O/R |
| `scripts/desenho.py`, `scripts/estilo_plano.css` | primitivas de desenho e estilo das peças de leitura |
| `docs/CONTEXTO.md` | documento de passagem: geometria, premissas, restrições, perguntas em aberto |
| `RDS_Hall_2_Floorplan_(1).pdf` | planta oficial do RDS |
| `PLANO COM FLUXOS MELHORADO.png` | prancheta manual do Posto (28/08), origem da numeração S1–S9 usada pelo Ring 3 e pela sinalização |

Histórico recuperável: as duas primeiras ideias de layout ("ilhas", 28/08, e
"tudo nas paredes", 31/08) foram apagadas em 01/09 a pedido, mas continuam no
histórico (`git show f1f3c7d:scripts/ideia1_ilhas.py`,
`git show f1f3c7d:saidas/ideia2_plano.html`, etc.).

---

## 3. Prancheta e seus cenários

### 3.1 A planta das 28 mesas (ideia das mesas pareadas)

Desenhada sobre a planta-base com o mobiliário informado pelo Posto:

| Elemento | Medida | Origem |
|---|---|---|
| Mesa de identificação (3 mesários) | 1,70 × 0,80 m | informado |
| Mesa de votação (urna) | redonda, Ø 0,90 m, encostada e voltada para a parede | informado |
| Eleitor votando entre urna e parede | 0,90 m | premissa |
| Passagem entre as duas mesas | 0,60 m | premissa |
| Assento do mesário projetado no corredor | 0,75 m | premissa |
| **Módulo da MRV** | **0,90 m de frente × 4,10 m de profundidade**, eixo perpendicular à parede | derivado |
| Corredor dentro do par (mesários frente a frente) | 2,50–3,00 m (adotado **3,00**) | informado / decidido |
| Espaço entre pares (de costas) | 1,00–1,50 m (adotado **1,50**) | informado / decidido |
| Passo do par ao longo da parede | 5,80–6,30 m (2 MRVs) | derivado |
| Recuo das saídas de emergência | 3,0 m | informado |

A virada foi a **fileira recuada da fachada leste**: em vez de encostar mesas
entre os envelopes de 3 m das quatro saídas (sobravam três pedaços de 2,79 m),
uma faixa protegida contínua de 3 m corre a fachada inteira e a fileira começa
logo depois, com 38,4 m contínuos. A fachada leste passa de zero para 12 mesas.
Custo: 133 m² de piso reservados (contra 108 m² dos envelopes), que precisam
ficar vazios o dia inteiro.

**Planta final (cenários A e B, mesmas 28 posições):** 8 na parede norte, 12
na fileira recuada da fachada leste, 2 na face norte do recorte, 6 na parede
oeste; fachada sul sem mesa nenhuma (as nove portas fragmentam os 42,5 m).
Numeração **1 a 28 em circuito horário a partir do canto noroeste**: 1–8 norte
(oeste → leste), 9–20 descendo a fileira leste, 21–22 no recorte, 23–28 subindo
a parede oeste. Capacidade com a mesma folga: 30; apertando ao mínimo: 34. As
duas excedentes retiradas foram escolhidas sobre o desenho (`mesas.AJUSTE_28`).

- **Cenário A:** S1 e S9 fechadas e sem papel.
- **Cenário B:** S1 e S9 em uso, cada uma com vestíbulo de 2 m e divisória. A
  validação geométrica acusa que os dois vestíbulos invadem zonas protegidas
  (S9 na faixa da fachada leste, 4,9 m²; S1 no recuo de R1, 6,0 m²).
- **Plano B** se o RDS não aceitar a faixa contínua: a fachada leste volta a
  valer 3 MRVs avulsas, o salão cai a 21, e a resposta é uma divisória exenta
  de 11,1 m no miolo, que leva a 29 (depende de aprovação do RDS e do Cartório).

Toda planta passa por `mesas.valida()`: módulo dentro do contorno, fora de vão
de porta e de zona protegida, sem sobreposição.

### 3.2 A prancheta (`saidas/editor.html`)

Planta manipulável em escala, gerada por `scripts/gera_editor.py` a partir de
`scripts/editor_template.html`. Não recalcula nada: consome as MRVs já
validadas por `mesas.py`. Ferramentas, na versão final (PR #10, 06/09):

| Ferramenta | O que faz |
|---|---|
| Cenário A / B | carrega a planta oficial |
| Mover, girar 90°, seleção múltipla, passo de encaixe (1–25 cm), grade de 1 m | posicionamento |
| Cotas vivas ao arrastar | mostra as distâncias enquanto a mesa se move |
| Medir | distância entre dois pontos (fita), guardada com o cenário em `medidas` |
| Reparear | recompõe o par ao corredor de 3,00 m com encosto a 1,50 m |
| Desfazer / refazer | histórico |
| **Alinhar à parede (N, L, O, S)** | move as mesas da parede escolhida só no eixo perpendicular, para a distância em que mais mesas já estão (ou a da mesa selecionada); recorte conta como parede |
| **Pares** | detecta pares por proximidade (não pela numeração), mede corredor de cada par (alvo 3,00, mín. 2,50) e folga até o par vizinho (alvo 1,50, mín. 1,00), lista mesas sem par; na planta oficial dá 14 pares de 3,00 m |
| Avisos de conflito | mesa fica vermelha se cair fora do salão, sobre zona protegida, sobre vão de porta ou sobre outra mesa |
| Salvar | guarda no `localStorage` do navegador **e** copia o JSON |
| Apagar / ocultar / mostrar ocultos | cenário local pode ser apagado; cenário da lista publicada só pode ser ocultado naquele navegador |
| Colar cenário… | abre um JSON colado |
| Copiar posições / Restaurar planta | utilitários |
| **Copiar tudo p/ o simulador** | põe a biblioteca inteira num JSON só, que o `Carregar arranjo…` do simulador aceita de uma vez |

Não há botão de baixar arquivo: a sandbox do artefato torna inerte qualquer
download disparado pela página, e a *capability* que resolveria isso é recusada
em artefato compartilhado por link.

`scripts/teste_prancheta.js` recorta do template os blocos que só dependem de
números e roda **447 verificações** contra as plantas reais (parede de encosto,
alinhamento, pares).

### 3.3 Biblioteca de cenários (`cenarios/`)

Um cenário grava **só as mesas que saíram da posição da planta oficial**
(`alteracoes`, por número), não as 28, para os diffs ficarem legíveis e as
mesas não citadas acompanharem a planta se ela mudar. Formato:

```json
{"nome": "…", "base": "A",
 "alteracoes": [{"n": 9, "x": 44.9, "y": 39.9, "rot": 180, "lado": 1}],
 "medidas": [{"a": [10.0, 5.0], "b": [10.0, 8.0]}],
 "criadoEm": "2026-09-03T12:00:00.000Z"}
```

`x`/`y` em metros na ancoragem do módulo (onde ele encosta na parede), `rot` é
o giro, `lado` o lado das cadeiras dos mesários.

**`scripts/cenarios.py` é o leitor único**, chamado pelos dois geradores
(prancheta e simulador). Junta `cenarios/` do checkout com `cenarios/` do branch
de dados `cenarios-hall2` (onde `scripts/salva_cenario.py` grava cenários novos
sem tocar em código; em colisão de `id` vence o branch de dados). A leitura
nunca é ao vivo: a lista é embutida na hora de gerar; cenário novo só aparece
para todo mundo depois de `salva_cenario.py` + regerar + republicar as duas
páginas.

Cenários versionados (todos sobre a base A):

| Arquivo | Nome | Criado em | Mesas movidas | O que é |
|---|---|---|---|---|
| `hamad1-20260905-155811.json` | Hamad1 | 05/09 15:51 | 6 (1, 2, 3, 4, 21, 22) | desenho do Posto |
| `hamad-2-20260905-160048.json` | Hamad 2 | 05/09 15:59 | 6 (1, 2, 3, 4, 21, 22) | variante do anterior |
| `tres-polos-20260905-182000.json` | Três polos · 22/23/24 separadas | 05/09 18:20 | 19 | análise do PR #7 (abaixo) |
| `hamad-3polos-20260905-184518.json` | Hamad_3polos | 05/09 18:45 | 28 | desenho do Posto sobre a ideia dos três polos; a conferência de pares acusa o par 5–22 com 2,45 m (abaixo do mínimo) e a conferência geométrica do simulador acusa a mesa 4 sobre o vão da porta N2 |

**Cenário "Três polos" (PR #7):** tira as mesas de posição 22, 23 e 24 do
aglomerado no canto sudoeste (onde a fila da 22 batia no módulo da 23 depois de
0,98 m, a pior medida do salão) e as distribui em três áreas, com corredor dos
dois lados: 22 → parede norte entre a mesa 8 e a coluna leste; 23 → fachada
leste, extremo sul; 24 → parede oeste, ao sul de O2. Para abrir espaço, as
duplas (5,6) e (7,8) recuam 2,00 m para oeste e a coluna leste (9 a 20) sobe
2,60 m. Resultado medido por `scripts/folgas_prancheta.py`: pior folga lateral
do salão sobe de 0,98 para 1,16 m; pior fila de 0,98 para 2,70 m; único custo
relevante, a fila da mesa 9 encurta de 4,29 para 2,70 m. Limite: a fachada leste
não comporta mesa isolada com 3,00 m dos dois lados (2,70 é o máximo). **Ponto
em aberto do próprio PR:** "22, 23 e 24" são posições da prancheta (numeração
geográfica), tomadas como as mesas de maior movimento; isso só é verdade se a
posição *k* receber a MRV *k* do DJE (ver §9.2).

### 3.4 Arquivos e como rodar

```bash
cd scripts
python3 salao.py         # confere dados e capacidade de parede
python3 planta_base.py   # planta-base
python3 mesas.py         # as 8 combinações da ideia, com validação
python3 gera_mesas.py    # saidas/mesas.json, SVGs e saidas/mesas.html
cd ..
python3 scripts/gera_editor.py     # saidas/editor_dados.json e editor.html (a prancheta)
node scripts/teste_prancheta.js    # 447 verificações
python3 scripts/folgas_prancheta.py [cenarios/<arquivo>.json]   # folga lateral e fila por mesa
python3 scripts/salva_cenario.py arquivo.json                    # grava no branch cenarios-hall2
```

| Arquivo | Papel |
|---|---|
| `scripts/mesas.py` | módulo, faixa protegida, regras de bloqueio, empacotamento, `AJUSTE_28`, `valida()`, `numera_mrv()` |
| `scripts/planta_mesas.py`, `gera_mesas.py`, `mesas_template.html` | desenhos e peça de leitura "Quantas mesas cabem no Hall 2" (`saidas/mesas.html`, `mesas.json`, `mesas_*.svg`) |
| `scripts/gera_editor.py`, `editor_template.html` | a prancheta (`saidas/editor.html`, `editor_dados.json`) |
| `scripts/cenarios.py`, `salva_cenario.py`, `cenarios/README.md` | biblioteca de cenários e seu fluxo |
| `scripts/folgas_prancheta.py` | mede folga lateral e profundidade de fila mesa a mesa, sai com código 1 em conflito |
| `data/prancheta_hall2.json` | a mesma geometria de `saidas/editor_dados.json` (sem a lista de cenários), congelada para o simulador e para o `folgas_prancheta.py` |

---

## 4. Simulados de fluxo

Há **três modelos de simulação** no repositório, de escopo e premissas
diferentes. Não somar nem comparar os resultados de um com os de outro sem
olhar a tabela do §9.4.

### 4.1 Simulação de fila por urna em `scripts/salao.py` (etapa 2, 01/09)

Passos de 5 min sobre o perfil de chegada 8/13/15/14/12/11/10/9/8% (8h–17h),
55 s por eleitor como ponto de projeto, uma urna por mesa, fila serial. Serve
para dimensionar baias de fila na parede.

| s/eleitor | fila de pico somada nas 28 | maior fila | urnas com fila > 10 | última a fechar |
|---|---|---|---|---|
| 45 | 33 | 12 | 2 | 17h00 |
| 50 | 100 | 32 | 3 | 17h00 |
| **55** | **241** | **57** | **6** | **17h20** |
| 60 | 436 | 84 | 11 | 18h05 |
| 70 | 929 | 136 | 14 | 19h35 |
| 90 | 2.165 | 230 | 23 | 22h45 |

Conclusão: o tempo de atendimento domina (fator 65 entre 45 e 90 s); o método
de identificação é decisão de layout tanto quanto de procedimento.

### 4.2 Modelo de fila por urna em `scripts/simula_fluxo.py` (etapa 5, 05–06/09)

Separa duas perguntas com soluções diferentes: **horário de fechamento**
(vazão pura, depende só do ciclo por eleitor) e **tamanho da fila** (curva de
chegada, dimensiona o Ring 3). Perfil de chegada por hora .12/.15/.16/.15/.12/
.09/.08/.07/.06 (e um "agudo" alternativo); comparecimento 74/50 = 11.416.
Como o eleitor no exterior vota só para Presidente, o voto é curto (~22 s) e a
busca no caderno domina.

| Arranjo da mesa | t_id | ciclo nas T1 | urnas atrasadas | fila total no pico | fecha |
|---|---|---|---|---|---|
| Serial (fila única, identifica depois vota) | 45 s | 67 s | 6/28 | 1.058 | 18h59 |
| Serial | 55 s | 77 s | 12/28 | 1.637 | 20h37 |
| Serial | 65 s | 87 s | 16/28 | 2.240 | 22h15 |
| Serial | 75 s | 100 s | 21/28 | 2.974 | 24h23 |
| Pipeline (identifica o próximo enquanto o anterior vota) | 55 s | 55 s | 1/28 | 439 | 17h01 |
| Pipeline | 65 s | 65 s | 3/28 | 935 | 18h39 |
| **Dois cadernos em paralelo, um por seção** | 45–75 s | 22–38 s | **0/28** | **0** | **17h00** |

Achados de `saidas/analise_gargalos.md`:

- Teto aritmético: 590 eleitores ÷ 540 min = **54,9 s por eleitor** na 3313. O
  precipício está entre 50 e 60 s; a 60 s falham exatamente 3313, 3322 e 3315.
- Comunicação dirigida (pedir às seções críticas que evitem o pico) reduz a
  fila de pico (113 → 52) mas **não altera o fechamento** (17h51 vs 17h50).
- **O gargalo é a mesa, não a urna**: 23 das 28 urnas acumulam duas seções, logo
  dois cadernos; com os 3 mesários é possível operar duas posições de
  identificação em paralelo alimentando uma urna. Fecha às 17h00 mesmo com
  caderno lento (t_id 110 s ainda fecha 17h03). É a negociação a abrir com o
  Cartório e não custa nada ao TRE.
- Estratificação: **T1** 3313, 3322, 3315 (586–590, 55 s disponíveis); **T2**
  3142, 3161, 3245, 3302, 3305, 3306, 3108 (474–492, 66–68 s); **T3** 13 urnas
  (310–466, 69–104 s); **T4** 3688, 3862, 3832, 3308, 3442 (295–296, 110 s). A
  folga de T3/T4 não absorve carga de T1: redistribui-se recurso, nunca eleitor.

### 4.3 Simulador de fluxo do Hall 2 (`saidas/simulador_fluxo.html`, etapa 4)

Simulação **por eventos discretos, eleitor a eleitor**, do dia inteiro, sobre
o arranjo real das 28 mesas. Motor em `simulador/modelo.js` (roda no navegador
e em Node), interface em `simulador/app.js` + `template.html`, tudo embutido
por `scripts/gera_simulador.py`. Três telas: **Premissas**, **Simulação**
(planta minuto a minuto) e **Resultado** (relatório com critérios aprovados, em
atenção ou reprovados).

Estágios do eleitor: chegada ao Ring 3 → triagem → fila da área → porta com
liberação controlada → buffer → checkpoint → fila da mesa → mesa (identificação
pelo caderno) e urna em pipeline → saída.

**Fixo em todos os cenários:** identificação pelo caderno; liberação controlada;
curva de chegada em fatias de 30 min das 7h às 17h com 8% chegando antes da
abertura, vale entre 12h e 15h e repique perto das 17h (apoiada na pesquisa do
§7); caminhada a 1,2 m/s; 0,6 m por pessoa em fila; 200 m de fita de unifila
contratados. **Premissas de quem simula:** portas de entrada e saída na fachada
sul; número e recorte das zonas; onde a numeração MRV começa e o sentido;
checkpoint (existência, distância, atendentes, segundos por eleitor); fila por
peso de mesa (leve ≤ 500 aptos, média 501–700, pesada > 700); política de
liberação (buffer, só se a mesa tem vaga, livre); vazão da porta; comparecimento
(pequeno 62/40, médio 74/50, grande 84/60); tempos de identificação (30/45/60/90
s) e voto, variabilidade; justificativas; triagem e capacidade do Ring 3
(padrão 800); dias simulados e semente.

Onze critérios de veredito: última mesa fecha até 17h30; mesas pesadas sem
"fome" (≤ 10 min); espera P90 ≤ 45 min; fila interna não volta até a porta;
checkpoint ≤ 80% de ocupação; portas equilibradas (≤ 1,25×); saída não corta
corredor de entrada; fita ≤ 200 m; filas cabem no espaço; Ring 3 comporta a
fila externa (≤ capacidade informada); triagem ≤ 75%.

**Cenário Claude**, escolhido por `simulador/varredura.js` entre **4.228
combinações** (resultado em `saidas/varredura_top.json`): três zonas
geográficas (parede norte 8 mesas, fachada leste 12, recorte + oeste 8);
entradas pelas três portas duplas do meio (S5 → norte, S6 → leste, S4 → oeste);
saídas pelas portas de carga S1 e S9; MRV 1 começa na parede leste (MRV 1–12
leste, 13–20 oeste, 21–28 norte); checkpoint a 14 m com 2/3/2 atendentes; filas
de 4/5/8 por classe; mesas 23 e 24 deslocadas ao norte. Resultado com 4 dias
simulados (`node simulador/teste_modelo.js claude 4`): última mesa fecha 17h03
(p50) / 17h05 (p90); espera P90 de 56 min (47 fora, 20 dentro); pico de 344
pessoas dentro e ~950–990 fora; 180 m de fita; zero cruzamentos. Ficam em
atenção a espera, o desequilíbrio entre portas (1,35×) e o Ring 3 com 800 de
capacidade informada (o plano do §5 chegou depois a 1.402).

**Biblioteca de arranjos (PR #9 e #10):** o bloco *Salão* lista, com miniatura
e conferência geométrica, três origens: planta oficial (A e B), arranjos da
prancheta embutidos pelo gerador (os quatro de `cenarios/`) e arranjos
carregados na hora (JSON colado ou arquivo, no `localStorage`). O simulador
consome a geometria de `saidas/editor_dados.json` (o arquivo que a prancheta
acabou de escrever) e avisa se `data/prancheta_hall2.json` ficar para trás.
`simulador/teste_arranjos.js` (24 asserções) cobre leitura dos dois formatos,
lixo, mesa repetida e detecção de conflito.

**Rascunho superado (PR #4):** `saidas/simulador_fluxo_hall2.html`, com um
esquema do salão desenhado à mão em vez da planta-base; o próprio PR o marca
como não utilizável. Não está na árvore consolidada; fica no histórico
(`git show 6e9c5d1:saidas/simulador_fluxo_hall2.html`).

### 4.4 Como rodar

```bash
python3 scripts/gera_editor.py         # antes, porque o simulador lê editor_dados.json
python3 scripts/gera_simulador.py      # saidas/simulador_fluxo.html
node simulador/teste_arranjos.js
node simulador/teste_modelo.js claude 16
node simulador/varredura.js 3          # demora alguns minutos
python3 scripts/simula_fluxo.py        # tabelas do §4.2
python3 -c "import sys; sys.path.insert(0,'scripts'); import simula_fluxo as m; m._relatorio_entradas()"
```

---

## 5. Dimensões e plano do Ring 3

Fonte: `saidas/plano_ring3.md` (versão de 06/09, commit `8d4b3be`), sustentada
por `saidas/analise_gargalos.md` e desenhada por `scripts/layout_ring3.py`
(`saidas/layout_ring3.svg`/`.png`). Escopo: **só o Ring 3**; o interior do Hall
2 tem necessidade própria de barreira, ainda não dimensionada.

### 5.1 Dimensões

Estimadas por fotogrametria sobre imagem aérea, escala ancorada em feições de
solo (0,15 m/px, quatro aferições convergentes). **Incerteza ±10–15% nas
dimensões lineares**: suficiente para dimensionar, insuficiente para contrato.

| Área | Dimensão | Superfície |
|---|---|---|
| Ring 3 | ~39 m (leste-oeste) × ~35 m (sul-norte) | ~1.365 m² |
| Apron pavimentado entre o Ring 3 e a fachada sul | ~60 × 14 m | ~850 m² |

### 5.2 Portas da fachada sul e seus papéis (decisão do plano do Ring 3)

Distâncias medidas na prancheta manual do Posto (`PLANO COM FLUXOS
MELHORADO.png`), convertidas pela largura declarada de 50,2 m.

| Porta | Distância do canto sudoeste | Papel |
|---|---|---|
| S1 | 9,5 m | — |
| **S2** | 13,7 m | **SAÍDA** |
| S3 | 17,7 m | — |
| **S4** | 21,9 m | **ENTRADA A** |
| **S5** | 28,1 m | **ENTRADA B** |
| **S6** | 34,3 m | **ENTRADA C** |
| S7 | 38,6 m | — |
| **S8** | 42,6 m | **SAÍDA** |
| S9 | 46,8 m | — |

As três entradas estão a 6,2 m uma da outra (passo apertado, que vem do
prédio); as saídas ficam nos flancos, fora do vão das entradas, de modo que quem
sai não cruza fila de entrada. A planta do RDS numera as mesmas aberturas como
2.1–2.23 com posições que não coincidem exatamente com a prancheta; a aferição
em campo resolve.

### 5.3 Layout

Entrada pelo **canto sudeste** (garganta de pré-triagem) → **corredor de
distribuição** de 2,5 m no fundo (bordo sul), de leste para oeste → três
**serpenteados** ("Disney queue"), C primeiro, depois B, depois A → **faixa de
acesso** de 2,5 m ao norte, livre de barreira (rota de maca e travessia sob
marshal) → portas S4/S5/S6.

| Parâmetro | Valor |
|---|---|
| Folga sul | 1,5 m |
| Corredor de distribuição (fundo) | 2,5 m |
| Profundidade do serpenteado | **28,5 m** |
| Faixa de acesso ao norte | 2,5 m, sem barreira |
| Balizas por corredor (largura 1,40 m) | **A 3 · B 9 · C 3** (número ímpar obrigatório) |
| Largura de cada bloco | A 4,2 · B 12,6 · C 4,2 m |
| Corredor de egresso entre blocos | 2,6 m |
| Baia de reserva (só A e C, dedicada, colada à baliza de entrada do bloco) | 6,4 m em cada flanco |
| Fechamento | 6,4 + 4,2 + 2,6 + 12,6 + 2,6 + 4,2 + 6,4 = 39,0 m; 1,5 + 2,5 + 28,5 + 2,5 = 35,0 m (o script falha se não fechar) |

| Entrada | Balizas | Serpenteado | Baia | **Total** | Quota |
|---|---|---|---|---|---|
| A → S4 | 3 | 171 | 274 | **445** | 31,7% |
| B → S5 | 9 | 513 | — | **513** | 36,6% |
| C → S6 | 3 | 171 | 274 | **445** | 31,7% |
| | | 855 | 547 | **1.402** | |

Decisões que o desenho registra: o bloco A é espelhado (entra pela baliza
oeste, encostada na baia); serpenteados desiguais (3·9·3) para **equilibrar
capacidade total**, não balizas (5·5·5 daria 559/285/559, disparidade de 274,
mesmo custo); a baia guarda gente **em massa** e o serpenteado **em ordem** (a
baia drena para o fim do serpenteado). Taxas de câmbio: +1 m de profundidade =
+49 pessoas por 9 separadores; +2 balizas = +114 por 27; +1 m de baia = +43 por 1.

### 5.4 Separadores de barreira (só Ring 3)

| # | Componente | Cálculo | Metros | Separadores |
|---|---|---|---|---|
| 1 | Balizas externas dos 3 blocos | 3 × 2 × 28,5 | 171,0 | 86 |
| 2 | Balizas internas | (2+8+2) × 27,1 | 325,2 | 163 |
| 3 | Corredor de distribuição | 2 × 36,0 − 3 vãos de 1,5 | 67,5 | 34 |
| 4 | Garganta de entrada | funil | 10,0 | 5 |
| 5 | Fechamento das baias (A e C) | 2 × (4,9 + 6,4) | 22,6 | 12 |
| | **Total do Ring 3** | | **596,3** | **300** |
| | Fornecidos pela organizadora (2 m × 1 m de altura) | 200 un. | −400,0 | −200 |
| | **A adquirir** | | **200,0** | **100 ≈ EUR 1.302** (EUR 6,51/m; ~8% do orçamento revisado) |

Esse estoque de 200 separadores de barreira externa é distinto dos **100
unifilas (200 m) do item (d) do orçamento** que o simulador e a sinalização
tratam como fita interna do Hall 2.

### 5.5 Atribuição das urnas às entradas

Proporcional à capacidade (quotas 31,7 / 36,6 / 31,7%), com uma urna T1 em cada
entrada. Saída atual de `simula_fluxo._relatorio_entradas()` (desvio máximo de
7 eleitores em 11.416):

| Entrada | Urnas | Esperado | Lista |
|---|---|---|---|
| A (S4) | 9 | 3.614 | 513, 1352, 3229, 3302, 3306, 3309, **3322**, 3688, 3832 |
| B (S5) | 10 | 4.185 | 511, 517, 3054, 3078, 3142, 3161, 3305, 3311, **3313**, 3442 |
| C (S6) | 9 | 3.618 | 512, 1160, 3108, 3179, 3216, 3245, 3308, **3315**, 3862 |

> As listas impressas em `plano_ring3.md` §6 (com 3313 em A, 3315 em B, 3322 em
> C e contagens 11/6/11) estão **defasadas** em relação ao script; a tabela de
> totais do mesmo §6 (9/10/9) já bate com o script. Ver §9.5.

### 5.6 O Ring 3 comporta a fila prevista?

| Arranjo da mesa | Fila total no pico | Cabe em Hall 2 (~1.100) + Ring 3 (1.402)? |
|---|---|---|
| Dois cadernos em paralelo | 0 | sim, o Ring 3 nem abre |
| Pipeline, 55 s | 439 | sim, só no Hall 2 |
| Serial, 55 s | 1.637 | sim, com os serpenteados |
| Serial, 65 s | 2.240 | sim, com o flanco aberto |
| Serial, 75 s | 2.974 | **não: transborda para a Merrion Road** |

**O Ring 3 é apólice contra erro de previsão, não solução do gargalo.** Quem
resolve é o arranjo de dois cadernos em paralelo.

### 5.7 Evacuação, tempo, acessibilidade, equipe

- **Evacuação:** densidade OK (1,43 p/m² no serpenteado, 1,50 na baia, limite
  2,0); grade de circulação ≥ 2,5 m (mínimo 1,2 m para maca). **Fragilidade: a
  saída única** pela garganta de 1,5 m leva 11,4 min para 1.402 pessoas, acima
  do alvo de 8 min. Recomendação: duas brechas de emergência de 2,0 m no
  perímetro sul e leste (evacuação cai a 3,1 min). Depende de saber se o
  perímetro do Ring 3 é fechado ou aberto.
- **Chuva:** outubro é o mês mais chuvoso de Dublin (76–79 mm); 12 dias de
  chuva pelas normais 1991–2020 (≥ 1 mm) ou 17–20 por fontes de limiar mais
  frouxo, isto é, 40–65% de probabilidade para o dia 4, fontes não comparáveis
  entre si. Mitigação: cobertura leve sobre os últimos 8–10 m de cada
  serpenteado.
- **Prioritários:** ~296 pessoas (211 com 60+ e 85 PcD), ~33 por hora no pico;
  nenhum entra no serpenteado (130 m de percurso); rota dedicada pelo apron
  com 1 agente.
- **Equipe:** 1 coordenador, 3 agentes de pré-triagem, 3 marshals de corredor, 3
  de porta, 1 de acessibilidade, 4–6 seguranças (dos 20 contratados): 15–17.

### 5.8 Pendências do plano do Ring 3

1. Aferir as dimensões do Ring 3 e a distância do seu bordo oeste ao canto
   sudoeste do Hall 2 (translada o conjunto para os eixos coincidirem com as
   portas).
2. Conciliar S1–S9 (prancheta) com 2.1–2.23 (planta do RDS).
3. Submeter o pedido de +100 separadores (~EUR 1.302) e dimensionar o interior
   do Hall 2 à parte.
4. Cotar cobertura leve para os serpenteados.
5. Verificar se o perímetro do Ring 3 é fechado; se for, abrir as duas brechas.
6. **Definir o arranjo da mesa receptora com o Cartório Eleitoral** (decide se
   o Ring 3 chega a ser usado).

---

## 6. Plano de sinalização externo

Fonte: `saidas/plano_sinalizacao.html` ("Rota do Eleitor RDS"), gerado por
`scripts/gera_plano_sinalizacao.py` a partir de `saidas/plano_sinalizacao.tmpl.html`
e de `saidas/dados.json`, com as 21 fotos de 24/08/2026 em `data/fotos/`.

### 6.1 A tese

O problema não é onde cabem placas, é **onde o eleitor para para pensar**. Cada
consulta ("qual a minha mesa?", "qual a minha porta?") custa 10–20 s; feita num
ponto estreito vira servidor de fila. A rota do RDS oferece ~150 m de caminhada
pela lateral leste como tempo morto aproveitável. Três regras: **uma consulta,
não duas** (seção → mesa → porta no mesmo painel); **consulta replicada** a cada
25–30 m em vez de um quadro grande no portão; **bifurcação sem informação nova**
(na porta, só a confirmação).

### 6.2 A rota e os oito pontos

Portão da Merrion Road → lateral leste do Hall 2 → Ring 3 → portas da fachada
sul → saída por S2/S8 sem reentrar no Ring 3.

| Ponto | Onde | O que decide | O que a peça diz | Peças |
|---|---|---|---|---|
| P0 Aproximação | calçada da Merrion Road, pontos de ônibus, outros portões do RDS | se está no lugar certo e por qual portão entra | "ELEIÇÕES BRASILEIRAS 2026 · Entrada de eleitores →" | 4 painéis |
| P1 Portão de entrada | no vão do portão | entrada confirmada; primeira consulta; desvio dos sem seção | pórtico + tabela mestra completa + "não sabe sua seção? →" | 1 pórtico, 3 painéis, 1 totem do balcão |
| P2 Corredor da lateral leste | nos três vãos entre as quatro saídas de emergência, a 10,75 / 22,50 / 33,90 m do canto norte, mais dois no gradil | nada; repete a consulta no tempo morto | a mesma tabela mestra + "Ring 3 →" | 3 painéis de 1,8 × 1,2 m + 2 lonas |
| P3 Garganta sudeste | funil de entrada do Ring 3, junto aos 3 agentes de pré-triagem | última consulta; divisão nos três serpenteados | tabela mestra + três totens com as faixas de mesas | 2 painéis, 3 totens de 3 m |
| P4 Cabeças dos serpenteados | início de cada bloco, no corredor de distribuição | confirmação; captura de quem errou enquanto cabe corrigir | corpo grande + faixa de mesas + "errou? volte →" | 3 totens, 1 faixa |
| P5 Portas de entrada | no vidro da fachada sul, lidas de dentro do serpenteado | só confirmação de que ali se entra | "ENTRADA" em 300 mm + faixa da cor da fila | 3 bandeirolas de fachada (vinil no vidro) |
| P6 Checkpoint interno | logo depois das portas | mesa → posição física | faixas suspensas por bloco + totem por mesa | 3 faixas, 28 totens |
| P7 Saídas S2 e S8 | flancos da fachada sul | encaminha para a rua | "SAÍDA / WAY OUT → Merrion Road" | 2 internos, 2 externos |

### 6.3 O que o levantamento fotográfico mudou (06/09)

- **A fachada do Hall 2 é uma cortina de vidro** de pé-direito inteiro, modulada
  pelos montantes nos vãos das portas: o item mais caro (letras das portas) vira
  vinil de vitrine, sem estrutura nem base.
- **As paredes do salão não aceitam adesivo** (bloco/tijolo na base, chapa
  metálica ondulada em cima). Fora, os painéis de P2 vão colados nas folhas das
  portas de serviço em aço ou parafusados nas terças; dentro, só as treliças a
  7 m, com fixação suspensa. Uma medida de trena decide o método: base lisa
  acima de 2,2 m → vinil; ~1,3 m → chapa rígida parafusada.
- **O RDS já usa letra para portão (Gate D, Gate G) e número para pavilhão ("2
  Shelbourne Hall")**, em azul-marinho com branco. Decisão da versão final:
  **as portas não são nomeadas**; o cartaz diz apenas ENTRADA com a faixa de cor
  da raia que descarrega ali; a identidade da fila mora na raia. As letras A/B/C
  ficam como rótulo interno de planejamento. Nossas peças nunca em azul-marinho
  com branco.
- **Código de cor das três filas: azul, âmbar e magenta**, distinguíveis em
  deuteranopia e protanopia; a cor nunca aparece sozinha, sempre com o número
  da mesa.
- **A placa EXIT** citada no briefing não aparece em nenhuma das 21 fotos (há
  "ENTRY" pintado no piso e uma placa em bronze, ambos de veículos); risco
  reescrito como dúvida.

### 6.4 Especificação

300 mm nas portas (legível a ~60 m); 120 mm nos totens de cabeça de fila (15 m,
acima dos guarda-chuvas) e nas setas do corredor (25 m em movimento); 18 mm no
corpo da tabela mestra; montagem ≥ 2,5 m; regra "sem base" (colar, amarrar,
abraçar, suspender); lona 440 g com ilhoses ou PVC alveolar 5 mm; PT + EN.
Razão de 1 mm de letra por 200 mm de distância, entre a regra da International
Sign Association (1:120) e o limite de acuidade (1:600), com ~25% de margem
para chuva, ângulo e céu encoberto.

### 6.5 Distribuição das mesas pelas portas (ilustrativa e reversível)

Equilibrada por **comparecimento esperado 74/50**, em serpentina sobre a lista
ordenada, o que separa as três mesas pesadas uma por porta; numeração M1–M28
contígua por porta para a placa poder dizer "Mesas 1–9".

| Porta | Cor | Mesas | Aptos | Esperado | Mais pesada |
|---|---|---|---|---|---|
| A | azul | 9 (M1–M9) | 5.418 | 3.667 | M7 = urna 3313 (590) |
| B | âmbar | 9 (M10–M18) | 5.403 | 3.713 | M17 = urna 3322 (588) |
| C | magenta | 10 (M19–M28) | 5.973 | 4.038 | M27 = urna 3315 (586) |

A correspondência M → urna está na tabela do §1.4. **A tabela mestra tem 51
linhas ordenadas por seção, não 28 por mesa**: são 23 seções agregadas, e um
eleitor da 3889 precisa encontrar "3889"; num quadro por mesa, ~7 mil
eleitores não se acham e vão ao balcão de dúvidas.

Dimensionamento de leitura: 21 chegadas/min em média, 38/min no pico (premissa
1,8×), 15 s por leitura (premissa) → ~10 posições simultâneas → 4 painéis de
1,2 m, ou o equivalente replicado ao longo do corredor.

### 6.6 Riscos e confirmações pendentes

- Confirmar o que há no portão (placa EXIT fixa ou marcação viária) e manter um
  agente humano ali nas duas primeiras horas.
- Medir a altura da base lisa e a distância real entre as saídas da parede
  leste (posições estimadas da planta reescalada para os 44 m informados).
- A identidade da fila depende inteiramente da disciplina de raia (do Ring 3
  até a soleira); se ela não se sustentar, a triagem cai toda no checkpoint.
- A fila se forma dentro de um **estacionamento em operação**: bloquear as
  vagas em frente às portas na véspera; acordo formal com o RDS sobre veículos.
- As três entradas a 6,2 m: a correção de rota tem de estar em P4, não na
  descarga.
- Numeração S1–S9 vs 2.1–2.23 a fechar em campo antes de imprimir.
- Fator de pico 1,8× é premissa, não medida; o precedente de Dublin 2022
  sugere fila que nunca esvazia em vez de pico isolado.
- Balcão "não sei minha seção" em P1, recuado, com 2–3 operadores e caderno
  impresso (Wi-Fi no portão não confirmado).
- Sinalizar a rota prioritária desde a rua (P0 e portão).
- **A numeração das mesas precisa estar congelada antes de qualquer impressão**;
  a decisão sobre os nomes das portas contamina todas as peças.

Próxima etapa já encaminhada: sinalização interna **por par de mesas, suspensa
nas treliças** (14 peças em vez de 28), condicionada a autorização de rigging
do RDS, plataforma elevatória na véspera e não obstruir luminária de
emergência, detector de fumaça ou placa de EXIT.

```bash
pip install Pillow            # para embutir as fotos
python3 scripts/gera_plano_sinalizacao.py   # falha se a tabela mestra não cobrir as 51 seções
```

---

## 7. Expectativa de horários de pico

Fonte: `pesquisa_horarios_pico_votacao.md` (03/09/2026), levantamento por busca
ampla restrito à eleição brasileira (domingo, 8h–17h, no país e no exterior).

### 7.1 O que existe e o que não existe

- **Não há estatística oficial e consolidada de comparecimento por hora** (TSE,
  TREs ou institutos). O TSE publica dicas de comportamento, não curva.
- Desde 2022 os **logs de urna com o horário de cada voto são dados públicos**
  (Portal de Dados Abertos do TSE). É o caminho para uma curva real, ainda não
  explorado por ninguém neste projeto.

### 7.2 O padrão qualitativo recorrente (2022 e 2024)

| Fase | Janela | Relato |
|---|---|---|
| Abertura e primeiras horas | de 1h30–2h antes das 8h até ~10h–11h | fila já formada antes da abertura; maior volume de chegada do dia |
| Meio do dia | ~12h–15h | movimento cai; seções "tranquilas, sem fila" |
| Final da tarde | ~16h–17h | repique de retardatários; a regra de que quem está na fila às 17h vota incentiva deixar para o fim; o TSE recomenda explicitamente não fazer isso |

Evidência no exterior (mesma eleição, mesmo domingo): Nova York 2022 com ~100
pessoas na fila 1h30 antes de abrir; Lisboa 2022 (~45 mil eleitores) com filas
desde duas horas antes e, no 2º turno, extensão do horário das 17h até as 20h
com ~4.000 na fila; Londres 2022 com fluxo rápido apesar do volume.

**Precedente direto: Dublin 2022.** No 1º turno, na Erin School of English,
filas de **2h30 a 3 horas** o dia inteiro e além das 17h (senhas a quem ainda
estava na fila); a Embaixada mudou o 2º turno para o **Croke Park**. No 2º turno
compareceram 7.492 de 11.946 aptos (62,7%).

### 7.3 Duas noções de pico, e qual importa

1. **Pico de chegada** (novos eleitores por hora): concentrado na abertura e na
   manhã, com repique menor perto do fechamento.
2. **Pico de fila acumulada** (chegada menos capacidade): pode durar **o dia
   inteiro** quando a capacidade é insuficiente, como em Dublin e Lisboa em
   2022, onde a fila nunca esvaziou.

Para dimensionar fluxo importa o segundo, e ele é dominado por **capacidade
instalada** (urnas, velocidade de identificação, layout), não pela hora. Isso
converge com o achado estrutural das etapas 1 e 5: o gargalo é o ciclo por
eleitor na mesa.

### 7.4 Limitações e como o resultado foi usado

A amostra de cidades não é aleatória (cobre os casos que viraram notícia) e a
evidência é jornalística e convergente, não série estatística. No projeto, a
pesquisa sustenta a **curva de chegada fixa do simulador** (§4.3: 8% antes da
abertura, vale 12h–15h, repique às 16h–16h30) e a leitura, no plano de
sinalização, de que o fator de pico 1,8× é premissa e de que a distribuição dos
painéis ao longo do corredor importa mais que o número.

---

## 8. Revisão dos pull requests

Todos os 10 PRs estão **abertos, em rascunho**, e todos apontam para a base
`claude/dublin-electoral-sections-3odh1w` exceto #9 (base #5) e #10 (base
`deisgn-fluxo`). Nenhum tem revisão ou CI. Esta branch consolidada contém o
conteúdo de todos; a decisão sobre fechá-los ou mesclá-los individualmente fica
para o Posto.

| PR | Título | Branch | Etapa | Estado do conteúdo | Como entrou aqui |
|---|---|---|---|---|---|
| [#1](https://github.com/hamadmkalaf/eleicoes2026/pull/1) | Desenha o fluxo de votação do RDS Hall 2 — ideia 1, em ilhas | `deisgn-fluxo` (22 commits, 28/08–03/09) | 2, 3 | **Corpo do PR defasado**: descreve a ideia 1 "em ilhas" e a ideia 2 "nas paredes", ambas apagadas em 01/09 (`f03203b`). O head entrega a planta-base, a ideia das mesas pareadas com fileira recuada (28 MRVs), a prancheta e o fluxo de cenários. | via PR #10 (que o contém) |
| [#2](https://github.com/hamadmkalaf/eleicoes2026/pull/2) | Pesquisa: horários de pico de comparecimento | `claude/eleicoes-brasileiras-horarios-pico-210a6l` (1 commit) | 7 | Só markdown, fontes com link; coerente com o head. | merge limpo |
| [#3](https://github.com/hamadmkalaf/eleicoes2026/pull/3) | Junta MRVs (DJE/TRE-DF) ao eleitorado por seção | `claude/mrv-secoes-eleitorais-rjvkxf` (2 commits) | 1 | O 2º commit trocou a estimativa binária 74/50 pela taxa por domicílio (total 11.498); o corpo do PR ainda cita "~11.418". Fonte da designação MRV é PDF do DJE transcrito à mão. | merge limpo |
| [#4](https://github.com/hamadmkalaf/eleicoes2026/pull/4) | WIP: interior flow scenario simulator | `claude/electoral-flow-simulation-c48buh` (1 commit) | 4 | Rascunho explicitamente não utilizável (esquema do salão desenhado à mão). Superado pelo #5. | `merge -s ours` (histórico preservado, arquivo fora da árvore) |
| [#5](https://github.com/hamadmkalaf/eleicoes2026/pull/5) | Adiciona simulador de fluxo do Hall 2 | `claude/electoral-flow-simulator-5ihr5v` (2 commits) | 4 | Motor, interface, varredura de 4.228 combinações, Cenário Claude, `data/mrv_secoes.json`, `data/prancheta_hall2.json`. Coerente. | via PR #9 |
| [#6](https://github.com/hamadmkalaf/eleicoes2026/pull/6) | Plano base do Ring 3 e análise de gargalos | `claude/ring-3-dimensions-estimate-ge0jop` (11 commits, 05–06/09) | 5, 4 | **Corpo do PR defasado** em relação ao head: cita serpenteado de 26 m, 5 balizas, 780 + 390 = 1.170 pessoas, 282 separadores, +82 ≈ EUR 1.068; o head (`8d4b3be`) tem 28,5 m, 3·9·3 balizas, 1.402 pessoas, 300 separadores, +100 ≈ EUR 1.302. Dentro do head, as listas de urnas por entrada do §6 do `plano_ring3.md` estão defasadas do script (§9.5). | merge limpo |
| [#7](https://github.com/hamadmkalaf/eleicoes2026/pull/7) | Cenário "Três polos" | `claude/prancheta-busy-tables-scenario-h2iwgq` (2 commits) | 3 | Cenário + `folgas_prancheta.py` + `planta_hall2.json` (cópia da geometria). O próprio PR registra que "22/23/24" são posições da prancheta, não urnas verificadas. | merge com conflito em `cenarios/README.md` (juntado); duplicata da geometria retirada |
| [#8](https://github.com/hamadmkalaf/eleicoes2026/pull/8) | Plano de sinalização | `claude/rds-ballsbridge-signage-points-kml93e` (5 commits, 05–06/09) | 6 | O corpo ainda recomenda "PORTA AZUL/AMARELA/ROXA"; o head decidiu "ENTRADA" sem nome + faixa de cor (azul/âmbar/magenta). O HTML gerado cita números do Ring 3 de uma versão anterior (560,2 m / 281 separadores / 780 + ~490 / faltam 362 m ≈ EUR 2.357), já superados pelo head do #6 (§9.6). | merge limpo |
| [#9](https://github.com/hamadmkalaf/eleicoes2026/pull/9) | Carrega arranjos da prancheta no simulador | `claude/simulador-fluxo-carregar-sinais-k4qxfw` (3 commits, sobre #5) | 4 | Biblioteca de arranjos, conferência geométrica, `teste_arranjos.js`. A nota "Fora deste PR" (só 2 cenários embutidos) foi resolvida pelo #10. | merge com conflitos add/add resolvidos a favor do #10 |
| [#10](https://github.com/hamadmkalaf/eleicoes2026/pull/10) | Prancheta: alinhar parede, conferir pares, apagar cenários; junta a biblioteca com o simulador | `claude/prancheta-delete-align-fv9e5o` (2 commits sobre `deisgn-fluxo`, 06/09) | 3, 4 | Versão mais recente da prancheta e do simulador; `scripts/cenarios.py` como leitor único; os 4 cenários versionados. Base do PR é `deisgn-fluxo`, então para o GitHub o diff só mostra os 2 commits finais. | merge limpo |

Observação de método: por causa da estrutura em estrela dos PRs (todos sobre a
mesma base, sem se enxergarem), vários corpos de PR ficaram defasados em
relação ao próprio head e entre si. **Quando houver divergência entre um corpo
de PR e um arquivo desta branch, vale o arquivo.**

---

## 9. Inconsistências entre etapas e pendências consolidadas

### 9.1 Três totais de comparecimento esperado

| Total | Onde aparece | Método |
|---|---|---|
| 11.416 | `simula_fluxo.py`, `analise_gargalos.md`, `plano_ring3.md`, simulador ("médio (2022)") | 74/50 por urna, a partir de `residencia_urna` |
| 11.418 | `salao.py`, `docs/CONTEXTO.md`, `plano_sinalizacao.html`, README | 74/50 por seção, arredondado por seção |
| 11.498 | `saidas/mrv_secoes_comparecimento.md`, `dublin_agregacoes.html` | taxa de 2022 do domicílio de origem de cada seção agregada |
| ~12.000 | `contexto_eleicoes_dublin_2026.md` (nota verbal) | base histórica, taxa única |

A diferença entre 11.416 e 11.418 é só arredondamento. A "por domicílio" é
mais fina (Longford 77,8%, Limerick 43,4%…), mas de qualidade desigual (proxy,
genérico). **Nenhuma é oficial.** Ao comparar etapas, usar a mesma base; ao
apresentar ao TRE, dizer qual foi usada.

### 9.2 Quatro numerações para as 28 mesas

| Sistema | Quem usa | Regra |
|---|---|---|
| **MRV 1–28 (DJE/TRE-DF)** | `mrv_secoes_comparecimento.md`, `data/mrv_secoes.json`, cadernos e mesários | ordem crescente da seção principal (MRV 22 = 3313, 23 = 3315, 24 = 3322) |
| **Posição 1–28 da prancheta** | `mesas.py`, prancheta, cenários salvos, PR #7 | circuito horário a partir do canto noroeste (1–8 norte, 9–20 leste, 21–22 recorte, 23–28 oeste) |
| **M1–M28 da sinalização** | `plano_sinalizacao.html` | blocos contíguos por porta (A: M1–M9, B: M10–M18, C: M19–M28), ordenados pela seção principal dentro do bloco |
| **MRV sobre posição no simulador** | simulador | premissa configurável: "MRV 1 começa na zona X, sentido horário/anti-horário"; no Cenário Claude MRV 1–12 ficam na fachada leste (posições 9–20), 13–20 na oeste, 21–28 na norte |

Consequências: o cenário "Três polos" isola as **posições** 22/23/24, que só
coincidem com as urnas críticas 3313/3315/3322 se a posição *k* receber a MRV
*k*; no Cenário Claude do simulador, as MRVs 22/23/24 caem nas posições 2/3/4
da parede norte. A sinalização impressa vai usar M1–M28, que não é nenhum dos
outros dois. **Pendência transversal: congelar uma numeração única de campo
(posição física → MRV → seções) antes de imprimir qualquer coisa.**

### 9.3 Papéis das portas da fachada sul

| Fonte | Entradas | Saídas |
|---|---|---|
| Planta-base / `docs/CONTEXTO.md` / `CLAUDE.md` | nenhuma decidida ("não assumir") | nenhuma |
| Plano do Ring 3 e plano de sinalização | S4 (A), S5 (B), S6 (C) | **S2 e S8** (1,20 m cada, emergência permanentemente aberta) |
| Simulador, Cenário Claude | S4, S5, S6 | **S1 e S9** (portas de carga, 3,6 m cada) |
| Prancheta, cenário B | — | S1 e S9 em uso com vestíbulo, que invade zonas protegidas |

O Ring 3 e a sinalização já desenham S2/S8 como saída de ~11 mil pessoas por
dois vãos de 1,20 m estimados sobre foto; o simulador considera S1/S9. A
planta-base diz que nada está decidido. **Pendência: decidir formalmente
entradas e saídas, medir S2/S8 no local e confirmar S1/S9 (abertas e travadas 9
horas, soleira para pedestre) antes de fechar Ring 3, sinalização e simulação.**

### 9.4 Três curvas de chegada e três modelos

| Modelo | Curva | Ciclo | Comparecimento | Para quê |
|---|---|---|---|---|
| `salao.py` (§4.1) | 8/13/15/14/12/11/10/9/8% por hora, 8h–17h | 55 s de projeto, serial | 11.418 | baias de fila na parede |
| `simula_fluxo.py` (§4.2) | .12/.15/.16/.15/.12/.09/.08/.07/.06 por hora (e "agudo") | t_id + t_voto por arranjo (serial/pipeline/paralelo) | 11.416 | fechamento e dimensionamento do Ring 3 |
| simulador (§4.3) | fatias de 30 min das 7h às 17h, 8% antes das 8h, vale 12h–15h, repique 16h | log-normal (cv 0,35) sobre identificação 30–90 s e voto | 11.416 (médio) | fluxo eleitor a eleitor no salão |

Todas as três são **premissas, não medidas** (a pesquisa do §7 confirma que não
há curva oficial). O simulador ainda usa Ring 3 = 800 como padrão; o plano do
Ring 3 chegou a 1.402.

### 9.5 Plano do Ring 3: listas de urnas por entrada defasadas

`plano_ring3.md` §6 imprime A com 11 urnas (3313 incluída), B com 6 (3315) e C
com 11 (3322), mas a tabela do mesmo parágrafo diz 9/10/9 e o script produz
3322 → A, 3313 → B, 3315 → C (§5.5). O texto não foi regerado depois da
recalibração 3·9·3. Corrigir o markdown a partir de
`simula_fluxo._relatorio_entradas()`.

### 9.6 Plano de sinalização cita o Ring 3 antigo

`plano_sinalizacao.html` diz "três serpenteados… somam 560,2 m (281
separadores), contra 200 m em mãos — faltam 362 m, ~EUR 2.357… 780 pessoas nos
serpenteados mais ~490 na reserva" e desenha blocos de 7,0 m a passo de 9,0 m.
O head do Ring 3 tem 596,3 m / 300 separadores, 200 unidades (400 m) em mãos,
faltam 100 (~EUR 1.302), capacidade 1.402, blocos de 4,2 / 12,6 / 4,2 m. Os
"200 m em mãos" da sinalização são os unifilas do orçamento (item d), não os
separadores de barreira externa do Ring 3. Regerar o template com os números
atuais.

### 9.7 Estado do arranjo da mesa receptora

`docs/CONTEXTO.md` e a prancheta modelam a mesa com 3 mesários e **uma** posição
de identificação; `analise_gargalos.md` conclui que só **duas posições de
identificação em paralelo** (dois cadernos) fecham às 17h com caderno físico. A
prancheta não tem esse módulo desenhado. **É a decisão que determina todo o
resto** (se o Ring 3 chega a ser usado, quanta fila cabe no salão, quantos
separadores internos).

### 9.8 Pendências consolidadas, por dono

**Cartório Eleitoral / TRE**
1. Arranjo da mesa receptora: dois cadernos em paralelo nas 23 urnas de duas
   seções (§4.2, §9.7).
2. Conferir se o erro 3222/3322 do PNG se propagou para cadernos ou
   configuração da urna 3322 (§1.3).
3. Haverá leitor biométrico em Dublin? (54,6% da zona com biometria coletada.)
4. Validar seção fora da parede (divisória exenta do plano B) se necessário.

**RDS (medições em campo e autorizações)**
5. Numeração S1–S9 vs 2.1–2.23; posição e vão reais de S2/S8; S1/S9 abertas e
   travadas 9 h; caminho do catering até N2; recuo de S3/S7/R1; caixas de piso
   elétricas; aceitação da faixa contínua de 3 m na fachada leste.
6. Dimensões do Ring 3 e distância do seu bordo oeste ao canto sudoeste do Hall
   2; perímetro do Ring 3 fechado ou aberto (brechas de emergência).
7. Altura da base lisa e distância entre saídas na parede leste externa;
   autorização de rigging nas treliças; bloqueio das vagas na véspera;
   circulação de veículos no dia.

**Posto (decisões de projeto)**
8. Congelar entradas/saídas (§9.3), a numeração única de campo (§9.2) e a base
   de comparecimento a apresentar (§9.1).
9. Pedido de +100 separadores de barreira (~EUR 1.302) e dimensionamento da
   barreira interna do Hall 2.
10. Cotar cobertura leve para os serpenteados; sinalização interna por par de
    mesas; balcão "não sei minha seção" em P1; rota prioritária desde a rua.
11. Regerar `plano_ring3.md` §6 e o template da sinalização com os números
    atuais (§9.5, §9.6); atualizar a capacidade padrão do Ring 3 no simulador.

**Análise (opcional, para calibrar)**
12. Reconstruir a curva real de chegada de 2022 a partir dos logs de urna do
    Portal de Dados Abertos do TSE (§7.1).
13. Rodar as três simulações sobre a mesma base de comparecimento e a mesma
    curva, para comparabilidade.

---

## 10. Como reproduzir, e como resgatar algo do backup

### 10.1 Pipeline completo, na ordem

```bash
pip install pandas openpyxl Pillow        # pymupdf é opcional (PNG do Ring 3)
# 1. agregação
(cd scripts && python3 mapa_agregacoes.py && python3 gera_pagina.py && python3 gera_mrv_comparecimento.py)
# 2 e 3. planta-base, mesas, prancheta
(cd scripts && python3 salao.py && python3 planta_base.py && python3 mesas.py && python3 gera_mesas.py)
python3 scripts/gera_editor.py && node scripts/teste_prancheta.js
python3 scripts/folgas_prancheta.py cenarios/tres-polos-20260905-182000.json
# 4. simulações
python3 scripts/gera_simulador.py && node simulador/teste_arranjos.js && node simulador/teste_modelo.js claude 16
python3 scripts/simula_fluxo.py
# 5. Ring 3
python3 scripts/layout_ring3.py
# 6. sinalização
python3 scripts/gera_plano_sinalizacao.py
```

Toda saída em `saidas/` é gerada por script; editar HTML ou SVG à mão se perde
na próxima geração. Na consolidação de 06/09 esse pipeline reproduziu todas as
saídas versionadas byte a byte (o `.xlsx` muda só em metadados do openpyxl).

### 10.2 Branches e backup

| Branch | O que é |
|---|---|
| `claude/project-analysis-documentation-w49q34` | **esta branch**: consolidação + documentação; base de trabalho daqui em diante |
| `backup/consolidado-2026-09-06` | cópia congelada do mesmo commit; não receber commits |
| `claude/dublin-electoral-sections-3odh1w` | base histórica (default do repositório) |
| `cenarios-hall2` | branch de dados dos cenários; `salva_cenario.py` continua gravando nela |
| as 9 branches `claude/*` e `deisgn-fluxo` restantes | heads dos PRs #1–#10, intactos |

Como todo merge foi real, **todo commit de toda branch é alcançável a partir da
branch de backup**, inclusive o que não está na árvore (ideias 1 e 2 apagadas,
rascunho do PR #4, README antigo do `cenarios-hall2`).

```bash
git fetch origin
git log --oneline --graph backup/consolidado-2026-09-06 | less     # o histórico inteiro
git log --all --oneline -- saidas/plano_ring3.md                    # quem mexeu num arquivo
git show 8d4b3be:saidas/plano_ring3.md > /tmp/ring3_head_pr6.md     # versão de um commit
git show f1f3c7d:scripts/ideia1_ilhas.py                            # ideia apagada em 01/09
git show 6e9c5d1:saidas/simulador_fluxo_hall2.html                  # rascunho do PR #4
git show origin/claude/simulador-fluxo-carregar-sinais-k4qxfw:simulador/app.js   # versão do PR #9
git restore --source backup/consolidado-2026-09-06 -- caminho/do/arquivo         # trazer de volta
git diff backup/consolidado-2026-09-06 -- .                         # o que mudou desde o backup
```

Para voltar tudo ao estado do backup numa branch nova:

```bash
git checkout -b resgate backup/consolidado-2026-09-06
```
