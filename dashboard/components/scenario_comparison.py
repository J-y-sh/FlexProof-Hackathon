"""Scenario comparison, benchmarking, and scorecard visualizations for FlexProof."""
from typing import Dict, Any
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

from dashboard.components.kpi_cards import render_comparative_kpi_table


def create_scenario_benchmark_bars(summary: Dict[str, Any]) -> go.Figure:
    """Create a 2x2 grid of horizontal comparison bars with legible labels and clear values."""
    scenarios = ['Baseline (Unmanaged)', 'Reactive Control', 'Predictive FlexProof']
    # Reverse so Baseline is at top, Predictive is at bottom of each horizontal chart
    y_labels = ['Predictive FlexProof', 'Reactive Control', 'Baseline (Unmanaged)']
    colors = ['#10b981', '#f59e0b', '#ef4444']

    b = summary.get('baseline', {})
    r = summary.get('reactive', {})
    p = summary.get('predictive', {})

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            "1. Deficit Energy (kWh) [Lower is Better]",
            "2. Feeder Stress Overloads (15-min Intervals)",
            "3. Max Overload Deficit (kW)",
            "4. Battery Cycling Burden (kWh Throughput)"
        ),
        horizontal_spacing=0.15,
        vertical_spacing=0.18
    )

    # 1. Deficit Energy
    v1 = [p.get('deficit_energy_kwh', 0), r.get('deficit_energy_kwh', 0), b.get('deficit_energy_kwh', 0)]
    t1 = [f"{v:,.2f} kWh" if v < 10 else f"{v:,.1f} kWh" for v in v1]
    fig.add_trace(
        go.Bar(
            y=y_labels, x=v1, orientation='h',
            marker_color=colors,
            text=t1, textposition='outside',
            showlegend=False
        ),
        row=1, col=1
    )

    # 2. Stress Intervals
    v2 = [p.get('stress_intervals', 0), r.get('stress_intervals', 0), b.get('stress_intervals', 0)]
    t2 = [f"{v} intervals ({v*0.25:.1f}h)" for v in v2]
    fig.add_trace(
        go.Bar(
            y=y_labels, x=v2, orientation='h',
            marker_color=colors,
            text=t2, textposition='outside',
            showlegend=False
        ),
        row=1, col=2
    )

    # 3. Max Deficit kW
    v3 = [p.get('max_deficit_kw', 0), r.get('max_deficit_kw', 0), b.get('max_deficit_kw', 0)]
    t3 = [f"{v:.1f} kW" for v in v3]
    fig.add_trace(
        go.Bar(
            y=y_labels, x=v3, orientation='h',
            marker_color=colors,
            text=t3, textposition='outside',
            showlegend=False
        ),
        row=2, col=1
    )

    # 4. Battery Throughput
    v4 = [p.get('battery_throughput_kwh', 0), r.get('battery_throughput_kwh', 0), b.get('battery_throughput_kwh', 0)]
    t4 = [f"{v:,.1f} kWh" if v > 0 else "0.0 kWh (Idle)" for v in v4]
    fig.add_trace(
        go.Bar(
            y=y_labels, x=v4, orientation='h',
            marker_color=colors,
            text=t4, textposition='outside',
            showlegend=False
        ),
        row=2, col=2
    )

    fig.update_layout(
        template="plotly_dark",
        height=420,
        margin=dict(l=10, r=60, t=40, b=20),
        plot_bgcolor='rgba(15, 23, 42, 0.7)',
        paper_bgcolor='rgba(15, 23, 42, 0.0)',
    )
    fig.update_xaxes(showgrid=True, gridcolor='rgba(51, 65, 85, 0.4)')
    fig.update_yaxes(tickfont=dict(size=11, color="#cbd5e1"))
    return fig


def create_cumulative_deficit_chart(scenarios: Dict[str, pd.DataFrame], dt_hours: float = 0.25) -> go.Figure:
    """Create cumulative unserved deficit energy chart across 30 days."""
    fig = go.Figure()

    colors = {
        'baseline': '#ef4444',
        'reactive': '#f59e0b',
        'predictive': '#10b981'
    }
    labels = {
        'baseline': 'Baseline (Unmanaged)',
        'reactive': 'Reactive Control',
        'predictive': 'Predictive FlexProof'
    }

    for name in ['baseline', 'reactive', 'predictive']:
        if name in scenarios:
            df = scenarios[name]
            def_series = df['deficit_kw'] * dt_hours
            cum_def = def_series.cumsum()
            fig.add_trace(go.Scatter(
                x=cum_def.index,
                y=cum_def.values,
                name=labels.get(name, name),
                line=dict(color=colors.get(name, '#ffffff'), width=2.5),
                mode='lines'
            ))

    fig.update_layout(
        title="<b>Cumulative Deficit Energy Trajectory (30 Days)</b>",
        xaxis_title="Simulation Timeline",
        yaxis_title="Cumulative Deficit (kWh)",
        template="plotly_dark",
        height=350,
        margin=dict(l=40, r=20, t=45, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor='rgba(15, 23, 42, 0.7)',
        paper_bgcolor='rgba(15, 23, 42, 0.0)',
        hovermode="x unified"
    )
    fig.update_xaxes(showgrid=True, gridcolor='rgba(51, 65, 85, 0.4)')
    fig.update_yaxes(showgrid=True, gridcolor='rgba(51, 65, 85, 0.4)')
    return fig


def create_net_demand_timeline(scenarios: Dict[str, pd.DataFrame],
                                firm_limit_kw: float = 2300.0,
                                date_range=None) -> go.Figure:
    """Plot controlled net demand trajectories against the firm feeder limit."""
    fig = go.Figure()

    b_df = scenarios.get('baseline')
    r_df = scenarios.get('reactive')
    p_df = scenarios.get('predictive')

    if b_df is None or r_df is None or p_df is None:
        return fig

    if date_range is not None and len(date_range) == 2:
        start_date, end_date = date_range
        b_df = b_df.loc[start_date:end_date]
        r_df = r_df.loc[start_date:end_date]
        p_df = p_df.loc[start_date:end_date]

    fig.add_trace(go.Scatter(
        x=b_df.index, y=b_df['net_demand_kw'],
        name='Baseline Net Demand',
        line=dict(color='#ef4444', width=1.5, dash='dot'),
        opacity=0.7
    ))

    fig.add_trace(go.Scatter(
        x=r_df.index, y=r_df['controlled_net_demand_kw'],
        name='Reactive Controlled Demand',
        line=dict(color='#f59e0b', width=1.8),
        opacity=0.85
    ))

    fig.add_trace(go.Scatter(
        x=p_df.index, y=p_df['controlled_net_demand_kw'],
        name='Predictive Controlled Demand',
        line=dict(color='#10b981', width=2.2)
    ))

    # Firm Feeder Limit Line
    fig.add_hline(
        y=firm_limit_kw,
        line_dash="dash",
        line_color="#38bdf8",
        line_width=2,
        annotation_text=f"Firm Feeder Limit ({firm_limit_kw:,.0f} kW)",
        annotation_position="top left",
        annotation_font_color="#38bdf8"
    )

    fig.update_layout(
        title="<b>Feeder Net Demand vs. Capacity Limit Over Time</b>",
        xaxis_title="Time",
        yaxis_title="Power (kW)",
        template="plotly_dark",
        height=400,
        margin=dict(l=40, r=20, t=45, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor='rgba(15, 23, 42, 0.7)',
        paper_bgcolor='rgba(15, 23, 42, 0.0)',
        hovermode="x unified"
    )
    fig.update_xaxes(showgrid=True, gridcolor='rgba(51, 65, 85, 0.4)')
    fig.update_yaxes(showgrid=True, gridcolor='rgba(51, 65, 85, 0.4)')
    return fig


def render_scenario_scorecard(summary: Dict[str, Any]):
    """Render a clean, judge-friendly multi-scenario scorecard table."""
    render_comparative_kpi_table(summary)


def render_scenario_comparison_section(scenarios: Dict[str, pd.DataFrame],
                                        summary: Dict[str, Any],
                                        firm_limit_kw: float = 2300.0):
    """Render the full scenario comparison module with interactive controls."""
    st.subheader("⚡ 30-Day Multi-Scenario Grid Dynamics & Benchmark")

    # 2x2 Horizontal Benchmark Bars
    st.plotly_chart(create_scenario_benchmark_bars(summary), width="stretch")

    # Detailed Industrial Scorecard
    render_scenario_scorecard(summary)

    # Time window filter for deep drilldown
    timestamps = scenarios['baseline'].index
    min_date = timestamps.min().date()
    max_date = timestamps.max().date()

    col_ctrl1, col_ctrl2 = st.columns([2, 1])
    with col_ctrl1:
        date_sel = st.date_input(
            "Select Custom Date Window to Inspect",
            value=(min_date, min_date + pd.Timedelta(days=7)),
            min_value=min_date,
            max_value=max_date
        )
    with col_ctrl2:
        quick_pick = st.selectbox(
            "Quick Zoom Presets",
            ["Week 1 (Days 1-7)", "Week 2 (Days 8-14)", "Week 3 (Days 15-21)", "Week 4 (Days 22-28)", "All 30 Days"]
        )
        if quick_pick == "Week 1 (Days 1-7)":
            date_sel = (min_date, min_date + pd.Timedelta(days=6))
        elif quick_pick == "Week 2 (Days 8-14)":
            date_sel = (min_date + pd.Timedelta(days=7), min_date + pd.Timedelta(days=13))
        elif quick_pick == "Week 3 (Days 15-21)":
            date_sel = (min_date + pd.Timedelta(days=14), min_date + pd.Timedelta(days=20))
        elif quick_pick == "Week 4 (Days 22-28)":
            date_sel = (min_date + pd.Timedelta(days=21), min_date + pd.Timedelta(days=27))
        elif quick_pick == "All 30 Days":
            date_sel = (min_date, max_date)

    # Main timeline & cumulative deficit
    st.plotly_chart(create_net_demand_timeline(scenarios, firm_limit_kw, date_sel), width="stretch")
    st.plotly_chart(create_cumulative_deficit_chart(scenarios), width="stretch")
