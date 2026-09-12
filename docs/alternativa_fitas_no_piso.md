# Entrada no RDS Hall 2: triagem central × fitas no piso

Documento de discussão. Compara a organização de entrada prevista no esboço
atual (`PLANO COM FLUXOS MELHORADO.png`) com a sugestão de um colega:
eliminar o ponto de triagem no meio do salão e levar o eleitor da porta
direto à sua mesa por fitas no piso com sinalização.

Os números vêm de `scripts/modelo_fluxo_entrada.py`, que lê
`saidas/dados.json` (28 urnas, 16.794 aptos) e grava
`saidas/fluxo_entrada_comparacao.{md,json,html}` e as plantas
`saidas/fluxo_hub.svg` e `saidas/fluxo_fitas.svg`. Todas as premissas estão
no bloco `PREMISSAS` do script e são marcadas como tais aqui.

## 1. As duas organizações

| | HUB (esboço atual) | FITAS (sugestão) |
|---|---|---|
| Onde o eleitor descobre a mesa | no hub, perguntando à equipe | antes da porta: painel "seção → mesa" e, para quem não sabe, balcão de apoio fora da porta |
| Quem faz a triagem | equipe do Posto, para 100% dos eleitores | o próprio eleitor; equipe só para quem não sabe a seção |
| Guia física até a mesa | corredor de unifila até o hub; depois indicação verbal + banner | fita colorida no piso da porta até a zona; dentro da zona, número alto na mesa |
| Onde a fila de triagem se forma | no corredor, dentro do salão (buffer ≈ 42 pessoas por porta) | fora da porta, no pátio do RDS |
| Ponto único de falha | os dois hubs | o painel "seção → mesa" e a comunicação prévia |
| Material específico | banners (já contratados, EUR 1.961) + 200 m de unifila (já contratados) | fita de piso (≈ EUR 100–300, premissa) + placas numeradas de mesa + painel de consulta por porta |

A sugestão literal ("uma fita por mesa") não é executável: 28 linhas
saindo de uma porta formam um feixe de quase 3 m de largura, não há 28
cores distinguíveis e ninguém segue a linha certa numa multidão. A versão
que modelamos usa **6 troncos por zona (3 por porta)**, cada tronco com uma
cor, e numera as mesas de 1 a 28 em sentido horário. O eleitor precisa
guardar duas informações na porta: cor da zona e número da mesa.

## 2. O que o modelo diz

Base comum: 11.416 comparecentes esperados (74% Dublin, 50% interior, taxas
de 2022), 9 h de votação, fator de pico 1,5 → 31,7 chegadas/min no pico,
15,9/min por porta. Premissa central: 25% dos eleitores chegam sem saber a
própria seção; quem sabe leva 8 s para ser apontado, quem não sabe leva 45 s
de consulta.

| Indicador | HUB | FITAS |
|---|---|---|
| Chegadas na triagem no pico, por porta | 15,9/min (todos) | 4,0/min (só quem não sabe) |
| Triadores por porta/hub para a fila não explodir | 5 | 3 |
| Triadores por porta/hub com folga (ocupação < 80%) | 6 | 4 |
| Total de triadores nas duas portas, com folga | 12 | 8 |
| Caminho médio porta → mesa | 37 m | 26 m |
| Cruzamentos entrada × saída com a saída no meio da parede sul | 451 | 186 |
| Cruzamentos entrada × saída usando as saídas laterais (portas 2.8/2.9 e 2.22/2.23) | 70 | 70 |

Três leituras:

**O hub é um servidor obrigatório em série para 100% do fluxo.** Com 4
pessoas por hub a ocupação passa de 100% e a fila cresce sem limite na hora
de pico; com 5 estabiliza mas com 79% de chance de esperar; só com 6 por
hub (12 no total) a espera fica desprezível. O corredor de 21 m absorve
cerca de 42 pessoas; a partir daí a fila transborda para a porta e o pátio,
e o hub passa a comandar o ritmo de entrada do salão inteiro.

**As fitas não eliminam a triagem; movem-na para antes da porta e reduzem-na
a uma fração.** A economia de pessoal é real mas menor do que parece (8 em
vez de 12), e depende inteiramente da fração que não sabe a seção. A tabela
de sensibilidade é o dado que decide:

| Não sabe a seção | HUB, por hub | FITAS, por porta |
|---|---|---|
| 10% | 4 | 2 |
| 25% | 6 | 4 |
| 40% | 8 | 6 |
| 60% | 10 | 9 |

A 60% as duas organizações custam o mesmo em pessoal, e a de FITAS é pior,
porque a fila de apoio se forma na rua e não num corredor coberto. Ou seja:
**a sugestão só vale a pena se o plano de comunicação conseguir que a
maioria chegue sabendo a seção** (e-Título com print, post "confira sua
seção antes de sair de casa", consulta pelo nome na fila externa).

**O ganho mais robusto está fora da disputa hub × fitas: a saída.** Com a
saída no meio da parede sul, entre A e B, quem sai de qualquer mesa atravessa
o leque de quem entra: 451 pares de trajetos em conflito no HUB, 186 no
FITAS. Mandando a saída para as portas laterais do RDS (2.8/2.9 a oeste,
2.22/2.23 a leste), ambos caem a 70 e o miolo do salão deixa de ser
cruzado em contrafluxo. Isso vale para qualquer das duas organizações e
custa uma placa e um segurança por porta.

Achado lateral: as posições do esboço dão 12 mesas ao lado A e 16 ao lado
B. Mesmo mandando as urnas mais cheias para A, a porta B recebe 55% do
fluxo (6.305 contra 5.111 esperados). Vale mover duas posições do lado
leste para o lado oeste, ou rotular as portas de forma que as filas
externas se equilibrem.

## 3. Organização no dia, lado a lado

### HUB
- **Antes da porta:** segurança separa a fila em A e B (critério: número da
  mesa, informado por painel na fila).
- **Corredor:** unifila até o hub; sem parada.
- **Hub:** 5–6 pessoas por hub em pé, com lista impressa seção → mesa e
  consulta por nome para quem não sabe; apontam a mesa. Precisam de voz,
  banner alto atrás de si e revezamento (9 h em pé falando).
- **Dispersão:** o eleitor atravessa até 25 m de piso aberto sem guia
  física, cruzando quem sai. Precisa de 1–2 "orientadores volantes" no
  miolo.
- **Falhas típicas:** hub sobrecarregado bloqueia a porta; eleitor esquece
  a indicação no meio do caminho e volta ao hub (retrabalho não modelado);
  aglomeração no centro do salão dificulta a passagem de quem sai.

### FITAS
- **Antes da porta:** painel grande "SUA SEÇÃO → COR E NÚMERO DA MESA" (51
  linhas, ordenadas por seção; as 23 seções agregadas apontam para a mesa da
  principal). Balcão de apoio com 3–4 pessoas por porta, **na fila externa
  e não na porta**, consultando por nome quem não sabe a seção: o tempo de
  consulta é absorvido pela espera que já existe.
- **Porta:** o eleitor entra sabendo "verde, mesa 15". Segurança na porta
  só confere que ele está na porta certa.
- **Piso:** 3 fitas coloridas por porta, cada uma para uma zona; ao chegar
  na zona, o eleitor segue a fita ao longo da parede até o número.
- **Mesa:** placa numerada alta (acima da cabeça, visível por sobre a fila)
  na cor da zona. Os banners já contratados servem para isso.
- **Miolo do salão:** vazio, exceto pela fita. 1–2 orientadores volantes
  por lado para quem perde a linha.
- **Falhas típicas:** eleitor que não leu o painel entra sem saber para onde
  ir (o orientador volante resolve, mas se forem muitos vira um hub
  informal); fita escondida sob a multidão nos trechos onde a fila da mesa
  invade o piso; fita solta ou levantada pelos cabos elétricos que o
  eletricista vai passar pelo piso (validar com o RDS o tipo de piso e a
  fita permitida).

## 4. Efeitos de segunda e terceira ordem

- **HUB, 2ª ordem:** a fila da triagem é interna e visível, o que dá a
  impressão de controle, mas concentra no centro do salão exatamente o
  público que mais precisa de espaço (idosos, crianças no colo). Se um hub
  trava, a única resposta é tirar gente das mesas para reforçá-lo.
- **HUB, 3ª ordem:** por ser o passo que dita o ritmo, o hub define a hora
  em que a última pessoa entra; um hub lento às 16h30 é a mesma coisa que
  fechar mesas de madrugada, o risco já descrito no contexto (seção 2.4).
- **FITAS, 2ª ordem:** desloca custo do dia para a comunicação prévia. Cada
  ponto percentual a mais de eleitores que chegam sabendo a seção tira gente
  do balcão de apoio. Isso transforma o plano de comunicação (pendência 3)
  de "divulgação" em peça operacional com meta mensurável.
- **FITAS, 3ª ordem:** o painel "seção → mesa" e as placas numeradas viram
  um artefato reutilizável para o 2º turno e para o funcionamento das MRVs
  (pendência 5): se as mesas têm número e cor, os cadernos e os mesários
  podem ser organizados na mesma chave.
- **Ambas:** trocar a saída central por laterais reduz cruzamentos em
  75% no HUB e 60% no FITAS. É a decisão de maior efeito por euro.

## 5. Recomendação para a discussão

Não é "hub ou fitas": é **híbrido, com a triagem antes da porta**.

1. Adotar a lógica de zona por cor + número de mesa em qualquer cenário.
   Ela serve ao hub (o triador diz "verde 15" em vez de apontar) e às fitas.
2. Levar a consulta "não sei minha seção" para a fila externa, com 3–4
   pessoas por porta e listas por nome. Isso tira o pior do hub e é o que
   faz as fitas funcionarem.
3. Manter um hub **reduzido** (1–2 pessoas por porta) como rede de
   segurança para quem entra perdido, em vez de servidor obrigatório.
4. Fitas por zona no piso (6 troncos, ≈ 240 m, custo baixo) mais placas
   altas nas mesas. Validar com o RDS a fita e o piso.
5. Saída pelas portas laterais, não pela porta central.
6. Rebalancear as posições entre os lados A e B (hoje 12 × 16).

O que precisa ser medido antes de decidir: a fração de eleitores que sabe
a própria seção. Uma enquete simples nas redes do Posto ("você sabe sua
seção? abra o e-Título") ou a contagem na fila do 1º turno de 2022, se
houver registro, muda a tabela de sensibilidade de premissa para dado.
