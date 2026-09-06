/* Varredura de cenários para escolher o Cenário Claude.
 * node simulador/varredura.js [runs por cenário]
 *
 * As portas e as entradas sao as da decisao do Posto (S4/S5/S6 entram, S2/S8
 * saem; cada entrada com as mesas que scripts/decisoes.py lhe atribuiu), entao
 * o que se varre e o que ainda e premissa de quem simula: o arranjo das 28
 * mesas (planta oficial e cenarios salvos na prancheta), a distancia e a
 * lotacao do checkpoint, e o tamanho das filas por classe.
 * Etapa 1: so geometria (conflitos, cruzamentos) para podar arranjos.
 * Etapa 2: simula as combinacoes restantes. */
const fs = require("fs"), path = require("path");
const Modelo = require("./modelo.js");
const RAIZ = path.join(__dirname, "..");
const base = JSON.parse(fs.readFileSync(path.join(RAIZ, "data/prancheta_hall2.json"), "utf8"));
const mrvs = JSON.parse(fs.readFileSync(path.join(RAIZ, "data/mrv_secoes.json"), "utf8"));
const dec = JSON.parse(fs.readFileSync(path.join(RAIZ, "data/decisoes.json"), "utf8"));
const RUNS = +(process.argv[2] || 3);

// arranjos: planta A, planta A com as mesas 23/24 subidas (ajuste antigo do
// Cenario Claude) e os cenarios salvos em cenarios/
const arranjos = [
  {id: "A", nome: "planta A", salao: {base: "A", alteracoes: []}},
  {id: "A+23/24", nome: "planta A, 23 e 24 ao norte", salao: {base: "A", alteracoes: [{n: 23, y: 17.5}, {n: 24, y: 21.4}]}},
];
const pasta = path.join(RAIZ, "cenarios");
for (const f of fs.readdirSync(pasta).filter(x => x.endsWith(".json")).sort()) {
  const c = JSON.parse(fs.readFileSync(path.join(pasta, f), "utf8"));
  const a = Modelo.normalizaArranjo(c, base);
  if (a) arranjos.push({id: f.replace(/\.json$/, ""), nome: a.nome, salao: {base: a.base, alteracoes: a.alteracoes}});
}

// Etapa 1: geometria
const cand = [];
for (const A of arranjos) {
  const cen = Modelo.cenarioPadrao(dec);
  cen.salao = A.salao;
  cen.checkpoint = {existe: true, dist: 12, filas: 2, atendentes: dec.entradas.map(() => 2), seg: 8};
  const conflitosArranjo = Modelo.conflitosArranjo(base, A.salao).length;
  const m = Modelo.montar(base, mrvs, cen, dec);
  const distMedia = m.zonas.reduce((s, z) => s + z.distCpMedia * z.mesas.length, 0) / 28;
  cand.push({A, cen, conflitosArranjo, conflitos: m.conflitos.length, fracaoCruza: m.fracaoCruza, deseq: m.desequilibrio, distMedia});
  console.log(`  ${A.nome.padEnd(36)} mesas em conflito ${conflitosArranjo} · filas em conflito ${m.conflitos.length} · cruza ${(m.fracaoCruza*100).toFixed(0)} % · deseq ${m.desequilibrio.toFixed(2)} · dist cp ${distMedia.toFixed(1)} m`);
}
const finalistas = cand.filter(c => c.conflitosArranjo === 0 && c.conflitos === 0);
console.log(`\netapa 1: ${cand.length} arranjos, ${finalistas.length} sem conflito`);

// Etapa 2: simula
const variantes = [];
for (const dist of [8, 12, 16]) for (const folga of [0, 1]) for (const fila of [[3, 4, 5], [3, 4, 6], [4, 5, 8]])
  variantes.push({dist, folga, fila});
const resultados = [];
let n = 0;
for (const f of finalistas) for (const v of variantes) {
  const cen = JSON.parse(JSON.stringify(f.cen));
  const m0 = Modelo.montar(base, mrvs, cen, dec);
  cen.checkpoint = {existe: true, dist: v.dist, filas: 2, seg: 8,
    atendentes: m0.zonas.map(z => Math.ceil(z.mesas.length * (60 / 45) / 7.5) + v.folga)};
  cen.filaMesa = {leve: v.fila[0], media: v.fila[1], pesada: v.fila[2]};
  cen.sim = {runs: RUNS, seed: 7};
  const r = Modelo.simular(base, mrvs, cen, dec);
  const falhas = r.vereditos.filter(x => x.status === "falha").length, atencoes = r.vereditos.filter(x => x.status === "atencao").length;
  resultados.push({f, v, cen, r, falhas, atencoes, atend: cen.checkpoint.atendentes.join("/")});
  n++; if (n % 10 === 0) console.log(`  ${n} simulados…`);
}
resultados.sort((a, b) => (a.falhas - b.falhas) || (a.atencoes - b.atencoes) || (a.r.resumo.totalP90.p50 - b.r.resumo.totalP90.p50) || (a.r.resumo.fechaUltima.p90 - b.r.resumo.fechaUltima.p90));
console.log("\nTOP 15 (falhas, atenções, espera P90, fecha p90, ring3 p90, fome vermelhas/mesa, sep m, cruza %):");
for (const x of resultados.slice(0, 15)) {
  const R = x.r.resumo, pes = x.r.porMesa.filter(m => m.classe === "pesada");
  const fome = pes.reduce((s, m) => s + m.fome, 0) / Math.max(1, pes.length) / 60;
  console.log(`  F${x.falhas} A${x.atencoes} · P90 ${Math.round(R.totalP90.p50/60)} min · fecha ${Modelo.hhmm(R.fechaUltima.p90)} · ring3 ${Math.round(R.ring3TotalMax.p90)} · fome ${fome.toFixed(0)} · sep ${x.r.mont.separadores.toFixed(0)} · cruza ${(x.f.fracaoCruza*100).toFixed(0)} % · ${x.f.A.nome} · cp ${x.v.dist} m atend ${x.atend} · fila ${x.v.fila.join("/")}`);
  console.log(`     vereditos ruins: ${x.r.vereditos.filter(v => v.status !== "ok").map(v => `${v.titulo} [${v.status}] ${v.valor}`).join(" | ")}`);
}
fs.writeFileSync(path.join(RAIZ, "saidas/varredura_top.json"), JSON.stringify(resultados.slice(0, 15).map(x => ({arranjo: x.f.A.id, cen: x.cen, falhas: x.falhas, atencoes: x.atencoes, P90min: Math.round(x.r.resumo.totalP90.p50/60), fecha90: Modelo.hhmm(x.r.resumo.fechaUltima.p90), ring3p90: Math.round(x.r.resumo.ring3TotalMax.p90)})), null, 1));
console.log("\ngravado saidas/varredura_top.json");
