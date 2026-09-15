# Handoff — Agregação de seções e simulação eleitoral, jurisdição Dublin (Eleições 2026)

Cole este bloco no novo chat para dar todo o contexto. Projeto: logística das eleições brasileiras de 2026 na jurisdição de Dublin — agregação de seções em mesas e simulação de filas/tempo de votação.

---

## 1. Dois conjuntos de dados (ATENÇÃO à comparabilidade)

Usamos duas fotografias do eleitorado que **não são intercambiáveis**:

- **Base "markdown" (16.794 aptos, 51 seções):** Dublin 32 seções / 12.581 aptos; interior 19 seções / 4.213 aptos. Foi a base das Propostas 1 e 2.
- **Arquivo do TRE `Irlanda_-_Dublin.xlsx` (14.626 aptos, 51 seções):** proposta oficial já agregada em **20 mesas**. Foi a base da Simulação 3.

A diferença (~2.168 aptos) parece vir de limpeza/atualização do cadastro, concentrada no interior. **Propostas 1–2 e a Simulação 3 não são diretamente comparáveis** por usarem eleitorados diferentes. Para comparar em pé de igualdade, rodar as propostas sobre o arquivo do TRE (14.626).

## 2. Composição por domicílio (base markdown 16.794)

| Domicílio | Seções | Aptos | Turnout 2022 | Qualidade do dado |
|---|---|---|---|---|
| Dublin | 32 | 12.581 | 74% | direto |
| Cork | 3 | 986 | 53,3% | direto |
| Outros locais da Irlanda | 2 | 745 | 60% | direto |
| Galway | 2 | 728 | 48,1% | direto |
| Limerick | 2 | 468 | 43,4% | proxy |
| Westmeath | 1 | 278 | 46,1% | proxy |
| Waterford | 1 | 217 | 46,1% | proxy |
| Roscommon | 1 | 182 | 43,4% | proxy |
| Clare | 1 | 173 | 64,9% | direto |
| Cavan | 1 | 113 | 46,1% | proxy |
| Mayo | 1 | 102 | 54,4% | proxy |
| Longford | 1 | 76 | 77,8% | direto |
| Donegal | 1 | 62 | 51% | genérico (0,49 abst.) |
| Kerry | 1 | 54 | 54,4% | proxy |
| Leitrim | 1 | 29 | 51% | genérico (0,49 abst.) |

## 3. Fatos estruturais e parâmetros operacionais

- **Teto legal:** 800 aptos por mesa.
- **Seções de Dublin ≈ 393–398 aptos cada** → cabem no máximo **2 por mesa** (786–800). Interior é pequeno.
- **Janela de votação:** 8h–17h horário local = **9h = 32.400s** (TSE / Agência Brasil, 2022). Uma urna (MRV) por seção; um eleitor por vez.
- **Capacidade por mesa em 9h:** 30s/eleitor → 1.080; 60s → 540; 90s → 360.
- **Comparecimento estimado** = aptos × taxa de comparecimento de 2022 do respectivo domicílio.

---

## 4. Entregável 1 — Dublin isoladas / não-Dublin agrupadas entre si
Arquivo: `proposta_agregacao_dublin_isoladas.xlsx` (base 16.794)

**Regra:** cada uma das 32 seções de Dublin vira uma mesa (isolada); as 19 seções não-Dublin são agrupadas **exclusivamente entre si**; teto 800.

- **Variante A (consolidação máxima):** 38 mesas (32 Dublin + 6 não-Dublin). CV do comparecimento 15,2%.
- **Variante B (recomendada, equilíbrio):** 40 mesas (32 Dublin + 8 não-Dublin balanceadas por comparecimento). As 40 mesas ficam entre **266 e 292 comparecentes** (CV 2,5%) — a grade mais uniforme possível sob a regra.
- **Trade-off:** usa mais mesas (38–40) que as demais (23–31); isolar Dublin fixa um piso de 32 mesas. Troca nº de mesas por transparência e uniformidade.

## 5. Entregável 2 — Minimizar o máximo de comparecentes (24 e 30 mesas)
Arquivo: `proposta_minmax_24_30.xlsx` (base 16.794)

**Objetivo:** menor máximo de comparecentes por mesa, teto 800, exatamente K mesas.

- **Achado central (contraintuitivo):** o menor máximo é **582 comparecentes para 24 E para 30 mesas** — e para qualquer K entre 22 e 31. Fica travado por **pares Dublin-Dublin forçados** (786 aptos / 583 comparecentes). Casa dos pombos: com 32 seções de Dublin e ≤2 por mesa, K<32 obriga (32−K) pares.
- K=24 → 8 mesas no pico; K=30 → 2 mesas no pico. **Mesmo pico**, mas 30 mesas tem menos mesas saturadas e carga média menor → **30 domina 24**.
- **Ponto de quebra:** o pico só cai a partir de **K≥32** (515 em 32; 466 em 33; 292 em 40). Se minimizar o máximo é a prioridade real, é preciso ≥32 mesas.

## 6. Entregável 3 — Simulação de tempo da proposta do TRE
Arquivo: `simulacao_tempo_votacao_TRE.xlsx` (base TRE 14.626)

TRE agrega as 51 seções em **20 mesas**. Simulamos comparecimento e tempo a 30/60/90s por eleitor.

- **Comparecimento total estimado ≈ 10.395** (turnout ~71%).
- **Gargalo:** as **11 mesas de par Dublin-Dublin** (~800 aptos → ~590 comparecentes).
- **A 30s/eleitor:** todas as 20 mesas cabem nas 9h (a mais cheia ~4,9h). Folgado.
- **A 60s/eleitor:** **11 mesas estouram** a janela (~9,8h > 9h).
- **A 90s/eleitor:** **19 das 20 estouram** (a mais cheia ~14,8h).
- **Conclusão:** a proposta do TRE só é segura perto de 30s/eleitor; a 60s (identificação + voto realistas) os pares de Dublin colapsam.

**Efeitos de 2ª/3ª ordem:** encerramento (apuração/BU/lacre) desliza para a madrugada nas mesas de Dublin; filas matinais causam desistência (privação de voto mascarada no papel); 11 de 20 urnas no limite, sem folga para absorver falha de equipamento; o desequilíbrio é interno a Dublin, não Dublin vs. interior.

---

## 7. Método e ressalvas (válidas para tudo acima)

- **Não temos o aptos por seção.** As seções de Dublin foram tratadas como ~iguais (~393–398); o interior foi atomizado por condado. Nas **mesas mistas do TRE**, o arquivo só dá o total por mesa — o rateio Dublin/interior foi estimado (±5%), mas **nenhuma mista é gargalo**, então as conclusões de tempo não mudam.
- As **mesas puras de Dublin** (o gargalo) têm comparecimento **exato** (74% do total) → conclusões robustas.
- O arquivo real por seção estaria em `perfil_eleitor_secao_ZZ` no Google Drive, mas a ferramenta de busca do Drive só abre Google Docs (não xlsx/CSV), então não foi possível lê-lo nas sessões anteriores.
- Tempos de 30/60/90s incluem identificação + voto. Presidente-only tende a 20–40s reais; 60–90s modelam fila/identificação lenta.

## 8. Pendências / próximos passos sugeridos

1. **Rodar as Propostas 1 e 2 sobre o eleitorado real do TRE (14.626)** para comparação apples-to-apples com a proposta oficial.
2. **Comparar tempo de votação:** proposta TRE (20 mesas) vs. alternativas de 30 e 32 mesas — quantificar quanto do estouro a 60s some ao desmembrar os pares de Dublin.
3. **Obter o aptos por seção** (`perfil_eleitor_secao_ZZ`) para exatidão nas mesas mistas e para permitir emparelhar as menores seções de Dublin (o que pode baixar o pico de 582).
