"""Scenario integrity and reproducibility tests.

Verifies that all three scenarios (Baseline, Reactive, Predictive)
run on the EXACT SAME underlying time series inputs and initial conditions.
"""
import numpy as np
import pytest
from simulator.config import load_config
from simulator.data_sources.synthetic import SyntheticDataSource
from simulator.simulation import run_all_scenarios


def test_scenario_input_equality():
    """Verify demand and renewable time series are identical across all scenarios."""
    config = load_config("config.yaml")
    results = run_all_scenarios(config)
    
    base_df = results['baseline'].dataframe
    react_df = results['reactive'].dataframe
    pred_df = results['predictive'].dataframe
    
    # Timestamps must match exactly
    assert base_df.index.equals(react_df.index)
    assert base_df.index.equals(pred_df.index)
    
    # Demand time series must match exactly
    np.testing.assert_allclose(base_df['demand_kw'].values, react_df['demand_kw'].values, atol=1e-5)
    np.testing.assert_allclose(base_df['demand_kw'].values, pred_df['demand_kw'].values, atol=1e-5)
    
    # Renewable time series must match exactly
    np.testing.assert_allclose(base_df['renewable_kw'].values, react_df['renewable_kw'].values, atol=1e-5)
    np.testing.assert_allclose(base_df['renewable_kw'].values, pred_df['renewable_kw'].values, atol=1e-5)


def test_deterministic_reproducibility():
    """Verify that running the simulation twice with seed=42 produces bit-for-bit identical results."""
    config1 = load_config("config.yaml")
    config2 = load_config("config.yaml")
    
    res1 = run_all_scenarios(config1)
    res2 = run_all_scenarios(config2)
    
    for key in ['baseline', 'reactive', 'predictive']:
        df1 = res1[key].dataframe
        df2 = res2[key].dataframe
        np.testing.assert_allclose(
            df1['controlled_net_demand_kw'].values,
            df2['controlled_net_demand_kw'].values,
            atol=1e-6
        )
        assert res1[key].metrics.deficit_energy_kwh == pytest.approx(res2[key].metrics.deficit_energy_kwh)
        assert res1[key].metrics.stress_intervals == res2[key].metrics.stress_intervals


def test_deficit_hierarchy():
    """Verify that Predictive deficit <= Reactive deficit <= Baseline deficit."""
    config = load_config("config.yaml")
    results = run_all_scenarios(config)
    
    b_def = results['baseline'].metrics.deficit_energy_kwh
    r_def = results['reactive'].metrics.deficit_energy_kwh
    p_def = results['predictive'].metrics.deficit_energy_kwh
    
    assert r_def <= b_def, f"Reactive deficit ({r_def}) was greater than Baseline ({b_def})"
    assert p_def <= r_def, f"Predictive deficit ({p_def}) was greater than Reactive ({r_def})"
