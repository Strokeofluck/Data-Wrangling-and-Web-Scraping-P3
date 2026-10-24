"""Record accurate hover regions for every parsed row on each displayed PDF page.

Uses the inherited P2 geometry observer, without modifying the pinned parser or
raw inputs. Cached results and source hashes make later site builds inexpensive.
"""
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
import argparse
import hashlib
import json
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/data/house_geometry'
TRACER=None
AUDITED=None

def initialize():
    global TRACER,AUDITED
    from trace_geometry import load_parser
    TRACER=load_parser(ROOT)
    df=pd.read_csv(ROOT/'data/raw/house_transactions_p2.csv',dtype=str,keep_default_na=False)
    AUDITED={(row['filing_id'],row['transaction_number_in_filing']):row for row in df.to_dict('records')}

def build_one(metadata_path):
    import fitz
    entry=json.loads(Path(metadata_path).read_text(encoding='utf-8'))
    ident=entry['filing_id'];page_number=entry['geometry']['page']
    pdf=ROOT/f'data/raw/2025_pdfs/{ident}.pdf'
    fingerprint=hashlib.sha256(pdf.read_bytes()).hexdigest()
    cached=OUT/f'{ident}.json'
    if cached.exists():
        old=json.loads(cached.read_text(encoding='utf-8'))
        if old.get('version')==1 and old.get('source_sha256')==fingerprint:return ident,'cached'
    parsed,metadata,traces=TRACER(pdf)
    if len(parsed)!=entry['rows']:
        raise ValueError(f'{ident}: geometry parser returned {len(parsed)} rows; expected {entry["rows"]}')
    fields=[]
    labels={'id':'Printed item ID','owner':'Owner','asset':'Asset & ticker',
            'transaction_type':'Transaction type','transaction_date':'Transaction date',
            'notification_date':'Notification date','amount':'Amount range','cap_gains':'Capital gains > $200?'}
    for index,trace in enumerate(traces,1):
        if trace['page']!=page_number:continue
        audited=AUDITED[(ident,str(index))]
        for item in trace['fields']:
            name=item['name']
            if name not in labels:raise ValueError(f'Unmapped House source column: {name}')
            after=item['after'] or '(kept blank)'
            if name=='asset':after=f"{audited['asset_v8_2_cleaned']} · ticker {audited['ticker_v8_2_cleaned'] or '(unresolved)'} · type {audited['asset_type'] or '(blank)'}"
            elif name in ['transaction_date','notification_date']:after=audited[name] or '(kept blank)'
            elif name=='transaction_type':after={'P':'purchase','S':'sale','E':'exchange'}.get(audited[name],audited[name])
            elif name=='id':after='Not exported from this printed column; a sequential filing row number is generated.'
            elif name=='cap_gains':after='Not exported as a structured checkbox value. No checked/unchecked state is inferred.'
            fields.append({'key':name,'label':labels[name],'rect':item['rect'],
                'before':item['before'].strip() or '(no text in this source cell)',
                'after':after,'row':str(index),'source_only':name in ['id','cap_gains']})
    # Filer metadata is also scraped. Mark its actual text bounds on page one.
    if page_number==1:
        audited=AUDITED[(ident,'1')]
        with fitz.open(pdf) as document:
            page=document[0]
            for key,label in [('politician','Filer name'),('member_status','Member status'),('state_district','State / district')]:
                value=audited[key]
                matches=[rect for rect in page.search_for(value) if rect.y0<page.rect.height*.4] if value else []
                if matches:
                    rect=matches[0]
                    fields.append({'key':key,'label':label,'rect':list(rect),
                        'before':page.get_text('text',clip=rect).strip(),'after':value,'row':'metadata','source_only':False})
    result={'version':1,'source_sha256':fingerprint,'filing_id':ident,'page':page_number,'fields':fields}
    cached.write_text(json.dumps(result,ensure_ascii=True,separators=(',',':')),encoding='utf-8')
    return ident,len(fields)

def build(filing=None,workers=2):
    OUT.mkdir(parents=True,exist_ok=True)
    paths=sorted((ROOT/'docs/source').glob(f'{filing or "*"}.json'))
    if not paths:raise ValueError('No captured House filing metadata found')
    if workers==1:
        initialize()
        for path in paths:print(build_one(str(path)),flush=True)
    else:
        with ProcessPoolExecutor(max_workers=workers,initializer=initialize) as pool:
            for index,result in enumerate(pool.map(build_one,map(str,paths)),1):
                if index%25==0 or index==len(paths):print(f'PDF hover geometry: {index}/{len(paths)} filings ready',flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--filing');parser.add_argument('--workers',type=int,default=2)
    args=parser.parse_args();build(args.filing,args.workers)
