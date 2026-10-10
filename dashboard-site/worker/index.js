const snapshot = {
  metrics: { processed: 100000, completed: 100000, quarantined: 0, cacheReuses: 24106 },
  issues: [
    [1,"OTHER-GENERAL",3679,2.048655,7537],
    [2,"CATALOG-CONTENT",2902,2.122329,6159],
    [3,"PLAYBACK-GENERAL",2123,2.243994,4764],
    [4,"USABILITY-ADS",1539,2.086420,3211],
    [5,"PLAYBACK-CRASH",1018,3.009823,3064],
    [6,"BILLING-GENERAL",1241,2.214343,2748],
    [7,"PLAYBACK-STOPS",979,2.628192,2573],
    [8,"DOWNLOADS-GENERAL",498,2.124498,1058]
  ].map(([rank,issue_id,complaint_count,mean_severity,priority_score])=>({rank,issue_id,complaint_count,mean_severity,priority_score})),
  recommendation: "Development finding only: inspect OTHER-GENERAL and improve the taxonomy before treating it as a product priority. Catalog and playback are the leading specific issue families.",
};

const page = `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Spotify Review Priority Audit</title><style>
:root{--ink:#0e1915;--paper:#f3f0e7;--green:#1ed760;--muted:#66736d;--line:#d6d8d0;--white:#fff;--amber:#ffd166}*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font-family:Inter,ui-sans-serif,system-ui,sans-serif}.notice{background:var(--amber);padding:12px max(6vw,24px);font-weight:750}header{padding:62px max(6vw,24px) 52px;background:var(--ink);color:var(--white)}header h1{font-family:Georgia,serif;font-size:clamp(42px,7vw,88px);font-weight:500;letter-spacing:-.045em;line-height:.95;max-width:900px;margin:16px 0}header>p:last-child{color:#b7c2bd;font-size:18px}.eyebrow{font-size:12px;letter-spacing:.16em;font-weight:800;color:#5f6f68}.eyebrow.light{color:var(--green)}main{max-width:1180px;margin:auto;padding:48px max(4vw,20px)}section{margin-bottom:66px}.metrics{display:grid;grid-template-columns:repeat(4,1fr);gap:1px;background:var(--line);border:1px solid var(--line)}.metric{background:var(--paper);padding:26px}.metric strong{display:block;font-family:Georgia,serif;font-size:42px;font-weight:500}.metric span{color:var(--muted)}.section-title{display:flex;align-items:end;justify-content:space-between;gap:24px;border-bottom:1px solid var(--ink);padding-bottom:14px}.section-title h2,.recommendation h2{font-family:Georgia,serif;font-size:clamp(30px,4vw,50px);font-weight:500;margin:8px 0}.issue{display:grid;grid-template-columns:58px 1fr 145px 130px;gap:18px;align-items:center;padding:19px 0;border-bottom:1px solid var(--line)}.rank{font-family:Georgia,serif;font-size:29px}.bar{height:8px;background:#d5ddd8;margin-top:9px}.bar i{display:block;height:100%;background:var(--green)}.recommendation{background:var(--green);padding:38px}.recommendation .eyebrow{color:var(--ink)}.note{border-left:4px solid var(--amber);padding:4px 0 4px 20px;max-width:850px;color:#3f4a45}footer{padding:28px max(6vw,24px);border-top:1px solid var(--line);color:var(--muted)}@media(max-width:760px){.metrics{grid-template-columns:1fr 1fr}.issue{grid-template-columns:40px 1fr}.issue .count,.issue .severity{display:none}}
</style></head><body><div class="notice">Development preview — the 100,000 rows below use a deterministic test classifier, not the final paid model run.</div><header><p class="eyebrow light">BERKELEY • AGENTIC AI CAPSTONE</p><h1>Spotify Review Priority Audit</h1><p>An inspectable path from source reviews to product priorities.</p></header><main><section id="metrics" class="metrics"></section><section><div class="section-title"><div><p class="eyebrow">BASELINE RANKING</p><h2>Where product effort should go</h2></div><p>Priority score = severity sum</p></div><div id="issues"></div></section><section class="recommendation"><p class="eyebrow">GROUNDED RECOMMENDATION</p><h2 id="recommendation"></h2></section><section class="note"><strong>Interpretation limit</strong><p>This development snapshot proves data flow, accounting, ranking, and dashboard behavior. It must be replaced with evaluated model outputs before submission. Historical app-store reviews do not establish revenue impact, confirmed churn, or causality.</p></section></main><footer>Saved snapshot generated from the auditable pipeline • 100,000 selected nonempty reviews</footer><script>
const f=n=>new Intl.NumberFormat().format(n);fetch('/api/snapshot').then(r=>r.json()).then(d=>{const m=d.metrics;document.querySelector('#metrics').innerHTML=[['Processed',m.processed],['Completed',m.completed],['Quarantined',m.quarantined],['Exact-text reuses',m.cacheReuses]].map(([k,v])=>'<div class="metric"><strong>'+f(v)+'</strong><span>'+k+'</span></div>').join('');const max=Math.max(...d.issues.map(x=>x.priority_score),1);document.querySelector('#issues').innerHTML=d.issues.map(x=>'<article class="issue"><span class="rank">'+String(x.rank).padStart(2,'0')+'</span><div><strong>'+x.issue_id+'</strong><div class="bar"><i style="width:'+(100*x.priority_score/max)+'%"></i></div></div><span class="count">'+f(x.complaint_count)+' reviews</span><span class="severity">severity '+x.mean_severity.toFixed(2)+'</span></article>').join('');document.querySelector('#recommendation').textContent=d.recommendation});
</script></body></html>`;

export default {
  async fetch(request) {
    const path = new URL(request.url).pathname;
    if (path === "/api/health") return Response.json({status:"ok", source:"saved-development-snapshot"});
    if (path === "/api/snapshot") return Response.json(snapshot, {headers:{"cache-control":"public,max-age=300"}});
    if (path !== "/") return new Response("Not found", {status:404});
    return new Response(page, {headers:{"content-type":"text/html; charset=utf-8"}});
  }
};
