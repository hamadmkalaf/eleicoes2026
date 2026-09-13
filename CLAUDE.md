# eleicoes2026

Análise das seções eleitorais de Dublin e desenho da operação de votação do
posto do RDS Ballsbridge, Hall 2, para o 1º turno de 04/10/2026.

## Leia primeiro

1. `DOCUMENTACAO_PROJETO.md`: documentação consolidada das sete etapas
   (agregação, planta-base, prancheta e cenários, simulados de fluxo, Ring 3,
   sinalização, horários de pico), revisão dos dez PRs, inconsistências entre
   etapas (§9) e pendências por dono. Retomar o trabalho sem lê-la leva a
   refazer o que já está feito ou a repetir uma divergência já mapeada.
2. `docs/CONTEXTO.md`: documento de passagem do desenho de fluxo do salão
   (geometria medida, premissas, carga das 28 urnas, perguntas em aberto).
3. `docs/SESSAO_2026-09-13.md`: passagem da sessão do dashboard e das portas
   vivas (decisões do Posto sobre as ferramentas, PR #16, como verificar a
   propagação entre Simulador, Prancheta e Ring 3, o que ficou fora).

## Branches

- `claude/integrated-artifacts-dashboard-cmfi4l` (PR para o branch padrão):
  consolida a branch de 06/09 mais barreiras, Ring 3 oficial, cenário
  Equitativo e cotações, e acrescenta o dashboard. Base de trabalho a partir
  de 11/09/2026.
- `claude/project-analysis-documentation-w49q34`: última versão de todas as
  etapas, consolidada em 06/09/2026.
- `backup/consolidado-2026-09-06`: cópia congelada do mesmo estado. Não
  receber commits; serve para resgatar arquivos e histórico (§10 da
  documentação).
- `cenarios-hall2`: branch de dados dos cenários da prancheta;
  `scripts/salva_cenario.py` grava nela e `scripts/cenarios.py` a lê.
- As demais branches `claude/*` e `deisgn-fluxo` são os heads dos PRs #1–#10,
  intactos.

## A planta-base é a referência

`saidas/planta_base.html` (gerada por `scripts/planta_base.py`) é a leitura
acordada do salão. Duas regras valem para tudo que for produzido depois:

- **Portas são chamadas pelo número de fachada**, N1, N2, L1 a L4, S1 a S9,
  O1, O2 e R1, com o código do RDS junto quando o interlocutor for o RDS. A
  numeração é por fachada, na ordem de leitura do desenho: de oeste para leste
  nas paredes norte e sul, de norte para sul nas paredes leste e oeste. Ela é
  gerada por `planta_base.py`, não escrita à mão.
- **Entradas de eleitor: S4 (A), S5 (B) e S6 (C); saídas: S2 e S8.** Decisão
  do Posto de 06/09/2026, em `scripts/decisoes.py`; planta-base, prancheta,
  simulador, Ring 3 e sinalização leem dali. Não altere o papel de uma porta
  em nenhum gerador: altere em `decisoes.py` e regenere.

## Fontes únicas

- Decisões do Posto: `scripts/decisoes.py` (portas, numeração, classes e cores
  de carga, atribuição das mesas às entradas do Ring 3) e
  `scripts/comparecimento.py` (base B). `gera_decisoes.py` grava
  `data/decisoes.json`; rode-o antes dos outros geradores.
- Numeração das mesas: **só o MRV do DJE/TRE-DF**, identidade da mesa que não
  depende da posição. Não numere mesas por posição, por porta ou por bloco. A
  numeração voltada ao eleitor só entra depois que o cenário da prancheta for
  fechado.
- Cores: vermelho/amarelo/verde marcam a **carga** da mesa (as 3 maiores, ≥ 450
  esperados, o resto); azul/âmbar/magenta são as **raias** A/B/C da
  sinalização. Não misturar. Cor ou letra para o eleitor: sem decisão.
- Geometria: `scripts/salao.py`, inclusive o Ring 3 (`RING3`, `ring3_rect()`). As medidas saíram do PDF do RDS e da versão
  revisada com as portas de carga; não remeça o PDF nem duplique constantes.
  `data/prancheta_hall2.json` é a exportação congelada dessa geometria para o
  simulador e para `scripts/folgas_prancheta.py`.
- Cenários salvos: `scripts/cenarios.py`. A prancheta e o simulador mostram a
  mesma lista porque os dois geradores chamam esse módulo; não duplique a
  leitura. Ver `cenarios/README.md`.
- Dados das urnas: `saidas/dados.json` (etapa 1); todas as etapas seguintes
  leem daqui.
- Desenho: `scripts/desenho.py` e `scripts/estilo_plano.css`.
- Portas vivas: `simulador/portas.js` é o único lugar que deriva N entradas,
  N zonas do Ring 3 e mesa → entrada a partir de um estado de portas; o
  Simulador publica, a Prancheta, o Ring 3 ao vivo e o dashboard assinam
  (localStorage + BroadcastChannel na mesma origem; hash `#portas=` para
  links). Não reimplemente a regra nas páginas. Alterar a decisão continua
  sendo em `decisoes.py`.
- Dashboard: `scripts/gera_dashboard.py` monta `saidas/dashboard/` (index +
  cópias das ferramentas e peças) e roda por último. Sem orçamento nem lista
  de pendências na página, a pedido do Posto (foram para o Planner).

## Convenções

- Prosa e comentários em português. Código e comentários de código em ASCII;
  acentuação só em strings que vão para a tela.
- Toda saída em `saidas/` é gerada por script; editar o HTML ou o SVG à mão
  perde-se na próxima geração. Os geradores falham em vez de gravar saída
  errada.
- As peças publicadas têm URL registrada no §0 de `DOCUMENTACAO_PROJETO.md` e
  no §10 de `docs/CONTEXTO.md`. Republique na mesma URL passando-a em `url`.
- Comparecimento esperado é sempre a base B (11.499, `comparecimento.py`);
  não reintroduza 74/50 nem "~12.000". Mesa é sempre "MRV n".
