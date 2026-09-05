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

def diagrama_rota():
    discos = [
        (240, 47, "0"), (700, 47, "0"),
        (570, 100, "1"),
        (668, 190, "2"), (668, 262, "2"), (668, 334, "2"), (668, 406, "2"),
        (652, 470, "3"),
        (340, 470, "4"),
        (352, 397, "5"),
        (400, 350, "6"),
        (700, 240, "7"),
    ]
    marcas = "".join(
        f'<circle cx="{x}" cy="{y}" r="11" fill="currentColor"/>'
        f'<text x="{x}" y="{y + 4}" text-anchor="middle" font-family="ui-monospace,monospace"'
        f' font-size="11.5" font-weight="700" fill="var(--ground)">{n}</text>'
        for x, y, n in discos
    )

    # Mesas sugeridas encostadas nas paredes norte e oeste do salão.
    mesas_norte = "".join(
        f'<rect x="{388 + i * 27}" y="168" width="19" height="7" fill="currentColor" opacity=".28"/>'
        for i in range(9)
    )
    mesas_oeste = "".join(
        f'<rect x="{376}" y="{200 + i * 27}" width="7" height="19" fill="currentColor" opacity=".28"/>'
        for i in range(5)
    )

    portas = ""
    for x, cor, letra in ((410, "--a", "A"), (480, "--b", "B"), (550, "--c", "C")):
        portas += (
            f'<rect x="{x - 17}" y="385" width="34" height="16" rx="2" fill="var({cor})"/>'
            f'<text x="{x}" y="397" text-anchor="middle" font-family="Archivo,sans-serif"'
            f' font-size="12" font-weight="700" fill="var(--ground)">{letra}</text>'
            f'<line x1="{x}" y1="448" x2="{x}" y2="407" stroke="var({cor})" stroke-width="2.5"'
            f' marker-end="url(#arw{letra})"/>'
            f'<rect x="{x - 16}" y="470" width="32" height="86" rx="3" fill="var({cor}-soft)"'
            f' stroke="var({cor})" stroke-width="1"/>'
        )

    return f'''<figure>
  <div class="figbox">
    <svg class="diagram" viewBox="0 0 920 660" role="img"
         aria-label="Planta esquemática do RDS Ballsbridge mostrando a rota do eleitor do portão da Merrion Road, pela lateral leste do Hall 2, até o Ring 3 e as portas A, B e C da fachada sul, com a saída em circuito pela fachada leste.">
      <defs>
        <marker id="arw" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker>
        <marker id="arwA" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="var(--a)"/></marker>
        <marker id="arwB" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="var(--b)"/></marker>
        <marker id="arwC" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="var(--c)"/></marker>
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

      <rect x="370" y="155" width="260" height="240" fill="var(--surface)" stroke="currentColor" stroke-width="1.5"/>
      {mesas_norte}{mesas_oeste}
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

      <rect x="300" y="452" width="330" height="150" rx="8" fill="var(--surface)"
            stroke="var(--rule)" stroke-width="1.5"/>
      <text x="316" y="590" font-family="Archivo,sans-serif" font-size="11.5" font-weight="600"
            fill="var(--muted)">RING 3 · área de fila</text>
      {portas}

      <polyline points="570,78 570,112 668,142 668,432 668,470 642,470" fill="none"
                stroke="currentColor" stroke-width="3.5" marker-end="url(#arw)"/>
      <text x="690" y="128" font-family="Archivo,sans-serif" font-size="11" font-weight="600"
            fill="currentColor">≈150 m · fila e leitura</text>
      <text x="292" y="443" text-anchor="end" font-family="Archivo,sans-serif" font-size="10.5"
            fill="var(--muted)">triagem já resolvida</text>

      <rect x="626" y="232" width="8" height="26" fill="var(--muted)"/>
      <polyline points="636,245 790,245 790,88" fill="none" stroke="currentColor" stroke-width="2"
                stroke-dasharray="7 4" opacity=".75" marker-end="url(#arw)"/>
      <text x="800" y="300" font-family="Archivo,sans-serif" font-size="11" font-weight="600"
            fill="currentColor">saída</text>
      <text x="800" y="316" font-family="Archivo,sans-serif" font-size="10.5"
            fill="var(--muted)">não cruza a fila</text>

      <line x1="140" y1="632" x2="399" y2="632" stroke="currentColor" stroke-width="1.5"/>
      <line x1="140" y1="627" x2="140" y2="637" stroke="currentColor" stroke-width="1.5"/>
      <line x1="399" y1="627" x2="399" y2="637" stroke="currentColor" stroke-width="1.5"/>
      <text x="270" y="623" text-anchor="middle" font-family="ui-monospace,monospace" font-size="10"
            fill="var(--muted)">50 m</text>

      {marcas}
    </svg>
    <p class="key">
      <b>0</b> aproximação na Merrion Road e nos demais portões &nbsp;·&nbsp;
      <b>1</b> portão de entrada &nbsp;·&nbsp;
      <b>2</b> corredor da lateral leste, painéis a cada 25–30 m &nbsp;·&nbsp;
      <b>3</b> boca do Ring 3, divisão em três filas &nbsp;·&nbsp;
      <b>4</b> cabeças de fila &nbsp;·&nbsp;
      <b>5</b> portas A · B · C &nbsp;·&nbsp;
      <b>6</b> checkpoint interno &nbsp;·&nbsp;
      <b>7</b> saída pela fachada leste
    </p>
  </div>
  <figcaption>A consulta acontece toda no trecho 1 → 3, onde as pessoas já estão paradas ou andando. Da boca do Ring 3 em diante o eleitor só confirma uma letra que já sabe. A saída pela fachada leste fecha um circuito de sentido único: quem sai nunca atravessa quem entra. Traçado esquemático, na escala do Hall 2 (ficha técnica RDS); a posição exata do Ring 3 e do portão ainda depende de conferência no local.</figcaption>
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
    ("P3", "Boca do Ring 3",
     "Na entrada da área de fila, imediatamente antes da divisão",
     "Última consulta possível · divisão em três filas",
     "Tabela mestra (última ocorrência) + três totens A · B · C com as faixas de mesas",
     "2 painéis · 3 totens de 3 m"),
    ("P4", "Cabeças de fila",
     "No início de cada serpentina, dentro do Ring 3",
     "Confirmação da letra · captura de quem errou, sem refluxo na fila",
     "Letra em corpo grande + faixa de mesas + “errou? faixa lateral →”",
     "3 totens · 1 faixa de correção"),
    ("P5", "Portas A · B · C",
     "Sobre cada vão da fachada sul do Hall 2",
     "Só confirmação. Nenhuma informação nova",
     "Letra de 300 mm + lista das mesas atendidas",
     "3 bandeirolas de fachada"),
    ("P6", "Checkpoint interno",
     "Logo depois das portas, dentro do salão",
     "Mesa → posição física no salão",
     "Faixas suspensas por bloco de mesas + numeração em totem sobre cada mesa",
     "3 faixas suspensas · 28 totens de mesa"),
    ("P7", "Saída",
     "Portas da fachada leste (vãos 2.16 a 2.23), com desemboque no estacionamento",
     "Fecha o circuito de sentido único",
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
    ("Material", "PVC 5 mm", "Alveolar em base d'água, ou lona com ilhoses. Chove em Dublin cerca de 20 dos 31 dias de outubro."),
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
