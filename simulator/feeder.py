"""Feeder model for FlexProof.

Models a distribution feeder with firm capacity limit,
stress detection, and deficit calculation.
"""
import numpy as np
import pandas as pd
from typing import Tuple

from models.schemas import FeederState, RiskLevel


class Feeder:
    """Distribution feeder model.
    
    Attributes:
        firm_limit_kw: Maximum continuous feeder capacity (kW)
        warning_threshold: Fraction of limit that triggers WARNING
        watch_threshold: Fraction of limit that triggers WATCH
    """
    
    def __init__(self, firm_limit_kw: float, 
                 warning_threshold: float = 0.85,
                 watch_threshold: float = 0.75):
        self.firm_limit_kw = firm_limit_kw
        self.warning_threshold = warning_threshold
        self.watch_threshold = watch_threshold
    
    def calculate_state(self, timestamp: pd.Timestamp,
                        demand_kw: float, 
                        renewable_kw: float) -> FeederState:
        """Calculate feeder state for a single interval.
        
        Args:
            timestamp: Current timestamp
            demand_kw: Total demand in kW
            renewable_kw: Renewable generation in kW
            
        Returns:
            FeederState with all calculated values
        """
        net_demand_kw = demand_kw - renewable_kw
        loading_pct = (net_demand_kw / self.firm_limit_kw) * 100 if self.firm_limit_kw > 0 else 0.0
        stress = net_demand_kw > self.firm_limit_kw
        deficit_kw = max(0.0, net_demand_kw - self.firm_limit_kw)
        risk_level = self._calculate_risk_level(net_demand_kw)
        
        return FeederState(
            timestamp=timestamp,
            demand_kw=demand_kw,
            renewable_kw=renewable_kw,
            net_demand_kw=net_demand_kw,
            feeder_limit_kw=self.firm_limit_kw,
            loading_pct=loading_pct,
            stress=stress,
            deficit_kw=deficit_kw,
            risk_level=risk_level
        )
    
    def _calculate_risk_level(self, net_demand_kw: float) -> RiskLevel:
        """Determine risk level based on net demand relative to feeder limit."""
        ratio = net_demand_kw / self.firm_limit_kw if self.firm_limit_kw > 0 else 0.0
        
        if ratio >= 1.0:
            return RiskLevel.CRITICAL
        elif ratio >= self.warning_threshold:
            return RiskLevel.WARNING
        elif ratio >= self.watch_threshold:
            return RiskLevel.WATCH
        else:
            return RiskLevel.NORMAL
    
    def calculate_risk_from_forecast(self, forecast_net_demand: np.ndarray) -> list:
        """Calculate risk levels for forecast horizon."""
        risk_levels = []
        for nd in forecast_net_demand:
            risk_levels.append(self._calculate_risk_level(nd))
        return risk_levels
    
    @staticmethod
    def calculate_stress_metrics(net_demand: np.ndarray, 
                                  feeder_limit: float,
                                  dt_hours: float = 0.25) -> dict:
        """Calculate aggregate stress metrics from a time series.
        
        Args:
            net_demand: Array of net demand values (kW)
            feeder_limit: Feeder firm limit (kW)
            dt_hours: Time step duration (hours)
            
        Returns:
            Dictionary of stress metrics
        """
        deficit = np.maximum(0, net_demand - feeder_limit)
        stress_mask = net_demand > feeder_limit
        
        stress_intervals = int(np.sum(stress_mask))
        stress_duration_hours = stress_intervals * dt_hours
        deficit_energy_kwh = float(np.sum(deficit * dt_hours))
        max_deficit_kw = float(np.max(deficit)) if len(deficit) > 0 else 0.0
        avg_deficit_kw = float(np.mean(deficit[stress_mask])) if stress_intervals > 0 else 0.0
        stress_pct = (stress_intervals / len(net_demand)) * 100 if len(net_demand) > 0 else 0.0
        peak_net_demand = float(np.max(net_demand)) if len(net_demand) > 0 else 0.0
        
        return {
            'stress_intervals': stress_intervals,
            'stress_duration_hours': stress_duration_hours,
            'deficit_energy_kwh': deficit_energy_kwh,
            'max_deficit_kw': max_deficit_kw,
            'avg_deficit_kw': avg_deficit_kw,
            'stress_percentage': stress_pct,
            'peak_net_demand_kw': peak_net_demand
        }
