"""
Dashboard Streamlit untuk monitoring kualitas udara.

Cara jalan lokal:
    streamlit run dashboard/app.py

CATATAN: dashboard ini baca dari data/air_quality.db LOKAL.
Kalau mau lihat data terbaru dari cron job GitHub Actions, jalankan
`git pull` dulu sebelum buka dashboard.
"""

import os
import sys
from datetime import datetime, timezone

import pandas as pd
import plotly.express as px
import sqlite3
import streamlit as st

# supaya bisa import config dari src/ meski app.py ada di folder dashboard/
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
from config import CITIES, DB_PATH  # noqa: E402


# --- Kategori AQI standar OpenWeatherMap (skala 1-5) ---
AQI_LABELS = {
    1: ("Baik", "#00e400"),
    2: ("Sedang", "#a3d900"),
    3: ("Tidak Sehat bagi Sensitif", "#ff9900"),
    4: ("Tidak Sehat", "#ff0000"),
    5: ("Sangat Tidak Sehat", "#7e0023"),
}


@st.cache_data(ttl=300)  # cache 5 menit, supaya tidak query ulang tiap interaksi UI
def load_data() -> pd.DataFrame:
    """Baca seluruh data dari SQLite jadi DataFrame."""
    if not os.path.exists(DB_PATH):
        return pd.DataFrame()

    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        "SELECT * FROM air_quality_readings ORDER BY timestamp_utc ASC", conn
    )
    conn.close()

    if df.empty:
        return df

    df["datetime_utc"] = pd.to_datetime(df["timestamp_utc"], unit="s", utc=True)
    df["datetime_wib"] = df["datetime_utc"].dt.tz_convert("Asia/Jakarta")
    return df


def render_map(latest_df: pd.DataFrame):
    """Peta sebaran AQI per kota, warna sesuai kategori."""
    map_df = latest_df.copy()
    map_df["kategori"] = map_df["aqi"].map(lambda x: AQI_LABELS.get(x, ("N/A", "#888"))[0])

    fig = px.scatter_mapbox(
        map_df,
        lat="lat",
        lon="lon",
        color="kategori",
        size="pm2_5",
        hover_name="city",
        hover_data={"aqi": True, "pm2_5": True, "lat": False, "lon": False},
        color_discrete_map={label: color for label, color in AQI_LABELS.values()},
        zoom=3.5,
        height=450,
    )
    fig.update_layout(mapbox_style="carto-darkmatter", margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig, use_container_width=True)


def render_trend_chart(df: pd.DataFrame, city: str):
    """Grafik tren AQI/PM2.5 historis untuk satu kota."""
    city_df = df[df["city"] == city].sort_values("datetime_wib")

    if city_df.empty:
        st.info(f"Belum ada data historis untuk {city}.")
        return

    fig = px.line(
        city_df,
        x="datetime_wib",
        y="pm2_5",
        title=f"Tren PM2.5 — {city}",
        labels={"datetime_wib": "Waktu (WIB)", "pm2_5": "PM2.5 (µg/m³)"},
    )
    st.plotly_chart(fig, use_container_width=True)


def render_forecast_placeholder(city: str):
    """
    Placeholder untuk panel forecasting (Prophet).
    Diisi setelah data historis cukup (~1-2 minggu) dan src/forecast.py dibuat.
    """
    st.subheader(f"Prediksi 24 Jam ke Depan — {city}")
    st.info(
        "Belum aktif. Panel ini akan menampilkan prediksi dari model Prophet "
        "setelah data historis terkumpul minimal 1-2 minggu. "
        "Forecasting dengan data lebih pendek dari itu tidak reliable."
    )


def main():
    st.set_page_config(page_title="Monitor Kualitas Udara Indonesia", layout="wide")
    st.title("Monitor Kualitas Udara Indonesia")

    df = load_data()

    if df.empty:
        st.warning(
            "Belum ada data. Pastikan `data/air_quality.db` ada dan sudah diisi "
            "oleh `src/fetch_data.py` (jalankan `git pull` kalau data terbaru "
            "ada di GitHub tapi belum ada di lokal)."
        )
        return

    # Ambil baris terbaru per kota untuk peta & ringkasan
    latest_df = (
        df.sort_values("timestamp_utc").groupby("city").tail(1).reset_index(drop=True)
    )

    last_update = df["datetime_wib"].max()
    st.caption(f"Update terakhir: {last_update.strftime('%Y-%m-%d %H:%M WIB')}")

    # --- Ringkasan kartu per kota ---
    cols = st.columns(len(CITIES))
    for col, (city_name, _) in zip(cols, CITIES.items()):
        row = latest_df[latest_df["city"] == city_name]
        if row.empty:
            col.metric(city_name, "N/A")
            continue
        aqi_val = int(row.iloc[0]["aqi"])
        label, _ = AQI_LABELS.get(aqi_val, ("N/A", "#888"))
        col.metric(city_name, label, f"AQI {aqi_val}")

    st.divider()

    # --- Peta ---
    st.subheader("Peta Sebaran AQI")
    render_map(latest_df)

    st.divider()

    # --- Grafik tren + placeholder forecasting, per kota terpilih ---
    selected_city = st.selectbox("Pilih kota untuk detail tren", list(CITIES.keys()))

    tab_trend, tab_forecast = st.tabs(["Tren Historis", "Prediksi (belum aktif)"])
    with tab_trend:
        render_trend_chart(df, selected_city)
    with tab_forecast:
        render_forecast_placeholder(selected_city)

    st.divider()
    st.caption(
        f"Jumlah total baris data: {len(df)} | "
        f"Rentang: {df['datetime_wib'].min().strftime('%Y-%m-%d')} — "
        f"{df['datetime_wib'].max().strftime('%Y-%m-%d')}"
    )


if __name__ == "__main__":
    main()
