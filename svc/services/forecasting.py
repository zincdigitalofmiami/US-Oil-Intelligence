from __future__ import annotations
import numpy as np, pandas as pd
from dataclasses import dataclass
from typing import List, Dict
from datetime import timedelta
from sklearn.linear_model import LinearRegression
from .data_loader import load_market_daily

@dataclass
class ForecastResult:
    dates: List[pd.Timestamp]
    p10: List[float]; p50: List[float]; p90: List[float]
    current_price: float

class Forecaster:
    def __init__(self):
        self.model=None; self.hist=None
    def _prep(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepares the input DataFrame by adding features for the model."""
        df = df.copy(); df['date']=pd.to_datetime(df['date']); df=df.sort_values('date')
        df['ret']=df['price'].pct_change().fillna(0.0)
        df['vol']=df['ret'].rolling(5, min_periods=1).std().fillna(0.01)
        df['ma5']=df['price'].rolling(5, min_periods=1).mean()
        df['ma20']=df['price'].rolling(20, min_periods=1).mean()
        df['trend']=range(len(df)); return df
    def fit(self):
        df=load_market_daily(); dfp=self._prep(df)
        X=dfp[['trend','ma5','ma20','vol']].values; y=dfp['price'].values
        self.model=LinearRegression().fit(X,y); self.hist=dfp; return self
    def forecast_lr(self, days:int=30)->ForecastResult:
        if self.model is None: self.fit()
        last=self.hist.iloc[-1]; last_date=self.hist['date'].max()
        ds=[]; p10=[]; p50=[]; p90=[]
        for i in range(days):
            d = pd.to_datetime(last_date)+timedelta(days=i+1); ds.append(d)
            trend=len(self.hist)+i; ma5=float(last['ma5']); ma20=float(last['ma20']); vol=float(last['vol'])
            base=float(self.model.predict([[trend,ma5,ma20,vol]])[0])
            std=max(0.0005,vol)*max(0.2,base)*np.sqrt(i+1)*2
            p10.append(base-1.28*std); p50.append(base); p90.append(base+1.28*std)
        return ForecastResult(ds,p10,p50,p90,float(self.hist['price'].iloc[-1]))
    def forecast_mc(self, days:int=30, paths:int=500)->ForecastResult:
        if self.hist is None: self.fit()
        rets=self.hist['ret'].dropna().values; mu=float(np.mean(rets)); sigma=float(np.std(rets) or 0.01)
        spot=float(self.hist['price'].iloc[-1]); sims=np.zeros((paths,days))
        for p in range(paths): sims[p]=spot*np.cumprod(1.0+np.random.normal(mu,sigma,size=days))
        med=np.median(sims,axis=0); p10=np.percentile(sims,10,axis=0); p90=np.percentile(sims,90,axis=0)
        ds=[pd.to_datetime(self.hist['date'].max())+timedelta(days=i+1) for i in range(days)]
        return ForecastResult(ds,p10.tolist(),med.tolist(),p90.tolist(),spot)
    @staticmethod
    def apply_scenario(res:ForecastResult, basis:float=0.0, vol_scale:float=1.0, demand:float=0.0)->Dict[str,list]:
        adj={"p10":list(res.p10),"p50":list(res.p50),"p90":list(res.p90)}
        for k in adj: adj[k]=[v*(1+basis/100.0) for v in adj[k]]
        mid=adj["p50"]; width=[(adj["p90"][i]-adj["p10"][i])/2 for i in range(len(mid))]
        for i in range(len(mid)): adj["p10"][i]=mid[i]-width[i]*vol_scale; adj["p90"][i]=mid[i]+width[i]*vol_scale
        for k in adj: adj[k]=[v*(1+demand/1000.0) for v in adj[k]]
        return adj
# Triggering CI/CD pipeline
