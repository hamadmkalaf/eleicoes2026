"""Confere todos os consumidores contra data/zonas.json, a fonte unica.

A vinculacao entre o plano de sinalizacao e o desenho dos separadores nao e uma
promessa escrita num documento: e este script. Mudou a cor de uma porta em
``data/zonas.json``? Rode isto. O que nao tiver acompanhado sai nomeado, e o
script sai com **codigo 1**.

    python3 scripts/confere_zonas.py

Confere, para cada zona, que zona = porta = parede = cor bate em:

  * ``scripts/arranjo_paredes.py``   (CORES, ENTRADA, PORTA)
  * ``scripts/separadores_fila.py``  (CORES_ZONA, ESTOQUE_FITA, CORES_FITA)
  * ``data/decisoes.json``           (portas[].cor, entradas[].hex/cor/porta/parede)
  * ``data/prancheta_hall2.json``    (o espelho legado do bloco de decisoes)
  * ``data/grupos_mesas.json``       (entrada/porta/parede de cada grupo)
  * ``saidas/separadores_*.svg``     (os hex efetivamente desenhados)
  * ``saidas/sinalizacao_v2.json``   (o plano de sinalizacao, quando presente)

E confere que **nenhuma paleta superada** sobreviveu em lugar nenhum.
"""
import glob
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import zonas  # noqa: E402

# Paletas que ja foram cor de zona neste projeto e nao podem mais aparecer.
# Se uma delas voltar a um arquivo, e sinal de que alguem regenerou a partir de
# um gerador antigo -- exatamente o modo de falha que esta conferencia existe
# para pegar.
SUPERADAS = {
    "#2A78D6": "paleta de 15/09 (azul antigo)",
    "#E08A00": "paleta de 15/09 (âmbar)",
    "#C2185B": "paleta de 15/09 (magenta)",
    "#1F5FA8": "paleta do sinalizacao_v2 (azul antigo)",
    "#B8760A": "paleta do sinalizacao_v2 (âmbar)",
    "#8B3A8E": "paleta do sinalizacao_v2 (magenta)",
}
# Arquivos em que uma cor superada e historia, nao erro.
ISENTOS = ("plano_separadores_fila.md", "contexto_separadores_fila_hall2.md",
           "TRANSFERENCIA_SEPARADORES_FILA.md", "confere_zonas.py",
           "CONFERENCIA_PRANCHETA_2026-09-15.md", "gera_pagina.py",
           "dublin_agregacoes.html", "prancheta_por_secao.html",
           "prancheta_por_secao_template.html")


def ok(caminho):
    return os.path.exists(os.path.join(RAIZ, caminho))


def carrega(caminho):
    with open(os.path.join(RAIZ, caminho), encoding="utf-8") as f:
        return json.load(f)


def confere_modulos():
    faltas = []
    import arranjo_paredes as ap
    faltas += zonas.divergencias({i: h for i, (_, h) in ap.CORES.items()},
                                 "arranjo_paredes.CORES")
    for i in zonas.IDS:
        if ap.PORTA.get(i) != zonas.PORTA[i]:
            faltas.append(f"arranjo_paredes.PORTA: zona {i} → {ap.PORTA.get(i)}, "
                          f"a fonte diz {zonas.PORTA[i]}")
        if ap.ENTRADA.get(zonas.PAREDE[i]) != i:
            faltas.append(f"arranjo_paredes.ENTRADA: parede {zonas.PAREDE[i]} → "
                          f"{ap.ENTRADA.get(zonas.PAREDE[i])}, a fonte diz {i}")

    import separadores_fila as sf
    faltas += zonas.divergencias(sf.CORES_ZONA, "separadores_fila.CORES_ZONA")
    for i in zonas.IDS:
        if sf.ESTOQUE_FITA.get(i) != zonas.ESTOQUE[i]:
            faltas.append(f"separadores_fila.ESTOQUE_FITA: zona {i} tem "
                          f"{sf.ESTOQUE_FITA.get(i)}, a fonte diz {zonas.ESTOQUE[i]}")
        if zonas.normaliza(sf.CORES_FITA[i]["hex"]) != zonas.normaliza(zonas.HEX[i]):
            faltas.append(f"separadores_fila.CORES_FITA: zona {i} tem "
                          f"{sf.CORES_FITA[i]['hex']}, a fonte diz {zonas.HEX[i]}")
    for chave, aux in zonas.AUXILIARES.items():
        interno = {"espera": "espera", "pref": "pref", "saida": "neutro"}[chave]
        if zonas.normaliza(sf.CORES_FITA[interno]["hex"]) != zonas.normaliza(aux["hex"]):
            faltas.append(f"separadores_fila.CORES_FITA['{interno}'] tem "
                          f"{sf.CORES_FITA[interno]['hex']}, a fonte diz {aux['hex']}")
    return faltas


def confere_decisoes(caminho, bloco=None):
    """decisoes.json, e o espelho dele dentro do prancheta_hall2.json."""
    faltas = []
    d = carrega(caminho)
    if bloco:
        d = d[bloco]
    rot = caminho + (f"[{bloco}]" if bloco else "")

    portas = d.get("portas", {})
    for i in zonas.IDS:
        p = zonas.PORTA[i]
        if p not in portas:
            faltas.append(f"{rot}: porta {p} (zona {i}) ausente")
            continue
        if zonas.normaliza(portas[p].get("cor")) != zonas.normaliza(zonas.HEX[i]):
            faltas.append(f"{rot}: porta {p} tem cor {portas[p].get('cor')}, "
                          f"a fonte diz {zonas.HEX[i]}")
        if portas[p].get("entrada") != i:
            faltas.append(f"{rot}: porta {p} → entrada {portas[p].get('entrada')}, "
                          f"a fonte diz {i}")

    ent = {e["id"]: e for e in d.get("entradas", [])}
    faltas += zonas.divergencias({i: e.get("hex") for i, e in ent.items()},
                                 f"{rot} entradas[].hex")
    for i in zonas.IDS:
        e = ent.get(i)
        if not e:
            continue
        if e.get("porta") != zonas.PORTA[i]:
            faltas.append(f"{rot}: entrada {i} → porta {e.get('porta')}, "
                          f"a fonte diz {zonas.PORTA[i]}")
        if e.get("parede") != zonas.PAREDE[i]:
            faltas.append(f"{rot}: entrada {i} → parede {e.get('parede')}, "
                          f"a fonte diz {zonas.PAREDE[i]}")
        if e.get("cor") != zonas.NOME_COR[i]:
            faltas.append(f"{rot}: entrada {i} → cor '{e.get('cor')}', "
                          f"a fonte diz '{zonas.NOME_COR[i]}'")
    return faltas


def confere_grupos():
    faltas = []
    for g in carrega("data/grupos_mesas.json")["grupos"]:
        i = g["entrada"]
        if i not in zonas.IDS:
            faltas.append(f"grupos_mesas: grupo {g['id']} tem entrada {i}, "
                          f"que não existe na fonte")
            continue
        if g["parede"] != zonas.PAREDE[i]:
            faltas.append(f"grupos_mesas: grupo {g['id']} (zona {i}) diz parede "
                          f"{g['parede']}, a fonte diz {zonas.PAREDE[i]}")
        if g["porta"] != zonas.PORTA[i]:
            faltas.append(f"grupos_mesas: grupo {g['id']} (zona {i}) diz porta "
                          f"{g['porta']}, a fonte diz {zonas.PORTA[i]}")
        if not g["id"].startswith(i):
            faltas.append(f"grupos_mesas: grupo {g['id']} não começa pela letra "
                          f"da sua zona ({i})")
    return faltas


def confere_sinalizacao():
    """O plano de sinalizacao, quando estiver no repositorio."""
    alvo = "saidas/sinalizacao_v2.json"
    if not ok(alvo):
        return [], False

    faltas = []
    d = carrega(alvo)
    faltas += zonas.divergencias(d.get("cores", {}), f"{alvo} cores")
    for p in d.get("portas", []):
        i = p.get("letra")
        if i not in zonas.IDS:
            faltas.append(f"{alvo}: porta com letra {i}, que não existe na fonte")
            continue
        if p.get("parede") != zonas.PAREDE[i]:
            faltas.append(f"{alvo}: zona {i} diz parede {p.get('parede')}, "
                          f"a fonte diz {zonas.PAREDE[i]}")
        if p.get("porta") != zonas.PORTA[i]:
            faltas.append(f"{alvo}: zona {i} diz porta {p.get('porta')}, "
                          f"a fonte diz {zonas.PORTA[i]}")
        if zonas.normaliza(p.get("cor")) != zonas.normaliza(zonas.HEX[i]):
            faltas.append(f"{alvo}: zona {i} tem cor {p.get('cor')}, "
                          f"a fonte diz {zonas.HEX[i]}")
    return faltas, True


def confere_desenhos():
    faltas = []
    for cam in sorted(glob.glob(os.path.join(SAIDAS_DIR, "separadores_*.svg"))):
        txt = open(cam, encoding="utf-8").read().upper()
        nome = os.path.relpath(cam, RAIZ)
        if "detalhe" in nome:
            continue        # o detalhe e o corte de UMA parede: so traz uma cor
        for i in zonas.IDS:
            if zonas.normaliza(zonas.HEX[i]) not in txt:
                faltas.append(f"{nome}: a cor da zona {i} "
                              f"({zonas.normaliza(zonas.HEX[i])}) não aparece")
    return faltas


def confere_superadas():
    faltas = []
    for raiz, dirs, arqs in os.walk(RAIZ):
        dirs[:] = [d for d in dirs if d not in (".git", "__pycache__")]
        for a in arqs:
            if not a.endswith((".py", ".json", ".md", ".svg")) or a in ISENTOS:
                continue
            cam = os.path.join(raiz, a)
            try:
                txt = open(cam, encoding="utf-8").read().upper()
            except (UnicodeDecodeError, OSError):
                continue
            for h, porque in SUPERADAS.items():
                if h in txt:
                    faltas.append(f"{os.path.relpath(cam, RAIZ)}: sobreviveu "
                                  f"{h} — {porque}")
    return faltas


SAIDAS_DIR = os.path.join(RAIZ, "saidas")

# O gerador do plano de sinalizacao vive no branch
# claude/voter-route-signage-update-bjgbhp e depende de entradas que nao estao
# aqui, entao nao roda neste repositorio. O que falta nele e literalmente isto.
PATCH_SINALIZACAO = """
  AVISO: o plano de sinalização ainda não está vinculado neste repositório.
  scripts/sinalizacao_v2.py (branch claude/voter-route-signage-update-bjgbhp)
  declara a sua própria paleta. Para vinculá-lo, troque as quatro linhas:

      CORES        = {"A": "#1f5fa8", ...}
      CORES_ESCURO = {"A": "#79b0ea", ...}
      NOME_COR     = {"A": "azul", ...}
      PAREDE       = {"A": "oeste", ...}

  por:

      import sys, os
      sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
      import zonas
      CORES    = dict(zonas.HEX)
      NOME_COR = dict(zonas.NOME_COR)
      PAREDE   = dict(zonas.PAREDE)
      CORES_ESCURO = {i: zonas.clareia(zonas.HEX[i]) for i in zonas.IDS}

  e leve junto data/zonas.json e scripts/zonas.py. Depois de regenerar,
  saidas/sinalizacao_v2.json passa a ser conferido aqui automaticamente."""


def sincroniza_espelho():
    """Reescreve o espelho de decisoes dentro do prancheta_hall2.json.

    O prancheta_hall2.json e fonte medida, mas carrega uma copia do bloco de
    decisoes -- e e essa copia que sai do lugar quando a cor muda. Aqui ela e
    reescrita a partir da fonte, em vez de editada a mao.
    """
    cam = os.path.join(RAIZ, "data", "prancheta_hall2.json")
    with open(cam, encoding="utf-8") as f:
        d = json.load(f)
    dec = d["decisoes"]
    mexeu = []
    for i in zonas.IDS:
        p = zonas.PORTA[i]
        if p in dec.get("portas", {}):
            if dec["portas"][p].get("cor") != zonas.HEX[i]:
                dec["portas"][p]["cor"] = zonas.HEX[i]
                mexeu.append(f"portas.{p}.cor")
            dec["portas"][p]["entrada"] = i
    for e in dec.get("entradas", []):
        i = e.get("id")
        if i not in zonas.IDS:
            continue
        for chave, valor in (("hex", zonas.HEX[i]), ("cor", zonas.NOME_COR[i]),
                             ("porta", zonas.PORTA[i]), ("parede", zonas.PAREDE[i])):
            if e.get(chave) != valor:
                e[chave] = valor
                mexeu.append(f"entradas[{i}].{chave}")
    if mexeu:
        with open(cam, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=1)
    return mexeu


def main():
    if "--sincroniza" in sys.argv:
        mexeu = sincroniza_espelho()
        if mexeu:
            print("data/prancheta_hall2.json sincronizado com a fonte:")
            for m in mexeu:
                print("   ", m)
        else:
            print("data/prancheta_hall2.json já estava em dia")
        print("Agora regenere o que é gerado:")
        print("    python3 scripts/arranjo_paredes.py --grava")
        print("    python3 scripts/separadores_fila.py --grava\n")

    return _confere()


def _confere():
    print("Fonte única: data/zonas.json")
    for i in zonas.IDS:
        print(f"    zona {i} · porta {zonas.PORTA[i]} · parede {zonas.PAREDE[i]:6s} · "
              f"{zonas.NOME_COR[i]:8s} {zonas.HEX[i]}")
    for k, a in zonas.AUXILIARES.items():
        print(f"    {k:8s} · {a['cor']:24s} {a['hex']}")
    print()

    faltas = []
    checados = []

    faltas += confere_modulos()
    checados += ["scripts/arranjo_paredes.py", "scripts/separadores_fila.py"]

    faltas += confere_decisoes("data/decisoes.json")
    checados.append("data/decisoes.json")

    faltas += confere_decisoes("data/prancheta_hall2.json", bloco="decisoes")
    checados.append("data/prancheta_hall2.json")

    faltas += confere_grupos()
    checados.append("data/grupos_mesas.json")

    f_sin, tinha = confere_sinalizacao()
    faltas += f_sin
    checados.append("saidas/sinalizacao_v2.json" if tinha
                    else "saidas/sinalizacao_v2.json (ausente — não conferido)")
    if not tinha:
        pendente_sinalizacao = True
    else:
        pendente_sinalizacao = False

    faltas += confere_desenhos()
    checados.append("saidas/separadores_*.svg")

    faltas += confere_superadas()
    checados.append("nenhuma paleta superada no repositório")

    for c in checados:
        print(f"  conferido: {c}")

    if faltas:
        print(f"\n{len(faltas)} divergência(s) — a vinculação está quebrada:\n")
        for f in faltas:
            print("   ", f)
        print("\nCorrija o consumidor, ou, se a decisão mudou de verdade, mude "
              "data/zonas.json e regenere: \n"
              "    python3 scripts/arranjo_paredes.py --grava\n"
              "    python3 scripts/separadores_fila.py --grava")
        return 1

    print("\n  as zonas batem em todos os consumidores")
    if pendente_sinalizacao:
        print(PATCH_SINALIZACAO)
    return 0


if __name__ == "__main__":
    sys.exit(main())
