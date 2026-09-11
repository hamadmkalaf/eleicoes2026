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
- **`saidas/plano_ring3_horizontal.md`**, **`saidas/ring3.json`**,
  **`saidas/ring3_horizontal.html`** e **`saidas/ring3_*.svg`** — o Ring 3
  girado, os números por entrada e as plantas em escala das geometrias
  comparadas.

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

## Ring 3 — a fila externa

`scripts/ring3.py` modela o compound de fila ao ar livre do RDS, **44,0 × 35,0 m
(medida oficial)**, 14 m ao sul da fachada do Hall 2. O eleitor entra pelo
**canto nordeste**, desce rente ao gradil leste e vira no fundo: o corredor de
chegada é um **L** de 3,0 m, e as três zonas são alimentadas pelo trecho de
fundo. Restam dois desenhos, pela direção das raias.

```bash
python3 scripts/ring3.py              # plano, JSON e as plantas em SVG
python3 scripts/gera_pagina_ring3.py  # a página
```

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

Cada corrida que a conta soma está desenhada em `saidas/ring3_barreiras_*.svg`,
colorida pelo componente; o mapa **é** a conta, e `scripts/ring3.py` recusa a
gerar a planta se os dois não fecharem (`confere_mapa`).

O plano vigente (`scripts/layout_ring3.py`, `saidas/plano_ring3.md`) não está
neste repositório: foi produzido em sessão anterior e não chegou a ser
versionado. Reconstruído das cotas publicadas, continua servindo de aferição do
modelo de densidade — reproduz os 855 dos serpenteados e os 547 das baias.


## Escopo

Nenhum modelo de tempo de votação foi aplicado, a pedido: as saídas entregam os
totais ordenados e o critério de gargalo fica a cargo de quem analisa.
