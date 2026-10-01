"""KPI, Executive Hero, and Metric Card components for FlexProof Command Center."""
from typing import Dict, Any
import streamlit as st


def render_executive_hero(summary: Dict[str, Any], firm_limit_kw: float = 2300.0):
    """Render the top executive hero section with prominent 3-scenario outcomes."""
    b = summary.get('baseline', {})
    r = summary.get('reactive', {})
    p = summary.get('predictive', {})
    imp = summary.get('improvements', {})

    def_red = imp.get('predictive_deficit_reduction_pct', 0.0)
    stress_red = imp.get('predictive_stress_reduction_pct', 0.0)
    bat_saving = imp.get('battery_throughput_reduction_pct', 0.0)
    peak_shave = imp.get('peak_shaving_predictive_kw', 0.0)

    st.html(f"""
    <div style="
        background: linear-gradient(135deg, #090e17 0%, #111a2e 50%, #0f172a 100%);
        border: 1px solid #1e293b;
        border-top: 4px solid #06b6d4;
        border-radius: 12px;
        padding: 24px 28px;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
    ">
        <!-- Title and Platform Scope Badge -->
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 16px;">
            <div>
                <div style="display: inline-flex; align-items: center; gap: 8px; background: rgba(6, 182, 212, 0.12); border: 1px solid rgba(6, 182, 212, 0.35); color: #38bdf8; font-size: 0.75rem; font-weight: 700; padding: 4px 12px; border-radius: 20px; letter-spacing: 0.06em; text-transform: uppercase; margin-bottom: 10px;">
                    <span style="display: inline-block; width: 6px; height: 6px; border-radius: 50%; background: #38bdf8;"></span>
                    Control-Room Simulation Prototype • 30 Days (2,880 Intervals)
                </div>
                <h1 style="color: #f8fafc; font-size: 2.3rem; font-weight: 800; margin: 0; letter-spacing: -0.03em; line-height: 1.15;">
                    FLEXPROOF COMMAND CENTER
                </h1>
                <div style="color: #38bdf8; font-size: 0.95rem; font-weight: 700; letter-spacing: 0.04em; margin-top: 6px; text-transform: uppercase;">
                    Predict → Prepare → Coordinate → Dispatch → Learn
                </div>
            </div>
            <div style="background: rgba(15, 23, 42, 0.85); border: 1px solid #334155; border-radius: 8px; padding: 12px 20px; text-align: right;">
                <div style="font-size: 0.72rem; color: #64748b; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;">Feeder Firm Capacity</div>
                <div style="font-size: 1.6rem; color: #38bdf8; font-weight: 800; font-family: monospace;">{firm_limit_kw:,.0f} kW</div>
                <div style="font-size: 0.72rem; color: #10b981; font-weight: 600;">11 kV / 415 V Substation Feeder</div>
            </div>
        </div>

        <!-- One-Sentence Clear Purpose Context -->
        <p style="color: #cbd5e1; font-size: 1.0rem; font-weight: 400; line-height: 1.55; margin-top: 14px; margin-bottom: 20px; max-width: 950px;">
            FlexProof simulates how a distribution feeder anticipates renewable intermittency and coordinates flexible load pre-shifting and community battery reserves before feeder stress breaches transformer thermal limits.
        </p>

        <!-- 4 Primary Headline Outcome Cards -->
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 14px;">
            <!-- Metric 1: Deficit Reduction -->
            <div style="background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.35); border-radius: 8px; padding: 14px 16px;">
                <div style="font-size: 0.72rem; font-weight: 700; color: #34d399; text-transform: uppercase; letter-spacing: 0.05em;">Deficit Energy Reduction</div>
                <div style="font-size: 2.1rem; font-weight: 900; color: #34d399; margin-top: 4px; line-height: 1.1;">↓{def_red:.2f}%</div>
                <div style="font-size: 0.8rem; color: #94a3b8; margin-top: 6px;"><b>{p.get('deficit_energy_kwh', 0):,.2f} kWh</b> residual vs {b.get('deficit_energy_kwh', 0):,.0f} kWh</div>
            </div>

            <!-- Metric 2: Stress Intervals -->
            <div style="background: rgba(6, 182, 212, 0.08); border: 1px solid rgba(6, 182, 212, 0.35); border-radius: 8px; padding: 14px 16px;">
                <div style="font-size: 0.72rem; font-weight: 700; color: #38bdf8; text-transform: uppercase; letter-spacing: 0.05em;">Feeder Stress Reduced</div>
                <div style="font-size: 2.1rem; font-weight: 900; color: #38bdf8; margin-top: 4px; line-height: 1.1;">{b.get('stress_intervals', 0)} → {p.get('stress_intervals', 0)}</div>
                <div style="font-size: 0.8rem; color: #94a3b8; margin-top: 6px;"><b>↓{stress_red:.1f}%</b> overload duration ({p.get('stress_duration_hours', 0):.2f}h residual)</div>
            </div>

            <!-- Metric 3: Battery Longevity -->
            <div style="background: rgba(139, 92, 246, 0.08); border: 1px solid rgba(139, 92, 246, 0.35); border-radius: 8px; padding: 14px 16px;">
                <div style="font-size: 0.72rem; font-weight: 700; color: #c4b5fd; text-transform: uppercase; letter-spacing: 0.05em;">Battery Cycling Savings</div>
                <div style="font-size: 2.1rem; font-weight: 900; color: #c4b5fd; margin-top: 4px; line-height: 1.1;">↓{bat_saving:.1f}%</div>
                <div style="font-size: 0.8rem; color: #94a3b8; margin-top: 6px;"><b>{p.get('battery_throughput_kwh', 0):,.0f} kWh</b> throughput vs {r.get('battery_throughput_kwh', 0):,.0f} kWh</div>
            </div>

            <!-- Metric 4: Peak Shaving -->
            <div style="background: rgba(245, 158, 11, 0.08); border: 1px solid rgba(245, 158, 11, 0.35); border-radius: 8px; padding: 14px 16px;">
                <div style="font-size: 0.72rem; font-weight: 700; color: #fbbf24; text-transform: uppercase; letter-spacing: 0.05em;">Peak Feeder Shaving</div>
                <div style="font-size: 2.1rem; font-weight: 900; color: #fbbf24; margin-top: 4px; line-height: 1.1;">↓{peak_shave:.1f} kW</div>
                <div style="font-size: 0.8rem; color: #94a3b8; margin-top: 6px;">Peak: <b>{p.get('peak_net_demand_kw', 0):,.0f} kW</b> (Baseline: {b.get('peak_net_demand_kw', 0):,.0f} kW)</div>
            </div>
        </div>
    </div>
    """)


def render_why_flexproof_story(summary: Dict[str, Any] = None):
    """Render the clear 3-stage control progression story."""
    b = summary.get('baseline', {}) if summary else {}
    r = summary.get('reactive', {}) if summary else {}
    p = summary.get('predictive', {}) if summary else {}
    imp = summary.get('improvements', {}) if summary else {}

    b_def = b.get('deficit_energy_kwh', 2707.6)
    b_int = b.get('stress_intervals', 125)
    r_def = r.get('deficit_energy_kwh', 83.8)
    r_int = r.get('stress_intervals', 14)
    p_def = p.get('deficit_energy_kwh', 1.67)
    p_int = p.get('stress_intervals', 1)
    p_red = imp.get('predictive_deficit_reduction_pct', 99.94)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.html(f"""
        <div style="background: #111827; border: 1px solid #374151; border-top: 4px solid #ef4444; border-radius: 8px; padding: 18px 20px; height: 100%; display: flex; flex-direction: column; justify-content: space-between;">
            <div>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 0.72rem; font-weight: 800; color: #f87171; letter-spacing: 0.05em; text-transform: uppercase;">Stage 01 • Baseline</span>
                    <span style="font-size: 0.7rem; background: rgba(239, 68, 68, 0.18); color: #fca5a5; padding: 2px 8px; border-radius: 4px; font-weight: 700;">NO COORDINATION</span>
                </div>
                <h4 style="color: #f8fafc; margin-top: 8px; margin-bottom: 8px; font-size: 1.15rem; font-weight: 700;">Unmanaged Feeder</h4>
                <p style="font-size: 0.85rem; color: #94a3b8; line-height: 1.5; margin-bottom: 12px;">
                    Solar PV drops as residential cooking, cooling, and EV charging ramp up. The unmitigated feeder repeatedly breaches its 2,300 kW limit, degrading substation transformer insulation.
                </p>
            </div>
            <div style="background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.25); border-radius: 6px; padding: 10px 12px; margin-top: 8px;">
                <div style="font-size: 0.72rem; color: #fca5a5; font-weight: 600; text-transform: uppercase;">Observed Impact</div>
                <div style="font-size: 1.15rem; color: #f87171; font-weight: 800;">{b_def:,.1f} kWh Deficit</div>
                <div style="font-size: 0.75rem; color: #94a3b8;">{b_int} stress intervals ({b_int * 0.25:.1f} hours overload)</div>
            </div>
        </div>
        """)

    with col2:
        st.html(f"""
        <div style="background: #111827; border: 1px solid #374151; border-top: 4px solid #f59e0b; border-radius: 8px; padding: 18px 20px; height: 100%; display: flex; flex-direction: column; justify-content: space-between;">
            <div>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 0.72rem; font-weight: 800; color: #fbbf24; letter-spacing: 0.05em; text-transform: uppercase;">Stage 02 • Reactive Control</span>
                    <span style="font-size: 0.7rem; background: rgba(245, 158, 11, 0.18); color: #fde68a; padding: 2px 8px; border-radius: 4px; font-weight: 700;">THRESHOLD RESPONSE</span>
                </div>
                <h4 style="color: #f8fafc; margin-top: 8px; margin-bottom: 8px; font-size: 1.15rem; font-weight: 700;">Actuator Latency Trap</h4>
                <p style="font-size: 0.85rem; color: #94a3b8; line-height: 1.5; margin-bottom: 12px;">
                    Controller reacts only <i>after</i> the limit is breached. Water pumps and agricultural wells require 15–30 min to spool down safely. To compensate, the battery discharges at emergency rates, rapidly burning cell throughput.
                </p>
            </div>
            <div style="background: rgba(245, 158, 11, 0.08); border: 1px solid rgba(245, 158, 11, 0.25); border-radius: 6px; padding: 10px 12px; margin-top: 8px;">
                <div style="font-size: 0.72rem; color: #fde68a; font-weight: 600; text-transform: uppercase;">Observed Impact</div>
                <div style="font-size: 1.15rem; color: #fbbf24; font-weight: 800;">{r_def:,.1f} kWh Deficit</div>
                <div style="font-size: 0.75rem; color: #94a3b8;">{r_int} residual stress intervals • High battery wear</div>
            </div>
        </div>
        """)

    with col3:
        st.html(f"""
        <div style="background: #111827; border: 1px solid rgba(16, 185, 129, 0.4); border-top: 4px solid #10b981; border-radius: 8px; padding: 18px 20px; height: 100%; display: flex; flex-direction: column; justify-content: space-between; box-shadow: 0 4px 15px -2px rgba(16, 185, 129, 0.15);">
            <div>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 0.72rem; font-weight: 800; color: #34d399; letter-spacing: 0.05em; text-transform: uppercase;">Stage 03 • Predictive FlexProof</span>
                    <span style="font-size: 0.7rem; background: rgba(16, 185, 129, 0.22); color: #6ee7b7; padding: 2px 8px; border-radius: 4px; font-weight: 800;">LOOKAHEAD PRE-DISPATCH</span>
                </div>
                <h4 style="color: #f8fafc; margin-top: 8px; margin-bottom: 8px; font-size: 1.15rem; font-weight: 700;">Forecast-Informed Harmony</h4>
                <p style="font-size: 0.85rem; color: #94a3b8; line-height: 1.5; margin-bottom: 12px;">
                    Forecasts upcoming stress 1 hour ahead. Pre-shifts slow-response loads with advance notice, holding storage in reserve for smooth real-time precision buffering.
                </p>
            </div>
            <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.35); border-radius: 6px; padding: 10px 12px; margin-top: 8px;">
                <div style="font-size: 0.72rem; color: #6ee7b7; font-weight: 700; text-transform: uppercase;">Observed Impact</div>
                <div style="font-size: 1.15rem; color: #34d399; font-weight: 900;">{p_def:,.2f} kWh (↓{p_red:.2f}%)</div>
                <div style="font-size: 0.75rem; color: #cbd5e1;">{p_int} residual interval • 53% less battery cycling</div>
            </div>
        </div>
        """)


def render_scenario_kpis(metrics: Dict[str, float], scenario_name: str, firm_limit_kw: float = 2300.0):
    """Render a 5-column metric summary row for a specific scenario."""
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        stress_int = metrics.get('stress_intervals', 0)
        stress_hrs = metrics.get('stress_duration_hours', 0.0)
        st.metric(
            label="Feeder Stress Duration",
            value=f"{stress_hrs:.2f} hrs",
            delta=f"{stress_int} intervals (15-min)",
            delta_color="inverse" if stress_int > 0 else "off"
        )

    with col2:
        def_kwh = metrics.get('deficit_energy_kwh', 0.0)
        st.metric(
            label="Total Deficit Energy",
            value=f"{def_kwh:,.1f} kWh",
            delta="Unserved energy",
            delta_color="inverse" if def_kwh > 0 else "off"
        )

    with col3:
        max_def = metrics.get('max_deficit_kw', 0.0)
        st.metric(
            label="Peak Deficit Power",
            value=f"{max_def:,.1f} kW",
            delta=f"Over {firm_limit_kw:,.0f} kW limit",
            delta_color="inverse" if max_def > 0 else "off"
        )

    with col4:
        peak_nd = metrics.get('peak_net_demand_kw', 0.0)
        loading = (peak_nd / firm_limit_kw * 100) if firm_limit_kw > 0 else 0
        st.metric(
            label="Max Feeder Loading",
            value=f"{peak_nd:,.1f} kW",
            delta=f"{loading:.1f}% capacity",
            delta_color="inverse" if loading > 100 else "normal"
        )

    with col5:
        bat_thr = metrics.get('battery_throughput_kwh', 0.0)
        st.metric(
            label="Battery Throughput",
            value=f"{bat_thr:,.1f} kWh",
            delta="Energy cycled",
            delta_color="off"
        )


def render_comparative_kpi_table(summary: Dict[str, Dict]):
    """Render a clean industrial control scorecard table replacing raw markdown lists."""
    b = summary.get('baseline', {})
    r = summary.get('reactive', {})
    p = summary.get('predictive', {})
    imp = summary.get('improvements', {})

    st.html(f"""
    <div style="background: #0f172a; border: 1px solid #334155; border-radius: 8px; overflow-x: auto; margin-top: 12px; margin-bottom: 24px;">
        <table style="width: 100%; border-collapse: collapse; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 0.88rem; text-align: left;">
            <thead>
                <tr style="background: #1e293b; border-bottom: 2px solid #475569;">
                    <th style="padding: 12px 16px; color: #94a3b8; font-weight: 700; text-transform: uppercase; font-size: 0.75rem;">Operational Metric</th>
                    <th style="padding: 12px 16px; color: #f87171; font-weight: 700; text-transform: uppercase; font-size: 0.75rem;">🔴 Baseline (Unmanaged)</th>
                    <th style="padding: 12px 16px; color: #fbbf24; font-weight: 700; text-transform: uppercase; font-size: 0.75rem;">🟡 Reactive Control</th>
                    <th style="padding: 12px 16px; color: #34d399; font-weight: 800; text-transform: uppercase; font-size: 0.75rem; background: rgba(16, 185, 129, 0.1); border-left: 2px solid #10b981; border-right: 2px solid #10b981;">🟢 Predictive FlexProof</th>
                    <th style="padding: 12px 16px; color: #38bdf8; font-weight: 700; text-transform: uppercase; font-size: 0.75rem;">Predictive Advantage</th>
                </tr>
            </thead>
            <tbody>
                <tr style="border-bottom: 1px solid #1e293b;">
                    <td style="padding: 10px 16px; font-weight: 600; color: #e2e8f0;">Deficit Energy (kWh)</td>
                    <td style="padding: 10px 16px; color: #fca5a5; font-family: monospace;">{b.get('deficit_energy_kwh', 0):,.1f}</td>
                    <td style="padding: 10px 16px; color: #fde68a; font-family: monospace;">{r.get('deficit_energy_kwh', 0):,.1f}</td>
                    <td style="padding: 10px 16px; color: #6ee7b7; font-weight: 700; font-family: monospace; background: rgba(16, 185, 129, 0.08); border-left: 2px solid #10b981; border-right: 2px solid #10b981;">{p.get('deficit_energy_kwh', 0):,.2f}</td>
                    <td style="padding: 10px 16px; color: #38bdf8; font-weight: 700;">↓ {imp.get('predictive_deficit_reduction_pct', 0):.2f}%</td>
                </tr>
                <tr style="border-bottom: 1px solid #1e293b; background: rgba(255, 255, 255, 0.015);">
                    <td style="padding: 10px 16px; font-weight: 600; color: #e2e8f0;">Feeder Stress Intervals (15-min)</td>
                    <td style="padding: 10px 16px; color: #fca5a5; font-family: monospace;">{b.get('stress_intervals', 0)} int <span style="font-size: 0.7rem; color: #ef4444; background: rgba(239, 68, 68, 0.2); padding: 1px 5px; border-radius: 3px;">SEVERE</span></td>
                    <td style="padding: 10px 16px; color: #fde68a; font-family: monospace;">{r.get('stress_intervals', 0)} int <span style="font-size: 0.7rem; color: #f59e0b; background: rgba(245, 158, 11, 0.2); padding: 1px 5px; border-radius: 3px;">LAG TRAP</span></td>
                    <td style="padding: 10px 16px; color: #6ee7b7; font-weight: 700; font-family: monospace; background: rgba(16, 185, 129, 0.08); border-left: 2px solid #10b981; border-right: 2px solid #10b981;">{p.get('stress_intervals', 0)} int <span style="font-size: 0.7rem; color: #10b981; background: rgba(16, 185, 129, 0.25); padding: 1px 5px; border-radius: 3px;">RESIDUAL</span></td>
                    <td style="padding: 10px 16px; color: #38bdf8; font-weight: 700;">↓ {imp.get('predictive_stress_reduction_pct', 0):.1f}%</td>
                </tr>
                <tr style="border-bottom: 1px solid #1e293b;">
                    <td style="padding: 10px 16px; font-weight: 600; color: #e2e8f0;">Overload Duration (hours)</td>
                    <td style="padding: 10px 16px; color: #fca5a5; font-family: monospace;">{b.get('stress_duration_hours', 0):.2f} hrs</td>
                    <td style="padding: 10px 16px; color: #fde68a; font-family: monospace;">{r.get('stress_duration_hours', 0):.2f} hrs</td>
                    <td style="padding: 10px 16px; color: #6ee7b7; font-weight: 700; font-family: monospace; background: rgba(16, 185, 129, 0.08); border-left: 2px solid #10b981; border-right: 2px solid #10b981;">{p.get('stress_duration_hours', 0):.2f} hrs</td>
                    <td style="padding: 10px 16px; color: #38bdf8; font-weight: 700;">↓ {imp.get('predictive_stress_reduction_pct', 0):.1f}%</td>
                </tr>
                <tr style="border-bottom: 1px solid #1e293b; background: rgba(255, 255, 255, 0.015);">
                    <td style="padding: 10px 16px; font-weight: 600; color: #e2e8f0;">Peak Net Demand (kW)</td>
                    <td style="padding: 10px 16px; color: #fca5a5; font-family: monospace;">{b.get('peak_net_demand_kw', 0):,.1f} kW</td>
                    <td style="padding: 10px 16px; color: #fde68a; font-family: monospace;">{r.get('peak_net_demand_kw', 0):,.1f} kW</td>
                    <td style="padding: 10px 16px; color: #6ee7b7; font-weight: 700; font-family: monospace; background: rgba(16, 185, 129, 0.08); border-left: 2px solid #10b981; border-right: 2px solid #10b981;">{p.get('peak_net_demand_kw', 0):,.1f} kW</td>
                    <td style="padding: 10px 16px; color: #38bdf8; font-weight: 700;">↓ {imp.get('peak_shaving_predictive_kw', 0):.1f} kW</td>
                </tr>
                <tr style="border-bottom: 1px solid #1e293b;">
                    <td style="padding: 10px 16px; font-weight: 600; color: #e2e8f0;">Maximum Overload Deficit (kW)</td>
                    <td style="padding: 10px 16px; color: #fca5a5; font-family: monospace;">{b.get('max_deficit_kw', 0):,.1f} kW</td>
                    <td style="padding: 10px 16px; color: #fde68a; font-family: monospace;">{r.get('max_deficit_kw', 0):,.1f} kW</td>
                    <td style="padding: 10px 16px; color: #6ee7b7; font-weight: 700; font-family: monospace; background: rgba(16, 185, 129, 0.08); border-left: 2px solid #10b981; border-right: 2px solid #10b981;">{p.get('max_deficit_kw', 0):,.1f} kW</td>
                    <td style="padding: 10px 16px; color: #38bdf8; font-weight: 700;">↓ {b.get('max_deficit_kw', 0) - p.get('max_deficit_kw', 0):.1f} kW</td>
                </tr>
                <tr style="border-bottom: 1px solid #1e293b; background: rgba(255, 255, 255, 0.015);">
                    <td style="padding: 10px 16px; font-weight: 600; color: #e2e8f0;">Battery Cycling Throughput (kWh)</td>
                    <td style="padding: 10px 16px; color: #94a3b8; font-family: monospace;">0.0 (Idle)</td>
                    <td style="padding: 10px 16px; color: #fde68a; font-family: monospace;">{r.get('battery_throughput_kwh', 0):,.1f}</td>
                    <td style="padding: 10px 16px; color: #6ee7b7; font-weight: 700; font-family: monospace; background: rgba(16, 185, 129, 0.08); border-left: 2px solid #10b981; border-right: 2px solid #10b981;">{p.get('battery_throughput_kwh', 0):,.1f}</td>
                    <td style="padding: 10px 16px; color: #c4b5fd; font-weight: 700;">↓ {imp.get('battery_throughput_reduction_pct', 0):.1f}% less wear</td>
                </tr>
                <tr>
                    <td style="padding: 10px 16px; font-weight: 600; color: #e2e8f0;">Flexible Energy Shifted (kWh)</td>
                    <td style="padding: 10px 16px; color: #94a3b8; font-family: monospace;">0.0</td>
                    <td style="padding: 10px 16px; color: #fde68a; font-family: monospace;">{r.get('shifted_energy_kwh', 0):,.1f}</td>
                    <td style="padding: 10px 16px; color: #6ee7b7; font-weight: 700; font-family: monospace; background: rgba(16, 185, 129, 0.08); border-left: 2px solid #10b981; border-right: 2px solid #10b981;">{p.get('shifted_energy_kwh', 0):,.1f}</td>
                    <td style="padding: 10px 16px; color: #38bdf8; font-weight: 700;">↑ 2.3× more load flex</td>
                </tr>
            </tbody>
        </table>
    </div>
    """)
