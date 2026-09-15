/* Testa a geometria nova da prancheta fora do navegador.
 *
 * Recorta de scripts/editor_template.html os blocos que so dependem de
 * numeros -- a geometria do modulo, a parede de encosto e o pareamento -- e
 * roda contra os dados de verdade (saidas/editor_dados.json). Assim o
 * alinhamento e a conferencia de pares tem prova antes de a pagina subir; o
 * resto do arquivo mexe em DOM e fica de fora.
 *
 * Uso: node scripts/teste_prancheta.js
 */
"use strict";
const fs = require("fs");
const path = require("path");

const RAIZ = path.dirname(__dirname);
const modelo = fs.readFileSync(path.join(RAIZ, "scripts", "editor_template.html"), "utf8");
const D = JSON.parse(fs.readFileSync(path.join(RAIZ, "saidas", "editor_dados.json"), "utf8"));

function recorta(de, ate) {
  const i = modelo.indexOf(de), j = modelo.indexOf(ate);
  if (i < 0 || j < 0 || j <= i) throw new Error("nao achei o bloco " + de);
  return modelo.slice(i, j);
}

/* O ambiente minimo que os dois blocos esperam: a folha da prancheta guarda
   estado em variaveis de modulo e chama o historico, que aqui nao existe. */
const fonte = `
  const M = D.modulo, SAL = D.salao;
  const ALT = SAL.altura, LARG = SAL.largura;
  let mrvs = [], selecao = new Set();
  const instantanea = () => JSON.stringify(mrvs);
  const registra = () => {}, rascunho = () => {};
  ${recorta("const fx = v => v;", "/* --- estado ---")}
  ${recorta("/* --- parede de encosto ---", "/* --- reparear ---")}
  return {
    set mesas(v) { mrvs = v; }, get mesas() { return mrvs; },
    set marcadas(v) { selecao = v; },
    paredeDe, distanciaDeEncosto, poeDistancia, naParede, alinhaParede,
    pares, corpoRect, M, SAL,
  };
`;
const P = new Function("D", fonte)(D);

/* ------------------------------------------------------------------ */
let falhas = 0, testes = 0;
function ok(cond, o_que) {
  testes++;
  if (!cond) { falhas++; console.error("  FALHOU:", o_que); }
}
function quase(a, b, o_que, tol = 1e-6) {
  ok(Math.abs(a - b) <= tol, `${o_que} — esperava ${b}, veio ${a}`);
}
function bloco(titulo, fn) { console.log("\n" + titulo); fn(); }

const planta = cen => D.cenarios[cen].mrvs.map(m => ({...m}));
function comAlteracoes(cen) {
  const ms = planta(cen.base);
  for (const a of cen.alteracoes || []) Object.assign(ms.find(m => m.n === a.n), a);
  return ms;
}
const salvos = D.cenariosSalvos || [];
const acha = nome => {
  const c = salvos.find(s => s.nome === nome);
  if (!c) throw new Error("cenario ausente em editor_dados.json: " + nome);
  return c;
};

/* --- 1. a parede sai do giro, e bate com a face de origem ------------- */
bloco("parede de encosto", () => {
  const esperado = {norte: "N", leste_recuada: "L", oeste: "O", recorte_h: "S"};
  for (const cen of ["A", "B"]) {
    P.mesas = planta(cen);
    for (const m of P.mesas)
      ok(P.paredeDe(m) === esperado[m.origem],
         `planta ${cen}, mesa ${m.n} (${m.origem}): parede ${P.paredeDe(m)}`);
  }
  // na planta original so a fileira leste esta recuada, e esta nos 3 m do recuo
  P.mesas = planta("A");
  for (const m of P.mesas)
    quase(P.distanciaDeEncosto(m), m.origem === "leste_recuada" ? 3.0 : 0.0,
          `planta A, mesa ${m.n}: recuo`);
  // as duas do recorte medem ate a quina do recorte, nao ate a parede sul
  const m21 = P.mesas.find(m => m.n === 21);
  ok(m21.y === D.salao.recorte[3], "mesa 21 ancorada na quina do recorte");
  quase(P.distanciaDeEncosto(m21), 0, "mesa 21: recuo do recorte");
});

/* --- 2. poeDistancia e o inverso de distanciaDeEncosto ---------------- */
bloco("poeDistancia devolve a distancia pedida", () => {
  for (const d of [0, 0.35, 1.5, 3.0]) {
    P.mesas = planta("A");
    for (const m of P.mesas) {
      const antes = {rot: m.rot, lado: m.lado};
      P.poeDistancia(m, d);
      quase(P.distanciaDeEncosto(m), d, `mesa ${m.n} a ${d} m`, 1e-3);
      ok(m.rot === antes.rot && m.lado === antes.lado,
         `mesa ${m.n}: alinhar nao mexe em giro nem lado`);
    }
  }
});

/* --- 3. alinhar uma parede mexe so nela, e so no eixo dela ------------ */
bloco("alinhar a parede", () => {
  const cen = acha("Hamad_3polos");
  P.mesas = comAlteracoes(cen);
  const oeste = P.naParede("O").map(m => m.n).sort((a, b) => a - b);
  ok(oeste.length === 9, `oeste tem 9 mesas no Hamad_3polos, veio ${oeste.length}`);
  const espalhadas = P.naParede("O").map(P.distanciaDeEncosto);
  ok(Math.max(...espalhadas) - Math.min(...espalhadas) > 0.5,
     "o cenario de teste tem mesmo a parede oeste desalinhada");

  const antes = new Map(P.mesas.map(m => [m.n, {...m}]));
  const mexidas = P.alinhaParede("O", 0.9);
  for (const m of P.naParede("O"))
    quase(P.distanciaDeEncosto(m), 0.9, `mesa ${m.n} depois de alinhar`, 1e-3);
  ok(mexidas > 0 && mexidas <= oeste.length, `mexeu ${mexidas} de ${oeste.length}`);

  for (const m of P.mesas) {
    const a = antes.get(m.n);
    if (P.paredeDe(m) !== "O") {
      ok(a.x === m.x && a.y === m.y, `mesa ${m.n} de outra parede ficou parada`);
    } else {
      // parede oeste: so o x muda; a posicao ao longo da parede fica
      ok(a.y === m.y, `mesa ${m.n}: alinhar oeste nao mexe em y`);
    }
  }
  ok(P.alinhaParede("O", 0.9) === 0, "alinhar de novo no mesmo valor nao mexe nada");
});

/* --- 4. pares na planta original: 14 pares de 3,00 m ------------------ */
bloco("pares na planta original", () => {
  for (const cen of ["A", "B"]) {
    P.mesas = planta(cen);
    const {pares, soltas} = P.pares();
    ok(pares.length === 14, `planta ${cen}: 14 pares, veio ${pares.length}`);
    ok(soltas.length === 0, `planta ${cen}: nenhuma mesa sem par, veio ${soltas}`);
    for (const c of pares) {
      quase(c.corredor, 3.0, `planta ${cen}, par ${c.a}-${c.b}: corredor`, 1e-3);
      ok(c.b === c.a + 1, `planta ${cen}: par ${c.a}-${c.b} e o da numeracao`);
    }
    // o vizinho mais proximo de cada par existe e nao invade o minimo de 1 m
    for (const c of pares)
      if (c.vizinho)
        ok(c.vizinho.folga >= D.modulo.entre_pares[0] - 1e-6,
           `planta ${cen}, par ${c.a}-${c.b}: folga ${c.vizinho.folga} para o vizinho`);
  }
});

/* --- 5. pares num cenario desenhado a mao ----------------------------- */
bloco("pares num cenario desenhado a mao", () => {
  P.mesas = comAlteracoes(acha("Hamad_3polos"));
  const {pares, soltas} = P.pares();
  ok(pares.length + soltas.length * 0.5 >= 1, "achou alguma coisa");
  ok(pares.every(c => c.corredor <= 6.0), "nenhum 'par' com corredor acima do alcance");
  ok(pares.every(c => c.a !== c.b), "nenhum par de uma mesa com ela mesma");
  const presas = pares.flatMap(c => [c.a, c.b]);
  ok(new Set(presas).size === presas.length, "nenhuma mesa em dois pares");
  ok(presas.length + soltas.length === 28, "as 28 mesas foram classificadas");
  // o par 5-22 e o caso que motivou a conferencia: corredor abaixo dos 2,50 m
  const apertado = pares.find(c => c.corredor < D.modulo.corredor[0]);
  ok(!!apertado, "o cenario tem mesmo um corredor abaixo do minimo para acusar");
  if (apertado)
    console.log(`  par ${apertado.a}-${apertado.b}: corredor `
      + `${apertado.corredor.toFixed(2)} m, abaixo do mínimo de `
      + `${D.modulo.corredor[0].toFixed(2)} m`);
});

/* --- 6. reparear + alinhar deixam o par na regra ---------------------- */
bloco("alinhar nao estraga o corredor de um par", () => {
  P.mesas = comAlteracoes(acha("Hamad_3polos"));
  const antes = P.pares().pares.filter(c => c.parede === "L")
    .map(c => [c.a + "-" + c.b, c.corredor]);
  P.alinhaParede("L", 3.0);
  const depois = new Map(P.pares().pares.map(c => [c.a + "-" + c.b, c.corredor]));
  for (const [quem, v] of antes)
    quase(depois.get(quem), v, `par ${quem}: corredor sobrevive ao alinhamento`, 1e-3);
});

console.log(`\n${testes - falhas}/${testes} verificações passaram`);
if (falhas) process.exit(1);
