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
Revisao de 23/09/2026:
  * as laterais A/B e B/C fecham de ponta a ponta (32,0 m), e nao mais so nos
    8 m ao norte: a divisoria de cada raia termina em fita, e fita precisa de
    um ponto fixo dos dois lados. Cada zona ganha a SUA linha, nas duas faces
    de cada vao, e o corredor de 1,20 m entre elas continua livre -- e por ele
    que entram maca e fiscal. Custou 28 CCBs acima do estoque.
Revisao de 24/09/2026 -- economia de CCB (pedido do Posto):
  * a lateral deixa de ser parede continua. **CCB so onde a fita amarra**, fita
    no resto. Numa linha de lateral nao amarram as 22 divisorias da zona: a
    ponta fixa de cada divisoria alterna de lado a cada raia, entao cada linha
    recebe so as de indice par (ou so as de indice impar) -- 11 pontos, a
    2,78 m um do outro. Um painel de 2,00 m nao alcanca dois pontos vizinhos,
    logo e 1 painel por ponto: **11 CCBs por linha em vez de 16**;
  * o fechamento contra o trecho de fundo passa a alternar CCB e fita do mesmo
    jeito, com CCB nas DUAS pontas -- a de fora encosta na lateral da zona e a
    de dentro e a **porta da boca**, que e o que o pedido exige. Sao 3 paineis
    por zona em vez de 5, com vaos de fita de 2,00 m;
  * o portao a cada 8 m sai de cena: os vaos de fita da propria lateral sao a
    passagem, e sao 12 por linha em vez de 4 portoes.
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
PRECO_CCB = 13.02         # EUR por CCB, item d do orcamento

# Como a lateral de cada zona e fechada. Tres modos, e a folha desenha o
# primeiro:
#   'amarracao' -- 24/09. CCB de 2,00 m centrada em cada ponto onde a fita da
#                  divisoria amarra, fita entre elas. Sao 11 pontos por linha,
#                  porque a ponta fixa alterna de lado a cada raia, e eles
#                  ficam a 2,78 m: um painel nao pega dois. 44 CCBs de lateral.
#   'faces'     -- 23/09. Uma parede continua em CADA face do vao, 4 trechos de
#                  32,0 m = 64 CCBs. Fecha o corte lateral inteiro, e por isso
#                  custava 28 CCBs acima do estoque.
#   'eixo'      -- uma linha so, no meio do vao, 2 trechos = 32 CCBs. Cabe no
#                  estoque mas sobra 0,60 m de cada lado: nao passa maca, e o
#                  vao deixa de ter funcao.
LATERAL = 'amarracao'
LATERAL_VARIANTE = 'faces'
# O fechamento contra o trecho de fundo. 'amarracao' alterna CCB e fita com CCB
# nas duas pontas; 'solido' e a parede continua de 5 paineis de ate 23/09.
FUNDO = 'amarracao'
# A parede que separa a zona C do corredor de chegada continua CONTINUA, e nao
# entra na economia. Nao e simetrica as laterais: a lateral A|B da para a zona
# vizinha, onde ninguem pode votar, e o vao de servico entre as duas linhas e
# patrulhado; a parede da C da para o corredor por onde passam os 16,8 mil que
# entram, e um vao ali e um atalho para o meio da fila da propria zona -- vale
# ~150 m de percurso. 'amarracao' aqui economizaria 5 CCBs e fecharia a compra
# em zero; e decisao do Posto, e esta como variante no relatorio.
PAREDE_C = 'solida'
# Vao maximo de fita que o desenho aceita sem um apoio rigido no meio. Sai da
# divisoria da zona B, que e o vao mais longo que o Posto ja aprovou (3,84 m).
VAO_FITA_MAX = 4.00
# Vao de fita que uma pessoa atravessa de lado -- e o que faz de um vao uma
# PASSAGEM para o corredor de servico, e nao uma folga de montagem. Sobra de
# extremidade menor do que isto e desperdicio: o painel da ponta e encostado no
# fim da linha e a sobra vai para o vao seguinte, que ganha 0,39 m.
VAO_PASSAGEM = 0.75
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

# Onde a ponta FIXA da divisoria amarra, por zona. A oeste da A e o gradil
# permanente do Ring e a leste da C e a parede do corredor de chegada: esses
# dois ja existiam. Os dois vaos internos levam a linha de cada zona na sua
# propria face.
meio_vao = {k: round(x0[k] + W[k] + VAO_ZONA/2, 2) for k in ('A', 'B')}
if LATERAL in ('amarracao', 'faces'):
    anc_o = {k: x0[k] for k in W}
    anc_l = {k: round(x0[k] + W[k], 2) for k in W}
else:
    anc_o = {'A': 0.0, 'B': meio_vao['A'], 'C': meio_vao['B']}
    anc_l = {'A': meio_vao['A'], 'B': meio_vao['B'], 'C': UTIL}

DIV = LANES - 1           # divisorias por zona
segs = []                 # (tipo, x1,y1, x2,y2)  tipo in ccb|ccb_novo|fita

def add(t, a, b, c, d): segs.append((t, a, b, c, d))

# divisorias: CCB na ponta livre + fita + CCB de apoio no meio da fita + fita.
# Divisoria i separa a raia i-1 (ao norte) da raia i (ao sul). `leste` diz de
# que lado fica o vao de meia-volta dela -- e, por consequencia, de que lado
# fica a ponta FIXA: no lado oposto. Como `leste` alterna com a paridade de i,
# **cada linha de lateral recebe so metade das divisorias da zona vizinha**, e
# e essa alternancia que faz a economia de 24/09 caber.
amarras = {}              # x da linha -> lista de y onde a fita amarra
for k in ('A', 'B', 'C'):
    a, b = x0[k], x0[k] + W[k]
    for i in range(1, LANES):
        y = PROF*i/LANES
        leste = (i % 2 == 1) != BOCA_OESTE[k]
        # a ponta LIVRE fica do lado do vao de meia-volta; a ponta FIXA vai ate
        # a linha de CCB da lateral daquele lado
        p0, p1 = (anc_o[k], b - TURN) if leste else (a + TURN, anc_l[k])
        amarras.setdefault(round(p0 if leste else p1, 2), []).append(y)
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


def linha_amarrada(x, ys, y0=0.0, y1=PROF, tipo='ccb_novo'):
    """Linha vertical com um CCB centrado em cada amarracao e fita no resto.

    Devolve (paineis, vaos): os intervalos de y de cada painel e os vaos de
    fita entre eles, incluindo as duas pontas. E o vao que importa na operacao:
    e por ele que se entra no corredor de servico.
    """
    paineis = []
    for y in sorted(ys):
        c0, c1 = y - CCB/2, y + CCB/2
        if c0 < y0:  c0, c1 = y0, y0 + CCB          # encosta na ponta norte
        if c1 > y1:  c0, c1 = y1 - CCB, y1          # encosta na ponta sul
        assert not paineis or c0 >= paineis[-1][1] - 1e-9, (x, y, paineis[-1])
        paineis.append((c0, c1))
    ys_ord = sorted(ys)
    # encosta o painel da ponta quando a sobra ali nao passa ninguem
    if paineis and paineis[0][0] - y0 < VAO_PASSAGEM and y0 + CCB >= ys_ord[0] - 1e-9:
        paineis[0] = (y0, y0 + CCB)
    if paineis and y1 - paineis[-1][1] < VAO_PASSAGEM and y1 - CCB <= ys_ord[-1] + 1e-9:
        paineis[-1] = (y1 - CCB, y1)
    vaos, cur_y = [], y0
    for c0, c1 in paineis:
        if c0 - cur_y > 1e-9:
            add('fita', x, cur_y, x, c0)
            vaos.append(round(c0 - cur_y, 2))
        add(tipo, x, c0, x, c1)
        cur_y = c1
    if y1 - cur_y > 1e-9:
        add('fita', x, cur_y, x, y1)
        vaos.append(round(y1 - cur_y, 2))
    return paineis, vaos


# parede zona C / corredor de chegada
if PAREDE_C == 'solida':
    add('ccb', UTIL, 0.0, UTIL, PROF)
    n_par = int(round(PROF/CCB))
else:
    pan, _ = linha_amarrada(UTIL, amarras[round(UTIL, 2)], tipo='ccb')
    n_par = len(pan)

# fechamento contra o trecho de fundo, com boca de entrada. Desde 24/09 ele
# alterna CCB e fita, e o ultimo painel de cada zona encosta na boca: e a
# PORTA DA BOCA, o batente rigido em que a corrente de entrada se apoia.
bocas = {}          # largura real da boca
boca_x = {}         # (x1, x2) da boca do fundo
vao_fundo = {}      # vao de fita entre dois paineis do fechamento
n_fundo = 0
for k in ('A', 'B', 'C'):
    a, b = x0[k], x0[k] + W[k]
    n = math.floor((W[k] - 1.0)/CCB)
    L = n*CCB                                   # trecho fechado, 10,00 m
    bocas[k] = round(W[k] - L, 2)
    if FUNDO == 'amarracao':
        c = 2
        while (L - c*CCB)/(c - 1) > VAO_FITA_MAX:
            c += 1
        vao = (L - c*CCB)/(c - 1)
    else:
        c, vao = n, 0.0
    assert c <= n, (k, c, n)
    vao_fundo[k] = round(vao, 2)
    n_fundo += c
    p, s = (b, -1.0) if BOCA_OESTE[k] else (a, +1.0)   # da borda da zona para dentro
    for j in range(c):
        q = p + s*CCB
        add('ccb_novo', min(p, q), PROF, max(p, q), PROF)
        p = q
        if j < c - 1 and vao > 1e-9:
            q = p + s*vao
            add('fita', min(p, q), PROF, max(p, q), PROF)
            p = q
    boca_x[k] = (round(a, 2), round(p, 2)) if BOCA_OESTE[k] else (round(p, 2), round(b, 2))
    assert abs((boca_x[k][1] - boca_x[k][0]) - bocas[k]) < 1e-6, (k, boca_x[k], bocas[k])

# laterais: as duas faces de cada vao interno, amarracao por amarracao (24/09)
laterais_x = []
if LATERAL in ('amarracao', 'faces'):
    for k in ('A', 'B'):
        xr = x0[k] + W[k]
        laterais_x += [round(xr, 2), round(xr + VAO_ZONA, 2)]
else:
    laterais_x = [meio_vao[k] for k in ('A', 'B')]

n_lat, vaos_lat, pts_lat, linha_paineis = 0, [], {}, {}
for xl in laterais_x:
    if LATERAL == 'amarracao':
        pan, vaos = linha_amarrada(xl, amarras[xl])
        n_lat += len(pan)
        pts_lat[xl] = len(pan)
        linha_paineis[xl] = pan
        vaos_lat.append({'x': xl, 'vaos': vaos})
    else:
        add('ccb_novo', xl, 0.0, xl, PROF)
        n_lat += int(round(PROF/CCB))
        pts_lat[xl] = 0
        linha_paineis[xl] = [(0.0, PROF)]

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
it_par   = n_par*CCB
it_fundo = n_fundo*CCB
it_lat   = n_lat*CCB
it_bat   = CCB*len(SAIDA_MEIO)
assert abs(it_ponta + it_apoio + it_par + it_fundo + it_lat + it_bat - (m_ccb+m_novo)) < 1e-6

# fita por destino, para a compra: a divisoria e o que sempre existiu; a
# lateral e o fechamento do fundo sao o que a economia de 24/09 acrescenta.
f_div   = DIV*3*2*0.0   # preenchido abaixo
f_div   = sum(comp(s) for s in segs if s[0] == 'fita' and abs(s[2]-s[4]) < 1e-9
              and s[2] not in (PROF,))
f_lat   = sum(comp(s) for s in segs if s[0] == 'fita' and abs(s[1]-s[3]) < 1e-9)
f_fundo = sum(comp(s) for s in segs if s[0] == 'fita' and s[2] == PROF and s[4] == PROF)
assert abs(f_div + f_lat + f_fundo - m_fita) < 1e-6, (f_div, f_lat, f_fundo, m_fita)

lane_m = LANES*sum(W.values()) - morta
lot = lane_m*DENS
vao_fita = {k: round(((W[k]-TURN) - 2*CCB)/2, 2) for k in W}
vaos_planos = sorted(v for l in vaos_lat for v in l['vaos'])

# comparacao com a revisao de 23/09, que fechava lateral e fundo em parede
n_23 = int(it_ponta/CCB) + int(it_apoio/CCB) + int(round(PROF/CCB)) \
       + sum(math.floor((W[k]-1.0)/CCB) for k in W) + 4*int(round(PROF/CCB)) \
       + int(it_bat/CCB)
# variante: a mesma amarracao aplicada a parede da zona C
n_par_amarr = len(amarras[round(UTIL, 2)])
n_com_par = n_ccb - n_par + n_par_amarr

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
print(f"bocas do fundo {bocas} em x {boca_x} | vao de fita do fechamento {vao_fundo}")
print(f"saidas na face norte {saidas}")
for t in tabela_aberturas:
    print(f"  {t['abertura']:<20} x {t['x_oeste'][0]:6.2f}-{t['x_oeste'][1]:6.2f} m"
          f"  | do canto NE {t['do_canto_ne'][0]:6.2f}-{t['do_canto_ne'][1]:6.2f} m")
print(f"CCB: {n_ccb}  ({m_ccb:.1f} m ja na conta + {m_novo:.1f} m novos = {m_ccb+m_novo:.1f} m)")
print(f"  divisorias ponta {int(it_ponta/CCB)} | apoios {int(it_apoio/CCB)} | parede C {n_par} "
      f"| fundo {n_fundo} | laterais {n_lat} | batente B {int(it_bat/CCB)}")
print(f"fita grossa {m_fita:.1f} m  (divisorias {f_div:.1f} + laterais {f_lat:.1f} + fundo {f_fundo:.1f})"
      f" | vao maximo de fita da divisoria {vao_fita}")
print(f"raia-metros {lane_m:.1f} (menos {morta:.2f} m mortos na B) | lotacao {lot:.0f} | percurso max {LANES*W['A']:.0f} m")
print(f"desvios ao eixo da porta {desvio} | dentro do vao {dentro_do_vao}")
print(f"laterais: modo {LATERAL} em x {laterais_x} | {pts_lat} pontos de amarracao por linha")
from collections import Counter
dist_vaos = sorted(Counter(vaos_planos).items())
print(f"  {len(vaos_planos)} vaos de fita nas laterais, {f_lat:.1f} m no total: "
      + " · ".join(f"{n}x {v:.2f} m" for v, n in dist_vaos))
print(f"compra {max(0, n_ccb-ESTOQUE)} | sobra {max(0, ESTOQUE-n_ccb)} | "
      f"economia sobre 23/09: {n_23 - n_ccb} CCBs (EUR {(n_23-n_ccb)*PRECO_CCB:,.2f})")
print(f"variante: com a parede da C tambem amarrada, {n_com_par} CCBs "
      f"({max(0, n_com_par-ESTOQUE)} a comprar, sobra {max(0, ESTOQUE-n_com_par)})")

json.dump({
    'revisao': '2026-09-24', 'ring': [RING_W, RING_D], 'corredor': COR, 'vao_zona': VAO_ZONA,
    'raias': LANES, 'modulo': round(MOD, 3), 'larguras': W, 'x0': x0,
    'boca_oeste': BOCA_OESTE, 'saida_meio': SAIDA_MEIO,
    'bocas_fundo': {k: {'largura': bocas[k], 'x': boca_x[k], 'paineis': n_fundo//3,
                        'vao_fita': vao_fundo[k]} for k in bocas},
    'saidas_norte': {k: list(saidas[k]) for k in saidas},
    'aberturas_face_norte': tabela_aberturas,
    'portas_eixo': portas, 'desvio_ao_eixo': desvio, 'dentro_do_vao': dentro_do_vao,
    'ccb': {'total': n_ccb, 'ponta': int(it_ponta/CCB), 'apoio': int(it_apoio/CCB),
            'parede_c': n_par, 'fundo': n_fundo, 'laterais': n_lat,
            'batente_b': int(it_bat/CCB), 'metros': round(m_ccb+m_novo, 1),
            'estoque': ESTOQUE, 'compra': max(0, n_ccb-ESTOQUE), 'sobra': max(0, ESTOQUE-n_ccb),
            'preco_unitario_eur': PRECO_CCB,
            'total_2309': n_23, 'economia': n_23 - n_ccb,
            'economia_eur': round((n_23 - n_ccb)*PRECO_CCB, 2)},
    'laterais': {'modo': LATERAL, 'variante': LATERAL_VARIANTE, 'x': laterais_x,
                 'pontos_por_linha': pts_lat, 'ccb': n_lat,
                 'amarras_por_linha': (min(pts_lat.values()) if pts_lat else 0),
                 'vaos': vaos_lat, 'vao_min': vaos_planos[0], 'vao_max': vaos_planos[-1],
                 'n_vaos': len(vaos_planos), 'vaos_por_linha': len(vaos_planos)//4,
                 'distribuicao_vaos': [[v, n] for v, n in dist_vaos],
                 'vao_passagem': VAO_PASSAGEM, 'fita_m': round(f_lat, 1)},
    'fundo': {'modo': FUNDO, 'paineis_por_zona': n_fundo//3, 'ccb': n_fundo,
              'vao_fita': vao_fundo, 'fita_m': round(f_fundo, 1)},
    'parede_c': {'modo': PAREDE_C, 'ccb': n_par,
                 'variante_amarrada': n_par_amarr, 'total_com_variante': n_com_par,
                 'compra_com_variante': max(0, n_com_par-ESTOQUE),
                 'sobra_com_variante': max(0, ESTOQUE-n_com_par)},
    'fita_m': round(m_fita, 1), 'fita_divisorias_m': round(f_div, 1),
    'vao_fita': vao_fita,
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
  f'divisorias de fita grossa ancoradas por dois CCB cada, fechamento de fundo alternando CCB e fita com boca de entrada (a oeste na zona A), '
  f'laterais dos dois vaos internos com um CCB em cada ponto de amarracao de fita e fita entre eles, '
  f'e quatro aberturas na face norte do gradil: corredor de chegada e as saidas C, B e A.">')
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
    # o vao entre zonas continua circulacao, e desde 23/09 fechado dos dois
    # lados: vira corredor de servico, com entrada unica pelo trecho de fundo
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

# os vaos de fita das laterais sao a passagem para o corredor de servico: um
# tracinho verde marca cada um, para o montador saber que ali nao vai painel
for l in vaos_lat:
    xl = l['x']
    cur_v = 0.0
    for c0, c1 in linha_paineis[xl]:
        if c0 - cur_v > 1e-9:
            e(f'<line x1="{X(xl)-3:.1f}" y1="{Y((cur_v+c0)/2):.1f}" x2="{X(xl)+3:.1f}" y2="{Y((cur_v+c0)/2):.1f}" stroke="var(--verde)" stroke-width="2.2"/>')
        cur_v = c1
    if PROF - cur_v > 1e-9:
        e(f'<line x1="{X(xl)-3:.1f}" y1="{Y((cur_v+PROF)/2):.1f}" x2="{X(xl)+3:.1f}" y2="{Y((cur_v+PROF)/2):.1f}" stroke="var(--verde)" stroke-width="2.2"/>')

# rotulos das zonas
for k in ('A', 'B', 'C'):
    lab = ('zona %s · %.2f m' % (k, W[k])).replace('.', ',')
    e(f'<text x="{X(x0[k]+W[k]/2):.1f}" y="{Y(2.45):.1f}" text-anchor="middle" font-size="12.5" font-weight="700" fill="{cor_zona[k]}" '
      f'paint-order="stroke" stroke="var(--folha)" stroke-width="4.5" stroke-linejoin="round">{lab}</text>')

# cotas dos vaos entre zonas
for k in ('A', 'B'):
    xr = x0[k] + W[k]
    e(f'<text x="{X(xr+VAO_ZONA/2):.1f}" y="{Y(19):.1f}" text-anchor="middle" font-size="10" font-weight="600" fill="var(--verde)" '
      f'paint-order="stroke" stroke="var(--folha)" stroke-width="3.5" '
      f'transform="rotate(-90 {X(xr+VAO_ZONA/2):.1f} {Y(19):.1f})">1,20 m · maca e fiscal · 12 vãos por face</text>')

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
