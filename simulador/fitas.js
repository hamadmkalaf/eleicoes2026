/* Fitas no piso em vez do checkpoint: varredura no motor oficial.
 * node simulador/fitas.js [dias por cenário]
 *
 * Sugestão em exame: tirar o checkpoint do meio do salão e guiar o eleitor
 * da porta direto à mesa por fitas coloridas no piso. O motor do simulador
 * (modelo.js) já trata "sem checkpoint" (cen.checkpoint.existe = false): o
 * eleitor liberado na porta caminha direto à mesa. O que este script faz:
 *
 *  1. roda o Cenário Claude (arranjo "Três polos", entradas e portas da
 *     decisão) com e sem checkpoint, sob as três políticas de liberação da
 *     porta e com filas de mesa mais longas, para medir o que o checkpoint
 *     faz além de apontar a mesa: reter quem chega a uma fila cheia;
 *  2. acrescenta o erro de sinalização (cen.sinalizacao: fração que se perde
 *     e desvio em metros), que só existe sem checkpoint;
 *  3. mede a geometria das fitas sobre o arranjo real: metros por entrada,
 *     cruzamentos entre fitas de entradas diferentes e entre fita e saída,
 *     com a atribuição mesa → entrada da decisão (por quota, mistura paredes)
 *     e com uma atribuição geográfica (cada porta leva à parede mais perto);
 *  4. simula também a atribuição geográfica, para mostrar o que ela custa em
 *     equilíbrio das portas e do Ring 3.
 *
 * Grava saidas/fitas_piso.json (lido por scripts/fitas_piso.py, que desenha
 * as fitas sobre a planta e monta a página). */
const fs = require("fs"), path = require("path");
const Modelo = require("./modelo.js");
const RAIZ = path.join(__dirname, "..");
const base = JSON.parse(fs.readFileSync(path.join(RAIZ, "data/prancheta_hall2.json"), "utf8"));
const mrvs = JSON.parse(fs.readFileSync(path.join(RAIZ, "data/mrv_secoes.json"), "utf8"));
const dec = JSON.parse(fs.readFileSync(path.join(RAIZ, "data/decisoes.json"), "utf8"));
const RUNS = +(process.argv[2] || 8);

const pasta = path.join(RAIZ, "cenarios");
const arranjos = fs.readdirSync(pasta).filter(f => f.endsWith(".json")).sort().map(f => {
  const a = Modelo.normalizaArranjo(JSON.parse(fs.readFileSync(path.join(pasta, f), "utf8")), base);
  return a && {...a, id: f.replace(/\.json$/, "")};
}).filter(Boolean);

/* ---------------------------------------------------------------- */
/* Atribuição geográfica: cada mesa vai para a porta mais próxima    */
/* ---------------------------------------------------------------- */
function decGeografica(cenBase){
  // Por parede: a porta mais a oeste (S4, A) leva à parede oeste, a do meio
  // (S5, B) à parede norte, a mais a leste (S6, C) à fachada leste. (A regra
  // "porta mais próxima de cada mesa" degenera: S5 fica com duas mesas.)
  const m0 = Modelo.montar(base, mrvs, cenBase, dec);
  const d2 = JSON.parse(JSON.stringify(dec));
  for (const e of d2.entradas) e.mrvs = [];
  const porParede = {0: "A", 270: "B", 180: "C"};      // rot do módulo: 0 oeste, 270 norte, 180 leste
  for (const m of m0.mesas) {
    const letra = porParede[m.pos.rot] || "B";
    d2.entradas.find(e => e.id === letra).mrvs.push(m.mrv);
  }
  for (const e of d2.entradas) {
    e.mrvs.sort((a, b) => a - b);
    e.esperado = e.mrvs.reduce((s, k) => s + d2.mesas.find(x => x.mrv === k).esperado, 0);
    for (const k of e.mrvs) { const x = d2.mesas.find(q => q.mrv === k); x.entrada = e.id; x.porta = e.porta; }
  }
  return d2;
}

/* ---------------------------------------------------------------- */
/* Geometria das fitas                                               */
/* ---------------------------------------------------------------- */
function cruzam(p1, p2, p3, p4){
  const d = (a, b, c) => (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]);
  const d1 = d(p3, p4, p1), d2 = d(p3, p4, p2), d3 = d(p1, p2, p3), d4 = d(p1, p2, p4);
  return ((d1 > 0) !== (d2 > 0)) && ((d3 > 0) !== (d4 > 0)) && d1 !== 0 && d2 !== 0 && d3 !== 0 && d4 !== 0;
}
const hip = (a, b) => Math.hypot(b[0] - a[0], b[1] - a[1]);

/* Fita por mesa: reta da soleira da porta à frente da fila da mesa (cauda).
 * Fita por parede (tronco): da porta ao primeiro ponto da parede, depois
 * rente à parede, passando pela cauda de cada mesa daquela parede. */
function geometriaFitas(m, rotulo){
  const portas = {}; for (const p of base.portas) portas[p.id] = p;
  const centro = id => [(portas[id].x1 + portas[id].x2) / 2, (portas[id].y1 + portas[id].y2) / 2];
  const parede = mesa => {
    const p = mesa.pos;
    if (p.rot === 270) return "norte";
    if (p.rot === 180) return "leste";
    if (p.rot === 0) return "oeste";
    return "recorte";
  };
  const linhas = m.mesas.map(mesa => {
    const z = m.zonas[mesa.zona];
    return {mrv: mesa.mrv, entrada: z.letra, porta: z.porta, cor: z.cor, parede: parede(mesa),
            a: z.portaCentro, b: mesa.cauda, comp: hip(z.portaCentro, mesa.cauda), saida: mesa.saida,
            bSaida: centro(mesa.saida), classe: mesa.classeDecisao, esperados: mesa.esperados};
  });
  // cruzamentos entre fitas de entradas diferentes (as da mesma entrada
  // saem do mesmo ponto e não se cruzam)
  let cruzEntre = 0, paresEntre = [];
  for (let i = 0; i < linhas.length; i++) for (let j = i + 1; j < linhas.length; j++) {
    const A = linhas[i], B = linhas[j];
    if (A.entrada === B.entrada) continue;
    if (cruzam(A.a, A.b, B.a, B.b)) { cruzEntre++; paresEntre.push([A.mrv, B.mrv]); }
  }
  // cruzamentos fita × trajeto de saída (cauda da mesa → porta de saída)
  let cruzSaida = 0;
  for (const A of linhas) for (const B of linhas)
    if (cruzam(A.a, A.b, B.b, B.bSaida)) cruzSaida++;
  // troncos por parede, por entrada
  const troncos = [];
  for (const z of m.zonas) {
    const porParede = {};
    for (const L of linhas.filter(l => l.entrada === z.letra)) (porParede[L.parede] = porParede[L.parede] || []).push(L);
    for (const [par, Ls] of Object.entries(porParede)) {
      // ordena ao longo da parede a partir do ponto mais perto da porta
      Ls.sort((p, q) => hip(z.portaCentro, p.b) - hip(z.portaCentro, q.b));
      const pts = [z.portaCentro, ...Ls.map(l => l.b)];
      let comp = 0; for (let i = 1; i < pts.length; i++) comp += hip(pts[i - 1], pts[i]);
      troncos.push({entrada: z.letra, cor: z.cor, parede: par, mesas: Ls.map(l => l.mrv), pontos: pts, comp});
    }
  }
  let cruzTroncos = 0;
  for (let i = 0; i < troncos.length; i++) for (let j = i + 1; j < troncos.length; j++) {
    if (troncos[i].entrada === troncos[j].entrada) continue;
    const P = troncos[i].pontos, Q = troncos[j].pontos;
    for (let a = 1; a < P.length; a++) for (let b = 1; b < Q.length; b++)
      if (cruzam(P[a - 1], P[a], Q[b - 1], Q[b])) cruzTroncos++;
  }
  const porEntrada = m.zonas.map(z => {
    const Ls = linhas.filter(l => l.entrada === z.letra);
    return {entrada: z.letra, porta: z.porta, cor: z.cor, mesas: z.mrvs, esperados: Math.round(z.esperados),
            capRing3: z.capRing3, paredes: [...new Set(Ls.map(l => l.parede))],
            fitaPorMesa_m: Ls.reduce((s, l) => s + l.comp, 0),
            fitaTroncos_m: troncos.filter(t => t.entrada === z.letra).reduce((s, t) => s + t.comp, 0),
            nTroncos: troncos.filter(t => t.entrada === z.letra).length,
            distMedia_m: Ls.reduce((s, l) => s + l.comp * l.esperados, 0) / Ls.reduce((s, l) => s + l.esperados, 0)};
  });
  return {rotulo, linhas, troncos, porEntrada, cruzEntre, paresEntre, cruzSaida, cruzTroncos,
          fitaPorMesa_m: linhas.reduce((s, l) => s + l.comp, 0),
          fitaTroncos_m: troncos.reduce((s, t) => s + t.comp, 0),
          desequilibrio: m.desequilibrio};
}

/* ---------------------------------------------------------------- */
/* Grade de cenários                                                 */
/* ---------------------------------------------------------------- */
function cenBase(d){
  const c = Modelo.cenarioClaude(d, arranjos);
  c.sim = {runs: RUNS, seed: 7};
  return c;
}
const semCp = c => { c.checkpoint = {...c.checkpoint, existe: false}; return c; };
const GRADE = [
  {id: "ref", grupo: "referência", nome: "Cenário Claude: checkpoint a 16 m, 3/3/3, liberação por buffer", mod: c => c},
  {id: "fitas-buffer", grupo: "fitas", nome: "Fitas, sem checkpoint, porta libera enquanto cabe na zona (buffer = soma das filas)", mod: c => semCp(c)},
  {id: "fitas-livre", grupo: "fitas", nome: "Fitas, sem checkpoint, porta livre (sem contenção)", mod: c => { semCp(c); c.liberacao = "livre"; return c; }},
  {id: "fitas-mesa", grupo: "fitas", nome: "Fitas, sem checkpoint, porta só libera quem tem vaga na sua mesa", mod: c => { semCp(c); c.liberacao = "mesa"; return c; }},
  {id: "fitas-buffer-filas", grupo: "fitas", nome: "Fitas, sem checkpoint, buffer, filas de mesa 5/8/12", mod: c => { semCp(c); c.filaMesa = {leve: 5, media: 8, pesada: 12}; return c; }},
  {id: "fitas-livre-filas", grupo: "fitas", nome: "Fitas, sem checkpoint, porta livre, filas de mesa 5/8/12", mod: c => { semCp(c); c.liberacao = "livre"; c.filaMesa = {leve: 5, media: 8, pesada: 12}; return c; }},
  {id: "fitas-buffer-erro10", grupo: "sinalização", nome: "Fitas, buffer, 10 % se perdem e andam 30 m a mais", mod: c => { semCp(c); c.sinalizacao = {erro: 0.10, desvio: 30}; return c; }},
  {id: "fitas-buffer-erro25", grupo: "sinalização", nome: "Fitas, buffer, 25 % se perdem e andam 40 m a mais", mod: c => { semCp(c); c.sinalizacao = {erro: 0.25, desvio: 40}; return c; }},
  {id: "fitas-livre-erro25", grupo: "sinalização", nome: "Fitas, porta livre, 25 % se perdem e andam 40 m a mais", mod: c => { semCp(c); c.liberacao = "livre"; c.sinalizacao = {erro: 0.25, desvio: 40}; return c; }},
  {id: "ref-id60", grupo: "identificação 60 s", nome: "Checkpoint, identificação 60 s", mod: c => { c.tempos.identificacao = 60; return c; }},
  {id: "fitas-buffer-id60", grupo: "identificação 60 s", nome: "Fitas, buffer, identificação 60 s", mod: c => { semCp(c); c.tempos.identificacao = 60; return c; }},
  {id: "fitas-livre-id60", grupo: "identificação 60 s", nome: "Fitas, porta livre, identificação 60 s", mod: c => { semCp(c); c.liberacao = "livre"; c.tempos.identificacao = 60; return c; }},
  {id: "ref-grande", grupo: "comparecimento +15 %", nome: "Checkpoint, comparecimento grande", mod: c => { c.comparecimento = "grande"; return c; }},
  {id: "fitas-buffer-grande", grupo: "comparecimento +15 %", nome: "Fitas, buffer, comparecimento grande", mod: c => { semCp(c); c.comparecimento = "grande"; return c; }},
  {id: "geo-ref", grupo: "atribuição geográfica", nome: "Checkpoint, mesas atribuídas por parede (oeste A, norte B, leste C)", dec: "geo", mod: c => c},
  {id: "geo-fitas-buffer", grupo: "atribuição geográfica", nome: "Fitas, buffer, mesas atribuídas por parede", dec: "geo", mod: c => semCp(c)},
  {id: "geo-fitas-livre", grupo: "atribuição geográfica", nome: "Fitas, porta livre, mesas atribuídas por parede", dec: "geo", mod: c => { semCp(c); c.liberacao = "livre"; return c; }},
];

const decGeo = decGeografica(cenBase(dec));
const resultados = [];
for (const g of GRADE) {
  const d = g.dec === "geo" ? decGeo : dec;
  const cen = g.mod(cenBase(d));
  const t0 = Date.now();
  const r = Modelo.simular(base, mrvs, cen, d);
  const R = r.resumo, m = r.mont;
  const ruins = r.vereditos.filter(v => v.status !== "ok").map(v => ({id: v.id, titulo: v.titulo, status: v.status, valor: v.valor}));
  const linha = {
    id: g.id, grupo: g.grupo, nome: g.nome, atribuicao: g.dec === "geo" ? "geográfica" : "decisão (quota)",
    checkpoint: cen.checkpoint.existe, liberacao: cen.liberacao, filaMesa: cen.filaMesa,
    identificacao: cen.tempos.identificacao, comparecimento: cen.comparecimento, sinalizacao: cen.sinalizacao || null,
    fechaP50: Modelo.hhmm(R.fechaUltima.p50), fechaP90: Modelo.hhmm(R.fechaUltima.p90),
    p90TotalMin: Math.round(R.totalP90.p50 / 60), p90ForaMin: Math.round(R.esperaForaP90.p50 / 60), p90DentroMin: Math.round(R.esperaDentroP90.p50 / 60),
    dentroMax: R.dentroMax.p50, ring3Max: Math.round(R.ring3TotalMax.p50), ring3MaxP90: Math.round(R.ring3TotalMax.p90),
    fomeVermelhasMin: Math.round(R.fomePesadasMin.p50), estouroFilas: Math.round(R.estouroFilas.p50),
    perdidos: Math.round(R.perdidos.p50), fita_m: Math.round(m.separadores), capBuffer: m.zonas.map(z => z.capBuffer),
    desequilibrio: +m.desequilibrio.toFixed(2), conflitos: m.conflitos.length,
    nota: r.nota, ruins, porZona: r.porZona.map(z => ({nome: z.nome, porta: z.porta, esperados: Math.round(z.esperados), ring3Max: z.ring3Max, capRing3: m.zonas[z.idx].capRing3, bufferMax: z.bufferMax, capBuffer: z.capBuffer})),
    filaMaxPorClasse: ["pesada", "media", "leve"].map(cl => ({classe: cl, filaMax: Math.max(...r.porMesa.filter(x => x.classe === cl).map(x => x.filaMax)), L: r.porMesa.find(x => x.classe === cl).L})),
  };
  resultados.push(linha);
  console.log(`${g.id.padEnd(22)} ${linha.fechaP50}/${linha.fechaP90} · P90 ${linha.p90TotalMin} (fora ${linha.p90ForaMin} dentro ${linha.p90DentroMin}) · dentro ${linha.dentroMax} · ring3 ${linha.ring3Max} · fome ${linha.fomeVermelhasMin} · estouro ${linha.estouroFilas} · perdidos ${linha.perdidos} · ${linha.nota} · ${Date.now() - t0} ms`);
}

// geometria das fitas nas duas atribuições (sem checkpoint: cauda da fila da mesa)
const mDec = Modelo.montar(base, mrvs, semCp(cenBase(dec)), dec);
const mGeo = Modelo.montar(base, mrvs, semCp(cenBase(decGeo)), decGeo);
const geo = {decisao: geometriaFitas(mDec, "atribuição da decisão (por quota do Ring 3)"),
             geografica: geometriaFitas(mGeo, "atribuição por parede (oeste A, norte B, leste C)")};
for (const k of Object.keys(geo)) {
  const g = geo[k];
  console.log(`\n${g.rotulo}: fita por mesa ${g.fitaPorMesa_m.toFixed(0)} m · troncos ${g.fitaTroncos_m.toFixed(0)} m · cruzamentos entre entradas ${g.cruzEntre} (troncos ${g.cruzTroncos}) · fita × saída ${g.cruzSaida} · deseq ${g.desequilibrio.toFixed(2)}`);
  for (const e of g.porEntrada) console.log(`  ${e.entrada} (${e.porta}): mesas ${e.mesas.join(",")} · ${e.esperados} esperados (Ring 3 ${e.capRing3}) · paredes ${e.paredes.join("/")} · ${e.nTroncos} troncos ${e.fitaTroncos_m.toFixed(0)} m · caminho médio ${e.distMedia_m.toFixed(1)} m`);
}

// planta resolvida para o desenho (arranjo Três polos, sem checkpoint)
const planta = {
  salao: base.salao, modulo: base.modulo, portas: base.portas, zonasProtegidas: base.cenarios.A.zonas,
  mesas: mDec.mesas.map(x => ({mrv: x.mrv, x: x.pos.x, y: x.pos.y, rot: x.pos.rot, lado: x.pos.lado, classe: x.classeDecisao, cor: x.cor,
                              frente: x.frente, cauda: x.cauda, L: x.L, esperados: Math.round(x.esperados), secao: x.secao, agregada: x.agregada,
                              entradaDecisao: mDec.zonas[x.zona].letra, entradaGeo: mGeo.zonas[mGeo.mesas.find(q => q.mrv === x.mrv).zona].letra, saida: x.saida})),
  entradas: mDec.zonas.map(z => ({letra: z.letra, porta: z.porta, centro: z.portaCentro, cor: z.cor})),
  checkpointClaude: {dist: 16, pontos: Modelo.montar(base, mrvs, cenBase(dec), dec).zonas.map(z => z.checkpoint)},
};
const saida = {geradoEm: new Date().toISOString(), runs: RUNS, arranjo: cenBase(dec).salao.nome, resultados, geometria: geo, planta,
               premissas: {curvaChegada: "a do simulador (fatias de 30 min, 7h–17h)", identificacao: 45, voto: 30, cv: 0.35, velocidade: 1.2, passoFila: 0.6,
                           semCheckpoint: "10 s para ler a sinalização na porta + caminhada direta; erro de sinalização opcional (cen.sinalizacao)"}};
fs.writeFileSync(path.join(RAIZ, "saidas/fitas_piso.json"), JSON.stringify(saida, null, 1));
console.log("\ngravado saidas/fitas_piso.json");
