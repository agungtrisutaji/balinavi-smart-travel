# Panduan Data Pipeline - BaliNavi

Dokumen ini menjelaskan alur data pipeline, dari dataset mentah sampai model-ready dataset, pada BaliNavi MVP.

## Ikhtisar Data Pipeline

Data pipeline BaliNavi memproses dataset destinasi Bali melalui tiga tahap:

```text
data/raw/              dataset mentah asli
    │
    ▼
src/data/load_data.py        memuat data
    │
    ▼
src/preprocessing/preprocess.py    pembersihan dan normalisasi
    │
    ▼
data/processed/        dataset yang sudah dibersihkan
    │
    ▼
src/features/build_features.py     feature engineering
    │
    ▼
data/final/            dataset model-ready
    │
    ▼
src/models/train_recommender.py    training model
    │
    ▼
artifacts/             model dan vectorizer artifact
```

## Tahapan Data Pipeline

### 1. Data Loading (`src/data/load_data.py`)

Fungsi `load_destination_data()` bertanggung jawab memuat dataset mentah dari folder `data/raw/`.

Status saat ini: skeleton (mengembalikan list kosong). Akan diimplementasikan untuk memuat file CSV destinasi Bali.

Tanggung jawab:

- Membaca file dataset dari `data/raw/`.
- Mengembalikan data sebagai list of dict.
- Menangani format file (CSV, JSON, dll).

### 2. Preprocessing (`src/preprocessing/preprocess.py`)

Fungsi `preprocess_destination_data()` bertanggung jawab membersihkan dan menormalisasi data.

Status saat ini: skeleton (mengembalikan data tanpa perubahan). Akan diimplementasikan dengan langkah pembersihan.

Tanggung jawab yang direncanakan:

- Menghapus duplikat.
- Menormalisasi nama kategori dan sub-kategori.
- Menangani nilai yang hilang (missing values).
- Membangun quality flags.
- Membersihkan format harga dan rating.
- Menyimpan hasil ke `data/processed/`.

### 3. Feature Engineering (`src/features/build_features.py`)

Fungsi `build_destination_features()` bertanggung jawab membangun fitur untuk model rekomendasi.

Status saat ini: skeleton (mengembalikan data tanpa perubahan). Akan diimplementasikan dengan fitur berikut.

Fitur yang direncanakan:

- **content_text**: gabungan dari nama, kategori, tags, aktivitas, deskripsi, dan lokasi.
- **normalized_price**: normalisasi harga tiket.
- **popularity_score**: skor popularitas berdasarkan rating dan jumlah review.
- **budget_score**: skor kesesuaian dengan budget tier.
- Menyimpan hasil ke `data/final/`.

### 4. Model Training (`src/models/train_recommender.py`)

Fungsi `train_recommender()` bertanggung jawab melatih model rekomendasi.

Status saat ini: skeleton (mengembalikan status not_implemented). Akan diimplementasikan dengan pendekatan berikut.

Pendekatan yang direncanakan:

- Membangun TF-IDF vectorizer dari content_text.
- Menghitung cosine similarity matrix.
- Menyimpan vectorizer dan model ke `artifacts/`.

### 5. Model Artifacts (`artifacts/`)

File artifact yang diharapkan setelah training:

```text
artifacts/vectorizer.pkl      TF-IDF vectorizer
artifacts/recommender.pkl     model rekomendasi
artifacts/metadata.json       metadata model
```

Artifact disimpan menggunakan Joblib.

## Konvensi Folder Data

| Folder | Isi | Aturan Commit |
|---|---|---|
| `data/raw/` | Dataset mentah asli | Jangan commit file besar tanpa persetujuan |
| `data/processed/` | Dataset yang sudah dibersihkan | Jangan commit file besar tanpa persetujuan |
| `data/final/` | Dataset model-ready | Jangan commit file besar tanpa persetujuan |
| `artifacts/` | Model dan vectorizer | Commit hanya jika diperlukan untuk demo |

## Atribut Dataset Destinasi

Dataset destinasi Bali diharapkan memiliki atribut berikut:

| Atribut | Tipe | Deskripsi |
|---|---|---|
| destination_id | string | ID unik destinasi |
| name | string | Nama destinasi |
| category | string | Kategori utama (nature, culture, recreation, general) |
| sub_category | string | Sub-kategori (beach, temple, waterfall, dll) |
| district | string | Kecamatan |
| regency_city | string | Kabupaten atau kota |
| estimated_ticket_price | integer | Estimasi harga tiket per orang (IDR) |
| rating | float | Rating destinasi |
| review_count | integer | Jumlah review |
| latitude | float | Koordinat lintang |
| longitude | float | Koordinat bujur |
| maps_url | string | URL Google Maps (opsional) |
| image_url | string | URL gambar (opsional) |

## Status Implementasi Saat Ini

| Komponen | Status |
|---|---|
| `load_data.py` | Skeleton |
| `preprocess.py` | Skeleton |
| `build_features.py` | Skeleton |
| `train_recommender.py` | Skeleton |
| `recommender_service.py` | Menggunakan data dummy |

Saat ini, `recommender_service.py` menggunakan `DUMMY_DESTINATIONS` sebagai data sementara sampai pipeline data selesai diimplementasikan.

## Hubungan dengan Service Layer

Setelah data pipeline diimplementasikan:

- `recommender_service.py` akan menggunakan model artifact dari `artifacts/` alih-alih data dummy.
- Service akan memuat vectorizer dan model saat startup.
- Rekomendasi akan dihasilkan menggunakan cosine similarity dari TF-IDF.

## Referensi

- Arsitektur: [ARCHITECTURE.md](ARCHITECTURE.md)
- Scope MVP: [MVP_SCOPE.md](MVP_SCOPE.md)
- Panduan Recommender: [RECOMMENDER_GUIDE.md](RECOMMENDER_GUIDE.md)
