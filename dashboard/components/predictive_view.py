"""Predictive intelligence, forecasting, and lookahead architecture visualizations for FlexProof."""
from typing import Dict, Any
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st


def create_forecast_vs_actual_plot(df: pd.DataFrame, firm_limit_kw: float = 2300.0, sample_days: int = 5) -> go.Figure:
    """Plot actual net demand vs forecasted net demand and forecast gap."""
    # Select first N days after lookback (lookback is interval 96, day 2)
    start_idx = 96
    end_idx = min(len(df), start_idx + sample_days * 96)
    sub_df = df.iloc[start_idx:end_idx]
    
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        row_heights=[0.7, 0.3],
        subplot_titles=("Actual vs. Forecast Net Demand (kW)", "Predicted Feeder Stress Gap Over Firm Limit (kW)")
    )
    
    # 1. Actual Net Demand
    fig.add_trace(
        go.Scatter(
            x=sub_df.index, y=sub_df['net_demand_kw'],
            name='Actual Net Demand (kW)',
            line=dict(color='#94a3b8', width=2)
        ),
        row=1, col=1
    )
    
    # 2. Forecast Net Demand
    fig.add_trace(
        go.Scatter(
            x=sub_df.index, y=sub_df['forecast_net_demand_kw'],
            name='Forecast Net Demand (kW)',
            line=dict(color='#06b6d4', width=2, dash='dash')
        ),
        row=1, col=1
    )
    
    # Firm limit line
    fig.add_hline(
        y=firm_limit_kw, line_dash="dot", line_color="#ef4444", line_width=1.5,
        annotation_text="Firm Feeder Limit (2300 kW)",
        annotation_position="top left",
        row=1, col=1
    )
    
    # 3. Forecast Gap
    fig.add_trace(
        go.Bar(
            x=sub_df.index, y=sub_df['forecast_gap_kw'],
            name='Forecast Gap (kW)',
            marker_color='#f59e0b',
            opacity=0.8
        ),
        row=2, col=1
    )
    
    fig.update_layout(
        template="plotly_dark",
        height=450,
        margin=dict(l=40, r=20, t=40, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor='rgba(15, 23, 42, 0.6)',
        paper_bgcolor='rgba(15, 23, 42, 0.0)',
        hovermode="x unified"
    )
    return fig


def create_risk_level_distribution(df: pd.DataFrame) -> go.Figure:
    """Create a donut chart of risk level classifications across all simulation intervals."""
    if 'risk_level' not in df.columns:
        return go.Figure()
        
    counts = df['risk_level'].value_counts()
    colors = {
        'NORMAL': '#10b981',
        'WATCH': '#06b6d4',
        'WARNING': '#f59e0b',
        'CRITICAL': '#ef4444'
    }
    
    color_seq = [colors.get(k, '#94a3b8') for k in counts.index]
    
    fig = go.Figure(data=[go.Pie(
        labels=counts.index,
        values=counts.values,
        hole=0.55,
        marker=dict(colors=color_seq),
        textinfo='label+percent',
        textfont_size=12
    )])
    
    fig.update_layout(
        title="<b>Grid Risk Classification Breakdown</b>",
        template="plotly_dark",
        height=320,
        margin=dict(l=20, r=20, t=40, b=20),
        plot_bgcolor='rgba(15, 23, 42, 0.0)',
        paper_bgcolor='rgba(15, 23, 42, 0.0)',
    )
    return fig


def create_forecast_error_residuals(df: pd.DataFrame) -> go.Figure:
    """Plot forecast error residuals distribution."""
    if 'forecast_net_demand_kw' not in df.columns:
        return go.Figure()
        
    valid = df['forecast_net_demand_kw'] > 0
    residuals = df.loc[valid, 'forecast_net_demand_kw'] - df.loc[valid, 'net_demand_kw']
    
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=residuals,
        nbinsx=40,
        marker_color='#38bdf8',
        opacity=0.75,
        name='Forecast Error (kW)'
    ))
    
    mae = residuals.abs().mean()
    rmse = np.sqrt((residuals**2).mean())
    
    fig.add_vline(x=0, line_dash="dash", line_color="#10b981", annotation_text="Zero Error")
    
    fig.update_layout(
        title=f"<b>Forecast Error Residuals (MAE: {mae:.1f} kW | RMSE: {rmse:.1f} kW)</b>",
        xaxis_title="Prediction Error: (Forecast - Actual) kW",
        yaxis_title="Interval Count",
        template="plotly_dark",
        height=320,
        margin=dict(l=40, r=20, t=40, b=20),
        plot_bgcolor='rgba(15, 23, 42, 0.6)',
        paper_bgcolor='rgba(15, 23, 42, 0.0)',
    )
    return fig


def render_predictive_intelligence_section(predictive_df: pd.DataFrame, 
                                            firm_limit_kw: float = 2300.0):
    """Render the full predictive intelligence view with conceptual narrative and plots."""
    st.subheader("🧠 Predictive Grid Intelligence & Lookahead Radar")
    
    # 5-Stage Visual Workflow Pipeline
    st.html("""
    <div style="background: linear-gradient(90deg, #0f172a 0%, #1e293b 100%); border: 1px solid #334155; border-radius: 8px; padding: 16px 20px; margin-bottom: 20px;">
        <div style="font-size: 0.8rem; font-weight: 700; color: #38bdf8; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 8px;">
            The 5-Stage FlexProof Predictive Pipeline
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
            <div style="background: rgba(148, 163, 184, 0.1); border: 1px solid #475569; border-radius: 6px; padding: 8px 12px; text-align: center; flex: 1; min-width: 130px;">
                <div style="font-size: 0.75rem; color: #94a3b8; font-weight: 600;">1. TELEMETRY</div>
                <div style="font-size: 0.85rem; color: #f8fafc; font-weight: 700;">Historical Lags</div>
            </div>
            <div style="color: #64748b; font-size: 1.2rem;">→</div>
            <div style="background: rgba(6, 182, 212, 0.15); border: 1px solid #06b6d4; border-radius: 6px; padding: 8px 12px; text-align: center; flex: 1; min-width: 130px;">
                <div style="font-size: 0.75rem; color: #67e8f9; font-weight: 600;">2. FORECAST</div>
                <div style="font-size: 0.85rem; color: #f8fafc; font-weight: 700;">1-Hr Lookahead</div>
            </div>
            <div style="color: #64748b; font-size: 1.2rem;">→</div>
            <div style="background: rgba(245, 158, 11, 0.15); border: 1px solid #f59e0b; border-radius: 6px; padding: 8px 12px; text-align: center; flex: 1; min-width: 130px;">
                <div style="font-size: 0.75rem; color: #fde68a; font-weight: 600;">3. RISK RADAR</div>
                <div style="font-size: 0.85rem; color: #f8fafc; font-weight: 700;">Gap & Severity</div>
            </div>
            <div style="color: #64748b; font-size: 1.2rem;">→</div>
            <div style="background: rgba(139, 92, 246, 0.15); border: 1px solid #8b5cf6; border-radius: 6px; padding: 8px 12px; text-align: center; flex: 1; min-width: 130px;">
                <div style="font-size: 0.75rem; color: #c4b5fd; font-weight: 600;">4. PREPARE</div>
                <div style="font-size: 0.85rem; color: #f8fafc; font-weight: 700;">Pre-Shift & Reserve</div>
            </div>
            <div style="color: #64748b; font-size: 1.2rem;">→</div>
            <div style="background: rgba(16, 185, 129, 0.15); border: 1px solid #10b981; border-radius: 6px; padding: 8px 12px; text-align: center; flex: 1; min-width: 130px;">
                <div style="font-size: 0.75rem; color: #6ee7b7; font-weight: 600;">5. DISPATCH</div>
                <div style="font-size: 0.85rem; color: #f8fafc; font-weight: 700;">Smooth Buffering</div>
            </div>
        </div>
    </div>
    """)
    
    # Forecast vs actual plot
    st.plotly_chart(create_forecast_vs_actual_plot(predictive_df, firm_limit_kw), width="stretch")
    
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(create_risk_level_distribution(predictive_df), width="stretch")
    with col2:
        st.plotly_chart(create_forecast_error_residuals(predictive_df), width="stretch")
