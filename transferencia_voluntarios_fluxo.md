# Transferência — tema "Voluntários de apoio e fluxo do eleitor"

> **Tema:** o desenho do voluntariado que organiza o percurso do eleitor no dia da
> votação — funções, posições, efetivo e cenários de escala.
>
> Instruções para levar **este tema** a outro repositório. Escrito para ser executado
> por outra sessão do Claude, sem depender da conversa que o originou.

Para mover o projeto inteiro, e não só este tema, use `MIGRACAO.md` — ele cobre também
o pipeline de dados, as agregações, o orçamento e as referências do Cartório. Este
arquivo é o recorte temático, e os dois não se contradizem: onde houver sobreposição,
vale o destino que o `MIGRACAO.md` define.

---

## 0. Leia antes de clonar

As versões finais **não estão na branch padrão** do repositório de origem
`hamadmkalaf/eleicoes2026`, que é `claude/dublin-electoral-sections-3odh1w`. Tudo o que
este tema produziu está em `claude/elegant-euler-jss6uv`, no PR #24, ainda em draft.

```bash
git clone --branch claude/elegant-euler-jss6uv \
  https://github.com/hamadmkalaf/eleicoes2026 origem
```

Clonar sem `--branch` traz arquivos desatualizados e a transferência sai errada em
silêncio.

---

## 1. O que compõe o tema

### 1.1 Produzido por este trabalho — vai inteiro

| Origem | Destino sugerido | O que é |
|---|---|---|
| `lista_postos.md` | `docs/voluntarios/lista_postos.md` | **A fonte única.** Os 17 postos, os quatro cenários, a fila de preenchimento da posição 10 à 49, as compensações. É o documento do briefing. |
| `voluntarios_postos.html` | `mapa/voluntarios_postos.html` | Os postos marcados sobre a rota e sobre a planta do salão, com seletor de cenário. Publicado em https://claude.ai/artifact/YaFNHUua2Hkqu7dtR7tf7A |
| `contexto_voluntarios_fluxo.md` | `docs/voluntarios/contexto.md` | Contexto consolidado do tema: o princípio de projeto, os achados com a conta, as correções feitas no caminho, as premissas. Leitura obrigatória antes de mexer em número. |
| `plano_voluntarios_apoio.md` | `docs/voluntarios/dimensionamento.md` | O raciocínio: taxas de chegada, dimensionamento, achados das plantas, riscos de segunda e terceira ordem. Carrega um aviso de que seus códigos de posto são da revisão anterior. |
| `transferencia_voluntarios_fluxo.md` | — | Este arquivo. Não copiar: cumpriu a função ao ser executado. |

### 1.2 Insumo obrigatório — sem isto o tema não se sustenta

| Origem | Destino | Por quê |
|---|---|---|
| `CLAUDE.md`, seções **Geometria do local** e **Cenários de efetivo** | `CLAUDE.md` do destino | A geometria é a base de toda posição de posto. Se o destino já tiver `CLAUDE.md`, **funda** as duas seções em vez de sobrescrever o arquivo. |
| `contexto_eleicoes_dublin_2026.md` | `docs/contexto_geral.md` | Orçamento (a unifila de 200 m, os 20 seguranças, os EUR 1.961 de sinalização) e as taxas de comparecimento de 2022. |
| `saidas/dados.json` | `saidas/dados.json` | Fonte dos aptos e do comparecimento por urna. |
| `scripts/zonas_balanceadas.py` | `scripts/` | Confere a composição das três zonas contra os dados. Único script que este tema usa. |

### 1.3 Não faz parte do tema

Pipeline de agregação (`scripts/parse_dados.py`, `mapa_agregacoes.py`,
`gera_pagina.py`), os CSVs em `data/raw/`, os PDFs de referência do Cartório e as
planilhas de proposta do TSE. Se o repositório de destino for só deste tema, eles ficam
de fora — mas então `saidas/dados.json` passa a ser um arquivo órfão, sem quem o
regenere, e isso precisa estar dito no README do destino.

---

## 2. O que só você tem

Nada disto está em repositório nenhum. São os quatro desenhos que sustentam as posições
dos postos, e a lista que o posto P0 precisa.

| O quê | Onde deve ficar | Observação |
|---|---|---|
| **Artefato da Rota do Eleitor** — https://claude.ai/artifact/1PQjgzstbiNorfJgagXhB5 | `mapa/rota_do_eleitor.html` | Define os pontos P0–P7, a tabela mestra seção → porta e o plano de sinalização. É a origem dos códigos de posto. |
| **Prancheta do Hall 2 pelas seções** — https://claude.ai/artifact/Szv5egKpHy3umh4udAybvr | `mapa/prancheta_hall2.html` | Coordenadas reais de portas e das 28 mesas; a planta do salão no `voluntarios_postos.html` foi gerada delas. |
| **Ring 3** — https://claude.ai/artifact/FcQs4H7fM3RcBxmyFywazV | `mapa/ring3.html` | **Não foi lido na íntegra neste trabalho.** Conferir contra a §5 do contexto. |
| **Sinalização interna** — https://claude.ai/artifact/BcT5yzxRkSaUsbbHQQgjWF | `mapa/sinalizacao_interna.html` | **Não foi lido na íntegra neste trabalho.** |
| **Plantas em imagem** do Ring 3 e do Hall 2 | `plantas/` | A geometria do `CLAUDE.md` é prosa escrita a partir delas. Sem as imagens, a descrição perde a fonte. |
| **Caderno nominal de seções** (51 seções × nome do eleitor, do Cartório) | `data/` | Insumo do posto P0. Pode não existir — ver pendência 3 do contexto. |

Guardar o **fonte** de cada artefato, não só a URL: o repositório versiona o arquivo, a
publicação é outra coisa. Registrar as URLs num `mapa/README.md`.

---

## 3. Reescritas de caminho

Mover os arquivos quebra referências no texto. Conferidas uma a uma:

| Arquivo | Trocar | Por |
|---|---|---|
| `docs/voluntarios/contexto.md` | `lista_postos.md` | `docs/voluntarios/lista_postos.md` |
| `docs/voluntarios/contexto.md` | `plano_voluntarios_apoio.md` | `docs/voluntarios/dimensionamento.md` |
| `docs/voluntarios/contexto.md` | `voluntarios_postos.html` | `mapa/voluntarios_postos.html` |
| `docs/voluntarios/contexto.md` | `contexto_eleicoes_dublin_2026.md` | `docs/contexto_geral.md` |
| `docs/voluntarios/contexto.md` | `PENDENCIAS` | o equivalente no destino |
| `docs/voluntarios/lista_postos.md` | `plano_voluntarios_apoio.md` | `docs/voluntarios/dimensionamento.md` |
| `docs/voluntarios/lista_postos.md` | `voluntarios_postos.html` | `mapa/voluntarios_postos.html` |
| `docs/voluntarios/dimensionamento.md` | `lista_postos.md` (3×) | `docs/voluntarios/lista_postos.md` |
| `docs/voluntarios/dimensionamento.md` | `contexto_eleicoes_dublin_2026.md` (3×) | `docs/contexto_geral.md` |
| `scripts/zonas_balanceadas.py` | `contexto_eleicoes_dublin_2026.md` (docstring) | `docs/contexto_geral.md` |

O `voluntarios_postos.html` é autocontido: não referencia nenhum arquivo do
repositório e não precisa de reescrita.

---

## 4. Passo a passo

```bash
git clone --branch claude/elegant-euler-jss6uv \
  https://github.com/hamadmkalaf/eleicoes2026 origem
cd <repositório de destino>
mkdir -p docs/voluntarios mapa plantas saidas scripts

cp ../origem/lista_postos.md              docs/voluntarios/lista_postos.md
cp ../origem/contexto_voluntarios_fluxo.md docs/voluntarios/contexto.md
cp ../origem/plano_voluntarios_apoio.md   docs/voluntarios/dimensionamento.md
cp ../origem/voluntarios_postos.html      mapa/
cp ../origem/saidas/dados.json            saidas/
cp ../origem/scripts/zonas_balanceadas.py scripts/
cp ../origem/contexto_eleicoes_dublin_2026.md docs/contexto_geral.md
```

Depois: fundir as seções de geometria e de cenários do `CLAUDE.md` de origem no
`CLAUDE.md` do destino, aplicar as reescritas da §3, acrescentar os arquivos da §2, e
só então rodar a verificação.

---

## 5. Verificação de aceite

A transferência está correta quando as cinco coisas abaixo passam.

1. `python3 scripts/zonas_balanceadas.py` imprime **3.860 / 3.755 / 3.802**, total de
   **11.417**, spread de **2,8%**, e "Cada zona tem exatamente uma das três urnas
   grandes". São os números do estimador grosso do script; a base B da prancheta dá
   3.834 / 3.832 / 3.833 e 11.499. As duas convivem de propósito — ver §6 do contexto.
2. As quatro colunas de `lista_postos.md` somam **9, 15, 24 e 43** postos (o C4 tem
   ainda 6 de reserva, fechando 49).
3. `mapa/voluntarios_postos.html` abre num navegador, os quatro botões de cenário
   trocam os números dentro dos círculos, e a coluna correspondente da tabela é
   destacada.
4. Nenhum link quebrado:
   `grep -rn "PENDENCIAS\|contexto_eleicoes_dublin_2026\|plano_voluntarios_apoio\|lista_postos\|voluntarios_postos" .`
   não retorna caminho que não exista.
5. O `CLAUDE.md` do destino contém a seção de geometria (Ring 3 como pátio de fila,
   Hall 2 como salão, portas S4/S5/S6/S7) e a tabela dos quatro cenários.

O item 2 é o que pega erro de cópia parcial. Não pular.

---

## 6. O que não pode se perder

Se tudo o mais falhar, estas são as afirmações que o tema precisa carregar:

- **A sinalização atende o caso padrão; o voluntário atende a exceção.** Nenhum posto
  para o eleitor: a 40 chegadas por minuto, inspeção de 100% não escala em nenhuma
  configuração de pessoal.
- **P0 é o posto crítico.** Fica fora do portão, na calçada. Depois do portão toda peça
  pressupõe a seção conhecida, e não há regra numérica de atalho.
- **C4 é referência de teto, não meta de recrutamento** — decisão do Posto, 17/09.
- **O preenchimento é uma fila contínua da posição 10 à 49**, não uma escada de
  cenários. Serve para qualquer efetivo intermediário.
- **C1 e C2 só fecham com três compensações contratadas:** seguranças assumindo presença
  de fila por escrito, CCB de separação no apron, e a campanha "descubra sua seção antes
  de sair de casa".
- **Voluntário orienta, não decide.** Identificação é monopólio legal do mesário.
- **Três pendências com número:** ~926 m de barreira necessários contra 200 m orçados;
  protocolo de chuva para um pátio inteiramente descoberto; lista nominal para o P0.
