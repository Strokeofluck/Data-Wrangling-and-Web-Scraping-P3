'use strict';
const P=window.P3, $=id=>document.getElementById(id);
const repo='https://github.com/Strokeofluck/Data-Wrangling-and-Web-Scraping-P3/blob/main/';
let chamber='House',selectedSource=null,page=0,filtered=[],returnFocus=null;
const fmt=n=>n==null?'—':Number(n).toLocaleString('en-US');
function node(tag,text,className){const n=document.createElement(tag);if(text!=null)n.textContent=text;if(className)n.className=className;return n;}
function showView(name){
  if(!['sources','join','data','notes'].includes(name))name='sources';
  document.querySelectorAll('.view').forEach(n=>n.hidden=n.id!==name);
  document.querySelectorAll('[data-view]').forEach(n=>n.setAttribute('aria-pressed',String(n.dataset.view===name)));
  history.replaceState(null,'','#'+name);
}
document.querySelectorAll('[data-view]').forEach(n=>n.addEventListener('click',()=>showView(n.dataset.view)));
window.addEventListener('hashchange',()=>showView(location.hash.slice(1)));
function openExplanation(key,before='See source code',after='See validated output'){
  const e=P.explanations[key];if(!e)return;
  returnFocus=document.activeElement;
  $('popup-title').textContent=e.title;$('popup-why').textContent=e.why;
  $('popup-before').textContent=before;$('popup-after').textContent=after;
  $('popup-code').textContent=e.code;
  $('popup-location').textContent=`${e.file} · lines ${e.line}–${e.end}${e.partial?' · excerpt; open the file for the complete function':''}`;
  $('popup-link').href=repo+e.file+'#L'+e.line;
  $('explanation').showModal();
}
$('close-popup').addEventListener('click',()=>$('explanation').close());
$('explanation').addEventListener('close',()=>returnFocus?.focus());
$('explanation').addEventListener('click',e=>{if(e.target===$('explanation')){const r=e.target.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)e.target.close();}});
function chamberSources(){return P.sources.filter(n=>n.chamber===chamber);}
function renderChamber(){
  document.querySelectorAll('[data-chamber]').forEach(n=>n.setAttribute('aria-pressed',String(n.dataset.chamber===chamber)));
  $('filing').replaceChildren(...chamberSources().map(s=>{const o=node('option',s.name);o.value=s.id;return o;}));
  renderSource();
}
function sourceFieldButton(field){
  const button=node('button',field.label);button.type='button';
  button.addEventListener('click',()=>openExplanation(`${chamber}:${field.key}`,field.before,field.after));
  return button;
}
function renderSource(){
  selectedSource=chamberSources().find(s=>s.id===$('filing').value)||chamberSources()[0];
  const source=selectedSource;$('document').replaceChildren();$('field-list').replaceChildren();
  $('original').href=source.original;$('local-source').href=source.archive;
  $('document-kind').textContent=chamber==='House'?'ACTUAL PDF · ARCHIVED SOURCE':'OFFICIAL HTML · LOCAL READING VIEW';
  $('source-caption').textContent=source.caption;
  $('source-context').replaceChildren(node('strong',source.politician),node('span',chamber==='House'?`Filing ${source.id} · ${fmt(source.rows)} extracted report row${source.rows===1?'':'s'} · Page ${source.page}`:`Filed ${source.filing_date} · ${source.total_rows} original table rows`));
  if(chamber==='House'){
    const sheet=node('div',null,'pdf-sheet');const img=node('img');img.src=source.image;img.alt=`Archived House disclosure for ${source.politician}, filing ${source.id}`;
    img.width=source.width;img.height=source.height;sheet.append(img);
    source.fields.forEach(field=>{
      const b=node('button',null,'hotspot');b.type='button';b.setAttribute('aria-label',`Explain ${field.label}`);b.dataset.label=field.label;
      const [x0,y0,x1,y1]=field.rect;
      Object.assign(b.style,{left:`${x0/source.width*100}%`,top:`${y0/source.height*100}%`,width:`${(x1-x0)/source.width*100}%`,height:`${(y1-y0)/source.height*100}%`});
      b.addEventListener('click',()=>openExplanation(`House:${field.key}`,field.before,field.after));sheet.append(b);
      $('field-list').append(sourceFieldButton(field));
    });$('document').append(sheet);
  }else{
    const sheet=node('div',null,'senate-sheet');
    sheet.append(node('div','UNITED STATES SENATE · FINANCIAL DISCLOSURES','agency'),node('h3','Periodic Transaction Report'),node('div',source.politician,'filer-name'),node('p',`Filed ${source.filing_date}`,'filed'),node('h4','Transactions'));
    const table=node('table',null,'senate-table'),thead=node('thead'),hr=node('tr');
    ['#','Transaction date','Owner','Ticker','Asset name','Asset type','Type','Amount','Comment'].forEach(label=>hr.append(node('th',label)));thead.append(hr);table.append(thead);
    const tbody=node('tbody'),fields=[];
    const definitions={1:['transaction_date','Transaction date'],2:['owner','Owner'],3:['asset','Asset & ticker'],6:['transaction_type','Transaction type'],7:['amount','Amount range']};
    source.table.forEach((row,index)=>{
      const tr=node('tr');row.forEach((value,col)=>{
        const td=node('td',value||'—');
        if(index===0&&definitions[col]){
          const [key,label]=definitions[col],field={key,label,before:value||'(blank in source)',after:col===1?value.split('/').reverse().join(' / '):value||'(kept blank)'};
          if(col===1){const [m,d,y]=value.split('/');field.after=`${y}-${m.padStart(2,'0')}-${d.padStart(2,'0')}`;}
          const b=node('button',null,'cell-hotspot');b.setAttribute('aria-label',`Explain ${label}`);b.addEventListener('click',()=>openExplanation(`Senate:${key}`,field.before,field.after));td.append(b);fields.push(field);
        }tr.append(td);
      });tbody.append(tr);
    });table.append(tbody);sheet.append(table,node('p',`Readable excerpt from archived official HTML · ${Math.min(6,source.total_rows)} of ${source.total_rows} rows shown. Source text is retained; appearance is simplified.`,'source-note'));
    $('document').append(sheet);fields.forEach(f=>$('field-list').append(sourceFieldButton(f)));
  }
  $('document').scrollTop=0;$('document').scrollLeft=0;
}
document.querySelectorAll('[data-chamber]').forEach(n=>n.addEventListener('click',()=>{chamber=n.dataset.chamber;renderChamber();}));
$('filing').addEventListener('change',renderSource);
$('overlays').addEventListener('change',()=>{$('document').classList.toggle('hide-overlays',!$('overlays').checked);});
function renderJoin(){
  const s=P.summary,d=s.design;
  const flows=[['HOUSE SUMMARY',d.left_rows,'ticker-month keys'],['SENATE SUMMARY',d.right_rows,'ticker-month keys'],['OUTER JOIN',d.expected_rows,'unique keys retained']];
  flows.forEach((f,index)=>{if(index)$('join-flow').append(node('span',index===1?'+':'→','flow-arrow'));const div=node('div',null,'flow-node');div.append(node('span',f[0]),node('strong',fmt(f[1])),node('p',f[2]));$('join-flow').append(div);});
  [['Keys','ticker + calendar month (2025)'],['Left grain',d.left_grain],['Right grain',d.right_grain],['Relationship','One-to-one after aggregation'],['Expected rows',fmt(d.expected_rows)+' = union of both key sets'],['Join type','Outer: retain both sources’ unmatched keys'],['Missing values','Keep NA; a missing report is not an observed zero']].forEach(([a,b])=>{const div=node('div');div.append(node('dt',a),node('dd',b));$('design').append(div);});
  $('merge-code').textContent=P.explanations.merge.code;
  $('coverage').append(node('h3','Where the 3,760 combined keys come from'));
  [['House only',d.left_only],['Senate only',d.right_only],['Both chambers',d.both]].forEach(([label,value])=>{const row=node('div',null,'coverage-row'),track=node('div',null,'bar-track'),bar=node('div',null,'bar-fill');bar.style.width=(value/d.expected_rows*100)+'%';track.append(bar);row.append(node('span',label),track,node('strong',fmt(value)));$('coverage').append(row);});
  $('coverage').append(node('p',`Denominator: ${fmt(d.expected_rows)} unique ticker-month keys. “Only” describes these archives, not all actual trading.`,'quiet'));
  P.failures.forEach(f=>{const div=node('article',null,'failure');div.append(node('span','CAUGHT AS EXPECTED'),node('h3',f.title),node('code',`${f.caught}: ${f.message}`));$('failure-cases').append(div);});
  s.checks.forEach(text=>$('checks').append(node('li',text)));
}
$('explain-merge').addEventListener('click',()=>openExplanation('merge','House + Senate summaries',`${fmt(P.summary.design.expected_rows)} unique ticker-month keys`));
$('explain-acquisition').addEventListener('click',()=>openExplanation('acquisition','A finite source URL inventory','Verified immutable responses on disk'));
function applyFilters(){
  const query=$('ticker-search').value.trim().toUpperCase(),month=$('month-filter').value,match=$('match-filter').value;
  filtered=P.rows.filter(r=>(!query||r.ticker.includes(query))&&(!month||r.month===month)&&(!match||r._merge===match));page=0;$('lineage').hidden=true;renderRows();
}
function renderRows(){
  const size=12,start=page*size;$('results').replaceChildren();
  filtered.slice(start,start+size).forEach(row=>{
    const tr=node('tr');[row.ticker,row.month,fmt(row.house_reports),fmt(row.senate_reports)].forEach(v=>tr.append(node('td',v)));
    const td=node('td');td.append(node('span',row._merge==='both'?'Both chambers':row._merge==='left_only'?'House only':'Senate only','coverage-tag '+(row._merge==='both'?'both':'')));tr.append(td);
    const evidence=node('td'),b=node('button','Trace rows ↗');b.setAttribute('aria-label',`Trace ${row.ticker} ${row.month} source rows`);b.addEventListener('click',()=>showLineage(row));evidence.append(b);tr.append(evidence);$('results').append(tr);
  });
  if(!filtered.length){const tr=node('tr'),td=node('td','No keys match these filters.','empty');td.colSpan=6;tr.append(td);$('results').append(tr);}
  $('result-count').textContent=fmt(filtered.length)+' matching keys';$('page-label').textContent=`${filtered.length?start+1:0}–${Math.min(start+size,filtered.length)} of ${fmt(filtered.length)}`;
  $('previous').disabled=page===0;$('next').disabled=start+size>=filtered.length;
}
function showLineage(row){
  const panel=$('lineage');panel.replaceChildren();panel.hidden=false;
  const close=node('button','Close evidence');close.className='text-button';close.addEventListener('click',()=>panel.hidden=true);panel.append(close,node('h3',`${row.ticker} · ${row.month} — source records`));
  const records=P.lineage[`${row.ticker}|${row.month}`]||[];
  panel.append(node('p',`${records.length} disclosed report rows. Links can repeat when a filing reports several transactions. Amendments are retained; these are not deduplicated economic trades.`));
  const ul=node('ul');records.forEach(r=>{const li=node('li');li.append(document.createTextNode(`${r.chamber} · ${r.person} · ${r.date} · ${r.action} · `));const a=node('a',`Filing ${r.id}, row ${r.row}`);a.href=r.url;a.target='_blank';a.rel='noopener';li.append(a);ul.append(li);});panel.append(ul);panel.scrollIntoView({block:'nearest',behavior:'auto'});
}
['ticker-search','month-filter','match-filter'].forEach(id=>$(id).addEventListener(id==='ticker-search'?'input':'change',applyFilters));
$('previous').addEventListener('click',()=>{page--;renderRows();});$('next').addEventListener('click',()=>{page++;renderRows();});
[...new Set(P.rows.map(r=>r.month))].sort().forEach(m=>{const option=node('option',m);option.value=m;$('month-filter').append(option);});
renderChamber();renderJoin();applyFilters();showView(location.hash.slice(1));
