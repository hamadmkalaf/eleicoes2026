#!/usr/bin/env python3
"""Sinalizacao do 1o turno (04/10/2026) - versao 2, sem numero de mesa.

Entrada:
  data/prancheta_paredes_abc.json   prancheta "Paredes_ABC" de 15/09/2026
                                    (28 mesas com x, y, rot, lado, secoes,
                                    esperado; portas; zonas livres)
  saidas/dados.json                 51 secoes / 28 urnas do TSE
Saida:
  saidas/sinalizacao_v2.json        blocos, listas por porta, tabela mestra,
                                    pecas e orcamento
  saidas/rota_do_eleitor_v2.html    plano externo (Merrion Road -> Ring 3 -> porta)
  saidas/sinalizacao_hall2_v2.html  plano interno (porta -> mesa)

Regras fixadas pelo Posto (15/09/2026):
  - porta A -> parede oeste, porta B -> parede norte, porta C -> parede leste;
  - as mesas nao sao numeradas: o eleitor precisa saber apenas a SECAO;
  - nao ha regra por condado nem por faixa numerica: toda peca de triagem
    carrega a lista completa (51 secoes -> porta);
  - o ponto "descubra sua secao" fica FORA do RDS, na calcada da Merrion Road;
  - banners externos so em grade, gradil, CCB ou parede (vento; sem base);
  - banners internos podem ser autoportantes.

O script falha em vez de gravar se as 51 secoes nao aparecerem exatamente
uma vez, se os aptos nao somarem 16.794 ou se as 28 mesas nao fecharem.
"""
from __future__ import annotations

import json
import html
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data" / "prancheta_paredes_abc.json"
DADOS = BASE / "saidas" / "dados.json"
SAIDAS = BASE / "saidas"

VAO_DO_PAR = 3.9        # m entre as duas mesas de um par (corredor de 3,0 m)
TOL = 0.05

# Identidade visual comum as duas paginas, igual a da prancheta e do Ring 3.
CORES = {"A": "#1f5fa8", "B": "#b8760a", "C": "#8b3a8e"}
CORES_ESCURO = {"A": "#79b0ea", "B": "#e8b354", "C": "#cb8ace"}
NOME_COR = {"A": "azul", "B": "âmbar", "C": "magenta"}
PAREDE = {"A": "oeste", "B": "norte", "C": "leste"}
PORTA_DA_PAREDE = {v: k for k, v in PAREDE.items()}

# Ring 3 - montagem adotada (artefato "Montagem do Ring 3", 15/09/2026).
# Coordenadas no sistema da prancheta: x para leste a partir do canto sudoeste
# do Hall 2, y para norte; a fachada sul esta em y = 0 e o apron vai ate -14.
RING = {
    "x0": 6.285, "x1": 50.285, "y_norte": -14.0, "y_sul": -49.0,
    "apron": 14.0, "corredor": 3.0, "fundo": 3.0, "vao_zonas": 1.2,
    "zonas": {  # x0, x1, largura
        "A": (6.285, 18.515), "B": (19.715, 33.855), "C": (35.055, 47.285),
    },
    "raias": 23, "passo_raia": 1.40,
    # boca de cada zona: extremo leste da borda sul, abertura = resto do modulo
    "bocas": {"A": (16.285, 18.515), "B": (31.715, 33.855), "C": (45.055, 47.285)},
    "entrada": "canto nordeste",
}

# Parede leste externa do Hall 2 (rota do eleitor), medida do canto norte.
PAREDE_LESTE = {
    "comprimento": 44.0,
    "saidas_emergencia": [4.7, 16.8, 28.2, 39.6],   # centros, m do canto norte
    "paineis": [10.75, 22.50, 33.90],               # centros dos paineis P2
}

# ---------------------------------------------------------------------------
# Modelos de peca e precos.  PREMISSA: o anexo de precos do Posto nao chegou a
# esta sessao; os valores abaixo sao precos de tabela publicados por graficas
# irlandesas em 16/09/2026 (inc. IVA), arredondados, e ficam editaveis na
# pagina.  Trocar aqui (ou na pagina) recalcula tudo.
# ---------------------------------------------------------------------------
MODELOS = {
    "mesh": {
        "nome": "Banner em mesh 2,0 × 1,0 m",
        "desc": "Poliéster perfurado (70/30), bainha e ilhós a cada 50 cm. Deixa o vento passar; é a única peça admissível em grade, gradil e CCB.",
        "preco": 60.0,
        "fonte": "mesh 'from €20 + VAT' (Kaizen Print, Printroom); PVC 2×4 ft €25–45 (PrintNPack). Valor de 2×1 m é extrapolação.",
    },
    "pvc": {
        "nome": "Banner PVC 440 g 1,8 × 1,2 m",
        "desc": "Lona fechada com ilhós, só onde a parede abriga do vento (lateral leste do Hall 2).",
        "preco": 55.0,
        "fonte": "banners maiores €60–150 (PrintNPack); £15/m² no Reino Unido (Synegraphics).",
    },
    "pullup": {
        "nome": "Pull-up 850 × 2000 mm",
        "desc": "Cassete com base própria; interno. Letra da porta em 300 mm e as seções da parede em 60 mm.",
        "preco": 85.0,
        "fonte": "€80 (PrintNPack) a €90 (Bannerz.ie), inc. IVA.",
    },
    "xbanner": {
        "nome": "X-banner 600 × 1600 mm",
        "desc": "Tripé em X com lona tensionada; o formato autoportante mais barato. Interno, um por bloco de mesas.",
        "preco": 40.0,
        "fonte": "PREMISSA — não verificado em fonte irlandesa; ordem de grandeza de pull-up de entrada menos a cassete.",
    },
    "correx": {
        "nome": "Placa correx 4 mm A2",
        "desc": "Placa rígida leve, furada nos cantos para abraçadeira.",
        "preco": 15.0,
        "fonte": "correx 'from €5' (Printco Dublin); A1 £35 + VAT no Reino Unido.",
    },
    "vinil": {
        "nome": "Vinil recortado por porta",
        "desc": "Letra da porta em 300 mm + ENTRADA, colado por dentro do vidro da fachada sul. Sem estrutura.",
        "preco": 30.0,
        "fonte": "PREMISSA — recorte simples de 4–8 caracteres.",
    },
    "fixacao": {
        "nome": "Fixação (abraçadeiras, ímãs, fita)",
        "desc": "200 abraçadeiras de nylon 300 mm, 12 ganchos magnéticos para as portas de aço, fita dupla-face para o vinil.",
        "preco": 40.0,
        "fonte": "PREMISSA — itens de ferragem.",
    },
}
ORCAMENTO_MIN, ORCAMENTO_MAX = 1700, 1900


def carrega():
    D = json.loads(DATA.read_text(encoding="utf-8"))
    tse = json.loads(DADOS.read_text(encoding="utf-8"))
    origem = {s["secao"]: s["origem"] for s in D["secoes"]}
    aptos_secao = {s["secao"]: s["aptos"] for s in D["secoes"]}
    return D, tse, origem, aptos_secao


def eixo(m):
    return m["x"] if m["parede"] == "norte" else m["y"]


def agrupa(mesas, parede):
    """Pares: duas mesas a 3,90 m com os lados voltados uma para a outra.
    Nas paredes oeste e norte o par lê (+1, −1) no sentido crescente do eixo;
    na leste, rotacionada 180°, lê (−1, +1)."""
    mesas = sorted(mesas, key=eixo)
    primeiro, segundo = (-1, 1) if parede == "leste" else (1, -1)
    grupos, i = [], 0
    while i < len(mesas):
        a = mesas[i]
        b = mesas[i + 1] if i + 1 < len(mesas) else None
        par = (b is not None and abs(eixo(b) - eixo(a) - VAO_DO_PAR) < TOL
               and a["lado"] == primeiro and b["lado"] == segundo)
        grupos.append([a, b] if par else [a])
        i += 2 if par else 1
    return grupos


def secoes_da_mesa(m):
    s = [m["principal"]]
    if m["agregada"]:
        s.append(m["agregada"])
    return sorted(s)


def monta():
    D, tse, origem, aptos_secao = carrega()
    por_parede = {}
    for m in D["mesas"]:
        por_parede.setdefault(m["parede"], []).append(m)

    portas = []
    todas = []
    for letra in "ABC":
        parede = PAREDE[letra]
        grupos = agrupa(por_parede[parede], parede)
        blocos = []
        for k, g in enumerate(grupos, start=1):
            secoes = sorted(s for m in g for s in secoes_da_mesa(m))
            # posicao do banner de bloco: boca do corredor do par, a 4,6 m da parede
            if parede == "oeste":
                pos = (4.6, sum(eixo(m) for m in g) / len(g))
            elif parede == "leste":
                pos = (D["salao"]["largura"] - 4.6, sum(eixo(m) for m in g) / len(g))
            else:
                pos = (sum(eixo(m) for m in g) / len(g), D["salao"]["altura"] - 4.6)
            blocos.append({
                "id": f"B{letra}{k}",
                "tipo": "par" if len(g) == 2 else "isolada",
                "mrvs": [m["mrv"] for m in g],
                "coord": [round(eixo(m), 2) for m in g],
                "secoes": secoes,
                "por_mesa": [secoes_da_mesa(m) for m in g],
                "aptos": sum(m["aptos"] for m in g),
                "esperado": sum(m["esperado"] for m in g),
                "classe": "alta" if any(m["classe"] == "alta" for m in g) else
                          ("media" if any(m["classe"] == "media" for m in g) else "baixa"),
                "pos_banner": [round(pos[0], 2), round(pos[1], 2)],
            })
        secoes_porta = sorted(s for b in blocos for s in b["secoes"])
        todas += secoes_porta
        ent = next(e for e in D["entradas"] if e["id"] == letra)
        portas.append({
            "letra": letra, "parede": parede, "porta": ent["porta"], "cor": CORES[letra],
            "nome_cor": NOME_COR[letra],
            "mesas": len(por_parede[parede]), "blocos": blocos,
            "pares": sum(1 for b in blocos if b["tipo"] == "par"),
            "isoladas": sum(1 for b in blocos if b["tipo"] == "isolada"),
            "secoes": secoes_porta,
            "secoes_em_ordem_fisica": [b["secoes"] for b in blocos],
            "aptos": sum(b["aptos"] for b in blocos),
            "esperado": ent["esperado"],
            "metros": ent["metros"],
        })

    # validacoes
    assert sorted(todas) == sorted(s["secao"] for s in D["secoes"]), "secoes nao fecham"
    assert len(todas) == 51 and len(set(todas)) == 51, "51 secoes exatamente uma vez"
    assert sum(p["aptos"] for p in portas) == 16794, "aptos nao somam 16.794"
    assert sum(p["mesas"] for p in portas) == 28, "28 mesas"
    assert len(tse["urnas"]) == 28

    porta_da_secao = {}
    for p in portas:
        for s in p["secoes"]:
            porta_da_secao[s] = p["letra"]
    mestra = [{"secao": s, "porta": porta_da_secao[s], "parede": PAREDE[porta_da_secao[s]],
               "origem": origem[s], "aptos": aptos_secao[s]}
              for s in sorted(porta_da_secao)]

    # condados: a porta nao e funcao do condado (Cork e Limerick caem em 2 portas)
    condados = {}
    for r in mestra:
        if r["origem"] != "Dublin":
            condados.setdefault(r["origem"], set()).add(r["porta"])
    condados_ambiguos = sorted(k for k, v in condados.items() if len(v) > 1)

    pecas = lista_de_pecas(portas)
    orcamento = calcula_orcamento(pecas)
    return {
        "gerado_por": "scripts/sinalizacao_v2.py",
        "prancheta": D["cenario"],
        "salao": D["salao"], "portas_salao": D["portas"], "sinalizacao_portas": D["sinalizacao"],
        "zonas_livres": D["zonas"], "serpenteados": D["serpenteados"],
        "ring": RING, "parede_leste": PAREDE_LESTE,
        "cores": CORES, "cores_escuro": CORES_ESCURO,
        "portas": portas, "mestra": mestra, "condados_ambiguos": condados_ambiguos,
        "comparecimento": D["comparecimento"],
        "modelos": MODELOS, "pecas": pecas, "orcamento": orcamento,
        "faixa_orcamento": [ORCAMENTO_MIN, ORCAMENTO_MAX],
    }


def lista_de_pecas(portas):
    """Cada peca: ponto, onde, o que diz, modelo, quantidade, fixacao."""
    P = []

    def add(ponto, nome, onde, diz, modelo, qtd, fixacao, externo, corpo):
        P.append(dict(ponto=ponto, nome=nome, onde=onde, diz=diz, modelo=modelo,
                      qtd=qtd, fixacao=fixacao, externo=externo, corpo=corpo))

    add("P0", "Ponto “descubra sua seção”",
        "Calçada da Merrion Road, no gradil do RDS, 20–30 m antes do portão, fora do fluxo: mesa, 2–3 operadores com o caderno impresso e o e-Título",
        "NÃO SABE SUA SEÇÃO? · Don’t know your section? · Consulte aqui ANTES de entrar · QR do e-Título",
        "mesh", 1, "amarrado no gradil de ferro fundido, ilhós a ilhós", True, "letra 150 mm · lido a 30 m")
    add("P0", "Tabela mestra na calçada", "Gradil da Merrion Road, ao lado do ponto de consulta e no trecho onde a fila da calçada se forma",
        "SEÇÃO → PORTA · 51 linhas em 3 colunas, cor e letra da porta", "mesh", 2,
        "amarrado no gradil", True, "dígitos 30 mm · lido a 6 m")
    add("P1", "Portão de entrada do RDS", "Nas grades do portão de eleitores (Merrion Road), uma folha de cada lado do vão",
        "ELEIÇÕES BRASIL 2026 · ENTRADA DE ELEITORES → Hall 2 (Shelbourne Hall) · Preferencial: idoso, gestante, PcD →",
        "mesh", 1, "amarrado nas grades do portão", True, "letra 150 mm")
    add("P1", "Tabela mestra no portão", "Na outra folha da grade do portão",
        "SEÇÃO → PORTA · 51 linhas", "mesh", 1, "amarrado nas grades do portão", True, "dígitos 30 mm")
    add("P2", "Tabela mestra na parede leste do Hall 2",
        "Nos três vãos entre as quatro saídas de emergência da lateral leste, a 10,75 · 22,50 · 33,90 m do canto norte; borda inferior a 1,0 m",
        "SEÇÃO → PORTA · 51 linhas + seta “Ring 3 ↓”", "pvc", 3,
        "pendurado nas folhas das portas de serviço (aço pintado) com ganchos magnéticos; 4 cantos presos — parede abriga do vento",
        True, "dígitos 40 mm · lido a 8 m")
    add("P3", "Entrada do Ring 3", "Na CCB do corredor de chegada, logo depois do canto nordeste, virada para quem entra",
        "SEÇÃO → PORTA · 51 linhas · “siga o corredor: C, depois B, depois A”", "mesh", 1,
        "amarrado na CCB (painel de 2,0 m)", True, "dígitos 30 mm")
    for p in portas:
        add("P4", f"Boca da zona {p['letra']}",
            f"Na CCB de fechamento imediatamente antes da boca da zona {p['letra']}, virada para o trecho de fundo (quem caminha para oeste lê antes de chegar)",
            f"ZONA {p['letra']} · PORTA {p['letra']} · {len(p['secoes'])} seções em 80 mm · “não está aqui? siga em frente / volte”",
            "mesh", 1, "amarrado na CCB (painel de 2,0 m × 1,1 m)", True, f"letra 400 mm · seções 80 mm · lido a 15 m")
    add("P5", "Letra da porta no vidro", "Por dentro da cortina de vidro da fachada sul, sobre cada vão de entrada S4 · S5 · S6",
        "ENTRADA + letra e cor da porta em 300 mm", "vinil", 3, "colado no vidro; sai sem resíduo", True, "300 mm · lido a 60 m, do Ring 3")
    add("P5", "Entrada preferencial", "Gradil branco de pedestres do apron, junto à porta S7",
        "ENTRADA PREFERENCIAL · Priority entrance · idoso, gestante, PcD, acompanhante · qualquer porta", "mesh", 1,
        "amarrado no gradil do apron", True, "letra 150 mm")
    for p in portas:
        add("P6", f"Painel da porta {p['letra']}",
            f"Logo depois da porta {p['porta']}, dentro do salão, do lado oposto à curva do eleitor",
            f"PORTA {p['letra']} · parede {p['parede']} · as {len(p['secoes'])} seções da parede, agrupadas por bloco, na ordem física",
            "pullup", 1, "autoportante (cassete)", False, "letra 300 mm · seções 60 mm")
    for p in portas:
        add("P6", f"Banners de bloco — porta {p['letra']}",
            f"Na boca do corredor de cada bloco da parede {p['parede']}, a 4,6 m da parede",
            "Só as seções do bloco (2 a 4 números), 4 dígitos, sem número de mesa",
            "xbanner", len(p["blocos"]), "autoportante (tripé em X)", False, "seções 120 mm · lido a 20 m")
    add("P7", "Saídas S2 e S8", "Dentro do salão, sobre cada vão de saída",
        "SAÍDA · WAY OUT → Merrion Road", "correx", 2, "abraçadeira no batente / fita", False, "letra 150 mm")
    add("—", "Fixação", "Todas as peças", "—", "fixacao", 1, "—", True, "—")
    return P


def calcula_orcamento(pecas):
    linhas = []
    for p in pecas:
        m = MODELOS[p["modelo"]]
        linhas.append({"peca": p["nome"], "ponto": p["ponto"], "modelo": p["modelo"],
                       "qtd": p["qtd"], "unit": m["preco"], "total": round(p["qtd"] * m["preco"], 2)})
    por_modelo = {}
    for l in linhas:
        e = por_modelo.setdefault(l["modelo"], {"qtd": 0, "total": 0.0})
        e["qtd"] += l["qtd"]
        e["total"] = round(e["total"] + l["total"], 2)
    total = round(sum(l["total"] for l in linhas), 2)
    return {"linhas": linhas, "por_modelo": por_modelo, "total": total}


# ---------------------------------------------------------------------------
# HTML helpers
# ---------------------------------------------------------------------------
def pad(s):
    return f"{int(s):04d}"


def br(n):
    return f"{n:,}".replace(",", ".")


def eur(v):
    return "€ " + f"{v:,.0f}".replace(",", ".")


def esc(t):
    return html.escape(str(t), quote=True)


def tokens_css():
    return f"""
  :root{{ --a:{CORES['A']}; --b:{CORES['B']}; --c:{CORES['C']};
    --a-soft:#e2edf8; --b-soft:#f8eed9; --c-soft:#f2e4f3; }}
  @media (prefers-color-scheme:dark){{ :root:not([data-theme="light"]){{
    --a:{CORES_ESCURO['A']}; --b:{CORES_ESCURO['B']}; --c:{CORES_ESCURO['C']};
    --a-soft:#1a2c40; --b-soft:#33290f; --c-soft:#332034; }} }}
  :root[data-theme="dark"]{{
    --a:{CORES_ESCURO['A']}; --b:{CORES_ESCURO['B']}; --c:{CORES_ESCURO['C']};
    --a-soft:#1a2c40; --b-soft:#33290f; --c-soft:#332034; }}
  .t-a{{--k:var(--a);--k-soft:var(--a-soft)}} .t-b{{--k:var(--b);--k-soft:var(--b-soft)}} .t-c{{--k:var(--c);--k-soft:var(--c-soft)}}
"""


def chip(letra):
    return f'<span class="chip t-{letra.lower()}">{letra}</span>'


def tabela_mestra_html(M, colunas=3):
    n = len(M)
    por = -(-n // colunas)
    cols = [M[i * por:(i + 1) * por] for i in range(colunas)]
    out = ['<div class="mestra">']
    for col in cols:
        out.append('<div class="mcol">')
        for r in col:
            out.append(f'<div class="mrow"><span class="sec">{pad(r["secao"])}</span>'
                       f'<span class="dots"></span>{chip(r["porta"])}</div>')
        out.append('</div>')
    out.append('</div>')
    return "".join(out)


def orcamento_html(S, id_prefix):
    """Tabela de orcamento com preco unitario editavel; recalcula no navegador."""
    mods = S["modelos"]
    linhas = []
    for l in S["orcamento"]["linhas"]:
        linhas.append(
            f'<tr data-modelo="{l["modelo"]}" data-qtd="{l["qtd"]}">'
            f'<td class="pt">{l["ponto"]}</td><td>{esc(l["peca"])}</td>'
            f'<td>{esc(mods[l["modelo"]]["nome"])}</td>'
            f'<td class="num">{l["qtd"]}</td><td class="num unit"></td><td class="num tot"></td></tr>')
    modelos = []
    for k, m in mods.items():
        modelos.append(
            f'<div class="modelo"><label for="{id_prefix}-{k}"><b>{esc(m["nome"])}</b>'
            f'<span>{esc(m["desc"])}</span><small>Fonte: {esc(m["fonte"])}</small></label>'
            f'<div class="preco"><span>€</span><input type="number" min="0" step="1" id="{id_prefix}-{k}" '
            f'data-modelo="{k}" value="{m["preco"]:.0f}" inputmode="decimal"></div></div>')
    lo, hi = S["faixa_orcamento"]
    return f"""
<div class="orc" id="{id_prefix}">
  <div class="modelos">{"".join(modelos)}</div>
  <div class="tscroll"><table class="orctab"><thead><tr><th>Ponto</th><th>Peça</th><th>Modelo</th>
    <th class="num">Qtd</th><th class="num">Unit.</th><th class="num">Total</th></tr></thead>
    <tbody>{"".join(linhas)}</tbody>
    <tfoot><tr><td colspan="5">Total, inc. IVA</td><td class="num" id="{id_prefix}-total"></td></tr>
    <tr class="faixa"><td colspan="5">Faixa do Posto</td><td class="num">{eur(lo)} – {eur(hi)}</td></tr>
    <tr class="delta"><td colspan="5" id="{id_prefix}-veredito"></td><td class="num" id="{id_prefix}-delta"></td></tr></tfoot>
  </table></div>
  <p class="orcnota">Os preços unitários são <strong>premissa</strong> (tabela pública de gráficas irlandesas em 16/09/2026, inc. IVA de 23%), não o anexo do Posto, que não chegou a esta revisão. Edite os campos acima com os preços do anexo: a tabela recalcula na hora e guarda os valores só neste navegador.</p>
  <p class="orcnota"><button type="button" class="reset" id="{id_prefix}-reset">Voltar aos preços de referência</button></p>
</div>
<script>
(function(){{
  const raiz=document.getElementById("{id_prefix}");
  const chave="orc-{id_prefix}-v2", lo={lo}, hi={hi};
  const inputs=[...raiz.querySelectorAll("input[data-modelo]")];
  const base={{}}; inputs.forEach(i=>base[i.dataset.modelo]=+i.value);
  const fmt=v=>"€ "+Math.round(v).toLocaleString("pt-BR");
  function precos(){{const p={{}};inputs.forEach(i=>p[i.dataset.modelo]=Math.max(0,+i.value||0));return p;}}
  function calc(){{
    const p=precos(); let total=0;
    raiz.querySelectorAll("tbody tr").forEach(tr=>{{
      const q=+tr.dataset.qtd, u=p[tr.dataset.modelo]||0, t=q*u; total+=t;
      tr.querySelector(".unit").textContent=fmt(u); tr.querySelector(".tot").textContent=fmt(t);
    }});
    document.getElementById("{id_prefix}-total").textContent=fmt(total);
    const v=document.getElementById("{id_prefix}-veredito"), d=document.getElementById("{id_prefix}-delta");
    if(total<lo){{v.textContent="Abaixo da faixa — sobra para reforço";d.textContent="+"+fmt(lo-total);raiz.dataset.estado="sob";}}
    else if(total>hi){{v.textContent="Acima da faixa — aplicar a ordem de cortes";d.textContent="−"+fmt(total-hi);raiz.dataset.estado="acima";}}
    else{{v.textContent="Dentro da faixa";d.textContent="";raiz.dataset.estado="ok";}}
    try{{localStorage.setItem(chave,JSON.stringify(p));}}catch(e){{}}
  }}
  try{{const s=JSON.parse(localStorage.getItem(chave)||"null");if(s)inputs.forEach(i=>{{if(s[i.dataset.modelo]!=null)i.value=s[i.dataset.modelo];}});}}catch(e){{}}
  inputs.forEach(i=>i.addEventListener("input",calc));
  document.getElementById("{id_prefix}-reset").addEventListener("click",()=>{{inputs.forEach(i=>i.value=base[i.dataset.modelo]);calc();}});
  calc();
}})();
</script>"""


CSS_ORC = """
  .orc .modelos{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:1px;
    background:var(--rule);border:1px solid var(--rule);margin:22px 0}
  .orc .modelo{background:var(--surface);padding:14px 15px;display:flex;flex-direction:column;gap:10px}
  .orc .modelo label{display:flex;flex-direction:column;gap:5px;font-family:var(--sans);font-size:13.5px;
    line-height:1.45}
  .orc .modelo label b{font-weight:600;font-size:14px}
  .orc .modelo label span{color:var(--muted)}
  .orc .modelo label small{color:var(--muted);font-size:11.5px;line-height:1.4}
  .orc .preco{display:flex;align-items:center;gap:6px;font-family:var(--mono);font-size:15px;margin-top:auto}
  .orc .preco input{width:6.5em;font:600 16px var(--mono);padding:6px 8px;border:1.5px solid var(--rule);
    border-radius:3px;background:var(--ground);color:var(--ink);text-align:right}
  .orc .preco input:focus{border-color:var(--a);outline:none}
  .orctab tfoot td{font-family:var(--sans);font-weight:600;padding:10px 14px;border-top:1px solid var(--rule);
    background:var(--surface-2)}
  .orctab tfoot .faixa td{font-weight:400;color:var(--muted);background:var(--surface)}
  .orc[data-estado="acima"] .delta td{color:var(--alert)}
  .orc[data-estado="sob"] .delta td{color:var(--muted)}
  .orcnota{font-size:14.5px;color:var(--muted);max-width:74ch}
  .reset{font:600 13px var(--sans);padding:7px 12px;border:1px solid var(--rule);background:var(--surface);
    color:var(--ink);border-radius:3px;cursor:pointer}
  .reset:hover{border-color:var(--muted)}
  .mestra{display:grid;grid-template-columns:repeat(3,1fr);gap:0 28px;margin:20px 0 0;
    font-family:var(--mono);font-size:14px}
  @media (max-width:640px){.mestra{grid-template-columns:repeat(2,1fr)}}
  @media (max-width:420px){.mestra{grid-template-columns:1fr}}
  .mrow{display:flex;align-items:center;gap:8px;padding:4.5px 0;border-bottom:1px solid var(--rule-soft)}
  .mrow .sec{font-weight:600;font-variant-numeric:tabular-nums}
  .mrow .dots{flex:1;border-bottom:1px dotted var(--rule);height:.7em}
  .chip{display:inline-block;min-width:22px;text-align:center;font-family:var(--sans);font-weight:700;
    font-size:12px;line-height:19px;border-radius:2px;padding:0 5px;background:var(--k-soft);color:var(--k);
    box-shadow:inset 0 0 0 1px var(--k)}
"""

# ---------------------------------------------------------------------------
# Figuras (SVG)
# ---------------------------------------------------------------------------
def figura_sitio(S):
    """Planta esquematica do percurso: Merrion Road -> portao -> lateral leste
    do Hall 2 -> apron -> Ring 3 (canto nordeste) -> corredor em L -> boca da
    zona -> porta.  Escala 5,4 px/m; x para leste, y do SVG para o sul."""
    E = 5.4
    sal = S["salao"]
    L, A = sal["largura"], sal["altura"]
    R = S["ring"]
    # sistema: X = 40 + x*E ; Y = 60 + (A + 22 - y)*E  (a Merrion Road fica ao norte, y = A + 22)
    def X(x): return round(40 + x * E, 1)
    def Y(y): return round(60 + (A + 22 - y) * E, 1)
    W = round(40 + (L + 16) * E + 40)
    H = round(Y(R["y_sul"]) + 60)
    o = [f'<svg class="diagram" viewBox="0 0 {W} {H}" role="img" aria-label="Percurso do eleitor: do gradil da Merrion Road, onde fica o ponto de consulta da seção, pelo portão, pela lateral leste do Hall 2, pelo apron até o canto nordeste do Ring 3; dentro do Ring, o corredor em L passa pelas bocas das zonas C, B e A, e cada zona descarrega ao norte na sua porta.">',
         '<defs><marker id="ar" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker></defs>']
    # Merrion Road
    o.append(f'<rect x="0" y="{Y(A+26)}" width="{W}" height="{4*E}" fill="var(--surface-2)"/>')
    o.append(f'<text x="14" y="{Y(A+23.6)}" font-family="Archivo,sans-serif" font-size="11" font-weight="600" letter-spacing="1.6" fill="var(--muted)">MERRION ROAD (R118) · calçada e gradil do RDS</text>')
    # gradil
    gx0, gx1 = X(-6), X(L + 14)
    o.append(f'<line x1="{gx0}" y1="{Y(A+21)}" x2="{X(L+2)}" y2="{Y(A+21)}" stroke="currentColor" stroke-width="2" opacity=".5"/>')
    o.append(f'<line x1="{X(L+6)}" y1="{Y(A+21)}" x2="{gx1}" y2="{Y(A+21)}" stroke="currentColor" stroke-width="2" opacity=".5"/>')
    # portao
    o.append(f'<line x1="{X(L+2)}" y1="{Y(A+22.5)}" x2="{X(L+2)}" y2="{Y(A+19.5)}" stroke="currentColor" stroke-width="2.5"/>')
    o.append(f'<line x1="{X(L+6)}" y1="{Y(A+22.5)}" x2="{X(L+6)}" y2="{Y(A+19.5)}" stroke="currentColor" stroke-width="2.5"/>')
    o.append(f'<text x="{X(L+7)}" y="{Y(A+18.2)}" font-family="Archivo,sans-serif" font-size="10.5" font-weight="600" fill="currentColor">portão de eleitores · P1</text>')
    # ponto de consulta, fora do RDS, na calcada a oeste do portao
    o.append(f'<rect x="{X(L-14)}" y="{Y(A+25.4)}" width="{8*E}" height="{3*E}" rx="2" fill="var(--alert-soft)" stroke="var(--alert)" stroke-width="1.4"/>')
    o.append(f'<text x="{X(L-10)}" y="{Y(A+23.5)}" text-anchor="middle" font-family="Archivo,sans-serif" font-size="10" font-weight="700" fill="var(--alert)">P0 · descubra sua seção</text>')
    o.append(f'<text x="{X(L-10)}" y="{Y(A+21.7)}" text-anchor="middle" font-family="Archivo,sans-serif" font-size="9.5" fill="var(--muted)">na calçada, antes do portão</text>')
    # Hall 1 (esquematico) e Hall 2
    o.append(f'<rect x="{X(-14)}" y="{Y(A)}" width="{12*E}" height="{A*E}" fill="var(--surface-2)" stroke="var(--rule)"/>')
    o.append(f'<text x="{X(-8)}" y="{Y(A/2)}" text-anchor="middle" font-family="Archivo,sans-serif" font-size="11" font-weight="600" fill="var(--muted)">HALL 1</text>')
    o.append(f'<rect x="{X(0)}" y="{Y(A)}" width="{L*E}" height="{A*E}" fill="var(--surface)" stroke="currentColor" stroke-width="1.5"/>')
    o.append(f'<text x="{X(L/2)}" y="{Y(A/2+2)}" text-anchor="middle" font-family="Archivo,sans-serif" font-size="15" font-weight="700" fill="currentColor">HALL 2</text>')
    o.append(f'<text x="{X(L/2)}" y="{Y(A/2-1.5)}" text-anchor="middle" font-family="Archivo,sans-serif" font-size="10.5" fill="var(--muted)">Shelbourne Hall · {str(L).replace(".",",")} × {str(A).replace(".",",")} m</text>')
    # paredes internas com portas A/B/C
    for p in S["portas"]:
        k = p["letra"].lower()
        if p["parede"] == "oeste":
            o.append(f'<rect x="{X(0)}" y="{Y(A-3)}" width="{2.2*E}" height="{(A-6)*E}" fill="var(--{k})" opacity=".55"/>')
        elif p["parede"] == "leste":
            o.append(f'<rect x="{X(L-2.2)}" y="{Y(A-3)}" width="{2.2*E}" height="{(A-6)*E}" fill="var(--{k})" opacity=".55"/>')
        else:
            o.append(f'<rect x="{X(8)}" y="{Y(A)}" width="{(L-11)*E}" height="{2.2*E}" fill="var(--{k})" opacity=".55"/>')
    # saidas de emergencia da lateral leste + paineis P2
    for c in S["parede_leste"]["saidas_emergencia"]:
        o.append(f'<rect x="{X(L)-2}" y="{Y(A-c-1.5)}" width="5" height="{3*E}" fill="var(--alert)" opacity=".8"/>')
    for c in S["parede_leste"]["paineis"]:
        o.append(f'<rect x="{X(L)+1}" y="{Y(A-c-0.9)}" width="4" height="{1.8*E}" fill="var(--a)"/>')
    o.append(f'<text x="{X(L+2.5)}" y="{Y(A-22.5)}" font-family="Archivo,sans-serif" font-size="10.5" font-weight="600" fill="currentColor" transform="rotate(90 {X(L+2.5)} {Y(A-22.5)})">P2 · 3 tabelas mestras entre as 4 saídas de emergência</text>')
    # portas da fachada sul
    for pid, cor in (("S4", "--a"), ("S5", "--b"), ("S6", "--c")):
        d = next(q for q in S["portas_salao"] if q["id"] == pid)
        o.append(f'<line x1="{X(d["x1"])}" y1="{Y(0)}" x2="{X(d["x2"])}" y2="{Y(0)}" stroke="var({cor})" stroke-width="6"/>')
        letra = {"S4": "A", "S5": "B", "S6": "C"}[pid]
        o.append(f'<text x="{X((d["x1"]+d["x2"])/2)}" y="{Y(-2.6)}" text-anchor="middle" font-family="Archivo,sans-serif" font-size="11" font-weight="700" fill="var({cor})">{pid} · {letra}</text>')
    for pid, rot in (("S2", "saída"), ("S8", "saída"), ("S7", "prefer.")):
        d = next(q for q in S["portas_salao"] if q["id"] == pid)
        o.append(f'<line x1="{X(d["x1"])}" y1="{Y(0)}" x2="{X(d["x2"])}" y2="{Y(0)}" stroke="var(--muted)" stroke-width="5"/>')
        o.append(f'<text x="{X((d["x1"]+d["x2"])/2)}" y="{Y(-2.6)}" text-anchor="middle" font-family="Archivo,sans-serif" font-size="9" fill="var(--muted)">{pid} {rot}</text>')
    # apron
    o.append(f'<rect x="{X(R["x0"]-4)}" y="{Y(0)}" width="{(R["x1"]-R["x0"]+8)*E}" height="{R["apron"]*E}" fill="var(--surface-2)" opacity=".7"/>')
    o.append(f'<text x="{X(R["x0"]-2)}" y="{Y(-8)}" font-family="Archivo,sans-serif" font-size="10" fill="var(--muted)">apron pavimentado · 14 m</text>')
    # Ring 3
    o.append(f'<rect x="{X(R["x0"])}" y="{Y(R["y_norte"])}" width="{(R["x1"]-R["x0"])*E}" height="{(R["y_norte"]-R["y_sul"])*E}" fill="var(--surface)" stroke="var(--muted)" stroke-width="1.5" stroke-dasharray="6 4"/>')
    o.append(f'<text x="{X(R["x0"]+1)}" y="{Y(R["y_norte"]-1.6)}" font-family="Archivo,sans-serif" font-size="11" font-weight="600" fill="var(--muted)">RING 3 · 44 × 35 m</text>')
    # corredor em L
    yz_sul = R["y_sul"] + R["fundo"]
    o.append(f'<rect x="{X(R["x1"]-R["corredor"])}" y="{Y(R["y_norte"])}" width="{R["corredor"]*E}" height="{(R["y_norte"]-R["y_sul"])*E}" fill="var(--a-soft)" opacity=".8"/>')
    o.append(f'<rect x="{X(R["x0"])}" y="{Y(yz_sul)}" width="{(R["x1"]-R["x0"])*E}" height="{R["fundo"]*E}" fill="var(--a-soft)" opacity=".8"/>')
    # zonas
    for letra, (zx0, zx1) in R["zonas"].items():
        k = letra.lower()
        o.append(f'<rect x="{X(zx0)}" y="{Y(R["y_norte"])}" width="{(zx1-zx0)*E}" height="{(R["y_norte"]-yz_sul)*E}" fill="var(--{k}-soft)" stroke="var(--{k})" stroke-width="1"/>')
        # raias esquematicas (uma a cada 4)
        for i in range(1, R["raias"], 4):
            yy = R["y_norte"] - i * R["passo_raia"]
            o.append(f'<line x1="{X(zx0+0.6)}" y1="{Y(yy)}" x2="{X(zx1-0.6)}" y2="{Y(yy)}" stroke="var(--{k})" stroke-width=".6" opacity=".5"/>')
        o.append(f'<text x="{X((zx0+zx1)/2)}" y="{Y(R["y_norte"]-16)}" text-anchor="middle" font-family="Archivo,sans-serif" font-size="20" font-weight="700" fill="var(--{k})">{letra}</text>')
        o.append(f'<text x="{X((zx0+zx1)/2)}" y="{Y(R["y_norte"]-19)}" text-anchor="middle" font-family="Archivo,sans-serif" font-size="9.5" fill="var(--{k})">raias L–O · 23</text>')
        # boca
        bx0, bx1 = R["bocas"][letra]
        o.append(f'<rect x="{X(bx0)}" y="{Y(yz_sul)-3}" width="{(bx1-bx0)*E}" height="6" fill="var(--surface)" stroke="var(--{k})" stroke-width="1.2"/>')
        # banner P4 na CCB antes da boca
        o.append(f'<rect x="{X(bx0-2.2)}" y="{Y(yz_sul)-2}" width="{2.0*E}" height="4" fill="var(--{k})"/>')
        o.append(f'<text x="{X(bx0-1.2)}" y="{Y(yz_sul-2.2)}" text-anchor="middle" font-family="Archivo,sans-serif" font-size="9.5" font-weight="700" fill="var(--{k})">P4</text>')
        # descarga ao norte -> porta
        porta = {"A": "S4", "B": "S5", "C": "S6"}[letra]
        d = next(q for q in S["portas_salao"] if q["id"] == porta)
        px = (d["x1"] + d["x2"]) / 2
        o.append(f'<line x1="{X((zx0+zx1)/2)}" y1="{Y(R["y_norte"]+0.5)}" x2="{X(px)}" y2="{Y(-0.8)}" stroke="var(--{k})" stroke-width="2" marker-end="url(#ar)"/>')
    # P3 na entrada do ring
    o.append(f'<rect x="{X(R["x1"]-R["corredor"])-3}" y="{Y(R["y_norte"]-2)}" width="4" height="{2*E}" fill="var(--a)"/>')
    o.append(f'<text x="{X(R["x1"]+0.8)}" y="{Y(R["y_norte"]-3)}" font-family="Archivo,sans-serif" font-size="9.5" font-weight="700" fill="currentColor">P3</text>')
    # rota do eleitor
    xr = L + 4
    pts = [(L+4, A+21), (xr, A+19), (xr, 0), (R["x1"]-1.5, -2), (R["x1"]-1.5, R["y_norte"]), (R["x1"]-1.5, yz_sul-1.5), (R["x0"]+3, yz_sul-1.5)]
    o.append('<polyline points="' + " ".join(f"{X(x)},{Y(y)}" for x, y in pts) + '" fill="none" stroke="currentColor" stroke-width="3.2" marker-end="url(#ar)"/>')
    o.append(f'<text x="{X(L+5.6)}" y="{Y(A/2)}" font-family="Archivo,sans-serif" font-size="11" font-weight="600" fill="currentColor" transform="rotate(90 {X(L+5.6)} {Y(A/2)})">≈ 44 m de fila e leitura ao longo da lateral leste</text>')
    o.append(f'<text x="{X(R["x0"]+3)}" y="{Y(R["y_sul"]-2.4)}" font-family="Archivo,sans-serif" font-size="10.5" font-weight="600" fill="currentColor">trecho de fundo · lê C, depois B, depois A</text>')
    o.append(f'<text x="{X(R["x1"]+0.8)}" y="{Y(R["y_norte"]-18)}" font-family="Archivo,sans-serif" font-size="10" fill="var(--muted)" transform="rotate(90 {X(R["x1"]+0.8)} {Y(R["y_norte"]-18)})">corredor de chegada · 3,0 m</text>')
    # saidas pelos flancos
    for pid, dx in (("S2", -8), ("S8", 8)):
        d = next(q for q in S["portas_salao"] if q["id"] == pid)
        px = (d["x1"] + d["x2"]) / 2
        o.append(f'<polyline points="{X(px)},{Y(-1)} {X(px)},{Y(-6)} {X(px+dx)},{Y(-6)}" fill="none" stroke="currentColor" stroke-width="1.6" stroke-dasharray="6 4" opacity=".7" marker-end="url(#ar)"/>')
    # escala e norte
    o.append(f'<line x1="{X(-14)}" y1="{H-30}" x2="{X(6)}" y2="{H-30}" stroke="currentColor" stroke-width="1.5"/><text x="{X(-4)}" y="{H-36}" text-anchor="middle" font-family="ui-monospace,monospace" font-size="10" fill="var(--muted)">20 m</text>')
    o.append(f'<line x1="{W-30}" y1="{Y(A+16)}" x2="{W-30}" y2="{Y(A+21)}" stroke="currentColor" stroke-width="1.5" marker-end="url(#ar)"/><text x="{W-30}" y="{Y(A+22.5)}" text-anchor="middle" font-family="Archivo,sans-serif" font-size="10" font-weight="700" fill="var(--muted)">N</text>')
    o.append('</svg>')
    return "".join(o)


def figura_parede_leste(S):
    PL = S["parede_leste"]
    Lm = PL["comprimento"]
    E = 820 / Lm
    o = ['<svg class="diagram" viewBox="0 0 920 200" role="img" style="min-width:640px" aria-label="Elevação da lateral leste do Hall 2: 44 m com quatro saídas de emergência e três tabelas mestras de 1,8 por 1,2 m penduradas nos vãos entre elas.">']
    o.append('<rect x="50" y="40" width="820" height="110" fill="var(--surface-2)" stroke="var(--rule)"/>')
    for i in range(1, 12):
        o.append(f'<line x1="50" y1="{40+i*8}" x2="870" y2="{40+i*8}" stroke="currentColor" stroke-width=".7" opacity=".14"/>')
    for i, c in enumerate(PL["saidas_emergencia"], 1):
        x = 50 + c * E
        o.append(f'<rect x="{x-1.5*E:.1f}" y="95" width="{3*E:.1f}" height="55" fill="var(--alert)" fill-opacity=".5" stroke="var(--alert)"/>')
        o.append(f'<text x="{x:.1f}" y="170" text-anchor="middle" font-family="Archivo,sans-serif" font-size="10.5" font-weight="600" fill="var(--alert)">saída {i}</text>')
    for i, c in enumerate(PL["paineis"], 1):
        x = 50 + c * E
        o.append(f'<rect x="{x-0.9*E:.1f}" y="{150-2.2*E*1.0:.1f}" width="{1.8*E:.1f}" height="{1.2*E:.1f}" fill="var(--a-soft)" stroke="var(--a)" stroke-width="1.8"/>')
        o.append(f'<text x="{x:.1f}" y="{150-2.4*E:.1f}" text-anchor="middle" font-family="Archivo,sans-serif" font-size="11" font-weight="700" fill="var(--a)">P2·{i}</text>')
        o.append(f'<text x="{x:.1f}" y="188" text-anchor="middle" font-family="ui-monospace,monospace" font-size="9.5" fill="var(--muted)">{str(c).replace(".",",")} m</text>')
    o.append('<text x="50" y="28" font-family="Archivo,sans-serif" font-size="10.5" font-weight="600" fill="var(--muted)">canto norte (portão)</text>')
    o.append('<text x="870" y="28" text-anchor="end" font-family="Archivo,sans-serif" font-size="10.5" font-weight="600" fill="var(--muted)">canto sul (apron · Ring 3)</text>')
    o.append('</svg>')
    return "".join(o)


def figura_planta_hall(S, D_mesas, com_pecas=True):
    """Planta do Hall 2 em metros: x para leste, y do SVG = altura - y."""
    sal = S["salao"]
    L, A = sal["largura"], sal["altura"]
    def Y(y): return round(A - y, 2)
    o = [f'<svg class="planta" viewBox="-11 -12 {L+22} {A+22}" role="img" aria-label="Planta do Hall 2 com as 28 mesas agrupadas em 16 blocos, coloridas pela porta que as atende, e a posição dos painéis de porta e dos banners de bloco.">']
    o.append(f'<path class="salao" d="M {sal["recorte"][2]} {Y(0)} L {L} {Y(0)} L {L} {Y(A)} L 0 {Y(A)} L 0 {Y(sal["recorte"][3])} L {sal["recorte"][2]} {Y(sal["recorte"][3])} Z"/>')
    o.append(f'<g class="rosa"><text x="{L/2}" y="-8.4" text-anchor="middle">N</text></g>')
    # zonas livres
    for z in S["zonas_livres"]:
        x0, y0, x1, y1 = z["rect"]
        cls = "zona-emerg" if z["tipo"] == "faixa_emergencia" else ("zona-apoio" if z["tipo"] == "sala_apoio" else "zona-recuo")
        o.append(f'<rect class="{cls}" x="{x0}" y="{Y(y1)}" width="{x1-x0:.2f}" height="{y1-y0:.2f}"/>')
    # serpenteados reservados
    for sp in S["serpenteados"]:
        x0, y0, x1, y1 = sp["rect"]
        o.append(f'<rect class="serp" x="{x0}" y="{Y(y1)}" width="{x1-x0:.2f}" height="{y1-y0:.2f}"/>')
    # blocos e mesas
    prof, larg = 4.1, 0.9
    for p in S["portas"]:
        k = p["letra"].lower()
        for b in p["blocos"]:
            c0, c1 = b["coord"][0], b["coord"][-1]
            if p["parede"] == "oeste":
                o.append(f'<rect class="bloco t-{k}" x="-0.4" y="{Y(c1+1.2):.2f}" width="{prof+0.9:.2f}" height="{c1-c0+2.4:.2f}" rx=".5"/>')
                for c in b["coord"]:
                    o.append(f'<rect class="mesa t-{k}" x="0" y="{Y(c+larg/2):.2f}" width="{prof}" height="{larg}"/>')
                tx, ty, anc = prof + 1.3, Y((c0 + c1) / 2), "start"
            elif p["parede"] == "leste":
                o.append(f'<rect class="bloco t-{k}" x="{L-prof-0.5:.2f}" y="{Y(c1+1.2):.2f}" width="{prof+0.9:.2f}" height="{c1-c0+2.4:.2f}" rx=".5"/>')
                for c in b["coord"]:
                    o.append(f'<rect class="mesa t-{k}" x="{L-prof:.2f}" y="{Y(c+larg/2):.2f}" width="{prof}" height="{larg}"/>')
                tx, ty, anc = L - prof - 1.3, Y((c0 + c1) / 2), "end"
            else:
                o.append(f'<rect class="bloco t-{k}" x="{c0-1.2:.2f}" y="-0.4" width="{c1-c0+2.4:.2f}" height="{prof+0.9:.2f}" rx=".5"/>')
                for c in b["coord"]:
                    o.append(f'<rect class="mesa t-{k}" x="{c-larg/2:.2f}" y="0" width="{larg}" height="{prof}"/>')
                tx, ty, anc = (c0 + c1) / 2, -1.6 - 1.5 * (len(b["secoes"]) - 1) / 2, "middle"
            # rotulo com as secoes do bloco
            if p["parede"] == "norte":
                linhas = [pad(s) for s in b["secoes"]]
                o.append(f'<text class="rot t-{k}" x="{tx:.2f}" y="{ty:.2f}" text-anchor="middle">' +
                         "".join(f'<tspan x="{tx:.2f}" dy="{0 if i == 0 else 1.5}">{t}</tspan>' for i, t in enumerate(linhas)) + '</text>')
            else:
                pares = [" ".join(pad(s) for s in b["secoes"][i:i+2]) for i in range(0, len(b["secoes"]), 2)]
                y0 = ty - 0.75 * (len(pares) - 1) + 0.45
                o.append(f'<text class="rot t-{k}" x="{tx:.2f}" y="{y0:.2f}" text-anchor="{anc}">' +
                         "".join(f'<tspan x="{tx:.2f}" dy="{0 if i == 0 else 1.5}">{t}</tspan>' for i, t in enumerate(pares)) + '</text>')
            if com_pecas:
                bx, by = b["pos_banner"]
                o.append(f'<rect class="peca t-{k}" x="{bx-0.8:.2f}" y="{Y(by)-0.3:.2f}" width="1.6" height=".6"/>')
    # portas
    for d in S["portas_salao"]:
        sin = S["sinalizacao_portas"][d["id"]]
        if d["face"] != "sul" or sin["papel"] == "livre":
            continue
        ent = sin.get("entrada")
        cls = f"porta t-{ent.lower()}" if ent else ("porta-saida" if sin["papel"] == "saida" else "porta-pref")
        o.append(f'<rect class="{cls}" x="{d["x1"]}" y="{Y(0)-0.45:.2f}" width="{d["x2"]-d["x1"]:.2f}" height=".9"/>')
        cx = (d["x1"] + d["x2"]) / 2
        if ent:
            o.append(f'<text class="letra t-{ent.lower()}" x="{cx:.2f}" y="{Y(0)+4.4:.2f}" text-anchor="middle">{ent}</text>')
        else:
            o.append(f'<text class="mini" x="{cx:.2f}" y="{Y(0)+2.4:.2f}" text-anchor="middle">{d["id"]} {"saída" if sin["papel"]=="saida" else "prefer."}</text>')
    if com_pecas:
        # painel de porta (pull-up) e fluxo
        for p in S["portas"]:
            k = p["letra"].lower()
            d = next(q for q in S["portas_salao"] if q["id"] == p["porta"])
            cx = (d["x1"] + d["x2"]) / 2
            off = 3.4 if p["letra"] != "C" else -3.4
            o.append(f'<circle class="peca t-{k}" cx="{cx+off:.2f}" cy="{Y(3.2):.2f}" r=".85"/>')
            o.append(f'<text class="tagpeca t-{k}" x="{cx+off+(1.3 if off>0 else -1.3):.2f}" y="{Y(3.2)+0.6:.2f}" text-anchor="{"start" if off>0 else "end"}">painel {p["letra"]}</text>')
            if p["parede"] == "oeste":
                path = f"M {cx} {Y(0)} L {cx} {Y(6)} L 6.5 {Y(6)} L 6.5 {Y(A-7)}"
            elif p["parede"] == "leste":
                path = f"M {cx} {Y(0)} L {cx} {Y(6)} L {L-6.5} {Y(6)} L {L-6.5} {Y(A-7)}"
            else:
                path = f"M {cx} {Y(0)} L {cx} {Y(A-6)}"
            o.append(f'<path class="fluxo t-{k}" d="{path}"/>')
    o.append(f'<text class="centro" x="{L/2}" y="{Y(A/2-2)}" text-anchor="middle">MIOLO LIVRE · circulação</text>')
    o.append('</svg>')
    return "".join(o)


# ---------------------------------------------------------------------------
# Pagina 1: Rota do Eleitor
# ---------------------------------------------------------------------------
def pagina_rota(S):
    P = S["portas"]
    M = S["mestra"]
    modelos = S["modelos"]
    tot = S["orcamento"]["total"]
    ext = [p for p in S["pecas"] if p["externo"] and p["modelo"] != "fixacao"]
    n_ext = sum(p["qtd"] for p in ext)
    n_int = sum(p["qtd"] for p in S["pecas"] if not p["externo"])
    linhas_pecas = "".join(
        f'<tr><td class="pt">{p["ponto"]}<span class="sub">{esc(p["nome"])}</span></td><td>{esc(p["onde"])}</td>'
        f'<td>{esc(p["diz"])}</td><td>{esc(modelos[p["modelo"]]["nome"])}<span class="sub">{esc(p["corpo"])}</span></td>'
        f'<td class="num">{p["qtd"]}</td><td>{esc(p["fixacao"])}</td></tr>'
        for p in S["pecas"] if p["modelo"] != "fixacao")
    zonas = "".join(
        f'<article class="zona t-{p["letra"].lower()}"><h4>Zona {p["letra"]} → porta {p["letra"]} · parede {p["parede"]}</h4>'
        f'<p class="sub">{len(p["secoes"])} seções · {br(p["esperado"])} eleitores esperados</p>'
        f'<div class="grid-sec">' + "".join(f'<span class="sec">{pad(s)}</span>' for s in p["secoes"]) + '</div></article>'
        for p in P)
    amb = ", ".join(S["condados_ambiguos"])
    return f"""<title>Rota do Eleitor RDS</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;600;700&family=IBM+Plex+Mono:wght@400;600&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400&display=swap">
<style>
  :root{{
    --ink:#16202b; --ground:#f1f3f0; --surface:#ffffff; --surface-2:#e6eae5;
    --rule:#c6cfc8; --rule-soft:#dde3dd; --muted:#5c6a70; --alert:#a8352a; --alert-soft:#f7e3e0;
    --sans:"Archivo","Helvetica Neue",Arial,sans-serif;
    --serif:"Source Serif 4",Georgia,"Times New Roman",serif;
    --mono:"IBM Plex Mono",ui-monospace,"SF Mono",Menlo,monospace;
  }}
  @media (prefers-color-scheme:dark){{ :root:not([data-theme="light"]){{
    --ink:#e3eae6; --ground:#101719; --surface:#182022; --surface-2:#202a2d;
    --rule:#33403f; --rule-soft:#283335; --muted:#94a3a0; --alert:#e88375; --alert-soft:#3a201d; }} }}
  :root[data-theme="dark"]{{
    --ink:#e3eae6; --ground:#101719; --surface:#182022; --surface-2:#202a2d;
    --rule:#33403f; --rule-soft:#283335; --muted:#94a3a0; --alert:#e88375; --alert-soft:#3a201d; }}
  {tokens_css()}
  *{{box-sizing:border-box}}
  body{{background:var(--ground);color:var(--ink);font-family:var(--serif);font-size:17px;line-height:1.62;-webkit-font-smoothing:antialiased}}
  .wrap{{max-width:1080px;margin:0 auto;padding-inline:24px;padding-block:0 96px}}
  p{{margin:0 0 1.1em;max-width:68ch}} strong{{font-weight:600}} em{{font-style:italic}}
  header.mast{{padding:52px 0 30px;border-bottom:2px solid var(--ink)}}
  .eyebrow{{font-family:var(--sans);font-size:11.5px;font-weight:600;letter-spacing:.16em;text-transform:uppercase;color:var(--muted);margin:0 0 14px}}
  h1{{font-family:var(--sans);font-weight:700;font-size:clamp(34px,6vw,56px);line-height:1.02;letter-spacing:-.025em;margin:0 0 16px;text-wrap:balance}}
  .standfirst{{font-size:19px;color:var(--muted);max-width:60ch;margin:0}}
  .facts{{display:grid;grid-template-columns:repeat(auto-fit,minmax(128px,1fr));gap:1px;background:var(--rule);border:1px solid var(--rule);margin:28px 0 0}}
  .fact{{background:var(--ground);padding:13px 14px}}
  .fact dt{{font-family:var(--sans);font-size:10.5px;font-weight:600;letter-spacing:.11em;text-transform:uppercase;color:var(--muted);margin:0 0 5px}}
  .fact dd{{margin:0;font-family:var(--mono);font-size:21px;font-weight:600;font-variant-numeric:tabular-nums;letter-spacing:-.02em}}
  .fact dd span{{font-family:var(--sans);font-size:12px;font-weight:500;color:var(--muted)}}
  section{{padding-top:52px}}
  h2{{font-family:var(--sans);font-weight:700;font-size:26px;letter-spacing:-.018em;margin:0 0 6px;text-wrap:balance;display:flex;align-items:baseline;gap:13px}}
  h2 .num{{font-family:var(--mono);font-size:13px;font-weight:600;color:var(--muted);letter-spacing:0;flex:none}}
  h3{{font-family:var(--sans);font-weight:600;font-size:16px;margin:34px 0 9px}}
  .lede{{font-size:18.5px;color:var(--muted);max-width:62ch;margin:0 0 26px}}
  figure{{margin:30px 0;padding:0}}
  .figbox{{background:var(--surface);border:1px solid var(--rule);padding:20px 20px 14px;overflow-x:auto}}
  svg.diagram{{display:block;width:100%;min-width:560px;height:auto;color:var(--ink)}}
  figcaption{{font-size:14.5px;color:var(--muted);margin-top:12px;max-width:74ch}}
  .tscroll{{overflow-x:auto;margin:24px 0;border:1px solid var(--rule);background:var(--surface)}}
  table{{border-collapse:collapse;width:100%;min-width:640px;font-family:var(--sans);font-size:14px}}
  th{{text-align:left;font-weight:600;font-size:10.5px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);padding:11px 14px;border-bottom:1px solid var(--rule);background:var(--surface-2);vertical-align:bottom;white-space:nowrap}}
  td{{padding:11px 14px;border-bottom:1px solid var(--rule-soft);vertical-align:top}}
  tbody tr:last-child td{{border-bottom:0}}
  td.num,th.num{{font-family:var(--mono);font-variant-numeric:tabular-nums;text-align:right;white-space:nowrap}}
  td.pt{{font-family:var(--mono);font-weight:600;white-space:nowrap}}
  .sub{{display:block;color:var(--muted);font-size:12.5px;line-height:1.45;margin-top:3px;font-family:var(--sans);font-weight:400;white-space:normal}}
  .note{{border-left:3px solid var(--a);background:var(--surface);padding:16px 20px;margin:26px 0;font-size:16px}}
  .note.warn{{border-left-color:var(--alert);background:var(--alert-soft)}}
  .note p:last-child{{margin-bottom:0}}
  .note .tag{{font-family:var(--sans);font-size:10.5px;font-weight:600;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);display:block;margin-bottom:7px}}
  .note.warn .tag{{color:var(--alert)}}
  .specs{{display:grid;grid-template-columns:repeat(auto-fit,minmax(232px,1fr));gap:1px;background:var(--rule);border:1px solid var(--rule);margin:24px 0}}
  .spec{{background:var(--surface);padding:16px 17px}}
  .spec h4{{font-family:var(--sans);font-size:13px;font-weight:600;margin:0 0 8px}}
  .spec p{{font-size:14.5px;margin:0;color:var(--muted);max-width:none}}
  .spec .big{{font-family:var(--mono);font-size:24px;font-weight:600;color:var(--ink);display:block;margin:0 0 4px;letter-spacing:-.02em}}
  .zonas{{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:14px;margin:22px 0}}
  .zona{{background:var(--surface);border:1px solid var(--rule);border-left:5px solid var(--k);padding:16px;display:flex;flex-direction:column;gap:9px}}
  .zona h4{{font-family:var(--sans);color:var(--k);font-size:15px;margin:0}}
  .zona .sub{{font-family:var(--mono);font-size:12px;margin:0}}
  .grid-sec{{display:grid;grid-template-columns:repeat(3,1fr);gap:4px 10px;font-family:var(--mono);font-size:14px;font-weight:600}}
  ul.plain{{list-style:none;margin:20px 0;padding:0;display:flex;flex-direction:column;gap:10px;max-width:74ch}}
  ul.plain li{{display:grid;grid-template-columns:auto 1fr;gap:12px;font-size:16px;padding-bottom:10px;border-bottom:1px solid var(--rule-soft)}}
  ul.plain .n{{font-family:var(--mono);font-size:12.5px;color:var(--muted);padding-top:4px}}
  ul.plain b{{font-family:var(--sans);font-weight:600;font-size:15px}}
  footer{{margin-top:64px;padding-top:22px;border-top:1px solid var(--rule);font-size:13.5px;color:var(--muted);font-family:var(--sans)}}
  :focus-visible{{outline:2px solid var(--a);outline-offset:3px}}
  @media (prefers-reduced-motion:reduce){{*{{animation:none!important;transition:none!important}}}}
  {CSS_ORC}
</style>

<div class="wrap">
<header class="mast">
  <p class="eyebrow">Eleições 2026 · 1º turno · 4 de outubro · Posto de Dublin · revisão de 16/09</p>
  <h1>Rota do Eleitor</h1>
  <p class="standfirst">Da calçada da Merrion Road à porta do Hall 2 com uma única informação na mão: o número da seção. As mesas não têm mais número, o Ring 3 mudou de desenho, e todo banner externo vai amarrado em grade.</p>
  <dl class="facts">
    <div class="fact"><dt>Aptos</dt><dd>{br(S["comparecimento"]["aptos"])}</dd></div>
    <div class="fact"><dt>Seções</dt><dd>51</dd></div>
    <div class="fact"><dt>Comparecimento esperado</dt><dd>{br(S["comparecimento"]["total"])}</dd></div>
    <div class="fact"><dt>Portas</dt><dd>3 <span>A · B · C</span></dd></div>
    <div class="fact"><dt>Peças externas</dt><dd>{n_ext}</dd></div>
    <div class="fact"><dt>Peças internas</dt><dd>{n_int}</dd></div>
    <div class="fact"><dt>Orçamento de referência</dt><dd>{eur(tot)} <span>faixa {eur(S["faixa_orcamento"][0])}–{eur(S["faixa_orcamento"][1])}</span></dd></div>
  </dl>
</header>

<section id="tese">
  <h2><span class="num">01</span>O que mudou e o que isso decide</h2>
  <p class="lede">Uma consulta só, e ela ficou mais simples: seção → porta. Mas passou a ter um pré-requisito que antes era opcional.</p>
  <p>Na versão anterior o eleitor precisava descobrir a <em>mesa</em> e a <em>porta</em>. Com as mesas sem número, a mesa deixou de existir como informação: o eleitor procura a sua <strong>seção</strong> na lista da porta e, dentro do salão, procura a mesma seção no banner do bloco. A tabela mestra encolheu de três colunas para duas — <strong>seção → porta</strong> — e cabe num banner de 2 × 1 m com 51 linhas.</p>
  <p>O preço dessa simplificação é que <strong>não há mais nenhum atalho</strong>. Não existe regra numérica (as seções 33xx de Dublin estão nas três portas) e o condado também não serve: {amb} caem em duas portas cada. Quem chega sem saber o número da seção não consegue ser triado por ninguém, em lugar nenhum — e cada um desses casos, se for parar na garganta ou dentro do salão, custa um operador parado por dois ou três minutos. Por isso o plano ganha um ponto novo, <strong>P0, fora do RDS</strong>, na calçada, antes do portão: é ali, e só ali, que se resolve “não sei minha seção”. Depois do portão, todas as peças pressupõem a seção conhecida.</p>
  <p>A segunda mudança é o Ring 3. Não há mais garganta de pré-triagem nem três serpenteados centrados nas portas: o eleitor entra pelo <strong>canto nordeste</strong>, desce um corredor de 3 m pela lateral leste do cercado, vira no trecho de fundo e passa, nessa ordem, pelas <strong>bocas das zonas C, B e A</strong>. Cada boca é uma abertura de ~2,2 m numa linha de CCB — e é nas CCBs dessas bocas que os últimos banners externos se amarram. Dali em diante, a raia leva o eleitor sozinha até a porta certa.</p>
  <p>A terceira mudança é de fixação, e vem do orçamento e do vento: <strong>nenhuma peça externa tem base</strong>. Tudo o que fica ao ar livre vai em mesh (tela perfurada, que deixa o vento passar) amarrado ilhós a ilhós nas grades do portão, no gradil da Merrion Road e nas CCBs do Ring 3; na lateral do Hall 2, onde a parede abriga, lona fechada pendurada nas portas de serviço. As peças internas, sem vento, podem ser autoportantes.</p>
</section>

<section id="rota">
  <h2><span class="num">02</span>A rota e os oito pontos</h2>
  <p class="lede">Da calçada à urna. A consulta acontece antes do portão; do portão em diante o eleitor só confirma.</p>
  <figure>
  <div class="figbox">{figura_sitio(S)}
  </div>
  <figcaption>Em escala sobre a prancheta Paredes_ABC (Hall 2, {str(S["salao"]["largura"]).replace(".",",")} × {str(S["salao"]["altura"]).replace(".",",")} m) e a montagem adotada do Ring 3 (44 × 35 m, corredor em L de 3,0 m, zonas A 12,23 · B 14,14 · C 12,23 m com raias leste-oeste e vãos de 1,20 m). O ponto de consulta P0 fica na calçada, fora do recinto. A tabela mestra se repete em P0, P1, P2 e P3; nas bocas das zonas (P4) só aparecem as seções daquela zona; na fachada (P5) só a letra e a cor. A posição do portão de eleitores na Merrion Road e a do Ring 3 no apron são estimativas a conferir em campo.</figcaption>
  </figure>

  <div class="tscroll"><table style="min-width:980px"><thead><tr><th>Ponto</th><th>Onde fica</th><th>O que a peça diz</th><th>Modelo · corpo</th><th class="num">Qtd</th><th>Fixação</th></tr></thead><tbody>{linhas_pecas}</tbody></table></div>

  <div class="note">
    <span class="tag">P0 · o ponto que não pode faltar</span>
    <p>Mesa dobrável encostada no gradil da Merrion Road, 20 a 30 m antes do portão de eleitores, do lado de quem chega, com barreira própria para não represar a calçada. Dois a três operadores com o caderno de seções impresso (51 seções × nome do eleitor, entregue pelo Cartório), um celular com o e-Título aberto e cópia da tabela mestra. A cobertura de dados na calçada precisa ser testada na véspera; sem ela, o caderno impresso é o único recurso. Quem sai do P0 sai com a seção e a letra da porta anotadas — daí em diante a rota só confirma.</p>
    <p>A mesma mensagem precisa existir antes do dia: <strong>“descubra sua seção antes de sair de casa”</strong> é a chamada dominante da comunicação com o eleitor. Cada eleitor que chega sabendo a seção é um eleitor que não para no P0.</p>
  </div>
</section>

<section id="ring">
  <h2><span class="num">03</span>Dentro do Ring 3: três bocas, três listas</h2>
  <p>O corredor de chegada é de passagem, não de parada, e passa pelas bocas na ordem C → B → A. O banner de cada boca fica na CCB imediatamente <em>antes</em> da abertura, virado para o trecho de fundo, para ser lido em movimento a 10–15 m: letra da zona em 400 mm, cor da porta no fundo inteiro da peça, e as seções daquela zona em 80 mm. O eleitor que não encontra a sua seção na zona C segue em frente; o que passou da zona A sem encontrar volta pelo mesmo corredor — e é um caso para o operador do fundo, não para a boca.</p>
  <div class="zonas">{zonas}</div>
  <p>As três listas somam 51 seções e são exatamente as listas que o eleitor vai reencontrar no painel da porta, dentro do salão. A boca é o último ponto em que errar custa pouco: dali para a frente há 23 raias e ~300 m de serpenteado até a porta.</p>
  <div class="note warn">
    <span class="tag">O que a boca não resolve</span>
    <p>A pré-triagem humana perdeu endereço dentro do Ring: o corredor é estreito demais para conferência de documento. Fica um único operador no trecho de fundo, entre as bocas B e A, para reencaminhar quem passou da sua zona. E a corrente que entra pelo canto nordeste cruza o apron a leste, por onde a S8 despeja quem já votou — isso pede um operador ou uma CCB de separação no apron, não banner.</p>
  </div>
</section>

<section id="mestra">
  <h2><span class="num">04</span>Tabela mestra</h2>
  <p>As 51 seções em ordem crescente, com a porta. É o conteúdo literal de P0, P1, P2 e P3 — quatro pontos, sete cópias. Quatro dígitos, como no e-Título. A cor acompanha a letra do primeiro ao último nível, do gradil ao banner do bloco.</p>
  {tabela_mestra_html(M)}
</section>

<section id="parede">
  <h2><span class="num">05</span>A lateral leste do Hall 2</h2>
  <p>Continua sendo o trecho em que o eleitor mais tempo passa parado — 44 m de fila entre o portão e o apron — e por isso recebe a tabela mestra três vezes. As posições são as mesmas da revisão anterior: nos vãos entre as quatro saídas de emergência, nunca sobre elas, com 2 m livres de cada lado de cada vão.</p>
  <figure><div class="figbox">{figura_parede_leste(S)}</div>
  <figcaption>Três lonas de 1,8 × 1,2 m, borda inferior a 1,0 m do piso, centradas a 10,75 · 22,50 · 33,90 m do canto norte. A parede não aceita adesivo (bloco de concreto embaixo, chapa ondulada em cima), mas cada vão tem uma folha de porta de serviço em aço pintado: a lona vai pendurada nela por ganchos magnéticos nos quatro cantos. A parede abriga do vento; ainda assim nenhum canto fica solto.</figcaption></figure>
</section>

<section id="spec">
  <h2><span class="num">06</span>Vento, chuva e fixação</h2>
  <p>Dublin em outubro: entre 40% e 65% de chance de chuva no dia 4, conforme o limiar da fonte, e vento médio que uma lona fechada de 2 m² transforma em vela. A regra que sai daí é simples e vale para todas as peças externas.</p>
  <div class="specs">
    <div class="spec"><h4>Externo em grade, gradil ou CCB</h4><span class="big">mesh</span><p>Tela perfurada 70/30. Reduz a carga de vento a um terço; é o que o próprio RDS amarra no gradil da Merrion Road.</p></div>
    <div class="spec"><h4>Amarração</h4><span class="big">ilhós a ilhós</span><p>Abraçadeira em cada ilhós, a cada 50 cm, nas quatro bordas. Nenhum canto solto; nenhuma peça maior que o painel que a segura.</p></div>
    <div class="spec"><h4>Tamanho das peças de CCB</h4><span class="big">2,0 × 1,0 m</span><p>A CCB tem 2,0 m de largura e ~1,1 m de altura: a peça cobre o painel inteiro e não avança sobre a boca.</p></div>
    <div class="spec"><h4>Parede leste</h4><span class="big">lona 440 g</span><p>Só ali, porque a parede abriga. Pendurada na folha de aço da porta de serviço com ganchos magnéticos; testar um ímã na visita.</p></div>
    <div class="spec"><h4>Portas, no vidro</h4><span class="big">300 mm</span><p>Vinil recortado por dentro da cortina de vidro. Sem estrutura, legível a 60 m, do Ring 3.</p></div>
    <div class="spec"><h4>Interno</h4><span class="big">autoportante</span><p>Sem vento, o pull-up e o tripé em X bastam. Nenhuma peça interna precisa de fixação.</p></div>
    <div class="spec"><h4>Altura de letra</h4><span class="big">1 : 200</span><p>1 mm de letra para cada 200 mm de leitura. Tabela mestra em 30–40 mm (6–8 m), boca em 80 mm (15 m), bloco em 120 mm (20 m).</p></div>
    <div class="spec"><h4>Idiomas</h4><span class="big">PT + EN</span><p>Bilíngue nas peças de rua e de portão; numéricas nas listas de seção.</p></div>
    <div class="spec"><h4>Código de cor</h4><span class="big">3 tons</span><p>A azul, B âmbar, C magenta — os mesmos da prancheta e da montagem do Ring 3. Nunca azul-marinho com branco, que é a libré do RDS.</p></div>
  </div>
</section>

<section id="orcamento">
  <h2><span class="num">07</span>Orçamento</h2>
  <p class="lede">Modelos, quantidades e um total de referência dentro da faixa de {eur(S["faixa_orcamento"][0])} a {eur(S["faixa_orcamento"][1])}. Os preços unitários são editáveis.</p>
  {orcamento_html(S, "orc-rota")}
  <h3>Se estourar: ordem de cortes</h3>
  <ul class="plain">
    <li><span class="n">1</span><span><b>P3, a tabela na entrada do Ring 3</b> (−1 mesh). O eleitor já leu a tabela quatro vezes antes; a boca da zona ainda confirma.</span></li>
    <li><span class="n">2</span><span><b>Uma das duas tabelas mestras da calçada</b> (−1 mesh). Fica uma junto ao P0.</span></li>
    <li><span class="n">3</span><span><b>Painéis de porta em X-banner em vez de pull-up</b> (−3 × diferença). Perde robustez onde as pessoas esbarram, não perde informação.</span></li>
    <li><span class="n">4</span><span><b>P2 de três para duas lonas</b> (−1 PVC). A fila continua lendo a cada ~20 m.</span></li>
  </ul>
  <h3>Se sobrar: ordem de reforços</h3>
  <ul class="plain">
    <li><span class="n">1</span><span><b>Mais uma tabela mestra na calçada</b>, no trecho onde a fila da Merrion Road se forma no pico.</span></li>
    <li><span class="n">2</span><span><b>Um segundo painel da porta B</b> no meio do salão: é a única porta cujo destino não se vê da entrada (44 m até a parede norte).</span></li>
    <li><span class="n">3</span><span><b>Uma CCB de separação no apron</b> entre a corrente de chegada e a saída S8 — não é banner, mas resolve o único cruzamento que restou.</span></li>
  </ul>
</section>

<section id="pendencias">
  <h2><span class="num">08</span>Antes de imprimir</h2>
  <ul class="plain">
    <li><span class="n">01</span><span><b>O anexo de preços e modelos do Posto.</b> Não chegou a esta revisão; a tabela acima usa preços públicos de referência. Colar os preços do anexo nos campos e conferir se o total continua na faixa.</span></li>
    <li><span class="n">02</span><span><b>Autorização do RDS para o P0 no gradil da Merrion Road</b> e para a mesa na calçada (Dublin City Council, se a calçada for pública).</span></li>
    <li><span class="n">03</span><span><b>Ímã na porta de serviço.</b> Testar na visita se as folhas das portas da lateral leste são de aço e se o ímã segura 1,8 × 1,2 m de lona; se não, abraçadeira no batente.</span></li>
    <li><span class="n">04</span><span><b>Posição do portão de eleitores e do Ring 3 no apron</b> — as duas são estimativas neste desenho.</span></li>
    <li><span class="n">05</span><span><b>Caderno impresso das 51 seções para o P0</b>, pedido ao Cartório Eleitoral, e teste de cobertura de dados na calçada.</span></li>
    <li><span class="n">06</span><span><b>Congelar a atribuição seção → porta.</b> Ela vem da prancheta Paredes_ABC de 15/09; qualquer troca de mesa entre paredes depois da impressão invalida sete tabelas mestras e três bocas.</span></li>
  </ul>
</section>

<footer>
  <p>Gerado por <code>scripts/sinalizacao_v2.py</code> a partir de <code>data/prancheta_paredes_abc.json</code> (prancheta Paredes_ABC, 15/09/2026) e <code>saidas/dados.json</code> (TSE). Geometria do Ring 3 da montagem adotada em 15/09/2026 (44 × 35 m, corredor em L de 3,0 m, 180 CCBs). Comparecimento esperado: base B, taxa de 2022 por domicílio de origem, não oficial. Validação automática: as 51 seções aparecem exatamente uma vez, os aptos somam 16.794 e as 28 mesas fecham.</p>
  <p>Preços de referência (inc. IVA, 16/09/2026): pull-up 850 × 2000 €80–90 (PrintNPack, Bannerz.ie); mesh “from €20 + VAT” (Kaizen Print, Printroom); PVC pequeno €25–45 e grande €60–150 (PrintNPack); correx “from €5” (Printco). Onde não há fonte irlandesa a peça está marcada como premissa.</p>
</footer>
</div>
"""


# ---------------------------------------------------------------------------
# Pagina 2: Sinalizacao interna do Hall 2
# ---------------------------------------------------------------------------
def pagina_hall(S):
    P = S["portas"]
    tiles = "".join(
        f'<article class="tile t-{p["letra"].lower()}"><p class="tile-k">Porta {p["letra"]}</p><p class="tile-w">{p["porta"]} → parede {p["parede"]}</p>'
        f'<dl><div><dt>mesas</dt><dd>{p["mesas"]}</dd></div><div><dt>blocos</dt><dd>{len(p["blocos"])}</dd></div>'
        f'<div><dt>seções</dt><dd>{len(p["secoes"])}</dd></div><div><dt>aptos</dt><dd>{br(p["aptos"])}</dd></div>'
        f'<div class="hi"><dt>esperados</dt><dd>{br(p["esperado"])}</dd></div></dl></article>' for p in P)

    def tabela_blocos(p):
        rows = "".join(
            f'<tr><th scope="row">{b["id"]}</th><td><span class="tag {"tag-par" if b["tipo"]=="par" else "tag-isolada"}">{b["tipo"]}</span></td>'
            f'<td class="num">{" – ".join(str(c).replace(".",",") for c in b["coord"])} m</td>'
            f'<td class="secs">' + "".join(f'<span class="sec">{pad(s)}</span>' for s in b["secoes"]) + '</td>'
            f'<td class="num">{br(b["aptos"])}</td><td class="num">{br(b["esperado"])}</td></tr>' for b in p["blocos"])
        return (f'<section class="wall t-{p["letra"].lower()}"><h3>Porta {p["letra"]} <span>parede {p["parede"]} · {p["pares"]} pares + {p["isoladas"]} isolada(s)</span></h3>'
                f'<div class="scroll"><table><thead><tr><th scope="col">Peça</th><th scope="col">Tipo</th><th scope="col">Posição na parede</th>'
                f'<th scope="col">Seções impressas</th><th scope="col">Aptos</th><th scope="col">Esperados</th></tr></thead><tbody>{rows}</tbody></table></div></section>')

    paineis = "".join(
        f'<article class="lista t-{p["letra"].lower()}"><h4>Porta {p["letra"]} · parede {p["parede"]}</h4><p class="sub">{len(p["secoes"])} seções · na ordem em que o eleitor as encontra</p>'
        + "".join(f'<div class="grupo"><span class="gn">{b["id"]}</span><div class="grid-sec">' + "".join(f'<span class="sec">{pad(s)}</span>' for s in b["secoes"]) + '</div></div>' for b in p["blocos"])
        + f'<p class="rodape">não encontrou a sua? procure um mesário — sua seção está em outra porta</p></article>' for p in P)
    n_blocos = sum(len(p["blocos"]) for p in P)
    cargas = [p["esperado"] for p in P]
    ampl = max(cargas) - min(cargas)
    return f"""<title>Sinalização RDS Hall 2</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;600;800&family=IBM+Plex+Mono:wght@400;600&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&display=swap">
<style>
:root{{
  --paper:#F5F7F4; --card:#FFFFFF; --ink:#161B18; --mid:#4C554F; --muted:#6B7570;
  --rule:#D6DDD7; --rule-soft:#E6EBE6; --warn:#9B2860; --emerg:#0e8a74; --apoio:#8a5a2b; --serp:#c0392b;
  --ground:var(--paper); --surface:var(--card); --surface-2:var(--rule-soft); --alert:var(--warn);
  --disp:"Archivo","Helvetica Neue",Arial,sans-serif; --sans:var(--disp);
  --body:"Source Serif 4",Georgia,"Times New Roman",serif;
  --mono:"IBM Plex Mono",ui-monospace,"SF Mono",Menlo,monospace;
  --measure:64ch;
}}
@media (prefers-color-scheme:dark){{ :root:not([data-theme="light"]){{
  --paper:#0F1412; --card:#171E1A; --ink:#E7EDE8; --mid:#B4BEB7; --muted:#8B958E;
  --rule:#2A332D; --rule-soft:#222A25; --warn:#EE85B2; --emerg:#42c0a5; --apoio:#c08e56; --serp:#e8806f; }} }}
:root[data-theme="dark"]{{
  --paper:#0F1412; --card:#171E1A; --ink:#E7EDE8; --mid:#B4BEB7; --muted:#8B958E;
  --rule:#2A332D; --rule-soft:#222A25; --warn:#EE85B2; --emerg:#42c0a5; --apoio:#c08e56; --serp:#e8806f; }}
{tokens_css()}
*{{box-sizing:border-box}}
body{{background:var(--paper);color:var(--ink);font-family:var(--body);font-size:17px;line-height:1.62;-webkit-text-size-adjust:100%}}
.page{{max-width:1080px;margin:0 auto;padding-inline:20px;padding-block:0 72px}}
.col{{max-width:var(--measure)}}
h1,h2,h3,h4,.tile-k,.eyebrow,.letra,th{{font-family:var(--disp)}}
h1{{font-size:clamp(2rem,5.4vw,3.15rem);line-height:1.04;font-weight:800;letter-spacing:-.022em;margin:0;text-wrap:balance}}
h2{{font-size:clamp(1.3rem,2.9vw,1.72rem);font-weight:700;letter-spacing:-.014em;line-height:1.16;margin:0;text-wrap:balance}}
h3{{font-size:1.05rem;font-weight:600;margin:0}} h4{{font-size:.95rem;font-weight:600;margin:0}} p{{margin:0}}
.eyebrow{{font-size:.7rem;font-weight:600;letter-spacing:.15em;text-transform:uppercase;color:var(--muted);margin:0}}
strong{{font-weight:600}} code,.sec,.num,.mono{{font-family:var(--mono);font-variant-numeric:tabular-nums}}
header.masthead{{display:flex;flex-direction:column;gap:18px;padding-block:56px 30px;border-bottom:2px solid var(--ink)}}
.lede{{font-size:1.09rem;color:var(--mid);max-width:58ch}}
.meta{{display:flex;flex-wrap:wrap;gap:6px 22px;font-family:var(--mono);font-size:.74rem;color:var(--muted);letter-spacing:.02em;padding-top:4px}}
section.band{{display:flex;flex-direction:column;gap:20px;padding-block:44px;border-bottom:1px solid var(--rule-soft)}}
section.band:last-of-type{{border-bottom:0}}
.band > p, .band > ul, .band > ol{{max-width:var(--measure)}}
.hd{{display:flex;flex-direction:column;gap:7px}}
.tiles{{display:grid;grid-template-columns:repeat(auto-fit,minmax(215px,1fr));gap:14px}}
.tile{{background:var(--card);border:1px solid var(--rule);border-top:5px solid var(--k);padding:18px 18px 14px;display:flex;flex-direction:column;gap:12px}}
.tile-k{{font-size:1.5rem;font-weight:800;letter-spacing:-.02em;color:var(--k);margin:0;line-height:1}}
.tile-w{{font-size:.78rem;color:var(--muted);margin:0;letter-spacing:.04em;text-transform:uppercase;font-family:var(--disp);font-weight:500}}
.tile dl{{margin:0;display:flex;flex-direction:column}}
.tile dl div{{display:flex;justify-content:space-between;align-items:baseline;gap:12px;padding:5px 0;border-top:1px solid var(--rule-soft)}}
.tile dl dt{{color:var(--muted);font-size:.8rem}} .tile dl dd{{margin:0;font-family:var(--mono);font-size:.93rem;font-variant-numeric:tabular-nums}}
.tile dl .hi dd{{font-weight:600;color:var(--k)}}
figure.plan{{margin:0;display:flex;flex-direction:column;gap:12px}}
.plan-wrap{{background:var(--card);border:1px solid var(--rule);padding:12px}}
svg.planta{{display:block;width:100%;height:auto;max-width:100%}}
.planta .salao{{fill:none;stroke:var(--ink);stroke-width:.34}}
.planta .bloco{{fill:var(--k);opacity:.12;stroke:none}} .planta .mesa{{fill:var(--k);stroke:none}}
.planta .rot{{font-family:var(--mono);font-size:1.25px;fill:var(--k);paint-order:stroke fill;stroke:var(--card);stroke-width:.5px;stroke-linejoin:round}}
.planta .porta{{fill:var(--k)}} .planta .porta-saida{{fill:var(--muted)}} .planta .porta-pref{{fill:var(--emerg)}}
.planta .peca{{fill:var(--k);stroke:var(--card);stroke-width:.3}}
.planta .tagpeca{{font-family:var(--disp);font-weight:700;font-size:2px;fill:var(--k);paint-order:stroke fill;stroke:var(--card);stroke-width:.6px}}
.planta .letra{{font-family:var(--disp);font-weight:800;font-size:4.2px;fill:var(--k)}}
.planta .mini{{font-family:var(--disp);font-size:1.6px;fill:var(--muted)}}
.planta .fluxo{{fill:none;stroke:var(--k);stroke-width:.4;stroke-dasharray:1.5 1.2;opacity:.7;stroke-linejoin:round}}
.planta .zona-emerg{{fill:var(--emerg);fill-opacity:.08;stroke:var(--emerg);stroke-width:.15;stroke-dasharray:.8 .6}}
.planta .zona-recuo{{fill:var(--muted);fill-opacity:.07;stroke:var(--muted);stroke-width:.15;stroke-dasharray:.8 .6}}
.planta .zona-apoio{{fill:var(--apoio);fill-opacity:.12;stroke:var(--apoio);stroke-width:.2;stroke-dasharray:.8 .6}}
.planta .serp{{fill:var(--serp);fill-opacity:.10;stroke:var(--serp);stroke-width:.2;stroke-dasharray:.6 .6}}
.planta .centro{{font-family:var(--disp);font-weight:600;font-size:1.75px;fill:var(--muted);letter-spacing:.11em}}
.planta .rosa text{{font-family:var(--disp);font-weight:600;font-size:2.7px;fill:var(--muted)}}
figcaption{{font-size:.86rem;color:var(--muted);max-width:var(--measure)}}
ol.journey{{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;max-width:none}}
ol.journey li{{display:grid;grid-template-columns:62px 1fr;gap:18px;padding:16px 0;border-top:1px solid var(--rule)}}
ol.journey li:last-child{{border-bottom:1px solid var(--rule)}}
.lvl{{font-family:var(--mono);font-size:.76rem;font-weight:600;color:var(--muted);letter-spacing:.06em;padding-top:4px}}
.j-b{{display:flex;flex-direction:column;gap:5px}} .j-h{{display:flex;flex-wrap:wrap;align-items:baseline;gap:8px 12px}} .j-h h4{{font-size:1rem}}
.qty{{font-family:var(--mono);font-size:.75rem;color:var(--muted);border:1px solid var(--rule);padding:1px 7px;border-radius:99px;white-space:nowrap}}
.j-b p{{font-size:.95rem;color:var(--mid);max-width:60ch}}
.wall{{display:flex;flex-direction:column;gap:10px;margin-top:8px}}
.wall h3{{color:var(--k);display:flex;flex-wrap:wrap;align-items:baseline;gap:10px}}
.wall h3 span{{font-family:var(--mono);font-size:.74rem;color:var(--muted);font-weight:400}}
.scroll,.tscroll{{overflow-x:auto;background:var(--card);border:1px solid var(--rule)}}
table{{border-collapse:collapse;width:100%;min-width:600px;font-size:.88rem}}
th,td{{text-align:left;padding:9px 12px;border-bottom:1px solid var(--rule-soft)}}
thead th{{font-size:.68rem;letter-spacing:.09em;text-transform:uppercase;color:var(--muted);font-weight:600;border-bottom:1px solid var(--rule);white-space:nowrap}}
tbody tr:last-child td,tbody tr:last-child th{{border-bottom:0}}
tbody th{{font-family:var(--mono);font-weight:600;color:var(--k);white-space:nowrap}}
td.num{{font-family:var(--mono);font-variant-numeric:tabular-nums;white-space:nowrap;color:var(--mid);text-align:right}}
td.pt{{font-family:var(--mono);font-weight:600;white-space:nowrap}}
td.secs{{min-width:210px}}
.sec{{display:inline-block;font-size:.85rem;font-weight:600;letter-spacing:.01em;margin:1px 9px 1px 0}}
.tag{{font-family:var(--disp);font-size:.65rem;font-weight:600;letter-spacing:.08em;text-transform:uppercase;padding:2px 7px;border-radius:2px;white-space:nowrap}}
.tag-par{{background:var(--k);color:var(--card)}} .tag-isolada{{background:transparent;color:var(--muted);box-shadow:inset 0 0 0 1px var(--rule)}}
.listas{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:14px}}
.lista{{background:var(--card);border:1px solid var(--rule);border-left:5px solid var(--k);padding:16px;display:flex;flex-direction:column;gap:10px}}
.lista h4{{color:var(--k);font-size:1rem}} .lista .sub{{font-family:var(--mono);font-size:.72rem;color:var(--muted)}}
.grupo{{display:grid;grid-template-columns:34px 1fr;gap:8px;align-items:start;padding-top:6px;border-top:1px solid var(--rule-soft)}}
.gn{{font-family:var(--mono);font-size:.7rem;color:var(--muted);padding-top:3px}}
.grid-sec{{display:grid;grid-template-columns:repeat(2,1fr);gap:2px 10px}} .grid-sec .sec{{margin:0;color:var(--ink)}}
.rodape{{font-size:.8rem;color:var(--muted);font-style:italic;padding-top:6px;border-top:1px solid var(--rule-soft)}}
.finds{{display:flex;flex-direction:column}}
.find{{display:grid;grid-template-columns:auto 1fr;gap:16px;padding:18px 0;border-top:1px solid var(--rule)}}
.finds .find:last-child{{border-bottom:1px solid var(--rule)}}
.find .k{{font-family:var(--disp);font-size:1.6rem;font-weight:800;color:var(--rule);line-height:1;padding-top:2px}}
.find-b{{display:flex;flex-direction:column;gap:6px;max-width:62ch}} .find h4{{font-size:1.02rem}} .find p{{font-size:.95rem;color:var(--mid)}}
.find.alert h4{{color:var(--warn)}}
.note{{border-left:3px solid var(--warn);padding:2px 0 2px 16px;font-size:.95rem;color:var(--mid);max-width:var(--measure)}}
.note b{{color:var(--warn);font-weight:600}}
ul.plain{{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:9px}}
ul.plain li{{display:grid;grid-template-columns:auto 1fr;gap:12px;font-size:.95rem;color:var(--mid);padding-bottom:9px;border-bottom:1px solid var(--rule-soft)}}
ul.plain li:last-child{{border-bottom:0;padding-bottom:0}}
ul.plain .n{{font-family:var(--mono);font-size:.78rem;color:var(--muted);padding-top:3px}} ul.plain b{{color:var(--ink);font-weight:600}}
.legenda{{display:flex;flex-wrap:wrap;gap:8px 22px;font-size:.83rem;color:var(--muted)}}
.legenda span{{display:inline-flex;align-items:center;gap:7px}} .sw{{width:13px;height:13px;border-radius:2px;flex:none}}
footer{{padding-block:34px 0;border-top:2px solid var(--ink);margin-top:44px;font-size:.82rem;color:var(--muted);display:flex;flex-direction:column;gap:6px}}
footer code{{font-size:.78rem}}
@media (max-width:560px){{ body{{font-size:16px}} ol.journey li{{grid-template-columns:1fr;gap:6px}} .find{{grid-template-columns:1fr;gap:6px}} .find .k{{font-size:1.1rem}} }}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important;transition:none!important}}}}
:focus-visible{{outline:2px solid var(--a);outline-offset:3px}}
{CSS_ORC}
.orc .modelo label{{font-family:var(--disp)}} .orctab{{font-size:.88rem}}
</style>

<div class="page">
<header class="masthead">
  <p class="eyebrow">Posto de Dublin · 1º turno · 04 out 2026 · revisão de 16/09</p>
  <h1>Sinalização interna do RDS&nbsp;Hall&nbsp;2</h1>
  <p class="lede">Três portas, três paredes, 28 mesas sem número em {n_blocos} blocos. O eleitor entra sabendo a seção e a letra da porta; lá dentro, só reencontra a seção — primeiro no painel da porta, depois no banner do bloco.</p>
  <div class="meta">
    <span>prancheta {S["prancheta"]["nome"]} · {S["prancheta"]["id"]}</span>
    <span>{br(S["comparecimento"]["aptos"])} aptos</span>
    <span>{br(S["comparecimento"]["total"])} comparecimento esperado</span>
    <span>51 seções</span>
  </div>
</header>

<section class="band">
  <div class="hd"><p class="eyebrow">A regra que organiza tudo</p><h2>Porta A leva ao oeste, B ao norte, C ao leste — e as mesas não têm número</h2></div>
  <p class="col">O salão está em orientação L-O e as três portas ficam na parede sul, a única livre na prancheta. Cada porta atende uma parede e nenhuma outra. A prancheta Paredes_ABC de 15/09 redistribuiu as mesas para equilibrar a carga por porta: a amplitude entre as três caiu para <strong>{ampl} eleitores esperados</strong>. E a numeração das mesas saiu de toda peça: o eleitor procura a seção, e a seção é o único texto das listas.</p>
  <div class="tiles">{tiles}</div>
</section>

<section class="band">
  <div class="hd"><p class="eyebrow">Planta em escala · {str(S["salao"]["largura"]).replace(".",",")} × {str(S["salao"]["altura"]).replace(".",",")} m</p><h2>Onde cada peça fica e o que ela diz</h2></div>
  <figure class="plan"><div class="plan-wrap">{figura_planta_hall(S, None)}</div>
  <figcaption>Cada retângulo cheio é uma mesa, na coordenada da prancheta; o bloco sombreado é o par que compartilha o corredor de 3,0 m e, portanto, o banner. Os números ao lado de cada bloco são o que vai impresso no banner daquele bloco. Círculo: painel da porta (pull-up). Retângulo pequeno na boca do corredor: banner de bloco (X-banner). Tracejado: o percurso da porta até a parede. Áreas tracejadas: faixa de 3 m das saídas de emergência L1–L4, recuos de N2, O2, S3, S7 e R1, sala de apoio; em vermelho, o espaço reservado ao serpenteado das três mesas mais carregadas.</figcaption></figure>
  <div class="legenda">
    <span><i class="sw" style="background:var(--a)"></i>porta A · parede oeste</span>
    <span><i class="sw" style="background:var(--b)"></i>porta B · parede norte</span>
    <span><i class="sw" style="background:var(--c)"></i>porta C · parede leste</span>
    <span><i class="sw" style="background:var(--emerg)"></i>S7 preferencial · faixa de emergência</span>
    <span><i class="sw" style="background:var(--muted)"></i>S2 · S8 saídas</span>
    <span><i class="sw" style="background:var(--serp)"></i>serpenteado reservado</span>
  </div>
</section>

<section class="band">
  <div class="hd"><p class="eyebrow">O percurso do eleitor · {3 + n_blocos + 2} peças internas</p><h2>Três níveis, na ordem em que são lidos</h2></div>
  <ol class="journey">
    <li><span class="lvl">N0</span><div class="j-b"><div class="j-h"><h4>Antes da porta: a boca da zona no Ring 3</h4><span class="qty">3 un · plano externo</span></div>
      <p>Não é peça interna, mas é a premissa de todas elas: o eleitor só chega à porta A porque entrou na zona A do Ring 3, cuja boca lista as {len(P[0]["secoes"])} seções da parede oeste. A lista da boca e a lista do painel da porta são a mesma, na mesma cor. Ver a Rota do Eleitor.</p></div></li>
    <li><span class="lvl">N1</span><div class="j-b"><div class="j-h"><h4>Painel da porta</h4><span class="qty">3 un · pull-up 850 × 2000</span></div>
      <p>Logo depois da porta, do lado oposto à curva que o eleitor faz (A vira a oeste, C vira a leste, B segue reto), para que quem para de ler não represe a entrada. Letra da porta em 300 mm no alto, cor da porta no fundo, e as seções da parede em 60 mm <strong>agrupadas por bloco e na ordem física</strong> em que o eleitor vai encontrá-las — o painel espelha a parede. É a única confirmação até o bloco, e para a porta B resolve a travessia de 40 m até a parede norte. Substitui o totem e a lista da revisão anterior numa peça só.</p></div></li>
    <li><span class="lvl">N2</span><div class="j-b"><div class="j-h"><h4>Banner de bloco</h4><span class="qty">{n_blocos} un · X-banner 600 × 1600 · peça crítica</span></div>
      <p>Na boca do corredor de cada par, a 4,6 m da parede, lido de dentro da fila em movimento: só as seções do bloco (duas a quatro), em 120 mm, quatro dígitos. <strong>Nenhum número de mesa.</strong> Dentro do par, cada mesa se distingue pelas suas seções — o eleitor da 3313 entra na via da 3313, não “na mesa da esquerda”.</p></div></li>
    <li><span class="lvl">N3</span><div class="j-b"><div class="j-h"><h4>Saídas</h4><span class="qty">2 un · correx A2</span></div>
      <p>SAÍDA / WAY OUT sobre S2 e S8, que ficam nos flancos, fora do vão das entradas: os fluxos se separam sozinhos.</p></div></li>
  </ol>
  <p class="col">Em todas as peças: seção com <strong>4 dígitos</strong>, como no e-Título (<code>0511</code>, não <code>511</code>); ordem crescente dentro de cada bloco; a cor da porta constante do gradil da Merrion Road ao banner do bloco — A azul, B âmbar, C magenta, a mesma paleta da prancheta e da montagem do Ring 3.</p>
</section>

<section class="band">
  <div class="hd"><p class="eyebrow">N2 · conteúdo literal</p><h2>Os {n_blocos} banners de bloco</h2></div>
  <p class="col">A coluna de posição é para a equipe de montagem — não vai impressa. Nada aqui carrega número de mesa; os MRVs ficam em <code>saidas/sinalizacao_v2.json</code> para o Cartório.</p>
  {"".join(tabela_blocos(p) for p in P)}
</section>

<section class="band">
  <div class="hd"><p class="eyebrow">N1 · conteúdo literal</p><h2>Os 3 painéis de porta</h2></div>
  <p class="col">Blocos na ordem física da parede, do ponto em que o eleitor chega. Na arte, quatro dígitos e o rodapé obrigatório.</p>
  <div class="listas">{paineis}</div>
</section>

<section class="band">
  <div class="hd"><p class="eyebrow">Filas no piso</p><h2>Uma via por mesa, nenhuma cruza outra</h2></div>
  <p class="col"><strong>A fila é por mesa, não por par.</strong> Cada mesa guarda o caderno das suas próprias seções; o eleitor da 3313 não pode ser atendido na mesa ao lado. São 28 filas em {n_blocos} blocos: o banner é do bloco, a fita no chão desce ao nível da mesa e se bifurca dentro do corredor de 3,0 m do par, um ramo por conjunto de seções, com o decalque da seção na cauda.</p>
  <p class="col">A regra que garante o não cruzamento continua geométrica: cada mesa é dona da faixa de piso à sua frente, tão larga quanto o vão até a vizinha, e essa faixa avança perpendicular à própria parede. Toda a circulação acontece no miolo livre; o eleitor entra na via pela cauda. A prancheta já reserva, à frente das três mesas de maior carga (3313·3889, 3315·3778, 3322·3752), o retângulo de um serpenteado de ~20 pessoas em duas raias de 4,2 m, com 1,90 m de folga dos dois lados.</p>
  <p class="note"><b>O dimensionamento mesa a mesa das vias saiu desta revisão.</b> Ele foi calculado sobre a prancheta anterior (Hamad_Final) e as posições mudaram; a simulação a 60 s por voto precisa ser refeita sobre a Paredes_ABC antes de qualquer colagem. O que não muda: a 90 s por voto o piso não comporta a fila, qualquer que seja a prancheta.</p>
</section>

<section class="band">
  <div class="hd"><p class="eyebrow">Achados que condicionam o plano</p><h2>Quatro coisas que não dá para contornar com design</h2></div>
  <div class="finds">
    <div class="find alert"><span class="k">01</span><div class="find-b"><h4>Não existe regra numérica que leve o eleitor à porta certa</h4>
      <p>As seções 33xx de Dublin continuam espalhadas pelas três portas. Nenhuma peça pode usar faixa de numeração; toda peça de triagem carrega a lista completa.</p></div></div>
    <div class="find alert"><span class="k">02</span><div class="find-b"><h4>Nem o condado serve de atalho</h4>
      <p>{", ".join(S["condados_ambiguos"])} caem em duas portas cada. O eleitor do interior só pode ser triado pelo número da seção — e quem não o sabe precisa do ponto de consulta fora do RDS, não de um mesário na porta.</p></div></div>
    <div class="find"><span class="k">03</span><div class="find-b"><h4>Sem número de mesa, o bloco é a menor unidade nomeável</h4>
      <p>O eleitor não pode ser mandado “à mesa 12”: é mandado à parede, depois ao bloco, depois à via da sua seção. Por isso o painel da porta precisa espelhar a ordem física dos blocos, e por isso o banner de bloco é a peça crítica.</p></div></div>
    <div class="find"><span class="k">04</span><div class="find-b"><h4>A porta B é a única cujo destino não se vê da entrada</h4>
      <p>São ~40 m de travessia pelo miolo até a parede norte. Se sobrar orçamento, o primeiro reforço é um segundo painel da porta B no meio do salão.</p></div></div>
  </div>
</section>

<section class="band">
  <div class="hd"><p class="eyebrow">Separadores físicos · item (d) do orçamento</p><h2>A fita muda a conta</h2></div>
  <p class="col">Com o miolo livre fazendo o papel de corredor-tronco, o separador físico (unifila, 100 un / 200 m) deixa de acompanhar as três paredes. Sobram três usos em que a fita no chão não basta: a <strong>bifurcação dentro do corredor de 3,0 m de cada par</strong>, onde duas vias se separam a menos de dois metros uma da outra; o <strong>recuo das três mesas de maior carga</strong>, cujo serpenteado de duas raias precisa de ponta rígida; e a <strong>separação no apron</strong> entre a corrente que chega ao Ring 3 e a saída S8. A fila externa inteira agora é do Ring 3 (180 CCBs do estoque de 200) e não sai deste item.</p>
</section>

<section class="band">
  <div class="hd"><p class="eyebrow">Tabela mestra · 51 seções</p><h2>Seção → porta</h2></div>
  <p class="col">A peça mais reaproveitável do plano: é o conteúdo literal das sete tabelas externas, do Instagram e do site, do roteiro dos orientadores e do cartão de bolso dos mesários. Ordem crescente de seção, porque é assim que o eleitor procura.</p>
  {tabela_mestra_html(S["mestra"])}
</section>

<section class="band">
  <div class="hd"><p class="eyebrow">Orçamento · peças internas e externas</p><h2>Onde os {eur(S["faixa_orcamento"][0])}–{eur(S["faixa_orcamento"][1])} vão</h2></div>
  <p class="col">A mesma tabela da Rota do Eleitor, para fechar as duas listas de uma vez. As peças internas não precisam de fixação: pull-up e X-banner são autoportantes. Os preços unitários são editáveis.</p>
  {orcamento_html(S, "orc-hall")}
</section>

<section class="band">
  <div class="hd"><p class="eyebrow">Antes de fechar a arte</p><h2>Cinco pendências</h2></div>
  <ul class="plain">
    <li><span class="n">01</span><span><b>Congelar a prancheta Paredes_ABC.</b> Qualquer troca de mesa entre paredes muda três painéis de porta, as bocas do Ring 3 e sete tabelas mestras.</span></li>
    <li><span class="n">02</span><span><b>Confirmar a posição real das portas S4 · S5 · S6 e S7</b> na parede sul, contra a planta cotada do RDS.</span></li>
    <li><span class="n">03</span><span><b>Refazer a simulação das vias de fila</b> sobre a nova prancheta antes de comprar fita e decalque.</span></li>
    <li><span class="n">04</span><span><b>Colar os preços do anexo do Posto</b> na tabela e conferir a faixa.</span></li>
    <li><span class="n">05</span><span><b>Medir o contraste do âmbar da porta B sobre branco</b> antes de imprimir; no plano anterior o âmbar era da porta C.</span></li>
  </ul>
</section>

<footer>
  <p>Gerado por <code>scripts/sinalizacao_v2.py</code>, a partir de <code>data/prancheta_paredes_abc.json</code> (prancheta Paredes_ABC, 15/09/2026) e <code>saidas/dados.json</code>.</p>
  <p>Validação automática: as 51 seções aparecem exatamente uma vez, os aptos somam 16.794 e as 28 mesas fecham — o script falha em vez de gravar um plano que não bata com a base do TSE.</p>
</footer>
</div>
"""


def main():
    S = monta()
    SAIDAS.mkdir(exist_ok=True)
    (SAIDAS / "sinalizacao_v2.json").write_text(json.dumps(S, ensure_ascii=False, indent=1), encoding="utf-8")
    (SAIDAS / "rota_do_eleitor_v2.html").write_text(pagina_rota(S), encoding="utf-8")
    (SAIDAS / "sinalizacao_hall2_v2.html").write_text(pagina_hall(S), encoding="utf-8")
    o = S["orcamento"]
    print("blocos:", [len(p["blocos"]) for p in S["portas"]],
          "secoes/porta:", [len(p["secoes"]) for p in S["portas"]])
    for k, v in o["por_modelo"].items():
        print(f"  {k:9s} {v['qtd']:3d} × {MODELOS[k]['preco']:6.0f} = {v['total']:8.2f}")
    print("TOTAL", o["total"], "faixa", S["faixa_orcamento"])
    print("condados ambiguos:", S["condados_ambiguos"])


if __name__ == "__main__":
    main()
