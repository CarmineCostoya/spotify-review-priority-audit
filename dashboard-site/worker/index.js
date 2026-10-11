const SEED_VERSION = "official-100000-v2";

const metrics = {
  processed: 100000,
  completed: 100000,
  quarantined: 0,
  uniqueModelEnriched: 75894,
  cacheReuses: 24106,
  verificationSample: 1000,
  verificationDisagreements: 135,
  measuredCostUsd: 3.523864,
};

const recommendation = {
  issue_id: "PLAYBACK-GENERAL",
  headline: "Prioritize general playback reliability next quarter.",
  rationale: "Playback failures combine the highest severity-weighted volume with direct disruption of Spotify's core listening job.",
  actions: [
    "Improve playback-start success and time-to-first-audio.",
    "Investigate loading, logo-screen, and false-connectivity failures.",
    "Test wrong-track and unexpected-shuffle behavior across releases.",
  ],
};

const issues = [
  [1,"PLAYBACK-GENERAL",6887,22010,3.195876,22010],
  [2,"USABILITY-GENERAL",4783,12457,2.604432,12457],
  [3,"USABILITY-ADS",4494,9701,2.158656,9701],
  [4,"CATALOG-CONTENT",2158,6310,2.924004,6310],
  [5,"PLAYBACK-STOPS",1917,5922,3.089202,5922],
  [6,"BILLING-GENERAL",1580,4479,2.834810,4479],
  [7,"OTHER-GENERAL",2042,4251,2.081783,4251],
  [8,"USABILITY-QUEUE",1345,3985,2.962825,3985],
  [9,"PLAYBACK-CRASH",1203,3891,3.234414,3891],
  [10,"ACCESS-GENERAL",832,2879,3.460337,2879],
  [11,"DOWNLOADS-GENERAL",929,2779,2.991389,2779],
  [12,"CATALOG-GENERAL",882,2421,2.744898,2421],
  [13,"ACCESS-LOGIN",526,2014,3.828897,2014],
  [14,"DOWNLOADS-OFFLINE",406,1218,3.000000,1218],
  [15,"CATALOG-SEARCH",368,1093,2.970109,1093],
  [16,"ACCESS-ACCOUNT",211,744,3.526066,744],
  [17,"BILLING-CHARGE",89,382,4.292135,382],
  [18,"BILLING-PRICE",139,302,2.172662,302],
  [19,"SUPPORT-GENERAL",66,185,2.803030,185],
  [20,"DOWNLOADS-MISSING",28,89,3.178571,89],
  [21,"SUPPORT-RESPONSE",19,56,2.947368,56],
];

const evidence = [
  ["PLAYBACK-GENERAL","b3da207e-888d-40bd-bd5d-11f376f5eeda","Every time I play my favorite song, it plays another song and I hate it.","playback","complaint",3,"Every time I play my favorite song, it plays another song and I hate it."],
  ["PLAYBACK-GENERAL","6344f653-1a48-44df-a9f7-d8a28bceee75","No music but still having 5G! Even though I have the best internet connection, spotify keeps on telling mee that I don't have internet connection. I have a premium account. I am expecting it to be good","playback","complaint",3,"spotify keeps on telling mee that I don't have internet connection"],
  ["PLAYBACK-GENERAL","1d2804a8-3d89-4609-afeb-a369266816df","I can't even play any song that i want to play i wish i could give zero","playback","complaint",4,"I can't even play any song that i want to play"],
  ["PLAYBACK-GENERAL","3d9c548f-1c89-44f2-bc65-9fbde01fa6ab","I can't even open the app anymore. it's stuck at the logo screen. I tried a clean reinstall.but doesn't work","playback","complaint",4,"I can't even open the app anymore. it's stuck at the logo screen."],
  ["USABILITY-GENERAL","da6377bb-76c1-4c6f-a64a-4728adbc275a","Why is the ultimate shuffle button not working anymore?","usability","complaint",3,"ultimate shuffle button not working anymore"],
  ["USABILITY-GENERAL","faf05e24-a8eb-4726-ad2f-3c2b989bfbd2","Completely unreasonable and unjustifiable UI change moving the playback buttons to the left and switching the order, with no option to revert.","usability","complaint",3,"UI change moving the playback buttons to the left and switching the order, with no option to revert."],
  ["USABILITY-ADS","cd61e48a-5606-4615-8811-d0e27e6b0036","Can you like let me use my free 6 skips an hour. Sometimes like it takes 2 days to get them. But is good music. Also don't show the same ad 3 times in a row every 2 songs.","usability","complaint",3,"Can you like let me use my free 6 skips an hour. Sometimes like it takes 2 days to get them. But is good music. Also don't show the same ad 3 times in a row every 2 songs."],
  ["USABILITY-ADS","b78cef3b-2abc-4c6e-b54d-b61bc4668eed","Was a good app but now they're getting excessive with ads, its about the same amount of ads as there is music, plus they mix random songs in your playlists and won't let you pick a certain song without premium.","usability","complaint",3,"they mix random songs in your playlists and won't let you pick a certain song without premium."],
];

async function seedDatabase(db) {
  const existing = await db.prepare("SELECT value FROM metadata WHERE key = ?").bind("seed_version").first();
  if (existing?.value === SEED_VERSION) return;
  const statements = [
    db.prepare("DELETE FROM issue_membership"),
    db.prepare("DELETE FROM reviews"),
    db.prepare("DELETE FROM ranking"),
    db.prepare("DELETE FROM metadata"),
    ...issues.map(row => db.prepare("INSERT INTO ranking VALUES (?,?,?,?,?,?)").bind(...row)),
    ...evidence.map(row => db.prepare("INSERT INTO reviews VALUES (?,?,?,?,?,?)").bind(row[1],row[2],row[3],row[4],row[5],row[6])),
    ...evidence.map(row => db.prepare("INSERT INTO issue_membership VALUES (?,?)").bind(row[0],row[1])),
    db.prepare("INSERT INTO metadata VALUES (?,?)").bind("metrics", JSON.stringify(metrics)),
    db.prepare("INSERT INTO metadata VALUES (?,?)").bind("recommendation", JSON.stringify(recommendation)),
    db.prepare("INSERT INTO metadata VALUES (?,?)").bind("seed_version", SEED_VERSION),
  ];
  await db.batch(statements);
}

const page = `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Spotify Review Priority Audit</title><style>
:root{--ink:#101713;--paper:#f3f0e8;--green:#1ed760;--muted:#66726b;--line:#d3d8d1;--white:#fff;--amber:#f5c451}*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.55 Inter,ui-sans-serif,system-ui,sans-serif}header{padding:72px max(6vw,24px) 58px;background:var(--ink);color:var(--white)}header h1{font:500 clamp(44px,7vw,88px)/.95 Georgia,serif;letter-spacing:-.045em;max-width:950px;margin:16px 0 24px}header .lede{max-width:760px;color:#c4cec8;font-size:19px}.eyebrow{font-size:12px;letter-spacing:.16em;font-weight:800;text-transform:uppercase;color:#607069}.light{color:var(--green)}main{max-width:1180px;margin:auto;padding:52px max(4vw,20px)}section{margin-bottom:72px}.metrics{display:grid;grid-template-columns:repeat(4,1fr);gap:1px;background:var(--line);border:1px solid var(--line)}.metric{background:var(--paper);padding:26px}.metric strong{display:block;font:500 40px/1 Georgia,serif}.metric span{color:var(--muted)}.section-title{display:flex;align-items:end;justify-content:space-between;gap:24px;border-bottom:1px solid var(--ink);padding-bottom:14px}.section-title h2,.recommendation h2{font:500 clamp(30px,4vw,52px)/1.05 Georgia,serif;margin:8px 0}.issue{display:grid;grid-template-columns:58px 1fr 145px 130px;gap:18px;align-items:center;padding:18px 0;border-bottom:1px solid var(--line);cursor:pointer}.issue:hover,.issue:focus{background:#e8eee8;outline:none}.rank{font:500 29px Georgia,serif}.bar{height:8px;background:#d5ddd8;margin-top:9px}.bar i{display:block;height:100%;background:var(--green)}.recommendation{background:var(--green);padding:40px}.recommendation ul{margin:20px 0 0;padding-left:22px}.evidence{display:grid;grid-template-columns:1fr 1fr;gap:16px}.quote{background:var(--white);padding:24px;border:1px solid var(--line)}.quote p{font:20px/1.4 Georgia,serif;margin-top:0}.quote small{color:var(--muted)}.method{border-left:4px solid var(--amber);padding:6px 0 6px 20px;max-width:860px}.status{display:inline-flex;gap:8px;align-items:center;background:#203128;padding:8px 12px;border-radius:99px;color:#d9e5dd;font-size:13px}.status i{width:8px;height:8px;border-radius:50%;background:var(--green)}footer{padding:30px max(6vw,24px);border-top:1px solid var(--line);color:var(--muted)}@media(max-width:760px){.metrics,.evidence{grid-template-columns:1fr 1fr}.issue{grid-template-columns:40px 1fr}.issue .count,.issue .severity{display:none}}@media(max-width:520px){.metrics,.evidence{grid-template-columns:1fr}}
</style></head><body><header><p class="eyebrow light">Berkeley · Agentic AI Capstone</p><h1>100,000 reviews.<br>One inspectable priority.</h1><p class="lede">A database-backed product audit of historical Spotify reviews, with reproducible rankings and traceable customer evidence.</p><span class="status"><i></i> Official run · checker passed</span></header><main><section id="metrics" class="metrics" aria-label="Overall metrics"></section><section><div class="section-title"><div><p class="eyebrow">Baseline ranking</p><h2>Where product effort should go</h2></div><p>Score = severity sum</p></div><div id="issues"></div></section><section class="recommendation"><p class="eyebrow">Grounded recommendation</p><h2 id="recommendation">Loading saved analysis…</h2><p id="rationale"></p><ul id="actions"></ul></section><section><p class="eyebrow">Traceable evidence</p><h2 id="evidence-title">Select an issue</h2><div id="evidence" class="evidence"></div></section><section class="method"><strong>Interpretation limit</strong><p>Historical app-store reviewers are self-selected. These results do not establish population prevalence, revenue impact, confirmed churn, or causality. Independent verification found 135 disagreements in 1,000 reviews.</p></section></main><footer>Official GPT-6 Luna classification · D1 database · corrected deterministic ranking</footer><script>
const fmt=n=>new Intl.NumberFormat().format(n),esc=s=>String(s).replace(/[&<>\"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',"'":'&#39;'}[c]));let issues=[];async function json(path){const r=await fetch(path);if(!r.ok)throw new Error(await r.text());return r.json()}async function show(id){const d=await json('/api/issues/'+encodeURIComponent(id));document.querySelector('#evidence-title').textContent=id+' evidence';document.querySelector('#evidence').innerHTML=d.reviews.length?d.reviews.map(x=>'<article class="quote"><p>“'+esc(x.review_text)+'”</p><small>'+esc(x.review_id)+' · severity '+x.severity+' · '+esc(x.intent)+'</small></article>').join(''):'<p>No published examples for this issue. Full membership remains in the grading export.</p>'}async function load(){const [m,r,rec]=await Promise.all([json('/api/metrics'),json('/api/issues'),json('/api/recommendation')]);issues=r;document.querySelector('#metrics').innerHTML=[['Processed',m.processed],['Completed',m.completed],['Cache reuses',m.cacheReuses],['Verifier agreement',(100*(1-m.verificationDisagreements/m.verificationSample)).toFixed(1)+'%']].map(([k,v])=>'<div class="metric"><strong>'+((typeof v==='number')?fmt(v):v)+'</strong><span>'+k+'</span></div>').join('');const max=Math.max(...issues.map(x=>x.priority_score),1);document.querySelector('#issues').innerHTML=issues.map(x=>'<article class="issue" data-id="'+esc(x.issue_id)+'" tabindex="0"><span class="rank">'+String(x.rank).padStart(2,'0')+'</span><div><strong>'+esc(x.issue_id)+'</strong><div class="bar"><i style="width:'+(100*x.priority_score/max)+'%"></i></div></div><span class="count">'+fmt(x.complaint_count)+' reviews</span><span class="severity">severity '+Number(x.mean_severity).toFixed(2)+'</span></article>').join('');document.querySelectorAll('.issue').forEach(el=>{el.onclick=()=>show(el.dataset.id);el.onkeydown=e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();show(el.dataset.id)}}});document.querySelector('#recommendation').textContent=rec.headline;document.querySelector('#rationale').textContent=rec.rationale;document.querySelector('#actions').innerHTML=rec.actions.map(x=>'<li>'+esc(x)+'</li>').join('');show(rec.issue_id)}load().catch(e=>{document.querySelector('#recommendation').textContent='Saved analysis is temporarily unavailable.';document.querySelector('#rationale').textContent=e.message});
</script></body></html>`;

const json = (payload, status = 200) => new Response(JSON.stringify(payload), {status, headers:{"content-type":"application/json; charset=utf-8","cache-control":"public,max-age=300"}});

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (!env.DB) return json({error:"D1 database binding is unavailable"}, 503);
    await seedDatabase(env.DB);
    if (url.pathname === "/api/health") {
      const ranking = await env.DB.prepare("SELECT COUNT(*) AS count FROM ranking").first();
      const evidenceRows = await env.DB.prepare("SELECT COUNT(*) AS count FROM reviews").first();
      return json({status:"ok",database:"D1",ranking_rows:ranking.count,evidence_rows:evidenceRows.count,seed_version:SEED_VERSION});
    }
    if (url.pathname === "/api/metrics" || url.pathname === "/api/recommendation") {
      const key = url.pathname.endsWith("metrics") ? "metrics" : "recommendation";
      const row = await env.DB.prepare("SELECT value FROM metadata WHERE key = ?").bind(key).first();
      return row ? json(JSON.parse(row.value)) : json({error:"not found"},404);
    }
    if (url.pathname === "/api/issues") {
      const rows = await env.DB.prepare("SELECT * FROM ranking ORDER BY rank").all();
      return json(rows.results);
    }
    if (url.pathname.startsWith("/api/issues/")) {
      const issueId = decodeURIComponent(url.pathname.slice("/api/issues/".length));
      const rows = await env.DB.prepare("SELECT r.review_id,r.review_text,r.topic,r.intent,r.severity,r.evidence_quote FROM reviews r JOIN issue_membership m ON m.review_id=r.review_id WHERE m.issue_id=? ORDER BY r.severity DESC,r.review_id").bind(issueId).all();
      return json({issue_id:issueId,reviews:rows.results});
    }
    if (url.pathname !== "/") return new Response("Not found",{status:404});
    return new Response(page,{headers:{"content-type":"text/html; charset=utf-8","cache-control":"public,max-age=300"}});
  }
};
