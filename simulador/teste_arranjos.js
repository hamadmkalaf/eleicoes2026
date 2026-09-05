/* Teste dos arranjos vindos da prancheta: node simulador/teste_arranjos.js
 *
 * Cobre o que o simulador passou a aceitar de fora — arquivo de cenarios/,
 * JSON colado, formato antigo — e a conferencia geometrica que avisa quando
 * um arranjo salvo na prancheta tem mesa em cima de porta, zona ou vizinha.
 */
const fs = require("fs"), path = require("path");
const M = require("./modelo.js");
const base = JSON.parse(fs.readFileSync(path.join(__dirname, "../data/prancheta_hall2.json"), "utf8"));

let falhas = 0;
function ok(cond, msg){
  console.log((cond ? "  ok   " : "  FALHA ") + msg);
  if (!cond) falhas++;
}
const A = base.cenarios.A.mrvs;

console.log("normalizaArranjo");
ok(M.normalizaArranjo({base: "A", alteracoes: []}, base).alteracoes.length === 0, "arranjo vazio é a planta A");
for (const lixo of [null, 42, "texto", [], {}, {base: "C", alteracoes: []}, {base: "A"}, {alteracoes: []}])
  ok(M.normalizaArranjo(lixo, base) === null, "recusa " + JSON.stringify(lixo));

const antigo = {base: "A", mrvs: A.map(m => ({...m}))};
antigo.mrvs[6] = {...antigo.mrvs[6], x: antigo.mrvs[6].x + 2};
const conv = M.normalizaArranjo(antigo, base);
ok(conv.alteracoes.length === 1 && conv.alteracoes[0].n === 7,
   "formato antigo (as 28 mesas) vira só a mesa que saiu do lugar");

const sujo = M.normalizaArranjo({base: "A", alteracoes: [
  {n: 5, x: "abc", rot: "77", lado: 0},   // campos tortos caem para a planta
  {n: 99, x: 1},                          // mesa que nao existe
  {n: 5, y: 10},                          // mesma mesa de novo: vale a ultima
]}, base);
ok(sujo.alteracoes.length === 1 && sujo.alteracoes[0].n === 5, "descarta mesa inexistente e não duplica");
ok(sujo.alteracoes[0].x === A.find(m => m.n === 5).x && sujo.alteracoes[0].y === 10,
   "campo torto cai para o valor da planta, o bom é preservado");
ok([0, 90, 180, 270].includes(sujo.alteracoes[0].rot), "giro é encaixado em múltiplo de 90°");

console.log("mesasDoArranjo");
for (const cen of ["A", "B"]) {
  const mesas = M.mesasDoArranjo(base, {base: cen, alteracoes: []});
  ok(mesas.length === 28, `planta ${cen} devolve as 28 mesas`);
  ok(mesas.every((m, i) => m.n === base.cenarios[cen].mrvs[i].n), `planta ${cen} preserva a numeração`);
}
const movido = M.mesasDoArranjo(base, {base: "A", alteracoes: [{n: 3, y: 40}]});
ok(movido.find(m => m.n === 3).y === 40, "alteração parcial move só o eixo citado");
ok(movido.find(m => m.n === 3).x === A.find(m => m.n === 3).x, "e mantém o resto da mesa");

console.log("conflitosArranjo");
ok(M.conflitosArranjo(base, {base: "A", alteracoes: []}).length === 0, "planta oficial A não tem conflito");
ok(M.conflitosArranjo(base, {base: "B", alteracoes: []}).length === 0, "planta oficial B não tem conflito");
const m1 = A.find(m => m.n === 1);
const empilhado = M.conflitosArranjo(base, {base: "A", alteracoes: [{n: 2, ...m1, n: 2}]});
ok(empilhado.length === 2 && empilhado.every(c => c.motivos.some(t => t.startsWith("mesa"))),
   "duas mesas no mesmo lugar acusam uma à outra");
const foraDoSalao = M.conflitosArranjo(base, {base: "A", alteracoes: [{n: 1, x: 200, y: 200}]});
ok(foraDoSalao.some(c => c.mesa === 1 && c.motivos.includes("fora do salão")), "mesa fora do salão é pega");
const noRecorte = M.conflitosArranjo(base, {base: "A", alteracoes: [{n: 1, x: 3, y: 3, rot: 90}]});
ok(noRecorte.some(c => c.mesa === 1), "mesa dentro do recorte do salão é pega");

console.log(falhas ? `\n${falhas} FALHA(S)` : "\ntodos os testes passaram");
process.exit(falhas ? 1 : 0);
