# Contexto — Separadores de fila e fita no chão no Hall 2

> **Tema:** como as 100 unifilas (Tensa de 2 m) e a fita adesiva de piso repartem
> entre si o trabalho de conduzir 11,5 mil eleitores da porta até a mesa
> receptora, no RDS Ballsbridge Hall 2, no 1º turno de 04/10/2026.
>
> Documento gerado ao fim da conversa de 17–18/09/2026, para ser lido por quem
> pegar este tema noutro repositório, sem o histórico. Acompanha o
> `TRANSFERENCIA_SEPARADORES_FILA.md`, que diz o que levar e como provar que
> chegou inteiro.

---

## 1. O problema, em um parágrafo

O Posto tem **100 unifilas** no orçamento (item d, EUR 1.303,00) e um salão em
que **toda a fila tem de caber dentro** — o RDS proibiu fila no seu terreno e o
Ring 3 foi abandonado em 15/09. A chefia aprovou **fita adesiva no chão** como
estrutura de fila, com o papel de sinalização das seções colado junto. A
pergunta que esta conversa respondeu não foi "como montar a fila com unifila",
e sim **que parte do desenho não pode ser fita** — porque o traçado completo do
Hall 2 pediria 395 unifilas, e as orçadas são 25% disso.

## 2. O que este tema herda, e não discute

Nada aqui mexe no que já estava fechado. O desenho lê estas decisões e as
respeita:

| Decisão | Quando | Onde vive |
|---|---|---|
| 28 mesas receptoras, agregação principal → agregada do Cartório | — | `data/decisoes.json` |
| Cenário `Paredes_ABC`: 9 mesas na oeste, 9 na norte, 10 na leste | 15/09 | `cenarios/paredes-abc-20260915.json` |
| Uma entrada por parede: A→oeste (S4), B→norte (S5), C→leste (S6) | 15/09 | `decisoes.entradas` |
| Portas: S4/S5/S6 entradas, S2/S8 saídas, S7 preferencial | 16/09 | `decisoes.sinalizacao_portas` |
| Zonas protegidas: recuos de S3, S7, R1, N2, O2 e faixa de emergência leste | 16/09 | `decisoes.zonas_protegidas` |
| Serpenteado de ~20 pessoas à frente de cada mesa vermelha | 16/09 | `decisoes.serpenteados` |
| Módulo de 4,10 m de profundidade, 0,90 m de largura | — | `data/prancheta_hall2.json` |
| 16 grupos de mesas (A1–A5, B1–B5, C1–C6) e as suas seções | — | `data/grupos_mesas.json` |

As três mesas de alto comparecimento — as "vermelhas" — são os grupos **A3**
(seções 3313 · 3889), **B2** (3315 · 3778) e **C5** (3322 · 3752), com 586 a 590
comparecentes esperados cada.

## 3. As premissas de material

**A unifila rende menos do que o orçamento sugere.** Uma cinta de 2,00 m só fica
esticada com os postes a cerca de **1,80 m** — 90% do comprimento da cinta é a
regra corrente dos fabricantes. E **cada trecho independente custa um poste a
mais**, o terminal. Um trecho contínuo de L metros custa `ceil(L / 1,80) + 1`
postes. Os "200 metros" do orçamento são comprimento nominal de cinta:
esticados e repartidos em trechos, as 100 unidades rendem perto de **170 m de
linha útil**.

**A fita se compra por cor, em rolo.** A conta útil não é "metros de fita", é
"metros de cada cor" — é isso que quem compra precisa. Rolo de referência: 50 m.
Margem de 10% para o retoque do meio-dia e perdas de corte.

**As fitas em estoque** (foto de 17/09): azul, amarelo e laranja, **165 m** —
está por confirmar se são 165 m por cor ou no total.

## 4. O traçado

**Banda da seção.** Cada parede usada reserva uma faixa que contém o módulo
(4,10 m), o serpenteado (4,20 m) e a circulação de saída: **11,00 m na oeste,
9,00 m na norte, 10,80 m na leste**. A banda vai da parede até o trilho mais
próximo da avenida daquela parede.

**Avenidas.** Uma por entrada, 3,00 m de largura (a A tem 3,20 m, para o trilho
externo encostar na alvenaria de 0,29 m entre S4 e S5).

- **A (azul, S4 → oeste).** Sai pelos 3,20 m **leste** de S4 — a metade oeste da
  porta está sobre o recuo de emergência S3, que vai até x = 21,47 —, sobe
  3,40 m, vira a oeste por baixo das mesas da parede oeste e sobe rente à banda.
  Distribui em **pente**, 5 aberturas.
- **B (amarela, S5 → norte).** Sobe reta, 35,4 m, e **termina em T**: todo o
  fluxo da entrada B (3.832 esperados) passa por um só metro quadrado antes de
  se repartir. É a fragilidade conhecida do traçado.
- **C (laranja, S6 → leste).** Sai pelos 3 m **oeste** de S6 — a leste de
  x = 35,09 está o recuo da preferencial S7 — e abre para a banda leste, 6
  aberturas.

**Ramal de mesa.** Canal de 1,10 m da avenida até 1,50 m da mesa: 6,90 m na
oeste, 4,90 m na norte, 6,70 m na leste. Marcas de 0,65 m no chão — o passo de
projeto do plano de filas —, que dão ao mesário a leitura do tamanho da fila sem
contar cabeças.

**Linha de espera.** Faixa cheia de 1,10 m a 1,50 m da mesa. É a linha do sigilo
do voto: só passa quem o mesário chamar. É o único elemento do desenho com
função procedimental, não de fluxo.

**Saída.** Campo livre, sem canal. Quem já votou está disperso e sem pressa;
canalizar a saída dobraria a fita e criaria 28 cruzamentos com os ramais.

## 5. As decisões desta conversa

### 17/09 — as três que o Posto fixou

**1. As cores são as das fitas em estoque.** A azul `#33507E`, B amarelo
`#E8C63A`, C laranja `#DE7343` — as mesmas do artefato de sinalização
(`Ek3FfeYnwvQLZEs4ZJ5Zzr`), que já as usa nos painéis de porta. *Consequência
que isso força:* amarelo virou cor de zona, então a **linha de espera não pode
mais ser amarela** — passa a **zebrado preto-e-branco**. Saída em branco,
preferencial em verde. São **seis cores de rolo** ao todo.

**2. Rótulo por grupo de mesas e por seção, nunca por número de mesa.** É a
convenção que o artefato já fixou — *"Nenhum traz número de mesa: só as seções
do grupo"* — e ela está certa: o eleitor sabe a sua seção, não sabe que mesa é a
sua.

**3. As avenidas nunca se cruzam.** Cada uma vive numa faixa de x própria, e as
três faixas são disjuntas: A 11,00–25,03, B 26,80–29,80, C 32,00–36,50.

### A regra que completa a terceira

A regra "avenidas não se cruzam" só vale se o fluxo de **saída** também não as
atravessar. Daí:

> **As avenidas levam para dentro; as bandas trazem para fora.**

Quem votou sai andando pela banda da sua própria parede até S2 (banda oeste) ou
S8 (banda leste). Nenhum fluxo de saída atravessa avenida nenhuma, e o campo
central deixa de ser circulação — vira reserva de fila, que é o que ele precisa
ser. O preço, dito com todas as letras: a saída atravessa os **ramais** da sua
própria parede. É um cruzamento entre um fluxo contínuo e um intermitente, numa
banda larga — o mais barato dos disponíveis.

### A alocação definitiva

| Trecho | m | unifilas |
|---|---:|---:|
| Boca da avenida A (S4), dois trilhos, 6 m cada | 12,0 | 10 |
| Boca da avenida C (S6), dois trilhos, 6 m cada | 12,0 | 10 |
| Avenida B, os dois trilhos inteiros | 70,8 | 42 |
| Serpenteados dos grupos A3, B2 e C5 | 37,8 | 36 |
| **Total** | **133 m** | **98** |
| Reserva móvel | | **2** |

A avenida B entra inteira e por isso não tem item de boca separado — contar as
duas coisas seria contar os primeiros 6 m duas vezes.

**Por que aqui.** A barreira paga os três pontos onde a fita não faz o serviço:
(a) a **boca**, porque as três portas são contíguas — 0,29 m de alvenaria entre
elas, 18,4 m de porta no total — e quem entra pela errada não se perde, é
*conduzido até a parede errada*; (b) a **avenida B**, porque atravessa 35 m de
piso aberto com a reserva de fila encostada nos dois flancos; (c) as **três
vermelhas**, os únicos lugares com multidão parada declarada.

### A fita, por cor

| Cor | Necessário | Em estoque | Saldo |
|---|---:|---:|---:|
| Azul (zona A) | 244,8 m | 165 m | **−79,8 m** |
| Amarelo (zona B) | 149,8 m | 165 m | +15,2 m |
| Laranja (zona C) | 241,2 m | 165 m | **−76,2 m** |
| Zebrado preto-e-branco (linha de espera) | 30,8 m | — | comprar |
| Verde (preferencial S7) | 20,0 m | — | comprar |
| Branco (rota de saída) | 82,0 m | — | comprar |
| **Total** | **769 m** | | |
| **Com 10% de retoque** | **846 m** | | |

**Faltam 8 rolos de 50 m**: 2 azul, 2 laranja, 1 zebrado, 1 verde, 2 branco.
Ordem de EUR 100–160 (*estimativa, a cotar*).

Azul e laranja passam tanto do amarelo porque as bandas oeste e leste são bem
mais fundas que a norte, então os seus ramais são mais compridos. **A parede
norte é barata em fita justamente porque a avenida B chega perpendicular:** o T
que é a fragilidade do traçado é também o que encurta os seus ramais.

## 6. Achados

**1. A conferência pegou um erro real.** A primeira versão da boca da avenida A
ficava sobre o **recuo de emergência S3** (x 14,22–21,47). Só apareceu porque a
regra das avenidas foi escrita como conferência executável, e não como
afirmação no texto. A boca foi para a metade leste de S4.

**2. O x-banner da parede leste está fora do salão útil.** O
`sinalizacao_v2.json` põe os seis x-banners da zona C em **x = 45,70**, medido a
4,60 m dos 50,30 m da fachada. Mas a linha das mesas da parede leste é
**x = 47,30** — os 3 m entre 47,30 e 50,30 são a faixa protegida das saídas de
emergência L1–L4. A 45,70 o x-banner fica atrás das mesas, dentro da faixa. O
valor certo é **42,70**. A oeste (4,60) e a norte (39,80) estão corretas.

**3. Nos três grupos vermelhos, 4,60 m cai dentro do serpenteado.** O
serpenteado de A3, B2 e C5 ocupa de 4,10 a 8,30 m da parede; um x-banner a
4,60 m fica no meio dele. Nesses três o banner recua para **8,60 m** — logo
atrás da última raia, ainda visível de toda a fila.

Os achados 2 e 3 são correções ao **plano de sinalização**, não a este desenho;
o desenho já os aplica.

## 7. Onde eu discordo do desenho aprovado

**O papel colado no chão não é lido — é pisado.** Um A4 no chão some atrás do
corpo de quem está na frente, e depois de 11,5 mil pares de pés em nove horas
vira farrapo antes do meio-dia. Duas correções que não custam nada: papel
**plastificado**, colado **fora da linha de pisada**; e o número que *decide* à
altura dos olhos, no x-banner — já orçado no item (c), EUR 1.961,00. O chão diz
*por onde andar*; o banner diz *para onde ir*.

**A reserva de 2 unifilas é insuficiente.** Fita colada às 7h não se move às
13h. A barreira é a única parte do desenho que responde a uma surpresa — e as
surpresas deste projeto têm nome: MRV 24 e MRV 11 ainda sem mesário confirmado.
**Pedido: mais 15 unidades, EUR 195,45**, para levar a reserva a 17. É 1,2% do
orçamento do 1º turno.

## 8. Efeitos de segunda e terceira ordem

**A fita não é vencida, é desacreditada.** Uma linha colada é permeável por
definição. O problema não é o primeiro eleitor que corta caminho: é que ele
economiza 30 segundos **à vista de todos**, e um corte impune normaliza o corte.
Duas consequências de desenho: a barreira rende mais perto da **cabeça** da
fila, onde cortar compensa mais; e onde só há fita, o que a sustenta é
**presença humana** — o que amarra este plano ao dimensionamento de pessoal de
fluxo, não só ao de segurança.

**A cor só funciona se for aprendida antes de chegar.** Se o eleitor descobre no
portão que é "azul", a triagem vira leitura de título na porta — e a porta é o
gargalo não paralelizável. A tabela seção → cor → grupo tem de sair **antes** no
Instagram, na página da Embaixada e na divulgação alternativa. Isto converte um
item do plano de comunicação em **dependência do plano físico**.

**Fila desordenada gera reclamação formal; fila longa, não.** Quem espera 40
minutos numa fila visivelmente ordenada reclama do TSE; quem espera 20 numa fila
em que viu alguém furar reclama do Posto. A ordem visível é ativo reputacional,
e é o que se perde primeiro quando a fita cede.

## 9. O que não está resolvido

**Bloqueante.** Ninguém confirmou que o **RDS permite fita adesiva no piso do
Hall 2**. O manual do expositor do RDS não é público, e os manuais de outros
eventos no mesmo recinto tratam de adesivo em painéis, não em piso. Vários
recintos proíbem ou exigem resíduo zero com remoção integral. **Se a resposta
for não, este desenho inteiro cai** — e as 100 unifilas passariam a ter de fazer
sozinhas um trabalho de 395.

**Também em aberto:**

1. Submeter o layout de barreira ao responsável de incêndio do RDS — barreira em
   zona de egresso muda o cálculo de evacuação, e isso se submete, não se
   comunica.
2. As 15 unifilas adicionais e os 8 rolos de fita.
3. Se os 165 m em estoque são por cor ou no total.
4. As bandas de 11,00 / 9,00 / 10,80 m pressupõem o módulo de 4,10 m da planta
   medida e o serpenteado de 4,20 m. Conferir com a mesa, a cabine e a urna
   reais.
5. A boca da avenida A deixa **36 cm** entre o trilho interno (x = 21,83) e o
   recuo S3 (até 21,47). É a folga mais apertada do traçado.
6. O **T da parede norte**. Se houver folga, vale estudar uma segunda perna para
   a avenida B — mas isso mexe na atribuição mesa → entrada, fechada desde
   15/09.
7. Quem cola os 769 m de fita, e quando. É trabalho de véspera com o salão
   vazio.

## 10. Fontes

Premissas de material:
[Queue Solutions](https://queuesolutions.com/retractable-belt-barriers/) ·
[Displays2Go](https://www.displays2go.com/C-24746/Retractable-Stanchions-Nylon-Belt-Barriers-Queue-Lines) ·
[Safety Direct2U](https://www.direct2u.co.uk/safety/standard-rectractable-belt-barrier-systems)

Documentos do projeto de que este tema depende: `plano_filas_confinado_hall2.md`
(passo de fila de 0,65 m, teto de densidade, o achado de que 28 urnas só cabem a
60 s por eleitor), `CONFERENCIA_PRANCHETA_2026-09-15.md` (o porquê de cada
decisão de arranjo) e o artefato de sinalização
[`Ek3FfeYnwvQLZEs4ZJ5Zzr`](https://claude.ai/artifact/Ek3FfeYnwvQLZEs4ZJ5Zzr)
(cores, grupos e peças).
