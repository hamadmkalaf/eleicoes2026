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

## Branches

- `claude/project-analysis-documentation-w49q34`: última versão de todas as
  etapas, consolidada em 06/09/2026. Base de trabalho.
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
- **Entradas de eleitor: S4, S5 e S6; saídas: S2 e S8.** Decisão do Posto
  registrada em 06/09/2026 (§9.3 da documentação). O plano do Ring 3 e a
  sinalização já seguem isso; o Cenário Claude do simulador ainda usa S1/S9
  como saída e a planta-base ainda não desenha papel nenhum: ambos estão por
  alinhar, não são fonte da decisão.

## Fontes únicas

- Geometria: `scripts/salao.py`. As medidas saíram do PDF do RDS e da versão
  revisada com as portas de carga; não remeça o PDF nem duplique constantes.
  `data/prancheta_hall2.json` é a exportação congelada dessa geometria para o
  simulador e para `scripts/folgas_prancheta.py`.
- Cenários salvos: `scripts/cenarios.py`. A prancheta e o simulador mostram a
  mesma lista porque os dois geradores chamam esse módulo; não duplique a
  leitura. Ver `cenarios/README.md`.
- Dados das urnas: `saidas/dados.json` (etapa 1); todas as etapas seguintes
  leem daqui.
- Desenho: `scripts/desenho.py` e `scripts/estilo_plano.css`.

## Convenções

- Prosa e comentários em português. Código e comentários de código em ASCII;
  acentuação só em strings que vão para a tela.
- Toda saída em `saidas/` é gerada por script; editar o HTML ou o SVG à mão
  perde-se na próxima geração. Os geradores falham em vez de gravar saída
  errada.
- As peças publicadas têm URL registrada no §0 de `DOCUMENTACAO_PROJETO.md` e
  no §10 de `docs/CONTEXTO.md`. Republique na mesma URL passando-a em `url`.
- Ao citar comparecimento esperado, diga qual base (74/50 ≈ 11.416–11.418, ou
  por domicílio ≈ 11.498); ao citar uma mesa, diga qual numeração (MRV do DJE,
  posição da prancheta ou M da sinalização). §9.1 e §9.2 da documentação.
