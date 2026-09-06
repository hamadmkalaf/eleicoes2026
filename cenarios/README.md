# Cenários salvos da prancheta do Hall 2

Cada arquivo `.json` desta pasta é um cenário salvo pela Prancheta do Hall 2
(`saidas/editor.html`, gerada por `scripts/gera_editor.py` a partir de
`scripts/editor_template.html`). É a **biblioteca publicada**: a lista que
tanto a prancheta quanto o simulador de fluxo embutem ao serem gerados, e
que todo mundo que abre as duas páginas vê.

## Uma pasta, duas páginas

Quem lê esta pasta é `scripts/cenarios.py`, e é o único que lê:
`gera_editor.py` (prancheta) e `gera_simulador.py` (simulador) chamam
`cenarios.carrega()`. Antes cada gerador tinha a sua cópia da leitura e as
duas olhavam só o branch de dados `cenarios-hall2` — dois cenários acabaram
num branch de trabalho, e o simulador publicado ficou com dois arranjos
enquanto a prancheta mostrava quatro. A lista dupla não volta a acontecer se
todo cenário entrar por aqui.

`cenarios.carrega()` junta duas origens pelo nome do arquivo (o `id`):

1. **esta pasta**, versionada junto com o código — é o que garante a mesma
   lista mesmo sem rede;
2. **`cenarios/` no branch `cenarios-hall2`**, onde `salva_cenario.py` grava
   sem tocar em código. Em colisão de `id`, esta origem vence, por ser o
   alvo das gravações novas.

## Como um cenário chega até aqui

A prancheta não grava sozinha em lugar nenhum — a sandbox do artefato
publicado bloqueia chamadas de rede para fora do claude.ai. O caminho tem
três degraus, e os dois primeiros não dependem de ninguém:

1. **Salvar**, na prancheta, guarda o cenário no `localStorage` daquele
   navegador e copia o JSON. O cenário fica na lista, marcado *neste
   navegador*, e sobrevive a recarregar a página. **Apagar** o remove de
   vez; um cenário da biblioteca publicada só pode ser **ocultado** ali,
   porque tirá-lo de todo mundo é republicar a página.
2. **Copiar tudo p/ o simulador** põe a biblioteca inteira num JSON só.
   No simulador, `Carregar arranjo… › colar` aceita a lista de uma vez e
   guarda tudo no navegador de lá. É o caminho para levar cenário novo de
   uma página à outra sem esperar republicação. (Não há botão de baixar
   arquivo: a sandbox do artefato torna inerte qualquer download que a
   própria página dispare, e a capacidade que faria isso é recusada em
   artefato compartilhado por link — que é como a prancheta precisa ficar.
   O `Escolher arquivo…` do simulador continua servindo para os `.json`
   desta pasta.)
3. Para o cenário entrar na **lista publicada**, que todo mundo vê, o JSON
   vai para quem publica a prancheta (mensagem, e-mail, colado numa conversa
   com o Claude), que roda:

```bash
python3 scripts/salva_cenario.py arquivo.json   # ou "-" para ler da entrada padrão
```

O script valida o formato, monta o nome do arquivo a partir do `nome` do
cenário e grava no branch `cenarios-hall2` sem tocar no checkout local (usa
um worktree temporário). Depois disso é preciso rodar `gera_editor.py` e
`gera_simulador.py` e republicar as duas páginas. Também dá para criar o
arquivo à mão nesta pasta, seguindo o formato abaixo.

(Uma primeira versão deste fluxo tentava abrir o GitHub com o commit pronto
para a própria pessoa confirmar. Foi abandonada: exige conta no GitHub e um
clique final numa página externa que nem sempre acontece, e a prancheta não
tem como saber se aconteceu.)

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

`medidas` só serve à prancheta (são as medições de fita guardadas com o
desenho); o simulador as descarta ao embutir a lista.

## O que está aqui

| Arquivo | Cenário | Mesas fora do lugar |
|---|---|---|
| `hamad-3polos-20260905-184518.json` | Hamad_3polos | 28 |
| `tres-polos-20260905-182000.json` | Três polos · 22/23/24 separadas | 19 |
| `hamad-2-20260905-160048.json` | Hamad 2 | 6 |
| `hamad1-20260905-155811.json` | Hamad1 | 6 |
