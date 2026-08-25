"""Unit tests for Baseline, Reactive, and Predictive controllers."""
import pytest
from simulator.config import load_config
from simulator.data_sources.synthetic import SyntheticDataSource
from simulator.controller import BaselineController, ReactiveController, PredictiveController
from models.schemas import ScenarioResult


def test_baseline_controller_execution():
    """Verify BaselineController runs without intervention and maintains initial battery SOC."""
    config = load_config("config.yaml")
    ds = SyntheticDataSource(config)
    
    controller = BaselineController(config)
    result = controller.run(ds)
    
    assert isinstance(result, ScenarioResult)
    assert result.name == "Baseline"
    assert len(result.dataframe) == config.simulation.intervals
    assert result.metrics.stress_intervals > 0
    assert result.metrics.deficit_energy_kwh > 0
    assert result.metrics.battery_throughput_kwh == 0.0
    assert result.metrics.min_battery_soc == config.battery.initial_soc
    assert result.metrics.max_battery_soc == config.battery.initial_soc


def test_reactive_controller_execution():
    """Verify ReactiveController reduces deficit compared to baseline."""
    config = load_config("config.yaml")
    ds = SyntheticDataSource(config)
    
    baseline = BaselineController(config).run(ds)
    reactive = ReactiveController(config).run(ds)
    
    assert reactive.name == "Reactive"
    assert reactive.metrics.deficit_energy_kwh < baseline.metrics.deficit_energy_kwh
    assert reactive.metrics.stress_intervals <= baseline.metrics.stress_intervals
    assert reactive.metrics.battery_throughput_kwh > 0
    assert len(reactive.controller_events) > 0


def test_predictive_controller_uses_forecast():
    """Verify PredictiveController prepares before stress and outperforms baseline and reactive."""
    config = load_config("config.yaml")
    ds = SyntheticDataSource(config)
    
    baseline = BaselineController(config).run(ds)
    reactive = ReactiveController(config).run(ds)
    predictive = PredictiveController(config).run(ds)
    
    assert predictive.name == "Predictive FlexProof"
    assert predictive.metrics.deficit_energy_kwh < baseline.metrics.deficit_energy_kwh
    assert predictive.metrics.deficit_energy_kwh <= reactive.metrics.deficit_energy_kwh
    assert predictive.metrics.forecast_mae > 0.0
    
    # Check that events include pre-shift / reservation decisions
    decisions = [e.decision for e in predictive.controller_events]
    assert any("reserve" in d.lower() or "pre-shift" in d.lower() or "charging" in d.lower() for d in decisions)
