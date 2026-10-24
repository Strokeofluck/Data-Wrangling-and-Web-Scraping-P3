"""Common schema, explicit ticker-month grains, and a validated outer join."""
from __future__ import annotations
import json
import hashlib
from pathlib import Path
import pandas as pd
from senate import parse_archive
from house import extract_house

ROOT=Path(__file__).resolve().parents[1]
KEYS=['ticker','month']

def verify_raw(root=ROOT):
    manifest=json.loads((root/'provenance/raw_sha256.json').read_text())
    for relative,expected in manifest.items():
        path=root/relative
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=expected:
            raise ValueError(f'Original raw file changed: {relative}')
    return len(manifest)

def load_house(root=ROOT):
    src=extract_house(root)
    out=pd.DataFrame({
        'transaction_id':'House:'+src.filing_id+':'+src.transaction_number_in_filing,
        'chamber':'House','filing_id':src.filing_id,'row_number':src.transaction_number_in_filing,
        'politician':src.politician,'filing_date':'','transaction_date':src.transaction_date,
        'owner':src.owner,'ticker':src.ticker_v8_2_cleaned,'asset_name':src.asset_v8_2_cleaned,
        'asset_type':src.asset_type,'transaction_type':src.transaction_type,
        'amount_raw':src.amount_raw,'amount_min':pd.to_numeric(src.amount_min,errors='coerce'),
        'amount_max':pd.to_numeric(src.amount_max,errors='coerce'),
        'source_url':src.original_pdf_url,'source_format':'PDF','comment':src.comments,
        'review_flag':src.needs_review,'ticker_status':src.ticker_parse_status})
    if out.transaction_id.duplicated().any(): raise ValueError('Duplicate House report + item identity')
    return out

def prepare_comparable(frame, chamber, year=2025):
    df=frame.copy()
    parsed=pd.to_datetime(df.transaction_date,format='%Y-%m-%d',errors='coerce')
    # Protects against silently accepting a malformed date as a missing observation.
    assert parsed.notna().all(),f'{chamber}: invalid or missing transaction dates'
    df['ticker']=df.ticker.str.strip().str.upper()
    df['month']=parsed.dt.strftime('%Y-%m')
    date_ok=parsed.dt.year.eq(year)
    ticker_ok=df.ticker.str.fullmatch(r'[A-Z][A-Z0-9.\-^/]{0,14}',na=False)&~df.ticker.isin(['N/A','NA','NONE'])
    if chamber=='House':
        scope_ok=df.asset_type.eq('ST') & df.ticker_status.eq('accepted')
    else:
        scope_ok=df.asset_type.eq('Stock')
    eligible=date_ok&ticker_ok&scope_ok
    df['exclusion_reason']=''
    df.loc[~date_ok,'exclusion_reason']='outside transaction year'
    df.loc[date_ok&~scope_ok,'exclusion_reason']='outside ticker-bearing stock/fund scope'
    df.loc[date_ok&scope_ok&~ticker_ok,'exclusion_reason']='missing or unsupported ticker'
    kind=df.transaction_type.str.lower()
    df['action']='other'
    df.loc[kind.eq('p')|kind.str.startswith('purchase'),'action']='purchase'
    df.loc[kind.eq('s')|kind.str.startswith('sale'),'action']='sale'
    df.loc[kind.eq('e')|kind.str.startswith('exchange'),'action']='exchange'
    # Preserve source rows and all uncertain amounts; this join counts reports, never dollars.
    counts={'input_rows':len(df),'eligible_rows':int(eligible.sum()),
            'outside_year':int((~date_ok).sum()),
            'excluded_scope':int((date_ok&~scope_ok).sum()),
            'excluded_ticker':int((date_ok&scope_ok&~ticker_ok).sum())}
    assert counts['input_rows']==sum(counts[k] for k in ['eligible_rows','outside_year','excluded_scope','excluded_ticker'])
    return df[eligible].copy(),df[~eligible].copy(),counts

def aggregate(frame, prefix):
    # One row per reported ticker and calendar month within ONE chamber.
    result=frame.groupby(KEYS,as_index=False).agg(
        reports=('transaction_id','size'),filings=('filing_id','nunique'),
        filers=('politician','nunique'),purchases=('action',lambda s:int(s.eq('purchase').sum())),
        sales=('action',lambda s:int(s.eq('sale').sum())))
    assert not result.duplicated(KEYS).any(),'Protects against ambiguous summary keys'
    return result.rename(columns={c:f'{prefix}_{c}' for c in result.columns if c not in KEYS})

def join_design(house,senate):
    left=set(map(tuple,house[KEYS].to_numpy()))
    right=set(map(tuple,senate[KEYS].to_numpy()))
    return {'keys':KEYS,'left_grain':'one row per ticker and calendar month in House filings',
        'right_grain':'one row per ticker and calendar month in Senate electronic filings',
        'relationship':'one_to_one','join_type':'outer','expected_rows':len(left|right),
        'left_rows':len(left),'right_rows':len(right),'both':len(left&right),
        'left_only':len(left-right),'right_only':len(right-left),
        'unmatched':'retained; opposite chamber values remain NA, not zero',
        'why':'Compare reported ticker-month activity without matching different politicians or multiplying transactions.'}

def merge_summaries(house,senate,design):
    joined=house.merge(senate,on=KEYS,how='outer',validate='one_to_one',indicator=True)
    return joined.sort_values(KEYS).reset_index(drop=True)

def verify_join(joined,house,senate,design,house_transactions,senate_transactions):
    # Each assertion states the real data assumption it protects.
    assert len(joined)==design['expected_rows'],'Protects against fan-out or dropped keys'
    assert not joined.duplicated(KEYS).any(),'Protects against duplicated ticker-month summaries'
    assert set(map(tuple,joined[KEYS].to_numpy()))==(set(map(tuple,house[KEYS].to_numpy()))|set(map(tuple,senate[KEYS].to_numpy()))),'Protects against an accidental inner join dropping unmatched months'
    assert int(joined.house_reports.sum())==len(house_transactions),'Protects against lost or multiplied House report rows'
    assert int(joined.senate_reports.sum())==len(senate_transactions),'Protects against lost or multiplied Senate report rows'
    assert joined[KEYS].notna().all().all(),'Protects against missing merge keys matching each other'
    assert joined.month.str.fullmatch(r'2025-(0[1-9]|1[0-2])').all(),'Protects against joining different analysis years'
    for prefix in ['house','senate']:
        values=joined[f'{prefix}_reports'].dropna()
        assert (values.ge(1)&values.mod(1).eq(0)).all(),'Protects against impossible report counts'
    assert int(joined._merge.eq('both').sum())==design['both'],'Protects against changed overlap cardinality'
    return ['Expected union row count','Unique ticker-month keys','All unmatched keys retained',
        'House report-count conservation','Senate report-count conservation','Nonmissing join keys',
        'Valid 2025 months','Positive integer counts','Expected overlap cardinality']

def build(root=ROOT):
    raw_count=verify_raw(root)
    house_all=load_house(root)
    senate_all,coverage=parse_archive(root)
    house,h_ex,h_count=prepare_comparable(house_all,'House')
    senate,s_ex,s_count=prepare_comparable(senate_all,'Senate')
    h_summary,s_summary=aggregate(house,'house'),aggregate(senate,'senate')
    design=join_design(h_summary,s_summary)
    joined=merge_summaries(h_summary,s_summary,design)
    checks=verify_join(joined,h_summary,s_summary,design,house,senate)
    out=root/'data/processed';out.mkdir(parents=True,exist_ok=True)
    for name,df in [('house_transactions_2025',house),('senate_transactions_2025',senate),
                    ('house_ticker_month',h_summary),('senate_ticker_month',s_summary),
                    ('combined_ticker_month',joined),('excluded_rows',pd.concat([h_ex,s_ex],ignore_index=True)),
                    ('combined_transactions',pd.concat([house,senate],ignore_index=True))]:
        df.to_csv(out/f'{name}.csv',index=False)
    summary={'year':2025,'house':h_count,'senate':s_count,'senate_coverage':coverage,
             'design':design,'checks':checks,'raw_files_verified':raw_count}
    (out/'validation.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    return summary

if __name__=='__main__': print(json.dumps(build(),indent=2))
