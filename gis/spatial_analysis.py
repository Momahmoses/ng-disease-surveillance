"""GIS: Disease hotspot analysis, vector habitat mapping, epidemic spread visualization."""
import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import Point
import folium
from folium.plugins import HeatMap
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from data.generate_data import generate_disease_cases, generate_vector_habitats


RISK_COLORS = {"Very High": "#b71c1c", "High": "#e53935",
               "Moderate": "#f57c00", "Low": "#388e3c"}


def build_disease_map(cases_df: pd.DataFrame, habitats_df: pd.DataFrame,
                       selected_disease: str = "Malaria") -> folium.Map:
    m = folium.Map(location=[9.08, 8.67], zoom_start=6, tiles="CartoDB positron")

    disease_cases = cases_df[cases_df["disease"] == selected_disease]
    state_totals = disease_cases.groupby(["state", "lat", "lon", "risk_level"])["cases"].sum().reset_index()

    heat = [[r.lat, r.lon, min(1.0, r.cases / state_totals["cases"].max())]
            for _, r in state_totals.iterrows()]
    HeatMap(heat, radius=22, blur=18, min_opacity=0.35).add_to(m)

    for _, row in state_totals.iterrows():
        color = RISK_COLORS.get(row.get("risk_level", "Low"), "#388e3c")
        folium.CircleMarker(
            location=[row.lat, row.lon],
            radius=max(6, min(30, row["cases"] / state_totals["cases"].max() * 30)),
            color=color, fill=True, fill_opacity=0.7,
            popup=(f"<b>{row['state']}</b><br>{selected_disease}<br>"
                   f"Total Cases: {int(row['cases']):,}<br>Risk: {row.get('risk_level', 'N/A')}"),
            tooltip=row["state"],
        ).add_to(m)

    for _, h in habitats_df.iterrows():
        folium.CircleMarker(
            location=[h.lat, h.lon], radius=3,
            color="#1565c0", fill=True, fill_opacity=0.5,
            popup=f"<b>{h['state']}</b><br>Vector Density: {h['anopheles_density_index']:.2f}<br>ITN Coverage: {h['itn_coverage_pct']}%",
        ).add_to(m)
    return m


if __name__ == "__main__":
    cases = generate_disease_cases(52)
    habitats = generate_vector_habitats()
    m = build_disease_map(cases, habitats)
    os.makedirs("app", exist_ok=True)
    m.save("app/disease_map.html")
    print("Map saved.")
