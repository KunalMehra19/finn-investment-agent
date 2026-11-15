from fastapi.testclient import TestClient
from backend.app.main import app
import json

with TestClient(app) as client:
    for ticker in ['HCLTECH','ASIANPAINT','AXISBANK','NOTAREALSTOCKZZ']:
        r=client.get('/api/company/'+ticker)
        body=r.json();print(ticker,r.status_code,body.get('company',{}).get('name'),body.get('price',{}).get('as_of') if body.get('price') else None,body.get('status'))
    a=client.post('/api/research',json={'ticker':'TCS','question':'What changed in margins?'}).json()
    print('Research',a['status'],len(a['insights']),a['engine'])
