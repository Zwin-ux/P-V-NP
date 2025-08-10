// P vs NP — Interactive Demos (Remade)
// Robust, modular, and isolated initializers. Each init guards DOM presence and errors.

(function bootstrap() {
  document.addEventListener('DOMContentLoaded', () => {
    safeInit('SAT', initSAT);
    safeInit('SubsetSum', initSubsetSum);
    safeInit('GraphColoring', initGraphColoring);
    safeInit('ReductionsGallery', initReductionsGallery);
    safeInit('ReductionQuiz', initReductionQuiz);
    safeInit('Theme', initTheme);
    // Advanced labs
    safeInit('ReductionLab', initReductionLab);
    safeInit('ScalingWall', initScalingWall);
    safeInit('ApproximationGame', initApproxGame);
    safeInit('FPTPlayground', initFPTPlayground);
    safeInit('FineGrainedStopwatch', initFineGrainedStopwatch);
  });

  function safeInit(name, fn) {
    try { fn(); console.debug(`[Init] ${name}: OK`); }
    catch (e) { console.error(`[Init] ${name}: FAILED`, e); }
  }

  // Utilities
  function $(sel) { return document.querySelector(sel); }
  function $all(sel) { return Array.from(document.querySelectorAll(sel)); }
  function el(tag, props={}) { const n = document.createElement(tag); Object.assign(n, props); return n; }

  // SAT Playground (tiny CNF)
  function initSAT() {
    const cnfInput = $('#cnf-input');
    const varsContainer = $('#vars-container');
    const checkBtn = $('#sat-check');
    const solveBtn = $('#sat-solve');
    const resultEl = $('#sat-result');
    const errorEl = $('#sat-error');
    const witnessEl = $('#sat-witness');
    const metricsEl = $('#sat-metrics');
    if (!cnfInput || !varsContainer || !checkBtn || !resultEl || !errorEl) return;

    const MAX_VARS = 9;

    function extractVars(expr) {
      const s = new Set();
      const re = /x([1-9])/g; let m;
      while ((m = re.exec(expr)) !== null) s.add(`x${m[1]}`);
      return Array.from(s).sort((a,b)=>Number(a.slice(1))-Number(b.slice(1))).slice(0, MAX_VARS);
    }

    function renderToggles(names) {
      varsContainer.innerHTML = '';
      names.forEach(name => {
        const b = el('button', { className: 'toggle', type: 'button', textContent: `${name}: false` });
        b.dataset.on = 'false'; b.dataset.varName = name;
        b.setAttribute('aria-pressed','false'); b.setAttribute('aria-label', `Toggle ${name}`);
        b.addEventListener('click', () => {
          const on = b.dataset.on === 'true';
          b.dataset.on = String(!on);
          b.textContent = `${name}: ${!on}`;
          b.setAttribute('aria-pressed', String(!on));
        });
        varsContainer.appendChild(b);
      });
    }

    const TOK = { VAR:'VAR', NOT:'NOT', AND:'AND', OR:'OR', LP:'LP', RP:'RP' };
    function tokenize(expr) {
      const t = []; const src = (expr||'').replace(/\s+/g,'');
      for (let i=0;i<src.length;i++) {
        const c = src[i];
        if (c==='(') { t.push({t:TOK.LP}); continue; }
        if (c===')') { t.push({t:TOK.RP}); continue; }
        if (c==='!') { t.push({t:TOK.NOT}); continue; }
        if (c==='&') { t.push({t:TOK.AND}); continue; }
        if (c==='|') { t.push({t:TOK.OR}); continue; }
        if (c==='x') { const n = src[i+1]; if (!/[1-9]/.test(n)) throw new Error(`Invalid var at ${i}`); t.push({t:TOK.VAR,v:`x${n}`}); i++; continue; }
        throw new Error(`Unexpected '${c}' at ${i}`);
      }
      return t;
    }
    const PREC = { [TOK.NOT]:3, [TOK.AND]:2, [TOK.OR]:1 };
    const RIGHT = { [TOK.NOT]: true };
    function toRPN(tokens) {
      const out=[], op=[]; for (const tk of tokens) {
        if (tk.t===TOK.VAR) out.push(tk);
        else if (tk.t===TOK.NOT||tk.t===TOK.AND||tk.t===TOK.OR) {
          while (op.length) {
            const top=op[op.length-1]; if (top.t===TOK.LP) break;
            const pTop=PREC[top.t]||0, pTk=PREC[tk.t]||0;
            if ((RIGHT[tk.t] && pTk<pTop) || (!RIGHT[tk.t] && pTk<=pTop)) out.push(op.pop()); else break;
          }
          op.push(tk);
        } else if (tk.t===TOK.LP) op.push(tk);
        else if (tk.t===TOK.RP) {
          let f=false; while (op.length) { const top=op.pop(); if (top.t===TOK.LP) { f=true; break; } out.push(top); }
          if (!f) throw new Error('Unbalanced parentheses');
        }
      }
      while (op.length) { const top=op.pop(); if (top.t===TOK.LP||top.t===TOK.RP) throw new Error('Unbalanced parentheses'); out.push(top); }
      return out;
    }
    function evalRPN(rpn, env) {
      const st=[]; for (const tk of rpn) {
        if (tk.t===TOK.VAR) st.push(Boolean(env[tk.v]));
        else if (tk.t===TOK.NOT) { if (!st.length) throw new Error('Parse error'); st.push(!st.pop()); }
        else if (tk.t===TOK.AND||tk.t===TOK.OR) { if (st.length<2) throw new Error('Parse error'); const b=st.pop(), a=st.pop(); st.push(tk.t===TOK.AND?(a&&b):(a||b)); }
        else throw new Error('Unknown token');
      }
      if (st.length!==1) throw new Error('Parse error');
      return st[0];
    }
    function envFromToggles() { const env={}; varsContainer.querySelectorAll('button.toggle').forEach(b=>env[b.dataset.varName]=b.dataset.on==='true'); return env; }

    function syncVars() { try { errorEl && (errorEl.textContent=''); renderToggles(extractVars(cnfInput.value)); } catch(_){} }
    cnfInput.addEventListener('input', syncVars); syncVars();

    checkBtn.addEventListener('click', () => {
      try {
        if (errorEl) errorEl.textContent=''; if (witnessEl) witnessEl.textContent=''; if (metricsEl) metricsEl.textContent='';
        const rpn = toRPN(tokenize(cnfInput.value));
        const val = evalRPN(rpn, envFromToggles());
        resultEl.textContent = val ? 'Satisfies (under current assignment)' : 'Does NOT satisfy';
        resultEl.style.color = val ? 'rgb(34 197 94)' : 'rgb(248 113 113)';
      } catch (e) {
        resultEl.textContent='—'; resultEl.style.color=''; if (errorEl) errorEl.textContent = String(e.message||e);
      }
    });

    if (solveBtn) solveBtn.addEventListener('click', () => {
      try {
        if (errorEl) errorEl.textContent=''; if (witnessEl) witnessEl.textContent=''; if (metricsEl) metricsEl.textContent='';
        const t0=performance.now(); const rpn=toRPN(tokenize(cnfInput.value)); const names=extractVars(cnfInput.value); const n=names.length;
        if (n===0) throw new Error('No variables found'); const limit = 1<<Math.min(n,20);
        let found=null, checked=0; for (let mask=0; mask<limit; mask++) { const env={}; for (let i=0;i<n;i++) env[names[i]] = !!(mask & (1<<i)); checked++; if (evalRPN(rpn, env)) { found=env; break; } }
        const t1=performance.now();
        if (found) { resultEl.textContent='SAT (found assignment)'; resultEl.style.color='rgb(34 197 94)'; if (witnessEl) witnessEl.textContent='Witness: '+names.map(k=>`${k}=${found[k]}`).join(', '); }
        else { resultEl.textContent='UNSAT (under brute-force search)'; resultEl.style.color='rgb(248 113 113)'; }
        if (metricsEl) metricsEl.textContent=`Tried ${checked} assignments in ${(t1-t0).toFixed(1)} ms`;
      } catch(e) { resultEl.textContent='—'; resultEl.style.color=''; if (errorEl) errorEl.textContent=String(e.message||e); }
    });
  }

  // Subset Sum Verifier
  function initSubsetSum() {
    const numsInput=$('#ss-numbers'); const targetInput=$('#ss-target'); const btn=$('#ss-check'); const resultEl=$('#ss-result'); const witnessEl=$('#ss-witness');
    if (!numsInput || !targetInput || !btn || !resultEl || !witnessEl) return;
    const MAX_N=20, MAX_MS=500;
    function parseNums(s){ if(!s.trim()) return []; const arr=s.split(/[\,\s]+/).filter(Boolean).map(Number); if(arr.some(n=>!Number.isFinite(n))) throw new Error('Numbers must be numeric'); return arr; }
    function backtrack(nums, target){ const order=nums.map((v,i)=>({v,i})).sort((a,b)=>Math.abs(b.v)-Math.abs(a.v)); const idxs=order.map(o=>o.i); const vals=order.map(o=>o.v); const start=performance.now(); let best=null; function dfs(i,sum,take){ if(performance.now()-start>MAX_MS) return false; if(sum===target){ best=take.slice(); return true;} if(i>=vals.length) return false; take.push(idxs[i]); if(dfs(i+1,sum+vals[i],take)) return true; take.pop(); if(dfs(i+1,sum,take)) return true; return false;} const ok=dfs(0,0,[]); if(!ok) return null; return best.map(j=>nums[j]); }
    btn.addEventListener('click', ()=>{ try { witnessEl.textContent=''; resultEl.style.color=''; const nums=parseNums(numsInput.value); const target=Number(targetInput.value); if(!Number.isFinite(target)) throw new Error('Target must be a number'); if(nums.length>MAX_N) throw new Error(`Please use at most ${MAX_N} numbers`); const subset=backtrack(nums,target); if(subset){ resultEl.textContent='Subset found!'; resultEl.style.color='rgb(34,197,94)'; const sum=subset.reduce((a,b)=>a+b,0); witnessEl.textContent=`Subset: [${subset.join(', ')}], sum = ${sum}`; } else { resultEl.textContent='No subset found (within demo limits)'; resultEl.style.color='rgb(248,113,113)'; witnessEl.textContent=''; } } catch(e){ resultEl.textContent='—'; witnessEl.textContent=String(e.message||e);} });
  }

  // Graph Coloring (3-color) small demo
  function initGraphColoring(){
    const host=$('#gc-canvas'); if(!host) return; const statusEl=$('#gc-status'); const edgesEl=$('#gc-edges'); const btnCheck=$('#gc-check'); const btnReset=$('#gc-reset'); const btnGreedy=$('#gc-greedy');
    const nodes=[ {id:1,x:24,y:24,c:-1},{id:2,x:180,y:28,c:-1},{id:3,x:320,y:36,c:-1},{id:4,x:70,y:160,c:-1},{id:5,x:220,y:140,c:-1},{id:6,x:340,y:190,c:-1} ];
    const edges=[[1,2],[2,3],[1,4],[2,5],[3,6],[4,5],[5,6],[2,4]];
    function render(){ host.innerHTML=''; for(const n of nodes){ const d=el('div',{className:'gc-node',textContent:String(n.id)}); if(n.c>=0) d.classList.add(`gc-c${n.c}`); d.style.left=`${n.x}px`; d.style.top=`${n.y}px`; d.title='Click to change color'; d.addEventListener('click',()=>{ n.c=(n.c+1)%3; render();}); host.appendChild(d);} edgesEl && (edgesEl.textContent='Edges: '+edges.map(([u,v])=>`(${u}-${v})`).join(', ')); }
    function valid(){ for(const [u,v] of edges){ const cu=nodes.find(n=>n.id===u).c; const cv=nodes.find(n=>n.id===v).c; if(cu===-1||cv===-1) return false; if(cu===cv) return false;} return true; }
    function greedy(){ for(const n of nodes){ const used=new Set(); for(const [u,v] of edges){ if(u===n.id){ const c=nodes.find(x=>x.id===v).c; if(c>=0) used.add(c);} if(v===n.id){ const c=nodes.find(x=>x.id===u).c; if(c>=0) used.add(c);} } for(let c=0;c<3;c++){ if(!used.has(c)){ n.c=c; break; } } } render(); }
    btnCheck && btnCheck.addEventListener('click',()=>{ const ok=valid(); statusEl && (statusEl.textContent = ok?'Proper 3-coloring ✓':'Not a valid 3-coloring'); statusEl && (statusEl.style.color= ok?'rgb(34 197 94)':'rgb(248 113 113)'); });
    btnReset && btnReset.addEventListener('click',()=>{ nodes.forEach(n=>n.c=-1); statusEl && (statusEl.textContent='—'); statusEl && (statusEl.style.color=''); render(); });
    btnGreedy && btnGreedy.addEventListener('click',greedy);
    render();
  }

  // Reductions Gallery (tabs + 3-SAT→CLIQUE + CLIQUE→VC)
  function initReductionsGallery(){
    const tabBtns=$all('.reduction-tab'); const panels=$all('.reduction-panel'); if(!tabBtns.length||!panels.length) return;
    tabBtns.forEach(btn=>btn.addEventListener('click',()=>{ tabBtns.forEach(b=>b.classList.remove('active')); panels.forEach(p=>p.classList.remove('active')); btn.classList.add('active'); const id=btn.dataset.tab; const p=document.getElementById(id); if(p) p.classList.add('active'); tabBtns.forEach(b=>{ b.setAttribute('aria-selected', b===btn?'true':'false'); b.setAttribute('role','tab'); const pid=b.dataset.tab; if(pid) b.setAttribute('aria-controls',pid); }); panels.forEach(panel=>{ panel.setAttribute('role','tabpanel'); panel.setAttribute('aria-hidden', panel.id === (btn.dataset.tab||'') ? 'false' : 'true'); }); }));

    // 3-SAT -> CLIQUE builder
    const input=$('#rg-3sat-input'); const buildBtn=$('#rg-3sat-build'); const outGraph=$('#rg-3sat-graph'); const outResult=$('#rg-3sat-result');
    function parse3CNF(expr){ const cleaned=(expr||'').replace(/\s+/g,''); if(!cleaned) throw new Error('Enter a 3-CNF formula'); const clauses=cleaned.split('&').map(cl=>{ const m=cl.match(/^\(([^()]+)\)$/); if(!m) throw new Error(`Clause must be in parentheses: ${cl}`); const lits=m[1].split('|').map(s=>s.trim()).filter(Boolean); if(lits.length===0||lits.length>3) throw new Error('Each clause must have 1..3 literals'); lits.forEach(L=>{ if(!/^!?x[1-5]$/.test(L)) throw new Error(`Invalid literal: ${L}`);} ); return lits; }); if(clauses.length>3) throw new Error('Please use at most 3 clauses in this demo'); return clauses; }
    function conflict(a,b){ const va=a.replace('!',''); const vb=b.replace('!',''); if(va!==vb) return false; return (a.startsWith('!') !== b.startsWith('!')); }
    function buildCliqueGraph(clauses){ const nodes=[], edges=[]; for(let i=0;i<clauses.length;i++){ for(let j=0;j<clauses[i].length;j++){ nodes.push({id:`c${i}l${j}`, clause:i, lit:clauses[i][j]}); } } for(let u=0;u<nodes.length;u++){ for(let v=u+1;v<nodes.length;v++){ const A=nodes[u],B=nodes[v]; if(A.clause===B.clause) continue; if(!conflict(A.lit,B.lit)) edges.push([A.id,B.id]); } } return {nodes,edges}; }
    function hasKCliqueAcrossClauses(G,k){ const by={}; G.nodes.forEach(n=>{ (by[n.clause] ||= []).push(n); }); const groups=Object.keys(by).map(k=>by[k]); if(groups.length!==k) return false; const E=new Set(G.edges.map(e=>`${e[0]}|${e[1]}`)); const conn=(a,b)=> E.has(`${a}|${b}`)||E.has(`${b}|${a}`); function dfs(i,picked){ if(i===groups.length) return true; for(const cand of groups[i]){ let ok=true; for(const p of picked){ if(!conn(p.id,cand.id)){ ok=false; break; } } if(!ok) continue; if(dfs(i+1,picked.concat(cand))) return true; } return false; } return dfs(0,[]); }
    if (buildBtn) buildBtn.addEventListener('click',()=>{ try{ if(outResult) outResult.textContent=''; const clauses=parse3CNF(input.value); const G=buildCliqueGraph(clauses); if(outGraph){ const nodesStr=G.nodes.map(n=>`${n.id}:${n.lit}[c${n.clause}]`).join(', '); const edgesStr=G.edges.map(e=>`(${e[0]}–${e[1]})`).join(', '); outGraph.textContent=`Nodes: ${nodesStr}\nEdges: ${edgesStr}`; } const k=clauses.length; const ok=hasKCliqueAcrossClauses(G,k); if(outResult){ outResult.textContent= ok ? `k-clique exists (k=${k}) ⇒ formula satisfiable` : `No k-clique found (k=${k}) under this construction`; outResult.style.color = ok ? 'rgb(34 197 94)' : 'rgb(248 113 113)'; } } catch(e){ if(outGraph) outGraph.textContent=String(e.message||e); if(outResult){ outResult.textContent=''; outResult.style.color=''; } } });

    // CLIQUE -> Vertex Cover quick checker
    const cvEdges=$('#rg-cv-edges'); const cvK=$('#rg-cv-k'); const cvBtn=$('#rg-cv-check'); const cvOut=$('#rg-cv-out');
    function parseEdges(s){ const list=(s||'').split(',').map(x=>x.trim()).filter(Boolean); const edges=[]; let maxV=0; for(const e of list){ const m=e.match(/^(\d+)-(\d+)$/); if(!m) throw new Error(`Invalid edge: ${e}`); const u=Number(m[1]), v=Number(m[2]); maxV=Math.max(maxV,u,v); if(u===v) continue; edges.push([u,v]); } return {edges,n:maxV}; }
    function buildAdj(n, edges){ const adj=Array.from({length:n+1},()=>new Set()); for(const [u,v] of edges){ adj[u].add(v); adj[v].add(u);} return adj; }
    function hasCliqueOfSizeK(adj,n,k){ const vs=Array.from({length:n},(_,i)=>i+1); const comb=(arr,k,start=0,cur=[],out=[])=>{ if(cur.length===k){ out.push(cur.slice()); return out;} for(let i=start;i<arr.length;i++) comb(arr,k,i+1,cur.concat(arr[i]),out); return out; }; const sets=comb(vs,k); for(const S of sets){ let ok=true; for(let i=0;i<S.length && ok;i++) for(let j=i+1;j<S.length && ok;j++){ if(!adj[S[i]].has(S[j])) ok=false; } if(ok) return true; } return false; }
    if (cvBtn) cvBtn.addEventListener('click',()=>{ try{ const {edges,n}=parseEdges(cvEdges.value); const k=Number(cvK.value); if(!Number.isFinite(k)||k<0) throw new Error('k must be a non-negative number'); const adj=buildAdj(n,edges); const has=hasCliqueOfSizeK(adj,n,k); const vcSize=n-k; cvOut.textContent = has ? `G has a clique of size k=${k}. Then Ḡ has an independent set of size k, and G has a vertex cover of size |V|−k=${vcSize}.` : `No clique of size k=${k} found in this small brute-force check.`; } catch(e){ cvOut.textContent=String(e.message||e);} });
  }

  // Reduction Quiz
  function initReductionQuiz(){
    const qEl=$('#rq-question'); const optsEl=$('#rq-options'); const nextBtn=$('#rq-next'); const scoreEl=$('#rq-score'); if(!qEl||!optsEl||!nextBtn||!scoreEl) return;
    const QS=[
      { q:'Which reduction shows SAT ≤p 3-SAT?', opts:['Duplicate variables','Clause splitting with new vars','Graph complement'], a:1 },
      { q:'Independent Set and Vertex Cover are related by…', opts:['Graph complement','Set complement in same graph','Edge subdivision'], a:1 },
      { q:'3-SAT to CLIQUE mapping uses…', opts:['Edges within clauses','Edges across non-conflicting literals','Edges only on negations'], a:1 },
      { q:'Subset Sum encodes SAT by…', opts:['Digits per clause/variable','Matrix multiplication','Sorting'], a:0 },
    ];
    let i=0, score=0, locked=false;
    function render(){ locked=false; const cur=QS[i%QS.length]; qEl.textContent=cur.q; optsEl.innerHTML=''; cur.opts.forEach((txt,idx)=>{ const b=el('button',{className:'btn-ghost',type:'button',textContent:txt}); b.addEventListener('click',()=>{ if(locked) return; locked=true; if(idx===cur.a){ score++; b.style.background='rgba(34,197,94,0.25)'; } else { b.style.background='rgba(248,113,113,0.25)'; } scoreEl.textContent=`Score: ${score}`; }); optsEl.appendChild(b); }); }
    nextBtn.addEventListener('click',()=>{ i++; render(); });
    render();
  }

  // Theme controls
  function initTheme(){
    const root=document.documentElement; const swatches=$all('.theme-swatch'); const applyBtn=$('#apply-brand'); const titleInput=$('#brand-title'); const titleEl=$('#brand-title-text'); const logoBox=$('#brand-logo-box');
    const THEMES={ indigo:{b500:'#6366f1',b600:'#4f46e5',b700:'#4338ca'}, emerald:{b500:'#34d399',b600:'#059669',b700:'#065f46'}, rose:{b500:'#fb7185',b600:'#e11d48',b700:'#9f1239'} };
    function hexToRgba(hex,a){ const h=hex.replace('#',''); const n=parseInt(h.length===3?h.split('').map(c=>c+c).join(''):h,16); const r=(n>>16)&255,g=(n>>8)&255,b=n&255; return `rgba(${r}, ${g}, ${b}, ${a})`; }
    function setTheme(name){ const t=THEMES[name]||THEMES.indigo; root.style.setProperty('--brand-500',t.b500); root.style.setProperty('--brand-600',t.b600); root.style.setProperty('--brand-700',t.b700); if(logoBox){ logoBox.style.backgroundImage=`linear-gradient(135deg, ${t.b500}, ${t.b700})`; logoBox.style.boxShadow=`0 10px 15px -3px ${hexToRgba(t.b700,0.3)}, 0 4px 6px -4px ${hexToRgba(t.b700,0.3)}`; } }
    swatches.forEach(s=>s.addEventListener('click',()=>setTheme(s.dataset.theme)));
    if (applyBtn) applyBtn.addEventListener('click',()=>{ if(titleEl && titleInput && titleInput.value.trim()) titleEl.textContent=titleInput.value.trim(); });
  }

  // =============== Advanced Labs ===============
  // Reduction Lab (drag-and-drop-ish via clicks) MVP
  function initReductionLab(){
    const palette = document.querySelectorAll('#reduction-lab .reduction-node');
    const pipe = document.getElementById('rl-pipeline');
    const clear = document.getElementById('rl-clear');
    const explain = document.getElementById('rl-explain');
    const stats = document.getElementById('rl-stats');
    const expl = document.getElementById('rl-explainer');
    if (!pipe || !palette.length) return;

    const names = { '3sat':'3-SAT', 'clique':'CLIQUE', 'vc':'Vertex Cover', 'is':'Independent Set', '3color':'3-Coloring' };
    const edges = new Set([
      '3sat>clique', 'clique>vc', 'vc>is', 'is>3color'
    ]);
    const blowup = { '3sat>clique': n=>`O(n)`, 'clique>vc': n=>`O(n)`, 'vc>is': n=>`O(n)`, 'is>3color': n=>`O(n)` };
    const cert = {
      '3sat>clique': 'assignment → one literal per clause',
      'clique>vc': 'k-clique ↔ |V|−k cover',
      'vc>is': 'cover ↔ complement independent set',
      'is>3color': 'independent set forces color class'
    };
    const examples = {
      '3sat>clique': 'Example: (x1∨¬x2∨x3)∧(¬x1∨x2∨x3) ⇒ nodes are clause-literals; edges connect non-conflicting literals across clauses.',
      'clique>vc': 'Example: k=3 clique ⇒ vertex cover size |V|−3. Certificate maps to complement.',
      'vc>is': 'Example: VC C ⇒ V\\C is an independent set.',
      'is>3color': 'Example: Independent set can share the same color in 3-coloring.'
    };
    const seq=[];
    function render(){
      pipe.innerHTML='';
      pipe.style.position='relative';
      // SVG overlay for animated edges
      const svg = document.createElementNS('http://www.w3.org/2000/svg','svg');
      svg.setAttribute('width','100%'); svg.setAttribute('height','70'); svg.style.position='absolute'; svg.style.left='0'; svg.style.top='18px'; svg.style.pointerEvents='none';
      const items=[];
      seq.forEach((id,idx)=>{
        const b = el('span',{className:'chip', textContent:names[id]||id});
        b.tabIndex=0; b.setAttribute('draggable','true'); b.dataset.idx=String(idx);
        b.addEventListener('dragstart', ev=>{ ev.dataTransfer.setData('text/plain', b.dataset.idx); });
        b.addEventListener('dragover', ev=>{ ev.preventDefault(); });
        b.addEventListener('drop', ev=>{ ev.preventDefault(); const from=Number(ev.dataTransfer.getData('text/plain')); const to=Number(b.dataset.idx); if(Number.isFinite(from)&&Number.isFinite(to)&&from!==to){ const x=seq.splice(from,1)[0]; seq.splice(to,0,x); render(); }});
        pipe.appendChild(b);
        items.push(b);
        if (idx<seq.length-1){ const arrow=el('span',{textContent:'  '}); pipe.appendChild(arrow); }
      });
      // Draw animated edges between chips
      pipe.appendChild(svg);
      setTimeout(()=>{
        svg.innerHTML='';
        for(let i=0;i<items.length-1;i++){
          const a=items[i].getBoundingClientRect();
          const b=items[i+1].getBoundingClientRect();
          const r=pipe.getBoundingClientRect();
          const x1=a.left - r.left + a.width/2; const y1=22;
          const x2=b.left - r.left + b.width/2; const y2=22;
          const path=document.createElementNS('http://www.w3.org/2000/svg','path');
          const d=`M ${x1} ${y1} C ${(x1+x2)/2} ${y1-15}, ${(x1+x2)/2} ${y2+15}, ${x2} ${y2}`;
          path.setAttribute('d', d);
          path.setAttribute('stroke','rgba(99,102,241,0.9)');
          path.setAttribute('stroke-width','2');
          path.setAttribute('fill','none');
          path.style.transition='stroke-dashoffset 600ms ease';
          const len=200; path.setAttribute('stroke-dasharray', String(len)); path.setAttribute('stroke-dashoffset', String(len));
          svg.appendChild(path);
          // animate
          requestAnimationFrame(()=>{ path.setAttribute('stroke-dashoffset','0'); });
        }
      },0);

      if (stats){
        let ok=true, details=[]; for(let i=0;i<seq.length-1;i++){
          const k=`${seq[i]}>${seq[i+1]}`; if(!edges.has(k)) { ok=false; details.push(`No known poly-time reduction: ${names[seq[i]]} → ${names[seq[i+1]]}`); }
          else details.push(`${names[seq[i]]} → ${names[seq[i+1]]}: size blowup ${blowup[k]('n')}, certificate: ${cert[k]}`);
        }
        stats.textContent = seq.length? (ok? 'Pipeline valid. '+details.join(' | ') : 'Invalid pipeline. '+details.join(' | ')) : 'Click problems above to build a pipeline.';
      }
      if (expl){
        if (seq.length<2) expl.textContent=''; else {
          const lines=[]; for(let i=0;i<seq.length-1;i++){ const k=`${seq[i]}>${seq[i+1]}`; if(examples[k]) lines.push(examples[k]); }
          expl.textContent = lines.join(' ');
        }
      }
    }
    palette.forEach(btn=>btn.addEventListener('click',()=>{ seq.push(btn.dataset.prob); render(); }));
    clear && clear.addEventListener('click',()=>{ seq.length=0; render(); expl && (expl.textContent=''); });
    explain && explain.addEventListener('click',()=>{
      if (seq.length<2){ expl && (expl.textContent='Add at least two nodes.'); return; }
      const lines=[]; for(let i=0;i<seq.length-1;i++){ const k=`${seq[i]}>${seq[i+1]}`; if(edges.has(k)) lines.push(`${names[seq[i]]} reduces to ${names[seq[i+1]]} in poly time. Witness mapping: ${cert[k]}.`); else lines.push(`No standard reduction known from ${names[seq[i]]} to ${names[seq[i+1]]}.`);} expl && (expl.textContent=lines.join(' '));
    });
    render();
  }

  // Scaling Wall (tiny random instances + measured backtracking work)
  function initScalingWall(){
    const sel=$('#sw-problem'); const rn=$('#sw-n'); const rd=$('#sw-density'); const run=$('#sw-run'); const clr=$('#sw-clear'); const chart=$('#sw-chart'); const log=$('#sw-log'); const nVal=$('#sw-n-val'); const dVal=$('#sw-density-val');
    if (!sel || !rn || !rd || !run || !clr || !chart) return;
    const ctx = chart.getContext('2d');
    // add Export CSV button
    let exportBtn = document.getElementById('sw-export');
    if (!exportBtn && clr && clr.parentElement){ exportBtn = el('button',{id:'sw-export', className:'btn-ghost', textContent:'Export CSV'}); clr.parentElement.appendChild(exportBtn); }
    function setText(){ nVal && (nVal.textContent=String(rn.value)); dVal && (dVal.textContent=`${rd.value}%`); }
    rn.addEventListener('input', setText); rd.addEventListener('input', setText); setText();
    const runs=[]; // {problem,n,density,work,color}
    function clearPlot(){ ctx.clearRect(0,0,chart.width,chart.height); log && (log.textContent=''); runs.length=0; }
    clr.addEventListener('click', clearPlot);
    function plotPoint(x,y,color='rgba(16,185,129,0.9)'){ ctx.fillStyle=color; ctx.beginPath(); ctx.arc(x,y,3,0,Math.PI*2); ctx.fill(); }
    function axes(){ ctx.strokeStyle='rgba(148,163,184,0.5)'; ctx.beginPath(); ctx.moveTo(32,8); ctx.lineTo(32,200); ctx.lineTo(300,200); ctx.stroke(); }
    function redraw(){ ctx.clearRect(0,0,chart.width,chart.height); axes(); const xscale=260/20; const yscale=180/10000; runs.forEach(r=>{ const x=32+(r.n-4)*xscale; const y=200-Math.min(180, r.work*yscale); plotPoint(x,y,r.color); }); // legend
      let lx=40, ly=16; runs.slice(-5).forEach(r=>{ ctx.fillStyle=r.color; ctx.fillRect(lx,ly,8,8); ctx.fillStyle='rgba(226,232,240,0.9)'; ctx.fillText(`${r.problem}@n=${r.n}`, lx+12, ly+8); ly+=14; }); }
    function toCSV(){ const header='problem,n,density,work'; const lines=runs.map(r=>`${r.problem},${r.n},${r.density},${r.work}`); return [header,...lines].join('\n'); }
    exportBtn && exportBtn.addEventListener('click',()=>{ const blob=new Blob([toCSV()],{type:'text/csv'}); const url=URL.createObjectURL(blob); const a=el('a',{href:url,download:'scaling_wall.csv'}); document.body.appendChild(a); a.click(); a.remove(); URL.revokeObjectURL(url); });
    function randSAT(n, density){ // density ~ clause/var ratio *100
      const vars = Array.from({length:n},(_,i)=>`x${i+1}`);
      const m = Math.max(1, Math.round((density/100)*n*4));
      const clauses=[]; for(let i=0;i<m;i++){ const lits=[]; for(let j=0;j<3;j++){ const v=vars[Math.floor(Math.random()*vars.length)]; const neg=Math.random()<0.5; lits.push(neg?'!'+v:v); } clauses.push(lits); }
      return clauses; // array of clauses of size 3
    }
    function evalClause(cl, env){ return cl.some(L=> L[0]==='!'? !env[L.slice(1)] : !!env[L]); }
    function satBacktrack(n, clauses, timeCapMs=800){ const names=Array.from({length:n},(_,i)=>`x${i+1}`); const start=performance.now(); let nodes=0; function dfs(i, env){ if(performance.now()-start>timeCapMs) return null; if(i===n){ nodes++; return clauses.every(c=>evalClause(c,env))? env : null; } env[names[i]]=false; nodes++; const a=dfs(i+1,env); if(a) return a; env[names[i]]=true; nodes++; return dfs(i+1,env); } const sol=dfs(0,{}); return {nodes, sol, timeout: (performance.now()-start>timeCapMs)}; }
    function randGraph(n, density){ const edges=[]; for(let u=1;u<=n;u++){ for(let v=u+1;v<=n;v++){ if(Math.random()<density/100) edges.push([u,v]); } } return edges; }
    function cliqueBruteforce(n, edges, k){ const adj=Array.from({length:n+1},()=>new Set()); edges.forEach(([u,v])=>{adj[u].add(v); adj[v].add(u)}); const vs=Array.from({length:n},(_,i)=>i+1); function* comb(arr,k,start=0,cur=[]){ if(cur.length===k){ yield cur.slice(); return;} for(let i=start;i<arr.length;i++){ cur.push(arr[i]); yield* comb(arr,k,i+1,cur); cur.pop(); } } let cnt=0; for(const S of comb(vs, Math.max(2,Math.min(5,Math.floor(n/3))))){ cnt++; let ok=true; for(let i=0;i<S.length && ok;i++) for(let j=i+1;j<S.length && ok;j++){ if(!adj[S[i]].has(S[j])) ok=false; } if(ok) return {found:true, nodes:cnt}; } return {found:false, nodes:cnt}; }
    run.addEventListener('click',()=>{ const n=Number(rn.value); const density=Number(rd.value); const color = sel.value==='sat' ? 'rgba(59,130,246,0.9)' : 'rgba(249,115,22,0.9)'; if(sel.value==='sat'){ const inst=randSAT(n,density); const res=satBacktrack(n,inst); runs.push({problem:'SAT', n, density, work:res.nodes, color}); log && (log.textContent=`SAT n=${n}, clauses≈${inst.length}, nodes=${res.nodes}${res.timeout?' (timeout cap)':''}`); } else { const edges=randGraph(n,density); const res=cliqueBruteforce(n,edges); runs.push({problem:'CLIQUE', n, density, work:res.nodes, color}); log && (log.textContent=`CLIQUE n=${n}, edges=${edges.length}, combos=${res.nodes}`); } redraw(); });
  }

  // Approximation Game (VC & Set Cover)
  function initApproxGame(){
    const sel=$('#ag-problem'); const size=$('#ag-size'); const sizeVal=$('#ag-size-val'); const gen=$('#ag-generate'); const runG=$('#ag-greedy'); const runX=$('#ag-exact'); const inst=$('#ag-instance'); const out=$('#ag-result');
    if(!sel || !size || !gen || !runG || !runX) return;
    size.addEventListener('input',()=> sizeVal && (sizeVal.textContent=String(size.value)));
    let G=null; let U=null, sets=null;
    function randVC(n){ const edges=[]; for(let u=1;u<=n;u++) for(let v=u+1;v<=n;v++) if(Math.random()<0.3) edges.push([u,v]); return {n,edges}; }
    function vcGreedy(g){ const edges=g.edges.slice(); const cover=new Set(); while(edges.length){ const deg=new Map(); edges.forEach(([u,v])=>{ deg.set(u,(deg.get(u)||0)+1); deg.set(v,(deg.get(v)||0)+1); }); const v=[...deg.entries()].sort((a,b)=>b[1]-a[1])[0][0]; cover.add(v); for(let i=edges.length-1;i>=0;i--){ if(edges[i][0]===v||edges[i][1]===v) edges.splice(i,1); } } return [...cover]; }
    function vcExact(g){ const n=g.n; const vs=Array.from({length:n},(_,i)=>i+1); let best=null; function* subsets(arr,i=0,cur=[]){ if(i===arr.length){ yield cur.slice(); return;} cur.push(arr[i]); yield* subsets(arr,i+1,cur); cur.pop(); yield* subsets(arr,i+1,cur); } outer: for(const S of subsets(vs)){ // prune large
        if(best && S.length>=best.length) continue; for(const [u,v] of g.edges){ if(!(S.includes(u)||S.includes(v))) continue outer; } best=S.slice(); } return best||[]; }
    function randSetCover(n){ const U=Array.from({length:n},(_,i)=>i+1); const sets=[]; for(let i=0;i<n;i++){ const s=new Set(); for(const u of U) if(Math.random()<0.35) s.add(u); if(s.size) sets.push([...s]); } return {U,sets}; }
    function scGreedy(U,sets){ const need=new Set(U); const pick=[]; while(need.size){ let best=-1,idx=-1; sets.forEach((S,i)=>{ const gain=S.filter(x=>need.has(x)).length; if(gain>best){ best=gain; idx=i; } }); if(best<=0) break; pick.push(idx); sets[idx].forEach(x=>need.delete(x)); } return pick; }
    function scExact(U,sets){ const m=sets.length; let best=null; function dfs(i,pick,covered){ if(i===m){ if(covered.size===U.length){ if(!best||pick.length<best.length) best=pick.slice(); } return; } dfs(i+1,pick,covered); const newC=new Set(covered); sets[i].forEach(x=>newC.add(x)); pick.push(i); dfs(i+1,pick,newC); pick.pop(); } dfs(0,[],new Set()); return best||[]; }
    function prettyVCSet(arr){ return '{'+arr.sort((a,b)=>a-b).join(', ')+'}'; }
    function prettyPick(arr){ return '{'+arr.sort((a,b)=>a-b).map(i=>'S'+i).join(', ')+'}'; }
    gen.addEventListener('click',()=>{ const n=Number(size.value); if(sel.value==='vc'){ G=randVC(n); inst && (inst.textContent=`VC: n=${G.n}, edges=${G.edges.length} — edges: `+G.edges.map(e=>`(${e[0]}-${e[1]})`).join(', ')); } else { ({U,sets}=randSetCover(n)); inst && (inst.textContent=`Set Cover: |U|=${U.length}, m=${sets.length} — sets: `+sets.map((S,i)=>`S${i}:{${S.join(', ')}}`).join('  ')); } out && (out.textContent=''); });
    runG.addEventListener('click',()=>{ if(sel.value==='vc' && G){ const g=vcGreedy(G); out && (out.textContent=`Greedy VC = ${prettyVCSet(g)} (size ${g.length})`); } else if(sel.value==='sc' && U){ const pick=scGreedy(U,sets); out && (out.textContent=`Greedy SC = ${prettyPick(pick)} (size ${pick.length})`); } });
    runX.addEventListener('click',()=>{ if(sel.value==='vc' && G){ const opt=vcExact(G); const text=`Optimal VC = ${prettyVCSet(opt)} (size ${opt.length})`; if(out){ const greedy=vcGreedy(G).length; out.textContent = text + (greedy>opt.length? ' — counterexample: greedy is worse' : ''); } } else if(sel.value==='sc' && U){ const opt=scExact(U,sets); const text=`Optimal SC = ${prettyPick(opt)} (size ${opt.length})`; if(out){ const greedy=scGreedy(U,sets).length; out.textContent = text + (greedy>opt.length? ' — counterexample: greedy is worse' : ''); } } });
  }

  // Parameterized Complexity Playground (k-Clique, k-Path simplified)
  function initFPTPlayground(){
    const sel=$('#fpt-problem'); const rn=$('#fpt-n'); const rk=$('#fpt-k'); const run=$('#fpt-run'); const randBtn=$('#fpt-rand'); const out=$('#fpt-output'); const nVal=$('#fpt-n-val'); const kVal=$('#fpt-k-val');
    if(!sel || !rn || !rk || !run || !randBtn) return;
    rn.addEventListener('input',()=> nVal && (nVal.textContent=String(rn.value)));
    rk.addEventListener('input',()=> kVal && (kVal.textContent=String(rk.value)));
    let edges=[]; function randGraph(n,p=0.25){ const E=[]; for(let u=1;u<=n;u++) for(let v=u+1;v<=n;v++) if(Math.random()<p) E.push([u,v]); return E; }
    function kClique(n,k,E){ const adj=Array.from({length:n+1},()=>new Set()); E.forEach(([u,v])=>{adj[u].add(v); adj[v].add(u)}); const vs=Array.from({length:n},(_,i)=>i+1); function* comb(arr,k,start=0,cur=[]){ if(cur.length===k){ yield cur.slice(); return;} for(let i=start;i<arr.length;i++){ cur.push(arr[i]); yield* comb(arr,k,i+1,cur); cur.pop(); } } let checked=0; for(const S of comb(vs,k)){ checked++; let ok=true; for(let i=0;i<S.length && ok;i++) for(let j=i+1;j<S.length && ok;j++){ if(!adj[S[i]].has(S[j])) ok=false; } if(ok) return {found:true, checked}; } return {found:false, checked}; }
    function kPath(n,k,E){ // naive DFS bounded by k
      const G=Array.from({length:n+1},()=>[]); E.forEach(([u,v])=>{G[u].push(v); G[v].push(u)}); let checked=0; function dfs(u,vis,len){ if(len===k) return true; for(const v of G[u]) if(!vis.has(v)){ vis.add(v); checked++; if(dfs(v,vis,len+1)) return true; vis.delete(v);} return false; } for(let s=1;s<=n;s++){ const vis=new Set([s]); if(dfs(s,vis,1)) return {found:true, checked}; } return {found:false, checked}; }
    randBtn.addEventListener('click',()=>{ const n=Number(rn.value); edges=randGraph(n); out && (out.textContent=`Random graph generated: n=${n}, edges=${edges.length}`); });
    function kernelizeVC(n,E,k){ // simple rule: remove vertices with degree < k-1
      const adj=Array.from({length:n+1},()=>new Set()); E.forEach(([u,v])=>{adj[u].add(v); adj[v].add(u)});
      let changed=true; const removed=[];
      while(changed){ changed=false; for(let v=1; v<=n; v++){ if(adj[v] && adj[v].size>0 && adj[v].size < k-1){ // remove v
            for(const u of adj[v]){ adj[u].delete(v); }
            adj[v].clear(); removed.push(v); changed=true; }
        }
      }
      let remV=0, remE=0; for(let v=1; v<=n; v++){ if(adj[v] && adj[v].size>=0) { if(adj[v].size>0) remV++; remE+=adj[v].size; } } remE=Math.round(remE/2);
      return {removed:removed.sort((a,b)=>a-b), remainingV:remV, remainingE:remE};
    }
    run.addEventListener('click',()=>{ const n=Number(rn.value), k=Number(rk.value); if(!edges.length) edges=randGraph(n); if(sel.value==='kclique'){ const r=kClique(n,k,edges); const ker=kernelizeVC(n,edges,k); out && (out.textContent=`k-Clique k=${k}: ${r.found?'FOUND':'not found'}; combinations checked=${r.checked}. Kernelization demo (VC rule): removed ${ker.removed.length} low-degree vertices [${ker.removed.join(', ')}], remaining ~ V=${ker.remainingV}, E=${ker.remainingE}.`); } else { const r=kPath(n,k,edges); out && (out.textContent=`k-Path k=${k}: ${r.found?'FOUND':'not found'}; DFS steps=${r.checked}`); } });
  }

  // Fine-Grained Complexity Stopwatch (ETH/SETH-inspired toy model)
  function initFineGrainedStopwatch(){
    const rk=$('#fg-k'); const rn=$('#fg-n'); const btn=$('#fg-calc'); const out=$('#fg-output'); const kVal=$('#fg-k-val'); const nVal=$('#fg-n-val');
    if(!rk || !rn || !btn) return;
    rk.addEventListener('input',()=> kVal && (kVal.textContent=String(rk.value)));
    rn.addEventListener('input',()=> nVal && (nVal.textContent=String(rn.value)));
    function models(k,n){
      const out=[];
      // brute force 2^n
      const brute = Math.pow(2,n);
      out.push({name:'Brute-force', steps: brute, tip:'Try all assignments (2^n).'});
      if(k<=2){ const poly = n*n; out.push({name:'Poly-time (2-SAT-like)', steps: poly, tip:'2-SAT is solvable in polynomial time.'}); }
      // DPLL-ish c^n (toy): c grows with k
      const base = 1.3 + (k-3)*0.15; const dpll = Math.pow(base, n);
      out.push({name:`Branching (~${base.toFixed(2)}^n)`, steps: dpll, tip:'Toy DPLL-style branching factor depending on k.'});
      return out;
    }
    function humanize(x){ return x>1e9? `≈ ${(x/1e9).toFixed(2)}B` : x>1e6? `≈ ${(x/1e6).toFixed(2)}M` : x>1e3? `≈ ${(x/1e3).toFixed(2)}K` : `≈ ${x.toFixed(0)}`; }
    btn.addEventListener('click',()=>{ const k=Number(rk.value), n=Number(rn.value); const ms=models(k,n); if(out){ out.innerHTML=''; ms.forEach(m=>{ const span=el('span',{className:'chip', textContent:`${m.name}: ${humanize(m.steps)} steps`}); span.title=m.tip; out.appendChild(span); out.appendChild(document.createTextNode(' ')); }); } });
  }
})();
