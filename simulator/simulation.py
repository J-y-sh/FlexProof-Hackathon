"""Main simulation runner for FlexProof.

Orchestrates all three scenarios using the same data source.
"""
import time
from typing import Dict, Tuple
from .config import FlexProofConfig, load_config
from .data_sources.synthetic import SyntheticDataSource
from .data_sources.base import DataSource
from .controller import BaselineController, ReactiveController, PredictiveController
from models.schemas import ScenarioResult, ImprovementMetrics


def run_all_scenarios(config: FlexProofConfig, 
                      data_source: DataSource = None) -> Dict[str, ScenarioResult]:
    """Run all three scenarios with the same data.
    
    Args:
        config: Configuration
        data_source: Data source (creates SyntheticDataSource if None)
        
    Returns:
        Dict with 'baseline', 'reactive', 'predictive' ScenarioResults
    """
    if data_source is None:
        data_source = SyntheticDataSource(config)
    
    print("Running Baseline scenario...")
    start = time.time()
    baseline = BaselineController(config).run(data_source)
    print(f"  Baseline complete in {time.time()-start:.1f}s")
    
    print("Running Reactive scenario...")
    start = time.time()
    reactive = ReactiveController(config).run(data_source)
    print(f"  Reactive complete in {time.time()-start:.1f}s")
    
    print("Running Predictive FlexProof scenario...")
    start = time.time()
    predictive = PredictiveController(config).run(data_source)
    print(f"  Predictive complete in {time.time()-start:.1f}s")
    
    return {
        'baseline': baseline,
        'reactive': reactive,
        'predictive': predictive
    }


def calculate_improvements(baseline: ScenarioResult,
                           reactive: ScenarioResult,
                           predictive: ScenarioResult) -> Dict:
    """Calculate improvement metrics between scenarios."""
    def safe_pct(base, controlled):
        if base == 0:
            return 0.0
        return ((base - controlled) / base) * 100
    
    bm = baseline.metrics
    rm = reactive.metrics
    pm = predictive.metrics
    
    reactive_improvement = ImprovementMetrics(
        deficit_reduction_pct=safe_pct(bm.deficit_energy_kwh, rm.deficit_energy_kwh),
        stress_reduction_pct=safe_pct(bm.stress_intervals, rm.stress_intervals),
        max_deficit_reduction_pct=safe_pct(bm.max_deficit_kw, rm.max_deficit_kw),
        peak_demand_reduction_kw=bm.peak_net_demand_kw - rm.peak_net_demand_kw
    )
    
    predictive_improvement = ImprovementMetrics(
        deficit_reduction_pct=safe_pct(bm.deficit_energy_kwh, pm.deficit_energy_kwh),
        stress_reduction_pct=safe_pct(bm.stress_intervals, pm.stress_intervals),
        max_deficit_reduction_pct=safe_pct(bm.max_deficit_kw, pm.max_deficit_kw),
        peak_demand_reduction_kw=bm.peak_net_demand_kw - pm.peak_net_demand_kw,
        predictive_advantage_pct=safe_pct(rm.deficit_energy_kwh, pm.deficit_energy_kwh)
    )
    
    return {
        'reactive': reactive_improvement,
        'predictive': predictive_improvement
    }
