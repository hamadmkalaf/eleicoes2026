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

# Tres leituras. O maximo empacota com os minimos da faixa que o usuario deu
# (2,50 dentro do par, 1,00 entre pares) e serviu de teste de capacidade; a
# folga cheia exige os maximos (3,00 e 1,50); a planta final e a folga cheia
# menos as duas MRVs que o usuario escolheu tirar sobre o desenho (AJUSTE_28).
A_MAXIMO, A_FOLGA = MM.CORREDOR_MIN, MM.CORREDOR_MAX

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
        final = MM.roda(cen, "prudente", A_FOLGA, ordem=MM.ORDEM,
                        ajustes=MM.AJUSTE_28)
        folga = MM.roda(cen, "prudente", A_FOLGA, ordem=MM.ORDEM)
        maximo = MM.roda(cen, "prudente", A_MAXIMO, ordem=MM.ORDEM)
        for r in (final, folga, maximo):
            assert not r["erros"], r["erros"]
        assert final["mrv"] == MM.URNAS, final["mrv"]

        def frente(r):
            return round(sum(t["livre"] - t["sobra"]
                             for d in r["por_face"].values() for t in d["trechos"]
                             if t["pares"] or t["avulsas"]), 1)

        fileira = [t for t in final["por_face"][MM.FACE_LESTE_RECUADA]["trechos"]
                   if t["pares"]][0]

        out["cenarios"][cen] = dict(
            mrv=final["mrv"], mrv_folga=folga["mrv"], mrv_maximo=maximo["mrv"],
            por_face={k: v["mrv"] for k, v in final["por_face"].items() if v["mrv"]},
            trechos={k: v["trechos"] for k, v in final["por_face"].items()},
            frente=frente(final), fileira_leste=fileira,
            corredor_maximo=[t for t in
                             maximo["por_face"][MM.FACE_LESTE_RECUADA]["trechos"]
                             if t["pares"]][0]["corredor"],
            choques=final["choques"])

        grava(f"mesas_cenario_{cen}.svg", PM.planta(
            f"CENÁRIO {cen} — {final['mrv']} mesas receptoras",
            f"{SUBTITULO[cen]}; 3,00 m dentro do par e 1,50 m entre pares",
            final,
            notas=[NOTA_FLUXO,
                   "A fachada leste tem uma faixa protegida de 3 m ao longo de toda "
                   "a sua extensão; a fileira começa logo depois dela, alinhada, e "
                   "por isso as quatro saídas não a recortam."]
                  + notas_de_choque(final)))

        grava(f"mesas_reguas_{cen}.svg", PM.reguas(cen, ajustes=MM.AJUSTE_28))

    grava("mesas_leste.svg", PM.compara_leste())
    grava("mesas_modulo.svg", PM.figura_modulo())

    # Plano B: se o RDS nao aceitar a faixa continua, a fachada leste volta a
    # valer tres MRVs avulsas e a divisoria exenta do miolo fecha a conta.
    sem = MM.roda("A", "prudente", A_FOLGA, ordem=MM.ORDEM, faixa_leste=False)
    div = MM.roda_com_divisorias("A", "prudente", A_FOLGA, [dict(DIVISORIA)],
                                 faixa_leste=False)
    for r in (sem, div):
        assert not r["erros"], r["erros"]
    out["plano_b"] = dict(
        mrv=sem["mrv"], leste=sem["por_face"]["leste"]["mrv"],
        com_divisoria=div["mrv"], acrescimo=div["divisorias"][0]["mrv"],
        comprimento=div["divisorias"][0]["comprimento"])

    grava("mesas.json", json.dumps(out, ensure_ascii=False, indent=2))
    grava("mesas.html", pagina(out))

    print(f"perímetro {out['perimetro']} m · vãos {out['vaos']} m")
    for m in out["matriz"]:
        print(f"  {m['cenario']} · recuo {m['hipotese']:9s} · A={m['corredor']:.2f}"
              f" -> {m['mrv']:2d}  {m['por_face']}")
    for c, v in out["cenarios"].items():
        f = v["fileira_leste"]
        print(f"  cenário {c}: planta final {v['mrv']} · folga cheia "
              f"{v['mrv_folga']} · máximo {v['mrv_maximo']}; frente {v['frente']} m; "
              f"fileira leste {f['pares']} pares em {f['livre']} m")


# ----------------------------------------------------------- peca de leitura
def pagina(d):
    A, B = d["cenarios"]["A"], d["cenarios"]["B"]
    fil = A["fileira_leste"]

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

    matriz = "".join(
        f'<tr><td>cenário {c}</td><td class="num">{v["mrv"]}</td>'
        f'<td class="num">{v["mrv_folga"]}</td>'
        f'<td class="num">{v["mrv_maximo"]}</td></tr>'
        for c, v in d["cenarios"].items())

    choques = "".join(
        f'<li><span class="mono">{c["a"]}</span> e <span class="mono">{c["b"]}</span>'
        f' disputam <span class="mono">{vg(c["area"], 1)} m²</span> do mesmo chão.</li>'
        for c in B["choques"])

    ordem = ["norte", "oeste", "sul", "recorte_h", "recorte_v",
             MM.FACE_LESTE_RECUADA]
    artigo = {"norte": "8 na parede norte", "oeste": "na oeste", "sul": "na sul",
              "recorte_h": "na face norte do recorte",
              "recorte_v": "na face leste do recorte",
              MM.FACE_LESTE_RECUADA: "na fileira recuada da fachada leste"}
    partes = [f"{A['por_face'][f]} {artigo[f]}" for f in ordem
              if A["por_face"].get(f) and f != "norte"]
    partes.insert(0, f"{A['por_face']['norte']} na parede norte")
    det_a = ", ".join(partes[:-1]) + " e " + partes[-1]

    passagem = A["corredor_maximo"] - 2 * MM.MESARIO_ASSENTO
    sub = {
        "estilo": D.estilo(),
        "margem": f"+{A['mrv_folga'] - MM.URNAS}",
        "mrv_folga": str(A["mrv_folga"]), "mrv_maximo": str(A["mrv_maximo"]),
        "fileira_mrv": str(2 * fil["pares"]), "fileira_pares": str(fil["pares"]),
        "fileira_livre": vg(fil["livre"], 1),
        "corr_max": vg(A["corredor_maximo"], 2), "passagem_max": vg(passagem, 2),
        "frente": vg(A["frente"], 1),
        "area_faixa": milhar(d["area_faixa_leste"]),
        "area_envelopes": milhar(d["area_envelopes"]),
        "div_comp": vg(d["plano_b"]["comprimento"], 1),
        "div_acrescimo": str(d["plano_b"]["acrescimo"]),
        "plano_b": str(d["plano_b"]["mrv"]),
        "plano_b_leste": str(d["plano_b"]["leste"]),
        "plano_b_div": str(d["plano_b"]["com_divisoria"]),
        "faltam_sem_faixa": str(MM.URNAS - d["plano_b"]["mrv"]),
        "det_a": det_a, "choques": choques,
        "tabela_faces": "".join(linhas), "matriz": matriz,
    }
    for nome, arq in (("svg_modulo", "mesas_modulo.svg"),
                      ("svg_leste", "mesas_leste.svg"),
                      ("svg_reguas", "mesas_reguas_A.svg"),
                      ("svg_a", "mesas_cenario_A.svg"),
                      ("svg_b", "mesas_cenario_B.svg")):
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
