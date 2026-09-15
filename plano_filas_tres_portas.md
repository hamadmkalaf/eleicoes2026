# Serpentina para três entradas — prancheta Hamad_Final

Desenho de fila para a prancheta atual: **28 mesas nas paredes oeste, norte e
leste (9 / 9 / 10), entradas S4 (A), S5 (B) e S6 (C), saídas S2 e S8.** Nada
de mesa foi movido. A fila ocupa a zona da fachada sul até o centro do salão.

Condições impostas e como foram atendidas:

1. **Máximo de pessoas com circulação adequada** — canais norte-sul de 1,10 m,
   corredores de 1,20 m entre blocos, faixa de triagem de 4,0 m, corredor de
   saída de 3,0 m para S2, faixas perimetrais de 7,0 m preservadas.
2. **Blocos por porta, em múltiplos de 3** — 3, 6 e 9 blocos testados; **6 é o
   melhor** e 9 é inviável (ver §3).
3. **Mesma capacidade por porta** — obtida por busca exaustiva da repartição
   dos canais, com o último bloco de cada porta recuado até que as três portas
   tenham os mesmos metros de canal: **A 193 · B 194 · C 194.**

Números de `scripts/tres_portas.py`; desenhos em
`saidas/tres_portas_serpentina.svg` e `saidas/tres_portas_s2_fechada.svg`.

---

## 1. A resposta: 580 pessoas em 6 blocos

| | Confortável | **Projeto** | Máximo admissível |
|---|---:|---:|---:|
| **6 blocos (2 por porta)** | 416 | **580** | 757 |
| 3 blocos (1 por porta) | 356 | 497 | 648 |
| 9 blocos (3 por porta) | — | inviável | — |

25 canais, 383 m de canal, 240 unifilas (479 m). Passo de 0,65 m por pessoa
no projeto; 0,50 m no máximo admissível (2,0 p/m², teto do *Purple Guide*
para área de espera).

| Bloco | Porta | Canais | Profundidade | Canal | Pessoas | Observação |
|---|---|---:|---:|---:|---:|---|
| A1 | A | 7 | 11,8 m | 83 m | 125 | a oeste do corredor S2 |
| A2 | A | 3 | 14,9 m | 45 m | 68 | recuado para igualar |
| B1 | B | 3 | 18,2 m | 55 m | 83 | |
| B2 | B | 4 | 18,2 m | 73 m | 111 | |
| C1 | C | 3 | 18,2 m | 55 m | 83 | |
| C2 | C | 5 | 14,6 m | 73 m | 110 | recuado para igualar |

"Recuado" significa que a entrada do bloco (extremo sul) começa mais ao norte
— a barreira é simplesmente colocada mais adiante. É o único mecanismo usado
para igualar as portas; os canais são todos de 1,10 m.

## 2. Por que 6 blocos ganham de 3 e de 9

**3 blocos perdem o canto oeste.** Com um bloco só por porta, a região a oeste
do corredor de S2 (7 canais, 83 m) não pode ser usada: se fosse o único bloco
da porta A, B e C teriam de ser reduzidos a 83 m cada para manter a igualdade.
O ótimo com 3 blocos ignora o canto e fica em 497.

**6 blocos usam o canto.** A porta A ganha A1 no canto oeste e completa com A2
a leste do corredor; B e C se repartem no restante. É a única configuração que
respeita as regras 2 e 3 e ainda aproveita toda a largura: **+17% sobre 3
blocos.**

**9 blocos não fecham.** Oito blocos a leste de S2 exigem sete corredores de
1,20 m, sobram 14 canais para 8 blocos — menos de 2 canais por bloco. Com dois
canais não há serpentina, há um corredor de ida e volta. Impondo o mínimo de 3
canais por bloco, não existe solução. Se a regra dos múltiplos de 3 for lida
como "áreas por porta" e não como "blocos físicos", cada porta pode
subdividir seus dois blocos com sinalização, sem barreira adicional.

## 3. O custo da saída S2

A saída oeste em S2 (x ≈ 17 m) está **dentro da largura da zona de fila**, e
não no flanco como S8. Para levar quem votou nas paredes oeste e norte até
ela, o corredor desce pela faixa oeste, passa por cima do recorte sudoeste
(y = 7,4 a 10,4 m) e desce até a porta (x = 15,5 a 18,5 m). Isso custa:

- 3,0 m de largura da zona (o corredor vertical);
- 6,4 m de profundidade nos 7 canais do canto oeste (A1 fica com 11,8 m em
  vez de 18,2);
- **um cruzamento**: quem entra por S4 e vai para A1 atravessa o fluxo de
  saída a caminho de S2. É um cruzamento de pedestres com fiscal — rotineiro,
  mas é o único ponto do desenho onde entrada e saída se tocam. Está marcado
  na prancha.

**Variante: S2 fechada, saída oeste pelo norte até S8/S7.** Quem votou nas
paredes oeste e norte circula pelo piso norte e desce pela faixa leste; o
corredor de S2 desaparece, o canto oeste ganha profundidade, o cruzamento
some. Resultado: **747 pessoas no projeto (+29%), 975 no máximo, 249 por
porta**, sem nenhum cruzamento. O preço é uma caminhada de até ~60 m para
quem votou na parede oeste e a concentração de toda a saída em S8/S7 — que
comporta o fluxo (~1.300 saídas/h no pico contra capacidade de porta muito
maior), mas põe todo o egresso num só lado do salão. Vale a decisão.

| Variante | Projeto | Máximo | Por porta | Cruzamentos |
|---|---:|---:|---:|---:|
| S2 e S8 abertas (pedido) | **580** | 757 | 193 | 1 |
| S2 fechada, tudo por S8/S7 | 747 | 975 | 249 | 0 |

## 4. O que vai para a rua

Teto de 580 dentro do salão (S2 aberta):

| Perfil | t/eleitor | Pico | **Na rua** |
|---|---:|---:|---:|
| Base | 60 s | 415 | **0** |
| Pico de manhã | 60 s | 899 | **319** |
| Base | 75 s | 1.188 | **608** |
| Pico de manhã | 75 s | 1.746 | **1.166** |

Com S2 fechada (747): 152 na rua no caso de 60 s com pico de manhã; 441 e
999 nos de 75 s. A ordem de grandeza continua sendo decidida pelo tempo por
eleitor, não pelo desenho.

## 5. Premissas próprias deste desenho

- Portas lidas da prancheta como fração da fachada sul, entre o recorte e o
  canto sudeste: S2 = 17,0 m; S4 = 24,6; S5 = 30,2; S6 = 35,9; S7 = 39,7;
  S8 = 43,5 (±1 m). O corredor de S2 e o desequilíbrio que ele causa dependem
  dessa leitura.
- Recorte do canto sudoeste mantido em 11,7 × 7,4 m (leitura da planta do
  RDS). A prancheta sugere um recorte um pouco menor (~8 × 7 m); se for esse o
  caso, A1 ganha 2 a 3 canais.
- Faixa perimetral de 7,0 m e triagem de 4,0 m são estimativas de projeto. A
  faixa tem um degrau em 5,6 m (entra um canal a mais por bloco).
- Mínimo de 3 canais por bloco; bloco recuado não fica mais raso que 6,0 m.
- Mesma base de comparecimento e perfis de chegada dos documentos anteriores.
