'use strict';
const P=window.P3, $=id=>document.getElementById(id);
const repo='https://github.com/Strokeofluck/Data-Wrangling-and-Web-Scraping-P3/blob/main/';
let chamber='House',selectedSource=null,page=0,filtered=[],returnFocus=null;
let journey=[],journeyIndex=0;
let renderedCodeFile=null;
let pageSize=10,resultSort={key:'transaction_date',direction:-1},columnQueries={};
const tableCollator=new Intl.Collator('en-US',{numeric:true,sensitivity:'base'});
const fmt=n=>n==null?'—':Number(n).toLocaleString('en-US');
function node(tag,text,className){const n=document.createElement(tag);if(text!=null)n.textContent=text;if(className)n.className=className;return n;}
let tooltipOwner=null;
function hideFieldTooltip(){
  const tip=$('field-tooltip');if(tip)tip.hidden=true;
  tooltipOwner?.removeAttribute('aria-describedby');tooltipOwner=null;
}
function showFieldTooltip(button,key,field){
  if($('explanation').open)return;
  const explanation=P.explanations[key],tip=$('field-tooltip');if(!explanation||!tip)return;
  hideFieldTooltip();tooltipOwner=button;button.setAttribute('aria-describedby','field-tooltip');
  const context=field.row&&field.row!=='metadata'?` · row ${field.row}`:'';
  tip.replaceChildren(node('strong',field.label+context),node('span',field.origin||(field.source_only?'Source column · not exported':'Extracted source field'),'hover-status'));
  const before=String(field.before).replace(/\s+/g,' '),after=String(field.after).replace(/\s+/g,' ');
  tip.append(node('p',`Source: ${before.length>180?before.slice(0,180)+'…':before}`),node('p',`Result: ${after.length>200?after.slice(0,200)+'…':after}`),node('p',explanation.why));
  const first=explanation.steps?.[0];
  if(first){const line=first.focus?.[0]||first.line;tip.append(node('code',`${first.file}:${line}\n${(P.code_files?.[first.file]||[])[line-1]||''}`));}
  tip.append(node('span','Click or press Enter to browse the full code →','hover-action'));
  tip.hidden=false;const rect=button.getBoundingClientRect(),height=tip.offsetHeight,width=tip.offsetWidth;
  tip.style.left=Math.max(8,Math.min(innerWidth-width-8,rect.left))+'px';
  tip.style.top=Math.max(8,Math.min(innerHeight-height-8,rect.bottom+height+12<innerHeight?rect.bottom+8:rect.top-height-8))+'px';
}
function bindSourceField(button,key,field){
  button.dataset.field=field.key;button.dataset.row=field.row||'';
  if(field.source_only)button.classList.add('source-only');
  button.addEventListener('click',()=>openExplanation(key,field.before,field.after,button));
  button.addEventListener('pointerenter',event=>{if(event.pointerType!=='touch')showFieldTooltip(button,key,field);});
  button.addEventListener('pointerleave',hideFieldTooltip);
  button.addEventListener('focus',()=>showFieldTooltip(button,key,field));
  button.addEventListener('blur',hideFieldTooltip);
}
function showView(name){
  if(!['sources','join','data','notes'].includes(name))name='sources';
  if($('explanation').open)$('explanation').close();
  document.querySelectorAll('.view').forEach(n=>n.hidden=n.id!==name);
  document.querySelectorAll('[data-view]').forEach(n=>n.setAttribute('aria-pressed',String(n.dataset.view===name)));
  history.replaceState(null,'','#'+name);
}
document.querySelectorAll('[data-view]').forEach(n=>n.addEventListener('click',()=>showView(n.dataset.view)));
window.addEventListener('hashchange',()=>showView(location.hash.slice(1)));
function revealSourceField(target){
  if(!target)return;
  const pane=$('document'),box=pane.getBoundingClientRect(),field=target.getBoundingClientRect();
  if(field.top<box.top+24||field.bottom>box.bottom-24)pane.scrollTop+=field.top-box.top-pane.clientHeight*.38;
  if(field.left<box.left+16||field.right>box.right-16)pane.scrollLeft+=field.left-box.left-(pane.clientWidth-field.width)/2;
}
function openExplanation(key,before='See source code',after='See validated output',sourceButton=null){
  const e=P.explanations[key];if(!e)return;
  hideFieldTooltip();
  returnFocus=document.activeElement;
  document.querySelectorAll('.active-source').forEach(n=>{n.classList.remove('active-source');n.removeAttribute('aria-current');});
  const panel=$('explanation'),workspace=document.querySelector('.workspace'),isSource=/^(House|Senate):/.test(key);
  workspace.classList.toggle('inspecting',isSource);panel.dataset.placement=isSource?'source':'page';
  (isSource?workspace:document.body).append(panel);
  let target=null;
  if(isSource){
    target=sourceButton?.closest('#document')?sourceButton:[...$('document').querySelectorAll('[data-field]')].find(n=>n.dataset.field===sourceButton?.dataset.field&&n.dataset.row===sourceButton?.dataset.row);
    if(target){target.classList.add('active-source');target.setAttribute('aria-current','true');}
  }
  $('popup-title').textContent=e.title;$('popup-why').textContent=e.why;
  $('popup-before').textContent=before;$('popup-after').textContent=after;
  journey=e.steps||[e];journeyIndex=0;
  $('journey-steps').replaceChildren(...journey.map((step,index)=>{
    const button=node('button',`${index+1}`);button.type='button';button.title=step.title;
    button.setAttribute('aria-label',`Step ${index+1}: ${step.title}`);
    button.addEventListener('click',()=>renderJourney(index));return button;
  }));
  if(!panel.open)panel.show();
  panel.scrollTop=0;renderJourney(0);
  if(isSource){workspace.scrollIntoView({block:'start',behavior:'instant'});requestAnimationFrame(()=>revealSourceField(target));}
}
function highlightConcept(id){
  $('popup-code').querySelectorAll('[data-concepts]').forEach(part=>part.classList.toggle('concept-active',Boolean(id)&&part.dataset.concepts.split(' ').includes(id)));
  $('popup-code').querySelectorAll('.explanation-term').forEach(term=>term.classList.toggle('term-active',term.dataset.concept===id));
}
let codeTooltipOwner=null;
function hideCodeTooltip(){
  $('code-tooltip').hidden=true;codeTooltipOwner?.removeAttribute('aria-describedby');codeTooltipOwner=null;
}
function showCodeMeaning(part,link,note){
  hideCodeTooltip();hideFieldTooltip();highlightConcept(link.id);
  const tip=$('code-tooltip');codeTooltipOwner=part;part.setAttribute('aria-describedby','code-tooltip');
  const label=link.phrase.charAt(0).toUpperCase()+link.phrase.slice(1);
  tip.replaceChildren(node('strong',label),node('code',link.code),node('p',note.meaning),node('span',`Line ${note.line} · matching words highlighted below`,'hover-status'));
  tip.hidden=false;
  const rect=part.getBoundingClientRect(),height=tip.offsetHeight,width=tip.offsetWidth;
  tip.style.left=Math.max(8,Math.min(innerWidth-width-8,rect.left))+'px';
  tip.style.top=Math.max(8,Math.min(innerHeight-height-8,rect.top-height-8>=8?rect.top-height-8:rect.bottom+8))+'px';
}
function renderLineMeaning(row,text,note){
  const links=(note.links||[]).map((link,index)=>({...link,id:`L${note.line}T${index}`}));
  const source=row.querySelector('.source-text'),cuts=[...new Set([0,text.length,...links.flatMap(link=>[link.start,link.end])])].sort((a,b)=>a-b);
  source.replaceChildren(...cuts.slice(0,-1).map((start,index)=>{
    const end=cuts[index+1],part=node('span',text.slice(start,end));
    const matches=links.filter(link=>link.start<=start&&link.end>=end);
    if(matches.length){
      part.dataset.concepts=matches.map(link=>link.id).join(' ');
      if(part.textContent.trim()&&(/\w/.test(part.textContent)||matches.some(link=>link.code.trim()===part.textContent.trim()))){
        // Prefer the specific value over an overlapping whole-statement verb.
        const link=[...matches].sort((a,b)=>(a.end-a.start)-(b.end-b.start))[0];
        part.classList.add('code-term');part.tabIndex=0;part.dataset.concept=link.id;
        part.setAttribute('role','button');part.setAttribute('aria-label',`Explain code: ${part.textContent.trim()} (line ${note.line})`);
        part.addEventListener('pointerenter',()=>showCodeMeaning(part,link,note));
        part.addEventListener('pointerleave',()=>{hideCodeTooltip();highlightConcept(document.activeElement?.dataset.concept||null);});
        part.addEventListener('focus',()=>{
          if($('explanation').dataset.placement==='source')document.querySelector('.workspace').scrollIntoView({block:'start',behavior:'instant'});
          requestAnimationFrame(()=>{if(document.activeElement===part)showCodeMeaning(part,link,note);});
        });
        part.addEventListener('blur',()=>{hideCodeTooltip();highlightConcept(null);});
        part.addEventListener('click',()=>showCodeMeaning(part,link,note));
        part.addEventListener('keydown',event=>{
          if(event.key==='Escape'&&!$('code-tooltip').hidden){event.preventDefault();event.stopPropagation();hideCodeTooltip();highlightConcept(null);}
          else if(event.key==='Enter'||event.key===' '){event.preventDefault();showCodeMeaning(part,link,note);}
        });
      }
    }
    return part;
  }));
  const meaning=node('span',null,'line-explanation');meaning.append(node('strong','In plain English'));
  const matches=[];
  [...links].sort((a,b)=>b.phrase.length-a.phrase.length).forEach(link=>{
    const escaped=link.phrase.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');
    const pattern=new RegExp(`(^|\\W)(${escaped})(?=$|\\W)`,'gi');let match;
    while((match=pattern.exec(note.meaning))){
      const start=match.index+match[1].length,end=start+match[2].length;
      if(!matches.some(other=>start<other.end&&end>other.start))matches.push({start,end,link});
    }
  });
  let cursor=0;
  matches.sort((a,b)=>a.start-b.start).forEach(({start,end,link})=>{
    meaning.append(document.createTextNode(note.meaning.slice(cursor,start)));
    const term=node('button',note.meaning.slice(start,end),'explanation-term');term.type='button';term.dataset.concept=link.id;
    term.title=`Highlights: ${link.code}`;
    term.addEventListener('pointerenter',()=>highlightConcept(link.id));
    term.addEventListener('pointerleave',()=>highlightConcept(document.activeElement===term?link.id:null));
    term.addEventListener('focus',()=>{highlightConcept(link.id);if($('explanation').dataset.placement==='source')document.querySelector('.workspace').scrollIntoView({block:'start',behavior:'instant'});});
    term.addEventListener('blur',()=>highlightConcept(null));
    term.addEventListener('click',()=>highlightConcept(link.id));
    meaning.append(term);cursor=end;
  });
  meaning.append(document.createTextNode(note.meaning.slice(cursor)));row.append(meaning);
}
function renderJourney(index){
  if(index<0||index>=journey.length)return;
  hideCodeTooltip();
  journeyIndex=index;const step=journey[index],focus=new Set(step.focus||[step.line]);
  $('journey-title').textContent=step.title;$('journey-why').textContent=step.why;
  $('journey-count').textContent=`Step ${index+1} of ${journey.length}`;
  $('popup-filename').textContent=step.file;
  const fullFile=P.code_files?.[step.file],lines=fullFile||step.code.split('\n'),firstLine=fullFile?1:step.line;
  if(renderedCodeFile!==step.file){
    $('popup-code').replaceChildren(...lines.map((text,offset)=>{
      const number=firstLine+offset,row=node('span',null,'code-line');row.dataset.line=number;
      const gutter=node('span',String(number),'line-number');gutter.setAttribute('aria-hidden','true');
      row.append(gutter,node('code',text||' ','source-text'));return row;
    }));
    renderedCodeFile=step.file;
  }
  $('popup-code').querySelectorAll('.line-explanation').forEach(note=>note.remove());
  $('popup-code').querySelectorAll('.focused').forEach(row=>{
    row.classList.remove('focused');const number=Number(row.dataset.line);row.querySelector('.source-text').textContent=lines[number-firstLine]||' ';
  });
  focus.forEach(number=>$('popup-code').querySelector(`[data-line="${number}"]`)?.classList.add('focused'));
  (step.line_notes||[]).forEach(note=>{
    const row=$('popup-code').querySelector(`[data-line="${note.line}"]`);
    if(row)renderLineMeaning(row,lines[note.line-firstLine]||' ',note);
  });
  $('popup-location').textContent=`Entire file: ${fmt(lines.length)} lines · step ${step.line}–${step.end} · highlighted lines ${[...focus].join(', ')}`;
  $('popup-link').href=repo+step.file+'#L'+Math.min(...focus);
  const activeControl=document.activeElement;
  $('journey-back').disabled=index===0;$('journey-next').disabled=index===journey.length-1;
  if(activeControl===$('journey-next')&&$('journey-next').disabled)$('journey-back').focus({preventScroll:true});
  if(activeControl===$('journey-back')&&$('journey-back').disabled)$('journey-next').focus({preventScroll:true});
  [...$('journey-steps').children].forEach((button,i)=>{
    if(i===index)button.setAttribute('aria-current','step');else button.removeAttribute('aria-current');
  });
  // Scroll only the code pane, keeping the step explanation and arrows visible.
  requestAnimationFrame(()=>{
    if($('explanation').dataset.placement==='source')document.querySelector('.workspace').scrollIntoView({block:'start',behavior:'instant'});
    const pane=$('popup-code'),target=pane.querySelector('.focused');
    if(target){const delta=target.getBoundingClientRect().top-pane.getBoundingClientRect().top;pane.scrollTop=Math.max(0,pane.scrollTop+delta-pane.clientHeight*.30);}
    pane.scrollLeft=0;
  });
}
$('jump-to-code').addEventListener('click',()=>renderJourney(journeyIndex));
$('journey-back').addEventListener('click',()=>renderJourney(journeyIndex-1));
$('journey-next').addEventListener('click',()=>renderJourney(journeyIndex+1));
$('explanation').addEventListener('keydown',event=>{
  if(event.key==='Escape'){event.preventDefault();$('explanation').close();}
  else if(event.key==='ArrowLeft'||event.key==='ArrowRight'){
    event.preventDefault();renderJourney(journeyIndex+(event.key==='ArrowLeft'?-1:1));
  }
});
$('close-popup').addEventListener('click',()=>$('explanation').close());
$('popup-code').addEventListener('scroll',hideCodeTooltip,{passive:true});
window.addEventListener('scroll',hideCodeTooltip,{passive:true});
window.addEventListener('resize',hideCodeTooltip);
document.addEventListener('keydown',event=>{if(event.key==='Escape'&&$('explanation').open)$('explanation').close();});
$('explanation').addEventListener('close',()=>{
  hideCodeTooltip();
  document.querySelector('.workspace').classList.remove('inspecting');
  document.querySelectorAll('.active-source').forEach(n=>{n.classList.remove('active-source');n.removeAttribute('aria-current');});
  document.body.append($('explanation'));
  if(returnFocus?.isConnected)returnFocus.focus({preventScroll:true});
});
function chamberSources(){return P.sources.filter(n=>n.chamber===chamber);}
function renderChamber(filingId=null){
  document.querySelectorAll('[data-chamber]').forEach(n=>n.setAttribute('aria-pressed',String(n.dataset.chamber===chamber)));
  $('filing').replaceChildren(...chamberSources().map(s=>{const o=node('option',s.name);o.value=s.id;return o;}));
  const available=chamberSources();
  $('filing').value=(available.find(source=>source.id===filingId)||available[Math.floor(Math.random()*available.length)]).id;
  renderSource();
}
function sourceFieldButton(field){
  const button=node('button',field.label);button.type='button';
  bindSourceField(button,`${chamber}:${field.key}`,field);
  return button;
}
function renderSource(){
  if($('explanation').open)$('explanation').close();
  hideFieldTooltip();
  selectedSource=chamberSources().find(s=>s.id===$('filing').value)||chamberSources()[0];
  const source=selectedSource;$('document').replaceChildren();$('field-list').replaceChildren();
  $('original').href=source.original;$('local-source').href=source.archive;
  $('document-kind').textContent=chamber==='House'?'ACTUAL PDF · CAPTURED SOURCE':'OFFICIAL HTML · CAPTURED SOURCE';
  $('filing-status').textContent=chamber==='House'?`${chamberSources().length} parsed House filings from the captured 2025 filing-index collection · 66 additional PDFs have no parsed rows · not a complete official census`:`${chamberSources().length} captured electronic Senate filings across the saved collection’s dates · comparison uses 2025 transaction dates`;
  $('source-caption').textContent=source.caption;
  $('source-context').replaceChildren(node('strong',source.politician),node('span',chamber==='House'?`Filing ${source.id} · ${fmt(source.rows)} extracted report row${source.rows===1?'':'s'} · Page ${source.page}`:`Filed ${source.filing_date} · ${source.total_rows} original table rows`));
  if(chamber==='House'){
    const sheet=node('div',null,'pdf-sheet');const img=node('img');img.src=source.image;img.alt=`Captured House disclosure for ${source.politician}, filing ${source.id}`;
    img.width=source.width;img.height=source.height;sheet.append(img);
    const seen=new Set();
    source.fields.forEach(field=>{
      const first=!seen.has(field.key),b=node('button',null,'hotspot');b.type='button';b.setAttribute('aria-label',`Explain ${field.label}${first?'':', row '+field.row}`);b.dataset.label=field.label;
      const [x0,y0,x1,y1]=field.rect;
      Object.assign(b.style,{left:`${x0/source.width*100}%`,top:`${y0/source.height*100}%`,width:`${(x1-x0)/source.width*100}%`,height:`${(y1-y0)/source.height*100}%`});
      bindSourceField(b,`House:${field.key}`,field);sheet.append(b);
      if(first)$('field-list').append(sourceFieldButton(field));seen.add(field.key);
    });$('document').append(sheet);
  }else{
    const sheet=node('div',null,'senate-sheet');
    sheet.append(node('div','UNITED STATES SENATE · FINANCIAL DISCLOSURES','agency'));
    [['report_title','Report title','h3',source.report_title],['politician','Filer name','div',source.politician],['filing_date','Filing date','p',source.filing_date]].forEach(([key,label,tag,value])=>{
      const block=node(tag,null,key==='politician'?'filer-name':key==='filing_date'?'filed':'report-title');
      const button=node('button',key==='filing_date'?`Filed ${value}`:value,'metadata-hotspot');button.type='button';button.setAttribute('aria-label',`Explain ${label}`);
      const field={key,label,before:value,after:value,row:'metadata',origin:'Captured Senate filing index'};
      bindSourceField(button,`Senate:${key}`,field);block.append(button);sheet.append(block);$('field-list').append(sourceFieldButton(field));
    });
    sheet.append(node('h4','Transactions'));
    const table=node('table',null,'senate-table'),thead=node('thead'),hr=node('tr');
    ['#','Transaction date','Owner','Ticker','Asset name','Asset type','Type','Amount','Comment'].forEach(label=>hr.append(node('th',label)));thead.append(hr);table.append(thead);
    const tbody=node('tbody'),fields=[];
    const definitions={0:['item_number','Filing item'],1:['transaction_date','Transaction date'],2:['owner','Owner'],3:['ticker','Ticker'],4:['asset_name','Asset name'],5:['asset_type','Asset type'],6:['transaction_type','Transaction type'],7:['amount','Amount range'],8:['comment','Comment']};
    source.table.forEach((row,index)=>{
      const tr=node('tr');row.forEach((value,col)=>{
        const td=node('td',value||'—');
        if(definitions[col]){
          const [key,label]=definitions[col],field={key,label,before:value||'(blank in source)',after:col===1?value.split('/').reverse().join(' / '):value||'(kept blank)'};
          if(col===1){const [m,d,y]=value.split('/');field.after=`${y}-${m.padStart(2,'0')}-${d.padStart(2,'0')}`;}
          field.row=String(row[0]||index+1);
          const b=node('button',null,'cell-hotspot');b.setAttribute('aria-label',`Explain ${label}${index===0?'':', row '+field.row}`);bindSourceField(b,`Senate:${key}`,field);td.append(b);if(index===0)fields.push(field);
        }tr.append(td);
      });tbody.append(tr);
    });table.append(tbody);sheet.append(table,node('p',`Captured official HTML · all ${source.total_rows} transaction rows shown. Name, filing date, and report title come from the captured Senate filing index. Agency and section headings are fixed display labels. Hover or click an outlined value to follow its code.`,'source-note'));
    $('document').append(sheet);fields.forEach(f=>$('field-list').append(sourceFieldButton(f)));
  }
  $('document').scrollTop=0;$('document').scrollLeft=0;
}
document.querySelectorAll('[data-chamber]').forEach(n=>n.addEventListener('click',()=>{chamber=n.dataset.chamber;renderChamber();}));
$('filing').addEventListener('change',renderSource);
$('random-filing').addEventListener('click',()=>{
  const options=chamberSources().filter(source=>source.id!==selectedSource?.id);
  if(!options.length)return;
  const choice=options[Math.floor(Math.random()*options.length)];
  $('filing').value=choice.id;renderSource();
});
$('overlays').addEventListener('change',()=>{$('document').classList.toggle('hide-overlays',!$('overlays').checked);});
$('document').addEventListener('scroll',hideFieldTooltip,{passive:true});
window.addEventListener('resize',hideFieldTooltip);
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
function resultColumns(){
  return [{key:'chamber',label:'Chamber',options:['House','Senate']},{key:'filing_id',label:'Filing ID'},
    {key:'politician',label:'Politician'},{key:'transaction_date',label:'Transaction date'},
    {key:'owner',label:'Owner'},{key:'asset_name',label:'Asset'},{key:'ticker',label:'Ticker'},
    {key:'action',label:'Type',options:['Purchase','Sale','Exchange','Other']},{key:'amount_raw',label:'Amount',numberKey:'amount_min'},
    {key:'source_url',label:'Source',fixed:true}];
}
function tableValue(row,key){
  if(key==='action')return row.action?row.action.charAt(0).toUpperCase()+row.action.slice(1):'';
  return row[key]??'';
}
function resultData(){return P.transactions;}
function buildResultHead(){
  const labels=node('tr'),filters=node('tr',null,'column-filters');
  resultColumns().forEach(col=>{
    const th=node('th');th.scope='col';
    if(col.fixed)th.textContent=col.label;
    else{
      th.dataset.sortKey=col.key;const button=node('button',null,'sort-column');button.type='button';
      button.setAttribute('aria-label',`Sort by ${col.label}`);if(col.numberKey)button.title='Sort by the lower bound of the reported range';button.append(document.createTextNode(col.label),node('span','↕','sort-marker'));
      button.addEventListener('click',()=>{
        resultSort={key:col.key,direction:resultSort.key===col.key?-resultSort.direction:1};page=0;sortResults();renderRows();
      });th.append(button);
    }
    labels.append(th);const cell=node('th');
    if(!col.fixed){
      const input=node(col.options?'select':'input');input.setAttribute('aria-label',`Filter ${col.label}`);input.dataset.column=col.key;
      if(col.options){const option=node('option','All');option.value='';input.append(option);col.options.forEach(value=>{const item=node('option',value);item.value=value;input.append(item);});}
      else{input.type='search';input.placeholder=col.key==='transaction_date'?'YYYY-MM-DD':'Search…';}
      input.addEventListener(col.options?'change':'input',()=>{columnQueries[col.key]=input.value;applyFilters();});cell.append(input);
    }
    filters.append(cell);
  });$('results-head').replaceChildren(labels,filters);
}
function sortResults(){
  const key=resultSort.key,col=resultColumns().find(c=>c.key===key);
  filtered.sort((a,b)=>{
    const av=col.numberKey?(a[col.numberKey]??''):tableValue(a,key),bv=col.numberKey?(b[col.numberKey]??''):tableValue(b,key),emptyA=av==='',emptyB=bv==='';
    if(emptyA!==emptyB)return emptyA?1:-1;
    const order=col.numeric||col.numberKey?Number(av)-Number(bv):tableCollator.compare(String(av),String(bv));
    return resultSort.direction*order||tableCollator.compare(a.transaction_id||a.ticker+'|'+a.month,b.transaction_id||b.ticker+'|'+b.month);
  });
}
function applyFilters(){
  const columns=resultColumns(),words=$('table-search').value.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
  filtered=resultData().filter(row=>{
    if(!columns.every(col=>{
      const query=(columnQueries[col.key]||'').trim().toLocaleLowerCase(),value=String(tableValue(row,col.key)).toLocaleLowerCase();
      return !query||(col.options?value===query:value.includes(query));
    }))return false;
    const text=[...columns.map(col=>tableValue(row,col.key)),row.transaction_type||''].join(' ').toLocaleLowerCase();
    return words.every(word=>text.includes(word));
  });page=0;sortResults();renderRows();
}
function inspectResultFiling(row){
  chamber=row.chamber;renderChamber(row.filing_id);showView('sources');
  document.querySelector('.workspace').scrollIntoView({block:'start',behavior:'instant'});
}
function renderRows(){
  const columns=resultColumns(),start=page*pageSize,total=resultData().length;
  $('results').replaceChildren();
  filtered.slice(start,start+pageSize).forEach(row=>{
    const tr=node('tr');
    columns.forEach(col=>{
      const td=node('td');td.dataset.column=col.key;
      if(col.key==='filing_id'){
        const button=node('button',row.filing_id,'filing-link');button.type='button';button.title=row.filing_id;
        button.setAttribute('aria-label',`Inspect ${row.chamber} filing ${row.filing_id}`);button.addEventListener('click',()=>inspectResultFiling(row));td.append(button);
      }else if(col.key==='source_url'){
        const link=node('a',row.chamber==='House'?'View PDF ↗':'View filing ↗');link.href=row.source_url;link.target='_blank';link.rel='noopener';td.append(link);
      }else{td.textContent=tableValue(row,col.key)||'—';if(col.key==='action')td.title=`Reported source value: ${row.transaction_type}`;}
      tr.append(td);
    });$('results').append(tr);
  });
  if(!filtered.length){const tr=node('tr'),td=node('td','No entries match your search. Clear filters to start again.','empty');td.colSpan=columns.length;tr.append(td);$('results').append(tr);}
  $('results-head').querySelectorAll('[data-sort-key]').forEach(th=>{
    const current=th.dataset.sortKey===resultSort.key;
    th.setAttribute('aria-sort',current?(resultSort.direction===1?'ascending':'descending'):'none');th.querySelector('.sort-marker').textContent=current?(resultSort.direction===1?'↑':'↓'):'↕';
  });
  $('result-count').textContent=`Showing ${fmt(filtered.length?start+1:0)} to ${fmt(Math.min(start+pageSize,filtered.length))} of ${fmt(filtered.length)} entries`+(filtered.length<total?` (filtered from ${fmt(total)} total entries)`:'');
  renderResultPages();
}
function renderResultPages(){
  const nav=$('result-pages'),last=Math.max(0,Math.ceil(filtered.length/pageSize)-1);nav.replaceChildren();
  const control=(text,target,label,disabled=false)=>{
    const button=node('button',text);button.type='button';button.disabled=disabled;button.setAttribute('aria-label',label);
    if(target===page&&/^\d+$/.test(text))button.setAttribute('aria-current','page');
    button.addEventListener('click',()=>{page=target;renderRows();});nav.append(button);
  };
  control('Previous',page-1,'Previous page',page===0);
  const pages=[...new Set([0,last,page-1,page,page+1].filter(n=>n>=0&&n<=last))].sort((a,b)=>a-b);
  pages.forEach((n,index)=>{if(index&&n>pages[index-1]+1)nav.append(node('span','…'));control(String(n+1),n,`Page ${n+1}`);});
  control('Next',page+1,'Next page',page>=last);
}
$('table-search').addEventListener('input',applyFilters);
$('page-size').addEventListener('change',()=>{pageSize=Number($('page-size').value);page=0;renderRows();});
$('reset-results').addEventListener('click',()=>{
  columnQueries={};$('table-search').value='';$('results-head').querySelectorAll('input,select').forEach(input=>input.value='');applyFilters();
});
renderChamber();renderJoin();buildResultHead();applyFilters();showView(location.hash.slice(1));
