"""Grava data/decisoes.json a partir de scripts/decisoes.py e imprime o resumo.

Uso: python3 scripts/gera_decisoes.py
Roda antes dos demais geradores: prancheta, simulador, sinalizacao e
planta-base embutem ou leem o que esta aqui.
"""
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "scripts"))

import decisoes as DC                                         # noqa: E402


def main():
    d = DC.montar()
    with open(DC.ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print("gravado", os.path.relpath(DC.ARQUIVO, RAIZ), os.path.getsize(DC.ARQUIVO), "bytes")
    c = d["comparecimento"]
    print(f"comparecimento: base {c['base']} · {c['total']} de {c['aptos']} aptos "
          f"({c['total'] / c['aptos']:.1%}) · {c['rotulo']}")
    print("portas:", ", ".join(f"{k} {v['papel']}" + (f" {v['entrada']}" if "entrada" in v else "")
                               for k, v in sorted(d["portas"].items())))
    print(f"classes: {d['classes']['regra']} -> "
          + ", ".join(f"{k} {n}" for k, n in d["classes"]["contagem"].items()))
    print("\nentrada  porta  cor       balizas  serp  baia  capac  quota   mesas  esperado  alvo")
    for e in d["entradas"]:
        print(f"{e['id']:<8} {e['porta']:<6} {e['cor']:<9} {e['balizas']:>7} {e['serpenteado']:>5} "
              f"{e['baia']:>5} {e['capacidade']:>6} {e['quota']:>6.1%} {len(e['mrvs']):>6} "
              f"{e['esperado']:>9} {e['alvo']:>5}")
        print("         MRV " + ", ".join(str(m) for m in e["mrvs"]))
    print("\nMRV  principal  agregada  origem                    aptos  esperado  classe  entrada")
    for m in d["mesas"]:
        print(f"{m['mrv']:>3}  {m['principal']:>9}  {m['agregada'] or '—':>8}  "
              f"{(m['origem_agregada'] or '—'):<24}  {m['aptos']:>5}  {m['esperado']:>8}  "
              f"{m['classe']:<6}  {m['entrada']}")
    r = d["ring3"]
    print(f"\nRing 3: {r['largura']:.0f} x {r['profundidade']:.0f} m · capacidade {r['capacidade']} · "
          f"{r['separadores']} separadores ({r['metros']} m), {r['em_maos']} em maos, "
          f"{r['a_adquirir']} a adquirir (~EUR {r['custo_eur']}) · evacuacao {r['evacuacao_min']} min")


if __name__ == "__main__":
    main()
