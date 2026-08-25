"""Metrics calculation for FlexProof.

Calculates baseline, reactive, and predictive metrics,
and improvement comparisons.
"""
import numpy as np
import pandas as pd
from typing import Dict
from models.schemas import SimulationMetrics, ScenarioResult, ImprovementMetrics


def calculate_scenario_metrics(df: pd.DataFrame, 
                                feeder_limit_kw: float,
                                dt_hours: float = 0.25,
                                use_controlled: bool = False) -> SimulationMetrics:
    """Calculate metrics from scenario dataframe."""
    if use_controlled and 'controlled_net_demand_kw' in df.columns:
        net_demand = df['controlled_net_demand_kw'].values
    else:
        net_demand = df['net_demand_kw'].values
    
    deficit = np.maximum(0, net_demand - feeder_limit_kw)
    stress_mask = net_demand > feeder_limit_kw
    
    stress_intervals = int(np.sum(stress_mask))
    
    return SimulationMetrics(
        stress_intervals=stress_intervals,
        stress_duration_hours=stress_intervals * dt_hours,
        deficit_energy_kwh=float(np.sum(deficit * dt_hours)),
        max_deficit_kw=float(np.max(deficit)) if len(deficit) > 0 else 0.0,
        avg_deficit_kw=float(np.mean(deficit[stress_mask])) if stress_intervals > 0 else 0.0,
        stress_percentage=(stress_intervals / len(net_demand)) * 100 if len(net_demand) > 0 else 0.0,
        peak_net_demand_kw=float(np.max(net_demand)) if len(net_demand) > 0 else 0.0,
        peak_demand_kw=float(df['demand_kw'].max()) if 'demand_kw' in df.columns else 0.0,
        total_renewable_kwh=float(df['renewable_kw'].sum() * dt_hours) if 'renewable_kw' in df.columns else 0.0
    )


def calculate_improvement_metrics(baseline: SimulationMetrics,
                                   controlled: SimulationMetrics) -> ImprovementMetrics:
    """Calculate improvement of controlled scenario over baseline."""
    def safe_pct(base, ctrl):
        return ((base - ctrl) / base * 100) if base > 0 else 0.0
    
    return ImprovementMetrics(
        deficit_reduction_pct=safe_pct(baseline.deficit_energy_kwh, controlled.deficit_energy_kwh),
        stress_reduction_pct=safe_pct(baseline.stress_intervals, controlled.stress_intervals),
        max_deficit_reduction_pct=safe_pct(baseline.max_deficit_kw, controlled.max_deficit_kw),
        peak_demand_reduction_kw=baseline.peak_net_demand_kw - controlled.peak_net_demand_kw
    )


def calculate_predictive_advantage(reactive: SimulationMetrics,
                                    predictive: SimulationMetrics) -> float:
    """Calculate predictive advantage over reactive."""
    if reactive.deficit_energy_kwh == 0:
        return 0.0
    return ((reactive.deficit_energy_kwh - predictive.deficit_energy_kwh) / 
            reactive.deficit_energy_kwh * 100)


def format_metrics_report(baseline: SimulationMetrics,
                          reactive: SimulationMetrics,
                          predictive: SimulationMetrics) -> str:
    """Format a human-readable metrics report."""
    lines = []
    lines.append("=" * 50)
    lines.append("FLEXPROOF SIMULATION RESULTS")
    lines.append("=" * 50)
    
    for name, m in [('BASELINE', baseline), ('REACTIVE', reactive), ('PREDICTIVE FLEXPROOF', predictive)]:
        lines.append(f"\n--- {name} ---")
        lines.append(f"  Stress intervals:     {m.stress_intervals}")
        lines.append(f"  Stress duration:      {m.stress_duration_hours:.2f} hours")
        lines.append(f"  Deficit energy:       {m.deficit_energy_kwh:.2f} kWh")
        lines.append(f"  Maximum deficit:      {m.max_deficit_kw:.2f} kW")
        lines.append(f"  Peak net demand:      {m.peak_net_demand_kw:.2f} kW")
    
    # Improvements
    lines.append("\n--- IMPROVEMENTS ---")
    
    reactive_imp = calculate_improvement_metrics(baseline, reactive)
    predictive_imp = calculate_improvement_metrics(baseline, predictive)
    pred_adv = calculate_predictive_advantage(reactive, predictive)
    
    lines.append(f"\n  Reactive vs Baseline:")
    lines.append(f"    Deficit reduction:  {reactive_imp.deficit_reduction_pct:.2f}%")
    lines.append(f"    Stress reduction:   {reactive_imp.stress_reduction_pct:.2f}%")
    
    lines.append(f"\n  Predictive vs Baseline:")
    lines.append(f"    Deficit reduction:  {predictive_imp.deficit_reduction_pct:.2f}%")
    lines.append(f"    Stress reduction:   {predictive_imp.stress_reduction_pct:.2f}%")
    
    lines.append(f"\n  Predictive Advantage:")
    lines.append(f"    Additional reduction: {pred_adv:.2f}%")
    
    lines.append("\n" + "=" * 50)
    
    return "\n".join(lines)
