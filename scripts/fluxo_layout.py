"""
Desenho de fluxo do posto de votacao de Dublin — RDS Ballsbridge, Hall 2.

Le as 28 urnas apuradas em saidas/dados.json, estima comparecimento, simula a
fila de cada urna, aloca cada uma a uma posicao fisica no perimetro do Hall 2 e
grava saidas/fluxo_dados.json + saidas/planta_fluxo.svg.

A geometria do Hall 2 foi medida diretamente do PDF oficial do RDS
(RDS_Hall_2_Floorplan_(1).pdf, pagina 2). A escala de 8,69 pt/m foi aferida
contra a ficha tecnica do salao no mesmo PDF: 50,2 m x 44,5 m, 2.238 m2.
Origem (0,0) = canto sudoeste util; x cresce para leste, y para norte.
"""
import json, math, os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------------------------------------------------------------- premissas
TAXA_DUBLIN, TAXA_INTERIOR = 0.74, 0.50   # comparecimento observado em 2022
SEG_POR_VOTO = 55                          # ponto de projeto das baias de fila
ABERTURA, FECHAMENTO = 8, 17
PERFIL = [.08, .13, .15, .14, .12, .11, .10, .09, .08]  # chegadas por hora
AREA_PESSOA = 1.0        # m2 por pessoa em fila serpenteada com balizadores
FOLGA_BAIA = 0.6         # m de balizador entre baias vizinhas
LARG_MIN_BAIA = 2.6      # m — largura minima para modulo mesa+urna e sigilo

# ------------------------------------------------------- geometria do salao
HALL_W, HALL_H = 50.3, 44.4
RECORTE = (0.0, 0.0, 7.8, 7.0)      # canto sudoeste suprimido do salao

PORTAS = {
    "sul":   [("2.7", 17.22, 18.47), ("2.5/2.6", 19.10, 25.03),
              ("2.4", 25.32, 31.25), ("2.2/2.3", 31.54, 37.47),
              ("2.1", 38.09, 39.36)],
    "norte": [("2.13", 7.41, 9.44), ("2.14/2.15", 20.66, 24.22)],
    "leste": [("2.22/2.23", 2.95, 6.01), ("2.20/2.21", 14.80, 17.87),
              ("2.18/2.19", 26.66, 29.72), ("2.16/2.17", 38.51, 41.57)],
    "oeste": [("2.10/2.11 (WC)", 19.36, 22.43), ("acesso Hall 1", 36.80, 38.50)],
}
ENTRADA_A, ENTRADA_B, SAIDA = (22.07, 0.0), (34.51, 0.0), (28.29, 0.0)
ESPINHA = dict(x0=25.32, x1=31.25, y0=0.0, y1=12.0)   # canal de saida balizado

# profundidade maxima de baia de fila por parede (m)
# profundidade maxima da baia de fila, por parede (m). Os tetos garantem que
# as baias de paredes vizinhas nao se sobreponham nos cantos do salao.
PROF_MAX = {"norte": 12.0, "oeste": 8.0, "leste": 8.0, "sul": 4.0}

# Trechos de parede livres de porta corta-fogo, em ordem de percurso: comeca
# junto a Entrada A, contorna o salao por oeste/norte/leste e termina junto a
# Entrada B. (id, parede, coord fixa, de, ate, n_slots, zona)
TRECHOS = [
    ("SO", "sul",    0.0, 16.60,  8.00, 3, "A"),
    ("OB", "oeste",  0.0,  8.00, 18.76, 4, "A"),
    ("OA", "oeste",  0.0, 23.03, 42.90, 6, "A"),
    ("NM", "norte", 44.4, 14.00, 20.06, 2, "A"),
    ("NL", "norte", 44.4, 24.82, 48.80, 4, "B"),
    ("LM", "leste", 50.3, 26.06, 18.47, 3, "B"),
    ("LB", "leste", 50.3, 14.20,  6.61, 3, "B"),
    ("SL", "sul",    0.0, 48.80, 39.96, 3, "B"),
]
NORMAL = {"sul": (0, 1), "norte": (0, -1), "oeste": (1, 0), "leste": (-1, 0)}
ENTRADA_ZONA = {"A": ENTRADA_A, "B": ENTRADA_B}


def carrega_urnas():
    with open(os.path.join(RAIZ, "saidas", "dados.json"), encoding="utf-8") as f:
        d = json.load(f)
    res = {r["Urna"]: r for r in d["residencia_urna"]}
    urnas = []
    for u in d["urnas"]:
        r = res[u["Urna"]]
        dub, tot = r["DUBLIN"], r["TOTAL"]
        fora = sorted(((k, v) for k, v in r.items()
                       if k not in ("Urna", "TOTAL", "DUBLIN") and v),
                      key=lambda kv: -kv[1])
        urnas.append({
            "urna": u["Urna"],
            "secoes": [int(s) for s in (u["Secao_principal"], u["Secao_agregada"])
                       if s == s and s],
            "aptos": tot, "aptos_dublin": dub, "aptos_interior": tot - dub,
            "origem_interior": fora[0][0].title() if fora else None,
            "esperado": round(TAXA_DUBLIN * dub + TAXA_INTERIOR * (tot - dub)),
        })
    return urnas


def simula_fila(esperado, seg_por_voto=SEG_POR_VOTO, passo=5):
    """Fila minuto a minuto. Devolve (pico, hora do pico, encerramento efetivo)."""
    por_passo = [esperado * s / (60 / passo) for s in PERFIL for _ in range(60 // passo)]
    atende = passo * 60 / seg_por_voto
    fila = pico = 0.0
    t_pico = 0
    for i, chega in enumerate(por_passo):
        fila += chega
        fila -= min(fila, atende)
        if fila > pico:
            pico, t_pico = fila, i
    extra = 0
    while fila > 0.01 and extra < 600:
        fila -= min(fila, atende)
        extra += passo
    return math.ceil(pico), ABERTURA + t_pico * passo / 60, FECHAMENTO + extra / 60


def constroi_slots():
    """Expande os trechos em 28 posicoes, cada uma com o comprimento de parede
    disponivel e a distancia ate a porta da sua zona."""
    slots = []
    for tid, parede, fixa, de, ate, n, zona in TRECHOS:
        comp = abs(ate - de) / n
        sinal = 1 if ate > de else -1
        for i in range(n):
            t = de + sinal * (i + 0.5) * comp
            x, y = (t, fixa) if parede in ("sul", "norte") else (fixa, t)
            ex, ey = ENTRADA_ZONA[zona]
            slots.append({
                "trecho": tid, "parede": parede, "zona": zona,
                "normal": NORMAL[parede],
                "x": round(x, 2), "y": round(y, 2),
                "eixo_de": de + sinal * i * comp, "eixo_ate": de + sinal * (i + 1) * comp,
                "larg_disponivel": round(comp, 2),
                "prof_max": PROF_MAX[parede],
                "dist_entrada": round(math.hypot(x - ex, y - ey), 1),
            })
    return slots


def largura_exigida(fila, prof_max):
    """Largura de parede que a baia de fila daquela urna precisa ocupar."""
    if fila <= 0:
        return LARG_MIN_BAIA
    return max(LARG_MIN_BAIA, fila * AREA_PESSOA / prof_max + FOLGA_BAIA)


def aloca(urnas, slots):
    """Aloca as 28 urnas as 28 posicoes de parede sob duas regras.

    (a) Gradiente de carga: dentro de cada zona a carga cresce com a distancia
        ate a porta. Nenhum eleitor de urna leve caminha por tras da fila de
        uma urna pesada, porque as urnas pesadas ficam sempre alem das leves.
    (b) Suficiencia: a baia de fila de cada urna cabe no trecho de parede que
        lhe toca. Os trechos foram escolhidos de modo que profundidade e
        largura disponiveis crescam junto com a distancia ate a porta, o que
        torna as duas regras compativeis.
    """
    def cap_max(s):
        return (s["larg_disponivel"] - FOLGA_BAIA) * s["prof_max"] / AREA_PESSOA

    por_zona = {z: sorted([s for s in slots if s["zona"] == z],
                          key=lambda s: s["dist_entrada"]) for z in "AB"}

    # 1) urnas criticas -> trecho NL, unico com largura para baias profundas
    criticas = sorted([u for u in urnas
                       if largura_exigida(u["fila_pico"], PROF_MAX["norte"]) > 4.0],
                      key=lambda u: -u["esperado"])
    nl = [s for s in por_zona["B"] if s["trecho"] == "NL"]
    assert len(criticas) <= len(nl), (
        f"{len(criticas)} urnas criticas para {len(nl)} posicoes largas")
    fixo = {u["urna"]: s for u, s in
            zip(criticas, sorted(nl, key=lambda s: -cap_max(s)))}

    # 2) demais urnas repartidas entre as zonas equilibrando eleitores, sem
    #    mandar urna para zona cujas baias remanescentes nao comportem a fila
    livres = {z: [s for s in por_zona[z] if s not in fixo.values()] for z in "AB"}
    teto = {z: max(cap_max(s) for s in livres[z]) for z in "AB"}
    zonas = {"A": [], "B": []}
    total = {z: sum(u["esperado"] for u in criticas if fixo[u["urna"]]["zona"] == z)
             for z in "AB"}
    for u in sorted([u for u in urnas if u["urna"] not in fixo],
                    key=lambda u: -u["esperado"]):
        cand = [z for z in "AB" if len(zonas[z]) < len(livres[z])
                and teto[z] >= u["fila_pico"]]
        if not cand:
            cand = [z for z in "AB" if len(zonas[z]) < len(livres[z])]
        z = min(cand, key=lambda z: (total[z], z))
        zonas[z].append(u)
        total[z] += u["esperado"]

    saida = [monta(u, fixo[u["urna"]]) for u in criticas]
    for z in "AB":
        ordenadas = sorted(zonas[z], key=lambda u: (u["fila_pico"], u["esperado"]))
        for slot, u in zip(livres[z], ordenadas):
            saida.append(monta(u, slot))
    return saida, total


def monta(u, slot):
    prof_max = slot["prof_max"]
    larg = min(largura_exigida(u["fila_pico"], prof_max), slot["larg_disponivel"])
    util = max(larg - FOLGA_BAIA, 1.0)
    area = max(u["fila_pico"], 6) * AREA_PESSOA
    prof = max(3.0, min(area / util, prof_max))
    cap = int(util * prof / AREA_PESSOA)
    return {**u, **slot,
            "baia_largura": round(larg, 2),
            "baia_profundidade": round(prof, 1),
            "baia_capacidade": cap,
            "baia_suficiente": cap >= u["fila_pico"],
            "mesarios": 4 if u["fila_pico"] >= 40 else 3}


def classe(u):
    if u["esperado"] >= 550:
        return "critica"
    if u["esperado"] >= 450:
        return "alta"
    if u["esperado"] >= 360:
        return "media"
    return "leve"


def main():
    urnas = carrega_urnas()
    for u in urnas:
        pico, h, fim = simula_fila(u["esperado"])
        u.update(fila_pico=pico, hora_pico=round(h, 2), encerramento=round(fim, 2),
                 fila_pico_45s=simula_fila(u["esperado"], 45)[0],
                 fila_pico_90s=simula_fila(u["esperado"], 90)[0],
                 encerramento_45s=round(simula_fila(u["esperado"], 45)[2], 2),
                 encerramento_90s=round(simula_fila(u["esperado"], 90)[2], 2))
        u["classe"] = classe(u)

    mrvs, total = aloca(urnas, constroi_slots())
    mrvs.sort(key=lambda m: (m["zona"], m["dist_entrada"]))

    balizador = sum(2 * m["baia_profundidade"] + m["baia_largura"] for m in mrvs)
    balizador += 2 * ESPINHA["y1"] + 2 * 15          # espinha dentro e fora
    balizador += 2 * (2 * 12)                        # canais das duas entradas

    out = {
        "premissas": dict(taxa_dublin=TAXA_DUBLIN, taxa_interior=TAXA_INTERIOR,
                          seg_por_voto=SEG_POR_VOTO, perfil_horario=PERFIL,
                          area_por_pessoa_m2=AREA_PESSOA),
        "hall": dict(largura_m=HALL_W, profundidade_m=HALL_H, area_bruta_m2=2238,
                     recorte_sudoeste=RECORTE),
        "portas": PORTAS,
        "papeis_portas": {
            "2.5/2.6": "ENTRADA A — frente oeste (baia de 5,93 m)",
            "2.2/2.3": "ENTRADA B — frente leste (baia de 5,93 m)",
            "2.4":     "SAIDA UNICA — baia central recuada (5,93 m)",
            "2.7":     "Entrada prioritaria da zona A (1,25 m)",
            "2.1":     "Entrada prioritaria da zona B (1,27 m)",
        },
        "espinha_saida": ESPINHA,
        "totais": dict(
            aptos=sum(u["aptos"] for u in urnas),
            esperado=sum(u["esperado"] for u in urnas),
            esperado_A=total["A"], esperado_B=total["B"],
            fila_pico_somada=sum(u["fila_pico"] for u in urnas),
            fila_pico_somada_60s=sum(simula_fila(u["esperado"], 60)[0] for u in urnas),
            fila_pico_somada_45s=sum(u["fila_pico_45s"] for u in urnas),
            fila_pico_somada_90s=sum(u["fila_pico_90s"] for u in urnas),
            baias_insuficientes=[m["urna"] for m in mrvs if not m["baia_suficiente"]],
            balizador_estimado_m=round(balizador),
            mesarios=sum(m["mesarios"] for m in mrvs),
        ),
        "mrvs": mrvs,
    }
    cam = os.path.join(RAIZ, "saidas", "fluxo_dados.json")
    with open(cam, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)

    t = out["totais"]
    print(f"esperado {t['esperado']}  |  zona A {t['esperado_A']}  "
          f"zona B {t['esperado_B']}  (delta {abs(t['esperado_A']-t['esperado_B'])})")
    print(f"fila de pico somada: {t['fila_pico_somada']} pessoas no ponto de "
          f"projeto ({SEG_POR_VOTO}s/voto); {t['fila_pico_somada_45s']} a 45s, "
          f"{t['fila_pico_somada_60s']} a 60s, {t['fila_pico_somada_90s']} a 90s")
    print(f"reserva de fila a mobilizar se o atendimento cair para 60s/voto: "
          f"{t['fila_pico_somada_60s'] - t['fila_pico_somada']} pessoas "
          f"(~{t['fila_pico_somada_60s'] - t['fila_pico_somada']} m2)")
    print(f"balizador de unifila estimado: {t['balizador_estimado_m']} m "
          f"(orcado: 200 m)")
    print(f"baias insuficientes: {t['baias_insuficientes'] or 'nenhuma'}")
    print(f"\n{'zn':>2} {'trecho':>6} {'urna':>6} {'classe':>8} {'apt':>5} {'esp':>5} "
          f"{'fila':>4} {'dist':>5} {'baia (l x p)':>13} {'cap':>4} {'mes':>3} {'fecha':>5}")
    for m in mrvs:
        print(f"{m['zona']:>2} {m['trecho']:>6} {m['urna']:>6} {m['classe']:>8} "
              f"{m['aptos']:>5} {m['esperado']:>5} {m['fila_pico']:>4} "
              f"{m['dist_entrada']:>5} {m['baia_largura']:>5.1f} x{m['baia_profundidade']:>5.1f} "
              f"{m['baia_capacidade']:>4} {m['mesarios']:>3} {m['encerramento']:>5.1f}")


if __name__ == "__main__":
    main()
