# Decisões de fluxo: as que faltam, as que já saíram e como uma condiciona a outra

> Gerado por `scripts/decisoes_abertas.py` (registro de 2026-09-13). Não editar à mão: mudar uma decisão é editar o módulo e regenerar. A seção "Decisões" do dashboard e `docs/instrucoes_fluxo.md` saem do mesmo registro.

## Premissas

- **Identificação por caderno físico.** Único método disponível no exterior. Impõe ≤ 55 s por eleitor nas três urnas críticas e ≤ 66–68 s nas sete seguintes para fechar às 17h; a 90 s, 16 das 28 urnas estouram a janela. (contexto_eleicoes_dublin_2026.md §8.2)
- **4 seguranças + mesários voluntários + polícia fora.** Orçamento comporta 4 seguranças (não 20). A organização do fluxo fica com voluntários identificados; a polícia fica do lado de fora do recinto. (Posto, 13/09 · contexto §8.1 decisão 4)

## Decisões em aberto

### D9 — (a) Como fazer a identificação no caderno físico

**Pergunta.** Com 28 urnas e caderno físico, as três urnas críticas (MRV 22, 24, 23; ~590 comparecentes) só fecham às 17h a ≤ 55 s por eleitor. Como se organiza a identificação na mesa receptora para chegar a esse ritmo?

Dono: Posto + Cartório Eleitoral · depende de: nada · condiciona: D2, D6, D7

- **(i) Caderno único em ordem alfabética, um mesário identificando**  
  Hipótese do Posto sobre como o caderno chega (a confirmar). É o arranjo que a simulação por urna trata como serial: a 55 s por eleitor, fecha 20h37 na mesa mais carregada.
  - se esta: **D2** → A mesa é o gargalo e retém por si só: o checkpoint só faz sentido como válvula (reter por mesa) — as fitas no piso não ajudam a mesa.
  - se esta: **D7** → Nada muda na equipe de piso; o esforço vai para a mesa (mesários).
- **(ii) Caderno dividido por seção agregada, um mesário por caderno**  
  23 das 28 urnas somam duas seções: dois cadernos, dois mesários identificando em paralelo; o terceiro opera a urna. É o arranjo que `simula_fluxo.py` chama de 'dois cadernos': fila zero, fecha 17h00.
  - se esta: **D2** → A mesa deixa de ser o gargalo; o checkpoint pode ser leve (2 por porta) ou ceder lugar às fitas sem que a fila migre para dentro.
  - se esta: **D7** → Pré-triagem precisa dizer ao eleitor a SEÇÃO, não só a mesa: o painel seção → mesa ganha a coluna do caderno.
- **(iii) Caderno dividido por faixa de letras, um mesário por faixa**  
  Independe de como o caderno chega (se for único alfabético, corta-se ao meio). Equilibra melhor que por seção quando uma seção é maior que a outra.
  - se esta: **D2** → Como (ii).
  - se esta: **D7** → Placa da mesa com as faixas de letras (A–L / M–Z); orientador aponta a fila certa.
- **(iv) Identificação em paralelo com o voto (o mesário localiza o próximo enquanto o anterior vota)**  
  Um caderno só, mas o tempo de ciclo vira o maior entre identificação e voto, não a soma. Fecha 17h01 a 55 s no modelo por urna. Depende de disciplina de mesa, não de material.
  - se esta: **D2** → Mesa no limite (55 s): o checkpoint como válvula continua necessário nas três críticas.
  - se esta: **D7** → Treinamento dos mesários vira parte do plano de fluxo (webinar).
- **(v) Pré-triagem na fila: eleitor chega à mesa com documento na mão e seção sabida**  
  Complementa qualquer das anteriores: tira da mesa os 10–20 s de procurar documento e seção. Custa equipe na fila, não na mesa.
  - se esta: **D2** → Se houver checkpoint, a pré-triagem acontece nele; sem checkpoint, acontece na fila da mesa, por orientador.
  - se esta: **D7** → 1 orientador a cada 3 mesas conferindo documento na fila.

Fontes: `PENDENCIAS item 5` · `contexto_eleicoes_dublin_2026.md §8.2` · `DOCUMENTACAO_PROJETO.md §4.2 e §9.7`

### D2 — (b) Checkpoint ou sinalização por fitas?

**Pergunta.** Depois da porta, o eleitor passa por um ponto onde a equipe confere a seção, aponta a mesa e retém quando a fila da mesa está cheia — ou segue fitas no piso da porta à mesa, sem ponto de controle?

Dono: Posto · depende de: D9 · condiciona: D4, D6, D7

- **Checkpoint: confere a seção e retém por mesa** **← o que as saídas de hoje assumem**  
  Cenário Claude: a 16 m da porta, 3 atendentes por entrada, 10 s por conferência; última mesa fecha às 17h03, P90 de 49 min, pico de 321 pessoas dentro e 962 no Ring 3. No pico a porta B recebe 14,1 pessoas/min e precisa de 3 posições. Variante leve: só informativo (aponta, não retém).
  - se esta: **D4** → As divisórias do canal de entrada levam até o checkpoint (1e: 2 linhas de 20 m + 6 bochechas); nos traçados em T (1f/1g/1h) o checkpoint fica no topo do canal B.
  - se esta: **D6** → O painel seção → mesa fica no checkpoint (P6); o eleitor lê parado, com a equipe ao lado.
  - se esta: **D7** → 6 a 9 pessoas em posições fixas (2–3 por porta), mais 1 supervisor do checkpoint.
- **Sinalização por fitas no piso, sem checkpoint**  
  Simulado no motor oficial: fecha às 17h03 (mesmo horário), mas com porta livre 950 pessoas ficam dentro do salão e 5.795 chegam a fila cheia; com porta regulando às cegas o Ring 3 vai a 1.516–2.283. Perder-se custa 1–3 min no P90. O checkpoint não custa vazão; o que ele faz é reter por mesa.
  - se esta: **D4** → Os postes do canal de entrada viram guia curta (1h: 5 m + braços de 3 m) e as filas de mesa são a única contenção; fitas no piso por parede (214–463 m).
  - se esta: **D6** → Painel seção → mesa na soleira da porta (10 s de leitura em pé) e placa alta numerada em cada mesa, obrigatória.
  - se esta: **D7** → 6 a 9 orientadores volantes no salão; a resposta a uma fila de 40 pessoas passa a ser deles, sem ponto de controle documentado para o Cartório.

Fontes: `docs/registro_fitas_no_piso_2026-09-12.md` · `docs/alternativa_fitas_no_piso.md` · `saidas/tensa_barreiras.md` · `DOCUMENTACAO_PROJETO.md §4.3`

## Decididas em 13/09/2026

| Decisão | Escolha | Resumo |
|---|---|---|
| **D1** Portas: quantas e quais | 3 entradas (S4 A, S5 B, S6 C) e 2 saídas (S2, S8) | Decisão de 06/09, confirmada em 13/09. Vãos contíguos de 5,93 m; pico de 12,1 / 14,1 / 12,1 pessoas/min. O1 também fica fechada no dia. |
| **D8** Identidade das filas: letra | Letra (A, B, C), como nos rótulos de planejamento | Decidido em 13/09. Coincide com o simulador, a prancheta e o Ring 3. |
| **D3** Desenho do Ring 3 e apoios da fita | Raias leste-oeste, CCB só na ponta + fita grossa (1.964 pessoas) | Decidido em 13/09. Entrada pelo canto nordeste, corredor em L de 3,0 m. 82 separadores contados, registrados 100 para dar margem; nenhum a comprar; 576 m de fita grossa com 66 apoios a cada 5 m; 66 meias-voltas. |
| **D4** Unifilas internas (postes Tensa) | 1e: duas divisórias de 20 m (A|B e B|C) até o checkpoint + regra de mesa | Adotado. As duas linhas que separam as três correntes da porta ao checkpoint, com 6 bochechas de portão; nas mesas, a regra de 13/09. |

## Planos derivados (não são decisões)

- **D1b Rota preferencial (plano derivado)** — Rota prioritária pelo apron, com 1 agente, até a porta da sua zona. O que o plano do Ring 3 prevê: nenhum prioritário entra no serpenteado.
- **D5 Sinalização externa (plano derivado)** — P0–P2 nas paredes do RDS + uma placa por porta nas CCBs de cabeça de zona. Cada placa lista as seções e as mesas (número eleitor e MRV) que entram por aquela porta, com a letra da fila.
- **D6 Sinalização interna (plano derivado)** — P6 como está: 3 faixas suspensas por bloco + 28 totens de mesa + P7 nas saídas. O plano de sinalização de 05/09, agora com número eleitor em destaque e MRV oficial ao lado.
  - Placa alta com o número eleitor (e o MRV oficial em corpo menor) em cada mesa, legível de 40 m.
  - "Fim da fila" móvel para as mesas vermelhas (10 m) e placa "esta fila: mesa n".
  - Saídas S2 e S8 (P7) e "não volte pelo salão".
  - Balcão de dúvidas / "não sei minha seção" (em P1, fora; repetido no checkpoint).
  - Rota prioritária e banheiros (portaloos) desde P0.
- **D7 Voluntários de apoio (plano derivado)** — Equipe dimensionada para o pico, derivada das outras decisões. A tabela por posto sai de gera_instrucoes_fluxo.py.

## Matriz "se … então …" (opções das decisões em aberto)

| Se … | D2 Checkpoint ou fitas | D4 Unifilas internas | D6 Sinalização interna | D7 Voluntários |
|---|---|---|---|---|
| **D9** = (i) Caderno único em ordem alfabética, um mesário identificando | A mesa é o gargalo e retém por si só: o checkpoint só faz sentido como válvula (reter por mesa) — as fitas no piso não ajudam a mesa. |  |  | Nada muda na equipe de piso; o esforço vai para a mesa (mesários). |
| **D9** = (ii) Caderno dividido por seção agregada, um mesário por caderno | A mesa deixa de ser o gargalo; o checkpoint pode ser leve (2 por porta) ou ceder lugar às fitas sem que a fila migre para dentro. |  |  | Pré-triagem precisa dizer ao eleitor a SEÇÃO, não só a mesa: o painel seção → mesa ganha a coluna do caderno. |
| **D9** = (iii) Caderno dividido por faixa de letras, um mesário por faixa | Como (ii). |  |  | Placa da mesa com as faixas de letras (A–L / M–Z); orientador aponta a fila certa. |
| **D9** = (iv) Identificação em paralelo com o voto (o mesário localiza o próximo enquanto o anterior vota) | Mesa no limite (55 s): o checkpoint como válvula continua necessário nas três críticas. |  |  | Treinamento dos mesários vira parte do plano de fluxo (webinar). |
| **D9** = (v) Pré-triagem na fila: eleitor chega à mesa com documento na mão e seção sabida | Se houver checkpoint, a pré-triagem acontece nele; sem checkpoint, acontece na fila da mesa, por orientador. |  |  | 1 orientador a cada 3 mesas conferindo documento na fila. |
| **D2** = Checkpoint: confere a seção e retém por mesa |  | As divisórias do canal de entrada levam até o checkpoint (1e: 2 linhas de 20 m + 6 bochechas); nos traçados em T (1f/1g/1h) o checkpoint fica no topo do canal B. | O painel seção → mesa fica no checkpoint (P6); o eleitor lê parado, com a equipe ao lado. | 6 a 9 pessoas em posições fixas (2–3 por porta), mais 1 supervisor do checkpoint. |
| **D2** = Sinalização por fitas no piso, sem checkpoint |  | Os postes do canal de entrada viram guia curta (1h: 5 m + braços de 3 m) e as filas de mesa são a única contenção; fitas no piso por parede (214–463 m). | Painel seção → mesa na soleira da porta (10 s de leitura em pé) e placa alta numerada em cada mesa, obrigatória. | 6 a 9 orientadores volantes no salão; a resposta a uma fila de 40 pessoas passa a ser deles, sem ponto de controle documentado para o Cartório. |
