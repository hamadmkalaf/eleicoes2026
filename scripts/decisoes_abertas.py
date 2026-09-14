"""Registro das decisoes de fluxo: o que esta em aberto, o que ja foi decidido
e como uma condiciona a outra.

`decisoes.py` guarda a configuracao vigente (portas, numeracoes, classes,
atribuicao das mesas, Ring 3 decidido). Este modulo guarda o registro:

  - as opcoes em cima da mesa, e qual delas as saidas de hoje assumem
    (`vigente`): e o que o dashboard, o simulador e as instrucoes de fluxo
    mostram enquanto a decisao nao sai (ou depois que saiu);
  - `estado`: "em aberto", "parcial", "decidida" ou "derivada" (nao e uma
    decisao: e um plano que sai das outras, como a equipe e a sinalizacao);
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

Estado em 13/09/2026 (tarde), pelo Posto: as UNICAS decisoes de fluxo por
tomar sao (a) como fazer a identificacao no caderno fisico e (b) checkpoint
ou sinalizacao por fitas. Portas (D1), Ring 3 (D3), unifilas (D4) e letra
(D8) estao decididas; porta preferencial, sinalizacao e voluntarios sao
planos derivados. Mudar uma decisao = trocar `vigente`, marcar `estado` e
regenerar o pipeline (§10 de DOCUMENTACAO_PROJETO.md).
"""
import json
import os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARQUIVO_JSON = os.path.join(RAIZ, "data", "decisoes_abertas.json")
ARQUIVO_MD = os.path.join(RAIZ, "docs", "decisoes_em_aberto.md")

REGISTRADO_EM = "2026-09-13"
ESTADOS = ("em aberto", "parcial", "decidida", "derivada")
ABERTOS = ("em aberto", "parcial")

# -------------------------------------------------------------- premissas ---
# Nao sao decisoes: sao restricoes que toda opcao abaixo respeita. So as duas
# que o Posto manteve em 13/09 (28 urnas, dimensoes, base B e estoque de
# separadores sairam do registro: sao fatos do plano, nao do fluxo).
FATOS = [
    {"id": "F2", "titulo": "Identificação por caderno físico",
     "texto": "Único método disponível no exterior. Impõe ≤ 55 s por eleitor nas três "
              "urnas críticas e ≤ 66–68 s nas sete seguintes para fechar às 17h; a 90 s, "
              "16 das 28 urnas estouram a janela.",
     "fonte": "contexto_eleicoes_dublin_2026.md §8.2"},
    {"id": "F3", "titulo": "4 seguranças + mesários voluntários + polícia fora",
     "texto": "Orçamento comporta 4 seguranças (não 20). A organização do fluxo fica com "
              "voluntários identificados; a polícia fica do lado de fora do recinto.",
     "fonte": "Posto, 13/09 · contexto §8.1 decisão 4"},
]

# --------------------------------------------------------------- decisoes ---
DECISOES = [
    {
        "id": "D9",
        "curto": "Caderno",
        "titulo": "(a) Como fazer a identificação no caderno físico",
        "pergunta": "Com 28 urnas e caderno físico, as três urnas críticas (MRV 22, 24, 23; "
                    "~590 comparecentes) só fecham às 17h a ≤ 55 s por eleitor. Como se "
                    "organiza a identificação na mesa receptora para chegar a esse ritmo?",
        "dono": "Posto + Cartório Eleitoral",
        "estado": "em aberto",
        "vigente": None,
        "depende_de": [],
        "restricoes": ["F2"],
        "fontes": ["PENDENCIAS item 5", "contexto_eleicoes_dublin_2026.md §8.2",
                   "DOCUMENTACAO_PROJETO.md §4.2 e §9.7"],
        "opcoes": [
            {"id": "unico", "rotulo": "(i) Caderno único em ordem alfabética, um mesário identificando",
             "resumo": "Hipótese do Posto sobre como o caderno chega (a confirmar). É o arranjo "
                       "que a simulação por urna trata como serial: a 55 s por eleitor, fecha "
                       "20h37 na mesa mais carregada.",
             "parametros": {"cadernos": 1, "identificadores": 1, "pipeline": False},
             "efeitos": {
                 "D2": "A mesa é o gargalo e retém por si só: o checkpoint só faz sentido como "
                       "válvula (reter por mesa) — as fitas no piso não ajudam a mesa.",
                 "D7": "Nada muda na equipe de piso; o esforço vai para a mesa (mesários).",
             }},
            {"id": "por_secao", "rotulo": "(ii) Caderno dividido por seção agregada, um mesário por caderno",
             "resumo": "23 das 28 urnas somam duas seções: dois cadernos, dois mesários "
                       "identificando em paralelo; o terceiro opera a urna. É o arranjo que "
                       "`simula_fluxo.py` chama de 'dois cadernos': fila zero, fecha 17h00.",
             "parametros": {"cadernos": 2, "identificadores": 2, "pipeline": True},
             "efeitos": {
                 "D2": "A mesa deixa de ser o gargalo; o checkpoint pode ser leve (2 por porta) "
                       "ou ceder lugar às fitas sem que a fila migre para dentro.",
                 "D7": "Pré-triagem precisa dizer ao eleitor a SEÇÃO, não só a mesa: o painel "
                       "seção → mesa ganha a coluna do caderno.",
             }},
            {"id": "por_letras", "rotulo": "(iii) Caderno dividido por faixa de letras, um mesário por faixa",
             "resumo": "Independe de como o caderno chega (se for único alfabético, corta-se ao "
                       "meio). Equilibra melhor que por seção quando uma seção é maior que a outra.",
             "parametros": {"cadernos": 2, "identificadores": 2, "pipeline": True},
             "efeitos": {
                 "D2": "Como (ii).",
                 "D7": "Placa da mesa com as faixas de letras (A–L / M–Z); orientador aponta a fila certa.",
             }},
            {"id": "pipeline", "rotulo": "(iv) Identificação em paralelo com o voto (o mesário localiza o próximo enquanto o anterior vota)",
             "resumo": "Um caderno só, mas o tempo de ciclo vira o maior entre identificação e "
                       "voto, não a soma. Fecha 17h01 a 55 s no modelo por urna. Depende de "
                       "disciplina de mesa, não de material.",
             "parametros": {"cadernos": 1, "identificadores": 1, "pipeline": True},
             "efeitos": {
                 "D2": "Mesa no limite (55 s): o checkpoint como válvula continua necessário "
                       "nas três críticas.",
                 "D7": "Treinamento dos mesários vira parte do plano de fluxo (webinar).",
             }},
            {"id": "pretriagem", "rotulo": "(v) Pré-triagem na fila: eleitor chega à mesa com documento na mão e seção sabida",
             "resumo": "Complementa qualquer das anteriores: tira da mesa os 10–20 s de "
                       "procurar documento e seção. Custa equipe na fila, não na mesa.",
             "parametros": {"cadernos": None, "identificadores": None, "pipeline": None},
             "efeitos": {
                 "D2": "Se houver checkpoint, a pré-triagem acontece nele; sem checkpoint, "
                       "acontece na fila da mesa, por orientador.",
                 "D7": "1 orientador a cada 3 mesas conferindo documento na fila.",
             }},
        ],
    },
    {
        "id": "D2",
        "curto": "Checkpoint ou fitas",
        "titulo": "(b) Checkpoint ou sinalização por fitas?",
        "pergunta": "Depois da porta, o eleitor passa por um ponto onde a equipe confere a "
                    "seção, aponta a mesa e retém quando a fila da mesa está cheia — ou "
                    "segue fitas no piso da porta à mesa, sem ponto de controle?",
        "dono": "Posto",
        "estado": "em aberto",
        "vigente": "checkpoint",
        "depende_de": ["D9"],
        "restricoes": ["F2", "F3"],
        "fontes": ["docs/registro_fitas_no_piso_2026-09-12.md", "docs/alternativa_fitas_no_piso.md",
                   "saidas/tensa_barreiras.md", "DOCUMENTACAO_PROJETO.md §4.3"],
        "opcoes": [
            {"id": "checkpoint", "rotulo": "Checkpoint: confere a seção e retém por mesa",
             "resumo": "Cenário Claude: a 16 m da porta, 3 atendentes por entrada, 10 s por "
                       "conferência; última mesa fecha às 17h03, P90 de 49 min, pico de 321 "
                       "pessoas dentro e 962 no Ring 3. No pico a porta B recebe 14,1 pessoas/min "
                       "e precisa de 3 posições. Variante leve: só informativo (aponta, não retém).",
             "parametros": {"existe": True, "modo": "valvula", "posicoes_por_porta": [2, 3],
                            "seg_por_conferencia": 10, "distancia_m": 16},
             "efeitos": {
                 "D4": "As divisórias do canal de entrada levam até o checkpoint (1e: 2 linhas "
                       "de 20 m + 6 bochechas); nos traçados em T (1f/1g/1h) o checkpoint fica "
                       "no topo do canal B.",
                 "D6": "O painel seção → mesa fica no checkpoint (P6); o eleitor lê parado, com a equipe ao lado.",
                 "D7": "6 a 9 pessoas em posições fixas (2–3 por porta), mais 1 supervisor do checkpoint.",
             }},
            {"id": "fitas", "rotulo": "Sinalização por fitas no piso, sem checkpoint",
             "resumo": "Simulado no motor oficial: fecha às 17h03 (mesmo horário), mas com porta "
                       "livre 950 pessoas ficam dentro do salão e 5.795 chegam a fila cheia; com "
                       "porta regulando às cegas o Ring 3 vai a 1.516–2.283. Perder-se custa 1–3 "
                       "min no P90. O checkpoint não custa vazão; o que ele faz é reter por mesa.",
             "parametros": {"existe": False, "modo": "nenhum", "posicoes_por_porta": [0, 0],
                            "seg_por_conferencia": 0, "distancia_m": 0},
             "efeitos": {
                 "D4": "Os postes do canal de entrada viram guia curta (1h: 5 m + braços de 3 m) e "
                       "as filas de mesa são a única contenção; fitas no piso por parede (214–463 m).",
                 "D6": "Painel seção → mesa na soleira da porta (10 s de leitura em pé) e placa alta "
                       "numerada em cada mesa, obrigatória.",
                 "D7": "6 a 9 orientadores volantes no salão; a resposta a uma fila de 40 pessoas "
                       "passa a ser deles, sem ponto de controle documentado para o Cartório.",
             }},
        ],
    },
    {
        "id": "D1",
        "curto": "Portas",
        "titulo": "Portas: quantas e quais",
        "pergunta": "Quantas portas da fachada sul recebem eleitor, e quais?",
        "dono": "Posto",
        "estado": "decidida",
        "vigente": "3portas",
        "depende_de": [],
        "restricoes": [],
        "fontes": ["scripts/decisoes.py", "simulador/portas.js", "DOCUMENTACAO_PROJETO.md §5.2"],
        "opcoes": [
            {"id": "3portas", "rotulo": "3 entradas (S4 A, S5 B, S6 C) e 2 saídas (S2, S8)",
             "resumo": "Decisão de 06/09, confirmada em 13/09. Vãos contíguos de 5,93 m; pico de "
                       "12,1 / 14,1 / 12,1 pessoas/min. O1 também fica fechada no dia.",
             "parametros": {"n_entradas": 3, "portas": ["S4", "S5", "S6"], "saidas": ["S2", "S8"]},
             "efeitos": {
                 "D3": "Três zonas no Ring 3, uma por entrada.",
                 "D4": "Dois canais de entrada partilham divisória: 2 linhas entre A|B e B|C.",
                 "D5": "Uma placa de porta por cabeça de zona (3) e três vinis de fachada (P5).",
                 "D6": "Um painel seção → mesa por porta (3).",
                 "D7": "1 marshal por porta (3) e 1 marshal por zona do Ring 3 (3).",
             }},
            {"id": "2portas", "rotulo": "2 portas (por exemplo S4 e S6)", "resumo": "Descartada em 13/09.",
             "parametros": {"n_entradas": 2, "portas": ["S4", "S6"], "saidas": ["S2", "S8"]}, "efeitos": {}},
            {"id": "4portas", "rotulo": "4 portas (S3 a S6 ou S4 a S7)", "resumo": "Descartada em 13/09.",
             "parametros": {"n_entradas": 4, "portas": ["S3", "S4", "S5", "S6"], "saidas": ["S2", "S8"]}, "efeitos": {}},
        ],
    },
    {
        "id": "D1b",
        "curto": "Porta preferencial",
        "titulo": "Rota preferencial (plano derivado)",
        "pergunta": "Eleitores prioritários (~296: 211 com 60+ e 85 PcD, ~33 por hora no pico) "
                    "entram por uma rota própria na mesma porta, por uma porta dedicada ou pela fila comum?",
        "dono": "Posto",
        "estado": "derivada",
        "vigente": "apron",
        "depende_de": ["D1"],
        "restricoes": ["F3"],
        "fontes": ["saidas/plano_ring3.md §10", "DOCUMENTACAO_PROJETO.md §5.7"],
        "opcoes": [
            {"id": "apron", "rotulo": "Rota prioritária pelo apron, com 1 agente, até a porta da sua zona",
             "resumo": "O que o plano do Ring 3 prevê: nenhum prioritário entra no serpenteado.",
             "parametros": {"rota": "apron", "porta_dedicada": None, "agentes": 1},
             "efeitos": {"D5": "Sinalizar a rota prioritária desde a rua (P0 e portão P1).",
                         "D7": "1 agente de acessibilidade no apron."}},
            {"id": "dedicada", "rotulo": "Porta dedicada (S3 ou S7)", "resumo": "Não adotada.",
             "parametros": {"rota": "porta", "porta_dedicada": "S3", "agentes": 2}, "efeitos": {}},
        ],
    },
    {
        "id": "D3",
        "curto": "Desenho do Ring 3",
        "titulo": "Desenho do Ring 3 e apoios da fita",
        "pergunta": "Qual desenho de fila externa, e com que barreira?",
        "dono": "Posto",
        "estado": "decidida",
        "vigente": "HP",
        "depende_de": ["D1"],
        "restricoes": [],
        "fontes": ["contexto_ring3_2026.md", "saidas/ring3.json", "saidas/plano_ring3_horizontal.md"],
        "opcoes": [
            {"id": "HP", "rotulo": "Raias leste-oeste, CCB só na ponta + fita grossa (1.964 pessoas)",
             "resumo": "Decidido em 13/09. Entrada pelo canto nordeste, corredor em L de 3,0 m. "
                       "82 separadores contados, registrados 100 para dar margem; nenhum a comprar; "
                       "576 m de fita grossa com 66 apoios a cada 5 m; 66 meias-voltas.",
             "parametros": {"ring3_json": "girado_ccb_na_ponta", "regime": "fita",
                            "corredor_em_L": True, "apoios_fita": 66, "separadores_registrados": 100},
             "efeitos": {
                 "D5": "As placas de porta vão nos CCB das pontas e na separação da zona C; o resto é fita.",
                 "D7": "Fita delimita, não contém: 1 marshal por zona no pico, mais 1 no L (cruzamento com S8).",
             }},
            {"id": "PV", "rotulo": "Plano vigente anterior: garganta ao sul, 3 serpenteados e 2 baias (1.402)",
             "resumo": "Superado em 13/09; continua sendo a fonte das quotas por entrada (mesma atribuição).",
             "parametros": {"ring3_json": "plano_vigente_reconstruido", "regime": "barreira",
                            "corredor_em_L": False, "apoios_fita": 0}, "efeitos": {}},
            {"id": "VS", "rotulo": "Raias norte-sul, barreira inteira (1.997)", "resumo": "Descartado: 371 separadores, 171 a comprar.",
             "parametros": {"ring3_json": "vertical_sem_baias", "regime": "barreira", "corredor_em_L": True, "apoios_fita": 0}, "efeitos": {}},
            {"id": "H", "rotulo": "Raias leste-oeste, barreira inteira (1.964)", "resumo": "Descartado: 371 separadores.",
             "parametros": {"ring3_json": "girado", "regime": "barreira", "corredor_em_L": True, "apoios_fita": 0}, "efeitos": {}},
            {"id": "VSP", "rotulo": "Raias norte-sul, CCB só na ponta + fita grossa (1.997)", "resumo": "Descartado: 115 apoios de fita.",
             "parametros": {"ring3_json": "vertical_ccb_na_ponta", "regime": "fita", "corredor_em_L": True, "apoios_fita": 115}, "efeitos": {}},
        ],
    },
    {
        "id": "D4",
        "curto": "Unifilas internas",
        "titulo": "Unifilas internas (postes Tensa)",
        "pergunta": "Onde vai a fita retrátil dentro do salão: no canal de entrada e nas filas de mesa. "
                    "Regra de mesa (13/09) em todos os traçados: par = uma linha de 4 m no meio; "
                    "não vermelha sem par = sem unifila; vermelha = 10 m.",
        "dono": "Posto",
        "estado": "decidida",
        "vigente": "1e",
        "depende_de": ["D1", "D2"],
        "restricoes": [],
        "fontes": ["saidas/tensa_barreiras.md", "saidas/tensa_barreiras.json", "registro_barreiras_hall2.md"],
        "opcoes": [
            {"id": "1e", "rotulo": "1e: duas divisórias de 20 m (A|B e B|C) até o checkpoint + regra de mesa",
             "resumo": "Adotado. As duas linhas que separam as três correntes da porta ao checkpoint, "
                       "com 6 bochechas de portão; nas mesas, a regra de 13/09.",
             "parametros": {"tensa": "1e", "canal": "meio", "canal_m": 20.0, "braco_m": 0.0,
                            "filas_mesa_m": {"par": 4.0, "polo": 10.0, "solta": 0.0}},
             "efeitos": {"D6": "Toda mesa pareada ou vermelha tem guia; as soltas verdes e amarelas dependem de placa alta e orientador.",
                         "D7": "Equipe segura a borda externa dos canais e as mesas sem guia."}},
            {"id": "1f", "rotulo": "1f: desenho em T — canal B isolado por 15 m, braços perpendiculares para oeste (fila A) e leste (fila C)",
             "resumo": "Duas linhas em x 25,18 e 31,40 da parede sul até 15 m; no metro 15, um braço "
                       "para oeste guia a fila A e um para leste guia a fila C (6 m cada, premissa).",
             "parametros": {"tensa": "1f", "canal": "T", "canal_m": 15.0, "braco_m": 6.0,
                            "filas_mesa_m": {"par": 4.0, "polo": 10.0, "solta": 0.0}},
             "efeitos": {"D6": "O painel seção → mesa fica no topo do T; A e C viram antes de ler.",
                         "D7": "1 orientador em cada braço do T no pico."}},
            {"id": "1g", "rotulo": "1g: T com canal B de 10 m",
             "resumo": "Como o 1f, com o canal B encurtado para 10 m; braços de 6 m.",
             "parametros": {"tensa": "1g", "canal": "T", "canal_m": 10.0, "braco_m": 6.0,
                            "filas_mesa_m": {"par": 4.0, "polo": 10.0, "solta": 0.0}},
             "efeitos": {"D6": "Como o 1f, com o painel a 10 m da porta.",
                         "D7": "Como o 1f."}},
            {"id": "1h", "rotulo": "1h: T com canal B de 5 m e braços de 3 m",
             "resumo": "O mínimo que ainda marca a virada: 5 m de canal e 3 m de braço.",
             "parametros": {"tensa": "1h", "canal": "T", "canal_m": 5.0, "braco_m": 3.0,
                            "filas_mesa_m": {"par": 4.0, "polo": 10.0, "solta": 0.0}},
             "efeitos": {"D6": "Painel a 5 m da porta; sinalização de piso ou placa alta obrigatória para A e C.",
                         "D7": "2 orientadores fixos no topo do T."}},
        ],
    },
    {
        "id": "D5",
        "curto": "Sinalização externa",
        "titulo": "Sinalização externa (plano derivado)",
        "pergunta": "P0, P1 e P2 penduradas nas paredes do RDS (aprovado). Placas nas CCBs do Ring 3 "
                    "dizendo, por porta, quais seções e mesas entram por ela.",
        "dono": "Posto",
        "estado": "derivada",
        "vigente": "ccb_por_porta",
        "depende_de": ["D1", "D1b", "D3", "D8"],
        "restricoes": [],
        "fontes": ["saidas/plano_sinalizacao.html", "DOCUMENTACAO_PROJETO.md §6"],
        "opcoes": [
            {"id": "ccb_por_porta", "rotulo": "P0–P2 nas paredes do RDS + uma placa por porta nas CCBs de cabeça de zona",
             "resumo": "Cada placa lista as seções e as mesas (número eleitor e MRV) que entram por aquela porta, com a letra da fila.",
             "parametros": {"placas_ccb": "por_porta", "p0_p2": "paredes_rds"},
             "efeitos": {"D7": "A placa na CCB responde \"é aqui?\" sem equipe; o marshal de zona só corrige quem errou."}},
        ],
    },
    {
        "id": "D6",
        "curto": "Sinalização interna",
        "titulo": "Sinalização interna (plano derivado)",
        "pergunta": "Painel seção → mesa (no checkpoint ou na soleira, conforme D2); placa do par de mesas "
                    "com as seções de cada mesa; placa alta com o número eleitor.",
        "dono": "Posto",
        "estado": "derivada",
        "vigente": "p6_atual",
        "depende_de": ["D1", "D2", "D4", "D8", "D9"],
        "restricoes": [],
        "fontes": ["DOCUMENTACAO_PROJETO.md §6.2 (P6, P7) e §6.6", "docs/alternativa_fitas_no_piso.md"],
        "opcoes": [
            {"id": "p6_atual", "rotulo": "P6 como está: 3 faixas suspensas por bloco + 28 totens de mesa + P7 nas saídas",
             "resumo": "O plano de sinalização de 05/09, agora com número eleitor em destaque e MRV oficial ao lado.",
             "parametros": {"painel_secao_mesa": "checkpoint", "placa_par": False, "placa_alta_mesa": False, "totens_mesa": 28},
             "efeitos": {"D7": "Sem placa alta, o eleitor que perde a fila pergunta: orientadores absorvem."}},
            {"id": "trelica", "rotulo": "Painel no checkpoint + placa do par suspensa nas treliças (14) + placa alta por mesa",
             "resumo": "Exige rigging autorizado pelo RDS e plataforma elevatória na véspera.",
             "parametros": {"painel_secao_mesa": "checkpoint", "placa_par": True, "placa_alta_mesa": True, "totens_mesa": 28},
             "efeitos": {"D7": "Menos consultas ao orientador com o salão cheio."}},
        ],
        "adicionais": [
            "Placa alta com o número eleitor (e o MRV oficial em corpo menor) em cada mesa, legível de 40 m.",
            "\"Fim da fila\" móvel para as mesas vermelhas (10 m) e placa \"esta fila: mesa n\".",
            "Saídas S2 e S8 (P7) e \"não volte pelo salão\".",
            "Balcão de dúvidas / \"não sei minha seção\" (em P1, fora; repetido no checkpoint).",
            "Rota prioritária e banheiros (portaloos) desde P0.",
        ],
    },
    {
        "id": "D7",
        "curto": "Voluntários",
        "titulo": "Voluntários de apoio (plano derivado)",
        "pergunta": "Quantas pessoas, em que postos e com que tarefa, para comunicar a sinalização, "
                    "orientar o eleitor e organizar as filas, com 4 seguranças fixos e polícia fora.",
        "dono": "Posto",
        "estado": "derivada",
        "vigente": "pico",
        "depende_de": ["D1", "D1b", "D2", "D3", "D4", "D5", "D6", "D9"],
        "restricoes": ["F3"],
        "fontes": ["docs/instrucoes_fluxo.md", "saidas/plano_ring3.md §11"],
        "opcoes": [
            {"id": "pico", "rotulo": "Equipe dimensionada para o pico, derivada das outras decisões",
             "resumo": "A tabela por posto sai de gera_instrucoes_fluxo.py.",
             "parametros": {"fator": 1.0, "orientador_por_mesas": 3}, "efeitos": {}},
            {"id": "minima", "rotulo": "Equipe mínima: 1 pessoa por posto", "resumo": "Não cobre o pico das 8h–10h.",
             "parametros": {"fator": 0.6, "orientador_por_mesas": 6}, "efeitos": {}},
        ],
    },
    {
        "id": "D8",
        "curto": "Letra",
        "titulo": "Identidade das filas: letra",
        "pergunta": "Como o eleitor reconhece a sua fila, do Ring 3 até a porta?",
        "dono": "Posto",
        "estado": "decidida",
        "vigente": "letra",
        "depende_de": [],
        "restricoes": [],
        "fontes": ["DOCUMENTACAO_PROJETO.md §6.3", "scripts/decisoes.py (NOMENCLATURA_PORTAS)"],
        "opcoes": [
            {"id": "letra", "rotulo": "Letra (A, B, C), como nos rótulos de planejamento",
             "resumo": "Decidido em 13/09. Coincide com o simulador, a prancheta e o Ring 3.",
             "parametros": {"identidade": "letra"},
             "efeitos": {"D5": "Letra em corpo grande nas placas de CCB e nos vinis de fachada.",
                         "D6": "Painel seção → mesa e placas de mesa com a letra da porta."}},
            {"id": "cor", "rotulo": "Cor (azul, âmbar, magenta)", "resumo": "Descartada em 13/09.",
             "parametros": {"identidade": "cor"}, "efeitos": {}},
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
        if d["estado"] not in ESTADOS:
            _erro(f"{d['id']}: estado {d['estado']!r} desconhecido")
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
        if d["vigente"] is None and d["estado"] in ("decidida", "derivada"):
            _erro(f"{d['id']}: {d['estado']} sem opcao vigente")
    condiciona = {k: [] for k in por_id}
    for d in DECISOES:
        for r in d["depende_de"]:
            condiciona[r].append(d["id"])
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
        d["aberta"] = d["estado"] in ABERTOS
        d["opcoes"] = [dict(o) for o in d["opcoes"]]
        for o in d["opcoes"]:
            o["vigente"] = (o["id"] == d["vigente"])
        saida.append(d)
    abertas = [d["id"] for d in saida if d["aberta"]]
    if not abertas:
        _erro("nenhuma decisao em aberto: confira os estados")
    return {
        "registradoEm": REGISTRADO_EM,
        "fatos": [dict(f) for f in FATOS],
        "ordem": ordem,
        "camadas": camadas,
        "abertas": abertas,
        "decididas": [d["id"] for d in saida if d["estado"] == "decidida"],
        "derivadas": [d["id"] for d in saida if d["estado"] == "derivada"],
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
    vig = {d["id"]: next((o for o in d["opcoes"] if o["vigente"]), None) for d in reg["decisoes"]}
    L = []
    L.append("# Decisões de fluxo: as que faltam, as que já saíram e como uma condiciona a outra\n")
    L.append(f"> Gerado por `scripts/decisoes_abertas.py` (registro de {reg['registradoEm']}). Não editar à mão: "
             "mudar uma decisão é editar o módulo e regenerar. A seção \"Decisões\" do dashboard e "
             "`docs/instrucoes_fluxo.md` saem do mesmo registro.\n")
    L.append("## Premissas\n")
    for f in reg["fatos"]:
        L.append(f"- **{f['titulo']}.** {f['texto']} ({f['fonte']})")
    L.append("\n## Decisões em aberto\n")
    for k in reg["abertas"]:
        d = por_id[k]
        L.append(f"### {d['id']} — {d['titulo']}\n")
        L.append(f"**Pergunta.** {d['pergunta']}\n")
        L.append(f"Dono: {d['dono']} · depende de: " + (", ".join(d["depende_de"]) or "nada")
                 + " · condiciona: " + (", ".join(d["condiciona"]) or "nada") + "\n")
        for o in d["opcoes"]:
            marca = " **← o que as saídas de hoje assumem**" if o["vigente"] else ""
            L.append(f"- **{o['rotulo']}**{marca}  \n  {o['resumo']}")
            for alvo, txt in o["efeitos"].items():
                L.append(f"  - se esta: **{alvo}** → {txt}")
        L.append("\nFontes: " + " · ".join(f"`{f}`" for f in d["fontes"]) + "\n")
    L.append("## Decididas em 13/09/2026\n")
    L.append("| Decisão | Escolha | Resumo |\n|---|---|---|")
    for k in reg["decididas"]:
        d, o = por_id[k], vig[k]
        L.append(f"| **{d['id']}** {d['titulo']} | {o['rotulo']} | {o['resumo']} |")
    L.append("\n## Planos derivados (não são decisões)\n")
    for k in reg["derivadas"]:
        d, o = por_id[k], vig[k]
        L.append(f"- **{d['id']} {d['titulo']}** — {o['rotulo']}. {o['resumo']}")
        if d.get("adicionais"):
            for a in d["adicionais"]:
                L.append(f"  - {a}")
    L.append("\n## Matriz \"se … então …\" (opções das decisões em aberto)\n")
    alvos = [k for k in reg["ordem"] if any(k in o["efeitos"] for kk in reg["abertas"] for o in por_id[kk]["opcoes"])]
    L.append("| Se … | " + " | ".join(f"{a} {por_id[a]['curto']}" for a in alvos) + " |")
    L.append("|---|" + "---|" * len(alvos))
    for k in reg["abertas"]:
        for o in por_id[k]["opcoes"]:
            if not o["efeitos"]:
                continue
            L.append(f"| **{k}** = {o['rotulo']} | " + " | ".join(o["efeitos"].get(a, "") for a in alvos) + " |")
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
    print("em aberto:", ", ".join(reg["abertas"]), "| decididas:", ", ".join(reg["decididas"]),
          "| derivadas:", ", ".join(reg["derivadas"]))
    print("ordem:", " > ".join(" · ".join(c) for c in reg["camadas"]))
    for d in reg["decisoes"]:
        v = next((o["id"] for o in d["opcoes"] if o["vigente"]), "—")
        print(f"  {d['id']:<4} {d['estado']:<9} vigente={v:<14} depende_de={','.join(d['depende_de']) or '—':<26} "
              f"condiciona={','.join(d['condiciona']) or '—'}")


if __name__ == "__main__":
    main()
