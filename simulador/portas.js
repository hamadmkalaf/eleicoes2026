/* Portas vivas do posto de Dublin: o estado das portas da fachada sul e tudo o
 * que deriva dele, calculado no navegador (e em Node, para os testes).
 *
 * Fonte unica da decisao continua sendo scripts/decisoes.py (06/09/2026:
 * entradas S4 A, S5 B, S6 C; saidas S2 e S8). Este modulo serve ao que a
 * decisao nao cobre: quando alguem, no Simulador, muda o papel de uma porta,
 * a Prancheta, o desenho do Ring 3 e o dashboard precisam seguir a mudanca --
 * com N entradas, N serpenteados, N letras, e cada mesa numa entrada.
 *
 * Tres blocos:
 *   1. estado das portas: validacao, letras e cores das entradas;
 *   2. Ring 3 parametrico: porte de scripts/ring3.py (Zona/Desenho) para N
 *      zonas, mais a reconstrucao do plano vigente (3 · 9 · 3 com baias);
 *   3. atribuicao mesa -> entrada: porte de decisoes.atribui_entradas.
 * E a sincronizacao entre paginas da mesma origem (localStorage +
 * BroadcastChannel) com fallback pelo hash da URL.
 *
 * Roda no navegador (global `Portas`) e em Node (module.exports). Nao depende
 * de DOM, exceto `svgRing3`, que devolve texto SVG.
 */
(function (raiz) {
"use strict";

/* ------------------------------------------------------------------ */
/* 1. Estado das portas                                                */
/* ------------------------------------------------------------------ */
const SUL = ["S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8", "S9"];
const PAPEIS = ["fechada", "entrada", "saida"];
/* Cores das raias: azul, ambar e magenta sao as do plano de sinalizacao
 * (distinguiveis em deuteranopia e protanopia); as duas extras servem a uma
 * quarta e uma quinta entrada. */
const PALETA = [
  {cor: "azul", hex: "#2a78d6"}, {cor: "âmbar", hex: "#e08a00"},
  {cor: "magenta", hex: "#c2185b"}, {cor: "verde-água", hex: "#1baf7a"},
  {cor: "roxo", hex: "#7d3c98"}, {cor: "castanho", hex: "#8a5a2b"},
  {cor: "cinza", hex: "#5c6c80"}, {cor: "oliva", hex: "#7a8a1a"},
  {cor: "preto", hex: "#17202b"},
];

const DECISAO = {S2: "saida", S4: "entrada", S5: "entrada", S6: "entrada", S8: "saida"};

function estadoDaDecisao(dec){
  const e = {};
  for (const id of SUL) e[id] = "fechada";
  const portas = (dec && dec.portas) ? dec.portas : null;
  if (portas) for (const id of Object.keys(portas)) if (SUL.includes(id)) e[id] = portas[id].papel;
  else Object.assign(e, DECISAO);
  return e;
}

/* Le qualquer coisa parecida com um estado (objeto por porta, ou o `portas`
 * do cenario do simulador) e devolve os nove papeis, um por porta. */
function normalizaEstado(obj){
  const e = {};
  for (const id of SUL) {
    const v = obj && obj[id];
    e[id] = PAPEIS.includes(v) ? v : "fechada";
  }
  return e;
}

function igual(a, b){
  a = normalizaEstado(a); b = normalizaEstado(b);
  return SUL.every(id => a[id] === b[id]);
}

/* Centro em x de cada porta da fachada sul. `portas` e a lista de BASE.portas
 * (prancheta / simulador), com x1 e x2 em metros do canto sudoeste. */
function centros(portas){
  const c = {};
  for (const p of (portas || [])) if (p.face === "sul" && SUL.includes(p.id)) c[p.id] = (p.x1 + p.x2) / 2;
  return c;
}

/* As entradas em ordem de x (oeste -> leste), com letra e cor. */
function entradas(estado, portas){
  const e = normalizaEstado(estado), cx = centros(portas);
  const ids = SUL.filter(id => e[id] === "entrada")
    .sort((a, b) => (cx[a] ?? SUL.indexOf(a)) - (cx[b] ?? SUL.indexOf(b)));
  return ids.map((id, i) => ({
    id: String.fromCharCode(65 + i), porta: id, x: cx[id],
    cor: PALETA[i % PALETA.length].cor, hex: PALETA[i % PALETA.length].hex,
  }));
}
function saidas(estado){ return SUL.filter(id => normalizaEstado(estado)[id] === "saida"); }

function valida(estado, portas){
  const e = normalizaEstado(estado), erros = [], avisos = [];
  const ent = SUL.filter(id => e[id] === "entrada"), sai = SUL.filter(id => e[id] === "saida");
  if (!ent.length) erros.push("Nenhuma porta de entrada: marque ao menos uma.");
  if (!sai.length) erros.push("Nenhuma porta de saída: marque ao menos uma.");
  if (ent.length > PALETA.length) erros.push(`No máximo ${PALETA.length} entradas.`);
  for (const id of Object.keys(estado || {})) {
    if (!SUL.includes(id) && estado[id] && estado[id] !== "fechada")
      erros.push(`${id} não é porta da fachada sul; só S1 a S9 servem ao eleitor.`);
  }
  // saida entre duas entradas: quem sai cruza a fila de quem entra
  const cx = centros(portas);
  const ex = ent.map(id => cx[id] ?? SUL.indexOf(id));
  if (ex.length >= 2) {
    const lo = Math.min(...ex), hi = Math.max(...ex);
    for (const id of sai) {
      const x = cx[id] ?? SUL.indexOf(id);
      if (x > lo && x < hi) avisos.push(`A saída ${id} fica entre duas entradas: quem sai cruza a fila de quem entra.`);
    }
  }
  for (const id of ["S1", "S9"]) if (e[id] !== "fechada")
    avisos.push(`${id} é porta de carga: depende de ficar aberta e travada as nove horas e de a soleira servir a pedestre.`);
  return {ok: !erros.length, erros, avisos};
}

/* ------------------------------------------------------------------ */
/* 2. Ring 3 parametrico (porte de scripts/ring3.py)                   */
/* ------------------------------------------------------------------ */
const R3 = {
  LARG_RING: 44.0, PROF_RING: 35.0, EIXO_S5: 28.285, APRON: 14.0,
  Y0: -49.0,
  PASSO_RAIA: 1.40, TOL_PASSO: 0.05, RAIA_UTIL: 1.20, DENS_FILA: 2.00,
  DENS_BAIA: 1.80, VAO_RETORNO: 1.20, VAO_SAIDA: 1.40,
  SEPARADOR_M: 2.00, SEPARADOR_EUR: 13.02, ESTOQUE: 200,
  LARG_BAIA: 6.40, LARG_CORREDOR: 3.00, VAO_ENTRE_ZONAS: 2.60, VAO_MIN: 2.00,
  // reconstrucao do plano vigente (aferição)
  BLOCOS_ORIG: {A: [15.16, 19.36], B: [22.09, 34.69], C: [37.19, 41.39]},
  PROF_PLANO_ORIGINAL: 23.75, CORREDOR_ORIGINAL: 36.70, FUNIL_GARGANTA: 12.0,
};
const POR_METRO_RAIA = R3.RAIA_UTIL * R3.DENS_FILA;

function ring(largura){
  const L = largura || R3.LARG_RING;
  return {x0: R3.EIXO_S5 - L / 2, x1: R3.EIXO_S5 + L / 2, y0: R3.Y0, y1: R3.Y0 + R3.PROF_RING};
}
const PROF_SERP = R3.PROF_RING - R3.LARG_CORREDOR;   // 32,0 m sem faixa de garganta

function raiasQueCabem(dim){
  let n = Math.round(dim / R3.PASSO_RAIA);
  while (n > 0 && dim / n < R3.PASSO_RAIA - R3.TOL_PASSO) n--;
  return Math.max(n, 0);
}
const unidades = m => Math.ceil(m / R3.SEPARADOR_M - 1e-9);

/* Uma zona: o retangulo de serpenteado de uma entrada. `eixo` e o x da porta. */
function zona(nome, x0, x1, prof, orientacao, eixo, oesteGradil, lesteGradil){
  const larg = x1 - x0, vertical = orientacao === "vertical";
  const raias = raiasQueCabem(vertical ? larg : prof);
  const comp = vertical ? prof : larg;
  const passo = raias ? (vertical ? larg : prof) / raias : 0;
  let portao, toco;
  if (vertical) { portao = Math.abs(eixo - x0) <= Math.abs(eixo - x1) ? x0 : x1; toco = 0; }
  else { portao = Math.min(Math.max(eixo, x0), x1); toco = Math.min(portao - x0, x1 - portao); }
  const diagonal = Math.hypot(R3.APRON, eixo - portao);
  const capacidade = (raias * comp - toco) * POR_METRO_RAIA;
  let perimetro = larg - R3.VAO_SAIDA;
  if (!oesteGradil) perimetro += prof;
  if (!lesteGradil) perimetro += prof;
  const divisorias = raias <= 1 ? 0 : (raias - 1) * Math.max(0, comp - R3.VAO_RETORNO);
  return {nome, x0, x1, larg, prof, orientacao, raias, passo, comp, portao, toco, diagonal,
          eixo, capacidade, perimetro, divisorias, barreira: perimetro + divisorias,
          meiasVoltas: Math.max(0, raias - 1)};
}

function larguraEquivalenteDaBaia(){ return R3.LARG_BAIA * R3.DENS_BAIA / (POR_METRO_RAIA / R3.PASSO_RAIA); }

/* Reparte a largura entre N zonas na proporcao do esperado de cada uma.
 * `esperado` e uma lista alinhada com as entradas (oeste -> leste). Onde ha
 * baia de flanco, a primeira e a ultima zona ja ganham lotacao da baia e
 * recebem menos largura, exatamente o equivalente. `snap` arredonda para um
 * numero inteiro de raias (orientacao vertical). */
function reparteLargura(disponivel, esperado, snap, comBaias){
  const n = esperado.length, total = esperado.reduce((s, v) => s + v, 0) || n;
  const baia = comBaias ? larguraEquivalenteDaBaia() : 0;
  const flancos = i => (n === 1 ? 2 : ((i === 0 || i === n - 1) ? 1 : 0));
  const equivalente = disponivel + 2 * baia;
  const alvo = esperado.map((v, i) => equivalente * (total ? v / total : 1 / n) - baia * flancos(i));
  if (!snap) return alvo;
  const totalRaias = Math.floor(disponivel / R3.PASSO_RAIA + 0.02);
  const exato = alvo.map(v => Math.max(0, v) / R3.PASSO_RAIA);
  const nr = exato.map(v => Math.floor(v));
  const sobra = totalRaias - nr.reduce((s, v) => s + v, 0);
  const ordem = exato.map((v, i) => i).sort((a, b) => (exato[b] - nr[b]) - (exato[a] - nr[a]));
  for (let i = 0; i < Math.max(0, sobra); i++) nr[ordem[i % n]]++;
  return nr.map(v => v * R3.PASSO_RAIA);
}

/* Monta as N zonas dentro do Ring, com ou sem baias, e devolve o desenho
 * completo (capacidade, barreira, separadores). `ents` vem de entradas():
 * cada uma com x (eixo da porta); `esperado` alinhado com `ents`. */
function desenho(ents, esperado, opts){
  opts = opts || {};
  const orientacao = opts.orientacao === "horizontal" ? "horizontal" : "vertical";
  const comBaias = !!opts.baias;
  const RG = ring(opts.largura);
  const L = RG.x1 - RG.x0, n = ents.length;
  if (!n) return null;
  const prof = opts.prof || PROF_SERP;
  const vaoMin = comBaias ? R3.VAO_MIN : (orientacao === "horizontal" ? R3.VAO_ENTRE_ZONAS : R3.VAO_MIN);
  const borda = comBaias ? R3.LARG_BAIA : 0;
  const disponivel = L - 2 * borda - (n - 1) * vaoMin;
  const larg = reparteLargura(disponivel, esperado, orientacao === "vertical", comBaias);
  const somaLarg = larg.reduce((s, v) => s + v, 0);
  const vao = n > 1 ? (L - 2 * borda - somaLarg) / (n - 1) : 0;
  const zonas = [];
  let x = RG.x0 + borda;
  ents.forEach((e, i) => {
    const x1 = x + larg[i];
    zonas.push(zona(e.id, x, x1, prof, orientacao, e.x,
      !comBaias && Math.abs(x - RG.x0) < 0.05, !comBaias && Math.abs(x1 - RG.x1) < 0.05));
    x = x1 + vao;
  });
  const baias = {};
  if (comBaias) {
    baias[ents[0].id] = {rotulo: "baia do flanco oeste", area: R3.LARG_BAIA * prof, x0: RG.x0, x1: RG.x0 + R3.LARG_BAIA};
    baias[ents[n - 1].id] = {rotulo: "baia do flanco leste", area: R3.LARG_BAIA * prof, x0: RG.x1 - R3.LARG_BAIA, x1: RG.x1};
    if (n === 1) baias[ents[0].id].area *= 2;
  }
  const extra = {"corredor de fundo (parede norte)": L - n * R3.VAO_SAIDA};
  if (comBaias) extra["fechamento das baias de flanco"] = 2 * R3.LARG_BAIA;
  return fecha({codigo: orientacao === "vertical" ? (comBaias ? "V" : "VS") : (comBaias ? "HB" : "H"),
    nome: (orientacao === "vertical" ? "Raias norte-sul" : "Raias leste-oeste") + (comBaias ? ", com baias" : ", sem baias"),
    ring: RG, apron: R3.APRON, prof, vao, orientacao, comBaias, zonas, baias, extra});
}

/* Reconstrucao do plano vigente (3 · 9 · 3 raias, 23,75 m, garganta ao sul),
 * so valida com tres entradas: serve de aferição e de preset "vigente". */
function desenhoPlanoVigente(ents){
  if (ents.length !== 3) return null;
  const RG = ring(R3.LARG_RING);
  const prof = R3.PROF_PLANO_ORIGINAL;
  const zonas = ents.map((e, i) => {
    const b = R3.BLOCOS_ORIG[["A", "B", "C"][i]];
    return zona(e.id, b[0], b[1], prof, "vertical", e.x, false, false);
  });
  const baias = {};
  baias[ents[0].id] = {rotulo: "baia do flanco oeste", area: R3.LARG_BAIA * prof, x0: RG.x0 + 2.5, x1: RG.x0 + 2.5 + R3.LARG_BAIA};
  baias[ents[2].id] = {rotulo: "baia do flanco leste", area: R3.LARG_BAIA * prof, x0: RG.x1 - 2.5 - R3.LARG_BAIA, x1: RG.x1 - 2.5};
  const extra = {"corredor de fundo (2 lados)": 2 * R3.CORREDOR_ORIGINAL,
                 "fechamento das baias de flanco": 2 * R3.LARG_BAIA,
                 "funil da garganta sudeste": 2 * R3.FUNIL_GARGANTA};
  return fecha({codigo: "PV", nome: "Plano vigente (3 · 9 · 3, com garganta)", ring: RG, apron: R3.APRON,
    prof, vao: null, orientacao: "vertical", comBaias: true, zonas, baias, extra, garganta: true});
}

function fecha(d){
  const capRaias = d.zonas.reduce((s, z) => s + z.capacidade, 0);
  const capBaias = Object.values(d.baias).reduce((s, b) => s + b.area * R3.DENS_BAIA, 0);
  const porEntrada = {};
  for (const z of d.zonas) porEntrada[z.nome] = z.capacidade + (d.baias[z.nome] ? d.baias[z.nome].area * R3.DENS_BAIA : 0);
  const barreira = {"perímetro das zonas": d.zonas.reduce((s, z) => s + z.perimetro, 0),
                    "divisórias entre as raias": d.zonas.reduce((s, z) => s + z.divisorias, 0)};
  Object.assign(barreira, d.extra);
  barreira["raias do apron até as portas"] = d.zonas.reduce((s, z) => s + 2 * z.diagonal, 0);
  const total = Object.values(barreira).reduce((s, v) => s + v, 0);
  const separadores = unidades(total);
  d.capacidade = capRaias + capBaias; d.capRaias = capRaias; d.capBaias = capBaias;
  d.porEntrada = porEntrada; d.barreira = barreira; d.barreiraTotal = total;
  d.separadores = separadores; d.compra = Math.max(0, separadores - R3.ESTOQUE);
  d.custoCompra = d.compra * R3.SEPARADOR_EUR;
  d.meiasVoltas = d.zonas.reduce((s, z) => s + z.meiasVoltas, 0);
  return d;
}

const DESENHOS = [
  {id: "vigente", nome: "Plano vigente · 3·9·3 com baias e garganta", so3: true},
  {id: "VS", nome: "Norte-sul, sem baias", orientacao: "vertical", baias: false},
  {id: "V", nome: "Norte-sul, com baias", orientacao: "vertical", baias: true},
  {id: "H", nome: "Leste-oeste, sem baias", orientacao: "horizontal", baias: false},
  {id: "HB", nome: "Leste-oeste, com baias", orientacao: "horizontal", baias: true},
];

function desenhoPorId(id, ents, esperado, opts){
  if (id === "vigente") return desenhoPlanoVigente(ents);
  const d = DESENHOS.find(x => x.id === id) || DESENHOS[1];
  return desenho(ents, esperado, Object.assign({}, opts || {}, {orientacao: d.orientacao, baias: d.baias}));
}

/* ------------------------------------------------------------------ */
/* 3. Atribuicao mesa -> entrada (porte de decisoes.atribui_entradas)  */
/* ------------------------------------------------------------------ */
/* `lista`: [{mrv, esperado, classe}]; `quotas`: {entrada: fracao}. Uma mesa de
 * classe alta em cada entrada (as tres criticas nunca na mesma fila), depois
 * as demais, sempre para a entrada mais distante da sua quota. */
function atribuiEntradas(lista, quotas){
  const total = lista.reduce((s, m) => s + m.esperado, 0);
  const chaves = Object.keys(quotas);
  const alvo = {}, grupos = {}, carga = {};
  for (const k of chaves) { alvo[k] = quotas[k] * total; grupos[k] = []; carga[k] = 0; }
  const ordenadas = lista.slice().sort((a, b) => (b.esperado - a.esperado) || (a.mrv - b.mrv));
  const altas = ordenadas.filter(m => m.classe === "alta");
  const porQuota = chaves.slice().sort((a, b) => quotas[b] - quotas[a]);
  const postas = new Set();
  porQuota.forEach((k, i) => {
    if (i >= altas.length) return;
    grupos[k].push(altas[i].mrv); carga[k] += altas[i].esperado; postas.add(altas[i].mrv);
  });
  for (const m of ordenadas) {
    if (postas.has(m.mrv)) continue;
    let melhor = chaves[0], folga = -Infinity;
    for (const k of chaves) { const f = alvo[k] - carga[k]; if (f > folga) { folga = f; melhor = k; } }
    grupos[melhor].push(m.mrv); carga[melhor] += m.esperado;
  }
  for (const k of chaves) grupos[k].sort((a, b) => a - b);
  return {grupos, carga, alvo};
}

/* As 28 mesas com esperado e classe, lidas do bloco de decisoes (objeto por
 * MRV na prancheta, lista no simulador). */
function mesasDaDecisao(dec){
  const m = dec && dec.mesas;
  if (!m) return [];
  if (Array.isArray(m)) return m.map(x => ({mrv: x.mrv, esperado: x.esperado, classe: x.classe, principal: x.principal}));
  return Object.keys(m).map(k => ({mrv: +k, esperado: m[k].esperado, classe: m[k].classe, principal: m[k].principal}))
    .sort((a, b) => a.mrv - b.mrv);
}

/* ------------------------------------------------------------------ */
/* Resolucao: do estado das portas ao quadro completo                  */
/* ------------------------------------------------------------------ */
/* ctx = {portas: BASE.portas, dec: DECISOES, desenho: id, largura}. Devolve
 * {estado, entradas, saidas, mesas: {mrv: {entrada, porta}}, ring3, avisos,
 * erros, igualDecisao}. Com as portas da decisao e o desenho "vigente", a
 * atribuicao e a da decisao (data/decisoes.json), letra por letra. */
function resolve(estado, ctx){
  ctx = ctx || {};
  const e = normalizaEstado(estado);
  const v = valida(e, ctx.portas);
  const ents = entradas(e, ctx.portas);
  const lista = mesasDaDecisao(ctx.dec);
  const igualDecisao = igual(e, estadoDaDecisao(ctx.dec));
  let desenhoId = ctx.desenho || "vigente";
  if (desenhoId === "vigente" && ents.length !== 3) desenhoId = "VS";
  const out = {estado: e, entradas: ents, saidas: saidas(e), mesas: {}, avisos: v.avisos.slice(),
               erros: v.erros.slice(), igualDecisao, desenho: desenhoId, ring3: null};
  if (!ents.length || !lista.length) return out;

  let esperado = ents.map(() => 1), grupos = null, r3 = null;
  if (desenhoId === "vigente" && igualDecisao && ctx.dec && Array.isArray(ctx.dec.entradas)) {
    // a decisao, tal como esta em decisoes.py
    r3 = desenhoPlanoVigente(ents);
    ctx.dec.entradas.forEach((de, i) => { ents[i].capacidade = de.capacidade; ents[i].quota = de.quota; });
    grupos = {}; ctx.dec.entradas.forEach((de, i) => { grupos[ents[i].id] = de.mrvs.slice(); });
  } else {
    // itera: largura das zonas <- esperado <- atribuicao <- capacidade das zonas
    let anterior = "";
    for (let it = 0; it < 8; it++) {
      r3 = desenhoPorId(desenhoId, ents, esperado, {largura: ctx.largura});
      const tot = Object.values(r3.porEntrada).reduce((s, x) => s + x, 0);
      const quotas = {}; for (const z of ents) quotas[z.id] = r3.porEntrada[z.id] / tot;
      const a = atribuiEntradas(lista, quotas);
      grupos = a.grupos;
      esperado = ents.map(z => a.carga[z.id]);
      const chave = JSON.stringify(grupos);
      if (chave === anterior) break;
      anterior = chave;
    }
    const tot = Object.values(r3.porEntrada).reduce((s, x) => s + x, 0);
    ents.forEach(z => { z.capacidade = Math.round(r3.porEntrada[z.id]); z.quota = r3.porEntrada[z.id] / tot; });
  }
  const porMrv = {}; for (const m of lista) porMrv[m.mrv] = m;
  ents.forEach(z => {
    z.mrvs = grupos[z.id] || [];
    z.esperado = z.mrvs.reduce((s, n) => s + (porMrv[n] ? porMrv[n].esperado : 0), 0);
    for (const n of z.mrvs) out.mesas[n] = {entrada: z.id, porta: z.porta, hex: z.hex};
  });
  out.ring3 = r3;
  out.ring3.rect = [r3.ring.x0, r3.ring.y0, r3.ring.x1, r3.ring.y1];
  if (r3.zonas.some(z => z.raias === 0)) out.avisos.push("Alguma zona do Ring 3 ficou sem raia: entradas demais para a largura do Ring.");
  return out;
}

/* ------------------------------------------------------------------ */
/* SVG do Ring 3 (porte de ring3.svg), em escala                       */
/* ------------------------------------------------------------------ */
function svgRing3(res, opts){
  opts = opts || {};
  const d = res && res.ring3;
  if (!d) return "";
  const RG = d.ring, ESC = opts.escala || 12, MG = 40;
  const px = (x, y) => [MG + (x - RG.x0 + 6) * ESC, MG + (2.0 - y) * ESC];
  const larg = (RG.x1 - RG.x0 + 12) * ESC + 2 * MG, alt = (RG.y1 - RG.y0 + d.apron + 6) * ESC + 2 * MG;
  const s = [];
  const ret = (x0, y0, x1, y1, at) => { const [ax, ay] = px(x0, y1), [bx, by] = px(x1, y0);
    s.push(`<rect x="${ax.toFixed(1)}" y="${ay.toFixed(1)}" width="${(bx - ax).toFixed(1)}" height="${(by - ay).toFixed(1)}" ${at}/>`); };
  const lin = (x0, y0, x1, y1, at) => { const [ax, ay] = px(x0, y0), [bx, by] = px(x1, y1);
    s.push(`<line x1="${ax.toFixed(1)}" y1="${ay.toFixed(1)}" x2="${bx.toFixed(1)}" y2="${by.toFixed(1)}" ${at}/>`); };
  const txt = (x, y, t, size, peso, cor, anchor, rot) => { const [ax, ay] = px(x, y);
    const r = rot ? ` transform="rotate(${rot} ${ax.toFixed(1)} ${ay.toFixed(1)})"` : "";
    s.push(`<text x="${ax.toFixed(1)}" y="${ay.toFixed(1)}" text-anchor="${anchor || "middle"}" font-family="IBM Plex Sans,ui-sans-serif,system-ui,sans-serif" font-size="${size}" font-weight="${peso || 400}" fill="${cor}" paint-order="stroke" stroke="var(--prancha,#fbfaf7)" stroke-width="3" stroke-linejoin="round"${r}>${t}</text>`); };
  s.push(`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${larg.toFixed(0)} ${alt.toFixed(0)}" role="img" aria-label="Ring 3 com ${d.zonas.length} zona(s) de fila, uma por entrada" style="width:100%;height:auto;display:block">`);
  s.push(`<rect width="${larg.toFixed(0)}" height="${alt.toFixed(0)}" fill="var(--prancha,#fbfaf7)"/>`);
  ret(RG.x0 - 5, -d.apron, RG.x1 + 5, 0, 'fill="var(--piso,#eef1f4)"');
  ret(RG.x0, RG.y0, RG.x1, RG.y1, 'fill="var(--folha,#f6f4ef)" stroke="var(--traco,#1c2733)" stroke-width="2"');
  lin(RG.x0 - 5, 0, RG.x1 + 5, 0, 'stroke="var(--traco,#1c2733)" stroke-width="3"');
  txt((RG.x0 + RG.x1) / 2, 1.3, "FACHADA SUL DO HALL 2", 10, 700, "var(--meio,#5c6c80)");
  const portas = (opts.portas || []).filter(p => p.face === "sul");
  for (const p of portas) {
    const papel = res.estado[p.id] || "fechada";
    const ent = res.entradas.find(z => z.porta === p.id);
    const cor = ent ? ent.hex : (papel === "saida" ? "#b26a12" : "#b2bcc8");
    lin(p.x1, 0, p.x2, 0, `stroke="${cor}" stroke-width="${ent ? 6 : (papel === "saida" ? 6 : 3)}"`);
    if (ent) txt((p.x1 + p.x2) / 2, -1.7, `${p.id} · ${ent.id}`, 10, 700, cor);
    else if (papel === "saida") txt((p.x1 + p.x2) / 2, -1.7, `${p.id} saída`, 9, 400, cor);
  }
  txt(RG.x0 - 4.2, -d.apron / 2, `apron pavimentado · ${d.apron} m`, 9, 400, "var(--meio,#5c6c80)", "middle", -90);
  const yTopo = RG.y1, yBase = RG.y1 - d.prof;
  for (const z of d.zonas) {
    const c = (res.entradas.find(e => e.id === z.nome) || {}).hex || "#5c6c80";
    ret(z.x0, yBase, z.x1, yTopo, `fill="${c}" fill-opacity=".13" stroke="${c}" stroke-width="1.4"`);
    if (z.orientacao === "vertical") {
      for (let i = 1; i < z.raias; i++) {
        const x = z.x0 + i * z.passo;
        lin(x, i % 2 ? yBase + R3.VAO_RETORNO : yBase, x, i % 2 ? yTopo : yTopo - R3.VAO_RETORNO, `stroke="${c}" stroke-width="1" stroke-opacity=".6"`);
      }
      txt((z.x0 + z.x1) / 2, yTopo + 1.3, `${z.nome} · ${z.raias} raias de ${z.comp.toFixed(1).replace(".", ",")} m`, 10, 700, c);
    } else {
      for (let i = 1; i < z.raias; i++) {
        const y = yBase + i * z.passo;
        lin(i % 2 ? z.x0 + R3.VAO_RETORNO : z.x0, y, i % 2 ? z.x1 : z.x1 - R3.VAO_RETORNO, y, `stroke="${c}" stroke-width="1" stroke-opacity=".6"`);
      }
      txt((z.x0 + z.x1) / 2, yTopo + 1.3, `${z.nome} · ${z.raias} × ${z.larg.toFixed(1).replace(".", ",")} m`, 10, 700, c);
    }
    lin(z.portao, yTopo, z.eixo, -0.4, `stroke="${c}" stroke-width="2" stroke-dasharray="4 3"`);
  }
  for (const k of Object.keys(d.baias)) {
    const b = d.baias[k];
    if (b.x0 === undefined) continue;
    ret(b.x0, yBase, b.x1, yTopo, 'fill="#8a919b" fill-opacity=".16" stroke="#8a919b" stroke-width="1.2" stroke-dasharray="4 3"');
    txt((b.x0 + b.x1) / 2, (yBase + yTopo) / 2, b.rotulo, 9, 400, "var(--meio,#5c6c80)", "middle", -90);
  }
  ret(RG.x0, RG.y0, RG.x1, RG.y0 + R3.LARG_CORREDOR, 'fill="none" stroke="#5c6c80" stroke-width="1.2"');
  txt((RG.x0 + RG.x1) / 2, RG.y0 + R3.LARG_CORREDOR / 2 - 0.4, "CORREDOR DE FUNDO · 3,0 m", 9, 600, "var(--meio,#5c6c80)");
  txt(RG.x0, RG.y0 - 1.8, `Ring 3 · ${(RG.x1 - RG.x0).toFixed(1).replace(".", ",")} × ${R3.PROF_RING.toFixed(1).replace(".", ",")} m · ${Math.round(d.capacidade).toLocaleString("pt-BR")} pessoas · ${d.separadores} separadores`, 9, 400, "#8a919b", "start");
  s.push("</svg>");
  return s.join("\n");
}

/* ------------------------------------------------------------------ */
/* Sincronizacao entre paginas                                         */
/* ------------------------------------------------------------------ */
const CHAVE = "posto-dublin/portas", CANAL = "posto-dublin";
let canal = null;
function abreCanal(){
  if (canal !== null) return canal;
  try { canal = (typeof BroadcastChannel !== "undefined") ? new BroadcastChannel(CANAL) : false; }
  catch (e) { canal = false; }
  return canal;
}
function guarda(msg){ try { localStorage.setItem(CHAVE, JSON.stringify(msg)); } catch (e) {} }
function le(){
  try { const s = JSON.parse(localStorage.getItem(CHAVE) || "null"); if (s && s.estado) return s; } catch (e) {}
  const h = deHash(typeof location !== "undefined" ? location.hash : "");
  return h ? {estado: h.estado, desenho: h.desenho, origem: "hash"} : null;
}
/* Publica o estado para as outras paginas da mesma origem. `origem` e um nome
 * curto da pagina que publicou, para cada uma ignorar o proprio eco. */
function publica(estado, extra){
  const msg = Object.assign({}, extra || {}, {estado: normalizaEstado(estado), quando: Date.now()});
  guarda(msg);
  const c = abreCanal();
  if (c) { try { c.postMessage(msg); } catch (e) {} }
  return msg;
}
function assina(fn){
  const c = abreCanal();
  if (c) c.addEventListener("message", ev => { if (ev.data && ev.data.estado) fn(ev.data); });
  if (typeof window !== "undefined") window.addEventListener("storage", ev => {
    if (ev.key !== CHAVE || !ev.newValue) return;
    try { const m = JSON.parse(ev.newValue); if (m && m.estado) fn(m); } catch (e) {}
  });
}
/* #portas=S4:A,S5:B,S6:C,S2:x,S8:x&desenho=VS  (x = saida; letra = entrada) */
function paraHash(estado, desenho){
  const e = normalizaEstado(estado), ents = entradas(e);
  const partes = [];
  for (const id of SUL) {
    if (e[id] === "entrada") partes.push(`${id}:${(ents.find(z => z.porta === id) || {}).id || "E"}`);
    else if (e[id] === "saida") partes.push(`${id}:x`);
  }
  return "portas=" + partes.join(",") + (desenho ? "&desenho=" + desenho : "");
}
function deHash(hash){
  const m = /portas=([^&]+)/.exec(hash || "");
  if (!m) return null;
  const e = {}; for (const id of SUL) e[id] = "fechada";
  for (const par of m[1].split(",")) {
    const [id, v] = par.split(":");
    if (SUL.includes(id)) e[id] = (v === "x" ? "saida" : "entrada");
  }
  const d = /desenho=([A-Za-z]+)/.exec(hash || "");
  return {estado: e, desenho: d ? d[1] : null};
}

const Portas = {
  SUL, PAPEIS, PALETA, DECISAO, R3, DESENHOS,
  estadoDaDecisao, normalizaEstado, igual, centros, entradas, saidas, valida,
  ring, raiasQueCabem, desenho, desenhoPlanoVigente, desenhoPorId, atribuiEntradas,
  mesasDaDecisao, resolve, svgRing3,
  CHAVE, CANAL, publica, assina, le, paraHash, deHash,
};
if (typeof module !== "undefined" && module.exports) module.exports = Portas;
else raiz.Portas = Portas;
})(typeof window !== "undefined" ? window : globalThis);
