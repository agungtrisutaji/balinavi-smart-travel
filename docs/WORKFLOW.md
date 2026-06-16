# Workflow Tim - BaliNavi

Dokumen ini menjelaskan alur kerja tim dalam pengembangan BaliNavi MVP.

## Ikhtisar Alur Kerja

Tim BaliNavi mengikuti alur kerja iteratif yang berfokus pada MVP. Setiap anggota tim bekerja pada area tanggung jawab masing-masing dan berkoordinasi melalui branch strategy yang telah disepakati.

## Siklus Pengembangan

```text
1. Ambil task dari backlog
2. Buat feature branch dari develop
3. Implementasi sesuai scope task
4. Tulis atau perbarui test
5. Jalankan pytest secara lokal
6. Buat Pull Request ke develop
7. Review oleh anggota tim lain
8. Merge setelah disetujui dan CI hijau
9. Integrasi ke main saat fitur stabil
```

## Tahapan Kerja Harian

### 1. Perencanaan Task

- Baca dokumen acuan sebelum mulai:
  - [MVP_SCOPE.md](MVP_SCOPE.md)
  - [API_CONTRACT.md](API_CONTRACT.md)
  - [ARCHITECTURE.md](ARCHITECTURE.md)
  - [DECISION_LOG.md](DECISION_LOG.md)
- Pastikan task sesuai dengan scope MVP.
- Gunakan template task dari [TASK_TEMPLATE.md](TASK_TEMPLATE.md).

### 2. Implementasi

- Buat feature branch sesuai konvensi (lihat [GIT_WORKFLOW.md](GIT_WORKFLOW.md)).
- Tulis kode sesuai area tanggung jawab (lihat [TEAM_ROLES.md](TEAM_ROLES.md)).
- Jaga agar route handler tetap tipis, business logic di `src/services/`.
- Jangan duplikasi business logic di frontend.

### 3. Testing

- Jalankan test sebelum membuat Pull Request:

```bash
pytest tests/ -v
```

- Pastikan semua test yang ada tetap lulus.
- Tambahkan test baru jika ada logika baru.
- Lihat panduan lengkap di [TESTING_GUIDE.md](TESTING_GUIDE.md).

### 4. Review dan Merge

- Buat Pull Request menggunakan template yang tersedia di `.github/pull_request_template.md`.
- Minta review dari anggota tim yang bertanggung jawab atas area terkait.
- Pastikan CI GitHub Actions hijau sebelum merge.
- Merge ke `develop` terlebih dahulu, baru ke `main` saat stabil.

## Aturan Kolaborasi

### Yang Harus Dilakukan

- Selalu bekerja di feature branch, bukan langsung di `main` atau `develop`.
- Selalu jalankan test sebelum push.
- Selalu baca dan ikuti API contract yang sudah disepakati.
- Tulis pesan commit yang jelas dan deskriptif.
- Perbarui dokumentasi jika ada perubahan behavior.

### Yang Tidak Boleh Dilakukan

- Jangan commit file `.env` atau `.streamlit/secrets.toml`.
- Jangan commit dataset besar tanpa persetujuan tim.
- Jangan commit model artifact besar kecuali diperlukan untuk demo.
- Jangan mengubah API contract tanpa memperbarui dokumen, test, dan frontend.
- Jangan menambahkan fitur di luar scope MVP tanpa diskusi tim.
- Jangan push langsung ke `main`.

## Komunikasi Tim

- Gunakan Pull Request sebagai media diskusi teknis utama.
- Catat keputusan teknis penting di [DECISION_LOG.md](DECISION_LOG.md).
- Jika ada fitur baru yang ingin ditambahkan, masukkan ke backlog terlebih dahulu sesuai aturan di [MVP_SCOPE.md](MVP_SCOPE.md).

## Dokumen Acuan

| Dokumen | Kegunaan |
|---|---|
| [MVP_SCOPE.md](MVP_SCOPE.md) | Batasan scope dan definisi selesai |
| [API_CONTRACT.md](API_CONTRACT.md) | Kontrak API backend dan frontend |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Arsitektur sistem dan tanggung jawab folder |
| [DECISION_LOG.md](DECISION_LOG.md) | Riwayat keputusan teknis |
| [TASK_TEMPLATE.md](TASK_TEMPLATE.md) | Template task untuk tim dan Codex |
| [TEAM_ROLES.md](TEAM_ROLES.md) | Pembagian peran dan tanggung jawab |
| [GIT_WORKFLOW.md](GIT_WORKFLOW.md) | Strategi branching dan alur Git |
| [TESTING_GUIDE.md](TESTING_GUIDE.md) | Panduan testing |
| [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md) | Panduan setup dan pengembangan |
