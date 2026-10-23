"""Strict parser for the archived official Senate HTML tables."""
from __future__ import annotations
import hashlib
import re
from datetime import datetime
from pathlib import Path
import pandas as pd
from bs4 import BeautifulSoup

HEADERS=['#','Transaction Date','Owner','Ticker','Asset Name','Asset Type','Type','Amount','Comment']

class SourceStructureError(ValueError):
    pass

def find_table(html):
    soup=BeautifulSoup(html,'html.parser')
    for table in soup.find_all('table'):
        headers=[re.sub(r'\s+',' ',cell.get_text(' ',strip=True)) for cell in table.select('thead th')]
        if headers == HEADERS: return table
    raise SourceStructureError('Expected Senate transaction table matched nothing, or its headers changed.')

def parse_report(html, filing):
    table=find_table(html)
    output=[]
    for position,tr in enumerate(table.select('tbody tr'),1):
        cells=tr.find_all('td',recursive=False)
        values=[re.sub(r'\s+',' ',c.get_text(' ',strip=True)).strip() for c in cells]
        if not values: continue
        if len(values)!=len(HEADERS):
            raise SourceStructureError(f"{filing['report_id']} row {position}: {len(values)} cells; expected 9")
        item,date,owner,ticker,asset,asset_type,kind,amount,comment=values
        try: date=datetime.strptime(date,'%m/%d/%Y').date().isoformat()
        except ValueError as exc: raise SourceStructureError(f'Unrecognized transaction date: {date!r}') from exc
        nums=[int(x.replace(',','')) for x in re.findall(r'\$\s*([0-9][0-9,]*)',amount)]
        if not nums: raise SourceStructureError(f'Unrecognized amount range: {amount!r}')
        low=nums[0]
        high=None if re.search(r'over|more than',amount,re.I) else nums[-1]
        report_id=filing['report_id']
        output.append({'transaction_id':f'Senate:{report_id}:{item or position}',
            'chamber':'Senate','filing_id':report_id,'row_number':item or str(position),
            'politician':filing['filer_name'],'filing_date':filing['filing_date'],
            'transaction_date':date,'owner':owner,'ticker':ticker,'asset_name':asset,
            'asset_type':asset_type,'transaction_type':kind,'amount_raw':amount,
            'amount_min':low,'amount_max':high,'source_url':filing['report_url'],
            'source_format':'HTML','comment':comment})
    # An empty matched table is not silently treated as a successful scrape.
    if not output: raise SourceStructureError(f"No transaction rows in {filing['report_id']}")
    return output

def parse_archive(root):
    raw=root/'data/raw/senate'
    filings=pd.read_csv(raw/'filing_index.csv',dtype=str,keep_default_na=False)
    records=[]
    electronic=filings[filings.filing_format=='electronic_html']
    for filing in electronic.to_dict('records'):
        path=raw/'html'/f"{filing['report_id']}.html"
        if not path.exists(): raise SourceStructureError(f'Missing archived HTML: {path.name}')
        records.extend(parse_report(path.read_text(encoding='utf-8'),filing))
    result=pd.DataFrame(records)
    if result.transaction_id.duplicated().any():
        raise SourceStructureError('Duplicate Senate report + item identities.')
    return result, {'electronic_reports':len(electronic),
        'paper_reports_deferred':int((filings.filing_format=='paper_scan').sum()),
        'index_rows':len(filings),'parsed_rows':len(result)}
