const {useEffect,useMemo,useState} = React;
const h = React.createElement;

const RISK = {NORMAL:'#1fa971', REVIEW:'#e5b84b', HIGH:'#ee8b32', CRITICAL:'#d94b4b'};
const fmt = n => n == null || Number.isNaN(Number(n)) ? 'Data Not Available' : Number(n).toLocaleString('en-IN',{maximumFractionDigits:2});
const cr = n => n == null || Number.isNaN(Number(n)) ? 'Data Not Available' : `₹${(Number(n)/1e7).toLocaleString('en-IN',{maximumFractionDigits:2})} Cr`;
const pct = n => n == null || Number.isNaN(Number(n)) ? 'Data Not Available' : `${Number(n).toFixed(1)}%`;
const api = async (path) => { const r=await fetch(path); if(!r.ok) throw new Error(await r.text()); return r.json(); };
const esc = s => s==null ? 'Data Not Available' : String(s);
function go(path){ location.hash=path; }
function useRoute(){ const [route,setRoute]=useState(location.hash.slice(1)||'/'); useEffect(()=>{const f=()=>setRoute(location.hash.slice(1)||'/'); addEventListener('hashchange',f); return()=>removeEventListener('hashchange',f)},[]); return route; }

function Badge({level}){return h('span',{className:'badge',style:{color:RISK[level]||'#9aa8b8',borderColor:(RISK[level]||'#596579')+'66',background:(RISK[level]||'#596579')+'14'}},level||'Data Not Available')}
function Card({children,className=''}){return h('div',{className:'card '+className},children)}
function Metric({label,value,tone}){return h(Card,{className:'metric'},h('div',{className:'metric-label'},label),h('div',{className:'metric-value',style:tone?{color:tone}:{}},value))}
function Breadcrumbs({items}){return h('div',{className:'breadcrumbs'},items.map((x,i)=>h(React.Fragment,{key:i},i?h('span',null,'›'):null,h('button',{onClick:()=>go(x.path)},x.label))))}

function Layout({route,children}){
 const [summary,setSummary]=useState(null), [chamber,setChamber]=useState('All');
 useEffect(()=>{api('/api/summary?chamber='+encodeURIComponent(chamber)).then(setSummary).catch(()=>{})},[chamber]);
 const nav=[['/','Command Center','⌂'],['/chamber/lok-sabha','Lok Sabha','▦'],['/chamber/rajya-sabha','Rajya Sabha','▦'],['/critical','Critical Cases','!'],['/risk-explorer','Risk Explorer','⌕'],['/outliers','Spending Outliers','◈']];
 const aside=h('aside',{className:'sidebar'},
   h('div',{className:'brand'},h('div',{className:'brand-mark'},'M'),h('div',null,h('strong',null,'MPLADS'),h('small',null,'AI AUDIT INTELLIGENCE'))),
   h('div',{className:'nav-title'},'AUDIT CONSOLE'),
   nav.map(([p,l,ic])=>h('button',{key:p,className:'nav-item '+((route===p||route.startsWith(p+'/'))?'active':''),onClick:()=>go(p)},h('span',{className:'nav-icon'},ic),l)),
   h('div',{className:'nav-title'},'SYSTEM'),
   h('button',{className:'nav-item',onClick:()=>go('/methodology')},h('span',{className:'nav-icon'},'◉'),'Methodology'),
   h('div',{className:'sidebar-foot'},'PS SIH26102','Audit-support tool — human verification required.')
 );
 const header=h('header',{className:'topbar'},
   h('div',null,h('div',{className:'eyebrow'},'GOVERNMENT AUDIT INTELLIGENCE'),h('h1',null,'MPLADS AI AUDIT INTELLIGENCE'),h('p',null,'AI-Powered MPLADS Audit & Risk Intelligence')),
   h('div',{className:'top-actions'},h('span',{className:'status-dot'},'● SYSTEM ACTIVE'),h('select',{value:chamber,onChange:e=>setChamber(e.target.value)},h('option',null,'All India'),h('option',null,'Lok Sabha'),h('option',null,'Rajya Sabha')))
 );
 const strip=summary&&h('div',{className:'global-strip'},h('span',null,`${fmt(summary.total_works)} works screened`),h('span',null,`${fmt(summary.risk.CRITICAL)} critical`),h('span',null,`${fmt(summary.risk.HIGH)} high`),h('span',null,'Classification ≠ fraud finding'));
 return h('div',{className:'shell'},aside,h('main',{className:'main'},header,strip,h('div',{className:'content'},children)));
}

const CODE_MAP={'Jammu And Kashmir':'JK','Ladakh':'LA','Himachal Pradesh':'HP','Punjab':'PB','Uttarakhand':'UK','Haryana':'HR','Delhi':'DL','Rajasthan':'RJ','Uttar Pradesh':'UP','Sikkim':'SK','Arunachal Pradesh':'AR','Assam':'AS','Nagaland':'NL','Meghalaya':'ML','Bihar':'BR','Jharkhand':'JH','West Bengal':'WB','Tripura':'TR','Mizoram':'MZ','Madhya Pradesh':'MP','Gujarat':'GJ','Daman And Diu':'DN','Dadra And Nagar Haveli':'DN','Chhattisgarh':'CT','Odisha':'OR','Maharashtra':'MH','Telangana':'TG','Goa':'GA','Karnataka':'KA','Andhra Pradesh':'AP','Kerala':'KL','Tamil Nadu':'TN','Puducherry':'PY','Andaman And Nicobar Islands':'AN','Lakshadweep':'LD','Chandigarh':'CH'};
function codeFor(state){return CODE_MAP[state]||''}

function IndiaMap({states}){
 const [tip,setTip]=useState(null);
 const byCode=useMemo(()=>{const m={}; (states||[]).forEach(s=>m[codeFor(s.state)] = s); return m},[states]);
 function attach(e){const doc=e.target.contentDocument; if(!doc)return; doc.querySelectorAll('[data-state]').forEach(el=>{const code=el.getAttribute('data-state'); const s=byCode[code]; el.style.fill=s?(s.critical?RISK.CRITICAL:s.high_risk?RISK.HIGH:'#245b57'):'#1c3346'; el.style.stroke='#0a1420'; el.style.strokeWidth='1.2'; el.style.cursor=s?'pointer':'default'; el.onmouseenter=ev=>{if(s){setTip({x:ev.clientX,y:ev.clientY,state:s})}}; el.onmousemove=ev=>{if(s)setTip(t=>t?{...t,x:ev.clientX,y:ev.clientY,state:s}:t)}; el.onmouseleave=()=>setTip(null); el.onclick=()=>{if(s)go('/state/'+encodeURIComponent(s.state_display))}; }); }
 return h('div',{className:'map-wrap'},h('object',{data:'/maps/india-states.svg',type:'image/svg+xml',className:'india-svg',onLoad:attach}),tip&&h('div',{className:'map-tip',style:{left:Math.min(tip.x+14,window.innerWidth-270),top:Math.min(tip.y+14,window.innerHeight-150)}},h('strong',null,tip.state.state_display),h('span',null,`${fmt(tip.state.total_works)} total works`),h('span',null,`${fmt(tip.state.high_risk)} high-risk`),h('span',null,`${fmt(tip.state.critical)} critical`)))
}
function RiskDonut({risk}){const total=Object.values(risk).reduce((a,b)=>a+b,0); let acc=0; const stops=Object.entries(RISK).map(([k,c])=>{const a=acc; acc+=((risk[k]||0)/total)*360; return `${c} ${a}deg ${acc}deg`}).join(','); return h('div',{className:'donut-box'},h('div',{className:'donut',style:{background:`conic-gradient(${stops})`}},h('div',{className:'donut-hole'},h('strong',null,fmt(total)),h('span',null,'Total'))),h('div',{className:'legend'},Object.entries(RISK).map(([k,c])=>h('div',{key:k},h('i',{style:{background:c}}),k,h('b',null,fmt(risk[k]||0))))) )}
function BarList({items,valueKey='value',labelKey='label',money=false}){
 const max=Math.max(...items.map(x=>Number(x[valueKey])||0),1);
 return h('div',{className:'bars'},items.map((x,i)=>
   h('div',{className:'bar-row',key:i},
     h('div',{className:'bar-head'},h('span',null,esc(x[labelKey])),h('b',null,money?cr(x[valueKey]):fmt(x[valueKey]))),
     h('div',{className:'bar-track'},h('div',{className:'bar-fill',style:{width:`${Math.max(3,(Number(x[valueKey])||0)/max*100)}%`}}))
   )
 ));
}

function Loading(){return h('div',{className:'loading'},'Loading audit data…')}
function ErrorBox({e}){return h(Card,{className:'error'},h('strong',null,'Data service error'),h('p',null,String(e&&e.message||e)),h('small',null,'Start the FastAPI server from the project root: uvicorn backend.api:app --reload'))}

function Home(){
 const [data,setData]=useState(null),[states,setStates]=useState([]),[err,setErr]=useState(null);
 useEffect(()=>{Promise.all([api('/api/summary'),api('/api/states')]).then(([a,b])=>{setData(a);setStates(b)}).catch(setErr)},[]);
 if(err)return h(ErrorBox,{e:err}); if(!data)return h(Loading);
 const top=states.slice().sort((a,b)=>b.expenditure-a.expenditure).slice(0,6);
 const hero=h('section',{className:'hero'},
   h('div',null,h('div',{className:'eyebrow'},'MPLADS AI AUDIT INTELLIGENCE'),h('h2',null,'Screen. Prioritize. Verify.'),h('p',null,'A government-grade audit screening layer over the existing MPLADS anomaly pipeline. It surfaces potential risk signals for human audit verification — it does not establish fraud.')),
   h('div',{className:'hero-badge'},'PS SIH26102'),
   h('div',{className:'hero-actions'},h('button',{className:'primary',onClick:()=>go('/risk-explorer')},'Open Risk Explorer'),h('button',{className:'secondary',onClick:()=>go('/critical')},'Review Critical Cases'))
 );
 const metrics=h('div',{className:'metrics-grid'},
   h(Metric,{label:'Total Works',value:fmt(data.total_works)}),h(Metric,{label:'Normal',value:fmt(data.risk.NORMAL),tone:RISK.NORMAL}),h(Metric,{label:'Review',value:fmt(data.risk.REVIEW),tone:RISK.REVIEW}),h(Metric,{label:'High',value:fmt(data.risk.HIGH),tone:RISK.HIGH}),h(Metric,{label:'Critical',value:fmt(data.risk.CRITICAL),tone:RISK.CRITICAL}),h(Metric,{label:'Total Expenditure',value:cr(data.money.expenditure)})
 );
 const mapCard=h(Card,null,h('div',{className:'card-title'},h('div',null,h('h3',null,'India Risk Distribution'),h('span',null,'Hover a state. Click to drill down.')),h('span',{className:'pill'},'REAL DATA')),h(IndiaMap,{states}),h('div',{className:'map-note'},'State statistics are aggregated from anomaly_results.csv. The SVG is used for dashboard navigation, not legal boundary determination.'));
 const riskCard=h(Card,null,h('div',{className:'card-title'},h('div',null,h('h3',null,'Risk Level Distribution'),h('span',null,'Current pipeline output')),h('span',{className:'pill'},'64,193 SCREENED')),h(RiskDonut,{risk:data.risk}),h('div',{className:'quick-grid'},
   h('button',{onClick:()=>go('/critical')},h('b',null,'Critical Works'),h('span',null,fmt(data.risk.CRITICAL)+' cases')),
   h('button',{onClick:()=>go('/risk-explorer?risk=HIGH')},h('b',null,'High-Risk Works'),h('span',null,fmt(data.risk.HIGH)+' cases')),
   h('button',{onClick:()=>go('/outliers')},h('b',null,'Spending Outliers'),h('span',null,'Statistical ranking'))
 ));
 const insights=h('div',{className:'grid-2'},
   h(Card,null,h('div',{className:'card-title'},h('div',null,h('h3',null,'Top States by Expenditure'),h('span',null,'Aggregated from backend output'))),h(BarList,{items:top.map(x=>({label:x.state_display,value:x.expenditure})),money:true})),
   h(Card,null,h('div',{className:'card-title'},h('div',null,h('h3',null,'Audit Safeguard'),h('span',null,'How to interpret risk'))),h('div',{className:'safeguard'},
     h('div',null,h('b',null,'Potential signal'),h('span',null,'The pipeline prioritizes records using deterministic rules, statistical evidence and ML supporting signal.')),
     h('div',null,h('b',null,'Human verification'),h('span',null,'High / Critical cases require audit review. They are not confirmed fraud findings.')),
     h('div',null,h('b',null,'Risk weights'),h('span',null,'50% Rule Score · 30% ML Anomaly Percentile · 20% Statistical Risk Score.'))
   ))
 );
 return h('div',null,Breadcrumbs({items:[{label:'Home',path:'/'}]}),hero,metrics,h('div',{className:'grid-2'},mapCard,riskCard),insights);
}

function ChamberPage({chamber}){const [data,setData]=useState(null),[filters,setFilters]=useState(null),[q,setQ]=useState(''); useEffect(()=>{Promise.all([api('/api/summary?chamber='+encodeURIComponent(chamber)),api('/api/filters?chamber='+encodeURIComponent(chamber))]).then(([a,b])=>{setData(a);setFilters(b)})},[chamber]); if(!data||!filters)return h(Loading); return h('div',null,Breadcrumbs({items:[{label:'Home',path:'/'},{label:chamber,path:'/chamber/'+(chamber==='Lok Sabha'?'lok-sabha':'rajya-sabha')}]}),h('div',{className:'page-head'},h('div',null,h('div',{className:'eyebrow'},'PARLIAMENTARY CHAMBER'),h('h2',null,chamber),h('p',null,chamber==='Rajya Sabha'?'No constituency is fabricated. Nodal/assigned district is shown only if present in the source data.':'State, constituency and district filters are driven by the actual output schema.')),h('button',{className:'secondary',onClick:()=>go('/risk-explorer')},'Explore all works')),
 h('div',{className:'metrics-grid'},h(Metric,{label:'Total Works',value:fmt(data.total_works)}),h(Metric,{label:'Normal',value:fmt(data.risk.NORMAL),tone:RISK.NORMAL}),h(Metric,{label:'Review',value:fmt(data.risk.REVIEW),tone:RISK.REVIEW}),h(Metric,{label:'High',value:fmt(data.risk.HIGH),tone:RISK.HIGH}),h(Metric,{label:'Critical',value:fmt(data.risk.CRITICAL),tone:RISK.CRITICAL}),h(Metric,{label:'Expenditure',value:cr(data.money.expenditure)})),
 h(Card,null,h('div',{className:'filterbar'},h('select',null,h('option',null,'All States'),filters.states.map(s=>h('option',{key:s},s))),chamber==='Lok Sabha'&&h('select',null,h('option',null,'All Constituencies'),filters.constituencies.map(s=>h('option',{key:s},s))),chamber==='Rajya Sabha'&&h('div',{className:'field-note'},'Assigned / Nodal District: Data Not Available'),h('input',{value:q,onChange:e=>setQ(e.target.value),placeholder:chamber==='Lok Sabha'?'Search by MP Name or Constituency…':'Search by MP Name or Nodal District…'}),h('button',{className:'primary',onClick:()=>go('/risk-explorer?q='+encodeURIComponent(q))},'Search'))),
 h(Card,null,h('div',{className:'card-title'},h('div',null,h('h3',null,'Audit posture'),h('span',null,'Use Risk Explorer for server-side pagination across the full dataset.'))),h('div',{className:'three-col'},h('div',{className:'info-box'},h('b',null,'Normal'),h('span',null,fmt(data.risk.NORMAL)+' works')),h('div',{className:'info-box'},h('b',null,'High / Critical'),h('span',null,fmt(data.risk.HIGH+data.risk.CRITICAL)+' prioritized cases')),h('div',{className:'info-box'},h('b',null,'Data discipline'),h('span',null,'Missing fields remain Data Not Available')))));
}

function StatePage({name}){const [d,setD]=useState(null),[err,setErr]=useState(null); useEffect(()=>api('/api/state/'+encodeURIComponent(name)).then(setD).catch(setErr),[name]); if(err)return h(ErrorBox,{e:err}); if(!d)return h(Loading); if(!d.found)return h(Card,null,'State not found in current dataset.'); return h('div',null,Breadcrumbs({items:[{label:'Home',path:'/'},{label:d.state,path:'/state/'+encodeURIComponent(d.state)}]}),h('div',{className:'page-head'},h('div',null,h('div',{className:'eyebrow'},'STATE AUDIT VIEW'),h('h2',null,d.state),h('p',null,'Aggregated from the existing anomaly pipeline.')),h(Badge,{level:d.summary.critical?'CRITICAL':'NORMAL'})),h('div',{className:'metrics-grid'},h(Metric,{label:'Total Works',value:fmt(d.summary.total_works)}),h(Metric,{label:'Normal',value:fmt(d.summary.NORMAL),tone:RISK.NORMAL}),h(Metric,{label:'Review',value:fmt(d.summary.REVIEW),tone:RISK.REVIEW}),h(Metric,{label:'High',value:fmt(d.summary.HIGH),tone:RISK.HIGH}),h(Metric,{label:'Critical',value:fmt(d.summary.CRITICAL),tone:RISK.CRITICAL}),h(Metric,{label:'Expenditure',value:cr(d.summary.expenditure)})),h('div',{className:'grid-2'},h(Card,null,h('div',{className:'card-title'},h('div',null,h('h3',null,'Risk Distribution')),h('span',{className:'pill'},'STATE')),h(RiskDonut,{risk:{NORMAL:d.summary.NORMAL,REVIEW:d.summary.REVIEW,HIGH:d.summary.HIGH,CRITICAL:d.summary.CRITICAL}})),h(Card,null,h('div',{className:'card-title'},h('div',null,h('h3',null,'MP Risk Concentration'),h('span',null,'Top 50 by high/critical workload'))),h(BarList,{items:d.mps.slice(0,8).map(x=>({label:x.mp_name,value:x.critical*5+x.high})),valueKey:'value'}))),h(Card,null,h('div',{className:'card-title'},h('div',null,h('h3',null,'MPs')),h('span',{className:'pill'},fmt(d.mps.length)+' shown')),h(Table,{columns:['mp_name','chamber','constituency','works','high','critical'],rows:d.mps,rowClick:r=>go('/mp/'+r.mp_id),render:{constituency:r=>r.constituency||'Data Not Available',mp_name:r=>r.mp_name}})),h(Card,null,h('div',{className:'card-title'},h('div',null,h('h3',null,'High & Critical Works')),h('span',{className:'pill'},'PRIORITIZED')),h(WorkTable,{rows:[...d.critical_works,...d.high_works]})));
}

function Table({columns,rows,rowClick,render={}}){return h('div',{className:'table-scroll'},h('table',null,h('thead',null,h('tr',null,columns.map(c=>h('th',{key:c},c.replaceAll('_',' '))))),h('tbody',null,rows.map((r,i)=>h('tr',{key:i,onClick:()=>rowClick&&rowClick(r),className:rowClick?'clickable':''},columns.map(c=>h('td',{key:c},render[c]?render[c](r):esc(r[c]))))))));}
function WorkTable({rows}){return h(Table,{columns:['work_id','mp_name','state','risk_score','risk_level','primary_reason'],rows,rowClick:r=>go('/work/'+encodeURIComponent(r.work_id)),render:{risk_level:r=>h(Badge,{level:r.risk_level}),risk_score:r=>Number(r.risk_score||0).toFixed(1),primary_reason:r=>h('span',{className:'truncate'},r.primary_reason||'Data Not Available')}})}

function MpPage({id}){const [d,setD]=useState(null);useEffect(()=>api('/api/mp/'+id).then(setD),[id]);if(!d)return h(Loading);if(!d.found)return h(Card,null,'MP profile not found.');return h('div',null,Breadcrumbs({items:[{label:'Home',path:'/'},{label:d.profile.chamber,path:'/chamber/'+(d.profile.chamber==='Lok Sabha'?'lok-sabha':'rajya-sabha')},{label:d.profile.mp_name,path:'/mp/'+id}]}),h(Card,{className:'profile-head'},h('div',{className:'avatar'},d.profile.mp_name.split(/\s+/).map(x=>x[0]).slice(0,2).join('')),h('div',{className:'profile-main'},h('div',{className:'eyebrow'},d.profile.chamber),h('h2',null,d.profile.mp_name),h('p',null,`${d.profile.state} · ${d.profile.chamber==='Lok Sabha'?(d.profile.constituency||'Data Not Available'):'Assigned / Nodal District: Data Not Available'}`),h('small',null,'Photo source not present in uploaded data — initials placeholder used.'))),h('div',{className:'metrics-grid'},h(Metric,{label:'Total Works',value:fmt(d.summary.total_works)}),h(Metric,{label:'Expenditure',value:cr(d.summary.total_expenditure)}),h(Metric,{label:'High Risk',value:fmt(d.summary.high),tone:RISK.HIGH}),h(Metric,{label:'Critical',value:fmt(d.summary.critical),tone:RISK.CRITICAL})),h('div',{className:'grid-2'},h(Card,null,h('div',{className:'card-title'},h('div',null,h('h3',null,'Risk Distribution')),h('span',{className:'pill'},'PROFILE')),h(RiskDonut,{risk:{NORMAL:d.summary.normal,REVIEW:d.summary.review,HIGH:d.summary.high,CRITICAL:d.summary.critical}})),h(Card,null,h('div',{className:'card-title'},h('div',null,h('h3',null,'Work Status / Lifecycle'),h('span',null,'Actual lifecycle_status values'))),h(BarList,{items:Object.entries(d.lifecycle).map(([label,value])=>({label,value}))}))),h(Card,null,h('div',{className:'card-title'},h('div',null,h('h3',null,'High & Critical Works')),h('span',{className:'pill'},'AUDIT QUEUE')),h(WorkTable,{rows:d.works})));
}

function WorkPage({id}){
 const [d,setD]=useState(null); useEffect(()=>api('/api/work/'+id).then(setD),[id]);
 if(!d)return h(Loading); if(!d.found)return h(Card,null,'Work not found.'); const w=d.work;
 const financial=h(Card,null,h('div',{className:'card-title'},h('div',null,h('h3',null,'Work & Financials'))),h('div',{className:'detail-grid'},[
   ['MP',w.mp_name],['State',w.state_display],['Constituency / District',w.constituency||'Data Not Available'],['Category',w.work_category],['Sanctioned Amount',cr(w.sanctioned_amount)],['Total Expenditure',cr(w.total_expenditure)],['Completion Amount',cr(w.completion_amount)],['Work Status',w.work_status_raw||'Data Not Available']
 ].map(([a,b])=>h('div',{key:a},h('span',null,a),h('b',null,esc(b))))),h('div',{className:'lifecycle'},[
   ['Recommendation',w.recommended_date],['Sanction',w.sanction_date],['Expenditure',w.first_payment_date],['Completion',w.completion_date]
 ].map(([a,b],i)=>h('div',{key:a},h('span',{className:'life-dot'},i+1),h('b',null,a),h('small',null,b||'Data Not Available'),i<3&&h('i',null,'→')))));
 const evidence=h(Card,null,h('div',{className:'card-title'},h('div',null,h('h3',null,'Audit Evidence'),h('span',null,'Deterministic + statistical + ML supporting signals')),h('div',{className:'evidence-block'},
   h('h4',null,'DETERMINISTIC RULE SIGNALS'),(d.evidence.deterministic||[]).map((x,i)=>h('div',{className:'evidence',key:i},'• ',x)),
   h('h4',null,'STATISTICAL SIGNAL'),h('div',{className:'evidence'},`Statistical Risk Score: ${esc(d.evidence.statistical.stat_risk_score)} · Sanction robust Z-score: ${esc(d.evidence.statistical.sanc_robust_zscore)} · Expenditure robust Z-score: ${esc(d.evidence.statistical.exp_robust_zscore)}`),
   h('h4',null,'ML SUPPORTING SIGNAL'),h('div',{className:'evidence'},`ML anomaly score: ${esc(d.evidence.ml.ml_anomaly_score)} · percentile: ${pct(d.evidence.ml.ml_anomaly_percentile)}`),
   h('div',{className:'human-check'},h('strong',null,'REQUIRES HUMAN AUDIT VERIFICATION'),h('span',null,'This classification indicates potential audit-risk signals. It does not establish fraud.'))
 )));
 const payments=h(Card,null,h('div',{className:'card-title'},h('div',null,h('h3',null,'Payment Information'),h('span',null,fmt(d.payments.length)+' records'))),h('div',{className:'payment-grid'},[
   ['Payment Count',w.payment_count],['Vendor Count',w.vendor_count],['Duplicate Payment Indicators',w.duplicate_payment_count],['Vendor Concentration Score',w.vendor_concentration_score]
 ].map(([a,b])=>h('div',{key:a},h('span',null,a),h('b',null,esc(b))))),d.payments.length?h(Table,{columns:['expenditure_id','expenditure_date','vendor_name','payment_status','amount'],rows:d.payments}):h('div',{className:'empty'},'No expenditure records linked to this work.'));
 return h('div',null,
   Breadcrumbs({items:[{label:'Home',path:'/'},{label:w.parliament_house,path:'/chamber/'+(w.parliament_house==='Lok Sabha'?'lok-sabha':'rajya-sabha')},{label:w.state_display,path:'/state/'+encodeURIComponent(w.state_display)},{label:'Work Details',path:'/work/'+id}]}),
   h('div',{className:'page-head'},h('div',null,h('div',{className:'eyebrow'},'DETAILED AUDIT EVIDENCE'),h('h2',null,w.work_id),h('p',null,w.work_description||'Data Not Available')),h(Badge,{level:w.risk_level})),
   h('div',{className:'metrics-grid'},h(Metric,{label:'Risk Score',value:Number(w.risk_score||0).toFixed(1),tone:RISK[w.risk_level]}),h(Metric,{label:'Rule Score',value:Number(w.rule_score||0).toFixed(1)}),h(Metric,{label:'Statistical Risk',value:Number(w.stat_risk_score||0).toFixed(1)}),h(Metric,{label:'ML Percentile',value:pct(w.ml_anomaly_percentile)})),
   h('div',{className:'grid-2'},financial,evidence),payments
 );
}

function CriticalPage(){const [d,setD]=useState(null),[q,setQ]=useState(''),[page,setPage]=useState(1);useEffect(()=>{api('/api/critical?page='+page+'&page_size=20&q='+encodeURIComponent(q)).then(setD)},[page,q]);if(!d)return h(Loading);return h('div',null,Breadcrumbs({items:[{label:'Home',path:'/'},{label:'Critical Cases',path:'/critical'}]}),h('div',{className:'page-head'},h('div',null,h('div',{className:'eyebrow'},'PRIORITY AUDIT QUEUE'),h('h2',null,'Critical Cases'),h('p',null,'Current backend classification contains 28 CRITICAL works.')),h('div',{className:'critical-count'},fmt(d.total))),h(Card,null,h('div',{className:'filterbar'},h('input',{value:q,onChange:e=>{setPage(1);setQ(e.target.value)},placeholder:'Search Work ID or MP Name…'})),h(WorkTable,{rows:d.rows}),h('div',{className:'pager'},h('button',{disabled:page<=1,onClick:()=>setPage(page-1)},'Previous'),h('span',null,`Page ${page} · ${d.total} critical`),h('button',{disabled:page*d.page_size>=d.total,onClick:()=>setPage(page+1)},'Next'))));}

function Explorer(){const params=new URLSearchParams(location.hash.split('?')[1]||'');const [d,setD]=useState(null),[page,setPage]=useState(1),[q,setQ]=useState(params.get('q')||''),[risk,setRisk]=useState(params.get('risk')||'All'),[state,setState]=useState('All'),[filters,setFilters]=useState(null);useEffect(()=>{api('/api/filters').then(setFilters)},[]);useEffect(()=>{const u=new URLSearchParams({page,page_size:40,q,risk,state});api('/api/works?'+u).then(setD)},[page,q,risk,state]);if(!d||!filters)return h(Loading);return h('div',null,Breadcrumbs({items:[{label:'Home',path:'/'},{label:'Risk Explorer',path:'/risk-explorer'}]}),h('div',{className:'page-head'},h('div',null,h('div',{className:'eyebrow'},'64,193-WORK EXPLORER'),h('h2',null,'Risk Explorer'),h('p',null,'Server-side pagination keeps the full dataset out of the browser DOM.')),h('div',{className:'pill'},`${fmt(d.total)} matches`)),h(Card,null,h('div',{className:'filterbar'},h('input',{value:q,onChange:e=>{setPage(1);setQ(e.target.value)},placeholder:'Search Work ID or MP Name…'}),h('select',{value:state,onChange:e=>{setPage(1);setState(e.target.value)}},h('option',null,'All States'),filters.states.map(s=>h('option',{key:s},s))),h('select',{value:risk,onChange:e=>{setPage(1);setRisk(e.target.value)}},h('option',null,'All Risk Levels'),filters.risk_levels.map(s=>h('option',{key:s},s))),h('span',{className:'score-range'},`Score ${filters.score_min.toFixed(1)}–${filters.score_max.toFixed(1)}`)),h(Table,{columns:['work_id','mp_name','state','risk_score','risk_level','primary_reason'],rows:d.rows,rowClick:r=>go('/work/'+encodeURIComponent(r.work_id)),render:{risk_level:r=>h(Badge,{level:r.risk_level}),risk_score:r=>Number(r.risk_score||0).toFixed(1),primary_reason:r=>h('span',{className:'truncate'},r.primary_reason||'Data Not Available')}}),h('div',{className:'pager'},h('button',{disabled:page<=1,onClick:()=>setPage(page-1)},'Previous'),h('span',null,`Page ${page} · ${fmt(d.total)} matches`),h('button',{disabled:page*d.page_size>=d.total,onClick:()=>setPage(page+1)},'Next'))));}

function Outliers(){
 const [d,setD]=useState(null); useEffect(()=>api('/api/quick/spending-outliers?limit=30').then(setD),[]); if(!d)return h(Loading);
 const rows=d.rows.map(x=>({...x,primary_reason:(x.primary_reason||'Data Not Available')+' · |z|='+Number(x.abs_exp_robust_zscore||0).toFixed(2)}));
 return h('div',null,Breadcrumbs({items:[{label:'Home',path:'/'},{label:'Spending Outliers',path:'/outliers'}]}),
   h('div',{className:'page-head'},h('div',null,h('div',{className:'eyebrow'},'STATISTICAL SCREEN'),h('h2',null,'Spending Outliers'),h('p',null,d.method+'.')),h('span',{className:'pill'},'BACKEND DATA')),
   h(Card,null,h('div',{className:'card-title'},h('div',null,h('h3',null,'Highest Absolute Expenditure Robust Z-scores'),h('span',null,'Ranking only; not a fraud conclusion.'))),h(WorkTable,{rows}))
 );
}

function Methodology(){return h('div',null,Breadcrumbs({items:[{label:'Home',path:'/'},{label:'Methodology',path:'/methodology'}]}),h('div',{className:'page-head'},h('div',null,h('div',{className:'eyebrow'},'SOURCE-OF-TRUTH PIPELINE'),h('h2',null,'Methodology & Audit Guardrails'),h('p',null,'The frontend does not implement or alter anomaly detection logic. It reads the verified pipeline outputs.'))),h('div',{className:'grid-2'},h(Card,null,h('h3',null,'Risk Score Composition'),h('div',{className:'weight-list'},h('div',null,h('b',null,'50%'),h('span',null,'Rule Score')),h('div',null,h('b',null,'30%'),h('span',null,'ML Anomaly Percentile')),h('div',null,h('b',null,'20%'),h('span',null,'Statistical Risk Score')))),h(Card,null,h('h3',null,'Audit-safe terminology'),h('ul',{className:'clean-list'},['Potential Duplicate Payment','Vendor Concentration Risk','Peer Statistical Outlier','Lifecycle Gap / Data Quality Issue','ML Supporting Signal','Requires Human Audit Verification'].map(x=>h('li',{key:x},x))),h('div',{className:'human-check'},'Never present a risk classification as confirmed fraud.'))));}

function App(){const route=useRoute();let page;if(route==='/')page=h(Home);else if(route==='/critical')page=h(CriticalPage);else if(route.startsWith('/risk-explorer'))page=h(Explorer);else if(route==='/outliers')page=h(Outliers);else if(route==='/methodology')page=h(Methodology);else if(route.startsWith('/state/'))page=h(StatePage,{name:decodeURIComponent(route.split('/state/')[1])});else if(route.startsWith('/mp/'))page=h(MpPage,{id:route.split('/mp/')[1]});else if(route.startsWith('/work/'))page=h(WorkPage,{id:decodeURIComponent(route.split('/work/')[1])});else if(route==='/chamber/lok-sabha')page=h(ChamberPage,{chamber:'Lok Sabha'});else if(route==='/chamber/rajya-sabha')page=h(ChamberPage,{chamber:'Rajya Sabha'});else page=h(Home);return h(Layout,{route},page)}
ReactDOM.render(h(App),document.getElementById('root'));
