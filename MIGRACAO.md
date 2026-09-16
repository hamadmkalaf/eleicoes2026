# Transferência para o repositório final

Instruções para migrar este projeto para um repositório novo, contendo só as
versões finais e o que é necessário para chegar a elas. Escrito para ser executado
por outra sessão do Claude, sem depender da conversa que o originou.

---

## 0. Leia isto antes de clonar

**As versões finais não estão na branch padrão.** O repositório de origem
`hamadmkalaf/eleicoes2026` tem como branch padrão `claude/dublin-electoral-sections-3odh1w`,
que **não** contém `CLAUDE.md`, `plano_voluntarios_apoio.md`,
`scripts/zonas_balanceadas.py` nem este arquivo. Tudo isso está na branch
`claude/elegant-euler-jss6uv`, no PR #24, ainda em draft.

Antes de migrar: mesclar o PR #24, ou clonar explicitamente aquela branch.

```bash
git clone --branch claude/elegant-euler-jss6uv \
  https://github.com/hamadmkalaf/eleicoes2026 origem
```

Clonar sem `--branch` traz arquivos desatualizados e a migração sai errada em
silêncio.

---

## 1. Inventário

### 1.1 Vão para o repositório final

| Origem | Destino | O que é |
|---|---|---|
| `CLAUDE.md` | `CLAUDE.md` | Memória do projeto: fatos fixos, geometria do local, convenções. É o arquivo mais importante da transferência. |
| `plano_voluntarios_apoio.md` | `docs/plano_voluntarios.md` | Postos, efetivo e regras de operação dos voluntários. |
| `contexto_eleicoes_dublin_2026.md` | `docs/contexto.md` | Contexto consolidado: orçamento, simulações de tempo de votação, argumentação com o TSE. |
| `README.md` | `docs/agregacoes.md` | Análise das agregações de seções e como rodar o pipeline. |
| `PENDENCIAS` | `docs/pendencias.md` | Lista de tarefas do Posto. Converter para markdown ao mover. |
| `data/raw/eleitorado_local_votacao_2026_ZZ.csv` | igual | Fonte oficial do TSE. Entrada do pipeline. |
| `data/raw/Filtrado_Dublin.csv` | igual | Perfil do eleitorado. Entrada do pipeline. |
| `data/raw/mapa_agregacoes_TSE.png` | igual | Mapa oficial de agregações. Não é lido por script; é a evidência do erro de digitação registrado nas convenções. |
| `scripts/parse_dados.py` | igual | Carga e limpeza dos CSVs. |
| `scripts/mapa_agregacoes.py` | igual | Gera `saidas/dados.json` e o xlsx. |
| `scripts/gera_pagina.py` | igual | Gera a página HTML a partir do JSON. |
| `scripts/zonas_balanceadas.py` | igual | Confere o equilíbrio das três zonas. |
| `scripts/requirements.txt` | igual | pandas e openpyxl. |
| `saidas/dados.json` | igual | Saída gerada; é a fonte de número de todo o resto. |
| `saidas/Dublin_2026_agregacoes.xlsx` | igual | Saída gerada; entregável que se abre sem rodar Python. |
| `saidas/dublin_agregacoes.html` | igual | Saída gerada; a mesma análise em página. |
| `RDS_Hall_2_Floorplan_(1).pdf` | `plantas/rds_hall2_oficial.pdf` | Planta oficial do RDS, com as cotas do Hall 2. |
| `MRV - DUBLIN.pdf` | `referencias/mrv_dublin.pdf` | Referência sobre a MRV. |
| `SEÇÕES E RESPECTIVAS AGREGADAS - DUBLIN.pdf` | `referencias/secoes_agregadas_dublin.pdf` | Referência das agregações. |
| `2026.7.6_Proposta_Agregação_Eleições.xlsx` | `referencias/proposta_agregacao_tse_2026-07-06.xlsx` | Proposta de agregação do TSE. |
| `MIGRACAO.md` | — | Este arquivo. Não copiar: cumpriu a função ao ser executado. |

Os renomeados perdem espaços, acentos e parênteses. Nomes de arquivo com espaço
quebram comandos e links relativos.

### 1.2 Ficam para trás

| Arquivo | Por quê |
|---|---|
| `PLANO COM FLUXOS MELHORADO.png` | Desenho de fluxo com duas entradas, anterior às plantas de 16/09. Superado pela geometria de três zonas. Continua no histórico do repositório de origem, que passa a ser o arquivo morto do projeto. |

### 1.3 Referenciados mas ausentes

`docs/contexto.md` (§2.5) cita dois arquivos que nunca estiveram no repositório:
`contraproposta_agregacao_dublin.xlsx` e `Irlanda_-_Dublin.xlsx`. Ou se recuperam do
Google Drive do Posto e entram em `referencias/`, ou a menção no texto passa a dizer
onde eles estão. Deixar a citação apontando para o nada é o pior dos três caminhos.

---

## 2. Arquivos que só você tem

Nada disto está em nenhum repositório. Sem eles a migração fica incompleta, e o
item 1 é o motivo declarado da transferência.

| O que | Onde deve ficar | Observação |
|---|---|---|
| **O artefato interativo da planta do Hall 2** | `mapa/` | É a página com o rótulo das mesas alternando entre Seções, Nº eleitor e MRV. Salvar o HTML fonte; se estiver publicado como Artifact, guardar também a URL num `mapa/README.md`, porque o repositório guarda o fonte, não a publicação. |
| **Planta do Ring 3** (pátio de fila, 44 × 35 m, 23 raias) | `plantas/ring3_filas.png` | É a fonte das cotas que `CLAUDE.md` descreve em texto. Hoje a geometria existe só como prosa. |
| **Planta do Hall 2** (salão, portas S1–S9, mesas por parede) | `plantas/hall2_salao.png` | Idem. É também a fonte da distribuição de urnas por zona conferida por `scripts/zonas_balanceadas.py`. |

Se o artefato tiver dados embutidos — a tabela de mesas, seções e números de urna —
vale extrair esses dados para um arquivo próprio em `data/` e fazer a página lê-lo,
em vez de manter duas cópias dos mesmos números que podem divergir. Decisão para a
sessão que fizer a migração, com o fonte em mãos.

---

## 3. Estrutura de destino

```
<repositório final>/
├── CLAUDE.md                  memória do projeto
├── README.md                  porta de entrada (novo, §5)
├── docs/
│   ├── agregacoes.md
│   ├── contexto.md
│   ├── plano_voluntarios.md
│   └── pendencias.md
├── plantas/
│   ├── ring3_filas.png        a fornecer
│   ├── hall2_salao.png        a fornecer
│   └── rds_hall2_oficial.pdf
├── referencias/
│   ├── mrv_dublin.pdf
│   ├── secoes_agregadas_dublin.pdf
│   └── proposta_agregacao_tse_2026-07-06.xlsx
├── mapa/                      artefato interativo, a fornecer
├── data/raw/                  dois CSVs + o PNG do mapa do TSE
├── scripts/                   quatro scripts + requirements.txt
└── saidas/                    três arquivos gerados
```

`.gitignore`: manter `__pycache__/` e `*.pyc`. **Não** ignorar `saidas/` — os três
arquivos de lá são entregáveis, e quem abre o repositório precisa deles sem ter de
instalar Python.

---

## 4. Reescritas de caminho obrigatórias

Mover os arquivos quebra referências dentro do texto. São poucas e todas verificadas:

| Arquivo | Trocar | Por | Ocorrências |
|---|---|---|---|
| `CLAUDE.md` | `contexto_eleicoes_dublin_2026.md` | `docs/contexto.md` | 2 |
| `CLAUDE.md` | `PENDENCIAS` | `docs/pendencias.md` | 2 |
| `CLAUDE.md` | `plano_voluntarios_apoio.md` | `docs/plano_voluntarios.md` | 1 |
| `CLAUDE.md` | `README.md` (na lista de documentos) | `docs/agregacoes.md` | 1 |
| `CLAUDE.md` | `RDS_Hall_2_Floorplan_(1).pdf` | `plantas/rds_hall2_oficial.pdf` | 1 |
| `CLAUDE.md` | parágrafo final da seção de geometria, que cita `PLANO COM FLUXOS MELHORADO.png` | reescrever apontando para `plantas/` e dizendo que o PNG antigo ficou no repositório de origem | 1 |
| `docs/plano_voluntarios.md` | `contexto_eleicoes_dublin_2026.md` | `docs/contexto.md` | 3 |
| `docs/plano_voluntarios.md` | `PENDENCIAS` | `docs/pendencias.md` | 4 |
| `scripts/zonas_balanceadas.py` | `contexto_eleicoes_dublin_2026.md` (docstring) | `docs/contexto.md` | 1 |

`docs/agregacoes.md` não precisa de ajuste: só cita `scripts/`, `saidas/` e
`data/raw/`, que não mudam de lugar.

A seção "Documentos do repositório" do `CLAUDE.md` precisa ganhar as entradas novas:
`plantas/`, `referencias/` e `mapa/`.

---

## 5. README do repositório final

O `README.md` atual vira `docs/agregacoes.md` — ele fala só das agregações, e o
projeto hoje é maior que isso. Criar um README novo na raiz, curto, com:

1. Uma frase sobre o que é: organização do 1º turno de 04/10/2026 em Dublin,
   16.794 aptos, 28 urnas, RDS.
2. Onde está cada coisa (a árvore da §3, comentada).
3. Como rodar o pipeline:
   ```bash
   pip install -r scripts/requirements.txt
   python3 scripts/mapa_agregacoes.py   # gera saidas/dados.json e o xlsx
   python3 scripts/gera_pagina.py       # gera a página HTML
   python3 scripts/zonas_balanceadas.py # confere o equilíbrio das zonas
   ```
4. Um ponteiro explícito: **leia `CLAUDE.md` antes de mexer em número.**

---

## 6. Passo a passo

```bash
# 1. origem, na branch certa
git clone --branch claude/elegant-euler-jss6uv \
  https://github.com/hamadmkalaf/eleicoes2026 origem

# 2. destino, vazio
git init destino && cd destino

# 3. estrutura
mkdir -p docs plantas referencias mapa data/raw scripts saidas

# 4. o que vai direto
cp ../origem/CLAUDE.md .
cp ../origem/plano_voluntarios_apoio.md docs/plano_voluntarios.md
cp ../origem/contexto_eleicoes_dublin_2026.md docs/contexto.md
cp ../origem/README.md docs/agregacoes.md
cp ../origem/PENDENCIAS docs/pendencias.md
cp ../origem/data/raw/* data/raw/
cp ../origem/scripts/* scripts/
cp ../origem/saidas/* saidas/
cp "../origem/RDS_Hall_2_Floorplan_(1).pdf" plantas/rds_hall2_oficial.pdf
cp "../origem/MRV - DUBLIN.pdf" referencias/mrv_dublin.pdf
cp "../origem/SEÇÕES E RESPECTIVAS AGREGADAS - DUBLIN.pdf" \
   referencias/secoes_agregadas_dublin.pdf
cp "../origem/2026.7.6_Proposta_Agregação_Eleições.xlsx" \
   referencias/proposta_agregacao_tse_2026-07-06.xlsx
cp ../origem/.gitignore .
```

Depois: converter `docs/pendencias.md` para markdown, aplicar as reescritas da §4,
escrever o `README.md` da §5, acrescentar os arquivos da §2 e só então rodar a
verificação da §7.

---

## 7. Verificação de aceite

A migração está correta quando as quatro coisas abaixo passam. Rodar antes do
primeiro commit no repositório final.

```bash
pip install -r scripts/requirements.txt
python3 scripts/mapa_agregacoes.py
python3 scripts/gera_pagina.py
python3 scripts/zonas_balanceadas.py
```

1. `mapa_agregacoes.py` termina sem erro. Ele falha de propósito se as validações
   não passarem, então terminar já é o teste: 16.794 eleitores pelos três caminhos
   de soma, 51 seções, 28 urnas, e a conferência independente contra
   `QT_ELEITOR_ELEICAO_FEDERAL`.
2. `zonas_balanceadas.py` imprime **3.860 / 3.755 / 3.802**, spread de **2,8%**, e
   "Cada zona tem exatamente uma das três urnas grandes".
3. `saidas/dados.json` e `saidas/dublin_agregacoes.html` regerados **idênticos** aos
   copiados — ambos são texto determinista, sem data de geração embutida:
   ```bash
   git status --porcelain saidas/dados.json saidas/dublin_agregacoes.html
   ```
   tem de sair vazio. Se sair alguma coisa, alguma entrada veio diferente na cópia.
   **Não vale para o `.xlsx`**: openpyxl grava a data de criação dentro do arquivo,
   então ele difere byte a byte a cada execução mesmo com os dados iguais. Para
   conferir o xlsx, compare o conteúdo das abas, não o arquivo.
4. Nenhum link quebrado: `grep -rn "PENDENCIAS\|contexto_eleicoes_dublin_2026\|plano_voluntarios_apoio" .`
   não retorna nada.

O item 3 é o que pega erro de cópia silencioso. Não pular.

---

## 8. Decisões que não podem se perder

Estão todas em `CLAUDE.md` e em `docs/plano_voluntarios.md`, mas repetidas aqui
porque são o resultado do trabalho, e o que se perde numa migração é sempre o que
não estava escrito em dois lugares.

- **Geometria.** Ring 3 é o pátio de fila ao ar livre; Hall 2 é o salão de votação.
  A letra da zona (A, B, C) acompanha o eleitor da raia até a parede: zona do Ring →
  porta do Hall (S4, S5, S6) → parede do salão (oeste, norte, leste).
- **Distribuição de urnas por zona está fechada** em 3.860 / 3.755 / 3.802 de
  comparecimento esperado, com uma urna grande por zona. Não mexer sem refazer a
  conta com `scripts/zonas_balanceadas.py`.
- **Efetivo de voluntários:** 45 postos no pico, 32 fora dele, 57 escalados,
  66 recrutados.
- **Decisões do Posto de 16/09:** triagem preferencial com 1 pessoa; fluxo de saída
  opcional; encerramento das 17h acumulado pelo posto de cabeça de fila; contagem de
  fluxo descartada; coordenadores já contados.
- **Regra que governa o desenho:** nenhum posto para o eleitor. Sinalização atende o
  caso padrão, voluntário atende a exceção.
- **Três pendências abertas com número:** ~926 m de barreira necessários contra
  200 m orçados; protocolo de chuva para um pátio inteiramente descoberto; lista
  nominal para o balcão de consulta.
