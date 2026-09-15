# Ring 3 — briefing para abrir uma nova sessão e simular outra possibilidade

Documento de passagem de contexto. Foi escrito para ser **colado ou lido no
início de outra sessão**, de modo que ela possa propor e calcular um cenário
novo de fila sem repetir o trabalho já feito nem reintroduzir erros já
corrigidos.

Complementa — não substitui — `contexto_ring3_2026.md`, que é a memória do
*resultado*. Este aqui é a memória do *método*: como o modelo funciona, o que
pode ser mexido, o que não pode, e como acrescentar um cenário.

- Repositório: `hamadmkalaf/eleicoes2026`
- Branch de trabalho: `claude/ring-3-horizontal-queue-pe4x3f`
- Última revisão desta memória: 15 set 2026

---

## 1. Em uma frase

Ring 3 é o cercado externo de fila do Posto Eleitoral de Dublin (eleição
presidencial brasileira de 4 out 2026, RDS Ballsbridge, Hall 2, 28 mesas,
11.499 eleitores esperados). Ele mede **44 × 35 m** (medida oficial), fica
diante da fachada com um apron de 14 m até as portas, e precisa acomodar em
serpentina a fila das três entradas — A, B e C — com o menor número possível de
separadores de barreira (*crowd control barriers*, CCB), dos quais a empresa
disponibiliza **200 em estoque**.

---

## 2. O que está decidido e não se rediscute

Estas são decisões do Posto, não escolhas do modelo. Uma sessão nova deve
tratá-las como dadas, salvo se o usuário disser o contrário.

| # | Decisão | Consequência no modelo |
|---|---|---|
| 1 | A entrada é pelo **canto nordeste**, perto da porta C | O corredor de chegada é em **L**: um trecho lateral leste + o corredor de fundo |
| 2 | O corredor tem **3,00 m** de largura | Sobram 41 m de largura útil e 32 m de profundidade para as zonas |
| 3 | **Não há garganta de pré-triagem** dentro do Ring | O corredor de fundo foi empurrado até o limite e as filas começam logo depois dele |
| 4 | **Não há baias de flanco** (leste/oeste) | As barreiras laterais são removíveis; a evacuação sai pelos vãos entre zonas e pelo gradil |
| 5 | O **perímetro das zonas não leva CCB** | O gradil já fecha o cercado; a delimitação de zona é feita com fita |
| 6 | A **parede do corredor de fundo não entra na conta** | Fica registrada em `fora_da_conta`, para memória |
| 7 | As **raias do apron até as portas não entram na conta** | Idem |
| 8 | A **zona C precisa de CCB** contra o trecho lateral do corredor | É a única contenção fora das divisórias: dois fluxos em sentidos diferentes, encostados |

Resultado dessas decisões: a conta de separadores tem hoje **dois componentes
apenas** — `divisórias entre as raias` + `separação entre a zona C e o
corredor`. Tudo o mais é fita, gradil, ou está fora do escopo.

---

## 3. O modelo, em termos operacionais

Tudo vive em **`scripts/ring3.py`** (Python de biblioteca padrão, sem
dependências). Rodar é simplesmente:

```bash
python3 scripts/ring3.py          # regenera JSON, markdown e os 8 SVGs
python3 scripts/gera_pagina_ring3.py   # regenera a página HTML a partir do JSON
```

### 3.1 Os parâmetros que governam tudo

```python
LARG_RING, PROF_RING = 44.0, 35.0   # medida oficial
LARG_CORREDOR = 3.00                # corredor de chegada
PROF_SERP     = 35.0 - 3.00 = 32.0  # profundidade que sobra para serpenteado
PASSO_RAIA    = 1.40   # eixo a eixo da divisória
RAIA_UTIL     = 1.20   # largura livre de caminhada
DENS_FILA     = 2.00   # pessoas/m2 em raia, em pé, sob guarda-chuva
VAO_RETORNO   = 1.20   # folga de meia-volta na ponta da raia
VAO_SAIDA     = 1.40   # abertura do portão de saída
SEPARADOR_M   = 2.00   # 1 separador = 2 m de barreira
SEPARADOR_EUR = 13.02  # EUR 1.303,00 / 100 unidades
ESTOQUE_SEPARADORES = 200
```

Capacidade de uma zona = `raias × comprimento_da_raia × RAIA_UTIL × DENS_FILA`,
ou seja **2,4 pessoas por metro linear de raia**.

### 3.2 As duas peças de código que importam

- **`class Zona`** — um bloco de serpenteado. Recebe `(entrada, x0, x1,
  profundidade, orientacao)` e deriva tudo: `raias`, `passo`, `comp`,
  `capacidade`, `divisorias`, `portao`, `toco`, `diagonal`, `meias_voltas`.
  A orientação (`"vertical"` = raias norte-sul, `"horizontal"` = raias
  leste-oeste) muda o comprimento da raia e, por consequência, as divisórias.
- **`class Desenho`** — um cenário. Recebe uma lista de zonas, as baias (hoje
  sempre `{}`) e um dicionário de `barreira_extra`. Tem um `regime`:
  - `REGIME_INTEGRAL` — a divisória é barreira de ponta a ponta;
  - `REGIME_PONTA` — a divisória é fita grossa ancorada por **um** CCB de 2 m
    na ponta livre. A conta deixa de ser proporcional ao comprimento da raia e
    passa a ser proporcional ao **número** de raias.

### 3.3 A regra que impede o desenho de mentir

`segmentos_do_desenho()` produz a lista de segmentos que o SVG desenha **e** a
que a conta soma. `confere_mapa()` compara as duas e **aborta** se divergirem
mais de 5 cm. Qualquer cenário novo tem de passar por aí; se passar, o mapa e
a planilha não podem discordar.

### 3.4 Álgebra da orientação (útil para intuição)

Girar as raias de uma zona não muda o perímetro; muda só as divisórias, por

```
Δ divisórias = 0,14 × (profundidade − largura)   [por zona]
```

Por isso, no Ring de hoje, os dois cenários de barreira integral dão **o mesmo
total** de 740,4 m: a diferença de divisórias entre eles é de centímetros.

---

## 4. Os quatro cenários já calculados

Todos com o Ring de 44 × 35 m, corredor em L de 3 m, sem baias, sem perímetro
de CCB.

| Código | Cenário | Lotação | Barreira | Separadores | A comprar |
|---|---|---|---|---|---|
| `VS` | Raias norte-sul, barreira integral | **1.997** | 740,4 m (708,4 divisórias + 32,0 zona C) | 371 | 171 (€ 2.226,42) |
| `H` | Raias leste-oeste, barreira integral | 1.964 | 740,4 m (708,4 + 32,0) | 371 | 171 (€ 2.226,42) |
| `VSP` | Norte-sul, CCB só na ponta + fita | **1.997** | 78,0 m (46,0 pontas + 32,0 zona C) | **39** | 0 |
| `HP` | Leste-oeste, CCB só na ponta + fita | 1.964 | 164,0 m (132,0 + 32,0) | 82 | 0 |

Detalhes que costumam ser perguntados:

- **Lotação por entrada**, cenários N–S: A 614 / B 768 / C 614. Cenários L–O:
  A 626 / B 712 / C 626.
- **Repartição das zonas**, N–S: 8 / 10 / 8 raias de 32,0 m (larguras 11,2 /
  14,0 / 11,2 m). L–O: 23 / 23 / 23 raias (larguras 11,34 / 13,12 / 11,34 m).
- **Fita grossa** necessária no regime de ponta: 662,4 m (N–S) ou 576,4 m
  (L–O). Ver a ressalva em §6.
- **Fora da conta**, registrado mas não comprado: contorno das zonas ≈ 160 m
  (hoje fita), parede do corredor 39,8 m, raias do apron ≈ 86–88 m.
- **Meias-voltas**: 23 no N–S contra 66 no L–O. Com a perda de 0,60 m por
  meia-volta, a lotação efetiva cai para 1.964 (N–S) e 1.869 (L–O).

**Leitura**: o N–S é melhor em lotação e muito melhor em número de
meias-voltas; o L–O só ganha na descarga (o portão pode ficar no eixo da
porta, porque a borda norte é contínua). O regime de ponta corta a compra a
zero, mas ver §6 antes de recomendá-lo.

---

## 5. Como acrescentar um cenário novo (receita)

1. Escrever uma função `desenho_<nome>()` em `scripts/ring3.py`, no estilo de
   `desenho_vertical_sem_baias()`: montar as zonas com `_zonas(orientacao,
   com_baias=False, prof=..., vao_min=...)`, instanciar `Desenho(...)` com
   `_separacao_do_corredor(prof)` como `barreira_extra`, e preencher `d.notas`
   com as ressalvas honestas do cenário.
2. Se o cenário for uma variação de regime de um existente, usar
   `desenho_com_ccb_na_ponta(base)` — ele clona as zonas e troca só o regime.
3. Em `main()`: incluir o desenho, chamar `confere_mapa(d)`, acrescentar
   `bloco_json(d)` ao dicionário de saída e gerar `svg(d)` + `svg_mapa(d)`.
4. Rodar os dois scripts. Se `confere_mapa` abortar, o desenho e a conta
   discordam — corrigir a lista de segmentos, nunca o total.
5. Atualizar `README.md` e `contexto_ring3_2026.md`, commitar no branch de
   trabalho e atualizar o PR.

### Alavancas que fazem sentido variar

| Alavanca | Onde | Efeito esperado |
|---|---|---|
| Largura do corredor (3,0 m) | `LARG_CORREDOR` | Cada 0,5 m a menos devolve ~0,5 m de profundidade a todas as raias |
| Corredor do lado oeste | `CORREDOR_LATERAL` | Inverte qual zona precisa de CCB de separação |
| Passo da raia (1,40 m) | `PASSO_RAIA` | Mais raias e mais divisórias; cuidado com acessibilidade (cadeira de rodas) |
| Densidade (2,0 p/m²) | `DENS_FILA` | Só muda lotação, não muda barreira — é a premissa mais frágil |
| Regime misto | novo | Barreira integral na zona de maior pressão, fita nas outras |
| Zonas desiguais | `_reparte_raias` | Hoje é proporcional ao esperado; poderia ser proporcional ao tempo de mesa |
| Duas fileiras de profundidade | novo | Serpenteado partido ao meio com um corredor transversal de serviço |

---

## 6. Ressalvas que precisam sobreviver à troca de sessão

Não são opiniões decorativas; cada uma já mudou uma conclusão.

1. **Fita não contém multidão.** Ela marca, não resiste. No regime de ponta,
   cada divisória fica com um vão livre do comprimento inteiro da raia — 28,8 m
   no N–S, 8,7 m no L–O. A 5 m de espaçamento seriam ~115 apoios; se
   esses apoios forem CCBs, o cenário volta a ~154 separadores e a economia
   evapora. O `0 a comprar` do `VSP` é verdadeiro **só se** os apoios vierem de
   outro material.
2. **A corrente de chegada cruza a saída S8.** A entrada no canto nordeste põe
   quem chega no mesmo ponto por onde parte de quem sai passa. Precisa de
   solução de fluxo, não de geometria.
3. **A pré-triagem perdeu endereço dentro do Ring.** Ao eliminar a garganta,
   a conferência de documento e fila preferencial não tem mais lugar
   reservado. Ou acontece no apron, ou antes do cercado.
4. **A lotação não é a demanda.** 1.997 lugares para 11.499 eleitores
   esperados significa ~17% do dia em fila simultânea; o dimensionamento real
   depende da taxa de atendimento das 28 mesas, que ainda não foi modelada.
5. **A aferição do plano original não é comparável na linha de barreira.**
   Está marcado no JSON (`barreira_comparavel: false`). A regra de contagem
   mudou duas vezes — de `perímetro + divisórias` para `divisórias +
   separação da zona C` — então os 380,8 m do modelo não contradizem os 596,3 m
   publicados: contam coisas diferentes. Capacidade e geometria continuam
   comparáveis.
6. **A posição do cercado é estimativa minha**, centrada no eixo da porta S5.
   As dimensões (44 × 35) são oficiais; o posicionamento, não.

---

## 7. Erros já cometidos — não repetir

- **Perímetro faltando na regra de barreira.** A regra contava só as corridas
  paralelas às raias, o que criava uma economia falsa ao girar o desenho. Foi o
  usuário quem encontrou. Qualquer regra nova tem de fechar o polígono ou
  declarar explicitamente que não fecha.
- **Descarga vertical modelada pela boca do bloco.** Na vertical a borda norte
  é aberta pelas meias-voltas; o portão tem de ser o canto do bloco, não o eixo
  da porta.
- **Desenho de "horizontal" errado**, em decks empilhados com tubos de
  ligação. Horizontal quer dizer **raias que correm de leste para oeste**,
  entrada pelo norte e saída pelo sul — nada mais.
- **Desenhos com baias** (L–O e N–S) foram descartados por decisão do Posto;
  não ressuscitar sem pedido explícito.

---

## 8. Mapa de arquivos

| Arquivo | O que é |
|---|---|
| `scripts/ring3.py` | O modelo inteiro: geometria, conta, SVGs, markdown |
| `scripts/gera_pagina_ring3.py` | Constrói o HTML a partir do JSON, sem recalcular nada |
| `saidas/ring3.json` | Todos os números, por cenário — a fonte para citar |
| `saidas/plano_ring3_horizontal.md` | O plano em prosa |
| `saidas/ring3_horizontal.html` | A página "Ring 3, cenários de fila" |
| `saidas/ring3_*.svg` | 4 plantas + 4 mapas de barreira com legenda |
| `contexto_ring3_2026.md` | Memória do resultado (10 seções, todos os números) |
| `contexto_ring3_para_nova_sessao.md` | Este arquivo: memória do método |
| `README.md` | Seção Ring 3 com o corredor em L e a conta de dois componentes |

---

## 9. Prompt sugerido para a nova sessão

> Estou retomando o projeto do Ring 3 (fila externa do Posto Eleitoral de
> Dublin, eleição de 4 out 2026). Leia `contexto_ring3_para_nova_sessao.md` e
> `contexto_ring3_2026.md` na raiz do repositório antes de qualquer coisa. O
> modelo está em `scripts/ring3.py` e roda com Python puro. Quero simular o
> seguinte cenário novo: **[descrever]**. Acrescente-o como um desenho novo,
> sem apagar os quatro existentes, faça `confere_mapa` passar, e me diga a
> lotação, os metros de barreira por componente, os separadores e quantos
> faltam para os 200 do estoque. Aponte as fragilidades do cenário.
