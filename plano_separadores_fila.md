# As 100 unifilas — onde a barreira vale mais do que a fita

Desenho aprovado pela chefia: **fita no chão** como estrutura de fila, com o
papel de sinalização das seções colado junto. As 100 unifilas do orçamento
(item d, EUR 1.303,00) deixam de ser "a fila" e passam a ser um recurso escasso
a alocar.

Números de `scripts/separadores_fila.py`; desenhos em `saidas/separadores_opcao{1,2,3}.svg`
e `saidas/separadores_detalhe.svg`. Geometria lida do cenário fechado
`Paredes_ABC` — não altera nenhuma decisão de 15 e 16/09.

---

## 1. Resposta direta

| | Opção 1 · As três avenidas | Opção 2 · As cabeças de fila | **Opção 3 · Boca, avenida do meio e vermelhas** |
|---|---|---|---|
| **A barreira paga** | o trajeto | a contenção | o cruzamento |
| Unifilas | **102 — não cabe** | 100 | **97** |
| Metros de cinta | 168 | 116 | 135 |
| Reserva móvel | −2 | 0 | **3** |
| **Fita no chão** | 624 m | 676 m | 657 m |
| Fita com retoque | 686 m | 743 m | 723 m |
| Rolos de 50 m | 16 | 18 | 18 |
| As três vermelhas | na fita | na barreira | na barreira |
| A boca das três portas | divisores | na fita | divisores |
| O T da parede norte | na barreira | na fita | na barreira |

**Recomendo a Opção 3**, com um pedido anexo: **comprar mais 15 unidades
(EUR 195,45)** para levar a reserva móvel de 3 a 18. É 1,2% do orçamento do
1º turno e é a única parte do desenho que pode ser movida às 13h. Fita colada
às 7h não se move.

---

## 2. A aritmética que muda a conversa

**Duas correções ao que o orçamento sugere.**

A primeira: uma unifila de 2,00 m só fica com a cinta esticada se os postes
ficarem a cerca de **1,80 m** — 90% do comprimento da cinta é a regra corrente
dos fabricantes ([Queue Solutions](https://queuesolutions.com/retractable-belt-barriers/),
[Displays2Go](https://www.displays2go.com/C-24746/Retractable-Stanchions-Nylon-Belt-Barriers-Queue-Lines)).
E cada trecho independente custa um poste a mais, o terminal. Os "200 metros"
do orçamento são comprimento nominal de cinta: esticados e repartidos em
trechos, as 100 unidades rendem perto de **170 m de linha útil**.

A segunda, e a que importa: o traçado completo deste salão — três avenidas com
os dois trilhos, os divisores de boca, o T da parede norte, os três
serpenteados, as 28 cabeças de fila, as bocas de saída e o canal preferencial —
pede **358 unifilas em 516 m de trilho**. As 100 orçadas são **28% do desejado**.

Isto não é uma falha do orçamento: é a consequência aritmética da decisão de
15/09 de trazer a fila inteira para dentro do Hall 2. O
`plano_filas_confinado_hall2.md` já tinha chegado a 433 unidades pela
serpentina norte-sul; com o desenho por paredes e a fita fazendo o grosso, o
número cai para 358 — mas continua três vezes e meia o orçado.

**A conclusão prática:** a pergunta deixa de ser "como montar a fila com
unifila" e passa a ser "**que 28% do desenho não pode ser fita**". É isso que
as três opções respondem, cada uma com uma teoria diferente do que dá errado.

---

## 3. O traçado comum às três opções

As três opções desenham o mesmo caminho. Só muda o que nele é barreira.

**Banda da seção — 9,00 m.** Cada parede usada reserva 9,00 m: os 4,10 m do
módulo, os 4,20 m do serpenteado já decidido em 16/09 e 0,70 m de folga. É a
faixa em que o eleitor pára.

**Avenidas — 3,00 m, uma por entrada.** Cada porta tem a sua e não cruza as
outras, porque a geometria coopera: S4 é a porta mais a oeste e serve a parede
oeste, S6 a mais a leste e serve a leste, S5 a do meio e serve o norte.

- **Avenida A (azul, S4 → parede oeste).** Sai da porta, corre para oeste numa
  perna ao sul das mesas e ao norte do recuo de emergência S3, dá uma
  cotovelada em y = 7,40 para desviar do recuo R1 e sobe rente à banda oeste.
  Distribui em **pente**: nove aberturas, uma por mesa.
- **Avenida B (âmbar, S5 → parede norte).** Sobe reta, 35,4 m. Não distribui em
  pente: chega perpendicular à banda norte e **termina em T**.
- **Avenida C (magenta, S6 → parede leste).** Sai pela metade oeste da porta — a
  leste de x = 35,09 está o recuo da preferencial S7 — e abre para a banda
  leste, também em pente, dez aberturas.

**Ramal de mesa — canal de 1,10 m.** Da avenida até 1,50 m da mesa. Cabem ~5
pessoas no canal; o excedente recua para o campo central, que está vazio.

**Linha de espera — 1,50 m da mesa.** Faixa contínua, cor distinta de tudo o
mais. É a linha do sigilo do voto: só passa quem o mesário chamar. É o único
elemento do desenho com função procedimental, não de fluxo.

**Saída — campo livre.** Quem já votou está disperso e sem pressa. Canalizar a
saída dobraria a fita e criaria 28 cruzamentos com os ramais. Sai por S2 e S8
com sinalização, sem canal.

### Três pontos onde dois fluxos têm de se cruzar

O traçado tem exatamente três cruzamentos inevitáveis. São eles que decidem a
alocação das unifilas:

1. **A boca das três portas.** S4, S5 e S6 são contíguas — 0,29 m de alvenaria
   entre uma e outra, 18,4 m de porta no total. Quem entra pela porta errada não
   se perde: é **conduzido até a parede errada**, e volta atravessando o salão
   contra o fluxo.
2. **O T da parede norte.** Todo o fluxo da entrada B — 3.832 esperados — passa
   por um só metro quadrado antes de se repartir para os dois lados. É o único
   ponto do salão com essa propriedade. A avenida B é também a única com campo
   de retorno dos **dois** lados.
3. **A boca da saída S2.** S2 tem 1,20 m e está espremida entre a porta de carga
   S1 e o recuo de emergência S3. A perna oeste da avenida A passa logo acima
   dela.

---

## 4. As três opções

### Opção 1 — As três avenidas *(canalizar o trajeto)*

`saidas/separadores_opcao1.svg` · 102 unifilas, 168 m

Barreira nos divisores de boca e no flanco de cada avenida que dá para o campo
de retorno: A do lado leste, B dos dois lados, C do lado oeste. As cabeças de
fila e os três serpenteados ficam na fita.

**A aposta:** um eleitor mal encaminhado custa mais do que um eleitor mal
enfileirado. Quem chega à parede errada volta atravessando o salão, contra o
fluxo, e leva junto quem o seguiu.

**O risco:** nada segura as três vermelhas. Os ~20 em pé à frente de cada uma
— o serpenteado decidido em 16/09 — ficam contidos só por fita, e fila estática
é justamente onde a fita não segura.

**E não cabe.** Faltam 2 unidades. Cabe encurtando 4 m do trilho da avenida C,
o que é aceitável, mas a opção nasce sem reserva nenhuma.

### Opção 2 — As cabeças de fila *(conter onde se pára)*

`saidas/separadores_opcao2.svg` · 100 unifilas, 116 m

Barreira nos três serpenteados vermelhos, nas 8 mesas amarelas e nas 8 verdes
de maior carga — 19 das 28 mesas com canal físico. Boca e avenidas inteiramente
na fita.

**A aposta:** pressão de multidão só existe onde a fila é estática. Corredor é
fluxo andando, e fluxo andando obedece a linha pintada. Esta opção também é a
que mais protege o sigilo do voto e a mesa dos mesários.

**O risco:** a boca é o gargalo não paralelizável já identificado no
`contexto_eleicoes_dublin_2026.md` §4 — 11,5 mil pessoas por 18,4 m de porta,
com as três correntes separadas apenas por fita. E deixa 9 mesas de fora, o que
é difícil de explicar a um mesário cuja mesa ficou sem canal.

### Opção 3 — Boca, avenida do meio e vermelhas — **recomendada**

`saidas/separadores_opcao3.svg` · 97 unifilas, 135 m, 3 de reserva

| Trecho | Unifilas |
|---|---:|
| Divisor das bocas A\|B — prolonga a alvenaria 6 m para dentro | 5 |
| Divisor das bocas B\|C — idem | 5 |
| Trilho sul da perna A — separa a entrada da saída S2 e do recuo S3 | 9 |
| Avenida B, os dois trilhos, 35,4 m cada | 42 |
| Serpenteado da mesa 5 (MRV 22, 590 esperados) | 12 |
| Serpenteado da mesa 12 (MRV 23, 586) | 12 |
| Serpenteado da mesa 21 (MRV 24, 588) | 12 |
| **Total** | **97** |

**A aposta:** fita é uma fronteira que se vê; barreira é uma fronteira que
custa atravessar. Gasta-se barreira onde atravessar compensa — nos três
cruzamentos da §3 e nas três filas que ficam paradas. Tudo o mais é fluxo
andando, e a fita governa fluxo andando.

**O risco:** as avenidas A e C ficam na fita. Se o corte de caminho aparecer
nelas, é a reserva móvel que responde — e com 3 unidades ela mal existe. Daí o
pedido das 15 adicionais.

---

## 5. O desenho da fita

`saidas/separadores_detalhe.svg` mostra o trecho crítico em escala: onde a
barreira acaba e a fita leva até a mesa. Vale igual nas três paredes.

**Cor por entrada, a mesma em tudo.** Azul para A/oeste, âmbar para B/norte,
magenta para C/leste — os hexadecimais já fixados em `data/decisoes.json`. A
fita do chão, o banner da porta, a seta e o papel da mesa usam a mesma cor. O
eleitor recebe uma instrução só: *siga a linha azul*.

**Geometria.**

| Elemento | Especificação |
|---|---|
| Avenida | 2 linhas contínuas a 3,00 m, galão a cada 5 m no sentido da marcha |
| Ramal | canal de 1,10 m, da avenida até a linha de espera |
| Marcas de fila | tique de 0,25 m a cada **0,65 m** no canal |
| Linha de espera | faixa cheia, 1,10 m, a 1,50 m da mesa, amarelo/preto |
| Pegadas | duas, depois da linha: posição de identificação e posição da urna |
| Saída | cor que **não** é de nenhuma entrada; nunca reutilizar azul/âmbar/magenta |

São seis cores de rolo ao todo: as três das entradas, mais amarelo-preto para a
linha de espera, verde para a preferencial e branco-preto para saída e
divisores.

As marcas de 0,65 m não são enfeite: 0,65 m é o passo de projeto do
`plano_filas_confinado_hall2.md`. Materializadas no chão, dão ao mesário e ao
pessoal de fluxo uma leitura instantânea do tamanho da fila — *12 marcas
ocupadas são 12 pessoas* — sem contar cabeças.

### Metragem de fita, opção a opção

Fita é o **complemento** da barreira: todo trecho do traçado existe no chão de
um jeito ou de outro, e o que a unifila não cobre, a fita cobre. Somam-se os
elementos que são sempre fita — o lado livre de cada ramal, a linha de espera,
as marcas de 0,65 m, os galões das avenidas e a sinalização de saída — e
acrescenta-se 10% para o retoque do meio-dia e as perdas de corte.

| Cor do rolo | Onde | Opção 1 | Opção 2 | **Opção 3** |
|---|---|---:|---:|---:|
| Azul | avenida A, 9 ramais oeste, marcas, galões | 169,1 m | 170,0 m | **199,4 m** |
| Âmbar | avenida B, distribuidor norte, 9 ramais, marcas | 150,4 m | 184,2 m | **137,8 m** |
| Magenta | avenida C, 10 ramais leste, marcas, galões | 171,8 m | 176,6 m | **201,1 m** |
| Amarelo-preto | as 28 linhas de espera | 30,8 m | 30,8 m | **30,8 m** |
| Verde | canal da preferencial S7 | 20,0 m | 20,0 m | **20,0 m** |
| Branco-preto | bocas de saída, divisores, setas do campo livre | 82,0 m | 94,0 m | **68,0 m** |
| **Total** | | **624,1 m** | **675,6 m** | **657,1 m** |
| **Com 10% de retoque** | | **686,5 m** | **743,2 m** | **722,8 m** |

**Em rolos de 50 m** (é assim que se compra, e sobra é melhor do que falta):

| | Azul | Âmbar | Magenta | Amarelo-preto | Verde | Branco-preto | **Total** |
|---|---:|---:|---:|---:|---:|---:|---:|
| Opção 1 | 4 | 4 | 4 | 1 | 1 | 2 | **16** |
| Opção 2 | 4 | 5 | 4 | 1 | 1 | 3 | **18** |
| **Opção 3** | **5** | **4** | **5** | **1** | **1** | **2** | **18** |

**A leitura que importa: a escolha da opção quase não mexe na conta da fita.**
Os três desenhos ficam entre 624 e 676 m — 8% de diferença, dois rolos. O que
muda é **qual cor** se compra mais: a Opção 3, por deixar as avenidas A e C
inteiramente na fita, precisa de 5 rolos de azul e 5 de magenta contra 4 e 4
das outras. Ou seja: **a decisão entre as três opções é uma decisão sobre as
unifilas, não sobre a fita.** Para o orçamento, pode-se comprar o pacote maior
(18 rolos, com 5 de azul e 5 de magenta) e ficar coberto em qualquer das três
— a diferença entre o pacote mínimo e o máximo são dois rolos.

**Custo.** Não cotei fita de marcação de piso; 18 rolos de 50 mm × 50 m são
ordem de **EUR 220–360** (**estimativa minha, a cotar** — e a cotação tem de
especificar resíduo zero, ver §6). É ruído no orçamento de EUR 15.703,32 e não
é por aí que a decisão passa.

**O que a metragem não diz:** fita se aplica no chão, curva a curva, com o
salão vazio. 657 m de fita colada, mais 28 papéis e 18 rolos trocados de cor,
é trabalho de equipe na véspera, não de meia hora antes da abertura. Vale
dimensionar isso junto com o único segurança já contratado para o dia anterior
(item a do orçamento).

---

## 6. Onde eu discordo do desenho aprovado

Duas objeções concretas, uma bloqueante.

**O papel colado no chão não é lido — é pisado.** Um A4 no chão é legível a
2–3 m e some atrás do corpo de quem está na frente. Depois de 11,5 mil pares de
pés em nove horas, papel sob fita transparente vira farrapo antes do
meio-dia. Duas correções que não custam nada:

1. O papel é **plastificado ou vinil adesivo**, e vai **fora da linha de
   pisada** — na borda do canal, junto ao poste, não no eixo.
2. O número que **decide** vai à altura dos olhos, no banner — e banner já está
   orçado (item c, EUR 1.961,00). O chão diz *por onde andar*; o banner diz
   *para onde ir*. Papel no chão serve para confirmar, nunca para decidir.

**Ninguém confirmou que o RDS permite fita no piso do Hall 2.** Procurei: o
manual do expositor do RDS não é público e os manuais de outros eventos no
mesmo recinto tratam de adesivo em painéis, não em piso. Vários recintos
proíbem adesivo no piso ou exigem fita de resíduo zero com remoção integral
antes da devolução. **Se a resposta for não, o desenho aprovado morre inteiro**
— e as 100 unifilas passariam a ter de fazer sozinhas um trabalho de 358.
Isto é pergunta para esta semana, não para setembro, e vai junto com a outra
que já está em aberto: barreira em zona de egresso muda o cálculo de evacuação
e o layout **tem de ser submetido** ao responsável de incêndio do RDS, não
apenas comunicado (`plano_filas_confinado_hall2.md` §7).

---

## 7. Efeitos de segunda e terceira ordem

**Segunda ordem — a fita não é vencida, é desacreditada.** Uma linha colada é
permeável por definição. O problema não é o primeiro eleitor que corta caminho:
é que ele economiza 30 segundos **à vista de todos**, e um corte impune
normaliza o corte. A fila deixa de existir por consenso, não por pressão. Isto
tem duas consequências de desenho: (a) a barreira rende mais perto da **cabeça**
da fila, onde cortar compensa mais, do que no meio do corredor; (b) onde só há
fita, o que a sustenta é **presença humana**, não a fita — o que amarra este
plano ao dimensionamento de pessoal de fluxo, e não só ao de segurança.

**Segunda ordem — a cor só funciona se for aprendida antes de chegar.** Se o
eleitor descobre no portão que é "azul, mesa 12", a triagem vira leitura de
título na porta, e a porta é o gargalo não paralelizável. A tabela
seção → cor → mesa tem de sair **antes** no Instagram, na página da Embaixada e
na divulgação alternativa, e estar repetida na aproximação externa. Isto
converte um item do plano de comunicação (PENDÊNCIAS §3) em **dependência do
plano físico**: sem ele, o desenho de fluxo perde o seu pressuposto.

**Terceira ordem — fita colada às 7h não se move às 13h.** Tudo o que for fita
é irreversível no dia. Uma operação sem nenhuma peça móvel perde a capacidade
de responder ao que não foi previsto — e o que não foi previsto, neste projeto,
tem nome: MRV 24 e MRV 11 ainda sem mesário confirmado, as taxas de 2022 sem
fonte primária, a profundidade da sala de apoio por medir. **Uma reserva de 15 a
18 postes vale mais do que 30 m de trilho a mais**, porque é a única parte do
desenho que responde a uma surpresa. É por isso que ela é o pedido anexo à
Opção 3, e não um arredondamento.

**Terceira ordem — fila desordenada gera reclamação formal, fila longa não.**
Um eleitor que espera 40 minutos numa fila visivelmente ordenada reclama do
TSE; o que espera 20 numa fila em que viu alguém furar reclama do Posto. A
ordem visível é um ativo reputacional, e é exatamente o que se perde primeiro
quando a fita cede. O `plano_filas_confinado_hall2.md` §5 já dizia isso do modo
curral: *perde-se a ordem de chegada*. Vale igual, em grau menor, para cada
metro de fita sem barreira.

---

## 8. O que decidir, e o que aferir em campo

**Decisões que dependem da chefia**

1. Qual das três opções — recomendo a 3.
2. As 15 unifilas adicionais (EUR 195,45) para a reserva móvel.
3. Comprar o pacote de fita maior — 18 rolos de 50 m em 6 cores, 5 de azul e 5
   de magenta — que cobre qualquer das três opções. A diferença entre o pacote
   mínimo e o máximo são dois rolos, e assim a compra da fita não fica travada
   pela decisão da opção.
4. Papel plastificado fora da linha de pisada, com o número de decisão no
   banner e não no chão.
5. Quem cola os 657 m de fita, e quando. É trabalho de véspera com o salão
   vazio, não de meia hora antes da abertura.

**Perguntas ao RDS, esta semana**

6. Fita adesiva no piso do Hall 2 é permitida? Qual tipo, e qual a exigência de
   remoção? (**bloqueante**)
7. Submissão do layout de barreira ao responsável de incêndio.

**A aferir em campo, antes de imprimir**

8. A banda de 9,00 m pressupõe o módulo de 4,10 m da planta medida e o
   serpenteado de 4,20 m de 16/09. Confirmar com a mesa, a cabine e a urna reais.
9. A perna oeste da avenida A passa entre o recuo R1 (até y = 7,00) e as mesas
   da parede oeste (a partir de y = 7,45): sobram 45 cm de margem. Medir.
10. A avenida C sai pela metade oeste de S6 porque o recuo de S7 começa em
   x = 35,09. Se o recuo de S7 for menor do que o desenhado, a avenida C ganha
   1,5 m de largura de boca.
11. O T da parede norte é o ponto mais frágil do traçado. Se houver folga de
   espaço, vale estudar uma segunda perna para a avenida B — mas isso mexe na
   atribuição mesa → entrada, que está fechada desde 15/09.

---

## 9. Como refazer as contas

```bash
python3 scripts/separadores_fila.py           # relatório, sem gravar
python3 scripts/separadores_fila.py --grava   # + os 4 SVG e o JSON
```

O script lê `data/prancheta_hall2.json`, `data/decisoes.json` e
`cenarios/paredes-abc-20260915.json`, e não escreve em nenhum dos três. Mudar
`VAO_POSTE`, `BANDA`, `LARG_CANAL` ou `PASSO_FILA` no topo do arquivo refaz o
orçamento e os desenhos juntos.

**Fontes das premissas de material:**
[Queue Solutions — retractable belt barriers](https://queuesolutions.com/retractable-belt-barriers/) ·
[Displays2Go — retractable stanchions](https://www.displays2go.com/C-24746/Retractable-Stanchions-Nylon-Belt-Barriers-Queue-Lines) ·
[Safety Direct2U — cinta de 2 m](https://www.direct2u.co.uk/safety/standard-rectractable-belt-barrier-systems)
