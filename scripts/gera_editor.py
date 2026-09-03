"""Gera saidas/editor.html — a planta manipulavel, em escala.

Exporta a geometria do salao e as 28 MRVs numeradas para um editor que roda no
navegador: arrastar mesa, girar de 90 em 90, e medir distancia entre dois
pontos. Os numeros continuam saindo de `mesas.py`; o editor nao recalcula nada,
so move o que ja foi validado aqui.
"""
import json
import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "scripts"))

import salao as FL                                            # noqa: E402
import mesas as MM                                            # noqa: E402
import planta_base as PB                                      # noqa: E402

SAIDAS = os.path.join(RAIZ, "saidas")
BRANCH_CENARIOS = "cenarios-hall2"


def cenarios_salvos():
    """Le os cenarios salvos do branch de dados (cenarios/*.json).

    A prancheta nao le isso ao vivo -- o artefato publicado nao pode fazer
    fetch para fora do claude.ai. A lista e embutida aqui, na hora de gerar
    a pagina; ver cenarios/README.md no branch cenarios-hall2.
    """
    ref = "origin/" + BRANCH_CENARIOS
    try:
        subprocess.run(["git", "fetch", "-q", "origin", BRANCH_CENARIOS],
                        cwd=RAIZ, check=True, timeout=20)
    except Exception as e:
        print("aviso: nao consegui atualizar", ref, "-", e, file=sys.stderr)
    try:
        listagem = subprocess.run(
            ["git", "ls-tree", "-r", "--name-only", ref, "--", "cenarios/"],
            cwd=RAIZ, check=True, capture_output=True, text=True).stdout
    except subprocess.CalledProcessError:
        return []

    salvos = []
    for caminho in listagem.splitlines():
        if not caminho.endswith(".json"):
            continue
        conteudo = subprocess.run(
            ["git", "show", ref + ":" + caminho],
            cwd=RAIZ, check=True, capture_output=True, text=True).stdout
        try:
            cen = json.loads(conteudo)
        except json.JSONDecodeError as e:
            print("aviso: ignorando", caminho, "- json invalido:", e, file=sys.stderr)
            continue
        cen["id"] = caminho[len("cenarios/"):-len(".json")]
        salvos.append(cen)
    salvos.sort(key=lambda c: c.get("criadoEm", ""), reverse=True)
    return salvos


def _rot(dx, dy):
    """Angulo em graus, no sentido anti-horario a partir do eixo x."""
    return {(1, 0): 0, (0, 1): 90, (-1, 0): 180, (0, -1): 270}[(round(dx), round(dy))]


def modulo_exportado(m):
    """A MRV como o editor precisa: ancora na parede, direcao e lado.

    `lado` vale +1 quando os mesarios ficam a 90 graus no sentido anti-horario
    da direcao em que o modulo entra no salao, e -1 no outro. Sai medido do
    proprio modelo, e nao deduzido: o referencial local de `ponto()` troca de
    mao conforme a face, e deduzir daria errado em metade delas.
    """
    f = FL.FACES[m["face"]]
    if f["eixo"] == "h":
        ancora = (m["s"], f["fixo"])
        direcao = (0, f["dentro"])
        desloc = (1 if m["lado"] == "a" else -1, 0)
    else:
        ancora = (f["fixo"], m["s"])
        direcao = (f["dentro"], 0)
        desloc = (0, 1 if m["lado"] == "a" else -1)
    # rot90 anti-horario de (x, y) e (-y, x)
    ccw = (-direcao[1], direcao[0])
    lado = 1 if (round(ccw[0]), round(ccw[1])) == desloc else -1
    return dict(n=m["n"], x=round(ancora[0], 3), y=round(ancora[1], 3),
                rot=_rot(*direcao), lado=lado, origem=m["face"],
                corredor=round(m["corredor"], 2))


def dados(cenario="A"):
    r = MM.roda(cenario, "prudente", MM.CORREDOR_MAX, ordem=MM.ORDEM,
                ajustes=MM.AJUSTE_28)
    assert not r["erros"], r["erros"]
    assert r["mrv"] == MM.URNAS, r["mrv"]

    portas = []
    for p in PB.numera():
        face = "recorte_v" if p["parede"] == "recorte" else p["parede"]
        a = PB.ponto(p["parede"], p["a"])
        b = PB.ponto(p["parede"], p["b"])
        portas.append(dict(id=p["num"], rds=p["codigo"], face=face,
                           estado=p["estado"], x1=a[0], y1=a[1], x2=b[0], y2=b[1],
                           larg=round(p["larg"], 2)))

    zonas = [dict(rect=[round(v, 3) for v in rect], rotulo=motivo)
             for rect, motivo in r["reservas"]]
    vaos = [dict(rect=[round(v, 3) for v in rect], rotulo=motivo)
            for rect, motivo in MM.vaos_proibidos()]

    return dict(
        salao=dict(largura=FL.HALL_W, altura=FL.HALL_H,
                   recorte=list(FL.RECORTE), contorno=FL.CONTORNO),
        modulo=dict(prof=MM.PROF, larg=MM.LARG, urna=MM.URNA_D,
                    mesa=list(MM.MESA_IDENT), eleitor=MM.FOLGA_ELEITOR,
                    passagem=MM.PASSAGEM, assento=MM.MESARIO_ASSENTO,
                    corredor=[MM.CORREDOR_MIN, MM.CORREDOR_MAX],
                    entre_pares=[MM.ENTRE_PARES_MIN, MM.ENTRE_PARES_MAX]),
        portas=portas, zonas=zonas, vaos=vaos,
        mrvs=[modulo_exportado(m) for m in sorted(r["modulos"], key=lambda m: m["n"])])


def main():
    pacote = {cen: dados(cen) for cen in ("A", "B")}
    # o salao, o modulo e as portas sao os mesmos nos dois cenarios
    comum = {k: pacote["A"][k] for k in ("salao", "modulo", "portas")}
    saida = dict(**comum,
                 cenarios={cen: {k: pacote[cen][k] for k in ("zonas", "vaos", "mrvs")}
                           for cen in ("A", "B")},
                 cenariosSalvos=cenarios_salvos())

    cam = os.path.join(SAIDAS, "editor_dados.json")
    open(cam, "w", encoding="utf-8").write(json.dumps(saida, ensure_ascii=False))
    print("gravado", cam, os.path.getsize(cam), "bytes")

    modelo = open(os.path.join(RAIZ, "scripts", "editor_template.html"),
                  encoding="utf-8").read()
    html = modelo.replace("@@dados@@", json.dumps(saida, ensure_ascii=False))
    if "@@" in html:
        raise SystemExit("placeholder nao substituido: " + html.split("@@")[1])
    cam = os.path.join(SAIDAS, "editor.html")
    open(cam, "w", encoding="utf-8").write(html)
    print("gravado", cam, os.path.getsize(cam), "bytes")


if __name__ == "__main__":
    main()
