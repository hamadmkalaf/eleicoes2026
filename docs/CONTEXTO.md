# Contexto do desenho de fluxo — posto de Dublin, 1º turno de 2026

Documento de passagem. Reúne tudo que já foi medido e calculado sobre o salão
de votação, para que uma sessão nova possa retomar sem refazer nada.

**Há uma ideia de layout no repositório: as mesas pareadas, encostadas nas
paredes e numa fileira recuada da fachada leste** (`scripts/mesas.py`, §11). As
duas anteriores — mesas em ilhas e mesas nas paredes — tinham sido apagadas a
pedido do usuário; esta é nova, foi desenhada sobre a planta-base e com o
mobiliário que o usuário informou depois. **As 28 MRVs cabem**, com folga.

**Decisões do Posto de 06/09/2026** (fonte única: `scripts/decisoes.py`):
entradas de eleitor **S4 (A), S5 (B) e S6 (C)**, saídas **S2 e S8**; o número
da mesa é o **MRV do DJE/TRE-DF** e não depende da posição; comparecimento
esperado pela **base B** (`scripts/comparecimento.py`, 11.499); mesas coloridas
por carga (vermelho as 3 maiores, amarelo médio, verde baixo). A planta-base, a
prancheta, o simulador, o Ring 3 e a sinalização leem essas decisões do mesmo
módulo.

**A planta-base é a referência do projeto.** Toda ideia, planta, peça de leitura
ou conversa com o RDS daqui em diante usa a numeração de portas do §3 — N1, N2,
L1 a L4, S1 a S9, O1, O2 e R1 — com o código do RDS entre parênteses quando o
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

A 1 está respondida pela planta das 28 MRVs (§11); a 2 e a 3 foram decididas
pelo Posto em 06/09/2026 durante o desenho do Ring 3: **três entradas, S4, S5 e
S6; saídas S2 e S8** (`scripts/decisoes.py`).

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
| **S2** | Sul | *sem código RDS* | 13,25 | 14,45 | 1,20 m | **emergência confirmada — sem recuo, porta permanece aberta** |
| **S3** | Sul | 2.7 | 17,22 | 18,47 | 1,25 m | a definir |
| **S4** | Sul | 2.5/2.6 | 19,10 | 25,03 | 5,93 m | a definir |
| **S5** | Sul | 2.4 | 25,32 | 31,25 | 5,93 m | a definir |
| **S6** | Sul | 2.2/2.3 | 31,54 | 37,47 | 5,93 m | a definir |
| **S7** | Sul | 2.1 | 38,09 | 39,36 | 1,27 m | a definir |
| **S8** | Sul | *sem código RDS* | 42,12 | 43,32 | 1,20 m | **emergência confirmada — sem recuo, porta permanece aberta** |
| **S9** | Sul | carga leste | 45,12 | 48,75 | 3,63 m | a definir |
| **O1** | Oeste | acesso Hall 1 | 36,80 | 38,50 | 1,70 m | a definir · leva ao Hall 1 |
| **O2** | Oeste | 2.10/2.11 | 19,36 | 22,43 | 3,07 m | a definir · único acesso aos WC |
| **R1** | Recorte | 2.8/2.9 | 3,00 | 6,50 | 3,50 m | a definir · fora das fachadas |

**"A definir" não é o mesmo que disponível.** Quer dizer que nada foi decidido
sobre a porta — nem que sirva ao público, nem que possa ficar aberta. Isso
inclui **S3 (2.7) e S7 (2.1)**: constam como EXIT na planta do RDS, mas seu
recuo nunca foi determinado — não confundir com S2 e S8 (§4), que são outras
portas.

**S2 e S8 não constam na planta do RDS.** São as saídas de emergência
confirmadas no local em 02/09/2026 — ver §4 — junto às portas de carga.
Posição e vão **são estimados** sobre fotos da fachada sul, ainda sem medição
no local: 1,20 m de vão, a cerca de 1,8 m de cada porta de carga.

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
| Comparecimento esperado | base B: taxa de 2022 por domicílio de origem de cada seção (`scripts/comparecimento.py`), 11.499 no total | decisão de 06/09/2026; substitui a binária 74% Dublin / 50% interior usada até então |
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
- **A fachada leste recebe MRVs numa fileira recuada**, decidido pelo usuário:
  o recuo de 3 m é **perpendicular à parede**, não lateral aos vãos. Uma
  **faixa protegida de 3 m corre a fachada inteira**, ligando as quatro saídas;
  a fileira começa logo depois dela, com **todas as mesas à mesma distância da
  parede**, e por isso os vãos deixam de recortá-la. O tráfego por L1 a L4 fica
  restringido e a faixa não recebe mobiliário nem fila.
- **Espaço entre pares: 1,00 a 1,50 m** (antes era fixo em 1,50). O corredor de
  dentro do par continua em 2,50 a 3,00 m.

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
- **S2 e S8 são saída de emergência confirmada, sem recuo.** Confirmado no
  local em 02/09/2026 pelo chefe de segurança do RDS, a partir de fotos da
  fachada sul: são portas pretas de sinalização verde, encostadas a cada porta
  de carga — **sem código na planta do RDS**, que não as registrava. Ficam
  **permanentemente abertas**, por isso dispensam o recuo de 3 m. Ver
  `salao.SEM_RECUO`. Posição e vão são estimados sobre a foto (§3), ainda sem
  medição no local.
  >  Correção de uma leitura anterior deste documento: a confirmação havia
  >  sido atribuída por engano a duas portas diferentes — as que hoje são S3
  >  (2.7) e S7 (2.1) —, mais afastadas das portas de carga do que as fotos
  >  mostravam. Essas duas continuam "a definir", como estavam antes.
- Para as saídas de emergência restantes fora da leste — **N1** (já fechada,
  então o recuo não teria efeito), **S3** (2.7), **S7** (2.1) e **R1** — **não
  foi determinado recuo nenhum**. A planta-base não desenha recuo nelas.

---

## 5. As 28 urnas — o essencial

**11.499 comparecentes esperados** de 16.794 aptos (base B). A distribuição
tem um degrau nítido, e é ela que dá as cores da prancheta:

- **3 urnas críticas (vermelhas): MRV 22 = 3313 (590), MRV 24 = 3322 (588),
  MRV 23 = 3315 (586).** São as únicas que somam **duas seções inteiras de
  Dublin**.
- **8 urnas de carga alta (amarelas): 466 a 518** (MRV 16 = 3302, 18 = 3306,
  11 = 3161, 15 = 3245, 17 = 3305, 9 = 3108, 10 = 3142, 21 = 3311). Sete delas
  são uma seção de Dublin somada a **um condado inteiro do interior** (Cork,
  Galway, Limerick…). São **4.213 eleitores que moram fora de Dublin** e vão
  viajar para votar — **chegam em rajada**, não diluídos ao longo do dia.
  Precisam de piso de fila desproporcional à média.
- **17 urnas abaixo de 425 (verdes)**, das quais 12 praticamente não formam
  fila.

> A premissa inicial da conversa era "4 MRVs com ~600 eleitores". Os dados
> mostram **3**, e o segundo grupo é um problema de *rajada*, não de volume.

---

## 6. O que realmente decide: o tempo de atendimento

Simulação em passos de 5 min sobre o perfil de chegada. Fila de pico **somada
nas 28 urnas**:

| s/eleitor | fila de pico somada | maior fila | urnas com fila > 10 | última a fechar |
|---|---|---|---|---|
| 45 s | 33 | 12 | 2 | 17h00 |
| 50 s | 114 | 32 | 3 | 17h00 |
| **55 s** | **261** | **57** | **7** | **17h20** |
| 60 s | 465 | 84 | 11 | 18h05 |
| 70 s | 968 | 136 | 15 | 19h35 |
| 90 s | 2.227 | 230 | 23 | 22h45 |

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

**A pergunta 1 do §1 está respondida: a planta com as 28 MRVs está desenhada**
(§11), com fileira recuada na fachada leste e folga cheia em todos os
corredores. As perguntas 2 e 3 — quantas entradas e quais portas — foram
decididas em 06/09/2026: entradas S4, S5 e S6, saídas S2 e S8. A fachada sul
continua livre de mesas, o que deixa os três vãos duplos para o eleitor. O
plano do Ring 3 (`saidas/plano_ring3.md`), o simulador e a sinalização já
trabalham com essa decisão; a atribuição de mesas a entradas está em
`scripts/decisoes.py`.

A base sobre a qual ela foi construída continua valendo: a planta-base (§3 e
`saidas/planta_base.html`), as premissas (§4), a carga das urnas (§5), a
simulação de fila (§6) e a capacidade de parede (§7).

O §7 **não foi refeito** com o mobiliário novo: ele mede o teto de parede com o
módulo de 2,80 m de frente, sem pareamento, e serve de comparação. O número que
vale para o mobiliário atual é o do §11.

---

## 9. Perguntas em aberto

Por ordem de retorno:

1. **As portas de carga S1 e S9 podem ficar abertas e travadas durante as nove
   horas, e a soleira serve para pedestre?** São os dois maiores vãos da fachada
   sul. Portas de carga costumam ser de enrolar e às vezes têm função
   corta-fogo. A resposta decide o que é possível fazer com a fachada sul.
   *Preço em mesas: zero* — o §11 mostrou que a fachada sul não entrega MRV de
   um jeito nem do outro. O que a resposta decide é por onde o eleitor entra. No
   cenário B os dois vestíbulos ainda colidem com zonas protegidas (§11).
2. **Quanto de caminho livre a saída do catering exige, e por onde ele chega até
   a N2?** Enquanto não estiver definido, a metade central da parede norte não
   pode ser ocupada com segurança.
3. **O recuo de 3 m vale para as saídas de emergência das outras paredes?**
   Determinado só para a leste, e agora também para S2 e S8 — que dispensam
   recuo, confirmado no local (§4). Seguem em aberto **S3** (2.7), **S7**
   (2.1) e **R1**; N1 não conta, já que permanece fechada. *Preço em mesas:
   zero, nos dois sentidos* — a fachada sul não entrega MRV nem que os três
   dispensem recuo (§11, "capacidade, que é maior"), porque as portas por si
   só já fragmentam a parede. Não afeta a fachada leste, cuja faixa de 3 m já
   está determinada.
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
   da fila? *Preço em mesas: zero desde que a fileira recuada entrou* — nenhuma
   MRV fica fora de parede ou de faixa protegida no layout atual. Vale a mesma pergunta para o RDS, que precisa
   aprovar a divisória exenta do §11 como montagem e como rota de fuga.
8. **O RDS aceita a faixa protegida contínua de 3 m na fachada leste, no lugar
   dos envelopes por porta?** É a premissa de que a fileira inteira depende —
   14 MRVs, quase metade do salão. Reserva 133 m² em vez de 108 m², e exige que
   a faixa fique vazia o dia inteiro, sem mobiliário, sem material de apoio e
   sem fila. Sem ela, a fachada leste volta a valer três mesas.
9. **Onde ficam as caixas de piso elétricas do Hall 2**, se houver? Decide se as
   urnas podem ficar longe das paredes sem canaleta atravessando corredor. A
   fileira recuada aperta a pergunta: as 14 urnas da fachada leste ficam a 3 m
   da parede, e a canaleta teria de atravessar justamente a faixa protegida.

---

## 10. Arquivos

| Arquivo | O que é |
|---|---|
| `scripts/salao.py` | **Núcleo:** geometria medida, as seis faces do salão (`FACES`), o Ring 3 (`RING3`, `ring3_rect()`), carga das urnas (via `comparecimento.py`), simulação de fila, cálculo de capacidade de parede. Rodando sozinho, imprime os cenários do §7. |
| `scripts/comparecimento.py` | **Fonte única do comparecimento esperado** (base B: taxa de 2022 por domicílio de origem). |
| `scripts/decisoes.py` + `gera_decisoes.py` | **Fonte única das decisões:** papéis das portas, numeração MRV do DJE, classes e cores de carga, atribuição das mesas às entradas do Ring 3 (quotas de `layout_ring3.py`). `gera_decisoes.py` grava `data/decisoes.json`. |
| `scripts/desenho.py` | Primitivas de desenho das plantas: escala, paleta, `px`, `rect`, `txt`, `cota`, e a folha de estilo comum das peças de leitura. |
| `scripts/planta_base.py` + `planta_base_template.html` | **Planta-base:** o salão vazio, as portas numeradas por fachada e o que já se sabe de cada uma. Grava `saidas/planta_base.svg` e `saidas/planta_base.html`. Fonte da numeração N/L/S/O. |
| `scripts/estilo_plano.css` | Folha de estilo das peças de leitura. |
| `scripts/mesas.py` | **Ideia 1 (§11):** módulo da MRV com o mobiliário novo, faixa protegida e fileira recuada da fachada leste, regras de bloqueio, empacotamento por face e divisórias exentas. Toda planta passa por `valida()` antes de ser gravada. |
| `scripts/planta_mesas.py` | Desenhos da ideia 1: o módulo cotado, a fachada leste de perto, as réguas de parede e as plantas de ocupação. Usa as primitivas de `desenho.py`. |
| `scripts/gera_mesas.py` + `mesas_template.html` | Grava `saidas/mesas.json`, os SVGs e `saidas/mesas.html`. |
| `scripts/gera_editor.py` + `editor_template.html` | Grava `saidas/editor_dados.json` e `saidas/editor.html`, a prancheta: arrastar (com seleção múltipla e cotas vivas), girar de 90 em 90, reparear ao corredor de 3,00 m com encosto a 1,50 m, **alinhar uma parede inteira**, **conferir a distância entre os pares**, medir distância, desfazer/refazer e salvar, apagar e exportar cenários. Não recalcula nada — consome as MRVs já validadas por `mesas.py`. |
| `scripts/cenarios.py` | **Fonte única da biblioteca de cenários**, lida pelos dois geradores. Junta `cenarios/` do checkout com `cenarios/` do branch `cenarios-hall2`. |
| `scripts/teste_prancheta.js` | Testa fora do navegador a geometria nova da prancheta — parede de encosto, alinhamento e pareamento — recortando os blocos puros do template e rodando contra `saidas/editor_dados.json`. `node scripts/teste_prancheta.js`. |
| `scripts/gera_simulador.py` + `simulador/` | Grava `saidas/simulador_fluxo.html`, o simulador de fluxo: premissas, simulação por eventos discretos eleitor a eleitor e relatório. Consome a base geométrica de `saidas/editor_dados.json` e a mesma biblioteca de cenários da prancheta. |
| `saidas/dados.json` | As 28 urnas apuradas (etapa anterior, não mexer). |

A planta-base está publicada em
<https://claude.ai/code/artifact/48817634-cbe1-426e-829f-5b5c674a688c>. Para
atualizá-la de outra sessão, publique passando essa URL em `url` — sem isso,
cria-se um artefato separado.

A peça da ideia 1 está publicada em
<https://claude.ai/code/artifact/8ea7b55b-ec3f-4dd4-baaf-7702c4d3fcce> e a
prancheta — a mesma planta manipulável, em escala — em
<https://claude.ai/code/artifact/f6a9b812-2b5e-4972-bb81-104b018e16b0>. O
simulador de fluxo está em
<https://claude.ai/code/artifact/f2fea148-f618-4d3d-aa63-b0653f4139bc>. Mesma
regra das outras: para atualizar de outra sessão, publique passando a URL em
`url`.

### As duas ferramentas de conferência da prancheta

**Alinhar à parede.** A mesa entra no salão a partir da parede em que está
encostada: a âncora `(x, y)` fica nessa parede e o giro aponta para dentro.
Então a parede sai do giro, sem precisar de campo novo, e a distância até ela
é a folga que sobrou quando a mesa foi puxada para dentro — outra coisa, e de
propósito, da leitura "urna à parede" do painel de seleção, que mede da urna
até a parede mais próxima em qualquer direção. Escolhida a parede, o campo
vem preenchido com a distância em que mais mesas já estão (ou com a da mesa
selecionada, quando há uma só); alinhar move as demais **só no eixo
perpendicular** — posição ao longo da parede, giro e lado dos mesários ficam
onde estavam. O recorte noroeste conta como parede: quem está dentro dele
mede até a quina, não até a borda do salão.

**Pares.** Duas mesas formam par quando se encaram através do corredor de
serviço: mesmo giro, mesma distância da parede, mesários de lados opostos e a
segunda caindo do lado para onde a primeira põe os seus. O pareamento é por
proximidade, não pela numeração — quem arrasta desfaz a ordem 1-2, 3-4 da
planta original, e o que importa é quem está de fato frente a frente. O
painel mede o corredor de cada par (alvo 3,00 m, mínimo 2,50 m) e a folga até
o par vizinho da mesma fileira (alvo 1,50 m, mínimo 1,00 m), lista as mesas
que ficaram sem par, e clicar numa linha seleciona o par na planta. Na planta
oficial dá 14 pares de 3,00 m e nenhuma mesa solta; no cenário `Hamad_3polos`
acusa o par 5–22 com 2,45 m, abaixo do mínimo.

**Os cenários salvos moram em `cenarios/`**, um arquivo `.json` por cenário,
lidos por `scripts/cenarios.py` — que junta a pasta do checkout com a pasta
do branch de dados `cenarios-hall2` (formato e por quê em
`cenarios/README.md`). Os **dois** geradores chamam esse módulo, e é essa a
correção do descasamento que existia: cada um tinha a sua cópia da leitura e
as duas olhavam só o branch de dados, então dois cenários que ficaram num
branch de trabalho apareciam na prancheta e não no simulador. A prancheta não
lê nada ao vivo —
a sandbox do artefato publicado bloqueia qualquer chamada de rede para fora
do próprio claude.ai, então nem GitHub nem qualquer outro serviço externo dá
para consultar em tempo real de dentro da página (só as capabilities do
claude.ai escapam disso, e usar a `db` de novo voltaria a prender o artefato
à organização, o que motivou essa troca).

O caminho tem três degraus, e os dois primeiros não dependem de ninguém.
**Salvar** guarda o cenário no `localStorage` daquele navegador e copia o
JSON — antes o botão só copiava, e o cenário sumia se ninguém o gravasse no
repositório. Na lista, cenário local tem **apagar** (some de vez) e cenário
da lista publicada tem **ocultar** (some só ali, porque tirá-lo de todo mundo
é republicar). **Copiar tudo p/ o simulador** põe a biblioteca inteira num
JSON só, que o `Carregar arranjo…` do simulador aceita de uma vez — é o que
leva cenário novo de uma página à outra sem esperar republicação. Não há
botão de baixar arquivo: a sandbox torna inerte qualquer download que a
própria página dispare, e a capability `downloads`, que resolveria isso, é
recusada em artefato compartilhado por link — a prancheta precisa continuar
compartilhável, então fica a área de transferência. Para o cenário entrar na
lista publicada, quem desenha manda o JSON (mensagem,
e-mail, colando numa conversa com o Claude) para quem publica a prancheta,
que roda
`python3 scripts/salva_cenario.py arquivo.json` (ou `-` para ler da entrada
padrão): o script grava o arquivo no branch `cenarios-hall2` sem tocar no
checkout local (usa um worktree temporário) e não pede nada além do JSON
colado. Só depois disso — `gera_editor.py` e `gera_simulador.py` leem a
biblioteca e a embutem **na hora de gerar e publicar** as páginas — o cenário
aparece para todo mundo; salvar sozinho não basta, é preciso pedir a
republicação das duas. Cada cenário grava só as mesas que
mudaram da planta oficial (`alteracoes`, por número da mesa) — não as 28 —,
o que mantém os arquivos pequenos e os diffs do git legíveis, e significa
que mesas não citadas acompanham a planta oficial se ela mudar depois.

(A primeira versão desse fluxo tentava abrir o GitHub com o commit pronto
para a própria pessoa confirmar — `.../new/cenarios-hall2?filename=...`.
Foi abandonada: exige conta no GitHub e um clique final em página externa
que ninguém sem experiência técnica completa de forma confiável — não dá
para saber, de dentro da prancheta, se aquele clique aconteceu. `Colar
cenário` na prancheta ainda aceita o link de um item da lista para abrir
localmente; a leitura do arquivo em si, por quem publica, é sempre pelo
`salva_cenario.py`.)

A prancheta não declara mais a capability `db`; o artefato volta a admitir
compartilhamento público.

```bash
cd scripts
python3 salao.py           # confere os dados e a capacidade de parede
python3 planta_base.py     # planta-base: salao vazio e portas numeradas
python3 mesas.py           # as 8 combinacoes da ideia 1, com validacao
python3 gera_mesas.py      # saidas/mesas.json, os SVGs e saidas/mesas.html
```

As duas páginas manipuláveis saem em sequência — a prancheta primeiro, porque
o simulador consome a geometria que ela grava — e cada uma tem o seu teste:

```bash
python3 scripts/gera_editor.py      # saidas/editor_dados.json e editor.html
python3 scripts/gera_simulador.py   # saidas/simulador_fluxo.html
node scripts/teste_prancheta.js     # parede de encosto, alinhamento, pares
node simulador/teste_modelo.js      # motor do simulador
node simulador/teste_arranjos.js    # leitura de arranjo da prancheta
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

### A fileira recuada da fachada leste

É a decisão que mudou a conta. Enquanto se tentou pôr as mesas **encostadas** na
fachada leste, cada um dos quatro vãos levava um envelope de 3 m para cada lado
e dos 44,40 m sobravam três pedaços de 2,79 m — nem um par cabia. Recuando a
fileira, a faixa de 3 m passa a correr a fachada inteira e os vãos deixam de
recortá-la: sobram **37,30 m contínuos**, que aceitam **7 pares — 14 MRVs**,
mais do que qualquer parede do salão.

A urna continua fazendo o que tem de fazer: voltada para a fachada, com o
eleitor entre ela e a faixa protegida, de modo que a tela aponte para a parede
e não seja vista do salão.

O que a faixa custa: **133 m² de piso** reservados, contra 108 m² dos quatro
envelopes somados. Sai mais barato porque o piso sobra e a frente não. Em troca
ela tem de ficar vazia o dia inteiro — sem mobiliário, sem material de apoio e
sem fila, inclusive a de quem já votou.

### A numeração

**O número da mesa é o MRV do DJE/TRE-DF** (decisão de 06/09/2026): MRV k é a
k-ésima seção principal em ordem crescente, e o número acompanha a mesa quando
ela é arrastada — a 22 é a 22 na parede norte, leste ou oeste. A **posição
inicial** de cada MRV na planta oficial é a do circuito de `mesas.numera_mrv()`,
horário a partir do canto noroeste: **1 a 8** na parede norte de oeste para
leste, **9 a 20** descendo a fileira recuada da fachada leste, **21 e 22** na
face norte do recorte e **23 a 28** subindo a parede oeste. Consequência: na
planta oficial as três mesas vermelhas (MRV 22, 23 e 24) caem juntas no canto
sudoeste; o cenário "Três polos" da prancheta as separa, e é o arranjo do
Cenário Claude do simulador.

### A planta final — 28 MRVs

**A planta entregue tem as 28 MRVs**, com a folga no topo das duas faixas:
3,00 m dentro do par e 1,50 m entre pares em toda a planta. Vale igual nos dois
cenários — a fachada sul não recebe mesa nenhuma, então a decisão sobre S1 e S9
não desloca nada.

| Face | MRVs |
|---|---|
| fileira recuada da fachada leste | **12** (6 pares em 38,4 m contínuos) |
| parede norte | **8** |
| parede oeste | **6** |
| face norte do recorte | **2** |
| fachada sul, parede leste encostada, face leste do recorte | zero |

Usa **84,0 m de frente**, entre parede encostada e fileira recuada.

### A capacidade, que é maior

O teste de capacidade que precedeu a planta: com a mesma folga cheia o salão
comporta **30**, e apertando até o mínimo da faixa dada (2,50 e 1,00), **34**.
As duas MRVs excedentes foram escolhidas **pelo usuário sobre o desenho**, e a
escolha está nomeada em `mesas.AJUSTE_28`, não escondida no empacotamento:

- sai o **par mais a leste da parede norte**, que se aproximava demais da
  fileira recuada no canto nordeste;
- o **par da face norte do recorte** é encostado à direita, liberando o canto
  sudoeste em vez de ficar no meio do trecho.

A fachada sul entra com zero em qualquer combinação de recuo — inclusive sem
recuo nenhum, isto é, mesmo que S3, S7 e R1 também dispensem (§9, pergunta 3).
Não é mais questão de recuo: as nove portas da fachada sul (§3) já fragmentam
os 42,5 m dela em trechos curtos demais para um par de 5,3 m, então
`mesas.AJUSTE_28["sul"]` hoje não remove posição nenhuma — fica no código como
trava, não como corte real, para o caso de a fachada sul voltar a caber
alguma coisa se a posição estimada de S2/S8 mudar depois de medida no local.

Passar `ajustes={}` devolve as 30; `a_min=CORREDOR_MIN`, as 34.

### Três achados

**A decisão sobre S1 e S9 não muda o número de mesas.** A fachada sul não
entrega MRV de um jeito nem do outro — e agora se sabe por quê com mais
precisão: não é (só) o recuo. As nove portas da fachada sul (§3, depois de
02/09/2026) somam quase 30 m de vão em 42,5 m de parede, e o que sobra vem em
pedaços curtos demais para um par de 5,3 m, mesmo nas contas sem recuo nenhum
(§9, pergunta 3). O que a decisão sobre S1 e S9 muda é por onde o eleitor
entra, e quanto chão os vestíbulos consomem.

**Apertar as folgas compra quatro mesas de que ninguém precisa.** Empacotando
pelo mínimo da faixa (2,50 no par, 1,00 entre pares) cabem 34; exigindo o máximo
(3,00 e 1,50), 30 — ainda duas acima das 28. O custo de apertar é concreto: o
mesário sentado ocupa 0,75 m de cada lado, então 3,00 m deixam 1,50 m de
passagem livre e o corredor de 2,67 m da fileira leste no empacotamento máximo
deixa 1,17 m — mão única, sem cruzamento e sem manobra de cadeira de rodas, no
mesmo corredor por onde sai quem já votou. **Adotar 3,00 m no par e 1,50 m entre
pares.**

**No cenário B, os dois vestíbulos caem dentro de zonas protegidas.** A
validação geométrica pegou: o vestíbulo de S9 invade a **faixa protegida da
fachada leste** em 4,9 m² — e é dela que a fileira inteira depende —, e o de S1
invade o recuo de **R1** em 6,0 m², se a porta 2.8/2.9 exigir os mesmos 3 m. Nos
dois casos a saída é encurtar a divisória ou afastá-la do canto.

### O plano B, se a faixa contínua não for aceita

Está no modelo, em `roda(..., faixa_leste=False)`: volta aos quatro envelopes
por porta na fachada leste. Aí ela vale **3 MRVs avulsas** — os três pedaços de
2,79 m entre os envelopes, uma mesa sozinha em cada, com 1,09 m de passagem — e
o salão cai para **21**, faltando 7. A resposta volta a ser a **divisória exenta**
de 11,1 m atravessada no miolo, que serve de parede pelas duas faces, acrescenta
8 e leva o salão a **29**. Apoia-se no que o §4 já registrava: o sigilo vem da
estrutura que fecha a urna, não da parede do prédio.

(Recalculado duas vezes em 02/09/2026, depois de S2/S8 entrarem na planta —
ver "capacidade, que é maior", acima: a fachada sul continua sem contribuir
nada aqui também, então os números não mudaram dos originais.)

É o que se perde se o RDS não aceitar a faixa — e é por isso que a questão 8 do
§9 é a mais importante das que restam.

Depende de duas aprovações que ainda não existem: a do RDS, como montagem e
rota de fuga, e a do Cartório Eleitoral, para seção fora da parede do prédio
(questão 7 do §9).

### Validação

Nenhuma planta é gravada sem passar por `mesas.valida()`: todo módulo tem de
caber no contorno do Hall 2, não invadir vão de porta nem recuo de emergência,
e não se sobrepor a outro módulo. `mesas.choques()` reporta à parte as reservas
que se pisam — foi assim que os dois conflitos do cenário B apareceram.
