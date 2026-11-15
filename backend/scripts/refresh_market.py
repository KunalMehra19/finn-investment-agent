import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from backend.app.market import refresh_market, DATA
if __name__=='__main__':
    data=refresh_market([c['ticker'] for c in json.loads((DATA/'companies.json').read_text())])
    print(json.dumps({k:v for k,v in data.items() if k!='prices'}))
    print('Available:',len(data.get('prices',{})))
