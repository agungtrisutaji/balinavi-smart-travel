# Peran dan Tanggung Jawab Tim - BaliNavi

Dokumen ini mendefinisikan pembagian peran dan area tanggung jawab setiap anggota tim dalam pengembangan BaliNavi MVP.

## Peta Tanggung Jawab

| Area | Cakupan | Folder Utama |
|---|---|---|
| Backend dan Integrasi | FastAPI, API contract, service layer, Docker, CI | `app/backend/`, `docker/`, `.github/` |
| Frontend | Streamlit UI, form input, halaman hasil, visualisasi | `app/frontend/` |
| Data Engineering | Pengumpulan dataset, pembersihan, preprocessing, EDA | `src/data/`, `src/preprocessing/`, `data/`, `notebooks/` |
| AI Systems dan Budget Logic | Feature engineering, aturan budget tier, allocation engine | `src/features/`, `src/services/budget_service.py`, `src/services/allocation_service.py` |
| Recommender Model | Content-based filtering, tuning, evaluasi | `src/models/`, `src/services/recommender_service.py` |

## Detail per Area

### Backend dan Integrasi

Tanggung jawab:

- Membangun dan memelihara FastAPI backend.
- Menjaga stabilitas API contract sesuai [API_CONTRACT.md](API_CONTRACT.md).
- Mengelola route handler di `app/backend/api/routes.py`.
- Mengelola request dan response schema di `app/backend/schemas/trip_schema.py`.
- Mengelola konfigurasi aplikasi di `app/backend/core/config.py`.
- Mengintegrasikan service layer ke route handler.
- Memelihara Dockerfile dan Docker Compose.
- Memelihara GitHub Actions CI workflow.

File yang dikelola:

```text
app/backend/main.py
app/backend/api/routes.py
app/backend/schemas/trip_schema.py
app/backend/core/config.py
docker/backend.Dockerfile
docker/frontend.Dockerfile
docker-compose.yml
.github/workflows/ci-docker.yml
```

### Frontend

Tanggung jawab:

- Membangun dan memelihara Streamlit frontend.
- Menampilkan form input sesuai metadata dari backend.
- Memanggil API backend untuk menghasilkan rekomendasi.
- Menampilkan hasil rekomendasi dan visualisasi alokasi budget.
- Tidak menduplikasi business logic yang ada di backend.

File yang dikelola:

```text
app/frontend/streamlit_app.py
```

### Data Engineering

Tanggung jawab:

- Mengumpulkan dan mengelola dataset destinasi Bali.
- Membersihkan data mentah dan menangani duplikat.
- Menyiapkan dataset yang sudah diproses untuk model.
- Melakukan EDA (Exploratory Data Analysis) di notebook.
- Menjaga konvensi folder data (`raw/`, `processed/`, `final/`).

File yang dikelola:

```text
src/data/load_data.py
src/preprocessing/preprocess.py
data/raw/
data/processed/
data/final/
notebooks/
```

### AI Systems dan Budget Logic

Tanggung jawab:

- Membangun feature engineering untuk dataset destinasi.
- Mengimplementasikan aturan klasifikasi budget tier.
- Mengimplementasikan rule-based budget allocation.
- Memastikan total alokasi tidak melebihi total budget.
- Menjaga aturan budget tetap eksplainable dan terkontrol.

File yang dikelola:

```text
src/features/build_features.py
src/services/budget_service.py
src/services/allocation_service.py
src/utils/constants.py
```

### Recommender Model

Tanggung jawab:

- Mengimplementasikan content-based recommendation menggunakan Scikit-learn.
- Membangun pipeline TF-IDF dan cosine similarity.
- Menyimpan model dan vectorizer artifact.
- Mengevaluasi output rekomendasi.
- Memastikan dummy recommender dapat diganti dengan model nyata.

File yang dikelola:

```text
src/models/train_recommender.py
src/models/recommender.py
src/models/evaluate_recommender.py
src/services/recommender_service.py
artifacts/
```

## Aturan Lintas Area

1. Jika perubahan memengaruhi API contract, koordinasikan dengan area Backend dan Frontend.
2. Jika perubahan memengaruhi service layer, koordinasikan dengan area yang memanggil service tersebut.
3. Setiap area bertanggung jawab menulis test untuk logika yang ditambahkan.
4. Jangan mengubah file di luar area tanggung jawab tanpa koordinasi.
5. Catat keputusan teknis lintas area di [DECISION_LOG.md](DECISION_LOG.md).

## Referensi

- Arsitektur sistem: [ARCHITECTURE.md](ARCHITECTURE.md)
- Scope MVP: [MVP_SCOPE.md](MVP_SCOPE.md)
- Kontrak API: [API_CONTRACT.md](API_CONTRACT.md)
- Alur kerja: [WORKFLOW.md](WORKFLOW.md)
