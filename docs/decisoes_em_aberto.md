# Decisões de fluxo em aberto e como uma condiciona a outra

> Gerado por `scripts/decisoes_abertas.py` em 2026-09-13. Não editar à mão: mudar uma decisão é editar o módulo e regenerar. A seção "Decisões em aberto" do dashboard e `docs/instrucoes_fluxo.md` saem do mesmo registro.

## Fatos fixos (restrições que toda opção respeita)

| # | Fato | O que impõe | Fonte |
|---|---|---|---|
| F1 | **28 urnas, 51 seções, 16.794 aptos** | Configuração oficial do TSE (CSV de 13/08/2026). Desagregar as seções de Dublin não é mais viável (Posto, 13/09). Três urnas Dublin+Dublin com ~590 comparecentes esperados cada: MRV 22 (3313), 24 (3322), 23 (3315). | saidas/dados.json · contexto_eleicoes_dublin_2026.md §8.1 |
| F2 | **Identificação por caderno físico** | Único método disponível no exterior. Impõe ≤ 55 s por eleitor nas três urnas críticas e ≤ 66–68 s nas sete seguintes para fechar às 17h; a 90 s, 16 das 28 urnas estouram a janela. O arranjo da mesa (cadernos, quem identifica) é a pendência 5 do PENDENCIAS, sem recomendação ainda. | contexto_eleicoes_dublin_2026.md §8.2 · PENDENCIAS item 5 |
| F3 | **4 seguranças + mesários voluntários + polícia fora** | Orçamento comporta 4 seguranças (não 20). A organização do fluxo fica com voluntários identificados; a polícia fica do lado de fora do recinto. | Posto, 13/09 · contexto §8.1 decisão 4 |
| F4 | **Hall 2 50,0 × 44,5 m · Ring 3 44,0 × 35,0 m** | Dimensões reais confirmadas. Ring 3 a 14 m ao sul da fachada; posição lateral centrada em S5 por estimativa (bordo oeste a aferir). | RDS_Hall_2_Floorplan · contexto_ring3_2026.md §1 |
| F5 | **Comparecimento esperado 11.499 (base B)** | Taxa de 2022 por domicílio de origem, aplicada aos aptos de 2026. Não é oficial; todos os cenários usam a mesma base. Pico por porta 12,1 / 14,1 / 12,1 pessoas por minuto com três entradas. | scripts/comparecimento.py · registro_barreiras_hall2.md §3 |
| F6 | **200 CCB externos em mãos + 100 unifilas internos contratados** | Os separadores de barreira externa (2 m, da organizadora do RDS) servem o Ring 3 e podem ser comprados a mais (EUR 13,02/un.). Os 100 postes Tensa do item d) do orçamento são a fita interna do Hall 2 e são outra coisa. | DOCUMENTACAO_PROJETO.md §5.4 · contexto_ring3_2026.md §3.8 |

## Ordem recomendada de decisão

Cada camada só depende das anteriores; decidir fora da ordem obriga a rever a camada seguinte.

1. **D1** Portas: quantas e quais · **D2** Checkpoint interno · **D8** Identidade das filas: cor ou letra
2. **D1b** Porta ou rota preferencial · **D3** Desenho do Ring 3 e apoios da fita · **D4** Unifilas internas (postes Tensa)
3. **D5** Sinalização externa (parcialmente aprovada) · **D6** Sinalização interna (a elaborar)
4. **D7** Voluntários de apoio: quantos, onde, tarefas

## As decisões

### D1 — Portas: quantas e quais

**Pergunta.** Quantas portas da fachada sul recebem eleitor, e quais? Cada porta é uma corrente de fila desde o Ring 3 até o checkpoint.

Estado: **em aberto** · dono: Posto · depende de: nada · condiciona: D1b, D3, D4, D5, D6, D7 · restrições: F4, F5

- **3 portas: S4 (A), S5 (B), S6 (C)** **← o que as saídas de hoje assumem**  
  Decisão de 06/09. Vãos contíguos de 5,93 m com 0,29 m entre eles; pico de 12,1 / 14,1 / 12,1 pessoas/min. É o que todas as peças assumem.
  - se esta: **D3** → Três zonas no Ring 3 (A 11,2 · B 14,0 · C 11,2 m no desenho N–S; 8/10/8 raias). O módulo vivo já redesenha N zonas para N portas.
  - se esta: **D4** → Dois canais de entrada partilham divisória: bastam 2 linhas de 20 m entre A|B e B|C (22 postes), sem bordas externas no 1e.
  - se esta: **D5** → Uma placa de porta por cabeça de zona (3) e três vinis de fachada (P5).
  - se esta: **D6** → Um painel seção → mesa por porta (3) na entrada do salão.
  - se esta: **D7** → 1 marshal por porta (3) e 1 marshal por zona do Ring 3 (3).
- **2 portas (por exemplo S4 e S6)**  
  Menos canais e menos equipe de porta; cada corrente recebe ~18 pessoas/min no pico e cada zona do Ring 3 precisa guardar ~1.000 pessoas.
  - se esta: **D3** → Duas zonas, cada uma com ~20 m de largura: 14 raias por zona no N–S; a lotação total não muda, a caminhada por zona sobe.
  - se esta: **D4** → Uma só divisória de entrada (11 postes) e canais mais largos; a conferência no checkpoint precisa de 4 posições por porta a 10 s.
  - se esta: **D5** → Duas placas de cabeça de zona, dois vinis; a tabela mestra muda a coluna de porta.
  - se esta: **D6** → Dois painéis seção → mesa; cada painel lista 14 mesas.
  - se esta: **D7** → 2 marshals de porta, 2 de zona; checkpoint com 8 posições ao todo.
- **4 portas (S3 a S6 ou S4 a S7)**  
  Mais capilaridade: ~9 pessoas/min por porta. S3 e S7 têm recuo de emergência a confirmar (docs/CONTEXTO.md §9.3).
  - se esta: **D3** → Quatro zonas de ~10 m: 7 raias por zona no N–S; mais meias-voltas e mais divisórias curtas (o L–O passa a custar mais que o N–S).
  - se esta: **D4** → Três divisórias de entrada (33 postes) e 4 canais; o 1e perde 11 postes de folga.
  - se esta: **D5** → Quatro placas de cabeça de zona, quatro vinis de fachada.
  - se esta: **D6** → Quatro painéis seção → mesa, com 7 mesas cada.
  - se esta: **D7** → 4 marshals de porta, 4 de zona; checkpoint com 2 posições por porta.

Fontes: `scripts/decisoes.py` · `simulador/portas.js` · `DOCUMENTACAO_PROJETO.md §5.2`

### D2 — Checkpoint interno

**Pergunta.** Depois da porta, existe um ponto onde a equipe confere a seção do eleitor e o encaminha à mesa? Ele retém quando a fila da mesa está cheia?

Estado: **em aberto** · dono: Posto · depende de: nada · condiciona: D3, D4, D6, D7 · restrições: F2, F5

- **(a) Manter o checkpoint como válvula: confere e retém por mesa** **← o que as saídas de hoje assumem**  
  Cenário Claude: a 16 m da porta, 3 atendentes por entrada, 10 s por conferência; última mesa fecha às 17h03, P90 de 49 min, pico de 321 pessoas dentro e 962 no Ring 3. No pico a porta B recebe 14,1 pessoas/min e precisa de 3 posições.
  - se esta: **D3** → O Ring 3 recebe só o que o checkpoint devolve: pico de 962 no Ring 3 (cabe em qualquer desenho de 1.402 ou mais).
  - se esta: **D4** → Mantém as duas divisórias de 20 m e as 6 bochechas de portão do 1e (28 postes presos ao checkpoint).
  - se esta: **D6** → O painel seção → mesa fica no checkpoint (P6); o eleitor lê parado, com a equipe ao lado.
  - se esta: **D7** → 6 a 9 pessoas em posições fixas (2–3 por porta), mais 1 supervisor do checkpoint.
- **(b) Checkpoint só informativo: painel e equipe apontam, ninguém retém**  
  Guarda o ponto de consulta e a presença da equipe, mas a porta deixa de regular por mesa: a fila migra para dentro do salão quando uma mesa lota.
  - se esta: **D3** → A porta regula pela soma das filas de mesa, não por mesa: pico no Ring 3 sobe para ~1.500 (cenário "buffer" do simulador).
  - se esta: **D4** → As divisórias de entrada continuam; as bochechas de portão viram só guia. Filas de mesa passam a ser a única contenção: 1e ou C.
  - se esta: **D6** → Painel seção → mesa no mesmo lugar, maior, lido em movimento; placa alta por mesa.
  - se esta: **D7** → 1 orientador por porta no ponto informativo e 3 a 6 volantes no salão.
- **(c) Eliminar o checkpoint: fitas no piso da porta à mesa**  
  Simulado no motor oficial: fecha às 17h03 (mesmo horário), mas com porta livre 950 pessoas ficam dentro do salão e 5.795 chegam a fila cheia; com porta regulando às cegas o Ring 3 vai a 1.516–2.283. Perder-se custa 1–3 min no P90. O checkpoint não custa vazão; o que ele faz é reter por mesa.
  - se esta: **D3** → Ring 3 precisa guardar 1.516 a 2.283 no pico (porta regulando às cegas) ou o salão recebe 950: só os desenhos de ~2.000 servem, e a fita de contorno não contém.
  - se esta: **D4** → Libera os 28 postes do checkpoint para filas de mesa de 5/8/12 m; as filas de mesa viram a única contenção (1 conflito geométrico no Três polos).
  - se esta: **D6** → Painel seção → mesa na soleira da porta (10 s de leitura em pé) e placa alta numerada em cada mesa, obrigatória; fitas no piso por parede (214–463 m).
  - se esta: **D7** → 6 a 9 orientadores volantes no salão; a resposta a uma fila de 40 pessoas passa a ser deles, sem ponto de controle documentado para o Cartório.

Fontes: `docs/registro_fitas_no_piso_2026-09-12.md` · `docs/alternativa_fitas_no_piso.md` · `saidas/tensa_barreiras.md` · `DOCUMENTACAO_PROJETO.md §4.3`

### D8 — Identidade das filas: cor ou letra

**Pergunta.** Como o eleitor reconhece a sua fila, do Ring 3 até a porta: por cor (azul, âmbar, magenta), por letra (A, B, C) ou pelas duas?

Estado: **em aberto** · dono: Posto · depende de: nada · condiciona: D5, D6

- **Cor (azul, âmbar, magenta; distinguíveis em deuteranopia e protanopia)**  
  Evita duas nomenclaturas por letra no mesmo recinto (o RDS chama os portões de Gate D, Gate G).
  - se esta: **D5** → Faixa de cor nas placas de CCB e nos vinis de fachada.
  - se esta: **D6** → Painel seção → mesa e placa de mesa com a faixa de cor da porta.
- **Letra (A, B, C), como nos rótulos de planejamento**  
  Coincide com o simulador, a prancheta e o Ring 3; risco de confusão com Gate D/G.
  - se esta: **D5** → Letra em corpo grande nas placas de CCB e nos vinis.
  - se esta: **D6** → Painel e placas com a letra da porta.
- **Cor e letra juntas**  
  Redundância que custa só na diagramação; a letra fala, a cor se vê de longe.
  - se esta: **D5** → Faixa de cor + letra em todas as peças externas.
  - se esta: **D6** → Faixa de cor + letra em todas as peças internas.

Fontes: `DOCUMENTACAO_PROJETO.md §6.3 e §9.8 item 8` · `scripts/decisoes.py (nomenclatura_portas)`

### D1b — Porta ou rota preferencial

**Pergunta.** Eleitores prioritários (~296: 211 com 60+ e 85 PcD, ~33 por hora no pico) entram por uma porta própria, por uma rota própria na mesma porta, ou pela fila comum?

Estado: **em aberto** · dono: Posto · depende de: D1 · condiciona: D5, D7 · restrições: F3

- **Rota prioritária pelo apron, com 1 agente, até a porta da sua zona** **← o que as saídas de hoje assumem**  
  O que o plano do Ring 3 prevê: nenhum prioritário entra no serpenteado (130 m de percurso); do desembarque direto à porta, pavimentado.
  - se esta: **D5** → Sinalizar a rota prioritária desde a rua (P0 e portão P1); nenhuma placa de porta a mais.
  - se esta: **D7** → 1 agente de acessibilidade no apron; o marshal de porta recebe o prioritário fora de fila.
- **Porta dedicada (S3 ou S7), fora das correntes**  
  Isola o prioritário da corrente de chegada que desce pelo apron leste (hoje cruza a saída S8). Exige checkpoint próprio ou painel na soleira.
  - se esta: **D5** → Uma placa de porta a mais ("Atendimento prioritário") e vinil na fachada; rota sinalizada desde P0.
  - se esta: **D7** → 2 pessoas: 1 na porta dedicada, 1 conduzindo do portão; a porta precisa de posição de conferência própria.
- **Sem rota própria: prioridade tratada na cabeça de cada fila**  
  Menos equipe, mas 296 pessoas atravessam o apron sem guia e a cabeça de fila precisa negociar a passagem a cada caso.
  - se esta: **D5** → Placa "prioridade: apresente-se ao marshal" em P4 (cabeça de cada zona).
  - se esta: **D7** → Nenhum agente dedicado; cada marshal de zona absorve ~11 casos por hora no pico.

Fontes: `saidas/plano_ring3.md §10` · `DOCUMENTACAO_PROJETO.md §5.7`

### D3 — Desenho do Ring 3 e apoios da fita

**Pergunta.** Qual desenho de fila externa, e com que barreira? Se a divisória for fita com CCB só na ponta, quantos apoios a fita leva?

Estado: **em aberto** · dono: Posto · depende de: D1, D2 · condiciona: D5, D7 · restrições: F4, F6

- **Plano vigente: garganta de pré-triagem ao sul, 3 serpenteados e 2 baias (1.402)** **← o que as saídas de hoje assumem**  
  Calculado a 39 × 35 m; é o que decisoes.py usa para as quotas por entrada (445/513/445). 300 separadores (314 na reconstrução a 44 × 35), 100 a comprar.
  - se esta: **D5** → P3 (garganta) e P4 (cabeças) continuam existindo; 300 CCB disponíveis para placas.
  - se esta: **D7** → 3 agentes de pré-triagem na garganta (gargalo potencial) + 3 marshals de corredor.
- **Raias norte-sul, barreira inteira, corredor em L (1.997)**  
  Entrada pelo canto nordeste, corredor em L de 3,0 m, raias de 32 m. 371 separadores, 171 a comprar (EUR 2.226); 160 m de fita no contorno.
  - se esta: **D5** → A pré-triagem sai do Ring 3: P3 migra para o portão e o corredor leste; 371 CCB para pendurar as placas de porta nas cabeças de zona.
  - se esta: **D7** → Sem garganta: pré-triagem a montante (portão) com 2–3 pessoas; 1 marshal por zona; 1 no L, onde a corrente de chegada cruza a saída S8.
- **Raias leste-oeste, barreira inteira, corredor em L (1.964)**  
  Mesmos 371 separadores; descarga da zona B alinhada com o eixo de S5 (desvio 0,0 m contra 5,5 m no N–S); 66 meias-voltas.
  - se esta: **D5** → Como o N–S; a placa de porta fica na borda norte, no portão de descarga.
  - se esta: **D7** → Como o N–S; mais meias-voltas exigem mais atenção do marshal de zona.
- **Raias norte-sul, CCB só na ponta + fita grossa (1.997)**  
  39 separadores, nenhum a comprar, 662 m de fita grossa. Cada divisória fica com 28,8 m de fita sem apoio: a 5 m são 115 apoios; se forem CCB, o total volta a 154.
  - se esta: **D5** → Só 39 CCB, nas cabeças e na separação da zona C: as placas de porta vão exatamente ali; o resto é fita e não segura placa.
  - se esta: **D7** → Fita delimita, não contém: 1 marshal por zona no pico, obrigatório, mais 1 no L; sem eles a fila passa de A para B.
- **Raias leste-oeste, CCB só na ponta + fita grossa (1.964)**  
  82 separadores, nenhum a comprar, 576 m de fita grossa; 66 divisórias curtas.
  - se esta: **D5** → 82 CCB, um por ponta de divisória: mais pontos de fixação para placas.
  - se esta: **D7** → Como o N–S com fita; divisórias de 11–14 m precisam de menos apoio.

Fontes: `contexto_ring3_2026.md` · `saidas/ring3.json` · `saidas/plano_ring3_horizontal.md` · `saidas/plano_ring3.md`

### D4 — Unifilas internas (postes Tensa)

**Pergunta.** Onde vai a fita retrátil dentro do salão: nas filas de mesa, nos canais da porta ao checkpoint, nos dois, ou só num deles?

Estado: **em aberto** · dono: Posto · depende de: D1, D2 · condiciona: D6, D7 · restrições: F2, F6

- **1e: linha no meio de cada par + linha por mesa sem par + 2 divisórias até o checkpoint** **← o que as saídas de hoje assumem**  
  Adotado em 07/09: 100 postes (111 com reserva), 146 m de fita, EUR 1.745 ex-VAT. Sem as bordas externas dos canais: sinalização e equipe seguram o eleitor no canal.
  - se esta: **D6** → Toda mesa tem guia; a placa alta por mesa é reforço, não necessidade.
  - se esta: **D7** → 1 orientador para cada 3 mesas; equipe segura a borda externa dos canais de entrada. A 60 s por voto, 12 mesas transbordam em 14–19 min de pico.
- **1i: mesma topologia, filas dimensionadas para 20 min de pico**  
  126 postes (139 com reserva): as mesas de média sobem de 5 para 6–7,5 m. O par 17–18 não tem os 7,5 m na parede leste.
  - se esta: **D6** → Como o 1e.
  - se esta: **D7** → Menos gestão de piso nas mesas de média; 26 postes a mais.
- **A: só as duas divisórias da porta ao checkpoint (28 postes)**  
  Nenhuma barreira nas 28 mesas: da triagem em diante o eleitor circula solto e a ordem nas mesas fica com a equipe. EUR 1.200 a menos que o 1e.
  - se esta: **D6** → Placa alta numerada em todas as 28 mesas, obrigatória: sem canal, a placa é o único guia.
  - se esta: **D7** → 5 orientadores a mais só para as mesas (1 para cada 3 que acumulam); se pagos, EUR 1.569, e o total (2.114) passa o 1e.
- **B: só pares e polos (47 postes), nada na entrada**  
  Linha do meio de cada par e os três polos; as três correntes chegam juntas ao checkpoint. 7 mesas sem guia (3.028 esperados).
  - se esta: **D6** → Placa alta nas 7 mesas sem guia (5, 6, 9, 12, 15, 16, 21).
  - se esta: **D7** → Sem divisórias de entrada, as 3 correntes se misturam antes do checkpoint: 1 marshal por porta dentro do salão, além dos orientadores das mesas soltas.
- **B2: B mais as de média sem par (63 postes)**  
  As mesas 9, 15, 16 e 21 contam como grandes e ganham linha; sobram 3 mesas sem guia (1.079 esperados).
  - se esta: **D6** → Placa alta nas 3 mesas sem guia (5, 6, 12).
  - se esta: **D7** → Como B, com menos mesas para a equipe cobrir.
- **C: síntese — divisórias do checkpoint + pares + polos (75 postes)**  
  O 1e sem as sete linhas das mesas soltas. O único corte que o documento de hipóteses recomenda: EUR 1.325 ex-VAT, 17 postes de folga.
  - se esta: **D6** → Placa alta nas 7 mesas sem guia (5, 6, 9, 12, 15, 16, 21).
  - se esta: **D7** → Os 7 postos das mesas soltas passam à equipe: 2 a 3 orientadores para elas.

Fontes: `saidas/tensa_barreiras.md` · `saidas/propostas_alternativas.md` · `registro_barreiras_hall2.md` · `saidas/tensa_barreiras.json`

### D5 — Sinalização externa (parcialmente aprovada)

**Pergunta.** P0, P1 e P2 vão penduradas nas paredes do RDS (aprovado). Falta: as placas nas CCBs do Ring 3 dizendo, por porta, quais seções e mesas entram por ela. Quantas, onde e com que identidade de fila?

Estado: **parcial** · dono: Posto · depende de: D1, D1b, D3, D8 · condiciona: D7 · restrições: F1

- **P0–P2 nas paredes do RDS + uma placa por porta nas CCBs de cabeça de zona** **← o que as saídas de hoje assumem**  
  Cada placa lista as seções (51 linhas no total, ordenadas por seção) e as mesas que entram por aquela porta, com a identidade da fila (D8). Substitui os totens de P3/P4 nos desenhos sem garganta.
  - se esta: **D7** → A placa na CCB responde "é aqui?" sem equipe; o marshal de zona só corrige quem errou (captura em P4).
- **P0–P2 nas paredes do RDS e nada nas CCBs (só os totens de P4)**  
  Menos peças impressas; a confirmação da fila depende da equipe e dos totens da cabeça de cada serpenteado.
  - se esta: **D7** → Mais consultas ao marshal de zona ("é esta a minha fila?"): 1 pessoa a mais por zona no pico.

Fontes: `saidas/plano_sinalizacao.html` · `DOCUMENTACAO_PROJETO.md §6` · `scripts/gera_plano_sinalizacao.py`

### D6 — Sinalização interna (a elaborar)

**Pergunta.** O que sinalizar dentro do salão: (1) a distribuição das seções por mesa, no checkpoint ou na porta; (2) o par de mesas e as seções de cada mesa; (3) o que mais.

Estado: **em aberto** · dono: Posto · depende de: D1, D2, D4, D8 · condiciona: D7 · restrições: F1

- **P6 como está: 3 faixas suspensas por bloco + 28 totens de mesa + P7 nas saídas** **← o que as saídas de hoje assumem**  
  O plano de sinalização de 05/09; nada foi acrescentado desde então. É o mínimo que o dashboard assume.
  - se esta: **D7** → Sem placa alta, o eleitor que perde a fila pergunta: orientadores volantes absorvem.
- **Painel seção → mesa no checkpoint + placa do par suspensa nas treliças (14) + placa alta por mesa**  
  Por par de mesas, 14 peças em vez de 28, penduradas nas treliças a 7 m (as paredes não aceitam adesivo). Exige rigging autorizado pelo RDS e plataforma elevatória na véspera; não obstruir luminária de emergência, detector de fumaça nem placa de EXIT.
  - se esta: **D7** → A placa alta é visível com 300 a 950 pessoas dentro; menos consultas ao orientador.
- **Painel seção → mesa na soleira da porta + placa alta por mesa + fitas no piso**  
  A variante para D2 = (c): leitura em pé na soleira (10 s), erro de 10–25 % assumido; fitas no piso por parede (214 m) ou pela atribuição da decisão (463 m, 18 cruzamentos).
  - se esta: **D7** → Orientadores volantes no salão (6–9) em vez de posições fixas.

Sinalizações adicionais a prever:
- Placa alta numerada (MRV) em cada mesa, legível de 40 m com o salão cheio.
- "Fim da fila" móvel para as mesas de 10 m (polos) e placa "esta fila: MRV n".
- Saídas S2 e S8 (P7) e "não volte pelo salão".
- Balcão de dúvidas / "não sei minha seção" (em P1, fora; repetido no checkpoint).
- Rota prioritária e banheiros (portaloos) desde P0.
- Identidade da fila (cor ou letra) coerente com a raia do Ring 3 até a porta.

Fontes: `DOCUMENTACAO_PROJETO.md §6.2 (P6, P7) e §6.6` · `docs/alternativa_fitas_no_piso.md`

### D7 — Voluntários de apoio: quantos, onde, tarefas

**Pergunta.** Quantas pessoas, em que postos e com que tarefa, para comunicar a sinalização, orientar o eleitor e organizar as filas, com 4 seguranças fixos e polícia fora.

Estado: **em aberto** · dono: Posto · depende de: D1, D1b, D2, D3, D4, D5, D6 · condiciona: nada · restrições: F3

- **Equipe dimensionada para o pico, derivada das outras decisões** **← o que as saídas de hoje assumem**  
  A tabela por posto sai das opções vigentes de D1–D6 (gera_instrucoes_fluxo.py): portão, corredor, zonas, portas, checkpoint, salão, saídas, acessibilidade.
- **Equipe mínima: 1 pessoa por posto, sem reforço de pico**  
  Cobre a sinalização mas não o pico das 8h–10h; as filas de mesa de média transbordam em 14 min sem ninguém para redirecionar.

Fontes: `saidas/plano_ring3.md §11` · `DOCUMENTACAO_PROJETO.md §5.7` · `saidas/propostas_alternativas.md` · `docs/instrucoes_fluxo.md`

## Matriz "se … então …"

Linhas: opção de uma decisão. Colunas: decisões que ela condiciona.

| Se … | D3 | D4 | D5 | D6 | D7 |
|---|---|---|---|---|---|
| **D1** = 3 portas: S4 (A), S5 (B), S6 (C) | Três zonas no Ring 3 (A 11,2 · B 14,0 · C 11,2 m no desenho N–S; 8/10/8 raias). O módulo vivo já redesenha N zonas para N portas. | Dois canais de entrada partilham divisória: bastam 2 linhas de 20 m entre A|B e B|C (22 postes), sem bordas externas no 1e. | Uma placa de porta por cabeça de zona (3) e três vinis de fachada (P5). | Um painel seção → mesa por porta (3) na entrada do salão. | 1 marshal por porta (3) e 1 marshal por zona do Ring 3 (3). |
| **D1** = 2 portas (por exemplo S4 e S6) | Duas zonas, cada uma com ~20 m de largura: 14 raias por zona no N–S; a lotação total não muda, a caminhada por zona sobe. | Uma só divisória de entrada (11 postes) e canais mais largos; a conferência no checkpoint precisa de 4 posições por porta a 10 s. | Duas placas de cabeça de zona, dois vinis; a tabela mestra muda a coluna de porta. | Dois painéis seção → mesa; cada painel lista 14 mesas. | 2 marshals de porta, 2 de zona; checkpoint com 8 posições ao todo. |
| **D1** = 4 portas (S3 a S6 ou S4 a S7) | Quatro zonas de ~10 m: 7 raias por zona no N–S; mais meias-voltas e mais divisórias curtas (o L–O passa a custar mais que o N–S). | Três divisórias de entrada (33 postes) e 4 canais; o 1e perde 11 postes de folga. | Quatro placas de cabeça de zona, quatro vinis de fachada. | Quatro painéis seção → mesa, com 7 mesas cada. | 4 marshals de porta, 4 de zona; checkpoint com 2 posições por porta. |
| **D2** = (a) Manter o checkpoint como válvula: confere e retém por mesa | O Ring 3 recebe só o que o checkpoint devolve: pico de 962 no Ring 3 (cabe em qualquer desenho de 1.402 ou mais). | Mantém as duas divisórias de 20 m e as 6 bochechas de portão do 1e (28 postes presos ao checkpoint). |  | O painel seção → mesa fica no checkpoint (P6); o eleitor lê parado, com a equipe ao lado. | 6 a 9 pessoas em posições fixas (2–3 por porta), mais 1 supervisor do checkpoint. |
| **D2** = (b) Checkpoint só informativo: painel e equipe apontam, ninguém retém | A porta regula pela soma das filas de mesa, não por mesa: pico no Ring 3 sobe para ~1.500 (cenário "buffer" do simulador). | As divisórias de entrada continuam; as bochechas de portão viram só guia. Filas de mesa passam a ser a única contenção: 1e ou C. |  | Painel seção → mesa no mesmo lugar, maior, lido em movimento; placa alta por mesa. | 1 orientador por porta no ponto informativo e 3 a 6 volantes no salão. |
| **D2** = (c) Eliminar o checkpoint: fitas no piso da porta à mesa | Ring 3 precisa guardar 1.516 a 2.283 no pico (porta regulando às cegas) ou o salão recebe 950: só os desenhos de ~2.000 servem, e a fita de contorno não contém. | Libera os 28 postes do checkpoint para filas de mesa de 5/8/12 m; as filas de mesa viram a única contenção (1 conflito geométrico no Três polos). |  | Painel seção → mesa na soleira da porta (10 s de leitura em pé) e placa alta numerada em cada mesa, obrigatória; fitas no piso por parede (214–463 m). | 6 a 9 orientadores volantes no salão; a resposta a uma fila de 40 pessoas passa a ser deles, sem ponto de controle documentado para o Cartório. |
| **D8** = Cor (azul, âmbar, magenta; distinguíveis em deuteranopia e protanopia) |  |  | Faixa de cor nas placas de CCB e nos vinis de fachada. | Painel seção → mesa e placa de mesa com a faixa de cor da porta. |  |
| **D8** = Letra (A, B, C), como nos rótulos de planejamento |  |  | Letra em corpo grande nas placas de CCB e nos vinis. | Painel e placas com a letra da porta. |  |
| **D8** = Cor e letra juntas |  |  | Faixa de cor + letra em todas as peças externas. | Faixa de cor + letra em todas as peças internas. |  |
| **D1b** = Rota prioritária pelo apron, com 1 agente, até a porta da sua zona |  |  | Sinalizar a rota prioritária desde a rua (P0 e portão P1); nenhuma placa de porta a mais. |  | 1 agente de acessibilidade no apron; o marshal de porta recebe o prioritário fora de fila. |
| **D1b** = Porta dedicada (S3 ou S7), fora das correntes |  |  | Uma placa de porta a mais ("Atendimento prioritário") e vinil na fachada; rota sinalizada desde P0. |  | 2 pessoas: 1 na porta dedicada, 1 conduzindo do portão; a porta precisa de posição de conferência própria. |
| **D1b** = Sem rota própria: prioridade tratada na cabeça de cada fila |  |  | Placa "prioridade: apresente-se ao marshal" em P4 (cabeça de cada zona). |  | Nenhum agente dedicado; cada marshal de zona absorve ~11 casos por hora no pico. |
| **D3** = Plano vigente: garganta de pré-triagem ao sul, 3 serpenteados e 2 baias (1.402) |  |  | P3 (garganta) e P4 (cabeças) continuam existindo; 300 CCB disponíveis para placas. |  | 3 agentes de pré-triagem na garganta (gargalo potencial) + 3 marshals de corredor. |
| **D3** = Raias norte-sul, barreira inteira, corredor em L (1.997) |  |  | A pré-triagem sai do Ring 3: P3 migra para o portão e o corredor leste; 371 CCB para pendurar as placas de porta nas cabeças de zona. |  | Sem garganta: pré-triagem a montante (portão) com 2–3 pessoas; 1 marshal por zona; 1 no L, onde a corrente de chegada cruza a saída S8. |
| **D3** = Raias leste-oeste, barreira inteira, corredor em L (1.964) |  |  | Como o N–S; a placa de porta fica na borda norte, no portão de descarga. |  | Como o N–S; mais meias-voltas exigem mais atenção do marshal de zona. |
| **D3** = Raias norte-sul, CCB só na ponta + fita grossa (1.997) |  |  | Só 39 CCB, nas cabeças e na separação da zona C: as placas de porta vão exatamente ali; o resto é fita e não segura placa. |  | Fita delimita, não contém: 1 marshal por zona no pico, obrigatório, mais 1 no L; sem eles a fila passa de A para B. |
| **D3** = Raias leste-oeste, CCB só na ponta + fita grossa (1.964) |  |  | 82 CCB, um por ponta de divisória: mais pontos de fixação para placas. |  | Como o N–S com fita; divisórias de 11–14 m precisam de menos apoio. |
| **D4** = 1e: linha no meio de cada par + linha por mesa sem par + 2 divisórias até o checkpoint |  |  |  | Toda mesa tem guia; a placa alta por mesa é reforço, não necessidade. | 1 orientador para cada 3 mesas; equipe segura a borda externa dos canais de entrada. A 60 s por voto, 12 mesas transbordam em 14–19 min de pico. |
| **D4** = 1i: mesma topologia, filas dimensionadas para 20 min de pico |  |  |  | Como o 1e. | Menos gestão de piso nas mesas de média; 26 postes a mais. |
| **D4** = A: só as duas divisórias da porta ao checkpoint (28 postes) |  |  |  | Placa alta numerada em todas as 28 mesas, obrigatória: sem canal, a placa é o único guia. | 5 orientadores a mais só para as mesas (1 para cada 3 que acumulam); se pagos, EUR 1.569, e o total (2.114) passa o 1e. |
| **D4** = B: só pares e polos (47 postes), nada na entrada |  |  |  | Placa alta nas 7 mesas sem guia (5, 6, 9, 12, 15, 16, 21). | Sem divisórias de entrada, as 3 correntes se misturam antes do checkpoint: 1 marshal por porta dentro do salão, além dos orientadores das mesas soltas. |
| **D4** = B2: B mais as de média sem par (63 postes) |  |  |  | Placa alta nas 3 mesas sem guia (5, 6, 12). | Como B, com menos mesas para a equipe cobrir. |
| **D4** = C: síntese — divisórias do checkpoint + pares + polos (75 postes) |  |  |  | Placa alta nas 7 mesas sem guia (5, 6, 9, 12, 15, 16, 21). | Os 7 postos das mesas soltas passam à equipe: 2 a 3 orientadores para elas. |
| **D5** = P0–P2 nas paredes do RDS + uma placa por porta nas CCBs de cabeça de zona |  |  |  |  | A placa na CCB responde "é aqui?" sem equipe; o marshal de zona só corrige quem errou (captura em P4). |
| **D5** = P0–P2 nas paredes do RDS e nada nas CCBs (só os totens de P4) |  |  |  |  | Mais consultas ao marshal de zona ("é esta a minha fila?"): 1 pessoa a mais por zona no pico. |
| **D6** = P6 como está: 3 faixas suspensas por bloco + 28 totens de mesa + P7 nas saídas |  |  |  |  | Sem placa alta, o eleitor que perde a fila pergunta: orientadores volantes absorvem. |
| **D6** = Painel seção → mesa no checkpoint + placa do par suspensa nas treliças (14) + placa alta por mesa |  |  |  |  | A placa alta é visível com 300 a 950 pessoas dentro; menos consultas ao orientador. |
| **D6** = Painel seção → mesa na soleira da porta + placa alta por mesa + fitas no piso |  |  |  |  | Orientadores volantes no salão (6–9) em vez de posições fixas. |
