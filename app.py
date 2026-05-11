"""Nigeria Disease Surveillance System — Streamlit Dashboard"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import folium
from streamlit_folium import st_folium
import sys, os

sys.path.insert(0, os.path.dirname(__file__))
from data.generate_data import generate_disease_cases, generate_vector_habitats, DISEASES
from gis.spatial_analysis import build_disease_map

st.set_page_config(page_title="NG Disease Surveillance", page_icon="🦟", layout="wide")
st.markdown("""<style>
.kpi{background:#880e4f;color:white;padding:14px;border-radius:8px;text-align:center;}
.kpi-val{font-size:1.9rem;font-weight:700;}
.kpi-lbl{font-size:.8rem;opacity:.85;}
.alert-red{background:#d32f2f;color:white;padding:6px 12px;border-radius:6px;font-weight:bold;}
</style>""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    cases = generate_disease_cases(104)
    habitats = generate_vector_habitats()
    cases["week_start"] = pd.to_datetime(cases["week_start"])
    return cases, habitats


def main():
    cases_df, habitats_df = load_data()

    with st.sidebar:
        st.title("🦟 Disease Surveillance")
        st.caption("Nigeria Epidemic Tracker")
        st.divider()
        selected_disease = st.selectbox("Disease", DISEASES[:5])
        zone_filter = st.multiselect("Zone", cases_df["zone"].unique().tolist(),
                                     default=cases_df["zone"].unique().tolist())
        date_range = st.date_input("Date Range",
                                    value=[cases_df["week_start"].min().date(),
                                           cases_df["week_start"].max().date()])
        st.divider()
        st.markdown("**NCDC Alert System**")
        st.error("Malaria — Kano (RED ALERT)")
        st.warning("Cholera — Rivers (WATCH)")
        st.success("Lassa Fever — Nationwide (NORMAL)")

    disease_df = cases_df[
        (cases_df["disease"] == selected_disease) &
        cases_df["zone"].isin(zone_filter) &
        (cases_df["week_start"].dt.date >= date_range[0]) &
        (cases_df["week_start"].dt.date <= date_range[1])
    ]

    st.title("🦟 Nigeria Disease Surveillance & Epidemic Tracker")
    st.caption("Real-time case tracking · Hotspot analysis · Vector mapping · GIS + PySpark + Azure Health Data")
    st.divider()

    c1, c2, c3, c4 = st.columns(4)
    total_cases = disease_df["cases"].sum()
    total_deaths = disease_df["deaths"].sum()
    avg_incidence = disease_df["incidence_per_100k"].mean()
    outbreak_states = len(disease_df[disease_df["incidence_per_100k"] > 100]["state"].unique())
    for col, val, lbl in zip(
        [c1, c2, c3, c4],
        [f"{total_cases:,}", f"{total_deaths:,}", f"{avg_incidence:.1f}", outbreak_states],
        [f"Total {selected_disease} Cases", "Total Deaths", "Avg Incidence/100k", "Alert States"]
    ):
        col.markdown(f'<div class="kpi"><div class="kpi-val">{val}</div>'
                     f'<div class="kpi-lbl">{lbl}</div></div>', unsafe_allow_html=True)

    st.divider()
    col_map, col_chart = st.columns([3, 2])

    with col_map:
        st.subheader(f"🗺 {selected_disease} Hotspot Map")
        m = build_disease_map(disease_df, habitats_df, selected_disease)
        st_folium(m, width=700, height=460)

    with col_chart:
        st.subheader("📊 Cases by State")
        state_cases = disease_df.groupby("state")["cases"].sum().sort_values().tail(15).reset_index()
        fig = px.bar(state_cases, x="cases", y="state", orientation="h",
                     color="cases", color_continuous_scale="Reds",
                     labels={"cases": "Total Cases", "state": ""}, height=460)
        fig.update_layout(coloraxis_showscale=False,
                          plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                          margin=dict(l=0, r=10, t=5, b=10))
        st.plotly_chart(fig, use_container_width=True)

    st.divider()
    col_trend, col_season = st.columns(2)

    with col_trend:
        st.subheader("📈 Epidemic Curve")
        weekly = disease_df.groupby("week_start")["cases"].sum().reset_index()
        fig_t = px.line(weekly, x="week_start", y="cases",
                        color_discrete_sequence=["#c62828"],
                        labels={"week_start": "Week", "cases": "Cases"})
        fig_t.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                            margin=dict(l=0, r=0, t=5, b=0))
        st.plotly_chart(fig_t, use_container_width=True)

    with col_season:
        st.subheader("📅 Seasonal Pattern")
        disease_df_copy = disease_df.copy()
        disease_df_copy["month"] = disease_df_copy["week_start"].dt.month
        monthly = disease_df_copy.groupby("month")["cases"].mean().reset_index()
        fig_s = px.bar(monthly, x="month", y="cases",
                       color="cases", color_continuous_scale="Reds",
                       labels={"month": "Month", "cases": "Avg Weekly Cases"})
        fig_s.update_layout(coloraxis_showscale=False,
                            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                            margin=dict(l=0, r=0, t=5, b=0))
        st.plotly_chart(fig_s, use_container_width=True)

    st.divider()
    st.subheader("🦟 Vector Habitat & Intervention Coverage")
    fig_v = px.scatter(habitats_df, x="anopheles_density_index", y="itn_coverage_pct",
                       color="malaria_risk", size="water_body_coverage_pct",
                       hover_name="state", size_max=30,
                       color_discrete_map={"Very High": "#b71c1c", "High": "#e53935",
                                           "Moderate": "#f57c00", "Low": "#388e3c"},
                       labels={"anopheles_density_index": "Vector Density",
                               "itn_coverage_pct": "ITN Coverage (%)"})
    fig_v.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_v, use_container_width=True)

    st.caption("Data: Synthetic — replace with NCDC IDSR, WHO EWARN, NMEP malaria survey. "
               "Pipeline: Azure Databricks PySpark. Storage: Azure Health Data Services.")


if __name__ == "__main__":
    main()
