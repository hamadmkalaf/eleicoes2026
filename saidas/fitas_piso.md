# Fitas no piso em vez do checkpoint: o que o simulador diz

Arranjo **Três polos · 22/23/24 separadas**, entradas S4/S5/S6 e saídas S2/S8 da decisão de 06/09, base B (11.499 esperados), identificação de 45 s e voto de 30 s salvo onde indicado, 8 dias simulados por cenário. Motor: `simulador/modelo.js`, o mesmo do simulador publicado; varredura em `simulador/fitas.js`.

## Resultados por cenário

Espera P90 = tempo da chegada ao Ring 3 até o voto para nove em dez eleitores (fora + dentro). "Chegadas a fila cheia" = eleitores que chegaram à mesa com a fila já além do comprimento previsto (sem checkpoint ninguém os retém). "Fome" = minutos em que uma mesa vermelha ficou ociosa com gente esperando fora.

### referência

| Cenário | Fecha (p50 / p90) | Espera P90 | fora / dentro | Pico dentro | Pico Ring 3 | Fome vermelhas | Chegadas a fila cheia | Perdidos | Fita | Veredito |
|---|---|---|---|---|---|---|---|---|---|---|
| Cenário Claude: checkpoint a 16 m, 3/3/3, liberação por buffer | 17h03 / 17h03 | 49 min | 33 / 20 | 321 | 962 | 4 min | 0 | 0 | 157 m | **atencao**: espera do eleitor (p90) (atencao) |

### fitas

| Cenário | Fecha (p50 / p90) | Espera P90 | fora / dentro | Pico dentro | Pico Ring 3 | Fome vermelhas | Chegadas a fila cheia | Perdidos | Fita | Veredito |
|---|---|---|---|---|---|---|---|---|---|---|
| Fitas, sem checkpoint, porta libera enquanto cabe na zona (buffer = soma das filas) | 17h03 / 17h03 | 68 min | 63 / 7 | 121 | 1.516 | 10 min | 2.216 | 0 | 61 m | **falha**: espera do eleitor (p90) (atencao); filas das mesas sem checkpoint (falha); ring 3 comporta a fila externa (atencao) |
| Fitas, sem checkpoint, porta livre (sem contenção) | 17h03 / 17h03 | 50 min | 5 / 44 | 950 | 962 | 4 min | 5.795 | 0 | 61 m | **falha**: espera do eleitor (p90) (atencao); filas das mesas sem checkpoint (falha) |
| Fitas, sem checkpoint, porta só libera quem tem vaga na sua mesa | 17h28 / 17h34 | 103 min | 100 / 3 | 110 | 2.283 | 123 min | 0 | 0 | 61 m | **falha**: última mesa fecha (atencao); mesas vermelhas sem fome (falha); espera do eleitor (p90) (falha); ring 3 comporta a fila externa (falha) |
| Fitas, sem checkpoint, buffer, filas de mesa 5/8/12 | 17h03 / 17h04 | 52 min | 42 / 17 | 206 | 1.001 | 4 min | 2.188 | 0 | 111 m | **falha**: espera do eleitor (p90) (atencao); filas das mesas sem checkpoint (falha); filas cabem no espaço (falha); ring 3 comporta a fila externa (atencao) |
| Fitas, sem checkpoint, porta livre, filas de mesa 5/8/12 | 17h03 / 17h03 | 50 min | 5 / 44 | 950 | 962 | 4 min | 5.392 | 0 | 111 m | **falha**: espera do eleitor (p90) (atencao); filas das mesas sem checkpoint (falha); filas cabem no espaço (falha) |

### sinalização

| Cenário | Fecha (p50 / p90) | Espera P90 | fora / dentro | Pico dentro | Pico Ring 3 | Fome vermelhas | Chegadas a fila cheia | Perdidos | Fita | Veredito |
|---|---|---|---|---|---|---|---|---|---|---|
| Fitas, buffer, 10 % se perdem e andam 30 m a mais | 17h03 / 17h03 | 65 min | 61 / 7 | 121 | 1.491 | 9 min | 2.130 | 1.214 | 61 m | **falha**: espera do eleitor (p90) (atencao); filas das mesas sem checkpoint (falha); ring 3 comporta a fila externa (falha) |
| Fitas, buffer, 25 % se perdem e andam 40 m a mais | 17h03 / 17h03 | 66 min | 61 / 6 | 121 | 1.530 | 11 min | 2.077 | 3.038 | 61 m | **falha**: espera do eleitor (p90) (atencao); filas das mesas sem checkpoint (falha); ring 3 comporta a fila externa (falha) |
| Fitas, porta livre, 25 % se perdem e andam 40 m a mais | 17h03 / 17h04 | 49 min | 5 / 42 | 954 | 962 | 4 min | 5.773 | 3.005 | 61 m | **falha**: espera do eleitor (p90) (atencao); filas das mesas sem checkpoint (falha) |

### identificação 60 s

| Cenário | Fecha (p50 / p90) | Espera P90 | fora / dentro | Pico dentro | Pico Ring 3 | Fome vermelhas | Chegadas a fila cheia | Perdidos | Fita | Veredito |
|---|---|---|---|---|---|---|---|---|---|---|
| Checkpoint, identificação 60 s | 18h53 / 18h55 | 112 min | 97 / 40 | 315 | 2.036 | 3 min | 0 | 0 | 157 m | **falha**: última mesa fecha (falha); espera do eleitor (p90) (falha); ring 3 comporta a fila externa (falha) |
| Fitas, buffer, identificação 60 s | 18h59 / 19h07 | 147 min | 141 / 11 | 118 | 2.724 | 9 min | 2.828 | 0 | 61 m | **falha**: última mesa fecha (falha); espera do eleitor (p90) (falha); filas das mesas sem checkpoint (falha); ring 3 comporta a fila externa (falha) |
| Fitas, porta livre, identificação 60 s | 18h50 / 18h53 | 108 min | 5 / 107 | 1.401 | 962 | 3 min | 8.800 | 0 | 61 m | **falha**: última mesa fecha (falha); espera do eleitor (p90) (falha); filas das mesas sem checkpoint (falha) |

### comparecimento +15 %

| Cenário | Fecha (p50 / p90) | Espera P90 | fora / dentro | Pico dentro | Pico Ring 3 | Fome vermelhas | Chegadas a fila cheia | Perdidos | Fita | Veredito |
|---|---|---|---|---|---|---|---|---|---|---|
| Checkpoint, comparecimento grande | 17h37 / 17h44 | 82 min | 68 / 32 | 317 | 1.852 | 4 min | 0 | 0 | 157 m | **falha**: última mesa fecha (atencao); espera do eleitor (p90) (atencao); ring 3 comporta a fila externa (falha) |
| Fitas, buffer, comparecimento grande | 17h46 / 17h50 | 112 min | 107 / 8 | 121 | 2.619 | 12 min | 3.076 | 0 | 61 m | **falha**: última mesa fecha (atencao); espera do eleitor (p90) (falha); filas das mesas sem checkpoint (falha); ring 3 comporta a fila externa (falha) |

### atribuição geográfica

| Cenário | Fecha (p50 / p90) | Espera P90 | fora / dentro | Pico dentro | Pico Ring 3 | Fome vermelhas | Chegadas a fila cheia | Perdidos | Fita | Veredito |
|---|---|---|---|---|---|---|---|---|---|---|
| Checkpoint, mesas atribuídas por parede (oeste A, norte B, leste C) | 17h03 / 17h03 | 50 min | 39 / 21 | 315 | 971 | 6 min | 0 | 0 | 157 m | **falha**: espera do eleitor (p90) (atencao); portas equilibradas (falha); ring 3 comporta a fila externa (falha) |
| Fitas, buffer, mesas atribuídas por parede | 17h03 / 17h03 | 70 min | 65 / 7 | 120 | 1.551 | 10 min | 2.264 | 0 | 61 m | **falha**: espera do eleitor (p90) (atencao); filas das mesas sem checkpoint (falha); portas equilibradas (falha); ring 3 comporta a fila externa (falha) |
| Fitas, porta livre, mesas atribuídas por parede | 17h03 / 17h04 | 48 min | 9 / 42 | 868 | 962 | 6 min | 5.785 | 0 | 61 m | **falha**: espera do eleitor (p90) (atencao); filas das mesas sem checkpoint (falha); portas equilibradas (falha); ring 3 comporta a fila externa (atencao) |

## Geometria das fitas sobre o arranjo

Fita por mesa = uma reta da soleira da porta à ponta da fila de cada mesa (a sugestão literal). Troncos = uma fita por parede servida por cada entrada, correndo rente à parede e passando pela ponta da fila de cada mesa. Cruzamentos contam pares de fitas de entradas diferentes que se cortam no piso; fita × saída conta fitas cortadas pelo trajeto de quem sai.

| Atribuição mesa → entrada | Fita por mesa | Troncos | Cruzamentos entre entradas (por mesa / troncos) | Fita × saída | Porta mais carregada ÷ menos |
|---|---|---|---|---|---|
| atribuição da decisão (por quota do Ring 3) | 906 m | 463 m | 103 / 18 | 102 | 1.16× |
| atribuição por parede (oeste A, norte B, leste C) | 860 m | 214 m | 6 / 1 | 102 | 3.36× |

**atribuição da decisão (por quota do Ring 3)**

| Entrada | Porta | Mesas (MRV) | Esperados | Cabe no Ring 3 | Paredes servidas | Troncos | Caminho médio porta → fila |
|---|---|---|---|---|---|---|---|
| A | S4 | 3, 5, 9, 12, 15, 20, 24, 26, 28 | 3.642 | 445 | norte / leste / oeste | 3 (149 m) | 32.7 m |
| B | S5 | 1, 4, 7, 8, 16, 17, 18, 21, 22, 25 | 4.215 | 513 | norte / leste / recorte / oeste | 4 (167 m) | 31.2 m |
| C | S6 | 2, 6, 10, 11, 13, 14, 19, 23, 27 | 3.642 | 445 | norte / leste / oeste | 3 (146 m) | 30.0 m |

**atribuição por parede (oeste A, norte B, leste C)**

| Entrada | Porta | Mesas (MRV) | Esperados | Cabe no Ring 3 | Paredes servidas | Troncos | Caminho médio porta → fila |
|---|---|---|---|---|---|---|---|
| A | S4 | 24, 25, 26, 27, 28 | 1.771 | 445 | oeste | 1 (41 m) | 29.0 m |
| B | S5 | 1, 2, 3, 4, 5, 6, 7, 8, 21, 22 | 3.777 | 513 | norte / recorte | 2 (128 m) | 38.6 m |
| C | S6 | 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 23 | 5.951 | 445 | leste | 1 (46 m) | 24.2 m |

