import numpy as np
import pandas as pd
from simulator.config import load_config
from simulator.simulation import run_all_scenarios

cfg = load_config('config.yaml')
results = run_all_scenarios(cfg)

b_df = results['baseline'].dataframe
r_df = results['reactive'].dataframe
p_df = results['predictive'].dataframe

ts = pd.Timestamp('2024-01-12 18:00:00')

print('Deep trace for 2024-01-12 17:00 to 19:30:')
hdr = f"{'Time':20} {'BaseND':8} {'RND':8} {'RBat':6} {'RDisp':8} {'PND':8} {'PBat':6} {'PfcGap':8} {'PDisp':8}"
print(hdr)

for h_off in range(-8, 8):
    dt = pd.Timedelta(minutes=15 * h_off)
    check_ts = ts + dt
    if check_ts in b_df.index:
        b_nd = b_df.loc[check_ts, 'net_demand_kw']
        r_nd = r_df.loc[check_ts, 'controlled_net_demand_kw']
        r_bat = r_df.loc[check_ts, 'battery_soc']
        r_disp = r_df.loc[check_ts, 'flexibility_dispatched_kw']
        p_nd = p_df.loc[check_ts, 'controlled_net_demand_kw']
        p_bat = p_df.loc[check_ts, 'battery_soc']
        p_fg = p_df.loc[check_ts, 'forecast_gap_kw']
        p_disp = p_df.loc[check_ts, 'flexibility_dispatched_kw']
        
        marker = ''
        if r_nd > 2300:
            marker += ' <R-STRESS'
        if p_nd > 2300:
            marker += ' <P-STRESS'
        
        row = f"{str(check_ts):20} {b_nd:8.1f} {r_nd:8.1f} {r_bat:6.3f} {r_disp:8.1f} {p_nd:8.1f} {p_bat:6.3f} {p_fg:8.1f} {p_disp:8.1f}{marker}"
        print(row)

# Also check Jan 12 18:00 — why did reactive fail?
print()
print("--- Jan 12 18:00 detailed analysis ---")
r_row = r_df.loc[ts]
b_row = b_df.loc[ts]
p_row = p_df.loc[ts]

print(f"Baseline net demand: {b_row['net_demand_kw']:.1f} kW (deficit = {max(0, b_row['net_demand_kw'] - 2300):.1f} kW)")
print(f"Reactive net demand: {r_row['controlled_net_demand_kw']:.1f} kW")
print(f"  Battery SOC: {r_row['battery_soc']:.3f}")
print(f"  Battery action: {r_row['battery_action']}")
print(f"  Flex dispatched: {r_row['flexibility_dispatched_kw']:.1f} kW")

print(f"Predictive net demand: {p_row['controlled_net_demand_kw']:.1f} kW")
print(f"  Battery SOC: {p_row['battery_soc']:.3f}")
print(f"  Battery action: {p_row['battery_action']}")
print(f"  Flex dispatched: {p_row['flexibility_dispatched_kw']:.1f} kW")
print(f"  Forecast gap: {p_row['forecast_gap_kw']:.1f} kW")

print()
print("--- Checking why reactive still shows stress at 18:00 ---")
# What is reactive's battery discharge cap?
react_max = cfg.battery.max_discharge_power_kw * cfg.controller.reactive.max_battery_discharge_fraction
print(f"Reactive battery max discharge: {cfg.battery.max_discharge_power_kw:.0f} kW * {cfg.controller.reactive.max_battery_discharge_fraction:.2f} = {react_max:.1f} kW")
print(f"Predictive has NO cap on discharge (full 150 kW available)")