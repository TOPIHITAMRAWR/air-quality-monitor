"""
components/sidebar.py — nav sidebar dengan routing beneran.

Kenapa st.query_params (bukan session_state + invisible button overlay
seperti opsi di PRD 7.2.3): query_params lebih sederhana untuk routing
antar-"halaman" sederhana seperti ini, tetap trigger rerun standar
Streamlit, dan URL-nya bisa di-bookmark/share — tidak butuh trik overlay
tombol transparan yang rapuh terhadap perubahan versi Streamlit.

Halaman "Analisis Lanjutan" dan "Pengaturan" masih placeholder
("Segera Hadir") karena isinya belum ditentukan di luar scope PRD ini —
routing-nya sudah nyata dan berfungsi, tinggal isi kontennya nanti.
"""

import streamlit as st

PAGES = {
    "dashboard": {"label": "Dashboard", "icon": "🏠", "enabled": True},
    "analisis": {"label": "Analisis", "icon": "📊", "enabled": False},
    "pengaturan": {"label": "Pengaturan", "icon": "⚙️", "enabled": False},
}

DEFAULT_PAGE = "dashboard"


def render_sidebar() -> str:
    """
    Render nav item di sidebar, baca/tulis halaman aktif lewat st.query_params.
    Return: key halaman yang sedang aktif (str).
    """
    current_page = st.query_params.get("page", DEFAULT_PAGE)
    if current_page not in PAGES:
        current_page = DEFAULT_PAGE

    with st.sidebar:
        for key, meta in PAGES.items():
            is_active = key == current_page

            if not meta["enabled"]:
                st.markdown(
                    f'<div class="nav-item disabled" title="Segera hadir">'
                    f'{meta["icon"]}<span>{meta["label"]}</span></div>',
                    unsafe_allow_html=True,
                )
                continue

            # Tombol asli Streamlit (perlu untuk trigger rerun + set query param).
            # Halaman aktif ditandai bullet "●" di depan label — bukan class CSS,
            # karena st.button tidak menerima conditional class (batasan widget native).
            prefix = "●" if is_active else "○"
            clicked = st.button(
                f'{meta["icon"]} {prefix} {meta["label"]}',
                key=f"nav_{key}",
                width="stretch",
            )
            if clicked:
                st.query_params["page"] = key
                st.rerun()

    return current_page


def render_disabled_page_notice(page_key: str):
    """Tampilan untuk halaman yang route-nya ada tapi kontennya belum dibuat."""
    meta = PAGES.get(page_key, {})
    st.markdown(
        f'<div class="glass-card empty-state">'
        f'<div style="font-size:32px;">{meta.get("icon", "🚧")}</div>'
        f'<div class="metric-label" style="margin-top:8px;">'
        f'Halaman "{meta.get("label", page_key)}" segera hadir</div>'
        f'<div style="font-size:13px; margin-top:4px;">'
        f'Routing sudah aktif — kontennya menyusul di scope berikutnya.</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
