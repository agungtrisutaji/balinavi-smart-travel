# Dokumentasi Data — BaliNavi

Folder ini berisi dokumentasi teknis tentang proses pengolahan data destinasi wisata Bali untuk sistem rekomendasi BaliNavi.

## Daftar Dokumen

| # | Dokumen | Deskripsi | Status |
|---|---|---|---|
| 01 | [Data Cleaning, EDA, dan Preprocessing](01_DATA_CLEANING_EDA_PREPROCESSING.md) | Pembersihan data, eksplorasi, normalisasi, feature engineering, dan validasi kualitas | ✅ Selesai |

## Alur Pipeline Data

```
data/raw/                         Dataset mentah (1452 destinasi)
    │
    ▼
[01] Cleaning + EDA + Preprocessing
    │   • Drop baris invalid
    │   • Normalisasi harga/kategori/lokasi/rating
    │   • Deduplikasi
    │   • Data quality scoring
    │
    ├── data/processed/            Dataset bersih (1443 × 23 kolom)
    │
    ▼
[01] Feature Engineering
    │   • Content text enrichment (5 jenis)
    │   • Popularity score
    │   • Budget tiers
    │   • Recommendation eligibility
    │
    ├── data/final/                Dataset model-ready (1443 × 27 kolom)
    │
    ▼
[Berikutnya] Model Training
    │   • TF-IDF vectorization
    │   • Cosine similarity matrix
    │
    └── artifacts/                 Model artifacts
```

## Hubungan dengan Dokumen Lain

| Dokumen | Lokasi | Hubungan |
|---|---|---|
| Dataset Contract | [../DATASET_CONTRACT.md](../DATASET_CONTRACT.md) | Kontrak schema yang harus dipenuhi |
| Data Quality Rules | [../DATA_QUALITY_RULES.md](../DATA_QUALITY_RULES.md) | Aturan validasi per kolom |
| Data Pipeline Guide | [../DATA_PIPELINE_GUIDE.md](../DATA_PIPELINE_GUIDE.md) | Alur pipeline end-to-end |
| Recommender Guide | [../RECOMMENDER_GUIDE.md](../RECOMMENDER_GUIDE.md) | Panduan model rekomendasi |

## Cara Menjalankan Notebook

```bash
# Dari root project
cd notebooks/
jupyter notebook 01_data_cleaning_imputation_preprocessing_eda_quality_validation.ipynb
```

Atau Run All cells secara berurutan. Output CSV akan disimpan otomatis ke `data/processed/` dan `data/final/`.

### Dependensi

```
pandas >= 2.0
numpy >= 1.24
matplotlib >= 3.7
```
