"""Community battery storage and cycling burden visualization component for FlexProof."""
from typing import Dict, Any
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st


def create_battery_soc_timeline(scenarios: Dict[str, pd.DataFrame], 
                                min_soc: float = 0.50, 
                                max_soc: float = 0.90,
                                date_range=None) -> go.Figure:
    """Plot battery State of Charge (SOC) trajectories across scenarios."""
    fig = go.Figure()
    
    b_df = scenarios.get('baseline')
    r_df = scenarios.get('reactive')
    p_df = scenarios.get('predictive')
    
    if r_df is None or p_df is None:
        return fig
        
    if date_range is not None and len(date_range) == 2:
        start_date, end_date = date_range
        r_df = r_df.loc[start_date:end_date]
        p_df = p_df.loc[start_date:end_date]
        if b_df is not None:
            b_df = b_df.loc[start_date:end_date]
            
    if b_df is not None:
        fig.add_trace(go.Scatter(
            x=b_df.index, y=b_df['battery_soc'] * 100,
            name='Baseline SOC (Idle @ 70%)',
            line=dict(color='#94a3b8', width=1.5, dash='dot')
        ))
        
    fig.add_trace(go.Scatter(
        x=r_df.index, y=r_df['battery_soc'] * 100,
        name='Reactive SOC Trajectory',
        line=dict(color='#f59e0b', width=1.8),
        opacity=0.85
    ))
    
    fig.add_trace(go.Scatter(
        x=p_df.index, y=p_df['battery_soc'] * 100,
        name='Predictive FlexProof SOC',
        line=dict(color='#10b981', width=2.2)
    ))
    
    # Safe operating bounds
    fig.add_hline(
        y=max_soc * 100, line_dash="dash", line_color="#ef4444", line_width=1.5,
        annotation_text=f"Max Allowed Operating SOC ({max_soc*100:.0f}%)", annotation_position="top left"
    )
    fig.add_hline(
        y=min_soc * 100, line_dash="dash", line_color="#ef4444", line_width=1.5,
        annotation_text=f"Min Safe Operating SOC ({min_soc*100:.0f}%)", annotation_position="bottom left"
    )
    
    fig.update_layout(
        title="<b>Community Battery State of Charge (SOC %) Trajectory</b>",
        xaxis_title="Time",
        yaxis_title="Battery SOC (%)",
        yaxis=dict(range=[40, 100]),
        template="plotly_dark",
        height=380,
        margin=dict(l=40, r=20, t=40, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor='rgba(15, 23, 42, 0.6)',
        paper_bgcolor='rgba(15, 23, 42, 0.0)',
        hovermode="x unified"
    )
    return fig


def create_battery_action_distribution(p_df: pd.DataFrame, r_df: pd.DataFrame) -> go.Figure:
    """Compare battery operating action distributions (IDLE, CHARGING, DISCHARGING, RESERVED)."""
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Reactive Battery State Distribution", "Predictive Battery State Distribution"),
        specs=[[{"type": "domain"}, {"type": "domain"}]]
    )
    
    colors = {
        'IDLE': '#64748b',
        'CHARGING': '#38bdf8',
        'DISCHARGING': '#f59e0b',
        'RESERVED': '#10b981'
    }
    
    if 'battery_action' in r_df.columns:
        r_counts = r_df['battery_action'].value_counts()
        fig.add_trace(
            go.Pie(
                labels=r_counts.index, values=r_counts.values,
                hole=0.5,
                marker=dict(colors=[colors.get(k, '#94a3b8') for k in r_counts.index]),
                name="Reactive"
            ),
            row=1, col=1
        )
        
    if 'battery_action' in p_df.columns:
        p_counts = p_df['battery_action'].value_counts()
        fig.add_trace(
            go.Pie(
                labels=p_counts.index, values=p_counts.values,
                hole=0.5,
                marker=dict(colors=[colors.get(k, '#94a3b8') for k in p_counts.index]),
                name="Predictive"
            ),
            row=1, col=2
        )
        
    fig.update_layout(
        template="plotly_dark",
        height=300,
        margin=dict(l=20, r=20, t=40, b=20),
        plot_bgcolor='rgba(15, 23, 42, 0.0)',
        paper_bgcolor='rgba(15, 23, 42, 0.0)',
    )
    return fig


def render_battery_health_section(scenarios: Dict[str, pd.DataFrame], 
                                  config_battery: Any,
                                  summary: Dict[str, Any]):
    """Render the complete battery health and storage management section."""
    st.subheader("🔋 Community Battery Storage & Cycling Burden Analysis")
    
    r_thr = summary.get('reactive', {}).get('battery_throughput_kwh', 0.0)
    p_thr = summary.get('predictive', {}).get('battery_throughput_kwh', 0.0)
    thr_saving = summary.get('improvements', {}).get('battery_throughput_reduction_pct', 0.0)
    
    st.html(f"""
    <div style="background: rgba(139, 92, 246, 0.08); border-left: 4px solid #8b5cf6; padding: 14px 18px; border-radius: 6px; margin-bottom: 20px;">
        <span style="color: #c4b5fd; font-weight: 700; font-size: 1.05rem;">Cycling Burden Proxy & Storage Longevity Dividend:</span><br>
        <span style="color: #e2e8f0; font-size: 0.92rem; line-height: 1.5;">
        Predictive control protects the distribution feeder while reducing battery cycling burden relative to reactive control.
        Because <b>Reactive Control</b> lacks foresight, it relies heavily on sudden battery discharges to absorb unpredicted evening peaks (accumulating <b>{r_thr:,.1f} kWh</b> of throughput).<br>
        In contrast, <b>Predictive FlexProof</b> pre-shifts deferrable loads in advance, using storage only as a smooth precision buffer (accumulating <b>{p_thr:,.1f} kWh</b>, a <b>{thr_saving:.1f}% reduction in battery cycling burden</b>).
        </span>
    </div>
    """)
    
    min_soc = getattr(config_battery, 'min_soc', 0.50)
    max_soc = getattr(config_battery, 'max_soc', 0.90)
    
    st.plotly_chart(create_battery_soc_timeline(scenarios, min_soc, max_soc), width="stretch")
    
    if 'predictive' in scenarios and 'reactive' in scenarios:
        st.plotly_chart(create_battery_action_distribution(scenarios['predictive'], scenarios['reactive']), width="stretch")
