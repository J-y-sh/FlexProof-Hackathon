from abc import ABC, abstractmethod
import pandas as pd
import numpy as np

class DataSource(ABC):
    """Abstract base class for data sources.
    
    All data sources must provide time-indexed demand and renewable
    generation data at the simulation resolution.
    """
    
    @abstractmethod
    def get_timestamps(self) -> pd.DatetimeIndex:
        """Return the full timestamp index for the simulation."""
        ...
    
    @abstractmethod
    def get_demand(self) -> pd.DataFrame:
        """Return demand data with columns: residential_kw, commercial_kw, industrial_kw, total_kw."""
        ...
    
    @abstractmethod  
    def get_renewable(self) -> pd.DataFrame:
        """Return renewable data with columns: solar_kw, irradiance."""
        ...
    
    @abstractmethod
    def get_flexible_load_profiles(self) -> pd.DataFrame:
        """Return flexible load baseline profiles with columns for each load type."""
        ...
    
    def get_net_demand(self) -> pd.Series:
        """Calculate net demand = total demand - renewable generation."""
        demand = self.get_demand()
        renewable = self.get_renewable()
        return demand['total_kw'] - renewable['solar_kw']
    
    def get_complete_dataset(self) -> pd.DataFrame:
        """Return a unified DataFrame with all data columns."""
        demand = self.get_demand()
        renewable = self.get_renewable()
        flex_loads = self.get_flexible_load_profiles()
        
        df = pd.DataFrame(index=self.get_timestamps())
        df = df.join(demand).join(renewable).join(flex_loads)
        df['net_demand_kw'] = df['total_kw'] - df['solar_kw']
        return df
    
    @property
    @abstractmethod
    def num_intervals(self) -> int:
        ...
    
    @property
    @abstractmethod
    def resolution_minutes(self) -> int:
        ...
