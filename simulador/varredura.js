/* Varredura sob a REGRA DE PAREDE (oeste→A, norte→B, leste→C).
 * Substitui a varredura de 06/09, que otimizava sobre a lista fixa de MRVs.
 * Percorre arranjo × distância do checkpoint × atendentes × fila da mesa e
 * ordena por: falhas, atenções, espera P90 do eleitor, hora de fechamento. */
const {BASE, MRVS, DECISOES, ARRANJOS} = require("./dados.js");
const M = require("./modelo.js");

const arranjos = [
  {id: "A", nome: "Cenário A (planta oficial)", base: "A", alteracoes: []},
  {id: "B", nome: "Cenário B (planta oficial)", base: "B", alteracoes: []},
  ...ARRANJOS.map(a => M.normalizaArranjo(a, BASE)).filter(Boolean),
  require("./equitativo.js").arranjoEquitativo(),
];
// Hamad1 e "Hamad 2" são idênticos: mantém só o primeiro
const vistos = new Set(); const lista = [];
for (const a of arranjos) {
  const k = JSON.stringify(a.alteracoes) + a.base;
  if (vistos.has(k)) continue;
  vistos.add(k); lista.push(a);
}

const DISTS = [8, 12, 16, 20];
const FILAS = [{leve: 3, media: 4, pesada: 5}, {leve: 3, media: 4, pesada: 6}, {leve: 4, media: 5, pesada: 8}];
const RUNS = 6, SEED = 7;

/* Modos de alocação dos 9 atendentes de checkpoint entre as três entradas:
 * uniformes, e um proporcional à carga — que sob a regra de parede deixou de
 * ser igual entre entradas e por isso passa a ser candidato natural. */
function atendentesDe(modo, mont) {
  if (typeof modo === "number") return mont.zonas.map(() => modo);
  const tot = mont.zonas.reduce((s, z) => s + z.esperados, 0) || 1;
  const n = modo.total;
  const bruto = mont.zonas.map(z => z.esperados / tot * n);
  const base = bruto.map(v => Math.max(1, Math.floor(v)));
  let sobra = n - base.reduce((a, b) => a + b, 0);
  const ordem = bruto.map((v, i) => [v - Math.floor(v), i]).sort((a, b) => b[0] - a[0]);
  for (let k = 0; sobra > 0 && k < ordem.length * 3; k++, sobra--) base[ordem[k % ordem.length][1]]++;
  return base;
}
const MODOS = [2, 3, 4, {total: 9, nome: "9 proporcionais"}, {total: 12, nome: "12 proporcionais"}];
const nomeModo = m => typeof m === "number" ? `${m} por entrada` : m.nome;

const out = [];
let feitos = 0, total = lista.length * DISTS.length * MODOS.length * FILAS.length;
const t0 = Date.now();

for (const arr of lista) {
  for (const dist of DISTS) {
    for (const modo of MODOS) {
      for (const fila of FILAS) {
        const c = M.cenarioPadrao(DECISOES);
        c.salao = {base: arr.base, alteracoes: arr.alteracoes.map(m => ({...m})), arranjo: arr.id, nome: arr.nome};
        c.checkpoint = {existe: true, dist, filas: 2, atendentes: [2, 2, 2], seg: 8};
        c.filaMesa = {...fila};
        c.liberacao = "buffer";
        c.sim = {runs: RUNS, seed: SEED};
        // atendentes proporcionais precisam da carga por zona: monta uma vez antes
        const prov = M.montar(BASE, MRVS, c, DECISOES);
        c.checkpoint.atendentes = atendentesDe(modo, prov);
        const r = M.simular(BASE, MRVS, c, DECISOES);
        const falhas = r.vereditos.filter(v => v.status === "falha");
        const atencoes = r.vereditos.filter(v => v.status === "atencao");
        out.push({
          arranjo: arr.nome, arranjoId: arr.id, dist, atendentes: c.checkpoint.atendentes.join("/"),
          modo: nomeModo(modo), fila: `${fila.leve}/${fila.media}/${fila.pesada}`,
          nota: r.nota, nFalhas: falhas.length, nAtencoes: atencoes.length,
          falhas: falhas.map(v => v.id), atencoes: atencoes.map(v => v.id),
          p90min: Math.round(r.resumo.totalP90.p50 / 60),
          foraP90min: Math.round(r.resumo.esperaForaP90.p50 / 60),
          fecha: r.resumo.fechaUltima.p90,
          picoFora: Math.round(r.resumo.ring3TotalMax.p90),
          desequilibrio: +prov.desequilibrio.toFixed(2),
          conflitos: prov.conflitos.length,
          fita: Math.round(prov.separadores),
          carga: prov.zonas.map(z => `${z.letra} ${Math.round(z.esperados)}`).join(" "),
          cen: c,
        });
        feitos++;
        if (feitos % 25 === 0)
          process.stderr.write(`${feitos}/${total} (${Math.round((Date.now() - t0) / 1000)} s)\n`);
      }
    }
  }
}

out.sort((a, b) => a.nFalhas - b.nFalhas || a.nAtencoes - b.nAtencoes
  || a.p90min - b.p90min || a.fecha - b.fecha);
require("fs").writeFileSync("varredura_resultado.json", JSON.stringify(out, null, 1));
console.log(`${out.length} configurações em ${Math.round((Date.now() - t0) / 1000)} s\n`);
const cab = ["#", "arranjo", "cp", "atend", "fila", "nota", "F/A", "P90", "fora", "fecha", "pico", "deseq", "conf"];
console.log(cab.join("\t"));
out.slice(0, 20).forEach((r, i) => console.log([i + 1, r.arranjo.slice(0, 26), r.dist + "m", r.atendentes,
  r.fila, r.nota, `${r.nFalhas}/${r.nAtencoes}`, r.p90min + "min", r.foraP90min, M.hhmm(r.fecha),
  r.picoFora, r.desequilibrio, r.conflitos].join("\t")));
console.log("\nMelhor por arranjo:");
const porArr = {};
for (const r of out) if (!porArr[r.arranjo]) porArr[r.arranjo] = r;
for (const k of Object.keys(porArr)) { const r = porArr[k];
  console.log(`  ${k.padEnd(30)} ${r.nFalhas}F/${r.nAtencoes}A  P90 ${r.p90min}min  fecha ${M.hhmm(r.fecha)}  deseq ${r.desequilibrio}  cp ${r.dist}m atend ${r.atendentes} fila ${r.fila}  [${r.carga}]  falhas: ${r.falhas.join(",") || "—"}`); }
