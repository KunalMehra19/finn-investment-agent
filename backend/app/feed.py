import json,os
from pathlib import Path
from datetime import datetime,timezone
DATA=Path(__file__).resolve().parents[1]/'data'
def overlay(data):
    try:
        feed=json.loads(Path(os.getenv('FINN_FEED_FILE',str(DATA/'live_feed.json'))).read_text(encoding='utf-8'))
        if feed.get('schema_version')!=1:raise ValueError()
        age=(datetime.now(timezone.utc)-datetime.fromisoformat(feed['feed_status']['last_success_at'])).total_seconds()
        state='stale' if age>7200 or feed['feed_status']['state']=='stale' else 'fresh'
        return {**data,'current_stories':feed['current_stories'],'sources':list({s['id']:s for s in data['sources']+feed['sources']}.values()),'filing_coverage':feed['filing_coverage'],'feed_status':{**feed['feed_status'],'state':state}}
    except (OSError,ValueError,KeyError,TypeError):return {**data,'feed_status':{'state':'baseline','message':'Automatic feed unavailable; showing bundled verified snapshot.','last_success_at':data.get('filing_coverage',{}).get('checked_at')}}
