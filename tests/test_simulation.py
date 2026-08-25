"""End-to-end simulation tests for FlexProof."""
import numpy as np
import pytest
from simulator.config import load_config
from simulator.simulation import run_all_scenarios, calculate_improvements
from simulator.validation import run_full_validation


def test_full_simulation_run_2880_intervals():
    """Verify 30-day simulation runs all 2880 intervals with valid dataframes."""
    config = load_config("config.yaml")
    results = run_all_scenarios(config)
    
    assert "baseline" in results
    assert "reactive" in results
    assert "predictive" in results
    
    for name, res in results.items():
        df = res.dataframe
        assert len(df) == 2880
        assert not df.isna().any().any()
        assert not np.any(np.isinf(df.select_dtypes(include=[np.number]).values))
        
        # Check required schema columns
        required_cols = [
            'demand_kw', 'renewable_kw', 'net_demand_kw',
            'forecast_demand_kw', 'forecast_renewable_kw', 'forecast_net_demand_kw',
            'stress', 'risk_level', 'battery_soc', 'battery_action',
            'flexibility_available_kw', 'flexibility_dispatched_kw', 'deficit_kw',
            'controlled_net_demand_kw'
        ]
        for col in required_cols:
            assert col in df.columns, f"Column {col} missing in {name} dataframe"


def test_simulation_validation_invariants():
    """Verify full validation engine passes with 0 critical errors."""
    config = load_config("config.yaml")
    results = run_all_scenarios(config)
    
    passed, val_report = run_full_validation(results, config)
    assert passed is True, f"Validation failed:\n{val_report}"
