"""
components/live_conditions.py — sparkline per kota, section terpisah
dari kartu ringkasan (sesuai keputusan Anda).
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.data import load_city_history


def _make_sparkline_fig(values: pd.Series) -> go.Figure:
    fig = go.Figure(
        go.Scatter(
            y=values,
            mode="lines",
            line=dict(color="#6c8cff", width=2, shape="spline"),
        )
    )
    fig.update_layout(
        height=60,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        showlegend=False,
    )
    return fig


def render_live_conditions(cities: dict):
    st.markdown('<div class="metric-label" style="margin-bottom:8px;">Live Conditions</div>', unsafe_allow_html=True)

    cols = st.columns(len(cities))
    for col, city_name in zip(cols, cities.keys()):
        # Sparkline hanya butuh beberapa titik terakhir — query terpisah
        # dari load_all_readings supaya tidak duplikasi beban baca (task 7.7.3).
        history = load_city_history(city_name, limit_points=20)

        with col:
            st.markdown(
                f'<div class="glass-card" style="padding:12px;">'
                f'<div class="metric-label" style="font-size:10px;">{city_name}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
            if history.empty or len(history) < 2:
                st.caption("Data belum cukup")
            else:
                fig = _make_sparkline_fig(history["pm2_5"])
                st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
