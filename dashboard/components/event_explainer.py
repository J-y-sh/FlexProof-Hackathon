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
    """Create a high-resolution synchronized multi-trace timeline around a specific stress event."""
    start_ts = center_ts - pd.Timedelta(hours=window_hours)
    end_ts = center_ts + pd.Timedelta(hours=window_hours)
    
    b_sub = scenarios['baseline'].loc[start_ts:end_ts]
    r_sub = scenarios['reactive'].loc[start_ts:end_ts]
    p_sub = scenarios['predictive'].loc[start_ts:end_ts]
    
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.06,
        row_heights=[0.50, 0.25, 0.25],
        subplot_titles=(
            "1. Feeder Net Demand & Peak Overload Breaches (kW)",
            "2. Flexibility Dispatch & Pre-Shifting Power (kW)",
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
        annotation_text=f"Firm Limit ({firm_limit_kw:,.0f} kW)", row=1, col=1
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
    
    fig.update_layout(
        template="plotly_dark",
        height=560,
        margin=dict(l=40, r=20, t=40, b=30),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor='rgba(15, 23, 42, 0.6)',
        paper_bgcolor='rgba(15, 23, 42, 0.0)',
        hovermode="x unified"
    )
    return fig


def render_event_explainer_section(scenarios: Dict[str, pd.DataFrame], 
                                   events: Dict[str, pd.DataFrame],
                                   firm_limit_kw: float = 2300.0):
    """Render the interactive event replay and explainability tool."""
    st.subheader("🔍 Stress Event Replay & Control Causality Drill-Down")
    
    top_events = find_top_stress_events(scenarios['baseline'], firm_limit_kw)
    if not top_events:
        st.info("No feeder stress events identified in baseline simulation.")
        return
        
    event_options = [
        f"{e['peak_time'].strftime('%b %d, %Y (%a) %H:%M')} — Peak Overload: {e['max_deficit_kw']:.1f} kW (Total: {e['total_deficit_kwh']:.1f} kWh)"
        for e in top_events
    ]
    
    col_sel1, col_sel2 = st.columns([3, 1])
    with col_sel1:
        # Default to strongest event (index 0)
        sel_idx = st.selectbox(
            "Select Real Feeder Stress Event to Replay:",
            range(len(event_options)),
            index=0,
            format_func=lambda x: event_options[x]
        )
    with col_sel2:
        window_hrs = st.slider("Replay Window (± Hours)", min_value=1.5, max_value=6.0, value=3.0, step=0.5)
        
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
    
    # Render synchronized multi-subplot timeline
    st.plotly_chart(create_event_replay_plot(scenarios, center_time, window_hrs, firm_limit_kw), width="stretch")
    
    # Dynamic Causality Narrative Box
    st.markdown("#### 🔬 Dynamic Event Causality & Decision Audit")
    
    st.html(f"""
    <div style="background: rgba(15, 23, 42, 0.9); border: 1px solid #334155; border-radius: 8px; padding: 16px 20px; margin-bottom: 20px;">
        <div style="font-size: 0.85rem; color: #38bdf8; font-weight: 700; text-transform: uppercase;">
            Peak Event Analysis @ {center_time.strftime('%Y-%m-%d %H:%M')}
        </div>
        <p style="font-size: 0.95rem; color: #f1f5f9; line-height: 1.6; margin-top: 8px; margin-bottom: 0;">
            • <b>Baseline:</b> Unmanaged net demand peaked at <b>{b_nd:,.1f} kW</b>, exceeding the firm capacity by <span style="color: #f87171;"><b>{b_def:,.1f} kW</b></span>.<br>
            • <b>Reactive:</b> Responded only after detecting the limit breach. Actuator response lags in pumps restricted immediate relief, leaving controlled demand at <b>{r_nd:,.1f} kW</b> (<span style="color: #fbbf24;"><b>{r_def:,.1f} kW</b></span> residual deficit).<br>
            • <b>Predictive FlexProof:</b> Anticipated the peak 1 hour ahead, pre-shifted deferrable loads, and reserved battery capacity, maintaining controlled demand at <span style="color: #34d399;"><b>{p_nd:,.1f} kW</b></span> (<span style="color: #34d399;"><b>{p_def:,.1f} kW</b></span> deficit).
        </p>
    </div>
    """)
    
    col_e1, col_e2 = st.columns(2)
    
    with col_e1:
        st.html("""
        <div style="background: rgba(245, 158, 11, 0.06); border: 1px solid rgba(245, 158, 11, 0.4); border-radius: 8px; padding: 14px 16px;">
            <h5 style="color: #fbbf24; margin-top: 0; margin-bottom: 8px;">🟡 Reactive Control Bottlenecks</h5>
            <ul style="font-size: 0.88rem; color: #cbd5e1; padding-left: 18px; margin-bottom: 0;">
                <li><b>Zero Advance Notice:</b> Controller stayed idle until the overload occurred.</li>
                <li><b>Actuator Lag Trap:</b> Water pumps and agricultural wells require 15–30 min response time, preventing immediate relief.</li>
                <li><b>Emergency Battery Stress:</b> Forced high discharge to compensate, accelerating cell throughput burden.</li>
            </ul>
        </div>
        """)
        
    with col_e2:
        st.html("""
        <div style="background: rgba(16, 185, 129, 0.06); border: 1px solid rgba(16, 185, 129, 0.4); border-radius: 8px; padding: 14px 16px;">
            <h5 style="color: #34d399; margin-top: 0; margin-bottom: 8px;">🟢 Predictive FlexProof Advantages</h5>
            <ul style="font-size: 0.88rem; color: #cbd5e1; padding-left: 18px; margin-bottom: 0;">
                <li><b>1-Hour Advance Lookahead:</b> Forecasted the evening ramp from historical lag patterns.</li>
                <li><b>Advance Pre-Dispatch:</b> Pre-shifted pumps and EV chargers with lead time, overcoming actuator response lags.</li>
                <li><b>Precision Storage Buffering:</b> Coordinated storage gently as a fine-tuning buffer, saving battery life.</li>
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
            st.html("<div style='margin-bottom: 16px;'></div>")
            with st.expander(f"📋 View Active Controller Decision Audit Log ({len(sub_events)} events in window)"):
                st.dataframe(
                    sub_events[['timestamp', 'decision', 'reason', 'resource_selected', 'power_delivered_kw', 'battery_soc_before', 'battery_soc_after']],
                    width="stretch"
                )
