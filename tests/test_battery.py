"""Unit tests for CommunityBattery physical model."""
import pytest
from simulator.battery import CommunityBattery
from models.schemas import BatteryAction


def test_battery_initialization():
    """Verify default initial battery parameters and physical limits."""
    bat = CommunityBattery(
        capacity_kwh=500.0,
        max_charge_power_kw=150.0,
        max_discharge_power_kw=150.0,
        min_soc=0.50,
        max_soc=0.90,
        initial_soc=0.70,
        charge_efficiency=0.95,
        discharge_efficiency=0.95
    )
    assert bat.soc == 0.70
    assert bat.capacity_kwh == 500.0
    assert bat.energy_kwh == pytest.approx(350.0)
    assert bat.available_energy_kwh == pytest.approx(100.0)  # (0.70 - 0.50) * 500
    assert bat.available_charge_energy_kwh == pytest.approx(100.0)  # (0.90 - 0.70) * 500
    assert bat.available_discharge_power_kw == 150.0
    assert bat.available_charge_power_kw == 150.0
    assert bat.action == BatteryAction.IDLE


def test_battery_invalid_soc_configuration():
    """Verify ValueError is raised if min_soc >= max_soc or initial_soc out of bounds."""
    with pytest.raises(ValueError):
        CommunityBattery(min_soc=0.90, max_soc=0.50)
    with pytest.raises(ValueError):
        CommunityBattery(initial_soc=1.20)
    with pytest.raises(ValueError):
        CommunityBattery(initial_soc=-0.10)


def test_battery_charging_physics_and_efficiency():
    """Verify charge efficiency losses and max SOC ceiling."""
    bat = CommunityBattery(capacity_kwh=500.0, initial_soc=0.70, max_soc=0.90, charge_efficiency=0.95)
    
    # Request 100 kW charge for 15 min (0.25 h)
    # Grid energy consumed = 25.0 kWh
    # Energy stored in battery = 25.0 * 0.95 = 23.75 kWh
    pwr_act, stored = bat.charge(power_kw=100.0, dt_hours=0.25)
    assert pwr_act == 100.0
    assert stored == pytest.approx(23.75)
    assert bat.soc == pytest.approx(0.70 + 23.75 / 500.0)
    assert bat.action == BatteryAction.CHARGING
    
    # Attempt to charge beyond max_soc (0.90)
    pwr_act2, stored2 = bat.charge(power_kw=500.0, dt_hours=1.0)
    assert bat.soc <= 0.90001
    assert bat.soc >= 0.89999
    
    # Once at max_soc, further charging returns 0
    pwr_act3, stored3 = bat.charge(power_kw=50.0, dt_hours=0.25)
    assert pwr_act3 == 0.0
    assert stored3 == 0.0


def test_battery_discharging_physics_and_efficiency():
    """Verify discharge efficiency losses and min SOC floor."""
    bat = CommunityBattery(capacity_kwh=500.0, initial_soc=0.70, min_soc=0.50, discharge_efficiency=0.95)
    
    # Request 100 kW delivered to grid for 15 min (0.25 h)
    # Grid energy delivered = 25.0 kWh
    # Energy consumed from battery = 25.0 / 0.95 = 26.3158 kWh
    pwr_act, energy_consumed = bat.discharge(power_kw=100.0, dt_hours=0.25)
    assert pwr_act == 100.0
    assert energy_consumed == pytest.approx(25.0 / 0.95)
    assert bat.soc == pytest.approx(0.70 - (25.0 / 0.95) / 500.0)
    assert bat.action == BatteryAction.DISCHARGING
    
    # Attempt to discharge below min_soc (0.50)
    pwr_act2, energy_consumed2 = bat.discharge(power_kw=500.0, dt_hours=2.0)
    assert bat.soc >= 0.49999
    assert bat.available_energy_kwh == pytest.approx(0.0, abs=1e-4)
    
    # Once at min_soc, further discharge returns 0
    pwr_act3, energy_consumed3 = bat.discharge(power_kw=50.0, dt_hours=0.25)
    assert pwr_act3 == 0.0
    assert energy_consumed3 == 0.0


def test_battery_reset():
    """Verify reset restores initial SOC and clears tracking metrics."""
    bat = CommunityBattery(capacity_kwh=500.0, initial_soc=0.70)
    bat.charge(50.0, 0.25)
    bat.discharge(80.0, 0.25)
    assert bat.throughput_kwh > 0
    
    bat.reset()
    assert bat.soc == 0.70
    assert bat.action == BatteryAction.IDLE
    assert bat.throughput_kwh == 0.0
    assert bat.min_soc_reached == 0.70
    assert bat.max_soc_reached == 0.70
