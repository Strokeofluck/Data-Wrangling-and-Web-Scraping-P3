"""Build P3's House dataset from this repository's PDFs, parser, and review rules."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
import sys
import uuid
from decimal import Decimal, InvalidOperation
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {'filing_id', 'transaction_number_in_filing', 'politician', 'owner',
            'asset_v8_2_cleaned', 'ticker_v8_2_cleaned', 'asset_type',
            'transaction_type', 'transaction_date', 'notification_date',
            'amount_raw', 'amount_min', 'amount_max', 'original_pdf_url',
            'comments', 'needs_review', 'ticker_parse_status'}


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def input_recipe(root):
    """Verify primary PDFs and bundled code, then identify the exact local recipe."""
    manifest = root / 'data/raw/2025_pdf_manifest.csv'
    with manifest.open(encoding='utf-8', newline='') as stream:
        pdfs = list(csv.DictReader(stream))
    if len(pdfs) != 515 or len({row['filename'] for row in pdfs}) != len(pdfs):
        raise ValueError('House PDF inventory is incomplete or duplicated')
    for row in pdfs:
        path = root / 'data/raw/2025_pdfs' / row['filename']
        if not path.is_file() or sha256(path) != row['sha256']:
            raise ValueError(f'House source PDF checksum mismatch: {path.name}')
    parser_files = json.loads((root / 'vendor/house-ptr-scraper/SHA256.json').read_text())
    for name, expected in parser_files.items():
        path = root / 'vendor/house-ptr-scraper/src' / name
        if not path.is_file() or sha256(path) != expected:
            raise ValueError(f'Bundled House parser checksum mismatch: {name}')
    files = ['data/raw/2025_pdf_manifest.csv', 'data/review/decisions.json',
             'scripts/house.py', 'scripts/rebuild_house.py']
    return {'files': {name: sha256(root / name) for name in files},
            'parser_files': parser_files, 'pdf_count': len(pdfs)}


def same_value(left, right):
    if str(left) == str(right):
        return True
    try:
        return Decimal(str(left)) == Decimal(str(right))
    except InvalidOperation:
        return False


def apply_reviews(frame, decisions):
    """Replay checked, repository-local review decisions on newly parsed evidence."""
    frame = frame.copy()
    keys = ['filing_id', 'transaction_number_in_filing']
    if frame.duplicated(keys).any():
        raise ValueError('Duplicate House filing/row identity before review')
    changes = []
    reviewed = set()
    for decision in decisions:
        for item in decision['rows']:
            row_id = str(item['transaction_number_in_filing'])
            selected = frame.index[frame.filing_id.eq(decision['filing_id']) &
                                   frame.transaction_number_in_filing.eq(row_id)]
            if len(selected) != 1:
                raise ValueError(f'Review must match exactly one House row: {decision["id"]}/{row_id}')
            index = selected[0]
            reviewed.add((decision['filing_id'], row_id))
            for column, expected in item['before'].items():
                if not same_value(frame.at[index, column], expected):
                    raise ValueError(f'Review evidence changed: {decision["id"]}/{row_id}/{column}')
            for column, value in item['after'].items():
                before = frame.at[index, column]
                if same_value(before, value):
                    continue
                audit_column = column + '_before_review'
                if audit_column not in frame:
                    frame[audit_column] = ''
                frame.at[index, audit_column] = before
                frame.at[index, column] = value
                changes.append({'filing_id': decision['filing_id'], 'row': row_id,
                                'column': column, 'before': before, 'after': value,
                                'decision': decision['id'], 'reason': decision['reason']})
    return frame, {'reviewed_rows': len(reviewed), 'changed_cells': len(changes), 'changes': changes}


def validate_extract(frame):
    missing = REQUIRED - set(frame.columns)
    if missing or frame.empty:
        raise ValueError(f'House extraction schema missing required fields: {sorted(missing)}')
    if frame.duplicated(['filing_id', 'transaction_number_in_filing']).any():
        raise ValueError('Duplicate House filing/row identity')


def extract_house(root=ROOT, rebuild=False):
    """Use P3's verified output, or regenerate it entirely from its own inputs."""
    root = Path(root).resolve()
    recipe = input_recipe(root)
    signature = hashlib.sha256(json.dumps(recipe, sort_keys=True).encode()).hexdigest()
    output = root / 'data/processed/house_extracted.csv'
    record = root / 'data/processed/house_extraction.json'
    if not rebuild and output.exists() and record.exists():
        saved = json.loads(record.read_text())
        if saved.get('input_signature') == signature:
            if sha256(output) != saved['output_sha256']:
                raise ValueError('P3 House output checksum mismatch; run python scripts/house.py --rebuild')
            frame = pd.read_csv(output, dtype=str, keep_default_na=False)
            validate_extract(frame)
            return frame

    # A new workspace never resumes checkpoints from a different recipe or run.
    work = root / 'data/work/house_runs' / (signature[:16] + '-' + uuid.uuid4().hex[:8])
    work.mkdir(parents=True)
    log_path = work / 'build.log'
    print('Building P3 House input from 515 bundled PDFs; progress log:', log_path.relative_to(root), flush=True)
    with log_path.open('w', encoding='utf-8') as log:
        subprocess.run([sys.executable, '-u', str(root / 'scripts/rebuild_house.py'),
                        '--work-dir', str(work)], cwd=root, stdout=log,
                       stderr=subprocess.STDOUT, check=True)
    frame = pd.read_csv(work / '04_transactions/transactions_resolved.csv', dtype=str, keep_default_na=False)
    validate_extract(frame)
    decisions = json.loads((root / 'data/review/decisions.json').read_text())
    frame, review = apply_reviews(frame, decisions)
    checkpoint = pd.read_csv(work / '05_status/checkpoint.csv', dtype=str, keep_default_na=False)
    if len(checkpoint) != recipe['pdf_count']:
        raise ValueError('House rebuild stopped before every captured PDF was accounted for')
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix('.csv.tmp')
    frame.to_csv(temporary, index=False)
    temporary.replace(output)
    saved = {'input_signature': signature, 'recipe': recipe, 'rows': len(frame),
             'parsed_filings': int(frame.filing_id.nunique()),
             'filings_without_rows': recipe['pdf_count'] - int(frame.filing_id.nunique()),
             'review': review, 'output_sha256': sha256(output)}
    record.write_text(json.dumps(saved, indent=2) + '\n', encoding='utf-8')
    print(f'Built P3 House dataset: {len(frame):,} rows from {saved["parsed_filings"]} parsed filings.', flush=True)
    return frame


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rebuild', action='store_true', help='Reparse every bundled PDF in a new local workspace')
    args = parser.parse_args()
    extract_house(rebuild=args.rebuild)
