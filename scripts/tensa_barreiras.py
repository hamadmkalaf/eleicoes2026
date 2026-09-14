"""Quantos separadores Tensa o Hall 2 consome, nos quatro tracados de 13/09.

Le o cenario de trabalho da Prancheta (scripts/decisoes.py: posicoes das 28
mesas, entradas, classes, numeracao eleitor) e os quatro tracados registrados
na decisao D4 de scripts/decisoes_abertas.py, e converte geometria em postes
e fitas. Nada e digitado a mao: mudar o cenario de trabalho (decisoes.py) ou
um tracado (decisoes_abertas.py) muda a conta.

REGRA DE MESA (Posto, 13/09/2026), igual nos quatro tracados:
  - par de mesas que se encaram: UMA linha de 4 m no meio do corredor;
  - mesa vermelha (classe alta, os "polos"): 10 m de unifila, do seu lado;
  - mesa nao vermelha sem par: SEM unifila (fica com placa e orientador).

TRACADOS (decisao D4; o vigente e o que o Posto vai montar):
  1e  duas divisorias de 20 m entre os canais A|B e B|C, ate o checkpoint,
      mais 6 bochechas de portao (2 por canal);
  1f  "desenho em T": o canal B isolado por duas linhas de 15 m; no metro 15,
      um braco perpendicular para oeste guia a fila A e um para leste guia a
      fila C (braco de 6 m, premissa); 2 bochechas no portao do canal B;
  1g  o T com o canal B de 10 m (bracos de 6 m);
  1h  o T com o canal B de 5 m e bracos de 3 m.

Convencao de contagem, valida para o poste Tensa de fita retratil de 2,00 m:
uma corrida de L metros gasta ceil(L/2) fitas e ceil(L/2)+1 postes -- o poste
a mais e o de ponta, que fecha a corrida. Corridas independentes nao
compartilham poste. Cada lado do T e UMA corrida continua (o canto e um poste
com duas fitas), de comprimento canal + braco.

Uso: python3 scripts/tensa_barreiras.py   (depois de gera_decisoes.py e
decisoes_abertas.py; grava saidas/tensa_barreiras.json; a planta e o
registro em markdown saem de scripts/gera_barreiras_hall2.py)
"""
import datetime
import json
import math
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, AQUI)

import decisoes as DC                                         # noqa: E402
import decisoes_abertas as DA                                 # noqa: E402

ARQUIVO = os.path.join(RAIZ, "saidas", "tensa_barreiras.json")

FITA = 2.00          # m de fita por poste Tensa
LARG_FILA = 0.90     # m de largura util da fila, igual ao modulo da mesa
DENSIDADE = 2.0      # pessoas por metro de fila simples (0,50 m por pessoa)
PROF = 4.10          # m do modulo: a fila comeca onde o modulo termina
RECUO_FAIXA = 0.30   # m de recuo de uma linha de mesa antes da faixa de entrada
TETO_LINHA = 14.0    # m: nenhuma linha de mesa passa disso

# --- precos ---------------------------------------------------------------
# M. O'Byrne Hire, pagina do produto "Tensa Barrier (2m Black Ribbon)":
# EUR 15,00 ex-VAT / EUR 18,45 inc-VAT por unidade; entrega em Dublin
# (ida e volta) EUR 80,00. O telegrama de orcamento ja previu 100 unidades
# por EUR 1.303,00, ou EUR 13,03 por unidade.
PRECO_LISTA_EX = 15.00
PRECO_LISTA_INC = 18.45
PRECO_ORCADO = 13.03
ENTREGA_DUBLIN = 80.00
ORCADO_UNIDADES = 100
RESERVA = 0.10

BOCHECHAS_POR_CANAL = 2   # postes de portao no checkpoint, por canal fechado


def corrida(L):
    """(fitas, postes, metros cobertos) de uma corrida de L metros."""
    if L <= 0:
        raise ValueError("corrida sem comprimento: filtre antes de contar")
    f = math.ceil(round(L / FITA, 6))
    return f, f + 1, f * FITA


class Conta:
    """Soma corridas mantendo a rastreabilidade linha a linha."""

    def __init__(self, nome, desc=""):
        self.nome, self.desc, self.itens = nome, desc, []

    def add(self, rotulo, n_corridas, L):
        if not n_corridas:
            return self
        f, p, m = corrida(L)
        self.itens.append(dict(rotulo=rotulo, corridas=n_corridas, L=round(L, 2),
                               fitas=f * n_corridas, postes=p * n_corridas,
                               metros=round(m * n_corridas, 2)))
        return self

    def avulso(self, rotulo, postes):
        if postes:
            self.itens.append(dict(rotulo=rotulo, corridas=0, L=0.0, fitas=0,
                                   postes=postes, metros=0.0))
        return self

    def total(self, chave):
        return sum(i[chave] for i in self.itens)


# --- geometria ------------------------------------------------------------
def DIR(rot):
    r = math.radians(rot)
    return (round(math.cos(r)), round(math.sin(r)))


def CCW(d):
    return (-d[1], d[0])


def carrega():
    """As 28 mesas do cenario de trabalho, com posicao, classe, entrada e as
    duas numeracoes; o salao e as portas da planta-base; o cenario usado."""
    dec = DC.montar()
    with open(DC.PRANCHETA, encoding="utf-8") as f:
        D = json.load(f)
    cen = DC.cenario_trabalho()
    pos = DC.posicoes(cen)
    mesas = []
    for m in dec["mesas"]:
        p = pos[m["mrv"]]
        mesas.append(dict(mrv=m["mrv"], eleitor=m["eleitor"], parede=m["parede"],
                          principal=m["principal"], agregada=m["agregada"],
                          classe=m["classe"], esperado=m["esperado"], aptos=m["aptos"],
                          entrada=m["entrada"], porta=m["porta"],
                          rot=int(p["rot"]) % 360, x=p["x"], y=p["y"], lado=p["lado"]))
    mesas.sort(key=lambda m: m["mrv"])
    return D, dec, mesas, cen


def _parede(m, S):
    return {270: "N", 180: "L", 0: "O", 90: "S"}[int(m["rot"]) % 360]


def _origem(m, S):
    p = _parede(m, S)
    if p == "N":
        return S["altura"]
    if p == "L":
        return S["largura"]
    if p == "O":
        return S["recorte"][2] if m["y"] < S["recorte"][3] - 1e-9 else 0
    return S["recorte"][3] if m["x"] < S["recorte"][2] - 1e-9 else 0


def _recuo(m, S):
    o, p = _origem(m, S), _parede(m, S)
    return {"N": o - m["y"], "L": o - m["x"],
            "O": m["x"] - o, "S": m["y"] - o}[p]


def _ao_longo(m):
    q = CCW(DIR(m["rot"]))
    return m["x"] * q[0] + m["y"] * q[1]


def pares(mesas, S, polos, desalinho=0.30, alcance=6.0):
    """Quem encara quem atraves do corredor de servico.

    Mesma regra da prancheta -- mesmo giro, mesmo recuo da parede, mesarios
    de lados opostos, e a segunda caindo do lado para onde a primeira poe os
    seus. Os polos (mesas vermelhas) saem do sorteio antes: a regra de 13/09
    lhes da 10 m proprios. Devolve (pares, sem_par, polos).
    """
    pool = [m for m in mesas if m["mrv"] not in polos]
    cand = []
    for a in pool:
        for b in pool:
            if b["mrv"] <= a["mrv"] or a["rot"] != b["rot"] or a["lado"] == b["lado"]:
                continue
            if abs(_recuo(a, S) - _recuo(b, S)) > desalinho:
                continue
            delta = _ao_longo(b) - _ao_longo(a)
            if (delta > 0) != (a["lado"] > 0):
                continue
            corredor = abs(delta) - LARG_FILA
            if corredor > alcance:
                continue
            cand.append((corredor, a["mrv"], b["mrv"]))
    cand.sort()
    usado, saida = set(), []
    for corredor, x, y in cand:
        if x in usado or y in usado:
            continue
        usado.update((x, y))
        saida.append(dict(a=x, b=y, corredor=round(corredor, 2)))
    sem_par = sorted(m["mrv"] for m in pool if m["mrv"] not in usado)
    return sorted(saida, key=lambda p: p["a"]), sem_par, sorted(polos)


def folga_geometrica(x0, y0, d, faixa, S, teto=TETO_LINHA):
    """Quanto uma linha pode correr a partir de (x0,y0) antes de esbarrar.

    Duas paradas: a faixa de entrada (canal da porta ao checkpoint ou ao topo
    do T), que a fila nao pode invadir sob pena de misturar quem entra com
    quem espera, e a parede oposta do salao. Devolve o comprimento livre.
    """
    lim = teto
    for t in range(1, int(teto * 20) + 1):
        u = t / 20
        x, y = x0 + d[0] * u, y0 + d[1] * u
        dentro = faixa and (faixa[0] <= x <= faixa[2] and faixa[1] <= y <= faixa[3])
        fora = not (0 <= x <= S["largura"] and 0 <= y <= S["altura"]) or (
            x <= S["recorte"][2] and y <= S["recorte"][3])
        if dentro or fora:
            lim = max(0.0, u - RECUO_FAIXA)
            break
    return round(lim, 2)


def rotulo_mesa(m):
    return f"mesa {m['eleitor']} (MRV {m['mrv']})"


def linhas_de_fila(mesas, S, filas, faixa, polos):
    """A geometria das linhas de mesa sob a regra de 13/09.

    `filas` = {"par": m, "polo": m, "solta": m}. O par recebe uma linha unica
    no eixo do corredor entre os dois modulos; o polo, a sua linha rente a
    fila, do lado dos mesarios; a solta, o que `filas["solta"]` disser (zero
    = sem unifila: a linha entra na lista com L 0 e nunca e contada).
    """
    ind = {m["mrv"]: m for m in mesas}
    ps, soltas, polos = pares(mesas, S, polos)
    out = []
    for p in ps:
        a, b = ind[p["a"]], ind[p["b"]]
        pedido = filas["par"]
        d, q = DIR(a["rot"]), CCW(DIR(a["rot"]))
        meio = (_ao_longo(b) - _ao_longo(a)) / 2
        x0 = a["x"] + d[0] * PROF + q[0] * meio
        y0 = a["y"] + d[1] * PROF + q[1] * meio
        L = min(pedido, folga_geometrica(x0, y0, d, faixa, S))
        out.append(dict(tipo="par", quem=[p["a"], p["b"]], L=L, pedido=pedido,
                        cortada=round(pedido - L, 2),
                        classe=max((a, b), key=lambda m: m["esperado"])["classe"],
                        pontos=[[round(x0, 3), round(y0, 3)],
                                [round(x0 + d[0] * L, 3), round(y0 + d[1] * L, 3)]],
                        rotulo=f"par {a['eleitor']}–{b['eleitor']} (MRV {a['mrv']}–{b['mrv']}) · "
                               f"linha do meio · {L:.1f} m".replace(".", ",")))
    for n in soltas + polos:
        m = ind[n]
        tipo = "polo" if n in polos else "solta"
        pedido = filas[tipo]
        if pedido <= 0:
            out.append(dict(tipo=tipo, quem=[n], L=0.0, pedido=0.0, cortada=0.0,
                            classe=m["classe"], pontos=[],
                            rotulo=f"{rotulo_mesa(m)} · sem par · sem unifila"))
            continue
        d, q = DIR(m["rot"]), CCW(DIR(m["rot"]))
        off = (LARG_FILA / 2 + 0.15) * m["lado"]
        x0 = m["x"] + d[0] * PROF + q[0] * off
        y0 = m["y"] + d[1] * PROF + q[1] * off
        L = min(pedido, folga_geometrica(x0, y0, d, faixa, S))
        out.append(dict(tipo=tipo, quem=[n], L=L, pedido=pedido, cortada=round(pedido - L, 2),
                        classe=m["classe"],
                        pontos=[[round(x0, 3), round(y0, 3)],
                                [round(x0 + d[0] * L, 3), round(y0 + d[1] * L, 3)]],
                        rotulo=f"{rotulo_mesa(m)} · {'polo' if tipo == 'polo' else 'sem par'}"
                               f" · {L:.1f} m".replace(".", ",")))
    return out


def portas_entrada(D, dec):
    """As portas de entrada, na ordem em que aparecem na parede sul."""
    por = {p["id"]: p for p in D["portas"]}
    return sorted((dict(entrada=e["id"], porta=p["id"], x1=p["x1"], x2=p["x2"],
                        larg=p["larg"], esperado=e["esperado"])
                   for e in dec["entradas"] for p in [por[e["porta"]]]),
                  key=lambda p: p["x1"])


def divisas(portas):
    """Os x das divisorias do canal, das bordas para o meio.

    S4, S5 e S6 sao contiguas -- 0,29 m entre vaos -- entao os tres canais
    dividem divisoria: as duas do meio sao as que separam A de B e B de C.
    """
    meio = [round((a["x2"] + b["x1"]) / 2, 3) for a, b in zip(portas, portas[1:])]
    return dict(bordas=[portas[0]["x1"], portas[-1]["x2"]], meio=meio)


def linhas_do_canal(portas, canal, canal_m, braco_m):
    """A geometria do canal de entrada: 1e ("meio") ou T ("T").

    "meio": uma divisoria vertical de `canal_m` em cada limite entre vaos.
    "T": as mesmas divisorias, so ate `canal_m`, e no topo de cada uma um
    braco de `braco_m` para fora (oeste na divisoria A|B, leste na B|C):
    cada lado e uma corrida continua de canal_m + braco_m.
    Devolve (linhas, bochechas).
    """
    d = divisas(portas)
    out = []
    if canal == "meio":
        for i, x in enumerate(d["meio"]):
            out.append(dict(tipo="divisoria", L=canal_m, pontos=[[x, 0.0], [x, canal_m]],
                            rotulo=f"divisória {'A|B' if i == 0 else 'B|C'} · {canal_m:.0f} m"))
        return out, BOCHECHAS_POR_CANAL * len(portas)
    if canal == "T":
        if len(d["meio"]) != 2:
            raise SystemExit("o desenho em T supoe tres entradas contiguas (duas divisorias)")
        xo, xl = d["meio"]
        out.append(dict(tipo="T", L=canal_m + braco_m,
                        pontos=[[xo, 0.0], [xo, canal_m], [round(xo - braco_m, 3), canal_m]],
                        rotulo=f"lado oeste do T · canal {canal_m:.0f} m + braço {braco_m:.0f} m (guia a fila A)"))
        out.append(dict(tipo="T", L=canal_m + braco_m,
                        pontos=[[xl, 0.0], [xl, canal_m], [round(xl + braco_m, 3), canal_m]],
                        rotulo=f"lado leste do T · canal {canal_m:.0f} m + braço {braco_m:.0f} m (guia a fila C)"))
        return out, BOCHECHAS_POR_CANAL
    raise SystemExit(f"canal {canal!r} desconhecido (esperado 'meio' ou 'T')")


# --- cenarios -------------------------------------------------------------
def agrupa(linhas):
    """Junta as linhas de mesa por (tipo, comprimento) para virarem itens."""
    g = {}
    for l in linhas:
        g.setdefault((l["tipo"], l["L"]), []).append(l)
    return sorted(g.items(), key=lambda kv: (-kv[0][1], kv[0][0]))


NOME_TIPO = {"par": "linha do meio de par", "solta": "mesa sem par",
             "polo": "polo (mesa vermelha)"}


def monta(op, portas, mesas, S, polos):
    """Uma conta por opcao de D4: canal + regra de mesa."""
    P = op["parametros"]
    canal, faixa_y = P["canal"], P["canal_m"]
    faixa = (portas[0]["x1"], 0.0, portas[-1]["x2"], faixa_y)
    lm = linhas_de_fila(mesas, S, P["filas_mesa_m"], faixa, polos)
    lc, bochechas = linhas_do_canal(portas, canal, P["canal_m"], P["braco_m"])
    c = Conta(op["id"], op["resumo"])
    for l in lc:
        c.add(l["rotulo"], 1, l["L"])
    c.avulso(f"bochechas de portão ({bochechas})", bochechas)
    ind = {m["mrv"]: m for m in mesas}
    for (tipo, L), g in agrupa([l for l in lm if l["L"] > 0]):
        quem = ", ".join("–".join(str(ind[n]["eleitor"]) for n in l["quem"]) for l in g)
        c.add(f"{NOME_TIPO[tipo]} · {L:.1f} m".replace(".", ",")
              + f" ({len(g)}: mesa{'s' if len(g) > 1 else ''} {quem})", len(g), L)
    sem_guia = sorted(n for l in lm if l["L"] <= 0 for n in l["quem"])
    return c, lc + lm, sem_guia


def tipo_por_mesa(linhas):
    """{mrv: (tipo, comprimento da fila da mesa)}."""
    out = {}
    for l in linhas:
        if l["tipo"] in ("par", "polo", "solta"):
            for n in l["quem"]:
                out[n] = (l["tipo"], l["L"])
    return out


def folego(mesas, por_mesa, seg_por_voto=60.0, janela_h=9.0, pico=1.8):
    """Quanto tempo de pico cada fila de mesa aguenta antes de transbordar.

    `minutos` None com `guia` True: a fila nunca cresce (chega menos do que a
    mesa atende). `guia` False: mesa sem unifila; o folego nao se aplica.
    """
    atende = 60.0 / seg_por_voto
    saida = []
    for m in mesas:
        tipo, fila = por_mesa[m["mrv"]]
        guia = fila > 0
        cap = round(fila * DENSIDADE) if guia else 0
        chega = m["esperado"] / janela_h / 60 * pico
        liq = chega - atende
        saida.append(dict(mrv=m["mrv"], eleitor=m["eleitor"], principal=m["principal"],
                          classe=m["classe"], esperado=m["esperado"], tipo=tipo, guia=guia,
                          fila=fila, cap=cap, chega_min=round(chega, 2), liquido_min=round(liq, 2),
                          minutos=(round(cap / liq) if guia and liq > 0 else None)))
    return saida


# --- saida ----------------------------------------------------------------
def custo(postes):
    return dict(postes=postes,
                lista_ex=round(postes * PRECO_LISTA_EX + ENTREGA_DUBLIN, 2),
                lista_inc=round(postes * PRECO_LISTA_INC + ENTREGA_DUBLIN * 1.23, 2),
                ao_preco_orcado=round(postes * PRECO_ORCADO, 2))


def resumo(c):
    p = c.total("postes")
    return dict(nome=c.nome, desc=c.desc, corridas=c.total("corridas"),
                fitas=c.total("fitas"), postes=p,
                postes_reserva=math.ceil(p * (1 + RESERVA)),
                metros=round(c.total("metros"), 2), itens=c.itens,
                custo=custo(math.ceil(p * (1 + RESERVA))))


def calcula():
    D, dec, mesas, cen = carrega()
    S = D["salao"]
    reg = DA.montar()
    d4 = next(d for d in reg["decisoes"] if d["id"] == "D4")
    if not d4["vigente"]:
        raise SystemExit("D4 sem opcao vigente: defina o tracado adotado em decisoes_abertas.py")
    portas = portas_entrada(D, dec)
    polos = sorted(m["mrv"] for m in mesas if m["classe"] == "alta")
    avisos = []
    # um polo que encara outra mesa: a regra de 13/09 nao diz o que fazer
    ps_com_polos, _, _ = pares(mesas, S, polos=[])
    for p in ps_com_polos:
        if p["a"] in polos or p["b"] in polos:
            avisos.append(f"MRV {p['a']} e {p['b']} se encaram e um deles e polo: o polo recebe os "
                          "seus 10 m e o outro fica sem par (regra de 13/09; confirmar com o Posto)")
    cenarios, linhas_por = [], {}
    for op in d4["opcoes"]:
        c, linhas, sem_guia = monta(op, portas, mesas, S, polos)
        r = resumo(c)
        r.update(adotado=(op["id"] == d4["vigente"]), canal=dict(op["parametros"]),
                 linhas=linhas, sem_guia=sem_guia, mesas_sem_guia=len(sem_guia))
        cenarios.append(r)
        linhas_por[op["id"]] = linhas
    adotado = next(c for c in cenarios if c["adotado"])
    ps, soltas, polos_ = pares(mesas, S, polos)
    por_mesa = tipo_por_mesa(linhas_por[d4["vigente"]])
    filas = d4["opcoes"][0]["parametros"]["filas_mesa_m"]
    if any(op["parametros"]["filas_mesa_m"] != filas for op in d4["opcoes"]):
        avisos.append("os tracados de D4 nao usam a mesma regra de mesa; a tabela de folego e a do vigente")
    for m in mesas:
        m["tipo"], m["fila_m"] = por_mesa[m["mrv"]]
        m["guia"] = m["fila_m"] > 0
    return dict(
        geradoEm=datetime.date.today().isoformat(),
        fonte=dict(cenario=cen["nome"], id=cen.get("id"), criadoEm=cen.get("criadoEm"),
                   base=cen.get("base", "A"), provisorio=bool(cen.get("provisorio")),
                   pendente=(DC.CENARIO_TRABALHO if cen.get("provisorio") else None), salao=S),
        numeracao=dec["numeracao"],
        premissas=dict(fita_m=FITA, largura_fila=LARG_FILA, densidade_p_por_m=DENSIDADE,
                       profundidade_modulo=PROF, recuo_faixa_m=RECUO_FAIXA, teto_linha_m=TETO_LINHA,
                       filas_mesa_m=filas, bochechas_por_canal=BOCHECHAS_POR_CANAL, reserva=RESERVA,
                       precos=dict(lista_ex=PRECO_LISTA_EX, lista_inc=PRECO_LISTA_INC,
                                   orcado=PRECO_ORCADO, entrega=ENTREGA_DUBLIN, orcado_unidades=ORCADO_UNIDADES),
                       regra="par = uma linha de 4 m no meio; vermelha = 10 m do seu lado; "
                             "nao vermelha sem par = sem unifila (Posto, 13/09/2026)"),
        divisas=divisas(portas), portas=portas,
        pareamento=dict(pares=ps, sem_par=soltas, polos=polos_),
        mesas=mesas, sem_guia=adotado["sem_guia"],
        folego=folego(mesas, por_mesa),
        comparecimento_total=dec["comparecimento"]["total"],
        adotado=d4["vigente"], cenarios=cenarios, avisos=avisos)


def tabela(c):
    marca = " — **adotado**" if c["adotado"] else ""
    out = [f"### Traçado {c['nome']}{marca}", "", c["desc"], "",
           "| Item | Corridas | Comp. | Fitas | Postes |", "|---|--:|--:|--:|--:|"]
    for i in c["itens"]:
        comp = f"{i['L']:.1f} m".replace(".", ",") if i["L"] else "—"
        cor = str(i["corridas"]) if i["corridas"] else "—"
        out.append(f"| {i['rotulo']} | {cor} | {comp} | {i['fitas']} | {i['postes']} |")
    out.append(f"| **Total** | **{c['corridas']}** | | **{c['fitas']}** | **{c['postes']}** |")
    return "\n".join(out)


def main():
    J = calcula()
    ind = {m["mrv"]: m for m in J["mesas"]}
    pa = J["pareamento"]
    marca = " (PROVISORIO: " + J["fonte"]["pendente"] + " ainda nao colado)" if J["fonte"]["provisorio"] else ""
    print(f"cenario de trabalho: {J['fonte']['cenario']}{marca}")
    print(f"pareamento: {len(pa['pares'])} pares ({2 * len(pa['pares'])} mesas), "
          f"{len(pa['sem_par'])} sem par, {len(pa['polos'])} polos")
    for p in pa["pares"]:
        a, b = ind[p["a"]], ind[p["b"]]
        print(f"  par {a['eleitor']:>2}–{b['eleitor']:<2} (MRV {p['a']:>2}–{p['b']:<2}) corredor {p['corredor']:.2f} m  "
              f"{a['classe']}/{b['classe']}")
    print("  sem par (sem unifila):", ", ".join(f"{ind[n]['eleitor']} (MRV {n}, {ind[n]['classe']})" for n in pa["sem_par"]))
    print("  polos (10 m):         ", ", ".join(f"{ind[n]['eleitor']} (MRV {n})" for n in pa["polos"]))
    for c in J["cenarios"]:
        cortes = [l for l in c["linhas"] if l.get("cortada", 0) > 0.01]
        for l in cortes:
            print(f"  {c['nome']}: {l['rotulo']} pedia {l['pedido']:.1f} m, cabe {l['L']:.1f} m")
    for a in J["avisos"]:
        print("  AVISO:", a)
    print()
    for c in J["cenarios"]:
        print(tabela(c)); print()
    for c in J["cenarios"]:
        k = c["custo"]
        print(f"{'>>' if c['adotado'] else '  '} Traçado {c['nome']}: corridas {c['corridas']} | fitas {c['fitas']} "
              f"| postes {c['postes']} | com reserva de 10% {c['postes_reserva']} | metros {c['metros']:.0f} "
              f"| sem guia {c['mesas_sem_guia']}")
        print(f"  EUR {k['lista_ex']:,.2f} ex-VAT | EUR {k['lista_inc']:,.2f} inc-VAT"
              f" | EUR {k['ao_preco_orcado']:,.2f} ao preço do telegrama"
              f" | vs. {ORCADO_UNIDADES} já contratados: {c['postes_reserva'] - ORCADO_UNIDADES:+d}")
    with open(ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(J, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print("gravado", os.path.relpath(ARQUIVO, RAIZ))


if __name__ == "__main__":
    main()
