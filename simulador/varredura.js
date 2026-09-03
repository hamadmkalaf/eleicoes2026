/* Varredura de cenários para escolher o Cenário Claude.
 * node simulador/varredura.js [runs por cenário]
 * Etapa 1: só geometria (cargas, cruzamentos, distâncias) para podar.
 * Etapa 2: simula os finalistas. */
const fs = require("fs"), path = require("path");
const Modelo = require("./modelo.js");
const base = JSON.parse(fs.readFileSync(path.join(__dirname, "../data/prancheta_hall2.json"), "utf8"));
const mrvs = JSON.parse(fs.readFileSync(path.join(__dirname, "../data/mrv_secoes.json"), "utf8"));
const RUNS = +(process.argv[2] || 3);

const particoes = [
  {nome: "N | E | W", inicio: 1, tamanhos: [8, 12, 8]},
  {nome: "N+E-norte | resto", inicio: 1, tamanhos: [16, 12]},
  {nome: "W+N | E+recorte", inicio: 23, tamanhos: [14, 14]},
  {nome: "N | E-norte | E-sul | W", inicio: 1, tamanhos: [8, 6, 6, 8]},
  {nome: "N+W | E", inicio: 21, tamanhos: [16, 12]},
];
const conjuntosPortas = [
  {e: ["S4", "S5", "S6"], x: ["S3", "S7"]},
  {e: ["S4", "S5", "S6"], x: ["S1", "S9"]},
  {e: ["S4", "S6"], x: ["S5"]},
  {e: ["S4", "S6"], x: ["S3", "S7"]},
  {e: ["S4", "S6"], x: ["S1", "S9"]},
  {e: ["S3", "S5", "S7"], x: ["S4", "S6"]},
  {e: ["S4", "S5"], x: ["S7", "S9"]},
  {e: ["S5", "S6"], x: ["S1", "S3"]},
  {e: ["S3", "S4", "S6", "S7"], x: ["S5"]},
  {e: ["S4", "S5", "S6", "S7"], x: ["S1", "S3"]},
];
function perms(a){ if (a.length <= 1) return [a]; const out = []; a.forEach((x, i) => { for (const p of perms(a.filter((_, j) => j !== i))) out.push([x, ...p]); }); return out; }
const todasPortas = ["S1", "S3", "S4", "S5", "S6", "S7", "S9"];

// Etapa 1
const cand = [];
for (const P of particoes) for (const C of conjuntosPortas) {
  const nz = P.tamanhos.length;
  // zonas → portas de entrada: todas as atribuições (com repetição só se faltar porta)
  let atribs;
  if (C.e.length >= nz) atribs = perms(C.e).map(p => p.slice(0, nz));
  else { // menos portas que zonas: gera todas as combinações com repetição
    atribs = [[]];
    for (let z = 0; z < nz; z++) atribs = atribs.flatMap(a => C.e.map(p => [...a, p]));
  }
  const vistos = new Set();
  for (const A of atribs) {
    const chave = A.join(","); if (vistos.has(chave)) continue; vistos.add(chave);
    for (let iz = 0; iz < nz; iz++) for (const sentido of ["horario", "antihorario"]) {
      const cen = Modelo.cenarioPadrao();
      // ajuste herdado para o Cenário Claude: mesas 23 e 24 sobem 3,5 m para a
      // fila da mesa do recorte (slot 22) não invadir a mesa 23
      cen.salao = {base: "A", alteracoes: [{n: 23, y: 16.03}, {n: 24, y: 19.93}]};
      cen.portas = {}; for (const p of todasPortas) cen.portas[p] = C.e.includes(p) ? "entrada" : (C.x.includes(p) ? "saida" : "fechada");
      cen.zonas = {inicio: P.inicio, tamanhos: P.tamanhos.slice(), portas: A};
      cen.ordem = {inicioZona: iz, sentido};
      cen.checkpoint = {existe: true, dist: 12, filas: 2, atendentes: P.tamanhos.map(() => 2), seg: 8};
      const m = Modelo.montar(base, mrvs, cen);
      const distMedia = m.zonas.reduce((s, z) => s + z.distCpMedia * z.mesas.length, 0) / 28;
      cand.push({P: P.nome, C, A, iz, sentido, cen, fracaoCruza: m.fracaoCruza, deseq: m.desequilibrio, conflitos: m.conflitos.length, distMedia, cargas: m.zonas.map(z => Math.round(z.esperados)), faixas: m.zonas.map(z => z.faixaMrv)});
    }
  }
}
console.log(`etapa 1: ${cand.length} candidatos`);
// poda: sem conflitos, menor cruzamento, menor desequilíbrio, menor distância
cand.sort((a, b) => (a.fracaoCruza - b.fracaoCruza) || (a.deseq - b.deseq) || (a.distMedia - b.distMedia));
const semConf = cand.filter(c => c.conflitos === 0);
console.log(`sem conflitos: ${semConf.length}`);
// estatísticas por partição/portas
const grupos = {};
for (const c of semConf) { const k = `${c.P} | E ${c.C.e.join("+")} | X ${c.C.x.join("+")}`; (grupos[k] = grupos[k] || []).push(c); }
console.log("\nmelhor por grupo (cruza %, deseq, dist média, cargas, faixas MRV, portas por zona):");
const melhores = [];
for (const [k, arr] of Object.entries(grupos)) {
  arr.sort((a, b) => (a.fracaoCruza - b.fracaoCruza) || (a.deseq - b.deseq) || (a.distMedia - b.distMedia));
  const b = arr[0];
  console.log(`  ${k.padEnd(48)} cruza ${(b.fracaoCruza*100).toFixed(0).padStart(3)} %  deseq ${b.deseq.toFixed(2)}  dist ${b.distMedia.toFixed(1)}  cargas ${b.cargas.join("/")}  MRV ${b.faixas.join(" ")}  portas ${b.A.join(",")}  ordem z${b.iz} ${b.sentido}`);
  melhores.push(b);
}
// Etapa 2: simula finalistas com cruzamento ≤ 15 % e deseq ≤ 1.6, variando checkpoint e filas
const finalistas = melhores.filter(c => c.fracaoCruza <= 0.15 && c.deseq <= 1.6);
console.log(`\netapa 2: ${finalistas.length} finalistas × variantes`);
const variantes = [];
for (const dist of [8, 12, 16]) for (const folga of [0, 1]) for (const fila of [[3, 4, 5], [3, 4, 6], [4, 5, 8]])
  variantes.push({dist, folga, fila});
const resultados = [];
let n = 0;
for (const f of finalistas) for (const v of variantes) {
  const cen = JSON.parse(JSON.stringify(f.cen));
  const nz = cen.zonas.tamanhos.length;
  // atendentes dimensionados pela capacidade das mesas da zona (ciclo 45 s, 8 s por eleitor no checkpoint)
  const m0 = Modelo.montar(base, mrvs, cen);
  cen.checkpoint = {existe: true, dist: v.dist, filas: 2, seg: 8,
    atendentes: m0.zonas.map(z => Math.ceil(z.mesas.length * (60 / 45) / 7.5) + v.folga)};
  cen.filaMesa = {leve: v.fila[0], media: v.fila[1], pesada: v.fila[2]};
  cen.sim = {runs: RUNS, seed: 7};
  const r = Modelo.simular(base, mrvs, cen);
  const falhas = r.vereditos.filter(x => x.status === "falha").length, atencoes = r.vereditos.filter(x => x.status === "atencao").length;
  resultados.push({f, v, cen, r, falhas, atencoes, atend: cen.checkpoint.atendentes.join("/")});
  n++; if (n % 20 === 0) console.log(`  ${n} simulados…`);
}
resultados.sort((a, b) => (a.falhas - b.falhas) || (a.atencoes - b.atencoes) || (a.r.resumo.totalP90.p50 - b.r.resumo.totalP90.p50) || (a.r.resumo.fechaUltima.p90 - b.r.resumo.fechaUltima.p90));
console.log("\nTOP 15 (falhas, atenções, espera P90, fecha p90, ring3 p90, fome pesadas/mesa, sep m, cruza %):");
for (const x of resultados.slice(0, 15)) {
  const R = x.r.resumo, pes = x.r.porMesa.filter(m => m.classe === "pesada");
  const fome = pes.reduce((s, m) => s + m.fome, 0) / pes.length / 60;
  console.log(`  F${x.falhas} A${x.atencoes} · P90 ${Math.round(R.totalP90.p50/60)} min · fecha ${Modelo.hhmm(R.fechaUltima.p90)} · ring3 ${Math.round(R.ring3TotalMax.p90)} · fome ${fome.toFixed(0)} · sep ${x.r.mont.separadores.toFixed(0)} · cruza ${(x.f.fracaoCruza*100).toFixed(0)} % · ${x.f.P} · E ${x.f.C.e.join("+")} X ${x.f.C.x.join("+")} · portas ${x.f.A.join(",")} · z${x.f.iz} ${x.f.sentido} · cp ${x.v.dist} m atend ${x.atend} · fila ${x.v.fila.join("/")}`);
  console.log(`     vereditos ruins: ${x.r.vereditos.filter(v => v.status !== "ok").map(v => `${v.titulo} [${v.status}] ${v.valor}`).join(" | ")}`);
}
fs.writeFileSync(path.join(__dirname, "../saidas/varredura_top.json"), JSON.stringify(resultados.slice(0, 15).map(x => ({cen: x.cen, falhas: x.falhas, atencoes: x.atencoes, P90min: Math.round(x.r.resumo.totalP90.p50/60), fecha90: Modelo.hhmm(x.r.resumo.fechaUltima.p90)})), null, 1));
console.log("\ngravado saidas/varredura_top.json");
