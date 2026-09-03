# Cenários salvos da prancheta do Hall 2

Cada arquivo `.json` nesta pasta é um cenário salvo pela Prancheta do Hall 2
(`saidas/editor.html`, gerada por `scripts/gera_editor.py` a partir de
`scripts/editor_template.html`). Este branch existe só para guardar esses
arquivos; o código do desenho de fluxo vive em `deisgn-fluxo`.

## Como um arquivo chega aqui

Pelo botão **Salvar** da prancheta, que abre o GitHub com o commit pronto
para confirmar (ou, sem permissão de escrita, para abrir um PR por fork).
Também dá para criar o arquivo à mão, seguindo o formato abaixo.

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
de salvar um cenário novo, é preciso gerar e publicar a prancheta de novo
para ele aparecer na lista de todo mundo.
