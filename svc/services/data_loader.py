import os, json, pandas as pd
from ..core.config import settings

def _read_ohlc_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    if 'time' not in df.columns or 'close' not in df.columns:
        raise ValueError("Expected columns: time, close")
    t = df['time']
    if pd.api.types.is_numeric_dtype(t):
        dt = pd.to_datetime(t, unit='s', utc=True).dt.tz_localize(None)
    else:
        dt = pd.to_datetime(t, utc=True, errors='coerce').dt.tz_localize(None)
    df['date'] = dt.dt.date
    out = df.groupby('date', as_index=False)['close'].last().rename(columns={'close':'price'})
    return out.dropna().sort_values('date')

def load_market_daily() -> pd.DataFrame:
    base = settings.data_dir
    for fn in ["zl_1d.csv","zl_60.csv","zl_240.csv","zl_1w.csv","zl_1m.csv"]:
        p = os.path.join(base, fn)
        if os.path.exists(p):
            return _read_ohlc_csv(p)
    raise FileNotFoundError("Place your ZL CSV as data/zl_1d.csv (or zl_60.csv, zl_240.csv, zl_1w.csv, zl_1m.csv)")

def load_restaurants() -> pd.DataFrame:
    p = os.path.join(settings.data_dir, "restaurants.csv")
    if not os.path.exists(p):
        return pd.DataFrame(columns=['restaurant_name','casino_name','fryers','is_active'])
    df = pd.read_csv(p)
    df['restaurant_name'] = df.get('Name', df.get('restaurant_name','Unknown'))
    df['casino_name'] = df.get('Casino/Name', df.get('casino_name', None))
    df['fryers'] = pd.to_numeric(df.get('Fryers/Count', df.get('fryers', 0)), errors='coerce').fillna(0).astype(int)
    df['is_active'] = df.get('Active', True)
    return df[['restaurant_name','casino_name','fryers','is_active']]

def iter_events_jsonl():
    p = os.path.join(settings.data_dir, "events.jsonl")
    if not os.path.exists(p): return []
    out = []
    with open(p,'r',encoding='utf-8') as f:
        for line in f:
            try: out.append(json.loads(line))
            except: pass
    return out
