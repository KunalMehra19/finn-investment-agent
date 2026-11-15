import pytest
import json,sqlite3
from pathlib import Path

@pytest.fixture(autouse=True)
def offline_by_default(monkeypatch,tmp_path):
    monkeypatch.setenv('GEMINI_API_KEY','')
    from backend.app import research
    original=Path(__file__).resolve().parents[1]/'data/demo.json'
    data=json.loads(original.read_text(encoding='utf-8'))
    (tmp_path/'demo.json').write_text(json.dumps(data),encoding='utf-8')
    with sqlite3.connect(tmp_path/'finn.sqlite') as db:
        db.execute('CREATE VIRTUAL TABLE pages USING fts5(source_id UNINDEXED,ticker UNINDEXED,page UNINDEXED,text)')
        db.executemany('INSERT INTO pages VALUES(?,?,?,?)',[(s['id'],s['ticker'],s['page'],s['excerpt']) for s in data['sources'] if s['excerpt']])
    monkeypatch.setattr(research,'DATA',tmp_path)
