# -*- coding: utf-8 -*-
"""
Dimensionamento de filas para o RDS Hall 2 SEM o Ring 3.

Simula, urna a urna (dados reais de saidas/dados.json), a fila que se acumula
dentro do salao ao longo do dia e converte o pico em area, metros de barreira,
unidades de unifila e de CCB (crowd control barrier).

Premissas explicitas em PREMISSAS; todas parametrizaveis.
"""
import json, os, math

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DADOS = os.path.join(BASE, "saidas", "dados.json")

# ---------------------------------------------------------------- premissas
TAXA_DUBLIN = 0.74     # comparecimento 2022, secoes domiciliadas em Dublin
TAXA_INTERIOR = 0.50   # comparecimento 2022, secoes do interior
PASSO_MIN = 5          # granularidade da simulacao, em minutos
ABERTURA, FECHAMENTO = 8.0, 17.0

# perfil de chegada (fracao do comparecimento do dia por hora, 8h->17h)
PERFIS = {
    "base":  [0.10, 0.14, 0.15, 0.14, 0.12, 0.10, 0.09, 0.08, 0.08],
    "pico_manha": [0.14, 0.17, 0.16, 0.13, 0.11, 0.09, 0.07, 0.07, 0.06],
}
# fracao do comparecimento que ja esta na porta as 8h00 (fila de abertura)
FILA_ABERTURA = {"base": 0.03, "pico_manha": 0.05}

# densidade de espera (UK Purple Guide: 2 p/m2 e o teto de area de espera)
DENS_PROJETO = 1.7     # p/m2 na area bruta do bloco de fila (conservador)
LARG_CANAL = 1.10      # m, largura util do canal de fila
COMP_UNIFILA = 2.00    # m por poste retratil (orcamento: 100 un = 200 m)
COMP_CCB = 2.00        # m por grade metalica de contencao

def carrega():
    d = json.load(open(DADOS, encoding="utf-8"))
    res = {r["Urna"]: r for r in d["residencia_urna"]}
    urnas = []
    for u in d["urnas"]:
        r = res[u["Urna"]]
        dub = r["DUBLIN"]
        interior = r["TOTAL"] - dub
        esperado = dub * TAXA_DUBLIN + interior * TAXA_INTERIOR
        urnas.append({"urna": u["Urna"], "aptos": u["Total_combinado"],
                      "dublin": dub, "interior": interior, "esperado": esperado})
    return d, urnas

def perfil_por_passo(perfil):
    """Distribui o perfil horario em passos de PASSO_MIN, interpolando."""
    passos_por_hora = 60 // PASSO_MIN
    out = []
    for h in perfil:
        out += [h / passos_por_hora] * passos_por_hora
    return out

def simula(urnas, t_servico, perfil_nome, n_urnas=None, fator_extra=1.0):
    """Fila por urna, em paralelo. Retorna serie temporal do total em fila."""
    perfil = PERFIS[perfil_nome]
    fr = perfil_por_passo(perfil)
    # redistribuicao: se n_urnas > len(urnas), o eleitorado e reparticionado
    esperados = [u["esperado"] * fator_extra for u in urnas]
    if n_urnas and n_urnas != len(esperados):
        total = sum(esperados)
        esperados = [total / n_urnas] * n_urnas   # caso ideal, carga uniforme
    cap_passo = (PASSO_MIN * 60) / t_servico      # eleitores atendidos/urna/passo
    filas = [e * FILA_ABERTURA[perfil_nome] for e in esperados]
    serie, atendidos = [], [0.0] * len(esperados)
    for k, f in enumerate(fr):
        for i, e in enumerate(esperados):
            filas[i] += e * f * (1 - FILA_ABERTURA[perfil_nome])
            s = min(filas[i], cap_passo)
            filas[i] -= s
            atendidos[i] += s
        serie.append((ABERTURA + k * PASSO_MIN / 60.0, sum(filas), list(filas)))
    # esvaziamento apos as 17h (quem entrou ate 17h vota)
    t, restante = FECHAMENTO, list(filas)
    while sum(restante) > 0.5 and t < 26:
        for i in range(len(restante)):
            restante[i] = max(0.0, restante[i] - cap_passo)
        t += PASSO_MIN / 60.0
    pico = max(serie, key=lambda s: s[1])
    return {"pico_total": pico[1], "pico_hora": pico[0],
            "pico_por_urna": max(pico[2]) if pico[2] else 0,
            "fecha_as": t, "serie": [(round(a, 2), round(b)) for a, b, _ in serie]}

def barreiras(pessoas, dens=DENS_PROJETO, larg=LARG_CANAL):
    """Area, metros de barreira e unidades para conter N pessoas em serpentina."""
    area = pessoas / dens
    # serpentina: ~1 linha de barreira por canal + 1 de fechamento
    metros = area / larg * 1.0
    return {"pessoas": round(pessoas), "area_m2": round(area),
            "barreira_m": round(metros),
            "unifila_un": math.ceil(metros / COMP_UNIFILA),
            "ccb_un": math.ceil(metros / COMP_CCB)}

if __name__ == "__main__":
    d, urnas = carrega()
    tot_apt = sum(u["aptos"] for u in urnas)
    tot_esp = sum(u["esperado"] for u in urnas)
    print(f"Aptos {tot_apt} | comparecimento esperado {tot_esp:,.0f} "
          f"({tot_esp/tot_apt:.1%})")
    print(f"Urnas {len(urnas)} | maior urna {max(u['esperado'] for u in urnas):.0f} esperados\n")

    print(f"{'cenario':<34}{'pico fila':>10}{'hora':>7}{'pior urna':>11}{'fecha':>8}")
    linhas = []
    for perfil in ("base", "pico_manha"):
        for n in (28, 32, 38):
            for ts in (45, 60, 75, 90):
                r = simula(urnas, ts, perfil, n_urnas=n)
                nome = f"{perfil} | {n} urnas | {ts}s"
                hh = int(r['fecha_as']); mm = int((r['fecha_as']-hh)*60)
                print(f"{nome:<34}{r['pico_total']:>10.0f}{r['pico_hora']:>7.1f}"
                      f"{r['pico_por_urna']:>11.0f}{hh:>6}:{mm:02d}")
                linhas.append({"perfil": perfil, "urnas": n, "t_servico": ts,
                               "pico": round(r["pico_total"]),
                               "hora_pico": round(r["pico_hora"], 2),
                               "pior_urna": round(r["pico_por_urna"]),
                               "fecha_as": round(r["fecha_as"], 2)})

    print("\nDimensionamento de contencao (densidade %.1f p/m2, canal %.2f m):" %
          (DENS_PROJETO, LARG_CANAL))
    print(f"{'pico a conter':>14}{'area m2':>10}{'barreira m':>12}{'unifila':>9}{'CCB':>7}")
    dims = {}
    for p in (200, 300, 400, 500, 600, 800, 1000, 1200):
        b = barreiras(p)
        dims[p] = b
        print(f"{p:>14}{b['area_m2']:>10}{b['barreira_m']:>12}"
              f"{b['unifila_un']:>9}{b['ccb_un']:>7}")

    json.dump({"premissas": {"taxa_dublin": TAXA_DUBLIN, "taxa_interior": TAXA_INTERIOR,
                             "densidade_p_m2": DENS_PROJETO, "largura_canal_m": LARG_CANAL,
                             "perfis": PERFIS, "fila_abertura": FILA_ABERTURA},
               "total_aptos": tot_apt, "comparecimento_esperado": round(tot_esp),
               "cenarios": linhas, "dimensionamento": dims},
              open(os.path.join(BASE, "saidas", "filas_sem_ring3.json"), "w"),
              ensure_ascii=False, indent=2)
