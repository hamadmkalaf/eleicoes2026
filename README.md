# Eleições 2026 — posto de Dublin (RDS Ballsbridge, Hall 2)

Análise das seções eleitorais de Dublin e desenho da operação de votação do
**1º turno de 04/10/2026 (8h–17h)** no **Royal Dublin Society, Hall 2** (RDS,
Merrion Road, Ballsbridge, Dublin 4): **16.794 eleitores aptos, 51 seções, 28
urnas**, identificação por caderno físico, Hall 2 + Ring 3 (descoberto).

**Leia primeiro [`DOCUMENTACAO_PROJETO.md`](DOCUMENTACAO_PROJETO.md)**: é a
documentação consolidada das sete etapas, com a revisão dos dez pull requests,
as inconsistências entre etapas e as pendências por dono. Esta branch
(`claude/project-analysis-documentation-w49q34`) reúne a última versão de cada
etapa; `backup/consolidado-2026-09-06` é a cópia congelada do estado de 06/09
antes da integração.

**Decisões do Posto (06/09/2026), fonte única em `scripts/decisoes.py`:**
comparecimento esperado pela base B (taxa de 2022 por domicílio de origem,
`scripts/comparecimento.py`, 11.499); o número da mesa é o **MRV do DJE** e
não depende da posição; mesas coloridas por carga (vermelho as 3 maiores,
amarelo médio, verde baixo); entradas **S4 (A), S5 (B), S6 (C)** e saídas **S2
e S8**; cada entrada do Ring 3 com as suas mesas. A nomenclatura das filas para
o eleitor (cor ou letra) está em aberto.

## Mapa do projeto

| # | Etapa | Entregáveis | Documento de referência |
|---|---|---|---|
| 1 | Agregação final: seções → MRVs, comparecimento esperado por seção (2022) | `saidas/Dublin_2026_agregacoes.xlsx`, `saidas/dados.json`, `saidas/dublin_agregacoes.html`, `saidas/mrv_secoes_comparecimento.md`, `data/mrv_secoes.json` | `DOCUMENTACAO_PROJETO.md` §1, `handoff_agregacao_dublin_2026.md`, `contexto_eleicoes_dublin_2026.md` |
| 2 | Planta-base do Hall 2 (salão, 18 portas numeradas por fachada) | `saidas/planta_base.html`, `saidas/planta_base.svg`, `scripts/salao.py` | §2, `docs/CONTEXTO.md` |
| 3 | Prancheta e seus cenários (planta das 28 mesas, editor em escala, biblioteca de cenários) | `saidas/editor.html`, `saidas/mesas.html`, `cenarios/*.json` | §3, `cenarios/README.md` |
| 4 | Simulados de fluxo (simulador eleitor a eleitor; modelos de fila por urna) | `saidas/simulador_fluxo.html`, `simulador/`, `scripts/simula_fluxo.py`, `saidas/analise_gargalos.md` | §4 |
| 5 | Dimensões e plano do Ring 3 | `saidas/plano_ring3.md`, `saidas/layout_ring3.svg/.png` | §5 |
| 6 | Plano de sinalização externo | `saidas/plano_sinalizacao.html`, `data/fotos/` | §6 |
| 7 | Expectativa de horários de pico | `pesquisa_horarios_pico_votacao.md` | §7 |

Artefatos publicados: planta-base, planta das 28 mesas, prancheta, simulador e
plano de sinalização; URLs no §0 da documentação.

## Como rodar

```bash
pip install pandas openpyxl Pillow        # pymupdf é opcional (PNG do Ring 3)
# 1. agregação e decisões
(cd scripts && python3 mapa_agregacoes.py && python3 gera_pagina.py && python3 gera_mrv_comparecimento.py)
python3 scripts/gera_decisoes.py          # data/decisoes.json
# 2 e 3. planta-base, mesas, prancheta
(cd scripts && python3 salao.py && python3 planta_base.py && python3 mesas.py && python3 gera_mesas.py)
python3 scripts/gera_editor.py && node scripts/teste_prancheta.js
python3 scripts/folgas_prancheta.py [cenarios/<arquivo>.json]
# 4. simulações (o simulador lê a geometria que gera_editor.py acabou de gravar)
python3 scripts/gera_simulador.py && node simulador/teste_arranjos.js && node simulador/teste_modelo.js claude 16
python3 scripts/simula_fluxo.py
# 5. Ring 3
python3 scripts/layout_ring3.py
# 6. sinalização
python3 scripts/gera_plano_sinalizacao.py
```

Toda saída em `saidas/` é gerada por script: editar HTML ou SVG à mão se perde
na próxima geração. Os geradores falham em vez de gravar saída errada quando
uma validação não passa.

## Etapa 1 em detalhe: agregação de seções

### Fontes

Os três arquivos em `data/raw/` vieram da pasta do Google Drive do usuário:

| Arquivo | Gerado em | Papel |
|---|---|---|
| `eleitorado_local_votacao_2026_ZZ.csv` | 13/08/2026 | Seção a seção no exterior: papel (Principal/Agregada), `NR_SECAO_PRINCIPAL`, `QT_ELEITOR_SECAO` |
| `Filtrado_Dublin.csv` | 14/07/2026 | Perfil do eleitorado de Dublin, com `NR_SECAO` × `NM_LOCAL_VOTACAO` × `QT_ELEITORES` |
| `mapa_agregacoes_TSE.png` | 13/08/2026 | Mapa oficial de pares principal → agregada |

Ambos os CSVs estão em **latin-1**, separados por `;`. O `Filtrado_Dublin.csv`
foi re-exportado com a linha inteira envolvida em aspas e as aspas internas
duplicadas, então precisa de um passo de desempacotamento, tratado em
`scripts/parse_dados.py`. `NM_LOCAL_VOTACAO` no arquivo de perfil é o local de
votação original do eleitor e é usado como referência de onde ele reside.

A designação **MRV 1–28 → seção principal** vem da convocação de mesários do
DJE/TRE-DF (Ano 2026 n. 139, 04/08/2026), transcrita em
`scripts/gera_mrv_comparecimento.py` e `data/mrv_secoes.json`; não está em
nenhum CSV do TSE. `handoff_agregacao_dublin_2026.md` traz a taxa de
comparecimento de 2022 por domicílio de origem: taxa histórica, de qualidade
desigual entre localidades, **não** comparecimento oficial por seção.

### Resultado em uma linha

16.794 eleitores, 51 seções, 28 urnas. As urnas variam de 398 a **797**
eleitores. As 23 urnas que somam duas seções vão de 429 a 797; as 5 restantes
operam com uma seção só, perto de 400.

### Saídas

- **`saidas/Dublin_2026_agregacoes.xlsx`**: cinco abas, `Urnas` (28 linhas,
  ordenadas por total combinado), `Secoes` (as 51), `Residencia x Secao`,
  `Residencia x Urna` e `Inconsistencias`.
- **`saidas/dublin_agregacoes.html`**: a mesma análise em página visual.
- **`saidas/dados.json`**: os dados estruturados que alimentam a página e todas
  as etapas seguintes.
- **`saidas/mrv_secoes_comparecimento.md`**: MRV × seção × aptos × comparecimento
  esperado pela base B (não oficial; ver aviso no próprio arquivo).
- **`data/decisoes.json`**: a tabela mestra com classe, cor e entrada de cada
  MRV, os papéis das portas e o Ring 3, gerada por `scripts/gera_decisoes.py`.

### Validações

`mapa_agregacoes.py` falha em vez de gravar saída errada se alguma destas não
passar:

1. Soma por seção = soma por urna = total do perfil do eleitorado (16.794 nos
   três caminhos).
2. As 51 seções sobrevivem ao processamento e o número de urnas fecha em 28.
3. **Conferência independente:** o total calculado para cada uma das 28 urnas
   coincide com `QT_ELEITOR_ELEICAO_FEDERAL`, campo que o próprio TSE já
   publica agregado na seção principal.

### Achados

**Erro de digitação no PNG do TSE.** O mapa lista a seção agregada 3752 sob a
principal **3222**, que não existe em Dublin (pertence ao Porto). A correta é a
**3322** (Dublin, 398 eleitores), como consta do CSV oficial. O CSV prevalece;
o caso está na aba `Inconsistencias`, e a 3322 é ao mesmo tempo uma das três
urnas críticas.

**Cada seção é de uma única localidade.** Nas 51 seções, 100% dos eleitores
vêm de um mesmo local de origem. As 28 seções principais são todas de
residentes em Dublin (11.155 eleitores); as 23 agregadas trazem os condados do
interior e mais 4 seções de Dublin.

**Duas naturezas de urna cheia.** No topo do ranking convivem urnas que somam
duas seções de Dublin (3313, 3322, 3315) e urnas que somam uma seção de Dublin
com uma seção inteira do interior (3142 com Limerick, 3161 e 3245 com Cork,
3305 e 3108 com Galway). São 4.213 eleitores, 25% da zona, que residem fora de
Dublin e passam a votar lá.

## Etapas 2 a 7, em resumo

- **Planta-base** (`docs/CONTEXTO.md`, `saidas/planta_base.html`): geometria
  medida do PDF do RDS e codificada em `scripts/salao.py`, fonte única; portas
  chamadas pelo número de fachada (N1, N2, L1–L4, S1–S9, O1, O2, R1); desenha
  as entradas A/B/C e as saídas decididas.
- **Prancheta** (`saidas/editor.html`): as 28 mesas pareadas, com fileira
  recuada na fachada leste, numeradas pelo MRV do DJE e coloridas por carga;
  editor em escala com alinhar à parede, conferência de pares, medir, salvar e
  exportar cenários, papéis das portas e contorno do Ring 3; biblioteca em
  `cenarios/` lida por `scripts/cenarios.py`.
- **Simulador** (`saidas/simulador_fluxo.html`): eventos discretos, eleitor a
  eleitor, sobre qualquer arranjo da prancheta, com as entradas do Ring 3 e as
  portas da decisão; Cenário Claude (arranjo "Três polos", checkpoint a 16 m,
  3/3/3 atendentes) escolhido por varredura. `scripts/simula_fluxo.py` responde
  à pergunta do fechamento: só dois cadernos em paralelo fecham às 17h com
  caderno físico.
- **Ring 3** (`saidas/plano_ring3.md`): ~39 × 35 m; entradas S4/S5/S6, saídas
  S2/S8; três serpenteados (3·9·3 balizas) e duas baias, 1.402 pessoas; 300
  separadores, 100 a adquirir (~EUR 1.302); evacuação e pendências.
- **Sinalização** (`saidas/plano_sinalizacao.html`): oito pontos do portão da
  Merrion Road à urna; uma consulta só (seção → mesa → entrada), replicada a
  cada 25–30 m; mesas pelo MRV e entradas do plano do Ring 3; cor ou letra
  para as filas ainda em aberto; tabela mestra de 51 linhas.
- **Horários de pico** (`pesquisa_horarios_pico_votacao.md`): não há
  estatística oficial por hora; padrão de abertura forte, vale ao meio-dia e
  repique às 17h; em Dublin 2022 a fila não esvaziou o dia inteiro.

O que a integração de 06/09 resolveu (comparecimento, numeração, portas,
números do Ring 3 na sinalização) e o que ficou (curvas de chegada, arranjo da
mesa receptora, cor ou letra) está no §9 da documentação.
