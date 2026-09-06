#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Monta a pagina do Ring 3 girado a partir de saidas/ring3.json.

Todo numero da pagina vem do JSON que scripts/ring3.py gerou: a pagina nao
guarda nenhuma conta propria. Saida: saidas/ring3_horizontal.html
"""

import json
import os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAIDAS = os.path.join(RAIZ, "saidas")

D = json.load(open(os.path.join(SAIDAS, "ring3.json"), encoding="utf-8"))
V, H, HL = D["vigente"], D["girado"], D["raias_longas"]
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


def barreira_zona(d, e):
    """Barreira do serpenteado de uma zona, a partir das cotas do JSON."""
    z = zona(d, e)
    n, L = z["raias"], z["comprimento_raia_m"]
    return 2 * L + (n - 1) * max(0.0, L - P["vao_retorno_m"])


# ---- tabelas -------------------------------------------------------------
serp = []
for e in ENTRADAS:
    bv, bh = barreira_zona(V, e), barreira_zona(H, e)
    zv, zh = zona(V, e), zona(H, e)
    serp.append(
        f'<tr><td><span class="pin {e.lower()}">{e}</span> {PORTA[e]} · '
        f'{num(zv["largura_m"],1)} × {num(zv["profundidade_m"],2)} m</td>'
        f'<td class="mono num">{zv["raias"]} × {num(zv["comprimento_raia_m"],1)} m</td>'
        f'<td class="mono num">{num(bv,1)}</td>'
        f'<td class="mono num">{zh["raias"]} × {num(zh["comprimento_raia_m"],1)} m</td>'
        f'<td class="mono num">{num(bh,1)}</td>'
        f'<td class="mono num ganho">{sinal(bh-bv,1)}</td></tr>')
tv = sum(barreira_zona(V, e) for e in ENTRADAS)
th = sum(barreira_zona(H, e) for e in ENTRADAS)
serp.append(f'<tr class="total"><td>Serpenteados</td><td></td>'
            f'<td class="mono num">{num(tv,1)}</td><td></td>'
            f'<td class="mono num">{num(th,1)}</td>'
            f'<td class="mono num ganho">{sinal(th-tv,1)}</td></tr>')
serp = "\n".join(serp)

comp = []
chaves = list(dict.fromkeys(list(V["barreira_por_componente_m"]) +
                            list(H["barreira_por_componente_m"])))
for k in chaves:
    a = V["barreira_por_componente_m"].get(k, 0.0)
    b = H["barreira_por_componente_m"].get(k, 0.0)
    d = b - a
    cls = ' class="mono num ganho"' if d < -0.05 else ' class="mono num"'
    comp.append(f'<tr><td>{k}</td><td class="mono num">{num(a,1)}</td>'
                f'<td class="mono num">{num(b,1)}</td>'
                f'<td{cls}>{sinal(d,1) if abs(d) > 0.05 else "—"}</td></tr>')
comp = "\n".join(comp)

descarga = "\n".join(
    f'<tr><td><span class="pin {e.lower()}">{e}</span> {PORTA[e]}</td>'
    f'<td class="mono num">{num(zona(V,e)["desvio_lateral_m"],2)} m</td>'
    f'<td class="mono num">{num(zona(H,e)["desvio_lateral_m"],2)} m</td>'
    f'<td class="mono num">{num(zona(V,e)["meias_voltas"])}</td>'
    f'<td class="mono num{" perda" if zona(H,e)["meias_voltas"] > 20 else ""}">'
    f'{num(zona(H,e)["meias_voltas"])}</td>'
    f'<td class="mono num">{num(zona(V,e)["capacidade"])}</td>'
    f'<td class="mono num">{num(zona(H,e)["capacidade"])}</td></tr>'
    for e in ENTRADAS)

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
  <p class="chamada">As mesmas três zonas, o mesmo corredor de fundo, as mesmas portas — só a
  dobra da fila gira 90°: as raias passam a correr de leste para oeste, empilhadas em altura.
  A pergunta que isso responde é de quantas barreiras o Ring precisa.</p>
  <dl class="faixa">
    <div><dt>Separadores</dt><dd class="delta">{H['separadores']}<small>plano vigente: {V['separadores']} · {V['separadores']-H['separadores']} a menos</small></dd></div>
    <div><dt>A comprar</dt><dd class="delta">{H['compra']}<small>vigente: {V['compra']} · estoque de {P['estoque_separadores']}</small></dd></div>
    <div><dt>Custo da compra</dt><dd>EUR {num(H['custo_compra_eur'],0)}<small>vigente: EUR {num(V['custo_compra_eur'],0)}</small></dd></div>
    <div><dt>Capacidade</dt><dd>{num(H['capacidade'])}<small>vigente: {num(V['capacidade'])} pessoas</small></dd></div>
    <div><dt>Meias-voltas</dt><dd class="alerta">{H['meias_voltas']}<small>vigente: {V['meias_voltas']} · é o custo do giro</small></dd></div>
  </dl>
</header>

<section>
  <p class="rotulo">A resposta</p>
  <h2>{V['separadores']-H['separadores']} separadores a menos, com a mesma fila</h2>
  <div class="prosa">
  <p>Girar as raias mantém a área ocupada — e, portanto, a lotação — mas troca
  <strong>raias longas e poucas</strong> por <strong>raias curtas e muitas</strong>. A barreira de
  um serpenteado é <span class="mono">(n+1) × comprimento − 1,2 × (n−1)</span>: são n+1 corridas
  longitudinais, e cada divisória interna para 1,2 m antes da ponta para abrir a meia-volta. Mais
  raias significam mais desses descontos, sobre corridas mais curtas. O total cai
  {num((1-H['barreira_m']/V['barreira_m'])*100,0)}%.</p>
  </div>
  <div class="rolagem"><table>
    <thead><tr><th></th><th class="num">Vigente · raias N–S</th><th class="num">Girado · raias L–O</th><th class="num">Δ</th></tr></thead>
    <tbody>
      <tr><td>Barreira</td><td class="mono num">{num(V['barreira_m'],1)} m</td><td class="mono num">{num(H['barreira_m'],1)} m</td><td class="mono num ganho">{sinal(H['barreira_m']-V['barreira_m'],1)} m</td></tr>
      <tr class="total"><td>Separadores de 2 m</td><td class="mono num">{V['separadores']}</td><td class="mono num">{H['separadores']}</td><td class="mono num ganho">{sinal(H['separadores']-V['separadores'])}</td></tr>
      <tr><td>A comprar (estoque {P['estoque_separadores']})</td><td class="mono num">{V['compra']}</td><td class="mono num">{H['compra']}</td><td class="mono num ganho">{sinal(H['compra']-V['compra'])}</td></tr>
      <tr><td>Custo da compra</td><td class="mono num">EUR {num(V['custo_compra_eur'],2)}</td><td class="mono num">EUR {num(H['custo_compra_eur'],2)}</td><td class="mono num ganho">EUR {sinal(H['custo_compra_eur']-V['custo_compra_eur'],2)}</td></tr>
      <tr><td>Capacidade</td><td class="mono num">{num(V['capacidade'])}</td><td class="mono num">{num(H['capacidade'])}</td><td class="mono num">{sinal(H['capacidade']-V['capacidade'])}</td></tr>
      <tr><td>Metros de barreira por pessoa</td><td class="mono num">{num(V['m_por_pessoa'],3)}</td><td class="mono num">{num(H['m_por_pessoa'],3)}</td><td class="mono num ganho">{sinal(H['m_por_pessoa']-V['m_por_pessoa'],3)}</td></tr>
    </tbody>
    <caption>Os dois desenhos medidos com o mesmo modelo — mesma densidade, mesmo módulo de raia,
    mesma regra de barreira. A diferença é entre geometrias, não entre métodos.</caption>
  </table></div>
</section>

<section>
  <p class="rotulo">Os dois desenhos</p>
  <h2>O que exatamente mudou de lugar</h2>
  <div class="prosa">
  <p>Nada, além da direção das raias. O corredor de fundo continua ao sul, a garganta de
  pré-triagem no canto sudeste, as baias nos dois flancos, e cada zona continua descarregando
  ao norte na sua porta.</p>
  </div>
  <div class="plantas">
    <figure><div class="prancha">{svg('ring3_vertical.svg')}</div>
      <figcaption><b>Vigente.</b> Raias norte-sul de {num(zona(V,'B')['comprimento_raia_m'],2)} m.
      A fila sobe do corredor de fundo e sai pela boca inteira do bloco — que tem a largura do
      bloco e não coincide com o vão da porta.</figcaption></figure>
    <figure><div class="prancha">{svg('ring3_horizontal.svg')}</div>
      <figcaption><b>Girado.</b> Raias leste-oeste empilhadas. A última raia corre rente à borda
      norte da zona, então o portão de saída pode ficar em qualquer ponto dela — e vai para o eixo
      da porta.</figcaption></figure>
  </div>
</section>

<section>
  <p class="rotulo">De onde vem a economia</p>
  <h2>Zona por zona</h2>
  <div class="rolagem"><table>
    <thead><tr><th>Zona</th><th class="num">Vigente</th><th class="num">Barreira (m)</th>
    <th class="num">Girado</th><th class="num">Barreira (m)</th><th class="num">Δ</th></tr></thead>
    <tbody>{serp}</tbody>
    <caption>A profundidade de {num(zona(V,'A')['profundidade_m'],2)} m comporta
    {zona(H,'A')['raias']} raias giradas, com o passo apertado de {num(P['passo_raia_m'],2)} m
    para {num(zona(H,'A')['passo_m'],3)} m.</caption>
  </table></div>
  <div class="rolagem"><table>
    <thead><tr><th>Componente do plano</th><th class="num">Vigente (m)</th>
    <th class="num">Girado (m)</th><th class="num">Δ</th></tr></thead>
    <tbody>
      {comp}
      <tr class="total"><td>Total</td><td class="mono num">{num(V['barreira_m'],1)}</td>
      <td class="mono num">{num(H['barreira_m'],1)}</td>
      <td class="mono num ganho">{sinal(H['barreira_m']-V['barreira_m'],1)}</td></tr>
    </tbody>
    <caption>Fora desta conta: o gradil permanente do Ring, que os dois desenhos usam de graça, e
    os 100 unifilas (200 m) do item <em>d</em> do orçamento, que servem ao interior do Hall 2.</caption>
  </table></div>
  <p class="nota">A queda quase toda está nos serpenteados. As raias do apron encurtam de leve por
  um motivo que vale registrar: na zona B o eixo de S5 cai dentro do bloco, e com o portão móvel a
  descarga fica <strong>perpendicular</strong> — desvio lateral zero, contra
  {num(zona(V,'B')['desvio_lateral_m'],2)} m no desenho vigente.</p>
</section>

<section>
  <p class="rotulo">O outro lado</p>
  <h2>O que o giro cobra: a meia-volta</h2>
  <div class="rolagem"><table>
    <thead><tr><th>Zona</th><th class="num">Desvio vigente</th><th class="num">Desvio girado</th>
    <th class="num">Curvas vigente</th><th class="num">Curvas girado</th>
    <th class="num">Fila vigente</th><th class="num">Fila girada</th></tr></thead>
    <tbody>{descarga}</tbody>
    <caption>“Desvio” é a distância lateral entre o ponto de descarga da zona e o eixo da sua porta;
    “curvas” são as meias-voltas que o eleitor dá até sair.</caption>
  </table></div>
  <div class="prosa" style="margin-top:22px">
  <p>Nas zonas A e C, de {num(zona(V,'A')['largura_m'],1)} m de largura, a raia girada tem
  {num(zona(H,'A')['comprimento_raia_m'],1)} m e o eleitor dá {zona(H,'A')['meias_voltas']} curvas
  até sair: é um ziguezague, não uma fila. Na zona B, de
  {num(zona(V,'B')['largura_m'],1)} m, a raia girada continua confortável.</p>
  <p>O modelo de capacidade não cobra nada pela curva. Se cada meia-volta custar
  {num(P['perda_por_meia_volta_m'],1)} m de fila aproveitável — premissa, não medição —, a
  paridade de lotação desaparece:</p>
  </div>
  <div class="rolagem"><table>
    <thead><tr><th></th><th class="num">Vigente</th><th class="num">Girado</th></tr></thead>
    <tbody>
      <tr><td>Capacidade nominal</td><td class="mono num">{num(V['capacidade'])}</td><td class="mono num">{num(H['capacidade'])}</td></tr>
      <tr><td>Descontadas as meias-voltas</td><td class="mono num">{num(V['capacidade_com_perda_de_meia_volta'])}</td><td class="mono num perda">{num(H['capacidade_com_perda_de_meia_volta'])}</td></tr>
    </tbody>
  </table></div>
  <p class="nota"><strong>A economia de barreira é robusta; a paridade de capacidade não é.</strong>
  Sob a premissa da curva, o girado perde cerca de
  {num(V['capacidade_com_perda_de_meia_volta']-H['capacidade_com_perda_de_meia_volta'])} pessoas
  para o vigente — ainda muito acima do pico plausível, mas não é empate.</p>
</section>

<section>
  <p class="rotulo">Variante</p>
  <h2>Se o ziguezague de A e C incomodar</h2>
  <div class="prosa">
  <p>A saída é alargar as três zonas até a largura do Ring, o que consome as baias de flanco.
  Toda a lotação vira fila em raia medida — e a capacidade que o plano vigente ganha de graça nas
  baias, que usam o gradil em três lados, passa a ser paga em divisória.</p>
  </div>
  <div class="rolagem"><table>
    <thead><tr><th></th><th class="num">Vigente</th><th class="num">Girado</th><th class="num">Raias longas</th></tr></thead>
    <tbody>
      <tr><td>Raia mais curta</td><td class="mono num">{num(min(z['comprimento_raia_m'] for z in V['zonas']),1)} m</td><td class="mono num perda">{num(min(z['comprimento_raia_m'] for z in H['zonas']),1)} m</td><td class="mono num">{num(min(z['comprimento_raia_m'] for z in HL['zonas']),1)} m</td></tr>
      <tr><td>Capacidade</td><td class="mono num">{num(V['capacidade'])}</td><td class="mono num">{num(H['capacidade'])}</td><td class="mono num">{num(HL['capacidade'])}</td></tr>
      <tr><td>… em raia medida</td><td class="mono num">{num(V['capacidade_raias'])}</td><td class="mono num">{num(H['capacidade_raias'])}</td><td class="mono num">{num(HL['capacidade_raias'])}</td></tr>
      <tr><td>… em baia de espera</td><td class="mono num">{num(V['capacidade_baias'])}</td><td class="mono num">{num(H['capacidade_baias'])}</td><td class="mono num">—</td></tr>
      <tr class="total"><td>Separadores</td><td class="mono num">{V['separadores']}</td><td class="mono num">{H['separadores']}</td><td class="mono num perda">{HL['separadores']}</td></tr>
      <tr><td>A comprar</td><td class="mono num">{V['compra']}</td><td class="mono num">{H['compra']}</td><td class="mono num">{HL['compra']}</td></tr>
    </tbody>
  </table></div>
</section>

<section>
  <p class="rotulo">Método</p>
  <h2>Premissas, e o que se sabe do plano original</h2>
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
  regra deste modelo <strong>nos dois desenhos</strong>. Aplicada aos 300 separadores publicados, a
  mesma redução de {num((1-H['separadores']/V['separadores'])*100,0)}% daria cerca de
  <strong>{round(300*H['separadores']/V['separadores'])} unidades</strong>.</p>
  <div class="rolagem"><table>
    <thead><tr><th>Premissa</th><th class="num">Valor</th><th>Origem</th></tr></thead>
    <tbody>
      <tr><td>Módulo da raia</td><td class="mono num">{num(P['passo_raia_m'],2)} m</td><td>reconstruído dos blocos de 4,2 e 12,6 m</td></tr>
      <tr><td>Largura livre da raia</td><td class="mono num">{num(P['raia_util_m'],2)} m</td><td>reconstruído</td></tr>
      <tr><td>Densidade em raia</td><td class="mono num">{num(P['densidade_fila_p_m2'],1)} p/m²</td><td>reconstruído</td></tr>
      <tr><td>Densidade em baia</td><td class="mono num">{num(P['densidade_baia_p_m2'],1)} p/m²</td><td>reconstruído</td></tr>
      <tr><td>Vão de meia-volta</td><td class="mono num">{num(P['vao_retorno_m'],1)} m</td><td>premissa</td></tr>
      <tr><td>Perda por meia-volta</td><td class="mono num">{num(P['perda_por_meia_volta_m'],1)} m</td><td>premissa (só na análise de sensibilidade)</td></tr>
      <tr><td>Separador de fila</td><td class="mono num">{num(P['separador_m'],1)} m · EUR {num(P['separador_eur'],2)}</td><td>item d do orçamento (100 un. = EUR 1.303)</td></tr>
      <tr><td>Estoque da organizadora</td><td class="mono num">{P['estoque_separadores']} un. · {num(P['estoque_separadores']*P['separador_m'])} m</td><td>plano do Ring 3</td></tr>
    </tbody>
  </table></div>
</section>

<section>
  <p class="rotulo">Antes de contratar</p>
  <h2>O que decidir</h2>
  <ol class="pend">
    <li><div><h3>O ziguezague de A e C é aceitável?</h3><p>{num(zona(H,'A')['comprimento_raia_m'],1)} m
    de raia com {zona(H,'A')['meias_voltas']} curvas, para um público que inclui idosos, cadeirantes
    e carrinhos de bebê. É a única pergunta que decide entre o giro e a variante de raias longas.</p></div></li>
    <li><div><h3>Onde o gradil abre</h3><p>A descarga perpendicular da zona B supõe portão no eixo
    de S5. Sem isso, o giro ainda economiza barreira, mas perde a melhoria de descarga.</p></div></li>
    <li><div><h3>A largura real das zonas</h3><p>O retângulo do Ring está centrado em S5 por
    estimativa. Na geometria girada, a largura da zona <em>é</em> o comprimento da raia — a medição
    de campo mexe diretamente na capacidade.</p></div></li>
    <li><div><h3>As densidades</h3><p>{num(P['densidade_fila_p_m2'],1)} pessoas/m² em raia e
    {num(P['densidade_baia_p_m2'],1)} em baia são reconstrução, não medição. Se a densidade real sob
    guarda-chuva for menor, os dois desenhos perdem na mesma proporção e a comparação não muda.</p></div></li>
  </ol>
</section>

<footer>
  <p>Geometria do salão e das portas de <span class="mono">scripts/salao.py</span>; comparecimento
  esperado e papéis das portas das decisões do Posto de 06/09/2026. Modelo, plantas e todos os
  números desta página gerados por <span class="mono">scripts/ring3.py</span> e
  <span class="mono">scripts/gera_pagina_ring3.py</span>.</p>
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
