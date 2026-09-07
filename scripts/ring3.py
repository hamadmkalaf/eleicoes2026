#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ring 3 — girar as serpentinas 90 graus dentro das mesmas tres zonas.

O plano vigente da fila externa (Ring 3 do RDS, 39,0 x 35,0 m, 14 m ao sul da
fachada do Hall 2) tem tres zonas lado a lado, A, B e C, alimentadas por um
corredor de fundo ao sul e descarregando ao norte nas portas S4, S5 e S6.
Dentro de cada zona as raias correm norte-sul.

Este script mede o que muda quando as raias, dentro das MESMAS zonas, passam a
correr leste-oeste, empilhadas em altura -- o corredor de fundo, as zonas, as
baias de flanco, a garganta e as portas ficam onde estao. So a dobra da fila
gira 90 graus.

  vigente        raias norte-sul, com as baias de flanco (plano vigente)
  girado         raias leste-oeste, sem baias: as tres zonas ocupam a largura
                 toda do Ring e toda a lotacao e fila em raia medida
  girado c/baia  o passo intermediario: so girar, mantendo as baias

Saidas: saidas/ring3.json, saidas/plano_ring3_horizontal.md,
        saidas/ring3_vigente.svg, saidas/ring3_girado.svg,
        saidas/ring3_girado_com_baias.svg
"""

from __future__ import annotations

import json
import math
import os
from dataclasses import dataclass, field

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAIDAS = os.path.join(RAIZ, "saidas")

# --------------------------------------------------------------------------
# 1. Geometria herdada — de scripts/salao.py e das decisoes do Posto,
#    replicada aqui porque aqueles arquivos nao estao neste repositorio.
#    Metros, origem no canto sudoeste do salao, y para o norte. A fachada sul
#    do Hall 2 e y = 0; o Ring 3 fica ao sul dela (y negativo).
# --------------------------------------------------------------------------
RING = {"x0": 8.79, "x1": 47.78, "y0": -49.0, "y1": -14.0}   # 39,0 x 35,0 m
APRON = 14.0

PORTAS = {
    "A": {"porta": "S4", "x0": 19.10, "x1": 25.03},
    "B": {"porta": "S5", "x0": 25.32, "x1": 31.25},
    "C": {"porta": "S6", "x0": 31.54, "x1": 37.47},
}
SAIDAS_FACHADA = {"S2": (13.25, 14.45), "S8": (42.12, 43.32)}
ESPERADO = {"A": 3642, "B": 4215, "C": 3642}          # base B de 2022
ESPERADO_TOTAL = sum(ESPERADO.values())

# --------------------------------------------------------------------------
# 2. Premissas do modelo de fila. As quatro primeiras sao RECONSTRUIDAS: sao
#    os valores que reproduzem exatamente os 855 (serpenteados) e os 547
#    (baias) do plano original — ver confere_original().
# --------------------------------------------------------------------------
PASSO_RAIA = 1.40      # modulo da raia, eixo a eixo da barreira
TOL_PASSO = 0.05       # aperto aceito no passo para caber mais uma raia
RAIA_UTIL = 1.20       # largura livre de caminhada
DENS_FILA = 2.00       # pessoas/m2 em raia, em pe, sob guarda-chuva
DENS_BAIA = 1.80       # pessoas/m2 em baia de espera
VAO_RETORNO = 1.20     # folga de meia-volta na ponta de cada raia
PERDA_MEIA_VOLTA = 0.60   # fila perdida em cada meia-volta (analise de sensibilidade)

SEPARADOR_M = 2.00     # 1 separador = 2 m de barreira
SEPARADOR_EUR = 13.02  # EUR 1.303,00 / 100 unidades (item d do orcamento)
ESTOQUE_SEPARADORES = 200

POR_METRO_RAIA = RAIA_UTIL * DENS_FILA     # pessoas por metro de raia

# geometria do plano vigente
PROF_SERP = 23.75      # profundidade da faixa de serpenteados
LARG_BAIA = 6.40       # baia de flanco, cada lado
CORREDOR = {"comp": 36.70, "larg": 3.00}   # corredor de fundo, ao sul
FUNIL_GARGANTA = 12.0
BLOCOS_ORIG = {"A": (15.16, 19.36), "B": (22.09, 34.69), "C": (37.19, 41.39)}


def eixo_porta(e: str) -> float:
    return (PORTAS[e]["x0"] + PORTAS[e]["x1"]) / 2


def raias_que_cabem(dim: float) -> int:
    """Quantas raias cabem numa dimensao, aceitando apertar o passo em ate 5 cm."""
    n = int(round(dim / PASSO_RAIA))
    while n > 0 and dim / n < PASSO_RAIA - TOL_PASSO:
        n -= 1
    return max(n, 0)


def unidades(metros: float) -> int:
    return math.ceil(metros / SEPARADOR_M)


# --------------------------------------------------------------------------
# 3. Uma zona: o retangulo de serpenteado de uma entrada
# --------------------------------------------------------------------------
@dataclass
class Zona:
    nome: str
    x0: float
    x1: float
    prof: float
    orientacao: str          # "vertical" (raias N-S) ou "horizontal" (raias L-O)

    @property
    def larg(self) -> float:
        return self.x1 - self.x0

    @property
    def raias(self) -> int:
        return raias_que_cabem(self.larg if self.orientacao == "vertical" else self.prof)

    @property
    def passo(self) -> float:
        d = self.larg if self.orientacao == "vertical" else self.prof
        return d / self.raias if self.raias else 0.0

    @property
    def comp(self) -> float:
        """Comprimento de uma raia."""
        return self.prof if self.orientacao == "vertical" else self.larg

    # -- descarga ---------------------------------------------------------
    @property
    def portao(self) -> float:
        """x do portao de saida da zona, na sua borda norte.

        Na vertical a fila sobe pelas raias e sai pela boca do bloco: o ponto
        de descarga e o eixo do bloco. Na horizontal a ultima raia corre rente
        a borda norte, entao o portao pode ficar em qualquer x dessa borda —
        e vai para o eixo da porta, se ele cair dentro da zona.
        """
        if self.orientacao == "vertical":
            return (self.x0 + self.x1) / 2
        return min(max(eixo_porta(self.nome), self.x0), self.x1)

    @property
    def toco(self) -> float:
        """Pedaco da ultima raia que sobra depois do portao, e nao enfileira."""
        if self.orientacao == "vertical":
            return 0.0
        return min(self.portao - self.x0, self.x1 - self.portao)

    @property
    def diagonal(self) -> float:
        """Percurso da descarga, do portao ate o eixo da porta, no apron."""
        return math.hypot(APRON, eixo_porta(self.nome) - self.portao)

    # -- medidas ----------------------------------------------------------
    @property
    def capacidade(self) -> float:
        return (self.raias * self.comp - self.toco) * POR_METRO_RAIA

    @property
    def barreira(self) -> float:
        n, L = self.raias, self.comp
        if n <= 0:
            return 0.0
        return 2 * L + (n - 1) * max(0.0, L - VAO_RETORNO)

    @property
    def meias_voltas(self) -> int:
        return max(0, self.raias - 1)

    @property
    def caminhada(self) -> float:
        return self.raias * self.comp - self.toco

    @property
    def perda_por_voltas(self) -> float:
        """Fila perdida nas meias-voltas, se cada uma custar PERDA_MEIA_VOLTA."""
        return self.meias_voltas * PERDA_MEIA_VOLTA * POR_METRO_RAIA


# --------------------------------------------------------------------------
# 4. Um desenho: as tres zonas mais o resto da barreira
# --------------------------------------------------------------------------
@dataclass
class Desenho:
    codigo: str
    nome: str
    resumo: str
    zonas: list
    baias: dict = field(default_factory=dict)      # entrada -> (rotulo, area)
    barreira_extra: dict = field(default_factory=dict)
    notas: list = field(default_factory=list)

    def zona(self, nome: str) -> Zona:
        return next(z for z in self.zonas if z.nome == nome)

    # -- capacidade -------------------------------------------------------
    @property
    def cap_raias(self) -> float:
        return sum(z.capacidade for z in self.zonas)

    @property
    def cap_baias(self) -> float:
        return sum(a * DENS_BAIA for _, a in self.baias.values())

    @property
    def capacidade(self) -> float:
        return self.cap_raias + self.cap_baias

    def cap_por_entrada(self) -> dict:
        fora = {}
        for z in self.zonas:
            baia = self.baias.get(z.nome)
            fora[z.nome] = z.capacidade + (baia[1] * DENS_BAIA if baia else 0.0)
        return fora

    def equilibrio(self) -> dict:
        cap = self.cap_por_entrada()
        return {e: cap[e] / ESPERADO[e] for e in cap}

    @property
    def meias_voltas(self) -> int:
        return sum(z.meias_voltas for z in self.zonas)

    @property
    def capacidade_com_perda(self) -> float:
        return self.capacidade - sum(z.perda_por_voltas for z in self.zonas)

    # -- barreira ---------------------------------------------------------
    @property
    def barreira(self) -> dict:
        b = {"serpenteados": sum(z.barreira for z in self.zonas)}
        b.update(self.barreira_extra)
        b["raias do apron até as portas"] = sum(2 * z.diagonal for z in self.zonas)
        b["funil da garganta sudeste"] = 2 * FUNIL_GARGANTA
        return b

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


def _baias_de_flanco() -> dict:
    return {"A": ("baia do flanco oeste", LARG_BAIA * PROF_SERP),
            "C": ("baia do flanco leste", LARG_BAIA * PROF_SERP)}


def _extra_do_plano_vigente() -> dict:
    return {"corredor de fundo (2 lados)": 2 * CORREDOR["comp"],
            "fechamento das baias de flanco": 2 * (2 * LARG_BAIA)}


def desenho_original() -> Desenho:
    """Plano vigente: raias norte-sul, tres blocos lado a lado.

    Cotas lidas do diagrama publicado na pagina "Rota do Eleitor": blocos de
    4,2 / 12,6 / 4,2 m (3 / 9 / 3 raias), 23,75 m de raia, corredor de fundo de
    3,0 m ao sul e baias de 6,4 m nos flancos.
    """
    z = [Zona(e, *BLOCOS_ORIG[e], PROF_SERP, "vertical") for e in ("A", "B", "C")]
    d = Desenho("V", "Serpenteados verticais (plano vigente, reconstruído)",
                "Raias norte-sul; a fila sobe do corredor de fundo até a boca do "
                "bloco e atravessa o apron em diagonal.",
                z, _baias_de_flanco(), _extra_do_plano_vigente())
    d.notas = [
        "Cada bloco descarrega pela sua boca inteira, que tem a largura do "
        "bloco e não coincide com o vão da porta: as três correntes cruzam o "
        "apron em diagonal.",
        "As raias de 23,75 m são longas e com poucas meias-voltas — o ponto "
        "forte deste desenho.",
    ]
    return d


def desenho_girado_com_baias() -> Desenho:
    """As mesmas zonas, com as raias giradas para leste-oeste."""
    z = [Zona(e, *BLOCOS_ORIG[e], PROF_SERP, "horizontal") for e in ("A", "B", "C")]
    d = Desenho("H", "Serpenteados horizontais (mesmas zonas, raias giradas)",
                "Raias leste-oeste empilhadas em altura, dentro dos mesmos "
                "retângulos; corredor de fundo, baias, garganta e portas "
                "no lugar.",
                z, _baias_de_flanco(), _extra_do_plano_vigente())
    d.notas = [
        "A última raia corre rente à borda norte da zona, então o portão de "
        "saída pode ficar em qualquer ponto dela — e vai para o eixo da porta. "
        "Na zona B o eixo de S5 cai dentro do bloco: a descarga fica "
        "perpendicular, sem diagonal nenhuma.",
        "A barreira cai porque cada divisória passa a ter o comprimento da "
        "zona, não a profundidade dela — e porque cada meia-volta a mais "
        "encurta a divisória em 1,2 m.",
        "O preço é a meia-volta: nas zonas A e C, de 4,2 m de largura, a raia "
        "vira um ziguezague de 4,2 m com 16 curvas.",
    ]
    return d


VAO_ENTRE_ZONAS = 2.60


def desenho_girado(raias: int | None = None) -> Desenho:
    """O desenho: raias leste-oeste, sem baias, zonas na largura toda do Ring.

    Tirar as baias devolve os 12,8 m dos dois flancos as tres zonas. Cada zona
    fica com a largura proporcional ao comparecimento que ela espera — e essa
    largura e, agora, o comprimento da raia. `raias` fixa quantas raias cada
    zona tem (a profundidade sai disso); sem argumento, usa a faixa inteira de
    23,75 m do plano vigente.
    """
    prof = PROF_SERP if raias is None else raias * PASSO_RAIA
    util = (RING["x1"] - RING["x0"]) - 2 * VAO_ENTRE_ZONAS
    larg = {e: util * ESPERADO[e] / ESPERADO_TOTAL for e in ESPERADO}
    x = RING["x0"]
    z = []
    for e in ("A", "B", "C"):
        z.append(Zona(e, x, x + larg[e], prof, "horizontal"))
        x += larg[e] + VAO_ENTRE_ZONAS
    d = Desenho("H", "Serpenteados horizontais, sem baias (o desenho)",
                "Raias leste-oeste empilhadas; as três zonas ocupam a largura "
                "toda do Ring e toda a lotação é fila em raia medida.",
                z, {}, {"corredor de fundo (2 lados)": 2 * CORREDOR["comp"]})
    d.notas = [
        "Sem baias: toda a lotação é fila em raia — contável, com ordem de "
        "chegada preservada e vazão previsível. No plano vigente, 39% da "
        "lotação é massa parada nas baias de flanco.",
        "A raia mais curta passa de 4,2 m (o ziguezague das zonas A e C quando "
        "só se gira, mantendo as baias) para mais de 10 m.",
        "A largura de cada zona é proporcional ao comparecimento que ela "
        "espera — e, nesta geometria, largura da zona é comprimento de raia.",
        "Custa mais barreira que o plano vigente: a lotação que ele ganha de "
        "graça nas baias, que usam o gradil do Ring em três lados, passa a ser "
        "paga em divisória.",
    ]
    return d


def escada_de_raias() -> list:
    """Capacidade contra separadores, variando o numero de raias por zona."""
    fora = []
    for n in range(6, int(PROF_SERP / (PASSO_RAIA - TOL_PASSO)) + 1):
        d = desenho_girado(n)
        if sum(z.prof for z in d.zonas) / 3 > PROF_SERP + 0.01:
            break
        fora.append({
            "raias_por_zona": n,
            "profundidade_m": round(n * PASSO_RAIA, 2),
            "capacidade": round(d.capacidade),
            "por_entrada": {e: round(x) for e, x in d.cap_por_entrada().items()},
            "barreira_m": round(d.barreira_total, 1),
            "separadores": d.separadores,
            "compra": d.compra,
            "custo_compra_eur": round(d.custo_compra, 2),
        })
    return fora


def confere_original(v: Desenho) -> dict:
    return {
        "raias_calculado": round(v.cap_raias, 1), "raias_publicado": 855,
        "baias_calculado": round(v.cap_baias, 1), "baias_publicado": 547,
        "total_calculado": round(v.capacidade), "total_publicado": 1402,
        "barreira_calculada_m": round(v.barreira_total, 1),
        "barreira_publicada_m": 596.3,
        "separadores_calculado": v.separadores, "separadores_publicado": 300,
    }


# --------------------------------------------------------------------------
# 5. Planta em SVG (escala real)
# --------------------------------------------------------------------------
ESCALA = 14.0
MARGEM = 46.0
CORES = {"A": "#2a78d6", "B": "#e08a00", "C": "#c2185b"}
MARCADOR = ('<defs><marker id="seta" viewBox="0 0 10 10" refX="8" refY="5" '
            'markerWidth="5" markerHeight="5" orient="auto-start-reverse">'
            '<path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker></defs>')


def _proj(x, y):
    return MARGEM + (x - RING["x0"] + 6) * ESCALA, MARGEM + (2.0 - y) * ESCALA


def _ret(x0, y0, x1, y1, **kw):
    ax, ay = _proj(x0, y1)
    bx, by = _proj(x1, y0)
    at = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in kw.items())
    return (f'<rect x="{ax:.1f}" y="{ay:.1f}" width="{bx - ax:.1f}" '
            f'height="{by - ay:.1f}" {at}/>')


def _linha(x0, y0, x1, y1, **kw):
    ax, ay = _proj(x0, y0)
    bx, by = _proj(x1, y1)
    at = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in kw.items())
    return f'<line x1="{ax:.1f}" y1="{ay:.1f}" x2="{bx:.1f}" y2="{by:.1f}" {at}/>'


def _txt(x, y, t, size=11, anchor="middle", peso=400, cor="#243244", rot=None,
         halo=None):
    px, py = _proj(x, y)
    r = f' transform="rotate({rot} {px:.1f} {py:.1f})"' if rot else ""
    h = (f' paint-order="stroke" stroke="{halo}" stroke-width="3.5" '
         'stroke-linejoin="round"') if halo else ""
    return (f'<text x="{px:.1f}" y="{py:.1f}" text-anchor="{anchor}" '
            f'font-family="ui-sans-serif,system-ui,Helvetica,Arial,sans-serif" '
            f'font-size="{size}" font-weight="{peso}" fill="{cor}"{h}{r}>{t}</text>')


def svg(d: Desenho) -> str:
    larg = (RING["x1"] - RING["x0"] + 12) * ESCALA + 2 * MARGEM
    alt = (RING["y1"] - RING["y0"] + APRON + 6) * ESCALA + 2 * MARGEM
    p = [_ret(RING["x0"] - 5, -APRON, RING["x1"] + 5, 0, fill="#eef1f4"),
         _ret(RING["x0"], RING["y0"], RING["x1"], RING["y1"], fill="#f6f4ef",
              stroke="#1c2733", stroke_width="2.2"),
         _linha(RING["x0"] - 5, 0, RING["x1"] + 5, 0, stroke="#1c2733", stroke_width="3"),
         _txt((RING["x0"] + RING["x1"]) / 2, 1.2, "FACHADA SUL DO HALL 2", 11,
              peso=700, cor="#5c6c80")]
    for e, dd in PORTAS.items():
        p.append(_linha(dd["x0"], 0, dd["x1"], 0, stroke=CORES[e], stroke_width="6"))
        p.append(_txt(eixo_porta(e), -1.6, f'{dd["porta"]} · {e}', 11, peso=700, cor=CORES[e]))
    for nome, (a, b) in SAIDAS_FACHADA.items():
        p.append(_linha(a, 0, b, 0, stroke="#b26a12", stroke_width="6"))
        p.append(_txt((a + b) / 2, -1.6, f"{nome} saída", 9.5, cor="#b26a12"))
    p.append(_txt(RING["x0"] - 4.5, -APRON / 2, "apron pavimentado · 14 m", 10,
                  cor="#5c6c80", rot=-90))

    y_topo, y_base = RING["y1"], RING["y1"] - PROF_SERP
    for z in d.zonas:
        c = CORES[z.nome]
        p.append(_ret(z.x0, y_base, z.x1, y_topo, fill=c, fill_opacity=".13",
                      stroke=c, stroke_width="1.4"))
        if z.orientacao == "vertical":
            for i in range(1, z.raias):
                x = z.x0 + i * z.passo
                p.append(_linha(x, y_base + VAO_RETORNO if i % 2 else y_base, x,
                                y_topo if i % 2 else y_topo - VAO_RETORNO,
                                stroke=c, stroke_width="1", stroke_opacity=".6"))
            p.append(_txt((z.x0 + z.x1) / 2, y_topo + 1.3,
                          f"{z.nome} · {z.raias} raias de {z.comp:.1f} m", 11,
                          peso=700, cor=c, halo="#eef1f4"))
        else:
            for i in range(1, z.raias):
                y = y_base + i * z.passo
                a = z.x0 + VAO_RETORNO if i % 2 else z.x0
                b = z.x1 if i % 2 else z.x1 - VAO_RETORNO
                p.append(_linha(a, y, b, y, stroke=c, stroke_width="1",
                                stroke_opacity=".6"))
            p.append(_txt((z.x0 + z.x1) / 2, y_topo + 1.3,
                          f"{z.nome} · {z.raias} × {z.comp:.1f} m", 11, peso=700,
                          cor=c, halo="#eef1f4"))
        p.append(_linha(z.portao, y_topo, eixo_porta(z.nome), -0.4, stroke=c,
                        stroke_width="2", marker_end="url(#seta)"))
    for nome, (x0, x1) in (("baia oeste", (RING["x0"], RING["x0"] + LARG_BAIA)),
                           ("baia leste", (RING["x1"] - LARG_BAIA, RING["x1"]))):
        if d.baias:
            p.append(_ret(x0, y_base, x1, y_topo, fill="#8a919b", fill_opacity=".16",
                          stroke="#8a919b", stroke_width="1.2", stroke_dasharray="4 3"))
            p.append(_txt((x0 + x1) / 2, (y_base + y_topo) / 2, nome, 10,
                          cor="#5c6c80", rot=-90))
    cy1 = y_base - 1.2
    cy0 = cy1 - CORREDOR["larg"]
    p.append(_ret((RING["x0"] + RING["x1"]) / 2 - CORREDOR["comp"] / 2, cy0,
                  (RING["x0"] + RING["x1"]) / 2 + CORREDOR["comp"] / 2, cy1,
                  fill="none", stroke="#5c6c80", stroke_width="1.2"))
    p.append(_txt((RING["x0"] + RING["x1"]) / 2, (cy0 + cy1) / 2 - 0.4,
                  "CORREDOR DE FUNDO · 3,0 m", 10, peso=600, cor="#5c6c80"))
    p.append(_linha(RING["x1"] - 1.0, RING["y0"] + 2.0,
                    (RING["x0"] + RING["x1"]) / 2 + CORREDOR["comp"] / 2 - 1,
                    (cy0 + cy1) / 2, stroke="#5c6c80", stroke_width="2",
                    marker_end="url(#seta)"))
    p.append(_txt(RING["x1"] - 6, RING["y0"] + 3.4, "garganta sudeste · pré-triagem",
                  10, anchor="end", cor="#5c6c80"))
    p.append(_txt(RING["x0"] + 0.4, RING["y0"] + 1.0,
                  "gradil permanente do Ring 3 · 39,0 × 35,0 m", 10,
                  anchor="start", cor="#8a919b"))
    corpo = "\n".join(p)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {larg:.0f} '
            f'{alt:.0f}" width="{larg:.0f}" height="{alt:.0f}" role="img">\n'
            f'<rect width="{larg:.0f}" height="{alt:.0f}" fill="#fbfaf7"/>\n{MARCADOR}\n'
            f'{_txt(RING["x0"], 3.4, d.nome, 15, anchor="start", peso=700)}\n'
            f'{corpo}\n</svg>\n')


# --------------------------------------------------------------------------
# 6. Relatorio
# --------------------------------------------------------------------------
def n(v, casas=0):
    return f"{v:,.{casas}f}".replace(",", "@").replace(".", ",").replace("@", ".")


def sinal(v, casas=0):
    return ("+" if v >= 0 else "−") + n(abs(v), casas)


def bloco_json(d: Desenho) -> dict:
    return {
        "codigo": d.codigo, "nome": d.nome,
        "capacidade": round(d.capacidade),
        "capacidade_raias": round(d.cap_raias),
        "capacidade_baias": round(d.cap_baias),
        "capacidade_com_perda_de_meia_volta": round(d.capacidade_com_perda),
        "meias_voltas": d.meias_voltas,
        "por_entrada": {k: round(x) for k, x in d.cap_por_entrada().items()},
        "capacidade_por_eleitor_esperado": {k: round(x, 4)
                                            for k, x in d.equilibrio().items()},
        "barreira_m": round(d.barreira_total, 1),
        "barreira_por_componente_m": {k: round(x, 1) for k, x in d.barreira.items()},
        "separadores": d.separadores, "estoque": ESTOQUE_SEPARADORES,
        "compra": d.compra, "custo_compra_eur": round(d.custo_compra, 2),
        "m_por_pessoa": round(d.m_por_pessoa, 3),
        "zonas": [{"entrada": z.nome, "orientacao": z.orientacao,
                   "largura_m": round(z.larg, 2), "profundidade_m": round(z.prof, 2),
                   "raias": z.raias, "comprimento_raia_m": round(z.comp, 2),
                   "passo_m": round(z.passo, 3), "meias_voltas": z.meias_voltas,
                   "caminhada_m": round(z.caminhada, 1),
                   "toco_perdido_m": round(z.toco, 2),
                   "portao_x_m": round(z.portao, 2),
                   "descarga_m": round(z.diagonal, 2),
                   "desvio_lateral_m": round(abs(eixo_porta(z.nome) - z.portao), 2),
                   "capacidade": round(z.capacidade)} for z in d.zonas],
        "baias": {k: {"rotulo": r, "area_m2": round(a, 1),
                      "capacidade": round(a * DENS_BAIA)}
                  for k, (r, a) in d.baias.items()},
        "notas": d.notas,
    }


def markdown(v: Desenho, h: Desenho, hb: Desenho, escada: list) -> str:
    conf = confere_original(v)
    L = []
    A = L.append
    A("# Ring 3 — serpentinas giradas, sem baias\n")
    A("O plano vigente da fila externa (Ring 3, 39,0 × 35,0 m, 14 m ao sul da "
      "fachada) tem três zonas lado a lado — A, B e C —, alimentadas por um "
      "**corredor de fundo** ao sul e descarregando ao norte nas portas S4, S5 "
      "e S6. Dentro de cada zona as raias correm norte-sul, e os dois flancos "
      "do Ring são baias de espera.\n")
    A("Este desenho faz duas coisas: **gira as raias** para leste-oeste, "
      "empilhadas em altura, e **preenche as baias de flanco com serpenteado**. "
      "As três zonas passam a ocupar a largura toda do Ring, com largura "
      "proporcional ao comparecimento que cada uma espera — e nesta geometria "
      "largura de zona é comprimento de raia. Corredor de fundo, garganta e "
      "portas ficam onde estão.\n")

    A("## O que muda\n")
    A("| | Plano vigente | Este desenho | Δ |")
    A("|---|---:|---:|---:|")
    A(f"| Lotação total | {n(v.capacidade)} | {n(h.capacidade)} | "
      f"{sinal(h.capacidade-v.capacidade)} |")
    A(f"| … em raia medida | {n(v.cap_raias)} | {n(h.cap_raias)} | "
      f"{sinal(h.cap_raias-v.cap_raias)} |")
    A(f"| … em baia de espera | {n(v.cap_baias)} | 0 | {sinal(-v.cap_baias)} |")
    A(f"| Raia mais curta | {n(min(z.comp for z in v.zonas),1)} m | "
      f"{n(min(z.comp for z in h.zonas),1)} m | "
      f"{sinal(min(z.comp for z in h.zonas)-min(z.comp for z in v.zonas),1)} m |")
    A(f"| Meias-voltas | {v.meias_voltas} | {h.meias_voltas} | "
      f"{sinal(h.meias_voltas-v.meias_voltas)} |")
    A(f"| Barreira | {n(v.barreira_total,1)} m | {n(h.barreira_total,1)} m | "
      f"{sinal(h.barreira_total-v.barreira_total,1)} m |")
    A(f"| **Separadores de 2 m** | **{v.separadores}** | **{h.separadores}** | "
      f"**{sinal(h.separadores-v.separadores)}** |")
    A(f"| A comprar (estoque {ESTOQUE_SEPARADORES}) | {v.compra} | {h.compra} | "
      f"{sinal(h.compra-v.compra)} |")
    A(f"| Custo da compra | EUR {n(v.custo_compra,2)} | EUR {n(h.custo_compra,2)} "
      f"| EUR {sinal(h.custo_compra-v.custo_compra,2)} |")
    A("")
    A(f"A lotação cai {n(abs(h.capacidade-v.capacidade))} pessoas "
      f"({n(abs(h.capacidade/v.capacidade-1)*100,1)}%), mas **toda ela vira fila "
      f"em raia**: {n(h.cap_raias)} contra {n(v.cap_raias)} do plano vigente, um "
      f"aumento de {n((h.cap_raias/v.cap_raias-1)*100,0)}%. Fila em raia é fila "
      "contável, com ordem de chegada preservada e vazão previsível; baia é "
      "aglomeração que precisa de fiscal para voltar a ser fila.\n")
    A(f"O preço está na barreira: **{h.separadores} separadores** contra "
      f"{v.separadores}. Sobre as {ESTOQUE_SEPARADORES} unidades da "
      f"organizadora, faltam **{h.compra}** — contra as {v.compra} que o plano "
      f"vigente já precisava comprar. São {h.compra - v.compra} unidades a mais, "
      f"EUR {n(h.custo_compra - v.custo_compra,2)}. A razão é direta: a lotação "
      "que o plano vigente ganha de graça nas baias — que usam o gradil do Ring "
      "em três lados e não gastam divisória nenhuma — passa a ser paga em "
      "barreira.\n")

    A("## As três zonas\n")
    A("| Zona | Porta | Largura = raia | Raias | Profundidade | Caminhada | "
      "Lotação | Esperado | por eleitor |")
    A("|---|---|---:|---:|---:|---:|---:|---:|---:|")
    for z in h.zonas:
        A(f"| {z.nome} | {PORTAS[z.nome]['porta']} | {n(z.comp,2)} m | "
          f"{z.raias} | {n(z.prof,2)} m | {n(z.caminhada)} m | "
          f"{n(z.capacidade)} | {n(ESPERADO[z.nome])} | "
          f"{n(h.equilibrio()[z.nome],4)} |")
    A("")
    A("As larguras saem do comparecimento esperado de cada entrada (base B de "
      "2022), então a lotação de cada zona fica proporcional à fila que ela "
      "vai receber. Entre as zonas ficam "
      f"{n(VAO_ENTRE_ZONAS,1)} m de folga, para circulação de fiscal e passagem "
      "de prioritário.\n")
    A("**Descarga.** Com as raias na horizontal, a última raia corre rente à "
      "borda norte da zona, então o portão de saída pode ficar em qualquer "
      "ponto dela — e vai para o eixo da porta. Na zona B o eixo de S5 cai "
      "dentro do bloco e a descarga fica perpendicular.\n")
    A("| Zona | Desvio lateral no plano vigente | Neste desenho |")
    A("|---|---:|---:|")
    for e in ("A", "B", "C"):
        A(f"| {e} | {n(abs(eixo_porta(e)-v.zona(e).portao),2)} m | "
          f"{n(abs(eixo_porta(e)-h.zona(e).portao),2)} m |")
    A("")

    A("## Barreira, componente a componente\n")
    A("Fora desta conta: o gradil permanente do Ring, que os dois desenhos usam "
      "de graça, e os 100 unifilas (200 m) do item *d* do orçamento, que servem "
      "ao interior do Hall 2.\n")
    A("| Componente | Plano vigente (m) | Este desenho (m) |")
    A("|---|---:|---:|")
    chaves = list(dict.fromkeys(list(v.barreira) + list(h.barreira)))
    for k in chaves:
        a, b = v.barreira.get(k, 0.0), h.barreira.get(k, 0.0)
        A(f"| {k} | {n(a,1) if a else '—'} | {n(b,1) if b else '—'} |")
    A(f"| **Total** | **{n(v.barreira_total,1)}** | **{n(h.barreira_total,1)}** |")
    A(f"| **Separadores** | **{v.separadores}** | **{h.separadores}** |")
    A("")
    A("A barreira de um serpenteado é `(n+1) × comprimento da raia − 1,2 × "
      "(n−1)`: n+1 corridas longitudinais, e cada divisória interna para 1,2 m "
      "antes da ponta para abrir a meia-volta. O que encarece aqui não é o "
      "giro — é a área nova. O flanco que era baia virou serpenteado, e "
      "serpenteado se paga em divisória.\n")

    A("## Quanta barreira comprar\n")
    A("O número de raias por zona é a alavanca: ele troca lotação por barreira "
      "quase linearmente, sem mexer na largura das zonas nem na descarga. A "
      "profundidade sobrante do Ring fica livre.\n")
    A("| Raias por zona | Profundidade | Lotação | A | B | C | Separadores | "
      "A comprar | Custo |")
    A("|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for r in escada:
        marca = " ←" if r["raias_por_zona"] == h.zonas[0].raias else ""
        pe = r["por_entrada"]
        A(f"| {r['raias_por_zona']}{marca} | {n(r['profundidade_m'],1)} m | "
          f"{n(r['capacidade'])} | {n(pe['A'])} | {n(pe['B'])} | {n(pe['C'])} | "
          f"{r['separadores']} | {r['compra']} | EUR {n(r['custo_compra_eur'],2)} |")
    A("")
    cabe_v = [r for r in escada if r["separadores"] <= v.separadores]
    cabe_e = [r for r in escada if r["separadores"] <= ESTOQUE_SEPARADORES]
    fixa = h.barreira_total - sum(z.barreira for z in h.zonas)
    A(f"`←` o desenho: a faixa inteira de {n(PROF_SERP,2)} m do plano vigente.")
    if cabe_v:
        A(f"Se a compra de {h.compra} separadores não sair inteira, "
          f"{cabe_v[-1]['raias_por_zona']} raias por zona cabem dentro dos "
          f"mesmos {v.separadores} separadores do plano vigente, com "
          f"{n(cabe_v[-1]['capacidade'])} pessoas.")
    if not cabe_e:
        A(f"Nenhuma linha cabe nas {ESTOQUE_SEPARADORES} unidades da "
          f"organizadora: o corredor de fundo, as raias do apron e o funil da "
          f"garganta já consomem {n(fixa,1)} m — {unidades(fixa)} separadores "
          "— antes da primeira raia. A menor configuração da escada pede "
          f"{escada[0]['separadores']}.")
    A("")

    A("## O passo intermediário, para registro\n")
    A("Girar as raias **mantendo** as baias de flanco é o desenho mais barato "
      f"dos três — {hb.separadores} separadores, {v.separadores - hb.separadores} "
      "a menos que o plano vigente — porque as zonas A e C, de "
      f"{n(v.zona('A').larg,1)} m de largura, viram raias de "
      f"{n(hb.zona('A').comp,1)} m com {hb.zona('A').meias_voltas} meias-voltas. "
      "É barato e é um ziguezague. Preencher os flancos resolve isso: a raia "
      f"mais curta passa de {n(min(z.comp for z in hb.zonas),1)} m para "
      f"{n(min(z.comp for z in h.zonas),1)} m.\n")
    A("| | Vigente | Só girar (com baias) | Girar e preencher os flancos |")
    A("|---|---:|---:|---:|")
    A(f"| Lotação | {n(v.capacidade)} | {n(hb.capacidade)} | {n(h.capacidade)} |")
    A(f"| … em raia | {n(v.cap_raias)} | {n(hb.cap_raias)} | {n(h.cap_raias)} |")
    A(f"| Raia mais curta | {n(min(z.comp for z in v.zonas),1)} m | "
      f"{n(min(z.comp for z in hb.zonas),1)} m | "
      f"{n(min(z.comp for z in h.zonas),1)} m |")
    A(f"| Separadores | {v.separadores} | {hb.separadores} | {h.separadores} |")
    A(f"| A comprar | {v.compra} | {hb.compra} | {h.compra} |")
    A("")

    A("## Premissas e aderência ao plano original\n")
    A("| Parâmetro | Valor | Origem |")
    A("|---|---|---|")
    A(f"| Módulo da raia | {n(PASSO_RAIA,2)} m | reconstruído dos blocos de 4,2 e 12,6 m |")
    A(f"| Largura livre da raia | {n(RAIA_UTIL,2)} m | reconstruído |")
    A(f"| Densidade em raia | {n(DENS_FILA,1)} pessoas/m² | reconstruído |")
    A(f"| Densidade em baia | {n(DENS_BAIA,1)} pessoas/m² | reconstruído |")
    A(f"| Vão de meia-volta | {n(VAO_RETORNO,1)} m | premissa |")
    A(f"| Folga entre zonas | {n(VAO_ENTRE_ZONAS,1)} m | premissa |")
    A(f"| Separador | {n(SEPARADOR_M,1)} m · EUR {n(SEPARADOR_EUR,2)} | "
      "item d do orçamento (100 un. = EUR 1.303) |")
    A(f"| Estoque da organizadora | {ESTOQUE_SEPARADORES} un. | informado pelo Posto |")
    A("")
    A("`scripts/layout_ring3.py` e `saidas/plano_ring3.md` foram produzidos em "
      "sessão anterior e não chegaram a este repositório; o plano vigente foi "
      "reconstruído das cotas publicadas e reproduz os números publicados:\n")
    A("| Grandeza | Publicado | Recalculado |")
    A("|---|---:|---:|")
    A(f"| Serpenteados | {n(conf['raias_publicado'])} | {n(conf['raias_calculado'],1)} |")
    A(f"| Baias | {n(conf['baias_publicado'])} | {n(conf['baias_calculado'],1)} |")
    A(f"| Total | {n(conf['total_publicado'])} | {n(conf['total_calculado'])} |")
    A(f"| Barreira | {n(conf['barreira_publicada_m'],1)} m | "
      f"{n(conf['barreira_calculada_m'],1)} m |")
    A(f"| Separadores | {conf['separadores_publicado']} | "
      f"{conf['separadores_calculado']} |")
    A("")
    A("A capacidade fecha; a barreira fica "
      f"{n((conf['barreira_calculada_m']/conf['barreira_publicada_m']-1)*100,1)}% "
      "acima, porque a regra de contagem do plano original não é recuperável do "
      "que foi publicado. **A comparação usa a regra deste modelo nos dois "
      "desenhos.** Ancorando nos 300 separadores publicados em vez dos "
      f"{v.separadores} recalculados, este desenho daria cerca de "
      f"{round(300*h.separadores/v.separadores)} unidades.\n")

    A("## Pendências de campo\n")
    A("1. **Largura real do Ring.** O retângulo está centrado em S5 por "
      "estimativa. Nesta geometria a largura da zona *é* o comprimento da "
      "raia: a medição de campo mexe direto na lotação.\n")
    A("2. **Onde o gradil abre.** A descarga perpendicular da zona B supõe "
      f"portão no eixo de S5 (x ≈ {n(eixo_porta('B'),1)} m). Sem isso, o "
      "desenho continua de pé, mas a descarga volta a ser oblíqua.\n")
    A("3. **Piso e drenagem.** Raia leste-oeste de até "
      f"{n(max(z.comp for z in h.zonas),1)} m atravessa a declividade do Ring "
      "de lado a lado; verificar se algum trecho acumula água (40% a 65% de "
      "probabilidade de chuva em 4 de outubro, conforme o limiar da fonte).\n")
    A("4. **Compra dos separadores.** O desenho pede "
      f"{h.compra} unidades além das {ESTOQUE_SEPARADORES} da organizadora. "
      "Confirmar prazo e preço antes de fechar a profundidade das zonas — a "
      "escada acima é o que dá para recuar.\n")
    return "\n".join(L) + "\n"


def main() -> None:
    os.makedirs(SAIDAS, exist_ok=True)
    v = desenho_original()
    h = desenho_girado()
    hb = desenho_girado_com_baias()
    escada = escada_de_raias()

    with open(os.path.join(SAIDAS, "ring3.json"), "w", encoding="utf-8") as f:
        json.dump({
            "gerado_por": "scripts/ring3.py", "ring": RING, "apron_m": APRON,
            "premissas": {
                "passo_raia_m": PASSO_RAIA, "raia_util_m": RAIA_UTIL,
                "densidade_fila_p_m2": DENS_FILA, "densidade_baia_p_m2": DENS_BAIA,
                "vao_retorno_m": VAO_RETORNO,
                "vao_entre_zonas_m": VAO_ENTRE_ZONAS,
                "perda_por_meia_volta_m": PERDA_MEIA_VOLTA,
                "profundidade_serpenteado_m": PROF_SERP,
                "largura_baia_m": LARG_BAIA, "corredor_de_fundo": CORREDOR,
                "separador_m": SEPARADOR_M, "separador_eur": SEPARADOR_EUR,
                "estoque_separadores": ESTOQUE_SEPARADORES,
                "comparecimento_esperado": ESPERADO,
            },
            "aderencia_ao_plano_original": confere_original(v),
            "vigente": bloco_json(v), "girado": bloco_json(h),
            "girado_com_baias": bloco_json(hb),
            "escada_de_raias": escada,
        }, f, ensure_ascii=False, indent=2)
    with open(os.path.join(SAIDAS, "plano_ring3_horizontal.md"), "w",
              encoding="utf-8") as f:
        f.write(markdown(v, h, hb, escada))
    for d, nome in ((v, "ring3_vigente.svg"), (h, "ring3_girado.svg"),
                    (hb, "ring3_girado_com_baias.svg")):
        with open(os.path.join(SAIDAS, nome), "w", encoding="utf-8") as f:
            f.write(svg(d))

    for d in (v, hb, h):
        print(f"{d.codigo:<3} {d.capacidade:>6.0f} pessoas · {d.separadores:>3} "
              f"separadores · {d.barreira_total:6.1f} m · "
              f"{d.meias_voltas:>2} meias-voltas")
    print(f"girado contra vigente: {h.separadores - v.separadores} separadores, "
          f"{h.capacidade - v.capacidade:+.0f} pessoas")


if __name__ == "__main__":
    main()
