# Transferência para o repositório final

Este documento é o roteiro de execução da migração deste repositório
(`hamadmkalaf/eleicoes2026`) para um repositório novo, que conterá **apenas as
versões finais e os arquivos necessários para chegar a elas**.

Foi escrito para ser lido por uma sessão do Claude Code que vá executar a
migração, e por quem a supervisiona. Os passos estão na ordem em que devem
acontecer. As decisões que só o Posto pode tomar estão isoladas na seção 3 e
**bloqueiam o resto** — não comece pelo passo 5.

---

## 1. O que existe hoje, e onde

### 1.1 Repositório de origem

| | |
|---|---|
| Repositório | `hamadmkalaf/eleicoes2026` |
| Branch que carrega tudo | `claude/trusting-einstein-q6kefo` |
| Branch padrão do repositório | `claude/dublin-electoral-sections-3odh1w` |
| PR aberto | [#25](https://github.com/hamadmkalaf/eleicoes2026/pull/25), rascunho |
| Tamanho | 5,0 MB de árvore · 2,5 MB de `.git` |

**Anomalia a registrar:** não existe branch `main`. A branch padrão do
repositório é uma branch de trabalho do Claude. A branch
`claude/trusting-einstein-q6kefo` é um **superset estrito** da branch padrão —
verificado com
`git diff --name-only --diff-filter=A claude/trusting-einstein-q6kefo origin/claude/dublin-electoral-sections-3odh1w`,
que retorna vazio. Ou seja: **um único checkout da branch
`claude/trusting-einstein-q6kefo` carrega 100% do conteúdo do repositório.**
Não é preciso mesclar nada antes de migrar.

### 1.2 Os 22 arquivos versionados

| Arquivo | Papel | Vai? |
|---|---|---|
| `README.md` | índice da análise de agregações | reescrever |
| `PENDENCIAS` | lista de tarefas abertas | sim, renomear para `PENDENCIAS.md` |
| `contexto_eleicoes_dublin_2026.md` | contexto consolidado, 8 seções | sim |
| `data/raw/eleitorado_local_votacao_2026_ZZ.csv` | fonte TSE | sim, **sem renomear** |
| `data/raw/Filtrado_Dublin.csv` | fonte TSE | sim, **sem renomear** |
| `data/raw/mapa_agregacoes_TSE.png` | fonte TSE | sim, **sem renomear** |
| `scripts/parse_dados.py` | carga dos CSVs | sim |
| `scripts/mapa_agregacoes.py` | análise → xlsx + json | sim |
| `scripts/gera_pagina.py` | json → página das urnas | sim |
| `scripts/ring3_montagem.py` | geometria, lista de materiais e planta do Ring 3 | sim |
| `scripts/gera_pagina_ring3.py` | montagem da folha do Ring 3 | sim |
| `scripts/ring3_montagem.tpl.html` | template da folha do Ring 3 | sim |
| `saidas/Dublin_2026_agregacoes.xlsx` | 5 abas | sim (é saída, mas é o entregável) |
| `saidas/dados.json` | dados da página das urnas | sim |
| `saidas/dublin_agregacoes.html` | página "Urnas de Dublin" | sim |
| `saidas/ring3_montagem.html` | folha "Montagem do Ring 3" | sim |
| `saidas/ring3_planta.svg` | planta do Ring 3 | sim |
| `RDS_Hall_2_Floorplan_(1).pdf` | planta do RDS, recebida do local | sim, para `referencias/` |
| `MRV - DUBLIN.pdf` | material sobre a MRV | sim, para `referencias/` |
| `SEÇÕES E RESPECTIVAS AGREGADAS - DUBLIN.pdf` | agregação, versão TSE | sim, para `referencias/` |
| `2026.7.6_Proposta_Agregação_Eleições.xlsx` | proposta de agregação | sim, para `referencias/` |
| `PLANO COM FLUXOS MELHORADO.png` | rascunho de fluxo | **decidir** — ver 3.4 |

### 1.3 Os 16 artefatos publicados no claude.ai

Inventário completo em `transferencia/manifesto-artefatos.tsv`, com URL, data,
tema e status de cada um. Resumo:

| Situação | Quantos | Quais |
|---|---|---|
| Reproduzível a partir do repositório | **2** | Montagem do Ring 3 · Urnas de Dublin |
| Órfão — existe só como HTML no claude.ai | **10** | plantas do salão, sinalização, rota do eleitor, pranchetas, simulador, panorama |
| Superado por versão posterior | **1** | Ring 3, cenários de fila |
| Provavelmente superado, a confirmar | **3** | As 28 Mesas nas Paredes · Quantas mesas cabem no Hall 2 · Fluxo do Posto de Dublin |
| Fora de escopo | **1** | Teses Temáticas (outro projeto) |

---

## 2. O risco central desta transferência

**O repositório contém uma fração pequena do projeto.** Dois dos dezesseis
artefatos têm gerador versionado. Os outros catorze existem apenas como HTML
publicado no claude.ai, produzidos por scripts que rodaram em sessões
anteriores e nunca foram commitados — entre eles `scripts/salao.py` e
`scripts/ring3.py`, citados no rodapé do artefato "Ring 3, cenários de fila" e
hoje perdidos.

Consequência prática: **migrar o repositório não migra o projeto.** Se a
migração copiar só os 22 arquivos versionados, o repositório novo continuará
sem a planta-base do Hall 2, sem a sinalização, sem a rota do eleitor e sem o
panorama — que é justamente o conteúdo que o Posto mostra para terceiros.

Por isso o passo 5 (exportar os artefatos órfãos) não é opcional, e vem antes
de qualquer coisa que se pareça com "terminar".

### 2.1 Os artefatos não se movem junto com o repositório

Um artefato publicado é uma página no claude.ai com URL própria e permissão
própria. Copiar o HTML para o repositório novo **não muda o URL** e não
transfere nada; e republicar o mesmo HTML de outra conversa **cria um artefato
novo, com URL novo**, deixando o link antigo apontando para a versão velha.

Recomendação: **manter os URLs existentes** — alguns já foram compartilhados —
e tratar o HTML no repositório como arquivo de referência, não como fonte de
publicação. Quando um artefato precisar ser atualizado, republicar **no mesmo
URL**, passando o parâmetro `url` da ferramenta Artifact. Nunca republicar sem
`url`, sob pena de criar um segundo artefato com o mesmo título.

---

## 3. Decisões que bloqueiam a execução

Responda às cinco antes de abrir a sessão de migração. Elas mudam o que a
sessão faz.

### 3.1 Nome, dono e visibilidade do repositório novo

O repositório guarda planta do salão, desenho de barreiras, dimensionamento de
staff e orçamento de um local de votação. **Deve ser privado.** Defina também
se fica na conta pessoal ou numa organização do Posto — isso decide quem
mantém o acesso depois que a eleição passar.

Sugestão de nome: `eleicoes-dublin-2026`.

### 3.2 História: recomeçar ou preservar

**Recomendação: recomeçar.** O repositório novo nasce com `git init` e um único
commit inicial, e `hamadmkalaf/eleicoes2026` fica como arquivo morto, intacto,
para consulta. Motivos: a história atual tem só 7 commits, boa parte deles
`Add files via upload`; não há nada nela que valha carregar; e o pedido é
justamente um repositório com "apenas as versões finais".

A alternativa — `git filter-repo` para arrastar a história — custa mais e
entrega menos neste caso. Só vale se houver razão de auditoria para provar
quando cada arquivo entrou.

### 3.3 Os três artefatos "provavelmente superados"

`As 28 Mesas nas Paredes`, `Quantas mesas cabem no Hall 2` e `Fluxo do Posto de
Dublin` são de agosto e início de setembro, anteriores às plantas de 06 a 16 de
setembro. Provavelmente foram superados, mas **isso não pode ser inferido pelas
datas** — pode haver conteúdo neles que nunca foi transportado. Abra os três e
decida um a um: migra como final, migra como histórico, ou não migra.

### 3.4 `PLANO COM FLUXOS MELHORADO.png`

É um rascunho anotado à mão, de 1,1 MB — o maior arquivo do repositório. Se o
conteúdo dele já está na "Rota do Eleitor RDS", não migra. Se tem anotação que
não foi transportada, migra para `referencias/` com um nome que diga o que é.

### 3.5 O que fazer com o repositório de origem depois

Sugestão: mesclar o PR #25, arquivar o repositório no GitHub (Settings →
Archive), e pôr no `README.md` dele uma linha apontando para o novo. Repositório
arquivado fica somente-leitura e para de aparecer como trabalho em andamento.

---

## 4. Estrutura-alvo

```
eleicoes-dublin-2026/            (privado)
├── README.md                    índice: o que está decidido, o que está aberto
├── PENDENCIAS.md
├── contexto_eleicoes_dublin_2026.md
├── data/
│   └── raw/                     ← NOMES DE ARQUIVO INTOCADOS
│       ├── eleitorado_local_votacao_2026_ZZ.csv
│       ├── Filtrado_Dublin.csv
│       └── mapa_agregacoes_TSE.png
├── scripts/
│   ├── parse_dados.py
│   ├── mapa_agregacoes.py
│   ├── gera_pagina.py
│   ├── ring3_montagem.py
│   ├── gera_pagina_ring3.py
│   └── ring3_montagem.tpl.html
├── saidas/
│   ├── Dublin_2026_agregacoes.xlsx
│   ├── dados.json
│   ├── dublin_agregacoes.html
│   ├── ring3_montagem.html
│   └── ring3_planta.svg
├── referencias/                 recebidos de terceiros, não gerados aqui
│   ├── rds-hall2-planta.pdf
│   ├── mrv-dublin.pdf
│   ├── secoes-agregadas-dublin.pdf
│   └── proposta-agregacao-tse.xlsx
├── artefatos/                   HTML exportado do claude.ai — ver passo 5
│   ├── README.md                tabela título → URL → arquivo
│   └── *.html
└── transferencia/
    └── manifesto-artefatos.tsv
```

**Por que a estrutura plana se mantém.** Existe a tentação de reorganizar por
domínio (`ring3/`, `secoes/`, `salao/`). Não faça isso nesta migração. Os
scripts resolvem caminho por `Path(__file__).resolve().parent.parent`, e
`parse_dados.py` abre os CSVs pelo nome exato — mover pastas ou renomear os
arquivos de `data/raw/` quebra a cadeia inteira em silêncio. Migração de
conteúdo e refatoração de layout são duas tarefas; junte as duas e não se sabe
qual delas quebrou. Se quiser o layout por domínio depois, são três constantes
de caminho para editar, com os testes de aceite da seção 6 para provar que
continua fechando.

**Renomeações permitidas** (nenhum script lê estes arquivos):

| De | Para |
|---|---|
| `RDS_Hall_2_Floorplan_(1).pdf` | `referencias/rds-hall2-planta.pdf` |
| `MRV - DUBLIN.pdf` | `referencias/mrv-dublin.pdf` |
| `SEÇÕES E RESPECTIVAS AGREGADAS - DUBLIN.pdf` | `referencias/secoes-agregadas-dublin.pdf` |
| `2026.7.6_Proposta_Agregação_Eleições.xlsx` | `referencias/proposta-agregacao-tse.xlsx` |
| `PENDENCIAS` | `PENDENCIAS.md` |

Motivo: espaço e acento em nome de arquivo quebram script, URL e linha de
comando sem aviso. Os arquivos de `data/raw/` ficam como estão **apesar
disso**, porque `parse_dados.py` os abre pelo nome literal.

---

## 5. Procedimento

Os passos 1 a 4 são de uma sessão do Claude Code com acesso ao repositório de
origem e permissão de criar o repositório de destino.

### Passo 1 — Clonar a origem

```bash
git clone --branch claude/trusting-einstein-q6kefo \
  https://github.com/hamadmkalaf/eleicoes2026.git origem
```

Confirme que a branch é o superset antes de seguir:

```bash
cd origem
git fetch origin claude/dublin-electoral-sections-3odh1w
git diff --name-only --diff-filter=A HEAD origin/claude/dublin-electoral-sections-3odh1w
# esperado: saída vazia
```

Se a saída **não** for vazia, apareceu conteúdo novo na outra branch depois de
16/09/2026 — pare e reavalie.

### Passo 2 — Montar a árvore nova

```bash
mkdir -p destino/{data/raw,scripts,saidas,referencias,artefatos,transferencia}
cd destino

cp ../origem/contexto_eleicoes_dublin_2026.md .
cp ../origem/PENDENCIAS PENDENCIAS.md
cp ../origem/data/raw/* data/raw/
cp ../origem/scripts/{parse_dados.py,mapa_agregacoes.py,gera_pagina.py} scripts/
cp ../origem/scripts/{ring3_montagem.py,gera_pagina_ring3.py,ring3_montagem.tpl.html} scripts/
cp ../origem/saidas/* saidas/
cp ../origem/transferencia/manifesto-artefatos.tsv transferencia/

cp "../origem/RDS_Hall_2_Floorplan_(1).pdf"                  referencias/rds-hall2-planta.pdf
cp "../origem/MRV - DUBLIN.pdf"                              referencias/mrv-dublin.pdf
cp "../origem/SEÇÕES E RESPECTIVAS AGREGADAS - DUBLIN.pdf"   referencias/secoes-agregadas-dublin.pdf
cp "../origem/2026.7.6_Proposta_Agregação_Eleições.xlsx"     referencias/proposta-agregacao-tse.xlsx

printf '__pycache__/\n*.pyc\n.DS_Store\n' > .gitignore
```

`PLANO COM FLUXOS MELHORADO.png` fica de fora por enquanto — depende da
decisão 3.4.

### Passo 3 — Provar que os geradores rodam no destino

**Antes do primeiro commit.** Se um gerador não roda, o repositório novo nasce
com saída que ninguém consegue reproduzir, que é exatamente o problema que a
migração existe para resolver.

```bash
pip install pandas openpyxl
cd destino
python3 scripts/mapa_agregacoes.py
python3 scripts/gera_pagina.py
python3 scripts/ring3_montagem.py
python3 scripts/gera_pagina_ring3.py
git diff --stat   # antes do commit não há git; use `diff -r` contra ../origem/saidas
```

Os quatro devem rodar **de qualquer diretório de trabalho** e reproduzir
`saidas/` byte a byte. `mapa_agregacoes.py` falha de propósito se as validações
não passarem — se ele falhar, o problema é dado corrompido na cópia, não o
script. Veja os critérios de aceite na seção 6.

> O `README.md` atual manda `cd scripts` antes de rodar. É instrução obsoleta e
> enganosa: os scripts resolvem caminho pelo próprio arquivo. Corrija ao
> reescrever o README.

### Passo 4 — Criar o repositório e o commit inicial

```bash
cd destino
git init -b main
git add -A
git commit -m "Eleições Dublin 2026: versões finais e o que as reproduz"
```

Repare no `-b main`: o repositório de origem não tem `main`, e a branch padrão
dele é uma branch de trabalho do Claude. Não repita isso.

Crie o repositório **privado** no GitHub e publique. A sessão do Claude pode
usar `mcp__github__create_repository`; se preferir criar pela interface, crie
vazio (sem README, sem .gitignore, sem licença) e só então:

```bash
git remote add origin https://github.com/<dono>/eleicoes-dublin-2026.git
git push -u origin main
```

### Passo 5 — Exportar os artefatos órfãos

**Este é o passo que não pode ser pulado.** Precisa rodar numa sessão logada na
mesma conta que publicou os artefatos.

Para cada linha do manifesto com status `orfao`:

1. Chamar a ferramenta `Artifact` com `action: "read"` e o `url` da linha.
2. A ferramenta grava o HTML completo em disco e informa o caminho — **copiar
   esse arquivo** para `artefatos/<slug>.html`. Não reemitir o HTML pelo
   modelo: são páginas de 50 a 120 KB, e reescrever é como se perde conteúdo.
3. Anotar em `artefatos/README.md`: título, URL, data da versão lida, arquivo.

São dez leituras. Cada uma devolve um trecho grande para o contexto da sessão,
então faça em duas ou três levas, com commit a cada leva. Se a sessão ficar
pesada, abra outra: o manifesto diz o que já foi feito.

Ao fim, `artefatos/README.md` deve ter dez linhas e `artefatos/` dez arquivos.

### Passo 6 — Reescrever o `README.md`

O README atual descreve só a análise de agregações. O do repositório novo é o
índice do projeto inteiro. Deve responder, nesta ordem:

1. **O que está decidido** — as agregações (16.794 eleitores, 51 seções, 28
   urnas) e o desenho da fila do Ring 3 (cenário 3 adaptado, 180 CCBs), com
   link para a folha e para a página das urnas.
2. **O que está aberto** — apontar para `PENDENCIAS.md` e para as quatro
   pendências técnicas registradas na folha do Ring 3 (ancoragem da ponta fixa
   da divisória, largura real do painel entregue, boca real do fundo, e as duas
   premissas por confirmar com o safety officer do RDS).
3. **Como reproduzir** — os quatro comandos do passo 3, sem `cd scripts`.
4. **De onde vêm os dados** — a tabela de proveniência que já está no README
   atual, que é boa e deve ser preservada.
5. **O que é `artefatos/`** — cópia de leitura de páginas que vivem no
   claude.ai; a fonte de verdade de cada uma é o URL, não o arquivo.

### Passo 7 — Fechar a origem

Depende da decisão 3.5. Se for arquivar: mesclar o PR #25, acrescentar ao
`README.md` da origem uma linha apontando para o repositório novo, e arquivar
em Settings → Archive this repository.

---

## 6. Critérios de aceite

A migração está feita quando **todos** passam:

| # | Verificação | Como |
|---|---|---|
| 1 | Os quatro geradores rodam sem erro de qualquer cwd | `cd /tmp && python3 <repo>/scripts/mapa_agregacoes.py` |
| 2 | As saídas regeneradas são idênticas às migradas | rodar os quatro geradores e conferir que `git status saidas/` só acusa o `.xlsx` — ver nota abaixo |
| 3 | A conta do Ring 3 fecha | `python3 scripts/ring3_montagem.py` imprime `CCB: 180` e `compra 0 \| sobra 20` |
| 4 | A análise das seções fecha | `mapa_agregacoes.py` completa; as validações internas conferem 16.794 eleitores por três caminhos e 28 urnas |
| 5 | `artefatos/` tem dez arquivos e dez linhas no seu README | contagem |
| 6 | Nenhum nome de arquivo com espaço ou acento fora de `data/raw/` | `git ls-files \| grep -P '[ áàâãéêíóôõúçÁÀÂÃÉÊÍÓÔÕÚÇ]'` — só as três linhas de `data/raw/` devem aparecer |
| 7 | O repositório é privado | conferir no GitHub |
| 8 | A branch padrão é `main` | conferir no GitHub |

O critério 2 é o que prova que a migração não corrompeu nada: se o HTML
regenerado bate byte a byte com o que veio junto, a cadeia dado → script →
saída sobreviveu à mudança de repositório.

**Os oito critérios foram executados neste repositório em 16/09/2026**, com
`pandas` 3.0.5 e `openpyxl`, e o resultado é a linha de base do destino:

- os quatro geradores rodam de `/tmp` sem erro;
- `dados.json`, `dublin_agregacoes.html`, `ring3_montagem.html` e
  `ring3_planta.svg` são reproduzidos **byte a byte**;
- `Dublin_2026_agregacoes.xlsx` **nunca** é byte a byte, e isso é esperado: o
  formato grava data de criação dentro do arquivo, então cada execução produz
  bytes diferentes com o mesmo conteúdo. Não trate isso como falha e não
  commite o `.xlsx` regenerado só porque `git status` o acusa — compare abas e
  totais, não bytes;
- `ring3_montagem.py` imprime `CCB: 180` e `compra 0 | sobra 20`;
- `mapa_agregacoes.py` completa com as validações internas passando.

---

## 7. O que deliberadamente não vai

| Item | Por quê |
|---|---|
| História do git da origem | 7 commits, boa parte `Add files via upload`; o repositório antigo fica como arquivo |
| Branch `claude/dublin-electoral-sections-3odh1w` | subconjunto estrito da outra |
| Artefato "Ring 3, cenários de fila" | superado pela "Montagem do Ring 3"; migrar os dois como finais cria dois desenhos concorrentes do mesmo objeto |
| Artefato "Teses Temáticas" | outro projeto |
| `scripts/salao.py`, `scripts/ring3.py` | não existem — nunca foram commitados e não são recuperáveis |

---

## 8. Armadilhas

**Renomear os arquivos de `data/raw/`.** `parse_dados.py` abre
`eleitorado_local_votacao_2026_ZZ.csv` e `Filtrado_Dublin.csv` pelo nome
literal. Renomear parece arrumação e é quebra.

**Reorganizar pastas na mesma passada.** Os scripts dependem de
`parent.parent`. Mover `scripts/` para dentro de um subdiretório muda a raiz
calculada e as saídas vão parar no lugar errado — sem erro, o que é pior.

**Republicar artefato sem `url`.** Cria um segundo artefato com o mesmo título.
Depois de algumas semanas ninguém sabe qual dos dois é o bom.

**Achar que copiar o HTML migrou o artefato.** O artefato continua no
claude.ai, com o URL e as permissões dele. O arquivo no repositório é cópia de
leitura.

**Confiar na data para decidir o que está superado.** Vale para os três itens
da decisão 3.3 — abra e confira.

**Encoding.** Os dois CSVs estão em `latin-1`, separados por `;`, e o
`Filtrado_Dublin.csv` vem com a linha inteira entre aspas e as aspas internas
duplicadas. `parse_dados.py` já trata isso. Se alguma ferramenta de migração
"normalizar" os arquivos para UTF-8, a carga quebra.

---

## 9. Sobre os dados pessoais

Os dois CSVs são dados abertos do TSE e **não contêm eleitores nominalmente
identificados**: são contagens por seção. O `Filtrado_Dublin.csv` traz recortes
demográficos agregados (gênero, faixa etária, escolaridade, raça/cor,
identidade de gênero) por seção e local de votação.

Ainda assim o repositório novo deve ser privado, por outro motivo: ele reúne
planta do salão, desenho de barreiras, dimensionamento de staff e orçamento de
um local de votação com data e horário públicos.
