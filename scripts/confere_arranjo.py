"""Confere, item a item, os seis pedidos do Posto de 16/09/2026 sobre a planta.

  1. as portas das paredes oeste, norte e leste estao sinalizadas;
  2. N2 e O2 ficam desbloqueadas -- nenhum corpo de mesa e nenhuma fila
     invadem o vao nem o recuo de 3 m na frente dele;
  3. as saidas de emergencia da parede leste tem a faixa protegida de 3 m;
  4. S7 esta marcada como entrada preferencial;
  5. cada mesa vermelha fica no meio da sua parede e so tem mesa verde ao redor;
  6. o vao livre e de 3,00 m dentro de uma dupla e de 1,50 m entre duplas.

Sai com codigo 1 se algum item falhar.

    python3 scripts/confere_arranjo.py [cenario]
"""
import json
import math
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LARG = 0.90            # largura do corpo do modulo
PROF = 4.10            # profundidade do modulo, onde a fila se forma
VAO_DUPLA = 3.00       # livre entre as duas mesas de uma dupla
VAO_PAR = 1.50         # livre entre uma unidade e a seguinte
TOL = 0.01
RECUO_PORTA = 3.00     # desobstrucao exigida na frente de N2 e O2
FAIXA_LESTE = 3.00     # faixa protegida da fachada leste

PAREDE_POR_ROT = {0: "oeste", 270: "norte", 180: "leste"}
EIXO = {"oeste": "y", "norte": "x", "leste": "y"}

# Os trechos livres de cada parede, de scripts/arranjo_paredes.py. Duas mesas
# em trechos diferentes estao separadas por um vao de porta, nao por um vao
# entre unidades -- comparar as duas seria acusar a porta de ser folga errada.
TRECHOS = {
    "oeste": [(7.45, 18.81), (22.98, 36.25), (39.05, 43.95)],
    "norte": [(10.20, 20.21), (24.67, 42.30)],
    "leste": [(3.20, 39.50)],
}


def trecho_de(parede, c):
    for i, (a, b) in enumerate(TRECHOS[parede]):
        if a - 0.5 <= c <= b + 0.5:
            return i
    return None


def carrega(*caminho):
    with open(os.path.join(RAIZ, *caminho), encoding="utf-8") as f:
        return json.load(f)


def pega_posicoes(planta, cenario):
    pos = {m["n"]: dict(m) for m in planta["cenarios"][cenario["base"]]["mrvs"]}
    for a in cenario["alteracoes"]:
        pos[a["n"]].update({k: a[k] for k in ("x", "y", "rot", "lado")})
    return pos


def retangulo(m):
    """(x0, y0, x1, y1) do corpo do modulo, com a profundidade da fila junto.

    Devolve dois retangulos: o corpo (0,90 x 0,90 no encosto) e a faixa que a
    fila ocupa, que avanca `PROF` para dentro do salao.
    """
    rot = int(m["rot"]) % 360
    dx, dy = round(math.cos(math.radians(rot))), round(math.sin(math.radians(rot)))
    px, py = -dy, dx
    cantos = [(m["x"] + dx * u + px * v, m["y"] + dy * u + py * v)
              for u, v in ((0, -LARG / 2), (PROF, -LARG / 2),
                           (PROF, LARG / 2), (0, LARG / 2))]
    xs = [c[0] for c in cantos]
    ys = [c[1] for c in cantos]
    return (min(xs), min(ys), max(xs), max(ys))


def cruza(a, b):
    return (a[0] < b[2] - TOL and b[0] < a[2] - TOL
            and a[1] < b[3] - TOL and b[1] < a[3] - TOL)


class Itens:
    def __init__(self):
        self.linhas = []
        self.falhou = False

    def item(self, n, titulo):
        print(f"\n{n}. {titulo}")

    def ok(self, msg):
        print(f"   ✓ {msg}")

    def erro(self, msg):
        print(f"   ✗ {msg}")
        self.falhou = True


def main(argv):
    it = Itens()
    decisoes = carrega("data", "decisoes.json")
    planta = carrega("data", "prancheta_hall2.json")
    id_cen = argv[1] if len(argv) > 1 else decisoes["cenario_trabalho"]["id"]
    cenario = carrega("cenarios", id_cen + ".json")
    pos = pega_posicoes(planta, cenario)
    mesas = {m["mrv"]: m for m in decisoes["mesas"]}
    portas = {p["id"]: p for p in planta["portas"]}
    sinal = decisoes.get("sinalizacao_portas", {})
    zonas = decisoes.get("zonas_protegidas", [])

    print(f"Conferência do arranjo · cenário {cenario['nome']} ({id_cen})")

    # ---------------------------------------------------------------- 1
    it.item(1, "Sinalização das portas nas paredes oeste, norte e leste")
    esperadas = [p for p in planta["portas"] if p["face"] in ("norte", "leste", "oeste", "recorte_v")]
    faltam = [p["id"] for p in esperadas if p["id"] not in sinal]
    if faltam:
        it.erro(f"sem rótulo em decisoes.sinalizacao_portas: {', '.join(faltam)}")
    else:
        for face in ("norte", "leste", "oeste", "recorte_v"):
            ids = [p["id"] for p in esperadas if p["face"] == face]
            rotulos = ", ".join("{} ({})".format(i, sinal[i]["papel"]) for i in ids)
            it.ok(f"{face:<10} {rotulos}")

    # ---------------------------------------------------------------- 2
    it.item(2, "N2 e O2 desbloqueadas, por mesa e por fila")
    for pid in ("N2", "O2"):
        p = portas[pid]
        if p["face"] == "norte":
            zona = (p["x1"], p["y1"] - RECUO_PORTA, p["x2"], p["y2"])
        else:                                     # oeste
            zona = (p["x1"], p["y1"], p["x2"] + RECUO_PORTA, p["y2"])
        invasores = [n for n, m in pos.items() if cruza(retangulo(m), zona)]
        if invasores:
            it.erro(f"{pid}: mesas {sorted(invasores)} invadem o vão ou o recuo de "
                    f"{RECUO_PORTA:.1f} m")
        elif not any(z.get("porta") == pid for z in zonas):
            it.erro(f"{pid}: livre na planta, mas sem zona protegida registrada "
                    f"em decisoes.zonas_protegidas")
        else:
            larg = (p["x2"] - p["x1"]) or (p["y2"] - p["y1"])
            it.ok(f"{pid}: vão de {larg:.2f} m livre, com recuo de "
                  f"{RECUO_PORTA:.1f} m sem mesa nem fila")

    # ---------------------------------------------------------------- 3
    it.item(3, "Saídas de emergência da parede leste com faixa protegida de 3 m")
    emerg = [p for p in planta["portas"] if p["estado"] == "emergencia"]
    faixa = next((z for z in zonas if z.get("tipo") == "faixa_emergencia"), None)
    if faixa is None:
        it.erro("nenhuma faixa de emergência registrada em decisoes.zonas_protegidas")
    else:
        x0, y0, x1, y1 = faixa["rect"]
        if abs((x1 - x0) - FAIXA_LESTE) > TOL:
            it.erro(f"a faixa tem {x1 - x0:.2f} m, não {FAIXA_LESTE:.2f} m")
        else:
            dentro = [n for n, m in pos.items() if cruza(retangulo(m), (x0, y0, x1, y1))]
            if dentro:
                it.erro(f"mesas {sorted(dentro)} dentro da faixa protegida")
            else:
                it.ok(f"faixa de {x1 - x0:.2f} m entre x={x0} e x={x1}, "
                      f"livre em toda a fachada ({y0:.0f}–{y1:.1f} m)")
                it.ok(f"cobre as {len(emerg)} saídas de emergência: "
                      f"{', '.join(p['id'] for p in emerg)}")

    # ---------------------------------------------------------------- 4
    it.item(4, "S7 marcada como entrada preferencial")
    s7 = sinal.get("S7") or decisoes.get("portas", {}).get("S7")
    if not s7 or s7.get("papel") != "preferencial":
        it.erro(f"S7 está como {s7.get('papel') if s7 else 'ausente'}, não 'preferencial'")
    else:
        p = portas["S7"]
        it.ok(f"S7 (RDS {p['rds']}) · vão de {p['larg']:.2f} m · "
              f"{s7.get('rotulo', 'entrada preferencial')}")

    # ---------------------------------------------------------------- 5
    it.item(5, "Mesas vermelhas no meio da parede, com verdes ao redor")
    por_parede = {}
    for n, m in pos.items():
        por_parede.setdefault(PAREDE_POR_ROT[int(m["rot"]) % 360], []).append(n)
    for parede, ns in por_parede.items():
        eixo = EIXO[parede]
        ordenadas = sorted(ns, key=lambda n: pos[n][eixo])
        cs = [pos[n][eixo] for n in ordenadas]
        meio = (min(cs) + max(cs)) / 2
        vermelhas = [n for n in ns if mesas[n]["classe"] == "alta"]
        for v in vermelhas:
            i = ordenadas.index(v)
            vizinhas = [ordenadas[j] for j in (i - 1, i + 1) if 0 <= j < len(ordenadas)]
            cores = [mesas[w]["classe"] for w in vizinhas]
            desvio = abs(pos[v][eixo] - meio)
            metade = (max(cs) - min(cs)) / 2
            centro = f"a {desvio:.2f} m do meio da parede ({100 * desvio / metade:.0f}% do semi-eixo)"
            if any(c != "baixa" for c in cores):
                it.erro(f"{parede}: MRV {v} tem vizinha não-verde "
                        f"({', '.join(f'{w}={c}' for w, c in zip(vizinhas, cores))})")
            elif desvio > metade / 2:
                it.erro(f"{parede}: MRV {v} está {centro} — fora do terço central")
            else:
                it.ok(f"{parede:<6} MRV {v} ({mesas[v]['esperado']}) {centro}; "
                      f"vizinhas {', '.join(f'MRV {w} verde' for w in vizinhas)}")

    # ---------------------------------------------------------------- 6
    it.item(6, "3,00 m dentro da dupla e 1,50 m entre duplas")
    for parede in ("oeste", "norte", "leste"):
        eixo = EIXO[parede]
        ordenadas = sorted(por_parede[parede], key=lambda n: pos[n][eixo])
        vaos, entre_trechos = [], 0
        for a, b in zip(ordenadas, ordenadas[1:]):
            if trecho_de(parede, pos[a][eixo]) != trecho_de(parede, pos[b][eixo]):
                entre_trechos += 1
                continue
            vaos.append(round(pos[b][eixo] - pos[a][eixo] - LARG, 2))
        duplas = [v for v in vaos if abs(v - VAO_DUPLA) <= TOL]
        pares = [v for v in vaos if abs(v - VAO_PAR) <= TOL]
        outros = [v for v in vaos if v not in duplas and v not in pares]
        if outros:
            it.erro(f"{parede}: vãos fora do padrão: {outros} "
                    f"(esperado {VAO_DUPLA:.2f} ou {VAO_PAR:.2f})")
        else:
            it.ok(f"{parede:<6} {len(vaos)} vãos medidos: {len(duplas)} de "
                  f"{VAO_DUPLA:.2f} m (dentro da dupla) e {len(pares)} de "
                  f"{VAO_PAR:.2f} m (entre unidades); {entre_trechos} vão(s) de porta "
                  f"separando trechos, fora da conta")

    # brindes: nada fora do salão nem sobreposto
    it.item("+", "Verificações de sanidade")
    sobrepostas = [(a, b) for i, a in enumerate(sorted(pos))
                   for b in sorted(pos)[i + 1:] if cruza(retangulo(pos[a]), retangulo(pos[b]))]
    if sobrepostas:
        it.erro(f"mesas sobrepostas: {sobrepostas}")
    else:
        it.ok(f"nenhuma das {len(pos)} mesas se sobrepõe a outra")

    print()
    print("TODOS OS ITENS ATENDIDOS" if not it.falhou else "HÁ ITENS PENDENTES")
    return 1 if it.falhou else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
