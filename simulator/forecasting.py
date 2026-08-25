"""Forecasting engine for FlexProof.

Provides demand, renewable, and net demand forecasting.
Architecture is model-agnostic - the forecasting interface
remains stable regardless of underlying model.

Current implementation: Lightweight statistical model
Future: XGBoost, LightGBM, LSTM, TFT
"""
import numpy as np
import pandas as pd
from typing import Optional, Tuple
from models.schemas import ForecastResult


class ForecastModel:
    """Base forecast model interface."""
    
    def predict(self, history: np.ndarray, horizon: int) -> np.ndarray:
        raise NotImplementedError


class LightweightForecaster(ForecastModel):
    """Lightweight statistical forecaster.
    
    Uses a combination of:
    - Same-time-yesterday lag
    - Same-time-last-week lag (if available)
    - Rolling mean of recent intervals
    - Recent trend extrapolation
    - Time-of-day weighting
    """
    
    def __init__(self, intervals_per_day: int = 96):
        self.intervals_per_day = intervals_per_day
    
    def predict(self, history: np.ndarray, horizon: int) -> np.ndarray:
        """Predict next `horizon` intervals from history.
        
        Args:
            history: Historical values (at least 2 days recommended)
            horizon: Number of intervals to forecast
            
        Returns:
            Array of forecasted values
        """
        n = len(history)
        forecast = np.zeros(horizon)
        
        for h in range(horizon):
            estimates = []
            weights = []
            
            # 1. Same time yesterday
            lag_1d = n - self.intervals_per_day + h
            if 0 <= lag_1d < n:
                estimates.append(history[lag_1d])
                weights.append(0.35)
            
            # 2. Same time 2 days ago
            lag_2d = n - 2 * self.intervals_per_day + h
            if 0 <= lag_2d < n:
                estimates.append(history[lag_2d])
                weights.append(0.15)
            
            # 3. Same time last week
            lag_7d = n - 7 * self.intervals_per_day + h
            if 0 <= lag_7d < n:
                estimates.append(history[lag_7d])
                weights.append(0.10)
            
            # 4. Rolling mean of last 4 intervals (recent level)
            if n >= 4:
                recent_mean = np.mean(history[-4:])
                estimates.append(recent_mean)
                weights.append(0.25)
            
            # 5. Recent trend (linear extrapolation of last 8 intervals)
            if n >= 8:
                recent = history[-8:]
                trend = (recent[-1] - recent[0]) / 8
                trend_value = history[-1] + trend * (h + 1)
                estimates.append(trend_value)
                weights.append(0.15)
            
            if estimates:
                weights = np.array(weights)
                weights = weights / weights.sum()
                forecast[h] = np.average(estimates, weights=weights)
            else:
                forecast[h] = history[-1] if n > 0 else 0.0
        
        return forecast


class ForecastingEngine:
    """Main forecasting engine for FlexProof.
    
    Manages demand and renewable forecasting with
    configurable horizon and model selection.
    """
    
    def __init__(self, config):
        """
        Args:
            config: FlexProofConfig object
        """
        self.horizon_intervals = config.forecasting.horizon_intervals
        self.lookback_intervals = config.forecasting.lookback_intervals
        self.feeder_limit_kw = config.feeder.firm_limit_kw
        
        # Initialize forecasting models
        intervals_per_day = int(24 * 60 / config.simulation.resolution_minutes)
        self.demand_model = LightweightForecaster(intervals_per_day)
        self.renewable_model = LightweightForecaster(intervals_per_day)
        
        # Forecast error tracking
        self.demand_errors: list = []
        self.renewable_errors: list = []
    
    def forecast(self, demand_history: np.ndarray,
                 renewable_history: np.ndarray,
                 horizon: Optional[int] = None) -> ForecastResult:
        """Generate forecasts for demand, renewable, and net demand.
        
        Args:
            demand_history: Historical demand values (kW)
            renewable_history: Historical renewable values (kW)
            horizon: Override forecast horizon (intervals)
            
        Returns:
            ForecastResult with all forecast arrays
        """
        h = horizon or self.horizon_intervals
        
        # Forecast demand
        demand_fc = self.demand_model.predict(demand_history, h)
        
        # Forecast renewable (ensure non-negative)
        renewable_fc = self.renewable_model.predict(renewable_history, h)
        renewable_fc = np.maximum(renewable_fc, 0.0)
        
        # Calculate derived forecasts
        net_demand_fc = demand_fc - renewable_fc
        gap_fc = np.maximum(0.0, net_demand_fc - self.feeder_limit_kw)
        
        # Stress probability based on ratio to limit
        stress_prob = np.zeros(h)
        for i in range(h):
            ratio = net_demand_fc[i] / self.feeder_limit_kw if self.feeder_limit_kw > 0 else 0
            if ratio >= 1.0:
                stress_prob[i] = min(1.0, 0.7 + 0.3 * (ratio - 1.0))
            elif ratio >= 0.85:
                stress_prob[i] = 0.3 + 0.4 * (ratio - 0.85) / 0.15
            elif ratio >= 0.75:
                stress_prob[i] = 0.1 + 0.2 * (ratio - 0.75) / 0.10
            else:
                stress_prob[i] = max(0, ratio * 0.1)
        
        return ForecastResult(
            forecast_demand_kw=demand_fc,
            forecast_renewable_kw=renewable_fc,
            forecast_net_demand_kw=net_demand_fc,
            forecast_gap_kw=gap_fc,
            stress_probability=stress_prob,
            horizon_intervals=h
        )
    
    def update_errors(self, predicted: float, actual: float, is_demand: bool = True):
        """Track forecast errors for quality metrics."""
        error = abs(predicted - actual)
        if is_demand:
            self.demand_errors.append(error)
        else:
            self.renewable_errors.append(error)
    
    def get_forecast_metrics(self) -> dict:
        """Calculate forecast quality metrics."""
        metrics = {}
        
        if self.demand_errors:
            errors = np.array(self.demand_errors)
            metrics['demand_mae'] = float(np.mean(errors))
            metrics['demand_rmse'] = float(np.sqrt(np.mean(errors**2)))
        else:
            metrics['demand_mae'] = 0.0
            metrics['demand_rmse'] = 0.0
        
        if self.renewable_errors:
            errors = np.array(self.renewable_errors)
            metrics['renewable_mae'] = float(np.mean(errors))
            metrics['renewable_rmse'] = float(np.sqrt(np.mean(errors**2)))
        else:
            metrics['renewable_mae'] = 0.0
            metrics['renewable_rmse'] = 0.0
        
        # Combined
        all_demand = metrics['demand_mae']
        all_renewable = metrics['renewable_mae']
        metrics['overall_mae'] = (all_demand + all_renewable) / 2
        metrics['overall_rmse'] = (metrics['demand_rmse'] + metrics['renewable_rmse']) / 2
        
        return metrics
    
    def reset(self):
        """Reset error tracking."""
        self.demand_errors.clear()
        self.renewable_errors.clear()
