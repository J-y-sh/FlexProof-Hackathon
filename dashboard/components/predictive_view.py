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
        subplot_titles=("1. Actual vs. Forecast Net Demand (kW)", "2. Predicted Feeder Capacity Stress Gap Over 2,300 kW Limit (kW)")
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
            name='1-Hr Ahead Forecast Net Demand (kW)',
            line=dict(color='#06b6d4', width=2, dash='dash')
        ),
        row=1, col=1
    )

    # Firm limit line
    fig.add_hline(
        y=firm_limit_kw, line_dash="dot", line_color="#ef4444", line_width=1.5,
        annotation_text=f"Firm Limit ({firm_limit_kw:,.0f} kW)",
        annotation_position="top left", annotation_font_color="#f87171",
        row=1, col=1
    )

    # 3. Forecast Gap
    fig.add_trace(
        go.Bar(
            x=sub_df.index, y=sub_df['forecast_gap_kw'],
            name='Predicted Stress Gap (kW)',
            marker_color='#f59e0b',
            opacity=0.85
        ),
        row=2, col=1
    )

    fig.update_layout(
        template="plotly_dark",
        height=450,
        margin=dict(l=40, r=20, t=40, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor='rgba(15, 23, 42, 0.7)',
        paper_bgcolor='rgba(15, 23, 42, 0.0)',
        hovermode="x unified"
    )
    fig.update_xaxes(showgrid=True, gridcolor='rgba(51, 65, 85, 0.4)')
    fig.update_yaxes(showgrid=True, gridcolor='rgba(51, 65, 85, 0.4)')
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
        textfont=dict(size=12, color="#ffffff")
    )])

    fig.update_layout(
        title="<b>Grid Risk State Classification Breakdown</b>",
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

    fig.add_vline(x=0, line_dash="dash", line_color="#10b981", annotation_text="Zero Error Baseline")

    fig.update_layout(
        title=f"<b>Forecast Error Residuals (MAE: {mae:.1f} kW | RMSE: {rmse:.1f} kW)</b>",
        xaxis_title="Prediction Error: (Forecast - Actual) kW",
        yaxis_title="Interval Count",
        template="plotly_dark",
        height=320,
        margin=dict(l=40, r=20, t=40, b=20),
        plot_bgcolor='rgba(15, 23, 42, 0.7)',
        paper_bgcolor='rgba(15, 23, 42, 0.0)',
    )
    fig.update_xaxes(showgrid=True, gridcolor='rgba(51, 65, 85, 0.4)')
    fig.update_yaxes(showgrid=True, gridcolor='rgba(51, 65, 85, 0.4)')
    return fig


def render_predictive_intelligence_section(predictive_df: pd.DataFrame,
                                            firm_limit_kw: float = 2300.0):
    """Render the full predictive intelligence view with conceptual narrative and plots."""
    st.subheader("🧠 Predictive Grid Intelligence & Lookahead Architecture")

    # 5-Stage Visual Workflow Pipeline
    st.html("""
    <div style="background: #0f172a; border: 1px solid #334155; border-radius: 8px; padding: 18px 20px; margin-bottom: 24px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; border-bottom: 1px solid #1e293b; padding-bottom: 8px;">
            <div style="font-size: 0.8rem; font-weight: 800; color: #38bdf8; text-transform: uppercase; letter-spacing: 0.06em;">
                The 5-Stage FlexProof Predictive Coordination Pipeline
            </div>
            <div style="font-size: 0.72rem; color: #94a3b8;">
                Deterministic Multi-Lag Lookahead • No Future Actual Data Leakage
            </div>
        </div>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 10px;">
            <!-- Stage 1 -->
            <div style="background: rgba(15, 23, 42, 0.8); border: 1px solid #334155; border-top: 3px solid #64748b; border-radius: 6px; padding: 12px 14px;">
                <div style="font-size: 0.7rem; color: #94a3b8; font-weight: 700; text-transform: uppercase;">01 • Telemetry</div>
                <div style="font-size: 0.95rem; color: #f8fafc; font-weight: 700; margin-top: 2px;">24-Hr Lookback</div>
                <div style="font-size: 0.78rem; color: #94a3b8; margin-top: 4px; line-height: 1.4;">96-interval buffer of demand, solar PV & diurnal ramp rates.</div>
            </div>
            <!-- Stage 2 -->
            <div style="background: rgba(15, 23, 42, 0.8); border: 1px solid #334155; border-top: 3px solid #06b6d4; border-radius: 6px; padding: 12px 14px;">
                <div style="font-size: 0.7rem; color: #67e8f9; font-weight: 700; text-transform: uppercase;">02 • Forecast</div>
                <div style="font-size: 0.95rem; color: #f8fafc; font-weight: 700; margin-top: 2px;">1-Hr Lookahead</div>
                <div style="font-size: 0.78rem; color: #94a3b8; margin-top: 4px; line-height: 1.4;">Multi-lag statistical regression projecting upcoming evening surge.</div>
            </div>
            <!-- Stage 3 -->
            <div style="background: rgba(15, 23, 42, 0.8); border: 1px solid #334155; border-top: 3px solid #f59e0b; border-radius: 6px; padding: 12px 14px;">
                <div style="font-size: 0.7rem; color: #fde68a; font-weight: 700; text-transform: uppercase;">03 • Risk Radar</div>
                <div style="font-size: 0.95rem; color: #f8fafc; font-weight: 700; margin-top: 2px;">Stress Gap Scan</div>
                <div style="font-size: 0.78rem; color: #94a3b8; margin-top: 4px; line-height: 1.4;">Quantifies deficit power over 2,300 kW firm limit into risk tiers.</div>
            </div>
            <!-- Stage 4 -->
            <div style="background: rgba(15, 23, 42, 0.8); border: 1px solid #334155; border-top: 3px solid #a855f7; border-radius: 6px; padding: 12px 14px;">
                <div style="font-size: 0.7rem; color: #d8b4fe; font-weight: 700; text-transform: uppercase;">04 • Prepare</div>
                <div style="font-size: 0.95rem; color: #f8fafc; font-weight: 700; margin-top: 2px;">Load Pre-Shift</div>
                <div style="font-size: 0.78rem; color: #94a3b8; margin-top: 4px; line-height: 1.4;">Pre-dispatches deferrable pumps & EV charging with 15–30 min lead time.</div>
            </div>
            <!-- Stage 5 -->
            <div style="background: rgba(15, 23, 42, 0.8); border: 1px solid #334155; border-top: 3px solid #10b981; border-radius: 6px; padding: 12px 14px;">
                <div style="font-size: 0.7rem; color: #6ee7b7; font-weight: 700; text-transform: uppercase;">05 • Dispatch</div>
                <div style="font-size: 0.95rem; color: #f8fafc; font-weight: 700; margin-top: 2px;">Precision Buffer</div>
                <div style="font-size: 0.78rem; color: #94a3b8; margin-top: 4px; line-height: 1.4;">Smooth battery dispatch absorbs fine residuals without heavy cell wear.</div>
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
