# -*- coding: utf-8 -*-
"""Verifica o congelamento da atribuicao secao/porta e da posicao das mesas.

Falha com AssertionError na primeira divergencia. Roda de qualquer diretorio de
trabalho e nao escreve nada: e so leitura.

    python3 scripts/verifica_congelamento.py

Congelado quer dizer: `congelado/arranjo.json` e a fonte unica de verdade; os
dois CSV sao derivados dele e tem de ser reproduziveis byte a byte; os tres
arquivos tem hash registrado em `congelado/CHECKSUMS.sha256`. Mudar o arranjo e
um ato deliberado, descrito em CONGELAMENTO.md — nao um efeito colateral.
"""
import csv, hashlib, io, json, os, sys
from collections import defaultdict

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONG = os.path.join(RAIZ, 'congelado')
ARRANJO_ESPERADO = 'paredes-abc-20260915'
APTOS_TOTAL, ESPERADO_TOTAL = 16794, 11499
N_SECOES, N_MESAS = 51, 28
TOL = 1e-9

falhas = []


def cheque(condicao, mensagem):
    if not condicao:
        falhas.append(mensagem)


def le(nome):
    with open(os.path.join(CONG, nome), encoding='utf-8', newline='') as f:
        return f.read()


D = json.loads(le('arranjo.json'))

# ---------- 1. hashes ----------
registrados = {}
for linha in le('CHECKSUMS.sha256').splitlines():
    if linha.strip():
        h, nome = linha.split('  ', 1)
        registrados[nome] = h
for nome, h in sorted(registrados.items()):
    atual = hashlib.sha256(open(os.path.join(CONG, nome), 'rb').read()).hexdigest()
    cheque(atual == h, f'hash divergente em congelado/{nome}: {atual} != {h}')
for nome in ('arranjo.json', 'atribuicao_secao_porta.csv', 'posicao_mesas.csv'):
    cheque(nome in registrados, f'congelado/{nome} nao consta de CHECKSUMS.sha256')

# ---------- 2. os CSV sao derivados do JSON ----------
por_mrv = {m['mrv']: m for m in D['mesas']}


def csv_texto(cabecalho, linhas):
    buf = io.StringIO(newline='')
    w = csv.writer(buf, lineterminator='\n')
    w.writerow(cabecalho)
    w.writerows(linhas)
    return buf.getvalue()


derivado_sec = csv_texto(
    ['secao', 'papel', 'origem_eleitor', 'aptos', 'mrv', 'mesa_numero_eleitor',
     'parede', 'entrada', 'porta'],
    [[f"{s['secao']:04d}", s['papel'], s['origem'], s['aptos'], s['mrv'],
      por_mrv[s['mrv']]['eleitor'], por_mrv[s['mrv']]['parede'],
      por_mrv[s['mrv']]['entrada'], por_mrv[s['mrv']]['porta']]
     for s in sorted(D['secoes'], key=lambda s: s['secao'])])
cheque(derivado_sec == le('atribuicao_secao_porta.csv'),
       'atribuicao_secao_porta.csv nao e mais reproduzivel a partir de arranjo.json')

derivado_mesas = csv_texto(
    ['mrv', 'mesa_numero_eleitor', 'secao_principal', 'secao_agregada', 'aptos',
     'esperado', 'classe', 'parede', 'entrada', 'porta', 'x_m', 'y_m', 'rot_graus', 'lado'],
    [[m['mrv'], m['eleitor'], f"{m['principal']:04d}",
      f"{m['agregada']:04d}" if m['agregada'] else '', m['aptos'], m['esperado'],
      m['classe'], m['parede'], m['entrada'], m['porta'],
      f"{m['x']:.2f}", f"{m['y']:.2f}", m['rot'], m['lado']]
     for m in sorted(D['mesas'], key=lambda m: m['mrv'])])
cheque(derivado_mesas == le('posicao_mesas.csv'),
       'posicao_mesas.csv nao e mais reproduzivel a partir de arranjo.json')

# ---------- 3. identidade e totais ----------
cheque(D['cenario']['id'] == ARRANJO_ESPERADO,
       f"arranjo mudou de identidade: {D['cenario']['id']} != {ARRANJO_ESPERADO}")
cheque(len(D['secoes']) == N_SECOES, f"{len(D['secoes'])} secoes, esperadas {N_SECOES}")
cheque(len(D['mesas']) == N_MESAS, f"{len(D['mesas'])} mesas, esperadas {N_MESAS}")
cheque(sum(s['aptos'] for s in D['secoes']) == APTOS_TOTAL, 'soma de aptos por secao mudou')
cheque(sum(m['aptos'] for m in D['mesas']) == APTOS_TOTAL, 'soma de aptos por mesa mudou')
cheque(sum(m['esperado'] for m in D['mesas']) == ESPERADO_TOTAL, 'soma de esperados mudou')

numeros = sorted(m['eleitor'] for m in D['mesas'])
cheque(numeros == list(range(1, N_MESAS + 1)), 'numeracao de eleitor das mesas nao vai de 1 a 28')
cheque(sorted(por_mrv) == list(range(1, N_MESAS + 1)), 'MRV das mesas nao vai de 1 a 28')
cheque(len({s['secao'] for s in D['secoes']}) == N_SECOES, 'ha secao repetida')

# ---------- 4. atribuicao secao -> mesa -> porta ----------
soma = defaultdict(int)
secoes_da_mesa = defaultdict(set)
for s in D['secoes']:
    cheque(s['mrv'] in por_mrv, f"secao {s['secao']} aponta para MRV inexistente {s['mrv']}")
    soma[s['mrv']] += s['aptos']
    secoes_da_mesa[s['mrv']].add(s['secao'])
for m in D['mesas']:
    cheque(soma[m['mrv']] == m['aptos'],
           f"MRV {m['mrv']}: aptos {m['aptos']} != soma das secoes {soma[m['mrv']]}")
    par = {m['principal']} | ({m['agregada']} if m['agregada'] else set())
    cheque(par == secoes_da_mesa[m['mrv']],
           f"MRV {m['mrv']}: par declarado {par} != secoes que apontam {secoes_da_mesa[m['mrv']]}")
    cheque(1 <= len(par) <= 2, f"MRV {m['mrv']} tem {len(par)} secoes")

# uma entrada por parede, uma parede por entrada, e a porta de cada uma
paredes = defaultdict(set)
carga = defaultdict(lambda: [0, 0])
for m in D['mesas']:
    paredes[m['parede']].add((m['entrada'], m['porta']))
    carga[m['entrada']][0] += 1
    carga[m['entrada']][1] += m['esperado']
for parede, pares in sorted(paredes.items()):
    cheque(len(pares) == 1, f'parede {parede} servida por mais de uma entrada: {pares}')
cheque(len(paredes) == len(D['entradas']), 'numero de paredes != numero de entradas')

portas = {p['id']: p for p in D['portas']}
for e in D['entradas']:
    cheque(carga[e['id']] == [e['mesas'], e['esperado']],
           f"entrada {e['id']}: {carga[e['id']]} != [{e['mesas']}, {e['esperado']}]")
    cheque(paredes[e['parede']] == {(e['id'], e['porta'])},
           f"entrada {e['id']} nao casa com a parede {e['parede']}")
    cheque(portas.get(e['porta'], {}).get('estado') == 'entrada',
           f"porta {e['porta']} da entrada {e['id']} nao esta marcada como entrada")

# ---------- 5. geometria das mesas ----------
LARG, ALT = D['salao']['largura'], D['salao']['altura']
PROF, LARG_MOD = D['modulo']['prof'], D['modulo']['larg']
rx0, ry0, rx1, ry1 = D['salao']['recorte']
faixa = {}
for z in D['zonas']:
    if z['tipo'] == 'faixa_emergencia':
        zx0, _, zx1, _ = z['rect']
        faixa['leste'] = zx1 - zx0

ancora = {'oeste': (0.0, 0), 'norte': (ALT, 270),
          'leste': (LARG - faixa.get('leste', 0.0), 180)}


def retangulo(m):
    """Pegada da mesa: encosta a parede em (x,y) e avanca `prof` para dentro."""
    dx, dy = {0: (1, 0), 90: (0, 1), 180: (-1, 0), 270: (0, -1)}[m['rot']]
    px_, py_ = -dy, dx
    xs = [m['x'] + dx * u + px_ * v for u in (0, PROF) for v in (-LARG_MOD / 2, LARG_MOD / 2)]
    ys = [m['y'] + dy * u + py_ * v for u in (0, PROF) for v in (-LARG_MOD / 2, LARG_MOD / 2)]
    return min(xs), min(ys), max(xs), max(ys)


def sobrepoe(a, b):
    return (min(a[2], b[2]) - max(a[0], b[0]) > TOL and
            min(a[3], b[3]) - max(a[1], b[1]) > TOL)


ao_longo = defaultdict(list)
for m in D['mesas']:
    cheque(m['parede'] in ancora, f"MRV {m['mrv']}: parede desconhecida {m['parede']}")
    if m['parede'] not in ancora:
        continue
    coord, rot = ancora[m['parede']]
    eixo = m['x'] if m['parede'] in ('oeste', 'leste') else m['y']
    cheque(abs(eixo - coord) < 1e-6,
           f"MRV {m['mrv']} fora da linha da parede {m['parede']}: {eixo} != {coord}")
    cheque(m['rot'] == rot, f"MRV {m['mrv']} com rotacao {m['rot']}, esperada {rot}")

    r = retangulo(m)
    cheque(r[0] >= -TOL and r[1] >= -TOL and r[2] <= LARG + TOL and r[3] <= ALT + TOL,
           f"MRV {m['mrv']} sai do contorno do salao: {r}")
    cheque(not sobrepoe(r, (rx0, ry0, rx1, ry1)),
           f"MRV {m['mrv']} invade o recorte sudoeste do salao")
    for z in D['zonas']:
        zx0, zy0, zx1, zy1 = z['rect']
        cheque(not sobrepoe(r, (zx0, zy0, zx1, zy1)),
               f"MRV {m['mrv']} invade a zona livre {z['tipo']} ({z.get('porta')})")
    ao_longo[m['parede']].append((m['y'] if m['parede'] in ('oeste', 'leste') else m['x'],
                                  m['mrv']))

for parede, itens in sorted(ao_longo.items()):
    itens.sort()
    for (c1, a), (c2, b) in zip(itens, itens[1:]):
        cheque(c2 - c1 >= LARG_MOD - TOL,
               f'MRV {a} e {b} se tocam na parede {parede}: {c2 - c1:.2f} m entre eixos')

for sp in D['serpenteados']:
    m = por_mrv.get(sp['mrv'])
    cheque(m is not None and m['parede'] == sp['parede'],
           f"serpenteado do MRV {sp['mrv']} nao casa com a parede da mesa")
    cheque(m is not None and m['classe'] == 'alta',
           f"serpenteado reservado para o MRV {sp['mrv']}, que nao e mesa de carga alta")

# ---------- 6. cruzamento com a analise das agregacoes, se estiver presente ----------
dados = os.path.join(RAIZ, 'saidas', 'dados.json')
if os.path.exists(dados):
    with open(dados, encoding='utf-8') as f:
        ag = json.load(f)
    urnas = {u['Urna']: u for u in ag['urnas']}
    cheque(ag['total_eleitores'] == APTOS_TOTAL, 'dados.json discorda do total de aptos')
    cheque(len(urnas) == N_MESAS, 'dados.json discorda do numero de urnas')
    for m in D['mesas']:
        u = urnas.get(m['principal'])
        cheque(u is not None, f"MRV {m['mrv']}: secao principal {m['principal']} nao e urna no TSE")
        if u is None:
            continue
        bruto = u['Secao_agregada']
        # urna de uma secao so vem como null ou NaN no dados.json
        agregada = None if bruto is None or bruto != bruto else int(bruto)
        cheque(agregada == m['agregada'],
               f"MRV {m['mrv']}: agregada {m['agregada']} != {agregada} no TSE")
        cheque(u['Total_combinado'] == m['aptos'],
               f"MRV {m['mrv']}: aptos {m['aptos']} != {u['Total_combinado']} no TSE")
    origem = 'conferido contra saidas/dados.json'
else:
    origem = 'saidas/dados.json ausente — cruzamento com o TSE pulado'

if falhas:
    print(f'CONGELAMENTO ROMPIDO — {len(falhas)} divergencia(s):', file=sys.stderr)
    for f_ in falhas:
        print(f'  - {f_}', file=sys.stderr)
    print('\nSe a mudanca foi deliberada, siga "Como descongelar" em CONGELAMENTO.md.',
          file=sys.stderr)
    sys.exit(1)

print(f"congelamento intacto — arranjo {D['cenario']['id']} ({D['cenario']['nome']})")
print(f'  {N_SECOES} secoes -> {N_MESAS} mesas -> 3 portas | {APTOS_TOTAL} aptos | '
      f'{ESPERADO_TOTAL} esperados')
for e in D['entradas']:
    print(f"  entrada {e['id']} · porta {e['porta']} · parede {e['parede']:6s} · "
          f"{e['mesas']} mesas · {e['esperado']} esperados")
print(f'  {origem}')
