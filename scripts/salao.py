"""Nucleo comum do desenho de fluxo do posto de Dublin — RDS Hall 2.

Reune o que nao depende de qual layout se esta testando: a geometria do salao
medida da planta oficial, as premissas de comparecimento e de mobiliario, a
carga de cada urna e a simulacao de fila. Cada ideia de layout importa daqui.

A geometria foi medida diretamente dos PDFs do RDS — `RDS_Hall_2_Floorplan_(1).pdf`
(pagina 2) e a versao revisada que assinala as duas portas de carga. A escala de
8,69 pt/m foi aferida contra a ficha tecnica impressa no proprio documento:
50,2 m x 44,5 m, 2.238 m2. Origem (0,0) = canto sudoeste util do salao; x cresce
para leste, y para norte, em metros.
"""
import json, math, os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------------------------------------------------------------- premissas
TAXA_DUBLIN, TAXA_INTERIOR = 0.74, 0.50   # comparecimento observado em 2022
SEG_POR_VOTO = 55                          # ponto de projeto das baias de fila
ABERTURA, FECHAMENTO = 8, 17
PERFIL = [.08, .13, .15, .14, .12, .11, .10, .09, .08]  # chegadas por hora
AREA_PESSOA = 1.0        # m2 por pessoa em fila serpenteada com balizadores
FOLGA_BAIA = 0.6         # m de balizador entre baias vizinhas

# Modulo da MRV, medido a partir do mobiliario real: mesa dos mesarios de
# 1,60 x 0,70 m ao lado da mesa redonda da urna, de 0,90 m de diametro, mais a
# estrutura que fecha o fundo e as laterais. A urna fica girada 90 graus em
# relacao a mesa, com a tela voltada para o painel lateral do modulo — ou seja,
# perpendicular tanto a fila quanto ao corredor de retorno.
MOD_LARGURA, MOD_PROFUND = 2.80, 1.90
LARG_MIN_BAIA = MOD_LARGURA + 0.40   # modulo + balizador

# Recuo minimo entre qualquer secao e uma saida de emergencia.
RECUO_EMERGENCIA = 3.0

# ------------------------------------------------------- geometria do salao
HALL_W, HALL_H = 50.3, 44.4
RECORTE = (0.0, 0.0, 7.8, 7.0)      # canto sudoeste suprimido do salao

# As duas portas de carga da parede sul (medidas nas quinas assinaladas na
# planta revisada do RDS) tem 3,6 m de vao e ficam nas extremidades da fachada.
PORTA_CARGA_O = (7.83, 11.45)
PORTA_CARGA_L = (45.12, 48.75)

PORTAS = {
    "sul":   [("carga oeste", *PORTA_CARGA_O), ("2.7", 17.22, 18.47),
              ("2.5/2.6", 19.10, 25.03), ("2.4", 25.32, 31.25),
              ("2.2/2.3", 31.54, 37.47), ("2.1", 38.09, 39.36),
              ("carga leste", *PORTA_CARGA_L)],
    "norte": [("2.13", 7.41, 9.44), ("2.14/2.15", 20.66, 24.22)],
    "leste": [("2.22/2.23", 2.95, 6.01), ("2.20/2.21", 14.80, 17.87),
              ("2.18/2.19", 26.66, 29.72), ("2.16/2.17", 38.51, 41.57)],
    "oeste": [("2.10/2.11 (WC)", 19.36, 22.43), ("acesso Hall 1", 36.80, 38.50)],
}
# As saidas 2.8/2.9 ficam na parede do recorte sudoeste, medidas no PDF a 3,0 e
# 6,5 m do canto sul. Ficam fora de PORTAS e da numeracao das fachadas — a
# parede do recorte nao e fachada —, mas entram na geometria: o recuo delas cai
# dentro do salao e disputa chao com a fachada sul.
PORTA_RECORTE = ("2.8/2.9", 3.0, 6.5)

ENTRADA_A = (sum(PORTA_CARGA_O) / 2, 0.0)    # porta de carga oeste
ENTRADA_B = (sum(PORTA_CARGA_L) / 2, 0.0)    # porta de carga leste
SAIDA = (28.29, 0.0)                          # baia central 2.4

ENTRADA_ZONA = {"A": ENTRADA_A, "B": ENTRADA_B}


# ------------------------------------------------------------ faces do salao
# As quatro fachadas mais as duas faces do recorte sudoeste. Cada face tem uma
# coordenada fixa e um intervalo na outra; `dentro` e o sinal da normal que
# aponta para o interior do salao. `s` e a coordenada corrente da face — x nas
# horizontais, y nas verticais —, a mesma em que as portas estao medidas.
FACES = {
    "norte":     dict(eixo="h", fixo=HALL_H,    s0=0.0,         s1=HALL_W, dentro=-1),
    "leste":     dict(eixo="v", fixo=HALL_W,    s0=0.0,         s1=HALL_H, dentro=-1),
    "sul":       dict(eixo="h", fixo=0.0,       s0=RECORTE[2],  s1=HALL_W, dentro=+1),
    "oeste":     dict(eixo="v", fixo=0.0,       s0=RECORTE[3],  s1=HALL_H, dentro=+1),
    "recorte_v": dict(eixo="v", fixo=RECORTE[2], s0=0.0,        s1=RECORTE[3], dentro=+1),
    "recorte_h": dict(eixo="h", fixo=RECORTE[3], s0=0.0,        s1=RECORTE[2], dentro=+1),
}

# Portas que constam como saida de emergencia na planta do RDS, pelo codigo do
# RDS. So as quatro da parede leste tiveram o recuo de 3 m determinado; para as
# demais a exigencia esta em aberto (questao 3 do contexto).
EMERGENCIA = {"2.16/2.17", "2.18/2.19", "2.20/2.21", "2.22/2.23",
              "2.13", "2.7", "2.1", "2.8/2.9"}

CONTORNO = [(RECORTE[2], 0.0), (HALL_W, 0.0), (HALL_W, HALL_H), (0.0, HALL_H),
            (0.0, RECORTE[3]), (RECORTE[2], RECORTE[3])]


def portas_da_face(face):
    """[(codigo, a, b)] de uma face, incluida a do recorte."""
    if face == "recorte_v":
        return [PORTA_RECORTE]
    return list(PORTAS.get(face, []))


def retangulo_na_parede(face, s_a, s_b, profundidade):
    """Retangulo (x0, y0, x1, y1) encostado na face, do trecho [s_a, s_b] ate
    `profundidade` metros para dentro do salao."""
    f = FACES[face]
    fixo, d = f["fixo"], f["dentro"]
    if f["eixo"] == "h":
        y_a, y_b = sorted((fixo, fixo + d * profundidade))
        return (s_a, y_a, s_b, y_b)
    x_a, x_b = sorted((fixo, fixo + d * profundidade))
    return (x_a, s_a, x_b, s_b)


def recuo_da_porta(face, a, b, recuo=RECUO_EMERGENCIA):
    """Zona livre exigida por uma saida de emergencia: `recuo` metros para
    dentro do salao e `recuo` metros para cada lado do vao."""
    f = FACES[face]
    return retangulo_na_parede(face, max(f["s0"], a - recuo),
                               min(f["s1"], b + recuo), recuo)


def sobrepoe(r1, r2, tol=1e-9):
    return (r1[0] < r2[2] - tol and r2[0] < r1[2] - tol and
            r1[1] < r2[3] - tol and r2[1] < r1[3] - tol)


def dentro_do_salao(r, tol=1e-6):
    """O retangulo cabe no contorno do Hall 2 — retangulo menos o recorte?"""
    x0, y0, x1, y1 = r
    if x0 < -tol or y0 < -tol or x1 > HALL_W + tol or y1 > HALL_H + tol:
        return False
    return not sobrepoe(r, RECORTE)


def subtrai(intervalos, corte):
    """Remove o intervalo `corte` de uma lista de intervalos [(a, b), ...]."""
    ca, cb = corte
    saida = []
    for a, b in intervalos:
        if cb <= a or ca >= b:
            saida.append((a, b))
            continue
        if a < ca:
            saida.append((a, ca))
        if cb < b:
            saida.append((cb, b))
    return [(a, b) for a, b in saida if b - a > 1e-9]


def carrega_urnas():
    with open(os.path.join(RAIZ, "saidas", "dados.json"), encoding="utf-8") as f:
        d = json.load(f)
    res = {r["Urna"]: r for r in d["residencia_urna"]}
    urnas = []
    for u in d["urnas"]:
        r = res[u["Urna"]]
        dub, tot = r["DUBLIN"], r["TOTAL"]
        fora = sorted(((k, v) for k, v in r.items()
                       if k not in ("Urna", "TOTAL", "DUBLIN") and v),
                      key=lambda kv: -kv[1])
        urnas.append({
            "urna": u["Urna"],
            "secoes": [int(s) for s in (u["Secao_principal"], u["Secao_agregada"])
                       if s == s and s],
            "aptos": tot, "aptos_dublin": dub, "aptos_interior": tot - dub,
            "origem_interior": fora[0][0].title() if fora else None,
            "esperado": round(TAXA_DUBLIN * dub + TAXA_INTERIOR * (tot - dub)),
        })
    return urnas


def simula_fila(esperado, seg_por_voto=SEG_POR_VOTO, passo=5):
    """Fila minuto a minuto. Devolve (pico, hora do pico, encerramento efetivo)."""
    por_passo = [esperado * s / (60 / passo) for s in PERFIL for _ in range(60 // passo)]
    atende = passo * 60 / seg_por_voto
    fila = pico = 0.0
    t_pico = 0
    for i, chega in enumerate(por_passo):
        fila += chega
        fila -= min(fila, atende)
        if fila > pico:
            pico, t_pico = fila, i
    extra = 0
    while fila > 0.01 and extra < 600:
        fila -= min(fila, atende)
        extra += passo
    return math.ceil(pico), ABERTURA + t_pico * passo / 60, FECHAMENTO + extra / 60


def largura_exigida(fila, prof_max):
    """Largura de parede que a baia de fila daquela urna precisa ocupar."""
    if fila <= 0:
        return LARG_MIN_BAIA
    return max(LARG_MIN_BAIA, fila * AREA_PESSOA / prof_max + FOLGA_BAIA)


def classe(u):
    if u["esperado"] >= 550:
        return "critica"
    if u["esperado"] >= 450:
        return "alta"
    if u["esperado"] >= 360:
        return "media"
    return "leve"



def capacidade_de_parede(recuo=RECUO_EMERGENCIA, frente=None, incluir_sul=False,
                         cantos=1.5):
    """Quantas MRVs cabem no perimetro do salao sob dadas premissas.

    Usa-se para responder a pergunta que decide entre um layout em ilhas e um
    layout todo encostado nas paredes. `recuo` pode ser um numero (o mesmo para
    todas as saidas de emergencia) ou um dicionario {parede: recuo}. `frente` e
    a largura que cada MRV ocupa de parede; por omissao, o modulo mais o
    balizador. Devolve (trechos, total_de_metros, total_de_posicoes), em que
    cada trecho e (parede, inicio, fim, comprimento, posicoes).
    """
    frente = frente or LARG_MIN_BAIA
    limites = {"norte": (cantos, HALL_W - cantos),
               "oeste": (RECORTE[3] + cantos, HALL_H - cantos),
               "leste": (cantos, HALL_H - cantos),
               "sul":   (RECORTE[2] + cantos, HALL_W - cantos)}
    trechos, metros, posicoes = [], 0.0, 0
    for parede, (lo, hi) in limites.items():
        if parede == "sul" and not incluir_sul:
            continue
        r = recuo[parede] if isinstance(recuo, dict) else recuo
        livre = [(lo, hi)]
        for _, a, b in PORTAS[parede]:
            novo = []
            for x0, x1 in livre:
                if b + r <= x0 or a - r >= x1:
                    novo.append((x0, x1))
                    continue
                if x0 < a - r:
                    novo.append((x0, a - r))
                if b + r < x1:
                    novo.append((b + r, x1))
            livre = novo
        for x0, x1 in livre:
            n = int((x1 - x0) // frente)
            trechos.append((parede, round(x0, 2), round(x1, 2),
                            round(x1 - x0, 2), n))
            metros += x1 - x0
            posicoes += n
    return trechos, round(metros, 1), posicoes


if __name__ == "__main__":
    urnas = carrega_urnas()
    for u in urnas:
        u["fila_pico"] = simula_fila(u["esperado"])[0]
    print(f"{len(urnas)} urnas · {sum(u['aptos'] for u in urnas)} aptos · "
          f"{sum(u['esperado'] for u in urnas)} esperados")
    print(f"\nCapacidade de parede (modulo de {MOD_LARGURA} m + balizador = "
          f"{LARG_MIN_BAIA} m de frente):")
    for rot, kw in (("recuo de 3 m em todas as saidas", {}),
                    ("recuo de 3 m so nas saidas 2.16-2.23 (parede leste)",
                     {"recuo": {"leste": 3.0, "norte": 0.6, "oeste": 0.6, "sul": 0.6}}),
                    ("recuo de 3 m, modulo em linha de 1,80 m de frente",
                     {"frente": 2.2})):
        _, m, n = capacidade_de_parede(**kw)
        print(f"  {rot:<52} {m:6.1f} m  ->  {n:2d} posicoes de 28")
