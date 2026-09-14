# Formação de filas sem o Ring 3 — RDS Hall 2, 1º turno de 04/10/2026

Desenho de fluxo, dimensionamento de contenção e avaliação da alternativa de
fila na rua. Todos os números saem de `scripts/plano_filas.py` e
`scripts/filas_sem_ring3.py`, que rodam sobre o eleitorado real por urna em
`saidas/dados.json` (16.794 aptos, 51 seções, 28 urnas).

**Desenho:** `saidas/plano_filas_sem_ring3.svg` (e `.png`)

> **Atualização.** O RDS proibiu formação de fila em seu terreno, o uso da rua é
> incerto e não há autorização de Brasília para o Ring 3. As seções 3 a 5 deste
> documento — que contavam com retenção externa no pátio — estão **superadas
> por `plano_filas_confinado_hall2.md`**, que dimensiona toda a fila dentro do
> Hall 2. As seções 1, 2, 6 e 7 (fila esperada, equipe, efeitos de segunda e
> terceira ordem) continuam válidas.

---

## 1. O problema, em uma linha

Sem o Ring 3 não existe mais um lugar externo para *estocar* eleitores. A fila
deixa de ser um detalhe de sinalização e passa a ser **um consumidor de área
dentro do Hall 2**, competindo com as 28 mesas. O modelo mostra que, no cenário
realista (60 s por eleitor), o pico de gente esperando ao mesmo tempo é de
**415 a 899 pessoas** — e que isso **cabe dentro do salão**, mas só com uma
peça desenhada para isso e com cerca de **3,6× mais unifila do que o orçamento
atual prevê**.

## 2. Quanta fila existe para acomodar

Simulação urna a urna (28 filas paralelas, chegada distribuída ao longo das 9
horas, comparecimento de 11.416 eleitores = 74% Dublin + 50% interior):

| Perfil de chegada | 45 s/eleitor | 60 s/eleitor | 75 s/eleitor | 90 s/eleitor |
|---|---:|---:|---:|---:|
| Base | 248 | **415** | 1.188 | 2.013 |
| Pico de manhã | 511 | **899** | 1.746 | 2.671 |

*(pico de pessoas simultaneamente em fila, dentro do salão)*

Três leituras:

1. **O tempo por eleitor manda em tudo.** Entre 60 s e 75 s a fila **triplica**.
   Não é um ajuste fino: é a diferença entre um salão organizado e um salão
   intransitável. O plano de filas não substitui a discussão de agregação de
   seções (§2 do `contexto_eleicoes_dublin_2026.md`) — ele depende dela.
2. **A fila de abertura é o pior momento isolado.** Entre 3% e 5% do
   comparecimento já está na porta às 8h00: **342 a 571 pessoas**, todas
   necessariamente do lado de fora, antes de qualquer porta abrir. Nenhum
   desenho interno resolve isso.
3. **A partir de 75 s o problema deixa de ser de layout.** 1.746 pessoas em
   fila não é um problema de barreira: é falta de urna.

## 3. O desenho proposto: anel de espera com 6 filas

A ideia de "3 filas por porta" está certa, mas vale invertê-la geograficamente.
Em vez de blocos de fila no meio do salão (que obrigam o eleitor liberado a
atravessar o salão inteiro até sua urna), as filas ficam **em um anel entre a
faixa das mesas e o núcleo central** — cada fila parada na frente exata do
trecho de parede que ela serve.

```
  parede ─── faixa das MRV (7,0 m) ─── ANEL DE ESPERA (7,7 m) ─── NÚCLEO LIVRE
            mesa + urna + micro-fila     7 canais de 1,10 m       474 m² livres
```

**Cinco etapas, sem cruzamento entre entrada e saída:**

1. **Triagem na porta** (Entrada A ou B, parede sul) — o eleitor recebe a letra
   da sua fila.
2. **Corredor de distribuição** — três ramais por porta, atravessando o núcleo.
3. **Anel de espera** — serpentina de 7 canais, onde a fila efetivamente fica.
4. **Liberação** — o fiscal de cluster solta o eleitor para a micro-fila da sua
   urna quando abre vaga (4 m guiados por urna, 8 a 10 pessoas).
5. **Voto e saída pelas portas laterais** (leste e oeste), atrás da faixa de
   mesas. O eleitor nunca volta ao núcleo nem cruza quem está entrando.

### As 6 filas, balanceadas pelo eleitorado real

Como a alocação de seção → parede é nossa, as urnas foram distribuídas para
igualar a carga das 6 filas (amplitude de **2,5%** e divisão **50/50** entre as
portas), com as urnas grandes espalhadas uma por fila:

| Fila | Porta | Parede | Urnas | Esperados |
|---|---|---|---|---:|
| A1 | A | oeste-sul | 3179, 3216, 3305, 3313 | 1.883 |
| A2 | A | oeste-norte | 517, 3108, 3311, 3322 | 1.880 |
| A3 | A | norte-oeste | 513, 3309, 3315, 3442, 3688 | 1.927 |
| B1 | B | norte-leste | 511, 512, 3142, 3229, 3862 | 1.908 |
| B2 | B | leste-norte | 1160, 3054, 3161, 3306, 3308 | 1.920 |
| B3 | B | leste-sul | 1352, 3078, 3245, 3302, 3832 | 1.900 |

Distribuição de mesas: **8 na parede oeste, 10 na norte, 10 na leste** (passo de
4,5 a 5,0 m por seção — folgado; o Hall 2 comporta até 38 mesas nas três
paredes). A parede sul fica inteiramente livre para entrada e triagem.

### O que cabe

| Zona | Área | % do Hall 2 | Capacidade |
|---|---:|---:|---|
| Faixa das 28 MRV (3 paredes, 7,0 m) | 778 m² | 35% | 28 mesas + micro-filas |
| **Anel de espera (7,7 m, 7 canais)** | **622 m²** | **28%** | **1.058 pessoas** (teto 1.244) |
| Núcleo livre | 474 m² | 21% | reserva de +806 pessoas |
| Zona de triagem (parede sul) | 308 m² | 14% | consulta, prioritários, cadeiras |

Confronto com os picos da §2:

- 60 s, perfil base (**415**) → 39% do anel. Confortável.
- 60 s, pico de manhã (**899**) → 85% do anel. **É este o cenário de projeto.**
- 75 s (**1.188–1.746**) → estoura o anel e come o núcleo livre. Operável, mas
  sem margem de circulação e sem reserva de contingência.
- 90 s (**2.013–2.671**) → não cabe no salão. Transborda para a rua por
  definição.

## 4. Unifila e CCB — lista de materiais

Premissas de dimensionamento: canal de 1,10 m; **1,7 pessoa/m²** na área bruta
de fila (o *Purple Guide* britânico trata 2,0 p/m² como teto de área de espera —
projetamos abaixo disso); 1 linha longitudinal de barreira por canal; unifila =
poste retrátil de 2,0 m (confirmado pelo próprio orçamento: 100 unidades = 200
m); CCB (*crowd control barrier*, grade metálica) = 2,0 m.

**Critério de escolha entre os dois:** unifila é canalização — leve,
reconfigurável, sem resistência a empurrão. CCB é contenção — rígida,
resistente a pressão de multidão e a vento/chuva. **Fora do prédio e nos funis
de porta, só CCB. Dentro do salão, unifila.**

| Zona | Unifila | CCB | Detalhe |
|---|---:|---:|---|
| A. Retenção externa (pátio do RDS) | — | 66 | 600 pessoas em 300 m² (20 × 15 m), 3 divisores |
| B. Corredor portão → porta | — | 40 | 2 linhas × 40 m |
| C. Funis de porta e triagem | — | 16 | 2 portas × 2 linhas × 8 m |
| D. **Anel de espera interno** | **283** | — | 622 m², 7 canais, 566 m de barreira |
| E. Micro-filas de seção | 56 | — | 28 urnas × 4 m (mesa/parede como 2º lado) |
| F. Canal de saída e sinalização | 25 | — | 50 m |
| **TOTAL** | **364** | **122** | 728 m + 244 m |

### O impacto orçamentário

O orçamento aprovado tem **100 unifilas (200 m) por EUR 1.303,00** — ou seja,
**EUR 13,03/unidade**. O desenho exige **364**:

- **Déficit: 264 unifilas ≈ EUR 3.440** (extrapolando o preço unitário atual;
  **exige cotação nova** — locação de volume maior costuma ter desconto, e o
  fornecedor pode não ter 364 unidades disponíveis na data).
- **122 CCB não estão no orçamento em nenhuma linha.** Precisam de cotação
  própria. É o item de maior risco de prazo: CCB em Dublin no mesmo fim de
  semana disputa estoque com eventos esportivos.

**Se o orçamento não puder crescer**, a ordem de corte é: (F) sinalização de
piso → (E) micro-filas de seção, substituídas por fita no chão e fiscal →
reduzir o anel de 7 para 5 canais (931 pessoas, 249 unifilas). **A zona A
(retenção externa) não deve ser cortada**: é o único lugar onde cabe a fila das
8h00.

## 5. Fila na rua, em frente ao RDS: avaliação

A conta que decide é geométrica. Uma fila na rua é **linear**; uma serpentina é
**bidimensional**. As mesmas pessoas ocupam ordens de grandeza diferentes:

| Pessoas | Calçada de 2,5 m (1 por fileira) | Calçada de 4,0 m (4 por fileira) | Em serpentina (dentro) |
|---:|---:|---:|---:|
| 300 | 195 m | 49 m | 176 m² |
| 600 | 390 m | 98 m | 353 m² |
| 900 | **585 m** | 146 m | 529 m² |

Uma calçada de 2,5 m precisa manter ~1,5 m de passagem livre para pedestres,
sobrando ~1,0 m — **fila de uma pessoa só**. É por isso que 900 pessoas viram
quase 600 metros de calçada, o equivalente a **seis quarteirões** ao longo da
Merrion Road.

**Conclusão: fila na rua não funciona como parte do desenho.** Os obstáculos são
cumulativos, não alternativos:

- **Geometria.** Ver acima. Mesmo 300 pessoas consomem ~200 m de calçada.
- **Domínio público.** A Merrion Road é a R118, via arterial com faixa de
  ônibus. Ocupar calçada com fila organizada e barreiras não é decisão do Posto
  nem do RDS: depende de articulação com a **An Garda Síochána (Donnybrook)** e
  o **Dublin City Council**. Isso é prazo, não formalidade.
- **Clima.** Dublin em outubro: máxima média ~14 °C, ~79 mm de chuva e em torno
  de 12 a 20 dias de precipitação no mês. A probabilidade de chover em algum
  momento de um domingo de outubro é alta, e não há cobertura na calçada.
- **Acessibilidade.** Idosos e PcD em pé, sem assento e sem banheiro, em fila
  linear de centenas de metros — inaceitável, e é exatamente o grupo que mais
  desiste.
- **Exposição.** Imagem de fila de centenas de metros na porta de um posto
  brasileiro circula rápido. O custo reputacional recai sobre o Posto e o
  Itamaraty, não sobre o TSE que definiu a agregação.

**O que fazer no lugar:** negociar com o RDS uma **área de retenção no próprio
terreno** — os estacionamentos/pátios entre os portões (Merrion Rd, Anglesea Rd,
Simmonscourt Rd) e o Hall 2. É terreno privado já sob contrato, o que elimina a
questão de licença de via pública, permite banheiros químicos (já em cotação na
PENDENCIAS) e mantém o público dentro do perímetro dos 20 seguranças
contratados. **Esse é o substituto correto do Ring 3, não a rua.**

A rua deve ser tratada apenas como **transbordo de contingência**: um plano
escrito para o caso de o pátio encher, com acionamento definido (quem decide,
com que gatilho) e comunicação prévia à Garda — não como camada do desenho.

## 6. Equipe de fluxo

A triagem é a etapa **não paralelizável** do sistema: ela não ganha capacidade
com mais urnas.

| Função | Quantidade | Base de cálculo |
|---|---:|---|
| Triadores de porta | 3 | 1.941 chegadas/h no pico ÷ 5 s de direcionamento |
| Postos de consulta ("onde eu voto?") | **3 a 8** | 10% a 30% dos eleitores × 45 s |
| Liberadores de cluster | 6 | um por fila do anel |
| Coordenadores de parede | 3 | um por parede de mesas |
| Volantes | 2 | — |
| **Total** | **17 a 22** | (além dos 20 seguranças contratados) |

A faixa de 3 a 8 postos de consulta é o achado operacional mais barato do
documento: **a diferença entre 30% e 10% de eleitores que não sabem sua seção
vale 5 pessoas de equipe no pico** e reduz o tempo de triagem de todos os
outros. Isso liga diretamente o item 3 da PENDENCIAS (plano de comunicação) ao
desenho de fluxo: a campanha deve ter uma única chamada dominante —
**"descubra sua seção antes de sair de casa"** — com o link do TSE, e não uma
peça genérica sobre data e local.

## 7. Efeitos de segunda e terceira ordem

**Segunda ordem.**
- O anel de espera é uma **massa de gente entre o eleitor e a porta de saída**.
  Por isso a saída foi puxada para as portas laterais, atrás das mesas: se a
  saída fosse pela parede sul, cada eleitor que terminasse de votar teria de
  atravessar o anel na contramão. Essa decisão precisa ser validada com o RDS —
  as 12 portas de emergência do Hall 2 têm de continuar desobstruídas, e o
  layout de barreiras exige aval do responsável por incêndio do local.
- Triagem na porta **transfere** a fila, não a elimina: quanto melhor a triagem,
  mais rápido o anel enche. O ganho real é de **ordem**, não de vazão — evita
  que a fila de uma urna cheia contamine as vizinhas.
- A faixa prioritária (idosos, PcD, gestantes) não cria capacidade: ela realoca
  espera. Com uso intenso, o tempo da fila comum piora de forma perceptível, e
  isso precisa estar combinado com os mesários antes, não improvisado no dia.

**Terceira ordem.**
- Fila longa gera **desistência** — privação de voto que não aparece em
  nenhuma estatística, e que "melhora" as métricas de tempo pelo pior motivo.
- Mesa que fecha tarde atrasa a apuração do exterior e amplia a janela para
  questionamento do resultado. O risco migra de logístico para institucional.
- Um plano de filas bem documentado tem valor **argumentativo** junto ao TSE:
  mostra que o Posto exauriu as soluções de layout e que o gargalo restante é de
  número de urnas. É a contraparte operacional da contraproposta de agregação.

## 8. O que precisa ser decidido ou validado

1. **Área de retenção externa no terreno do RDS** — negociar com o RDS. Sem
   isso, a fila das 8h00 (342 a 571 pessoas) vai para a calçada por omissão.
2. **Tempo por eleitor** (biometria/eletrônico vs. caderno físico). Define se o
   desenho é confortável (60 s) ou inviável (90 s). É a variável dominante.
3. **Saída pelas portas laterais** — confirmar com o RDS que as portas das
   paredes leste e oeste dão em rota externa utilizável, e obter aval do
   responsável de incêndio para o layout de barreiras.
4. **Cotação de 264 unifilas adicionais e de 122 CCB** — nenhuma das duas está
   coberta pelo orçamento atual.
5. **Dimensões reais confirmadas.** O Hall 2 tem 50,2 × 44,5 m e 2.238 m²
   (ficha técnica do RDS). O recorte do canto sudoeste foi **estimado a partir
   da planta** (~11,7 × 7,4 m) e precisa de medição em vistoria.
6. **Divisão dos cadernos na MRV** (item 5 da PENDENCIAS) — é o que produz o
   tempo por eleitor da linha 2. Enquanto não estiver resolvido, este plano
   opera com uma faixa, não com um número.

## 9. Premissas e limites do modelo

- Comparecimento de **11.416** (74% Dublin, 50% interior, taxas de 2022 sobre o
  eleitorado real por urna). O `contexto` trabalha com ~12.000; a diferença não
  muda nenhuma conclusão.
- **Perfil de chegada é premissa, não dado.** Foram usados dois perfis (base e
  pico de manhã); não há série histórica de chegada por hora do posto de Dublin.
  **Se ela existir, é o insumo que mais melhora este modelo.**
- Modelo determinístico de fluido, 28 filas paralelas, passo de 5 minutos. Não
  simula variabilidade individual: os picos são **pisos**, não tetos.
- Densidade de projeto de 1,7 p/m² e canal de 1,10 m são premissas de desenho.
- Unifila e CCB assumidos com 2,0 m cada; confirmar com o fornecedor (há CCB de
  2,2 e 2,5 m, o que muda as quantidades).
- A posição exata de portas, sanitários e recortes na planta do RDS foi lida
  graficamente do PDF, não cotada.
