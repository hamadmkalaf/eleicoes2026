# Plano base do Ring 3 — RDS Ballsbridge, 04/10/2026

Escopo deste documento: **apenas o Ring 3**. O plano geral da votação está
fora daqui; a análise que o sustenta está em `saidas/analise_gargalos.md`.

Premissas fixadas: 28 urnas / 28 mesas (1:1), identificação por **caderno
físico**, espaço contratado **Hall 2 + Ring 3 sem cobertura**.

---

## 1. Dimensões adotadas

Estimadas por fotogrametria sobre imagem aérea do Google Maps, com escala
ancorada em feições de solo (carros, vagas, largura da R118, copas), não em
telhados — a imagem é oblíqua e telhado de prédio alto não coincide com sua
projeção no solo. Escala apurada: **0,15 m/px**, com quatro aferições
independentes convergindo.

| Área | Dimensão | Superfície | Uso previsto |
|---|---|---|---|
| **Ring 3 — núcleo de areia** | ~39 × 35 m | **~1.365 m²** | Retenção de fila |
| Ring 3 — recinto até a linha de árvores | ~52 × 50 m | ~2.600 m² | Circulação perimetral |
| Apron pavimentado (fachada sul do Hall 2 ↔ árvores) | ~60 × 14 m | ~850 m² | Rota acessível e triagem |

Incerteza: **±10–15% nas dimensões lineares, ±25% na área**. Suficiente para
dimensionar; insuficiente para contrato. Aferir com a ferramenta "Medir
distância" do Google Maps, ou pedir a planta do recinto ao RDS.

Distância a percorrer do limite norte do Ring 3 às portas do Hall 2: **20–35 m**.

## 2. O que o Ring 3 é, e o que não é

**É** pulmão de fila, ponto de pré-triagem e área de retenção antes da entrada.

**Não é** área de votação. Nenhuma urna, nenhuma mesa receptora e nenhum
caderno vai para fora do Hall 2 — piso de areia, sem cobertura, sem energia
protegida e sem controle de acesso não comportam ato eleitoral.

## 3. Quanta fila o Ring 3 precisa absorver

Da coluna FILA TOTAL de `scripts/simula_fluxo.py` (pessoas simultaneamente em
espera nas 28 urnas, no pico):

| Arranjo da mesa | t_id 45 s | t_id 55 s | t_id 65 s | t_id 75 s |
|---|---|---|---|---|
| Serial (fila única) | 1.058 | 1.637 | 2.240 | 2.974 |
| Pipeline | 91 | 439 | 935 | 1.517 |
| **Dois cadernos em paralelo** | **0** | **0** | **0** | **0** |

O Hall 2 comporta internamente **~1.000–1.200 pessoas em fila** (2.238 m² menos
~378 m² de estações, ~150 m² de sala de transmissão e WC, e ~30% de corredores
de saída, a ~1,0 pessoa/m²).

**Consequência que decide o plano:** o Ring 3 é dimensionado para ~1.050
pessoas (item 4). Somado ao Hall 2, o sítio comporta ~2.250. No arranjo serial
com caderno lento a fila chega a **2.974 — não cabe no RDS** e transborda para
a Merrion Road. Isso deixa de ser logística e vira ordem pública.

**O Ring 3 não salva o arranjo serial. Só o arranjo de dois cadernos em
paralelo salva.** O Ring 3 é a apólice contra o erro de previsão, não a
solução do gargalo.

## 4. Layout base — quatro currais, não serpentina

Serpentina com barreiras é ineficiente aqui: cada metro de fila comporta ~2
pessoas, então os 200 m de unifila já orçados (item d, EUR 1.303) renderiam
~200 pessoas em 1.365 m² de área disponível. Desperdício de espaço.

Desenho adotado — **currais marshalados com liberação em lotes**:

```
                    ↑ Hall 2 (portas A / B)  — 20 a 35 m
        ┌───────────────────────────────────┐
        │   3 m livre no perímetro          │   funil de
        │  ┌──────────┬─┬──────────┐        │   liberação
        │  │  CURRAL  │ │  CURRAL  │        │      ↑
        │  │    A     │4│    B     │ 12,5 m │   ═══════
        │  │ 14,5 m   │m│  14,5 m  │        │
        │  ├──────────┼─┼──────────┤ ← 4 m  │
        │  │  CURRAL  │ │  CURRAL  │        │
        │  │    C     │ │    D     │ 12,5 m │
        │  └──────────┴─┴──────────┘        │
        │        espinha central 4 m        │
        └───────────────────────────────────┘
             33 m úteis  (de 39 m brutos)
```

| Parâmetro | Valor |
|---|---|
| Área bruta | 39 × 35 m = 1.365 m² |
| Faixa livre de perímetro | 3 m em todo o contorno |
| Área de trabalho | 33 × 29 m = 957 m² |
| Espinha central (N–S, para liberação e emergência) | 4 m |
| Corredor transversal (E–O) | 4 m |
| Área líquida em currais | **725 m²** (4 × ~181 m²) |
| **Capacidade de projeto** (1,5 pessoa/m²) | **~1.050 pessoas** (~270 por curral) |
| Teto absoluto (2,0 pessoa/m²) | ~1.450 pessoas — só com marshal em cada curral |

Nunca planejar acima de 2 pessoas/m² ao ar livre com liberação em lotes.

**Alocação dos currais por seção**, para que a fila já chegue ordenada: um
curral por grupo de urnas, com as três urnas críticas (**3313, 3322, 3315**)
distribuídas em currais diferentes — concentrá-las num só cria um ponto único
de congestionamento na liberação.

## 5. Restrição de material — o gargalo real do layout

Barreira necessária: espinha (2 × 29 = 58 m) + transversal (2 × 33 = 66 m) +
funil de liberação (~30 m) = **~154 m**.

Disponível: **200 m** (100 separadores, item d do orçamento). Sobram 46 m para
todo o interior do Hall 2 — **insuficiente**.

A linha de árvores e o meio-fio já delimitam o perímetro externo do Ring 3, o
que dispensa barreira ali. Ainda assim:

> **Pedido orçamentário específico: +200 m de unifila (~100 unidades).** Ao
> custo unitário já contratado (EUR 1.303 / 200 m = EUR 6,51/m), são **~EUR
> 1.300** — 8% do orçamento revisado de EUR 15.703,32, e o item mais barato do
> plano inteiro em relação ao risco que remove.

## 6. Chuva sobre areia — o risco dominante

Outubro é o mês mais chuvoso de Dublin: **76–79 mm**. O número de dias de
chuva diverge conforme a fonte e o limiar adotado — **12 dias** pelas normais
de 30 anos (1991–2020, limiar ≥1 mm) até **17–20 dias** em fontes com limiar
mais frouxo. Traduzindo para o dia 4: probabilidade de chuva de **~40% a
~65%**, a depender do critério. Registre-se que as fontes não são
metodologicamente comparáveis entre si.

Areia molhada com 1.000 pessoas em cima gera três problemas, em ordem de
gravidade:

1. **Lama arrastada para dentro do Hall 2**, sobre piso onde correm os pontos
   elétricos das urnas (item b, EUR 5.387,40). Risco elétrico e de queda junto
   ao equipamento de votação.
2. **Superfície escorregadia** para uma multidão em movimento de lote.
3. **Inacessibilidade** — areia já é intransitável para cadeira de rodas seca;
   molhada, é intransitável para muita gente.

Mitigações, em ordem de custo:

- **Mínimo indispensável:** piso de proteção (trackway) na espinha central e
  no funil de liberação — ~116 m² + funil. É a rota por onde todos passam.
- **Barreira de limpeza:** tapete de retenção de sujeira nos 3 m antes de cada
  porta do Hall 2, sobre o apron pavimentado.
- **Alternativa em tempo chuvoso:** não abrir a areia. Operar a retenção só no
  **apron pavimentado** (~850 m² brutos; com 3 m livres e a fachada do Hall 2
  de um lado, sobram ~400–500 pessoas de capacidade). É menos da metade da
  capacidade do Ring 3, o que reforça o item 3: sem o arranjo de cadernos
  paralelos, a operação não fecha em dia de chuva.

## 7. Acessibilidade e atendimento prioritário

São **211 eleitores com 60+ anos e 85 com deficiência declarada** em toda a
zona — ~296 pessoas ao longo de 9 horas, ~33 por hora no pico. Volume trivial,
desde que roteado corretamente.

**Nenhum eleitor prioritário passa pela areia, com chuva ou sem.** Rota
dedicada pelo apron pavimentado, do ponto de desembarque direto à porta do
Hall 2, com 1 agente designado. Sinalização própria (item c do orçamento).

## 8. Fluxo e regra de liberação

1. **Chegada** → triagem na entrada norte do Ring 3: o agente identifica a
   seção do eleitor (e-Título ou documento) e entrega **cartão de roteamento**
   com seção, urna e porta.
2. **Curral** conforme o cartão.
3. **Liberação em lotes** pela espinha central, sob comando do marshal de
   liberação, calibrada para manter a fila interna do Hall 2 em torno de
   **800 pessoas** — abaixo da capacidade de ~1.000–1.200, com margem.
4. **Apron** → portas A / B.

A pré-triagem converte tempo morto de fila em roteamento útil e resolve
estruturalmente o problema levantado na seção 4 do contexto (fila de cabine
movimentada contaminando cabine calma). O risco a vigiar é a própria triagem
virar gargalo: dimensioná-la para o pico, não para a média.

## 9. Equipe do Ring 3

| Função | Nº | Observação |
|---|---|---|
| Coordenador do Ring 3 | 1 | Decide abertura, ritmo de liberação e fechamento |
| Marshals de curral | 4 | 1 por curral |
| Agentes de pré-triagem | 3 | Dimensionar para o pico; é gargalo potencial |
| Marshals de liberação | 2 | No funil, em contato com o interior do Hall 2 |
| Agente de acessibilidade | 1 | Rota prioritária pelo apron |
| Segurança | 4–6 | Dos 20 já contratados (item a) |
| **Total** | **15–17** | dos quais 4–6 já orçados |

## 10. Estacionamento — decisão que não pode ser adiada

O Ring 3 hoje estaciona ~20–25 carros no perímetro. Convertê-lo em retenção de
fila elimina essas vagas, justamente quando **4.213 eleitores (25% da zona)
residem fora de Dublin** e chegam de carro.

**A conversão não pode ser feita às 11h — os carros já estarão lá.** É decisão
de véspera, ou no máximo às 07h00 do dia 4, e depende de dois fatores:

| Condição | Uso do Ring 3 |
|---|---|
| Arranjo de cadernos paralelos aprovado **e** tempo seco | Estacionamento (fila prevista: zero) |
| Arranjo paralelo aprovado **e** chuva | Estacionamento; apron como reserva |
| Arranjo serial ou pipeline, qualquer tempo | **Retenção de fila** — sinalizar e vedar ao estacionamento desde D-1 |

## 11. Pendências

1. Aferir as dimensões do Ring 3 (Google Maps "Medir distância" ou planta do RDS).
2. Confirmar com o RDS que o Ring 3 está de fato incluído no contrato e que a
   vedação ao estacionamento em D-1 é possível.
3. Obter cotação de trackway para espinha e funil (~150 m²).
4. Submeter o pedido de +200 m de unifila (~EUR 1.300).
5. Definir o arranjo da mesa receptora com o Cartório Eleitoral — **é o que
   determina se o Ring 3 será usado ou ficará como estacionamento**.
