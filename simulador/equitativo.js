/* Constrói o arranjo "Equitativo": reparto equilibrado entre as três entradas
 * sob a regra de parede, com uma mesa vermelha por parede/porta, as demais em
 * duplas e as vermelhas isoladas.
 *
 * Convenções geométricas lidas da planta oficial A:
 *   - dupla  = dois módulos a 3,9 m, o primeiro com lado +1 e o segundo com
 *              lado -1, de modo que as cadeiras dos mesários fiquem voltadas
 *              uma para a outra no vão interno (1,6 m entre os assentos);
 *   - entre unidades (duplas ou isoladas) = 2,4 m de centro a centro, ou seja
 *              1,5 m livres de corpo a corpo, o mesmo que a planta A usa entre
 *              as mesas 6 e 7.
 *
 * Eixos e sentidos por parede (conferidos contra a planta A):
 *   norte  rot 270, eixo x crescente,  dupla (x, +1) e (x+3,9, -1)
 *   leste  rot 180, eixo y decrescente, dupla (y, +1) e (y-3,9, -1)
 *   oeste  rot   0, eixo y crescente,  dupla (y, +1) e (y+3,9, -1)
 */
const {BASE, MRVS, DECISOES} = require("./dados.js");
const M = require("./modelo.js");

const ESPERADO = {}, CLASSE = {};
for (const m of DECISOES.mesas) { ESPERADO[m.mrv] = m.esperado; CLASSE[m.mrv] = m.classe; }
const VERMELHAS = DECISOES.mesas.filter(m => m.classe === "alta").map(m => m.mrv).sort((a, b) => a - b);
const OUTRAS = DECISOES.mesas.map(m => m.mrv).filter(n => !VERMELHAS.includes(n)).sort((a, b) => a - b);
const TOTAL = DECISOES.mesas.reduce((s, m) => s + m.esperado, 0);

const PASSO_DUPLA = 3.9;   // dentro da dupla
const PASSO_UNID = 2.4;    // entre unidades (corpo a corpo 1,5 m)
const MEIO = 0.45;         // meia largura do corpo

/* Trechos livres do eixo de cada parede, em coordenada do ponto de encosto da
 * mesa. Descontam meia largura do corpo, os vãos de porta e a faixa protegida
 * da fachada leste, e ainda reservam os DOIS CANTOS usados — que é onde a
 * primeira tentativa quebrou:
 *
 *   canto noroeste: a fila de uma mesa da parede oeste é um segmento
 *     horizontal que avança até x = 4,4 + L·0,6 (9,2 m na fila mais longa).
 *     Por isso a parede norte só começa em x = 10,2 (corpo a partir de 9,75).
 *   canto nordeste: a fila de uma mesa da parede leste avança até
 *     x = 42,9 − L·0,6 e cortaria o corpo das mesas do norte. Por isso a
 *     parede leste para em y = 39,5 (corpo até 39,95), abaixo dos corpos do
 *     norte, que começam em y = 40,3; e a parede norte para em x = 42,3
 *     (corpo até 42,75), a oeste dos corpos do leste, que começam em 43,2.
 *
 * O recorte sudoeste ficou de fora de propósito: a fila de uma mesa ali corta
 * o corpo da primeira mesa da parede oeste — é o conflito que a própria
 * planta oficial A carrega entre as mesas 22 e 23. */
const PAREDES = {
  norte: {rot: 270, eixo: "x", fixo: 44.4, sentido: +1,
          trechos: [[10.20, 20.21], [24.67, 42.30]]},
  leste: {rot: 180, eixo: "y", fixo: 47.3, sentido: -1,
          trechos: [[3.20, 39.50]]},
  oeste: {rot: 0, eixo: "y", fixo: 0.0, sentido: +1,
          trechos: [[7.45, 18.81], [22.98, 36.25], [39.05, 43.95]]},
};
const ENTRADA = {oeste: "A", norte: "B", leste: "C"};

/* Quantas unidades cabem: devolve o número máximo de duplas e de isoladas por
 * trecho, para saber de antemão se um plano de composição é viável. */
function cabeNoTrecho(span, duplas, isoladas) {
  const n = duplas + isoladas;
  if (n === 0) return true;
  const largura = duplas * PASSO_DUPLA + (n - 1) * PASSO_UNID;
  return largura <= span + 1e-9;
}

/* Distribui as unidades de uma parede pelos seus trechos, do maior para o
 * menor, e devolve as posições. `unidades` é uma lista de {tipo, mrvs}. */
function distribuiPorTrechos(parede, unidades) {
  const trechos = PAREDES[parede].trechos.map((t, i) => ({i, ini: t[0], fim: t[1], span: t[1] - t[0], u: []}));
  // empacotamento simples: percorre as unidades (duplas primeiro, que são
  // maiores) e põe cada uma no trecho com mais folga que ainda a comporte
  const ordem = unidades.slice().sort((a, b) => (b.tipo === "dupla") - (a.tipo === "dupla"));
  for (const u of ordem) {
    let melhor = null;
    for (const t of trechos) {
      const d = t.u.filter(x => x.tipo === "dupla").length + (u.tipo === "dupla" ? 1 : 0);
      const iso = t.u.filter(x => x.tipo === "isolada").length + (u.tipo === "isolada" ? 1 : 0);
      if (!cabeNoTrecho(t.span, d, iso)) continue;
      const usado = d * PASSO_DUPLA + (d + iso - 1) * PASSO_UNID;
      const folga = t.span - usado;
      // Uma isolada prefere um trecho que já tem duplas a abrir um trecho
      // vazio: sozinha num trecho de ponta, a mesa vermelha fica no canto do
      // salão, com o maior percurso do checkpoint até ela — justamente a mesa
      // que menos pode ficar sem alimentação.
      const abreVazio = u.tipo === "isolada" && t.u.length === 0 ? 1 : 0;
      const chave = [abreVazio, -folga];
      if (!melhor || chave[0] < melhor.chave[0]
          || (chave[0] === melhor.chave[0] && chave[1] < melhor.chave[1])) melhor = {t, folga, chave};
    }
    if (!melhor) return null;                 // não coube: plano inviável
    melhor.t.u.push(u);
  }
  return trechos;
}

/* Converte os trechos preenchidos em posições de mesa. Dentro do trecho as
 * unidades ficam distribuídas com a folga repartida igualmente entre os vãos,
 * para ninguém ficar espremido contra um vão de porta. As posições saem num
 * eixo local crescente e, nas paredes de sentido -1 (leste), são espelhadas
 * no fim — assim a dupla desce em y com o lado +1 no alto, como na planta A. */
function posicoesDaParede(parede, trechos) {
  const P = PAREDES[parede], out = [];
  for (const t of trechos) {
    if (!t.u.length) continue;
    const nd = t.u.filter(x => x.tipo === "dupla").length, n = t.u.length;
    const usado = nd * PASSO_DUPLA + (n - 1) * PASSO_UNID;
    const folga = Math.max(0, t.span - usado);
    // A folga do trecho vira respiro entre as unidades, mas com teto: sem ele
    // a última unidade é empurrada contra a borda do trecho, que é justamente
    // um vão de porta. Com teto, o bloco fica centrado e sobra recuo dos dois
    // lados — importante para a vermelha isolada, que não deve encostar no vão
    // de serviço N2.
    // Teto de 0,6 m: o vão entre unidades fica entre 2,4 e 3,0 m — o corredor
    // que o módulo prevê — e nunca chega aos 3,9 m que separam as duas mesas
    // DENTRO de uma dupla. Sem esse teto a folga espalhada deixava a parede
    // num pente uniforme de 3,9 m e a leitura das duplas sumia.
    const extra = n > 1 ? Math.min(folga / (n - 1), 0.6) : 0;
    const bloco = usado + (n - 1) * extra;
    let cur = t.ini + (t.span - bloco) / 2;
    // As isoladas entram intercaladas entre as duplas, nunca uma ao lado da
    // outra: duas isoladas vizinhas se leem como uma dupla de cadeiras
    // trocadas, que é o oposto do que a regra quer mostrar.
    const iso = t.u.filter(u => u.tipo === "isolada"), dup = t.u.filter(u => u.tipo === "dupla");
    const seq = [];
    if (!iso.length) seq.push(...dup);
    else {
      const cortes = iso.map((_, k) => Math.round((k + 1) * dup.length / (iso.length + 1)));
      let d = 0;
      for (let k = 0; k < iso.length; k++) {
        while (d < cortes[k]) seq.push(dup[d++]);
        seq.push(iso[k]);
      }
      while (d < dup.length) seq.push(dup[d++]);
    }
    for (let k = 0; k < seq.length; k++) {
      const u = seq[k];
      if (u.tipo === "dupla") {
        out.push({n: u.mrvs[0], u: cur, lado: 1});
        out.push({n: u.mrvs[1], u: cur + PASSO_DUPLA, lado: -1});
        cur += PASSO_DUPLA;
      } else {
        out.push({n: u.mrvs[0], u: cur, lado: 1});
      }
      cur += PASSO_UNID + extra;
    }
  }
  const todos = P.trechos.flat();
  const espelho = Math.min(...todos) + Math.max(...todos);
  return out.map(o => {
    const c = +(P.sentido > 0 ? o.u : espelho - o.u).toFixed(2);
    return P.eixo === "x"
      ? {n: o.n, x: c, y: P.fixo, rot: P.rot, lado: o.lado}
      : {n: o.n, x: P.fixo, y: c, rot: P.rot, lado: o.lado};
  });
}

/* ---------- 1. composição: que MRV vai para que parede ---------- */
/* Alvo: somas iguais. Cada parede leva uma vermelha isolada; das 25 restantes,
 * 24 formam 12 duplas e sobra UMA, que fica isolada — 25 é ímpar, não há
 * arranjo em que todas as não-vermelhas estejam em duplas. */
function melhorComposicao(iteracoes = 400000, semente = 20261004) {
  let rnd = semente;
  const rand = () => (rnd = (rnd * 1103515245 + 12345) & 0x7fffffff) / 0x7fffffff;
  const tamanhos = [9, 8, 8];                 // não-vermelhas por parede
  let melhor = null;
  for (let it = 0; it < iteracoes / 1000; it++) {
    // partida aleatória
    const baralho = OUTRAS.slice();
    for (let i = baralho.length - 1; i > 0; i--) { const j = Math.floor(rand() * (i + 1)); [baralho[i], baralho[j]] = [baralho[j], baralho[i]]; }
    const g = [baralho.slice(0, 9), baralho.slice(9, 17), baralho.slice(17, 25)];
    const soma = k => g[k].reduce((s, n) => s + ESPERADO[n], 0);
    const custo = () => { const s = [0, 1, 2].map(soma); return Math.max(...s) - Math.min(...s); };
    let c = custo();
    // busca local: troca pares entre grupos enquanto melhorar
    for (let passo = 0; passo < 1000; passo++) {
      let melhorou = false;
      for (let a = 0; a < 3 && !melhorou; a++) for (let b = a + 1; b < 3 && !melhorou; b++)
        for (let i = 0; i < g[a].length && !melhorou; i++) for (let j = 0; j < g[b].length && !melhorou; j++) {
          [g[a][i], g[b][j]] = [g[b][j], g[a][i]];
          const nc = custo();
          if (nc < c - 1e-9) { c = nc; melhorou = true; } else { [g[a][i], g[b][j]] = [g[b][j], g[a][i]]; }
        }
      if (!melhorou) break;
    }
    if (!melhor || c < melhor.custo) melhor = {custo: c, grupos: g.map(x => x.slice())};
    if (melhor.custo === 0) break;
  }
  return melhor;
}

/* ---------- 2. monta o arranjo completo ---------- */
function montaEquitativo(grupos, mapaParede, mapaVermelha, ondeSobra) {
  const alteracoes = [];
  const relatorio = {};
  for (let k = 0; k < 3; k++) {
    const parede = mapaParede[k];
    const vermelha = mapaVermelha[k];
    const naoVermelhas = grupos[k].slice().sort((a, b) => a - b);
    const unidades = [{tipo: "isolada", mrvs: [vermelha]}];
    let resto = naoVermelhas.slice();
    if (parede === ondeSobra) {
      // a mesa que sobra do total ímpar: fica isolada, e escolhemos a de menor
      // comparecimento da parede, que é a que menos precisa de vizinha
      const sobra = resto.reduce((a, b) => ESPERADO[b] < ESPERADO[a] ? b : a);
      resto = resto.filter(n => n !== sobra);
      unidades.push({tipo: "isolada", mrvs: [sobra], sobra: true});
    }
    for (let i = 0; i < resto.length; i += 2) unidades.push({tipo: "dupla", mrvs: [resto[i], resto[i + 1]]});
    const trechos = distribuiPorTrechos(parede, unidades);
    if (!trechos) return null;
    const pos = posicoesDaParede(parede, trechos);
    alteracoes.push(...pos);
    relatorio[parede] = {
      entrada: ENTRADA[parede], vermelha, mesas: [vermelha, ...naoVermelhas].sort((a, b) => a - b),
      esperado: [vermelha, ...naoVermelhas].reduce((s, n) => s + ESPERADO[n], 0),
      duplas: unidades.filter(u => u.tipo === "dupla").map(u => u.mrvs),
      isoladas: unidades.filter(u => u.tipo === "isolada").map(u => ({mrv: u.mrvs[0], motivo: u.sobra ? "sobra do total ímpar" : "vermelha"})),
    };
  }
  alteracoes.sort((a, b) => a.n - b.n);
  return {alteracoes, relatorio};
}

module.exports = {ESPERADO, CLASSE, VERMELHAS, OUTRAS, TOTAL, PAREDES, ENTRADA,
                  melhorComposicao, montaEquitativo, distribuiPorTrechos, posicoesDaParede};

if (require.main === module) {
  const comp = melhorComposicao();
  console.log("Partição das 25 não-vermelhas (custo = maior − menor):", comp.custo);
  comp.grupos.forEach((g, i) => console.log(`  grupo ${i} (${g.length}): ${g.join(", ")} = ${g.reduce((s, n) => s + ESPERADO[n], 0)}`));
}

/* --------------------------------------------------------------- */
/* Execução: compõe, monta, confere geometria e simula.              */
/* --------------------------------------------------------------- */
function construir() {
  const comp = melhorComposicao();
  // Grupos: o de 9 não-vermelhas (10 mesas com a vermelha) vai para a parede
  // leste, o trecho contínuo mais longo. As vermelhas ficam onde a decisão de
  // 06/09 já as tinha posto por entrada: 24 na A, 22 na B, 23 na C.
  const g = comp.grupos.slice().sort((a, b) => b.length - a.length);   // [9, 8, 8]
  const plano = [
    {parede: "leste", vermelha: 23, grupo: g[0]},
    {parede: "oeste", vermelha: 24, grupo: g[1]},
    {parede: "norte", vermelha: 22, grupo: g[2]},
  ];
  const r = montaEquitativo(plano.map(p => p.grupo), plano.map(p => p.parede),
                            plano.map(p => p.vermelha), "leste");
  if (!r) throw new Error("composição não coube nas paredes");
  return {...r, custoParticao: comp.custo};
}
module.exports.construir = construir;

/* O arranjo pronto, no formato que a prancheta grava e o simulador lê. */
function arranjoEquitativo() {
  const r = construir();
  return {nome: "Equitativo", base: "A", alteracoes: r.alteracoes,
          criadoEm: "2026-10-04T00:00:00.000Z", id: "equitativo-20261004-000000"};
}
module.exports.arranjoEquitativo = arranjoEquitativo;
