"""Record accurate hover regions for every parsed row on each displayed PDF page.

Uses the bundled geometry observer, without modifying the pinned parser or raw
inputs. Structured values come from P3's own PDF extraction.
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
EXTRACTED=None
EXTRACT_SHA=None

def initialize():
    global EXTRACTED,EXTRACT_SHA
    from house import extract_house
    df=extract_house(ROOT)
    EXTRACT_SHA=hashlib.sha256((ROOT/'data/processed/house_extracted.csv').read_bytes()).hexdigest()
    EXTRACTED={(row['filing_id'],row['transaction_number_in_filing']):row for row in df.to_dict('records')}


def structured_value(name,record):
    if name=='asset':return f"{record['asset_v8_2_cleaned']} · ticker {record['ticker_v8_2_cleaned'] or '(unresolved)'} · type {record['asset_type'] or '(blank)'}"
    if name=='transaction_type':return {'P':'purchase','S':'sale','E':'exchange'}.get(record[name],record[name])
    if name=='id':return 'Not exported from this printed column; a sequential filing row number is generated.'
    if name=='cap_gains':return 'Not exported as a structured checkbox value. No checked/unchecked state is inferred.'
    return record['amount_raw' if name=='amount' else name] or '(kept blank)'

def build_one(metadata_path):
    global TRACER
    import fitz
    entry=json.loads(Path(metadata_path).read_text(encoding='utf-8'))
    ident=entry['filing_id'];page_number=entry['geometry']['page']
    pdf=ROOT/f'data/raw/2025_pdfs/{ident}.pdf'
    fingerprint=hashlib.sha256(pdf.read_bytes()).hexdigest()
    cached=OUT/f'{ident}.json'
    if cached.exists():
        old=json.loads(cached.read_text(encoding='utf-8'))
        if old.get('source_sha256')==fingerprint:
            if old.get('version')==2 and old.get('extract_sha256')==EXTRACT_SHA:return ident,'cached'
            # Coordinates remain valid for the unchanged pinned parser and PDF.
            # Refresh their displayed values from this project's own extraction.
            actual=sum(key[0]==ident for key in EXTRACTED)
            if actual!=entry['rows']:raise ValueError(f'{ident}: P3 row count differs from source geometry metadata')
            for field in old['fields']:
                row='1' if field['row']=='metadata' else field['row']
                field['after']=structured_value(field['key'],EXTRACTED[(ident,row)])
            old.update(version=2,extract_sha256=EXTRACT_SHA)
            cached.write_text(json.dumps(old,ensure_ascii=True,separators=(',',':')),encoding='utf-8')
            return ident,'updated from P3 extract'
    if TRACER is None:
        from trace_geometry import load_parser
        TRACER=load_parser(ROOT)
    parsed,metadata,traces=TRACER(pdf)
    if len(parsed)!=entry['rows']:
        raise ValueError(f'{ident}: geometry parser returned {len(parsed)} rows; expected {entry["rows"]}')
    fields=[]
    labels={'id':'Printed item ID','owner':'Owner','asset':'Asset & ticker',
            'transaction_type':'Transaction type','transaction_date':'Transaction date',
            'notification_date':'Notification date','amount':'Amount range','cap_gains':'Capital gains > $200?'}
    for index,trace in enumerate(traces,1):
        if trace['page']!=page_number:continue
        record=EXTRACTED[(ident,str(index))]
        for item in trace['fields']:
            name=item['name']
            if name not in labels:raise ValueError(f'Unmapped House source column: {name}')
            after=structured_value(name,record)
            fields.append({'key':name,'label':labels[name],'rect':item['rect'],
                'before':item['before'].strip() or '(no text in this source cell)',
                'after':after,'row':str(index),'source_only':name in ['id','cap_gains']})
    # Filer metadata is also scraped. Mark its actual text bounds on page one.
    if page_number==1:
        record=EXTRACTED[(ident,'1')]
        with fitz.open(pdf) as document:
            page=document[0]
            for key,label in [('politician','Filer name'),('member_status','Member status'),('state_district','State / district')]:
                value=record[key]
                matches=[rect for rect in page.search_for(value) if rect.y0<page.rect.height*.4] if value else []
                if matches:
                    rect=matches[0]
                    fields.append({'key':key,'label':label,'rect':list(rect),
                        'before':page.get_text('text',clip=rect).strip(),'after':value,'row':'metadata','source_only':False})
    result={'version':2,'source_sha256':fingerprint,'extract_sha256':EXTRACT_SHA,'filing_id':ident,'page':page_number,'fields':fields}
    cached.write_text(json.dumps(result,ensure_ascii=True,separators=(',',':')),encoding='utf-8')
    return ident,len(fields)

def build(filing=None,workers=2):
    OUT.mkdir(parents=True,exist_ok=True)
    paths=sorted((ROOT/'docs/source').glob(f'{filing or "*"}.json'))
    if not paths:raise ValueError('No captured House filing metadata found')
    if workers==1:
        initialize()
        for index,path in enumerate(paths,1):
            build_one(str(path))
            if index==len(paths):print(f'PDF hover geometry: {index}/{len(paths)} filings verified against P3 extraction',flush=True)
    else:
        with ProcessPoolExecutor(max_workers=workers,initializer=initialize) as pool:
            for index,result in enumerate(pool.map(build_one,map(str,paths)),1):
                if index%25==0 or index==len(paths):print(f'PDF hover geometry: {index}/{len(paths)} filings ready',flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--filing');parser.add_argument('--workers',type=int,default=2)
    args=parser.parse_args();build(args.filing,args.workers)
