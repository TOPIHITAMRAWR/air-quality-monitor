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
    """
    Baca style.css dan inject sekali di awal app.py, sekaligus terapkan
    override tema terang kalau mode terang aktif.

    CATATAN PENTING: toggle tema TIDAK memakai JavaScript sama sekali.
    Percobaan awal pakai <script> untuk toggle class di client-side gagal
    karena script yang di-inject lewat unsafe_allow_html (innerHTML) tidak
    pernah dieksekusi browser — ini batasan platform web, bukan bug
    Streamlit. Solusinya: Python yang langsung memutuskan nilai variabel
    CSS mana yang dikirim, di-generate ulang tiap render sesuai
    st.session_state["dark_mode"].
    """
    with open(_CSS_PATH, "r", encoding="utf-8") as f:
        css = f.read()

    is_light = st.session_state.get("dark_mode", True) is False
    if is_light:
        # Override token warna langsung di :root (bukan lewat class .theme-light,
        # supaya tidak bergantung apa pun di client-side).
        css += """
        :root {
          --bg-primary: #faf3ea !important;
          --glass-bg: rgba(60, 35, 15, 0.045) !important;
          --glass-border: rgba(60, 35, 15, 0.12) !important;
          --text-primary: #2b1c0f !important;
          --text-secondary: #8a6a4a !important;
          --accent: #c96a2c !important;
        }
        .stApp {
          background:
            radial-gradient(circle at 12% 15%, rgba(232, 130, 60, 0.10), transparent 38%),
            radial-gradient(circle at 88% 10%, rgba(180, 110, 60, 0.10), transparent 40%),
            radial-gradient(circle at 78% 80%, rgba(200, 90, 30, 0.08), transparent 45%),
            var(--bg-primary) !important;
        }
        section[data-testid="stSidebar"] {
          background: rgba(250, 243, 234, 0.9) !important;
        }
        """

    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def render_theme_toggle():
    """Tombol toggle mode gelap/terang. Return True kalau mode saat ini gelap."""
    if "dark_mode" not in st.session_state:
        st.session_state["dark_mode"] = True

    st.markdown('<div class="theme-toggle-btn">', unsafe_allow_html=True)
    icon = "🌙" if st.session_state["dark_mode"] else "☀️"
    if st.button(icon, key="theme_toggle", help="Ganti mode gelap/terang"):
        st.session_state["dark_mode"] = not st.session_state["dark_mode"]
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    return st.session_state["dark_mode"]


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
