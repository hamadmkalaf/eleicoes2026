# Separadores de fila no Hall 2 — desenho definitivo

**Decidido em 17/09/2026.** A estrutura de fila é **fita no chão**; as 100
unifilas do orçamento (item d, EUR 1.303,00) vão onde a fita comprovadamente
não funciona. Este documento fixa o desenho, as cores, os rótulos e a
metragem.

Desenho: `saidas/separadores_definitivo.svg` · detalhe do ramal:
`saidas/separadores_detalhe.svg` · números: `scripts/separadores_fila.py`.
Geometria lida do cenário fechado `Paredes_ABC` — não altera nenhuma decisão de
15 e 16/09, nem a agregação de seções.

---

## 1. As três decisões de 17/09

**1. As cores são as das fitas já em estoque.** Zona A azul, zona B amarelo,
zona C laranja — as mesmas do artefato de sinalização, que já as usa nos painéis
de porta. As zonas são as áreas servidas por cada porta: A = S4 = parede oeste,
B = S5 = parede norte, C = S6 = parede leste.

| Zona | Porta | Parede | Cor | Hex |
|---|---|---|---|---|
| A | S4 | oeste | azul | `#33507E` |
| B | S5 | norte | amarelo | `#E8C63A` |
| C | S6 | leste | laranja | `#DE7343` |

> **Consequência que isso força:** amarelo virou cor de zona, então a **linha de
> espera não pode mais ser amarela** — viraria a cor da zona B no chão da zona
> A. Passa a **zebrado preto-e-branco**, que não colide com nenhuma zona e lê
> como "pare" em qualquer cultura. A rota de saída fica em branco e a
> preferencial em verde.

**2. Rótulo por grupo e por seção, nunca por número de mesa.** É a convenção que
o artefato de sinalização já fixou — *"Nenhum traz número de mesa: só as seções
do grupo"* — e ela está certa: o eleitor sabe a sua seção, não sabe que mesa é
a sua. As 28 mesas estão agrupadas em **16 grupos**: A1–A5 (5 na oeste), B1–B5
(5 na norte), C1–C6 (6 na leste). O agrupamento está versionado em
`data/grupos_mesas.json`, extraído do `sinalizacao_v2.json` e conferido contra o
artefato.

**3. As avenidas nunca se cruzam.** Não é promessa: é conferido. Cada avenida
vive numa faixa de x própria, e as três faixas são disjuntas.

```
A:  11,00 .. 25,03 m
B:  26,80 .. 29,80 m
C:  32,00 .. 36,50 m
```

`scripts/separadores_fila.py` roda essa conferência a cada execução e **sai com
código 1** se alguma avenida cruzar outra ou invadir zona protegida. Ela já
pegou um erro real: a primeira boca da avenida A ficava sobre o **recuo de
emergência S3** (x 14,22–21,47). A boca foi para a metade **leste** de S4, com o
trilho externo encostado na alvenaria de 0,29 m que separa S4 de S5.

---

## 2. Como o retorno também deixa de cruzar

A regra "avenidas não se cruzam" só vale se o fluxo de **saída** também não as
atravessar. Daí a regra que a completa:

> **As avenidas levam para dentro; as bandas trazem para fora.**

Quem votou não volta pelo campo central: sai andando pela **banda da sua própria
parede** até S2 (banda oeste) ou S8 (banda leste). Nenhum fluxo de saída
atravessa avenida nenhuma, e o campo central deixa de ser circulação — vira
reserva de fila, que é o que ele precisa ser.

Isso tem um preço, dito com todas as letras: a saída atravessa os **ramais** da
sua própria parede — 9 na oeste, 10 na leste. É um cruzamento entre um fluxo
contínuo (saída) e um intermitente (quem entra no seu ramal), dentro de uma
banda larga. É o cruzamento mais barato dos disponíveis, e é o preço de não ter
nenhum no campo central.

### A geometria

| Elemento | Medida |
|---|---|
| Banda da seção — oeste | 11,00 m da parede até o trilho da avenida |
| Banda da seção — norte | 9,00 m |
| Banda da seção — leste | 10,80 m |
| Avenidas | 3,00 m (A: 3,20 m, para encostar na alvenaria S4\|S5) |
| Ramal de mesa | canal de 1,10 m, da avenida até a linha de espera |
| Linha de espera | 1,50 m da mesa |
| Marcas de fila | tique a cada 0,65 m no canal |

**Avenida A (azul, S4 → oeste).** Sai pelos 3,20 m leste de S4, sobe 3,40 m,
vira a oeste por baixo das mesas da parede oeste e sobe rente à banda.
Distribui em **pente**: 5 aberturas, uma por grupo.

**Avenida B (amarela, S5 → norte).** Sobe reta, 35,4 m. Não distribui em pente:
chega perpendicular à banda norte e **termina em T** — todo o fluxo da entrada B
(3.832 esperados) passa por um só metro quadrado antes de se repartir. É a
fragilidade conhecida do traçado.

**Avenida C (laranja, S6 → leste).** Sai pelos 3 m oeste de S6 — a leste de
x = 35,09 está o recuo da preferencial S7 — e abre para a banda leste, 6
aberturas.

---

## 3. As 98 unifilas

| Trecho | m | unifilas |
|---|---:|---:|
| Boca da avenida A (S4) · trilho interno | 6,0 | 5 |
| Boca da avenida A (S4) · trilho externo | 6,0 | 5 |
| Boca da avenida C (S6) · trilho interno | 6,0 | 5 |
| Boca da avenida C (S6) · trilho externo | 6,0 | 5 |
| Avenida B · trilho do lado da parede | 35,4 | 21 |
| Avenida B · trilho do lado do campo | 35,4 | 21 |
| Serpenteado do grupo **A3** · seções 3313 · 3889 | 12,6 | 12 |
| Serpenteado do grupo **B2** · seções 3315 · 3778 | 12,6 | 12 |
| Serpenteado do grupo **C5** · seções 3322 · 3752 | 12,6 | 12 |
| **Total** | **133 m** | **98** |
| Reserva móvel | | **2** |

A avenida B entra **inteira** e por isso não tem item de boca separado — contar
as duas coisas seria contar os primeiros 6 m duas vezes.

**Por que aqui e não noutro lugar.** A barreira paga os três pontos onde a fita
não faz o serviço: (a) a **boca**, porque as três portas são contíguas e quem
entra pela errada não se perde — é conduzido até a parede errada; (b) a
**avenida B**, porque atravessa 35 m de piso aberto com a reserva de fila
encostada nos dois flancos; (c) as **três vermelhas**, porque são os únicos
lugares com multidão parada declarada (~20 pessoas cada, decisão de 16/09).

**A reserva de 2 é insuficiente, e isto não é detalhe.** Fita colada às 7h não
se move às 13h; a barreira é a única parte do desenho que responde a uma
surpresa. **Pedido: mais 15 unidades, EUR 195,45**, para levar a reserva a 17.
É 1,2% do orçamento do 1º turno.

Para o registro: o traçado completo — as três avenidas com os dois trilhos
inteiros, o T da parede norte, as 28 cabeças de fila, as bocas de saída e o
canal preferencial — pediria **395 unifilas em 572 m**. As 100 orçadas são
**25% disso**. Por isso a fita faz o grosso.

---

## 4. A fita: metragem e estoque

| Cor | Onde | Necessário | Em estoque | Saldo |
|---|---|---:|---:|---:|
| **Azul** | avenida A, 9 ramais oeste, marcas, galões | **244,8 m** | 165 m | **−79,8 m** |
| **Amarelo** | avenida B, distribuidor norte, 9 ramais, marcas | **149,8 m** | 165 m | +15,2 m |
| **Laranja** | avenida C, 10 ramais leste, marcas, galões | **241,2 m** | 165 m | **−76,2 m** |
| Zebrado preto-e-branco | as 28 linhas de espera | 30,8 m | — | comprar |
| Verde | canal da preferencial S7 | 20,0 m | — | comprar |
| Branco | rota de saída, setas do campo livre | 82,0 m | — | comprar |
| **Total** | | **769 m** | | |
| **Com 10% de retoque** | | **846 m** | | |

**Falta bastante fita azul e laranja.** Assumindo 165 m **por cor** em estoque
(a confirmar — se for 165 m no total, a falta triplica), faltam **80 m de azul e
76 m de laranja**, mais as três cores que ainda não existem. Em rolos de 50 m:
**2 azul + 2 laranja + 1 zebrado + 1 verde + 2 branco = 8 rolos a comprar**,
ordem de **EUR 100–160** (*estimativa minha, a cotar*).

Por que azul e laranja passam tanto do amarelo: as bandas oeste (11,00 m) e
leste (10,80 m) são bem mais fundas que a norte (9,00 m), então os 9 ramais de A
e os 10 de C são mais compridos — 6,90 e 6,70 m contra 4,90 m — e a avenida A
ainda tem a perna que vira para oeste. **A parede norte é barata em fita
justamente porque a avenida B chega perpendicular**: o T que é a fragilidade do
traçado é também o que encurta os seus ramais.

**O que a metragem não diz:** 769 m de fita colada, curva a curva, com 6 cores e
16 marcadores de grupo, é trabalho de véspera com o salão vazio — não meia hora
antes da abertura.

---

## 5. O desenho da fita, no detalhe

`saidas/separadores_detalhe.svg` mostra o trecho em escala: onde a barreira
acaba e a fita leva até a mesa.

| Elemento | Especificação |
|---|---|
| Avenida | 2 linhas contínuas a 3,00 m, galão a cada 5 m no sentido da marcha |
| Ramal | canal de 1,10 m, na cor da zona |
| Marcas de fila | tique de 0,25 m a cada **0,65 m** — 8 marcas = 8 pessoas |
| Linha de espera | faixa cheia de 1,10 m, **zebrado preto-e-branco**, a 1,50 m da mesa |
| Pegadas | duas, depois da linha: identificação e urna |
| Papel do grupo | plastificado, **fora da linha de pisada**, na borda do canal |

As marcas de 0,65 m são o passo de projeto do `plano_filas_confinado_hall2.md`.
Materializadas no chão, dão ao mesário e ao pessoal de fluxo uma leitura
instantânea do tamanho da fila sem contar cabeças.

**O papel no chão confirma, nunca decide.** Um A4 no chão some atrás do corpo de
quem está na frente. O número que decide vai à altura dos olhos, no x-banner do
grupo — já orçado no item (c), EUR 1.961,00.

---

## 6. Dois achados para a sinalização

**1. O x-banner da parede leste está fora do salão útil.** O
`sinalizacao_v2.json` põe os seis x-banners da zona C em **x = 45,70**, medido a
4,60 m dos 50,30 m da fachada. Mas a linha das mesas da parede leste é
**x = 47,30** — os 3 m entre 47,30 e 50,30 são a **faixa protegida das saídas de
emergência L1–L4**. A 45,70 o x-banner fica atrás das mesas, dentro da faixa. O
valor certo é **42,70** (47,30 − 4,60). A oeste (4,60) e a norte (39,80) estão
corretas.

**2. Nos três grupos vermelhos, 4,60 m cai dentro do serpenteado.** O
serpenteado de A3, B2 e C5 ocupa de 4,10 a 8,30 m da parede. Um x-banner a
4,60 m fica no meio dele. Nesses três, o banner recua para **8,60 m** — logo
atrás da última raia, ainda visível de toda a fila.

Os dois são correções ao plano de sinalização, não a este desenho; o desenho já
os aplica.

---

## 7. O que ficou pelo caminho

Duas alternativas foram desenhadas e descartadas. Ficam em
`saidas/separadores_opcao1.svg` e `saidas/separadores_opcao2.svg` como registro
do porquê.

**Opção 1 — As três avenidas.** Toda a barreira nos flancos das avenidas,
nenhuma nas cabeças de fila. Aposta: o eleitor mal encaminhado custa mais que o
mal enfileirado. Descartada porque deixa as três vermelhas contidas só por fita
— e fila parada é exatamente onde a fita não segura. E, com a geometria
definitiva, custa **104 unifilas**: não cabe.

**Opção 2 — As cabeças de fila.** Toda a barreira nas 19 mesas de maior carga,
boca e avenidas na fita. Aposta: pressão só existe onde a fila é estática.
Descartada porque deixa a boca — o gargalo não paralelizável, 11,5 mil pessoas
por 18,4 m de porta — separada apenas por fita, e porque deixa 9 mesas sem
canal, o que é difícil de explicar ao mesário dessas mesas. Com a geometria
definitiva custa **111 unifilas** — também não cabe.

As duas deixaram de caber quando as bandas oeste e leste se aprofundaram para
11,00 e 10,80 m. **A definitiva é a única das três que cabe nas 100**, e isso não
foi arranjado: foi consequência de pôr as avenidas em faixas disjuntas.

---

## 8. O que ainda depende de terceiros

**Bloqueante, esta semana**

1. **O RDS permite fita adesiva no piso do Hall 2?** Qual tipo, e qual a
   exigência de remoção? O manual do expositor do RDS não é público e os manuais
   de outros eventos no mesmo recinto tratam de adesivo em painéis, não em piso.
   Vários recintos proíbem ou exigem resíduo zero com remoção integral. **Se a
   resposta for não, este desenho inteiro cai.**
2. Submeter o layout de barreira ao responsável de incêndio do RDS — barreira em
   zona de egresso muda o cálculo de evacuação, e isso se submete, não se
   comunica.

**Compras**

3. As **15 unifilas adicionais** (EUR 195,45) para a reserva móvel.
4. **8 rolos de fita**: 2 azul, 2 laranja, 1 zebrado preto-e-branco, 1 verde,
   2 branco.
5. Confirmar se os 165 m em estoque são **por cor** ou no total.

**A aferir em campo, antes de imprimir**

6. As bandas de 11,00 / 9,00 / 10,80 m pressupõem o módulo de 4,10 m da planta
   medida e o serpenteado de 4,20 m de 16/09. Conferir com a mesa, a cabine e a
   urna reais.
7. A boca da avenida A deixa **36 cm** entre o trilho interno (x = 21,83) e o
   recuo de emergência S3 (até 21,47). É a folga mais apertada do traçado.
8. O **T da parede norte** é o ponto mais frágil. Se houver folga, vale estudar
   uma segunda perna para a avenida B — mas isso mexe na atribuição
   mesa → entrada, fechada desde 15/09.
9. Quem cola os 769 m de fita, e quando.

---

## 9. Como refazer

```bash
python3 scripts/separadores_fila.py           # conferência + relatório
python3 scripts/separadores_fila.py --grava   # + os 4 SVG e o JSON
```

Lê `data/prancheta_hall2.json`, `data/decisoes.json`,
`data/grupos_mesas.json` e `cenarios/paredes-abc-20260915.json`; não escreve em
nenhum deles. A conferência das avenidas sai com **código 1** se a geometria
quebrar a regra de 17/09.

**Fontes das premissas de material:**
[Queue Solutions](https://queuesolutions.com/retractable-belt-barriers/) ·
[Displays2Go](https://www.displays2go.com/C-24746/Retractable-Stanchions-Nylon-Belt-Barriers-Queue-Lines) ·
[Safety Direct2U](https://www.direct2u.co.uk/safety/standard-rectractable-belt-barrier-systems)
