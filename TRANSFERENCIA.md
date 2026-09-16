# Transferência para o repositório novo

Este documento é para ser lido por quem vai montar o repositório final — muito
provavelmente numa outra sessão do Claude, sem o histórico desta. Ele diz o que
levar, o que deixar, em que ordem, e como provar que a transferência deu certo.

**O desenho do Hall 2 está fechado.** O cenário `Paredes_ABC` é final, e as duas
conferências passam limpas. O que falta é separar o que produz esse desenho do
sedimento de vinte e tantas iterações.

---

## 1. Em uma tela

| | |
|---|---|
| Origem | `hamadmkalaf/eleicoes2026`, branch `claude/adoring-keller-zrmecn` (PR #23) |
| O que levar | **28 arquivos**, listados por `python3 scripts/exporta_final.py --listar` |
| Como levar | `python3 scripts/exporta_final.py /caminho/do/repo-novo --verificar` |
| Prova de que deu certo | o `--verificar` roda a cadeia inteira no destino e compara o que ela regenerou com o que foi copiado |
| Peça publicada | [Prancheta pelas Seções](https://claude.ai/artifact/Szv5egKpHy3umh4udAybvr) |

O `--verificar` é o ponto importante: ele não confere se os arquivos chegaram,
confere se **o repositório novo reproduz o desenho do zero**. Hoje ele responde:

```
  os 5 arquivos gerados saíram idênticos aos copiados — a cadeia é determinística
  a cadeia fecha sozinha no destino
```

Se essa linha não aparecer no destino, a transferência não terminou.

---

## 2. A cadeia, em sete passos

Nenhum passo depende de rede. Os dois primeiros precisam de `pandas` e
`openpyxl`; do terceiro em diante, de `pdfplumber`.

```bash
pip install pandas openpyxl pdfplumber

python3 scripts/mapa_agregacoes.py           # 1. os CSV do TSE  → saidas/dados.json
python3 scripts/gera_pagina.py               # 2. a página das agregações
python3 scripts/gera_decisoes_base.py --grava  # 3. os PDFs      → as 28 mesas
python3 scripts/arranjo_paredes.py --grava   # 4. o arranjo, as zonas e o cenário
python3 scripts/gera_prancheta_por_secao.py  # 5. a prancheta pelas seções
python3 scripts/confere_prancheta.py         # 6. confere os dados
python3 scripts/confere_arranjo.py           # 7. confere os sete itens do arranjo
```

Como isso se encadeia:

```
data/raw/*.csv ──▶ mapa_agregacoes ──▶ saidas/dados.json ──┐
                                                            ├─▶ gera_decisoes_base
data/oficiais/*.pdf ──▶ fontes_oficiais ───────────────────┤      │
                        comparecimento ────────────────────┘      ▼
                                                     data/decisoes.json (bloco mesas)
                                                                  │
data/prancheta_hall2.json ──────────────▶ arranjo_paredes ◀───────┘
                                              │
                    cenarios/paredes-abc-20260915.json
                    data/decisoes.json (camada de layout)
                                              │
                                              ▼
                              gera_prancheta_por_secao
                                              │
                              saidas/prancheta_por_secao.html
```

`data/decisoes.json` é lido **e** escrito: o passo 3 põe as 28 mesas, o passo 4
escreve a camada de layout por cima. Por isso a ordem 3 → 4 importa, e por isso
ele é versionado mesmo sendo gerado — é também o registro das decisões do Posto,
com datas e textos que não saem de conta nenhuma.

---

## 3. O que levar

`python3 scripts/exporta_final.py --listar` imprime o manifesto vivo. O resumo:

### Fontes — não geradas, entram como estão (7)

| Arquivo | O que é |
|---|---|
| `data/oficiais/aptos_por_secao_dublin_2026-07-13.pdf` | ELO 13/07: as 51 seções com aptos e condado |
| `data/oficiais/secoes_agregadas_dublin_2026.pdf` | Cartório: os 28 pares principal → agregada |
| `data/oficiais/mrv_mesarios_dublin_2026-09-13.pdf` | Convoca+ 13/09: os 109 mesários por MRV |
| `data/raw/eleitorado_local_votacao_2026_ZZ.csv` | TSE 13/08 |
| `data/raw/Filtrado_Dublin.csv` | TSE 14/07 |
| `data/prancheta_hall2.json` | a geometria medida do salão, do módulo e das 18 portas |
| `RDS_Hall_2_Floorplan_(1).pdf` | a planta original do RDS |

### Cadeia e conferências (11)

`parse_dados.py`, `mapa_agregacoes.py`, `gera_pagina.py`, `comparecimento.py`,
`fontes_oficiais.py`, `gera_decisoes_base.py`, `arranjo_paredes.py`,
`gera_prancheta_por_secao.py`, `prancheta_por_secao_template.html`,
`confere_prancheta.py`, `confere_arranjo.py`.

### Estado e saídas (6)

`data/decisoes.json`, `cenarios/paredes-abc-20260915.json`, `saidas/dados.json`,
`saidas/prancheta_por_secao.html`, `saidas/dublin_agregacoes.html`,
`saidas/Dublin_2026_agregacoes.xlsx`.

### Documentos (4)

`CONFERENCIA_PRANCHETA_2026-09-15.md`, `contexto_eleicoes_dublin_2026.md`,
`PENDENCIAS`, `TRANSFERENCIA.md`.

---

## 4. O que fica para trás, e por quê

| Arquivo | Por quê |
|---|---|
| `data/raw/mapa_agregacoes_TSE.png` | superado pelos PDFs oficiais, **e trazia o erro de digitação** da seção 3222 (que é do Porto) no lugar da 3322 |
| `cenarios/hamad-final-20260914-170656.json` | cenário anterior |
| `cenarios/equitativo.json` | cenário anterior |
| `PLANO COM FLUXOS MELHORADO.png` | rascunho anterior à planta medida |
| `README.md` | é do escopo antigo, só agregações; o repositório novo precisa de um próprio (§7) |

Os cenários antigos não são lixo: são o histórico das decisões. Se o Posto
quiser guardá-los, o lugar é uma pasta `historico/`, **fora** da pasta
`cenarios/` — senão o gerador os lê como alternativas válidas.

---

## 5. O que está noutros branches e precisa de decisão

Esta é a parte que o `exporta_final.py` **não** resolve: o Hall 2 é uma das sete
etapas do projeto, e as outras seis vivem no branch canônico
`claude/vibrant-wozniak-hvmqcr` (PR #18). Nada disso foi conferido por mim —
a lista é para a decisão ser consciente.

| Documento | Onde | Recomendação |
|---|---|---|
| `DOCUMENTACAO_PROJETO.md` | PR #18 | **levar** — é a documentação consolidada das sete etapas, com a §9 de inconsistências |
| `orcamento_final.md`, `orcamentos_itens_pequenos.md` | PR #18 | **levar** — orçamento é entregável |
| `handoff_agregacao_dublin_2026.md` | PR #18 | **levar** — é a única origem escrita das taxas de 2022 por condado (§6) |
| `pesquisa_horarios_pico_votacao.md` | PR #18 | **levar** — é a base de curva de chegada |
| `saidas/analise_gargalos.md` | PR #18 | **levar** — é o que decide identificação em uma ou duas posições |
| `plano_filas_confinado_hall2.md` | `claude/filas-sem-ring-3-b9qvqi` | **levar** — é o plano de filas vigente, já que o Ring 3 caiu |
| `saidas/plano_sinalizacao_interna.md` | `claude/serene-rubin-tdzmlb` | **levar**, mas **regerar**: cita a atribuição mesa → entrada antiga |
| `contexto_ring3_2026.md`, `saidas/plano_ring3*.md`, `saidas/ring3*.svg` | PR #18 | **histórico** — o Ring 3 foi abandonado em 15/09 |
| `docs/SESSAO_*.md` | PR #18 | **histórico** — são passagens de sessão, já absorvidas |
| `saidas/dashboard/**` | PR #18 | **decidir** — 20 páginas geradas; várias citam números superados |
| `saidas/editor.html`, `simulador/**` | PR #18 | **decidir** — a prancheta editável e o simulador de fluxo ainda são úteis, mas leem o `decisoes.json` antigo |
| `data/fotos/*.jpg` (20) | PR #18 | **levar** — é o levantamento fotográfico do local |
| branch `cenarios-hall2` | — | **não levar** — era o branch de dados dos cenários; morre com a pasta `cenarios/` enxuta |

**Aviso que vale para tudo dessa lista:** qualquer peça gerada antes de 15/09
carrega a atribuição mesa → entrada por cota do Ring 3 (A 3.642 / B 4.215 /
C 3.642) e a numeração eleitor antiga. Levar sem regerar é levar número errado.

---

## 6. O que está decidido, e o que não está

### Decidido e congelado

| Decisão | Quando | Onde vive |
|---|---|---|
| Base de comparecimento B — taxa de 2022 por condado | 06/09 | `scripts/comparecimento.py` |
| MRV do DJE como identidade da mesa | 06/09 | `data/decisoes.json`, campo `numeracao` |
| Numeração eleitor: 1 na mesa mais ao sul da oeste, sentido horário | 13/09 | `arranjo_paredes.numeracao_eleitor()` |
| Uma entrada por parede: A→oeste, B→norte, C→leste | 15/09 | `arranjo_paredes.ENTRADA` |
| Ring 3 abandonado | 15/09 | `data/decisoes.json`, bloco `ring3` |
| Portas: S4/S5/S6 entradas, S2/S8 saídas, S7 preferencial | 16/09 | `arranjo_paredes.PAPEIS_PORTA` |
| N2 e O2 desobstruídas, recuo de 3 m | 16/09 | `decisoes.zonas_protegidas` |
| Faixa de emergência de 3 m na fachada leste | 16/09 | idem |
| Sala de apoio entre O1 e a parede norte | 16/09 | idem |
| Serpenteado de ~20 pessoas à frente de cada vermelha | 16/09 | `decisoes.serpenteados` |
| Vão de 3,00 m na dupla, 1,50 entre unidades, 1,90 ao lado da vermelha | 16/09 | `arranjo_paredes`, constantes |

### Em aberto — o repositório novo herda isto

1. **Mesários.** 109 nomeados para 112 lugares, **83 confirmados**. As duas
   lacunas são MRV 24 (588 esperados, 2ª maior carga) e MRV 11 (504, sem
   Presidente nomeado). É o único item que pode desfazer o desenho no dia.
2. **A profundidade da sala de apoio** (7,80 m) é suposição minha, alinhada ao
   recorte sudoeste. Medir em campo.
3. **S7 tem 1,27 m de vão.** Serve um fluxo preferencial pequeno; se a fila
   preferencial crescer, não absorve. Medir antes de imprimir.
4. **As taxas de 2022 por condado não têm fonte primária registrada.** 91% do
   eleitorado está em taxa "direto", mas o repositório nunca guardou de onde
   vieram. O que fecha isso é o
   [`perfil_comparecimento_abstencao_2022`](https://dadosabertos.tse.jus.br/dataset/comparecimento-e-abstencao-2022)
   do TSE, recorte ZZ. Não bloqueia nada; melhora a defesa do número.
5. **A numeração MRV é inferida** como a ordem crescente da seção principal.
   Bate com o bloco que veio do DJE, mas é inferência — está avisado no
   cabeçalho de `gera_decisoes_base.py`.
6. **`plano_filas.py`**, no branch de filas, ainda usa 11.416 fixo no código em
   vez da base B (11.499).
7. **Densidade desigual entre paredes:** 131 esperados por metro na oeste contra
   107 na leste. Carga igual não é fila igual.

---

## 7. O que criar no repositório novo

### `README.md`

O atual é do escopo antigo. O novo precisa de: o que é o posto e a data;
o resultado em uma linha (16.794 aptos, 51 seções, 28 mesas, 3 paredes, 3
entradas); a cadeia dos sete passos; e como rodar as duas conferências.

### `CLAUDE.md`

Para a próxima sessão não refazer o já feito. Precisa dizer, no mínimo:

- **leia `CONFERENCIA_PRANCHETA_2026-09-15.md` antes de tocar no arranjo** — os
  onze adendos são o porquê de cada decisão, e várias ideias "novas" já foram
  testadas e descartadas ali com números;
- **nunca edite `data/decisoes.json` à mão** — rode os passos 3 e 4;
- **nunca mexa na agregação de seções**: o par principal → agregada é do
  Cartório, está conferido contra o PDF, e os mesários já estão nomeados por MRV;
- **as duas conferências saem com código 1** se algo divergir; rodar as duas
  antes de qualquer commit que toque em dados ou arranjo.

### Integração contínua

As duas conferências são um teste pronto. Um workflow que rode
`confere_prancheta.py` e `confere_arranjo.py` a cada push impede que uma
edição manual em `decisoes.json` passe despercebida.

---

## 8. Roteiro para a sessão que vai executar

1. Criar o repositório novo e clonar os dois lado a lado.
2. `python3 scripts/exporta_final.py /caminho/do/repo-novo --verificar`
   — e **exigir** as duas últimas linhas do §1.
3. Escrever `README.md` e `CLAUDE.md` conforme §7.
4. Decidir, item a item, a tabela do §5, e trazer o que for "levar" do PR #18 e
   dos dois branches citados. **Regerar** toda peça anterior a 15/09 antes de
   dar por transferida.
5. Copiar a lista do §6.2 para o `PENDENCIAS` do repositório novo.
6. Publicar a prancheta a partir do repositório novo, ou manter o artefato
   existente e registrar a URL no `README.md`. A URL atual é
   `https://claude.ai/artifact/Szv5egKpHy3umh4udAybvr`; republicar do mesmo
   arquivo mantém o endereço.
7. No repositório antigo, marcar o PR #23 como transferido e parar de commitar
   nele, para não existirem duas fontes da verdade.

---

## 9. Uma coisa para não repetir

O repositório atual tem **26 branches** e quatro cópias divergentes de
`contexto_eleicoes_dublin_2026.md`. A causa é conhecida e está escrita no
`cenarios/README.md`: cada sessão trabalhou num branch próprio e nenhuma
mesclou de volta. O sintoma mais caro apareceu aqui mesmo, duas vezes — um
gerador lendo um `decisoes.json` que outro branch já havia superado.

No repositório novo, **um branch só, com merge de volta**, é o que evita isso.
Se a regra for quebrada, que seja a integração contínua do §7 a avisar, e não a
próxima conferência.
