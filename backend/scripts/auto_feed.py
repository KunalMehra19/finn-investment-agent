"""Scheduled feed producer. Public JSON contains verified metadata, never credentials or PDF text."""
import argparse,json,subprocess,sys,time
from pathlib import Path
from datetime import datetime,timezone

ROOT=Path(__file__).resolve().parents[2];DATA=ROOT/'backend/data'
def atomic(path,value):
    path.parent.mkdir(parents=True,exist_ok=True);temp=path.with_suffix('.tmp');temp.write_text(json.dumps(value,ensure_ascii=False),encoding='utf-8');temp.replace(path)
def compose(current,sources,attempt):
    ids={s['source_id'] for s in current['stories']}
    verified=[s for s in sources if s['id'] in ids and s.get('status')=='verified']
    byid={s['id']:s for s in verified}
    stories={s['id']:s for s in current['stories'] if s['source_id'] in byid}
    failed=attempt.get('status')=='unavailable'
    return {'schema_version':1,'current_stories':sorted(stories.values(),key=lambda s:(s['priority'],s['published']),reverse=True),'sources':verified,'filing_coverage':current['coverage'],'feed_status':{'state':'stale' if failed else 'fresh','last_attempt_at':attempt.get('checked_at'),'last_success_at':current['coverage'].get('checked_at'),'message':'Refresh unavailable; retaining verified filings.' if failed else 'Scheduled NSE feed. Original attachments verified.'}}
def run_once():
    DATA.mkdir(exist_ok=True)
    path=DATA/'live_feed.json'
    if path.exists():
        old=json.loads(path.read_text(encoding='utf-8'))
        atomic(DATA/'current_filings.json',{'stories':old['current_stories'],'coverage':old['filing_coverage']})
        seed=json.loads((DATA/'source_manifest.json').read_text(encoding='utf-8'))
        atomic(DATA/'source_manifest.json',list({s['id']:s for s in seed+old['sources']}.values()))
    try:
        subprocess.run([sys.executable,str(ROOT/'backend/scripts/refresh_filings.py')],cwd=ROOT,timeout=420,check=True)
        attempt=json.loads((DATA/'filing_attempt.json').read_text(encoding='utf-8'))
    except (subprocess.SubprocessError,OSError,ValueError):
        attempt={'status':'unavailable','checked_at':datetime.now(timezone.utc).isoformat()}
    current=json.loads((DATA/'current_filings.json').read_text(encoding='utf-8'))
    sources=json.loads((DATA/'source_manifest.json').read_text(encoding='utf-8'))
    feed=compose(current,sources,attempt);atomic(path,feed)
    print(json.dumps({'state':feed['feed_status']['state'],'stories':len(feed['current_stories']),'last_success':feed['feed_status']['last_success_at']}),flush=True)
    return feed
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--once',action='store_true');p.add_argument('--interval',type=int,default=1800);a=p.parse_args()
    if a.interval<60:raise SystemExit('Minimum interval: 60 seconds')
    while True:
        run_once()
        if a.once:break
        time.sleep(a.interval)
