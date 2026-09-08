#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Monta a pagina dos quatro desenhos do Ring 3 a partir de saidas/ring3.json.

Todo numero da pagina vem do JSON que scripts/ring3.py gerou: a pagina nao
guarda nenhuma conta propria. Saida: saidas/ring3_horizontal.html
"""

import json
import math
import os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAIDAS = os.path.join(RAIZ, "saidas")

D = json.load(open(os.path.join(SAIDAS, "ring3.json"), encoding="utf-8"))
V, VS = D["vertical_com_baias"], D["vertical_sem_baias"]
PV = D["plano_vigente_reconstruido"]
HB, H = D["girado_com_baias"], D["girado"]
ESCADA_V, ESCADA_H = D["escada_de_profundidade"], D["escada_de_raias"]
P, CONF = D["premissas"], D["aderencia_ao_plano_original"]
ESP = P["comparecimento_esperado"]
PORTA = {"A": "S4", "B": "S5", "C": "S6"}
ENTRADAS = ("A", "B", "C")

QUATRO = [("Com baias", "raias N–S, com baias", V, "ring3_vertical_com_baias.svg"),
          ("O desenho pedido", "raias N–S, sem baias", VS, "ring3_vertical_sem_baias.svg"),
          ("Girado", "raias L–O, com baias", HB, "ring3_girado_com_baias.svg"),
          ("Girado sem baias", "raias L–O, sem baias", H, "ring3_girado.svg")]


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


def linha(rot, valor, destaque=False):
    tds = "".join(
        f'<td class="mono num{" marca" if d is VS and destaque else ""}">{valor(d)}</td>'
        for _, _, d, _ in QUATRO)
    return f'<tr{" class=total" if destaque else ""}><td>{rot}</td>{tds}</tr>'


tabela4 = "\n".join([
    linha("Lotação", lambda d: num(d["capacidade"]), True),
    linha("… em raia medida", lambda d: num(d["capacidade_raias"])),
    linha("… em baia de espera",
          lambda d: num(d["capacidade_baias"]) if d["capacidade_baias"] else "—"),
    linha("Raia mais curta",
          lambda d: num(min(z["comprimento_raia_m"] for z in d["zonas"]), 1) + " m"),
    linha("Meias-voltas", lambda d: num(d["meias_voltas"])),
    linha("Barreira", lambda d: num(d["barreira_m"], 1) + " m"),
    linha("Separadores de 2 m", lambda d: num(d["separadores"]), True),
    linha(f"A comprar (estoque {P['estoque_separadores']})", lambda d: num(d["compra"])),
    linha("Custo da compra", lambda d: "EUR " + num(d["custo_compra_eur"], 2)),
    linha("Metros por pessoa", lambda d: num(d["m_por_pessoa"], 3)),
])

COMPONENTES = [("Perímetro das zonas", "perímetro das zonas"),
               ("Divisórias entre as raias", "divisórias entre as raias"),
               ("Corredor de fundo (parede norte)", "corredor de fundo (parede norte)"),
               ("Fechamento das baias", "fechamento das baias de flanco"),
               ("Raias do apron", "raias do apron até as portas")]

componentes_tab = "\n".join(
    f'<tr><td>{rot}</td>' + "".join(
        f'<td class="mono num">'
        f'{num(d["barreira_por_componente_m"][ch],1) + " m" if d["barreira_por_componente_m"].get(ch) else "—"}'
        f'</td>' for _, _, d, _ in QUATRO) + "</tr>"
    for rot, ch in COMPONENTES) + "\n" + (
    '<tr class="total"><td>Total</td>' + "".join(
        f'<td class="mono num">{num(d["barreira_m"],1)} m</td>' for _, _, d, _ in QUATRO) +
    "</tr>\n" +
    '<tr class="total"><td>Separadores de 2 m</td>' + "".join(
        f'<td class="mono num">{d["separadores"]}</td>' for _, _, d, _ in QUATRO) + "</tr>")

mapas4 = "\n".join(
    f'<figure><div class="prancha">{svg(arq.replace("ring3_", "ring3_barreiras_"))}</div>'
    f'<figcaption><b>{rot}.</b> {sub} · {d["separadores"]} separadores</figcaption>'
    f'</figure>' for rot, sub, d, arq in QUATRO)

plantas4 = "\n".join(
    f'<figure><div class="prancha">{svg(arq)}</div>'
    f'<figcaption><b>{rot}.</b> {sub} · {num(d["capacidade"])} pessoas '
    f'({num(d["capacidade_raias"])} em raia) · {d["separadores"]} separadores'
    f'</figcaption></figure>' for rot, sub, d, arq in QUATRO)

zonas_tab = "\n".join(
    f'<tr><td><span class="pin {z["entrada"].lower()}">{z["entrada"]}</span> '
    f'{PORTA[z["entrada"]]}</td>'
    f'<td class="mono num">{num(z["largura_m"],2)} m</td>'
    f'<td class="mono num">{z["raias"]}</td>'
    f'<td class="mono num">{num(z["comprimento_raia_m"],2)} m</td>'
    f'<td class="mono num">{num(z["caminhada_m"])} m</td>'
    f'<td class="mono num">{num(z["capacidade"])}</td>'
    f'<td class="mono num">{num(ESP[z["entrada"]])}</td>'
    f'<td class="mono num">{num(VS["capacidade_por_eleitor_esperado"][z["entrada"]],4)}</td>'
    f'</tr>' for z in VS["zonas"])

desvio_tab = "\n".join(
    f'<tr><td><span class="pin {e.lower()}">{e}</span> {PORTA[e]}</td>' + "".join(
        f'<td class="mono num{" ganho" if zona(d,e)["desvio_lateral_m"] < 0.01 else ""}">'
        f'{num(zona(d,e)["desvio_lateral_m"],2)} m</td>' for _, _, d, _ in QUATRO) +
    "</tr>" for e in ENTRADAS)

escada_v_tab = "\n".join(
    '<tr{cls}><td class="mono num">{prof} m</td><td class="mono num">{cap}</td>'
    '<td class="mono num">{a}</td><td class="mono num">{b}</td>'
    '<td class="mono num">{c}</td><td class="mono num">{sep}</td>'
    '<td class="mono num">{compra}</td><td class="mono num">EUR {custo}</td></tr>'.format(
        cls=' class="marcada"' if abs(r["profundidade_m"] - P["profundidade_serpenteado_m"]) < 0.01 else "",
        prof=num(r["profundidade_m"], 2), cap=num(r["capacidade"]),
        a=num(r["por_entrada"]["A"]), b=num(r["por_entrada"]["B"]),
        c=num(r["por_entrada"]["C"]), sep=r["separadores"], compra=r["compra"],
        custo=num(r["custo_compra_eur"], 2)) for r in ESCADA_V)

escada_h_tab = "\n".join(
    '<tr{cls}><td class="mono num">{r}</td><td class="mono num">{prof} m</td>'
    '<td class="mono num">{cap}</td><td class="mono num">{sep}</td>'
    '<td class="mono num">{compra}</td></tr>'.format(
        cls=' class="marcada"' if l["raias_por_zona"] == H["zonas"][0]["raias"] else "",
        r=l["raias_por_zona"], prof=num(l["profundidade_m"], 1),
        cap=num(l["capacidade"]), sep=l["separadores"], compra=l["compra"])
    for l in ESCADA_H)

cabe_v = [r for r in ESCADA_V if r["separadores"] <= V["separadores"]]
fixa = VS["barreira_m"] - sum(
    2 * z["comprimento_raia_m"] + (z["raias"] - 1) *
    max(0.0, z["comprimento_raia_m"] - P["vao_retorno_m"]) for z in VS["zonas"])
folga = (D["ring"]["x1"] - D["ring"]["x0"] - sum(z["largura_m"] for z in VS["zonas"])) / 2
raias_vs = sum(z["raias"] for z in VS["zonas"])

HTML = f"""<title>Ring 3, quatro desenhos</title>
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
span.sub{{display:block; font-size:.72rem; color:var(--fraco); font-weight:400}}
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
<style>
td.marca{{background:var(--realce); font-weight:600}}
.plantas figcaption b{{color:var(--tinta)}}
</style>

<div class="folha">
<header>
  <p class="olho">Eleições 2026 · 1º turno · 4 de outubro · RDS Ballsbridge · fila externa</p>
  <h1>Ring 3, quatro desenhos</h1>
  <p class="chamada">Sem faixa de garganta: o corredor de fundo foi para o limite sul do Ring e as
  filas começam logo acima dele — {num(P['profundidade_serpenteado_m'],2)} m de raia contra os
  {num(P['profundidade_plano_vigente_m'],2)} m do plano vigente. Sobre essa moldura, duas decisões:
  a direção das raias e o que ocupa os flancos.</p>
  <dl class="faixa">
    <div><dt>O desenho pedido</dt><dd>N–S sem baias<small>{raias_vs} raias de {num(P['profundidade_serpenteado_m'],2)} m</small></dd></div>
    <div><dt>Lotação</dt><dd class="delta">{num(VS['capacidade'])}<small>toda em raia · a maior dos quatro</small></dd></div>
    <div><dt>Separadores</dt><dd class="alerta">{VS['separadores']}<small>a mais cara das quatro · com baias: {V['separadores']}</small></dd></div>
    <div><dt>A comprar</dt><dd>{VS['compra']}<small>sobre os {P['estoque_separadores']} da organizadora · EUR {num(VS['custo_compra_eur'],0)}</small></dd></div>
    <div><dt>Profundidade da raia</dt><dd class="delta">{num(P['profundidade_serpenteado_m'],2)} m<small>plano vigente: {num(P['profundidade_plano_vigente_m'],2)} m + garganta</small></dd></div>
  </dl>
</header>

<section>
  <p class="rotulo">As duas decisões</p>
  <h2>Direção das raias, e o que ocupa os flancos</h2>
  <div class="prosa">
  <p>A <strong>direção das raias</strong> é norte-sul, como no plano vigente, ou leste-oeste,
  empilhadas em altura. As <strong>baias de flanco</strong> — duas áreas de espera de
  {num(P['largura_baia_m'],1)} m — ficam como estão ou viram serpenteado. Como as barreiras
  laterais são removíveis e a evacuação sai pelos vãos entre as zonas e pelo gradil, a baia não
  precisa existir como reserva de escape.</p>
  <p>As duas decisões são independentes, e só uma delas mexe no orçamento de barreira:
  <strong>quem decide a barreira são as baias</strong>. Preencher os flancos custa
  {VS['separadores']-V['separadores']} separadores na vertical e {H['separadores']-HB['separadores']}
  na horizontal; girar as raias custa {HB['separadores']-V['separadores']} com as baias e poupa
  {VS['separadores']-H['separadores']} sem elas — ruído.</p>
  </div>
  <div class="rolagem"><table>
    <thead><tr><th></th>
      <th class="num">N–S<br>com baias</th><th class="num">N–S<br>sem baias</th>
      <th class="num">L–O<br>com baias</th><th class="num">L–O<br>sem baias</th></tr></thead>
    <tbody>{tabela4}</tbody>
    <caption>Coluna destacada: o desenho pedido. Todos medidos com o mesmo modelo — mesma
    densidade, mesmo módulo de raia, mesma regra de barreira.</caption>
  </table></div>
</section>

<section>
  <p class="rotulo">O que a garganta custava</p>
  <h2>Oito metros e um quarto, devolvidos à fila</h2>
  <div class="prosa">
  <p>O plano vigente reservava uma faixa de
  {num(35 - P['profundidade_plano_vigente_m'] - P['largura_corredor_m'],2)} m ao sul do Ring para
  a garganta e a pré-triagem, e punha o corredor de fundo acima dela. Sem essa faixa, o corredor
  encosta no gradil sul e a raia cresce de {num(P['profundidade_plano_vigente_m'],2)} m para
  {num(P['profundidade_serpenteado_m'],2)} m — <strong>{num(P['profundidade_serpenteado_m']-P['profundidade_plano_vigente_m'],2)} m
  a mais em cada raia</strong>, que é de onde vem quase toda a lotação a mais destes quatro
  desenhos.</p>
  <p>Na barreira, duas consequências: o funil da garganta sai da conta, e a <strong>parede sul do
  corredor passa a ser o próprio gradil</strong> do Ring — só a parede norte é barreira, e é ela
  que fecha o lado sul das três zonas.</p>
  </div>
  <div class="rolagem"><table>
    <thead><tr><th>Faixa (norte → sul)</th><th class="num">Plano vigente</th><th class="num">Estes desenhos</th></tr></thead>
    <tbody>
      <tr><td>Serpenteado</td><td class="mono num">{num(P['profundidade_plano_vigente_m'],2)} m</td><td class="mono num ganho">{num(P['profundidade_serpenteado_m'],2)} m</td></tr>
      <tr><td>Corredor de fundo</td><td class="mono num">{num(P['largura_corredor_m'],2)} m</td><td class="mono num">{num(P['largura_corredor_m'],2)} m</td></tr>
      <tr><td>Garganta e pré-triagem</td><td class="mono num">{num(35 - P['profundidade_plano_vigente_m'] - P['largura_corredor_m'],2)} m</td><td class="mono num">—</td></tr>
      <tr class="total"><td>Profundidade do Ring</td><td class="mono num">35,00 m</td><td class="mono num">35,00 m</td></tr>
    </tbody>
    <caption>A faixa de {num(35 - P['profundidade_plano_vigente_m'] - P['largura_corredor_m'],2)} m
    da garganta era, no modelo, uma área livre de {num((35 - P['profundidade_plano_vigente_m'] - P['largura_corredor_m']) * (D['ring']['x1']-D['ring']['x0']),0)} m²
    mais um funil de 12 m. Onde a pré-triagem passa a acontecer é uma decisão em aberto — ver as
    pendências.</caption>
  </table></div>
</section>

<section>
  <p class="rotulo">As quatro plantas</p>
  <h2>Em escala, sobre o mesmo Ring</h2>
  <div class="plantas">{plantas4}</div>
</section>

<section>
  <p class="rotulo">O desenho pedido</p>
  <h2>Raias norte-sul, os flancos preenchidos</h2>
  <div class="prosa">
  <p>Os {num(2*P['largura_baia_m'],1)} m dos dois flancos viram serpenteado. Como na vertical a
  largura da zona é um número inteiro de raias, as larguras são arredondadas para o módulo de
  {num(P['passo_raia_m'],2)} m e a sobra vai para os vãos entre as zonas: são {raias_vs} raias de
  {num(P['profundidade_serpenteado_m'],2)} m ocupando
  {num(sum(z['largura_m'] for z in VS['zonas']),2)} m dos
  {num(D['ring']['x1']-D['ring']['x0'],2)} m de largura do Ring, com <strong>{num(folga,2)} m de
  vão entre as zonas</strong>.</p>
  </div>
  <div class="rolagem"><table>
    <thead><tr><th>Zona</th><th class="num">Largura</th><th class="num">Raias</th>
    <th class="num">Raia</th><th class="num">Caminhada</th><th class="num">Lotação</th>
    <th class="num">Esperado</th><th class="num">por eleitor</th></tr></thead>
    <tbody>{zonas_tab}</tbody>
    <caption>“Caminhada” é o percurso de quem entra com a zona vazia. “Por eleitor” é a lotação
    dividida pelo comparecimento esperado daquela entrada (base B de 2022) — quanto mais parelho
    entre as três, melhor distribuída a fila.</caption>
  </table></div>
  <p class="nota"><strong>Onde se evacua.</strong> Os {num(folga,2)} m entre as zonas, mais o
  gradil: como as barreiras laterais são removíveis, nenhuma área precisa ficar vazia à espera de
  uma emergência — que era a função que sobrava para as baias.</p>
</section>

<section>
  <p class="rotulo">De onde vem a barreira</p>
  <h2>Perímetro e divisórias respondem a decisões diferentes</h2>
  <div class="prosa">
  <p>A barreira de uma zona tem duas parcelas. O <strong>perímetro</strong> fecha o retângulo — o
  lado norte, de frente para o apron, menos o portão de {num(P['vao_saida_m'],1)} m; os lados leste
  e oeste, exceto onde coincidem com o gradil permanente do Ring; o lado sul não entra porque a
  parede norte do corredor de fundo já o fecha. As <strong>divisórias</strong> separam raia de
  raia: (n−1) corridas, cada uma {num(P['vao_retorno_m'],1)} m mais curta que a raia para abrir a
  meia-volta.</p>
  <p>O perímetro é o mesmo nas duas orientações — é o mesmo retângulo. Só as divisórias mudam ao
  girar, e a diferença é <span class="mono">(profundidade − largura) × (1 −
  {num(P['vao_retorno_m'],1)}/{num(P['passo_raia_m'],2)})</span>, ou seja 0,14 × (profundidade −
  largura) por zona: menos de 3 m numa zona de 4,2 × 23,75 m. É por isso que girar não move o
  orçamento.</p>
  </div>
  <div class="rolagem"><table>
    <thead><tr><th>Componente</th>
      <th class="num">N–S<br>com baias</th><th class="num">N–S<br>sem baias</th>
      <th class="num">L–O<br>com baias</th><th class="num">L–O<br>sem baias</th></tr></thead>
    <tbody>{componentes_tab}</tbody>
    <caption>Fora desta conta: o gradil permanente do Ring, que os quatro desenhos usam de graça, e
    os 100 unifilas (200 m) do item <em>d</em> do orçamento, que servem ao interior do Hall 2.</caption>
  </table></div>
</section>

<section>
  <p class="rotulo">O mapa das barreiras</p>
  <h2>Onde cada metro é gasto, e o que ele segura</h2>
  <div class="prosa">
  <p>Cada corrida de barreira que a conta soma está desenhada aqui, colorida pelo seu componente —
  o mapa <em>é</em> a conta, gerado dos mesmos segmentos, e o script recusa a gerar a planta se os
  dois não fecharem. O gradil permanente do Ring aparece tracejado, em cinza: ele fecha o
  compound de graça. Os portões de {num(P['vao_saida_m'],1)} m aparecem como interrupções — são
  descontados de cada corrida que atravessam.</p>
  </div>
  <div class="plantas">{mapas4}</div>
  <div class="rolagem"><table>
    <thead><tr><th>Componente</th><th class="num">N–S sem baias</th><th>O que ele segura</th><th>Dá para cortar?</th></tr></thead>
    <tbody>
      <tr><td><span class="pin" style="color:#1f6fb2">▬</span> Perímetro das zonas</td>
        <td class="mono num">{num(VS['barreira_por_componente_m']['perímetro das zonas'],1)} m<span class="sub">{math.ceil(VS['barreira_por_componente_m']['perímetro das zonas']/P['separador_m'])} sep.</span></td>
        <td>Impede a fila de vazar de lado — para a zona vizinha, para o vão de circulação ou para o apron. É o que mantém as três entradas separadas, que é a razão de existir da pré-triagem.</td>
        <td><strong>Não.</strong> Só encurta: o lado que encosta no gradil já não é contado, e cada metro a mais de portão de saída tira um metro do lado norte.</td></tr>
      <tr><td><span class="pin" style="color:#7a8794">▬</span> Divisórias entre as raias</td>
        <td class="mono num">{num(VS['barreira_por_componente_m']['divisórias entre as raias'],1)} m<span class="sub">{math.ceil(VS['barreira_por_componente_m']['divisórias entre as raias']/P['separador_m'])} sep.</span></td>
        <td>São o serpenteado. Sem elas não há fila: há uma massa de gente dentro de um retângulo cercado, sem ordem de chegada nem vazão previsível.</td>
        <td><strong>Só encurtando a raia.</strong> É o maior item e a alavanca real: cada 4 m a menos de profundidade tiram cerca de 29 separadores — é a escada de dimensionamento abaixo.</td></tr>
      <tr><td><span class="pin" style="color:#16867f">▬</span> Corredor de fundo (parede norte)</td>
        <td class="mono num">{num(VS['barreira_por_componente_m']['corredor de fundo (parede norte)'],1)} m<span class="sub">{math.ceil(VS['barreira_por_componente_m']['corredor de fundo (parede norte)']/P['separador_m'])} sep.</span></td>
        <td>Separa quem está chegando de quem já está na fila, e é o fechamento sul das três zonas — por isso o lado sul das zonas não entra na conta.</td>
        <td><strong>Não, sem perder o controle da entrada.</strong> Se o corredor não for barrado, as zonas ficam abertas ao sul e qualquer um entra por qualquer ponto.</td></tr>
      <tr><td><span class="pin" style="color:#8b5cf6">▬</span> Fechamento das baias</td>
        <td class="mono num">—</td>
        <td>Fecha o lado norte das baias de espera, para a aglomeração não transbordar no apron. Só existe nos dois desenhos com baias ({num(V['barreira_por_componente_m'].get('fechamento das baias de flanco',0),1)} m).</td>
        <td><strong>Some junto com as baias.</strong> Nos desenhos sem baias, o item nem existe.</td></tr>
      <tr><td><span class="pin" style="color:#b23b2e">▬</span> Raias do apron</td>
        <td class="mono num">{num(VS['barreira_por_componente_m']['raias do apron até as portas'],1)} m<span class="sub">{math.ceil(VS['barreira_por_componente_m']['raias do apron até as portas']/P['separador_m'])} sep.</span></td>
        <td>Mantêm as três correntes separadas nos 14 m entre o gradil do Ring e a porta — o trecho onde elas convergem e podem se misturar.</td>
        <td><strong>É o candidato mais óbvio.</strong> Cerca de 45 separadores que podem virar marcação no chão mais fiscal, com o risco de troca de fila bem na soleira. No desenho girado, a corrente de B já sai perpendicular e nem precisaria de raia.</td></tr>
      <tr><td><span class="pin" style="color:#8a919b">┄</span> Gradil do Ring</td>
        <td class="mono num">0</td>
        <td>Fecha o compound inteiro e serve de lado oeste da zona A e de lado leste da zona C nos desenhos sem baias.</td>
        <td><strong>Já é de graça</strong> — desde que a organizadora confirme que ele fica montado e íntegro no dia.</td></tr>
    </tbody>
    <caption>Metragens da coluna do desenho pedido (N–S sem baias). A leitura vale para os quatro:
    muda a proporção, não a função de cada componente.</caption>
  </table></div>
  <p class="nota"><strong>O piso da conta.</strong> Corredor de fundo e raias do apron somam
  {num(VS['barreira_por_componente_m']['corredor de fundo (parede norte)'] + VS['barreira_por_componente_m']['raias do apron até as portas'],1)} m —
  {math.ceil((VS['barreira_por_componente_m']['corredor de fundo (parede norte)'] + VS['barreira_por_componente_m']['raias do apron até as portas'])/P['separador_m'])} separadores — antes
  da primeira raia de fila, em qualquer dos quatro desenhos. Tudo o que passa disso é fila: perímetro
  e divisórias crescem juntos com a lotação.</p>
</section>

<section>
  <p class="rotulo">Descarga</p>
  <h2>Por que a horizontal acerta a porta e a vertical não</h2>
  <div class="prosa">
  <p>É topologia de barreira, não escolha. Na <strong>vertical</strong> as divisórias correm
  norte-sul e as meias-voltas abrem a borda norte de duas em duas raias: a fila só sai pelo fim da
  última raia, num dos dois cantos do bloco — dá para escolher o canto mais perto da porta, e
  acaba aí. Na <strong>horizontal</strong> a última raia corre rente à borda norte, que é barreira
  contínua: o portão pode ser aberto em qualquer ponto dela, e vai para o eixo da porta.</p>
  </div>
  <div class="rolagem"><table>
    <thead><tr><th>Zona</th><th class="num">N–S com baias</th><th class="num">N–S sem baias</th>
    <th class="num">L–O com baias</th><th class="num">L–O sem baias</th></tr></thead>
    <tbody>{desvio_tab}</tbody>
    <caption>Desvio lateral entre o ponto de descarga da zona e o eixo da sua porta, no apron.
    O caso que separa os desenhos é o da zona B: girada, ela descarrega em cima de S5.</caption>
  </table></div>
</section>

<section>
  <p class="rotulo">Dimensionamento</p>
  <h2>Quanta barreira comprar</h2>
  <div class="prosa">
  <p>O estoque da organizadora é de {P['estoque_separadores']} separadores
  ({num(P['estoque_separadores']*P['separador_m'])} m) e o que faltar pode ser adquirido. Nenhum
  dos quatro desenhos cabe no estoque: corredor de fundo, raias do apron e funil da garganta
  consomem sozinhos {num(fixa,1)} m — {math.ceil(fixa/P['separador_m'])} separadores — antes da
  primeira raia de fila.</p>
  <p>No desenho pedido a alavanca é a <strong>profundidade da raia</strong>: encurtá-la não mexe na
  largura das zonas, no número de raias nem na descarga.</p>
  </div>
  <div class="rolagem"><table>
    <thead><tr><th class="num">Profundidade</th><th class="num">Lotação</th><th class="num">A</th>
    <th class="num">B</th><th class="num">C</th><th class="num">Separadores</th>
    <th class="num">A comprar</th><th class="num">Custo</th></tr></thead>
    <tbody>{escada_v_tab}</tbody>
    <caption>Linha destacada: a faixa inteira de {num(P['profundidade_serpenteado_m'],2)} m do
    o Ring inteiro acima do corredor.</caption>
  </table></div>
  {"<p class='nota'>Dentro dos " + str(PV['separadores']) + " separadores do plano vigente reconstruído cabem " + num(cabe_v[-1]['profundidade_m'],1) + " m de raia, com " + num(cabe_v[-1]['capacidade']) + " pessoas — ainda " + num(cabe_v[-1]['capacidade']-PV['capacidade_raias']) + " a mais de <strong>fila medida</strong> que o plano vigente, que tem " + num(PV['capacidade_raias']) + " em raia e " + num(PV['capacidade_baias']) + " em baia.</p>" if cabe_v else ""}
  <h3 style="margin-top:34px">No desenho girado sem baias, a alavanca é o número de raias</h3>
  <div class="rolagem"><table>
    <thead><tr><th class="num">Raias por zona</th><th class="num">Profundidade</th>
    <th class="num">Lotação</th><th class="num">Separadores</th><th class="num">A comprar</th></tr></thead>
    <tbody>{escada_h_tab}</tbody>
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
  regra deste modelo <strong>nos quatro desenhos</strong>. Ancorando nos 300 separadores publicados
  em vez dos {PV['separadores']} recalculados, o desenho pedido daria cerca de
  <strong>{round(300*VS['separadores']/PV['separadores'])} unidades</strong>.</p>
  <div class="rolagem"><table>
    <thead><tr><th>Premissa</th><th class="num">Valor</th><th>Origem</th></tr></thead>
    <tbody>
      <tr><td>Módulo da raia</td><td class="mono num">{num(P['passo_raia_m'],2)} m</td><td>reconstruído dos blocos de 4,2 e 12,6 m</td></tr>
      <tr><td>Largura livre da raia</td><td class="mono num">{num(P['raia_util_m'],2)} m</td><td>reconstruído</td></tr>
      <tr><td>Densidade em raia</td><td class="mono num">{num(P['densidade_fila_p_m2'],1)} p/m²</td><td>reconstruído</td></tr>
      <tr><td>Densidade em baia</td><td class="mono num">{num(P['densidade_baia_p_m2'],1)} p/m²</td><td>reconstruído</td></tr>
      <tr><td>Vão de meia-volta</td><td class="mono num">{num(P['vao_retorno_m'],1)} m</td><td>premissa</td></tr>
      <tr><td>Profundidade da raia</td><td class="mono num">{num(P['profundidade_serpenteado_m'],2)} m</td><td>Ring (35,00 m) menos o corredor de fundo</td></tr>
      <tr><td>Separador de fila</td><td class="mono num">{num(P['separador_m'],1)} m · EUR {num(P['separador_eur'],2)}</td><td>item d do orçamento (100 un. = EUR 1.303)</td></tr>
      <tr><td>Estoque da organizadora</td><td class="mono num">{P['estoque_separadores']} un. · {num(P['estoque_separadores']*P['separador_m'])} m</td><td>informado pelo Posto</td></tr>
    </tbody>
  </table></div>
</section>

<section>
  <p class="rotulo">Antes de contratar</p>
  <h2>O que decidir</h2>
  <ol class="pend">
    <li><div><h3>Onde o Ring começa</h3><p>A largura é medida — {num(D['ring']['x1']-D['ring']['x0'],1)} m
    oficiais —, mas a posição lateral do retângulo ainda é estimativa: ele está centrado no eixo de
    S5. Se o bordo oeste real estiver deslocado, as três zonas andam com ele e as diagonais de
    descarga mudam; o número de raias ({raias_vs} nesta configuração) não muda.</p></div></li>
    <li><div><h3>A compra dos separadores</h3><p>O desenho pedido precisa de {VS['compra']} unidades
    além das {P['estoque_separadores']} da organizadora, EUR {num(VS['custo_compra_eur'],2)}. A
    escada de profundidade é o que dá para recuar sem mexer no resto do desenho.</p></div></li>
    <li><div><h3>Onde a pré-triagem acontece agora</h3><p>A faixa da garganta saiu do Ring: a
    entrega do cartão de roteamento tem de migrar para o percurso a montante — o portão da Merrion
    Road e o corredor da lateral leste — ou para o próprio corredor de fundo, que passa a ser a
    única área de manobra dentro do Ring. Sem isso, a triagem vira um ponto de parada dentro de uma
    fila já formada.</p></div></li>
    <li><div><h3>Os vãos entre as zonas como rota de escape</h3><p>O desenho conta com
    {num(folga,2)} m de vão livre entre zonas e com a remoção rápida das barreiras laterais. Vale
    confirmar com quem assina o plano de evacuação do RDS antes de fechar.</p></div></li>
    <li><div><h3>As densidades</h3><p>{num(P['densidade_fila_p_m2'],1)} pessoas/m² em raia e
    {num(P['densidade_baia_p_m2'],1)} em baia são reconstrução, não medição. Se a densidade real sob
    guarda-chuva for menor, os quatro desenhos perdem na mesma proporção e a comparação não
    muda.</p></div></li>
  </ol>
</section>

<footer>
  <p>Geometria do salão e das portas de <span class="mono">scripts/salao.py</span>; comparecimento
  esperado e papéis das portas das decisões do Posto de 06/09/2026. Modelo, plantas e todos os
  números desta página gerados por <span class="mono">scripts/ring3.py</span> e
  <span class="mono">scripts/gera_pagina_ring3.py</span>.</p>
  <p>Plantas em escala real sobre o contorno medido do Hall 2 (50,3 × 44,4 m) e o retângulo do
  Ring 3 ({num(D['ring']['x1']-D['ring']['x0'],1)} × {num(D['ring']['y1']-D['ring']['y0'],1)} m
  medidos, apron de 14 m). Números de lotação são estimativa, não limite de segurança
  homologado.</p>
</footer>
</div>
"""

destino = os.path.join(SAIDAS, "ring3_horizontal.html")
with open(destino, "w", encoding="utf-8") as f:
    f.write(HTML)
print("gravado:", destino, f"({len(HTML)/1024:.1f} KB)")
