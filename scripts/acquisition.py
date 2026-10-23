"""Polite, immutable HTTP cache for the frozen P3 acquisition plan.

No login, agreement submission, CAPTCHA handling, or access-control bypass.
The default Senate origin is a pinned copy of Sean's previously collected HTML.
"""
from __future__ import annotations
import hashlib
import json
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
USER_AGENT = 'DSA405-P3-Coursework/1.0 (Sean Ryan; noncommercial academic acquisition)'

class AcquisitionError(RuntimeError):
    pass

class CachedFetcher:
    def __init__(self, cache_dir=None, interval=1.0, opener=None, clock=time.monotonic, sleep=time.sleep):
        if interval < 1.0:
            raise ValueError('Coursework rate limit must be at least one second.')
        self.cache_dir = Path(cache_dir or ROOT/'data/raw/http_cache')
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.interval, self.clock, self.sleep = interval, clock, sleep
        self.opener = opener or urllib.request.build_opener()
        self.last_request = None
        self.seen = {}
        self.events = []

    def fetch(self, url):
        # Both successful and failed attempts are memoized: no repeated resource in a run.
        if url in self.seen:
            result = self.seen[url]
            if isinstance(result, Exception): raise result
            self.events.append({'url':url,'from':'memory'})
            return result
        key = hashlib.sha256(url.encode()).hexdigest()
        body_path = self.cache_dir/f'{key}.body'
        meta_path = self.cache_dir/f'{key}.json'
        if body_path.exists() and meta_path.exists():
            body = body_path.read_bytes()
            meta = json.loads(meta_path.read_text(encoding='utf-8'))
            if hashlib.sha256(body).hexdigest() != meta['sha256']:
                raise AcquisitionError(f'Cache checksum mismatch for {url}')
            self.seen[url] = body
            self.events.append({'url':url,'from':'disk','sha256':meta['sha256']})
            return body
        if body_path.exists() or meta_path.exists():
            raise AcquisitionError(f'Incomplete cache pair for {url}; inspect it before recovery.')
        if self.last_request is not None:
            self.sleep(max(0, self.interval-(self.clock()-self.last_request)))
        self.last_request = self.clock()
        request = urllib.request.Request(url, headers={'User-Agent':USER_AGENT})
        try:
            with self.opener.open(request, timeout=30) as response:
                status = response.status
                if status != 200: raise AcquisitionError(f'HTTP {status}: {url}')
                body = response.read()
                safe_headers={'content-type','date','etag','last-modified','content-length',
                              'x-ratelimit-limit','x-ratelimit-remaining','x-ratelimit-reset','retry-after'}
                headers = {k:v for k,v in response.headers.items() if k.lower() in safe_headers}
            if not body: raise AcquisitionError(f'Empty response: {url}')
        except (urllib.error.URLError, TimeoutError, OSError, AcquisitionError) as exc:
            error = AcquisitionError(f'Acquisition stopped for {url}: {exc}')
            self.seen[url] = error
            raise error from exc
        meta = {'url':url,'status':status,'headers':headers,'user_agent':USER_AGENT,
                'retrieved_at_utc':datetime.now(timezone.utc).isoformat(),
                'sha256':hashlib.sha256(body).hexdigest()}
        # Exclusive creation prevents a refresh from silently overwriting an archive.
        with body_path.open('xb') as stream: stream.write(body)
        with meta_path.open('x',encoding='utf-8') as stream: json.dump(meta,stream,indent=2)
        self.seen[url] = body
        self.events.append({'url':url,'from':'network','status':status,'sha256':meta['sha256']})
        return body

def acquisition_plan():
    """A finite archived filing inventory has no pagination; every file is enumerated.

    Original Senate live-discovery pagination is retained in provenance; this
    coursework snapshot deliberately does not search the current agreement-gated site.
    """
    manifest=json.loads((ROOT/'provenance/raw_sha256.json').read_text())
    commits=json.loads((ROOT/'provenance/source_commits.json').read_text())
    plan=[]
    for path, digest in manifest.items():
        if path.startswith('data/raw/senate/html/'):
            name=Path(path).name
            # Git on Windows checked text out as CRLF. GitHub raw serves the
            # committed LF bytes; keep the archived file unchanged and record
            # its separate transport checksum rather than mislabel EOL drift.
            transport=hashlib.sha256((ROOT/path).read_bytes().replace(b'\r\n',b'\n')).hexdigest()
            plan.append({'path':path,'sha256':transport,'archive_sha256':digest,
                'url':f"https://raw.githubusercontent.com/Strokeofluck/senate-ptr-scraper/{commits['Senate']['commit']}/data/01_html/{name}",
                'official_url':f'https://efdsearch.senate.gov/search/view/ptr/{Path(name).stem}/'})
        elif path.startswith('data/raw/2025_pdfs/'):
            name=Path(path).name
            plan.append({'path':path,'sha256':digest,
                'url':f'https://disclosures-clerk.house.gov/public_disc/ptr-pdfs/2025/{name}'})
    return plan

def acquire(limit=None, chamber=None):
    client=CachedFetcher()
    plan=acquisition_plan()
    if chamber: plan=[r for r in plan if ('/senate/' in r['path']) == (chamber=='Senate')]
    if limit is not None: plan=plan[:limit]
    for item in plan:
        body=client.fetch(item['url'])
        if hashlib.sha256(body).hexdigest()!=item['sha256']:
            raise AcquisitionError(f"Source changed relative to the pinned snapshot: {item['url']}")
    out=ROOT/'data/processed/acquisition_receipt.json'
    out.write_text(json.dumps(client.events,indent=2),encoding='utf-8')
    return client.events

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--limit',type=int)
    parser.add_argument('--chamber',choices=['House','Senate'])
    args=parser.parse_args()
    print(json.dumps(acquire(args.limit,args.chamber),indent=2))
