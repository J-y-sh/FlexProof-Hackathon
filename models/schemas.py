from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional
import pandas as pd
import numpy as np

class RiskLevel(str, Enum):
    NORMAL = "NORMAL"
    WATCH = "WATCH"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"

class BatteryAction(str, Enum):
    IDLE = "IDLE"
    CHARGING = "CHARGING"
    DISCHARGING = "DISCHARGING"
    RESERVED = "RESERVED"

class ResourceStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    RESERVED = "RESERVED"
    SHIFTED = "SHIFTED"
    CURTAILED = "CURTAILED"
    DISPATCHED = "DISPATCHED"
    RESTORED = "RESTORED"

class ResourceType(str, Enum):
    EV_CHARGING = "ev_charging"
    WATER_PUMPING = "water_pumping"
    HVAC = "hvac"
    COMMERCIAL_REFRIGERATION = "commercial_refrigeration"
    AGRICULTURAL_PUMPING = "agricultural_pumping"

@dataclass
class FlexibleResource:
    resource_id: str
    resource_type: ResourceType
    baseline_power_kw: float
    available_power_kw: float
    available_energy_kwh: float
    minimum_duration: int  # intervals
    maximum_duration: int  # intervals
    response_time: int  # intervals
    availability: float  # 0-1
    priority: int
    criticality: float = 0.0
    status: ResourceStatus = ResourceStatus.AVAILABLE
    shifted_energy_kwh: float = 0.0
    shift_remaining_intervals: int = 0

@dataclass
class BatteryState:
    soc: float
    energy_kwh: float
    available_energy_kwh: float
    available_power_kw: float
    action: BatteryAction = BatteryAction.IDLE
    power_kw: float = 0.0

@dataclass
class FeederState:
    timestamp: pd.Timestamp
    demand_kw: float
    renewable_kw: float
    net_demand_kw: float
    feeder_limit_kw: float
    loading_pct: float
    stress: bool
    deficit_kw: float
    risk_level: RiskLevel = RiskLevel.NORMAL

@dataclass
class ForecastResult:
    forecast_demand_kw: np.ndarray
    forecast_renewable_kw: np.ndarray
    forecast_net_demand_kw: np.ndarray
    forecast_gap_kw: np.ndarray
    stress_probability: np.ndarray
    horizon_intervals: int

@dataclass
class ControllerEvent:
    timestamp: pd.Timestamp
    decision: str
    reason: str
    predicted_gap_kw: float = 0.0
    required_flexibility_kw: float = 0.0
    resource_selected: str = ""
    power_requested_kw: float = 0.0
    power_delivered_kw: float = 0.0
    battery_soc_before: float = 0.0
    battery_soc_after: float = 0.0

@dataclass
class ControllerAction:
    resource_actions: List[dict] = field(default_factory=list)
    battery_action: BatteryAction = BatteryAction.IDLE
    battery_power_kw: float = 0.0
    reserve_decision: str = ""
    events: List[ControllerEvent] = field(default_factory=list)
    total_flexibility_kw: float = 0.0
    total_battery_kw: float = 0.0

@dataclass
class IntervalRecord:
    timestamp: pd.Timestamp
    demand_kw: float
    renewable_kw: float
    net_demand_kw: float
    forecast_demand_kw: float = 0.0
    forecast_renewable_kw: float = 0.0
    forecast_net_demand_kw: float = 0.0
    forecast_gap_kw: float = 0.0
    stress: bool = False
    risk_level: str = "NORMAL"
    battery_soc: float = 0.0
    battery_action: str = "IDLE"
    flexibility_available_kw: float = 0.0
    flexibility_reserved_kw: float = 0.0
    flexibility_dispatched_kw: float = 0.0
    deficit_kw: float = 0.0
    controlled_net_demand_kw: float = 0.0

@dataclass
class SimulationMetrics:
    stress_intervals: int = 0
    stress_duration_hours: float = 0.0
    deficit_energy_kwh: float = 0.0
    max_deficit_kw: float = 0.0
    avg_deficit_kw: float = 0.0
    stress_percentage: float = 0.0
    peak_net_demand_kw: float = 0.0
    peak_demand_kw: float = 0.0
    total_renewable_kwh: float = 0.0
    renewable_utilization_pct: float = 0.0
    battery_throughput_kwh: float = 0.0
    flexibility_events: int = 0
    shifted_energy_kwh: float = 0.0
    avoided_deficit_kwh: float = 0.0
    min_battery_soc: float = 1.0
    max_battery_soc: float = 0.0
    forecast_mae: float = 0.0
    forecast_rmse: float = 0.0

@dataclass
class ScenarioResult:
    name: str
    dataframe: pd.DataFrame
    metrics: SimulationMetrics
    controller_events: List[ControllerEvent] = field(default_factory=list)
    battery_history: List[dict] = field(default_factory=list)
    flexibility_history: List[dict] = field(default_factory=list)
    forecast_metrics: dict = field(default_factory=dict)

@dataclass
class ImprovementMetrics:
    deficit_reduction_pct: float = 0.0
    stress_reduction_pct: float = 0.0
    max_deficit_reduction_pct: float = 0.0
    peak_demand_reduction_kw: float = 0.0
    predictive_advantage_pct: float = 0.0
