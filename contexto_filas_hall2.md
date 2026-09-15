# Contexto — desenho de filas no RDS Hall 2 (conversa de 14–15/09/2026)

Resumo da conversa sobre formação de filas para o 1º turno (04/10/2026), para
retomada posterior. Os documentos, scripts e desenhos citados estão no
repositório (branch `claude/filas-sem-ring-3-b9qvqi`, PR #22). Página visual
consolidada: https://claude.ai/artifact/P3x8Hy3j8gnEYKdwwfCSTe

---

## 1. Como as restrições evoluíram

A conversa passou por quatro cenários, cada um mais restrito que o anterior.
**Só o último vale como plano.** Os anteriores ficam como referência do que foi
descartado e por quê.

| Etapa | Restrição nova | Documento | Capacidade de fila |
|---|---|---|---:|
| 1 | Sem o Ring 3 | `plano_filas_sem_ring3.md` | 1.058 (anel interno) + retenção externa no pátio |
| 2 | RDS proibiu fila no terreno; rua incerta; Ring 3 sem autorização de Brasília | `plano_filas_confinado_hall2.md` | 911 (mesas movidas para o norte) |
| 3 | **Não mudar o desenho atual** — mesas onde estão, nas paredes | `plano_filas_prancheta.md` | 629 (2 entradas, saída central) |
| 4 | **Prancheta Hamad_Final**: entradas S4/S5/S6, saídas S2/S8, blocos em múltiplos de 3, mesma capacidade por porta | `plano_filas_tres_portas.md` | **580** (S2 aberta) / 747 (S2 fechada) |

Duas coisas que eu propus e foram rejeitadas, para não voltar a elas:
**mesas em ilha** e **mover as mesas para a metade norte**. As mesas ficam nas
paredes, onde estão.

O que o usuário estabeleceu como fato: **o que não couber vai para a rua.**
O trabalho é dizer quanto.

## 2. Base de dados e simulação (vale para todos os cenários)

- Eleitorado real por urna em `saidas/dados.json`: 16.794 aptos, 51 seções,
  28 urnas. Dublin 12.581, interior 4.213.
- Comparecimento esperado **11.416** (74% Dublin, 50% interior — taxas de 2022).
- Simulação urna a urna, 28 filas paralelas, passo de 5 min, dois perfis de
  chegada (**base** e **pico de manhã** — premissa, não dado; não há série
  histórica horária de Dublin). Script: `scripts/filas_sem_ring3.py`.
- Pico de gente simultaneamente em fila:

| Perfil | 45 s | 60 s | 75 s | 90 s |
|---|---:|---:|---:|---:|
| Base | 248 | 415 | 1.188 | 2.013 |
| Pico de manhã | 511 | 899 | 1.746 | 2.671 |

- **Entre 60 s e 75 s por eleitor a fila triplica.** É a variável dominante de
  toda a conversa, e ela se decide na MRV (divisão dos cadernos, método de
  identificação), não no desenho da fila.
- Fila de abertura: 3% a 5% do comparecimento já na porta às 8h = **342 a 571
  pessoas**, necessariamente fora. Recomendação recorrente: **abrir o Hall 2 às
  7h00** com votação às 8h00 (meia hora a mais no contrato de segurança, hoje
  7h30–17h30).

## 3. Geometria e premissas de desenho

- Hall 2: 50,2 × 44,5 m, 2.238 m² (ficha do RDS). Recorte do canto sudoeste
  estimado em 11,7 × 7,4 m pela planta do RDS; a prancheta Hamad_Final sugere
  ~8 × 7 m — **medir em vistoria**.
- Canal de 1,10 m. Passo por pessoa: 0,65 m (projeto), 0,90 m (confortável),
  0,50 m (máximo admissível = 2,0 p/m², teto do *Purple Guide* britânico para
  área de espera). Meia pessoa perdida por curva de retorno.
- Faixa perimetral das mesas: 7,0 m (mesa + mesários + micro-fila +
  circulação). **Tem um degrau em 5,6 m** — abaixo disso entra um canal a mais
  por bloco (+12%). Estimativa, não cota.
- Faixa de triagem junto à fachada sul: 4,0 m. Reduzir a 2,5 m vale +7%, mas
  aperta a etapa não paralelizável.
- Corredores de 1,20 m entre blocos; corredor de saída de 3,0 m.
- Unifila = poste retrátil de 2,0 m (orçamento: 100 un = 200 m = EUR 1.303,00,
  EUR 13,03/un). CCB = grade metálica de 2,0 m.
- **Norte-sul sempre venceu leste-oeste**: canais empilhados na largura pagam
  o pedágio dos corredores uma vez; em L-O cada metade paga separadamente e
  ainda perde a espinha central. Vantagem de 22% com a zona larga, 9% com as
  faixas perimetrais preservadas. E em N-S a cabeça de cada fila já aponta para
  o piso de votação.

## 4. O plano vigente — prancheta Hamad_Final (etapa 4)

`plano_filas_tres_portas.md` · `scripts/tres_portas.py` ·
`saidas/tres_portas_serpentina.svg` · `saidas/tres_portas_s2_fechada.svg`

- 28 mesas nas paredes oeste (9), norte (9) e leste (10), cada uma com a letra
  da porta que a alimenta; cada porta alimenta mesas nas três paredes.
- Entradas **S4 (A) = x 24,6 m**, **S5 (B) = 30,2**, **S6 (C) = 35,9**.
  Saídas **S2 = 17,0** e **S8 = 43,5** (ou S7 = 39,7). Posições lidas da
  prancheta como fração da fachada sul, ±1 m — **confirmar na planta cotada**.
- Zona de fila: da fachada sul até o centro (y = 22,25 m), entre as faixas
  perimetrais.

**Resultado: 6 blocos, 2 por porta, 580 pessoas no projeto (757 no máximo),
193/194/194 por porta.** 25 canais, 383 m de canal, 240 unifilas.

| Bloco | Porta | Canais | Prof. | Pessoas | Obs. |
|---|---|---:|---:|---:|---|
| A1 | A | 7 | 11,8 m | 125 | canto a oeste do corredor S2 |
| A2 | A | 3 | 14,9 m | 68 | recuado para igualar |
| B1 | B | 3 | 18,2 m | 83 | |
| B2 | B | 4 | 18,2 m | 111 | |
| C1 | C | 3 | 18,2 m | 83 | |
| C2 | C | 5 | 14,6 m | 110 | recuado para igualar |

- Igualdade por porta obtida por busca exaustiva da repartição de canais e
  recuo da entrada (sul) do último bloco de cada porta.
- **3 blocos = 497** (perde o canto oeste). **9 blocos = inviável** (menos de
  3 canais por bloco). Se "múltiplos de 3" for lido como áreas e não blocos
  físicos, subdivide-se com sinalização.
- **Custo da saída S2**: fica dentro da largura da zona; o corredor passa por
  cima do recorte e desce até a porta — custa 3 m de largura, 6 m de
  profundidade no canto oeste e **um cruzamento** (entrada de A1 × fluxo de
  saída), supervisionado por fiscal.
- **Variante S2 fechada** (tudo sai por S8/S7, saída oeste pelo piso norte):
  **747 pessoas (+29%), zero cruzamentos**; caminhada de ~60 m para quem votou
  na parede oeste e todo o egresso a leste — decisão de evacuação para o
  responsável de incêndio do RDS.

Transbordo para a rua (pico − teto):

| Perfil | t/eleitor | Pico | S2 aberta (580) | S2 fechada (747) |
|---|---:|---:|---:|---:|
| Base | 60 s | 415 | 0 | 0 |
| Pico de manhã | 60 s | 899 | 319 | 152 |
| Base | 75 s | 1.188 | 608 | 441 |
| Pico de manhã | 75 s | 1.746 | 1.166 | 999 |
| Pico de manhã | 90 s | 2.671 | 2.091 | 1.924 |

Conversão para calçada: 0,65 m por pessoa em fila de uma pessoa só (calçada de
2,5 m com 1,5 m livre). 270 pessoas ≈ 176 m; 900 ≈ 585 m.

## 5. Achados que atravessam os cenários

- **Urnas competem por piso com a fila** (etapa 2): mais urnas encurtam a fila
  mas ocupam piso; mesmo assim ganham. Com 28 urnas o salão só comporta a fila
  até ~60 s por eleitor; a 90 s, exigiria 38+ urnas. É a prova geométrica para
  levar ao TSE/Brasília junto com a contraproposta de agregação.
- **Triagem é a etapa não paralelizável.** 3 a 8 postos de "onde eu voto?"
  conforme 10% ou 30% dos eleitores chegam sem saber a seção — 5 pessoas de
  equipe de diferença no pico. Liga o plano de comunicação ao fluxo: a chamada
  dominante deve ser "descubra sua seção antes de sair de casa".
- **Alocação de urnas por porta** foi balanceada por comparecimento esperado
  (`scripts/plano_filas.py`, amplitude 2,5%). Na etapa 3, a saída central
  fora do meio criou desequilíbrio 60/40 entre portas — resolvido na etapa 4
  pelo balanceamento explícito.
- **Curral sem canais** na mesma zona: ~30% a mais de gente, mas perde a ordem
  de chegada. Só como contingência declarada.
- **Ocupação total** no pico fica em 40–50% da capacidade nominal do Hall 2
  (2.900). O limite não é o recinto, é o piso; mas barreira em zona de egresso
  exige **submissão ao responsável de incêndio do RDS**, não só comunicação.
- Material (etapa 4): 240 unifilas para a serpentina + ~56 micro-filas + ~25
  saída/sinalização ≈ 320, contra 100 no orçamento. CCB caiu a ~16 (só funis de
  porta) desde que não há retenção externa.

## 6. Pendências para retomar

1. Confirmar na planta cotada as posições de S2, S4, S5, S6, S7, S8 e medir o
   recorte sudoeste.
2. Decidir S2 aberta (580, 1 cruzamento) ou fechada (747, 0 cruzamentos).
3. Aferir faixa perimetral (7,0 vs 5,5 m) contra mesa, cabine e urna reais.
4. Abertura do Hall 2 às 7h00 — negociar com o RDS e estender a segurança.
5. Aval do responsável de incêndio do RDS para o layout de barreiras.
6. Cotação de unifila para ~320 unidades em data única.
7. Decisão jurídica sobre a fila na rua (An Garda Síochána / Dublin City
   Council) e responsável nomeado no dia — o transbordo é inevitável acima de
   60 s por eleitor.
8. O tempo por eleitor (divisão dos cadernos na MRV, identificação) continua
   sendo a variável que decide a ordem de grandeza de tudo acima.

## 7. Índice de arquivos

| Arquivo | O que é |
|---|---|
| `plano_filas_sem_ring3.md` | Etapa 1 — anel interno + pátio (§3–5 superadas) |
| `plano_filas_confinado_hall2.md` | Etapa 2 — tudo no Hall 2, mesas ao norte (rejeitado) |
| `plano_filas_prancheta.md` | Etapa 3 — desenho anterior inalterado, 2 entradas |
| `plano_filas_tres_portas.md` | **Etapa 4 — plano vigente** |
| `scripts/filas_sem_ring3.py` | Simulação de fila por cenário |
| `scripts/plano_filas.py` | Clusters por porta, anel, equipe, materiais |
| `scripts/serpentina_hall2.py` | N-S vs L-O, curva da linha divisória, fronteira urnas × fila |
| `scripts/prancheta_capacidade.py` | Capacidade no desenho anterior, transbordo |
| `scripts/tres_portas.py` | Busca balanceada para 3 entradas |
| `scripts/desenha_*.py` | Desenhos em escala (SVG/PNG em `saidas/`) |
| `saidas/*.json` | Saídas numéricas de cada script |
