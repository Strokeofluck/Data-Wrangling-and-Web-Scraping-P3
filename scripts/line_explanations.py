"""Reviewed plain-language notes for the walkthrough's exact highlighted lines.

Each note checks its source prefix so edits cannot silently move an explanation
onto unrelated code. These notes describe the code; they do not run the scraper.
"""

NOTES = {
    'scripts/acquisition.py': {
        23: ('if interval', 'Check whether the requested pause is shorter than one second. If it is, the next line stops the program.'),
        27: ('self.interval,', 'Remember the pause length, clock, and waiting function so later requests can be spaced out.'),
        43: ('if body_path.exists()', 'Check whether both the saved response and its information file already exist. If so, reuse them instead of downloading again.'),
        47: ('raise AcquisitionError', 'Stop because the saved response no longer matches its recorded fingerprint. This prevents using a changed or damaged copy.'),
        54: ('self.sleep(', 'Wait only as long as needed to leave the required gap since the previous request.'),
        55: ('self.last_request =', 'Record when this request starts so the next request can be spaced out.'),
        56: ('request =', 'Prepare a request for this URL and identify it as the coursework scraper in the User-Agent header.'),
        58: ('with self.opener.open', 'Open the URL and allow up to 30 seconds for this network operation.'),
        60: ('if status != 200:', 'Stop if the server did not return the expected successful response.'),
        65: ('if not body:', 'Stop if the server returned an empty document instead of usable source content.'),
        74: ("with body_path.open('xb')", 'Save the downloaded document as a new file. The x option refuses to overwrite an existing copy.'),
        75: ("with meta_path.open('x'", 'Save the URL, response details, and fingerprint in a separate new information file.'),
    },
    'scripts/integration.py': {
        26: ("'owner':src.owner", 'Copy the audited House owner, cleaned ticker, and cleaned asset name into the matching P3 columns.'),
        28: ("'amount_raw':src.amount_raw", 'Keep the original amount wording and convert its lower bound to a number. Unreadable numeric values become missing values.'),
        37: ('parsed=pd.to_datetime', 'Read transaction dates as year-month-day dates. Invalid dates become missing here; the next check stops if any are missing.'),
        40: ("df['ticker']=", 'Remove spaces at the edges of each ticker and make its letters uppercase, so aapl and AAPL can match.'),
        41: ("df['month']=", 'Keep just the year and month from each transaction date: for example, 2025-11-21 becomes 2025-11.'),
        42: ('date_ok=', 'Mark a row as passing the date check only when its transaction happened in the chosen year, 2025.'),
        43: ('ticker_ok=', 'Check that the ticker has an allowed format and is not a placeholder such as N/A. This checks text format, not whether a security exists.'),
        45: ('scope_ok=df.asset_type.eq(\'ST\')', 'For House rows, require the ST asset code and an accepted ticker result from the audited extract.'),
        47: ("scope_ok=df.asset_type.eq('Stock')", 'For Senate rows, include only records whose reported asset type is Stock.'),
        48: ('eligible=', 'Keep a row in the comparison only if it passes all three checks: year, ticker, and asset scope.'),
        53: ('kind=', 'Make a lowercase working copy of the transaction label so capital letters do not affect the checks below.'),
        54: ("df['action']='other'", 'Start every row in the other category. The next lines replace it when they recognize a purchase, sale, or exchange.'),
        55: ('df.loc[kind.eq(\'p\')', 'Label P and text beginning with purchase as purchase, giving both chambers the same action label.'),
        56: ('df.loc[kind.eq(\'s\')', 'Label S and text beginning with sale as sale. This includes labels such as Sale (Partial).'),
        57: ('df.loc[kind.eq(\'e\')', 'Label E and text beginning with exchange as exchange.'),
        68: ('result=frame.groupby', 'Put rows with the same ticker and month into a group, then calculate the counts listed on the following lines.'),
        72: ('assert not result.duplicated', 'Stop if the summary contains the same ticker and month twice. Each chamber must have only one summary row per pair.'),
        80: ("'relationship':'one_to_one'", 'Declare one summary row per ticker-month on each side. Plan to keep keys from either chamber, and count each distinct pair once.'),
        87: ('joined=house.merge', 'Match House and Senate summaries using ticker and month. Keep unmatched rows, reject duplicate pairs, and add a column showing which chamber supplied each row.'),
        92: ('assert len(joined)', 'Stop if the combined table has more or fewer rows than the number of distinct ticker-month pairs expected from both sources.'),
        93: ('assert not joined.duplicated', 'Stop if any ticker-month pair appears twice in the combined table.'),
        94: ('assert set(map', 'Check that every ticker-month pair from either chamber is still present, with no extra pairs added.'),
    },
    'scripts/senate.py': {
        18: ('headers=', 'Read the table column headings in order and replace runs of spaces or line breaks with a single space.'),
        19: ('if headers == HEADERS:', 'Use this table only when all its headings match the expected nine columns in the expected order.'),
        27: ('values=', 'Read the text from each cell in this row, remove extra spaces, and keep the cells in their original order.'),
        31: ('item,date,owner,', 'Give each of the nine cell values a name, so the owner, ticker, asset name, and other fields stay separate.'),
        34: ('nums=', 'Find the dollar numbers in the amount text, remove commas, and turn them into whole numbers. $1,001 becomes 1001.'),
        36: ('low=', 'Use the first dollar number as the lower end of the reported amount range.'),
        37: ('high=', 'Leave the upper end missing when the text says over or more than. Otherwise, use the last dollar number as the upper end.'),
        40: ("'chamber':'Senate'", 'Save the chamber, filing ID, and printed row number. If the row number is blank, use its position in the table.'),
        41: ("'politician':filing['filer_name']", 'Copy the filer name and filing date from the captured filing index onto this transaction. The filing date is separate from the transaction date.'),
        42: ("'transaction_date':date", 'Save the parsed transaction date, reported owner, ticker, and asset name in separate output columns.'),
        43: ("'asset_type':asset_type", 'Save the asset category, transaction action, and original amount wording without combining them.'),
        44: ("'amount_min':low", 'Save the lower and upper amount bounds and the original report URL, so the record can be traced back to its source.'),
        45: ("'source_format':'HTML'", 'Record that this came from HTML and keep the comment text, including any source placeholder.'),
        52: ('filings=pd.read_csv', 'Open the captured Senate filing index as text. Keep blank cells blank instead of automatically turning them into missing-value markers.'),
    },
    'vendor/house-ptr-scraper/src/stage3_extract.py': {
        425: ('def parse_amount_text', 'Define the helper that reads an amount field and any allowed continuation text. Defining it does not run it; the following lines contain its instructions.'),
        672: ('value = normalize_house_pdf_text', 'Repair known character-encoding problems in House PDF text before using the value.'),
        673: ('return re.sub', 'Replace repeated spaces and line breaks with one space, trim the ends, and return the cleaned text. An empty input stays empty.'),
        689: ('return clean_space', 'Read selectable text only inside the chosen PDF rectangle, clean its spacing, and return it. This does not read a scanned image.'),
        863: ('output[name] = clip_text(', 'Read the text inside this field’s PDF rectangle and save it under the field name, such as owner or amount. The next lines supply the page and rectangle.'),
        865: ('fitz.Rect', 'Draw the extraction rectangle using its left, top, right, and bottom positions. Only text inside that box is requested.'),
        1322: ('type_match = TXN_RE.search(', 'Look in the transaction-type text for a recognized purchase, sale, or exchange code.'),
        1330: ('notification_dates = DATE_RE.findall(', 'Find all date-shaped values in the notification-date cell. Later code chooses the usable value.'),
        1331: ('core.get("notification_date", "")', 'Get the notification-date cell text. If that field is absent, supply an empty string instead of crashing.'),
        1337: ('transaction_type = type_match.group', 'Take the transaction code that was found and make it uppercase, such as P or S.'),
        1598: ('candidate = match.group', 'Take the ticker text captured by the pattern and make it uppercase. It is still a candidate, not a confirmed security.'),
        1608: ('return candidates[-1][1]', 'Return the ticker text from the last candidate collected by this helper. Other checks decide whether it is usable.'),
        1675: ('return datetime.strptime(', 'Read the cleaned date text using the month/day/year format supplied on the following lines.'),
        1678: (').strftime', 'Write that date in year-month-day format, so 11/21/2025 becomes 2025-11-21.'),
        1782: ('"politician": metadata(', 'Find Name: on the PDF’s first page, take the text after it up to the next line break, and save it as politician. Extra spacing is cleaned; no match leaves a blank.'),
        1783: ('"member_status": metadata(', 'Find Status: on the first page, take the text after it on the same line, and save it as member_status. No match leaves a blank.'),
        1784: ('"state_district": metadata(', 'Find State/District: on the first page, skip any spaces, and take the rest of that line. Save it as state_district; if the label is not found, leave it blank.'),
        2133: ('for transaction_number, record in enumerate', 'Go through the accepted records one at a time and number them 1, 2, 3, and so on. These are generated numbers, not copied printed IDs.'),
        2210: ('notification_date = to_iso_date', 'Convert the notification-date text already extracted from the row into year-month-day format.'),
        2352: ('cleaned_rows.append({', 'Start adding one cleaned transaction to the output list. The fields below are the values it exports; a capital-gains checkbox field is not included.'),
        2354: ('"politician": record[', 'Copy the filer’s name already read from the PDF into this transaction’s output record.'),
        2355: ('"member_status": record[', 'Copy the member status already read from the PDF into this transaction’s output record.'),
        2356: ('"state_district": record[', 'Copy the state and district already read from the PDF into this transaction’s output record. It does not look for the text again here.'),
        2359: ('"transaction_number_in_filing":', 'Save the sequential number generated for this accepted transaction within its filing.'),
        2366: ('"notification_date": notification_date', 'Save the converted notification date in its own output column, separate from the transaction date.'),
        2371: ('"amount_status": amount_info', 'Save the amount parser’s status describing how the amount was read. This field says nothing about whether the capital-gains box is checked.'),
    },
    'provenance/senate_scraper_original.py': {
        215: ('first_name =', 'Take the first-name cell from the Senate search result and trim its spaces. If that cell is absent, use a blank.'),
        216: ('last_name =', 'Take the last-name cell from the search result and trim its spaces. If that cell is absent, use a blank.'),
        219: ('filing_date =', 'Read the fifth search-result cell as the filing date. This is when the report was filed, not when a transaction happened.'),
        226: ('report_title =', 'Read the visible text of the report link and save it as the report title. If the link is missing, leave the title blank.'),
        246: ('"filer_name":', 'Join the nonblank first and last names with a space and save the combined filer name in the filing index.'),
        248: ('"filing_date":', 'Keep the filing date from the search result in the filing-index record.'),
        249: ('"report_title":', 'Keep the report link’s title in the filing-index record so it can be displayed later.'),
        299: ('filings_df["filing_date"] =', 'Convert the collected filing dates into dates, then format them as year-month-day on the next line. Unreadable dates become missing.'),
        305: ('filings_df.to_csv', 'Save the collected filing-index records to a CSV file without adding an extra row-number column.'),
    },
}


# Each phrase is paired with a literal fragment of the line it explains.
# None means the full statement, useful for verbs such as "copy" or "save".
LINKS = {
    'scripts/acquisition.py': {
        23: [('Check', 'if'), ('shorter than one second', 'interval < 1.0')],
        27: [('Remember', None), ('pause length', 'self.interval'), ('clock', 'self.clock'), ('waiting function', 'self.sleep')],
        43: [('Check', 'if'), ('saved response', 'body_path.exists()'), ('information file', 'meta_path.exists()'), ('both', 'and')],
        47: [('Stop', 'raise AcquisitionError'), ('fingerprint', 'Cache checksum mismatch')],
        54: [('Wait', 'self.sleep'), ('required gap', 'self.interval'), ('previous request', 'self.last_request')],
        55: [('Record', None), ('when this request starts', 'self.clock()')],
        56: [('Prepare a request', 'urllib.request.Request'), ('URL', 'url'), ('User-Agent', "'User-Agent':USER_AGENT")],
        58: [('Open the URL', 'self.opener.open'), ('30 seconds', 'timeout=30')],
        60: [('Stop', 'raise AcquisitionError'), ('successful response', 'status != 200')],
        65: [('Stop', 'raise AcquisitionError'), ('empty document', 'not body')],
        74: [('Save', 'stream.write(body)'), ('new file', "body_path.open('xb')"), ('x option', "'xb'")],
        75: [('Save', 'json.dump(meta,stream,indent=2)'), ('new information file', "meta_path.open('x',encoding='utf-8')")],
    },
    'scripts/integration.py': {
        26: [('Copy', None), ('owner', 'src.owner'), ('cleaned ticker', 'src.ticker_v8_2_cleaned'), ('cleaned asset name', 'src.asset_v8_2_cleaned')],
        28: [('Keep', "'amount_raw':src.amount_raw"), ('original amount wording', 'src.amount_raw'), ('convert', 'pd.to_numeric'), ('lower bound', 'src.amount_min'), ('missing values', "errors='coerce'")],
        37: [('Read', 'pd.to_datetime'), ('transaction dates', 'df.transaction_date'), ('year-month-day', "format='%Y-%m-%d'"), ('become missing', "errors='coerce'")],
        40: [('Remove spaces', '.str.strip()'), ('ticker', 'df.ticker'), ('uppercase', '.str.upper()')],
        41: [('Keep just the year and month', "parsed.dt.strftime('%Y-%m')"), ('2025-11', "'%Y-%m'")],
        42: [('passing the date check', 'date_ok'), ('transaction happened in the chosen year', 'parsed.dt.year.eq(year)')],
        43: [('allowed format', 'str.fullmatch'), ('placeholder', "df.ticker.isin(['N/A','NA','NONE'])")],
        45: [('ST asset code', "df.asset_type.eq('ST')"), ('accepted ticker result', "df.ticker_status.eq('accepted')"), ('and', '&')],
        47: [('reported asset type is Stock', "df.asset_type.eq('Stock')")],
        48: [('all three checks', 'date_ok&ticker_ok&scope_ok'), ('year', 'date_ok'), ('ticker', 'ticker_ok'), ('asset scope', 'scope_ok')],
        53: [('lowercase', '.str.lower()'), ('transaction label', 'df.transaction_type')],
        54: [('Start every row', "df['action']="), ('other category', "'other'")],
        55: [('Label', None), ('P', "kind.eq('p')"), ('text beginning with purchase', "kind.str.startswith('purchase')")],
        56: [('Label', None), ('S', "kind.eq('s')"), ('text beginning with sale', "kind.str.startswith('sale')")],
        57: [('Label', None), ('E', "kind.eq('e')"), ('text beginning with exchange', "kind.str.startswith('exchange')")],
        68: [('same ticker and month', 'KEYS'), ('group', '.groupby'), ('calculate the counts', '.agg(')],
        72: [('Stop', 'assert'), ('ticker and month twice', 'result.duplicated(KEYS).any()')],
        80: [('one summary row', "'one_to_one'"), ('keep keys from either chamber', "'outer'"), ('count each distinct pair once', 'len(left|right)')],
        87: [('Match', 'house.merge'), ('ticker and month', 'on=KEYS'), ('Keep unmatched rows', "how='outer'"), ('reject duplicate pairs', "validate='one_to_one'"), ('which chamber supplied each row', 'indicator=True')],
        92: [('Stop', 'assert'), ('combined table', 'len(joined)'), ('expected', "design['expected_rows']")],
        93: [('Stop', 'assert'), ('ticker-month pair appears twice', 'joined.duplicated(KEYS).any()')],
        94: [('Check', 'assert'), ('either chamber', '|'), ('still present', '==')],
    },
    'scripts/senate.py': {
        18: [('Read', "cell.get_text(' ',strip=True)"), ('column headings', "table.select('thead th')"), ('spaces or line breaks', "re.sub(r'\\s+',' ',cell.get_text(' ',strip=True))")],
        19: [('headings match', 'headers == HEADERS'), ('Use this table', 'return table')],
        27: [('Read', "c.get_text(' ',strip=True)"), ('remove extra spaces', "re.sub(r'\\s+',' ',c.get_text(' ',strip=True)).strip()"), ('original order', 'for c in cells')],
        31: [('Give each of the nine cell values a name', None), ('owner', 'owner'), ('ticker', 'ticker'), ('asset name', 'asset,')],
        34: [('Find the dollar numbers', 're.findall'), ('remove commas', "x.replace(',','')"), ('whole numbers', 'int(')],
        36: [('first dollar number', 'nums[0]'), ('lower end', 'low')],
        37: [('Leave the upper end missing', 'high=None'), ('over or more than', "r'over|more than'"), ('last dollar number', 'nums[-1]')],
        40: [('Save', None), ('chamber', "'chamber':'Senate'"), ('filing ID', "'filing_id':report_id"), ('printed row number', 'item'), ('position in the table', 'str(position)')],
        41: [('Copy', None), ('filer name', "filing['filer_name']"), ('filing date', "filing['filing_date']")],
        42: [('Save', None), ('transaction date', "'transaction_date':date"), ('owner', "'owner':owner"), ('ticker', "'ticker':ticker"), ('asset name', "'asset_name':asset")],
        43: [('Save', None), ('asset category', "'asset_type':asset_type"), ('transaction action', "'transaction_type':kind"), ('original amount wording', "'amount_raw':amount")],
        44: [('Save', None), ('lower', "'amount_min':low"), ('upper', "'amount_max':high"), ('original report URL', "filing['report_url']")],
        45: [('HTML', "'source_format':'HTML'"), ('keep the comment text', "'comment':comment")],
        52: [('Open', 'pd.read_csv'), ('captured Senate filing index', "raw/'filing_index.csv'"), ('as text', 'dtype=str'), ('Keep blank cells blank', 'keep_default_na=False')],
    },
    'vendor/house-ptr-scraper/src/stage3_extract.py': {
        425: [('Define the helper', 'def parse_amount_text'), ('amount field', 'amount_raw'), ('continuation text', 'continuation_raw')],
        672: [('Repair', 'normalize_house_pdf_text'), ('PDF text', 'value')],
        673: [('Replace', 're.sub'), ('repeated spaces and line breaks', 'r"\\s+"'), ('one space', '" "'), ('trim the ends', '.strip()'), ('return', 'return')],
        689: [('Read selectable text', 'page.get_text("text", clip=rect)'), ('chosen PDF rectangle', 'clip=rect'), ('clean its spacing', 'clean_space'), ('return', 'return')],
        863: [('Read the text', 'clip_text('), ('save it under the field name', 'output[name] =')],
        865: [('extraction rectangle', 'fitz.Rect'), ('left', 'x0'), ('top', 'y0'), ('right', 'x1'), ('bottom', 'y1')],
        1322: [('Look', 'TXN_RE.search'), ('recognized purchase, sale, or exchange code', 'TXN_RE')],
        1330: [('Find all', 'DATE_RE.findall'), ('date-shaped values', 'DATE_RE'), ('notification-date cell', 'notification_dates')],
        1331: [('Get', 'core.get'), ('notification-date cell text', '"notification_date"'), ('empty string', '""')],
        1337: [('transaction code that was found', 'type_match.group(1)'), ('uppercase', '.upper()')],
        1598: [('ticker text captured by the pattern', 'match.group(1)'), ('uppercase', '.upper()'), ('candidate', 'candidate')],
        1608: [('Return', 'return'), ('ticker text', '[1]'), ('last candidate', 'candidates[-1]')],
        1675: [('Read', 'datetime.strptime')],
        1678: [('Write that date', '.strftime'), ('year-month-day format', '"%Y-%m-%d"')],
        1782: [('Find Name:', 'Name:'), ('take the text after it', '([^\\n]+)'), ('politician', '"politician"'), ('Extra spacing is cleaned', 'metadata(')],
        1783: [('Find Status:', 'Status:'), ('same line', '([^\\n]+)'), ('member_status', '"member_status"')],
        1784: [('Find State/District:', 'State/District:'), ('skip any spaces', '\\s*'), ('rest of that line', '([^\\n]+)'), ('Save it', 'metadata('), ('state_district', '"state_district"')],
        2133: [('Go through', 'for'), ('accepted records', 'records'), ('number them 1, 2, 3', 'enumerate(records, start=1)')],
        2210: [('Convert', 'to_iso_date'), ('notification-date text', 'record["notification_date_raw_value"]')],
        2352: [('adding one cleaned transaction', 'cleaned_rows.append'), ('fields below', '{')],
        2354: [('Copy', None), ('filer’s name already read', 'record["politician"]'), ('output record', '"politician":')],
        2355: [('Copy', None), ('member status already read', 'record["member_status"]'), ('output record', '"member_status":')],
        2356: [('Copy', None), ('state and district already read', 'record["state_district"]'), ('output record', '"state_district":')],
        2359: [('Save', None), ('sequential number', 'transaction_number,')],
        2366: [('Save', None), ('converted notification date', 'notification_date,')],
        2371: [('Save', None), ('amount parser’s status', 'amount_info["amount_status"]')],
    },
    'provenance/senate_scraper_original.py': {
        215: [('first-name cell', 'raw[0]'), ('trim its spaces', '.strip()'), ('cell is absent', 'len(raw) > 0'), ('blank', 'else ""')],
        216: [('last-name cell', 'raw[1]'), ('trim its spaces', '.strip()'), ('cell is absent', 'len(raw) > 1'), ('blank', 'else ""')],
        219: [('fifth search-result cell', 'raw[4]'), ('filing date', 'filing_date')],
        226: [('Read the visible text', 'anchor.get_text(" ", strip=True)'), ('report title', 'report_title'), ('link is missing', 'if anchor else ""')],
        246: [('Join', '" ".join'), ('nonblank', 'if x'), ('first and last names', '[first_name, last_name]'), ('filer name', '"filer_name"')],
        248: [('Keep', None), ('filing date', 'filing_date,')],
        249: [('Keep', None), ('report link’s title', 'report_title,')],
        299: [('Convert', 'pd.to_datetime'), ('collected filing dates', 'filings_df["filing_date"]'), ('format them', '.dt.strftime('), ('become missing', 'errors="coerce"')],
        305: [('Save', '.to_csv'), ('CSV file', 'FILING_INDEX_CSV'), ('without adding an extra row-number column', 'index=False')],
    },
}


def explain_line(path, number, source):
    try:
        prefix, meaning = NOTES[path][number]
    except KeyError as exc:
        raise ValueError(f'Missing plain-language note: {path}:{number}') from exc
    if not source.strip().startswith(prefix):
        raise ValueError(f'Plain-language note no longer matches source: {path}:{number}')
    import re
    links=[]
    for phrase,fragment in LINKS[path][number]:
        if not re.search(r'(?<!\w)'+re.escape(phrase)+r'(?!\w)',meaning,re.I):
            raise ValueError(f'Plain-language phrase missing: {path}:{number}: {phrase}')
        fragment=source.strip() if fragment is None else fragment
        start=source.find(fragment)
        if start<0:raise ValueError(f'Linked code fragment missing: {path}:{number}: {fragment}')
        links.append({'phrase':phrase,'start':start,'end':start+len(fragment),'code':fragment})
    return {'line': number, 'meaning': meaning, 'links':links}
