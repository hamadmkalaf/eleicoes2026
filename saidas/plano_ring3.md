# Plano base do Ring 3 — RDS Ballsbridge, 04/10/2026

Escopo: **apenas o Ring 3**. A análise que o sustenta está em
`saidas/analise_gargalos.md`. Desenho em escala: `saidas/layout_ring3.svg`,
gerado por `scripts/layout_ring3.py`.

Premissas fixadas: 28 urnas / 28 mesas (1:1), identificação por **caderno
físico**, **Hall 2 + Ring 3 sem cobertura**, **piso pavimentado**, espaço
**locado desde a véspera** — não há carros estacionados a remover.

---

## 1. Dimensões adotadas

Estimadas por fotogrametria sobre imagem aérea, com escala ancorada em feições
de solo (carros, vagas, largura da R118, copas), não em telhados — a imagem é
oblíqua e telhado de prédio alto não coincide com sua projeção no solo. Escala
apurada: **0,15 m/px**, com quatro aferições independentes convergindo.

| Área | Dimensão | Superfície |
|---|---|---|
| **Ring 3** | **~39 m (leste–oeste) × ~35 m (sul–norte)** | **~1.365 m²** |
| Apron pavimentado entre o Ring 3 e a fachada sul do Hall 2 | ~60 × 14 m | ~850 m² |

Incerteza: **±10–15% nas dimensões lineares**. Suficiente para dimensionar,
insuficiente para contrato. Aferir com a ferramenta "Medir distância" do Google
Maps ou com a planta do recinto.

## 2. Portas do Hall 2

A fachada sul do Hall 2, que encara o Ring 3, tem **nove aberturas, S1 a S9**,
conforme a prancheta do Posto. Papéis definidos:

| Porta | Distância do canto sudoeste | Papel |
|---|---|---|
| S1 | 9,5 m | — |
| **S2** | **13,7 m** | **SAÍDA** |
| S3 | 17,7 m | — |
| **S4** | **21,9 m** | **ENTRADA A** |
| **S5** | **28,1 m** | **ENTRADA B** |
| **S6** | **34,3 m** | **ENTRADA C** |
| S7 | 38,6 m | — |
| **S8** | **42,6 m** | **SAÍDA** |
| S9 | 46,8 m | — |

Distâncias medidas na prancheta e convertidas pela largura declarada de 50,2 m
(escala ~22,5 px/m) — a confirmar em campo.

Duas consequências de projeto:

**As três entradas estão a 6,2 m uma da outra.** É um passo apertado: um bloco
de fila de 7,0 m não cabe nesse intervalo sem invadir o vizinho. Por isso os
blocos ficam a 9,6 m de eixo e os eleitores caminham o pequeno desvio até a
porta na faixa de acesso ao norte — 0,6 m em A e C, 2,8 m em B.

**As saídas estão nos flancos, fora do vão das entradas** — S2 a 13,7 m e S8 a
42,6 m, enquanto as entradas ocupam de 21,9 a 34,3 m. Isso é uma vantagem: quem
sai do Hall 2 se afasta lateralmente, sem cruzar nenhuma fila de entrada. O
fluxo se separa sozinho, sem barreira adicional.

*Observação:* a planta `RDS_Hall_2_Floorplan_(1).pdf` numera as mesmas
aberturas como 2.1 a 2.23, com posições que não coincidem exatamente com as
lidas na prancheta. A aferição em campo resolve a divergência.

## 3. Layout

![Layout do Ring 3](layout_ring3.png)

*Fonte: `saidas/layout_ring3.svg`, gerado por `scripts/layout_ring3.py`.*

O eleitor entra pelo **canto sudeste**, percorre o **corredor de distribuição**
no fundo (bordo sul) de leste para oeste, e é desviado para o serpenteado da
sua urna — **C** primeiro, depois **B**, depois **A**. Cada serpenteado
descarrega ao norte, atravessando a **faixa de acesso** até a sua porta.

| Parâmetro | Valor |
|---|---|
| Folga sul | 1,5 m |
| Corredor de distribuição (fundo) | 2,5 m |
| **Profundidade do serpenteado** | **28,5 m** |
| **Faixa de acesso ao norte** | **2,5 m**, livre de barreira |
| Balizas por corredor | **5 em cada**, de 1,40 m |
| Largura de cada bloco | 7,0 m |
| Corredor de egresso entre blocos | 2,6 m |
| **Baia de reserva** | **6,4 m** em cada flanco |

Conferência de fechamento: 6,4 + 7,0 + 2,6 + 7,0 + 2,6 + 7,0 + 6,4 = **39,0 m**;
1,5 + 2,5 + 28,5 + 2,5 = **35,0 m**. O script falha alto se deixarem de fechar.

### Capacidade por entrada

| Entrada | Balizas | Serpenteado | Baia de reserva | **Total** | Quota |
|---|---|---|---|---|---|
| **A → S4** | 5 | 285 | 274 | **559** | 40% |
| **B → S5** | 5 | 285 | — | **285** | 20% |
| **C → S6** | 5 | 285 | 274 | **559** | 40% |
| | | 855 | 547 | **1.402** | |

### A faixa ao norte deixou de ser leque de descarga

Antes eram 5,0 m com três canais balizados convergindo às portas. Agora são
**2,5 m livres de barreira**, com duas funções:

1. **rota de maca e socorro a pé**, no sentido leste–oeste, ligando os dois
   flancos sem atravessar fila nenhuma;
2. travessia dos três fluxos até as suas portas, **sob orientação de marshal em
   vez de barreira**.

Os desvios laterais até as portas são pequenos: **A 0,6 m, B 2,8 m, C 0,6 m** —
percorridos a pé em espaço aberto, sem canal. Isso eliminou um componente
inteiro do quantitativo (os antigos canais de descarga, 18 separadores) e
devolveu **2,5 m de profundidade** ao serpenteado.

Com o corredor de fundo (2,5 m, sul), os egressos (2,6 m, norte–sul) e a faixa
de acesso (2,5 m, norte), o Ring 3 fica com uma **grade contínua de circulação**
que alcança qualquer ponto do layout — tudo acima do mínimo de 1,2 m para maca.
Acesso de veículo ao interior do Ring 3 foi dispensado.

### Serpenteados iguais, capacidades diferentes

Os três serpenteados são idênticos: **5 balizas, 285 pessoas cada**. Mas A e C
somam a baia do flanco e B não tem flanco nenhum — daí **40% / 20% / 40%**.

Isso não é corrigível na geometria: dar baia a B exigiria ocupar os corredores
de egresso, que são a saída lateral de quem está dentro da fila. **O ajuste é
feito na atribuição das urnas** (seção 6), e fecha com desvio de 0,4%.

## 4. Para que serve cada espaço, e como trocá-los

### O percurso do eleitor

**Garganta (canto sudeste)** → **corredor de distribuição** (fundo, leste→oeste)
→ **serpenteado** da sua entrada, ou **baia de reserva** se o serpenteado
estiver cheio → **faixa de acesso** → **porta S4, S5 ou S6**.

### O que cada faixa faz

| Eixo | Espaço | Medida | Função | O que a dimensiona |
|---|---|---|---|---|
| S→N | Folga sul | 1,5 m | recuo do limite | não se ocupa |
| S→N | **Corredor de distribuição** | 2,5 m | leva todos da garganta até a sua fila | é **passagem, não espera** |
| S→N | **Serpenteado** | 28,5 m | a fila **ordenada** | quantos esperam **com ordem de chegada preservada** |
| S→N | **Faixa de acesso** | 2,5 m | rota de maca leste–oeste; travessia até as portas | mínimo de 1,2 m para maca |
| L→O | **Baia de reserva** (×2) | 6,4 m | retenção **sem ordem**, exclusiva de A e de C | drena direto na baliza de entrada do bloco |
| L→O | **Blocos A / B / C** | 7,0 m | as balizas | número **ímpar** de balizas |
| L→O | **Corredor de egresso** (×2) | 2,6 m | saída lateral, marshals, socorro a pé, separação entre filas | 1,2 m mínimo de pedestre |

**A distinção que organiza tudo:** o serpenteado guarda pessoas **em ordem**; a
baia guarda pessoas **em massa**. Quem sai da baia entra no fim do serpenteado,
não na frente dele — a ordem se recompõe ali.

### Taxas de câmbio

As duas dimensões do Ring 3 são fixas (39 × 35 m). **Todo ajuste é uma troca.**

| Movimento | Rende | Custa |
|---|---|---|
| **+1 m de profundidade** do serpenteado (da faixa de acesso ou do fundo) | **+49 pessoas** | 9 separadores (~EUR 117) |
| **+2 balizas** num bloco (2,8 m, de baia ou egresso) | **+114 pessoas** | 27 separadores (~EUR 353) |
| **+1 m de largura** de baia (de bloco ou egresso) | **+43 pessoas** | 1 separador |

Por metro de largura, a baia rende **43 pessoas** e o serpenteado **41** —
praticamente o mesmo. Mas a baia custa **1 separador por metro** contra **9,7**.
**O serpenteado não se paga em capacidade; paga-se em ordem de chegada.**

### O que não é ajustável

- **Número ímpar de balizas** em cada bloco: entra-se pelo sul e a última tem de
  correr para o norte.
- **Baia colada ao seu bloco**: se não encostar na baliza de entrada, vira
  depósito comum.
- **Passo de 6,2 m entre S4, S5 e S6**: vem do prédio, não do desenho.

## 5. Necessidade de separadores de barreira

**Este quantitativo cobre somente o Ring 3.** O interior do Hall 2 tem
necessidade própria, ainda não dimensionada.

| # | Componente | Cálculo | Metros | Separadores |
|---|---|---|---|---|
| 1 | Balizas externas dos 3 blocos | 3 × 2 × 28,5 m | 171,0 | 86 |
| 2 | Balizas internas dos 3 blocos | (4+4+4) × 27,1 m | 325,2 | 163 |
| 3 | Corredor de distribuição (fundo) | 2 × 36,0 − 3 vãos de 1,5 m | 67,5 | 34 |
| 4 | Garganta de entrada (canto sudeste) | funil de pré-triagem | 10,0 | 5 |
| 5 | Fechamento das baias de flanco (A e C) | 2 × (4,9 + 6,4) m | 22,6 | 12 |
| | **TOTAL DO RING 3** | | **596,3** | **300** |
| | Fornecidos pela organizadora | 200 un. de 2 m × 1 m de altura | −400,0 | −200 |
| | **A ADQUIRIR** | | **200,0** | **100** |

> **100 separadores adicionais ≈ EUR 1.302**, ao custo unitário de referência
> (EUR 6,51/m). São ~8% do orçamento revisado de EUR 15.703,32.

A supressão dos canais de descarga eliminou um componente inteiro (18
separadores). O aprofundamento do serpenteado de 26,0 para 28,5 m devolveu
parte disso, e o resultado líquido é **de 117 para 100 separadores a adquirir,
com a capacidade subindo de 1.274 para 1.402**.

**Especificação recebida:** separadores de barreira externa, **2 m × 1 m de
altura**, fornecidos pela empresa organizadora. A altura de 1 m canaliza fila,
mas **não contém multidão sob pressão** — é o que sustenta os corredores de
egresso e a liberação em lotes.

## 6. Atribuição das urnas às entradas

As três entradas não têm a mesma capacidade, então a carga tem de ser repartida
**na proporção dessa capacidade**, e não em terços. Reproduzível com
`python3 -c "import sys; sys.path.insert(0,'scripts'); import simula_fluxo as m; m._relatorio_entradas()"`.

| Entrada | Urnas | Comparecimento esperado | Quota obtida | Alvo | Desvio |
|---|---|---|---|---|---|
| **A** | 11 | 4.569 | 40,0% | 4.544 | +25 |
| **B** | 6 | 2.276 | 19,9% | 2.318 | −41 |
| **C** | 11 | 4.572 | 40,0% | 4.544 | +28 |
| | 28 | 11.416 | | | |

O desvio máximo é de 41 eleitores em 11.416 — **0,4%**. A menor capacidade de
B deixa de ser um problema porque B recebe menos eleitorado: **6 urnas contra
11 em cada uma das outras**.

- **A:** 511, 513, 1352, 3108, 3161, 3302, 3305, 3308, 3309, **3313**, 3688
- **B:** 517, 1160, 3078, 3229, **3315**, 3832
- **C:** 512, 3054, 3142, 3179, 3216, 3245, 3306, 3311, **3322**, 3442, 3862

**As três urnas T1 vão para entradas diferentes** — 3313 em A, 3315 em B, 3322
em C. Concentrar as três (590 eleitores esperados cada) numa só entrada criaria
um pico que nenhuma reserva absorveria, e são justamente elas que definem o
horário de fechamento (ver `analise_gargalos.md`).

## 7. O Ring 3 comporta a fila prevista?

Da coluna FILA TOTAL de `scripts/simula_fluxo.py`, comparada à capacidade do
Hall 2 (~1.000–1.200 em fila interna) somada às ~1.300 do Ring 3:

| Arranjo da mesa | Fila total no pico | Cabe em Hall 2 (~1.100) + Ring 3 (~1.402)? |
|---|---|---|
| Dois cadernos em paralelo, qualquer t_id | 0 | Sim — o Ring 3 nem abre |
| Pipeline, t_id 55 s | 439 | Sim, só no Hall 2 |
| Serial, t_id 45 s | 1.058 | Sim, só no Hall 2 |
| Serial, t_id 55 s | 1.637 | Sim, com os serpenteados |
| Serial, t_id 65 s | 2.240 | Sim, com o flanco aberto |
| Serial, t_id 75 s | 2.974 | **Não — transborda para a Merrion Road** |

**O Ring 3 não resolve o gargalo; ele compra tempo.** Quem resolve é o arranjo
de dois cadernos em paralelo por urna, que fecha às 17h00 mesmo com caderno
lento e não custa nada ao TRE.

## 8. Evacuação e densidade

Referências de crowd safety para evento ao ar livre: escoamento de **82 pessoas
por metro de largura por minuto**, alvo de evacuação de **8 a 10 minutos**, e
**2 pessoas/m²** como densidade de referência. Conferência reproduzível em
`scripts/layout_ring3.py`.

| Verificação | Valor | Situação |
|---|---|---|
| Densidade no serpenteado | 1,43 p/m² | OK (limite 2,0) |
| Densidade na baia de reserva | 1,50 p/m² | OK (limite 2,0) |
| Grade de circulação (fundo 2,5 m + egressos 2,6 m + faixa norte 2,5 m) | ≥ 2,5 m | OK (mínimo 1,2 m para maca) |
| Acesso de veículo ao interior | — | **Dispensado pelo Posto** |
| Largura de saída exigida (1.402 pessoas / 8 min) | **2,14 m** | — |
| Largura de saída designada hoje | **1,50 m** (só a garganta sudeste) | **Insuficiente — 11,4 min** |

### A fragilidade é a saída única

**O Ring 3 tem hoje uma única saída designada: a garganta do canto sudeste.**
Os três fluxos ao norte levam para dentro do Hall 2 — inúteis se a emergência
for justamente lá.

1.402 pessoas por uma garganta de 1,5 m levam **11,4 minutos**, acima do alvo de
8. E é pior do que a conta sugere, porque toda a população converge para um
ponto único: qualquer obstrução ali não deixa alternativa. O aumento de
capacidade desta versão (1.274 → 1.402) **agravou** o problema em um minuto.

**Recomendação: abrir duas brechas de emergência de 2,0 m no perímetro sul e
leste**, em pontos distintos e distantes da garganta, sinalizadas e mantidas
desobstruídas. Com elas a evacuação cai para **3,1 minutos**.

Duas atenuantes que não substituem a medida: os separadores têm 1 m de altura e
são leves e autoportantes — numa emergência real são derrubados, e é assim que
funcionam; e o Ring 3 é área aberta, sem fumaça nem risco estrutural.

**Pendência que decide isto:** não sei se o perímetro do Ring 3 é fechado ou
aberto. Se for francamente aberto, o problema se dissolve e as brechas viram
sinalização. Se for fechado, são obrigatórias — e passam a ser o item mais
importante da lista, acima da barreira.

## 9. Exposição ao tempo

O espaço é descoberto. Outubro é o mês mais chuvoso de Dublin (**76–79 mm**). O
número de dias de chuva diverge conforme a fonte e o limiar: **12 dias** pelas
normais de 30 anos (1991–2020, limiar ≥1 mm) e **17–20** em fontes de limiar
mais frouxo — ou seja, **~40% a ~65%** de probabilidade para o dia 4. As fontes
não são metodologicamente comparáveis entre si.

Com piso pavimentado, o risco não é de lama nem de arraste para junto dos
pontos elétricos. É de **exposição**: gente parada 20–40 minutos na chuva
desiste. Desistência por fila é privação de voto que não aparece em nenhuma
estatística de comparecimento — e, ironicamente, *melhora* as métricas de
tempo por via indesejada.

Mitigação proporcional ao risco: cobertura leve (tenda ou toldo) sobre os
últimos 8–10 m de cada serpenteado, onde a espera é mais longa e a densidade
maior; e não sobre os 27 m inteiros. Cotar como item destacado.

## 10. Acessibilidade e atendimento prioritário

**211 eleitores com 60+ anos e 85 com deficiência declarada** em toda a zona —
~296 pessoas em 9 horas, ~33 por hora no pico. Volume trivial, desde que
roteado à parte.

**Nenhum eleitor prioritário entra no serpenteado.** Rota dedicada pelo apron
pavimentado, do desembarque direto à porta, com 1 agente designado. As balizas
de 1,40 m acomodam cadeira de rodas, mas 5 balizas de 26 m são **130 m de
percurso** — inaceitável para quem tem prioridade legal.

## 11. Equipe

| Função | Nº | Observação |
|---|---|---|
| Coordenador do Ring 3 | 1 | Decide abertura do flanco e ritmo de liberação |
| Agentes de pré-triagem (garganta sudeste) | 3 | Entregam o cartão de roteamento; gargalo potencial — dimensionar para o pico |
| Marshals de corredor | 3 | 1 por serpenteado |
| Marshals de porta | 3 | 1 por porta (S4, S5, S6); orientam a travessia da faixa de acesso, que não tem barreira, e falam com o interior do Hall 2 |
| Agente de acessibilidade | 1 | Rota prioritária pelo apron |
| Segurança | 4–6 | Dos 20 já contratados (item a) |
| **Total** | **15–17** | dos quais 4–6 já orçados |

## 12. Pendências

1. Aferir as dimensões do Ring 3 e **a distância entre o bordo oeste do Ring 3
   e o canto sudoeste do Hall 2** — é o número que translada todo o conjunto
   para os eixos coincidirem com as portas 2.7, 2.4 e 2.1.
2. Conciliar a numeração S1–S9 da prancheta com a numeração 2.1–2.23 da
   planta do RDS, que dão posições divergentes para as mesmas aberturas.
3. Submeter o pedido de **+100 separadores (~EUR 1.302)** para o Ring 3, e
   dimensionar à parte a necessidade do interior do Hall 2.
4. Cotar cobertura leve para os últimos 8–10 m de cada serpenteado.
5. **Verificar se o perímetro do Ring 3 é fechado ou aberto** e, se fechado,
   abrir duas brechas de emergência de 2,0 m (ver seção 7).
6. Definir o arranjo da mesa receptora com o Cartório Eleitoral — **é o que
   determina se o Ring 3 chega a ser usado**.
