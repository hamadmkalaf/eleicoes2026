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

## 2. Portas do Hall 2 — o que a planta realmente diz

A planta `RDS_Hall_2_Floorplan_(1).pdf` **não usa rótulos S4/S5/S6**. Ela numera
as aberturas de 2.1 a 2.23. A fachada sul, que encara o Ring 3, tem sete
aberturas, medidas na página 2 e convertidas pela escala aferida (~9,0 pt/m,
conferida contra os 50,2 m de largura declarados):

| Porta | Distância do canto sudoeste | Papel proposto |
|---|---|---|
| **2.7** | 18,5 m | **ENTRADA A** |
| 2.6 | 22,3 m | saída |
| 2.5 | 24,4 m | saída |
| **2.4** | 28,5 m | **ENTRADA B** |
| 2.3 | 32,4 m | saída |
| 2.2 | 34,5 m | saída |
| **2.1** | 38,5 m | **ENTRADA C** |

**Achado que simplifica o desenho:** as três aberturas isoladas — 2.7, 2.4 e
2.1 — estão a **exatamente 10,0 m uma da outra**. Servem de entrada para os
três corredores, e os dois pares intermediários (2.6/2.5 e 2.3/2.2) ficam
livres como **saída dedicada**, entre as entradas. Entrada e saída deixam de se
cruzar sem custo nenhum.

Se os rótulos S4/S5/S6 vierem de outra prancheta, é preciso confirmar a
correspondência antes de fixar a sinalização.

## 3. Layout

```
                 HALL 2  —  fachada sul
     ┌──────┬────────┬──────┬────────┬──────┬────────┐
     │ 2.7  │ 2.6 2.5│ 2.4  │ 2.3 2.2│ 2.1  │        │
     │ ENTR.│  SAÍDA │ ENTR.│  SAÍDA │ ENTR.│        │
     └──▲───┴────────┴──▲───┴────────┴──▲───┴────────┘
        │  10,0 m       │   10,0 m      │
  ╔═════╪═══════════════╪═══════════════╪══════════════╗
  ║  ┌──┴───┐        ┌──┴───┐        ┌──┴───┐          ║
  ║  │╷╻╷╻╷ │        │╷╻╷╻╷ │        │╷╻╷╻╷ │          ║  27 m de
  ║  │║║║║║ │        │║║║║║ │        │║║║║║ │  reserva ║  serpenteado
  ║  │╹╵╹╵╹ │        │╹╵╹╵╹ │        │╹╵╹╵╹ │de flanco ║
  ║  │ ENTR.│  3,0 m │ ENTR.│  3,0 m │ ENTR.│          ║
  ║  │   A  │ egresso│   B  │ egresso│   C  │          ║
  ║  └──────┘        └──────┘        └──────┘          ║
  ║ ←────────── corredor de distribuição 2,5 m ────────╬══ ENTRADA
  ╚════════════════════════════════════════════════════╝   canto sudeste
                      39 m
```

O eleitor entra pelo **canto sudeste**, percorre o **corredor de distribuição**
no fundo (bordo sul) de leste para oeste, e é desviado para o serpenteado
correspondente à sua urna — **C** primeiro, depois **B**, depois **A**. Cada
serpenteado descarrega ao norte, direto na sua porta.

| Parâmetro | Valor |
|---|---|
| Corredor de distribuição (fundo) | 2,5 m de largura, todo o bordo sul |
| Profundidade útil do serpenteado | **27,0 m** (35 m menos 1,5 de recuo sul, 2,5 de corredor e 4,0 de descarga) |
| Balizas por corredor | **5**, de **1,40 m** de largura |
| Largura de cada bloco | 7,0 m |
| Vão de egresso entre blocos | 3,0 m |
| Fila por corredor | 135 m lineares |
| **Capacidade por corredor** | **270 pessoas** (0,50 m por pessoa) |
| **Capacidade dos três corredores** | **810 pessoas** |

**Por que 5 balizas e não mais.** O número tem de ser ímpar — entra-se pelo sul
e a última baliza precisa correr para o norte, onde estão as portas. E o
espaçamento de 10,0 m entre as portas limita o bloco a 7,0 m se quisermos
manter 3,0 m de egresso entre blocos vizinhos. Com 7 balizas o bloco iria a
9,8 m e sobrariam 0,2 m — inviável. **5 é o máximo que a geometria das portas
permite.** Os ±15% de incerteza na largura do Ring 3 não mudam isso, porque a
restrição vem das portas, não do terreno.

**Reserva de flanco.** Os três blocos ocupam 27 m dos 39 m. As faixas laterais
(~12 m × 27 m) ficam como **retenção aberta, sem balizas**, sob marshals, para
absorver surto acima de 810: cerca de **490 pessoas** a 1,5 pessoa/m². Só se
abre quando os serpenteados encherem.

**Capacidade total do Ring 3: ~810 estruturadas + ~490 de flanco = ~1.300.**

## 4. Necessidade de separadores de barreira

Um serpenteado de *n* balizas precisa de *n+1* corridas de separador: as duas
externas correm a profundidade inteira, e as internas param a 1,40 m de uma das
pontas para abrir o retorno.

| Componente | Cálculo | Metros |
|---|---|---|
| Externas dos 3 blocos | 3 × 2 × 27,0 m | 162,0 |
| Internas dos 3 blocos | 3 × 4 × (27,0 − 1,40) m | 307,2 |
| Corredor de distribuição (dois lados, menos 3 vãos de acesso) | — | 57,5 |
| Garganta de entrada no canto sudeste | — | 10,0 |
| Descarga: 3 canais × 2 lados × 6 m | — | 36,0 |
| **Total** | | **~573 m** |

Ao módulo já contratado (100 separadores = 200 m, item d do orçamento):

> **~573 m ≈ 286 separadores de 2 m.**
> Disponíveis hoje: **100**. **Faltam 186 unidades.**
> Ao custo unitário já praticado (EUR 1.303,00 ÷ 200 m = **EUR 6,51/m**):
> **~EUR 2.430**.

E isso consome **todo** o estoque atual no Ring 3, sem sobra para o interior do
Hall 2. Se o Hall 2 também precisar de unifila, o pedido cresce na mesma
proporção.

**Alternativa de menor custo, para registro:** com 3 balizas por corredor a
barreira cai para ~414 m (207 unidades, ~EUR 1.390), mas a capacidade
estruturada cai para **486 pessoas** — insuficiente em qualquer cenário serial.
Cada baliza adicional por corredor custa ~53 m de barreira (~27 unidades,
~EUR 172) e rende 162 pessoas. É o metro quadrado mais barato do plano.

## 5. O Ring 3 comporta a fila prevista?

Da coluna FILA TOTAL de `scripts/simula_fluxo.py`, comparada à capacidade do
Hall 2 (~1.000–1.200 em fila interna) somada às ~1.300 do Ring 3:

| Arranjo da mesa | Fila total no pico | Cabe? |
|---|---|---|
| Dois cadernos em paralelo, qualquer t_id | 0 | Sim — o Ring 3 nem abre |
| Pipeline, t_id 55 s | 439 | Sim, só no Hall 2 |
| Serial, t_id 45 s | 1.058 | Sim |
| Serial, t_id 55 s | 1.637 | Sim, com flanco aberto |
| Serial, t_id 65 s | 2.240 | No limite |
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
de 1,40 m acomodam cadeira de rodas, mas 27 m de serpenteado são 135 m de
percurso — inaceitável para quem tem prioridade legal.

## 8. Equipe

| Função | Nº | Observação |
|---|---|---|
| Coordenador do Ring 3 | 1 | Decide abertura do flanco e ritmo de liberação |
| Agentes de pré-triagem (garganta sudeste) | 3 | Entregam o cartão de roteamento; gargalo potencial — dimensionar para o pico |
| Marshals de corredor | 3 | 1 por serpenteado |
| Marshals de descarga | 3 | 1 por porta, em contato com o interior do Hall 2 |
| Agente de acessibilidade | 1 | Rota prioritária pelo apron |
| Segurança | 4–6 | Dos 20 já contratados (item a) |
| **Total** | **15–17** | dos quais 4–6 já orçados |

## 9. Pendências

1. Aferir as dimensões do Ring 3 e **a distância entre o bordo oeste do Ring 3
   e o canto sudoeste do Hall 2** — é o número que translada todo o conjunto
   para os eixos coincidirem com as portas 2.7, 2.4 e 2.1.
2. Confirmar a correspondência entre os rótulos S4/S5/S6 e as aberturas
   2.7/2.4/2.1 da planta do RDS.
3. Submeter o pedido de **+186 separadores (~EUR 2.430)**.
4. Cotar cobertura leve para os últimos 8–10 m de cada serpenteado.
5. Definir o arranjo da mesa receptora com o Cartório Eleitoral — **é o que
   determina se o Ring 3 chega a ser usado**.
