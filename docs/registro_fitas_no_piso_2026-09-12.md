# Registro da sessão: fitas no piso em vez do checkpoint (12/09/2026)

Registro do que foi pedido, lido, construído e concluído na sessão que abriu
o PR #17 (branch `claude/direct-mrv-floor-guidance-k5urxi`). Serve para
retomar a discussão com o colega sem reler a conversa.

## 1. O pedido

Abrir uma branch para discutir e modelar a sugestão de um colega: **eliminar o
checkpoint** e guiar o eleitor da porta direto à MRV por **fitas no piso com
sinalização**, em contraste com a ideia de convergir os eleitores a um ponto
com banners onde a equipe aponta a mesa de cada um. Depois, a instrução de
usar a **planta-base, a prancheta e o simulador** já existentes no repositório
como base do modelo.

## 2. Duas iterações

### 2.1 Primeira versão (descartada)

Construída sobre o esboço `PLANO COM FLUXOS MELHORADO.png` (28/08): duas
portas, um hub no meio do salão, 28 posições transcritas do desenho, modelo
próprio de fila (Erlang C) só com biblioteca padrão. Conclusão daquela versão:
o hub precisaria de 6 pessoas por porta; as fitas moveriam a triagem para
antes da porta e o ganho dependeria da fração de eleitores que sabe a seção.

Foi retirada da branch porque o esboço está superado. Os PRs #1 a #16
registram o plano vigente: três entradas (S4/S5/S6), saídas S2/S8, checkpoint
a 16 m da porta (não no centro), consulta "qual é a minha mesa" feita fora, no
percurso do portão ao Hall 2, Ring 3 com três serpenteados, mesas numeradas
pelo MRV do DJE, arranjo Três polos na prancheta e cenário 1e de barreiras.

### 2.2 Segunda versão (a que ficou)

A branch foi rebaseada por merge sobre `claude/integrated-artifacts-dashboard-cmfi4l`
(PR #16, base de trabalho desde 11/09), e o PR #17 passou a apontar para ela.
O motor do simulador (`simulador/modelo.js`) já tratava "sem checkpoint" como
opção (`cen.checkpoint.existe = false`), então a sugestão foi simulada no
motor oficial em vez de num modelo paralelo.

## 3. O que foi lido para ancorar o modelo

- `DOCUMENTACAO_PROJETO.md` (sete etapas, §9 de inconsistências e pendências)
  e `CLAUDE.md`.
- `docs/CONTEXTO.md`, `scripts/decisoes.py`, `data/decisoes.json`,
  `data/prancheta_hall2.json`, `cenarios/README.md`, os cenários salvos.
- `saidas/tensa_barreiras.md` (cenário 1e: 100 postes, 28 presos ao checkpoint).
- `saidas/plano_ring3_horizontal.md`, PR #8 (plano de sinalização), PR #12.
- `simulador/modelo.js`, `varredura.js`, `teste_modelo.js`, `app.js`.

## 4. O que foi construído

| Arquivo | Papel |
|---|---|
| `simulador/fitas.js` | Varredura no motor oficial sobre o Cenário Claude (Três polos): com e sem checkpoint, três políticas de liberação da porta, filas 5/8/12, erro de sinalização, identificação 60 s, comparecimento +15 %, atribuição por parede. Mede metragem e cruzamentos das fitas. Grava `saidas/fitas_piso.json`. |
| `simulador/modelo.js` | Parâmetro opcional `cen.sinalizacao = {erro, desvio}` (fração que se perde sem checkpoint e desvio em metros) e contador `perdidos` no resumo. Padrão zero; nenhum cenário existente muda. |
| `scripts/fitas_piso.py` | Desenha as fitas sobre a planta (referência com checkpoint; troncos com a atribuição da decisão; troncos por parede) e monta `saidas/fitas_piso.html`, `.md` e três SVGs. |
| `docs/alternativa_fitas_no_piso.md` | Documento de discussão: papéis do checkpoint, resultados, geometria, organização no dia lado a lado, efeitos de 2ª e 3ª ordem, recomendação. |
| README, `DOCUMENTACAO_PROJETO.md` §4.4 | Registro da etapa e comandos. |

Testes que passaram após a mudança no motor: `teste_modelo` (conservação de
eleitores), `teste_arranjos` 24/24, `teste_portas` 167/167,
`teste_prancheta` 447/447. Geradores reexecutados: simulador, Ring 3 ao vivo e
dashboard (única diferença: o motor embutido).

## 5. Resultados (identificação 45 s, voto 30 s, 8 dias simulados)

| Cenário | Fecha (p50) | Espera P90 | fora / dentro | Pico dentro | Pico Ring 3 | Chegadas a fila cheia |
|---|---|---|---|---|---|---|
| Referência, checkpoint a 16 m, 3/3/3 | 17h03 | 49 min | 33 / 20 | 321 | 962 | 0 |
| Fitas, porta livre | 17h03 | 50 min | 5 / 44 | 950 | 962 | 5.795 |
| Fitas, porta libera enquanto cabe na zona | 17h03 | 68 min | 63 / 7 | 121 | 1.516 | 2.216 |
| Fitas, porta só libera quem tem vaga na mesa | 17h28 | 103 min | 100 / 3 | 110 | 2.283 | 0 |
| Fitas, buffer, filas 5/8/12 | 17h03 | 52 min | 42 / 17 | 206 | 1.001 | 2.188 |
| Fitas, 25 % se perdem (40 m a mais) | 17h03 | 66 min | 61 / 6 | 121 | 1.530 | 2.077 |
| Checkpoint, identificação 60 s | 18h53 | 112 min | 97 / 40 | 315 | 2.036 | 0 |
| Fitas, porta livre, identificação 60 s | 18h50 | 108 min | 5 / 107 | 1.401 | 962 | 8.800 |

Geometria das fitas (troncos rente à parede, um por parede servida por entrada):

| Atribuição mesa → entrada | Fita | Troncos | Cruzamentos entre entradas | Desequilíbrio das portas |
|---|---|---|---|---|
| Da decisão (por quota do Ring 3) | 463 m | 10 | 18 | 1,16× |
| Por parede (oeste A, norte B, leste C) | 214 m | 4 | 1 | 3,36× (porta C com 5.951 esperados para raia de 445) |

Uma fita por mesa (a sugestão literal): 906 m e 103 cruzamentos.

## 6. Conclusões

1. **O checkpoint não custa vazão.** A última mesa fecha às 17h03 com ou sem
   ele; a 60 s por eleitor tudo fecha depois das 18h50, com ou sem. O gargalo é
   a mesa receptora (pendência dos dois cadernos, §9.7 da documentação).
2. **O que o checkpoint faz é reter por mesa.** As fitas substituem o papel de
   informar (que o plano já resolve fora do salão), não o de regular. Sem ele,
   a fila migra do Ring 3 para dentro (950 pessoas no pico) ou a porta regula
   às cegas (Ring 3 acima da capacidade, bloqueio de cabeça de fila).
3. **Perder-se custa 1 a 3 minutos** na espera P90. O custo da má sinalização
   é de ordem no salão, não de tempo.
4. **Fitas exigem arranjo e atribuição desenhados para elas.** Com a
   atribuição da decisão, os troncos cruzam o meio do salão; por parede não
   cruzam, mas o Três polos tem 13 mesas na fachada leste e 5 na oeste.
5. **Recomendação:** manter o checkpoint como válvula (pode ser mais leve, 2
   por entrada) e usar a fita como guia a partir dele até as paredes, com placa
   alta numerada em cada mesa. Sem checkpoint só com um arranjo com um terço da
   carga por parede, filas 5/8/12 usando os 28 postes hoje presos ao checkpoint
   e 6 a 9 orientadores volantes.

## 7. Efeitos de segunda e terceira ordem registrados

- Ring 3 e interior são um sistema só: porta livre esvazia o Ring 3 e enche o
  salão; porta regulando às cegas estoura o Ring 3.
- O 1e foi contado com o checkpoint; sem ele, 28 postes mudam de lugar e as
  filas de mesa viram a única contenção (1 conflito geométrico no Três polos).
- Com 950 pessoas dentro, a fita deixa de ser visível junto às paredes com
  fila; a placa alta vale nos dois cenários, a fita só no salão vazio.
- O Cartório vê no checkpoint um ponto de controle documentado; sem ele a
  resposta a uma fila de 40 pessoas passa aos orientadores, sem registro.

## 8. Onde está tudo

- PR #17: https://github.com/hamadmkalaf/eleicoes2026/pull/17 (base:
  `claude/integrated-artifacts-dashboard-cmfi4l`).
- Página publicada: https://claude.ai/code/artifact/d36838b6-fb73-47b5-b7d1-d78b5eda8629
- Reproduzir: `node simulador/fitas.js 8 && python3 scripts/fitas_piso.py`.
- Conferir na interface do simulador publicado: Checkpoint → não e
  Liberação → livre mostram o salão a 950 pessoas.

## 9. Premissas a validar

- Sem checkpoint, 10 s para ler a sinalização na soleira (constante do motor).
- Erro de sinalização (10 % e 25 %, 30 a 40 m) é premissa, não medida.
- Fita: 33 m por rolo e EUR 12 por rolo são premissas de compra.
- Curva de chegada, identificação 45 s e comparecimento base B são os do
  simulador; a divergência entre as três curvas do repositório (§9.4) continua.
