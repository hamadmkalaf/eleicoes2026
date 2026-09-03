"""Gera saidas/simulador_fluxo.html a partir do template e dos dados.

Embute no HTML: a base da prancheta (data/prancheta_hall2.json), o mapeamento
MRV -> secao (data/mrv_secoes.json), o motor (simulador/modelo.js) e a
interface (simulador/app.js). O artefato publicado nao pode buscar arquivos
externos, entao tudo vai inline.
"""

import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
SIM = BASE / "simulador"
DATA = BASE / "data"
SAIDAS = BASE / "saidas"


def main():
    template = (SIM / "template.html").read_text(encoding="utf-8")
    modelo = (SIM / "modelo.js").read_text(encoding="utf-8")
    app = (SIM / "app.js").read_text(encoding="utf-8")
    base = json.loads((DATA / "prancheta_hall2.json").read_text(encoding="utf-8"))
    mrvs = json.loads((DATA / "mrv_secoes.json").read_text(encoding="utf-8"))

    def js(obj):
        # </script> dentro de string quebraria o HTML; nao ocorre nos dados, mas por seguranca
        return json.dumps(obj, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")

    html = (template
            .replace("/*__BASE__*/", "const BASE = " + js(base) + ";")
            .replace("/*__MRVS__*/", "const MRVS = " + js(mrvs) + ";")
            .replace("/*__MODELO_JS__*/", modelo)
            .replace("/*__APP_JS__*/", app))
    SAIDAS.mkdir(exist_ok=True)
    out = SAIDAS / "simulador_fluxo.html"
    out.write_text(html, encoding="utf-8")
    print(f"gravado {out.relative_to(BASE)} ({out.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
