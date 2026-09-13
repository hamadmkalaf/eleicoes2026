"""Instrucoes de gerenciamento de fluxo para o treinamento da equipe, geradas.

Principio (Posto, 13/09/2026): o fluxo deve correr o mais desimpedido
possivel, so com orientacao ao eleitor. A equipe aponta, nao barra; retencao
so onde o plano vigente preve.

Nenhum numero e digitado a mao. O documento le:
  - scripts/decisoes.py            portas, entradas, mesas por entrada, classes
  - scripts/decisoes_abertas.py    a opcao VIGENTE de cada decisao em aberto
  - saidas/dados.json              as 28 urnas
  - saidas/ring3.json              lotacao por zona do desenho vigente (D3)
  - saidas/tensa_barreiras.json    filas de mesa e folego do tracado vigente (D4)
  - saidas/varredura_top.json      o cenario do simulador (fechamento, P90)
  - saidas/fitas_piso.json         o cenario sem checkpoint, quando D2 = nenhum
e grava docs/instrucoes_fluxo.md e saidas/instrucoes_fluxo.html. Quando uma
decisao vigente ou uma saida muda, o documento muda; o rodape diz o que
mudaria em cada alternativa.

Uso: python3 scripts/gera_instrucoes_fluxo.py   (depois de decisoes_abertas.py,
antes de gera_dashboard.py)
"""
import html
import json
import math
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "scripts"))
SAIDAS = os.path.join(RAIZ, "saidas")
ARQUIVO_MD = os.path.join(RAIZ, "docs", "instrucoes_fluxo.md")
ARQUIVO_HTML = os.path.join(SAIDAS, "instrucoes_fluxo.html")
ARQUIVO_DEC_HTML = os.path.join(SAIDAS, "decisoes_em_aberto.html")

import decisoes as DC                                         # noqa: E402
import decisoes_abertas as DA                                 # noqa: E402

JANELA_MIN = 9 * 60          # 8h-17h
FATOR_PICO = 1.8             # pico = 1,8 x a media (premissa do simulador e das barreiras)
SEGURANCAS = 4               # decisao do Posto de 13/09 (fato F3)
# Prioritarios: 211 com 60+ e 85 PcD na zona (saidas/plano_ring3.md, secao 10).
PRIORITARIOS = {"idosos": 211, "pcd": 85}


def fmt(n):
    return f"{int(round(n)):,}".replace(",", ".")


def vg(v, c=1):
    return f"{v:.{c}f}".replace(".", ",")


def carrega(nome):
    with open(os.path.join(SAIDAS, nome), encoding="utf-8") as f:
        return json.load(f)


# ------------------------------------------------------------- derivacoes ---
def pico_por_min(esperado):
    return esperado * FATOR_PICO / JANELA_MIN


def equipe(dec, P, r3d, tb_cen, n_ent):
    """Tabela de equipe por posto, derivada das opcoes vigentes."""
    f = P["D7"].get("fator", 1.0)
    por_mesas = P["D7"].get("orientador_por_mesas", 3)
    chk = P["D2"]
    em_L = P["D3"].get("corredor_em_L", False)
    sem_guia = P["D4"].get("mesas_sem_guia", 0)
    n_mesas = len(dec["mesas"])
    linhas = []

    def add(posto, n, tarefa, reporta="coordenação"):
        linhas.append({"posto": posto, "n": max(1, int(math.ceil(n * f))) if n else 0,
                       "tarefa": tarefa, "reporta": reporta})

    add("Coordenação geral", 1, "Decide toda retenção; único ponto que autoriza fechar uma porta ou segurar uma zona.", "Posto")
    if em_L:
        add("Portão da Merrion Road (pré-triagem)", 3,
            "Recebe, confirma que o eleitor sabe a seção e a fila; quem não sabe vai ao balcão. "
            "Não conferem documento: apontam.")
    else:
        add("Garganta sudeste do Ring 3 (pré-triagem)", 3,
            "Entregam o cartão de roteamento e dividem nos serpenteados. Gargalo potencial: dimensionar para o pico.")
    add("Balcão \"não sei minha seção\" (P1)", 1, "Consulta a tabela mestra de 51 seções e devolve seção → mesa → fila.")
    add("Corredor da lateral leste (P2)", 1, "Mantém a corrente andando; repete a consulta a quem parou.")
    add(f"Ring 3: marshal por zona ({n_ent})", n_ent,
        "Segura a cabeça de fila e a passagem entre zonas (a fita delimita, não contém); corrige quem errou de fila enquanto cabe.")
    if em_L:
        add("Ring 3: cruzamento do corredor em L com a saída S8", 1,
            "Separa a corrente que desce pelo apron leste de quem já votou e sai por S8.")
    add(f"Portas de entrada ({n_ent})", n_ent,
        "Libera pelo ritmo combinado; conversa com o interior do salão; recebe prioritários fora de fila.")
    if chk.get("existe") and chk.get("modo") == "valvula":
        pos = chk["posicoes_por_porta"][1] * n_ent
        add(f"Checkpoint: posições de conferência ({chk['posicoes_por_porta'][0]}–{chk['posicoes_por_porta'][1]} por porta)", pos,
            f"Confere a seção em ~{chk['seg_por_conferencia']} s, aponta a mesa e retém só se a fila da mesa estiver no limite.")
        add("Checkpoint: supervisor", 1, "Redistribui posições entre portas conforme a carga; fala com a coordenação.")
    elif chk.get("existe"):
        add("Ponto informativo (1 por porta)", n_ent, "Aponta o painel seção → mesa; não retém ninguém.")
    if not chk.get("existe"):
        add("Salão: orientadores volantes", max(6, int(math.ceil(n_mesas / por_mesas))),
            "Sem checkpoint, são a única resposta a uma fila de mesa que cresce: redirecionam e chamam a coordenação.")
    else:
        add("Salão: orientadores de piso (norte, leste, oeste)", 3 + int(math.ceil(sem_guia / 3)),
            "Um por parede; mais um a cada três mesas sem guia. Mantêm o eleitor no canal e a fila da mesa dentro da fita.")
    add("Saídas S2 e S8", len(dec["saidas"]), "Encaminham para a rua; ninguém volta pelo salão nem reentra no Ring 3.")
    ag = P["D1b"].get("agentes", 0)
    if ag:
        add("Acessibilidade e prioridade", ag,
            "Conduz idosos e PcD pela rota prioritária; fala com o marshal de porta para a entrada fora de fila.")
    total_vol = sum(l["n"] for l in linhas)
    linhas.append({"posto": f"Seguranças contratados ({SEGURANCAS})", "n": SEGURANCAS,
                   "tarefa": "Controle de acesso e resposta a incidente. Proposta de postos: 2 no portão e no acesso, "
                             "1 na fachada das entradas, 1 nas saídas. Não organizam fila.", "reporta": "coordenação"})
    linhas.append({"posto": "Polícia", "n": 0, "tarefa": "Do lado de fora do recinto (formato a confirmar).", "reporta": "—"})
    return linhas, total_vol


# ---------------------------------------------------------------- documento --
def documento():
    dec = DC.montar()
    reg = DA.montar()
    P = DA.parametros(reg)
    V = DA.vigentes(reg)
    dados = carrega("dados.json")
    r3 = carrega("ring3.json")
    tb = carrega("tensa_barreiras.json")
    varr = carrega("varredura_top.json")
    fitas = carrega("fitas_piso.json") if os.path.exists(os.path.join(SAIDAS, "fitas_piso.json")) else None

    ent = dec["entradas"]
    n_ent = len(ent)
    if P["D1"].get("n_entradas") not in (None, n_ent):
        raise SystemExit(f"D1 vigente tem {P['D1']['n_entradas']} entradas, decisoes.py tem {n_ent}: alinhe os dois")
    r3d = r3[P["D3"]["ring3_json"]]
    tb_cen = next(c for c in tb["cenarios"] if c["nome"] == P["D4"]["tensa"])
    melhor = varr[0]
    chk = P["D2"]
    ident = P["D8"].get("identidade")
    ident_txt = {"cor": "a cor da fila", "letra": "a letra da fila", "ambas": "a cor e a letra da fila"}.get(ident, "a identidade da fila (cor ou letra, ainda sem decisão: D8)")
    altas = sorted([m for m in dec["mesas"] if m["classe"] == "alta"], key=lambda m: -m["esperado"])
    comp = tb["premissas"]["comprimentos"]
    folego = {f["n"]: f for f in tb["folego"]}
    zonas = {z["entrada"]: z for z in r3d["zonas"]} if r3d.get("zonas") else {}
    cap_zona = {}
    for e in ent:
        z = zonas.get(e["id"])
        # no plano vigente a zona e so o serpenteado; a baia de flanco entra na
        # capacidade por entrada de decisoes.py (445/513/445)
        if z and not r3d.get("capacidade_baias"):
            cap_zona[e["id"]] = int(round(z["capacidade"]))
        else:
            cap_zona[e["id"]] = e["capacidade"]
    eq, total_vol = equipe(dec, P, r3d, tb_cen, n_ent)

    L = []
    L.append("# Instruções de gerenciamento de fluxo — treinamento da equipe\n")
    L.append(f"> Gerado por `scripts/gera_instrucoes_fluxo.py` a partir das decisões vigentes "
             f"(`decisoes.py`, `decisoes_abertas.py`, registro de {reg['registradoEm']}) e das saídas do plano. "
             "Não editar à mão: quando uma decisão muda, o documento muda. O rodapé diz o que mudaria em cada alternativa.\n")
    L.append("Vale para o 1º turno, 4 de outubro de 2026, das 8h às 17h, no RDS Ballsbridge (Hall 2 e Ring 3). "
             f"Comparecimento esperado: {fmt(dec['comparecimento']['total'])} eleitores em {len(dec['mesas'])} mesas; "
             f"entradas {', '.join(e['porta'] + ' (' + e['id'] + ')' for e in ent)}; saídas {' e '.join(dec['saidas'])}.\n")

    L.append("## 0. Princípio\n")
    L.append("**O fluxo corre o mais desimpedido possível. A equipe orienta o eleitor; não o retém.**\n")
    L.append("- Aponte, não barre. Toda pessoa da equipe responde três perguntas: *qual é a minha fila*, *qual é a minha mesa*, *por onde saio*.")
    L.append("- Ninguém para o eleitor para conferir documento fora da mesa receptora" + (" e do checkpoint" if chk.get("existe") and chk.get("modo") == "valvula" else "") + ".")
    if chk.get("existe") and chk.get("modo") == "valvula":
        L.append("- A única retenção prevista é a do checkpoint, e só quando a fila da mesa de destino estiver no limite. Qualquer outra retenção é decisão da coordenação.")
    else:
        L.append("- Nenhuma retenção está prevista no plano vigente. Se uma fila crescer além do limite, a resposta é redirecionar e chamar a coordenação, não segurar.")
    L.append("- Quem tem prioridade (idosos, PcD, gestantes, lactantes, pessoas com criança de colo) não entra em fila de espera: vai pela rota prioritária.")
    L.append("- Colete de identificação sempre. Falar baixo e curto; apontar com o braço inteiro; repetir a instrução, não discutir.\n")

    L.append("## 1. Portão da Merrion Road e pré-triagem (P0, P1)\n")
    if P["D3"].get("corredor_em_L"):
        L.append("A pré-triagem acontece **no portão e no corredor da lateral leste**, não dentro do Ring 3 (o desenho vigente do Ring 3 não tem garganta).")
    else:
        L.append("A pré-triagem acontece **na garganta sudeste do Ring 3**, onde 3 agentes entregam o cartão de roteamento; o portão só confirma que o eleitor está no lugar certo.")
    L.append("- O que dizer: \"Eleições brasileiras, entrada por aqui. Sabe o número da sua seção? Então procure na tabela: seção → mesa → " + ident_txt + ".\"")
    L.append("- Quem não sabe a seção vai ao balcão \"não sei minha seção\" (P1), fora da corrente; não se resolve isso na fila.")
    L.append("- Eleitor do interior (Cork, Galway, Limerick…) procura o nome do condado no índice, não o número da seção.")
    rota = P["D1b"].get("rota")
    if rota == "apron":
        L.append(f"- Prioritários (~{fmt(PRIORITARIOS['idosos'] + PRIORITARIOS['pcd'])} no dia, ~{fmt((PRIORITARIOS['idosos'] + PRIORITARIOS['pcd']) / 9)} por hora no pico): o agente de acessibilidade conduz pelo apron pavimentado direto à porta da sua zona. Nenhum entra no serpenteado.")
    elif rota == "porta":
        L.append(f"- Prioritários: porta dedicada {P['D1b'].get('porta_dedicada')}, com conferência própria; conduzir desde o portão.")
    else:
        L.append("- Prioritários: apresentam-se ao marshal da cabeça da sua fila, que os passa à frente.")
    L.append("")

    L.append("## 2. Corredor da lateral leste e chegada ao Ring 3 (P2)\n")
    L.append("- A consulta seção → mesa → fila está repetida a cada 25–30 m no corredor. O eleitor decide **andando**; ninguém para na porta.")
    if P["D3"].get("corredor_em_L"):
        L.append("- O eleitor entra no Ring 3 pelo **canto nordeste**, desce rente ao gradil leste (trecho lateral de 3,0 m) e vira no fundo (trecho de fundo de 3,0 m): é o corredor em L. Do fundo, entra na sua zona.")
        L.append("- **Cruzamento com a saída S8:** a corrente que desce pelo apron leste divide o espaço com quem já votou e sai por S8. Um marshal fica no cruzamento e mantém os dois fluxos separados; quem sai vai para a rua, nunca para o Ring 3.")
    else:
        L.append("- O eleitor entra no Ring 3 pela garganta sudeste, recebe o cartão de roteamento e segue pelo corredor de distribuição até o seu serpenteado (C primeiro, depois B, depois A).")
    L.append("")

    L.append("## 3. Ring 3: uma zona por entrada\n")
    L.append(f"Desenho vigente: **{r3d['nome']}** — lotação {fmt(r3d['capacidade'])} pessoas, {r3d['separadores']} separadores"
             + (f", {vg(r3d['fita_grossa_m'], 0)} m de fita grossa" if r3d.get("fita_grossa_m") else "") + ".\n")
    L.append("| Zona | Porta | Cabe na zona | Esperados no dia | Pico (pessoas/min) | Mesas (MRV) |\n|---|---|---|---|---|---|")
    for e in ent:
        L.append(f"| {e['id']} | {e['porta']} | {fmt(cap_zona[e['id']])} | {fmt(e['esperado'])} | {vg(pico_por_min(e['esperado']))} | {', '.join(str(m) for m in e['mrvs'])} |")
    L.append("")
    L.append("- **A fita delimita, não contém.** O que mantém a zona A separada da B é o marshal da cabeça de fila. Num pico, ninguém passa de uma zona para outra sem ele.")
    L.append("- Quem errou de fila é corrigido na cabeça da zona (P4), enquanto ainda cabe voltar; depois da meia-volta, vai até a porta e o marshal de porta o encaminha.")
    L.append("- Meias-voltas: o marshal mantém o vão livre (1,20 m); guarda-chuvas fechados nas raias.")
    L.append(f"- **Gatilho:** zona com mais gente do que cabe ({', '.join(e['id'] + ' ' + fmt(cap_zona[e['id']]) for e in ent)}) → avisar a coordenação; a resposta é abrir ritmo na porta, nunca fechar a entrada da zona.")
    L.append("- Evacuação: as barreiras laterais são removíveis; sai-se pelos vãos entre zonas e pelo gradil. O marshal da zona abre, não conduz.\n")

    L.append(f"## 4. Portas de entrada ({', '.join(e['porta'] for e in ent)})\n")
    lib = melhor["cen"].get("liberacao", "buffer")
    lib_txt = {"buffer": "libera enquanto houver lugar nas filas de mesa do lado de dentro (é o que o simulador chama de liberação por buffer)",
               "livre": "libera sem contenção", "mesa": "libera só quem tem vaga na sua mesa"}.get(lib, lib)
    L.append(f"- Um marshal por porta. A porta {lib_txt}.")
    L.append(f"- Ritmo de pico por porta: {' · '.join(e['id'] + ' ' + vg(pico_por_min(e['esperado'])) + '/min' for e in ent)}. Acima disso, avisar a coordenação antes de segurar.")
    L.append("- Na soleira só se confirma " + ident_txt + ". Nenhuma informação nova é dada na porta.")
    L.append("- Prioritários entram fora de fila, pela mão do agente de acessibilidade.\n")

    if chk.get("existe") and chk.get("modo") == "valvula":
        L.append(f"## 5. Checkpoint (a {chk['distancia_m']} m da porta)\n")
        L.append(f"- {chk['posicoes_por_porta'][0]} a {chk['posicoes_por_porta'][1]} posições por porta, ~{chk['seg_por_conferencia']} s por eleitor. "
                 f"No pico a porta mais carregada recebe {vg(max(pico_por_min(e['esperado']) for e in ent))}/min: com {chk['seg_por_conferencia']} s por conferência cada posição atende {60 // chk['seg_por_conferencia']}, "
                 f"logo essa porta precisa de {math.ceil(max(pico_por_min(e['esperado']) for e in ent) / (60 / chk['seg_por_conferencia']))} posições.")
        L.append("- O que se faz: lê a seção (ou o cartão), diz o número da mesa e aponta a direção. Não se confere documento aqui.")
        L.append(f"- **Quando reter:** só se a fila da mesa de destino estiver no limite ({comp['alta']:.0f} m nas três críticas, {comp['media']:.0f} m nas de média, {comp['baixa']:.0f} m nas de baixa). Reter é segurar na posição por um ou dois minutos e liberar; não é formar fila nova.")
        L.append("- Quem não encontra a seção no painel vai ao balcão de dúvidas do checkpoint, fora da posição.\n")
    elif chk.get("existe"):
        L.append("## 5. Ponto informativo depois da porta\n")
        L.append("- Uma pessoa por porta aponta o painel seção → mesa e a direção. Ninguém é retido. Uma fila de mesa que cresce é problema dos orientadores do salão.\n")
    else:
        L.append("## 5. Sem checkpoint: fitas no piso da porta à mesa\n")
        fb = next((r for r in (fitas or {}).get("resultados", []) if r["id"] == "fitas-buffer"), None)
        if fb:
            L.append(f"- Simulado: fecha às {fb['fechaP50']}, espera P90 de {fb['p90TotalMin']} min, pico de {fmt(fb['dentroMax'])} dentro e {fmt(fb['ring3Max'])} no Ring 3, {fmt(fb['estouroFilas'])} chegadas a fila cheia.")
        L.append("- O eleitor lê o painel na soleira (10 s) e segue a fita da cor da sua porta até a parede da sua mesa; a placa alta numerada confirma.")
        L.append("- Orientadores volantes redirecionam quem se perdeu (custo esperado: 1 a 3 min no P90) e são a única resposta a uma fila de mesa cheia.\n")

    L.append("## 6. Salão e filas de mesa\n")
    L.append(f"Traçado vigente das unifilas: **{tb_cen['nome']}** — {tb_cen['postes']} postes ({tb_cen['postes_reserva']} com reserva), {vg(tb_cen['metros'], 0)} m de fita. {tb_cen['desc']}\n")
    L.append(f"- Comprimento de fila por classe: {comp['alta']:.0f} m nas três críticas (MRV {', '.join(str(m['mrv']) for m in altas)}), {comp['media']:.0f} m nas de média, {comp['baixa']:.0f} m nas de baixa. A linha do meio de cada par separa as duas filas; a fila só começa depois dos mesários.")
    curtos = sorted((f for f in tb["folego"] if f["minutos"] is not None and f["minutos"] < 20), key=lambda f: f["minutos"])
    if curtos:
        L.append(f"- **Mesas que lotam rápido no pico** (menos de 20 min a 60 s por voto): MRV {', '.join(str(f['n']) + ' (' + str(f['minutos']) + ' min)' for f in curtos)}. O orientador de piso fica com o olho nelas; fila além da fita → chamar o checkpoint para reter, não empurrar a fila pelo corredor.")
    nunca = [str(f["n"]) for f in tb["folego"] if f["minutos"] is None]
    if nunca:
        L.append(f"- Mesas que não lotam em hipótese nenhuma: MRV {', '.join(nunca)}. Não precisam de orientador dedicado.")
    if P["D4"].get("mesas_sem_guia"):
        L.append(f"- {P['D4']['mesas_sem_guia']} mesas sem fita: a ordem é do orientador. Fila em linha única rente à parede, placa alta como referência.")
    if P["D6"].get("placa_alta_mesa"):
        L.append("- Toda mesa tem placa alta com o número (MRV); o orientador aponta a placa, não a mesa.")
    else:
        L.append("- Sinalização interna vigente: faixas suspensas por bloco e totem por mesa (P6). Sem placa alta, o orientador precisa nomear a mesa em voz alta: \"MRV vinte e dois, ali, parede norte\".")
    L.append("- Quem chega à mesa errada não volta ao checkpoint: o orientador o leva à mesa certa pelo corredor mais curto.")
    L.append("- **Mesa receptora (identificação pelo caderno): a definir.** Com "
             f"{fmt(altas[0]['esperado'])} comparecentes esperados na mesa mais carregada (MRV {altas[0]['mrv']}), fechar às 17h exige no máximo "
             f"{JANELA_MIN * 60 // altas[0]['esperado']} s por eleitor; nas outras duas críticas, {JANELA_MIN * 60 // altas[-1]['esperado']} s. "
             "Como o caderno chega, quem identifica e se a identificação corre em paralelo com o voto é a pendência 5 do PENDENCIAS; este bloco é preenchido quando ela fechar.\n")

    L.append(f"## 7. Saídas {' e '.join(dec['saidas'])}\n")
    L.append("- Quem votou sai pela porta de saída do flanco mais próximo. Ninguém volta pelo salão para conversar, fotografar ou esperar alguém.")
    L.append("- Do lado de fora, seguir a placa \"SAÍDA / WAY OUT → Merrion Road\"; não reentrar no Ring 3 nem cruzar a fila de quem entra.")
    if P["D3"].get("corredor_em_L"):
        L.append("- S8 despeja no apron leste, onde a corrente de chegada desce: o marshal do cruzamento separa os dois fluxos.")
    L.append("")

    L.append("## 8. Acessibilidade e prioridade\n")
    L.append(f"- Cerca de {fmt(PRIORITARIOS['idosos'])} eleitores com 60 anos ou mais e {fmt(PRIORITARIOS['pcd'])} com deficiência declarada: ~{fmt(PRIORITARIOS['idosos'] + PRIORITARIOS['pcd'])} no dia, ~{fmt((PRIORITARIOS['idosos'] + PRIORITARIOS['pcd']) / 9)} por hora no pico.")
    L.append("- Ninguém com prioridade entra no serpenteado (130 m de percurso). Rota: " + {"apron": "apron pavimentado, do desembarque à porta da sua zona, com o agente de acessibilidade.",
                                                                                          "porta": f"porta dedicada {P['D1b'].get('porta_dedicada')}.",
                                                                                          "fila": "cabeça da fila da sua zona, pelo marshal."}.get(rota, "a definir (D1b)."))
    L.append("- Dentro do salão, o prioritário vai direto à mesa; o orientador de piso avisa o mesário.\n")

    L.append("## 9. Seguranças e polícia\n")
    L.append(f"- {SEGURANCAS} seguranças contratados, em postos fixos de controle de acesso e resposta a incidente. Proposta de distribuição: 2 no portão e no acesso, 1 na fachada das entradas, 1 nas saídas. **Não organizam fila**: isso é dos voluntários.")
    L.append("- Polícia do lado de fora do recinto (formato a confirmar com a Garda e registrar na nota verbal).")
    L.append("- Incidente (mal súbito, conflito, objeto suspeito): o voluntário chama o segurança mais próximo e a coordenação; não intervém.\n")

    L.append("## 10. Equipe por posto\n")
    L.append("| Posto | Pessoas | Tarefa | Reporta a |\n|---|---|---|---|")
    for l in eq:
        L.append(f"| {l['posto']} | {l['n'] if l['n'] else '—'} | {l['tarefa']} | {l['reporta']} |")
    L.append(f"| **Total de voluntários** | **{total_vol}** | mais {SEGURANCAS} seguranças | |")
    L.append("")
    L.append("**Gatilhos de escalada** (quem vê, avisa a coordenação; ninguém age sozinho):")
    for e in ent:
        L.append(f"- Zona {e['id']} com mais de {fmt(cap_zona[e['id']])} pessoas, ou porta {e['porta']} recebendo mais de {vg(pico_por_min(e['esperado']))} por minuto por mais de 10 min.")
    L.append(f"- Fila de mesa além da fita ({comp['alta']:.0f} / {comp['media']:.0f} / {comp['baixa']:.0f} m).")
    L.append(f"- Última mesa prevista para fechar depois das {melhor['fecha90']} (dia ruim do simulador).")
    L.append("- Qualquer cruzamento entre quem sai e quem entra fora do apron leste.\n")

    L.append("## 11. O que muda neste documento se uma decisão mudar\n")
    L.append("Gerado do registro de decisões: para cada decisão em aberto, o que a alternativa faria com a equipe e com a sinalização interna.\n")
    for d in reg["decisoes"]:
        vig = V[d["id"]]
        L.append(f"**{d['id']} — {d['titulo']}** (hoje: {vig['rotulo'] if vig else 'sem opção vigente'})")
        for o in d["opcoes"]:
            if vig and o["id"] == vig["id"]:
                continue
            ef = [o["efeitos"].get(k) for k in ("D7", "D6") if o["efeitos"].get(k)]
            if ef:
                L.append(f"- se *{o['rotulo']}*: " + " ".join(ef))
            else:
                L.append(f"- se *{o['rotulo']}*: sem efeito direto na equipe; ver `docs/decisoes_em_aberto.md`.")
        L.append("")
    return "\n".join(L) + "\n"


# --------------------------------------------------------------------- html --
def _inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", t)
    return t


def md_para_html(md):
    out, tab, lista, num = [], [], [], []

    def flush_tab():
        if not tab:
            return
        cab = [c.strip() for c in tab[0].strip("|").split("|")]
        corpo = [ln for ln in tab[2:]]
        out.append('<div class="tw"><table><thead><tr>' + "".join(f"<th>{_inline(c)}</th>" for c in cab) + "</tr></thead><tbody>")
        for ln in corpo:
            cels = [c.strip() for c in ln.strip("|").split("|")]
            out.append("<tr>" + "".join(f"<td>{_inline(c)}</td>" for c in cels) + "</tr>")
        out.append("</tbody></table></div>")
        tab.clear()

    def flush_lista():
        if lista:
            out.append("<ul>" + "".join(f"<li>{_inline(i)}</li>" for i in lista) + "</ul>")
            lista.clear()
        if num:
            out.append("<ol>" + "".join(f"<li>{_inline(i)}</li>" for i in num) + "</ol>")
            num.clear()

    for ln in md.split("\n"):
        if ln.startswith("|"):
            flush_lista(); tab.append(ln); continue
        flush_tab()
        if ln.startswith("- "):
            lista.append(ln[2:]); continue
        if ln.startswith("  - "):
            lista.append("↳ " + ln[4:]); continue
        if re.match(r"^\d+\. ", ln):
            num.append(ln.split(". ", 1)[1]); continue
        flush_lista()
        if ln.startswith("# "):
            out.append(f"<h1>{_inline(ln[2:])}</h1>")
        elif ln.startswith("### "):
            out.append(f"<h3>{_inline(ln[4:])}</h3>")
        elif ln.startswith("## "):
            out.append(f"<h2>{_inline(ln[3:])}</h2>")
        elif ln.startswith("> "):
            out.append(f'<p class="lead">{_inline(ln[2:])}</p>')
        elif ln.strip():
            out.append(f"<p>{_inline(ln)}</p>")
    flush_tab(); flush_lista()
    return "\n".join(out)


def html_pagina(md, titulo="Instruções de fluxo · Posto de Dublin 2026"):
    return f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(titulo)}</title>
<style>
:root{{--bg:#fbfaf7;--fg:#1f2c3c;--mut:#5c6c80;--line:#dfe5ec;--card:#fff;--acc:#1f6fb2;--warn:#b26a12}}
@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{--bg:#151a21;--fg:#e8ecf1;--mut:#a3aebb;--line:#2c3542;--card:#1c232c;--acc:#7fb3e6;--warn:#dda257}}}}
:root[data-theme="dark"]{{--bg:#151a21;--fg:#e8ecf1;--mut:#a3aebb;--line:#2c3542;--card:#1c232c;--acc:#7fb3e6;--warn:#dda257}}
body{{background:var(--bg);color:var(--fg);font:15.5px/1.55 ui-sans-serif,system-ui,'Segoe UI',Helvetica,Arial,sans-serif;margin:0;padding:24px 16px 56px}}
main{{max-width:880px;margin:0 auto}}h1{{font-size:1.6rem;line-height:1.2;margin:.2em 0 .4em;text-wrap:balance}}
h2{{font-size:1.15rem;margin:1.8em 0 .5em;color:var(--acc);border-bottom:1px solid var(--line);padding-bottom:.25em}}h3{{font-size:1rem;margin:1.3em 0 .3em}}ol{{padding-left:1.4em;max-width:80ch}}
p{{margin:.5em 0;max-width:80ch}}.lead{{color:var(--mut);max-width:80ch;border-left:3px solid var(--warn);padding-left:12px}}
ul{{padding-left:1.2em;max-width:80ch}}li{{margin:.3em 0}}
.tw{{overflow-x:auto;margin:.6em 0;border:1px solid var(--line);background:var(--card)}}table{{border-collapse:collapse;font-size:13.5px;width:100%;font-variant-numeric:tabular-nums}}
th,td{{border-bottom:1px solid var(--line);padding:6px 9px;text-align:left;vertical-align:top}}th{{color:var(--mut);font-weight:600;white-space:nowrap}}
code{{font-size:.92em;background:var(--line);padding:0 4px;border-radius:3px}}
@media print{{body{{padding:0}}h2{{break-after:avoid}}.tw{{break-inside:avoid}}}}
</style></head><body><main>
{md_para_html(md)}
</main></body></html>
"""


def main():
    md = documento()
    os.makedirs(os.path.dirname(ARQUIVO_MD), exist_ok=True)
    with open(ARQUIVO_MD, "w", encoding="utf-8") as f:
        f.write(md)
    with open(ARQUIVO_HTML, "w", encoding="utf-8") as f:
        f.write(html_pagina(md))
    # o registro de decisoes tambem ganha uma pagina, para o dashboard copiar
    with open(ARQUIVO_DEC_HTML, "w", encoding="utf-8") as f:
        f.write(html_pagina(DA.markdown(DA.montar()), "Decisões em aberto · Posto de Dublin 2026"))
    print("gravado", os.path.relpath(ARQUIVO_MD, RAIZ), "e", os.path.relpath(ARQUIVO_HTML, RAIZ),
          f"({len(md) // 1024} KB)")


if __name__ == "__main__":
    main()
