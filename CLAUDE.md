# Memória do projeto — Eleições 2026, Posto de Dublin

Organização logística do 1º turno (04/10/2026, 8h–17h) e do eventual 2º turno
(25/10/2026) na jurisdição de Dublin. Documentos em português.

## Fatos fixos

| Item | Valor | Fonte |
|---|---|---|
| Eleitores aptos | 16.794 | `saidas/dados.json`, dos CSVs oficiais do TSE |
| Seções / urnas | 51 seções agregadas em 28 urnas | idem |
| Residentes em Dublin / interior | 12.581 / 4.213 | idem |
| Comparecimento esperado | **11.499** (base B: taxa de 2022 do condado de origem por seção) | prancheta `Paredes_ABC`, 15/09 |
| Local | RDS, Merrion Road, Ballsbridge, Dublin 4 | contrato |
| Segurança contratada | 20 pessoas, 7h30–17h30, + 1 na véspera | orçamento (EUR 6.774,84) |

## Geometria do local (planta de 16/09/2026)

O percurso tem três trechos físicos distintos. **Ring 3 é o pátio de fila ao ar
livre; Hall 2 é o salão de votação.**

**Ring 3 — pátio de fila.** Recinto ao ar livre de gradil permanente, 44,0 × 35,0 m,
ao sul do Hall 2. Entrada única pelo **canto nordeste**. Um **corredor de chegada de
3,0 m** desce pelo lado leste; um **trecho de fundo de 3,0 m** corre na base e
distribui para as três zonas. Zonas lado a lado, separadas por vãos de 1,20 m:
**zona C 12,23 m (leste, a primeira que se alcança), zona B 14,14 m (centro), zona A
12,23 m (oeste, a mais distante)**. Cada zona tem **23 raias** ao longo de 32,0 m
(passo de 1,39 m). A fila avança de baixo para cima; a cabeça de cada zona fica no
topo, voltada para o Hall.

**Apron.** Faixa pavimentada de **14,0 m** entre a cabeça das filas e a fachada sul
do Hall 2. Espaço de travessia, sem raias.

**Hall 2 — salão de votação.** Portas na fachada sul: **S4 = entrada A, S5 = entrada
B, S6 = entrada C, S7 = preferencial**; **S2 e S8 são saídas**; S1, S3 e S9 ficam
livres. As 28 mesas ficam encostadas nas paredes: **parede oeste = zona A (9 urnas),
parede norte = zona B (9 urnas), parede leste = zona C (10 urnas)**. Sala de apoio no
canto noroeste. Faixa livre de 3 m junto à parede leste para as saídas de emergência
L1–L4. Portas O1 e N1 fechadas; O2, N2 e H1 livres. Serpentinas internas de 20
pessoas nas três mesas maiores (3313, 3315, 3322).

Correspondência que amarra tudo: **zona do Ring → porta do Hall → parede do salão**,
com a mesma letra em toda a rota.

| Zona | Ring 3 | Porta | Parede | Urnas | Aptos | Comparecimento esperado |
|---|---|---|---|---|---|---|
| A | oeste (12,23 m) | S4 | oeste | 9 | 5.695 | 3.834 |
| B | centro (14,14 m) | S5 | norte | 9 | 5.600 | 3.832 |
| C | leste (12,23 m) | S6 | leste | 10 | 5.499 | 3.833 |

Spread de 0,05% pela base B, com uma das três urnas grandes (3313, 3315, 3322) em
cada zona. A distribuição está equilibrada; não mexer sem refazer a conta.
`scripts/zonas_balanceadas.py` confere a composição com um estimador mais grosso
(74%/50%), que chega a 3.860 / 3.755 / 3.802 — mesma conclusão, 2% de diferença.

A rota também tem os pontos **P0 a P7** do plano de sinalização: **P0** é a mesa
"descubra sua seção" na calçada da Merrion Road, **fora** do portão. Depois do
portão toda peça pressupõe a seção conhecida, então P0 é o único ponto que resolve
quem chega sem o número.

O `RDS_Hall_2_Floorplan_(1).pdf` e o `PLANO COM FLUXOS MELHORADO.png` são anteriores
a esta planta e descrevem duas entradas apenas — material histórico.

## Documentos do repositório

- `README.md` — análise das agregações de seções (o núcleo técnico e os dados).
- `contexto_eleicoes_dublin_2026.md` — contexto consolidado: orçamento, layout,
  simulações de tempo de votação, argumentação com o TSE.
- `lista_postos.md` — lista operacional dos postos de voluntários: onde cada um
  fica e o que faz. É a fonte única desses números e o documento do briefing.
- `voluntarios_postos.html` — os postos marcados sobre a rota e sobre a planta do
  salão, em três cenários de efetivo (9, 24 e 49). Publicado em
  https://claude.ai/artifact/YaFNHUua2Hkqu7dtR7tf7A
- `plano_voluntarios_apoio.md` — o raciocínio por trás da lista: taxas de chegada,
  dimensionamento, decisões do Posto e achados das plantas.
- `PENDENCIAS` — lista de tarefas em aberto do Posto.
- `scripts/`, `saidas/` — pipeline de dados; os scripts falham em vez de gravar
  saída errada quando alguma validação não passa.

## Cenários de efetivo de voluntários (decisão de 17/09/2026)

Quatro cenários, numerados por quantas pessoas de apoio existem. **C4 é referência de
teto, não meta de recrutamento** — o Posto não o considera realista para 2026.

| | Pessoas no pico | Postos ocupados (de 17) | Turnos e reserva |
|---|---|---|---|
| **C1 · Contingência** | 9 — o efetivo de hoje | 5 | não |
| **C2 · Próximo degrau** | 15 | 7 | não |
| **C3 · Operacional** | 24 | 13 | não |
| **C4 · Pleno** | 49 (43 postos + 15% de reserva) | 17 | sim, 61 escaladas |

Histórico do efetivo: eram 25 voluntários; 14 foram cedidos para cobrir dispensas de
mesário e **não voltam** — mesário é função nomeada, com treinamento próprio. Campanha
de reserva em curso.

**C1 (9):** 3 no P0 da calçada, 1 no trecho de fundo do Ring (R3), 1 na porta
preferencial S7 (A3), 3 nas mesas vermelhas (H3) e 1 na coordenação (T1).

**C2 (15)** acrescenta o quarto operador do P0, as três cabeças de fila (R5, uma por
zona) e duas bocas do trecho de fundo (R2, zonas C e A).

O preenchimento é uma **fila contínua da posição 10 à 49**, para funcionar com
qualquer número intermediário — com 13 pessoas preenche-se até a posição 13, com 17 até
a 17. A fila está em `lista_postos.md` e em `voluntarios_postos.html`.

C1 e C2 só fecham com três compensações contratadas: os 20 seguranças assumindo
presença de fila por escrito no briefing, uma CCB de separação no apron no lugar do
posto A1, e a campanha "descubra sua seção antes de sair de casa".

## Convenções

- Números de eleitorado vêm sempre de `saidas/dados.json` (CSV oficial), nunca do
  PNG do mapa de agregações do TSE, que tem erro de digitação conhecido (seção 3752
  listada sob a principal 3222; a correta é 3322).
- Premissas não observadas (fator de pico, tempo por eleitor, permanência média)
  são rotuladas como premissas no texto.
- Voluntário orienta, não decide: não toca em documento, não confere título, não
  diz a ninguém se pode votar. Identificação é monopólio legal do mesário.

## Pendências que movem números

1. Método de identificação do eleitor — eletrônico/biométrico ou caderno físico
   (`PENDENCIAS` item 5). Decide tempo por eleitor e criticidade do balcão de
   consulta.
2. Confirmação da expectativa de comparecimento.
3. Orçamento final, incluindo o apoio ao voluntariado (~EUR 1.700–1.900).
