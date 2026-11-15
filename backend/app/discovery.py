"""One bounded NSE route, one allowlisted PDF; no arbitrary user URLs."""
import asyncio,hashlib,re,time
from datetime import datetime,timedelta
from zoneinfo import ZoneInfo
from urllib.parse import urlparse,urljoin
import httpx,pymupdf

CACHE={}
HOSTS={'nsearchives.nseindia.com','nsearchives.nseindia.in','archives.nseindia.com'}
def safe_url(url):
    try:
        u=urlparse(url)
        return u.scheme=='https' and u.hostname in HOSTS and not u.username and not u.password and u.port in (None,443)
    except ValueError:return False

async def discover(ticker):
    if ticker in CACHE and CACHE[ticker]['expires']>time.monotonic():return CACHE[ticker]
    empty={'sources':[],'passages':[],'discovery':'No suitable original document was retrieved within the bounded discovery budget.','expires':time.monotonic()+60}
    if not re.fullmatch(r'[A-Z][A-Z0-9&-]{0,19}',ticker):return empty
    try:
        async with asyncio.timeout(16):
            now=datetime.now(ZoneInfo('Asia/Kolkata'));start=now-timedelta(days=90)
            async with httpx.AsyncClient(timeout=8,follow_redirects=False,headers={'User-Agent':'Mozilla/5.0'}) as client:
                r=await client.get('https://www.nseindia.com/api/corporate-announcements',params={'index':'equities','symbol':ticker,'from_date':start.strftime('%d-%m-%Y'),'to_date':now.strftime('%d-%m-%Y')})
                if r.is_redirect:
                    target=urljoin(str(r.url),r.headers.get('location',''))
                    if urlparse(target).hostname not in {'www.nseindia.in','www.nseindia.com'}:raise ValueError()
                    r=await client.get(target)
                r.raise_for_status();rows=r.json()
                if not isinstance(rows,list):raise ValueError()
                choices=[x for x in rows if x.get('symbol')==ticker and safe_url(x.get('attchmntFile','')) and re.search(r'transcript|annual.report|financial.results',x.get('desc','')+' '+x.get('attchmntText',''),re.I) and not re.search('intimation|schedule|audio|newspaper',x.get('desc',''),re.I)]
                choices.sort(key=lambda x:'transcript' in x.get('attchmntText','').lower(),reverse=True)
                if not choices:raise ValueError()
                row=choices[0];url=row['attchmntFile'];body=None
                for _ in range(3):
                    if not safe_url(url):raise ValueError()
                    async with client.stream('GET',url) as pdf_response:
                        if pdf_response.is_redirect:
                            url=urljoin(url,pdf_response.headers['location']);continue
                        pdf_response.raise_for_status();buffer=bytearray()
                        async for chunk in pdf_response.aiter_bytes():
                            buffer.extend(chunk)
                            if len(buffer)>5_000_000:raise ValueError()
                        body=bytes(buffer);break
                if not body or not body.startswith(b'%PDF-'):raise ValueError()
            with pymupdf.open(stream=body,filetype='pdf') as pdf:
                if len(pdf)>80:raise ValueError()
                text=[' '.join(p.get_text().split())[:7500] for p in pdf]
            if sum(len(t) for t in text)<100:raise ValueError()
            sha=hashlib.sha256(body).hexdigest();sid='dynamic-'+ticker+'-'+sha[:12]
            try:published=datetime.strptime(row['an_dt'],'%d-%b-%Y %H:%M:%S').replace(tzinfo=ZoneInfo('Asia/Kolkata')).isoformat()
            except (ValueError,KeyError):published=None
            source={'id':sid,'ticker':ticker,'title':row.get('attchmntText') or row['desc'],'kind':'Transcript' if 'transcript' in row.get('attchmntText','').lower() else 'Exchange filing','period':'Period in original document','published':published,'url':row['attchmntFile'],'pages':len(text),'page':1,'excerpt':'','status':'verified','sha256':sha,'retrieved_at':now.isoformat()}
            result={'sources':[source],'passages':[{'ticker':ticker,'source_id':sid,'page':i+1,'text':t} for i,t in enumerate(text)],'discovery':'Original NSE attachment retrieved and indexed for this request.','expires':time.monotonic()+43200}
            if len(CACHE)>=24:CACHE.pop(next(iter(CACHE)))
            CACHE[ticker]=result;return result
    except (Exception,TimeoutError):CACHE[ticker]=empty;return empty

def source_by_id(sid):return next((s for r in CACHE.values() for s in r['sources'] if s['id']==sid),None)
