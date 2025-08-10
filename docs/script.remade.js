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
})();
