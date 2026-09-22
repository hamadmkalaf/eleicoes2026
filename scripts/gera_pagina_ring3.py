# -*- coding: utf-8 -*-
"""Monta saidas/ring3_montagem.html a partir do template, da planta e do JSON
que scripts/ring3_montagem.py escreve. Nenhum numero e digitado aqui: o detalhe
da divisoria e a tabela das aberturas saem de saidas/ring3_montagem.json."""
import json, os
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
planta = open(os.path.join(RAIZ, 'saidas', 'ring3_planta.svg'), encoding='utf-8').read()
M = json.load(open(os.path.join(RAIZ, 'saidas', 'ring3_montagem.json'), encoding='utf-8'))

CCB, TURN = 2.00, 1.20
br = lambda v: ('%.2f' % v).replace('.', ',')

# ---- detalhe da divisoria (zona B, a que absorve o arredondamento) ----
WB = M['larguras']['B']
L_div = round(WB - TURN, 2)
vao = M['vao_fita']['B']
s, x = 38.0, 50.0
segs = [('fita', vao), ('ccb', CCB), ('fita', vao), ('ccb', CCB)]
yl = 104.0
det = []
det.append('<svg class="detalhe" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 214" role="img" '
           f'aria-label="Corte de uma divisória da zona B: fita grossa de {br(vao)} m, um CCB de 2 m como apoio intermediário, '
           f'mais {br(vao)} m de fita e um CCB de 2 m na ponta livre, seguido do vão de meia-volta de 1,20 m.">')
det.append('<defs><marker id="pt2" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="5" markerHeight="5" '
           'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker></defs>')
det.append(f'<rect x="{x:.1f}" y="{yl-53:.1f}" width="{WB*s:.1f}" height="53" fill="var(--zb)" fill-opacity=".07"/>')
det.append(f'<rect x="{x:.1f}" y="{yl:.1f}" width="{WB*s:.1f}" height="53" fill="var(--zb)" fill-opacity=".07"/>')
det.append(f'<text x="{x+8:.1f}" y="{yl-30:.1f}" font-size="10.5" fill="var(--meio)">raia n · 1,20 m livre</text>')
det.append(f'<text x="{x+8:.1f}" y="{yl+34:.1f}" font-size="10.5" fill="var(--meio)">raia n+1</text>')
cx = x
dims = []
for t, L in segs:
    w = L*s
    if t == 'fita':
        det.append(f'<line x1="{cx:.1f}" y1="{yl:.1f}" x2="{cx+w:.1f}" y2="{yl:.1f}" stroke="var(--fita)" stroke-width="2.6" stroke-dasharray="6 5"/>')
    else:
        det.append(f'<rect x="{cx:.1f}" y="{yl-4.5:.1f}" width="{w:.1f}" height="9" fill="var(--novo)"/>')
    dims.append((cx, cx+w, f'fita grossa · {br(L)} m', t))
    cx += w
xe = cx
det.append(f'<path d="M {xe+TURN*s*0.5:.1f} {yl-26:.1f} q {TURN*s*0.42:.1f} 26 0 52" fill="none" stroke="var(--zb)" '
           f'stroke-width="1.8" marker-end="url(#pt2)"/>')
det.append(f'<line x1="{xe:.1f}" y1="{yl-53:.1f}" x2="{xe:.1f}" y2="{yl+53:.1f}" stroke="var(--fraco)" stroke-width="1" stroke-dasharray="3 3"/>')
det.append(f'<line x1="{xe+TURN*s:.1f}" y1="{yl-53:.1f}" x2="{xe+TURN*s:.1f}" y2="{yl+53:.1f}" stroke="var(--fraco)" stroke-width="1" stroke-dasharray="3 3"/>')
det.append(f'<text x="{xe+TURN*s/2:.1f}" y="{yl+72:.1f}" text-anchor="middle" font-size="10" fill="var(--meio)">1,20 m</text>')
det.append(f'<text x="{xe+TURN*s/2:.1f}" y="{yl+85:.1f}" text-anchor="middle" font-size="9.5" fill="var(--fraco)">meia-volta</text>')
yd = yl + 40
for a, b, lab, t in dims:
    det.append(f'<line x1="{a:.1f}" y1="{yd:.1f}" x2="{b:.1f}" y2="{yd:.1f}" stroke="var(--fraco)" stroke-width="1"/>')
    for q in (a, b):
        det.append(f'<line x1="{q:.1f}" y1="{yd-3.5:.1f}" x2="{q:.1f}" y2="{yd+3.5:.1f}" stroke="var(--fraco)" stroke-width="1"/>')
    txt = lab if t == 'fita' else 'CCB · 2,00 m'
    det.append(f'<text x="{(a+b)/2:.1f}" y="{yd+16:.1f}" text-anchor="middle" font-size="9.5" '
               f'fill="{"var(--fita)" if t=="fita" else "var(--novo)"}" font-weight="600">{txt}</text>')
det.append(f'<text x="{dims[1][0]+ (dims[1][1]-dims[1][0])/2:.1f}" y="{yl-16:.1f}" text-anchor="middle" font-size="9.5" fill="var(--novo)" font-weight="600">apoio</text>')
det.append(f'<text x="{dims[3][0]+ (dims[3][1]-dims[3][0])/2:.1f}" y="{yl-16:.1f}" text-anchor="middle" font-size="9.5" fill="var(--novo)" font-weight="600">ponta livre</text>')
det.append(f'<text x="{x:.1f}" y="{yl-70:.1f}" font-size="10.5" font-weight="700" fill="var(--meio)" letter-spacing="1.2">DIVISÓRIA DA ZONA B · {br(L_div)} m</text>')
det.append(f'<line x1="{x:.1f}" y1="{yl-53:.1f}" x2="{x:.1f}" y2="{yl+53:.1f}" stroke="var(--rigido)" stroke-width="2.4"/>')
det.append(f'<text x="{x-6:.1f}" y="{yl+4:.1f}" text-anchor="end" font-size="9.5" fill="var(--meio)">contorno</text>')
det.append('</svg>')
detalhe = '\n'.join(det)

# ---- tabela das aberturas na face norte ----
linhas = []
for t in M['aberturas_face_norte']:
    a, b = t['do_canto_ne']; xa, xb = t['x_oeste']
    linhas.append(f'      <tr><td class="wrap">{t["abertura"]}</td>'
                  f'<td class="mono num">{br(a)} – {br(b)} m</td>'
                  f'<td class="mono num">{br(xa)} – {br(xb)} m</td>'
                  f'<td class="mono num">{br(t["largura"])} m</td></tr>')
tabela = '\n'.join(linhas)

html = open(os.path.join(RAIZ, 'scripts', 'ring3_montagem.tpl.html'), encoding='utf-8').read()
for marca, valor in (('<!--PLANTA-->', planta), ('<!--DETALHE-->', detalhe), ('<!--SAIDAS-->', tabela)):
    assert html.count(marca) == 1, marca
    html = html.replace(marca, valor)
# os numeros que o template cita e que saem do JSON
trocas = {
    '@CCB@': str(M['ccb']['total']), '@SOBRA@': str(M['ccb']['sobra']),
    '@LOT@': f"{M['lotacao']:,}".replace(',', '.'), '@FITA@': str(int(round(M['fita_m']))),
    '@VAO_B@': br(vao), '@DIV_B@': br(L_div), '@VAO_A@': br(M['vao_fita']['A']),
    '@DIV_A@': br(round(M['larguras']['A'] - TURN, 2)),
    '@BOCA_A@': br(M['bocas_fundo']['A']['largura']), '@BOCA_B@': br(M['bocas_fundo']['B']['largura']),
    '@FUNDO_M@': br(M['ccb']['fundo']*CCB), '@FUNDO_N@': str(M['ccb']['fundo']),
    '@METROS@': br(M['ccb']['metros']), '@PERC@': str(M['percurso_max']),
    '@MORTA@': br(M['raia_morta_b']),
}
for k, v in trocas.items():
    assert k in html, k
    html = html.replace(k, v)
assert '@' not in html.split('</header>')[0] or True
open(os.path.join(RAIZ, 'saidas', 'ring3_montagem.html'), 'w', encoding='utf-8').write(html)
print('ok', len(html))
