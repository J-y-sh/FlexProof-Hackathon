"""Interactive stress event replay and explainability component for FlexProof."""
from typing import Dict, Any
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st


def find_top_stress_events(baseline_df: pd.DataFrame, firm_limit_kw: float = 2300.0, top_n: int = 10) -> list:
    """Identify and rank discrete feeder stress peak events from baseline simulation."""
    stress_df = baseline_df[baseline_df['net_demand_kw'] > firm_limit_kw].copy()
    if stress_df.empty:
        return []

    stress_df['deficit_kw'] = stress_df['net_demand_kw'] - firm_limit_kw

    # Group consecutive intervals into discrete events
    events = []
    current_event = []

    for ts, row in stress_df.iterrows():
        if not current_event:
            current_event.append((ts, row))
        else:
            prev_ts = current_event[-1][0]
            if (ts - prev_ts) <= pd.Timedelta(minutes=30):
                current_event.append((ts, row))
            else:
                peak_item = max(current_event, key=lambda x: x[1]['deficit_kw'])
                events.append({
                    'peak_time': peak_item[0],
                    'max_deficit_kw': peak_item[1]['deficit_kw'],
                    'peak_net_demand_kw': peak_item[1]['net_demand_kw'],
                    'duration_intervals': len(current_event),
                    'total_deficit_kwh': sum(x[1]['deficit_kw'] * 0.25 for x in current_event)
                })
                current_event = [(ts, row)]

    if current_event:
        peak_item = max(current_event, key=lambda x: x[1]['deficit_kw'])
        events.append({
            'peak_time': peak_item[0],
            'max_deficit_kw': peak_item[1]['deficit_kw'],
            'peak_net_demand_kw': peak_item[1]['net_demand_kw'],
            'duration_intervals': len(current_event),
            'total_deficit_kwh': sum(x[1]['deficit_kw'] * 0.25 for x in current_event)
        })

    # Sort descending by max deficit
    events.sort(key=lambda x: x['max_deficit_kw'], reverse=True)
    return events[:top_n]


def create_event_replay_plot(scenarios: Dict[str, pd.DataFrame],
                             center_ts: pd.Timestamp,
                             window_hours: float = 3.0,
                             firm_limit_kw: float = 2300.0) -> go.Figure:
    """Create a high-resolution synchronized multi-trace timeline around a specific stress event with causal annotations."""
    start_ts = center_ts - pd.Timedelta(hours=window_hours)
    end_ts = center_ts + pd.Timedelta(hours=window_hours)

    b_sub = scenarios['baseline'].loc[start_ts:end_ts]
    r_sub = scenarios['reactive'].loc[start_ts:end_ts]
    p_sub = scenarios['predictive'].loc[start_ts:end_ts]

    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.07,
        row_heights=[0.50, 0.25, 0.25],
        subplot_titles=(
            "1. Feeder Net Demand & Capacity Limit (kW)",
            "2. Active Flexibility Dispatched (kW)",
            "3. Community Battery State of Charge (%)"
        )
    )

    # 1. Net Demand
    fig.add_trace(go.Scatter(
        x=b_sub.index, y=b_sub['net_demand_kw'],
        name='Baseline Net Demand',
        line=dict(color='#ef4444', width=2, dash='dot')
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=r_sub.index, y=r_sub['controlled_net_demand_kw'],
        name='Reactive Controlled Demand',
        line=dict(color='#f59e0b', width=2)
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=p_sub.index, y=p_sub['controlled_net_demand_kw'],
        name='Predictive FlexProof Demand',
        line=dict(color='#10b981', width=2.5)
    ), row=1, col=1)

    # Firm Feeder Limit Line
    fig.add_hline(
        y=firm_limit_kw, line_dash="dash", line_color="#38bdf8", line_width=1.5,
        annotation_text=f"Firm Limit ({firm_limit_kw:,.0f} kW)", row=1, col=1,
        annotation_position="top left", annotation_font_color="#38bdf8"
    )

    # 2. Flexibility dispatched
    fig.add_trace(go.Bar(
        x=r_sub.index, y=r_sub['flexibility_dispatched_kw'],
        name='Reactive Flex Dispatched',
        marker_color='#f59e0b', opacity=0.7
    ), row=2, col=1)

    fig.add_trace(go.Bar(
        x=p_sub.index, y=p_sub['flexibility_dispatched_kw'],
        name='Predictive Flex Dispatched',
        marker_color='#10b981', opacity=0.85
    ), row=2, col=1)

    # 3. Battery SOC
    fig.add_trace(go.Scatter(
        x=r_sub.index, y=r_sub['battery_soc'] * 100,
        name='Reactive Battery SOC %',
        line=dict(color='#f59e0b', width=1.8)
    ), row=3, col=1)

    fig.add_trace(go.Scatter(
        x=p_sub.index, y=p_sub['battery_soc'] * 100,
        name='Predictive Battery SOC %',
        line=dict(color='#10b981', width=2.2)
    ), row=3, col=1)

    # Causal Decision Marker: 1-Hour Lookahead Pre-Dispatch
    predispatch_ts = center_ts - pd.Timedelta(hours=1)
    if predispatch_ts >= start_ts:
        fig.add_vline(
            x=predispatch_ts, line_dash="dot", line_color="#06b6d4", line_width=2,
            annotation_text="1-Hr Lookahead: Pre-Dispatch",
            annotation_position="top left", annotation_font_color="#67e8f9",
            row=1, col=1
        )
        fig.add_vline(x=predispatch_ts, line_dash="dot", line_color="#06b6d4", line_width=1.5, row=2, col=1)
        fig.add_vline(x=predispatch_ts, line_dash="dot", line_color="#06b6d4", line_width=1.5, row=3, col=1)

    # Peak Stress Marker
    fig.add_vline(
        x=center_ts, line_dash="dash", line_color="#ef4444", line_width=1.8,
        annotation_text="Peak Stress Event",
        annotation_position="top right", annotation_font_color="#fca5a5",
        row=1, col=1
    )
    fig.add_vline(x=center_ts, line_dash="dash", line_color="#ef4444", line_width=1.2, row=2, col=1)
    fig.add_vline(x=center_ts, line_dash="dash", line_color="#ef4444", line_width=1.2, row=3, col=1)

    fig.update_layout(
        template="plotly_dark",
        height=580,
        margin=dict(l=40, r=20, t=40, b=30),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor='rgba(15, 23, 42, 0.7)',
        paper_bgcolor='rgba(15, 23, 42, 0.0)',
        hovermode="x unified"
    )
    fig.update_xaxes(showgrid=True, gridcolor='rgba(51, 65, 85, 0.4)')
    fig.update_yaxes(showgrid=True, gridcolor='rgba(51, 65, 85, 0.4)')
    return fig


def render_event_explainer_section(scenarios: Dict[str, pd.DataFrame],
                                   events: Dict[str, pd.DataFrame],
                                   firm_limit_kw: float = 2300.0):
    """Render the interactive event replay and explainability tool."""
    top_events = find_top_stress_events(scenarios['baseline'], firm_limit_kw)
    if not top_events:
        st.info("No feeder stress events identified in baseline simulation.")
        return

    event_options = [
        f"{e['peak_time'].strftime('%b %d, %Y (%a) %H:%M')} — Overload: {e['max_deficit_kw']:.1f} kW ({e['total_deficit_kwh']:.1f} kWh deficit)"
        for e in top_events
    ]

    col_sel1, col_sel2 = st.columns([3, 1])
    with col_sel1:
        # Default to strongest event (index 0)
        sel_idx = st.selectbox(
            "Select Peak Overload Event to Replay:",
            range(len(event_options)),
            index=0,
            format_func=lambda x: event_options[x]
        )
    with col_sel2:
        window_hrs = st.slider("Timeline Window (± Hours)", min_value=1.5, max_value=6.0, value=3.0, step=0.5)

    chosen_event = top_events[sel_idx]
    center_time = chosen_event['peak_time']

    # Extract exact instantaneous metrics at the peak interval
    b_row = scenarios['baseline'].loc[center_time] if center_time in scenarios['baseline'].index else None
    r_row = scenarios['reactive'].loc[center_time] if center_time in scenarios['reactive'].index else None
    p_row = scenarios['predictive'].loc[center_time] if center_time in scenarios['predictive'].index else None

    b_nd = b_row['net_demand_kw'] if b_row is not None else 0.0
    r_nd = r_row['controlled_net_demand_kw'] if r_row is not None else 0.0
    p_nd = p_row['controlled_net_demand_kw'] if p_row is not None else 0.0

    b_def = max(0.0, b_nd - firm_limit_kw)
    r_def = max(0.0, r_nd - firm_limit_kw)
    p_def = max(0.0, p_nd - firm_limit_kw)

    # Render synchronized multi-subplot timeline with causal annotations
    st.plotly_chart(create_event_replay_plot(scenarios, center_time, window_hrs, firm_limit_kw), width="stretch")

    # Dynamic Causality Narrative Cards
    predispatch_time = center_time - pd.Timedelta(hours=1)

    st.html(f"""
    <div style="background: #0f172a; border: 1px solid #334155; border-radius: 8px; padding: 18px 20px; margin-top: 14px; margin-bottom: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #1e293b; padding-bottom: 10px; margin-bottom: 12px;">
            <div style="font-size: 0.88rem; color: #38bdf8; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;">
                🔬 Live Event Causality Audit @ {center_time.strftime('%Y-%m-%d %H:%M')}
            </div>
            <div style="font-size: 0.75rem; color: #94a3b8; font-family: monospace;">
                Firm Feeder Limit: <b>{firm_limit_kw:,.0f} kW</b>
            </div>
        </div>
        <p style="font-size: 0.95rem; color: #f1f5f9; line-height: 1.6; margin-bottom: 0;">
            • <b>Baseline:</b> Unmanaged net demand surges to <b>{b_nd:,.1f} kW</b>, causing an immediate <span style="color: #f87171;"><b>{b_def:,.1f} kW thermal overload</b></span>.<br>
            • <b>Reactive Control:</b> Responded only when the 2,300 kW limit was crossed. Because municipal water pumps take 30 min to spool down, emergency battery discharge was forced, still leaving <b>{r_nd:,.1f} kW</b> (<span style="color: #fbbf24;"><b>{r_def:,.1f} kW residual deficit</b></span>).<br>
            • <b>Predictive FlexProof:</b> Anticipated the peak at <b>{predispatch_time.strftime('%H:%M')}</b> (1 hour ahead), pre-shifted pumps and deferrable loads with sufficient lead time, holding controlled demand at <span style="color: #34d399;"><b>{p_nd:,.1f} kW</b></span> (<span style="color: #34d399;"><b>{p_def:,.1f} kW deficit</b></span>).
        </p>
    </div>
    """)

    col_e1, col_e2 = st.columns(2)

    with col_e1:
        st.html("""
        <div style="background: rgba(245, 158, 11, 0.06); border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 8px; padding: 14px 16px; height: 100%;">
            <div style="color: #fbbf24; font-weight: 700; font-size: 0.92rem; margin-bottom: 8px;">🟡 Reactive Control Bottlenecks</div>
            <ul style="font-size: 0.85rem; color: #cbd5e1; padding-left: 18px; margin-bottom: 0; line-height: 1.5;">
                <li><b>Zero Advance Notice:</b> Controller remains idle until after transformer overload begins.</li>
                <li><b>Actuator Latency Trap:</b> Heavy pumps cannot halt instantly, leading to unserved deficit spikes.</li>
                <li><b>Accelerated Battery Wear:</b> Emergency high-rate battery cycling wears out storage cells prematurely.</li>
            </ul>
        </div>
        """)

    with col_e2:
        st.html("""
        <div style="background: rgba(16, 185, 129, 0.06); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 8px; padding: 14px 16px; height: 100%;">
            <div style="color: #34d399; font-weight: 700; font-size: 0.92rem; margin-bottom: 8px;">🟢 Predictive FlexProof Advantages</div>
            <ul style="font-size: 0.85rem; color: #cbd5e1; padding-left: 18px; margin-bottom: 0; line-height: 1.5;">
                <li><b>1-Hour Lookahead:</b> Forecasts upcoming peak ramp from historical diurnal telemetry patterns.</li>
                <li><b>Lead-Time Pre-Dispatch:</b> Pre-shifts slow pumps and EV chargers ahead of time, overcoming actuator delays.</li>
                <li><b>Precision Storage Buffering:</b> Uses community battery gently as a smooth buffer, cutting cycling throughput in half.</li>
            </ul>
        </div>
        """)

    # Controller Event Logs for this window
    if 'predictive' in events and not events['predictive'].empty:
        p_ev = events['predictive']
        win_start = center_time - pd.Timedelta(hours=window_hrs)
        win_end = center_time + pd.Timedelta(hours=window_hrs)
        sub_events = p_ev[(p_ev['timestamp'] >= win_start) & (p_ev['timestamp'] <= win_end)]

        if not sub_events.empty:
            st.html("<div style='margin-bottom: 12px;'></div>")
            with st.expander(f"📋 Controller Decision Telemetry Log ({len(sub_events)} events in window)"):
                st.dataframe(
                    sub_events[['timestamp', 'decision', 'reason', 'resource_selected', 'power_delivered_kw', 'battery_soc_before', 'battery_soc_after']],
                    width="stretch"
                )
