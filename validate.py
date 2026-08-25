"""FlexProof validation entrypoint.

Executes the full simulation suite across Baseline, Reactive, and Predictive scenarios,
checks all physical invariants, constraints, and scenario integrity, and returns exit code 0
on success or non-zero on failure.
"""
import sys
from simulator.config import load_config
from simulator.simulation import run_all_scenarios, calculate_improvements
from simulator.metrics import format_metrics_report
from simulator.validation import run_full_validation


def main():
    print("=== FLEXPROOF VALIDATION ===")
    print("Loading configuration...")
    config = load_config("config.yaml")
    
    print(f"Simulation: {config.simulation.duration_days} days, "
          f"{config.simulation.intervals} intervals, "
          f"{config.simulation.resolution_minutes}-minute resolution")
    print(f"Feeder firm limit: {config.feeder.firm_limit_kw:.1f} kW\n")
    
    # Run all scenarios
    results = run_all_scenarios(config)
    
    # Print metrics report
    report = format_metrics_report(
        results['baseline'].metrics,
        results['reactive'].metrics,
        results['predictive'].metrics
    )
    print(report)
    
    # Run validation checks
    passed, val_report = run_full_validation(results, config)
    print(val_report)
    
    if passed:
        print("\n[SUCCESS] All validation invariants passed successfully.")
        sys.exit(0)
    else:
        print("\n[FAILURE] Validation checks failed. Inspect errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
