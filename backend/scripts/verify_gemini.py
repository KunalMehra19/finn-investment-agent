"""Verify configured credentials without printing secrets or response bodies."""
import json,os,sys
from pathlib import Path
import httpx
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parents[2]/'.env')
key=os.getenv('GEMINI_API_KEY','')
try:
    r=httpx.get('https://generativelanguage.googleapis.com/v1beta/models',headers={'x-goog-api-key':key},timeout=20)
    d=r.json()
    print(json.dumps({'status':r.status_code,'models':[m['name'] for m in d.get('models',[]) if 'generateContent' in m.get('supportedGenerationMethods',[])],'error':{'status':d.get('error',{}).get('status'),'reasons':[x.get('reason') for x in d.get('error',{}).get('details',[]) if x.get('reason')]}}))
except Exception as e:print(json.dumps({'error':type(e).__name__}))
