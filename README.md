# Agregações de seções eleitorais — Dublin, Eleições 2026

Análise do mapa de agregações que o TSE propôs para a zona eleitoral de Dublin
(Irlanda), no 1º turno de 04/10/2026. Responde a duas perguntas: **quantos
eleitores há em cada seção** (principal e agregada) e **onde esses eleitores
residem**.

Todas as 51 seções da Irlanda foram concentradas em 28 urnas num único local:
o **Royal Dublin Society – Hall 2** (RDS, Merrion Road, Ballsbridge, Dublin 4
D04 AK83).

## Resultado em uma linha

16.794 eleitores, 51 seções, 28 urnas. As urnas variam de 398 a **797**
eleitores. As 23 urnas que somam duas seções vão de 429 a 797; as 5 restantes
operam com uma seção só, perto de 400.

## Fontes

Os três arquivos em `data/raw/` vieram da pasta do Google Drive do usuário:

| Arquivo | Gerado em | Papel |
|---|---|---|
| `eleitorado_local_votacao_2026_ZZ.csv` | 13/08/2026 | Seção a seção no exterior: papel (Principal/Agregada), `NR_SECAO_PRINCIPAL`, `QT_ELEITOR_SECAO` |
| `Filtrado_Dublin.csv` | 14/07/2026 | Perfil do eleitorado de Dublin, com `NR_SECAO` × `NM_LOCAL_VOTACAO` × `QT_ELEITORES` |
| `mapa_agregacoes_TSE.png` | 13/08/2026 | Mapa oficial de pares principal → agregada |

Ambos os CSVs estão em **latin-1**, separados por `;`. O `Filtrado_Dublin.csv`
foi re-exportado com a linha inteira envolvida em aspas e as aspas internas
duplicadas, então precisa de um passo de desempacotamento — tratado em
`scripts/parse_dados.py`.

`NM_LOCAL_VOTACAO` no arquivo de perfil é o local de votação original do
eleitor e é usado aqui como referência de onde ele reside.

## Como rodar

```bash
pip install pandas openpyxl
cd scripts
python3 mapa_agregacoes.py   # gera saidas/Dublin_2026_agregacoes.xlsx e saidas/dados.json
python3 gera_pagina.py       # gera saidas/dublin_agregacoes.html
```

`parse_dados.py` também roda sozinho e imprime um resumo da carga.

## Saídas

- **`saidas/Dublin_2026_agregacoes.xlsx`** — cinco abas: `Urnas` (28 linhas,
  ordenadas por total combinado), `Secoes` (as 51), `Residencia x Secao`,
  `Residencia x Urna` e `Inconsistencias`.
- **`saidas/dublin_agregacoes.html`** — a mesma análise em página visual.
- **`saidas/dados.json`** — os dados estruturados que alimentam a página.

## Validações

`mapa_agregacoes.py` falha em vez de gravar saída errada se alguma destas não
passar:

1. Soma por seção = soma por urna = total do perfil do eleitorado (16.794 nos
   três caminhos).
2. As 51 seções sobrevivem ao processamento e o número de urnas fecha em 28.
3. **Conferência independente:** o total calculado para cada uma das 28 urnas
   coincide com `QT_ELEITOR_ELEICAO_FEDERAL`, campo que o próprio TSE já
   publica agregado na seção principal. Dois caminhos de cálculo, mesmo número.

## Achados

**Erro de digitação no PNG do TSE.** O mapa lista a seção agregada 3752 sob a
principal **3222**. Essa seção não existe em Dublin — pertence ao PORTO. A
seção correta é a **3322** (Dublin, 398 eleitores), como consta do CSV oficial.
O CSV prevalece no processamento; o caso está registrado na aba
`Inconsistencias`.

**Cada seção é de uma única localidade.** Nas 51 seções, 100% dos eleitores
vêm de um mesmo local de origem. As 28 seções principais são todas de
residentes em Dublin (11.155 eleitores); as 23 agregadas trazem os condados do
interior e mais 4 seções de Dublin.

**Duas naturezas de urna cheia.** No topo do ranking convivem urnas que somam
duas seções de Dublin (3313, 3322, 3315) e urnas que somam uma seção de Dublin
com uma seção inteira do interior (3142 com Limerick, 3161 e 3245 com Cork,
3305 e 3108 com Galway). São 4.213 eleitores — 25% da zona — que residem fora
de Dublin e passam a votar lá.

## Escopo

Nenhum modelo de tempo de votação foi aplicado, a pedido: as saídas entregam os
totais ordenados e o critério de gargalo fica a cargo de quem analisa.

## Desenho de fluxo do salão (RDS Hall 2)

`scripts/fluxo_layout.py` pega as 28 urnas apuradas acima, estima o
comparecimento por urna, simula a fila de cada uma ao longo das 9 horas de
votação e aloca cada urna a uma posição física no perímetro do Hall 2.
`scripts/planta_svg.py` desenha o resultado em escala.

```bash
cd scripts
python3 fluxo_layout.py   # gera saidas/fluxo_dados.json
python3 planta_svg.py     # gera saidas/planta_fluxo.svg
```

A geometria do salão foi medida do PDF oficial do RDS
(`RDS_Hall_2_Floorplan_(1).pdf`, página 2). A escala de 8,69 pt/m foi aferida
contra a ficha técnica impressa no próprio PDF — 50,2 m × 44,5 m, 2.238 m² —,
que confere com as dimensões usadas nas simulações anteriores. Daí saem as
cinco portas da parede sul (três vãos de 5,93 m e duas folhas de 1,25 m) e as
onze saídas de emergência das outras três paredes, que precisam ficar
desobstruídas e por isso recortam o perímetro disponível para as mesas.

### Premissas

| Premissa | Valor | Origem |
|---|---|---|
| Comparecimento, residentes em Dublin | 74% | taxa observada em 2022 |
| Comparecimento, residentes no interior | 50% | taxa observada em 2022 |
| Tempo por eleitor (ponto de projeto) | 55 s | escolhido; ver sensibilidade |
| Perfil de chegada (8h–17h) | 8/13/15/14/12/11/10/9/8 % | pico de meio de manhã |
| Área por pessoa em fila | 1,0 m² | fila serpenteada com balizadores |

### Resultados

- **11.418 eleitores esperados** dos 16.794 aptos.
- **Três urnas críticas** — 3313, 3322 e 3315, as que somam duas seções
  inteiras de Dublin — com 586 a 590 comparecentes cada. Depois delas há um
  degrau: as oito seguintes ficam entre 466 e 492, e as dezessete restantes
  abaixo de 435.
- O tempo de atendimento domina tudo. A fila de pico somada nas 28 urnas vai de
  **33 pessoas a 45 s/eleitor** para **241 a 55 s**, **436 a 60 s** e **2.165 a
  90 s**. O layout é dimensionado para 55 s e reserva piso livre para absorver
  o cenário de 60 s.
- As 28 posições ficam contra as paredes, com a carga crescendo conforme a
  distância até a porta da zona, de modo que nenhum eleitor de urna leve
  caminhe por trás da fila de uma urna pesada.
