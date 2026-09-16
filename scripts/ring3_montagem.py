# -*- coding: utf-8 -*-
"""Ring 3 — cenario 3 adaptado. O mapa e a conta: os mesmos segmentos geram SVG e BOM."""
import math, os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------- premissas ----------
RING_W, RING_D = 44.0, 35.0
COR = 3.0                 # corredor em L
UTIL = RING_W - COR       # 41.0
PROF = RING_D - COR       # 32.0
VAO_ZONA = 1.20           # NOVO: era 2.60
LANES, MOD = 23, PROF/23
TURN = 1.20               # vao de meia-volta
CCB = 2.00
DENS = 2.386              # p por metro de raia (calibrado no artefato anterior)
ESTOQUE = 200
LAT_N = 8.0               # trecho norte das laterais que vira CCB

# larguras proporcionais ao comparecimento esperado por porta
esp = {'A': 3642, 'B': 4215, 'C': 3642}
tot_esp = sum(esp.values())
livre = UTIL - 2*VAO_ZONA
W = {k: round(livre*v/tot_esp, 2) for k, v in esp.items()}
W['B'] = round(livre - W['A'] - W['C'], 2)
assert abs(W['A']+W['B']+W['C'] - livre) < 1e-9, (W, livre)

x0 = {}
cur = 0.0
for k in ('A', 'B', 'C'):
    x0[k] = cur
    cur += W[k] + VAO_ZONA
assert abs(cur - VAO_ZONA - UTIL) < 1e-9, cur

DIV = LANES - 1           # divisorias por zona
segs = []                 # (tipo, x1,y1, x2,y2)  tipo in ccb|ccb_novo|fita

def add(t, a, b, c, d): segs.append((t, a, b, c, d))

# divisorias: CCB na ponta livre + fita + CCB de apoio no meio da fita + fita
for k in ('A', 'B', 'C'):
    a, b = x0[k], x0[k] + W[k]
    for i in range(1, LANES):
        y = PROF*i/LANES
        leste = (i % 2 == 1)
        p0, p1 = (a, b - TURN) if leste else (a + TURN, b)
        L = p1 - p0                      # comprimento da divisoria
        if leste:
            add('ccb', p1 - CCB, y, p1, y)          # ponta livre (leste)
            f0, f1 = p0, p1 - CCB
        else:
            add('ccb', p0, y, p0 + CCB, y)          # ponta livre (oeste)
            f0, f1 = p0 + CCB, p1
        Lf = f1 - f0
        s = (Lf - CCB)/2                            # vao de fita de cada lado
        add('fita', f0, y, f0 + s, y)
        add('ccb_novo', f0 + s, y, f0 + s + CCB, y)  # apoio intermediario (novo)
        add('fita', f0 + s + CCB, y, f1, y)

# parede zona C / corredor de chegada (ja estava na conta)
add('ccb', UTIL, 0.0, UTIL, PROF)

# NOVO: fechamento contra o trecho de fundo, com boca de entrada
bocas = {}
for k in ('A', 'B', 'C'):
    a, b = x0[k], x0[k] + W[k]
    n = math.floor((W[k] - 1.0)/CCB)
    bocas[k] = round(W[k] - n*CCB, 2)
    add('ccb_novo', a, PROF, a + n*CCB, PROF)       # boca fica no lado leste

# NOVO: laterais parciais, 8 m ao norte, nas duas faces de cada vao
for k in ('A', 'B'):
    xr = x0[k] + W[k]
    add('ccb_novo', xr, 0.0, xr, LAT_N)
    add('ccb_novo', xr + VAO_ZONA, 0.0, xr + VAO_ZONA, LAT_N)

# ---------- a conta, derivada dos segmentos ----------
def comp(s): return math.hypot(s[3]-s[1], s[4]-s[2])
m_ccb  = sum(comp(s) for s in segs if s[0] == 'ccb')
m_novo = sum(comp(s) for s in segs if s[0] == 'ccb_novo')
m_fita = sum(comp(s) for s in segs if s[0] == 'fita')
n_ccb  = round((m_ccb + m_novo)/CCB)
assert abs((m_ccb+m_novo)/CCB - n_ccb) < 1e-6, (m_ccb+m_novo)

# quebra por item
it_div   = DIV*3*CCB*2                 # ponta + apoio
it_ponta = DIV*3*CCB
it_apoio = DIV*3*CCB
it_par   = PROF
it_fundo = sum(math.floor((W[k]-1.0)/CCB)*CCB for k in W)
it_lat   = 4*LAT_N
assert abs(it_div + it_par + it_fundo + it_lat - (m_ccb+m_novo)) < 1e-6

lane_m = LANES*sum(W.values())
lot = LANES*sum(W.values())*DENS
vao_fita = ((W['B']-TURN) - 2*CCB)/2

portas = {'A': 15.78, 'B': 22.00, 'C': 28.22}
desvio = {}
for k in portas:
    a, b = x0[k], x0[k]+W[k]
    desvio[k] = 0.0 if a <= portas[k] <= b else round(min(abs(a-portas[k]), abs(b-portas[k])), 2)

print(f"larguras {W}  x0 {x0}")
print(f"bocas reais {bocas}")
print(f"CCB: {n_ccb}  ({m_ccb:.1f} m ja na conta + {m_novo:.1f} m novos = {m_ccb+m_novo:.1f} m)")
print(f"  divisorias ponta {int(it_ponta/CCB)} | apoios {int(it_apoio/CCB)} | parede C {int(it_par/CCB)} | fundo {int(it_fundo/CCB)} | laterais {int(it_lat/CCB)}")
print(f"fita grossa {m_fita:.1f} m | vao maximo de fita {vao_fita:.2f} m (zona B)")
print(f"raia-metros {lane_m:.1f} | lotacao {lot:.0f} | percurso max {LANES*W['B']:.0f} m")
print(f"desvios {desvio}")
print(f"compra {max(0, n_ccb-ESTOQUE)} | sobra {max(0, ESTOQUE-n_ccb)}")

# ---------- SVG ----------
S = 15.0
MX, MT, MB = 58, 44, 74
APRON = 14.0
HW = 50.3   # nada, so referencia
def X(m): return MX + m*S
def Y(m): return MT + (APRON + m)*S      # m medido do topo do Ring
Wpx = MX*2 + RING_W*S
Hpx = MT + (APRON + RING_D)*S + MB

o = []
def e(s): o.append(s)
e(f'<svg class="planta" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {Wpx:.0f} {Hpx:.0f}" role="img" '
  f'aria-label="Planta do Ring 3 no cenario 3 adaptado: tres zonas de raias leste-oeste separadas por corredores de 1,2 m, '
  f'divisorias de fita grossa ancoradas por dois CCB cada, fechamento de fundo com boca de entrada e laterais rigidas nos 8 m ao norte.">')
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
e(f'<text x="{X(UTIL/2):.1f}" y="{Y(PROF+1.9):.1f}" text-anchor="middle" font-size="10.5" font-weight="600" fill="var(--verde)">TRECHO DE FUNDO · 3,0 m</text>')
# entrada
e(f'<line x1="{X(UTIL+1.5):.1f}" y1="{Y(0)-46:.1f}" x2="{X(UTIL+1.5):.1f}" y2="{Y(1.4):.1f}" stroke="var(--verde)" stroke-width="2.4" marker-end="url(#pta)"/>')
e(f'<text x="{X(UTIL+1.5)-9:.1f}" y="{Y(0)-34:.1f}" text-anchor="end" font-size="10" fill="var(--verde)">entrada · canto nordeste</text>')

# zonas + corredores entre zonas
for k in ('A', 'B', 'C'):
    e(f'<rect x="{X(x0[k]):.1f}" y="{Y(0):.1f}" width="{W[k]*S:.1f}" height="{PROF*S:.1f}" fill="{cor_zona[k]}" fill-opacity=".07"/>')
for k in ('A', 'B'):
    xr = x0[k] + W[k]
    e(f'<rect x="{X(xr):.1f}" y="{Y(0):.1f}" width="{VAO_ZONA*S:.1f}" height="{PROF*S:.1f}" fill="var(--circ)"/>')

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
    e(f'<text x="{X(x0[k]+W[k]/2):.1f}" y="{Y(1.05):.1f}" text-anchor="middle" font-size="12.5" font-weight="700" fill="{cor_zona[k]}" '
      f'paint-order="stroke" stroke="var(--folha)" stroke-width="4.5" stroke-linejoin="round">{lab}</text>')

# cotas dos vaos entre zonas
for k in ('A', 'B'):
    xr = x0[k] + W[k]
    e(f'<text x="{X(xr+VAO_ZONA/2):.1f}" y="{Y(19):.1f}" text-anchor="middle" font-size="10" font-weight="600" fill="var(--verde)" '
      f'transform="rotate(-90 {X(xr+VAO_ZONA/2):.1f} {Y(19):.1f})">1,20 m</text>')

# setas de descarga
for k in ('A', 'B', 'C'):
    sx = min(max(portas[k], x0[k]+1), x0[k]+W[k]-1)
    e(f'<line x1="{X(sx):.1f}" y1="{Y(0)-4:.1f}" x2="{X(portas[k]):.1f}" y2="{MT+9:.1f}" stroke="{cor_zona[k]}" stroke-width="1.8" marker-end="url(#pta)"/>')

# cota geral
yb = Y(RING_D) + 26
e(f'<line x1="{X(0):.1f}" y1="{yb:.1f}" x2="{X(RING_W):.1f}" y2="{yb:.1f}" stroke="var(--fraco)" stroke-width="1"/>')
for m in (0, RING_W):
    e(f'<line x1="{X(m):.1f}" y1="{yb-4:.1f}" x2="{X(m):.1f}" y2="{yb+4:.1f}" stroke="var(--fraco)" stroke-width="1"/>')
e(f'<text x="{X(RING_W/2):.1f}" y="{yb+16:.1f}" text-anchor="middle" font-size="10" fill="var(--fraco)">gradil permanente do Ring 3 · 44,0 × 35,0 m</text>')
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
open(os.path.join(RAIZ, 'saidas', 'ring3_planta.svg'), 'w').write(svg)
print("svg ok", len(svg))
