/* Teste de sanidade do motor em Node: node simulador/teste_modelo.js [padrao|claude] */
const fs = require("fs"), path = require("path");
const Modelo = require("./modelo.js");
const base = JSON.parse(fs.readFileSync(path.join(__dirname, "../data/prancheta_hall2.json"), "utf8"));
const mrvs = JSON.parse(fs.readFileSync(path.join(__dirname, "../data/mrv_secoes.json"), "utf8"));
const qual = process.argv[2] || "padrao";
const cen = qual === "claude" ? Modelo.cenarioClaude() : Modelo.cenarioPadrao();
cen.sim.runs = +(process.argv[3] || cen.sim.runs);

const t0 = Date.now();
const res = Modelo.simular(base, mrvs, cen);
const dt = Date.now() - t0;
const m = res.mont, r = res.resumo;
console.log(`== ${cen.nome} · ${r.runs} dias em ${dt} ms`);
console.log(`esperados ${Math.round(m.esperadosTotal)} de ${m.aptosTotal} aptos; taxa ${m.taxa.rotulo}`);
for (const z of m.zonas) console.log(`  ${z.nome}: slots ${z.slots[0]}–${z.slots[z.slots.length-1]} · MRV ${z.faixaMrv} · ${z.mesas.length} mesas · ${Math.round(z.esperados)} eleitores · porta ${z.porta} · capBuffer ${z.capBuffer} · cp atend ${z.atendentesCp} · distCp média ${z.distCpMedia.toFixed(1)} m máx ${z.distCpMax.toFixed(1)}`);
console.log(`desequilíbrio ${m.desequilibrio.toFixed(2)} · separadores ${m.separadores.toFixed(0)} m · conflitos ${JSON.stringify(m.conflitos)} · cruzam corredor ${(m.fracaoCruza*100).toFixed(0)} % (MRV ${m.mesasCruzam.join(",")}) · leque ${(m.fracaoLeque*100).toFixed(0)} % · avisos ${m.avisos.join(" / ")}`);
// conservação
for (const d of res.dias) {
  const votosMesas = d.porMesa.reduce((s, x) => s + x.votos + x.just, 0);
  if (votosMesas !== d.eleitores) console.log("!! conservação falhou", votosMesas, d.eleitores);
  if (d.linha.dentro[d.linha.dentro.length - 1] !== 0) console.log("!! sobrou gente dentro", d.linha.dentro[d.linha.dentro.length - 1]);
}
console.log(`fecha última: p50 ${Modelo.hhmm(r.fechaUltima.p50)} p90 ${Modelo.hhmm(r.fechaUltima.p90)} max ${Modelo.hhmm(r.fechaUltima.max)}`);
console.log(`espera total P90: p50 ${Math.round(r.totalP90.p50/60)} min · fora ${Math.round(r.esperaForaP90.p50/60)} · dentro ${Math.round(r.esperaDentroP90.p50/60)}`);
console.log(`dentro máx ${r.dentroMax.p50} · ring3 máx ${r.ring3TotalMax.p50} · fome pesadas ${r.fomePesadasMin.p50.toFixed(0)} min total · triagem ${(r.triOcupacao.p50*100).toFixed(0)} %`);
for (const z of res.porZona) console.log(`  ${z.nome}: ring3 máx ${z.ring3Max} · buffer máx ${z.bufferMax}/${z.capBuffer} · cp fila máx ${z.cpFilaMax} · cp ocup ${(z.cpOcupacao*100).toFixed(0)} % · fecha ${Modelo.hhmm(z.fecha)}`);
console.log("mesas (mrv: votos, fecha, ocupUrna, fome min, filaMax/L):");
console.log(res.porMesa.slice().sort((a,b)=>b.fecha-a.fecha).map(x => `${x.mrv}:${x.votos} ${Modelo.hhmm(x.fecha)} ${(x.ocupUrna*100).toFixed(0)}% f${(x.fome/60).toFixed(0)} ${x.filaMax}/${x.L}`).join(" | "));
console.log("vereditos:");
for (const v of res.vereditos) console.log(`  [${v.status}] ${v.titulo}: ${v.valor}  (meta ${v.meta})`);
console.log(res.texto.join("\n"));
// perfil da linha do tempo do dia de referência (a cada hora)
const L = res.ref.linha;
console.log("hora  ring3(z)  buffer(z)  cp(z)  dentro  votados");
for (let i = 0; i < L.t.length; i += 60) console.log(Modelo.hhmm(L.t[i]).padEnd(6), L.ring3.map(a=>a[i]).join("/").padEnd(12), L.buffer.map(a=>a[i]).join("/").padEnd(10), L.cp.map(a=>a[i]).join("/").padEnd(8), String(L.dentro[i]).padEnd(7), L.votados[i]);
