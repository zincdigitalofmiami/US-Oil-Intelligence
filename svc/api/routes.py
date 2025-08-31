from fastapi import APIRouter
from .schemas import ForecastReq, ScenarioReq, ForecastResp
from ..services.forecasting import Forecaster
from ..services.data_loader import load_market_daily
from ..services.vegas_intel import generate_opportunities

router = APIRouter()
_f = Forecaster()

@router.get("/market-data")
def market_data(limit:int=100):
    df = load_market_daily().sort_values('date', ascending=False).head(limit)
    return df.to_dict(orient='records')

@router.post("/forecast", response_model=ForecastResp)
def forecast(req: ForecastReq):
    _f.fit()
    res = _f.forecast_mc(days=req.days) if req.model=="mc" else _f.forecast_lr(days=req.days)
    return ForecastResp(
        dates=[d.date().isoformat() for d in res.dates],
        p10=res.p10, p50=res.p50, p90=res.p90, current_price=res.current_price
    )

@router.post("/scenario")
def scenario(req: ScenarioReq):
    _f.fit(); res = _f.forecast_lr(days=30)
    adj = _f.apply_scenario(res, req.basis_change, req.volatility_scale, req.demand_shock)
    impact = ((adj['p50'][0] - res.p50[0]) / res.p50[0] * 100.0) if res.p50 else 0.0
    return {"impact_pct": impact, "adjusted_price": adj['p50'][0], "adjusted_forecast": adj}

@router.get("/opportunities")
def opportunities():
    return generate_opportunities(limit=50)

@router.get("/health")
def health(): return {"ok": True}
