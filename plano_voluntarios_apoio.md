# Plano de Voluntários de Apoio ao Fluxo — Eleições 2026, Dublin

Dimensionamento das funções e do efetivo de voluntários que organizam o fluxo do
eleitor desde a chegada à RDS até o interior do salão de votação, no 1º turno de
04/10/2026 (8h–17h).

Este documento **não** cobre mesários, secretários de seção nem a segurança
contratada — são efetivos distintos, contados à parte na seção 6.

---

## 1. Base numérica

| Parâmetro | Valor | Origem |
|---|---|---|
| Eleitores aptos | 16.794 | `saidas/dados.json` (CSV oficial do TSE) |
| Seções / urnas | 51 seções em 28 urnas | idem |
| Residentes em Dublin | 12.581 | idem |
| Residentes no interior | 4.213 | idem |
| Comparecimento esperado | **~11.400** (74% Dublin, 50% interior) | taxas de 2022, `contexto_eleicoes_dublin_2026.md` §1 |
| Janela de votação | 8h–17h (9h) | idem |

### 1.1 Taxas de chegada (o número que dimensiona tudo)

- Média: 11.400 / 9h = **1.267 eleitores/h ≈ 21/min**.
- Pico (premissa: fator 1,7–2,0× sobre a média, concentração de manhã — **premissa,
  não dado observado**): **~2.100–2.500/h ≈ 35–42 pessoas/min**.
- Traduzindo: no pico, **alguém cruza o portão a cada 1,5 segundo**.
- Ocupação simultânea (permanência média de 20–30 min): **800–1.200 pessoas**
  presentes no circuito ao mesmo tempo.

Duas consequências diretas:

1. Qualquer posto que **pare o eleitor para uma conversa** precisa resolver cada
   atendimento em menos de 2 segundos por canal paralelo. Não existe. Logo, nenhum
   posto pode ser de inspeção de 100%.
2. A ocupação simultânea de 800–1.200 pessoas é compatível com os 20 seguranças já
   contratados (referência de 1 steward : 100 presentes do Purple Guide, para eventos
   de risco moderado). Voluntariado de orientação, porém, escala com **vazão**
   (pessoas/hora), não com ocupação — por isso o número de voluntários é maior que o
   de seguranças sem que haja contradição.

---

## 2. Avaliação da proposta inicial de seis funções

A lógica de **funil com redundância** (a mesma informação repetida em três pontos
antes do ponto de decisão) está correta e resolve o risco registrado em
`contexto_eleicoes_dublin_2026.md` §4: a pré-triagem deixa de ser um único ponto
serial de estrangulamento.

**Defeito estrutural a corrigir — ponto 3.** "Questionar se olharam as sinalizações"
é inspeção de 100% num ponto de 35–42 pessoas/min. Converte um problema de
sinalização num gargalo humano, e a fila recua para a rua (Dublin, outubro, chuva).

Correção: o ponto 3 deixa de ser *entrevista* e passa a ser **locução + captura de
exceções**:

- 2 voluntários em **locução contínua** ("Zona A, seções 3101 a 3161, porta da
  esquerda"), falando para o fluxo em movimento, sem parar ninguém;
- 2 voluntários em **interceptação seletiva**, abordando apenas quem exibe sinal de
  perda (parou, olha em volta, mexe no celular, segura papel).

Regra de projeto para todos os postos: **a sinalização atende o caso padrão; o
voluntário atende a exceção.** Orçar 10–20% dos eleitores como exceção.

**Limite jurídico dos voluntários** (precisa estar no briefing, não é detalhe):
voluntário **orienta, não decide**. Não toca em documento, não confere título, não
diz a ninguém se pode ou não votar — identificação é monopólio legal do mesário.
Voluntário com camiseta ou boné de campanha na porta é boca de urna e vira problema
do Posto; colete neutro obrigatório, sem cor partidária.

---

## 3. Funções que faltavam

| # | Função | Por que é necessária |
|---|---|---|
| A | **Portão viário / chegada externa** | ~11.400 pessoas chegando de carro, DART e ônibus. A RDS tem mais de um acesso; sem orientação na via, o erro acontece antes do ponto 1 e a correção custa 10 min por eleitor. |
| B | **Gestão da fila externa** | Os 100 separadores (200 m) já orçados não se organizam sozinhos. Cabeça de fila, cotovelos da serpentina e contingência de chuva. |
| C | **Triagem preferencial** | Idosos, PCD, gestantes, lactantes e pessoas com criança de colo têm prioridade legal. Sem canal separado e sem quem os conduza, a prioridade vira discussão na fila — a fricção mais comum e mais visível do dia. |
| D | **Balcão "Onde eu voto?"** | Eleitor que não sabe a seção, mudou de endereço, está sem e-Título ou veio de outra jurisdição. Se não for resolvido **antes** do funil, ele entope todos os pontos seguintes. Exige lista nominal impressa (16.794 nomes → seção → zona) e/ou tablets. |
| E | **Mesa de justificativa** | Quem não vota ali precisa ser desviado cedo; caso contrário percorre todo o circuito para descobrir no fim. |
| F | **Fluxo de saída / circuito unidirecional** | A proposta inicial é toda de entrada. Saída cruzando entrada é causa clássica de congestionamento. Porta de saída dedicada e ninguém voltando pelo caminho de entrada. |
| G | **Coordenação setorial** | Span of control: 1 coordenador para cada 6–8 voluntários, mais 1 coordenador geral. Sem isso não há realocação durante o pico. |
| H | **Contagem de fluxo** | Um contador manual por porta, registro de hora em hora. Custa quase nada, permite mover voluntários em tempo real e é a única fonte de dado real para o 2º turno (25/10) e para o próximo pleito. |
| I | **Encerramento da fila às 17h** | Art. 153 do Código Eleitoral: às 17h distribuem-se senhas a todos os presentes, começando pelo último da fila. É ato do mesário, mas alguém precisa **marcar fisicamente o fim da fila** às 17h00, com coordenador presente e registro de horário. Função sensível, briefada à parte. |
| J | **Base de voluntários** | Credenciamento às 7h, coletes, crachás, água, almoço, rendição de pausas. Sem base, as pausas viram ausências. |
| K | **Reserva flutuante** | Falta de voluntário em dia de evento fica tipicamente em 10–20%, mais pausas e banheiro. Reserva de 15% do efetivo em escala. |
| L | **Ligação com segurança e com o RDS** | Voluntário não faz contenção nem confronto — isso é dos 20 seguranças contratados. Precisa de regra de escalonamento escrita e de 1 interlocutor com o staff do RDS. |
| M | **Primeiros socorros** | 11.400 pessoas em 9 horas produzem desmaios. Confirmar se o RDS fornece posto médico; se não, contratar e, de todo modo, ter protocolo conhecido por todos os coordenadores. |

Observação sobre **acolhimento de fiscais de partido, imprensa e observadores**:
chegam antes das 8h, não são eleitores e não devem entrar pelo circuito de votação.
Cabe ao credenciamento (função J), não a um posto próprio.

---

## 4. Quadro de postos (posições simultâneas)

Pico = janela de maior chegada (premissa: 10h–14h). Fora do pico = 8h–10h e 14h–17h.

| Posto | Função | Pico | Fora do pico |
|---|---|---|---|
| 0 | Portão viário / chegada externa (novo — A) | 3 | 2 |
| 1 | Porta da RDS — locução e sinalização (original 1) | 2 | 1 |
| 1b | Fila externa (novo — B) | 2 | 1 |
| 2 | Lateral do Hall 2 — banners (original 2) | 3 | 2 |
| 2b | Balcão "Onde eu voto?" + justificativa (novo — D, E) | 4 | 2 |
| 2c | Triagem preferencial (novo — C) | 2 | 1 |
| 3 | Entrada do Ring — locução + captura de exceções (original 3, corrigido) | 4 | 2 |
| 4 | Frente das zonas A/B/C (original 4) | 4 | 3 |
| 5 | Portas de cada zona — controle de entrada (original 5) | 4 | 3 |
| 6 | Interior do salão — eleitores perdidos (original 6) | 4 | 2 |
| 6b | Acompanhamento preferencial até a mesa (novo — C) | 2 | 1 |
| 7 | Saída / circuito unidirecional (novo — F) | 2 | 1 |
| 8 | Contagem de fluxo por porta (novo — H) | 2 | 1 |
| 9 | Coordenação: 1 geral + 3 setoriais (novo — G) | 4 | 4 |
| 10 | Base de voluntários (novo — J) | 2 | 1 |
| | **Subtotal** | **44** | **27** |
| | Reserva flutuante 15% (novo — K) | 6 | 4 |
| | **Total em operação** | **50** | **31** |

Geometria confirmada (15/09/2026): o **Hall 2** é a área de chegada e fila, com
três portas de entrada **A, B e C**; o **Ring 3** é o salão de votação, dividido em
três zonas **A, B e C**, uma por porta. O quadro acima já reflete isso — 3 zonas,
3 portas de entrada e 1 saída dedicada. Caso o número de zonas ou de portas mude,
some **+1 voluntário por zona e +1 por porta**.

### 4.1 A porta é o ponto a proteger

Com uma única porta por zona, cada porta recebe no pico **12–14 pessoas/min**. Um
vão de 1 m escoa muito mais que isso em fluxo contínuo, então a porta não é gargalo
— **desde que ninguém pare nela**. Qualquer verificação, pergunta ou conferência
feita no batente converte a porta no gargalo de toda a zona. O posto 5 controla
ritmo e sentido; não confere nada.

### 4.2 Balanceamento das três zonas

As zonas devem ser equilibradas por **comparecimento esperado**, não por número de
urnas — as urnas vão de 398 a 797 aptos. Distribuição proposta (a validar com o
Cartório Eleitoral, que decide o arranjo físico das mesas):

| Zona | Urnas | Aptos | Interior | Comparecimento esperado |
|---|---|---|---|---|
| A | 9 | 5.526 | 1.539 | 3.720 |
| B | 9 | 5.365 | 1.150 | 3.695 |
| C | 10 | 5.903 | 1.524 | 4.003 |

Spread de 8,3% entre a maior e a menor; reproduzível com
`python3 scripts/zonas_balanceadas.py`, que também imprime a lista de urnas de cada
zona. Duas razões para não agrupar por faixa
numérica de seção: os números de urna não são contíguos (511, 1.160, 3.054…), então
faixa não gera sinalização mais simples; e o agrupamento por faixa desequilibra a
carga sem contrapartida.

Dois cuidados no arranjo:

- **Espalhar as urnas grandes** (756–797 aptos) pelas três zonas, uma por zona — é a
  mesma recomendação já registrada em `contexto_eleicoes_dublin_2026.md` §4, e a
  distribuição acima a respeita.
- **Espalhar as urnas do interior.** Os 4.213 eleitores de fora de Dublin chegam em
  grupo, de ônibus e carona, não em fluxo contínuo. Concentrar Cork, Galway e
  Limerick numa mesma zona produz um pico local que nenhum dimensionamento médio
  cobre. A distribuição acima deixa 1.539 / 1.150 / 1.524 interioranos por zona.

---

## 5. Efetivo a recrutar

Carga total estimada: ~380 pessoas-hora (2h a 31 postos + 4h a 50 + 3h a 31 +
encerramento + montagem).

| Modelo | Efetivo | Avaliação |
|---|---|---|
| Turno único 7h30–17h30 | 50–54 | Menor esforço de briefing e zero risco de rendição malfeita. Mas 10 horas em pé degradam a qualidade exatamente nas últimas 3 horas e no corte das 17h. |
| Dois turnos completos | ~80 recrutados | Melhor qualidade, custo de duas rodadas de briefing e de uma rendição no meio do pico. |
| **Híbrido (recomendado)** | **62 escalados / ~70 recrutados** | Núcleo de 30 o dia inteiro (inclui os 4 coordenadores, que não rodam), reforço de 20 das 9h30 às 14h30, rendição de 12 para a tarde. Cobre o pico com 50, libera pausas reais à tarde e mantém continuidade de comando. |

Recrutar **70** para escalar 62 absorve 10–15% de ausência no dia.

Briefing: 1 sessão on-line na semana anterior (30 min, com o mapa de zonas) + 45 min
presenciais às 7h do dia 4, por setor, com o coordenador setorial.

---

## 6. Efetivos que não entram nesta conta

| Efetivo | Nº | Situação |
|---|---|---|
| Mesários | ~84 (28 × 3) + suplentes | Lista do TSE pendente (`PENDENCIAS` item 4) |
| Secretários de seção (fila de cada mesa) | 28 | 1 por urna, conforme definido pelo Posto |
| Segurança contratada | 20 (7h30–17h30) + 1 na véspera | Já orçado — €6.774,84 |
| Equipe do Posto / RDS | a definir | — |
| **Voluntários de fluxo** | **62** | Este documento |

Total de pessoas credenciadas na operação: **~195–205**.

---

## 7. Custo estimado dos voluntários

Estimativa, **não orçamento cotado** — entra em `PENDENCIAS` item 2.

| Item | Cálculo | EUR |
|---|---|---|
| Coletes/camisetas identificadores | 70 × 6 | 420 |
| Água e almoço | 70 × 12 | 840 |
| Rádios comunicadores (aluguel) | 12 unidades | 250–400 |
| Impressões: listas nominais, mapas de zona, pranchetas, crachás | — | 200 |
| **Total** | | **~1.700–1.900** |

Rádio é item crítico: com 1.000 pessoas num pavilhão, celular não é meio confiável
de coordenação. 12 aparelhos cobrem 4 coordenadores + 8 postos-chave.

---

## 8. Pendências que alteram estes números

1. **Confirmar a porta de saída.** A geometria de entrada está definida (Hall 2 com
   portas A/B/C → zonas A/B/C do Ring 3); falta fixar por onde se sai e garantir que
   a saída não cruze nenhuma das três entradas.
2. **Validar a distribuição de urnas por zona** (§4.2) com o Cartório Eleitoral.
3. **Método de identificação do eleitor** (`PENDENCIAS` item 5). Se for por caderno
   físico, o tempo por eleitor sobe, a fila migra para dentro do salão e o balcão
   "Onde eu voto?" (posto 2b) passa de conveniência a item crítico.
4. **Confirmar a expectativa de comparecimento** — toda a tabela da seção 4 é linear
   na taxa de chegada de pico.

---

## 9. Riscos de segunda e terceira ordem

- **Segunda ordem.** Excesso de triagem humana na porta não elimina a fila: transfere
  a fila para fora do prédio. Em outubro, em Dublin, isso significa fila na chuva —
  e fila na chuva produz desistência, que é privação de voto que não aparece em
  nenhuma estatística de comparecimento (o mesmo mecanismo já registrado em
  `contexto_eleicoes_dublin_2026.md` §2.4).
- **Terceira ordem.** Desordem visível na entrada circula em vídeo antes do fim da
  votação e vira questionamento sobre a condução do pleito no exterior — risco que
  extrapola a logística e alcança a imagem do serviço consular. O investimento em
  sinalização (€1.961 já orçados) e em voluntariado é, nesse aspecto, mitigação de
  risco reputacional, não só de fluxo.
- **Neutralidade.** Voluntários recrutados na comunidade costumam ter vida política.
  A regra de vestuário e de conduta precisa ser condição de aceitação, por escrito,
  não recomendação verbal no dia.

---

## Fontes

- Dados de eleitorado e agregação: `saidas/dados.json`, gerado dos CSVs oficiais do
  TSE (ver `README.md`).
- Premissas de comparecimento, orçamento e layout: `contexto_eleicoes_dublin_2026.md`.
- Encerramento da votação e distribuição de senhas: Código Eleitoral, art. 153.
- Referência de proporção de stewards por público: Purple Guide (1:100 para risco
  moderado) — benchmark de mercado, não norma aplicável ao pleito.
