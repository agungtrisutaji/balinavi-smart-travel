# Panduan Demo - BaliNavi

Dokumen ini menjelaskan cara menyiapkan dan menjalankan demo BaliNavi MVP.

## Ikhtisar

Demo BaliNavi menunjukkan kemampuan MVP dalam:

1. Menerima input preferensi perjalanan pengguna.
2. Mengklasifikasikan budget tier.
3. Mengalokasikan budget ke komponen pengeluaran.
4. Merekomendasikan destinasi Bali yang sesuai.
5. Menampilkan visualisasi alokasi budget.

## Persiapan Demo

### Opsi 1: Docker Compose (Direkomendasikan)

Cara paling mudah untuk menjalankan demo:

```bash
docker compose up --build
```

Tunggu sampai kedua container berjalan, lalu akses:

```text
Streamlit App : http://localhost:8501
Backend API   : http://localhost:8000
API Docs      : http://localhost:8000/docs
```

### Opsi 2: Lokal Tanpa Docker

1. Aktifkan virtual environment dan install dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Mac/Linux
pip install -r requirements.txt
```

2. Jalankan backend di terminal pertama:

```bash
uvicorn app.backend.main:app --reload --host 0.0.0.0 --port 8000
```

3. Jalankan frontend di terminal kedua:

```bash
streamlit run app/frontend/streamlit_app.py
```

4. Buka `http://localhost:8501`.

### Verifikasi Sebelum Demo

Sebelum demo, pastikan:

- [ ] Backend berjalan: buka `http://localhost:8000/health` → harus menampilkan `{"status": "ok", ...}`.
- [ ] Frontend berjalan: buka `http://localhost:8501` → harus menampilkan form BaliNavi.
- [ ] Test lulus: jalankan `pytest tests/ -v` → semua test harus hijau.

## Skenario Demo

### Skenario 1: Budget Menengah, Wisata Keluarga

**Input:**

| Field | Nilai |
|---|---|
| Total budget | 5.000.000 IDR |
| Duration | 3 hari |
| Number of people | 2 |
| Travel type | family |
| Preferred categories | nature, culture |
| Preferred sub-categories | beach, temple |
| Preferred locations | Badung, Gianyar |
| Recommendations | 5 |

**Hasil yang diharapkan:**

- Budget tier: **Medium**
- Budget per person per day: **IDR 833.333**
- Alokasi budget:
  - destination_tickets: 1.250.000 (25%)
  - local_transport: 1.250.000 (25%)
  - food: 1.500.000 (30%)
  - buffer: 1.000.000 (20%)
- Rekomendasi destinasi: Pantai Kuta, Pura Tirta Empul, Tegenungan Waterfall

### Skenario 2: Budget Rendah, Solo Traveler

**Input:**

| Field | Nilai |
|---|---|
| Total budget | 2.000.000 IDR |
| Duration | 3 hari |
| Number of people | 2 |
| Travel type | solo |
| Preferred categories | nature |
| Preferred sub-categories | beach |
| Preferred locations | Badung |
| Recommendations | 5 |

**Hasil yang diharapkan:**

- Budget tier: **Low**
- Budget per person per day: **IDR 333.333**
- Rekomendasi: hanya destinasi yang mendukung budget tier low

### Skenario 3: Budget Tinggi, Tanpa Filter

**Input:**

| Field | Nilai |
|---|---|
| Total budget | 10.000.000 IDR |
| Duration | 3 hari |
| Number of people | 2 |
| Travel type | couple |
| Preferred categories | (kosong) |
| Preferred sub-categories | (kosong) |
| Preferred locations | (kosong) |
| Recommendations | 5 |

**Hasil yang diharapkan:**

- Budget tier: **High**
- Budget per person per day: **IDR 1.666.666**
- Rekomendasi: semua destinasi yang mendukung budget tier high

## Demo API Langsung

Selain Streamlit, API bisa didemonstrasikan langsung melalui Swagger UI:

1. Buka `http://localhost:8000/docs`.
2. Coba endpoint `/health` → klik "Try it out" → "Execute".
3. Coba endpoint `/metadata` → klik "Try it out" → "Execute".
4. Coba endpoint `/plan-trip`:
   - Klik "Try it out".
   - Masukkan request body JSON.
   - Klik "Execute".
   - Lihat response.

Contoh request body untuk `/plan-trip`:

```json
{
  "total_budget": 5000000,
  "duration_days": 3,
  "num_people": 2,
  "travel_type": "family",
  "preferred_categories": ["nature", "culture"],
  "preferred_sub_categories": ["beach", "temple"],
  "preferred_locations": ["Badung", "Gianyar"],
  "top_k": 5
}
```

## Poin-Poin Presentasi

Saat demo, soroti poin-poin berikut:

1. **End-to-end flow**: dari input pengguna sampai rekomendasi.
2. **Budget tier classification**: penjelasan rumus dan aturan tier.
3. **Budget allocation**: visualisasi alokasi yang jelas dan terkontrol.
4. **Content-based recommendation**: filter berdasarkan preferensi pengguna.
5. **API-first architecture**: backend dan frontend terpisah, berkomunikasi melalui API.
6. **Containerization**: satu perintah `docker compose up` untuk menjalankan semua.
7. **Automated testing**: test otomatis untuk menjaga kualitas.
8. **CI/CD**: GitHub Actions untuk validasi setiap perubahan.

## Troubleshooting Demo

### Frontend menampilkan "Backend is not reachable"

- Pastikan backend sudah berjalan.
- Jika menggunakan Docker Compose, tunggu sampai backend container selesai startup.
- Periksa log: `docker compose logs backend`.

### Tidak ada rekomendasi yang muncul

- Periksa apakah filter terlalu ketat.
- Coba kosongkan preferred categories dan locations untuk melihat semua destinasi.
- Pastikan budget tier sesuai dengan destinasi yang tersedia.

### Docker build gagal

- Pastikan Docker dan Docker Compose terinstal.
- Jalankan `docker compose config` untuk validasi.
- Periksa koneksi internet (untuk download Python image dan pip packages).

## Referensi

- Panduan pengembangan: [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md)
- Panduan Docker: [DOCKER_GUIDE.md](DOCKER_GUIDE.md)
- API Contract: [API_CONTRACT.md](API_CONTRACT.md)
- Scope MVP: [MVP_SCOPE.md](MVP_SCOPE.md)
