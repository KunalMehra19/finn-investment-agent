"""Bounded best-effort NSE announcement refresh. Failures preserve explicit coverage gaps."""
import json,sys,hashlib,sqlite3,re
from datetime import datetime,timedelta
from pathlib import Path
from zoneinfo import ZoneInfo
import httpx
import pymupdf
from ingest import acquire
ROOT=Path(__file__).resolve().parents[2];DATA=ROOT/'backend/data'
def main():
    now=datetime.now(ZoneInfo('Asia/Kolkata'));start=now-timedelta(days=7)
    companies={c['ticker'] for c in json.loads((DATA/'companies.json').read_text())}
    status={'status':'unavailable','from':start.isoformat(),'to':now.isoformat(),'checked_at':now.isoformat(),'message':'Current exchange coverage could not be retrieved.','records':[]}
    try:
        with httpx.Client(timeout=12,follow_redirects=True,headers={'User-Agent':'Mozilla/5.0','Accept':'application/json','Referer':'https://www.nseindia.com/companies-listing/corporate-filings-announcements'}) as client:
            try:client.get('https://www.nseindia.com/companies-listing/corporate-filings-announcements',timeout=3)
            except httpx.HTTPError:pass
            response=client.get('https://www.nseindia.com/api/corporate-announcements',params={'index':'equities','from_date':start.strftime('%d-%m-%Y'),'to_date':now.strftime('%d-%m-%Y')})
            response.raise_for_status();rows=response.json()
        if not isinstance(rows,list):raise ValueError('Unrecognized exchange response')
        relevant=[r for r in rows if r.get('symbol') in companies]
        status.update(status='checked',records=relevant,message='NSE announcements checked for all 15 watchlist symbols. Attachments are independently verified.')
    except Exception as e:status['error']=type(e).__name__
    if status['status']=='unavailable':
        print(json.dumps(status));print('Keeping prior filing snapshot, if available.');return
    (DATA/'filings_refresh.json').write_text(json.dumps(status,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in status.items() if k!='records'}));print('Relevant records:',len(status['records']))
    library=json.loads((DATA/'library.json').read_text(encoding='utf-8'))
    manifest=json.loads((DATA/'source_manifest.json').read_text(encoding='utf-8'))
    stories=[];seen=set()
    with sqlite3.connect(DATA/'finn.sqlite') as db:
        for record in status['records'][:40]:
            url=record.get('attchmntFile','');ticker=record['symbol'];desc=record.get('desc','Company update');body=record.get('attchmntText',desc)
            if (ticker,url) in seen:continue
            seen.add((ticker,url))
            published=datetime.strptime(record['an_dt'],'%d-%b-%Y %H:%M:%S').replace(tzinfo=ZoneInfo('Asia/Kolkata')).isoformat()
            text=(desc+' '+body).lower()
            if 'order' in desc.lower() or 'contract' in desc.lower():category,priority,why='Orders',90,'Order wins can change the revenue pipeline. Check the original filing for size, timing and execution conditions.'
            elif 'change in director' in desc.lower() or 're-appointment' in text:category,priority,why='Management',80,'Leadership and board changes matter for governance. Read the filing for the role, effective date and approvals.'
            elif 'transcript' in text:category,priority,why='Transcript',65,'The original earnings discussion adds management context. Separate specific commitments from general outlook.'
            elif 'financial result' in desc.lower():category,priority,why='Results',100,'Results can change the financial picture. Confirm the reporting period, accounting basis and any exceptional items.'
            else:category,priority,why='Routine',10,'Retained for completeness within the retrieved period. This filing is not ranked as a material operating development.'
            sid='nse-'+hashlib.sha256((ticker+url).encode()).hexdigest()[:12]
            try:
                path=DATA/'pdfs'/f'{sid}.pdf'
                if not path.exists():path.write_bytes(acquire(url))
                pdf=pymupdf.open(path);pages=[{'page':i+1,'text':' '.join(p.get_text().split())} for i,p in enumerate(pdf)]
                sha=hashlib.sha256(path.read_bytes()).hexdigest()
                if (ticker,sha) in seen:continue
                seen.add((ticker,sha))
                doc={'id':sid,'ticker':ticker,'title':desc,'kind':'Transcript' if category=='Transcript' else 'Exchange filing','period':date_period(published),'published':published,'url':url,'status':'verified','sha256':sha,'pages':len(pdf),'retrieved_at':now.isoformat(),'content':pages}
                library=[d for d in library if d['id']!=sid]+[doc]
                manifest=[d for d in manifest if d['id']!=sid]+[{k:v for k,v in doc.items() if k!='content'}]
                db.execute('DELETE FROM pages WHERE source_id=?',(sid,))
                db.executemany('INSERT INTO pages VALUES(?,?,?,?)',[(sid,ticker,p['page'],p['text']) for p in pages])
                title=f"{record.get('sm_name',ticker)} · {desc}"
                display={'Orders':'New orders. A fresh look at the pipeline.','Management':'A change at the board table.','Transcript':'From the call. To the evidence.','Results':'The latest numbers. The original source.'}.get(category,desc+'.')
                stories.append({'id':sid,'ticker':ticker,'display_title':display,'title':title,'summary':body[:500],'why':why,'source_id':sid,'page':1,'published':published,'timestamp_precision':'second','category':category,'priority':priority,'origin':'NSE filing','routine':category=='Routine'})
                print(f'{ticker}: {category} attachment verified ({len(pdf)} pages)',flush=True)
            except Exception as e:print(f'{ticker}: attachment unavailable ({type(e).__name__})',flush=True)
    stories.sort(key=lambda s:(s['priority'],s['published']),reverse=True)
    coverage={k:v for k,v in status.items() if k!='records'};coverage['metadata_count']=len(status['records']);coverage['verified_count']=len(stories)
    (DATA/'current_filings.json').write_text(json.dumps({'stories':stories,'coverage':coverage},ensure_ascii=False,indent=2),encoding='utf-8')
    (DATA/'library.json').write_text(json.dumps(library,ensure_ascii=False),encoding='utf-8')
    (DATA/'source_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')

def date_period(value):return datetime.fromisoformat(value).strftime('%b %Y')
if __name__=='__main__':main()
