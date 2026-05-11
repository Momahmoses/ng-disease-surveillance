import pandas as pd
import numpy as np
import os

STATES = [
    ("Lagos", 6.5244, 3.3792, "SW", 15388000, "Low"),
    ("Kano", 12.0022, 8.5920, "NW", 13076000, "High"),
    ("Kaduna", 10.5222, 7.4383, "NW", 8252000, "High"),
    ("Rivers", 4.8156, 7.0498, "SS", 7303000, "High"),
    ("Oyo", 7.3775, 3.9470, "SW", 7840000, "Moderate"),
    ("Abuja FCT", 9.0765, 7.3986, "NC", 3564000, "Low"),
    ("Anambra", 6.2104, 6.9623, "SE", 5527000, "Moderate"),
    ("Borno", 11.8846, 13.1571, "NE", 5860000, "Very High"),
    ("Imo", 5.4527, 7.0201, "SE", 4856000, "Moderate"),
    ("Delta", 5.5320, 5.8987, "SS", 5663000, "High"),
    ("Adamawa", 9.3265, 12.3984, "NE", 4253000, "High"),
    ("Plateau", 9.2182, 9.5179, "NC", 4200000, "Moderate"),
    ("Bauchi", 10.3158, 9.8442, "NE", 6537000, "High"),
    ("Sokoto", 13.0059, 5.2476, "NW", 4998000, "Very High"),
    ("Kebbi", 11.4943, 4.2333, "NW", 4459000, "High"),
    ("Niger", 10.0008, 5.5981, "NC", 5559000, "Moderate"),
    ("Kwara", 8.9669, 4.3873, "NC", 3194000, "Moderate"),
    ("Nassarawa", 8.4994, 8.1997, "NC", 2523000, "Moderate"),
    ("Benue", 7.3369, 8.7404, "NC", 5741000, "High"),
    ("Taraba", 7.9993, 10.7741, "NE", 3066000, "High"),
    ("Yobe", 12.2939, 11.4390, "NE", 3294000, "Very High"),
    ("Gombe", 10.2791, 11.1673, "NE", 3256000, "High"),
    ("Ebonyi", 6.2649, 8.0137, "SE", 2880000, "Moderate"),
    ("Cross River", 5.9631, 8.3305, "SS", 4059000, "Moderate"),
    ("Akwa Ibom", 5.0527, 7.9335, "SS", 5450000, "Moderate"),
    ("Enugu", 6.4584, 7.5464, "SE", 4411000, "Low"),
    ("Abia", 5.3671, 7.4948, "SE", 3728000, "Moderate"),
    ("Katsina", 12.9908, 7.6018, "NW", 8036000, "Very High"),
    ("Jigawa", 12.2280, 9.5616, "NW", 5829000, "High"),
    ("Zamfara", 12.1222, 6.2236, "NW", 4515000, "Very High"),
    ("Ogun", 6.9980, 3.4737, "SW", 5217000, "Low"),
    ("Edo", 6.3350, 5.6037, "SS", 4737000, "Moderate"),
    ("Bayelsa", 4.7719, 6.0699, "SS", 2278000, "High"),
    ("Ondo", 7.0003, 5.0000, "SW", 4671000, "Moderate"),
    ("Osun", 7.5629, 4.5624, "SW", 4705000, "Moderate"),
    ("Ekiti", 7.6218, 5.2311, "SW", 3270000, "Low"),
    ("Kebbi", 11.4943, 4.2333, "NW", 4459000, "High"),
]

DISEASES = ["Malaria", "Cholera", "Lassa Fever", "Meningitis",
            "Monkey Pox", "Yellow Fever", "Typhoid", "Measles", "COVID-19"]

MALARIA_RISK = {"Very High": (0.75, 0.95), "High": (0.55, 0.74),
                "Moderate": (0.35, 0.54), "Low": (0.10, 0.34)}


def generate_disease_cases(n_weeks: int = 156) -> pd.DataFrame:
    np.random.seed(42)
    records = []
    start_date = pd.Timestamp("2021-01-01")
    for state, slat, slon, zone, pop, risk_level in STATES[:30]:
        lo, hi = MALARIA_RISK[risk_level]
        for week in range(n_weeks):
            dt = start_date + pd.Timedelta(weeks=week)
            month = dt.month
            is_peak = 5 <= month <= 10
            for disease in DISEASES[:5]:
                base = {"Malaria": (500 if is_peak else 100) * (hi - lo + 0.2),
                        "Cholera": 30 if month in [4, 5, 10, 11] else 5,
                        "Lassa Fever": 8 if state in ("Edo", "Imo", "Rivers", "Bauchi") else 1,
                        "Meningitis": 20 if (zone in ("NW", "NE") and month in [12, 1, 2, 3]) else 2,
                        "Monkey Pox": 5 if state in ("Rivers", "Bayelsa", "Delta") else 1}[disease]
                cases = max(0, int(np.random.poisson(base)))
                deaths = int(np.random.binomial(cases, 0.02))
                records.append({
                    "week_start": dt, "state": state, "zone": zone,
                    "lat": slat + np.random.uniform(-0.1, 0.1),
                    "lon": slon + np.random.uniform(-0.1, 0.1),
                    "disease": disease, "risk_level": risk_level,
                    "cases": cases, "deaths": deaths,
                    "population": pop,
                    "incidence_per_100k": round(cases / pop * 100000, 2),
                    "cfr_pct": round(deaths / max(1, cases) * 100, 2),
                })
    return pd.DataFrame(records)


def generate_vector_habitats() -> pd.DataFrame:
    np.random.seed(42)
    records = []
    for state, slat, slon, zone, pop, risk in STATES[:25]:
        records.append({
            "state": state, "lat": slat, "lon": slon,
            "anopheles_density_index": round(np.random.uniform(0.2, 0.95), 3),
            "water_body_coverage_pct": round(np.random.uniform(2, 45), 1),
            "itn_coverage_pct": round(np.random.uniform(20, 85), 1),
            "irs_coverage_pct": round(np.random.uniform(10, 70), 1),
            "malaria_risk": risk,
        })
    return pd.DataFrame(records)


def save_all(output_dir: str = "data"):
    os.makedirs(output_dir, exist_ok=True)
    generate_disease_cases(104).to_csv(f"{output_dir}/disease_cases.csv", index=False)
    generate_vector_habitats().to_csv(f"{output_dir}/vector_habitats.csv", index=False)
    print("Disease surveillance data generated.")


if __name__ == "__main__":
    save_all()
