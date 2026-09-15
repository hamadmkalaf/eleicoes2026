# Quanto cabe sem mudar o desenho — RDS Hall 2

Resposta fechada, dentro do layout atual: **as 28 mesas ficam onde estão, nas
três paredes; as entradas A e B e a saída central permanecem na parede sul.** A
serpentina ocupa apenas o que sobra, da faixa de triagem até o centro do salão.
O que não couber vai para a rua — e este documento diz quanto.

Números de `scripts/prancheta_capacidade.py`; desenho em
`saidas/prancheta_serpentina.svg`.

---

## 1. A resposta

Zona disponível: **36,2 × 18,25 m = 661 m² brutos** — a largura é o que sobra
entre as duas faixas perimetrais de mesas (7,0 m cada), a profundidade vai da
faixa de triagem (4,0 m) até o centro (y = 22,25 m).

| | Confortável | **Projeto** | Máximo admissível |
|---|---:|---:|---:|
| **Norte-sul, saída central mantida** | 452 | **629** | 821 |
| Norte-sul, saída roteada pela faixa perimetral | 458 | 637 | 830 |
| Leste-oeste, saída central mantida | 413 | 575 | 750 |
| Leste-oeste, saída pela faixa perimetral | 426 | 593 | 774 |

**629 pessoas** no cenário de projeto (0,65 m de canal por pessoa), **821** no
máximo admissível (0,50 m, equivalente a 2,0 p/m² — o teto que o *Purple Guide*
britânico usa para área de espera). 24 canais de 1,10 m, 415 m de canal, 260
unifilas.

Norte-sul continua melhor, mas a vantagem caiu de 22% para **9%**: preservar as
faixas perimetrais tira 10 m de largura da zona, e é justamente da largura que
vinha a vantagem do norte-sul. A escolha agora se decide menos pela conta e mais
pela operação — em norte-sul a cabeça de cada fila já aponta para o piso de
votação, em leste-oeste quem sai da banda sul atravessa as do norte.

### Os seis blocos

| Bloco | Porta | Canais | Largura | Profundidade | Canal | Pessoas |
|---|---|---:|---:|---:|---:|---:|
| A1 | A | 5 | 5,5 m | 13,7 m | 68 m | 103 |
| A2 | A | 5 | 5,5 m | 18,2 m | 91 m | 138 |
| A3 | A | 5 | 5,5 m | 18,2 m | 91 m | 138 |
| B1 | B | 3 | 3,3 m | 18,2 m | 55 m | 83 |
| B2 | B | 3 | 3,3 m | 18,2 m | 55 m | 83 |
| B3 | B | 3 | 3,3 m | 18,2 m | 55 m | 83 |

A1 é menor porque fica sobre o recorte do canto sudoeste: começa em y = 8,6 m,
alimentado por um corredor lateral de 1,2 m junto à quina.

## 2. O desequilíbrio que o desenho impõe

**A saída central não fica no meio do salão.** Lida da prancheta, ela está em
x ≈ 29,3 m, enquanto o meio da zona útil está em x ≈ 25,1 m. O corredor de saída
corta a zona fora do centro, e as duas metades ficam desiguais: 20,5 m para a
porta A, 12,7 m para a porta B. Daí os 5 canais por bloco de um lado e 3 do
outro.

O resultado: **a porta A comporta 379 pessoas (60%) e a porta B, 249 (40%).**

Isso não é um defeito do desenho — é uma consequência aritmética dele. E tem
conserto sem tocar em nada da prancheta: **redistribuir as urnas entre as portas
na proporção 60/40 em vez de 50/50.** Hoje a alocação é de ~5.700 eleitores
esperados por porta; passaria a ~6.850 na A e ~4.570 na B. É um ajuste de
tabela, não de layout, e sem ele a fila da porta B transborda enquanto a da
porta A ainda tem folga.

## 3. O que vai para a rua

Teto de 629 pessoas dentro do salão. O excedente é fila na rua — não por
escolha, por aritmética:

| Perfil | t/eleitor | Pico | Dentro | **Na rua** | Horas acima do teto | Calçada (fila simples) |
|---|---:|---:|---:|---:|---:|---:|
| Base | 45 s | 248 | 248 | **0** | — | — |
| Base | 60 s | 415 | 415 | **0** | — | — |
| Base | 75 s | 1.188 | 629 | **559** | 6,6 h | 363 m |
| Base | 90 s | 2.013 | 629 | **1.384** | 7,4 h | 900 m |
| Pico de manhã | 45 s | 511 | 511 | **0** | — | — |
| Pico de manhã | 60 s | 899 | 629 | **270** | 4,0 h | 176 m |
| Pico de manhã | 75 s | 1.746 | 629 | **1.117** | 8,7 h | 726 m |
| Pico de manhã | 90 s | 2.671 | 629 | **2.042** | 8,9 h | 1.327 m |

Operando no máximo admissível (821 pessoas), o transbordo do caso de 60 s com
pico de manhã cai de 270 para **78 pessoas** — 51 m de calçada. Os casos de
75 s e 90 s continuam com 925 e 1.850 na rua.

Três leituras:

**A 60 s a rua é um problema de uma manhã; a 75 s é um problema de um dia
inteiro.** Não são graus do mesmo problema: 4 horas acima do teto contra 8,7 —
a fila na rua deixa de ser um pico e passa a ser o estado normal da operação,
das 9h às 17h30.

**A calçada dá a medida real.** 270 pessoas em fila de uma pessoa só são 176 m
de calçada; 1.117 são 726 m. Não é uma questão de organizar melhor lá fora — é
uma questão de quantos quarteirões.

**Só o caso de 45 s tem folga em qualquer perfil.** Entre 60 s e 75 s está a
fronteira entre "gerenciável" e "ingerenciável", e ela é decidida pela
identificação do eleitor, não pelo desenho da fila.

## 4. As alavancas que não tocam nas mesas

Duas dimensões podem ser revistas sem mover uma única mesa:

| Faixa perimetral | Triagem | Canais | Projeto | Ganho |
|---:|---:|---:|---:|---:|
| 7,0 m | 4,0 m | 24 | 629 | — |
| 7,0 m | 2,5 m | 24 | 673 | +7% |
| 5,5 m | 4,0 m | 27 | 705 | +12% |
| **5,5 m** | **2,5 m** | **27** | **754** | **+20%** |

**A faixa perimetral tem um degrau em 5,6 m.** Entre 7,0 e 5,7 m nada muda —
não cabe canal a mais. Abaixo de 5,6 m entra um canal em cada bloco, e a
capacidade sobe 12% de uma vez. Não é ajuste fino: ou se atravessa o degrau ou
não vale a pena mexer. O custo é encurtar a micro-fila junto a cada mesa e a
circulação atrás dela — precisa ser medido contra a mesa, a cabine e a urna
reais, não estimado.

**A faixa de triagem de 4,0 m para 2,5 m vale 44 pessoas.** É menos do que
parece e cobra caro: a triagem é a etapa não paralelizável do sistema, e
apertá-la empurra o gargalo para a porta. Só faz sentido se a comunicação prévia
tiver funcionado e a maioria chegar sabendo a seção.

Somadas, as duas levam a zona de 629 a 754 pessoas e reduzem o transbordo do
caso de 60 s de 270 para 145.

## 5. O que este documento não resolve

- **A fila de abertura.** 342 a 571 pessoas chegam antes das 8h. Elas estão
  necessariamente fora, e a zona interna só começa a receber quando as portas
  abrem. Abrir o Hall 2 às 7h00 continua sendo a medida de maior efeito e menor
  custo — meia hora a mais no contrato de segurança, hoje das 7h30 às 17h30.
- **A rua em si.** Este documento dimensiona o transbordo; não trata de sua
  autorização. Se a fila externa é inevitável, ela precisa de decisão jurídica
  própria com a An Garda Síochána e o Dublin City Council, e de um responsável
  nomeado no dia.
- **O aval de incêndio.** Barreira em zona de egresso, com multidão estática
  entre as portas e o salão, muda o cálculo de evacuação. O layout tem de ser
  submetido ao responsável do RDS, não apenas comunicado. As margens de 2,0 m
  junto às paredes leste e oeste já estão descontadas de todos os números.

## 6. Premissas

- Faixa perimetral de 7,0 m (mesa + mesários + micro-fila + circulação) e faixa
  de triagem de 4,0 m são **estimativas de projeto**, não cotas da prancheta.
  São as duas premissas que mais mexem no resultado — ver seção 4.
- Posições das portas lidas graficamente do desenho atual: A em x ≈ 25,2 m,
  saída em x ≈ 29,3 m, B em x ≈ 34,4 m, com incerteza de cerca de ±1 m. O
  desequilíbrio 60/40 depende dessa leitura e deve ser confirmado na planta
  cotada.
- Canal de 1,10 m; passo de 0,65 m por pessoa no projeto, 0,90 m confortável,
  0,50 m no máximo admissível; meia pessoa perdida por curva de retorno;
  corredor mínimo de 1,20 m entre blocos.
- Corredor da saída central de 3,0 m.
- Comparecimento de 11.416 (74% Dublin, 50% interior, taxas de 2022 sobre o
  eleitorado real por urna). Perfil de chegada é premissa, não dado.
- "Calçada" convertida a 0,65 m por pessoa em fila de uma pessoa só; é a
  conversão da seção 5 de `plano_filas_sem_ring3.md`.
