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
            line=dict(color="#e8823c", width=2, shape="spline"),
        )
    )
    fig.update_layout(
        height=45,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        showlegend=False,
    )
    return fig


def render_live_conditions(cities: dict):
    st.markdown('<div class="metric-label" style="margin-bottom:6px;">Live Conditions</div>', unsafe_allow_html=True)

    cols = st.columns(len(cities))
    for col, city_name in zip(cols, cities.keys()):
        # Sparkline hanya butuh beberapa titik terakhir — query terpisah
        # dari load_all_readings supaya tidak duplikasi beban baca (task 7.7.3).
        history = load_city_history(city_name, limit_points=20)

        with col:
            # FIX: sebelumnya label & chart dua elemen terpisah tanpa
            # pembungkus (bare chart, terlihat polos). Sekarang satu
            # container sungguhan (st.container(border=True)) berisi
            # label + nilai terkini + sparkline sekaligus.
            with st.container(border=True):
                st.markdown(
                    f'<div class="metric-label" style="font-size:10px;">{city_name}</div>',
                    unsafe_allow_html=True,
                )
                if history.empty or len(history) < 2:
                    st.caption("Data belum cukup")
                else:
                    current_val = history.iloc[-1]["pm2_5"]
                    st.markdown(
                        f'<div style="font-size:18px; font-weight:700; '
                        f'color:var(--text-primary);">{current_val:.1f}'
                        f'<span style="font-size:10px; color:var(--text-secondary);"> µg/m³</span></div>',
                        unsafe_allow_html=True,
                    )
                    fig = _make_sparkline_fig(history["pm2_5"])
                    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
