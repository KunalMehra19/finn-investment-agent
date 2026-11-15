import json
from datetime import datetime
from zoneinfo import ZoneInfo
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.market import summarize
from backend.app.research import Claim,validate_claim,deterministic,dataset,retrieve_pages

client=TestClient(app)

def test_volume_excludes_latest_and_intraday():
    rows=[{'date':f'2026-10-{n:02}','close':100,'volume':100} for n in range(1,22)]
    rows[-1].update(close=110,volume=500)
    rows.append({'date':'2026-10-22','close':500,'volume':1000})
    p=summarize(rows,datetime(2026,10,22,12,tzinfo=ZoneInfo('Asia/Kolkata')))
    assert p['move']==10 and p['relative_volume']==5 and p['as_of']=='2026-10-21'

def test_citation_rejects_nonexistent_page_and_quote():
    pages=[{'source_id':'source','page':2,'text':'Revenue was 100 crore.'}]
    claim=Claim(title='Revenue',text='Revenue was 100 crore.',source_id='source',page=2,supporting_excerpt='Revenue was 100 crore.')
    assert validate_claim(claim,pages,{'source'})
    assert not validate_claim(claim.model_copy(update={'page':3}),pages,{'source'})
    assert not validate_claim(claim.model_copy(update={'supporting_excerpt':'Revenue was 500 crore.'}),pages,{'source'})
    assert not validate_claim(claim.model_copy(update={'text':'Revenue was 200 crore.'}),pages,{'source'})

def test_current_does_not_leak_replay():
    assert client.get('/api/briefing?mode=current&window=24h').json()['stories']==[]
    assert len(client.get('/api/briefing?mode=replay').json()['stories'])==5

def test_fifteen_companies_and_five_deep():
    d=dataset();assert len(d['companies'])==15
    assert sum(c['deep'] for c in d['companies'])==5
    assert all(any(s['ticker']==c['ticker'] for s in d['sources']) for c in d['companies'] if c['deep'])

def test_guidance_quotes_and_python_calculations():
    d=dataset();assert len(d['ledger'])==3
    for row in d['ledger']:
        source=next(s for s in d['sources'] if s['id']==row['promise_source'])
        assert row['promise_page']<=source['pages']
        assert source['url'].startswith('https://')
        assert any(s['id']==row['actual_source'] for s in d['sources'])
    assert d['ledger'][0]['delta']==70
    assert d['ledger'][1]['delta']==-180
    assert d['ledger'][2]['status']=='Unclear'

def test_invalid_and_missing_sources():
    assert client.get('/api/company/BAD%21SYMBOL').status_code==400
    assert client.get('/api/sources/not-real').status_code==404
    assert client.post('/api/research',json={'ticker':'TCS','question':''}).status_code==422

def test_unknown_question_and_missing_documents_are_explicit():
    assert deterministic(dataset(),'TCS','Who will win the cricket match?')['status']=='partial'
    a=deterministic(dataset(),'ASIANPAINT','What drives revenue?')
    assert a['status']=='partial' and not a['insights']

def test_research_keyless_path_and_fts():
    response=client.post('/api/research',json={'ticker':'TCS','question':'What changed in margins?'})
    assert response.status_code==200
    a=response.json();assert len(a['insights'])>0
    assert all(any(s['id']==i['source_id'] for s in dataset()['sources']) for i in a['insights'])
    assert retrieve_pages('TCS','operating margin')

def test_title_numbers_are_checked():
    pages=[{'source_id':'source','page':1,'text':'Revenue was 100 crore.'}]
    claim=Claim(title='Revenue of 999 crore',text='Revenue was 100 crore.',source_id='source',page=1,supporting_excerpt='Revenue was 100 crore.')
    assert not validate_claim(claim,pages,{'source'})

def test_untrusted_pdf_urls_are_rejected():
    from backend.app.discovery import safe_url
    assert safe_url('https://nsearchives.nseindia.in/corporate/report.pdf')
    for url in ['http://nsearchives.nseindia.in/a.pdf','https://nsearchives.nseindia.in.evil.test/a.pdf','https://127.0.0.1/a.pdf','https://user:password@nsearchives.nseindia.in/a.pdf','https://nsearchives.nseindia.in:8080/a.pdf']:
        assert not safe_url(url)

def test_provider_error_keeps_evidence(monkeypatch):
    import asyncio,httpx
    from backend.app.research import answer_question
    class FailedClient:
        def __init__(self,**kwargs):pass
        async def __aenter__(self):return self
        async def __aexit__(self,*args):pass
        async def post(self,*args,**kwargs):raise httpx.ConnectTimeout('Test timeout')
    monkeypatch.setenv('GEMINI_API_KEY','invalid-test-key')
    monkeypatch.setattr(httpx,'AsyncClient',FailedClient)
    result=asyncio.run(answer_question('TCS','Explain operating margins in these documents, test provider failure'))
    assert result['insights'] and 'Indexed evidence' in result['engine']
    assert any('temporarily unavailable' in u for u in result['unknowns'])

def test_quota_uses_one_bounded_lite_fallback(monkeypatch):
    import asyncio,httpx
    from backend.app.research import answer_question
    calls=[]
    class QuotaClient:
        def __init__(self,**kwargs):pass
        async def __aenter__(self):return self
        async def __aexit__(self,*args):pass
        async def post(self,url,**kwargs):
            calls.append(url)
            if len(calls)==1:return httpx.Response(429,request=httpx.Request('POST',url))
            body={'claims':[{'title':'Margin outlook','text':'Management expects improvement.','source_id':'tcs-fy25-call','page':20,'supporting_excerpt':'yes, we should be able to improve margins.'}],'unknowns':[]}
            return httpx.Response(200,request=httpx.Request('POST',url),json={'candidates':[{'finishReason':'STOP','content':{'parts':[{'text':json.dumps(body)}]}}]})
    monkeypatch.setenv('GEMINI_API_KEY','invalid-test-key');monkeypatch.setenv('GEMINI_MODEL','gemini-2.5-flash');monkeypatch.setattr(httpx,'AsyncClient',QuotaClient)
    a=asyncio.run(answer_question('TCS','What changed in margins?'))
    assert 'Gemini' in a['engine'] and len(calls)==2 and 'flash-lite' in calls[-1]
