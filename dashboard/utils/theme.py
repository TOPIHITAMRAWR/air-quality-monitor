"""
utils/theme.py — loader CSS + helper untuk badge/warna status AQI.

Ambang kategori AQI mengikuti skala OpenWeatherMap (1-5), konsisten
dengan AQI_LABELS di versi lama dashboard supaya warna badge di semua
komponen (kartu, peta, chart) identik — sesuai Definition of Done #2.
"""

import os

import streamlit as st

_CSS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "style.css")

# (label, css_class, hex_warna) — hex dipakai untuk komponen non-HTML (Plotly)
AQI_SCALE = {
    1: ("Baik", "badge-good", "#2ecc71"),
    2: ("Sedang", "badge-good", "#2ecc71"),
    3: ("Tidak Sehat bagi Sensitif", "badge-moderate", "#f39c12"),
    4: ("Tidak Sehat", "badge-unhealthy", "#e74c3c"),
    5: ("Sangat Tidak Sehat", "badge-unhealthy", "#e74c3c"),
}


def load_css():
    """Baca style.css dan inject sekali di awal app.py."""
    with open(_CSS_PATH, "r", encoding="utf-8") as f:
        css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def get_aqi_badge(aqi_value):
    """
    Return (label, css_class, hex_warna) untuk satu nilai AQI.
    Nilai tidak dikenal (None/NaN/di luar 1-5) fallback ke label 'N/A' netral,
    bukan error — supaya UI tidak crash saat data sensor hilang.
    """
    try:
        aqi_int = int(aqi_value)
    except (TypeError, ValueError):
        return ("N/A", "badge-moderate", "#888888")

    return AQI_SCALE.get(aqi_int, ("N/A", "badge-moderate", "#888888"))


def render_badge_html(aqi_value) -> str:
    """Helper cepat untuk generate span badge HTML dari nilai AQI."""
    label, css_class, _ = get_aqi_badge(aqi_value)
    return f'<span class="badge {css_class}">{label}</span>'
