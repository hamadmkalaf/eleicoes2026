# -*- coding: utf-8 -*-
"""Ring 3 — cenario 3 adaptado. O mapa e a conta: os mesmos segmentos geram SVG e BOM.

Revisao de 22/09/2026:
  * as tres zonas sao iguais (decisao do Posto de 18/09), 12,87 / 12,86 / 12,87 m;
  * a boca do fundo da zona A passa para o extremo OESTE, e o serpenteado dela
    corre invertido: a raia de cima descarrega no extremo leste, junto a S4;
  * a zona B descarrega no MEIO: a raia de cima e percorrida do leste ate o
    meio e sai; a metade oeste da raia fica fechada por uma CCB atravessada;
  * a face norte do gradil ganha quatro aberturas, com a cota de cada uma
    medida do canto nordeste (onde a corrente entra).
Escreve saidas/ring3_planta.svg e saidas/ring3_montagem.json.
"""
import json, math, os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------- premissas ----------
RING_W, RING_D = 44.0, 35.0
COR = 3.0                 # corredor em L
UTIL = RING_W - COR       # 41.0
PROF = RING_D - COR       # 32.0
VAO_ZONA = 1.20           # era 2.60
LANES, MOD = 23, PROF/23
TURN = 1.20               # vao de meia-volta
CCB = 2.00
DENS = 2.386              # p por metro de raia (calibrado no artefato anterior)
ESTOQUE = 200
LAT_N = 8.0               # trecho norte das laterais que vira CCB
ABERTURA = 2.00           # largura de cada saida na face norte (um painel)

# Zonas iguais (18/09). A e C levam 12,87; B absorve o arredondamento (12,86).
livre = UTIL - 2*VAO_ZONA                      # 38.60
W = {k: round(livre/3, 2) for k in ('A', 'B', 'C')}
W['B'] = round(livre - W['A'] - W['C'], 2)
assert abs(W['A']+W['B']+W['C'] - livre) < 1e-9, (W, livre)

x0 = {}
cur = 0.0
for k in ('A', 'B', 'C'):
    x0[k] = round(cur, 2)
    cur += W[k] + VAO_ZONA
assert abs(cur - VAO_ZONA - UTIL) < 1e-9, cur

# Eixos das portas do Hall 2 em coordenada do Ring (x_hall = x_ring + 6,28).
portas = {'A': 15.78, 'B': 22.00, 'C': 28.22}
VAO_PORTA = {'A': (12.82, 18.75), 'B': (19.04, 24.97), 'C': (25.26, 31.19)}

# Onde a corrente entra em cada zona (boca do fundo) e por onde a raia de cima
# sai. Com 23 raias (impar) a raia de cima e percorrida no sentido contrario
# ao da boca: boca a leste -> saida a oeste. A zona A inverte para descarregar
# junto a S4; a B para no meio porque S5 esta no meio dela.
BOCA_OESTE = {'A': True, 'B': False, 'C': False}
SAIDA_MEIO = {'B': True}

DIV = LANES - 1           # divisorias por zona
segs = []                 # (tipo, x1,y1, x2,y2)  tipo in ccb|ccb_novo|fita

def add(t, a, b, c, d): segs.append((t, a, b, c, d))

# divisorias: CCB na ponta livre + fita + CCB de apoio no meio da fita + fita.
# Divisoria i separa a raia i-1 (ao norte) da raia i (ao sul). `leste` diz de
# que lado fica o vao de meia-volta dela.
for k in ('A', 'B', 'C'):
    a, b = x0[k], x0[k] + W[k]
    for i in range(1, LANES):
        y = PROF*i/LANES
        leste = (i % 2 == 1) != BOCA_OESTE[k]
        p0, p1 = (a, b - TURN) if leste else (a + TURN, b)
        if leste:
            add('ccb', p1 - CCB, y, p1, y)          # ponta livre (leste)
            f0, f1 = p0, p1 - CCB
        else:
            add('ccb', p0, y, p0 + CCB, y)          # ponta livre (oeste)
            f0, f1 = p0 + CCB, p1
        Lf = f1 - f0
        s = (Lf - CCB)/2                            # vao de fita de cada lado
        add('fita', f0, y, f0 + s, y)
        add('ccb_novo', f0 + s, y, f0 + s + CCB, y)  # apoio intermediario
        add('fita', f0 + s + CCB, y, f1, y)

# parede zona C / corredor de chegada
add('ccb', UTIL, 0.0, UTIL, PROF)

# fechamento contra o trecho de fundo, com boca de entrada
bocas = {}          # largura real da boca
boca_x = {}         # (x1, x2) da boca do fundo
for k in ('A', 'B', 'C'):
    a, b = x0[k], x0[k] + W[k]
    n = math.floor((W[k] - 1.0)/CCB)
    bocas[k] = round(W[k] - n*CCB, 2)
    if BOCA_OESTE[k]:
        add('ccb_novo', b - n*CCB, PROF, b, PROF)   # boca no lado oeste
        boca_x[k] = (round(a, 2), round(b - n*CCB, 2))
    else:
        add('ccb_novo', a, PROF, a + n*CCB, PROF)   # boca no lado leste
        boca_x[k] = (round(a + n*CCB, 2), round(b, 2))

# laterais parciais, 8 m ao norte, nas duas faces de cada vao
for k in ('A', 'B'):
    xr = x0[k] + W[k]
    add('ccb_novo', xr, 0.0, xr, LAT_N)
    add('ccb_novo', xr + VAO_ZONA, 0.0, xr + VAO_ZONA, LAT_N)

# saidas na face norte: uma abertura de 2,00 m no gradil por zona
saidas = {}
for k in ('A', 'B', 'C'):
    a, b = x0[k], x0[k] + W[k]
    if SAIDA_MEIO.get(k):
        c = (a + b)/2
        saidas[k] = (round(c - ABERTURA/2, 2), round(c + ABERTURA/2, 2))
    elif BOCA_OESTE[k]:
        saidas[k] = (round(b - ABERTURA, 2), round(b, 2))   # raia de cima vai para leste
    else:
        saidas[k] = (round(a, 2), round(a + ABERTURA, 2))   # raia de cima vai para oeste

# batente: fecha a metade morta da raia de cima da zona B com uma CCB de 2,00 m
# atravessada na raia (a raia tem 1,39 m; o painel entra de vies).
morta = 0.0
for k in SAIDA_MEIO:
    xg = saidas[k][0]                              # borda oeste da abertura
    dx = math.sqrt(CCB**2 - MOD**2)
    add('ccb_novo', xg, 0.0, xg - dx, MOD)
    morta += xg - x0[k]                            # metros de raia que ficam sem uso

# ---------- a conta, derivada dos segmentos ----------
def comp(s): return math.hypot(s[3]-s[1], s[4]-s[2])
m_ccb  = sum(comp(s) for s in segs if s[0] == 'ccb')
m_novo = sum(comp(s) for s in segs if s[0] == 'ccb_novo')
m_fita = sum(comp(s) for s in segs if s[0] == 'fita')
n_ccb  = round((m_ccb + m_novo)/CCB)
assert abs((m_ccb+m_novo)/CCB - n_ccb) < 1e-6, (m_ccb+m_novo)

# quebra por item
it_ponta = DIV*3*CCB
it_apoio = DIV*3*CCB
it_par   = PROF
it_fundo = sum(math.floor((W[k]-1.0)/CCB)*CCB for k in W)
it_lat   = 4*LAT_N
it_bat   = CCB*len(SAIDA_MEIO)
assert abs(it_ponta + it_apoio + it_par + it_fundo + it_lat + it_bat - (m_ccb+m_novo)) < 1e-6

lane_m = LANES*sum(W.values()) - morta
lot = lane_m*DENS
vao_fita = {k: round(((W[k]-TURN) - 2*CCB)/2, 2) for k in W}

# desvio: do centro da abertura ao eixo da porta (negativo = a oeste do eixo)
desvio = {k: round((saidas[k][0]+saidas[k][1])/2 - portas[k], 2) for k in saidas}
dentro_do_vao = {k: VAO_PORTA[k][0] <= (saidas[k][0]+saidas[k][1])/2 <= VAO_PORTA[k][1]
                 for k in saidas}

# aberturas na face norte, na ordem em que aparecem a quem entra pelo canto NE
aberturas = [('corredor de chegada', UTIL, RING_W)] + [
    (f'saída da zona {k}', *saidas[k]) for k in ('C', 'B', 'A')]
tabela_aberturas = [{
    'abertura': nome, 'x_oeste': (round(a, 2), round(b, 2)),
    'do_canto_ne': (round(RING_W - b, 2), round(RING_W - a, 2)),
    'largura': round(b - a, 2)} for nome, a, b in aberturas]

print(f"larguras {W}  x0 {x0}")
print(f"bocas do fundo {bocas} em x {boca_x}")
print(f"saidas na face norte {saidas}")
for t in tabela_aberturas:
    print(f"  {t['abertura']:<20} x {t['x_oeste'][0]:6.2f}-{t['x_oeste'][1]:6.2f} m"
          f"  | do canto NE {t['do_canto_ne'][0]:6.2f}-{t['do_canto_ne'][1]:6.2f} m")
print(f"CCB: {n_ccb}  ({m_ccb:.1f} m ja na conta + {m_novo:.1f} m novos = {m_ccb+m_novo:.1f} m)")
print(f"  divisorias ponta {int(it_ponta/CCB)} | apoios {int(it_apoio/CCB)} | parede C {int(it_par/CCB)} "
      f"| fundo {int(it_fundo/CCB)} | laterais {int(it_lat/CCB)} | batente B {int(it_bat/CCB)}")
print(f"fita grossa {m_fita:.1f} m | vao maximo de fita {vao_fita}")
print(f"raia-metros {lane_m:.1f} (menos {morta:.2f} m mortos na B) | lotacao {lot:.0f} | percurso max {LANES*W['A']:.0f} m")
print(f"desvios ao eixo da porta {desvio} | dentro do vao {dentro_do_vao}")
print(f"compra {max(0, n_ccb-ESTOQUE)} | sobra {max(0, ESTOQUE-n_ccb)}")

json.dump({
    'revisao': '2026-09-22', 'ring': [RING_W, RING_D], 'corredor': COR, 'vao_zona': VAO_ZONA,
    'raias': LANES, 'modulo': round(MOD, 3), 'larguras': W, 'x0': x0,
    'boca_oeste': BOCA_OESTE, 'saida_meio': SAIDA_MEIO,
    'bocas_fundo': {k: {'largura': bocas[k], 'x': boca_x[k]} for k in bocas},
    'saidas_norte': {k: list(saidas[k]) for k in saidas},
    'aberturas_face_norte': tabela_aberturas,
    'portas_eixo': portas, 'desvio_ao_eixo': desvio, 'dentro_do_vao': dentro_do_vao,
    'ccb': {'total': n_ccb, 'ponta': int(it_ponta/CCB), 'apoio': int(it_apoio/CCB),
            'parede_c': int(it_par/CCB), 'fundo': int(it_fundo/CCB), 'laterais': int(it_lat/CCB),
            'batente_b': int(it_bat/CCB), 'metros': round(m_ccb+m_novo, 1),
            'estoque': ESTOQUE, 'compra': max(0, n_ccb-ESTOQUE), 'sobra': max(0, ESTOQUE-n_ccb)},
    'fita_m': round(m_fita, 1), 'vao_fita': vao_fita,
    'raia_metros': round(lane_m, 1), 'raia_morta_b': round(morta, 2), 'lotacao': round(lot),
    'percurso_max': round(LANES*max(W.values())),
}, open(os.path.join(RAIZ, 'saidas', 'ring3_montagem.json'), 'w', encoding='utf-8'),
    ensure_ascii=False, indent=1)

# ---------- SVG ----------
S = 15.0
MX, MT, MB = 58, 44, 74
APRON = 14.0
def X(m): return MX + m*S
def Y(m): return MT + (APRON + m)*S      # m medido do topo do Ring
Wpx = MX*2 + RING_W*S
Hpx = MT + (APRON + RING_D)*S + MB

o = []
def e(s): o.append(s)
e(f'<svg class="planta" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {Wpx:.0f} {Hpx:.0f}" role="img" '
  f'aria-label="Planta do Ring 3 no cenario 3 adaptado: tres zonas iguais de raias leste-oeste separadas por vaos de 1,2 m, '
  f'divisorias de fita grossa ancoradas por dois CCB cada, fechamento de fundo com boca de entrada (a oeste na zona A), '
  f'laterais rigidas nos 8 m ao norte e quatro aberturas na face norte do gradil: corredor de chegada e as saidas C, B e A.">')
e('<defs><marker id="pta" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker></defs>')

# apron
e(f'<rect x="{X(0):.1f}" y="{MT:.1f}" width="{RING_W*S:.1f}" height="{APRON*S:.1f}" fill="var(--apron)"/>')
e(f'<line x1="{MX-14:.1f}" y1="{MT:.1f}" x2="{Wpx-MX+14:.1f}" y2="{MT:.1f}" stroke="var(--tinta)" stroke-width="2.6"/>')
e(f'<text x="{Wpx/2:.1f}" y="{MT-13:.1f}" text-anchor="middle" font-size="11.5" font-weight="700" fill="var(--meio)" letter-spacing="1.4">FACHADA SUL DO HALL 2</text>')
e(f'<text x="{X(RING_W)+10:.1f}" y="{MT+APRON*S/2:.1f}" text-anchor="middle" font-size="10.5" fill="var(--fraco)" transform="rotate(-90 {X(RING_W)+10:.1f} {MT+APRON*S/2:.1f})">apron pavimentado · 14,0 m</text>')

cor_zona = {'A': 'var(--za)', 'B': 'var(--zb)', 'C': 'var(--zc)'}
for k, sx in (('A', 'S4'), ('B', 'S5'), ('C', 'S6')):
    c = portas[k]
    e(f'<line x1="{X(c-2.96):.1f}" y1="{MT:.1f}" x2="{X(c+2.96):.1f}" y2="{MT:.1f}" stroke="{cor_zona[k]}" stroke-width="6"/>')
    e(f'<text x="{X(c):.1f}" y="{MT+17:.1f}" text-anchor="middle" font-size="11.5" font-weight="700" fill="{cor_zona[k]}">{sx} · {k}</text>')
for c, lab in ((7.56, 'S2'), (36.44, 'S8')):
    e(f'<line x1="{X(c-0.6):.1f}" y1="{MT:.1f}" x2="{X(c+0.6):.1f}" y2="{MT:.1f}" stroke="var(--fraco)" stroke-width="6"/>')
    e(f'<text x="{X(c):.1f}" y="{MT+17:.1f}" text-anchor="middle" font-size="9.5" fill="var(--fraco)">{lab} saída</text>')

# gradil do Ring
e(f'<rect x="{X(0):.1f}" y="{Y(0):.1f}" width="{RING_W*S:.1f}" height="{RING_D*S:.1f}" fill="var(--folha)" stroke="var(--fraco)" stroke-width="2" stroke-dasharray="8 5"/>')
# corredor em L
e(f'<rect x="{X(UTIL):.1f}" y="{Y(0):.1f}" width="{COR*S:.1f}" height="{RING_D*S:.1f}" fill="var(--circ)"/>')
e(f'<rect x="{X(0):.1f}" y="{Y(PROF):.1f}" width="{UTIL*S:.1f}" height="{COR*S:.1f}" fill="var(--circ)"/>')
e(f'<text x="{X(UTIL+1.5):.1f}" y="{Y(11):.1f}" text-anchor="middle" font-size="10.5" font-weight="600" fill="var(--verde)" transform="rotate(-90 {X(UTIL+1.5):.1f} {Y(11):.1f})">CORREDOR DE CHEGADA · 3,0 m</text>')
e(f'<text x="{X(UTIL/2):.1f}" y="{Y(PROF+1.9):.1f}" text-anchor="middle" font-size="10.5" font-weight="600" fill="var(--verde)">TRECHO DE FUNDO · 3,0 m · lê C, depois B, depois A</text>')
# entrada
e(f'<line x1="{X(UTIL+1.5):.1f}" y1="{Y(0)-46:.1f}" x2="{X(UTIL+1.5):.1f}" y2="{Y(1.4):.1f}" stroke="var(--verde)" stroke-width="2.4" marker-end="url(#pta)"/>')
e(f'<text x="{X(UTIL+1.5)-9:.1f}" y="{Y(0)-34:.1f}" text-anchor="end" font-size="10" fill="var(--verde)">entrada · canto nordeste</text>')

# zonas + corredores entre zonas
for k in ('A', 'B', 'C'):
    e(f'<rect x="{X(x0[k]):.1f}" y="{Y(0):.1f}" width="{W[k]*S:.1f}" height="{PROF*S:.1f}" fill="{cor_zona[k]}" fill-opacity=".07"/>')
for k in ('A', 'B'):
    xr = x0[k] + W[k]
    e(f'<rect x="{X(xr):.1f}" y="{Y(0):.1f}" width="{VAO_ZONA*S:.1f}" height="{PROF*S:.1f}" fill="var(--circ)"/>')
# metade morta da raia de cima da B
for k in SAIDA_MEIO:
    e(f'<rect x="{X(x0[k]):.1f}" y="{Y(0):.1f}" width="{(saidas[k][0]-x0[k])*S:.1f}" height="{MOD*S:.1f}" fill="var(--fraco)" fill-opacity=".18"/>')

# aberturas na face norte: apaga o traco do gradil e marca
for nome, a, b in aberturas:
    e(f'<line x1="{X(a):.1f}" y1="{Y(0):.1f}" x2="{X(b):.1f}" y2="{Y(0):.1f}" stroke="var(--folha)" stroke-width="4"/>')
    e(f'<line x1="{X(a):.1f}" y1="{Y(0):.1f}" x2="{X(b):.1f}" y2="{Y(0):.1f}" stroke="var(--verde)" stroke-width="4"/>')

# segmentos
for t, a, b, c, d in segs:
    if t == 'fita':
        e(f'<line x1="{X(a):.1f}" y1="{Y(b):.1f}" x2="{X(c):.1f}" y2="{Y(d):.1f}" stroke="var(--fita)" stroke-width="1.7" stroke-dasharray="3 2.4"/>')
for t, a, b, c, d in segs:
    if t == 'ccb':
        e(f'<line x1="{X(a):.1f}" y1="{Y(b):.1f}" x2="{X(c):.1f}" y2="{Y(d):.1f}" stroke="var(--rigido)" stroke-width="3" stroke-linecap="butt"/>')
for t, a, b, c, d in segs:
    if t == 'ccb_novo':
        e(f'<line x1="{X(a):.1f}" y1="{Y(b):.1f}" x2="{X(c):.1f}" y2="{Y(d):.1f}" stroke="var(--novo)" stroke-width="3.6" stroke-linecap="butt"/>')

# rotulos das zonas
for k in ('A', 'B', 'C'):
    lab = ('zona %s · %.2f m' % (k, W[k])).replace('.', ',')
    e(f'<text x="{X(x0[k]+W[k]/2):.1f}" y="{Y(2.45):.1f}" text-anchor="middle" font-size="12.5" font-weight="700" fill="{cor_zona[k]}" '
      f'paint-order="stroke" stroke="var(--folha)" stroke-width="4.5" stroke-linejoin="round">{lab}</text>')

# cotas dos vaos entre zonas
for k in ('A', 'B'):
    xr = x0[k] + W[k]
    e(f'<text x="{X(xr+VAO_ZONA/2):.1f}" y="{Y(19):.1f}" text-anchor="middle" font-size="10" font-weight="600" fill="var(--verde)" '
      f'transform="rotate(-90 {X(xr+VAO_ZONA/2):.1f} {Y(19):.1f})">1,20 m</text>')

# bocas do fundo: seta de entrada
for k in ('A', 'B', 'C'):
    cx = (boca_x[k][0] + boca_x[k][1])/2
    e(f'<line x1="{X(cx):.1f}" y1="{Y(PROF+2.4):.1f}" x2="{X(cx):.1f}" y2="{Y(PROF-1.2):.1f}" stroke="{cor_zona[k]}" stroke-width="1.8" marker-end="url(#pta)"/>')
    e(f'<text x="{X(cx):.1f}" y="{Y(PROF+2.7)+9:.1f}" text-anchor="middle" font-size="9" font-weight="700" fill="{cor_zona[k]}">boca {k} · {("%.2f" % bocas[k]).replace(".", ",")} m</text>')

# sentido da raia de cima e seta de descarga, da abertura ao eixo da porta
for k in ('A', 'B', 'C'):
    a, b = x0[k], x0[k] + W[k]
    xa, xb = saidas[k]
    cx = (xa + xb)/2
    # seta dentro da raia de cima apontando para a abertura
    if BOCA_OESTE[k]:
        e(f'<line x1="{X(a+1.5):.1f}" y1="{Y(MOD/2):.1f}" x2="{X(xa-0.4):.1f}" y2="{Y(MOD/2):.1f}" stroke="{cor_zona[k]}" stroke-width="1.6" marker-end="url(#pta)" opacity=".8"/>')
    else:
        e(f'<line x1="{X(b-1.5):.1f}" y1="{Y(MOD/2):.1f}" x2="{X(xb+0.4):.1f}" y2="{Y(MOD/2):.1f}" stroke="{cor_zona[k]}" stroke-width="1.6" marker-end="url(#pta)" opacity=".8"/>')
    e(f'<line x1="{X(cx):.1f}" y1="{Y(0)-4:.1f}" x2="{X(portas[k]):.1f}" y2="{MT+9:.1f}" stroke="{cor_zona[k]}" stroke-width="1.8" marker-end="url(#pta)"/>')
    lab = f'saída {k} · {("%.2f" % (RING_W-xb)).replace(".", ",")}–{("%.2f" % (RING_W-xa)).replace(".", ",")} m'
    dy = -22 if k == 'B' else -8
    e(f'<text x="{X(cx):.1f}" y="{Y(0)+dy:.1f}" text-anchor="middle" font-size="9" font-weight="700" fill="{cor_zona[k]}" '
      f'paint-order="stroke" stroke="var(--apron)" stroke-width="3">{lab}</text>')
e(f'<text x="{X(UTIL+1.5):.1f}" y="{Y(0)-8:.1f}" text-anchor="middle" font-size="9" font-weight="700" fill="var(--verde)" '
  f'paint-order="stroke" stroke="var(--apron)" stroke-width="3">0–3,00 m do canto NE</text>')

# cota geral
yb = Y(RING_D) + 26
e(f'<line x1="{X(0):.1f}" y1="{yb:.1f}" x2="{X(RING_W):.1f}" y2="{yb:.1f}" stroke="var(--fraco)" stroke-width="1"/>')
for m in (0, RING_W):
    e(f'<line x1="{X(m):.1f}" y1="{yb-4:.1f}" x2="{X(m):.1f}" y2="{yb+4:.1f}" stroke="var(--fraco)" stroke-width="1"/>')
e(f'<text x="{X(RING_W/2):.1f}" y="{yb+16:.1f}" text-anchor="middle" font-size="10" fill="var(--fraco)">gradil permanente do Ring 3 · 44,0 × 35,0 m · aberturas da face norte cotadas do canto nordeste</text>')
# escala
e(f'<line x1="{X(0):.1f}" y1="{yb+34:.1f}" x2="{X(10):.1f}" y2="{yb+34:.1f}" stroke="var(--tinta)" stroke-width="2.4"/>')
for m in (0, 5, 10):
    e(f'<line x1="{X(m):.1f}" y1="{yb+30:.1f}" x2="{X(m):.1f}" y2="{yb+38:.1f}" stroke="var(--tinta)" stroke-width="1.4"/>')
e(f'<text x="{X(10)+8:.1f}" y="{yb+38:.1f}" font-size="10" fill="var(--meio)">10 m</text>')
# cota vertical 32 m
e(f'<line x1="{X(0)-16:.1f}" y1="{Y(0):.1f}" x2="{X(0)-16:.1f}" y2="{Y(PROF):.1f}" stroke="var(--fraco)" stroke-width="1"/>')
e(f'<text x="{X(0)-21:.1f}" y="{Y(PROF/2):.1f}" text-anchor="middle" font-size="10" fill="var(--fraco)" transform="rotate(-90 {X(0)-21:.1f} {Y(PROF/2):.1f})">32,0 m · 23 raias</text>')

e('</svg>')
svg = '\n'.join(o)
open(os.path.join(RAIZ, 'saidas', 'ring3_planta.svg'), 'w', encoding='utf-8').write(svg)
print("svg ok", len(svg))
