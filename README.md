# Temporal and Spatial Dynamics of Antenatal Care Coverage and Fertility Inequities in Ghana: A Subnational Ecological Study Using Ghana Demographic and Health Surveys

[![CI](https://github.com/valentineghanem-bit/anc-fertility-ghana-inequities/actions/workflows/ci.yml/badge.svg)](https://github.com/valentineghanem-bit/anc-fertility-ghana-inequities/actions) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE) [![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/) [![R 4.3+](https://img.shields.io/badge/R-4.3+-blue.svg)](https://www.r-project.org/) [![ORCID](https://img.shields.io/badge/ORCID-0009--0002--8332--0220-green.svg)](https://orcid.org/0009-0002-8332-0220)

**Author:** Valentine Golden Ghanem | Ghana COCOBOD Cocoa Clinic, Accra, Ghana
**ORCID:** [0009-0002-8332-0220](https://orcid.org/0009-0002-8332-0220)
**Affiliation:** Ghana COCOBOD Cocoa Clinic, Accra, Ghana
**Reporting standard:** STROBE
**Date:** April 2026
**Status:** Manuscript in preparation | Part II of Ghana ANC longitudinal series

> Valentine Golden Ghanem (2026). *Temporal and Spatial Dynamics of Antenatal Care Coverage and Fertility Inequities in Ghana: A Subnational Ecological Study Using Ghana Demographic and Health Surveys.* GitHub repository. https://github.com/valentineghanem-bit/anc-fertility-ghana-inequities

---

## 1. Abstract

A 34-year (1988–2022) longitudinal spatial analysis of skilled antenatal care (ANC) coverage and total fertility rate (TFR) across all 16 administrative regions of Ghana, using nine DHS survey waves. The study introduces the **Care Efficiency Index** (CEI = ANC% / TFR) as a novel composite indicator to expose persistent regional inequities obscured by national coverage convergence. Spatial autocorrelation analysis reveals a significant ANC–TFR decoupling by 2022, with the Northern Belt remaining a persistent high-TFR, historically low-ANC spatial cluster.

---

## 2. Research Question & Aims

- **Primary:** Characterise the 34-year (1988–2022) temporal and spatial dynamics of skilled ANC coverage and fertility across Ghana's regions.
- **Secondary:** (a) Quantify subnational inequities using the novel Care Efficiency Index (CEI); (b) detect ANC–TFR spatial decoupling using global and local Moran's I; (c) identify the critical TFR threshold via Random Forest partial dependence; (d) stratify regions into policy priority zones.

---

## 3. Methods Summary

| Method | Tool | Purpose |
|--------|------|---------|
| Gini coefficient decomposition | scipy | Inequality over time |
| Global Moran's I (KNN k=4) | esda / libpysal | ANC and TFR spatial autocorrelation |
| LISA (Rook contiguity) | esda | Local cluster detection |
| Random Forest (n=200) | scikit-learn | ANC prediction and partial dependence |
| Decision Tree (CART) | scikit-learn | Interpretable benchmark comparator |
| Care Efficiency Index (CEI) | Custom (ANC% / TFR) | Novel composite performance indicator |
| Risk Stratification | Custom (z-score quadrant) | Policy zone classification |
| Mixed-effects models | lme4 (R) | Regional longitudinal trend decomposition |
| Choropleth maps | GeoPandas + Plotly | Temporal spatial visualisation |

---

## 4. Data Sources

| Source | Variables | Year | Access |
|--------|-----------|------|--------|
| Ghana DHS subnational | ANC coverage, TFR, regional indicators | 1988, 1993, 1998, 2003, 2008, 2014, 2016, 2019, 2022 | [dhsprogram.com](https://dhsprogram.com) (registration) |
| Ghana administrative boundaries | Regional polygons | 2021 | [GADM](https://gadm.org) |

> DHS data accessed under registration. Raw microdata are not redistributed in compliance with DHS access policies.

---

## 5. Key Findings

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

## 6. Repository Structure

```
anc-fertility-ghana-inequities/
├── analysis/
│   ├── analysis_pipeline.py        # Full analytical pipeline
│   ├── create_choropleths.py       # Choropleth map generation
│   └── fix_figures_legibility.py   # Figure legibility corrections
├── app.py                          # Plotly Dash interactive web application
├── analysis.R                      # R: mixed-effects models + Gini decomposition
├── dashboard/
│   └── ANC_Fertility_Dashboard_Ghana.html
├── poster/
│   └── ANC_Fertility_Poster_Ghana.html
├── outputs/
│   ├── *.csv                       # Analysis output tables
│   └── figures/06_figure_*.png     # 12 manuscript figures + supplementary
├── requirements.txt
├── renv.lock
├── CITATION.cff
└── README.md
```

---

## 7. Reproducibility

### 7.1 Requirements
- Python 3.12 (see `requirements.txt` for pinned versions)
- R 4.3+ (for R scripts; see `renv.lock` or `analysis.R` header for pinned packages)
- Random seed: 42 throughout (set via `random_state=42` and `np.random.seed(42)`)
- Estimated runtime: ~5 minutes on a standard laptop
- Tested on: Ubuntu 22.04 / macOS 14 / Windows 11 (CI: GitHub Actions)

### 7.2 Clone & install
```bash
git clone https://github.com/valentineghanem-bit/anc-fertility-ghana-inequities.git
cd anc-fertility-ghana-inequities
pip install -r requirements.txt
# For R scripts (optional):
Rscript -e "if (!requireNamespace('renv', quietly=TRUE)) install.packages('renv'); renv::restore()"
```

### 7.3 Run the analytical pipeline
```bash
cd analysis
python analysis_pipeline.py
# Then choropleths and legibility fixes:
python create_choropleths.py
python fix_figures_legibility.py
# R mixed-effects:
Rscript ../analysis.R
```

### 7.4 Run the test suite
```bash
pytest tests/ -v
```

### 7.5 Launch the interactive Dash application
```bash
python app.py
# Navigate to http://127.0.0.1:8050 in your browser
```

### 7.6 Open the static HTML dashboard
Open `dashboard/ANC_Fertility_Dashboard_Ghana.html` in any modern browser. No server required.

---

## 8. Outputs

- **Interactive Dash app:** `app.py` — `python app.py` → http://127.0.0.1:8050
- **Static HTML dashboard:** `dashboard/ANC_Fertility_Dashboard_Ghana.html`
- **A0 poster:** `poster/ANC_Fertility_Poster_Ghana.html`
- **Figures:** `outputs/figures/06_figure_*.png` — 12 manuscript + supplementary (300 DPI)
- **Tables:** `outputs/*.csv`

---

## 9. Reporting Standard

This study follows the **STROBE** (Strengthening the Reporting of Observational Studies in Epidemiology) reporting guideline for observational ecological studies.

---

## 10. Ethical Statement

This study used exclusively de-identified, publicly available secondary data from the Ghana Demographic and Health Survey programme. No primary data collection from human participants was conducted. DHS data accessed under registration from [dhsprogram.com](https://dhsprogram.com).

---

## 11. Citation

**APA:**
Ghanem, V. G. (2026). *Temporal and Spatial Dynamics of Antenatal Care Coverage and Fertility Inequities in Ghana: A Subnational Ecological Study Using Ghana Demographic and Health Surveys*. GitHub. https://github.com/valentineghanem-bit/anc-fertility-ghana-inequities

**BibTeX:**
```bibtex
@misc{ghanem2026ancfertility,
  author = {Ghanem, Valentine Golden},
  title  = {Temporal and Spatial Dynamics of Antenatal Care Coverage and Fertility Inequities in Ghana: A Subnational Ecological Study Using Ghana Demographic and Health Surveys},
  year   = {2026},
  url    = {https://github.com/valentineghanem-bit/anc-fertility-ghana-inequities}
}
```

A machine-readable citation is provided in `CITATION.cff`.

---

## 12. License

Code is released under the **MIT License** — see [LICENSE](LICENSE) for details. Outputs and figures: CC BY 4.0.

---

## 13. Author & Contact

- **Valentine Golden Ghanem**
  Ghana COCOBOD Cocoa Clinic, Accra, Ghana
  Email: [valentineghanem@gmail.com](mailto:valentineghanem@gmail.com)
  ORCID: [0009-0002-8332-0220](https://orcid.org/0009-0002-8332-0220)

---

## 14. Acknowledgements

- **Ghana Demographic and Health Survey programme** (ICF International) for survey data access under signed Data Use Agreement.
- **Ghana Statistical Service** for the 2021 Population and Housing Census and administrative boundary data.
- **WHO Global Health Observatory** for national-level indicators.
- **AIPOCH** (Anti-hallucination Pipeline for Open Computational Health) v6.0 quad-connector citation verification (PubMed · Consensus · Scholar · Scite).

---

*This README follows the AIPOCH v6.0 standardised research-output template (May 2026). All repository READMEs in the [valentineghanem-bit](https://github.com/valentineghanem-bit) organisation share this structure.*
