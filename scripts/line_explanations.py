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


def explain_line(path, number, source):
    try:
        prefix, meaning = NOTES[path][number]
    except KeyError as exc:
        raise ValueError(f'Missing plain-language note: {path}:{number}') from exc
    if not source.strip().startswith(prefix):
        raise ValueError(f'Plain-language note no longer matches source: {path}:{number}')
    return {'line': number, 'meaning': meaning}
