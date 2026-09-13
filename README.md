# Eleições 2026 — posto de Dublin (RDS Ballsbridge, Hall 2)

Análise das seções eleitorais de Dublin e desenho da operação de votação do
**1º turno de 04/10/2026 (8h–17h)** no **Royal Dublin Society, Hall 2** (RDS,
Merrion Road, Ballsbridge, Dublin 4): **16.794 eleitores aptos, 51 seções, 28
urnas**, identificação por caderno físico, Hall 2 + Ring 3 (descoberto).

**Leia primeiro [`DOCUMENTACAO_PROJETO.md`](DOCUMENTACAO_PROJETO.md)**: é a
documentação consolidada das sete etapas, com a revisão dos dez pull requests,
as inconsistências entre etapas e as pendências por dono; o §11 documenta o
dashboard e as portas vivas (11/09). Esta branch reúne a última versão de cada
etapa (consolidação de 06/09 mais barreiras, Ring 3 oficial, cenário
Equitativo e cotações); `backup/consolidado-2026-09-06` é a cópia congelada do
estado de 06/09 antes da integração.

**Decisões do Posto (06/09/2026), fonte única em `scripts/decisoes.py`:**
comparecimento esperado pela base B (taxa de 2022 por domicílio de origem,
`scripts/comparecimento.py`, 11.499); o número da mesa é o **MRV do DJE** e
não depende da posição; mesas coloridas por carga (vermelho as 3 maiores,
amarelo médio, verde baixo); entradas **S4 (A), S5 (B), S6 (C)** e saídas **S2
e S8**; cada entrada do Ring 3 com as suas mesas. A nomenclatura das filas para
o eleitor (cor ou letra) está em aberto.

## Mapa do projeto

| # | Etapa | Entregáveis | Documento de referência |
|---|---|---|---|
| 1 | Agregação final: seções → MRVs, comparecimento esperado por seção (2022) | `saidas/Dublin_2026_agregacoes.xlsx`, `saidas/dados.json`, `saidas/dublin_agregacoes.html`, `saidas/mrv_secoes_comparecimento.md`, `data/mrv_secoes.json` | `DOCUMENTACAO_PROJETO.md` §1, `handoff_agregacao_dublin_2026.md`, `contexto_eleicoes_dublin_2026.md` |
| 2 | Planta-base do Hall 2 (salão, 18 portas numeradas por fachada) | `saidas/planta_base.html`, `saidas/planta_base.svg`, `scripts/salao.py` | §2, `docs/CONTEXTO.md` |
| 3 | Prancheta e seus cenários (planta das 28 mesas, editor em escala, biblioteca de cenários) | `saidas/editor.html`, `saidas/mesas.html`, `cenarios/*.json` | §3, `cenarios/README.md` |
| 4 | Simulados de fluxo (simulador eleitor a eleitor; modelos de fila por urna) | `saidas/simulador_fluxo.html`, `simulador/`, `scripts/simula_fluxo.py`, `saidas/analise_gargalos.md` | §4 |
| 5 | Dimensões e plano do Ring 3 | `saidas/plano_ring3.md`, `saidas/layout_ring3.svg/.png` | §5 |
| 6 | Plano de sinalização externo | `saidas/plano_sinalizacao.html`, `data/fotos/` | §6 |
| 7 | Expectativa de horários de pico | `pesquisa_horarios_pico_votacao.md` | §7 |
| 8 | Separadores de fila do salão (cenário 1e adotado: 100 postes, 146 m de fita) | `saidas/barreiras_hall2.html`, `saidas/tensa_barreiras.md`, `saidas/tensa_barreiras.json`, `scripts/tensa_barreiras.py` | `saidas/tensa_barreiras.md` |
| 9 | Ring 3 nas dimensões oficiais (44 × 35 m): quatro desenhos de fila comparados | `saidas/ring3_horizontal.html`, `saidas/ring3.json`, `saidas/plano_ring3_horizontal.md`, `scripts/ring3.py` | `saidas/plano_ring3_horizontal.md` |
| 10 | Dashboard do plano (narrativa única, ferramentas embutidas, portas vivas) | `saidas/dashboard/index.html`, `saidas/ring3_vivo.html`, `simulador/portas.js`, `scripts/gera_dashboard.py`, `scripts/gera_ring3_vivo.py` | §0 e §11 de `DOCUMENTACAO_PROJETO.md` |
| 11 | Fitas no piso em vez do checkpoint (simulação no motor oficial) | `saidas/fitas_piso.html`, `saidas/fitas_piso.json`, `simulador/fitas.js`, `scripts/fitas_piso.py` | `docs/alternativa_fitas_no_piso.md`, `docs/registro_fitas_no_piso_2026-09-12.md` |
| 12 | Decisões de fluxo em aberto, com dependências, e instruções de fluxo para o treinamento (geradas das decisões vigentes) | `data/decisoes_abertas.json`, `docs/decisoes_em_aberto.md`, `docs/instrucoes_fluxo.md`, `saidas/instrucoes_fluxo.html`, `scripts/decisoes_abertas.py`, `scripts/gera_instrucoes_fluxo.py` | §12 de `DOCUMENTACAO_PROJETO.md`, `PENDENCIAS`, `orcamento_final.md` |

Artefatos publicados: o **dashboard do plano**
(https://claude.ai/code/artifact/1c434ede-3d79-439c-b97b-a8121979bd03), que
integra todas as peças, e cada peça em separado; URLs no §0 da documentação.

**Portas vivas (11/09/2026).** As portas clicáveis do Simulador são o controle
mestre: mudar uma entrada ou uma saída da fachada sul redesenha a Prancheta
(só papéis das portas, entradas e a entrada de cada mesa), o Ring 3 ao vivo
(N entradas, N serpenteados) e a faixa do dashboard. A lógica está em
`simulador/portas.js` (porte de `scripts/ring3.py` e de
`decisoes.atribui_entradas`), testada por `node simulador/teste_portas.js`.
A decisão de 06/09 continua em `scripts/decisoes.py`; o estado vivo é uma
exploração no navegador e não a altera.

## Como rodar

```bash
pip install pandas openpyxl Pillow        # pymupdf é opcional (PNG do Ring 3)
# 1. agregação e decisões
(cd scripts && python3 mapa_agregacoes.py && python3 gera_pagina.py && python3 gera_mrv_comparecimento.py)
python3 scripts/gera_decisoes.py          # data/decisoes.json
# 2 e 3. planta-base, mesas, prancheta
(cd scripts && python3 salao.py && python3 planta_base.py && python3 mesas.py && python3 gera_mesas.py)
python3 scripts/gera_editor.py && node scripts/teste_prancheta.js
python3 scripts/folgas_prancheta.py [cenarios/<arquivo>.json]
# 4. simulações (o simulador lê a geometria que gera_editor.py acabou de gravar)
python3 scripts/gera_simulador.py && node simulador/teste_arranjos.js && node simulador/teste_modelo.js claude 16
python3 scripts/simula_fluxo.py
# 5. Ring 3
python3 scripts/layout_ring3.py
# 6. sinalização
python3 scripts/gera_plano_sinalizacao.py
# 7. barreiras internas e Ring 3 nas dimensões oficiais
python3 scripts/tensa_barreiras.py && python3 scripts/ring3.py && python3 scripts/gera_pagina_ring3.py
# 8. fitas no piso (motor do simulador) e desenho sobre a planta
node simulador/fitas.js 8 && python3 scripts/fitas_piso.py
# 9. decisões em aberto e instruções de fluxo (leem as opções vigentes)
python3 scripts/decisoes_abertas.py && python3 scripts/gera_instrucoes_fluxo.py
# 10. portas vivas, Ring 3 ao vivo e dashboard (por último: copia as peças)
node simulador/teste_portas.js
python3 scripts/gera_ring3_vivo.py && python3 scripts/gera_dashboard.py
```

**Decisões em aberto (13/09/2026).** O que o Posto ainda não decidiu sobre o
fluxo (portas, porta preferencial, checkpoint, desenho do Ring 3, unifilas,
sinalização externa e interna, voluntários, cor ou letra) está em
`scripts/decisoes_abertas.py`, com as opções, a opção que as saídas de hoje
assumem, `depende_de` e os efeitos de cada opção sobre as outras decisões. O
módulo valida o grafo (acíclico, uma opção vigente por decisão) e grava
`data/decisoes_abertas.json` e `docs/decisoes_em_aberto.md`; a seção
"Decisões em aberto" do dashboard e `docs/instrucoes_fluxo.md` (instruções de
gerenciamento de fluxo para o treinamento, um bloco por posto) saem do mesmo
registro. Mudar uma decisão = trocar `vigente`, regenerar. Tarefas (não
decisões) continuam em `PENDENCIAS`; o orçamento preenchível está em
`orcamento_final.md`.

Toda saída em `saidas/` é gerada por script: editar HTML ou SVG à mão se perde
na próxima geração. Os geradores falham em vez de gravar saída errada quando
uma validação não passa.

## Etapa 1 em detalhe: agregação de seções

### Fontes

Os três arquivos em `data/raw/` vieram da pasta do Google Drive do usuário:

| Arquivo | Gerado em | Papel |
|---|---|---|
| `eleitorado_local_votacao_2026_ZZ.csv` | 13/08/2026 | Seção a seção no exterior: papel (Principal/Agregada), `NR_SECAO_PRINCIPAL`, `QT_ELEITOR_SECAO` |
| `Filtrado_Dublin.csv` | 14/07/2026 | Perfil do eleitorado de Dublin, com `NR_SECAO` × `NM_LOCAL_VOTACAO` × `QT_ELEITORES` |
| `mapa_agregacoes_TSE.png` | 13/08/2026 | Mapa oficial de pares principal → agregada |

Ambos os CSVs estão em **latin-1**, separados por `;`. O `Filtrado_Dublin.csv`
foi re-exportado com a linha inteira envolvida em aspas e as aspas internas
duplicadas, então precisa de um passo de desempacotamento, tratado em
`scripts/parse_dados.py`. `NM_LOCAL_VOTACAO` no arquivo de perfil é o local de
votação original do eleitor e é usado como referência de onde ele reside.

A designação **MRV 1–28 → seção principal** vem da convocação de mesários do
DJE/TRE-DF (Ano 2026 n. 139, 04/08/2026), transcrita em
`scripts/gera_mrv_comparecimento.py` e `data/mrv_secoes.json`; não está em
nenhum CSV do TSE. `handoff_agregacao_dublin_2026.md` traz a taxa de
comparecimento de 2022 por domicílio de origem: taxa histórica, de qualidade
desigual entre localidades, **não** comparecimento oficial por seção.

### Resultado em uma linha

16.794 eleitores, 51 seções, 28 urnas. As urnas variam de 398 a **797**
eleitores. As 23 urnas que somam duas seções vão de 429 a 797; as 5 restantes
operam com uma seção só, perto de 400.

### Saídas

- **`saidas/Dublin_2026_agregacoes.xlsx`**: cinco abas, `Urnas` (28 linhas,
  ordenadas por total combinado), `Secoes` (as 51), `Residencia x Secao`,
  `Residencia x Urna` e `Inconsistencias`.
- **`saidas/dublin_agregacoes.html`**: a mesma análise em página visual.
- **`saidas/dados.json`**: os dados estruturados que alimentam a página e todas
  as etapas seguintes.
- **`saidas/mrv_secoes_comparecimento.md`**: MRV × seção × aptos × comparecimento
  esperado pela base B (não oficial; ver aviso no próprio arquivo).
- **`data/decisoes.json`**: a tabela mestra com classe, cor e entrada de cada
  MRV, os papéis das portas e o Ring 3, gerada por `scripts/gera_decisoes.py`.

### Validações

`mapa_agregacoes.py` falha em vez de gravar saída errada se alguma destas não
passar:

1. Soma por seção = soma por urna = total do perfil do eleitorado (16.794 nos
   três caminhos).
2. As 51 seções sobrevivem ao processamento e o número de urnas fecha em 28.
3. **Conferência independente:** o total calculado para cada uma das 28 urnas
   coincide com `QT_ELEITOR_ELEICAO_FEDERAL`, campo que o próprio TSE já
   publica agregado na seção principal.

### Achados

**Erro de digitação no PNG do TSE.** O mapa lista a seção agregada 3752 sob a
principal **3222**, que não existe em Dublin (pertence ao Porto). A correta é a
**3322** (Dublin, 398 eleitores), como consta do CSV oficial. O CSV prevalece;
o caso está na aba `Inconsistencias`, e a 3322 é ao mesmo tempo uma das três
urnas críticas.

**Cada seção é de uma única localidade.** Nas 51 seções, 100% dos eleitores
vêm de um mesmo local de origem. As 28 seções principais são todas de
residentes em Dublin (11.155 eleitores); as 23 agregadas trazem os condados do
interior e mais 4 seções de Dublin.

**Duas naturezas de urna cheia.** No topo do ranking convivem urnas que somam
duas seções de Dublin (3313, 3322, 3315) e urnas que somam uma seção de Dublin
com uma seção inteira do interior (3142 com Limerick, 3161 e 3245 com Cork,
3305 e 3108 com Galway). São 4.213 eleitores, 25% da zona, que residem fora de
Dublin e passam a votar lá.

## Etapas 2 a 7, em resumo

- **Planta-base** (`docs/CONTEXTO.md`, `saidas/planta_base.html`): geometria
  medida do PDF do RDS e codificada em `scripts/salao.py`, fonte única; portas
  chamadas pelo número de fachada (N1, N2, L1–L4, S1–S9, O1, O2, R1); desenha
  as entradas A/B/C e as saídas decididas.
- **Prancheta** (`saidas/editor.html`): as 28 mesas pareadas, com fileira
  recuada na fachada leste, numeradas pelo MRV do DJE e coloridas por carga;
  editor em escala com alinhar à parede, conferência de pares, medir, salvar e
  exportar cenários, papéis das portas e contorno do Ring 3; biblioteca em
  `cenarios/` lida por `scripts/cenarios.py`.
- **Simulador** (`saidas/simulador_fluxo.html`): eventos discretos, eleitor a
  eleitor, sobre qualquer arranjo da prancheta, com as entradas do Ring 3 e as
  portas da decisão; Cenário Claude (arranjo "Três polos", checkpoint a 16 m,
  3/3/3 atendentes) escolhido por varredura. `scripts/simula_fluxo.py` responde
  à pergunta do fechamento: só dois cadernos em paralelo fecham às 17h com
  caderno físico.
- **Ring 3** (`saidas/plano_ring3.md`): ~39 × 35 m; entradas S4/S5/S6, saídas
  S2/S8; três serpenteados (3·9·3 balizas) e duas baias, 1.402 pessoas; 300
  separadores, 100 a adquirir (~EUR 1.302); evacuação e pendências. Nas
  dimensões oficiais (44 × 35 m), `scripts/ring3.py` desenha as alternativas
  sem garganta, com corredor em L e fita — ver seção própria abaixo.
- **Sinalização** (`saidas/plano_sinalizacao.html`): oito pontos do portão da
  Merrion Road à urna; uma consulta só (seção → mesa → entrada), replicada a
  cada 25–30 m; mesas pelo MRV e entradas do plano do Ring 3; cor ou letra
  para as filas ainda em aberto; tabela mestra de 51 linhas.
- **Horários de pico** (`pesquisa_horarios_pico_votacao.md`): não há
  estatística oficial por hora; padrão de abertura forte, vale ao meio-dia e
  repique às 17h; em Dublin 2022 a fila não esvaziou o dia inteiro.

O que a integração de 06/09 resolveu (comparecimento, numeração, portas,
números do Ring 3 na sinalização) e o que ficou (curvas de chegada, arranjo da
mesa receptora, cor ou letra) está no §9 da documentação.

## Fitas no piso em vez do checkpoint

`docs/alternativa_fitas_no_piso.md` examina a sugestão de tirar o checkpoint e
guiar o eleitor da porta à mesa por fitas no piso. `simulador/fitas.js` roda o
motor oficial do simulador com e sem checkpoint sobre o arranjo Três polos e
mede a geometria das fitas; `scripts/fitas_piso.py` desenha as fitas sobre a
planta e monta `saidas/fitas_piso.html`.

```bash
node simulador/fitas.js 8          # saidas/fitas_piso.json
python3 scripts/fitas_piso.py      # saidas/fitas_piso.{md,html} e fitas_piso_*.svg
```

## Barreiras internas: cenário 1e e as hipóteses de corte (11/09)

Registro completo, com as alternativas descartadas e os riscos que a escolha
aceita: [`saidas/tensa_barreiras.md`](saidas/tensa_barreiras.md). O caminho até
ela, com as correções feitas e as premissas declaradas, está em
[`registro_barreiras_hall2.md`](registro_barreiras_hall2.md).

- **`saidas/tensa_barreiras.md`** — o registro da decisão, com o desenho adotado,
  as alternativas descartadas e os riscos aceitos.
- **`saidas/propostas_alternativas.md`** — duas hipóteses de corte, com plano e
  desenho cada: **A**, unifila só para separar até o checkpoint; **B**, unifila só
  nas mesas pareadas e nas grandes. Mais a síntese **C**, o único corte que o
  documento recomenda.
- **`saidas/tensa_barreiras.json`** — os números estruturados, cenário a cenário.
- **`saidas/barreiras_hall2.html`** — a planta em escala com os sete traçados
  ([publicada](https://claude.ai/code/artifact/e2db2813-7842-4425-a028-ba64cd790981)).
- **`saidas/prancheta_hall2.json`** — o cenário salvo, extraído do artefato da
  prancheta, para a conta ser reproduzível sem abrir a página.

```bash
python3 scripts/tensa_barreiras.py    # saidas/tensa_barreiras.{md,json} e barreiras_hall2.html
```

Qual traçado vale depende das decisões D2 (checkpoint) e D4 de
`scripts/decisoes_abertas.py`.

## Ring 3 nas dimensões oficiais: corredor em L e fita com CCB na ponta (11/09)

`scripts/ring3.py` modela o compound de fila ao ar livre do RDS, **44,0 × 35,0 m
(medida oficial)**, 14 m ao sul da fachada do Hall 2. O eleitor entra pelo
**canto nordeste**, desce rente ao gradil leste e vira no fundo: o corredor de
chegada é um **L** de 3,0 m, e as três zonas são alimentadas pelo trecho de
fundo. Restam dois desenhos, pela direção das raias.

| | Raias N–S | Raias L–O |
|---|---:|---:|
| Lotação (toda em raia) | 1.997 | 1.964 |
| Raias por zona | 8/10/8 | 23/23/23 |
| Meias-voltas | 23 | 66 |
| Separadores | 371 | 371 |
| A comprar (estoque 200) | 171 | 171 |

**Só duas coisas são separador**, por decisão do Posto: as divisórias entre as
raias (708,4 m) e a parede que separa a zona C da corrente que desce pelo
corredor lateral (32,0 m). Saíram da conta o contorno das zonas — que passa a
ser fita, 160,2 m —, a parede do corredor de chegada (39,8 m) e as raias do
apron até as portas (87,7 m): 288 m, 144 separadores a menos.

### Cenário 3 — CCB só na ponta, fita grossa no resto

A divisória vira fita do tipo de isolamento, ancorada por **um CCB na ponta
livre** (o vão da meia-volta). A separação da zona C continua barreira inteira.

| | N–S barreira inteira | N–S CCB na ponta | L–O CCB na ponta |
|---|---:|---:|---:|
| Separadores | 371 | **39** | 82 |
| A comprar (estoque 200) | 171 | **0** | 0 |
| Fita grossa | — | 662,4 m | 576,4 m |
| Lotação | 1.997 | 1.997 | 1.964 |

A barreira deixa de ser proporcional ao *comprimento* da raia e passa a ser
proporcional ao *número* de raias — por isso o girado, com 66 divisórias curtas,
custa mais que o N–S com 23 longas. Ressalva registrada no plano: cada divisória
fica com 28,8 m de vão livre de fita; com apoio a cada 5 m seriam 115 apoios, e
se forem CCB o total volta a 154.

Cada corrida que a conta soma está desenhada em `saidas/ring3_barreiras_*.svg`,
colorida pelo componente; o mapa **é** a conta, e `scripts/ring3.py` recusa a
gerar a planta se os dois não fecharem (`confere_mapa`).

O plano vigente (`scripts/layout_ring3.py`, `saidas/plano_ring3.md`) não está
neste repositório: foi produzido em sessão anterior e não chegou a ser
versionado. Reconstruído das cotas publicadas, continua servindo de aferição do
modelo de densidade — reproduz os 855 dos serpenteados e os 547 das baias.

```bash
python3 scripts/ring3.py              # saidas/ring3.json, plano_ring3_horizontal.md e as plantas
python3 scripts/gera_pagina_ring3.py  # saidas/ring3_horizontal.html
```

Memória de trabalho: `contexto_ring3_2026.md`.
