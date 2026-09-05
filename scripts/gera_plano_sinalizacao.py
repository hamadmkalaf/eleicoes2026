#!/usr/bin/env python3
"""Injeta as tabelas e diagramas gerados a partir dos dados do TSE no
template de saidas/plano_sinalizacao.html.

Reexecutável: recalcula a distribuição das mesas pelas portas a partir de
saidas/dados.json e reescreve os blocos marcados com {{PLACEHOLDER}}.
O template com os placeholders vive em saidas/plano_sinalizacao.tmpl.html.
"""
import json
import pathlib

RAIZ = pathlib.Path(__file__).resolve().parent.parent
DADOS = RAIZ / "saidas" / "dados.json"
TEMPLATE = RAIZ / "saidas" / "plano_sinalizacao.tmpl.html"
SAIDA = RAIZ / "saidas" / "plano_sinalizacao.html"

# Taxas de comparecimento observadas em 2022, por domicílio do eleitor.
TAXA_DUBLIN = 0.74
TAXA_INTERIOR = 0.50
# Premissas assumidas (não medidas) para o dimensionamento de leitura.
FATOR_PICO = 1.8
SEG_LEITURA = 15
LEITORES_POR_PAINEL = 3
JANELA_H = 9


def carrega():
    d = json.loads(DADOS.read_text(encoding="utf-8"))
    residencia = {r["Urna"]: r for r in d["residencia_urna"]}
    urnas = []
    for u in d["urnas"]:
        r = residencia[u["Urna"]]
        dublin, total = r["DUBLIN"], r["TOTAL"]
        interior = total - dublin
        agregada = u["Secao_agregada"]
        urnas.append({
            "urna": u["Urna"],
            "principal": u["Secao_principal"],
            "agregada": int(agregada) if agregada == agregada else None,
            "aptos": total,
            "dublin": dublin,
            "interior": interior,
            "esperado": round(dublin * TAXA_DUBLIN + interior * TAXA_INTERIOR),
        })
    return d, urnas


def distribui(urnas):
    """Reparte as urnas em 3 portas equilibrando o comparecimento esperado.

    Distribuição em serpentina sobre a lista ordenada por comparecimento
    decrescente: equilibra os totais e, de quebra, separa as mesas mais
    pesadas uma por porta. As mesas são numeradas em blocos contíguos por
    porta, para que a placa possa dizer "Mesas 1-9" em vez de listar 28.
    """
    ordenadas = sorted(urnas, key=lambda u: -u["esperado"])
    grupos = [[], [], []]
    for i, u in enumerate(ordenadas):
        volta = (i // 3) % 2 == 0
        grupos[(i % 3) if volta else (2 - i % 3)].append(u)
    mesa = 1
    for indice, grupo in enumerate(grupos):
        grupo.sort(key=lambda u: u["principal"])
        for u in grupo:
            u["mesa"] = mesa
            u["porta"] = "ABC"[indice]
            mesa += 1
    return grupos


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

# Geometria do Hall 2 e do Ring 3, em metros, conforme a ficha técnica do RDS e
# as medições de saidas/plano_ring3.md (PR #6). ESCALA converte para o viewBox.
ESCALA = 5.18          # px por metro
X0, Y0 = 370, 155      # canto noroeste do Hall 2 no viewBox
HALL_L, HALL_P = 50.2, 44.5
# Aberturas da fachada sul, em metros a partir do canto sudoeste (prancheta do Posto).
ABERTURAS = {"S2": 13.7, "S4": 21.9, "S5": 28.1, "S6": 34.3, "S8": 42.6}


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

    # Serpenteados: blocos de 7,0 m a passo de 9,0 m, descarregando nas portas.
    blocos = ""
    passo = round(9 * ESCALA)
    largura = round(7 * ESCALA)
    centro_b = mx(ABERTURAS["S5"])
    for desloc, cor, nome in ((-passo, "--a", "S4"), (0, "--b", "S5"), (passo, "--c", "S6")):
        cx = centro_b + desloc
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
            fill="var(--alert)">placa fixa do venue: EXIT</text>
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
  <figcaption>Em escala, sobre as dimensões da ficha técnica do RDS e as medições do plano do Ring 3. A consulta acontece toda no trecho 1 → 3, onde as pessoas já estão paradas ou andando; da garganta em diante o eleitor só confirma a letra. As três entradas ficam a apenas 6,2 m uma da outra, e os serpenteados, a 9,0 m de passo, descarregam em diagonal sobre elas — é por isso que a disciplina de faixa precisa estar resolvida antes, e não na fachada. As saídas S2 e S8 já ficam fora do vão das entradas, então os fluxos se separam sem barreira adicional.</figcaption>
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
            f'M{m}&nbsp;{chip(next(u["porta"] for u in urnas if u["mesa"] == m))}'
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
     "A cada 25–30 m ao longo do percurso, alternando os lados",
     "Nada. Repete a consulta durante o tempo morto de caminhada e de fila",
     "A mesma tabela mestra, idêntica em todos · seta “Ring 3, 100 m”",
     "4 painéis duplos (8 faces)"),
    ("P3", "Garganta sudeste",
     "No funil de entrada do Ring 3, junto aos três agentes de pré-triagem",
     "Última consulta possível · divisão nos três serpenteados",
     "Tabela mestra (última ocorrência) + três totens A · B · C com as faixas de mesas",
     "2 painéis · 3 totens de 3 m"),
    ("P4", "Cabeças dos serpenteados",
     "No início de cada bloco de 7,0 m, ao longo do corredor de distribuição",
     "Confirmação da letra · captura de quem errou, enquanto ainda cabe corrigir",
     "Letra em corpo grande + faixa de mesas + “errou? volte ao corredor →”",
     "3 totens · 1 faixa de correção"),
    ("P5", "Portas S4 · S5 · S6",
     "Sobre cada vão de entrada da fachada sul, lidas de dentro do serpenteado",
     "Só confirmação. Nenhuma informação nova",
     "Letra de 300 mm + lista das mesas atendidas",
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
    ("Portas A · B · C", "300 mm", "Altura de letra para leitura de qualquer ponto do Ring 3, a cerca de 60 m."),
    ("Totens de cabeça de fila", "120 mm", "Leitura a 15 m, acima da linha dos guarda-chuvas."),
    ("Setas do corredor", "120 mm", "Leitura a 25 m, em movimento."),
    ("Corpo da tabela mestra", "18 mm", "Três vezes o limite de acuidade a 1,2 m — a tabela é lida em pé, sob chuva, por leitores présbitas."),
    ("Altura de montagem", "≥ 2,5 m", "Uma fila sob guarda-chuvas corta a linha de visão a 1,80 m. Peça baixa é peça invisível."),
    ("Material", "PVC 5 mm", "Alveolar em base d'água, ou lona com ilhoses. Entre 40% e 65% de chance de chuva no dia 4, conforme o limiar da fonte."),
    ("Idiomas", "PT + EN", "A placa do venue e a equipe do RDS são em inglês; a sinalização de rua precisa ser bilíngue."),
    ("Código de cor", "3 tons", "Azul, âmbar e magenta. Nunca verde com vermelho, e a cor nunca aparece sem a letra."),
]


def specs():
    cartoes = "".join(
        f'<div class="spec"><h4>{titulo}</h4><span class="big">{valor}</span><p>{nota}</p></div>'
        for titulo, valor, nota in SPECS
    )
    return f'<div class="specs">{cartoes}</div>'


def tabela_portas(grupos):
    cores = {"A": "Azul", "B": "Âmbar", "C": "Magenta"}
    linhas = ""
    for indice, grupo in enumerate(grupos):
        porta = "ABC"[indice]
        pesada = max(grupo, key=lambda u: u["esperado"])
        linhas += (
            f'<tr><td>{chip(porta)} <strong>Porta {porta}</strong></td>'
            f'<td>{cores[porta]}</td>'
            f'<td class="num">{len(grupo)}<span class="sub">M{grupo[0]["mesa"]}–M{grupo[-1]["mesa"]}</span></td>'
            f'<td class="num">{br(sum(u["aptos"] for u in grupo))}</td>'
            f'<td class="num">{br(sum(u["esperado"] for u in grupo))}</td>'
            f'<td class="pt">M{pesada["mesa"]}<span class="sub">{pesada["esperado"]} esperados</span></td></tr>'
        )
    return linhas


def tabela_mesas(urnas):
    linhas = ""
    for u in sorted(urnas, key=lambda x: x["mesa"]):
        secoes = str(u["principal"]) + (f' + {u["agregada"]}' if u["agregada"] else "")
        origem = "Dublin" if u["interior"] == 0 else f'Dublin + {br(u["interior"])} do interior'
        linhas += (
            f'<tr><td class="pt">M{u["mesa"]}</td><td>{chip(u["porta"])}</td>'
            f'<td class="num">{u["urna"]}</td><td class="pt">{secoes}'
            f'<span class="sub">{origem}</span></td>'
            f'<td class="num">{br(u["aptos"])}</td><td class="num">{br(u["esperado"])}</td></tr>'
        )
    return ('<div class="tscroll"><table><thead><tr><th>Mesa</th><th>Porta</th>'
            '<th class="num">Urna</th><th>Seções</th><th class="num">Aptos</th>'
            '<th class="num">Esperado</th></tr></thead><tbody>' + linhas + "</tbody></table></div>")


def bloco_mestra(mestra):
    linhas = "".join(
        f'<div class="mrow"><span class="sec">{secao}</span><span class="dots"></span>'
        f'<span class="mesa">M{mesa}</span>{chip(porta)}</div>'
        for secao, mesa, porta in mestra
    )
    return f'<div class="mestra">{linhas}</div>'


def main():
    dados, urnas = carrega()
    grupos = distribui(urnas)
    mestra = tabela_mestra(urnas)
    assert len(mestra) == dados["total_secoes"], "a tabela mestra precisa cobrir as 51 seções"
    assert len({s for s, _, _ in mestra}) == len(mestra), "seção duplicada na tabela mestra"
    total_esperado = sum(u["esperado"] for u in urnas)

    html = TEMPLATE.read_text(encoding="utf-8")
    for chave, valor in {
        "DIAGRAMA": diagrama_rota(),
        "FIG_CONSULTA": figura_consulta(),
        "TAB_LOCALIDADE": tabela_localidade(dados, urnas),
        "LEDGER_LEITURA": ledger_leitura(total_esperado),
        "TAB_PONTOS": tabela_pontos(),
        "SPECS": specs(),
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
        print(f"  porta {'ABC'[indice]}: {len(grupo)} mesas, "
              f"{sum(u['esperado'] for u in grupo)} comparecentes esperados")
    print(f"  total esperado {total_esperado} · {len(mestra)} seções na tabela mestra")


if __name__ == "__main__":
    main()
