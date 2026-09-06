# Ring 3 — desenho horizontal

Segunda geometria para o compound de fila ao ar livre do RDS (Ring 3, 39,0 × 35,0 m, 14 m ao sul da fachada do Hall 2). O plano vigente enfileira as pessoas em **serpenteados verticais** — raias norte-sul, três blocos lado a lado. Este documento desenha a alternativa **horizontal** — raias leste-oeste, três decks empilhados em profundidade — e refaz, com o mesmo modelo, as duas contas que mudam: **capacidade** e **separadores de fila**.

## Resultado em uma linha

O horizontal cabe no mesmo Ring e entrega **1.503 pessoas** contra 1.402 do vertical, mas custa **369 separadores** contra 312 — 0,490 m de barreira por pessoa contra 0,445 m. Como a capacidade não é o que aperta em nenhum dos dois, a versão enxuta abaixo (4/5/4 raias, 1.086 pessoas) resolve com **292 separadores**, abaixo dos 312 do vertical. O que o horizontal compra de verdade não é capacidade: é a descarga perpendicular, uma raia por porta, e o apron limpo em frente às duas saídas.

## Por que o desenho é este

Empilhar decks em profundidade cria um problema que o vertical não tem: o deck do fundo precisa atravessar os decks da frente para chegar à fachada. A solução que organiza tudo o resto é **alinhar cada saída com a sua porta e fazer os decks da frente pararem antes desse eixo**. Daí a escada: quanto mais ao fundo, mais largo o deck; o degrau que sobra a leste vira baia de espera; e a ordem dos decks fica imposta pela geometria — da frente para o fundo, a porta tem de andar para leste: **A = S4, B = S5, C = S6**.

Quatro consequências práticas:

- Cada deck sai por um portão dentro do vão da sua própria porta e cruza o apron em linha reta: as três correntes nunca se aproximam, e o apron fica livre a oeste de x = 19,1 m e a leste de x = 37,5 m, que é onde desembocam as saídas S2 e S8.
- As baias ficam do lado da chegada, encostadas na espinha, e não ao lado do meio da fila: enchem como buffer de cauda, antes das raias, e não como transbordo lateral.
- O preço da geometria é o tubo: cada deck de trás gasta duas corridas de barreira só para atravessar a profundidade dos decks da frente.
- A ordem dos decks é imposta, não escolhida: da frente para o fundo, a porta de cada deck tem de andar para leste (A=S4, B=S5, C=S6), senão o tubo de um deck de trás cortaria o serpenteado da frente.

E o que o vertical tem contra si, medido no mesmo desenho:

- Descarga em diagonal: nenhum dos três blocos está alinhado com a sua porta, então as três correntes cruzam o apron obliquamente e se aproximam entre si até os 6,2 m que separam as portas na fachada.
- As baias de flanco caem em frente às portas de saída S2 (oeste) e S8 (leste): a área de espera fica no caminho de quem já votou.

## Premissas do modelo

| Parâmetro | Valor | Origem |
|---|---|---|
| Módulo da raia | 1,40 m | reconstruído (4,2 / 12,6 m dos blocos do plano vertical = 3 e 9 raias) |
| Largura livre da raia | 1,20 m | reconstruído |
| Densidade em raia | 2,0 pessoas/m² | reconstruído |
| Densidade em baia | 1,8 pessoas/m² | reconstruído |
| Vão de meia-volta | 1,2 m | premissa |
| Separador de fila | 2,0 m/unidade · EUR 13,02 | item d do orçamento (100 un. = EUR 1.303) |
| Estoque da organizadora | 200 unidades (400 m) | plano vertical |
| Comparecimento esperado | A 3.642 · B 4.215 · C 3.642 | decisões do Posto, base B de 2022 |

**Aderência ao plano original.** As quatro densidades acima não estão escritas em lugar nenhum — `scripts/layout_ring3.py` e `saidas/plano_ring3.md` foram produzidos em sessão anterior e não chegaram a ser versionados. Foram reconstruídas por ajuste aos números publicados, e reproduzem-nos exatamente:

| Grandeza | Publicado | Recalculado aqui |
|---|---|---|
| Capacidade dos serpenteados | 855 | 855,0 |
| Capacidade das baias | 547 | 547,2 |
| Capacidade total | 1.402 | 1.402 |
| Barreira | 596,3 m | 623,3 m |
| Separadores | 300 | 312 |

A capacidade fecha na casa decimal; a barreira fica 4,5% acima, porque a regra de contagem de barreira do plano original não é recuperável a partir do que foi publicado. **A comparação abaixo usa a regra deste script nos dois desenhos** — é a única forma de ela valer alguma coisa.

## Capacidade

| | Vertical | Horizontal | Δ |
|---|---:|---:|---:|
| Em raia (fila medida) | 855 | 1.140 | +285 |
| Em baia (espera) | 547 | 362 | −185 |
| **Total** | **1.402** | **1.503** | **+101** |

| Entrada | Esperado | Vertical | por eleitor | Horizontal | por eleitor |
|---|---:|---:|---:|---:|---:|
| A (S4) | 3.642 | 445 | 0,1221 | 482 | 0,1325 |
| B (S5) | 4.215 | 513 | 0,1217 | 502 | 0,1191 |
| C (S6) | 3.642 | 445 | 0,1221 | 518 | 0,1423 |

O horizontal muda a natureza da capacidade, não só o total: no vertical 61% da lotação está em raia e o resto é massa parada nas baias de flanco; no horizontal a raia sobe para 76%. Fila em raia é fila contável, com ordem de chegada preservada e vazão previsível; baia é aglomeração que precisa de fiscal para virar fila outra vez.

## Separadores de fila

Barreira externa, componente a componente. Não entra aqui o gradil permanente do Ring, que os dois desenhos usam de graça, nem os 100 unifilas (200 m) do item d do orçamento, que servem ao interior do Hall 2.

| Componente | Vertical (m) | Horizontal (m) |
|---|---:|---:|
| serpenteados | 413,1 | 536,4 |
| corredor de distribuição (2 lados) | 73,4 | 0,0 |
| fechamento das baias de flanco | 25,6 | 0,0 |
| raias do apron até as portas | 87,2 | 84,0 |
| funil da garganta sudeste | 24,0 | 24,0 |
| espinha de distribuição (gradil a leste) | 0,0 | 25,2 |
| tubos de saída dos decks de trás | 0,0 | 50,4 |
| fechamento das baias | 0,0 | 16,8 |
| **Total** | **623,3** | **736,8** |
| **Separadores (2 m)** | **312** | **369** |
| A comprar (estoque 200) | 112 | 169 |
| Custo da compra | EUR 1.458,24 | EUR 2.200,38 |

Na versão cheia, o horizontal pede 57 separadores a mais que o vertical, e a razão é única e identificável: os **tubos**. Cada deck de trás gasta duas corridas de barreira só para atravessar a profundidade dos decks da frente — 50,4 m que o vertical não gasta. Os serpenteados propriamente ditos são levemente mais eficientes no horizontal, porque a raia longa dilui o custo das pontas.

## Escada de dimensionamento

O número de raias por deck é a única alavanca: com os decks na largura máxima, ela troca capacidade por barreira quase linearmente. A linha marcada é a recomendada.

| Raias A/B/C | Capacidade | A | B | C | Separadores | A comprar | Custo |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2/2/2 | 501 | 161 | 167 | 173 | 187 | 0 | EUR 0,00 |
| 2/3/2 | 585 | 161 | 251 | 173 | 201 | 1 | EUR 13,02 |
| 3/3/2 | 665 | 241 | 251 | 173 | 214 | 14 | EUR 182,28 |
| 3/3/3 | 751 | 241 | 251 | 259 | 232 | 32 | EUR 416,64 |
| 3/4/3 | 835 | 241 | 335 | 259 | 247 | 47 | EUR 611,94 |
| 4/4/3 | 916 | 322 | 335 | 259 | 260 | 60 | EUR 781,20 |
| 4/4/4 | 1.002 | 322 | 335 | 346 | 278 | 78 | EUR 1.015,56 |
| 4/5/4 ← | 1.086 | 322 | 418 | 346 | 292 | 92 | EUR 1.197,84 |
| 5/5/4 | 1.166 | 402 | 418 | 346 | 305 | 105 | EUR 1.367,10 |
| 5/5/5 | 1.252 | 402 | 418 | 432 | 323 | 123 | EUR 1.601,46 |
| 5/6/5 | 1.336 | 402 | 502 | 432 | 338 | 138 | EUR 1.796,76 |
| 6/6/5 | 1.417 | 482 | 502 | 432 | 351 | 151 | EUR 1.966,02 |
| 6/6/6 ←← | 1.503 | 482 | 502 | 518 | 369 | 169 | EUR 2.200,38 |

`←` recomendada · `←←` Ring cheio

## Recomendação

**4/5/4 raias**: 1.086 pessoas com 292 separadores (92 a comprar, EUR 1.197,84). Fica 20 separadores abaixo do plano vertical e ainda sustenta uma lotação muito acima de qualquer pico plausível — o Ring nunca foi o gargalo desta operação, e gastar barreira para enchê-lo é comprar capacidade que não vai ser usada. Se o Posto preferir margem, a linha `←←` enche o Ring.

## Pendências de campo

1. **Bordo oeste do Ring.** O retângulo está centrado em S5 por estimativa; medir no local decide a largura real dos decks e, com ela, a capacidade de cada um.

2. **Aberturas do gradil.** O desenho supõe que dá para abrir portão no gradil permanente do Ring nos três eixos de porta (x ≈ 22,1 / 28,3 / 34,5 m) e na garganta sudeste. Se o gradil não abrir onde se precisa, os tubos deixam de ser retos e a vantagem principal do desenho cai.

3. **Piso e drenagem.** Raia leste-oeste de 36 m acompanha a declividade do Ring por inteiro; verificar se algum trecho acumula água, o que inviabilizaria as raias do fundo num dia de chuva (40% a 65% de probabilidade em 4 de outubro, conforme o limiar).

4. **Confirmar a densidade adotada.** 2,0 pessoas/m² em raia e 1,8 em baia são reconstrução, não medição. Se a densidade real sob guarda-chuva for menor, as duas geometrias perdem capacidade na mesma proporção e a comparação não muda.

