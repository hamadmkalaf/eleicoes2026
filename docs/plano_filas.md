# Plano de distribuição de filas — fitas no piso, sem checkpoint

> Gerado por `scripts/gera_plano_filas.py` (registro de decisões de 2026-09-14; cenário de trabalho **Hamad_Final**). Não editar à mão: quando uma decisão ou uma saída muda, o plano muda. Regime decidido pelo Posto em 14/09: **sinalização por fitas no piso, sem checkpoint** (D2 = fitas), **nenhum poste na entrada** (D4 = só as filas de mesa), Ring 3 no desenho de 13/09 (D3).

Vale para o 1º turno, 04/10/2026, 8h–17h, RDS Hall 2 e Ring 3; 11.499 eleitores esperados em 28 mesas; entradas S4 (A), S5 (B), S6 (C); saídas S2 e S8.

## 1. O regime em uma frase

**O eleitor espera na zona do Ring 3 da sua entrada; a porta o libera enquanto houver lugar nas filas de mesa; na soleira ele lê o painel seção → mesa e segue a fita da sua entrada até a sua mesa; a fila da mesa é a única contenção, guiada por poste, e o orientador volante é a única resposta a uma fila cheia.**

- Não há ponto de controle entre a porta e a mesa: ninguém confere documento nem retém no caminho. A fita leva direto (Posto, 14/09).
- A porta não é livre: libera pelo ritmo da zona, com o marshal olhando as filas de mesa. É o regime que o simulador chama de "buffer" (seção 5); a porta livre lota o salão.
- Cada mesa é conhecida do eleitor pelo **número eleitor** (placa alta) e da equipe pelo **MRV**; as seções ficam no painel da soleira e na placa da mesa.

## 2. Fila externa: uma zona do Ring 3 por entrada

Desenho decidido: **Serpenteados horizontais (raias leste-oeste) · CCB só na ponta**, 1.964 pessoas, 82 separadores contados (100 registrados), 576 m de fita grossa. O eleitor entra no Ring 3 pelo canto nordeste, desce o corredor em L e entra na zona da sua letra.

| Zona | Porta | Cabe (decidido) | Raias | Esperados no dia | Pico (pessoas/min) | Pico simulado sem checkpoint (p50 / p90 do total) | Mesas da zona (nº eleitor · MRV · seções) |
|---|---|---|---|---|---|---|---|
| **A** | S4 | 626 | 23 × 11,3 m | 3.642 | 12,1 | 604 | 1 · MRV 5 · 1160 + 3845; 3 · MRV 12 · 3179 + 530; 7 · MRV 24 · 3322 + 3752; 8 · MRV 9 · 3108 + 3422; 10 · MRV 15 · 3245 + 519; 17 · MRV 20 · 3309 + 1314; 19 · MRV 3 · 513 + 1105; 25 · MRV 26 · 3688; 28 · MRV 28 · 3862 |
| **B** | S5 | 712 | 23 × 13,1 m | 4.215 | 14,1 | 637 | 4 · MRV 17 · 3305 + 521; 5 · MRV 1 · 511 + 1100; 6 · MRV 4 · 517 + 1292; 11 · MRV 16 · 3302 + 3181; 13 · MRV 8 · 3078 + 2847; 14 · MRV 22 · 3313 + 3889; 18 · MRV 25 · 3442; 20 · MRV 7 · 3054 + 1099; 23 · MRV 18 · 3306 + 518; 24 · MRV 21 · 3311 + 3913 |
| **C** | S6 | 626 | 23 × 11,3 m | 3.642 | 12,1 | 531 | 2 · MRV 6 · 1352 + 522; 9 · MRV 11 · 3161 + 3307; 12 · MRV 2 · 512 + 2855; 15 · MRV 10 · 3142 + 1278; 16 · MRV 13 · 3216 + 527; 21 · MRV 23 · 3315 + 3778; 22 · MRV 14 · 3229 + 3821; 26 · MRV 19 · 3308; 27 · MRV 27 · 3832 |

- No pico do dia simulado sem checkpoint (porta regulando), o Ring 3 inteiro chega a **1.429** pessoas (p50) e 1.600 no dia ruim (p90), contra 1.964 de lotação decidida: cabe, com folga de 364 no dia ruim. Com checkpoint eram 971.
- A fita delimita, não contém: o marshal da cabeça de cada zona segura a passagem entre zonas e corrige quem errou de letra enquanto ainda cabe voltar.

## 3. Da porta à mesa: os troncos de fita

Uma fita por entrada, na cor da entrada e com a letra a cada poucos metros, saindo da soleira e ramificando por parede: **462 m de fita** em 9 troncos (uma fita por mesa custaria 888 m). Os troncos de entradas diferentes se cruzam 23 vezes e cruzam o caminho de saída 133 vezes: a fita no piso admite cruzamento, o poste não. Caminho médio da porta à fila: A 32 m · B 33 m · C 32 m.

| Entrada | Parede | Mesas na ordem em que a fita as alcança (nº eleitor · MRV) | Fita do tronco |
|---|---|---|---|
| **A** (S4) | oeste | 1 · MRV 5 → 3 · MRV 12 → 7 · MRV 24 → 8 · MRV 9 | 45 m |
| **A** (S4) | leste | 28 · MRV 28 → 25 · MRV 26 → 19 · MRV 3 | 51 m |
| **A** (S4) | norte | 10 · MRV 15 → 17 · MRV 20 | 63 m |
| **B** (S5) | norte | 14 · MRV 22 → 13 · MRV 8 → 18 · MRV 25 → 11 · MRV 16 | 82 m |
| **B** (S5) | oeste | 4 · MRV 17 → 5 · MRV 1 → 6 · MRV 4 | 37 m |
| **B** (S5) | leste | 24 · MRV 21 → 23 · MRV 18 → 20 · MRV 7 | 37 m |
| **C** (S6) | leste | 27 · MRV 27 → 26 · MRV 19 → 22 · MRV 14 → 21 · MRV 23 | 32 m |
| **C** (S6) | norte | 15 · MRV 10 → 16 · MRV 13 → 12 · MRV 2 | 57 m |
| **C** (S6) | oeste | 2 · MRV 6 → 9 · MRV 11 | 58 m |

- A fita termina na **cauda** da fila de cada mesa, não na mesa: quem chega entra no fim da fila guiada.
- Placa alta com o número eleitor em toda mesa: é o que confirma o destino a 20 m; a fita no piso some sob os pés quando o salão enche.
- A atribuição mesa → entrada é a das quotas do Ring 3 (`decisoes.py`), uma vermelha por entrada; por isso cada entrada serve as três paredes e os troncos se cruzam. A alternativa por parede (oeste A, norte B, leste C) zera os cruzamentos mas desequilibra as portas e mudaria a decisão de 06/09: fica registrada em `saidas/fitas_piso.md`.

## 4. Filas de mesa

Regra de 13/09, traçado **so_mesas** (14/09): par de mesas = uma linha de 4 m no meio (cabem 8 por fila); mesa vermelha = 10 m (20); não vermelha sem par = sem fita. **54 postes** (60 com reserva), 39 fitas de 2 m, nenhum na entrada. 12 pares, 3 polos, 1 mesa(s) sem guia: 26 (MRV 19).

| Mesa (nº eleitor) | MRV | Seções | Entrada | Parede | Fila | Cabem | Lota em | Esperados |
|---|---|---|---|---|---|---|---|---|
| **1** | 5 | 1160 + 3845 | A | oeste | 4 m (par) | 8 | 86 min | 328 |
| **2** | 6 | 1352 + 522 | C | oeste | 4 m (par) | 8 | 86 min | 328 |
| **3** | 12 | 3179 + 530 | A | oeste | 4 m (par) | 8 | 20 min | 423 |
| **4** | 17 | 3305 + 521 | B | oeste | 4 m (par) | 8 | 14 min | 472 |
| **5** | 1 | 511 + 1100 | B | oeste | 4 m (par) | 8 | 32 min | 375 |
| **6** | 4 | 517 + 1292 | B | oeste | 4 m (par) | 8 | 50 min | 348 |
| **7** | 24 | 3322 + 3752 | A | oeste | 10 m (vermelha) | 20 | 21 min | 588 |
| **8** | 9 | 3108 + 3422 | A | oeste | 4 m (par) | 8 | 14 min | 467 |
| **9** | 11 | 3161 + 3307 | C | oeste | 4 m (par) | 8 | 12 min | 504 |
| **10** | 15 | 3245 + 519 | A | norte | 4 m (par) | 8 | 12 min | 498 |
| **11** | 16 | 3302 + 3181 | B | norte | 4 m (par) | 8 | 11 min | 518 |
| **12** | 2 | 512 + 2855 | C | norte | 4 m (par) | 8 | 44 min | 355 |
| **13** | 8 | 3078 + 2847 | B | norte | 4 m (par) | 8 | 218 min | 311 |
| **14** | 22 | 3313 + 3889 | B | norte | 10 m (vermelha) | 20 | 21 min | 590 |
| **15** | 10 | 3142 + 1278 | C | norte | 4 m (par) | 8 | 14 min | 466 |
| **16** | 13 | 3216 + 527 | C | norte | 4 m (par) | 8 | 22 min | 407 |
| **17** | 20 | 3309 + 1314 | A | norte | 4 m (par) | 8 | 25 min | 395 |
| **18** | 25 | 3442 | B | norte | 4 m (par) | 8 | não lota | 295 |
| **19** | 3 | 513 + 1105 | A | leste | 4 m (par) | 8 | 47 min | 351 |
| **20** | 7 | 3054 + 1099 | B | leste | 4 m (par) | 8 | 96 min | 325 |
| **21** | 23 | 3315 + 3778 | C | leste | 10 m (vermelha) | 20 | 21 min | 586 |
| **22** | 14 | 3229 + 3821 | C | leste | 4 m (par) | 8 | 23 min | 405 |
| **23** | 18 | 3306 + 518 | B | leste | 4 m (par) | 8 | 11 min | 515 |
| **24** | 21 | 3311 + 3913 | B | leste | 4 m (par) | 8 | 14 min | 466 |
| **25** | 26 | 3688 | A | leste | 4 m (par) | 8 | não lota | 296 |
| **26** | 19 | 3308 | C | leste | sem fita | — | — | 295 |
| **27** | 27 | 3832 | C | leste | 4 m (par) | 8 | não lota | 296 |
| **28** | 28 | 3862 | A | leste | 4 m (par) | 8 | não lota | 296 |

- Lotam em menos de 20 minutos de pico: 11 (MRV 16) em 11 min, 23 (MRV 18) em 11 min, 9 (MRV 11) em 12 min, 10 (MRV 15) em 12 min, 8 (MRV 9) em 14 min, 15 (MRV 10) em 14 min, 4 (MRV 17) em 14 min, 24 (MRV 21) em 14 min. São as mesas que o orientador volante vigia.
- Fila além do poste: o orientador volante abre uma segunda fila paralela rente à parede e avisa a coordenação; a coordenação segura a porta daquela entrada, não a mesa.

## 5. Liberação na porta: o que o simulador diz

Motor oficial (`simulador/modelo.js`), 8 dias por cenário, sobre o Hamad_Final. "Chegadas a fila cheia" conta eleitores que chegam à mesa com a fila no limite e ficam além do poste; "perdidos" os que erram o caminho.

| Cenário | Fecha (p50 / p90) | Espera P90 (fora / dentro) | Pico dentro | Pico Ring 3 (p50 / p90) | Chegadas a fila cheia | Veredito |
|---|---|---|---|---|---|---|
| Referência: com checkpoint (descartado) | 17h03 / 17h03 | 50 min (35 / 21) | 316 | 971 / 990 | 0 | **atencao**: Espera do eleitor (P90) |
| **Fitas, porta libera enquanto cabe (regime deste plano)** | 17h03 / 17h03 | 65 min (61 / 7) | 122 | 1.429 / 1.600 | 2.190 | **falha**: Espera do eleitor (P90); Filas das mesas sem checkpoint; Ring 3 comporta a fila externa |
| Fitas, porta regulando, filas de mesa maiores (5/8/12) | 17h03 / 17h04 | 51 min (40 / 16) | 206 | 995 / 1.138 | 2.234 | **falha**: Espera do eleitor (P90); Filas das mesas sem checkpoint; Ring 3 comporta a fila externa |
| Fitas, porta livre | 17h03 / 17h04 | 49 min (5 / 43) | 951 | 962 / 990 | 5.809 | **falha**: Espera do eleitor (P90); Filas das mesas sem checkpoint |
| Fitas, porta só libera quem tem vaga na sua mesa | 17h34 / 17h36 | 102 min (99 / 3) | 113 | 2.155 / 2.259 | 0 | **falha**: Última mesa fecha; Mesas vermelhas sem fome; Espera do eleitor (P90) |
| Fitas, porta regulando, 25 % se perdem | 17h03 / 17h04 | 68 min (64 / 7) | 121 | 1.548 / 1.676 | 2.092 | **falha**: Espera do eleitor (P90); Filas das mesas sem checkpoint; Ring 3 comporta a fila externa |
| Fitas, porta regulando, comparecimento +15 % | 17h43 / 17h59 | 113 min (108 / 8) | 121 | 2.588 / 2.788 | 3.025 | **falha**: Última mesa fecha; Espera do eleitor (P90); Filas das mesas sem checkpoint |

- **Fechamento não muda:** a última mesa fecha às 17h03 com ou sem checkpoint. O checkpoint nunca custou vazão; o que ele fazia era reter por mesa.
- **O preço das fitas é a espera lá fora:** P90 de 65 min (61 no Ring 3) contra 50 min com checkpoint, porque a porta só abre quando cabe. Com a porta livre a espera cai para 49 min, mas 951 pessoas ficam dentro do salão e 5.809 chegam a uma fila cheia: não é opção.
- Filas de mesa maiores (5/8/12 pessoas no simulador; as de 4 m e 10 m deste plano cabem 8 e 20) reduzem as chegadas a fila cheia de 2.190 para 2.234 e a espera para 51 min.
- Liberar só quem tem vaga na própria mesa (a porta "conferindo") atrasa o fechamento para 17h34 e empurra 2.155 pessoas para o Ring 3: é o checkpoint de volta, na porta.

## 6. Gatilhos e equipe

Quem vê, avisa a coordenação; ninguém retém por conta própria.

- Zona A com mais de 626 pessoas, ou porta S4 recebendo mais de 12,1 por minuto por mais de 10 min → abrir ritmo na porta; nunca fechar a entrada da zona.
- Zona B com mais de 712 pessoas, ou porta S5 recebendo mais de 14,1 por minuto por mais de 10 min → abrir ritmo na porta; nunca fechar a entrada da zona.
- Zona C com mais de 626 pessoas, ou porta S6 recebendo mais de 12,1 por minuto por mais de 10 min → abrir ritmo na porta; nunca fechar a entrada da zona.
- Fila de mesa além do poste (4 m no par, 10 m na vermelha) → segunda fila paralela pelo orientador volante e porta daquela entrada segurada pela coordenação.
- Mais de 183 pessoas dentro do salão (1,5× o pico simulado) → porta segurada nas três entradas até as filas baixarem.
- Eleitor na mesa errada → o orientador o leva à certa pelo corredor mais curto; nunca de volta à porta.

| Posto | Pessoas | Tarefa | Reporta a |
|---|---|---|---|
| Coordenação geral | 1 | Decide toda retenção; único ponto que autoriza fechar uma porta ou segurar uma zona. | Posto |
| Portão da Merrion Road (pré-triagem) | 3 | Recebe, confirma que o eleitor sabe a seção e a fila; quem não sabe vai ao balcão. Não conferem documento: apontam. | coordenação |
| Balcão "não sei minha seção" (P1) | 1 | Consulta a tabela mestra de 51 seções e devolve seção → mesa → fila. | coordenação |
| Corredor da lateral leste (P2) | 1 | Mantém a corrente andando; repete a consulta a quem parou. | coordenação |
| Ring 3: marshal por zona (3) | 3 | Segura a cabeça de fila e a passagem entre zonas (a fita delimita, não contém); corrige quem errou de fila enquanto cabe. | coordenação |
| Ring 3: cruzamento do corredor em L com a saída S8 | 1 | Separa a corrente que desce pelo apron leste de quem já votou e sai por S8. | coordenação |
| Portas de entrada (3) | 3 | Libera pelo ritmo combinado; conversa com o interior do salão; recebe prioritários fora de fila. | coordenação |
| Salão: orientadores volantes | 10 | Sem checkpoint, são a única resposta a uma fila de mesa que cresce: redirecionam e chamam a coordenação. | coordenação |
| Saídas S2 e S8 | 2 | Encaminham para a rua; ninguém volta pelo salão nem reentra no Ring 3. | coordenação |
| Acessibilidade e prioridade | 1 | Conduz idosos e PcD pela rota prioritária; fala com o marshal de porta para a entrada fora de fila. | coordenação |
| Seguranças contratados (4) | 4 | Controle de acesso e resposta a incidente. Proposta de postos: 2 no portão e no acesso, 1 na fachada das entradas, 1 nas saídas. Não organizam fila. | coordenação |
| Polícia | — | Do lado de fora do recinto (formato a confirmar). | — |
| **Total de voluntários** | **26** | mais 4 seguranças | |

## 7. Sinalização mínima do regime (D6, plano derivado)

- **Painel seção → mesa na soleira** de cada entrada (3), lido em pé em 10 s: seção, número eleitor da mesa, cor e letra da fita.
- **Fita no piso por entrada**, 462 m no total, na cor da entrada e com a letra impressa a cada poucos metros (A 159 m · B 156 m · C 147 m).
- **Placa alta com o número eleitor em toda mesa** (28), com as seções em corpo menor; o MRV só no verso, para a equipe.
- Placas P0–P2 fora e as placas de porta nas CCBs do Ring 3 (D5) seguem o plano de sinalização; o antigo painel do checkpoint (P6) sai.

## 8. O que muda neste plano se a decisão (a) mudar

A única decisão de fluxo em aberto é a identificação no caderno físico (D9). Efeitos de cada opção sobre este plano:

- *(i) Caderno único em ordem alfabética, um mesário identificando*: A mesa é o gargalo e retém por si só: o checkpoint só faz sentido como válvula (reter por mesa) — as fitas no piso não ajudam a mesa. Nada muda na equipe de piso; o esforço vai para a mesa (mesários).
- *(ii) Caderno dividido por seção agregada, um mesário por caderno*: A mesa deixa de ser o gargalo; o checkpoint pode ser leve (2 por porta) ou ceder lugar às fitas sem que a fila migre para dentro. Pré-triagem precisa dizer ao eleitor a SEÇÃO, não só a mesa: o painel seção → mesa ganha a coluna do caderno.
- *(iii) Caderno dividido por faixa de letras, um mesário por faixa*: Como (ii). Placa da mesa com as faixas de letras (A–L / M–Z); orientador aponta a fila certa.
- *(iv) Identificação em paralelo com o voto (o mesário localiza o próximo enquanto o anterior vota)*: Mesa no limite (55 s): o checkpoint como válvula continua necessário nas três críticas. Treinamento dos mesários vira parte do plano de fluxo (webinar).
- *(v) Pré-triagem na fila: eleitor chega à mesa com documento na mão e seção sabida*: Se houver checkpoint, a pré-triagem acontece nele; sem checkpoint, acontece na fila da mesa, por orientador. 1 orientador a cada 3 mesas conferindo documento na fila.
