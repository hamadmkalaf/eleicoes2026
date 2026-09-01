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

CORREDOR_MIN, CORREDOR_MAX = 2.50, 3.00    # A, faixa dada pelo usuario
ENTRE_PARES = 1.50                          # B

URNAS = 28


def passo_do_par(a):
    return 2 * LARG + a + ENTRE_PARES


def pares_no_trecho(L, a_min=CORREDOR_MIN, a_max=CORREDOR_MAX):
    """Maximo de pares num trecho livre de L metros, e o corredor resultante
    depois de distribuir a sobra ate a_max."""
    n = int(math.floor((L + ENTRE_PARES) / passo_do_par(a_min) + 1e-9))
    if n <= 0:
        return 0, 0.0, L
    a = min(a_max, (L + ENTRE_PARES) / n - (2 * LARG + ENTRE_PARES))
    return n, a, L - (n * passo_do_par(a) - ENTRE_PARES)


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

CARGA = {"carga oeste": "S1", "carga leste": "S7"}
ORDEM = ["norte", "recorte_h", "oeste", "sul", "leste", "recorte_v"]


def _numero(codigo):
    """Numero de fachada de uma porta, a partir do codigo do RDS."""
    for p in PB.numera():
        if p["codigo"] == codigo.split(" (")[0]:
            return p["num"]
    return codigo


def bloqueios(cenario, hipotese):
    """Cortes ao longo de cada face e retangulos proibidos no piso."""
    cortes = {f: [] for f in FL.FACES}
    rects = []

    for face in FL.FACES:
        for codigo, a, b in FL.portas_da_face(face):
            num = _numero(codigo)
            emerg = (codigo in FL.EMERGENCIA
                     and (face == "leste" or hipotese == "prudente")
                     and num != "N1")          # N1 esta fechada: nao e vao

            if emerg:
                r = FL.RECUO_EMERGENCIA
                rects.append((FL.recuo_da_porta(face, a, b),
                              f"{num} · recuo de emergência"))
                cortes[face].append((a - r, b + r, f"{num} recuo"))
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


def empacota(face, cortes, a_min, a_max, obstaculos=()):
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
        n, corredor, sobra = pares_no_trecho(L, a_min, a_max)
        trechos.append(dict(s0=round(a, 2), s1=round(b, 2), livre=round(L, 2),
                            pares=n, corredor=round(corredor, 2) if n else None,
                            sobra=round(sobra, 2)))
        s = a + sobra / 2          # centra o conjunto no trecho
        for i in range(n):
            par = f"{face}|{a:.2f}|{i}"
            modulos.append(dict(face=face, s=s + LARG / 2, corredor=corredor,
                                lado="a", par=par))
            modulos.append(dict(face=face, s=s + LARG + corredor + LARG / 2,
                                corredor=corredor, lado="b", par=par))
            s += passo_do_par(corredor)
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
         ordem=None, extras=()):
    """Perimetro. As faces sao processadas em ordem: cada faixa ja montada vira
    obstaculo para as seguintes, o que resolve os cantos — duas faces vizinhas
    nao podem ocupar o mesmo quadrado de PROF x PROF, e quem vem primeiro fica
    com ele."""
    cortes, rects = bloqueios(cenario, hipotese)
    proibidos = list(rects) + vaos_proibidos() + list(extras)

    obst = list(proibidos)
    modulos, por_face = [], {}
    for face in (ordem or ORDEM):
        mods, trechos = empacota(face, cortes, a_min, a_max, obst)
        modulos += mods
        por_face[face] = dict(mrv=len(mods), pares=len(mods) // 2, trechos=trechos)
        for m in mods:
            obst.append((rect_do_modulo(m), f"faixa~{face}"))

    return dict(cenario=cenario, hipotese=hipotese, a_min=a_min,
                mrv=len(modulos), por_face=por_face, modulos=modulos,
                proibidos=proibidos, reservas=rects,
                erros=valida(modulos, proibidos), choques=choques(rects))


def sombras(cenario, hipotese, a_min, ordem=None):
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
        mods, _ = empacota(face, cortes, a_min, CORREDOR_MAX, obst)
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


def roda_com_divisorias(cenario, hipotese, a_min, divisorias, a_max=CORREDOR_MAX):
    base = roda(cenario, hipotese, a_min, a_max, ordem=ORDEM)
    cortes, _ = bloqueios(cenario, hipotese)
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
    print(f"Passo do par: {passo_do_par(CORREDOR_MIN):.2f} m (A=2,50)  "
          f"{passo_do_par(CORREDOR_MAX):.2f} m (A=3,00)")
    print(f"Parede por mesa: {passo_do_par(CORREDOR_MIN)/2:.2f} a "
          f"{passo_do_par(CORREDOR_MAX)/2:.2f} m")
    print(f"Para {URNAS} urnas: {URNAS*passo_do_par(CORREDOR_MIN)/2:.1f} a "
          f"{URNAS*passo_do_par(CORREDOR_MAX)/2:.1f} m de parede util\n")
    for cen in ("A", "B"):
        for hip in HIPOTESES:
            for a in (CORREDOR_MIN, CORREDOR_MAX):
                r = roda(cen, hip, a, ordem=ORDEM)
                det = " ".join(f"{k[:3]}={v['mrv']}" for k, v in r["por_face"].items()
                               if v["mrv"])
                print(f"  cenario {cen} · recuo {hip:9s} · A>={a:.2f} -> "
                      f"{r['mrv']:2d} MRV   {det}"
                      + ("   ERROS: " + "; ".join(r["erros"]) if r["erros"] else ""))
