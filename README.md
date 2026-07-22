# Air Quality Monitor

Pipeline: fetch API → SQLite → (nanti) forecasting → dashboard.

## Setup Lokal

1. Dapatkan API key gratis dari https://openweathermap.org/api/air-pollution
   (daftar akun, key aktif biasanya butuh beberapa menit sampai jam).

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set API key sebagai environment variable:
   ```
   export OWM_API_KEY="isi_api_key_anda"
   ```
   (Windows PowerShell: `$env:OWM_API_KEY="isi_api_key_anda"`)

4. Jalankan fetch manual untuk tes:
   ```
   cd src
   python fetch_data.py
   ```

   Kalau berhasil, akan muncul output seperti:
   ```
   [OK] Jakarta: AQI=3, PM2.5=35.2
   [OK] Surabaya: AQI=2, PM2.5=18.1
   ...
   Selesai. Berhasil: 5, Gagal: 0
   ```

5. Cek isi database:
   ```
   python database.py
   ```

## Setup Cron Job Otomatis (GitHub Actions)

1. Push repo ini ke GitHub (harus public repo untuk GitHub Actions gratis
   tanpa batas ketat; private repo juga dapat jatah gratis tapi terbatas menit/bulan).

2. Di GitHub repo → Settings → Secrets and variables → Actions →
   New repository secret:
   - Name: `OWM_API_KEY`
   - Value: API key Anda

3. Workflow di `.github/workflows/fetch_daily.yml` akan otomatis jalan
   tiap 3 jam. Bisa juga trigger manual lewat tab "Actions" di GitHub →
   pilih workflow → "Run workflow".

4. Database (`data/air_quality.db`) akan ter-update dan ter-commit otomatis
   oleh bot setiap kali fetch berhasil.

## Catatan Penting

- **Jangan forecasting dulu** sebelum data terkumpul minimal 1-2 minggu.
  Cek jumlah data dengan `python src/database.py`.
- Skema database punya constraint `UNIQUE(city, timestamp_utc)` — kalau
  cron job kebetulan jalan dobel di waktu hampir sama, tidak akan
  menghasilkan duplikat data.
- Kalau API OpenWeatherMap berubah struktur response di masa depan,
  cek ulang `fetch_city()` di `fetch_data.py` — parsing-nya bergantung
  pada struktur JSON spesifik dari API ini.

## Struktur Selanjutnya (belum dibuat)

- `src/clean.py` — cleaning & handle outlier
- `src/forecast.py` — model Prophet per kota
- `dashboard/app.py` — Streamlit dashboard
