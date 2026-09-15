# Contexto — sessão de sinalização interna do RDS Hall 2

> Registro da conversa de 14–15/09/2026 com Claude Code sobre o plano de
> sinalização interna e de colagem das filas no piso para o 1º turno de
> 04/10/2026. Escrito para ser relido antes de retomar o assunto, sem
> depender do histórico da conversa.
>
> Documento irmão: `contexto_eleicoes_dublin_2026.md` (contexto geral do
> pleito). Este aqui cobre só sinalização e filas.

---

## 1. O que foi pedido, em ordem

1. Plano de sinalização interna considerando a prancheta **Hamad_Final** e o
   **Ring 3 no Cenário 3**, com filas entre os separadores e orientação L-O.
2. Sinalização nas barreiras identificando as entradas A, B e C.
3. Banners logo depois das portas, identificando **todas** as seções que votam
   naquela parede.
4. Um banner por **par de mesas**, com **apenas as seções — nunca o número da
   mesa**.
5. Mapa na entrada, apontando onde fica a seção do eleitor na parede específica.
6. As informações desta conversa modificam o plano de sinalização externa.
7. (Segunda rodada) Filas coladas no chão por número de seção — simular a
   melhor forma de colar, **sem que se cruzem** e com máxima clareza.

Regra de encaminhamento fixada pelo Posto: **porta A → parede oeste,
porta B → parede norte, porta C → parede leste.**

Esclarecimento dado pelo usuário na segunda rodada: **não se usará nenhuma
regra de condado nem de faixa numérica.** A regra é puramente espacial — o
eleitor entra, lê a lista, acha sua seção na parede.

---

## 2. Insumos

| Insumo | Onde está | Observação |
|---|---|---|
| Prancheta Hamad_Final | `scripts/plano_sinalizacao.py`, constante `PRANCHETA` | Veio colada no chat; não existia no repo. `id: hamad-final-20260913150300` |
| 51 seções / 28 urnas | `saidas/dados.json` | Já existia no repo |
| Planta do Hall 2 | `RDS_Hall_2_Floorplan_(1).pdf` | 50,2 × 44,5 m, 2.238 m² |
| Fluxo antigo (2 portas) | `PLANO COM FLUXOS MELHORADO.png` | **Superado** — tinha portas A e B na parede sul, não A/B/C |

Nada chamado "Ring 3" aparece no PDF do RDS. O termo foi tratado como nome
interno do cenário, não como sala diferente.

---

## 3. Como a prancheta foi decodificada

A prancheta traz 28 mesas com `x`, `y`, `rot` e `lado`. A leitura:

- `rot = 0` → parede **oeste** (x = 0,8), 9 mesas
- `rot = 270` → parede **norte** (y = 43,6), 9 mesas
- `rot = 180` → parede **leste** (x = 47,3), 10 mesas
- A parede **sul** (y = 0) fica livre — é onde estão as portas

**A chave dos pares está no campo `lado`:** duas mesas separadas por
**exatamente 3,90 m** e com os lados voltados uma para a outra compartilham o
corredor entre elas. Os vãos de 2,70–3,00 m são circulação entre blocos. Nas
paredes oeste e norte o par lê `(+1, −1)` no sentido crescente; na leste, que
está a 180°, a convenção de lado se inverte e o par lê `(−1, +1)`.

Resultado: **12 pares + 4 mesas isoladas = 16 blocos.** As quatro isoladas
(posições 19, 22, 23, 24) têm todas `lado = +1` e vãos simétricos de ~3 m dos
dois lados — são solteiras de propósito, não erro de desenho.

| Parede | Porta | Mesas | Pares | Isoladas | Blocos | Seções | Aptos | Compar. |
|---|---|---|---|---|---|---|---|---|
| Oeste | A | 9 | 4 | 1 | 5 | 17 | 6.146 | 4.179 |
| Norte | B | 9 | 4 | 1 | 5 | 17 | 5.412 | 3.662 |
| Leste | C | 10 | 4 | 2 | 6 | 17 | 5.236 | 3.575 |
| **Total** | | **28** | **12** | **4** | **16** | **51** | **16.794** | **11.416** |

Posição das portas (derivada, a confirmar): A em x ≈ 9, B em x ≈ 25,75,
C em x ≈ 41, todas em y = 0. A posição de B vem do maior vão livre da parede
norte fora dos pares (x 23,25–28,25), alinhado ao centro do salão (25,1 m).

---

## 4. A PREMISSA EM ABERTO — resolver antes de imprimir qualquer coisa

**O problema:** são duas listas que precisam ser costuradas.

- A **prancheta** sabe *onde* fica cada mesa (posições nº 1 a 28 com
  coordenadas) e não sabe *quem vota nela*.
- O **`dados.json`** sabe *quem vota em cada urna* (seções, eleitores) e não
  sabe *onde a urna fica*. Numera as urnas de 1 a 28 **por volume
  decrescente** — nº 1 é a urna de 797 eleitores, nº 28 a menor.

O único campo em comum é o número de 1 a 28. **Foi assumido que são a mesma
coisa:** prancheta nº 1 = urna maior. No código, `MAPA_MESA_URNA` em
`scripts/plano_sinalizacao.py`.

**Se a numeração da prancheta veio da ordem em que as mesas foram
arrastadas na tela, a premissa é falsa.** Nesse caso a estrutura continua
certa (16 blocos, 9/9/10, quais são pares) e **muda apenas qual lista de
seções vai em qual banner** — todos os 19 banners numéricos ficariam trocados,
e a reprovação das três posições de piso (seção 7) apontaria para as
posições erradas.

**Teste de uma pergunta:** na prancheta, a mesa nº 1 é a da seção 3313
(a maior, 797 eleitores)? Qualquer âncora resolve — "a mesa X é a da seção Y"
basta para reconstruir o resto.

**Como corrigir:** trocar o dicionário `MAPA_MESA_URNA` e rodar
`python3 scripts/plano_sinalizacao.py && python3 scripts/gera_pagina_sinalizacao.py`.
Documento, planta e tabelas se regeram sozinhos.

---
## 5. Arquitetura da sinalização — 25 peças em 4 níveis

Revisado em 15/09 por decisão do Posto: **N1 deixou de ser capa de barreira ao
longo da fila** (era 24 un) e virou uma peça única na boca de cada serpenteado
do Ring 3; **N4, o mapa de entrada, foi cortado**.

| Nível | Peça | Onde | Qtd | Altura de caractere |
|---|---|---|---|---|
| N1 | Painel de decisão A/B/C com as 51 seções | boca do serpenteado, Ring 3 | 3 | 250 mm (letra) · 80 mm (seção) |
| N2 | Totem alto de porta | dentro, 4,3 m da porta | 3 | 300 mm |
| N3 | Painel das seções da parede | dentro, 8,1 m da porta | 3 | 60 mm |
| N5 | Banner de bloco | boca do corredor do par | 16 | **120 mm** |

Alturas pela regra prática de 10 mm por metro de distância de leitura — regra
de projeto, **não** norma citável.

**Posição de N2 e N3**, em metros de planta (origem no canto sudoeste, portas
em y = 0). Ficam do lado oposto à curva que o eleitor faz ao entrar — A vira a
oeste, C vira a leste, B segue reto — para que quem para de ler não represe a
soleira. N2 vem antes porque responde uma pergunta binária lida em movimento;
N3 exige parar.

| Porta | N2 (x · y) | N3 (x · y) |
|---|---|---|
| A | 11,50 · 3,50 | 13,50 · 7,00 |
| B | 28,50 · 3,50 | 30,50 · 7,00 |
| C | 38,50 · 3,50 | 36,50 · 7,00 |

Nenhuma das seis posições cai sobre via de fila: a banda y < 4 m está livre de
ponta a ponta e a faixa y = 7 m só é ocupada junto às paredes.

**Regras de conteúdo (valem para todas as peças):**

- Nunca aparece número de mesa. Só número de seção.
- Seção sempre em **4 dígitos**, como no e-Título (`0511`, não `511`).
- Ordem crescente de seção, nunca ordem de mesa. **Exceção no N3:** os blocos
  vêm na ordem física da parede, e as seções em ordem crescente dentro de cada
  bloco.
- Cor por porta constante do primeiro ao último nível: A = ciano,
  B = magenta, C = âmbar (âmbar precisa ser escurecido — conferir contraste).
- Bilíngue só em N1 e N2. N3 e N5 são numéricos.
- Rodapé obrigatório do N3: *"não encontrou a sua? procure um mesário — sua
  seção está em outra porta."*

**O N3 mudou de formato porque o mapa saiu.** Sem o N4, o N3 é a única peça
que pode dizer *onde* na parede, e uma lista em ordem crescente não faz isso.
Passa a espelhar a parede: 5 ou 6 colunas, uma por bloco, da esquerda para a
direita na ordem física; cada coluna traz os mesmos números do banner N5 que o
eleitor vai encontrar lá na frente. Apaisado, mínimo 2,40 × 1,20 m.

**Risco aberto pela decisão do N1.** Com um único ponto de decisão em todo o
percurso, quem entra no serpenteado errado só descobre no N2, já dentro do
salão, e a correção custa refazer a fila inteira. Três atenuantes: (1) o N1
carrega as 51 seções, não as 17 de uma porta; (2) um orientador fixo na boca
de cada serpenteado, com a mesma lista em prancheta; (3) **recomendado, não
decidido** — um A-frame de repetição no meio de cada serpenteado, com o índice
das 51 seções, que dá uma segunda chance de correção sem reintroduzir a capa
de barreira.

---

## 6. Correção importante: a fila é por MESA, não por par

A primeira versão do plano previa uma fila por par, argumentando que as duas
mesas se revezariam no atendimento. **Está errado.** Cada mesa guarda o caderno
de votação das suas próprias seções — o eleitor da 3313 não pode ser atendido
na mesa vizinha, ainda que vazia. Não há substituição possível, logo não há
ganho de fila única.

**São 28 filas, não 16.** O banner continua sendo do par (as duas mesas se
distinguem pelas seções, não por número, então a instrução do Posto se
mantém). A fita no chão é que desce ao nível da mesa: dentro do corredor de
3,90 m do par, a via se bifurca, um ramo por conjunto de seções.

---

## 7. Simulação das filas e plano de colagem no piso

**Modelo:** determinístico por hora; comparecimento 74% Dublin / 50% interior;
perfil de chegada com pico matinal (12-15-16-14-11-9-8-8-7% por hora das 8h às
17h); 0,50 m por pessoa em fila simples; via de 1,00 m; 30% de folga.
**O perfil horário é a premissa mais frágil** — não há série histórica do Posto.

| Seg./voto | Pessoas em fila no pico | Mesas com fila | Via linear |
|---|---|---|---|
| 30 s | 0 | 0 | — |
| **60 s** | **592 (às 12h)** | **13 de 28** | **296 m** |
| 90 s | 2.191 (às 13h) | 28 de 28 | 1.095 m |

A 60 s a fila é muito concentrada: a mesa mediana não forma fila nenhuma e três
mesas sozinhas seguram ~300 pessoas. A 90 s, 1.095 m de via ocupariam cerca de
metade da área útil do salão — **nenhum plano de colagem resolve**. A colagem
é executada para 60 s, com o miolo do salão livre como transbordo.

### As cinco regras que garantem o não cruzamento (por construção)

1. Cada mesa é dona da faixa de piso à sua frente — tão larga quanto o vão até
   a mesa vizinha (2,0 a 3,9 m), tão profunda quanto sua fila exigir.
2. A faixa avança **perpendicular à sua própria parede**. Faixas paralelas
   saindo da mesma parede nunca se cruzam.
3. Nenhuma faixa alcança a parede oposta — a mais profunda tem 22 m num salão
   de 44,5 m; sobra miolo livre de ~14 m.
4. **Quadrado de canto de 8 m sem fila**, nos dois cantos norte.
5. Toda a circulação acontece no miolo livre; o eleitor entra na via **pela
   cauda**, onde fica o decalque com o número da seção. Não há corredor-tronco
   colado — o tronco é o próprio vazio.

Com isso as 28 vias são disjuntas por construção; não é preciso conferir
cruzamento caso a caso.

### Três posições da prancheta são reprovadas

| Mesa | Bloco | Seções | Precisa | Exigiria | Limite | Motivo |
|---|---|---|---|---|---|---|
| 2 | BB1 | 3322 / 3752 | 65 m | 22 m | 8 m | canto noroeste |
| 4 | BA4 | 3315 / 3778 | 64 m | 32 m | 22 m | vão de 2,75 m → só 2 vias |
| 3 | BC6 | 3142 / 1278 | 27 m | 9 m | 8 m | canto nordeste |

**Regra de projeto que sai daí: mesa pesada não vai para canto nem para vão
estreito.** As três mesas de ~590 comparecentes precisam de meio de parede com
vão de 3,9 m. Posições com folga e fila zero hoje — BB3 (norte, isolada),
BB2 (norte), BC1 (leste) — são destino natural. É troca na prancheta, custo
zero se feita antes de colar. *(Depende da premissa da seção 4.)*

### Quantitativo da colagem

- 16 slots de marca de início (via ≤ 6,5 m), 9 de via simples, 3 serpentinas
- **Via de fila projetada:** 489 m
- **Fita de piso:** 493 m — vinil antiderrapante 75 mm, na cor da porta
- **Decalques de seção:** 144 — 4 dígitos, altura 150 mm

---

## 8. Efeito no orçamento (item (d), separadores — EUR 1.303,00 / 100 un / 200 m)

A primeira versão do plano previa corredor-tronco de separador colado às três
paredes: 184,5 m dos 200 m, sem nada sobrar para a fila externa — era o único
item que estourava.

Com o vazio central assumindo o papel de tronco, o separador físico fica
reservado a três usos: (a) canais de aproximação externos das três portas,
(b) a bifurcação dentro do corredor de 3,90 m de cada par, (c) o reforço do
vão de 2,70 m entre BA3 e BA4. **Isso inverte o déficit.** Quanto exatamente
depende de quanto separador a fita substitui — pergunta para o fornecedor.

Item (c), banners — EUR 1.961,00 para 25 peças mais bases alugadas dá ~EUR 78
por peça. Era ~EUR 40 e apertado; o corte do mapa e a redução do N1 a três
painéis abriram folga. Ela deve ser gasta no N1, que virou a peça mais
crítica do plano.

---

## 9. O que a sinalização interna impõe à externa

A externa ainda não existe. Condições, não sugestões:

1. **A triagem acontece na boca do serpenteado do Ring 3, e em nenhum outro
   lugar** — decisão do Posto de 15/09. É o único ponto de decisão do
   percurso; ver o risco e os atenuantes na seção 5.
2. **O N1 carrega as 51 seções**, não as 17 de uma porta — como não há regra
   numérica nem por condado, é lista completa ou nada. Três colunas
   coloridas, A / B / C, em ordem crescente.
3. **Mesma paleta, mesma tipografia, mesmos 4 dígitos.** A cor com que o
   eleitor decidiu lá fora é a que ele procura lá dentro.
4. **Canal de prioridade** (idosos, gestantes, PcD) desembocando nas três
   portas, não numa só.
5. **Placa de chegada na Merrion Road** nomeando o Hall 2 (Shelbourne Hall).
   O RDS tem seis halls.

---

## 10. Pendências

1. **Confirmar a premissa da seção 4.** Bloqueia a impressão dos 19 banners
   numéricos e a validade da reprovação das três posições de piso.
2. Confirmar a posição real das portas na parede sul do Hall 2.
3. Trocar de posição, na prancheta, as três mesas pesadas que caem em canto ou
   vão estreito — antes de colar qualquer coisa.
4. Decidir entre mover blocos ou compensar com pessoal os 30% de
   desbalanceamento da porta A (464 comparecentes/mesa contra 358 na C, e a A
   ainda tem uma mesa a menos).
5. Definir com o fornecedor quanto de separador físico a fita substitui.
6. **Confirmar com o RDS se o contrato de locação admite fita e decalque no
   piso do Hall 2**, e em que condição de remoção. Alguns contratos de
   pavilhão proíbem.
7. Validar com o Cartório Eleitoral a realocação de mesários entre paredes a
   partir das 15h30 — a porta A vai terminar depois das outras duas.
8. Conferir se EUR 1.961,00 cobrem as 25 peças mais bases (~EUR 78 por peça,
   folgado onde antes era apertado). A folga deve ir para o N1, que virou a
   peça mais crítica do plano.
10. Decidir sobre o A-frame de repetição no meio do serpenteado (seção 5) —
    recomendado, ainda não decidido.
9. Medir o contraste do âmbar da porta C sobre branco antes de imprimir.

---

## 11. Arquivos e como regerar

| Arquivo | Papel |
|---|---|
| `scripts/plano_sinalizacao.py` | Prancheta, paredes, pares, conteúdo dos banners. **Falha em vez de gravar** se as 51 seções não aparecerem uma vez, se os aptos não somarem 16.794 ou se as 28 mesas não fecharem |
| `scripts/gera_pagina_sinalizacao.py` | Simulação de fila, dimensionamento dos slots de piso, página visual com as duas plantas em escala |
| `scripts/sinalizacao_template.html` | Template da página |
| `saidas/plano_sinalizacao_interna.md` | Documento completo |
| `saidas/plano_sinalizacao.html` | A mesma análise em página visual |
| `saidas/sinalizacao.json` | Saída estruturada (blocos + slots de piso) |

```bash
cd scripts
python3 plano_sinalizacao.py          # → saidas/sinalizacao.json
python3 gera_pagina_sinalizacao.py    # → saidas/plano_sinalizacao.html
```

- **Artifact:** https://claude.ai/artifact/BcT5yzxRkSaUsbbHQQgjWF
- **PR (rascunho):** https://github.com/hamadmkalaf/eleicoes2026/pull/20
- **Branch:** `claude/serene-rubin-tdzmlb`

---

## 12. Achados que valem para além da sinalização

- **Não existe regra numérica que leve o eleitor à porta certa.** As seções
  33xx de Dublin estão espalhadas: 3306/3307/3311/3313/3315 na porta A,
  3305/3309/3322 na B, 3302/3308 na C.
- **Nem o condado serve de atalho.** Cork aparece nas portas A e C, Limerick
  nas B e C, "outros locais da Irlanda" nas A e C.
- **A porta B é a única cujo destino não se vê da entrada** — ~44 m de
  travessia pelo miolo até a parede norte.
- **A colagem no piso é um teste físico da agregação.** A 90 s por voto o
  salão inteiro vira fila: o mesmo colapso que a simulação de agregação já
  apontava, agora medido em metros de piso. Serve de argumento junto ao TSE.
