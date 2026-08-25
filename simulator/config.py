import yaml
from pathlib import Path
from pydantic import BaseModel, model_validator
from typing import Optional

class SimulationConfig(BaseModel):
    duration_days: int = 30
    resolution_minutes: int = 15
    intervals: int = 2880
    random_seed: int = 42

    @property
    def dt_hours(self) -> float:
        """Computed property for time step in hours."""
        return self.resolution_minutes / 60.0

    @property
    def total_intervals(self) -> int:
        """Computed property for total number of intervals in the simulation."""
        return int(self.duration_days * 24 * 60 / self.resolution_minutes)


class FeederConfig(BaseModel):
    firm_limit_kw: float = 2300.0
    warning_threshold: float = 0.85
    watch_threshold: float = 0.75


class DemandConfig(BaseModel):
    residential_peak_kw: float = 1200.0
    commercial_peak_kw: float = 600.0
    industrial_peak_kw: float = 400.0
    noise_std: float = 0.03


class RenewableConfig(BaseModel):
    solar_capacity_kw: float = 800.0
    cloud_probability: float = 0.15
    noise_std: float = 0.05


class BatteryConfig(BaseModel):
    capacity_kwh: float = 500.0
    max_charge_power_kw: float = 150.0
    max_discharge_power_kw: float = 150.0
    min_soc: float = 0.50
    max_soc: float = 0.90
    initial_soc: float = 0.70
    charge_efficiency: float = 0.95
    discharge_efficiency: float = 0.95

    @model_validator(mode='after')
    def validate_soc_limits(self):
        if self.min_soc >= self.max_soc:
            raise ValueError("min_soc must be strictly less than max_soc")
        if not (self.min_soc <= self.initial_soc <= self.max_soc):
            raise ValueError("initial_soc must be between min_soc and max_soc")
        return self


class FlexibleLoadTypeConfig(BaseModel):
    count: int
    power_per_unit_kw: float
    flexibility_fraction: float
    min_shift_intervals: int
    max_shift_intervals: int
    response_time_intervals: int
    priority: int


class FlexibleLoadsConfig(BaseModel):
    ev_charging: FlexibleLoadTypeConfig
    water_pumping: FlexibleLoadTypeConfig
    hvac: FlexibleLoadTypeConfig
    commercial_refrigeration: FlexibleLoadTypeConfig
    agricultural_pumping: FlexibleLoadTypeConfig


class ForecastingConfig(BaseModel):
    horizon_intervals: int = 4
    model_type: str = "lightweight"
    lookback_intervals: int = 96
    update_frequency: int = 1


class StressRiskThresholds(BaseModel):
    watch: float = 0.75
    warning: float = 0.85
    critical: float = 0.95


class StressConfig(BaseModel):
    risk_thresholds: StressRiskThresholds


class PredictiveControllerConfig(BaseModel):
    reserve_margin: float = 0.1
    min_reserve_soc: float = 0.55
    dispatch_threshold: float = 0.90
    preparation_intervals: int = 4


class ReactiveControllerConfig(BaseModel):
    activation_threshold: float = 1.0
    max_battery_discharge_fraction: float = 0.8


class ControllerConfig(BaseModel):
    predictive: PredictiveControllerConfig
    reactive: ReactiveControllerConfig


class PathsConfig(BaseModel):
    raw_data: str = "data/raw"
    processed_data: str = "data/processed"
    sample_data: str = "data/sample"


class FlexProofConfig(BaseModel):
    simulation: SimulationConfig
    feeder: FeederConfig
    demand: DemandConfig
    renewable: RenewableConfig
    battery: BatteryConfig
    flexible_loads: FlexibleLoadsConfig
    forecasting: ForecastingConfig
    stress: StressConfig
    controller: ControllerConfig
    paths: PathsConfig


_GLOBAL_CONFIG: Optional[FlexProofConfig] = None


def load_config(path: str = "config.yaml") -> FlexProofConfig:
    """Load configuration from a YAML file."""
    global _GLOBAL_CONFIG
    
    config_path = Path(path)
    if not config_path.is_absolute():
        # Make path relative to the workspace root if it's relative
        workspace_dir = Path(__file__).parent.parent
        config_path = workspace_dir / path

    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found at {config_path}")
        
    with open(config_path, "r") as f:
        config_data = yaml.safe_load(f)
        
    _GLOBAL_CONFIG = FlexProofConfig(**config_data)
    return _GLOBAL_CONFIG


def get_config() -> FlexProofConfig:
    """Get the currently loaded global configuration."""
    if _GLOBAL_CONFIG is None:
        raise RuntimeError("Configuration is not loaded. Call load_config() first.")
    return _GLOBAL_CONFIG
