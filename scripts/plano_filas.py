# -*- coding: utf-8 -*-
"""
Plano fisico de filas no RDS Hall 2 SEM o Ring 3.

1) Reparte as 28 urnas em 6 clusters (3 por porta), equilibrados por
   comparecimento esperado, com as urnas grandes espalhadas.
2) Dimensiona o ANEL DE ESPERA interno (o substituto do Ring 3).
3) Emite lista de materiais (unifila / CCB), equipe e a comparacao com a
   alternativa de fila na rua.
"""
import json, os, math
from filas_sem_ring3 import (carrega, simula, DENS_PROJETO, LARG_CANAL,
                             COMP_UNIFILA, COMP_CCB, PERFIS)

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ------------------------------------------------- geometria real do Hall 2
HALL_L, HALL_P = 50.2, 44.5          # largura x profundidade, m (ficha RDS)
HALL_AREA = 2238                     # m2 brutos (ficha RDS)
RECORTE = (11.7, 7.4)                # recorte do canto sudoeste (estimado)
FAIXA_SECOES = 7.0                   # profundidade da faixa de mesas/urnas
ANEL_PROF = 7.7                      # profundidade do anel de espera (7 canais)
DENS_EXTERNA = 2.0                   # p/m2, teto de area de espera (Purple Guide)
FILA_SIMPLES = 0.65                  # m de fila por pessoa, fila de 1 pessoa

# ---------------------------------------------------------------- clusters
def clusters(urnas, n=6):
    """LPT: a maior urna vai sempre para o cluster mais leve, respeitando
    teto de 5 urnas por cluster (28 = 5+5+5+5+4+4)."""
    cl = [[] for _ in range(n)]
    teto = math.ceil(len(urnas) / n) + 1          # folga de 1 urna por cluster
    for u in sorted(urnas, key=lambda x: -x["esperado"]):
        cand = [i for i in range(n) if len(cl[i]) < teto]
        i = min(cand, key=lambda i: sum(x["esperado"] for x in cl[i]))
        cl[i].append(u)
    # refino: troca pares entre o cluster mais pesado e o mais leve enquanto
    # isso reduzir a amplitude
    carga = lambda c: sum(x["esperado"] for x in c)
    for _ in range(500):
        hi = max(range(n), key=lambda i: carga(cl[i]))
        lo = min(range(n), key=lambda i: carga(cl[i]))
        amp = carga(cl[hi]) - carga(cl[lo])
        melhor = None
        for a in cl[hi]:
            for b in cl[lo]:
                d = a["esperado"] - b["esperado"]
                if 0 < 2 * d < 2 * amp and (melhor is None or
                                            abs(amp - 2 * d) < melhor[0]):
                    melhor = (abs(amp - 2 * d), a, b)
        if not melhor:
            break
        _, a, b = melhor
        cl[hi].remove(a); cl[lo].remove(b); cl[hi].append(b); cl[lo].append(a)
    return cl

# ------------------------------------------------------------ anel de espera
def anel(prof=ANEL_PROF, faixa=FAIXA_SECOES):
    """Anel em U (paredes oeste, norte e leste) entre a faixa de secoes e o
    nucleo livre. Devolve area, capacidade e metros de barreira."""
    x0, x1 = faixa, faixa + prof                       # coluna oeste
    y0, y1 = faixa, HALL_P - faixa                     # extensao vertical util
    col_oeste = prof * (HALL_P - faixa - RECORTE[1] - 0.6)
    col_leste = prof * (HALL_P - 2 * faixa)
    larg_norte = HALL_L - 2 * (faixa + prof)
    tira_norte = prof * larg_norte
    area = col_oeste + col_leste + tira_norte
    nucleo = larg_norte * (HALL_P - 2 * faixa - prof)
    metros = area / LARG_CANAL                         # 1 linha por canal
    return {"prof_m": prof, "area_m2": round(area),
            "capacidade_p": round(area * DENS_PROJETO),
            "capacidade_max_p": round(area * DENS_EXTERNA),
            "nucleo_livre_m2": round(nucleo),
            "nucleo_reserva_p": round(nucleo * DENS_PROJETO),
            "barreira_m": round(metros),
            "unifila_un": math.ceil(metros / COMP_UNIFILA),
            "canais": int(prof / LARG_CANAL + 1e-6),
            "col_oeste_m2": round(col_oeste), "col_leste_m2": round(col_leste),
            "tira_norte_m2": round(tira_norte)}

# ----------------------------------------------------------------- equipe
def equipe(chegada_pico_h, frac_sem_secao=0.30, t_consulta=45, t_direcao=5,
           n_portas=2, n_clusters=6):
    """Postos necessarios na triagem, que e a etapa nao paralelizavel."""
    direcao = math.ceil(chegada_pico_h * t_direcao / 3600)
    consulta = math.ceil(chegada_pico_h * frac_sem_secao * t_consulta / 3600)
    return {"chegada_pico_h": round(chegada_pico_h),
            "frac_sem_secao": frac_sem_secao,
            "triadores_porta": max(n_portas, direcao),
            "postos_consulta": consulta,
            "liberadores_cluster": n_clusters,
            "coordenadores_parede": 3,
            "volantes": 2,
            "total": max(n_portas, direcao) + consulta + n_clusters + 3 + 2}

# ------------------------------------------------------------------- rua
def na_rua(pessoas, largura_calcada=2.5, min_livre=1.5):
    """Comprimento de calcada consumido por uma fila na rua."""
    util = largura_calcada - min_livre
    abreast = max(1, int(util // 0.6))
    comp = pessoas * FILA_SIMPLES / abreast
    return {"pessoas": pessoas, "calcada_m": round(largura_calcada, 1),
            "pessoas_lado_a_lado": abreast, "comprimento_m": round(comp),
            "equivalente_anel_m2": round(pessoas / DENS_PROJETO)}

def materiais(anel_d, retencao_externa=600, n_urnas=28, n_portas=2):
    """Lista de materiais por zona. CCB onde ha pressao de multidao, tempo e
    intemperie (fora); unifila dentro, onde e so canalizacao."""
    z = []
    area_ext = retencao_externa / DENS_EXTERNA
    lado = math.sqrt(area_ext * 1.4)                 # curral ~1,4:1
    curto = area_ext / lado
    div = max(1, int(curto // 3.3) - 1)
    m = 2 * (lado + curto) + div * lado
    z.append(["A. Reten\u00e7\u00e3o externa (p\u00e1tio do RDS)", 0, math.ceil(m / COMP_CCB),
              f"{retencao_externa} pessoas em {area_ext:.0f} m2 "
              f"({lado:.0f}x{curto:.0f} m), {div} divisores"])
    z.append(["B. Corredor port\u00e3o -> porta", 0, math.ceil(2 * 40 / COMP_CCB),
              "2 linhas x 40 m"])
    z.append(["C. Funis de porta e triagem", 0, math.ceil(n_portas * 2 * 8 / COMP_CCB),
              f"{n_portas} portas x 2 linhas x 8 m"])
    z.append(["D. Anel de espera interno", anel_d["unifila_un"], 0,
              f"{anel_d['area_m2']} m2, {anel_d['canais']} canais, "
              f"{anel_d['barreira_m']} m"])
    z.append(["E. Micro-filas de se\u00e7\u00e3o", math.ceil(n_urnas * 4 / COMP_UNIFILA), 0,
              f"{n_urnas} urnas x 4 m (mesa/parede como 2\u00ba lado)"])
    z.append(["F. Canal de sa\u00edda e sinaliza\u00e7\u00e3o de piso",
              math.ceil(50 / COMP_UNIFILA), 0, "50 m"])
    return z


if __name__ == "__main__":
    d, urnas = carrega()
    cl = clusters(urnas)
    saida = {}

    print("1) CLUSTERS — 3 filas por porta, 6 no total\n")
    print(f"{'fila':<6}{'urnas':>6}{'aptos':>7}{'esperado':>10}   urnas")
    loads = []
    comp = []
    for i, c in enumerate(cl):
        nome = f"{'AB'[i//3]}{i%3+1}"
        esp = sum(u['esperado'] for u in c); loads.append(esp)
        comp.append({"fila": nome, "urnas": [u["urna"] for u in c],
                     "aptos": sum(u["aptos"] for u in c), "esperado": round(esp)})
        print(f"{nome:<6}{len(c):>6}{sum(u['aptos'] for u in c):>7}{esp:>10.0f}"
              f"   {', '.join(str(u['urna']) for u in c)}")
    med = sum(loads)/len(loads)
    print(f"\n   equilibrio: {min(loads):.0f} a {max(loads):.0f} esperados por fila "
          f"(amplitude {100*(max(loads)-min(loads))/med:.1f}% da media)")
    porta_a, porta_b = sum(loads[:3]), sum(loads[3:])
    print(f"   porta A {porta_a:.0f} ({100*porta_a/sum(loads):.0f}%) | "
          f"porta B {porta_b:.0f} ({100*porta_b/sum(loads):.0f}%)")
    saida["clusters"] = comp

    print("\n2) ANEL DE ESPERA INTERNO (substituto do Ring 3)\n")
    for prof in (4.4, 6.6, 7.7, 8.8):
        a = anel(prof)
        print(f"   prof {prof:>4} m ({a['canais']} canais): area {a['area_m2']:>4} m2 | "
              f"capacidade {a['capacidade_p']:>5} p (teto {a['capacidade_max_p']}) | "
              f"nucleo livre {a['nucleo_livre_m2']:>4} m2 | "
              f"unifila {a['unifila_un']:>3} un ({a['barreira_m']} m)")
    a = anel()
    saida["anel"] = a
    print(f"\n   ESCOLHIDO: {a['prof_m']} m / {a['canais']} canais -> "
          f"{a['capacidade_p']} pessoas em {a['area_m2']} m2 "
          f"({100*a['area_m2']/HALL_AREA:.0f}% do Hall 2)")
    print(f"   nucleo central livre: {a['nucleo_livre_m2']} m2 "
          f"(reserva de contingencia: +{a['nucleo_reserva_p']} pessoas)")
    print(f"   oeste {a['col_oeste_m2']} m2 | norte {a['tira_norte_m2']} m2 | "
          f"leste {a['col_leste_m2']} m2")

    print("\n3) FILA ESPERADA vs CAPACIDADE DO ANEL\n")
    cen = []
    for perfil in ("base", "pico_manha"):
        for ts in (45, 60, 75, 90):
            r = simula(urnas, ts, perfil, n_urnas=28)
            cabe = r["pico_total"] <= a["capacidade_p"]
            cabe_tudo = r["pico_total"] <= a["capacidade_p"] + a["nucleo_reserva_p"]
            st = "cabe no anel" if cabe else ("consome o nucleo" if cabe_tudo
                                              else "NAO CABE no salao")
            print(f"   {perfil:<11}{ts:>3}s  pico {r['pico_total']:>6.0f} p  "
                  f"({100*r['pico_total']/a['capacidade_p']:>5.0f}% do anel)  {st}")
            cen.append({"perfil": perfil, "t_servico": ts,
                        "pico": round(r["pico_total"]), "situacao": st})
    saida["cenarios"] = cen

    print("\n4) EQUIPE DE FLUXO (etapa nao paralelizavel = triagem)\n")
    eq = {}
    for perfil in ("base", "pico_manha"):
        pico_h = max(PERFIS[perfil]) * 11416
        for frac in (0.30, 0.10):
            e = equipe(pico_h, frac_sem_secao=frac)
            print(f"   {perfil:<11} chegada de pico {e['chegada_pico_h']:>5}/h | "
                  f"{frac:.0%} sem saber a secao -> triadores {e['triadores_porta']}, "
                  f"consulta {e['postos_consulta']}, TOTAL {e['total']} pessoas")
            eq[f"{perfil}_{int(frac*100)}"] = e
    saida["equipe"] = eq

    print("\n5) ALTERNATIVA: FILA NA RUA\n")
    rua = []
    for p in (300, 400, 600, 900):
        for larg in (2.5, 4.0):
            r = na_rua(p, larg)
            print(f"   {p:>4} pessoas | calcada {larg} m -> {r['pessoas_lado_a_lado']} "
                  f"por fileira, {r['comprimento_m']:>4} m de calcada "
                  f"(dentro: {r['equivalente_anel_m2']} m2)")
            rua.append(r)
    saida["rua"] = rua

    print("\n6) LISTA DE MATERIAIS\n")
    mat = materiais(a)
    print(f"   {'zona':<38}{'unifila':>9}{'CCB':>6}   detalhe")
    su = sc = 0
    for nome, u, c, obs in mat:
        su += u; sc += c
        print(f"   {nome:<38}{u:>9}{c:>6}   {obs}")
    print(f"   {'TOTAL':<38}{su:>9}{sc:>6}")
    print(f"\n   unifila: {su} un = {su*COMP_UNIFILA:.0f} m | "
          f"CCB: {sc} un = {sc*COMP_CCB:.0f} m")
    print(f"   or\u00e7amento atual: 100 unifila (200 m) -> faltam {su-100} unidades")
    print(f"   custo unit\u00e1rio do or\u00e7amento: EUR 13,03/unifila -> "
          f"acr\u00e9scimo de EUR {(su-100)*13.03:,.0f}")
    saida["materiais"] = [{"zona": z[0], "unifila": z[1], "ccb": z[2], "obs": z[3]}
                          for z in mat]
    saida["materiais_total"] = {"unifila": su, "ccb": sc}

    json.dump(saida, open(os.path.join(BASE, "saidas", "plano_filas.json"), "w"),
              ensure_ascii=False, indent=2)
    print("\n-> saidas/plano_filas.json")
