"""FlexProof CLI simulation runner.

Runs Baseline, Reactive, and Predictive FlexProof scenarios,
calculates comparative improvements, exports interval-level data
and control events to CSV, and prints a comprehensive execution summary.
"""
import sys
from pathlib import Path
from simulator.config import load_config
from simulator.simulation import run_all_scenarios, calculate_improvements
from simulator.metrics import format_metrics_report
from simulator.reporting import export_all_scenarios, export_events_csv


def main():
    print("=" * 60)
    print("       FLEXPROOF — NEIGHBOURHOOD GRID FLEXIBILITY PLATFORM")
    print("=" * 60)
    
    config = load_config("config.yaml")
    print(f"Loaded config: {config.simulation.duration_days} days | "
          f"{config.simulation.intervals} intervals | "
          f"{config.feeder.firm_limit_kw} kW feeder limit\n")
    
    # Run simulation
    results = run_all_scenarios(config)
    
    # Calculate improvements
    improvements = calculate_improvements(
        results['baseline'], results['reactive'], results['predictive']
    )
    
    # Print metrics report
    report = format_metrics_report(
        results['baseline'].metrics,
        results['reactive'].metrics,
        results['predictive'].metrics
    )
    print(report)
    
    # Export CSVs
    output_dir = "data/processed"
    print(f"\nExporting scenario data to {output_dir}...")
    export_all_scenarios(results, output_dir)
    export_events_csv(results, output_dir)
    print("Data export complete.\n")
    
    print("=" * 60)
    print("SIMULATION RUN COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
