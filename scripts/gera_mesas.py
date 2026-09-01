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

# A divisoria exenta do miolo deixou de ser necessaria quando a fachada leste
# passou a receber a fileira recuada. Fica registrada porque ainda e a resposta
# se alguma das premissas cair — se o RDS exigir os envelopes por porta em vez
# da faixa continua, por exemplo.
DIVISORIA = dict(nome="D1", eixo="h", fixo=31.4, s0=26.0, s1=37.1)

# Duas leituras da folga: o maximo empacota com os minimos da faixa que o
# usuario deu (2,50 dentro do par, 1,00 entre pares); o recomendado exige os
# maximos (3,00 e 1,50) e ainda assim fecha as 28.
A_MAXIMO, A_RECOMENDADO = MM.CORREDOR_MIN, MM.CORREDOR_MAX

NOME_FACE = PM.NOME_FACE
SUBTITULO = {"A": "S1 e S7 fora de uso",
             "B": "S1 e S7 em uso, com divisória a 2 m do vão"}
FACES_REAIS = ["norte", "leste", "sul", "oeste", "recorte_v", "recorte_h"]
NOME_FACE_TXT = {"norte": "parede norte", "oeste": "oeste", "sul": "sul",
                 "leste": "leste", "recorte_h": "face norte do recorte",
                 "recorte_v": "face leste do recorte",
                 MM.FACE_LESTE_RECUADA: "fileira recuada da fachada leste"}
NOTA_FLUXO = ("O corredor de cada par é o espaço de encaminhamento: o eleitor entra "
              "por ele, passa pelos três mesários e chega à urna, que fica voltada "
              "para a parede — a tela aponta para ela e não é vista do salão.")


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
    passo_min = MM.passo_do_par(MM.CORREDOR_MIN, MM.ENTRE_PARES_MIN)
    passo_max = MM.passo_do_par(MM.CORREDOR_MAX, MM.ENTRE_PARES_MAX)

    out = dict(
        modulo=dict(mesa_identificacao=list(MM.MESA_IDENT), urna=MM.URNA_D,
                    profundidade=MM.PROF, largura=MM.LARG,
                    folga_eleitor=MM.FOLGA_ELEITOR, passagem=MM.PASSAGEM,
                    assento_mesario=MM.MESARIO_ASSENTO,
                    corredor=[MM.CORREDOR_MIN, MM.CORREDOR_MAX],
                    entre_pares=[MM.ENTRE_PARES_MIN, MM.ENTRE_PARES_MAX],
                    faixa_leste=MM.FAIXA_LESTE,
                    passo_par=[passo_min, passo_max],
                    frente_por_mesa=[passo_min / 2, passo_max / 2]),
        necessario=MM.URNAS,
        frente_para_28=[round(MM.URNAS * passo_min / 2, 1),
                        round(MM.URNAS * passo_max / 2, 1)],
        perimetro=round(sum(FL.FACES[f]["s1"] - FL.FACES[f]["s0"]
                            for f in FACES_REAIS), 1),
        vaos=round(sum(b - a for face in FACES_REAIS
                       for _c, a, b in FL.portas_da_face(face)), 1),
        area_faixa_leste=round(FL.HALL_H * MM.FAIXA_LESTE, 0),
        area_envelopes=round(sum(
            (min(FL.HALL_H, b + FL.RECUO_EMERGENCIA)
             - max(0.0, a - FL.RECUO_EMERGENCIA)) * FL.RECUO_EMERGENCIA
            for _c, a, b in FL.portas_da_face("leste")), 0),
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
        maximo = MM.roda(cen, "prudente", A_MAXIMO, ordem=MM.ORDEM)
        recom = MM.roda(cen, "prudente", A_RECOMENDADO, ordem=MM.ORDEM)
        for r in (maximo, recom):
            assert not r["erros"], r["erros"]

        def frente(r):
            return round(sum(t["livre"] - t["sobra"]
                             for d in r["por_face"].values() for t in d["trechos"]
                             if t["pares"] or t["avulsas"]), 1)

        fileira = [t for t in maximo["por_face"][MM.FACE_LESTE_RECUADA]["trechos"]
                   if t["pares"]][0]
        fileira_r = [t for t in recom["por_face"][MM.FACE_LESTE_RECUADA]["trechos"]
                     if t["pares"]][0]

        out["cenarios"][cen] = dict(
            mrv=maximo["mrv"], mrv_recomendado=recom["mrv"],
            por_face={k: v["mrv"] for k, v in maximo["por_face"].items() if v["mrv"]},
            por_face_recomendado={k: v["mrv"] for k, v in recom["por_face"].items()
                                  if v["mrv"]},
            trechos={k: v["trechos"] for k, v in maximo["por_face"].items()},
            frente=frente(maximo), frente_recomendado=frente(recom),
            fileira_leste=fileira, fileira_leste_recomendada=fileira_r,
            area_faixas=round(frente(recom) * MM.PROF, 0),
            choques=maximo["choques"])

        grava(f"mesas_cenario_{cen}.svg", PM.planta(
            f"CENÁRIO {cen} — {maximo['mrv']} mesas receptoras",
            f"{SUBTITULO[cen]}; máximo, com as folgas no mínimo da faixa "
            f"(2,50 m dentro do par, 1,00 m entre pares)", maximo,
            notas=[NOTA_FLUXO,
                   "A fachada leste tem uma faixa protegida de 3 m ao longo de "
                   "toda a sua extensão; a fileira começa logo depois dela, "
                   "alinhada, e por isso as quatro saídas não a recortam."]
                  + notas_de_choque(maximo)))

        grava(f"mesas_cenario_{cen}_folga.svg", PM.planta(
            f"CENÁRIO {cen} COM FOLGA CHEIA — {recom['mrv']} mesas receptoras",
            f"{SUBTITULO[cen]}; 3,00 m dentro do par e 1,50 m entre pares",
            recom,
            notas=[NOTA_FLUXO,
                   f"Quatro mesas a menos que o máximo, e ainda "
                   f"{recom['mrv'] - MM.URNAS} acima das {MM.URNAS} urnas "
                   f"exigidas."] + notas_de_choque(recom)))

        grava(f"mesas_reguas_{cen}.svg", PM.reguas(cen))

    grava("mesas_leste.svg", PM.compara_leste())
    grava("mesas_modulo.svg", PM.figura_modulo())

    div = MM.roda_com_divisorias("A", "prudente", A_RECOMENDADO, [dict(DIVISORIA)])
    assert not div["erros"], div["erros"]
    out["divisoria"] = dict(mrv=div["mrv"], acrescimo=div["divisorias"][0]["mrv"],
                            comprimento=div["divisorias"][0]["comprimento"])

    grava("mesas.json", json.dumps(out, ensure_ascii=False, indent=2))
    grava("mesas.html", pagina(out))

    print(f"perímetro {out['perimetro']} m · vãos {out['vaos']} m")
    for m in out["matriz"]:
        print(f"  {m['cenario']} · recuo {m['hipotese']:9s} · A={m['corredor']:.2f}"
              f" -> {m['mrv']:2d}  {m['por_face']}")
    for c, v in out["cenarios"].items():
        f = v["fileira_leste"]
        print(f"  cenário {c}: máximo {v['mrv']}, com folga cheia "
              f"{v['mrv_recomendado']}; frente {v['frente']} m; fileira leste "
              f"{f['pares']} pares em {f['livre']} m")


# ----------------------------------------------------------- peca de leitura
def pagina(d):
    A, B = d["cenarios"]["A"], d["cenarios"]["B"]
    fil, filf = A["fileira_leste"], A["fileira_leste_recomendada"]

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
                  f'<td class="num">—</td><td class="num">—</td>'
                  f'<td class="num">{A["mrv"]}</td></tr>')

    def mrv(cen, hip, corr):
        return next(x["mrv"] for x in d["matriz"] if x["cenario"] == cen
                    and x["hipotese"] == hip and x["corredor"] == corr)

    matriz = []
    for cen in ("A", "B"):
        for hip, rot in (("prudente", "3 m em todas as saídas de emergência"),
                         ("minima", "3 m só na fachada leste, como está determinado")):
            mn, mx = mrv(cen, hip, A_MAXIMO), mrv(cen, hip, A_RECOMENDADO)
            matriz.append(f'<tr><td>cenário {cen}</td><td>{rot}</td>'
                          f'<td class="num">{mn}</td><td class="num">{mx}</td>'
                          f'<td class="num">{mx - mn}</td></tr>')

    choques = "".join(
        f'<li><span class="mono">{c["a"]}</span> e <span class="mono">{c["b"]}</span>'
        f' disputam <span class="mono">{vg(c["area"], 1)} m²</span> do mesmo chão.</li>'
        for c in B["choques"])

    ordem = ["norte", "oeste", "sul", "recorte_h", "recorte_v",
             MM.FACE_LESTE_RECUADA]
    artigo = {"norte": "na parede norte", "oeste": "na oeste", "sul": "na sul",
              "recorte_h": "na face norte do recorte",
              "recorte_v": "na face leste do recorte",
              MM.FACE_LESTE_RECUADA: "na fileira recuada da fachada leste"}
    partes = [f"{A['por_face'][f]} {artigo[f]}" for f in ordem if A["por_face"].get(f)]
    det_a = ", ".join(partes[:-1]) + " e " + partes[-1]

    passagem = fil["corredor"] - 2 * MM.MESARIO_ASSENTO
    sub = {
        "estilo": D.estilo(),
        "mrv": str(A["mrv"]), "mrv_b": str(B["mrv"]),
        "mrv_folga": str(A["mrv_recomendado"]),
        "sobra_folga": str(A["mrv_recomendado"] - MM.URNAS),
        "fileira_mrv": str(2 * fil["pares"]), "fileira_pares": str(fil["pares"]),
        "fileira_livre": vg(fil["livre"], 1),
        "fileira_mrv_folga": str(2 * filf["pares"]),
        "fileira_pares_folga": str(filf["pares"]),
        "corr_max": vg(fil["corredor"], 2),
        "passagem_max": vg(passagem, 2),
        "frente": vg(A["frente"], 1),
        "frente_28": vg(d["frente_para_28"][1], 1),
        "frente_28_min": vg(d["frente_para_28"][0], 1),
        "perimetro": vg(d["perimetro"], 1), "vaos": vg(d["vaos"], 1),
        "area_faixa": milhar(d["area_faixa_leste"]),
        "area_envelopes": milhar(d["area_envelopes"]),
        "div_comp": vg(d["divisoria"]["comprimento"], 1),
        "div_acrescimo": str(d["divisoria"]["acrescimo"]),
        "div_mrv": str(d["divisoria"]["mrv"]),
        "det_a": det_a, "choques": choques,
        "tabela_faces": "".join(linhas), "matriz": "".join(matriz),
    }
    for nome, arq in (("svg_modulo", "mesas_modulo.svg"),
                      ("svg_leste", "mesas_leste.svg"),
                      ("svg_reguas", "mesas_reguas_A.svg"),
                      ("svg_a", "mesas_cenario_A.svg"),
                      ("svg_b", "mesas_cenario_B.svg"),
                      ("svg_a_folga", "mesas_cenario_A_folga.svg")):
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
