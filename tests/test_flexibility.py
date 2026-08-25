"""Unit tests for FlexibleLoadManager and FlexibilityCoordinator."""
import pandas as pd
import pytest
from simulator.config import load_config
from simulator.flexible_loads import FlexibleLoadManager
from simulator.battery import CommunityBattery
from simulator.flexibility import FlexibilityCoordinator
from models.schemas import ResourceStatus, RiskLevel, BatteryAction


def test_flexible_load_manager_initialization():
    """Verify flexible resource fleet registration and availability."""
    config = load_config("config.yaml")
    manager = FlexibleLoadManager(config.flexible_loads)
    
    assert len(manager.resources) == 5
    summary = manager.get_summary()
    assert summary['total_available_kw'] > 0
    assert summary['total_shifted_kw'] == 0
    assert summary['flexibility_events'] == 0


def test_load_shifting_and_energy_conservation():
    """Verify load shifting reduces demand and is completely energy-conserving upon restoration."""
    config = load_config("config.yaml")
    manager = FlexibleLoadManager(config.flexible_loads)
    
    # Request 80 kW shift at interval 10 for duration 4
    shifted_kw, actions = manager.shift_load(required_kw=80.0, current_interval=10, duration_intervals=4)
    assert shifted_kw == pytest.approx(80.0)
    assert len(actions) > 0
    assert manager.total_shifted_energy_kwh == pytest.approx(80.0 * 4 * 0.25)
    assert manager.flexibility_events > 0
    
    # During stress / unsafe conditions, restoration must NOT occur
    rest_unsafe = manager.get_restoration_power(current_interval=11, is_safe_window=False)
    assert rest_unsafe == 0.0
    
    # During safe window, restoration proceeds smoothly
    rest_safe = manager.get_restoration_power(
        current_interval=30, is_safe_window=True, max_safe_restore_kw=1000.0
    )
    assert rest_safe == pytest.approx(manager.total_shifted_energy_kwh / 0.25)
    assert manager.total_restored_energy_kwh == pytest.approx(manager.total_shifted_energy_kwh)


def test_flexibility_coordinator_dispatch():
    """Verify coordinator prioritizes flexible loads first, then battery."""
    config = load_config("config.yaml")
    battery = CommunityBattery(capacity_kwh=500.0, initial_soc=0.70)
    flex_manager = FlexibleLoadManager(config.flexible_loads)
    coordinator = FlexibilityCoordinator(battery, flex_manager, dt_hours=0.25)
    ts = pd.Timestamp("2024-01-01 18:00:00")
    
    # Dispatch for a 150 kW deficit
    res = coordinator.dispatch_for_stress(
        deficit_kw=150.0, current_interval=10, risk_level=RiskLevel.WARNING, timestamp=ts
    )
    assert res['total_flexibility_kw'] == pytest.approx(150.0)
    assert res['remaining_deficit_kw'] == 0.0
    assert len(res['events']) > 0
    assert res['flex_shifted_kw'] > 0
