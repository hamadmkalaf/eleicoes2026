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


def confere_ring3_decidido(d):
    """O desenho decidido do Ring 3 (girado_ccb_na_ponta) foi dimensionado por
    ring3.py sobre o comparecimento esperado por entrada (ESPERADO). Esse
    esperado sai da atribuicao de mesas feita aqui; se um dia a atribuicao
    mudar, ring3.py precisa ser rodado de novo. Este teste garante que
    saidas/ring3.json ainda corresponde a atribuicao vigente."""
    dec = d["ring3"].get("decidido")
    if not dec:
        return "ring3.json ausente: desenho decidido nao conferido"
    with open(DC.RING3_JSON, encoding="utf-8") as f:
        r3 = json.load(f)
    premissa = r3.get("premissas", {}).get("comparecimento_esperado")
    atual = {e["id"]: e["esperado"] for e in d["entradas"]}
    if premissa != atual:
        raise SystemExit("saidas/ring3.json foi dimensionado sobre outro esperado por entrada: "
                         f"{premissa} != {atual}; rode scripts/ring3.py de novo")
    tot = sum(dec["por_entrada"].values())
    return ("Ring 3 decidido dimensionado sobre o esperado vigente por entrada ("
            + ", ".join(f"{k} {v}" for k, v in atual.items())
            + "); capacidade por zona "
            + ", ".join(f"{k} {v} ({v / tot:.1%})" for k, v in dec["por_entrada"].items())
            + ": ok")


def main():
    d = DC.montar()
    with open(DC.ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print("gravado", os.path.relpath(DC.ARQUIVO, RAIZ), os.path.getsize(DC.ARQUIVO), "bytes")
    ct = d["cenario_trabalho"]
    print(f"cenario de trabalho: {ct['nome']} ({ct['id']})"
          + (" -- PROVISORIO: Hamad_Final ainda nao foi colado em cenarios/" if ct["provisorio"] else ""))
    print(confere_ring3_decidido(d))
    r3d = d["ring3"].get("decidido")
    if r3d:
        print(f"Ring 3 decidido: {r3d['nome']} · {r3d['capacidade']} pessoas · "
              f"{r3d['separadores']} separadores (registrados {r3d['registrados']})")
    print("numeracao eleitor (n. eleitor <- MRV): "
          + ", ".join(f"{m['eleitor']}<-{m['mrv']}" for m in sorted(d["mesas"], key=lambda m: m["eleitor"])))
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
    print("\nMRV  n.el  parede  principal  agregada  origem                    aptos  esperado  classe  entrada")
    for m in d["mesas"]:
        print(f"{m['mrv']:>3}  {m['eleitor']:>4}  {m['parede']:<6}  {m['principal']:>9}  {m['agregada'] or '—':>8}  "
              f"{(m['origem_agregada'] or '—'):<24}  {m['aptos']:>5}  {m['esperado']:>8}  "
              f"{m['classe']:<6}  {m['entrada']}")
    r = d["ring3"]
    print(f"\nRing 3: {r['largura']:.0f} x {r['profundidade']:.0f} m · capacidade {r['capacidade']} · "
          f"{r['separadores']} separadores ({r['metros']} m), {r['em_maos']} em maos, "
          f"{r['a_adquirir']} a adquirir (~EUR {r['custo_eur']}) · evacuacao {r['evacuacao_min']} min")


if __name__ == "__main__":
    main()
