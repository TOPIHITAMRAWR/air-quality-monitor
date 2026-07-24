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
        height=420,
    )
    fig.update_layout(
        mapbox_style="carto-darkmatter",
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color="#9aa4b8"),
        ),
    )

    st.markdown('<div class="glass-card" style="padding:8px;">', unsafe_allow_html=True)
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)
