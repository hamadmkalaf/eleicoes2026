# Cenários salvos da prancheta do Hall 2

Cada arquivo `.json` nesta pasta é um cenário salvo pela Prancheta do Hall 2
(`saidas/editor.html`, gerada por `scripts/gera_editor.py` a partir de
`scripts/editor_template.html`). Este branch existe só para guardar esses
arquivos; o código do desenho de fluxo vive em `deisgn-fluxo`.

## Como um arquivo chega aqui

A prancheta não grava neste branch sozinha — ela não pode fazer chamadas de
rede fora do claude.ai. Quem desenha clica em **Copiar cenário**, que copia
o JSON para a área de transferência, e manda esse texto (mensagem, e-mail,
colado numa conversa com o Claude) para quem publica a prancheta. Essa
pessoa grava o arquivo com:

```bash
python3 scripts/salva_cenario.py arquivo.json   # ou "-" para ler da entrada padrão
```

O script valida o formato, monta o nome do arquivo a partir do `nome` do
cenário e grava neste branch sem tocar no checkout local (usa um worktree
temporário). Também dá para criar o arquivo à mão, seguindo o formato
abaixo.

(Uma primeira versão deste fluxo tentava abrir o GitHub com o commit
pronto para a própria pessoa confirmar. Foi abandonada: exige conta no
GitHub e um clique final numa página externa que nem sempre acontece, e a
prancheta não tem como saber se aconteceu.)

## Formato

```json
{
  "nome": "nome do cenário",
  "base": "A",
  "alteracoes": [
    {"n": 9, "x": 44.9, "y": 39.9, "rot": 180, "lado": 1}
  ],
  "medidas": [{"a": [10.0, 5.0], "b": [10.0, 8.0]}],
  "criadoEm": "2026-09-03T12:00:00.000Z"
}
```

`alteracoes` lista só as mesas (por número `n`, 1 a 28) que saíram da posição
original do cenário `base` ("A" ou "B") — não as 28. Isso mantém os arquivos
pequenos e os diffs do git legíveis: dá para ver de relance o que cada
cenário muda. Reabrir um cenário aplica essas mudanças em cima da planta
oficial vigente; se a planta oficial mudar depois, as mesas não citadas em
`alteracoes` acompanham a mudança.

## Como um arquivo aparece na prancheta

A lista de cenários é embutida **na hora de gerar e publicar** a prancheta
(`scripts/gera_editor.py` lê os arquivos deste branch e grava a lista em
`saidas/editor_dados.json`). Não é leitura ao vivo — a sandbox do artefato
publicado bloqueia chamadas de rede para fora do próprio claude.ai. Depois
de gravar um cenário novo com `salva_cenario.py`, é preciso gerar e
publicar a prancheta de novo para ele aparecer na lista de todo mundo.
