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

O desenho de fluxo do salão está em `docs/CONTEXTO.md`, com a planta-base
(`saidas/planta_base.html`) e as duas ideias de layout.

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
entra, caminha, vota e sai no salão do RDS. Há mais de um layout possível, então
o código separa o que é comum do que é específico de cada ideia.

**`docs/CONTEXTO.md` é o documento de passagem** — geometria medida, premissas,
restrições, resultados e perguntas em aberto. Leia primeiro.

```bash
cd scripts
python3 salao.py           # confere os dados e a capacidade de parede
python3 ideia1_ilhas.py    # gera saidas/ideia1_dados.json
python3 ideia1_planta.py   # gera saidas/ideia1_planta.svg
python3 ideia1_pagina.py   # gera saidas/ideia1_plano.html
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
- **O perímetro é escasso.** Com o recuo de 3 m em todas as saídas de emergência
  e o módulo de 2,80 m, a parede comporta 11 das 28 posições; a parede leste
  some por inteiro, porque cada trecho livre entre as saídas 2.16 a 2.23 mede
  2,79 m. Relaxar o recuo para só a parede leste leva a 19; usar o módulo em
  linha (1,80 m de frente) leva a 21; as duas coisas juntas, a 29.

### Ideia 1 — três fileiras de ilhas

Como o sigilo do voto vem da estrutura que fecha o fundo e os lados da urna, e
não da parede, este layout tira as 28 MRVs das paredes.

- **Duas frentes de entrada pelas portas de carga**, nas extremidades da fachada
  sul e a 37 m uma da outra; **saída pela baia central 2.4**, com 2.5/2.6 e
  2.2/2.3 de reforço no pico; 2.7 e 2.1 só como emergência. A fachada se lê em
  três blocos contíguos: entra na ponta oeste, sai pelo meio, entra na ponta
  leste.
- **Três fileiras**, todas com os módulos voltados para o sul. O eleitor entra na
  baia pelo corredor de distribuição, vota e sai pelo fundo do módulo no
  corredor de retorno, que corre para a espinha central. Corredores de entrada e
  de retorno se alternam em faixas paralelas e nunca se cruzam.
- A tela da urna aponta para o painel lateral do módulo — perpendicular tanto à
  fila quanto ao retorno.
- A carga cresce da fileira 3 (junto às portas) para a fileira 1 (ao fundo); as
  três urnas críticas ficam agrupadas num setor reforçado de 16,5 × 12 m no
  canto noroeste, com quatro mesários cada.

Três consequências de custo: as baias sozinhas pedem cerca de **477 m de
balizador**, contra os 200 m orçados na alínea (d) do telegrama; a alimentação
elétrica das urnas passa a ser em ilha, não pela parede; e a divisão de
eleitores entre as duas frentes fica em **52/48**.

### Ideia 2 — todo o fluxo nas paredes

A fazer. `docs/CONTEXTO.md` registra o que já se sabe: a viabilidade depende de
duas perguntas de fato — se o recuo de 3 m vale só para as saídas 2.16 a 2.23 e
se a urna pode ficar atrás da mesa em vez de ao lado — e os problemas que a
exploração anterior desse layout já encontrou.
