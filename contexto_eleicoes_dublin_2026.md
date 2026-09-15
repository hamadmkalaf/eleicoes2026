# Contexto Consolidado — Eleições Presidenciais 2026 (Posto de Dublin)

> Documento gerado a partir de busca em conversas anteriores (Claude) sobre a organização logística, orçamentária e física das eleições presidenciais brasileiras de 2026 na jurisdição de Dublin. Destinado a servir de base para desenho de fluxo em outra conversa. Datas, valores e números abaixo refletem o que foi efetivamente discutido nas conversas — ainda sujeitos a validação final com o Cartório Eleitoral/TSE.
>
> **Atualizado.** Parte dos pontos em aberto da seção 8 foi resolvida depois, pelo processamento deste repositório e pela Prancheta do Hall 2. As correções estão marcadas com **[resolvido]** ao longo do texto, e o desenho de fila adotado está na nova seção 9. O `README.md` e `saidas/tensa_barreiras.md` são as fontes atuais; este documento é o registro do que se sabia antes.

---

## 1. Dados gerais do pleito

- **1º turno:** 4/10/2026, 8h–17h, local: **RDS Ballsbridge, Hall 2** (Dublin).
- **2º turno (se necessário):** 25/10/2026, mesmo local e horário.
- **Eleitores registrados:** ~16.000 (conforme nota verbal); outra fonte (planilha TSE) trabalha com **14.626 aptos** distribuídos em **51 seções** e **15 localidades**
  - **[resolvido]** O CSV oficial do TSE de 13/08/2026 (`data/raw/eleitorado_local_votacao_2026_ZZ.csv`) traz **16.794 aptos** em 51 seções, agregadas em **28 urnas**. É esse o número que prevalece em todo o processamento do repositório; os 14.626 são de planilha anterior. O comparecimento esperado, ponderado pelo domicílio de origem, fica em **11.499**. (32 seções em Dublin + 19 no interior da Irlanda: Cork, Galway, Donegal, Limerick, Kerry, Mayo, Cavan, Clare, Leitrim, Longford, Roscommon, Waterford, Westmeath, "outros locais" etc.).
- **Comparecimento esperado:** ~12.000 (base histórica), com taxa de comparecimento de 2022 de **74%** em seções domiciliadas em Dublin (próxima à taxa doméstica) e **~50%** em seções do interior.
- **Contexto especial 2026:** coincide com a presidência irlandesa do Conselho da UE, o que reduziu a oferta de espaços disponíveis para locação (o local usado no 2º turno de 2022, mais barato, estava indisponível).

---

## 2. Agregação de seções eleitorais em mesas (núcleo técnico do problema de fluxo)

### 2.1 Proposta original do TSE (referência a ser contraposta)
- **20 mesas**, **25 urnas/MRV no total**, 14.626 aptos → média ~731 aptos/mesa, ~585 aptos/urna.
- Todas as mesas ancoradas em "Dublin" como seção principal; seções do interior são absorvidas dentro de mesas de Dublin.
- Padrão de agregação:
  - **11 mesas Dublin+Dublin** (pares de seções de Dublin fundidas): 792–800 aptos cada — **ponto crítico/gargalo**.
  - **8 mesas Dublin+condado(s)**: 559–800 aptos, variável.
  - **1 mesa isolada** (seção 3308): 399 aptos.
- **Inconsistência formal identificada:** apenas 44 das 51 seções aparecem na proposta de agregação. Faltam **7 seções** (Cork: 3, Galway: 2, Donegal: 1, Limerick: 1), o que bate com a diferença entre 25 urnas nominais e as 20 mesas efetivamente modeladas (déficit de 5 mesas). Não ficou claro se é rascunho incompleto, exclusão silenciosa ou diluição sem registro de origem — mas é um argumento objetivo e verificável para a contraproposta.

### 2.2 Por que a proposta do TSE falha — lógica estrutural (não de otimização)
- Há **32 seções de Dublin**, e cada mesa comporta no máximo **2 seções de Dublin** (2 × ~397 aptos ≈ 794 < limite de 800).
- Por princípio de "casa dos pombos": com **K mesas totais**, são forçados pelo menos **(32 − K) pares Dublin-Dublin**. Cada par gera ~583–588 comparecentes esperados, **independentemente de qualquer otimização**.
- O **pico de comparecimento por mesa só cai abaixo de ~582–588 quando K ≥ 32** (ou seja, quando nenhuma mesa tem duas seções de Dublin simultaneamente).
- Isso vale identicamente para K entre 22 e 31 mesas — o pico máximo esperado por mesa é **idêntico a 582 comparecentes** nesse intervalo inteiro (verificado especificamente para K=24 e K=30).

### 2.3 Simulação de tempo de votação (janela de 9h: 8h–17h)
Premissas: fluxo contínuo de eleitores, 1 urna (MRV) por mesa, comparecimento ponderado por domicílio (taxas de 2022).

| Cenário | Urnas/Mesas | Tempo/voto 30s | Tempo/voto 60s | Tempo/voto 90s |
|---|---|---|---|---|
| 1 — proposta TSE (agregação original, ~20 mesas) | 20 | seguro | **11 mesas estouram (~9,8h)**, todas pares Dublin-Dublin | **19 de 20 mesas colapsam** |
| 2 — 25 urnas | 25 | — | 7 mesas estouram | — |
| 3 — 30 urnas | 30 | — | 2 mesas estouram | — |
| 4 — Dublin 100% desagregada (32 urnas) + interior em 3 mesas | 35 total | folga total | **nenhuma mesa estoura**, mesmo a 90s (pico 335 comparecentes, −43% vs. proposta TSE) | seguro |
| 4b — variante com folga extra a 90s | 36 | — | — | pico cai a 294 |
| 5 — Dublin desagregada + interior também desagregado ao máximo | 38 (ou mais) | imune ao pior caso | imune | imune |

- **Conclusão técnica central:** a proposta do TSE só é operacionalmente segura perto de **30s por eleitor** — cenário otimista que pressupõe identificação eletrônica/biométrica rápida. A 60s (mais realista, incluindo conferência de identidade) ela colapsa parcialmente; a 90s (identificação por caderno físico), colapsa quase inteiramente.
- Cenários 2 e 3 (25 e 30 urnas) reduzem o **número** de mesas problemáticas, mas **não resolvem o pico máximo** — tratam sintoma, não causa.
- Cenário 4 resolve o problema em condições realistas (60s); Cenário 5 resolve em qualquer condição, com custo adicional de urnas/mesários/espaço.
- **Trade-off central a levar à negociação com o TSE:** Cenário 4/5 exige mais urnas (+10 a +18 vs. proposta original), mais mesários, e mais espaço físico — mas elimina o risco de mesas fechando de madrugada, filas que desincentivam comparecimento, e atraso em cascata na apuração.

### 2.4 Efeitos de segunda e terceira ordem (documentados para sustentação argumentativa)
- **2ª ordem:** filas não se comportam linearmente — eleitores que chegam antes das 17h têm direito de votar mesmo após o horário oficial de encerramento (pela norma), então mesas sobrecarregadas simplesmente fecham tarde, arrastando mesários, fiscais e o início da apuração.
- **3ª ordem:** apuração tardia em mesas do exterior atrasa o cronograma consolidado de resultados, ampliando a janela para questionamentos — risco que extrapola a logística e afeta a imagem do serviço consular/Itamaraty.
- Filas longas geram **desistência de eleitores** (uma forma de privação de voto que não aparece nas estatísticas oficiais de comparecimento) — o que ironicamente "melhora" as métricas de tempo por via indesejada.
- Recomenda-se explicitar, na peça argumentativa, que todos os cenários comparados usam a **mesma base de aptos (14.626)** e a **mesma taxa de comparecimento (74% Dublin, 2022)** — comparabilidade "maçãs com maçãs", ponto que um interlocutor técnico do TSE tende a checar primeiro.
- Dois fatores operacionais concretos que decidem entre Cenário 4 e Cenário 5:
  1. Identificação será eletrônica/biométrica (favorece 4) ou por caderno físico (favorece 5)?
  2. O local comporta fisicamente 32–35 urnas simultâneas?

### 2.5 Ferramentas produzidas (podem ser recuperadas se necessário)
- Planilha de simulação `contraproposta_agregacao_dublin.xlsx` com abas por cenário (C1_Proposta_TSE etc.).
- Arquivo fonte oficial do TSE: `Irlanda_-_Dublin.xlsx`, aba "Dublin" (bloco "QUADRO ATUAL 2026" + bloco "PROPOSTA DE AGREGAÇÃO") e aba "NÃO MEXER" (validação).
- Variantes de contraproposta com Dublin 100% isolada + interior agregado com teto de 800 aptos/mesa: Variante A (38 mesas, consolidação máxima) e Variante B (40 mesas, CV 2,5%, comparecimento uniforme 266–292/mesa) — **Variante B recomendada**.

---

## 3. Layout físico do salão de votação

- **Local simulado:** pavilhão retangular de **50,00 m × 44,50 m** (nota: local real definido posteriormente foi RDS Ballsbridge, Hall 2 — validar se dimensões coincidem).
  - **[resolvido]** Confere. A planta do RDS (`RDS_Hall_2_Floorplan_(1).pdf`) dá o Hall 2 em **50,2 × 44,5 m**, 2.238 m² brutos, pé-direito de 7 m; a prancheta trabalha com **50,3 × 44,4 m** de contorno útil, com o recorte a noroeste. As simulações de layout valem.
- **Unidade básica:** "seção" = par mesa receptora (3 mesários) + urna eletrônica (MRV), legal e operacionalmente vinculados — **não podem ser fisicamente separados** sem validação prévia do Cartório Eleitoral/TSE.
- **Cenários de quantidade simulados:** 25, 30 e 38 seções.
- **Restrições de desenho adotadas:**
  - Portas de entrada centralizadas em uma parede.
  - Urnas posicionadas contra a parede (atrás da mesa dos mesários, mais próximas da parede).
  - Nenhuma seção junto à entrada (zona de exclusão de 10 m centrais + 1,5 m de canto).
  - Buffer de canto de 1,5 m; módulo de 2,0 m de largura por seção (premissas assumidas, a validar contra dimensões reais do equipamento).
- **Achado crítico de espaçamento:** ao remover a parede da entrada do jogo (usar só 3 das 4 paredes), perde-se ~37 m de perímetro útil, que precisa ser absorvido pelas outras 3 paredes:

| Parede | 25 seções | 30 seções | 38 seções |
|---|---|---|---|
| Superior | 9 seções · 3,22 m livre | 11 seções · 2,27 m | 14 seções · 1,36 m |
| Esquerda | 8 seções · 3,19 m | 9 seções · 2,61 m | 12 seções · 1,46 m |
| Direita | 8 seções · 3,19 m | 10 seções · 2,15 m | 12 seções · 1,46 m |

- Em **38 seções**, o vão livre mínimo (~1,36–1,46 m) fica **abaixo do adequado** para circulação e sigilo entre seções vizinhas. Duas saídas propostas: (1) encurtar a fila projetada por seção (de 3,2 m para ~2 m, ou fila em duas fileiras); (2) restringir a exclusão da entrada apenas aos 10 m centrais + cantos, em vez de vetar a parede inteira — devolveria os 37 m perdidos.
- **Variante de agrupamento de mesas:** exploração de juntar mesas dos mesários fisicamente (mantendo vínculo mesa+urna por seção), com duplas (pares de mesas lado a lado, contornos tracejados) organizadas em grade de três fileiras — compatível com o procedimento desde que cada mesa continue ligada à sua urna específica. Separar mesas de urnas fisicamente (mesas centralizadas, urnas nas paredes) foi sinalizado como **risco procedimental** a validar com o Cartório Eleitoral antes de formalizar.

---

## 4. Fluxo de filas e organização de entradas (modelo genérico de 28 cabines — a integrar com o layout real acima)

- Estrutura discutida: **28 cabines/urnas** divididas em **3 entradas**: Entrada A (cabines 1–10), Entrada B (11–20), Entrada C (21–28).
- **4 cabines de alto volume** (~600 eleitores cada) vs. as demais (~400 cada).
  - **[resolvido]** São **três**, não quatro: os MRVs **22 (3313), 23 (3315) e 24 (3322)**, com 590, 586 e 588 comparecentes esperados — as três urnas Dublin+Dublin. Há dez urnas na faixa dos ~790 aptos, mas as outras sete somam uma seção de Dublin com uma do interior, cuja taxa de comparecimento é de ~50%, e caem para 466–518 esperados.
- **Modelo de fila em dois níveis:**
  1. Fila de entrada — eleitores chegam e são direcionados para dentro.
  2. Filas individuais internas — direcionam diretamente à cabine/urna específica.
- **Questão central resolvida:** com **pré-triagem na entrada** (eleitores direcionados a sub-filas específicas por destino já no ponto de entrada), o problema de "cabines calmas contaminadas pela fila de cabines movimentadas" é **estruturalmente resolvido**, independentemente de onde as cabines de alto volume estejam fisicamente.
- **Recomendação de balanceamento:** distribuir as 4 cabines de alto volume **uma por zona de entrada** (não concentrar todas numa entrada), pois:
  - **[resolvido — implementado]** No cenário `Hamad_3polos` as três de alto volume estão uma por porta: **24 → A (S4)**, **22 → B (S5)**, **23 → C (S6)**, e afastadas entre si nas três paredes (norte, leste e oeste). É a origem do nome "três polos". Carga esperada por porta: A 3.642, B 4.215, C 3.642.
  - Concentrar cria problema de vazão bruta naquela porta específica e concentra risco operacional num único ponto.
  - Distribuir equilibra a carga de pico entre entradas e isola geograficamente qualquer incidente.
- Direcionar recursos incrementais (equipe extra, sinalização) às sub-filas específicas de cabines de alto volume, em vez de reestruturar toda uma entrada em função delas.
- **Gargalo potencial sinalizado:** se a pré-triagem depende de equipe (conferência de documento, direcionamento verbal), essa etapa de verificação pode se tornar, ela mesma, um ponto de estrangulamento não paralelizável — independente de como as cabines forem alocadas. Deve ser considerado no dimensionamento de equipe.

---

## 5. Segurança e dimensionamento de staff (evento de referência ~2.200 m²)

Discussão paralela (contexto genérico de evento, útil como benchmark) sobre dimensionamento de segurança:
- Área interna segura: ~2.200 m²; pico de público 500–1.500 pessoas; perfil de risco moderado (público em pé, acesso parcialmente aberto); controle de acesso geral na entrada, sem revista de bolsa/detector de metal.
- Framework: m² define capacidade máxima, mas **headcount, perfil de risco e configuração de pontos de entrada** são os principais determinantes do número de seguranças (referência: UK Purple Guide).
- Faixas estimadas: cobertura interna 4–5 (500 pessoas) a 12–15 (1.500 pessoas); controle de acesso frontal 3–6; supervisão 1–2. **Total: 8–10 (mínimo) a 19–23 (pico)**.
- Premissas: ponto de acesso único, turno único, sem álcool. Presença de álcool ou duração >5–6h empurra para o teto da faixa.

---

## 6. Orçamento do 1º turno (telegrama revisado)

- **Estimativa inicial (reftel 131):** EUR 70.050 (já incluindo aluguel de espaço para eventual 2º turno).
- **Base de comparação corrigida:** EUR 46.000 (metade do valor de locação de espaço subtraída, para comparabilidade mais precisa com 2022, que só tinha aluguel de uma votação).
- **Aumento de custos:**
  - Em termos absolutos: 91,6% (vs. 192% apontado inicialmente, usando base não corrigida).
  - Em termos relativos ao crescimento de 40% no número de eleitores registrados: aumento de apenas 36% face a 2022.
  - Inflação na Irlanda entre 2022–2026: 19%.
- **Valor final solicitado após revisão:** **EUR 15.703,32** — economia de EUR 5.946,48 (27%) em relação ao valor anteriormente pedido. Parte significativa dessas despesas se repetirá em caso de 2º turno.

### 6.1 Itens contratados (detalhamento)
| Item | Valor (EUR) | Descrição |
|---|---|---|
| a) Segurança | 6.774,84 | 20 seguranças das 7h30 às 17h30 no dia da votação + 1 segurança por 16h no dia anterior |
| b) Eletricista | 5.387,40 | Modificação de cabeamento e instalação de pontos elétricos para as urnas |
| c) Banners de sinalização | 1.961,00 | Impressão e aluguel de bases, para organizar o espaço e simplificar o fluxo de eleitores |
| d) Separadores de fila (unifila) | 1.303,00 | 100 unidades (200 metros) para controle de fluxo |
|  | | **[resolvido]** O desenho adotado (seção 9) consome exatamente **100 postes e 146 m** de fita. Cabe, com folga de 27% em fita e folga nenhuma em poste. Falta só a reserva de 10% — **11 unidades, EUR 143 ao preço unitário deste item**. |
| e) Locação de mobiliário | 276,48 | Mesas adicionais para posicionamento das urnas |
| f) Seguro obrigatório | 2.642,00 | Cobre 1º e 2º turno, exigido pelo local contratado |

### 6.2 Contexto adicional relevante
- Em 2022, a primeira votação foi feita em espaço gratuito com contratação reduzida, mas gerou muitos problemas — inclusive necessidade de contratar espaço de última hora quando o local original recusou sediar o 2º turno.
- Por isso, em 2026, o Posto optou por espaço maior desde o início (que amplia custos, mas mitiga o risco recorrente de 2022).
- Espaço mais barato usado no 2º turno de 2022 estava indisponível em 2026 por conta da presidência irlandesa do Conselho da UE (redução de oferta de locais disponíveis).

---

## 7. Comunicação diplomática (nota verbal)

- Nota verbal em elaboração ao governo irlandês informando datas/local/horários acima (16 mil eleitores registrados, ~12 mil esperados).
- Pendências na última interação: número da nota verbal (placeholder [Nº] adotado) e formato de entrega (Word .docx confirmado, seguindo modelo de nota verbal anterior em PDF, incluindo brasão extraído do modelo).

---

## 8. Pontos em aberto / a validar antes do desenho de fluxo final

1. ~~**Confirmar dimensões reais do RDS Ballsbridge Hall 2**~~ — **[resolvido]** 50,2 × 44,5 m brutos na planta do RDS, 50,3 × 44,4 m de contorno útil na prancheta. Ver seção 3.
2. **Confirmar com o TSE/Cartório Eleitoral** a viabilidade procedimental de desagregar totalmente as seções de Dublin (Cenário 4/5) — decisão pendente de negociação orçamentária e de espaço/mesários.
3. **Resolver a inconsistência das 7 seções não contabilizadas** (Cork, Galway, Donegal, Limerick) na proposta oficial do TSE antes de fechar o número final de mesas/urnas.
4. **Definir método de identificação do eleitor** (biométrico/eletrônico vs. caderno físico) — decide diretamente entre Cenário 4 (32–35 urnas) e Cenário 5 (38+ urnas).
5. ~~**Integrar o modelo de fila de 3 entradas / 28 cabines**~~ — **[resolvido]** Unificado no cenário `Hamad_3polos` da Prancheta do Hall 2 e na contagem de `scripts/tensa_barreiras.py`: as 28 mesas em posições reais sobre a planta do RDS, com as três entradas nos vãos S4, S5 e S6 e o checkpoint a 20 m. Continua pendente o **número final de mesas** com o TSE (ponto 2) — se houver desagregação, o layout muda.
6. Validar se a pré-triagem na entrada será mediada por equipe humana (risco de gargalo) ou por sinalização/autoatendimento. **Ficou mais crítico:** o desenho adotado (1e) dispensa as bordas externas dos canais de entrada, então é sinalização e equipe que mantêm o eleitor dentro do canal entre a porta e o checkpoint. No pico a porta B recebe 14,1 pessoas/min e precisa de três posições de conferência a 10 s cada.
7. Confirmar dimensionamento final de segurança específico para o RDS (a análise da seção 5 é de um evento genérico de referência, não deste evento).

---

## 9. Desenho de fila adotado (separadores Tensa)

> Acrescentado depois da consolidação original. Fonte viva:
> `saidas/tensa_barreiras.md`; conta reproduzível em `scripts/tensa_barreiras.py`.

**Cenário 1e**, sobre o cenário `Hamad_3polos` da Prancheta do Hall 2:

1. **Duas linhas de 20 m** nos canais de entrada, uma entre A e B, outra entre B
   e C — só as divisórias que separam as correntes. As portas S4, S5 e S6 são
   contíguas (5,93 m cada, 0,29 m entre vãos), então os canais compartilham
   divisória. As bordas externas ficam a cargo de sinalização e equipe.
2. **Uma linha no meio de cada par** de mesas, separando as duas filas. Cabe
   porque a fila só começa a 4,10 m da parede, além dos mesários.
3. **Uma linha por mesa sem par**, rente à fila.
4. **Escada de comprimento 10/5/3 m** — 10 m nos três polos, 5 m nas de média,
   3 m nas de baixa.

**Quantidade: 100 postes de consumo, 111 a encomendar** com reserva de 10%;
146 m de fita; EUR 1.745 ex-VAT com entrega em Dublin (EUR 2.146 inc-VAT).

**Pareamento real das 28 mesas:** 9 pares (18 mesas), 7 mesas sem par (5, 6, 9,
12, 15, 16, 21) e os 3 polos (22, 23, 24). Não são "todas pareadas menos os
polos" — 5, 16 e 21 perderam o par quando os polos foram afastados, e 28 − 3 = 25
é ímpar de qualquer modo. Reposicionar mesas para formar novos pares economiza
3 postes por par.

**Riscos que a escolha aceita.** A escada 3/5/10 m não equaliza resiliência: a
60 s por voto e pico de 1,8× a média, as mesas de média transbordam em **14
minutos** contra 21 das de alta, porque 5 m sobre 518 esperados é proporção pior
que 10 m sobre 590. Doze mesas (oito de média, quatro de baixa) transbordam
entre 14 e 19 minutos de pico sustentado e passam a depender de gestão de piso.
O cenário 1i corrigia isso por 28 unidades a mais e foi descartado.
