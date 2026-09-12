# Fitas no piso em vez do checkpoint

Documento de discussão. Examina a sugestão de um colega: **tirar o checkpoint
do salão e guiar o eleitor da porta direto à sua mesa por fitas no piso, com
sinalização**, em contraste com o plano vigente, em que cada entrada tem um
corredor de unifila até um ponto de triagem onde a equipe despacha o eleitor à
mesa.

Tudo aqui foi medido no material do próprio projeto: a planta-base
(`scripts/salao.py`), o arranjo **Três polos** da prancheta (o do Cenário
Claude), as decisões de 06/09 (`scripts/decisoes.py`: entradas S4/S5/S6,
saídas S2/S8, mesas atribuídas às entradas por quota do Ring 3, base B) e o
motor do simulador (`simulador/modelo.js`), que já sabe simular "sem
checkpoint". A varredura está em `simulador/fitas.js`; o desenho e a página em
`scripts/fitas_piso.py`; os números em `saidas/fitas_piso.{json,md,html}`.

> Nota sobre o esboço `PLANO COM FLUXOS MELHORADO.png` (28/08): ali havia duas
> portas e um hub no **meio** do salão. O plano vigente já não é esse: são três
> entradas, um checkpoint a **16 m** da porta (não no centro) e a consulta
> "qual é a minha mesa" acontece **fora**, no percurso do portão ao Hall 2
> (plano de sinalização, PR #8). Este documento compara a sugestão com o plano
> vigente, não com o esboço.

## 1. O que o checkpoint faz, de fato

No plano vigente o checkpoint tem dois papéis:

1. **Informar**: confirmar a mesa e apontar o caminho. Como a consulta já é
   feita no Ring 3 e no percurso externo, dentro do salão esse papel é de
   confirmação, não de descoberta.
2. **Regular**: o eleitor só é despachado à mesa quando há vaga na fila dela;
   senão fica retido no checkpoint. Junto com a liberação controlada na porta,
   é isso que mantém a fila dentro do comprimento previsto (3/4/6 pessoas) e o
   salão com ~320 pessoas no pico.

As fitas substituem o papel 1. Não substituem o papel 2. É essa distinção que
o simulador torna visível.

## 2. O que o simulador diz

Cenário de referência: Cenário Claude (Três polos, checkpoint a 16 m, 3
atendentes por entrada, liberação por buffer, filas 3/4/6, identificação 45 s,
voto 30 s), 8 dias simulados. "Sem checkpoint" = o eleitor liberado na porta
lê a sinalização (10 s) e caminha direto à mesa.

| Cenário | Fecha (p50) | Espera P90 | fora / dentro | Pico dentro | Pico Ring 3 | Chegadas a fila cheia | Veredito |
|---|---|---|---|---|---|---|---|
| **Referência, com checkpoint** | 17h03 | 49 min | 33 / 20 | 321 | 962 | 0 | atenção (só a espera) |
| Fitas, porta libera enquanto cabe na zona | 17h03 | 68 min | 63 / 7 | 121 | 1.516 | 2.216 | falha |
| Fitas, porta livre | 17h03 | 50 min | 5 / 44 | **950** | 962 | **5.795** | falha |
| Fitas, porta só libera quem tem vaga na mesa | 17h28 | 103 min | 100 / 3 | 110 | 2.283 | 0 | falha |
| Fitas, buffer, filas de mesa 5/8/12 | 17h03 | 52 min | 42 / 17 | 206 | 1.001 | 2.188 | falha (1 conflito de fila) |

Quatro leituras.

**O horário de fechamento não muda.** Com ou sem checkpoint, a última mesa
fecha às 17h03 a 45 s por eleitor, e às 18h50–19h00 a 60 s. O gargalo é a mesa
receptora (dois cadernos em paralelo, pendência §9.7 da documentação), não a
triagem. Tirar o checkpoint não ganha vazão; mantê-lo não custa vazão.

**O que muda é onde a fila fica.** Sem checkpoint e com porta livre, a espera
total é a mesma (50 min) mas migra de fora para dentro: 950 pessoas no salão
no pico em vez de 321, e 5.795 chegadas a mesas com a fila já além do
comprimento previsto. É a fila do Ring 3, desenhada com barreira para 1.402
pessoas, transportada para dentro de um salão com 61 m de unifila.

**Se a porta tenta regular sem ver as mesas, regula mal.** Liberando enquanto
"cabe na zona" (a soma das filas das 9–10 mesas da entrada), o salão fica
vazio (121) mas 2.216 eleitores ainda chegam a filas cheias, porque a porta não
sabe *qual* mesa está cheia, e a espera fora sobe para 63 min com o Ring 3
acima da capacidade. Liberando só quem tem vaga na própria mesa, a fila
externa trava: quem está na frente espera a sua mesa e segura todos atrás
(bloqueio de cabeça de fila), e a espera vai a 103 min com as vermelhas
ociosas 123 min. O checkpoint resolve exatamente isso: retém por mesa, dentro,
sem travar a porta.

**Perder-se custa pouco em tempo.** Com 10 % ou 25 % dos eleitores errando o
caminho e andando 30–40 m a mais, a espera P90 muda 1–3 min. O custo da má
sinalização não é em minutos: é em gente circulando no meio do salão sem
destino, o que a simulação não pune e o Cartório sim.

## 3. As fitas sobre a planta

A sugestão literal, uma fita por mesa, dá 906 m de fita e 103 cruzamentos
entre fitas de entradas diferentes. A versão executável é por **tronco**: uma
fita por parede servida por cada entrada, rente à parede, passando pela ponta
da fila de cada mesa, com o número da mesa em placa alta.

| Atribuição mesa → entrada | Fita (troncos) | Cruzamentos entre entradas | Porta mais carregada ÷ menos | Ring 3 |
|---|---|---|---|---|
| **A da decisão** (por quota do Ring 3) | 463 m em 10 troncos | 18 | 1,16× | cabe |
| **Por parede** (oeste → A, norte → B, leste → C) | 214 m em 4 troncos | 1 | **3,36×** | C estoura |

A atribuição da decisão foi feita para equilibrar as três raias do Ring 3 e
separar as três mesas vermelhas, e para isso mistura paredes: cada entrada
serve mesas nas paredes norte, leste e oeste. No piso, isso vira três feixes
que se cruzam no meio do salão, o lugar por onde também passa quem sai. A
atribuição por parede elimina os cruzamentos, mas no Três polos a fachada
leste tem 13 mesas e a oeste 5: a porta C receberia 5.951 eleitores para uma
raia de 445, e a A 1.771.

Ou seja: **fitas só funcionam com um arranjo desenhado para elas**, com um
terço da carga em cada parede e as vermelhas uma por parede. O Hamad_3polos
chega mais perto (9 / 9 / 10 mesas por parede, 3.674 / 3.311 / 4.514
esperados, 1,36×), mas tem a mesa 4 sobre o vão de N2. É uma iteração de
prancheta, não de fita.

## 4. Organização no dia, lado a lado

| | Plano vigente (checkpoint) | Sugestão (fitas, sem checkpoint) |
|---|---|---|
| Onde o eleitor descobre a mesa | fora, nos painéis do percurso; confirma no checkpoint | fora, nos painéis do percurso; confirma na soleira (placa "cor da fita → mesas") |
| Quem regula a entrada na fila da mesa | checkpoint (retém por mesa) + liberação na porta | ninguém, ou a porta às cegas |
| Guia física até a mesa | corredor de unifila + indicação da equipe | fita colorida rente à parede + placa alta na mesa |
| Pessoal dentro do salão | 3 por entrada no checkpoint (9) + orientadores | 0 no checkpoint; 2–3 orientadores volantes por entrada para a fila que estourou (6–9) |
| Barreira | 28 postes do 1e presos ao checkpoint (22 nas divisórias, 6 nas bochechas) | esses 28 postes liberam ~56 m, o bastante para alongar as filas de mesa para 5/8/12 (+50 m) |
| Material específico | banners (contratados) | ~460 m de fita (~14 rolos, EUR 150–250, premissa) + 28 placas altas + 3 placas de soleira |
| Pico de gente dentro | ~320 | 120 (porta regulando) a 950 (porta livre) |
| O que acontece quando uma fila estoura | o checkpoint retém; a mesa vizinha não é invadida | a ponta da fila espalha pelo corredor de serviço e encosta na vizinha |

## 5. Efeitos de segunda e terceira ordem

- **2ª ordem, fitas:** o Ring 3 foi dimensionado para segurar 1.402 pessoas
  fora porque o salão segura ~320. Se a porta for livre, o Ring 3 fica vazio e
  o salão cheio; se a porta regular às cegas, o Ring 3 passa da capacidade (1.516
  a 1.551 no pico). O desenho do Ring 3 e o do interior são um sistema só.
- **2ª ordem, barreira:** o 1e foi contado com o checkpoint. Sem ele, 28
  postes mudam de lugar, e as filas de mesa passam a ser a única contenção:
  precisam ser mais longas (5/8/12), o que gera 1 conflito geométrico no
  Três polos (fila que bate em módulo ou faixa protegida) e pede outra rodada
  de prancheta.
- **3ª ordem, sinalização:** com 950 pessoas dentro, a fita no piso deixa de
  ser visível justamente onde mais importa, junto às paredes com fila. A guia
  passa a ser a placa alta, e a fita vira redundância. Investir na placa alta
  vale nos dois cenários; investir na fita só vale no salão vazio.
- **3ª ordem, procedimento:** o Cartório vê no checkpoint um ponto de
  controle documentado (quem entrou, para onde foi). Sem ele, a resposta a
  "por que essa mesa tem 40 pessoas na fila?" passa a ser dos orientadores
  volantes, sem registro.
- **Ambos os cenários:** o 60 s por eleitor derruba tudo (fecha 18h50–19h07).
  A conversa hub × fitas é de segunda ordem diante da decisão dos dois
  cadernos.

## 6. Recomendação para a discussão

1. **Manter o checkpoint como válvula**, não como balcão. Sua função
   insubstituível é reter por mesa; a de informar já está resolvida fora. Pode
   ser mais leve (2 atendentes por entrada dão 37 % de ocupação no pico).
2. **Adotar a fita como guia a partir do checkpoint**, não a partir da
   porta: três troncos por entrada, do checkpoint às paredes que ela serve,
   com placa alta numerada em cada mesa. Isso pega o que a sugestão tem de
   melhor (o eleitor não depende de indicação verbal) sem perder a regulação.
   Fitas e checkpoint não são excludentes.
3. Se a ideia for levada ao limite (sem checkpoint), **exigir junto**: um
   arranjo com um terço da carga por parede, atribuição por parede, filas de
   mesa 5/8/12 com os 28 postes do checkpoint, e 6–9 orientadores volantes.
   Sem esses quatro, o simulador reprova.
4. Testar na própria página do simulador: *Checkpoint → não* e *Liberação →
   livre* mostram o salão a 950 pessoas; *Liberação → buffer* mostra o Ring 3
   estourando. O motor em Node (`node simulador/fitas.js`) reproduz as tabelas.

## 7. Premissas específicas deste estudo

Tudo o mais é o do simulador. Aqui, além disso:

- Sem checkpoint, 10 s para ler a sinalização na soleira e caminhada direta
  a 1,2 m/s (constante do motor).
- Erro de sinalização: parâmetro novo `cen.sinalizacao = {erro, desvio}` em
  `modelo.js`, aplicado só sem checkpoint; padrão zero (não muda nenhum
  cenário existente).
- Fita: reta da soleira à ponta da fila (por mesa) ou tronco rente à parede;
  33 m por rolo e EUR 12 por rolo são premissas de compra, não cotação.
- Os 28 postes "do checkpoint" são os do desenho 1e (`saidas/tensa_barreiras.md`).
