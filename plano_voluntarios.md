# Plano de voluntários — Dublin, 1º turno de 04/10/2026

Quantos voluntários o posto precisa para auxiliar os eleitores no RDS Hall 2,
onde alocá-los e como recrutá-los a tempo. Os números saem de
`scripts/voluntarios.py`, que lê o eleitorado real (`saidas/dados.json`) e o
converte em fluxo por hora; as tabelas completas estão em
`saidas/dimensionamento_voluntarios.md`.

## Resultado em uma linha

**41 voluntários simultâneos no pico** (10h–12h), **77 pessoas distintas no
dia** em dois turnos com um reforço de pico, e **~100 a recrutar** para
absorver 25% de absenteísmo. Dois cenários alternativos de premissa colocam a
faixa entre 56 e 96 pessoas no dia.

## 1. O que um voluntário pode fazer — e o que não pode

Esta é a restrição que estrutura o plano inteiro, e ela precede qualquer
cálculo.

A Mesa Receptora de Votos (MRV) é a **mesa**, não a urna: é composta por
presidente, 1º e 2º mesários e secretários, e cabe a ela receber o voto,
identificar o eleitor e manusear o caderno de votação. Quem faz isso são
mesários **nomeados pela Justiça Eleitoral**. Um voluntário do posto não
identifica eleitor, não manuseia caderno e não opera urna.

Existe, porém, uma categoria formal para o que este plano descreve: a Justiça
Eleitoral nomeia eleitores como **apoio logístico**, "no número e nos períodos
necessários", como pessoal auxiliar dos trabalhos eleitorais — função distinta
da de mesário. É sob esse enquadramento que os 77 devem ser nomeados.

> **Pendência urgente.** O prazo para os juízes nomearem mesários e apoio
> logístico das Eleições 2026 terminou em **28/08/2026** — já vencido na data
> deste plano. Antes de recrutar qualquer pessoa, é preciso confirmar com o
> Cartório Eleitoral/ZZ: (a) se o posto já tem apoio logístico nomeado e
> quantos; (b) se há nomeação complementar possível para seções no exterior;
> (c) se não houver, sob que figura os colaboradores do posto atuarão
> (colaborador consular sem vínculo com a Justiça Eleitoral), o que muda
> cobertura de seguro, direito a folga compensatória e crachá.
>
> Fontes: [TSE — prazo de nomeação de mesários e apoio logístico](https://www.tse.jus.br/comunicacao/noticias/2026/Agosto/termina-nesta-sexta-feira-28-prazo-para-nomeacao-de-mesarios-e-apoio-logistico)
> e [TSE — como funcionam as mesas receptoras de votos](https://www.tse.jus.br/comunicacao/noticias/2026/Abril/por-dentro-das-eleicoes-entenda-o-que-sao-e-como-funcionam-as-mesas-receptoras-de-votos).
> Conteúdo obtido por busca; o texto integral da
> [Resolução TSE nº 23.751/2026](https://www.tse.jus.br/legislacao/compilada/res/2026/resolucao-no-23-751-de-26-de-fevereiro-de-2026)
> não foi lido e deve ser conferido pelo Cartório.

Consequência prática: **todo voluntário trabalha fora da mesa**. O ganho que
ele entrega não é velocidade de votação — essa é limitada pelos mesários e
pela urna —, é impedir que o eleitor chegue à mesa errada, na fila errada, sem
documento, ou desista antes de chegar.

## 2. Base de cálculo

| Parâmetro | Valor | Origem |
|---|---|---|
| Eleitores aptos | 16.794 | CSV do TSE, 51 seções em 28 urnas |
| Comparecimento esperado | 11.418 (68%) | 74% dos domiciliados em Dublin, 50% do interior (taxas de 2022) |
| Janela de votação | 8h–17h | nota verbal |
| Pico de fluxo | 1.713 eleitores/h = 28,5/min | curva de chegada assumida, pico entre 10h e 12h |
| Fila já formada às 8h | ~411 pessoas | premissa: 45% do fluxo da 1ª hora chega antes da abertura |

Os 11.418 usam a mesma base de aptos e as mesmas taxas de 2022 para todos os
cenários — comparabilidade que o `contexto_eleicoes_dublin_2026.md` já
recomendava explicitar.

**A curva de chegada é a premissa mais frágil do modelo.** Não há série
histórica hora a hora do posto. Se o comparecimento for mais concentrado do
que os 15%/hora assumidos no pico, as funções sensíveis a fluxo (triagem,
consulta, prioritário) sobem proporcionalmente; as posicionais (corredor,
runner, coordenação) não mudam. Se o posto tiver a contagem horária de 2022,
substituí-la em `PREMISSAS["curva_chegada"]` e rodar o script de novo é a
primeira coisa a fazer com este plano.

## 3. Dimensionamento por função

Pico simultâneo, cenário base. Cada número vem de um critério explícito, não
de arredondamento.

| Função | Pico | Critério |
|---|---|---|
| Fila externa e recepção | 8 | 1 por 60 pessoas em fila; dimensionado pela fila de abertura (~411), não pelo pico de fluxo |
| Triagem nas entradas A e B | 8 | 60% dos eleitores pedem orientação falada, 20 s cada, utilização de 80% |
| Balcão de consulta e casos | 5 | 8% dos eleitores (seção não localizada, título, dúvida), 90 s cada |
| Orientação de corredor | 8 | 1 por cluster de 3–4 urnas |
| Atendimento prioritário | 3 | 10% do fluxo é prioritário; 60 atendimentos/hora por apoio |
| Apoio às mesas (runner) | 4 | 1 por 7 urnas |
| Saída e pós-voto | 2 | posto fixo no EXIT |
| Coordenação | 3 | 1 coordenador-geral + 1 supervisor por entrada |
| Reserva | 6 | 15% para pausas, atrasos e substituição |
| **Total no pico** | **41** | |

Dois números merecem atenção. O primeiro é a **fila externa às 8h**: é o único
momento em que a demanda é de contenção de multidão na Merrion Road, não de
atendimento — 8 pessoas na calçada às 7h45 valem mais que 8 pessoas dentro do
salão. O segundo é a **triagem**: 8 postos de triagem a 20 s por eleitor é o
que sustenta 28,5 chegadas por minuto com utilização de 80%. Acima de 80% a
fila de triagem cresce sem limite, e a triagem vira o gargalo que o próprio
`contexto` já sinalizava — um ponto de estrangulamento não paralelizável,
independente de como as urnas estejam distribuídas.

### Sensibilidade

| Cenário | Pico simultâneo | Pessoas no dia | A recrutar |
|---|---|---|---|
| Enxuto (40% pedem triagem a 15 s; 1 orientador por 6 urnas) | 30 | 56 | 75 |
| **Base** | **41** | **77** | **103** |
| Reforçado (75% a 25 s; 1 orientador por 3 urnas) | 52 | 96 | 128 |

O intervalo 56–96 é largo porque depende de uma variável que o posto controla:
**quanto da orientação é resolvida por sinalização em vez de por pessoa**. Os
EUR 1.961 já orçados em banners são, nesse sentido, um investimento que reduz
headcount — cada 10 pontos percentuais a menos de eleitores que precisam
perguntar algo tiram cerca de 1,2 voluntário do pico da triagem. Divulgação
prévia da seção pelo Instagram e pelo e-Título puxa na mesma direção.

## 4. Alocação física

O salão tem duas entradas (A e B) com um ponto de triagem cada, mesas nas três
paredes e uma saída central, conforme `PLANO COM FLUXOS MELHORADO.png`.

### 4.1 Divisão das 28 urnas entre as entradas

As urnas foram agrupadas em 8 clusters equilibrados por comparecimento
esperado e repartidos 4 e 4 entre as entradas:

| Cluster | Entrada | Urnas | Comparecimento esperado |
|---|---|---|---|
| C1 | A | 3313, 3216, 517 | 1.323 |
| C4 | A | 3142, 3309, 1160 | 1.227 |
| C6 | A | 3245, 3311, 3054, 3308 | 1.570 |
| C7 | A | 3302, 3108, 3078, 3832 | 1.561 |
| **Entrada A** | | **14 urnas** | **5.681** |
| C2 | B | 3322, 511, 513 | 1.322 |
| C3 | B | 3315, 3229, 512 | 1.319 |
| C5 | B | 3161, 3179, 1352, 3442 | 1.547 |
| C8 | B | 3305, 3306, 3688, 3862 | 1.549 |
| **Entrada B** | | **14 urnas** | **5.737** |

O desequilíbrio entre as portas é de 56 eleitores (0,5%). As cinco urnas mais
pesadas — 3313, 3322, 3315 (≈590 comparecentes cada) e 3142, 3161 (≈490) —
ficam **repartidas entre as duas entradas** (A: 3313, 3142; B: 3322, 3315,
3161), seguindo a recomendação já registrada no contexto de não concentrar
volume numa porta só.

Esta tabela é uma alocação **lógica**. Ela precisa ser conferida contra a
posição física das mesas no Hall 2: se um cluster da entrada A estiver fisicamente
na parede de trás à direita, o eleitor atravessa o salão inteiro e a
economia de fila se perde. **Regra de ouro: cluster da entrada A = mesas da
metade esquerda do salão.** Se a numeração das urnas no salão não permitir
isso, é a numeração que se ajusta, não o eleitor.

### 4.2 Postos no dia

| Posto | Quantos | Onde |
|---|---|---|
| Portão externo / Merrion Road | 4 (8 na abertura) | calçada e acesso ao RDS |
| Triagem A | 4 | hub azul-claro, à frente da entrada A |
| Triagem B | 4 | hub roxo, à frente da entrada B |
| Balcão de consulta | 5 | lateral, fora do caminho das duas filas |
| Corredor C1–C8 | 1 por cluster (8) | junto ao bloco de mesas |
| Prioritário | 3 | 1 por entrada + 1 volante interno |
| Runner de mesa | 4 | 1 por bloco de ~7 urnas |
| Saída | 2 | EXIT central |
| Coordenação | 3 | 1 geral (móvel) + 1 por entrada |
| Reserva | 6 | ponto de apoio, junto à sala de transmissão |

O balcão de consulta é o posto que mais depende de ferramenta: precisa de
listagem impressa por ordem alfabética **e** consulta eletrônica. É o único
ponto onde uma fila de 90 s por pessoa é aceitável, exatamente porque ele
existe para tirar essa fila de dentro da triagem.

## 5. Escala

| Turno | Horário | Pessoas |
|---|---|---|
| T1 Manhã | 07h00–13h30 | 40 |
| T3 Reforço de pico | 09h30–14h00 | 3 |
| T2 Tarde | 12h30–encerramento | 34 |
| **Distintas no dia** | | **77** |

Notas de escala:

- **T1 entra às 7h**, uma hora antes da abertura, porque a fila de abertura é o
  primeiro pico e porque a montagem de sinalização e separadores de fila
  precisa estar pronta às 7h45.
- **A passagem de turno às 12h30–13h30 se sobrepõe de propósito**: trocar a
  equipe inteira no meio da cauda do pico é como se perde o controle da fila.
- **T2 fica até o encerramento**, não até as 17h. Eleitor que chegou antes das
  17h vota depois das 17h; a fila interna não acaba com o relógio, e a equipe
  que a organiza não pode ir embora antes dela.
- Cada turno se organiza em **equipes de 8 com um líder**, e o líder é o único
  ponto de contato com a coordenação. Sem essa camada, 40 pessoas viram 40
  interrupções do coordenador.
- Além dos 77 do dia, prever **8 voluntários na véspera (03/10)** para montagem
  de sinalização, unifila e conferência de layout.

## 6. Recrutamento

Meta: **100 pessoas confirmadas** para 77 postos (absenteísmo de 25%, típico
de voluntariado não remunerado num domingo). Se o recrutamento fechar abaixo
de 85 confirmados, o corte deve ser feito por função, nesta ordem inversa de
prioridade: reserva → runner → saída → prioritário. Triagem e corredor não se
cortam.

| Etapa | Prazo | Responsável |
|---|---|---|
| Confirmar enquadramento com o Cartório (seção 1) | imediato | posto |
| Abrir chamada pública (Instagram, site da Embaixada, lista de e-mails) | até 20/09 | comunicação |
| Ativar multiplicadores | até 20/09 | posto |
| Fechar lista de 100 confirmados | 27/09 | coordenação |
| Webinar de treinamento (2 sessões, 1h) | 28/09–30/09 | coordenação |
| Confirmação individual final + escala nominal | 01/10 | coordenação |
| Briefing presencial no local | 03/10 | coordenação |

Fontes de recrutamento, por rendimento esperado: associações de brasileiros e
igrejas com comunidade brasileira em Dublin; estudantes de intercâmbio
(alta disponibilidade num domingo, baixa retenção — recrutar com folga);
familiares dos próprios mesários já nomeados; e voluntários das eleições de
2022, que já conhecem o fluxo e devem ser buscados nominalmente primeiro.

Um filtro que economiza trabalho: **inglês funcional é requisito só para o
portão externo e a coordenação** (interlocução com staff do RDS, segurança
contratada e Gardaí). Nos demais postos, o atendimento é em português.

## 7. Treinamento

Webinar de 1h, com material de 2 páginas, cobrindo:

1. **O que você não pode fazer** — não tocar em caderno, urna ou documento do
   eleitor; não orientar voto; não discutir política no salão. Esta é a
   primeira parte da pauta, não a última.
2. O mapa do salão, os 8 clusters e a regra A/B.
3. As três perguntas que 90% dos eleitores farão ("qual é a minha seção?",
   "esqueci o título", "moro em Cork, voto aqui?") e a resposta padrão de cada
   uma.
4. Atendimento prioritário: quem tem direito e como conduzir.
5. Escalonamento: o que vai para o líder de equipe, o que vai para o
   coordenador, o que vai para o presidente da mesa — e a regra de que
   problema de eleitor específico **sempre** termina no presidente da mesa,
   nunca no voluntário.

O webinar dos voluntários é distinto do webinar de mesários já previsto na
`PENDENCIAS` (item 4), mas as duas pautas devem ser escritas juntas, para que
a divisão de papéis seja explicada com as mesmas palavras dos dois lados.

## 8. Custo estimado

Não orçado ainda; ordem de grandeza para entrar na tabela final da
`PENDENCIAS` (item 2).

| Item | Estimativa (EUR) |
|---|---|
| Coletes identificadores (100, cor distinta da segurança contratada) | 600 |
| Crachás e cordões | 150 |
| Alimentação e água (77 pessoas + 8 da véspera) | 1.300 |
| Impressão de material de treinamento e listagens do balcão | 200 |
| Contingência de transporte | 250 |
| **Total** | **~2.500** |

Comparação útil: são ~2.500 EUR para 77 pessoas contra os 6.775 EUR já
contratados para 20 seguranças. O voluntariado é a linha mais barata do
orçamento por pessoa-hora e a que mais afeta a experiência do eleitor.

## 9. Efeitos de segunda e terceira ordem

**Segunda ordem.** Voluntário de colete é lido pelo eleitor como autoridade,
independentemente do que diga o crachá. Isso corta nos dois sentidos: acelera
o fluxo porque a orientação é aceita sem discussão, e cria risco porque uma
informação errada dita por um voluntário tem peso de informação oficial. Daí a
regra do item 7.5 — o voluntário encaminha, não decide. Um segundo efeito: se
a triagem funcionar bem, a fila visível desaparece da calçada e migra para
dentro do salão, o que muda a percepção pública do evento (foto de fila na rua
é o que vira notícia) sem mudar o tempo de espera real.

**Terceira ordem.** Os 4.213 eleitores do interior que viajam a Dublin
(Cork, Galway, Limerick) têm custo de deslocamento alto e tolerância a fila
baixa — quem dirigiu 3h não vai esperar 2h. Se esse grupo desistir, a queda de
comparecimento aparecerá concentrada nos condados, e o argumento de 2030 para
abrir seções fora de Dublin ficará mais forte com base num dado que é, na
verdade, artefato de fila. O inverso também vale: uma operação que funcione em
2026 com 16.794 eleitores estabelece a referência de custo e de equipe contra
a qual o crescimento seguinte do eleitorado será julgado — vale registrar as
métricas do dia (fluxo horário real, tempo de fila por hora, atendimentos no
balcão de consulta) exatamente para que a próxima negociação com o TSE não
recomece do zero.

## 10. Segundo turno (25/10)

Mesmo dimensionamento, com dois ajustes. O comparecimento de 2º turno tende a
ser igual ou levemente menor, mas a **curva costuma ser mais concentrada**
(eleitor já sabe onde é sua seção e vai mais cedo) — o que sustenta o mesmo
pico com menos gente na consulta e mais na triagem. E a retenção de
voluntários entre turnos raramente passa de 70%: manter a lista de 100 ativa e
reconfirmar na semana de 19/10, sem recomeçar o recrutamento.

## 11. O que pode invalidar estes números

1. **Nomeação de apoio logístico fora do prazo** (seção 1) — muda a figura
   jurídica dos 77, não a quantidade.
2. **Renegociação da agregação com o TSE.** Se as 28 urnas virarem 32–38
   (Cenários 4/5 do contexto), a orientação de corredor sobe para 10–11 e os
   runners para 5–6; a triagem e a fila externa não mudam, porque dependem do
   fluxo de eleitores, não do número de urnas. Efeito líquido: +4 a +6 no pico.
3. **Método de identificação do eleitor.** Caderno físico em vez de consulta
   eletrônica aumenta o tempo por eleitor na mesa e alonga as filas internas,
   o que exige mais orientação de corredor — mas não mais triagem.
4. **Curva de chegada real** diferente da assumida (seção 2).
5. **Dimensões e circulação reais do Hall 2**, ainda não confirmadas contra as
   simulações de layout.

## Como recalcular

```bash
cd scripts
python3 voluntarios.py   # gera saidas/dimensionamento_voluntarios.{json,md}
```

As premissas estão todas no dicionário `PREMISSAS` de `scripts/voluntarios.py`,
e os três cenários em `CENARIOS`. Nenhum número deste plano foi arredondado à
mão: mudar uma premissa e rodar de novo refaz todas as tabelas.
