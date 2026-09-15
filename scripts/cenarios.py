"""Fonte unica dos cenarios salvos na prancheta.

Ate aqui `gera_editor.py` e `gera_simulador.py` tinham cada um a sua copia da
leitura, e as duas liam so o branch de dados `cenarios-hall2`. Deu no que tinha
de dar: dois cenarios foram parar num branch de trabalho, o simulador publicado
ficou com dois arranjos e a prancheta com quatro. Agora as duas paginas leem
daqui, e daqui leem de duas origens:

  1. `cenarios/` no proprio checkout -- a biblioteca versionada junto com o
     codigo, que e o que garante uma lista igual mesmo sem rede;
  2. `cenarios/` no branch de dados `cenarios-hall2` -- onde
     `scripts/salva_cenario.py` grava cenario novo sem tocar em codigo.

As duas origens se juntam pelo `id` (o nome do arquivo). Em colisao vence o
branch de dados, que e o alvo das gravacoes novas. A leitura nunca e ao vivo:
o artefato publicado nao alcanca rede fora do claude.ai, entao a lista e
embutida na hora de gerar a pagina.
"""
import json
import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRANCH_CENARIOS = "cenarios-hall2"
PASTA = "cenarios"


def _valido(cen, rotulo):
    """Um cenario serve se diz de que planta partiu e o que mudou nela."""
    if not isinstance(cen, dict):
        print("aviso: ignorando", rotulo, "- nao e um objeto", file=sys.stderr)
        return False
    if cen.get("base") not in ("A", "B"):
        print("aviso: ignorando", rotulo, "- 'base' nao e A nem B", file=sys.stderr)
        return False
    if not isinstance(cen.get("alteracoes"), list) and not isinstance(cen.get("mrvs"), list):
        print("aviso: ignorando", rotulo, "- sem 'alteracoes' nem 'mrvs'", file=sys.stderr)
        return False
    return True


def _do_checkout():
    """Os arquivos de `cenarios/` que estao no checkout atual."""
    pasta = os.path.join(RAIZ, PASTA)
    if not os.path.isdir(pasta):
        return []
    achados = []
    for nome in sorted(os.listdir(pasta)):
        if not nome.endswith(".json"):
            continue
        caminho = os.path.join(pasta, nome)
        try:
            cen = json.loads(open(caminho, encoding="utf-8").read())
        except json.JSONDecodeError as e:
            print("aviso: ignorando", caminho, "- json invalido:", e, file=sys.stderr)
            continue
        if not _valido(cen, caminho):
            continue
        cen["id"] = nome[:-len(".json")]
        achados.append(cen)
    return achados


def _do_branch():
    """Os arquivos de `cenarios/` no branch de dados, se der para alcancar."""
    ref = "origin/" + BRANCH_CENARIOS
    try:
        subprocess.run(["git", "fetch", "-q", "origin", BRANCH_CENARIOS],
                       cwd=RAIZ, check=True, timeout=20)
    except Exception as e:
        print("aviso: nao consegui atualizar", ref, "-", e, file=sys.stderr)
    try:
        listagem = subprocess.run(
            ["git", "ls-tree", "-r", "--name-only", ref, "--", PASTA + "/"],
            cwd=RAIZ, check=True, capture_output=True, text=True).stdout
    except subprocess.CalledProcessError:
        print("aviso:", ref, "nao existe; vale so a biblioteca do checkout",
              file=sys.stderr)
        return []

    achados = []
    for caminho in listagem.splitlines():
        if not caminho.endswith(".json"):
            continue
        conteudo = subprocess.run(["git", "show", ref + ":" + caminho],
                                  cwd=RAIZ, check=True,
                                  capture_output=True, text=True).stdout
        try:
            cen = json.loads(conteudo)
        except json.JSONDecodeError as e:
            print("aviso: ignorando", caminho, "- json invalido:", e, file=sys.stderr)
            continue
        if not _valido(cen, caminho):
            continue
        cen["id"] = caminho[len(PASTA) + 1:-len(".json")]
        achados.append(cen)
    return achados


def carrega(com_medidas=True, offline=False):
    """A biblioteca inteira, mais recente primeiro.

    `com_medidas=False` derruba as medidas de fita, que so a prancheta usa --
    o simulador nao precisa carregar esse peso. `offline=True` pula o branch
    de dados, para gerar sem rede.
    """
    por_id = {c["id"]: c for c in _do_checkout()}
    if not offline:
        for c in _do_branch():
            por_id[c["id"]] = c
    salvos = sorted(por_id.values(), key=lambda c: c.get("criadoEm", ""), reverse=True)
    if not com_medidas:
        for c in salvos:
            c.pop("medidas", None)
    return salvos


if __name__ == "__main__":
    for c in carrega():
        n = len(c.get("alteracoes") or c.get("mrvs") or [])
        print(f'{c["id"]:<40} {c.get("base")}  {n:>2} mesa(s)  {c.get("nome")}')
