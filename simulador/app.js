/* Interface do simulador: três telas (premissas, simulação, resultado).
 * Depende de Modelo (modelo.js), BASE e MRVS embutidos pelo gerador. */
(function(){
"use strict";
const M = Modelo;
const $ = id => document.getElementById(id);
const NS = "http://www.w3.org/2000/svg";
const CORES_ZONA = ["var(--z1)", "var(--z2)", "var(--z3)", "var(--z4)"];
const LETRAS = ["A", "B", "C", "D"];
const CHAVE_RASCUNHO = "simulador-hall2-cenario-v1";
const CHAVE_COMPARATIVO = "simulador-hall2-comparativo-v1";
const SUL = BASE.portas.filter(p => p.face === "sul");
const SUL_USAVEIS = SUL.filter(p => p.estado !== "emergencia").map(p => p.id);
const ALT = BASE.salao.altura, LARG = BASE.salao.largura;
const fy = v => ALT - v;

function el(tag, attrs, pai){
  const e = document.createElementNS(NS, tag);
  for (const k in attrs) e.setAttribute(k, attrs[k]);
  if (pai) pai.appendChild(e);
  return e;
}
function h(tag, attrs, ...filhos){
  const e = document.createElement(tag);
  for (const k in (attrs || {})) {
    if (k === "class") e.className = attrs[k];
    else if (k === "text") e.textContent = attrs[k];
    else if (k.startsWith("on")) e.addEventListener(k.slice(2), attrs[k]);
    else e.setAttribute(k, attrs[k]);
  }
  for (const f of filhos) if (f != null) e.appendChild(typeof f === "string" ? document.createTextNode(f) : f);
  return e;
}
const fmt = n => Math.round(n).toLocaleString("pt-BR");
const vg = (v, c = 1) => Number(v).toFixed(c).replace(".", ",");
const pct = v => Math.round(v * 100) + " %";
const min = seg => Math.round(seg / 60) + " min";

/* ------------------------------------------------------------------ */
/* Estado                                                              */
/* ------------------------------------------------------------------ */
let cen = null;          // cenário atual (premissas)
let mont = null;         // montagem estática do cenário atual
let res = null;          // último resultado
let tempoIdx = 0, tocando = null;

function carregaRascunho(){
  try {
    const s = JSON.parse(localStorage.getItem(CHAVE_RASCUNHO) || "null");
    if (s && s.zonas && s.portas) return s;
  } catch (e) {}
  return null;
}
function guardaRascunho(){ try { localStorage.setItem(CHAVE_RASCUNHO, JSON.stringify(cen)); } catch (e) {} }

function normaliza(c){
  // garante campos e coerência (tamanhos somam 28, portas por zona válidas)
  const nz = Math.max(2, Math.min(4, c.zonas.tamanhos.length));
  c.zonas.tamanhos = c.zonas.tamanhos.slice(0, nz).map(v => Math.max(1, Math.round(v)));
  while (c.zonas.tamanhos.length < nz) c.zonas.tamanhos.push(1);
  let s = c.zonas.tamanhos.reduce((a, b) => a + b, 0);
  if (s !== 28) { c.zonas.tamanhos[nz - 1] = Math.max(1, c.zonas.tamanhos[nz - 1] + 28 - s); }
  s = c.zonas.tamanhos.reduce((a, b) => a + b, 0);
  if (s !== 28) { c.zonas.tamanhos = nz === 2 ? [16, 12] : (nz === 3 ? [8, 12, 8] : [8, 6, 6, 8]); }
  c.zonas.inicio = Math.max(1, Math.min(28, Math.round(c.zonas.inicio || 1)));
  const entradas = SUL_USAVEIS.filter(id => c.portas[id] === "entrada");
  if (!entradas.length) { c.portas.S5 = "entrada"; entradas.push("S5"); }
  c.zonas.portas = c.zonas.tamanhos.map((_, z) => entradas.includes(c.zonas.portas[z]) ? c.zonas.portas[z] : entradas[Math.min(z, entradas.length - 1)]);
  if (!Array.isArray(c.checkpoint.atendentes)) c.checkpoint.atendentes = c.zonas.tamanhos.map(() => c.checkpoint.atendentes || 2);
  c.checkpoint.atendentes = c.zonas.tamanhos.map((_, z) => Math.max(1, Math.round(c.checkpoint.atendentes[z] || 2)));
  c.ordem.inicioZona = Math.max(0, Math.min(nz - 1, c.ordem.inicioZona || 0));
  if (!c.salao) c.salao = {base: "A", alteracoes: []};
  if (!c.sim) c.sim = {runs: 12, seed: 7};
  return c;
}
function aplica(c, nome){
  cen = normaliza(JSON.parse(JSON.stringify(c)));
  if (nome !== undefined) cen.nome = nome;
  preencher(); atualizaDerivados(); guardaRascunho();
}

/* ------------------------------------------------------------------ */
/* Tela 1: formulário                                                  */
/* ------------------------------------------------------------------ */
function grupo(id, attr, valor){
  for (const b of $(id).querySelectorAll("button")) b.setAttribute("aria-pressed", String(b.dataset[attr]) === String(valor));
}
function preencher(){
  $("nomeCenario").value = cen.nome || "";
  grupo("nZonas", "n", cen.zonas.tamanhos.length);
  $("inicioZona1").value = cen.zonas.inicio;
  // tamanhos
  const T = $("tamanhos"); T.innerHTML = "";
  cen.zonas.tamanhos.forEach((v, z) => {
    const inp = h("input", {type: "number", min: 1, max: 26, value: v, "aria-label": `Mesas na zona ${LETRAS[z]}`, style: "width:58px"});
    inp.addEventListener("change", () => {
      const novo = Math.max(1, Math.min(26, Math.round(+inp.value || 1)));
      cen.zonas.tamanhos[z] = novo;
      const outros = z === cen.zonas.tamanhos.length - 1 ? 0 : cen.zonas.tamanhos.length - 1;
      const resto = 28 - cen.zonas.tamanhos.reduce((a, b) => a + b, 0);
      cen.zonas.tamanhos[outros] = Math.max(1, cen.zonas.tamanhos[outros] + resto);
      normaliza(cen); preencher(); atualizaDerivados();
    });
    T.appendChild(h("span", {class: "campo", style: "flex-direction:row;align-items:center;gap:4px"},
      h("span", {class: "swatch", style: `background:${CORES_ZONA[z]}`}), h("span", {class: "mono", text: LETRAS[z]}), inp));
  });
  // MRV começa na zona
  const IZ = $("inicioZonaMrv"); IZ.innerHTML = "";
  cen.zonas.tamanhos.forEach((_, z) => {
    const b = h("button", {"data-z": z, "aria-pressed": String(z === cen.ordem.inicioZona), text: `Zona ${LETRAS[z]}`});
    b.addEventListener("click", () => { cen.ordem.inicioZona = z; grupo("inicioZonaMrv", "z", z); atualizaDerivados(); });
    IZ.appendChild(b);
  });
  grupo("sentido", "s", cen.ordem.sentido);
  // checkpoint
  grupo("cpExiste", "v", cen.checkpoint.existe ? 1 : 0);
  $("cpDist").value = cen.checkpoint.dist; $("cpDistVal").textContent = cen.checkpoint.dist + " m";
  $("cpFilas").value = cen.checkpoint.filas; $("cpSeg").value = cen.checkpoint.seg;
  const CA = $("cpAtend"); CA.innerHTML = "";
  cen.zonas.tamanhos.forEach((_, z) => {
    const inp = h("input", {type: "number", min: 1, max: 8, value: cen.checkpoint.atendentes[z], "aria-label": `Atendentes na zona ${LETRAS[z]}`, style: "width:58px"});
    inp.addEventListener("change", () => { cen.checkpoint.atendentes[z] = Math.max(1, Math.round(+inp.value || 1)); atualizaDerivados(); });
    CA.appendChild(h("span", {class: "campo", style: "flex-direction:row;align-items:center;gap:4px"},
      h("span", {class: "swatch", style: `background:${CORES_ZONA[z]}`}), h("span", {class: "mono", text: LETRAS[z]}), inp));
  });
  $("filaLeve").value = cen.filaMesa.leve; $("filaMedia").value = cen.filaMesa.media; $("filaPesada").value = cen.filaMesa.pesada;
  grupo("liberacao", "v", cen.liberacao); $("vazao").value = cen.porta.vazao;
  // comparecimento
  const C = $("comparecimento"); C.innerHTML = "";
  for (const k of Object.keys(M.COMPARECIMENTO)) {
    const b = h("button", {"data-v": k, "aria-pressed": String(k === cen.comparecimento), text: M.COMPARECIMENTO[k].rotulo});
    b.addEventListener("click", () => { cen.comparecimento = k; grupo("comparecimento", "v", k); atualizaDerivados(); });
    C.appendChild(b);
  }
  grupo("tId", "v", cen.tempos.identificacao);
  $("tVoto").value = cen.tempos.voto; $("cv").value = cen.tempos.cv; $("just").value = Math.round((cen.extras.justificativas || 0) * 100);
  $("triAtend").value = cen.ring3.atendentes; $("triSeg").value = cen.ring3.seg; $("ring3Cap").value = cen.ring3.capacidade;
  $("runs").value = cen.sim.runs; $("seed").value = cen.sim.seed;
  for (const b of document.querySelectorAll("#tela-premissas [data-base]")) b.setAttribute("aria-pressed", String(b.dataset.base === (cen.salao.base || "A")));
  const na = (cen.salao.alteracoes || []).length;
  $("alteracoesInfo").textContent = na ? `${na} mesa${na > 1 ? "s" : ""} deslocada${na > 1 ? "s" : ""} em relação à planta original` : "planta original";
}

function ligaControles(){
  $("nomeCenario").addEventListener("input", ev => { cen.nome = ev.target.value; $("nomeAtual").textContent = cen.nome; guardaRascunho(); });
  for (const b of document.querySelectorAll("#tela-premissas [data-base]"))
    b.addEventListener("click", () => { cen.salao = {base: b.dataset.base, alteracoes: []}; preencher(); atualizaDerivados(); });
  for (const b of $("nZonas").querySelectorAll("button"))
    b.addEventListener("click", () => {
      const n = +b.dataset.n;
      cen.zonas.tamanhos = n === 2 ? [16, 12] : (n === 3 ? [8, 12, 8] : [8, 6, 6, 8]);
      cen.zonas.portas = cen.zonas.tamanhos.map((_, z) => cen.zonas.portas[z] || cen.zonas.portas[0]);
      cen.checkpoint.atendentes = cen.zonas.tamanhos.map((_, z) => cen.checkpoint.atendentes[z] || 2);
      normaliza(cen); preencher(); atualizaDerivados();
    });
  $("inicioZona1").addEventListener("change", ev => { cen.zonas.inicio = Math.max(1, Math.min(28, Math.round(+ev.target.value || 1))); atualizaDerivados(); });
  for (const b of $("sentido").querySelectorAll("button"))
    b.addEventListener("click", () => { cen.ordem.sentido = b.dataset.s; grupo("sentido", "s", b.dataset.s); atualizaDerivados(); });
  for (const b of $("cpExiste").querySelectorAll("button"))
    b.addEventListener("click", () => { cen.checkpoint.existe = b.dataset.v === "1"; grupo("cpExiste", "v", b.dataset.v); atualizaDerivados(); });
  $("cpDist").addEventListener("input", ev => { cen.checkpoint.dist = +ev.target.value; $("cpDistVal").textContent = cen.checkpoint.dist + " m"; atualizaDerivados(); });
  $("cpFilas").addEventListener("change", ev => { cen.checkpoint.filas = Math.max(1, Math.round(+ev.target.value || 1)); atualizaDerivados(); });
  $("cpSeg").addEventListener("change", ev => { cen.checkpoint.seg = Math.max(2, +ev.target.value || 8); atualizaDerivados(); });
  for (const [id, k] of [["filaLeve", "leve"], ["filaMedia", "media"], ["filaPesada", "pesada"]])
    $(id).addEventListener("change", ev => { cen.filaMesa[k] = Math.max(1, Math.round(+ev.target.value || 1)); atualizaDerivados(); });
  for (const b of $("liberacao").querySelectorAll("button"))
    b.addEventListener("click", () => { cen.liberacao = b.dataset.v; grupo("liberacao", "v", b.dataset.v); atualizaDerivados(); });
  $("vazao").addEventListener("change", ev => { cen.porta.vazao = Math.max(5, +ev.target.value || 30); atualizaDerivados(); });
  for (const b of $("tId").querySelectorAll("button"))
    b.addEventListener("click", () => { cen.tempos.identificacao = +b.dataset.v; grupo("tId", "v", b.dataset.v); atualizaDerivados(); });
  $("tVoto").addEventListener("change", ev => { cen.tempos.voto = Math.max(5, +ev.target.value || 30); atualizaDerivados(); });
  $("cv").addEventListener("change", ev => { cen.tempos.cv = Math.max(0, Math.min(1, +ev.target.value || 0)); atualizaDerivados(); });
  $("just").addEventListener("change", ev => { cen.extras.justificativas = Math.max(0, Math.min(0.5, (+ev.target.value || 0) / 100)); atualizaDerivados(); });
  $("triAtend").addEventListener("change", ev => { cen.ring3.atendentes = Math.max(1, Math.round(+ev.target.value || 1)); atualizaDerivados(); });
  $("triSeg").addEventListener("change", ev => { cen.ring3.seg = Math.max(1, +ev.target.value || 6); atualizaDerivados(); });
  $("ring3Cap").addEventListener("change", ev => { cen.ring3.capacidade = Math.max(50, Math.round(+ev.target.value || 800)); atualizaDerivados(); });
  $("runs").addEventListener("change", ev => { cen.sim.runs = Math.max(1, Math.min(60, Math.round(+ev.target.value || 12))); guardaRascunho(); });
  $("seed").addEventListener("change", ev => { cen.sim.seed = Math.max(1, Math.round(+ev.target.value || 7)); guardaRascunho(); });

  $("btnClaude").addEventListener("click", () => aplica(M.cenarioClaude()));
  $("btnPadrao").addEventListener("click", () => aplica(M.cenarioPadrao()));
  $("btnCopiar").addEventListener("click", async () => {
    const b = $("btnCopiar");
    try { await navigator.clipboard.writeText(JSON.stringify(cen)); b.textContent = "Copiado"; }
    catch (e) { b.textContent = "Não deu (veja o console)"; console.log(JSON.stringify(cen)); }
    setTimeout(() => { b.textContent = "Copiar cenário"; }, 1800);
  });
  $("btnColar").addEventListener("click", () => { $("colarCaixa").hidden = false; $("colarTexto").focus(); });
  $("colarCancelar").addEventListener("click", () => { $("colarCaixa").hidden = true; });
  $("colarAplicar").addEventListener("click", () => {
    let obj;
    try { obj = JSON.parse($("colarTexto").value); } catch (e) { alert("Isso não é um JSON válido."); return; }
    $("colarCaixa").hidden = true; $("colarTexto").value = "";
    if (obj && obj.zonas && obj.portas) { aplica(obj); return; }
    if (obj && (obj.base === "A" || obj.base === "B") && (Array.isArray(obj.alteracoes) || Array.isArray(obj.mrvs))) {
      // cenário salvo da prancheta: só muda o salão
      let alteracoes = obj.alteracoes || [];
      if (Array.isArray(obj.mrvs) && obj.mrvs.length === 28) {
        const orig = BASE.cenarios[obj.base].mrvs;
        alteracoes = obj.mrvs.filter(m => { const o = orig.find(q => q.n === m.n); return o && (o.x !== m.x || o.y !== m.y || o.rot !== m.rot); })
          .map(m => ({n: m.n, x: m.x, y: m.y, rot: m.rot, lado: m.lado}));
      }
      cen.salao = {base: obj.base, alteracoes};
      if (obj.nome) cen.nome = `${cen.nome || "cenário"} · salão “${obj.nome}”`;
      preencher(); atualizaDerivados(); guardaRascunho();
      return;
    }
    alert("JSON reconhecido nem como cenário do simulador nem como cenário salvo da prancheta.");
  });

  for (const b of document.querySelectorAll(".abas button")) b.addEventListener("click", () => mostraTela(b.dataset.tela));
  $("rodar").addEventListener("click", rodar);
  $("tempo").addEventListener("input", ev => { tempoIdx = +ev.target.value; pintaMinuto(); });
  $("play").addEventListener("click", togglePlay);
}

function mostraTela(nome){
  for (const s of document.querySelectorAll(".tela")) s.classList.toggle("ativa", s.id === "tela-" + nome);
  for (const b of document.querySelectorAll(".abas button")) b.setAttribute("aria-selected", String(b.dataset.tela === nome));
  if (nome !== "simulacao" && tocando) togglePlay();
}

/* ---- derivados da tela 1 ---- */
function atualizaDerivados(){
  normaliza(cen);
  try { mont = M.montar(BASE, MRVS, cen); } catch (e) { console.error(e); return; }
  $("nomeAtual").textContent = cen.nome || "";
  desenhaPortas(); desenhaZonasMini(); tabelaZonas(); kpisEstaticos(); guardaRascunho();
  $("cpCap").textContent = cen.checkpoint.existe
    ? `Cabem ${mont.zonas.map(z => `${z.capBuffer} na ${z.letra}`).join(", ")} entre porta e checkpoint (${cen.checkpoint.filas} fila${cen.checkpoint.filas > 1 ? "s" : ""}, 0,6 m por pessoa).`
    : "Sem checkpoint, a porta libera enquanto houver vaga somada nas filas das mesas da zona.";
  const n = {leve: 0, media: 0, pesada: 0}; for (const m of mont.mesas) n[m.classe]++;
  $("filaInfo").textContent = `${n.leve} leves · ${n.media} médias · ${n.pesada} pesadas · ${vg(mont.fitaMesas, 0)} m de fita nas mesas`;
  const tx = mont.taxa;
  $("compInfo").textContent = `Dublin ${Math.round(tx.dublin * 100)} % · interior ${Math.round(tx.interior * 100)} % → ${fmt(mont.esperadosTotal)} eleitores esperados, mais ${Math.round((cen.extras.justificativas || 0) * 100)} % de atendimentos sem voto.`;
}

function estadoPorta(id){ return cen.portas[id] || "fechada"; }
function desenhaPortas(){
  const svg = $("svgPortas"); svg.innerHTML = "";
  const esc = 540 / LARG, x0 = 10, yFach = 44;
  el("line", {x1: x0, y1: yFach, x2: x0 + LARG * esc, y2: yFach, stroke: "var(--traco)", "stroke-width": 2}, svg);
  // recorte (parede começa em 7,8 m)
  el("line", {x1: x0, y1: yFach, x2: x0 + BASE.salao.recorte[2] * esc, y2: yFach, stroke: "var(--regua)", "stroke-width": 2}, svg);
  const t0 = el("text", {x: x0, y: 62, "font-size": 9, fill: "var(--fraco)"}, svg); t0.textContent = "oeste";
  const t1 = el("text", {x: x0 + LARG * esc, y: 62, "font-size": 9, fill: "var(--fraco)", "text-anchor": "end"}, svg); t1.textContent = "leste";
  for (const p of SUL) {
    const emerg = p.estado === "emergencia";
    const est = emerg ? "emergencia" : estadoPorta(p.id);
    const cor = {entrada: "var(--entrada)", saida: "var(--saida)", fechada: "var(--regua)", emergencia: "var(--emerg)"}[est];
    const g = el("g", {class: emerg ? "" : "porta", tabindex: emerg ? -1 : 0, role: emerg ? null : "button",
      "aria-label": `${p.id}: ${est}`}, svg);
    const x = x0 + p.x1 * esc, w = Math.max(4, (p.x2 - p.x1) * esc);
    el("rect", {x, y: yFach - 9, width: w, height: 18, fill: cor, stroke: "var(--folha)", "stroke-width": 1}, g);
    el("rect", {x: x - 6, y: 4, width: w + 12, height: 52, fill: "transparent"}, g);
    const t = el("text", {x: x + w / 2, y: 24, "font-size": 10, "font-weight": 600, fill: "var(--tinta)", "text-anchor": "middle"}, g); t.textContent = p.id;
    const zonasNaPorta = mont.zonas.filter(z => z.porta === p.id).map(z => z.letra);
    if (est === "entrada" && zonasNaPorta.length) {
      const tz = el("text", {x: x + w / 2, y: 13, "font-size": 9, fill: "var(--meio)", "text-anchor": "middle", "font-weight": 600}, g); tz.textContent = "zona " + zonasNaPorta.join("+");
    }
    const tl = el("text", {x: x + w / 2, y: 70, "font-size": 8, fill: "var(--fraco)", "text-anchor": "middle"}, g); tl.textContent = vg(p.larg, 1) + " m";
    if (!emerg) {
      const alterna = () => { const ordem = ["fechada", "entrada", "saida"]; cen.portas[p.id] = ordem[(ordem.indexOf(estadoPorta(p.id)) + 1) % 3]; normaliza(cen); preencher(); atualizaDerivados(); };
      g.addEventListener("click", alterna);
      g.addEventListener("keydown", ev => { if (ev.key === "Enter" || ev.key === " ") { ev.preventDefault(); alterna(); } });
    }
  }
}

function desenhaZonasMini(){
  const svg = $("svgZonas"); svg.innerHTML = "";
  const esc = 5.4, ox = 14, oy = 12;
  const X = v => ox + v * esc, Y = v => oy + (ALT - v) * esc;
  const pts = BASE.salao.contorno.map(p => `${X(p[0])},${Y(p[1])}`).join(" ");
  el("polygon", {points: pts, fill: "var(--prancha)", stroke: "var(--traco)", "stroke-width": .8}, svg);
  for (const m of mont.mesas) {
    const r = m.corpo, cor = CORES_ZONA[m.zona];
    el("rect", {x: X(r[0]), y: Y(r[3]), width: (r[2] - r[0]) * esc, height: (r[3] - r[1]) * esc, fill: cor, opacity: .85}, svg);
    const t = el("text", {x: X((r[0] + r[2]) / 2), y: Y((r[1] + r[3]) / 2) + 2.6, "font-size": 6.4, "font-weight": 600, fill: "#fff", "text-anchor": "middle", "font-family": "IBM Plex Mono, monospace"}, svg);
    t.textContent = m.mrv;
  }
  for (const p of SUL) {
    const est = p.estado === "emergencia" ? "emergencia" : estadoPorta(p.id);
    const cor = {entrada: "var(--entrada)", saida: "var(--saida)", fechada: "var(--regua)", emergencia: "var(--emerg)"}[est];
    el("line", {x1: X(p.x1), y1: Y(0), x2: X(p.x2), y2: Y(0), stroke: cor, "stroke-width": 3}, svg);
    if (est !== "fechada" && est !== "emergencia") { const t = el("text", {x: X((p.x1 + p.x2) / 2), y: Y(0) + 9, "font-size": 6.5, fill: "var(--meio)", "text-anchor": "middle"}, svg); t.textContent = p.id; }
  }
  for (const z of mont.zonas) {
    if (z.checkpoint) {
      el("line", {x1: X(z.portaCentro[0]), y1: Y(0), x2: X(z.checkpoint[0]), y2: Y(z.checkpoint[1]), stroke: CORES_ZONA[z.idx], "stroke-width": 1.2, "stroke-dasharray": "2 2"}, svg);
      el("circle", {cx: X(z.checkpoint[0]), cy: Y(z.checkpoint[1]), r: 3.2, fill: CORES_ZONA[z.idx], stroke: "var(--prancha)", "stroke-width": 1}, svg);
      const t = el("text", {x: X(z.checkpoint[0]), y: Y(z.checkpoint[1]) - 5, "font-size": 7, "font-weight": 700, fill: "var(--tinta)", "text-anchor": "middle"}, svg); t.textContent = z.letra;
    }
  }
  const t = el("text", {x: X(LARG / 2), y: Y(ALT) - 4, "font-size": 6.5, fill: "var(--fraco)", "text-anchor": "middle"}, svg); t.textContent = "norte";
}

function tabelaZonas(){
  const T = $("tabZonas"); T.innerHTML = "";
  const entradas = SUL_USAVEIS.filter(id => cen.portas[id] === "entrada");
  T.appendChild(h("thead", null, h("tr", null,
    h("th", {text: "Zona"}), h("th", {text: "Slots"}), h("th", {text: "MRV"}), h("th", {class: "num", text: "Mesas"}),
    h("th", {class: "num", text: "Eleitores"}), h("th", {text: "Entra por"}))));
  const tb = h("tbody");
  for (const z of mont.zonas) {
    const sel = h("select", {"aria-label": `Porta de entrada da zona ${z.letra}`});
    for (const id of entradas) sel.appendChild(h("option", {value: id, text: id, selected: id === z.porta ? "" : null}));
    if (!entradas.includes(z.porta)) sel.appendChild(h("option", {value: z.porta, text: z.porta, selected: ""}));
    sel.value = z.porta;
    sel.addEventListener("change", () => { cen.zonas.portas[z.idx] = sel.value; atualizaDerivados(); });
    const arco = z.slots[0] === z.slots[z.slots.length - 1] ? `${z.slots[0]}` : `${z.slots[0]}→${z.slots[z.slots.length - 1]}`;
    tb.appendChild(h("tr", null,
      h("td", null, h("span", {class: "swatch", style: `background:${CORES_ZONA[z.idx]}`}), h("strong", {text: z.letra})),
      h("td", {class: "mono", text: arco}), h("td", {class: "mono", text: z.faixaMrv}),
      h("td", {class: "num", text: z.mesas.length}), h("td", {class: "num", text: fmt(z.esperados)}), h("td", null, sel)));
  }
  T.appendChild(tb);
  // carga (lateral)
  const C = $("tabCarga"); C.innerHTML = "";
  C.appendChild(h("thead", null, h("tr", null, h("th", {text: "Zona"}), h("th", {class: "num", text: "Mesas"}), h("th", {class: "num", text: "Eleit."}), h("th", {class: "num", text: "por mesa"}), h("th", {text: "Porta"}))));
  const cb = h("tbody");
  for (const z of mont.zonas) cb.appendChild(h("tr", null,
    h("td", null, h("span", {class: "swatch", style: `background:${CORES_ZONA[z.idx]}`}), z.letra + " · MRV " + z.faixaMrv),
    h("td", {class: "num", text: z.mesas.length}), h("td", {class: "num", text: fmt(z.esperados)}),
    h("td", {class: "num", text: fmt(z.esperados / z.mesas.length)}), h("td", {class: "mono", text: z.porta})));
  C.appendChild(cb);
}

function kpisEstaticos(){
  const K = $("kpiEstatico"); K.innerHTML = "";
  const add = (k, v, cls) => { K.appendChild(h("dt", {text: k})); K.appendChild(h("dd", {class: cls || "", text: v})); };
  add("Eleitores esperados", fmt(mont.esperadosTotal));
  add("Média por mesa", fmt(mont.esperadosTotal / 28));
  const cap = 28 * 60 / Math.max(cen.tempos.identificacao, cen.tempos.voto);
  add("Capacidade das mesas", vg(cap, 0) + " /min");
  add("Pico de chegada (≈)", vg(mont.esperadosTotal * 0.16 / 60, 0) + " /min");
  add("Desequilíbrio entre portas", vg(mont.desequilibrio, 2) + "×", mont.desequilibrio > 1.5 ? "ruim" : (mont.desequilibrio <= 1.25 ? "bom" : ""));
  add("Saída cruza corredor de entrada", pct(mont.fracaoCruza) + " dos eleitores", mont.fracaoCruza > 0.15 ? "ruim" : (mont.fracaoCruza === 0 ? "bom" : ""));
  add("Fita de unifila", vg(mont.separadores, 0) + " m de " + mont.limiteSeparadores, mont.separadores > mont.limiteSeparadores ? "ruim" : "bom");
  add("Conflitos de fila", String(mont.conflitos.length), mont.conflitos.length ? "ruim" : "bom");
  if (cen.checkpoint.existe) add("Checkpoint → mesa (média)", vg(mont.zonas.reduce((s, z) => s + z.distCpMedia * z.mesas.length, 0) / 28, 0) + " m");
  const A = $("avisos"); A.innerHTML = "";
  const avisos = mont.avisos.slice();
  for (const c of mont.conflitos.slice(0, 4)) avisos.push(`Fila da MRV ${c.mesa} invade ${c.com}.`);
  if (mont.mesmaPorta.length) avisos.push(`Entrada e saída pela mesma porta: ${mont.mesmaPorta.join(", ")}.`);
  if (!mont.saidas.length) avisos.push("Nenhuma porta de saída marcada: os eleitores saem pela porta em que entraram.");
  if (mont.zonas.some(z => z.dividePorta)) avisos.push("Duas zonas dividem a mesma porta de entrada; a vazão da porta é partilhada.");
  A.textContent = avisos.length ? "" : "Nenhum.";
  for (const a of avisos) A.appendChild(h("p", {class: "dica", text: a}));
}

function desenhaCurva(){
  const svg = $("svgCurva"); svg.innerHTML = "";
  const W = 560, H = 130, ml = 30, mr = 10, mt = 14, mb = 26;
  const n = M.CURVA_CHEGADA.length, pw = W - ml - mr, ph = H - mt - mb;
  const maxV = Math.max(...M.CURVA_CHEGADA);
  const yTicks = [0, 4, 8];
  for (const v of yTicks) {
    const y = mt + ph - v / maxV * ph;
    el("line", {x1: ml, y1: y, x2: W - mr, y2: y, stroke: v === 0 ? "var(--eixo)" : "var(--grade)", "stroke-width": 1}, svg);
    const t = el("text", {x: ml - 6, y: y + 3, "font-size": 9, fill: "var(--fraco)", "text-anchor": "end", "font-family": "IBM Plex Mono, monospace"}, svg); t.textContent = v + "%";
  }
  const bw = Math.min(22, pw / n - 4);
  M.CURVA_CHEGADA.forEach((v, i) => {
    const x = ml + (i + 0.5) * pw / n - bw / 2, hgt = v / maxV * ph, y = mt + ph - hgt;
    const g = el("g", {}, svg);
    el("path", {d: `M${x},${mt + ph} L${x},${y + 3} Q${x},${y} ${x + 3},${y} L${x + bw - 3},${y} Q${x + bw},${y} ${x + bw},${y + 3} L${x + bw},${mt + ph} Z`, fill: "var(--z1)"}, g);
    el("rect", {x: x - 2, y: mt, width: bw + 4, height: ph, fill: "transparent"}, g);
    const hora = 7 + Math.floor(i / 2), meia = i % 2 ? "30" : "00";
    tooltip(g, () => `<b>${v} %</b> dos eleitores chegam entre ${hora}h${meia} e ${i % 2 ? hora + 1 + "h00" : hora + "h30"}`);
    if (i % 2 === 0) { const t = el("text", {x: x + bw / 2, y: H - 10, "font-size": 9, fill: "var(--fraco)", "text-anchor": "middle", "font-family": "IBM Plex Mono, monospace"}, svg); t.textContent = hora + "h"; }
    if (v === maxV) { const t = el("text", {x: x + bw / 2, y: y - 4, "font-size": 9, fill: "var(--meio)", "text-anchor": "middle", "font-family": "IBM Plex Mono, monospace"}, svg); t.textContent = v + " %"; }
  });
  const ab = ml + 2 * pw / n;
  el("line", {x1: ab, y1: mt, x2: ab, y2: mt + ph, stroke: "var(--meio)", "stroke-width": 1}, svg);
  const t = el("text", {x: ab + 4, y: mt + 8, "font-size": 9, fill: "var(--meio)", "font-family": "IBM Plex Mono, monospace"}, svg); t.textContent = "abertura 8h";
}

/* tooltip genérico */
const TIP = $("tip");
function tooltip(alvo, texto){
  const mostra = ev => { TIP.innerHTML = typeof texto === "function" ? texto() : texto; TIP.style.display = "block"; move(ev); };
  const move = ev => { const x = ev.clientX + 14, y = ev.clientY + 14; TIP.style.left = Math.min(x, window.innerWidth - TIP.offsetWidth - 8) + "px"; TIP.style.top = Math.min(y, window.innerHeight - TIP.offsetHeight - 8) + "px"; };
  alvo.addEventListener("pointerenter", mostra); alvo.addEventListener("pointermove", move);
  alvo.addEventListener("pointerleave", () => { TIP.style.display = "none"; });
  alvo.addEventListener("focus", ev => mostra({clientX: 200, clientY: 200})); alvo.addEventListener("blur", () => { TIP.style.display = "none"; });
}

/* ------------------------------------------------------------------ */
/* Rodar                                                               */
/* ------------------------------------------------------------------ */
function rodar(){
  if (!mont) atualizaDerivados();
  const btn = $("rodar"); btn.disabled = true; btn.textContent = "Simulando…";
  const P = $("progresso"); P.hidden = false; P.firstElementChild.style.width = "0";
  const montagem = M.montar(BASE, MRVS, cen);
  const runs = cen.sim.runs, seed = cen.sim.seed, dias = [];
  let i = 0;
  const passo = () => {
    const t0 = performance.now();
    while (i < runs && performance.now() - t0 < 120) { dias.push(M.simularDia(montagem, seed + i * 7919)); i++; }
    P.firstElementChild.style.width = (100 * i / runs) + "%";
    if (i < runs) { setTimeout(passo, 0); return; }
    res = M.agregar(montagem, dias);
    btn.disabled = false; btn.textContent = "Rodar simulação"; P.hidden = true;
    pintaSimulacao(); pintaResultado();
    if ($("tela-premissas").classList.contains("ativa")) mostraTela("resultado");
  };
  setTimeout(passo, 0);
}

/* ------------------------------------------------------------------ */
/* Tela 2: simulação                                                   */
/* ------------------------------------------------------------------ */
let gEstatico, gDinamico, refs = {};
function pintaSimulacao(){
  $("simVazio").hidden = true; $("simConteudo").hidden = false;
  const L = res.ref.linha;
  const sl = $("tempo"); sl.max = L.t.length - 1;
  tempoIdx = Math.min(L.t.length - 1, 60 + 120); sl.value = tempoIdx;
  desenhaPlanta(); pintaMinuto(); kpisDia(); graficos();
}
function desenhaPlanta(){
  const svg = $("svgPlanta"); svg.innerHTML = "";
  const mo = res.mont, Mm = mo.M;
  el("rect", {x: -10, y: -10, width: LARG + 20, height: ALT + 30, fill: "var(--prancha)"}, svg);
  const pts = BASE.salao.contorno.map(p => `${p[0]},${fy(p[1])}`).join(" ");
  el("polygon", {points: pts, fill: "var(--folha)", stroke: "var(--traco)", "stroke-width": .18}, svg);
  gEstatico = el("g", {}, svg);
  // buffers e checkpoints
  for (const z of mo.zonas) {
    if (z.bufferRect) {
      const r = z.bufferRect;
      el("rect", {x: r[0], y: fy(r[3]), width: r[2] - r[0], height: r[3] - r[1], fill: CORES_ZONA[z.idx], opacity: .10}, gEstatico);
      el("line", {x1: z.checkpoint[0] - 2, y1: fy(z.checkpoint[1]), x2: z.checkpoint[0] + 2, y2: fy(z.checkpoint[1]), stroke: CORES_ZONA[z.idx], "stroke-width": .3}, gEstatico);
      const t = el("text", {x: z.checkpoint[0], y: fy(z.checkpoint[1]) - .6, "font-size": .9, "font-weight": 700, fill: "var(--tinta)", "text-anchor": "middle", "font-family": "IBM Plex Sans, sans-serif"}, gEstatico);
      t.textContent = `cp ${z.letra}`;
    }
  }
  // portas
  for (const p of BASE.portas) {
    const est = p.face === "sul" && p.estado !== "emergencia" ? (cen.portas[p.id] || "fechada") : (p.estado === "emergencia" ? "emergencia" : "outra");
    const cor = {entrada: "var(--entrada)", saida: "var(--saida)", fechada: "var(--regua)", emergencia: "var(--emerg)", outra: "var(--regua)"}[est];
    el("line", {x1: p.x1, y1: fy(p.y1), x2: p.x2, y2: fy(p.y2), stroke: cor, "stroke-width": .4}, gEstatico);
    if (p.face === "sul" && (est === "entrada" || est === "saida")) {
      const t = el("text", {x: (p.x1 + p.x2) / 2, y: fy(0) + 1.4, "font-size": .95, "font-weight": 700, fill: "var(--tinta)", "text-anchor": "middle", "font-family": "IBM Plex Sans, sans-serif"}, gEstatico);
      t.textContent = `${p.id} ${est === "entrada" ? "entrada" : "saída"}`;
    }
  }
  // mesas
  refs = {mesas: {}, filas: {}, ring3: {}, buffer: {}, cp: {}};
  for (const m of mo.mesas) {
    const pos = m.pos, d = M.DIR(pos.rot), p = M.CCW(d), cor = CORES_ZONA[m.zona];
    const P = (u, v) => [pos.x + d[0] * u + p[0] * v, pos.y + d[1] * u + p[1] * v];
    const g = el("g", {}, gEstatico);
    const r = m.corpo;
    el("rect", {x: r[0], y: fy(r[3]), width: r[2] - r[0], height: r[3] - r[1], fill: cor, opacity: .12}, g);
    const c = [P(Mm.prof - Mm.mesa[0], -Mm.mesa[1] / 2), P(Mm.prof, -Mm.mesa[1] / 2), P(Mm.prof, Mm.mesa[1] / 2), P(Mm.prof - Mm.mesa[0], Mm.mesa[1] / 2)];
    const mesa = el("polygon", {points: c.map(q => `${q[0]},${fy(q[1])}`).join(" "), fill: "var(--mesa)", opacity: .85}, g);
    const cu = P(Mm.eleitor + Mm.urna / 2, 0);
    const urna = el("circle", {cx: cu[0], cy: fy(cu[1]), r: Mm.urna / 2 - .1, fill: "none", stroke: cor, "stroke-width": .12}, g);
    const q = P(Mm.prof - Mm.mesa[0] / 2, 0);
    const t = el("text", {x: q[0], y: fy(q[1]) + .25, "font-size": .68, "font-weight": 700, fill: "var(--prancha)", "text-anchor": "middle", "font-family": "IBM Plex Mono, monospace"}, g);
    t.textContent = m.mrv;
    // fila: L posições
    const gf = el("g", {}, g); const dots = [];
    for (let k = 0; k < m.L; k++) {
      const pt = [m.frente[0] + d[0] * (k + .5) * M.PASSO_FILA, m.frente[1] + d[1] * (k + .5) * M.PASSO_FILA];
      dots.push(el("circle", {cx: pt[0], cy: fy(pt[1]), r: .21, fill: "none", stroke: "var(--pessoa)", "stroke-width": .06, opacity: .6}, gf));
    }
    const extra = el("text", {x: m.cauda[0] + d[0] * .9, y: fy(m.cauda[1] + d[1] * .9) + .3, "font-size": .8, "font-weight": 700, fill: "var(--falha)", "text-anchor": "middle", "font-family": "IBM Plex Mono, monospace"}, g);
    extra.textContent = "";
    refs.mesas[m.slot] = {mesa, urna, dots, extra, cor};
    const hit = el("rect", {x: r[0] - .3, y: fy(r[3]) - .3, width: r[2] - r[0] + .6, height: r[3] - r[1] + .6, fill: "transparent"}, g);
    tooltip(hit, () => {
      const i = tempoIdx, idx = mo.mesas.indexOf(m), L = res.ref.linha;
      const pm = res.porMesa[idx];
      return `<b>MRV ${m.mrv}</b> · seção ${m.secao}${m.agregada ? " + " + m.agregada : ""} · ${m.aptos} aptos (${m.classe})<br>` +
        `zona ${mo.zonas[m.zona].letra} · fila de ${m.L} · ${fmt(m.esperados)} eleitores esperados<br>` +
        `agora: ${L.mesaFila[idx][i]} na fila · ${["urna e mesário parados", "identificando", "identificando e votando", "votando", "mesário esperando a urna"][L.mesaEstado[idx][i]]}<br>` +
        `dia: fecha ${M.hhmm(pm.fecha)} · urna ${pct(pm.ocupUrna)} · fome ${min(pm.fome)} · fila máx ${pm.filaMax}`;
    });
  }
  // Ring 3: barras abaixo da fachada, uma por zona
  gDinamico = el("g", {}, svg);
  for (const z of mo.zonas) {
    const x = z.portaCentro[0] + (z.dividePorta ? (z.idx % 2 ? 1.4 : -1.4) : 0);
    const bar = el("rect", {x: x - 1.1, y: fy(0) + 2.2, width: 2.2, height: 0, fill: CORES_ZONA[z.idx], opacity: .8}, gDinamico);
    const t = el("text", {x, y: fy(0) + 3.6, "font-size": .95, "font-weight": 600, fill: "var(--tinta)", "text-anchor": "middle", "font-family": "IBM Plex Mono, monospace"}, gDinamico);
    const tb = el("text", {x: z.checkpoint ? z.checkpoint[0] : x, y: z.checkpoint ? fy(z.checkpoint[1] / 2) + .3 : fy(0) - 1, "font-size": .9, "font-weight": 600, fill: "var(--tinta)", "text-anchor": "middle", "font-family": "IBM Plex Mono, monospace"}, gDinamico);
    refs.ring3[z.idx] = {bar, t}; refs.buffer[z.idx] = tb;
  }
  const tr = el("text", {x: 2, y: fy(0) + 3.6, "font-size": 1, fill: "var(--meio)", "font-family": "IBM Plex Sans, sans-serif"}, gDinamico);
  tr.textContent = "Ring 3 · fila externa por zona";
  const tn = el("text", {x: LARG / 2, y: -.8, "font-size": .9, fill: "var(--fraco)", "text-anchor": "middle", "font-family": "IBM Plex Sans, sans-serif"}, gEstatico);
  tn.textContent = "norte · parede de fundo";
}
function pintaMinuto(){
  if (!res) return;
  const L = res.ref.linha, i = Math.min(tempoIdx, L.t.length - 1), mo = res.mont;
  $("horaAtual").textContent = M.hhmm(L.t[i]);
  mo.mesas.forEach((m, idx) => {
    const R = refs.mesas[m.slot], n = L.mesaFila[idx][i], cod = L.mesaEstado[idx][i];
    R.dots.forEach((dt, k) => { const cheio = k < n; dt.setAttribute("fill", cheio ? "var(--pessoa)" : "none"); dt.setAttribute("opacity", cheio ? .9 : .5); });
    R.extra.textContent = n > m.L ? `+${n - m.L}` : "";
    R.urna.setAttribute("fill", (cod === 2 || cod === 3 || cod === 4) ? R.cor : "none");
    R.mesa.setAttribute("opacity", (cod === 1 || cod === 2 || cod === 4) ? 1 : .55);
  });
  for (const z of mo.zonas) {
    const r3 = L.ring3[z.idx][i], hgt = Math.min(9, r3 / 60);
    refs.ring3[z.idx].bar.setAttribute("height", hgt);
    refs.ring3[z.idx].t.setAttribute("y", fy(0) + 2.2 + hgt + 1.2);
    refs.ring3[z.idx].t.textContent = r3 ? `${z.letra} ${r3}` : `${z.letra} 0`;
    refs.buffer[z.idx].textContent = z.checkpoint ? `${L.buffer[z.idx][i]}/${z.capBuffer}` : "";
  }
  // estágios
  const E = $("estagios"); E.innerHTML = "";
  const est = (nome, val, sub) => E.appendChild(h("div", {class: "estagio"}, h("span", {text: nome}), h("span", {class: "n", text: val}), sub ? h("span", {class: "sub", text: sub}) : null));
  const ring3 = mo.zonas.map(z => L.ring3[z.idx][i]);
  est("Fora, no Ring 3", fmt(ring3.reduce((a, b) => a + b, 0)), mo.zonas.map(z => `${z.letra} ${ring3[z.idx]}`).join(" · "));
  if (cen.checkpoint.existe) {
    est("Entre porta e checkpoint", fmt(mo.zonas.reduce((s, z) => s + L.buffer[z.idx][i], 0)), mo.zonas.map(z => `${z.letra} ${L.buffer[z.idx][i]}/${z.capBuffer}`).join(" · "));
    est("Na fila do checkpoint", fmt(mo.zonas.reduce((s, z) => s + L.cp[z.idx][i], 0)), mo.zonas.map(z => `${z.letra} ${L.cp[z.idx][i]}`).join(" · "));
  }
  const ociosas = mo.mesas.filter((m, idx) => L.mesaEstado[idx][i] === 0).length;
  const bloqueadas = mo.mesas.filter((m, idx) => L.mesaEstado[idx][i] === 4).length;
  est("Dentro do salão", fmt(L.dentro[i]), `${28 - ociosas} mesas trabalhando · ${ociosas} paradas · ${bloqueadas} esperando a urna`);
  est("Já votaram", fmt(L.votados[i]), `${pct(L.votados[i] / Math.max(1, res.ref.votos))} do dia`);
}
function togglePlay(){
  if (tocando) { clearInterval(tocando); tocando = null; $("play").textContent = "▶"; return; }
  $("play").textContent = "❚❚";
  tocando = setInterval(() => {
    const L = res.ref.linha, v = +$("velocidade").value;
    tempoIdx = Math.min(L.t.length - 1, tempoIdx + v / 5);
    $("tempo").value = Math.floor(tempoIdx); pintaMinuto();
    if (tempoIdx >= L.t.length - 1) togglePlay();
  }, 200);
}
function kpisDia(){
  const K = $("kpiDia"); K.innerHTML = "";
  const d = res.ref, add = (k, v) => { K.appendChild(h("dt", {text: k})); K.appendChild(h("dd", {text: v})); };
  add("Eleitores no dia", fmt(d.eleitores));
  add("Última mesa fecha", M.hhmm(d.fechaUltima));
  add("Espera total P90", min(d.totalP90));
  add("Espera fora P90", min(d.esperaForaP90));
  add("Pico dentro do salão", fmt(d.dentroMax));
  add("Pico no Ring 3", fmt(d.ring3TotalMax));
  add("Fome nas mesas pesadas", min(d.fomePesadasMin * 60));
  add("Dias simulados", String(res.resumo.runs));
}

/* ---- gráficos ---- */
function graficos(){
  const G = $("graficos"); G.innerHTML = "";
  const L = res.ref.linha, mo = res.mont;
  const zonasSeries = mo.zonas.map(z => ({nome: `${z.nome} · ${z.porta}`, cor: CORES_ZONA[z.idx], dados: L.ring3[z.idx]}));
  G.appendChild(graficoLinhas({titulo: "Fila externa no Ring 3", sub: "pessoas por zona, dia de referência", t: L.t, series: zonasSeries,
    limite: {v: cen.ring3.capacidade, rotulo: "capacidade do Ring 3"}}));
  if (cen.checkpoint.existe)
    G.appendChild(graficoLinhas({titulo: "Fila no checkpoint", sub: "pessoas esperando o atendente, por zona", t: L.t,
      series: mo.zonas.map(z => ({nome: `${z.nome} · ${z.atendentesCp} atend.`, cor: CORES_ZONA[z.idx], dados: L.cp[z.idx]}))}));
  G.appendChild(graficoLinhas({titulo: "Pessoas dentro do salão", sub: "em fila, sendo atendidas ou saindo", t: L.t,
    series: [{nome: "dentro", cor: "var(--z1)", dados: L.dentro}]}));
  G.appendChild(graficoLinhas({titulo: "Votos acumulados", sub: `${fmt(res.ref.votos)} votos no dia de referência`, t: L.t,
    series: [{nome: "votos", cor: "var(--z1)", dados: L.votados}], marca: {t: M.ENCERRAMENTO, rotulo: "17h"}}));
  G.appendChild(heatmapMesas());
}
function eixoY(max){
  const passo = Math.pow(10, Math.floor(Math.log10(Math.max(1, max))));
  const cand = [passo / 2, passo, passo * 2, passo * 5].find(p => max / p <= 5) || passo * 5;
  const topo = Math.ceil(max / cand) * cand || cand;
  const ticks = []; for (let v = 0; v <= topo + 1e-9; v += cand) ticks.push(v);
  return {topo, ticks};
}
function graficoLinhas(o){
  const W = 560, H = 210, ml = 44, mr = 14, mt = 12, mb = 28, pw = W - ml - mr, ph = H - mt - mb;
  const n = o.t.length, t0 = o.t[0], t1 = o.t[n - 1];
  const maxV = Math.max(1, ...o.series.map(s => Math.max(...s.dados)), o.limite ? o.limite.v : 0);
  const {topo, ticks} = eixoY(maxV);
  const X = t => ml + (t - t0) / (t1 - t0) * pw, Y = v => mt + ph - v / topo * ph;
  const fig = h("figure");
  const cap = h("figcaption", null, o.titulo, h("span", {class: "sub", text: o.sub}));
  fig.appendChild(cap);
  const svg = el("svg", {viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": o.titulo});
  for (const v of ticks) {
    el("line", {x1: ml, y1: Y(v), x2: W - mr, y2: Y(v), stroke: v === 0 ? "var(--eixo)" : "var(--grade)", "stroke-width": 1}, svg);
    const t = el("text", {x: ml - 6, y: Y(v) + 3, "font-size": 9, fill: "var(--fraco)", "text-anchor": "end", "font-family": "IBM Plex Mono, monospace"}, svg); t.textContent = fmt(v);
  }
  for (let hh = Math.ceil(t0 / 3600); hh * 3600 <= t1; hh++) {
    const x = X(hh * 3600);
    const t = el("text", {x, y: H - 10, "font-size": 9, fill: "var(--fraco)", "text-anchor": "middle", "font-family": "IBM Plex Mono, monospace"}, svg); t.textContent = hh + "h";
  }
  if (o.limite && o.limite.v <= topo) {
    el("line", {x1: ml, y1: Y(o.limite.v), x2: W - mr, y2: Y(o.limite.v), stroke: "var(--falha)", "stroke-width": 1, opacity: .7}, svg);
    const t = el("text", {x: W - mr, y: Y(o.limite.v) - 4, "font-size": 9, fill: "var(--meio)", "text-anchor": "end", "font-family": "IBM Plex Mono, monospace"}, svg); t.textContent = o.limite.rotulo;
  }
  if (o.marca) {
    el("line", {x1: X(o.marca.t), y1: mt, x2: X(o.marca.t), y2: mt + ph, stroke: "var(--meio)", "stroke-width": 1}, svg);
    const t = el("text", {x: X(o.marca.t) + 4, y: mt + 9, "font-size": 9, fill: "var(--meio)", "font-family": "IBM Plex Mono, monospace"}, svg); t.textContent = o.marca.rotulo;
  }
  const passo = Math.max(1, Math.floor(n / 280));
  for (const s of o.series) {
    let d = ""; for (let i = 0; i < n; i += passo) d += (i ? "L" : "M") + X(o.t[i]).toFixed(1) + "," + Y(s.dados[i]).toFixed(1);
    if ((n - 1) % passo) d += "L" + X(t1).toFixed(1) + "," + Y(s.dados[n - 1]).toFixed(1);
    if (o.series.length === 1) el("path", {d: d + `L${X(t1)},${Y(0)}L${X(t0)},${Y(0)}Z`, fill: s.cor, opacity: .1}, svg);
    el("path", {d, fill: "none", stroke: s.cor, "stroke-width": 2, "stroke-linejoin": "round", "stroke-linecap": "round"}, svg);
    // ponto e rótulo no máximo
    let im = 0; for (let i = 1; i < n; i++) if (s.dados[i] > s.dados[im]) im = i;
    el("circle", {cx: X(o.t[im]), cy: Y(s.dados[im]), r: 4, fill: s.cor, stroke: "var(--folha)", "stroke-width": 2}, svg);
    const t = el("text", {x: Math.min(W - mr - 20, Math.max(ml + 20, X(o.t[im]))), y: Y(s.dados[im]) - 8, "font-size": 9.5, "font-weight": 600, fill: "var(--tinta)", "text-anchor": "middle", "font-family": "IBM Plex Mono, monospace", "paint-order": "stroke", stroke: "var(--folha)", "stroke-width": 3}, svg);
    t.textContent = fmt(s.dados[im]);
  }
  // crosshair + tooltip
  const cross = el("line", {x1: 0, y1: mt, x2: 0, y2: mt + ph, stroke: "var(--meio)", "stroke-width": 1, opacity: 0}, svg);
  const hit = el("rect", {x: ml, y: mt, width: pw, height: ph, fill: "transparent"}, svg);
  hit.addEventListener("pointermove", ev => {
    const r = svg.getBoundingClientRect(), px = (ev.clientX - r.left) / r.width * W;
    const tt = t0 + (px - ml) / pw * (t1 - t0);
    const i = Math.max(0, Math.min(n - 1, Math.round((tt - t0) / (t1 - t0) * (n - 1))));
    cross.setAttribute("x1", X(o.t[i])); cross.setAttribute("x2", X(o.t[i])); cross.setAttribute("opacity", 1);
    TIP.innerHTML = `<b>${M.hhmm(o.t[i])}</b>` + o.series.map(s => `<br><span style="display:inline-block;width:10px;border-top:2px solid ${s.cor};vertical-align:middle;margin-right:5px"></span><b>${fmt(s.dados[i])}</b> ${s.nome}`).join("");
    TIP.style.display = "block"; TIP.style.left = Math.min(ev.clientX + 14, window.innerWidth - TIP.offsetWidth - 8) + "px"; TIP.style.top = (ev.clientY + 14) + "px";
  });
  hit.addEventListener("pointerleave", () => { cross.setAttribute("opacity", 0); TIP.style.display = "none"; });
  fig.appendChild(svg);
  if (o.series.length > 1) {
    const leg = h("div", {class: "legenda", style: "margin-top:6px"});
    for (const s of o.series) leg.appendChild(h("span", null, h("span", {style: `display:inline-block;width:14px;border-top:2px solid ${s.cor};vertical-align:middle;margin-right:5px`}), s.nome));
    fig.appendChild(leg);
  }
  return fig;
}
function heatmapMesas(){
  const L = res.ref.linha, mo = res.mont, n = L.t.length, linhaPx = 10;
  const fig = h("figure", {style: "grid-column:1/-1"});
  fig.appendChild(h("figcaption", null, "Estado de cada mesa ao longo do dia", h("span", {class: "sub", text: "uma linha por mesa, ordem MRV; passe o mouse para ler"})));
  const wrap = h("div", {style: "display:grid;grid-template-columns:38px 1fr;gap:4px;align-items:start"});
  const rot = h("div", {style: `display:flex;flex-direction:column;font-family:'IBM Plex Mono',monospace;font-size:8.5px;color:var(--meio);line-height:${linhaPx}px`});
  const ordem = mo.mesas.map((m, idx) => ({idx, mrv: m.mrv})).sort((a, b) => a.mrv - b.mrv);
  for (const o of ordem) rot.appendChild(h("span", {text: "MRV " + o.mrv}));
  const cv = document.createElement("canvas"); cv.width = n; cv.height = 28 * linhaPx;
  cv.style.height = (28 * linhaPx) + "px";
  const ctx = cv.getContext("2d");
  const cs = getComputedStyle(document.documentElement);
  const cores = ["rgba(140,140,140,0.18)", cs.getPropertyValue("--z1").trim() + "99", cs.getPropertyValue("--z1").trim(), cs.getPropertyValue("--z1").trim() + "cc", cs.getPropertyValue("--atencao").trim()];
  ordem.forEach((o, row) => {
    const est = L.mesaEstado[o.idx];
    for (let i = 0; i < n; i++) { ctx.fillStyle = cores[est[i]] || cores[0]; ctx.fillRect(i, row * linhaPx, 1, linhaPx - 1); }
  });
  // linha das 17h
  const i17 = L.t.findIndex(t => t >= M.ENCERRAMENTO);
  if (i17 >= 0) { ctx.fillStyle = cs.getPropertyValue("--tinta").trim(); ctx.fillRect(i17, 0, 1, cv.height); }
  cv.addEventListener("pointermove", ev => {
    const r = cv.getBoundingClientRect(); const i = Math.max(0, Math.min(n - 1, Math.floor((ev.clientX - r.left) / r.width * n)));
    const row = Math.max(0, Math.min(27, Math.floor((ev.clientY - r.top) / r.height * 28)));
    const o = ordem[row], m = mo.mesas[o.idx];
    TIP.innerHTML = `<b>MRV ${m.mrv}</b> · ${M.hhmm(L.t[i])}<br>${["urna e mesário parados", "identificando", "identificando e votando", "votando", "mesário esperando a urna"][L.mesaEstado[o.idx][i]]}<br>${L.mesaFila[o.idx][i]} na fila (cabem ${m.L})`;
    TIP.style.display = "block"; TIP.style.left = Math.min(ev.clientX + 14, window.innerWidth - TIP.offsetWidth - 8) + "px"; TIP.style.top = (ev.clientY + 14) + "px";
  });
  cv.addEventListener("pointerleave", () => { TIP.style.display = "none"; });
  wrap.appendChild(rot); wrap.appendChild(cv); fig.appendChild(wrap);
  const eixo = h("div", {style: "display:grid;grid-template-columns:38px 1fr;gap:4px"}, h("span"), h("div", {class: "legenda mono", style: "justify-content:space-between;font-size:.7rem"}));
  const ex = eixo.lastElementChild;
  for (let hh = Math.ceil(L.t[0] / 3600); hh * 3600 <= L.t[n - 1]; hh += 2) ex.appendChild(h("span", {text: hh + "h"}));
  fig.appendChild(eixo);
  const leg = h("div", {class: "legenda", style: "margin-top:6px"});
  [["parada", cores[0]], ["identificando", cores[1]], ["identificando e votando", cores[2]], ["só votando", cores[3]], ["mesário esperando a urna", cores[4]]].forEach(([nome, cor]) =>
    leg.appendChild(h("span", null, h("span", {class: "swatch", style: `background:${cor}`}), nome)));
  fig.appendChild(leg);
  return fig;
}

/* ------------------------------------------------------------------ */
/* Tela 3: resultado                                                   */
/* ------------------------------------------------------------------ */
function pintaResultado(){
  $("resVazio").hidden = true;
  const R = $("resConteudo"); R.hidden = false; R.innerHTML = "";
  const r = res.resumo, V = res.vereditos;
  const nF = V.filter(v => v.status === "falha").length, nA = V.filter(v => v.status === "atencao").length, nO = V.length - nF - nA;
  const selo = {ok: "Aprovado", atencao: "Atenção", falha: "Reprovado"}[res.nota];
  R.appendChild(h("div", {class: "notaGeral"},
    h("div", {class: "selo " + res.nota, text: selo}),
    h("div", null, h("h2", {text: `${cen.nome || "Cenário sem nome"}: ${nO} critérios passam, ${nA} pedem atenção, ${nF} falham`}),
      h("p", {text: res.texto[1]}))));
  const grid = h("div", {class: "vereditos"});
  const icone = {ok: "✓", atencao: "!", falha: "×"};
  for (const v of V) grid.appendChild(h("div", {class: "veredito " + v.status},
    h("span", {class: "icone", text: icone[v.status], "aria-label": v.status}), h("h3", {text: v.titulo}),
    h("span", {class: "valor", text: v.valor}), h("span", {class: "meta", text: "meta " + v.meta}),
    h("p", {class: "porque", text: v.porque + (v.detalhe ? " " + v.detalhe : "")})));
  R.appendChild(grid);
  const prosa = h("div", {class: "prosa"}, h("h2", {text: "O que a simulação diz"}));
  for (const p of res.texto) prosa.appendChild(h("p", {text: p}));
  prosa.appendChild(h("p", {class: "dica", text: "Premissas do modelo: curva de chegada fixa (7h–17h), caminhada a 1,2 m/s, 0,6 m por pessoa em fila, identificação pelo caderno com o mesário identificando o próximo enquanto o anterior vota. Não modelados: chuva, prioridade legal na fila, eleitor na zona errada, apuração."}));
  R.appendChild(prosa);

  // números
  const sec = h("div", {class: "secao"}, h("h2", {text: `Números em ${r.runs} dias simulados`}));
  const tab = h("table", {class: "tabela"});
  tab.appendChild(h("thead", null, h("tr", null, h("th", {text: "Indicador"}), h("th", {class: "num", text: "Dia mediano"}), h("th", {class: "num", text: "Dia ruim (P90)"}), h("th", {class: "num", text: "Pior dia"}))));
  const tb = h("tbody");
  const lin = (nome, a, f) => tb.appendChild(h("tr", null, h("td", {text: nome}), h("td", {class: "num", text: f(a.p50)}), h("td", {class: "num", text: f(a.p90)}), h("td", {class: "num", text: f(a.max)})));
  lin("Última mesa fecha", r.fechaUltima, M.hhmm);
  lin("Espera total, 9 em 10 eleitores", r.totalP90, min);
  lin("Espera fora (Ring 3), P90", r.esperaForaP90, min);
  lin("Espera dentro, P90", r.esperaDentroP90, min);
  lin("Pico de pessoas dentro", r.dentroMax, fmt);
  lin("Pico de pessoas fora", r.ring3TotalMax, fmt);
  lin("Fome total das mesas pesadas", r.fomePesadasMin, v => Math.round(v) + " min");
  lin("Votos", r.votos, fmt);
  tab.appendChild(tb); sec.appendChild(h("div", {class: "rolagem"}, tab)); R.appendChild(sec);

  // por zona
  const secZ = h("div", {class: "secao"}, h("h2", {text: "Por zona"}));
  const tz = h("table", {class: "tabela"});
  tz.appendChild(h("thead", null, h("tr", null, h("th", {text: "Zona"}), h("th", {text: "Porta"}), h("th", {class: "num", text: "Mesas"}), h("th", {class: "num", text: "Eleitores"}),
    h("th", {class: "num", text: "Pico fora"}), h("th", {class: "num", text: "Buffer máx / cabe"}), h("th", {class: "num", text: "Fila checkpoint"}), h("th", {class: "num", text: "Ocup. checkpoint"}), h("th", {class: "num", text: "Fecha"}))));
  const tzb = h("tbody");
  for (const z of res.porZona) tzb.appendChild(h("tr", null,
    h("td", null, h("span", {class: "swatch", style: `background:${CORES_ZONA[z.idx]}`}), `${z.nome} · MRV ${z.faixaMrv}`), h("td", {class: "mono", text: z.porta}),
    h("td", {class: "num", text: z.mesas}), h("td", {class: "num", text: fmt(z.esperados)}), h("td", {class: "num", text: fmt(z.ring3Max)}),
    h("td", {class: "num", text: cen.checkpoint.existe ? `${z.bufferMax} / ${z.capBuffer}` : "—"}), h("td", {class: "num", text: cen.checkpoint.existe ? String(z.cpFilaMax) : "—"}),
    h("td", {class: "num", text: cen.checkpoint.existe ? `${pct(z.cpOcupacao)} (${z.atendentesCp} atend.)` : "—"}), h("td", {class: "num", text: M.hhmm(z.fecha)})));
  tz.appendChild(tzb); secZ.appendChild(h("div", {class: "rolagem"}, tz)); R.appendChild(secZ);

  // por mesa
  const secM = h("div", {class: "secao"}, h("h2", {text: "Por mesa, da que fecha mais tarde à mais cedo"}),
    h("p", {class: "dica", style: "margin-bottom:10px", text: "“Fila necessária” é o maior tamanho que a fila da mesa atingiu; se bate no que cabe, o checkpoint reteve gente. Uso da urna acima de 90 % é mesa saturada. “Fome” é tempo parada enquanto havia gente da zona no Ring 3; em mesa leve é inevitável, porque quem espera lá fora é de outra mesa."}));
  const tm = h("table", {class: "tabela"});
  tm.appendChild(h("thead", null, h("tr", null, h("th", {text: "MRV"}), h("th", {text: "Seções"}), h("th", {class: "num", text: "Aptos"}), h("th", {text: "Zona"}), h("th", {class: "num", text: "Votos"}),
    h("th", {class: "num", text: "Fecha"}), h("th", {class: "num", text: "Uso da urna"}), h("th", {class: "num", text: "Fome"}), h("th", {class: "num", text: "Fila necessária / cabe"}))));
  const tmb = h("tbody");
  const maxOc = Math.max(...res.porMesa.map(m => m.ocupUrna), .01);
  for (const m of res.porMesa.slice().sort((a, b) => b.fecha - a.fecha)) {
    const mm = res.mont.mesas.find(x => x.slot === m.slot);
    tmb.appendChild(h("tr", null,
      h("td", {class: "mono", text: String(m.mrv)}), h("td", {class: "mono", text: `${mm.secao}${mm.agregada ? " + " + mm.agregada : ""}`}),
      h("td", {class: "num", text: String(m.aptos)}), h("td", null, h("span", {class: "swatch", style: `background:${CORES_ZONA[m.zona]}`}), LETRAS[m.zona]),
      h("td", {class: "num", text: fmt(m.votos)}), h("td", {class: "num", text: M.hhmm(m.fecha)}),
      h("td", {class: "num"}, h("span", {class: "barraMesa", style: `width:${Math.round(m.ocupUrna / maxOc * 60)}px;margin-right:6px;background:${m.ocupUrna > .9 ? "var(--falha)" : "var(--z1)"}`}), pct(m.ocupUrna)),
      h("td", {class: "num", text: min(m.fome)}), h("td", {class: "num", text: `${m.filaMax} / ${m.L}`})));
  }
  tm.appendChild(tmb); secM.appendChild(h("div", {class: "rolagem"}, tm)); R.appendChild(secM);

  // comparativo
  R.appendChild(comparativo());
  const acoes = h("div", {class: "linha"});
  const bg = h("button", {class: "acao", text: "Guardar este resultado para comparar"});
  bg.addEventListener("click", () => { guardaComparativo(); pintaResultado(); });
  const bc = h("button", {class: "acao", text: "Copiar relatório (texto)"});
  bc.addEventListener("click", async () => { try { await navigator.clipboard.writeText(relatorioTexto()); bc.textContent = "Copiado"; } catch (e) { bc.textContent = "não deu"; } setTimeout(() => { bc.textContent = "Copiar relatório (texto)"; }, 1800); });
  acoes.appendChild(bg); acoes.appendChild(bc); R.appendChild(acoes);
}
function leComparativo(){ try { return JSON.parse(localStorage.getItem(CHAVE_COMPARATIVO) || "[]"); } catch (e) { return []; } }
function guardaComparativo(){
  const lista = leComparativo(), r = res.resumo;
  lista.unshift({nome: cen.nome || "sem nome", quando: new Date().toISOString().slice(0, 16).replace("T", " "), nota: res.nota,
    falhas: res.vereditos.filter(v => v.status === "falha").length, atencoes: res.vereditos.filter(v => v.status === "atencao").length,
    fecha: r.fechaUltima.p90, p90: r.totalP90.p50, fora: r.ring3TotalMax.p50, cruza: res.mont.fracaoCruza, sep: res.mont.separadores, cen: JSON.parse(JSON.stringify(cen))});
  try { localStorage.setItem(CHAVE_COMPARATIVO, JSON.stringify(lista.slice(0, 12))); } catch (e) {}
}
function comparativo(){
  const lista = leComparativo();
  const sec = h("div", {class: "secao"}, h("h2", {text: "Cenários guardados neste navegador"}));
  if (!lista.length) { sec.appendChild(h("p", {class: "dica", text: "Guarde resultados para compará-los lado a lado. A lista fica só neste navegador."})); return sec; }
  const t = h("table", {class: "tabela comparativo"});
  t.appendChild(h("thead", null, h("tr", null, h("th", {text: "Cenário"}), h("th", {text: "Nota"}), h("th", {class: "num", text: "Falhas"}), h("th", {class: "num", text: "Fecha (P90)"}), h("th", {class: "num", text: "Espera P90"}), h("th", {class: "num", text: "Pico fora"}), h("th", {class: "num", text: "Cruza"}), h("th", {class: "num", text: "Fita"}), h("th"))));
  const tb = h("tbody");
  const melhorP90 = Math.min(...lista.map(x => x.p90)), melhorFecha = Math.min(...lista.map(x => x.fecha));
  lista.forEach((x, i) => {
    const ba = h("button", {class: "acao mini", text: "Abrir premissas"}); ba.addEventListener("click", () => { aplica(x.cen); mostraTela("premissas"); });
    const bx = h("button", {class: "acao mini", text: "×", "aria-label": "Remover"}); bx.addEventListener("click", () => { const l = leComparativo(); l.splice(i, 1); try { localStorage.setItem(CHAVE_COMPARATIVO, JSON.stringify(l)); } catch (e) {} pintaResultado(); });
    tb.appendChild(h("tr", null, h("td", null, h("strong", {text: x.nome}), h("span", {class: "dica", text: " " + x.quando})),
      h("td", null, h("span", {class: "chip " + x.nota, text: {ok: "aprovado", atencao: "atenção", falha: "reprovado"}[x.nota]})),
      h("td", {class: "num", text: `${x.falhas} / ${x.atencoes}`}), h("td", {class: "num" + (x.fecha === melhorFecha ? " melhor" : ""), text: M.hhmm(x.fecha)}),
      h("td", {class: "num" + (x.p90 === melhorP90 ? " melhor" : ""), text: min(x.p90)}), h("td", {class: "num", text: fmt(x.fora)}),
      h("td", {class: "num", text: pct(x.cruza)}), h("td", {class: "num", text: vg(x.sep, 0) + " m"}), h("td", null, ba, " ", bx)));
  });
  t.appendChild(tb); sec.appendChild(h("div", {class: "rolagem"}, t)); return sec;
}
function relatorioTexto(){
  const r = res.resumo, l = [];
  l.push(`# ${cen.nome || "Cenário"} — simulador do Hall 2`, "");
  l.push(...res.texto, "");
  l.push("## Critérios");
  for (const v of res.vereditos) l.push(`- [${{ok: "OK", atencao: "ATENÇÃO", falha: "FALHA"}[v.status]}] ${v.titulo}: ${v.valor} (meta ${v.meta}). ${v.porque}${v.detalhe ? " " + v.detalhe : ""}`);
  l.push("", "## Por zona");
  for (const z of res.porZona) l.push(`- ${z.nome} (MRV ${z.faixaMrv}, porta ${z.porta}): ${fmt(z.esperados)} eleitores, pico fora ${fmt(z.ring3Max)}, checkpoint ${pct(z.cpOcupacao)} com ${z.atendentesCp} atendente(s), fecha ${M.hhmm(z.fecha)}`);
  l.push("", "## Por mesa (fecha, uso da urna, fome, fila necessária/cabe)");
  for (const m of res.porMesa.slice().sort((a, b) => b.fecha - a.fecha)) l.push(`- MRV ${m.mrv} (${m.secao}, ${m.aptos} aptos): ${M.hhmm(m.fecha)}, ${pct(m.ocupUrna)}, ${min(m.fome)}, ${m.filaMax}/${m.L}`);
  l.push("", "## Premissas (JSON)", "```json", JSON.stringify(cen), "```");
  return l.join("\n");
}

/* ------------------------------------------------------------------ */
/* Início                                                              */
/* ------------------------------------------------------------------ */
ligaControles();
desenhaCurva();
aplica(carregaRascunho() || M.cenarioClaude());
rodar();
})();
