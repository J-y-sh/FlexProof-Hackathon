"""FlexProof — Predictive Neighbourhood Grid Flexibility Platform.

Industrial Energy Command Center Dashboard.
Schneider Electric / Yuva Yodha Energy Tech Hackathon.
"""
import sys
from pathlib import Path

# Add project root to path
root_dir = Path(__file__).parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import streamlit as st
import pandas as pd
import numpy as np

from dashboard.data_loader import (
    load_configuration, load_all_data, compute_comparative_summary
)
from dashboard.components.kpi_cards import (
    render_executive_hero, render_why_flexproof_story, render_scenario_kpis, render_comparative_kpi_table
)
from dashboard.components.scenario_comparison import (
    render_scenario_comparison_section, render_scenario_scorecard, create_scenario_benchmark_bars, create_cumulative_deficit_chart
)
from dashboard.components.predictive_view import (
    render_predictive_intelligence_section
)
from dashboard.components.battery_view import (
    render_battery_health_section
)
from dashboard.components.flexibility_view import (
    render_flexibility_section
)
from dashboard.components.event_explainer import (
    render_event_explainer_section
)


# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="FlexProof — Grid Flexibility Command Center",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM INDUSTRIAL STYLING (Injected via st.html) ---
st.html("""
<style>
    /* Dark Slate Industrial Energy Theme */
    .stApp {
        background-color: #0b1120;
        color: #f1f5f9;
    }
    
    /* Card Container */
    .metric-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    }
    
    /* Header Bar */
    .header-title {
        font-size: 1.8rem;
        font-weight: 800;
        color: #f8fafc;
        letter-spacing: -0.02em;
        margin-bottom: 0px;
    }
    .header-tagline {
        font-size: 0.95rem;
        color: #38bdf8;
        font-weight: 500;
        margin-bottom: 12px;
    }
    
    /* Streamlit Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #1e293b;
        border-radius: 6px 6px 0 0;
        color: #94a3b8;
        padding: 10px 18px;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0284c7 !important;
        color: #ffffff !important;
    }
</style>
""")


def main():
    # Load configuration
    try:
        config = load_configuration()
    except Exception as e:
        st.error(f"Error loading configuration: {e}")
        return

    firm_limit_kw = config.feeder.firm_limit_kw

    # Load data
    try:
        scenarios, events = load_all_data()
    except FileNotFoundError:
        st.warning("Processed scenario data not found. Running simulation now...")
        from simulator.simulation import run_all_scenarios
        from simulator.reporting import export_all_scenarios, export_events_csv
        
        with st.spinner("Executing 30-day simulation suite across all scenarios..."):
            sim_results = run_all_scenarios(config)
            export_all_scenarios(sim_results, "data/processed")
            export_events_csv(sim_results, "data/processed")
            
        scenarios, events = load_all_data()
        st.success("Simulation generated successfully!")

    # Compute dynamic summary
    summary = compute_comparative_summary(scenarios, firm_limit_kw)

    # --- SIDEBAR NAVIGATION & DEMO CONTROLS ---
    with st.sidebar:
        st.image("https://img.icons8.com/fluency/96/electricity.png", width=64)
        st.markdown("## **FLEXPROOF**")
        st.caption("Predictive Neighbourhood Grid Flexibility Platform")
        
        demo_mode = st.toggle("🎯 Hackathon Live Pitch Mode", value=True)
        st.divider()
        
        if demo_mode:
            view_mode = st.radio(
                "Pitch Navigation",
                [
                    "🏆 Executive / Judge Pitch",
                    "🔍 Stress Event Replay",
                    "📊 Full Benchmark Scorecard"
                ]
            )
        else:
            view_mode = st.radio(
                "Engineering Deep Dive",
                [
                    "🏢 Full Command Center",
                    "📊 Multi-Scenario Benchmark",
                    "🧠 Predictive Forecast Radar",
                    "🔋 Storage & Battery Health",
                    "⚙️ Flexible Load Fleets",
                    "🔍 Stress Event Replay"
                ]
            )
        
        st.divider()
        st.markdown("### ⚙️ Feeder Specifications")
        st.markdown(f"""
        - **Feeder Firm Limit:** `{firm_limit_kw:,.0f} kW`
        - **Solar PV Capacity:** `{config.renewable.solar_capacity_kw:,.0f} kW`
        - **Battery Capacity:** `{config.battery.capacity_kwh:,.0f} kWh`
        - **Max Battery Power:** `{config.battery.max_discharge_power_kw:,.0f} kW`
        - **Safe SOC Window:** `[{config.battery.min_soc*100:.0f}%, {config.battery.max_soc*100:.0f}%]`
        - **Simulation Horizon:** `30 Days (2,880 int)`
        """)
        
        st.divider()
        st.caption("⚡ FlexProof Engine • Physical Invariants Enforced")

    # --- RENDER SELECTED VIEW ---
    if view_mode in ["🏆 Executive / Judge Pitch", "🏢 Full Command Center"]:
        # 1. Executive Hero Section
        render_executive_hero(summary, firm_limit_kw)
        
        # 2. Why FlexProof 3-Stage Story
        render_why_flexproof_story()
        st.html("<div style='margin-bottom: 24px;'></div>")
        
        # 3. Interactive Key Event Replay
        render_event_explainer_section(scenarios, events, firm_limit_kw)
        st.html("<div style='margin-bottom: 24px;'></div>")
        
        # 4. Multi-Scenario Scorecard & Cumulative Trajectory
        st.markdown("### 📊 30-Day Multi-Scenario Benchmark & Cumulative Trajectory")
        render_scenario_scorecard(summary)
        st.plotly_chart(create_cumulative_deficit_chart(scenarios), width="stretch")
        
        # 5. Technical Deep Dive Expanders
        with st.expander("🔬 Technical Deep Dive: Predictive Forecast Radar & Error Residuals"):
            render_predictive_intelligence_section(scenarios['predictive'], firm_limit_kw)
            
        with st.expander("🔬 Technical Deep Dive: Battery Cycling Burden & Longevity Analysis"):
            render_battery_health_section(scenarios, config.battery, summary)
            
        with st.expander("🔬 Technical Deep Dive: Flexible Fleet Coordination & Actuator Response Times"):
            render_flexibility_section(scenarios, config.flexible_loads, summary)

    elif view_mode in ["📊 Full Benchmark Scorecard", "📊 Multi-Scenario Benchmark"]:
        render_executive_hero(summary, firm_limit_kw)
        render_scenario_comparison_section(scenarios, summary, firm_limit_kw)

    elif view_mode == "🧠 Predictive Forecast Radar":
        render_predictive_intelligence_section(scenarios['predictive'], firm_limit_kw)

    elif view_mode == "🔋 Storage & Battery Health":
        render_battery_health_section(scenarios, config.battery, summary)

    elif view_mode == "⚙️ Flexible Load Fleets":
        render_flexibility_section(scenarios, config.flexible_loads, summary)

    elif view_mode == "🔍 Stress Event Replay":
        render_event_explainer_section(scenarios, events, firm_limit_kw)

    # Footer
    st.markdown("---")
    st.caption("FlexProof Platform • Built for Schneider Electric / Yuva Yodha Energy Tech Hackathon • Deterministic 30-Day Feeder Simulation")


if __name__ == "__main__":
    main()
