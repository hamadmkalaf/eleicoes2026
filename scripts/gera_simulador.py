"""Gera saidas/simulador_fluxo.html a partir do template e dos dados.

Embute no HTML: a base da prancheta (data/prancheta_hall2.json), o mapeamento
MRV -> secao (data/mrv_secoes.json), os arranjos de mesa salvos na prancheta
(branch cenarios-hall2), o motor (simulador/modelo.js) e a interface
(simulador/app.js). O artefato publicado nao pode buscar arquivos externos,
entao tudo vai inline.
"""

import json
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
SIM = BASE / "simulador"
DATA = BASE / "data"
SAIDAS = BASE / "saidas"
BRANCH_CENARIOS = "cenarios-hall2"


def arranjos_salvos():
    """Le os arranjos de mesa salvos do branch de dados (cenarios/*.json).

    Mesma fonte e mesma leitura que scripts/gera_editor.py faz para a
    prancheta, para as duas paginas mostrarem a mesma lista. Nao e leitura
    ao vivo: a sandbox do artefato publicado bloqueia rede para fora do
    claude.ai, entao a lista e embutida aqui, na hora de gerar. Cenario novo
    so aparece para todo mundo depois de gravar com salva_cenario.py e
    republicar; quem abre a pagina pode carregar um arranjo na hora pelo
    botao "Carregar arranjo", sem depender disso. Ver cenarios/README.md no
    branch cenarios-hall2.
    """
    ref = "origin/" + BRANCH_CENARIOS
    try:
        subprocess.run(["git", "fetch", "-q", "origin", BRANCH_CENARIOS],
                       cwd=BASE, check=True, timeout=20)
    except Exception as e:
        print("aviso: nao consegui atualizar", ref, "-", e, file=sys.stderr)
    try:
        listagem = subprocess.run(
            ["git", "ls-tree", "-r", "--name-only", ref, "--", "cenarios/"],
            cwd=BASE, check=True, capture_output=True, text=True).stdout
    except subprocess.CalledProcessError:
        print("aviso:", ref, "nao existe; simulador sai so com as plantas A e B",
              file=sys.stderr)
        return []

    salvos = []
    for caminho in listagem.splitlines():
        if not caminho.endswith(".json"):
            continue
        conteudo = subprocess.run(["git", "show", ref + ":" + caminho],
                                  cwd=BASE, check=True,
                                  capture_output=True, text=True).stdout
        try:
            cen = json.loads(conteudo)
        except json.JSONDecodeError as e:
            print("aviso: ignorando", caminho, "- json invalido:", e, file=sys.stderr)
            continue
        if cen.get("base") not in ("A", "B") or not (
                isinstance(cen.get("alteracoes"), list) or isinstance(cen.get("mrvs"), list)):
            print("aviso: ignorando", caminho, "- nao e um arranjo", file=sys.stderr)
            continue
        cen["id"] = caminho[len("cenarios/"):-len(".json")]
        # `medidas` so serve a prancheta; nao carrega peso morto para o simulador
        cen.pop("medidas", None)
        salvos.append(cen)
    salvos.sort(key=lambda c: c.get("criadoEm", ""), reverse=True)
    return salvos


def main():
    template = (SIM / "template.html").read_text(encoding="utf-8")
    modelo = (SIM / "modelo.js").read_text(encoding="utf-8")
    app = (SIM / "app.js").read_text(encoding="utf-8")
    base = json.loads((DATA / "prancheta_hall2.json").read_text(encoding="utf-8"))
    mrvs = json.loads((DATA / "mrv_secoes.json").read_text(encoding="utf-8"))
    arranjos = arranjos_salvos()

    def js(obj):
        # </script> dentro de string quebraria o HTML; nao ocorre nos dados, mas por seguranca
        return json.dumps(obj, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")

    html = (template
            .replace("/*__BASE__*/", "const BASE = " + js(base) + ";")
            .replace("/*__MRVS__*/", "const MRVS = " + js(mrvs) + ";")
            .replace("/*__ARRANJOS__*/", "const ARRANJOS = " + js(arranjos) + ";")
            .replace("/*__MODELO_JS__*/", modelo)
            .replace("/*__APP_JS__*/", app))
    SAIDAS.mkdir(exist_ok=True)
    out = SAIDAS / "simulador_fluxo.html"
    if "/*__" in html:
        raise SystemExit("placeholder nao substituido no template")
    out.write_text(html, encoding="utf-8")
    print(f"gravado {out.relative_to(BASE)} ({out.stat().st_size // 1024} KB)"
          f"; {len(arranjos)} arranjo(s) da prancheta embutido(s)")


if __name__ == "__main__":
    main()
