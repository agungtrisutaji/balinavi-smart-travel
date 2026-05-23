# Kontrak Dataset - BaliNavi

Dokumen ini mendefinisikan skema dataset di setiap tahap data pipeline BaliNavi MVP: raw, processed, dan final. Dokumen ini berfungsi sebagai kontrak antara area Data Engineering, AI Systems, dan Recommender Model.

## Ikhtisar Tahapan Dataset

```text
data/raw/bali_tourist_destination_with_harga_full_1452.csv  ← current raw source file
        │
        ▼  src/preprocessing/preprocess.py (target implementasi)
data/processed/bali_destinations.csv    ← target dataset yang sudah dibersihkan
        │
        ▼  src/features/build_features.py
data/final/bali_destinations.csv        ← dataset model-ready
        │
        ▼  src/models/train_recommender.py
artifacts/                              ← model dan vectorizer artifact
```

File sample tersedia di `data/sample/bali_destinations_sample.csv` untuk referensi dan pengujian manual.

---

## Skema Raw Dataset

File saat ini: `data/raw/bali_tourist_destination_with_harga_full_1452.csv`

Nama `data/raw/bali_destinations.csv` hanya boleh digunakan sebagai target canonical filename di masa depan jika dataset raw sudah distandardisasi atau di-rename. Nama tersebut bukan file raw source saat ini.

Dataset mentah berasal dari sumber data destinasi Bali. Kolom menggunakan bahasa campuran sesuai sumber asli.

### Kolom Raw Dataset

| Kolom | Tipe Data | Wajib | Deskripsi |
|---|---|---|---|
| `nama_destinasi` | string | ya | Nama destinasi wisata |
| `kategori` | string | ya | Kategori gabungan, contoh: `"Alam - Pantai"`, `"Budaya - Pura"` |
| `deskripsi` | string | tidak | Deskripsi singkat destinasi |
| `tags` | string | tidak | Tags dipisahkan koma, contoh: `"pantai,surfing,sunset"` |
| `aktivitas` | string | tidak | Aktivitas yang bisa dilakukan, contoh: `"berenang,snorkeling"` |
| `kabupaten_kota` | string | ya | Nama kabupaten atau kota, contoh: `"Badung"`, `"Gianyar"` |
| `kecamatan` | string | tidak | Nama kecamatan |
| `harga_destinasi` | string atau integer | tidak | Harga tiket dalam IDR, bisa berisi: angka, `"Gratis"`, `"gratis"`, kosong, atau `0` |
| `rating` | float atau string | tidak | Rating destinasi, range 0.0 sampai 5.0 |
| `jumlah_ulasan` | integer atau string | tidak | Jumlah ulasan atau review |
| `latitude` | float | tidak | Koordinat lintang |
| `longitude` | float | tidak | Koordinat bujur |
| `maps_url` | string | tidak | URL Google Maps |
| `image_url` | string | tidak | URL gambar destinasi |

### Catatan Raw Dataset

- Kolom `kategori` berisi kategori dan sub-kategori dalam satu field, dipisahkan tanda hubung (`-`). Contoh: `"Alam - Pantai"`, `"Budaya - Pura"`, `"Rekreasi - Waterpark"`.
- Kolom `harga_destinasi` tidak konsisten: bisa angka murni, string `"Gratis"`, string angka `"50000"`, atau kosong (NaN).
- Kolom `rating` bisa berisi float atau string yang perlu dikonversi.
- Kolom `jumlah_ulasan` bisa berisi integer atau string yang perlu dikonversi.
- Baris bisa memiliki duplikat berdasarkan `nama_destinasi` + `kabupaten_kota`.

---

## Skema Processed Dataset

File: `data/processed/bali_destinations.csv`

Skema ini adalah target kontrak untuk dataset yang sudah dibersihkan dan dinormalisasi oleh implementasi preprocessing di masa depan. Implementasi `src/preprocessing/preprocess.py` saat ini masih skeleton/planned dan belum melakukan seluruh proses cleaning yang dijelaskan di dokumen ini.

### Kolom Processed Dataset

| Kolom | Tipe Data | Nullable | Deskripsi |
|---|---|---|---|
| `destination_id` | string | tidak | ID unik, format `"DEST-001"`, `"DEST-002"`, dst |
| `name` | string | tidak | Nama destinasi, sudah di-trim |
| `category_raw` | string | tidak | Kategori asli dari raw dataset, sudah di-trim |
| `category_main` | string | tidak | Kategori utama hasil mapping (lihat Mapping Kategori) |
| `detail_category` | string | ya | Detail kategori hasil parsing dari `kategori`, `null` jika tidak ada |
| `sub_category` | string | tidak | Sub-kategori hasil mapping (lihat Mapping Sub-Kategori) |
| `description` | string | ya | Deskripsi destinasi, `null` jika tidak ada |
| `tags` | string | ya | Tags, `null` jika tidak ada |
| `activity` | string | ya | Aktivitas, `null` jika tidak ada |
| `regency_city` | string | tidak | Kabupaten atau kota |
| `district` | string | tidak | Kecamatan; jika tidak tersedia pada data sumber, wajib diisi fallback non-null seperti `"Unknown"` atau `"-"` saat preprocessing |
| `estimated_ticket_price` | integer | tidak | Harga tiket per orang dalam IDR (lihat Mapping Harga) |
| `is_free` | boolean | tidak | `True` jika harga 0 atau `"Gratis"` |
| `price_level` | string | tidak | Level harga: `"free"`, `"low"`, `"medium"`, `"high"` |
| `rating` | float | tidak | Rating, default 0.0 jika tidak ada |
| `review_count` | integer | tidak | Jumlah ulasan, default 0 jika tidak ada |
| `latitude` | float | ya | Koordinat lintang |
| `longitude` | float | ya | Koordinat bujur |
| `maps_url` | string | ya | URL Google Maps |
| `image_url` | string | ya | URL gambar destinasi |
| `has_coordinates` | boolean | tidak | `True` jika latitude dan longitude valid dalam batas koordinat Bali |
| `has_description` | boolean | tidak | `True` jika deskripsi tersedia dan tidak blank |
| `data_quality_score` | float | tidak | Skor kualitas data 0.0 - 1.0 (lihat Data Quality Rules) |

Untuk representasi CSV, cell kosong pada kolom nullable dapat terbaca sebagai NaN saat loading. Setelah normalisasi, kolom teks opsional seperti `description`, `tags`, `activity`, dan `district` direpresentasikan sebagai `null` jika nilainya tidak tersedia.

### Mapping Kategori (`kategori` → `category_main`)

Kolom `kategori` dari raw dataset dipisah berdasarkan karakter tanda hubung (`-`) menjadi dua bagian, lalu whitespace di sekitar setiap hasil split di-trim. Bagian pertama di-mapping ke `category_main`:

| Bagian Pertama (raw) | `category_main` |
|---|---|
| `Alam` | `nature` |
| `Budaya` | `culture` |
| `Rekreasi` | `recreation` |
| (lainnya atau kosong) | `general` |

Mapping bersifat case-insensitive dan di-trim. Variasi seperti `Alam-Pantai`, `Alam - Pantai`, dan `Alam -Pantai` harus diperlakukan ekuivalen.

### Mapping Detail Kategori (`kategori` → `detail_category`)

Bagian kedua dari kolom `kategori` (setelah tanda hubung) disimpan sebagai `detail_category`:

| Contoh `kategori` | `category_main` | `detail_category` |
|---|---|---|
| `Alam - Pantai` | `nature` | `Pantai` |
| `Budaya - Pura` | `culture` | `Pura` |
| `Rekreasi - Waterpark` | `recreation` | `Waterpark` |
| `Alam` | `nature` | `null` |

### Mapping Sub-Kategori (`detail_category` → `sub_category`)

`detail_category` di-mapping ke `sub_category` yang didukung oleh sistem:

| `detail_category` (case-insensitive) | `sub_category` |
|---|---|
| `Pantai` | `beach` |
| `Pura`, `Candi` | `temple` |
| `Air Terjun` | `waterfall` |
| `Hutan` | `forest` |
| `Gunung`, `Bukit` | `mountain` |
| `Museum` | `museum` |
| `Desa`, `Desa Wisata` | `village` |
| `Waterpark`, `Taman Air` | `waterpark` |
| `Landmark`, `Monumen`, `Tugu` | `landmark` |
| `Belanja`, `Pasar`, `Mall` | `shopping` |
| (lainnya atau kosong) | menggunakan logika fallback berdasarkan `category_main` |

Fallback `sub_category` jika `detail_category` tidak cocok:

| `category_main` | Fallback `sub_category` |
|---|---|
| `nature` | `forest` |
| `culture` | `temple` |
| `recreation` | `landmark` |
| `general` | `landmark` |

Daftar `sub_category` yang didukung harus konsisten dengan `src/utils/constants.py`:

```python
SUPPORTED_SUB_CATEGORIES = [
    "beach", "temple", "waterfall", "forest", "mountain",
    "museum", "village", "waterpark", "landmark", "shopping",
]
```

### Mapping Harga (`harga_destinasi` → `estimated_ticket_price`, `is_free`, `price_level`)

`estimated_ticket_price` adalah estimasi harga tiket per orang dalam IDR.

#### Langkah 1: Konversi ke `estimated_ticket_price`

| Nilai `harga_destinasi` | `estimated_ticket_price` |
|---|---|
| `"Gratis"`, `"gratis"`, `"GRATIS"`, `"free"` | `0` |
| `""`, NaN, None | `0` |
| `"0"` atau `0` | `0` |
| String angka `"50000"` | `50000` |
| Integer `50000` | `50000` |
| String dengan format `"Rp 50.000"` | `50000` (hapus prefix dan titik) |

#### Langkah 2: Tentukan `is_free`

```text
is_free = True  jika estimated_ticket_price == 0
is_free = False jika estimated_ticket_price > 0
```

#### Langkah 3: Tentukan `price_level`

| Kondisi | `price_level` |
|---|---|
| `estimated_ticket_price == 0` | `"free"` |
| `estimated_ticket_price > 0` dan `<= 25_000` | `"low"` |
| `estimated_ticket_price > 25_000` dan `<= 75_000` | `"medium"` |
| `estimated_ticket_price > 75_000` | `"high"` |

---

## Skema Final Dataset

File: `data/final/bali_destinations.csv`

Dataset model-ready yang dihasilkan oleh `src/features/build_features.py`. Berisi semua kolom dari processed dataset ditambah kolom feature engineering.

### Kolom Tambahan di Final Dataset

| Kolom | Tipe Data | Nullable | Deskripsi |
|---|---|---|---|
| `content_text` | string | tidak | Gabungan teks untuk TF-IDF (lihat Konstruksi content_text) |
| `popularity_score` | float | tidak | Skor popularitas 0.0 - 1.0 |
| `budget_tiers` | string | tidak | Budget tier yang cocok, dipisahkan koma: `"low,medium,high"` |
| `recommendation_eligible` | boolean | tidak | Apakah destinasi layak direkomendasikan (lihat Aturan Eligibility) |

`estimated_ticket_total` bukan field persisted pada final dataset secara default. Field ini adalah field runtime API untuk konteks request tertentu dan dihitung dari `estimated_ticket_price * num_people`. Field tersebut hanya boleh dihasilkan ke dataset/file turunan jika ada kebutuhan eksplisit untuk konteks request tertentu.

### Konstruksi `content_text`

`content_text` dibangun dari gabungan beberapa field dengan format:

```text
{name} {category_main} {sub_category} {detail_category} {tags} {activity} {description} {regency_city} {district}
```

Aturan:

1. Semua field dikonversi ke lowercase.
2. Field yang kosong atau NaN dilewati (tidak menambahkan string kosong).
3. Spasi berlebihan dihilangkan (trim dan collapse multiple spaces).
4. Tidak ada karakter khusus yang dihapus — biarkan TF-IDF menangani tokenisasi.

Contoh:

```text
Input:
  name = "Pantai Kuta"
  category_main = "nature"
  sub_category = "beach"
  detail_category = "Pantai"
  tags = "pantai,surfing,sunset"
  activity = "berenang,berjemur"
  description = "Pantai populer di Bali selatan"
  regency_city = "Badung"
  district = "Kuta"

Output:
  "pantai kuta nature beach pantai pantai,surfing,sunset berenang,berjemur pantai populer di bali selatan badung kuta"
```

### Perhitungan `popularity_score`

```text
popularity_score = normalize(rating × log1p(review_count))
```

Normalisasi menggunakan min-max scaling ke rentang 0.0 - 1.0.

Jika `review_count == 0` atau `rating == 0.0`, `popularity_score = 0.0`.

### Aturan `budget_tiers`

Setiap destinasi ditetapkan ke satu atau lebih budget tier berdasarkan `estimated_ticket_price`:

| Kondisi | Budget Tier |
|---|---|
| `estimated_ticket_price == 0` (gratis) | `"low,medium,high"` |
| `estimated_ticket_price > 0` dan `<= 50_000` | `"low,medium,high"` |
| `estimated_ticket_price > 50_000` dan `<= 100_000` | `"medium,high"` |
| `estimated_ticket_price > 100_000` | `"high"` |

### Aturan `recommendation_eligible`

Destinasi dianggap layak untuk direkomendasikan (`recommendation_eligible = True`) jika memenuhi **semua** kondisi berikut:

1. `name` tidak kosong.
2. `category_main` ada dalam `SUPPORTED_CATEGORIES`.
3. `sub_category` ada dalam `SUPPORTED_SUB_CATEGORIES`.
4. `regency_city` tidak kosong.
5. `data_quality_score >= 0.4`.
6. `latitude` dan `longitude` adalah float non-null dalam batas koordinat Bali:
   - `latitude`: -9.5 sampai -8.0
   - `longitude`: 114.4 sampai 115.8

Jika koordinat kosong, NaN, tidak bisa diparse, atau berada di luar batas Bali, set `recommendation_eligible = False`. Jika salah satu kondisi eligibility tidak terpenuhi, `recommendation_eligible = False`. Destinasi dengan `recommendation_eligible = False` tidak akan dimasukkan ke model training dan tidak akan direkomendasikan.

Hanya record dengan `recommendation_eligible = True` yang dipetakan langsung ke field API `DestinationRecommendation` yang membutuhkan `latitude` dan `longitude` non-null.

---

## Mapping ke API Response

Kolom pada final dataset dipetakan ke field pada `DestinationRecommendation` schema di API response:

| Kolom Final Dataset | Field API Response | Catatan |
|---|---|---|
| `destination_id` | `destination_id` | Langsung |
| `name` | `name` | Langsung |
| `category_main` | `category` | Rename kolom |
| `sub_category` | `sub_category` | Langsung |
| `district` | `district` | Langsung |
| `regency_city` | `regency_city` | Langsung |
| `estimated_ticket_price` | `estimated_ticket_price` | Langsung; harga tiket per orang |
| (dihitung saat runtime) | `estimated_ticket_total` | `estimated_ticket_price * num_people` untuk request saat ini |
| `rating` | `rating` | Langsung |
| `review_count` | `review_count` | Langsung |
| `popularity_score` | `popularity_score` | Langsung |
| `latitude` | `latitude` | Langsung hanya untuk record eligible dengan koordinat valid non-null |
| `longitude` | `longitude` | Langsung hanya untuk record eligible dengan koordinat valid non-null |
| `maps_url` | `maps_url` | Langsung, nullable |
| `image_url` | `image_url` | Langsung, nullable |
| (dihitung saat runtime) | `score` | Cosine similarity score |
| (dihitung saat runtime) | `match_reasons` | Alasan kecocokan |

API response harus mengembalikan `estimated_ticket_total` sebagai total biaya tiket untuk group pada request saat ini, bukan harga per orang. Frontend harus menampilkan dan memperlakukan field ini sebagai total untuk group terpilih.

---

## File Sample

File `data/sample/bali_destinations_sample.csv` berisi 10 baris contoh dataset raw yang memenuhi kontrak ini. File ini digunakan untuk:

- Referensi format kolom.
- Pengujian manual data pipeline.
- Validasi aturan preprocessing.
- Tidak digunakan oleh runtime service.

---

## Aturan Perubahan Kontrak

1. Jangan menambahkan atau menghapus kolom tanpa memperbarui dokumen ini.
2. Jangan mengubah tipe data kolom tanpa memperbarui dokumen ini dan kode preprocessing.
3. Jika aturan mapping berubah, perbarui dokumen ini, [DATA_QUALITY_RULES.md](DATA_QUALITY_RULES.md), dan kode terkait.
4. Perubahan yang memengaruhi API response harus juga memperbarui [API_CONTRACT.md](API_CONTRACT.md).
5. `category_main` dan `sub_category` harus selalu konsisten dengan `src/utils/constants.py`.

## Referensi

- Aturan kualitas data: [DATA_QUALITY_RULES.md](DATA_QUALITY_RULES.md)
- Data pipeline: [DATA_PIPELINE_GUIDE.md](DATA_PIPELINE_GUIDE.md)
- API Contract: [API_CONTRACT.md](API_CONTRACT.md)
- Arsitektur: [ARCHITECTURE.md](ARCHITECTURE.md)
- Recommender: [RECOMMENDER_GUIDE.md](RECOMMENDER_GUIDE.md)
- Scope MVP: [MVP_SCOPE.md](MVP_SCOPE.md)
