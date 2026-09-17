# Plano de Voluntários de Apoio ao Fluxo — Eleições 2026, Dublin

Funções e efetivo dos voluntários que organizam o fluxo do eleitor desde a chegada à
RDS até a mesa, no 1º turno de 04/10/2026 (8h–17h).

Não cobre mesários, secretários de seção nem a segurança contratada — efetivos
distintos, contados à parte na seção 8.

---

## 1. Base numérica

| Parâmetro | Valor | Origem |
|---|---|---|
| Eleitores aptos | 16.794 | `saidas/dados.json` (CSV oficial do TSE) |
| Seções / urnas | 51 seções em 28 urnas | idem |
| Comparecimento esperado | **~11.400** (74% Dublin, 50% interior) | taxas de 2022, `contexto_eleicoes_dublin_2026.md` |
| Janela de votação | 8h–17h (9h) | idem |

Taxas de chegada: média de **21/min**; pico de **35–42/min** entre 10h e 14h
(**premissa**: fator de 1,7–2,0× sobre a média, não dado observado). Ocupação
simultânea de 800–1.200 pessoas no circuito.

Consequência que governa todo o desenho: **nenhum posto pode parar o eleitor.** A
sinalização atende o caso padrão; o voluntário atende a exceção, orçada em 10–20%.

---

## 2. A rota, em quatro trechos

Ver a geometria completa em `CLAUDE.md`.

1. **Rota do Eleitor** — do portão da RDS na via pública até o canto nordeste do
   Ring 3, passando pela lateral do Hall 2.
2. **Ring 3** — pátio de fila ao ar livre, 44 × 35 m. Entrada no canto nordeste,
   corredor de chegada de 3 m descendo pelo leste, trecho de fundo de 3 m
   distribuindo para as zonas **C (leste, a primeira), B (centro) e A (oeste, a mais
   distante)**. 23 raias por zona; a fila sobe e a cabeça fica no topo.
3. **Apron** — 14 m pavimentados entre a cabeça das filas e a fachada sul do Hall 2.
4. **Hall 2** — salão de votação. Portas **S4/A, S5/B, S6/C** e **S7 preferencial**;
   saídas S2 e S8. Mesas nas paredes oeste (A), norte (B) e leste (C).

A letra da zona acompanha o eleitor da fila até a parede. É a única informação que
ele precisa reter, e é o que toda locução e toda sinalização devem repetir.

---

## 3. Quadro de postos

A lista operacional — onde cada posto fica, o que faz e o que não faz — está em
**`lista_postos.md`**, que é a fonte única desses números e o documento que vai para
o briefing. Resumo por trecho da rota:

| Trecho | Postos | Pico | Fora do pico |
|---|---|---|---|
| Rota do Eleitor | RE1 a RE5 | 13 | 8 |
| Ring 3 | R1 a R4 | 11 | 8 |
| Apron e portas | A1, A2 | 4 | 4 |
| Hall 2 | H1, H2, H3 | 8 | 6 |
| Transversais | T1, T2 | 6 | 5 |
| **Subtotal** | | **42** | **31** |
| Reserva flutuante (15%) | | 6 | 5 |
| **Em operação** | | **48** | **36** |

O posto **H3** — uma pessoa em cada uma das três mesas mais movimentadas — é o mais
recente e o único dentro do salão que fica parado numa mesa. Justifica-se pela
distância entre a primeira e a quarta colocadas: 3313, 3315 e 3322 esperam 590, 588 e
586 comparecentes, contra 492 da seguinte, e são as três com serpentina interna de 20
prevista na planta. Uma em cada zona.

---

## 4. Efetivo

Carga estimada: ~410 pessoas-hora.

**Recomendado: 60 escalados, 69 recrutados.**

| Bloco | Pessoas | Horário |
|---|---|---|
| Núcleo (inclui os 4 coordenadores, que não rodam) | 36 | 7h30–17h45 |
| Reforço de pico | 12 | 9h30–14h30 |
| Rendição da tarde | 12 | 12h30–17h45 |

Cobre 48 no pico e 36 fora dele, com a rendição liberando pausas reais à tarde.
Recrutar 69 absorve 10–15% de ausência no dia.

Briefing: 30 min on-line na semana anterior, com o mapa das zonas, e 45 min
presenciais às 7h do dia 4, por setor, com o coordenador setorial.

---

## 5. Regras de operação

**Ninguém verifica nada na porta.** Com uma porta por zona, cada uma recebe 12–14
pessoas/min no pico — um vão de 1 m escoa isso sem dificuldade, desde que ninguém
pare nele. Qualquer pergunta feita no batente transforma a porta no gargalo da zona
inteira, e o efeito volta pelo apron até o Ring.

**O apron é travessia, não estoque.** São 14 m sem raias entre a cabeça das filas e
as portas. Se as portas engasgarem e o Ring continuar liberando, o apron vira
aglomeração ao ar livre sem estrutura de fila. Por isso R4 existe: libera em lote,
e só quando a porta está andando.

**Voluntário orienta, não decide.** Não toca em documento, não confere título, não
diz a ninguém se pode votar — identificação é monopólio legal do mesário.

**Neutralidade.** Colete neutro, sem cor partidária, sem discussão política, como
condição de aceitação e por escrito. Voluntário com camiseta de campanha na porta é
boca de urna e vira problema do Posto.

**Encerramento às 17h.** Art. 153 do Código Eleitoral: distribuem-se senhas a todos
os presentes, começando pelo último da fila. O ato é do mesário; **R4 marca
fisicamente o fim da fila** em cada zona às 17h00, com o coordenador setorial
presente e registro de horário. Se a fila tiver transbordado para fora do Ring, quem
marca o fim é RE1.

---

## 6. Achados da planta

**A zona A é a mais distante e a mais cheia.** Quem chega pelo canto nordeste alcança
C primeiro e A por último, depois de percorrer os 44 m do trecho de fundo. A zona A é
também a de maior comparecimento esperado (3.860). Consequência prática: a
sinalização de A tem de começar no canto nordeste, não na boca da zona, e o trecho de
fundo carrega o tráfego de A e B — cerca de dois terços dos eleitores — em 3 m de
largura. É o segundo ponto de congestionamento mais provável, depois das portas.

**A distribuição de urnas por zona está equilibrada** — e melhor do que a proposta
que este documento trazia antes, que fica descartada. Comparecimento esperado de
3.860 / 3.755 / 3.802 (spread de 2,8%), com uma das três urnas grandes em cada zona.
Nada a mexer.

**O Ring dá cerca de meia hora de fôlego.** 23 raias × (12,23 + 14,14 + 12,23) m =
**888 m de fila**. A 0,5–0,8 m por pessoa, isso comporta **1.100 a 1.800 pessoas**.
Contra um pico de ~2.300 chegadas/h, o pátio cheio representa **30 a 45 minutos** de
atraso absorvido. Passando disso, a fila sai pelo canto nordeste e volta para dentro
do recinto da RDS — que é exatamente quando RE1 e RE2 deixam de orientar e passam a
gerir fila.

**A unifila orçada não cobre o Ring.** As 23 raias exigem ~24 corridas de barreira
por zona: 24 × 38,60 m ≈ **926 m**. O orçamento tem **200 m** (100 separadores,
EUR 1.303). Faltam da ordem de 700 m, a menos que o gradil do Ring já traga
estrutura interna. É questão a fechar antes do orçamento final (`PENDENCIAS` item 2)
— sem raias, o pátio não é fila, é aglomeração.

**Todo o Ring é descoberto.** Com o salão de votação no Hall 2 e a fila ao ar livre,
até 1.800 pessoas podem estar na chuva em 4 de outubro. Duas mitigações a decidir:
cobertura ao menos da cabeça das três filas e do circuito preferencial; e um
**protocolo de chuva** que use o miolo vazio do Hall 2 como reserva de fila,
recuando a serpentina para dentro e abrindo as portas livres (O2, N2, H1). O miolo
do salão é o único abrigo de escala disponível.

---

## 7. Decisões de 16/09/2026

| Função proposta | Decisão | Efeito |
|---|---|---|
| Balcão "Onde eu voto?" | Mantido. **A lista nominal não existe e pode não existir.** | RE4 fica no quadro; sem a lista, atende por consulta ao e-Título e por conhecimento das faixas de seção, com eficácia menor. Obter a lista é a melhoria de maior retorno por euro gasto. |
| Triagem preferencial | Mantida, **1 pessoa** | RE5 = 1. A porta S7 continua precisando de A2, que também faz a escolta: são 2 pessoas no circuito preferencial, uma delas guardando uma porta que ficaria aberta e sem ninguém. |
| Fluxo de saída | **Opcional** | Nenhum posto alocado. Defensável: S2 e S8 são saídas próprias, e o circuito já é unidirecional por construção. Reativar se a saída acumular ou no encerramento. |
| Encerramento às 17h | **Acumulado** | Sem posto próprio: R4 em cada zona, ou RE1 se a fila tiver transbordado. |
| Contagem de fluxo | **Descartada** | Fora do quadro. Se depois quiserem o dado para o 2º turno, qualquer coordenador anota o horário de hora em hora sem custo. |
| Coordenação setorial | **Já contada** | T1 = 4, sem acréscimo. |

Em 17/09 o Posto acrescentou **três voluntários para as mesas mais movimentadas** —
posto H3, um por mesa em 3313, 3315 e 3322. Não contradiz a diretriz original de não
colocar voluntário na frente das mesas: essas três têm serpentina própria de 20
lugares na planta, e o H3 organiza essa fila ao lado do secretário de seção, não no
lugar dele. Efetivo sobe de 57 para 60 escalados.

---

## 8. Efetivos que não entram nesta conta

| Efetivo | Nº | Situação |
|---|---|---|
| Mesários | ~84 (28 × 3) + suplentes | Lista do TSE pendente (`PENDENCIAS` item 4) |
| Secretários de seção | 28 | 1 por urna. Os de 3313, 3315 e 3322 trabalham com o voluntário do posto H3 ao lado. |
| Segurança contratada | 20 + 1 na véspera | Orçado, EUR 6.774,84 |
| **Voluntários de fluxo** | **60** | `lista_postos.md` |

Total credenciado: ~190–200 pessoas.

---

## 9. Custo estimado do voluntariado

Estimativa, não orçamento cotado — `PENDENCIAS` item 2.

| Item | Cálculo | EUR |
|---|---|---|
| Coletes identificadores | 69 × 6 | 414 |
| Água e almoço | 69 × 12 | 828 |
| Rádios (aluguel, 12 aparelhos) | — | 250–400 |
| Impressões: listas, mapas de zona, pranchetas, crachás | — | 200 |
| **Total** | | **~1.700–1.850** |

Não inclui a barreira de fila faltante (§6), que é item de outra ordem de grandeza.

---

## 10. Pendências

1. **Barreira das raias do Ring** — ~926 m necessários contra 200 m orçados.
2. **Protocolo de chuva** e cobertura da cabeça das filas.
3. **Lista nominal** para o balcão RE4.
4. **Método de identificação do eleitor** (`PENDENCIAS` item 5). Caderno físico
   aumenta o tempo por eleitor, empurra fila para o Ring e torna RE4 crítico.
5. **Confirmar a expectativa de comparecimento** — o quadro da §3 é linear na taxa
   de chegada de pico.

---

## 11. Riscos de segunda e terceira ordem

- **Segunda ordem.** Triagem humana em excesso não elimina fila: empurra a fila para
  trás. Com o Ring descoberto, empurrar a fila para trás é empurrá-la para a chuva, e
  fila na chuva produz desistência — privação de voto que não aparece em nenhuma
  estatística de comparecimento (mesmo mecanismo já registrado em
  `contexto_eleicoes_dublin_2026.md` §2.4).
- **Terceira ordem.** Desordem na entrada circula em vídeo antes do fim da votação e
  vira questionamento sobre a condução do pleito no exterior. A sinalização
  (EUR 1.961 orçados) e o voluntariado são, nesse aspecto, mitigação de risco
  reputacional, não só de fluxo.

---

## Fontes

- Lista operacional dos postos: `lista_postos.md`.
- Eleitorado e agregação: `saidas/dados.json`, dos CSVs oficiais do TSE.
- Comparecimento, orçamento e histórico: `contexto_eleicoes_dublin_2026.md`.
- Geometria: plantas do Ring 3 e do Hall 2 de 16/09/2026, resumidas em `CLAUDE.md`.
- Encerramento e senhas: Código Eleitoral, art. 153.
