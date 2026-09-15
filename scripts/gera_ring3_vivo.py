"""Gera saidas/ring3_vivo.html: o Ring 3 redesenhado ao vivo para as portas em vigor.

Embute a geometria da prancheta (portas da fachada sul), o bloco de decisoes
(data/decisoes.json, via decisoes.montar()) e simulador/portas.js. A pagina
assina o canal das portas vivas: quando o Simulador muda uma entrada ou uma
saida, o Ring 3 e redesenhado com N serpenteados, um por entrada, e a tabela
de barreira e refeita. O seletor de desenho (norte-sul / leste-oeste, com ou
sem baias, plano vigente) publica a escolha de volta para as outras paginas.

Uso: python3 scripts/gera_ring3_vivo.py
"""
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE / "scripts"))

import decisoes as DC                                         # noqa: E402


def js(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def main():
    template = (BASE / "scripts" / "ring3_vivo_template.html").read_text(encoding="utf-8")
    portas_js = (BASE / "simulador" / "portas.js").read_text(encoding="utf-8")
    base = json.loads((BASE / "data" / "prancheta_hall2.json").read_text(encoding="utf-8"))
    base.pop("cenariosSalvos", None)
    base.pop("cenarios", None)
    dec = DC.montar()
    html = (template
            .replace("/*__BASE__*/", "const BASE = " + js({"portas": base["portas"], "salao": base["salao"]}) + ";")
            .replace("/*__DECISOES__*/", "const DECISOES = " + js(dec) + ";")
            .replace("/*__PORTAS_JS__*/", portas_js))
    destino = BASE / "saidas" / "ring3_vivo.html"
    destino.write_text(html, encoding="utf-8")
    print(f"gravado {destino.relative_to(BASE)} ({len(html) // 1024} KB)")


if __name__ == "__main__":
    main()
