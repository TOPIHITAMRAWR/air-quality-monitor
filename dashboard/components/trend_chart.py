"""
components/trend_chart.py — grafik tren historis PM2.5, tema gelap (task 7.5).
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


def render_trend_chart(df: pd.DataFrame, city: str):
    """Line chart PM2.5 dengan area fill gradient tipis, transparan menyatu ke glass card."""
    city_df = df[df["city"] == city].sort_values("datetime_wib") if not df.empty else pd.DataFrame()

    if city_df.empty:
        st.markdown(
            '<div class="glass-card empty-state">'
            f'<div class="metric-label">Belum ada data historis untuk {city}</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        return

    current_value = city_df.iloc[-1]["pm2_5"]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=city_df["datetime_wib"],
            y=city_df["pm2_5"],
            mode="lines",
            line=dict(color="#e8823c", width=2.5, shape="spline"),
            fill="tozeroy",
            fillcolor="rgba(232, 130, 60, 0.15)",
            hovertemplate="%{x|%d %b %H:%M}<br>PM2.5: %{y:.1f} µg/m³<extra></extra>",
        )
    )
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#c9a98a"),
        margin=dict(l=10, r=10, t=10, b=10),
        height=200,
        xaxis=dict(showgrid=False, showline=False, title=None),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(255,255,255,0.06)",
            showline=False,
            title=None,
        ),
        showlegend=False,
    )

    st.markdown(
        f'<div class="glass-card">'
        f'<div class="metric-label">PM2.5 — {city}</div>'
        f'<div class="metric-value" style="font-size:32px;">{current_value:.1f}'
        f'<span style="font-size:14px; color:var(--text-secondary);"> µg/m³</span></div>'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
