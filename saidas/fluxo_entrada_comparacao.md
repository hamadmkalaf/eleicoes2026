# Entrada: triagem central (HUB) × fitas no piso (FITAS)

Comparecimento esperado: **11.416** eleitores (74% Dublin, 50% interior). Hora de pico: **31,7/min** no total, **15,9/min por porta** (fator de pico 1.5). Fração que chega sem saber a seção: **25%** (premissa).

Divisão de fluxo entre portas: A = 5.111, B = 6.305 eleitores esperados.

## Resumo

| Indicador | HUB | FITAS |
|---|---|---|
| Quem passa pela triagem | 100% | só quem não sabe a seção (25%) |
| Chegadas na triagem (pico, por porta) | 15,9/min | 4,0/min |
| Atendentes mínimos por porta/hub (fila estável) | 5 | 3 |
| Atendentes para conforto (ocupação < 80%) | 6 | 4 |
| Total de triadores nas duas portas (conforto) | 12 | 8 |
| Caminho médio porta → mesa | 37,1 m | 26,4 m |
| Buffer de fila dentro do salão | corredor 21,2 m ≈ 42 pessoas por porta | nenhum: a fila fica fora da porta |
| Cruzamentos entre trajetos de entrada | 0 (dispersão a partir dos hubs) | 0 (leques A e B não se cruzam) |
| Cruzamentos entrada × saída, saída central | 451 | 186 |
| Cruzamentos entrada × saída, saídas laterais | 70 | 70 |
| Fita no piso (6 troncos por zona) | — | 237 m, 8 rolos ≈ EUR 96 |
| Fita no piso (28 linhas, uma por mesa) | — | 787 m, 24 rolos ≈ EUR 288 |
| Largura do feixe de fitas na porta | — | 0,25 m (zonas) vs 2,75 m (uma por mesa) |

## HUB: fila na triagem central (serviço médio 17,2 s)

| atendentes por hub | ocupação | prob. esperar | espera média | fila média |
|---|---|---|---|---|
| 1 | 456% | 100% | ∞ min | ∞ |
| 2 | 228% | 100% | ∞ min | ∞ |
| 3 | 152% | 100% | ∞ min | ∞ |
| 4 | 114% | 100% | ∞ min | ∞ |
| 5 | 91% | 79% | 0,5 min | 8,1 |
| 6 | 76% | 44% | 0,1 min | 1,4 |
| 7 | 65% | 23% | 0,0 min | 0,4 |
| 8 | 57% | 11% | 0,0 min | 0,1 |
| 9 | 51% | 5% | 0,0 min | 0,1 |
| 10 | 46% | 2% | 0,0 min | 0,0 |
| 11 | 41% | 1% | 0,0 min | 0,0 |
| 12 | 38% | 0% | 0,0 min | 0,0 |
| 13 | 35% | 0% | 0,0 min | 0,0 |
| 14 | 33% | 0% | 0,0 min | 0,0 |
| 15 | 30% | 0% | 0,0 min | 0,0 |

## FITAS: fila no balcão de apoio (serviço 45 s, só quem não sabe)

| atendentes por porta | ocupação | prob. esperar | espera média | fila média |
|---|---|---|---|---|
| 1 | 297% | 100% | ∞ min | ∞ |
| 2 | 149% | 100% | ∞ min | ∞ |
| 3 | 99% | 98% | 27,3 min | 108,4 |
| 4 | 74% | 50% | 0,4 min | 1,4 |
| 5 | 59% | 23% | 0,1 min | 0,3 |
| 6 | 50% | 10% | 0,0 min | 0,1 |
| 7 | 42% | 4% | 0,0 min | 0,0 |
| 8 | 37% | 1% | 0,0 min | 0,0 |
| 9 | 33% | 0% | 0,0 min | 0,0 |

## Sensibilidade: quantos atendentes por porta/hub conforme a fração que não sabe a seção

| não sabe a seção | HUB mínimo | HUB conforto | FITAS mínimo | FITAS conforto |
|---|---|---|---|---|
| 10% | 4 | 4 | 2 | 2 |
| 25% | 5 | 6 | 3 | 4 |
| 40% | 7 | 8 | 5 | 6 |
| 60% | 8 | 10 | 8 | 9 |

## Alocação das urnas às posições (equilibrando A e B)

| Mesa | Urna (seção principal) | Zona | Porta | Aptos | Esperados |
|---|---|---|---|---|---|
| 1 | 3311 | Oeste-Sul | A | 630 | 466 |
| 2 | 3306 | Oeste-Sul | A | 766 | 478 |
| 3 | 3302 | Oeste-Sul | A | 771 | 481 |
| 4 | 3161 | Oeste-Sul | A | 791 | 491 |
| 5 | 3142 | Oeste-Sul | A | 793 | 492 |
| 6 | 3313 | Oeste-Sul | A | 797 | 590 |
| 7 | 3309 | Oeste-Norte | A | 615 | 403 |
| 8 | 0511 | Oeste-Norte | A | 582 | 387 |
| 9 | 0517 | Oeste-Norte | A | 513 | 352 |
| 10 | 0512 | Oeste-Norte | A | 476 | 334 |
| 11 | 1352 | Norte-Oeste | A | 462 | 327 |
| 12 | 3078 | Norte-Oeste | A | 429 | 310 |
| 13 | 3862 | Norte-Leste | B | 400 | 296 |
| 14 | 3832 | Norte-Leste | B | 400 | 296 |
| 15 | 3308 | Norte-Leste | B | 399 | 295 |
| 16 | 3442 | Norte-Leste | B | 398 | 295 |
| 17 | 3229 | Leste-Norte | B | 606 | 399 |
| 18 | 3216 | Leste-Norte | B | 571 | 381 |
| 19 | 0513 | Leste-Norte | B | 502 | 347 |
| 20 | 1160 | Leste-Norte | B | 473 | 332 |
| 21 | 3054 | Leste-Norte | B | 454 | 323 |
| 22 | 3688 | Leste-Norte | B | 400 | 296 |
| 23 | 3322 | Leste-Sul | B | 794 | 588 |
| 24 | 3315 | Leste-Sul | B | 792 | 586 |
| 25 | 3245 | Leste-Sul | B | 781 | 486 |
| 26 | 3305 | Leste-Sul | B | 767 | 479 |
| 27 | 3108 | Leste-Sul | B | 756 | 474 |
| 28 | 3179 | Leste-Sul | B | 676 | 434 |
