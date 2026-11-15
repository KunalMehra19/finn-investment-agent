import json, math, threading
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from pathlib import Path
import yfinance as yf

DATA=Path(__file__).resolve().parents[1]/'data'
LOCK=threading.Lock()

def summarize(rows, now=None):
    now=now or datetime.now(ZoneInfo('Asia/Kolkata'))
    cutoff=now.date() if (now.hour,now.minute)>=(16,0) else now.date()-timedelta(days=1)
    rows=[r for r in rows if r['date']<=cutoff.isoformat() and r['close']>0 and r['volume']>=0 and math.isfinite(r['close'])]
    rows.sort(key=lambda r:r['date'])
    if len(rows)<2: return None
    last,prev=rows[-1],rows[-2]
    baseline=rows[-21:-1]
    mean=sum(r['volume'] for r in baseline)/len(baseline) if len(baseline)==20 else 0
    return {'close':round(last['close'],2),'move':round((last['close']/prev['close']-1)*100,2),'volume':last['volume'],'relative_volume':round(last['volume']/mean,2) if mean else None,'as_of':last['date'],'provider':'Yahoo Finance via yfinance','basis':'Unadjusted close; corporate actions may affect daily moves','history':rows[-30:]}

def load_market():
    path=DATA/'market.json'
    if path.exists():data=json.loads(path.read_text(encoding='utf-8'))
    elif (DATA/'demo.json').exists():data=json.loads((DATA/'demo.json').read_text(encoding='utf-8'))['market']
    else:return {'prices':{},'status':'unavailable','error':'Market data has not been retrieved.'}
    if not data.get('fetched_at'):return data
    age=datetime.now(ZoneInfo('UTC'))-datetime.fromisoformat(data['fetched_at'])
    if age.total_seconds()>43200:
        data['status']='stale'
    for row in data.get('prices',{}).values():
        if row['as_of']<datetime.now(ZoneInfo('Asia/Kolkata')).date().isoformat():
            row['session_label']='Latest retrieved completed session'
    return data

def refresh_market(tickers):
    if not LOCK.acquire(blocking=False): return load_market()
    try:
        prior=load_market(); prices=dict(prior.get('prices',{})); failures=[]
        frame=yf.download([f'{t}.NS' for t in tickers],period='3mo',interval='1d',auto_adjust=False,group_by='ticker',threads=True,timeout=12,progress=False)
        for ticker in tickers:
            try:
                f=frame[f'{ticker}.NS'] if frame.columns.nlevels>1 else frame
                rows=[{'date':str(idx.date()),'close':float(r['Close']),'volume':int(r['Volume'])} for idx,r in f.dropna(subset=['Close','Volume']).iterrows()]
                value=summarize(rows)
                if value: prices[ticker]=value
                else: failures.append(ticker)
            except Exception: failures.append(ticker)
        if prices:
            data={'prices':prices,'status':'partial' if failures else 'verified','fetched_at':datetime.now(ZoneInfo('UTC')).isoformat(),'failed_tickers':failures}
            path=DATA/'market.json';temp=path.with_suffix('.tmp');temp.write_text(json.dumps(data,allow_nan=False),encoding='utf-8');temp.replace(path)
            return data
        return {**prior,'error':'Yahoo Finance did not return usable completed-session data.'}
    except Exception:
        return {**load_market(),'error':'Market refresh unavailable; retaining the last successful snapshot.'}
    finally: LOCK.release()
