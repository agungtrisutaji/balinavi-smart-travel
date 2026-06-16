# Git Workflow - BaliNavi

Dokumen ini menjelaskan strategi branching, konvensi penamaan, dan alur Git yang digunakan tim BaliNavi.

## Strategi Branching

BaliNavi menggunakan model branching tiga tingkat:

```text
main        branch stabil untuk demo dan rilis
develop     branch integrasi untuk menggabungkan fitur
feature/*   branch kerja untuk implementasi fitur
```

### Alur Branch

```text
main ← develop ← feature/*
```

1. `main` hanya menerima merge dari `develop` yang sudah stabil.
2. `develop` menerima merge dari feature branch yang sudah di-review.
3. `feature/*` dibuat dari `develop` untuk setiap task.

## Konvensi Penamaan Branch

Format:

```text
feature/<deskripsi-singkat>
```

Contoh branch yang direkomendasikan:

| Branch | Deskripsi |
|---|---|
| `feature/backend-api` | Implementasi FastAPI backend |
| `feature/frontend-streamlit` | Implementasi Streamlit frontend |
| `feature/data-preprocessing` | Pembersihan dan preprocessing dataset |
| `feature/recommender-model` | Implementasi model rekomendasi |
| `feature/budget-allocation` | Implementasi alokasi budget |
| `feature/docker-ci` | Setup Docker dan GitHub Actions |

Aturan penamaan:

- Gunakan huruf kecil.
- Gunakan tanda hubung (`-`) sebagai pemisah kata.
- Nama harus singkat dan deskriptif.
- Jangan gunakan spasi atau karakter khusus.

## Alur Kerja Git Harian

### 1. Mulai Task Baru

```bash
git checkout develop
git pull origin develop
git checkout -b feature/nama-fitur
```

### 2. Kerja dan Commit

```bash
git add <file-yang-berubah>
git commit -m "deskripsi singkat perubahan"
```

Aturan commit message:

- Gunakan bahasa yang jelas dan deskriptif.
- Jelaskan apa yang berubah, bukan bagaimana.
- Satu commit untuk satu perubahan logis.

Contoh commit message yang baik:

```text
tambah endpoint GET /metadata
implementasi klasifikasi budget tier
perbaiki validasi preferred_categories di schema
tambah test untuk allocation service
```

### 3. Push ke Remote

```bash
git push origin feature/nama-fitur
```

### 4. Buat Pull Request

- Buat Pull Request dari `feature/nama-fitur` ke `develop`.
- Gunakan template PR yang tersedia di `.github/pull_request_template.md`.
- Isi bagian Summary, Changes, Validation, dan Notes.
- Minta review dari anggota tim yang relevan.

### 5. Review dan Merge

- Pastikan CI GitHub Actions hijau.
- Pastikan reviewer menyetujui perubahan.
- Merge menggunakan strategi merge biasa (bukan squash) untuk menjaga riwayat.
- Hapus feature branch setelah merge.

### 6. Rilis ke Main

- Merge `develop` ke `main` hanya ketika fitur sudah stabil dan siap demo.
- Pastikan semua test lulus sebelum merge ke `main`.

## Template Pull Request

Template tersedia di `.github/pull_request_template.md`:

```markdown
## Summary
-

## Changes
-

## Validation
- [ ] Tests passed locally
- [ ] Docker Compose config validated
- [ ] No secrets, `.env`, or `.streamlit/secrets.toml` files committed

## Notes
-
```

## File yang Tidak Boleh Di-commit

Jangan commit file berikut (sudah diatur di `.gitignore`):

- `.env`.
- `.streamlit/secrets.toml` (gunakan `.streamlit/secrets.toml.example` sebagai referensi).
- Folder virtual environment (`.venv/`).
- Dataset besar tanpa persetujuan tim.
- Model artifact besar kecuali diperlukan untuk demo.
- Credentials, API keys, dan tokens.
- Log files.
- Folder `__pycache__/`.

## Penyelesaian Konflik

1. Pull perubahan terbaru dari `develop`:

```bash
git checkout develop
git pull origin develop
git checkout feature/nama-fitur
git merge develop
```

2. Selesaikan konflik secara manual.
3. Jalankan test untuk memastikan tidak ada yang rusak:

```bash
pytest tests/ -v
```

4. Commit hasil penyelesaian konflik.

## Referensi

- Alur kerja tim: [WORKFLOW.md](WORKFLOW.md)
- Peran tim: [TEAM_ROLES.md](TEAM_ROLES.md)
- Template PR: `../.github/pull_request_template.md`
