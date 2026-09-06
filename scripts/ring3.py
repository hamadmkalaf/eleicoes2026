#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ring 3 — a fila externa do Hall 2, em duas geometrias.

Este script modela o compound de fila ao ar livre (o Ring 3 do RDS, ~39 x 35 m,
14 m ao sul da fachada) em dois desenhos e produz, para cada um, a capacidade
de pessoas e o consumo de separadores de fila:

  V  serpenteados verticais  — raias norte-sul, tres blocos lado a lado.
                               E o desenho original (`saidas/plano_ring3.md`,
                               produzido em sessao anterior e nao versionado);
                               aqui ele e reconstruido a partir das cotas
                               publicadas na pagina "Rota do Eleitor".
  H  serpenteados horizontais — raias leste-oeste, tres decks empilhados em
                               profundidade, cada um com porta propria.

As duas geometrias sao medidas com o MESMO modelo (mesma densidade, mesmo
modulo de raia, mesma regra de barreira), que e a unica forma de a comparacao
valer alguma coisa. Onde o desenho original nao pode ser recuperado, o
parametro esta marcado como RECONSTRUIDO e o teste de aderencia esta em
`confere_baseline()`.

Saidas: saidas/ring3.json, saidas/plano_ring3_horizontal.md,
        saidas/ring3_horizontal.svg, saidas/ring3_vertical.svg
"""

from __future__ import annotations

import json
import math
import os
from dataclasses import dataclass, field, asdict

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAIDAS = os.path.join(RAIZ, "saidas")

# --------------------------------------------------------------------------
# 1. Geometria herdada — vem de scripts/salao.py e das decisoes do Posto,
#    replicadas aqui porque aqueles arquivos nao estao neste repositorio.
#    Coordenadas em metros, origem no canto sudoeste do salao, y para o norte.
#    A fachada sul do Hall 2 e y = 0; o Ring 3 fica ao sul dela (y negativo).
# --------------------------------------------------------------------------
RING = {"x0": 8.79, "x1": 47.78, "y0": -49.0, "y1": -14.0}   # 39,0 x 35,0 m
APRON = 14.0                                                  # y1 do ring ate a fachada

PORTAS = {                       # vaos de entrada na fachada sul
    "A": {"porta": "S4", "x0": 19.10, "x1": 25.03},
    "B": {"porta": "S5", "x0": 25.32, "x1": 31.25},
    "C": {"porta": "S6", "x0": 31.54, "x1": 37.47},
}
SAIDAS_FACHADA = {"S2": (13.25, 14.45), "S8": (42.12, 43.32)}

# comparecimento esperado por entrada (decisoes do Posto, base B de 2022)
ESPERADO = {"A": 3642, "B": 4215, "C": 3642}
ESPERADO_TOTAL = sum(ESPERADO.values())

# --------------------------------------------------------------------------
# 2. Premissas do modelo de fila. As quatro primeiras sao RECONSTRUIDAS: sao
#    os valores que reproduzem exatamente os 855 (serpenteados) e 547 (baias)
#    do plano original — ver confere_baseline().
# --------------------------------------------------------------------------
PASSO_RAIA = 1.40      # modulo da raia, eixo a eixo da barreira
RAIA_UTIL = 1.20       # largura livre de caminhada dentro da raia
DENS_FILA = 2.00       # pessoas/m2 em raia de fila, em pe, sob guarda-chuva
DENS_BAIA = 1.80       # pessoas/m2 em baia de espera (precisa de circulacao)
VAO_RETORNO = 1.20     # folga de meia-volta na ponta de cada raia
LARG_TUBO = 1.60       # corredor de saida que atravessa um deck da frente
LARG_ESPINHA = 3.00    # corredor de distribuicao encostado no gradil
FUNIL_GARGANTA = 12.0  # comprimento do funil de pre-triagem na garganta sudeste

SEPARADOR_M = 2.00     # 1 separador de fila = 2 m de barreira
SEPARADOR_EUR = 13.02  # EUR 1.303,00 / 100 unidades (item d do orcamento)
ESTOQUE_SEPARADORES = 200   # fornecidos pela organizadora (400 m)
COMPRA_PLANO_V = 100        # o que o plano vertical ja previa comprar

# capacidade em pessoas por metro de raia
POR_METRO_RAIA = RAIA_UTIL * DENS_FILA


# --------------------------------------------------------------------------
# 3. Primitivas de medida
# --------------------------------------------------------------------------
def cap_raias(n: int, comp: float) -> float:
    """Pessoas que cabem em n raias de `comp` metros."""
    return n * comp * POR_METRO_RAIA


def barreira_serpenteado(n: int, comp: float) -> float:
    """Metros de barreira de um serpenteado de n raias de `comp` metros.

    Sao n+1 corridas longitudinais. As duas externas vao inteiras; cada uma das
    n-1 divisorias internas para antes da ponta para abrir a meia-volta.
    """
    if n <= 0:
        return 0.0
    return 2 * comp + (n - 1) * max(0.0, comp - VAO_RETORNO)


def cap_area(area: float, dens: float = DENS_BAIA) -> float:
    return area * dens


def unidades(metros: float) -> int:
    return math.ceil(metros / SEPARADOR_M)


@dataclass
class Bloco:
    """Um serpenteado: n raias de um comprimento."""
    nome: str
    raias: int
    comp: float

    @property
    def capacidade(self) -> float:
        return cap_raias(self.raias, self.comp)

    @property
    def barreira(self) -> float:
        return barreira_serpenteado(self.raias, self.comp)

    @property
    def prof(self) -> float:
        return self.raias * PASSO_RAIA

    @property
    def caminhada(self) -> float:
        return self.raias * self.comp


@dataclass
class Desenho:
    codigo: str
    nome: str
    resumo: str
    blocos: list = field(default_factory=list)     # Bloco por entrada
    baias: dict = field(default_factory=dict)      # entrada -> (rotulo, area)
    barreira: dict = field(default_factory=dict)   # componente -> metros
    geometria: dict = field(default_factory=dict)  # para o desenho SVG
    notas: list = field(default_factory=list)

    # -- capacidade -------------------------------------------------------
    @property
    def cap_raias_total(self) -> float:
        return sum(b.capacidade for b in self.blocos)

    @property
    def cap_baias_total(self) -> float:
        return sum(cap_area(a) for _, a in self.baias.values())

    @property
    def capacidade(self) -> float:
        return self.cap_raias_total + self.cap_baias_total

    def cap_por_entrada(self) -> dict:
        fora = {}
        for b in self.blocos:
            baia = self.baias.get(b.nome)
            fora[b.nome] = b.capacidade + (cap_area(baia[1]) if baia else 0.0)
        return fora

    # -- barreira ---------------------------------------------------------
    @property
    def barreira_total(self) -> float:
        return sum(self.barreira.values())

    @property
    def separadores(self) -> int:
        return unidades(self.barreira_total)

    @property
    def compra(self) -> int:
        return max(0, self.separadores - ESTOQUE_SEPARADORES)

    @property
    def custo_compra(self) -> float:
        return self.compra * SEPARADOR_EUR

    @property
    def m_por_pessoa(self) -> float:
        return self.barreira_total / self.capacidade

    def equilibrio(self) -> dict:
        """Capacidade por eleitor esperado, entrada a entrada."""
        cap = self.cap_por_entrada()
        return {e: cap[e] / ESPERADO[e] for e in cap}


# --------------------------------------------------------------------------
# 4. Desenho V — serpenteados verticais (reconstrucao do plano original)
# --------------------------------------------------------------------------
def desenho_vertical() -> Desenho:
    """Tres blocos lado a lado, raias norte-sul, baias nos dois flancos.

    Cotas lidas do diagrama publicado na pagina "Rota do Eleitor": blocos de
    4,2 / 12,6 / 4,2 m de largura (3 / 9 / 3 raias de 1,4 m), 23,75 m de raia,
    corredor de distribuicao de 3,0 m ao sul e baias de 6,4 m nos flancos.
    """
    comp = 23.75
    blocos = [Bloco("A", 3, comp), Bloco("B", 9, comp), Bloco("C", 3, comp)]

    larg_baia = 6.40
    baias = {
        "A": ("baia do flanco oeste", larg_baia * comp),
        "C": ("baia do flanco leste", larg_baia * comp),
    }

    # posicoes (para o desenho): blocos centrados no eixo do Ring, nao nas portas
    x_blocos = {"A": (15.16, 19.36), "B": (22.09, 34.69), "C": (37.19, 41.39)}
    y_serp = (RING["y1"] - comp, RING["y1"])          # -37,75 .. -14,00
    corredor_comp = 36.70
    y_corr = (y_serp[0] - LARG_ESPINHA, y_serp[0])

    # raias descarregam em diagonal sobre as portas: o percurso no apron vai do
    # eixo do bloco ate o eixo da porta
    apron = 0.0
    diagonais = {}
    for b in blocos:
        xb = sum(x_blocos[b.nome]) / 2
        xp = (PORTAS[b.nome]["x0"] + PORTAS[b.nome]["x1"]) / 2
        d = math.hypot(APRON, xp - xb)
        diagonais[b.nome] = d
        apron += 2 * d

    barreira = {
        "serpenteados": sum(b.barreira for b in blocos),
        "corredor de distribuição (2 lados)": 2 * corredor_comp,
        "fechamento das baias de flanco": 2 * (2 * larg_baia),
        "raias do apron até as portas": apron,
        "funil da garganta sudeste": 2 * FUNIL_GARGANTA,
    }

    d = Desenho(
        codigo="V",
        nome="Serpenteados verticais (plano original, reconstruido)",
        resumo="Tres blocos lado a lado com raias norte-sul; baias de espera "
               "nos dois flancos do Ring; descarga em diagonal sobre as portas.",
        blocos=blocos,
        baias=baias,
        barreira=barreira,
        geometria={"x_blocos": x_blocos, "y_serp": y_serp, "y_corr": y_corr,
                   "larg_baia": larg_baia, "corredor_comp": corredor_comp,
                   "diagonais": diagonais},
    )
    d.notas = [
        "Descarga em diagonal: nenhum dos três blocos está alinhado com a sua "
        "porta, então as três correntes cruzam o apron obliquamente e se "
        "aproximam entre si até os 6,2 m que separam as portas na fachada.",
        "As baias de flanco caem em frente às portas de saída S2 (oeste) e S8 "
        "(leste): a área de espera fica no caminho de quem já votou.",
    ]
    return d


def confere_baseline(v: Desenho) -> dict:
    """O plano original publicou 855 nos serpenteados e 547 nas baias."""
    return {
        "raias_calculado": round(v.cap_raias_total, 1),
        "raias_publicado": 855,
        "baias_calculado": round(v.cap_baias_total, 1),
        "baias_publicado": 547,
        "total_calculado": round(v.capacidade),
        "total_publicado": 1402,
        "barreira_calculada_m": round(v.barreira_total, 1),
        "barreira_publicada_m": 596.3,
        "separadores_calculado": v.separadores,
        "separadores_publicado": 300,
    }


# --------------------------------------------------------------------------
# 5. Desenho H — serpenteados horizontais
# --------------------------------------------------------------------------
# Regra geometrica que organiza tudo: cada deck e uma faixa horizontal de
# largura quase total do Ring, e os decks se empilham em profundidade. O deck
# da frente (encostado no apron) sai direto pela sua porta; cada deck de tras
# sobe por um tubo alinhado com a SUA porta, e para esse tubo existir os decks
# da frente param antes dele. Dai a escada: quanto mais ao fundo, mais largo o
# deck, e o degrau que sobra a leste vira baia de espera alimentada pela
# espinha.
#
# Ordem forcada pela geometria: a porta do deck da frente tem de ser a mais a
# oeste (A = S4), depois B = S5, depois C = S6 ao fundo.

EIXO_TUBO = {e: (PORTAS[e]["x0"] + PORTAS[e]["x1"]) / 2 for e in PORTAS}
FOLGA_TUBO = 0.20      # folga entre a borda leste de um deck e o tubo vizinho


def limites_deck() -> dict:
    """Faixa possivel para a borda leste de cada deck."""
    x_espinha = RING["x1"] - LARG_ESPINHA
    return {
        # o portao de saida do deck tem de caber dentro do vao da porta
        "A": (PORTAS["A"]["x0"] + PASSO_RAIA,
              EIXO_TUBO["B"] - LARG_TUBO / 2 - FOLGA_TUBO),
        "B": (PORTAS["B"]["x0"] + PASSO_RAIA,
              EIXO_TUBO["C"] - LARG_TUBO / 2 - FOLGA_TUBO),
        "C": (PORTAS["C"]["x0"] + PASSO_RAIA, x_espinha),
    }


def monta_horizontal(nA: int, nB: int, nC: int,
                     xA: float, xB: float, xC: float) -> Desenho:
    x0 = RING["x0"]
    x_espinha = RING["x1"] - LARG_ESPINHA
    bordas = {"A": xA, "B": xB, "C": xC}
    blocos = [Bloco("A", nA, xA - x0), Bloco("B", nB, xB - x0), Bloco("C", nC, xC - x0)]
    prof = {b.nome: b.prof for b in blocos}

    # baias: o degrau a leste de cada deck, menos os tubos que o atravessam
    tubos_que_cruzam = {"A": ["B", "C"], "B": ["C"], "C": []}
    baias = {}
    for e in ("A", "B", "C"):
        larg = x_espinha - bordas[e]
        area = max(0.0, larg * prof[e] - LARG_TUBO * prof[e] * len(tubos_que_cruzam[e]))
        if area > 1.0:
            baias[e] = (f"baia leste do deck {e}", area)

    # barreira
    barr_tubos = 0.0
    for e, cruzados in (("B", ["A"]), ("C", ["A", "B"])):
        barr_tubos += 2 * sum(prof[c] for c in cruzados)

    prof_total = sum(prof.values())
    barreira = {
        "serpenteados": sum(b.barreira for b in blocos),
        "espinha de distribuição (gradil a leste)": prof_total,
        "tubos de saída dos decks de trás": barr_tubos,
        "fechamento das baias": sum(prof[e] for e in baias),
        "raias do apron até as portas": 3 * 2 * APRON,
        "funil da garganta sudeste": 2 * FUNIL_GARGANTA,
    }

    d = Desenho(
        codigo="H",
        nome="Serpenteados horizontais (decks empilhados)",
        resumo="Tres decks em faixa, raias leste-oeste, empilhados em "
               "profundidade; cada deck sai por um tubo alinhado com a sua "
               "porta e atravessa o apron em linha reta.",
        blocos=blocos,
        baias=baias,
        barreira=barreira,
        geometria={"bordas": bordas, "prof": prof, "x_espinha": x_espinha,
                   "eixo_tubo": EIXO_TUBO, "prof_total": prof_total},
    )
    return d


def campo_profundidade() -> float:
    """Profundidade util para os decks: o Ring menos a faixa de triagem."""
    return RING["y1"] - RING["y0"] - FAIXA_TRIAGEM


FAIXA_TRIAGEM = 8.75   # faixa sul reservada a garganta e a pre-triagem (igual a V)




def larguras_maximas() -> dict:
    """Borda leste de cada deck no maximo que a geometria permite.

    Deck largo = mais fila medida em raia e menos massa parada em baia, que e
    a troca que interessa: raia e fila ordenada e contavel, baia e aglomeracao.
    """
    return {e: lim[1] for e, lim in limites_deck().items()}


def desenho_horizontal(raias=(6, 6, 6), bordas=None) -> Desenho:
    """O desenho H com os decks na largura maxima e as raias escolhidas.

    A quantidade de raias por deck e a unica alavanca de dimensionamento: ela
    troca capacidade por barreira quase linearmente (ver `tabela_troca`).
    """
    if bordas is None:
        bordas = larguras_maximas()
    d = monta_horizontal(raias[0], raias[1], raias[2],
                         bordas["A"], bordas["B"], bordas["C"])
    prof = sum(b.prof for b in d.blocos)
    d.geometria["prof_usada"] = prof
    d.geometria["prof_disponivel"] = campo_profundidade()
    d.geometria["faixa_triagem"] = FAIXA_TRIAGEM
    d.notas = [
        "Cada deck sai por um portão dentro do vão da sua própria porta e "
        "cruza o apron em linha reta: as três correntes nunca se aproximam, e "
        "o apron fica livre a oeste de x = 19,1 m e a leste de x = 37,5 m, "
        "que é onde desembocam as saídas S2 e S8.",
        "As baias ficam do lado da chegada, encostadas na espinha, e não ao "
        "lado do meio da fila: enchem como buffer de cauda, antes das raias, "
        "e não como transbordo lateral.",
        "O preço da geometria é o tubo: cada deck de trás gasta duas corridas "
        "de barreira só para atravessar a profundidade dos decks da frente.",
        "A ordem dos decks é imposta, não escolhida: da frente para o fundo, "
        "a porta de cada deck tem de andar para leste (A=S4, B=S5, C=S6), "
        "senão o tubo de um deck de trás cortaria o serpenteado da frente.",
    ]
    return d


def _mede(nA: int, nB: int, nC: int, xA: float, xB: float, xC: float):
    """Versao rapida de monta_horizontal: so os numeros que a busca usa."""
    x0 = RING["x0"]
    x_esp = RING["x1"] - LARG_ESPINHA
    n = (nA, nB, nC)
    x = (xA, xB, xC)
    prof = [k * PASSO_RAIA for k in n]
    comp = [xi - x0 for xi in x]
    cap = [n[i] * comp[i] * POR_METRO_RAIA for i in range(3)]
    cruzam = (2, 1, 0)
    baia = []
    for i in range(3):
        a = max(0.0, (x_esp - x[i]) * prof[i] - LARG_TUBO * prof[i] * cruzam[i])
        baia.append(a if a > 1.0 else 0.0)
    por_entrada = [cap[i] + baia[i] * DENS_BAIA for i in range(3)]
    total = sum(por_entrada)
    barr = sum(barreira_serpenteado(n[i], comp[i]) for i in range(3))
    barr += sum(prof)                                    # espinha
    barr += 2 * prof[0] + 2 * (prof[0] + prof[1])        # tubos de B e de C
    barr += sum(prof[i] for i in range(3) if baia[i])    # fechamento das baias
    barr += 3 * 2 * APRON + 2 * FUNIL_GARGANTA
    return total, por_entrada, math.ceil(barr / SEPARADOR_M)


def tabela_troca() -> list:
    """Capacidade contra separadores, variando so o numero de raias.

    Com os decks na largura maxima, percorre todas as reparticoes de raias que
    cabem na profundidade do Ring e devolve, para cada quantidade de raias, a
    reparticao que melhor equilibra as tres entradas (maior capacidade da
    entrada mais apertada, medida por eleitor esperado dela).
    """
    xm = larguras_maximas()
    n_max = int(campo_profundidade() // PASSO_RAIA)
    por_soma = {}
    for nA in range(2, n_max):
        for nB in range(2, n_max):
            for nC in range(2, n_max):
                soma = nA + nB + nC
                if soma > n_max:
                    continue
                total, cap, sep = _mede(nA, nB, nC, xm["A"], xm["B"], xm["C"])
                razao = min(cap[i] / ESPERADO[e]
                            for i, e in enumerate(("A", "B", "C")))
                chave = (round(razao, 6), round(total, 1))
                if soma not in por_soma or chave > por_soma[soma][0]:
                    por_soma[soma] = (chave, {
                        "raias": (nA, nB, nC),
                        "raias_total": soma,
                        "capacidade": round(total),
                        "por_entrada": {e: round(cap[i]) for i, e in
                                        enumerate(("A", "B", "C"))},
                        "separadores": sep,
                        "barreira_m": round(sep * SEPARADOR_M, 1),
                        "compra": max(0, sep - ESTOQUE_SEPARADORES),
                        "custo_compra_eur": round(
                            max(0, sep - ESTOQUE_SEPARADORES) * SEPARADOR_EUR, 2),
                    })
    return [por_soma[k][1] for k in sorted(por_soma)]


# --------------------------------------------------------------------------
# 6. Desenho em SVG (escala real, 1 m = ESCALA px)
# --------------------------------------------------------------------------
ESCALA = 14.0
MARGEM = 46.0


def _svg_cabeca(titulo: str) -> tuple:
    larg = (RING["x1"] - RING["x0"] + 12) * ESCALA + 2 * MARGEM
    alt = (RING["y1"] - RING["y0"] + APRON + 6) * ESCALA + 2 * MARGEM
    return larg, alt


def _proj(x: float, y: float) -> tuple:
    """Metros -> px. y cresce para o norte; no SVG, para baixo."""
    px = MARGEM + (x - RING["x0"] + 6) * ESCALA
    py = MARGEM + (2.0 - y) * ESCALA
    return px, py


def _ret(x0, y0, x1, y1, **kw):
    ax, ay = _proj(x0, y1)
    bx, by = _proj(x1, y0)
    at = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in kw.items())
    return (f'<rect x="{ax:.1f}" y="{ay:.1f}" width="{bx - ax:.1f}" '
            f'height="{by - ay:.1f}" {at}/>')


def _txt(x, y, t, size=11, anchor="middle", peso=400, cor="#243244", rot=None):
    px, py = _proj(x, y)
    r = f' transform="rotate({rot} {px:.1f} {py:.1f})"' if rot else ""
    return (f'<text x="{px:.1f}" y="{py:.1f}" text-anchor="{anchor}" '
            f'font-family="ui-sans-serif,system-ui,Helvetica,Arial,sans-serif" '
            f'font-size="{size}" font-weight="{peso}" fill="{cor}"{r}>{t}</text>')


def _linha(x0, y0, x1, y1, **kw):
    ax, ay = _proj(x0, y0)
    bx, by = _proj(x1, y1)
    at = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in kw.items())
    return f'<line x1="{ax:.1f}" y1="{ay:.1f}" x2="{bx:.1f}" y2="{by:.1f}" {at}/>'


CORES = {"A": "#2a78d6", "B": "#e08a00", "C": "#c2185b"}
MARCADOR = ('<defs><marker id="seta" viewBox="0 0 10 10" refX="8" refY="5" '
            'markerWidth="5" markerHeight="5" orient="auto-start-reverse">'
            '<path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker></defs>')


def _moldura(titulo: str, sub: str) -> list:
    """Fachada, apron, gradil do Ring e portas — comum aos dois desenhos."""
    p = []
    p.append(_ret(RING["x0"] - 5, -APRON, RING["x1"] + 5, 0,
                  fill="#eef1f4", stroke="none"))
    p.append(_ret(RING["x0"], RING["y0"], RING["x1"], RING["y1"],
                  fill="#f6f4ef", stroke="#1c2733", stroke_width="2.2"))
    p.append(_linha(RING["x0"] - 5, 0, RING["x1"] + 5, 0,
                    stroke="#1c2733", stroke_width="3"))
    p.append(_txt((RING["x0"] + RING["x1"]) / 2, 1.2,
                  "FACHADA SUL DO HALL 2", 11, peso=700, cor="#5c6c80"))
    for e, d in PORTAS.items():
        p.append(_linha(d["x0"], 0, d["x1"], 0, stroke=CORES[e], stroke_width="6"))
        p.append(_txt((d["x0"] + d["x1"]) / 2, -1.6,
                      f'{d["porta"]} · {e}', 11, peso=700, cor=CORES[e]))
    for nome, (a, b) in SAIDAS_FACHADA.items():
        p.append(_linha(a, 0, b, 0, stroke="#b26a12", stroke_width="6"))
        p.append(_txt((a + b) / 2, -1.6, f"{nome} saída", 9.5, cor="#b26a12"))
    p.append(_txt(RING["x0"] - 4.5, -APRON / 2, "apron pavimentado · 14 m",
                  10, anchor="middle", cor="#5c6c80", rot=-90))
    p.append(_txt(RING["x0"] + 0.4, RING["y0"] + 1.0,
                  "gradil permanente do Ring 3 · 39,0 × 35,0 m",
                  10, anchor="start", cor="#8a919b"))
    return p


def svg_vertical(d: Desenho) -> str:
    larg, alt = _svg_cabeca(d.nome)
    p = _moldura(d.nome, d.resumo)
    g = d.geometria
    y0, y1 = g["y_serp"]
    for b in d.blocos:
        x0, x1 = g["x_blocos"][b.nome]
        p.append(_ret(x0, y0, x1, y1, fill=CORES[b.nome], fill_opacity=".13",
                      stroke=CORES[b.nome], stroke_width="1.4"))
        for i in range(1, b.raias):
            x = x0 + i * PASSO_RAIA
            p.append(_linha(x, y0 + 1.2, x, y1, stroke=CORES[b.nome],
                            stroke_width="1", stroke_opacity=".55"))
        p.append(_txt((x0 + x1) / 2, y1 - 1.6,
                      f"{b.nome} · {b.raias} raias", 11, peso=700, cor=CORES[b.nome]))
        # descarga em diagonal ate a porta
        xp = (PORTAS[b.nome]["x0"] + PORTAS[b.nome]["x1"]) / 2
        p.append(_linha((x0 + x1) / 2, y1, xp, 0, stroke=CORES[b.nome],
                        stroke_width="2", stroke_dasharray="5 3"))
    lb = g["larg_baia"]
    for rot, (xa, xb) in (("baia oeste", (RING["x0"], RING["x0"] + lb)),
                          ("baia leste", (RING["x1"] - lb, RING["x1"]))):
        p.append(_ret(xa, y0, xb, y1, fill="#8a919b", fill_opacity=".16",
                      stroke="#8a919b", stroke_width="1.2", stroke_dasharray="4 3"))
        p.append(_txt((xa + xb) / 2, (y0 + y1) / 2, rot, 10, cor="#5c6c80", rot=-90))
    cy0, cy1 = g["y_corr"]
    p.append(_ret(RING["x0"] + lb, cy0, RING["x1"] - lb, cy1, fill="none",
                  stroke="#5c6c80", stroke_width="1.2"))
    p.append(_txt((RING["x0"] + RING["x1"]) / 2, (cy0 + cy1) / 2 - 0.4,
                  "corredor de distribuição · 3,0 m", 10, cor="#5c6c80"))
    p.append(_txt(RING["x1"] - 6, RING["y0"] + 3.4, "garganta sudeste", 10,
                  anchor="end", cor="#5c6c80"))
    corpo = "\n".join(p)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {larg:.0f} '
            f'{alt:.0f}" width="{larg:.0f}" height="{alt:.0f}" role="img">\n'
            f'<rect width="{larg:.0f}" height="{alt:.0f}" fill="#fbfaf7"/>\n'
            f'{MARCADOR}\n'
            f'{_txt(RING["x0"], 3.4, d.nome, 15, anchor="start", peso=700)}\n'
            f'{corpo}\n</svg>\n')


def svg_horizontal(d: Desenho) -> str:
    larg, alt = _svg_cabeca(d.nome)
    p = _moldura(d.nome, d.resumo)
    g = d.geometria
    x0 = RING["x0"]
    x_esp = g["x_espinha"]
    topo = RING["y1"]
    y = topo
    faixas = {}
    for b in d.blocos:                       # A na frente, C ao fundo
        y_sup, y_inf = y, y - b.prof
        faixas[b.nome] = (y_sup, y_inf)
        xb = g["bordas"][b.nome]
        p.append(_ret(x0, y_inf, xb, y_sup, fill=CORES[b.nome], fill_opacity=".13",
                      stroke=CORES[b.nome], stroke_width="1.4"))
        for i in range(1, b.raias):
            yy = y_sup - i * PASSO_RAIA
            p.append(_linha(x0, yy, xb - 1.2, yy, stroke=CORES[b.nome],
                            stroke_width="1", stroke_opacity=".55"))
        p.append(_txt(x0 + 6.5, y_sup - b.prof / 2,
                      f"deck {b.nome} · {b.raias} raias de {b.comp:.1f} m",
                      11, anchor="start", peso=700, cor=CORES[b.nome]))
        # baia do degrau
        baia = d.baias.get(b.nome)
        if baia:
            p.append(_ret(xb, y_inf, x_esp, y_sup, fill="#8a919b",
                          fill_opacity=".16", stroke="#8a919b",
                          stroke_width="1.2", stroke_dasharray="4 3"))
            p.append(_txt((xb + x_esp) / 2, y_sup - b.prof / 2 - 0.4,
                          f"baia {b.nome}", 10, cor="#5c6c80"))
        y = y_inf - 0.35
    # espinha de distribuicao
    p.append(_ret(x_esp, y, RING["x1"], topo, fill="#5c6c80", fill_opacity=".10",
                  stroke="#5c6c80", stroke_width="1.2"))
    p.append(_txt((x_esp + RING["x1"]) / 2, (y + topo) / 2,
                  "espinha de distribuição", 10, cor="#5c6c80", rot=-90))
    # tubos de saida + raias do apron, sempre perpendiculares
    for b in d.blocos:
        eixo = g["eixo_tubo"][b.nome]
        y_sup = faixas[b.nome][0]
        p.append(_ret(eixo - LARG_TUBO / 2, y_sup, eixo + LARG_TUBO / 2, topo,
                      fill=CORES[b.nome], fill_opacity=".22", stroke=CORES[b.nome],
                      stroke_width="1.2"))
        p.append(_ret(eixo - LARG_TUBO / 2, topo, eixo + LARG_TUBO / 2, 0,
                      fill=CORES[b.nome], fill_opacity=".22", stroke=CORES[b.nome],
                      stroke_width="1.2"))
    p.append(_txt(RING["x1"] - 6, RING["y0"] + 3.4,
                  "garganta sudeste · pré-triagem", 10, anchor="end", cor="#5c6c80"))
    seta = ' marker-end="url(#seta)" stroke-width="2" fill="none"'
    meio = (x_esp + RING["x1"]) / 2
    p.append(_linha(RING["x1"] - 0.6, RING["y0"] + 1.2, meio, RING["y0"] + 6.0,
                    stroke="#5c6c80", stroke_width="2", marker_end="url(#seta)"))
    p.append(_linha(meio, RING["y0"] + 6.4, meio, topo - 2.0, stroke="#5c6c80",
                    stroke_width="2", marker_end="url(#seta)",
                    stroke_dasharray="7 4"))
    for b in d.blocos:
        eixo = g["eixo_tubo"][b.nome]
        p.append(_linha(eixo, faixas[b.nome][0] + 1.0, eixo, -1.2,
                        stroke=CORES[b.nome], stroke_width="2",
                        marker_end="url(#seta)"))
    p.append(_ret(RING["x0"], RING["y0"], RING["x1"], RING["y0"] + FAIXA_TRIAGEM,
                  fill="none", stroke="#8a919b", stroke_width="1",
                  stroke_dasharray="6 4"))
    corpo = "\n".join(p)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {larg:.0f} '
            f'{alt:.0f}" width="{larg:.0f}" height="{alt:.0f}" role="img">\n'
            f'<rect width="{larg:.0f}" height="{alt:.0f}" fill="#fbfaf7"/>\n'
            f'{MARCADOR}\n'
            f'{_txt(RING["x0"], 3.4, d.nome, 15, anchor="start", peso=700)}\n'
            f'{corpo}\n</svg>\n')


# --------------------------------------------------------------------------
# 7. Relatorio
# --------------------------------------------------------------------------
def n(v, casas=0):
    s = f"{v:,.{casas}f}".replace(",", "@").replace(".", ",").replace("@", ".")
    return s


def sinal(v, casas=0):
    return ("+" if v >= 0 else "\u2212") + n(abs(v), casas)


def resumo_json(v: Desenho, h: Desenho, escada: list) -> dict:
    def bloco(d):
        return {
            "codigo": d.codigo,
            "nome": d.nome,
            "capacidade": round(d.capacidade),
            "capacidade_raias": round(d.cap_raias_total),
            "capacidade_baias": round(d.cap_baias_total),
            "por_entrada": {k: round(x) for k, x in d.cap_por_entrada().items()},
            "capacidade_por_eleitor_esperado": {k: round(x, 4)
                                                for k, x in d.equilibrio().items()},
            "barreira_m": round(d.barreira_total, 1),
            "barreira_por_componente_m": {k: round(x, 1)
                                          for k, x in d.barreira.items()},
            "separadores": d.separadores,
            "estoque": ESTOQUE_SEPARADORES,
            "compra": d.compra,
            "custo_compra_eur": round(d.custo_compra, 2),
            "m_por_pessoa": round(d.m_por_pessoa, 3),
            "blocos": [{"entrada": b.nome, "raias": b.raias,
                        "comprimento_m": round(b.comp, 2),
                        "profundidade_m": round(b.prof, 2),
                        "caminhada_m": round(b.caminhada, 1),
                        "capacidade": round(b.capacidade)} for b in d.blocos],
            "baias": {k: {"rotulo": r, "area_m2": round(a, 1),
                          "capacidade": round(cap_area(a))}
                      for k, (r, a) in d.baias.items()},
            "notas": d.notas,
        }
    return {
        "gerado_por": "scripts/ring3.py",
        "ring": RING,
        "apron_m": APRON,
        "premissas": {
            "passo_raia_m": PASSO_RAIA, "raia_util_m": RAIA_UTIL,
            "densidade_fila_p_m2": DENS_FILA, "densidade_baia_p_m2": DENS_BAIA,
            "vao_retorno_m": VAO_RETORNO, "largura_tubo_m": LARG_TUBO,
            "largura_espinha_m": LARG_ESPINHA, "faixa_triagem_m": FAIXA_TRIAGEM,
            "separador_m": SEPARADOR_M, "separador_eur": SEPARADOR_EUR,
            "estoque_separadores": ESTOQUE_SEPARADORES,
            "comparecimento_esperado": ESPERADO,
        },
        "aderencia_ao_plano_original": confere_baseline(v),
        "vertical": bloco(v),
        "horizontal": bloco(h),
        "escada_de_dimensionamento": escada,
    }


def markdown(v: Desenho, h: Desenho, escada: list, enxuta: Desenho) -> str:
    conf = confere_baseline(v)
    eq_v, eq_h = v.equilibrio(), h.equilibrio()
    cv, ch = v.cap_por_entrada(), h.cap_por_entrada()
    L = []
    A = L.append
    A("# Ring 3 — desenho horizontal\n")
    A("Segunda geometria para o compound de fila ao ar livre do RDS (Ring 3, "
      "39,0 × 35,0 m, 14 m ao sul da fachada do Hall 2). O plano vigente "
      "enfileira as pessoas em **serpenteados verticais** — raias norte-sul, "
      "três blocos lado a lado. Este documento desenha a alternativa "
      "**horizontal** — raias leste-oeste, três decks empilhados em "
      "profundidade — e refaz, com o mesmo modelo, as duas contas que mudam: "
      "**capacidade** e **separadores de fila**.\n")

    A("## Resultado em uma linha\n")
    A(f"O horizontal cabe no mesmo Ring e entrega **{n(h.capacidade)} pessoas** "
      f"contra {n(v.capacidade)} do vertical, mas custa "
      f"**{h.separadores} separadores** contra {v.separadores} — "
      f"{n(h.m_por_pessoa, 3)} m de barreira por pessoa contra "
      f"{n(v.m_por_pessoa, 3)} m. Como a capacidade não é o que aperta em "
      "nenhum dos dois, a versão enxuta abaixo "
      f"({'/'.join(str(b.raias) for b in enxuta.blocos)} raias, "
      f"{n(enxuta.capacidade)} pessoas) resolve com **{enxuta.separadores} "
      f"separadores**, abaixo dos {v.separadores} do vertical. O que o "
      "horizontal compra de verdade não é capacidade: é a descarga "
      "perpendicular, uma raia por porta, e o apron limpo em frente às duas "
      "saídas.\n")

    A("## Por que o desenho é este\n")
    A("Empilhar decks em profundidade cria um problema que o vertical não "
      "tem: o deck do fundo precisa atravessar os decks da frente para chegar "
      "à fachada. A solução que organiza tudo o resto é **alinhar cada saída "
      "com a sua porta e fazer os decks da frente pararem antes desse eixo**. "
      "Daí a escada: quanto mais ao fundo, mais largo o deck; o degrau que "
      "sobra a leste vira baia de espera; e a ordem dos decks fica imposta "
      "pela geometria — da frente para o fundo, a porta tem de andar para "
      "leste: **A = S4, B = S5, C = S6**.\n")
    A("Quatro consequências práticas:\n")
    for x in h.notas:
        A(f"- {x}")
    A("")
    A("E o que o vertical tem contra si, medido no mesmo desenho:\n")
    for x in v.notas:
        A(f"- {x}")
    A("")

    A("## Premissas do modelo\n")
    A("| Parâmetro | Valor | Origem |")
    A("|---|---|---|")
    A(f"| Módulo da raia | {n(PASSO_RAIA,2)} m | reconstruído "
      "(4,2 / 12,6 m dos blocos do plano vertical = 3 e 9 raias) |")
    A(f"| Largura livre da raia | {n(RAIA_UTIL,2)} m | reconstruído |")
    A(f"| Densidade em raia | {n(DENS_FILA,1)} pessoas/m² | reconstruído |")
    A(f"| Densidade em baia | {n(DENS_BAIA,1)} pessoas/m² | reconstruído |")
    A(f"| Vão de meia-volta | {n(VAO_RETORNO,1)} m | premissa |")
    A(f"| Separador de fila | {n(SEPARADOR_M,1)} m/unidade · "
      f"EUR {n(SEPARADOR_EUR,2)} | item d do orçamento (100 un. = EUR 1.303) |")
    A(f"| Estoque da organizadora | {ESTOQUE_SEPARADORES} unidades "
      f"({n(ESTOQUE_SEPARADORES*SEPARADOR_M)} m) | plano vertical |")
    A(f"| Comparecimento esperado | A {n(ESPERADO['A'])} · B {n(ESPERADO['B'])} "
      f"· C {n(ESPERADO['C'])} | decisões do Posto, base B de 2022 |")
    A("")
    A("**Aderência ao plano original.** As quatro densidades acima não estão "
      "escritas em lugar nenhum — `scripts/layout_ring3.py` e "
      "`saidas/plano_ring3.md` foram produzidos em sessão anterior e não "
      "chegaram a ser versionados. Foram reconstruídas por ajuste aos números "
      "publicados, e reproduzem-nos exatamente:\n")
    A("| Grandeza | Publicado | Recalculado aqui |")
    A("|---|---|---|")
    A(f"| Capacidade dos serpenteados | {n(conf['raias_publicado'])} | "
      f"{n(conf['raias_calculado'],1)} |")
    A(f"| Capacidade das baias | {n(conf['baias_publicado'])} | "
      f"{n(conf['baias_calculado'],1)} |")
    A(f"| Capacidade total | {n(conf['total_publicado'])} | "
      f"{n(conf['total_calculado'])} |")
    A(f"| Barreira | {n(conf['barreira_publicada_m'],1)} m | "
      f"{n(conf['barreira_calculada_m'],1)} m |")
    A(f"| Separadores | {conf['separadores_publicado']} | "
      f"{conf['separadores_calculado']} |")
    A("")
    A("A capacidade fecha na casa decimal; a barreira fica "
      f"{n((conf['barreira_calculada_m']/conf['barreira_publicada_m']-1)*100,1)}% "
      "acima, porque a regra de contagem de barreira do plano original não é "
      "recuperável a partir do que foi publicado. **A comparação abaixo usa a "
      "regra deste script nos dois desenhos** — é a única forma de ela valer "
      "alguma coisa.\n")

    A("## Capacidade\n")
    A("| | Vertical | Horizontal | Δ |")
    A("|---|---:|---:|---:|")
    A(f"| Em raia (fila medida) | {n(v.cap_raias_total)} | "
      f"{n(h.cap_raias_total)} | {sinal(h.cap_raias_total-v.cap_raias_total)} |")
    A(f"| Em baia (espera) | {n(v.cap_baias_total)} | {n(h.cap_baias_total)} | "
      f"{sinal(h.cap_baias_total-v.cap_baias_total)} |")
    A(f"| **Total** | **{n(v.capacidade)}** | **{n(h.capacidade)}** | "
      f"**{sinal(h.capacidade-v.capacidade)}** |")
    A("")
    A("| Entrada | Esperado | Vertical | por eleitor | Horizontal | por eleitor |")
    A("|---|---:|---:|---:|---:|---:|")
    for e in ("A", "B", "C"):
        A(f"| {e} ({PORTAS[e]['porta']}) | {n(ESPERADO[e])} | {n(cv[e])} | "
          f"{n(eq_v[e],4)} | {n(ch[e])} | {n(eq_h[e],4)} |")
    A("")
    A("O horizontal muda a natureza da capacidade, não só o total: no "
      f"vertical {n(v.cap_raias_total/v.capacidade*100,0)}% da lotação está em "
      f"raia e o resto é massa parada nas baias de flanco; no horizontal a "
      f"raia sobe para {n(h.cap_raias_total/h.capacidade*100,0)}%. Fila em "
      "raia é fila contável, com ordem de chegada preservada e vazão "
      "previsível; baia é aglomeração que precisa de fiscal para virar fila "
      "outra vez.\n")

    A("## Separadores de fila\n")
    A("Barreira externa, componente a componente. Não entra aqui o gradil "
      "permanente do Ring, que os dois desenhos usam de graça, nem os 100 "
      "unifilas (200 m) do item d do orçamento, que servem ao interior do "
      "Hall 2.\n")
    A("| Componente | Vertical (m) | Horizontal (m) |")
    A("|---|---:|---:|")
    chaves = list(dict.fromkeys(list(v.barreira) + list(h.barreira)))
    for k in chaves:
        A(f"| {k} | {n(v.barreira.get(k,0),1)} | {n(h.barreira.get(k,0),1)} |")
    A(f"| **Total** | **{n(v.barreira_total,1)}** | **{n(h.barreira_total,1)}** |")
    A(f"| **Separadores (2 m)** | **{v.separadores}** | **{h.separadores}** |")
    A(f"| A comprar (estoque {ESTOQUE_SEPARADORES}) | {v.compra} | {h.compra} |")
    A(f"| Custo da compra | EUR {n(v.custo_compra,2)} | EUR {n(h.custo_compra,2)} |")
    A("")
    A(f"Na versão cheia, o horizontal pede {h.separadores - v.separadores} "
      "separadores a mais que o vertical, e a razão é única e identificável: "
      "os **tubos**. Cada deck de trás gasta duas corridas de barreira só para "
      f"atravessar a profundidade dos decks da frente — "
      f"{n(h.barreira.get('tubos de saída dos decks de trás',0),1)} m que o "
      "vertical não gasta. Os serpenteados propriamente ditos são levemente "
      "mais eficientes no horizontal, porque a raia longa dilui o custo das "
      "pontas.\n")

    A("## Escada de dimensionamento\n")
    A("O número de raias por deck é a única alavanca: com os decks na largura "
      "máxima, ela troca capacidade por barreira quase linearmente. A linha "
      "marcada é a recomendada.\n")
    A("| Raias A/B/C | Capacidade | A | B | C | Separadores | A comprar | Custo |")
    A("|---|---:|---:|---:|---:|---:|---:|---:|")
    alvo = tuple(b.raias for b in enxuta.blocos)
    cheio = tuple(b.raias for b in h.blocos)
    for linha in escada:
        r = linha["raias"]
        marca = " ←" if r == alvo else (" ←←" if r == cheio else "")
        pe = linha["por_entrada"]
        A(f"| {r[0]}/{r[1]}/{r[2]}{marca} | {n(linha['capacidade'])} | "
          f"{n(pe['A'])} | {n(pe['B'])} | {n(pe['C'])} | {linha['separadores']} | "
          f"{linha['compra']} | EUR {n(linha['custo_compra_eur'],2)} |")
    A("")
    A("`←` recomendada · `←←` Ring cheio\n")

    A("## Recomendação\n")
    A(f"**{'/'.join(str(x) for x in alvo)} raias**: {n(enxuta.capacidade)} "
      f"pessoas com {enxuta.separadores} separadores "
      f"({enxuta.compra} a comprar, EUR {n(enxuta.custo_compra,2)}). Fica "
      f"{v.separadores - enxuta.separadores} separadores abaixo do plano "
      "vertical e ainda sustenta uma lotação muito acima de qualquer pico "
      "plausível — o Ring nunca foi o gargalo desta operação, e gastar "
      "barreira para enchê-lo é comprar capacidade que não vai ser usada. "
      "Se o Posto preferir margem, a linha `←←` enche o Ring.\n")

    A("## Pendências de campo\n")
    A("1. **Bordo oeste do Ring.** O retângulo está centrado em S5 por "
      "estimativa; medir no local decide a largura real dos decks e, com "
      "ela, a capacidade de cada um.\n")
    A("2. **Aberturas do gradil.** O desenho supõe que dá para abrir portão "
      "no gradil permanente do Ring nos três eixos de porta (x ≈ 22,1 / 28,3 "
      "/ 34,5 m) e na garganta sudeste. Se o gradil não abrir onde se precisa, "
      "os tubos deixam de ser retos e a vantagem principal do desenho cai.\n")
    A("3. **Piso e drenagem.** Raia leste-oeste de 36 m acompanha a "
      "declividade do Ring por inteiro; verificar se algum trecho acumula "
      "água, o que inviabilizaria as raias do fundo num dia de chuva "
      "(40% a 65% de probabilidade em 4 de outubro, conforme o limiar).\n")
    A("4. **Confirmar a densidade adotada.** 2,0 pessoas/m² em raia e 1,8 em "
      "baia são reconstrução, não medição. Se a densidade real sob "
      "guarda-chuva for menor, as duas geometrias perdem capacidade na mesma "
      "proporção e a comparação não muda.\n")
    return "\n".join(L) + "\n"


def main() -> None:
    os.makedirs(SAIDAS, exist_ok=True)
    v = desenho_vertical()
    h = desenho_horizontal((6, 6, 6))
    escada = tabela_troca()
    enxuta_raias = (4, 5, 4)
    enxuta = desenho_horizontal(enxuta_raias)

    with open(os.path.join(SAIDAS, "ring3.json"), "w", encoding="utf-8") as f:
        dados = resumo_json(v, h, escada)
        dados["horizontal_enxuta"] = resumo_json(v, enxuta, [])["horizontal"]
        json.dump(dados, f, ensure_ascii=False, indent=2)
    with open(os.path.join(SAIDAS, "plano_ring3_horizontal.md"), "w",
              encoding="utf-8") as f:
        f.write(markdown(v, h, escada, enxuta))
    with open(os.path.join(SAIDAS, "ring3_vertical.svg"), "w", encoding="utf-8") as f:
        f.write(svg_vertical(v))
    with open(os.path.join(SAIDAS, "ring3_horizontal.svg"), "w", encoding="utf-8") as f:
        f.write(svg_horizontal(h))
    with open(os.path.join(SAIDAS, "ring3_horizontal_enxuta.svg"), "w",
              encoding="utf-8") as f:
        f.write(svg_horizontal(enxuta))

    conf = confere_baseline(v)
    print(f"vertical    {conf['total_calculado']:>5} pessoas · "
          f"{v.separadores} separadores · {v.barreira_total:.1f} m")
    print(f"horizontal  {h.capacidade:>5.0f} pessoas · "
          f"{h.separadores} separadores · {h.barreira_total:.1f} m")
    print(f"h. enxuta   {enxuta.capacidade:>5.0f} pessoas · "
          f"{enxuta.separadores} separadores · {enxuta.barreira_total:.1f} m")
    print("saidas/: ring3.json, plano_ring3_horizontal.md, ring3_*.svg")


if __name__ == "__main__":
    main()
