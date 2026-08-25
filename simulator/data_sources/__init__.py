"""Data source abstraction for FlexProof."""
from .base import DataSource
from .synthetic import SyntheticDataSource
from .csv_source import CSVDataSource

__all__ = ["DataSource", "SyntheticDataSource", "CSVDataSource"]
