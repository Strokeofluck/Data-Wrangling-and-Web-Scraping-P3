"""Build the clean source/code inspector from the same processed P3 results."""
from pathlib import Path
import ast
import json
import shutil
import hashlib
import re
import pandas as pd
from senate import find_table, SourceStructureError
from integration import ROOT,build,KEYS
from walkthroughs import build_walkthroughs
from build_house_geometry import build as build_geometry

def snippet(path,function,max_lines=32):
    text=(ROOT/path).read_text(encoding='utf-8');lines=text.splitlines()
    node=next(n for n in ast.walk(ast.parse(text)) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name==function)
    end=min(node.end_lineno,node.lineno+max_lines-1)
    return {'code':'\n'.join(lines[node.lineno-1:end]),'file':path,'line':node.lineno,
        'end':end,'partial':end<node.end_lineno}

def explain(title,why,path,function,max_lines=32):
    return {'title':title,'why':why,**snippet(path,function,max_lines)}

def failure_cases():
    failures=[]
    try:find_table('<html><p>Maintenance page; no report table.</p></html>')
    except SourceStructureError as exc:failures.append({'title':'Missing HTML selector','caught':type(exc).__name__,'message':str(exc)})
    left=pd.DataFrame({'ticker':['ABC'],'month':['2025-01']})
    right=pd.DataFrame({'ticker':['ABC','ABC'],'month':['2025-01','2025-01']})
    try:left.merge(right,on=KEYS,validate='one_to_one')
    except pd.errors.MergeError as exc:failures.append({'title':'Duplicate join key','caught':type(exc).__name__,'message':str(exc)})
    return failures

def build_site():
    summary=build()
    build_geometry(workers=1)
    sources=[]
    for path in sorted((ROOT/'docs/source').glob('*.json')):
        entry=json.loads(path.read_text(encoding='utf-8'))
        geometry=entry.get('geometry');ident=entry['filing_id']
        if not geometry:continue
        full_geometry=ROOT/f'docs/data/house_geometry/{ident}.json'
        if not full_geometry.exists():
            raise FileNotFoundError('Run python scripts/build_house_geometry.py first: '+ident)
        fields=json.loads(full_geometry.read_text(encoding='utf-8'))['fields']
        sources.append({'chamber':'House','id':ident,'name':f"{entry['politician']} · {ident}",
            'politician':entry['politician'],'image':f'source/{ident}.webp','original':entry['pdf_url'],
            'archive':f'../data/raw/2025_pdfs/{ident}.pdf','width':geometry['width'],'height':geometry['height'],
            'fields':fields,'rows':entry['rows'],'page':entry['page'],
            'caption':f"Actual captured House PDF, page {entry['page']} of {entry['page_count']}. Highlights follow the bundled parser's PDF cell coordinates; values come from P3's own extraction. Open the captured PDF to inspect the complete filing."})
    filings=pd.read_csv(ROOT/'data/raw/senate/filing_index.csv',dtype=str,keep_default_na=False).set_index('report_id')
    candidates=filings[filings.filing_format=='electronic_html'].index
    for ident in candidates:
        raw=ROOT/f'data/raw/senate/html/{ident}.html'
        table=find_table(raw.read_text(encoding='utf-8'))
        rows=[]
        for tr in table.select('tbody tr'):
            rows.append([cell.get_text(' ',strip=True) for cell in tr.find_all('td',recursive=False)])
        entry=filings.loc[ident]
        sources.append({'chamber':'Senate','id':ident,'name':f"{entry.filer_name} · {entry.filing_date}",
            'politician':entry.filer_name,'filing_date':entry.filing_date,'report_title':entry.report_title,'original':entry.report_url,
            'archive':f'../data/raw/senate/html/{ident}.html','table':rows,'total_rows':len(table.select('tbody tr')),
            'caption':'Actual transaction cells from the captured Senate HTML, in a simplified local layout with external scripts removed. All rows in this filing are shown. This is a fixed collection, not a live site connection.'})
    house_code='vendor/house-ptr-scraper/src/stage3_extract.py'
    explanations={
        'House:owner':explain('Read the owner column','PDF text has positions. Clip the owner cell inside this row so an asset name or neighboring date cannot be read as the owner. A blank cell stays blank.',house_code,'extract_row_columns'),
        'House:asset':explain('Extract the asset and its reported ticker','The source reports the company name, ticker, and asset code together. Read this geometric cell before resolving ticker candidates. The raw wording remains available for review.',house_code,'extract_ticker_from_context'),
        'House:transaction_type':explain('Keep purchase, sale, and exchange distinct','Read the transaction-type column within the accepted row. The common schema maps P to purchase, S to sale, and E to exchange, while preserving the original source value.','scripts/integration.py','prepare_comparable'),
        'House:transaction_date':explain('Parse the transaction date','The transaction date is different from the notification date. The pinned House parser extracts the date before P3 derives the calendar month used in the join.',house_code,'to_iso_date'),
        'House:amount':explain('Keep the disclosed amount as a range','The source usually gives a bracket, not an exact investment amount. Preserve the original bracket and its bounds. P3 counts report rows rather than summing approximate dollars.',house_code,'parse_amount_text'),
        'Senate:transaction_date':explain('Read the dated HTML cell','Match the complete header contract before reading cells. Parse the transaction date explicitly as month/day/year. A malformed date raises an exception.','scripts/senate.py','parse_report'),
        'Senate:owner':explain('Preserve the disclosed owner','The owner cell distinguishes Self, Joint, Spouse, and other reported values. Preserve it alongside the filing identifier so the record stays traceable.','scripts/senate.py','parse_report'),
        'Senate:asset':explain('Read separate ticker and asset cells','Senate HTML separates ticker, asset name, and asset type. Match those columns by the verified header order, and retain the original reported text.','scripts/senate.py','parse_report'),
        'Senate:transaction_type':explain('Normalize the action across chambers','The Senate uses labels such as Purchase or Sale (Partial); the House uses codes. Normalize action labels without changing the raw source field.','scripts/integration.py','prepare_comparable'),
        'Senate:amount':explain('Preserve range uncertainty','Parse the reported numeric bounds. Open-ended amounts retain a missing upper bound. An amount that cannot be recognized stops extraction.','scripts/senate.py','parse_report'),
        'merge':explain('Validate the join while it runs','An outer join keeps ticker-months found in just one chamber. validate="one_to_one" rejects duplicate summary keys before they can multiply rows. The indicator records both, House-only, and Senate-only matches.','scripts/integration.py','merge_summaries'),
        'acquisition':explain('Acquire once, then reuse the archive','Use a coursework User-Agent, wait at least one second between requests, set a timeout, and stop on HTTP errors. Read a verified disk response before requesting the resource again.','scripts/acquisition.py','fetch',60)}
    for key,steps in build_walkthroughs().items():
        if key not in explanations:
            explanations[key]={'title':steps[-1]['title'],'why':steps[-1]['why'],**{k:steps[-1][k] for k in ['code','file','line','end']}}
        if key.startswith('Senate:'):
            label=key.split(':',1)[1].replace('_',' ')
            explanations[key]['title']='Read the Senate '+label
        explanations[key]['steps']=steps
    explanations['House:notification_date']['title']='Read the notification date'
    explanations['House:notification_date']['why']='This date is exported by the bundled House parser and retained in P3’s generated extract. It is distinct from the transaction date used in the join.'
    explanations['House:cap_gains']['title']='Capital-gains column: source only'
    explanations['House:cap_gains']['why']='This source column is clipped by the geometry helper, but its checkbox state is not exported as structured data. Empty extracted text does not establish whether the box is checked.'
    explanations['House:id']['title']='Printed ID and generated row number'
    explanations['House:id']['why']='The source cell is visible here. The parser uses a generated sequential transaction number rather than exporting a separate printed ID value.'
    code_files={}
    for explanation in explanations.values():
        for step in explanation.get('steps',[]):
            if step['file'] not in code_files:
                code_files[step['file']]=(ROOT/step['file']).read_text(encoding='utf-8').splitlines()
    joined=pd.read_csv(ROOT/'data/processed/combined_ticker_month.csv').astype(object)
    joined=joined.where(pd.notna(joined),None)
    transactions=pd.read_csv(ROOT/'data/processed/combined_transactions.csv',dtype=str,keep_default_na=False)
    lineage={}
    for row in transactions.to_dict('records'):
        key=f"{row['ticker']}|{row['month']}"
        lineage.setdefault(key,[]).append({'chamber':row['chamber'],'person':row['politician'],
            'id':row['filing_id'],'row':row['row_number'],'date':row['transaction_date'],
            'url':row['source_url'],'action':row['action']})
    payload={'summary':summary,'sources':sources,'explanations':explanations,'code_files':code_files,'transactions':transactions.to_dict('records'),
        'failures':failure_cases(),'rows':joined.to_dict('records'),'lineage':lineage}
    (ROOT/'docs/data/project.js').write_text('window.P3 = '+json.dumps(payload,ensure_ascii=True,allow_nan=False)+';\n',encoding='utf-8')
    html=(ROOT/'docs/index.html').read_text(encoding='utf-8')
    for relative in ['data/project.js','assets/app.js','assets/style.css']:
        version=hashlib.sha256((ROOT/'docs'/relative).read_bytes()).hexdigest()[:12]
        html=re.sub(re.escape(relative)+r'(?:\?v=[0-9a-f]+)?',relative+'?v='+version,html)
    (ROOT/'docs/index.html').write_text(html,encoding='utf-8')
    shutil.copy2(ROOT/'data/processed/combined_ticker_month.csv',ROOT/'docs/data/combined_ticker_month.csv')
    shutil.copy2(ROOT/'data/processed/combined_transactions.csv',ROOT/'docs/data/combined_transactions.csv')
    (ROOT/'data/processed/failure_demonstrations.json').write_text(json.dumps(payload['failures'],indent=2),encoding='utf-8')
    print(f"Built inspector: {len(sources)} source examples, {len(joined)} joined rows, {len(code_files)} complete source files.")

if __name__=='__main__':build_site()
