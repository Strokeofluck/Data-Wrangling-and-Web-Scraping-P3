"""Source-backed code journeys: complete functions with exact focus lines."""
import ast
from pathlib import Path
from line_explanations import explain_line

ROOT=Path(__file__).resolve().parents[1]
HOUSE='vendor/house-ptr-scraper/src/stage3_extract.py'
SENATE='scripts/senate.py'
INTEGRATION='scripts/integration.py'

def step(title,why,path,function,*anchors):
    source=(ROOT/path).read_text(encoding='utf-8')
    lines=source.splitlines()
    fn=next(n for n in ast.walk(ast.parse(source)) if isinstance(n,ast.FunctionDef) and n.name==function)
    focus=[]
    for anchor in anchors:
        found=[i+1 for i in range(fn.lineno-1,fn.end_lineno) if anchor in lines[i]]
        if not found:raise ValueError(f'Walkthrough anchor missing: {path}:{function}: {anchor}')
        focus.extend(found)
    focus=sorted(set(focus)) or [fn.lineno]
    return {'title':title,'why':why,'file':path,'line':fn.lineno,'end':fn.end_lineno,
            'code':'\n'.join(lines[fn.lineno-1:fn.end_lineno]),'focus':focus,
            'line_notes':[explain_line(path,n,lines[n-1]) for n in focus]}

def build_walkthroughs():
    journeys={}
    read=step('Locate the PDF cell','Use the row’s vertical bounds and this column’s horizontal bounds. The rectangle keeps neighboring fields out of the extraction.',HOUSE,'extract_row_columns','output[name] = clip_text(','fitz.Rect')
    clip=step('Read the text layer','Read text inside that rectangle, then clean the extracted text. This reads selectable PDF text rather than performing OCR.',HOUSE,'clip_text','return clean_space')
    clean=step('Repair and clean text','Repair the House PDF’s known character encoding, then collapse whitespace. The original source remains preserved.',HOUSE,'clean_space','normalize_house_pdf_text','re.sub')
    carry=lambda anchor:step('Carry the audited field into P3','P3 reads the audited P2 snapshot into its common schema. The PDF functions above explain how that earlier extract was produced; this is the current P3 input step.',INTEGRATION,'load_house',anchor)
    for name,anchor in [('owner',"'owner':src.owner"),('asset',"'ticker':src.ticker_v8_2_cleaned"),('transaction_date',"'transaction_date':src.transaction_date"),('transaction_type',"'transaction_type':src.transaction_type"),('amount',"'amount_raw':src.amount_raw")]:
        stages=[read,clip]
        if name=='owner':stages += [clean,carry(anchor)]
        if name=='asset':stages += [step('Extract a ticker candidate','Find the reported parenthesized ticker. This is an extraction candidate; P2’s resolver status is checked again when choosing P3’s comparable rows.',HOUSE,'extract_ticker_from_context','candidate = match.group(1).upper()','return candidates[-1][1]'),carry(anchor),step('Choose usable ticker records','Normalize ticker text and require an accepted House ticker before including it in the comparison.',INTEGRATION,'prepare_comparable',"df['ticker']",'ticker_ok=','scope_ok=df.asset_type')]
        if name=='transaction_date':stages += [step('Convert the date','Parse month/day/year into ISO format. P3 checks the resulting dates before deriving the join month.',HOUSE,'to_iso_date','datetime.strptime','strftime'),step('Derive the comparison month','Check the date, derive its calendar month, and restrict the comparison to the selected year.',INTEGRATION,'prepare_comparable',"parsed=pd.to_datetime", "df['month']",'date_ok=')]
        if name=='transaction_type':stages += [step('Read the transaction code','Read the purchase, sale or exchange code from the transaction-type cell.',HOUSE,'extract_core_values','type_match = TXN_RE.search','transaction_type = type_match.group(1).upper()'),step('Normalize the action','Map House codes and Senate labels to common action categories, retaining the original source field.',INTEGRATION,'prepare_comparable',"kind=df.transaction_type", "df['action']", "'action']=")]
        if name=='amount':stages += [step('Interpret the amount bracket','Read the reported amount as a range or exact amount where explicitly reported. The complete amount parser is scrollable here.',HOUSE,'parse_amount_text','def parse_amount_text'),carry(anchor)]
        journeys['House:'+name]=stages
    journeys['House:notification_date']=[read,clip,
        step('Read the notification date','This is a separate source column from the transaction date.',HOUSE,'extract_core_values','notification_dates = DATE_RE.findall','core.get("notification_date"'),
        step('Export the notification date','The original House parser converts and exports notification_date. P3 preserves it in its audited input; the ticker-month comparison uses transaction_date instead.',HOUSE,'parse_pdf_geometry_v8','notification_date = to_iso_date','"notification_date": notification_date')]
    journeys['House:cap_gains']=[read,clip,
        step('Check what the parser exports','The capital-gains column is visible and clipped as source text, but the output dictionary does not export a capital-gains checkbox value. Blank extracted text is not evidence of an unchecked box.',HOUSE,'parse_pdf_geometry_v8','cleaned_rows.append({','"amount_status": amount_info')]
    journeys['House:id']=[read,
        step('Generate the record identifier','The parser generates a sequential transaction_number_in_filing. It does not export the printed ID cell as a separate field.',HOUSE,'parse_pdf_geometry_v8','for transaction_number, record in enumerate(records','"transaction_number_in_filing": transaction_number')]
    for key,label in [('politician','filer name'),('member_status','member status'),('state_district','state / district')]:
        journeys['House:'+key]=[step('Read the '+label,'Extract the named metadata field from the first page’s text. The source overlay marks where that text appears.',HOUSE,'parse_pdf_geometry_v8',f'"{key}": metadata('),
            step('Export the '+label,'Keep this source metadata alongside the transaction record for provenance.',HOUSE,'parse_pdf_geometry_v8',f'"{key}": record["{key}"]')]
    field_anchors={
        'item_number':("'row_number':item or str(position)",'Keep the filing item number','The item number identifies the row inside its source filing.'),
        'transaction_date':("'transaction_date':date",'Save the transaction date','Read and parse the reported transaction date, not the filing date.'),
        'owner':("'owner':owner",'Save the owner','Preserve Self, Joint, Spouse, or the other owner text exactly as reported.'),
        'ticker':("'ticker':ticker",'Save the reported ticker','The Senate provides a separate ticker cell, so no parenthesis extraction is needed.'),
        'asset_name':("'asset_name':asset",'Save the asset name','The Asset Name cell is collected separately from ticker and asset type.'),
        'asset_type':("'asset_type':asset_type",'Save the asset type','This is the reported asset category, such as Stock. It is distinct from Purchase or Sale.'),
        'transaction_type':("'transaction_type':kind",'Save the transaction type','Collect the reported action, such as Purchase or Sale (Partial).'),
        'amount':("'amount_min':low",'Save the amount bounds','Preserve the original amount text, its lower bound and its upper bound when available.'),
        'comment':("'comment':comment",'Save the comment','Preserve the reported comment, including placeholder text. It is not used as a join key.')}
    for name,(anchor,title,why) in field_anchors.items():
        stages=[step('Find the source table','Match all nine expected headers. Missing or changed headers stop extraction instead of producing an empty dataset.',SENATE,'find_table','headers=','if headers == HEADERS'),step('Read the source columns','Read each HTML cell in the verified column order, then unpack the nine separate values.',SENATE,'parse_report',"values=[",'item,date,owner,ticker,asset,asset_type,kind,amount,comment=values'),step(title,why,SENATE,'parse_report',anchor)]
        if name=='asset_type':stages += [step('Apply the asset scope','P3 includes the Senate records labeled Stock in this comparison. Other categories remain accounted for in the exclusion output.',INTEGRATION,'prepare_comparable',"scope_ok=df.asset_type.eq('Stock')",'eligible=')]
        elif name=='transaction_date':stages += [step('Derive the join month','Check dates and derive the month for the ticker-month summary.',INTEGRATION,'prepare_comparable',"df['month']",'date_ok=')]
        elif name=='ticker':stages += [step('Normalize and check the ticker','Trim and uppercase the ticker, then keep only usable reported ticker text for the comparison.',INTEGRATION,'prepare_comparable',"df['ticker']",'ticker_ok=')]
        elif name=='transaction_type':stages += [step('Normalize the action','Map reported purchase and sale labels into the common action field.',INTEGRATION,'prepare_comparable',"kind=df.transaction_type", "df['action']", "'action']=")]
        elif name=='amount':stages.insert(2,step('Parse the amount range','Extract numeric bounds. An open-ended amount keeps its upper bound missing. P3 does not sum these as exact investment values.',SENATE,'parse_report','nums=','low=','high='))
        journeys['Senate:'+name]=stages
    journeys['Senate:asset']=journeys['Senate:ticker']
    original='provenance/senate_scraper_original.py'
    index_read=lambda:step('Read the captured filing index','P3 reuses the saved filing index. It does not need to request the Senate search page again.',SENATE,'parse_archive','filings=pd.read_csv')
    journeys['Senate:politician']=[
        step('Collect the filer name','The original scraper collected this metadata from the Senate search results before reading each transaction table.',original,'parse_search_result','first_name =','last_name =','"filer_name":'),
        index_read(),step('Attach the name to each transaction','P3 carries the captured index name into every transaction for this filing.',SENATE,'parse_report',"'politician':filing['filer_name']")]
    journeys['Senate:filing_date']=[
        step('Collect the filing date','Read the filing date from the Senate search result. It is separate from dates in the transaction table.',original,'parse_search_result','filing_date =','"filing_date":'),
        step('Format and save the index','The original scraper normalized filing dates before saving its index.',original,'build_filing_index','filings_df["filing_date"] =','filings_df.to_csv'),
        index_read(),step('Attach the filing date','P3 copies the saved filing date onto each transaction.',SENATE,'parse_report',"'politician':filing['filer_name']")]
    journeys['Senate:report_title']=[
        step('Collect the report title','Read the text of the report link in the Senate search result. The title is retained in the captured filing index; it is not a transaction field or join key.',original,'parse_search_result','report_title =','"report_title":'),
        step('Save the title in the index','Save the filing metadata, including the report title, in the original index CSV.',original,'build_filing_index','filings_df.to_csv'),index_read()]
    journeys['merge']=[step('Summarize each chamber','Group transaction rows by ticker and month before joining. This makes one row per key in each chamber.',INTEGRATION,'aggregate','result=frame.groupby','assert not result.duplicated'),step('Declare the expected relationship','Count the union of source keys before running the merge, and state what should happen to unmatched rows.',INTEGRATION,'join_design',"'relationship'", "'join_type'", "'expected_rows'"),step('Run the validated join','Keep unmatched keys using an outer join; reject duplicate summary keys with one-to-one validation.',INTEGRATION,'merge_summaries','joined=house.merge'),step('Check the result','Check row count, uniqueness, conservation of source counts and retention of unmatched keys.',INTEGRATION,'verify_join',"assert len(joined)",'assert not joined.duplicated','assert set(map')]
    journeys['acquisition']=[step('Identify and pace requests','Use an honest coursework User-Agent and at least one second between requests.','scripts/acquisition.py','__init__','if interval < 1.0','self.interval'),step('Reuse the disk cache','Verify the cached response hash before any network request.','scripts/acquisition.py','fetch','if body_path.exists() and meta_path.exists():','checksum mismatch'),step('Request and fail loudly','Wait before the request, set the timeout, and reject unsuccessful or empty responses.','scripts/acquisition.py','fetch','self.sleep(','request =','self.opener.open','if status != 200','if not body:'),step('Preserve the response','Store the body and its metadata without overwriting an existing cache entry.','scripts/acquisition.py','fetch',"with body_path.open('xb')","with meta_path.open('x'")]
    return journeys
