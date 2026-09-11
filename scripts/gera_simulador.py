"""Gera saidas/simulador_fluxo.html a partir do template e dos dados.

Embute no HTML: a base da prancheta, o mapeamento MRV -> secao
(data/mrv_secoes.json), as decisoes do Posto (scripts/decisoes.py: esperado e
classe por mesa, portas, entradas do Ring 3), os arranjos de mesa salvos na
prancheta (scripts/cenarios.py), o motor (simulador/modelo.js) e a interface
(simulador/app.js). O artefato publicado nao pode buscar arquivos externos,
entao tudo vai inline.

A base da prancheta sai de saidas/editor_dados.json quando ele existe -- o
proprio arquivo que gera_editor.py acabou de escrever --, e so cai em
data/prancheta_hall2.json quando o simulador e gerado sozinho. Assim as duas
paginas nao podem discordar da geometria: ou leem o mesmo arquivo, ou o
descasamento aparece no aviso.
"""

import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
SIM = BASE / "simulador"
DATA = BASE / "data"
SAIDAS = BASE / "saidas"
sys.path.insert(0, str(BASE / "scripts"))

import cenarios as CN                                          # noqa: E402
import decisoes as DC                                          # noqa: E402


def base_prancheta():
    """A geometria do salao, das portas e das 28 mesas, com a fonte no nome."""
    gerado = SAIDAS / "editor_dados.json"
    congelado = DATA / "prancheta_hall2.json"
    if gerado.exists():
        d = json.loads(gerado.read_text(encoding="utf-8"))
        d.pop("cenariosSalvos", None)          # a lista entra por /*__ARRANJOS__*/
        if congelado.exists():
            velho = json.loads(congelado.read_text(encoding="utf-8"))
            if velho != d:
                print("aviso: data/prancheta_hall2.json esta atrasado em relacao a",
                      "saidas/editor_dados.json; rode gera_editor.py e atualize a copia",
                      file=sys.stderr)
        return d, gerado
    return json.loads(congelado.read_text(encoding="utf-8")), congelado


def main():
    template = (SIM / "template.html").read_text(encoding="utf-8")
    modelo = (SIM / "modelo.js").read_text(encoding="utf-8")
    app = (SIM / "app.js").read_text(encoding="utf-8")
    portas = (SIM / "portas.js").read_text(encoding="utf-8")
    base, fonte_base = base_prancheta()
    mrvs = json.loads((DATA / "mrv_secoes.json").read_text(encoding="utf-8"))
    # decisoes do Posto: esperado e classe por mesa, portas, entradas do Ring 3
    decisoes = DC.montar()
    # `medidas` so serve a prancheta; nao carrega peso morto para o simulador
    arranjos = CN.carrega(com_medidas=False)

    def js(obj):
        # </script> dentro de string quebraria o HTML; nao ocorre nos dados, mas por seguranca
        return json.dumps(obj, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")

    html = (template
            .replace("/*__BASE__*/", "const BASE = " + js(base) + ";")
            .replace("/*__DECISOES__*/", "const DECISOES = " + js(decisoes) + ";")
            .replace("/*__MRVS__*/", "const MRVS = " + js(mrvs) + ";")
            .replace("/*__ARRANJOS__*/", "const ARRANJOS = " + js(arranjos) + ";")
            .replace("/*__PORTAS_JS__*/", portas)
            .replace("/*__MODELO_JS__*/", modelo)
            .replace("/*__APP_JS__*/", app))
    SAIDAS.mkdir(exist_ok=True)
    out = SAIDAS / "simulador_fluxo.html"
    if "/*__" in html:
        raise SystemExit("placeholder nao substituido no template")
    out.write_text(html, encoding="utf-8")
    print(f"gravado {out.relative_to(BASE)} ({out.stat().st_size // 1024} KB)"
          f"; base de {fonte_base.relative_to(BASE)}"
          f"; {len(arranjos)} arranjo(s) da prancheta embutido(s)")


if __name__ == "__main__":
    main()
