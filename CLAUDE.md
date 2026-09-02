# eleicoes2026

Análise das seções eleitorais de Dublin e desenho do fluxo de votação do posto
do RDS Ballsbridge, Hall 2, para o 1º turno de 04/10/2026.

## Leia primeiro

`docs/CONTEXTO.md` é o documento de passagem do desenho de fluxo: geometria
medida, premissas, carga das 28 urnas, simulação de fila e perguntas em aberto.
Retomar o trabalho sem lê-lo leva a refazer o que já está feito.

## A planta-base é a referência

`saidas/planta_base.html` (gerada por `scripts/planta_base.py`) é a leitura
acordada do salão. Duas regras valem para tudo que for produzido depois:

- **Portas são chamadas pelo número de fachada** — N1, N2, L1 a L4, S1 a S9,
  O1, O2 e R1 —, com o código do RDS junto quando o interlocutor for o RDS. A
  numeração é por fachada, na ordem de leitura do desenho: de oeste para leste
  nas paredes norte e sul, de norte para sul nas paredes leste e oeste. Ela é
  gerada por `planta_base.py`, não escrita à mão.
- **Entrada e saída de eleitor ainda não estão decididas.** Não atribua papel de
  entrada ou de saída a nenhuma porta sem que o usuário decida.

O que já está determinado sobre as portas está no §4 do contexto: parede leste
toda em emergência com recuo de 3 m, N1 fechada, N2 desbloqueada para o
catering. O resto é "a definir", que não é o mesmo que disponível.

## Fonte única de geometria

`scripts/salao.py`. As medidas saíram do PDF do RDS e da versão revisada com as
portas de carga; não remeça o PDF nem duplique constantes. `scripts/desenho.py`
tem as primitivas de desenho das plantas, e `scripts/estilo_plano.css` o estilo
das peças de leitura.

## Convenções

- Prosa e comentários em português. Código e comentários de código em ASCII;
  acentuação só em strings que vão para a tela.
- Toda saída em `saidas/` é gerada por script — editar o HTML ou o SVG à mão
  perde-se na próxima geração.
- As peças de leitura publicadas têm URL registrada no §10 do contexto.
  Republique na mesma URL passando-a em `url`.
