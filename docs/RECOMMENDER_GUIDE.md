# Panduan Recommender - BaliNavi

Dokumen ini menjelaskan sistem rekomendasi destinasi pada BaliNavi MVP, termasuk pendekatan, implementasi saat ini, dan rencana pengembangan.

## Ikhtisar

Recommender BaliNavi menggunakan pendekatan content-based filtering untuk merekomendasikan destinasi Bali berdasarkan preferensi pengguna dan budget tier.

## Pendekatan Rekomendasi

### Baseline MVP

```text
content text → TF-IDF → cosine similarity → budget filter → ranked recommendations
```

Langkah:

1. Bangun content text dari metadata destinasi (nama, kategori, tags, aktivitas, deskripsi, lokasi).
2. Buat TF-IDF vector dari content text.
3. Hitung cosine similarity antara preferensi pengguna dan destinasi.
4. Filter berdasarkan budget tier.
5. Urutkan berdasarkan skor dan ambil top-K.

### Implementasi Saat Ini

Saat ini, recommender menggunakan **data dummy** di `src/services/recommender_service.py`. Empat destinasi dummy tersedia:

| ID | Nama | Kategori | Sub-Kategori | Lokasi | Budget Tier |
|---|---|---|---|---|---|
| DUMMY-001 | Pantai Kuta | nature | beach | Badung | low, medium, high |
| DUMMY-002 | Pura Tirta Empul | culture | temple | Gianyar | medium, high |
| DUMMY-003 | Tegenungan Waterfall | nature | waterfall | Gianyar | low, medium, high |
| DUMMY-004 | Garuda Wisnu Kencana | recreation | landmark | Badung | medium, high |

## Struktur File Recommender

```text
src/models/
├── train_recommender.py        training script (skeleton)
├── recommender.py              DummyRecommender class (skeleton)
└── evaluate_recommender.py     evaluasi (skeleton)

src/services/
└── recommender_service.py      service layer dengan data dummy
```

## Cara Kerja Service Layer

### Fungsi `recommend_destinations()`

Parameter:

| Parameter | Tipe | Default | Deskripsi |
|---|---|---|---|
| `budget_tier` | string | (wajib) | Budget tier: low, medium, atau high |
| `preferred_categories` | list string | None | Filter kategori |
| `preferred_sub_categories` | list string | None | Filter sub-kategori |
| `preferred_locations` | list string | None | Filter lokasi (kabupaten/kota) |
| `top_k` | integer | 5 | Jumlah rekomendasi maksimal |

Alur pemrosesan:

1. **Filter budget tier**: hanya destinasi yang cocok dengan budget tier pengguna.
2. **Filter kategori**: jika ada preferensi kategori, hanya destinasi dengan kategori yang cocok.
3. **Filter sub-kategori**: jika ada preferensi sub-kategori, hanya destinasi yang cocok.
4. **Filter lokasi**: jika ada preferensi lokasi, hanya destinasi di lokasi yang cocok.
5. **Sortir**: urutkan berdasarkan skor (tertinggi ke terendah).
6. **Limit**: ambil top-K hasil.

### Fungsi `_build_match_reasons()`

Membangun daftar alasan kecocokan untuk setiap destinasi:

- Mengambil match reasons yang sudah ada di data destinasi.
- Menambahkan alasan budget tier jika belum ada.

### Fungsi `_format_destination()`

Memformat data destinasi untuk response:

- Menghapus field `budget_tiers` (internal, tidak dikirim ke frontend).
- Menambahkan match reasons yang sudah dibangun.

## Model Layer (Rencana)

### `DummyRecommender` (`src/models/recommender.py`)

Class placeholder yang saat ini mengembalikan destinasi tanpa pemrosesan. Akan diganti dengan implementasi nyata.

### Training (Rencana)

Saat model nyata diimplementasikan, langkah training yang direncanakan:

1. Muat dataset final dari `data/final/`.
2. Bangun content text untuk setiap destinasi.
3. Buat TF-IDF vectorizer menggunakan Scikit-learn.
4. Simpan vectorizer ke `artifacts/vectorizer.pkl`.
5. Simpan metadata model ke `artifacts/metadata.json`.

### Evaluasi (Rencana)

Metrik evaluasi yang direncanakan:

- Relevansi rekomendasi terhadap preferensi pengguna.
- Cakupan kategori dan lokasi.
- Kesesuaian dengan budget tier.

## Kategori dan Sub-Kategori yang Didukung

### Kategori

- `nature`
- `culture`
- `recreation`
- `general`

### Sub-Kategori

- `beach`
- `temple`
- `waterfall`
- `forest`
- `mountain`
- `museum`
- `village`
- `waterpark`
- `landmark`
- `shopping`

Daftar ini didefinisikan di `src/utils/constants.py`.

## Integrasi dengan Backend

Recommender service dipanggil oleh route handler `POST /plan-trip` di `app/backend/api/routes.py`:

```text
POST /plan-trip
    → classify_budget()
    → allocate_budget()
    → recommend_destinations()   ← recommender service
    → return PlanTripResponse
```

## Migrasi dari Dummy ke Model Nyata

Saat model nyata siap, langkah migrasi:

1. Implementasikan `train_recommender.py` untuk training.
2. Jalankan training untuk menghasilkan artifact.
3. Perbarui `recommender_service.py` untuk memuat artifact dan menggunakan TF-IDF cosine similarity.
4. Hapus `DUMMY_DESTINATIONS`.
5. Perbarui test di `tests/test_recommender_service.py`.
6. Pastikan semua test lulus.

## Referensi

- API Contract: [API_CONTRACT.md](API_CONTRACT.md)
- Arsitektur: [ARCHITECTURE.md](ARCHITECTURE.md)
- Data Pipeline: [DATA_PIPELINE_GUIDE.md](DATA_PIPELINE_GUIDE.md)
- Budget Engine: [BUDGET_ENGINE_GUIDE.md](BUDGET_ENGINE_GUIDE.md)
- Scope MVP: [MVP_SCOPE.md](MVP_SCOPE.md)
