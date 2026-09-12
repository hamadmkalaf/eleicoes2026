#!/usr/bin/env python3
"""Injeta as tabelas e diagramas gerados a partir dos dados do TSE no
template de saidas/plano_sinalizacao.html.

Reexecutável: le a distribuicao das mesas pelas entradas, o comparecimento
esperado (base B) e a numeracao MRV de scripts/decisoes.py, os numeros do
Ring 3 de scripts/layout_ring3.py e as posicoes das portas de scripts/salao.py,
e reescreve os blocos marcados com {{PLACEHOLDER}}. O template com os
placeholders vive em saidas/plano_sinalizacao.tmpl.html.
"""
import json
import pathlib
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
DADOS = RAIZ / "saidas" / "dados.json"
TEMPLATE = RAIZ / "saidas" / "plano_sinalizacao.tmpl.html"
SAIDA = RAIZ / "saidas" / "plano_sinalizacao.html"
sys.path.insert(0, str(RAIZ / "scripts"))

import decisoes as DC                                          # noqa: E402
import layout_ring3 as R3                                      # noqa: E402

# Premissas assumidas (não medidas) para o dimensionamento de leitura.
FATOR_PICO = 1.8
SEG_LEITURA = 15
LEITORES_POR_PAINEL = 3
JANELA_H = 9


DEC = DC.montar()


def carrega():
    """As 28 mesas pela numeracao do DJE, com a entrada (A/B/C) e o esperado
    (base B) das decisoes. `mesa` e o MRV; `porta` e a letra da entrada."""
    d = json.loads(DADOS.read_text(encoding="utf-8"))
    urnas = []
    for m in DEC["mesas"]:
        urnas.append({
            "urna": m["principal"],
            "principal": m["principal"],
            "agregada": m["agregada"],
            "aptos": m["aptos"],
            "dublin": m["aptos_dublin"],
            "interior": m["aptos_interior"],
            "esperado": m["esperado"],
            "classe": m["classe"],
            "mesa": m["mrv"],
            "porta": m["entrada"],
        })
    return d, urnas


def distribui(urnas):
    """As mesas de cada entrada, na ordem A, B, C, como scripts/decisoes.py
    as atribuiu (na proporcao da capacidade de cada serpenteado do Ring 3,
    com uma das tres mesas vermelhas em cada entrada)."""
    return [sorted([u for u in urnas if u["porta"] == e["id"]], key=lambda u: u["mesa"])
            for e in DEC["entradas"]]


def tabela_mestra(urnas):
    linhas = []
    for u in urnas:
        linhas.append((u["principal"], u["mesa"], u["porta"]))
        if u["agregada"]:
            linhas.append((u["agregada"], u["mesa"], u["porta"]))
    return sorted(linhas)


def br(n):
    return f"{n:,}".replace(",", ".")


def chip(porta):
    return f'<span class="chip {porta.lower()}">{porta}</span>'


# --------------------------------------------------------------------------
# Diagrama principal da rota
# --------------------------------------------------------------------------

# Geometria do Hall 2 e do Ring 3, em metros: portas de scripts/salao.py (via
# planta_base/layout_ring3), Ring 3 de scripts/layout_ring3.py. ESCALA converte
# para o viewBox.
ESCALA = 5.18          # px por metro
X0, Y0 = 370, 155      # canto noroeste do Hall 2 no viewBox
HALL_L, HALL_P = 50.2, 44.5
# Centro das aberturas da fachada sul, em metros a partir do canto sudoeste.
ABERTURAS = {k: R3.PORTAS_SUL[k] for k in ("S2", "S4", "S5", "S6", "S8")}


def mx(metros):
    return round(X0 + metros * ESCALA)


def diagrama_rota():
    sul = round(Y0 + HALL_P * ESCALA)                 # y da fachada sul
    apron_h = round(14 * ESCALA)                      # apron de 14 m de profundidade
    ring_y = sul + apron_h
    ring_l, ring_p = round(39 * ESCALA), round(35 * ESCALA)
    ring_x = round((mx(ABERTURAS["S5"])) - ring_l / 2)
    fundo_y = ring_y + ring_p - 18                    # corredor de distribuição

    portas = ""
    for nome, cor, letra in (("S4", "--a", "A"), ("S5", "--b", "B"), ("S6", "--c", "C")):
        x = mx(ABERTURAS[nome])
        portas += (
            f'<rect x="{x - 12}" y="{sul - 8}" width="24" height="16" rx="2" fill="var({cor})"/>'
            f'<text x="{x}" y="{sul + 4}" text-anchor="middle" font-family="Archivo,sans-serif"'
            f' font-size="11" font-weight="700" fill="var(--ground)">{letra}</text>'
        )
    for nome in ("S2", "S8"):
        x = mx(ABERTURAS[nome])
        portas += (
            f'<rect x="{x - 12}" y="{sul - 7}" width="24" height="14" rx="2" fill="var(--surface)"'
            f' stroke="var(--muted)" stroke-width="1.5"/>'
            f'<text x="{x}" y="{sul + 22}" text-anchor="middle" font-family="Archivo,sans-serif"'
            f' font-size="9.5" font-weight="600" fill="var(--muted)">saída {nome}</text>'
        )

    # Serpenteados: blocos com a largura e o eixo do plano do Ring 3 (A e C
    # estreitos com baia de flanco, B largo), descarregando nas portas.
    blocos = ""
    eixos_bloco, _ = R3.eixos()
    for i, (cor, nome) in enumerate((("--a", "S4"), ("--b", "S5"), ("--c", "S6"))):
        cx = ring_x + round(eixos_bloco[i] * ESCALA)
        largura = round(R3.LARG_BLOCOS[i] * ESCALA)
        topo = ring_y + 34
        blocos += (
            f'<rect x="{cx - largura // 2}" y="{topo}" width="{largura}"'
            f' height="{fundo_y - topo - 6}" rx="3" fill="var({cor}-soft)"'
            f' stroke="var({cor})" stroke-width="1"/>'
            f'<line x1="{cx}" y1="{topo - 2}" x2="{mx(ABERTURAS[nome])}" y2="{sul + 10}"'
            f' stroke="var({cor})" stroke-width="2.2" marker-end="url(#arw{nome[-1]})"/>'
        )

    discos = [
        (240, 47, "0"), (700, 47, "0"), (570, 100, "1"),
        (668, 200, "2"), (668, 292, "2"), (668, 384, "2"), (668, 476, "2"),
        (ring_x + ring_l + 22, fundo_y + 4, "3"),
        (ring_x + 16, ring_y + 96, "4"),
        (360, sul + 18, "5"),
        (400, 350, "6"),
        (700, 441, "7"),
    ]
    marcas = "".join(
        f'<circle cx="{x}" cy="{y}" r="11" fill="currentColor"/>'
        f'<text x="{x}" y="{y + 4}" text-anchor="middle" font-family="ui-monospace,monospace"'
        f' font-size="11.5" font-weight="700" fill="var(--ground)">{n}</text>'
        for x, y, n in discos
    )
    mesas = "".join(
        f'<rect x="{388 + i * 27}" y="168" width="19" height="7" fill="currentColor" opacity=".28"/>'
        for i in range(9)
    ) + "".join(
        f'<rect x="376" y="{200 + i * 27}" width="7" height="19" fill="currentColor" opacity=".28"/>'
        for i in range(5)
    )

    return f'''<figure>
  <div class="figbox">
    <svg class="diagram" viewBox="0 0 920 740" role="img"
         aria-label="Planta esquemática do RDS Ballsbridge: a rota do eleitor entra pelo portão da Merrion Road, desce pela lateral leste do Hall 2, entra no Ring 3 pela garganta sudeste, percorre um dos três serpenteados e descarrega nas portas S4, S5 e S6 da fachada sul. As saídas S2 e S8 ficam nos flancos, fora do vão das entradas.">
      <defs>
        <marker id="arw" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker>
        <marker id="arw4" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="var(--a)"/></marker>
        <marker id="arw5" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="var(--b)"/></marker>
        <marker id="arw6" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="var(--c)"/></marker>
      </defs>

      <rect x="0" y="26" width="920" height="42" fill="var(--surface-2)"/>
      <text x="16" y="52" font-family="Archivo,sans-serif" font-size="11" font-weight="600"
            letter-spacing="1.6" fill="var(--muted)">MERRION ROAD (R118)</text>
      <line x1="0" y1="76" x2="536" y2="76" stroke="currentColor" stroke-width="2" opacity=".5"/>
      <line x1="604" y1="76" x2="920" y2="76" stroke="currentColor" stroke-width="2" opacity=".5"/>
      <line x1="536" y1="66" x2="536" y2="86" stroke="currentColor" stroke-width="2.5"/>
      <line x1="604" y1="66" x2="604" y2="86" stroke="currentColor" stroke-width="2.5"/>
      <text x="614" y="64" font-family="Archivo,sans-serif" font-size="10.5" font-weight="600"
            fill="var(--alert)">portão de entrada · placa a conferir</text>
      <line x1="880" y1="132" x2="880" y2="102" stroke="currentColor" stroke-width="1.5" marker-end="url(#arw)"/>
      <text x="880" y="94" text-anchor="middle" font-family="Archivo,sans-serif" font-size="10"
            font-weight="700" fill="var(--muted)">N</text>

      <rect x="140" y="180" width="190" height="215" fill="var(--surface-2)" stroke="var(--rule)"/>
      <text x="235" y="292" text-anchor="middle" font-family="Archivo,sans-serif" font-size="12"
            font-weight="600" fill="var(--muted)">HALL 1</text>

      <rect x="{X0}" y="{Y0}" width="{round(HALL_L * ESCALA)}" height="{round(HALL_P * ESCALA)}"
            fill="var(--surface)" stroke="currentColor" stroke-width="1.5"/>
      {mesas}
      <text x="500" y="262" text-anchor="middle" font-family="Archivo,sans-serif" font-size="15"
            font-weight="700" fill="currentColor">HALL 2</text>
      <text x="500" y="280" text-anchor="middle" font-family="Archivo,sans-serif" font-size="10.5"
            fill="var(--muted)">Shelbourne · 50,2 × 44,5 m</text>
      <line x1="392" y1="350" x2="608" y2="350" stroke="var(--muted)" stroke-width="1.2" stroke-dasharray="5 4"/>
      <text x="520" y="342" text-anchor="middle" font-family="Archivo,sans-serif" font-size="10.5"
            fill="var(--muted)">checkpoint interno · mesa → posição</text>

      <rect x="700" y="150" width="190" height="300" fill="none" stroke="var(--rule)"
            stroke-width="1.2" stroke-dasharray="5 4"/>
      <text x="795" y="170" text-anchor="middle" font-family="Archivo,sans-serif" font-size="10.5"
            fill="var(--muted)">estacionamento</text>

      <rect x="345" y="{sul + 2}" width="311" height="{apron_h - 2}" fill="var(--surface-2)"
            stroke="var(--rule)" stroke-width="1"/>
      <text x="352" y="{sul + 40}" font-family="Archivo,sans-serif" font-size="10"
            fill="var(--muted)">apron pavimentado</text>
      {portas}

      <rect x="{ring_x}" y="{ring_y}" width="{ring_l}" height="{ring_p}" rx="6"
            fill="var(--surface)" stroke="var(--rule)" stroke-width="1.5"/>
      <rect x="{ring_x + 6}" y="{fundo_y}" width="{ring_l - 12}" height="13" rx="2"
            fill="var(--surface-2)"/>
      <text x="{ring_x + 10}" y="{ring_y + 17}" text-anchor="start"
            font-family="Archivo,sans-serif" font-size="11" font-weight="600"
            fill="var(--muted)">RING 3 · 39 × 35 m</text>
      {blocos}

      <polyline points="570,78 570,112 668,142 668,{fundo_y + 6} {ring_x + ring_l + 6},{fundo_y + 6}"
                fill="none" stroke="currentColor" stroke-width="3.5" marker-end="url(#arw)"/>
      <text x="528" y="128" text-anchor="end" font-family="Archivo,sans-serif" font-size="11"
            font-weight="600" fill="currentColor">≈150 m · fila e leitura</text>
      <text x="{ring_x + ring_l + 34}" y="{fundo_y + 42}" font-family="Archivo,sans-serif"
            font-size="10.5" fill="var(--muted)">garganta sudeste</text>

      <polyline points="{mx(ABERTURAS['S2'])},{sul + 30} {mx(ABERTURAS['S2'])},{sul + 56} 360,{sul + 56}"
                fill="none" stroke="currentColor" stroke-width="1.8" stroke-dasharray="7 4"
                opacity=".7" marker-end="url(#arw)"/>
      <polyline points="{mx(ABERTURAS['S8'])},{sul + 30} {mx(ABERTURAS['S8'])},{sul + 56} 762,{sul + 56} 762,88"
                fill="none" stroke="currentColor" stroke-width="1.8" stroke-dasharray="7 4"
                opacity=".7" marker-end="url(#arw)"/>
      <text x="772" y="{sul + 44}" font-family="Archivo,sans-serif" font-size="10.5"
            font-weight="600" fill="currentColor">saídas pelos flancos</text>

      <line x1="140" y1="712" x2="399" y2="712" stroke="currentColor" stroke-width="1.5"/>
      <line x1="140" y1="707" x2="140" y2="717" stroke="currentColor" stroke-width="1.5"/>
      <line x1="399" y1="707" x2="399" y2="717" stroke="currentColor" stroke-width="1.5"/>
      <text x="270" y="703" text-anchor="middle" font-family="ui-monospace,monospace" font-size="10"
            fill="var(--muted)">50 m</text>

      {marcas}
    </svg>
    <p class="key">
      <b>0</b> aproximação na Merrion Road e nos demais portões &nbsp;·&nbsp;
      <b>1</b> portão de entrada &nbsp;·&nbsp;
      <b>2</b> corredor da lateral leste, painéis a cada 25–30 m &nbsp;·&nbsp;
      <b>3</b> garganta sudeste do Ring 3 &nbsp;·&nbsp;
      <b>4</b> cabeças dos três serpenteados &nbsp;·&nbsp;
      <b>5</b> portas S4 · S5 · S6, no apron &nbsp;·&nbsp;
      <b>6</b> checkpoint interno &nbsp;·&nbsp;
      <b>7</b> saídas S2 e S8
    </p>
  </div>
  <figcaption>Em escala, sobre as dimensões da ficha técnica do RDS, as portas de <span style="font-family:var(--mono)">scripts/salao.py</span> e o plano do Ring 3 (blocos de {vg(R3.LARG_BLOCOS[0])}, {vg(R3.LARG_BLOCOS[1])} e {vg(R3.LARG_BLOCOS[2])} m, Ring 3 centrado em S5 por estimativa). A consulta acontece toda no trecho 1 → 3, onde as pessoas já estão paradas ou andando; da garganta em diante o eleitor só confirma a sua fila. As três entradas ficam a apenas {vg(R3.PASSO_PORTAS)} m uma da outra, e os serpenteados descarregam em diagonal sobre elas — é por isso que a disciplina de faixa precisa estar resolvida antes, e não na fachada. As saídas S2 e S8 já ficam fora do vão das entradas, então os fluxos se separam sem barreira adicional.</figcaption>
</figure>'''


# --------------------------------------------------------------------------
# Figura: uma consulta contra duas
# --------------------------------------------------------------------------

def figura_consulta():
    def caixa(x, y, w, h, linhas, forte=False, cor="var(--rule)"):
        peso = "600" if forte else "400"
        fundo = "var(--surface-2)" if forte else "var(--surface)"
        out = (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3" fill="{fundo}"'
               f' stroke="{cor}" stroke-width="1.3"/>')
        base = y + h / 2 - (len(linhas) - 1) * 7 + 4
        for i, texto in enumerate(linhas):
            out += (f'<text x="{x + w / 2}" y="{base + i * 14}" text-anchor="middle"'
                    f' font-family="Archivo,sans-serif" font-size="11.5" font-weight="{peso}"'
                    f' fill="currentColor">{texto}</text>')
        return out

    def seta(x1, x2, y):
        return (f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="currentColor"'
                f' stroke-width="1.6" marker-end="url(#arw2)"/>')

    linha1 = (
        caixa(8, 24, 148, 40, ["o eleitor sabe", "a SEÇÃO"]) + seta(162, 194, 44) +
        caixa(200, 24, 168, 40, ["painel 1", "seção → mesa"], cor="var(--alert)") + seta(374, 406, 44) +
        caixa(412, 24, 168, 40, ["painel 2", "mesa → porta"], cor="var(--alert)") + seta(586, 618, 44) +
        caixa(624, 24, 128, 40, ["MESA + PORTA"], forte=True) +
        '<text x="284" y="80" text-anchor="middle" font-family="Archivo,sans-serif" font-size="10"'
        ' font-weight="600" fill="var(--alert)">parada</text>'
        '<text x="496" y="80" text-anchor="middle" font-family="Archivo,sans-serif" font-size="10"'
        ' font-weight="600" fill="var(--alert)">parada</text>'
    )
    linha2 = (
        caixa(8, 112, 148, 40, ["o eleitor sabe", "a SEÇÃO"]) + seta(162, 194, 132) +
        caixa(200, 112, 380, 40,
              ["painel único · 51 linhas ordenadas por seção",
               "seção → mesa → porta"], cor="var(--a)") + seta(586, 618, 132) +
        caixa(624, 112, 128, 40, ["MESA + PORTA"], forte=True) +
        '<text x="390" y="168" text-anchor="middle" font-family="Archivo,sans-serif" font-size="10"'
        ' font-weight="600" fill="var(--a)">uma parada, replicável ao longo do corredor</text>'
    )
    return f'''<figure>
  <div class="figbox">
    <svg class="diagram" viewBox="0 0 760 180" role="img" style="min-width:560px"
         aria-label="Comparação entre duas consultas encadeadas, que criam duas paradas, e uma consulta única que resolve mesa e porta de uma vez.">
      <defs>
        <marker id="arw2" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker>
      </defs>
      <text x="8" y="14" font-family="Archivo,sans-serif" font-size="10.5" font-weight="600"
            letter-spacing=".1em" fill="var(--alert)">COMO NÃO FAZER</text>
      {linha1}
      <text x="8" y="102" font-family="Archivo,sans-serif" font-size="10.5" font-weight="600"
            letter-spacing=".1em" fill="var(--a)">COMO FAZER</text>
      {linha2}
    </svg>
  </div>
  <figcaption>Duas consultas encadeadas criam dois pontos de parada, e cada parada é um servidor de fila. A porta é função determinística da mesa, que é função determinística da seção — então as três colunas cabem no mesmo painel, e o painel pode ser replicado ao longo de todo o percurso.</figcaption>
</figure>'''


# --------------------------------------------------------------------------
# Blocos tabulares
# --------------------------------------------------------------------------

# Os nomes de localidade vêm em caixa alta do CSV do TSE; só um deles tem
# mais de uma palavra e não title-caseia bem.
ROTULOS_LOCALIDADE = {"OUTROS LOCAIS DA IRLANDA": "Outros locais da Irlanda"}


def tabela_localidade(dados, urnas):
    por_secao = {u["principal"]: u for u in urnas}
    for u in urnas:
        if u["agregada"]:
            por_secao[u["agregada"]] = u
    grupos = {}
    for s in dados["secoes"]:
        local = s["Residencia_predominante"]
        if local == "DUBLIN":
            continue
        g = grupos.setdefault(local, {"eleitores": 0, "secoes": []})
        g["eleitores"] += s["Eleitores"]
        g["secoes"].append(s["Secao"])
    linhas = []
    for local in sorted(grupos, key=lambda k: -grupos[k]["eleitores"]):
        g = grupos[local]
        secoes = sorted(g["secoes"])
        destinos = sorted({por_secao[s]["mesa"] for s in secoes})
        alvo = " ".join(
            f'MRV&nbsp;{m}&nbsp;{chip(next(u["porta"] for u in urnas if u["mesa"] == m))}'
            for m in destinos
        )
        rotulo = ROTULOS_LOCALIDADE.get(local, local.title())
        linhas.append(
            f'<tr><td>{rotulo}</td><td class="num">{br(g["eleitores"])}</td>'
            f'<td class="num">{" · ".join(str(s) for s in secoes)}</td>'
            f'<td class="pt">{alvo}</td></tr>'
        )
    return ('<div class="tscroll"><table><thead><tr><th>Localidade de origem</th>'
            '<th class="num">Eleitores</th><th class="num">Seções</th>'
            '<th>Mesa · porta</th></tr></thead><tbody>'
            + "".join(linhas) + "</tbody></table></div>")


def ledger_leitura(total_esperado):
    por_min = total_esperado / (JANELA_H * 60)
    pico = por_min * FATOR_PICO
    simultaneos = pico * SEG_LEITURA / 60
    paineis = -(-simultaneos // LEITORES_POR_PAINEL)
    linhas = [
        ("Comparecimento esperado", f"{br(total_esperado)} eleitores"),
        ("Janela de votação", f"{JANELA_H} h (8h–17h)"),
        ("Chegada média", f"{por_min:.0f} / min"),
        (f"Chegada no pico (premissa: {str(FATOR_PICO).replace('.', ',')}× a média)", f"{pico:.0f} / min"),
        (f"Tempo de leitura por pessoa (premissa)", f"{SEG_LEITURA} s"),
        ("Posições de leitura simultâneas necessárias", f"{simultaneos:.0f}"),
        ("Capacidade de um painel de 1,2 m", f"{LEITORES_POR_PAINEL} leitores"),
    ]
    corpo = "".join(f'<div class="lrow"><span>{a}</span><span>{b}</span></div>' for a, b in linhas)
    corpo += (f'<div class="lrow total"><span>Painéis simultâneos no pico</span>'
              f'<span>{paineis:.0f}</span></div>')
    return f'<div class="ledger">{corpo}</div>'


PONTOS = [
    ("P0", "Aproximação",
     "Calçada da Merrion Road nos dois sentidos, pontos de ônibus e demais portões do RDS (Anglesea / Simmonscourt)",
     "Se o eleitor está no lugar certo e por qual portão entra",
     "ELEIÇÕES BRASILEIRAS 2026 · Entrada de eleitores → · distância",
     "4 painéis (2 na via + 2 de redirecionamento)"),
    ("P1", "Portão de entrada",
     "No vão do portão, cobrindo ou dominando visualmente a placa EXIT fixa",
     "Entrada confirmada · primeira consulta seção → mesa → porta · desvio dos casos sem seção",
     "Pórtico de boas-vindas + tabela mestra completa + “não sabe sua seção? →”",
     "1 pórtico · 3 painéis de consulta · 1 totem do balcão de dúvidas"),
    ("P2", "Corredor da lateral leste",
     "Nos três vãos de parede entre as quatro saídas de emergência, a 10,75 m, 22,50 m e 33,90 m do canto norte; mais dois no gradil, na aproximação",
     "Nada. Repete a consulta durante o tempo morto de caminhada e de fila",
     "A mesma tabela mestra, idêntica em todas · seta “Ring 3 →”",
     "3 painéis de 1,8 × 1,2 m na parede + 2 em lona no gradil"),
    ("P3", "Garganta sudeste",
     "No funil de entrada do Ring 3, junto aos três agentes de pré-triagem",
     "Última consulta possível · divisão nos três serpenteados",
     "Tabela mestra (última ocorrência) + três totens A · B · C com as faixas de mesas",
     "2 painéis · 3 totens de 3 m"),
    ("P4", "Cabeças dos serpenteados",
     "No início de cada bloco, ao longo do corredor de distribuição",
     "Confirmação da fila · captura de quem errou, enquanto ainda cabe corrigir",
     "Identidade da fila (cor ou letra, a decidir) em corpo grande + lista das mesas + “errou? volte ao corredor →”",
     "3 totens · 1 faixa de correção"),
    ("P5", "Portas de entrada",
     "No vidro, à frente de cada vão de entrada da fachada sul, lidas de dentro do serpenteado",
     "Só confirmação de que ali se entra. Nenhuma informação nova",
     "ENTRADA em 300 mm + a identidade da fila que descarrega naquele vão (cor ou letra, a decidir)",
     "3 bandeirolas de fachada"),
    ("P6", "Checkpoint interno",
     "Logo depois das portas, dentro do salão",
     "Mesa → posição física no salão",
     "Faixas suspensas por bloco de mesas + numeração em totem sobre cada mesa",
     "3 faixas suspensas · 28 totens de mesa"),
    ("P7", "Saídas S2 e S8",
     "Nos flancos da fachada sul, fora do vão das entradas — os fluxos já se separam sozinhos",
     "Encaminha para a rua sem reentrar no Ring 3",
     "SAÍDA / WAY OUT → Merrion Road",
     "2 painéis internos · 2 externos"),
]


def tabela_pontos():
    linhas = "".join(
        f'<tr><td class="pt">{cod}<span class="sub">{nome}</span></td>'
        f'<td>{onde}</td><td>{decide}</td><td>{diz}</td><td>{pecas}</td></tr>'
        for cod, nome, onde, decide, diz, pecas in PONTOS
    )
    return ('<div class="tscroll"><table style="min-width:940px"><thead><tr><th>Ponto</th>'
            '<th>Onde fica</th><th>O que decide</th><th>O que a peça diz</th>'
            '<th>Peças</th></tr></thead><tbody>' + linhas + "</tbody></table></div>")


SPECS = [
    ("Portas, no vidro", "300 mm", "Vinil recortado sobre a cortina de vidro da fachada, legível de qualquer ponto do Ring 3, a cerca de 60 m. Sem estrutura e sem base."),
    ("Totens de cabeça de fila", "120 mm", "Leitura a 15 m, acima da linha dos guarda-chuvas. Amarrado na barreira, não plantado no chão."),
    ("Setas do corredor", "120 mm", "Leitura a 25 m, em movimento. Abraçadeira em poste já existente."),
    ("Corpo da tabela mestra", "18 mm", "Três vezes o limite de acuidade a 1,2 m — a tabela é lida em pé, sob chuva, por leitores présbitas."),
    ("Altura de montagem", "≥ 2,5 m", "Uma fila sob guarda-chuvas corta a linha de visão a 1,80 m. Peça baixa é peça invisível."),
    ("Regra de fixação", "sem base", "Colar no vidro, amarrar no gradil e na barreira, abraçar o poste, suspender na treliça. Totem autoportante só onde nada disso existir."),
    ("Material externo", "lona 440 g", "Com ilhoses, para amarrar; PVC alveolar 5 mm onde a peça for plana e abraçada. Entre 40% e 65% de chance de chuva no dia 4, conforme o limiar da fonte."),
    ("Idiomas", "PT + EN", "A sinalização do venue e a equipe do RDS são em inglês; as peças de rua precisam ser bilíngues."),
    ("Código de cor", "3 tons", "Azul, âmbar e magenta — que passam a nomear a porta, não apenas a marcá-la. Nunca verde com vermelho."),
]


def specs():
    cartoes = "".join(
        f'<div class="spec"><h4>{titulo}</h4><span class="big">{valor}</span><p>{nota}</p></div>'
        for titulo, valor, nota in SPECS
    )
    return f'<div class="specs">{cartoes}</div>'


CLASSE_TXT = {"alta": "vermelha", "media": "amarela", "baixa": "verde"}


def tabela_portas(grupos):
    linhas = ""
    for indice, grupo in enumerate(grupos):
        e = DEC["entradas"][indice]
        porta = e["id"]
        pesada = max(grupo, key=lambda u: u["esperado"])
        linhas += (
            f'<tr><td>{chip(porta)} <strong>Entrada {porta}</strong><span class="sub">porta {e["porta"]}</span></td>'
            f'<td>{e["cor"].capitalize()}</td>'
            f'<td class="num">{len(grupo)}<span class="sub">MRV {", ".join(str(u["mesa"]) for u in grupo)}</span></td>'
            f'<td class="num">{br(sum(u["aptos"] for u in grupo))}</td>'
            f'<td class="num">{br(sum(u["esperado"] for u in grupo))}</td>'
            f'<td class="num">{e["capacidade"]}</td>'
            f'<td class="pt">MRV {pesada["mesa"]}<span class="sub">{pesada["esperado"]} esperados</span></td></tr>'
        )
    return linhas


def tabela_mesas(urnas):
    linhas = ""
    for u in sorted(urnas, key=lambda x: x["mesa"]):
        secoes = str(u["principal"]) + (f' + {u["agregada"]}' if u["agregada"] else "")
        origem = "Dublin" if u["interior"] == 0 else f'Dublin + {br(u["interior"])} do interior'
        linhas += (
            f'<tr><td class="pt">MRV {u["mesa"]}</td><td>{chip(u["porta"])}</td>'
            f'<td class="pt">{secoes}'
            f'<span class="sub">{origem}</span></td>'
            f'<td class="num">{br(u["aptos"])}</td><td class="num">{br(u["esperado"])}</td>'
            f'<td>{CLASSE_TXT[u["classe"]]}</td></tr>'
        )
    return ('<div class="tscroll"><table><thead><tr><th>Mesa (MRV)</th><th>Entrada</th>'
            '<th>Seções</th><th class="num">Aptos</th>'
            '<th class="num">Esperado</th><th>Carga</th></tr></thead><tbody>' + linhas + "</tbody></table></div>")


def bloco_mestra(mestra):
    linhas = "".join(
        f'<div class="mrow"><span class="sec">{secao}</span><span class="dots"></span>'
        f'<span class="mesa">MRV {mesa}</span>{chip(porta)}</div>'
        for secao, mesa, porta in mestra
    )
    return f'<div class="mestra">{linhas}</div>'


def bloco_ring3():
    """O trecho do plano que cita o quantitativo do Ring 3, sempre do script."""
    r = R3.resumo()
    caps = r["caps"]
    serp = sum(c["serpenteado"] for c in caps)
    baia = sum(c["baia"] for c in caps)
    return (
        f'os três serpenteados, o corredor de distribuição, a garganta e o fechamento das '
        f'baias de flanco somam <strong>{vg(r["metros"])} m ({r["unidades"]} separadores)</strong>, '
        f'contra {R3.SEPARADORES_EM_MAOS} separadores de barreira ({R3.SEPARADORES_EM_MAOS * R3.METROS_POR_UNIDADE:.0f} m) '
        f'fornecidos pela organizadora — faltam <strong>{r["faltam"]} separadores, ~EUR {br(round(r["custo"]))}</strong>. '
        f'A capacidade resultante é de {serp:.0f} pessoas nos serpenteados mais {baia:.0f} nas duas baias de '
        f'flanco, <strong>{r["total_pessoas"]:.0f} no total</strong> ({", ".join(f"{c[chr(101)+chr(110)+chr(116)+chr(114)+chr(97)+chr(100)+chr(97)]} {c[chr(116)+chr(111)+chr(116)+chr(97)+chr(108)]:.0f}" for c in caps)}). '
        f'Esse estoque de barreira externa é distinto dos 100 unifilas (200 m) do orçamento, que servem ao interior do Hall 2.'
    )


def mesas_pesadas_txt(urnas):
    pes = sorted([u for u in urnas if u["classe"] == "alta"], key=lambda u: u["mesa"])
    return (", ".join(f'MRV {u["mesa"]}' for u in pes[:-1]) + f' e MRV {pes[-1]["mesa"]}'
            + f' (seções {", ".join(str(u["principal"]) for u in pes)}, {min(u["esperado"] for u in pes)} a '
            f'{max(u["esperado"] for u in pes)} comparecentes esperados cada), uma em cada entrada '
            + "(" + ", ".join(f'{u["porta"]}' for u in pes) + ")")


SUBSTRATOS = [
    ("Vidro da fachada sul", "apenas o trecho sul do Hall 2, onde ficam as portas de entrada",
     "sim", "Vinil recortado ou impresso, por dentro e por fora do vão"),
    ("Folha de porta de serviço, aço pintado", "lateral leste, ao longo de todo o corredor",
     "sim", "Vinil sobre a folha — o suporte de P2, se a porta não for rota de fuga em uso"),
    ("Chapa rígida sobre a chapa ondulada", "lateral leste, no padrão da placa “2 Shelbourne Hall”",
     "parafusa", "Painel em mão-francesa preso às terças, como o RDS já faz. Exige furação e autorização"),
    ("Porta de doca e porta de enrolar", "lateral leste, entre as portas de serviço",
     "não", "Perfil ondulado e folha operacional: não colar nem obstruir"),
    ("Folha lisa dos portões do perímetro", "Gate G e congêneres, na Merrion Road",
     "sim", "Vinil ou lona colada, só se o portão ficar travado no dia"),
    ("Painel rebocado liso", "trechos da parede interna do Hall 2",
     "sim", "Vinil removível"),
    ("Gradil de ferro fundido", "~300 m de calçada na Merrion Road",
     "amarra", "Lona com ilhoses e abraçadeiras — método que o próprio RDS usa"),
    ("Barreira metálica de contenção", "Ring 3 e cruzamentos internos",
     "amarra", "Capa de barreira impressa, sobre material já estocado no local"),
    ("Poste de iluminação ou de placa", "calçada e vias internas",
     "abraça", "Chapa de PVC alveolar 5 mm em abraçadeira"),
    ("Treliça metálica do vão, a 7 m", "todo o salão do Hall 2",
     "suspende", "Faixa suspensa em cabo de aço — a única solução com alcance visual no salão"),
    ("Bloco de concreto aparente", "base de todas as paredes do Hall 2",
     "não", "Poroso e rugoso: o adesivo solta. Não orçar vinil aqui"),
    ("Chapa metálica ondulada", "parte alta das paredes, por dentro e por fora",
     "não", "O perfil impede contato pleno: adesivo não. Aceita painel rígido parafusado nas terças"),
    ("Alvenaria de pedra e pilar de granito", "muro do perímetro e portões",
     "não", "Rugoso e provável fabric protegido: nem adesivo nem furação"),
]

FOTOS = [
    ("20260824_114831.jpg", "Gate G, na Merrion Road",
     "Os portões do RDS já são identificados por letra, em painel azul-marinho com letra branca — "
     "exatamente a linguagem visual que uma placa “PORTA A” usaria."),
    ("20260824_115057.jpg", "Gradil da Merrion Road, junto ao ponto de ônibus 480",
     "O RDS já amarra as próprias faixas no gradil. São centenas de metros de fixação pronta, "
     "sem base, ao longo da calçada por onde o eleitor chega."),
    ("20260824_115333.jpg", "Portão com “ENTRY” pintado no piso",
     "A marcação de solo e a placa em bronze organizam circulação de veículos, não de pedestres. "
     "Nenhuma das 21 fotos mostra a placa EXIT citada no briefing."),
    ("20260824_115634.jpg", "Cruzamento interno, com o indicador azul do RDS",
     "Sinalização permanente do venue que o eleitor lerá junto com a nossa — e, à direita, "
     "barreiras metálicas já estocadas: suporte de faixa sem base."),
    ("20260824_115840.jpg", "Fachada envidraçada do Hall 2",
     "A entrada do salão é uma cortina de vidro de pé-direito inteiro, modulada pelos montantes. "
     "É a superfície adesivável ideal, e está onde as letras das portas precisam aparecer."),
    ("20260824_115824.jpg", "Parede interna típica do Hall 2",
     "Bloco de concreto aparente embaixo, chapa ondulada em cima: as duas recusam adesivo. "
     "O que resolve são as treliças a 7 m — fixação suspensa, sem base."),
]


# Parede leste do Hall 2, medida em campo: 44,0 m com quatro saídas de
# emergência. Os centros vêm da planta do RDS (vãos 2.16 a 2.23) reescalados
# para o comprimento informado; a conferência final é com trena no local.
PAREDE_LESTE = 44.0
SAIDAS_LESTE = [4.7, 16.8, 28.2, 39.6]
VAO_SAIDA = 2.0        # largura do vão de emergência
FOLGA_SAIDA = 2.0      # faixa livre exigida de cada lado do vão
PAINEL_L, PAINEL_A = 1.8, 1.2   # painel de consulta, em metros
PAINEL_BASE = 1.0      # altura da borda inferior acima do piso
BASE_LISA = 1.3        # altura presumida do topo da base lisa — a medir


def vaos_leste():
    """Vãos de parede úteis entre as saídas, e onde cabe painel."""
    bordas = [0.0] + SAIDAS_LESTE + [PAREDE_LESTE]
    vaos = []
    for i in range(len(bordas) - 1):
        inicio = FOLGA_SAIDA if i == 0 else bordas[i] + VAO_SAIDA / 2 + FOLGA_SAIDA
        fim = (PAREDE_LESTE - FOLGA_SAIDA if i == len(bordas) - 2
               else bordas[i + 1] - VAO_SAIDA / 2 - FOLGA_SAIDA)
        vaos.append({"inicio": inicio, "fim": fim, "util": fim - inicio,
                     "centro": (inicio + fim) / 2, "extremo": i in (0, len(bordas) - 2)})
    return vaos


def vg(x, casas=1):
    """Número com vírgula decimal, para os rótulos dos desenhos."""
    return f"{x:.{casas}f}".replace(".", ",")


def elevacao_leste():
    x0, larg, solo, topo = 50, 820, 195, 60
    ex, ey = larg / PAREDE_LESTE, 30.0        # px por metro
    def px(m): return x0 + m * ex
    def py(m): return solo - m * ey

    y_base = py(BASE_LISA)
    ribs = "".join(
        f'<line x1="{x0}" y1="{y}" x2="{x0 + larg}" y2="{y}"'
        f' stroke="currentColor" stroke-width="0.7" opacity="0.16"/>'
        for y in range(topo + 9, int(y_base) - 4, 9)
    )

    saidas = ""
    for i, c in enumerate(SAIDAS_LESTE, 1):
        meia, folga = VAO_SAIDA / 2 * ex, FOLGA_SAIDA * ex
        saidas += (
            f'<rect x="{px(c) - meia - folga:.1f}" y="{py(2.1):.1f}"'
            f' width="{(VAO_SAIDA + 2 * FOLGA_SAIDA) * ex:.1f}" height="{2.1 * ey:.1f}"'
            f' fill="var(--alert-soft)"/>'
            f'<rect x="{px(c) - meia:.1f}" y="{py(2.1):.1f}" width="{VAO_SAIDA * ex:.1f}"'
            f' height="{2.1 * ey:.1f}" fill="var(--alert)" fill-opacity="0.55"'
            f' stroke="var(--alert)" stroke-width="1.4"/>'
            f'<text x="{px(c):.1f}" y="{solo + 16}" text-anchor="middle"'
            f' font-family="Archivo,sans-serif" font-size="10.5" font-weight="600"'
            f' fill="var(--alert)">saída {i}</text>'
            f'<text x="{px(c):.1f}" y="{solo + 28}" text-anchor="middle"'
            f' font-family="ui-monospace,monospace" font-size="9"'
            f' fill="var(--muted)">{vg(c)} m</text>'
        )

    paineis, n = "", 0
    for v in vaos_leste():
        if v["extremo"] or v["util"] < PAINEL_L + 0.6:
            continue
        n += 1
        w = PAINEL_L * ex
        paineis += (
            f'<rect x="{px(v["centro"]) - w / 2:.1f}" y="{py(PAINEL_BASE + PAINEL_A):.1f}"'
            f' width="{w:.1f}" height="{PAINEL_A * ey:.1f}" fill="var(--a-soft)"'
            f' stroke="var(--a)" stroke-width="1.8" rx="1.5"/>'
            f'<text x="{px(v["centro"]):.1f}" y="{py(PAINEL_BASE + PAINEL_A) - 7:.1f}"'
            f' text-anchor="middle" font-family="Archivo,sans-serif" font-size="11"'
            f' font-weight="700" fill="var(--a)">P2·{n}</text>'
            f'<text x="{px(v["centro"]):.1f}" y="{py(PAINEL_BASE) + 13:.1f}"'
            f' text-anchor="middle" font-family="ui-monospace,monospace" font-size="9"'
            f' fill="var(--muted)">{vg(v["centro"], 2)} m</text>'
        )

    itens = [
        ("var(--surface-2)", "var(--rule)", "chapa metálica ondulada · adesivo não cola", 236),
        ("var(--surface)", "var(--c)", f"base lisa até ~{vg(BASE_LISA)} m · medir", 158),
        ("var(--alert-soft)", "var(--alert)", f"{vg(FOLGA_SAIDA)} m livres de cada lado do escape", 210),
    ]
    legenda, lx = "", x0
    for preenche, borda, texto, avanco in itens:
        legenda += (
            f'<rect x="{lx}" y="26" width="13" height="10" fill="{preenche}"'
            f' stroke="{borda}" stroke-width="1.2"/>'
            f'<text x="{lx + 19}" y="35" font-family="Archivo,sans-serif" font-size="10.5"'
            f' fill="var(--muted)">{texto}</text>'
        )
        lx += avanco

    return f'''<figure>
  <div class="figbox">
    <svg class="diagram" viewBox="0 0 920 262" role="img" style="min-width:700px"
         aria-label="Elevação da parede leste do Hall 2: 44 metros com quatro saídas de emergência, cada uma com faixa livre de 2 metros de cada lado, e três painéis de consulta de 1,8 por 1,2 metro centrados nos vãos entre elas. Uma linha tracejada marca o topo da base lisa, altura que precisa ser medida porque decide se o painel cola ou precisa ser parafusado.">
      <rect x="{x0}" y="{topo}" width="{larg}" height="{y_base - topo:.1f}"
            fill="var(--surface-2)" stroke="var(--rule)" stroke-width="1"/>
      {ribs}
      <rect x="{x0}" y="{y_base:.1f}" width="{larg}" height="{solo - y_base:.1f}"
            fill="var(--surface)" stroke="var(--rule)" stroke-width="1"/>
      {saidas}
      {paineis}
      <line x1="{x0}" y1="{y_base:.1f}" x2="{x0 + larg}" y2="{y_base:.1f}"
            stroke="var(--c)" stroke-width="1.8" stroke-dasharray="7 4"/>
      {legenda}
      <line x1="{x0}" y1="{solo}" x2="{x0 + larg}" y2="{solo}" stroke="currentColor" stroke-width="2.2"/>
      <line x1="{x0}" y1="{solo + 42}" x2="{x0 + larg}" y2="{solo + 42}" stroke="currentColor" stroke-width="1"/>
      <line x1="{x0}" y1="{solo + 37}" x2="{x0}" y2="{solo + 47}" stroke="currentColor" stroke-width="1"/>
      <line x1="{x0 + larg}" y1="{solo + 37}" x2="{x0 + larg}" y2="{solo + 47}" stroke="currentColor" stroke-width="1"/>
      <text x="{x0 + larg / 2}" y="{solo + 58}" text-anchor="middle" font-family="ui-monospace,monospace"
            font-size="10.5" font-weight="600" fill="currentColor">{vg(PAREDE_LESTE)} m · parede leste do Hall 2</text>
    </svg>
  </div>
  <figcaption>Três painéis de 1,8 × 1,2 m, um por vão entre saídas, com a borda inferior a 1,0 m do piso — centrados a 10,75 m, 22,50 m e 33,90 m do canto norte, ~11,5 m um do outro. Os dois vãos de extremidade não recebem peça: as saídas 1 e 4 ficam a menos de 5 m dos cantos e a folga de 2,0 m consome o trecho inteiro. A linha tracejada é o que decide o método de fixação — se a base lisa subir acima de 2,2 m, o painel cola; se parar em ~1,3 m como parece, ele atravessa a chapa ondulada e tem de ser rígido, parafusado nas terças.</figcaption>
</figure>'''


def tabela_substrato():
    marca = {
        "sim": '<span class="chip a">cola</span>',
        "amarra": '<span class="chip b">amarra</span>',
        "abraça": '<span class="chip b">abraça</span>',
        "suspende": '<span class="chip b">suspende</span>',
        "parafusa": '<span class="chip c">parafusa</span>',
        "não": '<span class="chip x">não</span>',
    }
    linhas = "".join(
        f"<tr><td><strong>{sup}</strong><span class='sub'>{onde}</span></td>"
        f"<td>{marca[modo]}</td><td>{peca}</td></tr>"
        for sup, onde, modo, peca in SUBSTRATOS
    )
    return ('<div class="tscroll"><table><thead><tr><th>Superfície</th>'
            '<th>Fixação</th><th>Peça</th></tr></thead>'
            f"<tbody>{linhas}</tbody></table></div>")


def figura_fotos():
    import base64
    import io

    try:
        from PIL import Image
    except ModuleNotFoundError as erro:  # pragma: no cover
        raise SystemExit("este gerador precisa de Pillow: pip install pillow") from erro

    itens = []
    for nome, titulo, texto in FOTOS:
        caminho = RAIZ / "data" / "fotos" / nome
        assert caminho.exists(), f"foto ausente: {caminho}"
        imagem = Image.open(caminho)
        imagem.thumbnail((820, 820))
        buffer = io.BytesIO()
        imagem.convert("RGB").save(buffer, "JPEG", quality=72, optimize=True)
        dados = base64.b64encode(buffer.getvalue()).decode()
        itens.append(
            '<figure class="foto">'
            f'<img src="data:image/jpeg;base64,{dados}" alt="{titulo}" loading="lazy">'
            f"<figcaption><b>{titulo}</b>{texto}</figcaption></figure>"
        )
    return '<div class="fotos">' + "".join(itens) + "</div>"


def main():
    dados, urnas = carrega()
    grupos = distribui(urnas)
    mestra = tabela_mestra(urnas)
    assert len(mestra) == dados["total_secoes"], "a tabela mestra precisa cobrir as 51 seções"
    assert len({s for s, _, _ in mestra}) == len(mestra), "seção duplicada na tabela mestra"
    total_esperado = sum(u["esperado"] for u in urnas)

    html = TEMPLATE.read_text(encoding="utf-8")
    for chave, valor in {
        "ESPERADO": br(total_esperado),
        "RING3_BARREIRA": bloco_ring3(),
        "MESAS_PESADAS": mesas_pesadas_txt(urnas),
        "DIAGRAMA": diagrama_rota(),
        "FIG_CONSULTA": figura_consulta(),
        "TAB_LOCALIDADE": tabela_localidade(dados, urnas),
        "LEDGER_LEITURA": ledger_leitura(total_esperado),
        "TAB_PONTOS": tabela_pontos(),
        "SPECS": specs(),
        "TAB_SUBSTRATO": tabela_substrato(),
        "FIG_FOTOS": figura_fotos(),
        "ELEVACAO": elevacao_leste(),
        "TAB_PORTAS": tabela_portas(grupos),
        "TAB_MESAS": tabela_mesas(urnas),
        "TAB_MESTRA": bloco_mestra(mestra),
    }.items():
        marcador = "{{" + chave + "}}"
        assert marcador in html, f"marcador ausente no template: {marcador}"
        html = html.replace(marcador, valor)
    assert "{{" not in html, "sobrou marcador sem substituição"

    SAIDA.write_text(html, encoding="utf-8")
    print(f"gravado {SAIDA.relative_to(RAIZ)}")
    for indice, grupo in enumerate(grupos):
        print(f"  entrada {DEC['entradas'][indice]['id']} ({DEC['entradas'][indice]['porta']}): {len(grupo)} mesas, "
              f"{sum(u['esperado'] for u in grupo)} comparecentes esperados")
    print(f"  total esperado {total_esperado} · {len(mestra)} seções na tabela mestra")


if __name__ == "__main__":
    main()
