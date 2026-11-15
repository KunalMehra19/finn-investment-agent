"""Cache actual primary documents, not answers, for optional demo resilience."""
import asyncio,json,sys
from pathlib import Path
from backend.app.discovery import discover
ROOT=Path(__file__).resolve().parents[2]
async def main():
    docs=[]
    for ticker in sys.argv[1:] or ['HCLTECH','ASIANPAINT','AXISBANK']:
        r=await discover(ticker)
        for source in r['sources']:
            docs.append({**source,'content':[{'page':p['page'],'text':p['text']} for p in r['passages']]})
        print(ticker,len(r['sources']),len(r['passages']),flush=True)
    (ROOT/'backend/data/dynamic_library.json').write_text(json.dumps(docs,ensure_ascii=False),encoding='utf-8')
    (ROOT/'backend/data/prewarmed_sources.json').write_text(json.dumps([{k:v for k,v in d.items() if k!='content'} for d in docs],indent=2),encoding='utf-8')
if __name__=='__main__':asyncio.run(main())
