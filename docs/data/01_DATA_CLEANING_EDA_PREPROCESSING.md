# Dokumentasi Data Cleaning, EDA, dan Preprocessing

Dokumen ini menjelaskan proses pembersihan, eksplorasi, dan preprocessing dataset destinasi wisata Bali yang dilakukan di notebook [`01_data_cleaning_imputation_preprocessing_eda_quality_validation.ipynb`](../../notebooks/01_data_cleaning_imputation_preprocessing_eda_quality_validation.ipynb).

## Daftar Isi

- [Ringkasan](#ringkasan)
- [Input dan Output](#input-dan-output)
- [Tahap 1: Setup dan Konfigurasi](#tahap-1-setup-dan-konfigurasi)
- [Tahap 2: Load Raw Dataset dan Audit Schema](#tahap-2-load-raw-dataset-dan-audit-schema)
- [Tahap 3: Cleaning dan Normalization Helpers](#tahap-3-cleaning-dan-normalization-helpers)
- [Tahap 4: Clean, Impute, dan Build Processed Dataset](#tahap-4-clean-impute-dan-build-processed-dataset)
- [Tahap 5: Feature Engineering — Build Final Dataset](#tahap-5-feature-engineering--build-final-dataset)
- [Tahap 6: Exploratory Data Analysis (EDA)](#tahap-6-exploratory-data-analysis-eda)
- [Tahap 7: Validation Assertions](#tahap-7-validation-assertions)
- [Tahap 8: Save Output](#tahap-8-save-output)
- [Statistik Hasil](#statistik-hasil)
- [Keputusan Desain](#keputusan-desain)
- [Referensi](#referensi)

---

## Ringkasan

Notebook ini memproses dataset raw 1452 destinasi wisata Bali menjadi dua output tervalidasi:

1. **Processed dataset** (`data/processed/bali_destinations.csv`) — dataset bersih dengan 23 kolom sesuai kontrak.
2. **Final dataset** (`data/final/bali_destinations.csv`) — dataset model-ready dengan 27 kolom (23 processed + 4 fitur tambahan).

Proses mencakup:
- Data cleaning (drop baris invalid, trim whitespace, hapus duplikat)
- Imputation (fallback aman untuk harga/rating/review/district)
- Normalisasi (harga, kategori, lokasi, rating, koordinat, URL)
- Feature engineering (content_text enrichment, popularity_score, budget_tiers, eligibility flag)
- EDA (distribusi, outlier, missingness, koordinat)
- Validasi kualitas (assertion kontrak, data quality score)

---

## Input dan Output

### Input

| File | Deskripsi |
|---|---|
| `data/raw/bali_tourist_destination_with_harga_full_1452.csv` | Dataset mentah 1452 destinasi wisata Bali dari Google Maps |

Kolom raw (12 kolom):

| Kolom Raw | Tipe | Deskripsi |
|---|---|---|
| `id_tempat` | string | ID tempat dari sumber data |
| `nama_tempat_wisata` | string | Nama destinasi (Bahasa Indonesia) |
| `kategori` | string | Kategori: Alam, Budaya, Rekreasi, Umum |
| `kecamatan` | string | Nama kecamatan |
| `kabupaten_kota` | string | Nama kabupaten/kota dengan prefix |
| `harga_destinasi` | int/string | Harga tiket (format bervariasi) |
| `rating` | float | Rating Google Maps (0.0-5.0) |
| `jumlah_rating` | int | Jumlah review/rating |
| `latitude` | float | Koordinat lintang |
| `longitude` | float | Koordinat bujur |
| `link_google_maps` | string | URL Google Maps |
| `link_gambar` | string | URL gambar dari Google |

### Output

| File | Rows | Cols | Deskripsi |
|---|---|---|---|
| `data/processed/bali_destinations.csv` | 1443 | 23 | Dataset bersih sesuai [DATASET_CONTRACT.md](../DATASET_CONTRACT.md) |
| `data/final/bali_destinations.csv` | 1443 | 27 | Dataset model-ready dengan fitur TF-IDF |

---

## Tahap 1: Setup dan Konfigurasi

**Notebook Cell**: Setup (Cell 2)

### Yang dilakukan:
- Import library: `pandas`, `numpy`, `matplotlib`, `re`, `pathlib`
- Deteksi root project otomatis (bisa dijalankan dari folder `notebooks/` maupun root)
- Import konstanta resmi dari `src/utils/constants.py`:
  - `SUPPORTED_CATEGORIES`: `{nature, culture, recreation, general}`
  - `SUPPORTED_SUB_CATEGORIES`: `{beach, temple, waterfall, mountain, forest, museum, village, waterpark, landmark, shopping}`
- Definisi path input/output eksplisit
- Membuat folder output jika belum ada

### Dependensi:
```
pandas >= 2.0
numpy >= 1.24
matplotlib >= 3.7
```

---

## Tahap 2: Load Raw Dataset dan Audit Schema

**Notebook Cell**: Load Raw Dataset and Audit Schema (Cell 4)

### Yang dilakukan:
1. Membaca CSV raw ke `raw_df`
2. Menghitung statistik dasar (jumlah baris, kolom, duplikat, ukuran file)
3. Audit schema: tipe data, missing count, missing %, unique count per kolom
4. Deteksi blank string pada kolom teks
5. Menampilkan sampel data

### Temuan Audit:
| Metrik | Nilai |
|---|---|
| Total baris raw | 1452 |
| Total kolom | 12 |
| Duplikat (nama+lokasi) | 9 |
| Ukuran file | 0.7 MB |
| Missing values | 0 di semua kolom kecuali `link_gambar` (4 null) |
| Blank strings | 0 di semua kolom teks |

---

## Tahap 3: Cleaning dan Normalization Helpers

**Notebook Cell**: Cleaning and Normalization Helpers (Cell 6)

Bagian ini mendefinisikan semua fungsi reusable yang digunakan di tahap cleaning dan feature engineering. Fungsi-fungsi ini dirancang agar bisa dipindahkan ke `src/preprocessing/preprocess.py` dan `src/features/build_features.py`.

### 3.1 Konstanta Mapping

#### Kategori (`CATEGORY_MAP`)
```
"alam"     → "nature"
"budaya"   → "culture"
"rekreasi" → "recreation"
"umum"     → "general"
```

#### Detail Sub-kategori (`DETAIL_SUBCATEGORY_MAP`)
Mapping dari detail kategori raw (bagian setelah tanda hubung) ke sub-kategori:
```
"pantai"      → "beach"      "hutan"      → "forest"
"pura"        → "temple"     "gunung"     → "mountain"
"candi"       → "temple"     "bukit"      → "mountain"
"air terjun"  → "waterfall"  "museum"     → "museum"
"desa"        → "village"    "waterpark"  → "waterpark"
"desa wisata" → "village"    "landmark"   → "landmark"
"taman air"   → "waterpark"  "belanja"    → "shopping"
"monumen"     → "landmark"   "pasar"      → "shopping"
"tugu"        → "landmark"   "mall"       → "shopping"
```

#### Inferensi Sub-kategori dari Nama (`SUBCATEGORY_PATTERNS`)
Jika detail kategori kosong, nama destinasi diperiksa dengan regex pattern:
```
"waterfall" ← /air\s+terjun/, /waterfall/, /tegenungan/, /gitgit/, /sekumpul/
"beach"     ← /pantai/, /beach/, /sanur/, /kuta/, /nusa\s+dua/
"temple"    ← /pura/, /candi/, /temple/
"forest"    ← /hutan/, /forest/, /monkey\s+forest/
"mountain"  ← /gunung/, /bukit/, /mount/, /hill/, /cliff/
"museum"    ← /museum/
"village"   ← /desa/, /village/, /kampung/
"shopping"  ← /pasar/, /mall/, /market/, /shopping/
"landmark"  ← /patung/, /monumen/, /tugu/, /taman/, /park/, ...
```

#### Fallback Sub-kategori (`SUBCATEGORY_FALLBACK`)
Jika tidak ditemukan dari detail atau pattern nama:
```
nature     → "forest"
culture    → "temple"
recreation → "landmark"
general    → "landmark"
```

#### Batas Koordinat Bali
```
Latitude:  -9.5  sampai  -8.0
Longitude: 114.4 sampai  115.8
```

### 3.2 Fungsi Utility

| Fungsi | Input → Output | Deskripsi |
|---|---|---|
| `strip_to_none(value)` | any → str \| None | Trim whitespace, collapse multi-space, return None jika kosong |
| `normalize_key(value)` | any → str | Lowercase + strip untuk dedup key |
| `title_or_none(value)` | any → str \| None | Title case atau None |
| `normalize_regency_city(value)` | any → str \| None | Hapus prefix "Kabupaten"/"Kota", title case |

### 3.3 Fungsi Parsing

| Fungsi | Aturan | Contoh |
|---|---|---|
| `parse_category(value)` | Split pada `-`, map ke EN, case-insensitive | `"Alam - Pantai"` → `("nature", "Pantai", "Alam - Pantai")` |
| `infer_subcategory(name, detail, main)` | Detail → Pattern nama → Fallback | `("Pantai Kuta", None, "nature")` → `("beach", "keyword")` |
| `parse_price(value)` | Hapus Rp/IDR, strip non-digit, negatif→0 | `"Rp 50.000"` → `50000`, `"Gratis"` → `0` |
| `parse_nonnegative_int(value)` | Parse integer, negatif→0, NaN→0 | `"1234"` → `1234`, `NaN` → `0` |
| `parse_rating(value)` | Numeric, clamp 0.0–5.0 | `"4.7"` → `4.7`, `"6.0"` → `5.0` |
| `price_level(price)` | Kategorisasi threshold | `0`→`"free"`, `≤25k`→`"low"`, `≤75k`→`"medium"`, `>75k`→`"high"` |
| `budget_tiers(price)` | Budget tier string | `≤50k`→`"low,medium,high"`, `≤100k`→`"medium,high"`, `>100k`→`"high"` |

### 3.4 Fungsi Validasi

| Fungsi | Deskripsi |
|---|---|
| `valid_url_or_none(value)` | Return None jika URL tidak dimulai `http://` atau `https://` |
| `valid_bali_coordinates(lat, lon)` | Return `(NaN, NaN, False)` jika di luar batas Bali |

### 3.5 Fungsi Content Text Enrichment

Enrichment bertujuan memperkaya `content_text` (input utama TF-IDF) dari rata-rata 7.5 token menjadi ~21 token per destinasi.

| Fungsi | Deskripsi | Contoh Token |
|---|---|---|
| **Keyword Enrichment** (`SUBCATEGORY_KEYWORDS`) | Menambah 6-8 keyword domain per sub-kategori | beach → `pantai, ombak, pasir, surfing, snorkeling, sunset, pesisir` |
| `price_text_tokens(row)` | Encode harga sebagai token teks | `gratis, tanpa_tiket`, `harga_premium, eksklusif` |
| `rating_text_tokens(row)` | Encode rating dan popularitas | `rating_tinggi, sangat_populer, favorit`, `banyak_ulasan` |
| `normalize_name_for_content(name)` | Bersihkan noise dari nama | `"Uma.palak.(parkir.2)"` → `"uma palak"` |
| `bali_region_tokens(lat, lon)` | Encode region geografis | `bali_utara`, `bali_selatan`, `bali_barat` |

Pembagian region Bali berdasarkan koordinat:
```
lat > -8.4               → bali_utara    (Buleleng, Bangli utara)
lat < -8.65              → bali_selatan  (Kuta, Uluwatu, Nusa Dua)
-8.65 ≤ lat ≤ -8.4      → bali_tengah   (Ubud, Gianyar)
lon < 115.0              → bali_barat    (Jembrana, Tabanan barat)
lon > 115.5              → bali_timur    (Karangasem, Klungkung timur)
```

---

## Tahap 4: Clean, Impute, dan Build Processed Dataset

**Notebook Cell**: Clean, Impute, and Build Processed Dataset (Cell 8)

### 4.1 Alur Proses

```
raw_df (1452 rows, 12 cols)
    │
    ├── 1. Rename kolom raw → kontrak
    ├── 2. Drop baris: nama kosong/< 2 char     → 0 dropped
    ├── 3. Drop baris: lokasi kosong              → 0 dropped
    ├── 4. Normalisasi regency_city (hapus prefix, title case)
    ├── 5. Normalisasi district (title case, fallback "Unknown")
    ├── 6. Parse kategori → category_main, detail_category
    ├── 7. Infer sub_category (detail → nama pattern → fallback)
    ├── 8. Parse harga → estimated_ticket_price (int, non-negatif)
    ├── 9. Compute is_free, price_level
    ├── 10. Parse rating (clamp 0.0-5.0)
    ├── 11. Parse review_count (non-negatif)
    ├── 12. Validasi URL (maps_url, image_url)
    ├── 13. Set field opsional kosong: description, tags, activity = None
    ├── 14. Validasi koordinat (batas Bali) → has_coordinates
    ├── 15. Deduplikasi (name+regency_city, sort by completeness) → 9 dropped
    ├── 16. Compute data_quality_score (12 weights)
    └── 17. Generate destination_id (DEST-001, DEST-002, ...)
    │
    ▼
processed_df (1443 rows, 23 cols)
```

### 4.2 Rename Kolom

| Kolom Raw | Kolom Processed |
|---|---|
| `nama_tempat_wisata` | `name` |
| `jumlah_rating` | `review_count` |
| `link_google_maps` | `maps_url` |
| `link_gambar` | `image_url` |

Kolom `rating`, `latitude`, `longitude` tetap.

### 4.3 Aturan Drop Baris

| Aturan | Jumlah Dropped | Keterangan |
|---|---|---|
| Nama kosong / < 2 karakter | 0 | Semua baris punya nama valid |
| Lokasi (kabupaten_kota) kosong | 0 | Semua baris punya lokasi |
| Duplikat (nama+lokasi normalized) | 9 | Keep baris paling lengkap |

### 4.4 Deduplikasi

Strategi:
1. Buat key: `normalize_key(name) + "|" + normalize_key(regency_city)`
2. Sort by: `(dup_key ASC, completeness_score DESC, id_tempat ASC)`
3. Keep first (paling lengkap) dari setiap grup duplikat
4. `completeness_score` = jumlah kolom non-null dari 13 quality columns

### 4.5 Data Quality Score

Skor kualitas per baris (0.0 - 1.0) dihitung sebagai weighted sum dari 12 komponen:

| Komponen | Weight | Kondisi Bernilai |
|---|---|---|
| `name` tidak kosong | 0.20 | Selalu True (sudah di-filter) |
| `category_main` ≠ "general" | 0.15 | Kategori spesifik teridentifikasi |
| `sub_category` bukan fallback | 0.10 | Sub-kategori dari detail/pattern, bukan default |
| `description` tidak kosong | 0.10 | Selalu 0 (raw tidak punya) |
| `tags` tidak kosong | 0.05 | Selalu 0 (raw tidak punya) |
| `activity` tidak kosong | 0.05 | Selalu 0 (raw tidak punya) |
| `regency_city` tidak kosong | 0.10 | Selalu True (sudah di-filter) |
| `district` tidak kosong | 0.05 | True jika kecamatan ada |
| `rating` > 0.0 | 0.05 | Punya rating |
| `review_count` > 0 | 0.05 | Punya review |
| `has_coordinates` | 0.05 | Koordinat valid di Bali |
| `estimated_ticket_price` ≥ 0 | 0.05 | Selalu True (parse clamp ke 0) |

**Distribusi skor**: min=0.45, mean=0.695, max=0.80

### 4.6 Schema Processed Dataset (23 kolom)

| Kolom | Tipe | Nullable | Deskripsi |
|---|---|---|---|
| `destination_id` | string | No | ID unik format `DEST-001` |
| `name` | string | No | Nama destinasi (trimmed) |
| `category_raw` | string | No | Kategori asli dari raw |
| `category_main` | string | No | Kategori utama EN |
| `detail_category` | string | Yes | Detail dari raw (mostly null) |
| `sub_category` | string | No | Sub-kategori inferred |
| `description` | string | Yes | Selalu null (raw tidak punya) |
| `tags` | string | Yes | Selalu null (raw tidak punya) |
| `activity` | string | Yes | Selalu null (raw tidak punya) |
| `regency_city` | string | No | Kabupaten/kota (title case) |
| `district` | string | No | Kecamatan (title case, fallback "Unknown") |
| `estimated_ticket_price` | int | No | Harga tiket IDR (≥ 0) |
| `is_free` | bool | No | True jika harga = 0 |
| `price_level` | string | No | {free, low, medium, high} |
| `rating` | float | No | 0.0 – 5.0 |
| `review_count` | int | No | ≥ 0 |
| `latitude` | float | Yes | 7 null (invalid coords) |
| `longitude` | float | Yes | 7 null (invalid coords) |
| `maps_url` | string | Yes | URL Google Maps |
| `image_url` | string | Yes | URL gambar (4 null) |
| `has_coordinates` | bool | No | False jika coords invalid |
| `has_description` | bool | No | Selalu False |
| `data_quality_score` | float | No | 0.45 – 0.80 |

---

## Tahap 5: Feature Engineering — Build Final Dataset

**Notebook Cell**: Build Model-Ready Final Dataset (Cell 10)

### 5.1 Alur Proses

```
processed_df (1443 rows, 23 cols)
    │
    ├── 1. Build enriched content_text (5 jenis enrichment)
    ├── 2. Compute popularity_score (min-max normalized)
    ├── 3. Compute budget_tiers
    └── 4. Compute recommendation_eligible (8 kondisi)
    │
    ▼
final_df (1443 rows, 27 cols)
```

### 5.2 Content Text (`content_text`)

Content text adalah representasi teks destinasi yang menjadi input utama TF-IDF vectorizer untuk model rekomendasi.

**Konstruksi**:
```
content_text = [
    normalize_name_for_content(name),     # Improvement 4: nama dibersihkan
    category_main,                         # nature/culture/recreation/general
    sub_category,                          # beach/temple/waterfall/...
    detail_category,                       # dari raw (mostly null → skip)
    tags,                                  # null → skip
    activity,                              # null → skip
    description,                           # null → skip
    regency_city,                          # Badung/Gianyar/...
    district,                              # nama kecamatan
    + SUBCATEGORY_KEYWORDS[sub_category],  # Improvement 1: keyword domain
    + price_text_tokens(row),              # Improvement 2: sinyal harga
    + rating_text_tokens(row),             # Improvement 3: sinyal rating
    + bali_region_tokens(lat, lon),        # Improvement 5: region Bali
]
# Semua digabung lowercase, whitespace collapsed
```

**Contoh sebelum enrichment** (rata-rata 7.5 token):
```
"pantai padang galak nature beach denpasar denpasar barat"
```

**Contoh setelah enrichment** (rata-rata 21.3 token):
```
"pantai padang galak nature beach denpasar denpasar barat
 pantai ombak pasir laut surfing snorkeling sunset pesisir
 gratis tanpa_tiket rating_tinggi sangat_populer favorit
 cukup_ulasan bali_selatan"
```

**Dampak enrichment ke TF-IDF cosine similarity**:

| Metrik | Sebelum | Sesudah | Perubahan |
|---|---|---|---|
| Mean tokens per row | 7.5 | 21.3 | +184% |
| Rows ≤ 7 tokens | 863 (60.1%) | 0 (0%) | Semua diperkaya |
| Pairs sim = 1.0 (identik) | 5,968 | 153 | -97.4% |
| Pairs sim > 0.9 | 5,968 | 1,396 | -76.6% |

### 5.3 Popularity Score (`popularity_score`)

Formula:
```
raw_score = rating × log1p(review_count)
popularity_score = (raw_score - min) / (max - min)    # min-max normalization

# Override: jika rating==0 atau review_count==0 → popularity_score = 0.0
```

Range: 0.0 – 1.0, mean: 0.406, median: 0.402

### 5.4 Budget Tiers (`budget_tiers`)

| Harga Tiket | Budget Tiers | Arti |
|---|---|---|
| ≤ 50.000 | `"low,medium,high"` | Cocok untuk semua budget |
| > 50.000 dan ≤ 100.000 | `"medium,high"` | Budget menengah ke atas |
| > 100.000 | `"high"` | Hanya budget tinggi |

### 5.5 Recommendation Eligible (`recommendation_eligible`)

Destinasi dianggap eligible jika memenuhi **semua** 8 kondisi:

| # | Kondisi | Tujuan |
|---|---|---|
| 1 | `name` is not null | Punya nama valid |
| 2 | `category_main` ∈ SUPPORTED_CATEGORIES | Kategori yang didukung app |
| 3 | `sub_category` ∈ SUPPORTED_SUB_CATEGORIES | Sub-kategori yang didukung app |
| 4 | `regency_city` is not null | Punya lokasi |
| 5 | `data_quality_score` ≥ 0.4 | Kualitas data minimum |
| 6 | `has_coordinates` == True | Punya koordinat valid |
| 7 | Latitude & longitude dalam batas Bali | Berada di Bali |
| 8 | `content_text` length > 0 | Punya teks untuk TF-IDF |

**Hasil**: 1436 eligible / 7 not eligible (7 destinasi tanpa koordinat valid)

---

## Tahap 6: Exploratory Data Analysis (EDA)

**Notebook Cell**: EDA (Cells 12-15)

### 6.1 Missingness Analysis

Setelah cleaning:
- **0 missing** di semua kolom wajib
- **7 missing** di latitude/longitude (destinasi tanpa koordinat valid di Bali)
- **4 missing** di image_url
- **100% missing** di description, tags, activity (tidak ada di raw data)

### 6.2 Duplikat

| Tahap | Duplikat (nama+lokasi) |
|---|---|
| Raw | 9 |
| Processed | 0 (semua dihapus) |

### 6.3 Distribusi Kategori

| `category_main` | Jumlah | Persentase |
|---|---|---|
| general | 576 | 39.9% |
| nature | 523 | 36.2% |
| culture | 181 | 12.5% |
| recreation | 163 | 11.3% |

### 6.4 Distribusi Sub-Kategori

| `sub_category` | Jumlah | Top Source |
|---|---|---|
| landmark | 668 | Fallback (general/recreation) |
| beach | 229 | Pattern nama + detail |
| temple | 178 | Pattern nama + detail |
| waterfall | 136 | Pattern nama + detail |
| mountain | 73 | Pattern nama |
| forest | 67 | Fallback (nature) |
| village | 58 | Pattern nama |
| museum | 14 | Pattern nama |
| shopping | 14 | Pattern nama |
| waterpark | 6 | Detail / pattern |

### 6.5 Distribusi Lokasi

Semua 9 kabupaten/kota di Bali terrepresentasi:

| `regency_city` | Jumlah |
|---|---|
| Badung | 258 |
| Gianyar | 214 |
| Tabanan | 169 |
| Buleleng | 168 |
| Karangasem | 156 |
| Klungkung | 136 |
| Denpasar | 130 |
| Bangli | 110 |
| Jembrana | 102 |

### 6.6 Statistik Numerik

| Kolom | Mean | Median | Min | Max | Std |
|---|---|---|---|---|---|
| estimated_ticket_price | 19,199 | 10,000 | 0 | 350,000 | 44,460 |
| rating | 4.51 | 4.60 | 0.0 | 5.0 | 0.56 |
| review_count | 1,178 | 109 | 0 | 101,523 | 5,283 |
| data_quality_score | 0.695 | 0.70 | 0.45 | 0.80 | 0.11 |
| popularity_score | 0.406 | 0.402 | 0.0 | 1.0 | 0.18 |

### 6.7 Outlier (IQR Method)

| Kolom | Jumlah Outlier |
|---|---|
| estimated_ticket_price | 170 |
| review_count | 216 |

Top 3 harga tertinggi: Waterbom Bali (350K), Bali Exotic Marine Park (350K), Bali Dolphin Interaction (350K).
Top 3 review terbanyak: Tanah Lot (101K), Garuda Wisnu Kencana (70K), Monkey Forest (57K).

### 6.8 Koordinat

| Metrik | Nilai |
|---|---|
| Valid coordinates | 1436 |
| Invalid/missing coordinates | 7 |

7 destinasi tanpa koordinat valid semuanya dari kabupaten Tabanan.

### 6.9 Visualisasi yang Dihasilkan

1. **Bar chart**: distribusi `category_main`, `sub_category`, `regency_city`, `price_level`
2. **Histogram**: distribusi `estimated_ticket_price`, `rating`, `log1p(review_count)`
3. **Scatter plot**: koordinat destinasi valid pada peta Bali
4. **Tabel**: top 10 harga tertinggi, top 10 review terbanyak

---

## Tahap 7: Validation Assertions

**Notebook Cell**: Validation Assertions (Cell 17)

Notebook menjalankan serangkaian `assert` untuk memverifikasi bahwa output sesuai kontrak:

| Assertion | Deskripsi |
|---|---|
| `processed_df.columns == PROCESSED_COLUMNS` | Schema processed sesuai kontrak |
| `final_df.columns == FINAL_COLUMNS` | Schema final sesuai kontrak |
| `category_main` ∈ SUPPORTED_CATEGORIES | Semua kategori valid |
| `sub_category` ∈ SUPPORTED_SUB_CATEGORIES | Semua sub-kategori valid |
| `estimated_ticket_price` ≥ 0 | Harga non-negatif |
| `rating` antara 0.0 – 5.0 | Rating dalam range |
| `review_count` ≥ 0 | Review non-negatif |
| `data_quality_score` antara 0.0 – 1.0 | Skor kualitas valid |
| Tidak ada duplikat `destination_id` | ID unik |
| `popularity_score` antara 0.0 – 1.0 | Skor popularitas valid |
| `content_text` non-empty di eligible rows | Semua eligible punya teks |

Hasil: **Semua assertion passed** ✅

---

## Tahap 8: Save Output

**Notebook Cell**: Save (Cell 19)

```python
processed_df.to_csv("data/processed/bali_destinations.csv", index=False)
final_df.to_csv("data/final/bali_destinations.csv", index=False)
```

---

## Statistik Hasil

### Pipeline Summary

| Metrik | Nilai |
|---|---|
| Total baris raw | 1,452 |
| Dropped (nama kosong) | 0 |
| Dropped (lokasi kosong) | 0 |
| Dropped (duplikat) | 9 |
| Total processed | 1,443 |
| Total eligible | 1,436 |
| Total not eligible | 7 |
| Avg quality score | 0.695 |
| Gratis | 630 |
| Berbayar | 813 |

### Content Text Quality (Setelah Enrichment)

| Metrik | Nilai |
|---|---|
| Mean tokens per destinasi | 21.3 |
| Median tokens | 21.0 |
| Min tokens | 15 |
| Max tokens | 30 |
| Rows ≤ 7 tokens | 0 (0%) |
| Rows ≥ 20 tokens | 1,278 (88.6%) |

---

## Keputusan Desain

### 1. Tidak memfilter berdasarkan review count

Dataset mempertahankan semua 1436 eligible destinasi tanpa filter minimum review count, karena:
- Filter `review ≥ 100` akan menghilangkan 48.6% data
- Model content-based (TF-IDF) bekerja berdasarkan kesamaan teks, bukan popularitas
- `popularity_score` sudah menangani ranking berdasarkan review secara natural
- Destinasi dengan review rendah tetap valid untuk direkomendasikan (hidden gems)

### 2. Sub-kategori diinfer dari nama

Raw data hanya punya 4 kategori umum (Alam/Budaya/Rekreasi/Umum). Sub-kategori lebih granular (beach/temple/waterfall/dll) diinfer secara otomatis dari:
1. Detail kategori (jika ada dari parsing tanda hubung)
2. Regex pattern pada nama destinasi
3. Fallback berdasarkan kategori utama

### 3. Content text enrichment

Content text diperkaya dengan 5 jenis token tambahan untuk mengkompensasi ketiadaan `description`, `tags`, dan `activity` di raw data. Ini mengurangi pasangan destinasi yang dianggap identik oleh TF-IDF dari 5,968 menjadi 153 (-97.4%).

### 4. District fallback "Unknown"

Kolom `district` menggunakan fallback `"Unknown"` untuk memenuhi kontrak non-null, meskipun saat ini semua baris sudah memiliki kecamatan.

### 5. 7 destinasi not eligible

7 destinasi dari Tabanan tidak eligible karena koordinatnya di luar batas Bali (kemungkinan data error di Google Maps). Destinasi ini tetap disimpan di dataset dengan `recommendation_eligible = False`.

---

## Referensi

| Dokumen | Deskripsi |
|---|---|
| [DATASET_CONTRACT.md](../DATASET_CONTRACT.md) | Kontrak schema dan mapping rules |
| [DATA_QUALITY_RULES.md](../DATA_QUALITY_RULES.md) | Aturan validasi per kolom |
| [DATA_PIPELINE_GUIDE.md](../DATA_PIPELINE_GUIDE.md) | Alur pipeline data end-to-end |
| [constants.py](../../src/utils/constants.py) | Konstanta kategori dan sub-kategori resmi |
| [Notebook](../../notebooks/01_data_cleaning_imputation_preprocessing_eda_quality_validation.ipynb) | Notebook implementasi |
