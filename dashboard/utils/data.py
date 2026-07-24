"""
utils/data.py — semua pembacaan SQLite di-cache di sini.

PRD section 4 menandai ini sebagai wajib, bukan nice-to-have: tanpa cache,
komponen baru (sparkline per kota, dsb.) akan menambah query berulang tiap
interaksi UI dan membuat dashboard terasa lambat meski visualnya bagus.
"""

import os
import sys

import pandas as pd
import sqlite3
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "src"))
from config import CITIES, DB_PATH  # noqa: E402

# Ambang minimum data untuk mengaktifkan tab prediksi Prophet.
# Diputuskan: ~14 hari @ interval cron 3 jam (8x/hari) = 112 data point per kota.
FORECAST_MIN_DATAPOINTS = 112


@st.cache_data(ttl=300)
def load_all_readings() -> pd.DataFrame:
    """Baca seluruh data historis. Cache 5 menit."""
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


@st.cache_data(ttl=300)
def load_latest_per_city() -> pd.DataFrame:
    """Baris terbaru per kota — dipakai kartu ringkasan & peta."""
    df = load_all_readings()
    if df.empty:
        return df
    return df.sort_values("timestamp_utc").groupby("city").tail(1).reset_index(drop=True)


@st.cache_data(ttl=300)
def load_city_history(city: str, limit_points: int = 200) -> pd.DataFrame:
    """
    Histori satu kota, dibatasi limit_points titik terakhir.
    Query terpisah dari load_all_readings supaya sparkline (yang hanya
    butuh beberapa titik terakhir) tidak menduplikasi beban baca seluruh
    tabel tiap kali dipanggil (task 7.7.3).
    """
    df = load_all_readings()
    if df.empty:
        return df
    city_df = df[df["city"] == city].sort_values("datetime_wib")
    return city_df.tail(limit_points)


def data_count_for_city(city: str) -> int:
    """Jumlah baris data historis untuk satu kota — dipakai empty-state forecast."""
    df = load_all_readings()
    if df.empty:
        return 0
    return int((df["city"] == city).sum())
