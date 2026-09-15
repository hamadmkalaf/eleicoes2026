# Memória do projeto — Eleições 2026, Posto de Dublin

Organização logística do 1º turno (04/10/2026, 8h–17h) e do eventual 2º turno
(25/10/2026) na jurisdição de Dublin. Documentos em português.

## Fatos fixos

| Item | Valor | Fonte |
|---|---|---|
| Eleitores aptos | 16.794 | `saidas/dados.json`, dos CSVs oficiais do TSE |
| Seções / urnas | 51 seções agregadas em 28 urnas | idem |
| Residentes em Dublin / interior | 12.581 / 4.213 | idem |
| Comparecimento esperado | ~11.400 (74% Dublin, 50% interior — taxas de 2022) | `contexto_eleicoes_dublin_2026.md` |
| Local | RDS, Merrion Road, Ballsbridge, Dublin 4 | contrato |
| Segurança contratada | 20 pessoas, 7h30–17h30, + 1 na véspera | orçamento (EUR 6.774,84) |

## Geometria do local (decisão registrada em 15/09/2026)

- O **Hall 2 (Shelbourne Hall, 50,2 × 44,5 m)** é a área de chegada, fila e
  sinalização. Tem três portas de entrada nomeadas **A, B e C**.
- O **Ring 3** é o salão de votação, dividido em **três zonas, nomeadas A, B e C
  segundo as portas do Hall 2**. Cada zona corresponde a uma porta: porta A → zona
  A, porta B → zona B, porta C → zona C.
- Consequência para dimensionamento: **3 zonas e 3 portas de entrada**, mais a saída
  dedicada. Postos de voluntário em frente às zonas e em frente às portas escalam
  1:1 com esses números.

O `RDS_Hall_2_Floorplan_(1).pdf` e o `PLANO COM FLUXOS MELHORADO.png` são do Hall 2
e descrevem apenas duas entradas (A e B) — material anterior a esta decisão, a ser
relido como planta do espaço de chegada, não do salão de votação.

## Documentos do repositório

- `README.md` — análise das agregações de seções (o núcleo técnico e os dados).
- `contexto_eleicoes_dublin_2026.md` — contexto consolidado: orçamento, layout,
  simulações de tempo de votação, argumentação com o TSE.
- `plano_voluntarios_apoio.md` — funções e efetivo de voluntários de fluxo.
- `PENDENCIAS` — lista de tarefas em aberto do Posto.
- `scripts/`, `saidas/` — pipeline de dados; os scripts falham em vez de gravar
  saída errada quando alguma validação não passa.

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
