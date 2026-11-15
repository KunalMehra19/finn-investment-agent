"""Unauthenticated public endpoint checks, without browser or secret disclosure."""
import json,time
from datetime import datetime,timezone
from pathlib import Path
import httpx
BASE='https://finn-research-desk.delicateloon4.chatgpt.site'
rows=[]
with httpx.Client(timeout=50,follow_redirects=True) as client:
    for path in ['/','/api/health','/api/watchlist','/api/briefing?mode=current&window=7d','/api/ledger/TCS','/api/sources/ril-fy25']:
        r=client.get(BASE+path);row={'path':path,'status':r.status_code,'public_without_auth':r.status_code==200 and not any('login' in str(h.url) for h in r.history)}
        if path=='/api/health' and r.status_code==200:row['health']=r.json()
        rows.append(row);print(json.dumps(row),flush=True)
    for ticker,question in [('TCS','What changed in operating margins from FY25 to FY26?'),('SUNPHARMA','How did R&D spending compare with management guidance?'),('HCLTECH','Summarize management business outlook and risks from the available earnings call.')]:
        start=time.monotonic();r=client.post(BASE+'/api/research',json={'ticker':ticker,'question':question});a=r.json()
        row={'path':'/api/research','ticker':ticker,'http_status':r.status_code,'engine':a.get('engine'),'status':a.get('status'),'claims':len(a.get('insights',[])),'dynamic_sources':len(a.get('sources',[])),'seconds':round(time.monotonic()-start,2)}
        rows.append(row);print(json.dumps(row),flush=True)
        for i in a.get('insights',[])[:2]:
            source=client.get(BASE+'/api/sources/'+i['source_id']);assert source.status_code==200,'Citation failed';assert i['page']<=source.json()['pages']
    invalid=client.get(BASE+'/api/company/BAD!SYMBOL');rows.append({'path':'/api/company/BAD!SYMBOL','status':invalid.status_code,'expected':400})
result={'checked_at':datetime.now(timezone.utc).isoformat(),'base_url':BASE,'checks':rows}
(Path(__file__).resolve().parents[2]/'docs/PUBLIC_ENDPOINT_REVIEW.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
assert all(r.get('public_without_auth',True) for r in rows),'Public access failed'
assert any(r.get('ticker')=='TCS' and 'Gemini' in r.get('engine','') and r.get('claims',0)>0 for r in rows),'Hosted Gemini did not return supported claims'
