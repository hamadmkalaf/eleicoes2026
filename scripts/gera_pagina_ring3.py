#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Monta a pagina dos dois desenhos do Ring 3 a partir de saidas/ring3.json.

Todo numero da pagina vem do JSON que scripts/ring3.py gerou: a pagina nao
guarda nenhuma conta propria. Saida: saidas/ring3_horizontal.html
"""

import json
import math
import os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAIDAS = os.path.join(RAIZ, "saidas")

D = json.load(open(os.path.join(SAIDAS, "ring3.json"), encoding="utf-8"))
VS, H, PV = D["vertical_sem_baias"], D["girado"], D["plano_vigente_reconstruido"]
VP, HP = D["vertical_ccb_na_ponta"], D["girado_ccb_na_ponta"]
AP = VP["apoios_da_fita"]
ESCADA_V, ESCADA_H = D["escada_de_profundidade"], D["escada_de_raias"]
P, CONF = D["premissas"], D["aderencia_ao_plano_original"]
ESP = P["comparecimento_esperado"]
PORTA = {"A": "S4", "B": "S5", "C": "S6"}
ENTRADAS = ("A", "B", "C")
LARG_RING = D["ring"]["x1"] - D["ring"]["x0"]
PROF_RING = D["ring"]["y1"] - D["ring"]["y0"]
UTIL = LARG_RING - P["largura_corredor_m"]

DOIS = [("Raias norte-sul", VS, "ring3_vertical_sem_baias.svg"),
        ("Raias leste-oeste", H, "ring3_girado.svg")]


def num(v, casas=0):
    return f"{v:,.{casas}f}".replace(",", "@").replace(".", ",").replace("@", ".")


def sep(m):
    return math.ceil(m / P["separador_m"])


def zona(d, e):
    return next(z for z in d["zonas"] if z["entrada"] == e)


def svg(nome):
    s = open(os.path.join(SAIDAS, nome), encoding="utf-8").read()
    s = s.replace('fill="#fbfaf7"', 'fill="var(--prancha)"', 1)
    s = s.replace(' width="', ' data-w="', 1).replace(' height="', ' data-h="', 1)
    return s.replace("<svg ", '<svg class="planta" ', 1)


def linha(rot, valor, destaque=False):
    tds = "".join(f'<td class="mono num">{valor(d)}</td>' for _, d, _ in DOIS)
    return f'<tr{" class=total" if destaque else ""}><td>{rot}</td>{tds}</tr>'


COMP = [("Divisórias entre as raias", "divisórias entre as raias"),
        ("Separação da zona C / corredor", "separação entre a zona C e o corredor")]

comp_tab = "\n".join(
    linha(rot, lambda d, c=ch: num(d["barreira_por_componente_m"].get(c, 0), 1) + " m")
    for rot, ch in COMP) + "\n" + "\n".join([
    linha("Barreira total", lambda d: num(d["barreira_m"], 1) + " m", True),
    linha("Separadores de 2 m", lambda d: num(d["separadores"]), True),
    linha(f"A comprar (estoque {P['estoque_separadores']})", lambda d: num(d["compra"])),
    linha("Custo da compra", lambda d: "EUR " + num(d["custo_compra_eur"], 2)),
])

dois_tab = "\n".join([
    linha("Lotação — toda em raia medida", lambda d: num(d["capacidade"]), True),
    linha("Raias por zona", lambda d: "/".join(str(z["raias"]) for z in d["zonas"])),
    linha("Raia", lambda d: num(min(z["comprimento_raia_m"] for z in d["zonas"]), 1)
          + "–" + num(max(z["comprimento_raia_m"] for z in d["zonas"]), 1) + " m"),
    linha("Meias-voltas", lambda d: num(d["meias_voltas"])),
    linha("Caminhada máxima", lambda d: num(max(z["caminhada_m"] for z in d["zonas"])) + " m"),
    linha("Separadores", lambda d: num(d["separadores"])),
    linha("Metros por pessoa", lambda d: num(d["m_por_pessoa"], 3)),
])

desvio_tab = "\n".join(
    f'<tr><td><span class="pin {e.lower()}">{e}</span> {PORTA[e]}</td>' + "".join(
        f'<td class="mono num{" ganho" if zona(d,e)["desvio_lateral_m"] < 0.01 else ""}">'
        f'{num(zona(d,e)["desvio_lateral_m"],2)} m</td>' for _, d, _ in DOIS) +
    "</tr>" for e in ENTRADAS)

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

plantas = "\n".join(
    f'<figure><div class="prancha">{svg(arq)}</div>'
    f'<figcaption><b>{rot}.</b> {num(d["capacidade"])} pessoas · '
    f'{d["separadores"]} separadores · {num(d["meias_voltas"])} meias-voltas'
    f'</figcaption></figure>' for rot, d, arq in DOIS)

mapas_ponta = "\n".join(
    f'<figure><div class="prancha">{svg(arq)}</div>'
    f'<figcaption><b>{rot}.</b> {d["separadores"]} separadores · '
    f'{num(d["fita_grossa_m"],0)} m de fita grossa</figcaption></figure>'
    for rot, d, arq in (("Raias norte-sul", VP, "ring3_barreiras_vertical_ponta.svg"),
                        ("Raias leste-oeste", HP, "ring3_barreiras_girado_ponta.svg")))

mapas = "\n".join(
    f'<figure><div class="prancha">{svg(arq.replace("ring3_", "ring3_barreiras_"))}</div>'
    f'<figcaption><b>{rot}.</b> o que é separador, o que é fita, o que já existe'
    f'</figcaption></figure>' for rot, d, arq in DOIS)

escada_v_tab = "\n".join(
    '<tr{cls}><td class="mono num">{prof} m</td><td class="mono num">{cap}</td>'
    '<td class="mono num">{s}</td><td class="mono num">{c}</td>'
    '<td class="mono num">EUR {e}</td></tr>'.format(
        cls=' class="marcada"' if abs(r["profundidade_m"] - P["profundidade_serpenteado_m"]) < 0.01 else "",
        prof=num(r["profundidade_m"], 2), cap=num(r["capacidade"]),
        s=r["separadores"], c=r["compra"], e=num(r["custo_compra_eur"], 2))
    for r in ESCADA_V)

escada_h_tab = "\n".join(
    '<tr{cls}><td class="mono num">{r}</td><td class="mono num">{prof} m</td>'
    '<td class="mono num">{cap}</td><td class="mono num">{s}</td>'
    '<td class="mono num">{c}</td></tr>'.format(
        cls=' class="marcada"' if l["raias_por_zona"] == H["zonas"][0]["raias"] else "",
        r=l["raias_por_zona"], prof=num(l["profundidade_m"], 1),
        cap=num(l["capacidade"]), s=l["separadores"], c=l["compra"])
    for l in ESCADA_H)

sem_compra = [r for r in ESCADA_V if r["compra"] == 0]
FORA = VS["fora_da_conta"]
retirado = sum(FORA.values())

HTML = f"""<title>Ring 3, cenários de fila</title>
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

<div class="folha">
<header>
  <p class="olho">Eleições 2026 · 1º turno · 4 de outubro · RDS Ballsbridge · fila externa</p>
  <h1>Ring 3, cenários de fila</h1>
  <p class="chamada">O eleitor entra pelo canto nordeste, desce rente ao gradil leste e vira no
  fundo: o corredor de chegada é um L. As três zonas são alimentadas pelo trecho de fundo e
  descarregam ao norte em S4, S5 e S6. Só duas coisas são separador — as divisórias das raias e a
  parede que separa a zona C da corrente que desce.</p>
  <dl class="faixa">
    <div><dt>Ring</dt><dd>{num(LARG_RING,0)} × {num(PROF_RING,0)} m<small>medida oficial · {num(UTIL,1)} m úteis para as zonas</small></dd></div>
    <div><dt>Separadores</dt><dd class="delta">{VS['separadores']}<small>{num(VS['barreira_por_componente_m']['divisórias entre as raias'],0)} m de divisória + {num(VS['barreira_por_componente_m']['separação entre a zona C e o corredor'],0)} m na zona C</small></dd></div>
    <div><dt>A comprar</dt><dd>{VS['compra']}<small>sobre os {P['estoque_separadores']} da organizadora · EUR {num(VS['custo_compra_eur'],0)}</small></dd></div>
    <div><dt>Fora da conta</dt><dd class="ganho">−{sep(retirado)}<small>{num(retirado,0)} m que saíram por decisão do Posto</small></dd></div>
    <div><dt>CCB só na ponta</dt><dd class="ganho">{VP['separadores']}<small>cenário 3 · {num(VP['fita_grossa_m'],0)} m de fita grossa</small></dd></div>
  </dl>
</header>

<section>
  <p class="rotulo">O percurso</p>
  <h2>Entrada pelo canto nordeste, corredor em L</h2>
  <div class="prosa">
  <p>A entrada não é pelo fundo. O eleitor entra pelo <strong>canto nordeste</strong> do Ring — o
  lado mais perto da porta C —, desce rente ao gradil leste e vira no fundo. O corredor de chegada
  é um <strong>L</strong>: um trecho lateral a leste e um trecho de fundo ao sul, ambos de
  {num(P['largura_corredor_m'],1)} m. As zonas são alimentadas pelo trecho de fundo.</p>
  <p>Duas consequências, uma de área e outra de barreira. O trecho lateral consome
  {num(P['largura_corredor_m'],1)} m da largura: sobram <strong>{num(UTIL,1)} m</strong> para as
  três zonas, não os {num(LARG_RING,0)} m inteiros. E a zona C fica encostada nesse trecho, com a
  fila parada de um lado e a corrente que desce do outro — <strong>é a única contenção de verdade
  que o desenho ainda pede</strong>, e o único separador fora das divisórias.</p>
  </div>
  <div class="plantas">{plantas}</div>
</section>

<section>
  <p class="rotulo">A conta</p>
  <h2>O que ainda é separador</h2>
  <div class="prosa">
  <p>Três itens que o modelo contava saíram por decisão do Posto. Ficam registrados com a metragem
  que tinham — para dar o tamanho do que se está abrindo mão, e para a conta voltar a fechar se
  alguma dessas decisões mudar.</p>
  </div>
  <div class="rolagem"><table>
    <thead><tr><th>Item retirado</th><th>Por quê</th><th class="num">Quanto era</th><th class="num">Separadores</th></tr></thead>
    <tbody>
      <tr><td>Contorno das zonas</td><td>O gradil já fecha o compound; entre zonas, a delimitação é <strong>fita</strong></td><td class="mono num">{num(FORA['contorno das zonas (hoje, fita)'],1)} m</td><td class="mono num ganho">−{sep(FORA['contorno das zonas (hoje, fita)'])}</td></tr>
      <tr><td>Parede do corredor de chegada</td><td>Fora da conta</td><td class="mono num">{num(FORA['parede do corredor de chegada'],1)} m</td><td class="mono num ganho">−{sep(FORA['parede do corredor de chegada'])}</td></tr>
      <tr><td>Raias do apron até as portas</td><td>Fora da conta</td><td class="mono num">{num(FORA['raias do apron até as portas'],1)} m</td><td class="mono num ganho">−{sep(FORA['raias do apron até as portas'])}</td></tr>
      <tr class="total"><td>Total retirado</td><td></td><td class="mono num">{num(retirado,1)} m</td><td class="mono num ganho">−{sep(retirado)}</td></tr>
    </tbody>
  </table></div>
  <div class="rolagem"><table>
    <thead><tr><th>Componente</th><th class="num">Raias N–S</th><th class="num">Raias L–O</th></tr></thead>
    <tbody>{comp_tab}</tbody>
    <caption>O que sobra são dois componentes. A fita de delimitação é outro material e outro
    fornecedor: {num(FORA['contorno das zonas (hoje, fita)'],1)} m no desenho N–S,
    {num(H['fora_da_conta']['contorno das zonas (hoje, fita)'],1)} m no girado.</caption>
  </table></div>
</section>

<section>
  <p class="rotulo">O mapa</p>
  <h2>Onde cada metro é gasto, e o que ele segura</h2>
  <div class="prosa">
  <p>Cada corrida que a conta soma está desenhada, colorida pelo componente — o mapa <em>é</em> a
  conta, gerado dos mesmos segmentos, e o script recusa a gerar a planta se os dois não fecharem.
  O gradil permanente aparece tracejado em cinza; o contorno das zonas, pontilhado em azul, é fita
  e não entra na conta.</p>
  </div>
  <div class="plantas">{mapas}</div>
  <div class="rolagem"><table>
    <thead><tr><th>Elemento</th><th class="num">N–S</th><th>O que segura</th></tr></thead>
    <tbody>
      <tr><td><span class="pin" style="color:#7a8794">▬</span> Divisórias entre as raias</td>
        <td class="mono num">{num(VS['barreira_por_componente_m']['divisórias entre as raias'],1)} m<span class="sub">{sep(VS['barreira_por_componente_m']['divisórias entre as raias'])} sep.</span></td>
        <td>São o serpenteado. Sem elas não há fila: há uma massa dentro de um retângulo cercado, sem ordem de chegada nem vazão previsível. É 96% da conta, e a única alavanca real é o comprimento da raia.</td></tr>
      <tr><td><span class="pin" style="color:#b23b2e">▬</span> Separação da zona C / corredor</td>
        <td class="mono num">{num(VS['barreira_por_componente_m']['separação entre a zona C e o corredor'],1)} m<span class="sub">{sep(VS['barreira_por_componente_m']['separação entre a zona C e o corredor'])} sep.</span></td>
        <td>De um lado a fila parada da zona C, do outro a corrente que desce do canto nordeste para o fundo. Dois fluxos em sentidos diferentes, encostados: fita não segura isso.</td></tr>
      <tr><td><span class="pin" style="color:#1f6fb2">┈</span> Contorno das zonas</td>
        <td class="mono num">{num(FORA['contorno das zonas (hoje, fita)'],1)} m<span class="sub">fita</span></td>
        <td>Delimita, não contém. Enquanto a fila está ordenada, resolve; num pico, nada impede fisicamente a passagem de uma zona para a outra.</td></tr>
      <tr><td><span class="pin" style="color:#8a919b">┄</span> Gradil do Ring</td>
        <td class="mono num">0</td>
        <td>Fecha o compound inteiro e serve de lado oeste da zona A e de parede externa do corredor. Já existe.</td></tr>
    </tbody>
  </table></div>
</section>

<section>
  <p class="rotulo">Os dois desenhos</p>
  <h2>Norte-sul ou leste-oeste</h2>
  <div class="rolagem"><table>
    <thead><tr><th></th><th class="num">Raias N–S</th><th class="num">Raias L–O</th></tr></thead>
    <tbody>{dois_tab}</tbody>
  </table></div>
  <div class="prosa" style="margin-top:22px">
  <p>Na barreira os dois empatam: com o contorno fora da conta, o que sobra são as divisórias, e
  elas mudam <span class="mono">0,14 × (profundidade − largura)</span> por zona — ruído. O que
  separa os dois é a <strong>descarga</strong>. Na horizontal a última raia corre rente à borda
  norte, que é linha contínua, e o portão vai para o eixo da porta; na vertical a fila sai pelo fim
  da última raia, num canto do bloco.</p>
  </div>
  <div class="rolagem"><table>
    <thead><tr><th>Zona</th><th class="num">Desvio · N–S</th><th class="num">Desvio · L–O</th></tr></thead>
    <tbody>{desvio_tab}</tbody>
    <caption>Distância lateral entre o ponto de descarga da zona e o eixo da sua porta, no apron —
    que agora se atravessa sem raias de barreira.</caption>
  </table></div>
  <div class="rolagem"><table>
    <thead><tr><th>Zona</th><th class="num">Largura</th><th class="num">Raias</th>
    <th class="num">Raia</th><th class="num">Caminhada</th><th class="num">Lotação</th>
    <th class="num">Esperado</th><th class="num">por eleitor</th></tr></thead>
    <tbody>{zonas_tab}</tbody>
    <caption>Desenho norte-sul, zona a zona. A largura sai da lotação que cada entrada precisa, não
    da largura disponível.</caption>
  </table></div>
</section>

<section>
  <p class="rotulo">Cenário 3</p>
  <h2>CCB só na ponta, fita grossa no resto</h2>
  <div class="prosa">
  <p>A divisória deixa de ser barreira de ponta a ponta. Vira <strong>fita grossa</strong> — do
  tipo que a polícia usa para isolar — ancorada por <strong>um único CCB na ponta livre</strong>,
  no vão da meia-volta, que é por onde a pessoa passa e onde a fila empurra. A separação da zona C
  continua sendo barreira inteira: ali são dois fluxos encostados, e fita não segura isso.</p>
  </div>
  <div class="rolagem"><table>
    <thead><tr><th></th><th class="num">N–S · barreira inteira</th><th class="num">N–S · CCB na ponta</th><th class="num">L–O · CCB na ponta</th></tr></thead>
    <tbody>
      <tr><td>Divisórias (uma por vão de raia)</td><td class="mono num">{VS['meias_voltas']}</td><td class="mono num">{VP['n_divisorias']}</td><td class="mono num">{HP['n_divisorias']}</td></tr>
      <tr><td>Barreira</td><td class="mono num">{num(VS['barreira_m'],1)} m</td><td class="mono num">{num(VP['barreira_m'],1)} m</td><td class="mono num">{num(HP['barreira_m'],1)} m</td></tr>
      <tr class="total"><td>Separadores</td><td class="mono num">{VS['separadores']}</td><td class="mono num ganho">{VP['separadores']}</td><td class="mono num">{HP['separadores']}</td></tr>
      <tr><td>A comprar (estoque {P['estoque_separadores']})</td><td class="mono num">{VS['compra']}</td><td class="mono num ganho">{VP['compra']}</td><td class="mono num">{HP['compra']}</td></tr>
      <tr><td>Fita grossa</td><td class="mono num">—</td><td class="mono num">{num(VP['fita_grossa_m'],1)} m</td><td class="mono num">{num(HP['fita_grossa_m'],1)} m</td></tr>
      <tr><td>Lotação</td><td class="mono num">{num(VS['capacidade'])}</td><td class="mono num">{num(VP['capacidade'])}</td><td class="mono num">{num(HP['capacidade'])}</td></tr>
    </tbody>
    <caption>A lotação não muda: as raias são as mesmas, só o material que as separa é outro.</caption>
  </table></div>
  <p class="nota"><strong>A inversão.</strong> A barreira deixa de ser proporcional ao
  <em>comprimento</em> da raia e passa a ser proporcional ao <em>número</em> de raias. Por isso o
  girado, com {HP['n_divisorias']} divisórias curtas, custa mais ({HP['separadores']}) que o N–S com
  {VP['n_divisorias']} longas ({VP['separadores']}) — o contrário do que acontecia antes.</p>
  <div class="plantas">{mapas_ponta}</div>

  <h3 style="margin-top:34px">O que a fita pede, e o modelo não cobra</h3>
  <div class="prosa">
  <p>Cada divisória do desenho N–S fica com <strong>{num(AP['vao_livre_m'],1)} m de vão livre</strong>
  depois do CCB da ponta. Fita não se sustenta nesse vão: ela cede, e uma fila encostada atravessa.
  Mantendo o vão em {num(AP['espacamento_m'],0)} m, seriam <strong>{AP['apoios_por_divisoria']}
  apoios por divisória</strong>, {AP['apoios']} no total.</p>
  </div>
  <div class="rolagem"><table>
    <thead><tr><th>Se o apoio for…</th><th>Consequência</th></tr></thead>
    <tbody>
      <tr><td>Um CCB</td><td class="mono">{AP['separadores_se_forem_ccb']} separadores no total — {AP['separadores_se_forem_ccb']-P['estoque_separadores']} além do estoque; ainda bem abaixo dos {VS['separadores']} do regime inteiro, mas {AP['separadores_se_forem_ccb']//VP['separadores']}× o do cenário como pedido</td></tr>
      <tr><td>Um poste leve com base</td><td>Outro item de orçamento, mais barato e mais leve: {AP['apoios']} postes</td></tr>
      <tr><td>Nada</td><td>A fita cede entre as pontas e a raia deixa de existir na prática, justamente quando a fila enche</td></tr>
    </tbody>
  </table></div>
  <p class="nota"><strong>A decisão não é entre fita e barreira — é sobre quantos apoios a fita vai
  ter.</strong> O número de CCB cai de verdade só se os apoios intermediários forem outro
  material.</p>
</section>

<section>
  <p class="rotulo">Dimensionamento</p>
  <h2>Quanta barreira comprar</h2>
  <div class="prosa">
  <p>O estoque da organizadora é de {P['estoque_separadores']} separadores
  ({num(P['estoque_separadores']*P['separador_m'])} m) e o que faltar pode ser adquirido. Com a
  conta reduzida às divisórias, a alavanca é o comprimento da raia — no N–S, a profundidade; no
  girado, o número de raias.</p>
  </div>
  <div class="rolagem"><table>
    <thead><tr><th class="num">Profundidade</th><th class="num">Lotação</th>
    <th class="num">Separadores</th><th class="num">A comprar</th><th class="num">Custo</th></tr></thead>
    <tbody>{escada_v_tab}</tbody>
    <caption>Desenho norte-sul. Linha destacada: a faixa inteira, do corredor de fundo à borda
    norte do Ring.</caption>
  </table></div>
  {"<p class='nota'><strong>Dentro do estoque, sem comprar nada:</strong> " + num(sem_compra[-1]['profundidade_m'],1) + " m de raia, " + num(sem_compra[-1]['capacidade']) + " pessoas — " + num(sem_compra[-1]['capacidade']-PV['capacidade']) + " a mais que o plano vigente inteiro, que tinha " + num(PV['capacidade']) + " com 314 separadores.</p>" if sem_compra else ""}
  <div class="rolagem"><table>
    <thead><tr><th class="num">Raias por zona</th><th class="num">Profundidade</th>
    <th class="num">Lotação</th><th class="num">Separadores</th><th class="num">A comprar</th></tr></thead>
    <tbody>{escada_h_tab}</tbody>
    <caption>Desenho leste-oeste.</caption>
  </table></div>
</section>

<section>
  <p class="rotulo">Método</p>
  <h2>Premissas, e o que se sabe do plano vigente</h2>
  <div class="rolagem"><table>
    <thead><tr><th>Premissa</th><th class="num">Valor</th><th>Origem</th></tr></thead>
    <tbody>
      <tr><td>Ring</td><td class="mono num">{num(LARG_RING,1)} × {num(PROF_RING,1)} m</td><td>medida oficial</td></tr>
      <tr><td>Corredor de chegada</td><td class="mono num">{num(P['largura_corredor_m'],1)} m</td><td>em L (leste + fundo), decisão do Posto</td></tr>
      <tr><td>Profundidade da raia</td><td class="mono num">{num(P['profundidade_serpenteado_m'],2)} m</td><td>Ring menos o corredor de fundo</td></tr>
      <tr><td>Módulo da raia</td><td class="mono num">{num(P['passo_raia_m'],2)} m</td><td>reconstruído dos blocos de 4,2 e 12,6 m</td></tr>
      <tr><td>Largura livre da raia</td><td class="mono num">{num(P['raia_util_m'],2)} m</td><td>reconstruído</td></tr>
      <tr><td>Densidade em raia</td><td class="mono num">{num(P['densidade_fila_p_m2'],1)} p/m²</td><td>reconstruído</td></tr>
      <tr><td>Vão de meia-volta</td><td class="mono num">{num(P['vao_retorno_m'],1)} m</td><td>premissa</td></tr>
      <tr><td>Separador de fila</td><td class="mono num">{num(P['separador_m'],1)} m · EUR {num(P['separador_eur'],2)}</td><td>item d do orçamento</td></tr>
      <tr><td>Estoque da organizadora</td><td class="mono num">{P['estoque_separadores']} un.</td><td>informado pelo Posto</td></tr>
    </tbody>
  </table></div>
  <p class="nota">O plano vigente (<span class="mono">scripts/layout_ring3.py</span>,
  <span class="mono">saidas/plano_ring3.md</span>) não está no repositório — foi produzido em sessão
  anterior e não chegou a ser versionado. Reconstruído das cotas publicadas, ele continua servindo
  de aferição do modelo de densidade: {num(CONF['raias_calculado'],1)} contra
  {num(CONF['raias_publicado'])} publicados nos serpenteados, {num(CONF['baias_calculado'],1)}
  contra {num(CONF['baias_publicado'])} nas baias.</p>
</section>

<section>
  <p class="rotulo">Antes de contratar</p>
  <h2>O que decidir</h2>
  <ol class="pend">
    <li><div><h3>Fita delimita, não contém</h3><p>A decisão de marcar as zonas com fita vale
    enquanto a fila estiver ordenada. Num pico, nada impede fisicamente alguém de passar da zona A
    para a B — e a separação por porta, que é a razão de existir da pré-triagem, depende disso.
    Vale decidir se algum trecho volta a ser barreira, sobretudo junto às cabeças de fila, onde a
    pressão é maior.</p></div></li>
    <li><div><h3>A corrente que desce e a saída S8</h3><p>A entrada pelo canto nordeste cruza o
    apron a leste, que é onde S8 despeja quem já votou. Sem raias no apron, os dois fluxos dividem
    o mesmo espaço — resolver com sinalização, fiscal ou separação no tempo.</p></div></li>
    <li><div><h3>A largura do trecho lateral</h3><p>Os {num(P['largura_corredor_m'],1)} m assumidos
    vêm do corredor de fundo. Se a corrente de entrada pedir mais, cada metro sai da largura das
    zonas — e no desenho N–S tirar 1,4 m tira uma raia inteira.</p></div></li>
    <li><div><h3>Onde a pré-triagem acontece</h3><p>Continua sem endereço dentro do Ring: o
    corredor em L é de passagem, não de parada. A entrega do cartão de roteamento precisa acontecer
    a montante — no portão da Merrion Road ou no corredor da lateral leste do Hall.</p></div></li>
  </ol>
</section>

<footer>
  <p>Geometria do salão e das portas de <span class="mono">scripts/salao.py</span>; comparecimento
  esperado e papéis das portas das decisões do Posto de 06/09/2026. Modelo, plantas e todos os
  números desta página gerados por <span class="mono">scripts/ring3.py</span> e
  <span class="mono">scripts/gera_pagina_ring3.py</span>.</p>
  <p>Plantas em escala real sobre o contorno medido do Hall 2 (50,3 × 44,4 m) e o retângulo do
  Ring 3 ({num(LARG_RING,1)} × {num(PROF_RING,1)} m medidos, apron de 14 m). Números de lotação são
  estimativa, não limite de segurança homologado.</p>
</footer>
</div>
"""

destino = os.path.join(SAIDAS, "ring3_horizontal.html")
with open(destino, "w", encoding="utf-8") as f:
    f.write(HTML)
print("gravado:", destino, f"({len(HTML)/1024:.1f} KB)")
