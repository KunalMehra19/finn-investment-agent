"""Explicit live functional checks. Output contains results, never API credentials."""
import asyncio,json,time
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parents[2]/'.env')
from backend.app.research import answer_question

async def main():
    results=[]
    for ticker,question in [('RELIANCE','What drove revenue and earnings growth in FY25?'),('TCS','What changed in operating margins from FY25 to FY26?'),('HDFCBANK','What do NII and net interest margin show?'),('BHARTIARTL','What drove mobile ARPU and revenue growth?'),('SUNPHARMA','How did R&D spending compare with management guidance?'),('HCLTECH','Summarize management business outlook and risks from the available earnings call.')]:
        start=time.monotonic();a=await answer_question(ticker,question)
        row={'ticker':ticker,'question':question,'engine':a['engine'],'status':a['status'],'claims':len(a['insights']),'dynamic_sources':len(a.get('sources',[])),'seconds':round(time.monotonic()-start,2),'citations':[{'source_id':i['source_id'],'page':i['page']} for i in a['insights']]}
        row.update(ai_status=a.get('ai_status'),finish_reason=a.get('finish_reason'));results.append(row);print(json.dumps(row),flush=True)
    (Path(__file__).resolve().parents[2]/'docs/LIVE_FUNCTIONAL_REVIEW.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
if __name__=='__main__':asyncio.run(main())
