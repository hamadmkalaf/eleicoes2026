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

## Conferir um cenário fora do navegador

A planta em si — salão, módulo, portas e os cenários-base A e B — está em
`data/prancheta_hall2.json`, a mesma geometria que `saidas/editor_dados.json`
carrega (conferido na consolidação de 06/09/2026; o PR #7 trazia uma cópia
idêntica como `cenarios/planta_hall2.json`, retirada daqui para não ser lida
como cenário pela biblioteca). `x`/`y` em metros, na ancoragem do módulo (o
ponto onde ele encosta na parede), com x para leste e y para norte. `rot` é o
giro do módulo e `lado` diz de que lado ficam as cadeiras dos mesários.

Para conferir um cenário:

```bash
python3 scripts/folgas_prancheta.py cenarios/tres-polos-20260905-182000.json
```

O script mede, mesa a mesa, a **folga lateral** (espaço livre de cada lado do
módulo, ao longo da parede) e a **fila** (profundidade livre à frente da mesa
dos mesários, onde os eleitores se enfileiram), e compara com a planta original.

## `tres-polos-20260905-182000.json` — Três polos · 22/23/24 separadas

Espalha as três mesas de maior movimento — **22, 23 e 24** — em três áreas
distintas do salão, cada uma com corredor próprio dos dois lados, em vez de
mantê-las encostadas no canto sudoeste.

| Mesa | Vai para | Lateral | Fila |
|---|---|---|---|
| 22 | parede norte, entre a mesa 8 e a coluna leste | 3,00 → 2,69 m | **0,98 → 20,0 m** |
| 23 | fachada leste, extremo sul | **0,98 → 2,70 m** | 20,0 m |
| 24 | parede oeste, no trecho vazio ao sul da porta O2 | **2,48 → 5,71 m** | 20,0 m |

Na planta original a 22 e a 23 se estorvam: a fila da 22 caminha para o norte e
bate no módulo da 23 depois de 0,98 m, e o mesmo encontro deixa a 23 com apenas
0,98 m de folga lateral. São as duas piores medidas do salão inteiro, e caem
justamente sobre mesas de alto volume.

Para abrir espaço, o cenário move mais 16 mesas em dois blocos rígidos, sem
mexer em nenhum corredor de dupla nem em nenhum recuo de emergência:

- duplas **(5,6)** e **(7,8)** recuam 2,00 m para oeste na parede norte,
  liberando o trecho onde a 22 se instala;
- a coluna leste **(9 a 20)** sobe 2,60 m, abrindo no extremo sul da fachada o
  vão onde a 23 se instala.

A mesa 21, que dividia a borda do recorte com a 22, passa de 3,00 m para 6,90 m
de folga lateral.

**Custo a registrar:** a fila da mesa 9 encurta de 4,29 m para 2,70 m, porque o
módulo da 22 passa a fechar o canto nordeste. É a única piora relevante do
cenário. No conjunto, a pior folga lateral do salão sobe de 0,98 m para 1,16 m e
a pior fila sobe de 0,98 m para 2,70 m.

**Limite encontrado:** a fachada leste não comporta uma mesa isolada com 3,00 m
de corredor dos dois lados. São 12 mesas em 36,3 m de fachada, espremidas entre
o recuo de emergência da porta S7 (que a fila não pode ocupar, ao sul) e a
parede norte. Os 2,70 m da mesa 23 são o máximo disponível sem comprimir os
espaçamentos entre duplas abaixo do padrão da planta.
