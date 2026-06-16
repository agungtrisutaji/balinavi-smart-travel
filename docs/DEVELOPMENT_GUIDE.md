# Panduan Pengembangan - BaliNavi

Dokumen ini menjelaskan cara menyiapkan lingkungan pengembangan dan menjalankan BaliNavi secara lokal.

## Prasyarat

Pastikan software berikut sudah terinstal:

| Software | Versi Minimum | Kegunaan |
|---|---|---|
| Python | 3.12 | Bahasa pemrograman utama |
| pip | terbaru | Package manager Python |
| Git | terbaru | Version control |
| Docker | terbaru | Containerization |
| Docker Compose | terbaru | Orkestrasi container |

## Setup Lingkungan Pengembangan

### 1. Clone Repository

```bash
git clone <repository-url>
cd balinavi-smart-travel
```

### 2. Buat Virtual Environment

```bash
python -m venv .venv
```

### 3. Aktifkan Virtual Environment

Windows:

```bash
.venv\Scripts\activate
```

Mac atau Linux:

```bash
source .venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Siapkan Streamlit Secrets

Salin `.streamlit/secrets.toml.example` ke `.streamlit/secrets.toml`:

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Isi file `.streamlit/secrets.toml` tidak perlu diubah untuk pengembangan lokal. Nilai default sudah tersedia:

```toml
BACKEND_URL = "http://localhost:8000"
GOOGLE_API_KEY = ""
```

## Menjalankan Aplikasi Secara Lokal

### Menjalankan Backend

```bash
uvicorn app.backend.main:app --reload --host 0.0.0.0 --port 8000
```

Verifikasi backend berjalan:

```text
http://localhost:8000/health
http://localhost:8000/docs
```

Endpoint `/docs` menampilkan dokumentasi API interaktif yang dihasilkan otomatis oleh FastAPI.

### Menjalankan Frontend

Buka terminal baru (pastikan virtual environment aktif):

```bash
streamlit run app/frontend/streamlit_app.py
```

Buka browser:

```text
http://localhost:8501
```

Frontend akan memanggil backend di `http://localhost:8000`. Pastikan backend sudah berjalan sebelum membuka frontend.

### Menjalankan dengan Docker Compose

Jika ingin menjalankan kedua service sekaligus menggunakan Docker:

```bash
docker compose up --build
```

Akses:

```text
Backend API   : http://localhost:8000
API Docs      : http://localhost:8000/docs
Streamlit App : http://localhost:8501
```

Lihat panduan lengkap Docker di [DOCKER_GUIDE.md](DOCKER_GUIDE.md).

## Menjalankan Test

```bash
pytest tests/ -v
```

Lihat panduan lengkap testing di [TESTING_GUIDE.md](TESTING_GUIDE.md).

## Struktur Proyek

Lihat `PROJECT_STRUCTURE.md` di root repository untuk detail lengkap struktur folder.

Ringkasan folder utama:

```text
docs/              dokumentasi proyek
app/backend/       FastAPI backend
app/frontend/      Streamlit frontend
src/               data, preprocessing, features, models, services
data/              dataset mentah, diproses, dan final
artifacts/         model dan vectorizer artifact
notebooks/         EDA dan eksperimen
tests/             automated test
docker/            Dockerfile
.github/           GitHub Actions dan PR template
```

## Konvensi Kode

### Umum

- Gunakan Python 3.12.
- Ikuti PEP 8 untuk format kode.
- Gunakan type hint pada semua fungsi.
- Tulis docstring untuk fungsi publik.

### Backend

- Jaga route handler tetap tipis.
- Taruh business logic di `src/services/`.
- Gunakan Pydantic schema untuk validasi request dan response.
- Lihat panduan lengkap di [BACKEND_GUIDE.md](BACKEND_GUIDE.md).

### Frontend

- Jangan duplikasi business logic dari backend.
- Frontend hanya menampilkan UI dan memanggil API.
- Lihat panduan lengkap di [FRONTEND_GUIDE.md](FRONTEND_GUIDE.md).

### Services

- Setiap service punya satu tanggung jawab.
- `budget_service.py` untuk klasifikasi budget tier.
- `allocation_service.py` untuk alokasi budget.
- `recommender_service.py` untuk rekomendasi destinasi.

## Konfigurasi Runtime

| Konfigurasi | Default | Kegunaan |
|---|---|---|
| `.streamlit/secrets.toml` `BACKEND_URL` | `http://localhost:8000` | URL backend untuk frontend |
| `.streamlit/secrets.toml` `GOOGLE_API_KEY` | kosong | API key opsional untuk foto destinasi |
| environment `BACKEND_HOST` | `0.0.0.0` | Host backend jika menjalankan backend dengan konfigurasi environment |
| environment `BACKEND_PORT` | `8000` | Port backend jika menjalankan backend dengan konfigurasi environment |

## Troubleshooting

### Backend tidak bisa dijalankan

- Pastikan virtual environment aktif.
- Pastikan semua dependency terinstal dengan `pip install -r requirements.txt`.
- Pastikan port 8000 tidak digunakan oleh aplikasi lain.

### Frontend error "Backend is not reachable"

- Pastikan backend sudah berjalan di `http://localhost:8000`.
- Jika menggunakan Docker, pastikan `docker compose up --build` sudah berhasil.
- Periksa `BACKEND_URL` di `.streamlit/secrets.toml`.

### Test gagal

- Pastikan semua dependency terinstal.
- Pastikan tidak ada perubahan yang merusak API contract.
- Jalankan `pytest tests/ -v` untuk melihat detail error.

## Referensi

- Arsitektur: [ARCHITECTURE.md](ARCHITECTURE.md)
- API Contract: [API_CONTRACT.md](API_CONTRACT.md)
- Scope MVP: [MVP_SCOPE.md](MVP_SCOPE.md)
- Docker: [DOCKER_GUIDE.md](DOCKER_GUIDE.md)
- Testing: [TESTING_GUIDE.md](TESTING_GUIDE.md)
