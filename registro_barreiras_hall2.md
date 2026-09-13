# Registro de trabalho — separadores de fila do Hall 2

Memória da conversa que produziu a contagem de separadores Tensa para o Hall 2 do
RDS, entre **06 e 13/09/2026**. Guarda o caminho, não só o resultado: o que foi
pedido em cada rodada, o que os dados desmentiram, as correções feitas e por quê.

Os documentos vivos são outros — [`saidas/tensa_barreiras.md`](saidas/tensa_barreiras.md)
para a decisão e [`saidas/propostas_alternativas.md`](saidas/propostas_alternativas.md)
para as hipóteses de corte. Este aqui é o histórico.

---

## 1. A pergunta, em quatro rodadas

| | Pedido | O que mudou |
|---|---|---|
| **1** | Estimar separadores para filas de entrada (portas A/B/C até um checkpoint a 20 m) e uma fila por mesa: 3 m nas de baixa, 5 nas de média, 10 nas de alta. Mais um cenário com serpentina. | Primeira contagem, com duas linhas por fila. |
| **2** | Usar o cenário `Hamad_3polos` da Prancheta do Hall 2. | A conta passou a rodar sobre posições reais, não sobre a planta genérica. |
| **3** | Nos pares, uma linha só, no meio. Apagar as serpentinas — não são executáveis. | A conta caiu quase pela metade. |
| **4** | Adotar o **1e**. Alinhar o repositório. | Decisão registrada; contradições varridas. |
| **5** | Duas hipóteses de corte: unifila só até o checkpoint; unifila só nas pareadas e grandes. | Hipóteses A e B, mais a síntese C. |

---

## 2. Fontes

| Fonte | O que deu |
|---|---|
| Página do produto **M. O'Byrne Hire**, "Tensa Barrier (2m Black Ribbon)" (print enviado na conversa) | Fita de 2,00 m por poste; EUR 15,00 ex-VAT / 18,45 inc-VAT; entrega em Dublin com coleta, EUR 80,00 |
| **Prancheta do Hall 2**, cenário salvo `Hamad_3polos` (05/09/2026, 18h45) | Posição das 28 mesas, papel das portas, comparecimento esperado e classe de cada MRV. Extraído para `saidas/prancheta_hall2.json` |
| `RDS_Hall_2_Floorplan_(1).pdf` | Hall 2: 50,2 × 44,5 m brutos, 2.238 m², pé-direito 7 m |
| `data/raw/eleitorado_local_votacao_2026_ZZ.csv` (TSE, 13/08/2026) | 16.794 aptos, 51 seções, 28 urnas |
| `contexto_eleicoes_dublin_2026.md` | Orçamento (itens a e d), janela 8h–17h, taxas de comparecimento de 2022, apron do Ring 3 |

Salão de trabalho: **50,3 × 44,4 m** de contorno útil, com o recorte a noroeste.

---

## 3. Dados de partida

**Comparecimento esperado: 11.499** sobre 16.794 aptos (base B da prancheta — taxa
de 2022 por domicílio de origem). Mesma base em todos os cenários.

**Portas de entrada, na parede sul, contíguas:**

| Porta | Vão RDS | x | Largura | Esperados | Pico |
|---|---|---|--:|--:|--:|
| A | S4 | 19,10–25,03 | 5,93 m | 3.642 | 12,1/min |
| B | S5 | 25,32–31,25 | 5,93 m | 4.215 | 14,1/min |
| C | S6 | 31,54–37,47 | 5,93 m | 3.642 | 12,1/min |

Entre um vão e o seguinte há **0,29 m**. Essa contiguidade é o achado geométrico
mais rentável do trabalho: três canais compartilham divisórias e pedem **quatro
linhas, não seis** — ou duas, se só as do meio forem mantidas.

**Classes de comparecimento** (regra da prancheta: as 3 maiores = alta;
esperado ≥ 450 = média; abaixo = baixa). A escada 10/5/3 m pedida encaixou nelas
sem ajuste nenhum:

| Classe | Mesas | Fila | Quais |
|---|--:|--:|---|
| alta | 3 | 10 m | 22 (3313, 590), 23 (3315, 586), 24 (3322, 588) |
| média | 8 | 5 m | 9, 10, 11, 15, 16, 17, 18, 21 — 466 a 518 |
| baixa | 17 | 3 m | as demais — 295 a 423 |

As três de alta são as urnas Dublin+Dublin de ~790 aptos. Estão uma por porta —
**24 → A, 22 → B, 23 → C** — e afastadas nas três paredes. É a origem do nome
"três polos".

---

## 4. Como se conta um poste

O produto é um poste com fita retrátil de 2,00 m que engata no poste seguinte.
Uma corrida reta de *L* metros gasta `⌈L/2⌉` fitas e **`⌈L/2⌉ + 1` postes** — o
poste a mais é o de ponta, que fecha a corrida.

**Consequência que manda em tudo: o custo segue o número de corridas
independentes, não a metragem.** Trinta e quatro filas de 3 m custam mais postes
do que a mesma metragem em poucas corridas longas. Toda economia encontrada no
trabalho veio de cortar corridas.

---

## 5. Rodada 1 — duas linhas por fila

Primeira modelagem: cada fila de mesa como um canal fechado, duas linhas.

| Cenário | Postes |
|---|--:|
| 1 — canais retos + fila em toda mesa | 252 |
| 1e — 3 m com guia de um lado, divisórias partilhadas | 193 |
| 1i — filas dimensionadas por fôlego | 262 |
| 2 — serpentina na entrada + 10 m só nas de alta | 218 |
| 2b — serpentina + fila em todas as mesas | 384 |

Conclusão da rodada, hoje superada: o item (d) do orçamento estaria
subdimensionado por um fator de 2 a 4.

Registrou-se então que a serpentina de corredores **longos** (no sentido da
profundidade) gasta menos da metade dos postes de uma serpentina de corredores
atravessados — 44 contra ~94 por porta, mesma capacidade — porque cada corrida
longa gasta um único poste de ponta. O ponto morreu com a rodada 3, mas a
aritmética continua válida se a serpentina voltar à mesa.

---

## 6. Rodada 2 — o cenário salvo

A conta passou a rodar sobre `Hamad_3polos`. Os números da rodada 1 não mudaram
de forma, mas ganharam verificação geométrica contra posições reais.

---

## 7. Rodada 3 — uma linha por par

**Nova regra:** onde há par, uma única linha no meio, separando as duas filas;
onde não há, a mesa ganha a sua própria linha, de um lado só. Toda fila fica com
exatamente uma linha ao lado.

Funciona porque os mesários sentam entre 2,4 e 4,1 m da parede e a fila só começa
onde o módulo termina, a **4,10 m**: na profundidade da fila, o corredor de
serviço entre as duas mesas do par é chão livre.

As serpentinas foram apagadas a pedido — não executáveis.

| Cenário | Antes | Depois |
|---|--:|--:|
| 1 | 252 | **122** |
| 1e | 193 | **100** |
| 1i | 262 | **126** |

---

## 8. Rodada 4 — a decisão

**Cenário 1e adotado.** Uma linha no meio de cada par, uma por mesa sem par, e só
as duas divisórias que separam A de B e B de C — sem as bordas externas dos
canais.

Varredura de contradições no repositório inteiro (seção 10).

---

## 9. Rodada 5 — as hipóteses de corte

Duas hipóteses deliberadamente opostas: uma gasta barreira **só na entrada**, a
outra **só nas mesas**. A comparação mostrou que a carga não é simétrica —
**uma divisória de entrada organiza 12 a 14 pessoas/min por porta; uma linha de
mesa organiza 1 a 2** — e que o corte defensável é a interseção das duas (C).

---

## 10. Correções feitas no caminho

Quatro, e vale registrar todas, porque três delas mudaram conclusões.

### 10.1 A premissa de pareamento não se sustentou

Foi dito que "quase todas as mesas estão pareadas, com exceção de 24, 23 e 22".
Rodando a regra de pareamento da própria prancheta sobre as posições salvas — e
retirando os três polos do sorteio, porque estão isolados de propósito:

| | Mesas | Quais |
|---|--:|---|
| Pares | 18 | 1–2, 3–4, 7–8, 10–11, 13–14, 17–18, 19–20, 25–26, 27–28 |
| **Sem par** | **7** | **5, 6, 9, 12, 15, 16, 21** |
| Polos | 3 | 22, 23, 24 |

São nove pares e sete soltas. **5, 16 e 21** ficaram sozinhas porque eram os pares
de 22, 23 e 24 antes de eles serem afastados; **6, 9, 12 e 15** já estavam sem par
na planta salva. Aritmeticamente também não fecharia: 28 − 3 = 25 é ímpar.

A conta foi feita sobre o pareamento real. Cada novo par que vier de
reposicionamento converte duas linhas em uma: 3 postes a menos, a 3 m.

### 10.2 Duas contagens de corridas digitadas à mão

Na rodada 1, a coluna "corridas" do relatório trazia 47 para o 1e e 62 para o 1i,
quando os valores corretos eram **41** e **60**. Fitas e postes, que saíam do
script, estavam certos. Desde então o script imprime a coluna a partir do próprio
cálculo, para não divergir de novo.

### 10.3 O veredito sobre o orçamento inverteu

Com duas linhas por fila, o item (d) — 100 unidades por EUR 1.303,00 — parecia
subdimensionado por um fator de 2 a 4. Com uma linha por par, **ele cobre o
desenho adotado exatamente**: 100 postes de consumo, 146 dos 200 m de fita.
Falta só a reserva de 10%.

### 10.4 Contradições no repositório, varridas na rodada 4

- O `README.md` dizia que **nenhum modelo de tempo de votação foi aplicado**.
  Verdade para a análise de agregações, falso para a contagem de separadores, que
  não existe sem um. Os dois escopos foram separados e as premissas, declaradas.
- **14.626 aptos** era planilha anterior do TSE; o CSV oficial traz **16.794**.
  Os dois números conviviam em arquivos diferentes do mesmo repositório.
- **"4 cabines de alto volume (~600 cada)"** eram três. Há dez urnas na faixa dos
  ~790 aptos, mas sete somam uma seção do interior, com comparecimento de ~50%, e
  caem para 466–518 esperados.
- **Dimensões do Hall 2** estavam como "a validar" e já haviam sido confirmadas.
- **Pendências 1 e 5** da seção 8 do contexto estavam resolvidas sem baixa. A
  **pendência 6** (pré-triagem mediada por pessoa ou por sinalização) ficou mais
  crítica, porque o 1e devolve o limite externo do canal à equipe.

---

## 11. Estado final — todos os traçados

| | Corridas | Fitas | Postes | +10% | EUR ex-VAT | Entrada separada | Mesas sem guia | Esperados sem guia |
|---|--:|--:|--:|--:|--:|:--:|--:|--:|
| **1e — adotado** | 21 | 73 | **100** | 111 | 1.745 | sim | 0 | 0 |
| 1 — com as bordas | 23 | 93 | 122 | 135 | 2.105 | sim | 0 | 0 |
| 1i — por fôlego | 23 | 97 | 126 | 139 | 2.165 | sim | 0 | 0 |
| C — síntese | 14 | 55 | 75 | 83 | 1.325 | sim | 7 | 3.028 |
| B2 — pares, polos e médias soltas | 16 | 47 | 63 | 70 | 1.130 | não | 3 | 1.079 |
| B — só pares e polos | 12 | 35 | 47 | 52 | 860 | não | 7 | 3.028 |
| A — só o checkpoint | 2 | 20 | 28 | 31 | 545 | sim | 28 | 11.499 |

EUR ex-VAT já inclui a entrega de EUR 80,00 e a reserva de 10%. Inc-VAT a 23%.
Todos cabem nas 100 unidades contratadas; só o 1e pede as 11 da reserva.

---

## 12. Achados que sobrevivem a todas as rodadas

**A escada 3/5/10 m não equaliza resiliência.** A 60 s por voto e pico de 1,8× a
média, sobre a janela das 8h às 17h:

| Classe | Fila | Cabe | Cresce | Lota em |
|---|--:|--:|--:|--:|
| alta (3313) | 10 m | 20 | 0,97/min | **21 min** |
| média (3302) | 5 m | 10 | 0,73/min | **14 min** |
| baixa (3179) | 3 m | 6 | 0,41/min | **15 min** |
| baixa (3308) | 3 m | 6 | −0,02/min | não lota |

Os 10 m dos polos estão bem calibrados; os 5 m das de média é que estão curtos —
5 m sobre 518 esperados é proporção pior que 10 m sobre 590. Era o que o 1i
corrigia (média a 6–7,5 m) por 26 postes — 28 unidades com reserva. **Ao adotar o 1e, o Posto
aceita que doze mesas transbordem em 14 a 19 minutos de pico sustentado.**

**Treze mesas nunca precisam de barreira.** Cinco não lotam em hipótese nenhuma e
oito levam mais de meia hora para lotar. É o que dá razão parcial à hipótese A.

**O checkpoint é o gargalo, não a barreira.** No pico a porta B recebe 14,1
pessoas/min; a 10 s por conferência cada posição atende 6, então B precisa de
**três posições** e A e C de duas a três. Barreira nenhuma compensa checkpoint com
pessoal a menos.

**Trocar material por gente não é economia, nesta escala.** O item (a) do
orçamento contratou 216 hora-pessoa por EUR 6.774,84 — **EUR 31,37/h**. Os cinco
orientadores que a hipótese A exige custam EUR 1.569, e o total dela (EUR 2.114)
passa o desenho adotado. Só muda se as pessoas já existirem, e aí a decisão é de
escala de pessoal.

**A agregação do TSE custa metro linear de barreira.** Os três polos são 3313,
3315 e 3322 — as urnas Dublin+Dublin que sustentam a contraproposta. Se o TSE
aceitar desagregar, o pico por mesa cai de 590 para ~335, a classe de 10 m deixa
de existir e os polos podem voltar a parear.

**Verificações de geometria**, em todos os traçados: nenhuma linha invade a faixa
de entrada (x 19,10–37,47 / y 0–20), cruza outra, invade módulo de mesa ou sai do
salão. Toda linha de par equidista dos dois módulos (desvio máximo de 1 cm, no par
7–8). Folga mais apertada: o polo **23 (3315)** a **3,13 m** do checkpoint. No 1i,
o par 17–18 pediria 7,5 m e só teria 5,5 m — a parede leste entre y = 11 e y = 20
tem só ~5,7 m de chão livre.

---

## 13. Pontos em aberto

1. **Encomendar 111 unidades, não 100.** Os 100 são o consumo exato e não deixam
   um poste de reserva. As 11 custam EUR 143 ao preço unitário do próprio item (d).
2. **Confirmar a fita de 2,00 m na entrega.** Há modelos de 2,3 m e 3,0 m; com
   3,0 m a contagem cai ~30%.
3. **Validar com o Cartório Eleitoral que a linha única do meio serve** para
   separar as duas filas de um par. Se for exigido canal fechado por fila, o 1e
   deixa de existir e a conta volta a duas linhas por fila.
4. **Validar que o canal de entrada pode ficar sem borda externa.** É o que
   distingue o 1e do cenário 1, e vale 22 postes.
5. **Decidir a pré-triagem** — mediada por pessoa ou por sinalização. Com o 1e,
   ela virou parte do desenho.
6. **Conferir em campo** os vãos de 5,93 m e os 0,29 m entre eles, e a folga de
   3,13 m do polo 23.
7. **Se a identificação for por caderno físico (90 s por voto)**, nenhuma fila de
   3 m se sustenta e a decisão pelo 1e precisa ser reaberta.
8. **Desenhar a fila externa** junto com a interna. O reservatório do surto das 8h
   é o apron do Ring 3 (~1.402 pessoas), não o salão.

---

## 14. Onde está cada coisa

| | |
|---|---|
| Decisão e desenho adotado | [`saidas/tensa_barreiras.md`](saidas/tensa_barreiras.md) |
| Hipóteses de corte A, B, B2 e a síntese C | [`saidas/propostas_alternativas.md`](saidas/propostas_alternativas.md) |
| A conta, reproduzível | `python3 scripts/tensa_barreiras.py` |
| Números estruturados | `saidas/tensa_barreiras.json` |
| Cenário salvo da prancheta, extraído | `saidas/prancheta_hall2.json` |
| Planta com os sete traçados | `saidas/barreiras_hall2.html` · <https://claude.ai/code/artifact/e2db2813-7842-4425-a028-ba64cd790981> |
| Prancheta do Hall 2 (origem das posições) | <https://claude.ai/code/artifact/f6a9b812-2b5e-4972-bb81-104b018e16b0> |
| Pull request | <https://github.com/hamadmkalaf/eleicoes2026/pull/12> |

---

## 15. Premissas declaradas

Não são medições. Mudá-las muda o resultado.

| Premissa | Valor | Efeito se mudar |
|---|--:|---|
| Fita por poste | 2,00 m | 3,0 m derruba a contagem ~30% |
| Densidade de fila | 2,0 pessoas/m | com bagagem ou cadeira de rodas cai a 1,5–1,7 e todo o fôlego encolhe junto |
| Tempo por voto | 60 s | a 90 s nenhuma fila de 3 m se sustenta |
| Pico | 1,8× a média | move todos os tempos de transbordo |
| Janela | 8h–17h, 9 h | — |
| Comparecimento | 11.499 de 16.794 | base B da prancheta, taxa de 2022 por domicílio |
| Conferência no checkpoint | 10 s por eleitor | decide o número de posições por porta |
| Orientador de fila | 1 para cada 3 mesas | estimativa de planejamento; é a premissa mais frágil da hipótese A |
| Hora-pessoa de equipe | EUR 31,37 | inferida do item (a); segurança licenciada pode não ser o preço de orientador |
