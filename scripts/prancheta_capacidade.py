# -*- coding: utf-8 -*-
"""
Quanto cabe SEM mudar o desenho atual.

O layout da prancheta é mantido: as 28 mesas ficam onde estão, encostadas nas
paredes oeste, norte e leste ao longo de toda a altura do salão; as entradas A
e B e a saída central permanecem na parede sul. A serpentina ocupa apenas o que
sobra: da faixa de triagem até o centro, entre as faixas perimetrais.

O que não couber vai para a rua — e o objetivo aqui é dizer quanto.
"""
import json, os, math
from filas_sem_ring3 import carrega, simula, LARG_CANAL, COMP_UNIFILA, PERFIS
from serpentina_hall2 import (HALL_L, HALL_P, NOTCH_X, NOTCH_Y, Y_CENTRO,
                              PASSOS, PERDA_CURVA, GAP_MIN, encaixa, serpentina,
                              capacidade)

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ------------------------------------------------ o que a prancheta impõe
FAIXA = 7.0        # faixa perimetral: mesa + mesários + micro-fila + circulação
APRON = 4.0        # faixa de triagem junto à parede sul
SAIDA_L = 3.0      # corredor da saída central
PORTA_A, PORTA_SAIDA, PORTA_B = 25.2, 29.3, 34.4   # lidas do desenho (±1 m)
FILA_SIMPLES = 0.65   # m de calçada por pessoa, fila de uma pessoa


def zona(faixa=FAIXA, apron=APRON, y_div=Y_CENTRO):
    return {"x0": faixa, "x1": HALL_L - faixa, "y0": apron, "y1": y_div,
            "larg": HALL_L - 2 * faixa, "prof": y_div - apron}


def y_inicio(x0, apron):
    """Blocos sobre o recorte sudoeste começam mais ao norte."""
    return NOTCH_Y + GAP_MIN if x0 < NOTCH_X else apron


def blocos_ns(x0, x1, n_blocos, y_div, apron, rotulo):
    n_can, larg, gap = encaixa(x1 - x0, n_blocos)
    out, x = [], x0
    for i in range(n_blocos):
        y0 = y_inicio(x, apron)
        s = serpentina(larg, y_div - y0, sentido="comprimento")
        s.update({"nome": f"{rotulo}{i + 1}", "x0": round(x, 2),
                  "y0": round(y0, 2), "larg_m": round(larg, 2),
                  "prof_m": round(y_div - y0, 2), "gap_m": round(gap, 2)})
        out.append(s)
        x += larg + gap
    return out


def blocos_lo(x0, x1, n_bandas, y_div, apron, rotulo):
    n_can, prof, gap = encaixa(y_div - apron, n_bandas)
    out, y = [], apron
    for j in range(n_bandas):
        bx0 = max(x0, NOTCH_X) if (x0 < NOTCH_X and y < NOTCH_Y) else x0
        s = serpentina(x1 - bx0, prof, sentido="largura")
        s.update({"nome": f"{rotulo}{j + 1}", "x0": round(bx0, 2),
                  "y0": round(y, 2), "larg_m": round(x1 - bx0, 2),
                  "prof_m": round(prof, 2), "gap_m": round(gap, 2)})
        out.append(s)
        y += prof + gap
    return out


def layout(orientacao, saida_central, faixa=FAIXA, apron=APRON, y_div=Y_CENTRO):
    """saida_central=True mantém o corredor da saída da prancheta cortando a
    zona; False roteia a saída pela faixa perimetral e pelo apron."""
    z = zona(faixa, apron, y_div)
    if saida_central:
        partes = [("A", z["x0"], PORTA_SAIDA - SAIDA_L / 2, 3),
                  ("B", PORTA_SAIDA + SAIDA_L / 2, z["x1"], 3)]
    else:
        partes = [("", z["x0"], z["x1"], 6)]
    bl = []
    for rot, x0, x1, n in partes:
        if orientacao == "N-S":
            bl += blocos_ns(x0, x1, n, y_div, apron, rot or "F")
        else:
            # leste-oeste: cada metade empilha bandas; sem saída central ainda
            # são duas metades, separadas pela espinha necessária às 2 portas
            if rot:
                bl += blocos_lo(x0, x1, n, y_div, apron, rot)
            else:
                meio = (x0 + x1) / 2
                bl += blocos_lo(x0, meio - 1.0, 3, y_div, apron, "A")
                bl += blocos_lo(meio + 1.0, x1, 3, y_div, apron, "B")
    return {"orientacao": orientacao, "saida_central": saida_central,
            "zona": z, "blocos": bl}


def resume(lay):
    b = lay["blocos"]
    metros = sum(x["metros_canal"] for x in b)
    curvas = sum(x["curvas"] for x in b)
    barreira = sum(x["barreira_m"] for x in b)
    caps = {k: round(sum(capacidade(x, p) for x in b)) for k, p in PASSOS.items()}
    return {"orientacao": lay["orientacao"], "saida_central": lay["saida_central"],
            "blocos": len(b), "canais": sum(x["canais"] for x in b),
            "area_m2": round(sum(x["area_m2"] for x in b)),
            "metros_canal": round(metros), "curvas": curvas,
            "barreira_m": round(barreira),
            "unifila_un": math.ceil(barreira / COMP_UNIFILA),
            "capacidade": caps,
            "por_bloco": [{"nome": x["nome"], "canais": x["canais"],
                           "larg_m": x["larg_m"], "prof_m": x["prof_m"],
                           "metros_canal": round(x["metros_canal"]),
                           "cap": round(capacidade(x, PASSOS["projeto"]))} for x in b]}


def transbordo(urnas, teto, n_urnas=28):
    """Quanta gente sobra para a rua, e por quanto tempo."""
    out = []
    for perfil in ("base", "pico_manha"):
        for ts in (45, 60, 75, 90):
            r = simula(urnas, ts, perfil, n_urnas=n_urnas)
            serie = r["serie"]
            acima = [(h, q) for h, q in serie if q > teto]
            pico = r["pico_total"]
            out.append({
                "perfil": perfil, "t_servico": ts, "pico": round(pico),
                "transbordo_pico": max(0, round(pico - teto)),
                "horas_acima": round(len(acima) * 5 / 60, 1),
                "inicio": acima[0][0] if acima else None,
                "fim": acima[-1][0] if acima else None,
                "calcada_m": round(max(0, pico - teto) * FILA_SIMPLES)})
    return out


if __name__ == "__main__":
    d, urnas = carrega()
    z = zona()
    print("DESENHO ATUAL, INALTERADO")
    print(f"  mesas nas três paredes · entradas A (x={PORTA_A}) e B (x={PORTA_B}) "
          f"· saída central (x={PORTA_SAIDA})")
    print(f"  faixa perimetral {FAIXA:.1f} m · triagem {APRON:.1f} m · "
          f"linha no centro y={Y_CENTRO:.2f} m")
    print(f"  zona de fila disponível: {z['larg']:.1f} x {z['prof']:.2f} m "
          f"= {z['larg']*z['prof']:.0f} m² brutos\n")

    res = {}
    print(f"{'variante':<44}{'blocos':>7}{'canais':>7}{'canal m':>9}"
          f"{'projeto':>9}{'máximo':>8}{'unifila':>9}")
    for ori in ("N-S", "L-O"):
        for sc in (True, False):
            lay = layout(ori, sc)
            r = resume(lay)
            nome = (f"{ori} · " + ("saída central mantida" if sc else
                                   "saída pela faixa perimetral"))
            res[nome] = r
            c = r["capacidade"]
            print(f"{nome:<44}{r['blocos']:>7}{r['canais']:>7}{r['metros_canal']:>9}"
                  f"{c['projeto']:>9}{c['maximo']:>8}{r['unifila_un']:>9}")

    principal = res["N-S · saída central mantida"]
    print(f"\n   blocos de {principal['orientacao']} com a saída central:")
    for b in principal["por_bloco"]:
        print(f"     {b['nome']}  {b['canais']} canais x {b['prof_m']:>5.1f} m "
              f"({b['larg_m']:>4.1f} m de largura) | {b['metros_canal']:>3} m | "
              f"{b['cap']:>3} pessoas")
    lados = {}
    for b in principal["por_bloco"]:
        lados.setdefault(b["nome"][0], 0)
        lados[b["nome"][0]] += b["cap"]
    tot = sum(lados.values())
    print(f"\n   porta A {lados.get('A',0)} ({100*lados.get('A',0)/tot:.0f}%) | "
          f"porta B {lados.get('B',0)} ({100*lados.get('B',0)/tot:.0f}%) "
          f"-> a divisão 50/50 de urnas por porta precisa ser refeita nesta proporção")

    teto = principal["capacidade"]["projeto"]
    teto_max = principal["capacidade"]["maximo"]
    print(f"\n\nO QUE VAI PARA A RUA — teto de {teto} pessoas (projeto)\n")
    print(f"{'perfil':<12}{'t/eleitor':>10}{'pico':>7}{'dentro':>8}{'na rua':>8}"
          f"{'horas acima':>13}{'calçada':>10}")
    tb = transbordo(urnas, teto)
    for t in tb:
        print(f"{t['perfil']:<12}{str(t['t_servico'])+' s':>10}{t['pico']:>7}"
              f"{min(t['pico'], teto):>8}{t['transbordo_pico']:>8}"
              f"{t['horas_acima']:>13}{str(t['calcada_m'])+' m':>10}")

    print(f"\n\nMESMA CONTA NO MÁXIMO ADMISSÍVEL ({teto_max} pessoas)\n")
    print(f"{'perfil':<12}{'t/eleitor':>10}{'na rua':>8}{'calçada':>10}")
    tb2 = transbordo(urnas, teto_max)
    for t in tb2:
        print(f"{t['perfil']:<12}{str(t['t_servico'])+' s':>10}"
              f"{t['transbordo_pico']:>8}{str(t['calcada_m'])+' m':>10}")

    print("\n\nALAVANCAS QUE NÃO MEXEM NO ARRANJO DAS MESAS\n")
    print(f"{'faixa perimetral':>18}{'triagem':>10}{'canais':>8}{'projeto':>9}{'ganho':>8}")
    base = None
    alav = []
    for faixa in (7.0, 6.0, 5.5, 5.0):
        for ap in (4.0, 2.5):
            r = resume(layout("N-S", True, faixa=faixa, apron=ap))
            p = r["capacidade"]["projeto"]
            if base is None:
                base = p
            print(f"{faixa:>15.1f} m{ap:>8.1f} m{r['canais']:>8}{p:>9}"
                  f"{100*p/base-100:>7.0f}%")
            alav.append({"faixa_m": faixa, "apron_m": ap, "canais": r["canais"],
                         "projeto": p})

    json.dump({"premissas": {"faixa_perimetral_m": FAIXA, "apron_m": APRON,
                             "saida_central_m": SAIDA_L, "canal_m": LARG_CANAL,
                             "passos": PASSOS,
                             "portas": {"A": PORTA_A, "saida": PORTA_SAIDA,
                                        "B": PORTA_B}},
               "zona": z, "variantes": res, "transbordo_projeto": tb,
               "transbordo_maximo": tb2, "alavancas": alav},
              open(os.path.join(BASE, "saidas", "prancheta_capacidade.json"), "w"),
              ensure_ascii=False, indent=2)
    print("\n-> saidas/prancheta_capacidade.json")
