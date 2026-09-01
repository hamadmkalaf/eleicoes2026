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

O desenho de fluxo do salão está em `docs/CONTEXTO.md`: geometria do Hall 2,
premissas, e a planta-base em `saidas/planta_base.html`, que numera as portas
por fachada. Nenhuma ideia de layout está desenhada no momento.

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

Segunda etapa: a partir das 28 urnas apuradas acima, desenhar por onde o eleitor
entra, caminha, vota e sai no salão do RDS. **Nenhum layout está desenhado no
momento** — as duas ideias que existiam foram zeradas a pedido. O que está no
repositório é a base comum a qualquer layout: a geometria do salão, as
premissas, a carga das urnas e a planta-base com as portas numeradas.

**`docs/CONTEXTO.md` é o documento de passagem** — geometria medida, premissas,
restrições, resultados e perguntas em aberto. Leia primeiro.

```bash
cd scripts
python3 salao.py           # confere os dados e a capacidade de parede
python3 planta_base.py     # gera saidas/planta_base.svg e .html
```

### `scripts/salao.py` — o núcleo comum

Geometria do salão medida direto dos PDFs oficiais do RDS (o que já estava no
repositório e a versão revisada com as duas portas de carga assinaladas), com a
escala de 8,69 pt/m aferida contra a ficha técnica impressa no próprio
documento: 50,2 m × 44,5 m, 2.238 m². Daí saem as sete aberturas utilizáveis da
parede sul e as saídas de emergência das outras três paredes. Traz também as
premissas de comparecimento e mobiliário, a simulação de fila e o cálculo de
quantas MRVs cabem no perímetro sob dadas hipóteses.

| Premissa | Valor | Origem |
|---|---|---|
| Comparecimento, residentes em Dublin | 74% | taxa observada em 2022 |
| Comparecimento, residentes no interior | 50% | taxa observada em 2022 |
| Tempo por eleitor (ponto de projeto) | 55 s | escolhido; ver sensibilidade |
| Perfil de chegada (8h–17h) | 8/13/15/14/12/11/10/9/8 % | pico de meio de manhã |
| Módulo da MRV | 2,80 × 1,90 m | mesa de 1,60 × 0,70 m + mesa redonda de Ø 0,90 m + estrutura de sigilo |
| Recuo das saídas de emergência | 3,0 m | nenhuma seção dentro dessa faixa |
| Área por pessoa em fila | 1,0 m² | fila serpenteada com balizadores |

### Achados que valem para qualquer layout

- **11.418 eleitores esperados** dos 16.794 aptos.
- **Três urnas críticas** — 3313, 3322 e 3315, as que somam duas seções inteiras
  de Dublin — com 586 a 590 comparecentes cada. Depois delas há um degrau: as
  oito seguintes ficam entre 466 e 492, e as dezessete restantes abaixo de 435.
  Sete das oito somam um condado inteiro do interior, e esses 4.213 eleitores
  chegam em rajada, não diluídos ao longo do dia.
- O tempo de atendimento domina tudo. A fila de pico somada nas 28 urnas vai de
  **33 pessoas a 45 s/eleitor** para **241 a 55 s**, **436 a 60 s** e **2.165 a
  90 s** — fator 65.
- **O perímetro é escasso.** Com o recuo de 3 m determinado para a parede leste
  e o módulo de 2,80 m, a parede comporta 19 das 28 posições. A parede leste
  some por inteiro: cada trecho livre entre os recuos mede 2,79 m, um centímetro
  a menos que o módulo. Se o recuo valer para todas as saídas de emergência,
  caem para 11; com o módulo em linha (1,80 m de frente), sobem para 29.

### A planta-base

`scripts/planta_base.py` desenha o salão vazio e é onde a numeração das portas
é definida. O código do RDS numera folhas de porta e não localiza nada, então
cada porta ganhou **um número por fachada**, atribuído na ordem de leitura do
desenho: de oeste para leste nas paredes norte e sul, de norte para sul nas
paredes leste e oeste — N1, N2, L1 a L4, S1 a S7, O1, O2, mais a R1 na parede do
recorte. O código do RDS continua impresso abaixo de cada número.

A planta registra o que já está determinado sobre as portas e nada além disso:

- **Parede leste inteira em emergência**, com os 3 m de recuo desenhados em
  torno de cada vão.
- **N1 fechada.**
- **N2 desbloqueada** — é a saída do catering.

Entrada e saída de eleitor **não** aparecem: essa decisão vem depois.

Saídas em `saidas/planta_base.svg` e `saidas/planta_base.html`.
