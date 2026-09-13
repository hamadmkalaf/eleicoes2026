"""Registro das decisoes de fluxo ainda em aberto e de como uma condiciona a outra.

`decisoes.py` guarda o que o Posto JA decidiu (portas, numeracao, classes,
atribuicao das mesas). Este modulo guarda o que AINDA NAO foi decidido, com:

  - as opcoes em cima da mesa, e qual delas as saidas de hoje assumem
    (`vigente`): e o que o dashboard, o simulador e as instrucoes de fluxo
    mostram enquanto a decisao nao sai;
  - `depende_de`: as decisoes que precisam sair antes desta (o inverso,
    `condiciona`, e calculado, nunca digitado);
  - `efeitos`: para cada opcao, o que ela impoe as decisoes que ela condiciona,
    com os numeros das pecas de onde vieram;
  - `parametros`: a leitura da opcao por maquina, que
    `gera_instrucoes_fluxo.py` e o dashboard usam.

`montar()` valida o registro (ids, referencias, grafo aciclico, uma opcao
vigente por decisao) e devolve tudo num dicionario serializavel; `main()`
grava `data/decisoes_abertas.json` e `docs/decisoes_em_aberto.md`. Falha em
vez de gravar saida inconsistente, como os outros geradores.

Mudar uma decisao (o Posto escolheu) = trocar `vigente`, marcar `estado` como
"decidida" e regenerar o pipeline (§10 de DOCUMENTACAO_PROJETO.md).

Registro aberto em 13/09/2026, a partir da lista do Posto (portas, checkpoint,
Ring 3, unifilas, sinalizacao externa e interna, voluntarios) mais a pendencia
antiga de cor ou letra (§9.8 item 8 da documentacao).
"""
import json
import os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARQUIVO_JSON = os.path.join(RAIZ, "data", "decisoes_abertas.json")
ARQUIVO_MD = os.path.join(RAIZ, "docs", "decisoes_em_aberto.md")

REGISTRADO_EM = "2026-09-13"

# ------------------------------------------------------------- fatos fixos ---
# Nao sao decisoes: sao restricoes que toda opcao abaixo tem de respeitar.
FATOS = [
    {"id": "F1", "titulo": "28 urnas, 51 seções, 16.794 aptos",
     "texto": "Configuração oficial do TSE (CSV de 13/08/2026). Desagregar as seções de "
              "Dublin não é mais viável (Posto, 13/09). Três urnas Dublin+Dublin com "
              "~590 comparecentes esperados cada: MRV 22 (3313), 24 (3322), 23 (3315).",
     "fonte": "saidas/dados.json · contexto_eleicoes_dublin_2026.md §8.1"},
    {"id": "F2", "titulo": "Identificação por caderno físico",
     "texto": "Único método disponível no exterior. Impõe ≤ 55 s por eleitor nas três "
              "urnas críticas e ≤ 66–68 s nas sete seguintes para fechar às 17h; a 90 s, "
              "16 das 28 urnas estouram a janela. O arranjo da mesa (cadernos, quem "
              "identifica) é a pendência 5 do PENDENCIAS, sem recomendação ainda.",
     "fonte": "contexto_eleicoes_dublin_2026.md §8.2 · PENDENCIAS item 5"},
    {"id": "F3", "titulo": "4 seguranças + mesários voluntários + polícia fora",
     "texto": "Orçamento comporta 4 seguranças (não 20). A organização do fluxo fica com "
              "voluntários identificados; a polícia fica do lado de fora do recinto.",
     "fonte": "Posto, 13/09 · contexto §8.1 decisão 4"},
    {"id": "F4", "titulo": "Hall 2 50,0 × 44,5 m · Ring 3 44,0 × 35,0 m",
     "texto": "Dimensões reais confirmadas. Ring 3 a 14 m ao sul da fachada; posição "
              "lateral centrada em S5 por estimativa (bordo oeste a aferir).",
     "fonte": "RDS_Hall_2_Floorplan · contexto_ring3_2026.md §1"},
    {"id": "F5", "titulo": "Comparecimento esperado 11.499 (base B)",
     "texto": "Taxa de 2022 por domicílio de origem, aplicada aos aptos de 2026. Não é "
              "oficial; todos os cenários usam a mesma base. Pico por porta 12,1 / 14,1 / "
              "12,1 pessoas por minuto com três entradas.",
     "fonte": "scripts/comparecimento.py · registro_barreiras_hall2.md §3"},
    {"id": "F6", "titulo": "200 CCB externos em mãos + 100 unifilas internos contratados",
     "texto": "Os separadores de barreira externa (2 m, da organizadora do RDS) servem o "
              "Ring 3 e podem ser comprados a mais (EUR 13,02/un.). Os 100 postes Tensa "
              "do item d) do orçamento são a fita interna do Hall 2 e são outra coisa.",
     "fonte": "DOCUMENTACAO_PROJETO.md §5.4 · contexto_ring3_2026.md §3.8"},
]

# --------------------------------------------------------------- decisoes ---
DECISOES = [
    {
        "id": "D1",
        "curto": "Portas",
        "titulo": "Portas: quantas e quais",
        "pergunta": "Quantas portas da fachada sul recebem eleitor, e quais? Cada porta é "
                    "uma corrente de fila desde o Ring 3 até o checkpoint.",
        "dono": "Posto",
        "estado": "em aberto",
        "vigente": "3portas",
        "depende_de": [],
        "restricoes": ["F4", "F5"],
        "fontes": ["scripts/decisoes.py", "simulador/portas.js", "DOCUMENTACAO_PROJETO.md §5.2"],
        "opcoes": [
            {"id": "3portas", "rotulo": "3 portas: S4 (A), S5 (B), S6 (C)",
             "resumo": "Decisão de 06/09. Vãos contíguos de 5,93 m com 0,29 m entre eles; "
                       "pico de 12,1 / 14,1 / 12,1 pessoas/min. É o que todas as peças assumem.",
             "parametros": {"n_entradas": 3, "portas": ["S4", "S5", "S6"], "saidas": ["S2", "S8"]},
             "efeitos": {
                 "D3": "Três zonas no Ring 3 (A 11,2 · B 14,0 · C 11,2 m no desenho N–S; "
                       "8/10/8 raias). O módulo vivo já redesenha N zonas para N portas.",
                 "D4": "Dois canais de entrada partilham divisória: bastam 2 linhas de 20 m "
                       "entre A|B e B|C (22 postes), sem bordas externas no 1e.",
                 "D5": "Uma placa de porta por cabeça de zona (3) e três vinis de fachada (P5).",
                 "D6": "Um painel seção → mesa por porta (3) na entrada do salão.",
                 "D7": "1 marshal por porta (3) e 1 marshal por zona do Ring 3 (3).",
             }},
            {"id": "2portas", "rotulo": "2 portas (por exemplo S4 e S6)",
             "resumo": "Menos canais e menos equipe de porta; cada corrente recebe ~18 pessoas/min "
                       "no pico e cada zona do Ring 3 precisa guardar ~1.000 pessoas.",
             "parametros": {"n_entradas": 2, "portas": ["S4", "S6"], "saidas": ["S2", "S8"]},
             "efeitos": {
                 "D3": "Duas zonas, cada uma com ~20 m de largura: 14 raias por zona no N–S; a "
                       "lotação total não muda, a caminhada por zona sobe.",
                 "D4": "Uma só divisória de entrada (11 postes) e canais mais largos; a "
                       "conferência no checkpoint precisa de 4 posições por porta a 10 s.",
                 "D5": "Duas placas de cabeça de zona, dois vinis; a tabela mestra muda a coluna de porta.",
                 "D6": "Dois painéis seção → mesa; cada painel lista 14 mesas.",
                 "D7": "2 marshals de porta, 2 de zona; checkpoint com 8 posições ao todo.",
             }},
            {"id": "4portas", "rotulo": "4 portas (S3 a S6 ou S4 a S7)",
             "resumo": "Mais capilaridade: ~9 pessoas/min por porta. S3 e S7 têm recuo de "
                       "emergência a confirmar (docs/CONTEXTO.md §9.3).",
             "parametros": {"n_entradas": 4, "portas": ["S3", "S4", "S5", "S6"], "saidas": ["S2", "S8"]},
             "efeitos": {
                 "D3": "Quatro zonas de ~10 m: 7 raias por zona no N–S; mais meias-voltas e "
                       "mais divisórias curtas (o L–O passa a custar mais que o N–S).",
                 "D4": "Três divisórias de entrada (33 postes) e 4 canais; o 1e perde 11 postes de folga.",
                 "D5": "Quatro placas de cabeça de zona, quatro vinis de fachada.",
                 "D6": "Quatro painéis seção → mesa, com 7 mesas cada.",
                 "D7": "4 marshals de porta, 4 de zona; checkpoint com 2 posições por porta.",
             }},
        ],
    },
    {
        "id": "D1b",
        "curto": "Porta preferencial",
        "titulo": "Porta ou rota preferencial",
        "pergunta": "Eleitores prioritários (~296: 211 com 60+ e 85 PcD, ~33 por hora no pico) "
                    "entram por uma porta própria, por uma rota própria na mesma porta, ou "
                    "pela fila comum?",
        "dono": "Posto",
        "estado": "em aberto",
        "vigente": "apron",
        "depende_de": ["D1"],
        "restricoes": ["F3"],
        "fontes": ["saidas/plano_ring3.md §10", "DOCUMENTACAO_PROJETO.md §5.7"],
        "opcoes": [
            {"id": "apron", "rotulo": "Rota prioritária pelo apron, com 1 agente, até a porta da sua zona",
             "resumo": "O que o plano do Ring 3 prevê: nenhum prioritário entra no serpenteado "
                       "(130 m de percurso); do desembarque direto à porta, pavimentado.",
             "parametros": {"rota": "apron", "porta_dedicada": None, "agentes": 1},
             "efeitos": {
                 "D5": "Sinalizar a rota prioritária desde a rua (P0 e portão P1); nenhuma placa de porta a mais.",
                 "D7": "1 agente de acessibilidade no apron; o marshal de porta recebe o prioritário fora de fila.",
             }},
            {"id": "dedicada", "rotulo": "Porta dedicada (S3 ou S7), fora das correntes",
             "resumo": "Isola o prioritário da corrente de chegada que desce pelo apron leste "
                       "(hoje cruza a saída S8). Exige checkpoint próprio ou painel na soleira.",
             "parametros": {"rota": "porta", "porta_dedicada": "S3", "agentes": 2},
             "efeitos": {
                 "D5": "Uma placa de porta a mais (\"Atendimento prioritário\") e vinil na fachada; "
                       "rota sinalizada desde P0.",
                 "D7": "2 pessoas: 1 na porta dedicada, 1 conduzindo do portão; a porta precisa "
                       "de posição de conferência própria.",
             }},
            {"id": "nenhuma", "rotulo": "Sem rota própria: prioridade tratada na cabeça de cada fila",
             "resumo": "Menos equipe, mas 296 pessoas atravessam o apron sem guia e a cabeça "
                       "de fila precisa negociar a passagem a cada caso.",
             "parametros": {"rota": "fila", "porta_dedicada": None, "agentes": 0},
             "efeitos": {
                 "D5": "Placa \"prioridade: apresente-se ao marshal\" em P4 (cabeça de cada zona).",
                 "D7": "Nenhum agente dedicado; cada marshal de zona absorve ~11 casos por hora no pico.",
             }},
        ],
    },
    {
        "id": "D2",
        "curto": "Checkpoint",
        "titulo": "Checkpoint interno",
        "pergunta": "Depois da porta, existe um ponto onde a equipe confere a seção do eleitor "
                    "e o encaminha à mesa? Ele retém quando a fila da mesa está cheia?",
        "dono": "Posto",
        "estado": "em aberto",
        "vigente": "valvula",
        "depende_de": [],
        "restricoes": ["F2", "F5"],
        "fontes": ["docs/registro_fitas_no_piso_2026-09-12.md", "docs/alternativa_fitas_no_piso.md",
                   "saidas/tensa_barreiras.md", "DOCUMENTACAO_PROJETO.md §4.3"],
        "opcoes": [
            {"id": "valvula", "rotulo": "(a) Manter o checkpoint como válvula: confere e retém por mesa",
             "resumo": "Cenário Claude: a 16 m da porta, 3 atendentes por entrada, 10 s por "
                       "conferência; última mesa fecha às 17h03, P90 de 49 min, pico de 321 "
                       "pessoas dentro e 962 no Ring 3. No pico a porta B recebe 14,1 pessoas/min "
                       "e precisa de 3 posições.",
             "parametros": {"existe": True, "modo": "valvula", "posicoes_por_porta": [2, 3],
                            "seg_por_conferencia": 10, "distancia_m": 16},
             "efeitos": {
                 "D3": "O Ring 3 recebe só o que o checkpoint devolve: pico de 962 no Ring 3 "
                       "(cabe em qualquer desenho de 1.402 ou mais).",
                 "D4": "Mantém as duas divisórias de 20 m e as 6 bochechas de portão do 1e "
                       "(28 postes presos ao checkpoint).",
                 "D6": "O painel seção → mesa fica no checkpoint (P6); o eleitor lê parado, com a equipe ao lado.",
                 "D7": "6 a 9 pessoas em posições fixas (2–3 por porta), mais 1 supervisor do checkpoint.",
             }},
            {"id": "informativo", "rotulo": "(b) Checkpoint só informativo: painel e equipe apontam, ninguém retém",
             "resumo": "Guarda o ponto de consulta e a presença da equipe, mas a porta deixa de "
                       "regular por mesa: a fila migra para dentro do salão quando uma mesa lota.",
             "parametros": {"existe": True, "modo": "informativo", "posicoes_por_porta": [1, 1],
                            "seg_por_conferencia": 10, "distancia_m": 16},
             "efeitos": {
                 "D3": "A porta regula pela soma das filas de mesa, não por mesa: pico no Ring 3 sobe "
                       "para ~1.500 (cenário \"buffer\" do simulador).",
                 "D4": "As divisórias de entrada continuam; as bochechas de portão viram só guia. "
                       "Filas de mesa passam a ser a única contenção: 1e ou C.",
                 "D6": "Painel seção → mesa no mesmo lugar, maior, lido em movimento; placa alta por mesa.",
                 "D7": "1 orientador por porta no ponto informativo e 3 a 6 volantes no salão.",
             }},
            {"id": "nenhum", "rotulo": "(c) Eliminar o checkpoint: fitas no piso da porta à mesa",
             "resumo": "Simulado no motor oficial: fecha às 17h03 (mesmo horário), mas com porta "
                       "livre 950 pessoas ficam dentro do salão e 5.795 chegam a fila cheia; com "
                       "porta regulando às cegas o Ring 3 vai a 1.516–2.283. Perder-se custa 1–3 "
                       "min no P90. O checkpoint não custa vazão; o que ele faz é reter por mesa.",
             "parametros": {"existe": False, "modo": "nenhum", "posicoes_por_porta": [0, 0],
                            "seg_por_conferencia": 0, "distancia_m": 0},
             "efeitos": {
                 "D3": "Ring 3 precisa guardar 1.516 a 2.283 no pico (porta regulando às cegas) ou "
                       "o salão recebe 950: só os desenhos de ~2.000 servem, e a fita de "
                       "contorno não contém.",
                 "D4": "Libera os 28 postes do checkpoint para filas de mesa de 5/8/12 m; as filas "
                       "de mesa viram a única contenção (1 conflito geométrico no Três polos).",
                 "D6": "Painel seção → mesa na soleira da porta (10 s de leitura em pé) e placa alta "
                       "numerada em cada mesa, obrigatória; fitas no piso por parede (214–463 m).",
                 "D7": "6 a 9 orientadores volantes no salão; a resposta a uma fila de 40 pessoas "
                       "passa a ser deles, sem ponto de controle documentado para o Cartório.",
             }},
        ],
    },
    {
        "id": "D3",
        "curto": "Desenho do Ring 3",
        "titulo": "Desenho do Ring 3 e apoios da fita",
        "pergunta": "Qual desenho de fila externa, e com que barreira? Se a divisória for fita "
                    "com CCB só na ponta, quantos apoios a fita leva?",
        "dono": "Posto",
        "estado": "em aberto",
        "vigente": "PV",
        "depende_de": ["D1", "D2"],
        "restricoes": ["F4", "F6"],
        "fontes": ["contexto_ring3_2026.md", "saidas/ring3.json", "saidas/plano_ring3_horizontal.md",
                   "saidas/plano_ring3.md"],
        "opcoes": [
            {"id": "PV", "rotulo": "Plano vigente: garganta de pré-triagem ao sul, 3 serpenteados e 2 baias (1.402)",
             "resumo": "Calculado a 39 × 35 m; é o que decisoes.py usa para as quotas por entrada "
                       "(445/513/445). 300 separadores (314 na reconstrução a 44 × 35), 100 a comprar.",
             "parametros": {"ring3_json": "plano_vigente_reconstruido", "regime": "barreira",
                            "corredor_em_L": False, "apoios_fita": 0},
             "efeitos": {
                 "D5": "P3 (garganta) e P4 (cabeças) continuam existindo; 300 CCB disponíveis para placas.",
                 "D7": "3 agentes de pré-triagem na garganta (gargalo potencial) + 3 marshals de corredor.",
             }},
            {"id": "VS", "rotulo": "Raias norte-sul, barreira inteira, corredor em L (1.997)",
             "resumo": "Entrada pelo canto nordeste, corredor em L de 3,0 m, raias de 32 m. "
                       "371 separadores, 171 a comprar (EUR 2.226); 160 m de fita no contorno.",
             "parametros": {"ring3_json": "vertical_sem_baias", "regime": "barreira",
                            "corredor_em_L": True, "apoios_fita": 0},
             "efeitos": {
                 "D5": "A pré-triagem sai do Ring 3: P3 migra para o portão e o corredor leste; "
                       "371 CCB para pendurar as placas de porta nas cabeças de zona.",
                 "D7": "Sem garganta: pré-triagem a montante (portão) com 2–3 pessoas; 1 marshal "
                       "por zona; 1 no L, onde a corrente de chegada cruza a saída S8.",
             }},
            {"id": "H", "rotulo": "Raias leste-oeste, barreira inteira, corredor em L (1.964)",
             "resumo": "Mesmos 371 separadores; descarga da zona B alinhada com o eixo de S5 "
                       "(desvio 0,0 m contra 5,5 m no N–S); 66 meias-voltas.",
             "parametros": {"ring3_json": "girado", "regime": "barreira",
                            "corredor_em_L": True, "apoios_fita": 0},
             "efeitos": {
                 "D5": "Como o N–S; a placa de porta fica na borda norte, no portão de descarga.",
                 "D7": "Como o N–S; mais meias-voltas exigem mais atenção do marshal de zona.",
             }},
            {"id": "VSP", "rotulo": "Raias norte-sul, CCB só na ponta + fita grossa (1.997)",
             "resumo": "39 separadores, nenhum a comprar, 662 m de fita grossa. Cada divisória "
                       "fica com 28,8 m de fita sem apoio: a 5 m são 115 apoios; se forem CCB, "
                       "o total volta a 154.",
             "parametros": {"ring3_json": "vertical_ccb_na_ponta", "regime": "fita",
                            "corredor_em_L": True, "apoios_fita": 115},
             "efeitos": {
                 "D5": "Só 39 CCB, nas cabeças e na separação da zona C: as placas de porta vão "
                       "exatamente ali; o resto é fita e não segura placa.",
                 "D7": "Fita delimita, não contém: 1 marshal por zona no pico, obrigatório, "
                       "mais 1 no L; sem eles a fila passa de A para B.",
             }},
            {"id": "HP", "rotulo": "Raias leste-oeste, CCB só na ponta + fita grossa (1.964)",
             "resumo": "82 separadores, nenhum a comprar, 576 m de fita grossa; 66 divisórias curtas.",
             "parametros": {"ring3_json": "girado_ccb_na_ponta", "regime": "fita",
                            "corredor_em_L": True, "apoios_fita": 0},
             "efeitos": {
                 "D5": "82 CCB, um por ponta de divisória: mais pontos de fixação para placas.",
                 "D7": "Como o N–S com fita; divisórias de 11–14 m precisam de menos apoio.",
             }},
        ],
    },
    {
        "id": "D4",
        "curto": "Unifilas internas",
        "titulo": "Unifilas internas (postes Tensa)",
        "pergunta": "Onde vai a fita retrátil dentro do salão: nas filas de mesa, nos canais "
                    "da porta ao checkpoint, nos dois, ou só num deles?",
        "dono": "Posto",
        "estado": "em aberto",
        "vigente": "1e",
        "depende_de": ["D1", "D2"],
        "restricoes": ["F2", "F6"],
        "fontes": ["saidas/tensa_barreiras.md", "saidas/propostas_alternativas.md",
                   "registro_barreiras_hall2.md", "saidas/tensa_barreiras.json"],
        "opcoes": [
            {"id": "1e", "rotulo": "1e: linha no meio de cada par + linha por mesa sem par + 2 divisórias até o checkpoint",
             "resumo": "Adotado em 07/09: 100 postes (111 com reserva), 146 m de fita, EUR 1.745 "
                       "ex-VAT. Sem as bordas externas dos canais: sinalização e equipe seguram o eleitor no canal.",
             "parametros": {"tensa": "1e", "filas_mesa_m": {"alta": 10, "media": 5, "baixa": 3},
                            "mesas_sem_guia": 0},
             "efeitos": {
                 "D6": "Toda mesa tem guia; a placa alta por mesa é reforço, não necessidade.",
                 "D7": "1 orientador para cada 3 mesas; equipe segura a borda externa dos canais "
                       "de entrada. A 60 s por voto, 12 mesas transbordam em 14–19 min de pico.",
             }},
            {"id": "1i", "rotulo": "1i: mesma topologia, filas dimensionadas para 20 min de pico",
             "resumo": "126 postes (139 com reserva): as mesas de média sobem de 5 para 6–7,5 m. "
                       "O par 17–18 não tem os 7,5 m na parede leste.",
             "parametros": {"tensa": "1i", "filas_mesa_m": {"alta": 10, "media": 7, "baixa": 3},
                            "mesas_sem_guia": 0},
             "efeitos": {
                 "D6": "Como o 1e.",
                 "D7": "Menos gestão de piso nas mesas de média; 26 postes a mais.",
             }},
            {"id": "A", "rotulo": "A: só as duas divisórias da porta ao checkpoint (28 postes)",
             "resumo": "Nenhuma barreira nas 28 mesas: da triagem em diante o eleitor circula "
                       "solto e a ordem nas mesas fica com a equipe. EUR 1.200 a menos que o 1e.",
             "parametros": {"tensa": "A", "filas_mesa_m": {"alta": 0, "media": 0, "baixa": 0},
                            "mesas_sem_guia": 28},
             "efeitos": {
                 "D6": "Placa alta numerada em todas as 28 mesas, obrigatória: sem canal, a placa é o único guia.",
                 "D7": "5 orientadores a mais só para as mesas (1 para cada 3 que acumulam); "
                       "se pagos, EUR 1.569, e o total (2.114) passa o 1e.",
             }},
            {"id": "B", "rotulo": "B: só pares e polos (47 postes), nada na entrada",
             "resumo": "Linha do meio de cada par e os três polos; as três correntes chegam "
                       "juntas ao checkpoint. 7 mesas sem guia (3.028 esperados).",
             "parametros": {"tensa": "B", "filas_mesa_m": {"alta": 10, "media": 5, "baixa": 3},
                            "mesas_sem_guia": 7},
             "efeitos": {
                 "D6": "Placa alta nas 7 mesas sem guia (5, 6, 9, 12, 15, 16, 21).",
                 "D7": "Sem divisórias de entrada, as 3 correntes se misturam antes do checkpoint: "
                       "1 marshal por porta dentro do salão, além dos orientadores das mesas soltas.",
             }},
            {"id": "B2", "rotulo": "B2: B mais as de média sem par (63 postes)",
             "resumo": "As mesas 9, 15, 16 e 21 contam como grandes e ganham linha; sobram 3 "
                       "mesas sem guia (1.079 esperados).",
             "parametros": {"tensa": "B2", "filas_mesa_m": {"alta": 10, "media": 5, "baixa": 3},
                            "mesas_sem_guia": 3},
             "efeitos": {
                 "D6": "Placa alta nas 3 mesas sem guia (5, 6, 12).",
                 "D7": "Como B, com menos mesas para a equipe cobrir.",
             }},
            {"id": "C", "rotulo": "C: síntese — divisórias do checkpoint + pares + polos (75 postes)",
             "resumo": "O 1e sem as sete linhas das mesas soltas. O único corte que o documento "
                       "de hipóteses recomenda: EUR 1.325 ex-VAT, 17 postes de folga.",
             "parametros": {"tensa": "C", "filas_mesa_m": {"alta": 10, "media": 5, "baixa": 3},
                            "mesas_sem_guia": 7},
             "efeitos": {
                 "D6": "Placa alta nas 7 mesas sem guia (5, 6, 9, 12, 15, 16, 21).",
                 "D7": "Os 7 postos das mesas soltas passam à equipe: 2 a 3 orientadores para elas.",
             }},
        ],
    },
    {
        "id": "D5",
        "curto": "Sinalização externa",
        "titulo": "Sinalização externa (parcialmente aprovada)",
        "pergunta": "P0, P1 e P2 vão penduradas nas paredes do RDS (aprovado). Falta: as "
                    "placas nas CCBs do Ring 3 dizendo, por porta, quais seções e mesas "
                    "entram por ela. Quantas, onde e com que identidade de fila?",
        "dono": "Posto",
        "estado": "parcial",
        "vigente": "ccb_por_porta",
        "depende_de": ["D1", "D1b", "D3", "D8"],
        "restricoes": ["F1"],
        "fontes": ["saidas/plano_sinalizacao.html", "DOCUMENTACAO_PROJETO.md §6", "scripts/gera_plano_sinalizacao.py"],
        "opcoes": [
            {"id": "ccb_por_porta", "rotulo": "P0–P2 nas paredes do RDS + uma placa por porta nas CCBs de cabeça de zona",
             "resumo": "Cada placa lista as seções (51 linhas no total, ordenadas por seção) e as "
                       "mesas que entram por aquela porta, com a identidade da fila (D8). "
                       "Substitui os totens de P3/P4 nos desenhos sem garganta.",
             "parametros": {"placas_ccb": "por_porta", "p0_p2": "paredes_rds"},
             "efeitos": {
                 "D7": "A placa na CCB responde \"é aqui?\" sem equipe; o marshal de zona só corrige "
                       "quem errou (captura em P4).",
             }},
            {"id": "sem_ccb", "rotulo": "P0–P2 nas paredes do RDS e nada nas CCBs (só os totens de P4)",
             "resumo": "Menos peças impressas; a confirmação da fila depende da equipe e dos "
                       "totens da cabeça de cada serpenteado.",
             "parametros": {"placas_ccb": "nenhuma", "p0_p2": "paredes_rds"},
             "efeitos": {
                 "D7": "Mais consultas ao marshal de zona (\"é esta a minha fila?\"): 1 pessoa a mais por zona no pico.",
             }},
        ],
    },
    {
        "id": "D6",
        "curto": "Sinalização interna",
        "titulo": "Sinalização interna (a elaborar)",
        "pergunta": "O que sinalizar dentro do salão: (1) a distribuição das seções por mesa, "
                    "no checkpoint ou na porta; (2) o par de mesas e as seções de cada mesa; "
                    "(3) o que mais.",
        "dono": "Posto",
        "estado": "em aberto",
        "vigente": "p6_atual",
        "depende_de": ["D1", "D2", "D4", "D8"],
        "restricoes": ["F1"],
        "fontes": ["DOCUMENTACAO_PROJETO.md §6.2 (P6, P7) e §6.6", "docs/alternativa_fitas_no_piso.md"],
        "opcoes": [
            {"id": "p6_atual", "rotulo": "P6 como está: 3 faixas suspensas por bloco + 28 totens de mesa + P7 nas saídas",
             "resumo": "O plano de sinalização de 05/09; nada foi acrescentado desde então. É o "
                       "mínimo que o dashboard assume.",
             "parametros": {"painel_secao_mesa": "checkpoint", "placa_par": False,
                            "placa_alta_mesa": False, "totens_mesa": 28},
             "efeitos": {
                 "D7": "Sem placa alta, o eleitor que perde a fila pergunta: orientadores volantes absorvem.",
             }},
            {"id": "trelica", "rotulo": "Painel seção → mesa no checkpoint + placa do par suspensa nas treliças (14) + placa alta por mesa",
             "resumo": "Por par de mesas, 14 peças em vez de 28, penduradas nas treliças a 7 m "
                       "(as paredes não aceitam adesivo). Exige rigging autorizado pelo RDS e "
                       "plataforma elevatória na véspera; não obstruir luminária de emergência, "
                       "detector de fumaça nem placa de EXIT.",
             "parametros": {"painel_secao_mesa": "checkpoint", "placa_par": True,
                            "placa_alta_mesa": True, "totens_mesa": 28},
             "efeitos": {
                 "D7": "A placa alta é visível com 300 a 950 pessoas dentro; menos consultas ao orientador.",
             }},
            {"id": "soleira", "rotulo": "Painel seção → mesa na soleira da porta + placa alta por mesa + fitas no piso",
             "resumo": "A variante para D2 = (c): leitura em pé na soleira (10 s), erro de "
                       "10–25 % assumido; fitas no piso por parede (214 m) ou pela atribuição "
                       "da decisão (463 m, 18 cruzamentos).",
             "parametros": {"painel_secao_mesa": "soleira", "placa_par": True,
                            "placa_alta_mesa": True, "totens_mesa": 28},
             "efeitos": {
                 "D7": "Orientadores volantes no salão (6–9) em vez de posições fixas.",
             }},
        ],
        "adicionais": [
            "Placa alta numerada (MRV) em cada mesa, legível de 40 m com o salão cheio.",
            "\"Fim da fila\" móvel para as mesas de 10 m (polos) e placa \"esta fila: MRV n\".",
            "Saídas S2 e S8 (P7) e \"não volte pelo salão\".",
            "Balcão de dúvidas / \"não sei minha seção\" (em P1, fora; repetido no checkpoint).",
            "Rota prioritária e banheiros (portaloos) desde P0.",
            "Identidade da fila (cor ou letra) coerente com a raia do Ring 3 até a porta.",
        ],
    },
    {
        "id": "D7",
        "curto": "Voluntários",
        "titulo": "Voluntários de apoio: quantos, onde, tarefas",
        "pergunta": "Quantas pessoas, em que postos e com que tarefa, para comunicar a "
                    "sinalização, orientar o eleitor e organizar as filas, com 4 seguranças "
                    "fixos e polícia fora.",
        "dono": "Posto",
        "estado": "em aberto",
        "vigente": "pico",
        "depende_de": ["D1", "D1b", "D2", "D3", "D4", "D5", "D6"],
        "restricoes": ["F3"],
        "fontes": ["saidas/plano_ring3.md §11", "DOCUMENTACAO_PROJETO.md §5.7",
                   "saidas/propostas_alternativas.md", "docs/instrucoes_fluxo.md"],
        "opcoes": [
            {"id": "pico", "rotulo": "Equipe dimensionada para o pico, derivada das outras decisões",
             "resumo": "A tabela por posto sai das opções vigentes de D1–D6 (gera_instrucoes_fluxo.py): "
                       "portão, corredor, zonas, portas, checkpoint, salão, saídas, acessibilidade.",
             "parametros": {"fator": 1.0, "orientador_por_mesas": 3},
             "efeitos": {}},
            {"id": "minima", "rotulo": "Equipe mínima: 1 pessoa por posto, sem reforço de pico",
             "resumo": "Cobre a sinalização mas não o pico das 8h–10h; as filas de mesa de média "
                       "transbordam em 14 min sem ninguém para redirecionar.",
             "parametros": {"fator": 0.6, "orientador_por_mesas": 6},
             "efeitos": {}},
        ],
    },
    {
        "id": "D8",
        "curto": "Cor ou letra",
        "titulo": "Identidade das filas: cor ou letra",
        "pergunta": "Como o eleitor reconhece a sua fila, do Ring 3 até a porta: por cor "
                    "(azul, âmbar, magenta), por letra (A, B, C) ou pelas duas?",
        "dono": "Posto",
        "estado": "em aberto",
        "vigente": None,
        "depende_de": [],
        "restricoes": [],
        "fontes": ["DOCUMENTACAO_PROJETO.md §6.3 e §9.8 item 8", "scripts/decisoes.py (nomenclatura_portas)"],
        "opcoes": [
            {"id": "cor", "rotulo": "Cor (azul, âmbar, magenta; distinguíveis em deuteranopia e protanopia)",
             "resumo": "Evita duas nomenclaturas por letra no mesmo recinto (o RDS chama os "
                       "portões de Gate D, Gate G).",
             "parametros": {"identidade": "cor"},
             "efeitos": {"D5": "Faixa de cor nas placas de CCB e nos vinis de fachada.",
                         "D6": "Painel seção → mesa e placa de mesa com a faixa de cor da porta."}},
            {"id": "letra", "rotulo": "Letra (A, B, C), como nos rótulos de planejamento",
             "resumo": "Coincide com o simulador, a prancheta e o Ring 3; risco de confusão com Gate D/G.",
             "parametros": {"identidade": "letra"},
             "efeitos": {"D5": "Letra em corpo grande nas placas de CCB e nos vinis.",
                         "D6": "Painel e placas com a letra da porta."}},
            {"id": "ambas", "rotulo": "Cor e letra juntas",
             "resumo": "Redundância que custa só na diagramação; a letra fala, a cor se vê de longe.",
             "parametros": {"identidade": "ambas"},
             "efeitos": {"D5": "Faixa de cor + letra em todas as peças externas.",
                         "D6": "Faixa de cor + letra em todas as peças internas."}},
        ],
    },
]


# --------------------------------------------------------------- validacao ---
def _erro(msg):
    raise SystemExit("decisoes_abertas: " + msg)


def _ordem_topologica(decs):
    """Camadas de Kahn: cada camada so depende das anteriores. Falha se houver ciclo."""
    pend = {d["id"]: set(d["depende_de"]) for d in decs}
    camadas = []
    while pend:
        livres = sorted(k for k, v in pend.items() if not v)
        if not livres:
            _erro(f"ciclo entre {sorted(pend)}")
        camadas.append(livres)
        for k in livres:
            del pend[k]
        for v in pend.values():
            v.difference_update(livres)
    return camadas


def montar():
    ids = [d["id"] for d in DECISOES]
    if len(ids) != len(set(ids)):
        _erro("ids repetidos")
    fatos = {f["id"] for f in FATOS}
    por_id = {d["id"]: d for d in DECISOES}
    for d in DECISOES:
        for r in d["depende_de"]:
            if r not in por_id:
                _erro(f"{d['id']} depende de {r}, que nao existe")
            if r == d["id"]:
                _erro(f"{d['id']} depende de si mesma")
        for r in d["restricoes"]:
            if r not in fatos:
                _erro(f"{d['id']} cita o fato {r}, que nao existe")
        oids = [o["id"] for o in d["opcoes"]]
        if len(oids) != len(set(oids)):
            _erro(f"{d['id']}: opcoes repetidas")
        if d["vigente"] is not None and d["vigente"] not in oids:
            _erro(f"{d['id']}: vigente {d['vigente']} nao e opcao")
        if d["vigente"] is None and d["estado"] == "decidida":
            _erro(f"{d['id']}: decidida sem opcao vigente")
    # condiciona = inverso de depende_de (calculado)
    condiciona = {k: [] for k in por_id}
    for d in DECISOES:
        for r in d["depende_de"]:
            condiciona[r].append(d["id"])
    # todo efeito aponta para uma decisao que depende desta
    for d in DECISOES:
        for o in d["opcoes"]:
            for alvo in o["efeitos"]:
                if alvo not in por_id:
                    _erro(f"{d['id']}/{o['id']}: efeito sobre {alvo}, que nao existe")
                if d["id"] not in por_id[alvo]["depende_de"]:
                    _erro(f"{d['id']}/{o['id']}: efeito sobre {alvo}, mas {alvo} nao depende de {d['id']}")
    camadas = _ordem_topologica(DECISOES)
    ordem = [k for c in camadas for k in c]
    saida = []
    for k in ordem:
        d = dict(por_id[k])
        d["condiciona"] = sorted(condiciona[k], key=ordem.index)
        d["camada"] = next(i for i, c in enumerate(camadas) if k in c)
        d["opcoes"] = [dict(o) for o in d["opcoes"]]
        for o in d["opcoes"]:
            o["vigente"] = (o["id"] == d["vigente"])
        saida.append(d)
    return {
        "registradoEm": REGISTRADO_EM,
        "fatos": [dict(f) for f in FATOS],
        "ordem": ordem,
        "camadas": camadas,
        "decisoes": saida,
    }


def vigentes(reg=None):
    """{id: opcao vigente (dict) ou None} -- o que as saidas de hoje assumem."""
    reg = reg or montar()
    out = {}
    for d in reg["decisoes"]:
        out[d["id"]] = next((o for o in d["opcoes"] if o["vigente"]), None)
    return out


def parametros(reg=None):
    """{id: parametros da opcao vigente} (vazio quando nao ha vigente)."""
    return {k: (o["parametros"] if o else {}) for k, o in vigentes(reg).items()}


# ---------------------------------------------------------------- markdown ---
def markdown(reg):
    por_id = {d["id"]: d for d in reg["decisoes"]}
    L = []
    L.append("# Decisões de fluxo em aberto e como uma condiciona a outra\n")
    L.append(f"> Gerado por `scripts/decisoes_abertas.py` em {reg['registradoEm']}. Não editar à mão: "
             "mudar uma decisão é editar o módulo e regenerar. A seção \"Decisões em aberto\" do "
             "dashboard e `docs/instrucoes_fluxo.md` saem do mesmo registro.\n")
    L.append("## Fatos fixos (restrições que toda opção respeita)\n")
    L.append("| # | Fato | O que impõe | Fonte |\n|---|---|---|---|")
    for f in reg["fatos"]:
        L.append(f"| {f['id']} | **{f['titulo']}** | {f['texto']} | {f['fonte']} |")
    L.append("\n## Ordem recomendada de decisão\n")
    L.append("Cada camada só depende das anteriores; decidir fora da ordem obriga a rever a camada seguinte.\n")
    for i, c in enumerate(reg["camadas"]):
        L.append(f"{i + 1}. " + " · ".join(f"**{k}** {por_id[k]['titulo']}" for k in c))
    L.append("\n## As decisões\n")
    for d in reg["decisoes"]:
        L.append(f"### {d['id']} — {d['titulo']}\n")
        L.append(f"**Pergunta.** {d['pergunta']}\n")
        L.append(f"Estado: **{d['estado']}** · dono: {d['dono']} · depende de: "
                 + (", ".join(d["depende_de"]) or "nada") + " · condiciona: "
                 + (", ".join(d["condiciona"]) or "nada")
                 + (" · restrições: " + ", ".join(d["restricoes"]) if d["restricoes"] else "") + "\n")
        for o in d["opcoes"]:
            marca = " **← o que as saídas de hoje assumem**" if o["vigente"] else ""
            L.append(f"- **{o['rotulo']}**{marca}  \n  {o['resumo']}")
            for alvo, txt in o["efeitos"].items():
                L.append(f"  - se esta: **{alvo}** → {txt}")
        if d.get("adicionais"):
            L.append("\nSinalizações adicionais a prever:")
            for a in d["adicionais"]:
                L.append(f"- {a}")
        L.append("\nFontes: " + " · ".join(f"`{f}`" for f in d["fontes"]) + "\n")
    L.append("## Matriz \"se … então …\"\n")
    L.append("Linhas: opção de uma decisão. Colunas: decisões que ela condiciona.\n")
    alvos = [k for k in reg["ordem"] if any(k in o["efeitos"] for d in reg["decisoes"] for o in d["opcoes"])]
    L.append("| Se … | " + " | ".join(alvos) + " |")
    L.append("|---|" + "---|" * len(alvos))
    for d in reg["decisoes"]:
        for o in d["opcoes"]:
            if not o["efeitos"]:
                continue
            cel = [o["efeitos"].get(a, "") for a in alvos]
            L.append(f"| **{d['id']}** = {o['rotulo']} | " + " | ".join(cel) + " |")
    return "\n".join(L) + "\n"


def main():
    reg = montar()
    os.makedirs(os.path.dirname(ARQUIVO_JSON), exist_ok=True)
    with open(ARQUIVO_JSON, "w", encoding="utf-8") as f:
        json.dump(reg, f, ensure_ascii=False, indent=1)
        f.write("\n")
    os.makedirs(os.path.dirname(ARQUIVO_MD), exist_ok=True)
    with open(ARQUIVO_MD, "w", encoding="utf-8") as f:
        f.write(markdown(reg))
    print("gravado", os.path.relpath(ARQUIVO_JSON, RAIZ), "e", os.path.relpath(ARQUIVO_MD, RAIZ))
    print("ordem:", " > ".join(" · ".join(c) for c in reg["camadas"]))
    for d in reg["decisoes"]:
        v = next((o["id"] for o in d["opcoes"] if o["vigente"]), "—")
        print(f"  {d['id']:<4} {d['estado']:<9} vigente={v:<14} depende_de={','.join(d['depende_de']) or '—':<22} "
              f"condiciona={','.join(d['condiciona']) or '—'}")


if __name__ == "__main__":
    main()
