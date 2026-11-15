import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
d=json.loads((ROOT/'backend/data/demo.json').read_text(encoding='utf-8'))
lines=['# Verified source manifest','','All entries were fetched as genuine PDFs from the URL shown. Page numbers in FINN refer to PDF file pages, including exchange cover letters. No PDF bundles are committed.','','Snapshot retrieved: '+d['coverage']['as_of'],'','## Market and exchange coverage','','- Market: Yahoo Finance via yfinance, unadjusted close, completed EOD session '+max(p['as_of'] for p in d['market']['prices'].values())+'.','- Relative volume: latest completed session / mean of the preceding 20 completed sessions.','- NSE coverage: '+d['coverage']['filings'],'- Metadata records: '+str(d.get('filing_coverage',{}).get('metadata_count','unavailable'))+'; verified current attachments: '+str(d.get('filing_coverage',{}).get('verified_count','unavailable'))+'.','','## Original documents','']
for s in d['sources']:
    lines += ['### '+s['ticker']+' · '+s['title'],'','- Source ID: `'+s['id']+'`','- Period: '+s['period'],'- Published: '+str(s['published'] or 'Date unconfirmed; not inferred'),'- Original: ['+s['title']+']('+s['url']+')','- PDF pages: '+str(s['pages'])+'; verified: '+s['retrieved_at'],'- SHA-256: `'+s['sha256']+'`','']
lines+=['## Guidance records','']
for r in d['ledger']:
    lines += ['- '+r['ticker']+' · '+r['metric']+': promise `'+r['promise_source']+'`, PDF p. '+str(r['promise_page'])+'; actual `'+r['actual_source']+'`, PDF p. '+str(r['actual_page'])+'. '+r['calculation']+'. Status: '+r['status']+'.']
(ROOT/'docs/SOURCE_MANIFEST.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('Wrote source manifest for',len(d['sources']),'verified PDFs.')
