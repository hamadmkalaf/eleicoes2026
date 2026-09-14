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
4. `docs/SESSAO_2026-09-13b.md`: passagem da sessão que trouxe Ring 3 (corredor
   em L), barreiras (hipóteses de corte) e fitas no piso para o dashboard e
   criou o registro de decisões em aberto e as instruções de fluxo geradas.
5. `docs/SESSAO_2026-09-14.md`: transcrição da conversa de 13/09 (tarde) a
   14/09 (a lista de quinze mudanças do Posto, literal) e a passagem para a
   próxima sessão: estado, decisões em números, como rodar cada simulador e o
   que condiciona os resultados (o Hamad_Final já está em `cenarios/`).
6. `docs/decisoes_em_aberto.md` e `PENDENCIAS`: o que falta decidir (com
   dependências) e o que falta fazer. Não confundir: decisão de fluxo vai em
   `scripts/decisoes_abertas.py`; tarefa vai em `PENDENCIAS`.

## Branches

- `claude/vibrant-wozniak-hvmqcr` (PR #18, contra a branch do dashboard):
  mescla o dashboard (PR #16), as fitas no piso (PR #17) e as pontas dos
  branches de Ring 3 (#13) e barreiras (#12), e acrescenta o registro de
  decisões em aberto, as instruções de fluxo e o orçamento preenchível. Base
  de trabalho a partir de 13/09/2026.
- `claude/integrated-artifacts-dashboard-cmfi4l` (PR #16 para o branch padrão):
  consolida a branch de 06/09 mais barreiras, Ring 3 oficial, cenário
  Equitativo e cotações, e acrescenta o dashboard. Base de trabalho de 11 a
  13/09/2026.
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
- Numeração das mesas: duas, decididas em 13/09. **NUMERAÇÃO OFICIAL = MRV
  do DJE/TRE-DF**, identidade da mesa que não depende da posição (cadernos,
  convocação, comunicação interna). **NUMERAÇÃO ELEITOR** = 1 na mesa mais ao
  sul da parede oeste, sentido horário, 28 na mais ao sul da parede leste,
  calculada por `decisoes.numeracao_eleitor()` sobre o cenário de trabalho; as
  peças mostram o número eleitor em destaque e o MRV ao lado. Não numere mesas
  por porta ou por bloco, e não digite a numeração eleitor: ela sai de
  `decisoes.mesas()[*]["eleitor"]`.
- Cenário de trabalho: `decisoes.CENARIO_TRABALHO` (`hamad-final`, o
  Hamad_Final salvo pelo Posto em 13/09 e colado em
  `cenarios/hamad-final-20260914-170656.json` em 14/09). Se o arquivo faltar,
  `cenario_trabalho()` cai no `CENARIO_PROVISORIO` (Hamad_3polos) e marca
  `provisorio` nas saídas. Um cenário novo da prancheta entra pelo mesmo
  caminho: JSON colado pelo Posto, gravado em `cenarios/`, tudo regenerado.
- Cores: vermelho/amarelo/verde marcam a **carga** da mesa (as 3 maiores, ≥ 450
  esperados, o resto); azul/âmbar/magenta são as **raias** A/B/C da
  sinalização. Não misturar. Identidade da fila para o eleitor: **letra**
  (A, B, C; decisão de 13/09, `decisoes.NOMENCLATURA_PORTAS`); a cor é apoio.
- Ring 3: desenho decidido em 13/09 = `girado_ccb_na_ponta` de
  `saidas/ring3.json` (`decisoes.RING3_DESENHO`; 82 separadores contados,
  `RING3_SEPARADORES_REGISTRADOS = 100`). A atribuição das mesas às entradas
  continua pelas quotas de `layout_ring3.py`; não use as capacidades por zona
  do desenho como quota (é circular). `gera_decisoes.py` confere.
- Barreiras internas: `scripts/tensa_barreiras.py` lê o cenário de trabalho
  por `decisoes.py` e os traçados (1e adotado; 1f/1g/1h em T) pelos
  `parametros` de D4 em `decisoes_abertas.py`; `gera_barreiras_hall2.py` gera
  a planta e `saidas/tensa_barreiras.md`. Regra de mesa: par 4 m, vermelha
  10 m, solta não vermelha sem fita. Não edite `barreiras_hall2.html` à mão.
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
- Decisões em aberto: `scripts/decisoes_abertas.py` (opções, opção vigente,
  `depende_de`, efeitos; `condiciona` é calculado; estados `em aberto`,
  `parcial`, `decidida`, `derivada`). Desde 13/09 (tarde) só **D9**
  (identificação no caderno) e **D2** (checkpoint ou fitas) estão em aberto;
  D1, D3, D4 e D8 decididas; D1b, D5, D6, D7 derivadas. Grava
  `data/decisoes_abertas.json` e `docs/decisoes_em_aberto.md`. O dashboard
  (seção "Decisões em aberto") e `scripts/gera_instrucoes_fluxo.py`
  (`docs/instrucoes_fluxo.md`, `saidas/instrucoes_fluxo.html`) leem
  `montar()`; nenhum digita opção ou dependência por conta própria. Quando o
  Posto decide, troque `vigente`, marque `estado` e regenere; se a decisão
  muda algo de `decisoes.py` (portas, por exemplo), altere lá também.
- Dashboard: `scripts/gera_dashboard.py` monta `saidas/dashboard/` (index +
  cópias das ferramentas e peças) e roda por último. Sem orçamento nem lista
  de tarefas na página, a pedido do Posto (foram para o Planner e para
  `PENDENCIAS` / `orcamento_final.md`); as decisões de fluxo em aberto, sim,
  entram (decisão do Posto de 13/09).
- Ring 3 ao vivo (`simulador/portas.js`) desenha os cinco desenhos anteriores
  a 11/09 e abre no leste-oeste sem baias (`DESENHO_DECIDIDO = "H"`), o mais
  próximo do decidido; o corredor em L e a fita com CCB na ponta estão só em
  `scripts/ring3.py` e na peça estática. Portá-los segue pendente. O
  simulador continua no plano anterior (capacidade 1.402) por coerência com
  a varredura salva.

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
