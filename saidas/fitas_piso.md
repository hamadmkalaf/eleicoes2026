# Fitas no piso em vez do checkpoint: o que o simulador diz

Arranjo **Hamad_Final**, entradas S4/S5/S6 e saídas S2/S8 da decisão de 06/09, base B (11.499 esperados), identificação de 45 s e voto de 30 s salvo onde indicado, 8 dias simulados por cenário. Motor: `simulador/modelo.js`, o mesmo do simulador publicado; varredura em `simulador/fitas.js`.

## Resultados por cenário

Espera P90 = tempo da chegada ao Ring 3 até o voto para nove em dez eleitores (fora + dentro). "Chegadas a fila cheia" = eleitores que chegaram à mesa com a fila já além do comprimento previsto (sem checkpoint ninguém os retém). "Fome" = minutos em que uma mesa vermelha ficou ociosa com gente esperando fora.

### referência

| Cenário | Fecha (p50 / p90) | Espera P90 | fora / dentro | Pico dentro | Pico Ring 3 | Fome vermelhas | Chegadas a fila cheia | Perdidos | Fita | Veredito |
|---|---|---|---|---|---|---|---|---|---|---|
| Cenário Claude: checkpoint a 16 m, 3/3/3, liberação por buffer | 17h03 / 17h03 | 50 min | 35 / 21 | 316 | 971 | 5 min | 0 | 0 | 157 m | **atencao**: espera do eleitor (p90) (atencao) |

### fitas

| Cenário | Fecha (p50 / p90) | Espera P90 | fora / dentro | Pico dentro | Pico Ring 3 | Fome vermelhas | Chegadas a fila cheia | Perdidos | Fita | Veredito |
|---|---|---|---|---|---|---|---|---|---|---|
| Fitas, sem checkpoint, porta libera enquanto cabe na zona (buffer = soma das filas) | 17h03 / 17h03 | 65 min | 61 / 7 | 122 | 1.429 | 10 min | 2.190 | 0 | 61 m | **falha**: espera do eleitor (p90) (atencao); filas das mesas sem checkpoint (falha); ring 3 comporta a fila externa (falha) |
| Fitas, sem checkpoint, porta livre (sem contenção) | 17h03 / 17h04 | 49 min | 5 / 43 | 951 | 962 | 6 min | 5.809 | 0 | 61 m | **falha**: espera do eleitor (p90) (atencao); filas das mesas sem checkpoint (falha) |
| Fitas, sem checkpoint, porta só libera quem tem vaga na sua mesa | 17h34 / 17h36 | 102 min | 99 / 3 | 113 | 2.155 | 119 min | 0 | 0 | 61 m | **falha**: última mesa fecha (atencao); mesas vermelhas sem fome (falha); espera do eleitor (p90) (falha); ring 3 comporta a fila externa (falha) |
| Fitas, sem checkpoint, buffer, filas de mesa 5/8/12 | 17h03 / 17h04 | 51 min | 40 / 16 | 206 | 995 | 5 min | 2.234 | 0 | 111 m | **falha**: espera do eleitor (p90) (atencao); filas das mesas sem checkpoint (falha); ring 3 comporta a fila externa (atencao) |
| Fitas, sem checkpoint, porta livre, filas de mesa 5/8/12 | 17h03 / 17h04 | 49 min | 5 / 43 | 951 | 962 | 6 min | 5.379 | 0 | 111 m | **falha**: espera do eleitor (p90) (atencao); filas das mesas sem checkpoint (falha) |

### sinalização

| Cenário | Fecha (p50 / p90) | Espera P90 | fora / dentro | Pico dentro | Pico Ring 3 | Fome vermelhas | Chegadas a fila cheia | Perdidos | Fita | Veredito |
|---|---|---|---|---|---|---|---|---|---|---|
| Fitas, buffer, 10 % se perdem e andam 30 m a mais | 17h03 / 17h03 | 67 min | 62 / 6 | 121 | 1.474 | 11 min | 2.121 | 1.230 | 61 m | **falha**: espera do eleitor (p90) (atencao); filas das mesas sem checkpoint (falha); ring 3 comporta a fila externa (falha) |
| Fitas, buffer, 25 % se perdem e andam 40 m a mais | 17h03 / 17h04 | 68 min | 64 / 7 | 121 | 1.548 | 14 min | 2.092 | 3.017 | 61 m | **falha**: espera do eleitor (p90) (atencao); filas das mesas sem checkpoint (falha); ring 3 comporta a fila externa (falha) |
| Fitas, porta livre, 25 % se perdem e andam 40 m a mais | 17h03 / 17h04 | 50 min | 5 / 44 | 942 | 962 | 5 min | 5.749 | 3.047 | 61 m | **falha**: espera do eleitor (p90) (atencao); filas das mesas sem checkpoint (falha) |

### identificação 60 s

| Cenário | Fecha (p50 / p90) | Espera P90 | fora / dentro | Pico dentro | Pico Ring 3 | Fome vermelhas | Chegadas a fila cheia | Perdidos | Fita | Veredito |
|---|---|---|---|---|---|---|---|---|---|---|
| Checkpoint, identificação 60 s | 18h54 / 18h58 | 114 min | 99 / 43 | 314 | 2.059 | 3 min | 0 | 0 | 157 m | **falha**: última mesa fecha (falha); espera do eleitor (p90) (falha); ring 3 comporta a fila externa (falha) |
| Fitas, buffer, identificação 60 s | 19h00 / 19h04 | 149 min | 144 / 11 | 118 | 2.719 | 8 min | 2.820 | 0 | 61 m | **falha**: última mesa fecha (falha); espera do eleitor (p90) (falha); filas das mesas sem checkpoint (falha); ring 3 comporta a fila externa (falha) |
| Fitas, porta livre, identificação 60 s | 18h48 / 18h54 | 105 min | 5 / 104 | 1.401 | 962 | 3 min | 8.957 | 0 | 61 m | **falha**: última mesa fecha (falha); espera do eleitor (p90) (falha); filas das mesas sem checkpoint (falha) |

### comparecimento +15 %

| Cenário | Fecha (p50 / p90) | Espera P90 | fora / dentro | Pico dentro | Pico Ring 3 | Fome vermelhas | Chegadas a fila cheia | Perdidos | Fita | Veredito |
|---|---|---|---|---|---|---|---|---|---|---|
| Checkpoint, comparecimento grande | 17h37 / 17h47 | 86 min | 73 / 33 | 316 | 1.883 | 4 min | 0 | 0 | 157 m | **falha**: última mesa fecha (atencao); espera do eleitor (p90) (atencao); ring 3 comporta a fila externa (falha) |
| Fitas, buffer, comparecimento grande | 17h43 / 17h59 | 113 min | 108 / 8 | 121 | 2.588 | 14 min | 3.025 | 0 | 61 m | **falha**: última mesa fecha (atencao); espera do eleitor (p90) (falha); filas das mesas sem checkpoint (falha); ring 3 comporta a fila externa (falha) |

### atribuição geográfica

| Cenário | Fecha (p50 / p90) | Espera P90 | fora / dentro | Pico dentro | Pico Ring 3 | Fome vermelhas | Chegadas a fila cheia | Perdidos | Fita | Veredito |
|---|---|---|---|---|---|---|---|---|---|---|
| Checkpoint, mesas atribuídas por parede (oeste A, norte B, leste C) | 17h03 / 17h03 | 49 min | 34 / 21 | 320 | 962 | 6 min | 0 | 0 | 157 m | **atencao**: espera do eleitor (p90) (atencao) |
| Fitas, buffer, mesas atribuídas por parede | 17h03 / 17h03 | 68 min | 63 / 7 | 121 | 1.508 | 14 min | 2.139 | 0 | 61 m | **falha**: espera do eleitor (p90) (atencao); filas das mesas sem checkpoint (falha); ring 3 comporta a fila externa (falha) |
| Fitas, porta livre, mesas atribuídas por parede | 17h03 / 17h03 | 50 min | 5 / 43 | 952 | 962 | 6 min | 5.767 | 0 | 61 m | **falha**: espera do eleitor (p90) (atencao); filas das mesas sem checkpoint (falha) |

## Geometria das fitas sobre o arranjo

Fita por mesa = uma reta da soleira da porta à ponta da fila de cada mesa (a sugestão literal). Troncos = uma fita por parede servida por cada entrada, correndo rente à parede e passando pela ponta da fila de cada mesa. Cruzamentos contam pares de fitas de entradas diferentes que se cortam no piso; fita × saída conta fitas cortadas pelo trajeto de quem sai.

| Atribuição mesa → entrada | Fita por mesa | Troncos | Cruzamentos entre entradas (por mesa / troncos) | Fita × saída | Porta mais carregada ÷ menos |
|---|---|---|---|---|---|
| atribuição da decisão (por quota do Ring 3) | 888 m | 462 m | 109 / 23 | 133 | 1.16× |
| atribuição por parede (oeste A, norte B, leste C) | 828 m | 205 m | 0 / 0 | 134 | 1.00× |

**atribuição da decisão (por quota do Ring 3)**

| Entrada | Porta | Mesas (MRV) | Esperados | Cabe no Ring 3 | Paredes servidas | Troncos | Caminho médio porta → fila |
|---|---|---|---|---|---|---|---|
| A | S4 | 3, 5, 9, 12, 15, 20, 24, 26, 28 | 3.642 | 445 | leste / oeste / norte | 3 (159 m) | 31.7 m |
| B | S5 | 1, 4, 7, 8, 16, 17, 18, 21, 22, 25 | 4.215 | 513 | oeste / leste / norte | 3 (156 m) | 32.9 m |
| C | S6 | 2, 6, 10, 11, 13, 14, 19, 23, 27 | 3.642 | 445 | norte / oeste / leste | 3 (147 m) | 32.3 m |

**atribuição por parede (oeste A, norte B, leste C)**

| Entrada | Porta | Mesas (MRV) | Esperados | Cabe no Ring 3 | Paredes servidas | Troncos | Caminho médio porta → fila |
|---|---|---|---|---|---|---|---|
| A | S4 | 1, 4, 5, 6, 9, 11, 12, 17, 24 | 3.833 | 445 | oeste | 1 (49 m) | 29.4 m |
| B | S5 | 2, 8, 10, 13, 15, 16, 20, 22, 25 | 3.835 | 513 | norte | 1 (114 m) | 38.5 m |
| C | S6 | 3, 7, 14, 18, 19, 21, 23, 26, 27, 28 | 3.831 | 445 | leste | 1 (41 m) | 23.5 m |

