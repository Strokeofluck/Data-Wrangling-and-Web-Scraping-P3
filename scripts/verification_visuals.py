"""Render the exact real summary row copied in the duplicate-key demonstration."""
from html import escape
import hashlib
import json
import pandas as pd
from bs4 import BeautifulSoup


def original_filing_evidence(root):
    """Trace the demonstration key to unchanged raw HTML and its screenshot."""
    summary = pd.read_csv(root/'data/processed/senate_ticker_month.csv')
    key = summary.iloc[0]
    transactions = pd.read_csv(root/'data/processed/senate_transactions_2025.csv', dtype=str, keep_default_na=False)
    selected = transactions[(transactions.ticker == key.ticker) & (transactions.month == key.month)]
    manifest = json.loads((root/'provenance/duplicate_source_images.json').read_text(encoding='utf-8'))
    images = {entry['filing_id']: entry for entry in manifest}
    assert set(selected.filing_id) == set(images), 'Source images must cover the exact demonstration records'
    raw_hashes = json.loads((root/'provenance/raw_sha256.json').read_text())
    from senate import find_table, HEADERS
    evidence = []
    for record in selected.to_dict('records'):
        ident = record['filing_id']
        raw_path = f'data/raw/senate/html/{ident}.html'
        data = (root/raw_path).read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        assert digest == raw_hashes[raw_path], 'The original source HTML changed'
        soup = BeautifulSoup(data, 'html.parser')
        table = find_table(data.decode('utf-8'))
        rows = [[cell.get_text(' ', strip=True) for cell in tr.find_all('td', recursive=False)] for tr in table.select('tbody tr')]
        raw_row = next(values for values in rows if values[0] == record['row_number'])
        assert raw_row[3] == record['ticker'] and raw_row[4] == record['asset_name']
        assert raw_row[6] == record['transaction_type'] and raw_row[7] == record['amount_raw']
        image = images[ident]['image']
        assert (root/'docs'/image).is_file()
        evidence.append({'filing_id': ident, 'title': soup.find('h1').get_text(' ', strip=True),
                         'filer': soup.find('h2').get_text(' ', strip=True), 'filing_date': record['filing_date'],
                         'row_number': record['row_number'], 'headers': HEADERS, 'raw_cells': raw_row,
                         'original_url': record['source_url'], 'raw_path': raw_path, 'image': image,
                         'sha256': digest, 'image_sha256': hashlib.sha256((root/'docs'/image).read_bytes()).hexdigest(),
                         'capture_note': images[ident]['capture_note']})
    assert len(evidence) == int(key.senate_reports)
    return evidence


def duplicate_key_svg(senate, failure):
    """Return a portable SVG with real values and a clearly labeled test copy."""
    keys = ['ticker', 'month']
    assert not senate.duplicated(keys).any(), 'Original Senate summary must have unique keys'
    original = senate.iloc[[0]].copy(deep=True)
    assert original.iloc[0][keys].to_dict() == failure['changed_key']
    test = pd.concat([original, original.copy(deep=True)], ignore_index=True)
    assert test.duplicated(keys, keep=False).all()
    assert failure['caught'] == 'MergeError'
    columns = keys + ['senate_reports', 'senate_filings', 'senate_filers', 'senate_purchases', 'senate_sales']
    widths = [246, 115, 155, 124, 124, 124, 124, 124]
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="680" viewBox="0 0 1200 680" role="img" aria-labelledby="dup-title dup-desc">',
             '<title id="dup-title">Real Senate row and duplicate added only to a test copy</title>',
             '<desc id="dup-desc">The original summary has unique ticker-month keys. The actual first row is repeated only for testing. The one-to-one merge raises a MergeError.</desc>',
             '<rect width="1200" height="680" fill="#ffffff"/>',
             '<g font-family="Arial, sans-serif" fill="#343a40">']

    def text(x, y, value, size=18, weight=400, fill='#343a40'):
        parts.append(f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{fill}">{escape(str(value))}</text>')

    def table(y, frame, labels, highlight=False):
        headings = ['Row origin', 'Ticker', 'Month', 'Reports', 'Filings', 'Filers', 'Purchases', 'Sales']
        x = 32
        for i, (heading, width) in enumerate(zip(headings, widths)):
            fill = '#fff0d7' if highlight and i in (1, 2) else '#f1f3f5'
            parts.append(f'<rect x="{x}" y="{y}" width="{width}" height="36" fill="{fill}" stroke="#dee2e6"/>')
            text(x+12, y+24, heading, 17, 700)
            x += width
        for row_index, (_, row) in enumerate(frame.iterrows()):
            values = [labels[row_index]] + [row[column] for column in columns]
            x = 32
            for col_index, (value, width) in enumerate(zip(values, widths)):
                fill = '#fff0d7' if highlight and col_index in (1, 2) else '#ffffff'
                top = y+36+row_index*44
                parts.append(f'<rect x="{x}" y="{top}" width="{width}" height="44" fill="{fill}" stroke="#dee2e6"/>')
                text(x+12, top+28, value, 18, 700 if col_index in (1, 2) else 400)
                x += width

    text(32, 48, 'See the duplicate the check rejects', 30, 700)
    text(32, 83, 'One real summary row, copied only for the failure test. The source data stays unchanged.', 19)
    text(32, 132, '1. Original Senate summary: one row for this key', 22, 700)
    table(150, original, ['Actual saved row'])
    text(32, 289, '2. Test copy: the same row appears twice', 22, 700)
    table(310, test, ['Original row', 'Added copy (test only)'], highlight=True)
    row = original.iloc[0]
    text(32, 463, f"Repeated join key: {row.ticker} + {row.month}. Both rows also carry the same reported counts.", 19, 700)
    parts.append('<rect x="32" y="496" width="1136" height="96" fill="#fff0d7" stroke="#b66a00"/>')
    text(50, 529, "BLOCKED: validate='one_to_one' stops the merge", 21, 700, '#7c4700')
    text(50, 565, f"{failure['caught']}: {failure['message']}", 17, 400, '#7c4700')
    text(32, 630, f"Saved Senate summary: {len(senate):,} rows; 0 duplicate ticker-month keys.", 18, 700)
    text(32, 658, 'Source: data/processed/senate_ticker_month.csv. Duplicate exists only in the test copy.', 16)
    parts.append('</g></svg>')
    return ''.join(parts)
