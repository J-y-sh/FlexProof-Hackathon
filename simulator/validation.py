"""Validation engine for FlexProof.

Checks critical invariants in simulation results.
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from models.schemas import ScenarioResult


class ValidationError:
    def __init__(self, check: str, message: str, severity: str = 'ERROR'):
        self.check = check
        self.message = message
        self.severity = severity
    
    def __str__(self):
        return f"[{self.severity}] {self.check}: {self.message}"


def validate_scenario(result: ScenarioResult, config) -> List[ValidationError]:
    """Validate a single scenario result."""
    errors = []
    df = result.dataframe
    
    # Check interval count
    expected = config.simulation.intervals
    actual = len(df)
    if actual != expected:
        errors.append(ValidationError(
            'interval_count',
            f"Expected {expected} intervals, got {actual}"
        ))
    
    # Check for NaN
    nan_cols = df.columns[df.isna().any()].tolist()
    if nan_cols:
        errors.append(ValidationError(
            'no_nan',
            f"NaN found in columns: {nan_cols}"
        ))
    
    # Check renewable non-negative
    if 'renewable_kw' in df.columns:
        min_renewable = df['renewable_kw'].min()
        if min_renewable < -0.01:  # Small tolerance for float
            errors.append(ValidationError(
                'renewable_non_negative',
                f"Negative renewable generation: {min_renewable:.4f} kW"
            ))
    
    # Check deficit non-negative
    if 'deficit_kw' in df.columns:
        min_deficit = df['deficit_kw'].min()
        if min_deficit < -0.01:
            errors.append(ValidationError(
                'deficit_non_negative',
                f"Negative deficit: {min_deficit:.4f} kW"
            ))
    
    # Check battery SOC limits
    if 'battery_soc' in df.columns:
        min_soc = df['battery_soc'].min()
        max_soc = df['battery_soc'].max()
        if min_soc < config.battery.min_soc - 0.001:
            errors.append(ValidationError(
                'battery_min_soc',
                f"Battery SOC below minimum: {min_soc:.4f} < {config.battery.min_soc}"
            ))
        if max_soc > config.battery.max_soc + 0.001:
            errors.append(ValidationError(
                'battery_max_soc',
                f"Battery SOC above maximum: {max_soc:.4f} > {config.battery.max_soc}"
            ))
    
    # Check for infinity
    inf_cols = []
    for col in df.select_dtypes(include=[np.number]).columns:
        if np.any(np.isinf(df[col].values)):
            inf_cols.append(col)
    if inf_cols:
        errors.append(ValidationError(
            'no_infinity',
            f"Infinity found in columns: {inf_cols}"
        ))
    
    return errors


def validate_scenario_integrity(results: Dict[str, ScenarioResult]) -> List[ValidationError]:
    """Verify all scenarios use identical input data."""
    errors = []
    
    names = list(results.keys())
    if len(names) < 2:
        return errors
    
    base_df = results[names[0]].dataframe
    
    for name in names[1:]:
        other_df = results[name].dataframe
        
        # Check demand matches
        if 'demand_kw' in base_df.columns and 'demand_kw' in other_df.columns:
            if not np.allclose(base_df['demand_kw'].values, other_df['demand_kw'].values, atol=0.01):
                errors.append(ValidationError(
                    'scenario_integrity',
                    f"Demand mismatch between {names[0]} and {name}"
                ))
        
        # Check renewable matches
        if 'renewable_kw' in base_df.columns and 'renewable_kw' in other_df.columns:
            if not np.allclose(base_df['renewable_kw'].values, other_df['renewable_kw'].values, atol=0.01):
                errors.append(ValidationError(
                    'scenario_integrity',
                    f"Renewable mismatch between {names[0]} and {name}"
                ))
    
    # Check predictive deficit <= baseline deficit
    if 'baseline' in results and 'predictive' in results:
        b_deficit = results['baseline'].metrics.deficit_energy_kwh
        p_deficit = results['predictive'].metrics.deficit_energy_kwh
        if p_deficit > b_deficit * 1.01:  # 1% tolerance
            errors.append(ValidationError(
                'deficit_ordering',
                f"Predictive deficit ({p_deficit:.2f}) > baseline ({b_deficit:.2f})",
                'WARNING'
            ))
    
    if 'baseline' in results and 'reactive' in results:
        b_deficit = results['baseline'].metrics.deficit_energy_kwh
        r_deficit = results['reactive'].metrics.deficit_energy_kwh
        if r_deficit > b_deficit * 1.01:
            errors.append(ValidationError(
                'deficit_ordering',
                f"Reactive deficit ({r_deficit:.2f}) > baseline ({b_deficit:.2f})",
                'WARNING'
            ))
    
    return errors


def run_full_validation(results: Dict[str, ScenarioResult], config) -> Tuple[bool, str]:
    """Run complete validation and return (pass, report)."""
    all_errors = []
    
    for name, result in results.items():
        scenario_errors = validate_scenario(result, config)
        for e in scenario_errors:
            e.check = f"{name}.{e.check}"
            all_errors.append(e)
    
    integrity_errors = validate_scenario_integrity(results)
    all_errors.extend(integrity_errors)
    
    # Build report
    lines = []
    lines.append("=" * 50)
    lines.append("FLEXPROOF VALIDATION REPORT")
    lines.append("=" * 50)
    
    critical_errors = [e for e in all_errors if e.severity == 'ERROR']
    warnings = [e for e in all_errors if e.severity == 'WARNING']
    
    if not all_errors:
        lines.append("\nAll validation checks PASSED")
    else:
        if critical_errors:
            lines.append(f"\nERRORS ({len(critical_errors)}):")
            for e in critical_errors:
                lines.append(f"  {e}")
        if warnings:
            lines.append(f"\nWARNINGS ({len(warnings)}):")
            for e in warnings:
                lines.append(f"  {e}")
    
    lines.append("\n" + "=" * 50)
    
    passed = len(critical_errors) == 0
    return passed, "\n".join(lines)
