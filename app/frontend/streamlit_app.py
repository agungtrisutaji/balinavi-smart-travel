import os

import plotly.express as px
import requests
import streamlit as st


BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


def fetch_metadata() -> dict:
    response = requests.get(f"https://balinavi-smart-travel-1.onrender.com/metadata", timeout=10)
    response.raise_for_status()
    return response.json()


def request_trip_plan(payload: dict) -> dict:
    response = requests.post(f"https://balinavi-smart-travel-1.onrender.com/plan-trip", json=payload, timeout=20)
    response.raise_for_status()
    return response.json()


st.set_page_config(page_title="BaliNavi", layout="wide")
st.title("BaliNavi")

try:
    metadata = fetch_metadata()
except requests.RequestException as exc:
    st.error(f"Backend is not reachable: {exc}")
    st.stop()

with st.form("trip_plan_form"):
    col_budget, col_trip = st.columns(2)
    with col_budget:
        total_budget = st.number_input(
            "Total budget (IDR)",
            min_value=1,
            value=5_000_000,
            step=100_000,
        )
        duration_days = st.number_input(
            "Duration (days)",
            min_value=1,
            max_value=30,
            value=3,
            step=1,
        )
        num_people = st.number_input(
            "Number of people",
            min_value=1,
            max_value=20,
            value=2,
            step=1,
        )
    with col_trip:
        travel_type = st.selectbox("Travel type", metadata["travel_types"], index=2)
        preferred_categories = st.multiselect(
            "Preferred categories",
            metadata["categories"],
            default=["nature"],
        )
        preferred_sub_categories = st.multiselect(
            "Preferred sub-categories",
            metadata["sub_categories"],
            default=["beach"],
        )
        preferred_locations = st.multiselect(
            "Preferred locations",
            ["Badung", "Gianyar", "Denpasar", "Karangasem", "Tabanan"],
            default=["Badung"],
        )
        top_k = st.slider(
            "Recommendations",
            min_value=1,
            max_value=metadata["max_recommendations"],
            value=5,
        )

    submitted = st.form_submit_button("Plan Trip")

if submitted:
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

    try:
        result = request_trip_plan(request_payload)
    except requests.RequestException as exc:
        st.error(f"Failed to generate trip plan: {exc}")
        st.stop()

    budget = result["budget"]
    allocation = result["budget_allocation"]
    recommendations = result["recommended_destinations"]

    st.subheader("Budget")
    budget_cols = st.columns(3)
    budget_cols[0].metric("Tier", budget["tier"].title())
    budget_cols[1].metric(
        "Per person per day",
        f"IDR {budget['budget_per_person_per_day']:,}",
    )
    budget_cols[2].metric("Total budget", f"IDR {budget['total_budget']:,}")

    st.subheader("Budget Allocation")
    st.dataframe(allocation["items"], use_container_width=True)
    fig = px.bar(
        allocation["items"],
        x="component",
        y="amount",
        text="percentage",
        labels={"component": "Component", "amount": "Amount (IDR)"},
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Recommended Destinations")
    st.dataframe(recommendations, use_container_width=True)

    if result["warnings"]:
        st.warning("\n".join(result["warnings"]))
