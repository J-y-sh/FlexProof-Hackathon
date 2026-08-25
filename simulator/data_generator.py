"""Data generator module - convenience wrapper around SyntheticDataSource."""
import pandas as pd
from pathlib import Path
from .data_sources.synthetic import SyntheticDataSource
from .config import FlexProofConfig

def generate_data(config: FlexProofConfig) -> SyntheticDataSource:
    """Generate synthetic data and return the data source."""
    return SyntheticDataSource(config)

def export_raw_data(data_source: SyntheticDataSource, output_dir: str) -> None:
    """Export raw generated data to CSV files."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    demand = data_source.get_demand()
    demand.index.name = 'timestamp'
    demand.to_csv(output_path / 'demand.csv')
    
    renewable = data_source.get_renewable()
    renewable.index.name = 'timestamp'
    renewable.to_csv(output_path / 'renewable.csv')
    
    flex = data_source.get_flexible_load_profiles()
    flex.index.name = 'timestamp'
    flex.to_csv(output_path / 'flexible_loads.csv')
    
    print(f"Raw data exported to {output_path}")
