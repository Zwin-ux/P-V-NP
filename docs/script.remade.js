(function bootstrap() {
  document.addEventListener('DOMContentLoaded', () => {
    safeInit('Reveal', initReveal);
    safeInit('Handout', initHandoutMode);
    safeInit('SAT', initSAT);
    safeInit('SubsetSum', initSubsetSum);
    safeInit('ReductionBelt', initReductionBelt);
    safeInit('Zoo', initZoo);
    safeInit('GraphColoring', initGraphColoring);
    safeInit('ScalingWall', initScalingWall);
    safeInit('Approximation', initApproxGame);
    safeInit('FPT', initFPTPlayground);
  });

  function safeInit(name, fn) {
    try { fn(); console.debug(`[Init] ${name}: OK`); }
    catch (e) { console.error(`[Init] ${name}: FAILED`, e); }
  }

  const $ = (sel) => document.querySelector(sel);
  const $all = (sel) => Array.from(document.querySelectorAll(sel));
  const el = (tag, props = {}) => Object.assign(document.createElement(tag), props);

  // ---------------------- Entry reveal ----------------------
  function initReveal() {
    const prefersReduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReduce) return;
    const els = $all('.reveal');
    requestAnimationFrame(() => {
      els.forEach((node, i) => {
        node.style.setProperty('--reveal-delay', `${i * 80}ms`);
        node.classList.add('reveal-on');
      });
    });
  }

  // ---------------------- Handout mode ----------------------
  function initHandoutMode() {
    const btn = $('#handout-toggle');
    if (!btn) return;
    btn.addEventListener('click', () => {
      const on = document.body.classList.toggle('handout-mode');
      btn.textContent = on ? 'Exit handout' : 'Handout mode';
    });
  }

  // ---------------------- SAT rail ----------------------
  function initSAT() {
    const presetHost = $('#sat-presets');
    const formulaEl = $('#sat-formula');
    const togglesEl = $('#sat-toggles');
    const clauseLights = $('#sat-clause-lights');
    const resEl = $('#sat-result');
    const metricsEl = $('#sat-metrics');
    const btnCheck = $('#sat-check');
    const btnSolve = $('#sat-solve');
    const resetBtn = $('#reset-verify');
    if (!presetHost || !formulaEl || !togglesEl || !clauseLights) return;

    const PRESETS = [
      { id: 'easy', label: 'Easy SAT', formula: '(x1 | x2) & (!x1 | x3)', expect: 'SAT' },
      { id: 'tricky', label: 'Tricky SAT', formula: '(x1 | !x2 | x3) & (!x1 | x2 | x3) & (x2 | !x3)', expect: 'SAT' },
      { id: 'unsat', label: 'Unsat', formula: '(x1) & (!x1)', expect: 'UNSAT' },
      { id: 'custom', label: 'Custom small', formula: '(x1 | x2) & (x2 | x3)', expect: 'SAT' }
    ];
    let current = PRESETS[0];

    const TOK = { VAR: 'VAR', NOT: 'NOT', AND: 'AND', OR: 'OR', LP: 'LP', RP: 'RP' };
    const PREC = { [TOK.NOT]: 3, [TOK.AND]: 2, [TOK.OR]: 1 };
    const RIGHT = { [TOK.NOT]: true };

    function tokenize(expr) {
      const t = []; const src = (expr || '').replace(/\s+/g, '');
      for (let i = 0; i < src.length; i++) {
        const c = src[i];
        if (c === '(') { t.push({ t: TOK.LP }); continue; }
        if (c === ')') { t.push({ t: TOK.RP }); continue; }
        if (c === '!') { t.push({ t: TOK.NOT }); continue; }
        if (c === '&') { t.push({ t: TOK.AND }); continue; }
        if (c === '|') { t.push({ t: TOK.OR }); continue; }
        if (c === 'x') {
          const n = src[i + 1];
          if (!/[1-9]/.test(n)) throw new Error(`Invalid variable at ${i}`);
          t.push({ t: TOK.VAR, v: `x${n}` }); i++; continue;
        }
        throw new Error(`Unexpected '${c}' at ${i}`);
      }
      return t;
    }

    function toRPN(tokens) {
      const out = [], op = [];
      for (const tk of tokens) {
        if (tk.t === TOK.VAR) out.push(tk);
        else if (tk.t === TOK.NOT || tk.t === TOK.AND || tk.t === TOK.OR) {
          while (op.length) {
            const top = op[op.length - 1]; if (top.t === TOK.LP) break;
            const pTop = PREC[top.t] || 0, pTk = PREC[tk.t] || 0;
            if ((RIGHT[tk.t] && pTk < pTop) || (!RIGHT[tk.t] && pTk <= pTop)) out.push(op.pop()); else break;
          }
          op.push(tk);
        } else if (tk.t === TOK.LP) op.push(tk);
        else if (tk.t === TOK.RP) {
          let f = false;
          while (op.length) { const top = op.pop(); if (top.t === TOK.LP) { f = true; break; } out.push(top); }
          if (!f) throw new Error('Unbalanced parentheses');
        }
      }
      while (op.length) { const top = op.pop(); if (top.t === TOK.LP || top.t === TOK.RP) throw new Error('Unbalanced parentheses'); out.push(top); }
      return out;
    }

    function evalRPN(rpn, env) {
      const st = [];
      for (const tk of rpn) {
        if (tk.t === TOK.VAR) st.push(Boolean(env[tk.v]));
        else if (tk.t === TOK.NOT) { if (!st.length) throw new Error('Parse error'); st.push(!st.pop()); }
        else if (tk.t === TOK.AND || tk.t === TOK.OR) {
          if (st.length < 2) throw new Error('Parse error');
          const b = st.pop(), a = st.pop();
          st.push(tk.t === TOK.AND ? (a && b) : (a || b));
        } else throw new Error('Unknown token');
      }
      if (st.length !== 1) throw new Error('Parse error');
      return st[0];
    }

    function extractVars(expr) {
      const s = new Set(); const re = /x([1-9])/g; let m;
      while ((m = re.exec(expr)) !== null) s.add(`x${m[1]}`);
      return Array.from(s).sort((a, b) => Number(a.slice(1)) - Number(b.slice(1))).slice(0, 9);
    }

    function renderPresets() {
      presetHost.innerHTML = '';
      PRESETS.forEach(p => {
        const b = el('button', { className: 'chip', textContent: p.label, type: 'button' });
        b.addEventListener('click', () => { current = p; loadPreset(); });
        presetHost.appendChild(b);
      });
    }

    function renderToggles(vars) {
      togglesEl.innerHTML = '';
      vars.forEach(name => {
        const b = el('button', { className: 'toggle', type: 'button', textContent: `${name}: false` });
        b.dataset.on = 'false'; b.dataset.varName = name;
        b.setAttribute('aria-pressed', 'false');
        b.addEventListener('click', () => {
          const on = b.dataset.on === 'true';
          b.dataset.on = String(!on);
          b.textContent = `${name}: ${!on}`;
          b.setAttribute('aria-pressed', String(!on));
          updateClauseLights();
        });
        togglesEl.appendChild(b);
      });
    }

    function envFromToggles() {
      const env = {}; togglesEl.querySelectorAll('.toggle').forEach(b => env[b.dataset.varName] = b.dataset.on === 'true');
      return env;
    }

    function clauseList(expr) { return expr.split('&').map(x => x.trim()).filter(Boolean); }

    function updateClauseLights() {
      clauseLights.innerHTML = '';
      const env = envFromToggles();
      const rpnCache = new Map();
      const clauses = clauseList(current.formula);
      clauses.forEach(cl => {
        let rpn = rpnCache.get(cl);
        if (!rpn) { rpn = toRPN(tokenize(cl)); rpnCache.set(cl, rpn); }
        const ok = evalRPN(rpn, env);
        const dot = el('div', { className: `light ${ok ? 'on' : 'off'}` });
        dot.title = ok ? 'Clause satisfied' : 'Clause false';
        clauseLights.appendChild(dot);
      });
    }

    function loadPreset() {
      formulaEl.textContent = current.formula;
      renderToggles(extractVars(current.formula));
      if (resEl) { resEl.textContent = ''; resEl.style.color = ''; }
      if (metricsEl) metricsEl.textContent = '';
      updateClauseLights();
    }

    if (btnCheck) btnCheck.addEventListener('click', () => {
      try {
        const env = envFromToggles();
        const rpn = toRPN(tokenize(current.formula));
        const val = evalRPN(rpn, env);
        resEl.textContent = val ? 'Satisfies under this assignment' : 'Does NOT satisfy';
        resEl.style.color = val ? '#34d399' : '#f87171';
        metricsEl.textContent = `Expectation: ${current.expect}. Clauses lit: ${Array.from(clauseLights.children).filter(x => x.classList.contains('on')).length}/${clauseLights.children.length}.`;
      } catch (e) {
        resEl.textContent = String(e.message || e); resEl.style.color = '#f87171';
      }
    });

    if (btnSolve) btnSolve.addEventListener('click', () => {
      try {
        const names = extractVars(current.formula); const n = names.length;
        if (!n) throw new Error('No variables');
        const limit = 1 << Math.min(n, 12);
        const rpn = toRPN(tokenize(current.formula));
        let found = null, checked = 0;
        for (let mask = 0; mask < limit; mask++) {
          const env = {}; for (let i = 0; i < n; i++) env[names[i]] = !!(mask & (1 << i));
          checked++; if (evalRPN(rpn, env)) { found = env; break; }
        }
        if (found) {
          resEl.textContent = 'SAT (witness below)';
          resEl.style.color = '#34d399';
          metricsEl.textContent = names.map(k => `${k}=${found[k]}`).join(', ') + ` | Checked ${checked} assignments.`;
          togglesEl.querySelectorAll('.toggle').forEach(b => { const v = b.dataset.varName; const val = found[v]; b.dataset.on = String(val); b.textContent = `${v}: ${val}`; });
          updateClauseLights();
        } else {
          resEl.textContent = 'UNSAT under brute force';
          resEl.style.color = '#f87171';
          metricsEl.textContent = `Checked ${checked} assignments.`;
        }
      } catch (e) {
        resEl.textContent = String(e.message || e); resEl.style.color = '#f87171';
      }
    });

    if (resetBtn) resetBtn.addEventListener('click', () => { current = PRESETS[0]; loadPreset(); });

    renderPresets();
    loadPreset();
  }

  // ---------------------- Reduction conveyor ----------------------
  function initReductionBelt() {
    const palette = document.querySelectorAll('.reduction-node');
    const pipe = $('#rl-pipeline');
    const stats = $('#rl-stats');
    const expl = $('#rl-explainer');
    const clear = $('#rl-clear');
    const exportBtn = $('#rl-export');
    if (!pipe || !palette.length) return;

    const names = { '3sat': '3-SAT', 'clique': 'CLIQUE', 'vc': 'Vertex Cover', 'is': 'Independent Set', '3color': '3-Coloring', 'hamil': 'Hamiltonian Path' };
    const edges = new Set([
      '3sat>clique', 'clique>vc', 'vc>is', 'is>3color', '3sat>hamil', 'hamil>3color'
    ]);
    const blowup = {
      '3sat>clique': 'O(n)',
      'clique>vc': 'O(n)',
      'vc>is': 'O(n)',
      'is>3color': 'O(n)',
      '3sat>hamil': 'O(n)',
      'hamil>3color': 'O(n)'
    };
    const cert = {
      '3sat>clique': 'assignment -> one literal per clause',
      'clique>vc': 'k-clique -> |V|-k cover',
      'vc>is': 'cover -> complement independent set',
      'is>3color': 'independent set -> shared color class',
      '3sat>hamil': 'assignment -> path through gadgets',
      'hamil>3color': 'path -> colorable line gadget'
    };
    const seq = [];

    function render() {
      pipe.innerHTML = '';
      const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
      svg.setAttribute('width', '100%'); svg.setAttribute('height', '70');
      svg.style.position = 'absolute'; svg.style.left = '0'; svg.style.top = '14px'; svg.style.pointerEvents = 'none';
      const wrap = el('div', { style: 'position:relative; min-height:70px;' });
      pipe.appendChild(wrap);
      const items = [];
      seq.forEach((id, idx) => {
        const b = el('span', { className: 'chip', textContent: names[id] || id });
        b.tabIndex = 0; b.dataset.idx = String(idx);
        b.setAttribute('draggable', 'true');
        b.addEventListener('dragstart', ev => { ev.dataTransfer.setData('text/plain', b.dataset.idx); });
        b.addEventListener('dragover', ev => ev.preventDefault());
        b.addEventListener('drop', ev => {
          ev.preventDefault();
          const from = Number(ev.dataTransfer.getData('text/plain')); const to = Number(b.dataset.idx);
          if (Number.isFinite(from) && Number.isFinite(to) && from !== to) { const x = seq.splice(from, 1)[0]; seq.splice(to, 0, x); render(); }
        });
        wrap.appendChild(b);
        items.push(b);
        if (idx < seq.length - 1) wrap.appendChild(el('span', { textContent: '  ' }));
      });
      wrap.appendChild(svg);
      requestAnimationFrame(() => {
        svg.innerHTML = '';
        for (let i = 0; i < items.length - 1; i++) {
          const a = items[i].getBoundingClientRect();
          const b = items[i + 1].getBoundingClientRect();
          const r = wrap.getBoundingClientRect();
          const x1 = a.left - r.left + a.width / 2; const y1 = 22;
          const x2 = b.left - r.left + b.width / 2; const y2 = 22;
          const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
          const d = `M ${x1} ${y1} C ${(x1 + x2) / 2} ${y1 - 18}, ${(x1 + x2) / 2} ${y2 + 18}, ${x2} ${y2}`;
          path.setAttribute('d', d);
          path.setAttribute('stroke', 'rgba(217,255,90,0.8)');
          path.setAttribute('stroke-width', '2');
          path.setAttribute('fill', 'none');
          svg.appendChild(path);
        }
      });

      if (stats) {
        let ok = true; const details = [];
        for (let i = 0; i < seq.length - 1; i++) {
          const k = `${seq[i]}>${seq[i + 1]}`;
          if (!edges.has(k)) { ok = false; details.push(`No standard reduction: ${names[seq[i]]} -> ${names[seq[i + 1]]}`); }
          else details.push(`${names[seq[i]]} -> ${names[seq[i + 1]]}: size ${blowup[k]}, cert: ${cert[k]}`);
        }
        stats.textContent = seq.length ? (ok ? 'Pipeline valid. ' : 'Pipeline has gaps. ') + details.join(' | ') : 'Click problems to place them on the belt.';
      }
      if (expl) {
        const lines = [];
        for (let i = 0; i < seq.length - 1; i++) {
          const k = `${seq[i]}>${seq[i + 1]}`;
          if (edges.has(k)) lines.push(`${names[seq[i]]} carries instances to ${names[seq[i + 1]]} without super-polynomial blowup.`);
          else lines.push(`No known polynomial reduction from ${names[seq[i]]} to ${names[seq[i + 1]]}.`);
        }
        expl.textContent = lines.join(' ');
      }
    }

    palette.forEach(btn => btn.addEventListener('click', () => { seq.push(btn.dataset.prob); render(); }));
    clear && clear.addEventListener('click', () => { seq.length = 0; render(); });

    if (exportBtn) exportBtn.addEventListener('click', () => {
      if (!seq.length) return;
      const canvas = document.createElement('canvas');
      const w = Math.max(360, seq.length * 140); const h = 120;
      canvas.width = w; canvas.height = h;
      const ctx = canvas.getContext('2d');
      ctx.fillStyle = '#0b0f19'; ctx.fillRect(0, 0, w, h);
      ctx.fillStyle = '#d9ff5a'; ctx.font = '16px "Space Grotesk"';
      let x = 30;
      seq.forEach((id, idx) => {
        ctx.strokeStyle = '#3b3f52'; ctx.lineWidth = 1.5;
        ctx.fillStyle = '#141a28';
        ctx.roundRect(x, 34, 120, 44, 10); ctx.fill(); ctx.stroke();
        ctx.fillStyle = '#d9ff5a';
        ctx.fillText(names[id] || id, x + 12, 60);
        if (idx < seq.length - 1) {
          ctx.strokeStyle = '#d9ff5a'; ctx.beginPath(); ctx.moveTo(x + 120, 56); ctx.lineTo(x + 140, 56); ctx.stroke();
        }
        x += 140;
      });
      const link = document.createElement('a');
      link.href = canvas.toDataURL('image/png');
      link.download = 'reduction-belt.png';
      link.click();
    });

    render();
  }

  // ---------------------- NP-complete zoo ----------------------
  function initZoo() {
    const host = $('#zoo-grid'); if (!host) return;
    const cards = [
      { name: '3-SAT', cert: 'Assignment', why: 'Clause gadgets force consistent choices.' },
      { name: 'CLIQUE', cert: 'k vertices all connected', why: 'Search space of k-subsets grows fast.' },
      { name: 'Vertex Cover', cert: 'Set of vertices hitting every edge', why: 'Dual to Independent Set; hard via reduction from CLIQUE.' },
      { name: 'Independent Set', cert: 'Set of vertices with no edges', why: 'Complement of Vertex Cover; maps from CLIQUE.' },
      { name: '3-Coloring', cert: 'Coloring function on nodes', why: 'Enforces constraints via edge clashes.' },
      { name: 'Hamiltonian Path', cert: 'Permutation of vertices', why: 'Requires visiting all nodes exactly once.' }
    ];
    cards.forEach(c => {
      const card = el('div', { className: 'zoo-card' });
      const title = el('div', { className: 'zoo-title', textContent: c.name });
      const body = el('div', { className: 'zoo-body', textContent: `Certificate: ${c.cert}. ${c.why}` });
      card.append(title, body);
      card.addEventListener('click', () => {
        card.classList.toggle('flipped');
        body.textContent = card.classList.contains('flipped')
          ? `Relationships: typical reductions pass through 3-SAT or CLIQUE.`
          : `Certificate: ${c.cert}. ${c.why}`;
      });
      host.appendChild(card);
    });
  }

  // ---------------------- Graph coloring corner ----------------------
  function initGraphColoring() {
    const host = $('#gc-canvas'); if (!host) return;
    const statusEl = $('#gc-status'); const edgesEl = $('#gc-edges');
    const btnCheck = $('#gc-check'); const btnReset = $('#gc-reset'); const btnGreedy = $('#gc-greedy');
    const presetHost = $('#gc-presets');

    const PRESETS = {
      triangle: {
        label: 'Triangle',
        nodes: [ { id:1,x:50,y:50,c:-1},{id:2,x:150,y:60,c:-1},{id:3,x:100,y:160,c:-1} ],
        edges: [[1,2],[2,3],[1,3]]
      },
      cube: {
        label: 'Cube',
        nodes: [ {id:1,x:40,y:40,c:-1},{id:2,x:160,y:40,c:-1},{id:3,x:40,y:160,c:-1},{id:4,x:160,y:160,c:-1},{id:5,x:90,y:70,c:-1},{id:6,x:210,y:70,c:-1},{id:7,x:90,y:190,c:-1},{id:8,x:210,y:190,c:-1} ],
        edges: [[1,2],[1,3],[2,4],[3,4],[5,6],[5,7],[6,8],[7,8],[1,5],[2,6],[3,7],[4,8]]
      },
      petersen: {
        label: 'Petersen mini',
        nodes: [ {id:1,x:60,y:30,c:-1},{id:2,x:180,y:30,c:-1},{id:3,x:220,y:130,c:-1},{id:4,x:120,y:210,c:-1},{id:5,x:20,y:130,c:-1},{id:6,x:120,y:70,c:-1},{id:7,x:160,y:110,c:-1},{id:8,x:140,y:170,c:-1},{id:9,x:100,y:170,c:-1},{id:10,x:80,y:110,c:-1} ],
        edges: [[1,2],[2,3],[3,4],[4,5],[5,1],[1,6],[2,7],[3,8],[4,9],[5,10],[6,8],[8,10],[10,7],[7,9],[9,6]]
      }
    };
    let currentKey = 'triangle';
    let nodes = []; let edges = [];

    function loadPreset(key) {
      currentKey = key;
      nodes = PRESETS[key].nodes.map(n => ({ ...n }));
      edges = PRESETS[key].edges.map(e => [...e]);
      render();
      statusEl && (statusEl.textContent = '');
      if (edgesEl) edgesEl.textContent = 'Edges: ' + edges.map(([u,v]) => `(${u}-${v})`).join(', ');
    }

    function render() {
      host.innerHTML = '';
      nodes.forEach(n => {
        const d = el('div', { className: 'gc-node', textContent: String(n.id) });
        if (n.c >= 0) d.classList.add(`gc-c${n.c}`);
        d.style.left = `${n.x}px`; d.style.top = `${n.y}px`;
        d.title = 'Click to change color';
        d.addEventListener('click', () => { n.c = (n.c + 1) % 3; render(); });
        host.appendChild(d);
      });
    }

    function valid() {
      for (const [u, v] of edges) {
        const cu = nodes.find(n => n.id === u).c;
        const cv = nodes.find(n => n.id === v).c;
        if (cu === -1 || cv === -1) return false;
        if (cu === cv) return false;
      }
      return true;
    }

    function greedy() {
      for (const n of nodes) {
        const used = new Set();
        for (const [u, v] of edges) {
          if (u === n.id) { const c = nodes.find(x => x.id === v).c; if (c >= 0) used.add(c); }
          if (v === n.id) { const c = nodes.find(x => x.id === u).c; if (c >= 0) used.add(c); }
        }
        for (let c = 0; c < 3; c++) { if (!used.has(c)) { n.c = c; break; } }
      }
      render();
    }

    if (btnCheck) btnCheck.addEventListener('click', () => {
      const ok = valid();
      statusEl && (statusEl.textContent = ok ? 'Proper 3-coloring' : 'Not a valid 3-coloring');
      statusEl && (statusEl.style.color = ok ? '#34d399' : '#f87171');
    });
    if (btnReset) btnReset.addEventListener('click', () => { nodes.forEach(n => n.c = -1); render(); statusEl && (statusEl.textContent = ''); });
    if (btnGreedy) btnGreedy.addEventListener('click', greedy);

    if (presetHost) {
      presetHost.innerHTML = '';
      Object.keys(PRESETS).forEach(k => {
        const b = el('button', { className: 'chip', textContent: PRESETS[k].label });
        b.addEventListener('click', () => loadPreset(k));
        presetHost.appendChild(b);
      });
    }

    loadPreset(currentKey);
  }

  // ---------------------- Scaling wall ----------------------
  function initScalingWall() {
    const sel = $('#sw-problem'); const rn = $('#sw-n'); const rd = $('#sw-density');
    const run = $('#sw-run'); const clr = $('#sw-clear'); const chart = $('#sw-chart');
    const log = $('#sw-log'); const nVal = $('#sw-n-val'); const dVal = $('#sw-density-val'); const exportBtn = $('#sw-export');
    if (!sel || !rn || !rd || !run || !clr || !chart) return;
    const ctx = chart.getContext('2d');
    const runs = []; // {problem,n,density,work,color}

    function setText() { nVal && (nVal.textContent = String(rn.value)); dVal && (dVal.textContent = `${rd.value}%`); }
    rn.addEventListener('input', setText); rd.addEventListener('input', setText); setText();

    function clearPlot() { ctx.clearRect(0, 0, chart.width, chart.height); log && (log.textContent = ''); runs.length = 0; axes(); }
    clr.addEventListener('click', clearPlot);

    function axes() {
      ctx.strokeStyle = 'rgba(148,163,184,0.5)';
      ctx.beginPath(); ctx.moveTo(32, 8); ctx.lineTo(32, 200); ctx.lineTo(300, 200); ctx.stroke();
      ctx.fillStyle = 'rgba(182,177,165,0.8)';
      ctx.font = '12px "IBM Plex Mono"';
      ctx.fillText('work', 8, 16); ctx.fillText('n', 286, 214);
    }
    axes();

    function plotPoint(x, y, color) { ctx.fillStyle = color; ctx.beginPath(); ctx.arc(x, y, 4, 0, Math.PI * 2); ctx.fill(); }

    function redraw() {
      ctx.clearRect(0, 0, chart.width, chart.height); axes();
      const xscale = 260 / 20; const yscale = 180 / 10000;
      runs.forEach(r => {
        const x = 32 + (r.n - 4) * xscale;
        const y = 200 - Math.min(180, r.work * yscale);
        plotPoint(x, y, r.color);
      });
    }

    function randSAT(n, density) {
      const vars = Array.from({ length: n }, (_, i) => `x${i + 1}`);
      const m = Math.max(1, Math.round((density / 100) * n * 4));
      const clauses = [];
      for (let i = 0; i < m; i++) {
        const lits = [];
        for (let j = 0; j < 3; j++) {
          const v = vars[Math.floor(Math.random() * vars.length)];
          const neg = Math.random() < 0.5;
          lits.push(neg ? '!' + v : v);
        }
        clauses.push(lits);
      }
      return clauses;
    }

    function evalClause(cl, env) { return cl.some(L => L[0] === '!' ? !env[L.slice(1)] : !!env[L]); }
    function satBacktrack(n, clauses, timeCapMs = 800) {
      const names = Array.from({ length: n }, (_, i) => `x${i + 1}`);
      const start = performance.now(); let nodes = 0;
      function dfs(i, env) {
        if (performance.now() - start > timeCapMs) return null;
        if (i === n) { nodes++; return clauses.every(c => evalClause(c, env)) ? env : null; }
        env[names[i]] = false; nodes++; const a = dfs(i + 1, env); if (a) return a;
        env[names[i]] = true; nodes++; return dfs(i + 1, env);
      }
      const sol = dfs(0, {});
      return { nodes, sol, timeout: (performance.now() - start > timeCapMs) };
    }

    function randGraph(n, density) {
      const edges = [];
      for (let u = 1; u <= n; u++) for (let v = u + 1; v <= n; v++) if (Math.random() < density / 100) edges.push([u, v]);
      return edges;
    }
    function cliqueBruteforce(n, edges) {
      const adj = Array.from({ length: n + 1 }, () => new Set());
      edges.forEach(([u, v]) => { adj[u].add(v); adj[v].add(u); });
      const vs = Array.from({ length: n }, (_, i) => i + 1);
      const k = Math.max(2, Math.min(5, Math.floor(n / 3)));
      function* comb(arr, k, start = 0, cur = []) {
        if (cur.length === k) { yield cur.slice(); return; }
        for (let i = start; i < arr.length; i++) { cur.push(arr[i]); yield* comb(arr, k, i + 1, cur); cur.pop(); }
      }
      let cnt = 0;
      for (const S of comb(vs, k)) {
        cnt++; let ok = true;
        for (let i = 0; i < S.length && ok; i++) for (let j = i + 1; j < S.length && ok; j++) if (!adj[S[i]].has(S[j])) ok = false;
        if (ok) return { found: true, nodes: cnt };
      }
      return { found: false, nodes: cnt };
    }

    run.addEventListener('click', () => {
      const n = Number(rn.value); const density = Number(rd.value);
      const color = sel.value === 'sat' ? 'rgba(217,255,90,0.85)' : '#f5c278';
      if (sel.value === 'sat') {
        const inst = randSAT(n, density);
        const res = satBacktrack(n, inst);
        runs.push({ problem: 'SAT', n, density, work: res.nodes, color });
        log && (log.textContent = `SAT n=${n}, clauses=${inst.length}, nodes=${res.nodes}${res.timeout ? ' (timeout cap)' : ''}`);
      } else {
        const edges = randGraph(n, density);
        const res = cliqueBruteforce(n, edges);
        runs.push({ problem: 'CLIQUE', n, density, work: res.nodes, color });
        log && (log.textContent = `CLIQUE n=${n}, edges=${edges.length}, combos=${res.nodes}`);
      }
      redraw();
    });

    if (exportBtn) exportBtn.addEventListener('click', () => {
      const header = 'problem,n,density,work';
      const lines = runs.map(r => `${r.problem},${r.n},${r.density},${r.work}`);
      const csv = [header, ...lines].join('\n');
      const blob = new Blob([csv], { type: 'text/csv' });
      const url = URL.createObjectURL(blob);
      const a = el('a', { href: url, download: 'scaling_wall.csv' });
      document.body.appendChild(a); a.click(); a.remove(); URL.revokeObjectURL(url);
    });
  }

  // ---------------------- Approximation corner ----------------------
  function initApproxGame() {
    const sel = $('#ag-problem'); const size = $('#ag-size'); const sizeVal = $('#ag-size-val');
    const gen = $('#ag-generate'); const runG = $('#ag-greedy'); const runX = $('#ag-exact');
    const inst = $('#ag-instance'); const out = $('#ag-result');
    if (!sel || !size || !gen || !runG || !runX) return;
    size.addEventListener('input', () => sizeVal && (sizeVal.textContent = String(size.value)));
    let G = null; let U = null, sets = null;

    function randVC(n) { const edges = []; for (let u = 1; u <= n; u++) for (let v = u + 1; v <= n; v++) if (Math.random() < 0.3) edges.push([u, v]); return { n, edges }; }
    function vcGreedy(g) {
      const edges = g.edges.slice(); const cover = new Set();
      while (edges.length) {
        const deg = new Map();
        edges.forEach(([u, v]) => { deg.set(u, (deg.get(u) || 0) + 1); deg.set(v, (deg.get(v) || 0) + 1); });
        const v = [...deg.entries()].sort((a, b) => b[1] - a[1])[0][0];
        cover.add(v);
        for (let i = edges.length - 1; i >= 0; i--) if (edges[i][0] === v || edges[i][1] === v) edges.splice(i, 1);
      }
      return [...cover];
    }
    function vcExact(g) {
      const n = g.n; const vs = Array.from({ length: n }, (_, i) => i + 1); let best = null;
      function* subsets(arr, i = 0, cur = []) { if (i === arr.length) { yield cur.slice(); return; } cur.push(arr[i]); yield* subsets(arr, i + 1, cur); cur.pop(); yield* subsets(arr, i + 1, cur); }
      outer: for (const S of subsets(vs)) {
        if (best && S.length >= best.length) continue;
        for (const [u, v] of g.edges) { if (!(S.includes(u) || S.includes(v))) continue outer; }
        best = S.slice();
      }
      return best || [];
    }
    function randSetCover(n) {
      const U = Array.from({ length: n }, (_, i) => i + 1); const sets = [];
      for (let i = 0; i < n; i++) { const s = new Set(); for (const u of U) if (Math.random() < 0.35) s.add(u); if (s.size) sets.push([...s]); }
      return { U, sets };
    }
    function scGreedy(U, sets) {
      const need = new Set(U); const pick = [];
      while (need.size) {
        let best = -1, idx = -1;
        sets.forEach((S, i) => {
          const gain = S.filter(x => need.has(x)).length;
          if (gain > best) { best = gain; idx = i; }
        });
        if (best <= 0) break;
        pick.push(idx); sets[idx].forEach(x => need.delete(x));
      }
      return pick;
    }
    function scExact(U, sets) {
      const m = sets.length; let best = null;
      function dfs(i, pick, covered) {
        if (i === m) { if (covered.size === U.length) { if (!best || pick.length < best.length) best = pick.slice(); } return; }
        dfs(i + 1, pick, covered);
        const newC = new Set(covered); sets[i].forEach(x => newC.add(x)); pick.push(i); dfs(i + 1, pick, newC); pick.pop();
      }
      dfs(0, [], new Set()); return best || [];
    }
    function prettyVCSet(arr) { return '{' + arr.sort((a, b) => a - b).join(', ') + '}'; }
    function prettyPick(arr) { return '{' + arr.sort((a, b) => a - b).map(i => 'S' + i).join(', ') + '}'; }

    gen.addEventListener('click', () => {
      const n = Number(size.value);
      if (sel.value === 'vc') { G = randVC(n); inst && (inst.textContent = `VC: n=${G.n}, edges=${G.edges.length} :: ${G.edges.map(e => `(${e[0]}-${e[1]})`).join(', ')}`); }
      else { ({ U, sets } = randSetCover(n)); inst && (inst.textContent = `Set Cover |U|=${U.length}, m=${sets.length} :: ${sets.map((S, i) => `S${i}:{${S.join(', ')}}`).join('  ')}`); }
      out && (out.textContent = '');
    });
    runG.addEventListener('click', () => {
      if (sel.value === 'vc' && G) { const g = vcGreedy(G); out && (out.textContent = `Greedy VC = ${prettyVCSet(g)} (size ${g.length})`); }
      else if (sel.value === 'sc' && U) { const pick = scGreedy(U, sets); out && (out.textContent = `Greedy SC = ${prettyPick(pick)} (size ${pick.length})`); }
    });
    runX.addEventListener('click', () => {
      if (sel.value === 'vc' && G) {
        const opt = vcExact(G); const text = `Optimal VC = ${prettyVCSet(opt)} (size ${opt.length})`;
        if (out) { const greedy = vcGreedy(G).length; out.textContent = text + (greedy > opt.length ? ' | Greedy is worse here.' : ''); }
      } else if (sel.value === 'sc' && U) {
        const opt = scExact(U, sets); const text = `Optimal SC = ${prettyPick(opt)} (size ${opt.length})`;
        if (out) { const greedy = scGreedy(U, sets).length; out.textContent = text + (greedy > opt.length ? ' | Greedy is worse here.' : ''); }
      }
    });
  }

  // ---------------------- Parameterized nook ----------------------
  function initFPTPlayground() {
    const sel = $('#fpt-problem'); const rn = $('#fpt-n'); const rk = $('#fpt-k');
    const run = $('#fpt-run'); const randBtn = $('#fpt-rand'); const out = $('#fpt-output'); const nVal = $('#fpt-n-val'); const kVal = $('#fpt-k-val');
    if (!sel || !rn || !rk || !run || !randBtn) return;
    rn.addEventListener('input', () => nVal && (nVal.textContent = String(rn.value)));
    rk.addEventListener('input', () => kVal && (kVal.textContent = String(rk.value)));
    let edges = [];
    function randGraph(n, p = 0.25) { const E = []; for (let u = 1; u <= n; u++) for (let v = u + 1; v <= n; v++) if (Math.random() < p) E.push([u, v]); return E; }
    function kClique(n, k, E) {
      const adj = Array.from({ length: n + 1 }, () => new Set()); E.forEach(([u, v]) => { adj[u].add(v); adj[v].add(u); });
      const vs = Array.from({ length: n }, (_, i) => i + 1);
      function* comb(arr, k, start = 0, cur = []) { if (cur.length === k) { yield cur.slice(); return; } for (let i = start; i < arr.length; i++) { cur.push(arr[i]); yield* comb(arr, k, i + 1, cur); cur.pop(); } }
      let checked = 0;
      for (const S of comb(vs, k)) { checked++; let ok = true; for (let i = 0; i < S.length && ok; i++) for (let j = i + 1; j < S.length && ok; j++) if (!adj[S[i]].has(S[j])) ok = false; if (ok) return { found: true, checked }; }
      return { found: false, checked };
    }
    function kPath(n, k, E) {
      const G = Array.from({ length: n + 1 }, () => []); E.forEach(([u, v]) => { G[u].push(v); G[v].push(u); });
      let checked = 0;
      function dfs(u, vis, len) { if (len === k) return true; for (const v of G[u]) if (!vis.has(v)) { vis.add(v); checked++; if (dfs(v, vis, len + 1)) return true; vis.delete(v); } return false; }
      for (let s = 1; s <= n; s++) { const vis = new Set([s]); if (dfs(s, vis, 1)) return { found: true, checked }; }
      return { found: false, checked };
    }
    function kernelizeVC(n, E, k) {
      const adj = Array.from({ length: n + 1 }, () => new Set()); E.forEach(([u, v]) => { adj[u].add(v); adj[v].add(u); });
      let changed = true; const removed = [];
      while (changed) {
        changed = false;
        for (let v = 1; v <= n; v++) {
          if (adj[v] && adj[v].size > 0 && adj[v].size < k - 1) {
            for (const u of adj[v]) adj[u].delete(v);
            adj[v].clear(); removed.push(v); changed = true;
          }
        }
      }
      let remV = 0, remE = 0;
      for (let v = 1; v <= n; v++) { if (adj[v]) { if (adj[v].size > 0) remV++; remE += adj[v].size; } }
      remE = Math.round(remE / 2);
      return { removed: removed.sort((a, b) => a - b), remainingV: remV, remainingE: remE };
    }
    randBtn.addEventListener('click', () => { const n = Number(rn.value); edges = randGraph(n); out && (out.textContent = `Random graph: n=${n}, edges=${edges.length}`); });
    run.addEventListener('click', () => {
      const n = Number(rn.value), k = Number(rk.value); if (!edges.length) edges = randGraph(n);
      if (sel.value === 'kclique') {
        const r = kClique(n, k, edges); const ker = kernelizeVC(n, edges, k);
        out && (out.textContent = `k-Clique k=${k}: ${r.found ? 'FOUND' : 'not found'}; combinations checked=${r.checked}. Kernelization (VC low-degree rule): removed ${ker.removed.length} vertices [${ker.removed.join(', ')}], remaining ~ V=${ker.remainingV}, E=${ker.remainingE}.`);
      } else {
        const r = kPath(n, k, edges);
        out && (out.textContent = `k-Path k=${k}: ${r.found ? 'FOUND' : 'not found'}; DFS steps=${r.checked}.`);
      }
    });
  }
})();

  // ---------------------- Subset Sum rail ----------------------
  function initSubsetSum() {
    const presetHost = $('#ss-presets');
    const numsEl = $('#ss-numbers');
    const targetEl = $('#ss-target');
    const resEl = $('#ss-result');
    const witnessEl = $('#ss-witness');
    const checkBtn = $('#ss-check');
    const revealBtn = $('#ss-reveal');
    const resetBtn = $('#reset-verify');
    if (!presetHost || !numsEl || !targetEl) return;

    const PRESETS = [
      { id: 'partition', label: 'Balanced', nums: [3, 1, 1, 2, 2, 1], target: 5, expect: 'SAT' },
      { id: 'tricky', label: 'Tricky', nums: [3, 34, 4, 12, 5, 2], target: 9, expect: 'SAT' },
      { id: 'nosol', label: 'No solution', nums: [5, 7, 11], target: 3, expect: 'UNSAT' },
      { id: 'tight', label: 'Tight', nums: [8, 6, 2, 4], target: 14, expect: 'SAT' }
    ];
    let current = PRESETS[0];

    function renderPresets() {
      presetHost.innerHTML = '';
      PRESETS.forEach(p => {
        const b = el('button', { className: 'chip', textContent: p.label, type: 'button' });
        b.addEventListener('click', () => { current = p; loadPreset(); });
        presetHost.appendChild(b);
      });
    }

    function loadPreset() {
      numsEl.textContent = `[${current.nums.join(', ')}]`;
      targetEl.textContent = String(current.target);
      resEl && (resEl.textContent = '');
      witnessEl && (witnessEl.textContent = '');
    }

    function backtrack(nums, target, maxMs = 700) {
      const order = nums.map((v, i) => ({ v, i })).sort((a, b) => Math.abs(b.v) - Math.abs(a.v));
      const idxs = order.map(o => o.i); const vals = order.map(o => o.v);
      const start = performance.now(); let best = null;
      function dfs(i, sum, take) {
        if (performance.now() - start > maxMs) return false;
        if (sum === target) { best = take.slice(); return true; }
        if (i >= vals.length) return false;
        take.push(idxs[i]); if (dfs(i + 1, sum + vals[i], take)) return true; take.pop();
        if (dfs(i + 1, sum, take)) return true;
        return false;
      }
      const ok = dfs(0, 0, []);
      if (!ok) return null;
      return best.map(j => nums[j]);
    }

    if (checkBtn) checkBtn.addEventListener('click', () => {
      const subset = backtrack(current.nums, current.target);
      if (subset) {
        resEl.textContent = 'Subset found';
        resEl.style.color = '#34d399';
        witnessEl.textContent = `Subset: [${subset.join(', ')}], sum ${subset.reduce((a, b) => a + b, 0)}. Expectation: ${current.expect}.`;
      } else {
        resEl.textContent = 'No subset (within demo search)';
        resEl.style.color = '#f87171';
        witnessEl.textContent = `Expectation: ${current.expect}.`;
      }
    });

    if (revealBtn) revealBtn.addEventListener('click', () => {
      const subset = backtrack(current.nums, current.target, 1200);
      if (subset) {
        witnessEl.textContent = `One witness: [${subset.join(', ')}]`;
        resEl.textContent = 'SAT (witness shown)';
        resEl.style.color = '#34d399';
      } else {
        witnessEl.textContent = 'No subset witnessed in this search window.';
        resEl.textContent = 'UNSAT in window';
        resEl.style.color = '#f87171';
      }
    });

    if (resetBtn) resetBtn.addEventListener('click', () => { current = PRESETS[0]; loadPreset(); });

    renderPresets();
    loadPreset();
  }
