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

## Simulador de fluxo do Hall 2

Segundo artefato, irmão da prancheta: recebe o arranjo das 28 mesas (cenário A
ou B da prancheta, ou um cenário salvo nela colado como JSON) e as respostas às
perguntas de organização do fluxo, e simula o dia de votação eleitor a eleitor.
Três telas: **Premissas**, **Simulação** (planta minuto a minuto) e
**Resultado** (relatório com critérios aprovados, em atenção ou reprovados).

```bash
python3 scripts/gera_simulador.py   # gera saidas/simulador_fluxo.html
node simulador/teste_modelo.js claude 16   # roda o motor em Node e imprime o resumo
node simulador/varredura.js 3       # varre combinações e ranqueia (demora alguns minutos)
```

Arquivos:

| Arquivo | Papel |
|---|---|
| `simulador/modelo.js` | Motor: geometria herdada da prancheta, curva de chegada, simulação por eventos discretos, vereditos e texto. Roda no navegador e em Node. |
| `simulador/app.js` | Interface das três telas. |
| `simulador/template.html` | Casca HTML e CSS; o gerador embute dados, motor e interface. |
| `data/prancheta_hall2.json` | Base da prancheta: salão, portas, módulo da mesa, posições das 28 mesas nos cenários A e B. |
| `data/mrv_secoes.json` | MRV 1–28 → seção principal e agregada, conforme a convocação de mesários (DJE TRE-DF n. 139, 04/08/2026). MRV k é a k-ª seção principal em ordem crescente. |
| `simulador/varredura.js` | Varredura que escolheu o Cenário Claude. |

### O que é fixo e o que é premissa

Fixo em todos os cenários: identificação pelo caderno (sem biometria), liberação
controlada na porta, curva de chegada das 7h às 17h (8 % chegam antes da
abertura), caminhada a 1,2 m/s, 0,6 m por pessoa em fila, 200 m de fita de
unifila contratados. Premissas escolhidas por quem simula: portas de entrada e
saída na fachada sul, número e recorte das zonas, onde a numeração MRV começa,
existência, distância e atendentes do checkpoint, fila por peso de mesa,
política de liberação, comparecimento, tempos de identificação e voto, triagem
e capacidade do Ring 3.

### Cenário Claude

Escolhido por varredura de 4.228 combinações: três zonas geográficas (parede
norte, parede leste, recorte + parede oeste), entradas pelas três portas duplas
do meio (S5 → norte, S6 → leste, S4 → oeste), saídas pelas portas de carga das
pontas (S1 e S9), numeração começando na parede leste (MRV 1–12 leste, 13–20
oeste, 21–28 norte), checkpoint a 14 m com 2/3/2 atendentes, filas de 4/5/8 por
mesa leve/média/pesada, e as mesas 23 e 24 deslocadas para o norte para a fila
da mesa do recorte não invadir a mesa vizinha. Zera cruzamentos de saída com
corredor de entrada e mantém as mesas pesadas sem fome. O que sobra é
estrutural: fila de abertura de ~950 pessoas às 8h e espera P90 de ~1 h, que só
mais mesas, identificação mais rápida ou chegada mais espalhada mudam.
