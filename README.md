# Ghana ANC Fertility Spatial Analysis — Part II

**"Temporal and Spatial Dynamics of Antenatal Care Coverage and Fertility Inequities in Ghana: A Subnational Ecological Study Using Ghana Demographic and Health Surveys"**

> V. Ghanem | Part II of a longitudinal series on subnational maternal health inequity in Ghana

---

## Overview

This repository contains the full reproducible analysis pipeline and interactive dashboard for a 34-year (1988–2022) longitudinal spatial analysis of skilled antenatal care (ANC) coverage and total fertility rate (TFR) across all 16 administrative regions of Ghana.

**Key findings:**
- National ANC coverage rose from 83.1% (1988) to 97.7% (2022); inter-regional Gini coefficient fell 87.5%
- TFR spatial clustering intensified by 2022 (Moran's I = 0.570, p<0.001) while ANC clustering dissipated — a significant decoupling
- A critical TFR threshold of **5.90** (Random Forest partial dependence analysis) marks a sharp ANC coverage drop
- The novel **Care Efficiency Index (CEI = ANC% / TFR)** reveals a 2.2-fold performance gap between Greater Accra (CEI=30.8) and North East (CEI=14.3) despite coverage convergence
- Northern Belt remains a persistent spatial cluster of both high TFR and, historically, low ANC

---

## Repository Structure

```
ghana-anc-spatial/
├── README.md
├── LICENSE # MIT
├── requirements.txt # Python dependencies
├── .gitignore
│
├── analysis/
│ ├── analysis_pipeline.py # Full analytical pipeline (all steps)
│ ├── create_choropleths.py # Choropleth map generation
│ └── fix_figures_legibility.py # Figure legibility fixes (Figs 2,7,8,12)
│
├── dashboard/
│ └── ANC_Fertility_Dashboard_Ghana.html # Self-contained interactive dashboard
│
├── poster/
│ └── ANC_Fertility_Poster_Ghana.html # A0 conference poster (print-ready)
│
└── outputs/
 ├── *.csv # Analysis outputs (tables)
 └── figures/
 └── 06_figure_*.png # All 12 manuscript figures + supplementary
```

---

## Quick Start

### 1. Clone and install dependencies

```bash
git clone https://github.com/YOUR_USERNAME/ghana-anc-spatial.git
cd ghana-anc-spatial
pip install -r requirements.txt
```

### 2. Obtain DHS data

Register at [dhsprogram.com](https://dhsprogram.com) and download Ghana DHS subnational datasets for survey years: 1988, 1993, 1998, 2003, 2008, 2014, 2016, 2019, 2022.

Place raw data files in `data/raw/`. The pipeline expects a cleaned master panel CSV — see `analysis/analysis_pipeline.py` for the expected column schema.

### 3. Run the analysis pipeline

```bash
cd analysis
python analysis_pipeline.py
```

This generates all CSV outputs in `outputs/` and all PNG figures in `outputs/figures/`.

### 4. View the interactive dashboard

Open `dashboard/ANC_Fertility_Dashboard_Ghana.html` directly in any modern web browser — no server required. The dashboard is fully self-contained (data embedded as JavaScript objects, Plotly.js CDN).

## Methods Summary

| Method | Tool | Purpose |
|---|---|---|
| Gini coefficient | Custom (scipy) | Inequality decomposition |
| Global Moran's I | esda / libpysal (KNN k=4) | Spatial autocorrelation |
| LISA | esda / libpysal (Rook contiguity) | Local cluster detection |
| Random Forest | scikit-learn (n=200, max_depth=6) | Predictive modelling |
| Decision Tree | scikit-learn | Benchmark comparator |
| Partial Dependence | scikit-learn / Friedman (2001) | Critical TFR threshold |
| Care Efficiency Index | Custom (ANC% / TFR) | Novel composite indicator |
| Risk Stratification | Custom (z-score quadrant) | Policy zone classification |
| Choropleth maps | GeoPandas + Plotly | Spatial visualisation |

---

## Interactive Dashboard Features

The dashboard (`dashboard/ANC_Fertility_Dashboard_Ghana.html`) includes:

- **12 interactive Plotly charts** with hover, zoom, and pan
- **Temporal choropleth animation** (1988–2022 ANC by region)
- **LISA cluster map** with discrete High-High / Low-Low / outlier classification
- **Risk Zone choropleth** (Critical / Emerging / Workhorse / Resilient)
- **Care Efficiency Index choropleth** with continuous colour scale
- **All 5 data tables** (regional disparities, spatial autocorrelation, ML performance, CEI, risk zones)
- Dark/light mode, section navigation, and print-optimised layout

---

## Citation

If you use this code or analysis, please cite:

> Ghanem V. Temporal and spatial dynamics of antenatal care coverage and fertility inequities in Ghana: a subnational ecological study using Ghana Demographic and Health Surveys. [Journal Name]. [Year]. doi: [DOI]

And the Part I companion paper:

> Ghanem V. Spatial and machine learning analysis of district-level health insurance non-enrolment and antenatal care underutilisation in Ghana. [Journal Name]. [Year].

---

## Data Availability

- **Ghana DHS subnational data**: Available from [dhsprogram.com](https://dhsprogram.com) (free registration)
- **Ghana administrative boundaries**: Available from GADM ([gadm.org](https://gadm.org))
- **Analysis outputs**: Included in this repository under `outputs/`

---

## Reporting Standards

This ecological study was reported following the **STROBE guidelines for observational studies** (Strengthening the Reporting of Observational Studies in Epidemiology).

---

## Contact

Valentine Ghanem | valentineghanem@gmail.com
