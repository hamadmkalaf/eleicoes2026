# Toda a fila dentro do Hall 2 — dimensionamento da serpentina

Substitui as seções 3 a 5 de `plano_filas_sem_ring3.md` sob as novas restrições:
**o RDS proibiu formação de fila em seu terreno, o uso da rua é incerto e não há
autorização de Brasília para o Ring 3.** Não existe mais nenhum lugar de espera
fora do Hall 2. Números de `scripts/serpentina_hall2.py`; desenho em
`saidas/serpentina_hall2.svg`.

---

## 1. Resposta direta

Na zona pedida — da parede sul (portas A e B) até o centro do salão, y = 0 a
22,25 m — com 3 filas por porta:

| Orientação dos canais | Blocos | Área de fila | Metros de canal | **Projeto** | Máximo admissível | Unifilas |
|---|---:|---:|---:|---:|---:|---:|
| **Norte-sul** | 6 | 662 m² | 602 m | **911** | 1.189 | 352 |
| Leste-oeste | 6 | 541 m² | 492 m | 747 | 974 | 308 |

**Norte-sul acomoda 22% mais gente na mesma zona.** Adote norte-sul.

"Projeto" usa passo de 0,65 m de canal por pessoa; "máximo admissível", 0,50 m —
o equivalente a 2,0 p/m², que o *Purple Guide* britânico trata como teto de área
de espera. Acima disso não é dimensionamento, é risco.

## 2. Por que norte-sul ganha

Não é sobre o formato do salão — a área é a mesma nas duas. São duas razões
somadas:

**O pedágio dos corredores é pago uma vez, não duas.** O número de canais é
limitado pela dimensão ao longo da qual eles se empilham, menos o que os
corredores de separação consomem.

- **N-S:** os 6 blocos se empilham ao longo dos 46,2 m de largura útil. Cabem
  36 canais (6 por bloco), com 5 corredores de 1,32 m. Um só pedágio.
- **L-O:** manter 3 filas por porta obriga a separar as duas metades por uma
  espinha central — sem ela, uma banda que atravessa o salão inteiro seria
  alimentada pelas duas portas ao mesmo tempo. Cada metade então empilha seus
  canais na **mesma** profundidade de 18,25 m, e o pedágio dos corredores é
  pago duas vezes: 24 canais no total, mais 2 m de largura perdidos na espinha.

**A cabeça da fila aponta para o lugar certo.** Em N-S, cada bloco entra pelo
sul (junto às portas) e termina no norte, de frente para o piso de votação: o
eleitor liberado dá um passo e está na micro-fila da sua urna. Em L-O, quem sai
da banda mais ao sul precisa atravessar as duas bandas do norte — contrafluxo
dentro da zona de fila, que exige mais corredores e come mais área ainda.

### Os 6 blocos em norte-sul

| Bloco | Porta | Canais | Profundidade | Canal | Pessoas |
|---|---|---:|---:|---:|---:|
| A1 | A | 6 | 13,7 m | 82 m | 124 |
| A2 | A | 6 | 13,7 m | 82 m | 124 |
| A3 | A | 6 | 18,2 m | 110 m | 166 |
| B1 | B | 6 | 18,2 m | 110 m | 166 |
| B2 | B | 6 | 18,2 m | 110 m | 166 |
| B3 | B | 6 | 18,2 m | 110 m | 166 |

A1 e A2 são menores porque ficam sobre o recorte do canto sudoeste: começam em
y = 8,6 m, alimentados por um corredor lateral de 1,2 m junto à quina. A
alocação de urnas por bloco continua a de `plano_filas_sem_ring3.md` — só muda
onde os blocos ficam, não quem vai para cada um.

## 3. Até onde vale empurrar a linha divisória

O centro do salão não é um limite físico, é o limite que você pediu. Cada metro
a mais de zona de fila é um metro a menos de piso de votação:

| Linha | Área de fila | Projeto | Máximo | Parede p/ 28 MRV | Vão livre entre mesas | Mesas na parede | Mesas em ilha |
|---:|---:|---:|---:|---:|---:|---|---|
| 16,0 m | 414 m² | 565 | 739 | 107,2 m | 2,03 m | ok | ok |
| 18,0 m | 494 m² | 675 | 883 | 103,2 m | 1,89 m | ok | ok |
| 20,0 m | 573 m² | 786 | 1.027 | 99,2 m | 1,74 m | apertado | ok |
| **22,25 m** | **662 m²** | **911** | **1.189** | 94,7 m | 1,58 m | apertado | ok |
| 24,0 m | 731 m² | 1.008 | 1.315 | 91,2 m | 1,46 m | apertado | ok |
| 26,0 m | 810 m² | 1.119 | 1.459 | 87,2 m | 1,31 m | **inviável** | ok |
| 28,0 m | 890 m² | 1.229 | 1.603 | 83,2 m | 1,17 m | **inviável** | ok |

**Com as mesas encostadas nas paredes, o centro já é o limite prático.** A
22,25 m o vão livre entre seções vizinhas cai para 1,58 m — abaixo do que a
análise de layout anterior considerou adequado para circulação e sigilo, e a
26 m deixa de ser defensável.

**Com as mesas em ilha, a restrição de parede desaparece** e a linha pode ir a
26–28 m, rendendo 1.119 a 1.229 pessoas. A opção de agrupar mesas em ilhas já
foi levantada antes e é compatível com o procedimento **desde que cada mesa
continue fisicamente ligada à sua urna** — separar mesa de urna é que era o
risco. **Precisa de validação do Cartório Eleitoral antes de virar plano.**

## 4. A restrição que agora manda: urna disputa piso com fila

Este é o achado que muda a conversa. Mais urnas encurtam a fila, mas ocupam
piso, o que empurra a linha divisória para o sul e reduz a capacidade de
espera. As duas coisas puxam em sentidos opostos — e mesmo assim mais urnas
ganham, com folga.

Com mesas em ilha e a linha empurrada até o limite do piso de votação:

| Urnas | Linha máx. | Fila que cabe | 45 s | 60 s | 75 s | 90 s |
|---:|---:|---:|:--:|:--:|:--:|:--:|
| 28 | 31,6 m | 1.431 | sim | sim | **NÃO** | **NÃO** |
| 32 | 29,8 m | 1.330 | sim | sim | sim | **NÃO** |
| 36 | 28,0 m | 1.228 | sim | sim | sim | **NÃO** |
| 38 | 27,1 m | 1.177 | sim | sim | sim | sim |
| 40 | 26,1 m | 1.126 | sim | sim | sim | sim |

*(pico de fila do perfil "pico de manhã" contra a capacidade da zona)*

**Com 28 urnas, o Hall 2 comporta a fila somente se o atendimento ficar em
60 s ou menos.** A 75 s a fila supera qualquer arranjo possível dentro do
salão — e não há mais para onde transbordar.

Lido pela variável de tempo, na configuração pedida (linha no centro, teto de
911 pessoas):

| Urnas | Tempo máximo por eleitor — perfil base | — pico de manhã |
|---:|---:|---:|
| 28 | 69 s | **60 s** |
| 32 | 86 s | 72 s |
| 36 | 97 s | 81 s |
| 38 | 103 s | **86 s** |
| 40 | 108 s | 90 s |

Isto deixa de ser argumento de conforto e vira **condição física de
realização**: com identificação por caderno físico (~90 s), o 1º turno só cabe
no Hall 2 com 38 ou mais urnas. É esse o pedido a levar ao TSE e a Brasília,
e agora ele tem uma prova geométrica, não uma preferência operacional.

## 5. Os dois problemas que a serpentina não resolve

**A fila das 7h–8h.** De 342 a 571 pessoas chegam antes da abertura. Com o
terreno do RDS proibido e a rua incerta, **não existe lugar autorizado para
elas**. A única saída interna é **abrir o Hall 2 às 7h00 para formação de fila
dentro da serpentina, com a votação começando às 8h00**. Isso converte um
problema sem solução externa em um problema já dimensionado — a zona comporta
911, muito acima das 571. Requer duas providências:

1. Negociar com o RDS a abertura do salão uma hora antes (é uso do espaço
   contratado, não do terreno — categoria diferente da que foi proibida).
2. Estender o contrato de segurança, hoje das 7h30 às 17h30, para começar às
   7h00. É meia hora × 20 seguranças.

**O transbordo acima de 911.** Se o tempo por eleitor ficar em 75 s ou mais, a
fila estoura a zona e não há plano B externo. As alternativas internas, em
ordem de preferência: (a) avançar a linha divisória com mesas em ilha; (b)
converter o núcleo norte remanescente em segunda zona de espera, sacrificando
circulação; (c) operar a zona como **curral sem canais** — a mesma área
comporta 1.174 a 1.565 pessoas, **cerca de 30% a mais**, porque não se perde
área com corredores de separação. O custo de (c) é alto e deve ser dito com
todas as letras: **perde-se a ordem de chegada**. Numa eleição, fila sem ordem
visível gera disputa, sensação de privilégio e reclamação formal. Serve como
modo de contingência declarado, nunca como desenho.

## 6. Material

| | Unifila | CCB |
|---|---:|---:|
| Serpentina N-S (602 m de barreira) | 352 | — |
| Micro-filas de seção (28 × 4 m) | 56 | — |
| Funis de porta e triagem | — | 16 |
| Canal de saída e sinalização | 25 | — |
| **Total** | **433** | **16** |

Contra as **100 unifilas (200 m) do orçamento aprovado**, faltam **333
unidades**. Ao preço unitário da linha atual (EUR 13,03), cerca de
**EUR 4.340** — sujeito a cotação nova, porque 433 unidades é um volume que
muda o preço e pode não existir em estoque numa data única em Dublin.

A boa notícia da nova restrição: **as 122 CCB caíram para 16.** Sem retenção
externa e sem corredor de rua, some a necessidade de contenção rígida ao ar
livre. A economia de CCB compensa boa parte do acréscimo de unifila.

## 7. Ocupação e segurança

No pico de projeto: 911 em fila + cerca de 210 de operação (84 mesários, ~56
fiscais, 22 de fluxo, 20 de segurança, 28 votando) = **1.121 pessoas**, 39% da
capacidade de 2.900 que a ficha técnica do RDS atribui ao Hall 2. No máximo
admissível, 1.399 — 48%.

A capacidade nominal do recinto, portanto, **não é a restrição**. A restrição é
o piso: fila precisa de canais e corredores, não só de metro quadrado. Mas duas
coisas passam a exigir aval formal do responsável de incêndio do RDS, porque
agora há multidão estática entre as portas e o salão:

- As 12 saídas de emergência precisam continuar desobstruídas, com as margens
  de 2,0 m junto às paredes leste e oeste mantidas livres — elas já estão
  descontadas de todos os números acima.
- Barreira em zona de egresso muda o cálculo de evacuação do recinto. O layout
  tem de ser submetido, não apenas comunicado.

## 8. Premissas novas ou alteradas

- Canal de 1,10 m; passo de 0,65 m (projeto), 0,90 m (confortável) e 0,50 m
  (máximo) de canal por pessoa; meia pessoa perdida por curva de retorno.
- Faixa livre de 4,0 m junto à parede sul (triagem) e 2,0 m junto às paredes
  leste e oeste (egresso), descontadas da zona.
- Corredor mínimo de 1,20 m entre blocos.
- Módulo de seção em ilha estimado em 3,2 × 4,0 m com fator de circulação de
  1,8 — **é a premissa mais frágil do documento** e determina sozinha a
  coluna "linha máx." da seção 4. Precisa ser aferida contra as dimensões reais
  da mesa, da cabine e da urna.
- Recorte do canto sudoeste (~11,7 × 7,4 m) segue lido graficamente da planta
  e pendente de medição — ele custa dois blocos menores (A1 e A2).
