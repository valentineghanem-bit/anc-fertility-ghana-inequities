# Temporal and Spatial Dynamics of Antenatal Care Coverage and Fertility Inequities in Ghana: A Subnational Ecological Study Using Ghana Demographic and Health Surveys

[![CI](https://github.com/valentineghanem-bit/anc-fertility-ghana-inequities/actions/workflows/ci.yml/badge.svg)](https://github.com/valentineghanem-bit/anc-fertility-ghana-inequities/actions) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE) [![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/) [![R 4.3+](https://img.shields.io/badge/R-4.3+-blue.svg)](https://www.r-project.org/) [![ORCID](https://img.shields.io/badge/ORCID-0009--0002--8332--0220-green.svg)](https://orcid.org/0009-0002-8332-0220)

**Author:** Valentine Golden Ghanem | Ghana COCOBOD Cocoa Clinic, Accra, Ghana
**ORCID:** [0009-0002-8332-0220](https://orcid.org/0009-0002-8332-0220)
**Affiliation:** Ghana COCOBOD Cocoa Clinic, Accra, Ghana
**Reporting standard:** STROBE
**Date:** April 2026
**Status:** Manuscript in preparation

---

## 1. Abstract

A 34-year (1988–2022) longitudinal spatial analysis of skilled antenatal care (ANC) coverage and total fertility rate (TFR) across 14 harmonized Ghana DHS regional analytic units, using nine survey waves. The study introduces the **Care Efficiency Index** (CEI = ANC% / TFR) as an exploratory composite indicator to expose persistent regional inequities obscured by national coverage convergence. Spatial autocorrelation analysis shows ANC–TFR decoupling by 2022, with the Northern Belt remaining a persistent high-TFR spatial cluster.

---

## 2. Research Question & Aims

- **Primary:** Characterise the 34-year (1988–2022) temporal and spatial dynamics of skilled ANC coverage and fertility across harmonized Ghana DHS regional analytic units.
- **Secondary:** (a) Quantify subnational inequities using the Care Efficiency Index (CEI); (b) detect ANC–TFR spatial decoupling using global and local Moran's I; (c) identify an exploratory TFR inflection via Random Forest partial dependence; (d) stratify regions into policy priority zones.

---

## 3. Methods Summary

| Method | Tool | Purpose |
|--------|------|---------|
| Gini coefficient decomposition | scipy | ANC inequality over time |
| Global Moran's I (KNN k=4) | esda / libpysal | ANC and TFR spatial autocorrelation |
| LISA (Rook contiguity) | esda | Local cluster detection |
| Random Forest (n=200) | scikit-learn | ANC prediction and partial dependence |
| Decision Tree (CART) | scikit-learn | Interpretable benchmark comparator |
| Care Efficiency Index (CEI) | Custom (ANC% / TFR) | Novel composite performance indicator |
| Risk stratification | Custom (z-score quadrant) | Policy zone classification |
| Sensitivity analyses | statsmodels / scipy | Risk-zone robustness, ANC-TFR association checks, CEI gap stress-test |
| Mixed-effects models | lme4 (R) | Regional longitudinal trend decomposition |
| Choropleth maps | GeoPandas + Plotly | Temporal spatial visualisation |

---

## 4. Data Sources

| Source | Variables | Year | Access |
|--------|-----------|------|--------|
| Ghana DHS subnational (9 waves) | ANC coverage, TFR, regional indicators | 1988–2022 | [dhsprogram.com](https://dhsprogram.com) (registration) |
| Ghana administrative boundaries | Regional polygons | 2021 | [GADM](https://gadm.org) (open) |

> DHS data accessed under standard DHS Data Use Agreement. No individual participant data redistributed.

---

## 5. Key Findings

| Metric | Value |
|--------|-------|
| National ANC coverage | 83.1% (1988) → 97.7% (2022) |
| Inter-regional Gini reduction | 87.5% |
| TFR spatial clustering (2022) | Moran's I = 0.570 (p = 0.001; 999-permutation floor) |
| ANC–TFR decoupling | ANC clustering dissipated; TFR clustering intensified |
| Exploratory TFR inflection | 5.90 (RF partial dependence) |
| CEI range | North East 14.5 → Greater Accra 31.9 (2.2× gap) |
| Persistent cluster | Northern Belt — high TFR / historically low ANC |

---

## 6. Repository Structure

```
anc-fertility-ghana-inequities/
├── analysis/
│   ├── analysis_pipeline.py        # Full analytical pipeline
│   ├── create_choropleths.py       # Choropleth map generation
│   └── fix_figures_legibility.py   # Figure legibility corrections
├── app.py                          # Plotly Dash interactive application
├── analysis.R                      # R: mixed-effects models + Gini decomposition
├── scripts/
│   ├── spatial_utils.py            # Reusable spatial analysis utilities
│   └── spatial_diagnostics.R       # R: spatial autocorrelation diagnostics
├── dashboard/
│   └── ANC_Fertility_Dashboard_Ghana.html
├── poster/
│   └── ANC_Fertility_Poster_Ghana.html
├── tests/
├── data/
│   └── README_data.md
├── requirements.txt
└── CITATION.cff
```

---

## 7. Reproducibility

### 7.1 Requirements

- Python 3.12 (pinned in `requirements.txt`)
- R 4.3+ with packages: lme4, spdep, dplyr (see `analysis.R` header)
- Random seed: 42 throughout
- Estimated runtime: ~3–5 minutes on a standard laptop
- Tested on: Ubuntu 22.04 / macOS 14 / Windows 11 (CI: GitHub Actions)

### 7.2 Clone & install

```bash
git clone https://github.com/valentineghanem-bit/anc-fertility-ghana-inequities.git
cd anc-fertility-ghana-inequities
pip install -r requirements.txt
```

### 7.3 Run the analytical pipeline

```bash
python analysis/analysis_pipeline.py --all
```

Run the S+ sensitivity analyses:

```bash
python analysis/splus_sensitivity_analysis.py
```

### 7.4 Run the test suite

```bash
pytest tests/ -v
```

### 7.5 Launch the interactive Dash application

```bash
python app.py
# Visit http://127.0.0.1:8050
```

### 7.6 Open the static HTML dashboard

```bash
# macOS
open dashboard/ANC_Fertility_Dashboard_Ghana.html
# Windows
start dashboard/ANC_Fertility_Dashboard_Ghana.html
# Linux
xdg-open dashboard/ANC_Fertility_Dashboard_Ghana.html
```

---

## 8. Outputs

| Output | Description |
|--------|-------------|
| `data/processed/` | Cleaned master CSV, spatial weights, model outputs |
| `outputs/sensitivity/` | S+ sensitivity analyses for risk zones, ANC-TFR robustness, fixed effects/GEE, and CEI gap |
| `figures/` | Publication-quality PNG figures (300 DPI) |
| `dashboard/` | Self-contained interactive HTML dashboard |
| `poster/` | A0 conference poster (HTML, print-ready) |
| `docs/STROBE_CHECKLIST_MAPPING.md` | Tabulated STROBE checklist mapping |
| `docs/PLOS_GUIDELINE_ALIGNMENT_2026-07-12.md` | PLOS submission-readiness audit |

## 8a. Downloadable Artefacts (HTML)

Both the interactive dashboard and the conference poster are committed as self-contained HTML files — no server, no build step required.

| Artefact | View on GitHub | Live preview | Direct download (raw HTML) |
|----------|---------------|--------------|---------------------------|
| Interactive dashboard | [View](https://github.com/valentineghanem-bit/anc-fertility-ghana-inequities/blob/main/dashboard/ANC_Fertility_Dashboard_Ghana.html) | [Preview](https://htmlpreview.github.io/?https://github.com/valentineghanem-bit/anc-fertility-ghana-inequities/blob/main/dashboard/ANC_Fertility_Dashboard_Ghana.html) | [Download](https://raw.githubusercontent.com/valentineghanem-bit/anc-fertility-ghana-inequities/main/dashboard/ANC_Fertility_Dashboard_Ghana.html) |
| Conference poster | [View](https://github.com/valentineghanem-bit/anc-fertility-ghana-inequities/blob/main/poster/ANC_Fertility_Poster_Ghana.html) | [Preview](https://htmlpreview.github.io/?https://github.com/valentineghanem-bit/anc-fertility-ghana-inequities/blob/main/poster/ANC_Fertility_Poster_Ghana.html) | [Download](https://raw.githubusercontent.com/valentineghanem-bit/anc-fertility-ghana-inequities/main/poster/ANC_Fertility_Poster_Ghana.html) |

> **Tip:** The dashboard works fully offline once downloaded. The poster is print-ready at A0 (841 × 1189 mm).

---

## 9. Reporting Standard

This study follows the **STROBE** (Strengthening the Reporting of Observational Studies in Epidemiology) reporting guideline for observational ecological studies.

A tabulated STROBE mapping is provided in [`docs/STROBE_CHECKLIST_MAPPING.md`](docs/STROBE_CHECKLIST_MAPPING.md). The S+ sensitivity report is provided in [`outputs/sensitivity/SPLUS_SENSITIVITY_ANALYSIS_2026-07-12.md`](outputs/sensitivity/SPLUS_SENSITIVITY_ANALYSIS_2026-07-12.md).

---

## 10. Ethical Statement

This study analyses publicly released aggregate data from the Ghana Demographic and Health Survey Programme (ICF International) and Ghana Statistical Service. No individual participant data were accessed. All inputs are de-identified regional or district summary statistics. Ethical review was not required for analysis of publicly available aggregate statistics; DHS data were accessed under the standard DHS Programme Data Use Agreement.

---

## 11. Citation

**APA:**
Ghanem, V. G. (2026). *Temporal and Spatial Dynamics of Antenatal Care Coverage and Fertility Inequities in Ghana: A Subnational Ecological Study Using Ghana Demographic and Health Surveys.* GitHub. https://github.com/valentineghanem-bit/anc-fertility-ghana-inequities

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

Code is released under the **MIT License** — see [LICENSE](LICENSE) for details.
Outputs and figures: **CC BY 4.0**.

---

## 13. Author & Contact

**Valentine Golden Ghanem**
Ghana COCOBOD Cocoa Clinic, Accra, Ghana
Email: valentineghanem@gmail.com
ORCID: [0009-0002-8332-0220](https://orcid.org/0009-0002-8332-0220)

---

## 14. Acknowledgements

The author thanks the DHS Programme and ICF International for publicly releasing the Ghana DHS subnational data, and the Ghana Statistical Service for the 2021 Population and Housing Census district files. Spatial analysis relied on the open-source spdep, esda/libpysal, and GeoPandas ecosystems. Machine learning used scikit-learn and the R lme4 package for mixed-effects models.
