/* Simulador de fluxo do Hall 2 — motor de simulação.
 *
 * Roda no navegador (global `Modelo`) e em Node (module.exports). Não depende
 * de DOM. Recebe a base da prancheta (salão, portas, módulo, posições das 28
 * mesas), o mapeamento MRV → seção e um cenário de premissas; devolve o
 * resumo estático (cargas, geometria, cruzamentos) e o resultado de N dias
 * simulados por eventos discretos, eleitor a eleitor.
 *
 * Estágios do eleitor:
 *   chegada ao Ring 3 → triagem → fila da área → porta (liberação controlada)
 *   → buffer → checkpoint → fila da mesa → mesa (identificação por caderno)
 *   → urna → saída.
 */
(function (raiz) {
"use strict";

/* ------------------------------------------------------------------ */
/* Constantes do modelo (premissas fixas, iguais para todos os cenários) */
/* ------------------------------------------------------------------ */
const VEL = 1.2;               // m/s, caminhada em salão com gente
const PASSO_FILA = 0.6;        // m por pessoa numa fila em unifila
const ABERTURA = 8 * 3600;     // 8h00
const ENCERRAMENTO = 17 * 3600;// 17h00: quem chegou antes vota
const INICIO_CURVA = 7 * 3600; // primeiras chegadas às 7h00
const MEIA_HORA = 1800;
const LIMITE_SEPARADORES = 200;  // m de fita contratados (100 unifilas)

/* Curva fixa de chegada ao local, em fatias de 30 min a partir das 7h00.
 * É chegada, não votação: em 2022 o voto aconteceu bem depois da chegada
 * porque as filas eram longas. Forma apoiada no levantamento qualitativo
 * (branch claude/eleicoes-brasileiras-horarios-pico-210a6l): fila formada
 * de 1h30 a 2h antes da abertura (Nova York, Lisboa, Dublin em 2022), maior
 * volume nas primeiras horas, vale entre 12h e 15h e repique de retardatários
 * perto das 17h. Pesos somam 100. Não há estatística oficial por hora; os
 * logs de urna de 2022 permitiriam calibrar. */
const CURVA_CHEGADA = [
  /* 7h00 */ 3, /* 7h30 */ 5,
  /* 8h00 */ 7, /* 8h30 */ 7,
  /* 9h00 */ 7.5, /* 9h30 */ 7,
  /* 10h00 */ 7, /* 10h30 */ 6.5,
  /* 11h00 */ 6, /* 11h30 */ 5.5,
  /* 12h00 */ 4.5, /* 12h30 */ 4,
  /* 13h00 */ 3.5, /* 13h30 */ 3.5,
  /* 14h00 */ 3.5, /* 14h30 */ 3.5,
  /* 15h00 */ 4, /* 15h30 */ 4,
  /* 16h00 */ 4.5, /* 16h30 */ 3.5,
];

/* Taxas de comparecimento por origem do eleitor. "medio" replica 2022
 * (74 % nas seções de Dublin, ~50 % nas do interior). */
const COMPARECIMENTO = {
  pequeno: {dublin: 0.62, interior: 0.40, rotulo: "pequeno"},
  medio:   {dublin: 0.74, interior: 0.50, rotulo: "médio (2022)"},
  grande:  {dublin: 0.84, interior: 0.60, rotulo: "grande"},
};

const CLASSES = ["leve", "media", "pesada"];
function classeMesa(aptos){ return aptos > 700 ? "pesada" : (aptos > 500 ? "media" : "leve"); }
const ROTULO_CLASSE = {leve: "leve (≤ 500 aptos)", media: "média (501–700)", pesada: "pesada (> 700)"};

/* ------------------------------------------------------------------ */
/* Cenários de referência                                              */
/* ------------------------------------------------------------------ */
function cenarioPadrao(){
  return {
    nome: "Ponto de partida",
    salao: {base: "A", alteracoes: []},
    portas: {S1: "fechada", S3: "fechada", S4: "entrada", S5: "saida", S6: "entrada", S7: "fechada", S9: "fechada"},
    zonas: {inicio: 1, tamanhos: [16, 12], portas: ["S4", "S6"]},
    ordem: {inicioZona: 0, sentido: "horario"},
    checkpoint: {existe: true, dist: 8, filas: 2, atendentes: [2, 2], seg: 8},
    filaMesa: {leve: 3, media: 4, pesada: 5},
    liberacao: "buffer",
    porta: {vazao: 30},
    comparecimento: "medio",
    tempos: {identificacao: 45, voto: 30, cv: 0.35},
    ring3: {atendentes: 6, seg: 6, capacidade: 800},
    extras: {justificativas: 0.05},
    sim: {runs: 12, seed: 7},
  };
}

/* Escolhido por varredura em Node (simulador/varredura.js): entre 4.228
 * combinações de partição, portas, ordem e checkpoint, esta zera os
 * cruzamentos de saída com corredor de entrada, mantém as mesas pesadas sem
 * fome e cabe na fita contratada. Sobe as mesas 23 e 24 em 3,5 a 5 m para a
 * fila da mesa do recorte (slot 22) não invadir a mesa 23. */
function cenarioClaude(){
  const c = cenarioPadrao();
  c.nome = "Cenário Claude";
  c.salao = {base: "A", alteracoes: [{n: 23, y: 17.5}, {n: 24, y: 21.4}]};
  c.portas = {S1: "saida", S3: "fechada", S4: "entrada", S5: "entrada", S6: "entrada", S7: "fechada", S9: "saida"};
  c.zonas = {inicio: 1, tamanhos: [8, 12, 8], portas: ["S5", "S6", "S4"]};
  c.ordem = {inicioZona: 1, sentido: "horario"};
  c.checkpoint = {existe: true, dist: 14, filas: 2, atendentes: [2, 3, 2], seg: 8};
  c.filaMesa = {leve: 4, media: 5, pesada: 8};
  c.liberacao = "buffer";
  c.sim = {runs: 16, seed: 7};
  return c;
}

/* ------------------------------------------------------------------ */
/* Utilidades                                                          */
/* ------------------------------------------------------------------ */
function mulberry32(a){
  return function(){
    a |= 0; a = a + 0x6D2B79F5 | 0;
    let t = Math.imul(a ^ a >>> 15, 1 | a);
    t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
    return ((t ^ t >>> 14) >>> 0) / 4294967296;
  };
}
function lognormal(rnd, media, cv){
  if (!(cv > 0)) return () => media;
  const s2 = Math.log(1 + cv * cv), mu = Math.log(media) - s2 / 2, s = Math.sqrt(s2);
  return () => {
    let u = 0, v = 0;
    while (u === 0) u = rnd();
    while (v === 0) v = rnd();
    const z = Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v);
    return Math.exp(mu + s * z);
  };
}
function binomial(rnd, n, p){
  if (n > 60) {                   // aproximação normal, suficiente aqui
    let u = 0, v = 0;
    while (u === 0) u = rnd();
    while (v === 0) v = rnd();
    const z = Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v);
    return Math.max(0, Math.min(n, Math.round(n * p + z * Math.sqrt(n * p * (1 - p)))));
  }
  let k = 0; for (let i = 0; i < n; i++) if (rnd() < p) k++;
  return k;
}
const hipot = (a, b) => Math.hypot(b[0] - a[0], b[1] - a[1]);
const DIR = r => [Math.round(Math.cos(r * Math.PI / 180)), Math.round(Math.sin(r * Math.PI / 180))];
const CCW = ([x, y]) => [-y, x];
const percentil = (arr, p) => {
  if (!arr.length) return 0;
  const a = arr.slice().sort((x, y) => x - y);
  const i = Math.min(a.length - 1, Math.max(0, Math.round((a.length - 1) * p)));
  return a[i];
};
const mediana = arr => percentil(arr, 0.5);
const soma = arr => arr.reduce((s, v) => s + v, 0);
const hhmm = seg => {
  const h = Math.floor(seg / 3600), m = Math.floor((seg % 3600) / 60);
  return `${h}h${m < 10 ? "0" : ""}${m}`;
};
const minutos = seg => Math.round(seg / 60);

/* Fila com ponteiro de cabeça (evita shift O(n) nas filas grandes). */
class Fila {
  constructor(){ this.a = []; this.h = 0; }
  get length(){ return this.a.length - this.h; }
  push(v){ this.a.push(v); }
  peek(){ return this.a[this.h]; }
  shift(){
    const v = this.a[this.h++];
    if (this.h > 1024 && this.h * 2 > this.a.length) { this.a = this.a.slice(this.h); this.h = 0; }
    return v;
  }
}
/* Heap binário de eventos: [tempo, seq, tipo, dado]. */
class Heap {
  constructor(){ this.a = []; this.seq = 0; }
  get length(){ return this.a.length; }
  push(t, tipo, dado){
    const e = [t, this.seq++, tipo, dado]; const a = this.a; a.push(e);
    let i = a.length - 1;
    while (i > 0) {
      const p = (i - 1) >> 1;
      if (a[p][0] < e[0] || (a[p][0] === e[0] && a[p][1] < e[1])) break;
      a[i] = a[p]; i = p;
    }
    a[i] = e;
  }
  pop(){
    const a = this.a, top = a[0], fim = a.pop();
    if (a.length) {
      let i = 0; const n = a.length;
      for (;;) {
        let l = 2 * i + 1, r = l + 1, m = i;
        let mi = fim;
        if (l < n && (a[l][0] < mi[0] || (a[l][0] === mi[0] && a[l][1] < mi[1]))) { m = l; mi = a[l]; }
        if (r < n && (a[r][0] < mi[0] || (a[r][0] === mi[0] && a[r][1] < mi[1]))) { m = r; mi = a[r]; }
        if (m === i) break;
        a[i] = a[m]; i = m;
      }
      a[i] = fim;
    }
    return top;
  }
}

/* Segmentos e retângulos (para cruzamentos e conflitos de fila). */
function cruzam(p1, p2, p3, p4){
  const d = (a, b, c) => (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]);
  const d1 = d(p3, p4, p1), d2 = d(p3, p4, p2), d3 = d(p1, p2, p3), d4 = d(p1, p2, p4);
  return ((d1 > 0) !== (d2 > 0)) && ((d3 > 0) !== (d4 > 0)) && d1 !== 0 && d2 !== 0 && d3 !== 0 && d4 !== 0;
}
function segmentoBateRect(a, b, r){
  const dentro = p => p[0] > r[0] && p[0] < r[2] && p[1] > r[1] && p[1] < r[3];
  if (dentro(a) || dentro(b)) return true;
  const c = [[r[0], r[1]], [r[2], r[1]], [r[2], r[3]], [r[0], r[3]]];
  for (let i = 0; i < 4; i++) if (cruzam(a, b, c[i], c[(i + 1) % 4])) return true;
  return false;
}
const bate = (a, b, t = 1e-6) => a[0] < b[2] - t && b[0] < a[2] - t && a[1] < b[3] - t && b[1] < a[3] - t;

/* ------------------------------------------------------------------ */
/* Geometria herdada da prancheta                                      */
/* ------------------------------------------------------------------ */
function mesasDoCenario(base, cen){
  const orig = base.cenarios[cen.salao.base || "A"].mrvs.map(m => ({...m}));
  for (const alt of (cen.salao.alteracoes || [])) {
    const m = orig.find(q => q.n === alt.n);
    if (m) Object.assign(m, alt);
  }
  return orig;
}
function corpoRect(M, m){
  const d = DIR(m.rot), p = CCW(d), xs = [], ys = [];
  for (const u of [0, M.prof]) for (const v of [-M.larg / 2, M.larg / 2]) {
    xs.push(m.x + d[0] * u + p[0] * v); ys.push(m.y + d[1] * u + p[1] * v);
  }
  return [Math.min(...xs), Math.min(...ys), Math.max(...xs), Math.max(...ys)];
}
/* Ponto em que a fila da mesa começa (0,3 m à frente da mesa dos mesários). */
function frenteMesa(M, m){
  const d = DIR(m.rot);
  return [m.x + d[0] * (M.prof + 0.3), m.y + d[1] * (M.prof + 0.3)];
}
function caudaFila(M, m, L){
  const d = DIR(m.rot), f = frenteMesa(M, m);
  return [f[0] + d[0] * L * PASSO_FILA, f[1] + d[1] * L * PASSO_FILA];
}
function centroPorta(p){ return [(p.x1 + p.x2) / 2, (p.y1 + p.y2) / 2]; }

/* Zonas = arcos contíguos da sequência perimetral de slots (1→28 horário
 * a partir do canto noroeste). */
function slotsDasZonas(zonas){
  const n = 28, seq = [];
  const ini = ((zonas.inicio || 1) - 1 + n) % n;
  for (let i = 0; i < n; i++) seq.push(((ini + i) % n) + 1);
  const out = []; let k = 0;
  for (const tam of zonas.tamanhos) { out.push(seq.slice(k, k + tam)); k += tam; }
  return out;
}
/* Numeração MRV por slot: contígua dentro de cada zona, começando na zona
 * escolhida e seguindo o perímetro no sentido dado. */
function mapaMrv(zonasSlots, ordem){
  if (ordem.manual) return {...ordem.manual};
  const plano = [];
  const z0 = Math.min(ordem.inicioZona || 0, zonasSlots.length - 1);
  const ordemZonas = [];
  for (let i = 0; i < zonasSlots.length; i++) ordemZonas.push((z0 + i) % zonasSlots.length);
  if (ordem.sentido === "antihorario") {
    // percorre as zonas em ordem inversa e cada zona de trás para frente
    const inv = [z0];
    for (let i = 1; i < zonasSlots.length; i++) inv.push((z0 - i + zonasSlots.length) % zonasSlots.length);
    for (const z of inv) plano.push(...zonasSlots[z].slice().reverse());
  } else {
    for (const z of ordemZonas) plano.push(...zonasSlots[z]);
  }
  const mapa = {};
  plano.forEach((slot, i) => { mapa[slot] = i + 1; });
  return mapa;
}

/* ------------------------------------------------------------------ */
/* Montagem do cenário resolvido (estático)                            */
/* ------------------------------------------------------------------ */
function montar(base, mrvsDados, cen){
  const M = base.modulo;
  const mesasPos = mesasDoCenario(base, cen);
  const zonasSlots = slotsDasZonas(cen.zonas);
  const mapa = mapaMrv(zonasSlots, cen.ordem);
  const porMrv = {}; for (const r of mrvsDados.mrvs) porMrv[r.mrv] = r;
  const portas = {}; for (const p of base.portas) portas[p.id] = p;
  const taxa = COMPARECIMENTO[cen.comparecimento] || COMPARECIMENTO.medio;
  const avisos = [];

  // portas de saída
  const saidas = Object.keys(cen.portas).filter(id => cen.portas[id] === "saida" && portas[id]);
  const entradas = Object.keys(cen.portas).filter(id => cen.portas[id] === "entrada" && portas[id]);

  // zonas
  const zonas = zonasSlots.map((slots, z) => {
    let pid = cen.zonas.portas[z];
    if (!pid || cen.portas[pid] !== "entrada") {
      avisos.push(`Zona ${z + 1} sem porta de entrada válida; usando ${entradas[0] || "S5"}.`);
      pid = entradas[0] || "S5";
    }
    const porta = portas[pid], cp = centroPorta(porta);
    return {idx: z, nome: `Zona ${String.fromCharCode(65 + z)}`, letra: String.fromCharCode(65 + z),
            slots, porta: pid, portaCentro: cp, portaLarg: porta.larg};
  });
  // checkpoint de cada zona: à frente da porta, à distância escolhida.
  // Se duas zonas dividem a porta, afasta 1,5 m lateralmente.
  const usoPorta = {};
  for (const z of zonas) {
    const k = usoPorta[z.porta] = (usoPorta[z.porta] || 0) + 1;
    const dx = (k - 1) * 1.5 * (k % 2 ? 1 : -1);
    z.checkpoint = cen.checkpoint.existe ? [z.portaCentro[0] + dx, cen.checkpoint.dist] : null;
    z.dividePorta = false;
  }
  for (const z of zonas) if (usoPorta[z.porta] > 1) z.dividePorta = true;

  // mesas
  const mesas = mesasPos.map(pos => {
    const mrv = mapa[pos.n], dados = porMrv[mrv];
    const zona = zonas.find(z => z.slots.includes(pos.n));
    const classe = classeMesa(dados.aptos);
    const L = Math.max(1, Math.round(cen.filaMesa[classe] || 3));
    const frente = frenteMesa(M, pos), cauda = caudaFila(M, pos, L);
    const esperados = dados.aptos_dublin * taxa.dublin + dados.aptos_interior * taxa.interior;
    const saida = saidas.length
      ? saidas.map(id => ({id, d: hipot(frente, centroPorta(portas[id]))})).sort((a, b) => a.d - b.d)[0]
      : {id: zona.porta, d: hipot(frente, zona.portaCentro)};
    const distCp = zona.checkpoint ? hipot(zona.checkpoint, frente) : hipot(zona.portaCentro, frente);
    return {slot: pos.n, pos, mrv, secao: dados.principal, agregada: dados.agregada,
            origemAgregada: dados.origem_agregada, aptos: dados.aptos,
            aptosDublin: dados.aptos_dublin, aptosInterior: dados.aptos_interior,
            classe, L, zona: zona.idx, frente, cauda, esperados, saida: saida.id, distSaida: saida.d,
            distCp, corpo: corpoRect(M, pos)};
  });
  for (const z of zonas) {
    z.mesas = mesas.filter(m => m.zona === z.idx).map(m => m.slot);
    z.esperados = soma(mesas.filter(m => m.zona === z.idx).map(m => m.esperados));
    z.aptos = soma(mesas.filter(m => m.zona === z.idx).map(m => m.aptos));
    z.mrvs = mesas.filter(m => m.zona === z.idx).map(m => m.mrv).sort((a, b) => a - b);
    z.faixaMrv = `${z.mrvs[0]}–${z.mrvs[z.mrvs.length - 1]}`;
    z.capBuffer = cen.checkpoint.existe
      ? Math.max(1, Math.floor(cen.checkpoint.dist * Math.max(1, cen.checkpoint.filas) / PASSO_FILA))
      : soma(mesas.filter(m => m.zona === z.idx).map(m => m.L));
    z.atendentesCp = cen.checkpoint.existe
      ? Math.max(1, Math.round((Array.isArray(cen.checkpoint.atendentes)
          ? cen.checkpoint.atendentes[z.idx] : cen.checkpoint.atendentes) || 1))
      : 0;
    z.distCpMedia = soma(mesas.filter(m => m.zona === z.idx).map(m => m.distCp)) / z.mesas.length;
    z.distCpMax = Math.max(...mesas.filter(m => m.zona === z.idx).map(m => m.distCp));
    // retângulo do buffer (entre porta e checkpoint), para conflitos de fila
    const larg = Math.max(1, cen.checkpoint.filas) * 1.0 + 1.0;
    z.bufferRect = cen.checkpoint.existe
      ? [z.portaCentro[0] - larg / 2, 0, z.portaCentro[0] + larg / 2, cen.checkpoint.dist] : null;
  }
  // carga por porta (zonas podem dividir porta)
  const cargaPorta = {};
  for (const z of zonas) cargaPorta[z.porta] = (cargaPorta[z.porta] || 0) + z.esperados;
  const cargas = Object.values(cargaPorta);
  const desequilibrio = cargas.length > 1 ? Math.max(...cargas) / Math.min(...cargas) : 1;

  // separadores: filas das mesas + corredores até o checkpoint
  const fitaMesas = soma(mesas.map(m => m.L * PASSO_FILA));
  const fitaBuffer = cen.checkpoint.existe
    ? soma(zonas.map(z => cen.checkpoint.dist * Math.max(1, cen.checkpoint.filas))) : 0;
  const separadores = fitaMesas + fitaBuffer;

  // conflitos das filas das mesas com buffers, zonas protegidas, outras mesas
  const zonasProt = base.cenarios[cen.salao.base || "A"].zonas;
  const conflitos = [];
  for (const m of mesas) {
    const a = m.frente, b = m.cauda;
    for (const z of zonas) if (z.bufferRect && segmentoBateRect(a, b, z.bufferRect))
      conflitos.push({mesa: m.mrv, com: `corredor porta→checkpoint da ${z.nome}`});
    for (const zp of zonasProt) if (segmentoBateRect(a, b, zp.rect))
      conflitos.push({mesa: m.mrv, com: zp.rotulo.split(" · ")[0]});
    for (const o of mesas) if (o.slot !== m.slot && segmentoBateRect(a, b, o.corpo))
      conflitos.push({mesa: m.mrv, com: `mesa ${o.mrv}`});
    if (b[0] < 0 || b[1] < 0 || b[0] > base.salao.largura || b[1] > base.salao.altura
        || bate([Math.min(a[0], b[0]), Math.min(a[1], b[1]), Math.max(a[0], b[0]), Math.max(a[1], b[1])], base.salao.recorte))
      conflitos.push({mesa: m.mrv, com: "fora do salão"});
  }

  // cruzamentos. O que importa é a saída cortar um corredor denso de entrada
  // (porta→checkpoint, onde há fila parada). Cruzar as linhas do leque
  // checkpoint→mesa é gente andando contra gente andando: informativo.
  const corredores = zonas.filter(z => z.checkpoint).map(z => ({zona: z.idx, rect: z.bufferRect, a: z.portaCentro, b: z.checkpoint}));
  let eleitoresCruzam = 0; const mesasCruzam = [];
  for (const m of mesas) {
    const a = m.frente, b = centroPorta(portas[m.saida]);
    const corta = corredores.some(c => segmentoBateRect(a, b, c.rect) || cruzam(a, b, c.a, c.b));
    if (corta) { eleitoresCruzam += m.esperados; mesasCruzam.push(m.mrv); }
  }
  const fracaoCruza = mesas.length ? eleitoresCruzam / soma(mesas.map(m => m.esperados)) : 0;
  let paresLeque = 0, paresTotal = 0;
  for (const e of mesas) for (const sm of mesas) {
    if (e.slot === sm.slot) continue;
    paresTotal++;
    const z = zonas[e.zona];
    if (cruzam(z.checkpoint || z.portaCentro, e.frente, sm.frente, centroPorta(portas[sm.saida]))) paresLeque++;
  }
  const fracaoLeque = paresTotal ? paresLeque / paresTotal : 0;
  const mesmaPorta = zonas.filter(z => saidas.includes(z.porta)).map(z => z.porta);

  return {cen, base, M, zonas, mesas, mapa, portas, saidas, entradas, taxa,
          esperadosTotal: soma(mesas.map(m => m.esperados)),
          aptosTotal: soma(mesas.map(m => m.aptos)),
          cargaPorta, desequilibrio, separadores, fitaMesas, fitaBuffer, conflitos,
          eleitoresCruzam, fracaoCruza, mesasCruzam, fracaoLeque, mesmaPorta, avisos,
          curva: CURVA_CHEGADA.slice(), limiteSeparadores: LIMITE_SEPARADORES};
}

/* ------------------------------------------------------------------ */
/* Um dia simulado                                                     */
/* ------------------------------------------------------------------ */
const EV = {CHEGADA: 1, TRIAGEM_FIM: 2, PORTA_TICK: 3, CP_CHEGADA: 4, CP_FIM: 5,
            MESA_CHEGADA: 6, ID_FIM: 7, VOTO_FIM: 8, SAIDA_FIM: 9, AMOSTRA: 10};

function simularDia(mont, seed){
  const {cen, zonas, mesas} = mont;
  const rnd = mulberry32(seed);
  const tId = lognormal(rnd, cen.tempos.identificacao, cen.tempos.cv);
  const tVoto = lognormal(rnd, cen.tempos.voto, cen.tempos.cv);
  const tCp = lognormal(rnd, cen.checkpoint.seg || 8, 0.3);
  const tTri = lognormal(rnd, cen.ring3.seg || 8, 0.3);
  const comCp = !!cen.checkpoint.existe;
  const politica = cen.liberacao || "buffer";
  const gapPorta = 60 / Math.max(1, cen.porta.vazao || 30);

  // curva acumulada
  const acum = []; let s = 0;
  for (const w of CURVA_CHEGADA) { s += w; acum.push(s); }
  const sorteiaChegada = () => {
    const u = rnd() * s; let i = 0;
    while (acum[i] < u) i++;
    return INICIO_CURVA + i * MEIA_HORA + rnd() * MEIA_HORA;
  };

  // eleitores
  const porSlot = {}; mesas.forEach(m => { porSlot[m.slot] = m; });
  const eleitores = [];
  for (const m of mesas) {
    const nD = binomial(rnd, m.aptosDublin, mont.taxa.dublin);
    const nI = binomial(rnd, m.aptosInterior, mont.taxa.interior);
    const n = nD + nI;
    const nJ = Math.round(n * (cen.extras.justificativas || 0));
    for (let i = 0; i < n + nJ; i++)
      eleitores.push({id: eleitores.length, mesa: m.slot, zona: m.zona, just: i >= n,
                      tA: sorteiaChegada(), tR: -1, tM: -1, tI: -1, tV: -1});
  }
  eleitores.sort((a, b) => a.tA - b.tA);

  const heap = new Heap();
  for (const e of eleitores) heap.push(e.tA, EV.CHEGADA, e);

  // estado
  const nz = zonas.length;
  const triFila = new Fila(); let triOcupados = 0;
  const areaFila = zonas.map(() => new Fila());
  const proxLib = {}; const tickAgendado = zonas.map(() => false);
  const buffer = new Array(nz).fill(0);          // porta→checkpoint (inclui retidos)
  const dentroZona = new Array(nz).fill(0);       // dentro do salão, nesta zona
  const cpFila = zonas.map(() => new Fila()); const cpOcup = new Array(nz).fill(0);
  const cpAtend = new Array(nz).fill(0), cpServ = new Array(nz).fill(0);
  const est = {}; // por slot
  for (const m of mesas) est[m.slot] = {fila: [], transito: 0, retidos: new Fila(), mesarioLivre: true,
    urnaLivre: true, esperaUrna: null, votos: 0, just: 0, fecha: 0, ocioso: 0, fome: 0, urnaBusy: 0,
    idBusy: 0, filaMax: 0, estouro: 0, retidosMax: 0};
  let dentroTotal = 0, dentroMax = 0, restantes = eleitores.length;
  const ring3Max = new Array(nz).fill(0), bufferMax = new Array(nz).fill(0), cpFilaMax = new Array(nz).fill(0);
  let ring3TotalMax = 0, ring3Estouro = 0, bufferEstouro = new Array(nz).fill(0);
  let triFilaMax = 0, triBusy = 0, amostrasAberto = 0, amostrasTri = 0;
  const liberadosPorta = {};
  const saidasPorta = {};
  const linha = {t: [], ring3: zonas.map(() => []), buffer: zonas.map(() => []), cp: zonas.map(() => []),
                 dentro: [], votados: [], mesaFila: mesas.map(() => []), mesaEstado: mesas.map(() => [])};
  const idxSlot = {}; mesas.forEach((m, i) => { idxSlot[m.slot] = i; });
  let votados = 0;

  const slotsLivres = slot => { const e = est[slot]; return porSlot[slot].L - e.fila.length - e.transito; };

  function podeLiberar(z, v){
    if (politica === "livre") return true;
    const zz = zonas[z];
    const capOk = comCp ? buffer[z] < zz.capBuffer : dentroZona[z] < zz.capBuffer;
    if (!capOk) return false;
    if (politica === "mesa") return slotsLivres(v.mesa) - est[v.mesa].retidos.length > 0;
    return true;
  }
  function tentaLiberar(z, t){
    const zz = zonas[z], porta = zz.porta;
    if (t < ABERTURA - 1e-9) {
      if (!tickAgendado[z]) { tickAgendado[z] = true; heap.push(ABERTURA, EV.PORTA_TICK, z); }
      return;
    }
    while (areaFila[z].length) {
      const prox = proxLib[porta] || 0;
      if (prox > t + 1e-9) {
        if (!tickAgendado[z]) { tickAgendado[z] = true; heap.push(prox, EV.PORTA_TICK, z); }
        return;
      }
      const v = areaFila[z].peek();
      if (!podeLiberar(z, v)) return;
      areaFila[z].shift();
      proxLib[porta] = t + gapPorta;
      liberadosPorta[porta] = (liberadosPorta[porta] || 0) + 1;
      v.tR = t; dentroTotal++; dentroZona[z]++;
      if (dentroTotal > dentroMax) dentroMax = dentroTotal;
      if (comCp) {
        buffer[z]++;
        heap.push(t + cen.checkpoint.dist / VEL, EV.CP_CHEGADA, v);
      } else {
        est[v.mesa].transito++;
        heap.push(t + 10 + porSlot[v.mesa].distCp / VEL, EV.MESA_CHEGADA, v);
      }
    }
  }
  function tentaTriagem(t){
    while (triOcupados < Math.max(1, cen.ring3.atendentes) && triFila.length) {
      const v = triFila.shift(); triOcupados++;
      heap.push(t + tTri(), EV.TRIAGEM_FIM, v);
    }
  }
  function despacha(v, t){
    const z = v.zona, m = v.mesa;
    if (slotsLivres(m) > 0) {
      est[m].transito++; buffer[z]--;
      heap.push(t + porSlot[m].distCp / VEL, EV.MESA_CHEGADA, v);
      tentaLiberar(z, t);
    } else {
      est[m].retidos.push(v);
      if (est[m].retidos.length > est[m].retidosMax) est[m].retidosMax = est[m].retidos.length;
    }
  }
  function tentaCp(z, t){
    while (cpOcup[z] < zonas[z].atendentesCp && cpFila[z].length) {
      const v = cpFila[z].shift(); cpOcup[z]++;
      heap.push(t + tCp(), EV.CP_FIM, v);
    }
  }
  function liberaRetidos(m, t){
    const e = est[m];
    while (e.retidos.length && slotsLivres(m) > 0) {
      const v = e.retidos.shift();
      e.transito++; buffer[v.zona]--;
      heap.push(t + porSlot[m].distCp / VEL, EV.MESA_CHEGADA, v);
      tentaLiberar(v.zona, t);
    }
  }
  function tentaMesa(m, t){
    const e = est[m];
    if (e.mesarioLivre && e.fila.length) {
      const v = e.fila.shift(); v.tI = t; e.mesarioLivre = false;
      heap.push(t + tId() * (v.just ? 1.5 : 1), EV.ID_FIM, v);
      liberaRetidos(m, t);
    }
  }
  function sai(v, t){
    const m = porSlot[v.mesa];
    dentroZona[v.zona]--; restantes--;
    saidasPorta[m.saida] = (saidasPorta[m.saida] || 0) + 1;
    heap.push(t + m.distSaida / VEL, EV.SAIDA_FIM, v);
    if (!comCp) tentaLiberar(v.zona, t);
  }

  heap.push(INICIO_CURVA, EV.AMOSTRA, null);
  let tAnterior = INICIO_CURVA;
  while (heap.length) {
    const [t, , tipo, d] = heap.pop();
    switch (tipo) {
      case EV.CHEGADA:
        triFila.push(d); if (triFila.length > triFilaMax) triFilaMax = triFila.length;
        tentaTriagem(t); break;
      case EV.TRIAGEM_FIM:
        triOcupados--; areaFila[d.zona].push(d); tentaTriagem(t); tentaLiberar(d.zona, t); break;
      case EV.PORTA_TICK:
        tickAgendado[d] = false; tentaLiberar(d, t); break;
      case EV.CP_CHEGADA:
        cpFila[d.zona].push(d); tentaCp(d.zona, t); break;
      case EV.CP_FIM:
        cpOcup[d.zona]--; cpServ[d.zona]++; despacha(d, t); tentaCp(d.zona, t); break;
      case EV.MESA_CHEGADA: {
        const e = est[d.mesa]; e.transito--; e.fila.push(d); d.tM = t;
        if (e.fila.length > e.filaMax) e.filaMax = e.fila.length;
        if (e.fila.length > porSlot[d.mesa].L) e.estouro++;
        tentaMesa(d.mesa, t); break;
      }
      case EV.ID_FIM: {
        const e = est[d.mesa];
        if (d.just) { d.tV = t; e.just++; e.fecha = t; e.mesarioLivre = true; sai(d, t); tentaMesa(d.mesa, t); }
        else if (e.urnaLivre) { e.urnaLivre = false; heap.push(t + tVoto(), EV.VOTO_FIM, d); e.mesarioLivre = true; tentaMesa(d.mesa, t); }
        else { e.esperaUrna = d; }
        break;
      }
      case EV.VOTO_FIM: {
        const e = est[d.mesa]; d.tV = t; e.votos++; votados++; e.fecha = t; sai(d, t);
        if (e.esperaUrna) { const w = e.esperaUrna; e.esperaUrna = null; heap.push(t + tVoto(), EV.VOTO_FIM, w); e.mesarioLivre = true; tentaMesa(d.mesa, t); }
        else e.urnaLivre = true;
        break;
      }
      case EV.SAIDA_FIM: dentroTotal--; break;
      case EV.AMOSTRA: {
        linha.t.push(t);
        let ring3Total = triFila.length;
        for (let z = 0; z < nz; z++) {
          const r = areaFila[z].length; ring3Total += r;
          if (r > ring3Max[z]) ring3Max[z] = r;
          if (buffer[z] > bufferMax[z]) bufferMax[z] = buffer[z];
          if (buffer[z] > zonas[z].capBuffer) bufferEstouro[z] += 60;
          if (cpFila[z].length > cpFilaMax[z]) cpFilaMax[z] = cpFila[z].length;
          if (t >= ABERTURA && restantes > 0) cpAtend[z] += cpOcup[z];
          linha.ring3[z].push(r); linha.buffer[z].push(buffer[z]); linha.cp[z].push(cpFila[z].length);
        }
        if (ring3Total > ring3TotalMax) ring3TotalMax = ring3Total;
        if (ring3Total > (cen.ring3.capacidade || 1e9)) ring3Estouro += 60;
        if (ring3Total > 0 || triOcupados > 0) { triBusy += triOcupados; amostrasTri++; }
        if (t >= ABERTURA && restantes > 0) amostrasAberto++;
        linha.dentro.push(dentroTotal); linha.votados.push(votados);
        for (const m of mesas) {
          const e = est[m.slot];
          const ocioso = e.mesarioLivre && e.urnaLivre && !e.fila.length;
          let cod = 0; // 0 ocioso, 1 identificando, 2 identificando+urna, 3 só urna, 4 bloqueado
          if (!e.mesarioLivre && !e.urnaLivre) cod = e.esperaUrna ? 4 : 2;
          else if (!e.mesarioLivre) cod = 1;
          else if (!e.urnaLivre) cod = 3;
          if (t >= ABERTURA && restantes > 0) {
            if (ocioso) e.ocioso += 60;
            if (ocioso && (areaFila[m.zona].length > 0 || e.retidos.length > 0)) e.fome += 60;
          }
          if (t >= ABERTURA && t < ENCERRAMENTO) {
            if (!e.urnaLivre) e.urnaBusy += 60;
            if (!e.mesarioLivre) e.idBusy += 60;
          }
          linha.mesaFila[idxSlot[m.slot]].push(e.fila.length + e.transito);
          linha.mesaEstado[idxSlot[m.slot]].push(cod);
        }
        if (restantes > 0 || dentroTotal > 0) heap.push(t + 60, EV.AMOSTRA, null);
        break;
      }
    }
    tAnterior = t;
  }

  // agregados do dia
  const esperaFora = [], esperaDentro = [], total = [];
  for (const v of eleitores) if (v.tV >= 0) {
    esperaFora.push(v.tR - v.tA); esperaDentro.push(v.tI - v.tR); total.push(v.tV - v.tA);
  }
  const fechaUltima = Math.max(...mesas.map(m => est[m.slot].fecha));
  const abertoSeg = ENCERRAMENTO - ABERTURA;
  const nAmostrasAberto = abertoSeg / 60;
  const porMesa = mesas.map(m => {
    const e = est[m.slot];
    return {slot: m.slot, mrv: m.mrv, zona: m.zona, classe: m.classe, votos: e.votos, just: e.just,
            fecha: e.fecha, ocioso: e.ocioso, fome: e.fome, ocupUrna: e.urnaBusy / abertoSeg,
            ocupMesario: e.idBusy / abertoSeg, filaMax: e.filaMax, estouro: e.estouro, retidosMax: e.retidosMax};
  });
  const porZona = zonas.map((z, i) => ({
    idx: i, ring3Max: ring3Max[i], bufferMax: bufferMax[i], capBuffer: z.capBuffer,
    bufferEstouroMin: bufferEstouro[i] / 60, cpFilaMax: cpFilaMax[i],
    cpOcupacao: comCp ? cpAtend[i] / (Math.max(1, amostrasAberto) * Math.max(1, z.atendentesCp)) : 0,
    cpServ: cpServ[i], liberados: liberadosPorta[z.porta] || 0,
    fecha: Math.max(...porMesa.filter(m => m.zona === i).map(m => m.fecha)),
  }));
  return {
    seed, eleitores: eleitores.length, votos: votados, justificativas: eleitores.filter(v => v.just).length,
    fechaUltima, porMesa, porZona, linha,
    esperaForaP50: mediana(esperaFora), esperaForaP90: percentil(esperaFora, 0.9), esperaForaMax: Math.max(0, ...esperaFora),
    esperaDentroP50: mediana(esperaDentro), esperaDentroP90: percentil(esperaDentro, 0.9),
    totalP50: mediana(total), totalP90: percentil(total, 0.9), totalMax: Math.max(0, ...total),
    dentroMax, ring3TotalMax, ring3EstouroMin: ring3Estouro / 60, triFilaMax,
    triOcupacao: triBusy / (Math.max(1, amostrasTri) * Math.max(1, cen.ring3.atendentes)),
    fomeTotalMin: soma(porMesa.map(m => m.fome)) / 60,
    fomePesadasMin: soma(porMesa.filter(m => m.classe === "pesada").map(m => m.fome)) / 60,
    estouroFilas: soma(porMesa.map(m => m.estouro)),
    saidasPorta, liberadosPorta,
  };
}

/* ------------------------------------------------------------------ */
/* Vários dias, agregação e vereditos                                  */
/* ------------------------------------------------------------------ */
function simular(base, mrvsDados, cen, opts = {}){
  const mont = montar(base, mrvsDados, cen);
  const runs = Math.max(1, Math.min(200, (cen.sim && cen.sim.runs) || 10));
  const seed = (cen.sim && cen.sim.seed) || 7;
  const dias = [];
  for (let i = 0; i < runs; i++) {
    dias.push(simularDia(mont, seed + i * 7919));
    if (opts.progresso) opts.progresso(i + 1, runs);
  }
  return agregar(mont, dias);
}

/* Agrega N dias simulados: medianas, percentis, vereditos e texto. */
function agregar(mont, dias){
  const runs = dias.length;
  // dia de referência: o de fechamento mediano
  const fechas = dias.map(d => d.fechaUltima);
  const medF = mediana(fechas);
  const ref = dias.reduce((a, b) => Math.abs(b.fechaUltima - medF) < Math.abs(a.fechaUltima - medF) ? b : a, dias[0]);

  const agg = chave => ({p50: mediana(dias.map(d => d[chave])), p90: percentil(dias.map(d => d[chave]), 0.9),
                         max: Math.max(...dias.map(d => d[chave])), min: Math.min(...dias.map(d => d[chave]))});
  const resumo = {
    runs, fechaUltima: agg("fechaUltima"), totalP90: agg("totalP90"), totalP50: agg("totalP50"),
    esperaForaP90: agg("esperaForaP90"), esperaDentroP90: agg("esperaDentroP90"),
    dentroMax: agg("dentroMax"), ring3TotalMax: agg("ring3TotalMax"), ring3EstouroMin: agg("ring3EstouroMin"),
    fomePesadasMin: agg("fomePesadasMin"), fomeTotalMin: agg("fomeTotalMin"), estouroFilas: agg("estouroFilas"),
    triOcupacao: agg("triOcupacao"), votos: agg("votos"), eleitores: agg("eleitores"),
  };
  // por mesa: mediana entre dias
  const porMesa = mont.mesas.map((m, i) => {
    const col = chave => mediana(dias.map(d => d.porMesa[i][chave]));
    return {slot: m.slot, mrv: m.mrv, zona: m.zona, classe: m.classe, secao: m.secao, aptos: m.aptos,
            esperados: m.esperados, L: m.L, votos: col("votos"), fecha: col("fecha"), fechaMax: Math.max(...dias.map(d => d.porMesa[i].fecha)),
            ocioso: col("ocioso"), fome: col("fome"), ocupUrna: col("ocupUrna"), ocupMesario: col("ocupMesario"),
            filaMax: Math.max(...dias.map(d => d.porMesa[i].filaMax)), estouro: col("estouro"), retidosMax: Math.max(...dias.map(d => d.porMesa[i].retidosMax))};
  });
  const porZona = mont.zonas.map((z, i) => {
    const col = chave => mediana(dias.map(d => d.porZona[i][chave]));
    const mx = chave => Math.max(...dias.map(d => d.porZona[i][chave]));
    return {idx: i, nome: z.nome, porta: z.porta, esperados: z.esperados, mesas: z.mesas.length, faixaMrv: z.faixaMrv,
            ring3Max: mx("ring3Max"), ring3P50: col("ring3Max"), bufferMax: mx("bufferMax"), capBuffer: z.capBuffer,
            bufferEstouroMin: col("bufferEstouroMin"), cpFilaMax: mx("cpFilaMax"), cpOcupacao: col("cpOcupacao"),
            atendentesCp: z.atendentesCp, fecha: col("fecha"), liberados: col("liberados")};
  });
  const vereditos = avaliar(mont, resumo, porMesa, porZona);
  const nota = vereditos.filter(v => v.status === "falha").length ? "falha"
    : (vereditos.filter(v => v.status === "atencao").length ? "atencao" : "ok");
  return {mont, dias, ref, resumo, porMesa, porZona, vereditos, nota, texto: narrar(mont, resumo, porMesa, porZona, vereditos)};
}

function avaliar(mont, r, porMesa, porZona){
  const V = [];
  const add = (id, titulo, status, valor, meta, porque) => V.push({id, titulo, status, valor, meta, porque});
  const nivel = (v, ok, at) => v <= ok ? "ok" : (v <= at ? "atencao" : "falha");

  // 1 fechamento
  const f = r.fechaUltima.p50, f90 = r.fechaUltima.p90;
  add("fecho", "Última mesa fecha", f90 <= 17.5 * 3600 ? "ok" : (f90 <= 18.5 * 3600 ? "atencao" : "falha"),
      `${hhmm(f)} (mediana) · ${hhmm(f90)} em dia ruim`, "até 17h30",
      f90 <= 17.5 * 3600 ? "Todas as mesas terminam perto do encerramento oficial."
        : "Mesas ainda votam depois das 17h30: a fila de quem chegou antes das 17h se arrasta e atrasa a apuração.");
  const tardias = porMesa.filter(m => m.fecha > 17.5 * 3600).sort((a, b) => b.fecha - a.fecha);
  if (tardias.length) V[V.length - 1].detalhe = `Mesas que passam de 17h30: ${tardias.slice(0, 8).map(m => `MRV ${m.mrv} (${hhmm(m.fecha)})`).join(", ")}${tardias.length > 8 ? "…" : ""}.`;

  // 2 fome nas pesadas
  const pes = porMesa.filter(m => m.classe === "pesada");
  const fomeMedia = pes.length ? soma(pes.map(m => m.fome)) / pes.length / 60 : 0;
  add("fome", "Mesas pesadas sem fome", nivel(fomeMedia, 10, 30), `${Math.round(fomeMedia)} min por mesa pesada`, "≤ 10 min",
      fomeMedia <= 10 ? "As mesas de mais de 700 aptos quase nunca ficaram paradas enquanto havia gente esperando fora."
        : "Mesas pesadas ficaram ociosas com fila no Ring 3: a fila da frente delas ou o despacho do checkpoint não alimentou a urna.");

  // 3 espera total
  const t90 = r.totalP90.p50 / 60;
  add("espera", "Espera do eleitor (P90)", nivel(t90, 45, 90), `${Math.round(t90)} min da chegada ao voto`, "≤ 45 min",
      `Fora: ${Math.round(r.esperaForaP90.p50 / 60)} min · dentro: ${Math.round(r.esperaDentroP90.p50 / 60)} min (P90). ` +
      (t90 <= 45 ? "Espera dentro do que se tolera num domingo de eleição." : "Nove em dez eleitores esperam mais do que isso; parte desiste."));

  // 4 buffer / porta
  const est = porZona.map(z => z.bufferEstouroMin);
  const estMax = Math.max(0, ...est);
  if (mont.cen.checkpoint.existe)
    add("buffer", "Fila interna não volta até a porta", estMax === 0 ? "ok" : (estMax <= 15 ? "atencao" : "falha"),
        estMax === 0 ? "nunca" : `${Math.round(estMax)} min acima do que cabe`, "0 min",
        mont.cen.liberacao === "livre" ? "Sem controle na porta, o espaço entre porta e checkpoint enche e a fila sai pela porta."
          : `Cabem ${porZona.map(z => `${z.capBuffer} na ${z.nome}`).join(", ")} entre porta e checkpoint; a liberação controlada respeita isso.`);

  // 5 checkpoint
  if (mont.cen.checkpoint.existe) {
    const pior = porZona.reduce((a, b) => b.cpOcupacao > a.cpOcupacao ? b : a, porZona[0]);
    add("checkpoint", "Checkpoint acompanha as mesas", nivel(pior.cpOcupacao, 0.8, 0.93),
        `${Math.round(pior.cpOcupacao * 100)} % de ocupação na ${pior.nome} · fila até ${pior.cpFilaMax}`, "≤ 80 %",
        pior.cpOcupacao <= 0.8 ? "Os atendentes têm folga para redirecionar quem errou de área e cuidar de prioridades."
          : `Com ${pior.atendentesCp} atendente${pior.atendentesCp > 1 ? "s" : ""} na ${pior.nome}, o checkpoint vira o gargalo: as mesas atrás dele ficam com fome.`);
  } else {
    const estouro = r.estouroFilas.p50;
    add("semcp", "Filas das mesas sem checkpoint", estouro === 0 ? "ok" : (estouro < 50 ? "atencao" : "falha"),
        estouro === 0 ? "nenhum estouro" : `${Math.round(estouro)} chegadas com a fila da mesa já cheia`, "0",
        "Sem checkpoint ninguém retém o eleitor: quem chega a uma mesa cheia fica em pé no corredor.");
  }

  // 6 equilíbrio entre portas
  add("equilibrio", "Portas equilibradas", nivel(mont.desequilibrio, 1.25, 1.5),
      `porta mais carregada recebe ${mont.desequilibrio.toFixed(2)}× a menos carregada`, "≤ 1,25×",
      Object.entries(mont.cargaPorta).map(([p, v]) => `${p}: ${Math.round(v)} eleitores`).join(" · "));

  // 7 cruzamentos
  const pc = Math.round(mont.fracaoCruza * 100), pl = Math.round(mont.fracaoLeque * 100);
  add("cruzamentos", "Saída não corta corredor de entrada", pc === 0 ? "ok" : (pc <= 15 ? "atencao" : "falha"),
      `${pc} % dos eleitores cruzam um corredor porta→checkpoint ao sair` + (mont.mesmaPorta.length ? ` · mesma porta entra e sai: ${mont.mesmaPorta.join(", ")}` : ""), "0 %",
      (pc === 0 ? "Quem sai não atravessa fila parada de quem entra. " : `Saída das mesas MRV ${mont.mesasCruzam.slice(0, 10).join(", ")}${mont.mesasCruzam.length > 10 ? "…" : ""} atravessa corredor de entrada: precisa de separador físico ou outra porta. `) +
      `Cruzamentos de gente andando (leque checkpoint→mesa × saída): ${pl} % dos pares, inevitáveis em parte com entrada e saída na mesma fachada.`);

  // 8 separadores
  add("separadores", "Fita de unifila", nivel(mont.separadores, LIMITE_SEPARADORES, LIMITE_SEPARADORES * 1.25),
      `${Math.round(mont.separadores)} m (mesas ${Math.round(mont.fitaMesas)} m + corredores ${Math.round(mont.fitaBuffer)} m)`, `≤ ${LIMITE_SEPARADORES} m contratados`,
      mont.separadores <= LIMITE_SEPARADORES ? "Cabe nos 100 unifilas contratados, sem contar o Ring 3." : "Passa do contratado; encurte filas ou compre mais unifila.");

  // 9 conflitos geométricos
  add("encaixe", "Filas cabem no espaço", mont.conflitos.length === 0 ? "ok" : "falha",
      mont.conflitos.length === 0 ? "sem conflitos" : `${mont.conflitos.length} conflito${mont.conflitos.length > 1 ? "s" : ""}`, "0",
      mont.conflitos.length === 0 ? "Nenhuma fila invade corredor de porta, zona protegida ou outra mesa."
        : mont.conflitos.slice(0, 6).map(c => `MRV ${c.mesa} × ${c.com}`).join("; ") + (mont.conflitos.length > 6 ? "…" : ""));

  // 10 Ring 3
  const r3 = r.ring3TotalMax.p90;
  add("ring3", "Ring 3 comporta a fila externa", nivel(r3, mont.cen.ring3.capacidade, mont.cen.ring3.capacidade * 1.3),
      `pico de ${Math.round(r3)} pessoas fora (P90)`, `≤ ${mont.cen.ring3.capacidade}`,
      r3 <= mont.cen.ring3.capacidade ? "A fila externa cabe no espaço previsto." : "Fila externa maior que o espaço do Ring 3; transborda para a rua.");

  // 11 triagem
  add("triagem", "Triagem do Ring 3 dá vazão", nivel(r.triOcupacao.p50, 0.75, 0.9),
      `${Math.round(r.triOcupacao.p50 * 100)} % de ocupação`, "≤ 75 %",
      r.triOcupacao.p50 <= 0.75 ? "Quem separa as pessoas por área acompanha as chegadas." : "A triagem externa segura a chegada: ponha mais gente ou sinalização mais clara.");

  return V;
}

function narrar(mont, r, porMesa, porZona, V){
  const cen = mont.cen, p = [];
  const falhas = V.filter(v => v.status === "falha"), atencoes = V.filter(v => v.status === "atencao");
  const zonasTxt = mont.zonas.map(z => `${z.nome} (MRV ${z.faixaMrv}, ${z.mesas.length} mesas, ${Math.round(z.esperados)} eleitores) entra por ${z.porta}`).join("; ");
  p.push(`${Math.round(mont.esperadosTotal)} eleitores esperados sobre ${mont.aptosTotal} aptos (comparecimento ${mont.taxa.rotulo}), ` +
    `${mont.zonas.length} zona${mont.zonas.length > 1 ? "s" : ""}: ${zonasTxt}. ` +
    `Saída por ${mont.saidas.length ? mont.saidas.join(" e ") : "a mesma porta de entrada"}. ` +
    (cen.checkpoint.existe ? `Checkpoint a ${cen.checkpoint.dist} m da porta com ${mont.zonas.map(z => z.atendentesCp).join("/")} atendente(s) por zona.` : "Sem checkpoint interno: o eleitor acha a mesa pela sinalização."));
  p.push(`Em ${r.runs} dias simulados, a última mesa fecha às ${hhmm(r.fechaUltima.p50)} na mediana e às ${hhmm(r.fechaUltima.p90)} num dia ruim. ` +
    `Nove em dez eleitores levam até ${Math.round(r.totalP90.p50 / 60)} min da chegada ao voto, ${Math.round(r.esperaForaP90.p50 / 60)} deles fora e ${Math.round(r.esperaDentroP90.p50 / 60)} dentro. ` +
    `O pico dentro do salão é de ${Math.round(r.dentroMax.p50)} pessoas; fora, ${Math.round(r.ring3TotalMax.p50)}.`);
  if (falhas.length) p.push(`O que falha: ${falhas.map(v => v.titulo.toLowerCase() + " (" + v.valor + ")").join("; ")}.`);
  if (atencoes.length) p.push(`Pede atenção: ${atencoes.map(v => v.titulo.toLowerCase() + " (" + v.valor + ")").join("; ")}.`);
  if (!falhas.length && !atencoes.length) p.push("Todos os critérios passam. O gargalo remanescente é a própria capacidade das mesas pesadas, que a organização do fluxo não muda.");
  const piorMesa = porMesa.slice().sort((a, b) => b.fecha - a.fecha)[0];
  const melhorMesa = porMesa.slice().sort((a, b) => a.fecha - b.fecha)[0];
  p.push(`A mesa que fecha por último é a MRV ${piorMesa.mrv} (seção ${piorMesa.secao}, ${piorMesa.aptos} aptos) às ${hhmm(piorMesa.fecha)}, com ${Math.round(piorMesa.ocupUrna * 100)} % de uso da urna e ${Math.round(piorMesa.fome / 60)} min de fome; ` +
    `a primeira a fechar é a MRV ${melhorMesa.mrv} às ${hhmm(melhorMesa.fecha)}. ` +
    `Uma urna que passa de 90 % de uso está no limite físico: só mais mesas ou identificação mais rápida resolvem.`);
  return p;
}

/* ------------------------------------------------------------------ */
/* Exportação                                                          */
/* ------------------------------------------------------------------ */
const Modelo = {
  VEL, PASSO_FILA, ABERTURA, ENCERRAMENTO, INICIO_CURVA, MEIA_HORA, CURVA_CHEGADA, COMPARECIMENTO,
  CLASSES, ROTULO_CLASSE, LIMITE_SEPARADORES, classeMesa, cenarioPadrao, cenarioClaude,
  slotsDasZonas, mapaMrv, montar, simularDia, simular, agregar, hhmm, minutos, mediana, percentil,
  frenteMesa, caudaFila, corpoRect, centroPorta, DIR, CCW,
};
if (typeof module !== "undefined" && module.exports) module.exports = Modelo;
else raiz.Modelo = Modelo;
})(typeof window !== "undefined" ? window : globalThis);
