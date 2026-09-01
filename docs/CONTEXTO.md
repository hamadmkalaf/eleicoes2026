# Contexto do desenho de fluxo — posto de Dublin, 1º turno de 2026

Documento de passagem. Reúne tudo que já foi medido e calculado sobre o salão
de votação, para que uma sessão nova possa retomar sem refazer nada.

**Há uma ideia de layout no repositório: as mesas pareadas nas paredes**
(`scripts/mesas.py`, §11). As duas anteriores — mesas em ilhas e mesas nas
paredes — tinham sido apagadas a pedido do usuário; esta é nova, foi desenhada
sobre a planta-base e com o mobiliário que o usuário informou depois, e o que
ela achou está no §11. Nenhuma porta recebeu papel de entrada ou de saída.

**A planta-base é a referência do projeto.** Toda ideia, planta, peça de leitura
ou conversa com o RDS daqui em diante usa a numeração de portas do §3 — N1, N2,
L1 a L4, S1 a S7, O1, O2 e R1 — com o código do RDS entre parênteses quando o
interlocutor for o RDS. A geometria vem de `scripts/salao.py` e de mais lugar
nenhum: não remeça o PDF. Se a planta-base mudar, ela é regerada e republicada
na mesma URL (§10), nunca copiada à mão.

---

## 1. O problema

Organizar o fluxo de eleitores no **RDS Ballsbridge, Hall 2**, em Dublin, no 1º
turno de 04/10/2026 (8h–17h). São **28 MRVs** (mesa receptora + urna) para
**16.794 eleitores aptos** em 51 seções. Três perguntas a responder:

1. Como distribuir as 28 MRVs pelo salão.
2. Quantas entradas.
3. Quais portas para entrada e quais para saída.

Nenhuma das três está respondida. A distinção entre porta de entrada e porta de
saída é decisão posterior e **não deve ser assumida** em nenhum material.

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

### Numeração das portas — usar esta, não a do RDS

O código do RDS numera folhas de porta e não localiza nada: a 2.16 fica na
parede leste, a 2.13 na norte, a 2.4 na sul. **A partir de agora cada porta tem
um número por fachada**, atribuído na ordem de leitura do desenho: de oeste
para leste nas paredes norte e sul, de norte para sul nas paredes leste e
oeste. A inicial é a da parede — N, L, S, O. A numeração é gerada por
`scripts/planta_base.py`, não escrita à mão.

### Portas (metros, medidos do canto oeste em paredes horizontais e do canto sul em verticais)

| Nº | Parede | Código RDS | De | Até | Largura | Estado |
|---|---|---|---|---|---|---|
| **N1** | Norte | 2.13 | 7,41 | 9,44 | 2,03 m | **fechada** |
| **N2** | Norte | 2.14/2.15 | 20,66 | 24,22 | 3,56 m | **desbloqueada — saída do catering** |
| **L1** | Leste | 2.16/2.17 | 38,51 | 41,57 | 3,06 m | emergência · recuo de 3 m |
| **L2** | Leste | 2.18/2.19 | 26,66 | 29,72 | 3,06 m | emergência · recuo de 3 m |
| **L3** | Leste | 2.20/2.21 | 14,80 | 17,87 | 3,07 m | emergência · recuo de 3 m |
| **L4** | Leste | 2.22/2.23 | 2,95 | 6,01 | 3,06 m | emergência · recuo de 3 m |
| **S1** | Sul | carga oeste | 7,83 | 11,45 | 3,62 m | a definir |
| **S2** | Sul | 2.7 | 17,22 | 18,47 | 1,25 m | a definir |
| **S3** | Sul | 2.5/2.6 | 19,10 | 25,03 | 5,93 m | a definir |
| **S4** | Sul | 2.4 | 25,32 | 31,25 | 5,93 m | a definir |
| **S5** | Sul | 2.2/2.3 | 31,54 | 37,47 | 5,93 m | a definir |
| **S6** | Sul | 2.1 | 38,09 | 39,36 | 1,27 m | a definir |
| **S7** | Sul | carga leste | 45,12 | 48,75 | 3,63 m | a definir |
| **O1** | Oeste | acesso Hall 1 | 36,80 | 38,50 | 1,70 m | a definir · leva ao Hall 1 |
| **O2** | Oeste | 2.10/2.11 | 19,36 | 22,43 | 3,07 m | a definir · único acesso aos WC |
| **R1** | Recorte | 2.8/2.9 | 3,00 | 6,50 | 3,50 m | a definir · fora das fachadas |

**"A definir" não é o mesmo que disponível.** Quer dizer que nada foi decidido
sobre a porta — nem que sirva ao público, nem que possa ficar aberta.

As portas de carga **não** aparecem rotuladas como EXIT na planta porque são
portas de *get-in* de feira. A largura bate com a ficha técnica, que registra a
porta principal de carga em **4,87 × 3,73 m**. As saídas 2.8/2.9 ficam na parede
do recorte sudoeste, medidas do PDF em 3,0 a 6,5 m a partir do canto sul; não
entram em `PORTAS` porque nenhuma parede do recorte recebe MRV, e só aparecem
desenhadas na planta-base.

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

### Mobiliário — atualizado pelo usuário

O usuário revisou o mobiliário depois da planta-base. **Vale esta versão**; a
anterior está registrada logo abaixo porque os números do §7 ainda vêm dela.

- **Mesa de identificação: 1,70 × 0,80 m**, para **três mesários** sentados no
  lado voltado ao corredor. É a primeira mesa da MRV.
- **Mesa de votação: redonda, Ø 0,90 m**, com a urna. É a segunda mesa, e
  **fica sempre encostada e voltada para a parede**; o eleitor vota de costas
  para o salão. O usuário acrescentou que **as urnas não podem ficar muito
  distantes das paredes**.
- **As MRVs andam em pares.** Os mesários de duas MRVs vizinhas ficam de frente
  uns para os outros, partilhando um corredor de **2,50 a 3,00 m** que serve ao
  mesmo tempo de encaminhamento para a urna e de saída de quem já votou. O par
  seguinte fica **de costas**, a **1,50 m**.

Disso sai o módulo que `scripts/mesas.py` usa: **0,90 m de frente × 4,10 m de
profundidade**, com passo de par de **5,80 a 6,30 m** de parede para duas MRVs.

> **Versão anterior, superada.** Mesa dos mesários de 1,60 × 0,70 m com a urna
> **ao lado**, num módulo de 2,80 m de frente × 1,90 m de profundidade, mais a
> estrutura que fecha o fundo e os lados da urna. Dela veio uma observação que
> continua valendo e que sustenta a proposta de divisória do §11: **o que
> importa é bloquear a face para onde aponta a tela — o sigilo vem da
> estrutura, não da parede do prédio.** As constantes `MOD_LARGURA` e
> `MOD_PROFUND` de `salao.py` ainda são as dessa versão, e é com elas que o §7
> está calculado.

### Restrições conhecidas (informadas pelo usuário)

- **Parede leste: todas as portas são saídas de emergência**, e exige-se
  **3 m livres** em torno de cada uma. O recuo é medido para dentro do salão e
  para os lados de cada vão, e está desenhado na planta-base. Consome quase toda
  a parede: sobram três trechos de 2,79 m entre os recuos.
- **N1 permanece fechada.** Não conta como vão para nenhum efeito.
- **N2 fica desbloqueada — é a saída do catering.** Precisa de caminho livre até
  ela; quanto de caminho ainda não foi definido.
- Para as saídas de emergência das outras paredes (N1, S2, S6, R1) **não foi
  determinado recuo nenhum**. A planta-base não desenha recuo fora da leste.

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

## 7. Capacidade de parede — quanto perímetro existe

Quantas MRVs cabem encostadas nas paredes, respeitando os recuos e descontando
os cantos (1,5 m). É uma medição, não uma proposta: serve para saber o teto de
qualquer arranjo que queira usar parede. Rode `python3 scripts/salao.py` para
reproduzir.

| Cenário | Parede livre | Posições de 28 |
|---|---|---|
| Recuo de 3 m **só na parede leste**, como está determinado · módulo de 2,80 m | 74,9 m | 19 |
| Idem, com módulo **em linha** de 1,80 m de frente | 74,9 m | 29 |
| Recuo de 3 m em **todas** as saídas de emergência · módulo de 2,80 m | 55,7 m | 11 |
| Idem, com módulo em linha | 55,7 m | 21 |

A parede leste desaparece de qualquer cenário: cada trecho livre entre os
recuos mede **2,79 m**, um centímetro a menos que o módulo de 2,80 m.

Duas ressalvas, as duas importantes:

1. **Contar posições pela frente mínima subestima a exigência.** A MRV que forma
   fila precisa de baia, e a baia é tão larga quanto a fila pedir na
   profundidade disponível: a 55 s, cada urna crítica pede de 9,8 a 10,1 m de
   frente. Somadas, as 28 baias exigiriam cerca de 81 m — mais do que existe em
   qualquer cenário da tabela.
2. **O módulo em linha ainda é hipótese.** Depende de a urna poder ficar atrás
   da mesa dos mesários em vez de ao lado; ver §9.

Trechos aproveitáveis com o recuo só na leste, medidos parede a parede:

| Parede | De | Até | Comprimento |
|---|---|---|---|
| Norte | 1,50 | 6,81 | 5,31 m |
| Norte | 10,04 | 20,06 | 10,02 m |
| Norte | 24,82 | 48,80 | 23,98 m |
| Oeste | 8,50 | 18,76 | 10,26 m |
| Oeste | 23,03 | 36,20 | 13,17 m |
| Oeste | 39,10 | 42,90 | 3,80 m |
| Leste | 9,01 | 11,80 | 2,79 m |
| Leste | 20,87 | 23,66 | 2,79 m |
| Leste | 32,72 | 35,51 | 2,79 m |

O trecho de 23,98 m na parede norte **inclui a frente da N2**, que é a saída do
catering e precisa ficar livre. Enquanto o caminho do catering não estiver
definido, esse trecho não pode ser contado inteiro.

---

## 8. Estado do projeto

**Uma ideia desenhada: as mesas pareadas nas paredes (§11).** Responde à
pergunta 1 do §1 — como distribuir as 28 MRVs — e descobriu que, com o
mobiliário novo e a regra de pareamento, **elas não cabem todas nas paredes do
salão**. As perguntas 2 e 3 do §1, quantas entradas e quais portas, continuam
sem resposta e nada nesta ideia as antecipa.

A base sobre a qual ela foi construída continua valendo: a planta-base (§3 e
`saidas/planta_base.html`), as premissas (§4), a carga das urnas (§5), a
simulação de fila (§6) e a capacidade de parede (§7).

O §7 **não foi refeito** com o mobiliário novo: ele mede o teto de parede com o
módulo de 2,80 m de frente, sem pareamento, e serve de comparação. O número que
vale para o mobiliário atual é o do §11.

---

## 9. Perguntas em aberto

Por ordem de retorno:

1. **As portas de carga S1 e S7 podem ficar abertas e travadas durante as nove
   horas, e a soleira serve para pedestre?** São os dois maiores vãos da fachada
   sul. Portas de carga costumam ser de enrolar e às vezes têm função
   corta-fogo. A resposta decide o que é possível fazer com a fachada sul.
   *Preço em mesas: zero* — o §11 mostrou que a fachada sul não entrega MRV de
   um jeito nem do outro. O que a resposta decide é por onde o eleitor entra.
2. **Quanto de caminho livre a saída do catering exige, e por onde ele chega até
   a N2?** Enquanto não estiver definido, a metade central da parede norte não
   pode ser ocupada com segurança.
3. **O recuo de 3 m vale para as saídas de emergência das outras paredes?** Está
   determinado só para a leste. N1, S2, S6 e R1 também são saídas de emergência
   na planta do RDS; se exigirem o mesmo, some parede no norte e no sul.
   *Preço em mesas: quatro* — é a única variável do modelo do §11 que muda o
   número, e só no cenário com S1 e S7 fora de uso.
4. **A urna pode ficar atrás da mesa dos mesários** (módulo em linha, ~1,80 m de
   frente por 2,60 m de profundidade) em vez de ao lado? Muda a capacidade de
   parede de 19 para 29 posições.
5. **Qual o método de identificação do eleitor** — biométrico, eletrônico ou
   caderno físico? Põe o posto em 45, 55 ou 90 s por eleitor e decide o tamanho
   de toda a área de fila (§6).
6. **A triagem será humana ou por sinalização?** Se depender de conferência
   verbal na entrada, vira gargalo não paralelizável.
7. **O Cartório Eleitoral valida seções fora das paredes** (mesas em ilha) e um
   setor reforçado, com quatro mesários e conferência de documento feita dentro
   da fila? *Preço em mesas: dez* — é a diferença entre as 18 que cabem na
   parede e as 28 exigidas. Vale a mesma pergunta para o RDS, que precisa
   aprovar a divisória exenta do §11 como montagem e como rota de fuga.
8. **Onde ficam as caixas de piso elétricas do Hall 2**, se houver? Decide se as
   urnas podem ficar longe das paredes sem canaleta atravessando corredor. A
   divisória do §11 torna a pergunta decisiva: as mesas da ilha ficam a mais de
   15 m de qualquer parede.

---

## 10. Arquivos

| Arquivo | O que é |
|---|---|
| `scripts/salao.py` | **Núcleo:** geometria medida, as seis faces do salão (`FACES`), premissas, carga das urnas, simulação de fila, cálculo de capacidade de parede. Rodando sozinho, imprime os cenários do §7. |
| `scripts/desenho.py` | Primitivas de desenho das plantas: escala, paleta, `px`, `rect`, `txt`, `cota`, e a folha de estilo comum das peças de leitura. |
| `scripts/planta_base.py` + `planta_base_template.html` | **Planta-base:** o salão vazio, as portas numeradas por fachada e o que já se sabe de cada uma. Grava `saidas/planta_base.svg` e `saidas/planta_base.html`. Fonte da numeração N/L/S/O. |
| `scripts/estilo_plano.css` | Folha de estilo das peças de leitura. |
| `scripts/mesas.py` | **Ideia 1 (§11):** módulo da MRV com o mobiliário novo, regras de bloqueio, empacotamento por face e divisórias exentas. Toda planta passa por `valida()` antes de ser gravada. |
| `scripts/planta_mesas.py` | Desenhos da ideia 1: o módulo cotado, as réguas de parede e as plantas de ocupação. Usa as primitivas de `desenho.py`. |
| `scripts/gera_mesas.py` + `mesas_template.html` | Grava `saidas/mesas.json`, os seis SVGs e `saidas/mesas.html`. |
| `saidas/dados.json` | As 28 urnas apuradas (etapa anterior, não mexer). |

A planta-base está publicada em
<https://claude.ai/code/artifact/48817634-cbe1-426e-829f-5b5c674a688c>. Para
atualizá-la de outra sessão, publique passando essa URL em `url` — sem isso,
cria-se um artefato separado.

A peça da ideia 1 está publicada em
<https://claude.ai/code/artifact/8ea7b55b-ec3f-4dd4-baaf-7702c4d3fcce>. Mesma
regra: para atualizá-la de outra sessão, publique passando essa URL em `url`.

```bash
cd scripts
python3 salao.py           # confere os dados e a capacidade de parede
python3 planta_base.py     # planta-base: salao vazio e portas numeradas
python3 mesas.py           # as 8 combinacoes da ideia 1, com validacao
python3 gera_mesas.py      # saidas/mesas.json, os SVGs e saidas/mesas.html
```

---

## 11. Ideia 1 — as mesas pareadas nas paredes

Desenhada com o mobiliário do §4 atualizado e a regra de pareamento que o
usuário descreveu. Roda em `scripts/mesas.py`; a peça de leitura é
`saidas/mesas.html`.

### O módulo

O eleitor entra pelo corredor, percorre o lado longo de 1,70 m da mesa de
identificação — três mesários sentados desse lado —, segue até a mesa de
votação encostada na parede, vota de costas para o salão e volta pelo mesmo
corredor. O eixo do módulo é **perpendicular à parede**:

| Trecho, a partir da parede | m |
|---|---|
| eleitor votando, entre a urna e a parede | 0,90 |
| mesa de votação, Ø 0,90 | 0,90 |
| passagem entre as duas mesas | 0,60 |
| mesa de identificação, 1,70 no eixo | 1,70 |
| **profundidade total** | **4,10** |

Frente: **0,90 m** — a mesa de votação, que é o elemento mais largo. Passo do
par ao longo da parede: `0,90 + A + 0,90 + 1,50`, com A o corredor. Dá **5,80 m**
(A = 2,50) a **6,30 m** (A = 3,00), ou **2,90 a 3,15 m de parede por urna**.

As três cotas de profundidade **são premissas deste modelo**, não medidas
verificadas: 0,90 m para o eleitor junto à parede, 0,60 m de passagem, 0,75 m
de assento do mesário projetado no corredor. Estão explícitas para poderem ser
corrigidas.

### Resultado

**Cabem 18 das 28 MRVs**, nos dois cenários pedidos pelo usuário. O gargalo é
parede, não piso: 28 urnas pedem 81 a 88 m de parede útil, e o salão oferece
**47,7 m**. De 189,4 m de perímetro, 53,7 m são vão de porta; os recuos de 3 m
comem a parede leste inteira e quase toda a fachada sul; e o que sobra vem em
pedaços curtos demais para um par — 78,6 m de parede livre viram 47,7 m de
parede útil.

| | S1 e S7 fora de uso | S1 e S7 em uso, divisória a 2 m |
|---|---|---|
| Máximo em parede real | **18** | **18** |
| Com uma divisória exenta de 17,4 m no miolo | **30** | **30** |
| Se só a parede leste exigir recuo de 3 m | **22** | **18** |

Distribuição das 18: 10 na parede norte, 6 na oeste, 2 na face norte do
recorte. Fachada sul e parede leste entregam **zero**.

### Três achados

**A decisão sobre S1 e S7 não muda o número de mesas.** A fachada sul não
entrega MRV de um jeito nem do outro — as sete portas somam 27,6 m de vão e os
recuos de S2 e S6 fecham o resto. O que a decisão muda é por onde o eleitor
entra, e quanto chão os vestíbulos consomem.

**Corredor de 2,50 m não compra mesa nenhuma.** Nas oito combinações de cenário,
hipótese de recuo e corredor mínimo, 2,50 e 3,00 m dão o mesmo número — a
fragmentação da parede é grosseira demais para 50 cm por par fazerem diferença.
E o custo de apertar é concreto: o mesário sentado ocupa 0,75 m de cada lado,
então com 3,00 m sobra 1,50 m de passagem livre e com 2,50 m sobra 1,00 m —
fila de mão única, sem cruzamento e sem manobra de cadeira de rodas, no mesmo
corredor por onde sai quem já votou. **Adotar 3,00 m.**

**No cenário B, os dois vestíbulos caem dentro de recuos de emergência.** A
validação geométrica pegou: o vestíbulo de S7 invade o recuo de **L4** em
4,9 m² — e o da parede leste é o único recuo já determinado —, e o de S1 invade
o de **R1** em 6,0 m², se a porta 2.8/2.9 exigir os mesmos 3 m. Nos dois casos a
saída é encurtar a divisória ou afastá-la do canto.

### O que fecha a conta

Uma **divisória exenta** de 17,4 m atravessada no miolo serve de parede pelas
duas faces e acrescenta 12 mesas, levando o salão a **30** — duas acima das 28.
A ilha ocupa 8,30 m de profundidade e guarda 3 m livres em toda a volta.
Apoia-se no que o §4 já registrava: o sigilo vem da estrutura que fecha a urna,
não da parede do prédio. Loteando o miolo, o teto vai a **74 mesas com 4
divisórias** — ou seja, a partir daí a restrição deixa de ser capacidade e passa
a ser fluxo.

Depende de duas aprovações que ainda não existem: a do RDS, como montagem e
rota de fuga, e a do Cartório Eleitoral, para seção fora da parede do prédio
(questão 7 do §9).

### Validação

Nenhuma planta é gravada sem passar por `mesas.valida()`: todo módulo tem de
caber no contorno do Hall 2, não invadir vão de porta nem recuo de emergência,
e não se sobrepor a outro módulo. `mesas.choques()` reporta à parte as reservas
que se pisam — foi assim que os dois conflitos do cenário B apareceram.
