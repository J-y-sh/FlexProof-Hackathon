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
    bat_saving = imp.get('battery_throughput_reduction_pct', 0.0)
    pred_adv = imp.get('predictive_advantage_pct', 0.0)

    st.html(f"""
    <div style="
        background: linear-gradient(135deg, #090d16 0%, #131d31 50%, #0f172a 100%);
        border: 1px solid #1e293b;
        border-top: 4px solid #06b6d4;
        border-radius: 12px;
        padding: 24px 28px;
        margin-bottom: 24px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.4);
    ">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 16px;">
            <div>
                <div style="display: inline-block; background: rgba(6, 182, 212, 0.15); color: #38bdf8; font-size: 0.75rem; font-weight: 700; padding: 4px 10px; border-radius: 4px; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 8px;">
                    Neighbourhood Grid Flexibility Platform
                </div>
                <h1 style="color: #f8fafc; font-size: 2.2rem; font-weight: 800; margin: 0; letter-spacing: -0.02em;">
                    FLEXPROOF COMMAND CENTER
                </h1>
                <p style="color: #94a3b8; font-size: 1.05rem; font-weight: 500; margin-top: 4px; margin-bottom: 0;">
                    <i>"Predict feeder stress before it becomes a distribution transformer failure."</i>
                </p>
            </div>
            <div style="background: rgba(15, 23, 42, 0.8); border: 1px solid #334155; border-radius: 8px; padding: 12px 18px; text-align: right;">
                <div style="font-size: 0.75rem; color: #64748b; font-weight: 600; text-transform: uppercase;">Feeder Capacity Limit</div>
                <div style="font-size: 1.5rem; color: #38bdf8; font-weight: 800;">{firm_limit_kw:,.0f} kW</div>
                <div style="font-size: 0.75rem; color: #10b981; font-weight: 600;">30 Days • 2,880 Intervals</div>
            </div>
        </div>

        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 16px; margin-top: 22px;">
            <!-- Baseline Card -->
            <div style="background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 8px; padding: 14px 16px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 0.8rem; font-weight: 700; color: #f87171; text-transform: uppercase;">1. Baseline (Unmanaged)</span>
                    <span style="font-size: 0.75rem; background: rgba(239, 68, 68, 0.2); color: #fca5a5; padding: 2px 6px; border-radius: 4px;">Zero Control</span>
                </div>
                <div style="font-size: 1.8rem; font-weight: 800; color: #f87171; margin-top: 6px;">{b.get('stress_intervals', 0)} <span style="font-size: 0.9rem; font-weight: 500; color: #cbd5e1;">stress intervals</span></div>
                <div style="font-size: 0.85rem; color: #94a3b8; margin-top: 2px;"><b>{b.get('deficit_energy_kwh', 0):,.1f} kWh</b> unserved energy deficit</div>
            </div>

            <!-- Reactive Card -->
            <div style="background: rgba(245, 158, 11, 0.08); border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 8px; padding: 14px 16px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 0.8rem; font-weight: 700; color: #fbbf24; text-transform: uppercase;">2. Reactive Control</span>
                    <span style="font-size: 0.75rem; background: rgba(245, 158, 11, 0.2); color: #fde68a; padding: 2px 6px; border-radius: 4px;">Threshold</span>
                </div>
                <div style="font-size: 1.8rem; font-weight: 800; color: #fbbf24; margin-top: 6px;">{r.get('stress_intervals', 0)} <span style="font-size: 0.9rem; font-weight: 500; color: #cbd5e1;">stress intervals</span></div>
                <div style="font-size: 0.85rem; color: #94a3b8; margin-top: 2px;"><b>{r.get('deficit_energy_kwh', 0):,.1f} kWh</b> deficit (↓{imp.get('reactive_deficit_reduction_pct', 0):.1f}%)</div>
            </div>

            <!-- Predictive Card -->
            <div style="background: rgba(16, 185, 129, 0.12); border: 1px solid rgba(16, 185, 129, 0.4); border-radius: 8px; padding: 14px 16px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 0.8rem; font-weight: 700; color: #34d399; text-transform: uppercase;">3. Predictive FlexProof</span>
                    <span style="font-size: 0.75rem; background: rgba(16, 185, 129, 0.25); color: #6ee7b7; padding: 2px 6px; border-radius: 4px; font-weight: 700;">Optimal</span>
                </div>
                <div style="font-size: 1.8rem; font-weight: 800; color: #34d399; margin-top: 6px;">{p.get('stress_intervals', 0)} <span style="font-size: 0.9rem; font-weight: 500; color: #cbd5e1;">residual interval</span></div>
                <div style="font-size: 0.85rem; color: #94a3b8; margin-top: 2px;"><b>{p.get('deficit_energy_kwh', 0):,.2f} kWh</b> deficit (<b>↓{def_red:.2f}%</b>)</div>
            </div>
        </div>

        <div style="margin-top: 18px; padding-top: 14px; border-top: 1px solid #1e293b; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
            <div style="font-size: 0.95rem; color: #e2e8f0; font-weight: 600;">
                ⭐ <span style="color: #38bdf8;">Core Breakthrough:</span> FlexProof achieves <b>{def_red:.2f}% deficit reduction</b> while using <span style="color: #a78bfa;"><b>{bat_saving:.1f}% less battery throughput</b></span> than reactive control.
            </div>
            <div style="font-size: 0.8rem; color: #64748b;">
                Simulated 30-Day Feeder Data • 15-Minute Resolution • Physical Invariants Enforced
            </div>
        </div>
    </div>
    """)


def render_why_flexproof_story():
    """Render the compact 3-stage control progression story."""
    st.markdown("### 🧭 The Control Strategy Progression: Why FlexProof?")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.html("""
        <div style="background: #1e293b; border: 1px solid #334155; border-top: 4px solid #ef4444; border-radius: 8px; padding: 16px; height: 100%;">
            <div style="font-size: 0.85rem; font-weight: 700; color: #f87171; text-transform: uppercase;">Stage 1 • Baseline</div>
            <h4 style="color: #f8fafc; margin-top: 4px; margin-bottom: 8px;">Unmanaged Feeder</h4>
            <p style="font-size: 0.85rem; color: #94a3b8; line-height: 1.45;">
                No flexibility coordination. The distribution feeder absorbs uncontrolled evening peak demand, resulting in recurring limit breaches (125 intervals) and severe transformer thermal overload risk.
            </p>
            <div style="font-size: 0.75rem; color: #ef4444; font-weight: 600; margin-top: 8px;">
                ❌ 2,707.6 kWh Unserved Deficit
            </div>
        </div>
        """)
        
    with col2:
        st.html("""
        <div style="background: #1e293b; border: 1px solid #334155; border-top: 4px solid #f59e0b; border-radius: 8px; padding: 16px; height: 100%;">
            <div style="font-size: 0.85rem; font-weight: 700; color: #fbbf24; text-transform: uppercase;">Stage 2 • Reactive Control</div>
            <h4 style="color: #f8fafc; margin-top: 4px; margin-bottom: 8px;">Threshold Reaction</h4>
            <p style="font-size: 0.85rem; color: #94a3b8; line-height: 1.45;">
                Detects stress only <i>after</i> the feeder limit is breached. Heavy water pumps and agricultural loads have 15–30 min response lags, forcing emergency battery discharge that wears out cells.
            </p>
            <div style="font-size: 0.75rem; color: #f59e0b; font-weight: 600; margin-top: 8px;">
                ⚠️ 14 Stress Intervals • High Battery Wear
            </div>
        </div>
        """)
        
    with col3:
        st.html("""
        <div style="background: #1e293b; border: 1px solid #334155; border-top: 4px solid #10b981; border-radius: 8px; padding: 16px; height: 100%;">
            <div style="font-size: 0.85rem; font-weight: 700; color: #34d399; text-transform: uppercase;">Stage 3 • Predictive FlexProof</div>
            <h4 style="color: #f8fafc; margin-top: 4px; margin-bottom: 8px;">Forecast-Driven Coordination</h4>
            <p style="font-size: 0.85rem; color: #94a3b8; line-height: 1.45;">
                Forecasts upcoming stress 1 hour ahead. Pre-shifts slow-response loads with advance notice and reserves storage capacity, smoothing peak demand with minimal battery cycling.
            </p>
            <div style="font-size: 0.75rem; color: #10b981; font-weight: 600; margin-top: 8px;">
                ✅ 99.94% Deficit Reduction • 52% Less Wear
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
    """Render a structured side-by-side comparative scorecard table."""
    b = summary.get('baseline', {})
    r = summary.get('reactive', {})
    p = summary.get('predictive', {})
    imp = summary.get('improvements', {})

    st.markdown("### 📋 30-Day Multi-Scenario Scorecard")

    col1, col2, col3, col4 = st.columns([1.5, 1, 1, 1])

    with col1:
        st.markdown("""
        **Operational Metric**
        - **Deficit Energy (kWh)**
        - **Feeder Stress Intervals**
        - **Stress Duration (hours)**
        - **Peak Net Demand (kW)**
        - **Max Deficit (kW)**
        - **Battery Cycling Throughput (kWh)**
        - **Flexible Energy Shifted (kWh)**
        """)

    with col2:
        st.markdown(f"""
        **🔴 Baseline (Unmanaged)**
        - `{b.get('deficit_energy_kwh', 0):,.1f} kWh`
        - `{b.get('stress_intervals', 0)}`
        - `{b.get('stress_duration_hours', 0):.2f} hrs`
        - `{b.get('peak_net_demand_kw', 0):,.1f} kW`
        - `{b.get('max_deficit_kw', 0):,.1f} kW`
        - `{b.get('battery_throughput_kwh', 0):,.1f} kWh`
        - `{b.get('shifted_energy_kwh', 0):,.1f} kWh`
        """)

    with col3:
        st.markdown(f"""
        **🟡 Reactive Control**
        - `{r.get('deficit_energy_kwh', 0):,.1f} kWh` *(↓{imp.get('reactive_deficit_reduction_pct', 0):.1f}%)*
        - `{r.get('stress_intervals', 0)}` *(↓{imp.get('reactive_stress_reduction_pct', 0):.1f}%)*
        - `{r.get('stress_duration_hours', 0):.2f} hrs`
        - `{r.get('peak_net_demand_kw', 0):,.1f} kW`
        - `{r.get('max_deficit_kw', 0):,.1f} kW`
        - `{r.get('battery_throughput_kwh', 0):,.1f} kWh`
        - `{r.get('shifted_energy_kwh', 0):,.1f} kWh`
        """)

    with col4:
        st.markdown(f"""
        **🟢 Predictive FlexProof**
        - `{p.get('deficit_energy_kwh', 0):,.1f} kWh` **(↓{imp.get('predictive_deficit_reduction_pct', 0):.2f}%)**
        - `{p.get('stress_intervals', 0)}` **(↓{imp.get('predictive_stress_reduction_pct', 0):.1f}%)**
        - `{p.get('stress_duration_hours', 0):.2f} hrs`
        - `{p.get('peak_net_demand_kw', 0):,.1f} kW`
        - `{p.get('max_deficit_kw', 0):,.1f} kW`
        - `{p.get('battery_throughput_kwh', 0):,.1f} kWh` *(↓{imp.get('battery_throughput_reduction_pct', 0):.1f}% vs Reactive)*
        - `{p.get('shifted_energy_kwh', 0):,.1f} kWh`
        """)
