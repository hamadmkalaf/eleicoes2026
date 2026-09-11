# Documentação consolidada do projeto — Eleições 2026, posto de Dublin (RDS Ballsbridge, Hall 2)

> Consolidação feita em **06/09/2026** na branch
> `claude/project-analysis-documentation-w49q34`, que reúne a **última versão de
> cada etapa** do projeto (antes espalhadas por 12 branches e 10 pull requests
> abertos). Uma cópia congelada do estado consolidado (antes da integração
> descrita abaixo) está na branch **`backup/consolidado-2026-09-06`**, de onde
> qualquer arquivo ou commit de qualquer etapa pode ser resgatado (ver §10). As
> branches originais não foram apagadas nem alteradas.
>
> **Integração de 06/09/2026 (tarde):** as decisões do Posto passaram a morar
> num lugar só, `scripts/decisoes.py` (comparecimento pela base B, numeração
> MRV do DJE como identidade da mesa, cores por carga, portas S4/S5/S6 de
> entrada e S2/S8 de saída, entradas do Ring 3 com as suas mesas), e a
> planta-base, a prancheta, o simulador, o Ring 3 e a sinalização leem dali.
> O §9 registra o que isso resolveu e o que ficou.

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
| Comparecimento esperado (base B: taxa de 2022 por domicílio de origem) | **11.499** (68,5%), `scripts/comparecimento.py` | decisão de 06/09/2026; estimativa, não oficial |
| Urnas críticas (duas seções de Dublin; vermelhas) | **MRV 22 = 3313 (590), MRV 24 = 3322 (588), MRV 23 = 3315 (586)** | etapas 1 e 5 |
| Portas de eleitor | entradas S4 (A), S5 (B), S6 (C); saídas S2 e S8 | decisão de 06/09/2026, `scripts/decisoes.py` |
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

**Fonte única das decisões (transversal, desde 06/09/2026):**
`scripts/comparecimento.py` (base B) e `scripts/decisoes.py` (portas, numeração
MRV, classes e cores de carga, atribuição das mesas às entradas do Ring 3 com
as quotas de `layout_ring3.py`), gravados em `data/decisoes.json` por
`scripts/gera_decisoes.py`. `gera_editor.py`, `gera_simulador.py`,
`gera_plano_sinalizacao.py`, `planta_base.py`, `layout_ring3.py` e
`simula_fluxo.py` chamam `decisoes.montar()` ou leem o JSON; nenhum carrega
mais cópia própria de porta, taxa ou numeração.

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

8. **Integração (06/09, tarde), a pedido do Posto:** base B como fonte única
   de comparecimento; numeração MRV do DJE como identidade da mesa em toda
   parte; cores por carga na prancheta e no simulador; portas S4/S5/S6 e
   S2/S8 propagadas à planta-base, ao simulador (Cenário Claude refeito por
   varredura) e à sinalização; Ring 3 lendo as portas de `salao.py` e
   exportando capacidade e contorno para a prancheta e o simulador;
   `plano_ring3.md` §6 e o trecho do Ring 3 na sinalização regerados a partir
   dos scripts. Depois disso, geradores e testes rodaram de novo, e as duas
   páginas foram abertas em Chromium headless sem erro de JavaScript.

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

### 1.4 Tabela mestra: MRV × seções × aptos × comparecimento esperado × classe × entrada

**Base de comparecimento adotada (decisão de 06/09/2026): base B**, a taxa de
2022 do condado de origem de cada seção, de `handoff_agregacao_dublin_2026.md`,
implementada em `scripts/comparecimento.py`. O esperado de cada urna é o
arredondamento da soma exata das suas seções, e o total é a soma dos
arredondados: **11.499** (o `mrv_secoes_comparecimento.md` anterior somava as
seções antes de arredondar e dava 11.498; a diferença é só de arredondamento).
A base binária 74% Dublin / 50% interior, que dava 11.416–11.418 e alimentava
`salao.py`, `simula_fluxo.py`, o simulador e a sinalização, **saiu de todos os
scripts**; o "~12.000" de `contexto_eleicoes_dublin_2026.md` ficou como registro
histórico, com nota.

**Numeração:** a única identidade da mesa é o **MRV do DJE/TRE-DF** (MRV *k* =
*k*-ésima seção principal em ordem crescente). Na prancheta, no simulador e na
sinalização a mesa 22 é a MRV 22, esteja onde estiver. **Classe e cor** (regra
em `decisoes.py`): as 3 maiores são vermelhas (alta); esperado ≥ 450, amarelas
(média); o resto, verdes (baixa). **Entrada:** a atribuição às entradas A/B/C
do Ring 3 (§5.5), proporcional à capacidade de cada serpenteado, com uma mesa
vermelha em cada.

| MRV (DJE) | Seção principal | Seção agregada | Origem da agregada | Aptos | Esperado (base B) | Classe | Entrada / porta |
|---|---|---|---|---|---|---|---|
| 1 | 511 | 1100 | Roscommon | 582 | 375 | verde | B / S5 |
| 2 | 512 | 2855 | Longford | 476 | 355 | verde | C / S6 |
| 3 | 513 | 1105 | Mayo | 502 | 351 | verde | A / S4 |
| 4 | 517 | 1292 | Cavan | 513 | 348 | verde | B / S5 |
| 5 | 1160 | 3845 | Limerick | 473 | 328 | verde | A / S4 |
| 6 | 1352 | 522 | Donegal | 462 | 328 | verde | C / S6 |
| 7 | 3054 | 1099 | Kerry | 454 | 325 | verde | B / S5 |
| 8 | 3078 | 2847 | Leitrim | 429 | 311 | verde | B / S5 |
| 9 | 3108 | 3422 | Galway | 756 | 467 | amarela | A / S4 |
| 10 | 3142 | 1278 | Limerick | 793 | 466 | amarela | C / S6 |
| 11 | 3161 | 3307 | Cork | 791 | 504 | amarela | C / S6 |
| 12 | 3179 | 530 | Westmeath | 676 | 423 | verde | A / S4 |
| 13 | 3216 | 527 | Clare | 571 | 407 | verde | C / S6 |
| 14 | 3229 | 3821 | Cork | 606 | 405 | verde | C / S6 |
| 15 | 3245 | 519 | Cork | 781 | 498 | amarela | A / S4 |
| 16 | 3302 | 3181 | Outros locais da Irlanda | 771 | 518 | amarela | B / S5 |
| 17 | 3305 | 521 | Galway | 767 | 472 | amarela | B / S5 |
| 18 | 3306 | 518 | Outros locais da Irlanda | 766 | 515 | amarela | B / S5 |
| 19 | 3308 | — | — | 399 | 295 | verde | C / S6 |
| 20 | 3309 | 1314 | Waterford | 615 | 395 | verde | A / S4 |
| 21 | 3311 | 3913 | Dublin | 630 | 466 | amarela | B / S5 |
| **22** | **3313** | 3889 | Dublin | 797 | **590** | **vermelha** | B / S5 |
| **23** | **3315** | 3778 | Dublin | 792 | **586** | **vermelha** | C / S6 |
| **24** | **3322** | 3752 | Dublin | 794 | **588** | **vermelha** | A / S4 |
| 25 | 3442 | — | — | 398 | 295 | verde | B / S5 |
| 26 | 3688 | — | — | 400 | 296 | verde | A / S4 |
| 27 | 3832 | — | — | 400 | 296 | verde | C / S6 |
| 28 | 3862 | — | — | 400 | 296 | verde | A / S4 |
| **Total** | | | | **16.794** | **11.499** | 3 / 8 / 17 | A 3.642 · B 4.215 · C 3.642 |

**Não há comparecimento oficial por seção em nenhuma fonte do repositório**; a
coluna é uma taxa de 2022 aplicada a 2026, estimativa de trabalho a substituir
quando houver dado do Cartório. A mesma tabela sai de
`python3 scripts/gera_decisoes.py` e está em `data/decisoes.json`.

### 1.5 Arquivos e como rodar

```bash
pip install pandas openpyxl
cd scripts
python3 mapa_agregacoes.py          # saidas/Dublin_2026_agregacoes.xlsx e saidas/dados.json
python3 gera_pagina.py              # saidas/dublin_agregacoes.html
python3 gera_mrv_comparecimento.py  # saidas/mrv_secoes_comparecimento.md
python3 gera_decisoes.py            # data/decisoes.json (tabela mestra, entradas, Ring 3)
```

- `saidas/Dublin_2026_agregacoes.xlsx`: abas `Urnas`, `Secoes`,
  `Residencia x Secao`, `Residencia x Urna`, `Inconsistencias`.
- `saidas/dados.json`: os dados estruturados que alimentam a página e **todas
  as etapas seguintes** (simulações, Ring 3, sinalização leem daqui).
- `data/mrv_secoes.json`: a mesma designação MRV → seção, no formato que o
  simulador consome.
- `scripts/comparecimento.py`: a base B; `scripts/decisoes.py`: a tabela
  mestra com classe e entrada; `data/decisoes.json`: a mesma tabela gravada.

---

## 2. Planta-base do Hall 2

### 2.1 O que é

A leitura acordada do salão: o contorno medido do Hall 2, as 18 portas com um
número por fachada e o que está decidido sobre cada uma. Desde 06/09/2026 a
planta-base desenha também os papéis de eleitor decididos pelo Posto
(`scripts/decisoes.py`): **entradas S4 (A), S5 (B) e S6 (C); saídas S2 e S8**.

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
| S2 | sul | *sem código* | 13,25–14,45 | 1,20 m | **saída de eleitores**; emergência confirmada no local (02/09), permanentemente aberta, sem recuo; posição e vão estimados sobre foto |
| S3 | sul | 2.7 | 17,22–18,47 | 1,25 m | a definir |
| S4 | sul | 2.5/2.6 | 19,10–25,03 | 5,93 m | **entrada A** (serpenteado A do Ring 3) |
| S5 | sul | 2.4 | 25,32–31,25 | 5,93 m | **entrada B** (serpenteado B) |
| S6 | sul | 2.2/2.3 | 31,54–37,47 | 5,93 m | **entrada C** (serpenteado C) |
| S7 | sul | 2.1 | 38,09–39,36 | 1,27 m | a definir |
| S8 | sul | *sem código* | 42,12–43,32 | 1,20 m | **saída de eleitores**; emergência confirmada no local (02/09), permanentemente aberta, sem recuo; posição e vão estimados sobre foto |
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
- **Entradas S4, S5 e S6; saídas S2 e S8** (Posto, 06/09/2026). A planta-base
  rotula as portas e o Ring 3 (`RING3` em `salao.py`, 39 × 35 m a 14 m da
  fachada, centrado em S5 por estimativa) passou a fazer parte da geometria.

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
| `scripts/salao.py` | fonte única da geometria (contorno, faces, portas, recuos, Ring 3), carga das urnas via `comparecimento.py` e simulação simples de fila; `python3 salao.py` imprime a capacidade de parede |
| `scripts/decisoes.py` | papéis das portas, numeração MRV, classes de carga, atribuição às entradas; lido por `planta_base.py` |
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
**O número da mesa é o MRV do DJE** e não muda quando ela é movida. A posição
inicial de cada MRV na planta oficial segue o circuito horário a partir do
canto noroeste: 1–8 norte (oeste → leste), 9–20 descendo a fileira leste, 21–22
no recorte, 23–28 subindo a parede oeste; por isso, na planta oficial, as três
mesas vermelhas (MRV 22, 23, 24) caem juntas no canto sudoeste. Capacidade com
a mesma folga: 30; apertando ao mínimo: 34. As duas excedentes retiradas foram
escolhidas sobre o desenho (`mesas.AJUSTE_28`).

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
| **Cor por carga esperada** | mesa vermelha (as 3 de maior comparecimento), amarela (médio) ou verde (baixo), de `decisoes.py`; legenda com a lista de MRVs de cada classe; pode ser desligada |
| **Papéis das portas** | S4/S5/S6 rotuladas ENTRADA A/B/C, S2/S8 SAÍDA, com as cores da decisão |
| **Ring 3 e apron** | contorno do Ring 3 ao sul da fachada, com a capacidade de cada entrada e a linha até a sua porta; botão **+Ring 3** enquadra os dois |
| Painel de seleção | além das cotas, mostra seções, esperado, classe e entrada da mesa |
| Avisos de conflito | mesa ganha contorno roxo tracejado se cair fora do salão, sobre zona protegida, sobre vão de porta ou sobre outra mesa |
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
não comporta mesa isolada com 3,00 m dos dois lados (2,70 é o máximo). O ponto
em aberto do PR ("22, 23 e 24 são posições, não urnas verificadas") **ficou
resolvido pela decisão de numeração**: com o MRV do DJE como identidade, as
mesas 22, 23 e 24 são exatamente as três vermelhas (3313, 3315, 3322). Por
isso este é o arranjo que a varredura escolheu para o Cenário Claude do
simulador (§4.3).

### 3.4 Arquivos e como rodar

```bash
cd scripts
python3 gera_decisoes.py # data/decisoes.json
python3 salao.py         # confere dados e capacidade de parede
python3 planta_base.py   # planta-base
python3 mesas.py         # as 8 combinações da ideia, com validação
python3 gera_mesas.py    # saidas/mesas.json, SVGs e saidas/mesas.html
cd ..
python3 scripts/gera_editor.py     # saidas/editor_dados.json, editor.html (a prancheta) e data/prancheta_hall2.json
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
| `data/prancheta_hall2.json` | a mesma geometria de `saidas/editor_dados.json` (sem a lista de cenários, com o bloco `decisoes`), reescrita por `gera_editor.py` para o simulador e o `folgas_prancheta.py` |

---

## 4. Simulados de fluxo

Há **três modelos de simulação** no repositório, de escopo diferente. Desde
06/09/2026 os três usam o mesmo comparecimento (base B, 11.499) e a mesma
numeração; as curvas de chegada continuam diferentes (§9.4).

### 4.1 Simulação de fila por urna em `scripts/salao.py` (etapa 2)

Passos de 5 min sobre o perfil de chegada 8/13/15/14/12/11/10/9/8% (8h–17h),
55 s por eleitor como ponto de projeto, uma urna por mesa, fila serial. Serve
para dimensionar baias de fila na parede.

| s/eleitor | soma dos picos de fila das 28 | maior fila | urnas com fila > 10 | última a fechar |
|---|---|---|---|---|
| 45 | 33 | 12 | 2 | 17h00 |
| 50 | 114 | 32 | 3 | 17h00 |
| **55** | **261** | **57** | **7** | **17h20** |
| 60 | 465 | 84 | 11 | 18h05 |
| 70 | 968 | 136 | 15 | 19h35 |
| 90 | 2.227 | 230 | 23 | 22h45 |

Conclusão: o tempo de atendimento domina (fator 67 entre 45 e 90 s); o método
de identificação é decisão de layout tanto quanto de procedimento.

### 4.2 Modelo de fila por urna em `scripts/simula_fluxo.py` (etapa 5)

Separa duas perguntas com soluções diferentes: **horário de fechamento**
(vazão pura, depende só do ciclo por eleitor) e **tamanho da fila** (curva de
chegada, dimensiona o Ring 3). Perfil de chegada por hora .12/.15/.16/.15/.12/
.09/.08/.07/.06 (e um "agudo" alternativo). Como o eleitor no exterior vota só
para Presidente, o voto é curto (~22 s) e a busca no caderno domina.

| Arranjo da mesa | t_id | ciclo nas vermelhas | urnas atrasadas | fila total no pico | fecha |
|---|---|---|---|---|---|
| Serial (fila única, identifica depois vota) | 45 s | 67 s | 7/28 | 1.102 | 18h59 |
| Serial | 55 s | 77 s | 12/28 | 1.692 | 20h37 |
| Serial | 65 s | 87 s | 16/28 | 2.296 | 22h15 |
| Serial | 75 s | 100 s | 22/28 | 3.039 | 24h23 |
| Pipeline (identifica o próximo enquanto o anterior vota) | 55 s | 55 s | 1/28 | 464 | 17h01 |
| Pipeline | 65 s | 65 s | 6/28 | 982 | 18h39 |
| **Dois cadernos em paralelo, um por seção** | 45–75 s | 22–38 s | **0/28** | **0** | **17h00** |

Achados de `saidas/analise_gargalos.md`:

- Teto aritmético: 590 eleitores ÷ 540 min = **54,9 s por eleitor** na MRV 22
  (3313). O precipício está entre 50 e 60 s; a 60 s falham exatamente as três
  vermelhas.
- Comunicação dirigida (pedir às seções críticas que evitem o pico) reduz a
  fila de pico mas **não altera o fechamento**.
- **O gargalo é a mesa, não a urna**: 23 das 28 urnas acumulam duas seções, logo
  dois cadernos; com os 3 mesários é possível operar duas posições de
  identificação em paralelo alimentando uma urna. Fecha às 17h00 mesmo com
  caderno lento (t_id 110 s ainda fecha 17h03). É a negociação a abrir com o
  Cartório e não custa nada ao TRE.
- Estratificação = classes da prancheta: **T1 / vermelhas** MRV 22, 24, 23
  (586–590, 55 s disponíveis); **T2 / amarelas** MRV 16, 18, 11, 15, 17, 9, 10,
  21 (466–518, 63–70 s); **T3** 12 urnas (311–423, 77–104 s) e **T4** as 5 de
  seção única (295–296, 110 s), ambas verdes. A folga de T3/T4 não absorve
  carga de T1: redistribui-se recurso, nunca eleitor.

### 4.3 Simulador de fluxo do Hall 2 (`saidas/simulador_fluxo.html`, etapa 4)

Simulação **por eventos discretos, eleitor a eleitor**, do dia inteiro, sobre
o arranjo real das 28 mesas. Motor em `simulador/modelo.js` (roda no navegador
e em Node), interface em `simulador/app.js` + `template.html`, tudo embutido
por `scripts/gera_simulador.py` junto com o bloco de decisões. Três telas:
**Premissas**, **Simulação** (planta minuto a minuto) e **Resultado**
(relatório com critérios aprovados, em atenção ou reprovados).

Estágios do eleitor: chegada ao Ring 3 → triagem → fila da entrada → porta com
liberação controlada → buffer → checkpoint → fila da mesa → mesa (identificação
pelo caderno) e urna em pipeline → saída.

**O que vem das decisões (não é mais premissa de quem simula):** o número da
mesa é o MRV do DJE (sem remapeamento); as zonas são as **entradas A, B e C do
Ring 3**, cada uma com as mesas que `decisoes.py` lhe atribuiu e com a
capacidade do seu serpenteado mais baia; as portas padrão são S4/S5/S6 de
entrada e S2/S8 de saída (a página avisa e oferece o botão de volta se o
cenário se afastar disso); o comparecimento de cada mesa é o da base B, com
presets "pequeno" (−15 %) e "grande" (+15 %) só para sensibilidade; a classe
de fila de cada mesa é a sua cor (vermelha/amarela/verde); a capacidade do
Ring 3 é 1.402 no total e é conferida também por entrada (445/513/445).
**Fixo em todos os cenários:** identificação pelo caderno; liberação
controlada; curva de chegada em fatias de 30 min das 7h às 17h com 8% antes da
abertura, vale entre 12h e 15h e repique perto das 17h (apoiada na pesquisa do
§7); caminhada a 1,2 m/s; 0,6 m por pessoa em fila; 200 m de fita de unifila
contratados. **Premissas de quem simula:** o arranjo das mesas (biblioteca da
prancheta), checkpoint (existência, distância, atendentes por entrada,
segundos por eleitor), fila por classe de mesa, política de liberação, vazão da
porta, tempos de identificação (30/45/60/90 s) e voto, variabilidade,
justificativas, triagem e capacidade do Ring 3, dias simulados e semente.

Onze critérios de veredito: última mesa fecha até 17h30; mesas vermelhas sem
"fome" (≤ 10 min); espera P90 ≤ 45 min; fila interna não volta até a porta;
checkpoint ≤ 80% de ocupação; portas equilibradas (≤ 1,25×); saída não corta
corredor de entrada; fita ≤ 200 m; filas cabem no espaço; Ring 3 comporta a
fila externa (total e por entrada); triagem ≤ 75%.

**Cenário Claude (06/09/2026)**, escolhido por `simulador/varredura.js` sobre
as portas e entradas da decisão, variando o arranjo (planta oficial e os quatro
cenários da prancheta), a distância e a lotação do checkpoint e as filas por
classe (resultado em `saidas/varredura_top.json`): arranjo **"Três polos"** (as
três vermelhas separadas, MRV 24 na parede norte, 23 na fachada leste, 22 no
recorte), checkpoint a 16 m com 3 atendentes por entrada, filas 3/4/6. Resultado
com 16 dias (`node simulador/teste_modelo.js claude 16`): última mesa fecha
17h03 (p50) / 17h04 (p90); espera P90 de 50 min (33 fora, 22 dentro); pico de
318 pessoas dentro e ~970 fora (1.005 no dia ruim), com a entrada B em 478 das
513 que cabem; 157 m de fita; zero cruzamentos; desequilíbrio 1,16×. Só a
espera fica em atenção; todos os demais critérios passam. Os três cenários
salvos sem conflito (Três polos, Hamad1, Hamad 2) empatam dentro de 1 min de
espera; o Hamad_3polos tem a mesa 4 sobre o vão de N2 e fica fora.

**Biblioteca de arranjos:** o bloco *Salão* lista, com miniatura e
conferência geométrica, três origens: planta oficial (A e B), arranjos da
prancheta embutidos pelo gerador (os quatro de `cenarios/`) e arranjos
carregados na hora (JSON colado ou arquivo, no `localStorage`). O simulador
consome a geometria de `saidas/editor_dados.json` (que a prancheta acabou de
escrever) e avisa se `data/prancheta_hall2.json` ficar para trás.
`simulador/teste_arranjos.js` (24 asserções) cobre leitura dos dois formatos,
lixo, mesa repetida e detecção de conflito; `teste_modelo.js` confere
identidade MRV, classes, esperado e conservação de eleitores.

**Rascunho superado (PR #4):** `saidas/simulador_fluxo_hall2.html`, com um
esquema do salão desenhado à mão em vez da planta-base; não está na árvore
consolidada, fica no histórico (`git show 6e9c5d1:saidas/simulador_fluxo_hall2.html`).

### 4.4 Como rodar

```bash
python3 scripts/gera_decisoes.py       # data/decisoes.json (os testes em Node leem daqui)
python3 scripts/gera_editor.py         # antes, porque o simulador lê editor_dados.json
python3 scripts/gera_simulador.py      # saidas/simulador_fluxo.html
node simulador/teste_arranjos.js
node simulador/teste_modelo.js claude 16
node simulador/varredura.js 3          # alguns segundos por dia simulado
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

Centros das portas lidos de `scripts/salao.py` (planta do RDS), pela numeração
da planta-base, desde 06/09/2026 (antes, a prancheta manual do Posto, com
diferenças de 0,1–0,2 m).

| Porta | Centro, do canto sudoeste | Papel |
|---|---|---|
| S1 | 9,6 m | — |
| **S2** | 13,9 m | **SAÍDA** |
| S3 | 17,8 m | — |
| **S4** | 22,1 m | **ENTRADA A** |
| **S5** | 28,3 m | **ENTRADA B** |
| **S6** | 34,5 m | **ENTRADA C** |
| S7 | 38,7 m | — |
| **S8** | 42,7 m | **SAÍDA** |
| S9 | 46,9 m | — |

As três entradas estão a 6,2 m uma da outra (passo apertado, que vem do
prédio); as saídas ficam nos flancos, fora do vão das entradas, de modo que quem
sai não cruza fila de entrada. S2 e S8 estão estimadas sobre foto (1,20 m de
vão) e precisam de medição no local.

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

Em `scripts/decisoes.py` (`atribui_entradas`), proporcional à capacidade das
entradas (quotas 31,7 / 36,6 / 31,7%), com uma mesa vermelha em cada; a
mesma lista alimenta a prancheta, o simulador e a sinalização (desvio máximo
de 8 eleitores em 11.499):

| Entrada | Mesas | Esperado | MRV (seção) |
|---|---|---|---|
| A (S4) | 9 | 3.642 | 3 (513), 5 (1160), 9 (3108), 12 (3179), 15 (3245), 20 (3309), **24 (3322)**, 26 (3688), 28 (3862) |
| B (S5) | 10 | 4.215 | 1 (511), 4 (517), 7 (3054), 8 (3078), 16 (3302), 17 (3305), 18 (3306), 21 (3311), **22 (3313)**, 25 (3442) |
| C (S6) | 9 | 3.642 | 2 (512), 6 (1352), 10 (3142), 11 (3161), 13 (3216), 14 (3229), 19 (3308), **23 (3315)**, 27 (3832) |

`plano_ring3.md` §6 foi regerado com esta tabela (antes trazia listas de uma
versão anterior do script).

### 5.6 O Ring 3 comporta a fila prevista?

| Arranjo da mesa | Fila total no pico | Cabe em Hall 2 (~1.100) + Ring 3 (1.402)? |
|---|---|---|
| Dois cadernos em paralelo | 0 | sim, o Ring 3 nem abre |
| Pipeline, 55 s | 464 | sim, só no Hall 2 |
| Serial, 55 s | 1.692 | sim, com os serpenteados |
| Serial, 65 s | 2.296 | sim, com o flanco aberto |
| Serial, 75 s | 3.039 | **não: transborda para a Merrion Road** |

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
2. Medir no local posição e vão de S2 e S8 (estimados sobre foto), as saídas
   de ~11,5 mil eleitores por dois vãos de 1,20 m.
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
| P4 Cabeças dos serpenteados | início de cada bloco, no corredor de distribuição | confirmação; captura de quem errou enquanto cabe corrigir | identidade da fila (cor ou letra, a decidir) em corpo grande + lista das mesas + "errou? volte →" | 3 totens, 1 faixa |
| P5 Portas de entrada | no vidro da fachada sul, lidas de dentro do serpenteado | só confirmação de que ali se entra | "ENTRADA" em 300 mm + identidade da fila (cor ou letra, a decidir) | 3 bandeirolas de fachada (vinil no vidro) |
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
  Shelbourne Hall")**, em azul-marinho com branco: é o argumento a favor da
  cor. **Se a identidade da fila será cor ou letra não está decidido** (Posto,
  06/09/2026); o plano registra as duas opções e o cartaz diz ENTRADA mais a
  identidade da fila que descarrega ali. As letras A/B/C são rótulos de
  planejamento, os mesmos do Ring 3 e do simulador. Nossas peças nunca em
  azul-marinho com branco.
- **Código de cor das três filas, se a escolha for cor: azul, âmbar e
  magenta**, distinguíveis em deuteranopia e protanopia; a cor nunca aparece
  sozinha, sempre com o número da mesa. Não confundir com vermelho/amarelo/
  verde, que na prancheta e no simulador marcam a carga da mesa.
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

### 6.5 Distribuição das mesas pelas entradas

Desde 06/09/2026 a sinalização usa a atribuição do plano do Ring 3
(`decisoes.py`, §5.5) e a numeração MRV do DJE, em vez de uma distribuição
própria com numeração M1–M28 em blocos contíguos. A placa de cada fila lista
os MRVs da entrada.

| Entrada | Porta | Cor da raia | Mesas | Aptos | Esperado | Cabe no Ring 3 | Mais pesada |
|---|---|---|---|---|---|---|---|
| A | S4 | azul | 9 | 5.336 | 3.642 | 445 | MRV 24 (3322, 588) |
| B | S5 | âmbar | 10 | 6.199 | 4.215 | 513 | MRV 22 (3313, 590) |
| C | S6 | magenta | 9 | 5.259 | 3.642 | 445 | MRV 23 (3315, 586) |

**A tabela mestra tem 51 linhas ordenadas por seção, não 28 por mesa**: são 23
seções agregadas, e um eleitor da 3889 precisa encontrar "3889"; num quadro
por mesa, ~7 mil eleitores não se acham e vão ao balcão de dúvidas.

Dimensionamento de leitura: 21 chegadas/min em média, 38/min no pico (premissa
1,8×), 15 s por leitura (premissa) → ~10 posições simultâneas → 4 painéis de
1,2 m, ou o equivalente replicado ao longo do corredor. O trecho do plano que
cita o quantitativo do Ring 3 é gerado por `layout_ring3.py` (596,3 m, 300
separadores, 100 a adquirir, 1.402 pessoas).

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
- Posição e vão de S2 e S8 a medir em campo antes de imprimir.
- Fator de pico 1,8× é premissa, não medida; o precedente de Dublin 2022
  sugere fila que nunca esvazia em vez de pico isolado.
- Balcão "não sei minha seção" em P1, recuado, com 2–3 operadores e caderno
  impresso (Wi-Fi no portão não confirmado).
- Sinalizar a rota prioritária desde a rua (P0 e portão).
- **A atribuição mesa → entrada e a identidade de cada fila (cor ou letra)
  precisam estar congeladas antes de qualquer impressão**; a numeração MRV,
  essa é a do DJE e não muda.

Próxima etapa já encaminhada: sinalização interna **por par de mesas, suspensa
nas treliças** (14 peças em vez de 28), condicionada a autorização de rigging
do RDS, plataforma elevatória na véspera e não obstruir luminária de
emergência, detector de fumaça ou placa de EXIT.

```bash
pip install Pillow            # para embutir as fotos
python3 scripts/gera_plano_sinalizacao.py   # lê decisoes.py e layout_ring3.py; falha se a tabela mestra não cobrir as 51 seções
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
| [#3](https://github.com/hamadmkalaf/eleicoes2026/pull/3) | Junta MRVs (DJE/TRE-DF) ao eleitorado por seção | `claude/mrv-secoes-eleitorais-rjvkxf` (2 commits) | 1 | A taxa por domicílio deste PR virou a **base B, adotada pelo Posto em 06/09** (`scripts/comparecimento.py`); a designação MRV virou a numeração única das mesas (`scripts/decisoes.py`). Corpo do PR atualizado nesse sentido. | merge limpo |
| [#4](https://github.com/hamadmkalaf/eleicoes2026/pull/4) | WIP: interior flow scenario simulator | `claude/electoral-flow-simulation-c48buh` (1 commit) | 4 | Rascunho explicitamente não utilizável (esquema do salão desenhado à mão). Superado pelo #5. | `merge -s ours` (histórico preservado, arquivo fora da árvore) |
| [#5](https://github.com/hamadmkalaf/eleicoes2026/pull/5) | Adiciona simulador de fluxo do Hall 2 | `claude/electoral-flow-simulator-5ihr5v` (2 commits) | 4 | Motor, interface, varredura de 4.228 combinações, Cenário Claude, `data/mrv_secoes.json`, `data/prancheta_hall2.json`. Coerente. | via PR #9 |
| [#6](https://github.com/hamadmkalaf/eleicoes2026/pull/6) | Plano base do Ring 3 e análise de gargalos | `claude/ring-3-dimensions-estimate-ge0jop` (11 commits, 05–06/09) | 5, 4 | O corpo do PR citava a geometria de uma versão anterior (26 m, 1.170 pessoas, +82 separadores); o head tem 28,5 m, 3·9·3 balizas, 1.402 pessoas, +100. As listas de urnas por entrada do §6 estavam defasadas do script; **reharmonizadas nesta branch** a partir de `decisoes.py`, com base B. Corpo do PR atualizado. | merge limpo |
| [#7](https://github.com/hamadmkalaf/eleicoes2026/pull/7) | Cenário "Três polos" | `claude/prancheta-busy-tables-scenario-h2iwgq` (2 commits) | 3 | Cenário + `folgas_prancheta.py` + `planta_hall2.json` (cópia da geometria). O ponto em aberto ("22/23/24 são posições, não urnas verificadas") ficou resolvido pela numeração MRV como identidade: são as três vermelhas. É o arranjo do Cenário Claude. | merge com conflito em `cenarios/README.md` (juntado); duplicata da geometria retirada |
| [#8](https://github.com/hamadmkalaf/eleicoes2026/pull/8) | Plano de sinalização | `claude/rds-ballsbridge-signage-points-kml93e` (5 commits, 05–06/09) | 6 | O corpo recomendava nomear as portas por cor e o head afirmava que "não são nomeadas"; **o Posto registra que não há decisão entre cor e letra**, e o plano foi reescrito assim. Os números do Ring 3 passaram a ser lidos de `layout_ring3.py`; a distribuição das mesas e a numeração vêm de `decisoes.py`. Corpo do PR atualizado. | merge limpo |
| [#9](https://github.com/hamadmkalaf/eleicoes2026/pull/9) | Carrega arranjos da prancheta no simulador | `claude/simulador-fluxo-carregar-sinais-k4qxfw` (3 commits, sobre #5) | 4 | Biblioteca de arranjos, conferência geométrica, `teste_arranjos.js`. A nota "Fora deste PR" (só 2 cenários embutidos) foi resolvida pelo #10. | merge com conflitos add/add resolvidos a favor do #10 |
| [#10](https://github.com/hamadmkalaf/eleicoes2026/pull/10) | Prancheta: alinhar parede, conferir pares, apagar cenários; junta a biblioteca com o simulador | `claude/prancheta-delete-align-fv9e5o` (2 commits sobre `deisgn-fluxo`, 06/09) | 3, 4 | Versão mais recente da prancheta e do simulador; `scripts/cenarios.py` como leitor único; os 4 cenários versionados. Base do PR é `deisgn-fluxo`, então para o GitHub o diff só mostra os 2 commits finais. | merge limpo |

Observação de método: por causa da estrutura em estrela dos PRs (todos sobre a
mesma base, sem se enxergarem), vários corpos de PR ficaram defasados em
relação ao próprio head e entre si. **Quando houver divergência entre um corpo
de PR e um arquivo desta branch, vale o arquivo.** O PR #1 foi fechado em
06/09/2026 a pedido do Posto (sua branch `deisgn-fluxo` fica, por ser a base do
#10); o #11 é o PR desta branch consolidada.

---

## 9. Inconsistências entre etapas e pendências consolidadas

Estado depois da integração de 06/09/2026. Cada item diz o que foi decidido e o
que ainda falta.

### 9.1 Comparecimento esperado: resolvido (base B)

Conviviam 11.416 (74/50 por urna), 11.418 (74/50 por seção), 11.498 (por
domicílio) e "~12.000" (nota verbal). **Decisão: base B**, taxa de 2022 por
domicílio de origem de cada seção, em `scripts/comparecimento.py`; total
**11.499** (arredondado por urna). Os scripts que carregavam 74/50 (`salao.py`,
`simula_fluxo.py`, `gera_plano_sinalizacao.py`, `simulador/modelo.js`) passaram
a ler dali; `contexto_eleicoes_dublin_2026.md` ganhou nota de superação.
**Nenhuma base é oficial**: ao apresentar ao TRE, dizer que é taxa de 2022
aplicada a 2026. Pendência que a decisão não elimina: metade das taxas por
condado é proxy ou genérica; o dado de 2022 que existe no repositório (7.492 de
11.946 no 2º turno, 62,7% no conjunto) merece conferência contra os 74% de
Dublin.

### 9.2 Numeração das mesas: resolvido (MRV do DJE), com uma etapa futura

Conviviam a MRV do DJE, a posição 1–28 da prancheta, a M1–M28 da sinalização e o
remapeamento configurável do simulador. **Decisão: só a numeração do DJE, como
identidade da mesa que não depende da posição.** A prancheta mantém o número
ao arrastar (a posição inicial ainda é a do circuito geográfico), o simulador
perdeu o remapeamento (a mesa *n* é a MRV *n*) e a sinalização lista MRVs em vez
de M1–M28. Consequência útil: o cenário "Três polos" separa de fato as três
mesas de maior carga. **Etapa futura**: quando o cenário da prancheta for
fechado, haverá uma segunda numeração, por distribuição na parede, voltada ao
eleitor; a do DJE fica de uso interno. Até lá, uma só.

### 9.3 Papéis das portas: resolvido e propagado

**Entradas S4 (A), S5 (B), S6 (C); saídas S2 e S8** (`decisoes.py`). A
planta-base desenha os papéis; o Cenário Claude do simulador saiu de S1/S9 para
S2/S8 e foi refeito por varredura; Ring 3 e sinalização já seguiam a decisão.
Pendências que a decisão não elimina: medir S2/S8 no local (posição e vão de
1,20 m estimados sobre foto) e confirmar a vazão de dois vãos de 1,20 m como
saída de ~11,5 mil eleitores; S1/S9 seguem sem papel.

### 9.4 Curvas de chegada: ainda três

| Modelo | Curva | Ciclo | Para quê |
|---|---|---|---|
| `salao.py` (§4.1) | 8/13/15/14/12/11/10/9/8% por hora, 8h–17h | 55 s de projeto, serial | baias de fila na parede |
| `simula_fluxo.py` (§4.2) | .12/.15/.16/.15/.12/.09/.08/.07/.06 por hora (e "agudo") | t_id + t_voto por arranjo | fechamento e dimensionamento do Ring 3 |
| simulador (§4.3) | fatias de 30 min das 7h às 17h, 8% antes das 8h, vale 12h–15h, repique 16h | log-normal (cv 0,35) sobre identificação 30–90 s e voto | fluxo eleitor a eleitor no salão |

Todas são premissas, não medidas (a pesquisa do §7 confirma que não há curva
oficial). O comparecimento e a numeração já são os mesmos nos três; unificar a
curva é trabalho pequeno e fica como pendência de análise (§9.8, item 12).

### 9.5 Ring 3, listas por entrada: resolvido

`plano_ring3.md` §6 foi regerado a partir de `decisoes.py` (tabela e listas
coincidem com o script; 9/10/9 mesas, MRV 24 em A, 22 em B, 23 em C). As
portas do Ring 3 vêm agora de `salao.py`, e o desenho foi regerado (SVG e PNG).

### 9.6 Sinalização citando o Ring 3 antigo: resolvido

O trecho "Onde este plano encosta no plano do Ring 3" é gerado por
`layout_ring3.py` (596,3 m, 300 separadores, 100 a adquirir, 1.402 pessoas) e
distingue os 200 separadores de barreira externa dos 100 unifilas do orçamento.
O diagrama usa as larguras reais dos blocos (4,2 / 12,6 / 4,2 m).

### 9.7 Arranjo da mesa receptora: em aberto (o item que decide o resto)

`docs/CONTEXTO.md` e a prancheta modelam a mesa com uma posição de
identificação; `analise_gargalos.md` conclui que só **duas posições de
identificação em paralelo** (dois cadernos) fecham às 17h com caderno físico.
A prancheta não tem esse módulo desenhado. É a decisão que determina se o Ring
3 chega a ser usado, quanta fila cabe no salão e quantos separadores internos.

### 9.8 Pendências consolidadas, por dono

**Cartório Eleitoral / TRE**
1. Arranjo da mesa receptora: dois cadernos em paralelo nas 23 urnas de duas
   seções (§4.2, §9.7).
2. Conferir se o erro 3222/3322 do PNG se propagou para cadernos ou
   configuração da urna 3322 / MRV 24 (§1.3).
3. Haverá leitor biométrico em Dublin? (54,6% da zona com biometria coletada.)
4. Validar seção fora da parede (divisória exenta do plano B) se necessário.

**RDS (medições em campo e autorizações)**
5. Posição e vão reais de S2/S8; S1/S9 abertas e travadas 9 h (alternativa de
   saída); caminho do catering até N2; recuo de S3/S7/R1; caixas de piso
   elétricas; aceitação da faixa contínua de 3 m na fachada leste.
6. Dimensões do Ring 3 e distância do seu bordo oeste ao canto sudoeste do Hall
   2 (o contorno está centrado em S5 por estimativa); perímetro do Ring 3
   fechado ou aberto (brechas de emergência).
7. Altura da base lisa e distância entre saídas na parede leste externa;
   autorização de rigging nas treliças; bloqueio das vagas na véspera;
   circulação de veículos no dia.

**Posto (decisões de projeto)**
8. Identidade das filas para o eleitor: **cor ou letra** (§6.3), a única
   decisão que ainda contamina todas as peças impressas.
9. Fechar o cenário da prancheta (candidato: "Três polos", o do Cenário
   Claude) e, a partir dele, definir a numeração voltada ao eleitor (§9.2).
10. Pedido de +100 separadores de barreira (~EUR 1.302) e dimensionamento da
    barreira interna do Hall 2.
11. Cotar cobertura leve para os serpenteados; sinalização interna por par de
    mesas; balcão "não sei minha seção" em P1; rota prioritária desde a rua.

**Análise (opcional, para calibrar)**
12. Unificar a curva de chegada dos três modelos (§9.4) e, se possível,
    reconstruí-la a partir dos logs de urna de 2022 do Portal de Dados Abertos
    do TSE (§7.1).

### 9.9 A integração, como ficou

```
saidas/dados.json ──► scripts/comparecimento.py (base B: esperado por urna)
                                │
scripts/salao.py (geometria, portas, RING3) ──► scripts/planta_base.py (numeração S1–S9, papéis)
                                │                        │
                                ▼                        ▼
                      scripts/decisoes.py ◄──── scripts/layout_ring3.py (portas de salao; capacidades → quotas)
      (portas, MRV, classes/cores, atribuição às entradas, Ring 3)
                                │
        ┌───────────────┬───────┴────────┬──────────────────┬──────────────────┐
        ▼               ▼                ▼                  ▼                  ▼
  gera_decisoes.py  gera_editor.py   gera_simulador.py  gera_plano_sinalizacao.py  simula_fluxo.py
  data/decisoes.json  prancheta      simulador (DECISOES)   Rota do Eleitor        relatório de entradas
```

Mudar uma decisão é editar `decisoes.py` (ou `comparecimento.py`) e rodar o
pipeline do §10.1; nenhum gerador carrega mais cópia própria de porta, taxa,
numeração ou capacidade do Ring 3. A varredura do simulador
(`simulador/varredura.js`) é a única etapa que precisa de reexecução manual
para recalibrar o Cenário Claude depois de uma mudança.

---

## 10. Como reproduzir, e como resgatar algo do backup

### 10.1 Pipeline completo, na ordem

```bash
pip install pandas openpyxl Pillow        # pymupdf é opcional (PNG do Ring 3)
# 1. agregação e decisões
(cd scripts && python3 mapa_agregacoes.py && python3 gera_pagina.py && python3 gera_mrv_comparecimento.py)
python3 scripts/gera_decisoes.py
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
na próxima geração. Sem `pymupdf`, o PNG do Ring 3 pode ser regerado a partir
do SVG com o Chromium do Playwright (foi assim em 06/09). O `.xlsx` muda só em
metadados do openpyxl a cada geração.

### 10.2 Branches e backup

| Branch | O que é |
|---|---|
| `claude/project-analysis-documentation-w49q34` | **esta branch**: consolidação + documentação; base de trabalho daqui em diante |
| `backup/consolidado-2026-09-06` | cópia congelada do estado consolidado de 06/09 (manhã, antes da integração); não receber commits |
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
