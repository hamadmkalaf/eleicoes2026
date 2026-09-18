# Transferência — Separadores de fila e fita no chão no Hall 2

> **Tema:** o desenho definitivo de como as 100 unifilas e a fita adesiva de
> piso conduzem o eleitor da porta até a mesa, no Hall 2 do RDS.
>
> Este documento é para quem vai montar o tema noutro repositório. Diz o que
> levar, o que o levado depende, em que ordem rodar e **como provar que a
> transferência deu certo**. O porquê de cada decisão está no
> `contexto_separadores_fila_hall2.md`, que vai junto.

---

## 1. Em uma tela

| | |
|---|---|
| Origem | `hamadmkalaf/eleicoes2026`, branch `claude/line-separator-layout-j61pe9` (PR #28) |
| Commits do tema | `5f1eb87` → `7e3e202` → `84d5e36` → `8af6b12` (+ este) |
| O que levar | **12 arquivos** — 2 de código e dados, 3 documentos, 4 SVG, 1 JSON de saída, 2 PNG |
| Do que depende | 3 arquivos que **não** são deste tema e têm de existir no destino |
| Prova de que deu certo | `python3 scripts/separadores_fila.py --grava` sai com **código 0** e regenera os 4 SVG idênticos aos copiados |
| Estado | **fechado.** Desenho definitivo decidido em 17/09; o que falta é resposta de terceiros (§7) |

---

## 2. O que levar

### Código e dados próprios (2)

| Arquivo | O que é |
|---|---|
| `scripts/separadores_fila.py` | monta o catálogo de barreira, precifica em postes, calcula a fita por cor, confere a regra das avenidas e desenha tudo |
| `data/grupos_mesas.json` | os 16 grupos de mesas (A1–A5, B1–B5, C1–C6) com MRVs, coordenadas e seções |

### Documentos (3)

| Arquivo | O que é |
|---|---|
| `plano_separadores_fila.md` | o desenho definitivo: decisões, geometria, as 98 unifilas, a fita por cor, os achados e as pendências |
| `contexto_separadores_fila_hall2.md` | o contexto consolidado — leia antes de mexer em qualquer número |
| `TRANSFERENCIA_SEPARADORES_FILA.md` | este documento |

### Saídas geradas (7)

`saidas/separadores_definitivo.svg` (a planta que vale) ·
`saidas/separadores_detalhe.svg` (o corte do ramal, barreira → fita → mesa) ·
`saidas/separadores_opcao1.svg` e `saidas/separadores_opcao2.svg` (as duas
alternativas descartadas, mantidas como registro) ·
`saidas/separadores_fila.json` (premissas, catálogo e as três alocações).

Mais dois PNG, gerados dos SVG: `saidas/separadores_definitivo.png` e
`saidas/separadores_detalhe.png`. Servem para telegrama, apresentação e conversa
com o RDS, onde SVG não entra. Os PNG das duas opções descartadas não precisam
viajar.

---

## 3. Do que o tema depende — e não é dele

`scripts/separadores_fila.py` **lê** três arquivos que pertencem a outros temas
e **não escreve em nenhum**. Sem eles, nada roda:

| Arquivo | De quem é | O que o tema tira dele |
|---|---|---|
| `data/prancheta_hall2.json` | arranjo do Hall 2 | contorno do salão, as 18 portas, o módulo (4,10 × 0,90 m), o cenário base |
| `data/decisoes.json` | arranjo do Hall 2 | as 28 mesas com parede/entrada/classe, as zonas protegidas, os 3 serpenteados, a sinalização das portas |
| `cenarios/paredes-abc-20260915.json` | arranjo do Hall 2 | a posição e a rotação de cada uma das 28 mesas |

**Consequência prática:** este tema não viaja sozinho. Ou o repositório de
destino já tem o arranjo do Hall 2, ou os três arquivos acima vão junto. Se
forem junto, vão **como estão** — editá-los à mão quebra as conferências do tema
de origem.

---

## 4. Como rodar, e como provar

```bash
python3 scripts/separadores_fila.py           # conferência + relatório, sem gravar
python3 scripts/separadores_fila.py --grava   # + os 4 SVG e o JSON
```

Sem dependências externas: só `json`, `math`, `os` e `sys` da biblioteca padrão.
Não acessa a rede.

**A prova tem três partes, e as três têm de passar:**

1. **A conferência das avenidas.** O script imprime as faixas de x e sai com
   **código 1** se alguma avenida cruzar outra ou invadir zona protegida. No
   destino, tem de imprimir exatamente:

   ```
   As avenidas não se cruzam — faixas de x, disjuntas:
       A:  11.00 ..  25.03 m
       B:  26.80 ..  29.80 m
       C:  32.00 ..  36.50 m
       nenhuma avenida invade zona protegida
   ```

2. **Os números da definitiva.** `98 unifilas em 133 m · reserva móvel 2` e
   `fita: 769 m (846 m com retoque) · 20 rolos de 50 m`.

3. **A cadeia é determinística.** Rodar `--grava` duas vezes tem de gerar SVG
   byte a byte idênticos, e idênticos aos que foram copiados. Se um SVG mudar,
   alguma das três dependências do §3 mudou junto — investigue antes de aceitar.

Se qualquer uma das três falhar, **a transferência não terminou.**

---

## 5. O que fica para trás

| Item | Por quê |
|---|---|
| `saidas/separadores_opcao3.svg`/`.png` | foi renomeado para `separadores_definitivo` quando a Opção 3 virou definitiva; o arquivo antigo é a geometria velha |
| Os PNG das opções 1 e 2 | as alternativas descartadas bastam em SVG; o PNG só vale para o que vai a reunião |
| `saidas/sinalizacao_v2.json` (branch `claude/voter-route-signage-update-bjgbhp`) | o tema só precisa do agrupamento, já extraído para `data/grupos_mesas.json`; o resto é do tema de sinalização, e traz duas cores superadas e o `pos_banner` errado da parede leste |

---

## 6. O que criar no repositório novo

**Um `CLAUDE.md`, ou um parágrafo no que já existir**, dizendo no mínimo:

- **leia `contexto_separadores_fila_hall2.md` antes de tocar na geometria** — as
  três decisões de 17/09 e a regra "as avenidas levam para dentro, as bandas
  trazem para fora" são o que sustenta o desenho inteiro;
- **nunca edite `data/decisoes.json`, `data/prancheta_hall2.json` nem o cenário
  `paredes-abc`** a partir deste tema — eles são lidos, não escritos;
- **a conferência das avenidas sai com código 1**; rodá-la antes de qualquer
  commit que toque em `AVENIDAS`, `BANDA_PAREDE` ou nas zonas protegidas;
- as constantes que mudam tudo estão no topo de `separadores_fila.py`:
  `VAO_POSTE`, `BANDA_PAREDE`, `LARG_CANAL`, `PASSO_FILA`, `CORES_ZONA`,
  `ESTOQUE_FITA`.

**Integração contínua**, se houver: `separadores_fila.py` sem `--grava` é um
teste pronto — não escreve nada e já sai com código 1 quando a geometria quebra.

---

## 7. O que está em aberto quando isto chega

Herde a lista inteira; a primeira é bloqueante.

1. **O RDS permite fita adesiva no piso do Hall 2?** Se não, o desenho inteiro
   cai. Pergunta para esta semana.
2. Submeter o layout de barreira ao responsável de incêndio do RDS.
3. Comprar **15 unifilas** (EUR 195,45) e **11 rolos de fita** (3 azul, 3
   laranja, 1 amarelo, 1 zebrado, 1 verde, 2 branco).
4. Confirmar a **especificação** dos 165 m por cor em estoque: fita de
   **marcação de piso** ou de embalagem? Se forem de embalagem, não servem, o
   estoque vale zero e a compra vai a 17 rolos. *(A quantidade já está
   confirmada: 165 m por cor, 18/09.)*
5. Aferir em campo as bandas de 11,00 / 9,00 / 10,80 m e a folga de **36 cm**
   entre a boca da avenida A e o recuo S3.
6. Levar ao tema de sinalização os dois achados: o x-banner da parede leste está
   em 45,70 e devia estar em 42,70; e nos grupos vermelhos os 4,60 m caem dentro
   do serpenteado.
7. Definir quem cola os 769 m de fita, e quando.

---

## 8. Três armadilhas conhecidas

**A primeira: mudar uma banda e esquecer a fita.** `BANDA_PAREDE` entra em dois
lugares — no comprimento do ramal desenhado e na metragem de fita. Já houve um
caso em que a fita continuou usando um valor único de 9,00 m depois de as bandas
virarem 11,00 / 9,00 / 10,80, e isso subestimou azul e laranja em cerca de 40 m
cada. Se mexer na banda, confira a tabela de fita por cor.

**A segunda: contar a boca duas vezes.** A avenida B entra inteira na alocação
definitiva, então **não** leva item de boca separado. Somar os dois conta os
primeiros 6 m duas vezes e estoura o orçamento em 10 unifilas.

**A terceira: rotular por número de mesa.** O eleitor sabe a sua **seção**, não
a sua mesa. Toda peça voltada ao público — fita, papel, banner — é rotulada por
**grupo e seção**. É a convenção do artefato de sinalização, e mudá-la aqui
criaria duas linguagens no mesmo salão.

---

## 9. Uma nota sobre branches

O repositório de origem tem mais de trinta branches e nenhum `main`; o branch
padrão é `claude/dublin-electoral-sections-3odh1w`. Este tema foi desenvolvido
em `claude/line-separator-layout-j61pe9` e **não foi mesclado** — a decisão de
para onde integrar ficou em aberto.

No repositório novo, **um branch só, com merge de volta**. A causa da confusão
aqui é conhecida: cada sessão trabalhou num branch próprio e nenhuma mesclou de
volta, e o sintoma mais caro foi um gerador lendo um `decisoes.json` que outro
branch já havia superado.
