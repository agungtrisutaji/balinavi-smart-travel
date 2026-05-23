# Panduan Testing - BaliNavi

Dokumen ini menjelaskan strategi testing, cara menjalankan test, dan panduan menulis test baru untuk BaliNavi MVP.

## Ikhtisar Testing

BaliNavi menggunakan pytest sebagai framework testing utama dan HTTPX sebagai HTTP client untuk test API. Semua test berada di folder `tests/`.

## Menjalankan Test

### Menjalankan Semua Test

```bash
pytest tests/ -v
```

### Menjalankan Test Tertentu

```bash
pytest tests/test_api_contract.py -v
pytest tests/test_budget_rules.py -v
pytest tests/test_allocation.py -v
pytest tests/test_recommender_service.py -v
```

### Menjalankan Test dengan Nama Spesifik

```bash
pytest tests/ -v -k "test_health"
```

## Area Test yang Ada

MVP memiliki empat area test:

| File Test | Area yang Diuji | Service yang Diuji |
|---|---|---|
| `tests/test_api_contract.py` | API contract dan endpoint | `app/backend/api/routes.py` |
| `tests/test_budget_rules.py` | Klasifikasi budget tier | `src/services/budget_service.py` |
| `tests/test_allocation.py` | Alokasi budget | `src/services/allocation_service.py` |
| `tests/test_recommender_service.py` | Rekomendasi destinasi | `src/services/recommender_service.py` |

### Test API Contract (`test_api_contract.py`)

Test ini memastikan bahwa endpoint API berfungsi sesuai kontrak:

- `GET /health` mengembalikan status `ok`.
- `GET /metadata` mengembalikan opsi yang didukung.
- `POST /plan-trip` mengembalikan field yang terdokumentasi.
- Total alokasi tidak melebihi total budget.
- Remaining budget tidak negatif.

### Test Budget Rules (`test_budget_rules.py`)

Test ini memastikan klasifikasi budget tier benar:

- Budget rendah: di bawah 500.000 IDR per orang per hari.
- Budget menengah: 500.000 sampai 1.000.000 IDR per orang per hari.
- Budget tinggi: di atas 1.000.000 IDR per orang per hari.

### Test Allocation (`test_allocation.py`)

Test ini memastikan alokasi budget benar:

- Total alokasi tidak melebihi total budget.
- Komponen alokasi sesuai MVP (destination_tickets, local_transport, food, buffer).
- Persentase alokasi harus berjumlah 100.
- Persentase tidak boleh negatif.

### Test Recommender Service (`test_recommender_service.py`)

Test ini memastikan rekomendasi berfungsi:

- Rekomendasi mengembalikan list destinasi.
- Filter berdasarkan kategori dan lokasi berfungsi.
- Filter yang tidak cocok mengembalikan list kosong.
- Budget tier muncul di match reasons.

## Panduan Menulis Test Baru

### Konvensi Penamaan

- File test: `tests/test_<nama_area>.py`
- Fungsi test: `test_<apa_yang_diuji>()`
- Gunakan nama yang menjelaskan perilaku yang diuji.

Contoh nama yang baik:

```python
def test_allocation_never_exceeds_budget() -> None: ...
def test_budget_tier_low() -> None: ...
def test_recommender_returns_empty_list_when_filters_have_no_matches() -> None: ...
```

### Struktur Test

Gunakan pola Arrange-Act-Assert:

```python
def test_contoh() -> None:
    # Arrange: siapkan data input
    total_budget = 5_000_000

    # Act: panggil fungsi yang diuji
    result = allocate_budget(total_budget)

    # Assert: verifikasi hasil
    assert result["total_allocated"] <= total_budget
```

### Test API Endpoint

Gunakan `TestClient` dari FastAPI:

```python
from fastapi.testclient import TestClient
from app.backend.main import app

client = TestClient(app)

def test_contoh_endpoint() -> None:
    response = client.get("/health")
    assert response.status_code == 200
```

### Test Service Layer

Import langsung dari module service:

```python
from src.services.budget_service import classify_budget

def test_contoh_service() -> None:
    result = classify_budget(total_budget=5_000_000, duration_days=3, num_people=2)
    assert result["tier"] == "medium"
```

### Test Error Handling

Gunakan `pytest.raises` untuk menguji error:

```python
import pytest

def test_contoh_error() -> None:
    with pytest.raises(ValueError, match="must be greater than 0"):
        allocate_budget(0)
```

## CI Integration

Test dijalankan otomatis oleh GitHub Actions pada setiap push dan pull request melalui workflow `.github/workflows/ci-docker.yml`.

Langkah CI:

1. Checkout repository.
2. Setup Python 3.12.
3. Install dependencies.
4. Jalankan `pytest tests/ -v`.
5. Validasi Docker Compose config.
6. Build Docker image backend.
7. Build Docker image frontend.

## Checklist Sebelum Push

- [ ] Semua test yang ada tetap lulus.
- [ ] Test baru ditambahkan untuk logika baru.
- [ ] Tidak ada test yang di-skip tanpa alasan.
- [ ] Test dijalankan dari root project.

## Referensi

- API Contract: [API_CONTRACT.md](API_CONTRACT.md)
- Arsitektur: [ARCHITECTURE.md](ARCHITECTURE.md)
- Panduan pengembangan: [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md)
