"""Failure-oriented checks for acquisition and integration contracts."""
import io
import sys
import tempfile
import unittest
import urllib.error
from pathlib import Path
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from acquisition import CachedFetcher,AcquisitionError
from senate import find_table,SourceStructureError
from integration import join_design,merge_summaries,verify_join

class Response(io.BytesIO):
    status=200
    headers={'Content-Type':'text/html','X-RateLimit-Limit':'60'}
class FakeOpener:
    def __init__(self,error=None):self.calls=[];self.error=error
    def open(self,request,timeout):
        self.calls.append((request,timeout))
        if self.error:raise self.error
        return Response(b'archived source')

class AcquisitionTests(unittest.TestCase):
    def test_cache_memory_disk_and_honest_agent(self):
        with tempfile.TemporaryDirectory() as directory:
            opener=FakeOpener();client=CachedFetcher(directory,opener=opener)
            self.assertEqual(client.fetch('https://example.org/report'),client.fetch('https://example.org/report'))
            self.assertEqual(len(opener.calls),1)
            self.assertIn('Coursework',opener.calls[0][0].get_header('User-agent'))
            client2=CachedFetcher(directory,opener=FakeOpener(AssertionError('disk cache should avoid network')))
            self.assertEqual(client2.fetch('https://example.org/report'),b'archived source')

    def test_timeout_and_http_failure_are_loud_and_not_repeated(self):
        for error in [TimeoutError('timed out'),urllib.error.HTTPError('https://example.org',429,'rate limited',{},None)]:
            with tempfile.TemporaryDirectory() as directory:
                opener=FakeOpener(error);client=CachedFetcher(directory,opener=opener)
                for _ in range(2):
                    with self.assertRaises(AcquisitionError):client.fetch('https://example.org/report')
                self.assertEqual(len(opener.calls),1)

    def test_requests_are_spaced_at_least_one_second(self):
        with tempfile.TemporaryDirectory() as directory:
            waits=[];client=CachedFetcher(directory,opener=FakeOpener(),clock=lambda:10,sleep=waits.append)
            client.fetch('https://example.org/a');client.fetch('https://example.org/b')
            self.assertEqual(waits,[1.0])

    def test_corrupt_cached_body_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            CachedFetcher(directory,opener=FakeOpener()).fetch('https://example.org/a')
            next(Path(directory).glob('*.body')).write_bytes(b'changed')
            with self.assertRaisesRegex(AcquisitionError,'checksum'):
                CachedFetcher(directory).fetch('https://example.org/a')

class IntegrationTests(unittest.TestCase):
    def test_missing_selector_stops_parser(self):
        with self.assertRaisesRegex(SourceStructureError,'matched nothing'):
            find_table('<html><p>Maintenance page instead of data</p></html>')

    def test_fanout_is_rejected(self):
        house=pd.DataFrame({'ticker':['ABC'],'month':['2025-01'],'house_reports':[1]})
        senate=pd.DataFrame({'ticker':['ABC','ABC'],'month':['2025-01','2025-01'],'senate_reports':[1,2]})
        with self.assertRaises(pd.errors.MergeError):merge_summaries(house,senate,join_design(house,senate))

    def test_unmatched_keys_are_preserved_as_missing(self):
        house=pd.DataFrame({'ticker':['ABC','XYZ'],'month':['2025-01','2025-02'],'house_reports':[1,1]})
        senate=pd.DataFrame({'ticker':['ABC','DEF'],'month':['2025-01','2025-03'],'senate_reports':[1,1]})
        design=join_design(house,senate);joined=merge_summaries(house,senate,design)
        self.assertEqual(len(joined),3)
        self.assertTrue(pd.isna(joined.loc[joined.ticker=='XYZ','senate_reports'].iloc[0]))
        self.assertEqual(len(verify_join(joined,house,senate,design,[1,2],[1,2])),9)
        with self.assertRaises(AssertionError):
            verify_join(joined[joined._merge=='both'],house,senate,design,[1,2],[1,2])

if __name__=='__main__':unittest.main()
