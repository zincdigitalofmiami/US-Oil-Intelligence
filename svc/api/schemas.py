from pydantic import BaseModel
from typing import List

class ForecastReq(BaseModel):
    model: str = "lr"
    days: int = 30

class ScenarioReq(BaseModel):
    basis_change: float = 0.0
    volatility_scale: float = 1.0
    demand_shock: float = 0.0

class ForecastResp(BaseModel):
    dates: List[str]
    p10: List[float]
    p50: List[float]
    p90: List[float]
    current_price: float
