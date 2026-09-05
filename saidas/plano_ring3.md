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
de fila de 7,0 m não cabe nesse intervalo sem invadir o vizinho. Daí a faixa de
descarga (item 3).

**As saídas estão nos flancos, fora do vão das entradas** — S2 a 13,7 m e S8 a
42,6 m, enquanto as entradas ocupam de 21,9 a 34,3 m. Isso é uma vantagem: quem
sai do Hall 2 se afasta lateralmente, sem cruzar nenhuma fila de entrada. O
fluxo se separa sozinho, sem barreira adicional.

*Observação:* a planta `RDS_Hall_2_Floorplan_(1).pdf` numera as mesmas
aberturas como 2.1 a 2.23, com posições que não coincidem exatamente com as
lidas na prancheta. A aferição em campo resolve a divergência.

## 3. Layout

O eleitor entra pelo **canto sudeste**, percorre o **corredor de distribuição**
no fundo (bordo sul) de leste para oeste, e é desviado para o serpenteado da
sua urna — **C** primeiro, depois **B**, depois **A**. Cada serpenteado
descarrega ao norte, na sua porta.

| Parâmetro | Valor |
|---|---|
| Corredor de distribuição (fundo) | 2,5 m de largura, todo o bordo sul |
| Profundidade do serpenteado | **26,0 m** |
| Faixa de descarga | **5,0 m** |
| Balizas por corredor | **5**, de **1,40 m** |
| Largura de cada bloco | 7,0 m |
| Passo entre blocos | 9,0 m (7,0 de bloco + 2,0 de egresso) |
| Fila por corredor | 130 m lineares |
| **Capacidade por corredor** | **260 pessoas** (0,50 m por pessoa) |
| **Capacidade dos três** | **780 pessoas** |
| Reserva de flanco (sem balizas, sob marshals) | **~490 pessoas** |
| **Total do Ring 3** | **~1.270 pessoas** |

**Por que 5 balizas.** O número tem de ser **ímpar** — entra-se pelo sul e a
última baliza precisa correr para o norte, onde estão as portas. E 5 × 1,40 m
= 7,0 m é o bloco mais largo que preserva 2,0 m de egresso entre vizinhos no
passo de 9,0 m adotado.

**O bloco A é espelhado.** Nos blocos B e C entra-se pela baliza leste e sai-se
pela oeste. No bloco A a ordem se inverte: entra-se pela oeste, sai-se pela
leste. Sem essa inversão, a saída de A cairia **5,6 m** a oeste da porta S4 —
uma diagonal de 48° na faixa de descarga. Com ela, **A sai exatamente sobre S4
e C exatamente sobre S6**, e resta um único canal em diagonal, o de B, com
2,8 m em 5,0 m de profundidade (29°). É um ajuste de montagem que não custa
nada e elimina dois cruzamentos.

Desenho em escala: **`saidas/layout_ring3.svg`**, com cada componente de
barreira numerado e o quantitativo ao pé.

## 4. Necessidade de separadores de barreira

**Este quantitativo cobre somente o Ring 3.** O interior do Hall 2 — filas
junto às 28 urnas, canalização das portas para dentro, separação dos fluxos de
saída — tem necessidade própria, ainda não dimensionada.

Um serpenteado de *n* balizas exige *n+1* corridas de separador: as duas
externas correm a profundidade inteira, e as internas param a 1,40 m de uma das
pontas para abrir o retorno.

| # | Componente | Cálculo | Metros | Separadores |
|---|---|---|---|---|
| 1 | Balizas externas dos 3 blocos | 3 × 2 × 26,0 m | 156,0 | 78 |
| 2 | Balizas internas dos 3 blocos | 3 × 4 × 24,6 m | 295,2 | 148 |
| 3 | Corredor de distribuição (fundo) | 2 × 36,0 − 3 vãos de 1,5 m | 67,5 | 34 |
| 4 | Garganta de entrada (canto sudeste) | funil de pré-triagem | 10,0 | 5 |
| 5 | Canais de descarga até S4/S5/S6 | 2 lados × (5,0 + 5,7 + 5,0) m | 31,5 | 16 |
| | **TOTAL DO RING 3** | | **560,2** | **281** |
| | Em mãos hoje (item d do orçamento) | 100 separadores = 200 m | −200,0 | −100 |
| | **A ADQUIRIR** | | **362,0** | **181** |

> **181 separadores adicionais ≈ EUR 2.357**, ao custo unitário já praticado
> (EUR 1.303,00 ÷ 200 m = EUR 6,51/m). São ~15% do orçamento revisado de
> EUR 15.703,32.

E isso esgota o estoque atual no Ring 3, **sem sobrar um metro para dentro do
Hall 2**. Quando o interior for dimensionado, o pedido cresce.

As balizas dominam o quantitativo: os itens 1 e 2 somam 451 m, **80% do total**.
Cada baliza a menos por corredor devolve ~53 m (27 separadores, ~EUR 344) e
custa 156 pessoas de capacidade.

## 5. O Ring 3 comporta a fila prevista?

Da coluna FILA TOTAL de `scripts/simula_fluxo.py`, comparada à capacidade do
Hall 2 (~1.000–1.200 em fila interna) somada às ~1.300 do Ring 3:

| Arranjo da mesa | Fila total no pico | Cabe em Hall 2 (~1.100) + Ring 3 (~1.270)? |
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

## 6. Exposição ao tempo

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

## 7. Acessibilidade e atendimento prioritário

**211 eleitores com 60+ anos e 85 com deficiência declarada** em toda a zona —
~296 pessoas em 9 horas, ~33 por hora no pico. Volume trivial, desde que
roteado à parte.

**Nenhum eleitor prioritário entra no serpenteado.** Rota dedicada pelo apron
pavimentado, do desembarque direto à porta, com 1 agente designado. As balizas
de 1,40 m acomodam cadeira de rodas, mas 5 balizas de 26 m são **130 m de
percurso** — inaceitável para quem tem prioridade legal.

## 8. Equipe

| Função | Nº | Observação |
|---|---|---|
| Coordenador do Ring 3 | 1 | Decide abertura do flanco e ritmo de liberação |
| Agentes de pré-triagem (garganta sudeste) | 3 | Entregam o cartão de roteamento; gargalo potencial — dimensionar para o pico |
| Marshals de corredor | 3 | 1 por serpenteado |
| Marshals de descarga | 3 | 1 por porta (S4, S5, S6), em contato com o interior do Hall 2 |
| Agente de acessibilidade | 1 | Rota prioritária pelo apron |
| Segurança | 4–6 | Dos 20 já contratados (item a) |
| **Total** | **15–17** | dos quais 4–6 já orçados |

## 9. Pendências

1. Aferir as dimensões do Ring 3 e **a distância entre o bordo oeste do Ring 3
   e o canto sudoeste do Hall 2** — é o número que translada todo o conjunto
   para os eixos coincidirem com as portas 2.7, 2.4 e 2.1.
2. Conciliar a numeração S1–S9 da prancheta com a numeração 2.1–2.23 da
   planta do RDS, que dão posições divergentes para as mesmas aberturas.
3. Submeter o pedido de **+181 separadores (~EUR 2.357)** para o Ring 3, e
   dimensionar à parte a necessidade do interior do Hall 2.
4. Cotar cobertura leve para os últimos 8–10 m de cada serpenteado.
5. Definir o arranjo da mesa receptora com o Cartório Eleitoral — **é o que
   determina se o Ring 3 chega a ser usado**.
