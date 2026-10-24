"""Contracts that keep P3's regenerated House input independent and auditable."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from house import ROOT, apply_reviews, extract_house


class HouseExtractionTests(unittest.TestCase):
    def fixture(self):
        frame = pd.DataFrame([{'filing_id': 'example', 'transaction_number_in_filing': '1',
                               'amount_exact': '', 'amount_status': 'missing_range_bound',
                               'amount_raw': '$2,000.00', 'needs_review': 'True'}])
        decisions = [{'id': 'exact', 'filing_id': 'example', 'reason': 'Source reports an exact amount',
                      'rows': [{'transaction_number_in_filing': '1',
                                'before': {'amount_exact': '', 'amount_status': 'missing_range_bound'},
                                'after': {'amount_exact': '2000.0', 'amount_status': 'nonstandard_exact'}}]}]
        return frame, decisions

    def test_review_preserves_evidence_and_original_flags(self):
        frame, decisions = self.fixture()
        output, audit = apply_reviews(frame, decisions)
        self.assertEqual(len(output), len(frame))
        self.assertEqual(output.loc[0, 'amount_exact'], '2000.0')
        self.assertEqual(output.loc[0, 'amount_raw'], '$2,000.00')
        self.assertEqual(output.loc[0, 'amount_status_before_review'], 'missing_range_bound')
        self.assertEqual(output.loc[0, 'needs_review'], 'True')
        self.assertEqual(audit['changed_cells'], 2)

    def test_changed_review_evidence_is_rejected(self):
        frame, decisions = self.fixture()
        frame.loc[0, 'amount_status'] = 'unexpected value'
        with self.assertRaisesRegex(ValueError, 'Review evidence changed'):
            apply_reviews(frame, decisions)

    def test_review_cannot_target_missing_or_duplicated_identity(self):
        frame, decisions = self.fixture()
        with self.assertRaisesRegex(ValueError, 'Duplicate House'):
            apply_reviews(pd.concat([frame, frame]), decisions)
        decisions[0]['rows'][0]['transaction_number_in_filing'] = '99'
        with self.assertRaisesRegex(ValueError, 'exactly one House row'):
            apply_reviews(frame, decisions)

    def test_pipeline_reads_own_extract_not_the_finished_p2_table(self):
        read_csv = pd.read_csv
        opened = []
        def checked_read(path, *args, **kwargs):
            self.assertNotEqual(Path(path).name, 'house_transactions_p2.csv')
            opened.append(Path(path).resolve())
            return read_csv(path, *args, **kwargs)
        with patch('house.pd.read_csv', side_effect=checked_read):
            frame = extract_house(ROOT)
        self.assertEqual(len(frame), 7667)
        self.assertIn((ROOT / 'data/processed/house_extracted.csv').resolve(), opened)

    def test_altered_generated_cache_is_rejected_without_silent_rebuild(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            output = root / 'data/processed/house_extracted.csv'
            output.parent.mkdir(parents=True)
            output.write_bytes(b'original')
            record = {'input_signature': hashlib.sha256(json.dumps({}, sort_keys=True).encode()).hexdigest(),
                      'output_sha256': hashlib.sha256(output.read_bytes()).hexdigest()}
            output.with_name('house_extraction.json').write_text(json.dumps(record))
            output.write_bytes(b'changed')
            with patch('house.input_recipe', return_value={}), patch('house.subprocess.run') as runner:
                with self.assertRaisesRegex(ValueError, 'output checksum mismatch'):
                    extract_house(root)
                runner.assert_not_called()


if __name__ == '__main__':
    unittest.main()
