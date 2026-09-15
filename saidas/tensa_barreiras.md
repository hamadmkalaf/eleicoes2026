# Separadores Tensa para o Hall 2 — desenho adotado

> **Decisão do Posto: cenário 1e.** 100 postes, 111 com reserva de 10%, 146 m de
> fita, EUR 1.745 ex-VAT com entrega. Os cenários 1 e 1i ficam registrados como
> alternativas descartadas, para a decisão continuar auditável.

Base: cenário **`Hamad_3polos`** da *Prancheta do Hall 2* (salvo em 05/09/2026,
sobre a planta A), com as 28 mesas nas posições em que Hamad as deixou, os
papéis de porta já decididos (S4 = entrada **A**, S5 = **B**, S6 = **C**) e a
classe de comparecimento de cada MRV. Salão aferido na planta do RDS:
**50,3 × 44,4 m** úteis, 2.238 m² brutos.

Reproduzir: `python3 scripts/tensa_barreiras.py` (lê
`saidas/prancheta_hall2.json`, grava `saidas/tensa_barreiras.json`).

## O que será montado

**1. Canais de entrada.** Duas linhas de 20 m, da parede sul ao checkpoint,
posicionadas nos limites entre os vãos: uma entre A e B, outra entre B e C. São
as duas que de fato separam as três correntes de eleitores. As portas S4, S5 e
S6 são contíguas — 5,93 m cada, 0,29 m entre vãos —, então três canais precisam
de divisórias compartilhadas, e o desenho adotado fica só com as do meio.

**2. Uma linha no meio de cada par.** Onde duas mesas se encaram através do
corredor de serviço, uma única linha entre elas separa as duas filas. Funciona
porque os mesários sentam entre 2,4 e 4,1 m da parede e a fila só começa onde o
módulo termina, a 4,10 m: na profundidade da fila aquele corredor é chão livre.

**3. Uma linha por mesa sem par**, rente à fila, do lado dos mesários.

**4. Comprimentos pela escada 10/5/3 m** — 10 m nos três polos de alto
comparecimento, 5 m nas de média, 3 m nas de baixa.

| Item | Corridas | Comp. | Fitas | Postes |
|---|--:|--:|--:|--:|
| divisórias entre os canais A\|B e B\|C | 2 | 20,0 m | 20 | 22 |
| bochechas de portão no checkpoint | — | — | 0 | 6 |
| polos isolados (22, 23, 24) | 3 | 10,0 m | 15 | 18 |
| linha do meio de par (10–11, 17–18) | 2 | 5,0 m | 6 | 8 |
| mesas sem par (9, 15, 16, 21) | 4 | 5,0 m | 12 | 16 |
| linha do meio de par (7 pares) | 7 | 3,0 m | 14 | 21 |
| mesas sem par (5, 6, 12) | 3 | 3,0 m | 6 | 9 |
| **Total** | **21** | | **73** | **100** |

**Encomendar 111 unidades**, não 100: os 100 são o consumo exato do desenho e
não deixam um único poste de reserva para quebra ou realocação no dia.

## Como se conta um poste

O produto é o **Tensa Barrier (2 m Black Ribbon)**: um poste com fita retrátil
de 2,00 m que engata no poste seguinte. Uma corrida reta de *L* metros gasta
`⌈L/2⌉` fitas e **`⌈L/2⌉ + 1` postes** — o poste a mais é o de ponta, que fecha
a corrida. O custo segue o número de **corridas independentes**, não a metragem.

## O pareamento real do `Hamad_3polos`

Rodando a regra de pareamento da própria prancheta — mesmo giro, mesmo recuo da
parede, mesários de lados opostos, a segunda caindo do lado para onde a primeira
põe os seus — sobre as posições salvas, e retirando 22, 23 e 24 do sorteio
porque estão isoladas de propósito:

| | Mesas | Quais |
|---|--:|---|
| **Pares** | 18 | 1–2, 3–4, 7–8, 10–11, 13–14, 17–18, 19–20, 25–26, 27–28 |
| **Sem par** | 7 | 5, 6, 9, 12, 15, 16, 21 |
| **Polos** | 3 | 22, 23, 24 |

Não é "todas pareadas menos os polos": são **nove pares e sete mesas soltas**.
**5, 16 e 21** ficaram sozinhas porque eram os pares de 22, 23 e 24 antes de eles
serem afastados; **6, 9, 12 e 15** já estavam sem par na planta salva.
Aritmeticamente também não fecharia: 28 − 3 = 25 é ímpar.

Se as mesas forem reposicionadas para formar mais pares, cada novo par converte
**duas linhas em uma**: 2 fitas e 3 postes a menos, a 3 m.

## O orçamento fecha, no limite

O item (d) do telegrama de revisão contratou **100 unidades (200 m) por EUR
1.303,00**. O desenho adotado consome exatamente esses 100 postes e 146 dos 200
metros de fita — folga de 27% em fita, folga nenhuma em poste.

| | Contratado | 1e consome | Sobra |
|---|--:|--:|--:|
| Postes | 100 | 100 | 0 |
| Fita | 200 m | 146 m | 54 m |

A reserva de 10% (11 unidades) é o único complemento a pedir: **EUR 165 ex-VAT**
ao preço de lista da M. O'Byrne Hire (EUR 15,00/unidade), ou EUR 143 ao preço
unitário já negociado no telegrama (EUR 13,03).

Custo total do desenho adotado, com as 111 unidades e a entrega em Dublin com
coleta (EUR 80,00): **EUR 1.745 ex-VAT / EUR 2.146 inc-VAT** a preço de lista.

## Alternativas descartadas

| Cenário | Corridas | Fitas | Postes | +10% | EUR ex-VAT | Por que não |
|---|--:|--:|--:|--:|--:|---|
| **1e** | 21 | 73 | **100** | **111** | 1.745 | **adotado** |
| 1 | 23 | 93 | 122 | 135 | 2.105 | as duas bordas externas do canal são contenção, não separação |
| 1i | 23 | 97 | 126 | 139 | 2.165 | +28 unidades sobre o adotado, fora do contratado |

## O que a adoção do 1e aceita como risco

**A escada 3/5/10 não equaliza resiliência, e o 1e a mantém.** Quanto cada fila
aguenta antes de transbordar, a 60 s por voto e pico de 1,8× a média
(comparecimento espalhado em 9 h, das 8h às 17h):

| Classe | Fila | Cabe | Chegada no pico | Cresce | Lota em |
|---|--:|--:|--:|--:|--:|
| alta (3313) | 10 m | 20 pessoas | 1,97/min | 0,97/min | **21 min** |
| média (3302) | 5 m | 10 pessoas | 1,73/min | 0,73/min | **14 min** |
| baixa (3179) | 3 m | 6 pessoas | 1,41/min | 0,41/min | **15 min** |
| baixa (3308) | 3 m | 6 pessoas | 0,98/min | −0,02/min | não lota |

Os 10 m dos polos estão bem calibrados; os **5 m das mesas de média é que estão
curtos** — 5 m sobre 518 esperados é proporção pior que 10 m sobre 590. Era isso
que o cenário 1i corrigia, ao custo de 28 unidades a mais. Ao adotar o 1e, o
Posto aceita que **oito mesas de média e quatro de baixa transbordem em 14 a 19
minutos de pico sustentado**. Doze mesas, portanto, dependem de gestão de piso e
não da barreira.

**O limite externo dos canais deixa de ser físico.** Sem as duas bordas, o que
mantém o eleitor dentro do canal entre a porta e o checkpoint é sinalização e
equipe. Isso torna a pergunta em aberto sobre a pré-triagem — mediada por pessoa
ou por sinalização — parte do desenho, e não mais um detalhe operacional.

**Cada fila fica guiada de um lado só.** Enquanto a fila couber no comprimento
previsto, funciona. Quando transborda, a ponta sem guia se espalha lateralmente
e encosta na fila vizinha. A economia é real e o seu preço é que o desenho
depende de a fila não estourar.

## Verificações de geometria

Rodadas contra as posições reais das 28 mesas:

- Nenhuma linha invade a faixa de entrada/checkpoint (x 19,10–37,47 / y 0–20).
- Nenhuma linha cruza outra, invade módulo de mesa ou sai do salão.
- Toda linha de par equidista dos dois módulos (desvio máximo de 1 cm, no par
  7–8, onde os recuos diferem em 20 cm).
- Folga mais apertada: o polo **23 (3315)** termina a **3,13 m** do topo do
  checkpoint. É a única medida que merece conferência em campo.

No desenho adotado nenhuma linha precisa ser aparada. (No 1i, descartado, o par
17–18 pediria 7,5 m e só teria 5,5 m até a faixa de entrada — as mesas da parede
leste entre y = 11 e y = 20 têm só ~5,7 m de chão livre.)

## Efeitos de segunda e terceira ordem

**Segunda ordem.** O checkpoint continua sendo o gargalo não paralelizável. No
pico a porta B recebe **14,1 pessoas/min**; a 10 s por conferência cada posição
atende 6, então B precisa de **três posições**, A e C de duas a três. Nenhuma
barreira compensa checkpoint com pessoal a menos — e no 1e, que devolve o limite
externo do canal à equipe, a conta de gente cresce de novo.

**Terceira ordem.** Os três polos são 3313, 3315 e 3322 — as três urnas
Dublin+Dublin de ~790 aptos que sustentam a contraproposta ao TSE. Se o TSE
aceitar desagregar, o pico por mesa cai de 590 para ~335, a classe de 10 m deixa
de existir e os polos podem voltar a parear. A agregação do TSE não custa só
mesários e tempo de apuração — custa metro linear de barreira.

**Terceira ordem, no fluxo.** Fila longa na porta desestimula o comparecimento, e
quem desiste antes de entrar não aparece em estatística nenhuma. O reservatório
do surto das 8h não está dentro do salão: é o apron do **Ring 3** (~1.402
pessoas na prancheta). A fila externa precisa ser desenhada junto com a interna
— e no 1e, sem bordas de canal, a transição da calçada para o canal é o ponto
mais frágil do percurso.

## Premissas a validar antes de encomendar

1. **Fita de 2,00 m por poste** — confirmado no anúncio do fornecedor. Há modelos
   de 2,3 m e 3,0 m; com 3,0 m a contagem cai cerca de 30%.
2. **Que a linha única do meio seja aceita** para separar as duas filas de um par.
   Se o Cartório Eleitoral exigir canal fechado por fila, a conta volta a duas
   linhas por fila e o 1e deixa de existir.
3. **Que o canal de entrada possa ficar sem borda externa.** É o que distingue o
   1e do cenário 1, e vale 22 postes.
4. Vãos de 5,93 m em S4, S5 e S6, com 0,29 m entre eles — medidos na planta do
   RDS, conferir em campo.
5. Densidade de 2,0 pessoas por metro (0,50 m cada) e 60 s por voto, com pico de
   1,8× a média. Se a identificação for por caderno físico (90 s), nenhuma fila
   de 3 m se sustenta e a decisão pelo 1e precisa ser reaberta.

---

Página com a planta e os três cenários lado a lado:
<https://claude.ai/code/artifact/e2db2813-7842-4425-a028-ba64cd790981>
