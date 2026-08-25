"""Unit tests for Feeder model and StressPredictionEngine."""
import numpy as np
import pandas as pd
import pytest
from simulator.feeder import Feeder
from simulator.stress import StressPredictionEngine
from models.schemas import RiskLevel, ForecastResult


def test_feeder_state_and_stress_calculation():
    """Verify feeder state calculations under normal, watch, warning, and critical loading."""
    feeder = Feeder(firm_limit_kw=2300.0, warning_threshold=0.85, watch_threshold=0.75)
    ts = pd.Timestamp("2024-01-01 12:00:00")
    
    # 1. Normal state (loading < 75%)
    state1 = feeder.calculate_state(ts, demand_kw=1500.0, renewable_kw=500.0)
    assert state1.net_demand_kw == 1000.0
    assert state1.loading_pct == pytest.approx(1000.0 / 2300.0 * 100)
    assert not state1.stress
    assert state1.deficit_kw == 0.0
    assert state1.risk_level == RiskLevel.NORMAL
    
    # 2. Watch state (75% <= loading < 85%)
    state2 = feeder.calculate_state(ts, demand_kw=1800.0, renewable_kw=0.0)
    assert state2.loading_pct == pytest.approx(1800.0 / 2300.0 * 100)
    assert state2.risk_level == RiskLevel.WATCH
    assert not state2.stress
    
    # 3. Warning state (85% <= loading < 100%)
    state3 = feeder.calculate_state(ts, demand_kw=2100.0, renewable_kw=0.0)
    assert state3.risk_level == RiskLevel.WARNING
    assert not state3.stress
    
    # 4. Critical / Stress state (loading >= 100%)
    state4 = feeder.calculate_state(ts, demand_kw=2600.0, renewable_kw=100.0)
    assert state4.net_demand_kw == 2500.0
    assert state4.stress
    assert state4.deficit_kw == pytest.approx(200.0)
    assert state4.risk_level == RiskLevel.CRITICAL


def test_stress_prediction_engine():
    """Verify prediction engine correctly identifies upcoming stress from forecast arrays."""
    engine = StressPredictionEngine(feeder_limit_kw=2300.0)
    
    forecast = ForecastResult(
        forecast_demand_kw=np.array([1600.0, 2350.0, 2500.0, 2400.0]),
        forecast_renewable_kw=np.array([0.0, 0.0, 0.0, 0.0]),
        forecast_net_demand_kw=np.array([1600.0, 2350.0, 2500.0, 2400.0]),
        forecast_gap_kw=np.array([0.0, 50.0, 200.0, 100.0]),
        stress_probability=np.array([0.1, 0.8, 1.0, 0.9]),
        horizon_intervals=4
    )
    
    pred = engine.predict_stress(forecast)
    assert pred['stress_predicted'] is True
    assert pred['critical_predicted'] is True
    assert pred['max_gap_kw'] == pytest.approx(200.0)
    assert pred['time_to_stress_intervals'] == 1  # Index 1 is first critical/warning
    assert pred['max_risk'] == RiskLevel.CRITICAL
