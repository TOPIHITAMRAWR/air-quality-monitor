"""
components/summary_cards.py — kartu ringkasan AQI per kota (task 7.3).
"""

import pandas as pd
import streamlit as st

from utils.theme import get_aqi_badge


def render_summary_cards(latest_df: pd.DataFrame, cities: dict):
    """Grid kartu AQI, satu per kota, pakai CSS grid (bukan st.columns)."""
    cards_html = []

    for city_name in cities.keys():
        row = latest_df[latest_df["city"] == city_name] if not latest_df.empty else pd.DataFrame()

        if row.empty:
            cards_html.append(
                f'<div class="glass-card">'
                f'<div class="metric-label">{city_name}</div>'
                f'<div class="metric-value" style="font-size:28px;">N/A</div>'
                f'</div>'
            )
            continue

        aqi_val = row.iloc[0]["aqi"]
        pm25_val = row.iloc[0]["pm2_5"]
        label, css_class, _ = get_aqi_badge(aqi_val)

        cards_html.append(
            f'<div class="glass-card">'
            f'<div class="metric-label">{city_name}</div>'
            f'<div class="metric-value">{int(aqi_val)}</div>'
            f'<span class="badge {css_class}">{label}</span>'
            f'<div style="color:var(--text-secondary); font-size:12px; margin-top:8px;">'
            f'PM2.5: {pm25_val:.1f} µg/m³</div>'
            f'</div>'
        )

    st.markdown(
        f'<div class="card-grid">{"".join(cards_html)}</div>',
        unsafe_allow_html=True,
    )
