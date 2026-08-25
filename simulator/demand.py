"""Demand model for FlexProof.

Provides demand decomposition and analysis.
"""
import numpy as np
import pandas as pd


class DemandModel:
    """Demand tracking and analysis model.
    
    Tracks residential, commercial, and industrial demand.
    Provides peak detection and pattern analysis.
    """
    
    def __init__(self, residential_peak_kw: float = 1200,
                 commercial_peak_kw: float = 600,
                 industrial_peak_kw: float = 400):
        self.residential_peak_kw = residential_peak_kw
        self.commercial_peak_kw = commercial_peak_kw
        self.industrial_peak_kw = industrial_peak_kw
        self.total_peak_kw = residential_peak_kw + commercial_peak_kw + industrial_peak_kw
    
    @staticmethod
    def calculate_total(residential_kw: float, commercial_kw: float, 
                        industrial_kw: float) -> float:
        """Calculate total demand from components."""
        return residential_kw + commercial_kw + industrial_kw
    
    @staticmethod
    def detect_peak_periods(demand_series: pd.Series, 
                            threshold_pct: float = 0.85) -> pd.Series:
        """Identify peak demand periods.
        
        Args:
            demand_series: Time-indexed demand series (kW)
            threshold_pct: Fraction of max to consider 'peak'
            
        Returns:
            Boolean series marking peak periods
        """
        max_demand = demand_series.max()
        return demand_series > (max_demand * threshold_pct)
    
    @staticmethod  
    def calculate_demand_stats(demand_series: pd.Series, 
                                dt_hours: float = 0.25) -> dict:
        """Calculate demand statistics."""
        return {
            'peak_demand_kw': float(demand_series.max()),
            'min_demand_kw': float(demand_series.min()),
            'mean_demand_kw': float(demand_series.mean()),
            'total_energy_kwh': float(demand_series.sum() * dt_hours),
            'load_factor': float(demand_series.mean() / demand_series.max()) if demand_series.max() > 0 else 0.0
        }
