#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ring 3 — a fila externa do Hall 2, em quatro desenhos.

O plano vigente da fila externa (Ring 3 do RDS, 44,0 x 35,0 m medidos, 14 m ao sul da
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
# Medida oficial do Ring 3: 44,0 x 35,0 m. A posicao lateral continua sendo
# estimativa — o retangulo esta centrado no eixo de S5, e o bordo oeste ainda
# precisa ser aferido em campo.
LARG_RING, PROF_RING = 44.0, 35.0
_EIXO_S5 = 28.285
RING = {"x0": _EIXO_S5 - LARG_RING / 2, "x1": _EIXO_S5 + LARG_RING / 2,
        "y0": -49.0, "y1": -49.0 + PROF_RING}
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
VAO_SAIDA = 1.40       # abertura do portao de saida, na borda norte da zona
PERDA_MEIA_VOLTA = 0.60   # fila perdida em cada meia-volta (analise de sensibilidade)

SEPARADOR_M = 2.00     # 1 separador = 2 m de barreira
SEPARADOR_EUR = 13.02  # EUR 1.303,00 / 100 unidades (item d do orcamento)
ESTOQUE_SEPARADORES = 200

POR_METRO_RAIA = RAIA_UTIL * DENS_FILA     # pessoas por metro de raia

# geometria
LARG_BAIA = 6.40       # baia de flanco, cada lado
LARG_CORREDOR = 3.00   # corredor de chegada, encostado no gradil do Ring

# O corredor de chegada e um L: entra pelo canto nordeste do Ring, junto da
# porta C, desce rente ao gradil leste e vira no fundo, ao sul. As zonas sao
# alimentadas pelo trecho de fundo. Quem separa a zona C do trecho lateral e
# a unica barreira de contencao que sobra fora das divisorias — o resto do
# contorno e gradil permanente ou fita de delimitacao.
CORREDOR_LATERAL = "leste"
# Blocos do plano vigente, medidos do diagrama publicado — usados so na
# reconstrucao que serve de aferição.
BLOCOS_ORIG = {"A": (15.16, 19.36), "B": (22.09, 34.69), "C": (37.19, 41.39)}
LARG_RING_ORIGINAL = 38.99   # a largura estimada com que aquele plano foi feito

# Sem faixa de garganta: o corredor de fundo vai para o limite sul do Ring e os
# serpenteados comecam logo acima dele. Sobra para fila tudo o que nao e
# corredor.
PROF_SERP = (RING["y1"] - RING["y0"]) - LARG_CORREDOR

# O plano vigente, que serve de aferição, tinha outra reparticao: 23,75 m de
# serpenteado, 3,0 m de corredor com barreira nos dois lados e 8,25 m de faixa
# de garganta ao sul. Esses numeros ficam so na reconstrucao.
PROF_PLANO_ORIGINAL = 23.75
CORREDOR_ORIGINAL = 36.70
FUNIL_GARGANTA = 12.0


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
    oeste_no_gradil: bool = False   # o lado oeste coincide com o gradil do Ring
    leste_no_gradil: bool = False   # idem, a leste

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

        A topologia da barreira decide, e ela e diferente nas duas orientacoes.
        Na vertical as divisorias correm norte-sul e as meias-voltas abrem a
        borda norte de duas em duas raias: a fila so pode sair pelo fim da
        ultima raia, num dos dois cantos do bloco — escolhe-se o canto mais
        perto da porta, pela paridade do numero de raias. Na horizontal a
        ultima raia corre rente a borda norte, que e barreira continua: o
        portao pode ser aberto em qualquer x dela, e vai para o eixo da porta.
        """
        alvo = eixo_porta(self.nome)
        if self.orientacao == "vertical":
            return self.x0 if abs(alvo - self.x0) <= abs(alvo - self.x1) else self.x1
        return min(max(alvo, self.x0), self.x1)

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

    # -- barreira ---------------------------------------------------------
    # A conta tem duas parcelas, e a primeira e a que fecha o perimetro da
    # zona: sem ela a fila vaza pelos lados. Sao quatro lados:
    #   norte  — de frente para o apron, precisa de barreira menos o portao;
    #   sul    — encosta no corredor de fundo, cuja parede norte ja fecha;
    #   oeste/leste — de barreira, exceto onde coincidem com o gradil do Ring.
    # A segunda parcela sao as divisorias internas, que separam raia de raia.
    @property
    def perimetro(self) -> float:
        """Contorno da zona — hoje resolvido com fita, nao com barreira.

        O gradil do Ring ja fecha o compound; entre zonas, a delimitacao e
        fita. Este numero nao entra na conta de separadores: fica registrado
        para quem for comprar a fita, e para medir o que se abre mao.
        """
        lados = (self.larg - VAO_SAIDA)                       # norte, menos o portao
        if not self.oeste_no_gradil:
            lados += self.prof
        if not self.leste_no_gradil:
            lados += self.prof
        return lados

    @property
    def divisorias(self) -> float:
        n, L = self.raias, self.comp
        if n <= 1:
            return 0.0
        return (n - 1) * max(0.0, L - VAO_RETORNO)

    @property
    def barreira(self) -> float:
        """So as divisorias: o contorno da zona e fita, nao separador."""
        return self.divisorias

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
        b = {"divisórias entre as raias": sum(z.divisorias for z in self.zonas)}
        b.update(self.barreira_extra)
        return b

    @property
    def fora_da_conta(self) -> dict:
        """O que seria barreira se as decisoes do Posto fossem outras.

        Fica registrado para dar o tamanho do que se esta abrindo mao — e
        para a conta voltar a fechar se alguma dessas decisoes mudar.
        """
        return {
            "contorno das zonas (hoje, fita)":
                sum(math.dist(a, b) for _, a, b in segmentos_da_fita(self)),
            "parede do corredor de chegada":
                (RING["x1"] - RING["x0"]) - len(self.zonas) * VAO_SAIDA,
            "raias do apron até as portas": sum(2 * z.diagonal for z in self.zonas),
        }

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


def _largura_equivalente_da_baia() -> float:
    """Quantos metros de serpenteado valem uma baia de flanco, em lotacao.

    A baia guarda LARG_BAIA x prof x DENS_BAIA pessoas; um metro de largura de
    serpenteado guarda prof x POR_METRO_RAIA / PASSO_RAIA. A profundidade
    cancela, entao a equivalencia nao depende dela.
    """
    return LARG_BAIA * DENS_BAIA / (POR_METRO_RAIA / PASSO_RAIA)


def _reparte_largura(disponivel: float, snap: bool, com_baias: bool) -> dict:
    """Reparte a largura entre as tres zonas.

    O criterio nao e a largura, e a lotacao: cada entrada deve ficar com
    lotacao proporcional ao comparecimento que espera. Onde ha baia de flanco,
    ela ja entrega lotacao as zonas A e C — entao essas duas recebem menos
    largura de serpenteado, exatamente o equivalente da baia.

    `snap` arredonda para um numero inteiro de raias, o que a orientacao
    vertical exige: ali a largura da zona e feita de raias.
    """
    baia = _largura_equivalente_da_baia() if com_baias else 0.0
    equivalente = disponivel + 2 * baia
    alvo = {e: equivalente * ESPERADO[e] / ESPERADO_TOTAL - (baia if e != "B" else 0.0)
            for e in ESPERADO}
    if not snap:
        return alvo
    total = int(disponivel / PASSO_RAIA + 0.02)
    exato = {e: max(0.0, alvo[e]) / PASSO_RAIA for e in alvo}
    n = {e: int(exato[e]) for e in exato}
    sobra = total - sum(n.values())
    ordem = sorted(exato, key=lambda k: exato[k] - n[k], reverse=True)
    for i in range(max(0, sobra)):
        n[ordem[i % 3]] += 1
    return {e: n[e] * PASSO_RAIA for e in n}


def x_util() -> tuple:
    """Faixa de largura que sobra para as zonas, tirado o corredor lateral."""
    if CORREDOR_LATERAL == "leste":
        return RING["x0"], RING["x1"] - LARG_CORREDOR
    return RING["x0"] + LARG_CORREDOR, RING["x1"]


def _zonas(orientacao: str, com_baias: bool, prof: float,
           vao_min: float = 2.00) -> tuple:
    """Monta as tres zonas dentro do Ring, com ou sem as baias de flanco.

    Devolve (zonas, vao) — o vao entre zonas absorve a sobra do arredondamento,
    e nunca fica menor que `vao_min`.
    """
    xa, xb = x_util()
    disponivel = (xb - xa) - 2 * vao_min
    larg = _reparte_largura(disponivel, orientacao == "vertical", com_baias=False)
    vao = ((xb - xa) - sum(larg.values())) / 2
    x = xa
    z = []
    for e in ("A", "B", "C"):
        z.append(Zona(e, x, x + larg[e], prof, orientacao,
                      oeste_no_gradil=abs(x - RING["x0"]) < 0.05,
                      leste_no_gradil=abs(x + larg[e] - RING["x1"]) < 0.05))
        x += larg[e] + vao
    return z, vao


def _baias_de_flanco(prof: float | None = None) -> dict:
    p = PROF_SERP if prof is None else prof
    return {"A": ("baia do flanco oeste", LARG_BAIA * p),
            "C": ("baia do flanco leste", LARG_BAIA * p)}


def _separacao_do_corredor(prof: float) -> dict:
    """CCB entre a zona C e o trecho lateral do corredor de chegada.

    E a unica contencao fora das divisorias: de um lado a fila parada da zona
    C, do outro a corrente que desce do canto nordeste para o fundo. Fita nao
    serve aqui — sao dois fluxos em sentidos diferentes encostados.
    """
    return {"separação entre a zona C e o corredor": prof}


def desenho_plano_vigente() -> Desenho:
    """Reconstrucao do plano vigente, com a faixa de garganta que ele tinha.

    Cotas lidas do diagrama publicado na pagina "Rota do Eleitor": blocos de
    4,2 / 12,6 / 4,2 m (3 / 9 / 3 raias), 23,75 m de raia, corredor de fundo de
    3,0 m com barreira dos dois lados, baias de 6,4 m nos flancos e 8,25 m de
    faixa de garganta ao sul. Serve so de aferição — os quatro desenhos usam a
    reparticao nova, sem garganta.
    """
    z = [Zona(e, *BLOCOS_ORIG[e], PROF_PLANO_ORIGINAL, "vertical")
         for e in ("A", "B", "C")]
    d = Desenho("PV", "Plano vigente, reconstruído",
                "Raias norte-sul de 23,75 m, baias nos flancos e faixa de "
                "garganta ao sul.",
                z, _baias_de_flanco(PROF_PLANO_ORIGINAL),
                {"corredor de fundo (2 lados)": 2 * CORREDOR_ORIGINAL,
                 "fechamento das baias de flanco": 2 * LARG_BAIA,
                 "funil da garganta sudeste": 2 * FUNIL_GARGANTA})
    return d


VAO_ENTRE_ZONAS = 2.60


def desenho_girado(raias: int | None = None) -> Desenho:
    """O desenho: raias leste-oeste, sem baias, zonas na largura toda do Ring.

    Tirar as baias devolve os 12,8 m dos dois flancos as tres zonas. Cada zona
    fica com a largura proporcional ao comparecimento que ela espera — e essa
    largura e, agora, o comprimento da raia. `raias` fixa quantas raias cada
    zona tem (a profundidade sai disso); sem argumento, usa a faixa inteira,
    do corredor de fundo ate a borda norte do Ring.
    """
    prof = PROF_SERP if raias is None else min(raias * PASSO_RAIA, PROF_SERP)
    z, _ = _zonas("horizontal", com_baias=False, prof=prof,
                  vao_min=VAO_ENTRE_ZONAS)
    d = Desenho("H", "Serpenteados horizontais (raias leste-oeste)",
                "Raias leste-oeste empilhadas; as três zonas ocupam a largura "
                "toda do Ring e toda a lotação é fila em raia medida.",
                z, {}, _separacao_do_corredor(prof))
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


def _reparte_raias(total: int) -> dict:
    """Reparte `total` raias entre as tres zonas, proporcional ao esperado."""
    exato = {e: total * ESPERADO[e] / ESPERADO_TOTAL for e in ESPERADO}
    n = {e: int(exato[e]) for e in exato}
    sobra = total - sum(n.values())
    for e in sorted(exato, key=lambda k: exato[k] - n[k], reverse=True)[:sobra]:
        n[e] += 1
    return n


def desenho_vertical_sem_baias(vao: float = 2.00) -> Desenho:
    """O primeiro cenario — raias norte-sul — sem as baias de flanco.

    As barreiras laterais sao removiveis, entao a evacuacao nao precisa de baia
    reservada: sai pelos vaos entre as zonas e pelo gradil. Isso libera os
    12,8 m dos dois flancos para serpenteado. Como na vertical a largura da
    zona e um numero inteiro de raias, as larguras sao arredondadas para o
    modulo de 1,4 m e a sobra vai para os vaos entre zonas.
    """
    z, folga = _zonas("vertical", com_baias=False, prof=PROF_SERP, vao_min=vao)
    d = Desenho("VS", "Serpenteados verticais (raias norte-sul)",
                "Raias norte-sul, as três zonas ocupando a largura toda do "
                "Ring; toda a lotação é fila em raia medida.",
                z, {}, _separacao_do_corredor(PROF_SERP))
    d.notas = [
        "Sem baias: os 12,8 m dos dois flancos viram serpenteado, e toda a "
        "lotação é fila em raia medida.",
        "A evacuação sai pelos vãos de "
        f"{folga:.2f} m entre as zonas e pelo gradil, porque as barreiras "
        "laterais são removíveis — não é preciso reservar baia para isso.",
        "É o desenho de maior lotação dos quatro, e o mais caro em barreira: "
        "raia norte-sul de 23,75 m é longa, e divisória longa é divisória cara.",
        "A saída continua presa a um canto do bloco: na vertical a borda norte "
        "é aberta pelas meias-voltas, então o portão não pode ser movido para "
        "o eixo da porta como na horizontal.",
    ]
    return d


def escada_de_profundidade() -> list:
    """Para o desenho vertical sem baias, a alavanca e a profundidade da raia."""
    fora = []
    for prof in (12.0, 16.0, 20.0, 24.0, 28.0, PROF_SERP):
        base = desenho_vertical_sem_baias()
        z = [Zona(k.nome, k.x0, k.x1, prof, "vertical", k.oeste_no_gradil,
                  k.leste_no_gradil) for k in base.zonas]
        d = Desenho(base.codigo, base.nome, base.resumo, z, {},
                    _separacao_do_corredor(prof))
        fora.append({
            "profundidade_m": round(prof, 2),
            "capacidade": round(d.capacidade),
            "por_entrada": {e: round(x) for e, x in d.cap_por_entrada().items()},
            "barreira_m": round(d.barreira_total, 1),
            "separadores": d.separadores,
            "compra": d.compra,
            "custo_compra_eur": round(d.custo_compra, 2),
        })
    return fora


def escada_de_raias() -> list:
    """Capacidade contra separadores, variando o numero de raias por zona."""
    fora = []
    for n in range(6, int(PROF_SERP / (PASSO_RAIA - TOL_PASSO)) + 1):
        d = desenho_girado(n)
        if d.zonas[0].raias != n:
            break
        fora.append({
            "raias_por_zona": n,
            "profundidade_m": round(d.zonas[0].prof, 2),
            "capacidade": round(d.capacidade),
            "por_entrada": {e: round(x) for e, x in d.cap_por_entrada().items()},
            "barreira_m": round(d.barreira_total, 1),
            "separadores": d.separadores,
            "compra": d.compra,
            "custo_compra_eur": round(d.custo_compra, 2),
        })
    return fora


def confere_original(v: Desenho) -> dict:
    """`v` aqui e o desenho_plano_vigente(), nao um dos quatro."""
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
                          f"{z.nome} · {z.raias} raias de "
                          f"{z.comp:.1f} m".replace(".", ","), 11,
                          peso=700, cor=c, halo="#eef1f4"))
        else:
            for i in range(1, z.raias):
                y = y_base + i * z.passo
                a = z.x0 + VAO_RETORNO if i % 2 else z.x0
                b = z.x1 if i % 2 else z.x1 - VAO_RETORNO
                p.append(_linha(a, y, b, y, stroke=c, stroke_width="1",
                                stroke_opacity=".6"))
            p.append(_txt((z.x0 + z.x1) / 2, y_topo + 1.3,
                          f"{z.nome} · {z.raias} × {z.comp:.1f} m".replace(".", ","),
                          11, peso=700,
                          cor=c, halo="#eef1f4"))
        p.append(_linha(z.portao, y_topo, eixo_porta(z.nome), -0.4, stroke=c,
                        stroke_width="2", marker_end="url(#seta)"))
    cy0, cy1 = RING["y0"], RING["y0"] + LARG_CORREDOR
    xc = RING["x1"] - LARG_CORREDOR
    p.append(_ret(xc, RING["y0"], RING["x1"], RING["y1"], fill="#16867f",
                  fill_opacity=".10", stroke="#5c6c80", stroke_width="1"))
    p.append(_ret(RING["x0"], cy0, xc, cy1, fill="#16867f", fill_opacity=".10",
                  stroke="#5c6c80", stroke_width="1"))
    p.append(_txt(xc + LARG_CORREDOR / 2, RING["y1"] - 9.0,
                  f"CORREDOR · {LARG_CORREDOR:.1f} m".replace(".", ","), 10,
                  peso=600, cor="#0f6b64", rot=-90, halo="#f6f4ef"))
    p.append(_txt((RING["x0"] + xc) / 2, (cy0 + cy1) / 2 - 0.4,
                  "TRECHO DE FUNDO", 10, peso=600, cor="#0f6b64"))
    p.append(_linha(RING["x1"] - LARG_CORREDOR / 2, RING["y1"] + 3.2,
                    RING["x1"] - LARG_CORREDOR / 2, RING["y1"] - 1.5,
                    stroke="#0f6b64", stroke_width="2.2",
                    marker_end="url(#seta)"))
    p.append(_txt(RING["x1"] - LARG_CORREDOR - 0.8, RING["y1"] + 2.4,
                  "entrada · canto nordeste", 10, anchor="end", cor="#0f6b64"))
    p.append(_txt(RING["x0"] - 0.4, RING["y0"] - 1.6,
                  f"gradil permanente do Ring 3 · {LARG_RING:.1f} × "
                  f"{PROF_RING:.1f} m".replace(".", ","), 10,
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
        "fora_da_conta": {k: round(x, 1) for k, x in d.fora_da_conta.items()},
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


def markdown(h: Desenho, escada: list, vs: Desenho, escada_v: list,
             pv: Desenho) -> str:
    conf = confere_original(pv)
    L = []
    A = L.append
    dois = [("N–S", vs), ("L–O", h)]
    xa, xb = x_util()

    A("# Ring 3 — dois desenhos de fila\n")
    A(f"O compound de fila ao ar livre do RDS mede **{n(LARG_RING,1)} × "
      f"{n(PROF_RING,1)} m** (medida oficial) e fica {n(APRON,0)} m ao sul da "
      "fachada do Hall 2. Este documento traz os dois desenhos que sobraram — "
      "raias norte-sul e raias leste-oeste — e a conta de separadores de cada "
      "um.\n")

    A("## O percurso e a moldura\n")
    A("A entrada **não** é pelo fundo. O eleitor entra pelo **canto nordeste** "
      "do Ring, o mais perto da porta C, desce rente ao gradil leste e vira no "
      "fundo: o corredor de chegada é um **L**, com um trecho lateral a leste "
      f"e um trecho de fundo ao sul, ambos de {n(LARG_CORREDOR,1)} m. As três "
      "zonas são alimentadas pelo trecho de fundo, e descarregam ao norte nas "
      "portas S4, S5 e S6.\n")
    A("Duas consequências de geometria:\n")
    A(f"- O trecho lateral consome {n(LARG_CORREDOR,1)} m da largura do Ring. "
      f"Sobram **{n(xb - xa,1)} m** para as zonas, não os {n(LARG_RING,1)} m "
      "inteiros.")
    A("- A zona C fica encostada nesse trecho lateral, com a fila parada de um "
      "lado e a corrente que desce do outro. **É a única contenção de verdade "
      "que o desenho ainda pede**, e por isso é o único CCB fora das "
      "divisórias.\n")

    A("## O que entra na conta de separadores\n")
    A("Por decisão do Posto, três itens que o modelo contava saíram:\n")
    A("| Item | Por que saiu | Quanto era (N–S) |")
    A("|---|---|---:|")
    fora = vs.fora_da_conta
    A(f"| Contorno das zonas | O gradil já fecha o compound; entre zonas, a "
      f"delimitação é **fita** | {n(fora['contorno das zonas (hoje, fita)'],1)} m |")
    A(f"| Parede do corredor de chegada | Fora da conta | "
      f"{n(fora['parede do corredor de chegada'],1)} m |")
    A(f"| Raias do apron até as portas | Fora da conta | "
      f"{n(fora['raias do apron até as portas'],1)} m |")
    A(f"| **Total retirado** | | **{n(sum(fora.values()),1)} m** — "
      f"{unidades(sum(fora.values()))} separadores |")
    A("")
    A("Sobram dois componentes, e só eles são separadores:\n")
    A("| Componente | " + " | ".join(k for k, _ in dois) + " |")
    A("|---|" + "---:|" * len(dois))
    for rot, chave in (("Divisórias entre as raias", "divisórias entre as raias"),
                       ("Separação da zona C / corredor",
                        "separação entre a zona C e o corredor")):
        A(f"| {rot} | " + " | ".join(f"{n(d.barreira[chave],1)} m"
                                     for _, d in dois) + " |")
    A("| **Total** | " + " | ".join(f"**{n(d.barreira_total,1)} m**"
                                    for _, d in dois) + " |")
    A("| **Separadores de 2 m** | " + " | ".join(f"**{d.separadores}**"
                                                 for _, d in dois) + " |")
    A(f"| A comprar (estoque {ESTOQUE_SEPARADORES}) | " +
      " | ".join(str(d.compra) for _, d in dois) + " |")
    A("| Custo da compra | " + " | ".join(f"EUR {n(d.custo_compra,2)}"
                                          for _, d in dois) + " |")
    A("")
    A(f"A fita de delimitação é outro material e outro fornecedor: são "
      f"{n(fora['contorno das zonas (hoje, fita)'],1)} m no desenho N–S e "
      f"{n(h.fora_da_conta['contorno das zonas (hoje, fita)'],1)} m no "
      "girado.\n")

    A("## Os dois desenhos\n")
    A("| | " + " | ".join(k for k, _ in dois) + " |")
    A("|---|" + "---:|" * len(dois))
    A("| Lotação (toda em raia) | " + " | ".join(n(d.capacidade) for _, d in dois) + " |")
    A("| Raias por zona | " + " | ".join(
        "/".join(str(z.raias) for z in d.zonas) for _, d in dois) + " |")
    A("| Raia | " + " | ".join(
        f"{n(min(z.comp for z in d.zonas),1)}–{n(max(z.comp for z in d.zonas),1)} m"
        for _, d in dois) + " |")
    A("| Meias-voltas | " + " | ".join(str(d.meias_voltas) for _, d in dois) + " |")
    A("| Separadores | " + " | ".join(str(d.separadores) for _, d in dois) + " |")
    A("| Metros por pessoa | " + " | ".join(n(d.m_por_pessoa, 3)
                                            for _, d in dois) + " |")
    A("")
    A("A diferença entre os dois continua sendo ruído na barreira — o "
      "perímetro saiu da conta e o que sobra são as divisórias, que mudam "
      f"`0,14 × (profundidade − largura)` por zona. O que separa os dois é "
      "outra coisa: a **descarga**. Na horizontal a última raia corre rente à "
      "borda norte, que é linha contínua, e o portão pode ir para o eixo da "
      "porta; na vertical a fila sai pelo fim da última raia, num canto.\n")
    A("| Zona | " + " | ".join(f"desvio {k}" for k, _ in dois) + " |")
    A("|---|" + "---:|" * len(dois))
    for e in ("A", "B", "C"):
        A(f"| {e} | " + " | ".join(
            f"{n(abs(eixo_porta(e) - d.zona(e).portao),2)} m" for _, d in dois) + " |")
    A("")

    A("## O desenho norte-sul, zona a zona\n")
    A("| Zona | Porta | Largura | Raias | Raia | Caminhada | Lotação | "
      "Esperado | por eleitor |")
    A("|---|---|---:|---:|---:|---:|---:|---:|---:|")
    for z in vs.zonas:
        A(f"| {z.nome} | {PORTAS[z.nome]['porta']} | {n(z.larg,2)} m | "
          f"{z.raias} | {n(z.comp,2)} m | {n(z.caminhada)} m | "
          f"{n(z.capacidade)} | {n(ESPERADO[z.nome])} | "
          f"{n(vs.equilibrio()[z.nome],4)} |")
    A("")

    A("## Quanta barreira comprar\n")
    A(f"O estoque da organizadora é de {ESTOQUE_SEPARADORES} separadores "
      f"({n(ESTOQUE_SEPARADORES*SEPARADOR_M)} m). Com a conta reduzida aos dois "
      "componentes, a alavanca é a mesma de antes: a profundidade da raia no "
      "desenho N–S, o número de raias no girado.\n")
    A("| Profundidade | Lotação | Separadores | A comprar | Custo |")
    A("|---:|---:|---:|---:|---:|")
    for r in escada_v:
        marca = " ←" if abs(r["profundidade_m"] - PROF_SERP) < 0.01 else ""
        A(f"| {n(r['profundidade_m'],2)} m{marca} | {n(r['capacidade'])} | "
          f"{r['separadores']} | {r['compra']} | EUR {n(r['custo_compra_eur'],2)} |")
    A("")
    cabe = [r for r in escada_v if r["compra"] == 0]
    if cabe:
        A(f"Dentro do estoque, sem comprar nada: {n(cabe[-1]['profundidade_m'],1)} m "
          f"de raia, {n(cabe[-1]['capacidade'])} pessoas.\n")
    A("| Raias por zona | Profundidade | Lotação | Separadores | A comprar |")
    A("|---:|---:|---:|---:|---:|")
    for r in escada:
        marca = " ←" if r["raias_por_zona"] == h.zonas[0].raias else ""
        A(f"| {r['raias_por_zona']}{marca} | {n(r['profundidade_m'],1)} m | "
          f"{n(r['capacidade'])} | {r['separadores']} | {r['compra']} |")
    A("")

    A("## Premissas e aderência\n")
    A("| Parâmetro | Valor | Origem |")
    A("|---|---|---|")
    A(f"| Ring | {n(LARG_RING,1)} × {n(PROF_RING,1)} m | medida oficial |")
    A(f"| Corredor de chegada | {n(LARG_CORREDOR,1)} m, em L (leste + fundo) | decisão do Posto |")
    A(f"| Módulo da raia | {n(PASSO_RAIA,2)} m | reconstruído |")
    A(f"| Largura livre da raia | {n(RAIA_UTIL,2)} m | reconstruído |")
    A(f"| Densidade em raia | {n(DENS_FILA,1)} pessoas/m² | reconstruído |")
    A(f"| Vão de meia-volta | {n(VAO_RETORNO,1)} m | premissa |")
    A(f"| Separador | {n(SEPARADOR_M,1)} m · EUR {n(SEPARADOR_EUR,2)} | item d do orçamento |")
    A(f"| Estoque | {ESTOQUE_SEPARADORES} unidades | informado pelo Posto |")
    A("")
    A("O plano vigente foi reconstruído das cotas publicadas e continua "
      f"servindo de aferição do modelo de densidade: {n(conf['raias_calculado'],1)} "
      f"contra {n(conf['raias_publicado'])} publicados nos serpenteados, "
      f"{n(conf['baias_calculado'],1)} contra {n(conf['baias_publicado'])} nas "
      "baias.\n")

    A("## Pendências de campo\n")
    A("1. **Fita não contém massa.** A decisão de delimitar as zonas com fita, "
      "e não com barreira, vale enquanto a fila estiver ordenada. Num pico, "
      "nada impede fisicamente que alguém passe da zona A para a B — e a "
      "separação por porta, que é a razão de existir da pré-triagem, depende "
      "disso. Vale decidir se algum trecho crítico volta a ser CCB, sobretudo "
      "junto às cabeças de fila, onde a pressão é maior.\n")
    A("2. **A corrente que desce e a saída S8.** A entrada pelo canto nordeste "
      "cruza o apron a leste, que é justamente onde S8 despeja quem já votou. "
      "Sem raias no apron, os dois fluxos dividem o mesmo espaço — decidir se "
      "isso se resolve com sinalização, fiscal ou horário.\n")
    A("3. **A largura do trecho lateral.** Os "
      f"{n(LARG_CORREDOR,1)} m assumidos vêm do corredor de fundo. Se a "
      "corrente de entrada pedir mais, cada metro sai da largura das zonas — "
      "e, no desenho N–S, tirar 1,4 m tira uma raia inteira.\n")
    A("4. **Onde a pré-triagem acontece.** Continua sem endereço dentro do "
      "Ring: o corredor em L é de passagem, não de parada.\n")
    return "\n".join(L) + "\n"


def svg_mapa(d: Desenho) -> str:
    """Planta com cada corrida de barreira colorida pelo seu componente."""
    legenda_alt = 16.0
    larg = (RING["x1"] - RING["x0"] + 12) * ESCALA + 2 * MARGEM
    alt = (RING["y1"] - RING["y0"] + APRON + 6 + legenda_alt) * ESCALA + 2 * MARGEM
    p = []
    # fundo: apron, gradil do Ring, fachada e portas
    p.append(_ret(RING["x0"] - 5, -APRON, RING["x1"] + 5, 0, fill="#eef1f4"))
    p.append(_ret(RING["x0"], RING["y0"], RING["x1"], RING["y1"], fill="#faf9f5",
                  stroke=GRADIL["cor"], stroke_width=str(GRADIL["traco"]),
                  stroke_dasharray="7 4"))
    p.append(_linha(RING["x0"] - 5, 0, RING["x1"] + 5, 0, stroke="#1c2733",
                    stroke_width="3"))
    p.append(_txt((RING["x0"] + RING["x1"]) / 2, 1.2, "FACHADA SUL DO HALL 2", 11,
                  peso=700, cor="#5c6c80"))
    for e, dd in PORTAS.items():
        p.append(_linha(dd["x0"], 0, dd["x1"], 0, stroke=CORES[e], stroke_width="6"))
        p.append(_txt(eixo_porta(e), -1.6, f'{dd["porta"]} · {e}', 11, peso=700,
                      cor=CORES[e]))
    for nome, (a, b) in SAIDAS_FACHADA.items():
        p.append(_linha(a, 0, b, 0, stroke="#b26a12", stroke_width="6"))
    # fundo das zonas, so para localizar
    for z in d.zonas:
        p.append(_ret(z.x0, RING["y1"] - z.prof, z.x1, RING["y1"],
                      fill=CORES[z.nome], fill_opacity=".07"))
        p.append(_txt((z.x0 + z.x1) / 2, RING["y1"] - z.prof / 2,
                      f"zona {z.nome}", 12, peso=700, cor=CORES[z.nome],
                      halo="#faf9f5"))
    # corredor de chegada, em L
    xc = RING["x1"] - LARG_CORREDOR
    p.append(_ret(xc, RING["y0"], RING["x1"], RING["y1"], fill="#16867f",
                  fill_opacity=".10"))
    p.append(_ret(RING["x0"], RING["y0"], xc, RING["y0"] + LARG_CORREDOR,
                  fill="#16867f", fill_opacity=".10"))
    p.append(_txt(xc + LARG_CORREDOR / 2, RING["y1"] - 9.0, "corredor de chegada",
                  11, cor="#0f6b64", rot=-90, halo="#faf9f5"))
    p.append(_txt((RING["x0"] + xc) / 2, RING["y0"] + LARG_CORREDOR / 2 - 0.4,
                  "trecho de fundo", 11, cor="#0f6b64", halo="#faf9f5"))
    p.append(_linha(RING["x1"] - LARG_CORREDOR / 2, RING["y1"] + 3.0,
                    RING["x1"] - LARG_CORREDOR / 2, RING["y1"] - 2.0,
                    stroke="#0f6b64", stroke_width="2.4",
                    marker_end="url(#seta)"))
    p.append(_txt(RING["x1"] - LARG_CORREDOR - 0.8, RING["y1"] + 2.0,
                  "entrada · canto nordeste", 10, anchor="end", cor="#0f6b64"))
    # fita de delimitacao das zonas — fora da conta de separadores
    for _, p1, p2 in segmentos_da_fita(d):
        p.append(_linha(p1[0], p1[1], p2[0], p2[1], stroke=FITA["cor"],
                        stroke_width=str(FITA["traco"]), stroke_dasharray="3 5"))
    # as barreiras, uma cor por componente
    seg = segmentos_do_desenho(d)
    for comp, p1, p2 in seg:
        e = COMPONENTES[comp]
        p.append(_linha(p1[0], p1[1], p2[0], p2[1], stroke=e["cor"],
                        stroke_width=str(e["traco"]), stroke_linecap="round"))
    # portoes: as aberturas que a conta desconta
    for z in d.zonas:
        for y in (RING["y1"],):
            p.append(_linha(z.portao - VAO_SAIDA / 2, y, z.portao + VAO_SAIDA / 2, y,
                            stroke="#faf9f5", stroke_width="5"))
            p.append(_linha(z.portao - VAO_SAIDA / 2, y, z.portao + VAO_SAIDA / 2, y,
                            stroke="#b26a12", stroke_width="1.6",
                            stroke_dasharray="2 2"))
    p.append(_txt(RING["x0"], RING["y0"] - 1.6,
                  f"gradil permanente do Ring 3 · {LARG_RING:.1f} × "
                  f"{PROF_RING:.1f} m · não entra na conta".replace(".", ","),
                  10, anchor="start", cor=GRADIL["cor"]))
    p.append(_txt(RING["x1"], RING["y0"] - 1.6,
                  f"portões de {VAO_SAIDA:.1f} m, descontados".replace(".", ","),
                  10, anchor="end", cor="#b26a12"))
    # legenda: o mesmo total que a conta soma
    soma = soma_dos_segmentos(seg)
    y = RING["y0"] - 4.0
    p.append(_txt(RING["x0"], y, "O QUE CADA COR CUSTA", 11, anchor="start",
                  peso=700, cor="#1f2c3c"))
    y -= 2.4
    for comp, e in COMPONENTES.items():
        if not soma.get(comp):
            continue
        p.append(_linha(RING["x0"], y + 0.4, RING["x0"] + 2.2, y + 0.4,
                        stroke=e["cor"], stroke_width=str(max(3.0, e["traco"])),
                        stroke_linecap="round"))
        p.append(_txt(RING["x0"] + 3.0, y + 0.9, comp, 11, anchor="start",
                      cor="#243244"))
        p.append(_txt(RING["x0"] + 30.0, y + 0.9,
                      f"{soma[comp]:.1f} m".replace(".", ","), 11, anchor="end",
                      cor="#243244"))
        p.append(_txt(RING["x0"] + 41.0, y + 0.9,
                      f"{unidades(soma[comp])} separadores", 11, anchor="end",
                      cor="#5c6c80"))
        y -= 2.2
    p.append(_linha(RING["x0"], y + 1.4, RING["x0"] + 41.0, y + 1.4,
                    stroke="#c6cfc8", stroke_width="1"))
    p.append(_txt(RING["x0"] + 3.0, y + 0.6, "total", 11, anchor="start",
                  peso=700, cor="#1f2c3c"))
    p.append(_txt(RING["x0"] + 30.0, y + 0.6,
                  f"{d.barreira_total:.1f} m".replace(".", ","), 11, anchor="end",
                  peso=700, cor="#1f2c3c"))
    p.append(_txt(RING["x0"] + 41.0, y + 0.6, f"{d.separadores} separadores", 11,
                  anchor="end", peso=700, cor="#1f2c3c"))
    y -= 2.6
    fita = sum(math.dist(a, b) for _, a, b in segmentos_da_fita(d))
    p.append(_linha(RING["x0"], y + 0.4, RING["x0"] + 2.2, y + 0.4,
                    stroke=FITA["cor"], stroke_width="3", stroke_dasharray="3 4"))
    p.append(_txt(RING["x0"] + 3.0, y + 0.9,
                  "contorno das zonas — fita, não separador", 11, anchor="start",
                  cor="#5c6c80"))
    p.append(_txt(RING["x0"] + 30.0, y + 0.9, f"{fita:.1f} m".replace(".", ","),
                  11, anchor="end", cor="#5c6c80"))
    y -= 2.2
    p.append(_linha(RING["x0"], y + 0.4, RING["x0"] + 2.2, y + 0.4,
                    stroke=GRADIL["cor"], stroke_width="3", stroke_dasharray="7 4"))
    p.append(_txt(RING["x0"] + 3.0, y + 0.9,
                  "gradil permanente do Ring — já existe", 11, anchor="start",
                  cor="#5c6c80"))
    corpo = "\n".join(p)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {larg:.0f} '
            f'{alt:.0f}" width="{larg:.0f}" height="{alt:.0f}" role="img">\n'
            f'<rect width="{larg:.0f}" height="{alt:.0f}" fill="#fbfaf7"/>\n'
            f'{MARCADOR}\n'
            f'{_txt(RING["x0"], 3.4, "Mapa dos separadores · " + d.nome, 15, anchor="start", peso=700)}\n'
            f'{corpo}\n</svg>\n')



def main() -> None:
    os.makedirs(SAIDAS, exist_ok=True)
    pv = desenho_plano_vigente()
    vs = desenho_vertical_sem_baias()
    h = desenho_girado()
    escada = escada_de_raias()
    escada_v = escada_de_profundidade()

    with open(os.path.join(SAIDAS, "ring3.json"), "w", encoding="utf-8") as f:
        json.dump({
            "gerado_por": "scripts/ring3.py", "ring": RING, "apron_m": APRON,
            "premissas": {
                "passo_raia_m": PASSO_RAIA, "raia_util_m": RAIA_UTIL,
                "densidade_fila_p_m2": DENS_FILA, "densidade_baia_p_m2": DENS_BAIA,
                "vao_retorno_m": VAO_RETORNO,
                "vao_saida_m": VAO_SAIDA,
                "vao_entre_zonas_m": VAO_ENTRE_ZONAS,
                "perda_por_meia_volta_m": PERDA_MEIA_VOLTA,
                "profundidade_serpenteado_m": PROF_SERP,
                "largura_baia_m": LARG_BAIA,
                "largura_corredor_m": LARG_CORREDOR,
                "profundidade_plano_vigente_m": PROF_PLANO_ORIGINAL,
                "separador_m": SEPARADOR_M, "separador_eur": SEPARADOR_EUR,
                "estoque_separadores": ESTOQUE_SEPARADORES,
                "comparecimento_esperado": ESPERADO,
            },
            "aderencia_ao_plano_original": confere_original(pv),
            "plano_vigente_reconstruido": bloco_json(pv),
            "girado": bloco_json(h),
            "vertical_sem_baias": bloco_json(vs),
            "escada_de_raias": escada,
            "escada_de_profundidade": escada_v,
        }, f, ensure_ascii=False, indent=2)
    with open(os.path.join(SAIDAS, "plano_ring3_horizontal.md"), "w",
              encoding="utf-8") as f:
        f.write(markdown(h, escada, vs, escada_v, pv))
    for d, nome in ((vs, "ring3_vertical_sem_baias.svg"),
                    (h, "ring3_girado.svg")):
        with open(os.path.join(SAIDAS, nome), "w", encoding="utf-8") as f:
            f.write(svg(d))
        mapa = nome.replace("ring3_", "ring3_barreiras_")
        with open(os.path.join(SAIDAS, mapa), "w", encoding="utf-8") as f:
            f.write(svg_mapa(d))
        divergencia = {c: v for c, v in confere_mapa(d).items()
                       if abs(v[0] - v[1]) > 0.05}
        if divergencia:
            raise SystemExit(f"mapa nao bate com a conta em {d.codigo}: {divergencia}")

    for d in (vs, h):
        print(f"{d.codigo:<3} {d.capacidade:>6.0f} pessoas · {d.separadores:>3} "
              f"separadores · {d.barreira_total:6.1f} m · "
              f"{d.meias_voltas:>2} meias-voltas")



# --------------------------------------------------------------------------
# 8. Mapa das barreiras
#
# Cada corrida de barreira que a conta soma vira um segmento desenhado, e o
# total de cada componente sai da soma dos proprios segmentos: o mapa e a
# conta, nao uma ilustracao dela. `confere_mapa()` garante isso.
# --------------------------------------------------------------------------
COMPONENTES = {
    "divisórias entre as raias":             {"cor": "#7a8794", "traco": 1.6},
    "separação entre a zona C e o corredor": {"cor": "#b23b2e", "traco": 3.4},
}
FITA = {"cor": "#1f6fb2", "traco": 1.4}
GRADIL = {"cor": "#8a919b", "traco": 2.0}


def _y_faixa() -> tuple:
    """Borda sul e borda norte da faixa de serpenteado."""
    return RING["y1"] - PROF_SERP, RING["y1"]


def segmentos_da_zona(z: Zona) -> list:
    """A barreira que a zona `z` pede, segmento a segmento.

    So as divisorias internas: o contorno da zona e fita, e o gradil do Ring
    fecha o compound. A unica excecao esta em `segmentos_do_desenho`, no lado
    da zona C que encosta no corredor de chegada.
    """
    y0, y1 = RING["y1"] - z.prof, RING["y1"]
    seg = []
    # divisorias internas, cada uma encurtada de VAO_RETORNO numa ponta
    for i in range(1, z.raias):
        if z.orientacao == "vertical":
            x = z.x0 + i * z.passo
            a, b = (y0 + VAO_RETORNO, y1) if i % 2 else (y0, y1 - VAO_RETORNO)
            seg.append(("divisórias entre as raias", (x, a), (x, b)))
        else:
            y = y0 + i * z.passo
            a, b = (z.x0 + VAO_RETORNO, z.x1) if i % 2 else (z.x0, z.x1 - VAO_RETORNO)
            seg.append(("divisórias entre as raias", (a, y), (b, y)))
    return seg


def segmentos_da_fita(d: Desenho) -> list:
    """O contorno das zonas, que hoje e fita e nao entra na conta de CCB."""
    seg = []
    for z in d.zonas:
        y0, y1 = RING["y1"] - z.prof, RING["y1"]
        g0 = min(max(z.portao - VAO_SAIDA / 2, z.x0), z.x1 - VAO_SAIDA)
        for a, b in ((z.x0, g0), (g0 + VAO_SAIDA, z.x1)):
            if b - a > 1e-6:
                seg.append(("fita", (a, y1), (b, y1)))
        if not z.oeste_no_gradil:
            seg.append(("fita", (z.x0, y0), (z.x0, y1)))
        if not z.leste_no_gradil and z.nome != "C":
            seg.append(("fita", (z.x1, y0), (z.x1, y1)))
    return seg


def segmentos_do_desenho(d: Desenho) -> list:
    seg = []
    for z in d.zonas:
        seg += segmentos_da_zona(z)
    # CCB entre a zona C e o trecho lateral do corredor de chegada
    zc = d.zona("C")
    seg.append(("separação entre a zona C e o corredor",
                (zc.x1, RING["y1"] - zc.prof), (zc.x1, RING["y1"])))
    return seg


def soma_dos_segmentos(seg: list) -> dict:
    fora = {}
    for comp, p1, p2 in seg:
        fora[comp] = fora.get(comp, 0.0) + math.dist(p1, p2)
    return fora


def confere_mapa(d: Desenho) -> dict:
    """O mapa desenhado tem de somar o mesmo que a conta de barreira."""
    mapa = soma_dos_segmentos(segmentos_do_desenho(d))
    conta = d.barreira
    return {c: (round(conta.get(c, 0.0), 2), round(mapa.get(c, 0.0), 2))
            for c in set(conta) | set(mapa)}

if __name__ == "__main__":
    main()
