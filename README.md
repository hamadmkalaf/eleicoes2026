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

`handoff_agregacao_dublin_2026.md` (fornecido pelo usuário) traz a taxa de
comparecimento de 2022 por domicílio de origem, usada em
`scripts/gera_mrv_comparecimento.py` — não é um CSV do TSE, é uma taxa
histórica com qualidade de dado desigual entre localidades (ver o arquivo
gerado para o detalhe).

## Como rodar

```bash
pip install pandas openpyxl
cd scripts
python3 mapa_agregacoes.py          # gera saidas/Dublin_2026_agregacoes.xlsx e saidas/dados.json
python3 gera_pagina.py              # gera saidas/dublin_agregacoes.html
python3 gera_mrv_comparecimento.py  # gera saidas/mrv_secoes_comparecimento.md
```

`parse_dados.py` também roda sozinho e imprime um resumo da carga.

## Saídas

- **`saidas/Dublin_2026_agregacoes.xlsx`** — cinco abas: `Urnas` (28 linhas,
  ordenadas por total combinado), `Secoes` (as 51), `Residencia x Secao`,
  `Residencia x Urna` e `Inconsistencias`.
- **`saidas/dublin_agregacoes.html`** — a mesma análise em página visual.
- **`saidas/dados.json`** — os dados estruturados que alimentam a página.
- **`saidas/mrv_secoes_comparecimento.md`** — junta o número de MRV (fonte:
  convocação de mesários do DJE/TRE-DF, não está nos CSVs do TSE) à seção e
  ao eleitorado apto de cada urna. Inclui uma estimativa de comparecimento
  por seção, calculada com a taxa de comparecimento de 2022 por domicílio de
  origem citada em `handoff_agregacao_dublin_2026.md` — **não é
  comparecimento oficial por seção**, que não existe em nenhum arquivo deste
  repositório; ver aviso e coluna de qualidade do dado no próprio arquivo.

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
