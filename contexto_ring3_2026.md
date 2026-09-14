# Ring 3 — memória de trabalho da fila externa

> Registro consolidado do trabalho sobre o compound de fila ao ar livre do RDS
> (Ring 3), para as eleições presidenciais brasileiras de 4 de outubro de 2026,
> no Hall 2 do RDS Ballsbridge, Dublin. Documento destinado a abrir a próxima
> sessão de trabalho sem repetir o que já foi decidido, medido ou corrigido.
>
> Atualizado em 13/09/2026. Os números vêm de `saidas/ring3.json`, gerado por
> `scripts/ring3.py`; onde este texto e o JSON divergirem, **o JSON manda**.

---

## 1. O objeto

O Ring 3 é um recinto ao ar livre com gradil permanente, ao sul do Hall 2, onde
a fila se forma antes de entrar para votar.

| | |
|---|---|
| Dimensões | **44,0 × 35,0 m** — medida oficial, obtida em 11/09/2026 |
| Posição | Centrado no eixo da porta S5 — **estimativa**, o bordo oeste não foi aferido |
| Apron | 14 m de piso pavimentado entre o gradil norte do Ring e a fachada sul do Hall 2 |
| Portas de entrada | S4 (zona A), S5 (zona B), S6 (zona C), 5,93 m de vão cada, no meio da fachada |
| Portas de saída | S2 (x 13,25–14,45) e S8 (x 42,12–43,32), nos flancos |
| Comparecimento esperado | A 3.642 · B 4.215 · C 3.642 — total 11.499, base B de 2022 |

A geometria do salão, das portas e a atribuição de mesas por entrada vêm das
decisões do Posto de 06/09/2026 e de `scripts/salao.py` — **que não está neste
repositório** (ver §8).

---

## 2. O percurso decidido

1. O eleitor **entra pelo canto nordeste** do Ring, o lado mais próximo da
   porta C. A entrada não é pelo fundo.
2. Desce rente ao gradil leste por um **trecho lateral** de 3,0 m.
3. Vira no fundo, num **trecho de fundo** de 3,0 m encostado no gradil sul.
   Os dois trechos formam o **corredor de chegada em L**.
4. Do trecho de fundo, entra na sua zona (A, B ou C).
5. Percorre o serpenteado e sai ao norte, atravessando o apron até a sua porta.
6. Quem já votou sai por S2 ou S8, nos flancos da fachada.

Consequências de geometria:

- O trecho lateral consome 3,0 m da largura: sobram **41,0 m** para as zonas.
- A zona C fica encostada no trecho lateral — fila parada de um lado, corrente
  descendo do outro. É a **única contenção de verdade** que o desenho pede fora
  das divisórias das raias.

---

## 3. Decisões do Posto que o modelo obedece

Em ordem cronológica de chegada, com o efeito de cada uma:

| # | Decisão | Efeito |
|---|---|---|
| 1 | Eliminar a faixa de garganta / pré-triagem ao sul | Corredor vai para o limite sul; raia cresce de 23,75 m para 32,00 m |
| 2 | Eliminar os desenhos com baias de flanco | Toda a lotação passa a ser fila em raia medida |
| 3 | Entrada pelo canto nordeste, corredor em L | −3,0 m de largura útil; nasce o CCB da zona C |
| 4 | Contorno das zonas com **fita**, não com CCB | −160,2 m da conta (−81 separadores) |
| 5 | Parede do corredor de chegada fora da conta | −39,8 m (−20 separadores) |
| 6 | Raias do apron até as portas fora da conta | −87,7 m (−44 separadores) |
| 7 | Barreiras laterais são removíveis | Evacuação sai pelos vãos entre zonas e pelo gradil; nenhuma área fica vazia de reserva |
| 8 | Estoque da organizadora: 200 separadores, e dá para comprar mais | O teto de 200 é preferência, não restrição |

---

## 4. O modelo

`scripts/ring3.py` (só biblioteca padrão) monta a geometria, mede lotação e
barreira, e desenha as plantas. `scripts/gera_pagina_ring3.py` monta a página a
partir do JSON. Nenhum número é digitado à mão em nenhuma saída.

### 4.1 Parâmetros

| Parâmetro | Valor | Origem |
|---|---:|---|
| Módulo da raia | 1,40 m | **reconstruído** |
| Largura livre da raia | 1,20 m | **reconstruído** |
| Densidade em raia | 2,0 pessoas/m² | **reconstruído** |
| Densidade em baia | 1,8 pessoas/m² | **reconstruído** |
| Vão de meia-volta | 1,20 m | premissa |
| Vão do portão de saída | 1,40 m | premissa |
| Vão entre zonas | ≥ 2,0 m | premissa |
| Profundidade da raia | 32,00 m | Ring (35,0) menos o corredor (3,0) |
| Separador (CCB) | 2,00 m · EUR 13,02 | item *d* do orçamento (100 un. = EUR 1.303) |

Os quatro parâmetros marcados como **reconstruídos** não estão escritos em lugar
nenhum: foram deduzidos por ajuste aos números publicados do plano vigente. São
os valores que reproduzem **exatamente** os 855 dos serpenteados e os 547 das
baias daquele plano — e é essa a única coisa que a reconstrução afere.

### 4.2 Repartição das zonas

A largura de cada zona **não** sai da largura disponível: sai da lotação que
cada entrada precisa. As larguras ficam proporcionais ao comparecimento
esperado, e onde havia baia de flanco (cenários antigos) ela era descontada da
largura de A e C, no equivalente de 6,72 m de serpenteado — equivalência que não
depende da profundidade.

Na orientação vertical a largura da zona é um número inteiro de raias; a sobra
do arredondamento vai para os vãos entre zonas.

### 4.3 A regra de barreira

Hoje, só duas coisas são separador:

```
barreira = divisórias entre as raias + separação entre a zona C e o corredor
```

- **Divisórias**: (n−1) corridas por zona, cada uma 1,2 m mais curta que a raia
  para abrir a meia-volta.
- **Separação da zona C**: o lado leste da zona C, 32,0 m, contra o trecho
  lateral do corredor.

O contorno das zonas, a parede do corredor e as raias do apron ficam
registrados em `fora_da_conta`, com a metragem que teriam — para dimensionar o
que se está abrindo mão e para a conta voltar a fechar se alguma decisão mudar.

### 4.4 O mapa é a conta

`saidas/ring3_barreiras_*.svg` desenha cada corrida de barreira colorida pelo
componente. O desenho e a conta saem **dos mesmos segmentos**, e `main()` aborta
se `confere_mapa()` achar divergência maior que 5 cm em qualquer componente de
qualquer cenário. Planta e número não podem descolar.

---

## 5. Os três cenários salvos

Todos com o Ring de 44 × 35 m, corredor em L, sem baias, raia de 32,00 m.

### 5.1 Raias norte-sul, barreira inteira

| | |
|---|---:|
| Zonas (largura · raias) | A 11,2 m · 8 · B 14,0 m · 10 · C 11,2 m · 8 |
| Lotação | **1.997** (toda em raia) — A 614 · B 768 · C 614 |
| Meias-voltas | 23 |
| Caminhada máxima | 320 m (zona B) |
| Divisórias | 708,4 m |
| Separação da zona C | 32,0 m |
| **Separadores** | **371** — 171 a comprar, EUR 2.226,42 |
| Fita de contorno | 160,2 m |

### 5.2 Raias leste-oeste, barreira inteira

| | |
|---|---:|
| Zonas (largura · raias) | A 11,34 m · 23 · B 13,12 m · 23 · C 11,34 m · 23 |
| Lotação | **1.964** (toda em raia) — A 626 · B 712 · C 626 |
| Meias-voltas | 66 |
| **Separadores** | **371** — 171 a comprar |
| Fita de contorno | 159,6 m |

Empata com o N–S na barreira: com o contorno fora da conta, o que sobra são as
divisórias, e elas mudam `0,14 × (profundidade − largura)` por zona. O que
separa os dois é a **descarga**.

### 5.3 Raias norte-sul, CCB só na ponta + fita grossa

A divisória vira fita do tipo de isolamento, ancorada por **um CCB na ponta
livre** — no vão da meia-volta, onde a pessoa passa e a fila empurra.

| | N–S | L–O |
|---|---:|---:|
| Divisórias | 23 | 66 |
| CCB nas pontas | 46,0 m | 132,0 m |
| Separação da zona C | 32,0 m | 32,0 m |
| **Separadores** | **39** | **82** |
| A comprar | **0** | **0** |
| Fita grossa | 662,4 m | 576,4 m |
| Lotação | 1.997 | 1.964 |

**A inversão:** a barreira deixa de ser proporcional ao *comprimento* da raia e
passa a ser proporcional ao *número* de raias. Por isso o girado, com 66
divisórias curtas, passa a custar mais que o N–S com 23 longas — o contrário do
que acontecia no regime de barreira inteira.

**Ressalva que o modelo não cobra:** cada divisória do N–S fica com 28,8 m de
vão livre de fita depois do CCB da ponta. Fita não se sustenta nesse vão.
Mantendo o vão em 5 m seriam 5 apoios por divisória, **115 apoios**; se forem
CCB, o total volta a **154**. `apoios_da_fita(espacamento)` calcula para
qualquer espaçamento. **A decisão real não é entre fita e barreira — é quantos
apoios a fita vai ter.**

### 5.4 Descarga: desvio lateral entre o portão da zona e o eixo da porta

| Zona | N–S | L–O |
|---|---:|---:|
| A (S4) | 4,58 m | 4,44 m |
| B (S5) | 5,50 m | **0,00 m** |
| C (S6) | 1,58 m | 1,44 m |

É topologia de barreira, não escolha. Na **vertical** as divisórias correm
norte-sul e as meias-voltas abrem a borda norte de duas em duas raias: a fila só
sai pelo fim da última raia, num dos dois cantos — escolhe-se o mais perto da
porta. Na **horizontal** a última raia corre rente à borda norte, que é linha
contínua: o portão pode ser aberto em qualquer ponto dela, e vai para o eixo da
porta.

---

## 6. Escadas de dimensionamento

A lotação não é o que aperta: 2.000 pessoas no Ring são 17% de todo o
comparecimento esperado do dia. Encher o Ring é comprar barreira para uma fila
que provavelmente não vai existir. As escadas dizem o que dá para recuar sem
mexer no resto do desenho.

**N–S, barreira inteira — alavanca: profundidade da raia**

| Profundidade | Lotação | Separadores | A comprar |
|---:|---:|---:|---:|
| 12,00 m | 749 | 131 | 0 |
| 16,00 m | 998 | 179 | 0 |
| 20,00 m | 1.248 | 227 | 27 |
| 24,00 m | 1.498 | 275 | 75 |
| 28,00 m | 1.747 | 323 | 123 |
| 32,00 m | 1.997 | 371 | 171 |

**L–O, barreira inteira — alavanca: número de raias por zona**

| Raias/zona | Lotação | Separadores | A comprar |
|---:|---:|---:|---:|
| 6 | 503 | 85 | 0 |
| 8 | 675 | 119 | 0 |
| 10 | 847 | 152 | 0 |
| 23 | 1.964 | 371 | 171 |

---

## 7. Erros encontrados e corrigidos — não reintroduzir

Três erros de modelagem foram achados no meio do trabalho, dois deles por
pergunta do Posto. Ficam registrados porque uma sessão futura pode repeti-los.

1. **Perímetro não contado (achado pelo Posto).** A regra antiga contava, por
   zona, só as duas corridas *paralelas* às raias mais as divisórias internas.
   Faltavam os dois lados transversais. Como a orientação decidia *quais* lados
   a fórmula pegava, o erro não era simétrico e produzia uma economia
   inexistente ao girar as raias — chegou a ser reportada como "−47
   separadores". Corrigido para perímetro + divisórias; depois o perímetro saiu
   da conta por decisão (§3.4), mas a fórmula correta está no código.

2. **Descarga vertical pela boca inteira.** O serpenteado vertical não
   descarrega pela boca do bloco: as meias-voltas abrem a borda norte de duas em
   duas raias, então a fila sai pelo fim da última raia, num canto. Corrigido em
   `Zona.portao`.

3. **Aferição de barreira não comparável.** A reconstrução do plano vigente
   acerta a capacidade (855 / 547 / 1.402) com a regra atual, mas a linha de
   **barreira** — 380,8 m hoje contra 596,3 m publicados — compara regras
   diferentes e **não afere nada**. Está marcada com
   `barreira_comparavel: false` no JSON. Só as linhas de capacidade valem.

Vale registrar também dois desenhos **descartados**, para não voltarem:

- **Decks empilhados em profundidade**, com tubos de saída atravessando os decks
  da frente. Não era o que se pediu por "horizontal" e foi removido.
- **Baias de flanco**, em qualquer orientação. Eliminadas: as barreiras laterais
  são removíveis, então não é preciso reservar área para evacuação.

---

## 8. Pendências

1. **Fita delimita, não contém.** A decisão de marcar as zonas com fita vale
   enquanto a fila estiver ordenada. Num pico nada impede fisicamente a passagem
   da zona A para a B — e a separação por porta é a razão de existir da
   pré-triagem. Decidir se algum trecho volta a ser CCB, sobretudo junto às
   cabeças de fila.
2. **Quantos apoios a fita vai ter** (cenário 5.3). Pedir ao fornecedor a
   distância máxima recomendada entre apoios para o tipo de fita.
3. **A corrente que desce cruza a saída S8.** A entrada pelo canto nordeste usa
   o apron a leste, que é onde S8 despeja quem já votou. Sem raias no apron, os
   dois fluxos dividem o espaço.
4. **Largura do trecho lateral.** Os 3,0 m vêm do corredor de fundo. Cada metro
   a mais sai da largura das zonas, e no N–S tirar 1,4 m tira uma raia inteira.
5. **Onde a pré-triagem acontece.** A faixa saiu do Ring; o corredor em L é de
   passagem, não de parada. A entrega do cartão de roteamento precisa migrar
   para o percurso a montante — portão da Merrion Road, corredor da lateral
   leste do Hall.
6. **Posição lateral do Ring.** A largura é oficial; o retângulo está centrado
   no eixo de S5 por estimativa. Se o bordo oeste real estiver deslocado, as
   zonas andam junto e as diagonais de descarga mudam; o número de raias não.
7. **Vão dos portões (1,40 m).** É premissa, não medida. Se o procedimento pedir
   vão maior (cadeirante, maca, carrinho), cada metro a mais reduz barreira.
8. **Densidades reconstruídas.** 2,0 pessoas/m² em raia e 1,8 em baia. Se a
   densidade real sob guarda-chuva for menor, todos os cenários perdem lotação
   na mesma proporção e a comparação entre eles não muda.
9. **`scripts/salao.py`, `scripts/layout_ring3.py` e `saidas/plano_ring3.md` não
   estão no repositório.** Foram produzidos em sessão anterior e nunca
   versionados. A geometria do salão e das portas está replicada dentro de
   `scripts/ring3.py`; o plano vigente foi reconstruído das cotas publicadas na
   página "Rota do Eleitor".

---

## 9. Onde está o quê

| Arquivo | Conteúdo |
|---|---|
| `scripts/ring3.py` | Geometria, modelo de fila, escadas, plantas e mapas em SVG |
| `scripts/gera_pagina_ring3.py` | A página, montada a partir do JSON |
| `saidas/ring3.json` | Todos os números, por cenário — fonte para qualquer outra saída |
| `saidas/plano_ring3_horizontal.md` | O plano em texto |
| `saidas/ring3_horizontal.html` | A página publicada |
| `saidas/ring3_vertical_sem_baias.svg` · `ring3_girado.svg` | Plantas dos cenários 5.1 e 5.2 |
| `saidas/ring3_vertical_ponta.svg` · `ring3_girado_ponta.svg` | Plantas do cenário 5.3 |
| `saidas/ring3_barreiras_*.svg` | Mapas dos separadores, um por cenário |

```bash
python3 scripts/ring3.py              # plano, JSON e as plantas
python3 scripts/gera_pagina_ring3.py  # a página
```

- Página publicada: <https://claude.ai/code/artifact/c1257b13-e450-4bc1-b801-439a32bddb87>
- Pull request: <https://github.com/hamadmkalaf/eleicoes2026/pull/13>
- Contexto geral do pleito em Dublin: `contexto_eleicoes_dublin_2026.md`
- Agregação de seções e mesas: `README.md`, `saidas/dados.json`

---

## 10. Resumo para quem só quer o número

Para o desenho **norte-sul, corredor em L, fita no contorno**:

- **371 separadores** se cada divisória for barreira inteira — 171 a comprar.
- **39 separadores** se a divisória for fita grossa com um CCB na ponta —
  nenhum a comprar, mas **115 apoios de fita** entram no lugar.
- **Lotação de 1.997 pessoas**, toda em fila medida, nos dois casos.
- **160,2 m de fita** para o contorno das zonas, em qualquer dos dois.
