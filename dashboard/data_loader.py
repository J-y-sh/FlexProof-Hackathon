"""Data loader and metrics processing for FlexProof Streamlit dashboard.

Loads processed simulation scenarios and event logs, computes dynamic
metrics without hardcoding, and caches data for fast dashboard rendering.
"""
from pathlib import Path
from typing import Dict, Tuple, Optional
import pandas as pd
import numpy as np
import streamlit as st

from simulator.config import load_config, FlexProofConfig


@st.cache_data(show_spinner=False)
def load_configuration(config_path: str = "config.yaml") -> FlexProofConfig:
    """Load and cache the global FlexProof configuration."""
    return load_config(config_path)


@st.cache_data(show_spinner=False)
def load_scenario_data(data_dir: str = "data/processed") -> Dict[str, pd.DataFrame]:
    """Load scenario dataframes from processed CSV files.

    Returns:
        Dict with keys 'baseline', 'reactive', 'predictive'
    """
    path = Path(data_dir)
    scenarios = {}

    for name in ['baseline', 'reactive', 'predictive']:
        csv_file = path / f"{name}.csv"
        if not csv_file.exists():
            raise FileNotFoundError(
                f"Missing processed data file: {csv_file}. "
                f"Please run 'python run.py' first to generate scenario data."
            )
        df = pd.read_csv(csv_file, parse_dates=['timestamp'])
        df.set_index('timestamp', inplace=True)
        scenarios[name] = df

    return scenarios


@st.cache_data(show_spinner=False)
def load_event_data(data_dir: str = "data/processed") -> Dict[str, pd.DataFrame]:
    """Load controller event logs from processed CSV files.

    Returns:
        Dict with keys 'reactive', 'predictive'
    """
    path = Path(data_dir)
    events = {}

    for name in ['reactive', 'predictive']:
        csv_file = path / f"{name}_events.csv"
        if csv_file.exists():
            df = pd.read_csv(csv_file, parse_dates=['timestamp'])
            events[name] = df
        else:
            events[name] = pd.DataFrame()

    return events


@st.cache_data(show_spinner=False)
def load_all_data(data_dir: str = "data/processed") -> Tuple[Dict[str, pd.DataFrame], Dict[str, pd.DataFrame]]:
    """Load both scenario time series and controller events."""
    scenarios = load_scenario_data(data_dir)
    events = load_event_data(data_dir)
    return scenarios, events


def compute_scenario_metrics(df: pd.DataFrame,
                             firm_limit_kw: float = 2300.0,
                             dt_hours: float = 0.25) -> Dict[str, float]:
    """Dynamically compute key performance indicators from a scenario dataframe."""
    controlled_nd = df['controlled_net_demand_kw'].values if 'controlled_net_demand_kw' in df.columns else df['net_demand_kw'].values
    raw_nd = df['net_demand_kw'].values

    deficit = np.maximum(0.0, controlled_nd - firm_limit_kw)
    stress_mask = controlled_nd > firm_limit_kw
    stress_count = int(np.sum(stress_mask))

    # Battery metrics
    soc_values = df['battery_soc'].values if 'battery_soc' in df.columns else np.array([0.7])
    min_soc = float(np.min(soc_values))
    max_soc = float(np.max(soc_values))

    # Battery throughput: sum of absolute SOC changes converted to kWh
    if 'battery_soc' in df.columns and len(df) > 1:
        soc_diffs = np.abs(np.diff(soc_values))
        # 500 kWh capacity nominal
        throughput_kwh = float(np.sum(soc_diffs) * 500.0)
    else:
        throughput_kwh = 0.0

    # Flexibility metrics
    flex_disp = df['flexibility_dispatched_kw'].values if 'flexibility_dispatched_kw' in df.columns else np.zeros(len(df))
    shifted_energy_kwh = float(np.sum(flex_disp) * dt_hours)

    # Forecast errors if available
    if 'forecast_net_demand_kw' in df.columns and np.any(df['forecast_net_demand_kw'] > 0):
        valid_fc = df['forecast_net_demand_kw'] > 0
        fc_errors = np.abs(df.loc[valid_fc, 'forecast_net_demand_kw'] - df.loc[valid_fc, 'net_demand_kw'])
        mae = float(fc_errors.mean()) if len(fc_errors) > 0 else 0.0
        rmse = float(np.sqrt((fc_errors**2).mean())) if len(fc_errors) > 0 else 0.0
    else:
        mae = 0.0
        rmse = 0.0

    return {
        'stress_intervals': stress_count,
        'stress_duration_hours': stress_count * dt_hours,
        'deficit_energy_kwh': float(np.sum(deficit * dt_hours)),
        'max_deficit_kw': float(np.max(deficit)) if len(deficit) > 0 else 0.0,
        'peak_net_demand_kw': float(np.max(controlled_nd)) if len(controlled_nd) > 0 else 0.0,
        'peak_demand_kw': float(df['demand_kw'].max()) if 'demand_kw' in df.columns else 0.0,
        'total_renewable_kwh': float(df['renewable_kw'].sum() * dt_hours) if 'renewable_kw' in df.columns else 0.0,
        'battery_throughput_kwh': throughput_kwh,
        'shifted_energy_kwh': shifted_energy_kwh,
        'min_battery_soc': min_soc,
        'max_battery_soc': max_soc,
        'forecast_mae': mae,
        'forecast_rmse': rmse,
    }


def compute_comparative_summary(scenarios: Dict[str, pd.DataFrame],
                                firm_limit_kw: float = 2300.0,
                                dt_hours: float = 0.25) -> Dict[str, Dict]:
    """Compute metrics for all scenarios and derive relative percentage improvements."""
    summary = {}
    for name in ['baseline', 'reactive', 'predictive']:
        if name in scenarios:
            summary[name] = compute_scenario_metrics(scenarios[name], firm_limit_kw, dt_hours)

    # Compute relative improvements
    if 'baseline' in summary and 'reactive' in summary and 'predictive' in summary:
        b = summary['baseline']
        r = summary['reactive']
        p = summary['predictive']

        def pct_red(base_val, new_val):
            return ((base_val - new_val) / base_val * 100) if base_val > 0 else 0.0

        summary['improvements'] = {
            'reactive_deficit_reduction_pct': pct_red(b['deficit_energy_kwh'], r['deficit_energy_kwh']),
            'reactive_stress_reduction_pct': pct_red(b['stress_intervals'], r['stress_intervals']),
            'predictive_deficit_reduction_pct': pct_red(b['deficit_energy_kwh'], p['deficit_energy_kwh']),
            'predictive_stress_reduction_pct': pct_red(b['stress_intervals'], p['stress_intervals']),
            'predictive_advantage_pct': pct_red(r['deficit_energy_kwh'], p['deficit_energy_kwh']),
            'battery_throughput_reduction_pct': pct_red(r['battery_throughput_kwh'], p['battery_throughput_kwh']),
            'peak_shaving_reactive_kw': b['peak_net_demand_kw'] - r['peak_net_demand_kw'],
            'peak_shaving_predictive_kw': b['peak_net_demand_kw'] - p['peak_net_demand_kw'],
        }

    return summary
