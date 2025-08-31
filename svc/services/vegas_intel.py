import pandas as pd
from datetime import datetime
from typing import List, Dict, Iterable
from .data_loader import load_restaurants, iter_events_jsonl

PRICE_PER_LB = 0.85
SERVICE_FEE = 75.0
OIL_PER_ATTENDEE = 0.0015
ALLOW = {'concerts','conferences','expos','sports','festivals','performing-arts'}

def _events() -> Iterable[Dict]:
    for ev in iter_events_jsonl():
        cat = ev.get('category')
        if cat not in ALLOW: continue
        start_iso = ev.get('start') or ev.get('start_time')
        if not start_iso: continue
        try:
            dt = datetime.fromisoformat(start_iso.replace('Z','+00:00'))
        except Exception:
            continue
        att = ev.get('phq_attendance') or 0
        name = ev.get('title') or ev.get('name') or 'Event'
        venue = (ev.get('entities') or [{}])[0].get('name') if ev.get('entities') else ev.get('location',{}).get('name','Vegas')
        yield {"name":name,"date":dt.date(),"attendance":att,"venue":venue,"category":cat}

def generate_opportunities(limit:int=50) -> List[Dict]:
    rests = load_restaurants()
    outs: List[Dict] = []
    today = pd.Timestamp.today().normalize()
    for ev in _events():
        if not ev["attendance"] or ev["attendance"]<=0: continue
        days_until = (pd.Timestamp(ev["date"]) - today).days
        for _, rr in rests.iterrows():
            if not bool(rr.get('is_active', True)): continue
            fryers = int(rr.get('fryers',0))
            cuisine_mult = 1.2 if fryers >= 8 else 1.0
            base = ev["attendance"] * OIL_PER_ATTENDEE * cuisine_mult
            dist = 0.9 if rr.get('casino_name') and str(rr['casino_name']) in str(ev['venue']) else 0.7
            predicted = base * dist
            if predicted < 50: continue
            revenue = predicted * PRICE_PER_LB + SERVICE_FEE - 15
            revenue_score = min(40, revenue/10.0)
            volume_score = min(30, predicted/50.0)
            timing_score = 20 * (1 - max(0, min(60, abs(days_until)))/60.0)
            relationship_score = 8.0
            score = revenue_score + volume_score + timing_score + relationship_score
            outs.append({
                "event_name": ev["name"],
                "event_date": str(ev["date"]),
                "restaurant_name": rr["restaurant_name"],
                "predicted_lbs": round(predicted,2),
                "revenue": round(revenue,2),
                "score": round(score,2),
                "strategy": "IMMEDIATE" if score>80 else "SCHEDULE" if score>60 else "NURTURE"
            })
    outs = sorted(outs, key=lambda x: x["score"], reverse=True)
    return outs[:limit]
