# Temporal and Spatial Dynamics of Antenatal Care Coverage and Fertility Inequities in Ghana: A Subnational Ecological Study Using Ghana Demographic and Health Surveys

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE) [![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/) [![ORCID](https://img.shields.io/badge/ORCID-0009--0002--8332--0220-green.svg)](https://orcid.org/0009-0002-8332-0220)

**Author:** Valentine Golden Ghanem | Ghana COCOBOD Cocoa Clinic, Accra, Ghana
**ORCID:** [0009-0002-8332-0220](https://orcid.org/0009-0002-8332-0220)
**Reporting standard:** STROBE
**Date:** 2026
**Status:** Part II of a longitudinal series on subnational maternal health inequity in Ghana

> Ghanem VG. *Temporal and spatial dynamics of antenatal care coverage and fertility inequities in Ghana: a subnational ecological study using Ghana Demographic and Health Surveys.* 2026.

---

## Overview

A 34-year (1988–2022) longitudinal spatial analysis of skilled antenatal care (ANC) coverage and total fertility rate (TFR) across all 16 administrative regions of Ghana, using nine DHS survey waves. The study introduces the Care Efficiency Index (CEI = ANC% / TFR) as a novel composite indicator to expose persistent regional inequities obscured by national coverage convergence. Spatial autocorrelation analysis reveals a significant ANC–TFR decoupling by 2022, with the Northern Belt remaining a persistent high-TFR, historically low-ANC spatial cluster.

---

## Key Findings

| Metric | Value |
|--------|-------|
| National ANC coverage | 83.1% (1988) → 97.7% (2022) |
| Inter-regional Gini reduction | 87.5% |
| TFR spatial clustering (2022) | Moran's I = 0.570 (p < 0.001) |
| ANC–TFR decoupling | ANC clustering dissipated; TFR clustering intensified |
| Critical TFR threshold | 5.90 (RF partial dependence) |
| CEI range | North East 14.3 → Greater Accra 30.8 (2.2× gap) |
| Persistent cluster | Northern Belt — high TFR / historically low ANC |

---

## Repository Structure

```
anc-fertility-ghana-inequities/
├── analysis/
│   ├── analysis_pipeline.py        # Full analytical pipeline (all steps)
│   ├── create_choropleths.py       # Choropleth map generation
│   └── fix_figures_legibility.py   # Figure legibility corrections
├── app.py                          # Plotly Dash interactive web application
├── analysis.R                      # R: mixed-effects models + Gini decomposition
├── dashboard/
│   └── ANC_Fertility_Dashboard_Ghana.html   # Self-contained HTML dashboard
├── poster/
│   └── ANC_Fertility_Poster_Ghana.html      # A0 conference poster (print-ready)
├── outputs/
│   ├── *.csv                       # Analysis output tables
│   └── figures/
│       └── 06_figure_*.png         # 12 manuscript figures + supplementary
├── requirements.txt
├── renv.lock
├── CITATION.cff
└── README.md
```

---

## Quick Start

### 1. Clone

```bash
git clone https://github.com/valentineghanem-bit/anc-fertility-ghana-inequities.git
cd anc-fertility-ghana-inequities
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the pipeline

```bash
cd analysis
python analysis_pipeline.py
```

### 4. Run tests

```bash
pytest tests/ -v
```

### 5. Open the interactive dashboard

```bash
python app.py
# Visit http://127.0.0.1:8050
```

Or open `dashboard/ANC_Fertility_Dashboard_Ghana.html` directly in any modern browser. No server required.

---

## Data Sources

| Source | Variables | Year | Access |
|--------|-----------|------|--------|
| Ghana DHS subnational | ANC coverage, TFR, regional indicators | 1988, 1993, 1998, 2003, 2008, 2014, 2016, 2019, 2022 | [dhsprogram.com](https://dhsprogram.com) (free registration) |
| Ghana administrative boundaries | Regional polygons | 2021 | [GADM](https://gadm.org) |

> DHS data accessed under registration. Raw microdata are not redistributed in compliance with DHS access policies.

---

## Methods Summary

| Method | Tool | Purpose |
|--------|------|---------|
| Gini coefficient | scipy | Inequality decomposition over time |
| Global Moran's I | esda / libpysal (KNN k=4) | ANC and TFR spatial autocorrelation |
| LISA | esda / libpysal (Rook contiguity) | Local cluster detection |
| Random Forest | scikit-learn (n=200) | ANC prediction; partial dependence |
| Decision Tree (CART) | scikit-learn | Benchmark comparator |
| Partial Dependence | scikit-learn | Critical TFR threshold identification |
| Care Efficiency Index | Custom (ANC% / TFR) | Novel composite performance indicator |
| Risk Stratification | Custom (z-score quadrant) | Policy zone classification |
| Mixed-effects models | lme4 (R) | Regional longitudinal trend decomposition |
| Choropleth maps | GeoPandas + Plotly | Temporal spatial visualisation |

---

## Reproducibility

- Random seed: 42 throughout
- Reporting: STROBE
- All random seeds set explicitly (`random_state=42`)
- Python 3.12 | R 4.3+
- Runtime: ~5 minutes on a standard laptop

---

## Ethical Statement

This study used exclusively de-identified, publicly available secondary data from the Ghana Demographic and Health Survey programme. No primary data collection from human participants was conducted. DHS data accessed under registration from [dhsprogram.com](https://dhsprogram.com).

---

## Citation

```bibtex
@misc{ghanem2026ancfertility,
  author = {Ghanem, Valentine Golden},
  title  = {Temporal and Spatial Dynamics of Antenatal Care Coverage and Fertility Inequities in Ghana: A Subnational Ecological Study Using Ghana Demographic and Health Surveys},
  year   = {2026},
  url    = {https://github.com/valentineghanem-bit/anc-fertility-ghana-inequities}
}
```

---

## License

MIT — see [LICENSE](LICENSE) for details.

---

## Contact

Valentine Golden Ghanem
Ghana COCOBOD Cocoa Clinic, Accra, Ghana
valentineghanem@gmail.com
ORCID: [0009-0002-8332-0220](https://orcid.org/0009-0002-8332-0220)
