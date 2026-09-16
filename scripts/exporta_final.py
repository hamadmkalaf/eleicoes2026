"""Monta, num diretorio limpo, so o que o desenho final do Hall 2 precisa.

O repositorio atual carrega tres camadas misturadas: as fontes, a cadeia que
produz o desenho, e o sedimento de vinte e tantas iteracoes. Este script separa
a primeira da terceira e grava a segunda inteira, para o repositorio novo
comecar sem sedimento e ainda assim reproduzir tudo do zero.

    python3 scripts/exporta_final.py /caminho/do/destino
    python3 scripts/exporta_final.py --listar     # so imprime o manifesto

Depois de copiar, o destino roda a cadeia inteira sozinho -- e e isso que
`--verificar` testa, num diretorio temporario.
"""
import json
import os
import shutil
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------------------------------------------------------------------------
# O manifesto. Cada entrada e (caminho, papel, por que fica).
# ---------------------------------------------------------------------------
FONTES = [
    ("data/oficiais/aptos_por_secao_dublin_2026-07-13.pdf", "fonte",
     "ELO 13/07: as 51 seções com aptos e condado de origem"),
    ("data/oficiais/secoes_agregadas_dublin_2026.pdf", "fonte",
     "Cartório: os 28 pares principal → agregada"),
    ("data/oficiais/mrv_mesarios_dublin_2026-09-13.pdf", "fonte",
     "Convoca+ 13/09: os 109 mesários nomeados por MRV"),
    ("data/raw/eleitorado_local_votacao_2026_ZZ.csv", "fonte",
     "TSE 13/08: seção a seção no exterior; alimenta saidas/dados.json"),
    ("data/raw/Filtrado_Dublin.csv", "fonte",
     "TSE 14/07: perfil do eleitorado de Dublin; alimenta saidas/dados.json"),
    ("data/prancheta_hall2.json", "fonte",
     "geometria medida do salão, do módulo e das 18 portas"),
    ("RDS_Hall_2_Floorplan_(1).pdf", "fonte",
     "planta original do RDS, de onde a geometria foi lida"),
]

CADEIA = [
    ("scripts/parse_dados.py", "script", "lê os dois CSV em latin-1 e desempacota"),
    ("scripts/mapa_agregacoes.py", "script", "→ saidas/dados.json e o .xlsx"),
    ("scripts/gera_pagina.py", "script", "→ saidas/dublin_agregacoes.html"),
    ("scripts/comparecimento.py", "script", "a taxa de 2022 por condado (base B)"),
    ("scripts/fontes_oficiais.py", "script", "leitor dos três PDFs oficiais"),
    ("scripts/gera_decisoes_base.py", "script", "→ o bloco mesas de data/decisoes.json"),
    ("scripts/arranjo_paredes.py", "script", "→ o cenário e a camada de layout"),
    ("scripts/gera_prancheta_por_secao.py", "script", "→ saidas/prancheta_por_secao.html"),
    ("scripts/prancheta_por_secao_template.html", "script", "o molde da página"),
    ("scripts/confere_prancheta.py", "confere", "os dados, contra os três PDFs"),
    ("scripts/confere_arranjo.py", "confere", "os sete itens do arranjo"),
]

ESTADO = [
    ("data/decisoes.json", "estado",
     "as decisões do Posto e as 28 mesas; gerado, mas também é o registro"),
    ("cenarios/paredes-abc-20260915.json", "estado",
     "o cenário final: as 28 posições"),
    ("saidas/dados.json", "estado", "as 51 seções com aptos e origem"),
]

SAIDAS = [
    ("saidas/prancheta_por_secao.html", "saída", "a peça publicada"),
    ("saidas/dublin_agregacoes.html", "saída", "a análise das agregações"),
    ("saidas/Dublin_2026_agregacoes.xlsx", "saída", "a mesma análise em planilha"),
]

DOCS = [
    ("CONFERENCIA_PRANCHETA_2026-09-15.md", "doc",
     "a conferência e os onze adendos: o porquê de cada decisão"),
    ("contexto_eleicoes_dublin_2026.md", "doc",
     "o histórico do problema; tem trechos superados, marcados no próprio texto"),
    ("PENDENCIAS", "doc", "o que falta fazer, por dono"),
    ("TRANSFERENCIA.md", "doc", "este plano de transferência"),
]

MANIFESTO = FONTES + CADEIA + ESTADO + SAIDAS + DOCS

# O que fica para trás, e por quê. Entra no relatório para a decisão ser
# explícita em vez de silenciosa.
DESCARTES = [
    ("data/raw/mapa_agregacoes_TSE.png",
     "superado pelos PDFs oficiais, e trazia o erro de digitação da seção 3222"),
    ("cenarios/hamad-final-20260914-170656.json",
     "cenário anterior, substituído pelo Paredes_ABC"),
    ("cenarios/equitativo.json",
     "cenário anterior, substituído pelo Paredes_ABC"),
    ("PLANO COM FLUXOS MELHORADO.png",
     "rascunho de fluxo anterior à planta medida"),
    ("README.md",
     "é do escopo antigo (só agregações); o repositório novo precisa de um próprio"),
]

ORDEM_DE_EXECUCAO = [
    ("python3 scripts/mapa_agregacoes.py", "as 51 seções → saidas/dados.json"),
    ("python3 scripts/gera_pagina.py", "a página das agregações"),
    ("python3 scripts/gera_decisoes_base.py --grava", "as 28 mesas, aptos e esperados"),
    ("python3 scripts/arranjo_paredes.py --grava", "o arranjo, as zonas e o cenário"),
    ("python3 scripts/gera_prancheta_por_secao.py", "a prancheta pelas seções"),
    ("python3 scripts/confere_prancheta.py", "confere os dados (sai 1 se divergir)"),
    ("python3 scripts/confere_arranjo.py", "confere o arranjo (sai 1 se divergir)"),
]


def listar():
    por_papel = {}
    for caminho, papel, porque in MANIFESTO:
        por_papel.setdefault(papel, []).append((caminho, porque))
    rotulos = {"fonte": "FONTES — não geradas, entram como estão",
               "script": "CADEIA — o que reproduz o desenho",
               "confere": "CONFERÊNCIAS — saem com código 1 se algo divergir",
               "estado": "ESTADO — gerado, mas também é registro; versionar",
               "saída": "SAÍDAS — as peças finais",
               "doc": "DOCUMENTOS"}
    total = 0
    for papel in ("fonte", "script", "confere", "estado", "saída", "doc"):
        print(f"\n{rotulos[papel]}")
        for caminho, porque in por_papel.get(papel, []):
            existe = "  " if os.path.exists(os.path.join(RAIZ, caminho)) else "!!"
            print(f" {existe} {caminho:<52} {porque}")
            total += 1
    print(f"\n{total} arquivos no manifesto.")
    print("\nFICA PARA TRÁS")
    for caminho, porque in DESCARTES:
        print(f"    {caminho:<52} {porque}")
    print("\nORDEM DE EXECUÇÃO, no repositório novo")
    for i, (cmd, oq) in enumerate(ORDEM_DE_EXECUCAO, 1):
        print(f"    {i}. {cmd:<48} {oq}")


def faltando():
    return [c for c, _, _ in MANIFESTO if not os.path.exists(os.path.join(RAIZ, c))]


def copia(destino):
    ausentes = faltando()
    if ausentes:
        raise SystemExit("faltam no repositório atual:\n  " + "\n  ".join(ausentes))
    for caminho, _, _ in MANIFESTO:
        alvo = os.path.join(destino, caminho)
        os.makedirs(os.path.dirname(alvo) or destino, exist_ok=True)
        shutil.copy2(os.path.join(RAIZ, caminho), alvo)
    return len(MANIFESTO)


def _hashes(destino):
    """O sha256 de cada arquivo gerado, para ver se a cadeia e deterministica."""
    import hashlib
    fora = {}
    for caminho, papel, _ in MANIFESTO:
        if papel not in ("estado", "saída") or caminho.endswith(".xlsx"):
            continue      # o .xlsx grava a data de criação dentro do arquivo
        alvo = os.path.join(destino, caminho)
        if os.path.exists(alvo):
            fora[caminho] = hashlib.sha256(open(alvo, "rb").read()).hexdigest()
    return fora


def verifica(destino):
    """Roda a cadeia inteira no destino e devolve (ok, relatorio).

    Alem de exigir que todo passo saia com codigo 0, compara o que a cadeia
    regenerou com o que foi copiado: se algum arquivo gerado mudar, a cadeia
    reproduz mas nao e deterministica, e o repositorio novo vai versionar
    ruido a cada rodada.
    """
    antes = _hashes(destino)
    linhas, ok = [], True
    for cmd, oq in ORDEM_DE_EXECUCAO:
        r = subprocess.run(cmd, shell=True, cwd=destino,
                           capture_output=True, text=True)
        marca = "ok " if r.returncode == 0 else "FALHOU"
        if r.returncode != 0:
            ok = False
            linhas.append(f"  {marca} {cmd}\n        {r.stderr.strip()[:400]}")
        else:
            linhas.append(f"  {marca} {cmd}  — {oq}")
    depois = _hashes(destino)
    mudaram = sorted(k for k in antes if antes[k] != depois.get(k))
    linhas.append("")
    if mudaram:
        ok = False
        linhas.append(f"  {len(mudaram)} arquivo(s) gerado(s) saíram diferentes "
                      f"do que foi copiado — a cadeia não é determinística:")
        linhas.extend(f"        {k}" for k in mudaram)
    else:
        linhas.append(f"  os {len(antes)} arquivos gerados saíram idênticos aos "
                      f"copiados — a cadeia é determinística")
    return ok, "\n".join(linhas)


def main(argv):
    if "--listar" in argv or len(argv) < 2:
        listar()
        return 0
    destino = os.path.abspath(argv[1])
    os.makedirs(destino, exist_ok=True)
    n = copia(destino)
    print(f"{n} arquivos copiados para {destino}")
    if "--verificar" in argv:
        print("\nRodando a cadeia inteira no destino:")
        ok, relatorio = verifica(destino)
        print(relatorio)
        print("\n" + ("a cadeia fecha sozinha no destino"
                      if ok else "A CADEIA NÃO FECHA — ver acima"))
        return 0 if ok else 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
