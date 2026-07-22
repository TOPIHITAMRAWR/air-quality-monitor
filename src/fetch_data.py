"""
Ambil data kualitas udara dari OpenWeatherMap Air Pollution API
untuk semua kota di config.py, lalu simpan ke SQLite.

Jalankan manual: python src/fetch_data.py
Dijadwalkan otomatis lewat GitHub Actions (.github/workflows/fetch_daily.yml).
"""

import sys
import time
from datetime import datetime, timezone

import requests

from config import CITIES, OWM_API_KEY, OWM_BASE_URL
from database import get_connection, init_db, insert_reading


def fetch_city(city_name: str, lat: float, lon: float) -> dict | None:
    """
    Hit API untuk satu kota. Return None kalau gagal, supaya kota lain
    tetap bisa diproses walau satu kota error (jangan biarkan satu
    kegagalan menghentikan seluruh batch).
    """
    params = {"lat": lat, "lon": lon, "appid": OWM_API_KEY}

    try:
        resp = requests.get(OWM_BASE_URL, params=params, timeout=10)
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"[GAGAL] {city_name}: {e}", file=sys.stderr)
        return None

    data = resp.json()

    try:
        item = data["list"][0]
        components = item["components"]
    except (KeyError, IndexError) as e:
        print(f"[GAGAL] {city_name}: format response tidak sesuai ekspektasi ({e})",
              file=sys.stderr)
        return None

    return {
        "city": city_name,
        "lat": lat,
        "lon": lon,
        "timestamp_utc": item["dt"],
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "aqi": item["main"]["aqi"],
        "pm2_5": components.get("pm2_5"),
        "pm10": components.get("pm10"),
        "co": components.get("co"),
        "no2": components.get("no2"),
        "o3": components.get("o3"),
        "so2": components.get("so2"),
    }


def main():
    if not OWM_API_KEY:
        print(
            "ERROR: OWM_API_KEY belum diset. "
            "Set environment variable OWM_API_KEY sebelum menjalankan script ini.",
            file=sys.stderr,
        )
        sys.exit(1)

    init_db()

    success_count = 0
    fail_count = 0

    with get_connection() as conn:
        for city_name, coords in CITIES.items():
            reading = fetch_city(city_name, coords["lat"], coords["lon"])

            if reading is None:
                fail_count += 1
                continue

            insert_reading(conn, reading)
            success_count += 1
            print(f"[OK] {city_name}: AQI={reading['aqi']}, PM2.5={reading['pm2_5']}")

            # Jeda kecil antar request, sopan terhadap API meski free tier
            # OpenWeatherMap cukup longgar (60 calls/menit).
            time.sleep(1)

    print(f"\nSelesai. Berhasil: {success_count}, Gagal: {fail_count}")

    if fail_count > 0 and success_count == 0:
        # Kalau semua kota gagal, exit dengan error code supaya GitHub Actions
        # menandai run ini sebagai failed (bukan silently pass).
        sys.exit(1)


if __name__ == "__main__":
    main()
