# Contexto do desenho de fluxo — posto de Dublin, 1º turno de 2026

Documento de passagem. Reúne tudo que já foi medido, calculado e decidido sobre
o layout do salão de votação, para que uma sessão nova possa retomar sem
refazer nada. **As ideias 1 e 2 estão fechadas.** Falta a decisão entre elas,
que depende das perguntas em aberto do §10.

---

## 1. O problema

Organizar o fluxo de eleitores no **RDS Ballsbridge, Hall 2**, em Dublin, no 1º
turno de 04/10/2026 (8h–17h). São **28 MRVs** (mesa receptora + urna) para
**16.794 eleitores aptos** em 51 seções. Três perguntas a responder:

1. Como distribuir as 28 MRVs pelo salão.
2. Duas ou três entradas.
3. Quais portas para entrada e quais para saída.

Critérios dados pelo usuário: fluxo fluido e ininterrupto; evitar que eleitores
de MRVs tranquilas fiquem parados atrás de filas de MRVs cheias; entrada e
saída inequívocas.

---

## 2. Fontes

| Fonte | Onde | O que dá |
|---|---|---|
| `RDS_Hall_2_Floorplan_(1).pdf`, pág. 2 | raiz do repo | planta do Hall 2 e ficha técnica |
| Versão revisada da planta, com duas portas de carga circuladas | anexo do usuário | posição das portas de carga |
| `data/raw/eleitorado_local_votacao_2026_ZZ.csv` | repo | seção a seção, aptos e agregações |
| `data/raw/Filtrado_Dublin.csv` | repo | onde cada eleitor reside |
| `saidas/dados.json` | repo | as 28 urnas já apuradas (gerado por `scripts/mapa_agregacoes.py`) |

---

## 3. Geometria medida — não precisa remedir

Medida direto do PDF. **Escala aferida: 8,69 pt/m**, conferida contra a ficha
técnica impressa no próprio documento (50,2 m × 44,5 m, 2.238 m²). Está toda
codificada em **`scripts/salao.py`**, que é a fonte única.

- **Salão:** 50,3 m (leste-oeste) × 44,4 m (norte-sul), com o **canto sudoeste
  recortado** (x 0–7,8 m, y 0–7,0 m fora do salão).
- **Origem (0,0)** = canto sudoeste útil; x cresce para leste, y para norte.

### Portas (metros, medidos do canto oeste em paredes horizontais e do canto sul em verticais)

| Parede | Porta | De | Até | Largura | Papel na ideia 1 |
|---|---|---|---|---|---|
| Sul | **carga oeste** | 7,83 | 11,45 | 3,62 m | **Entrada A** |
| Sul | 2.7 | 17,22 | 18,47 | 1,25 m | só emergência |
| Sul | 2.5/2.6 | 19,10 | 25,03 | 5,93 m | reforço da saída |
| Sul | 2.4 | 25,32 | 31,25 | 5,93 m | **Saída principal** |
| Sul | 2.2/2.3 | 31,54 | 37,47 | 5,93 m | reforço da saída |
| Sul | 2.1 | 38,09 | 39,36 | 1,27 m | só emergência |
| Sul | **carga leste** | 45,12 | 48,75 | 3,63 m | **Entrada B** |
| Norte | 2.13 | 7,41 | 9,44 | 2,03 m | emergência |
| Norte | 2.14/2.15 | 20,66 | 24,22 | 3,55 m | emergência |
| Leste | 2.22/2.23 | 2,95 | 6,01 | 3,06 m | emergência |
| Leste | 2.20/2.21 | 14,80 | 17,87 | 3,06 m | emergência |
| Leste | 2.18/2.19 | 26,66 | 29,72 | 3,06 m | emergência |
| Leste | 2.16/2.17 | 38,51 | 41,57 | 3,06 m | emergência |
| Oeste | 2.10/2.11 | 19,36 | 22,43 | 3,07 m | acesso aos WC (fora do salão) |
| Oeste | acesso Hall 1 | 36,80 | 38,50 | 1,70 m | passagem |

As portas de carga **não** aparecem rotuladas como EXIT na planta porque são
portas de *get-in* de feira. A largura bate com a ficha técnica, que registra a
porta principal de carga em **4,87 × 3,73 m**. As saídas 2.8/2.9 ficam na parede
do recorte sudoeste.

---

## 4. Premissas

| Premissa | Valor | Origem |
|---|---|---|
| Comparecimento, residentes em Dublin | 74% | taxa observada em 2022 |
| Comparecimento, residentes no interior | 50% | taxa observada em 2022 |
| Perfil de chegada (8h–17h) | 8/13/15/14/12/11/10/9/8 % | premissa de projeto, pico de meio de manhã — **não é dado observado** |
| Tempo por eleitor (ponto de projeto) | 55 s | escolha conservadora; ver §6 |
| Área por pessoa em fila | 1,0 m² | fila serpenteada com balizadores |
| Balizador entre baias vizinhas | 0,6 m | |

### Mobiliário (informado pelo usuário)

- Mesa dos mesários: **1,60 × 0,70 m**
- Mesa da urna: **redonda, Ø 0,90 m**
- Estrutura que fecha o **fundo e os lados** da urna. **O que importa é bloquear
  a face para onde aponta a tela.** O sigilo vem da estrutura, não da parede —
  por isso ilha é tão válida quanto parede.
- Módulo adotado na ideia 1, com mesa e urna **lado a lado**: **2,80 m de frente
  × 1,90 m de profundidade**. Numa disposição **em linha** (urna atrás da mesa)
  o módulo cairia para ~1,80 m de frente × ~2,60 m de profundidade — ver §7.

### Restrição de segurança (informada pelo usuário)

**Nenhuma seção a menos de 3 m das saídas de emergência 2.16 a 2.23.** Na ideia 1
o recuo foi aplicado, por prudência, a **todas** as saídas de emergência. Se
valer só para 2.16–2.23, como está literalmente dito, a conta muda muito — ver §7.

---

## 5. As 28 urnas — o essencial

**11.418 comparecentes esperados** de 16.794 aptos. A distribuição tem um degrau
nítido:

- **3 urnas críticas: 3313 (590), 3322 (588), 3315 (586).** São as únicas que
  somam **duas seções inteiras de Dublin**.
- **8 urnas de carga alta: 466 a 492** (3142, 3161, 3245, 3302, 3305, 3306,
  3108, 3311). Sete delas são uma seção de Dublin somada a **um condado inteiro
  do interior** (Cork, Galway, Limerick, Westmeath…). São **4.213 eleitores que
  moram fora de Dublin** e vão viajar para votar — **chegam em rajada**, não
  diluídos ao longo do dia. Precisam de piso de fila desproporcional à média.
- **17 urnas abaixo de 435**, das quais 12 praticamente não formam fila.

> A premissa inicial da conversa era "4 MRVs com ~600 eleitores". Os dados
> mostram **3**, e o segundo grupo é um problema de *rajada*, não de volume.

---

## 6. O que realmente decide: o tempo de atendimento

Simulação em passos de 5 min sobre o perfil de chegada. Fila de pico **somada
nas 28 urnas**:

| s/eleitor | fila de pico somada | maior fila | urnas com fila > 10 | última a fechar |
|---|---|---|---|---|
| 45 s | 33 | 12 | 2 | 17h00 |
| 50 s | 100 | 32 | 3 | 17h00 |
| **55 s** | **241** | **57** | **6** | **17h20** |
| 60 s | 436 | 84 | 11 | 18h05 |
| 70 s | 929 | 136 | 14 | 19h35 |
| 90 s | 2.165 | 230 | 23 | 22h45 |

Fator 65 entre 45 s e 90 s. **O método de identificação do eleitor é uma decisão
de layout tanto quanto de procedimento.** Qualquer ideia deve ser dimensionada
para 55 s e reservar piso para o cenário de 60 s.

---

## 7. A conta que decide entre parede e ilha

Quantas das 28 MRVs cabem no **perímetro** do salão, respeitando os recuos e
descontando os cantos (1,5 m). Rode `python3 scripts/salao.py` para reproduzir.

| Cenário | Parede livre | Posições de 28 |
|---|---|---|
| Recuo de 3 m em **todas** as saídas · módulo de 2,80 m | 55,7 m | **11** |
| Recuo de 3 m em todas · módulo **em linha** de 1,80 m | 55,7 m | **21** |
| Recuo de 3 m **só na parede leste** · módulo de 2,80 m | 74,9 m | **19** |
| Recuo de 3 m **só na leste** · módulo **em linha** | 74,9 m | **29** ✅ |
| Idem, incluindo a parede sul | 84,0 m | 33 |

Na hipótese conservadora (primeira linha) a parede leste **desaparece por
inteiro**: cada trecho livre entre 2.16 e 2.23 mede **2,79 m**, um centímetro a
menos que o módulo de 2,80 m. Foi isso que empurrou a ideia 1 para ilhas.

> **Correção da ideia 2.** Esta tabela conta cada MRV pela frente mínima, e
> isso subestima a exigência. A MRV que forma fila precisa de *baia*, e a baia
> é tão larga quanto a fila pedir na profundidade disponível: a 55 s cada urna
> crítica pede 9,8 a 10,1 m de frente. Somadas, as 28 baias exigem **81,0 m**
> contra 68,2 m aproveitáveis. É preciso uma **terceira alavanca** — ver §9.

**Para a ideia 2 (tudo nas paredes), as duas alavancas são exatamente essas
duas**, e ambas são perguntas de fato, não de projeto:

1. O recuo de 3 m vale só para **2.16–2.23**, como foi dito, ou para todas as
   saídas de emergência?
2. A mesa da urna pode ficar **atrás** da mesa dos mesários (módulo em linha,
   ~1,80 m de frente) em vez de ao lado?

Com as duas respostas favoráveis, a parede comporta 29 posições e a ideia 2 é
viável. Com apenas uma, não fecha.

Trechos aproveitáveis no cenário favorável (só leste + módulo em linha):

| Parede | De | Até | Comprimento | Posições |
|---|---|---|---|---|
| Norte | 1,50 | 6,81 | 5,31 m | 2 |
| Norte | 10,04 | 20,06 | 10,02 m | 4 |
| Norte | 24,82 | 48,80 | 23,98 m | 10 |
| Oeste | 8,50 | 18,76 | 10,26 m | 4 |
| Oeste | 23,03 | 36,20 | 13,17 m | 5 |
| Oeste | 39,10 | 42,90 | 3,80 m | 1 |
| Leste | 9,01 | 11,80 | 2,79 m | 1 |
| Leste | 20,87 | 23,66 | 2,79 m | 1 |
| Leste | 32,72 | 35,51 | 2,79 m | 1 |

---

## 8. Ideia 1 — três fileiras de ilhas (fechada)

**Portas.** Entrada A pela porta de carga oeste, entrada B pela porta de carga
leste, saída pela baia central 2.4, com 2.5/2.6 e 2.2/2.3 de reforço no pico;
2.7 e 2.1 só emergência. As entradas ficam a **37 m** uma da outra e a fachada
se lê em três blocos contíguos: entra na ponta oeste, sai pelo meio, entra na
ponta leste. Atendimento prioritário em raia própria dentro de cada porta de
carga (3,6 m de vão comportam uma raia de 1,2 m ao lado da geral).

**Duas entradas, não três.** A porta não é o gargalo — um vão de 3,6 m passa
mais de 60 pessoas/min e o posto inteiro recebe ~29/min no pico. O gargalo é a
**triagem**, que se multiplica em raias na fila externa, não em portas. Uma
terceira entrada só caberia no meio, ao lado da saída, e faria a fachada
alternar entrada-saída-entrada-saída-entrada.

**Layout.** Três fileiras leste-oeste, todas com os módulos de frente para o
sul, partidas ao meio pela espinha de saída (x 26–31 m, sul-norte). Faixas do sul
para o norte: avental/distribuição 3 (0–4,7), baias 3 (4,7–8,2), fileira 3
(8,2–10,1), retorno 3 (10,1–12,6), distribuição 2 (12,6–16,1), baias 2
(16,1–19,6), fileira 2 (19,6–21,5), retorno 2 (21,5–24,0), distribuição 1
(24,0–27,5), baias 1 (27,5–39,5), fileira 1 (39,5–41,4), retorno 1 (41,4–44,4).
Avenidas de entrada em x 3–6 (oeste) e x 45–47,5 (leste).

Corredores de distribuição e de retorno **se alternam em faixas paralelas e
nunca se cruzam**; só se encontram na espinha.

**Gradiente de carga.** Fileira 3 (junto às portas) recebe as urnas leves com
baias de 2,5 m; fileira 1 (ao fundo) recebe as pesadas com baias de até 12 m.
Como a carga só cresce com a distância, o eleitor de urna leve nunca passa pelo
campo de fila de uma urna pesada.

**Setor reforçado.** As três críticas ficam **juntas** — não intercaladas — num
bloco de 16,5 × 12 m no canto noroeste, com 4 mesários cada (o quarto confere
documentos ainda dentro da fila). Intercalá-las com urnas leves obrigaria os
eleitores das leves a caminhar entre dois aglomerados densos.

**Tela da urna** girada 90° em relação à mesa, apontando para o painel lateral
do módulo — perpendicular tanto à fila (que chega pelo sul) quanto ao retorno
(que passa pelo norte).

**Resultados:** zona A 5.948 eleitores (52%), zona B 5.470 (48%); 87 mesários;
477 m de balizador; nenhuma baia abaixo da fila de pico da sua urna.

**Pontos fracos conhecidos da ideia 1:**
- Alimentação elétrica das urnas passa a ser **em ilha**, pelo piso — caixas de
  piso do salão, se houver, ou canaleta atravessando corredores. É a linha de
  custo mais provável de ter sido subestimada (alínea (b) do telegrama).
- Depende de o Cartório Eleitoral aceitar seções fora das paredes.
- Depende de as portas de carga poderem ficar abertas e travadas o dia inteiro.
- Gasta a metade sul do salão em circulação; a densidade de MRVs por m² é baixa.

---

## 9. Ideia 2 — todas as MRVs nas paredes (fechada)

**Viabilidade: cabe, e só cabe com três condições ao mesmo tempo.** As duas do
§7, mais uma terceira que aquele diagnóstico não viu.

1. Recuo de 3 m só nas saídas 2.16–2.23. Com o recuo em todas, 55,7 m e 11
   posições — a ideia morre aí.
2. Módulo **em linha**: urna atrás da mesa dos mesários, 1,80 m de frente por
   2,60 m de profundidade. Rende 29 posições contra 19 do módulo lado a lado.
3. **Setor reforçado nas três críticas.** Sem ele, as 28 baias dimensionadas
   pela fila exigem 81,0 m contra 68,2 m aproveitáveis. Com quatro mesários e
   conferência de documento dentro da fila, as três operam a 45 s, a fila de
   pico cai de 57 para 12, e a exigência cai para **61,9 m**. Folga final:
   6,3 m em 68,2.

**Os cantos comem parede.** O recuo de 3 m é um *envelope*, não uma faixa: a
saída 2.16/2.17 fica a 2,8 m do canto nordeste e come 3 m da ponta da parede
norte. Somado ao conflito entre a baia da ponta norte da parede oeste e a da
ponta oeste da parede norte, os 74,9 m do §7 viram **68,2 m em oito trechos**.
Os dois conflitos foram achados pela checagem geométrica, não pela conta feita
parede a parede.

**Layout.** Faixas a partir de cada parede: módulo 2,6 m, baia de fila até
7,0 m, corredor de retorno 2,4 m, avenida de entrada 3,0 m. A profundidade do
retorno e da avenida acompanha a baia mais funda daquela parede, então o anel
encolhe onde as filas são curtas — 15,0 m no norte, 10,5 m no oeste, 11,1 m no
leste. Avenida e retorno correm paralelos e adjacentes e só se encontram na
espinha de saída; quem entra cruza o retorno uma vez, perpendicularmente, na
boca da própria baia.

**Portas: as mesmas da ideia 1**, para que as duas sejam comparáveis. Entrada A
pela porta de carga oeste, entrada B pela leste, saída pela baia central 2.4
com 2.5/2.6 e 2.2/2.3 de reforço. A fachada sul inteira fica livre de MRVs.

**Repartição.** Zona A (parede oeste + ponta oeste da norte) com 15 MRVs e
4.970 comparecentes; zona B (parede leste + resto da norte) com 10 MRVs e
4.684; setor reforçado com 3 MRVs e 1.764, no meio da parede norte, logo acima
da cabeça da espinha e servido pelas duas entradas. Contando metade do setor
para cada lado, a divisão sai em 51/49. As zonas têm contagens diferentes
porque a parede leste, recortada por quatro pares de saídas, só oferece três
posições isoladas — o equilíbrio se faz pela carga, não pela contagem: a zona B
fica com as urnas mais pesadas, a zona A com as mais leves.

**Gradiente de carga** preservado: a carga cresce ao longo do circuito de cada
zona, então quem vota numa urna leve nunca atravessa o campo de fila de uma
urna pesada.

**Resultados:** 61,9 m de frente ocupada de 68,2 m; fila de pico somada 106
(seria 241 sem o setor reforçado); 87 mesários, os mesmos da ideia 1; 276 m de
balizador contra 477 m da ideia 1; caminhada média da porta ao módulo 41,6 m,
máxima 61,7 m.

**Pontos fracos conhecidos da ideia 2:**
- **Não sobra parede.** 6,3 m de folga em 68,2. Mobiliário maior que o
  informado, uma quarta urna crítica ou o cenário de 60 s derrubam o arranjo, e
  aqui não há piso de reserva ao lado das baias como na ideia 1.
- Depende de **três** condições externas, contra duas da ideia 1 (que não
  depende de nenhuma das do §7).
- As três posições da parede leste ficam isoladas entre pares de saídas de
  emergência, cada uma num nicho de 2,79 m.

**Comparação com a ideia 1:** ideia 2 gasta 276 m de balizador contra 477 m,
devolve o miolo do salão e mantém as seções encostadas nas paredes, com
alimentação elétrica pelo perímetro. Ideia 1 não depende de nenhuma das três
condições e tem piso de reserva, mas põe as 28 seções em ilha e leva a
alimentação elétrica para o meio do salão. A escolha é de risco, não de
eficiência.

## 10. Perguntas em aberto

Por ordem de retorno:

1. **As portas de carga podem ficar abertas e travadas durante as nove horas, e
   a soleira serve para pedestre?** Portas de carga costumam ser de enrolar e às
   vezes têm função corta-fogo. Se não puderem, as entradas voltam para as baias
   2.5/2.6 e 2.2/2.3, com as três aberturas amontoadas em 18 m.
2. **O recuo de 3 m vale só para 2.16–2.23 ou para todas as saídas?** Decide a
   viabilidade da ideia 2.
3. **A urna pode ficar atrás da mesa (módulo em linha, ~1,80 m de frente)?**
   Também decide a ideia 2.
3b. **O Cartório aceita as três críticas com quatro mesários e conferência
   antecipada na fila?** É a terceira condição da ideia 2 — sem ela a ideia 2
   não fecha. Vale para a ideia 1 também, onde é refinamento e não condição.
4. **Qual o método de identificação do eleitor** — biométrico, eletrônico ou
   caderno físico? Põe o posto em 45, 55 ou 90 s e decide se as baias bastam.
5. **A triagem será humana ou por sinalização?** Se depender de conferência
   verbal na entrada, vira gargalo não paralelizável e o número de raias
   externas precisa ser dimensionado.
6. **O Cartório Eleitoral valida seções em ilha** e o setor reforçado com 4
   mesários e conferência antecipada dentro da fila?
7. **Onde ficam as caixas de piso elétricas do Hall 2**, se houver?

---

## 11. Arquivos

| Arquivo | O que é |
|---|---|
| `scripts/salao.py` | **Núcleo comum:** geometria medida, premissas, carga das urnas, simulação de fila, cálculo de capacidade de parede. Toda ideia importa daqui. Rodando sozinho, imprime os cenários do §7. |
| `scripts/ideia1_ilhas.py` | Layout da ideia 1 → `saidas/ideia1_dados.json` |
| `scripts/ideia1_planta.py` | Planta em escala → `saidas/ideia1_planta.svg` |
| `scripts/ideia1_pagina.py` + `ideia1_template.html` | Peça de leitura → `saidas/ideia1_plano.html` |
| `scripts/estilo_plano.css` | Folha de estilo comum às peças de leitura das duas ideias |
| `scripts/ideia2_paredes.py` | Layout da ideia 2 → `saidas/ideia2_dados.json` |
| `scripts/ideia2_planta.py` | Planta em escala → `saidas/ideia2_planta.svg` |
| `scripts/ideia2_pagina.py` + `ideia2_template.html` | Peça de leitura → `saidas/ideia2_plano.html` |
| `saidas/dados.json` | As 28 urnas apuradas (etapa anterior, não mexer) |

A peça de leitura da ideia 1 está publicada em
<https://claude.ai/code/artifact/bdf8a5b8-2fdd-4b00-a409-9fe4af2bf3f2>.
Para atualizá-la de outra sessão, publique passando essa URL em `url` — sem
isso, cria-se um artefato separado.

```bash
cd scripts
python3 salao.py           # confere os dados e a capacidade de parede
python3 ideia1_ilhas.py    # imprime a alocação das 28 urnas
python3 ideia1_planta.py
python3 ideia1_pagina.py

python3 ideia2_paredes.py  # imprime a conta de viabilidade e a alocação
python3 ideia2_planta.py
python3 ideia2_pagina.py
```
