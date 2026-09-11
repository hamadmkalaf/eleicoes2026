# Análise de gargalos — 28 urnas fixadas (RDS Hall 2, 04/10/2026)

Registro do que foi apurado depois de encerrada a negociação com o TRE. A
configuração está fixada: **28 urnas, 28 mesas receptoras (1:1), 51 seções,
16.794 aptos**, janela 8h–17h. Identificação por **caderno físico impresso**.
Espaço contratado: **Hall 2 + Ring 3 sem cobertura**.

Reproduzível com `python3 scripts/simula_fluxo.py`.

## 1. O gargalo é aritmético, não de fila

Comparecimento esperado pela base B — taxa de 2022 por domicílio de origem de
cada seção, `scripts/comparecimento.py`, decisão do Posto de 06/09/2026:
**11.499 eleitores** (68,5%). A urna mais carregada é a **3313 (MRV 22), com
590 esperados**.

590 eleitores ÷ 540 minutos = **54,9 segundos por eleitor, sem folga alguma**.
É um teto de vazão. Nenhuma gestão de fila o altera.

| Ciclo por eleitor | Urnas ainda com fila às 17h | Última urna fecha |
|---|---|---|
| 45 s | 0 / 28 | 17h00 |
| 50 s | 0 / 28 | 17h00 |
| 55 s | 1 / 28 | 17h01 |
| 60 s | 3 / 28 | 17h50 |
| 75 s | 11 / 28 | 20h18 |
| 90 s | 16 / 28 | 22h45 |

O precipício está entre 50 s e 60 s. E a falha é concentrada: a 60 s falham
exatamente três urnas — **3313, 3322 e 3315**, os três pares Dublin+Dublin.
As outras 25 fecham no horário.

## 2. Comunicação dirigida não resolve o fechamento

Testado: pedir às três seções críticas que votem fora do pico. A 60 s o
fechamento vai a 17h51, contra 17h50 sem a medida — diferença nula.

Achatar a curva de chegada reduz muito o **pico de fila** (113 → 52 pessoas),
mas não reduz o **trabalho total**. A 60 s a urna 3313 precisa de 9,83 horas de
atendimento puro para uma janela de 9 horas.

**São dois problemas distintos, com ferramentas distintas:** tamanho de fila é
problema de curva de chegada (resolve-se com comunicação e layout); horário de
fechamento é problema de ciclo (resolve-se só com ciclo).

## 3. O único arranjo que fecha com caderno físico

O eleitor no exterior vota **só para Presidente**: o ato de votar é curto
(~22 s com liberação e deslocamento) e a busca no caderno domina o ciclo.
Isso significa que **a urna fica ociosa a maior parte do tempo — o gargalo é a
mesa, não o equipamento**.

| Arranjo | Ciclo nas urnas T1 | Urnas atrasadas | Fila total no pico | Fecha |
|---|---|---|---|---|
| Fila única, tudo serial (t_id 65 s) | 87 s | 16 / 28 | 2.296 | 22h15 |
| Pipeline: identifica B enquanto A vota | 65 s | 6 / 28 | 982 | 18h39 |
| **Dois cadernos em paralelo, um por seção** | **32 s** | **0 / 28** | **0** | **17h00** |

23 das 28 urnas acumulam **duas seções**, portanto **dois cadernos**. Com os
3 mesários que a mesa já tem, é possível operar **duas posições de
identificação em paralelo** alimentando uma única urna. O arranjo aguenta
mesmo com caderno muito lento (t_id de 110 s ainda fecha às 17h03).

As 5 urnas de seção única (3308, 3442, 3688, 3832, 3862) não paralelizam — mas
têm 110 s por eleitor de folga e não precisam.

**Esta é a negociação que resta abrir com o Cartório Eleitoral, e não custa
nada ao TRE:** nenhuma urna a mais, nenhum mesário a mais. Consta como risco
procedimental a validar na seção 3 de `contexto_eleicoes_dublin_2026.md`.

## 4. Estratificação das 28 urnas

Os tiers são as classes de carga de `scripts/decisoes.py`, as mesmas cores da
prancheta e do simulador: T1 = vermelho (as 3 maiores), T2 = amarelo
(esperado ≥ 450), T3 e T4 = verde.

| Tier | Urnas (MRV) | Esperado | s/eleitor disponível | Postura |
|---|---|---|---|---|
| **T1** | 3313 (22), 3322 (24), 3315 (23) | 586–590 | **55 s** | Recurso máximo. Duas posições de identificação obrigatórias. |
| **T2** | 3302 (16), 3306 (18), 3161 (11), 3245 (15), 3305 (17), 3108 (9), 3142 (10), 3311 (21) | 466–518 | 63–70 s | Duas posições recomendadas. |
| **T3** | 12 urnas (MRV 1–8, 12, 13, 14, 20) | 311–423 | 77–104 s | Padrão. |
| **T4** | 3688 (26), 3862 (28), 3832 (27), 3308 (19), 3442 (25) | 295–296 | 110 s | Reserva — origem de apoio redistribuível. |

**A folga de T3/T4 não absorve carga de T1**: o eleitor só vota na urna da sua
seção. Redistribui-se *recurso*, nunca *eleitor*. O plano tem de ser cirúrgico,
não uniforme.

## 5. Perfil do eleitorado (de `Filtrado_Dublin.csv`)

- **Eleitorado jovem:** 80% entre 25 e 49 anos. Apenas **211 eleitores com 60+
  anos em toda a zona** (1,3%) e **85 com deficiência declarada** (0,5%). A
  carga de atendimento prioritário é de ~7–8 pessoas por urna, não os 25–30%
  de uma seção doméstica. Isso torna um ciclo baixo realista.
- **Biometria: 54,6% da zona** (9.175 de 16.794) — mas **70%, 65% e 71% nas
  três urnas críticas**. As urnas com pior cobertura (511 com 21%, 512 com
  22%, 513 com 25%, 517 com 30%) estão todas em tiers com 84–97 s de folga. A
  urna 511 concentra 54 dos 211 eleitores 60+ e absorve isso sem problema.
- Nome social: 2 eleitores. Sem impacto de capacidade, mas exige orientação
  discreta aos mesários.

*Observação:* o campo indica biometria **coletada no cadastro**, não que
haverá leitor biométrico em Dublin. Confirmar com o Cartório.

## 6. Risco a verificar antes do dia

**A urna 3322 é simultaneamente uma urna T1 crítica e a que carrega o erro de
digitação documentado do TSE** — sua seção agregada 3752 aparece sob a
principal 3222 (seção do Porto) no PNG oficial. Se o erro se propagou para os
cadernos ou para a configuração da urna, a estação mais crítica do salão chega
mal configurada. Conferir contra o material final do TRE.

## 7. O espaço deixou de ser problema

28 estações em ~125 m de parede útil dão **passo de ~4,5 m por estação**,
contra os 1,36–1,46 m que preocupavam no cenário de 38 urnas. Perder a
negociação liberou área de piso. Essa área deve ser gasta deliberadamente em
posições de identificação em paralelo e em corredores de fila.
