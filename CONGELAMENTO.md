# Congelamento — atribuição de seção/porta e posição das mesas

Duas coisas deixam de ser recalculáveis a cada sessão e passam a ser **dado
versionado**: **por qual porta cada seção entra** e **onde cada uma das 28 mesas
fica no Hall 2**. Tudo o mais no projeto continua derivado; estas duas coisas
não, porque a partir delas se imprime sinalização, se convoca mesário, se marca
o piso e se responde ao eleitor — e uma versão diferente circulando é um eleitor
na parede errada no dia 04/10.

O arranjo congelado é o **`paredes-abc-20260915`** (`Paredes_ABC`).

## A regra, em uma linha

**Decisão do Posto de 15/09/2026: cada entrada serve uma parede inteira e só
ela.** Quem entra pela porta vai direto à sua mesa sem atravessar o salão, e a
fila de cada porta é a fila daquela parede.

| Entrada | Porta | Parede | Mesas | Esperados |
|---|---|---|---|---|
| **A** | S4 (RDS 2.5/2.6) | oeste | 9 | 3.834 |
| **B** | S5 (RDS 2.4) | norte | 9 | 3.832 |
| **C** | S6 (RDS 2.2/2.3) | leste | 10 | 3.833 |

51 seções · 28 mesas · 16.794 aptos · 11.499 comparecimentos esperados.
A amplitude entre as três filas é de **2 eleitores**.

`S7` (RDS 2.1) é a **entrada preferencial** — idoso, gestante, pessoa com
deficiência e acompanhante, sem fila, para qualquer uma das três paredes. `S2` e
`S8` são saídas. A parede sul não recebe mesa.

## Duas numerações convivem, de propósito

O **MRV** é a identidade oficial da mesa no DJE/TRE-DF: vale para caderno,
convocação e rádio, e não muda se a mesa for movida. O **número eleitor** é o
que vai na sinalização: começa em 1 na mesa mais ao sul da parede oeste e segue
em sentido horário até 28. Os dois estão congelados, e um não substitui o outro.

## Os arquivos

| Arquivo | O que é |
|---|---|
| `congelado/arranjo.json` | **fonte única de verdade** — salão, portas, zonas livres, serpenteados, as 28 mesas com coordenada em metros, as 51 seções |
| `congelado/atribuicao_secao_porta.csv` | 51 linhas: seção → mesa → parede → entrada → porta. Derivado do JSON |
| `congelado/posicao_mesas.csv` | 28 linhas: MRV, número eleitor, par de seções, aptos, esperados, parede, porta, `x_m`, `y_m`, rotação. Derivado do JSON |
| `congelado/CHECKSUMS.sha256` | SHA-256 dos três acima |
| `scripts/verifica_congelamento.py` | prova que nada se mexeu |

Coordenadas em **metros**, origem no canto sudoeste do Hall 2, `x` para leste e
`y` para norte. O módulo de mesa tem 4,10 m de profundidade por 0,90 m de
largura e encosta a parede em (`x_m`, `y_m`), avançando para dentro do salão no
sentido de `rot_graus`.

**Os mesmos arquivos, byte a byte, estão em `hamadmkalaf/eleicoes2026` e em
`hamadmkalaf/dublineleicoesfinal`.** Se os hashes dos dois repositórios
divergirem, um dos dois está errado — e é isso que os torna comparáveis sem ler
linha por linha.

## Como verificar

```bash
python3 scripts/verifica_congelamento.py    # roda de qualquer diretório, não escreve nada
```

Sai 0 e imprime o resumo do arranjo, ou sai 1 e lista cada divergência. O que ele
confere:

1. os três arquivos batem com `CHECKSUMS.sha256`;
2. os dois CSV são reproduzíveis **byte a byte** a partir do JSON;
3. identidade e totais: `paredes-abc-20260915`, 51 seções, 28 mesas, 16.794
   aptos, 11.499 esperados, número eleitor de 1 a 28 sem buraco;
4. cada seção aponta para uma mesa existente, os aptos da mesa são a soma dos
   aptos das suas seções, e o par declarado na mesa é exatamente o conjunto de
   seções que apontam para ela;
5. cada parede é servida por **uma** entrada, a contagem de mesas e o
   comparecimento esperado de cada entrada batem com a soma das suas mesas, e a
   porta de cada entrada está marcada como `entrada` na lista de portas;
6. geometria: cada mesa está na linha da parede que declara, com a rotação certa;
   a pegada cabe no contorno do salão; não invade o recorte sudoeste, a faixa de
   3 m das saídas de emergência, os recuos de `N2`, `O2`, `S3`, `S7` e `R1`, nem
   a sala de apoio; e duas mesas da mesma parede não se tocam;
7. cada serpenteado reservado está na parede da sua mesa, e a mesa é de carga
   alta;
8. **cruzamento independente:** se `saidas/dados.json` existir, o par
   principal/agregada e os aptos de cada uma das 28 mesas são conferidos contra a
   análise das agregações do TSE. Dois caminhos, mesmos números.

## Como descongelar

Mexer no arranjo é ato deliberado, não efeito colateral. Para mudar:

1. edite **só** `congelado/arranjo.json`;
2. troque `cenario.id` por um identificador novo (`paredes-abc-AAAAMMDD`), e
   ajuste `ARRANJO_ESPERADO` no verificador;
3. regenere os dois CSV e o `CHECKSUMS.sha256` — o verificador diz exatamente
   qual arquivo deixou de bater;
4. rode `python3 scripts/verifica_congelamento.py` até sair 0;
5. **propague para o outro repositório na mesma leva**, e confira que os hashes
   dos dois coincidem;
6. registre aqui o que mudou, por quê, e quem decidiu;
7. republique os artefatos afetados **no mesmo URL** (parâmetro `url` da
   ferramenta `Artifact`) — republicar sem `url` cria um segundo artefato com o
   mesmo título, e ninguém sabe depois qual é o bom.

## Procedência

O arranjo vem do artefato **Prancheta pelas Seções**
(<https://claude.ai/artifact/Szv5egKpHy3umh4udAybvr>, versão de 16/09/2026),
gerado por `scripts/gera_prancheta_por_secao.py` — script que **nunca foi
commitado** e não está em nenhum dos dois repositórios. Por isso o dado foi
extraído do artefato e congelado como dado, e não como saída de gerador: não há
gerador para rodar.

A geometria do salão e das portas vem de `referencias/rds-hall2-planta.pdf` (o
`RDS_Hall_2_Floorplan_(1).pdf` recebido do local), e a agregação de seções, dos
três PDFs do Cartório Eleitoral, conferida em
`CONFERENCIA_PRANCHETA_2026-09-15.md` — documento citado pelo artefato e também
ausente dos repositórios.

O comparecimento esperado é **estimativa, não número oficial do TSE**: aplica a
taxa de comparecimento de 2022 do condado onde o eleitor mora aos aptos de 2026
(base B). Os **aptos** são oficiais; os **esperados**, não. As larguras de fila e
a classificação de carga das mesas dependem dessa estimativa.

## Conflito conhecido, deixado de pé de propósito

`scripts/ring3_montagem.py` carrega **outra** atribuição de porta: `esp = {'A':
3642, 'B': 4215, 'C': 3642}`, da decisão do Posto de 06/09/2026, quando as três
entradas alimentavam o Ring 3 e cada uma se espalhava pelas três paredes. **Esse
arranjo foi abandonado** — com ele a entrada B levava 573 eleitores a mais que as
outras duas; a regra geográfica de 15/09 derrubou a diferença para 2.

O script **não foi alterado**. Ele é o gerador fiel da folha de montagem do Ring
3 e da planta `saidas/ring3_planta.svg`, e mudar a constante mudaria as saídas
sem que ninguém tivesse decidido isso. O que vale para o dia da eleição é o que
está em `congelado/`; o Ring 3 é contingência, e quando for retomado é a
atribuição congelada que deve descer para ele — não o contrário.
