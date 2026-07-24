"""
app.py — entry point dashboard redesign.

Urutan pemanggilan mengikuti PRD section 7.1.1-7.1.5: set_page_config
dulu, load_css() sebagai baris pertama setelahnya, baru render komponen.
"""

import streamlit as st

st.set_page_config(
    page_title="Monitor Kualitas Udara Indonesia",
    layout="wide",
    initial_sidebar_state="expanded",
)

from utils.theme import load_css  # noqa: E402
from utils.data import load_all_readings, load_latest_per_city  # noqa: E402
from components.sidebar import render_sidebar, render_disabled_page_notice  # noqa: E402
from components.summary_cards import render_summary_cards  # noqa: E402
from components.map_view import render_map  # noqa: E402
from components.trend_chart import render_trend_chart  # noqa: E402
from components.live_conditions import render_live_conditions  # noqa: E402
from components.forecast_tab import render_forecast_tab  # noqa: E402

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
from config import CITIES  # noqa: E402


load_css()
current_page = render_sidebar()


def render_dashboard_page():
    df = load_all_readings()
    latest_df = load_latest_per_city()

    st.title("Monitor Kualitas Udara Indonesia")

    if df.empty:
        st.markdown(
            '<div class="glass-card empty-state">'
            '<div class="metric-label">Belum ada data</div>'
            '<div style="font-size:13px; margin-top:4px;">'
            'Pastikan data/air_quality.db ada dan sudah diisi src/fetch_data.py '
            '(jalankan git pull kalau data terbaru ada di GitHub tapi belum di lokal).'
            '</div></div>',
            unsafe_allow_html=True,
        )
        return

    last_update = df["datetime_wib"].max()
    st.caption(f"Update terakhir: {last_update.strftime('%Y-%m-%d %H:%M WIB')}")

    # --- 7.3 Kartu ringkasan ---
    render_summary_cards(latest_df, CITIES)

    # --- 7.7 Live Conditions (sparkline), section terpisah ---
    render_live_conditions(CITIES)

    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

    # --- 7.4 Peta ---
    st.markdown('<div class="metric-label" style="margin-bottom:8px;">Peta Sebaran AQI</div>', unsafe_allow_html=True)
    render_map(latest_df)

    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

    # --- 7.5 Grafik tren + 7.6 Tab prediksi ---
    selected_city = st.selectbox("Pilih kota untuk detail tren", list(CITIES.keys()))

    tab_trend, tab_forecast = st.tabs(["Tren Historis", "Prediksi"])
    with tab_trend:
        render_trend_chart(df, selected_city)
    with tab_forecast:
        render_forecast_tab(selected_city)

    st.markdown(
        f'<div style="color:var(--text-secondary); font-size:12px; margin-top:16px;">'
        f'Total {len(df)} baris data | Rentang: '
        f'{df["datetime_wib"].min().strftime("%Y-%m-%d")} — '
        f'{df["datetime_wib"].max().strftime("%Y-%m-%d")}</div>',
        unsafe_allow_html=True,
    )


if current_page == "dashboard":
    render_dashboard_page()
else:
    st.title(current_page.capitalize())
    render_disabled_page_notice(current_page)
