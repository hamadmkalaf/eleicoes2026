# Transferência da sinalização (Rota do Eleitor + Hall 2) para o repositório final

> Documento de passagem. Escrito em 16/09/2026 para ser lido no início de outra
> sessão do Claude, que fará a transferência efetiva para o repositório onde
> ficarão só as versões finais. Tudo o que está aqui foi verificado nesta sessão:
> o conjunto mínimo abaixo foi copiado para um diretório vazio e regenerou as
> três saídas byte a byte idênticas às publicadas.

Origem: `hamadmkalaf/eleicoes2026`, branch `claude/voter-route-signage-update-bjgbhp`,
commit `1ca1e19` (PR [#26](https://github.com/hamadmkalaf/eleicoes2026/pull/26)).

---

## 1. O que está sendo transferido

Dois artefatos publicados e a cadeia que os gera.

| Artefato | URL | Versão publicada | Arquivo-fonte |
|---|---|---|---|
| Rota do Eleitor RDS | https://claude.ai/artifact/1PQjgzstbiNorfJgagXhB5 | 7 (16/09/2026) | `saidas/rota_do_eleitor_v2.html` |
| Sinalização RDS Hall 2 | https://claude.ai/artifact/BcT5yzxRkSaUsbbHQQgjWF | 4 (16/09/2026) | `saidas/sinalizacao_hall2_v2.html` |

Os dois HTML são gerados por um único script a partir de dois arquivos de dados.
Nada neles é escrito à mão: para alterar conteúdo, altera-se o script ou os
dados e roda-se de novo.

---

## 2. Conjunto mínimo de arquivos

### Nível 1 — reproduz as páginas (obrigatório)

| Arquivo | SHA-256 (12 primeiros) | Papel |
|---|---|---|
| `scripts/sinalizacao_v2.py` | `3658e9cfee2b` | Gerador: blocos, listas por porta, tabela mestra, peças, orçamento e as duas páginas. Falha em vez de gravar se as 51 seções não aparecerem uma vez, se os aptos não somarem 16.794 ou se as 28 mesas não fecharem. |
| `data/prancheta_paredes_abc.json` | `11f97fc776c4` | Prancheta **Paredes_ABC** (`paredes-abc-20260915`): 28 mesas com x, y, rot, lado, seções, esperado; portas S1–S9, O1, O2, N1, N2, L1–L4, R1; zonas livres; serpenteados reservados. Extraída do artefato "Prancheta pelas Seções" (https://claude.ai/artifact/Szv5egKpHy3umh4udAybvr), constante `D` do script embutido. |
| `saidas/dados.json` | `fae16cb49d9c` | As 51 seções e 28 urnas do TSE (aptos, principal/agregada, residência). Gerado dos CSVs do nível 2. |

Saídas geradas (também no branch, para conferência):

| Arquivo | SHA-256 (12 primeiros) |
|---|---|
| `saidas/sinalizacao_v2.json` | `22f27a722aaa` |
| `saidas/rota_do_eleitor_v2.html` | `02a19eebb8fd` |
| `saidas/sinalizacao_hall2_v2.html` | `18f96c270bcb` |

### Nível 2 — reproduz `saidas/dados.json` (recomendado)

Só é necessário se o repositório final quiser a cadeia completa a partir dos
arquivos oficiais do TSE. Verificado: `python3 scripts/mapa_agregacoes.py`
regenera `dados.json` idêntico (o `.xlsx` muda só por carimbo de data).

| Arquivo | SHA-256 (12 primeiros) | Papel |
|---|---|---|
| `data/raw/eleitorado_local_votacao_2026_ZZ.csv` | `6e7c6aa657fc` | TSE, 13/08/2026 — seção a seção no exterior (latin-1, `;`) |
| `data/raw/Filtrado_Dublin.csv` | `774054e30ee6` | TSE, 14/07/2026 — perfil do eleitorado de Dublin (latin-1, `;`, linhas envoltas em aspas) |
| `data/raw/mapa_agregacoes_TSE.png` | `2ba9f8515574` | Mapa oficial de pares principal → agregada (referência visual; registra o erro de digitação 3222 → 3322) |
| `scripts/parse_dados.py` | `52a03ee0e45e` | Leitura e desempacotamento dos CSVs |
| `scripts/mapa_agregacoes.py` | `4fc7cd0289d6` | Produz `saidas/dados.json` e `saidas/Dublin_2026_agregacoes.xlsx` |

Dependências do nível 2: `pip install pandas openpyxl`. O nível 1 usa só a
biblioteca padrão do Python 3.

### O que **não** precisa ir

- `PLANO COM FLUXOS MELHORADO.png`, `RDS_Hall_2_Floorplan_(1).pdf`,
  `MRV - DUBLIN.pdf`, `SEÇÕES E RESPECTIVAS AGREGADAS - DUBLIN.pdf`,
  `2026.7.6_Proposta_Agregação_Eleições.xlsx` — referências humanas, não são
  lidas pelo gerador. Levar se o repositório final quiser o dossiê, não pela
  reprodutibilidade.
- Os branches `claude/rds-ballsbridge-signage-points-kml93e` (Rota v1),
  `claude/serene-rubin-tdzmlb` (Hall 2 v1, prancheta Hamad_Final),
  `claude/ring-3-horizontal-queue-pe4x3f` (modelo do Ring 3) — superados.
  A geometria do Ring 3 que a Rota v2 usa está **embutida como constante
  `RING`** em `scripts/sinalizacao_v2.py` (44 × 35 m, corredor em L de 3,0 m,
  zonas A 12,23 · B 14,14 · C 12,23 m, vãos de 1,20 m, bocas no extremo leste
  da borda sul), copiada do artefato "Montagem do Ring 3"
  (https://claude.ai/artifact/FcQs4H7fM3RcBxmyFywazV). Se o Ring 3 mudar de
  novo, é ali que se edita.
- As 21 fotos de `data/fotos/` (branch `project-analysis-documentation-w49q34`):
  a Rota v2 não embute imagens.

---

## 3. Como exportar

No repositório de origem, no branch acima:

```bash
sh scripts/exporta_sinalizacao.sh /caminho/do/repositorio-final            # nível 1
sh scripts/exporta_sinalizacao.sh /caminho/do/repositorio-final --com-fontes   # níveis 1 + 2
```

O script copia os arquivos mantendo os caminhos relativos (o gerador resolve
`data/` e `saidas/` a partir da própria posição em `scripts/`), copia este
documento e grava `CONFERENCIA_SHA256.txt` no destino.

Alternativa sem o script, a partir de um clone do repositório de origem:

```bash
git fetch origin claude/voter-route-signage-update-bjgbhp
git checkout origin/claude/voter-route-signage-update-bjgbhp -- \
  scripts/sinalizacao_v2.py data/prancheta_paredes_abc.json saidas/dados.json \
  saidas/sinalizacao_v2.json saidas/rota_do_eleitor_v2.html saidas/sinalizacao_hall2_v2.html
```

---

## 4. Como conferir no destino

```bash
cd /caminho/do/repositorio-final
sha256sum -c CONFERENCIA_SHA256.txt          # todos "OK"
python3 scripts/sinalizacao_v2.py            # imprime blocos, orçamento e "TOTAL 1820.0"
git status --short saidas/                   # nada deve mudar
```

Saída esperada do gerador:

```
blocos: [5, 5, 6] secoes/porta: [18, 16, 17]
  mesh       10 ×     60 =   600.00
  pvc         3 ×     55 =   165.00
  vinil       3 ×     30 =    90.00
  pullup      3 ×     85 =   255.00
  xbanner    16 ×     40 =   640.00
  correx      2 ×     15 =    30.00
  fixacao     1 ×     40 =    40.00
TOTAL 1820.0 faixa [1700, 1900]
condados ambiguos: ['Cork', 'Limerick']
```

Se qualquer asserção falhar, os dados foram alterados — não publicar.

---

## 5. Os artefatos publicados

Os dois artefatos pertencem à conta `hamadmkalaf@gmail.com` e são
independentes do repositório: a URL continua válida depois da transferência.
Duas opções para a nova sessão:

**Manter as URLs atuais (recomendado, porque o Hall 2 já foi compartilhado).**
Na nova sessão, antes de qualquer republicação, ler cada artefato com a
ferramenta Artifact (`action: read`, com a URL) — a republicação é recusada se
a versão viva não tiver sido lida naquela sessão — e depois publicar o HTML
regenerado passando a mesma URL em `url`. O favicon fica o que é (🧭 na Rota,
🗳️🧭 no Hall 2); não passar `favicon` nem `icon` na republicação.

**Criar artefatos novos a partir do repositório final.** Publicar os dois HTML
sem `url`; anotar as URLs novas neste documento e no rodapé das páginas; avisar
quem tem o link antigo do Hall 2 (está compartilhado "com qualquer pessoa com o
link", apontando para uma versão fixada anterior).

Os HTML são escritos para o esqueleto do Artifact (começam em `<title>`, sem
`<html>`/`<head>`/`<body>`); para abrir localmente num navegador basta um
invólucro `<!doctype html><html><body>…</body></html>`.

O orçamento editável guarda os preços digitados só no `localStorage` do
navegador de quem edita. Para fixar novos preços de verdade, editar `MODELOS`
em `scripts/sinalizacao_v2.py` e regerar.

---

## 6. Fontes externas que as páginas citam (para o dossiê, não para rodar)

| Insumo | Onde está | Como entrou |
|---|---|---|
| Prancheta Paredes_ABC (15/09/2026) | https://claude.ai/artifact/Szv5egKpHy3umh4udAybvr | copiada para `data/prancheta_paredes_abc.json` |
| Montagem do Ring 3 (15/09/2026) | https://claude.ai/artifact/FcQs4H7fM3RcBxmyFywazV | geometria copiada para a constante `RING` |
| Levantamento fotográfico de 24/08/2026 (21 fotos) | Google Drive › Eleicao › Fotos local; branch `project-analysis-documentation-w49q34`, `data/fotos/` | base das decisões de fixação (vidro na fachada sul, portas de aço na lateral leste, gradil na Merrion Road) |
| Orçamento do 1º turno (itens c e d) | `contexto_eleicoes_dublin_2026.md` §6 | EUR 1.961 banners, EUR 1.303 / 100 unifilas |
| Contexto da sinalização v1 | Google Drive › `contexto_sinalizacao_hall2.md`; branch `serene-rubin-tdzmlb` | decisões que a v2 herda (4 dígitos, sem número de mesa, cor por porta) |
| Preços de referência (16/09/2026, inc. IVA) | PrintNPack, Bannerz.ie, Kaizen Print, Printroom, Printco — links no rodapé da Rota | premissa; **o anexo de preços do Posto não chegou** e deve substituí-los |

---

## 7. Decisões congeladas nas páginas

Mudar qualquer uma exige regerar e republicar as duas.

1. Porta A → parede oeste, B → norte, C → leste (Posto, 15/09).
2. Mesas sem número; o eleitor precisa saber só a seção; 4 dígitos.
3. Nenhuma regra por condado nem por faixa numérica: toda peça de triagem carrega as 51 seções.
4. Ponto "descubra sua seção" fora do RDS, na calçada da Merrion Road.
5. Externo só em grade, gradil e CCB, em mesh, sem base; lona fechada só na lateral leste; interno autoportante.
6. Paleta A azul `#1f5fa8`, B âmbar `#b8760a`, C magenta `#8b3a8e` (mesma da prancheta e do Ring 3).
7. Faixa de orçamento EUR 1.700–1.900.

---

## 8. Pendências que a transferência não resolve

1. **Anexo de preços e modelos do Posto** — substituir `MODELOS` no gerador.
2. Autorização do RDS para o gradil da Merrion Road e para a mesa do P0 na calçada.
3. Teste do ímã nas portas de serviço da lateral leste.
4. Posição real do portão de eleitores e do Ring 3 no apron (estimativas no desenho).
5. Caderno impresso das 51 seções para o P0 e teste de cobertura de dados na calçada.
6. Refazer a simulação das vias de fila sobre a Paredes_ABC antes de comprar fita e decalque.
7. Contraste do âmbar da porta B sobre branco.

---

## 9. Prompt sugerido para a nova sessão

> Estou transferindo a sinalização do 1º turno (Rota do Eleitor e Sinalização
> interna do Hall 2) para este repositório, que terá só as versões finais. Leia
> `TRANSFERENCIA_SINALIZACAO.md` antes de qualquer coisa. Os arquivos já estão
> copiados [ou: copie-os do branch `claude/voter-route-signage-update-bjgbhp`
> de `hamadmkalaf/eleicoes2026` com `scripts/exporta_sinalizacao.sh`]. Confira
> os SHA-256, rode `python3 scripts/sinalizacao_v2.py` e confirme que
> `saidas/` não muda. Depois [mantenha as URLs atuais dos dois artefatos,
> lendo-os antes de republicar | crie artefatos novos e anote as URLs]. Não
> altere conteúdo nesta sessão.
