# Cenários da Prancheta do Hall 2

Cada arquivo `*.json` é um cenário da prancheta: a lista de mesas que saem da
posição prevista na planta-base, e para onde vão. `planta_hall2.json` guarda a
planta em si — salão, módulo, portas e os cenários-base A e B — para que a
análise não dependa do artefato publicado.

Formato de um cenário:

```json
{"nome": "...", "base": "A",
 "alteracoes": [{"n": 22, "x": 40.05, "y": 44.4, "rot": 270, "lado": -1}],
 "medidas": [], "criadoEm": "...", "id": "..."}
```

`x`/`y` em metros, na ancoragem do módulo (o ponto onde ele encosta na parede),
com x para leste e y para norte. `rot` é o giro do módulo e `lado` diz de que
lado ficam as cadeiras dos mesários.

Para conferir um cenário:

```bash
python3 scripts/folgas_prancheta.py cenarios/tres-polos-20260905-182000.json
```

O script mede, mesa a mesa, a **folga lateral** (espaço livre de cada lado do
módulo, ao longo da parede) e a **fila** (profundidade livre à frente da mesa
dos mesários, onde os eleitores se enfileiram), e compara com a planta original.

## `tres-polos-20260905-182000.json` — Três polos · 22/23/24 separadas

Espalha as três mesas de maior movimento — **22, 23 e 24** — em três áreas
distintas do salão, cada uma com corredor próprio dos dois lados, em vez de
mantê-las encostadas no canto sudoeste.

| Mesa | Vai para | Lateral | Fila |
|---|---|---|---|
| 22 | parede norte, entre a mesa 8 e a coluna leste | 3,00 → 2,69 m | **0,98 → 20,0 m** |
| 23 | fachada leste, extremo sul | **0,98 → 2,70 m** | 20,0 m |
| 24 | parede oeste, no trecho vazio ao sul da porta O2 | **2,48 → 5,71 m** | 20,0 m |

Na planta original a 22 e a 23 se estorvam: a fila da 22 caminha para o norte e
bate no módulo da 23 depois de 0,98 m, e o mesmo encontro deixa a 23 com apenas
0,98 m de folga lateral. São as duas piores medidas do salão inteiro, e caem
justamente sobre mesas de alto volume.

Para abrir espaço, o cenário move mais 16 mesas em dois blocos rígidos, sem
mexer em nenhum corredor de dupla nem em nenhum recuo de emergência:

- duplas **(5,6)** e **(7,8)** recuam 2,00 m para oeste na parede norte,
  liberando o trecho onde a 22 se instala;
- a coluna leste **(9 a 20)** sobe 2,60 m, abrindo no extremo sul da fachada o
  vão onde a 23 se instala.

A mesa 21, que dividia a borda do recorte com a 22, passa de 3,00 m para 6,90 m
de folga lateral.

**Custo a registrar:** a fila da mesa 9 encurta de 4,29 m para 2,70 m, porque o
módulo da 22 passa a fechar o canto nordeste. É a única piora relevante do
cenário. No conjunto, a pior folga lateral do salão sobe de 0,98 m para 1,16 m e
a pior fila sobe de 0,98 m para 2,70 m.

**Limite encontrado:** a fachada leste não comporta uma mesa isolada com 3,00 m
de corredor dos dois lados. São 12 mesas em 36,3 m de fachada, espremidas entre
o recuo de emergência da porta S7 (que a fila não pode ocupar, ao sul) e a
parede norte. Os 2,70 m da mesa 23 são o máximo disponível sem comprimir os
espaçamentos entre duplas abaixo do padrão da planta.
