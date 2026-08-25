import pandas as pd
import numpy as np
from pathlib import Path
from .base import DataSource

class CSVDataSource(DataSource):
    """Data source that reads from CSV files.
    
    Expected files in the data directory:
    - demand.csv: columns [timestamp, residential_kw, commercial_kw, industrial_kw, total_kw]
    - renewable.csv: columns [timestamp, solar_kw, irradiance]
    - flexible_loads.csv: columns [timestamp, ev_charging_kw, water_pumping_kw, hvac_kw, ...]
    """
    
    def __init__(self, data_dir: str, resolution_minutes: int = 15):
        self._data_dir = Path(data_dir)
        self._resolution_minutes = resolution_minutes
        self._demand = None
        self._renewable = None
        self._flex_profiles = None
        self._timestamps = None
        self._load_data()
    
    def _load_data(self):
        """Load data from CSV files."""
        demand_path = self._data_dir / 'demand.csv'
        renewable_path = self._data_dir / 'renewable.csv'
        flex_path = self._data_dir / 'flexible_loads.csv'
        
        if demand_path.exists():
            self._demand = pd.read_csv(demand_path, parse_dates=['timestamp'], index_col='timestamp')
        else:
            raise FileNotFoundError(f"Demand data not found: {demand_path}")
        
        if renewable_path.exists():
            self._renewable = pd.read_csv(renewable_path, parse_dates=['timestamp'], index_col='timestamp')
        else:
            raise FileNotFoundError(f"Renewable data not found: {renewable_path}")
        
        if flex_path.exists():
            self._flex_profiles = pd.read_csv(flex_path, parse_dates=['timestamp'], index_col='timestamp')
        else:
            # Generate zero profiles if not available
            self._flex_profiles = pd.DataFrame(
                0.0, index=self._demand.index,
                columns=['ev_charging_kw', 'water_pumping_kw', 'hvac_kw', 
                         'commercial_refrigeration_kw', 'agricultural_pumping_kw']
            )
        
        self._timestamps = self._demand.index
    
    def get_timestamps(self) -> pd.DatetimeIndex:
        return self._timestamps
    
    def get_demand(self) -> pd.DataFrame:
        return self._demand.copy()
    
    def get_renewable(self) -> pd.DataFrame:
        return self._renewable.copy()
    
    def get_flexible_load_profiles(self) -> pd.DataFrame:
        return self._flex_profiles.copy()
    
    @property
    def num_intervals(self) -> int:
        return len(self._timestamps)
    
    @property
    def resolution_minutes(self) -> int:
        return self._resolution_minutes
