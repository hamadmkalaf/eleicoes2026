# Separadores Tensa para o Hall 2 — estimativa

Base: cenário **`Hamad_3polos`** da *Prancheta do Hall 2* (salvo em 05/09/2026,
sobre a planta A), com as 28 mesas nas posições em que Hamad as deixou, os
papéis de porta já decididos (S4 = entrada **A**, S5 = **B**, S6 = **C**) e a
classe de comparecimento de cada MRV. Salão aferido na planta do RDS:
**50,3 × 44,4 m**, 2.238 m².

Reproduzir: `python3 scripts/tensa_barreiras.py` (lê
`saidas/prancheta_hall2.json`, grava `saidas/tensa_barreiras.json`).

## A regra de fila

**Uma única linha por par, no meio, separando as duas filas.** Mesa sem par
ganha a sua própria linha, de um lado só. Toda fila fica então com exatamente
uma linha ao lado — compartilhada quando há par, própria quando não há.

Isso funciona porque os mesários sentam entre 2,4 e 4,1 m da parede e a fila só
começa onde o módulo termina, a 4,10 m: na profundidade da fila o corredor de
serviço entre as duas mesas do par é chão livre, e a linha do meio cabe ali sem
disputar espaço com ninguém.

## Como se conta um poste

O produto é o **Tensa Barrier (2 m Black Ribbon)**: um poste com fita retrátil
de 2,00 m que engata no poste seguinte. Uma corrida reta de *L* metros gasta
`⌈L/2⌉` fitas e **`⌈L/2⌉ + 1` postes** — o poste a mais é o de ponta, que fecha
a corrida. O custo segue o número de **corridas independentes**, não a metragem.

## O pareamento real do `Hamad_3polos`

Aqui a premissa precisa de correção. Rodando a regra de pareamento da própria
prancheta — mesmo giro, mesmo recuo da parede, mesários de lados opostos, a
segunda caindo do lado para onde a primeira põe os seus — sobre as posições
salvas, e retirando 22, 23 e 24 do sorteio porque no `Hamad_3polos` estão
isoladas de propósito:

| | Mesas | Quais |
|---|--:|---|
| **Pares** | 18 | 1–2, 3–4, 7–8, 10–11, 13–14, 17–18, 19–20, 25–26, 27–28 |
| **Sem par** | 7 | 5, 6, 9, 12, 15, 16, 21 |
| **Polos** | 3 | 22, 23, 24 |

Não é "quase todas pareadas exceto 22, 23 e 24": são **nove pares e sete mesas
soltas**. Três dessas sete ficaram sozinhas justamente por causa dos polos —
**5, 16 e 21** eram os pares de 22, 23 e 24 antes de eles serem afastados. As
outras quatro — **6, 9, 12 e 15** — já estavam sem par na planta salva, e nem o
painel de Pares da prancheta as pareia.

Aritmeticamente também não fecharia: 28 − 3 = 25 é ímpar, e 25 mesas não formam
só pares. Se a intenção é ter todas pareadas menos os três polos, faltam **seis
mesas a reposicionar** na prancheta — 6, 9, 12, 15 mais duas de 5/16/21 — e uma
sobra de qualquer jeito.

O cálculo abaixo usa o pareamento real. Se as mesas forem reposicionadas, cada
novo par converte **duas linhas em uma** e economiza, a 3 m, 2 fitas e 3 postes.

## Os cenários

### 1 — canais retos, escada 10/5/3 m

Quatro linhas de 20 m nos canais de entrada (as portas S4, S5 e S6 são
contíguas — 5,93 m cada, 0,29 m entre vãos —, então três canais dividem
divisórias), uma linha no meio de cada par e uma por mesa solta.

| Item | Corridas | Comp. | Fitas | Postes |
|---|--:|--:|--:|--:|
| divisórias entre os canais A\|B e B\|C | 2 | 20,0 m | 20 | 22 |
| bordas externas dos canais | 2 | 20,0 m | 20 | 22 |
| bochechas de portão no checkpoint | — | — | 0 | 6 |
| polos isolados (22, 23, 24) | 3 | 10,0 m | 15 | 18 |
| linha do meio de par (10–11, 17–18) | 2 | 5,0 m | 6 | 8 |
| mesas sem par (9, 15, 16, 21) | 4 | 5,0 m | 12 | 16 |
| linha do meio de par (7 pares) | 7 | 3,0 m | 14 | 21 |
| mesas sem par (5, 6, 12) | 3 | 3,0 m | 6 | 9 |
| **Total** | **23** | | **93** | **122** |

**122 postes**, 186 m de fita. Com reserva de 10%: **135 unidades**.

### 1e — sem as bordas externas dos canais

Das quatro linhas do canal, só as **duas do meio** separam de fato A de B e B de
C. As duas das bordas são contenção, não separação, e podem sair — o limite
externo passa a ser sinalização e equipe.

Todo o resto é idêntico ao cenário 1. **100 postes**, 146 m. Com reserva: **111**.

### 1i — filas dimensionadas por fôlego

Mesma topologia, comprimentos calculados para que toda mesa aguente 20 minutos
de pico (60 s por voto, pico de 1,8× a média). **126 postes**, 194 m. Com
reserva: **139**.

| Cenário | Corridas | Fitas | Postes | +10% | EUR ex-VAT¹ | vs. 100 contratados |
|---|--:|--:|--:|--:|--:|--:|
| 1 — escada 10/5/3 m | 23 | 93 | 122 | **135** | 2.105 | +35 |
| 1e — sem bordas externas | 21 | 73 | 100 | **111** | 1.745 | +11 |
| 1i — por fôlego de 20 min | 23 | 97 | 126 | **139** | 2.165 | +39 |

¹ EUR 15,00/unidade ex-VAT (lista M. O'Byrne Hire) + EUR 80,00 de entrega em
Dublin com coleta. Inc-VAT a 23%: EUR 18,45/unidade.

## O orçamento agora fecha

Com uma linha por par em vez de duas por fila, a conta cai pela metade e a
leitura do orçamento se inverte: as **100 unidades (200 m) por EUR 1.303,00** já
contratadas no item (d) **cobrem o cenário 1e exatamente** — 100 postes, sem
folga. Para o cenário 1 faltam 35 unidades com reserva; para o 1i, 39. São EUR
450 a 510 de complemento ao preço de lista, não os milhares que a contagem de
duas linhas por fila indicava.

Duas ressalvas. Os 200 m contratados dão 100 fitas, e o cenário 1 usa 93 — a
folga de fita é de 7%, apertada para um dia de operação. E 100 postes exatos não
comportam reserva nenhuma: um poste que quebra ou uma fila que precisa ser
redesenhada no dia sai de outro lugar do salão.

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
21 minutos — porque 5 m sobre 518 esperados é proporção pior que 10 m sobre 590.

O cenário **1i** iguala o fôlego em 20 minutos: média vai a 6–7,5 m, quatro das
de baixa a 3,5–4,5 m, os polos ficam nos 10 m. Custa **quatro postes** a mais
que o cenário 1.

## Verificações de geometria

Rodadas contra as posições reais das 28 mesas, nos dois traçados:

- Nenhuma linha invade a faixa de entrada/checkpoint (x 19,10–37,47 / y 0–20).
- Nenhuma linha cruza outra, invade módulo de mesa ou sai do salão.
- Toda linha de par equidista dos dois módulos (desvio máximo de 1 cm, no par
  7–8, onde os recuos diferem em 20 cm).
- Folga mais apertada: o polo **23 (3315)** termina a **3,13 m** do topo do
  checkpoint.

**Uma linha não cabe no comprimento que o fôlego pede.** O par **17–18** pediria
7,5 m e só tem **5,5 m** até a faixa de entrada. A mesa 18 (3306, 515 esperados)
fica com fôlego de **15 minutos** em vez de 20, e é a única que não alcança a
meta sem sair do lugar. As mesas da parede leste entre y = 11 e y = 20 têm só
~5,7 m de chão livre entre o módulo e o corredor de entrada — é o trecho mais
apertado do salão para alongar fila.

## Efeitos de segunda e terceira ordem

**Segunda ordem.** A linha única no meio do par baixa o custo mas muda o que a
barreira faz: cada fila passa a ter guia de um lado só, e o outro lado é chão
aberto. Isso funciona enquanto a fila estiver dentro do comprimento previsto; no
momento em que transborda — 14 a 21 minutos de pico, conforme a mesa —, a ponta
sem guia se espalha lateralmente e encosta na fila vizinha do outro par. Ou
seja: a economia é real, e o seu preço é que o desenho depende de a fila não
estourar. Equipe de piso deixa de ser conveniência e vira parte da solução.

**Segunda ordem, ainda.** O checkpoint continua sendo o gargalo não
paralelizável. No pico a porta B recebe **14,1 pessoas/min**; a 10 s por
conferência cada posição atende 6, então B precisa de **três posições**, A e C de
duas a três. Nenhuma barreira compensa checkpoint com pessoal a menos.

**Terceira ordem.** Os três polos são 3313, 3315 e 3322 — as três urnas
Dublin+Dublin de ~790 aptos que sustentam a contraproposta ao TSE. Se o TSE
aceitar desagregar, o pico por mesa cai de 590 para ~335, a classe de 10 m deixa
de existir e os polos podem voltar a parear: seriam mais três linhas convertidas
em uma e meia. A agregação do TSE não custa só mesários e tempo de apuração —
custa metro linear de barreira.

**Terceira ordem, no fluxo.** Fila longa na porta desestimula o comparecimento, e
quem desiste antes de entrar não aparece em estatística nenhuma. O reservatório
do surto das 8h não está dentro do salão: é o apron do **Ring 3** (~1.402
pessoas na prancheta). A fila externa precisa ser desenhada junto com a interna.

## Recomendação

**Cenário 1i, 139 unidades** (EUR ~2.165 ex-VAT, ~2.663 inc-VAT). Custa 4 postes
a mais que o cenário 1 e é o único em que nenhuma mesa fica mais frágil que
outra — com a exceção declarada da 18, que a geometria da parede leste limita a
15 minutos.

Se o teto for o já contratado, **1e com 111 unidades** cabe em EUR 1.745 e
entrega a separação que importa: as duas divisórias entre A, B e C, e uma linha
por par.

## Premissas a validar

1. Fita de <b>2,00 m</b> por poste — confirmado no anúncio do fornecedor. Há
   modelos de 2,3 m e 3,0 m; com 3,0 m a contagem cai cerca de 30%.
2. Densidade de 2,0 pessoas por metro (0,50 m cada). Com bagagem, carrinho ou
   cadeira de rodas cai para 1,5–1,7 e todo o fôlego encolhe na mesma proporção.
3. 60 s por voto e pico de 1,8× a média. Se a identificação for por caderno
   físico (90 s), nenhuma fila de 3 m se sustenta.
4. Vãos de 5,93 m em S4, S5 e S6, com 0,29 m entre eles. É essa contiguidade que
   faz três canais pedirem quatro linhas — ou duas, no cenário 1e.
5. Que a linha única do meio seja aceita operacionalmente para separar as duas
   filas de um par. Se o Cartório Eleitoral pedir canal fechado por fila, a
   conta volta para duas linhas por fila.

---

Página com a planta e os três cenários lado a lado:
<https://claude.ai/code/artifact/e2db2813-7842-4425-a028-ba64cd790981>
