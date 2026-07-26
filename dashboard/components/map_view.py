"""
components/map_view.py — peta sebaran AQI, basemap gelap (task 7.4).

carto-darkmatter dipakai karena tidak butuh Mapbox token (tetap 100% gratis),
sesuai catatan risiko section 4 baris ketiga.
"""

import pandas as pd
import plotly.express as px
import streamlit as st

from utils.theme import get_aqi_badge


def render_map(latest_df: pd.DataFrame):
    if latest_df.empty:
        st.markdown(
            '<div class="glass-card empty-state">'
            '<div class="metric-label">Belum ada data untuk ditampilkan di peta</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        return

    map_df = latest_df.copy()
    map_df["kategori"] = map_df["aqi"].apply(lambda x: get_aqi_badge(x)[0])
    # Warna konsisten dengan badge kartu ringkasan (Definition of Done #2)
    color_map = {
        "Baik": "#2ecc71",
        "Sedang": "#2ecc71",
        "Tidak Sehat bagi Sensitif": "#f39c12",
        "Tidak Sehat": "#e74c3c",
        "Sangat Tidak Sehat": "#e74c3c",
        "N/A": "#888888",
    }

    fig = px.scatter_mapbox(
        map_df,
        lat="lat",
        lon="lon",
        color="kategori",
        size="pm2_5",
        hover_name="city",
        hover_data={"aqi": True, "pm2_5": True, "lat": False, "lon": False},
        color_discrete_map=color_map,
        zoom=3.5,
        height=320,
    )
    fig.update_layout(
        mapbox_style="carto-darkmatter",
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color="#c9a98a"),
        ),
    )

    # FIX: sebelumnya pakai trik buka <div> di satu st.markdown lalu tutup
    # di st.markdown lain, dengan st.plotly_chart di antaranya. Ternyata
    # tidak konsisten (kadang chart dirender di luar div). st.container(
    # border=True) adalah wadah SUNGGUHAN dari Streamlit, dijamin
    # membungkus konten di dalamnya — styling-nya diatur lewat CSS
    # selector [data-testid="stVerticalBlockBorderWrapper"] di style.css.
    with st.container(border=True):
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
