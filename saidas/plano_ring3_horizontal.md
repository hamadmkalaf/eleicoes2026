# Ring 3 — serpentinas giradas para leste-oeste

O plano vigente da fila externa (Ring 3, 39,0 × 35,0 m, 14 m ao sul da fachada) tem três zonas lado a lado — A, B e C —, alimentadas por um **corredor de fundo** ao sul e descarregando ao norte nas portas S4, S5 e S6. Dentro de cada zona, as raias correm norte-sul. Este documento mede o que muda quando, **nas mesmas zonas**, as raias passam a correr leste-oeste, empilhadas em altura. Corredor, zonas, baias de flanco, garganta e portas ficam exatamente onde estão: só a dobra da fila gira 90°.

## A resposta

**265 separadores contra 312** — 47 a menos, 15% de economia — com a lotação praticamente igual (1.389 contra 1.402 pessoas). Sobre o estoque de 200 unidades da organizadora, a compra cai de 112 para 65 unidades: EUR 846,30 no lugar de EUR 1.458,24.

| | Vigente (raias N–S) | Girado (raias L–O) | Δ |
|---|---:|---:|---:|
| Barreira | 623,3 m | 528,4 m | −94,9 m |
| Separadores de 2 m | 312 | 265 | −47 |
| A comprar (estoque 200) | 112 | 65 | −47 |
| Custo da compra | EUR 1.458,24 | EUR 846,30 | EUR −611,94 |
| Capacidade | 1.402 | 1.389 | −13 |
| Metros de barreira por pessoa | 0,445 | 0,380 | −0,064 |

## De onde vem a economia

A barreira de um serpenteado é `(n+1) × comprimento da raia − 1,2 × (n−1)`: são n+1 corridas longitudinais, e cada divisória interna para 1,2 m antes da ponta para abrir a meia-volta. Girar as raias mantém a área — e, portanto, a fila — mas **troca raias longas por raias curtas e numerosas**. Como o número de raias multiplica o desconto da meia-volta e divide o comprimento, o total cai.

| Zona | Vigente | Girado | Barreira vigente | Barreira girada | Δ |
|---|---|---|---:|---:|---:|
| A (S4) | 3 raias de 23,8 m | 17 raias de 4,2 m | 92,6 m | 56,4 m | −36,2 m |
| B (S5) | 9 raias de 23,8 m | 17 raias de 12,6 m | 227,9 m | 207,6 m | −20,3 m |
| C (S6) | 3 raias de 23,8 m | 17 raias de 4,2 m | 92,6 m | 56,4 m | −36,2 m |
| **Total** | | | **413,1 m** | **320,4 m** | **−92,7 m** |

O resto do plano — corredor de fundo, fechamento das baias, funil da garganta — não muda. As raias do apron encurtam de leve, e por um motivo que vale registrar: com as raias na horizontal, **a última raia corre rente à borda norte da zona**, então o portão de saída pode ficar em qualquer ponto dessa borda. Na zona B, o eixo de S5 cai dentro do bloco, e a descarga fica perpendicular — desvio lateral zero, contra 0,1 m no desenho vigente.

| Zona | Desvio lateral vigente | Desvio girado |
|---|---:|---:|
| A | 4,81 m | 2,71 m |
| B | 0,11 m | 0,00 m |
| C | 4,79 m | 2,69 m |

## O que a rotação custa

**Meias-voltas: 48 contra 12.** Nas zonas A e C, de 4,2 m de largura, a raia girada tem 4,2 m e o eleitor dá 16 curvas até sair. É um ziguezague, não uma fila. Na zona B, de 12,6 m, a raia girada continua confortável.

O modelo de capacidade acima não cobra nada pela curva. Se cada meia-volta custar 0,6 m de fila aproveitável — premissa, não medição —, a conta fica:

| | Vigente | Girado |
|---|---:|---:|
| Capacidade nominal | 1.402 | 1.389 |
| Descontadas as meias-voltas | 1.385 | 1.320 |

Ou seja: a economia de barreira é robusta, a paridade de capacidade não. Sob a premissa da curva, o girado perde cerca de 65 pessoas para o vigente — ainda dentro do que a operação suporta, mas não é empate.

## Variante: raias longas, sem baias

Se o ziguezague de A e C incomodar, a saída é alargar as três zonas até a largura do Ring, o que consome as baias de flanco:

| | Vigente | Girado | Raias longas |
|---|---:|---:|---:|
| Raia mais curta | 23,8 m | 4,2 m | 10,7 m |
| Capacidade | 1.402 | 1.389 | 1.364 |
| … em raia medida | 855 | 842 | 1.364 |
| Separadores | 312 | 265 | 367 |
| A comprar | 112 | 65 | 167 |

Toda a lotação vira fila medida, e o preço aparece na barreira: a capacidade que o plano vigente ganha de graça nas baias — que usam o gradil do Ring em três lados — passa a ser paga em divisória.

## Premissas e aderência ao plano original

| Parâmetro | Valor | Origem |
|---|---|---|
| Módulo da raia | 1,40 m | reconstruído dos blocos de 4,2 e 12,6 m |
| Largura livre da raia | 1,20 m | reconstruído |
| Densidade em raia | 2,0 pessoas/m² | reconstruído |
| Densidade em baia | 1,8 pessoas/m² | reconstruído |
| Vão de meia-volta | 1,2 m | premissa |
| Separador | 2,0 m · EUR 13,02 | item d do orçamento (100 un. = EUR 1.303) |
| Estoque da organizadora | 200 un. | plano do Ring 3 |

`scripts/layout_ring3.py` e `saidas/plano_ring3.md` foram produzidos em sessão anterior e não chegaram a este repositório; o plano vigente foi reconstruído das cotas publicadas e reproduz os números publicados:

| Grandeza | Publicado | Recalculado |
|---|---:|---:|
| Serpenteados | 855 | 855,0 |
| Baias | 547 | 547,2 |
| Total | 1.402 | 1.402 |
| Barreira | 596,3 m | 623,3 m |
| Separadores | 300 | 312 |

A capacidade fecha; a barreira fica 4,5% acima, porque a regra de contagem do plano original não é recuperável do que foi publicado. **A comparação usa a regra deste script nos dois desenhos** — a diferença de −47 separadores é entre geometrias, não entre métodos. Aplicada aos 300 separadores publicados, a mesma redução de 15% daria cerca de 255 unidades.

## Pendências de campo

1. **Largura real das zonas.** O retângulo do Ring está centrado em S5 por estimativa; medir no local muda o comprimento das raias giradas — que, nesta geometria, é a largura da zona.

2. **Onde o gradil abre.** A descarga perpendicular da zona B supõe portão no eixo de S5 (x ≈ 28,3 m).

3. **Ziguezague de A e C.** Antes de fechar, decidir se 4,2 m de raia com 16 curvas é aceitável para o público do posto — inclusive idosos, cadeirantes e carrinhos de bebê — ou se a variante de raias longas compensa a barreira a mais.

