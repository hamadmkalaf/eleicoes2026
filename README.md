# Eleições 2026 — Dublin · Hall 2 do RDS

Dois trabalhos sobre o 1º turno de 04/10/2026 na zona eleitoral de Dublin, que
concentra as 51 seções da Irlanda em 28 urnas num único local: o **Royal Dublin
Society – Hall 2** (Merrion Road, Ballsbridge, Dublin 4 D04 AK83).

1. **Agregações de seções** — quantos eleitores há em cada seção e onde eles
   residem, sobre o mapa que o TSE propôs.
2. **Separadores de fila do salão** — quantos postes Tensa o desenho de fila
   consome, sobre as posições reais das mesas.

## Decisão em vigor

**O desenho de fila adotado é o cenário 1e:** uma linha no meio de cada par de
mesas, uma linha por mesa sem par, e apenas as duas divisórias que separam as
entradas A, B e C — sem as bordas externas dos canais.

**100 postes** de consumo, **111 a encomendar** com reserva de 10%, 146 m de
fita, EUR 1.745 ex-VAT com entrega. Cabe nas 100 unidades já contratadas no item
(d) do orçamento, com folga de fita e folga nenhuma de poste.

Registro completo, com as alternativas descartadas e os riscos que a escolha
aceita: [`saidas/tensa_barreiras.md`](saidas/tensa_barreiras.md).

---

## 1. Agregações de seções

16.794 eleitores, 51 seções, 28 urnas. As urnas variam de 398 a **797**
eleitores. As 23 que somam duas seções vão de 429 a 797; as 5 restantes operam
com uma seção só, perto de 400.

### Fontes

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

> **Nota sobre a base.** `contexto_eleicoes_dublin_2026.md` registra 14.626
> aptos, número de uma planilha anterior do TSE. O CSV oficial de 13/08/2026 traz
> **16.794**, e é ele que prevalece em todo o processamento deste repositório.

### Como rodar

```bash
pip install pandas openpyxl
cd scripts
python3 mapa_agregacoes.py   # gera saidas/Dublin_2026_agregacoes.xlsx e saidas/dados.json
python3 gera_pagina.py       # gera saidas/dublin_agregacoes.html
```

`parse_dados.py` também roda sozinho e imprime um resumo da carga.

### Saídas

- **`saidas/Dublin_2026_agregacoes.xlsx`** — cinco abas: `Urnas` (28 linhas,
  ordenadas por total combinado), `Secoes` (as 51), `Residencia x Secao`,
  `Residencia x Urna` e `Inconsistencias`.
- **`saidas/dublin_agregacoes.html`** — a mesma análise em página visual.
- **`saidas/dados.json`** — os dados estruturados que alimentam a página.

### Validações

`mapa_agregacoes.py` falha em vez de gravar saída errada se alguma destas não
passar:

1. Soma por seção = soma por urna = total do perfil do eleitorado (16.794 nos
   três caminhos).
2. As 51 seções sobrevivem ao processamento e o número de urnas fecha em 28.
3. **Conferência independente:** o total calculado para cada uma das 28 urnas
   coincide com `QT_ELEITOR_ELEICAO_FEDERAL`, campo que o próprio TSE já
   publica agregado na seção principal. Dois caminhos de cálculo, mesmo número.

### Achados

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

---

## 2. Separadores de fila do salão

`scripts/tensa_barreiras.py` conta postes e fitas de separador Tensa a partir do
cenário **`Hamad_3polos`** da *Prancheta do Hall 2* — as 28 mesas nas posições
salvas, os papéis de porta decididos (S4 = A, S5 = B, S6 = C) e a classe de
comparecimento de cada MRV.

```bash
python3 scripts/tensa_barreiras.py   # lê saidas/prancheta_hall2.json,
                                     # grava saidas/tensa_barreiras.json
```

### Saídas

- **`saidas/tensa_barreiras.md`** — o registro da decisão, com o desenho adotado,
  as alternativas descartadas e os riscos aceitos.
- **`saidas/propostas_alternativas.md`** — duas hipóteses de corte, com plano e
  desenho cada: **A**, unifila só para separar até o checkpoint; **B**, unifila só
  nas mesas pareadas e nas grandes. Mais a síntese **C**, o único corte que o
  documento recomenda.
- **`saidas/tensa_barreiras.json`** — os números estruturados, cenário a cenário.
- **`saidas/barreiras_hall2.html`** — a planta em escala com os três cenários
  ([publicada](https://claude.ai/code/artifact/e2db2813-7842-4425-a028-ba64cd790981)).
- **`saidas/prancheta_hall2.json`** — o cenário salvo, extraído do artefato da
  prancheta, para a conta ser reproduzível sem abrir a página.

### Como se conta

Uma corrida reta de *L* metros gasta `⌈L/2⌉` fitas e `⌈L/2⌉ + 1` postes — o poste
a mais é o de ponta, que fecha a corrida. **O custo segue o número de corridas
independentes, não a metragem.**

### Verificações

O script confere, contra as posições reais das 28 mesas, que nenhuma linha
invade a faixa de entrada até o checkpoint, cruza outra linha, invade módulo de
mesa ou sai do salão; e apara a linha que esbarraria na faixa de entrada,
registrando o corte. No desenho adotado nenhuma linha precisa ser aparada.

---

## Escopo

Na **análise de agregações** nenhum modelo de tempo de votação foi aplicado, a
pedido: as saídas entregam os totais ordenados e o critério de gargalo fica a
cargo de quem analisa.

Na **contagem de separadores** há um modelo de tempo, porque dimensionar fila
exige um: 60 s por voto, pico de 1,8× a média sobre a janela das 8h às 17h, e
2,0 pessoas por metro de fila. São premissas declaradas, não medições — estão
listadas em `saidas/tensa_barreiras.md` e mudá-las muda o resultado.
