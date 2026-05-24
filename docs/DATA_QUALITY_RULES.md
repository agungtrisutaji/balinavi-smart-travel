# Aturan Kualitas Data - BaliNavi

Dokumen ini mendefinisikan aturan validasi dan kualitas data yang diterapkan pada setiap tahap data pipeline BaliNavi MVP.

## Ikhtisar

Aturan kualitas data memastikan bahwa dataset destinasi Bali memenuhi standar minimum sebelum digunakan oleh model rekomendasi dan disajikan melalui API. Aturan ini adalah target validasi untuk implementasi pipeline dan diterapkan di dua tahap saat pipeline selesai:

1. **Preprocessing** (`src/preprocessing/preprocess.py`): validasi dan pembersihan per baris.
2. **Feature Engineering** (`src/features/build_features.py`): penentuan eligibility rekomendasi.

---

## Validasi Per Kolom

### `nama_destinasi` → `name`

| Aturan | Detail |
|---|---|
| Tidak boleh kosong | Baris dengan `nama_destinasi` kosong atau NaN harus di-drop |
| Trim whitespace | Hapus spasi di awal dan akhir |
| Tidak boleh hanya whitespace | `"   "` dianggap kosong |
| Minimal panjang | Minimal 2 karakter setelah trim |

### `kategori` → `category_main`, `detail_category`, `sub_category`

| Aturan | Detail |
|---|---|
| Default jika kosong | Jika `kategori` kosong atau NaN, set `category_main = "general"` dan `detail_category = null` |
| Baris tetap disimpan | Untuk MVP, baris dengan `kategori` kosong tetap disimpan kecuali field kritikal lain gagal, seperti `nama_destinasi` kosong |
| Parsing tanda hubung | Pisahkan berdasarkan karakter tanda hubung `-`, lalu trim whitespace pada setiap hasil split |
| Case-insensitive | `"alam"`, `"Alam"`, `"ALAM"` semuanya → `"nature"` |
| Mapping harus valid | `category_main` harus ada di `SUPPORTED_CATEGORIES` |
| Sub-kategori fallback | Jika `detail_category` tidak cocok, gunakan fallback berdasarkan `category_main` |

Parsing `kategori` harus menangani variasi whitespace secara ekuivalen. Contoh `Alam-Pantai`, `Alam - Pantai`, dan `Alam -Pantai` semuanya diperlakukan sebagai kategori utama `Alam` dan detail kategori `Pantai`.

Mapping lengkap didefinisikan di [DATASET_CONTRACT.md](DATASET_CONTRACT.md) bagian Mapping Kategori.

### `harga_destinasi` → `estimated_ticket_price`

| Aturan | Detail |
|---|---|
| Default ke 0 | Jika kosong, NaN, atau tidak bisa diparse, set ke `0` |
| String "Gratis" | Case-insensitive, konversi ke `0` |
| Hapus prefix mata uang | `"Rp"`, `"IDR"` dihapus |
| Hapus separator ribuan | Titik (`.`) dan koma (`,`) yang berfungsi sebagai separator dihapus |
| Harus non-negatif | Nilai negatif di-set ke `0` |
| Tipe akhir | integer |

Contoh konversi:

| Input | Output |
|---|---|
| `"Gratis"` | `0` |
| `""` atau NaN | `0` |
| `"0"` | `0` |
| `"50000"` | `50000` |
| `50000` | `50000` |
| `"Rp 50.000"` | `50000` |
| `"IDR 125,000"` | `125000` |
| `"-5000"` | `0` |

### `rating`

| Aturan | Detail |
|---|---|
| Default ke 0.0 | Jika kosong atau tidak bisa diparse, set ke `0.0` |
| Range valid | 0.0 sampai 5.0 |
| Clamp | Nilai di atas 5.0 di-clamp ke `5.0`, di bawah 0.0 ke `0.0` |
| Tipe akhir | float, satu desimal |

### `jumlah_ulasan` → `review_count`

| Aturan | Detail |
|---|---|
| Default ke 0 | Jika kosong atau tidak bisa diparse, set ke `0` |
| Harus non-negatif | Nilai negatif di-set ke `0` |
| Hapus separator ribuan | `"1.000"` → `1000` |
| Tipe akhir | integer |

### `kabupaten_kota` → `regency_city`

| Aturan | Detail |
|---|---|
| Tidak boleh kosong | Baris dengan `kabupaten_kota` kosong, NaN, atau hanya whitespace harus di-drop sebelum dataset processed dibuat |
| Trim whitespace | Hapus spasi di awal dan akhir |
| Normalisasi kapitalisasi | Title case: `"badung"` → `"Badung"` |

Kolom processed `regency_city` harus non-null karena digunakan untuk location filtering dan dikirim kembali pada API response. Untuk MVP, jangan menambahkan flag column baru untuk lokasi kosong; baris yang gagal aturan ini harus di-drop.

Kabupaten/kota yang diharapkan di Bali:

```text
Badung, Gianyar, Denpasar, Karangasem, Tabanan,
Bangli, Klungkung, Buleleng, Jembrana
```

### `kecamatan` → `district`

| Aturan | Detail |
|---|---|
| Default ke placeholder non-null | Jika kosong, hanya whitespace, atau NaN, set ke `"Unknown"` |
| Trim whitespace | Hapus spasi di awal dan akhir sebelum validasi/fallback |
| Normalisasi kapitalisasi | Title case untuk nilai valid; placeholder tetap `"Unknown"` |

Kolom processed `district` harus bertipe string non-null agar konsisten dengan kontrak dataset processed dan schema API `DestinationRecommendation`. Untuk MVP, nilai lokasi tingkat kecamatan yang tidak tersedia tidak menyebabkan baris di-drop; gunakan placeholder `"Unknown"` sebagai fallback non-null.

Dalam perhitungan `data_quality_score`, placeholder seperti `"Unknown"` harus diperlakukan sebagai nilai fallback, bukan sebagai bukti bahwa data kecamatan lengkap. Artinya, placeholder ini boleh menjaga kontrak non-null, tetapi tidak boleh otomatis menambah skor kelengkapan/kualitas untuk komponen `district`.

### `latitude` dan `longitude`

| Aturan | Detail |
|---|---|
| Default ke NaN | Jika kosong atau tidak bisa diparse |
| Range latitude | -9.5 sampai -8.0 (rentang Bali) |
| Range longitude | 114.4 sampai 115.8 (rentang Bali) |
| Di luar range | Set ke NaN, `has_coordinates = False`, dan pada tahap feature engineering set `recommendation_eligible = False` |

### `maps_url` dan `image_url`

| Aturan | Detail |
|---|---|
| Default ke None | Jika kosong atau NaN |
| Validasi format | Harus dimulai dengan `http://` atau `https://` jika ada |
| URL tidak valid | Set ke None |

---

## Deteksi dan Penghapusan Duplikat

### Aturan Duplikat

Dua baris dianggap duplikat jika:

```text
nama_destinasi (lowercase, trimmed) + kabupaten_kota (lowercase, trimmed)
```

bernilai sama.

### Penanganan Duplikat

1. Urutkan duplikat berdasarkan kelengkapan data (baris dengan lebih banyak field terisi dipertahankan).
2. Pertahankan baris pertama setelah pengurutan.
3. Drop baris duplikat lainnya.
4. Catat jumlah duplikat yang dihapus dalam log.

---

## Skor Kualitas Data (`data_quality_score`)

Skor kualitas dihitung per baris berdasarkan kelengkapan field:

| Field | Bobot |
|---|---|
| `name` tidak kosong | 0.20 |
| `category_main` bukan `"general"` | 0.15 |
| `sub_category` bukan fallback | 0.10 |
| `description` tidak kosong | 0.10 |
| `tags` tidak kosong | 0.05 |
| `activity` tidak kosong | 0.05 |
| `regency_city` tidak kosong | 0.10 |
| `district` terisi dan bukan placeholder (`"Unknown"`/`"-"`) | 0.05 |
| `rating > 0.0` | 0.05 |
| `review_count > 0` | 0.05 |
| `has_coordinates == True` | 0.05 |
| `has_price_info == True` | 0.05 |
| **Total** | **1.00** |

### Definisi `has_price_info`

`has_price_info` adalah sinyal validasi turunan (derived), bukan kolom yang harus dipersistensi di dataset. Nilainya ditentukan saat preprocessing berdasarkan apakah informasi harga mentah benar-benar tersedia dan bisa diparse:

| Kondisi raw `harga_destinasi` | `has_price_info` | Penjelasan |
|---|---|---|
| Angka valid (`50000`, `"50000"`, `"Rp 50.000"`) | `True` | Harga mentah ada dan berhasil diparse |
| `"Gratis"`, `"gratis"`, `"free"` | `True` | Informasi harga eksplisit: gratis |
| `"0"` atau `0` (eksplisit di raw) | `True` | Harga eksplisit nol |
| Kosong, NaN, None | `False` | Tidak ada informasi harga, default 0 digunakan sebagai fallback |
| String tidak bisa diparse | `False` | Parsing gagal, default 0 digunakan sebagai fallback |

`has_price_info` digunakan hanya untuk perhitungan `data_quality_score`. Kolom `estimated_ticket_price` tetap di-set ke 0 sebagai fallback ketika `has_price_info == False`, sesuai aturan Mapping Harga di [DATASET_CONTRACT.md](DATASET_CONTRACT.md).

Rumus:

```text
data_quality_score = jumlah bobot dari field yang terpenuhi
```

Contoh:

- Baris dengan semua field terisi lengkap dan harga tersedia: `data_quality_score = 1.0`
- Baris hanya dengan nama dan kabupaten (tanpa harga, tanpa deskripsi, dll): `data_quality_score = 0.30`
- Baris lengkap tapi harga tidak tersedia (fallback 0): `data_quality_score = 0.95`

---

## Aturan Recommendation Eligibility

Destinasi dianggap layak untuk direkomendasikan (`recommendation_eligible = True`) jika memenuhi **semua** kondisi:

| # | Kondisi | Alasan |
|---|---|---|
| 1 | `name` tidak kosong | Destinasi tanpa nama tidak bisa ditampilkan |
| 2 | `category_main` ada di `SUPPORTED_CATEGORIES` | Harus bisa difilter oleh pengguna |
| 3 | `sub_category` ada di `SUPPORTED_SUB_CATEGORIES` | Harus bisa difilter oleh pengguna |
| 4 | `regency_city` tidak kosong | Harus bisa difilter berdasarkan lokasi |
| 5 | `data_quality_score >= 0.4` | Data terlalu minim tidak layak direkomendasikan |
| 6 | `latitude` dan `longitude` valid, non-null, dan dalam batas Bali | Field API rekomendasi membutuhkan koordinat non-null |

Destinasi yang `recommendation_eligible = False`:

- Tidak dimasukkan ke model training.
- Tidak akan muncul dalam rekomendasi API.
- Tetap disimpan di dataset final untuk keperluan analisis.

---

## Ringkasan Validasi Per Tahap

### Tahap Preprocessing

| Validasi | Aksi |
|---|---|
| `nama_destinasi` kosong | Drop baris |
| `kabupaten_kota` kosong, NaN, atau hanya whitespace | Drop baris |
| Duplikat | Drop baris duplikat, pertahankan yang paling lengkap |
| `harga_destinasi` tidak bisa diparse | Set `estimated_ticket_price = 0` |
| `rating` di luar range | Clamp ke 0.0 - 5.0 |
| `jumlah_ulasan` negatif | Set ke 0 |
| Koordinat kosong, NaN, atau di luar range Bali | Set ke NaN dan `has_coordinates = False` |
| URL tidak valid | Set ke None |

### Tahap Feature Engineering

| Validasi | Aksi |
|---|---|
| `content_text` kosong setelah konstruksi | Set `recommendation_eligible = False` |
| `data_quality_score < 0.4` | Set `recommendation_eligible = False` |
| `category_main` tidak di `SUPPORTED_CATEGORIES` | Set `recommendation_eligible = False` |
| `sub_category` tidak di `SUPPORTED_SUB_CATEGORIES` | Set `recommendation_eligible = False` |
| `latitude` atau `longitude` kosong, NaN, atau di luar range Bali | Set `recommendation_eligible = False` |

---

## Statistik Kualitas yang Harus Dilaporkan

Setelah preprocessing selesai, log harus mencatat:

| Metrik | Deskripsi |
|---|---|
| `total_raw_rows` | Jumlah baris di raw dataset |
| `dropped_empty_name` | Baris yang di-drop karena nama kosong |
| `dropped_empty_location` | Baris yang di-drop karena lokasi kosong |
| `dropped_duplicates` | Baris duplikat yang dihapus |
| `total_processed_rows` | Jumlah baris di processed dataset |
| `total_eligible` | Jumlah destinasi `recommendation_eligible = True` |
| `total_not_eligible` | Jumlah destinasi `recommendation_eligible = False` |
| `avg_quality_score` | Rata-rata `data_quality_score` |
| `price_free_count` | Jumlah destinasi gratis |
| `price_paid_count` | Jumlah destinasi berbayar |
| `category_distribution` | Distribusi per `category_main` |

---

## Referensi

- Kontrak dataset: [DATASET_CONTRACT.md](DATASET_CONTRACT.md)
- Data pipeline: [DATA_PIPELINE_GUIDE.md](DATA_PIPELINE_GUIDE.md)
- Recommender: [RECOMMENDER_GUIDE.md](RECOMMENDER_GUIDE.md)
- API Contract: [API_CONTRACT.md](API_CONTRACT.md)
- Scope MVP: [MVP_SCOPE.md](MVP_SCOPE.md)
