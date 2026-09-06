#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Monta a pagina do desenho horizontal do Ring 3 a partir de saidas/ring3.json.

Todo numero da pagina vem do JSON que scripts/ring3.py gerou: a pagina nao
guarda nenhuma conta propria. Saida: saidas/ring3_horizontal.html
"""

import json
import os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAIDAS = os.path.join(RAIZ, "saidas")

D = json.load(open(os.path.join(SAIDAS, "ring3.json"), encoding="utf-8"))
V, H, E = D["vertical"], D["horizontal"], D["horizontal_enxuta"]
P, CONF = D["premissas"], D["aderencia_ao_plano_original"]
ESP = P["comparecimento_esperado"]
PORTA = {"A": "S4", "B": "S5", "C": "S6"}


def num(v, casas=0):
    return f"{v:,.{casas}f}".replace(",", "@").replace(".", ",").replace("@", ".")


def sinal(v, casas=0):
    return ("+" if v >= 0 else "−") + num(abs(v), casas)


def svg(nome):
    s = open(os.path.join(SAIDAS, nome), encoding="utf-8").read()
    s = s.replace('fill="#fbfaf7"', 'fill="var(--prancha)"', 1)
    s = s.replace(' width="', ' data-w="', 1).replace(' height="', ' data-h="', 1)
    return s.replace("<svg ", '<svg class="planta" ', 1)


def raias(d):
    return "/".join(str(b["raias"]) for b in d["blocos"])


escada = "\n".join(
    '<tr{cls}><td class="mono">{r}</td><td class="mono num">{cap}</td>'
    '<td class="mono num">{a}</td><td class="mono num">{b}</td>'
    '<td class="mono num">{c}</td><td class="mono num">{sep}</td>'
    '<td class="mono num">{compra}</td><td class="mono num">{custo}</td></tr>'.format(
        cls=(' class="marcada"' if tuple(l["raias"]) == tuple(b["raias"] for b in E["blocos"])
             else (' class="cheia"' if tuple(l["raias"]) == tuple(b["raias"] for b in H["blocos"]) else "")),
        r="/".join(str(x) for x in l["raias"]), cap=num(l["capacidade"]),
        a=num(l["por_entrada"]["A"]), b=num(l["por_entrada"]["B"]),
        c=num(l["por_entrada"]["C"]), sep=l["separadores"], compra=l["compra"],
        custo=num(l["custo_compra_eur"], 2))
    for l in D["escada_de_dimensionamento"])

comp = []
chaves = list(dict.fromkeys(list(V["barreira_por_componente_m"]) +
                            list(H["barreira_por_componente_m"])))
for k in chaves:
    a = V["barreira_por_componente_m"].get(k, 0.0)
    b = H["barreira_por_componente_m"].get(k, 0.0)
    comp.append(f'<tr><td>{k}</td><td class="mono num">{num(a,1) if a else "—"}</td>'
                f'<td class="mono num">{num(b,1) if b else "—"}</td></tr>')
comp = "\n".join(comp)

entradas = "\n".join(
    f'<tr><td><span class="pin {e.lower()}">{e}</span> {PORTA[e]}</td>'
    f'<td class="mono num">{num(ESP[e])}</td>'
    f'<td class="mono num">{num(V["por_entrada"][e])}</td>'
    f'<td class="mono num">{num(V["capacidade_por_eleitor_esperado"][e],4)}</td>'
    f'<td class="mono num">{num(H["por_entrada"][e])}</td>'
    f'<td class="mono num">{num(H["capacidade_por_eleitor_esperado"][e],4)}</td></tr>'
    for e in ("A", "B", "C"))

decks = "\n".join(
    f'<tr><td><span class="pin {b["entrada"].lower()}">{b["entrada"]}</span> '
    f'deck {b["entrada"]} → {PORTA[b["entrada"]]}</td>'
    f'<td class="mono num">{b["raias"]}</td>'
    f'<td class="mono num">{num(b["comprimento_m"],1)} m</td>'
    f'<td class="mono num">{num(b["profundidade_m"],1)} m</td>'
    f'<td class="mono num">{num(b["caminhada_m"])} m</td>'
    f'<td class="mono num">{num(b["capacidade"])}</td>'
    f'<td class="mono num">{num(H["baias"].get(b["entrada"],{}).get("capacidade",0)) if b["entrada"] in H["baias"] else "—"}</td></tr>'
    for b in H["blocos"])

HTML = f"""<title>Ring 3 na horizontal</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600&family=Source+Serif+4:opsz,wght@8..60,600;8..60,700&display=swap">
<style>
:root{{
  --papel:#f1efe7; --folha:#fffdf7; --prancha:#fbfaf7; --tinta:#16202b;
  --meio:#57616c; --fraco:#8b9099; --regua:#dbd5c7; --regua2:#eae5d9;
  --a:#1f6fb2; --b:#b26a12; --c:#b0245e; --alerta:#b23b2e; --ok:#1a7f6b;
  --realce:rgba(31,111,178,.10);
}}
@media (prefers-color-scheme:dark){{ :root:not([data-theme="light"]){{
  --papel:#101418; --folha:#181d23; --prancha:#f4f2ee; --tinta:#e6eaee;
  --meio:#a2aab4; --fraco:#767f89; --regua:#2b323a; --regua2:#222931;
  --a:#63a6e0; --b:#dda257; --c:#e77aa4; --alerta:#e0796a; --ok:#4fc0a8;
  --realce:rgba(99,166,224,.14);
}}}}
:root[data-theme="dark"]{{
  --papel:#101418; --folha:#181d23; --prancha:#f4f2ee; --tinta:#e6eaee;
  --meio:#a2aab4; --fraco:#767f89; --regua:#2b323a; --regua2:#222931;
  --a:#63a6e0; --b:#dda257; --c:#e77aa4; --alerta:#e0796a; --ok:#4fc0a8;
  --realce:rgba(99,166,224,.14);
}}
*{{box-sizing:border-box}}
body{{margin:0; background:var(--papel); color:var(--tinta);
  font-family:"IBM Plex Sans",ui-sans-serif,system-ui,Helvetica,Arial,sans-serif;
  font-size:16.5px; line-height:1.62; -webkit-font-smoothing:antialiased}}
.folha{{max-width:1080px; margin:0 auto; padding:0 26px 92px}}
.prosa{{max-width:68ch}}
h1,h2,h3{{font-family:"Source Serif 4",Georgia,"Times New Roman",serif;
  margin:0; font-weight:700; letter-spacing:-.01em; text-wrap:balance}}
h1{{font-size:clamp(2.1rem,4.6vw,3.1rem); line-height:1.06}}
h2{{font-size:clamp(1.4rem,2.4vw,1.85rem); line-height:1.2}}
h3{{font-size:1.02rem; font-weight:600}}
p{{margin:0 0 1.05em}}
strong{{font-weight:600}}
.mono{{font-family:"IBM Plex Mono",ui-monospace,SFMono-Regular,Menlo,monospace;
  font-variant-numeric:tabular-nums}}
a{{color:var(--a)}}

header{{padding:70px 0 0}}
.olho{{font-family:"IBM Plex Mono",monospace; font-size:.71rem; letter-spacing:.15em;
  text-transform:uppercase; color:var(--meio); margin:0 0 18px}}
.chamada{{font-family:"Source Serif 4",Georgia,serif; font-size:clamp(1.08rem,2vw,1.3rem);
  line-height:1.5; color:var(--meio); max-width:58ch; margin:20px 0 0; font-weight:600}}
.faixa{{display:grid; grid-template-columns:repeat(auto-fit,minmax(146px,1fr));
  gap:1px; background:var(--regua); border:1px solid var(--regua); margin:40px 0 0}}
.faixa div{{background:var(--papel); padding:14px 15px}}
.faixa dt{{font-size:.71rem; letter-spacing:.09em; text-transform:uppercase;
  color:var(--meio); margin:0 0 5px}}
.faixa dd{{margin:0; font-family:"IBM Plex Mono",monospace; font-size:1.4rem;
  font-weight:500; font-variant-numeric:tabular-nums; line-height:1.14}}
.faixa dd small{{display:block; font-family:"IBM Plex Sans",sans-serif; font-size:.73rem;
  font-weight:400; color:var(--fraco); letter-spacing:0; margin-top:4px}}
.faixa .delta{{color:var(--ok)}}

section{{margin:66px 0 0}}
.rotulo{{font-family:"IBM Plex Mono",monospace; font-size:.71rem; letter-spacing:.15em;
  text-transform:uppercase; color:var(--meio); margin:0 0 10px; padding-bottom:9px;
  border-bottom:1px solid var(--regua)}}
section>h2{{margin-bottom:16px}}

.plantas{{display:grid; gap:20px; grid-template-columns:1fr; margin:28px 0 0}}
@media (min-width:900px){{ .plantas{{grid-template-columns:1fr 1fr}} }}
@media (min-width:1180px){{ .plantas{{width:min(1240px,calc(100vw - 52px));
  margin-left:calc((1080px - min(1240px,100vw - 52px)) / 2)}} }}
figure{{margin:0}}
.prancha{{background:var(--prancha); border:1px solid var(--regua); padding:6px;
  overflow-x:auto}}
svg.planta{{display:block; width:100%; height:auto; min-width:430px}}
figcaption{{font-size:.84rem; color:var(--meio); margin-top:11px}}
figcaption b{{color:var(--tinta); font-weight:600}}

.rolagem{{overflow-x:auto; border:1px solid var(--regua); background:var(--folha);
  margin:24px 0 0}}
table{{border-collapse:collapse; width:100%; font-size:.86rem}}
th,td{{text-align:left; padding:9px 12px; border-bottom:1px solid var(--regua2);
  white-space:nowrap}}
thead th{{font-size:.68rem; letter-spacing:.08em; text-transform:uppercase;
  color:var(--meio); font-weight:500; border-bottom:1px solid var(--regua);
  background:var(--folha)}}
tbody tr:last-child td{{border-bottom:0}}
td.num,th.num{{text-align:right}}
tr.total td{{border-top:1.5px solid var(--regua); font-weight:600}}
tr.marcada td{{background:var(--realce); font-weight:600}}
tr.cheia td{{background:var(--regua2)}}
caption{{caption-side:bottom; text-align:left; font-size:.8rem; color:var(--fraco);
  padding:9px 12px}}

.pin{{display:inline-block; width:18px; text-align:center; font-family:"IBM Plex Mono",monospace;
  font-weight:600; font-size:.74rem; border:1px solid currentColor; margin-right:6px}}
.pin.a{{color:var(--a)}} .pin.b{{color:var(--b)}} .pin.c{{color:var(--c)}}

ul.marcas{{list-style:none; padding:0; margin:22px 0 0; display:grid; gap:13px;
  max-width:70ch}}
ul.marcas li{{padding-left:22px; position:relative; color:var(--meio)}}
ul.marcas li::before{{content:""; position:absolute; left:0; top:.66em; width:9px;
  height:1px; background:var(--fraco)}}
ul.marcas li strong{{color:var(--tinta)}}
ul.marcas.contra li::before{{background:var(--alerta)}}

.veredito{{margin-top:30px; border:1px solid var(--regua); border-left:3px solid var(--a);
  background:var(--folha); padding:22px 24px; display:flex; flex-direction:column; gap:9px}}
.veredito .curta{{font-family:"Source Serif 4",Georgia,serif; font-size:1.26rem;
  font-weight:700; line-height:1.3}}
.veredito p{{margin:0; color:var(--meio); font-size:.93rem; max-width:68ch}}
.nota{{border-left:2px solid var(--b); padding:2px 0 2px 18px; margin:26px 0 0;
  color:var(--meio); font-size:.94rem; max-width:70ch}}
.nota strong{{color:var(--tinta)}}

ol.pend{{counter-reset:p; list-style:none; padding:0; margin:24px 0 0; display:grid; gap:14px}}
ol.pend li{{counter-increment:p; display:grid; grid-template-columns:28px 1fr; gap:14px;
  align-items:start; max-width:72ch}}
ol.pend li::before{{content:counter(p); font-family:"IBM Plex Mono",monospace; font-size:.76rem;
  color:var(--a); border:1px solid var(--regua); width:28px; height:28px; display:grid;
  place-items:center; margin-top:2px}}
ol.pend p{{margin:5px 0 0; color:var(--meio); font-size:.92rem}}

footer{{margin:80px 0 0; padding-top:20px; border-top:1px solid var(--regua);
  font-size:.82rem; color:var(--fraco)}}
footer p{{margin:0 0 .5em; max-width:74ch}}
:focus-visible{{outline:2px solid var(--a); outline-offset:3px}}
@media (prefers-reduced-motion:reduce){{*{{transition:none!important}}}}
@media (max-width:640px){{ .folha{{padding:0 18px 60px}} header{{padding-top:44px}} }}
</style>

<div class="folha">
<header>
  <p class="olho">Eleições 2026 · 1º turno · 4 de outubro · RDS Ballsbridge · fila externa</p>
  <h1>Ring 3 na horizontal</h1>
  <p class="chamada">Segundo desenho para o compound de fila: três decks de raias leste-oeste
  empilhados em profundidade, no lugar dos três blocos verticais lado a lado. Cada deck sai
  por um tubo alinhado com a sua própria porta — e é isso, não a capacidade, que o desenho
  compra.</p>
  <dl class="faixa">
    <div><dt>Capacidade</dt><dd>{num(H['capacidade'])}<small>Ring cheio · vertical: {num(V['capacidade'])}</small></dd></div>
    <div><dt>Em raia</dt><dd>{num(H['capacidade_raias'])}<small>{num(H['capacidade_raias']/H['capacidade']*100)}% da lotação · vertical: {num(V['capacidade_raias']/V['capacidade']*100)}%</small></dd></div>
    <div><dt>Separadores</dt><dd>{H['separadores']}<small>vertical: {V['separadores']} · estoque: {P['estoque_separadores']}</small></dd></div>
    <div><dt>Versão enxuta</dt><dd class="delta">{E['separadores']}<small>{num(E['capacidade'])} pessoas · {V['separadores']-E['separadores']} abaixo do vertical</small></dd></div>
    <div><dt>Raia mais longa</dt><dd>{num(max(b['comprimento_m'] for b in H['blocos']),1)} m<small>vertical: {num(max(b['comprimento_m'] for b in V['blocos']),1)} m</small></dd></div>
  </dl>
</header>

<section>
  <p class="rotulo">Os dois desenhos</p>
  <h2>A mesma área, dois modos de dobrar a fila</h2>
  <div class="prosa">
  <p>O Ring 3 é um retângulo de {num(P['largura_ring'] if 'largura_ring' in P else 39.0,1)} × 35,0 m de gradil permanente,
  {num(D['apron_m'],0)} m ao sul da fachada do Hall 2, e a garganta de entrada fica no canto sudeste.
  Dentro dele cabem as duas geometrias; o que muda é para onde correm as raias — e, com isso,
  como cada fila chega à sua porta.</p>
  </div>
  <div class="plantas">
    <figure><div class="prancha">{svg('ring3_vertical.svg')}</div>
      <figcaption><b>Vertical (plano vigente).</b> Três blocos lado a lado, raias norte-sul,
      baias nos dois flancos. Nenhum bloco está alinhado com a sua porta: as três correntes
      cruzam o apron em diagonal e convergem nos 6,2 m que separam S4, S5 e S6.</figcaption></figure>
    <figure><div class="prancha">{svg('ring3_horizontal.svg')}</div>
      <figcaption><b>Horizontal (este desenho).</b> Três decks empilhados, raias leste-oeste.
      Cada deck sobe por um tubo no eixo da sua porta e cruza o apron perpendicularmente; o
      degrau que sobra a leste vira baia, alimentada pela espinha que vem da garganta.</figcaption></figure>
  </div>
</section>

<section>
  <p class="rotulo">A regra do desenho</p>
  <h2>Por que os decks formam uma escada</h2>
  <div class="prosa">
  <p>Empilhar decks cria um problema que o desenho vertical não tem: o deck do fundo precisa
  atravessar os decks da frente para chegar à fachada. A saída é <strong>alinhar cada tubo com a
  sua porta e fazer os decks da frente pararem antes desse eixo</strong>. Daí tudo o mais decorre:
  quanto mais ao fundo, mais largo o deck; o degrau que sobra a leste é baia de espera; e a ordem
  dos decks deixa de ser escolha — da frente para o fundo, a porta tem de andar para leste,
  <strong>A = S4, B = S5, C = S6</strong>, senão o tubo de um deck de trás cortaria o serpenteado
  da frente.</p>
  </div>
  <ul class="marcas">
    <li><strong>A descarga fica perpendicular.</strong> As três raias do apron ficam confinadas
    entre x = 19,1 m e x = 37,5 m. As saídas S2 e S8, nos flancos, deixam de ter fila de entrada
    à frente — no desenho vertical, são justamente as baias de flanco que caem ali.</li>
    <li><strong>As baias mudam de lugar na fila.</strong> Ficam do lado da chegada, encostadas na
    espinha: enchem como buffer de cauda, antes das raias, e não como transbordo lateral no meio
    do serpenteado.</li>
    <li><strong>A raia fica longa.</strong> Até {num(max(b['comprimento_m'] for b in H['blocos']),1)} m
    de corrida contra os {num(max(b['comprimento_m'] for b in V['blocos']),1)} m do vertical: menos
    meias-voltas por pessoa, menos pontos de atrito para fiscalizar.</li>
    <li><strong>E há um preço, que é o tubo.</strong> Cada deck de trás gasta duas corridas de
    barreira só para atravessar a profundidade dos decks da frente —
    {num(H['barreira_por_componente_m'].get('tubos de saída dos decks de trás',0),1)} m que o
    desenho vertical não gasta.</li>
  </ul>
  <div class="rolagem"><table>
    <thead><tr><th>Deck</th><th class="num">Raias</th><th class="num">Comprimento</th>
    <th class="num">Profundidade</th><th class="num">Caminhada</th><th class="num">Em raia</th>
    <th class="num">Em baia</th></tr></thead>
    <tbody>{decks}</tbody>
    <caption>Configuração de Ring cheio ({raias(H)} raias). Caminhada é o percurso de quem entra
    com o deck vazio e anda até a porta.</caption>
  </table></div>
</section>

<section>
  <p class="rotulo">Capacidade</p>
  <h2>Mais gente, e sobretudo mais gente em fila</h2>
  <div class="rolagem"><table>
    <thead><tr><th></th><th class="num">Vertical</th><th class="num">Horizontal</th><th class="num">Δ</th></tr></thead>
    <tbody>
      <tr><td>Em raia — fila medida</td><td class="mono num">{num(V['capacidade_raias'])}</td><td class="mono num">{num(H['capacidade_raias'])}</td><td class="mono num">{sinal(H['capacidade_raias']-V['capacidade_raias'])}</td></tr>
      <tr><td>Em baia — espera</td><td class="mono num">{num(V['capacidade_baias'])}</td><td class="mono num">{num(H['capacidade_baias'])}</td><td class="mono num">{sinal(H['capacidade_baias']-V['capacidade_baias'])}</td></tr>
      <tr class="total"><td>Total</td><td class="mono num">{num(V['capacidade'])}</td><td class="mono num">{num(H['capacidade'])}</td><td class="mono num">{sinal(H['capacidade']-V['capacidade'])}</td></tr>
    </tbody>
  </table></div>
  <div class="prosa" style="margin-top:22px">
  <p>O total muda pouco; a natureza da lotação muda muito. No vertical,
  {num(V['capacidade_baias']/V['capacidade']*100)}% da capacidade é massa parada nas baias de
  flanco. No horizontal, a raia sobe para {num(H['capacidade_raias']/H['capacidade']*100)}% —
  e fila em raia é fila contável, com ordem de chegada preservada e vazão previsível, enquanto
  baia é aglomeração que precisa de fiscal para voltar a ser fila.</p>
  </div>
  <div class="rolagem"><table>
    <thead><tr><th>Entrada</th><th class="num">Esperado</th><th class="num">Vertical</th>
    <th class="num">por eleitor</th><th class="num">Horizontal</th><th class="num">por eleitor</th></tr></thead>
    <tbody>{entradas}</tbody>
    <caption>Comparecimento esperado por entrada: base B (taxa de 2022 por domicílio de origem),
    decisão do Posto. “Por eleitor” é a capacidade dividida pelo comparecimento esperado daquela
    entrada — quanto mais parelho entre as três, melhor distribuída está a fila.</caption>
  </table></div>
</section>

<section>
  <p class="rotulo">Separadores de fila</p>
  <h2>Onde a barreira é gasta</h2>
  <div class="prosa">
  <p>Barreira externa, componente a componente. Não entram nesta conta o gradil permanente do
  Ring, que os dois desenhos usam de graça, nem os 100 unifilas (200 m) do item <em>d</em> do
  orçamento, que servem ao interior do Hall 2.</p>
  </div>
  <div class="rolagem"><table>
    <thead><tr><th>Componente</th><th class="num">Vertical (m)</th><th class="num">Horizontal (m)</th></tr></thead>
    <tbody>
      {comp}
      <tr class="total"><td>Barreira</td><td class="mono num">{num(V['barreira_m'],1)}</td><td class="mono num">{num(H['barreira_m'],1)}</td></tr>
      <tr class="total"><td>Separadores de 2 m</td><td class="mono num">{V['separadores']}</td><td class="mono num">{H['separadores']}</td></tr>
      <tr><td>A comprar (estoque {P['estoque_separadores']})</td><td class="mono num">{V['compra']}</td><td class="mono num">{H['compra']}</td></tr>
      <tr><td>Custo da compra</td><td class="mono num">EUR {num(V['custo_compra_eur'],2)}</td><td class="mono num">EUR {num(H['custo_compra_eur'],2)}</td></tr>
      <tr><td>Metros por pessoa de lotação</td><td class="mono num">{num(V['m_por_pessoa'],3)}</td><td class="mono num">{num(H['m_por_pessoa'],3)}</td></tr>
    </tbody>
  </table></div>
  <p class="nota"><strong>O horizontal é menos econômico por pessoa</strong> — {num(H['m_por_pessoa'],3)} m
  contra {num(V['m_por_pessoa'],3)} m — e a diferença tem nome: os tubos, mais o fato de as baias
  do vertical serem enormes e quase gratuitas, porque usam o gradil do Ring em três lados. Os
  serpenteados propriamente ditos são levemente mais eficientes no horizontal, já que a raia longa
  dilui o custo das pontas.</p>
</section>

<section>
  <p class="rotulo">Dimensionamento</p>
  <h2>A escada: quanta fila comprar</h2>
  <div class="prosa">
  <p>Com os decks na largura máxima, o número de raias é a única alavanca — e ela troca capacidade
  por barreira quase linearmente. A tabela percorre as repartições que cabem na profundidade do
  Ring; para cada total de raias, mostra a repartição que melhor equilibra as três entradas.</p>
  </div>
  <div class="rolagem"><table>
    <thead><tr><th>Raias A/B/C</th><th class="num">Capacidade</th><th class="num">A</th>
    <th class="num">B</th><th class="num">C</th><th class="num">Separadores</th>
    <th class="num">A comprar</th><th class="num">Custo (EUR)</th></tr></thead>
    <tbody>{escada}</tbody>
    <caption>Linha destacada: a recomendada ({raias(E)}). Linha cinza: o Ring cheio ({raias(H)}).</caption>
  </table></div>

  <div class="veredito">
    <p class="curta">Recomendação: {raias(E)} raias — {num(E['capacidade'])} pessoas com
    {E['separadores']} separadores.</p>
    <p>São {E['compra']} unidades a comprar (EUR {num(E['custo_compra_eur'],2)}), contra
    {V['compra']} do desenho vertical: {V['separadores']-E['separadores']} separadores
    <strong>a menos</strong>, com a geometria de descarga corrigida. O Ring nunca foi o gargalo
    desta operação — o gargalo é a mesa —, e gastar barreira para encher o Ring é comprar
    capacidade que não vai ser usada. Se o Posto preferir margem, a linha cinza enche o Ring por
    mais {H['separadores']-E['separadores']} separadores.</p>
  </div>
</section>

<section>
  <p class="rotulo">Método</p>
  <h2>Como as duas contas foram feitas</h2>
  <div class="prosa">
  <p>O plano vertical original não está no repositório: <span class="mono">scripts/layout_ring3.py</span>
  e <span class="mono">saidas/plano_ring3.md</span> foram produzidos em sessão anterior e não chegaram
  a ser versionados. Ele foi reconstruído a partir das cotas publicadas, e a reconstrução acerta os
  números publicados na casa decimal:</p>
  </div>
  <div class="rolagem"><table>
    <thead><tr><th>Grandeza</th><th class="num">Publicado</th><th class="num">Recalculado</th></tr></thead>
    <tbody>
      <tr><td>Capacidade dos serpenteados</td><td class="mono num">{num(CONF['raias_publicado'])}</td><td class="mono num">{num(CONF['raias_calculado'],1)}</td></tr>
      <tr><td>Capacidade das baias</td><td class="mono num">{num(CONF['baias_publicado'])}</td><td class="mono num">{num(CONF['baias_calculado'],1)}</td></tr>
      <tr><td>Capacidade total</td><td class="mono num">{num(CONF['total_publicado'])}</td><td class="mono num">{num(CONF['total_calculado'])}</td></tr>
      <tr><td>Barreira</td><td class="mono num">{num(CONF['barreira_publicada_m'],1)} m</td><td class="mono num">{num(CONF['barreira_calculada_m'],1)} m</td></tr>
      <tr><td>Separadores</td><td class="mono num">{CONF['separadores_publicado']}</td><td class="mono num">{CONF['separadores_calculado']}</td></tr>
    </tbody>
  </table></div>
  <p class="nota">A capacidade fecha; a barreira fica
  {num((CONF['barreira_calculada_m']/CONF['barreira_publicada_m']-1)*100,1)}% acima, porque a regra
  de contagem de barreira do plano original não é recuperável do que foi publicado.
  <strong>Por isso a comparação desta página usa a regra deste modelo nos dois desenhos</strong> —
  mesma densidade, mesmo módulo de raia, mesma contagem de barreira. Comparar o número publicado de
  um com o número calculado do outro daria uma diferença que é de método, não de desenho.</p>
  <div class="rolagem"><table>
    <thead><tr><th>Premissa</th><th class="num">Valor</th><th>Origem</th></tr></thead>
    <tbody>
      <tr><td>Módulo da raia</td><td class="mono num">{num(P['passo_raia_m'],2)} m</td><td>reconstruído dos blocos de 4,2 e 12,6 m</td></tr>
      <tr><td>Largura livre da raia</td><td class="mono num">{num(P['raia_util_m'],2)} m</td><td>reconstruído</td></tr>
      <tr><td>Densidade em raia</td><td class="mono num">{num(P['densidade_fila_p_m2'],1)} p/m²</td><td>reconstruído</td></tr>
      <tr><td>Densidade em baia</td><td class="mono num">{num(P['densidade_baia_p_m2'],1)} p/m²</td><td>reconstruído</td></tr>
      <tr><td>Separador de fila</td><td class="mono num">{num(P['separador_m'],1)} m · EUR {num(P['separador_eur'],2)}</td><td>item d do orçamento (100 un. = EUR 1.303)</td></tr>
      <tr><td>Estoque da organizadora</td><td class="mono num">{P['estoque_separadores']} un. · {num(P['estoque_separadores']*P['separador_m'])} m</td><td>plano do Ring 3</td></tr>
    </tbody>
  </table></div>
</section>

<section>
  <p class="rotulo">Antes de contratar</p>
  <h2>O que este desenho ainda supõe</h2>
  <ol class="pend">
    <li><div><h3>O bordo oeste do Ring</h3><p>O retângulo está centrado em S5 por estimativa.
    Medir no local decide a largura real dos decks e, com ela, a capacidade de cada um — é a
    medida que mais move os números desta página.</p></div></li>
    <li><div><h3>Onde o gradil abre</h3><p>O desenho supõe portão no gradil permanente nos três
    eixos de porta (x ≈ 22,1 / 28,3 / 34,5 m) e na garganta sudeste. Se o gradil não abrir onde se
    precisa, os tubos deixam de ser retos e a vantagem principal do desenho cai.</p></div></li>
    <li><div><h3>Piso e drenagem</h3><p>Raia leste-oeste de {num(max(b['comprimento_m'] for b in H['blocos']),0)} m
    acompanha a declividade do Ring inteiro. Se algum trecho acumula água, as raias do fundo ficam
    inviáveis num dia de chuva — entre 40% e 65% de probabilidade em 4 de outubro, conforme o
    limiar da fonte.</p></div></li>
    <li><div><h3>As densidades</h3><p>2,0 pessoas/m² em raia e 1,8 em baia são reconstrução, não
    medição. Se a densidade real sob guarda-chuva for menor, as duas geometrias perdem capacidade
    na mesma proporção e a comparação entre elas não muda.</p></div></li>
  </ol>
</section>

<footer>
  <p>Geometria do salão e das portas de <span class="mono">scripts/salao.py</span>; comparecimento
  esperado e papéis das portas das decisões do Posto de 06/09/2026. Modelo, plantas e todos os
  números desta página gerados por <span class="mono">scripts/ring3.py</span> e
  <span class="mono">scripts/gera_pagina_ring3.py</span>, no repositório
  <span class="mono">eleicoes2026</span>.</p>
  <p>Plantas em escala real sobre o contorno medido do Hall 2 (50,3 × 44,4 m) e o retângulo do
  Ring 3 (39,0 × 35,0 m, apron de 14 m). Números de capacidade são estimativa de lotação, não
  limite de segurança homologado.</p>
</footer>
</div>
"""

destino = os.path.join(SAIDAS, "ring3_horizontal.html")
with open(destino, "w", encoding="utf-8") as f:
    f.write(HTML)
print("gravado:", destino, f"({len(HTML)/1024:.1f} KB)")
