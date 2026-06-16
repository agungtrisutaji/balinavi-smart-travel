import os
from typing import Any, Dict
import html as html_lib
from urllib.parse import quote_plus

import pandas as pd
import plotly.express as px
import requests
import streamlit as st
import streamlit.components.v1 as components

try:
    # Saat dijalankan sebagai package (mis. python -m / import dari root project)
    from app.frontend.enrich import (
        get_google_place_photos,
        get_wikipedia_description,
        is_image_url_reachable,
        prefetch_enrichment,
    )
except ImportError:
    # Saat dijalankan langsung: streamlit run app/frontend/streamlit_app.py
    from enrich import (
        get_google_place_photos,
        get_wikipedia_description,
        is_image_url_reachable,
        prefetch_enrichment,
    )



def get_app_config(key: str, default: str) -> str:
    """Read Streamlit secrets first, then environment variables for Docker."""
    try:
        value = st.secrets[key]
        if value:
            return str(value).strip()
    except Exception:
        pass

    return os.getenv(key, default)


# CONFIGURATION BACKEND URL
BACKEND_URL = get_app_config(
    "BACKEND_URL", "http://localhost:8000"
)

st.set_page_config(
    page_title="BaliNavi Smart Travel",
    page_icon="🌴",
    layout="wide",
    initial_sidebar_state="expanded",
)

# DETEKSI TEMA AKTIF (light/dark) dari Streamlit.
# Dipakai untuk menyalakan override CSS light-mode dan menyesuaikan
# warna komponen iframe (galeri, modal, peta).
try:
    THEME_TYPE = st.context.theme.type or "dark"
except Exception:
    THEME_TYPE = "dark"

IS_LIGHT = THEME_TYPE == "light"

# CUSTOM CSS
st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(circle at top left, rgba(20,184,166,0.20), transparent 28%),
            radial-gradient(circle at top right, rgba(245,158,11,0.14), transparent 25%),
            linear-gradient(135deg, #020617 0%, #0f172a 45%, #111827 100%);
        color: #e5e7eb;
    }

    .block-container {
        padding-top: 1.6rem;
        padding-bottom: 3rem;
        max-width: 1240px;
    }

    section[data-testid="stSidebar"] {
        background: #020617;
        border-right: 1px solid rgba(148,163,184,0.18);
    }

    section[data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }

    section[data-testid="stSidebar"] .stButton button {
        background: linear-gradient(135deg, #0f766e, #14b8a6) !important;
        color: white !important;
        border-radius: 12px;
        border: none;
        font-weight: 800;
    }

    .hero {
        position: relative;
        padding: 2.5rem 2.3rem;
        border-radius: 30px;
        background:
            linear-gradient(135deg, rgba(2,6,23,0.88), rgba(15,118,110,0.70), rgba(245,158,11,0.45)),
            url("https://images.unsplash.com/photo-1537996194471-e657df975ab4?auto=format&fit=crop&w=1600&q=80");
        background-size: cover;
        background-position: center;
        color: white;
        margin-bottom: 1.7rem;
        box-shadow: 0 24px 55px rgba(0, 0, 0, 0.35);
        border: 1px solid rgba(255,255,255,0.12);
    }

    .hero h1 {
        font-size: 3rem;
        line-height: 1.05;
        margin: 0 0 0.7rem 0;
        font-weight: 900;
        letter-spacing: -0.04em;
    }

    .hero p {
        font-size: 1.05rem;
        max-width: 720px;
        margin: 0;
        color: #e2e8f0;
    }

    .hero-badges {
        margin-top: 1.3rem;
        display: flex;
        flex-wrap: wrap;
        gap: 0.6rem;
    }

    .hero-badge {
        display: inline-flex;
        padding: 0.45rem 0.8rem;
        border-radius: 999px;
        background: rgba(15,23,42,0.55);
        backdrop-filter: blur(8px);
        color: #f8fafc;
        font-size: 0.86rem;
        font-weight: 800;
        border: 1px solid rgba(255,255,255,0.16);
    }

    .section-title {
        font-size: 1.5rem;
        font-weight: 900;
        color: #f8fafc;
        margin-top: 0.7rem;
        margin-bottom: 0.3rem;
        letter-spacing: -0.02em;
    }

    .section-subtitle {
        color: #94a3b8;
        margin-bottom: 1rem;
        font-size: 0.95rem;
    }

    .glass-card {
        background: rgba(15,23,42,0.72);
        border: 1px solid rgba(148,163,184,0.18);
        box-shadow: 0 18px 45px rgba(0,0,0,0.26);
        border-radius: 24px;
        padding: 1.3rem;
        margin-bottom: 1rem;
    }

    .result-header {
        padding: 1.25rem 1.35rem;
        border-radius: 24px;
        background: linear-gradient(135deg, #042f2e, #0f766e, #92400e);
        color: white;
        margin: 1.5rem 0 1rem 0;
        box-shadow: 0 18px 42px rgba(0,0,0,0.30);
        border: 1px solid rgba(255,255,255,0.12);
    }

    .result-header h2 {
        margin: 0;
        font-size: 1.7rem;
        font-weight: 900;
    }

    .result-header p {
        margin: 0.3rem 0 0 0;
        color: #d1d5db;
    }

    .destination-card {
        border-radius: 24px;
        padding: 1.25rem 1.35rem;
        background: linear-gradient(145deg, rgba(15,23,42,0.95), rgba(30,41,59,0.92));
        border: 1px solid rgba(148,163,184,0.18);
        box-shadow: 0 16px 38px rgba(0,0,0,0.28);
        margin-bottom: 1rem;
        transition: all 0.18s ease;
    }

    .destination-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 24px 52px rgba(0,0,0,0.36);
        border-color: rgba(45,212,191,0.45);
    }

    .destination-top {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        gap: 1rem;
        margin-bottom: 0.65rem;
    }

    .rank-pill {
        min-width: 42px;
        height: 42px;
        border-radius: 14px;
        background: linear-gradient(135deg, #f59e0b, #14b8a6);
        color: #020617;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-weight: 950;
        font-size: 1rem;
        box-shadow: 0 10px 22px rgba(20,184,166,0.22);
    }

    .destination-title {
        font-size: 1.25rem;
        font-weight: 900;
        color: #f8fafc;
        line-height: 1.25;
        margin-bottom: 0.25rem;
    }

    .destination-location {
        color: #cbd5e1;
        font-size: 0.93rem;
        margin-bottom: 0.55rem;
    }

    .badge-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.45rem;
        margin: 0.55rem 0 0.75rem 0;
    }

    .badge {
        display: inline-flex;
        align-items: center;
        padding: 0.34rem 0.7rem;
        border-radius: 999px;
        background: rgba(20,184,166,0.14);
        color: #5eead4;
        border: 1px solid rgba(45,212,191,0.25);
        font-size: 0.78rem;
        font-weight: 800;
    }

    .badge-dark {
        background: rgba(148,163,184,0.12);
        color: #cbd5e1;
        border: 1px solid rgba(148,163,184,0.22);
    }

    .desc {
        color: #d1d5db;
        line-height: 1.55;
        font-size: 0.95rem;
        margin: 0.65rem 0 0.8rem 0;
    }

    .mini-stat-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 0.65rem;
        margin-top: 0.8rem;
    }

    .mini-stat {
        border-radius: 16px;
        padding: 0.75rem;
        background: rgba(2,6,23,0.55);
        border: 1px solid rgba(148,163,184,0.18);
    }

    .mini-stat-label {
        color: #94a3b8;
        font-size: 0.75rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-bottom: 0.15rem;
    }

    .mini-stat-value {
        color: #f8fafc;
        font-size: 0.98rem;
        font-weight: 900;
    }

    .maps-link {
        display: inline-block;
        margin-top: 0.85rem;
        padding: 0.58rem 0.95rem;
        border-radius: 12px;
        background: linear-gradient(135deg, #0f766e, #14b8a6);
        color: white !important;
        text-decoration: none !important;
        font-weight: 900;
        font-size: 0.9rem;
        box-shadow: 0 10px 22px rgba(20,184,166,0.20);
    }

    .maps-link:hover {
        background: linear-gradient(135deg, #f59e0b, #14b8a6);
        color: #020617 !important;
    }

    div[data-testid="stMetric"] {
        background: rgba(15,23,42,0.88);
        border: 1px solid rgba(148,163,184,0.18);
        padding: 1rem;
        border-radius: 20px;
        box-shadow: 0 14px 32px rgba(0,0,0,0.22);
    }

    div[data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
        font-weight: 800;
    }

    div[data-testid="stMetricValue"] {
        font-size: 1.35rem;
        font-weight: 900;
        color: #f8fafc;
    }

    .stButton > button {
        width: 100%;
        border-radius: 14px;
        font-weight: 900;
        background: linear-gradient(135deg, #f59e0b, #14b8a6);
        color: #020617;
        border: none;
        padding: 0.85rem 1rem;
        box-shadow: 0 12px 24px rgba(20,184,166,0.18);
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #14b8a6, #f59e0b);
        color: #020617;
        border: none;
    }

    /* Form/input colors */
    label, .stMarkdown, .stText {
        color: #e5e7eb;
    }

    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div {
        background-color: rgba(15,23,42,0.85);
        border-color: rgba(148,163,184,0.25);
        color: #e5e7eb;
    }

    .stNumberInput input {
        background-color: rgba(15,23,42,0.85);
        color: #f8fafc;
    }

    .stDataFrame {
        border-radius: 18px;
        overflow: hidden;
    }

    @media (max-width: 900px) {
        .hero h1 {
            font-size: 2.2rem;
        }

        .mini-stat-grid {
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }
    }

    /* ALLOCATION TABLE */
    .alloc-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        background: rgba(15,23,42,0.72);
        border: 1px solid rgba(148,163,184,0.18);
        border-radius: 20px;
        overflow: hidden;
        box-shadow: 0 16px 38px rgba(0,0,0,0.26);
        font-size: 0.92rem;
    }

    .alloc-table thead th {
        text-align: left;
        padding: 0.85rem 1.1rem;
        background: linear-gradient(135deg, #042f2e, #0f766e);
        color: #f0fdfa;
        font-size: 0.74rem;
        font-weight: 900;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        border-bottom: 1px solid rgba(148,163,184,0.18);
    }

    .alloc-table thead th.num {
        text-align: right;
    }

    .alloc-table tbody td {
        padding: 0.8rem 1.1rem;
        border-bottom: 1px solid rgba(148,163,184,0.10);
        color: #e5e7eb;
        vertical-align: middle;
    }

    .alloc-table tbody tr:last-child td {
        border-bottom: none;
    }

    .alloc-table tbody tr:hover td {
        background: rgba(20,184,166,0.07);
    }

    .alloc-component {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        font-weight: 800;
        color: #f8fafc;
    }

    .alloc-dot {
        width: 11px;
        height: 11px;
        border-radius: 50%;
        flex: 0 0 auto;
        box-shadow: 0 0 10px rgba(20,184,166,0.45);
    }

    .alloc-amount {
        text-align: right;
        font-weight: 800;
        color: #5eead4;
        white-space: nowrap;
    }

    .alloc-pct-cell {
        min-width: 160px;
    }

    .alloc-pct-wrap {
        display: flex;
        align-items: center;
        gap: 0.65rem;
    }

    .alloc-bar-track {
        flex: 1;
        height: 8px;
        border-radius: 999px;
        background: rgba(148,163,184,0.18);
        overflow: hidden;
    }

    .alloc-bar-fill {
        height: 100%;
        border-radius: 999px;
        background: linear-gradient(90deg, #14b8a6, #f59e0b);
    }

    .alloc-pct-value {
        font-weight: 900;
        color: #f8fafc;
        font-size: 0.85rem;
        min-width: 38px;
        text-align: right;
    }

    /* DETAIL CARD */
    .dc-head {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        gap: 1rem;
        margin: 0.9rem 0 0.2rem 0;
    }
    .dc-title {
        font-size: 1.55rem;
        font-weight: 900;
        color: #f8fafc;
        line-height: 1.15;
        letter-spacing: -0.02em;
    }
    .dc-rank {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-width: 38px;
        height: 30px;
        padding: 0 0.55rem;
        border-radius: 10px;
        background: linear-gradient(135deg, #f59e0b, #14b8a6);
        color: #020617;
        font-weight: 950;
        font-size: 0.95rem;
        margin-right: 0.55rem;
        vertical-align: middle;
    }
    .dc-location {
        color: #cbd5e1;
        font-size: 0.95rem;
        margin-top: 0.4rem;
    }
    .dc-score {
        flex: 0 0 auto;
        text-align: center;
        padding: 0.55rem 1rem;
        border-radius: 16px;
        background: rgba(2,6,23,0.55);
        border: 1px solid rgba(148,163,184,0.2);
    }
    .dc-score-label {
        font-size: 0.68rem;
        color: #94a3b8;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .dc-score-value {
        font-size: 1.3rem;
        font-weight: 900;
        color: #5eead4;
    }
    .dc-pills {
        display: flex;
        flex-wrap: wrap;
        gap: 0.45rem;
        margin: 0.85rem 0 0.2rem 0;
    }
    .dc-pill {
        display: inline-flex;
        align-items: center;
        padding: 0.34rem 0.78rem;
        border-radius: 999px;
        background: rgba(20,184,166,0.14);
        color: #5eead4;
        border: 1px solid rgba(45,212,191,0.28);
        font-size: 0.78rem;
        font-weight: 800;
    }
    .dc-pill.alt {
        background: rgba(148,163,184,0.12);
        color: #cbd5e1;
        border: 1px solid rgba(148,163,184,0.22);
    }
    .dc-info-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 0.7rem;
        margin: 0.9rem 0 0.2rem 0;
    }
    .dc-info {
        background: rgba(2,6,23,0.5);
        border: 1px solid rgba(148,163,184,0.18);
        border-radius: 16px;
        padding: 0.8rem 0.95rem;
    }
    .dc-info-label {
        font-size: 0.7rem;
        color: #94a3b8;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }
    .dc-info-value {
        font-size: 1.08rem;
        color: #f8fafc;
        font-weight: 900;
        margin-top: 0.18rem;
    }
    .dc-section-head {
        font-size: 1.12rem;
        font-weight: 900;
        color: #f8fafc;
        margin: 1.25rem 0 0.5rem 0;
        display: flex;
        align-items: center;
        gap: 0.45rem;
    }
    .dc-desc summary {
        list-style: none;
        cursor: pointer;
        outline: none;
    }
    .dc-desc summary::-webkit-details-marker { display: none; }
    .dc-desc-clamp {
        color: #d1d5db;
        line-height: 1.65;
        font-size: 0.96rem;
        display: -webkit-box;
        -webkit-line-clamp: 4;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }
    .dc-desc-full {
        color: #d1d5db;
        line-height: 1.65;
        font-size: 0.96rem;
        display: none;
    }
    .dc-desc details[open] .dc-desc-clamp { display: none; }
    .dc-desc details[open] .dc-desc-full { display: block; }
    .dc-readmore {
        color: #5eead4;
        font-weight: 800;
        font-size: 0.88rem;
        margin-top: 0.5rem;
        display: inline-block;
    }
    .dc-readmore::after { content: "Baca selengkapnya \\25BE"; }
    .dc-desc details[open] .dc-readmore::after { content: "Tutup \\25B4"; }
    .dc-desc-source {
        color: #94a3b8;
        font-size: 0.8rem;
        margin-top: 0.5rem;
    }
    @media (max-width: 760px) {
        .dc-info-grid { grid-template-columns: 1fr; }
        .dc-title { font-size: 1.25rem; }
        .dc-head { flex-direction: column; }
    }

    /* Tombol "Lihat semua foto" -> satu warna (tidak gradient) */
    [class*="st-key-open_gallery"] button {
        background: #14b8a6 !important;
        color: #022c22 !important;
        border: none !important;
    }
    [class*="st-key-open_gallery"] button:hover {
        background: #0f766e !important;
        color: #f0fdfa !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# LIGHT MODE OVERRIDES
# Desain default project adalah dark. Saat user memilih tema Light di menu
# Streamlit, kita override warna semua surface & teks agar ikut terang.
if IS_LIGHT:
    st.markdown(
        """
        <style>
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(20,184,166,0.10), transparent 28%),
                radial-gradient(circle at top right, rgba(245,158,11,0.08), transparent 25%),
                linear-gradient(135deg, #f8fafc 0%, #eef2f7 45%, #e7edf3 100%) !important;
            color: #0f172a !important;
        }
        section[data-testid="stSidebar"] {
            background: #ffffff !important;
            border-right: 1px solid rgba(15,23,42,0.10) !important;
        }
        section[data-testid="stSidebar"] * { color: #0f172a !important; }

        label, .stMarkdown, .stText { color: #0f172a; }

        .glass-card, .destination-card {
            background: #ffffff !important;
            border: 1px solid rgba(15,23,42,0.10) !important;
            box-shadow: 0 14px 34px rgba(15,23,42,0.10) !important;
        }
        .section-title, .destination-title, .dc-title { color: #0f172a !important; }
        .section-subtitle { color: #475569 !important; }

        /* Metric & input */
        div[data-testid="stMetric"] {
            background: #ffffff !important;
            border: 1px solid rgba(15,23,42,0.10) !important;
            box-shadow: 0 10px 24px rgba(15,23,42,0.08) !important;
        }
        div[data-testid="stMetricLabel"] { color: #475569 !important; }
        div[data-testid="stMetricValue"] { color: #0f172a !important; }
        div[data-baseweb="select"] > div,
        div[data-baseweb="input"] > div {
            background-color: #ffffff !important;
            border-color: rgba(15,23,42,0.18) !important;
            color: #0f172a !important;
        }
        .stNumberInput input { background-color: #ffffff !important; color: #0f172a !important; }

        /* Allocation table */
        .alloc-table {
            background: #ffffff !important;
            border: 1px solid rgba(15,23,42,0.10) !important;
            box-shadow: 0 12px 28px rgba(15,23,42,0.10) !important;
        }
        .alloc-table tbody td { color: #1e293b !important; border-bottom-color: rgba(15,23,42,0.08) !important; }
        .alloc-component { color: #0f172a !important; }
        .alloc-amount { color: #0d9488 !important; }
        .alloc-pct-value { color: #0f172a !important; }
        .alloc-bar-track { background: rgba(15,23,42,0.10) !important; }
        .alloc-table tbody tr:hover td { background: rgba(20,184,166,0.08) !important; }

        /* Detail card */
        .dc-location { color: #475569 !important; }
        .dc-score {
            background: #f1f5f9 !important;
            border: 1px solid rgba(15,23,42,0.10) !important;
        }
        .dc-score-label { color: #64748b !important; }
        .dc-score-value { color: #0d9488 !important; }
        .dc-pill {
            background: rgba(13,148,136,0.12) !important;
            color: #0f766e !important;
            border: 1px solid rgba(13,148,136,0.30) !important;
        }
        .dc-pill.alt {
            background: rgba(15,23,42,0.06) !important;
            color: #334155 !important;
            border: 1px solid rgba(15,23,42,0.15) !important;
        }
        .dc-info {
            background: #f1f5f9 !important;
            border: 1px solid rgba(15,23,42,0.10) !important;
        }
        .dc-info-label { color: #64748b !important; }
        .dc-info-value { color: #0f172a !important; }
        .dc-section-head { color: #0f172a !important; }
        .dc-desc-clamp, .dc-desc-full { color: #334155 !important; }
        .dc-readmore { color: #0d9488 !important; }
        .dc-desc-source { color: #64748b !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )


# API FUNCTIONS
@st.cache_data(ttl=300)
def fetch_metadata() -> Dict[str, Any]:
    response = requests.get(f"{BACKEND_URL}/metadata", timeout=15)
    response.raise_for_status()
    return response.json()


def request_trip_plan(payload: Dict[str, Any]) -> Dict[str, Any]:
    response = requests.post(f"{BACKEND_URL}/plan-trip", json=payload, timeout=30)
    response.raise_for_status()
    return response.json()

# HELPER FUNCTIONS
def format_idr(value: Any) -> str:
    try:
        return f"IDR {int(float(value)):,}".replace(",", ".")
    except (ValueError, TypeError):
        return "IDR 0"


def safe_get(data: Dict[str, Any], *keys: str, default: Any = "-") -> Any:
    for key in keys:
        value = data.get(key)
        if value is not None and value != "":
            return value
    return default


def build_address(destination: Dict[str, Any]) -> str:
    full_address = safe_get(
        destination,
        "alamat",
        "address",
        "full_address",
        default="",
    )

    if full_address:
        return full_address

    district = safe_get(destination, "district", "kecamatan", default="")
    regency_city = safe_get(
        destination,
        "regency_city",
        "kabupaten_kota",
        "city",
        "location",
        default="",
    )

    parts = [part for part in [district, regency_city, "Bali"] if part and part != "-"]
    return ", ".join(parts) if parts else "-"


def format_score(value: Any) -> str:
    try:
        return f"{float(value):.3f}"
    except (TypeError, ValueError):
        return "-"


def format_rating(value: Any) -> str:
    try:
        return f"{float(value):.1f}"
    except (TypeError, ValueError):
        return "-"


def is_valid_image_url(url: Any) -> bool:
    if not url or not isinstance(url, str):
        return False

    url = url.strip()

    if url in ["-", "None", "none", "null", "NULL"]:
        return False

    return url.startswith("http://") or url.startswith("https://")


def render_image_placeholder() -> None:
    st.markdown(
        "<div style=\"height:210px;width:100%;border-radius:18px;"
        "background:linear-gradient(135deg,rgba(20,184,166,0.22),rgba(245,158,11,0.18));"
        "border:1px solid rgba(148,163,184,0.25);display:flex;align-items:center;"
        "justify-content:center;color:#e2e8f0;font-weight:900;text-align:center;"
        "box-shadow:inset 0 0 40px rgba(2,6,23,0.25);\">"
        "🌴<br>Gambar tidak tersedia</div>",
        unsafe_allow_html=True,
    )


def prettify_component(name: Any) -> str:
    """Ubah 'destination_tickets' -> 'Destination Tickets'."""
    text = str(name).replace("_", " ").replace("-", " ").strip()
    return text.title() if text else "-"


def render_detail_gallery(name: str, idx: int, image_urls: list[str]) -> None:
    """
    Galeri foto gaya detail-card (komponen iframe + JS):
    - gambar utama besar di kiri,
    - 4 thumbnail dalam grid 2x2 di kanan,
    - overlay "+N" di thumbnail terakhir bila foto > 5,
    - badge ranking #idx + nama destinasi sebagai overlay di gambar utama,
    - klik thumbnail untuk mengganti gambar utama.
    Responsive: di layar sempit, gambar utama melebar penuh & thumbnail
    menjadi baris di bawahnya.
    """
    valid = [u for u in (image_urls or []) if is_valid_image_url(u)]

    safe_name = html_lib.escape(str(name))

    if not valid:
        # Tidak ada foto -> placeholder bertema dengan badge ranking + nama.
        st.markdown(
            "<div style='position:relative;height:240px;width:100%;border-radius:18px;"
            "background:linear-gradient(135deg,rgba(20,184,166,0.22),rgba(245,158,11,0.18));"
            "border:1px solid rgba(148,163,184,0.25);display:flex;align-items:center;"
            "justify-content:center;color:#e2e8f0;font-weight:900;'>"
            f"<span style='position:absolute;top:14px;left:14px;background:rgba(2,6,23,0.7);"
            "padding:0.3rem 0.7rem;border-radius:10px;font-size:0.85rem;'>"
            f"#{idx} {safe_name}</span>"
            "🌴 Gambar tidak tersedia</div>",
            unsafe_allow_html=True,
        )
        return

    main_url = valid[0]
    thumbs = valid[1:5]
    extra = max(0, len(valid) - 5)

    # Thumbnails (maksimal 4). Bila kurang dari 4, sisanya kosong.
    thumb_cells = ""
    for i in range(4):
        if i < len(thumbs):
            url = thumbs[i]
            overlay = ""
            if i == 3 and extra > 0:
                overlay = f"<span class='thumb-more'>+{extra}</span>"
            # data-src dipakai JS untuk swap gambar utama.
            thumb_cells += (
                f"<div class='thumb' data-src='{url}'>"
                f"<img src='{url}' alt='Foto {i + 2}' loading='lazy'>{overlay}</div>"
            )
        else:
            thumb_cells += "<div class='thumb empty'></div>"

    template = """
<!doctype html><html><head><meta charset="utf-8"><style>
*{box-sizing:border-box;} html,body{margin:0;padding:0;background:transparent;overflow:hidden;
font-family:"Source Sans Pro",-apple-system,BlinkMacSystemFont,sans-serif;}
.gallery{display:grid;grid-template-columns:1.7fr 1fr 1fr;grid-template-rows:1fr 1fr;gap:8px;height:300px;}
.main{grid-column:1;grid-row:1/3;position:relative;border-radius:16px;overflow:hidden;cursor:pointer;
border:1px solid rgba(148,163,184,0.18);}
.main img{width:100%;height:100%;object-fit:cover;display:block;}
.main .scrim{position:absolute;left:0;right:0;bottom:0;padding:14px;
background:linear-gradient(transparent,rgba(2,6,23,0.85));}
.rank{display:inline-flex;align-items:center;justify-content:center;min-width:34px;height:28px;
padding:0 8px;border-radius:9px;background:linear-gradient(135deg,#f59e0b,#14b8a6);color:#020617;
font-weight:900;font-size:0.85rem;margin-right:8px;}
.title{color:#fff;font-weight:900;font-size:1.05rem;text-shadow:0 2px 8px rgba(0,0,0,0.5);}
.thumb{position:relative;border-radius:14px;overflow:hidden;cursor:pointer;
border:1px solid rgba(148,163,184,0.18);transition:transform .15s ease,border-color .15s ease;}
.thumb:hover{transform:scale(1.02);border-color:rgba(45,212,191,0.5);}
.thumb img{width:100%;height:100%;object-fit:cover;display:block;}
.thumb.empty{background:__EMPTYBG__;cursor:default;}
.thumb-more{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;
background:rgba(2,6,23,0.62);color:#fff;font-weight:900;font-size:1.2rem;backdrop-filter:blur(2px);}
@media(max-width:620px){
.gallery{grid-template-columns:1fr 1fr 1fr 1fr;grid-template-rows:2fr 1fr;height:300px;}
.main{grid-column:1/5;grid-row:1;}
.thumb:nth-of-type(1){grid-column:1;grid-row:2;}
.thumb:nth-of-type(2){grid-column:2;grid-row:2;}
.thumb:nth-of-type(3){grid-column:3;grid-row:2;}
.thumb:nth-of-type(4){grid-column:4;grid-row:2;}
}
</style></head><body>
<div class="gallery">
<div class="main" id="main"><img id="mainImg" src="__MAIN__" alt="__NAME__">
<div class="scrim"><span class="rank">#__IDX__</span><span class="title">__NAME__</span></div></div>
__THUMBS__
</div>
<script>(function(){
var mainImg=document.getElementById("mainImg");
document.querySelectorAll(".thumb[data-src]").forEach(function(t){
t.addEventListener("click",function(){
var s=t.getAttribute("data-src");
var cur=mainImg.getAttribute("src");
var tImg=t.querySelector("img");
mainImg.setAttribute("src",s);
if(tImg){tImg.setAttribute("src",cur);}  // tukar agar foto sebelumnya tetap bisa diakses
});});
})();</script>
</body></html>
"""

    component_html = (
        template.replace("__MAIN__", main_url)
        .replace("__THUMBS__", thumb_cells)
        .replace("__IDX__", str(idx))
        .replace("__NAME__", safe_name)
        .replace("__EMPTYBG__", "rgba(15,23,42,0.08)" if IS_LIGHT else "rgba(15,23,42,0.6)")
    )
    components.html(component_html, height=312, scrolling=False)


def render_location_map(name: str, maps_url: str = "") -> None:
    """
    Embed peta lokasi destinasi (Google Maps embed, tanpa API key) dengan
    marker berdasarkan nama tempat.
    """
    query = quote_plus(f"{name} Bali Indonesia")
    src = f"https://www.google.com/maps?q={query}&z=14&output=embed"
    st.markdown(
        "<div style='border-radius:16px;overflow:hidden;border:1px solid "
        "rgba(148,163,184,0.2);box-shadow:0 12px 28px rgba(0,0,0,0.28);"
        "margin-bottom:0.9rem;'>"
        f"<iframe src='{src}' width='100%' height='240' style='border:0;display:block;' "
        "loading='lazy' referrerpolicy='no-referrer-when-downgrade'></iframe></div>",
        unsafe_allow_html=True,
    )


def render_modal_carousel(image_urls: list[str]) -> None:
    """
    Carousel foto ukuran besar untuk modal: tombol panah ◀ ▶ yang bisa
    diklik, dot indikator, counter, navigasi keyboard, dan swipe sentuh.
    """
    valid = [u for u in (image_urls or []) if is_valid_image_url(u)]
    if not valid:
        st.info("Tidak ada foto untuk ditampilkan.")
        return

    slides = "".join(
        f"<div class='ms'><img src='{u}' alt='Foto destinasi'></div>" for u in valid
    )
    dots = "".join(
        f"<button class='md{' on' if i == 0 else ''}' data-i='{i}' "
        f"aria-label='Foto {i + 1}'></button>"
        for i in range(len(valid))
    )

    template = """
<!doctype html><html><head><meta charset="utf-8"><style>
*{box-sizing:border-box;} html,body{margin:0;padding:0;background:transparent;overflow:hidden;
font-family:"Source Sans Pro",-apple-system,BlinkMacSystemFont,sans-serif;}
.mc{position:relative;width:100%;border-radius:16px;overflow:hidden;background:__BG__;
border:1px solid rgba(148,163,184,0.2);user-select:none;}
.mvp{width:100%;overflow:hidden;}
.mt{display:flex;transition:transform .38s cubic-bezier(0.22,0.61,0.36,1);}
.ms{min-width:100%;height:460px;display:flex;align-items:center;justify-content:center;background:__BG__;}
.ms img{max-width:100%;max-height:460px;width:auto;height:auto;object-fit:contain;display:block;}
.mnav{position:absolute;top:50%;transform:translateY(-50%);width:46px;height:46px;
border:1px solid rgba(255,255,255,0.2);border-radius:50%;background:rgba(2,6,23,0.6);
color:#f8fafc;font-size:26px;line-height:1;cursor:pointer;display:flex;align-items:center;
justify-content:center;backdrop-filter:blur(6px);transition:background .15s,transform .15s;z-index:3;}
.mnav:hover{background:linear-gradient(135deg,#0f766e,#14b8a6);transform:translateY(-50%) scale(1.08);}
.mprev{left:14px;} .mnext{right:14px;}
.mcount{position:absolute;top:12px;right:14px;padding:0.3rem 0.7rem;border-radius:999px;
background:rgba(2,6,23,0.72);color:#f8fafc;font-size:0.78rem;font-weight:800;
border:1px solid rgba(255,255,255,0.16);backdrop-filter:blur(6px);z-index:3;}
.mdots{position:absolute;bottom:14px;left:50%;transform:translateX(-50%);display:flex;gap:7px;z-index:3;}
.md{width:9px;height:9px;border-radius:999px;border:none;background:rgba(255,255,255,0.5);
cursor:pointer;padding:0;transition:width .2s,background .2s;}
.md.on{width:22px;background:#14b8a6;}
</style></head><body>
<div class="mc">
<div class="mvp"><div class="mt" id="mt">__SLIDES__</div></div>
<button class="mnav mprev" id="mprev" aria-label="Sebelumnya">&#8249;</button>
<button class="mnav mnext" id="mnext" aria-label="Berikutnya">&#8250;</button>
<div class="mcount"><span class="mcur">1</span>/__COUNT__</div>
<div class="mdots" id="mdots">__DOTS__</div>
</div>
<script>(function(){
var mt=document.getElementById("mt");var n=mt?mt.children.length:0;if(n<1)return;
var idx=0;var dots=document.querySelectorAll(".md");var cur=document.querySelector(".mcur");
function go(i){idx=(i+n)%n;mt.style.transform="translateX("+(-idx*100)+"%)";
dots.forEach(function(d,di){d.classList.toggle("on",di===idx);});if(cur)cur.textContent=(idx+1);}
var p=document.getElementById("mprev"),nx=document.getElementById("mnext");
if(p)p.addEventListener("click",function(){go(idx-1);});
if(nx)nx.addEventListener("click",function(){go(idx+1);});
dots.forEach(function(d){d.addEventListener("click",function(){go(parseInt(d.getAttribute("data-i"),10));});});
document.addEventListener("keydown",function(e){if(e.key==="ArrowLeft")go(idx-1);if(e.key==="ArrowRight")go(idx+1);});
var sx=null,vp=document.querySelector(".mvp");
vp.addEventListener("touchstart",function(e){sx=e.touches[0].clientX;},{passive:true});
vp.addEventListener("touchend",function(e){if(sx===null)return;var dx=e.changedTouches[0].clientX-sx;
if(Math.abs(dx)>40)go(dx<0?idx+1:idx-1);sx=null;},{passive:true});
})();</script>
</body></html>
"""
    component_html = (
        template.replace("__SLIDES__", slides)
        .replace("__DOTS__", dots)
        .replace("__COUNT__", str(len(valid)))
        .replace("__BG__", "#e7edf3" if IS_LIGHT else "#020617")
    )
    components.html(component_html, height=482, scrolling=False)


@st.dialog("Galeri Foto", width="large")
def open_gallery_modal(place_name: str, image_urls: list[str]) -> None:
    """Modal berisi carousel foto besar yang bisa digeser dengan tombol."""
    st.markdown(f"#### {place_name}")
    render_modal_carousel(image_urls)


def render_allocation_table(allocation_df: pd.DataFrame) -> None:
    """
    Render tabel alokasi budget sebagai tabel HTML custom yang senada
    dengan gaya glass-card project (dark, aksen teal/amber, progress bar).
    """
    # Palet titik warna per baris (selaras tema teal -> amber).
    dot_colors = ["#14b8a6", "#22d3ee", "#f59e0b", "#a78bfa", "#34d399", "#fb7185"]

    # Total untuk normalisasi lebar bar jika percentage tidak tersedia.
    amounts = []
    for _, row in allocation_df.iterrows():
        try:
            amounts.append(float(row.get("amount", 0)))
        except (TypeError, ValueError):
            amounts.append(0.0)
    total_amount = sum(amounts) or 1.0

    rows_html = ""
    for i, (_, row) in enumerate(allocation_df.iterrows()):
        component = prettify_component(row.get("component", "-"))
        amount_raw = row.get("amount", 0)

        pct_value = row.get("percentage", None)
        try:
            pct = float(pct_value)
        except (TypeError, ValueError):
            try:
                pct = float(amount_raw) / total_amount * 100
            except (TypeError, ValueError):
                pct = 0.0

        pct = max(0.0, min(100.0, pct))
        color = dot_colors[i % len(dot_colors)]

        # HTML harus kompak tanpa indentasi, kalau tidak Streamlit/markdown
        # akan menganggapnya code block dan menampilkan tag mentah.
        rows_html += (
            "<tr>"
            "<td><div class='alloc-component'>"
            f"<span class='alloc-dot' style='background:{color};'></span>"
            f"{component}</div></td>"
            f"<td class='alloc-amount'>{format_idr(amount_raw)}</td>"
            "<td class='alloc-pct-cell'><div class='alloc-pct-wrap'>"
            "<div class='alloc-bar-track'>"
            f"<div class='alloc-bar-fill' style='width:{pct:.0f}%;'></div></div>"
            f"<span class='alloc-pct-value'>{pct:.0f}%</span>"
            "</div></td>"
            "</tr>"
        )

    table_html = (
        "<table class='alloc-table'>"
        "<thead><tr>"
        "<th>Komponen</th>"
        "<th class='num'>Jumlah</th>"
        "<th>Porsi</th>"
        "</tr></thead>"
        f"<tbody>{rows_html}</tbody>"
        "</table>"
    )

    st.markdown(table_html, unsafe_allow_html=True)

# SESSION STATE
if "trip_result" not in st.session_state:
    st.session_state.trip_result = None

if "last_payload" not in st.session_state:
    st.session_state.last_payload = None

def get_sort_value(destination: Dict[str, Any], field_names: list[str], default: Any = 0) -> Any:
    for field in field_names:
        value = destination.get(field)
        if value is not None and value != "":
            try:
                return float(value)
            except (ValueError, TypeError):
                return value
    return default



# SIDEBAR - OPSIONAL
with st.sidebar:
    st.markdown("## 🌴 BaliNavi")
    st.caption("Smart Travel Planner")

    st.markdown("---")
    st.markdown("### Status Backend")
    st.code(BACKEND_URL, language="text")

    if st.button("Check Backend"):
        try:
            fetch_metadata()
            st.success("Backend aktif")
        except requests.RequestException as exc:
            st.error(f"Backend error: {exc}")

    st.markdown("---")
    st.markdown("### Flow Aplikasi")
    st.caption("1. Isi detail perjalanan")
    st.caption("2. Pilih preferensi wisata")
    st.caption("3. Generate rekomendasi")
    st.caption("4. Buka Maps untuk destinasi")



# HEADER
st.markdown(
    """
    <div class="hero">
        <h1>BaliNavi Smart Travel</h1>
        <p>
            Platform rekomendasi destinasi wisata Bali berbasis budget, durasi perjalanan,
            lokasi, kategori wisata, dan preferensi pengguna.
        </p>
        <div class="hero-badges">
            <span class="hero-badge">Budget-aware</span>
            <span class="hero-badge">Personalized Recommendation</span>
            <span class="hero-badge">Bali Destination Planner</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# LOAD METADATA
try:
    metadata = fetch_metadata()
except requests.RequestException as exc:
    st.error(f"Backend tidak bisa diakses: {exc}")
    st.stop()


travel_types = metadata.get("travel_types", ["solo", "couple", "family", "group"])
categories = metadata.get("categories", [])
sub_categories = metadata.get("sub_categories", [])
max_recommendations = int(metadata.get("max_recommendations", 10))

locations = metadata.get(
    "locations",
    [
        "Badung",
        "Gianyar",
        "Denpasar",
        "Karangasem",
        "Tabanan",
        "Buleleng",
        "Bangli",
        "Klungkung",
        "Jembrana",
    ],
)



# INPUT FORM
st.markdown('<div class="section-title">Buat Rencana Perjalanan</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-subtitle">Masukkan detail perjalanan dan preferensi destinasi yang kamu inginkan.</div>',
    unsafe_allow_html=True,
)

with st.form("trip_plan_form"):

    left_col, right_col = st.columns([1, 1], gap="large")

    with left_col:
        st.markdown("#### 💰 Budget & Trip Detail")

        total_budget = st.number_input(
            "Total Budget",
            min_value=100_000,
            value=5_000_000,
            step=100_000,
            help="Masukkan total budget perjalanan dalam Rupiah.",
        )

        trip_col_1, trip_col_2 = st.columns(2)

        with trip_col_1:
            duration_days = st.number_input(
                "Durasi",
                min_value=1,
                max_value=30,
                value=3,
                step=1,
            )

        with trip_col_2:
            num_people = st.number_input(
                "Jumlah Orang",
                min_value=1,
                max_value=20,
                value=2,
                step=1,
            )

        travel_type_default = 0
        if "family" in travel_types:
            travel_type_default = travel_types.index("family")

        travel_type = st.selectbox(
            "Tipe Perjalanan",
            travel_types,
            index=travel_type_default,
        )

    with right_col:
        st.markdown("#### 🧭 Preferensi Wisata")

        default_categories = ["nature"] if "nature" in categories else categories[:1]
        preferred_categories = st.multiselect(
            "Kategori Wisata",
            categories,
            default=default_categories,
        )

        default_sub_categories = ["beach"] if "beach" in sub_categories else sub_categories[:1]
        preferred_sub_categories = st.multiselect(
            "Sub-Kategori Wisata",
            sub_categories,
            default=default_sub_categories,
        )

        preferred_locations = st.multiselect(
            "Lokasi yang Diinginkan",
            locations,
            default=["Badung"] if "Badung" in locations else locations[:1],
        )

        top_k = st.slider(
            "Jumlah Rekomendasi",
            min_value=1,
            max_value=max_recommendations,
            value=min(5, max_recommendations),
        )

    submitted = st.form_submit_button("Generate Travel Plan")

    st.markdown("</div>", unsafe_allow_html=True)


# RESULT

if submitted:
    if not preferred_categories:
        st.warning("Pilih minimal satu kategori wisata dulu.")
        st.stop()

    if not preferred_locations:
        st.warning("Pilih minimal satu lokasi dulu.")
        st.stop()

    request_payload = {
        "total_budget": int(total_budget),
        "duration_days": int(duration_days),
        "num_people": int(num_people),
        "travel_type": travel_type,
        "preferred_categories": preferred_categories,
        "preferred_sub_categories": preferred_sub_categories,
        "preferred_locations": preferred_locations,
        "top_k": int(top_k),
    }

    with st.spinner("Sedang membuat rekomendasi terbaik untuk perjalanan kamu..."):
        try:
            result = request_trip_plan(request_payload)
            st.session_state.trip_result = result
            st.session_state.last_payload = request_payload
        except requests.RequestException as exc:
            st.error(f"Gagal membuat rencana perjalanan: {exc}")
            st.stop()
            
if st.session_state.trip_result is not None:
    result = st.session_state.trip_result

    budget = result.get("budget", {})
    allocation = result.get("budget_allocation", {})
    recommendations = result.get("recommended_destinations", [])
    warnings = result.get("warnings", [])

    st.markdown(
        """
        <div class="result-header">
            <h2>Hasil Rekomendasi Perjalanan</h2>
            <p>Rekomendasi disusun berdasarkan input budget, lokasi, kategori, dan skor kecocokan destinasi.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # BUDGET SUMMARY

    st.markdown('<div class="section-title">Ringkasan Budget</div>', unsafe_allow_html=True)

    metric_cols = st.columns(4)

    metric_cols[0].metric(
        "Total Budget",
        format_idr(budget.get("total_budget", total_budget)),
    )

    metric_cols[1].metric(
        "Budget Tier",
        str(budget.get("tier", "-")).title(),
    )

    metric_cols[2].metric(
        "Per Orang / Hari",
        format_idr(budget.get("budget_per_person_per_day", 0)),
    )

    metric_cols[3].metric(
        "Destinasi",
        len(recommendations),
    )

    # BUDGET ALLOCATION
  
    st.markdown('<div class="section-title">Alokasi Budget</div>', unsafe_allow_html=True)
    allocation_items = allocation.get("items", [])

    if allocation_items:
        allocation_df = pd.DataFrame(allocation_items)

        col_table, col_chart = st.columns([1, 1.1], gap="large")

        with col_table:
            render_allocation_table(allocation_df)

        with col_chart:
            fig = px.pie(
                allocation_df,
                names="component",
                values="amount",
                hole=0.55,
            )
            fig.update_traces(
                textposition="inside",
                textinfo="percent+label",
            )
            fig.update_layout(
                margin=dict(t=10, b=10, l=10, r=10),
                height=360,
                showlegend=False,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Data alokasi budget belum tersedia dari backend.")

    # ========================================================
    # DESTINATION CARDS
    # ========================================================
    st.markdown('<div class="section-title">Destinasi yang Direkomendasikan</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">Default-nya mengikuti ranking dari backend. Kamu juga bisa mengurutkan ulang tampilan dari frontend.</div>',
        unsafe_allow_html=True,
    )

    # ========================================================
    # SORT CONTROL
    # ========================================================
    sorted_recommendations = recommendations

    if recommendations:
        sort_by = st.selectbox(
            "Urutkan rekomendasi berdasarkan",
            [
                "Rekomendasi Terbaik",
                "Rating Tertinggi",
                "Review Terbanyak",
                "Harga Termurah",
                "Harga Termahal",
                "Score Tertinggi",
            ],
            key="sort_by",
        )

        if sort_by == "Rekomendasi Terbaik":
            # Urutan asli dari backend/recommender
            sorted_recommendations = recommendations

        elif sort_by == "Rating Tertinggi":
            sorted_recommendations = sorted(
                recommendations,
                key=lambda x: get_sort_value(x, ["rating"], 0),
                reverse=True,
            )

        elif sort_by == "Review Terbanyak":
            sorted_recommendations = sorted(
                recommendations,
                key=lambda x: get_sort_value(x, ["review_count", "jumlah_review", "jumlah_rating"], 0),
                reverse=True,
            )

        elif sort_by == "Harga Termurah":
            sorted_recommendations = sorted(
                recommendations,
                key=lambda x: get_sort_value(
                    x,
                    [
                        "estimated_ticket_price",
                        "estimated_price",
                        "price",
                        "ticket_price",
                        "harga_tiket",
                        "harga_destinasi",
                    ],
                    0,
                ),
                reverse=False,
            )

        elif sort_by == "Harga Termahal":
            sorted_recommendations = sorted(
                recommendations,
                key=lambda x: get_sort_value(
                    x,
                    [
                        "estimated_ticket_price",
                        "estimated_price",
                        "price",
                        "ticket_price",
                        "harga_tiket",
                        "harga_destinasi",
                    ],
                    0,
                ),
                reverse=True,
            )

        elif sort_by == "Score Tertinggi":
            sorted_recommendations = sorted(
                recommendations,
                key=lambda x: get_sort_value(x, ["score", "final_score", "recommendation_score"], 0),
                reverse=True,
            )

    if sorted_recommendations:
        # Prefetch foto & deskripsi secara paralel agar cache hangat sebelum
        # render. Tanpa ini tiap card memanggil API berurutan dan halaman
        # terasa menggantung.
        prefetch_names = [
            safe_get(
                dest,
                "name",
                "nama_destinasi",
                "nama_tempat_wisata",
                default=f"Destination {i}",
            )
            for i, dest in enumerate(sorted_recommendations, start=1)
        ]
        with st.spinner("Menyiapkan foto & deskripsi destinasi..."):
            prefetch_enrichment(prefetch_names)

        for idx, destination in enumerate(sorted_recommendations, start=1):
            name = safe_get(
                destination,
                "name",
                "nama_destinasi",
                "nama_tempat_wisata",
                default=f"Destination {idx}",
            )

            district = safe_get(destination, "district", "kecamatan", default="-")

            regency_city = safe_get(
                destination,
                "regency_city",
                "kabupaten_kota",
                "city",
                "location",
                default="-",
            )

            address = build_address(destination)

            category = safe_get(
                destination,
                "category",
                "category_main",
                "kategori",
                default="-",
            )

            sub_category = safe_get(
                destination,
                "sub_category",
                "sub_kategori",
                default="-",
            )

            description = safe_get(
                destination,
                "description",
                "deskripsi",
                "content_text",
                default="",
            )

            rating = safe_get(destination, "rating", default="-")

            review_count = safe_get(
                destination,
                "review_count",
                "jumlah_review",
                "jumlah_rating",
                default="-",
            )

            price = safe_get(
                destination,
                "estimated_ticket_price",
                "estimated_price",
                "price",
                "ticket_price",
                "harga_tiket",
                "harga_destinasi",
                default=0,
            )

            score = safe_get(destination, "score", "final_score", "recommendation_score", default="-")

            maps_url = safe_get(
                destination,
                "maps_url",
                "link_google_maps",
                "google_maps_url",
                default="",
            )

            image_url = safe_get(
                destination,
                "image_url",
                "foto_url",
                "link_gambar",
                "image",
                "thumbnail",
                default="",
            )

            match_reasons = destination.get("match_reasons", [])
            if not isinstance(match_reasons, list):
                match_reasons = []

            with st.container(border=True):
                # ---- GALLERY (gambar utama + thumbnail 2x2 + overlay +N) ----
                gallery_urls = get_google_place_photos(name, limit=5)
                if not gallery_urls and is_valid_image_url(image_url):
                    if is_image_url_reachable(image_url):
                        gallery_urls = [image_url]

                render_detail_gallery(name, idx, gallery_urls)

                # Klik tombol -> modal carousel foto besar (bisa digeser).
                if gallery_urls:
                    if st.button(
                        "Lihat semua foto",
                        key=f"open_gallery_{idx}",
                        icon=":material/photo_library:",
                        use_container_width=True,
                    ):
                        open_gallery_modal(name, gallery_urls)

                # ---- DESKRIPSI: diprioritaskan dari Wikipedia ----
                wiki_data = get_wikipedia_description(name)
                wiki_source_url = wiki_data.get("source_url")
                from_dataset = bool(description and description != "-")
                wiki_is_real = str(wiki_data.get("source", "")).startswith("Wikipedia")
                if wiki_is_real:
                    desc_text = wiki_data["description"]
                    show_source = True
                elif from_dataset:
                    desc_text = description
                    show_source = False
                else:
                    desc_text = wiki_data["description"]
                    show_source = False

                # ---- INFO UTAMA (judul, lokasi, score, pills, mini info) ----
                pills = ""
                for value, cls in [
                    (category, "dc-pill"),
                    (sub_category, "dc-pill"),
                    (district, "dc-pill alt"),
                    (regency_city, "dc-pill alt"),
                ]:
                    if value and value != "-":
                        pills += f"<span class='{cls}'>{html_lib.escape(str(value))}</span>"

                info_html = (
                    "<div class='dc-head'>"
                    "<div>"
                    f"<div class='dc-title'><span class='dc-rank'>#{idx}</span>"
                    f"{html_lib.escape(str(name))}</div>"
                    f"<div class='dc-location'>"
                    "<svg width='15' height='15' viewBox='0 0 24 24' fill='#5eead4' "
                    "style='vertical-align:-2px;margin-right:5px;'>"
                    "<path d='M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13"
                    "c0-3.87-3.13-7-7-7zm0 9.5a2.5 2.5 0 110-5 2.5 2.5 0 010 5z'/>"
                    f"</svg>{html_lib.escape(str(address))}</div>"
                    "</div>"
                    "<div class='dc-score'>"
                    "<div class='dc-score-label'>Score</div>"
                    f"<div class='dc-score-value'>{format_score(score)}</div>"
                    "</div>"
                    "</div>"
                    f"<div class='dc-pills'>{pills}</div>"
                    "<div class='dc-info-grid'>"
                    "<div class='dc-info'><div class='dc-info-label'>Rating</div>"
                    f"<div class='dc-info-value'>★ {format_rating(rating)}</div></div>"
                    "<div class='dc-info'><div class='dc-info-label'>Review</div>"
                    f"<div class='dc-info-value'>{html_lib.escape(str(review_count))}</div></div>"
                    "<div class='dc-info'><div class='dc-info-label'>Harga Tiket</div>"
                    f"<div class='dc-info-value'>{format_idr(price)}</div></div>"
                    "</div>"
                )
                st.markdown(info_html, unsafe_allow_html=True)

                # ---- DESKRIPSI (clamp 4 baris + read more, pure CSS) ----
                esc_desc = html_lib.escape(str(desc_text))
                source_html = ""
                if show_source:
                    source_html = (
                        f"<div class='dc-desc-source'>Sumber: "
                        f"{html_lib.escape(wiki_data['source'])}</div>"
                    )

                st.markdown(
                    "<div class='dc-section-head'>Deskripsi</div>", unsafe_allow_html=True
                )
                if len(str(desc_text)) > 200:
                    st.markdown(
                        "<div class='dc-desc'><details>"
                        f"<summary><div class='dc-desc-clamp'>{esc_desc}</div>"
                        "<span class='dc-readmore'></span></summary>"
                        f"<div class='dc-desc-full'>{esc_desc}</div></details>"
                        f"{source_html}</div>",
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        "<div class='dc-desc'>"
                        f"<div class='dc-desc-full' style='display:block;'>{esc_desc}</div>"
                        f"{source_html}</div>",
                        unsafe_allow_html=True,
                    )

                # ---- LOKASI (embed map + tombol) ----
                st.markdown(
                    "<div class='dc-section-head'>Lokasi</div>", unsafe_allow_html=True
                )
                render_location_map(name, maps_url)

                has_maps = bool(maps_url and maps_url != "-")
                btn_maps_url = (
                    maps_url
                    if has_maps
                    else f"https://www.google.com/maps/search/?api=1&query={quote_plus(name + ' Bali')}"
                )
                action_cols = st.columns(2)
                with action_cols[0]:
                    st.link_button(
                        "Buka Google Maps",
                        btn_maps_url,
                        icon=":material/map:",
                        use_container_width=True,
                    )
                with action_cols[1]:
                    if wiki_source_url:
                        st.link_button(
                            "Lihat di Wikipedia",
                            wiki_source_url,
                            icon=":material/menu_book:",
                            use_container_width=True,
                        )

        # ====================================================
        # TABLE
        # ====================================================
        with st.expander("Lihat tabel data rekomendasi"):
            recommendations_df = pd.DataFrame(sorted_recommendations)
            st.dataframe(
                recommendations_df,
                use_container_width=True,
                hide_index=True,
            )

    else:
        st.warning("Belum ada destinasi yang direkomendasikan.")

    if warnings:
        st.warning("\n".join(warnings))
