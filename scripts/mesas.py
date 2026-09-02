"""Quantas mesas receptoras de votos cabem no Hall 2.

Uma ideia de layout, montada sobre `salao.py`. Modela a MRV com o mobiliario
que o usuario informou nesta rodada — mesa de identificacao de 1,70 x 0,80 m
para tres mesarios, mais a mesa de votacao redonda de 0,90 m — e com a regra de
pareamento do croqui, e depois empacota o maximo de modulos no perimetro.

O modulo, visto de cima, com o eixo PERPENDICULAR a parede:

    parede
    |<-0,90->|<-0,90->|<-0,60->|<------- 1,70 ------->|
    | eleitor|  urna  |passagem| mesa de identificacao|
    | votando| Ø 0,90 |        | 3 mesarios no lado   |
    |        |        |        | voltado ao corredor  |
    |<---------------- 4,10 m de profundidade ------->|

O eleitor entra pelo corredor, percorre o lado longo da mesa de identificacao,
segue ate a mesa de votacao encostada na parede, vota de costas para o salao e
volta pelo mesmo corredor. Na direcao paralela a parede o modulo ocupa 0,90 m —
a mesa de votacao, que e o elemento mais largo.

Pareamento: dois modulos vizinhos partilham um corredor de A metros, com os
mesarios de frente uns para os outros; o par seguinte fica de costas, a
B = 1,50 m. Passo do par ao longo da parede:

    passo = 0,90 + A + 0,90 + 1,50 = 3,30 + A

Com n pares num trecho livre de L metros:  n * (3,30 + A) - 1,50 <= L
"""
import math
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "scripts"))

import salao as FL                                            # noqa: E402
import planta_base as PB                                      # noqa: E402

# ------------------------------------------------------------------ o modulo
# Dimensoes informadas pelo usuario nesta rodada. Substituem a mesa de 1,60 x
# 0,70 m do secao 4 do contexto, e mudam a orientacao: a urna deixa de ficar ao
# lado da mesa e passa a ficar em linha com ela, encostada na parede.
MESA_IDENT = (1.70, 0.80)     # 1,70 no eixo do modulo, 0,80 de largura
URNA_D = 0.90                 # mesa de votacao, redonda

# Premissas de trabalho deste modelo, nao medidas verificadas.
FOLGA_ELEITOR = 0.90          # eleitor votando, entre a urna e a parede
PASSAGEM = 0.60               # entre a mesa de votacao e a mesa de identificacao
MESARIO_ASSENTO = 0.75        # cadeira + pessoa, projetada no corredor

PROF = FOLGA_ELEITOR + URNA_D + PASSAGEM + MESA_IDENT[0]   # 4,10 m
LARG = max(URNA_D, MESA_IDENT[1])                          # 0,90 m

CORREDOR_MIN, CORREDOR_MAX = 2.50, 3.00    # A, corredor de dentro do par
ENTRE_PARES_MIN, ENTRE_PARES_MAX = 1.00, 1.50   # B, espaco entre pares

# MRV avulsa: onde o trecho de parede nao aceita um par, cabe um modulo
# sozinho, com os mesarios de um lado so e o corredor do outro. E o caso dos
# tres trechos de 2,79 m da parede leste, entre os recuos das saidas de
# emergencia. O corredor de uma avulsa e menor que o de um par — o modelo
# devolve quanto — e o modulo tem de caber inteiro no trecho, sem que cadeira
# de mesario invada o recuo vizinho.
CORREDOR_AVULSO_MIN = 1.00     # passagem livre minima ao lado dos mesarios
FOLGA_ASSENTO = 0.05           # entre a cadeira do mesario e a borda do trecho
LARG_AVULSA = LARG + MESARIO_ASSENTO + FOLGA_ASSENTO + CORREDOR_AVULSO_MIN

URNAS = 28


def passo_do_par(a, b=ENTRE_PARES_MIN):
    return 2 * LARG + a + b


def pares_no_trecho(L, a_min=CORREDOR_MIN, a_max=CORREDOR_MAX,
                    b_min=ENTRE_PARES_MIN, b_max=ENTRE_PARES_MAX):
    """Maximo de pares num trecho livre de L metros.

    Empacota com os minimos e depois distribui a sobra: primeiro alarga o
    corredor de dentro do par ate a_max, que e onde o eleitor anda, e so
    depois o espaco entre pares ate b_max. Devolve (pares, corredor, entre
    pares, sobra)."""
    n = int(math.floor((L + b_min) / passo_do_par(a_min, b_min) + 1e-9))
    if n <= 0:
        return 0, 0.0, 0.0, L
    sobra = L - (n * (2 * LARG + a_min) + (n - 1) * b_min)
    t = min(sobra, n * (a_max - a_min))
    a, sobra = a_min + t / n, sobra - t
    b = b_min
    if n > 1:
        t = min(sobra, (n - 1) * (b_max - b_min))
        b, sobra = b_min + t / (n - 1), sobra - t
    return n, a, b, sobra


def ocupa_trecho(L, a_min=CORREDOR_MIN, a_max=CORREDOR_MAX, avulsa=False):
    """O que cabe num trecho livre de L metros.

    Devolve (pares, corredor, entre_pares, sobra, avulsas, corredor_avulso). A
    MRV avulsa so entra onde nao cabe par nenhum, e so se `avulsa` estiver
    ligado."""
    n, corredor, entre, sobra = pares_no_trecho(L, a_min, a_max)
    if n or not avulsa or L < LARG_AVULSA:
        return n, corredor, entre, sobra, 0, 0.0
    # o corredor da avulsa e o que sobra do trecho depois do modulo e da fila
    # de mesarios de um lado so
    return 0, 0.0, 0.0, 0.0, 1, L - LARG - MESARIO_ASSENTO - FOLGA_ASSENTO


# ---------------------------------------------------------------- bloqueios
FOLGA_VAO = 0.30          # nada encosta na folha de uma porta
FOLGA_SERVICO = 1.50      # N2 (catering) e O2 (unico acesso aos WC)
FOLGA_HALL1 = 1.00        # O1
VESTIBULO = 2.00          # divisoria a 2 m da porta de carga, no cenario B
VESTIBULO_LADO = 1.00     # quanto a divisoria passa dos lados do vao
CIRC_VESTIBULO = 1.50     # circulacao para chegar ao vestibulo

# Fora da parede leste o recuo de 3 m nao foi determinado (questao 3 do
# contexto). "prudente" aplica os 3 m a toda saida de emergencia; "minima" so
# a exige onde ja esta decidido, na leste.
HIPOTESES = ("prudente", "minima")

# O recuo de emergencia tem duas medidas, e elas nao precisam ser iguais:
#   RECUO_FRONTAL  profundidade da faixa livre a frente do vao
#   RECUO_LATERAL  afastamento exigido de cada lado do vao, ao longo da parede
# O RDS determinou 3 m; se os 3 m valerem so a frente, e nao dos lados, a
# parede leste rende bem mais. E a diferenca entre as leituras comparadas em
# `compara_recuo_lateral()`.
RECUO_FRONTAL = FL.RECUO_EMERGENCIA
RECUO_LATERAL = FL.RECUO_EMERGENCIA

CARGA = {"carga oeste": "S1", "carga leste": "S7"}

# ---------------------------------------------------- a fachada leste recuada
# Decisao do usuario: a parede leste inteira e area protegida numa faixa de 3 m
# — nao um envelope por porta —, e as mesas ficam alinhadas logo depois dela,
# todas comecando a mesma distancia da parede. E o que permite uma fileira
# continua: as quatro saidas L1 a L4 nao recortam mais a fileira, porque ela
# nao encosta na parede.
#
# A urna continua voltada para a parede: o eleitor se coloca entre ela e a
# faixa protegida, de modo que a tela fique virada para a fachada e ninguem no
# salao a veja. A faixa de 3 m nao recebe mobiliario nem fila; serve de
# aproximacao e de rota de fuga, com o trafego restringido.
FAIXA_LESTE = 3.0
FACE_LESTE_RECUADA = "leste_recuada"
# A fileira guarda CIRCULACAO livre das fachadas norte e sul: as bocas dos
# corredores precisam de aproximacao, e as pontas nao podem parar em cima de
# uma porta da fachada sul.
FL.FACES[FACE_LESTE_RECUADA] = dict(
    eixo="v", fixo=FL.HALL_W - FAIXA_LESTE, s0=3.0, s1=FL.HALL_H - 3.0, dentro=-1)

ORDEM = ["norte", "recorte_h", "oeste", "sul", FACE_LESTE_RECUADA, "recorte_v"]

# Onde a MRV avulsa e permitida. Nenhuma face precisa dela desde que a fachada
# leste passou a receber uma fileira recuada em vez de modulos encostados entre
# os recuos: os trechos de 2,79 m sairam de cena. A maquinaria fica, porque
# qualquer mudanca nos recuos pode trazer o caso de volta.
AVULSA_EM = ()

# --------------------------------------------------------------- ajuste final
# O salao comporta 30 MRVs com a folga cheia, e sao 28 urnas. As duas que
# sobram foram escolhidas pelo usuario sobre a planta: sai o par mais a leste
# da parede norte, que se aproximava demais da fileira recuada no canto
# nordeste, e o par da face norte do recorte encosta a direita, liberando o
# canto sudoeste em vez de ficar no meio do trecho.
#
# Sao decisoes de desenho, nao de calculo: por isso ficam aqui, nomeadas, e nao
# escondidas no empacotamento. Passar `ajustes={}` devolve o maximo.
AJUSTE_28 = {
    "norte": dict(tirar_ultimos_pares=1),
    "recorte_h": dict(alinha="direita"),
}


def _numero(codigo):
    """Numero de fachada de uma porta, a partir do codigo do RDS."""
    for p in PB.numera():
        if p["codigo"] == codigo.split(" (")[0]:
            return p["num"]
    return codigo


def bloqueios(cenario, hipotese, lateral=None, frontal=None, faixa_leste=True):
    """Cortes ao longo de cada face e retangulos proibidos no piso.

    `faixa_leste=False` volta atras na decisao da fachada leste: em vez da
    faixa protegida continua, os quatro envelopes por porta. E o plano B, para
    o caso de o RDS nao aceitar a faixa."""
    lateral = RECUO_LATERAL if lateral is None else lateral
    frontal = RECUO_FRONTAL if frontal is None else frontal
    cortes = {f: [] for f in FL.FACES}
    rects = []

    if faixa_leste:
        # a fachada leste inteira, numa faixa de 3 m: e a reserva que substitui
        # os quatro envelopes de porta
        rects.append((FL.retangulo_na_parede("leste", 0.0, FL.HALL_H, FAIXA_LESTE),
                      "fachada leste · faixa protegida de 3 m"))
        cortes["leste"].append((0.0, FL.HALL_H, "fachada leste protegida"))

    for face in FL.FACES:
        for codigo, a, b in FL.portas_da_face(face):
            num = _numero(codigo)
            if face == "leste" and faixa_leste:
                continue                       # ja coberta pela faixa
            emerg = (codigo in FL.EMERGENCIA and num != "N1"
                     and (face == "leste" or hipotese == "prudente"))

            if emerg:
                f = FL.FACES[face]
                rects.append((FL.retangulo_na_parede(
                    face, max(f["s0"], a - lateral), min(f["s1"], b + lateral),
                    frontal), f"{num} · recuo de emergência"))
                cortes[face].append((a - lateral, b + lateral, f"{num} recuo"))
                continue

            if num in ("S1", "S7"):
                if cenario == "B":
                    lado = VESTIBULO_LADO + CIRC_VESTIBULO
                    cortes[face].append((a - lado, b + lado, f"{num} vestíbulo"))
                    f = FL.FACES[face]
                    rects.append((FL.retangulo_na_parede(
                        face, max(f["s0"], a - VESTIBULO_LADO),
                        min(f["s1"], b + VESTIBULO_LADO), VESTIBULO),
                        f"{num} · vestíbulo da divisória"))
                else:
                    cortes[face].append((a - FOLGA_VAO, b + FOLGA_VAO, f"{num} vão"))
                continue

            folga = FOLGA_VAO
            if num == "N2":
                folga = FOLGA_SERVICO          # saida do catering
            elif num == "O2":
                folga = FOLGA_SERVICO          # unico acesso aos WC
            elif num == "O1":
                folga = FOLGA_HALL1
            cortes[face].append((a - folga, b + folga, f"{num} vão"))

    return cortes, rects


def vaos_proibidos():
    """A folha de cada porta, que nenhum modulo pode tapar."""
    out = []
    for face in FL.FACES:
        for codigo, a, b in FL.portas_da_face(face):
            out.append((FL.retangulo_na_parede(face, a, b, FOLGA_VAO),
                        f"{_numero(codigo)} vão"))
    return out


# -------------------------------------------------------------- empacotamento
def rect_do_modulo(m):
    return FL.retangulo_na_parede(m["face"], m["s"] - LARG / 2,
                                  m["s"] + LARG / 2, PROF)


def _sombra(face, rect):
    """Intervalo de s em que `rect` atrapalha uma faixa de PROF nesta face."""
    f = FL.FACES[face]
    faixa = FL.retangulo_na_parede(face, f["s0"], f["s1"], PROF)
    if not FL.sobrepoe(faixa, rect):
        return None
    return (rect[0], rect[2]) if f["eixo"] == "h" else (rect[1], rect[3])


ALINHA = {"centro": 0.5, "direita": 1.0, "esquerda": 0.0}


def empacota(face, cortes, a_min, a_max, obstaculos=(), avulsa_em=(), ajustes=None):
    ajuste = (ajustes or {}).get(face, {})
    fracao = ALINHA[ajuste.get("alinha", "centro")]
    f = FL.FACES[face]
    livres = [(f["s0"], f["s1"])]
    for a, b, _ in cortes.get(face, []):
        livres = FL.subtrai(livres, (a, b))
    for rect, _motivo in obstaculos:
        sb = _sombra(face, rect)
        if sb:
            livres = FL.subtrai(livres, sb)

    modulos, trechos = [], []
    for a, b in livres:
        L = b - a
        n, corredor, entre, sobra, avulsas, corr_av = ocupa_trecho(
            L, a_min, a_max, avulsa=face in avulsa_em)
        trechos.append(dict(s0=round(a, 2), s1=round(b, 2), livre=round(L, 2),
                            pares=n, corredor=round(corredor, 2) if n else None,
                            entre_pares=round(entre, 2) if n > 1 else None,
                            sobra=round(sobra, 2), avulsas=avulsas,
                            corredor_avulso=round(corr_av, 2) if avulsas else None))
        s = a + sobra * fracao     # centrado por omissao; ver AJUSTE_28
        for i in range(n):
            par = f"{face}|{a:.2f}|{i}"
            modulos.append(dict(face=face, s=s + LARG / 2, corredor=corredor,
                                lado="a", par=par))
            modulos.append(dict(face=face, s=s + LARG + corredor + LARG / 2,
                                corredor=corredor, lado="b", par=par))
            s += passo_do_par(corredor, entre)
        if avulsas:
            # modulo encostado numa borda do trecho, mesarios voltados para o
            # corredor que sobra do outro lado
            modulos.append(dict(face=face, s=a + LARG / 2, corredor=corr_av,
                                lado="a", par=None))

    tirar = ajuste.get("tirar_ultimos_pares", 0)
    if tirar:
        alvo = [p for p in dict.fromkeys(m["par"] for m in modulos) if p][-tirar:]
        modulos = [m for m in modulos if m["par"] not in alvo]
        for t in trechos:
            for p in alvo:
                if p.startswith(f"{face}|{t['s0']:.2f}|"):
                    t["pares"] -= 1
    return modulos, trechos


def valida(modulos, proibidos):
    """Nenhuma planta e gravada sem passar por aqui."""
    erros = []
    caixas = [rect_do_modulo(m) for m in modulos]
    for m, c in zip(modulos, caixas):
        if not FL.dentro_do_salao(c):
            erros.append(f"módulo {m['face']}@{m['s']:.2f} sai do salão")
        for r, motivo in proibidos:
            if FL.sobrepoe(c, r):
                erros.append(f"módulo {m['face']}@{m['s']:.2f} invade {motivo}")
    for i in range(len(caixas)):
        for j in range(i + 1, len(caixas)):
            if FL.sobrepoe(caixas[i], caixas[j]):
                erros.append(f"módulos {i} e {j} se sobrepõem")
    return erros


def choques(rects):
    """Reservas que se pisam — um vestibulo dentro do recuo de uma saida de
    emergencia, por exemplo. Nao invalida o layout das mesas, mas e um conflito
    real de projeto."""
    out = []
    for i in range(len(rects)):
        for j in range(i + 1, len(rects)):
            (ra, ma), (rb, mb) = rects[i], rects[j]
            if FL.sobrepoe(ra, rb):
                x0, y0 = max(ra[0], rb[0]), max(ra[1], rb[1])
                x1, y1 = min(ra[2], rb[2]), min(ra[3], rb[3])
                out.append(dict(a=ma, b=mb, area=round((x1 - x0) * (y1 - y0), 1)))
    return out


def roda(cenario, hipotese, a_min=CORREDOR_MIN, a_max=CORREDOR_MAX,
         ordem=None, extras=(), avulsa_em=AVULSA_EM, ajustes=None,
         faixa_leste=True):
    """Perimetro. As faces sao processadas em ordem: cada faixa ja montada vira
    obstaculo para as seguintes, o que resolve os cantos — duas faces vizinhas
    nao podem ocupar o mesmo quadrado de PROF x PROF, e quem vem primeiro fica
    com ele."""
    cortes, rects = bloqueios(cenario, hipotese, faixa_leste=faixa_leste)
    proibidos = list(rects) + vaos_proibidos() + list(extras)
    ordem = list(ordem or ORDEM)
    if not faixa_leste:
        # sem a faixa, a fileira recuada some e a fachada volta a receber
        # modulos encostados — que so cabem avulsos, entre os envelopes
        ordem = ["leste" if f == FACE_LESTE_RECUADA else f for f in ordem]
        avulsa_em = tuple(avulsa_em) + ("leste",)

    obst = list(proibidos)
    modulos, por_face = [], {}
    for face in ordem:
        mods, trechos = empacota(face, cortes, a_min, a_max, obst, avulsa_em,
                                 ajustes)
        modulos += mods
        por_face[face] = dict(mrv=len(mods),
                              pares=sum(t["pares"] for t in trechos),
                              avulsas=sum(t["avulsas"] for t in trechos),
                              trechos=trechos)
        for m in mods:
            obst.append((rect_do_modulo(m), f"faixa~{face}"))

    numera_mrv(modulos)
    return dict(cenario=cenario, hipotese=hipotese, a_min=a_min,
                mrv=len(modulos), por_face=por_face, modulos=modulos,
                proibidos=proibidos, reservas=rects,
                erros=valida(modulos, proibidos), choques=choques(rects))


# Ordem em que as MRVs sao numeradas: um circuito unico pelo salao, no sentido
# horario a partir do canto noroeste. O sinal e o sentido de percurso ao longo
# de cada face — +1 segue a coordenada corrente, -1 vai contra ela.
CIRCUITO = [("norte", +1), (FACE_LESTE_RECUADA, -1), ("leste", -1), ("sul", -1),
            ("recorte_v", -1), ("recorte_h", -1), ("oeste", +1)]


def numera_mrv(modulos):
    """Numera as MRVs de 1 a N seguindo o circuito, e devolve a lista ordenada.

    O numero e a identidade da mesa em campo: e por ele que se fala de uma
    secao no dia, e e ele que a planta imprime."""
    ordenados, vistas = [], set()
    for face, sentido in CIRCUITO:
        da_face = [m for m in modulos if m["face"] == face]
        ordenados += sorted(da_face, key=lambda m: sentido * m["s"])
        vistas.add(face)
    # faces fora do circuito — as divisorias exentas, por exemplo — entram
    # depois, em ordem estavel
    resto = [m for m in modulos if m["face"] not in vistas]
    ordenados += sorted(resto, key=lambda m: (m["face"], m["s"]))
    for i, m in enumerate(ordenados, 1):
        m["n"] = i
    return ordenados


def sombras(cenario, hipotese, a_min, ordem=None, avulsa_em=AVULSA_EM):
    """Por face, os trechos comidos por algo que nao esta nela: o recuo de uma
    porta da face vizinha, ou a faixa de modulos que ja tomou o canto."""
    cortes, rects = bloqueios(cenario, hipotese)
    dono = {}
    for face in FL.FACES:
        for codigo, _a, _b in FL.portas_da_face(face):
            dono[_numero(codigo)] = face

    obst = list(rects) + vaos_proibidos()
    fora = {}
    for face in (ordem or ORDEM):
        f = FL.FACES[face]
        marcas = []
        for rect, motivo in obst:
            if dono.get(motivo.split()[0]) == face:
                continue                       # reserva da propria face
            sb = _sombra(face, rect)
            if not sb:
                continue
            a, b = max(f["s0"], sb[0]), min(f["s1"], sb[1])
            if b - a > 1e-9:
                marcas.append((round(a, 2), round(b, 2)))
        fora[face] = marcas
        mods, _ = empacota(face, cortes, a_min, CORREDOR_MAX, obst, avulsa_em)
        for m in mods:
            obst.append((rect_do_modulo(m), f"faixa~{face}"))
    return fora


# ------------------------------------------------- divisorias exentas
# O salao tem piso de sobra e parede de menos. Uma divisoria exenta funciona
# como parede para as duas faces: a urna continua encostada e voltada para uma
# superficie cega, que e o que a secao 4 do contexto ja registrava como
# suficiente — o sigilo vem da estrutura, nao da parede do predio.
ESPESSURA_DIV = 0.10
CIRCULACAO = 3.00      # folga livre em volta da ilha


def registra_divisoria(nome, eixo, fixo, s0, s1, espessura=ESPESSURA_DIV):
    """Registra as duas faces de uma divisoria como faces virtuais do salao."""
    faces = []
    for lado, sinal in (("a", -1), ("b", +1)):
        chave = f"{nome}_{lado}"
        FL.FACES[chave] = dict(eixo=eixo, fixo=fixo + sinal * espessura / 2,
                               s0=s0, s1=s1, dentro=sinal)
        faces.append(chave)
    return faces


def ilha_rect(eixo, fixo, s0, s1, espessura=ESPESSURA_DIV, folga=0.0):
    meia = espessura / 2 + PROF + folga
    if eixo == "h":
        return (s0 - folga, fixo - meia, s1 + folga, fixo + meia)
    return (fixo - meia, s0 - folga, fixo + meia, s1 + folga)


def roda_com_divisorias(cenario, hipotese, a_min, divisorias, a_max=CORREDOR_MAX,
                        avulsa_em=AVULSA_EM, faixa_leste=True):
    base = roda(cenario, hipotese, a_min, a_max, ordem=ORDEM, avulsa_em=avulsa_em,
                faixa_leste=faixa_leste)
    cortes, _ = bloqueios(cenario, hipotese, faixa_leste=faixa_leste)
    modulos = list(base["modulos"])
    obst = [(rect_do_modulo(m), "faixa de perímetro") for m in modulos] \
        + list(base["proibidos"])

    detalhe = []
    for d in divisorias:
        faces = registra_divisoria(d["nome"], d["eixo"], d["fixo"], d["s0"], d["s1"])
        halo = ilha_rect(d["eixo"], d["fixo"], d["s0"], d["s1"], folga=CIRCULACAO)
        conflitos = sorted({mo for r, mo in obst if FL.sobrepoe(halo, r)})
        n_face = []
        for face in faces:
            mods, _ = empacota(face, cortes, a_min, a_max, obst)
            modulos += mods
            n_face.append(len(mods))
            for m in mods:
                obst.append((rect_do_modulo(m), f"faixa~{face}"))
        detalhe.append(dict(**d, mrv=sum(n_face), faces=n_face,
                            comprimento=round(d["s1"] - d["s0"], 2),
                            conflitos_de_circulacao=conflitos))

    return dict(cenario=cenario, hipotese=hipotese, a_min=a_min,
                mrv=len(modulos), perimetro=base["mrv"], por_face=base["por_face"],
                divisorias=detalhe, modulos=modulos, proibidos=base["proibidos"],
                reservas=base["reservas"], choques=base["choques"],
                erros=valida(modulos, base["proibidos"]))


def busca_divisoria(base, eixo="h", passo=0.5, a_min=CORREDOR_MIN,
                    a_max=CORREDOR_MAX):
    """Procura a divisoria exenta que mais rende sem encostar em nada."""
    ocupado = [(rect_do_modulo(m), "faixa") for m in base["modulos"]] \
        + list(base["proibidos"])

    def livre(r):
        return FL.dentro_do_salao(r) and not any(
            FL.sobrepoe(r, o) for o, _ in ocupado)

    melhor = None
    lim_f = FL.HALL_H if eixo == "h" else FL.HALL_W
    lim_s = FL.HALL_W if eixo == "h" else FL.HALL_H
    f = passo
    while f < lim_f:
        s = 0.0
        while s < lim_s:
            e = lim_s
            while e > s and not livre(ilha_rect(eixo, f, s, e, folga=CIRCULACAO)):
                e -= passo
            L = e - s
            if L > 0:
                n, _, _ = pares_no_trecho(L, a_min, a_max)
                cand = (4 * n, -L, eixo, f, s, e)
                if n and (melhor is None or cand[:2] > melhor[:2]):
                    melhor = cand
            s += passo
        f += passo
    return melhor


def teto_com_divisorias(cenario, hipotese, a_min, maximo=6):
    """Quantas mesas caberiam se o miolo fosse todo loteado com divisorias."""
    escolhidas = []
    est = roda(cenario, hipotese, a_min, ordem=ORDEM)
    while len(escolhidas) < maximo:
        melhor = None
        for eixo in ("h", "v"):
            c = busca_divisoria(est, eixo=eixo, a_min=a_min)
            if c and (melhor is None or c[0] > melhor[0]):
                melhor = c
        if not melhor or melhor[0] == 0:
            break
        _, _, eixo, fixo, s0, s1 = melhor
        escolhidas.append(dict(nome=f"E{len(escolhidas) + 1}", eixo=eixo,
                               fixo=fixo, s0=s0, s1=s1))
        est = roda_com_divisorias(cenario, hipotese, a_min, escolhidas)
        if est["erros"]:
            escolhidas.pop()
            break
    return est, escolhidas


if __name__ == "__main__":
    print(f"Modulo: {LARG:.2f} m de largura x {PROF:.2f} m de profundidade")
    apertado = passo_do_par(CORREDOR_MIN, ENTRE_PARES_MIN)
    folgado = passo_do_par(CORREDOR_MAX, ENTRE_PARES_MAX)
    print(f"Passo do par: {apertado:.2f} m (2,50 / 1,00)  "
          f"{folgado:.2f} m (3,00 / 1,50)")
    print(f"Parede por mesa: {apertado/2:.2f} a {folgado/2:.2f} m")
    print(f"Para {URNAS} urnas: {URNAS*apertado/2:.1f} a {URNAS*folgado/2:.1f} m "
          f"de parede util\n")
    for cen in ("A", "B"):
        for hip in HIPOTESES:
            for a in (CORREDOR_MIN, CORREDOR_MAX):
                r = roda(cen, hip, a, ordem=ORDEM)
                det = " ".join(f"{k[:3]}={v['mrv']}" for k, v in r["por_face"].items()
                               if v["mrv"])
                print(f"  cenario {cen} · recuo {hip:9s} · A>={a:.2f} -> "
                      f"{r['mrv']:2d} MRV   {det}"
                      + ("   ERROS: " + "; ".join(r["erros"]) if r["erros"] else ""))
