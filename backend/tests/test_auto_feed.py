from backend.scripts.auto_feed import compose
from backend.app.research import dataset

def test_producer_deduplicates_and_excludes_unverified_sources():
    d=dataset();s=d['current_stories'][0];current={'stories':[s,s],'coverage':d['filing_coverage']}
    a=compose(current,d['sources'],{'status':'checked','checked_at':d['filing_coverage']['checked_at']})
    assert len(a['current_stories'])==1
    b=compose(current,[],{'status':'checked'})
    assert b['current_stories']==[]

def test_producer_outage_marks_retained_stories_stale():
    d=dataset();current={'stories':d['current_stories'],'coverage':d['filing_coverage']}
    a=compose(current,d['sources'],{'status':'unavailable','checked_at':'2026-11-16T00:00:00+05:30'})
    assert a['feed_status']['state']=='stale'
    assert len(a['current_stories'])==len(d['current_stories'])
    assert a['feed_status']['last_success_at']==d['filing_coverage']['checked_at']

def test_local_api_receives_new_feed_and_resolves_source(monkeypatch,tmp_path):
    import json
    from datetime import datetime,timezone
    from fastapi.testclient import TestClient
    from backend.app.main import app
    from backend.app import feed
    d=dataset();story={**d['current_stories'][0],'id':'review-added-story','published':datetime.now(timezone.utc).isoformat()}
    value=compose({'stories':[story],'coverage':{**d['filing_coverage'],'checked_at':story['published']}},d['sources'],{'status':'checked','checked_at':story['published']})
    (tmp_path/'live_feed.json').write_text(json.dumps(value),encoding='utf-8');monkeypatch.setattr(feed,'DATA',tmp_path)
    client=TestClient(app)
    assert client.get('/api/snapshot').json()['current_stories'][0]['id']=='review-added-story'
    assert client.get('/api/briefing?mode=current&window=24h').json()['stories'][0]['id']=='review-added-story'
    assert client.get('/api/sources/'+story['source_id']).status_code==200
    assert client.get('/api/briefing?mode=replay').json()['stories']==d['stories']
