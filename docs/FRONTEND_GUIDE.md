# Panduan Frontend - BaliNavi

Dokumen ini menjelaskan arsitektur, komponen, dan cara kerja frontend Streamlit pada BaliNavi MVP.

## Ikhtisar

Frontend BaliNavi dibangun menggunakan Streamlit. Frontend berfungsi sebagai antarmuka pengguna yang menampilkan form input, memanggil API backend, dan menampilkan hasil rekomendasi beserta visualisasi alokasi budget.

## Arsitektur Frontend

```text
Pengguna
    │
    ▼
Streamlit UI (streamlit_app.py)
    │
    ├── Ambil metadata dari GET /metadata
    ├── Tampilkan form input
    ├── Kirim request ke POST /plan-trip
    └── Tampilkan hasil:
        ├── Budget tier dan metrik
        ├── Tabel dan grafik alokasi budget
        └── Tabel destinasi rekomendasi
```

## Struktur Folder Frontend

```text
app/frontend/
├── __init__.py
└── streamlit_app.py     aplikasi Streamlit utama
```

## Komponen Frontend

### Konfigurasi

- Judul halaman: "BaliNavi".
- Layout: wide.
- URL backend diambil dari `.streamlit/secrets.toml` melalui key `BACKEND_URL`, dengan fallback ke environment variable `BACKEND_URL` untuk Docker/deploy.

### Fungsi Utama

#### `fetch_metadata()`

- Memanggil `GET /metadata` dari backend.
- Mengambil data opsi untuk form input.
- Data yang diambil: travel_types, categories, sub_categories, budget_tiers, max_recommendations.
- Jika backend tidak tersedia, menampilkan pesan error dan menghentikan aplikasi.

#### `request_trip_plan(payload)`

- Memanggil `POST /plan-trip` dari backend dengan data form.
- Mengembalikan response lengkap dari backend.
- Jika gagal, menampilkan pesan error.

### Form Input

Form input menggunakan `st.form` dan terbagi dalam dua kolom:

**Kolom Kiri (Budget):**

| Field | Tipe | Default |
|---|---|---|
| Total budget (IDR) | number_input | 5.000.000 |
| Duration (days) | number_input | 3 |
| Number of people | number_input | 2 |

**Kolom Kanan (Preferensi):**

| Field | Tipe | Default |
|---|---|---|
| Travel type | selectbox | family |
| Preferred categories | multiselect | nature |
| Preferred sub-categories | multiselect | beach |
| Preferred locations | multiselect | Badung |
| Recommendations | slider | 5 |

### Tampilan Hasil

Setelah pengguna menekan tombol "Plan Trip", frontend menampilkan:

#### 1. Metrik Budget

Tiga kolom metrik:

- **Tier**: budget tier (Low, Medium, atau High).
- **Per person per day**: budget per orang per hari dalam IDR.
- **Total budget**: total budget yang dimasukkan.

#### 2. Alokasi Budget

- Tabel alokasi budget (komponen, jumlah, persentase).
- Grafik batang Plotly yang menampilkan alokasi per komponen.

#### 3. Destinasi Rekomendasi

- Tabel dataframe yang menampilkan semua destinasi yang direkomendasikan.

#### 4. Peringatan

- Jika ada warnings dari backend, ditampilkan sebagai pesan peringatan.

## Prinsip Desain Frontend

1. **Tidak ada business logic di frontend**: Semua logika budget tier, alokasi, dan rekomendasi dilakukan oleh backend. Frontend hanya menampilkan hasil.
2. **Metadata-driven form**: Opsi form diambil dari endpoint `/metadata`, bukan di-hardcode di frontend (kecuali lokasi yang masih di-hardcode sebagai daftar statis).
3. **Error handling sederhana**: Jika backend tidak tersedia atau request gagal, tampilkan pesan error yang jelas.
4. **Layout responsif**: Menggunakan `layout="wide"` dan `st.columns` untuk penataan yang rapi.

## Menjalankan Frontend

### Lokal (Tanpa Docker)

Pastikan backend sudah berjalan di `http://localhost:8000`:

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
streamlit run app/frontend/streamlit_app.py
```

Buka: `http://localhost:8501`

### Docker

```bash
docker build -f docker/frontend.Dockerfile -t balinavi-frontend .
docker run -p 8501:8501 -e BACKEND_URL=http://host.docker.internal:8000 balinavi-frontend
```

### Docker Compose

Frontend secara otomatis terhubung ke backend melalui `http://backend:8000` saat menggunakan Docker Compose:

```bash
docker compose up --build
```

## Konfigurasi Frontend

| Konfigurasi | Default | Kegunaan |
|---|---|---|
| `.streamlit/secrets.toml` `BACKEND_URL` | `http://localhost:8000` | URL backend API |
| `.streamlit/secrets.toml` `GOOGLE_API_KEY` | kosong | API key opsional untuk foto destinasi |

Saat menggunakan Docker Compose, variabel ini di-set ke `http://backend:8000` melalui `docker-compose.yml`.

## Visualisasi

Frontend menggunakan Plotly Express untuk visualisasi alokasi budget:

- Tipe grafik: bar chart.
- Sumbu X: komponen alokasi (destination_tickets, local_transport, food, buffer).
- Sumbu Y: jumlah dalam IDR.
- Teks: persentase alokasi.

## Troubleshooting

### "Backend is not reachable"

- Pastikan backend berjalan di URL yang benar.
- Periksa `BACKEND_URL` di `.streamlit/secrets.toml` atau environment container.
- Jika menggunakan Docker Compose, pastikan `docker compose up --build` berhasil.

### Visualisasi tidak muncul

- Pastikan library Plotly terinstal (`pip install plotly`).
- Pastikan response dari backend berisi data `budget_allocation.items`.

### Form tidak menampilkan opsi

- Pastikan endpoint `GET /metadata` mengembalikan data yang benar.
- Periksa log backend untuk error.

## Referensi

- Panduan Backend: [BACKEND_GUIDE.md](BACKEND_GUIDE.md)
- API Contract: [API_CONTRACT.md](API_CONTRACT.md)
- Arsitektur: [ARCHITECTURE.md](ARCHITECTURE.md)
- Panduan pengembangan: [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md)
