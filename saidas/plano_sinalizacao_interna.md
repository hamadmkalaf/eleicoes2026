# Plano de sinalização interna — RDS Hall 2, 1º turno 04/10/2026

Base: prancheta **Hamad_Final** (`hamad-final-20260913150300`, 13/09/2026),
Cenário 3 / Ring 3 — **28 mesas**, salão em orientação **L-O** (eixo x =
leste-oeste), portas na parede sul.

Regra de encaminhamento dada pelo Posto: **porta A → parede oeste**,
**porta B → parede norte**, **porta C → parede leste**.

Tudo neste documento é gerado por `scripts/plano_sinalizacao.py` a partir da
prancheta e de `saidas/dados.json`; a saída estruturada fica em
`saidas/sinalizacao.json`.

---

## 1. Premissas e o que ainda não está fechado

| # | Premissa | Status |
|---|---|---|
| P1 | A numeração 1–28 da prancheta corresponde à coluna `Posicao` de `dados.json` (urnas ordenadas por volume decrescente) | **A validar.** É a única premissa que muda o conteúdo dos banners. Trocar `MAPA_MESA_URNA` no script regera o plano inteiro. |
| P2 | As três portas ficam na parede sul (y = 0), única livre na prancheta | Derivada da geometria; confirmar contra a planta de portas do RDS |
| P3 | Porta A a oeste do vão sul, B no centro (x ≈ 25,75 m), C a leste | Derivada: o maior vão livre da parede norte fora dos pares fica em x 23,25–28,25 m, alinhado ao centro do salão (25,1 m) |
| P4 | Alturas de caractere pela regra prática de 10 mm por metro de distância de leitura | Regra de projeto, **não** norma citável. Se o Posto quiser lastro normativo, medir no local antes de imprimir. |
| P5 | Comparecimento ponderado: 74% Dublin, 50% interior (taxas de 2022) | Mesma base do `contexto_eleicoes_dublin_2026.md` — comparável com as simulações anteriores |

**Validação automática:** o script falha em vez de gravar se as 51 seções não
aparecerem exatamente uma vez, se os aptos não somarem 16.794, ou se as 28
mesas não fecharem.

---

## 2. O que a prancheta diz

As 28 mesas se distribuem em três paredes, e a prancheta codifica os pares no
campo `lado`: duas mesas separadas por **exatamente 3,90 m** e com os lados
voltados uma para a outra compartilham o corredor entre elas. Os vãos de
2,70–3,00 m são circulação entre blocos.

| Parede | Porta | Mesas | Pares | Isoladas | Blocos (= banners de mesa) | Aptos | Comparecimento esperado |
|---|---|---|---|---|---|---|---|
| Oeste | **A** | 9 | 4 | 1 | 5 | 6.146 | 4.179 |
| Norte | **B** | 9 | 4 | 1 | 5 | 5.412 | 3.662 |
| Leste | **C** | 10 | 4 | 2 | 6 | 5.236 | 3.575 |
| **Total** | | **28** | **12** | **4** | **16** | **16.794** | **11.416** |

As quatro mesas isoladas (posições 19, 22, 23 e 24 da prancheta) têm todas
`lado = +1` e vãos simétricos de ~3 m dos dois lados — são de fato mesas
solteiras, não erro de desenho.

---

## 3. Os quatro achados que condicionam o plano

**(1) Não existe regra numérica que leve o eleitor à porta certa.**
As seções de Dublin da série 33xx estão espalhadas: 3306, 3307, 3311, 3313 e
3315 na porta A; 3305, 3309 e 3322 na B; 3302 e 3308 na C. Consequência
direta: **nenhuma peça de sinalização pode usar faixa de numeração** ("seções
3300–3350 → porta B" é falso). Toda peça de triagem precisa carregar a lista
completa, e a tabela de 51 linhas da seção 8 é obrigatória na comunicação
prévia e na sinalização externa.

**(2) O mesmo vale para o condado.** Cork aparece nas portas A e C; Limerick
nas portas B e C; "outros locais da Irlanda" nas portas A e C. Eleitores do
interior **não** podem ser triados por localidade — só por número de seção.

**(3) As portas estão desbalanceadas, e a sinalização não conserta isso.**
Porta A: 464 comparecentes esperados por mesa. Porta C: 358. São **30% a
mais por mesa na porta A, que ainda tem uma mesa a menos que a C.** Nenhum
banner resolve isso — a carga está fisicamente amarrada às mesas. As duas
saídas reais são (a) mover mesas na prancheta antes de imprimir, ou (b)
aceitar e compensar com pessoal. O plano abaixo adota (b) e concentra staff
na porta A, mas registro que (a) é mais barata: trocar dois blocos entre as
paredes oeste e leste custa zero em impressão se feito antes do fechamento
da arte.

**(4) A porta B obriga uma travessia de ~44 m.** O eleitor da parede norte
entra ao sul e atravessa o salão inteiro, cruzando o miolo. É a única porta
cujo destino não é visível da entrada. Exige peça aérea/alta, não só banner
de chão.

---

## 4. Arquitetura da sinalização — quatro níveis, 25 peças

| Nível | Peça | Onde | Função | Qtd |
|---|---|---|---|---|
| **N1** | Painel de decisão | Boca de cada serpenteado, no Ring 3 | Única triagem A/B/C do percurso | 3 |
| **N2** | Totem alto de porta | Logo após cada porta, dentro do Hall 2 | Confirmar que o eleitor entrou certo | 3 |
| **N3** | Painel das seções da parede | 7 m depois da porta, fora da linha de caminhada | Dizer qual bloco, na ordem física da parede | 3 |
| **N5** | Banner de bloco | Na boca do corredor de cada par | Identificar as seções daquele par | 16 |

Total: **25 peças**. Somar 3 banners de bloco em branco como reserva, caso a
premissa P1 mude depois da impressão.

**O que mudou em relação à versão anterior deste plano:**

- **N1 deixou de ser capa de barreira ao longo da fila** e virou uma peça
  única na boca de cada serpenteado, por decisão do Posto. De 24 capas para
  3 painéis.
- **N4, o mapa de entrada, foi cortado.** Sua função — dizer *onde* na parede
  — passou para o N3, que por isso muda de formato (ver seção 7).

### A consequência de sinalizar só a boca do serpenteado

Com a capa de barreira eliminada ao longo da fila, **o eleitor tem um único
ponto de decisão em todo o percurso**, e a próxima confirmação só chega no N2,
já dentro do salão. Quem entrar no serpenteado errado só descobre no fim dele,
e a correção custa refazer a fila inteira — no pior horário, é a diferença
entre votar e desistir.

Três medidas atenuam isso sem reintroduzir a capa:

1. **O N1 carrega as 51 seções**, não as 17 de uma porta. É a peça mais densa
   do plano: três colunas coloridas, A / B / C, em ordem crescente, para que a
   decisão seja verificável ali mesmo.
2. **Um orientador fixo na boca de cada serpenteado**, com a mesma lista em
   prancheta. É a barreira contra o erro que a sinalização sozinha não dá.
3. **Recomendo um totem de repetição no meio de cada serpenteado** — um
   A-frame com o índice das 51 seções, não uma capa de barreira. Dá uma
   segunda chance de correção enquanto ainda é barato sair da fila. Fica como
   recomendação, não como premissa: se o Posto preferir manter o serpenteado
   limpo, as medidas 1 e 2 seguem valendo.

### Regra de conteúdo, válida para todas as peças

- **Nunca aparece número de mesa.** Só número de seção. (Instrução do Posto.)
- Número de seção sempre em **4 dígitos**, como no e-Título — inclusive as de
  três dígitos, grafadas `0511`, `0517` etc. Evita que o eleitor procure
  "511" numa lista que mostra "0511" e conclua que não está lá.
- Ordem crescente de seção dentro da peça, nunca ordem de mesa. No N3 a
  ordenação desce um nível: os blocos vêm na ordem física da parede, e as
  seções em ordem crescente dentro de cada bloco.
- Cor por porta, constante em todos os níveis: **A = ciano, B = magenta,
  C = âmbar** — as duas primeiras já aparecem no `PLANO COM FLUXOS
  MELHORADO.png`. Verificar contraste ≥ 4,5:1 sobre branco antes de fechar a
  arte; âmbar puro costuma reprovar e precisa de escurecimento.
- Toda peça leva a letra da porta no canto superior, sempre na mesma posição.
- Bilíngue apenas em N1 e N2 (`ENTRADA A / ENTRANCE A`). N3 e N5 são
  numéricos e dispensam tradução.

### Alturas de caractere (premissa P4)

| Peça | Distância de leitura | Altura mínima do caractere |
|---|---|---|
| N1 letra da porta | 25 m | 250 mm |
| N1 números de seção | 8 m | 80 mm |
| N2 letra da porta | 30 m (visível do fundo do salão) | 300 mm |
| N3 números de seção | 6 m | 60 mm |
| **N5 números de seção** | **12 m** | **120 mm** |

O N5 é a peça crítica: é lida de dentro da fila, em movimento. 120 mm para
quatro dígitos × até 4 seções obriga banner de no mínimo **0,85 m de largura
por 2,0 m de altura** em base alugada (item (d) do orçamento).

---

## 5. Conteúdo literal dos banners de bloco (N5)

Um banner por bloco, na boca do corredor de 3,90 m do par (ou à frente da
mesa isolada). Sem número de mesa; a coluna "Posição na parede" abaixo é
para a equipe de montagem, não vai impressa.


#### Porta A — parede OESTE

| Peça | Tipo | Posição na parede | Seções no banner | Aptos | Compar. |
|---|---|---|---|---|---|
| **BA1** | Par | 8,90–12,80 m | **517 · 1292 · 3311 · 3913** | 1.143 | 819 |
| **BA2** | Par | 15,80–19,70 m | **519 · 3245 · 3313 · 3889** | 1.578 | 1.076 |
| **BA3** | Isolada | 23,00 m | **3688** | 400 | 296 |
| **BA4** | Par | 25,70–29,60 m | **3161 · 3307 · 3315 · 3778** | 1.583 | 1.077 |
| **BA5** | Par | 32,35–36,25 m | **518 · 530 · 3179 · 3306** | 1.442 | 912 |
| | | **Total porta A** | 17 seções | **6.146** | **4.179** |

#### Porta B — parede NORTE

| Peça | Tipo | Posição na parede | Seções no banner | Aptos | Compar. |
|---|---|---|---|---|---|
| **BB1** | Par | 8,55–12,45 m | **3322 · 3752 · 3862** | 1.194 | 884 |
| **BB2** | Par | 19,35–23,25 m | **511 · 527 · 1100 · 3216** | 1.153 | 768 |
| **BB3** | Isolada | 28,25 m | **1099 · 3054** | 454 | 323 |
| **BB4** | Par | 32,30–36,20 m | **521 · 3108 · 3305 · 3422** | 1.523 | 952 |
| **BB5** | Par | 39,05–42,95 m | **1160 · 1314 · 3309 · 3845** | 1.088 | 736 |
| | | **Total porta B** | 17 seções | **5.412** | **3.662** |

#### Porta C — parede LESTE

| Peça | Tipo | Posição na parede | Seções no banner | Aptos | Compar. |
|---|---|---|---|---|---|
| **BC1** | Par | 6,05–9,95 m | **3308 · 3442** | 797 | 590 |
| **BC2** | Isolada | 12,95 m | **512 · 2855** | 476 | 334 |
| **BC3** | Par | 15,95–19,85 m | **522 · 1352 · 3832** | 862 | 623 |
| **BC4** | Par | 22,85–26,75 m | **513 · 1105 · 3229 · 3821** | 1.108 | 746 |
| **BC5** | Isolada | 29,75 m | **2847 · 3078** | 429 | 310 |
| **BC6** | Par | 32,75–36,65 m | **1278 · 3142 · 3181 · 3302** | 1.564 | 973 |
| | | **Total porta C** | 17 seções | **5.236** | **3.575** |


Notas de conteúdo:

- **BC1** (797 aptos) e **BB1** (1.194) são os dois blocos 100% Dublin de maior
  volume da sua parede — são os candidatos naturais a reforço de pessoal.
- **BA2** e **BA4** (1.578 e 1.583 aptos) são os dois blocos mais carregados do
  salão inteiro e estão na mesma parede, **a 6 m um do outro**. A fila de um
  encosta na do outro. É o ponto de estrangulamento físico do Cenário 3 e
  precisa de separador reforçado no vão de 23,00–25,70 m, que é o mais
  estreito da parede oeste (2,70 m).
- **BB1** e **BC3** têm 3 seções; **BC1** tem 2. Manter o mesmo gabarito
  gráfico dos de 4 seções, com os números maiores — não redesenhar a peça.

---

## 6. Banners de porta (N3) — todas as seções que votam naquela parede

Grade de 3 colunas × 6 linhas, ordem crescente. Na arte impressa os
números vão com 4 dígitos (`0511`, `0517`, …); as listas abaixo estão sem os
zeros à esquerda porque é assim que saem da base do TSE.



**Porta A** (17 seções, 6.146 aptos):

    517 · 518 · 519 · 530 · 1292 · 3161
    3179 · 3245 · 3306 · 3307 · 3311 · 3313
    3315 · 3688 · 3778 · 3889 · 3913

**Porta B** (17 seções, 5.412 aptos):

    511 · 521 · 527 · 1099 · 1100 · 1160
    1314 · 3054 · 3108 · 3216 · 3305 · 3309
    3322 · 3422 · 3752 · 3845 · 3862

**Porta C** (17 seções, 5.236 aptos):

    512 · 513 · 522 · 1105 · 1278 · 1352
    2847 · 2855 · 3078 · 3142 · 3181 · 3229
    3302 · 3308 · 3442 · 3821 · 3832

Texto fixo no topo de cada peça:

> **PORTA A — PAREDE OESTE**
> Estas são as seções que votam nesta parede.
> Não encontrou a sua? Procure um mesário — sua seção está em outra porta.

A segunda linha é o que evita o pior caso operacional: o eleitor que não se
acha na lista e caminha pelo salão inteiro procurando, na contramão do fluxo.

---

## 7. Onde N2 e N3 ficam dentro do Hall 2

Coordenadas em metros de planta, origem no canto sudoeste, portas na parede
sul (y = 0). A premissa P3 coloca as portas em x = 9,00 (A), 25,75 (B) e
41,00 (C).

| Porta | Peça | Posição (x · y) | Distância da porta | Voltada para | Lado do eleitor |
|---|---|---|---|---|---|
| A | N2 totem | 11,50 · 3,50 | 4,3 m | sul | direita |
| A | N3 painel | 13,50 · 7,00 | 8,1 m | sudoeste | direita |
| B | N2 totem | 28,50 · 3,50 | 4,5 m | sul | direita |
| B | N3 painel | 30,50 · 7,00 | 8,4 m | sul | direita |
| C | N2 totem | 38,50 · 3,50 | 4,3 m | sul | esquerda |
| C | N3 painel | 36,50 · 7,00 | 8,1 m | sudeste | esquerda |

**Por que fora do eixo da porta.** O eleitor que entra pela A vira a oeste,
pela C vira a leste, e pela B segue reto. As duas peças ficam do lado oposto à
curva: quem para para ler sai da linha de caminhada em vez de represar a
soleira. É o mesmo motivo de o N3 estar a 7 m e não a 3 m — a 3 m, a
aglomeração de quem lê alcança a porta.

**Por que o N2 vem antes do N3.** O N2 responde a uma pergunta binária
("entrei certo?") e é lido em movimento, de 30 m; o N3 exige parar. Invertê-los
faria o eleitor parar antes de saber se está no lugar certo.

**Verificação de folga.** Nenhuma das seis posições cai sobre via de fila: a
faixa de piso mais ao sul da parede oeste começa em y = 7,4 m e x ≤ 3,6 m; a
da leste, em y = 4,1 m e x ≥ 44,5 m. Toda a banda y < 4 m está livre de ponta
a ponta, e a faixa y = 7 m só é ocupada junto às paredes.

### O N3 muda de formato porque o mapa saiu

Com o N4 cortado, o N3 é a única peça que pode dizer **onde** na parede. Uma
lista em ordem crescente não faz isso. Portanto:

- O painel **espelha a parede**: os 5 ou 6 blocos dispostos da esquerda para a
  direita na mesma ordem física em que o eleitor vai encontrá-los.
- Dentro de cada bloco, as seções em ordem crescente — a regra de ordenação
  continua valendo, só desce um nível.
- Cada célula de bloco traz os mesmos números que estarão no banner N5 lá na
  frente. A correspondência literal entre os dois é o que substitui o mapa.
- Formato apaisado, mínimo 2,40 × 1,20 m, para caber seis colunas legíveis.

É a forma mais barata de recuperar a informação que o mapa daria, sem uma peça
a mais no orçamento.

## 8. Tabela mestra seção → porta (51 seções)

Esta tabela é a peça mais reaproveitável do plano: alimenta a sinalização
externa, o site/Instagram, o roteiro dos orientadores e o cartão de bolso dos
mesários. Ordem crescente de seção, porque é assim que o eleitor procura.

| Seção | Porta | Seção | Porta | Seção | Porta |
|---|---|---|---|---|---|
| 511 | **B** · Norte | 1352 | **C** · Leste | 3308 | **C** · Leste |
| 512 | **C** · Leste | 2847 | **C** · Leste | 3309 | **B** · Norte |
| 513 | **C** · Leste | 2855 | **C** · Leste | 3311 | **A** · Oeste |
| 517 | **A** · Oeste | 3054 | **B** · Norte | 3313 | **A** · Oeste |
| 518 | **A** · Oeste | 3078 | **C** · Leste | 3315 | **A** · Oeste |
| 519 | **A** · Oeste | 3108 | **B** · Norte | 3322 | **B** · Norte |
| 521 | **B** · Norte | 3142 | **C** · Leste | 3422 | **B** · Norte |
| 522 | **C** · Leste | 3161 | **A** · Oeste | 3442 | **C** · Leste |
| 527 | **B** · Norte | 3179 | **A** · Oeste | 3688 | **A** · Oeste |
| 530 | **A** · Oeste | 3181 | **C** · Leste | 3752 | **B** · Norte |
| 1099 | **B** · Norte | 3216 | **B** · Norte | 3778 | **A** · Oeste |
| 1100 | **B** · Norte | 3229 | **C** · Leste | 3821 | **C** · Leste |
| 1105 | **C** · Leste | 3245 | **A** · Oeste | 3832 | **C** · Leste |
| 1160 | **B** · Norte | 3302 | **C** · Leste | 3845 | **B** · Norte |
| 1278 | **C** · Leste | 3305 | **B** · Norte | 3862 | **B** · Norte |
| 1292 | **A** · Oeste | 3306 | **A** · Oeste | 3889 | **A** · Oeste |
| 1314 | **B** · Norte | 3307 | **A** · Oeste | 3913 | **A** · Oeste |


---

## 9. Filas: uma por mesa, coladas no piso

### Correção ao desenho anterior

A primeira versão deste plano previa **uma fila por par de mesas**, com o
argumento de que as duas mesas do par compartilham o corredor de 3,90 m e
poderiam se revezar no atendimento. **Está errado.** Cada mesa guarda o
caderno de votação das suas próprias seções: o eleitor da 3313 só pode ser
atendido na mesa que tem o caderno da 3313, ainda que a mesa vizinha esteja
vazia. Não há ganho de enfileiramento único porque não há substituição
possível entre as duas mesas.

Portanto: **28 filas, não 16.** O banner continua sendo do par — a instrução
do Posto de não numerar mesas se mantém, porque as duas mesas do par se
distinguem pelas seções, não por número. Mas a fita no chão desce ao nível da
mesa: dentro do corredor do par, a via se bifurca, um ramo para cada conjunto
de seções.

### Quanta fila cada mesa vai ter

Modelo determinístico por hora, comparecimento ponderado (74% Dublin / 50%
interior), perfil de chegada com pico matinal
(12-15-16-14-11-9-8-8-7% das 8h às 17h), 0,50 m por pessoa em fila simples.

| Segundos por voto | Pessoas em fila no pico | Mesas com fila | Via linear total |
|---|---|---|---|
| 30 s | 0 | 0 | — |
| **60 s** | **592 (às 12h)** | **13 de 28** | **296 m** |
| 90 s | 2.191 (às 13h) | 28 de 28 | 1.095 m |

A 60 s a fila se concentra: a mediana das mesas não forma fila nenhuma e três
mesas sozinhas concentram 300 pessoas. A 90 s o salão inteiro vira fila —
1.095 m de via ocupariam cerca de metade da área útil do Hall 2. **Não existe
plano de colagem que resolva o cenário de 90 s**; é o mesmo colapso que a
simulação de agregação já apontava, agora medido em metros de piso. A colagem
é executada para 60 s, com o miolo do salão mantido livre como transbordo.

### A regra que garante o não cruzamento

Não é bom senso, é geometria:

1. **Cada mesa é dona da faixa de piso à sua frente** — tão larga quanto o vão
   até a mesa vizinha (2,0 a 3,9 m), tão profunda quanto a fila projetada
   exigir.
2. **A faixa avança perpendicular à sua própria parede.** Faixas paralelas
   saindo da mesma parede nunca se cruzam.
3. **Nenhuma faixa alcança a parede oposta.** A mais profunda tem 22 m num
   salão de 44,5 m; sobra um miolo livre de 14 m de largura.
4. **Quadrado de canto de 8 m sem fila**, nos dois cantos norte, onde as
   faixas da parede norte e das paredes leste/oeste se aproximariam.
5. **Toda a circulação acontece no miolo livre.** O eleitor entra pela porta,
   atravessa o vazio central e entra na sua via **pela cauda** — que é onde
   fica o decalque com o número da seção. Não há corredor-tronco colado: o
   tronco é o próprio vazio, o que também economiza fita.

Com essas cinco regras, as 28 vias são disjuntas por construção. Não é preciso
verificar cruzamento caso a caso.

### Três mesas não cabem onde a prancheta as coloca

| Mesa | Bloco | Seções | Via necessária | Profundidade que exigiria | Limite | Motivo |
|---|---|---|---|---|---|---|
| 2 | BB1 | 3322 / 3752 | 65 m | 22 m | 8 m | canto noroeste |
| 4 | BA4 | 3315 / 3778 | 64 m | 32 m | 22 m | vão de 2,75 m → só 2 vias |
| 3 | BC6 | 3142 / 1278 | 27 m | 9 m | 8 m | canto nordeste |

O padrão é claro e vale como regra de projeto para qualquer revisão da
prancheta: **mesa pesada não pode ir para canto nem para vão estreito.** As
três mesas de ~590 comparecentes precisam de posição de meio de parede com
vão de 3,9 m. Posições que hoje têm folga e fila zero — BB3 (norte, isolada,
3,9 m), BB2 (norte, 3,9 m), BC1 (leste, 3,9 m) — são destino natural para
elas. É uma troca na prancheta, custo zero se feita antes da colagem.

### Tipos de colagem e quantitativo

| Tipo | Quando | Slots | O que se cola |
|---|---|---|---|
| **1 — marca de início** | via até 6,5 m | 16 | linha-guia simples + decalque de seção na cauda |
| **2 — via simples** | 6,5 a 30 m | 9 | duas bordas contínuas |
| **3 — serpentina** | acima de 30 m | 3 | 3 vias de 1,00 m, 4 linhas longitudinais |

- **Via de fila projetada:** 489 m (pico de 60 s + 30% de folga)
- **Fita de piso:** 493 m
- **Decalques de seção:** 144 (1 na cauda + 1 a cada 5 m de via)

Especificação da fita: largura 75 mm, vinil de piso antiderrapante com
classificação de resistência ao escorregamento, na cor da porta. Decalques
com número de seção em 4 dígitos, altura de caractere 150 mm, legíveis de pé.
Confirmar com o RDS se há restrição de adesivo no piso do Hall 2 — alguns
contratos de locação proíbem fita de piso ou exigem remoção sem resíduo.

### Separadores físicos (item (d) do orçamento)

Com o vazio central fazendo o papel de tronco, os separadores físicos ficam
reservados a três usos: (a) os canais de aproximação externos das três portas,
(b) a bifurcação dentro do corredor de 3,90 m de cada par, onde a fita sozinha
não impede corte de fila, e (c) o reforço do vão de 2,70 m entre BA3 e BA4.
Isso reduz a demanda interna estimada na versão anterior deste plano (184,5 m)
e **libera folga para a fila externa**, que era o item que estourava o
orçamento. O número exato depende de quanta fita substitui separador — decisão
a tomar com o fornecedor, mas agora com margem em vez de déficit.

## 10. Impactos sobre a sinalização externa

A sinalização externa ainda não existe. Estes são os requisitos que o plano
interno impõe a ela — não são sugestões, são condições para o interno
funcionar:

1. **A triagem acontece na boca do serpenteado, no Ring 3, e em nenhum outro
   lugar.** É a decisão do Posto e ela concentra todo o risco num ponto: quem
   entra no serpenteado errado só descobre no N2, já dentro do salão. Ver as
   três medidas atenuantes da seção 4.
2. **O N1 carrega as 51 seções**, não as 17 de uma porta. Pela seção 3, achado
   (1), não há atalho numérico: é lista completa ou nada. Três colunas
   coloridas, A / B / C, em ordem crescente — é a tabela da seção 8 impressa
   em grande formato.
3. **Mesma paleta, mesma tipografia, mesmos 4 dígitos.** A cor com que o
   eleitor decidiu lá fora é a cor que ele procura lá dentro. Qualquer
   divergência entre externo e interno anula o ganho da triagem.
4. **A fila externa precisa de separadores próprios** — ver seção 9.
5. **Sinalização de acessibilidade e prioridade** (idosos, gestantes, PcD)
   é externa e precisa de canal próprio que desemboque nas três portas, não
   numa só; caso contrário concentra toda a demanda prioritária numa parede.
6. **Placa de rua / chegada** no acesso ao RDS pela Merrion Road, com o nome
   do Hall 2 (Shelbourne Hall) — o RDS tem seis halls e o eleitor que erra de
   hall gasta 5–10 minutos e volta pelo fim da fila.

---

## 11. Efeitos de segunda e terceira ordem

**Segunda ordem.** A triagem correta desloca o gargalo, não o elimina: com
as filas separadas por bloco, o tempo de espera passa a ser visível e
desigual — o eleitor da porta C vê a fila da porta A e conclui que foi mal
atendido. Recomenda-se não posicionar as três filas em campo visual comum,
o que a geometria em três paredes já favorece. O risco inverso também existe:
a porta A, 30% mais carregada por mesa, vai terminar depois das outras duas,
e mesários das paredes norte e leste ficarão ociosos enquanto a oeste ainda
atende. Prever **realocação de mesários entre paredes a partir das 15h30** —
o que exige que o Cartório Eleitoral valide previamente a movimentação, já
que mesário é vinculado à sua seção.

**Terceira ordem.** Sinalização que funciona reduz o tempo médio por eleitor
sem tocar no tempo de urna — é o único ganho de vazão disponível depois que o
número de mesas está fechado em 28. Se o Cenário 3 estourar mesmo assim, a
sinalização bem documentada vira a prova de que o gargalo é o número de
urnas, não a organização do Posto: este documento, com os números de
comparecimento por bloco, é peça de defesa junto ao TSE tanto quanto peça
operacional. Inversamente, sinalização improvisada transfere a culpa do
desenho de agregação para a execução local — que é exatamente o que o Posto
não quer, tendo contestado a agregação desde o início.

E o efeito que raramente se mede: fila longa não aparece na estatística de
comparecimento como privação de voto, aparece como abstenção. O eleitor que
desiste melhora as métricas de tempo por mesa. Nenhum indicador operacional
do dia vai sinalizar esse custo — só a comparação de comparecimento com 2022,
depois do fato.

---

## 12. Pendências antes de fechar a arte

1. **Confirmar a premissa P1** (prancheta 1–28 ↔ `Posicao` de `dados.json`).
   É o que decide o conteúdo de todos os 19 banners numéricos (16 N5 + 3 N3). Se mudar,
   rodar `python3 scripts/plano_sinalizacao.py` com o novo `MAPA_MESA_URNA`.
2. Confirmar posição real das portas na parede sul do Hall 2 (P2/P3).
3. Decidir entre mover blocos na prancheta ou compensar com pessoal o
   desbalanceamento de 30% da porta A (seção 3, achado 3).
4. Fechar a contratação adicional de separadores para a fila externa
   (seção 9) — é o item que estoura o orçamento revisado.
5. Validar com o Cartório Eleitoral a realocação de mesários entre paredes
   no fim do dia (seção 11).
6. Conferir se EUR 1.961,00 (item (c) do orçamento) cobrem as 25 peças mais
   bases alugadas — com o corte do mapa e a redução do N1 a três painéis, dá
   ~EUR 78 por peça, folgado onde antes era apertado. A folga deve ser
   gasta no N1, que virou a peça mais crítica do plano.
7. Medir o contraste da cor âmbar da porta C sobre branco antes de imprimir.
8. Confirmar com o RDS se o contrato de locação admite fita e decalque no
   piso do Hall 2, e em que condições de remoção.
9. Trocar de posição, na prancheta, as três mesas pesadas que hoje caem em
   canto ou vão estreito (seção 9) — antes de colar qualquer coisa.

---

*Gerado por `scripts/plano_sinalizacao.py` a partir da prancheta Hamad_Final
e de `saidas/dados.json`. Saída estruturada: `saidas/sinalizacao.json`.*
