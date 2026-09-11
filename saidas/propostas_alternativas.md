# Duas hipóteses alternativas de unifila — Hall 2

Documento de trabalho. O desenho em vigor continua sendo o **1e**
(`saidas/tensa_barreiras.md`); aqui estão duas hipóteses de corte, cada uma com
o seu plano, o seu desenho e o que ela custa fora do orçamento de material.

Tudo contado sobre o mesmo cenário **`Hamad_3polos`** da Prancheta do Hall 2, com
a mesma regra de par (uma linha no meio) e a mesma escada 10/5/3 m, para as
comparações serem maçãs com maçãs. Reproduzir com
`python3 scripts/tensa_barreiras.py`.

## As duas hipóteses são complementares

Não é acaso que elas se oponham: uma gasta barreira **só na entrada**, a outra
**só nas mesas**. Juntas, cobrem a pergunta de onde o dinheiro de barreira rende
mais — e a resposta não é simétrica, porque a carga não é simétrica.

| | Onde a barreira atua | Carga no ponto, no pico |
|---|---|---|
| **A** | os 20 m entre a porta e o checkpoint | **12 a 14 pessoas/min por porta** |
| **B** | a boca de cada mesa | **1 a 2 pessoas/min por mesa** |

Uma divisória de entrada organiza dez vezes mais fluxo por metro do que uma
linha de mesa. Esse é o eixo de toda a análise abaixo.

---

# Proposta A — unifila só para separar até o checkpoint

**Duas corridas de 20 m e mais nada.** Uma divisória entre os vãos de A e B,
outra entre B e C, da parede sul ao checkpoint. Nenhuma barreira nas 28 mesas.

| Item | Corridas | Comp. | Fitas | Postes |
|---|--:|--:|--:|--:|
| divisórias entre os canais A\|B e B\|C | 2 | 20,0 m | 20 | 22 |
| bochechas de portão no checkpoint | — | — | 0 | 6 |
| **Total** | **2** | | **20** | **28** |

**28 postes, 31 com reserva de 10%, 40 m de fita. EUR 545 ex-VAT** com entrega —
**EUR 1.200 a menos que o 1e**, e 69 unidades sobrando do que já está contratado.

## O plano

1. **Montagem.** Duas linhas retas, ancoradas na parede sul nos limites
   19,10 → 25,18 e 25,18 → 31,40 (as portas S4/S5/S6 são contíguas, com 0,29 m
   entre vãos, então uma divisória serve os dois canais que ela separa). Cada
   linha sobe 20 m até o checkpoint. Duas horas de montagem, uma pessoa.
2. **Triagem.** Mantida como está: o eleitor é direcionado à porta A, B ou C
   na chegada e permanece na sua corrente até a conferência.
3. **Da triagem em diante, chão livre.** O eleitor recebe o número da mesa no
   checkpoint e caminha até ela sem canal. Na mesa, forma-se aglomeração, não
   fila.
4. **Equipe de piso substitui a barreira** nas mesas que acumulam.

## O que essa hipótese assume

Que a fila de mesa possa ser **um agrupamento gerido por pessoa** em vez de um
canal físico. É uma escolha legítima — muitos postos no exterior operam assim —
mas ela tem número.

**Quinze mesas precisam de gestão ativa.** São as que transbordam em até
20 minutos de pico sustentado, a 60 s por voto: as três de alta (21 min cada) e
mais doze — oito de média e quatro de baixa — entre 14 e 19 minutos.

| Mesas | Fôlego | Precisam de quem organize |
|---|--:|---|
| 16, 18 | 14 min | sim |
| 11, 15, 12 | 15 min | sim |
| 17, 13, 14 | 17 min | sim |
| 9, 10, 21 | 18 min | sim |
| 20 | 19 min | sim |
| 22, 23, 24 (polos) | 21 min | sim |
| 1, 2, 3, 4 | 24–38 min | vigilância ocasional |
| 5, 6, 7, 8 | 64–164 min | não |
| 19, 25, 26, 27, 28 | não lotam | não |

**Treze mesas não precisam de barreira nenhuma** — é o achado que dá razão
parcial à hipótese. As nove últimas da tabela nunca formam fila que justifique
um poste.

## O custo que sai do material e entra na folha

As quinze mesas que acumulam estão distribuídas nas três paredes. A uma
proporção de **um orientador para cada três mesas** — possível porque elas são
contíguas ao longo das paredes —, são **cinco pessoas** durante as dez horas de
operação.

O item (a) do orçamento contratou segurança por **EUR 6.774,84** cobrindo
20 pessoas × 10 h no dia mais 16 h na véspera: **216 hora-pessoa, EUR 31,37 a
hora**. Se os orientadores tiverem de ser contratados a esse mesmo preço:

| | Material | Equipe extra | Total |
|---|--:|--:|--:|
| 1e (adotado) | EUR 1.745 | — | **EUR 1.745** |
| **A** | EUR 545 | 5 × 10 h = **EUR 1.569** | **EUR 2.114** |

**A hipótese A não economiza: ela custa cerca de EUR 370 a mais que o desenho
adotado**, trocando material por gente. E gente que falta no dia é um risco que
poste alugado não tem.

Duas ressalvas honestas. O EUR 31,37/h vem de segurança contratada — porteiro
licenciado —, e orientador de fila pode ser mais barato. E se os orientadores
forem servidores do Posto ou voluntários já previstos, o custo marginal é zero,
e aí a conta vira de **disponibilidade de pessoas**, não de dinheiro. A pergunta
que decide a hipótese A é essa, e não o preço do poste.

## Onde a A falha

O agrupamento sem canal **perde a ordem de chegada**. Numa mesa de polo, com
1,97 pessoa/min chegando e uma sendo atendida por minuto, trinta minutos de pico
acumulam trinta pessoas em volta de uma mesa de 0,9 m de largura. Sem linha, a
ordem vira negociação, e negociação em dia de eleição vira reclamação formal.

Segundo: **aglomeração ocupa mais chão do que fila**. Uma fila de 2 pessoas/m
num canal de 0,9 m usa 2,2 pessoas/m²; o mesmo grupo solto se espalha a 1,5–2
pessoas/m² e invade o corredor de circulação. As mesas pareadas têm 2,5 a 3,1 m
de corredor de serviço entre si — é exatamente o espaço que o agrupamento toma
primeiro, e é por onde os mesários e o material circulam.

---

# Proposta B — unifila só nas mesas pareadas e nas grandes

**Doze corridas: a linha do meio de cada um dos nove pares e uma linha para cada
um dos três polos.** Nada na entrada.

| Item | Corridas | Comp. | Fitas | Postes |
|---|--:|--:|--:|--:|
| polos isolados (22, 23, 24) | 3 | 10,0 m | 15 | 18 |
| linha do meio de par (10–11, 17–18) | 2 | 5,0 m | 6 | 8 |
| linha do meio de par (1–2, 3–4, 7–8, 13–14, 19–20, 25–26, 27–28) | 7 | 3,0 m | 14 | 21 |
| **Total** | **12** | | **35** | **47** |

**47 postes, 52 com reserva, 70 m de fita. EUR 860 ex-VAT** — EUR 885 a menos
que o 1e.

**Variante B2**, se "mesas grandes" incluir as quatro de média que ficaram sem
par (9, 15, 16, 21): mais 4 corridas de 5 m, **63 postes, 70 com reserva,
EUR 1.130**.

## O plano

1. **Montagem.** Uma linha entre as duas mesas de cada par, começando a 4,10 m
   da parede (onde o módulo termina e a fila começa) e correndo o comprimento da
   maior das duas filas do par. Três linhas de 10 m rentes às filas dos polos.
2. **Entrada sem barreira.** Os três vãos, que somam 18,37 m contíguos, operam
   como uma única boca. A distribuição por porta passa a ser feita por
   sinalização e orientação verbal.
3. **Checkpoint** recebe a corrente única e faz a triagem.

## Por que essa é a hipótese mais frágil das duas

**Ela retira a barreira justamente do ponto de maior carga.** No pico chegam
12,1 pessoas/min por A e C e 14,1 por B — quase 38 por minuto no conjunto — e é
esse fluxo que os 18,37 m de vão indiferenciado passam a receber sem nenhuma
separação física.

E o que se perde ali não é conforto: é a **pré-triagem**, que o contexto
consolidado registra como a coisa que "estruturalmente resolve" o problema de
mesas calmas contaminadas pela fila de mesas movimentadas. Sem as duas
divisórias, as três correntes se misturam nos 20 m antes do checkpoint e a
designação por porta — A, B, C, já decidida e já colorida na planta — vira
recomendação, não percurso.

**A falha é sistêmica, não local.** Uma fila de mesa sem barreira degrada o
atendimento *daquela* mesa. A entrada sem separação degrada a triagem de
**todos os 11.499 eleitores**, porque é por ali que todos passam, uma única vez,
no momento de maior densidade do dia.

## E ainda deixa sete mesas descobertas

A hipótese B cobre as 18 pareadas e os 3 polos, e deixa de fora as sete soltas
— **3.028 eleitores esperados**, entre elas quatro de média que transbordam em
14 a 18 minutos:

| Mesa | MRV | Classe | Esperados | Lota em |
|---|---|---|--:|--:|
| 16 | 3302 | média | 518 | 14 min |
| 15 | 3245 | média | 498 | 15 min |
| 9 | 3108 | média | 467 | 18 min |
| 21 | 3311 | média | 466 | 18 min |
| 12 | 3179 | baixa | 423 | 15 min |
| 5 | 1160 | baixa | 328 | 64 min |
| 6 | 1352 | baixa | 328 | 64 min |

A variante **B2** resolve quatro das sete por 16 postes — e vale a pena se a
hipótese B for mesmo adotada. Mas não resolve a entrada, que é o buraco
principal.

---

# Síntese: o corte que faz sentido

As duas hipóteses testam extremos opostos, e a comparação mostra que o corte
defensável não é nenhum dos dois isolados, mas a interseção deles:

**Proposta C — as duas divisórias do checkpoint mais a linha do meio de cada par
e os três polos.** É o 1e sem as sete linhas das mesas soltas.

| Item | Corridas | Fitas | Postes |
|---|--:|--:|--:|
| divisórias A\|B e B\|C + bochechas | 2 | 20 | 28 |
| polos (22, 23, 24) | 3 | 15 | 18 |
| linhas do meio dos 9 pares | 9 | 20 | 29 |
| **Total** | **14** | **55** | **75** |

**75 postes, 83 com reserva, EUR 1.325 ex-VAT.** Economiza 25 postes e EUR 420
sobre o adotado, mantém a separação das três correntes e cobre 21 das 28 mesas.
A exposição são as mesmas sete soltas da hipótese B — mas agora sem o buraco da
entrada.

---

# Comparação

| | Postes | +10% | EUR ex-VAT | Entrada separada | Mesas sem guia | Esperados sem guia | Equipe extra |
|---|--:|--:|--:|:--:|--:|--:|--:|
| **1e** (adotado) | 100 | 111 | 1.745 | sim | 0 | 0 | — |
| **C** (síntese) | 75 | 83 | 1.325 | sim | 7 | 3.028 | 1–2 pessoas |
| **B2** | 63 | 70 | 1.130 | **não** | 3 | 1.079 | 2–3 pessoas |
| **B** | 47 | 52 | 860 | **não** | 7 | 3.028 | 3–4 pessoas |
| **A** | 28 | 31 | 545 | sim | 28 | 11.499 | 5 pessoas |

Todas cabem nas 100 unidades já contratadas; só o 1e pede as 11 da reserva.

## Recomendação

**Se o objetivo é cortar custo, a proposta C é o único corte que eu
defenderia** — EUR 420 abaixo do adotado, sem abrir mão da separação das três
correntes, com exposição concentrada em sete mesas identificadas e endereçáveis
com um ou dois orientadores.

**A hipótese A é coerente mas não é economia.** Somando os cinco orientadores
que ela exige, ao preço-hora do próprio orçamento, ela sai mais cara que o
desenho adotado. Só faz sentido se as pessoas já existirem — e aí a decisão é
sobre escala de pessoal, não sobre material.

**A hipótese B eu não recomendaria em nenhuma versão.** Ela economiza EUR 885
retirando barreira do único ponto do salão onde passam todos os 11.499
eleitores, no minuto mais denso do dia, para colocá-la em doze pontos que
recebem uma a duas pessoas por minuto cada. Se o corte de B for inevitável por
orçamento, a variante B2 é menos ruim — mas a proposta C custa EUR 195 a mais
que B2 e devolve a entrada.

## Premissas

As mesmas do desenho adotado, e elas mandam no resultado: fita de 2,00 m por
poste; 2,0 pessoas por metro de fila; 60 s por voto; pico de 1,8× a média sobre
a janela das 8h às 17h; comparecimento esperado de 11.499. A proporção de um
orientador para cada três mesas é estimativa de planejamento, não medição — a
90 s por voto, que é o cenário de caderno físico, ela não se sustenta e todas as
hipóteses de corte precisam ser reabertas.
