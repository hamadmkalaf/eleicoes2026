"""Compara duas organizacoes de entrada para o RDS Hall 2.

  HUB    -- ideia atual: cada porta (A, B) leva por corredor a um ponto de
            triagem no centro do salao, onde equipe com banners aponta cada
            eleitor para a sua mesa.
  FITAS  -- sugestao alternativa: sem triagem central; fitas no piso, com
            sinalizacao, levam o eleitor da porta direto a sua mesa.

O script nao modela o tempo de votacao na urna (fora do escopo, como no
restante do projeto): compara apenas a etapa "da porta ate a fila da mesa".

So usa a biblioteca padrao. Le saidas/dados.json e grava:
  saidas/fluxo_entrada_comparacao.json  -- numeros
  saidas/fluxo_entrada_comparacao.md    -- tabelas
  saidas/fluxo_hub.svg, saidas/fluxo_fitas.svg -- plantas esquematicas
  saidas/fluxo_entrada_comparacao.html  -- pagina com tudo

Todos os parametros sao premissas declaradas em PREMISSAS; mude-as e rode
de novo.
"""

import json
import math
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
SAIDAS = BASE / "saidas"

# --------------------------------------------------------------------------
# Premissas (todas ajustaveis)
# --------------------------------------------------------------------------
PREMISSAS = {
    # Comparecimento por residencia (taxas de 2022, ver contexto secao 1).
    "comparecimento_dublin": 0.74,
    "comparecimento_interior": 0.50,
    # Janela de votacao em horas e fator de pico (hora de pico / hora media).
    "janela_horas": 9.0,
    "fator_pico": 1.5,
    # Fracao de eleitores que chega SEM saber a propria secao/mesa.
    "fracao_nao_sabe": 0.25,
    # Tempos de servico da triagem, em segundos.
    "s_sabe": 8.0,        # "qual sua secao?" -> "mesa 12, ali"
    "s_nao_sabe": 45.0,   # consulta por nome em lista/tablet
    # Fitas: no modelo FITAS o eleitor que sabe a secao nao para; o que nao
    # sabe e atendido no balcao de apoio (fora da porta ou logo apos).
    "velocidade_m_s": 1.0,
    # Unifila: pessoas por metro de corredor em fila.
    "pessoas_por_metro": 2.0,
    # Fita adesiva de piso: metros por rolo e preco por rolo (EUR), premissa.
    "metros_por_rolo": 33.0,
    "eur_por_rolo": 12.0,
}

# --------------------------------------------------------------------------
# Geometria do salao (metros). Origem no canto sudoeste; y cresce para o
# norte. Dimensoes do RDS Hall 2: 50,2 m x 44,5 m. Posicoes das mesas e
# portas transcritas aproximadamente do esboco "PLANO COM FLUXOS MELHORADO".
# --------------------------------------------------------------------------
LARGURA, COMPRIMENTO = 50.2, 44.5

PORTAS = {"A": (25.4, 0.0), "B": (34.9, 0.0)}
SAIDA_CENTRAL = (29.7, 0.0)
SAIDAS_LATERAIS = {"W": (11.0, 8.0), "E": (50.2, 8.0)}   # portas 2.8/2.9 e 2.22/2.23
HUBS = {"A": (25.4, 21.2), "B": (34.9, 21.2)}

# 28 posicoes de mesa em 6 zonas. Cada zona tem uma cor de fita.
ZONAS = {
    "LN": {"porta": "A", "cor": "#d62728", "nome": "Oeste-Norte",
           "mesas": [(8.8, 35.8), (8.8, 32.9), (8.8, 29.1), (8.8, 26.9)]},
    "LS": {"porta": "A", "cor": "#ff7f0e", "nome": "Oeste-Sul",
           "mesas": [(8.8, 18.5), (8.8, 15.6), (8.8, 12.8), (8.8, 10.1),
                     (14.2, 5.9), (14.2, 3.0)]},
    "TW": {"porta": "A", "cor": "#9467bd", "nome": "Norte-Oeste",
           "mesas": [(19.1, 40.8), (21.6, 40.8)]},
    "TE": {"porta": "B", "cor": "#2ca02c", "nome": "Norte-Leste",
           "mesas": [(29.8, 40.8), (32.4, 40.8), (35.9, 40.8), (38.4, 40.8)]},
    "RN": {"porta": "B", "cor": "#1f77b4", "nome": "Leste-Norte",
           "mesas": [(41.5, 39.5), (41.5, 36.5), (41.5, 33.5), (41.5, 30.5),
                     (41.5, 27.5), (41.5, 24.5)]},
    "RS": {"porta": "B", "cor": "#17becf", "nome": "Leste-Sul",
           "mesas": [(41.5, 21.0), (41.5, 18.0), (41.5, 15.0), (41.5, 12.0),
                     (41.5, 9.0), (41.5, 6.0)]},
}


# --------------------------------------------------------------------------
# Utilidades
# --------------------------------------------------------------------------
def dist(p, q):
    return math.hypot(p[0] - q[0], p[1] - q[1])


def erlang_c(lam, mu, c):
    """Espera media (min) e prob. de esperar numa fila M/M/c.

    lam: chegadas/min; mu: atendimentos/min por atendente; c: atendentes.
    Retorna (rho, prob_espera, espera_media_min, fila_media). Se rho >= 1 a
    fila nao estabiliza: devolve inf.
    """
    a = lam / mu
    rho = a / c
    if rho >= 1:
        return rho, 1.0, math.inf, math.inf
    soma = sum(a ** k / math.factorial(k) for k in range(c))
    termo = a ** c / (math.factorial(c) * (1 - rho))
    p_esp = termo / (soma + termo)
    espera = p_esp / (c * mu - lam)
    fila = espera * lam
    return rho, p_esp, espera, fila


def cruzam(p1, p2, q1, q2):
    """True se os segmentos p1-p2 e q1-q2 se cruzam (ignora extremos comuns)."""
    def orient(a, b, c):
        v = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
        return 0 if abs(v) < 1e-9 else (1 if v > 0 else -1)
    if p1 == q1 or p1 == q2 or p2 == q1 or p2 == q2:
        return False
    o1, o2 = orient(p1, p2, q1), orient(p1, p2, q2)
    o3, o4 = orient(q1, q2, p1), orient(q1, q2, p2)
    return o1 != o2 and o3 != o4 and 0 not in (o1, o2, o3, o4)


def conta_cruzamentos(caminhos_a, caminhos_b):
    """Pares (segmento de A, segmento de B) que se cruzam."""
    n = 0
    for ca in caminhos_a:
        for cb in caminhos_b:
            for i in range(len(ca) - 1):
                for j in range(len(cb) - 1):
                    if cruzam(ca[i], ca[i + 1], cb[j], cb[j + 1]):
                        n += 1
    return n


# --------------------------------------------------------------------------
# Dados: comparecimento esperado por urna e alocacao as posicoes
# --------------------------------------------------------------------------
def carrega_urnas(P):
    d = json.loads((SAIDAS / "dados.json").read_text(encoding="utf-8"))
    por_urna = {r["Urna"]: r for r in d["residencia_urna"]}
    urnas = []
    for u in d["urnas"]:
        r = por_urna[u["Urna"]]
        dub = r["DUBLIN"]
        inte = r["TOTAL"] - dub
        esperado = dub * P["comparecimento_dublin"] + inte * P["comparecimento_interior"]
        urnas.append({
            "urna": u["Urna"], "aptos": u["Total_combinado"],
            "aptos_dublin": dub, "aptos_interior": inte,
            "esperado": esperado,
        })
    urnas.sort(key=lambda x: -x["esperado"])
    return d, urnas


def aloca_posicoes(urnas):
    """Distribui as urnas nas 28 posicoes equilibrando o fluxo entre A e B.

    Percorre da mais cheia para a mais vazia e manda cada uma ao lado (A ou
    B) com menor comparecimento acumulado, enquanto houver vaga. Dentro do
    lado, ocupa as zonas em ordem (mais proximas da porta recebem as mais
    cheias -- caminho curto para quem mais pesa).
    """
    ordem = {"A": ["LS", "LN", "TW"], "B": ["RS", "RN", "TE"]}
    vagas = {lado: [(z, i) for z in ordem[lado] for i in range(len(ZONAS[z]["mesas"]))]
             for lado in ordem}
    acum = {"A": 0.0, "B": 0.0}
    for u in urnas:
        lado = min(("A", "B"), key=lambda l: (acum[l] if vagas[l] else math.inf))
        z, i = vagas[lado].pop(0)
        u["zona"], u["pos"] = z, ZONAS[z]["mesas"][i]
        u["porta"] = ZONAS[z]["porta"]
        acum[lado] += u["esperado"]
    return acum


# --------------------------------------------------------------------------
# Modelos
# --------------------------------------------------------------------------
def taxa_pico(total, P):
    media_min = total / (P["janela_horas"] * 60)
    return media_min * P["fator_pico"]


def modelo_hub(urnas, P, lam_porta):
    """Triagem central obrigatoria para 100% dos eleitores."""
    s_med = (1 - P["fracao_nao_sabe"]) * P["s_sabe"] + P["fracao_nao_sabe"] * P["s_nao_sabe"]
    mu = 60.0 / s_med
    filas = {}
    for c in range(1, 16):
        rho, p, w, l = erlang_c(lam_porta, mu, c)
        filas[c] = {"rho": rho, "p_espera": p, "espera_min": w, "fila": l}
    c_min = next(c for c in filas if filas[c]["rho"] < 1)
    c_conf = next(c for c in filas if filas[c]["rho"] < 0.8)

    tot = sum(u["esperado"] for u in urnas)
    passos = 0.0
    for u in urnas:
        hub = HUBS[u["porta"]]
        passos += u["esperado"] * (dist(PORTAS[u["porta"]], hub) + dist(hub, u["pos"]))
    cam_medio = passos / tot

    corredor = dist(PORTAS["A"], HUBS["A"])
    buffer_pessoas = corredor * P["pessoas_por_metro"]

    entrada = [[PORTAS[u["porta"]], HUBS[u["porta"]], u["pos"]] for u in urnas]
    saida_c = [[u["pos"], SAIDA_CENTRAL] for u in urnas]
    saida_l = [[u["pos"], SAIDAS_LATERAIS["W" if u["porta"] == "A" else "E"]] for u in urnas]
    # so o trecho hub->mesa dispersa; o corredor e canalizado por unifila
    dispersao = [[HUBS[u["porta"]], u["pos"]] for u in urnas]

    return {
        "servico_medio_s": s_med,
        "atendimentos_min_por_pessoa": mu,
        "fila_por_atendentes": filas,
        "atendentes_min_por_hub": c_min,
        "atendentes_conforto_por_hub": c_conf,
        "caminho_medio_m": cam_medio,
        "corredor_m": corredor,
        "buffer_corredor_pessoas": buffer_pessoas,
        "cruz_dispersao_x_dispersao": conta_cruzamentos(dispersao, dispersao) // 2,
        "cruz_entrada_x_saida_central": conta_cruzamentos(entrada, saida_c),
        "cruz_entrada_x_saida_lateral": conta_cruzamentos(entrada, saida_l),
    }


def modelo_fitas(urnas, P, lam_porta):
    """Sem triagem central: so quem nao sabe a secao para num balcao."""
    lam_apoio = lam_porta * P["fracao_nao_sabe"]
    mu = 60.0 / P["s_nao_sabe"]
    filas = {}
    for c in range(1, 10):
        rho, p, w, l = erlang_c(lam_apoio, mu, c)
        filas[c] = {"rho": rho, "p_espera": p, "espera_min": w, "fila": l}
    c_min = next(c for c in filas if filas[c]["rho"] < 1)
    c_conf = next(c for c in filas if filas[c]["rho"] < 0.8)

    tot = sum(u["esperado"] for u in urnas)
    cam_medio = sum(u["esperado"] * dist(PORTAS[u["porta"]], u["pos"]) for u in urnas) / tot

    # Fitas por zona: porta -> primeira mesa da zona, depois ao longo da zona.
    metros_zona = 0.0
    linhas_zona = []
    for z, zona in ZONAS.items():
        porta = PORTAS[zona["porta"]]
        ms = zona["mesas"]
        # o tronco chega a mesa mais proxima da porta e segue pelas demais
        ms_ord = sorted(ms, key=lambda m: dist(porta, m))
        linha = [porta] + ms_ord
        linhas_zona.append(linha)
        metros_zona += sum(dist(linha[i], linha[i + 1]) for i in range(len(linha) - 1))
    # Fitas individuais (uma por mesa): o que a sugestao literal implica.
    metros_mesa = sum(dist(PORTAS[u["porta"]], u["pos"]) for u in urnas)
    larg_feixe_mesa = 28 * 0.05 + 27 * 0.05      # 5 cm de fita + 5 cm de vao
    larg_feixe_zona = 3 * 0.05 + 2 * 0.05         # 3 fitas por porta

    entrada = [[PORTAS[u["porta"]], u["pos"]] for u in urnas]
    saida_c = [[u["pos"], SAIDA_CENTRAL] for u in urnas]
    saida_l = [[u["pos"], SAIDAS_LATERAIS["W" if u["porta"] == "A" else "E"]] for u in urnas]

    rolos_zona = math.ceil(metros_zona / P["metros_por_rolo"])
    rolos_mesa = math.ceil(metros_mesa / P["metros_por_rolo"])
    return {
        "chegadas_apoio_min_por_porta": lam_apoio,
        "fila_por_atendentes": filas,
        "atendentes_min_por_porta": c_min,
        "atendentes_conforto_por_porta": c_conf,
        "caminho_medio_m": cam_medio,
        "fitas_por_zona_m": metros_zona,
        "fitas_por_zona_rolos": rolos_zona,
        "fitas_por_zona_eur": rolos_zona * P["eur_por_rolo"],
        "fitas_por_mesa_m": metros_mesa,
        "fitas_por_mesa_rolos": rolos_mesa,
        "fitas_por_mesa_eur": rolos_mesa * P["eur_por_rolo"],
        "largura_feixe_na_porta_por_mesa_m": larg_feixe_mesa,
        "largura_feixe_na_porta_por_zona_m": larg_feixe_zona,
        "cruz_entrada_x_entrada": conta_cruzamentos(entrada, entrada) // 2,
        "cruz_entrada_x_saida_central": conta_cruzamentos(entrada, saida_c),
        "cruz_entrada_x_saida_lateral": conta_cruzamentos(entrada, saida_l),
        "linhas_zona": linhas_zona,
    }


def sensibilidade(urnas, P, lam_porta):
    """Atendentes minimos por porta/hub para varias fracoes de 'nao sabe'."""
    linhas = []
    for f in (0.10, 0.25, 0.40, 0.60):
        Q = dict(P, fracao_nao_sabe=f)
        h = modelo_hub(urnas, Q, lam_porta)
        t = modelo_fitas(urnas, Q, lam_porta)
        linhas.append({
            "fracao_nao_sabe": f,
            "hub_min": h["atendentes_min_por_hub"],
            "hub_conforto": h["atendentes_conforto_por_hub"],
            "fitas_min": t["atendentes_min_por_porta"],
            "fitas_conforto": t["atendentes_conforto_por_porta"],
        })
    return linhas


# --------------------------------------------------------------------------
# SVG
# --------------------------------------------------------------------------
def svg_planta(urnas, modo, extra, titulo):
    esc = 12.0
    W, H = LARGURA * esc + 40, COMPRIMENTO * esc + 70
    def X(x): return 20 + x * esc
    def Y(y): return 20 + (COMPRIMENTO - y) * esc
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.0f} {H:.0f}" '
           f'font-family="system-ui, sans-serif" font-size="11">']
    # contorno do salao: recuo no canto sudoeste (x<11, y<8 fica fora) e
    # bloco de sanitarios/foyer encostado por fora da parede oeste (x<5.7)
    poly = [(5.7, COMPRIMENTO), (LARGURA, COMPRIMENTO), (LARGURA, 0), (11, 0),
            (11, 8), (5.7, 8)]
    pts = " ".join(f"{X(x):.1f},{Y(y):.1f}" for x, y in poly)
    out.append(f'<polygon points="{pts}" fill="#f8f8f6" stroke="#333" stroke-width="2"/>')
    out.append(f'<rect x="{X(0)}" y="{Y(COMPRIMENTO)}" width="{5.7*esc}" height="{17.5*esc}" '
               f'fill="#e6e6e2" stroke="#333"/>')
    out.append(f'<text x="{X(2.85)}" y="{Y(36)}" text-anchor="middle" fill="#555" font-size="9">WC</text>')
    out.append(f'<text x="{X(LARGURA/2)}" y="{Y(COMPRIMENTO)-6}" text-anchor="middle" '
               f'font-size="14" font-weight="600">{titulo}</text>')

    if modo == "hub":
        for p, porta in PORTAS.items():
            hub = HUBS[p]
            out.append(f'<line x1="{X(porta[0])}" y1="{Y(porta[1])}" x2="{X(hub[0])}" '
                       f'y2="{Y(hub[1])}" stroke="#444" stroke-width="10" opacity="0.35"/>')
            out.append(f'<circle cx="{X(hub[0])}" cy="{Y(hub[1])}" r="12" fill="#444"/>')
            out.append(f'<text x="{X(hub[0])}" y="{Y(hub[1])+4}" text-anchor="middle" '
                       f'fill="#fff" font-weight="700">{p}</text>')
            for u in urnas:
                if u["porta"] != p:
                    continue
                cor = ZONAS[u["zona"]]["cor"]
                out.append(f'<line x1="{X(hub[0])}" y1="{Y(hub[1])}" x2="{X(u["pos"][0])}" '
                           f'y2="{Y(u["pos"][1])}" stroke="{cor}" stroke-width="1.2" '
                           f'stroke-dasharray="4 3" opacity="0.8"/>')
    else:
        for linha, (z, zona) in zip(extra["linhas_zona"], ZONAS.items()):
            pts = " ".join(f"{X(x):.1f},{Y(y):.1f}" for x, y in linha)
            out.append(f'<polyline points="{pts}" fill="none" stroke="{zona["cor"]}" '
                       f'stroke-width="4" opacity="0.85"/>')
        for p, porta in PORTAS.items():
            out.append(f'<rect x="{X(porta[0])-26}" y="{Y(0)+18}" width="52" height="22" '
                       f'fill="#fff" stroke="#444"/>')
            out.append(f'<text x="{X(porta[0])}" y="{Y(0)+33}" text-anchor="middle" '
                       f'font-size="9">apoio {p}</text>')

    for u in urnas:
        x, y = u["pos"]
        cor = ZONAS[u["zona"]]["cor"]
        out.append(f'<rect x="{X(x)-9}" y="{Y(y)-6}" width="18" height="12" fill="{cor}" '
                   f'stroke="#222" rx="2"/>')
        out.append(f'<text x="{X(x)}" y="{Y(y)+3.5}" text-anchor="middle" fill="#fff" '
                   f'font-size="8" font-weight="700">{u["mesa_n"]}</text>')

    for p, porta in PORTAS.items():
        out.append(f'<rect x="{X(porta[0])-14}" y="{Y(0)-4}" width="28" height="8" fill="#222"/>')
        out.append(f'<text x="{X(porta[0])}" y="{Y(0)+14}" text-anchor="middle" '
                   f'font-weight="700">{p}</text>')
    sx, sy = SAIDA_CENTRAL
    out.append(f'<rect x="{X(sx)-10}" y="{Y(0)-4}" width="20" height="8" fill="#0a7d2c"/>')
    out.append(f'<text x="{X(sx)}" y="{Y(0)+14}" text-anchor="middle" fill="#0a7d2c" '
               f'font-size="9">SAÍDA</text>')
    for k, (sx, sy) in SAIDAS_LATERAIS.items():
        out.append(f'<rect x="{X(sx)-4}" y="{Y(sy)-10}" width="8" height="20" fill="#0a7d2c" opacity="0.5"/>')
    out.append("</svg>")
    return "\n".join(out)


# --------------------------------------------------------------------------
# Saidas
# --------------------------------------------------------------------------
def fmt(n, d=0):
    if n is None or (isinstance(n, float) and math.isinf(n)):
        return "∞"
    s = f"{n:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return s


def tabela_filas(filas, rotulo):
    linhas = [f"| {rotulo} | ocupação | prob. esperar | espera média | fila média |",
              "|---|---|---|---|---|"]
    for c, f in filas.items():
        linhas.append(f"| {c} | {fmt(f['rho']*100)}% | {fmt(f['p_espera']*100)}% | "
                      f"{fmt(f['espera_min'], 1)} min | {fmt(f['fila'], 1)} |")
    return "\n".join(linhas)


def markdown(res):
    P, h, t, s = res["premissas"], res["hub"], res["fitas"], res["sensibilidade"]
    md = []
    md.append("# Entrada: triagem central (HUB) × fitas no piso (FITAS)\n")
    md.append(f"Comparecimento esperado: **{fmt(res['comparecimento_esperado'])}** eleitores "
              f"({fmt(P['comparecimento_dublin']*100)}% Dublin, "
              f"{fmt(P['comparecimento_interior']*100)}% interior). "
              f"Hora de pico: **{fmt(res['chegadas_pico_min'], 1)}/min** no total, "
              f"**{fmt(res['chegadas_pico_min_por_porta'], 1)}/min por porta** "
              f"(fator de pico {P['fator_pico']}). Fração que chega sem saber a seção: "
              f"**{fmt(P['fracao_nao_sabe']*100)}%** (premissa).\n")
    md.append(f"Divisão de fluxo entre portas: A = {fmt(res['fluxo_porta']['A'])}, "
              f"B = {fmt(res['fluxo_porta']['B'])} eleitores esperados.\n")
    md.append("## Resumo\n")
    md.append("| Indicador | HUB | FITAS |\n|---|---|---|")
    md.append(f"| Quem passa pela triagem | 100% | só quem não sabe a seção ({fmt(P['fracao_nao_sabe']*100)}%) |")
    md.append(f"| Chegadas na triagem (pico, por porta) | {fmt(res['chegadas_pico_min_por_porta'],1)}/min | {fmt(t['chegadas_apoio_min_por_porta'],1)}/min |")
    md.append(f"| Atendentes mínimos por porta/hub (fila estável) | {h['atendentes_min_por_hub']} | {t['atendentes_min_por_porta']} |")
    md.append(f"| Atendentes para conforto (ocupação < 80%) | {h['atendentes_conforto_por_hub']} | {t['atendentes_conforto_por_porta']} |")
    md.append(f"| Total de triadores nas duas portas (conforto) | {2*h['atendentes_conforto_por_hub']} | {2*t['atendentes_conforto_por_porta']} |")
    md.append(f"| Caminho médio porta → mesa | {fmt(h['caminho_medio_m'],1)} m | {fmt(t['caminho_medio_m'],1)} m |")
    md.append(f"| Buffer de fila dentro do salão | corredor {fmt(h['corredor_m'],1)} m ≈ {fmt(h['buffer_corredor_pessoas'])} pessoas por porta | nenhum: a fila fica fora da porta |")
    md.append(f"| Cruzamentos entre trajetos de entrada | {h['cruz_dispersao_x_dispersao']} (dispersão a partir dos hubs) | {t['cruz_entrada_x_entrada']} (leques A e B não se cruzam) |")
    md.append(f"| Cruzamentos entrada × saída, saída central | {h['cruz_entrada_x_saida_central']} | {t['cruz_entrada_x_saida_central']} |")
    md.append(f"| Cruzamentos entrada × saída, saídas laterais | {h['cruz_entrada_x_saida_lateral']} | {t['cruz_entrada_x_saida_lateral']} |")
    md.append(f"| Fita no piso (6 troncos por zona) | — | {fmt(t['fitas_por_zona_m'])} m, {t['fitas_por_zona_rolos']} rolos ≈ EUR {fmt(t['fitas_por_zona_eur'])} |")
    md.append(f"| Fita no piso (28 linhas, uma por mesa) | — | {fmt(t['fitas_por_mesa_m'])} m, {t['fitas_por_mesa_rolos']} rolos ≈ EUR {fmt(t['fitas_por_mesa_eur'])} |")
    md.append(f"| Largura do feixe de fitas na porta | — | {fmt(t['largura_feixe_na_porta_por_zona_m'],2)} m (zonas) vs {fmt(t['largura_feixe_na_porta_por_mesa_m'],2)} m (uma por mesa) |")
    md.append("")
    md.append(f"## HUB: fila na triagem central (serviço médio {fmt(h['servico_medio_s'],1)} s)\n")
    md.append(tabela_filas(h["fila_por_atendentes"], "atendentes por hub"))
    md.append("")
    md.append(f"## FITAS: fila no balcão de apoio (serviço {fmt(P['s_nao_sabe'])} s, só quem não sabe)\n")
    md.append(tabela_filas(t["fila_por_atendentes"], "atendentes por porta"))
    md.append("")
    md.append("## Sensibilidade: quantos atendentes por porta/hub conforme a fração que não sabe a seção\n")
    md.append("| não sabe a seção | HUB mínimo | HUB conforto | FITAS mínimo | FITAS conforto |\n|---|---|---|---|---|")
    for l in s:
        md.append(f"| {fmt(l['fracao_nao_sabe']*100)}% | {l['hub_min']} | {l['hub_conforto']} | {l['fitas_min']} | {l['fitas_conforto']} |")
    md.append("")
    md.append("## Alocação das urnas às posições (equilibrando A e B)\n")
    md.append("| Mesa | Urna (seção principal) | Zona | Porta | Aptos | Esperados |\n|---|---|---|---|---|---|")
    for u in sorted(res["urnas"], key=lambda u: u["mesa_n"]):
        md.append(f"| {u['mesa_n']} | {u['urna']:04d} | {ZONAS[u['zona']]['nome']} | {u['porta']} | "
                  f"{fmt(u['aptos'])} | {fmt(u['esperado'])} |")
    return "\n".join(md) + "\n"


def pagina_html(res, svg_hub, svg_fitas, md_body):
    # conversao minima de markdown (titulos, tabelas, paragrafos) para HTML
    import html as H
    linhas, out, tabela = md_body.splitlines(), [], []
    def flush():
        nonlocal tabela
        if tabela:
            out.append("<div class='tw'><table>")
            for i, r in enumerate(tabela):
                if set(r.replace("|", "").strip()) <= set("-: "):
                    continue
                cels = [c.strip() for c in r.strip().strip("|").split("|")]
                tag = "th" if i == 0 else "td"
                out.append("<tr>" + "".join(f"<{tag}>{inline(c)}</{tag}>" for c in cels) + "</tr>")
            out.append("</table></div>")
            tabela = []
    def inline(s):
        s = H.escape(s)
        while "**" in s:
            s = s.replace("**", "<b>", 1).replace("**", "</b>", 1)
        return s
    for l in linhas:
        if l.startswith("|"):
            tabela.append(l); continue
        flush()
        if l.startswith("# "):
            out.append(f"<h1>{inline(l[2:])}</h1>")
        elif l.startswith("## "):
            out.append(f"<h2>{inline(l[3:])}</h2>")
        elif l.strip():
            out.append(f"<p>{inline(l)}</p>")
    flush()
    corpo = "\n".join(out)
    return f"""<title>Entrada RDS: hub × fitas</title>
<style>
:root{{--bg:#fbfaf7;--fg:#1d1d1b;--mut:#66655f;--line:#dcdad3;--card:#fff;--acc:#1f3864}}
@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{--bg:#16171a;--fg:#ececea;--mut:#a5a49e;--line:#33353a;--card:#1f2024;--acc:#9db4e3}}}}
:root[data-theme="dark"]{{--bg:#16171a;--fg:#ececea;--mut:#a5a49e;--line:#33353a;--card:#1f2024;--acc:#9db4e3}}
body{{background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,sans-serif;padding:24px 16px 48px;max-width:1100px;margin:0 auto}}
h1{{font-size:1.5rem;line-height:1.2;margin:.2em 0 .6em}}h2{{font-size:1.1rem;margin:1.6em 0 .4em;color:var(--acc)}}
p{{margin:.4em 0}}.tw{{overflow-x:auto;margin:.6em 0}}table{{border-collapse:collapse;font-size:13.5px;min-width:520px}}
th,td{{border-bottom:1px solid var(--line);padding:5px 10px;text-align:left;vertical-align:top}}th{{color:var(--mut);font-weight:600}}
.plantas{{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:16px;margin:12px 0 24px}}
.plantas figure{{margin:0;background:var(--card);border:1px solid var(--line);border-radius:8px;padding:8px}}
.plantas svg{{width:100%;height:auto;max-width:100%}}figcaption{{color:var(--mut);font-size:13px;padding:6px 4px 0}}
.leg{{display:flex;flex-wrap:wrap;gap:8px 14px;font-size:13px;color:var(--mut);margin:0 0 8px}}.leg i{{display:inline-block;width:12px;height:12px;border-radius:2px;vertical-align:-1px;margin-right:4px}}
</style>
<h1>Entrada no RDS Hall 2: triagem central × fitas no piso</h1>
<p>Modelo da etapa "da porta até a fila da mesa" para as 28 urnas do 1º turno de 04/10/2026. Não inclui o tempo de votação. Plantas esquemáticas na escala real do salão (50,2 × 44,5 m); posições transcritas do esboço atual.</p>
<div class="leg">{"".join(f"<span><i style='background:{z['cor']}'></i>{z['nome']} ({len(z['mesas'])} mesas, porta {z['porta']})</span>" for z in ZONAS.values())}</div>
<div class="plantas">
<figure>{svg_hub}<figcaption>HUB: corredores de unifila levam ao ponto de triagem; de lá, a equipe aponta (tracejado) cada eleitor à sua mesa.</figcaption></figure>
<figure>{svg_fitas}<figcaption>FITAS: seis troncos de fita colorida, três por porta, levam da porta à zona; dentro da zona, o eleitor procura o número da mesa. Balcão de apoio fora de cada porta só para quem não sabe a seção.</figcaption></figure>
</div>
{corpo}
"""


def main():
    P = PREMISSAS
    d, urnas = carrega_urnas(P)
    fluxo_porta = aloca_posicoes(urnas)
    # numera as mesas 1..28 no sentido horario a partir do canto SW
    ordem_z = ["LS", "LN", "TW", "TE", "RN", "RS"]
    seq = []
    for z in ordem_z:
        ms = ZONAS[z]["mesas"]
        us = [u for u in urnas if u["zona"] == z]
        us.sort(key=lambda u: ms.index(u["pos"]) if z not in ("LS",) else -ms.index(u["pos"]))
        seq.extend(us)
    for i, u in enumerate(seq, 1):
        u["mesa_n"] = i

    total = sum(u["esperado"] for u in urnas)
    lam_total = taxa_pico(total, P)
    lam_porta = lam_total / 2

    h = modelo_hub(urnas, P, lam_porta)
    t = modelo_fitas(urnas, P, lam_porta)
    s = sensibilidade(urnas, P, lam_porta)

    res = {
        "premissas": P,
        "aptos": d["total_eleitores"],
        "comparecimento_esperado": total,
        "chegadas_pico_min": lam_total,
        "chegadas_pico_min_por_porta": lam_porta,
        "fluxo_porta": fluxo_porta,
        "hub": {k: v for k, v in h.items()},
        "fitas": {k: v for k, v in t.items() if k != "linhas_zona"},
        "sensibilidade": s,
        "urnas": urnas,
    }
    svg_hub = svg_planta(urnas, "hub", h, "HUB: triagem central")
    svg_fitas = svg_planta(urnas, "fitas", t, "FITAS: fitas no piso por zona")
    md = markdown(res)

    SAIDAS.mkdir(exist_ok=True)
    (SAIDAS / "fluxo_entrada_comparacao.json").write_text(
        json.dumps(res, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    (SAIDAS / "fluxo_entrada_comparacao.md").write_text(md, encoding="utf-8")
    (SAIDAS / "fluxo_hub.svg").write_text(svg_hub, encoding="utf-8")
    (SAIDAS / "fluxo_fitas.svg").write_text(svg_fitas, encoding="utf-8")
    (SAIDAS / "fluxo_entrada_comparacao.html").write_text(
        pagina_html(res, svg_hub, svg_fitas, md), encoding="utf-8")
    print(md)


if __name__ == "__main__":
    main()
