"""Unit tests for metrics calculation and comparative improvement formulas."""
import pytest
from simulator.metrics import (
    calculate_improvement_metrics,
    calculate_predictive_advantage,
    format_metrics_report
)
from models.schemas import SimulationMetrics, ImprovementMetrics


def test_improvement_metrics_calculation():
    """Verify deficit reduction and stress reduction percentage formulas."""
    baseline = SimulationMetrics(
        stress_intervals=100,
        stress_duration_hours=25.0,
        deficit_energy_kwh=2000.0,
        max_deficit_kw=300.0,
        peak_net_demand_kw=2600.0
    )
    controlled = SimulationMetrics(
        stress_intervals=20,
        stress_duration_hours=5.0,
        deficit_energy_kwh=200.0,
        max_deficit_kw=150.0,
        peak_net_demand_kw=2450.0
    )
    
    imp = calculate_improvement_metrics(baseline, controlled)
    assert isinstance(imp, ImprovementMetrics)
    assert imp.deficit_reduction_pct == pytest.approx(90.0)
    assert imp.stress_reduction_pct == pytest.approx(80.0)
    assert imp.max_deficit_reduction_pct == pytest.approx(50.0)
    assert imp.peak_demand_reduction_kw == pytest.approx(150.0)


def test_predictive_advantage_calculation():
    """Verify predictive advantage relative to reactive residual deficit."""
    reactive = SimulationMetrics(deficit_energy_kwh=200.0)
    predictive = SimulationMetrics(deficit_energy_kwh=10.0)
    
    adv = calculate_predictive_advantage(reactive, predictive)
    # (200 - 10) / 200 * 100 = 95.0%
    assert adv == pytest.approx(95.0)


def test_format_metrics_report_string():
    """Verify metrics report string generation."""
    m1 = SimulationMetrics(stress_intervals=100, deficit_energy_kwh=2000.0)
    m2 = SimulationMetrics(stress_intervals=30, deficit_energy_kwh=300.0)
    m3 = SimulationMetrics(stress_intervals=5, deficit_energy_kwh=20.0)
    
    report = format_metrics_report(m1, m2, m3)
    assert "FLEXPROOF SIMULATION RESULTS" in report
    assert "BASELINE" in report
    assert "REACTIVE" in report
    assert "PREDICTIVE FLEXPROOF" in report
