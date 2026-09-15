"""Le as tres fontes oficiais do Cartorio Eleitoral em `data/oficiais/`.

Ate 15/09/2026 o aptos por secao e o mapa de agregacoes chegavam por CSV do
TSE (`data/raw/`) e por um PNG do mapa de agregacoes, que trazia um erro de
digitacao. Estes tres PDFs sao a fonte primaria e substituem o PNG:

  aptos_por_secao_dublin_2026-07-13.pdf   ELO, 13/07/2026 16:24
      "Quantitativo de eleitores aptos por secao", zona 1/ZZ, municipio
      29661-DUBLIN: as 51 secoes com aptos, agrupadas pelo local de votacao
      de origem (o condado de domicilio do eleitor). 16.794 aptos.

  secoes_agregadas_dublin_2026.pdf        Cartorio Eleitoral
      "Secoes e respectivas agregadas": os 28 pares principal -> agregada.

  mrv_mesarios_dublin_2026-09-13.pdf      ELO/Convoca+, 13/09/2026 11:32
      "Relatorio de Mesarios por Situacao", tipo de funcao MRV: os mesarios
      nomeados, secao a secao, com a situacao de cada nomeacao.

Precisa de `pdfplumber` (pip install pdfplumber). Rodando sozinho, imprime o
resumo do que leu.
"""
import os
import re

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OFICIAIS = os.path.join(RAIZ, "data", "oficiais")

APTOS = os.path.join(OFICIAIS, "aptos_por_secao_dublin_2026-07-13.pdf")
AGREGADAS = os.path.join(OFICIAIS, "secoes_agregadas_dublin_2026.pdf")
MESARIOS = os.path.join(OFICIAIS, "mrv_mesarios_dublin_2026-09-13.pdf")

FUNCOES = ("Presidente", "1º Mesário", "2º Mesário", "1º Secretário", "2º Secretário")
# As quatro que compoem a mesa receptora completa; a 2a secretaria nao e usada
# em Dublin (nenhuma secao tem cinco nomeados).
FUNCOES_MINIMAS = {"Presidente", "1º Mesário", "2º Mesário", "1º Secretário"}


def _texto(caminho):
    try:
        import pdfplumber
    except ImportError:  # pragma: no cover - depende do ambiente
        raise SystemExit("este script precisa de pdfplumber: pip install pdfplumber")
    if not os.path.exists(caminho):
        raise SystemExit(f"fonte oficial ausente: {caminho}")
    with pdfplumber.open(caminho) as pdf:
        return "\n".join(pg.extract_text() or "" for pg in pdf.pages)


def aptos_por_secao():
    """({secao: (aptos, localidade)}, {localidade: total}, total_declarado).

    `localidade` e o NM_LOCAL_VOTACAO de origem do eleitor -- o condado onde
    ele mora, nao onde vota. E a chave das taxas de `comparecimento.py`.
    """
    secoes, totais, local = {}, {}, None
    for linha in _texto(APTOS).split("\n"):
        # "Local : 1031 CORK" (um "*" antes do codigo marca local bloqueado)
        m = re.match(r"Local\s*:\s*\*?\s*(\d+)\s+(.+?)\s*$", linha)
        if m:
            local = m.group(2).strip()
            continue
        # "Seção(ões)/Aptos : 0519** | 384 3307** | 394" -- varias por linha
        for secao, n in re.findall(r"(\d{4})\*\*\s*\|\s*(\d+)", linha):
            secoes[int(secao)] = (int(n), local)
        m = re.search(r"Total de Eleitores aptos do local\s*:\s*(\d+)", linha)
        if m:
            totais[local] = int(m.group(1))
    m = re.search(r"Total de Eleitores\s*:\s*(\d+)", _texto(APTOS))
    return secoes, totais, int(m.group(1))


def agregacoes():
    """([(principal, agregada|None)], n_mrv_declarado), na ordem do PDF."""
    texto = _texto(AGREGADAS)
    pares = []
    for linha in texto.split("\n"):
        # "3313 3889" ou "3442 ---" para a mesa que roda com uma secao so
        m = re.match(r"^(\d{4})\s+(\d{4}|-+)\s*$", linha.strip())
        if m:
            agregada = m.group(2)
            pares.append((int(m.group(1)), None if set(agregada) == {"-"} else int(agregada)))
    m = re.search(r"DUBLIN\s+(\d+)", texto)
    return pares, (int(m.group(1)) if m else None)


def mesarios():
    """({secao: [(funcao, nome, situacao)]}, resumo do cabecalho)."""
    texto = _texto(MESARIOS)
    por_secao, secao = {}, None
    for linha in texto.split("\n"):
        m = re.match(r"^Seção\s+(\d{4})\s*$", linha.strip())
        if m:
            secao = int(m.group(1))
            por_secao.setdefault(secao, [])
            continue
        for funcao in FUNCOES:
            if not linha.startswith(funcao) or secao is None:
                continue
            # "<nome> <inscricao 12 dig> <sit. eleitor> <sit. mesario> <resposta>"
            # O nome pode quebrar para a linha seguinte; a quebra fica de fora.
            m = re.match(r"(.+?)\s+(\d{12})\s+(\w+)\s+(\w+)\s+(.*?)\s*-?\s*$",
                         linha[len(funcao):].strip())
            if m:
                por_secao[secao].append((funcao, m.group(1).strip(), m.group(5).strip()))
            break
    m = re.search(r"Total\s+Atribuídos\s+Convocados\s+Nomeados\s+Confirmados\s+"
                  r"Sem resposta\s+Pedido de dispensa\s*\n\s*" + r"(\d+)\s+" * 6 + r"(\d+)", texto)
    campos = ("total", "atribuidos", "convocados", "nomeados",
              "confirmados", "sem_resposta", "dispensa")
    return por_secao, (dict(zip(campos, map(int, m.groups()))) if m else {})


if __name__ == "__main__":
    secoes, totais, total = aptos_por_secao()
    pares, n_mrv = agregacoes()
    mesa, resumo = mesarios()
    print(f"aptos    · {len(secoes)} seções em {len(totais)} localidades · "
          f"soma {sum(v[0] for v in secoes.values())} · declarado {total}")
    print(f"agregações · {len(pares)} pares (o PDF declara {n_mrv} MRVs) · "
          f"{len({s for p in pares for s in p if s})} seções cobertas")
    print(f"mesários · {len(mesa)} seções · {sum(len(v) for v in mesa.values())} nomeados · {resumo}")
