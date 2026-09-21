"""A fonte unica da identidade das zonas: zona = porta = parede = cor.

Todo script que precise saber a cor de uma zona, a porta que a serve ou a
parede que ela atende importa isto -- nunca declara por conta propria. O
arquivo que manda e ``data/zonas.json``; este modulo so o le e oferece os
atalhos que os consumidores usam.

    import zonas
    zonas.HEX["A"]       # '#33507E'
    zonas.PAREDE["A"]    # 'oeste'
    zonas.PORTA["A"]     # 'S4'
    zonas.CORES["A"]     # ('azul', '#33507E')  -- o formato do arranjo_paredes
    zonas.ESTOQUE["A"]   # 165.0

Para conferir um consumidor contra a fonte, ``scripts/confere_zonas.py``.
"""
import json
import os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAMINHO = os.path.join(RAIZ, "data", "zonas.json")


def carrega(caminho=CAMINHO):
    with open(caminho, encoding="utf-8") as f:
        return json.load(f)


_D = carrega()

ZONAS = {z["id"]: z for z in _D["zonas"]}
IDS = tuple(sorted(ZONAS))
HEX = {i: z["hex"] for i, z in ZONAS.items()}
NOME_COR = {i: z["cor"] for i, z in ZONAS.items()}
PORTA = {i: z["porta"] for i, z in ZONAS.items()}
PAREDE = {i: z["parede"] for i, z in ZONAS.items()}
ESTOQUE = {i: z["estoque_fita_m"] for i, z in ZONAS.items()}
AUXILIARES = _D["auxiliares"]
CONSUMIDORES = _D["consumidores"]

# Os formatos que os consumidores ja usavam, agora derivados e nao declarados.
CORES = {i: (NOME_COR[i], HEX[i]) for i in IDS}          # arranjo_paredes.py
ENTRADA_DE_PAREDE = {PAREDE[i]: i for i in IDS}          # parede -> zona
ZONA_DE_PORTA = {PORTA[i]: i for i in IDS}               # porta  -> zona


def normaliza(h):
    """Hex comparavel: sem espaco, maiusculo, com '#'."""
    h = (h or "").strip().upper()
    return h if h.startswith("#") else "#" + h


def clareia(h, f=0.55):
    """A variante clara de uma cor de zona, para fundo escuro.

    O plano de sinalizacao precisa de um par claro/escuro por zona. Derivar
    aqui evita que alguem declare um segundo conjunto de cores que possa sair
    do lugar sozinho.
    """
    h = normaliza(h).lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    mistura = lambda c: round(c + (255 - c) * f)
    return "#%02X%02X%02X" % (mistura(r), mistura(g), mistura(b))


def divergencias(mapa, rotulo, campo="hex"):
    """Confere um {zona: hex} contra a fonte. Devolve a lista de diferencas."""
    faltas = []
    for i in IDS:
        if i not in mapa:
            faltas.append(f"{rotulo}: zona {i} ausente")
            continue
        if normaliza(mapa[i]) != normaliza(HEX[i]):
            faltas.append(f"{rotulo}: zona {i} tem {normaliza(mapa[i])}, "
                          f"a fonte diz {normaliza(HEX[i])} ({NOME_COR[i]})")
    for i in mapa:
        if i not in IDS:
            faltas.append(f"{rotulo}: zona {i} não existe na fonte")
    return faltas


# Duas cores de zona iguais seriam pior do que nenhuma cor: o eleitor nao teria
# como distinguir as filas. Isto falha no import, antes de qualquer desenho.
_vistos = {}
for _i in IDS:
    _h = normaliza(HEX[_i])
    if _h in _vistos:
        raise ValueError(f"data/zonas.json: zonas {_vistos[_h]} e {_i} têm a "
                         f"mesma cor {_h} — cor de zona tem de ser única")
    _vistos[_h] = _i
for _k, _a in AUXILIARES.items():
    _h = normaliza(_a["hex"])
    if _h in _vistos:
        raise ValueError(f"data/zonas.json: a cor auxiliar '{_k}' ({_h}) "
                         f"colide com a zona {_vistos[_h]}")
    _vistos[_h] = _k
