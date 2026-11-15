"""Reproducible editorial snapshot. Every number is tied to an original PDF page."""
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; DATA=ROOT/'backend/data'
def read(name):return json.loads((DATA/name).read_text(encoding='utf-8'))

def build():
    library=read('library.json'); byid={d['id']:d for d in library}
    sources=[]
    excerpts={
      'ril-fy25':(2,'RECORD ANNUAL CONSOLIDATED REVENUE AT ₹ 1,071,174 CRORE'),
      'tcs-fy25-call':(20,'yes, we should be able to improve margins.'),
      'tcs-fy26-call':(8,'The operating margin for the year excludes a few one-off items recognised during this year.'),
      'hdfc-fy25':(1,'Net interest margin was at 3.54% on total assets'),
      'airtel-fy25':(1,'Mobile ARPU increased to Rs 245 in Q4’25 vs Rs 209 in Q4’24'),
      'sun-fy25':(2,'consolidated R&D investment were Rs. 32,484 million for FY25 or 6.2% of sales.'),
      'sun-fy24-call':(5,"we expect high single-digit consolidated top line growth for FY'25."),
      'sun-q1-call':(8,'Yes, I think you should presume a step up in the subsequent quarters.'),
      'sun-fy25-call':(5,"We now expect our FY'26 R&D spend to be 6% to 8% of sales for the next year."),
      'hdfc-ar25':(5,''),
    }
    normalize=lambda s:re.sub(r'\s+',' ',s).casefold()
    for doc in library:
        page,quote=excerpts.get(doc['id'],(1,''))
        text=doc['content'][page-1]['text']
        if quote and normalize(quote) not in normalize(text):
            # Apostrophes, bullet separators and PDF spacing vary: never label unmatched excerpts verified.
            quote=''
        sources.append({**{k:v for k,v in doc.items() if k!='content'},'page':page,'excerpt':quote})
    facts={
    'RELIANCE':[
      {'label':'Gross revenue','value':'₹10,71,174 cr','period':'FY25 · Consolidated','source_id':'ril-fy25','page':2},
      {'label':'EBITDA','value':'₹1,83,422 cr','period':'FY25 · Consolidated','source_id':'ril-fy25','page':2},
      {'label':'Profit after tax','value':'₹81,309 cr','period':'FY25 · Including associates','source_id':'ril-fy25','page':2}],
    'TCS':[
      {'label':'Adj. operating margin','value':'25.0%','period':'FY26 · Excludes one-off items','source_id':'tcs-fy26-call','page':8},
      {'label':'Revenue growth','value':'−2.4%','period':'FY26 · Constant currency YoY','source_id':'tcs-fy26-call','page':5},
      {'label':'Order book','value':'$40.7 bn','period':'FY26 · Total contract value','source_id':'tcs-fy26-call','page':5}],
    'HDFCBANK':[
      {'label':'Net interest margin','value':'3.54%','period':'Q4 FY25 · Total assets','source_id':'hdfc-fy25','page':1},
      {'label':'Net interest income','value':'₹32,070 cr','period':'Q4 FY25 · Standalone','source_id':'hdfc-fy25','page':1},
      {'label':'NII growth','value':'+10.3%','period':'Q4 FY25 · YoY','source_id':'hdfc-fy25','page':1}],
    'BHARTIARTL':[
      {'label':'Mobile ARPU','value':'₹245','period':'Q4 FY25 · India mobile','source_id':'airtel-fy25','page':1},
      {'label':'Revenue','value':'₹47,876 cr','period':'Q4 FY25 · Consolidated','source_id':'airtel-fy25','page':1},
      {'label':'EBITDA margin','value':'57.2%','period':'Q4 FY25 · Consolidated','source_id':'airtel-fy25','page':1}],
    'SUNPHARMA':[
      {'label':'Gross sales','value':'₹52,041 cr','period':'FY25 · Consolidated','source_id':'sun-fy25','page':1},
      {'label':'EBITDA margin','value':'29.0%','period':'FY25 · Including operating revenue','source_id':'sun-fy25','page':1},
      {'label':'R&D / sales','value':'6.2%','period':'FY25 · Reported ratio','source_id':'sun-fy25','page':2}]
    }
    insights={
    'RELIANCE':[
      {'title':'Growth across a large base','text':'FY25 gross revenue reached ₹10,71,174 crore, up 7.1% year on year. This is gross revenue, not net revenue from operations.','source_id':'ril-fy25','page':2,'tags':'business revenue growth'},
      {'title':'Earnings grew more slowly than revenue','text':'Consolidated EBITDA rose 2.9% to ₹1,83,422 crore; profit after tax including associates rose 2.9% to ₹81,309 crore. The differing growth rates merit a closer look at segment mix.','source_id':'ril-fy25','page':2,'tags':'margin profit economics EBITDA'},
      {'title':'Jio and retail add a second lens','text':'FY25 Jio Platforms PAT was ₹26,109 crore, up 21.9%; Reliance Retail PAT was ₹12,392 crore, up 11.6%. These segment outcomes should be distinguished from group-level growth.','source_id':'ril-fy25','page':2,'tags':'business segments jio retail telecom'}],
    'TCS':[
      {'title':'Margins improved despite weaker demand','text':'FY26 adjusted operating margin reached 25.0%, compared with 24.3% in FY25: +70 basis points. FY26 excludes severance, legal provisions and India wage-code effects; the issuer reports the expansion on this basis.','source_id':'tcs-fy26-call','page':8,'tags':'margin guidance outcome profitability','calculation':'(25.0 − 24.3) × 100 = +70 bps','related_source':'tcs-fy25-call'},
      {'title':'Bookings and revenue tell different stories','text':'FY26 constant-currency revenue declined 2.4%, while total contract value was $40.7 billion including five mega deals. Bookings are not recognized revenue.','source_id':'tcs-fy26-call','page':5,'tags':'business demand revenue growth deals'},
      {'title':'A directional commitment with a measurable result','text':'In April 2025, CFO Samir Seksaria said margins should improve. The annual reported operating margin subsequently rose. This does not establish that the wider 26% aspiration was achieved.','source_id':'tcs-fy25-call','page':20,'tags':'guidance promise management expect outcome'}],
    'HDFCBANK':[
      {'title':'Read the bank through NII and NIM','text':'Q4 FY25 standalone net interest income rose 10.3% to ₹32,070 crore. Net interest margin was 3.54% on total assets and 3.73% on interest-earning assets; these denominators are different.','source_id':'hdfc-fy25','page':1,'tags':'business margin NIM NII growth'},
      {'title':'Consolidated and standalone are separate views','text':'Q4 FY25 consolidated profit after tax was ₹18,830 crore, using the press release’s rounded ₹188.3 billion figure. This should not be compared directly with standalone profit.','source_id':'hdfc-fy25','page':1,'tags':'profit results performance consolidated'},
      {'title':'Watch the comparison base','text':'The prior-year quarter included gains from the sale of HDFC Credila. Reported net revenue comparisons therefore need the context of that one-off transaction.','source_id':'hdfc-fy25','page':1,'tags':'growth changes risk comparison'}],
    'BHARTIARTL':[
      {'title':'Realization improved in India mobile','text':'Q4 FY25 mobile ARPU rose to ₹245 from ₹209 a year earlier. The release attributes India mobile revenue growth to tariff repair, smartphone additions and premiumization.','source_id':'airtel-fy25','page':1,'tags':'business ARPU revenue growth'},
      {'title':'Consolidation matters to the growth rate','text':'Consolidated quarterly revenue rose 27.3% to ₹47,876 crore. The company explicitly identifies the full-quarter impact of Indus Towers consolidation among the drivers.','source_id':'airtel-fy25','page':1,'tags':'revenue changes consolidation'},
      {'title':'Keep EBITDA and EBITDAaL distinct','text':'Q4 FY25 consolidated EBITDA margin was 57.2%, while EBITDA after leases margin was 50.9%. Use matching definitions when comparing performance.','source_id':'airtel-fy25','page':1,'tags':'margin EBITDA profitability'}],
    'SUNPHARMA':[
      {'title':'Growth was led by specialty and India','text':'FY25 gross sales rose 9.0% to ₹52,041 crore. Global specialty sales rose 17.1% to $1,216 million, while India formulation sales grew 13.7%.','source_id':'sun-fy25','page':1,'tags':'business revenue sales growth specialty'},
      {'title':'Research spending came below the original range','text':'FY25 reported R&D investment was 6.2% of sales, below the earlier 8–10% spending range. Spending below plan is a variance, not a verdict on clinical execution.','source_id':'sun-fy25','page':2,'tags':'R&D research guidance outcome promise management','related_source':'sun-fy24-call'},
      {'title':'Reported profit needs exceptional-item context','text':'FY25 adjusted net profit rose 19.0%, while reported net profit was ₹10,929 crore. The quarterly release separates adjusted and reported profit, so those growth rates should not be interchanged.','source_id':'sun-fy25','page':1,'tags':'profit margin risk adjusted results'}]
    }
    story_specs=[
      ('ril-fy25','RELIANCE','A record year. A closer look at the mix.','Reliance crosses ₹10.7 lakh crore in annual gross revenue','FY25 gross revenue grew 7.1%, while consolidated EBITDA grew 2.9%.','The gap between sales and earnings growth puts segment economics in focus.',2),
      ('tcs-fy26-call','TCS','Margins held. Demand told another story.','TCS lifts adjusted annual operating margin to 25%','FY26 constant-currency revenue declined 2.4%; the order book reached $40.7 billion.','A useful test of management’s prior commitment to improve profitability.',5),
      ('airtel-fy25','BHARTIARTL','Better realizations. A wider footprint.','Airtel’s mobile ARPU reaches ₹245','Q4 FY25 revenue rose 27.3%, including the impact of Indus Towers consolidation.','Separate organic operating momentum from the change in the reporting perimeter.',1),
      ('sun-fy25','SUNPHARMA','The specialty story meets the numbers.','Sun Pharma posts 9% full-year sales growth','Global specialty sales grew 17.1%; annual R&D spending was 6.2% of sales.','Compare the outcome with management’s original growth and R&D guidance.',1),
      ('hdfc-fy25','HDFCBANK','Look beneath the headline growth.','HDFC Bank’s net interest income grows 10.3%','Q4 FY25 NIM was 3.54% on total assets, with NII of ₹32,070 crore.','Bank economics need the right denominator and a clean comparison base.',1)
    ]
    stories=[{'id':sid,'ticker':t,'display_title':hero,'title':title,'summary':summary,'why':why,'source_id':sid,'page':page,'published':byid[sid]['published'],'timestamp_precision':'date','category':'Results','priority':100-i,'origin':'Issuer publication','routine':False} for i,(sid,t,hero,title,summary,why,page) in enumerate(story_specs)]
    ledger=[
      {'id':'tcs-margin','ticker':'TCS','metric':'Adjusted operating margin','period':'FY26 vs FY25','status':'Met','promise':'yes, we should be able to improve margins.','speaker':'Samir Seksaria · CFO','date':'2025-04-10','target':'Improve year on year','actual':'25.0%','previous':'24.3%','delta':round((25-24.3)*100),'delta_label':'+70 bps YoY','explanation':'On the issuer’s stated basis, annual operating margin rose from 24.3% to 25.0%. FY26 excludes severance, legal provisions and India wage-code effects. Met applies to directional improvement on that basis; it does not imply the 26% aspiration was achieved.','promise_source':'tcs-fy25-call','promise_page':20,'actual_source':'tcs-fy26-call','actual_page':8,'calculation':'(25.0% − 24.3%) × 100 = +70 basis points'},
      {'id':'sun-rd','ticker':'SUNPHARMA','metric':'R&D investment / sales','period':'FY25','status':'Missed','promise':'R&D investments will be 8% to 10% of sales for the next year.','speaker':'Dilip Shanghvi · Managing Director','date':'2024-05-22','target':'8–10% of sales','actual':'6.2%','previous':'8% lower bound','delta':round((6.2-8)*100),'delta_label':'−180 bps vs lower bound','explanation':'Reported R&D / sales of 6.2% was below the original 8–10% range. This is a spending variance, not a judgment on product development. The reported ratio uses the issuer’s sales basis; do not substitute gross sales.','promise_source':'sun-fy24-call','promise_page':5,'actual_source':'sun-fy25','actual_page':2,'calculation':'(6.2% − 8.0%) × 100 = −180 basis points'},
      {'id':'sun-growth','ticker':'SUNPHARMA','metric':'Consolidated top-line growth','period':'FY25','status':'Unclear','promise':"we expect high single-digit consolidated top line growth for FY'25.",'speaker':'Dilip Shanghvi · Managing Director','date':'2024-05-22','target':'High single-digit growth','actual':f"{(520412.5/477584.5-1)*100:.2f}%",'previous':'₹4,77,584.5 mn FY24','delta':None,'delta_label':'Qualitative target','explanation':'Gross sales grew approximately 9%, broadly consistent with the wording. The promise did not specify a numerical range or precise top-line accounting definition, so a binary pass/fail would overstate precision.','promise_source':'sun-fy24-call','promise_page':5,'actual_source':'sun-fy25','actual_page':3,'calculation':'(520,412.5 / 477,584.5 − 1) × 100 = 8.97% gross sales growth'}
    ]
    # Validate every promised quote against the downloaded original page.
    for row in ledger:
        p=byid[row['promise_source']]['content'][row['promise_page']-1]['text']
        assert normalize(row['promise']) in normalize(p),f"Unverified promise: {row['id']}"
    market=read('market.json') if (DATA/'market.json').exists() else {'prices':{},'status':'unavailable'}
    current=read('current_filings.json') if (DATA/'current_filings.json').exists() else {'stories':[],'coverage':{'status':'unavailable'}}
    # Manually checked primary passages for the current evaluator journey.
    for event in current['stories']:
        if event['id']=='nse-9350a9336340':
            event.update(display_title='New orders. A longer runway.',title='L&T wins Noida Metro Aqua Line extension order',summary='L&T secured a 15.1 km elevated metro project with 10 stations, to be completed within 36 months.',why='The issuer classifies the order as “Significant”: ₹1,000–2,500 crore. That is a value band, not a disclosed exact contract price.',page=2)
            facts['LT']=[{'label':'Order value band','value':'₹1,000–2,500 cr','period':'9 Nov 2026 · Issuer classification','source_id':event['id'],'page':2},{'label':'Elevated viaduct','value':'15.1 km','period':'Noida Aqua Line extension','source_id':event['id'],'page':2},{'label':'Execution period','value':'36 months','period':'As disclosed · 9 Nov 2026','source_id':event['id'],'page':2}]
            insights['LT']=[{'title':'An urban transit order with a defined scope','text':'L&T’s Heavy Civil Infrastructure vertical secured part design and construction of a 15.1 km elevated viaduct and 10 stations for the Noida Metro Aqua Line extension.','source_id':event['id'],'page':2,'tags':'business order revenue growth pipeline metro'},{'title':'A range is not an exact contract price','text':'The company categorizes this as a Significant order, defined as ₹1,000–2,500 crore. The exact contract price is not disclosed in this filing. The disclosed completion timeline is 36 months.','source_id':event['id'],'page':2,'tags':'order value guidance expect timeline execution risk'}]
        elif event['id']=='nse-e8e8a6658a44':
            event.update(display_title='A board decision. The conditions attached.',title='HDFC Bank approves V. Srinivasa Rangan’s re-appointment',summary='The board approved a one-year term as Executive Director from 23 November 2026, subject to shareholder approval.',why='RBI approval and board approval are recorded. Shareholder approval remains a stated condition; the process should not be described as complete.')
        elif event['id']=='nse-d49d4485080c':
            event.update(title='RBI approves HDFC Bank Executive Director re-appointment',summary='RBI approved the re-appointment of V. Srinivasa Rangan for one year from 23 November 2026.',why='This is the regulatory approval stage, distinct from the subsequent board decision and shareholder approval.')
        elif event['id']=='nse-1ab61b8444c1':
            event.update(title='Airtel publishes its Q2 FY27 earnings-call transcript',summary='The original 6 November 2026 call discusses results for the quarter and half-year ended 30 September 2026.',why='The filing was published on 12 November; the call itself took place on 6 November. Keep the two dates distinct.')
        elif event['id']=='nse-6604440c2ada':
            event.update(title='Titan publishes its Q2 FY27 earnings-call transcript',summary='The original 5 November 2026 analyst call covers standalone and consolidated results for the quarter and half-year ended September 2026.',why='Management commentary adds context to the reported results. The document’s call date is distinct from the 11 November exchange filing date.')
    # Prefer one source for byte-identical PDFs while preserving every referenced document ID.
    used={s['source_id'] for s in current['stories']}|{s['source_id'] for s in stories}|{r['promise_source'] for r in ledger}|{r['actual_source'] for r in ledger}
    seen_hashes=set();deduped=[]
    for s in sources:
        if s['sha256'] not in seen_hashes or s['id'] in used:
            deduped.append(s);seen_hashes.add(s['sha256'])
    sources=deduped
    result={'companies':read('companies.json'),'sources':sources,'stories':stories,'current_stories':current['stories'],'filing_coverage':current['coverage'],'facts':facts,'insights':insights,'ledger':ledger,'market':market,'coverage':{'filings':current['coverage'].get('message','Historical issuer publications; current exchange coverage not yet checked'),'deep_companies':5,'documents':len(sources),'as_of':max(d['retrieved_at'] for d in library)},'schema_version':1}
    (DATA/'demo.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    (ROOT/'frontend/src/data').mkdir(parents=True,exist_ok=True)
    (ROOT/'frontend/src/data/demo.json').write_text(json.dumps(result,ensure_ascii=False),encoding='utf-8')
    print(f"Curated {len(stories)} stories, {len(sources)} sources, {len(ledger)} verified guidance records, {len(market['prices'])} market snapshots")
if __name__=='__main__':build()
