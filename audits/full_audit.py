"""Audit: No look-ahead leakage validation."""
from simulator.config import load_config
from simulator.simulation import run_all_scenarios
import pandas as pd
import numpy as np

cfg = load_config('config.yaml')
results = run_all_scenarios(cfg)

b_df = results['baseline'].dataframe
r_df = results['reactive'].dataframe
p_df = results['predictive'].dataframe

# -----------------------------------------------------------------------
# AUDIT 1: No look-ahead leakage
# The forecaster only receives demand_values[i - lookback:i] (strictly past).
# Forecast values should NOT match exact future actuals.
# -----------------------------------------------------------------------
p_stress_fc = p_df[p_df['forecast_gap_kw'] > 0]
print(f'Intervals with non-zero forecast gap: {len(p_stress_fc)}')

violations = 0
for ts, row in list(p_stress_fc.iterrows())[:30]:
    ts_int = p_df.index.get_loc(ts)
    fc_nd = row['forecast_net_demand_kw']

    for ahead in [1, 2, 3, 4]:
        if ts_int + ahead < len(b_df):
            actual_future_nd = b_df.iloc[ts_int + ahead]['net_demand_kw']
            if abs(fc_nd - actual_future_nd) < 0.001:
                violations += 1
                print(f'  LEAKAGE: {ts} forecast_net={fc_nd:.2f} == actual+{ahead}i={actual_future_nd:.2f}')

if violations == 0:
    print('PASS: No look-ahead leakage detected (forecast values differ from future actuals)')

# -----------------------------------------------------------------------
# AUDIT 2: Forecast error confirms imperfect prediction (not cheating)
# -----------------------------------------------------------------------
p_fc_err = (p_df['forecast_net_demand_kw'] - p_df['net_demand_kw']).abs()
print()
print('Forecast error stats (forecast_net vs current_net_demand at same interval):')
print(f'  Mean absolute error: {p_fc_err.mean():.1f} kW')
print(f'  Max absolute error:  {p_fc_err.max():.1f} kW')
print(f'  Median absolute error: {p_fc_err.median():.1f} kW')

# -----------------------------------------------------------------------
# AUDIT 3: Verify lookback boundary
# -----------------------------------------------------------------------
print()
print('Lookback boundary check:')
fc_gap_95 = p_df.iloc[95]['forecast_gap_kw']
fc_gap_96 = p_df.iloc[96]['forecast_gap_kw']
print(f'  interval 95 (before lookback): forecast_gap = {fc_gap_95:.2f} (should be 0)')
print(f'  interval 96 (at lookback):     forecast_gap = {fc_gap_96:.2f}')
if fc_gap_95 == 0.0:
    print('  PASS: No forecast before sufficient history')

# -----------------------------------------------------------------------
# AUDIT 4: Reactive controller does NOT use forecast
# -----------------------------------------------------------------------
print()
print('Reactive controller forecast usage:')
r_fc_gap_nonzero = (r_df['forecast_gap_kw'] != 0).sum()
print(f'  Non-zero forecast_gap in reactive: {r_fc_gap_nonzero} (should be 0)')
if r_fc_gap_nonzero == 0:
    print('  PASS: Reactive never uses forecast (all forecast_gap == 0)')

# -----------------------------------------------------------------------
# AUDIT 5: Baseline does NOT dispatch
# -----------------------------------------------------------------------
print()
print('Baseline controller flexibility check:')
b_dispatched = b_df['flexibility_dispatched_kw'].sum()
b_bat_var = b_df['battery_soc'].std()
print(f'  Total flexibility dispatched: {b_dispatched:.2f} kW-intervals (should be 0)')
print(f'  Battery SOC std dev: {b_bat_var:.6f} (should be 0 - no changes)')
if b_dispatched == 0 and b_bat_var == 0:
    print('  PASS: Baseline has zero dispatch and constant battery SOC')

# -----------------------------------------------------------------------
# AUDIT 6: Response time delay enforcement
# -----------------------------------------------------------------------
print()
print('Response time delay enforcement audit:')
from simulator.data_sources.synthetic import SyntheticDataSource
from simulator.flexible_loads import FlexibleLoadManager

ds = SyntheticDataSource(cfg)
flex_mgr = FlexibleLoadManager(cfg.flexible_loads)

# Shift HVAC (response_time=1) at interval 10
hvac_res = [r for r in flex_mgr.resources if 'hvac' in r.resource_id][0]
print(f'  HVAC response_time_intervals: {hvac_res.response_time}')

# Trigger a shift at interval 10
flex_mgr.shift_load(30.0, 10, duration_intervals=4)

# Check reduction at interval 10 (before response time)
red_at_10 = flex_mgr.get_active_reduction(10)
# Check reduction at interval 11 (after response time=1)
red_at_11 = flex_mgr.get_active_reduction(11)

print(f'  Reduction at interval 10 (same as shift start, response_time=1): {red_at_10:.1f} kW (expected 0)')
print(f'  Reduction at interval 11 (after 1 interval lag): {red_at_11:.1f} kW (expected >0)')

if red_at_10 == 0.0 and red_at_11 > 0:
    print('  PASS: Response time delay is enforced correctly')
else:
    print('  FAIL: Response time delay not enforced')

# EV charging (response_time=1)  
flex_mgr2 = FlexibleLoadManager(cfg.flexible_loads)
ev_res = [r for r in flex_mgr2.resources if 'ev' in r.resource_id][0]
print(f'  EV response_time_intervals: {ev_res.response_time}')

# Water pumping (response_time=2)
wp_res = [r for r in flex_mgr2.resources if 'water' in r.resource_id][0]
print(f'  Water pumping response_time_intervals: {wp_res.response_time}')

flex_mgr2.shift_load(200.0, 10, duration_intervals=8)  # Will use all resources

wp_red_10 = flex_mgr2.get_active_reduction(10)   # Before any response time
wp_red_11 = flex_mgr2.get_active_reduction(11)   # After 1 interval (only resp_time=1 active)
wp_red_12 = flex_mgr2.get_active_reduction(12)   # After 2 intervals (resp_time=2 also active)

print(f'  200kW shift at t=10: reduction at t=10={wp_red_10:.1f}, t=11={wp_red_11:.1f}, t=12={wp_red_12:.1f}')
print(f'  (Water pumping power = {wp_res.available_power_kw:.1f} kW, resp_time=2 means it only activates at t=12)')