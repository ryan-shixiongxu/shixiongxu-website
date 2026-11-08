const tabs=[...document.querySelectorAll('nav a')];
function route(){const hash=location.hash.replace('#','');const page=['home','cv','research'].includes(hash)?hash:'home';document.querySelectorAll('.page').forEach(el=>el.hidden=el.id!==page);tabs.forEach(a=>{a.classList.toggle('active',a.dataset.page===page);if(a.dataset.page===page)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current')});document.title=`${page==='home'?'Home':page==='cv'?'CV':'Research'} | Shixiong Xu`;window.scrollTo(0,0)}
window.addEventListener('hashchange',route);route();document.querySelector('#year').textContent=new Date().getFullYear();
let papers=[];
let monthlySummaries={};
const paperRoot=document.querySelector('#papers');
const overview=document.querySelector('#monthly-overview');
const topicFilter=document.querySelector('#topic-filter');
const sortFilter=document.querySelector('#sort-filter');
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const fullMonth=ym=>{if(!/^\d{4}-\d{2}$/.test(ym))return ym;const [year,month]=ym.split('-').map(Number);return new Date(Date.UTC(year,month-1,1)).toLocaleDateString('en-US',{month:'long',year:'numeric',timeZone:'UTC'})};
function render(){
  const topic=topicFilter.value;
  const sort=sortFilter.value;
  const rows=papers.filter(p=>topic==='all'||(Array.isArray(p.topics)&&p.topics.includes(topic))).sort((a,b)=>{
    if(sort==='relevance')return (Number(b.score)||0)-(Number(a.score)||0)||String(b.date||'').localeCompare(String(a.date||''));
    return (sort==='oldest'?1:-1)*String(a.date||'').localeCompare(String(b.date||''));
  }).slice(0,20);
  const latestMonth=papers.map(p=>String(p.date||'').slice(0,7)).filter(x=>/^\d{4}-\d{2}$/.test(x)).sort().at(-1);
  const entry=monthlySummaries[latestMonth];
  // The monthly overview is generated for all themes. Hide it on topic-specific views to avoid misrepresenting its scope.
  if(topic==='all'&&entry&&entry.summary){
    const count=Number(entry.paper_count)||0;
    overview.hidden=false;
    overview.innerHTML=`<h3>${esc(fullMonth(latestMonth))} · Monthly AI Summary</h3><p>${esc(entry.summary)}</p><p class="summary-footnote">Based on ${count} indexed paper abstract${count===1?'':'s'}.</p>`;
  }else{
    overview.hidden=true;
    overview.replaceChildren();
  }
  if(!rows.length){
    paperRoot.innerHTML='<p class="research-empty">No papers found yet for this topic. The feed will appear after the first successful update.</p>';
    return;
  }
  paperRoot.innerHTML=rows.map(p=>{
    const url=/^https:\/\//.test(p.url||'')?esc(p.url):null;
    const authors=(Array.isArray(p.authors)?p.authors:[]).filter(Boolean);
    const metadata=[authors.slice(0,6).join(', ')+(authors.length>6?', et al.':''),p.venue,p.date].filter(Boolean).map(esc).join(' · ');
    const summary=p.ai_summary?`<p class="paper-label">AI Summary</p><p class="paper-description">${esc(p.ai_summary)}</p>`:'';
    const abstract=p.abstract?`<details class="paper-abstract"><summary>Abstract</summary><p>${esc(p.abstract)}</p></details>`:'<p class="paper-unavailable">Abstract not available from OpenAlex.</p>';
    return `<article class="research-paper"><h3>${url?`<a href="${url}" target="_blank" rel="noopener noreferrer">${esc(p.title)}</a>`:esc(p.title)}</h3><p class="paper-meta">${metadata}</p>${summary}${abstract}</article>`;
  }).join('');
}
topicFilter.addEventListener('change',render);
sortFilter.addEventListener('change',render);
fetch('papers.json',{cache:'no-store'}).then(r=>{if(!r.ok)throw Error('No feed');return r.json()}).then(data=>{papers=Array.isArray(data.papers)?data.papers:[];monthlySummaries=data.monthly_summaries&&typeof data.monthly_summaries==='object'?data.monthly_summaries:{};render()}).catch(()=>render());
