# Panduan Docker - BaliNavi

Dokumen ini menjelaskan setup Docker, cara menjalankan container, dan troubleshooting untuk BaliNavi MVP.

## Arsitektur Docker

BaliNavi menggunakan dua container Docker:

```text
┌─────────────────┐     ┌─────────────────┐
│    Frontend     │────▶│    Backend      │
│   (Streamlit)   │     │   (FastAPI)     │
│   Port: 8501    │     │   Port: 8000    │
└─────────────────┘     └─────────────────┘
```

- Container frontend menjalankan Streamlit di port 8501.
- Container backend menjalankan FastAPI di port 8000.
- Frontend berkomunikasi dengan backend melalui URL internal `http://backend:8000`.

## File Docker

| File | Kegunaan |
|---|---|
| `docker/backend.Dockerfile` | Dockerfile untuk backend FastAPI |
| `docker/frontend.Dockerfile` | Dockerfile untuk frontend Streamlit |
| `docker-compose.yml` | Orkestrasi kedua container |
| `.dockerignore` | File dan folder yang diabaikan saat build |

### Backend Dockerfile

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend Dockerfile

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app/frontend/streamlit_app.py", "--server.address", "0.0.0.0", "--server.port", "8501"]
```

### Docker Compose

```yaml
services:
  backend:
    build:
      context: .
      dockerfile: docker/backend.Dockerfile
    ports:
      - "8000:8000"

  frontend:
    build:
      context: .
      dockerfile: docker/frontend.Dockerfile
    environment:
      BACKEND_URL: http://backend:8000
    ports:
      - "8501:8501"
    depends_on:
      - backend
```

## Menjalankan Docker

### Build dan Jalankan Semua Service

```bash
docker compose up --build
```

### Jalankan di Background

```bash
docker compose up --build -d
```

### Hentikan Semua Service

```bash
docker compose down
```

### Lihat Log

```bash
docker compose logs
docker compose logs backend
docker compose logs frontend
```

### Rebuild Satu Service

```bash
docker compose build backend
docker compose build frontend
```

## Akses Setelah Menjalankan

```text
Backend API   : http://localhost:8000
API Docs      : http://localhost:8000/docs
Health Check  : http://localhost:8000/health
Streamlit App : http://localhost:8501
```

## Validasi Docker Compose Config

Gunakan perintah berikut untuk memvalidasi konfigurasi tanpa menjalankan container:

```bash
docker compose config
```

Perintah ini juga dijalankan oleh CI GitHub Actions.

## Build Image Secara Terpisah

Jika perlu build image secara manual tanpa Docker Compose:

### Backend

```bash
docker build -f docker/backend.Dockerfile -t balinavi-backend .
```

### Frontend

```bash
docker build -f docker/frontend.Dockerfile -t balinavi-frontend .
```

## CI Integration

GitHub Actions workflow (`.github/workflows/ci-docker.yml`) secara otomatis:

1. Memvalidasi `docker compose config`.
2. Mem-build image `balinavi-backend`.
3. Mem-build image `balinavi-frontend`.

Ini memastikan bahwa Dockerfile dan Docker Compose selalu valid.

## Troubleshooting

### Port sudah digunakan

Jika port 8000 atau 8501 sudah digunakan:

```bash
# Periksa proses yang menggunakan port
# Windows:
netstat -ano | findstr :8000
netstat -ano | findstr :8501
```

Hentikan proses yang menggunakan port tersebut, atau ubah port mapping di `docker-compose.yml`.

### Container gagal start

```bash
# Lihat log untuk detail error
docker compose logs backend
docker compose logs frontend
```

### Frontend tidak bisa terhubung ke backend

- Pastikan backend container berjalan.
- Periksa bahwa variabel `BACKEND_URL` di `docker-compose.yml` menggunakan `http://backend:8000`.
- Jangan gunakan `localhost` untuk komunikasi antar container Docker.

### Image build lambat

- Pastikan `.dockerignore` mengecualikan file yang tidak diperlukan.
- Gunakan `--no-cache-dir` saat install pip (sudah diatur di Dockerfile).

## Referensi

- Panduan pengembangan: [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md)
- Arsitektur: [ARCHITECTURE.md](ARCHITECTURE.md)
