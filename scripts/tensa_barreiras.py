"""Quantos separadores Tensa o Hall 2 consome, no desenho de canal reto.

Le o cenario `Hamad_3polos` da Prancheta do Hall 2 (posicoes das 28 mesas,
papel das portas, comparecimento esperado e classe de cada MRV) e converte
geometria em quantidade de postes e de fitas.

DESENHO ADOTADO PELO POSTO: **cenario 1e**. Uma unica linha por par, no
meio, separando as duas filas do par; mesa sem par ganha a sua propria
linha, de um lado so; e, dos quatro traçados possiveis no canal de entrada,
so as duas divisorias do meio -- as que de fato separam A de B e B de C.
Sao 100 postes, 111 com reserva de 10%.

Os cenarios 1 e 1i continuam calculados como alternativas descartadas, para
a decisao ficar auditavel: 1 acrescenta as duas bordas externas do canal;
1i redimensiona as filas por folego de pico. Nao sao o que sera montado.

Convencao de contagem, valida para o poste Tensa de fita retratil de 2,00 m:
uma corrida reta de L metros gasta ceil(L/2) fitas e ceil(L/2)+1 postes -- o
poste a mais e o de ponta, que fecha a corrida. Corridas independentes nao
compartilham poste; por isso o numero de corridas, e nao so a metragem, e o
que manda no orcamento.

Fonte dos dados: saidas/prancheta_hall2.json, extraido do artefato
"Prancheta do Hall 2" (cenario salvo em 05/09/2026).
"""
import json, math, os

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
FONTE = os.path.join(RAIZ, "saidas", "prancheta_hall2.json")

FITA = 2.00          # m de fita por poste Tensa
LARG_FILA = 0.90     # m de largura util da fila, igual ao modulo da mesa
DENSIDADE = 2.0      # pessoas por metro de fila simples (0,50 m por pessoa)
PROF = 4.10          # m do modulo: a fila comeca onde o modulo termina
COMPRIMENTO = {"alta": 10.0, "media": 5.0, "baixa": 3.0}

ADOTADO = "1e"       # o desenho que o Posto vai montar

# Os tres polos do cenario Hamad_3polos: as mesas de maior comparecimento,
# postas de proposito longe uma da outra e sem par.
POLOS = {22, 23, 24}

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

PORTOES = 6          # bochechas de portao no checkpoint, 2 por canal


def corrida(L):
    """(fitas, postes, metros cobertos) de uma corrida reta de L metros."""
    f = math.ceil(round(L / FITA, 6))
    return f, f + 1, f * FITA


class Conta:
    """Soma corridas mantendo a rastreabilidade linha a linha."""

    def __init__(self, nome, desc=""):
        self.nome, self.desc, self.itens = nome, desc, []
        self.familia = "cenário"

    def add(self, rotulo, n_corridas, L):
        if not n_corridas:
            return self
        f, p, m = corrida(L)
        self.itens.append(dict(rotulo=rotulo, corridas=n_corridas, L=L,
                               fitas=f * n_corridas, postes=p * n_corridas,
                               metros=round(m * n_corridas, 2)))
        return self

    def avulso(self, rotulo, postes):
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
    D = json.load(open(FONTE, encoding="utf-8"))
    base = {m["n"]: dict(m) for m in D["cenarios"]["A"]["mrvs"]}
    salvo = next(c for c in D["cenariosSalvos"] if c["nome"] == "Hamad_3polos")
    for a in salvo["alteracoes"]:
        base[a["n"]].update(a)
    dec = D["decisoes"]
    mesas = []
    for n in sorted(base):
        m, info = base[n], dec["mesas"][str(n)]
        mesas.append(dict(n=n, mrv=info["principal"], classe=info["classe"],
                          esperado=info["esperado"], aptos=info["aptos"],
                          entrada=info["entrada"], porta=info["porta"],
                          rot=m["rot"], x=m["x"], y=m["y"], lado=m["lado"],
                          fila=COMPRIMENTO[info["classe"]]))
    return D, dec, mesas, salvo


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


def pares(mesas, S, polos=POLOS, desalinho=0.30, alcance=6.0):
    """Quem encara quem atraves do corredor de servico.

    Mesma regra da prancheta -- mesmo giro, mesmo recuo da parede, mesarios
    de lados opostos, e a segunda caindo do lado para onde a primeira poe os
    seus -- com os polos retirados do sorteio antes, porque no Hamad_3polos
    eles estao isolados de proposito. Devolve (pares, sem_par, polos).
    """
    pool = [m for m in mesas if m["n"] not in polos]
    cand = []
    for a in pool:
        for b in pool:
            if b["n"] <= a["n"] or a["rot"] != b["rot"] or a["lado"] == b["lado"]:
                continue
            if abs(_recuo(a, S) - _recuo(b, S)) > desalinho:
                continue
            delta = _ao_longo(b) - _ao_longo(a)
            if (delta > 0) != (a["lado"] > 0):
                continue
            corredor = abs(delta) - LARG_FILA
            if corredor > alcance:
                continue
            cand.append((corredor, a["n"], b["n"]))
    cand.sort()
    usado, saida = set(), []
    for corredor, x, y in cand:
        if x in usado or y in usado:
            continue
        usado.update((x, y))
        saida.append(dict(a=x, b=y, corredor=round(corredor, 2)))
    sem_par = sorted(m["n"] for m in pool if m["n"] not in usado)
    return sorted(saida, key=lambda p: p["a"]), sem_par, sorted(polos)


def linhas_de_fila(mesas, S, comp, faixa=None):
    """A geometria das linhas: uma por par, no meio; uma por mesa solta.

    `comp` devolve o comprimento da fila de cada mesa. O par recebe uma linha
    unica, tao longa quanto a maior das duas filas, no eixo do corredor entre
    os dois modulos. A mesa sem par recebe a sua linha rente a fila, do lado
    dos mesarios.
    """
    ind = {m["n"]: m for m in mesas}
    ps, soltas, polos = pares(mesas, S)
    out = []
    for p in ps:
        a, b = ind[p["a"]], ind[p["b"]]
        pedido = max(comp(a), comp(b))
        d, q = DIR(a["rot"]), CCW(DIR(a["rot"]))
        meio = (_ao_longo(b) - _ao_longo(a)) / 2
        x0 = a["x"] + d[0] * PROF + q[0] * meio
        y0 = a["y"] + d[1] * PROF + q[1] * meio
        livre = folga_geometrica(x0, y0, d, faixa, S) if faixa else pedido
        L = min(pedido, livre)
        out.append(dict(tipo="par", quem=[p["a"], p["b"]], L=L,
                        pedido=pedido, cortada=round(pedido - L, 2),
                        classe=max((a, b), key=comp)["classe"],
                        x1=x0, y1=y0, x2=x0 + d[0] * L, y2=y0 + d[1] * L,
                        rotulo=f"par {p['a']}–{p['b']} · linha do meio · "
                               f"{L:.1f} m".replace(".", ",")))
    for n in soltas + polos:
        m = ind[n]
        pedido = comp(m)
        d, q = DIR(m["rot"]), CCW(DIR(m["rot"]))
        off = (LARG_FILA / 2 + 0.15) * m["lado"]
        x0 = m["x"] + d[0] * PROF + q[0] * off
        y0 = m["y"] + d[1] * PROF + q[1] * off
        livre = folga_geometrica(x0, y0, d, faixa, S) if faixa else pedido
        L = min(pedido, livre)
        tipo = "polo" if n in polos else "solta"
        out.append(dict(tipo=tipo, quem=[n], L=L, classe=m["classe"],
                        pedido=pedido, cortada=round(pedido - L, 2),
                        x1=x0, y1=y0, x2=x0 + d[0] * L, y2=y0 + d[1] * L,
                        rotulo=f"mesa {n} · {'polo' if tipo=='polo' else 'sem par'}"
                               f" · {L:.1f} m".replace(".", ",")))
    return out


def folga_geometrica(x0, y0, d, faixa, S, teto=14.0):
    """Quanto uma linha pode correr a partir de (x0,y0) antes de esbarrar.

    Duas paradas: a faixa de entrada que vai das portas ao checkpoint, que a
    fila nao pode invadir sob pena de misturar quem entra com quem espera, e a
    parede oposta do salao. Devolve o comprimento livre, em metros.
    """
    lim = teto
    for t in range(1, int(teto * 20) + 1):
        u = t / 20
        x, y = x0 + d[0] * u, y0 + d[1] * u
        dentro = (faixa[0] <= x <= faixa[2] and faixa[1] <= y <= faixa[3])
        fora = not (0 <= x <= S["largura"] and 0 <= y <= S["altura"]) or (
            x <= S["recorte"][2] and y <= S["recorte"][3])
        if dentro or fora:
            lim = max(0.0, u - 0.30)   # 0,30 m de recuo da faixa
            break
    return round(lim, 2)


def portas_entrada(D, dec):
    """As tres portas de entrada, na ordem em que aparecem na parede sul."""
    por = {p["id"]: p for p in D["portas"]}
    return sorted((dict(entrada=e["id"], porta=p["id"], x1=p["x1"], x2=p["x2"],
                        larg=p["larg"], esperado=e["esperado"])
                   for e in dec["entradas"] for p in [por[e["porta"]]]),
                  key=lambda p: p["x1"])


def divisas(portas):
    """Os x das linhas do canal reto, das bordas para o meio.

    S4, S5 e S6 sao contiguas -- 0,29 m entre vaos -- entao os tres canais
    dividem divisoria: sao quatro linhas, nao seis. As duas do meio sao as
    que de fato separam A de B e B de C; as duas das bordas sao contencao.
    """
    meio = [(a["x2"] + b["x1"]) / 2 for a, b in zip(portas, portas[1:])]
    return dict(bordas=[portas[0]["x1"], portas[-1]["x2"]], meio=meio)


# --- cenarios -------------------------------------------------------------
def agrupa(linhas):
    """Junta as linhas por (tipo, comprimento) para virarem itens da conta."""
    g = {}
    for l in linhas:
        g.setdefault((l["tipo"], l["L"]), []).append(l)
    return sorted(g.items(), key=lambda kv: (-kv[0][1], kv[0][0]))


NOME_TIPO = {"par": "linha do meio de par", "solta": "mesa sem par",
             "polo": "polo isolado"}


def monta(nome, desc, portas, linhas, canal="meio", tipos=None, familia="cenário"):
    """Monta uma conta a partir de duas escolhas independentes.

    `canal` diz o que vai na entrada -- "meio" so as duas divisorias entre as
    portas, "completo" com as duas bordas externas tambem, "nenhum" para as
    hipoteses que nao gastam barreira ali. `tipos` filtra as linhas de mesa por
    papel ("par", "solta", "polo"); None aceita todas.
    """
    c = Conta(nome, desc)
    c.familia = familia
    d = divisas(portas)
    if canal != "nenhum":
        c.add("divisórias entre os canais A|B e B|C", len(d["meio"]), 20.0)
        if canal == "completo":
            c.add("bordas externas dos canais", len(d["bordas"]), 20.0)
        c.avulso("bochechas de portão no checkpoint (2 por canal)", PORTOES)
    alvo = [l for l in linhas if tipos is None or l["tipo"] in tipos]
    for (tipo, L), g in agrupa(alvo):
        quem = ", ".join("–".join(str(n) for n in l["quem"]) for l in g)
        c.add(f"{NOME_TIPO[tipo]} · {L:.1f} m".replace(".", ",")
              + f" ({len(g)}: {quem})", len(g), L)
    return c


def isotempo(mesas, minutos=20.0, seg_por_voto=60.0, janela_h=9.0, pico=1.8,
             piso=3.0, passo=0.5):
    """Extensao que daria a toda mesa o mesmo folego em minutos de pico.

    A escada 3/5/10 m nao equaliza resiliencia: quanto maior o comparecimento,
    mais rapido a fila cresce, e 5 m sobre uma media de 518 esperados aguenta
    menos pico do que 10 m sobre uma alta de 590.
    """
    atende = 60.0 / seg_por_voto
    saida = []
    for m in mesas:
        liquido = m["esperado"] / janela_h / 60 * pico - atende
        L = max(piso, liquido * minutos / DENSIDADE) if liquido > 0 else piso
        saida.append(dict(n=m["n"], mrv=m["mrv"], classe=m["classe"],
                          esperado=m["esperado"], atual=m["fila"],
                          iso=round(math.ceil(L / passo) * passo, 1)))
    return saida


def folego(mesas, seg_por_voto=60.0, janela_h=9.0, pico=1.8):
    """Quanto tempo de pico cada fila de mesa aguenta antes de transbordar."""
    atende = 60.0 / seg_por_voto
    saida = []
    for m in mesas:
        cap = round(m["fila"] * DENSIDADE)
        chega = m["esperado"] / janela_h / 60 * pico
        liq = chega - atende
        saida.append(dict(n=m["n"], mrv=m["mrv"], classe=m["classe"],
                          esperado=m["esperado"], fila=m["fila"], cap=cap,
                          chega_min=round(chega, 2), liquido_min=round(liq, 2),
                          minutos=(round(cap / liq) if liq > 0 else None)))
    return saida


def cenarios(D, dec, mesas):
    S, portas = D["salao"], portas_entrada(D, dec)
    iso = {i["n"]: i["iso"] for i in isotempo(mesas)}
    faixa = (portas[0]["x1"], 0.0, portas[-1]["x2"], 20.0)
    escada = linhas_de_fila(mesas, S, lambda m: COMPRIMENTO[m["classe"]], faixa)
    porfol = linhas_de_fila(mesas, S, lambda m: iso[m["n"]], faixa)
    # As mesas de média que ficaram sem par: grandes o bastante para entrarem
    # na variante B2, pequenas o bastante para ficarem de fora da B.
    media_solta = {l["quem"][0] for l in escada
                   if l["tipo"] == "solta" and l["classe"] == "media"}
    escada_B2 = [l for l in escada
                 if l["tipo"] in ("par", "polo") or l["quem"][0] in media_solta]
    return [
        monta("1e", "ADOTADO. Uma linha no meio de cada par, uma linha por mesa "
              "sem par, e só as duas divisórias que separam A de B e B de C. "
              "O limite externo dos canais fica com sinalização e equipe.",
              portas, escada, canal="meio"),
        monta("1", "Descartado. O mesmo, mais as duas bordas externas dos "
              "canais de entrada.",
              portas, escada, canal="completo"),
        monta("1i", "Descartado. Mesma topologia, filas redimensionadas para "
              "que toda mesa aguente 20 minutos de pico.",
              portas, porfol, canal="completo"),
        monta("A", "HIPÓTESE. Unifila só para separar as três correntes da porta "
              "até o checkpoint. Nenhuma barreira nas mesas: da triagem em diante "
              "o eleitor circula solto e a ordem nas mesas fica com a equipe.",
              portas, escada, canal="meio", tipos=(), familia="hipótese"),
        monta("B", "HIPÓTESE. Unifila só nas mesas pareadas e nas grandes — a "
              "linha do meio de cada par e os três polos. Nada na entrada: as "
              "três correntes chegam juntas ao checkpoint.",
              portas, escada, canal="nenhum", tipos=("par", "polo"),
              familia="hipótese"),
        monta("B2", "HIPÓTESE, variante larga da B: as de média que ficaram sem "
              "par (9, 15, 16, 21) contam como grandes e também ganham linha.",
              portas, escada_B2, canal="nenhum", tipos=("par", "polo", "solta"),
              familia="hipótese"),
        monta("C", "SÍNTESE das duas hipóteses: as duas divisórias do checkpoint "
              "mais a linha do meio de cada par e os três polos. É o 1e sem as "
              "sete linhas das mesas soltas.",
              portas, escada, canal="meio", tipos=("par", "polo"),
              familia="síntese"),
    ], dict(escada=escada, porfolego=porfol, iso=iso, escada_B2=escada_B2)


# --- saida ----------------------------------------------------------------
RESERVA = 0.10


def custo(postes):
    return dict(postes=postes,
                lista_ex=round(postes * PRECO_LISTA_EX + ENTREGA_DUBLIN, 2),
                lista_inc=round(postes * PRECO_LISTA_INC
                                + ENTREGA_DUBLIN * 1.23, 2),
                ao_preco_orcado=round(postes * PRECO_ORCADO, 2))


def resumo(c):
    p = c.total("postes")
    return dict(nome=c.nome, desc=c.desc, familia=c.familia,
                corridas=c.total("corridas"),
                fitas=c.total("fitas"), postes=p,
                postes_reserva=math.ceil(p * (1 + RESERVA)),
                metros=c.total("metros"), itens=c.itens,
                custo=custo(math.ceil(p * (1 + RESERVA))))


def tabela(c):
    marca = " — **adotado**" if c.nome == ADOTADO else ""
    titulo = c.familia[0].upper() + c.familia[1:]
    out = [f"### {titulo} {c.nome}{marca}", "", c.desc, "",
           "| Item | Corridas | Comp. | Fitas | Postes |",
           "|---|--:|--:|--:|--:|"]
    for i in c.itens:
        comp = f"{i['L']:.1f} m".replace(".", ",") if i["L"] else "—"
        cor = str(i["corridas"]) if i["corridas"] else "—"
        out.append(f"| {i['rotulo']} | {cor} | {comp} | {i['fitas']} | {i['postes']} |")
    out.append(f"| **Total** | **{c.total('corridas')}** | | "
               f"**{c.total('fitas')}** | **{c.total('postes')}** |")
    return "\n".join(out)


def main():
    D, dec, mesas, salvo = carrega()
    S = D["salao"]
    cs, extra = cenarios(D, dec, mesas)
    ps, soltas, polos = pares(mesas, S)
    ind = {m["n"]: m for m in mesas}

    print(f"pareamento no {salvo['nome']}: {len(ps)} pares ({2*len(ps)} mesas), "
          f"{len(soltas)} sem par, {len(polos)} polos")
    for p in ps:
        print(f"  par {p['a']:>2}–{p['b']:<2} corredor {p['corredor']:.2f} m  "
              f"{ind[p['a']]['classe']}/{ind[p['b']]['classe']}")
    print("  sem par:", ", ".join(f"{n} ({ind[n]['classe']})" for n in soltas))
    print("  polos:  ", ", ".join(f"{n} ({ind[n]['classe']})" for n in polos))
    for nome, ls in (("escada", extra["escada"]), ("por fôlego", extra["porfolego"])):
        cortes = [l for l in ls if l.get("cortada", 0) > 0.01]
        if cortes:
            print(f"  {nome}: {len(cortes)} linha(s) aparada(s) pela faixa de entrada")
            for l in cortes:
                print(f"    {l['rotulo']}  pedia {l['pedido']:.1f} m, "
                      f"cabe {l['L']:.1f} m")
    print()
    for c in cs:
        print(tabela(c)); print()
    for c in cs:
        r = resumo(c)
        print(f"{'>>' if c.nome == ADOTADO else '  '} "
              f"Cenário {r['nome']}: corridas {r['corridas']} | fitas {r['fitas']} "
              f"| postes {r['postes']} | com reserva de 10% {r['postes_reserva']} "
              f"| metros {r['metros']:.0f}")
        k = r["custo"]
        print(f"  EUR {k['lista_ex']:,.2f} ex-VAT | EUR {k['lista_inc']:,.2f} inc-VAT"
              f" | EUR {k['ao_preco_orcado']:,.2f} ao preço do telegrama"
              f" | vs. 100 já contratados: {r['postes_reserva']-ORCADO_UNIDADES:+d}")

    saida = dict(
        fonte=dict(cenario=salvo["nome"], criadoEm=salvo["criadoEm"],
                   base=salvo["base"], salao=S),
        premissas=dict(fita_m=FITA, largura_fila=LARG_FILA,
                       densidade_p_por_m=DENSIDADE, profundidade_modulo=PROF,
                       profundidade_checkpoint=20.0, comprimentos=COMPRIMENTO,
                       reserva=RESERVA, polos=sorted(POLOS), adotado=ADOTADO,
                       regra="uma linha no meio de cada par; uma linha por mesa sem par"),
        pareamento=dict(pares=ps, sem_par=soltas, polos=polos),
        mesas=mesas, isotempo=isotempo(mesas), folego=folego(mesas),
        comparecimento_total=dec["comparecimento"]["total"],
        adotado=ADOTADO,
        cenarios=[dict(adotado=(c.nome == ADOTADO), **resumo(c)) for c in cs])
    with open(os.path.join(RAIZ, "saidas", "tensa_barreiras.json"), "w",
              encoding="utf-8") as f:
        json.dump(saida, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
