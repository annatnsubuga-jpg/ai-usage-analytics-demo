/* ═══ VIEW 0 · RANKINGS ═════════════════════════════════ */
const W = {chat:1, cowork:4, code:6};
const METRICS = [
  ['all',    'All products', null],
  ['chat',   'Chat',         'messages'],
  ['cowork', 'Cowork',       'coworkMessages'],
  ['code',   'Claude Code',  'codeSessions'],
  ['spend',  'Spend',        'spend'],
  ['depth',  'Depth of use', null],
];
/* Depth of use is scored across five categories rather than one number, because
   no single count describes how deeply someone has taken Claude on.

     Volume       weighted activity, chat 1 / Cowork 4 / Code 6
     Breadth      how many of the five surfaces they touch at all
     Consistency  share of the period they were active
     Output       pull requests, artifacts and file edits
     Building     projects created, so set up for reuse rather than asked one-offs

   Each is scored out of 100 against the best performer in that category, then
   averaged. Leading a category gives you 100 for it. Five equal fifths, no
   hidden weighting. Spend is deliberately not one of them: it is ranked on its
   own tab, because costing more is not the same as using it more deeply. */
const DEPTH_CATS = [
  ['Volume',      m => (m.messages||0) + (m.coworkMessages||0)*4 + (m.codeSessions||0)*6],
  ['Breadth',     m => ['messages','coworkMessages','codeSessions','projectsCreated','prs']
                        .reduce((n,f)=>n+((m[f]||0)>0?1:0),0)],
  ['Consistency', m => m._pct||0],
  ['Output',      m => (m.prs||0) + (m.artifacts||0) + (m.fileEdits||0)],
  ['Building',    m => m.projectsCreated||0],
];
/* the monthly records carry prs, artifacts, fileEdits and projectsCreated;
   the all-time roster does not, so all-time is the sum of the months */
let _rollup = null;
function rolledUp(){
  if(_rollup) return _rollup;
  _rollup = {};
  const F = ['messages','coworkMessages','codeSessions','prs','artifacts',
             'fileEdits','projectsCreated','daysActive','spend'];
  let totalDays = 0;
  MONTHS.forEach(k=>{
    const md = DATA.months[k]; if(!md) return;
    totalDays += md.days||0;
    md.members.forEach(m=>{
      const a = _rollup[m.email] || (_rollup[m.email] =
        Object.assign({}, m, Object.fromEntries(F.map(f=>[f,0]))));
      F.forEach(f=> a[f] += (m[f]||0));
    });
  });
  Object.values(_rollup).forEach(a=>{ a._pct = totalDays ? a.daysActive/totalDays : 0; });
  return _rollup;
}
function depthBreakdown(pool){
  /* pool is the set being compared; best in each category scores 100 */
  const best = DEPTH_CATS.map(([,fn]) => Math.max(1e-9, ...pool.map(fn)));
  return m => {
    const parts = DEPTH_CATS.map(([name,fn],i)=>({name, pct: Math.min(100, fn(m)/best[i]*100)}));
    return {parts, score: parts.reduce((a,p)=>a+p.pct,0)/parts.length};
  };
}
const gbp=n=>'£'+Number(n||0).toLocaleString('en-GB',{minimumFractionDigits:2,maximumFractionDigits:2});
let rankMetric='all', rankTeam='all';

/* Leavers are excluded from the rankings only. They stay in every other view,
   because the raw figures for a month they worked are still true.
   The list lives in the DATA, as meta.leavers {name: lastWorkingDay}, so that a
   public build simply has none. Never hardcode real names in this file: it is
   shared with the public demo. Source for the real build is the Leavers database
   in Notion, IT @ TZ. That database is known to hold at least one stale row for
   someone who has not left, so check each entry against the current roster
   before adding it. */
function hasLeft(name){
  const d = (DATA && DATA.meta && DATA.meta.leavers || {})[name];
  return !!d && new Date(d+'T23:59:59') < new Date();
}
function setRankMetric(v){ rankMetric=v; const y=window.scrollY; render(); window.scrollTo(0,y); }
function setRankTeam(v){ rankTeam=v; const y=window.scrollY; render(); window.scrollTo(0,y); }
function rankPeriods(){ return MONTHS.concat([ALLTIME]); }
function stepMonth(d){
  const ps=rankPeriods(), i=ps.indexOf(isAll()?ALLTIME:currentMonth)+d;
  if(i<0||i>=ps.length) return;
  setMonth(ps[i]);
}

function scoreOf(m, metric, span){
  const k = (metric||rankMetric);
  if(k==='depth')  return m._depth||0;
  if(k==='spend')  return m.spend!=null ? m.spend : spendAllTime(m.email);
  if(k==='chat')   return m.messages||0;
  if(k==='cowork') return m.coworkMessages||0;
  if(k==='code')   return m.codeSessions||0;
  return (m.messages||0)*W.chat + (m.coworkMessages||0)*W.cowork + (m.codeSessions||0)*W.code;
}
function unitLabel(){
  return rankMetric==='chat'?'messages': rankMetric==='cowork'?'messages':
         rankMetric==='code'?'sessions': rankMetric==='spend'?'spend':
         rankMetric==='depth'?'depth':'points';
}
const showVal=v=>rankMetric==='spend'?gbp(v):rankMetric==='depth'?Number(v).toFixed(1):fmt(v);
function mixBar(m){
  const a=(m.messages||0)*W.chat, b=(m.coworkMessages||0)*W.cowork, c=(m.codeSessions||0)*W.code;
  const t=a+b+c||1, p=n=>(n/t*100).toFixed(1)+'%';
  return '<div class="mix" title="chat '+p(a)+' · cowork '+p(b)+' · code '+p(c)+'">'+
    '<i style="width:'+p(a)+';background:var(--chat)"></i>'+
    '<i style="width:'+p(b)+';background:var(--cowork)"></i>'+
    '<i style="width:'+p(c)+';background:var(--code)"></i></div>';
}

function ranksFor(monthKey){
  /* rank map for one month, under the filters currently applied */
  const md = DATA.months[monthKey]; if(!md) return null;
  const r = md.members.filter(m=>(m.daysActive||0)>0 && !hasLeft(m.name))
    .filter(m=>rankTeam==='all'||(m.dept||'Unassigned')===rankTeam)
    .map(m=>({email:m.email, score:scoreOf(m, null, md.days||1)}))
    .sort((a,b)=>b.score-a.score);
  const out={}; r.forEach((m,i)=>out[m.email]=i+1); return out;
}
function movement(prev, email, rank){
  if(!prev) return '';
  const was = prev[email];
  if(was==null) return '<span class="mv new">new</span>';
  const d = was - rank;
  if(d===0)  return '<span class="mv flat">&ndash;</span>';
  return '<span class="mv '+(d>0?'up':'down')+'">'+(d>0?'\u25b2':'\u25bc')+Math.abs(d)+'</span>';
}

function vStandings(){
  const allTime = isAll();
  const md = allTime ? null : DATA.months[currentMonth];
  if(!allTime && !md) return '<div class="nodata">No data for this month.</div>';
  const src  = allTime ? DATA.allTime.members : md.members;
  const span = allTime ? null : (md.days||1);
  const label= allTime ? DATA.allTime.period : longMonth(currentMonth);

  const active = src.filter(m=>(m.daysActive||0)>0 && !hasLeft(m.name));
  const goneCount = src.filter(m=>(m.daysActive||0)>0 && hasLeft(m.name)).length;
  const allTeams = Array.from(new Set(active.map(m=>m.dept||'Unassigned'))).sort();
  if(rankTeam!=='all' && allTeams.indexOf(rankTeam)===-1) rankTeam='all';

  let pool = active.map(m=>Object.assign({}, m,
      allTime ? (rolledUp()[m.email]||{}) : {},
      {_pct: allTime ? (rolledUp()[m.email]||{})._pct||0 : (m.daysActive||0)/span}));
  if(rankMetric==='depth'){
    const calc = depthBreakdown(pool);
    pool.forEach(m=>{ const r = calc(m); m._depth = r.score; m._parts = r.parts; });
  }
  const shaped = pool.map(m=>Object.assign({}, m, {
      score: scoreOf(m, null, span),
      pct: Math.min(100, allTime ? (m.pctDaysUsed||0) : (m.daysActive||0)/span*100)
    }));
  const people = shaped.filter(m=>rankTeam==='all'||(m.dept||'Unassigned')===rankTeam)
                       .sort((x,y)=>y.score-x.score);

  let h='';

  if(!people.length) return h+'<div class="nodata">Nobody was active here in this period.</div>';

  const curIdx0 = isAll() ? MONTHS.length-1 : MONTHS.indexOf(currentMonth);
  const prevLabel = curIdx0>0 ? longMonth(MONTHS[curIdx0-1]) : null;

  /* ── podium ────────────────────────────────────────── */
  const isSpend = rankMetric==='spend';
  const pod=people.slice(0,3);
  h+='<div class="rank-hero"><div class="eyebrow">Rankings</div>'+
    '<h3>'+esc(allTime?'All time':label)+'</h3>'+
    '<div class="sub">'+(allTime?esc(DATA.allTime.period.replace(/\u2013|-/g,'to'))+' · ':'')+
    people.length+' people'+
    (goneCount?' · '+goneCount+(goneCount===1?' leaver':' leavers')+' excluded':'')+
    (prevLabel&&!allTime?' · movement against '+esc(prevLabel):'')+'</div>'+
    controlBar(allTeams)+
    (isSpend ? '' : '<div class="pod">'+pod.map((m,i)=>
      '<div class="p'+(i===0?' first':'')+'">'+
      '<div class="mdl">'+(i+1)+'</div>'+
      '<div class="idy"><div class="who">'+esc(m.name)+'</div>'+
      '<div class="rol">'+esc(m.title||'')+' · '+esc(m.dept||'')+'</div></div>'+
      '<div class="val">'+showVal(m.score)+'</div></div>').join('')+'</div>')+
    (rankMetric==='all'
      ? '<div class="scoring"><b>Points</b><span>1 per chat message</span><span>4 per Cowork message</span>'+
        '<span>6 per Claude Code session</span></div>'
      : rankMetric==='depth'
      ? '<div class="scoring"><b>Depth of use</b>'+
        DEPTH_CATS.map(c=>'<span>'+esc(c[0])+'</span>').join('')+
        '<span>each scored out of 100, then averaged</span></div>'
      : isSpend
      ? '<div class="scoring"><b>Showing</b><span>Metered usage above plan limits</span>'+
        '<span>'+people.length+' of '+DATA.meta.people+' people have any</span>'+
        '<span>Seat subscription not included</span></div>'
      : '<div class="scoring"><b>Ranked on</b><span>'+
        esc(METRICS.filter(x=>x[0]===rankMetric)[0][1])+' only, no weighting applied</span></div>')+
  '</div>';

  /* ── teams, always across the whole org so the table is a comparison ── */
  const teams={};
  shaped.forEach(m=>{
    const d=m.dept||'Unassigned';
    (teams[d]=teams[d]||{dept:d,n:0,score:0,chat:0,cowork:0,code:0,days:0});
    const T=teams[d];
    T.n++; T.score+=m.score; T.chat+=m.messages||0; T.cowork+=m.coworkMessages||0;
    T.code+=m.codeSessions||0; T.days+=m.pct;
  });
  const tl=Object.values(teams).map(T=>Object.assign(T,{
    per:(rankMetric==='spend'||rankMetric==='depth'? T.score/(T.n||1) : Math.round(T.score/(T.n||1))),
    consistency:T.days/(T.n||1)
  })).sort((a,b)=>b.per-a.per);

  const steady=people.slice().sort((a,b)=>b.pct-a.pct)[0];
  const curIdx = curIdx0;
  const prevRanks = curIdx>0 ? ranksFor(MONTHS[curIdx-1]) : null;
  let climber=null;
  const idx = allTime ? MONTHS.length-1 : MONTHS.indexOf(currentMonth);
  if(idx>0 && DATA.months[MONTHS[idx-1]] && DATA.months[MONTHS[idx]]){
    const ok=m=>rankTeam==='all'||(m.dept||'Unassigned')===rankTeam;
    const was={}; DATA.months[MONTHS[idx-1]].members.forEach(p=>was[p.email]=scoreOf(p));
    DATA.months[MONTHS[idx]].members.filter(ok).filter(c=>!hasLeft(c.name)).forEach(c=>{
      const b=was[c.email]; if(b==null||b<40) return;
      const now=scoreOf(c); if(now<=b) return;
      const lift=(now-b)/b; if(!climber||lift>climber.lift) climber={name:c.name,lift:lift};
    });
  }
  const initial=n=>{const p=String(n).split(' ');return p[0]+(p[1]?' '+p[1][0]:'');};

  h+='<div class="cards">'+
    card(isSpend?'Costliest team':'Leading team', esc(tl[0].dept), showVal(tl[0].per)+' per person') +
    card('Most consistent', esc(initial(steady.name)), steady.pct.toFixed(0)+'% of days active') +
    card('Biggest climber', climber?esc(initial(climber.name)):'—',
         climber?('up '+Math.round(climber.lift*100)+'% on the month before'):'not enough history') +
    (rankMetric==='depth'
      ? card('Average depth',
             (people.reduce((a,b)=>a+b.score,0)/(people.length||1)).toFixed(1),
             'of a possible 100')
      : card(isSpend?'Total spend':'Total '+unitLabel(), showVal(people.reduce((a,b)=>a+b.score,0)),
             rankTeam==='all'?'across the organisation':'in '+rankTeam)) +
  '</div>';

  h+='<div class="panel"><div class="p-title">Team standings</div><table class="st">'+
    '<thead><tr><th></th><th>Team</th><th class="r">People</th><th class="r">Per person</th>'+
    '<th style="width:30%">Where the points come from</th><th class="r">Days active</th></tr></thead><tbody>'+
    tl.map((T,i)=>'<tr'+(rankTeam===T.dept?' class="me"':'')+'><td class="rk'+(i===0?' top':'')+'">'+(i+1)+'</td>'+
      '<td><b>'+esc(T.dept)+'</b></td><td class="r">'+T.n+'</td>'+
      '<td class="r"><span class="sc">'+showVal(T.per)+'</span></td>'+
      '<td>'+mixBar({messages:T.chat,coworkMessages:T.cowork,codeSessions:T.code})+'</td>'+
      '<td class="r">'+T.consistency.toFixed(0)+'%</td></tr>').join('')+
    '</tbody></table>'+
    '<div class="p-note">Ranked per person, not by total, so a team of three is not beaten by a team of twenty. '+
    'This table always covers the whole organisation, so it stays a comparison when a team filter is on.</div></div>';

  h+='<div class="panel"><div class="p-title">Individual standings</div><table class="st">'+
    '<thead><tr><th></th><th>Name</th><th>Team</th><th class="r">'+esc(isSpend?'Spend':unitLabel().replace(/^./,c=>c.toUpperCase()))+'</th>'+
    '<th class="r">Move</th>'+
    '<th style="width:26%">Chat · Cowork · Code</th>'+
    '<th class="r">Days active</th></tr></thead><tbody>'+
    people.slice(0,15).map((m,i)=>{
      return '<tr><td class="rk'+(i<3?' top':'')+'">'+(i+1)+'</td>'+
        '<td><b>'+esc(m.name)+'</b><div class="lb-s">'+esc(m.title||'')+'</div></td>'+
        '<td>'+esc(m.dept||'')+'</td>'+
        '<td class="r"><span class="sc">'+showVal(m.score)+'</span></td>'+
        '<td class="r">'+movement(prevRanks, m.email, i+1)+'</td>'+
        '<td>'+(rankMetric==='depth'?depthBar(m):mixBar(m))+'</td>'+
        '<td class="r">'+m.pct.toFixed(0)+'%</td></tr>';
    }).join('')+'</tbody></table>'+
    (prevLabel?'<div class="p-note">Move compares this period with '+esc(prevLabel)+'.</div>':'')+'</div>';

  h+=howTo();
  return h;
}

function controlBar(teams){
  const ps=rankPeriods(), cur=isAll()?ALLTIME:currentMonth, i=ps.indexOf(cur);
  const label=p=>p===ALLTIME?'All time':longMonth(p);
  return '<div class="rk-bar">'+
    '<div class="seg">'+METRICS.map(([k,lbl])=>
      '<button class="'+(rankMetric===k?'on':'')+'" onclick="setRankMetric(\''+k+'\')">'+
      esc(lbl)+'</button>').join('')+'</div>'+
    '<div class="step">'+
      '<button onclick="stepMonth(-1)"'+(i<=0?' disabled':'')+' title="Earlier">&#8249;</button>'+
      '<select class="rk-sel" onchange="setMonth(this.value)">'+
        ps.map(p=>'<option value="'+esc(p)+'"'+(p===cur?' selected':'')+'>'+esc(label(p))+'</option>').join('')+
      '</select>'+
      '<button onclick="stepMonth(1)"'+(i>=ps.length-1?' disabled':'')+' title="Later">&#8250;</button>'+
    '</div>'+
    '<select class="rk-sel" onchange="setRankTeam(this.value)">'+
      '<option value="all"'+(rankTeam==='all'?' selected':'')+'>All teams</option>'+
      teams.map(d=>'<option value="'+esc(d)+'"'+(rankTeam===d?' selected':'')+'>'+esc(d)+'</option>').join('')+
    '</select>'+
  '</div>';
}

const DEPTH_COL=['var(--chat)','var(--cowork)','var(--code)','var(--amber)','var(--link)','var(--spend)'];
function depthBar(m){
  if(!m._parts) return '';
  return '<div class="mix" title="'+esc(m._parts.map(p=>p.name+' '+p.pct.toFixed(0)).join(' · '))+
    '">'+m._parts.map((p,i)=>'<i style="width:'+(p.pct/DEPTH_CATS.length).toFixed(1)+'%;background:'+
    DEPTH_COL[i%DEPTH_COL.length]+'"></i>').join('')+'</div>';
}
