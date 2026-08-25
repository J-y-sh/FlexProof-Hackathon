"""Reporting and data export for FlexProof."""
import pandas as pd
from pathlib import Path
from typing import Dict
from models.schemas import ScenarioResult


def export_scenario_csv(result: ScenarioResult, output_path: str) -> str:
    """Export scenario results to CSV."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    result.dataframe.to_csv(path)
    return str(path)


def export_all_scenarios(results: Dict[str, ScenarioResult], 
                          output_dir: str) -> Dict[str, str]:
    """Export all scenario results to CSV files."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    paths = {}
    for name, result in results.items():
        filename = f"{name}.csv"
        filepath = output_path / filename
        result.dataframe.to_csv(filepath)
        paths[name] = str(filepath)
        print(f"  Exported {name} to {filepath}")
    
    return paths


def export_events_csv(results: Dict[str, ScenarioResult],
                       output_dir: str) -> None:
    """Export controller events to CSV."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    for name, result in results.items():
        if result.controller_events:
            events_data = []
            for e in result.controller_events:
                events_data.append({
                    'timestamp': e.timestamp,
                    'decision': e.decision,
                    'reason': e.reason,
                    'predicted_gap_kw': e.predicted_gap_kw,
                    'required_flexibility_kw': e.required_flexibility_kw,
                    'resource_selected': e.resource_selected,
                    'power_requested_kw': e.power_requested_kw,
                    'power_delivered_kw': e.power_delivered_kw,
                    'battery_soc_before': e.battery_soc_before,
                    'battery_soc_after': e.battery_soc_after
                })
            df = pd.DataFrame(events_data)
            filepath = output_path / f"{name}_events.csv"
            df.to_csv(filepath, index=False)
            print(f"  Exported {name} events to {filepath}")
