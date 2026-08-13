"""Carga e normalizacao dos dados do TSE para a zona de Dublin (Irlanda).

Fontes (pasta Google Drive do usuario, copiadas em data/raw/):
  - eleitorado_local_votacao_2026_ZZ.csv  : uma linha por secao do exterior,
    com tipo (Principal/Agregada), NR_SECAO_PRINCIPAL e QT_ELEITOR_SECAO.
  - Filtrado_Dublin.csv                   : perfil do eleitorado de Dublin,
    uma linha por cruzamento demografico, com NR_SECAO x NM_LOCAL_VOTACAO
    x QT_ELEITORES. NM_LOCAL_VOTACAO e o local de votacao original do
    eleitor e funciona como proxy de onde ele reside.

Os dois arquivos vem em latin-1. O Filtrado_Dublin.csv foi re-exportado com a
linha inteira envolvida em aspas e as aspas internas duplicadas, entao precisa
de um passo de desempacotamento antes do split por ';'.
"""

from pathlib import Path

import pandas as pd

RAW = Path(__file__).resolve().parent.parent / "data" / "raw"

CD_MUNICIPIO_DUBLIN = "29661"
ENCODING = "latin-1"


def _limpa(valor: str) -> str:
    """Remove aspas externas e espacos de um campo."""
    valor = valor.strip()
    if len(valor) >= 2 and valor[0] == '"' and valor[-1] == '"':
        valor = valor[1:-1]
    return valor.strip()


def carrega_locais_votacao() -> pd.DataFrame:
    """Le o arquivo de secoes do exterior e devolve apenas as de Dublin."""
    caminho = RAW / "eleitorado_local_votacao_2026_ZZ.csv"
    df = pd.read_csv(
        caminho,
        sep=";",
        quotechar='"',
        encoding=ENCODING,
        dtype=str,
        keep_default_na=False,
    )
    df.columns = [c.strip().strip('"') for c in df.columns]
    df = df[df["CD_MUNICIPIO"].str.strip() == CD_MUNICIPIO_DUBLIN].copy()

    for col in ("NR_SECAO", "NR_SECAO_PRINCIPAL", "QT_ELEITOR_SECAO",
                "QT_ELEITOR_ELEICAO_FEDERAL", "NR_LOCAL_VOTACAO"):
        df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")

    for col in ("DS_TIPO_SECAO_AGREGADA", "NM_LOCAL_VOTACAO", "DS_ENDERECO",
                "NM_LOCAL_VOTACAO_ORIGINAL", "DS_SITU_SECAO"):
        df[col] = df[col].astype(str).str.strip()

    return df.sort_values("NR_SECAO").reset_index(drop=True)


def carrega_perfil_eleitorado() -> pd.DataFrame:
    """Le o perfil do eleitorado de Dublin, desempacotando as aspas duplas.

    Cada linha do arquivo e um registro CSV de campo unico cujo conteudo e a
    linha real separada por ';'. Devolve o dataframe ja em formato tabular.
    """
    caminho = RAW / "Filtrado_Dublin.csv"
    linhas = caminho.read_text(encoding=ENCODING).splitlines()

    registros = []
    for bruta in linhas:
        bruta = bruta.strip()
        if not bruta:
            continue
        # Desempacota: tira as aspas externas e desdobra as aspas internas.
        if bruta.startswith('"') and bruta.endswith('"'):
            bruta = bruta[1:-1]
        bruta = bruta.replace('""', '"')
        registros.append([_limpa(c) for c in bruta.split(";")])

    cabecalho, dados = registros[0], registros[1:]
    # Descarta linhas com contagem de colunas divergente, se houver.
    dados = [linha for linha in dados if len(linha) == len(cabecalho)]

    df = pd.DataFrame(dados, columns=cabecalho)
    for col in ("NR_SECAO", "NR_LOCAL_VOTACAO", "QT_ELEITORES",
                "QT_ELEITORES_BIOMETRIA", "QT_ELEITORES_DEFICIENCIA",
                "QT_ELEITORES_NOME_SOCIAL"):
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    df["NM_LOCAL_VOTACAO"] = df["NM_LOCAL_VOTACAO"].str.strip()
    return df


def residencia_por_secao(perfil: pd.DataFrame) -> pd.DataFrame:
    """Soma QT_ELEITORES por secao x local de residencia.

    O arquivo de perfil e uma tabela de cruzamentos demograficos: cada linha e
    uma combinacao de genero/idade/escolaridade/etc. Somar QT_ELEITORES e
    obrigatorio -- contar linhas daria um numero sem sentido.
    """
    return (
        perfil.groupby(["NR_SECAO", "NR_LOCAL_VOTACAO", "NM_LOCAL_VOTACAO"],
                       as_index=False)["QT_ELEITORES"]
        .sum()
        .sort_values(["NR_SECAO", "QT_ELEITORES"], ascending=[True, False])
        .reset_index(drop=True)
    )


if __name__ == "__main__":
    locais = carrega_locais_votacao()
    perfil = carrega_perfil_eleitorado()
    residencia = residencia_por_secao(perfil)

    print(f"Secoes de Dublin no arquivo de locais : {len(locais)}")
    print(f"Tipos de secao                        : "
          f"{locais['DS_TIPO_SECAO_AGREGADA'].value_counts().to_dict()}")
    print(f"Total de eleitores (QT_ELEITOR_SECAO) : "
          f"{locais['QT_ELEITOR_SECAO'].sum():,}")
    print(f"Linhas no perfil do eleitorado        : {len(perfil):,}")
    print(f"Total de eleitores (perfil)           : "
          f"{perfil['QT_ELEITORES'].sum():,}")
    print(f"Secoes distintas no perfil            : {perfil['NR_SECAO'].nunique()}")
    print("\nLocais de residencia:")
    print(residencia.groupby("NM_LOCAL_VOTACAO")["QT_ELEITORES"].sum()
          .sort_values(ascending=False).to_string())
