#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Monta a pagina do Ring 3 girado a partir de saidas/ring3.json.

Todo numero da pagina vem do JSON que scripts/ring3.py gerou: a pagina nao
guarda nenhuma conta propria. Saida: saidas/ring3_horizontal.html
"""

import json
import math
import os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAIDAS = os.path.join(RAIZ, "saidas")

D = json.load(open(os.path.join(SAIDAS, "ring3.json"), encoding="utf-8"))
V, H, HB = D["vigente"], D["girado"], D["girado_com_baias"]
ESCADA = D["escada_de_raias"]
P, CONF = D["premissas"], D["aderencia_ao_plano_original"]
ESP = P["comparecimento_esperado"]
PORTA = {"A": "S4", "B": "S5", "C": "S6"}
ENTRADAS = ("A", "B", "C")


def num(v, casas=0):
    return f"{v:,.{casas}f}".replace(",", "@").replace(".", ",").replace("@", ".")


def sinal(v, casas=0):
    return ("+" if v >= 0 else "−") + num(abs(v), casas)


def zona(d, e):
    return next(z for z in d["zonas"] if z["entrada"] == e)


def svg(nome):
    s = open(os.path.join(SAIDAS, nome), encoding="utf-8").read()
    s = s.replace('fill="#fbfaf7"', 'fill="var(--prancha)"', 1)
    s = s.replace(' width="', ' data-w="', 1).replace(' height="', ' data-h="', 1)
    return s.replace("<svg ", '<svg class="planta" ', 1)


raia_curta = lambda d: min(z["comprimento_raia_m"] for z in d["zonas"])
fixa = H["barreira_m"] - sum(
    2 * z["comprimento_raia_m"] + (z["raias"] - 1) *
    max(0.0, z["comprimento_raia_m"] - P["vao_retorno_m"]) for z in H["zonas"])

zonas_tab = "\n".join(
    f'<tr><td><span class="pin {z["entrada"].lower()}">{z["entrada"]}</span> '
    f'{PORTA[z["entrada"]]}</td>'
    f'<td class="mono num">{num(z["comprimento_raia_m"],2)} m</td>'
    f'<td class="mono num">{z["raias"]}</td>'
    f'<td class="mono num">{num(z["profundidade_m"],2)} m</td>'
    f'<td class="mono num">{num(z["caminhada_m"])} m</td>'
    f'<td class="mono num">{num(z["capacidade"])}</td>'
    f'<td class="mono num">{num(ESP[z["entrada"]])}</td>'
    f'<td class="mono num">{num(H["capacidade_por_eleitor_esperado"][z["entrada"]],4)}</td>'
    f'</tr>' for z in H["zonas"])

descarga_tab = "\n".join(
    f'<tr><td><span class="pin {e.lower()}">{e}</span> {PORTA[e]}</td>'
    f'<td class="mono num">{num(zona(V,e)["desvio_lateral_m"],2)} m</td>'
    f'<td class="mono num{" ganho" if zona(H,e)["desvio_lateral_m"] < zona(V,e)["desvio_lateral_m"] else ""}">'
    f'{num(zona(H,e)["desvio_lateral_m"],2)} m</td></tr>' for e in ENTRADAS)

comp = []
chaves = list(dict.fromkeys(list(V["barreira_por_componente_m"]) +
                            list(H["barreira_por_componente_m"])))
for k in chaves:
    a = V["barreira_por_componente_m"].get(k, 0.0)
    b = H["barreira_por_componente_m"].get(k, 0.0)
    d = b - a
    cls = " ganho" if d < -0.05 else (" perda" if d > 0.05 else "")
    comp.append(f'<tr><td>{k}</td>'
                f'<td class="mono num">{num(a,1) if a else "—"}</td>'
                f'<td class="mono num">{num(b,1) if b else "—"}</td>'
                f'<td class="mono num{cls}">{sinal(d,1) if abs(d) > 0.05 else "—"}</td></tr>')
comp = "\n".join(comp)

escada_tab = "\n".join(
    '<tr{cls}><td class="mono num">{r}</td><td class="mono num">{prof} m</td>'
    '<td class="mono num">{cap}</td><td class="mono num">{a}</td>'
    '<td class="mono num">{b}</td><td class="mono num">{c}</td>'
    '<td class="mono num">{sep}</td><td class="mono num">{compra}</td>'
    '<td class="mono num">{custo}</td></tr>'.format(
        cls=' class="marcada"' if l["raias_por_zona"] == H["zonas"][0]["raias"] else "",
        r=l["raias_por_zona"], prof=num(l["profundidade_m"], 1),
        cap=num(l["capacidade"]), a=num(l["por_entrada"]["A"]),
        b=num(l["por_entrada"]["B"]), c=num(l["por_entrada"]["C"]),
        sep=l["separadores"], compra=l["compra"],
        custo="EUR " + num(l["custo_compra_eur"], 2))
    for l in ESCADA + [{"raias_por_zona": H["zonas"][0]["raias"],
                        "profundidade_m": H["zonas"][0]["profundidade_m"],
                        "capacidade": H["capacidade"],
                        "por_entrada": H["por_entrada"],
                        "separadores": H["separadores"], "compra": H["compra"],
                        "custo_compra_eur": H["custo_compra_eur"]}])

cabe_v = [l for l in ESCADA if l["separadores"] <= V["separadores"]]

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
td.ganho{{color:var(--ok); font-weight:600}}
td.perda{{color:var(--alerta); font-weight:600}}
.faixa dd.alerta{{color:var(--alerta)}}
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
  <p class="chamada">As raias giram para leste-oeste e as baias de flanco viram serpenteado. As três
  zonas passam a ocupar a largura toda do Ring, com largura proporcional à fila que cada uma
  espera — e nesta geometria largura de zona é comprimento de raia.</p>
  <dl class="faixa">
    <div><dt>Lotação</dt><dd>{num(H['capacidade'])}<small>toda em raia medida · vigente: {num(V['capacidade'])}, {num(V['capacidade_raias'])} em raia</small></dd></div>
    <div><dt>Raia mais curta</dt><dd class="delta">{num(raia_curta(H),1)} m<small>vigente: {num(raia_curta(V),1)} m · só girando: {num(raia_curta(HB),1)} m</small></dd></div>
    <div><dt>Separadores</dt><dd>{H['separadores']}<small>vigente: {V['separadores']}</small></dd></div>
    <div><dt>A comprar</dt><dd class="alerta">{H['compra']}<small>sobre os {P['estoque_separadores']} da organizadora · vigente: {V['compra']}</small></dd></div>
    <div><dt>Custo da compra</dt><dd>EUR {num(H['custo_compra_eur'],0)}<small>vigente: EUR {num(V['custo_compra_eur'],0)}</small></dd></div>
  </dl>
</header>

<section>
  <p class="rotulo">O que muda</p>
  <h2>Menos gente no Ring, e toda ela em fila</h2>
  <div class="prosa">
  <p>O plano vigente guarda {num(V['capacidade_baias'])} pessoas — {num(V['capacidade_baias']/V['capacidade']*100,0)}%
  da lotação — em duas baias de espera nos flancos. Baia é aglomeração: não tem ordem de chegada,
  não tem vazão previsível, e precisa de fiscal para virar fila outra vez. Preenchendo os flancos
  com serpenteado, a lotação cai {num(abs(H['capacidade']-V['capacidade']))} pessoas
  ({num(abs(H['capacidade']/V['capacidade']-1)*100,1)}%) e a <strong>fila medida sobe
  {num((H['capacidade_raias']/V['capacidade_raias']-1)*100,0)}%</strong>.</p>
  </div>
  <div class="rolagem"><table>
    <thead><tr><th></th><th class="num">Plano vigente</th><th class="num">Este desenho</th><th class="num">Δ</th></tr></thead>
    <tbody>
      <tr><td>Lotação total</td><td class="mono num">{num(V['capacidade'])}</td><td class="mono num">{num(H['capacidade'])}</td><td class="mono num">{sinal(H['capacidade']-V['capacidade'])}</td></tr>
      <tr class="total"><td>… em raia medida</td><td class="mono num">{num(V['capacidade_raias'])}</td><td class="mono num">{num(H['capacidade_raias'])}</td><td class="mono num ganho">{sinal(H['capacidade_raias']-V['capacidade_raias'])}</td></tr>
      <tr><td>… em baia de espera</td><td class="mono num">{num(V['capacidade_baias'])}</td><td class="mono num">0</td><td class="mono num">{sinal(-V['capacidade_baias'])}</td></tr>
      <tr><td>Raia mais curta</td><td class="mono num">{num(raia_curta(V),1)} m</td><td class="mono num">{num(raia_curta(H),1)} m</td><td class="mono num">{sinal(raia_curta(H)-raia_curta(V),1)} m</td></tr>
      <tr><td>Meias-voltas</td><td class="mono num">{V['meias_voltas']}</td><td class="mono num">{H['meias_voltas']}</td><td class="mono num">{sinal(H['meias_voltas']-V['meias_voltas'])}</td></tr>
      <tr><td>Barreira</td><td class="mono num">{num(V['barreira_m'],1)} m</td><td class="mono num">{num(H['barreira_m'],1)} m</td><td class="mono num perda">{sinal(H['barreira_m']-V['barreira_m'],1)} m</td></tr>
      <tr class="total"><td>Separadores de 2 m</td><td class="mono num">{V['separadores']}</td><td class="mono num">{H['separadores']}</td><td class="mono num perda">{sinal(H['separadores']-V['separadores'])}</td></tr>
      <tr><td>A comprar (estoque {P['estoque_separadores']})</td><td class="mono num">{V['compra']}</td><td class="mono num">{H['compra']}</td><td class="mono num perda">{sinal(H['compra']-V['compra'])}</td></tr>
      <tr><td>Custo da compra</td><td class="mono num">EUR {num(V['custo_compra_eur'],2)}</td><td class="mono num">EUR {num(H['custo_compra_eur'],2)}</td><td class="mono num perda">EUR {sinal(H['custo_compra_eur']-V['custo_compra_eur'],2)}</td></tr>
    </tbody>
    <caption>Os dois desenhos medidos com o mesmo modelo — mesma densidade, mesmo módulo de raia,
    mesma regra de barreira.</caption>
  </table></div>
  <p class="nota"><strong>O preço está na barreira.</strong> A lotação que o plano vigente ganha de
  graça nas baias — que usam o gradil do Ring em três lados e não gastam divisória nenhuma — passa a
  ser paga em separador. Faltam <strong>{H['compra']} unidades</strong> sobre as
  {P['estoque_separadores']} da organizadora, contra as {V['compra']} que o plano vigente já
  precisava comprar: {H['compra']-V['compra']} a mais, EUR {num(H['custo_compra_eur']-V['custo_compra_eur'],2)}.</p>
</section>

<section>
  <p class="rotulo">Os dois desenhos</p>
  <h2>O gradil está no mesmo lugar</h2>
  <div class="prosa">
  <p>Corredor de fundo ao sul, garganta de pré-triagem no canto sudeste, cada zona descarregando ao
  norte na sua porta. O que mudou: a direção das raias e o que ocupa os flancos.</p>
  </div>
  <div class="plantas">
    <figure><div class="prancha">{svg('ring3_vigente.svg')}</div>
      <figcaption><b>Vigente.</b> Raias norte-sul de {num(zona(V,'B')['comprimento_raia_m'],1)} m em
      três blocos estreitos; os dois flancos, {num(P['largura_baia_m'],1)} m cada, são baias de
      espera. A fila sai pela boca inteira do bloco, que não coincide com o vão da porta.</figcaption></figure>
    <figure><div class="prancha">{svg('ring3_girado.svg')}</div>
      <figcaption><b>Este desenho.</b> Raias leste-oeste empilhadas, as três zonas ocupando a
      largura toda. A última raia corre rente à borda norte, então o portão de saída vai para o eixo
      da porta.</figcaption></figure>
  </div>
</section>

<section>
  <p class="rotulo">As três zonas</p>
  <h2>Largura de zona é comprimento de raia</h2>
  <div class="rolagem"><table>
    <thead><tr><th>Zona</th><th class="num">Raia</th><th class="num">Raias</th>
    <th class="num">Profundidade</th><th class="num">Caminhada</th><th class="num">Lotação</th>
    <th class="num">Esperado</th><th class="num">por eleitor</th></tr></thead>
    <tbody>{zonas_tab}</tbody>
    <caption>As larguras saem do comparecimento esperado de cada entrada (base B de 2022), então a
    lotação de cada zona fica proporcional à fila que ela vai receber. Entre as zonas ficam
    {num(P['vao_entre_zonas_m'],1)} m de folga, para fiscal e passagem de prioritário. “Caminhada” é
    o percurso de quem entra com a zona vazia.</caption>
  </table></div>
  <p class="nota"><strong>A descarga melhora de graça.</strong> Com as raias na horizontal, a última
  raia corre rente à borda norte da zona — o portão pode ficar em qualquer ponto dela, e vai para o
  eixo da porta. Na zona B o eixo de S5 cai dentro do bloco e a descarga fica perpendicular.</p>
  <div class="rolagem"><table>
    <thead><tr><th>Zona</th><th class="num">Desvio lateral · vigente</th><th class="num">Desvio · este desenho</th></tr></thead>
    <tbody>{descarga_tab}</tbody>
    <caption>Distância lateral entre o ponto de descarga da zona e o eixo da sua porta, no apron.</caption>
  </table></div>
</section>

<section>
  <p class="rotulo">Barreira</p>
  <h2>Onde os separadores são gastos</h2>
  <div class="rolagem"><table>
    <thead><tr><th>Componente</th><th class="num">Vigente (m)</th><th class="num">Este desenho (m)</th><th class="num">Δ</th></tr></thead>
    <tbody>
      {comp}
      <tr class="total"><td>Total</td><td class="mono num">{num(V['barreira_m'],1)}</td><td class="mono num">{num(H['barreira_m'],1)}</td><td class="mono num perda">{sinal(H['barreira_m']-V['barreira_m'],1)}</td></tr>
      <tr class="total"><td>Separadores de 2 m</td><td class="mono num">{V['separadores']}</td><td class="mono num">{H['separadores']}</td><td class="mono num perda">{sinal(H['separadores']-V['separadores'])}</td></tr>
    </tbody>
    <caption>Fora desta conta: o gradil permanente do Ring, que os dois desenhos usam de graça, e os
    100 unifilas (200 m) do item <em>d</em> do orçamento, que servem ao interior do Hall 2.</caption>
  </table></div>
  <div class="prosa" style="margin-top:22px">
  <p>A barreira de um serpenteado é <span class="mono">(n+1) × comprimento da raia − 1,2 × (n−1)</span>:
  n+1 corridas longitudinais, e cada divisória interna para 1,2 m antes da ponta para abrir a
  meia-volta. O que encarece aqui não é o giro — é a área nova. O flanco que era baia virou
  serpenteado, e serpenteado se paga em divisória.</p>
  </div>
</section>

<section>
  <p class="rotulo">Dimensionamento</p>
  <h2>Quanta barreira comprar</h2>
  <div class="prosa">
  <p>O número de raias por zona é a alavanca: troca lotação por barreira quase linearmente, sem
  mexer na largura das zonas nem na descarga. A profundidade que sobrar do Ring fica livre.</p>
  </div>
  <div class="rolagem"><table>
    <thead><tr><th class="num">Raias por zona</th><th class="num">Profundidade</th>
    <th class="num">Lotação</th><th class="num">A</th><th class="num">B</th><th class="num">C</th>
    <th class="num">Separadores</th><th class="num">A comprar</th><th class="num">Custo</th></tr></thead>
    <tbody>{escada_tab}</tbody>
    <caption>Linha destacada: o desenho, com a faixa inteira de
    {num(P['profundidade_serpenteado_m'],2)} m do plano vigente.</caption>
  </table></div>
  <p class="nota">Nenhuma linha cabe nas {P['estoque_separadores']} unidades da organizadora: o
  corredor de fundo, as raias do apron e o funil da garganta consomem {num(fixa,1)} m —
  {math.ceil(fixa/P['separador_m'])} separadores — antes da primeira raia.
  {"Se a compra de " + str(H['compra']) + " unidades não sair inteira, " + str(cabe_v[-1]['raias_por_zona']) + " raias por zona cabem dentro dos mesmos " + str(V['separadores']) + " separadores do plano vigente, com " + num(cabe_v[-1]['capacidade']) + " pessoas." if cabe_v else ""}</p>
</section>

<section>
  <p class="rotulo">Para registro</p>
  <h2>O passo intermediário: girar sem preencher</h2>
  <div class="prosa">
  <p>Girar as raias mantendo as baias é o mais barato dos três — {HB['separadores']} separadores,
  {V['separadores']-HB['separadores']} a menos que o plano vigente. Mas as zonas A e C, de
  {num(zona(V,'A')['largura_m'],1)} m de largura, viram raias de
  {num(zona(HB,'A')['comprimento_raia_m'],1)} m com {zona(HB,'A')['meias_voltas']} meias-voltas: é
  ziguezague, não fila. Preencher os flancos é o que resolve isso.</p>
  </div>
  <div class="rolagem"><table>
    <thead><tr><th></th><th class="num">Vigente</th><th class="num">Só girar</th><th class="num">Girar e preencher</th></tr></thead>
    <tbody>
      <tr><td>Lotação</td><td class="mono num">{num(V['capacidade'])}</td><td class="mono num">{num(HB['capacidade'])}</td><td class="mono num">{num(H['capacidade'])}</td></tr>
      <tr><td>… em raia medida</td><td class="mono num">{num(V['capacidade_raias'])}</td><td class="mono num">{num(HB['capacidade_raias'])}</td><td class="mono num ganho">{num(H['capacidade_raias'])}</td></tr>
      <tr><td>Raia mais curta</td><td class="mono num">{num(raia_curta(V),1)} m</td><td class="mono num perda">{num(raia_curta(HB),1)} m</td><td class="mono num">{num(raia_curta(H),1)} m</td></tr>
      <tr class="total"><td>Separadores</td><td class="mono num">{V['separadores']}</td><td class="mono num ganho">{HB['separadores']}</td><td class="mono num">{H['separadores']}</td></tr>
      <tr><td>A comprar</td><td class="mono num">{V['compra']}</td><td class="mono num">{HB['compra']}</td><td class="mono num">{H['compra']}</td></tr>
    </tbody>
  </table></div>
</section>

<section>
  <p class="rotulo">Método</p>
  <h2>Premissas, e o que se sabe do plano vigente</h2>
  <div class="prosa">
  <p>O plano vigente não está no repositório: <span class="mono">scripts/layout_ring3.py</span> e
  <span class="mono">saidas/plano_ring3.md</span> foram produzidos em sessão anterior e não chegaram
  a ser versionados. Ele foi reconstruído das cotas publicadas, e a reconstrução acerta os números
  publicados:</p>
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
  de contagem do plano original não é recuperável do que foi publicado. Por isso a comparação usa a
  regra deste modelo <strong>nos dois desenhos</strong>. Ancorando nos 300 separadores publicados em
  vez dos {V['separadores']} recalculados, este desenho daria cerca de
  <strong>{round(300*H['separadores']/V['separadores'])} unidades</strong>.</p>
  <div class="rolagem"><table>
    <thead><tr><th>Premissa</th><th class="num">Valor</th><th>Origem</th></tr></thead>
    <tbody>
      <tr><td>Módulo da raia</td><td class="mono num">{num(P['passo_raia_m'],2)} m</td><td>reconstruído dos blocos de 4,2 e 12,6 m</td></tr>
      <tr><td>Largura livre da raia</td><td class="mono num">{num(P['raia_util_m'],2)} m</td><td>reconstruído</td></tr>
      <tr><td>Densidade em raia</td><td class="mono num">{num(P['densidade_fila_p_m2'],1)} p/m²</td><td>reconstruído</td></tr>
      <tr><td>Densidade em baia</td><td class="mono num">{num(P['densidade_baia_p_m2'],1)} p/m²</td><td>reconstruído (só o plano vigente usa baia)</td></tr>
      <tr><td>Vão de meia-volta</td><td class="mono num">{num(P['vao_retorno_m'],1)} m</td><td>premissa</td></tr>
      <tr><td>Folga entre zonas</td><td class="mono num">{num(P['vao_entre_zonas_m'],1)} m</td><td>premissa</td></tr>
      <tr><td>Separador de fila</td><td class="mono num">{num(P['separador_m'],1)} m · EUR {num(P['separador_eur'],2)}</td><td>item d do orçamento (100 un. = EUR 1.303)</td></tr>
      <tr><td>Estoque da organizadora</td><td class="mono num">{P['estoque_separadores']} un. · {num(P['estoque_separadores']*P['separador_m'])} m</td><td>informado pelo Posto</td></tr>
    </tbody>
  </table></div>
</section>

<section>
  <p class="rotulo">Antes de contratar</p>
  <h2>O que decidir</h2>
  <ol class="pend">
    <li><div><h3>A compra dos separadores</h3><p>O desenho pede {H['compra']} unidades além das
    {P['estoque_separadores']} da organizadora, EUR {num(H['custo_compra_eur'],2)}. Confirmar prazo
    e preço antes de fechar a profundidade das zonas — a escada acima é o que dá para recuar sem
    mexer no resto do desenho.</p></div></li>
    <li><div><h3>A largura real do Ring</h3><p>O retângulo está centrado em S5 por estimativa. Nesta
    geometria a largura da zona <em>é</em> o comprimento da raia: a medição de campo mexe direto na
    lotação de cada entrada.</p></div></li>
    <li><div><h3>Onde o gradil abre</h3><p>A descarga perpendicular da zona B supõe portão no eixo
    de S5. Sem isso o desenho continua de pé, mas a descarga volta a ser oblíqua.</p></div></li>
    <li><div><h3>Piso e drenagem</h3><p>Raia leste-oeste de até {num(max(z['comprimento_raia_m'] for z in H['zonas']),1)} m
    atravessa a declividade do Ring de lado a lado. Verificar se algum trecho acumula água — entre
    40% e 65% de probabilidade de chuva em 4 de outubro, conforme o limiar da fonte.</p></div></li>
  </ol>
</section>

<footer>
  <p>Geometria do salão e das portas de <span class="mono">scripts/salao.py</span>; comparecimento
  esperado e papéis das portas das decisões do Posto de 06/09/2026. Modelo, plantas e todos os
  números desta página gerados por <span class="mono">scripts/ring3.py</span> e
  <span class="mono">scripts/gera_pagina_ring3.py</span>.</p>
  <p>Plantas em escala real sobre o contorno medido do Hall 2 (50,3 × 44,4 m) e o retângulo do
  Ring 3 (39,0 × 35,0 m, apron de 14 m). Números de lotação são estimativa, não limite de segurança
  homologado.</p>
</footer>
</div>
"""

destino = os.path.join(SAIDAS, "ring3_horizontal.html")
with open(destino, "w", encoding="utf-8") as f:
    f.write(HTML)
print("gravado:", destino, f"({len(HTML)/1024:.1f} KB)")
