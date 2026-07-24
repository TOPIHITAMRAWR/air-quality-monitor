"""
components/forecast_tab.py — tab prediksi 24 jam (task 7.6).

Ambang minimum 112 data point (~14 hari @ 3 jam/fetch) diputuskan bersama
user — lihat utils/data.py FORECAST_MIN_DATAPOINTS.

Model Prophet SENGAJA belum diimplementasikan di file ini — scope PRD ini
murni redesign UI (section 3: "Out of scope: model Prophet itu sendiri,
hanya tampilan tab-nya"). Fungsi ini hanya menyiapkan UI empty-state dan
placeholder hasil forecast untuk diisi nanti.
"""

import streamlit as st

from utils.data import FORECAST_MIN_DATAPOINTS, data_count_for_city


def render_forecast_tab(city: str):
    st.markdown('<div class="forecast-tabs-scope">', unsafe_allow_html=True)

    count = data_count_for_city(city)

    if count < FORECAST_MIN_DATAPOINTS:
        progress_pct = min(100, int((count / FORECAST_MIN_DATAPOINTS) * 100))
        st.markdown(
            f'<div class="glass-card empty-state">'
            f'<div style="font-size:28px;">⏳</div>'
            f'<div class="metric-label" style="margin-top:8px;">'
            f'Data historis belum cukup untuk prediksi</div>'
            f'<div style="font-size:13px; margin:8px 0;">'
            f'{count} / {FORECAST_MIN_DATAPOINTS} data point terkumpul '
            f'(~14 hari dibutuhkan untuk hasil prediksi yang reliable)</div>'
            f'<div class="progress-track">'
            f'<div class="progress-fill" style="width:{progress_pct}%;"></div>'
            f'</div>'
            f'<div style="font-size:12px; color:var(--text-secondary);">{progress_pct}%</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    else:
        # Placeholder — model Prophet belum diimplementasikan (out of scope PRD ini).
        st.markdown(
            f'<div class="glass-card empty-state">'
            f'<div style="font-size:28px;">✅</div>'
            f'<div class="metric-label" style="margin-top:8px;">'
            f'Data cukup ({count} data point) — model prediksi belum diaktifkan</div>'
            f'<div style="font-size:13px; margin-top:4px;">'
            f'Implementasi model Prophet ada di scope terpisah, di luar '
            f'redesign UI ini.</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)
