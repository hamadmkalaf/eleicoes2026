# Contexto — plano de voluntários de Dublin (sessões de 14 e 15/09/2026)

Registro do que foi pedido, decidido, calculado e deixado em aberto na
construção do plano de voluntários, para retomar depois sem reconstruir o
raciocínio. O plano em si está em `plano_voluntarios.md`.

---

## 1. O que foi pedido, em duas rodadas

**Rodada 1 (14/09).** "Quantifique a quantidade de voluntários necessários para
auxiliar as pessoas e faça um plano para alocação deles."

Resultado: modelo de headcount — 41 voluntários simultâneos no pico, 77 pessoas
distintas no dia em dois turnos mais reforço, ~100 a recrutar com 25% de
absenteísmo. Entregue no PR
[#21](https://github.com/hamadmkalaf/eleicoes2026/pull/21).

**Rodada 2 (15/09).** Três correções de escopo do usuário:

1. **Não dimensionar pessoas, e sim funções.** Recrutamento fica com o usuário.
2. **Marcar os pontos** onde os voluntários estarão, em três zonas: (1) rota do
   eleitor até o Ring 3; (2) no Ring 3; (3) dentro do Hall 2, sobre o desenho
   atual.
3. Salvar este contexto.

O modelo foi reescrito de headcount para **postos**. A camada de turnos,
absenteísmo e funil de recrutamento foi removida — está no histórico do git
(commit `2795987`) se voltar a ser necessária.

## 2. Fatos confirmados pelo usuário nesta rodada

| Questão | Resposta |
|---|---|
| O que é o Ring 3 no fluxo | **Área de espera a céu aberto** — o pulmão onde a fila se acumula antes das portas |
| Entrada no recinto | **Portão único na Merrion Road** |

Essas duas respostas são o que viabilizou a decisão de desenho da seção 4.

## 3. Fatos confirmados por fonte documental

- **Hall 2 = Shelbourne Hall**, 50,2 × 44,5 m, 2.238 m², pé-direito 7 m,
  2 × 250 A trifásico, porta de carga 4,87 × 3,73 m. Fonte: ficha técnica no
  `RDS_Hall_2_Floorplan_(1).pdf` do próprio repositório. **Isso fecha a
  pendência nº 1 do `contexto_eleicoes_dublin_2026.md`**, que pedia confirmar se
  o Hall 2 real batia com os 50 × 44,5 m usados nas simulações de layout. Bate.
- Os WC ficam **fora do salão**, num corredor lateral a oeste (planta do PDF).
- **Mesa Receptora de Votos (MRV) é a mesa**, não a urna: presidente, 1º e 2º
  mesários e secretários. O `contexto_eleicoes_dublin_2026.md` usa "MRV" como
  sinônimo de urna em vários pontos — leitura a corrigir, porque contamina o
  item 5 da `PENDENCIAS` ("funcionamento da MRV").
- **"Apoio logístico" é categoria formal** nomeada pela Justiça Eleitoral,
  distinta de mesário, "no número e nos períodos necessários". É sob essa figura
  que os voluntários deveriam ser nomeados.
- **O prazo de nomeação de mesários e apoio logístico das Eleições 2026
  terminou em 28/08/2026** — vencido. Pendência urgente com o Cartório.

Fontes: [TSE — prazo de nomeação](https://www.tse.jus.br/comunicacao/noticias/2026/Agosto/termina-nesta-sexta-feira-28-prazo-para-nomeacao-de-mesarios-e-apoio-logistico),
[TSE — mesas receptoras](https://www.tse.jus.br/comunicacao/noticias/2026/Abril/por-dentro-das-eleicoes-entenda-o-que-sao-e-como-funcionam-as-mesas-receptoras-de-votos),
[Resolução TSE nº 23.751/2026](https://www.tse.jus.br/legislacao/compilada/res/2026/resolucao-no-23-751-de-26-de-fevereiro-de-2026).
O domínio `tse.jus.br` está bloqueado pelo proxy da sessão: o conteúdo veio de
busca, o texto integral da resolução **não foi lido**.

## 4. A decisão de desenho desta rodada

**A triagem saiu da porta do Hall 2 e foi para dentro da fila do Ring 3.**

Antes: 8 postos de triagem nas entradas A e B, atendendo 28,5 eleitores/min com
utilização de 80%. Era o gargalo não paralelizável.

Agora: 4 postos móveis (G2–G5) que percorrem a serpentina, perguntam a seção,
entregam cartão de cor A/B e resolvem dúvida enquanto o eleitor já espera.

A queda de 8 para 4 não é mágica. Vem de duas coisas:

1. **Some a folga de utilização.** Ela só era necessária porque a fila de
   triagem na porta não tinha válvula de escape. Na fila do Ring 3, quem escapa
   da triagem é recuperado no nó de despacho (H3/H4) — falha suave.
2. **Interações, não pessoas.** Eleitor chega em dupla e em família; assumido
   1,5 eleitor por interação.

Consequência em cadeia: as portas A e B deixam de triar e passam a **dosar** —
só admitem enquanto houver fila útil dentro, empurrando a espera para o Ring 3,
que tem espaço. E o balcão de casos sai de dentro do salão para o Ring 3, fora
da fila.

## 5. Resultado

**36 postos no pico**: 6 na rota (R1–R6), 12 no Ring 3 (G1–G12), 18 no Hall 2
(H1–H18). Três grupos são calculados por vazão (triagem móvel, balcão de casos,
orientação de corredor); os outros 27 são posicionais.

Mapas: `saidas/postos_rota_ring3.png` (zonas 1 e 2, esquemático) e
`saidas/postos_hall2.png` (zona 3, marcado sobre o desenho de fluxo atual).

## 6. Premissas do modelo — e quais são frágeis

Todas em `PREMISSAS`, em `scripts/voluntarios.py`.

| Premissa | Valor | Origem | Confiança |
|---|---|---|---|
| Comparecimento Dublin / interior | 74% / 50% | taxas de 2022 | alta |
| Curva de chegada horária | pico de 15%/h entre 10h e 12h | **assumida** | **baixa — a mais frágil do modelo** |
| Fração que pede orientação | 60% | assumida | média |
| Tempo por triagem | 20 s | assumido | média |
| Eleitores por interação | 1,5 | assumido | média |
| Casos difíceis | 3% a 120 s | assumido | média |
| Utilização-alvo do balcão | 80% | teoria de filas | alta |
| Mesas por bloco de corredor | 3,5 (9 blocos em 30 posições) | geometria do desenho | alta |

Se aparecer a contagem horária de 2022 do posto, é a primeira coisa a
substituir.

## 7. Pendências abertas

1. **Nomeação de apoio logístico fora do prazo** — confirmar com o Cartório
   Eleitoral/ZZ. Muda a figura jurídica, não o número de postos.
2. **Geometria real do recinto do RDS.** `rds.ie` está bloqueado pelo proxy; o
   site map não pôde ser obtido. O mapa das zonas 1 e 2 tem topologia correta e
   proporções inventadas. Corrigir antes de virar sinalização.
3. **Capacidade do Ring 3** — número de baias da serpentina é ilustrativo.
4. **30 posições de mesa no desenho × 28 urnas na agregação do TSE.** Confirmar
   as duas sobrando; servem de reserva se uma urna falhar.
5. **Segundo portão para saída** — vale pedir ao RDS. Elimina o posto R6 e o
   cruzamento entre quem entra e quem sai.
6. **Abrigo de chuva no Ring 3** — não muda a contagem de postos, muda a
   prioridade de orçamento. 4 de outubro em Dublin, fila a céu aberto.

## 8. Mapa de arquivos

| Arquivo | O que é |
|---|---|
| `plano_voluntarios.md` | O plano: postos por zona, com os mapas |
| `scripts/voluntarios.py` | Modelo: premissas, cálculo por vazão, numeração dos postos |
| `scripts/postos_hall2.py` | Marca os postos sobre o desenho de fluxo atual |
| `scripts/postos_rota_ring3.py` | Desenha o esquemático das zonas 1 e 2 |
| `saidas/postos_voluntarios.{json,md}` | Tabela de postos gerada |
| `saidas/postos_hall2.png` | Mapa da zona 3 |
| `saidas/postos_rota_ring3.png` | Mapa das zonas 1 e 2 |
| `contexto_eleicoes_dublin_2026.md` | Contexto anterior: agregações, orçamento, layout |
| `PENDENCIAS` | Lista de tarefas do posto; este plano cobre parte dos itens 4 e 5 |

Os códigos dos postos são gerados pelo modelo, e os dois scripts de desenho
conferem os códigos que marcam contra o JSON — se o modelo mudar e o mapa não,
o desenho falha em vez de sair errado.
