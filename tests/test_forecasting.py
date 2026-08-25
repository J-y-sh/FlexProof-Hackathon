"""Unit tests for ForecastingEngine and statistical predictor."""
import numpy as np
import pytest
from simulator.config import load_config
from simulator.forecasting import ForecastingEngine, LightweightForecaster
from models.schemas import ForecastResult


def test_lightweight_forecaster_output_dimensions():
    """Verify forecaster produces requested horizon length."""
    forecaster = LightweightForecaster(intervals_per_day=96)
    history = np.sin(np.linspace(0, 10 * np.pi, 288)) * 500.0 + 1000.0
    
    for h in [1, 4, 8, 12]:
        preds = forecaster.predict(history, horizon=h)
        assert len(preds) == h
        assert isinstance(preds, np.ndarray)


def test_forecasting_engine_integration():
    """Verify forecasting engine integrates demand and solar predictions."""
    config = load_config("config.yaml")
    engine = ForecastingEngine(config)
    
    rng = np.random.RandomState(42)
    demand_hist = rng.uniform(1000.0, 2200.0, 192)
    solar_hist = rng.uniform(0.0, 750.0, 192)
    
    res = engine.forecast(demand_hist, solar_hist, horizon=4)
    assert isinstance(res, ForecastResult)
    assert len(res.forecast_demand_kw) == 4
    assert len(res.forecast_renewable_kw) == 4
    assert len(res.forecast_net_demand_kw) == 4
    assert len(res.forecast_gap_kw) == 4
    assert len(res.stress_probability) == 4
    
    # Solar must never be negative
    assert np.all(res.forecast_renewable_kw >= 0.0)
    
    # Net demand = Demand - Renewable
    assert np.allclose(
        res.forecast_net_demand_kw,
        res.forecast_demand_kw - res.forecast_renewable_kw
    )
    
    # Gap = max(0, Net - Limit)
    expected_gap = np.maximum(0.0, res.forecast_net_demand_kw - config.feeder.firm_limit_kw)
    assert np.allclose(res.forecast_gap_kw, expected_gap)


def test_forecasting_error_tracking():
    """Verify MAE and RMSE calculation over updates."""
    config = load_config("config.yaml")
    engine = ForecastingEngine(config)
    
    engine.update_errors(predicted=1500.0, actual=1450.0, is_demand=True)
    engine.update_errors(predicted=1600.0, actual=1650.0, is_demand=True)
    engine.update_errors(predicted=500.0, actual=480.0, is_demand=False)
    
    metrics = engine.get_forecast_metrics()
    assert metrics['demand_mae'] == pytest.approx(50.0)
    assert metrics['demand_rmse'] == pytest.approx(50.0)
    assert metrics['renewable_mae'] == pytest.approx(20.0)
    assert metrics['overall_mae'] == pytest.approx(35.0)
