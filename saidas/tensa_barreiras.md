# Separadores Tensa para o Hall 2 — estimativa

Base: cenário **`Hamad_3polos`** da *Prancheta do Hall 2* (salvo em 05/09/2026,
sobre a planta A), com as 28 mesas nas posições em que Hamad as deixou, os
papéis de porta já decididos (S4 = entrada **A**, S5 = **B**, S6 = **C**) e a
classe de comparecimento de cada MRV. Salão aferido na planta do RDS:
**50,3 × 44,4 m**, 2.238 m².

Reproduzir: `python3 scripts/tensa_barreiras.py` (lê
`saidas/prancheta_hall2.json`, grava `saidas/tensa_barreiras.json`).

## Como se conta um poste

O produto é o **Tensa Barrier (2 m Black Ribbon)**: um poste com fita retrátil
de 2,00 m que engata no poste seguinte. Então uma corrida reta de *L* metros
gasta `⌈L/2⌉` fitas e **`⌈L/2⌉ + 1` postes** — o poste a mais é o de ponta, que
fecha a corrida.

A consequência orçamentária é contraintuitiva e vale registrar: **o que encarece
não é a metragem, é o número de corridas independentes.** Trinta e quatro filas
de 3 m (34 corridas, 102 postes) custam mais postes do que 372 m distribuídos em
poucas corridas longas. Toda economia abaixo vem de reduzir corridas, não metros.

## Escada de comprimentos e classes

A prancheta já classifica as mesas (regra: as 3 maiores = alta; esperado ≥ 450 =
média; abaixo = baixa), e a escada pedida encaixa nela sem ajuste:

| Classe | MRVs | Fila | Mesas |
|---|--:|--:|---|
| alta | 3 | 10 m | 22 (3313), 23 (3315), 24 (3322) — 590/586/588 esperados |
| média | 8 | 5 m | 9, 10, 11, 15, 16, 17, 18, 21 — 466 a 518 |
| baixa | 17 | 3 m | as demais — 295 a 423 |

Comparecimento esperado total **11.499** sobre 16.794 aptos (base B da
prancheta: taxa de 2022 por domicílio de origem).

## Cenário 1 — canais retos até o checkpoint (principal)

Três canais retos, do vão de cada porta até o checkpoint a 20 m, mais uma fila
por mesa.

**As portas S4, S5 e S6 são contíguas** — 5,93 m cada, com 0,29 m de intervalo
entre vãos. Isso é o achado geométrico que mais economiza no cenário: os três
canais dividem as divisórias e pedem **quatro linhas de 20 m, não seis**.

| Item | Corridas | Comp. | Fitas | Postes |
|---|--:|--:|--:|--:|
| canais A/B/C até o checkpoint | 4 | 20,00 m | 40 | 44 |
| bochechas de portão no checkpoint | — | — | 0 | 6 |
| filas de mesa — alta (3 × 10 m, 2 lados) | 6 | 10,00 m | 30 | 36 |
| filas de mesa — média (8 × 5 m, 2 lados) | 16 | 5,00 m | 48 | 64 |
| filas de mesa — baixa (17 × 3 m, 2 lados) | 34 | 3,00 m | 68 | 102 |
| **Total** | **60** | | **186** | **252** |

**252 postes**, 372 m de fita. Com reserva técnica de 10%: **278 unidades**.

## Cenário 2 — serpentina até o checkpoint + 10 m só nas de alta

Cada porta ganha um bloco de serpentina de 5,93 × 20 m, com **corredores no
sentido da profundidade** (5 corredores de 1,18 m por porta), e só as três mesas
de alta mantêm fila própria.

Corredores longos, e não atravessados, são deliberados: 4 corridas de 18,8 m por
porta gastam 44 postes; a mesma serpentina com corredores no sentido da largura
seriam 18 corridas curtas e ~94 postes por porta. Mesma capacidade, o dobro dos
postes. O preço é legibilidade — corredor de 20 m sem visão do fim desanima
quem entra —, que se compensa com sinalização de tempo estimado e aberturas de
atalho controladas pela equipe quando a fila está curta.

| Item | Corridas | Comp. | Fitas | Postes |
|---|--:|--:|--:|--:|
| bordas e divisas entre os três blocos | 4 | 20,00 m | 40 | 44 |
| divisórias internas — serpentina A | 4 | 18,80 m | 40 | 44 |
| divisórias internas — serpentina B | 4 | 18,80 m | 40 | 44 |
| divisórias internas — serpentina C | 4 | 18,80 m | 40 | 44 |
| bochechas de portão no checkpoint | — | — | 0 | 6 |
| filas de mesa — alta (3 × 10 m, 2 lados) | 6 | 10,00 m | 30 | 36 |
| **Total** | **22** | | **190** | **218** |

**218 postes**, 380 m de fita. Com reserva de 10%: **240 unidades**.

O cenário 2 sai **34 postes mais barato que o cenário 1** com *mais* metragem de
fita — porque troca 50 corridas curtas (as filas de média e baixa) por 12
corridas longas. É a aritmética das corridas outra vez.

## Variantes

| Cenário | Corridas | Fitas | Postes | +10% | EUR ex-VAT¹ |
|---|--:|--:|--:|--:|--:|
| 1 — canais retos + fila em toda mesa | 60 | 186 | 252 | **278** | 4.250 |
| 1e — 3 m com guia de um lado só, divisórias partilhadas | 47 | 146 | 193 | **213** | 3.275 |
| 1i — canais retos + fila dimensionada por fôlego | 62 | 196 | 262 | **289** | 4.415 |
| 2 — serpentina + 10 m só nas de alta | 22 | 190 | 218 | **240** | 3.680 |
| 2b — serpentina + fila em todas as mesas | 72 | 306 | 384 | **423** | 6.425 |

¹ EUR 15,00/unidade ex-VAT (lista M. O'Byrne Hire) + EUR 80,00 de entrega em
Dublin com coleta. Inc-VAT a 23%: EUR 18,45/unidade.

**1e** é o mínimo defensável: as 17 filas de 3 m viram guia de um lado só (o
módulo da mesa faz o outro lado) e as 7 vizinhanças em que duas filas correm a
≤ 1,70 m uma da outra dividem a divisória do meio — apuradas da geometria real
do `Hamad_3polos`: 10–9, 16–17, 26–27, 2–3, 4–5, 14–15, 18–19.

## O confronto com o orçamento já enviado

O telegrama de revisão orçamentária pediu **100 unidades (200 m) por EUR
1.303,00** — EUR 13,03 a unidade. Nenhum dos cenários cabe nisso:

| Cenário | Unidades | Faltam vs. 100 | EUR ao preço do telegrama |
|---|--:|--:|--:|
| 1 | 278 | +178 | 3.622 |
| 1e | 213 | +113 | 2.775 |
| 2 | 240 | +140 | 3.127 |
| 2b | 423 | +323 | 5.512 |

Ou seja: **o item (d) do orçamento está subdimensionado por um fator de 2 a 4**.
Mesmo o cenário mais enxuto pede o dobro do contratado. Isso precisa entrar na
próxima revisão antes de virar problema de véspera — e o custo incremental
(EUR 1.500 a 4.200) é pequeno diante dos EUR 70.050 do pleito, mas não é zero e
não se resolve alugando no dia.

## Achado: a escada 3/5/10 não equaliza resiliência

Quanto uma fila aguenta antes de transbordar, a 60 s por voto e pico de 1,8× a
média (comparecimento espalhado em 9 h, das 8h às 17h):

| Classe | Fila | Cabe | Chegada no pico | Cresce | Lota em |
|---|--:|--:|--:|--:|--:|
| alta (3313) | 10 m | 20 pessoas | 1,97/min | 0,97/min | **21 min** |
| média (3302) | 5 m | 10 pessoas | 1,73/min | 0,73/min | **14 min** |
| baixa (3179) | 3 m | 6 pessoas | 1,41/min | 0,41/min | **15 min** |
| baixa (3308) | 3 m | 6 pessoas | 0,98/min | −0,02/min | não lota |

**Os 10 m das mesas de alta estão bem calibrados; os 5 m das de média é que
estão curtos.** A fila de média aguenta *menos* pico que a de alta — 14 contra
21 minutos — porque 5 m sobre 518 esperados é uma proporção pior que 10 m sobre
590. A escada premia a mesa mais visível e deixa a segunda linha desprotegida.

O cenário **1i** corrige isso igualando o fôlego em 20 minutos para todas:

| Classe | Atual | Dimensionado | MRVs |
|---|--:|--:|---|
| alta | 10 m | **10,0 m** (sem mudança) | 22, 23, 24 |
| média | 5 m | **7,5 m** | 16, 18 |
| média | 5 m | **7,0 m** | 11, 15 |
| média | 5 m | **6,0 m** | 9, 10, 17, 21 |
| baixa | 3 m | **4,5 / 4,0 / 3,5 m** | 12 / 13, 14 / 20 |
| baixa | 3 m | **3,0 m** (piso) | as 13 restantes |

Custa **+10 postes** sobre o cenário 1 (262 contra 252). É a melhor relação
custo-benefício do conjunto: por dez postes, nenhuma mesa fica mais frágil que
outra.

## Verificações de geometria no `Hamad_3polos`

Rodadas contra as posições reais das 28 mesas:

- Nenhuma fila invade a faixa de entrada/checkpoint (x 19,10–37,47 / y 0–20).
- Nenhuma fila cruza outra fila.
- Nenhuma fila invade o módulo de outra mesa.
- Folga mais apertada: **MRV 23 (3315, alta, parede leste)** termina a
  **3,40 m** do topo do checkpoint. É a única que merece conferência em campo —
  qualquer alongamento dessa fila além de 13 m encosta no canal C.

## Efeitos de segunda e terceira ordem

**Segunda ordem.** A capacidade bruta não é o que separa os dois cenários. O
canal reto do cenário 1 tem 5,93 × 20 m = 118,6 m² por porta, e a 2 pessoas/m²
comporta ~237 pessoas — mais, em números, que os 100 m de corredor da serpentina
(~200 pessoas a 2 pessoas/m). O que a serpentina compra não é volume, é
**ordem**: fila única, chegada-atendimento em sequência visível, e vazão
previsível para o checkpoint. Num canal largo de 5,93 m a fila não é fila, é
aglomeração, e a ordem de chegada se perde — o que gera atrito na porta
justamente no momento de pico.

**Segunda ordem, ainda.** O checkpoint é o gargalo não paralelizável já
sinalizado no contexto. No pico, a porta B recebe **14,1 pessoas/min**; a 10 s
por conferência, cada posição atende 6/min, então B precisa de **3 posições**
para não represar, e A e C de 2 a 3 cada. Barreira nenhuma resolve um checkpoint
com pessoal a menos: ela só decide se a espera será ordenada ou não.

**Terceira ordem.** As três mesas de alta são 3313, 3315 e 3322 — as três urnas
Dublin+Dublin de ~790 aptos que já são o argumento central da contraproposta ao
TSE. Se o TSE aceitar desagregar (Cenário 4/5 do contexto), essas três somem
como categoria, o pico por mesa cai de 590 para ~335, e **a classe de 10 m
deixa de existir**: a demanda de barreiras cairia para algo próximo do cenário
1e. Vale dizer isso na negociação — a agregação do TSE não custa só mesários e
tempo de apuração, custa metro linear de barreira e área de salão.

**Terceira ordem, no fluxo.** Fila longa demais na porta desestimula o
comparecimento, e o eleitor que desiste antes de entrar não aparece em
estatística nenhuma — some como se nunca tivesse vindo. O reservatório real
para o surto de abertura das 8h não está dentro do salão: é o **apron do Ring 3**
(capacidade ~1.402 na prancheta). Vale desenhar a fila externa junto com a
interna, ou a serpentina de 20 m absorve 14 a 16 minutos de pico e depois
transborda para a calçada da Merrion Road sem ordenação nenhuma.

## Recomendação

**Cenário 1i, 289 unidades com reserva** (EUR ~4.415 ex-VAT, ~5.430 inc-VAT).
Mantém o desenho principal que Hamad pediu, custa dez postes a mais que o
cenário 1 e é o único que não deixa a segunda linha de mesas mais frágil que a
primeira.

Se o corte orçamentário for inevitável, **1e com 213 unidades** entrega o
essencial. O cenário 2 vale por si se a decisão for de *ordem na porta* e não de
economia — e nesse caso o número certo é 240.

## Premissas a validar

1. Fita de 2,00 m por poste — confirmado no anúncio do fornecedor, mas conferir
   na entrega (há modelos de 2,3 m e 3,0 m; com 3,0 m a contagem cai ~30%).
2. Densidade de 2,0 pessoas por metro de fila (0,50 m por pessoa). Com bagagem,
   carrinho de bebê ou cadeira de rodas cai para 1,5–1,7, e todo fôlego calculado
   acima encolhe na mesma proporção.
3. 60 s por voto e pico de 1,8× a média — as duas premissas que mais mexem no
   dimensionamento. Se a identificação for por caderno físico (90 s), nenhuma
   fila de 3 m se sustenta.
4. Se o checkpoint terá 2 ou 3 posições por porta. Abaixo de 3 em B, a fila
   externa vira o problema principal e o desenho interno perde relevância.
5. Largura de 5,93 m nos três vãos e os 0,29 m entre eles — medidos na planta do
   RDS, conferir em campo antes de encomendar.
