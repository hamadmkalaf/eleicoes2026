"""Calcula as simulacoes de ocupacao e grava as saidas.

    saidas/mesas.json                    todos os numeros da peca de leitura
    saidas/mesas_modulo.svg              o modulo e o passo do par
    saidas/mesas_reguas_{A,B}.svg        as reguas de parede
    saidas/mesas_cenario_{A,B}.svg       o maximo em parede real
    saidas/mesas_cenario_{A,B}_div.svg   o mesmo, com a divisoria do miolo
    saidas/mesas.html                    a peca de leitura
"""
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "scripts"))

import salao as FL                                            # noqa: E402
import mesas as MM                                            # noqa: E402
import planta_mesas as PM                                     # noqa: E402
import desenho as D                                           # noqa: E402

SAIDAS = os.path.join(RAIZ, "saidas")

# A divisoria proposta: atravessada no miolo, longe do corredor do catering
# (N2) e do caminho dos sanitarios (O2), com 3 m livres em toda a volta.
DIVISORIA = dict(nome="D1", eixo="h", fixo=31.4, s0=16.0, s1=33.4)

NOME_FACE = PM.NOME_FACE
SUBTITULO = {"A": "S1 e S7 fora de uso",
             "B": "S1 e S7 em uso, com divisória a 2 m do vão"}
NOTA_FLUXO = ("O corredor de cada par é o espaço de encaminhamento: o eleitor "
              "entra por ele, passa pelos três mesários, vota de costas para o "
              "salão e sai pelo mesmo corredor.")


def vg(x, casas=2):
    return f"{x:.{casas}f}".replace(".", ",")


def milhar(n):
    return f"{int(round(n)):,}".replace(",", ".")


def grava(nome, conteudo):
    cam = os.path.join(SAIDAS, nome)
    open(cam, "w", encoding="utf-8").write(conteudo)
    return cam


def notas_de_choque(r):
    return [f"Conflito: {c['a']} e {c['b']} disputam "
            f"{vg(c['area'], 1)} m² do mesmo chão." for c in r["choques"]]


def main():
    os.makedirs(SAIDAS, exist_ok=True)
    passo_max = MM.passo_do_par(MM.CORREDOR_MAX)

    out = dict(
        modulo=dict(mesa_identificacao=list(MM.MESA_IDENT), urna=MM.URNA_D,
                    profundidade=MM.PROF, largura=MM.LARG,
                    folga_eleitor=MM.FOLGA_ELEITOR, passagem=MM.PASSAGEM,
                    assento_mesario=MM.MESARIO_ASSENTO,
                    corredor=[MM.CORREDOR_MIN, MM.CORREDOR_MAX],
                    entre_pares=MM.ENTRE_PARES,
                    passo_par=[MM.passo_do_par(MM.CORREDOR_MIN), passo_max],
                    parede_por_mesa=[MM.passo_do_par(MM.CORREDOR_MIN) / 2,
                                     passo_max / 2]),
        necessario=MM.URNAS,
        parede_para_28=[round(MM.URNAS * MM.passo_do_par(MM.CORREDOR_MIN) / 2, 1),
                        round(MM.URNAS * passo_max / 2, 1)],
        perimetro=round(sum(f["s1"] - f["s0"] for f in FL.FACES.values()), 1),
        vaos=round(sum(b - a for face in FL.FACES
                       for _c, a, b in FL.portas_da_face(face)), 1),
        matriz=[], cenarios={})

    for cen in ("A", "B"):
        for hip in MM.HIPOTESES:
            for a in (MM.CORREDOR_MIN, MM.CORREDOR_MAX):
                r = MM.roda(cen, hip, a, ordem=MM.ORDEM)
                assert not r["erros"], r["erros"]
                out["matriz"].append(dict(
                    cenario=cen, hipotese=hip, corredor=a, mrv=r["mrv"],
                    por_face={k: v["mrv"] for k, v in r["por_face"].items() if v["mrv"]}))

    for cen in ("A", "B"):
        base = MM.roda(cen, "prudente", MM.CORREDOR_MAX, ordem=MM.ORDEM)
        div = MM.roda_com_divisorias(cen, "prudente", MM.CORREDOR_MAX, [dict(DIVISORIA)])
        for r in (base, div):
            assert not r["erros"], r["erros"]

        livre = util = 0.0
        for d in base["por_face"].values():
            for t in d["trechos"]:
                livre += t["livre"]
                if t["pares"]:
                    util += t["livre"] - t["sobra"]

        out["cenarios"][cen] = dict(
            mrv=base["mrv"], mrv_com_divisoria=div["mrv"],
            por_face={k: v["mrv"] for k, v in base["por_face"].items() if v["mrv"]},
            trechos={k: v["trechos"] for k, v in base["por_face"].items()},
            parede_livre=round(livre, 1), parede_util=round(util, 1),
            area_faixas=round(base["mrv"] // 2 * passo_max * MM.PROF, 0),
            divisoria=div["divisorias"][0], choques=base["choques"])

        grava(f"mesas_cenario_{cen}.svg", PM.planta(
            f"CENÁRIO {cen} — {base['mrv']} mesas receptoras", SUBTITULO[cen], base,
            notas=[NOTA_FLUXO,
                   f"Máximo em parede real. Faltam {MM.URNAS - base['mrv']} das "
                   f"{MM.URNAS} urnas."] + notas_de_choque(base)))

        grava(f"mesas_cenario_{cen}_div.svg", PM.planta(
            f"CENÁRIO {cen} + DIVISÓRIA — {div['mrv']} mesas receptoras",
            f"{SUBTITULO[cen]}; divisória exenta de "
            f"{vg(div['divisorias'][0]['comprimento'], 1)} m no miolo",
            div, divisorias=[DIVISORIA],
            notas=[NOTA_FLUXO,
                   "A divisória do miolo é parede pelas duas faces: um só elemento "
                   "serve a duas fileiras de módulos e fecha a conta das 28 urnas "
                   "com duas de folga."] + notas_de_choque(div)))

        grava(f"mesas_reguas_{cen}.svg", PM.reguas(cen))

    grava("mesas_modulo.svg", PM.figura_modulo())

    teto, esc = MM.teto_com_divisorias("A", "prudente", MM.CORREDOR_MAX, maximo=6)
    assert not teto["erros"], teto["erros"]
    out["teto"] = dict(mrv=teto["mrv"], divisorias=len(esc))

    grava("mesas.json", json.dumps(out, ensure_ascii=False, indent=2))
    grava("mesas.html", pagina(out))

    print(f"perímetro {out['perimetro']} m · vãos {out['vaos']} m")
    for m in out["matriz"]:
        print(f"  {m['cenario']} · recuo {m['hipotese']:9s} · A={m['corredor']:.2f}"
              f" -> {m['mrv']:2d}  {m['por_face']}")
    for c, v in out["cenarios"].items():
        print(f"  cenário {c}: {v['mrv']} no perímetro, {v['mrv_com_divisoria']} com "
              f"divisória; parede livre {v['parede_livre']} m, útil {v['parede_util']} m")
    print(f"  teto com {out['teto']['divisorias']} divisórias: {out['teto']['mrv']}")


# ----------------------------------------------------------- peca de leitura
def pagina(d):
    A, B = d["cenarios"]["A"], d["cenarios"]["B"]

    linhas = []
    for face, trechos in A["trechos"].items():
        livre = sum(t["livre"] for t in trechos)
        maior = max((t["livre"] for t in trechos), default=0.0)
        n = A["por_face"].get(face, 0)
        linhas.append(f'<tr><td>{NOME_FACE[face]}</td>'
                      f'<td class="num">{len(trechos)}</td>'
                      f'<td class="num">{vg(livre, 1)}</td>'
                      f'<td class="num">{vg(maior, 1)}</td>'
                      f'<td class="num{"" if n else " nulo"}">{n or "—"}</td></tr>')
    linhas.append(f'<tr class="somatorio"><td>total</td>'
                  f'<td class="num">{sum(len(t) for t in A["trechos"].values())}</td>'
                  f'<td class="num">{vg(A["parede_livre"], 1)}</td>'
                  f'<td class="num">—</td><td class="num">{A["mrv"]}</td></tr>')

    def mrv(cen, hip, corr):
        return next(x["mrv"] for x in d["matriz"] if x["cenario"] == cen
                    and x["hipotese"] == hip and x["corredor"] == corr)

    matriz = []
    for cen in ("A", "B"):
        for hip, rot in (("prudente", "3 m em todas as saídas de emergência"),
                         ("minima", "3 m só na parede leste, como está determinado")):
            matriz.append(f'<tr><td>cenário {cen}</td><td>{rot}</td>'
                          f'<td class="num">{mrv(cen, hip, 2.5)}</td>'
                          f'<td class="num">{mrv(cen, hip, 3.0)}</td>'
                          f'<td class="num nulo">0</td></tr>')

    maxb = d["perimetro"]
    def barra(v, cls):
        return (f'<span class="trilho"><span class="{cls}" '
                f'style="width:{v / maxb * 100:.2f}%"></span></span>')

    conta = [
        ("Perímetro do salão", "quatro fachadas mais as duas faces do recorte",
         d["perimetro"], "b-bruto"),
        ("Parede livre", "descontados vãos, recuos de emergência e cantos",
         A["parede_livre"], "b-livre"),
        ("Parede aproveitável", "só os trechos com 6,30 m contínuos",
         A["parede_util"], "b-util"),
        ("O que 28 urnas pedem", "a 3,15 m de parede por urna",
         d["parede_para_28"][1], "b-pedido"),
    ]
    conta_html = "".join(
        f'<div class="linha-conta{" pedido" if cls == "b-pedido" else ""}">'
        f'<span class="rot">{rot}<small>{sub}</small></span>{barra(v, cls)}'
        f'<span class="val">{vg(v, 1)} m</span></div>'
        for rot, sub, v, cls in conta)

    choques = "".join(
        f'<li><span class="mono">{c["a"]}</span> e <span class="mono">{c["b"]}</span>'
        f' disputam <span class="mono">{vg(c["area"], 1)} m²</span> do mesmo chão.</li>'
        for c in B["choques"])

    ARTIGO = {"norte": "na parede norte", "oeste": "na oeste", "sul": "na sul",
              "leste": "na leste", "recorte_h": "na face norte do recorte",
              "recorte_v": "na face leste do recorte"}
    ordem = ["norte", "oeste", "sul", "leste", "recorte_h", "recorte_v"]
    partes = [f"{A['por_face'][f]} {ARTIGO[f]}" for f in ordem if A["por_face"].get(f)]
    det_a = (", ".join(partes[:-1]) + " e " + partes[-1]) if len(partes) > 1 else partes[0]

    sub = {
        "estilo": D.estilo(),
        "mrv": str(A["mrv"]), "mrv_b": str(B["mrv"]),
        "mrv_div": str(A["mrv_com_divisoria"]),
        "mrv_div_b": str(B["mrv_com_divisoria"]),
        "piso_livre": milhar(FL.HALL_W * FL.HALL_H - FL.RECORTE[2] * FL.RECORTE[3]
                             - A["area_faixas"]),
        "parede_28": vg(d["parede_para_28"][1], 1),
        "parede_util": vg(A["parede_util"], 1),
        "parede_livre": vg(A["parede_livre"], 1),
        "perimetro": vg(d["perimetro"], 1), "vaos": vg(d["vaos"], 1),
        "div_comp": vg(A["divisoria"]["comprimento"], 1),
        "div_mrv": str(A["divisoria"]["mrv"]),
        "div_face": str(A["divisoria"]["faces"][0]),
        "teto": str(d["teto"]["mrv"]), "teto_div": str(d["teto"]["divisorias"]),
        "det_a": det_a, "conta": conta_html, "choques": choques,
        "tabela_paredes": "".join(linhas), "matriz": "".join(matriz),
    }
    for nome, arq in (("svg_modulo", "mesas_modulo.svg"),
                      ("svg_reguas", "mesas_reguas_A.svg"),
                      ("svg_a", "mesas_cenario_A.svg"),
                      ("svg_b", "mesas_cenario_B.svg"),
                      ("svg_a_div", "mesas_cenario_A_div.svg"),
                      ("svg_b_div", "mesas_cenario_B_div.svg")):
        sub[nome] = open(os.path.join(SAIDAS, arq), encoding="utf-8").read()

    html = open(os.path.join(RAIZ, "scripts", "mesas_template.html"),
                encoding="utf-8").read()
    for k, v in sub.items():
        html = html.replace(f"@@{k}@@", v)
    if "@@" in html:
        raise SystemExit("placeholder nao substituido: " + html.split("@@")[1])
    return html


if __name__ == "__main__":
    main()
