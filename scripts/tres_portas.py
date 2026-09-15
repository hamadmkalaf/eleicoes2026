# -*- coding: utf-8 -*-
"""
Serpentina para a prancheta 'Hamad_Final': entradas S4 (A), S5 (B), S6 (C);
saídas S2 e S8; mesas onde estão. Zona de fila da fachada sul até o centro.

Regras do pedido:
  1) máximo de pessoas, mantendo circulação;
  2) blocos organizados por porta, em múltiplos de 3 (3, 6 ou 9);
  3) cada porta com a MESMA capacidade.

Método: canais norte-sul de 1,10 m; busca exaustiva da repartição de canais
entre os blocos; a igualdade por porta é obtida recuando a entrada (sul) do
último bloco de cada porta até que as três portas tenham os mesmos metros.
"""
import json, os, math, itertools
from filas_sem_ring3 import LARG_CANAL, COMP_UNIFILA
from serpentina_hall2 import HALL_L, HALL_P, NOTCH_X, NOTCH_Y, Y_CENTRO, PASSOS, PERDA_CURVA

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FAIXA = 7.0          # faixa perimetral das mesas (oeste e leste)
APRON = 4.0          # triagem e distribuição junto à fachada sul
GAP = 1.2            # corredor entre blocos
SAIDA_L = 3.0        # corredor de saída para S2
PROF_MIN = 6.0       # bloco não pode ficar mais raso que isto
MIN_CANAIS = 3       # menos que isso não é serpentina, é corredor

FRAC = {"S1": .039, "S2": .137, "S3": .234, "S4": .335, "S5": .481,
        "S6": .628, "S7": .727, "S8": .827, "S9": .924}
PORTAS = {k: round(NOTCH_X + f * (HALL_L - NOTCH_X), 1) for k, f in FRAC.items()}
ENTRADAS = {"A": PORTAS["S4"], "B": PORTAS["S5"], "C": PORTAS["S6"]}


def regioes(y_div=Y_CENTRO, s2_aberta=True):
    """Duas regiões de canais: oeste do corredor S2 (mais rasa, porque a
    saída passa por cima do recorte) e leste dele."""
    xw0 = FAIXA
    if s2_aberta:
        xv0, xv1 = PORTAS["S2"] - SAIDA_L / 2, PORTAS["S2"] + SAIDA_L / 2
        oeste = {"x0": xw0, "x1": xv0, "y0": NOTCH_Y + SAIDA_L}
        leste = {"x0": xv1, "x1": HALL_L - FAIXA, "y0": APRON}
    else:
        # S2 fechada: a saída oeste vai pelo norte até S8/S7; a região oeste
        # ganha profundidade, só o recorte limita
        oeste = {"x0": xw0, "x1": NOTCH_X, "y0": NOTCH_Y}
        leste = {"x0": NOTCH_X, "x1": HALL_L - FAIXA, "y0": APRON}
    for r in (oeste, leste):
        r["prof"] = y_div - r["y0"]
        r["largura"] = r["x1"] - r["x0"]
    return oeste, leste


def canais_em(largura, n_blocos):
    """Canais que cabem numa largura com n_blocos e (n-1) corredores."""
    return int((largura - (n_blocos - 1) * GAP) / LARG_CANAL + 1e-9)


def melhor(k, y_div=Y_CENTRO, s2_aberta=True, usar_oeste=True):
    """k blocos por porta. Devolve a melhor repartição balanceada."""
    oeste, leste = regioes(y_div, s2_aberta)
    melhor_sol = None
    # opção 1: a região oeste é um bloco só, da porta A (k >= 2), ou de A com k = 1
    # opção 2: região oeste não usada
    opcoes = []
    if usar_oeste:
        opcoes.append(True)
    opcoes.append(False)
    for com_oeste in opcoes:
        if com_oeste:
            n_oeste_blocos = 1
            m_oeste = canais_em(oeste["largura"], 1) * oeste["prof"]
            c_oeste = canais_em(oeste["largura"], 1)
        else:
            n_oeste_blocos, m_oeste, c_oeste = 0, 0.0, 0
        n_leste_blocos = 3 * k - n_oeste_blocos
        if n_leste_blocos < 2:
            continue
        total_c = canais_em(leste["largura"], n_leste_blocos)
        if total_c < n_leste_blocos:
            continue
        # composições de total_c em n_leste_blocos partes >= 1
        for cuts in itertools.combinations(range(1, total_c), n_leste_blocos - 1):
            parts = [b - a for a, b in zip((0,) + cuts, cuts + (total_c,))]
            if min(parts) < MIN_CANAIS:
                continue
            # blocos por porta: A recebe (k - n_oeste_blocos) blocos do leste
            ka = k - n_oeste_blocos
            pa, pb, pc = parts[:ka], parts[ka:ka + k], parts[ka + k:]
            mA = m_oeste + sum(pa) * leste["prof"]
            mB = sum(pb) * leste["prof"]
            mC = sum(pc) * leste["prof"]
            alvo = min(mA, mB, mC)
            # o bloco recuado não pode ficar mais raso que PROF_MIN
            ok = True
            for m, p in ((mA, pa), (mB, pb), (mC, pc)):
                exc = m - alvo
                if exc > 1e-6:
                    ult = p[-1] if p else c_oeste
                    if leste["prof"] - exc / ult < PROF_MIN:
                        ok = False
            if not ok:
                continue
            tot = 3 * alvo
            if melhor_sol is None or tot > melhor_sol["metros"] + 1e-6:
                melhor_sol = {"metros": tot, "alvo": alvo, "com_oeste": com_oeste,
                              "parts": parts, "c_oeste": c_oeste}
    if melhor_sol is None:
        return None
    # materializa os blocos
    s = melhor_sol
    blocos = []
    if s["com_oeste"]:
        blocos.append({"nome": "A1", "porta": "A", "canais": s["c_oeste"],
                       "x0": oeste["x0"], "y0": oeste["y0"], "prof": oeste["prof"],
                       "oeste": True})
    ka = k - (1 if s["com_oeste"] else 0)
    ordem = [("A", ka), ("B", k), ("C", k)]
    x = leste["x0"]
    i = 0
    for porta, kk in ordem:
        n0 = 1 if (porta == "A" and s["com_oeste"]) else 0
        for j in range(kk):
            n = s["parts"][i]; i += 1
            blocos.append({"nome": f"{porta}{j + 1 + n0}", "porta": porta,
                           "canais": n, "x0": round(x, 2), "y0": leste["y0"],
                           "prof": leste["prof"], "oeste": False})
            x += n * LARG_CANAL + GAP
    # recuo do último bloco de cada porta até o alvo
    for porta in "ABC":
        bs = [b for b in blocos if b["porta"] == porta]
        m = sum(b["canais"] * b["prof"] for b in bs)
        exc = m - s["alvo"]
        if exc > 1e-6:
            u = bs[-1]
            u["prof"] = round(u["prof"] - exc / u["canais"], 2)
            u["y0"] = round(y_div - u["prof"], 2)
            u["recuado"] = True
    for b in blocos:
        b["prof"] = round(b["prof"], 2)
        b["x0"] = round(b["x0"], 2)
        b["y0"] = round(b["y0"], 2)
        b["metros"] = round(b["canais"] * b["prof"], 1)
    return blocos


def resume(blocos):
    tot = sum(b["metros"] for b in blocos)
    curvas = sum(max(0, b["canais"] - 1) for b in blocos)
    barreira = sum((b["canais"] + 1) * b["prof"] for b in blocos)
    cap = {k: round(tot / p - curvas * PERDA_CURVA) for k, p in PASSOS.items()}
    pp = {}
    for porta in "ABC":
        bs = [b for b in blocos if b["porta"] == porta]
        m = sum(b["metros"] for b in bs)
        cv = sum(max(0, b["canais"] - 1) for b in bs)
        pp[porta] = {"blocos": len(bs), "canais": sum(b["canais"] for b in bs),
                     "metros": round(m), "projeto": round(m / PASSOS["projeto"] - cv * PERDA_CURVA),
                     "maximo": round(m / PASSOS["maximo"] - cv * PERDA_CURVA)}
    return {"blocos": len(blocos), "canais": sum(b["canais"] for b in blocos),
            "metros_canal": round(tot), "curvas": curvas, "barreira_m": round(barreira),
            "unifila_un": math.ceil(barreira / COMP_UNIFILA), "capacidade": cap,
            "por_porta": pp}


if __name__ == "__main__":
    print("portas lidas da prancheta:", PORTAS)
    print(f"entradas A={ENTRADAS['A']} · B={ENTRADAS['B']} · C={ENTRADAS['C']} | "
          f"saídas S2={PORTAS['S2']} · S8={PORTAS['S8']}\n")
    out = {"portas": PORTAS, "variantes": []}
    for s2 in (True, False):
        print("=" * 76)
        print("S2 ABERTA (saída oeste cruza a zona)" if s2 else
              "S2 FECHADA — tudo sai por S8/S7, saída oeste pelo norte")
        for k in (1, 2, 3):
            bl = melhor(k, s2_aberta=s2)
            if not bl:
                print(f"  {3*k} blocos: sem solução"); continue
            r = resume(bl)
            c = r["capacidade"]
            print(f"\n  {3*k} BLOCOS ({k} por porta): projeto {c['projeto']} · "
                  f"máximo {c['maximo']} · confortável {c['confortavel']} · "
                  f"{r['canais']} canais · {r['metros_canal']} m · {r['unifila_un']} unifilas")
            print("     por porta: " + " | ".join(
                f"{p} {v['projeto']} pessoas ({v['blocos']} bl, {v['canais']} can, {v['metros']} m)"
                for p, v in r["por_porta"].items()))
            for b in bl:
                flag = " (oeste de S2)" if b["oeste"] else (" (recuado)" if b.get("recuado") else "")
                print(f"       {b['nome']:<3} x={b['x0']:>5.1f}  {b['canais']:>2} canais × "
                      f"{b['prof']:>5.1f} m = {b['metros']:>5.0f} m{flag}")
            out["variantes"].append({"s2_aberta": s2, "k": k, "resumo": r, "blocos": bl})
    json.dump(out, open(os.path.join(BASE, "saidas", "tres_portas.json"), "w"),
              ensure_ascii=False, indent=2)
    print("\n-> saidas/tres_portas.json")
