[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/deploy?repository=Momahmoses%2Fng-disease-surveillance&branch=main&mainModule=app.py)

# 🦟 Nigeria Disease Surveillance & Epidemic Tracker

Real-time epidemic surveillance platform for Nigeria tracking malaria, cholera, Lassa fever, meningitis, and monkeypox using **GIS hotspot analysis**, **PySpark rolling case windows**, **Azure Health Data Services**, and **Streamlit**.

## Problem Statement
Nigeria accounts for 27% of global malaria deaths. Cholera outbreaks occur seasonally in flood-affected states. Lassa fever is endemic in the forest zone. This platform helps NCDC, WHO, and state epidemiologists detect outbreaks early and prioritize interventions.

## Quick Start
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Data Sources (Production)
- **NCDC IDSR** — Integrated Disease Surveillance and Response
- **WHO EWARN** — Early Warning Alert and Response Network
- **NMEP** — National Malaria Elimination Programme
- **FMOH** — Federal Ministry of Health weekly bulletins
