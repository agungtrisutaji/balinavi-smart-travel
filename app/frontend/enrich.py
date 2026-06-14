"""
Enrichment layer untuk tampilan rekomendasi BaliNavi.

Modul ini TIDAK mengubah dataset maupun output model rekomendasi.
Tugasnya hanya memperkaya tampilan card dengan:
  - Foto tempat  -> Google Places API (butuh API key)
  - Deskripsi    -> Wikipedia / Wikimedia REST API (tanpa API key)

Semua pemanggilan API dilakukan berbasis nama tempat dari hasil
rekomendasi, dan dibungkus cache agar request tidak berulang.
Jika gagal, fungsi mengembalikan nilai fallback yang aman (None / teks
default) sehingga tampilan tetap rapi.
"""

import os
import re
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, Dict, Any, List
from urllib.parse import quote

import requests
import streamlit as st

try:
    from streamlit.runtime.scriptrunner import add_script_run_ctx, get_script_run_ctx
except Exception:  # pragma: no cover - jaga kompatibilitas versi streamlit
    add_script_run_ctx = None
    get_script_run_ctx = None


WIKI_HEADERS = {
    "User-Agent": "BaliNavi/1.0 (Smart Travel Planner; contact: balinavi@example.com)"
}

# Kata-kata generik yang TIDAK dipakai sebagai penentu kecocokan judul artikel
# (mis. "beach", "pantai"), karena yang menentukan adalah nama uniknya
# (mis. "Balangan", "Kuta", "Tanah Lot").
_GENERIC_TOKENS = {
    "beach", "pantai", "pura", "temple", "museum", "waterfall", "air", "terjun",
    "mount", "gunung", "danau", "lake", "hutan", "forest", "taman", "garden",
    "park", "monkey", "rice", "terrace", "sawah", "desa", "village", "pasar",
    "market", "bukit", "hill", "cliff", "tebing", "gua", "cave", "island",
    "pulau", "nusa", "the", "of", "di", "dan", "and", "bali", "indonesia",
    "wisata", "objek", "tempat", "kawasan",
}


def _tokenize(text: str) -> List[str]:
    """Pecah teks jadi token huruf/angka, lowercase."""
    return [t for t in re.split(r"[^a-z0-9]+", str(text).lower()) if t]


def _significant_tokens(place_name: str) -> List[str]:
    """Token unik penanda tempat (membuang kata generik)."""
    tokens = _tokenize(place_name)
    significant = [t for t in tokens if t not in _GENERIC_TOKENS and len(t) > 2]
    # Jika nama hanya terdiri dari kata generik, pakai apa adanya sebagai cadangan.
    return significant or tokens


def _title_matches_place(place_name: str, title: str) -> bool:
    """
    Pastikan judul artikel Wikipedia benar-benar mengacu ke tempat tsb.

    Aturannya: minimal satu token unik dari nama tempat harus muncul di
    judul artikel. Ini menyaring hasil nyasar seperti 'Marriott' untuk
    pencarian 'Balangan Beach'.
    """
    sig = _significant_tokens(place_name)
    if not sig:
        return False
    title_tokens = set(_tokenize(title))
    return any(tok in title_tokens for tok in sig)


def get_google_api_key() -> Optional[str]:
    """
    Ambil Google Places API key dengan aman.

    Prioritas:
      1. st.secrets["GOOGLE_API_KEY"]  (untuk deploy Streamlit / secrets.toml)
      2. environment variable GOOGLE_API_KEY

    Mengembalikan None jika tidak ada, sehingga enrichment foto bisa
    di-skip tanpa membuat aplikasi error.
    """
    try:
        key = st.secrets["GOOGLE_API_KEY"]
        if key:
            return str(key).strip()
    except Exception:
        pass

    key = os.getenv("GOOGLE_API_KEY")
    if key:
        return key.strip()

    return None


@st.cache_data(ttl=60 * 60 * 24, show_spinner=False)
def is_image_url_reachable(url: Optional[str]) -> bool:
    """
    Cek apakah URL gambar benar-benar bisa diakses dan mengembalikan
    konten gambar.

    Berguna untuk link dataset lama (mis. Google Maps / googleusercontent)
    yang sering 403 / expired. Tanpa cek ini, st.image akan tetap
    menampilkan ikon gambar rusak di browser.

    Return True hanya jika status 200 dan content-type berupa image/*.
    """
    if not url or not isinstance(url, str):
        return False

    url = url.strip()
    if not (url.startswith("http://") or url.startswith("https://")):
        return False

    try:
        response = requests.get(
            url,
            headers={"User-Agent": WIKI_HEADERS["User-Agent"]},
            timeout=8,
            stream=True,
        )
        content_type = response.headers.get("Content-Type", "").lower()
        ok = response.status_code == 200 and content_type.startswith("image")
        response.close()
        return ok
    except Exception:
        return False


@st.cache_data(ttl=60 * 60 * 24, show_spinner=False)
def get_google_place_photos(place_name: str, limit: int = 5) -> List[str]:
    """
    Ambil beberapa URL foto tempat dari Google Places API (Text Search v1)
    berdasarkan nama tempat dari hasil rekomendasi.

    Mengembalikan list URL foto (maksimal `limit`), atau list kosong jika
    tidak ada API key, tempat tidak ditemukan, atau terjadi error.
    """
    if not place_name:
        return []

    api_key = get_google_api_key()
    if not api_key:
        return []

    search_url = "https://places.googleapis.com/v1/places:searchText"

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "places.id,places.displayName,places.photos",
    }

    payload = {
        "textQuery": f"{place_name} Bali Indonesia",
        "languageCode": "id",
        "pageSize": 1,
    }

    try:
        response = requests.post(
            search_url,
            headers=headers,
            json=payload,
            timeout=10,
        )
        response.raise_for_status()

        data = response.json()
        places = data.get("places", [])
        if not places:
            return []

        photos = places[0].get("photos", [])
        if not photos:
            return []

        urls: List[str] = []
        for photo in photos[: max(1, limit)]:
            photo_name = photo.get("name")
            if not photo_name:
                continue
            urls.append(
                f"https://places.googleapis.com/v1/{photo_name}/media"
                f"?maxWidthPx=800&key={api_key}"
            )
        return urls

    except Exception:
        return []


@st.cache_data(ttl=60 * 60 * 24, show_spinner=False)
def get_google_place_photo(place_name: str) -> Optional[str]:
    """
    Ambil satu URL foto tempat (foto pertama) dari Google Places API.
    Dipertahankan untuk kompatibilitas; secara internal memakai
    get_google_place_photos.
    """
    photos = get_google_place_photos(place_name, limit=1)
    return photos[0] if photos else None


@st.cache_data(ttl=60 * 60 * 24 * 7, show_spinner=False)
def get_wikipedia_description(place_name: str) -> Dict[str, Any]:
    """
    Ambil deskripsi/ringkasan tempat dari Wikipedia (ID lalu EN).

    Akurasi dijaga: dari beberapa kandidat hasil pencarian, hanya artikel
    yang JUDULNYA cocok dengan nama tempat yang dipakai (lihat
    _title_matches_place). Halaman disambiguasi juga ditolak. Ini mencegah
    deskripsi nyasar (mis. 'Marriott' untuk 'Balangan Beach').

    Tidak membutuhkan API key. Mengembalikan dict:
      { "description": str, "source": str, "source_url": Optional[str] }

    Jika tidak ada artikel yang cocok, mengembalikan fallback description.
    """
    if place_name:
        for lang in ("id", "en"):
            try:
                search_url = f"https://{lang}.wikipedia.org/w/api.php"
                search_params = {
                    "action": "query",
                    "list": "search",
                    "srsearch": f"{place_name} Bali",
                    "format": "json",
                    "srlimit": 5,
                }

                search_response = requests.get(
                    search_url,
                    params=search_params,
                    headers=WIKI_HEADERS,
                    timeout=10,
                )
                search_response.raise_for_status()

                results = (
                    search_response.json()
                    .get("query", {})
                    .get("search", [])
                )
                if not results:
                    continue

                # Pilih kandidat pertama yang judulnya benar-benar cocok.
                matched_title = None
                for item in results:
                    title = item.get("title", "")
                    if _title_matches_place(place_name, title):
                        matched_title = title
                        break

                if not matched_title:
                    # Tidak ada yang cocok di bahasa ini, coba bahasa berikutnya.
                    continue

                summary_url = (
                    f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/"
                    f"{quote(matched_title)}"
                )
                summary_response = requests.get(
                    summary_url,
                    headers=WIKI_HEADERS,
                    timeout=10,
                )
                summary_response.raise_for_status()

                summary_data = summary_response.json()

                # Tolak halaman disambiguasi.
                if summary_data.get("type") == "disambiguation":
                    continue

                description = summary_data.get("extract")
                page_url = (
                    summary_data.get("content_urls", {})
                    .get("desktop", {})
                    .get("page")
                )

                if description:
                    return {
                        "description": description,
                        "source": f"Wikipedia {lang.upper()}",
                        "source_url": page_url,
                    }

            except Exception:
                continue

    return {
        "description": (
            f"{place_name} merupakan salah satu destinasi wisata yang dapat "
            "menjadi pilihan kunjungan berdasarkan minat pengguna."
        ),
        "source": "Fallback",
        "source_url": None,
    }


def prefetch_enrichment(place_names: List[str]) -> None:
    """
    Pra-ambil foto (Google Places) & deskripsi (Wikipedia) untuk daftar
    nama tempat secara paralel, agar cache "hangat" sebelum render.

    Tanpa ini, tiap card memanggil API secara berurutan saat render dan
    halaman terasa menggantung. Dengan prefetch + spinner di UI, semua
    request berjalan bersamaan sekali di awal.
    """
    names = [n for n in dict.fromkeys(place_names) if n]
    if not names:
        return

    ctx = None
    if get_script_run_ctx is not None:
        try:
            ctx = get_script_run_ctx()
        except Exception:
            ctx = None

    def _warm(name: str) -> None:
        if ctx is not None and add_script_run_ctx is not None:
            try:
                add_script_run_ctx(threading.current_thread(), ctx)
            except Exception:
                pass
        try:
            get_google_place_photos(name)
        except Exception:
            pass
        try:
            get_wikipedia_description(name)
        except Exception:
            pass

    try:
        with ThreadPoolExecutor(max_workers=min(8, len(names))) as executor:
            list(executor.map(_warm, names))
    except Exception:
        # Kalau prefetch gagal, render per-card tetap jalan (lebih lambat).
        pass
