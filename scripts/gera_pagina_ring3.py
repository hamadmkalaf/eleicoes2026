# -*- coding: utf-8 -*-
import io, os
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
planta = open(os.path.join(RAIZ, 'saidas', 'ring3_planta.svg')).read()

# ---- detalhe da divisoria (zona B) ----
s, x = 38.0, 50.0
segs = [('fita', 4.47), ('ccb', 2.00), ('fita', 4.47), ('ccb', 2.00)]
yl = 104.0
det = []
det.append('<svg class="detalhe" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 214" role="img" '
           'aria-label="Corte de uma divisória da zona B: fita grossa de 4,47 m, um CCB de 2 m como apoio intermediário, '
           'mais 4,47 m de fita e um CCB de 2 m na ponta livre, seguido do vão de meia-volta de 1,20 m.">')
det.append('<defs><marker id="pt2" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="5" markerHeight="5" '
           'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker></defs>')
# raias
det.append(f'<rect x="{x:.1f}" y="{yl-53:.1f}" width="{12.94*s+1.2*s:.1f}" height="53" fill="var(--zb)" fill-opacity=".07"/>')
det.append(f'<rect x="{x:.1f}" y="{yl:.1f}" width="{12.94*s+1.2*s:.1f}" height="53" fill="var(--zb)" fill-opacity=".07"/>')
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
    dims.append((cx, cx+w, ('fita grossa · %.2f m' % L).replace('.', ','), t))
    cx += w
xe = cx
# vao de meia-volta
det.append(f'<path d="M {xe+1.2*s*0.5:.1f} {yl-26:.1f} q {1.2*s*0.42:.1f} 26 0 52" fill="none" stroke="var(--zb)" '
           f'stroke-width="1.8" marker-end="url(#pt2)"/>')
det.append(f'<line x1="{xe:.1f}" y1="{yl-53:.1f}" x2="{xe:.1f}" y2="{yl+53:.1f}" stroke="var(--fraco)" stroke-width="1" stroke-dasharray="3 3"/>')
det.append(f'<line x1="{xe+1.2*s:.1f}" y1="{yl-53:.1f}" x2="{xe+1.2*s:.1f}" y2="{yl+53:.1f}" stroke="var(--fraco)" stroke-width="1" stroke-dasharray="3 3"/>')
det.append(f'<text x="{xe+1.2*s/2:.1f}" y="{yl+72:.1f}" text-anchor="middle" font-size="10" fill="var(--meio)">1,20 m</text>')
det.append(f'<text x="{xe+1.2*s/2:.1f}" y="{yl+85:.1f}" text-anchor="middle" font-size="9.5" fill="var(--fraco)">meia-volta</text>')
# cotas
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
det.append(f'<text x="{x:.1f}" y="{yl-70:.1f}" font-size="10.5" font-weight="700" fill="var(--meio)" letter-spacing="1.2">DIVISÓRIA DA ZONA B · 12,94 m</text>')
det.append(f'<line x1="{x:.1f}" y1="{yl-53:.1f}" x2="{x:.1f}" y2="{yl+53:.1f}" stroke="var(--rigido)" stroke-width="2.4"/>')
det.append(f'<text x="{x-6:.1f}" y="{yl+4:.1f}" text-anchor="end" font-size="9.5" fill="var(--meio)">contorno</text>')
det.append('</svg>')
detalhe = '\n'.join(det)

html = open(os.path.join(RAIZ, 'scripts', 'ring3_montagem.tpl.html')).read()
html = html.replace('<!--PLANTA-->', planta).replace('<!--DETALHE-->', detalhe)
open(os.path.join(RAIZ, 'saidas', 'ring3_montagem.html'), 'w').write(html)
print('ok', len(html))
