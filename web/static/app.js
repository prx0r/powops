const T=new URLSearchParams(location.search).get('token')||'';
const G=(p)=>fetch(p+'?token='+encodeURIComponent(T)).then(r=>{if(!r.ok)throw new Error(r.status);return r.json()}).catch(e=>({error:e.message}));
let V='status';
setInterval(()=>{const e=document.getElementById('clk');if(e)e.textContent=new Date().toISOString().slice(11,19)+'Z'},1000);
const rail=document.getElementById('rail');
['status','history','uptime','volume','schemas','alerts','incidents','events','repos'].forEach((id,i)=>{
  const d=document.createElement('div');d.className='i'+(i===0?' a':'');
  d.textContent=id;d.onclick=()=>go(id);d.dataset.v=id;rail.appendChild(d);});
function go(v){document.querySelectorAll('.rail .i').forEach(i=>i.classList.toggle('a',i.dataset.v===v));V=v;render();}
function age_str(s){if(s==null)return'--';if(s<60)return s+'s';if(s<3600)return Math.round(s/60)+'m';if(s<86400)return Math.round(s/3600)+'h';return Math.round(s/86400)+'d';}
function fmt_ts(iso){if(!iso)return'--';try{return new Date(iso).toISOString().slice(11,16)}catch(e){return'--';}}
function esc(s){return String(s||'').replace(/</g,'&lt;');}
function N(v){return v==null?'--':v<1?v.toPrecision(3):Number(v).toLocaleString(undefined,{maximumFractionDigits:2});}
function verified_at(s){
  if(!s.checked_at)return'';
  const ago=(Date.now()-new Date(s.checked_at).getTime())/1000;
  const tag=ago<60?'live':ago<3600?Math.round(ago/60)+'m ago':Math.round(ago/3600)+'h ago';
  const h=s.check_hash?s.check_hash.slice(0,8):'';
  return`<span class="verified">${tag}</span> <span class="hash">${h}</span>`;
}
async function render(){
  const el=document.getElementById('ed');
  const sb=document.getElementById('sb');
  if(V==='status'){
    const d=await G('/api/status');
    if(d.error){el.innerHTML=`<div class="box">${esc(d.error)}</div>`;return;}
    const gs={};(d.sources||[]).forEach(s=>{if(!gs[s.garden])gs[s.garden]=[];gs[s.garden].push(s);});
    sb.innerHTML=Object.entries(gs).map(([g,srcs])=>{
      const ok=srcs.filter(s=>s.status==='ok').length;
      return`<div class="kv"><div class="k">${esc(g)}</div><div class="v">${ok}/${srcs.length}</div></div>`;
    }).join('');
    let h=`<table><tr><th>garden</th><th>source</th><th>age</th><th>status</th><th>verified</th></tr>`;
    (d.sources||[]).forEach(s=>{
      h+=`<tr><td class="dim">${esc(s.garden)}</td><td>${esc(s.source_id)}</td>`;
      h+=`<td>${age_str(s.age_seconds)}</td>`;
      h+=`<td class="status-${s.status}">${esc(s.status)}</td>`;
      h+=`<td>${verified_at(s)}</td></tr>`;
    });
    el.innerHTML=h+`</table><div class="box">server checked at ${d.checked_at} — hashes are server-signed, cannot be faked</div>`;
  }
  if(V==='history'){
    sb.innerHTML='';
    const d=await G('/api/history?days=1');
    if(d.error){el.innerHTML=`<div class="box">${esc(d.error)}</div>`;return;}
    let h=`<table><tr><th>time</th><th>source</th><th>status</th><th>checked</th><th>chain</th></tr>`;
    (d.entries||[]).slice(-100).reverse().forEach(e=>{
      h+=`<tr><td>${fmt_ts(e.ts)}</td><td>${esc(e.source_id)}</td>`;
      h+=`<td class="status-${e.status}">${esc(e.status)}</td>`;
      h+=`<td>${fmt_ts(e.checked_at)}</td>`;
      h+=`<td class="hash">${(e.chain_hash||'').slice(0,8)}</td></tr>`;
    });
    el.innerHTML=h+`</table>`;
  }
  if(V==='uptime'){
    sb.innerHTML='';
    const d=await G('/api/uptime?days=7');
    if(d.error){el.innerHTML=`<div class="box">${esc(d.error)}</div>`;return;}
    let h=`<table><tr><th>source</th><th>checks</th><th>ok%</th><th>stale</th><th>error</th><th>avg age</th></tr>`;
    Object.entries(d.sources||{}).sort((a,b)=>(b[1].uptime_pct||0)-(a[1].uptime_pct||0)).forEach(([sid,s])=>{
      h+=`<tr><td>${esc(sid)}</td><td>${s.total_checks||0}</td><td>${s.uptime_pct!=null?s.uptime_pct+'%':'--'}</td>`;
      h+=`<td>${s.stale||0}</td><td>${s.error||0}</td>`;
      h+=`<td>${s.mean_age_seconds!=null?age_str(s.mean_age_seconds):'--'}</td></tr>`;
    });
    el.innerHTML=h+`</table>`;
  }
  if(V==='volume'){
    sb.innerHTML='';
    const d=await G('/api/volume?days=7');
    if(d.error){el.innerHTML=`<div class="box">${esc(d.error)}</div>`;return;}
    let h=`<table><tr><th>source</th><th>mean</th><th>stddev</th><th>min</th><th>max</th></tr>`;
    Object.entries(d.sources||{}).sort((a,b)=>(b[1].mean||0)-(a[1].mean||0)).forEach(([sid,s])=>{
      h+=`<tr><td>${esc(sid)}</td><td>${N(s.mean)}</td><td>${N(s.stddev)}</td><td>${N(s.min)}</td><td>${N(s.max)}</td></tr>`;
    });
    el.innerHTML=h+`</table>`;
  }
  if(V==='schemas'){
    sb.innerHTML='';
    const d=await G('/api/schemas');
    if(d.error){el.innerHTML=`<div class="box">${esc(d.error)}</div>`;return;}
    if(!(d.schemas||[]).length){el.innerHTML=`<div class="box">no schemas</div>`;return;}
    let h=`<table><tr><th>source</th><th>garden</th><th>cols</th><th>since</th></tr>`;
    (d.schemas||[]).forEach(s=>{
      h+=`<tr><td>${esc(s.source_id)}</td><td class="dim">${esc(s.garden)}</td>`;
      h+=`<td>${(s.columns||[]).length}</td><td>${fmt_ts(s.snapshot_at)}</td></tr>`;
    });
    el.innerHTML=h+`</table>`;
  }
  if(V==='alerts'){
    sb.innerHTML='';
    const d=await G('/api/alerts');
    if(d.error){el.innerHTML=`<div class="box">${esc(d.error)}</div>`;return;}
    const a=d.alerts||{};
    if(!Object.keys(a).length){el.innerHTML=`<div class="box">no alert state (first run)</div>`;return;}
    let h=`<table><tr><th>source</th><th>status</th><th>updated</th></tr>`;
    Object.entries(a).sort().forEach(([sid,info])=>{
      h+=`<tr><td>${esc(sid)}</td><td class="status-${info.status||''}">${esc(info.status||'')}</td>`;
      h+=`<td>${fmt_ts(info.updated_at)}</td></tr>`;
    });
    el.innerHTML=h+`</table>`;
  }
  if(V==='incidents'){
    sb.innerHTML='';
    const d=await G('/api/incidents?status=all');
    if(d.error){el.innerHTML=`<div class="box">${esc(d.error)}</div>`;return;}
    const inc=d.incidents||[];
    if(!inc.length){el.innerHTML=`<div class="box">no incidents</div>`;return;}
    let h=`<table><tr><th>id</th><th>source</th><th>garden</th><th>severity</th><th>status</th><th>opened</th></tr>`;
    inc.forEach(i=>{
      h+=`<tr><td class="dim">${esc(i.incident_id)}</td><td>${esc(i.source_id)}</td>`;
      h+=`<td class="dim">${esc(i.garden)}</td><td>${esc(i.severity)}</td>`;
      h+=`<td>${esc(i.status)}</td><td>${fmt_ts(i.opened_at)}</td></tr>`;
    });
    el.innerHTML=h+`</table>`;
  }
  if(V==='events'){
    sb.innerHTML='';
    const d=await G('/api/events?days=1');
    if(d.error){el.innerHTML=`<div class="box">${esc(d.error)}</div>`;return;}
    const ev=d.events||[];
    if(!ev.length){el.innerHTML=`<div class="box">no events in last 24h</div>`;return;}
    let h=`<table><tr><th>time</th><th>type</th><th>source</th><th>garden</th><th>severity</th></tr>`;
    ev.slice(0,100).forEach(e=>{
      h+=`<tr><td>${fmt_ts(e.at)}</td><td>${esc(e.type)}</td>`;
      h+=`<td>${esc(e.source_id||'')}</td><td class="dim">${esc(e.garden)}</td>`;
      h+=`<td>${esc(e.severity||'')}</td></tr>`;
    });
    el.innerHTML=h+`</table>`;
  }
  if(V==='repos'){
    sb.innerHTML='';
    const d=await G('/api/repos');
    if(d.error){el.innerHTML=`<div class="box">${esc(d.error)}</div>`;return;}
    const repos=d.repos||{};
    const ci_colors={success:'status-ok',failure:'status-error',pending:'status-stale',none:'status-unknown',unknown:'status-unknown'};
    let h=`<table><tr><th>repo</th><th>commit</th><th>message</th><th>ci</th><th>date</th></tr>`;
    Object.entries(repos).sort().forEach(([name,info])=>{
      const c=info.last_commit||{};
      const sha=(c.sha||'').slice(0,8);
      const msg=(c.message||'').slice(0,38);
      const date=(c.date||'').slice(0,10);
      const ci=info.ci_status||'unknown';
      h+=`<tr><td>${esc(name)}</td><td class="hash">${esc(sha)}</td>`;
      h+=`<td>${esc(msg)}</td><td class="${ci_colors[ci]||''}">${esc(ci)}</td>`;
      h+=`<td class="dim">${esc(date)}</td></tr>`;
    });
    el.innerHTML=h+`</table><div class="box">github status — requires authenticated gh CLI</div>`;
  }
}
G('/api/health').then(h=>document.getElementById('health').textContent=h.ok?'live':'down').catch(()=>document.getElementById('health').textContent='down');
render();setInterval(()=>render(),60000);
