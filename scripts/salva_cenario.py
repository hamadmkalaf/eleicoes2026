"""Grava um cenario recebido (colado no chat) no branch cenarios-hall2.

Quem desenha na prancheta clica em "Copiar cenario" e manda o JSON por
mensagem; este script grava esse JSON como um arquivo no branch de dados,
sem tocar no checkout local (usa um worktree temporario). Depois de gravar,
rode scripts/gera_editor.py e republique a prancheta para o cenario entrar
na lista de todos.

Uso:
  python3 scripts/salva_cenario.py cenario.json
  echo '{"nome": "...", ...}' | python3 scripts/salva_cenario.py -
"""
import json
import os
import re
import subprocess
import sys
import tempfile
import unicodedata
from datetime import datetime, timezone

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRANCH = "cenarios-hall2"


def slugifica(s):
    s = unicodedata.normalize("NFD", s or "").encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-").lower()
    return s[:40] or "cenario"


def valida(cen):
    if not isinstance(cen, dict):
        raise SystemExit("json invalido: o cenario precisa ser um objeto")
    if cen.get("base") not in ("A", "B"):
        raise SystemExit("campo 'base' precisa ser 'A' ou 'B'")
    if not isinstance(cen.get("alteracoes"), list) and not isinstance(cen.get("mrvs"), list):
        raise SystemExit("faltam 'alteracoes' (ou 'mrvs', formato antigo)")


def grava(cen):
    valida(cen)
    cen = dict(cen)
    cen.setdefault("criadoEm", datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z"))
    nome = cen.get("nome") or "sem nome"
    carimbo = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    arquivo = "cenarios/" + slugifica(nome) + "-" + carimbo + ".json"

    subprocess.run(["git", "fetch", "-q", "origin", BRANCH], cwd=RAIZ, check=True)
    with tempfile.TemporaryDirectory() as wt:
        subprocess.run(["git", "worktree", "add", "-q", "--detach", wt, "origin/" + BRANCH],
                        cwd=RAIZ, check=True)
        try:
            destino = os.path.join(wt, arquivo)
            with open(destino, "w", encoding="utf-8") as f:
                json.dump(cen, f, ensure_ascii=False)
            subprocess.run(["git", "add", arquivo], cwd=wt, check=True)
            subprocess.run(
                ["git", "commit", "-q", "-m", "Cenario salvo: " + nome],
                cwd=wt, check=True)
            subprocess.run(["git", "push", "-q", "origin", "HEAD:" + BRANCH],
                            cwd=wt, check=True)
        finally:
            subprocess.run(["git", "worktree", "remove", "-f", wt], cwd=RAIZ, check=True)
    print("gravado", arquivo, "no branch", BRANCH)
    return arquivo


def main():
    if len(sys.argv) != 2:
        raise SystemExit("uso: salva_cenario.py <arquivo.json | ->")
    origem = sys.argv[1]
    texto = sys.stdin.read() if origem == "-" else open(origem, encoding="utf-8").read()
    grava(json.loads(texto))


if __name__ == "__main__":
    main()
