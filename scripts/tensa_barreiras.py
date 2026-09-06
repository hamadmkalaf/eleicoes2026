"""Quantos separadores Tensa o Hall 2 consome, nos dois cenarios de fila.

Le o cenario `Hamad_3polos` da Prancheta do Hall 2 (posicoes das 28 mesas,
papel das portas, comparecimento esperado e classe de cada MRV) e converte
geometria em quantidade de postes e de fitas.

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
COMPRIMENTO = {"alta": 10.0, "media": 5.0, "baixa": 3.0}

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


def corrida(L):
    """(fitas, postes, metros cobertos) de uma corrida reta de L metros."""
    f = math.ceil(round(L / FITA, 6))
    return f, f + 1, f * FITA


class Conta:
    """Soma corridas mantendo a rastreabilidade linha a linha."""

    def __init__(self, nome):
        self.nome = nome
        self.itens = []

    def add(self, rotulo, n_corridas, L):
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

    def linhas(self):
        for i in self.itens:
            yield i


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
                          rot=m["rot"], x=m["x"], y=m["y"],
                          fila=COMPRIMENTO[info["classe"]]))
    return D, dec, mesas, salvo


def portas_entrada(D, dec):
    """As tres portas de entrada, na ordem em que aparecem na parede sul."""
    por = {p["id"]: p for p in D["portas"]}
    saida = []
    for e in dec["entradas"]:
        p = por[e["porta"]]
        saida.append(dict(entrada=e["id"], porta=p["id"], x1=p["x1"], x2=p["x2"],
                          larg=p["larg"], esperado=e["esperado"]))
    return sorted(saida, key=lambda p: p["x1"])


def canal_linear(portas, profundidade):
    """Tres canais retos ate o checkpoint.

    As portas S4, S5 e S6 sao contiguas (0,29 m entre vaos), entao os canais
    dividem as divisorias: tres canais pedem quatro linhas, nao seis.
    """
    return len(portas) + 1


def serpentina(porta, profundidade, pitch, giro=1.20):
    """Linhas de uma serpentina de corredores longos dentro de um vao.

    Corredores no sentido da profundidade (e nao atravessados) porque cada
    corrida longa gasta um unico poste de ponta: menos corridas, menos postes.
    Devolve (n_corredores, divisorias_internas, comprimento_da_divisoria).
    """
    n = max(1, int(porta["larg"] // pitch))
    return n, n - 1, profundidade - giro


def cenario_1(portas, mesas, profundidade):
    c = Conta("Cenario 1 - canais retos ate o checkpoint + fila por mesa")
    c.add("canais de entrada A/B/C ate o checkpoint (divisorias compartilhadas)",
          canal_linear(portas, profundidade), profundidade)
    c.avulso("bochechas de portao no checkpoint (2 por canal)", 2 * len(portas))
    for classe in ("alta", "media", "baixa"):
        g = [m for m in mesas if m["classe"] == classe]
        if g:
            c.add(f"filas de mesa - {classe} ({len(g)} MRVs, {COMPRIMENTO[classe]:.0f} m, 2 lados)",
                  2 * len(g), COMPRIMENTO[classe])
    return c


def cenario_2(portas, mesas, profundidade, pitch):
    c = Conta("Cenario 2 - serpentina ate o checkpoint + 10 m so nas de alta")
    c.add("bordas e divisas entre os tres blocos de serpentina",
          canal_linear(portas, profundidade), profundidade)
    for p in portas:
        n, div, comp = serpentina(p, profundidade, pitch)
        c.add(f"divisorias internas da serpentina {p['entrada']} ({n} corredores)",
              div, comp)
    c.avulso("bochechas de portao no checkpoint (2 por canal)", 2 * len(portas))
    g = [m for m in mesas if m["classe"] == "alta"]
    c.add(f"filas de mesa - alta ({len(g)} MRVs, 10 m, 2 lados)", 2 * len(g), 10.0)
    return c


def capacidade_fila(L):
    return round(L * DENSIDADE)


def cenario_2b(portas, mesas, profundidade, pitch):
    """Serpentina na entrada e fila em todas as mesas, nao so nas de alta."""
    c = cenario_2(portas, mesas, profundidade, pitch)
    c.nome = "Cenario 2b - serpentina + fila em todas as mesas"
    for classe in ("media", "baixa"):
        g = [m for m in mesas if m["classe"] == classe]
        c.add(f"filas de mesa - {classe} ({len(g)} MRVs, {COMPRIMENTO[classe]:.0f} m, 2 lados)",
              2 * len(g), COMPRIMENTO[classe])
    return c


# Vizinhancas do Hamad_3polos em que duas filas de mesma extensao correm a
# 1,70 m ou menos uma da outra e podem dividir a divisoria do meio. Apuradas
# da geometria do cenario salvo; ver `vizinhancas()`.
PARTILHAVEIS = [(10, 9, 5.0), (16, 17, 5.0), (26, 27, 3.0), (2, 3, 3.0),
                (4, 5, 3.0), (14, 15, 3.0), (18, 19, 3.0)]


def vizinhancas(mesas, limite=1.70):
    """Pares de mesas vizinhas cujo vao livre cabe numa divisoria unica."""
    def eixo(m):
        r = math.radians(m["rot"])
        px, py = -round(math.sin(r)), round(math.cos(r))
        return m["x"] * px + m["y"] * py
    saida = []
    for rot in sorted({m["rot"] for m in mesas}):
        g = sorted((m for m in mesas if m["rot"] == rot), key=eixo)
        for a, b in zip(g, g[1:]):
            vao = abs(eixo(b) - eixo(a)) - LARG_FILA
            if vao <= limite:
                saida.append((a["n"], b["n"], round(vao, 2),
                              min(a["fila"], b["fila"])))
    return saida


def isotempo(mesas, minutos=20.0, seg_por_voto=60.0, janela_h=9.0, pico=1.8,
             piso=3.0, passo=0.5):
    """Extensao que daria a toda mesa o mesmo folego em minutos de pico.

    A escada 3/5/10 m nao equaliza resiliencia: quanto maior o comparecimento,
    mais rapido a fila cresce, e 5 m sobre uma media de 518 esperados aguenta
    menos pico do que 10 m sobre uma alta de 590. Esta funcao devolve o
    comprimento que iguala o folego, arredondado para cima em `passo`.
    """
    atende = 60.0 / seg_por_voto
    saida = []
    for m in mesas:
        liquido = m["esperado"] / janela_h / 60 * pico - atende
        L = max(piso, liquido * minutos / DENSIDADE) if liquido > 0 else piso
        L = math.ceil(L / passo) * passo
        saida.append(dict(n=m["n"], mrv=m["mrv"], classe=m["classe"],
                          esperado=m["esperado"], atual=m["fila"], iso=round(L, 1)))
    return saida


def cenario_1_isotempo(portas, mesas, profundidade, iso):
    c = Conta("Cenario 1i - canais retos + fila dimensionada por folego (20 min de pico)")
    c.add("canais de entrada A/B/C ate o checkpoint (divisorias compartilhadas)",
          canal_linear(portas, profundidade), profundidade)
    c.avulso("bochechas de portao no checkpoint (2 por canal)", 2 * len(portas))
    porL = {}
    for i in iso:
        porL.setdefault(i["iso"], []).append(i["n"])
    for L in sorted(porL, reverse=True):
        g = porL[L]
        c.add(f"filas de mesa de {L:.1f} m ({len(g)} MRVs: "
              f"{', '.join(str(n) for n in sorted(g))}, 2 lados)", 2 * len(g), L)
    return c


def cenario_1_economico(portas, mesas, profundidade):
    """Cenario 1 no minimo defensavel: 3 m com guia de um lado so e
    divisoria unica entre as filas vizinhas que correm coladas."""
    c = Conta("Cenario 1e - canais retos, 3 m com guia simples, divisorias partilhadas")
    c.add("canais de entrada A/B/C ate o checkpoint (divisorias compartilhadas)",
          canal_linear(portas, profundidade), profundidade)
    c.avulso("bochechas de portao no checkpoint (2 por canal)", 2 * len(portas))
    partilha = {cl: sum(1 for a, b, L in PARTILHAVEIS
                        if L == COMPRIMENTO[cl] and cl != "baixa")
                for cl in COMPRIMENTO}
    for classe in ("alta", "media"):
        g = [m for m in mesas if m["classe"] == classe]
        n = 2 * len(g) - partilha[classe]
        c.add(f"filas de mesa - {classe} ({len(g)} MRVs, {COMPRIMENTO[classe]:.0f} m, "
              f"2 lados, {partilha[classe]} divisorias partilhadas)",
              n, COMPRIMENTO[classe])
    g = [m for m in mesas if m["classe"] == "baixa"]
    c.add(f"filas de mesa - baixa ({len(g)} MRVs, 3 m, guia de um lado so)",
          len(g), 3.0)
    return c


def folego(mesas, dec, seg_por_voto=60.0, janela_h=9.0, pico=1.8):
    """Quanto tempo de pico cada fila de mesa aguenta antes de transbordar."""
    saida = []
    for m in mesas:
        cap = capacidade_fila(m["fila"])
        chega = m["esperado"] / janela_h / 60 * pico      # pessoas por minuto
        atende = 60.0 / seg_por_voto
        liquido = chega - atende
        minutos = (cap / liquido) if liquido > 0 else None
        saida.append(dict(n=m["n"], mrv=m["mrv"], classe=m["classe"],
                          esperado=m["esperado"], fila=m["fila"], cap=cap,
                          chega_min=round(chega, 2), liquido_min=round(liquido, 2),
                          minutos=(round(minutos) if minutos else None)))
    return saida


def demanda(dec, portas, janela_h=9.0, pico=1.8):
    """Chegada media e de pico por porta, e o que a serpentina absorve."""
    total = dec["comparecimento"]["total"]
    linhas = []
    for p in portas:
        med = p["esperado"] / janela_h
        pic = med * pico
        linhas.append(dict(entrada=p["entrada"], esperado=p["esperado"],
                           media_h=round(med), pico_h=round(pic),
                           pico_min=round(pic / 60, 1)))
    return total, linhas


def custo(postes):
    frete = ENTREGA_DUBLIN
    return dict(postes=postes,
                lista_ex=round(postes * PRECO_LISTA_EX + frete, 2),
                lista_inc=round(postes * PRECO_LISTA_INC + frete * 1.23, 2),
                ao_preco_orcado=round(postes * PRECO_ORCADO, 2))


def tabela(c):
    out = [f"### {c.nome}", "",
           "| Item | Corridas | Comp. | Fitas | Postes | Metros |",
           "|---|--:|--:|--:|--:|--:|"]
    for i in c.linhas():
        comp = f"{i['L']:.2f} m".replace(".", ",") if i["L"] else "—"
        cor = str(i["corridas"]) if i["corridas"] else "—"
        met = f"{i['metros']:.0f}".replace(".", ",") if i["metros"] else "—"
        out.append(f"| {i['rotulo']} | {cor} | {comp} | {i['fitas']} | {i['postes']} | {met} |")
    out.append(f"| **Total** | | | **{c.total('fitas')}** | **{c.total('postes')}** | "
               f"**{c.total('metros'):.0f}** |".replace(".0 ", " "))
    return "\n".join(out)


def main():
    D, dec, mesas, salvo = carrega()
    portas = portas_entrada(D, dec)
    PROF = 20.0
    PITCH = 1.18

    c1 = cenario_1(portas, mesas, PROF)
    c1e = cenario_1_economico(portas, mesas, PROF)
    c2 = cenario_2(portas, mesas, PROF, PITCH)
    c2b = cenario_2b(portas, mesas, PROF, PITCH)
    iso = isotempo(mesas)
    c1i = cenario_1_isotempo(portas, mesas, PROF, iso)
    todos = (c1, c1e, c1i, c2, c2b)

    RESERVA = 0.10
    res = {}
    for c in todos:
        p = c.total("postes")
        pr = math.ceil(p * (1 + RESERVA))
        res[c.nome] = dict(fitas=c.total("fitas"), postes=p, postes_reserva=pr,
                           metros=c.total("metros"), custo=custo(pr))

    total, dem = demanda(dec, portas)
    saida = dict(fonte=dict(cenario=salvo["nome"], criadoEm=salvo["criadoEm"],
                            base=salvo["base"], salao=D["salao"]),
                 premissas=dict(fita_m=FITA, largura_fila=LARG_FILA,
                                densidade_p_por_m=DENSIDADE,
                                profundidade_checkpoint=PROF,
                                pitch_serpentina=PITCH,
                                comprimentos=COMPRIMENTO, reserva=RESERVA),
                 mesas=mesas, demanda=dem, comparecimento_total=total,
                 vizinhancas=vizinhancas(mesas), folego=folego(mesas, dec),
                 isotempo=iso,
                 cenarios={c.nome: dict(itens=list(c.linhas()), **res[c.nome])
                           for c in todos})
    os.makedirs(os.path.join(RAIZ, "saidas"), exist_ok=True)
    with open(os.path.join(RAIZ, "saidas", "tensa_barreiras.json"), "w",
              encoding="utf-8") as f:
        json.dump(saida, f, ensure_ascii=False, indent=1)

    for c in todos:
        print(tabela(c)); print()
    for c in todos:
        r = res[c.nome]
        print(f"{c.nome}\n  fitas {r['fitas']} | postes {r['postes']} "
              f"| com reserva de 10% {r['postes_reserva']} | metros {r['metros']:.0f}")
        k = r["custo"]
        print(f"  EUR {k['lista_ex']:,.2f} ex-VAT | EUR {k['lista_inc']:,.2f} inc-VAT "
              f"(lista O'Byrne, frete incluso) | EUR {k['ao_preco_orcado']:,.2f} ao preco do telegrama")
        print(f"  orcado no telegrama: {ORCADO_UNIDADES} unidades -> faltam "
              f"{r['postes_reserva'] - ORCADO_UNIDADES}")
    print()
    print(f"comparecimento esperado {total}")
    for d in dem:
        print(f"  porta {d['entrada']}: {d['esperado']} esperados | media {d['media_h']}/h "
              f"| pico {d['pico_h']}/h = {d['pico_min']}/min")


if __name__ == "__main__":
    main()
