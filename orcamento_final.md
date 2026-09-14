# Orçamento final — tabela preenchível (1º turno, RDS Hall 2, 04/10/2026)

> Criado em 13/09/2026 para a pendência 2 do `PENDENCIAS`. Duas tabelas: o que
> **já existe** (contratado ou em mãos) e o que **ainda custa** e depende de
> decisão ou de cotação. As células marcadas `___` são para o Posto preencher a
> cada cotação recebida. Referências: itens a–f do telegrama revisado
> (`contexto_eleicoes_dublin_2026.md` §6.1, EUR 15.703,32), cotações de
> `orcamentos_itens_pequenos.md`, decisões D1–D9 de `scripts/decisoes_abertas.py`
> (em 14/09: D1, D2 (fitas no piso, sem checkpoint), D3, D4 (só filas de mesa) e D8
> decididas; só D9 em aberto).
> Valores em EUR; indicar ex-VAT ou inc-VAT (23 %) na coluna de observação.

## 1. Recursos disponíveis

| # | Item | Contratado / em mãos | Quantidade | Valor (EUR) | Fonte | Status | Observação |
|---|---|---|---|---|---|---|---|
| R1 | Segurança (item a) | 20 seguranças 7h30–17h30 + 1 × 16 h na véspera | **a revisar: 4** | 6.774,84 (para 20) → ___ (para 4) | telegrama | a revisar | Decisão de 13/09: 4 seguranças. Verificar efetivo mínimo exigido pela apólice do RDS (R6). |
| R2 | Eletricista (item b) | cabeamento e pontos elétricos para as urnas | 28 pontos | 5.387,40 | telegrama | fechado | Conferir contra o arranjo final da prancheta (Hamad_3polos) e as caixas de piso do RDS. |
| R3 | Banners de sinalização (item c) | impressão + aluguel de bases | ___ peças | 1.961,00 | telegrama | a revisar | Cobre P0–P7 do plano de sinalização? Peças novas em C6–C8. |
| R4 | Unifilas / postes Tensa (item d) | 100 unidades (200 m) | 100 | 1.303,00 | telegrama | fechado | Traçado `so_mesas` (14/09, só filas de mesa, sobre o Hamad_Final) consome 54 (60 com reserva de 10 %): sobram 40. Nada a encomendar (C1). |
| R5 | Mobiliário (item e) | mesas adicionais para as urnas | ___ | 276,48 | telegrama | fechado | |
| R6 | Seguro obrigatório (item f) | 1º e 2º turno | 1 apólice | 2.642,00 | telegrama | fechado | **Ler a apólice:** impõe efetivo mínimo de segurança? |
| R7 | Separadores de barreira externa (CCB) | estoque da organizadora do RDS, 2 m × 1 m | 200 | 0 (em mãos) | contexto Ring 3 §3 | em mãos | Serve o Ring 3; "dá para comprar mais" (C2). |
| R8 | Espaço | RDS Hall 2 + Ring 3 + apron | 1º e 2º turno | (já pago, reftel 131) | telegrama | fechado | 50,0 × 44,5 m; Ring 3 44 × 35 m. |
| R9 | Mesários voluntários (fluxo) | organização de fila e orientação | ___ pessoas | 0 | decisão 13/09 | a confirmar | Ver tabela de equipe em `docs/instrucoes_fluxo.md` (D7). |
| R10 | Polícia (fora do recinto) | presença externa | ___ | 0 | decisão 13/09 | a confirmar | Formato (viatura fixa, ronda, horário) a confirmar e registrar na nota verbal. |
| R11 | Coletes hi-vis | ___ | 20 | ~110,80 inc-VAT (Medguard) | orcamentos_itens_pequenos §2 | cotação de tabela | Confirmar estoque e frete. |
| R12 | Adaptadores de tomada (tipo N/J → G) | ___ | ___ | ___ | orcamentos_itens_pequenos §4 | a cotar | Confirmar compatibilidade BR/CH. |

## 2. Custos em aberto

| # | Item | Depende de | Quantidade estimada | Estimativa (EUR) | Fornecedor / cotação | Status | A preencher |
|---|---|---|---|---|---|---|---|
| C1 | Unifilas de reserva (10 %) | D4 = só filas de mesa (decidida 14/09) | 0: os 100 contratados cobrem os 60 com reserva | 0 | M. O'Byrne Hire | resolvido | se o Posto voltar a um traçado com poste na entrada (1e/1f/1g/1h: 91/88/82/73 com reserva), ainda sobra |
| C2 | Separadores externos (CCB) a mais | **D3 decidida (13/09)**: CCB só na ponta, raias L–O | **0** a comprar (82 contados, 100 registrados com margem, 200 em estoque) | 0 | organizadora do RDS | resolvido | confirmar com a organizadora que os 100 registrados saem do estoque de 200 |
| C3 | Fita grossa de isolamento | **D3 decidida**: CCB na ponta, L–O | **576 m** | ___ (premissa: ~EUR 12 por rolo de 33 m → ~EUR 210) | orcamentos_itens_pequenos §5 | a cotar | fornecedor ___ · valor ___ |
| C4 | Apoios da fita (a cada 5 m) | **D3 decidida**: L–O | **66** | ___ (0 se forem CCB do estoque: 82 + 66 = 148 CCB, ainda dentro dos 200) | ___ | a definir o tipo | tipo de apoio ___ · valor ___ |
| C5 | Fita de contorno das zonas do Ring 3 | D3 decidida (sem garganta) | 160 m | ___ | ___ | a cotar | |
| C6 | Placas de porta nas CCBs do Ring 3 (seções + mesas por porta, com número eleitor e MRV) | **D1, D3, D8 decididas**; D5 derivada | 3 (uma por cabeça de zona) + ___ | ___ | gráfica ___ | liberado para orçar; imprimir só depois do Hamad_Final colado | quantidade ___ · valor ___ |
| C7 | Sinalização interna: placa do par de mesas suspensa nas treliças | D6 derivada; rigging do RDS | 14 peças + plataforma elevatória na véspera | ___ | ___ | a decidir se entra | rigging autorizado? ___ |
| C8 | Sinalização interna: painel seção → mesa **na soleira** | **D2 decidida (fitas, 14/09)** | 3 (um por porta), lidos em pé em 10 s | ___ | ___ | a cotar | |
| C9 | Placa alta com o número eleitor em toda mesa | **D2 decidida (fitas, 14/09)**: obrigatória | 28 | ___ | ___ | a cotar | |
| C16 | Fita de piso por entrada (três cores, letra impressa) | **D2 decidida (fitas, 14/09)** | 462 m em 9 troncos (A 159 m, B 156 m, C 147 m; `docs/plano_filas.md`) | ___ | ___ | a cotar | fita antiderrapante para piso de pavilhão; conferir com o RDS se pode colar |
| C10 | Cobertura leve dos serpenteados (chuva) | D3 | últimos 8–10 m de cada zona | ___ | ___ | a cotar | |
| C11 | Portaloos | pendência 2 | 2 padrão + 1 PCD | ___ | Envira Loo / CleanLoo / CES / O'Byrne | a cotar | fornecedor ___ · valor ___ |
| C12 | Walkie-talkies (aluguel, 1 dia) | D7 (equipe) | 10 | ___ | RadioTrader / Hire Here / Choice | a cotar | |
| C13 | Orientadores pagos, se faltarem voluntários | **D7** | ___ pessoas × 10 h | ref. 31,37/h (item a) → 5 orientadores ≈ 1.569 | ___ | condicional | nº de voluntários confirmados ___ |
| C14 | Água / abrigo para a fila | D3, chuva | ___ | ___ | ___ | a decidir | |
| C15 | Segurança revisada (4 seguranças) | decisão 13/09 | 4 × 10 h + véspera | ___ (≈ 1/5 do item a) | mesma empresa do item a | a recotar | valor ___ |

## 3. Como fechar

1. Preencher C15 e R1 assim que a empresa de segurança recotar para 4.
2. ~~Fechar D3~~ Decidida em 13/09: cotar C3 (576 m de fita), C4 (66 apoios), C5 e C10.
3. ~~Fechar D1 e D8~~ Decididas em 13/09 (3 + 2 portas; letra): orçar C6; imprimir só
   depois de colar o Hamad_Final (a numeração eleitor depende dele).
4. ~~Fechar D2~~ Decidida em 14/09 (fitas no piso, sem checkpoint): cotar C8, C9 e C16.
   Fechar **D9 (a)** (caderno) não muda o orçamento, muda a equipe (D7) e as instruções.
5. Somar as colunas "Valor" e "Estimativa" e comparar com os EUR 15.703,32 do
   telegrama revisado; a diferença do item a) (≈ 5.400) e os 19 postes que sobram
   são a folga para C3–C14.
