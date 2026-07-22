"""
Konfigurasi proyek: API key, daftar kota, path database.

PENTING: jangan hardcode API key di sini. Simpan sebagai environment variable
(lokal: file .env, GitHub Actions: repo secret bernama OWM_API_KEY).
"""

import os

# --- API ---
OWM_API_KEY = os.environ.get("OWM_API_KEY", "")
OWM_BASE_URL = "http://api.openweathermap.org/data/2.5/air_pollution"

if not OWM_API_KEY:
    # Tidak raise error di sini supaya file ini bisa di-import untuk testing
    # tanpa API key. fetch_data.py yang akan validasi sebelum request.
    pass

# --- Daftar kota awal (mulai kecil dulu, scope terkendali) ---
# lat/lon didapat dari OpenStreetMap / Google Maps, koordinat pusat kota.
CITIES = {
    "Jakarta": {"lat": -6.2088, "lon": 106.8456},
    "Surabaya": {"lat": -7.2575, "lon": 112.7521},
    "Bandung": {"lat": -6.9175, "lon": 107.6191},
    "Medan": {"lat": 3.5952, "lon": 98.6722},
    "Makassar": {"lat": -5.1477, "lon": 119.4327},
}

# --- Database ---
DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data",
    "air_quality.db",
)
