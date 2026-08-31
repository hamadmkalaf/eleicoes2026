"""Ideia 1 — as 28 MRVs em tres fileiras de ilhas no meio do salao.

Com o recuo de 3 m em torno de cada saida de emergencia e o modulo real de
2,80 m de frente, o perimetro do Hall 2 comporta 11 das 28 posicoes (a parede
leste some por inteiro: cada trecho livre entre as saidas 2.16 a 2.23 mede
2,79 m). Como o sigilo do voto vem da estrutura que fecha o fundo e os lados da
urna, e nao da parede, este layout tira as MRVs das paredes.

Tres fileiras leste-oeste, todas com os modulos de frente para o sul. O eleitor
entra na baia pelo corredor de distribuicao ao sul, vota, e sai pelo fundo do
modulo no corredor de retorno ao norte, que corre para a espinha central. Cada
fileira e partida ao meio pela espinha, o que separa as duas zonas.

A geometria, as premissas e a simulacao de fila vivem em salao.py.
Gera saidas/ideia1_dados.json.
"""
import json, math, os

from salao import (RAIZ, ABERTURA, FECHAMENTO, PERFIL, SEG_POR_VOTO,
                   TAXA_DUBLIN, TAXA_INTERIOR, AREA_PESSOA, FOLGA_BAIA,
                   LARG_MIN_BAIA, MOD_LARGURA, MOD_PROFUND, RECUO_EMERGENCIA,
                   HALL_W, HALL_H, RECORTE, PORTAS, ENTRADA_A, ENTRADA_B,
                   ENTRADA_ZONA, SAIDA, carrega_urnas, simula_fila,
                   largura_exigida, classe)

ESPINHA = dict(x0=26.0, x1=31.0, y0=0.0, y1=44.4)   # canal de saida, sul-norte

# Faixas leste-oeste do salao, do sul para o norte (y inicial, y final, uso).
# A soma fecha os 44,4 m de profundidade util.
FAIXAS = [
    (0.0,  4.7,  "avental sul e corredor de distribuicao 3"),
    (4.7,  8.2,  "baias da fileira 3"),
    (8.2, 10.1,  "fileira 3 — modulos"),
    (10.1, 12.6, "retorno 3"),
    (12.6, 16.1, "corredor de distribuicao 2"),
    (16.1, 19.6, "baias da fileira 2"),
    (19.6, 21.5, "fileira 2 — modulos"),
    (21.5, 24.0, "retorno 2"),
    (24.0, 27.5, "corredor de distribuicao 1"),
    (27.5, 39.5, "baias da fileira 1"),
    (39.5, 41.4, "fileira 1 — modulos"),
    (41.4, 44.4, "retorno 1 (faixa livre da parede norte)"),
]
AVENIDA_O = (3.0, 6.0)     # avenida de entrada da zona A, sentido sul-norte
AVENIDA_L = (45.0, 47.5)   # avenida de entrada da zona B

# profundidade maxima de baia de fila por parede (m)
# As 28 posicoes ficam em ilhas, nao contra as paredes: com o recuo de 3 m das
# saidas de emergencia e o modulo real de 2,80 m, so 11 posicoes caberiam no
# perimetro (a parede leste some por inteiro — todo trecho livre entre as
# saidas 2.16 a 2.23 tem 2,79 m). O sigilo do voto vem da estrutura que fecha o
# fundo e os lados da urna, nao da parede, entao a ilha e legitima.
#
# Tres fileiras leste-oeste, todas com os modulos de frente para o sul: o
# eleitor chega pelo corredor de distribuicao ao sul, entra na baia da sua
# urna, vota e sai pelo fundo do modulo no corredor de retorno ao norte. Cada
# fileira e partida ao meio pela espinha de saida, o que separa as duas zonas.
#
# (id, y da face sul do modulo, x inicial, x final, profundidade da baia,
#  n_slots, zona)
FILEIRAS = [
    ("F1c", 39.5,  3.0, 19.5, 12.0, 3, "A"),   # setor reforcado
    ("F1A", 39.5, 19.5, 26.0, 12.0, 2, "A"),
    ("F1B", 39.5, 31.0, 45.0, 12.0, 4, "B"),
    ("F2A", 19.6,  6.0, 26.0,  3.5, 6, "A"),
    ("F2B", 19.6, 31.0, 45.0,  3.5, 4, "B"),
    # a fileira 3 comeca em x = 7,8: abaixo de y = 7 o salao tem o canto
    # sudoeste recortado, e a baia nao pode invadi-lo
    ("F3A",  8.2,  7.8, 26.0,  3.5, 5, "A"),
    ("F3B",  8.2, 31.0, 45.0,  3.5, 4, "B"),
]


def constroi_slots():
    """Expande as fileiras em 28 posicoes. Cada posicao guarda o centro do
    modulo, a largura de fileira que lhe cabe, a profundidade disponivel para a
    baia de fila e a distancia ate a porta da sua zona."""
    slots = []
    for fid, y, x0, x1, prof, n, zona in FILEIRAS:
        larg = (x1 - x0) / n
        for i in range(n):
            x = x0 + (i + 0.5) * larg
            ex, ey = ENTRADA_ZONA[zona]
            slots.append({
                "fileira": fid, "zona": zona,
                "x": round(x, 2), "y": y,
                "larg_disponivel": round(larg, 2),
                "prof_max": prof,
                "dist_entrada": round(math.hypot(x - ex, y - ey), 1),
            })
    return slots


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
                       if u["fila_pico"] >= 40],
                      key=lambda u: -u["esperado"])
    nl = [s for s in por_zona["A"] if s["fileira"] == "F1c"]
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
    alvo = sum(u["esperado"] for u in urnas) / 2
    for u in sorted([u for u in urnas if u["urna"] not in fixo],
                    key=lambda u: -u["esperado"]):
        cand = [z for z in "AB" if len(zonas[z]) < len(livres[z])
                and teto[z] >= u["fila_pico"]]
        if not cand:
            cand = [z for z in "AB" if len(zonas[z]) < len(livres[z])]
        # a zona escolhida e a que tem maior deficit por vaga restante: como as
        # duas zonas tem numeros diferentes de posicoes, distribuir pelo total
        # corrente favoreceria a zona maior e desequilibraria o resultado
        z = max(cand, key=lambda z: ((alvo - total[z])
                                     / (len(livres[z]) - len(zonas[z])), z))
        zonas[z].append(u)
        total[z] += u["esperado"]

    saida = [monta(u, fixo[u["urna"]]) for u in criticas]
    for z in "AB":
        ordenadas = sorted(zonas[z], key=lambda u: (u["fila_pico"], u["esperado"]))
        for slot, u in zip(livres[z], ordenadas):
            saida.append(monta(u, slot))
    return saida, total


def monta(u, slot):
    """Dimensiona a baia de fila da urna dentro da largura que lhe cabe."""
    prof_max = slot["prof_max"]
    larg = min(largura_exigida(u["fila_pico"], prof_max), slot["larg_disponivel"])
    util = max(larg - FOLGA_BAIA, 1.0)
    area = max(u["fila_pico"], 4) * AREA_PESSOA
    prof = max(2.5, min(area / util, prof_max))
    cap = int(util * prof / AREA_PESSOA)
    return {**u, **slot,
            "baia_largura": round(larg, 2),
            "baia_profundidade": round(prof, 1),
            "baia_capacidade": cap,
            "baia_suficiente": cap >= u["fila_pico"],
            "mesarios": 4 if u["fila_pico"] >= 40 else 3}


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
        "faixas": FAIXAS,
        "fileiras": FILEIRAS,
        "avenidas": {"oeste": AVENIDA_O, "leste": AVENIDA_L},
        "modulo": {"largura_m": MOD_LARGURA, "profundidade_m": MOD_PROFUND,
                   "mesa_mesarios_m": [1.60, 0.70], "mesa_urna_diametro_m": 0.90},
        "recuo_emergencia_m": RECUO_EMERGENCIA,
        "papeis_portas": {
            "carga oeste": "ENTRADA A — porta de carga oeste (3,62 m)",
            "carga leste": "ENTRADA B — porta de carga leste (3,63 m)",
            "2.4":     "SAIDA principal — baia central (5,93 m)",
            "2.5/2.6": "Saida de reforco no pico; fora disso, emergencia",
            "2.2/2.3": "Saida de reforco no pico; fora disso, emergencia",
            "2.7":     "Somente emergencia",
            "2.1":     "Somente emergencia",
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
    cam = os.path.join(RAIZ, "saidas", "ideia1_dados.json")
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
    print(f"\n{'zn':>2} {'fila':>6} {'urna':>6} {'classe':>8} {'apt':>5} {'esp':>5} "
          f"{'fila':>4} {'dist':>5} {'baia (l x p)':>13} {'cap':>4} {'mes':>3} {'fecha':>5}")
    for m in mrvs:
        print(f"{m['zona']:>2} {m['fileira']:>6} {m['urna']:>6} {m['classe']:>8} "
              f"{m['aptos']:>5} {m['esperado']:>5} {m['fila_pico']:>4} "
              f"{m['dist_entrada']:>5} {m['baia_largura']:>5.1f} x{m['baia_profundidade']:>5.1f} "
              f"{m['baia_capacidade']:>4} {m['mesarios']:>3} {m['encerramento']:>5.1f}")


if __name__ == "__main__":
    main()
