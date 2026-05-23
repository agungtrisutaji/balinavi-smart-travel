# Panduan Backend - BaliNavi

Dokumen ini menjelaskan arsitektur, komponen, dan cara kerja backend FastAPI pada BaliNavi MVP.

## Ikhtisar

Backend BaliNavi dibangun menggunakan FastAPI dan berfungsi sebagai server API yang menerima request dari frontend Streamlit, memproses melalui service layer, dan mengembalikan response berupa rekomendasi destinasi dan alokasi budget.

## Arsitektur Backend

```text
Request dari Frontend
        │
        ▼
   FastAPI App (main.py)
        │
        ▼
   Router (api/routes.py)
        │
        ├── GET /health
        ├── GET /metadata
        └── POST /plan-trip
                │
                ▼
         Service Layer
                │
                ├── budget_service.classify_budget()
                ├── allocation_service.allocate_budget()
                └── recommender_service.recommend_destinations()
                        │
                        ▼
                  Response ke Frontend
```

## Struktur Folder Backend

```text
app/backend/
├── __init__.py
├── main.py              entrypoint FastAPI
├── api/
│   ├── __init__.py
│   └── routes.py        definisi endpoint
├── schemas/
│   ├── __init__.py
│   └── trip_schema.py   Pydantic schema
└── core/
    ├── __init__.py
    └── config.py        konfigurasi aplikasi
```

## Komponen Backend

### Entrypoint (`main.py`)

File ini membuat instance FastAPI dan mendaftarkan router:

- Membuat `FastAPI` app dengan nama dan versi dari config.
- Memasukkan `router` dari `api/routes.py`.

### Routes (`api/routes.py`)

File ini mendefinisikan tiga endpoint MVP:

#### `GET /health`

- Health check endpoint.
- Mengembalikan status `ok`, nama service, dan versi.
- Tidak memerlukan request body.

#### `GET /metadata`

- Mengembalikan opsi yang tersedia untuk form input frontend.
- Data diambil dari `src/utils/constants.py`.
- Response berisi: travel_types, categories, sub_categories, budget_tiers, max_recommendations.

#### `POST /plan-trip`

- Endpoint utama untuk menghasilkan rekomendasi.
- Menerima request body dengan informasi trip.
- Memanggil tiga service secara berurutan:
  1. `classify_budget()` untuk menentukan budget tier.
  2. `allocate_budget()` untuk mengalokasikan budget.
  3. `recommend_destinations()` untuk menghasilkan rekomendasi.
- Mengembalikan response lengkap dengan budget, alokasi, rekomendasi, dan summary.

### Schemas (`schemas/trip_schema.py`)

File ini mendefinisikan Pydantic model untuk validasi:

| Schema | Kegunaan |
|---|---|
| `PlanTripRequest` | Validasi request body untuk `/plan-trip` |
| `BudgetSummary` | Struktur data budget tier |
| `AllocationItem` | Satu item alokasi budget |
| `BudgetAllocation` | Keseluruhan alokasi budget |
| `DestinationRecommendation` | Satu destinasi rekomendasi |
| `PlanTripResponse` | Response lengkap `/plan-trip` |
| `MetadataResponse` | Response untuk `/metadata` |

Validasi yang dilakukan:

- `total_budget` harus lebih besar dari 0.
- `duration_days` harus antara 1 sampai 30.
- `num_people` harus antara 1 sampai 20.
- `travel_type` harus salah satu dari: solo, couple, family, group.
- `preferred_categories` divalidasi terhadap daftar kategori yang didukung.
- `preferred_sub_categories` divalidasi terhadap daftar sub-kategori yang didukung.
- `top_k` default 5, maksimal sesuai `MAX_RECOMMENDATIONS` (10).

### Config (`core/config.py`)

File ini menyimpan konfigurasi aplikasi:

| Variabel | Default | Kegunaan |
|---|---|---|
| `APP_NAME` | `BaliNavi Backend` | Nama aplikasi di dokumentasi API |
| `APP_VERSION` | `0.1.0` | Versi API |
| `BACKEND_HOST` | `0.0.0.0` | Host server |
| `BACKEND_PORT` | `8000` | Port server |

## Prinsip Desain Backend

1. **Route handler tipis**: Route handler hanya memanggil service dan mengembalikan response. Business logic ada di `src/services/`.
2. **Validasi di schema**: Semua validasi request menggunakan Pydantic, bukan logika manual di route handler.
3. **API contract stabil**: Jangan mengubah field request atau response tanpa memperbarui [API_CONTRACT.md](API_CONTRACT.md), test, dan frontend.
4. **Separation of concerns**: Backend tidak mengimplementasikan logika preprocessing data atau training model.

## Menjalankan Backend

### Lokal

```bash
uvicorn app.backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker

```bash
docker build -f docker/backend.Dockerfile -t balinavi-backend .
docker run -p 8000:8000 balinavi-backend
```

### Verifikasi

```text
http://localhost:8000/health     → health check
http://localhost:8000/docs       → dokumentasi API interaktif
http://localhost:8000/metadata   → metadata opsi form
```

## Referensi

- API Contract: [API_CONTRACT.md](API_CONTRACT.md)
- Arsitektur: [ARCHITECTURE.md](ARCHITECTURE.md)
- Panduan Frontend: [FRONTEND_GUIDE.md](FRONTEND_GUIDE.md)
- Panduan Testing: [TESTING_GUIDE.md](TESTING_GUIDE.md)
- Budget Engine: [BUDGET_ENGINE_GUIDE.md](BUDGET_ENGINE_GUIDE.md)
- Recommender: [RECOMMENDER_GUIDE.md](RECOMMENDER_GUIDE.md)
