# Dimensionamento de voluntarios — anexo quantitativo

Gerado por `scripts/voluntarios.py`. Todas as premissas estao no
dicionario `PREMISSAS` do script; mudar um valor e rodar de novo
refaz este anexo.

Base: **16794 aptos**, **28 urnas**, comparecimento esperado **11418** (68%).

## Fluxo e equipe necessaria, hora a hora

| Hora | Eleitores | Por minuto | Fila ext. | Triagem | Consulta | Corredor | Prioritario | Runner | Saida | Coord. | Reserva | **Total** |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 08-09 | 913 | 15.2 | 8 | 4 | 3 | 8 | 2 | 4 | 2 | 3 | 6 | **40** |
| 09-10 | 1370 | 22.8 | 2 | 6 | 4 | 8 | 3 | 4 | 2 | 3 | 5 | **37** |
| 10-11 | 1713 | 28.5 | 2 | 8 | 5 | 8 | 3 | 4 | 2 | 3 | 6 | **41** |
| 11-12 | 1713 | 28.5 | 2 | 8 | 5 | 8 | 3 | 4 | 2 | 3 | 6 | **41** |
| 12-13 | 1484 | 24.7 | 2 | 7 | 4 | 8 | 3 | 4 | 2 | 3 | 5 | **38** |
| 13-14 | 1256 | 20.9 | 2 | 6 | 4 | 8 | 3 | 4 | 2 | 3 | 5 | **37** |
| 14-15 | 1142 | 19.0 | 2 | 5 | 3 | 8 | 2 | 4 | 2 | 3 | 5 | **34** |
| 15-16 | 1028 | 17.1 | 2 | 5 | 3 | 8 | 2 | 4 | 2 | 3 | 5 | **34** |
| 16-17 | 799 | 13.3 | 2 | 4 | 2 | 8 | 2 | 4 | 2 | 3 | 5 | **32** |

Pico de equipe simultanea: **41 pessoas** (entre 10h e 12h).

## Escala de turnos

| Turno | Pessoas |
|---|---|
| T1 Manha (07h00-13h30) | 40 |
| T2 Tarde (12h30-encerramento) | 34 |
| T3 Reforco de pico (09h30-14h00) | 3 |
| **Pessoas distintas no dia** | **77** |
| **A recrutar** (absenteismo de 25%) | **103** |

## Sensibilidade

| Cenario | Pico simultaneo | Pessoas no dia | A recrutar |
|---|---|---|---|
| Enxuto | 30 | 56 | 75 |
| Base | 41 | 77 | 103 |
| Reforcado | 52 | 96 | 128 |

## Alocacao fisica: clusters de corredor e entradas

Um orientador de corredor por cluster. A reparticao entre as
entradas A e B equilibra o comparecimento esperado, nao a
contagem de urnas.

| Cluster | Entrada | Urnas | Comparecimento esperado |
|---|---|---|---|
| C1 | A | 3313, 3216, 517 | 1323 |
| C2 | B | 3322, 511, 513 | 1322 |
| C3 | B | 3315, 3229, 512 | 1319 |
| C4 | A | 3142, 3309, 1160 | 1227 |
| C5 | B | 3161, 3179, 1352, 3442 | 1547 |
| C6 | A | 3245, 3311, 3054, 3308 | 1570 |
| C7 | A | 3302, 3108, 3078, 3832 | 1561 |
| C8 | B | 3305, 3306, 3688, 3862 | 1549 |
| **Entrada A** | | **14 urnas** | **5681** |
| **Entrada B** | | **14 urnas** | **5737** |

## Comparecimento esperado por urna

| Urna | Aptos | Comparecimento esperado |
|---|---|---|
| 3313 | 797 | 590 |
| 3322 | 794 | 588 |
| 3315 | 792 | 586 |
| 3142 | 793 | 492 |
| 3161 | 791 | 491 |
| 3245 | 781 | 486 |
| 3302 | 771 | 481 |
| 3305 | 767 | 479 |
| 3306 | 766 | 478 |
| 3108 | 756 | 474 |
| 3311 | 630 | 466 |
| 3179 | 676 | 434 |
| 3309 | 615 | 403 |
| 3229 | 606 | 399 |
| 511 | 582 | 387 |
| 3216 | 571 | 381 |
| 517 | 513 | 352 |
| 513 | 502 | 347 |
| 512 | 476 | 334 |
| 1160 | 473 | 332 |
| 1352 | 462 | 327 |
| 3054 | 454 | 323 |
| 3078 | 429 | 310 |
| 3688 | 400 | 296 |
| 3862 | 400 | 296 |
| 3832 | 400 | 296 |
| 3308 | 399 | 295 |
| 3442 | 398 | 295 |
