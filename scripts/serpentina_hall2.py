# -*- coding: utf-8 -*-
"""
Quanta fila cabe DENTRO do Hall 2, sem pátio do RDS, sem rua e sem Ring 3.

Zona de fila: da parede sul (portas A e B) até o centro do salão.
Duas orientações de serpentina comparadas:
  N-S: canais no sentido norte-sul, 6 faixas lado a lado na largura.
  L-O: canais no sentido leste-oeste, 2 metades (uma por porta) x 3 bandas.
Em ambas, a organização por porta de entrada é preservada: 3 filas por porta.
"""
import json, os, math
from filas_sem_ring3 import (carrega, simula, LARG_CANAL, COMP_UNIFILA,
                             COMP_CCB, PERFIS)

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ------------------------------------------------------- geometria do Hall 2
HALL_L, HALL_P = 50.2, 44.5
HALL_AREA = 2238
NOTCH_X, NOTCH_Y = 11.7, 7.4        # recorte do canto sudoeste (estimado)
CAP_RECINTO = 2900                  # capacidade "reception" na ficha do RDS

APRON = 4.0                         # faixa livre junto às portas (triagem)
MARGEM = 2.0                        # corredor de egresso junto às paredes
GAP_MIN = 1.20                      # corredor mínimo entre blocos de fila
ESPINHA = 2.0                       # corredor central (layout L-O)
Y_CENTRO = HALL_P / 2               # 22,25 m — o "centro" pedido

# passo de fila, em metros de canal por pessoa
PASSOS = {"confortavel": 0.90, "projeto": 0.65, "maximo": 0.50}
PERDA_CURVA = 0.5                   # pessoas perdidas por curva de retorno


def serpentina(largura, comprimento, canal=LARG_CANAL, sentido="longo"):
    """Serpentina num retângulo. 'sentido' diz ao longo de qual lado correm
    os canais: 'largura' (canais paralelos ao lado 'largura') ou
    'comprimento'. Devolve canais, metros de canal, curvas e barreira."""
    if sentido == "largura":
        n = int(comprimento / canal + 1e-9)
        comp_canal = largura
        barreira = (n + 1) * largura
    else:
        n = int(largura / canal + 1e-9)
        comp_canal = comprimento
        barreira = (n + 1) * comprimento
    return {"canais": n, "comp_canal_m": comp_canal,
            "metros_canal": n * comp_canal, "curvas": max(0, n - 1),
            "barreira_m": barreira, "area_m2": largura * comprimento}


def capacidade(s, passo):
    return max(0.0, s["metros_canal"] / passo - s["curvas"] * PERDA_CURVA)


def encaixa(disponivel, n_blocos, canal=LARG_CANAL, gap_min=GAP_MIN):
    """Maior nº de canais por bloco que cabe em 'disponivel' deixando pelo
    menos gap_min entre blocos. Devolve (canais, largura_bloco, gap)."""
    for n in range(20, 0, -1):
        larg = n * canal
        sobra = disponivel - n_blocos * larg
        if n_blocos > 1 and sobra >= (n_blocos - 1) * gap_min:
            return n, larg, sobra / (n_blocos - 1)
        if n_blocos == 1 and sobra >= 0:
            return n, larg, 0.0
    return 0, 0.0, 0.0


def layout_ns(y_div=Y_CENTRO, n_faixas=6):
    """6 faixas lado a lado; canais correm norte-sul. Entrada de cada faixa
    no sul (junto às portas), cabeça no norte (junto ao piso de votação)."""
    x0, x1 = MARGEM, HALL_L - MARGEM
    n_can, larg, gap = encaixa(x1 - x0, n_faixas)
    blocos = []
    x = x0
    for i in range(n_faixas):
        # faixas que pegam o recorte sudoeste começam mais ao norte
        y0 = NOTCH_Y + GAP_MIN if x < NOTCH_X else APRON   # corredor de acesso lateral
        s = serpentina(larg, y_div - y0, sentido="comprimento")
        s.update({"nome": f"{'AB'[i // 3]}{i % 3 + 1}", "x0": round(x, 2),
                  "x1": round(x + larg, 2), "y0": round(y0, 2),
                  "y1": round(y_div, 2), "prof_m": round(y_div - y0, 2),
                  "larg_m": round(larg, 2), "gap_m": round(gap, 2)})
        blocos.append(s)
        x += larg + gap
    return {"orientacao": "N-S", "blocos": blocos}


def layout_lo(y_div=Y_CENTRO, bandas=3):
    """2 metades (porta A a oeste, porta B a leste) separadas por espinha
    central; 3 bandas empilhadas por metade; canais correm leste-oeste."""
    x0, x1 = MARGEM, HALL_L - MARGEM
    meio = (x0 + x1) / 2
    metades = [("A", x0, meio - ESPINHA / 2), ("B", meio + ESPINHA / 2, x1)]
    n_can, prof, gap = encaixa(y_div - APRON, bandas)
    blocos = []
    for letra, mx0, mx1 in metades:
        y = APRON
        for j in range(bandas):
            bx0 = mx0
            # a banda mais ao sul da metade A esbarra no recorte sudoeste
            if letra == "A" and y < NOTCH_Y:
                bx0 = max(mx0, NOTCH_X)
            s = serpentina(mx1 - bx0, prof, sentido="largura")
            s.update({"nome": f"{letra}{j + 1}", "x0": round(bx0, 2),
                      "x1": round(mx1, 2), "y0": round(y, 2),
                      "y1": round(y + prof, 2), "prof_m": round(prof, 2),
                      "larg_m": round(mx1 - bx0, 2), "gap_m": round(gap, 2)})
            blocos.append(s)
            y += prof + gap
    return {"orientacao": "L-O", "blocos": blocos}


def resume(lay):
    b = lay["blocos"]
    area = sum(x["area_m2"] for x in b)
    metros = sum(x["metros_canal"] for x in b)
    curvas = sum(x["curvas"] for x in b)
    barreira = sum(x["barreira_m"] for x in b)
    caps = {k: round(sum(capacidade(x, p) for x in b)) for k, p in PASSOS.items()}
    return {"orientacao": lay["orientacao"], "blocos": len(b),
            "area_m2": round(area), "metros_canal": round(metros),
            "curvas": curvas, "barreira_m": round(barreira),
            "unifila_un": math.ceil(barreira / COMP_UNIFILA),
            "densidade_projeto_p_m2": round(caps["projeto"] / area, 2),
            "capacidade": caps,
            "por_bloco": [{"nome": x["nome"], "canais": x["canais"],
                           "larg_m": x["larg_m"], "prof_m": x["prof_m"],
                           "metros_canal": round(x["metros_canal"]),
                           "cap_projeto": round(capacidade(x, PASSOS["projeto"]))}
                          for x in b]}


MOD_ILHA = 3.2 * 4.0        # módulo de uma seção em ilha: mesa+urna+operação
FATOR_CIRC = 1.8            # multiplicador de circulação sobre os módulos


def parede_para_secoes(y_div, n_urnas=28):
    """Espaço restante para as MRV ao norte da linha divisória, nas duas
    hipóteses: encostadas nas paredes, ou em ilhas no meio do piso."""
    total = HALL_L + 2 * (HALL_P - y_div)
    area_norte = HALL_L * (HALL_P - y_div)
    precisa = n_urnas * MOD_ILHA * FATOR_CIRC
    return {"y_div": y_div, "parede_m": round(total, 1),
            "passo_por_urna_m": round(total / n_urnas, 2),
            "vao_livre_m": round(total / n_urnas - 1.8, 2),
            "area_norte_m2": round(area_norte),
            "area_ilhas_necessaria_m2": round(precisa),
            "ilhas_cabem": area_norte >= precisa,
            "folga_ilhas_m2": round(area_norte - precisa)}


def t_servico_maximo(urnas, teto, perfil, n_urnas=28):
    """Maior tempo por eleitor que mantém o pico de fila abaixo do teto."""
    ok = None
    for ts in range(30, 121):
        r = simula(urnas, ts, perfil, n_urnas=n_urnas)
        if r["pico_total"] <= teto:
            ok = ts
        else:
            break
    return ok


if __name__ == "__main__":
    d, urnas = carrega()
    saida = {"premissas": {"passos_m_por_pessoa": PASSOS, "canal_m": LARG_CANAL,
                           "apron_m": APRON, "margem_m": MARGEM,
                           "gap_min_m": GAP_MIN, "perda_por_curva": PERDA_CURVA}}

    print("ZONA DE FILA: parede sul -> centro do salão (y = 0 a %.2f m)\n" % Y_CENTRO)
    lays = [layout_ns(), layout_lo()]
    res = [resume(l) for l in lays]
    saida["layouts"] = res

    print(f"{'':<14}{'blocos':>7}{'área m²':>9}{'canais m':>10}{'curvas':>8}"
          f"{'confort.':>10}{'projeto':>9}{'máximo':>8}{'unifila':>9}")
    for r in res:
        c = r["capacidade"]
        print(f"{r['orientacao']:<14}{r['blocos']:>7}{r['area_m2']:>9}"
              f"{r['metros_canal']:>10}{r['curvas']:>8}{c['confortavel']:>10}"
              f"{c['projeto']:>9}{c['maximo']:>8}{r['unifila_un']:>9}")

    for r in res:
        print(f"\n   {r['orientacao']} — blocos (3 por porta):")
        for b in r["por_bloco"]:
            print(f"     {b['nome']}  {b['canais']:>2} canais de {b['larg_m'] if r['orientacao']=='L-O' else b['prof_m']:>5.1f} m"
                  f" | {b['metros_canal']:>4} m de canal | {b['cap_projeto']:>4} pessoas")

    print("\n\nATÉ ONDE VALE EMPURRAR A LINHA DIVISÓRIA (orientação N-S)\n")
    print(f"{'linha y':>9}{'área m²':>9}{'projeto':>9}{'máximo':>8}   "
          f"{'parede p/ 28 MRV':>17}{'passo':>8}{'vão':>8}  {'paredes':<9}{'ilhas':>9}")
    curva = []
    for y in (16, 18, 20, 22.25, 24, 26, 28):
        r = resume(layout_ns(y_div=y))
        p = parede_para_secoes(y)
        flag = "ok" if p["vao_livre_m"] >= 1.8 else ("apertado" if p["vao_livre_m"] >= 1.4 else "inviável")
        ilha = "ok" if p["ilhas_cabem"] else "não cabe"
        print(f"{y:>9.2f}{r['area_m2']:>9}{r['capacidade']['projeto']:>9}"
              f"{r['capacidade']['maximo']:>8}   {p['parede_m']:>17}"
              f"{p['passo_por_urna_m']:>8}{p['vao_livre_m']:>8}  {flag:<9}{ilha:>9}")
        curva.append({"y_div": y, "area_m2": r["area_m2"],
                      "cap_projeto": r["capacidade"]["projeto"],
                      "cap_maximo": r["capacidade"]["maximo"], **p})
    saida["curva_linha_divisoria"] = curva

    teto = res[0]["capacidade"]["projeto"]
    print(f"\n\nCONDIÇÃO DE VIABILIDADE — teto de {teto} pessoas em fila\n")
    print(f"{'urnas':>7}{'perfil base':>16}{'pico de manhã':>18}")
    viab = []
    for n in (28, 32, 36, 38, 40):
        a = t_servico_maximo(urnas, teto, "base", n_urnas=n)
        b = t_servico_maximo(urnas, teto, "pico_manha", n_urnas=n)
        fa = f"{a} s" if a else "nenhum"
        fb = f"{b} s" if b else "nenhum"
        print(f"{n:>7}{fa:>16}{fb:>18}")
        viab.append({"urnas": n, "t_max_base_s": a, "t_max_pico_s": b})
    saida["viabilidade"] = viab
    saida["teto_projeto"] = teto

    print("\n\nOCUPAÇÃO TOTAL DO RECINTO NO PICO\n")
    for nome, fila in (("projeto", res[0]["capacidade"]["projeto"]),
                       ("máximo", res[0]["capacidade"]["maximo"])):
        equipe = 28 * 3 + 28 * 2 + 22 + 20 + 28   # mesários, fiscais, fluxo, segurança, votando
        tot = fila + equipe
        print(f"   {nome:<9} fila {fila:>5} + {equipe} de operação = {tot:>5} pessoas "
              f"({100*tot/CAP_RECINTO:.0f}% da capacidade de {CAP_RECINTO} da ficha do RDS)")
        saida[f"ocupacao_{nome}"] = {"fila": fila, "operacao": equipe, "total": tot}

    print("\n\nFRONTEIRA DE VIABILIDADE — urnas competem por piso com a fila\n")
    print("   mesas em ilha; linha divisória empurrada até onde o piso de votação permite\n")
    print(f"{'urnas':>6}{'y_div máx':>11}{'fila cabe':>11}   " +
          "".join(f"{t:>6}s" for t in (45, 60, 75, 90)))
    front = []
    for n in (28, 32, 36, 38, 40):
        y_max = min(HALL_P - 2 * MARGEM,
                    HALL_P - n * MOD_ILHA * FATOR_CIRC / HALL_L)
        cap = resume(layout_ns(y_div=y_max))["capacidade"]["projeto"]
        cels, linha = [], []
        for t in (45, 60, 75, 90):
            pico = simula(urnas, t, "pico_manha", n_urnas=n)["pico_total"]
            ok = pico <= cap
            cels.append(f"{'sim' if ok else 'NÃO':>7}")
            linha.append({"t_servico": t, "pico": round(pico), "cabe": ok})
        print(f"{n:>6}{y_max:>11.1f}{cap:>11}   " + "".join(cels))
        front.append({"urnas": n, "y_div_max": round(y_max, 1),
                      "capacidade_fila": cap, "cenarios": linha})
    saida["fronteira"] = front

    print("\n\nTETO TEÓRICO: MESMA ZONA COMO CURRAL, SEM CANAIS\n")
    area_zona = res[0]["area_m2"] + sum(
        b.get("gap_m", 0) for b in layout_ns()["blocos"][:-1]) * (Y_CENTRO - APRON)
    for nome, dens in (("projeto 1,5 p/m²", 1.5), ("máximo 2,0 p/m²", 2.0)):
        print(f"   {nome:<18} {round(area_zona * dens):>5} pessoas  "
              f"(+{100*(area_zona*dens)/res[0]['capacidade']['projeto' if dens==1.5 else 'maximo']-100:.0f}% "
              f"sobre a serpentina, ao custo de perder a ordem de chegada)")
    saida["curral"] = {"area_m2": round(area_zona),
                       "cap_1_5": round(area_zona * 1.5),
                       "cap_2_0": round(area_zona * 2.0)}

    json.dump(saida, open(os.path.join(BASE, "saidas", "serpentina_hall2.json"), "w"),
              ensure_ascii=False, indent=2)
    print("\n-> saidas/serpentina_hall2.json")
