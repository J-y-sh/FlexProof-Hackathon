"""Feeder stress prediction engine for FlexProof.

Analyzes forecast data to predict upcoming feeder stress,
assign risk levels, and calculate required flexibility.
"""
import numpy as np
from typing import List, Tuple, Dict
from models.schemas import RiskLevel, ForecastResult


class StressPredictionEngine:
    """Predicts feeder stress from forecast data.
    
    For each future interval in the forecast horizon:
    1. Calculate forecast net demand
    2. Compare to feeder limit
    3. Determine forecast gap
    4. Assign risk level
    5. Estimate required flexibility
    """
    
    def __init__(self, feeder_limit_kw: float,
                 watch_threshold: float = 0.75,
                 warning_threshold: float = 0.85,
                 critical_threshold: float = 0.95):
        self.feeder_limit_kw = feeder_limit_kw
        self.watch_threshold = watch_threshold
        self.warning_threshold = warning_threshold
        self.critical_threshold = critical_threshold
    
    def predict_stress(self, forecast: ForecastResult) -> Dict:
        """Analyze forecast and predict stress events.
        
        Args:
            forecast: ForecastResult from forecasting engine
            
        Returns:
            Dictionary with stress prediction details
        """
        horizon = forecast.horizon_intervals
        risk_levels = []
        gaps = []
        required_flexibility = []
        
        for i in range(horizon):
            nd = forecast.forecast_net_demand_kw[i]
            ratio = nd / self.feeder_limit_kw if self.feeder_limit_kw > 0 else 0
            
            # Determine risk level
            if ratio >= 1.0:
                risk_levels.append(RiskLevel.CRITICAL)
            elif ratio >= self.warning_threshold:
                risk_levels.append(RiskLevel.WARNING)
            elif ratio >= self.watch_threshold:
                risk_levels.append(RiskLevel.WATCH)
            else:
                risk_levels.append(RiskLevel.NORMAL)
            
            # Gap and flexibility
            gap = max(0.0, nd - self.feeder_limit_kw)
            gaps.append(gap)
            
            # Required flexibility includes margin
            margin = gap * 0.1 if gap > 0 else 0  # 10% margin
            required_flexibility.append(gap + margin)
        
        # Aggregate assessment
        max_gap = max(gaps) if gaps else 0
        max_risk = self._worst_risk(risk_levels)
        stress_predicted = any(r in (RiskLevel.WARNING, RiskLevel.CRITICAL) for r in risk_levels)
        critical_predicted = any(r == RiskLevel.CRITICAL for r in risk_levels)
        
        # Time to stress (intervals until first WARNING or CRITICAL)
        time_to_stress = horizon  # No stress predicted
        for i, r in enumerate(risk_levels):
            if r in (RiskLevel.WARNING, RiskLevel.CRITICAL):
                time_to_stress = i
                break
        
        return {
            'risk_levels': risk_levels,
            'gaps_kw': gaps,
            'required_flexibility_kw': required_flexibility,
            'max_gap_kw': max_gap,
            'max_risk': max_risk,
            'stress_predicted': stress_predicted,
            'critical_predicted': critical_predicted,
            'time_to_stress_intervals': time_to_stress,
            'total_gap_kwh': sum(g * 0.25 for g in gaps),
            'max_required_flexibility_kw': max(required_flexibility) if required_flexibility else 0,
        }
    
    def _worst_risk(self, levels: List[RiskLevel]) -> RiskLevel:
        """Return the worst (highest severity) risk level."""
        order = {
            RiskLevel.NORMAL: 0,
            RiskLevel.WATCH: 1,
            RiskLevel.WARNING: 2,
            RiskLevel.CRITICAL: 3
        }
        if not levels:
            return RiskLevel.NORMAL
        return max(levels, key=lambda l: order.get(l, 0))
    
    def calculate_current_risk(self, net_demand_kw: float) -> RiskLevel:
        """Calculate risk level for current interval."""
        ratio = net_demand_kw / self.feeder_limit_kw if self.feeder_limit_kw > 0 else 0
        
        if ratio >= 1.0:
            return RiskLevel.CRITICAL
        elif ratio >= self.warning_threshold:
            return RiskLevel.WARNING
        elif ratio >= self.watch_threshold:
            return RiskLevel.WATCH
        else:
            return RiskLevel.NORMAL
    
    def is_stress(self, net_demand_kw: float) -> bool:
        """Check if current interval is under stress."""
        return net_demand_kw > self.feeder_limit_kw
    
    def calculate_deficit(self, net_demand_kw: float) -> float:
        """Calculate current deficit (kW)."""
        return max(0.0, net_demand_kw - self.feeder_limit_kw)
