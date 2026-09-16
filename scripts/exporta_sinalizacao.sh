#!/usr/bin/env sh
# Copia para um diretorio de destino o conjunto minimo de arquivos que
# reproduz a Rota do Eleitor e a Sinalizacao interna do Hall 2 (versao 2).
#
#   sh scripts/exporta_sinalizacao.sh /caminho/do/novo/repositorio [--com-fontes]
#
# Sem --com-fontes: leva o gerador, a prancheta e saidas/dados.json (nivel 1).
# Com --com-fontes: leva tambem os CSVs do TSE e os scripts que produzem
# saidas/dados.json (nivel 2), para que a cadeia inteira seja reproduzivel.
set -eu
DEST="${1:?destino obrigatorio}"
BASE="$(cd "$(dirname "$0")/.." && pwd)"
NIVEL1="scripts/sinalizacao_v2.py data/prancheta_paredes_abc.json saidas/dados.json"
NIVEL2="data/raw/Filtrado_Dublin.csv data/raw/eleitorado_local_votacao_2026_ZZ.csv data/raw/mapa_agregacoes_TSE.png scripts/parse_dados.py scripts/mapa_agregacoes.py"
SAIDAS="saidas/sinalizacao_v2.json saidas/rota_do_eleitor_v2.html saidas/sinalizacao_hall2_v2.html"
LISTA="$NIVEL1 $SAIDAS"
[ "${2:-}" = "--com-fontes" ] && LISTA="$LISTA $NIVEL2"
for f in $LISTA; do
  mkdir -p "$DEST/$(dirname "$f")"
  cp "$BASE/$f" "$DEST/$f"
  echo "copiado  $f"
done
cp "$BASE/TRANSFERENCIA_SINALIZACAO.md" "$DEST/"
echo "copiado  TRANSFERENCIA_SINALIZACAO.md"
( cd "$DEST" && sha256sum $LISTA > CONFERENCIA_SHA256.txt ) && echo "gerado   CONFERENCIA_SHA256.txt"
echo
echo "Conferir no destino: cd $DEST && python3 scripts/sinalizacao_v2.py && git diff --stat saidas/"
