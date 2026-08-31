import React from 'react';
import ReactDOM from 'react-dom';
globalThis.React = React;
globalThis.ReactDOM = ReactDOM;
const {useEffect,useMemo,useState} = React;
const h = React.createElement;

const APP_CSS = `
:root{
  --bg:#071522;--bg2:#0a1b2b;--panel:#0d2133;--panel2:#10283d;--line:#20384c;
  --text:#e7eef5;--muted:#8fa1b4;--muted2:#667c90;--accent:#42b6a4;
  --green:#1fa971;--yellow:#e5b84b;--orange:#ee8b32;--red:#d94b4b;
  --shadow:0 16px 45px rgba(0,0,0,.24);
}
*{box-sizing:border-box}
html,body,#root{margin:0;min-height:100%;width:100%;font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:var(--bg);color:var(--text)}
body{overflow-x:hidden}
button,input,select{font:inherit}
button{color:inherit}
.shell{display:flex;min-height:100vh;background:radial-gradient(circle at 70% 5%,rgba(34,82,111,.16),transparent 35%),var(--bg)}
.sidebar{position:fixed;inset:0 auto 0 0;width:238px;background:#081725;border-right:1px solid #1c3448;padding:24px 14px;display:flex;flex-direction:column;z-index:10}
.brand{display:flex;align-items:center;gap:11px;padding:3px 10px 26px}.brand-mark{width:34px;height:34px;border-radius:9px;background:#17384d;border:1px solid #2d5870;display:grid;place-items:center;font-weight:800;color:#69d1bd}.brand strong{display:block;font-size:14px;letter-spacing:1.4px}.brand small{display:block;color:#71879b;font-size:8px;letter-spacing:1.2px;margin-top:2px}
.nav-title{font-size:9px;color:#60778b;letter-spacing:1.8px;font-weight:700;padding:12px 12px 7px}.nav-item{width:100%;border:0;background:transparent;border-radius:7px;text-align:left;padding:11px 12px;color:#91a3b5;cursor:pointer;display:flex;align-items:center;gap:11px;margin:2px 0;font-size:12px}.nav-item:hover{background:#0e2639;color:#d9e5ed}.nav-item.active{background:#123047;color:#eaf5f7;box-shadow:inset 2px 0 0 var(--accent)}.nav-icon{width:18px;text-align:center;color:#7691a6}.nav-item.active .nav-icon{color:#63cbbb}.sidebar-foot{margin-top:auto;padding:14px 11px;color:#62798c;font-size:9px;line-height:1.7;border-top:1px solid #173047}
.main{margin-left:238px;width:calc(100% - 238px);min-width:0}.topbar{min-height:92px;padding:20px 28px 16px;border-bottom:1px solid #1b3448;display:flex;align-items:center;justify-content:space-between;background:rgba(7,21,34,.88);backdrop-filter:blur(10px)}.eyebrow{font-size:9px;letter-spacing:1.8px;color:#6d879b;font-weight:700}.topbar h1{margin:4px 0 1px;font-size:18px;letter-spacing:.4px}.topbar p{margin:0;color:#71879a;font-size:10px}.top-actions{display:flex;align-items:center;gap:16px}.status-dot{font-size:9px;color:#55c7a7;letter-spacing:.8px}.top-actions select{background:#0b1e2f;color:#d8e3ea;border:1px solid #28445a;border-radius:6px;padding:7px 28px 7px 9px;outline:none;font-size:10px}
.global-strip{height:34px;border-bottom:1px solid #1b3448;background:#091b2a;padding:0 28px;display:flex;align-items:center;gap:24px;color:#8195a7;font-size:9px}.global-strip span:not(:last-child){padding-right:24px;border-right:1px solid #21394d}.content{padding:20px 28px 42px;max-width:1500px;margin:auto}.breadcrumbs{display:flex;align-items:center;gap:7px;margin-bottom:14px;color:#72879a;font-size:10px}.breadcrumbs button{background:none;border:0;color:#8498aa;padding:0;cursor:pointer}.breadcrumbs button:hover{color:#d9e8ee}
.hero{position:relative;overflow:hidden;border:1px solid #214158;background:linear-gradient(110deg,#0d2639,#0a1d2d 65%,#0b2032);border-radius:9px;padding:25px 26px;box-shadow:var(--shadow);margin-bottom:15px}.hero:after{content:"";position:absolute;width:300px;height:300px;right:-100px;top:-180px;border-radius:50%;border:1px solid rgba(65,182,164,.14);box-shadow:0 0 0 35px rgba(65,182,164,.025),0 0 0 70px rgba(65,182,164,.02)}.hero h2{font-size:25px;margin:5px 0 6px;letter-spacing:-.5px}.hero p{max-width:760px;color:#90a5b7;font-size:11px;line-height:1.7;margin:0}.hero-badge{position:absolute;right:24px;top:22px;border:1px solid #355267;border-radius:5px;color:#71899b;padding:5px 8px;font-size:8px;letter-spacing:1px}.hero-actions{display:flex;gap:8px;margin-top:18px}.primary,.secondary{border-radius:6px;padding:9px 13px;font-size:10px;cursor:pointer}.primary{background:#1b655f;border:1px solid #2b8b80;color:#e8fffa}.primary:hover{background:#24776f}.secondary{background:#0c2031;border:1px solid #315069;color:#a9bac7}.secondary:hover{background:#112b40}
.metrics-grid{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:10px;margin-bottom:15px}.metric-clickable{cursor:pointer;transition:border-color .16s ease,background .16s ease,transform .16s ease}.metric-clickable:hover{border-color:#3b7482;background:linear-gradient(145deg,#0e2638,#0d2031);transform:translateY(-1px)}.metric-clickable:focus-visible{outline:2px solid #42b6a4;outline-offset:2px}.card{background:linear-gradient(145deg,#0c2031,#0b1c2c);border:1px solid #1c374b;border-radius:8px;box-shadow:0 8px 28px rgba(0,0,0,.12)}.metric{padding:13px 14px;min-height:73px}.metric-label{font-size:8px;letter-spacing:1.1px;text-transform:uppercase;color:#71879a}.metric-value{font-size:20px;font-weight:750;margin-top:8px;color:#e8f0f4;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.grid-2{display:grid;grid-template-columns:minmax(0,1.35fr) minmax(0,1fr);gap:15px;margin-bottom:15px}.card-title{display:flex;justify-content:space-between;align-items:flex-start;padding:15px 16px 10px}.card-title h3{font-size:12px;margin:0 0 3px}.card-title span{display:block;color:#6f8496;font-size:9px}.pill{border:1px solid #28475b;background:#0b1d2c;color:#7590a2;border-radius:4px;padding:4px 7px;font-size:8px;letter-spacing:.8px;white-space:nowrap}
.map-wrap{height:425px;margin:0 10px 4px;border-radius:7px;overflow:hidden;position:relative;background:radial-gradient(circle at 48% 45%,rgba(22,61,82,.22),transparent 55%),#081825;border:1px solid #142e41}.india-svg{width:100%;height:100%;display:block;border:0;background:transparent}.map-note{padding:0 16px 14px;color:#60778a;font-size:8px;line-height:1.5}.map-tip{position:fixed;z-index:50;min-width:205px;max-width:255px;background:#07131f;border:1px solid #315069;border-radius:6px;box-shadow:0 15px 35px rgba(0,0,0,.45);padding:10px 12px;pointer-events:none}.map-tip strong{display:block;font-size:11px;color:#e7f0f4;margin-bottom:5px}.map-tip span{display:block;font-size:9px;color:#849bad;line-height:1.55}
.donut-box{display:flex;align-items:center;justify-content:center;gap:28px;padding:22px 20px 18px}.donut{width:150px;height:150px;border-radius:50%;display:grid;place-items:center;position:relative}.donut-hole{width:91px;height:91px;border-radius:50%;background:#0b1d2c;display:grid;place-items:center;align-content:center}.donut-hole strong{font-size:19px}.donut-hole span{font-size:8px;color:#6f8496}.legend{min-width:130px}.legend>div{display:flex;align-items:center;gap:7px;font-size:9px;color:#8da0b1;margin:8px 0}.legend i{width:7px;height:7px;border-radius:2px;display:inline-block}.legend b{margin-left:auto;color:#dce6eb}.quick-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:7px;padding:0 14px 15px}.quick-grid button{border:1px solid #1d3a4e;background:#0b1d2c;text-align:left;border-radius:6px;padding:10px;cursor:pointer}.quick-grid button:hover{border-color:#315d70;background:#0e2639}.quick-grid-primary button{min-height:102px;padding:17px}.quick-grid-primary b{font-size:14px}.quick-grid-primary span{font-size:11px}.quick-grid b{display:block;font-size:9px}.quick-grid span{display:block;color:#71889a;font-size:8px;margin-top:4px}
.bars{padding:5px 16px 18px}.bar-row{margin:10px 0}.bar-head{display:flex;justify-content:space-between;gap:10px;font-size:9px;color:#91a3b2}.bar-head b{color:#dce7ec;font-weight:600}.bar-track{height:5px;background:#10283a;border-radius:4px;margin-top:5px;overflow:hidden}.bar-fill{height:100%;background:linear-gradient(90deg,#1d7067,#42b6a4);border-radius:4px}.safeguard{padding:0 16px 16px}.safeguard>div{border-top:1px solid #183246;padding:12px 0}.safeguard b{display:block;font-size:9px;color:#c8d6df;margin-bottom:4px}.safeguard span{display:block;color:#71899b;font-size:9px;line-height:1.5}
.chooser-shell{min-height:100vh;background:radial-gradient(circle at 50% 0%,rgba(38,103,126,.18),transparent 42%),#06131f;display:flex;align-items:center;justify-content:center;padding:40px}.chooser{width:min(1120px,100%);text-align:center}.chooser-brand{display:inline-flex;align-items:center;gap:12px;color:#e8f2f6;margin-bottom:28px}.chooser-brand-mark{width:46px;height:46px;border-radius:12px;background:#12384b;border:1px solid #2d6072;display:grid;place-items:center;color:#67cdbb;font-weight:800;font-size:20px}.chooser h1{font-size:32px;margin:0 0 8px;letter-spacing:-.6px}.chooser>p{color:#8ea4b5;font-size:13px;margin:0 auto 34px;max-width:650px;line-height:1.6}.house-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;text-align:left}.house-card{position:relative;min-height:230px;border:1px solid #23465b;border-radius:14px;background:linear-gradient(145deg,#0d2638,#091b2a);padding:26px;cursor:pointer;transition:.18s;box-shadow:0 18px 50px rgba(0,0,0,.2)}.house-card:hover{transform:translateY(-4px);border-color:#3b8790;background:linear-gradient(145deg,#103044,#0a2030)}.house-icon{width:52px;height:52px;border-radius:12px;background:#123b50;border:1px solid #2d6374;display:grid;place-items:center;color:#6bd1bf;font-size:22px;margin-bottom:28px}.house-card h2{font-size:19px;margin:0 0 8px}.house-card p{font-size:10px;color:#8399aa;line-height:1.6;margin:0}.house-arrow{position:absolute;right:22px;bottom:20px;color:#58c6b2;font-size:18px}.chooser-note{margin-top:22px;color:#60788a;font-size:9px}.view-banner{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:15px;padding:12px 15px;border:1px solid #24475c;border-radius:8px;background:#0a1d2d}.view-banner strong{font-size:12px}.view-banner span{display:block;color:#71899b;font-size:9px;margin-top:3px}.directory-card{margin-bottom:15px}.directory-grid{display:grid;grid-template-columns:1.5fr 1fr 1fr auto;gap:8px;padding:14px}.directory-grid input,.directory-grid select{background:#091b2a;color:#c3d0d8;border:1px solid #29475b;border-radius:6px;padding:10px;font-size:10px;outline:none}.directory-grid input:focus,.directory-grid select:focus{border-color:#3c7d89}.search-results{border-top:1px solid #183246}.search-result{display:flex;justify-content:space-between;align-items:center;padding:11px 14px;border-bottom:1px solid #142e40;cursor:pointer}.search-result:hover{background:#0e2638}.search-result strong{font-size:10px}.search-result span{display:block;color:#72899a;font-size:8px;margin-top:3px}.profile-hero{display:grid;grid-template-columns:150px 1fr auto;gap:22px;align-items:center;padding:20px;margin-bottom:15px}.profile-photo{width:130px;height:150px;border-radius:10px;object-fit:cover;background:#102f43;border:1px solid #31586a}.profile-placeholder{width:130px;height:150px;border-radius:10px;background:linear-gradient(145deg,#14384b,#0d2536);border:1px solid #31586a;display:grid;place-items:center;color:#6bd1bf;font-size:28px;font-weight:800}.profile-identity h2{font-size:24px;margin:5px 0 8px}.profile-identity p{margin:0 0 7px;color:#879dac;font-size:10px;line-height:1.6}.party-badge{display:inline-block;border:1px solid #2e5266;background:#0c2334;border-radius:5px;padding:5px 8px;color:#a8bac6;font-size:9px}.profile-actions{text-align:right}.profile-actions button{margin-bottom:8px}.profile-data-grid{display:grid;grid-template-columns:repeat(5,1fr);gap:10px;margin-bottom:15px}.profile-data-grid .metric{min-height:86px}.chooser-back{margin-top:22px;background:none;border:1px solid #28495d;color:#8299a9;border-radius:6px;padding:8px 12px;font-size:9px;cursor:pointer}
.page-head{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:14px}.page-head h2{font-size:22px;margin:5px 0}.page-head p{margin:0;color:#7890a2;font-size:10px;line-height:1.6}.critical-count{font-size:23px;font-weight:750;color:#d94b4b}.filterbar{display:flex;align-items:center;gap:8px;padding:12px 14px;border-bottom:1px solid #183246}.filterbar input,.filterbar select{background:#091b2a;color:#b9c8d3;border:1px solid #28455a;border-radius:5px;padding:8px 9px;font-size:9px;outline:none;min-width:150px}.filterbar input{flex:1}.filterbar input:focus,.filterbar select:focus{border-color:#3c7a8a}.field-note,.score-range{font-size:9px;color:#71889a;padding:7px 9px}.table-scroll{width:100%;overflow:auto}.table-scroll table{width:100%;border-collapse:collapse;min-width:720px}.table-scroll th{font-size:8px;text-transform:uppercase;letter-spacing:.8px;color:#667e91;background:#091b2a;text-align:left;padding:10px 12px;border-bottom:1px solid #1c374b;white-space:nowrap}.table-scroll td{font-size:9px;color:#a8b8c4;padding:10px 12px;border-bottom:1px solid #152f42;white-space:nowrap}.table-scroll tr.clickable{cursor:pointer}.table-scroll tbody tr:hover{background:#0e2538}.badge{display:inline-block;border:1px solid;border-radius:4px;padding:3px 6px;font-size:8px;letter-spacing:.6px}.truncate{display:block;max-width:310px;overflow:hidden;text-overflow:ellipsis}.pager{display:flex;align-items:center;justify-content:center;gap:16px;padding:13px;color:#71899b;font-size:9px}.pager button{background:#0c2031;border:1px solid #28475b;border-radius:5px;padding:7px 10px;color:#a7b8c5;cursor:pointer;font-size:9px}.pager button:disabled{opacity:.35;cursor:not-allowed}.three-col{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;padding:14px}.info-box{border:1px solid #1c374b;border-radius:6px;padding:12px;background:#0a1c2b}.info-box b{display:block;font-size:9px;margin-bottom:5px}.info-box span{font-size:10px;color:#7e95a7}.profile-head{display:flex;gap:16px;align-items:center;padding:18px;margin-bottom:15px}.avatar{width:52px;height:52px;border-radius:50%;display:grid;place-items:center;background:#16374c;border:1px solid #2e586c;color:#73cdbc;font-weight:750}.profile-main h2{margin:4px 0;font-size:20px}.profile-main p{margin:0;color:#7890a2;font-size:10px}.profile-main small{display:block;color:#5f7789;font-size:8px;margin-top:6px}.detail-grid,.payment-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:1px;background:#183246;margin:0 16px 16px}.detail-grid>div,.payment-grid>div{background:#0b1d2c;padding:11px}.detail-grid span,.payment-grid span{display:block;color:#637b8e;font-size:8px;margin-bottom:5px}.detail-grid b,.payment-grid b{font-size:9px;color:#c9d6de}.lifecycle{display:grid;grid-template-columns:repeat(4,1fr);padding:12px 16px 17px;gap:0}.lifecycle>div{position:relative}.life-dot{display:inline-grid;place-items:center;width:21px;height:21px;border-radius:50%;background:#14384b;border:1px solid #2c6271;color:#79cdbd;font-size:8px;margin-right:7px}.lifecycle b{font-size:8px}.lifecycle small{display:block;color:#637b8d;font-size:8px;margin:7px 0 0 29px}.lifecycle i{position:absolute;right:8px;top:10px;color:#48677a;font-style:normal}.evidence-block{padding:0 16px 17px}.evidence-block h4{font-size:8px;letter-spacing:1px;color:#6f899c;margin:15px 0 7px}.evidence{border-left:2px solid #315568;background:#0a1c2b;padding:9px;color:#9eb0bc;font-size:9px;line-height:1.5}.human-check{margin-top:14px;border:1px solid #6d3f3f;background:#25171a;border-radius:5px;padding:10px}.human-check strong{display:block;color:#e57b7b;font-size:8px;letter-spacing:.8px}.human-check span{display:block;color:#9b7c7c;font-size:8px;margin-top:4px}.empty{padding:18px;color:#6f8798;font-size:9px}.weight-list{padding:0 16px 17px}.weight-list>div{display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid #173246}.weight-list b{color:#66c7b6;font-size:11px}.weight-list span{color:#8ca0af;font-size:9px}.clean-list{padding:0 30px 15px;color:#8da1b0;font-size:9px;line-height:2}.loading{padding:70px 20px;text-align:center;color:#70889a;font-size:10px}.error{padding:20px}.error strong{color:#e47777}.error p{font-size:10px;color:#a0afb9}.error small{color:#667d90;font-size:8px}
.dup-pair{border:1px solid #1c374b;border-radius:8px;margin:0 16px 12px;overflow:hidden}.dup-pair-head{display:flex;justify-content:space-between;align-items:center;padding:10px 13px;background:#0b1d2c;border-bottom:1px solid #183246}.dup-pair-head b{font-size:10px;color:#dce6eb}.dup-vs{display:grid;grid-template-columns:1fr 1fr;gap:1px;background:#183246}.dup-vs>div{background:#0a1c2b;padding:11px}.dup-vs span{display:block;color:#637b8e;font-size:8px;margin-bottom:4px}.dup-vs b{display:block;font-size:9px;color:#c9d6de;margin-bottom:6px}.dup-match-tags{display:flex;flex-wrap:wrap;gap:5px;padding:9px 13px}.dup-match-tags span{border:1px solid #2c5340;background:#0e2419;color:#7fcf9c;border-radius:4px;padding:3px 6px;font-size:8px}.dup-action{padding:9px 13px;border-top:1px solid #183246;color:#9eb0bc;font-size:9px}.batch-row{display:flex;justify-content:space-between;align-items:center;padding:11px 14px;border-bottom:1px solid #152f42;gap:10px}.batch-row b{font-size:9px;color:#dce6eb;display:block}.batch-row span{font-size:8px;color:#71889a}.unit-pill{border:1px solid #2e5266;background:#0c2334;color:#a8bac6;border-radius:12px;padding:4px 10px;font-size:9px;white-space:nowrap}.signal-tags{display:flex;flex-wrap:wrap;gap:4px}.signal-tag{border:1px solid #4a3320;background:#241708;color:#e5a94b;border-radius:4px;padding:2px 6px;font-size:8px}.severity-badge{border-radius:4px;padding:4px 9px;font-size:8px;letter-spacing:.6px;font-weight:700}.trend-select{margin:0 16px 12px}

/* Dashboard readability: larger official branding, labels and clickable cards */
.brand{padding:4px 10px 30px}.brand-mark{width:42px;height:42px;border-radius:10px;font-size:18px}.brand strong{font-size:18px;letter-spacing:1.8px}.brand small{font-size:9px;letter-spacing:1.35px}
.nav-title{font-size:10px;padding:14px 12px 8px}.nav-item{padding:13px 12px;font-size:14px;gap:12px}.nav-icon{width:20px;font-size:14px}.sidebar-foot{font-size:10px}
.topbar{min-height:116px;padding:22px 30px 20px}.topbar .eyebrow{font-size:10px}.topbar h1{font-size:30px;line-height:1.05;letter-spacing:.6px;margin:5px 0 4px}.topbar p{font-size:13px;color:#a5b6c3;margin:0}.topbar-subtitle{display:block;color:#71899b;font-size:11px;margin-top:3px}.status-dot{font-size:10px}.top-actions select,.top-actions .secondary{font-size:12px;padding:9px 12px}
.content{padding:24px 30px 50px;max-width:1700px}.breadcrumbs{margin-bottom:18px;font-size:13px}.view-banner{padding:17px 18px;margin-bottom:18px}.view-banner strong{font-size:17px}.view-banner span{font-size:11px;margin-top:5px}.secondary,.primary{font-size:12px;padding:10px 14px}
.metrics-grid{gap:14px;margin-bottom:18px}.metric{padding:18px 18px;min-height:104px}.metric-label{font-size:10px;letter-spacing:1.25px}.metric-value{font-size:28px;margin-top:11px;line-height:1.1}
.card-title{padding:18px 18px 12px}.card-title h3{font-size:15px;margin-bottom:5px}.card-title span{font-size:11px}.pill{padding:6px 9px;font-size:10px}.grid-2{gap:18px;margin-bottom:18px}.quick-grid{gap:10px;padding:0 16px 18px}.quick-grid button{min-height:92px;padding:15px;border-radius:8px}.quick-grid b{font-size:13px}.quick-grid span{font-size:11px;margin-top:6px}.map-note{font-size:10px}.legend>div{font-size:11px}.donut-hole strong{font-size:22px}.donut-hole span{font-size:10px}
.directory-grid input,.directory-grid select{padding:12px;font-size:12px}.search-result{padding:14px 16px}.search-result strong{font-size:12px}.search-result span{font-size:10px}.filterbar input,.filterbar select{padding:10px;font-size:11px}.filterbar{padding:15px 16px}.field-note,.score-range{font-size:11px}.table-scroll th{font-size:10px;padding:12px 14px}.table-scroll td{font-size:11px;padding:13px 14px}.badge{font-size:10px;padding:4px 7px}.pager{font-size:11px}.pager button{font-size:11px;padding:9px 12px}
.page-head h2{font-size:26px}.page-head p{font-size:12px}.eyebrow{font-size:10px}.profile-identity h2{font-size:28px}.profile-identity p{font-size:12px}.profile-data-grid .metric{min-height:100px}.detail-grid>div,.payment-grid>div{padding:14px}.detail-grid span,.payment-grid span{font-size:10px;margin-bottom:7px}.detail-grid b,.payment-grid b{font-size:12px}.lifecycle{padding:15px 18px 20px}.lifecycle b{font-size:10px}.lifecycle small{font-size:10px}.life-dot{width:25px;height:25px;font-size:9px}.three-col{gap:12px;padding:16px}.info-box{padding:14px}.info-box b{font-size:11px}.info-box span{font-size:12px}.safeguard{padding:0 18px 18px}.safeguard b{font-size:11px}.safeguard span{font-size:11px}.bars{padding:6px 18px 20px}.bar-head{font-size:11px}.bar-track{height:6px}
.work-id-title{font-size:32px!important}.work-description{font-size:16px!important}.risk-summary{font-size:13px}.risk-summary b{font-size:15px}.risk-summary-text{font-size:12px}.review-action span{font-size:10px}.review-action strong{font-size:12px}.risk-factor span{font-size:9px}.risk-factor b{font-size:12px}.detail-toggle{padding:16px 18px}.detail-toggle strong{font-size:13px}.detail-toggle span{font-size:11px}

@media(max-width:1100px){.sidebar{width:205px}.main{margin-left:205px;width:calc(100% - 205px)}.metrics-grid{grid-template-columns:repeat(3,1fr)}.grid-2{grid-template-columns:1fr}.content{padding:18px}.topbar{padding:17px 18px}.global-strip{padding:0 18px}}

/* Work detail readability + progressive disclosure */
.work-id-title{font-size:30px!important;line-height:1.2!important;color:#ffffff!important;font-weight:800!important;letter-spacing:.1px!important;margin:6px 0 8px!important}
.work-description{font-size:15px!important;line-height:1.55!important;color:#ffffff!important;max-width:1100px!important;margin:0!important}
.risk-explanation{margin-bottom:15px}.risk-explanation .explain-body{padding:0 16px 17px}
.risk-summary{border-left:3px solid var(--accent);background:#0a1d2c;border-radius:5px;padding:14px 16px;color:#dce8ee;font-size:12px;line-height:1.65}.risk-summary b{color:#fff;display:block;font-size:13px;margin-bottom:5px}.risk-summary-text{color:#9fb1bd;font-size:11px;line-height:1.6}
.review-action{margin-top:10px;border:1px solid #36576a;background:#0b2030;border-radius:6px;padding:11px 13px}.review-action span{display:block;color:#6f899b;font-size:8px;letter-spacing:1px;font-weight:700;margin-bottom:5px}.review-action strong{display:block;color:#d9e5eb;font-size:10px;line-height:1.5;font-weight:600}
.risk-factors{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:9px;margin-top:10px}.risk-factor{border:1px solid #1c374b;border-radius:6px;background:#091b2a;padding:10px 12px}.risk-factor span{display:block;color:#6f8799;font-size:8px;letter-spacing:.7px;text-transform:uppercase;margin-bottom:5px}.risk-factor b{font-size:11px;color:#fff;line-height:1.35}
.screening-disclaimer{display:flex;gap:9px;align-items:flex-start;margin-top:10px;border:1px solid #6d3f3f;background:#25171a;border-radius:5px;padding:9px 11px}.screening-disclaimer strong{color:#e57b7b;font-size:8px;letter-spacing:.7px;white-space:nowrap}.screening-disclaimer span{color:#9b7c7c;font-size:8px;line-height:1.45}
.detail-toggle{width:100%;display:flex;align-items:center;justify-content:space-between;background:#0a1d2c;border:1px solid #25445a;border-radius:7px;padding:13px 16px;color:#e9f2f6;cursor:pointer;margin-bottom:15px;text-align:left}.detail-toggle:hover{background:#0d2639;border-color:#397082}.detail-toggle strong{font-size:11px;letter-spacing:.3px}.detail-toggle span{font-size:10px;color:#7f95a6}
.detail-panel{display:grid;gap:15px;margin-bottom:15px}
@media(max-width:760px){.risk-factors{grid-template-columns:1fr}.work-id-title{font-size:24px!important}.work-description{font-size:13px!important}}
@media(max-width:760px){.sidebar{position:static;width:100%;height:auto}.shell{display:block}.main{margin-left:0;width:100%}.sidebar{flex-direction:row;align-items:center;overflow:auto;padding:8px}.brand{padding:0 10px}.nav-title,.sidebar-foot{display:none}.nav-item{width:auto;white-space:nowrap}.nav-item span{display:none}.topbar{align-items:flex-start;gap:12px;flex-direction:column}.metrics-grid{grid-template-columns:repeat(2,1fr)}.content{padding:12px}.hero{padding:20px}.hero-badge{display:none}.quick-grid{grid-template-columns:1fr}.donut-box{flex-direction:column}.filterbar{flex-wrap:wrap}.filterbar input{min-width:100%}.detail-grid,.payment-grid{grid-template-columns:repeat(2,1fr)}.lifecycle{grid-template-columns:1fr 1fr;gap:14px}.lifecycle i{display:none}.three-col{grid-template-columns:1fr}}
`;

const RISK = {NORMAL:'#1fa971', REVIEW:'#e5b84b', HIGH:'#ee8b32', CRITICAL:'#d94b4b'};
const fmt = n => n == null || Number.isNaN(Number(n)) ? 'Data Not Available' : Number(n).toLocaleString('en-IN',{maximumFractionDigits:2});
const cr = n => n == null || Number.isNaN(Number(n)) ? 'Data Not Available' : `₹${(Number(n)/1e7).toLocaleString('en-IN',{maximumFractionDigits:2})} Cr`;
const pct = n => n == null || Number.isNaN(Number(n)) ? 'Data Not Available' : `${Number(n).toFixed(1)}%`;
const API_BASE = (import.meta.env.VITE_API_URL || '').replace(/\\/$/, '');
const api = async (path) => {
  const r = await fetch(`${API_BASE}${path}`);
  if(!r.ok) throw new Error(await r.text());
  return r.json();
};
const esc = s => s==null ? 'Data Not Available' : String(s);
function go(path){
  const next=path.startsWith('#')?path.slice(1):path;
  if(location.hash.slice(1)!==next){ location.hash=next; } else { window.dispatchEvent(new HashChangeEvent('hashchange')); }
}
function useRoute(){
  const read=()=>location.hash.slice(1)||'/';
  const [route,setRoute]=useState(read);
  useEffect(()=>{
    const onHash=()=>setRoute(read());
    window.addEventListener('hashchange',onHash);
    window.addEventListener('popstate',onHash);
    return()=>{window.removeEventListener('hashchange',onHash);window.removeEventListener('popstate',onHash)};
  },[]);
  return route;
}

function Badge({level}){return h('span',{className:'badge',style:{color:RISK[level]||'#9aa8b8',borderColor:(RISK[level]||'#596579')+'66',background:(RISK[level]||'#596579')+'14'}},level||'Data Not Available')}
function Card({children,className='',...props}){return h('div',{...props,className:'card '+className},children)}
function Metric({label,value,tone,onClick}){
  const clickable=typeof onClick==='function';
  const props={className:'metric'+(clickable?' metric-clickable':''),onClick};
  if(clickable){props.role='button';props.tabIndex=0;props.title='Open '+label;props.onKeyDown=e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();onClick();}};}
  return h(Card,props,h('div',{className:'metric-label'},label),h('div',{className:'metric-value',style:tone?{color:tone}:{}},value));
}
function Breadcrumbs({items}){return h('div',{className:'breadcrumbs'},items.map((x,i)=>h(React.Fragment,{key:i},i?h('span',null,'›'):null,h('button',{onClick:()=>go(x.path)},x.label))))}

function Layout({route,children}){
 const nav=[['/','Command Center','⌂'],['/chamber/lok-sabha','Lok Sabha','▦'],['/chamber/rajya-sabha','Rajya Sabha','▦'],['/critical','Critical Cases','!'],['/risk-explorer','Risk Explorer','⌕'],['/outliers','Spending Outliers','◈']];
 const navGaps=[['/duplicates','Potential Duplicates','⧉'],['/cost-overruns','Cost Overruns','₹'],['/compliance','Compliance','✓'],['/early-warnings','Early Warnings','⚠'],['/trends','Trends','▤'],['/predictions','Predictive Insights','↗']];
 const aside=h('aside',{className:'sidebar'},
   h('div',{className:'brand'},h('div',{className:'brand-mark'},'M'),h('div',null,h('strong',null,'MPLADS'),h('small',null,'AI AUDIT INTELLIGENCE'))),
   h('div',{className:'nav-title'},'AUDIT CONSOLE'),
   nav.map(([p,l,ic])=>h('button',{key:p,className:'nav-item '+((route===p||route.startsWith(p+'/'))?'active':''),onClick:()=>go(p)},h('span',{className:'nav-icon'},ic),l)),
   h('div',{className:'nav-title'},'PS26102 GAP ANALYSIS'),
   navGaps.map(([p,l,ic])=>h('button',{key:p,className:'nav-item '+((route===p||route.startsWith(p+'/'))?'active':''),onClick:()=>go(p)},h('span',{className:'nav-icon'},ic),l)),
   h('div',{className:'nav-title'},'SYSTEM'),
   h('button',{className:'nav-item',onClick:()=>go('/methodology')},h('span',{className:'nav-icon'},'◉'),'Methodology'),
   h('div',{className:'sidebar-foot'},'PS SIH26102','Audit-support tool — human verification required.')
 );
 const header=h('header',{className:'topbar'},
   h('div',null,
     h('div',{className:'eyebrow'},'GOVERNMENT AUDIT INTELLIGENCE'),
     h('h1',null,'MPLADS'),
     h('p',null,'Members of Parliament Local Area Development Scheme'),
     h('span',{className:'topbar-subtitle'},'AI-Powered Audit & Risk Intelligence')
   ),
   h('div',{className:'top-actions'},h('span',{className:'status-dot'},'● SYSTEM ACTIVE'),h('button',{className:'secondary',onClick:()=>go('/')},route.includes('/lok-sabha')?'Lok Sabha':route.includes('/rajya-sabha')?'Rajya Sabha':route.includes('/combined')?'Combined View':'Choose View'))
 );
 return h('div',{className:'shell'},aside,h('main',{className:'main'},header,h('div',{className:'content'},children)));
}

const CODE_MAP={'Jammu And Kashmir':'JK','Ladakh':'LA','Himachal Pradesh':'HP','Punjab':'PB','Uttarakhand':'UK','Haryana':'HR','Delhi':'DL','Rajasthan':'RJ','Uttar Pradesh':'UP','Sikkim':'SK','Arunachal Pradesh':'AR','Assam':'AS','Nagaland':'NL','Meghalaya':'ML','Bihar':'BR','Jharkhand':'JH','West Bengal':'WB','Tripura':'TR','Mizoram':'MZ','Madhya Pradesh':'MP','Gujarat':'GJ','Daman And Diu':'DN','Dadra And Nagar Haveli':'DN','Chhattisgarh':'CT','Odisha':'OR','Maharashtra':'MH','Telangana':'TG','Goa':'GA','Karnataka':'KA','Andhra Pradesh':'AP','Kerala':'KL','Tamil Nadu':'TN','Puducherry':'PY','Andaman And Nicobar Islands':'AN','Lakshadweep':'LD','Chandigarh':'CH'};
function codeFor(state){return CODE_MAP[state]||''}

function IndiaMap({states,chamber}){
  const [tip,setTip]=useState(null);
  const byCode=useMemo(()=>{
    const m={};
    (states||[]).forEach(s=>{
      const code=codeFor(s.state);
      if(code)m[code]=s;
    });
    return m;
  },[states]);

  const NAME_TO_CODE={
    'andhra pradesh':'AP','arunachal pradesh':'AR','assam':'AS','bihar':'BR',
    'chhattisgarh':'CT','goa':'GA','gujarat':'GJ','haryana':'HR','himachal pradesh':'HP',
    'jharkhand':'JH','karnataka':'KA','kerala':'KL','madhya pradesh':'MP',
    'maharashtra':'MH','manipur':'MN','meghalaya':'ML','mizoram':'MZ','nagaland':'NL',
    'odisha':'OR','orissa':'OR','punjab':'PB','rajasthan':'RJ','sikkim':'SK',
    'tamil nadu':'TN','tamilnadu':'TN','telangana':'TG','tripura':'TR',
    'uttar pradesh':'UP','uttarakhand':'UK','uttaranchal':'UK','west bengal':'WB',
    'delhi':'DL','new delhi':'DL','jammu and kashmir':'JK','jammu & kashmir':'JK',
    'ladakh':'LA','puducherry':'PY','pondicherry':'PY','chandigarh':'CH',
    'andaman and nicobar islands':'AN','andaman & nicobar islands':'AN',
    'lakshadweep':'LD','daman and diu':'DN','dadra and nagar haveli':'DN',
    'dadra and nagar haveli and daman and diu':'DN',
    'dadra & nagar haveli and daman & diu':'DN'
  };

  function norm(v){
    return String(v||'')
      .toLowerCase()
      .replace(/[_-]+/g,' ')
      .replace(/&/g,' and ')
      .replace(/[^\w\s]/g,' ')
      .replace(/\s+/g,' ')
      .trim();
  }

  function identify(el){
    const attrs=['data-state','data-name','data-state-name','name','id','class'];
    for(const a of attrs){
      const raw=el.getAttribute&&el.getAttribute(a);
      if(!raw)continue;
      const n=norm(raw);
      if(byCode[raw]) return raw;
      if(NAME_TO_CODE[n]) return NAME_TO_CODE[n];
      const found=Object.entries(NAME_TO_CODE).find(([name])=>n.includes(name));
      if(found)return found[1];
      const code=Object.keys(byCode).find(c=>n===c.toLowerCase() || n.includes(c.toLowerCase()));
      if(code)return code;
      const inCode=n.match(/\bin[-_ ]?(ap|ar|as|br|ct|ga|gj|hr|hp|jh|ka|kl|mp|mh|mn|ml|mz|nl|or|pb|rj|sk|tn|tg|tr|up|uk|wb|dl|jk|la|py|ch|an|ld|dn)\b/);
      if(inCode)return inCode[1].toUpperCase();
    }
    const title=el.querySelector&&el.querySelector('title');
    if(title){
      const n=norm(title.textContent);
      if(NAME_TO_CODE[n])return NAME_TO_CODE[n];
    }
    return '';
  }

  function applyState(el,s){
    if(!el)return;
    const targets=el.matches&&el.matches('path,polygon,polyline,rect,circle,ellipse')?[el]:
      Array.from(el.querySelectorAll?el.querySelectorAll('path,polygon,polyline,rect,circle,ellipse'):[]);
    const nodes=targets.length?targets:[el];
    nodes.forEach(node=>{
      node.style.setProperty('fill',s?(s.critical?RISK.CRITICAL:s.high_risk?RISK.HIGH:RISK.NORMAL):'#1c3346','important');
      node.style.setProperty('stroke','#0a1420','important');
      node.style.setProperty('stroke-width','1.2','important');
      node.style.cursor=s?'pointer':'default';
      node.style.transition='fill .18s ease, opacity .18s ease';
    });
    return nodes;
  }

  async function attach(e){
    try{
      const doc=e.target.contentDocument;
      if(!doc)return;
      const all=Array.from(doc.querySelectorAll('path,polygon,polyline,g'));
      let matched=0;
      all.forEach(el=>{
        const code=identify(el);
        if(!code)return;
        const s=byCode[code];
        const nodes=applyState(el,s);
        if(s && nodes)matched++;
        if(s){
          const enter=ev=>setTip({x:ev.clientX,y:ev.clientY,state:s});
          const move=ev=>setTip(t=>t?{...t,x:ev.clientX,y:ev.clientY,state:s}:t);
          const leave=()=>setTip(null);
          (nodes||[el]).forEach(node=>{
            node.onmouseenter=enter;
            node.onmousemove=move;
            node.onmouseleave=leave;
            node.onclick=()=>{const stateName=s.state_display||s.state||s.name;if(stateName)go('/state/'+encodeURIComponent(stateName)+'?chamber='+encodeURIComponent(chamber||'All'));};
          });
        }
      });

      // Fallback for SVGs that use only <title> elements inside state groups.
      if(matched===0){
        doc.querySelectorAll('g').forEach(g=>{
          const code=identify(g);
          if(code)applyState(g,byCode[code]);
        });
      }
    }catch(err){
      console.error('India SVG initialization failed:',err);
    }
  }

  return h('div',{className:'map-wrap'},
    h('object',{data:'/maps/india-states.svg',type:'image/svg+xml',className:'india-svg',onLoad:attach}),
    tip&&h('div',{
      className:'map-tip',
      style:{left:Math.min(tip.x+14,window.innerWidth-270),top:Math.min(tip.y+14,window.innerHeight-150)}
    },
      h('strong',null,tip.state.state_display),
      h('span',null,`${fmt(tip.state.total_works)} total works`),
      h('span',null,`${fmt(tip.state.high_risk)} high-risk`),
      h('span',null,`${fmt(tip.state.critical)} critical`)
    )
  );
}

function RiskDonut({risk,onSelect}){
  const total=Object.values(risk).reduce((a,b)=>a+(Number(b)||0),0);
  let acc=0;
  const stops=total?Object.entries(RISK).map(([k,c])=>{const a=acc;acc+=((Number(risk[k])||0)/total)*360;return `${c} ${a}deg ${acc}deg`}).join(','):'#163247 0deg 360deg';
  return h('div',{className:'donut-box'},
    h('div',{className:'donut',style:{background:`conic-gradient(${stops})`,cursor:onSelect?'pointer':'default'},onClick:()=>onSelect&&onSelect('All'),title:onSelect?'Click to open all risk levels':''},h('div',{className:'donut-hole'},h('strong',null,fmt(total)),h('span',null,'Total'))),
    h('div',{className:'legend'},Object.entries(RISK).map(([k,c])=>h('div',{key:k,onClick:()=>onSelect&&onSelect(k),style:{cursor:onSelect?'pointer':'default'},title:onSelect?'Open '+k+' works':''},h('i',{style:{background:c}}),k,h('b',null,fmt(risk[k]||0)))))
  );
}
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

function ChamberChooser(){
 const choose=(value)=>{location.hash='/dashboard/'+(value==='All'?'combined':value==='Lok Sabha'?'lok-sabha':'rajya-sabha')};
 return h('div',{className:'chooser-shell'},h('div',{className:'chooser'},
   h('div',{className:'chooser-brand'},h('div',{className:'chooser-brand-mark'},'M'),h('strong',null,'MPLADS AI AUDIT INTELLIGENCE')),
   h('h1',null,'Choose your view'),
   h('p',null,'Select the parliamentary house you want to explore. All statistics, the India map, searches and MP profiles will be limited to that selection.'),
   h('div',{className:'house-grid'},
     h('button',{className:'house-card',onClick:()=>choose('Lok Sabha')},h('div',{className:'house-icon'},'LS'),h('h2',null,'Lok Sabha'),h('p',null,'Explore Lok Sabha works, states, constituencies, MPs and audit-risk signals.'),h('span',{className:'house-arrow'},'→')),
     h('button',{className:'house-card',onClick:()=>choose('Rajya Sabha')},h('div',{className:'house-icon'},'RS'),h('h2',null,'Rajya Sabha'),h('p',null,'Explore Rajya Sabha works, states, assigned or nodal districts where available, MPs and audit-risk signals.'),h('span',{className:'house-arrow'},'→')),
     h('button',{className:'house-card',onClick:()=>choose('All')},h('div',{className:'house-icon'},'ALL'),h('h2',null,'Combined View'),h('p',null,'View the complete MPLADS dataset across Lok Sabha and Rajya Sabha together.'),h('span',{className:'house-arrow'},'→'))
   ),
   h('div',{className:'chooser-note'},'Risk classifications are screening signals for human audit verification, not findings of fraud.')
 ));
}

function SearchDirectory({chamber}){
 const [q,setQ]=useState(''),[state,setState]=useState(''),[constituency,setConstituency]=useState(''),[filters,setFilters]=useState(null),[results,setResults]=useState([]),[busy,setBusy]=useState(false);
 useEffect(()=>{api('/api/filters?chamber='+encodeURIComponent(chamber)).then(setFilters).catch(()=>{})},[chamber]);
 const run=async()=>{const term=q||constituency||state;if(!term)return;if(state){go('/state/'+encodeURIComponent(state)+'?chamber='+encodeURIComponent(chamber));return}setBusy(true);try{const d=await api('/api/works?'+new URLSearchParams({page:1,page_size:12,q:term,chamber}).toString());setResults(d.rows||[])}finally{setBusy(false)}};
 const open=(r)=>{if((q||constituency)&&r.mp_id)go('/mp/'+r.mp_id+'?chamber='+encodeURIComponent(chamber));else if(state)go('/state/'+encodeURIComponent(state)+'?chamber='+encodeURIComponent(chamber));else go('/work/'+encodeURIComponent(r.work_id))};
 return h(Card,{className:'directory-card'},h('div',{className:'card-title'},h('div',null,h('h3',null,'Find an MP, Constituency or State'),h('span',null,'Search within the selected parliamentary view.'))),
   h('div',{className:'directory-grid'},
     h('input',{value:q,onChange:e=>{setQ(e.target.value);setConstituency('');setState('')},placeholder:'Search by MP name…'}),
     h('select',{value:constituency,onChange:e=>{setConstituency(e.target.value);setQ('');setState('')}},h('option',{value:''},'Select constituency'),filters&&filters.constituencies.map(x=>h('option',{key:x,value:x},x))),
     h('select',{value:state,onChange:e=>{setState(e.target.value);setQ('');setConstituency('')}},h('option',{value:''},'Select state'),filters&&filters.states.map(x=>h('option',{key:x,value:x},x))),
     h('button',{className:'primary',onClick:run},busy?'Searching…':'Search')
   ),results.length&&h('div',{className:'search-results'},results.map((r,i)=>h('div',{className:'search-result',key:i,onClick:()=>open(r)},h('div',null,h('strong',null,r.mp_name||'Data Not Available'),h('span',null,`${r.state_display||r.state||'Data Not Available'} · ${r.constituency||'Data Not Available'}`)),h('span',null,`Risk ${Number(r.risk_score||0).toFixed(1)}`))))
 );
}

function Home({chamber}){
 const [data,setData]=useState(null),[states,setStates]=useState([]),[err,setErr]=useState(null);
 useEffect(()=>{Promise.all([api('/api/summary?chamber='+encodeURIComponent(chamber)),api('/api/states?chamber='+encodeURIComponent(chamber))]).then(([a,b])=>{setData(a);setStates(b)}).catch(setErr)},[chamber]);
 if(err)return h(ErrorBox,{e:err}); if(!data)return h(Loading);
 const top=states.slice().sort((a,b)=>b.expenditure-a.expenditure).slice(0,6);
 const openRisk=(level)=>{
    if(level==='CRITICAL'){go('/critical?chamber='+encodeURIComponent(chamber));return;}
    const risk=level==='All'?'All':level;
    go('/risk-explorer?risk='+encodeURIComponent(risk)+'&chamber='+encodeURIComponent(chamber));
  };
  const metrics=h('div',{className:'metrics-grid'},
    h(Metric,{label:'Total Works',value:fmt(data.total_works),onClick:()=>openRisk('All')}),
    h(Metric,{label:'Normal',value:fmt(data.risk.NORMAL),tone:RISK.NORMAL,onClick:()=>openRisk('NORMAL')}),
    h(Metric,{label:'Review',value:fmt(data.risk.REVIEW),tone:RISK.REVIEW,onClick:()=>openRisk('REVIEW')}),
    h(Metric,{label:'High Risk',value:fmt(data.risk.HIGH),tone:RISK.HIGH,onClick:()=>openRisk('HIGH')}),
    h(Metric,{label:'Critical',value:fmt(data.risk.CRITICAL),tone:RISK.CRITICAL,onClick:()=>openRisk('CRITICAL')}),
    h(Metric,{label:'Total Expenditure',value:cr(data.money.expenditure)})
  );
 const mapCard=h(Card,null,h('div',{className:'card-title'},h('div',null,h('h3',null,'India Risk Distribution'),h('span',null,'Hover a state. Click to open its audit view.')),h('span',{className:'pill'},chamber.toUpperCase())),h(IndiaMap,{states,chamber}),h('div',{className:'map-note'},'State statistics are filtered to the selected parliamentary view. The SVG is used for navigation, not legal boundary determination.'));
 const riskCard=h(Card,null,h('div',{className:'card-title'},h('div',null,h('h3',null,'Risk Level Distribution'),h('span',null,`${chamber} pipeline output`)),h('span',{className:'pill'},`${fmt(data.total_works)} SCREENED`)),h(RiskDonut,{risk:data.risk,onSelect:openRisk}),h('div',{className:'quick-grid quick-grid-primary'},h('button',{onClick:()=>go('/critical?chamber='+encodeURIComponent(chamber))},h('b',null,'Critical Works'),h('span',null,fmt(data.risk.CRITICAL)+' cases')),h('button',{onClick:()=>go('/risk-explorer?risk=HIGH&chamber='+encodeURIComponent(chamber))},h('b',null,'High-Risk Works'),h('span',null,fmt(data.risk.HIGH)+' cases')),h('button',{onClick:()=>go('/outliers?chamber='+encodeURIComponent(chamber))},h('b',null,'Spending Outliers'),h('span',null,'Statistical ranking'))));
 const insights=h('div',{className:'grid-2'},h(Card,null,h('div',{className:'card-title'},h('div',null,h('h3',null,'Top States by Expenditure'),h('span',null,`${chamber} aggregated output`))),h(BarList,{items:top.map(x=>({label:x.state_display,value:x.expenditure})),money:true})),h(Card,null,h('div',{className:'card-title'},h('div',null,h('h3',null,'Audit Safeguard'),h('span',null,'How to interpret risk'))),h('div',{className:'safeguard'},h('div',null,h('b',null,'Potential signal'),h('span',null,'Risk prioritizes records for audit review using the verified pipeline output.')),h('div',null,h('b',null,'Human verification'),h('span',null,'High / Critical cases are not confirmed fraud findings.')))));
 return h('div',null,Breadcrumbs({items:[{label:'Home',path:'/'},{label:chamber,path:'/dashboard/'+(chamber==='Lok Sabha'?'lok-sabha':chamber==='Rajya Sabha'?'rajya-sabha':'combined')}] }),h('div',{className:'view-banner'},h('div',null,h('strong',null,chamber),h('span',null,'All dashboard statistics below are limited to this selection.')),h('button',{className:'secondary',onClick:()=>go('/')},'Change View')),metrics,h('div',{className:'grid-2'},mapCard,riskCard),h(SearchDirectory,{chamber}),insights);
}

function ChamberPage({chamber}){const [data,setData]=useState(null),[filters,setFilters]=useState(null),[q,setQ]=useState(''); useEffect(()=>{Promise.all([api('/api/summary?chamber='+encodeURIComponent(chamber)),api('/api/filters?chamber='+encodeURIComponent(chamber))]).then(([a,b])=>{setData(a);setFilters(b)})},[chamber]); if(!data||!filters)return h(Loading); return h('div',null,Breadcrumbs({items:[{label:'Home',path:'/'},{label:chamber,path:'/chamber/'+(chamber==='Lok Sabha'?'lok-sabha':'rajya-sabha')}]}),h('div',{className:'page-head'},h('div',null,h('div',{className:'eyebrow'},'PARLIAMENTARY CHAMBER'),h('h2',null,chamber),h('p',null,chamber==='Rajya Sabha'?'No constituency is fabricated. Nodal/assigned district is shown only if present in the source data.':'State, constituency and district filters are driven by the actual output schema.')),h('button',{className:'secondary',onClick:()=>go('/risk-explorer')},'Explore all works')),
 h('div',{className:'metrics-grid'},h(Metric,{label:'Total Works',value:fmt(data.total_works),onClick:()=>go('/risk-explorer?risk=All&chamber='+encodeURIComponent(chamber))}),h(Metric,{label:'Normal',value:fmt(data.risk.NORMAL),tone:RISK.NORMAL,onClick:()=>go('/risk-explorer?risk=NORMAL&chamber='+encodeURIComponent(chamber))}),h(Metric,{label:'Review',value:fmt(data.risk.REVIEW),tone:RISK.REVIEW,onClick:()=>go('/risk-explorer?risk=REVIEW&chamber='+encodeURIComponent(chamber))}),h(Metric,{label:'High',value:fmt(data.risk.HIGH),tone:RISK.HIGH,onClick:()=>go('/risk-explorer?risk=HIGH&chamber='+encodeURIComponent(chamber))}),h(Metric,{label:'Critical',value:fmt(data.risk.CRITICAL),tone:RISK.CRITICAL,onClick:()=>go('/critical?chamber='+encodeURIComponent(chamber))}),h(Metric,{label:'Expenditure',value:cr(data.money.expenditure)})),
 h(Card,null,h('div',{className:'filterbar'},h('select',null,h('option',null,'All States'),filters.states.map(s=>h('option',{key:s},s))),chamber==='Lok Sabha'&&h('select',null,h('option',null,'All Constituencies'),filters.constituencies.map(s=>h('option',{key:s},s))),chamber==='Rajya Sabha'&&h('div',{className:'field-note'},'Assigned / Nodal District: Data Not Available'),h('input',{value:q,onChange:e=>setQ(e.target.value),placeholder:chamber==='Lok Sabha'?'Search by MP Name or Constituency…':'Search by MP Name or Nodal District…'}),h('button',{className:'primary',onClick:()=>go('/risk-explorer?q='+encodeURIComponent(q))},'Search'))),
 h(Card,null,h('div',{className:'card-title'},h('div',null,h('h3',null,'Audit posture'),h('span',null,'Use Risk Explorer for server-side pagination across the full dataset.'))),h('div',{className:'three-col'},h('div',{className:'info-box'},h('b',null,'Normal'),h('span',null,fmt(data.risk.NORMAL)+' works')),h('div',{className:'info-box'},h('b',null,'High / Critical'),h('span',null,fmt(data.risk.HIGH+data.risk.CRITICAL)+' prioritized cases')),h('div',{className:'info-box'},h('b',null,'Data discipline'),h('span',null,'Missing fields remain Data Not Available')))));
}

function StatePage({name}){const params=new URLSearchParams(location.hash.split('?')[1]||'');const chamber=params.get('chamber')||'All';const [d,setD]=useState(null),[err,setErr]=useState(null); useEffect(()=>{api('/api/state/'+encodeURIComponent(name)+'?chamber='+encodeURIComponent(chamber)).then(setD).catch(setErr)},[name,chamber]); if(err)return h(ErrorBox,{e:err}); if(!d)return h(Loading); if(!d.found)return h(Card,null,'State not found in current dataset.'); return h('div',null,Breadcrumbs({items:[{label:'Home',path:'/'},{label:d.state,path:'/state/'+encodeURIComponent(d.state)+'?chamber='+encodeURIComponent(chamber)}]}),h('div',{className:'page-head'},h('div',null,h('div',{className:'eyebrow'},'STATE AUDIT VIEW'),h('h2',null,d.state),h('p',null,'Aggregated from the existing anomaly pipeline.')),h(Badge,{level:d.summary.critical?'CRITICAL':'NORMAL'})),h('div',{className:'metrics-grid'},h(Metric,{label:'Total Works',value:fmt(d.summary.total_works)}),h(Metric,{label:'Normal',value:fmt(d.summary.NORMAL),tone:RISK.NORMAL}),h(Metric,{label:'Review',value:fmt(d.summary.REVIEW),tone:RISK.REVIEW}),h(Metric,{label:'High',value:fmt(d.summary.HIGH),tone:RISK.HIGH}),h(Metric,{label:'Critical',value:fmt(d.summary.CRITICAL),tone:RISK.CRITICAL}),h(Metric,{label:'Expenditure',value:cr(d.summary.expenditure)})),h('div',{className:'grid-2'},h(Card,null,h('div',{className:'card-title'},h('div',null,h('h3',null,'Risk Distribution')),h('span',{className:'pill'},'STATE')),h(RiskDonut,{risk:{NORMAL:d.summary.NORMAL,REVIEW:d.summary.REVIEW,HIGH:d.summary.HIGH,CRITICAL:d.summary.CRITICAL}})),h(Card,null,h('div',{className:'card-title'},h('div',null,h('h3',null,'MP Risk Concentration'),h('span',null,'Top 50 by high/critical workload'))),h(BarList,{items:d.mps.slice(0,8).map(x=>({label:x.mp_name,value:x.critical*5+x.high})),valueKey:'value'}))),h(Card,null,h('div',{className:'card-title'},h('div',null,h('h3',null,'MPs')),h('span',{className:'pill'},fmt(d.mps.length)+' shown')),h(Table,{columns:['mp_name','chamber','constituency','works','high','critical'],rows:d.mps,rowClick:r=>go('/mp/'+r.mp_id+'?chamber='+encodeURIComponent(chamber)),render:{constituency:r=>r.constituency||'Data Not Available',mp_name:r=>r.mp_name}})),h(Card,null,h('div',{className:'card-title'},h('div',null,h('h3',null,'High & Critical Works')),h('span',{className:'pill'},'PRIORITIZED')),h(WorkTable,{rows:[...d.critical_works,...d.high_works]})));
}

function Table({columns,rows,rowClick,render={}}){return h('div',{className:'table-scroll'},h('table',null,h('thead',null,h('tr',null,columns.map(c=>h('th',{key:c},c.replaceAll('_',' '))))),h('tbody',null,rows.map((r,i)=>h('tr',{key:i,onClick:()=>rowClick&&rowClick(r),className:rowClick?'clickable':''},columns.map(c=>h('td',{key:c},render[c]?render[c](r):esc(r[c]))))))));}
function WorkTable({rows}){return h(Table,{columns:['work_id','mp_name','state','risk_score','risk_level','primary_reason'],rows,rowClick:r=>go('/work/'+encodeURIComponent(r.work_id)),render:{risk_level:r=>h(Badge,{level:r.risk_level}),risk_score:r=>Number(r.risk_score||0).toFixed(1),primary_reason:r=>h('span',{className:'truncate'},r.primary_reason||'Data Not Available')}})}

function daysBetween(a,b){
 const x=new Date(a),y=new Date(b);
 if(Number.isNaN(x.getTime())||Number.isNaN(y.getTime())) return null;
 return Math.max(0,Math.round((y-x)/86400000));
}
function workDuration(w){
 const start=w.recommended_date||w.recommendation_date||w.recommended_on||w.sanction_date;
 const end=w.completion_date||w.completed_date||w.completion_on;
 const days=daysBetween(start,end);
 return days==null?'Data Not Available':`${days} days`;
}
function MpPage({id}){
 const params=new URLSearchParams(location.hash.split('?')[1]||'');
 const selectedChamber=params.get('chamber')||'';
 const [d,setD]=useState(null),[err,setErr]=useState(null);
 useEffect(()=>{
   let alive=true;
   setD(null);setErr(null);
   api('/api/mp/'+encodeURIComponent(id)+(selectedChamber?'?chamber='+encodeURIComponent(selectedChamber):''))
     .then(x=>{if(alive)setD(x)})
     .catch(e=>{if(alive)setErr(e)});
   return()=>{alive=false};
 },[id,selectedChamber]);
 if(err)return h(ErrorBox,{e:err});
 if(!d)return h(Loading);
 if(!d.found)return h(Card,null,'MP profile not found.');
 const p=d.profile||{},s=d.summary||{};
 const photo=p.photo_url||p.photo||p.image_url||p.image;
 const party=p.party||p.party_name||p.political_party||'Data Not Available';
 const initials=(p.mp_name||'MP').split(/\s+/).map(x=>x[0]).slice(0,2).join('').toUpperCase();
 const sanctioned=s.sanctioned??s.total_sanctioned??s.sanctioned_amount??s.total_sanctioned_amount;
 const spent=s.expenditure??s.total_expenditure??s.amount_spent;
 const completed=s.completion??s.total_completed??s.completion_amount??s.completed_amount;
 const normal=s.NORMAL??s.normal??0;
 const review=s.REVIEW??s.review??0;
 const high=s.HIGH??s.high??0;
 const critical=s.CRITICAL??s.critical??0;
 const works=d.works||[];
 const riskRows=works.map(w=>({
   ...w,
   duration:workDuration(w),
   status:w.work_status_raw||w.work_status||w.lifecycle_status||'Data Not Available',
   reason:w.primary_reason||((w.risk_level&&w.risk_level!=='NORMAL')?'Requires human audit verification':'No primary audit signal returned')
 }));
 return h('div',null,
   Breadcrumbs({items:[{label:'Home',path:'/'},{label:p.chamber||selectedChamber||'Parliamentary House',path:'/dashboard/'+((p.chamber||selectedChamber)==='Lok Sabha' ? 'lok-sabha' : ((p.chamber||selectedChamber)==='Rajya Sabha' ? 'rajya-sabha' : 'combined'))},{label:p.state||'State',path:'/state/'+encodeURIComponent(p.state||'')+'?chamber='+encodeURIComponent(selectedChamber||p.chamber||'All')},{label:p.mp_name||'MP Profile',path:'/mp/'+id+'?chamber='+encodeURIComponent(selectedChamber||p.chamber||'All')}]}),
   h(Card,{className:'profile-hero'},
     photo?h('img',{className:'profile-photo',src:photo,alt:p.mp_name||'MP photo',onError:e=>{e.currentTarget.style.display='none';if(e.currentTarget.nextSibling)e.currentTarget.nextSibling.style.display='grid'}}):null,
     !photo&&h('div',{className:'profile-placeholder'},initials),
     photo&&h('div',{className:'profile-placeholder',style:{display:'none'}},initials),
     h('div',{className:'profile-identity'},
       h('div',{className:'eyebrow'},p.chamber||'PARLIAMENTARY HOUSE'),
       h('h2',null,p.mp_name||'Data Not Available'),
       h('p',null,`${p.state||'Data Not Available'} · ${p.chamber==='Lok Sabha'?(p.constituency||'Data Not Available'):(p.nodal_district||p.assigned_district||'Assigned / Nodal District: Data Not Available')}`),
       h('span',{className:'party-badge'},`Party: ${party}`),
       !photo&&h('small',{className:'photo-note'},'Official photo not available in the current data source; initials placeholder shown.')
     ),
     h('div',{className:'profile-actions'},h('button',{className:'secondary',onClick:()=>go('/risk-explorer?q='+encodeURIComponent(p.mp_name||''))},'View All Works'))
   ),
   h('div',{className:'profile-data-grid'},h(Metric,{label:'Total Works',value:fmt(s.total_works)}),h(Metric,{label:'Sanctioned Amount',value:cr(sanctioned)}),h(Metric,{label:'Amount Spent',value:cr(spent)}),h(Metric,{label:'Completed Amount',value:cr(completed)}),h(Metric,{label:'Critical Works',value:fmt(critical),tone:RISK.CRITICAL})),
   h('div',{className:'metrics-grid'},h(Metric,{label:'Normal',value:fmt(normal),tone:RISK.NORMAL}),h(Metric,{label:'Review',value:fmt(review),tone:RISK.REVIEW}),h(Metric,{label:'High Risk',value:fmt(high),tone:RISK.HIGH}),h(Metric,{label:'Critical',value:fmt(critical),tone:RISK.CRITICAL}),h(Metric,{label:'Total Expenditure',value:cr(spent)}),h(Metric,{label:'Works in Audit Queue',value:fmt(high+critical)})),
   h('div',{className:'grid-2'},
     h(Card,null,h('div',{className:'card-title'},h('div',null,h('h3',null,'Risk Distribution')),h('span',{className:'pill'},'MP PROFILE')),h(RiskDonut,{risk:{NORMAL:normal,REVIEW:review,HIGH:high,CRITICAL:critical}})),
     h(Card,null,h('div',{className:'card-title'},h('div',null,h('h3',null,'Work Status / Lifecycle'),h('span',null,'Actual lifecycle values returned by the backend'))),h(BarList,{items:Object.entries(d.lifecycle||{}).map(([label,value])=>({label,value}))}))
   ),
   h(Card,null,
     h('div',{className:'card-title'},h('div',null,h('h3',null,'Works Associated With This MP'),h('span',null,`${fmt(riskRows.length)} shown`))),
     h('p',{className:'section-note'},'Duration is calculated from recommendation date to completion date when both dates are available; otherwise sanction date to completion date. No audit reason is invented when the backend does not provide one.'),
     h(Table,{columns:['work_id','work_description','work_status_raw','duration','risk_level','risk_score','primary_reason'],rows:riskRows,rowClick:r=>go('/work/'+encodeURIComponent(r.work_id)),render:{work_description:r=>h('span',{className:'truncate'},r.work_description||r.description||'Data Not Available'),work_status_raw:r=>r.status,risk_level:r=>h(Badge,{level:r.risk_level}),risk_score:r=>r.risk_score==null?'Data Not Available':Number(r.risk_score).toFixed(1),primary_reason:r=>h('span',{className:'truncate'},r.reason)}})
   )
 );
}

function WorkPage({id}){
  const [d,setD]=useState(null);
  const [showDetails,setShowDetails]=useState(false);
  useEffect(()=>{api('/api/work/'+id).then(setD).catch(()=>setD({found:false}))},[id]);
  if(!d)return h(Loading); if(!d.found)return h(Card,null,'Work not found.'); const w=d.work;
  const financial=h(Card,null,h('div',{className:'card-title'},h('div',null,h('h3',null,'Work & Financials'))),h('div',{className:'detail-grid'},[
    ['MP',w.mp_name],['State',w.state_display],['Constituency / District',w.constituency||'Data Not Available'],['Category',w.work_category],['Sanctioned Amount',cr(w.sanctioned_amount)],['Total Expenditure',cr(w.total_expenditure)],['Completion Amount',cr(w.completion_amount)],['Work Status',w.work_status_raw||'Data Not Available']
  ].map(([a,b])=>h('div',{key:a},h('span',null,a),h('b',null,esc(b))))),h('div',{className:'lifecycle'},[
    ['Recommendation',w.recommended_date],['Sanction',w.sanction_date],['Expenditure',w.first_payment_date],['Completion',w.completion_date]
  ].map(([a,b],i)=>h('div',{key:a},h('span',{className:'life-dot'},i+1),h('b',null,a),h('small',null,b||'Data Not Available'),i<3&&h('i',null,'→')))));
  const evidenceData=d.evidence||{}, statistical=evidenceData.statistical||{}, ml=evidenceData.ml||{};
  const evidence=h(Card,null,h('div',{className:'card-title'},h('div',null,h('h3',null,'Technical Audit Evidence'),h('span',null,'Detailed signals used by the audit pipeline'))),h('div',{className:'evidence-block'},
    h('h4',null,'RULE-BASED SIGNALS'),((evidenceData.deterministic)||[]).map((x,i)=>h('div',{className:'evidence',key:i},'• ',x)),((evidenceData.deterministic)||[]).length===0&&h('div',{className:'evidence'},'No deterministic rule signal was returned.'),
    h('h4',null,'STATISTICAL SIGNAL'),h('div',{className:'evidence'},`Statistical Risk Score: ${esc(statistical.stat_risk_score)} · Sanction deviation: ${esc(statistical.sanc_robust_zscore)} · Expenditure deviation: ${esc(statistical.exp_robust_zscore)}`),
    h('h4',null,'ML SUPPORTING SIGNAL'),h('div',{className:'evidence'},`ML anomaly score: ${esc(ml.ml_anomaly_score)} · percentile: ${pct(ml.ml_anomaly_percentile)}`),
    h('div',{className:'human-check'},h('strong',null,'SCREENING RESULT — HUMAN VERIFICATION REQUIRED'),h('span',null,'This classification indicates potential audit-risk signals. It does not establish fraud or wrongdoing.'))
  ));
  const payments=h(Card,null,h('div',{className:'card-title'},h('div',null,h('h3',null,'Payment Information'),h('span',null,fmt((d.payments||[]).length)+' records'))),h('div',{className:'payment-grid'},[
    ['Payment Count',w.payment_count],['Vendor Count',w.vendor_count],['Duplicate Payment Indicators',w.duplicate_payment_count],['Vendor Concentration Score',w.vendor_concentration_score]
  ].map(([a,b])=>h('div',{key:a},h('span',null,a),h('b',null,esc(b))))),(d.payments||[]).length?h(Table,{columns:['expenditure_id','expenditure_date','vendor_name','payment_status','amount'],rows:d.payments}):h('div',{className:'empty'},'No expenditure records linked to this work.'));
  const co=d.cost_overrun,comp=d.compliance,pred=d.prediction,ew=d.early_warning,dupMatches=d.duplicate_matches||[];
  const complianceTone={COMPLIANT:RISK.NORMAL,'PARTIALLY COMPLIANT':RISK.REVIEW,'REQUIRES REVIEW':RISK.HIGH,'INSUFFICIENT DATA':'#667c90'};
  const priorityTone={LOW:RISK.NORMAL,MEDIUM:RISK.REVIEW,HIGH:RISK.HIGH};
  const actions=(ew&&ew.recommended_actions&&ew.recommended_actions.length)?ew.recommended_actions:(dupMatches.length?['Verify whether this work represents a separate asset from its matched pair(s).']:['Verify the flagged information against the original source documents.']);
  const gapPanel=h(Card,null,h('div',{className:'card-title'},h('div',null,h('h3',null,'Additional Audit Signals'))),h('div',{className:'evidence-block'},
    h('h4',null,'RECOMMENDED ACTION'),actions.map((a,i)=>h('div',{className:'evidence',key:i},'• ',a)),
    h('h4',null,'COMPLIANCE STATUS'),comp?h('div',{className:'three-col'},h('div',{className:'info-box'},h('b',null,'Status'),h('span',{style:{color:complianceTone[comp.status]}},comp.status)),h('div',{className:'info-box'},h('b',null,'Score'),h('span',null,comp.score==null?'Data Not Available':(comp.score+' ('+comp.passed_count+'/'+comp.total_checks+' checks)'))),h('div',{className:'info-box'},h('b',null,'Failed / Missing'),h('span',null,((comp.checks_failed||[]).length+(comp.checks_missing_data||[]).length)+' item(s)'))):h('div',{className:'evidence'},'Data Not Available'),
    comp&&(comp.checks_failed||[]).length>0&&h('div',{className:'evidence'},comp.checks_failed.map((f,i)=>h('div',{key:i},'⚠ ',f))),comp&&(comp.checks_missing_data||[]).length>0&&h('div',{className:'evidence'},comp.checks_missing_data.map((f,i)=>h('div',{key:i},'? ',f))),
    h('h4',null,'COST OVERRUN'),co&&co.determinable?h('div',{className:'three-col'},h('div',{className:'info-box'},h('b',null,'Overrun Amount'),h('span',null,cr(co.overrun_amount))),h('div',{className:'info-box'},h('b',null,'Overrun %'),h('span',null,co.overrun_percentage+'%')),h('div',{className:'info-box'},h('b',null,'Risk Band'),h('span',null,co.risk_band||'None'))):h('div',{className:'evidence'},'Cost overrun cannot be determined from available source data.'),
    h('h4',null,'PREDICTIVE RISK ESTIMATE'),pred?h('div',{className:'three-col'},h('div',{className:'info-box'},h('b',null,'Delay Risk'),h('span',null,pred.delay_risk.level)),h('div',{className:'info-box'},h('b',null,'Completion Risk'),h('span',null,pred.completion_risk.level)),h('div',{className:'info-box'},h('b',null,'Expenditure Risk'),h('span',null,pred.expenditure_risk.level))):h('div',{className:'evidence'},'Data Not Available'),
    h('h4',null,'DUPLICATE WORK SCREENING'),dupMatches.length?dupMatches.map((p,i)=>h('div',{className:'evidence',key:i},p.label+' ('+p.similarity_score+'% similarity) with ',h('a',{href:'#/work/'+encodeURIComponent(p.work_a.work_id===w.work_id?p.work_b.work_id:p.work_a.work_id)},p.work_a.work_id===w.work_id?p.work_b.work_id:p.work_a.work_id))):h('div',{className:'evidence'},'No duplicate-work matches found for this work.'),h(AuditNote)
  ));
  const level=(w.risk_level||'NORMAL').toUpperCase();
  const reasonRaw=(w.primary_reason||((evidenceData.deterministic)||[])[0]||'').trim();
  const z=Number(statistical.sanc_robust_zscore);
  const hasSanctionOutlier=Number.isFinite(z)&&Math.abs(z)>=3;
  const cleanReason=reasonRaw.replace(/^Peer Statistical Signal:\s*/i,'').replace(/^Statistical Signal:\s*/i,'').trim();
  const finding=level==='NORMAL'?'No elevated audit signal detected':(hasSanctionOutlier?'Unusual sanctioned amount detected':cleanReason||'Potential audit signal detected');
  const plainReason=level==='NORMAL'?'The verified pipeline did not return an elevated audit signal for this work.':(hasSanctionOutlier?'The sanctioned amount is significantly different from similar works in the defined peer group.':(cleanReason||'The verified pipeline identified this work for human audit review.'));
  const priority=pred&&pred.future_review_priority?pred.future_review_priority:(level==='CRITICAL'?'HIGH':level==='HIGH'?'HIGH':level==='REVIEW'?'MEDIUM':'LOW');
  const actionText=actions[0]||'Verify the flagged information against the original source documents.';
  const riskExplanation=h(Card,{className:'risk-explanation'},
    h('div',{className:'card-title'},h('div',null,h('h3',null,'Why this work needs review'),h('span',null,'Plain-language explanation of the current audit screening result')),h(Badge,{level:level})),
    h('div',{className:'explain-body'},
      h('div',{className:'risk-summary'},h('b',null,level==='NORMAL'?'No elevated signal was returned.':`Review recommended — ${finding}.`),h('div',{className:'risk-summary-text'},plainReason)),
      level!=='NORMAL'&&h('div',{className:'review-action'},h('span',null,'RECOMMENDED ACTION'),h('strong',null,actionText)),
      h('div',{className:'risk-factors'},h('div',{className:'risk-factor'},h('span',null,'Review priority'),h('b',{style:{color:priorityTone[priority]||RISK.REVIEW}},priority)),h('div',{className:'risk-factor'},h('span',null,'Primary finding'),h('b',null,finding)),h('div',{className:'risk-factor'},h('span',null,'Human verification'),h('b',null,level==='NORMAL'?'Standard review':'Required'))),
      h('div',{className:'screening-disclaimer'},h('strong',null,'SCREENING RESULT — NOT A FRAUD FINDING'),h('span',null,'This is an analytical signal for human verification. It does not establish fraud or wrongdoing.'))
    )
  );
  const detailBar=h('button',{className:'detail-toggle',onClick:()=>setShowDetails(v=>!v),ariaExpanded:showDetails},h('div',null,h('strong',null,showDetails?'Hide technical analysis':'View technical analysis'),h('span',null,'Statistical, ML, compliance, prediction and duplicate-work evidence')),h('span',null,showDetails?'▲':'▼'));
  return h('div',null,
    Breadcrumbs({items:[{label:'Home',path:'/'},{label:w.parliament_house,path:'/chamber/'+(w.parliament_house==='Lok Sabha'?'lok-sabha':'rajya-sabha')},{label:w.state_display,path:'/state/'+encodeURIComponent(w.state_display)},{label:'Work Details',path:'/work/'+id}]}),
    h('div',{className:'page-head'},h('div',null,h('h2',{className:'work-id-title'},w.work_id),h('p',{className:'work-description'},w.work_description||'Data Not Available')),h(Badge,{level:w.risk_level})),
    h('div',{className:'metrics-grid'},h(Metric,{label:'Risk Score',value:Number(w.risk_score||0).toFixed(1),tone:RISK[w.risk_level]}),h(Metric,{label:'Rule Score',value:Number(w.rule_score||0).toFixed(1)}),h(Metric,{label:'Statistical Risk',value:Number(w.stat_risk_score||0).toFixed(1)}),h(Metric,{label:'ML Percentile',value:pct(w.ml_anomaly_percentile)}),pred&&h(Metric,{label:'Future Review Priority',value:pred.future_review_priority,tone:priorityTone[pred.future_review_priority]})),
    riskExplanation,
    detailBar,
    showDetails&&h('div',{className:'detail-panel'},gapPanel,evidence),
    h('div',{className:'grid-2'},financial,payments)
  );
}
function CriticalPage(){const params=new URLSearchParams(location.hash.split('?')[1]||'');const chamber=params.get('chamber')||'All';const [d,setD]=useState(null),[q,setQ]=useState(''),[page,setPage]=useState(1);useEffect(()=>{api('/api/critical?page='+page+'&page_size=20&q='+encodeURIComponent(q)+'&chamber='+encodeURIComponent(chamber)).then(setD)},[page,q,chamber]);if(!d)return h(Loading);return h('div',null,Breadcrumbs({items:[{label:'Home',path:'/'},{label:'Critical Cases',path:'/critical'}]}),h('div',{className:'page-head'},h('div',null,h('div',{className:'eyebrow'},'PRIORITY AUDIT QUEUE'),h('h2',null,'Critical Cases'),h('p',null,`Current backend classification contains ${fmt(d.total)} CRITICAL works.`)),h('div',{className:'critical-count'},fmt(d.total))),h(Card,null,h('div',{className:'filterbar'},h('input',{value:q,onChange:e=>{setPage(1);setQ(e.target.value)},placeholder:'Search Work ID or MP Name…'})),h(WorkTable,{rows:d.rows}),h('div',{className:'pager'},h('button',{disabled:page<=1,onClick:()=>setPage(page-1)},'Previous'),h('span',null,`Page ${page} · ${d.total} critical`),h('button',{disabled:page*d.page_size>=d.total,onClick:()=>setPage(page+1)},'Next'))));}

function Explorer(){const params=new URLSearchParams(location.hash.split('?')[1]||'');const chamber=params.get('chamber')||'All';const [d,setD]=useState(null),[page,setPage]=useState(1),[q,setQ]=useState(params.get('q')||''),[risk,setRisk]=useState(params.get('risk')||'All'),[state,setState]=useState('All'),[filters,setFilters]=useState(null),[summary,setSummary]=useState(null);useEffect(()=>{api('/api/filters?chamber='+encodeURIComponent(chamber)).then(setFilters)},[chamber]);useEffect(()=>{api('/api/summary?chamber='+encodeURIComponent(chamber)).then(setSummary)},[chamber]);useEffect(()=>{const u=new URLSearchParams({page,page_size:40,q,risk,state,chamber});api('/api/works?'+u).then(setD)},[page,q,risk,state,chamber]);if(!d||!filters)return h(Loading);return h('div',null,Breadcrumbs({items:[{label:'Home',path:'/'},{label:'Risk Explorer',path:'/risk-explorer'}]}),h('div',{className:'page-head'},h('div',null,h('div',{className:'eyebrow'},(summary?fmt(summary.total_works):'')+'-WORK EXPLORER'),h('h2',null,'Risk Explorer'),h('p',null,'Server-side pagination keeps the full dataset out of the browser DOM.')),h('div',{className:'pill'},`${fmt(d.total)} matches`)),h(Card,null,h('div',{className:'filterbar'},h('input',{value:q,onChange:e=>{setPage(1);setQ(e.target.value)},placeholder:'Search Work ID or MP Name…'}),h('select',{value:state,onChange:e=>{setPage(1);setState(e.target.value)}},h('option',null,'All States'),filters.states.map(s=>h('option',{key:s},s))),h('select',{value:risk,onChange:e=>{setPage(1);setRisk(e.target.value)}},h('option',null,'All Risk Levels'),filters.risk_levels.map(s=>h('option',{key:s},s))),h('span',{className:'score-range'},`Score ${filters.score_min.toFixed(1)}–${filters.score_max.toFixed(1)}`)),h(Table,{columns:['work_id','mp_name','state','risk_score','risk_level','primary_reason'],rows:d.rows,rowClick:r=>go('/work/'+encodeURIComponent(r.work_id)),render:{risk_level:r=>h(Badge,{level:r.risk_level}),risk_score:r=>Number(r.risk_score||0).toFixed(1),primary_reason:r=>h('span',{className:'truncate'},r.primary_reason||'Data Not Available')}}),h('div',{className:'pager'},h('button',{disabled:page<=1,onClick:()=>setPage(page-1)},'Previous'),h('span',null,`Page ${page} · ${fmt(d.total)} matches`),h('button',{disabled:page*d.page_size>=d.total,onClick:()=>setPage(page+1)},'Next'))));}

function Outliers(){
 const [d,setD]=useState(null); useEffect(()=>{api('/api/quick/spending-outliers?limit=30').then(setD)},[]); if(!d)return h(Loading);
 const rows=d.rows.map(x=>({...x,primary_reason:(x.primary_reason||'Data Not Available')+' · |z|='+Number(x.abs_exp_robust_zscore||0).toFixed(2)}));
 return h('div',null,Breadcrumbs({items:[{label:'Home',path:'/'},{label:'Spending Outliers',path:'/outliers'}]}),
   h('div',{className:'page-head'},h('div',null,h('div',{className:'eyebrow'},'STATISTICAL SCREEN'),h('h2',null,'Spending Outliers'),h('p',null,d.method+'.')),h('span',{className:'pill'},'BACKEND DATA')),
   h(Card,null,h('div',{className:'card-title'},h('div',null,h('h3',null,'Highest Absolute Expenditure Robust Z-scores'),h('span',null,'Ranking only; not a fraud conclusion.'))),h(WorkTable,{rows}))
 );
}

function Methodology(){return h('div',null,Breadcrumbs({items:[{label:'Home',path:'/'},{label:'Methodology',path:'/methodology'}]}),h('div',{className:'page-head'},h('div',null,h('div',{className:'eyebrow'},'SOURCE-OF-TRUTH PIPELINE'),h('h2',null,'Methodology & Audit Guardrails'),h('p',null,'The frontend does not implement or alter anomaly detection logic. It reads the verified pipeline outputs.'))),h('div',{className:'grid-2'},h(Card,null,h('h3',null,'Risk Score Composition'),h('div',{className:'weight-list'},h('div',null,h('b',null,'50%'),h('span',null,'Rule Score')),h('div',null,h('b',null,'30%'),h('span',null,'ML Anomaly Percentile')),h('div',null,h('b',null,'20%'),h('span',null,'Statistical Risk Score')))),h(Card,null,h('h3',null,'Audit-safe terminology'),h('ul',{className:'clean-list'},['Potential Duplicate Payment','Vendor Concentration Risk','Peer Statistical Outlier','Lifecycle Gap / Data Quality Issue','ML Supporting Signal','Requires Human Audit Verification'].map(x=>h('li',{key:x},x))),h('div',{className:'human-check'},'Never present a risk classification as confirmed fraud.'))));}

// ---------------------------------------------------------------------------
// NEW: gap-closing analytics pages (duplicates, cost overruns, compliance,
// early warnings, trends, predictions). All read-only against the new
// backend/analytics.py endpoints; the existing risk pipeline is untouched.
// ---------------------------------------------------------------------------

function AuditNote({children}){return h('div',{className:'human-check'},h('strong',null,'SCREENING SIGNAL'),h('span',null,children||'This indicates a pattern worth review. It does not establish fraud or wrongdoing.'))}

function DuplicateWorkCard({p}){
 const a=p.work_a,b=p.work_b;
 return h('div',{className:'dup-pair'},
  h('div',{className:'dup-pair-head'},h('b',null,p.label+' · '+p.similarity_score+'% similarity'),h(Badge,{level:p.tier==='A'?'HIGH':'REVIEW'})),
  h('div',{className:'dup-vs'},
   [a,b].map((w,i)=>h('div',{key:i,className:'clickable',onClick:()=>go('/work/'+encodeURIComponent(w.work_id)),style:{cursor:'pointer'}},
     h('span',null,'Work '+(i===0?'A':'B')),h('b',null,w.work_id),
     h('span',null,'Description'),h('b',null,esc(w.work_description)),
     h('span',null,'MP · State'),h('b',null,esc(w.mp_name)+' · '+esc(w.state)),
     h('span',null,'Sanctioned Amount'),h('b',null,cr(w.sanctioned_amount)),
     h('span',null,'Sanction Date'),h('b',null,esc(w.sanction_date))
   ))
  ),
  h('div',{className:'dup-match-tags'},p.matching_fields.map((m,i)=>h('span',{key:i},'✓ '+m))),
  h('div',{className:'dup-action'},h('b',null,'Recommended Action: '),p.recommended_action)
 );
}

function DuplicatesPage(){
 const [summary,setSummary]=useState(null),[d,setD]=useState(null),[batches,setBatches]=useState(null),[tier,setTier]=useState('All'),[view,setView]=useState('pairs');
 useEffect(()=>{api('/api/duplicates/summary').then(setSummary)},[]);
 useEffect(()=>{setD(null);api('/api/duplicates?tier='+tier+'&limit=60').then(setD)},[tier]);
 useEffect(()=>{if(view==='batches'&&!batches)api('/api/duplicates/batches?limit=100').then(setBatches)},[view,batches]);
 return h('div',null,Breadcrumbs({items:[{label:'Home',path:'/'},{label:'Potential Duplicate Works',path:'/duplicates'}]}),
  h('div',{className:'page-head'},h('div',null,h('div',{className:'eyebrow'},'DUPLICATE WORK SCREENING'),h('h2',null,'Potential Duplicate Works'),h('p',null,'Structural + fuzzy text matching across MP, description, amount and date. Screening only — every pair requires human verification.')),summary&&h('div',{className:'pill'},fmt((summary.potential_duplicate_pairs||0)+(summary.possible_duplicate_pairs||0))+' flagged pairs')),
  summary&&h('div',{className:'metrics-grid'},
   h(Metric,{label:'Potential Duplicate (Tier A)',value:fmt(summary.potential_duplicate_pairs),tone:RISK.HIGH}),
   h(Metric,{label:'Possible Duplicate (Tier B)',value:fmt(summary.possible_duplicate_pairs),tone:RISK.REVIEW}),
   h(Metric,{label:'Batch / Repeated Patterns',value:fmt(summary.batch_pattern_groups)}),
   h(Metric,{label:'Works Inside Batch Patterns',value:fmt(summary.works_in_batch_patterns)})
  ),
  h(Card,null,h('div',{className:'filterbar'},
    h('button',{className:view==='pairs'?'primary':'secondary',onClick:()=>setView('pairs')},'Duplicate Pairs'),
    h('button',{className:view==='batches'?'primary':'secondary',onClick:()=>setView('batches')},'Batch Patterns'),
    view==='pairs'&&h('select',{value:tier,onChange:e=>setTier(e.target.value)},h('option',{value:'All'},'All Tiers'),h('option',{value:'A'},'Tier A · Potential Duplicate'),h('option',{value:'B'},'Tier B · Possible Duplicate'))
   ),
   view==='pairs'&&(!d?h(Loading):(d.pairs.length?d.pairs.map((p,i)=>h(DuplicateWorkCard,{key:i,p})):h('div',{className:'empty'},'No duplicate pairs match this filter.'))),
   view==='batches'&&(!batches?h(Loading):(batches.rows.length?batches.rows.map((bt,i)=>h('div',{className:'batch-row',key:i},h('div',null,h('b',null,esc(bt.work_description)),h('span',null,esc(bt.mp_name)+' · '+esc(bt.state)+' · '+esc(bt.sanction_date)+' · '+cr(bt.sanctioned_amount))),h('span',{className:'unit-pill'},bt.unit_count+' identical units'))):h('div',{className:'empty'},'No batch patterns found.')))
  ),
  d&&h('p',{className:'section-note'},d.method)
 );
}

function CostOverrunsPage(){
 const [summary,setSummary]=useState(null),[d,setD]=useState(null),[band,setBand]=useState('All'),[page,setPage]=useState(1);
 useEffect(()=>{api('/api/cost-overruns/summary').then(setSummary)},[]);
 useEffect(()=>{api('/api/cost-overruns?page='+page+'&page_size=25&band='+band).then(setD)},[page,band]);
 return h('div',null,Breadcrumbs({items:[{label:'Home',path:'/'},{label:'Cost Overrun Analysis',path:'/cost-overruns'}]}),
  h('div',{className:'page-head'},h('div',null,h('div',{className:'eyebrow'},'SANCTIONED VS ACTUAL'),h('h2',null,'Cost Overrun Analysis'),h('p',null,'Compares sanctioned amount against completion/expenditure amount. Never inferred from sanctioned amount alone.'))),
  summary&&h('div',{className:'metrics-grid'},
   h(Metric,{label:'Overrun Determinable',value:fmt(summary.overrun_determinable_count)}),
   h(Metric,{label:'Cannot Be Determined',value:fmt(summary.overrun_not_determinable_count)}),
   h(Metric,{label:'Overruns Flagged',value:fmt(summary.overrun_flagged_count),tone:RISK.HIGH}),
   h(Metric,{label:'Total Overrun Amount',value:cr(summary.total_overrun_amount)})
  ),
  summary&&h(Card,null,h('div',{className:'card-title'},h('div',null,h('h3',null,'Risk Bands'),h('span',null,summary.band_thresholds_pct.note))),h('div',{className:'three-col'},['LOW','MEDIUM','HIGH'].map(b=>h('div',{className:'info-box',key:b},h('b',null,b),h('span',null,fmt((summary.band_counts||{})[b]||0)+' works'))))),
  h(Card,null,h('div',{className:'filterbar'},h('select',{value:band,onChange:e=>{setPage(1);setBand(e.target.value)}},h('option',{value:'All'},'All Bands'),h('option',{value:'LOW'},'LOW'),h('option',{value:'MEDIUM'},'MEDIUM'),h('option',{value:'HIGH'},'HIGH'))),
   !d?h(Loading):h(Table,{columns:['work_id','mp_name','sanctioned_amount','overrun_amount','overrun_percentage','risk_band'],rows:d.rows.map(r=>({work_id:r.work_id,mp_name:r.mp_name,sanctioned_amount:cr(r.cost_overrun.sanctioned_amount),overrun_amount:cr(r.cost_overrun.overrun_amount),overrun_percentage:r.cost_overrun.overrun_percentage+'%',risk_band:r.cost_overrun.risk_band,_id:r.work_id})),rowClick:r=>go('/work/'+encodeURIComponent(r._id)),render:{risk_band:r=>h(Badge,{level:r.risk_band==='HIGH'?'HIGH':r.risk_band==='MEDIUM'?'REVIEW':'NORMAL'})}}),
   d&&h('div',{className:'pager'},h('button',{disabled:page<=1,onClick:()=>setPage(page-1)},'Previous'),h('span',null,`Page ${page} · ${fmt(d.total)} flagged`),h('button',{disabled:page*d.page_size>=d.total,onClick:()=>setPage(page+1)},'Next'))
  )
 );
}

function CompliancePage(){
 const [summary,setSummary]=useState(null),[d,setD]=useState(null),[status,setStatus]=useState('All'),[page,setPage]=useState(1);
 useEffect(()=>{api('/api/compliance/summary').then(setSummary)},[]);
 useEffect(()=>{api('/api/compliance?page='+page+'&page_size=25&status='+status).then(setD)},[page,status]);
 const statuses=['COMPLIANT','PARTIALLY COMPLIANT','REQUIRES REVIEW','INSUFFICIENT DATA'];
 const tone={COMPLIANT:RISK.NORMAL,'PARTIALLY COMPLIANT':RISK.REVIEW,'REQUIRES REVIEW':RISK.HIGH,'INSUFFICIENT DATA':'#667c90'};
 return h('div',null,Breadcrumbs({items:[{label:'Home',path:'/'},{label:'Compliance Monitoring',path:'/compliance'}]}),
  h('div',{className:'page-head'},h('div',null,h('div',{className:'eyebrow'},'AUTOMATED COMPLIANCE ENGINE'),h('h2',null,'Compliance Monitoring'),h('p',null,'Data-availability and process checks — never invents government rules the data cannot support.'))),
  summary&&h('div',{className:'metrics-grid'},statuses.map(s=>h(Metric,{key:s,label:s,value:fmt((summary.status_counts||{})[s]||0),tone:tone[s]}))),
  h(Card,null,h('div',{className:'filterbar'},h('select',{value:status,onChange:e=>{setPage(1);setStatus(e.target.value)}},h('option',{value:'All'},'All Statuses'),statuses.map(s=>h('option',{key:s,value:s},s)))),
   !d?h(Loading):h(Table,{columns:['work_id','mp_name','status','score','passed_count'],rows:d.rows.map(r=>({work_id:r.work_id,mp_name:r.mp_name,status:r.compliance.status,score:r.compliance.score==null?'Data Not Available':r.compliance.score,passed_count:r.compliance.passed_count+' / '+r.compliance.total_checks,_id:r.work_id})),rowClick:r=>go('/work/'+encodeURIComponent(r._id)),render:{status:r=>h('span',{className:'badge',style:{color:tone[r.status],borderColor:tone[r.status]+'66',background:tone[r.status]+'14'}},r.status)}}),
   d&&h('div',{className:'pager'},h('button',{disabled:page<=1,onClick:()=>setPage(page-1)},'Previous'),h('span',null,`Page ${page} · ${fmt(d.total)} works`),h('button',{disabled:page*d.page_size>=d.total,onClick:()=>setPage(page+1)},'Next'))
  )
 );
}

function EarlyWarningsPage(){
 const [summary,setSummary]=useState(null),[d,setD]=useState(null),[severity,setSeverity]=useState('All'),[page,setPage]=useState(1);
 useEffect(()=>{api('/api/early-warnings/summary').then(setSummary)},[]);
 useEffect(()=>{api('/api/early-warnings?page='+page+'&page_size=20&severity='+severity).then(setD)},[page,severity]);
 const tone={'Immediate Review':RISK.CRITICAL,'Priority Review':RISK.HIGH,'Monitor':RISK.REVIEW};
 return h('div',null,Breadcrumbs({items:[{label:'Home',path:'/'},{label:'Early Warnings',path:'/early-warnings'}]}),
  h('div',{className:'page-head'},h('div',null,h('div',{className:'eyebrow'},'COMBINED SIGNAL LAYER'),h('h2',null,'Early Warnings'),h('p',null,'Combines existing risk classification with duplicate, cost-overrun and compliance signals. Informational — never an accusation.'))),
  summary&&h('div',{className:'metrics-grid'},
   h(Metric,{label:'Total Flagged',value:fmt(summary.total_flagged)}),
   h(Metric,{label:'Immediate Review',value:fmt(summary.severity_counts['Immediate Review']),tone:RISK.CRITICAL}),
   h(Metric,{label:'Priority Review',value:fmt(summary.severity_counts['Priority Review']),tone:RISK.HIGH}),
   h(Metric,{label:'Monitor',value:fmt(summary.severity_counts['Monitor']),tone:RISK.REVIEW})
  ),
  h(Card,null,h('div',{className:'filterbar'},h('select',{value:severity,onChange:e=>{setPage(1);setSeverity(e.target.value)}},h('option',{value:'All'},'All Severities'),h('option',null,'Immediate Review'),h('option',null,'Priority Review'),h('option',null,'Monitor'))),
   !d?h(Loading):(d.rows.length?d.rows.map((w,i)=>h('div',{key:i,className:'batch-row',style:{cursor:'pointer'},onClick:()=>go('/work/'+encodeURIComponent(w.work_id))},
     h('div',null,h('b',null,w.work_id+' · '+esc(w.mp_name)),h('span',null,w.reasons.join(' · ')),h('div',{className:'signal-tags'},w.signals.map((s,j)=>h('span',{className:'signal-tag',key:j},s)))),
     h('span',{className:'severity-badge',style:{color:tone[w.severity],background:tone[w.severity]+'18',border:'1px solid '+tone[w.severity]+'55'}},w.severity)
   )):h('div',{className:'empty'},'No works match this filter.')),
   d&&h('div',{className:'pager'},h('button',{disabled:page<=1,onClick:()=>setPage(page-1)},'Previous'),h('span',null,`Page ${page} · ${fmt(d.total)} flagged`),h('button',{disabled:page*d.page_size>=d.total,onClick:()=>setPage(page+1)},'Next'))
  )
 );
}

function TrendsPage(){
 const [metric,setMetric]=useState('sanctions'),[d,setD]=useState(null);
 useEffect(()=>{setD(null);api('/api/trends?metric='+metric).then(setD)},[metric]);
 const metrics=[['sanctions','Sanctions Over Time'],['expenditure','Expenditure Over Time'],['completions','Completions Over Time'],['risk','Risk Distribution Over Time']];
 const valueKey=metric==='sanctions'?'sanctioned_amount':metric==='expenditure'?'amount':metric==='completions'?'completion_amount':null;
 return h('div',null,Breadcrumbs({items:[{label:'Home',path:'/'},{label:'Trend Analysis',path:'/trends'}]}),
  h('div',{className:'page-head'},h('div',null,h('div',{className:'eyebrow'},'TEMPORAL ANALYSIS'),h('h2',null,'Trend Analysis'),h('p',null,'Only periods present in the source data are shown. No fabricated or interpolated periods.'))),
  h(Card,null,
   h('div',{className:'trend-select'},h('select',{value:metric,onChange:e=>setMetric(e.target.value)},metrics.map(([v,l])=>h('option',{key:v,value:v},l)))),
   !d?h(Loading):(!d.series.length?h('div',{className:'empty'},d.note||'No data available for this metric.'):
     metric==='risk'
       ?h(Table,{columns:['month','NORMAL','REVIEW','HIGH','CRITICAL'],rows:d.series.map(r=>({month:r.month,NORMAL:r.NORMAL||0,REVIEW:r.REVIEW||0,HIGH:r.HIGH||0,CRITICAL:r.CRITICAL||0}))})
       :h(BarList,{items:d.series.map(r=>({label:r.month,value:r[valueKey]||0})),money:true})
   )
  )
 );
}

function PredictionsPage(){
 const [summary,setSummary]=useState(null),[d,setD]=useState(null),[priority,setPriority]=useState('All'),[page,setPage]=useState(1);
 useEffect(()=>{api('/api/predictions/summary').then(setSummary)},[]);
 useEffect(()=>{api('/api/predictions?page='+page+'&page_size=25&priority='+priority).then(setD)},[page,priority]);
 const tone={LOW:RISK.NORMAL,MEDIUM:RISK.REVIEW,HIGH:RISK.HIGH};
 return h('div',null,Breadcrumbs({items:[{label:'Home',path:'/'},{label:'Predictive Insights',path:'/predictions'}]}),
  h('div',{className:'page-head'},h('div',null,h('div',{className:'eyebrow'},'RISK ESTIMATE — NOT A GUARANTEED PREDICTION'),h('h2',null,'Predictive Insights'),h('p',null,'Transparent, rule-based forward-looking risk estimates derived from existing pipeline features. This is not the ML anomaly model and not a guaranteed prediction.'))),
  summary&&h('div',{className:'metrics-grid'},
   h(Metric,{label:'Review Priority: HIGH',value:fmt((summary.review_priority_counts||{}).HIGH),tone:RISK.HIGH}),
   h(Metric,{label:'Review Priority: MEDIUM',value:fmt((summary.review_priority_counts||{}).MEDIUM),tone:RISK.REVIEW}),
   h(Metric,{label:'Delay Risk: MEDIUM+',value:fmt(((summary.delay_risk_counts||{}).MEDIUM||0)+((summary.delay_risk_counts||{}).HIGH||0))}),
   h(Metric,{label:'Completion Risk: MEDIUM+',value:fmt(((summary.completion_risk_counts||{}).MEDIUM||0)+((summary.completion_risk_counts||{}).HIGH||0))})
  ),
  h(Card,null,h('div',{className:'filterbar'},h('select',{value:priority,onChange:e=>{setPage(1);setPriority(e.target.value)}},h('option',{value:'All'},'All Review Priorities'),h('option',{value:'HIGH'},'HIGH'),h('option',{value:'MEDIUM'},'MEDIUM'),h('option',{value:'LOW'},'LOW'))),
   !d?h(Loading):h(Table,{columns:['work_id','mp_name','delay_risk','completion_risk','expenditure_risk','future_review_priority'],rows:d.rows.map(r=>({work_id:r.work_id,mp_name:r.mp_name,delay_risk:r.prediction.delay_risk.level,completion_risk:r.prediction.completion_risk.level,expenditure_risk:r.prediction.expenditure_risk.level,future_review_priority:r.prediction.future_review_priority,_id:r.work_id})),rowClick:r=>go('/work/'+encodeURIComponent(r._id)),render:{future_review_priority:r=>h('span',{className:'badge',style:{color:tone[r.future_review_priority],borderColor:tone[r.future_review_priority]+'66',background:tone[r.future_review_priority]+'14'}},r.future_review_priority)}}),
   d&&h('div',{className:'pager'},h('button',{disabled:page<=1,onClick:()=>setPage(page-1)},'Previous'),h('span',null,`Page ${page} · ${fmt(d.total)} works`),h('button',{disabled:page*d.page_size>=d.total,onClick:()=>setPage(page+1)},'Next'))
  )
 );
}

function App(){const route=useRoute();let page;if(route==='/')return h(React.Fragment,null,h('style',null,APP_CSS),h(ChamberChooser));else if(route==='/dashboard/lok-sabha')page=h(Home,{chamber:'Lok Sabha'});else if(route==='/dashboard/rajya-sabha')page=h(Home,{chamber:'Rajya Sabha'});else if(route==='/dashboard/combined')page=h(Home,{chamber:'All'});else if(route==='/critical')page=h(CriticalPage);else if(route.startsWith('/risk-explorer'))page=h(Explorer);else if(route==='/outliers')page=h(Outliers);else if(route==='/duplicates')page=h(DuplicatesPage);else if(route==='/cost-overruns')page=h(CostOverrunsPage);else if(route==='/compliance')page=h(CompliancePage);else if(route==='/early-warnings')page=h(EarlyWarningsPage);else if(route==='/trends')page=h(TrendsPage);else if(route==='/predictions')page=h(PredictionsPage);else if(route==='/methodology')page=h(Methodology);else if(route.startsWith('/state/')){const raw=route.slice('/state/'.length).split('?')[0];page=h(StatePage,{name:decodeURIComponent(raw)});}else if(route.startsWith('/mp/')){const raw=route.slice('/mp/'.length).split('?')[0];page=h(MpPage,{id:decodeURIComponent(raw)});}else if(route.startsWith('/work/')){const raw=route.slice('/work/'.length).split('?')[0];page=h(WorkPage,{id:decodeURIComponent(raw)});}else if(route==='/chamber/lok-sabha')page=h(Home,{chamber:'Lok Sabha'});else if(route==='/chamber/rajya-sabha')page=h(Home,{chamber:'Rajya Sabha'});else page=h(Home);return h(React.Fragment,null,h('style',null,APP_CSS),h(Layout,{route},page))}
ReactDOM.render(h(App),document.getElementById('root'));
