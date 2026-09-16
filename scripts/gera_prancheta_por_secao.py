"""A prancheta pelas secoes: as 28 mesas rotuladas pela secao que vota em cada.

A Prancheta do Hall 2 numera as mesas pela numeracao eleitor (1 a 28, sentido
horario) e leva o MRV do DJE ao lado. Esta peca inverte a ordem: o rotulo e a
**secao eleitoral**, que e o numero que o eleitor ja tem na mao (titulo de
eleitor e e-Titulo), e a mesa e o MRV ficam na ficha e no indice.

Le, sem recalcular nada:
  data/prancheta_hall2.json   geometria do salao, do modulo e das portas, mais
                              as posicoes do cenario-base
  cenarios/<id>.json          as mesas que o cenario de trabalho move
  data/decisoes.json          secoes, aptos, esperado, classe, parede, entrada
                              e numeracao eleitor de cada mesa
  saidas/dados.json           a localidade de origem de cada uma das 51 secoes

Grava saidas/prancheta_por_secao.html, uma pagina so, pronta para publicar.

    python3 scripts/gera_prancheta_por_secao.py [cenario]
"""
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELO = os.path.join(RAIZ, "scripts", "prancheta_por_secao_template.html")
SAIDA = os.path.join(RAIZ, "saidas", "prancheta_por_secao.html")
MARCA = "/*__DADOS__*/null"


def carrega(*caminho):
    with open(os.path.join(RAIZ, *caminho), encoding="utf-8") as f:
        return json.load(f)


def posicoes(planta, cenario):
    """{mrv: {x, y, rot, lado}} do cenario, sobre as posicoes do cenario-base.

    Um cenario so guarda as mesas que saiu do lugar; as demais ficam onde a
    planta oficial as pos.
    """
    pos = {m["n"]: {k: m[k] for k in ("x", "y", "rot", "lado")}
           for m in planta["cenarios"][cenario["base"]]["mrvs"]}
    for a in cenario["alteracoes"]:
        if a["n"] not in pos:
            raise SystemExit(f"o cenário move a mesa {a['n']}, que não está no cenário-base")
        pos[a["n"]].update({k: a[k] for k in ("x", "y", "rot", "lado")})
    return pos


def monta(planta, decisoes, dados, cenario):
    pos = posicoes(planta, cenario)
    origem = {s["Secao"]: s["Residencia_predominante"] for s in dados["secoes"]}
    aptos = {s["Secao"]: s["Eleitores"] for s in dados["secoes"]}

    mesas, secoes = [], []
    for m in sorted(decisoes["mesas"], key=lambda m: m["mrv"]):
        p = pos[m["mrv"]]
        mesas.append({
            "mrv": m["mrv"], "eleitor": m["eleitor"],
            "principal": m["principal"], "agregada": m["agregada"],
            "aptos": m["aptos"], "esperado": m["esperado"], "classe": m["classe"],
            "parede": m["parede"], "entrada": m["entrada"], "porta": m["porta"],
            "x": p["x"], "y": p["y"], "rot": int(p["rot"]) % 360, "lado": p["lado"],
        })
        for secao, papel in ((m["principal"], "principal"), (m["agregada"], "agregada")):
            if secao is None:
                continue
            if secao not in origem:
                raise SystemExit(f"a seção {secao} não está em saidas/dados.json")
            secoes.append({"secao": secao, "papel": papel, "mrv": m["mrv"],
                           "aptos": aptos[secao], "origem": origem[secao].title()})
    secoes.sort(key=lambda s: s["secao"])

    if len(secoes) != len(dados["secoes"]):
        raise SystemExit(f"{len(secoes)} seções nas mesas × {len(dados['secoes'])} no eleitorado")
    if len({s["secao"] for s in secoes}) != len(secoes):
        raise SystemExit("há seção repetida em mais de uma mesa")

    return {
        "cenario": {"id": cenario.get("id", decisoes["cenario_trabalho"]["id"]),
                    "nome": cenario["nome"]},
        "salao": planta["salao"], "modulo": planta["modulo"], "portas": planta["portas"],
        "entradas": [{"id": e["id"], "porta": e["porta"], "parede": e["parede"],
                      "mesas": len(e["mrvs"]), "esperado": e["esperado"],
                      "quota": e["quota"], "metros": e["metros_de_parede"],
                      "por_metro": e["por_metro"]}
                     for e in decisoes["entradas"]],
        "saidas": decisoes["saidas"],
        "sinalizacao": decisoes["sinalizacao_portas"],
        "zonas": decisoes["zonas_protegidas"],
        "serpenteados": decisoes["serpenteados"],
        "classes": {"n_alta": decisoes["classes"]["n_alta"],
                    "limiar_media": decisoes["classes"]["limiar_media"]},
        "comparecimento": {k: decisoes["comparecimento"][k] for k in ("base", "rotulo", "total", "aptos")},
        "mesas": mesas, "secoes": secoes,
    }


def main(argv):
    decisoes = carrega("data", "decisoes.json")
    id_cenario = argv[1] if len(argv) > 1 else decisoes["cenario_trabalho"]["id"]
    cenario = carrega("cenarios", id_cenario + ".json")
    cenario.setdefault("id", id_cenario)

    d = monta(carrega("data", "prancheta_hall2.json"), decisoes,
              carrega("saidas", "dados.json"), cenario)

    with open(MODELO, encoding="utf-8") as f:
        pagina = f.read()
    if MARCA not in pagina:
        raise SystemExit(f"o modelo perdeu a marca {MARCA}")
    # `</` dentro do JSON fecharia o <script> que carrega os dados
    bloco = json.dumps(d, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    with open(SAIDA, "w", encoding="utf-8") as f:
        f.write(pagina.replace(MARCA, bloco))

    print(f"gravado saidas/prancheta_por_secao.html · cenário {d['cenario']['nome']} · "
          f"{len(d['mesas'])} mesas · {len(d['secoes'])} seções · "
          f"{d['comparecimento']['aptos']} aptos")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
