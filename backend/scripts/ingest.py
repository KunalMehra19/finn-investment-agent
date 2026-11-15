"""Download a bounded allowlisted issuer library, extract page-level evidence and index FTS5."""
import hashlib, json, sqlite3, sys, re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
import fitz, httpx

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'backend/data'
ALLOWED = {'www.ril.com', 'www.tcs.com', 'www.hdfc.bank.in', 'assets.airtel.in', 'sunpharma.com', 'nsearchives.nseindia.com', 'nsearchives.nseindia.in'}

def acquire(url):
    if urlparse(url).scheme != 'https' or urlparse(url).hostname not in ALLOWED:
        raise ValueError('Source domain is not allowed')
    with httpx.Client(timeout=18, follow_redirects=False) as client:
        for _ in range(4):
            with client.stream('GET', url, headers={'User-Agent':'FINN-Research-Demo/1.0'}) as r:
                if r.is_redirect:
                    from urllib.parse import urljoin
                    url = urljoin(url, r.headers['location'])
                    if urlparse(url).scheme != 'https' or urlparse(url).hostname not in ALLOWED:
                        raise ValueError('Unapproved redirect')
                    continue
                r.raise_for_status()
                body = bytearray()
                for chunk in r.iter_bytes():
                    body.extend(chunk)
                    if len(body)>25_000_000: raise ValueError('PDF exceeds 25 MB')
                if not body.startswith(b'%PDF'): raise ValueError('Response is not a PDF')
                return bytes(body)
    raise ValueError('Too many redirects')

def main():
    docs=json.loads((DATA/'source_manifest.json').read_text(encoding='utf-8'))
    (DATA/'pdfs').mkdir(exist_ok=True)
    db=sqlite3.connect(DATA/'finn.sqlite')
    db.execute('CREATE VIRTUAL TABLE IF NOT EXISTS pages USING fts5(source_id UNINDEXED, ticker UNINDEXED, page UNINDEXED, text)')
    records=[]
    for doc in docs:
        try:
            path=DATA/'pdfs'/f"{doc['id']}.pdf"
            if not path.exists(): path.write_bytes(acquire(doc['url']))
            body=path.read_bytes()
            pdf=fitz.open(stream=body,filetype='pdf')
            db.execute('DELETE FROM pages WHERE source_id=?',(doc['id'],))
            pages=[]
            for n,p in enumerate(pdf):
                text=' '.join(p.get_text().split())
                db.execute('INSERT INTO pages VALUES(?,?,?,?)',(doc['id'],doc['ticker'],n+1,text))
                pages.append({'page':n+1,'text':text})
            doc.update(status='verified',sha256=hashlib.sha256(body).hexdigest(),pages=len(pdf),retrieved_at=datetime.now(timezone.utc).isoformat())
            records.append({**doc,'content':pages})
            print(f"{doc['id']}: verified {len(pdf)} pages",flush=True)
        except Exception as e:
            doc.update(status='unavailable',error=type(e).__name__)
            print(f"{doc['id']}: {type(e).__name__}: {e}",flush=True)
    db.commit();db.close()
    (DATA/'library.json').write_text(json.dumps(records,ensure_ascii=False),encoding='utf-8')
    (DATA/'source_manifest.json').write_text(json.dumps(docs,ensure_ascii=False,indent=2),encoding='utf-8')

if __name__=='__main__': main()
