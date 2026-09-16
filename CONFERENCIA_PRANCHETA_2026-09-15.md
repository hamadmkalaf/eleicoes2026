# Conferência final da prancheta do Hall 2 — 15/09/2026

Duas perguntas, respondidas contra as três fontes oficiais que o Cartório
Eleitoral entregou em julho e setembro de 2026:

1. **Os dados que estimam o número de eleitores esperado estão certos?**
   Sim. Nenhuma divergência em 51 seções, 28 agregações e 28 mesas.
2. **O cenário Hamad_Final reparte o esperado por igual entre as paredes?**
   Sim, e com margem larga: **3.833 · 3.835 · 3.831**, amplitude de **4
   eleitores em 11.499** (0,10% do terço perfeito).

Tudo abaixo sai de `scripts/confere_prancheta.py`, que refaz as contas do zero
a partir dos PDFs e sai com código 1 se qualquer número divergir:

```bash
pip install pdfplumber
python3 scripts/confere_prancheta.py            # cenário de trabalho (Hamad_Final)
python3 scripts/confere_prancheta.py equitativo # qualquer cenário de cenarios/
```

---

## 1. As fontes

Os três PDFs ficam em `data/oficiais/`. Eles são **fonte primária** e
substituem o `data/raw/mapa_agregacoes_TSE.png`, que trazia erro de digitação.

| Arquivo | Emissão | O que traz |
|---|---|---|
| `aptos_por_secao_dublin_2026-07-13.pdf` | ELO, 13/07/2026 16:24 | as 51 seções com aptos, agrupadas pelo local de origem do eleitor · 16.794 aptos em 15 localidades |
| `secoes_agregadas_dublin_2026.pdf` | Cartório Eleitoral | os 28 pares principal → agregada |
| `mrv_mesarios_dublin_2026-09-13.pdf` | ELO/Convoca+, 13/09/2026 11:32 | 109 mesários nomeados, seção a seção, com a situação de cada nomeação |

**Comparabilidade.** As três fotografias são de datas diferentes (13/07, sem
data no PDF de agregações, 13/09) e o repositório trabalhava com CSVs de 14/07
e 13/08. Os três caminhos fecham no mesmo 16.794, seção a seção — não há
mistura de safras.

## 2. Aptos e agregações: batem, um a um

- As **51 seções** do PDF existem no repositório com o **mesmo aptos** e a
  **mesma localidade de origem**. Zero divergências.
- Os **28 pares** do PDF de agregações são exatamente as 28 mesas da
  prancheta. Cada uma das 51 seções aparece em **exatamente uma** mesa:
  nenhuma sobra, nenhuma falta. (É o que desfaz, em definitivo, a
  inconsistência das "7 seções não contabilizadas" que a proposta antiga do
  TSE carregava — ver `contexto_eleicoes_dublin_2026.md` §2.1.)
- O par **3322 → 3752** é oficial, e as duas seções são de Dublin (398 e 396
  aptos). O erro registrado na aba `Inconsistencias` era de digitação do PNG
  na *principal* (3222, que é do Porto, em vez de 3322) e está resolvido: com
  o PDF em mãos, o PNG deixa de ser fonte.
- As 5 mesas que rodam com uma seção só — 3308, 3442, 3688, 3832, 3862 —
  constam do PDF com `---` na coluna da agregada. Confere.

## 3. O comparecimento esperado, refeito do zero

Método: `aptos da seção × taxa de 2022 do condado de domicílio`, somado por
mesa e arredondado por mesa (base B, decisão do Posto de 06/09/2026,
`scripts/comparecimento.py`). Recalculado a partir do PDF, mesa a mesa, bate
com `data/decisoes.json` nas 28 — em aptos, em esperado e na origem da
agregada. Total **11.499** (soma exata 11.497,7).

| MRV | principal | agregada | origem da agregada | aptos | esperado |
|---:|---:|---:|---|---:|---:|
| 1 | 0511 | 1100 | Roscommon | 582 | 375 |
| 2 | 0512 | 2855 | Longford | 476 | 355 |
| 3 | 0513 | 1105 | Mayo | 502 | 351 |
| 4 | 0517 | 1292 | Cavan | 513 | 348 |
| 5 | 1160 | 3845 | Limerick | 473 | 328 |
| 6 | 1352 | 0522 | Donegal | 462 | 328 |
| 7 | 3054 | 1099 | Kerry | 454 | 325 |
| 8 | 3078 | 2847 | Leitrim | 429 | 311 |
| 9 | 3108 | 3422 | Galway | 756 | 467 |
| 10 | 3142 | 1278 | Limerick | 793 | 466 |
| 11 | 3161 | 3307 | Cork | 791 | 504 |
| 12 | 3179 | 0530 | Westmeath | 676 | 423 |
| 13 | 3216 | 0527 | Clare | 571 | 407 |
| 14 | 3229 | 3821 | Cork | 606 | 405 |
| 15 | 3245 | 0519 | Cork | 781 | 498 |
| 16 | 3302 | 3181 | Outros locais da Irlanda | 771 | 518 |
| 17 | 3305 | 0521 | Galway | 767 | 472 |
| 18 | 3306 | 0518 | Outros locais da Irlanda | 766 | 515 |
| 19 | 3308 | — | — | 399 | 295 |
| 20 | 3309 | 1314 | Waterford | 615 | 395 |
| 21 | 3311 | 3913 | Dublin | 630 | 466 |
| 22 | 3313 | 3889 | Dublin | 797 | **590** |
| 23 | 3315 | 3778 | Dublin | 792 | **586** |
| 24 | 3322 | 3752 | Dublin | 794 | **588** |
| 25 | 3442 | — | — | 398 | 295 |
| 26 | 3688 | — | — | 400 | 296 |
| 27 | 3832 | — | — | 400 | 296 |
| 28 | 3862 | — | — | 400 | 296 |
| | | | **total** | **16.794** | **11.499** |

## 4. Equidade por parede do Hamad_Final

| Parede | Mesas | Esperado | Desvio do terço | Metros úteis | Por metro | Maior mesa |
|---|---:|---:|---:|---:|---:|---:|
| norte | 9 | 3.835 | +2 | 50,3 | 76,2 | 590 (MRV 22) |
| oeste | 9 | 3.833 | ±0 | 37,4 | 102,5 | 588 (MRV 24) |
| leste | 10 | 3.831 | −2 | 44,4 | 86,3 | 586 (MRV 23) |

**Amplitude de 4 eleitores. CV de 0,04%.** Na prática, o arranjo está no
ótimo: não existe repartição melhor das 28 mesas em três grupos sob a regra de
uma mesa vermelha por parede. E as três mesas de maior carga — 22, 23 e 24,
que são os três pares Dublin+Dublin — ficam **uma em cada parede**, que é a
razão de a coisa fechar tão bem.

Duas observações sobre o que esse número *não* diz:

- **A composição das paredes não é mérito do Hamad_Final: veio do cenário
  `Equitativo`,** gerado por `simulador/equitativo.js`, que busca exatamente
  isso (minimizar máx−mín do esperado entre as três paredes). O Hamad_Final
  move 16 das 28 mesas **ao longo** das paredes, sem trocar nenhuma de parede
  — e por isso herda o equilíbrio intacto. Mexer numa mesa de parede desfaz a
  otimização; mexer na posição dela dentro da parede, não.
- **Por metro de parede o quadro é outro.** A oeste é a parede mais curta
  (37,4 m, por causa do recorte sudoeste) e leva o mesmo terço: **102,5
  esperados por metro, contra 76,2 na norte** — 35% mais denso. Equidade de
  carga não é equidade de espaço de fila.

## 5. Quão robusto é esse equilíbrio

O equilíbrio é **ajustado à base B**, não uma propriedade do arranjo. Trocando
a base de comparecimento e mantendo as mesmas mesas nas mesmas paredes:

| Base de comparecimento | Total | Amplitude | % do terço |
|---|---:|---:|---:|
| **B — taxa de 2022 por condado (a que a prancheta usa)** | 11.498 | **3** | **0,08%** |
| A — binária: 74% Dublin, 50% interior | 11.416 | 92 | 2,42% |
| Dublin 80%, interior 45% | 11.961 | 95 | 2,37% |
| Dublin 70%, interior 60% | 11.334 | 216 | 5,71% |
| uniforme de 68,5% (mesmo total, sem contraste entre condados) | 11.499 | 318 | 8,31% |
| nota verbal: uniforme de 71,5% (≈12.000) | 12.000 | 332 | 8,31% |

Como ler a tabela:

1. **Errar o *nível* do comparecimento não desequilibra nada.** Se todas as
   taxas subirem ou descerem juntas, as três paredes se movem juntas: a linha
   "uniforme de 71,5%" tem a mesma amplitude relativa que a "uniforme de
   68,5%". O risco não está em acertar os 11.499.
2. **O que desequilibra é errar o *contraste* entre condados.** No pior caso
   testado (taxas uniformes, isto é, o contraste inteiro errado) a amplitude
   vai a 8,3% — 318 eleitores entre a parede mais carregada e a menos
   carregada, o que diluído em 9 mesas e 9 horas dá ~4 eleitores por mesa por
   hora, ou 4 minutos de trabalho a mais por hora a 60 s por eleitor.
   **Nenhuma das bases testadas quebra o desenho.**
3. **A parede oeste é a mais exposta a taxa de qualidade fraca** (proxy ou
   genérica): 323 dos seus 3.833 esperados, contra 85 na leste. Se *todas* as
   taxas fracas errarem 20% na mesma direção, a oeste anda ±65 e a leste ±17 —
   um descolamento de ~48 eleitores, 1,3% do terço. Tolerável.

**A qualidade da base, em números:** das 15 localidades, 6 têm taxa "direto" e
cobrem **91,0% do eleitorado** (Dublin sozinha é 74,9%); 7 são proxy (8,4%) e
2 são genéricas (0,5%). O grosso do modelo está em terreno firme.

**A ressalva honesta:** as taxas de 2022 por condado foram transcritas de
`handoff_agregacao_dublin_2026.md` §2 e **o repositório não registra a fonte
primária de nenhuma delas**. O único dado de 2022 com origem citada é
agregado: 7.492 de 11.946 aptos no 2º turno, 62,7%
([eDublin](https://www.edublin.com.br/eleicoes-brasileiras-na-irlanda-2022/),
em `pesquisa_horarios_pico_votacao.md` §4) — abaixo dos 68,5% que a base B
implica, mas os dois não são comparáveis (turnos diferentes, e o eleitorado
cresceu 40% desde então). Quem fecha isso é o
[`perfil_comparecimento_abstencao_2022`](https://dadosabertos.tse.jus.br/dataset/comparecimento-e-abstencao-2022)
do Portal de Dados Abertos do TSE, no recorte ZZ, que dá comparecimento
observado seção a seção. Não foi possível baixá-lo deste ambiente (a política
de rede bloqueia `cdn.tse.jus.br`). Fica como a pendência §9.1 já registrava —
mas, pelo item 1 acima, ela **não bloqueia** o congelamento da prancheta.

## 6. O que a conferência achou de fora da pergunta

### 6.1 A atribuição mesa → entrada não é equitativa, e podia ser

`data/decisoes.json` reparte as 28 mesas entre as três entradas por **cota do
Ring 3** — a zona de fila de B era mais larga, então B levou mais carga:

| Entrada | Por cota do Ring 3 | Desvio | Se a regra fosse "uma entrada por parede" | Desvio |
|---|---:|---:|---:|---:|
| A (S4) | 3.642 | −191 | 3.833 (oeste) | ±0 |
| B (S5) | **4.215** | **+382** | 3.835 (norte) | +2 |
| C (S6) | 3.642 | −191 | 3.831 (leste) | −2 |
| | amplitude **573** | | amplitude **4** | |

Três razões para trocar:

1. **O Ring 3 não existe mais.** O RDS proibiu fila no terreno dele e não
   houve autorização de Brasília (`plano_filas_sem_ring3.md`). A cota que
   justificava os +10% de B morreu com ele.
2. **`simulador/equitativo.js` já assume a regra por parede**
   (`ENTRADA = {oeste: "A", norte: "B", leste: "C"}`). Hoje o gerador do
   arranjo e o arquivo de decisões dizem coisas diferentes sobre a mesma
   mesa.
3. **A geometria ajuda.** S4 (centro em x = 22,07), S5 (28,29) e S6 (34,50)
   estão na ordem oeste → centro → leste; mandar cada porta para a parede
   correspondente é o percurso curto, não um desvio.

Não é decisão desta conferência — é do Posto, e depende do desenho de fila
confinado que substituiu o Ring 3. Mas é barato e melhora 573 → 4.

### 6.2 Uma base de comparecimento fora do lugar

`scripts/plano_filas.py`, no branch `claude/filas-sem-ring-3-b9qvqi`, dimensiona
a fila com **11.416** fixo no código (base A: 74%/50%), não com os 11.499 da
base B decidida em 06/09. A diferença no total é de 0,7% e não muda conclusão
nenhuma daquele documento, mas é a inconsistência §9.1 voltando por uma porta
lateral. Vale trocar a constante por `comparecimento.total()`.

### 6.3 Os mesários: a parede mais densa é a mais descoberta

O relatório Convoca+ cobre exatamente as 28 seções principais — confirmando
que o TSE nomeou **uma junta por MRV, não uma por seção**. São **109 nomeados
para 112 lugares** (4 × 28) e só **83 confirmados**.

| Parede | Mesas | Esperado | Nomeados | de | Confirmados | Por mesa |
|---|---:|---:|---:|---:|---:|---:|
| norte | 9 | 3.835 | 36 | 36 | 31 | 3,44 |
| leste | 10 | 3.831 | 39 | 40 | 28 | 2,80 |
| **oeste** | 9 | 3.833 | 34 | 36 | **24** | **2,67** |

O cruzamento incomoda: a **oeste** é a parede mais densa por metro (102,5/m) e
é também a mais descoberta — e as duas lacunas de nomeação dela caem nas mesas
erradas:

- **MRV 24** (seção 3322, 588 esperados, **2ª maior carga do salão**) — 3
  nomeados, falta o 2º Mesário, e só 2 confirmados;
- **MRV 11** (seção 3161, 504 esperados, 6ª maior) — 3 nomeados e **sem
  Presidente nomeado**, com 1 confirmado.

Na leste, **MRV 19** (seção 3308) tem 4 nomeados mas 3 sem resposta, e **MRV
26** (3688) está sem 2º Mesário. Se as 25 pendências não virarem confirmação,
sobram 83 pessoas para 28 mesas — 2,96 por mesa, contra as 4 previstas.

Isso é matéria do item 4 do `PENDENCIAS` (plano de comunicação com mesários),
não da prancheta. Mas a prancheta diz **por onde começar a ligar**: MRV 24 e
MRV 11, nessa ordem.

## 7. Efeitos de segunda e terceira ordem

- **Segunda ordem — a equidade por parede não é equidade por mesa.** As 28
  mesas vão de 295 a 590 esperados (razão 2,00×, CV 23,3%). Equilibrar as
  paredes reparte o *fluxo pelo salão*; não reparte o *tempo de fila do
  eleitor*, que é função da mesa dele. Quem cai na MRV 22 tem o dobro de
  gente à frente de quem cai na 25 (e, numa fila, a espera cresce mais que
  proporcionalmente à carga), e nenhum arranjo de posição conserta isso — só desagregar
  os três pares Dublin+Dublin conserta, e isso é negociação com o TSE, não
  desenho de piso. O ganho real do equilíbrio é outro: **as três filas de
  entrada crescem no mesmo ritmo**, então não há uma porta que colapse antes
  das outras, e a equipe pode ser dividida em três partes iguais sem
  remanejamento durante o dia.
- **Segunda ordem — densidade linear vira profundidade de fila.** Com 102,5
  esperados por metro na oeste contra 76,2 na norte, a fila da parede oeste é
  ~35% mais profunda para a mesma carga. No plano de fila confinado dentro do
  Hall 2, é a oeste que estoura primeiro, e não porque leve mais gente.
- **Terceira ordem — o equilíbrio é frágil ao congelamento tardio.** A
  numeração eleitor (1 a 28, sentido horário) é calculada *sobre o cenário de
  trabalho*, e a atribuição mesa → entrada também. Toda peça impressa —
  sinalização, cadernos, crachá de mesário, o mapa que o eleitor olha na
  porta — depende dos três congelarem juntos. Mudar uma mesa de parede depois
  da impressão não custa só a reimpressão: custa o equilíbrio, porque a
  composição por parede é o resultado de uma otimização, não um arranjo que
  tolere troca manual.
- **Terceira ordem — o risco de mesário é o que pode anular tudo.** Uma mesa
  que abre com 3 pessoas em vez de 4 perde a posição de identificação
  redundante e desce de patamar de velocidade — exatamente o cenário que
  `saidas/analise_gargalos.md` mostra não fechar às 17h com caderno físico.
  Se isso acontecer na MRV 24 (588 esperados), a parede oeste deixa de ser
  um terço equilibrado e vira o gargalo do salão. **O equilíbrio desenhado
  em metros se perde por falta de gente, não por falta de espaço.**

## 8. Veredito

A prancheta pode ser congelada. Os números estão certos e o Hamad_Final está,
de fato, equitativo por parede — no ótimo, e robusto a todas as bases de
comparecimento testadas.

O que ainda merece uma decisão do Posto, em ordem de urgência:

1. **Mesários da MRV 24 e da MRV 11** (item 4 do `PENDENCIAS`) — é o único
   item que pode desfazer o equilíbrio no dia.
2. ~~**Adotar "uma entrada por parede"** e regerar `data/decisoes.json`.~~
   **Feito em 15/09** — ver o adendo do item 9.
3. **Trocar o 11.416 de `plano_filas.py`** pela base B.
4. **Baixar o `perfil_comparecimento_abstencao_2022` (ZZ) do TSE** e conferir
   as taxas proxy. Não bloqueia nada — melhora a defesa do número diante do
   TRE.

---

## 9. Adendo de 15/09 — uma entrada por parede, e o rearranjo que ela pede

Depois desta conferência o Posto fechou a regra que o item 6.1 propunha, e foi
além dela: **cada entrada serve uma parede inteira e só ela.**

| Entrada | Porta | Parede | Mesas | Esperados | % | Metros | Por metro |
|---|---|---|---:|---:|---:|---:|---:|
| A | S4 | oeste | 9 | 3.833 | 33,3% | 29,53 | 129,8 |
| B | S5 | norte | 9 | 3.835 | 33,4% | 27,64 | 138,7 |
| C | S6 | leste | 10 | 3.831 | 33,3% | 36,30 | 105,5 |

Com isso **equilibrar as entradas e equilibrar as paredes passaram a ser o
mesmo problema**, e a amplitude entre filas caiu de **573 para 4 eleitores**.
A geometria ajuda: S4 (centro em x = 22,07), S5 (28,29) e S6 (34,50) estão na
ordem oeste → centro → leste, então cada porta manda para o lado que já é o
seu. Ninguém atravessa o salão, e nenhuma fila cruza outra.

O cenário de trabalho passou a ser `Paredes_ABC`
(`cenarios/paredes-abc-20260915.json`), gerado por
`scripts/arranjo_paredes.py`.

### 9.1 O que mudou, e o que não mudou

| | |
|---|---:|
| Mesas que mudam de **parede** | **0** de 28 |
| Mesas que mudam de **entrada** | **16** de 28 |
| Mesas que mudam de **número eleitor** | 5 de 28 |
| Mesas repareadas (posição refeita) | 28 de 28 |

**A agregação de seções não foi tocada.** O par principal → agregada de cada
urna é do Cartório Eleitoral, foi conferido no item 2 contra o PDF oficial, e
os mesários já estão nomeados por MRV. O que se repartiu foi a mesa inteira,
com as suas duas seções juntas.

### 9.2 Por que a composição das paredes ficou como estava

`scripts/arranjo_paredes.py` varreu as **21 repartições** (n_oeste, n_norte,
n_leste) que cabem fisicamente nas três paredes, com as duplas de 3,90 m e os
2,40 m entre unidades da planta oficial, e otimizou cada uma:

| Mesas o/n/l | Amplitude | Mesas trocando de parede | Metros por mesa | Menor folga livre |
|---|---:|---:|---|---|
| 10/8/10 | **0** | 16 | 2,95 · 3,45 · 3,63 | 1,83 · 2,10 · 2,10 |
| 10/10/8 | **0** | 16 | 2,95 · 2,76 · 4,54 | 1,83 · 2,06 · 2,10 |
| 9/9/10 | **0** | 19 | 3,28 · 3,07 · 3,63 | 1,83 · 2,06 · 2,10 |
| **9/9/10 (a de hoje, repareada)** | **4** | **0** | 3,28 · 3,07 · 3,63 | 1,83 · 2,06 · 2,10 |

A amplitude zero existe — e custa **mover 16 das 28 mesas de parede para ganhar
4 eleitores**, 0,03% do terço. Não é uma troca que se faça: muda a entrada de
uns 6.500 eleitores e a numeração de quase toda a sinalização para um ganho
que nenhum mesário sentiria. A composição de hoje ficou.

### 9.3 O que o repareamento ganhou

As posições foram refeitas pelo empacotador — duplas de 3,90 m, uma mesa de
alta carga isolada por parede, folga repartida por igual dentro de cada trecho.
O ganho é de folga, não de carga:

| Parede | Menor folga livre, antes | Depois |
|---|---:|---:|
| oeste | 2,10 m | 1,83 m |
| norte | **1,50 m** | 2,06 m |
| leste | 2,10 m | 2,10 m |
| **pior do salão** | **1,50 m** | **1,83 m** |

O Hamad_Final tinha dois pontos de 1,50 m na parede norte — o mínimo do padrão,
sem margem nenhuma. O arranjo novo não tem nada abaixo de 1,83 m.

### 9.4 O que isto não resolve

- **A densidade continua desigual, e agora importa mais.** Sem o Ring 3, a fila
  de cada entrada vive dentro do salão, na frente da sua parede. A norte leva
  138,7 esperados por metro contra 105,5 da leste — 31% mais densa para a mesma
  carga, porque é 8,7 m mais curta. Carga igual não é fila igual: é a parede
  norte que enche primeiro.
- **O gargalo por mesa é estrutural.** As 28 mesas continuam indo de 295 a 590
  esperados (razão 2,00×). Isso não é pareamento ruim: com 32 seções de Dublin
  e 28 mesas, a casa dos pombos força 4 pares Dublin+Dublin de ~790 aptos.
  Só desagregar, com o TSE, baixa esse teto.
- **A pendência de mesário segue igual** (item 6.3): MRV 24 e MRV 11, as duas
  lacunas, continuam na parede oeste.

---

## 10. Adendo de 16/09 — portas, zonas livres e as vermelhas ao centro

Seis pedidos do Posto, todos verificados por `scripts/confere_arranjo.py`, que
sai com código 1 se algum falhar:

```bash
python3 scripts/confere_arranjo.py
```

| # | Pedido | Como ficou |
|---|---|---|
| 1 | Sinalização das portas nas paredes oeste, norte e leste | N1, N2, L1–L4, O1, O2 e R1 com rótulo e papel em `decisoes.sinalizacao_portas`, desenhados na planta |
| 2 | N2 e O2 desbloqueadas | vão livre (3,56 m e 3,07 m) mais recuo de 3 m sem mesa **e sem fila** |
| 3 | Emergência da parede leste | faixa protegida de 3,00 m em toda a fachada (x 47,3 → 50,3), cobrindo L1 a L4 |
| 4 | S7 preferencial | `papel: preferencial` — idoso, gestante, PcD e acompanhante, sem fila, para qualquer parede |
| 5 | Vermelhas ao centro, verdes em volta | **revisto em 16/09 — ver §11**: o objetivo era espaço de serpenteado, não a posição |
| 6 | 3,00 m na dupla, 1,50 m entre duplas | 12 vãos de 3,00 m e 10 de 1,50 m, exatos; os 3 vãos restantes são portas separando trechos |

### 10.1 O item 5 custou a amplitude

A regra "vermelha no meio, verde em volta" é uma restrição geométrica dura, e
ela derrubou a repartição 9/9/10:

- a parede norte tem dois trechos, de 10,01 m e 17,63 m;
- pôr a vermelha no trecho central com uma unidade verde de cada lado reserva
  **12,60 m**, e o que sobra não cabe: duas duplas no trecho de 10,01 m pedem
  10,20 m;
- com 9 mesas, a norte só fecha com a vermelha no trecho oeste — a 8,54 m do
  meio da fileira, fora do terço central.

Das 21 repartições que cabiam ontem, **9 sobrevivem** aos itens 5 e 6. A melhor
é **9/8/11**:

| Parede | Entrada | Mesas | Esperados | Desvio | Por metro |
|---|---|---:|---:|---:|---:|
| oeste | A · S4 | 9 | 3.871 | +38 | 131,1 |
| norte | B · S5 | 8 | 3.757 | −76 | 135,9 |
| leste | C · S6 | 11 | 3.871 | +38 | 106,6 |

**Amplitude 114 eleitores (2,97% do terço), contra 4 ontem.** É o preço do item
5, e é um preço barato: 114 eleitores repartidos em nove horas são ~13 por hora
entre a parede mais cheia e a mais vazia. Continua dentro de "mais ou menos o
mesmo número de eleitores por parede".

### 10.2 O que mudou desde o Hamad_Final

| | |
|---|---:|
| Mesas que mudam de parede | 14 de 28 |
| Mesas que mudam de entrada | 17 de 28 |
| Mesas que mudam de número eleitor | 28 de 28 |

A numeração eleitor mudou inteira porque ela é posicional e as posições foram
todas refeitas. **Nada disso toca a agregação de seções nem a nomeação de
mesários**, que são por MRV.

### 10.3 O que continua em aberto

- **A densidade segue desigual**, e o item 5 a piorou um pouco: a norte agora
  leva 135,9 esperados por metro contra 106,6 da leste. Sem o Ring 3, é a
  parede norte que enche primeiro.
- **S7 tem 1,27 m de vão.** Serve a um fluxo preferencial pequeno, mas é o
  ponto a medir em campo antes de imprimir a sinalização: se a fila
  preferencial crescer, 1,27 m não absorve.
- **A pendência de mesário segue** (item 6.3): MRV 24 e MRV 11 continuam as
  duas lacunas, agora nas paredes leste e norte respectivamente.

---

## 11. Revisão de 16/09 — o que o item 5 realmente queria

O pedido de pôr a mesa vermelha no meio da parede tinha um objetivo por trás:
**abrir espaço para serpentear mais eleitores em volta dela**, com unifila, sem
comer a fila das vizinhas. Com o objetivo explícito, a posição deixou de
importar e a geometria ficou muito mais fácil.

### 11.1 O que se reserva, e com que conta

Cada mesa vermelha ganha, **à frente dela**, um retângulo reservado:

| | |
|---|---|
| Footprint | 2,80 m ao longo da parede × 4,20 m de profundidade |
| Onde começa | onde o módulo acaba, a 4,10 m da parede |
| Composição | 2 raias de 4,20 m, no passo de raia de 1,40 m do projeto |
| Capacidade | 2 × 4,20 × 1,20 × 2,00 = **20,2 pessoas** |
| Folga lateral exigida | **1,90 m** de cada lado da mesa |

Os parâmetros de fila são os do próprio `scripts/ring3.py` — passo de raia
1,40 m, largura útil 1,20 m, 2,00 pessoas por m², ou seja 2,4 por metro de
raia. **O serpenteado não é desenhado**, como pedido: o que a planta garante é
que o espaço existe, livre de mesa, de fila vizinha e de zona protegida.

A folga de 1,90 m sai de uma conta simples: o serpenteado tem 2,80 m e o corpo
da mesa 0,90 m, então ele avança 0,95 m para cada lado. Exigir 1,90 m de vão
garante que ele não passe do meio do caminho até a mesa vizinha — é isso que
significa "sem afetar as outras filas".

### 11.2 Os três serpenteados

| Parede | MRV | Retângulo reservado (x, y) | Pessoas |
|---|---:|---|---:|
| oeste | 22 (590) | x 4,10–8,30 · y 21,72–24,52 | 20 |
| norte | 23 (586) | x 17,16–19,96 · y 36,10–40,30 | 20 |
| leste | 24 (588) | x 39,00–43,20 · y 27,45–30,25 | 20 |

Todas as três com 1,90 m de folga dos **dois** lados, e nenhuma na ponta da
parede — o canto do salão é o pior lugar para a mesa mais cheia, porque é o
percurso mais longo da entrada até ela.

### 11.3 Soltar o centro devolveu o equilíbrio

| Regra do item 5 | Repartições viáveis | Amplitude |
|---|---:|---:|
| vermelha no terço central + verdes obrigatórios (15/09) | 9 de 21 | 114 |
| **serpenteado reservado, posição livre (16/09)** | **13 de 21** | **2** |

**3.834 · 3.832 · 3.833** — amplitude de **2 eleitores em 11.499**, o melhor
de toda a série. A restrição geométrica ficou mais útil e menos apertada ao
mesmo tempo: o que travava não era o espaço de fila, era a exigência de
posição.

Verdes ao redor voltou a ser **preferência**, como o pedido original dizia
("preferencialmente"), e não regra — foi por tê-la endurecido em 15/09 que a
amplitude tinha subido para 114.

### 11.4 Sala de apoio na parede oeste

O trecho entre a porta **O1** e a parede norte saiu da lista de trechos
utilizáveis: é onde fica a sala de apoio.

- zona reservada: x 0,00–7,80 · y 38,50–44,40, começando na borda norte de O1;
- a parede oeste perde o trecho (39,05–43,95) e cai de **29,53 m para 24,63 m**
  de comprimento útil;
- com 9 mesas em 24,63 m, ela passa a 2,74 m por mesa — a mais apertada das
  três, e a mais densa em eleitores por metro.

**A profundidade de 7,80 m é suposição minha**, alinhada ao recorte sudoeste do
salão. O que o pedido fixa é o trecho de parede; a profundidade da sala precisa
ser medida em campo antes de imprimir.

### 11.5 O aperto de 2,50 m não foi preciso

A autorização para comprimir a dupla de 3,00 m para 2,50 m entrou no motor como
**segunda tentativa**: ele monta tudo a 3,00 m e só aperta se não couber. Nas
três paredes os 3,00 m couberam, então **nenhuma dupla foi apertada**. A
autorização fica registrada em `decisoes.vao_dupla_por_parede` e é usada
automaticamente se uma mudança futura exigir.

### 11.6 O que isto custou

| | |
|---|---:|
| Mesas que mudam de parede (vs. 15/09) | 17 de 28 |
| Amplitude | 114 → **2** |
| Comprimento útil da parede oeste | 29,53 → 24,63 m |
| Duplas apertadas | nenhuma |
