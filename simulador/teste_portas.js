/* Testes do modulo de portas vivas. Uso: node simulador/teste_portas.js */
"use strict";
const fs = require("fs"), path = require("path");
const P = require("./portas.js");
const RAIZ = path.resolve(__dirname, "..");
const DEC = JSON.parse(fs.readFileSync(path.join(RAIZ, "data", "decisoes.json"), "utf8"));
const BASE = JSON.parse(fs.readFileSync(path.join(RAIZ, "data", "prancheta_hall2.json"), "utf8"));
const R3J = JSON.parse(fs.readFileSync(path.join(RAIZ, "saidas", "ring3.json"), "utf8"));

let n = 0, falhas = 0;
function ok(cond, msg){ n++; if (!cond) { falhas++; console.log("FALHA:", msg); } }
function perto(a, b, tol, msg){ ok(Math.abs(a - b) <= tol, `${msg}: ${a} vs ${b}`); }

const ctx = {portas: BASE.portas, dec: DEC};
const decisao = P.estadoDaDecisao(DEC);

// 1. letras e cores seguem a ordem de x
const ents = P.entradas(decisao, BASE.portas);
ok(ents.map(e => e.id + e.porta).join() === "AS4,BS5,CS6", "letras da decisao");
const e5 = P.entradas({S3: "entrada", S7: "entrada", S4: "entrada", S1: "entrada", S9: "entrada"}, BASE.portas);
ok(e5.map(e => e.porta).join() === "S1,S3,S4,S7,S9" && e5.map(e => e.id).join("") === "ABCDE", "cinco entradas em ordem de x");
ok(new Set(e5.map(e => e.hex)).size === 5, "cinco cores distintas");

// 2. validacao
let v = P.valida({S4: "entrada"}, BASE.portas);
ok(!v.ok && v.erros.some(m => /saída/.test(m)), "sem saida e erro");
v = P.valida({S2: "saida"}, BASE.portas);
ok(!v.ok && v.erros.some(m => /entrada/.test(m)), "sem entrada e erro");
v = P.valida({S4: "entrada", S5: "saida", S6: "entrada"}, BASE.portas);
ok(v.ok && v.avisos.some(m => /cruza/.test(m)), "saida entre entradas avisa");
v = P.valida({S4: "entrada", N2: "entrada", S2: "saida"}, BASE.portas);
ok(!v.ok && v.erros.some(m => /N2/.test(m)), "porta fora do sul e erro");
ok(P.valida(decisao, BASE.portas).ok, "decisao e valida");

// 3. resolucao com a decisao reproduz decisoes.json
const rd = P.resolve(decisao, ctx);
ok(rd.igualDecisao && rd.desenho === P.DESENHO_DECIDIDO && rd.desenhoDecidido, "reconhece a decisao e abre no desenho decidido (H)");
ok(rd.ring3 && rd.ring3.codigo !== "PV" && rd.ring3.zonas.length === 3, "com a decisao o Ring 3 e o desenho H, tres zonas");
ok(P.resolve(decisao, Object.assign({desenho: "VS"}, ctx)).desenhoDecidido === false, "VS nao e o desenho decidido");
DEC.entradas.forEach((de, i) => {
  ok(rd.entradas[i].id === de.id && rd.entradas[i].porta === de.porta, `entrada ${de.id} porta`);
  ok(JSON.stringify(rd.entradas[i].mrvs) === JSON.stringify(de.mrvs), `mesas da entrada ${de.id}`);
  ok(rd.entradas[i].esperado === de.esperado, `esperado da entrada ${de.id}: ${rd.entradas[i].esperado} vs ${de.esperado}`);
});
for (const m of DEC.mesas) ok(rd.mesas[m.mrv].entrada === m.entrada, `mesa ${m.mrv} -> ${m.entrada}`);
ok(JSON.stringify(rd.saidas) === JSON.stringify(["S2", "S8"]), "saidas S2 e S8");

// 4. Ring 3: plano anterior (vigente ate 13/09) reconstruido bate com ring3.json
const pv = P.resolve(decisao, Object.assign({desenho: "vigente"}, ctx)).ring3, pvj = R3J.plano_vigente_reconstruido;
perto(pv.capacidade, pvj.capacidade, 0.6, "PV capacidade");
perto(pv.capRaias, pvj.capacidade_raias, 0.6, "PV raias");
// ring3.py de 11/09 passou a contar so as divisorias, o corredor de fundo, as
// baias e o funil como separador (191) e pos o contorno das zonas, a parede do
// corredor e as raias do apron "fora da conta" (fita); o porte em JS e o de
// 08/09, que conta tudo como separador (314, DOCUMENTACAO §11).
ok(pv.separadores === 314, `PV separadores no porte de 08/09: ${pv.separadores} vs 314`);
ok(pv.barreiraTotal > pvj.barreira_m && pv.barreiraTotal < pvj.barreira_m + Object.values(pvj.fora_da_conta).reduce((s, x) => s + x, 0) + 1,
   "PV barreira do porte = barreira contada + o que ring3.py deixou fora da conta");
for (const k of Object.keys(pvj.barreira_por_componente_m)) perto(pv.barreira[k], pvj.barreira_por_componente_m[k], 0.15, "PV " + k);
for (const [e, c] of Object.entries(pvj.por_entrada)) perto(pv.porEntrada[e], c, 0.6, "PV por entrada " + e);

// 5. Ring 3: os quatro desenhos sem garganta, com o esperado da decisao.
// O porte em JS e o dos desenhos anteriores a 11/09 (sem corredor em L, sem
// CCB na ponta); ring3.json mudou de geometria e de chaves em 11/09, entao a
// comparacao numerica so vale para o plano vigente reconstruido (teste 4).
// Aqui confere-se a consistencia interna e o que ainda bate: a largura das
// zonas do desenho decidido (H) e proporcional ao esperado por entrada.
const esperado = DEC.entradas.map(e => e.esperado);
const HPJ = R3J.girado_ccb_na_ponta;
for (const id of ["VS", "V", "H", "HB"]) {
  const d = P.desenhoPorId(id, ents, esperado, {});
  ok(d.capacidade > 0 && d.separadores > 0 && d.barreiraTotal > 0, id + " numeros positivos");
  ok(d.zonas.length === 3 && d.zonas.every(z => z.raias > 0), id + " tres zonas com raias");
  const tot = Object.values(d.porEntrada).reduce((s, x) => s + x, 0);
  const esp = esperado.reduce((s, x) => s + x, 0);
  ents.forEach((z, i) => perto(d.porEntrada[z.id] / tot, esperado[i] / esp, 0.02, `${id} quota da zona ${z.id} proporcional ao esperado`));
}
const dH = P.desenhoPorId("H", ents, esperado, {});
ents.forEach((z, i) => perto(dH.porEntrada[z.id] / dH.capacidade, HPJ.por_entrada[z.id] / HPJ.capacidade, 0.01, `H: quota da zona ${z.id} igual a do desenho decidido (ring3.json)`));
ok(Object.keys(R3J).includes(P.DESENHO_DECIDIDO === "H" ? "girado_ccb_na_ponta" : ""), "ring3.json tem o desenho decidido");

// 6. cinco entradas: cinco zonas que fecham em 44 m, cinco letras, 28 mesas
const est5 = {S1: "entrada", S3: "entrada", S4: "entrada", S7: "entrada", S9: "entrada", S2: "saida", S8: "saida"};
for (const id of ["VS", "V", "H", "HB"]) {
  const r = P.resolve(est5, Object.assign({desenho: id}, ctx));
  ok(r.ring3.zonas.length === 5 && r.entradas.length === 5, id + " cinco zonas");
  const RG = r.ring3.ring, z = r.ring3.zonas;
  const borda = r.ring3.comBaias ? P.R3.LARG_BAIA : 0;
  perto(z[0].x0, RG.x0 + borda, 0.01, id + " primeira zona encosta");
  perto(z[4].x1, RG.x1 - borda, 0.01, id + " ultima zona encosta");
  for (let i = 1; i < 5; i++) ok(z[i].x0 - z[i - 1].x1 >= 1.99, `${id} vao entre zonas ${i}`);
  ok(Object.keys(r.mesas).length === 28, id + " 28 mesas atribuidas");
  const altas = DEC.mesas.filter(m => m.classe === "alta").map(m => r.mesas[m.mrv].entrada);
  ok(new Set(altas).size === 3, id + " as tres vermelhas em entradas distintas");
  ok(r.entradas.every(e => e.mrvs.length > 0), id + " toda entrada tem mesa");
  ok(r.ring3.capacidade > 0 && r.ring3.separadores > 0, id + " numeros positivos");
  ok(r.igualDecisao === false, id + " nao e a decisao");
}
// preset vigente com 5 entradas cai em VS
ok(P.resolve(est5, Object.assign({desenho: "vigente"}, ctx)).desenho === "VS", "vigente so com tres entradas");

// 7. uma entrada so
const r1 = P.resolve({S5: "entrada", S2: "saida"}, Object.assign({desenho: "VS"}, ctx));
ok(r1.entradas.length === 1 && r1.ring3.zonas.length === 1 && Object.keys(r1.mesas).length === 28, "uma entrada");
perto(r1.ring3.zonas[0].larg, 31 * P.R3.PASSO_RAIA, 0.01, "uma zona ocupa o Ring inteiro em raias inteiras (VS)");
ok(r1.ring3.zonas[0].raias === 31, "31 raias de 1,4 m em 44 m");

// 8. hash de ida e volta
const h = P.paraHash(est5, "H");
const volta = P.deHash("#" + h);
ok(P.igual(volta.estado, est5) && volta.desenho === "H", "hash ida e volta: " + h);
ok(P.deHash("#nada") === null, "hash sem portas");

// 9. SVG
const svg = P.svgRing3(P.resolve(est5, Object.assign({desenho: "VS"}, ctx)), {portas: BASE.portas});
ok(svg.startsWith("<svg") && (svg.match(/<rect/g) || []).length > 5 && /S9 · E/.test(svg), "svg com cinco zonas");

// 10. decisao viva
ok(P.decisaoViva(DEC, P.resolve(decisao, Object.assign({desenho: "vigente"}, ctx))) === DEC, "decisao viva com a decisao e o plano anterior e o proprio bloco");
const dvH = P.decisaoViva(DEC, rd);
ok(dvH !== DEC && dvH.ring3.desenho === P.DESENHO_DECIDIDO && dvH.entradas.every((e, i) => JSON.stringify(e.mrvs) === JSON.stringify(DEC.entradas[i].mrvs)), "decisao viva com o desenho decidido: mesmas mesas por entrada, Ring 3 do desenho H");
const dv = P.decisaoViva(DEC, P.resolve(est5, Object.assign({desenho: "VS"}, ctx)));
ok(dv.entradas.length === 5 && dv.portas.S1.papel === "entrada" && dv.portas.S1.entrada === "A" && dv.saidas.join() === "S2,S8", "decisao viva: portas e entradas");
ok(Array.isArray(dv.mesas) && dv.mesas.every(m => /^[A-E]$/.test(m.entrada)) && dv.ring3.capacidade > 1000 && dv.ring3.rect.length === 4, "decisao viva: mesas e ring3");
const decObj = Object.assign({}, DEC, {mesas: Object.fromEntries(DEC.mesas.map(m => [m.mrv, m]))});
const dvo = P.decisaoViva(decObj, P.resolve(est5, {portas: BASE.portas, dec: decObj, desenho: "H"}));
ok(!Array.isArray(dvo.mesas) && Object.keys(dvo.mesas).length === 28 && dvo.mesas["22"].entrada.length === 1, "decisao viva com mesas por MRV (prancheta)");

console.log(`${n - falhas}/${n} verificações passaram`);
process.exit(falhas ? 1 : 0);
