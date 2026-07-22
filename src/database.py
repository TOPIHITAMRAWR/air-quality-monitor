"""
Skema dan fungsi database SQLite.

Kenapa SQLite: gratis, tanpa server, cukup untuk skala data proyek ini
(ribuan-puluhan ribu baris selama beberapa bulan fetch berkala).
"""

import sqlite3
from contextlib import contextmanager

from config import DB_PATH


SCHEMA = """
CREATE TABLE IF NOT EXISTS air_quality_readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    city TEXT NOT NULL,
    lat REAL NOT NULL,
    lon REAL NOT NULL,
    timestamp_utc INTEGER NOT NULL,   -- unix timestamp dari API (dt field)
    fetched_at TEXT NOT NULL,          -- kapan baris ini di-insert (ISO string)
    aqi INTEGER,                       -- 1-5 sesuai skala OpenWeatherMap
    pm2_5 REAL,
    pm10 REAL,
    co REAL,
    no2 REAL,
    o3 REAL,
    so2 REAL,
    UNIQUE(city, timestamp_utc)        -- cegah duplikat kalau cron jalan dobel
);

CREATE INDEX IF NOT EXISTS idx_city_timestamp
    ON air_quality_readings (city, timestamp_utc);
"""


@contextmanager
def get_connection():
    """Context manager supaya koneksi selalu ditutup meski ada error."""
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """Buat tabel kalau belum ada. Aman dipanggil berkali-kali."""
    with get_connection() as conn:
        conn.executescript(SCHEMA)


def insert_reading(conn, reading: dict):
    """
    Insert satu baris data. Pakai INSERT OR IGNORE supaya duplikat
    (city + timestamp_utc sama) tidak menyebabkan error, cukup di-skip.
    """
    conn.execute(
        """
        INSERT OR IGNORE INTO air_quality_readings
            (city, lat, lon, timestamp_utc, fetched_at,
             aqi, pm2_5, pm10, co, no2, o3, so2)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            reading["city"],
            reading["lat"],
            reading["lon"],
            reading["timestamp_utc"],
            reading["fetched_at"],
            reading["aqi"],
            reading["pm2_5"],
            reading["pm10"],
            reading["co"],
            reading["no2"],
            reading["o3"],
            reading["so2"],
        ),
    )


def count_readings():
    """Berguna untuk cek cepat: sudah berapa banyak data terkumpul."""
    with get_connection() as conn:
        cur = conn.execute("SELECT COUNT(*) FROM air_quality_readings")
        return cur.fetchone()[0]


if __name__ == "__main__":
    init_db()
    print(f"Database siap di: {DB_PATH}")
    print(f"Jumlah baris saat ini: {count_readings()}")
