# Panduan Budget Engine - BaliNavi

Dokumen ini menjelaskan sistem klasifikasi budget tier dan alokasi budget pada BaliNavi MVP.

## Ikhtisar

Budget engine BaliNavi terdiri dari dua komponen utama:

1. **Budget Tier Classification** (`src/services/budget_service.py`): menentukan apakah budget pengguna termasuk low, medium, atau high.
2. **Budget Allocation** (`src/services/allocation_service.py`): mengalokasikan total budget ke komponen pengeluaran.

## Budget Tier Classification

### Fungsi `classify_budget()`

Parameter:

| Parameter | Tipe | Deskripsi |
|---|---|---|
| `total_budget` | integer | Total budget perjalanan dalam IDR |
| `duration_days` | integer | Durasi perjalanan dalam hari |
| `num_people` | integer | Jumlah orang |

Return value: dictionary dengan key `tier`, `budget_per_person_per_day`, dan `total_budget`.

### Rumus

```text
budget_per_person_per_day = total_budget // (duration_days × num_people)
```

Catatan: menggunakan integer division (`//`) untuk menghindari desimal.

### Aturan Tier

| Tier | Aturan |
|---|---|
| `low` | budget_per_person_per_day di bawah 500.000 IDR |
| `medium` | budget_per_person_per_day antara 500.000 dan 1.000.000 IDR (inklusif) |
| `high` | budget_per_person_per_day di atas 1.000.000 IDR |

### Konstanta Batas

```python
LOW_BUDGET_LIMIT = 500_000      # batas atas tier low
MEDIUM_BUDGET_LIMIT = 1_000_000  # batas atas tier medium
```

### Validasi

- `total_budget` harus lebih besar dari 0.
- `duration_days` harus lebih besar dari 0.
- `num_people` harus lebih besar dari 0.
- Jika tidak valid, akan melempar `ValueError`.

### Contoh

| Total Budget | Durasi | Orang | Per Orang Per Hari | Tier |
|---|---|---|---|---|
| 2.000.000 | 3 | 2 | 333.333 | low |
| 5.000.000 | 3 | 2 | 833.333 | medium |
| 7.000.000 | 3 | 2 | 1.166.666 | high |

## Budget Allocation

### Fungsi `allocate_budget()`

Parameter:

| Parameter | Tipe | Deskripsi |
|---|---|---|
| `total_budget` | integer | Total budget yang akan dialokasikan |

Return value: dictionary dengan key `items`, `total_allocated`, dan `is_within_budget`.

### Aturan Alokasi Default

| Komponen | Persentase |
|---|---|
| `destination_tickets` | 25% |
| `local_transport` | 25% |
| `food` | 30% |
| `buffer` | 20% |
| **Total** | **100%** |

### Logika Alokasi

1. Hitung alokasi untuk setiap komponen kecuali yang terakhir: `amount = total_budget × percentage // 100`.
2. Komponen terakhir (`buffer`) mendapat sisa budget: `amount = total_budget - total sebelumnya`.
3. Ini memastikan total alokasi selalu sama persis dengan total budget, tanpa pembulatan yang menyebabkan selisih.

### Validasi

#### `validate_allocation_rules()`

Memastikan aturan alokasi valid:

- Semua persentase harus non-negatif.
- Total persentase harus berjumlah 100.
- Jika tidak valid, akan melempar `ValueError`.

#### `allocate_budget()`

- `total_budget` harus lebih besar dari 0.
- `total_allocated` tidak boleh melebihi `total_budget`.
- `is_within_budget` bernilai `True` jika `total_allocated <= total_budget`.

### Contoh Alokasi

Untuk total budget 5.000.000 IDR:

| Komponen | Persentase | Jumlah (IDR) |
|---|---|---|
| destination_tickets | 25% | 1.250.000 |
| local_transport | 25% | 1.250.000 |
| food | 30% | 1.500.000 |
| buffer | 20% | 1.000.000 |
| **Total** | **100%** | **5.000.000** |

Untuk total budget 5.000.001 IDR (kasus pembulatan):

| Komponen | Persentase | Jumlah (IDR) |
|---|---|---|
| destination_tickets | 25% | 1.250.000 |
| local_transport | 25% | 1.250.000 |
| food | 30% | 1.500.000 |
| buffer | 20% | 1.000.001 |
| **Total** | **100%** | **5.000.001** |

Buffer menyerap sisa pembulatan untuk menjamin `total_allocated == total_budget`.

## Integrasi dengan Backend

Kedua service dipanggil secara berurutan oleh route handler `POST /plan-trip`:

```text
POST /plan-trip
    → classify_budget(total_budget, duration_days, num_people)
    → allocate_budget(total_budget)
    → recommend_destinations(budget_tier, ...)
    → return PlanTripResponse
```

Budget tier dari `classify_budget()` digunakan oleh `recommend_destinations()` untuk memfilter destinasi yang sesuai.

## Format Response

### Budget Summary

```json
{
  "tier": "medium",
  "budget_per_person_per_day": 833333,
  "total_budget": 5000000
}
```

### Budget Allocation

```json
{
  "items": [
    {"component": "destination_tickets", "amount": 1250000, "percentage": 25},
    {"component": "local_transport", "amount": 1250000, "percentage": 25},
    {"component": "food", "amount": 1500000, "percentage": 30},
    {"component": "buffer", "amount": 1000000, "percentage": 20}
  ],
  "total_allocated": 5000000,
  "is_within_budget": true
}
```

## Test yang Tersedia

| Test | Yang Diuji |
|---|---|
| `test_budget_tier_low` | Tier low untuk budget rendah |
| `test_budget_tier_medium` | Tier medium untuk budget menengah |
| `test_budget_tier_high` | Tier high untuk budget tinggi |
| `test_budget_tier_returns_supported_values_only` | Tier selalu salah satu dari low, medium, high |
| `test_allocation_never_exceeds_budget` | Total alokasi tidak melebihi total budget |
| `test_allocation_uses_mvp_components` | Komponen alokasi sesuai MVP |
| `test_allocation_rule_percentages_must_sum_to_100` | Persentase harus berjumlah 100 |
| `test_allocation_rule_percentages_must_not_be_negative` | Persentase tidak boleh negatif |

## Referensi

- API Contract: [API_CONTRACT.md](API_CONTRACT.md)
- Arsitektur: [ARCHITECTURE.md](ARCHITECTURE.md)
- Panduan Recommender: [RECOMMENDER_GUIDE.md](RECOMMENDER_GUIDE.md)
- Panduan Testing: [TESTING_GUIDE.md](TESTING_GUIDE.md)
- Scope MVP: [MVP_SCOPE.md](MVP_SCOPE.md)
