# S+ Repository Sync Report

Date: 2026-07-12

## Purpose

This report records the final GitHub-repository alignment with the S+ submission package. The repository contains reproducibility materials, dashboard, poster, data outputs, sensitivity analyses, and reporting-standard documentation. Manuscript files, cover letters, and submission-system-only documents remain outside the repository.

## Canonical Scientific Values

| Field | Canonical value |
|---|---|
| Analytic sample | 92 region-year observations |
| Geography | 14 harmonized Ghana DHS regional analytic units |
| Display geometry | Modern district/region boundaries only; Bono East -> Bono and Western North -> Western for analytic interpretation |
| ANC coverage | 83.1% in 1988 to 97.7% in 2022 |
| ANC Gini | 0.070 to 0.009, 87.5% reduction |
| TFR spatial clustering | Moran's I = 0.570, p = 0.001, 999-permutation floor |
| CEI gap | Greater Accra 31.9 vs North East 14.5, 2.2x gap |
| RF TFR inflection | 5.90, exploratory partial-dependence finding |
| Risk-zone counts | Critical=23, Emerging=6, Workhorse=18, Resilient=45 |

## S+ Additions Now in Repository

- `analysis/splus_sensitivity_analysis.py`
- `outputs/sensitivity/SPLUS_SENSITIVITY_ANALYSIS_2026-07-12.md`
- `outputs/sensitivity/*.csv`
- `docs/STROBE_CHECKLIST_MAPPING.md`
- `docs/PLOS_GUIDELINE_ALIGNMENT_2026-07-12.md`
- `docs/SPLUS_FINAL_READINESS_VERDICT_2026-07-12.md`
- `docs/DATA_CODE_RELEASE_NOTE.md`

## Sensitivity Summary

- Same-year risk-zone sensitivity: 53.3% agreement with grand-mean labels; Critical-zone Jaccard overlap = 0.324.
- ANC-TFR association: negative in crude, survey-year, and clustered models; attenuates under GEE and simultaneous region-plus-year adjustment.
- CEI gap: pooled regional leader/trailer gap remains 2.20x; descriptive bootstrap interval = 1.55x to 2.20x.
- Interpretation: conclusions are presented as ecological spatial-temporal patterning and equity monitoring, not causal effect estimation.

## Repository Exclusions

The repository intentionally excludes:

- manuscript DOCX/PDF files,
- cover letter files,
- response-to-reviewer files,
- local planning files,
- credentials or tokens,
- raw identifiable data.

## QA Status

- README structure gate: 15 h2 entries including `## 8a`, and 6 reproducibility h3 entries.
- Python syntax check: passed for `analysis/splus_sensitivity_analysis.py`.
- Test suite: `4 passed, 1 skipped`.
- Dashboard/poster: HI-EI ECharts standard retained; legacy 60 KB size ceiling superseded by the 2026-06-16 HI-EI rule.
