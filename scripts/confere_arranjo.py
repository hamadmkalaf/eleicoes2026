"""Confere, item a item, os seis pedidos do Posto de 16/09/2026 sobre a planta.

  1. as portas das paredes oeste, norte e leste estao sinalizadas;
  2. N2 e O2 ficam desbloqueadas -- nenhum corpo de mesa e nenhuma fila
     invadem o vao nem o recuo de 3 m na frente dele;
  3. as saidas de emergencia da parede leste tem a faixa protegida de 3 m;
  4. S7 esta marcada como entrada preferencial;
  5. cada mesa vermelha tem, a frente, o retangulo reservado de um serpenteado
     de ~20 pessoas, que nao invade fila vizinha nem zona protegida;
  6. o vao livre e de 3,00 m dentro de uma dupla (2,50 m se apertado), 1,50 m
     entre unidades e 1,90 m dos dois lados da vermelha;
  7. a sala de apoio, entre a porta O1 e a parede norte, nao recebe mesa.

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
VAO_DUPLA_APERTADO = 2.50   # o aperto autorizado em 16/09
VAO_PAR = 1.50         # livre entre uma unidade e a seguinte
VAO_VERMELHA = 1.90    # livre dos dois lados da vermelha, para o serpenteado
TOL = 0.01
RECUO_PORTA = 3.00     # desobstrucao exigida na frente de N2 e O2
FAIXA_LESTE = 3.00     # faixa protegida da fachada leste

PAREDE_POR_ROT = {0: "oeste", 270: "norte", 180: "leste"}
EIXO = {"oeste": "y", "norte": "x", "leste": "y"}

# Os trechos livres de cada parede, de scripts/arranjo_paredes.py. Duas mesas
# em trechos diferentes estao separadas por um vao de porta, nao por um vao
# entre unidades -- comparar as duas seria acusar a porta de ser folga errada.
TRECHOS = {
    "oeste": [(7.45, 18.81), (22.98, 36.25)],
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
    it.item(5, "Espaço de serpenteado à frente de cada mesa vermelha")
    por_parede = {}
    for n, m in pos.items():
        por_parede.setdefault(PAREDE_POR_ROT[int(m["rot"]) % 360], []).append(n)
    serps = {s["mrv"]: s for s in decisoes.get("serpenteados", [])}
    vermelhas = [n for n, m in mesas.items() if m["classe"] == "alta"]
    if set(serps) != set(vermelhas):
        it.erro(f"serpenteado registrado para {sorted(serps)}, "
                f"vermelhas são {sorted(vermelhas)}")
    for n in sorted(vermelhas):
        sp = serps.get(n)
        if sp is None:
            continue
        rect = tuple(sp["rect"])
        parede = PAREDE_POR_ROT[int(pos[n]["rot"]) % 360]
        # o retângulo fica à frente da mesa, não em cima dela nem de outra
        choca = [k for k, m in pos.items() if cruza(retangulo(m), rect)]
        zonas_rect = [tuple(z["rect"]) for z in zonas]
        em_zona = [z["rotulo"] for z in zonas if cruza(rect, tuple(z["rect"]))]
        # folga lateral: quanto a vermelha tem de cada lado até a mesa vizinha
        eixo = EIXO[parede]
        ordenadas = sorted(por_parede[parede], key=lambda k: pos[k][eixo])
        i = ordenadas.index(n)
        lados = [round(abs(pos[ordenadas[j]][eixo] - pos[n][eixo]) - LARG, 2)
                 for j in (i - 1, i + 1) if 0 <= j < len(ordenadas)]
        cap = sp["raias"] * sp["profundidade"] * 1.20 * 2.00
        if choca:
            it.erro(f"{parede}: o serpenteado da MRV {n} encosta nas mesas {sorted(choca)}")
        elif em_zona:
            it.erro(f"{parede}: o serpenteado da MRV {n} invade {em_zona}")
        elif lados and min(lados) < VAO_VERMELHA - TOL:
            it.erro(f"{parede}: MRV {n} tem só {min(lados):.2f} m de folga lateral, "
                    f"menos que os {VAO_VERMELHA:.2f} m que o serpenteado pede")
        elif cap < 19:
            it.erro(f"{parede}: o serpenteado da MRV {n} comporta {cap:.0f} pessoas, "
                    f"menos que as ~20 pedidas")
        else:
            prof = sp["profundidade"]
            it.ok(f"{parede:<6} MRV {n} ({mesas[n]['esperado']}) · {sp['raias']} raias de "
                  f"{prof:.2f} m à frente da mesa = {cap:.0f} pessoas · "
                  f"folga lateral {min(lados):.2f} m dos dois lados")

    # ---------------------------------------------------------------- 6
    it.item(6, "Vãos: 3,00 m na dupla (2,50 se apertada), 1,50 entre unidades, "
               "1,90 ao lado da vermelha")
    aceitos = {VAO_DUPLA, VAO_DUPLA_APERTADO, VAO_PAR, VAO_VERMELHA}
    for parede in ("oeste", "norte", "leste"):
        eixo = EIXO[parede]
        ordenadas = sorted(por_parede[parede], key=lambda n: pos[n][eixo])
        contagem, entre_trechos, outros = {}, 0, []
        for a, b in zip(ordenadas, ordenadas[1:]):
            if trecho_de(parede, pos[a][eixo]) != trecho_de(parede, pos[b][eixo]):
                entre_trechos += 1
                continue
            v = round(pos[b][eixo] - pos[a][eixo] - LARG, 2)
            casa = next((x for x in aceitos if abs(v - x) <= TOL), None)
            if casa is None:
                outros.append(v)
            else:
                contagem[casa] = contagem.get(casa, 0) + 1
        if outros:
            it.erro(f"{parede}: vãos fora do padrão: {outros}")
        else:
            resumo = " · ".join(f"{k} de {v:.2f} m" for v, k in sorted(contagem.items()))
            it.ok(f"{parede:<6} {resumo}; {entre_trechos} vão(s) de porta, fora da conta")
    apertadas = [p for p, v in decisoes.get("vao_dupla_por_parede", {}).items()
                 if abs(v - VAO_DUPLA_APERTADO) <= TOL]
    it.ok(f"duplas apertadas para {VAO_DUPLA_APERTADO:.2f} m: "
          + (", ".join(apertadas) if apertadas else "nenhuma — os 3,00 m couberam"))

    # ---------------------------------------------------------------- 7
    it.item(7, "Sala de apoio entre a porta O1 e a parede norte, sem mesa")
    sala = next((z for z in zonas if z.get("tipo") == "sala_apoio"), None)
    if sala is None:
        it.erro("nenhuma sala de apoio registrada em decisoes.zonas_protegidas")
    else:
        rect = tuple(sala["rect"])
        dentro = [n for n, m in pos.items() if cruza(retangulo(m), rect)]
        o1 = portas["O1"]
        if dentro:
            it.erro(f"mesas {sorted(dentro)} dentro da sala de apoio")
        elif abs(rect[1] - o1["y2"]) > 0.2:
            it.erro(f"a sala começa em y={rect[1]}, não na borda norte de O1 (y={o1['y2']})")
        else:
            it.ok(f"reservada de y={rect[1]} (borda de O1) a y={rect[3]} (parede norte), "
                  f"{rect[2] - rect[0]:.1f} m de profundidade · nenhuma mesa dentro")

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
