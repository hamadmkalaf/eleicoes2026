#!/usr/bin/env python3
"""Mede as folgas de cada mesa receptora num cenario da Prancheta do Hall 2.

Para cada mesa devolve duas medidas, ambas em metros e no mesmo modelo
geometrico que a prancheta usa:

  lateral  menor espaco livre de um lado ou do outro do modulo, ao longo da
           parede — e o que separa uma mesa da vizinha;
  fila     profundidade livre a frente da mesa dos mesarios, que e onde a
           fila de eleitores se forma.

Uso:
    python3 scripts/folgas_prancheta.py                        # planta original
    python3 scripts/folgas_prancheta.py cenarios/<arquivo>.json
"""
import json, math, os, sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = json.load(open(os.path.join(RAIZ, "cenarios", "planta_hall2.json"), encoding="utf-8"))
M, SAL = D["modulo"], D["salao"]
LARG, ALT = SAL["largura"], SAL["altura"]
CAP = 20.0                     # teto das medidas: alem disso o salao esta aberto


def direcao(rot):
    return (round(math.cos(math.radians(rot))), round(math.sin(math.radians(rot))))


def perpendicular(d):
    return (-d[1], d[0])


def corpo(m):
    """Retangulo que o modulo inteiro ocupa: eleitor, urna, mesa dos mesarios."""
    d, p = direcao(m["rot"]), perpendicular(direcao(m["rot"]))
    xs, ys = [], []
    for u in (0, M["prof"]):
        for v in (-M["larg"] / 2, M["larg"] / 2):
            xs.append(m["x"] + d[0] * u + p[0] * v)
            ys.append(m["y"] + d[1] * u + p[1] * v)
    return [min(xs), min(ys), max(xs), max(ys)]


def assento(m):
    d = direcao(m["rot"])
    p = perpendicular(d)
    p = (p[0] * m["lado"], p[1] * m["lado"])
    xs, ys = [], []
    for u in (M["prof"] - M["mesa"][0], M["prof"]):
        for v in (M["mesa"][1] / 2, M["mesa"][1] / 2 + M["assento"]):
            xs.append(m["x"] + d[0] * u + p[0] * v)
            ys.append(m["y"] + d[1] * u + p[1] * v)
    return [min(xs), min(ys), max(xs), max(ys)]


def bate(a, b, t=1e-6):
    return a[0] < b[2] - t and b[0] < a[2] - t and a[1] < b[3] - t and b[1] < a[3] - t


def conflitos(m, mrvs, cen):
    r, fora = corpo(m), []
    if r[0] < -1e-6 or r[1] < -1e-6 or r[2] > LARG + 1e-6 or r[3] > ALT + 1e-6:
        fora.append("fora do salao")
    if bate(r, SAL["recorte"]):
        fora.append("fora do salao")
    for z in D["cenarios"][cen]["zonas"]:
        if bate(r, z["rect"]):
            fora.append(z["rotulo"].split(" · ")[0])
    for v in D["cenarios"][cen]["vaos"]:
        if bate(r, v["rect"]):
            fora.append("vao " + v["rotulo"].split(" ")[0])
    for o in mrvs:
        if o["n"] != m["n"] and bate(r, corpo(o)):
            fora.append("mesa %d" % o["n"])
    a = assento(m)
    for z in D["cenarios"][cen]["zonas"]:
        if bate(a, z["rect"]):
            fora.append("cadeiras em " + z["rotulo"].split(" · ")[0])
    return sorted(set(fora))


def livre(r, d, obs):
    """Distancia livre a partir do retangulo r andando na direcao d."""
    eixo, sentido = (0, d[0]) if d[0] else (1, d[1])
    lo, hi = (r[1], r[3]) if eixo == 0 else (r[0], r[2])
    melhor = CAP
    for o in obs:
        o_lo, o_hi = (o[1], o[3]) if eixo == 0 else (o[0], o[2])
        if o_lo < hi - 1e-6 and lo < o_hi - 1e-6:
            v = o[eixo] - r[eixo + 2] if sentido > 0 else r[eixo] - o[eixo + 2]
            if v >= -1e-6:
                melhor = min(melhor, max(v, 0.0))
    limite = (LARG, ALT)[eixo]
    v = limite - r[eixo + 2] if sentido > 0 else r[eixo]
    return round(min(melhor, max(v, 0.0)), 2)


def audita(mrvs, cen="A"):
    zonas = [z["rect"] for z in D["cenarios"][cen]["zonas"]]
    vaos = [v["rect"] for v in D["cenarios"][cen]["vaos"]]
    saida = {}
    for m in mrvs:
        obs = [corpo(o) for o in mrvs if o["n"] != m["n"]] + zonas + vaos + [SAL["recorte"]]
        r, d = corpo(m), direcao(m["rot"])
        p = perpendicular(d)
        saida[m["n"]] = {
            "fila": livre(r, d, obs),
            "lateral": min(livre(r, p, obs), livre(r, (-p[0], -p[1]), obs)),
            "conflito": conflitos(m, mrvs, cen),
        }
    return saida


def carrega(caminho=None):
    """Devolve (nome, cenario_base, mesas) do arquivo dado ou da planta original."""
    if not caminho:
        return "planta original", "A", [dict(m) for m in D["cenarios"]["A"]["mrvs"]]
    c = json.load(open(caminho, encoding="utf-8"))
    base = c.get("base", "A")
    mrvs = [dict(m) for m in D["cenarios"][base]["mrvs"]]
    for a in c.get("alteracoes", []):
        for m in mrvs:
            if m["n"] == a["n"]:
                m.update(a)
    return c.get("nome", os.path.basename(caminho)), base, mrvs


def main():
    caminho = sys.argv[1] if len(sys.argv) > 1 else None
    nome, base, mrvs = carrega(caminho)
    orig = audita([dict(m) for m in D["cenarios"][base]["mrvs"]], base)
    novo = audita(mrvs, base)

    ruins = {n: v["conflito"] for n, v in novo.items() if v["conflito"]}
    print("%s  (cenario base %s, %d mesas)" % (nome, base, len(mrvs)))
    print("conflitos: %s" % (ruins if ruins else "nenhum"))
    print()
    print(" mesa | lateral | fila  |  planta original")
    print("------+---------+-------+------------------")
    for n in sorted(novo):
        v, o = novo[n], orig[n]
        mudou = abs(v["lateral"] - o["lateral"]) > 0.01 or abs(v["fila"] - o["fila"]) > 0.01
        print("  %2d  |  %5.2f  | %5.2f | %s" % (
            n, v["lateral"], v["fila"],
            ("%5.2f / %5.2f" % (o["lateral"], o["fila"])) if mudou else "sem alteracao"))
    print()
    print("pior lateral: %.2f m (original %.2f) | pior fila: %.2f m (original %.2f)" % (
        min(v["lateral"] for v in novo.values()), min(v["lateral"] for v in orig.values()),
        min(v["fila"] for v in novo.values()), min(v["fila"] for v in orig.values())))
    return 1 if ruins else 0


if __name__ == "__main__":
    sys.exit(main())
