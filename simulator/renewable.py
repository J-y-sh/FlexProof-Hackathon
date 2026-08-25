"""Renewable generation model for FlexProof.

Provides solar generation tracking and surplus calculation.
"""
import numpy as np
import pandas as pd


class RenewableModel:
    """Solar generation model.
    
    Tracks solar generation, calculates surpluses,
    and provides generation forecasting support.
    """
    
    def __init__(self, solar_capacity_kw: float):
        self.solar_capacity_kw = solar_capacity_kw
        self.total_generation_kwh = 0.0
        self.total_surplus_kwh = 0.0
        self.total_curtailed_kwh = 0.0
    
    def calculate_surplus(self, renewable_kw: float, demand_kw: float) -> float:
        """Calculate renewable surplus when generation exceeds demand.
        
        Args:
            renewable_kw: Current renewable generation (kW)
            demand_kw: Current demand (kW)
            
        Returns:
            Surplus power in kW (0 if no surplus)
        """
        return max(0.0, renewable_kw - demand_kw)
    
    def calculate_ramp(self, current_kw: float, previous_kw: float) -> float:
        """Calculate renewable generation ramp rate.
        
        Args:
            current_kw: Current generation (kW)
            previous_kw: Previous interval generation (kW)
            
        Returns:
            Ramp in kW (positive = increasing)
        """
        return current_kw - previous_kw
    
    def update_totals(self, generation_kw: float, surplus_kw: float, 
                      curtailed_kw: float = 0.0, dt_hours: float = 0.25):
        """Update cumulative totals."""
        self.total_generation_kwh += generation_kw * dt_hours
        self.total_surplus_kwh += surplus_kw * dt_hours
        self.total_curtailed_kwh += curtailed_kw * dt_hours
    
    def get_utilization(self) -> float:
        """Calculate renewable utilization percentage."""
        if self.total_generation_kwh == 0:
            return 0.0
        useful = self.total_generation_kwh - self.total_curtailed_kwh
        return (useful / self.total_generation_kwh) * 100
