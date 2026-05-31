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

Saat ini, recommender menggunakan model **Content-Based Filtering** nyata yang diimplementasikan di `src/models/recommender.py` dan dilatih menggunakan dataset destinasi Bali yang lengkap (`data/clustered/bali_destination.csv`). Sistem ini dilengkapi dengan **DummyRecommender** sebagai fallback (backward compatibility) jika model artifacts belum tersedia.

## Struktur File Recommender

```text
src/models/
├── train_recommender.py        training script & CLI entry point
├── recommender.py              ContentBasedRecommender & DummyRecommender
└── evaluate_recommender.py     modul evaluasi model & metrik

src/services/
└── recommender_service.py      service layer dengan lazy loading & fallback
```

## Cara Kerja Service Layer

### Fungsi `recommend_destinations()`

Parameter:

| Parameter | Tipe | Default | Deskripsi |
|---|---|---|---|
| `budget_tier` | string | (wajib) | Budget tier: low, medium, atau high |
| `preferred_categories` | list string | None | Filter kategori utama |
| `preferred_sub_categories` | list string | None | Filter sub-kategori |
| `preferred_locations` | list string | None | Filter lokasi (kabupaten/kota) |
| `top_k` | integer | 5 | Jumlah rekomendasi maksimal |

Alur pemrosesan:

1. **Lazy Loading Singleton**: Memuat real model dari folder `artifacts/`. Jika artifacts tidak ditemukan, sistem otomatis fallback ke `DummyRecommender` menggunakan data dummy statis (`DUMMY_DESTINATIONS`).
2. **Build Query Text**: Menggabungkan parameter preferensi pengguna (`preferred_categories`, `preferred_sub_categories`, `preferred_locations`) menjadi satu string query text.
3. **TF-IDF Transform**: Transformasi string query menjadi vector space menggunakan `TfidfVectorizer` yang telah dilatih.
4. **Cosine Similarity**: Menghitung skor kemiripan antara vector query pengguna dengan matrix TF-IDF seluruh destinasi di Bali.
5. **Hybrid Scoring**: Menggabungkan skor kemiripan cosine dengan bobot tambahan berbasis kecocokan kategori, sub-kategori, lokasi, skor popularitas, serta sanksi (penalty) jika budget tier tidak cocok.
6. **Sort & Limit**: Mengurutkan destinasi berdasarkan skor hybrid akhir dari yang tertinggi dan membatasi output sebanyak `top_k`.
7. **Format & Match Reasons**: Memformat respons sesuai API contract dan menyusun penjelasan alasan pencocokan (`match_reasons`) secara dinamis.

### Formula Hybrid Scoring

Skor akhir untuk setiap destinasi dihitung menggunakan rumus berikut:

```text
final_score = (cosine_sim × 0.6)
            + (category_match × 0.15)
            + (location_match × 0.10)
            + (popularity_score × 0.10)
            + (sub_category_match × 0.05)
            + budget_penalty
```

Di mana:
- `cosine_sim` (0.0 - 1.0): Kemiripan teks deskriptif destinasi dengan preferensi pengguna.
- `category_match` (1.0 jika cocok, 0.0 jika tidak): Kecocokan dengan kategori utama yang dipilih.
- `location_match` (1.0 jika cocok, 0.0 jika tidak): Kecocokan dengan lokasi/kabupaten yang dipilih.
- `popularity_score` (0.0 - 1.0): Skor popularitas destinasi yang dinormalisasi.
- `sub_category_match` (1.0 jika cocok, 0.0 jika tidak): Kecocokan dengan sub-kategori yang dipilih.
- `budget_penalty` (`-0.3` jika budget tier destinasi tidak cocok dengan preferensi pengguna, `0.0` jika cocok).

---

## Model Layer

### `ContentBasedRecommender` (`src/models/recommender.py`)

Class utama yang membungkus logika scoring, loading artifact dari `artifacts/` (`vectorizer.pkl`, `tfidf_matrix.pkl`, `destination_data.pkl`), dan mengembalikan hasil rekomendasi yang terformat.

### Training (`src/models/train_recommender.py`)

Proses training memproses data destinasi dengan langkah-langkah:
1. Muat dataset dari `data/clustered/bali_destination.csv`.
2. Filter destinasi yang bertanda `recommendation_eligible == True`.
3. Lakukan pengayaan teks (`content_text`) dengan menggabungkan deskripsi, kategori, lokasi, serta `cluster_label`.
4. Latih `TfidfVectorizer` berbasis n-gram `(1, 2)`.
5. Simpan artifact model ke folder `artifacts/`.

**CLI Command:**
```bash
python -m src.models.train_recommender --data-path data/clustered/bali_destination.csv --output-dir artifacts/
```

### Evaluasi (`src/models/evaluate_recommender.py`)

Model dievaluasi menggunakan tiga metrik utama berdasarkan skenario pengguna nyata:

| Metrik | Deskripsi | Hasil Evaluasi | Target Minimum |
|---|---|---|---|
| **Precision@K** | Persentase destinasi direkomendasikan yang relevan dengan preferensi pengguna. | **1.0** | ≥ 0.6 |
| **Category Coverage** | Keanekaragaman kategori destinasi yang direkomendasikan. | **0.93** | ≥ 0.5 |
| **Budget Compliance Rate** | Persentase kesesuaian destinasi dengan budget tier pengguna. | **1.0** | ≥ 0.7 |

---

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
    → recommend_destinations()   ← recommender service (ContentBasedRecommender)
    → return PlanTripResponse
```

## Status Migrasi dari Dummy ke Model Nyata

Status migrasi: **SELESAI (COMPLETED)** ✅

Semua langkah migrasi telah diselesaikan:
1. Implementasi `train_recommender.py` selesai dan sukses dieksekusi.
2. Artifacts model (`vectorizer.pkl`, `tfidf_matrix.pkl`, `destination_data.pkl`, `metadata.json`) telah digenerate dan disimpan.
3. Service layer `recommender_service.py` diperbarui menggunakan lazy loading singleton dan menyertakan fallback data dummy.
4. Unit tests di `tests/test_recommender_service.py` telah diperbarui dan semuanya **lulus 100% (19/19 passed)**.

## Referensi

- API Contract: [API_CONTRACT.md](API_CONTRACT.md)
- Arsitektur: [ARCHITECTURE.md](ARCHITECTURE.md)
- Data Pipeline: [DATA_PIPELINE_GUIDE.md](DATA_PIPELINE_GUIDE.md)
- Budget Engine: [BUDGET_ENGINE_GUIDE.md](BUDGET_ENGINE_GUIDE.md)
- Scope MVP: [MVP_SCOPE.md](MVP_SCOPE.md)
