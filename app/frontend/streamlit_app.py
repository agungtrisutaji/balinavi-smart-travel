import os
from typing import Any, Dict

import pandas as pd
import plotly.express as px
import requests
import streamlit as st



# CONFIGURATION BACKEND URL
BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "https://balinavi-smart-travel.onrender.com"
)

st.set_page_config(
    page_title="BaliNavi Smart Travel",
    page_icon="🌴",
    layout="wide",
    initial_sidebar_state="expanded",
)

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
        """
        <div style="
            height: 210px;
            width: 100%;
            border-radius: 18px;
            background: linear-gradient(135deg, rgba(20,184,166,0.22), rgba(245,158,11,0.18));
            border: 1px solid rgba(148,163,184,0.25);
            display: flex;
            align-items: center;
            justify-content: center;
            color: #e2e8f0;
            font-weight: 900;
            text-align: center;
            box-shadow: inset 0 0 40px rgba(2,6,23,0.25);
        ">
            🌴<br>Gambar tidak tersedia
        </div>
        """,
        unsafe_allow_html=True,
    )

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
            display_allocation = allocation_df.copy()

            if "amount" in display_allocation.columns:
                display_allocation["amount"] = display_allocation["amount"].apply(format_idr)

            st.dataframe(
                display_allocation,
                use_container_width=True,
                hide_index=True,
            )

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
                image_col, content_col = st.columns([1.15, 3], gap="large")

                with image_col:
                    if is_valid_image_url(image_url):
                        try:
                            st.image(image_url, use_container_width=True)
                        except Exception:
                            render_image_placeholder()
                    else:
                        render_image_placeholder()

                with content_col:
                    top_left, top_right = st.columns([4, 1])

                    with top_left:
                        st.markdown(f"### #{idx} {name}")
                        st.caption(f"📍 {address}")

                    with top_right:
                        st.metric("Score", format_score(score))

                    st.markdown(f"**Kategori:** `{category}`  `{sub_category}`  `{district}`  `{regency_city}`")

                    if description and description != "-":
                        st.markdown(f"📝 {description}")

                    stat_col1, stat_col2, stat_col3 = st.columns(3)
                    stat_col1.metric("Rating", f"⭐ {format_rating(rating)}")
                    stat_col2.metric("Review", review_count)
                    stat_col3.metric("Harga Tiket", format_idr(price))

                    if maps_url and maps_url != "-":
                        st.link_button("Buka Google Maps", maps_url)

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