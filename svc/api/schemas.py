from pydantic import BaseModel, Field
from typing import List
from datetime import date

class ForecastReq(BaseModel):
    model: str = "lr"
    days: int = 30

class ScenarioReq(BaseModel):
    basis_change: float = Field(default=0.0, description="Basis point change to apply to the forecast.")
    volatility_scale: float = Field(default=1.0, description="Volatility scaling factor.")
    demand_shock: float = Field(default=0.0, description="Demand shock to apply to the forecast.")

class ForecastResp(BaseModel):
    dates: List[str]
    p10: List[float]
    p50: List[float]
    p90: List[float]
    current_price: float

class PredictionRequest(BaseModel):
    dates: List[date]

class PredictionResponse(BaseModel):
    predictions: List[float]
