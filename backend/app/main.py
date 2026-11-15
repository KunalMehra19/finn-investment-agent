import asyncio,json,os,re,time
from collections import defaultdict,deque
from datetime import datetime,timedelta,timezone
from pathlib import Path
from contextlib import asynccontextmanager
from zoneinfo import ZoneInfo
import httpx
from fastapi import FastAPI,HTTPException,Query,Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel,Field
from dotenv import load_dotenv
from .market import load_market,refresh_market
from .research import answer_question,dataset

ROOT=Path(__file__).resolve().parents[2];DATA=ROOT/'backend/data'
load_dotenv(ROOT/'.env')
requests=defaultdict(deque);global_calls=deque();dynamic_cache={}
app=FastAPI(title='FINN Evidence API',version='1.0.0')
app.add_middleware(CORSMiddleware,allow_origins=os.getenv('FINN_ALLOWED_ORIGINS','http://127.0.0.1:5173,http://localhost:5173').split(','),allow_methods=['GET','POST'],allow_headers=['Content-Type'])

def symbol(ticker):
    value=ticker.upper().removesuffix('.NS')
    if not re.fullmatch(r'[A-Z][A-Z0-9&-]{0,19}',value):raise HTTPException(400,'Invalid NSE symbol')
    return value

def rate_limit(request,kind='research',maximum=8):
    now=time.monotonic();key=(request.client.host if request.client else 'local',kind);q=requests[key]
    while q and q[0]<now-60:q.popleft()
    if len(q)>=maximum:raise HTTPException(429,'Please wait a moment before trying again.')
    q.append(now)

@app.get('/api/health')
def health():
    d=dataset();return {'status':'ready','as_of':d['coverage']['as_of'],'documents':len(d['sources']),'eod_available':len(load_market().get('prices',{})),'gemini_configured':bool(os.getenv('GEMINI_API_KEY')),'current_filings':d.get('filing_coverage',{}).get('status','not_checked')}

@app.get('/api/snapshot')
def snapshot():
    d=dataset();d['market']=load_market();return d

@app.get('/api/watchlist')
def watchlist():
    d=dataset();m=load_market();return {'companies':[{**c,'price':m.get('prices',{}).get(c['ticker']),'document_count':sum(s['ticker']==c['ticker'] for s in d['sources'])} for c in d['companies']],'as_of':m.get('fetched_at'),'coverage':d['coverage']}

@app.get('/api/briefing')
def briefing(window:str=Query('24h',pattern='^(24h|7d)$'),mode:str=Query('current',pattern='^(current|replay)$')):
    d=dataset();cutoff=datetime.now(timezone.utc)-timedelta(days=7 if window=='7d' else 1)
    stories=d['stories'] if mode=='replay' else [s for s in d.get('current_stories',[]) if cutoff<=datetime.fromisoformat(s['published'])<=datetime.now(timezone.utc)]
    # De-duplicate a filing notified through multiple channels and sort materiality first.
    stories=list({(s['ticker'],s['source_id']):s for s in stories}.values())
    stories.sort(key=lambda s:(s['priority'],s['published']),reverse=True)
    return {'stories':stories,'mode':mode,'window':window,'market':load_market(),'coverage':{'status':'historical' if mode=='replay' else d.get('filing_coverage',{}).get('status','unavailable'),'message':d['coverage']['filings']},'as_of':d['coverage']['as_of']}

@app.get('/api/company/{ticker}')
async def company(ticker:str,request:Request):
    t=symbol(ticker);d=dataset();c=next((c for c in d['companies'] if c['ticker']==t),None)
    if c:return {'company':c,'price':load_market().get('prices',{}).get(t),'facts':d['facts'].get(t,[]),'documents':[s for s in d['sources'] if s['ticker']==t],'status':'verified' if c['deep'] else 'partial','as_of':d['coverage']['as_of']}
    rate_limit(request,'ticker',6)
    if t in dynamic_cache and dynamic_cache[t][0]>time.monotonic()-43200:return dynamic_cache[t][1]
    try:
        async with httpx.AsyncClient(timeout=14) as client:
            r=await client.get(f'https://query1.finance.yahoo.com/v8/finance/chart/{t}.NS',params={'range':'3mo','interval':'1d'},headers={'User-Agent':'Mozilla/5.0'})
            r.raise_for_status();result=r.json()['chart']['result'][0];meta=result['meta']
        if meta.get('symbol')!=t+'.NS' or meta.get('exchangeName') not in ('NSI','NSE'):raise ValueError('Identity mismatch')
        from .market import summarize
        q=result['indicators']['quote'][0]
        rows=[{'date':datetime.fromtimestamp(ts,ZoneInfo('Asia/Kolkata')).date().isoformat(),'close':float(close),'volume':int(volume)} for ts,close,volume in zip(result['timestamp'],q['close'],q['volume']) if close is not None and volume is not None]
        p=summarize(rows)
        value={'company':{'ticker':t,'name':meta.get('longName') or meta.get('shortName') or t,'short':meta.get('shortName') or t,'sector':'NSE equity','color':'#697d57','initials':t[:2],'deep':False},'price':p,'documents':[],'status':'partial','message':'Document research unavailable for this ticker.','as_of':datetime.now(timezone.utc).isoformat()}
        dynamic_cache[t]=(time.monotonic(),value);return value
    except Exception:raise HTTPException(404,'Symbol could not be verified with the provider.')

class ResearchRequest(BaseModel):
    ticker:str=Field(min_length=1,max_length=24)
    question:str=Field(min_length=3,max_length=1000)

@app.post('/api/research')
async def research(body:ResearchRequest,request:Request):
    rate_limit(request);t=symbol(body.ticker)
    now=time.monotonic()
    while global_calls and global_calls[0]<now-86400:global_calls.popleft()
    if len(global_calls)>=100:raise HTTPException(429,'Daily research budget reached. Indexed evidence is still available.')
    global_calls.append(now)
    return await answer_question(t,body.question)

@app.get('/api/ledger/{ticker}')
def ledger(ticker:str):
    d=dataset();t=symbol(ticker);return {'records':[r for r in d['ledger'] if r['ticker']==t],'as_of':d['coverage']['as_of']}

@app.get('/api/sources/{source_id}')
def sources(source_id:str):
    result=next((s for s in dataset()['sources'] if s['id']==source_id),None)
    if not result:raise HTTPException(404,'Source not found')
    return result

@app.post('/api/refresh')
async def refresh(request:Request):
    rate_limit(request,'refresh',2)
    await asyncio.to_thread(refresh_market,[c['ticker'] for c in dataset()['companies']])
    return snapshot()

if (ROOT/'dist/index.html').exists():app.mount('/',StaticFiles(directory=ROOT/'dist',html=True),name='frontend')
