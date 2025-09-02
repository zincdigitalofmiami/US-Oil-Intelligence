
from fastapi import APIRouter, Depends, HTTPException
from .schemas import ForecastReq, ForecastResp, ScenarioReq # Import the new schemas
from svc.services.forecasting import Forecaster
from typing import Dict
from fastapi.responses import JSONResponse


# Assuming a single, shared Forecaster instance is managed in the application's state
# This is a common practice for resource-intensive objects.
from fastapi import Request

def get_forecaster(request: Request) -> Forecaster:
    return request.app.state.forecaster

router = APIRouter()

@router.post("/forecast", response_model=ForecastResp)
def get_forecast(req: ForecastReq, forecaster: Forecaster = Depends(get_forecaster)):
    """The main endpoint to get a forecast."""
    # We'll use the MC forecaster for now
    res = forecaster.forecast_mc(days=req.days)
    
    # Convert timestamps to ISO 8601 strings
    dates_iso = [d.isoformat() for d in res.dates]
    
    return ForecastResp(
        dates=dates_iso,
        p10=res.p10,
        p50=res.p50,
        p90=res.p90,
        current_price=res.current_price
    )

@router.post("/scenario")
def apply_scenario(req: ScenarioReq, forecaster: Forecaster = Depends(get_forecaster)) -> Dict[str, list]:
    """
    Applies a scenario to the latest forecast.
    This is a simplified example. A real implementation would be more robust.
    """
    # Get the latest forecast (or a default one)
    res = forecaster.forecast_mc(days=30) 
    
    # Apply the scenario
    adjusted_forecast = forecaster.apply_scenario(
        res, 
        basis=req.basis_change, 
        vol_scale=req.volatility_scale, 
        demand=req.demand_shock
    )
    return adjusted_forecast

# A simple health check endpoint
@router.get("/health")
def health_check():
    return JSONResponse(content={"status": "ok"})
