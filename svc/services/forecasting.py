from __future__ import annotations
import numpy as np, pandas as pd
from dataclasses import dataclass
from typing import List, Dict
from datetime import timedelta
from prophet import Prophet
from .data_loader import load_market_daily
import pickle

@dataclass
class ForecastResult:
    dates: List[pd.Timestamp]
    p10: List[float]; p50: List[float]; p90: List[float]
    current_price: float

class Forecaster:
    def __init__(self, model_path: str = None):
        self.model = None
        self.hist = None
        if model_path:
            try:
                self.load_model(model_path)
            except FileNotFoundError:
                print(f"WARNING: Model file not found at {model_path}. The API will run without a pre-trained model. Please run the training script.")

    def _prep(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepares the input DataFrame for Prophet."""
        df = df.copy()
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        # Prophet requires columns 'ds' and 'y'
        df = df.rename(columns={'date': 'ds', 'price': 'y'})
        return df

    def fit(self):
        """Fits the Prophet model using historical market data."""
        df = load_market_daily()
        dfp = self._prep(df)
        
        # Initialize and fit the Prophet model
        self.model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False,
            interval_width=0.8 # Corresponds to P10 and P90
        )
        self.model.fit(dfp)
        self.hist = dfp
        return self

    def save_model(self, path: str):
        """Saves the trained model and historical data to a file."""
        if self.model is None or self.hist is None:
            raise RuntimeError("Model has not been trained. Please call fit() before saving.")
        with open(path, 'wb') as f:
            # Prophet models can be large, but we'll stick with pickle for now
            pickle.dump({'model': self.model, 'hist': self.hist}, f)

    def load_model(self, path: str):
        """Loads a pre-trained model and historical data from a file."""
        with open(path, 'rb') as f:
            data = pickle.load(f)
            self.model = data['model']
            self.hist = data['hist']

    def forecast_prophet(self, days: int = 30) -> ForecastResult:
        """Generates a forecast using the pre-loaded Prophet model."""
        if self.model is None or self.hist is None:
            print("WARNING: No pre-trained model loaded. Fitting a new model for this request. This is inefficient.")
            self.fit()
        
        # Create a future dataframe to predict on
        future_df = self.model.make_future_dataframe(periods=days)
        
        # Generate predictions
        forecast = self.model.predict(future_df)
        
        # Extract the relevant data
        forecast_slice = forecast.iloc[-days:]
        dates = forecast_slice['ds'].tolist()
        # Prophet's yhat_lower and yhat_upper correspond to our P10 and P90
        p10 = forecast_slice['yhat_lower'].tolist()
        p50 = forecast_slice['yhat'].tolist()
        p90 = forecast_slice['yhat_upper'].tolist()
        
        current_price = float(self.hist['y'].iloc[-1])

        return ForecastResult(dates, p10, p50, p90, current_price)

    def forecast_mc(self, days:int=30, paths:int=500)->ForecastResult:
        """Generates a forecast using Monte Carlo simulation."""
        if self.hist is None:
            print("WARNING: No historical data loaded. Fitting a new model for this request. This is inefficient.")
            self.fit()
        
        # Prophet prep renames columns, so we need to adjust
        self.hist['ret'] = self.hist['y'].pct_change().fillna(0.0)
        rets = self.hist['ret'].dropna().values
        mu = float(np.mean(rets))
        sigma = float(np.std(rets) or 0.01)
        spot = float(self.hist['y'].iloc[-1])
        sims = np.zeros((paths, days))
        for p in range(paths):
            sims[p] = spot * np.cumprod(1.0 + np.random.normal(mu, sigma, size=days))
        
        med = np.median(sims, axis=0)
        p10 = np.percentile(sims, 10, axis=0)
        p90 = np.percentile(sims, 90, axis=0)
        
        last_date = self.hist['ds'].max()
        ds = [last_date + timedelta(days=i + 1) for i in range(days)]
        
        return ForecastResult(ds, p10.tolist(), med.tolist(), p90.tolist(), spot)

    @staticmethod
    def apply_scenario(res:ForecastResult, basis:float=0.0, vol_scale:float=1.0, demand:float=0.0)->Dict[str,list]:
        """Applies scenario adjustments to a given forecast result."""
        adj={"p10":list(res.p10),"p50":list(res.p50),"p90":list(res.p90)}
        for k in adj: adj[k]=[v*(1+basis/100.0) for v in adj[k]]
        mid=adj["p50"]; width=[(adj["p90"][i]-adj["p10"][i])/2 for i in range(len(mid))]
        for i in range(len(mid)): adj["p10"][i]=mid[i]-width[i]*vol_scale; adj["p90"][i]=mid[i]+width[i]*vol_scale
        for k in adj: adj[k]=[v*(1+demand/1000.0) for v in adj[k]]
        return adj
